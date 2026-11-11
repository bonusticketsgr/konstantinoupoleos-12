"""Ανάκτηση των διαστάσεων του μελετητή (γραμμή 0.28 + βέλη + πλάγια τιμή) – από το recover_dims.py των Σ1/Σ2,
με παράμετρο κλίμακας S (pt/m) και εφεδρική μέθοδο για τις μικρές διαστάσεις (βέλη απέξω): τα άκρα κάθε διάστασης
έχουν σταυρωτή παύλα ±2.3 pt κάθετα στη γραμμή."""
import pymupdf, json, math, re, sys, collections


def _fallback(dims, segs, S, tol_val):
    def L(a, b): return math.hypot(b.x - a.x, b.y - a.y)
    hticks = collections.defaultdict(set); vticks = collections.defaultdict(set)   # άκρο -> πλευρές που έχουν παύλα
    for a, b in segs:
        l = L(a, b)
        if not (1.6 <= l <= 3.2): continue
        if abs(a.y - b.y) < 0.05: hticks[(round(a.x, 1), round(a.y, 1))].add(1 if b.x > a.x else -1)
        elif abs(a.x - b.x) < 0.05: vticks[(round(a.x, 1), round(a.y, 1))].add(1 if b.y > a.y else -1)
    hpts = [p for p, s in hticks.items() if len(s) == 2]      # παύλα οριζόντια και από τις δύο πλευρές -> άκρο ΚΑΤΑΚΟΡΥΦΗΣ διάστασης
    vpts = [p for p, s in vticks.items() if len(s) == 2]
    for d in dims:
        if not d.get("unresolved"): continue
        v = float(d["value"]); best = None
        if d["dir"] == "V":
            c = [p for p in hpts if abs(p[0] - d["tx"]) <= 16 and abs(p[1] - d["ty"]) <= 70]
            for i in range(len(c)):
                for j in range(i + 1, len(c)):
                    if abs(c[i][0] - c[j][0]) < 0.3 and abs(abs(c[i][1] - c[j][1]) / S - v) <= min(tol_val, 0.012 + 0.0):
                        sc = abs((c[i][1] + c[j][1]) / 2 - d["ty"]) + abs(c[i][0] - d["tx"])
                        if best is None or sc < best[0]: best = (sc, c[i][0], min(c[i][1], c[j][1]), c[i][0], max(c[i][1], c[j][1]))
        else:
            c = [p for p in vpts if abs(p[1] - d["ty"]) <= 16 and abs(p[0] - d["tx"]) <= 70]
            for i in range(len(c)):
                for j in range(i + 1, len(c)):
                    if abs(c[i][1] - c[j][1]) < 0.3 and abs(abs(c[i][0] - c[j][0]) / S - v) <= min(tol_val, 0.012):
                        sc = abs((c[i][0] + c[j][0]) / 2 - d["tx"]) + abs(c[i][1] - d["ty"])
                        if best is None or sc < best[0]: best = (sc, min(c[i][0], c[j][0]), c[i][1], max(c[i][0], c[j][0]), c[i][1])
        if best:
            _, x0, y0, x1, y1 = best
            d.update(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2), fallback=True)
            d["side"] = -1 if (d["ty"] < y0 if d["dir"] == "H" else d["tx"] < x0) else 1
            del d["unresolved"]
    # γραμμή διάστασης σε δύο κομμάτια (κενό για το κείμενο), συχνά ελαφρά λοξή (όριο οικοπέδου): τα δύο κομμάτια εκατέρωθεν του κειμένου
    for d in dims:
        if not d.get("unresolved"): continue
        v = float(d["value"]); V = d["dir"] == "V"; cand = []
        c = d["ty"] if V else d["tx"]
        for a, b in segs:
            l = L(a, b)
            if l < 6: continue
            if V and abs(a.x - b.x) > 0.03 * l + 0.3: continue
            if not V and abs(a.y - b.y) > 0.03 * l + 0.3: continue
            if (V and a.y > b.y) or (not V and a.x > b.x): a, b = b, a
            lo, hi = (a.y, b.y) if V else (a.x, b.x)
            off = ((a.x + b.x) / 2 - d["tx"]) if V else ((a.y + b.y) / 2 - d["ty"])
            if abs(off) <= 16 and hi >= c - v * S - 3 and lo <= c + v * S + 3: cand.append((lo, hi, a, b))
        best = None
        for lo1, hi1, a1, b1 in cand:               # κομμάτι πριν από το κείμενο
            if not (hi1 <= c + 4): continue
            for lo2, hi2, a2, b2 in cand:           # κομμάτι μετά το κείμενο
                if not (lo2 >= c - 4 and lo2 > hi1 and lo2 - hi1 < 40): continue
                # συγγραμμικά;
                ux, uy = (b1.x - a1.x) / L(a1, b1), (b1.y - a1.y) / L(a1, b1)
                perp = abs((b2.x - a1.x) * uy - (b2.y - a1.y) * ux)
                if perp > 1.5: continue
                tot = L(a1, b2)
                if abs(tot / S - v) <= 0.015:
                    sc = abs(((a1.x + b2.x) / 2 - d["tx"])) + abs(((a1.y + b2.y) / 2 - d["ty"]))
                    if best is None or sc < best[0]: best = (sc, a1, b2)
        if best:
            _, a, b = best
            d.update(x0=round(a.x, 2), y0=round(a.y, 2), x1=round(b.x, 2), y1=round(b.y, 2), slant=True)
            del d["unresolved"]
    # λοξές διαστάσεις (κατά μήκος λοξού ορίου οικοπέδου): γραμμή 0.28 με μήκος = τιμή, κοντά και παράλληλα στο κείμενο
    for d in dims:
        if not d.get("unresolved"): continue
        v = float(d["value"]); best = None
        for a, b in segs:
            l = L(a, b)
            if abs(l / S - v) > 0.012 or l < 8: continue
            mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
            dist = math.hypot(mx - d["tx"], my - d["ty"])
            if dist > 22: continue
            if best is None or dist < best[0]: best = (dist, a, b)
        if best:
            _, a, b = best
            if (d["dir"] == "H" and a.x > b.x) or (d["dir"] == "V" and a.y > b.y): a, b = b, a
            d.update(x0=round(a.x, 2), y0=round(a.y, 2), x1=round(b.x, 2), y1=round(b.y, 2), slant=True)
            del d["unresolved"]
    return dims


