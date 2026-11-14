"""Σ2α – ΛΕΠΤΟΜΕΡΕΙΑ ΣΚΑΛΑΣ ΥΠΟΓΕΙΟΥ → ΙΣΟΓΕΙΟΥ (φύλλο Α2, κάτοψη 1:20 · ανάπτυγμα 1:20 · τυπική βαθμίδα 1:10 · πίνακας σταθμών).

    python3 stair_s2.py

Το φύλλο σχεδιάζεται από ΡΗΤΟ μοντέλο (m, κοινό σύστημα όλων των κατόψεων: x → ανατολή, y → νότος):
  · γεωμετρία σκάλας (ρίχτια, φανάρι, γραμμή ανάβασης, πλάκες, δοκοί, τοιχεία) = διανυσματικές γραμμές του Σ2_ΕΦ (Κόγιας, 19/10/2026),
    βαθμονόμηση X0 1203,06 / Y0 618,18 pt, 56,693 pt/m – ίδιες γραμμές με το A-10-B R01 του αρχιτέκτονα·
  · αρίθμηση 1–16 και στάθμες τελικού δαπέδου = A-10-B R01 (−3,00 Υπ.) και Α-30-ΑΑ R01 (+0,45 ισόγειο, επίστρωση 0,10 / 0,15)·
  · στάθμες μπετού πλατύσκαλων = Σ1_ΕΦ (Σ.Μ. −3,10) και Σ2_ΕΦ (+0,30)· πάχη Π6 / Π9 h=15 = Σ2_ΕΦ.
ΠΑΡΑΔΟΧΗ (να επιβεβαιωθεί): επένδυση βαθμίδας T_STEP = 5 cm (μάρμαρο 3 + κονίαμα 2) → στάθμη μπετού πατήματος = τελική − 5 cm."""
import os, sys, math
import pymupdf
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "xylotypoi_S1_S2"))
import lib
from lib import MM, FONT_R, FONT_B, BLACK, GRAY, BLUE

REV, DATE = "R06", "14/11/2026"
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΞΥΛΟΤΥΠΟΙ")
NAME = "Σ2α_Σκάλα_υπογείου_πλατύσκαλο_A3_%s.pdf" % REV

# ---------------------------------------------------------------- μοντέλο
N = 19                                   # ρίχτια συνολικά – R06 (Γιάννης 14/11/2026: ρίχτι ≤ 19, πάτημα ≥ 25, πλάτη 1,20): 2 στο χωλ + 17 στη σκάλα
N_DESIGN = 16                            # η μελέτη (Σ2_ΕΦ / A-10-B): 16 ρίχτια × 21,56 από το −3,00 ως το +0,45
NL = 2                                   # ρίχτια στο χωλ (ένα σκαλί → υπερυψωμένο πλατύσκαλο)
NS = N - NL                              # ρίχτια της σκάλας μέσα στο κλιμακοστάσιο
FFL_STUDY = 0.45                         # τελικό χωλ ισογείου κατά τη μελέτη
FFL0, FFL1 = -3.00, 0.60                 # τελικό δάπεδο υπογείου / χωλ ισογείου (ΝΕΟ +0,60: ένα σκαλί ακόμη στην εξωτερική σκάλα εισόδου)
SSL0, SSL1 = -3.10, 0.30                 # άνω στάθμη μπετού: κοιτόστρωση υπογείου (Σ1) / πλατύσκαλο Π6 (Σ2)
T_STEP = 0.10                            # επένδυση σκαλιών και υπερυψωμένου πλατύσκαλου (Γιάννης 14/11/2026)
H_SLAB = 0.15
RISE = (FFL1 - FFL0) / N                 # 3,60 / 19 = 0,1895
XL, XE = 10.90, 13.10                    # αρχή φαναριού / παρειά ανατολικού τοιχείου
YN, YS = 5.10, 7.60                      # παρειά τοιχείου ανελκυστήρα Κ6 / παρειά δοκού Δ12.1
W0, W1, WX = 6.30, 6.40, 11.90           # φανάρι 1,00 × 0,10 (μελέτη) → κλάδοι και στροφή 1,20
XS = 10.87                               # 1ο ρίχτι της σκάλας (ρίχτι 3): 3 cm πριν από το φανάρι → πάτημα ≥ 25 παντού
WALL_X = 9.50                            # παρειά του τοίχου parking (γυψοσανίδα 9,40–9,50, κάτω από τη Δ9.1)
K3_Y = 5.15
DOOR_Y = (5.20, 6.10)                    # πόρτα parking 0,90: 5 cm από την Κ3, ανοίγει μέσα, μεντεσές νότια
LOBBY = {1: 6.15, 2: 6.40}               # ρίχτια του χωλ (Α–Δ, από τον τοίχο 9,50 ως το φανάρι)
XW = 10.20
YC = (W0 + W1) / 2
RW = 0.60
ARCH_NUM = True
# σκάλα 17 ριχτιών (j = 1…17 → ρίχτια 3…19) = η χάραξη της σκάλας ισογείου → Α΄ (stair_s3) κατοπτρικά
STRAIGHT = {1: XS, 2: 11.12, 3: 11.37, 15: 11.40, 16: 11.15, 17: 10.90}
INNER_PT = {4: (11.51, W1), 5: (11.61, W1), 6: (11.69, W1), 7: (11.77, W1), 8: (11.85, W1), 9: (WX, 6.37),
            10: (11.89, W0), 11: (11.81, W0), 12: (11.73, W0), 13: (11.65, W0), 14: (11.55, W0)}


def _walk_pts():
    pts = [(XS, W1 + RW), (WX, W1 + RW)]
    for i in range(1, 46): a = math.radians(90 - 2 * i); pts.append((WX + RW * math.cos(a), W1 + RW * math.sin(a)))
    for i in range(0, 46): a = math.radians(-2 * i); pts.append((WX + RW * math.cos(a), W0 + RW * math.sin(a)))
    pts.append((XL, W0 - RW))
    return LineString(pts)


def _make_risers():
    wl = _walk_pts(); g = wl.length / (NS - 1); out = {}
    for j, x in STRAIGHT.items(): out[j + NL] = ((x, W1), (x, YS)) if j <= 3 else ((x, W0), (x, YN))
    for j, (ix, iy) in INNER_PT.items():
        w = wl.interpolate((j - 1) * g); dx, dy = w.x - ix, w.y - iy; cand = []
        if dy > 1e-9: cand.append((YS - iy) / dy)
        if dy < -1e-9: cand.append((YN - iy) / dy)
        if dx > 1e-9: cand.append((XE - ix) / dx)
        t = min(c for c in cand if c > 0); ox, oy = ix + t * dx, iy + t * dy
        r5 = lambda v_: round(v_ * 200) / 200.0
        if abs(ox - XE) < 1e-6: oy = r5(oy)
        else: ox = r5(ox)
        out[j + NL] = ((ix, iy), (ox, oy))
    return out


RISERS = _make_risers()
assert sorted(RISERS) == list(range(NL + 1, N + 1))


def walk_path():
    return _walk_pts()


WALK = walk_path()
SPOS = {}
for k_, (a_, b_) in RISERS.items():
    ip = WALK.intersection(LineString([a_, b_]))
    SPOS[k_] = WALK.project(ip if ip.geom_type == "Point" else ip.centroid)
