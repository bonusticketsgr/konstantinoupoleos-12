"""zoom.py out.pdf png x0 y0 x1 y1 [zoom] [ox oy]: crop of the OUTPUT pdf given a SOURCE rectangle (pt) — uses same transform as Sheet."""
import pymupdf, sys, json
pdf, png = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
z = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
meta = json.load(open(pdf + ".meta.json"))
K, OX, OY, SX0, SY0 = meta["K"], meta["OX"], meta["OY"], meta["SX0"], meta["SY0"]
def X(x): return OX + (x - SX0) * K
def Y(y): return OY + (y - SY0) * K
doc = pymupdf.open(pdf); pg = doc[0]
clip = pymupdf.Rect(X(x0), Y(y0), X(x1), Y(y1))
pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip); pix.save(png); print(png, pix.width, pix.height)

