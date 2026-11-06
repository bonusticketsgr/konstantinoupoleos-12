"""Έλεγχος «λευκών κουκίδων»: ακάλυπτα τετραγωνάκια στις γωνίες τοίχων (R05, ερώτηση Γιάννη 05/11/2026).
Raster 1 cm των τοίχων + υποστυλωμάτων + κουφωμάτων. Αναφέρει (α) κλειστές τρύπες ≤ 0,04 m² (π.χ. το 5×5 Τ3-02/Τ7-01/Κ2 του R04)
και (β) «σημειακές επαφές»: δύο τοίχοι που ακουμπούν μόνο στη γωνία τους (διαγώνια) – ανάμεσα στα άκρα τους μένει λευκό
τετραγωνάκι (π.χ. Τ2N-01/Τ2N-03 του R04 στο 5,45–5,55 × 5,05–5,15).
Χρήση: python3 check_corners.py [gf|b1]"""
import sys, importlib
name = sys.argv[1] if len(sys.argv) > 1 else "gf"
M = importlib.import_module({"gf": "gf_model", "b1": "b1_model", "s": "s_model"}[name])
R = 100  # κελιά / m
rects = [M.bbox(w["pts"]) for w in M.WALLS if M.is_rect(w["pts"])] + [M.bbox(p) for p in M.COLS] + [M.bbox(p) for p in M.WINS]
x0 = min(r[0] for r in rects) - 0.2; y0 = min(r[1] for r in rects) - 0.2
x1 = max(r[2] for r in rects) + 0.2; y1 = max(r[3] for r in rects) + 0.2
W, Hh = int((x1 - x0) * R) + 1, int((y1 - y0) * R) + 1
cov = bytearray(W * Hh)
for (a, b, c, d) in rects:
    i0, i1 = int(round((a - x0) * R)), int(round((c - x0) * R)); j0, j1 = int(round((b - y0) * R)), int(round((d - y0) * R))
    for j in range(j0, j1):
        cov[j * W + i0:j * W + i1] = b"\x01" * (i1 - i0)


def C(i, j):
    return 0 <= i < W and 0 <= j < Hh and cov[j * W + i]


# (α) κλειστές τρύπες
seen = bytearray(W * Hh); holes = []
for s in range(W * Hh):
    if cov[s] or seen[s]:
        continue
    stack = [s]; seen[s] = 1; comp = []; open_ = False
    while stack:
        t = stack.pop(); comp.append(t); i, j = t % W, t // W
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ii, jj = i + di, j + dj
            if not (0 <= ii < W and 0 <= jj < Hh):
                open_ = True; continue
            u = jj * W + ii
            if not cov[u] and not seen[u]:
                seen[u] = 1; stack.append(u)
    if len(comp) <= 400 and not open_:
        xs = [t % W for t in comp]; ys = [t // W for t in comp]
        holes.append((round(x0 + min(xs) / R, 3), round(y0 + min(ys) / R, 3), round(x0 + (max(xs) + 1) / R, 3), round(y0 + (max(ys) + 1) / R, 3), len(comp)))
# (β) εγκοπές
L = 12
notches = set()
for j in range(1, Hh - 1):
    for i in range(1, W - 1):
        if cov[j * W + i]:
            continue
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            # δύο τοίχοι που ακουμπούν μόνο σε ένα σημείο (διαγώνια): τοίχος δίπλα (x) και τοίχος δίπλα (y), αλλά η διαγώνια
            # γωνία ακάλυπτη → λευκό τετραγωνάκι ανάμεσα στα άκρα τους
            if C(i + sx, j) and C(i, j + sy) and not C(i + sx, j + sy):
                notches.add((round(x0 + i / R, 2), round(y0 + j / R, 2)))
# ομαδοποίηση εγκοπών ανά 10 cm
groups = {}
for (x, y) in notches:
    groups.setdefault((round(x, 1), round(y, 1)), []).append((x, y))
print("ΜΟΝΤΕΛΟ", name, "– κλειστές τρύπες:", len(holes))
for h in holes:
    print("   τρύπα", h)
print("εγκοπές (ομάδες ~10 cm):", len(groups))
for k in sorted(groups):
    xs = [p[0] for p in groups[k]]; ys = [p[1] for p in groups[k]]
    print("   εγκοπή κοντά στο x %.2f–%.2f · y %.2f–%.2f (%d κελιά)" % (min(xs), max(xs) + 0.01, min(ys), max(ys) + 0.01, len(groups[k])))
