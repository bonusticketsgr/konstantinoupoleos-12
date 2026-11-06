"""Έλεγχος αλυσίδων διαστάσεων (R11/R22, Γιάννης 07/11: «κάνε τελικό έλεγχο διαστάσεων ότι δεν σου έχει ξεφύγει κάτι»):
κάθε σημείο κάθε αλυσίδας (DIMS_IN / DIMS_OUT) πρέπει να πέφτει σε παρειά τοίχου / υποστυλώματος / κουφώματος / ντουλάπας /
εξοπλισμού / λουτρού / πόρτας / θερμοπρόσοψης του μοντέλου (ανοχή 6 mm). Αναφέρει ό,τι δεν ταιριάζει.
Χρήση: python3 check_dims.py [gf|b1]"""
import sys, importlib
name = sys.argv[1] if len(sys.argv) > 1 else "gf"
M = importlib.import_module({"gf": "gf_model", "b1": "b1_model", "s": "s_model"}[name])
xs, ys = {}, {}


def add(x0, y0, x1, y1, what):
    for v in (x0, x1): xs.setdefault(round(v, 3), set()).add(what)
    for v in (y0, y1): ys.setdefault(round(v, 3), set()).add(what)


for w in M.WALLS: add(*M.bbox(w["pts"]), w["id"])
for p in M.COLS: add(*M.bbox(p), "υποστύλωμα")
for p in M.COLS2: add(*M.bbox(p), "στηθαίο")
for p in M.WINS: add(*M.bbox(p), "κούφωμα")
for p in M.ETICS + M.ETICS5: add(*M.bbox(p), "ETICS")
for p in M.FLOORS: add(*M.bbox(p), "δάπεδο εξώστη")
for wd in M.WARDROBES: add(*wd["r"], wd["name"])
for e in getattr(M, "EQUIP", []): add(*e[1:5], e[0])
for b in M.BATHS:
    add(*b["counter"], "πάγκος " + b["name"])
    if b.get("shower"): add(*b["shower"], "ντους " + b["name"])
    (tx, ty), _ = b["toilet"]; add(tx, ty, tx, ty, "άξονας λεκάνης " + b["name"])
    if b.get("screen"): (a, bb) = b["screen"]; add(a[0], a[1], bb[0], bb[1], "γυαλί " + b["name"])
for h, l, j in M.DOORS:
    add(h[0], h[1], j[0], j[1], "πόρτα"); add(l[0], l[1], l[0], l[1], "φύλλο πόρτας")


def find(table, v, tol=0.006):
    hits = set()
    for k, s in table.items():
        if abs(k - v) <= tol: hits |= s
    return hits


bad = 0; n = 0
for kind, chains in (("DIMS_IN", M.DIMS_IN), ("DIMS_OUT", M.DIMS_OUT)):
    for orient, pos, pts in chains:
        for p in pts:
            n += 1
            hits = find(xs if orient == "H" else ys, p)
            if not hits:
                bad += 1
                print("  ΔΕΝ ΤΑΙΡΙΑΖΕΙ: %s %s@%.2f σημείο %.3f" % (kind, orient, pos, p))
print("ΜΟΝΤΕΛΟ %s – σημεία αλυσίδων: %d · χωρίς αντιστοιχία: %d" % (name, n, bad))