GOING = {k: SPOS[k + 1] - SPOS[k] for k in range(NL + 1, N)}                   # πάτημα στη γραμμή ανάβασης (σκάλα)
STEP_GO = LOBBY[2] - LOBBY[1]                                                    # πάτημα του σκαλιού του χωλ
# πλάτος πατήματος ΣΤΟ ΦΑΝΑΡΙ (εσωτερικό πλάτος): απόσταση διαδοχικών ριχτιών πάνω στην ακμή του φαναριού· το 8 = το στενό άκρο 0,10
def _inner_t(p):
    """θέση πάνω στην περίμετρο του φαναριού (m): νότια ακμή → άκρο → βόρεια ακμή."""
    if abs(p[1] - W1) < 1e-9: return p[0] - XL
    if abs(p[1] - W0) < 1e-9: return (WX - XL) + (W1 - W0) + (WX - p[0])
    return (WX - XL) + (W1 - p[1])
INNER = {k: _inner_t(RISERS[k + 1][0]) - _inner_t(RISERS[k][0]) for k in range(NL + 1, N)}
FFL = {k: FFL0 + k * RISE for k in range(1, N + 1)}
SSL = {k: (min(FFL[k] - T_STEP, SSL1) if k < N else SSL1) for k in range(1, N + 1)}      # το τελευταίο πάτημα δεν ξεπερνά την πλάκα Π6


def cm(v, d=1):
    s = ("%.*f" % (d, v * 100)).rstrip("0").rstrip(".") if d else "%.0f" % (v * 100)
    return s.replace(".", ",")
def mt(v):
    v = round(v, 3)
    return (("%.2f" % v) if abs(v * 100 - round(v * 100)) < 1e-6 else ("%.3f" % v)).replace(".", ",")
def lv(v): return ("%+.2f" % v).replace(".", ",").replace("-", "−")
def lv3(v): return ("%+.3f" % v).replace(".", ",").replace("-", "−")


# ---------------------------------------------------------------- σχεδίαση
CONC = (0.80, 0.80, 0.80); WALLC = (0.90, 0.90, 0.90); RED = (0.80, 0.05, 0.05); FIN = (0.55, 0.36, 0.10)
PLATC = (0.975, 0.90, 0.74); STEPC = (0.99, 0.955, 0.87); DOORC = (0.10, 0.35, 0.60)


class View:
    """τοπικό σύστημα: (x, y) σε m → pt χαρτιού, κλίμακα 1:sc, flip = ο άξονας y του μοντέλου προς τα πάνω (ανάπτυγμα)."""
    def __init__(self, sh, x0_mm, y0_mm, mx0, my0, sc, flip=False):
        self.sh, self.x0, self.y0, self.mx0, self.my0, self.k, self.flip = sh, x0_mm * MM, y0_mm * MM, mx0, my0, 1000.0 / sc * MM, flip
    def X(self, x): return self.x0 + (x - self.mx0) * self.k
    def Y(self, y): return self.y0 - (y - self.my0) * self.k if self.flip else self.y0 + (y - self.my0) * self.k
    def line(self, a, b, w=0.5, color=BLACK, dashes=None): self.sh.oline(self.X(a[0]), self.Y(a[1]), self.X(b[0]), self.Y(b[1]), w, color, dashes)
    def poly(self, pts, w=0.5, color=BLACK, fill=None, dashes=None, close=True):
        self.sh.shape.draw_polyline([pymupdf.Point(self.X(x), self.Y(y)) for x, y in pts]); self.sh.shape.finish(width=w, color=color, fill=fill, dashes=dashes, closePath=close)
    def rect(self, x0, y0, x1, y1, w=0.5, color=BLACK, fill=None): self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w, color, fill)
    def text(self, x, y, s, size=7, dx=0.0, dy=0.0, **kw): self.sh.otext(self.X(x) + dx, self.Y(y) + dy, s, size=size, **kw)
    def hdim(self, xs, y, vals=None, off=0.0, size=7.2, color=BLACK, side=-1, unit=None):
        """οριζόντια αλυσίδα στο y (m) + off (pt)· vals = κείμενα (αλλιώς αποστάσεις σε m)."""
        yo = self.Y(y) + off; sh = self.sh
        sh.oline(self.X(xs[0]) - 3, yo, self.X(xs[-1]) + 3, yo, 0.35, color)
        for x in xs: sh.tick(self.X(x), yo, color)
        for i, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
            s = vals[i] if vals else mt(abs(b - a)); w = FONT_R.text_length(s, fontsize=size); L = abs(self.X(b) - self.X(a))
            sz = size if w + 3 <= L else max(5.0, size * (L - 1.5) / max(w, 1));
            if FONT_R.text_length(s, fontsize=sz) + 2 > L: sz = 5.6; sh.otext((self.X(a) + self.X(b)) / 2, yo + side * (2.2 + (7.4 if i % 2 else 0)) + (sz * 0.72 if side > 0 else 0), s, size=sz, align="center", color=color, mask=True)
            else: sh.otext((self.X(a) + self.X(b)) / 2, yo + side * 2.2 + (sz * 0.72 if side > 0 else 0), s, size=sz, align="center", color=color)
    def vdim(self, ys, x, vals=None, off=0.0, size=7.2, color=BLACK, side=-1, mask=False, tight=False):
        xo = self.X(x) + off; sh = self.sh
        y0, y1 = sorted((self.Y(ys[0]), self.Y(ys[-1])))
        sh.oline(xo, y0 - 3, xo, y1 + 3, 0.35, color)
        for y in ys: sh.tick(xo, self.Y(y), color)
        for i, (a, b) in enumerate(zip(ys[:-1], ys[1:])):
            s = vals[i] if vals else mt(abs(b - a)); w = FONT_R.text_length(s, fontsize=size); L = abs(self.Y(b) - self.Y(a)); ym = (self.Y(a) + self.Y(b)) / 2
            if w + 3 <= L: sh.otext(xo + side * 2.2 + (size * 0.72 if side > 0 else 0), ym + w / 2, s, size=size, rot=90, color=color, mask=mask)
            elif tight and FONT_R.text_length(s, fontsize=5.8) + 1 <= L: sh.otext(xo + side * 2.2, ym + FONT_R.text_length(s, fontsize=5.8) / 2, s, size=5.8, rot=90, color=color)
            else: sh.otext(xo + side * 3.0 - (w if side < 0 else 0), ym + size * 0.36, s, size=min(size, 6.4), color=color, mask=True)


def level_mark(sh, x, y, s, size=7.0, color=BLACK, right=True, bold=True):
    """σύμβολο στάθμης (τρίγωνο) με την τιμή δίπλα· (x, y) = η μύτη πάνω στη στάθμη."""
    sh.shape.draw_polyline([pymupdf.Point(x, y), pymupdf.Point(x - 3.2, y - 5.0), pymupdf.Point(x + 3.2, y - 5.0)]); sh.shape.finish(width=0.4, color=color, fill=color, closePath=True)
    w = (FONT_B if bold else FONT_R).text_length(s, fontsize=size)
    if right: sh.oline(x, y - 5.0, x + w + 6, y - 5.0, 0.4, color); sh.otext(x + 5, y - 6.6, s, size=size, bold=bold, color=color)
    else: sh.oline(x - w - 6, y - 5.0, x, y - 5.0, 0.4, color); sh.otext(x - 5 - w, y - 6.6, s, size=size, bold=bold, color=color)


