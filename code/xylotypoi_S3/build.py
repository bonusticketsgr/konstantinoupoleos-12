"""Build the clean, fully dimensioned 1:80 formwork plan (A3) from geometry.json."""
import pymupdf, json, math, datetime
from shapely.geometry import Polygon, LineString

S = 56.6929            # pt per metre in the source (1:50)
K = 50.0 / 80.0        # source pt -> output pt (1:80)
MM = 72 / 25.4

G = json.load(open("geometry.json"))
FONT_R = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
FONT_B = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")

PAGE_W, PAGE_H = 420 * MM, 297 * MM
OX, OY = 45 * MM, 24 * MM          # output position of source point (579.33, 504.93)
SX0, SY0 = 579.33, 504.93
def X(x): return OX + (x - SX0) * K
def Y(y): return OY + (y - SY0) * K
def P(x, y): return pymupdf.Point(X(x), Y(y))

BLUE = (0, 0.43, 0.85)
BLACK = (0, 0, 0)
GRAY = (0.35, 0.35, 0.35)

doc = pymupdf.open()
page = doc.new_page(width=PAGE_W, height=PAGE_H)
shape = page.new_shape()

def flush():
    global shape
    shape.commit(); shape = page.new_shape()

# ---------------------------------------------------------------- primitives
def oline(x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
    shape.draw_line(pymupdf.Point(x0, y0), pymupdf.Point(x1, y1))
    shape.finish(width=w, color=color, dashes=dashes, lineCap=0)
def sline(x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
    oline(X(x0), Y(y0), X(x1), Y(y1), w, color, dashes)
def orect(x0, y0, x1, y1, w=0.5, color=BLACK, fill=None):
    shape.draw_rect(pymupdf.Rect(x0, y0, x1, y1)); shape.finish(width=w, color=color, fill=fill)

def text_w(s, size, bold=False):
    return (FONT_B if bold else FONT_R).text_length(s, fontsize=size)

def otext(x, y, s, size=7, bold=False, rot=0, align="left", color=BLACK):
    """text in OUTPUT coords. (x,y) = baseline start; align left/center/right.
    rot=90 -> reads bottom-to-top, (x,y) is the baseline start at the bottom, glyphs extend to the left of x."""
    flush()
    font = FONT_B if bold else FONT_R
    w = font.text_length(s, fontsize=size)
    off = -w / 2 if align == "center" else (-w if align == "right" else 0)
    tw = pymupdf.TextWriter(page.rect)
    tw.append(pymupdf.Point(x + off, y), s, font=font, fontsize=size)
    if rot == 0:
        tw.write_text(page, color=color)
    else:
        m = pymupdf.Matrix(1, 0, 0, 1, 0, 0).prerotate(rot)
        tw.write_text(page, color=color, morph=(pymupdf.Point(x, y), m))
    return w
def stext(x, y, s, **kw): return otext(X(x), Y(y), s, **kw)

def hatch_polygon(pts_src, spacing=2.6, angle=45, w=0.25, color=BLACK):
    poly = Polygon([(X(x), Y(y)) for x, y in pts_src])
    minx, miny, maxx, maxy = poly.bounds
    d = max(maxx - minx, maxy - miny) * 2
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    a = math.radians(angle); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    n = int(d / spacing) + 1
    for i in range(-n, n + 1):
        ox, oy = cx + nx * i * spacing, cy + ny * i * spacing
        inter = LineString([(ox - ux * d, oy - uy * d), (ox + ux * d, oy + uy * d)]).intersection(poly)
        for gseg in getattr(inter, "geoms", [inter]):
            if gseg.is_empty or gseg.geom_type != "LineString": continue
            c = list(gseg.coords); oline(c[0][0], c[0][1], c[-1][0], c[-1][1], w, color)

# ---------------------------------------------------------------- geometry
for poly in G["columns"]:
    hatch_polygon(poly)
    pts = [P(x, y) for x, y in poly] + [P(*poly[0])]
    shape.draw_polyline(pts); shape.finish(width=1.1, color=BLACK)
WMAP = {1.7: 1.1, 0.85: 0.6, 0.57: 0.3, 0.28: 0.22}
for l in G["lines"]:
    sline(l["x0"], l["y0"], l["x1"], l["y1"], w=WMAP[l["w"]], color=BLUE if l["blue"] else BLACK)
for c in G["curves"]:
    p = [P(x, y) for x, y in c["pts"]]
    shape.draw_bezier(*p); shape.finish(width=WMAP[c["w"]], color=BLUE if c["blue"] else BLACK)

# ---------------------------------------------------------------- dimensioning
DIM_SIZE = 7.2
TICK = 2.2 * MM
def fmt(v):
    c = v * 100
    if abs(c - round(c)) < 0.35: return "%.2f" % (round(c) / 100)
    return "%.3f" % v
def tick(xo, yo, color=BLACK):
    oline(xo - TICK / 2 * 0.7071, yo + TICK / 2 * 0.7071, xo + TICK / 2 * 0.7071, yo - TICK / 2 * 0.7071, 0.6, color)

def hchain(xs, y_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True):
    """horizontal chain; xs = source x coords; y_out = output y of the line; text_side -1 above / +1 below;
    ext: {x_src: y_src} start of the extension line."""
    xs = sorted(xs); x0, x1 = X(xs[0]), X(xs[-1])
    oline(x0 - 1.0 * MM, y_out, x1 + 1.0 * MM, y_out, 0.35, color)
    for x in xs:
        xo = X(x); tick(xo, y_out, color)
        if ext and x in ext:
            ys = Y(ext[x]); gap = 0.8 * MM
            if ys < y_out: oline(xo, ys + gap, xo, y_out + ext_over, 0.25, color)
            else: oline(xo, ys - gap, xo, y_out - ext_over, 0.25, color)
    last1 = -1e9; last2 = -1e9
    for a, b in zip(xs[:-1], xs[1:]):
        s = fmt((b - a) / S); w = text_w(s, size); mid = (X(a) + X(b)) / 2; L = X(b) - X(a)
        lvl = 0
        if stagger and w + 1.5 > L:
            lvl = 1
            if mid - w / 2 < last1 + 1.0: lvl = 2
        if lvl == 1: last1 = mid + w / 2
        dy = 0.6 * MM + lvl * (size * 0.72 + 1.6)
        yb = y_out - dy if text_side < 0 else y_out + dy + size * 0.72
        otext(mid, yb, s, size=size, align="center", color=color)

def vchain(ys, x_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True, narrow_h=False):
    ys = sorted(ys); y0, y1 = Y(ys[0]), Y(ys[-1])
    oline(x_out, y0 - 1.0 * MM, x_out, y1 + 1.0 * MM, 0.35, color)
    for y in ys:
        yo = Y(y); tick(x_out, yo, color)
        if ext and y in ext:
            xs_ = X(ext[y]); gap = 0.8 * MM
            if xs_ > x_out: oline(xs_ - gap, yo, x_out - ext_over, yo, 0.25, color)
            else: oline(xs_ + gap, yo, x_out + ext_over, yo, 0.25, color)
    last1 = -1e9
    for a, b in zip(ys[:-1], ys[1:]):
        s = fmt((b - a) / S); w = text_w(s, size); mid = (Y(a) + Y(b)) / 2; L = Y(b) - Y(a)
        lvl = 0
        if stagger and w + 1.5 > L:
            lvl = 1
            if mid - w / 2 < last1 + 1.0: lvl = 2
        if lvl == 1: last1 = mid + w / 2
        if narrow_h and lvl > 0:
            # horizontal text beside the line, vertically centred on the (narrow) segment
            xh = x_out - 1.5 * MM - w if text_side < 0 else x_out + 1.5 * MM
            otext(xh, mid + size * 0.36, s, size=size, color=color)
            continue
        dx = 0.6 * MM + lvl * (size * 0.72 + 1.6)
        xb = x_out - dx if text_side < 0 else x_out + dx + size * 0.72
        otext(xb, mid + w / 2, s, size=size, rot=90, color=color)

ROW = 8.0 * MM
# ---- NORTH
top_edge = Y(581.89)
ext_n = {807.38: 581.89, 920.75: 615.91, 937.76: 615.91, 1136.18: 615.91, 1147.52: 587.57, 1249.57: 615.91,
         1408.30: 615.91, 1425.31: 615.91, 1524.53: 624.41, 1632.24: 757.64, 1666.11: 1015.45,
         929.255: 615.91, 1192.875: 615.91, 1416.805: 615.91, 1625.15: 757.64}
hchain([807.38, 920.75, 937.76, 1136.18, 1147.52, 1249.57, 1408.30, 1425.31, 1524.53, 1632.24, 1666.11], top_edge - ROW, -1, ext=ext_n)
hchain([807.38, 929.255, 1192.875, 1416.805, 1625.15, 1666.11], top_edge - 2 * ROW, -1, ext={k: ext_n[k] for k in (929.255, 1192.875, 1416.805, 1625.15)})
hchain([807.38, 1632.24, 1666.11], top_edge - 3 * ROW, -1)
# ---- SOUTH
bot_edge = Y(1230.89)
ext_s = {807.38: 1230.89, 954.77: 1230.89, 1068.16: 1123.17, 1385.62: 1123.17, 1394.13: 1230.89, 1413.97: 1168.52,
         1425.31: 1168.52, 1595.39: 1168.52, 1632.24: 1168.1, 1666.11: 1133.37,
         1011.465: 1123.17, 1405.465: 1123.17, 1613.815: 1123.17}
hchain([807.38, 954.77, 1068.16, 1385.62, 1394.13, 1413.97, 1425.31, 1595.39, 1632.24, 1666.11], bot_edge + ROW, +1, ext=ext_s)
hchain([807.38, 1011.465, 1405.465, 1613.815, 1666.11], bot_edge + 2 * ROW, +1, ext={k: ext_s[k] for k in (1011.465, 1405.465, 1613.815)})
hchain([807.38, 1632.24, 1666.11], bot_edge + 3 * ROW, +1)
# ---- WEST (outermost element = balcony x=779.02)
west_edge = X(779.02)
ext_w = {581.89: 807.38, 615.91: 807.38, 655.59: 920.75, 754.81: 807.38, 862.38: 920.75, 879.39: 909.42,
         885.06: 779.02, 1104.46: 779.02, 1123.17: 807.38, 1230.89: 807.38,
         635.75: 920.75, 870.885: 920.75, 1114.665: 954.77}
vchain([581.89, 615.91, 655.59, 754.81, 862.38, 879.39, 885.06, 1104.46, 1123.17, 1230.89], west_edge - ROW, -1, ext=ext_w)
vchain([581.89, 635.75, 870.885, 1114.665, 1230.89], west_edge - 2 * ROW, -1, ext={k: ext_w[k] for k in (635.75, 870.885, 1114.665)})
vchain([581.89, 1230.89], west_edge - 3 * ROW, -1)
# ---- EAST (outermost element = stair strip x=1666.11)
east_edge = X(1666.11)
ext_e = {615.91: 1425.31, 624.41: 1524.53, 737.8: 1524.53, 757.64: 1632.24, 876.55: 1632.24, 1015.45: 1666.11,
         1106.16: 1632.24, 1123.17: 1632.24, 1133.37: 1666.11, 1168.5: 1631.53,
         764.725: 1632.24, 869.465: 1632.24, 1114.665: 1632.24}
vchain([615.91, 624.41, 737.8, 757.64, 876.55, 1015.45, 1106.16, 1123.17, 1133.37, 1168.5], east_edge + ROW, +1, ext=ext_e)
vchain([615.91, 764.725, 869.465, 1114.665, 1168.5], east_edge + 2 * ROW, +1, ext={k: ext_e[k] for k in (764.725, 869.465, 1114.665)})
vchain([615.91, 757.64, 1123.17, 1168.5], east_edge + 3 * ROW, +1)

# ---- decorative front (μετώπη) K23-K25
mx = X(579.33)
vchain([504.93, 516.27, 657.58, 668.92, 792.51, 803.84], mx - ROW, -1,
       ext={504.93: 579.33, 516.27: 579.33, 657.58: 579.61, 668.92: 579.61, 792.51: 579.9, 803.84: 579.9})
vchain([504.93, 657.58, 803.84], mx - 2 * ROW, -1)
vchain([504.93, 803.84], mx - 3 * ROW, -1)
hchain([579.33, 633.19], Y(504.93) - 1.6 * ROW, -1, ext={579.33: 504.93, 633.19: 504.93})
# offset front -> K1 (designer's value 6.01) and vertical offset 1.96 (K25 top -> K1 top face)
y601 = Y(504.93) - 2.6 * ROW
oline(X(579.33) - 1 * MM, y601, X(920.75) + 1 * MM, y601, 0.35)
for xx, ys in ((579.33, 504.93), (920.75, 615.91)):
    oline(X(xx), Y(ys) - 0.8 * MM, X(xx), y601 - 1.2 * MM, 0.25); tick(X(xx), y601)
otext((X(579.33) + X(920.75)) / 2, y601 - 0.6 * MM, "6.01", size=DIM_SIZE, align="center")
vchain([504.93, 615.91], X(760), +1, ext={504.93: 633.19, 615.91: 807.38})

# ---- interior dimensions
def idim_h(xs, y_src, side=-1, ext_to=None): hchain(xs, Y(y_src), side, size=6.8, ext=ext_to, ext_over=0.8 * MM)
def idim_v(ys, x_src, side=-1, ext_to=None, narrow_h=True): vchain(ys, X(x_src), side, size=6.8, ext=ext_to, ext_over=0.8 * MM, narrow_h=narrow_h)
idim_v([587.57, 615.91], 1120, -1, ext_to={587.57: 1147.52, 615.91: 1147.52})            # Π2 overhang 0.50
idim_v([615.91, 632.92, 862.38, 879.39], 1370, +1)                                        # Π3: 0.30 | 4.05 | 0.30
idim_h([807.38, 858.3, 869.6, 915.1, 920.75], 575, -1, ext_to={807.38: 581.89, 915.1: 593.2, 920.75: 581.89})    # rain-pipe duct (as Σ3): 0.90 | 0.20 | 0.80 | 0.10
idim_h([807.38, 949.1], 906, +1, ext_to={949.1: 896.0})                                    # hidden outline 2.50 (as Σ3)
idim_h([818.71, 875.4, 920.75], 762, +1)                                                  # void: 1.00 | 0.80
idim_v([754.81, 845.37, 879.39], 866, -1, ext_to={845.37: 875.4, 879.39: 909.42}, narrow_h=False)  # void: 1.60 | 0.60
idim_h([1516.0, 1618.06], 850, -1)                                                        # shaft 1.80
idim_v([771.81, 862.38], 1535, +1)                                                        # shaft 1.60
idim_h([1425.31, 1493.34], 930, -1)                                                       # Π6 width 1.20
idim_h([1493.34, 1550.03], 935, -1)                                                       # landing 1.00
idim_v([876.55, 944.6, 950.3, 1018.3], 1482, -1, ext_to={944.6: 1493.34, 950.3: 1493.34})  # stair: 1.20 | 0.10 | 1.20
idim_v([1018.3, 1032.5, 1106.16, 1123.17, 1168.5], 1445, +1)                              # 0.25 | 1.30 | 0.30 | 0.80
idim_v([1015.45, 1123.17], 1003, +1, ext_to={1015.45: 983.1})                             # hidden zone 1.90
idim_h([954.77, 1153.19], 1065, +1, ext_to={1153.19: 1094.8})                             # hidden zone 3.50
idim_h([779.02, 807.38], 878, -1, ext_to={779.02: 885.06, 807.38: 885.06})                # balcony width 0.50

# ---------------------------------------------------------------- labels
CS = 8.4
def col_label(x, y, s, rot=0, align="left"): stext(x, y, s, size=CS, bold=True, rot=rot, align=align)
col_label(943.0, 611.0, "Κ1  30/70")
col_label(1150.0, 647.0, "Κ2  200/30")
col_label(1288.0, 748.0, "Κ3  30/215")
col_label(1546.0, 752.0, "Κ4  230/25")
col_label(1650.0, 866.0, "Κ5  25/210", rot=90)
stext(1650.0, 964.0, "Κ6  230/25", size=7.6, bold=True, rot=90)
col_label(1575.0, 1152.0, "Κ7  65/30")
col_label(1300.0, 1149.4, "Κ8  70/30")
col_label(1020.0, 1145.3, "Κ9  200/30")
col_label(973.9, 839.2, "Κ10  90/30")
for nm, cx, cy in (("Κ25", 606.2, 481.0), ("Κ24", 606.4, 636.0), ("Κ23", 606.8, 822.0)):
    stext(cx, cy, nm, size=7.6, bold=True, align="center"); stext(cx, cy + 14.5, "95/20", size=7.0, bold=True, align="center")

BS = 7.2
def beam_label(x, y, s, rot=0, size=BS, align="left"): stext(x, y, s, size=size, rot=rot, align=align)
beam_label(1000.0, 629.0, "Δ1.1  30/40  L=3.50")
beam_label(1250.0, 629.1, "Δ1.4  30/55  L=2.80")
beam_label(1422.0, 745.0, "Δ9.5  30/55  L=2.20", rot=90, size=6.6)
beam_label(933.8, 800.0, "Δ6.1  30/55  L=3.65", rot=90)
beam_label(1427.0, 751.5, "Δ2.1  40/40  L=1.35")
beam_label(1513.0, 863.5, "Δ5.1  25/40  L=1.60", rot=90, size=5.8)
beam_label(832.0, 880.0, "Δ  20/112  L=2.30", rot=90, size=7.0)
beam_label(1150.0, 875.5, "Δ3.1  30/50  L=7.70")
beam_label(1421.2, 1060.0, "Δ9.1  30/50  L=4.00", rot=90)
beam_label(1497.0, 1100.0, "Δ10.2  25/50  L=4.05"); sline(1614.0, 1097.5, 1620.0, 1097.5, 0.3); sline(1620.0, 1097.5, 1624.0, 1094.0, 0.3)
beam_label(967.6, 1000.0, "Δ7.1  30/55  L=4.00", rot=90)
beam_label(1484.0, 1029.9, "Δ13.1  25/40  L=3.40")
beam_label(1150.0, 1118.6, "Δ4.4  30/55  L=5.60")
beam_label(1480.0, 1119.3, "Δ4.6  30/55  L=3.00", size=6.8)
# strengthened zones
beam_label(810.0, 634.6, "Ε.Ζ.  40/22  L=4.00", size=6.6)
beam_label(1430.0, 845.0, "Ε.Ζ.  25/15", size=6.6); beam_label(1430.0, 856.0, "L=1.35", size=6.6)
beam_label(812.0, 1113.7, "Ε.Ζ.  50/32  L=2.60")
beam_label(973.5, 1228.0, "Ε.Ζ.  50/32  L=1.90", rot=90, size=6.2)
beam_label(622.0, 782.0, "Ε.Ζ.  95/15", rot=90, size=6.8)

# slab labels
def slab_label(cx, cy, name, h, r=3.0 * MM):
    c = pymupdf.Point(X(cx), Y(cy))
    shape.draw_circle(c, r); shape.finish(width=0.35, color=BLACK, fill=(1, 1, 1))
    oline(c.x - r, c.y, c.x + r, c.y, 0.35)
    otext(c.x, c.y - 1.1, name, size=6.8, bold=True, align="center")
    otext(c.x, c.y + 5.8, "h=%s" % h, size=6.0, align="center")
SLABS = [("Π1", 22, 838.05, 691.38), ("Π2", 22, 1035.63, 602.0), ("Π3", 18, 1172.97, 747.51), ("Π4", 18, 1474.85, 680.89),
         ("Π5", 22, 904.38, 791.44), ("Π6", 15, 1447.0, 998.0), ("Π7", 32, 883.83, 975.41), ("Π8", 24, 1189.97, 992.56),
         ("Π9", 15, 1590.07, 988.31), ("Π10", 15, 1509.15, 1062.01), ("Π11", 20, 1650.0, 1060.0), ("Π12", 32, 1188.55, 1176.81),
         ("Π14", 20, 1521.76, 1141.1), ("Π", 20, 793.2, 931.76), ("Π", 15, 606.2, 598.12), ("Π", 15, 606.4, 704.99)]
for name, h, cx, cy in SLABS: slab_label(cx, cy, name, h, r=(2.6 * MM if name == "Π11" else 3.0 * MM))

# level marks
def level_mark(cx, cy, s, r=1.5 * MM, color=BLACK, textpos=None, rot=0):
    c = pymupdf.Point(X(cx), Y(cy))
    shape.draw_circle(c, r); shape.finish(width=0.35, color=color, fill=(1, 1, 1))
    for a0 in (90, 270):
        pts = [c]
        for kk in range(0, 91, 10):
            a = math.radians(a0 + kk); pts.append(pymupdf.Point(c.x + r * math.cos(a), c.y - r * math.sin(a)))
        shape.draw_polyline(pts + [c]); shape.finish(width=0, color=color, fill=color)
    oline(c.x - r * 1.4, c.y, c.x + r * 1.4, c.y, 0.3, color); oline(c.x, c.y - r * 1.4, c.x, c.y + r * 1.4, 0.3, color)
    if textpos is None: textpos = (c.x + r + 1.5, c.y + 2.4)
    otext(textpos[0], textpos[1], s, size=7.4, bold=True, rot=rot, color=color)
level_mark(1293.3, 762.5, "+3,65")
level_mark(805.0, 1046.7, "+3,85", r=1.25 * MM, rot=90, textpos=(X(805) - 1.25 * MM - 3.2, Y(1046.7) + 11))
level_mark(599.0, 728.0, "+2,71", r=1.4 * MM, rot=90, textpos=(X(599) - 1.4 * MM - 1.6, Y(728) + 11))
stext(545.0, 536.0, "+2,71", size=7.2, bold=True, color=BLUE)
stext(768.0, 749.0, "+4,55", size=7.2, bold=True, color=BLUE)
stext(768.0, 811.5, "+3,43", size=7.2, bold=True, color=BLUE)

# R=0.60 of the curved corner
stext(893.0, 897.0, "R=0.60", size=6.2); sline(896.0, 889.0, 889.0, 869.0, 0.25)

# notes with leaders
def note(x_src, y_src, lines, size=6.4, leader_from=None, leader_to=None, rot=0):
    lh = size * 1.25
    for i, ln in enumerate(lines):
        if rot == 0: otext(X(x_src), Y(y_src) + i * lh, ln, size=size)
        else: otext(X(x_src) + i * lh, Y(y_src), ln, size=size, rot=90)
    if leader_from and leader_to:
        sline(leader_from[0], leader_from[1], leader_to[0], leader_to[1], 0.25)
        c = P(*leader_to); shape.draw_circle(c, 0.9); shape.finish(width=0, color=BLACK, fill=BLACK)
def marker(cx, cy, num, r=2.0 * MM):
    c = P(cx, cy)
    shape.draw_circle(c, r); shape.finish(width=0.6, color=BLACK, fill=(1, 1, 1))
    otext(c.x, c.y + 2.6, str(num), size=7.2, bold=True, align="center")
marker(905.0, 602.0, 1)
marker(940.0, 1148.0, 1)
note(515.0, 852.0, ["Θέσεις (1): Η υποδοχή για το", "σιφώνι και η υδρορροή να", "προβλεφθούν πριν τη", "σκυροδέτηση, για να μην", "κόψει ο υδραυλικός τον", "οπλισμό της Ε.Ζ."], size=6.2)

# ---------------------------------------------------------------- tables (right side)
TX0 = 336 * MM; TW = 74 * MM
def table(y0, title, header, rows, colx, size=6.4):
    """simple table; returns y after the table"""
    lh = size * 1.55
    otext(TX0, y0, title, size=7.2, bold=True)
    y = y0 + 3
    oline(TX0, y, TX0 + TW, y, 0.5)
    y += lh
    for cx, h in zip(colx, header): otext(TX0 + cx, y - 2, h, size=size, bold=True)
    oline(TX0, y + 1, TX0 + TW, y + 1, 0.3)
    for row in rows:
        y += lh
        for cx, cell in zip(colx, row): otext(TX0 + cx, y - 2, cell, size=size)
    oline(TX0, y + 1.5, TX0 + TW, y + 1.5, 0.5)
    return y + 1.5

ty = 26 * MM
ty = table(ty, "ΥΠΟΣΤΥΛΩΜΑΤΑ / ΤΟΙΧΙΑ", ["Στοιχείο", "b/h (cm)", "Παρατήρηση"],
           [("Κ1", "30/70", ""), ("Κ2", "200/30", "τοιχίο"), ("Κ3", "30/215", "τοιχίο"), ("Κ4", "230/25", "πυρήνας ανελκ."),
            ("Κ5", "25/210", "πυρήνας ανελκ."), ("Κ6", "230/25", "πυρήνας ανελκ."), ("Κ7", "65/30", ""), ("Κ8", "70/30", ""),
            ("Κ9", "200/30", "τοιχίο"), ("Κ10", "90/30", ""), ("Κ23, Κ24, Κ25", "95/20", "διακοσμ. μετώπη +2,71")],
           [0, 24 * MM, 42 * MM])
ty = table(ty + 6 * MM, "ΔΟΚΟΙ  (L = καθαρό μήκος μεταξύ παρειών στηρίξεων)", ["Δοκός", "b/h (cm)", "L (m)", "Από – έως"],
           [("Δ1.1", "30/40", "3.50", "Κ1 – Κ2"), ("Δ1.4", "30/55", "2.80", "Κ2 – Δ9.5"), ("Δ2.1", "40/40", "1.35", "Κ3 – Κ4"),
            ("Δ3.1", "30/50", "7.70", "Κ10 – Κ3"), ("Δ4.4", "30/55", "5.60", "Κ9 – Κ8"), ("Δ4.6", "30/55", "3.00", "Κ8 – Κ7"),
            ("Δ5.1", "25/40", "1.60", "Κ4 – Κ6"), ("Δ6.1", "30/55", "3.65", "Κ1 – Κ10"), ("Δ7.1", "30/55", "4.00", "Κ10 – Κ9"),
            ("Δ9.1", "30/50", "4.00", "Κ3 – Κ8"), ("Δ9.5", "30/55", "2.20", "Δ1.4 – Κ3"), ("Δ10.2", "25/50", "4.05", "Κ6 – Κ7"),
            ("Δ13.1", "25/40", "3.40", "Δ9.1 – Δ10.2"), ("Δ (κενού)", "20/112", "2.30", "άνοιγμα δυτ. πλευράς"),
            ("Ε.Ζ.", "40/22", "4.00", "Π1/Π2"), ("Ε.Ζ.", "25/15", "1.35", "Κ3 – Κ4/Κ6"), ("Ε.Ζ.", "50/32", "2.60", "Π7 (οριζ.)"),
            ("Ε.Ζ.", "50/32", "1.90", "Π12 (κατακ.)"), ("Ε.Ζ.", "95/15", "–", "μετώπη Κ23–Κ25")],
           [0, 17 * MM, 33 * MM, 45 * MM])
ty = table(ty + 6 * MM, "ΠΛΑΚΕΣ", ["Πλάκα", "h (cm)", "Στάθμη", "Πλάκα", "h (cm)", "Στάθμη"],
           [("Π1", "22", "+3,65", "Π9", "15", "+3,65"), ("Π2", "22", "+3,65", "Π10", "15", "+3,65"),
            ("Π3", "18", "+3,65", "Π11", "20", "+3,65"), ("Π4", "18", "+3,65", "Π12", "32", "+3,65"),
            ("Π5", "22", "+3,65", "Π14", "20", "+3,65"), ("Π6", "15", "+3,65", "Π (εξώστης δυτ.)", "20", "+3,85"),
            ("Π7", "32", "+3,65", "Π (μετώπη) ×2", "15", "+2,71"), ("Π8", "24", "+3,65", "", "", "")],
           [0, 11 * MM, 22 * MM, 37 * MM, 57 * MM, 66 * MM])

# ---------------------------------------------------------------- notes + title block
NY = 222 * MM
notes = ["ΣΗΜΕΙΩΣΕΙΣ",
         "1. Όλες οι διαστάσεις σε μέτρα (m). Διατομές υποστυλωμάτων/δοκών σε cm (b/h). Πάχη πλακών h σε cm.",
         "2. L = καθαρό μήκος δοκού μεταξύ παρειών στηρίξεων. Οι αλυσίδες διαστάσεων περιμετρικά δίνουν: παρειές στοιχείων (1η σειρά), αποστάσεις αξόνων υποστυλωμάτων (2η σειρά), συνολικά (3η σειρά).",
         "3. Το σχέδιο είναι γεωμετρική/κατασκευαστική εκδοχή του εγκεκριμένου ξυλοτύπου Σ3 (Γ. Κόγιας, 02/2024, κλ. 1:50) χωρίς οπλισμούς. Όλες οι διαστάσεις προέκυψαν από τη διανυσματική γεωμετρία του Σ3 και ελέγχθηκαν έναντι των αναγραφόμενων διαστάσεων του μελετητή.",
         "4. Οπλισμοί, αγκυρώσεις και οι τομές 1-1, 2-2, 3-3 των διακοσμητικών μετωπών (κλ. 1:20): βλ. εγκεκριμένο σχέδιο Σ3. Σε περίπτωση διαφοράς υπερισχύει το εγκεκριμένο σχέδιο και ο μελετητής.",
         "5. Στάθμες: πλάκα οροφής ισογείου +3,65 · εξώστης δυτικής πλευράς +3,85 · διακοσμητική μετώπη Κ23–Κ25 +2,71 · φυτευτό τοιχείο δυτικής πλευράς +3,43 έως +4,55 (μπλε).",
         "6. Το διαγραμμισμένο τοιχείο επί της Δ10.2 (κάτω από τη σκάλα) κατασκευάζεται έως το ύψος της σκάλας για τη στήριξή της (βλ. Σ3).",
         "7. Η απόσταση 6.01 της μετώπης από το Κ1 αναγράφεται όπως στο Σ3 (η διανυσματική γεωμετρία δίνει 6.02). Η μετώπη Κ23–Κ25 ακολουθεί τη ρυμοτομική γραμμή."]
yy = NY
otext(12 * MM, yy, notes[0], size=7.4, bold=True); yy += 10
for ln in notes[1:]:
    otext(12 * MM, yy, ln, size=6.6); yy += 9.2

# title block
TB_Y0, TB_Y1 = 262 * MM, 289 * MM
orect(10 * MM, TB_Y0, 410 * MM, TB_Y1, 0.8)
cols = [10 * MM, 140 * MM, 250 * MM, 330 * MM, 370 * MM, 410 * MM]
for cx in cols[1:-1]: oline(cx, TB_Y0, cx, TB_Y1, 0.5)
def cell(x, y, label, lines, lsize=5.6, vsize=7.0, bold=True):
    otext(x + 2 * MM, y + 3.2 * MM, label, size=lsize, color=GRAY)
    for i, ln in enumerate(lines): otext(x + 2 * MM, y + 7.2 * MM + i * (vsize + 2.2), ln, size=vsize, bold=bold)
cell(cols[0], TB_Y0, "ΕΡΓΟ", ["ΑΝΕΓΕΡΣΗ ΠΕΝΤΑΟΡΟΦΟΥ ΚΤΗΡΙΟΥ ΚΑΤΟΙΚΙΩΝ ΜΕ ΥΠΟΓΕΙΟ, ΣΟΦΙΤΑ ΚΑΙ ΔΩΜΑ", "ΟΔΟΣ ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ – Ο.Τ. 103-15, ΔΗΜΟΣ ΕΛΛΗΝΙΚΟΥ-ΑΡΓΥΡΟΥΠΟΛΗΣ"], vsize=6.6)
otext(cols[0] + 2 * MM, TB_Y0 + 20.5 * MM, "ΕΡΓΟΔΟΤΗΣ: ARKAD Ι.Κ.Ε.     ΜΕΛΕΤΗΤΗΣ ΣΤΑΤΙΚΩΝ: ΓΙΩΡΓΟΣ ΚΟΓΙΑΣ, ΠΟΛΙΤΙΚΟΣ ΜΗΧΑΝΙΚΟΣ", size=6.2)
cell(cols[1], TB_Y0, "ΘΕΜΑ ΣΧΕΔΙΟΥ", ["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ ΙΣΟΓΕΙΟΥ (+3,65)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"], vsize=8.0)
cell(cols[2], TB_Y0, "ΒΑΣΗ", ["Εγκεκριμένο σχέδιο Σ3", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], vsize=6.6, bold=False)
cell(cols[3], TB_Y0, "ΚΛΙΜΑΚΑ", ["1:80", "A3"], vsize=11.0)
cell(cols[4], TB_Y0, "ΑΡ. ΣΧΕΔΙΟΥ / ΗΜΕΡΟΜΗΝΙΑ", ["Σ3 – ΓΕΩΜΕΤΡΙΑ 1:80", datetime.date.today().strftime("%d/%m/%Y")], vsize=8.6)
# scale bar
sbx, sby = 336 * MM, 254 * MM
for i in range(5):
    orect(sbx + i * (S * K), sby, sbx + (i + 1) * (S * K), sby + 1.6 * MM, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
for i in range(6): otext(sbx + i * (S * K), sby - 1.2 * MM, str(i), size=5.5, align="center")
otext(sbx + 5.4 * (S * K), sby + 1.4 * MM, "m  (1:80)", size=5.5)

flush()
doc.save("S3_clean_1-80.pdf", garbage=4, deflate=True)
print("saved")

