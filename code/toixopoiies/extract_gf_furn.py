"""Έπιπλα ισογείου από το layer EPIPLA του A-10-GF (EDGE): κρεβάτια, καναπές, πολυθρόνα, τραπέζι, καρέκλες, κουζίνα (πάγκος,
εστίες, νεροχύτης). Κρατάμε μόνο ό,τι είναι μέσα στα δωμάτια (όχι τοίχοι / hatch / πόρτες / ετικέτες / σύμβολα στάθμης) και
ΟΧΙ στις περιοχές που ξανασχεδιάζουμε εμείς (λουτρό, WC, αποθήκες → ντουλάπες, χωλ/πλυντήριο, lobby).
Χρήση: python3 -I extract_gf_furn.py <A-10-GF.pdf> data/gf_furn.json"""
import sys, json, pymupdf
SRC, OUT = sys.argv[1], sys.argv[2]
S, X0, Y0 = 56.693, 525.3, 397.4
KEEP = [(1.10, 0.80, 4.60, 3.70), (6.60, 0.75, 9.40, 2.90), (1.72, 5.17, 9.40, 9.15)]      # Υπν.1 · Υπν.2 · καθιστικό-κουζίνα (R06: χωρίς τα τσιμπήματα hatch στις παρειές 1,70 / 5,15)
EXCLUDE = [(6.40, 5.10, 9.45, 6.30), (8.10, 5.10, 9.45, 9.20), (4.95, 8.05, 6.15, 9.20), (7.75, 8.25, 8.75, 9.20),
           (3.65, 2.40, 4.60, 3.70), (1.05, 0.80, 3.15, 3.40),
           (6.20, 6.60, 8.00, 8.10), (2.60, 3.60, 2.80, 3.75), (3.40, 3.20, 3.70, 3.45)]
# WC + εσοχή ψυγείου · κουζίνα (R05/R06: δική μας) · τόξα Θ0.03/W0.03 · τόξο πόρτας Υπν.1 · κρεβάτι + κομοδίνα Υπν.1 (EQUIP) ·
# R06: τραπεζαρία + 6 καρέκλες (αντικαθίσταται από τη νησίδα-τραπεζαρία) · δύο μικρά υπολείμματα γραμμών στην εσοχή του Υπν.1
page = pymupdf.open(SRC)[0]; M = page.rotation_matrix


def m(p):
    return round((p.x - X0) / S, 3), round((p.y - Y0) / S, 3)


def inbox(b, x0, y0, x1, y1):
    return b[0] <= x0 and b[1] <= y0 and x1 <= b[2] and y1 <= b[3]


out = []
for d in page.get_drawings():
    r = d["rect"] * M
    x0, y0 = m(pymupdf.Point(r.x0, r.y0)); x1, y1 = m(pymupdf.Point(r.x1, r.y1))
    if not any(inbox(b, x0, y0, x1, y1) for b in KEEP): continue
    if any(x0 < b[2] and x1 > b[0] and y0 < b[3] and y1 > b[1] for b in EXCLUDE): continue
    col = tuple(round(v, 2) for v in d["color"]) if d.get("color") else None
    w = round(d.get("width") or 0, 2)
    if d.get("fill") is not None or col is None: continue
    if not (0.3 <= w <= 0.8): continue                                  # 0,12/0,24 διαστάσεις · ≥ 1,44 τοίχοι
    if col not in ((0.0, 0.0, 0.0), (0.6, 0.6, 0.6), (0.5, 0.5, 0.5), (0.46, 0.46, 0.46)): continue
    kinds = set(it[0] for it in d["items"])
    if w >= 0.6 and "c" in kinds: continue                              # κύκλοι ετικετών / σύμβολα στάθμης
    items = []
    for it in d["items"]:
        if it[0] == "l":
            items.append(["l", *m(it[1] * M), *m(it[2] * M)])
        elif it[0] == "c":
            items.append(["c", *m(it[1] * M), *m(it[2] * M), *m(it[3] * M), *m(it[4] * M)])
        elif it[0] == "re":
            rr = it[1] * M; rr.normalize(); items.append(["re", *m(pymupdf.Point(rr.x0, rr.y0)), *m(pymupdf.Point(rr.x1, rr.y1))])
        elif it[0] == "qu":
            q = it[1]; items.append(["qu", *m(q.ul * M), *m(q.ur * M), *m(q.lr * M), *m(q.ll * M)])
    if items:
        out.append({"c": col, "f": None, "w": w, "closed": bool(d.get("closePath")), "items": items})
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print(OUT, len(out), "paths")