def hatch_rect(v, x0, y0, x1, y1, step=0.07, w=0.2, color=(0.35, 0.35, 0.35)):
    c = x0 - (y1 - y0)
    while c < x1:
        ax, ay = c, y1; bx, by = c + (y1 - y0), y0
        if ax < x0: ay = y1 - (x0 - ax); ax = x0
        if bx > x1: by = y0 + (bx - x1); bx = x1
        if ay > by: v.line((ax, ay), (bx, by), w, color)
        c += step


def draw_plan(sh, big=False):
    """big = μόνη της σε Α3: χωρίς επικεφαλίδα / σημειώσεις, πιο σφιχτές σειρές διαστάσεων."""
    v = View(sh, 30.0, 33.0, 9.25, 4.72, 20); yb = 4.85 if big else 4.72
    if not big: sh.otext(14 * MM, 17 * MM, "ΚΑΤΟΨΗ ΣΚΑΛΑΣ", size=12, bold=True); sh.otext(14 * MM + 104, 17 * MM, "κλίμακα 1:20 · διαστάσεις σε m, από παρειές μπετού", size=7.5, color=GRAY)
    # δάπεδα χωλ: δάπεδο πόρτας / ασανσέρ (−3,00), σκαλί, ΥΠΕΡΥΨΩΜΕΝΟ ΠΛΑΤΥΣΚΑΛΟ
    v.rect(WALL_X, K3_Y, XL, LOBBY[1], 0, (1, 1, 1), (0.955, 0.955, 0.93)); v.rect(9.70, yb, 11.05, YN, 0, (1, 1, 1), (0.955, 0.955, 0.93)); v.rect(9.70, YN, XL, K3_Y, 0, (1, 1, 1), (0.955, 0.955, 0.93))
    v.rect(WALL_X, LOBBY[1], XL, LOBBY[2], 0, (1, 1, 1), STEPC); v.rect(WALL_X, LOBBY[2], XS, YS, 0, (1, 1, 1), PLATC)
    # τοιχεία / υποστυλώματα
    v.rect(9.40, yb, 9.70, 5.15, 1.3, BLACK, CONC); v.rect(11.05, 4.85, 13.35, YN, 1.3, BLACK, CONC)
    if not big: v.rect(11.05, 4.72, 11.30, 4.85, 1.3, BLACK, CONC); v.rect(13.10, 4.72, 13.35, 4.85, 1.3, BLACK, CONC)
    v.rect(XE, YN, 13.35, 7.10, 0.9, BLACK, WALLC); hatch_rect(v, XE, 6.40, 13.35, 7.10)
    v.rect(XE, 7.10, 13.35, 7.85, 1.3, BLACK, CONC)
    # δοκοί (η Δ9.1 από πάνω: η ανατολική παρειά της διακεκομμένη μέσα στο χωλ)
    v.line((9.40, K3_Y), (9.40, 8.02), 0.8); v.line((9.70, K3_Y), (9.70, YS), 0.3, GRAY, "[3 2] 0"); v.line((9.70, YS), (9.70, 8.02), 0.8)
    v.line((WALL_X, YS), (9.70, YS), 0.8)
    for y in (YS, 7.85): v.line((9.70, y), (XE, y), 0.8)
    v.line((9.40, 8.02), (9.70, 8.02), 0.3, GRAY, "[2 2] 0")
    # τοίχος γυψοσανίδας + ΝΕΑ πόρτα parking (ανοίγει μέσα, μεντεσές νότια)
    for y0_, y1_ in ((K3_Y, DOOR_Y[0]), (DOOR_Y[1], 8.02)): v.rect(WALL_X - 0.10, y0_, WALL_X, y1_, 0.5, BLACK, (0.80, 0.86, 0.93))
    v.line((WALL_X - 0.10, DOOR_Y[0]), (WALL_X - 0.10, DOOR_Y[1]), 0.3, GRAY, "[2 2] 0"); v.line((WALL_X, DOOR_Y[0]), (WALL_X, DOOR_Y[1]), 0.3, GRAY, "[2 2] 0")
    dw = DOOR_Y[1] - DOOR_Y[0]
    v.line((WALL_X, DOOR_Y[1]), (WALL_X + dw, DOOR_Y[1]), 1.1, DOORC)
    sh.shape.draw_polyline([pymupdf.Point(v.X(WALL_X + dw * math.sin(math.radians(a_))), v.Y(DOOR_Y[1] - dw * math.cos(math.radians(a_)))) for a_ in range(0, 91, 3)]); sh.shape.finish(width=0.35, color=DOORC, dashes="[2 2] 0", closePath=False)
    sh.otext(v.X(WALL_X - 0.05) + 2.3, v.Y((DOOR_Y[0] + DOOR_Y[1]) / 2) + 20, "ΠΟΡΤΑ 0,90", size=6.4, bold=True, rot=90, color=DOORC)
    # ρίχτια: σκαλί του χωλ (1, 2) και σκάλα του μελετητή (3 … 18)
    for y in LOBBY.values(): v.line((WALL_X, y), (XL, y), 0.85)
    for k, (a, b) in RISERS.items(): v.line(a, b, 0.85 if k in (NL + 1, N) else 0.55)
    # φανάρι
    v.rect(XL, W0, WX, W1, 0.85, BLACK, (1, 1, 1))
    # γραμμή ανάβασης
    sh.shape.draw_polyline([pymupdf.Point(v.X(x), v.Y(y)) for x, y in WALK.coords]); sh.shape.finish(width=0.45, color=BLUE, dashes="[6 2 1 2] 0", closePath=False)
    lob = [(XW, 5.86), (XW, W1 + RW - 0.30)] + [(XW + 0.30 - 0.30 * math.cos(math.radians(a_)), W1 + RW - 0.30 + 0.30 * math.sin(math.radians(a_))) for a_ in range(6, 91, 6)] + [(XS, W1 + RW)]
    sh.shape.draw_polyline([pymupdf.Point(v.X(x), v.Y(y)) for x, y in lob]); sh.shape.finish(width=0.45, color=BLUE, dashes="[6 2 1 2] 0", closePath=False)
    ax, ay = v.X(XL - 0.20), v.Y(W0 - RW); v.line((XL, W0 - RW), (XL - 0.18, W0 - RW), 0.45, BLUE)
    sh.shape.draw_polyline([pymupdf.Point(ax, ay), pymupdf.Point(ax + 7, ay - 2.6), pymupdf.Point(ax + 7, ay + 2.6)]); sh.shape.finish(width=0.3, color=BLUE, fill=BLUE, closePath=True)
    sh.flush()
    # αρίθμηση πατημάτων + στάθμη μπετού
    def num(cx, cy, lab): sh.ocircle(v.X(cx), v.Y(cy), 5.6, 0.5, BLACK, (1, 1, 1)); sh.otext(v.X(cx), v.Y(cy) + 2.7, str(lab), size=7.6, bold=True, align="center")
    num(XW, 5.86, 1); num(XW, (LOBBY[1] + LOBBY[2]) / 2, 2); num(XL - 0.24, W1 + RW, 3)
    for k in range(NL + 1, N):
        s = SPOS[k] + GOING[k] / 2
        p = WALK.interpolate(s); q = WALK.interpolate(min(WALK.length, s + 0.02)); q0 = WALK.interpolate(max(0, s - 0.02))
        tx, ty = q.x - q0.x, q.y - q0.y; L = math.hypot(tx, ty) or 1; nx, ny = ty / L, -tx / L            # κάθετη προς τα έξω (μακριά από το φανάρι)
        if (p.x + nx - WX) ** 2 + (p.y + ny - YC) ** 2 < (p.x - nx - WX) ** 2 + (p.y - ny - YC) ** 2: nx, ny = -nx, -ny
        num(p.x + nx * 0.02, p.y + ny * 0.02, k + 1)
        pts_ = []                                                                        # στάθμη: στη μέση ανάμεσα στα δύο ρίχτια του πατήματος, 0,34 έξω από τη γραμμή ανάβασης
        for kk in (k, k + 1):
            w_ = WALK.interpolate(SPOS[kk]); o_ = RISERS[kk][1]; L_ = math.hypot(o_[0] - w_.x, o_[1] - w_.y) or 1; d_ = min(0.34, 0.8 * L_)
            pts_.append((w_.x + (o_[0] - w_.x) / L_ * d_, w_.y + (o_[1] - w_.y) / L_ * d_))
        lx, ly = (pts_[0][0] + pts_[1][0]) / 2, (pts_[0][1] + pts_[1][1]) / 2
        sh.otext(v.X(lx), v.Y(ly) + 2.2, lv(SSL[k]), size=6.2, bold=True, color=RED, align="center", mask=True)
    # ετικέτες
    v.text(10.42, 5.19, "ΔΑΠΕΔΟ ΥΠΟΓΕΙΟΥ (πόρτα · ασανσέρ)", size=5.8, align="center", color=GRAY)
    level_mark(sh, v.X(10.05), v.Y(5.345), lv(SSL0) + " μπετό", 7.0, RED); v.text(10.53, 5.345, "(τελικό %s)" % lv(FFL0), size=6.2, dy=-6.6, color=FIN)
    v.text(10.62, (LOBBY[1] + LOBBY[2]) / 2, "ΣΚΑΛΙ  " + lv(SSL[1]), size=6.6, bold=True, dy=2.3, align="center", color=RED)
    v.text(9.93, (LOBBY[1] + LOBBY[2]) / 2, "(τελ. %s)" % lv(FFL[1]), size=5.6, dy=2.0, align="center", color=FIN)
    v.text(10.20, 7.17, "ΥΠΕΡΥΨΩΜΕΝΟ ΠΛΑΤΥΣΚΑΛΟ", size=7.4, bold=True, align="center"); v.text(10.20, 7.17, "%s × %s" % (mt(XS - WALL_X), mt(YS - LOBBY[2])), size=6.6, dy=8.0, align="center")
    level_mark(sh, v.X(9.80), v.Y(7.44), lv(SSL[2]) + " μπετό", 7.2, RED); v.text(10.30, 7.44, "(τελικό %s)" % lv(FFL[2]), size=6.2, dy=-6.6, color=FIN)
    v.text(10.20, 7.54, "+%s cm από το μπετό υπογείου %s" % (cm(SSL[2] - SSL0, 0), lv(SSL0)), size=5.6, align="center", color=GRAY)
    v.text(12.90, 7.49, "Π9  h=15", size=8.5, bold=True, align="center", mask=True)
    v.text(10.375, 4.94, "από πάνω: πλατύσκαλο ισογείου Π6 h=15", size=5.8, align="center", color=GRAY); v.text(10.375, 4.94, "μπετό %s · τελικό %s (μελέτη %s)" % (lv(SSL1), lv(FFL1), lv(FFL_STUDY)), size=5.8, dy=7.0, align="center", color=GRAY)
    # ΠΛΑΤΟΣ ΣΚΑΛΙΩΝ ΣΤΟ ΦΑΝΑΡΙ (cm): η ακμή του φαναριού είναι η γραμμή διάστασης, οι τιμές γράφονται μέσα στο κενό
    for k in range(NL + 1, N):
        a, b = RISERS[k][0], RISERS[k + 1][0]; t_ = cm(INNER[k])
        if abs(a[1] - W1) < 1e-9 and abs(b[1] - W1) < 1e-9: sh.otext(v.X((a[0] + b[0]) / 2), v.Y(W1) - 1.4, t_, size=6.4, bold=True, align="center")
        elif abs(a[1] - W0) < 1e-9 and abs(b[1] - W0) < 1e-9: sh.otext(v.X((a[0] + b[0]) / 2), v.Y(W0) + 6.0, t_, size=6.4, bold=True, align="center")
        else:                                                                             # γύρω από τη γωνία του φαναριού: στη μέση της σφήνας, 9 cm ανατολικά
            xq = WX + 0.09; ya, yb_ = [r_[0][1] + (r_[1][1] - r_[0][1]) * (xq - r_[0][0]) / (r_[1][0] - r_[0][0]) for r_ in (RISERS[k], RISERS[k + 1])]
            sh.otext(v.X(xq), v.Y((ya + yb_) / 2) + 2.2, t_, size=6.0, bold=True, align="center")
    v.text(9.55, 5.02, "Κ3", size=8.5, bold=True, align="center", dy=0); v.text(12.20, 4.975, "Κ6  230/25", size=8.5, bold=True, align="center", dy=3)
    sh.otext(v.X(13.225) + 3, v.Y(7.475) + 22, "Κ27 25/75", size=7.4, bold=True, rot=90)
    sh.otext(v.X(13.225) + 2.6, v.Y(6.35) + 40, "τοιχείο υπογείου 25", size=6.2, rot=90, mask=True)
    sh.otext(v.X(9.60) + 2.6, v.Y(7.82) + 26, "Δ9.1  30/50", size=6.6, bold=True, rot=90)
    v.text(11.75, 7.725, "Δ12.1  25/50", size=7.6, bold=True, align="center", dy=2.6)
    v.text(XL - 0.05, W0 - RW - 0.21, "ΑΦΙΞΗ στο Π6 ισογείου", size=5.8, color=BLUE, align="right"); v.text(XL - 0.05, W0 - RW - 0.21, "%s (από πάνω)" % lv(SSL1), size=5.8, dy=7.0, color=BLUE, align="right")
    # διαστάσεις: πάνω (ευθύγραμμα + σημεία στο τοιχείο Κ6), κάτω (σημεία στη δοκό Δ12.1), αριστερά, δεξιά (σημεία στο ανατολικό τοιχείο)
    sx = sorted(b[0] for a, b in RISERS.values() if abs(b[1] - YS) < 1e-9)              # σημεία ριχτιών στη δοκό Δ12.1
    nx_ = sorted(b[0] for a, b in RISERS.values() if abs(b[1] - YN) < 1e-9)             # … στο τοιχείο Κ6
    ey = sorted(b[1] for a, b in RISERS.values() if abs(b[0] - XE) < 1e-9)              # … στο ανατολικό τοιχείο
    top = [9.40, 9.70] + nx_ + [XE, 13.35]
    o1, o2 = (13, 27) if big else (14, 34); b1 = 15 if big else 22; l1, l2 = (13, 36) if big else (16, 38)
    v.hdim(top, yb, off=-o1)
    if big: v.hdim([9.70, XL, WX, XE], yb, off=-o2, vals=[mt(XL - 9.70), mt(WX - XL) + " φανάρι", mt(XE - WX)])
    else: v.hdim([9.70, XL, XE], yb, off=-o2); v.hdim([XL, WX, XE], 7.85, off=44, side=1, vals=["1,00 φανάρι", "1,20"])
    v.hdim([WALL_X] + sx + [XE], 7.85, off=b1, side=1)
    sh.oline(v.X(WALL_X), v.Y(8.02) + 1, v.X(WALL_X), v.Y(7.85) + b1 + 2, 0.2, GRAY)
    v.vdim([K3_Y, DOOR_Y[0], DOOR_Y[1], LOBBY[1], LOBBY[2], YS], 9.40, off=-l1); v.vdim([4.85, YN, W0, W1, YS, 7.85], 9.40, off=-l2, tight=True)
    for y in (DOOR_Y[0], DOOR_Y[1], LOBBY[1], LOBBY[2]): sh.oline(v.X(9.40) - l1 - 2, v.Y(y), v.X(9.40) - 1, v.Y(y), 0.2, GRAY)
    v.vdim([YN] + ey + [YS], 13.35, off=17, side=1)
    # βοηθητικές γραμμές προέκτασης
    for x in sx:
        sh.oline(v.X(x), v.Y(7.85) + 2, v.X(x), v.Y(7.85) + b1 + 2, 0.2, GRAY)
        if not big and x in nx_: sh.oline(v.X(x), v.Y(yb) - o1 - 2, v.X(x), v.Y(4.85) - 2, 0.2, GRAY, "[1 1.5] 0")
    for y in ey: sh.oline(v.X(13.35) + 2, v.Y(y), v.X(13.35) + 19, v.Y(y), 0.2, GRAY)
    if not big:
        yn = v.Y(7.85) + 64
        for i, ln in enumerate(("Μέσα στο φανάρι: πλάτος κάθε σκαλιού στο φανάρι (cm).",
                                "Κόκκινο = στάθμη ΜΠΕΤΟΥ πατήματος.   Μπλε = γραμμή ανάβασης, 60 cm από το φανάρι (πάτημα 26,5 cm σε όλα τα σκαλοπάτια).",
                                "Ανατολικό τοιχείο, διαγραμμισμένο τμήμα 6,40–7,10: έως το ύψος της σκάλας (μελετητής).")):
            sh.otext(14 * MM, yn + i * 9.2, ln, size=6.6)
    sh.flush()


