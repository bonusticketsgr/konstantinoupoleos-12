"""Recover the designer's dimension lines (0.28 lines with arrowheads + italic value) inside a region of a Fespa sheet.
Output: list of dims {x0,y0,x1,y1 (source pts), value (text), dir 'H'/'V', text_side, ext: [(x,y,x,y)...] extension line stubs}."""
import pymupdf, json, math, re, sys, collections

def recover(pdf, texts, region, tol_val=0.02):
    X0, Y0, X1, Y1 = region
    doc = pymupdf.open(pdf); page = doc[0]; dr = page.get_drawings()
    S = 56.6929
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
    return dims

if __name__ == "__main__":
    pdf, texts, out = sys.argv[1], sys.argv[2], sys.argv[3]
    region = [float(v) for v in sys.argv[4:8]]
    T = json.load(open(texts))
    dims = recover(pdf, T, region)
    ok = [d for d in dims if not d.get("unresolved")]
    print("dimension texts:", len(dims), "resolved:", len(ok))
    for d in dims:
        if d.get("unresolved"): print("  UNRESOLVED", d["value"], d["dir"], "at", d["tx"], d["ty"])
    json.dump(dims, open(out, "w"), indent=0)

