"""Υπόβαθρο κήπου / περιβάλλοντος χώρου ισογείου: απόσπασμα του A-10-GF (EDGE) ως αχνή εικόνα, με το κτίριο μασκαρισμένο.
Χρήση: python3 -I make_gf_underlay.py <A-10-GF.pdf> data/gf_underlay.png
Βαθμονόμηση όπως extract_gf.py (1:50 → 56,693 pt/m, αρχή μοντέλου X0 525,3 / Y0 397,4 pt display)."""
import sys, io, pymupdf
from PIL import Image, ImageDraw
SRC, OUT = sys.argv[1], sys.argv[2]
S, X0, Y0 = 56.693, 525.3, 397.4
BBOX = (-6.0, -2.4, 18.4, 15.6)            # m μοντέλου (πρέπει να ταυτίζεται με gf_model.UNDERLAY["bbox"])
DPI, FADE = 110, 0.60                      # FADE: ποσοστό αντίθεσης που κρατιέται (1 = κανονικό, 0 = λευκό)
BUILDING = [(0.70, 0.40), (9.80, 0.40), (9.80, 2.70), (13.45, 2.70), (13.45, 9.55), (1.30, 9.55), (1.30, 5.25), (0.70, 5.25)]
page = pymupdf.open(SRC)[0]
x0, y0, x1, y1 = BBOX
clip = pymupdf.Rect(X0 + x0 * S, Y0 + y0 * S, X0 + x1 * S, Y0 + y1 * S)
pix = page.get_pixmap(matrix=pymupdf.Matrix(DPI / 72, DPI / 72), clip=clip)
img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
ppm = S * DPI / 72
W, H = img.size
# αχνό: p' = 255 − (255 − p)·FADE
img = Image.eval(img, lambda p: int(255 - (255 - p) * FADE))
mask = Image.new("L", (W, H), 255)
ImageDraw.Draw(mask).polygon([((x - x0) * ppm, (y - y0) * ppm) for x, y in BUILDING], fill=0)
img.putalpha(mask)
img.save(OUT, optimize=True)
print(OUT, img.size)
