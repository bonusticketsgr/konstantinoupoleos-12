"""Εξαγωγή της γεωμετρίας (χωρίς οπλισμούς), των κειμένων και των διαστάσεων του μελετητή από φύλλο ξυλοτύπου Fespa
(διανυσματικό PDF 1:50, 56.6929 pt/m). Όλες οι συντεταγμένες σε pt του αρχικού PDF.

Πάχη γραμμών Fespa: 1.7 περιγράμματα υποστυλωμάτων · 0.85 δοκοί / πλάκες (παύλες 2.8/1.7 = οπλισμός πλάκας → φεύγουν) ·
0.57 βοηθητικές (dotted = γραμμές αναφοράς διαστάσεων, dashed = κρυφές, μπλε = φυτευτά) · 0.28 διαγραμμίσεις, διαγώνιοι,
κύκλοι πλακών, γραμμές διαστάσεων · 1.42 ΟΠΛΙΣΜΟΙ (φεύγουν) · 1.13 ίχνη τομών."""
import pymupdf, math, collections, statistics, re

S = 56.6929


def _W(d): return round(d.get("width") or 0, 2)
def _BLUE(d): return (d.get("color") or (0, 0, 0))[2] > 0.5
def _ang(p, q): return math.degrees(math.atan2(q.y - p.y, q.x - p.x)) % 180.0
def _is_axis(p, q, tol=1.0):
    g = _ang(p, q); return g < tol or abs(g - 90) < tol or g > 180 - tol
def _len(p, q): return math.hypot(q.x - p.x, q.y - p.y)
def _in_rect(p, r): return r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]


def _in_poly(px, py, poly):
    inside = False; n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        if (y0 > py) != (y1 > py):
            xi = x0 + (py - y0) * (x1 - x0) / (y1 - y0)
            if xi > px: inside = not inside
    return inside