def recover(dr, texts, region, S=56.6929, tol_val=0.02):
    X0, Y0, X1, Y1 = region
    def inreg(p): return X0 <= p.x <= X1 and Y0 <= p.y <= Y1
    segs = []   # 0.28 single-line segments
    for d in dr:
        if round(d.get("width") or 0, 2) != 0.28: continue
        its = d["items"]
        if len(its) == 1 and its[0][0] == 'l':
            a, b = its[0][1], its[0][2]
            if inreg(a) or inreg(b): segs.append((a, b))
    def L(a, b): return math.hypot(b.x - a.x, b.y - a.y)
    def ang(a, b): return math.degrees(math.atan2(b.y - a.y, b.x - a.x)) % 180
    # arrowhead strokes: short, oblique (10..40 deg off axis)
    tips = []
    for a, b in segs:
        l = L(a, b)
        if 1.5 <= l <= 7.0:
            g = ang(a, b); off = min(g % 90, 90 - g % 90)
            if 8 <= off <= 40: tips.append(a); tips.append(b)
    # πραγματική μύτη βέλους = σημείο όπου συναντώνται οι δύο λοξές πινελιές (εμφανίζεται ≥2 φορές)· τα άκρα των «φτερών» μία φορά.
    # Χωρίς αυτό, ένα ζεύγος «φτερών» γειτονικών διαστάσεων μπορεί να δώσει σωστό μήκος αλλά θέση μετατοπισμένη κατά 3,4 pt (6 cm).
    cnt = collections.Counter((round(p.x, 1), round(p.y, 1)) for p in tips)
    true_tips = [p for p in tips if cnt[(round(p.x, 1), round(p.y, 1))] >= 2]
    if len(true_tips) >= 2: tips = true_tips
    # axis-aligned candidate dim pieces
    H = [(a, b) for a, b in segs if abs(a.y - b.y) <= 0.02 * L(a, b) + 0.05 and L(a, b) >= 3]
    V = [(a, b) for a, b in segs if abs(a.x - b.x) <= 0.02 * L(a, b) + 0.05 and L(a, b) >= 3]
    dims = []
    vals = [t for t in texts if any("Italic" in f for f in t["fonts"]) and re.match(r"^\d+\.\d\d$", t["text"])
            and X0 <= (t["x0"] + t["x1"]) / 2 <= X1 and Y0 <= (t["y0"] + t["y1"]) / 2 <= Y1]
    for t in vals:
        v = float(t["text"]); cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
        horiz = abs(t["dir"][1]) < 0.2
        best = None
        if horiz:
            # dim line is horizontal, near (below or above) the text: |y - cy| <= 12, and text centre within the line's x-extent (merged)
            cands = [(a, b) for a, b in H if abs(a.y - cy) <= 12]
            # group by y (round 0.5) and merge pieces within 40 pt gaps
            groups = collections.defaultdict(list)
            for a, b in cands: groups[round(a.y * 2) / 2].append((min(a.x, b.x), max(a.x, b.x)))
            for y, ivs in groups.items():
                ivs.sort(); runs = []; cur = list(ivs[0])
                for a_, b_ in ivs[1:]:
                    if a_ <= cur[1] + 40: cur[1] = max(cur[1], b_)
                    else: runs.append(tuple(cur)); cur = [a_, b_]
                runs.append(tuple(cur))
                for a_, b_ in runs:
                    slack = 5 if v >= 0.3 else 30
                    if not (a_ - slack <= cx <= b_ + slack): continue
                    # arrow tips on this line near the run ends
                    on = [p.x for p in tips if abs(p.y - y) <= 2.5 and a_ - 6 <= p.x <= b_ + 6]
                    if len(on) < 2: continue
                    # choose the pair of tips (left of cx, right of cx) whose distance matches v
                    lefts = sorted(set(round(x, 1) for x in on if x < cx)); rights = sorted(set(round(x, 1) for x in on if x > cx))
                    for xl in lefts:
                        for xr in rights:
                            if abs((xr - xl) / S - v) <= tol_val:
                                d = abs(cy - y)
                                if best is None or d < best[0]: best = (d, xl, y, xr, y)
        else:
            cands = [(a, b) for a, b in V if abs(a.x - cx) <= 12]
            groups = collections.defaultdict(list)
            for a, b in cands: groups[round(a.x * 2) / 2].append((min(a.y, b.y), max(a.y, b.y)))
            for x, ivs in groups.items():
                ivs.sort(); runs = []; cur = list(ivs[0])
                for a_, b_ in ivs[1:]:
                    if a_ <= cur[1] + 40: cur[1] = max(cur[1], b_)
                    else: runs.append(tuple(cur)); cur = [a_, b_]
                runs.append(tuple(cur))
                for a_, b_ in runs:
                    slack = 5 if v >= 0.3 else 30
                    if not (a_ - slack <= cy <= b_ + slack): continue
                    on = [p.y for p in tips if abs(p.x - x) <= 2.5 and a_ - 6 <= p.y <= b_ + 6]
                    if len(on) < 2: continue
                    ups = sorted(set(round(yv, 1) for yv in on if yv < cy)); downs = sorted(set(round(yv, 1) for yv in on if yv > cy))
                    for yu in ups:
                        for yd in downs:
                            if abs((yd - yu) / S - v) <= tol_val:
                                d = abs(cx - x)
                                if best is None or d < best[0]: best = (d, x, yu, x, yd)
        if best:
            d, x0, y0, x1, y1 = best
            side = -1 if (cy < y0 if horiz else cx < x0) else +1   # text above/left = -1
            dims.append(dict(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2), value=t["text"], dir="H" if horiz else "V", side=side,
                             tx=round(cx, 1), ty=round(cy, 1)))
        else:
            dims.append(dict(value=t["text"], dir="H" if horiz else "V", tx=round(cx, 1), ty=round(cy, 1), unresolved=True))
    return _fallback(dims, segs, S, tol_val)

