"""(ΣΟΦΙΤΑ) Δώμα / στηθαία / πέργκολα / καναπέδες από το A-10-S – παραλλαγή του extract_gf_site.py με το περίγραμμα της σοφίτας.
Χρήση: python3 -I extract_s_site.py <A-10-S.pdf> data/s_site.json
Περιβάλλων χώρος ισογείου από τη διανυσματική γεωμετρία του A-10-GF (EDGE): κήπος, βεράντες, φυτεύσεις, δέντρα, σκάλες,
ράμπα, περίφραξη – ΧΩΡΙΣ κείμενα, διαστάσεις, ετικέτες κουφωμάτων, σύμβολα στάθμης, σημεία όψεων (ο Γιάννης: «μη δείχνεις Ε.Ζ.
και τέτοια πράματα»). Χρήση: python3 -I extract_gf_site.py <A-10-GF.pdf> data/gf_site.json
Βαθμονόμηση όπως extract_gf.py (1:50 → 56,693 pt/m, αρχή μοντέλου X0 525,3 / Y0 397,4 pt display)."""
import sys, json, pymupdf
SRC, OUT = sys.argv[1], sys.argv[2]
S, X0, Y0 = 56.693, 525.3, 397.4
REGION = (-6.2, -2.6, 18.6, 15.8)
page = pymupdf.open(SRC)[0]; M = page.rotation_matrix


def m(p):
    return round((p.x - X0) / S, 3), round((p.y - Y0) / S, 3)


def _arc(cx, cy, r, a0, a1, n=8):
    import math
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


BUILDING = [(2.35, 0.40), (9.75, 0.40), (9.75, 2.70), (11.50, 2.70), (11.50, 2.95), (13.40, 2.95), (13.40, 7.90), (11.50, 7.90)] + \
           _arc(11.50, 7.25, 0.65, 90, 180) + [(10.85, 6.45), (2.35, 6.45)]


def inside(x, y):   # περίγραμμα σοφίτας (εξωτερική παρειά θερμοπρόσοψης) – point in polygon
    n = len(BUILDING); c = False
    for i in range(n):
        (x1, y1), (x2, y2) = BUILDING[i], BUILDING[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


out = []
for d in page.get_drawings():
    r = d["rect"] * M
    x0, y0 = m(pymupdf.Point(r.x0, r.y0)); x1, y1 = m(pymupdf.Point(r.x1, r.y1))
    if x1 < REGION[0] or x0 > REGION[2] or y1 < REGION[1] or y0 > REGION[3]:
        continue
    if all(inside(x, y) for x, y in ((x0, y0), (x1, y1), (x0, y1), (x1, y0))):
        continue
    col = tuple(round(v, 2) for v in d["color"]) if d.get("color") else None
    fil = tuple(round(v, 2) for v in d["fill"]) if d.get("fill") else None
    w = round(d.get("width") or 0, 2)
    kinds = set(it[0] for it in d["items"])
    diag = max(x1 - x0, y1 - y0)
    if fil == (1.0, 1.0, 1.0): continue                                   # λευκά κουτιά ετικετών
    if col == (0.33, 0.33, 0.33) or fil == (0.33, 0.33, 0.33): continue   # πλαίσια ετικετών κουφωμάτων, γραμμές / σύμβολα τομών A-30
    if fil is None and w < 0.2: continue                                  # γραμμές διαστάσεων / οδηγοί
    if fil == (0.0, 0.0, 0.0) and diag < 0.5: continue                    # βέλη, σύμβολα στάθμης / τομής
    if col == (0.65, 0.32, 0.0) and "c" in kinds: continue                # κύκλοι σημείων όψεων
    if col == (0.24, 0.53, 0.62) and w < 3: continue                      # βέλη κλίσης 1 %
    if col == (0.0, 0.0, 0.0) and "c" in kinds and diag < 0.8: continue   # μικρά σύμβολα, κύκλοι τομών A-30
    items = []
    for it in d["items"]:
        if it[0] == "l":
            a, b = it[1] * M, it[2] * M; items.append(["l", *m(a), *m(b)])
        elif it[0] == "c":
            items.append(["c", *m(it[1] * M), *m(it[2] * M), *m(it[3] * M), *m(it[4] * M)])
        elif it[0] == "re":
            rr = it[1] * M; rr.normalize(); items.append(["re", *m(pymupdf.Point(rr.x0, rr.y0)), *m(pymupdf.Point(rr.x1, rr.y1))])
        elif it[0] == "qu":
            q = it[1]; items.append(["qu", *m(q.ul * M), *m(q.ur * M), *m(q.lr * M), *m(q.ll * M)])
    if items:
        out.append({"c": col, "f": fil, "w": w, "closed": bool(d.get("closePath")), "items": items})
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print(OUT, len(out), "paths")