def extract_geometry(page, region, keep=(), stairs=(), diag_min=50, x57_min=100, sections=False, drawings=None, section_mode=False):
    """region = (x0,y0,x1,y1) ή λίστα ορθογωνίων. keep: ορθογώνια όπου οι λεπτές συνεχείς 0.57 είναι γεωμετρία.
    stairs: ορθογώνια όπου οι λοξές 0.28 είναι γεωμετρία (σκαλοπάτια)."""
    regs = [tuple(region)] if isinstance(region[0], (int, float)) else [tuple(r) for r in region]
    X0 = min(r[0] for r in regs); Y0 = min(r[1] for r in regs); X1 = max(r[2] for r in regs); Y1 = max(r[3] for r in regs)
    dr = drawings if drawings is not None else page.get_drawings()

    def inreg(d):
        r = d["rect"]
        return any(not (r.x1 < g[0] or r.x0 > g[2] or r.y1 < g[1] or r.y0 > g[3]) for g in regs)

    def pin(p): return any(g[0] <= p.x <= g[2] and g[1] <= p.y <= g[3] for g in regs)

    out = dict(columns=[], lines=[], curves=[], circles=[], ext=[], cuts=[], rcols=[], thin=[], region=[X0, Y0, X1, Y1])
    if section_mode: return _extract_section(dr, inreg, pin, out)

    # ---------- 1.7 : περιγράμματα υποστυλωμάτων -> κλειστοί βρόχοι
    segs17 = []
    for d in dr:
        if inreg(d) and _W(d) == 1.7:
            for it in d["items"]:
                if it[0] == 'l' and (pin(it[1]) or pin(it[2])): segs17.append((it[1], it[2]))
                elif it[0] == 'c' and pin(it[1]):
                    out["curves"].append(dict(w=1.7, blue=False, pts=[(round(p.x, 2), round(p.y, 2)) for p in it[1:5]]))
    def key(p): return (round(p.x, 1), round(p.y, 1))
    adj = collections.defaultdict(list)
    for i, (p, q) in enumerate(segs17): adj[key(p)].append(i); adj[key(q)].append(i)
    used = set(); loops = []; open_chains = []
    for i in range(len(segs17)):
        if i in used: continue
        p, q = segs17[i]; used.add(i); poly = [p, q]; cur = q; closed = False
        while True:
            nxt = [j for j in adj[key(cur)] if j not in used]
            if not nxt: break
            j = nxt[0]; used.add(j); c, d2 = segs17[j]
            cur = d2 if key(c) == key(cur) else c
            if key(cur) == key(poly[0]): closed = True; break
            poly.append(cur)
        (loops if closed else open_chains).append([(round(pp.x, 2), round(pp.y, 2)) for pp in poly])
    out["columns"] = loops; out["open17"] = open_chains

    # ---------- στρογγυλά υποστυλώματα: 4 τόξα πάχους 1.7 που κλείνουν κύκλο
    arcs = [c for c in out["curves"] if c["w"] == 1.7]
    usedc = set()
    for i, c in enumerate(arcs):
        if i in usedc: continue
        grp_ = [i]; usedc.add(i)
        bx = [min(p[0] for p in c["pts"]), min(p[1] for p in c["pts"]), max(p[0] for p in c["pts"]), max(p[1] for p in c["pts"])]
        changed = True
        while changed:
            changed = False
            for j, c2 in enumerate(arcs):
                if j in usedc: continue
                b2 = [min(p[0] for p in c2["pts"]), min(p[1] for p in c2["pts"]), max(p[0] for p in c2["pts"]), max(p[1] for p in c2["pts"])]
                if not (b2[0] > bx[2] + 1 or b2[2] < bx[0] - 1 or b2[1] > bx[3] + 1 or b2[3] < bx[1] - 1):
                    bx = [min(bx[0], b2[0]), min(bx[1], b2[1]), max(bx[2], b2[2]), max(bx[3], b2[3])]; usedc.add(j); grp_.append(j); changed = True
        w_, h_ = bx[2] - bx[0], bx[3] - bx[1]
        if len(grp_) >= 4 and abs(w_ - h_) < 1.5 and 12 < w_ < 80:
            out["rcols"].append((round((bx[0] + bx[2]) / 2, 2), round((bx[1] + bx[3]) / 2, 2), round(w_ / 2, 2)))

    # ---------- 0.85 : δομικές γραμμές (φεύγουν οι παύλες οπλισμού πλάκας ~2.8/1.7)
    segs85 = []
    for d in dr:
        if inreg(d) and _W(d) == 0.85:
            for it in d["items"]:
                if it[0] == 'l' and (pin(it[1]) or pin(it[2])): segs85.append((it[1], it[2], _BLUE(d)))
                elif it[0] == 'c' and pin(it[1]):
                    out["curves"].append(dict(w=0.85, blue=_BLUE(d), pts=[(round(p.x, 2), round(p.y, 2)) for p in it[1:5]]))
    groups = collections.defaultdict(list)
    for idx, (p, q, bl) in enumerate(segs85):
        if abs(p.y - q.y) < 0.05: groups[('H', round(p.y, 1))].append((min(p.x, q.x), max(p.x, q.x), idx))
        elif abs(p.x - q.x) < 0.05: groups[('V', round(p.x, 1))].append((min(p.y, q.y), max(p.y, q.y), idx))
    drop85 = set(); dashed85 = set()
    for k, ivs in groups.items():
        ivs.sort(); runs = []; cur = [ivs[0]]
        for iv in ivs[1:]:
            if iv[0] <= cur[-1][1] + 8: cur.append(iv)
            else: runs.append(cur); cur = [iv]
        runs.append(cur)
        for run in runs:
            if len(run) >= 3:
                med = statistics.median([b - a_ for a_, b, i in run])
                if med < 3.5:
                    for a_, b, i in run: drop85.add(i)
                elif med < 10:
                    for a_, b, i in run: dashed85.add(i)
    for idx, (p, q, bl) in enumerate(segs85):
        if idx in drop85: continue
        out["lines"].append(dict(w=0.85, blue=bl, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2), dashed=(idx in dashed85)))

    # ---------- 0.57 μπλε : φυτευτά
    for d in dr:
        if inreg(d) and _W(d) == 0.57 and _BLUE(d):
            for it in d["items"]:
                if it[0] == 'l' and (pin(it[1]) or pin(it[2])):
                    out["lines"].append(dict(w=0.57, blue=True, x0=round(it[1].x, 2), y0=round(it[1].y, 2), x1=round(it[2].x, 2), y1=round(it[2].y, 2)))
                elif it[0] == 'c' and pin(it[1]):
                    out["curves"].append(dict(w=0.57, blue=True, pts=[(round(p.x, 2), round(p.y, 2)) for p in it[1:5]]))

    # ---------- 0.57 μαύρες : dashed = κρυφές (μένουν) · dotted = γραμμές αναφοράς διαστάσεων (ξεχωριστά, «ext») · solid μόνο Χ / keep
    def line_key(p, q):
        dx, dy = q.x - p.x, q.y - p.y
        if math.hypot(dx, dy) < 1e-6: return None
        g = round((math.degrees(math.atan2(dy, dx)) % 180.0) / 2.0) * 2.0 % 180
        r = math.radians(g); nx, ny = -math.sin(r), math.cos(r)
        return (g, round(p.x * nx + p.y * ny))
    grp = collections.defaultdict(list); singles = []
    for d in dr:
        if not (inreg(d) and _W(d) == 0.57 and not _BLUE(d)): continue
        its = d["items"]
        if len(its) == 1 and its[0][0] == 'l':
            p, q = its[0][1], its[0][2]; k = line_key(p, q)
            if k is None or not (pin(p) or pin(q)): continue
            r = math.radians(k[0]); ux, uy = math.cos(r), math.sin(r)
            t0, t1 = p.x * ux + p.y * uy, q.x * ux + q.y * uy
            grp[k].append((min(t0, t1), max(t0, t1), p, q))
        else: singles.append(d)
    # διαγράμμιση 45° με πάχος 0.57 (π.χ. «τοιχείο έως το ύψος της σκάλας»): ομάδες ≥3 παράλληλων γραμμών σε μικρή απόσταση
    hatch57 = set()
    for g in (44.0, 46.0, 134.0, 136.0):
        offs = sorted((off, s) for (gg, off), segs in grp.items() if gg == g for s in segs if (s[1] - s[0]) > 4.0)
        for i, (off, sgm) in enumerate(offs):
            near = [o for o, s2 in offs if abs(o - off) <= 14 and s2 is not sgm and s2[0] < sgm[1] + 6 and s2[1] > sgm[0] - 6]
            if len(near) >= 2: hatch57.add((round(sgm[2].x, 2), round(sgm[2].y, 2), round(sgm[3].x, 2), round(sgm[3].y, 2)))
    for (g, off), segs in grp.items():
        segs.sort(key=lambda s: s[0]); runs = []; cur = [segs[0]]
        for s in segs[1:]:
            if s[0] <= cur[-1][1] + 8: cur.append(s)
            else: runs.append(cur); cur = [s]
        runs.append(cur)
        for run in runs:
            med = statistics.median([b - a_ for a_, b, _, _ in run])
            style = 'dotted' if (len(run) >= 3 and med < 1.8) else ('dashed' if (len(run) >= 3 and med < 10) else 'solid')
            if style == 'dotted':
                pts = [s[2] for s in run] + [s[3] for s in run]
                r = math.radians(g); ux, uy = math.cos(r), math.sin(r)
                pts.sort(key=lambda p: p.x * ux + p.y * uy)
                a_, b_ = pts[0], pts[-1]
                if _is_axis(a_, b_): out["ext"].append(dict(x0=round(a_.x, 2), y0=round(a_.y, 2), x1=round(b_.x, 2), y1=round(b_.y, 2)))
                continue
            for a_, b, p, q in run:
                kp = False
                if style == 'dashed': kp = not (not _is_axis(p, q) and (run[-1][1] - run[0][0]) < 20)
                else:
                    if (b - a_) > x57_min and not _is_axis(p, q): kp = True
                    if any(_in_rect(p, r) and _in_rect(q, r) for r in keep): kp = True
                    if (round(p.x, 2), round(p.y, 2), round(q.x, 2), round(q.y, 2)) in hatch57: kp = True
                if kp:
                    out["lines"].append(dict(w=0.57, blue=False, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2), dashed=(style == 'dashed')))
    for d in singles:      # καμπύλες: μόνο τα μεγάλα τόξα (σκάλες) – οι μικροί κύκλοι είναι σημάδια ράβδων
        r = d["rect"]
        if max(r.width, r.height) > 20 and pin(pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
            for it in d["items"]:
                if it[0] == 'c': out["curves"].append(dict(w=0.57, blue=False, pts=[(round(p.x, 2), round(p.y, 2)) for p in it[1:5]]))
                elif it[0] == 'l': out["lines"].append(dict(w=0.57, blue=False, x0=round(it[1].x, 2), y0=round(it[1].y, 2), x1=round(it[2].x, 2), y1=round(it[2].y, 2)))

    # ---------- 0.28 : διαγραμμίσεις 45°, διαγώνιοι πλακών, σκαλοπάτια, κύκλοι πλακών
    def in_any_column(px, py): return any(_in_poly(px, py, c) for c in out["columns"])
    for d in dr:
        if not (inreg(d) and _W(d) == 0.28): continue
        its = d["items"]
        if len(its) == 1 and its[0][0] == 'l':
            p, q = its[0][1], its[0][2]; L = _len(p, q)
            if not (pin(p) or pin(q)): continue
            g = _ang(p, q); hatch = (abs(g - 45) < 2.5 or abs(g - 135) < 2.5) and L > 4.0
            kp = (L > diag_min and not _is_axis(p, q)) or any(_in_rect(p, r) and _in_rect(q, r) and not _is_axis(p, q, 0.5) and L > 5 for r in stairs)
            if hatch: kp = True
            if kp and not hatch and in_any_column((p.x + q.x) / 2, (p.y + q.y) / 2): kp = False
            if kp:
                out["lines"].append(dict(w=0.28, blue=False, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2), hatch=hatch))
        elif all(it[0] == 'c' for it in its) and len(its) == 4:
            r = d["rect"]
            if 22 < max(r.width, r.height) < 28 and pin(pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
                out["circles"].append(dict(cx=round((r.x0 + r.x1) / 2, 2), cy=round((r.y0 + r.y1) / 2, 2), r=round(r.width / 2, 2)))

    # ---------- 1.13 : ίχνη τομών (αξονική γραμμή + βέλη)
    if sections:
        for d in dr:
            if inreg(d) and _W(d) == 1.13:
                for it in d["items"]:
                    if it[0] == 'l' and (pin(it[1]) or pin(it[2])):
                        out["cuts"].append(dict(x0=round(it[1].x, 2), y0=round(it[1].y, 2), x1=round(it[2].x, 2), y1=round(it[2].y, 2)))
    return out


def _extract_section(dr, inreg, pin, out):
    """Τομή (π.χ. διακοσμητικής μετώπης 1:20): το περίγραμμα σκυροδέματος και οι ράβδοι έχουν το ίδιο πάχος 0.85.
    Κρατιούνται οι ομάδες συνδεδεμένων ευθειών 0.85 που ΔΕΝ βρίσκονται μέσα στο πλαίσιο άλλης ομάδας (οι ράβδοι είναι πάντα μέσα
    στο σκυρόδεμα), οι παύλες των τριγώνων στάθμης (0.57, μικρές) και οι λεπτές 0.28 (φιλτράρονται αργότερα με βάση τα κείμενα)."""
    segs = []
    for d in dr:
        if inreg(d) and _W(d) == 0.85:
            for it in d["items"]:
                if it[0] == 'l' and pin(it[1]) and pin(it[2]) and _len(it[1], it[2]) > 0.5: segs.append((it[1], it[2]))
    # Περίγραμμα = οι ευθείες που «φαίνονται» απέξω: ακτίνες από 16 διευθύνσεις, κρατιέται η πρώτη γραμμή που συναντά καθεμία.
    # Οι ράβδοι είναι πάντα πίσω από το περίγραμμα. Στα κομμένα άκρα (η πλάκα συνεχίζει) μπαίνει φράγμα για να μη «μπαίνουν» ακτίνες.
    from shapely.geometry import LineString
    if not segs: return out
    xs = [v for p, q in segs for v in (p.x, q.x)]; ys = [v for p, q in segs for v in (p.y, q.y)]
    bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
    lines = [LineString([(p.x, p.y), (q.x, q.y)]) for p, q in segs]
    blockers = []
    for xe in (bx0, bx1):
        dang = [pt.y for p, q in segs for pt in (p, q) if abs(pt.x - xe) < 1.0 and abs(p.y - q.y) < 0.3]
        vert = [1 for p, q in segs if abs(p.x - xe) < 1.0 and abs(q.x - xe) < 1.0 and abs(p.y - q.y) > 8]
        if len(dang) >= 2 and not vert: blockers.append(LineString([(xe, min(dang) - 0.5), (xe, max(dang) + 0.5)]))
    allg = lines + blockers
    hits = collections.Counter()
    diag = math.hypot(bx1 - bx0, by1 - by0) + 20; cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    for ai in range(32):
        a_ = math.radians(ai * 11.25 + 3.0); ux, uy = math.cos(a_), math.sin(a_); nx, ny = -uy, ux
        n = int(diag / 1.2)
        for j in range(-n // 2, n // 2 + 1):
            sx, sy = cx + nx * j * 1.2 - ux * diag, cy + ny * j * 1.2 - uy * diag
            ray = LineString([(sx, sy), (sx + ux * 2 * diag, sy + uy * 2 * diag)])
            best = None
            for gi, g in enumerate(allg):
                if not ray.intersects(g): continue
                it = ray.intersection(g)
                pt = it if it.geom_type == "Point" else it.representative_point()
                dd = math.hypot(pt.x - sx, pt.y - sy)
                if best is None or dd < best[0]: best = (dd, gi)
            if best is not None and best[1] < len(lines): hits[best[1]] += 1
    keep_idx = [i for i in range(len(segs)) if hits[i] >= max(4, 0.15 * _len(*segs[i]) / 1.2)]
    for i in keep_idx:
        p, q = segs[i]
        out["lines"].append(dict(w=0.85, blue=False, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2)))
    if keep_idx:
        kx = [v for i in keep_idx for v in (segs[i][0].x, segs[i][1].x)]; ky = [v for i in keep_idx for v in (segs[i][0].y, segs[i][1].y)]
        out["outline_box"] = [(min(kx), min(ky), max(kx), max(ky))]
    out["cut_sides"] = [("L" if abs(bl.coords[0][0] - bx0) < 0.1 else "R") for bl in blockers]
    for d in dr:
        if not inreg(d): continue
        w = _W(d)
        for it in d["items"]:
            if it[0] != 'l' or not (pin(it[1]) and pin(it[2])): continue
            p, q = it[1], it[2]; L = _len(p, q)
            if w == 0.57 and L <= 6.5 and abs(p.y - q.y) < 0.05:         # γέμισμα τριγώνου στάθμης
                out["lines"].append(dict(w=0.57, blue=False, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2), tri=True))
            elif w == 0.28 and L > 2.0:
                out["thin"].append(dict(w=0.28, blue=False, x0=round(p.x, 2), y0=round(p.y, 2), x1=round(q.x, 2), y1=round(q.y, 2)))
    return out


