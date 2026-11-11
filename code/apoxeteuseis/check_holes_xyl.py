"""Οπτικός έλεγχος οπών πάνω στους ΠΡΩΤΟΤΥΠΟΥΣ ξυλοτύπους (Γιάννης 11/11/2026: «έλεγχος … και για τις τρύπες πάλι»).
Για κάθε πλάκα Σ2 … Σ8 και κάθε κουτί 20 × 20 του apox_r22.HOLES: μεγέθυνση 1,3 × 1,3 m του ξυλοτύπου (PDF, διανυσματικό) με
κάναβο 10 cm, το κουτί (κόκκινο) και τον σωλήνα (μπλε) → ένα PNG ανά πλάκα. Τυπώνει και το ποσοστό «μελανιού» μέσα στο κουτί
(διαγράμμιση υποστυλώματος ≈ > 25 %· πλάκα με οπλισμό / κείμενα < 15 %).
Χρήση: python3 check_holes_xyl.py <φάκελος με S2.pdf … S8.pdf> <φάκελος εξόδου>"""
import sys, os, runpy, tempfile
import fitz
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["apox_r22.py", os.path.join(tempfile.mkdtemp(), "x.pdf")]
ns = runpy.run_path(os.path.join(here, "apox_r22.py"), run_name="apox_build")
HOLES, EXIT_BOX = ns["HOLES"], ns["EXIT_BOX"]
S_ = 56.693
CAL = {"Σ2": ("S2", 1203.0, 617.5), "Σ3": ("S3", 877.5, 582.0), "Σ4": ("S4", 523.8, 759.3), "Σ5": ("S5", 462.7, 760.15), "Σ6": ("S6", 458.9, 760.15),
       "Σ7": ("S7", 341.25, 867.8), "Σ8": ("S8", 543.4, 839.7)}
Z, M = 7.0, 0.55
os.makedirs(out, exist_ok=True)
for sl, (nm, X0, Y0) in CAL.items():
    hs = [h for h in HOLES if sl in h["slabs"]]; tiles = []
    for h in hs:
        doc = fitz.open(os.path.join(src, nm + ".pdf")); p = doc[0]
        x0, y0, x1, y1 = h["box"]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        P = lambda x, y: (X0 + x * S_, Y0 + y * S_)
        clipb = fitz.Rect(*P(x0, y0), *P(x1, y1))
        pm0 = p.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=clipb, colorspace=fitz.csGRAY)
        ink = sum(1 for b in pm0.samples if b < 140) / max(1, len(pm0.samples))
        sh = p.new_shape()
        g = round(cx - M, 1)
        while g <= cx + M:
            sh.draw_line(P(g, cy - M), P(g, cy + M)); sh.finish(color=(0.3, 0.7, 1), width=0.12)
            sh.insert_text((P(g, cy - M)[0] + 0.6, P(g, cy - M)[1] + 4.2), ("%.1f" % g), fontsize=3.4, color=(0, 0.3, 0.9)); g = round(g + 0.1, 1)
        g = round(cy - M, 1)
        while g <= cy + M:
            sh.draw_line(P(cx - M, g), P(cx + M, g)); sh.finish(color=(0.3, 0.7, 1), width=0.12)
            sh.insert_text((P(cx - M, g)[0] + 0.6, P(cx - M, g)[1] - 0.6), ("%.1f" % g), fontsize=3.4, color=(0, 0.3, 0.9)); g = round(g + 0.1, 1)
        sh.draw_rect(clipb); sh.finish(color=(1, 0, 0), width=0.9)
        sh.draw_circle(P(h["x"], h["y"]), h["od"] / 2 * S_); sh.finish(color=(0, 0.1, 0.9), width=0.7)
        sh.insert_text((P(cx - M, cy - M)[0] + 2, P(cx - M, cy + M)[1] - 2), "H%d  %s  ink %d%%" % (h["id"], sl, round(ink * 100)), fontsize=5, color=(1, 0, 0))
        sh.commit()
        pm = p.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=fitz.Rect(*P(cx - M, cy - M), *P(cx + M, cy + M)))
        tiles.append(Image.frombytes("RGB", (pm.width, pm.height), pm.samples))
        print("%s Η%-2d %-24s ink %4.1f %%" % (sl, h["id"], h["name"], ink * 100))
    cols = 4; w, hgt = tiles[0].size; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8), rows * (hgt + 8)), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (w + 8), (i // cols) * (hgt + 8)))
    sheet.save(os.path.join(out, "holes_%s.png" % nm))
