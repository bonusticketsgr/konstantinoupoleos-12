"""Εξαγωγή γεωμετρίας ισογείου από το αρχιτεκτονικό A-10-GF.pdf (EDGE, 1:50, σελίδα περιστραμμένη 270°).
Σύστημα μοντέλου = ίδιο με Β1 (m, x→ανατολή, y→νότο): βαθμονόμηση στο φρεάτιο ανελκυστήρα
(βόρειο τοιχείο 2,30×0,25 στο x 11,05–13,35 / y 3,00–3,25, όπως στο Σ5 του Β1 – ο πυρήνας είναι κοινός).
Χρήση: python3 extract_gf.py <A-10-GF.pdf> data/gf_geom.json
Εξάγει: COL (μαύρα γεμίσματα = σκυρόδεμα), texts (διαστάσεις / ονόματα), stroke segments (μαύρα/γκρι, για τοίχους & κουφώματα)."""
import sys, json, pymupdf

SRC, OUT = sys.argv[1], sys.argv[2]
S = 72 / 25.4 * 20            # pt/m στο 1:50
X0, Y0 = 525.3, 397.4         # pt (display) της αρχής του μοντέλου
doc = pymupdf.open(SRC); page = doc[0]; M = page.rotation_matrix

def m(x, y):
    return round((x - X0) / S, 3), round((y - Y0) / S, 3)

cols, strokes, texts = [], [], []
for d in page.get_drawings():
    f = d.get("fill")
    fk = tuple(round(v, 2) for v in f) if f else None
    if fk == (0, 0, 0):
        r = d["rect"] * M
        if r.width > 2 and r.height > 2:
            cols.append([m(r.x0, r.y0), m(r.x1, r.y1)])
        continue
    for it in d["items"]:
        if it[0] == "l" and d.get("color") is not None:
            ck = tuple(round(v, 2) for v in d["color"]); w = round(d.get("width") or 0, 2)
            if ck in ((0, 0, 0), (0.33, 0.33, 0.33), (0.46, 0.46, 0.46), (0.6, 0.6, 0.6), (0.5, 0.5, 0.5)):
                a, b = it[1] * M, it[2] * M
                strokes.append({"c": ck, "w": w, "a": m(a.x, a.y), "b": m(b.x, b.y)})
for blk in page.get_text("dict")["blocks"]:
    for ln in blk.get("lines", []):
        for sp in ln["spans"]:
            r = pymupdf.Rect(sp["bbox"]) * M
            texts.append({"t": sp["text"], "x": m(r.x0, r.y0)[0], "y": m(r.x0, r.y0)[1], "x1": m(r.x1, r.y1)[0], "y1": m(r.x1, r.y1)[1], "size": round(sp["size"], 1)})
# κρατάμε μόνο ό,τι είναι στην περιοχή του κτιρίου (−4 … 18 m)
inb = lambda x, y: -4 <= x <= 18 and -4 <= y <= 16
cols = [c for c in cols if inb(*c[0])]
strokes = [s for s in strokes if inb(*s["a"]) and inb(*s["b"])]
texts = [t for t in texts if inb(t["x"], t["y"])]
json.dump({"S": S, "X0": X0, "Y0": Y0, "cols": cols, "strokes": strokes, "texts": texts}, open(OUT, "w"), ensure_ascii=False)
print("cols", len(cols), "strokes", len(strokes), "texts", len(texts))