def find_sections(page, word="ΜΕΤΩΠΗΣ"):
    """Τομές του φύλλου: τίτλοι «ΤΟΜΗ n-n ... ΜΕΤΩΠΗΣ» -> [(όνομα, περιοχή σχεδίου πάνω από τον τίτλο)], από πάνω προς τα κάτω."""
    tt = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(sp["text"] for sp in l["spans"])
            if txt.strip().startswith("ΤΟΜΗ") and word in txt:
                m = re.search(r"ΤΟΜΗ\s+(\S+)", txt); tt.append((l["bbox"], m.group(1) if m else "?"))
    tt.sort(key=lambda t: (round(t[0][0] / 200), t[0][1]))
    out = []
    for i, (bb, name) in enumerate(tt):
        prev = [o[0][3] for o in tt if o[0][3] < bb[1] and abs(o[0][0] - bb[0]) < 120]
        y0 = max(bb[1] - 300, (max(prev) + 26) if prev else 0)
        out.append((name, (bb[0] - 75, y0, bb[2] + 40, bb[1] - 6)))
    return out


# ------------------------------------------------------------------ κείμενα
def load_texts(page, region):
    """Κείμενα της περιοχής, ενωμένα ανά ετικέτα (π.χ. «Κ» + «1  30/70», ή τα 3 κομμάτια ενός κατακόρυφου «Δ9.5  30/55»),
    χωρίς τα διπλά (το Fespa γράφει συχνά την ίδια ετικέτα δύο φορές)."""
    regs = [tuple(region)] if isinstance(region[0], (int, float)) else [tuple(r) for r in region]
    def cin(x, y): return any(g[0] <= x <= g[2] and g[1] <= y <= g[3] for g in regs)
    items = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            sp = [s for s in l["spans"] if s["text"].strip() != "" or len(l["spans"]) > 1]
            if not sp: continue
            d = (round(l["dir"][0], 3), round(l["dir"][1], 3))
            if d[0] > 0.9985: d = (1.0, 0.0)            # ετικέτες κατά μήκος ελαφρά λοξών τοιχείων (< 3°): σαν οριζόντιες / κατακόρυφες
            elif d[1] < -0.9985: d = (0.0, -1.0)
            x0 = min(s["bbox"][0] for s in sp); y0 = min(s["bbox"][1] for s in sp)
            x1 = max(s["bbox"][2] for s in sp); y1 = max(s["bbox"][3] for s in sp)
            items.append(dict(block=b["number"], text="".join(s["text"] for s in sp), x0=x0, y0=y0, x1=x1, y1=y1, dir=d,
                              size=max(s["size"] for s in sp), fonts=sorted(set(s["font"] for s in sp)), color=sp[0]["color"],
                              origin=tuple(sp[0]["origin"])))
    # διπλά (ίδιο κείμενο στην ίδια θέση) φεύγουν πριν από την ένωση
    seen0 = set(); uniq = []
    for it in items:
        k = (it["text"], round(it["origin"][0]), round(it["origin"][1]), it["dir"])
        if k in seen0: continue
        seen0.add(k); uniq.append(it)
    # ένωση κομματιών της ίδιας γραμμής κειμένου (ίδια διεύθυνση, ίδια γραμμή βάσης, συνεχόμενα)
    merged = []
    bydir = collections.defaultdict(list)
    for it in uniq: bydir[it["dir"]].append(it)
    for d, its in bydir.items():
        if d == (1.0, 0.0): its.sort(key=lambda t: (round(t["origin"][1] / 2.0), t["x0"]))
        elif d == (0.0, -1.0): its.sort(key=lambda t: (round(t["origin"][0] / 2.0), -t["y1"]))
        cur = None
        for t in its:
            ok = False
            if cur is not None and not (RE_NUM.match(cur["text"].strip()) and any("Italic" in f for f in cur["fonts"])) \
                    and not (RE_NUM.match(t["text"].strip()) and any("Italic" in f for f in t["fonts"])):
                lim = (2.4 if re.match(r"^Δ\s?(\d+\.\d+)?$", cur["text"].strip()) else 1.05) * t["size"]      # «Δ» + «5.1» + «25/40» γραμμένα χωριστά
                if d == (1.0, 0.0): ok = abs(cur["origin"][1] - t["origin"][1]) < 2.0 and -4.0 < t["x0"] - cur["x1"] < lim
                elif d == (0.0, -1.0): ok = abs(cur["origin"][0] - t["origin"][0]) < 2.0 and -4.0 < cur["y0"] - t["y1"] < lim
            if ok:
                gap = (t["x0"] - cur["x1"]) if d == (1.0, 0.0) else (cur["y0"] - t["y1"])
                if gap > 0.22 * t["size"] and not cur["text"].endswith(" ") and not t["text"].startswith(" "): cur["text"] += " "
                cur["text"] += t["text"]; cur["x0"] = min(cur["x0"], t["x0"]); cur["y0"] = min(cur["y0"], t["y0"])
                cur["x1"] = max(cur["x1"], t["x1"]); cur["y1"] = max(cur["y1"], t["y1"]); cur["size"] = max(cur["size"], t["size"])
                cur["fonts"] = sorted(set(cur["fonts"]) | set(t["fonts"]))
            else:
                cur = dict(t); merged.append(cur)
    seen = set(); out = []
    for t in merged:
        cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
        if not cin(cx, cy): continue
        k = (t["text"].strip(), round(cx), round(cy))
        if k in seen: continue
        seen.add(k); t["cx"], t["cy"] = cx, cy; t["raw"] = t["text"]; t["text"] = re.sub(r"\s+", " ", t["text"]).strip()
        out.append(t)
    return out


