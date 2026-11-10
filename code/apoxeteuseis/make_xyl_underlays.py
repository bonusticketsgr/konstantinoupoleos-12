"""Υπόβαθρα ξυλοτύπων για τα φύλλα οπών (ΑΠ-10 …): αχνό raster απόσπασμα κάθε ξυλοτύπου Σ2 … Σ8 (Κόγιας, Drive «ΤΕΛΙΚΑ ΣΩΣΤΑ
ΣΤΑΤΙΚΑ») στο παράθυρο BOX του μοντέλου. Βαθμονόμηση 56,693 pt/m (1:50), αρχή μοντέλου X0 / Y0 σε pt ανά φύλλο (ταύτιση παρειών
υποστυλωμάτων – CLAUDE.md §10Ζ R17).
Χρήση: python3 -I make_xyl_underlays.py <φάκελος με S2.pdf … S8.pdf>   →  data/xyl_S2.png … (+ data/xyl_S2_exit.png)"""
import sys, os
import fitz
from PIL import Image

S_ = 56.693
CAL = {"S2": (1203.0, 617.5), "S3": (877.5, 582.0), "S4": (523.8, 759.3), "S5": (462.7, 760.15), "S6": (458.9, 760.15),
       "S7": (341.25, 867.8), "S8": (543.4, 839.7)}
BOX = (-1.80, -0.50, 13.95, 11.05)        # ίδιο παράθυρο με το φύλλο οπών (HB)
BOX_EXIT = (-1.90, 13.55, 1.60, 15.80)    # Σ2: έξοδος συλλεκτήρα από το νότιο τοιχείο
ZOOM, FADE = 3.6, 0.36                    # ≈ 260 dpi στο 1:50 · αχνό (36 % της έντασης)


def make(src, nm, box, out):
    p = fitz.open(os.path.join(src, nm + ".pdf"))[0]; X0, Y0 = CAL[nm]
    clip = fitz.Rect(X0 + box[0] * S_, Y0 + box[1] * S_, X0 + box[2] * S_, Y0 + box[3] * S_)
    pm = p.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip, colorspace=fitz.csGRAY)
    im = Image.frombytes("L", (pm.width, pm.height), pm.samples)
    im = im.point(lambda v: int(255 - (255 - v) * FADE)).quantize(16)
    im.save(out, optimize=True); print(out, im.size, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    src = sys.argv[1]; here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"); os.makedirs(here, exist_ok=True)
    for nm in CAL:
        make(src, nm, BOX, os.path.join(here, "xyl_%s.png" % nm))
    make(src, "S2", BOX_EXIT, os.path.join(here, "xyl_S2_exit.png"))
