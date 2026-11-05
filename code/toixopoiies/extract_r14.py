"""Εξαγωγή γεωμετρίας από το Β1_ΤΟΙΧΟΠΟΙΙΕΣ_Τ-01_Τ-03_R14.pdf (φύλλο Τ-01) σε συντεταγμένες μοντέλου.

Το R14 παράχθηκε από κώδικα που χάθηκε· το PDF είναι διανυσματικό, οπότε ανακτούμε
τοίχους / κολόνες / κουφώματα / θερμοπρόσοψη (γεμίσματα ανά χρώμα), τις γραμμές
(έπιπλα, εξώστες, κάγκελα, ζαρντινιέρες) και τα κείμενα. Κλίμακα 1:60 → 47,244 pt/m.
Αρχή μοντέλου: εξωτερική Β παρειά Τ4-01 (y=0) / εξωτερική Δ παρειά Τ4-05 (x=0).
Χρήση:  python3 extract_r14.py <R14.pdf> data/b1_geom_r14.json
"""
import sys, json, re, collections
import pymupdf

OX, OY, S = 309.5, 99.8, 72 / 25.4 * 1000 / 60   # pt origin και pt/m (1:60)
FILLS = {(0.82, 0.47, 0.3): "T1", (0.95, 0.72, 0.58): "T4", (0.93, 0.64, 0.52): "T5",
         (0.78, 0.86, 0.95): "T3", (0.8, 0.78, 0.92): "T9", (0.72, 0.8, 0.9): "T2",
         (0.8, 0.86, 0.93): "T2N", (0.45, 0.6, 0.85): "T2A", (0.62, 0.45, 0.75): "T7",
         (0.55, 0.75, 0.6): "T6", (0.85, 0.8, 0.65): "T8", (0.36, 0.36, 0.38): "COL",
         (0.62, 0.62, 0.64): "COL2", (0.99, 0.93, 0.7): "ETICS", (0.9, 0.93, 0.97): "WIN",
         (0.98, 0.97, 0.95): "FLOOR", (1.0, 1.0, 1.0): "WHITE"}   # FLOOR: δάπεδα εξωστών · WHITE: περσίδες σκιάστρου / κουτιά ετικετών

def m(p):
    return [round((p[0] - OX) / S, 4), round((p[1] - OY) / S, 4)]

def main(pdf, out):
    page = pymupdf.open(pdf)[0]
    polys, strokes = [], collections.defaultdict(list)
    for d in page.get_drawings():
        if d.get("fill"):
            key = tuple(round(c, 2) for c in d["fill"])
            t = FILLS.get(key)
            if not t:
                continue
            if t == "WHITE":
                continue   # λευκά = φόντα ετικετών / κειμένων (ξαναπαράγονται)
            pts = []
            for it in d["items"]:
                if it[0] == "re":
                    r = it[1]; pts += [m((r.x0, r.y0)), m((r.x1, r.y0)), m((r.x1, r.y1)), m((r.x0, r.y1))]
                elif it[0] == "l":
                    pts += [m(it[1]), m(it[2])]
                elif it[0] == "c":
                    pts += [m(it[1]), m(it[4])]
            # αφαίρεση διαδοχικών διπλών
            clean = []
            for p in pts:
                if not clean or clean[-1] != p:
                    clean.append(p)
            polys.append({"type": t, "pts": clean})
        else:
            col = tuple(round(c, 2) for c in (d.get("color") or (0, 0, 0)))
            key = "%s|%.2f" % (col, d.get("width") or 0)
            segs = []
            for it in d["items"]:
                if it[0] == "l":
                    segs.append(["l", m(it[1]), m(it[2])])
                elif it[0] == "re":
                    r = it[1]; segs.append(["re", m((r.x0, r.y0)), m((r.x1, r.y1))])
                elif it[0] == "c":
                    segs.append(["c", m(it[1]), m(it[2]), m(it[3]), m(it[4])])
            strokes[key].append(segs)
    texts = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                x0, y0, x1, y1 = s["bbox"]
                texts.append({"text": s["text"], "bbox": m((x0, y0)) + m((x1, y1)),
                              "size": s["size"], "dir": list(l["dir"]), "font": s["font"]})
    json.dump({"polys": polys, "strokes": strokes, "texts": texts}, open(out, "w"), ensure_ascii=False)
    print("polys", len(polys), "stroke groups", len(strokes), "texts", len(texts))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