RE_COL = re.compile(r"^Κ\s?\d*[α-ωΑ-Ω]?\s+(\d+(/\d+)+|d=\d+)$")
RE_BEAM = re.compile(r"^Δ\s?[\d.]*\s+\d+/\d+")
RE_EZ = re.compile(r"^Ε\.?Ζ\.?")
RE_SLAB = re.compile(r"^Π\d*$")
RE_H = re.compile(r"^h=\s*\d+$")
RE_LEVEL = re.compile(r"^[+±\-−]\s?\d+[,.]\d\d$")
RE_NUM = re.compile(r"^\d+\.\d\d$")
# σημείωση σιφωνιού (μπαίνει στις ΣΗΜΕΙΩΣΕΙΣ της πινακίδας) και υπόλοιπα κομμάτια σημειώσεων οπλισμού
RE_DROP = re.compile(r"υποδοχή για το σιφώνι|ρόη να προβλεφθούν|δέτηση,? για να μην|τον οπλισμό της ΕΖ|οπλισμ|μέχρι τη στ\.|Τοιχείο έως το ύψος|σκάλας,? για στήριξ|σκάλας \(σαν|^Αναμονές")


def classify(t):
    s = t["text"]
    if "Φ" in s or "#" in s: return "rebar"
    if RE_DROP.search(s) or any("Tahoma" in f for f in t["fonts"]): return "drop"
    if RE_NUM.match(s) and any("Italic" in f for f in t["fonts"]): return "dim"
    if RE_COL.match(s): return "col"
    if RE_BEAM.match(s): return "beam"
    if RE_EZ.match(s): return "ez"
    if RE_SLAB.match(s): return "slab"
    if RE_H.match(s): return "h"
    if RE_LEVEL.match(s): return "level"
    if re.match(r"^\d$", s) and any("Arial" in f for f in t["fonts"]): return "cutmark"
    return "other"