def draw_dev(sh):
    """ανάπτυγμα στη γραμμή ανάβασης 1:20"""
    s0 = -0.62; z0 = -3.36
    v = View(sh, 274.0, 236.0, s0, z0, 20, flip=True)
    sh.otext(262 * MM, 17 * MM, "ΑΝΑΠΤΥΓΜΑ ΣΤΗ ΓΡΑΜΜΗ ΑΝΑΒΑΣΗΣ", size=12, bold=True); sh.otext(262 * MM + 228, 17 * MM, "κλίμακα 1:20 · στάθμες ΜΠΕΤΟΥ (κόκκινο) και τελικές (καφέ)", size=7.5, color=GRAY)
    sN = SPOS[N]; send = sN + 0.95
    # προφίλ μπετού (πάνω)
    top = [(s0, SSL0), (SPOS[1], SSL0)]
    for k in range(1, N + 1): top += [(SPOS[k], SSL[k])] + ([(SPOS[k + 1], SSL[k])] if k < N else [(send, SSL1)])
    # κάτω παρειά πλάκας σκάλας: παράλληλη στη γραμμή των εσωτερικών γωνιών, h = 15 κάθετα
    base = [(SPOS[k], SSL0 if k == 1 else SSL[k - 1]) for k in range(1, N + 1)]
    soff = []
    for i, (s, z) in enumerate(base):
        a = base[max(0, i - 1)]; b = base[min(len(base) - 1, i + 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); soff.append((s + H_SLAB * math.sin(ang), z - H_SLAB * math.cos(ang)))
    soff = [p for p in soff if p[1] > SSL0 + 0.001]
    # σημείο όπου η κάτω παρειά συναντά την κοιτόστρωση
    p0, p1 = soff[0], soff[1]; tx = p0[0] - (p0[1] - SSL0) * (p1[0] - p0[0]) / (p1[1] - p0[1])
    bot_land = SSL1 - H_SLAB
    last = soff[-1]; soff_top = [q for q in soff if q[1] < bot_land - 0.001]
    pa, pb = soff_top[-1], soff[len(soff_top)] if len(soff_top) < len(soff) else (sN + 0.2, bot_land)
    jx = pa[0] + (bot_land - pa[1]) * (pb[0] - pa[0]) / (pb[1] - pa[1]) if pb[1] != pa[1] else pa[0]
    under = [(tx, SSL0)] + soff_top + [(jx, bot_land), (send, bot_land)]
    # κοιτόστρωση
    v.poly([(s0, SSL0), (send, SSL0), (send, z0), (s0, z0)], 0, (1, 1, 1), (0.86, 0.86, 0.86)); v.line((s0, SSL0), (send, SSL0), 1.0)
    hatch = [(x / 10.0) for x in range(int(s0 * 10), 44, 3)]
    # σκάλα + πλατύσκαλο
    v.poly(top[1:] + under[::-1], 1.1, BLACK, CONC)
    # τελικές επιφάνειες
    fin = [(s0, FFL0), (SPOS[1], FFL0)]
    for k in range(1, N + 1): fin += [(SPOS[k], FFL[k])] + ([(SPOS[k + 1], FFL[k])] if k < N else [(send, FFL1)])
    sh.shape.draw_polyline([pymupdf.Point(v.X(x), v.Y(y)) for x, y in fin]); sh.shape.finish(width=0.45, color=FIN, dashes="[3 1.6] 0", closePath=False)
    sh.flush()
    # στάθμες ανά πάτημα
    for k in range(1, N):
        xm = (v.X(SPOS[k]) + v.X(SPOS[k + 1])) / 2
        sh.otext(xm + 2.3, v.Y(FFL[k]) - 4, lv3(SSL[k]), size=6.4, bold=True, color=RED, rot=90)
        sh.ocircle(xm, v.Y(SSL[k]) + 7.2, 4.6, 0.4, BLACK, (1, 1, 1)); sh.otext(xm, v.Y(SSL[k]) + 9.6, str(k), size=6.4, bold=True, align="center")
    xm = v.X(sN) + 44; sh.ocircle(xm, v.Y(SSL1) + 7.2, 4.6, 0.4, BLACK, (1, 1, 1)); sh.otext(xm, v.Y(SSL1) + 9.6, str(N), size=6.4, bold=True, align="center")
    level_mark(sh, v.X(s0 + 0.10), v.Y(SSL0), lv(SSL0) + " μπετό", 7.0, RED); level_mark(sh, v.X(s0 + 0.10), v.Y(FFL0), lv(FFL0) + " τελικό", 6.6, FIN)
    level_mark(sh, v.X(sN + 0.38), v.Y(SSL1), lv(SSL1) + " μπετό", 7.0, RED); level_mark(sh, v.X(sN + 0.38), v.Y(FFL1), lv(FFL1) + " τελικό", 6.6, FIN)
    v.text(sN + 0.50, (SSL1 + bot_land) / 2, "Π6  h=15", size=7.0, bold=True, dy=2.4)
    # ρίχτια μπετού: πρώτο / ενδιάμεσα / τελευταίο
    r1 = SSL[1] - SSL0; rN = SSL1 - SSL[N - 1]
    for (za, zb, sx, txt) in ((SSL0, SSL[1], SPOS[1], cm(r1)), (SSL[N - 1], SSL1, SPOS[N], cm(rN))):      # 1ο και τελευταίο ρίχτι μπετού: η τιμή μέσα στη βαθμίδα
        xo = v.X(sx) + 5.5; sh.oline(xo, v.Y(za), xo, v.Y(zb), 0.4, RED); sh.tick(xo, v.Y(za), RED); sh.tick(xo, v.Y(zb), RED)
        sh.otext(xo + 3.5, (v.Y(za) + v.Y(zb)) / 2 + 2.4, txt, size=6.6, bold=True, color=RED)
    # αλυσίδα πατημάτων στη γραμμή ανάβασης
    xs = [SPOS[k] for k in range(1, N + 1)]
    v.hdim(xs, z0, off=6, vals=[cm(GOING[k]) for k in range(1, N)], size=6.6, side=1); v.hdim([xs[0], xs[-1]], z0, off=25, vals=[mt(xs[-1] - xs[0]) + " m στη γραμμή ανάβασης"], side=1)
    for x in xs: sh.oline(v.X(x), v.Y(z0) + 8, v.X(x), v.Y(SSL0) + 3, 0.18, GRAY, "[1 2] 0")
    # ύψος ορόφου
    v.vdim([FFL0, FFL1], send, off=20, vals=["%d × %s = %s m (τελικό)" % (N, cm(RISE, 2), mt(FFL1 - FFL0))], side=1, color=FIN)
    v.vdim([SSL0, SSL1], send, off=42, vals=[mt(SSL1 - SSL0) + " m μπετό με μπετό"], side=1, color=RED)
    # πάχος πλάκας σκάλας
    k = 11; a = (SPOS[k], SSL[k - 1]); ang = math.atan2(SSL[k] - SSL[k - 2], SPOS[k + 1] - SPOS[k - 1]); b = (a[0] + H_SLAB * math.sin(ang), a[1] - H_SLAB * math.cos(ang))
    v.line(a, b, 0.5, BLACK); sh.tick(v.X(a[0]), v.Y(a[1])); sh.tick(v.X(b[0]), v.Y(b[1]))
    v.text(b[0], b[1], "Π9  h=15 (κάθετα)", size=6.8, bold=True, dx=6, dy=9)
    v.text(2.6, SSL0 - 0.15, "ΚΟΙΤΟΣΤΡΩΣΗ ΥΠΟΓΕΙΟΥ", size=6.6, color=GRAY, align="center")
    sh.flush()


def draw_step(sh):
    """τυπική ευθύγραμμη βαθμίδα 1:10"""
    g = 0.265; n = 3
    v = View(sh, 46.0, 334.0, 0.0, 0.0, 10, flip=True)
    sh.otext(14 * MM, 243 * MM, "ΤΥΠΙΚΗ ΒΑΘΜΙΔΑ (ευθύγραμμη)", size=12, bold=True); sh.otext(14 * MM + 190, 243 * MM, "κλίμακα 1:10 · cm", size=7.5, color=GRAY)
    ang = math.atan2(RISE, g); hv = H_SLAB / math.cos(ang); xl = -0.10
    top = [(xl, 0), (0, 0)] + [p for i in range(n) for p in ((i * g, (i + 1) * RISE), ((i + 1) * g, (i + 1) * RISE))]
    v.poly(top + [(n * g, n * RISE - hv), (xl, xl * math.tan(ang) - hv)], 1.1, BLACK, CONC)
    fin = [(xl, T_STEP), (0, T_STEP)] + [p for i in range(n) for p in ((i * g, T_STEP + (i + 1) * RISE), ((i + 1) * g, T_STEP + (i + 1) * RISE))]
    sh.shape.draw_polyline([pymupdf.Point(v.X(x), v.Y(y)) for x, y in fin]); sh.shape.finish(width=0.5, color=FIN, dashes="[3 1.6] 0", closePath=False)
    sh.flush()
    v.hdim([g, 2 * g], 2 * RISE + T_STEP, off=-13, vals=["πάτημα " + cm(g)], size=7.2)
    v.vdim([RISE, 2 * RISE], g, off=-24, vals=["ρίχτι " + cm(RISE, 2)], size=7.2, mask=True)
    for z in (RISE, 2 * RISE): sh.oline(v.X(g) - 27, v.Y(z), v.X(g) - 2, v.Y(z), 0.2, GRAY)
    xo = v.X(n * g) + 12; sh.oline(xo, v.Y(n * RISE), xo, v.Y(n * RISE + T_STEP), 0.4, FIN); sh.tick(xo, v.Y(n * RISE), FIN); sh.tick(xo, v.Y(n * RISE + T_STEP), FIN)
    sh.otext(xo + 5, v.Y(n * RISE + T_STEP / 2) + 2.4, "επένδυση " + cm(T_STEP) + " *", size=6.8, color=FIN)
    a0 = (2 * g, 2 * RISE); a1 = (a0[0] + H_SLAB * math.sin(ang), a0[1] - H_SLAB * math.cos(ang))
    v.line(a0, a1, 0.5); sh.tick(v.X(a0[0]), v.Y(a0[1])); sh.tick(v.X(a1[0]), v.Y(a1[1]))
    v.text(a1[0], a1[1], "πλάκα h = 15", size=7.4, bold=True, dx=6, dy=9)
    v.text(xl, 0.0, "μπετό", size=6.2, color=RED, dx=0, dy=-2.5); v.text(xl, T_STEP, "τελικό", size=6.2, color=FIN, dx=0, dy=-2.5)
    x = 152 * MM; y = 282 * MM
    for i, ln in enumerate(("* ΠΑΡΑΔΟΧΗ: επένδυση βαθμίδας 5 cm", "  (μάρμαρο 3 + κονίαμα 2).", "  Αν αλλάξει, οι στάθμες μπετού των", "  πατημάτων 1–15 μετακινούνται ισόποσα·",
                            "  οι στάθμες −3,10 και +0,30 δεν αλλάζουν.", "", "Τελικό ρίχτι παντού %s cm." % cm(RISE, 2), "Ρίχτια ΜΠΕΤΟΥ: 1ο %s · 2ο–15ο %s ·" % (cm(SSL[1] - SSL0), cm(RISE, 2)), "16ο (στο πλατύσκαλο) %s cm." % cm(SSL1 - SSL[N - 1]))):
        sh.otext(x, y + i * 9.4, ln, size=6.9, bold=(i in (0, 7, 8)))


def draw_table(sh):
    x0, y0 = 300 * MM, 266 * MM
    sh.otext(x0, y0 - 9, "ΣΤΑΘΜΕΣ ΠΑΤΗΜΑΤΩΝ", size=12, bold=True)
    cols = [0, 62, 150, 226, 302]; heads = [["πάτημα"], ["πάτημα στη γραμμή", "ανάβασης (cm)"], ["στάθμη ΜΠΕΤΟΥ", "(m)"], ["τελική στάθμη", "(m)"]]
    rh = 12.6; W = cols[-1]
    sh.orect(x0, y0, x0 + W, y0 + 22, 0.6, BLACK, (0.92, 0.92, 0.92))
    for i, h in enumerate(heads):
        for j, ln in enumerate(h): sh.otext(x0 + (cols[i] + cols[i + 1]) / 2, y0 + (9 if len(h) == 2 else 14) + j * 8.6, ln, size=6.6, bold=True, align="center", color=RED if i == 2 else FIN if i == 3 else BLACK)
    y = y0 + 22
    rows = [("0", "δάπεδο υπογείου", lv(SSL0), lv(FFL0))] + [(str(k), cm(GOING[k]) if k < N else "πλατύσκαλο Π6", lv3(SSL[k]) if k < N else lv(SSL1), lv3(FFL[k]) if k < N else lv(FFL1)) for k in range(1, N + 1)]
    for r, row in enumerate(rows):
        if r % 2 == 1: sh.orect(x0, y, x0 + W, y + rh, 0, (1, 1, 1), (0.965, 0.965, 0.965))
        for i, s in enumerate(row):
            sh.otext(x0 + (cols[i] + cols[i + 1]) / 2, y + rh - 3.6, s, size=7.4 if i != 1 else 6.8, bold=(i in (0, 2)), align="center", color=RED if i == 2 else FIN if i == 3 else BLACK)
        y += rh
    sh.orect(x0, y0, x0 + W, y, 0.6, BLACK)
    for c in cols[1:-1]: sh.oline(x0 + c, y0, x0 + c, y, 0.3)
    sh.oline(x0, y0 + 22, x0 + W, y0 + 22, 0.6)
    xr = x0 + W + 9 * MM; y = y0 + 8
    sh.otext(xr, y, "ΣΤΟΙΧΕΙΑ ΣΚΑΛΑΣ", size=9, bold=True); y += 13
    for ln, b in (("%d ρίχτια · τελικό ρίχτι %s cm" % (N, cm(RISE, 2)), True),
                  ("τελικά δάπεδα %s (υπόγειο) → %s (ισόγειο) = %s m" % (lv(FFL0), lv(FFL1), mt(FFL1 - FFL0)), False),
                  ("μπετό %s (κοιτόστρωση) → %s (Π6) = %s m" % (lv(SSL0), lv(SSL1), mt(SSL1 - SSL0)), False),
                  ("πάτημα στη γραμμή ανάβασης 26,5 cm", False),
                  ("πλάτος κλάδου 1,20 m · φανάρι 1,00 × 0,10 m", False),
                  ("πλάκα σκάλας Π9 h=15 · πλατύσκαλο Π6 h=15", False),
                  ("", False),
                  ("Γεωμετρία / πάχη: Σ2_ΕΦ (μελετητής).", False),
                  ("Ρίχτια / στάθμες: A-10-B, Α-30-ΑΑ R01 (αρχιτέκτονας).", False),
                  ("Οπλισμοί ΜΟΝΟ από το σχέδιο του μελετητή.", True)):
        sh.otext(xr, y, ln, size=7.0, bold=b); y += 9.8


def title(sh):
    PW, PH = 594 * MM, 420 * MM; m = 10 * MM; fr = 8 * MM
    sh.orect(fr, fr, PW - fr, PH - fr, 0.6)
    TH = 11 * MM; x0, x1, y1 = m, PW - m, PH - m; y0 = y1 - TH; yc = (y0 + y1) / 2
    sh.orect(x0, y0, x1, y1, 0.9)
    def cap(x, s_): sh.otext(x, y0 + 8.2, s_, size=5.6, color=GRAY)
    def big(x, s_, size): sh.otext(x, y1 - 6.4, s_, size=size, bold=True); return x + FONT_B.text_length(s_, fontsize=size)
    def sep(x): sh.oline(x, y0, x, y1, 0.4); return x + 3.2 * MM
    x = x0 + 3.0 * MM
    sh.otext(x, yc + 20 * 0.36, "Σ2α", size=20, bold=True); x = sep(x + FONT_B.text_length("Σ2α", fontsize=20) + 3.2 * MM)
    cap(x, "ΞΥΛΟΤΥΠΟΣ ΕΡΓΟΤΑΞΙΟΥ – ΛΕΠΤΟΜΕΡΕΙΑ"); x = sep(big(x, "ΣΚΑΛΑ ΥΠΟΓΕΙΟΥ → ΙΣΟΓΕΙΟΥ", 12.5) + 3.2 * MM)
    cap(x, "ΣΤΑΘΜΕΣ ΜΠΕΤΟΥ"); x = sep(big(x, "%s → %s" % (lv(SSL0), lv(SSL1)), 12.5) + 3.2 * MM)
    cap(x, "ΚΛΙΜΑΚΑ"); x = sep(big(x, "1:20 · 1:10", 12.5) + 3.2 * MM)
    cap(x, "ΕΡΓΟ"); big(x, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓ. ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ", 10.5)
    sh.otext(x1 - 2.6 * MM, y1 - 6.4, "%s · %s" % (REV, DATE), size=6.4, align="right", color=GRAY)
    sh.otext(x1 - 2.6 * MM, y0 + 8.2, "Α2 – εκτύπωση 100 %", size=5.6, align="right", color=GRAY)


def info_a3(sh, x, y0, y1, scale_txt):
    """στενή στήλη στοιχείων δεξιά (Α3): τίτλος, κλίμακα, υπόμνημα χρωμάτων, στάθμες, έργο."""
    sh.orect(x, y0, x + 40 * MM, y1, 0.9); xx = x + 2.4 * MM; y = y0 + 11 * MM
    sh.otext(xx, y, "Σ2α", size=26, bold=True); y += 8 * MM
    for ln in ("ΣΚΑΛΑ ΥΠΟΓΕΙΟΥ", "→ ΙΣΟΓΕΙΟΥ"): sh.otext(xx, y, ln, size=9.6, bold=True); y += 4.4 * MM
    sh.otext(xx, y + 1, "ΚΑΤΟΨΗ ΞΥΛΟΤΥΠΟΥ", size=7.4); y += 8 * MM
    sh.otext(xx, y, "ΚΛΙΜΑΚΑ", size=5.8, color=GRAY); y += 5.2 * MM; sh.otext(xx, y, scale_txt, size=13, bold=True); y += 3.6 * MM
    sh.otext(xx, y, "Α3 – εκτύπωση 100 %", size=5.8, color=GRAY); y += 3.2 * MM
    k = 1000.0 / float(scale_txt.split(":")[1].replace(",", ".")) * MM * 0.4             # γραφική κλίμακα 0,40 m
    yb = y + 2.2 * MM; sh.oline(xx, yb, xx + k, yb, 0.8)
    for i in range(0, 5): sh.oline(xx + k * i / 4, yb, xx + k * i / 4, yb - (5 if i in (0, 4) else 2.8), 0.4)
    sh.otext(xx, yb + 7.2, "0", size=5.6); sh.otext(xx + k / 2, yb + 7.2, "20", size=5.6, align="center"); sh.otext(xx + k, yb + 7.2, "40 cm", size=5.6, align="right")
    y = yb + 9 * MM; sh.oline(x, y - 4 * MM, x + 40 * MM, y - 4 * MM, 0.4)
    def blk(head, lines, color=BLACK):
        nonlocal y
        sh.otext(xx, y, head, size=7.0, bold=True, color=color); y += 3.5 * MM
        for ln in lines: sh.otext(xx, y, ln, size=6.5); y += 3.2 * MM
        y += 2.0 * MM
    blk("ΑΛΛΑΓΗ: %d ΡΙΧΤΙΑ" % N, ("αντί %d της μελέτης (%s cm):" % (N_DESIGN, cm((FFL_STUDY - FFL0) / N_DESIGN, 1)), "πόρτα → ένα σκαλί (2 ρίχτια)", "→ υπερυψωμένο πλατύσκαλο", "→ σκάλα %d ριχτιών" % NS, "ρίχτι ≤ 19 · πάτημα 25 · 1,20", "ΜΕ ΕΓΚΡΙΣΗ ΜΕΛΕΤΗΤΩΝ"), RED)
    blk("ΧΩΛ ΙΣΟΓΕΙΟΥ %s" % lv(FFL1), ("(μελέτη %s): ένα σκαλί" % lv(FFL_STUDY), "ακόμη στην εξωτερική σκάλα", "εισόδου · γέμισμα χωλ %s cm" % cm(FFL1 - SSL1, 0)), RED)
    blk("ΥΠΕΡΥΨ. ΠΛΑΤΥΣΚΑΛΟ", ("%s × %s m" % (mt(XS - WALL_X), mt(YS - LOBBY[2])), "μπετό %s · τελικό %s" % (lv(SSL[2]), lv(FFL[2])), "%s cm πάνω από το μπετό" % cm(SSL[2] - SSL0, 0), "του υπογείου (%s)" % lv(SSL0)))
    blk("ΠΟΡΤΑ PARKING 0,90", ("5 cm από την Κ3 (νέα θέση)", "ανοίγει μέσα, μεντεσές νότια"))
    blk("ΦΑΝΑΡΙ %s × %s" % (mt(WX - XL), mt(W1 - W0)), ("όπως η μελέτη · κλάδοι 1,20", "στροφή %s · πέρασμα ισογ. 1,20" % mt(XE - WX)))
    blk("ΜΕΣΑ ΣΤΟ ΦΑΝΑΡΙ", ("πλάτος κάθε σκαλιού", "στο φανάρι, σε cm"))
    blk("ΚΟΚΚΙΝΟ", ("στάθμη ΜΠΕΤΟΥ", "(τελικό − επένδυση %s cm)" % cm(T_STEP)), RED)
    blk("ΜΠΛΕ", ("γραμμή ανάβασης · πάτημα", "σκάλας %s cm (60 cm από το" % cm(GOING[NL + 1], 0), "φανάρι) · σκαλί χωλ %s cm" % cm(STEP_GO, 0)), BLUE)
    blk("ΡΙΧΤΙΑ", ("%d × %s cm (τελικό)" % (N, cm(RISE, 2)), "μπετό: όλα %s · το τελευταίο" % cm(RISE, 2), "πάτημα στη στάθμη της πλάκας"))
    y = y1 - 18.5 * MM; sh.oline(x, y - 4.2 * MM, x + 40 * MM, y - 4.2 * MM, 0.4)
    for ln in ("ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12", "& ΑΓ. ΒΑΡΒΑΡΑΣ", "ΑΡΓΥΡΟΥΠΟΛΗ"): sh.otext(xx, y, ln, size=6.6, bold=True); y += 3.3 * MM
    sh.otext(xx, y + 1.2 * MM, "Βάση: Σ2_ΕΦ · A-10-B · Α-30-ΑΑ", size=5.4, color=GRAY); sh.otext(xx, y + 4.2 * MM, "%s · %s" % (REV, DATE), size=5.8, color=GRAY)


def main():
    """Α3: ΜΙΑ μεγάλη κάτοψη (η κάτοψη 1:20 μεγεθύνεται διανυσματικά ώστε να γεμίζει το φύλλο) + στενή στήλη στοιχείων."""
    tmp = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=20, page_w=594, page_h=420, sx0=0, sy0=0)
    draw_plan(tmp, big=True); tmp.flush()
    bb = pymupdf.Rect()
    for d in tmp.page.get_drawings(): bb |= d["rect"]
    for r, _ in tmp.texts_out: bb |= r
    bb = bb + (-2, -2, 2, 2)
    PW, PH = 420 * MM, 297 * MM; m = 8 * MM; col = 40 * MM; gap = 3 * MM
    aw, ah = PW - 2 * m - col - gap, PH - 2 * m
    f = min(aw / bb.width, ah / bb.height)
    for sc in (10, 12.5, 15, 20):                                                       # η μεγαλύτερη «στρογγυλή» κλίμακα που χωράει
        if 20.0 / sc <= f + 1e-6: f = 20.0 / sc; break
    scale_txt = "1:" + ("%g" % sc).replace(".", ",")
    sh = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=sc, page_w=420, page_h=297, sx0=0, sy0=0)
    w, h = bb.width * f, bb.height * f; x0 = m + (aw - w) / 2; y0 = m + (ah - h) / 2
    src = pymupdf.open("pdf", tmp.doc.tobytes())
    sh.page.show_pdf_page(pymupdf.Rect(x0, y0, x0 + w, y0 + h), src, 0, clip=bb)
    sh.shape = sh.page.new_shape()
    sh.orect(m - 2 * MM, m - 2 * MM, PW - m + 2 * MM, PH - m + 2 * MM, 0.6)
    info_a3(sh, PW - m - col, m, PH - m, scale_txt); sh.flush()
    os.makedirs(OUT, exist_ok=True)
    for d_ in (OUT, os.path.join(OUT, "ΕΡΓΟΤΑΞΙΟΥ_A2")):
        for fn in os.listdir(d_):
            if fn.startswith("Σ2α_") and fn != NAME and REV in fn: os.remove(os.path.join(d_, fn))
    path = os.path.join(OUT, NAME)
    sh.doc.set_metadata(dict(title="Σ2α – Σκάλα υπογείου → ισογείου, κάτοψη", author="ARKAD Ι.Κ.Ε."))
    sh.doc.save(path, garbage=4, deflate=True)
    print("->", NAME, "· κλίμακα", scale_txt, "· κάτοψη %.0f × %.0f mm σε %.0f × %.0f" % (w / MM, h / MM, aw / MM, ah / MM))
    print("πάτημα στη γραμμή ανάβασης (cm):", " ".join("%d:%.1f" % (k, GOING[k] * 100) for k in range(NL + 1, N)), "· σύνολο %.3f" % (SPOS[N] - SPOS[NL + 1]), "· σκαλί χωλ %.1f" % (STEP_GO * 100))
    print("στάθμες μπετού:", " ".join("%d:%+.3f" % (k, SSL[k]) for k in range(1, N + 1)), "· ρίχτι %.4f" % RISE)
    print("πλάτος στο φανάρι (cm):", " ".join("%d:%s" % (k, cm(INNER[k])) for k in range(NL + 1, N)), "· σύνολο %s" % cm(sum(INNER.values())))
    if len(sys.argv) > 1: pymupdf.open(path)[0].get_pixmap(dpi=int(sys.argv[2]) if len(sys.argv) > 2 else 110).save(sys.argv[1])


if __name__ == "__main__":
    main()
