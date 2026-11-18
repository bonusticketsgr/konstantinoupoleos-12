"""ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1 – κάτοψη διαδρομής + ΤΟΜΕΣ (τυπικός όροφος Α΄ · Β΄ · Γ΄ · Δ΄ και ισόγειο).

Ιδιοκτήτης 18/11/2026: «φτιάξε εσύ το μηχάνημα στο σαλόνι όπως καλύτερα πιστεύεις · μην θεωρήσεις ότι θα περάσεις κάτω από δοκάρια ·
κάνε μου τομές να καταλάβω διαδρομή».

Όλα διαβάζονται από τα μοντέλα των ανόψεων (b1_anopsi R21 · gf_anopsi R09) και των τοιχοποιιών – αν αλλάξει η όδευση εκεί, οι τομές ξαναβγαίνουν.
Φύλλα A3: ΚΜ-01 κάτοψη διαδρομής 1:40 · ΚΜ-02 τομή Α-Α κατά μήκος της διαδρομής 1:20 (+ το δάπεδο σε μεγέθυνση) · ΚΜ-03 τομή Β-Β μέσα από το
μηχάνημα 1:15 · ΚΜ-04 τομή Γ-Γ έξοδος στον ΒΑ εξώστη 1:15 · ΚΜ-05 λεπτομέρειες 1:5 (κανάλι γωνίας · σωλήνες στο γέμισμα) · ΚΜ-06 ισόγειο 1:40.

Χρήση: python3 tomes_km1.py [out.pdf]  →  ΑΝΟΨΕΙΣ/ΚΛΙΜΑΤΙΣΤΙΚΟ_ΣΑΛΟΝΙΟΥ_ΚΜ1_ΤΟΜΕΣ_<REV>.pdf
Συντεταγμένες: m του κοινού συστήματος (x ανατολή, y νότος) · στάθμες από το τελικό δάπεδο του ορόφου (γέμισμα 12 cm).
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import b1_anopsi as A
import gf_anopsi as G
import checks, sheets
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow, new_canvas
from reportlab.pdfbase import pdfmetrics

REV, DATE = "R00", "18/11/2026"
OUTDIR = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΑΝΟΨΕΙΣ")
BASE = "Ανόψεις Β1 %s · Δ΄ R10 · ισόγειο %s · τοιχοποιίες Β1 %s · γέμισμα δαπέδων 12 cm" % (A.REV, G.REV, A.W.REV)

MM = 72 / 25.4


def scale(n):
    return MM * 1000.0 / n


# ---------------------------------------------------------------- χρώματα
MAG = (0.80, 0.10, 0.50)
MAG_F = (0.97, 0.80, 0.90)
ORANGE = (0.86, 0.45, 0.04)
ORANGE_F = (0.99, 0.88, 0.70)
BLUE = (0.05, 0.36, 0.66)
BLUE2 = (0.25, 0.55, 0.75)
BLUE_F = (0.82, 0.90, 0.98)
RAIN = (0.15, 0.45, 0.80)
GREEN = (0.05, 0.52, 0.42)
CABLE = (0.10, 0.45, 0.30)
BEAMC = (0.62, 0.30, 0.16)
RED = (0.78, 0.10, 0.12)
CONC = (0.74, 0.74, 0.76)
CONC_H = (0.50, 0.50, 0.53)
CONC_L = (0.90, 0.90, 0.92)
BRICK = (0.86, 0.56, 0.42)
BRICK_H = (0.62, 0.32, 0.22)
GYP = (0.80, 0.87, 0.95)
GYP_S = (0.30, 0.42, 0.58)
FILLC = (0.94, 0.90, 0.80)
FILL_H = (0.70, 0.62, 0.45)
ETICS = (0.99, 0.94, 0.70)
ETICS_S = (0.72, 0.60, 0.20)
WOOD = (0.97, 0.94, 0.88)
WOOD_S = (0.62, 0.52, 0.38)
WALL_BG = (0.965, 0.962, 0.955)
WHITE = (1, 1, 1)

# ---------------------------------------------------------------- στοιχεία από τα μοντέλα (τυπικός όροφος)
W = A.W
FILL = A.COND_FILL["fill"]                      # γέμισμα δαπέδου 12 cm
TOP = A.TOP_SLAB                                # πάνω παρειά πλάκας οροφής +2,98
SOF8, SOF3, SOF6 = A.SLABS["Π8 h20"], A.SLABS["Π3 h18"], A.SLABS["Π6 h15"]
BEAM = {b[0]: b for b in A.BEAMS}
ZL = {z["id"]: z["level"] for z in A.ZONES}
LV_LIV, LV_STRIP, LV_BED, LV_B50, LV_STAIR, LV_PSB = ZL["Ζ1"], ZL["Ζ2"], ZL["Ζ10"], ZL["Ζ11"], ZL["Ζ12"], ZL["Ζ13"]
UNIT = A.UNITS[0]
UX0, UY0, UX1, UY1 = UNIT["rect"]
U_TOP = SOF8 - A.HANG
U_BOT = U_TOP - UNIT["hmax"]
PLEN = A.DUCTS[0][1]
SLOT = [d for d in A.DIFFUSERS if d["kind"] == "slot"]
RET = [d for d in A.DIFFUSERS if d["kind"] == "ret"][0]["rect"]
HATCH = A.HATCHES[0]["rect"]
BX0, BY0, BX1, BY1 = A.BOX["rect"]
KX, CX, BYC = A.KM1_X, A.COND_X, A.BOX_Y
STRIP_X = A.STRIP_X
WARD = [r for n, r in A.TALL if n == "ντουλάπα Υπν.2"][0]
KR2 = [c for c in A.CURTAINS if c["id"] == "ΚΡ2"][0]["rect"]
EM = A.OUTDOOR_T
GULLY = A.EXIT_GULLY
YD1 = (GULLY[-1][0], 0.57)                      # υδρορροή ΥΔ1 (τεύχος αποχετεύσεων)
EXIT_Y = A.KM1_FLOOR[1][1]                      # y εξόδου των ψυκτικών από τον πεσσό (1,20)
EXIT_Z = A.KM1_EXIT_Z
COND_TURN_Y = A.COND_FLOOR[1][1]                # y όπου τα συμπυκνώματα στρίβουν προς τον πεσσό (0,98)
R_GAS, R_LIQ, R_CON = A.REFR_PIPE["od"] / 2, A.REFR_PIPE["od_liq"] / 2, A.COND_FILL["od"] / 2
Z_REF = -FILL + R_GAS + 0.004                   # άξονας ψυκτικών μέσα στο γέμισμα (πάνω στην πλάκα, μέσα σε σπιράλ)
COVER, SLOPE = A.COND_FILL["cover"], A.COND_FILL["slope"]


def wall(i, model=None):
    w = [w_ for w_ in (model or W).WALLS if w_["id"] == i][0]
    xs = [p[0] for p in w["pts"]]; ys = [p[1] for p in w["pts"]]
    return round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)


T206, T6A3, T6A1, T105, T306, T104 = wall("T2-06"), wall("T6A-03"), wall("T6A-01"), wall("T1-05"), wall("T3-06"), wall("T1-04")
T106 = wall("T1-06")
K3 = (9.40, 3.00, 9.70, 5.15)
W206 = (9.45, 1.38, 9.70, 2.38)                 # μπαλκονόπορτα W2.06
DOOR = (5.30, 6.30)                             # πόρτα εισόδου (y)
BALC = (9.80, 0.65, 11.45, 2.70)                # δάπεδο ΒΑ εξώστη
PAR_E = (11.25, 0.85, 11.45, 2.65)              # ανατολικό στηθαίο (σκυρόδεμα)
PAR_N = (9.80, 0.65, 11.45, 0.85)               # βόρειο στηθαίο
BALC_Z = -0.02                                  # τελικό δάπεδο εξώστη ως προς το εσωτερικό (εξώστες 2 cm χαμηλότερα)


def cond_inv(d):
    """Ροή (κάτω παρειά) των συμπυκνωμάτων μέσα στο γέμισμα σε απόσταση d από το κανάλι, από το τελικό δάπεδο."""
    return -(COVER + 2 * R_CON + SLOPE * d)


D_TURN = BYC - COND_TURN_Y                      # μήκος στο δάπεδο ως τη στροφή προς τον πεσσό
Z_C_START = -COVER - 2 * R_CON                  # ροή στην αρχή (−0,062)
Z_C_TURN = cond_inv(D_TURN)
Z_C_END = A.COND_END
Z_C_VOID_END = LV_STRIP + 0.0125 + A.COND_PIPE["od"] / 2      # άξονας συμπυκνωμάτων στο κενό, στο κανάλι
Z_C_VOID_START = Z_C_VOID_END + 0.01 * (UY0 - BYC)            # στην έξοδο της μονάδας (κλίση 1 %)
Z_R_VOID = 2.63                                                # άξονας ψυκτικών στο κενό (δεμένα ψηλά, δίπλα στον τοίχο)


def cm(v):
    return ("%.1f" % (v * 100)).rstrip("0").rstrip(".").replace(".", ",")


def mm2(v):
    return ("%.2f" % (v + 1e-9)).replace(".", ",")


def lv(v, nd=2):
    s = ("%+." + str(nd) + "f") % v
    if abs(v) < 0.5 * 10 ** -nd:
        s = "±" + ("%." + str(nd) + "f") % 0
    return s.replace(".", ",")


# ================================================================ όψη τομής
class Sec:
    """Τομή: u οριζόντια θέση (m), z στάθμη από το τελικό δάπεδο (m, προς τα πάνω). sz = κατακόρυφη κλίμακα (αν διαφέρει)."""

    def __init__(self, c, ox, oy, s, u0=0.0, sz=None, brk=None):
        self.c, self.ox, self.oy, self.s, self.u0, self.sz = c, ox, oy, s, u0, sz or s
        self.brk = brk          # (zl, zh, gap): το ύψος zl…zh παραλείπεται (σπάσιμο τομής), gap σε pt

    def p(self, u, z):
        X = self.ox + (u - self.u0) * self.s
        if not self.brk:
            return X, self.oy + z * self.sz
        zl, zh, gap = self.brk
        if z <= zl:
            return X, self.oy + z * self.sz
        if z >= zh:
            return X, self.oy + zl * self.sz + gap + (z - zh) * self.sz
        return X, self.oy + zl * self.sz + gap * (z - zl) / (zh - zl)

    def break_band(self, u0, u1, ext=14):
        """Λευκή λωρίδα + δύο γραμμές σπασίματος εκεί που παραλείπεται το ύψος."""
        c = self.c
        zl, zh, gap = self.brk
        X0, Y0 = self.p(u0, zl); X1, Y1 = self.p(u1, zh)
        c.setFillColorRGB(1, 1, 1); c.rect(X0 - ext, Y0, X1 - X0 + 2 * ext, Y1 - Y0, stroke=0, fill=1)
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.6)
        for Y in (Y0, Y1):
            pth = c.beginPath(); x = X0 - ext; pth.moveTo(x, Y); k = 0
            while x < X1 + ext:
                x += 9; pth.lineTo(min(x, X1 + ext), Y + (2.2 if k % 2 == 0 else -2.2)); k += 1
            c.drawPath(pth, stroke=1, fill=0)
        c.setFont("Inter", 5.2); c.setFillColorRGB(*GREY)
        c.drawRightString(X1 - 6, (Y0 + Y1) / 2 - 1.8, "(το ενδιάμεσο ύψος του χώρου παραλείπεται)")

    def rect(self, u0, z0, u1, z1, fill=None, stroke=None, lw=0.5, dash=None):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0), stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def poly(self, pts, fill=None, stroke=None, lw=0.5, close=True, dash=None):
        c = self.c
        pth = c.beginPath()
        pth.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*self.p(*q))
        if close: pth.close()
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.drawPath(pth, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def line(self, u0, z0, u1, z1, color=DARK, lw=0.5, dash=None):
        c = self.c
        c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        c.line(*self.p(u0, z0), *self.p(u1, z1))
        c.setDash([])

    def pipe(self, pts, color, lw=2.0, dash=None, halo=True):
        c = self.c
        c.saveState(); c.setLineJoin(1); c.setLineCap(1)
        for col, w_, d_ in ((WHITE, lw + 1.8, None), (color, lw, dash)) if halo else ((color, lw, dash),):
            pth = c.beginPath(); pth.moveTo(*self.p(*pts[0]))
            for q in pts[1:]:
                pth.lineTo(*self.p(*q))
            c.setStrokeColorRGB(*col); c.setLineWidth(w_); c.setDash(d_ or [])
            c.drawPath(pth, stroke=1, fill=0)
        c.restoreState()

    def circle(self, u, z, r, fill=None, stroke=None, lw=0.6, dash=None, pt=False):
        c = self.c
        X, Y = self.p(u, z)
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.circle(X, Y, r if pt else r * self.s, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def text(self, u, z, s, size=6, font="Inter", color=DARK, anchor="c", rot=0, bg=False, dx=0, dy=0):
        c = self.c
        X, Y = self.p(u, z)
        c.saveState(); c.translate(X + dx, Y + dy); c.rotate(rot)
        w = pdfmetrics.stringWidth(s, font, size)
        off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
        if bg:
            c.setFillColorRGB(1, 1, 1); c.rect(off - 1.6, -size * 0.36 - 1.4, w + 3.2, size + 2.2, stroke=0, fill=1)
        c.setFont(font, size); c.setFillColorRGB(*color)
        c.drawString(off, -size * 0.36, s)
        c.restoreState()

    def hatch(self, u0, z0, u1, z1, step=5.0, ang=45, color=CONC_H, lw=0.3):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        c.saveState()
        pth = c.beginPath(); pth.rect(x0, y0, x1 - x0, y1 - y0); c.clipPath(pth, stroke=0, fill=0)
        c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        t = math.tan(math.radians(ang))
        h = y1 - y0
        k = x0 - h / t - step
        while k < x1 + step:
            c.line(k, y0, k + h / t, y1)
            k += step
        c.restoreState()

    def dots(self, u0, z0, u1, z1, step=5.0, color=FILL_H, r=0.35):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        c.saveState()
        pth = c.beginPath(); pth.rect(x0, y0, x1 - x0, y1 - y0); c.clipPath(pth, stroke=0, fill=0)
        c.setFillColorRGB(*color)
        j = 0
        yy = y0 + step / 2
        while yy < y1:
            xx = x0 + (step / 2 if j % 2 else step)
            while xx < x1:
                c.circle(xx, yy, r, stroke=0, fill=1)
                xx += step
            yy += step * 0.8; j += 1
        c.restoreState()

    def bricks(self, u0, z0, u1, z1, course=0.065, color=BRICK_H, lw=0.25):
        z = z0
        while z < z1 - 1e-6:
            self.line(u0, z, u1, z, color=color, lw=lw)
            z += course

    # ---- υλικά
    def concrete(self, pts):
        self.poly(pts, fill=CONC)
        us = [q[0] for q in pts]; zs = [q[1] for q in pts]
        c = self.c
        c.saveState()
        pth = c.beginPath(); pth.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*self.p(*q))
        pth.close(); c.clipPath(pth, stroke=0, fill=0)
        self.hatch(min(us), min(zs), max(us), max(zs), step=5.5)
        c.restoreState()
        self.poly(pts, stroke=DARK, lw=0.8)

    def concrete_r(self, u0, z0, u1, z1):
        self.concrete([(u0, z0), (u1, z0), (u1, z1), (u0, z1)])

    def fill_r(self, u0, u1, z0=None, z1=0.0):
        z0 = -FILL if z0 is None else z0
        self.rect(u0, z0, u1, z1, fill=FILLC)
        self.dots(u0, z0, u1, z1)
        self.line(u0, z1, u1, z1, color=DARK, lw=0.9)

    def brick_r(self, u0, z0, u1, z1):
        self.rect(u0, z0, u1, z1, fill=BRICK)
        self.bricks(u0, z0, u1, z1)
        self.rect(u0, z0, u1, z1, stroke=DARK, lw=0.7)

    def gyp_r(self, u0, z0, u1, z1, lw=0.6):
        self.rect(u0, z0, u1, z1, fill=GYP, stroke=GYP_S, lw=lw)

    def etics_r(self, u0, z0, u1, z1):
        self.rect(u0, z0, u1, z1, fill=ETICS, stroke=ETICS_S, lw=0.5)

    def board(self, u0, u1, z, down=True, t=0.0125):
        """Γυψοσανίδα οροφής (τελική στάθμη z = κάτω επιφάνεια) + σκελετός από πάνω."""
        self.rect(u0, z, u1, z + t, fill=WHITE, stroke=DARK, lw=0.7)
        self.line(u0, z + t + 0.027, u1, z + t + 0.027, color=GYP_S, lw=0.35, dash=[3, 1.2])

    # ---- διαστάσεις / στάθμες / σημάνσεις
    def dim_h(self, z, us, size=5.6, above=True, color=DIMC, fmt=mm2, dy=0, tick=3.0):
        c = self.c
        us = sorted(us)
        X0, Y = self.p(us[0], z); X1, _ = self.p(us[-1], z)
        Y += dy
        c.setStrokeColorRGB(*color); c.setLineWidth(0.4); c.line(X0, Y, X1, Y)
        for u in us:
            X, _ = self.p(u, z)
            c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(us[:-1], us[1:]):
            s = fmt(b - a)
            Xa, _ = self.p(a, z); Xb, _ = self.p(b, z)
            w = pdfmetrics.stringWidth(s, "Inter", size)
            c.setFont("Inter", size); c.setFillColorRGB(*color)
            if w <= (Xb - Xa) - 3:
                c.drawCentredString((Xa + Xb) / 2, Y + (2.2 if above else -size - 0.6), s)
            else:
                c.saveState(); c.translate((Xa + Xb) / 2 + size * 0.35, Y + (4 if above else -4 - w)); c.rotate(90)
                c.drawString(0, 0, s); c.restoreState()

    def dim_v(self, u, zs, size=5.6, left=True, color=DIMC, fmt=mm2, dx=0, tick=3.0):
        c = self.c
        zs = sorted(zs)
        X, Y0 = self.p(u, zs[0]); _, Y1 = self.p(u, zs[-1])
        X += dx
        c.setStrokeColorRGB(*color); c.setLineWidth(0.4); c.line(X, Y0, X, Y1)
        for z in zs:
            _, Y = self.p(u, z)
            c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(zs[:-1], zs[1:]):
            s = fmt(b - a)
            _, Ya = self.p(u, a); _, Yb = self.p(u, b)
            w = pdfmetrics.stringWidth(s, "Inter", size)
            c.setFont("Inter", size); c.setFillColorRGB(*color)
            if w <= (Yb - Ya) - 3:
                c.saveState(); c.translate(X + (-2.2 if left else size + 0.4), (Ya + Yb) / 2); c.rotate(90)
                c.drawCentredString(0, 0, s); c.restoreState()
            else:
                (c.drawRightString if left else c.drawString)(X + (-4 if left else 4), (Ya + Yb) / 2 - size * 0.35, s)

    def level(self, u, z, txt=None, right=True, size=6.2, color=DARK, lead=14, note=None, below=False):
        """Σύμβολο στάθμης: τρίγωνο πάνω στη στάθμη + τιμή (below=True: κάτω από τη γραμμή – για οροφές)."""
        c = self.c
        X, Y = self.p(u, z)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.5)
        d = 1 if right else -1
        k = -1 if below else 1
        if not below:
            c.line(X, Y, X + d * lead, Y)
        c.setFillColorRGB(*color)
        pth = c.beginPath(); pth.moveTo(X + d * 3.2, Y); pth.lineTo(X + d * 6.2, Y + k * 4.2); pth.lineTo(X + d * 0.2, Y + k * 4.2); pth.close()
        c.drawPath(pth, stroke=0, fill=1)
        s = txt or lv(z)
        c.setFont("Inter-Bold", size)
        w = pdfmetrics.stringWidth(s, "Inter-Bold", size)
        if below:
            lead = 7
        tx = X + d * (lead + 2) if right else X - lead - 2 - w
        ty = Y - size - 0.6 if below else Y + 0.6
        c.setFillColorRGB(1, 1, 1); c.rect(tx - 1, ty - 1.4, w + 2, size + 1.6, stroke=0, fill=1)
        c.setFillColorRGB(*color); c.drawString(tx, ty, s)
        if note:
            c.setFont("Inter", size - 1.2); c.setFillColorRGB(*GREY)
            wn = pdfmetrics.stringWidth(note, "Inter", size - 1.2)
            if below:
                c.setFillColorRGB(1, 1, 1)
                c.rect((tx + w + 2) if right else (tx - 4 - wn), ty - 1.2, wn + 3, size + 0.6, stroke=0, fill=1)
                c.setFillColorRGB(*GREY)
            if right:
                c.drawString(tx + w + 3, ty + 0.2, note)
            else:
                c.drawRightString(tx - 3, ty + 0.2, note)

    def badge(self, u, z, n, r=7.0, dx=0, dy=0):
        badge(self.c, self.p(u, z)[0] + dx, self.p(u, z)[1] + dy, n, r)

    def leader(self, a, b, lines, anchor="l", size=6.0, color=DARK, font="Inter-Medium", lh=None, dot=True):
        """Οδηγός από το σημείο a (u, z) ως το b (u, z) και κείμενο στο b (γραμμές προς τα κάτω)."""
        c = self.c
        X0, Y0 = self.p(*a); X1, Y1 = self.p(*b)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.line(X0, Y0, X1, Y1)
        if dot:
            c.setFillColorRGB(*color); c.circle(X0, Y0, 1.3, stroke=0, fill=1)
        lh = lh or size + 1.8
        for i, s in enumerate(lines if isinstance(lines, (list, tuple)) else [lines]):
            f = font if i == 0 else "Inter"
            w = pdfmetrics.stringWidth(s, f, size)
            tx = X1 + 3 if anchor == "l" else (X1 - 3 - w if anchor == "r" else X1 - w / 2)
            ty = Y1 - size * 0.36 - i * lh
            c.setFillColorRGB(1, 1, 1); c.rect(tx - 1.2, ty - 1.2, w + 2.4, size + 2.0, stroke=0, fill=1)
            c.setFont(f, size); c.setFillColorRGB(*color); c.drawString(tx, ty, s)

    def arrow(self, u0, z0, u1, z1, color=BLUE, lw=0.8, head=5.0):
        arrow(self.c, *self.p(u0, z0), *self.p(u1, z1), color=color, lw=lw, head=head)

    def cut_mark(self, u, z0, z1):
        """Γραμμή αποκοπής (η τομή συνεχίζει)."""
        c = self.c
        X, Y0 = self.p(u, z0); _, Y1 = self.p(u, z1)
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.6); c.setDash([7, 2, 1.5, 2]); c.line(X, Y0 - 6, X, Y1 + 6); c.setDash([])


# ---------------------------------------------------------------- βοηθητικά σελίδας
def arrow(c, x0, y0, x1, y1, color=BLUE, lw=0.8, head=5.0):
    c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash([])
    c.line(x0, y0, x1, y1)
    a = math.atan2(y1 - y0, x1 - x0)
    c.setFillColorRGB(*color)
    pth = c.beginPath(); pth.moveTo(x1, y1)
    pth.lineTo(x1 - head * math.cos(a - 0.38), y1 - head * math.sin(a - 0.38))
    pth.lineTo(x1 - head * math.cos(a + 0.38), y1 - head * math.sin(a + 0.38)); pth.close()
    c.drawPath(pth, stroke=0, fill=1)


def badge(c, X, Y, n, r=7.0, color=DARK):
    c.setFillColorRGB(*color); c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(1.0)
    c.circle(X, Y, r, stroke=1, fill=1)
    c.setFillColorRGB(1, 1, 1); c.setFont("Inter-Bold", r * 1.25)
    c.drawCentredString(X, Y - r * 0.44, str(n))


def wrap(s, font, size, w):
    out, cur = [], ""
    for wd in s.split(" "):
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) > w and cur:
            out.append(cur); cur = wd
        else:
            cur = t
    return out + [cur]


def para(c, x, y, w, s, size=7.0, font="Inter", color=DARK, lead=None, indent=0):
    lead = lead or size + 2.4
    for i, l in enumerate(wrap(s, font, size, w - indent)):
        c.setFont(font, size); c.setFillColorRGB(*color)
        c.drawString(x + indent, y, l); y -= lead
    return y


def head(c, x, y, s, size=9.5, color=DARK):
    c.setFont("Inter-Bold", size); c.setFillColorRGB(*color); c.drawString(x, y, s)
    return y - size - 5


STEPS = [
    ("ΤΟ ΜΗΧΑΝΗΜΑ ΜΕΝΕΙ ΣΤΗ ΛΩΡΙΔΑ ΤΗΣ ΕΙΣΟΔΟΥ", "ΚΜ1 καναλάτη, μέσα στη χαμηλή οροφή 1,10 δίπλα στον τοίχο της εισόδου (οροφή %s, κενό 35 cm). "
     "Οι συνδέσεις στο βόρειο άκρο της." % lv(LV_STRIP)),
    ("%s m ΜΕΣΑ ΣΤΗΝ ΨΕΥΔΟΡΟΦΗ ΤΗΣ ΛΩΡΙΔΑΣ" % mm2(UY0 - BYC), "Ψυκτικά και συμπυκνώματα πάνε προς βορρά, δίπλα στον τοίχο της εισόδου, ως τη γωνία. "
     "Σε αυτό το κομμάτι δεν υπάρχει δοκάρι."),
    ("ΚΑΝΑΛΙ ΓΩΝΙΑΣ ΚΓ %s" % A.BOX["size"], "Κουτί γυψοσανίδας στη γωνία, πίσω από το φύλλο της πόρτας εισόδου, από την οροφή ως το δάπεδο. "
     "Μέσα του οι σωλήνες ΚΑΤΕΒΑΙΝΟΥΝ στο δάπεδο."),
    ("ΚΑΤΩ ΑΠΟ ΤΟΝ ΤΟΙΧΟ, ΜΕΣΑ ΣΤΟ ΓΕΜΙΣΜΑ", "Περνούν μέσα στο γέμισμα του δαπέδου κάτω από τη βάση του γυψότοιχου Τ2-06 και μπαίνουν στο Υπν.2. "
     "Το δοκάρι Δ3.1 είναι ψηλά, από πάνω – δεν το αγγίζουμε."),
    ("%s m ΣΤΟ ΔΑΠΕΔΟ ΤΟΥ ΥΠΝ.2, ΚΟΛΛΗΤΑ ΣΤΟΝ ΤΟΙΧΟ" % mm2(BYC - EXIT_Y), "Μέσα στο γέμισμα 12 cm, σε λωρίδα 20 cm κατά μήκος του ανατολικού τοίχου "
     "(εκεί χωρίς ενδοδαπέδια). Τα συμπυκνώματα με κλίση 1 %."),
    ("ΠΕΣΣΟΣ ΜΕΣΑ ΣΤΗ ΝΤΟΥΛΑΠΑ – ΕΞΟΔΟΣ ΧΑΜΗΛΑ", "Στο τούβλο δίπλα στη μπαλκονόπορτα (μέσα στη ντουλάπα του Υπν.2): τα ψυκτικά ανεβαίνουν σε αυλάκι "
     "ως %s και βγαίνουν έξω· τα συμπυκνώματα από τη βάση του τοίχου." % lv(EXIT_Z)),
    ("ΒΑ ΕΞΩΣΤΗΣ", "Ψυκτικά → εξωτερική μονάδα. Συμπυκνώματα → σωλήνας του σιφωνιού του εξώστη → υδρορροή ΥΔ1 (με φυσική ροή, χωρίς αντλία)."),
]


def steps_panel(c, x, y, w, only=None, size=7.2, title="Η ΔΙΑΔΡΟΜΗ ΒΗΜΑ – ΒΗΜΑ"):
    y = head(c, x, y, title)
    for i, (t, d) in enumerate(STEPS, 1):
        if only and i not in only:
            continue
        badge(c, x + 7, y + 2.5, i, 7.0)
        c.setFont("Inter-Bold", size); c.setFillColorRGB(*DARK); c.drawString(x + 20, y, t)
        y -= size + 3.0
        y = para(c, x + 20, y, w - 20, d, size=size - 0.4) - 3.5
    return y


def legend(c, x, y, items, size=6.4, w=250, title="ΥΠΟΜΝΗΜΑ"):
    y = head(c, x, y, title, 8.5)
    for kind, col, txt in items:
        yy = y + 2
        if kind == "line":
            c.setStrokeColorRGB(*col); c.setLineWidth(2.0); c.setDash([]); c.line(x, yy, x + 22, yy)
        elif kind == "dash":
            c.setStrokeColorRGB(*col); c.setLineWidth(1.6); c.setDash([1.4, 1.8]); c.line(x, yy, x + 22, yy); c.setDash([])
        elif kind == "ddash":
            c.setStrokeColorRGB(*col); c.setLineWidth(1.2); c.setDash([4, 2]); c.line(x, yy, x + 22, yy); c.setDash([])
        elif kind == "box":
            c.setFillColorRGB(*col[0]); c.setStrokeColorRGB(*col[1]); c.setLineWidth(0.7); c.rect(x + 3, yy - 4, 16, 8, stroke=1, fill=1)
        elif kind == "hatch":
            c.setFillColorRGB(*col[0]); c.setStrokeColorRGB(*col[1]); c.setLineWidth(0.7); c.rect(x + 3, yy - 4, 16, 8, stroke=1, fill=1)
            c.setLineWidth(0.3)
            for k in range(4):
                c.line(x + 3 + k * 4, yy - 4, x + 7 + k * 4, yy + 4)
        elif kind == "badge":
            badge(c, x + 11, yy, col, 5.5)
        c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        ls = wrap(txt, "Inter", size, w - 30)
        for j, l in enumerate(ls):
            c.drawString(x + 30, y - j * (size + 1.8), l)
        y -= (size + 1.8) * len(ls) + 3.2
    return y


LEG_PIPES = [("line", MAG, "ψυκτικά ΚΜ1 (αερίου 5/8″ + υγρού 3/8″, προμονωμένος χαλκός)"),
             ("line", ORANGE, "συμπυκνώματα ΚΜ1 – PVC Ø 32, φυσική ροή"),
             ("ddash", BLUE2, "ψυκτικά split ΚΜ2 / ΚΜ3 (υπνοδωματίων)"),
             ("line", RAIN, "υδρορροή ΥΔ1 · σωλήνας σιφωνιού εξώστη Φ50"),
             ("box", (MAG_F, MAG), "ΚΓ κανάλι γωνίας %s (κουτί γυψοσανίδας)" % A.BOX["size"]),
             ("hatch", (CONC, DARK), "σκυρόδεμα: πλάκες, δοκάρια, κολόνες – δεν τρυπιέται, δεν περνάμε από κάτω του")]


def frame(c, no, theme, sub, scale_txt, floor="Α΄ · Β΄ · Γ΄ · Δ΄ ΟΡΟΦΟΣ (ίδια διαδρομή σε όλους)"):
    frame_and_title(c, no, theme, sub, floor, BASE, scale_txt, REV, DATE)


def big_title(c, x, y, t, sub=None):
    c.setFont("Inter-Bold", 13); c.setFillColorRGB(*DARK); c.drawString(x, y, t)
    if sub:
        c.setFont("Inter", 8); c.setFillColorRGB(*GREY); c.drawString(x, y - 12, sub)


def sec_marker(c, X, Y, letter, dx, dy, r=8.5):
    """Άκρο γραμμής τομής: κύκλος με γράμμα + βέλος προς τη φορά που κοιτάμε (dx, dy μοναδιαίο, σε pt σελίδας)."""
    c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(*RED); c.setLineWidth(1.2); c.circle(X, Y, r, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("Inter-Bold", 9.5); c.drawCentredString(X, Y - 3.4, letter)
    arrow(c, X + dx * (r + 1), Y + dy * (r + 1), X + dx * (r + 13), Y + dy * (r + 13), color=RED, lw=1.2, head=5.5)


# ================================================================ ΚΜ-01 κάτοψη διαδρομής (τυπικός όροφος)
def plan_bg(c, model, ox, oy, s, clip):
    """Υπόβαθρο: κάτοψη τοιχοποιιών του ορόφου (όπως στα φύλλα ανόψεων), κομμένη στο παράθυρο clip = (x0, y0, x1, y1) σε m."""
    sheets.bind(model)
    v = View(c, ox, oy, s)
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.saveState()
    pth = c.beginPath(); pth.rect(X0, Y0, X1 - X0, Y1 - Y0); c.clipPath(pth, stroke=0, fill=0)
    c.setFillColorRGB(1, 1, 1); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=0, fill=1)
    sheets.zones_fill(v, colored=False)
    sheets.plan(v)
    return v


def beams_plan(v, model, names, lab=None):
    c = v.c
    for name, sec, x0, y0, x1, y1 in model.BEAMS:
        if name not in names:
            continue
        c.saveState(); c.setFillAlpha(0.30)
        v.rect(x0, y0, x1, y1, fill=BEAMC)
        c.restoreState()
        v.hatch([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], 0.09, 45, BEAMC, 0.35)
        c.setDash([5, 2]); v.rect(x0, y0, x1, y1, stroke=BEAMC, lw=0.9); c.setDash([])
    for name, (x, y, r) in (lab or {}).items():
        sec = [b[1] for b in model.BEAMS if b[0] == name][0]
        v.text(x, y, "ΔΟΚΑΡΙ %s %s" % (name, sec), size=6.0, rot=r, color=BEAMC, font="Inter-Bold", bg=True)


def vpipe(v, pts, color, lw=2.0, dash=None, halo=True):
    c = v.c
    c.saveState(); c.setLineJoin(1); c.setLineCap(1 if not dash else 0)
    for col, w_, d_ in ((WHITE, lw + 1.6, None), (color, lw, dash)) if halo else ((color, lw, dash),):
        pth = c.beginPath(); pth.moveTo(*v.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*v.p(*q))
        c.setStrokeColorRGB(*col); c.setLineWidth(w_); c.setDash(d_ or [])
        c.drawPath(pth, stroke=1, fill=0)
    c.restoreState()


def vbadge(v, x, y, n, r=7.0, dx=0, dy=0):
    X, Y = v.p(x, y)
    badge(v.c, X + dx, Y + dy, n, r)


def vlabel(v, x, y, lines, anchor="l", size=6.0, color=DARK, to=None, font="Inter-SemiBold"):
    c = v.c
    X, Y = v.p(x, y)
    if to:
        X0, Y0 = v.p(*to)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.line(X0, Y0, X, Y)
        c.setFillColorRGB(*color); c.circle(X0, Y0, 1.3, stroke=0, fill=1)
    for i, s_ in enumerate(lines):
        f = font if i == 0 else "Inter"
        w = pdfmetrics.stringWidth(s_, f, size)
        tx = X + 3 if anchor == "l" else (X - 3 - w if anchor == "r" else X - w / 2)
        ty = Y - size * 0.36 - i * (size + 1.8)
        c.setFillColorRGB(1, 1, 1); c.rect(tx - 1.2, ty - 1.2, w + 2.4, size + 2.0, stroke=0, fill=1)
        c.setFont(f, size); c.setFillColorRGB(*color); c.drawString(tx, ty, s_)


def vdim(v, orient, pos, pts, size=6.0, side=1, fmt=None, color=DIMC, tick=2.8):
    """Αλυσίδα διαστάσεων σε κάτοψη (View) με στοιχεία σε pt – για κλίμακες 1:5 / 1:10. side: +1 κείμενο νότια / ανατολικά της γραμμής."""
    c = v.c
    fmt = fmt or cm
    pts = sorted(pts)
    c.setStrokeColorRGB(*color); c.setFillColorRGB(*color)
    if orient == "H":
        X0, Y = v.p(pts[0], pos); X1, _ = v.p(pts[-1], pos)
        c.setLineWidth(0.4); c.line(X0, Y, X1, Y)
        for q in pts:
            X, _ = v.p(q, pos); c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(pts[:-1], pts[1:]):
            Xa, _ = v.p(a, pos); Xb, _ = v.p(b, pos)
            c.setFont("Inter-SemiBold", size); c.drawCentredString((Xa + Xb) / 2, Y - size - 1.5 if side > 0 else Y + 2.2, fmt(b - a))
    else:
        X, Y0 = v.p(pos, pts[0]); _, Y1 = v.p(pos, pts[-1])
        c.setLineWidth(0.4); c.line(X, Y0, X, Y1)
        for q in pts:
            _, Y = v.p(pos, q); c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(pts[:-1], pts[1:]):
            _, Ya = v.p(pos, a); _, Yb = v.p(pos, b)
            c.saveState(); c.translate(X + (size + 1.0 if side > 0 else -2.4), (Ya + Yb) / 2); c.rotate(90)
            c.setFont("Inter-SemiBold", size); c.drawCentredString(0, 0, fmt(b - a)); c.restoreState()


def ac_unit_plan(v, model, slot_lab=True):
    """Μονάδα, plenum, slot, επιστροφή, θυρίδα και το όριο της χαμήλωσης (από το μοντέλο ανόψεων)."""
    c = v.c
    for r in getattr(model, "AC_OUTLINE", []):
        if isinstance(r[0], (tuple, list)):
            for a_, b_ in zip(r, r[1:]):
                v.line(*a_, *b_, color=(0.55, 0.42, 0.22), lw=0.9, dash=[5, 2.5])
    for name, r in model.DUCTS:
        v.rect(*r, fill=BLUE_F, stroke=BLUE, lw=0.5)
    for d in model.DIFFUSERS:
        x0, y0, x1, y1 = d["rect"]
        if d["kind"] == "slot":
            v.rect(x0, y0, x1, y1, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.6)
            n = 4
            for k in range(n):
                yy = y0 + (k + 0.5) * (y1 - y0) / n
                X0, Y0 = v.p(x0 - 0.03, yy); X1, Y1 = v.p(x0 - 0.42, yy)
                arrow(c, X0, Y0, X1, Y1, color=BLUE, lw=0.7, head=4.5)
        elif d["kind"] == "ret":
            v.rect(x0, y0, x1, y1, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.8)
    for u in model.UNITS:
        x0, y0, x1, y1 = u["rect"]
        v.rect(x0, y0, x1, y1, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.1)
        v.line(x0, y0, x1, y1, color=BLUE, lw=0.4); v.line(x0, y1, x1, y0, color=BLUE, lw=0.4)
    for h in model.HATCHES:
        c.setDash([2, 1.2]); v.rect(*h["rect"], stroke=DARK, lw=0.6); c.setDash([])


def section_line(v, a, b, letter, look, off=10):
    """Γραμμή τομής από a ως b (m) με κύκλους-γράμματα στα άκρα· look = φορά που κοιτάμε σε pt σελίδας (dx, dy)."""
    c = v.c
    X0, Y0 = v.p(*a); X1, Y1 = v.p(*b)
    c.setStrokeColorRGB(*RED); c.setLineWidth(1.1); c.setDash([9, 2.5, 1.5, 2.5]); c.line(X0, Y0, X1, Y1); c.setDash([])
    L = math.hypot(X1 - X0, Y1 - Y0)
    ux, uy = (X1 - X0) / L, (Y1 - Y0) / L
    sec_marker(c, X0 - ux * off, Y0 - uy * off, letter, *look)
    sec_marker(c, X1 + ux * off, Y1 + uy * off, letter, *look)


def sheet_plan(c):
    s = scale(40)
    clip = (3.25, -0.05, 11.95, 9.62)
    ox = 34 - clip[0] * s
    oy = PAGE_H - 815 - clip[1] * s
    v = plan_bg(c, A, ox, oy, s, clip)
    # δοκάρια που κλείνουν το καθιστικό
    beams_plan(v, A, ("Δ3.1", "Δ9.1", "Δ4.4", "Δ9.5", "Δ1.4"),
               {"Δ3.1": (7.45, 5.00, 0), "Δ9.1": (9.55, 8.35, 90), "Δ4.4": (7.35, 9.30, 0), "Δ9.5": (9.55, 2.62, 90), "Δ1.4": (7.75, 0.65, 0)})
    ac_unit_plan(v, A)
    # εξωτερική μονάδα · σιφώνι εξώστη · ΥΔ1
    c.setDash([3, 1.5]); v.rect(*EM, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=0.8); c.setDash([])
    vpipe(v, GULLY, RAIN, 1.6, halo=False)
    v.circle(GULLY[0][0], GULLY[0][1], 0.06, fill=WHITE, stroke=RAIN, lw=1.0)
    v.circle(YD1[0], YD1[1], 0.045, fill=RAIN, stroke=RAIN)
    # κανάλι γωνίας
    v.rect(BX0, BY0, BX1, BY1, fill=MAG_F, stroke=MAG, lw=1.1)
    # split (υπνοδωματίων)
    for a_, b_ in A.SPLIT_DRAW:
        vpipe(v, [a_, b_], BLUE2, 1.1, dash=[4, 2], halo=False)
    # οδεύσεις ΚΜ1: στην ψευδοροφή συνεχής γραμμή, στο δάπεδο κουκκίδες
    vpipe(v, A.COND_ROUTE, ORANGE, 1.9)
    vpipe(v, A.KM1_VOID, MAG, 2.2)
    vpipe(v, A.COND_FLOOR, ORANGE, 2.0, dash=[1.4, 1.9])
    vpipe(v, A.KM1_FLOOR, MAG, 2.4, dash=[1.4, 1.9])
    # ετικέτες
    v.text((UX0 + UX1) / 2, (UY0 + UY1) / 2 - 0.10, "ΚΜ1", size=8, font="Inter-Bold", color=BLUE, bg=True)
    v.text((UX0 + UX1) / 2, (UY0 + UY1) / 2 + 0.12, "μηχάνημα", size=5.4, color=BLUE, bg=True)
    v.text(7.10, 7.30, "ΚΑΘΙΣΤΙΚΟ", size=9, font="Inter-Bold", color=GREY)
    v.text(7.10, 7.52, "οροφή %s" % lv(LV_LIV), size=6, color=GREY)
    v.text(7.75, 3.10, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=9, font="Inter-Bold", color=GREY)
    v.text(7.75, 3.32, "οροφή %s" % lv(LV_BED), size=5.6, color=GREY)
    v.text(7.75, 3.47, "(κανένας σωλήνας της ΚΜ1 στην οροφή του)", size=5.2, color=GREY)
    v.text(4.85, 3.85, "ΧΩΛ", size=7.5, font="Inter-Bold", color=GREY)
    v.text(5.72, 2.00, "ΛΟΥΤΡΟ", size=6.5, font="Inter-Bold", color=GREY)
    v.text(10.62, 2.25, "ΒΑ ΕΞΩΣΤΗΣ", size=7.5, font="Inter-Bold", color=GREY)
    v.text((EM[0] + EM[2]) / 2, (EM[1] + EM[3]) / 2, "εξωτ. μονάδα", size=5.4, color=BLUE, font="Inter-SemiBold")
    v.text((EM[0] + EM[2]) / 2, EM[3] + 0.12, "(θέση ενδεικτική)", size=4.8, color=BLUE, bg=True)
    v.text(10.75, 6.55, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=7.5, font="Inter-Bold", color=GREY)
    v.text(11.20, 8.85, "ΚΟΥΖΙΝΑ", size=8, font="Inter-Bold", color=GREY)
    v.text(11.20, 9.04, "οροφή %s (ενιαία με τη λωρίδα)" % lv(LV_STRIP), size=5.4, color=GREY)
    v.text(STRIP_X - 0.13, 8.30, "ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ 1,10 · οροφή %s" % lv(LV_STRIP), size=5.6, rot=90, color=(0.45, 0.33, 0.15), font="Inter-SemiBold", bg=True)
    v.text(7.95, 1.05, "ντουλάπα Υπν.2", size=5.6, color=GREY, bg=True)
    vlabel(v, 10.02, 5.02, ["ΚΓ ΚΑΝΑΛΙ ΓΩΝΙΑΣ %s" % A.BOX["size"], "πίσω από την πόρτα εισόδου:", "οι σωλήνες κατεβαίνουν στο δάπεδο"], color=MAG, to=(BX1 - 0.02, BYC), size=6.2)
    vlabel(v, 8.05, 4.42, ["ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ (γέμισμα)", "λωρίδα 20 cm στον τοίχο,", "χωρίς ενδοδαπέδια"], anchor="r", color=MAG, to=(CX - 0.03, 4.30), size=6.0)
    vlabel(v, 8.05, 6.02, ["ΜΕΣΑ ΣΤΗΝ ΨΕΥΔΟΡΟΦΗ", "%s m δίπλα στον τοίχο" % mm2(UY0 - BYC)], anchor="r", color=MAG, to=(CX - 0.03, 5.95), size=6.0)
    vlabel(v, 10.25, 0.28, ["ΥΔ1 υδρορροή", "(συμπυκνώματα)"], color=RAIN, to=(YD1[0] + 0.03, YD1[1]), size=5.8)
    vlabel(v, 8.55, 2.05, ["ψυκτικά split ΚΜ2 / ΚΜ3:", "κατεβαίνουν μέσα στη ντουλάπα"], anchor="r", color=BLUE2, to=(A.SPLIT_DROP[0] - 0.04, A.SPLIT_DROP[1] + 0.02), size=5.6)
    # βήματα
    vbadge(v, (UX0 + UX1) / 2 - 0.02, UY1 - 0.20, 1)
    vbadge(v, KX, 5.80, 2, dx=11)
    vbadge(v, BX0, BYC, 3, dx=-10, dy=-9)
    vbadge(v, KX, 4.93, 4, dx=12)
    vbadge(v, KX, 3.40, 5, dx=12)
    vbadge(v, 9.575, EXIT_Y, 6, dy=-12)
    vbadge(v, 10.05, 1.75, 7)
    # γραμμές τομών
    c.restoreState()
    section_line(v, (9.27, 0.24), (9.27, 8.30), "Α", (1, 0))
    section_line(v, (7.80, 7.15), (10.22, 7.15), "Β", (0, 1))
    section_line(v, (8.95, 1.25), (11.52, 1.25), "Γ", (0, 1))
    # πλαίσιο κάτοψης
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    # δεξιά στήλη
    x, w = X1 + 26, 1160 - (X1 + 26)
    big_title(c, x, 800, "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1 – ΔΙΑΔΡΟΜΗ ΣΩΛΗΝΩΝ", "Κάτοψη τυπικού ορόφου (Α΄ · Β΄ · Γ΄ · Δ΄) · οι τομές Α-Α, Β-Β, Γ-Γ στα επόμενα φύλλα")
    y = 766
    y = head(c, x, y, "ΓΙΑΤΙ ΕΤΣΙ", 9.5, RED)
    y = para(c, x, y, w / 2 - 12, "Το σαλόνι κλείνεται γύρω-γύρω από δοκάρια (καφέ στην κάτοψη): Δ3.1 προς τα δωμάτια, Δ9.1 προς την είσοδο και την κουζίνα, "
             "Δ4.4 και Δ7.1 στις τζαμαρίες. Ό,τι φύγει από την ψευδοροφή του πρέπει να περάσει κάτω από δοκάρι.", size=7.2)
    y = para(c, x, y - 3, w / 2 - 14, "Για να ΜΗΝ περάσει τίποτα κάτω από δοκάρι, οι σωλήνες του μηχανήματος κατεβαίνουν σε ένα κανάλι στη γωνία και φεύγουν "
             "μέσα στο ΔΑΠΕΔΟ ως τον ΒΑ εξώστη. Δοκάρι δεν τρυπιέται πουθενά.", size=7.2, font="Inter-SemiBold")
    y2 = 766
    x2 = x + w / 2 + 6
    y2 = head(c, x2, y2, "ΤΙ ΑΛΛΑΖΕΙ ΣΤΟ ΣΠΙΤΙ", 9.5)
    for t in ["Κουτί %s στη γωνία πίσω από την πόρτα εισόδου (δεν εμποδίζει το φύλλο)." % A.BOX["size"],
              "Στο Υπν.2 λωρίδα 20 cm στο δάπεδο δίπλα στον τοίχο χωρίς ενδοδαπέδια.",
              "Οροφή λωρίδας εισόδου και κουζίνας %s (3 cm ψηλότερα από πριν) – ενιαία, χωρίς δόντι." % lv(LV_STRIP),
              "Τα συμπυκνώματα πάνε στην υδρορροή του ΒΑ εξώστη (όχι στον νεροχύτη).",
              "Εξωτερική μονάδα στον ΒΑ εξώστη – οι σωλήνες βγαίνουν χαμηλά, πίσω της."]:
        c.setFillColorRGB(*DARK); c.circle(x2 + 2.5, y2 + 2.4, 1.3, stroke=0, fill=1)
        y2 = para(c, x2 + 9, y2, w / 2 - 20, t, size=7.0) - 2
    y = min(y, y2) - 12
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.5); c.line(x, y + 6, x + w, y + 6)
    y -= 8
    yl = steps_panel(c, x, y, w)
    legend(c, x, yl - 6, [("line", MAG, "ψυκτικά ΚΜ1 μέσα στην ΨΕΥΔΟΡΟΦΗ"),
                                  ("dash", MAG, "ψυκτικά ΚΜ1 μέσα στο ΔΑΠΕΔΟ (γέμισμα)"),
                                  ("line", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 στην ψευδοροφή"),
                                  ("dash", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 στο δάπεδο, κλίση 1 %"),
                                  ("ddash", BLUE2, "ψυκτικά split υπνοδωματίων (ψευδοροφή)"),
                                  ("line", RAIN, "σωλήνας σιφωνιού εξώστη → υδρορροή ΥΔ1"),
                                  ("box", (MAG_F, MAG), "ΚΓ κανάλι γωνίας %s" % A.BOX["size"]),
                                  ("hatch", ((0.86, 0.75, 0.68), BEAMC), "δοκάρια (δεν περνάμε από κάτω τους)"),
                                  ("badge", 3, "βήμα της διαδρομής (ίδιοι αριθμοί στις τομές)")], w=w)
    north_arrow(c, X1 - 20, Y1 - 24, 9)
    frame(c, "ΚΜ-01", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΔΙΑΔΡΟΜΗ", "Κάτοψη · οι σωλήνες της ΚΜ1 δεν περνούν κάτω από δοκάρι", "Κλίμακα 1:40 · A3")


# ================================================================ ΚΜ-02 τομή Α-Α (κατά μήκος της διαδρομής, κοιτάμε ανατολικά)
def cross_mark(sv, u, z, col, r=3.6):
    """Σύμβολο «ο σωλήνας στρίβει και φεύγει προς τα μέσα (μακριά μας)»."""
    c = sv.c
    sv.circle(u, z, r, fill=WHITE, stroke=col, lw=1.0, pt=True)
    X, Y = sv.p(u, z)
    k = r * 0.62
    c.setStrokeColorRGB(*col); c.setLineWidth(0.9); c.line(X - k, Y - k, X + k, Y + k); c.line(X - k, Y + k, X + k, Y - k)


def msg_box(c, X, Y, w, title, lines, size=6.2):
    """Κόκκινο πλαίσιο-μήνυμα· (X, Y) = πάνω-αριστερά."""
    h = 13 + len(lines) * (size + 2.2) + 4
    c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(*RED); c.setLineWidth(1.0); c.roundRect(X, Y - h, w, h, 4, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("Inter-Bold", size + 0.8); c.drawString(X + 6, Y - 11, title)
    c.setFont("Inter", size); c.setFillColorRGB(*DARK)
    for i, l in enumerate(lines):
        c.drawString(X + 6, Y - 11 - (i + 1) * (size + 2.2), l)
    return h


def bullets(c, x, y, w, items, size=7.2):
    for t in items:
        c.setFillColorRGB(*DARK); c.circle(x + 2.5, y + 2.6, 1.4, stroke=0, fill=1)
        y = para(c, x + 10, y, w - 12, t, size=size) - 4
    return y


def sheet_aa(c):
    S = scale(25)
    Y0, Y1 = 0.28, 8.10
    ZB = -0.36
    sv = Sec(c, 44, 396, S, u0=Y0)
    d19, d31 = BEAM["Δ1.4"], BEAM["Δ3.1"]
    s55 = A.beam_soffit("30/55")
    # ---- φόντο: ό,τι βλέπουμε πίσω από την τομή (ανατολικός τοίχος)
    sv.rect(WARD[3], 0, T206[1], LV_BED, fill=WALL_BG)                       # τοίχος Υπν.2
    sv.rect(BY1, 0, Y1, LV_STRIP, fill=WALL_BG)                              # τοίχος εισόδου
    sv.rect(WARD[3], s55, 3.00, LV_BED, fill=CONC_L)                         # Δ9.5 πάνω από τη μπαλκονόπορτα
    sv.rect(K3[1], 0, T206[1], LV_BED, fill=CONC_L, stroke=(0.7, 0.7, 0.72), lw=0.4)      # κολόνα Κ3
    sv.text((K3[1] + T206[1]) / 2, 1.02, "ΚΟΛΟΝΑ Κ3", size=6.5, color=GREY, font="Inter-SemiBold")
    sv.text((K3[1] + T206[1]) / 2, 0.90, "(πίσω)", size=5.4, color=GREY)
    sv.rect(W206[1], 0, W206[3], s55, fill=(0.90, 0.95, 0.99), stroke=(0.35, 0.45, 0.60), lw=0.8)        # μπαλκονόπορτα W2.06
    sv.rect(W206[1] + 0.06, 0.06, W206[3] - 0.06, s55 - 0.06, stroke=(0.35, 0.45, 0.60), lw=0.4)
    sv.text((W206[1] + W206[3]) / 2, 1.78, "μπαλκονόπορτα", size=6, color=(0.30, 0.40, 0.55), font="Inter-SemiBold")
    sv.text((W206[1] + W206[3]) / 2, 1.67, "προς τον ΒΑ εξώστη", size=5.4, color=(0.30, 0.40, 0.55))
    sv.rect(EM[1], 0.08, EM[3], 0.78, fill=(0.95, 0.97, 1.0), stroke=BLUE, lw=0.7, dash=[3, 1.5])          # εξωτερική μονάδα (έξω, στον εξώστη)
    sv.rect(DOOR[0], 0, DOOR[1], 2.20, fill=(0.93, 0.89, 0.82), stroke=WOOD_S, lw=0.9)                    # πόρτα εισόδου
    sv.rect(DOOR[0] + 0.05, 0.05, DOOR[1] - 0.05, 2.15, stroke=WOOD_S, lw=0.4)
    sv.circle(DOOR[1] - 0.10, 1.02, 2.2, fill=WOOD_S, pt=True)
    sv.text((DOOR[0] + DOOR[1]) / 2 + 0.06, 1.05, "ΠΟΡΤΑ ΕΙΣΟΔΟΥ", size=6.5, color=WOOD_S, font="Inter-Bold")
    sv.text((DOOR[0] + DOOR[1]) / 2 + 0.06, 0.93, "1,00 × 2,20", size=5.4, color=WOOD_S)
    sv.rect(T6A1[3], 0, Y1, LV_STRIP, fill=WHITE)                                                          # άνοιγμα κουζίνας
    sv.text((T6A1[3] + Y1) / 2, 1.05, "άνοιγμα", size=5.4, color=GREY); sv.text((T6A1[3] + Y1) / 2, 0.94, "κουζίνας", size=5.4, color=GREY)
    sv.rect(BY0, A.beam_soffit("30/50"), Y1, SOF8, fill=CONC_L)                                            # Δ9.1 πίσω, μέσα στο κενό
    sv.text(7.93, 2.70, "Δ9.1 (πίσω)", size=4.8, color=GREY)
    # ---- φέρων οργανισμός (τομή)
    sv.etics_r(0.40, ZB, 0.50, TOP + 0.02)
    sv.concrete([(d19[3], A.beam_soffit(d19[1])), (d19[5], A.beam_soffit(d19[1])), (d19[5], SOF3), (d31[3], SOF3),
                 (d31[3], A.beam_soffit(d31[1])), (d31[5], A.beam_soffit(d31[1])), (d31[5], SOF8), (Y1, SOF8), (Y1, TOP), (d19[3], TOP)])
    sv.concrete([(d19[3], -FILL), (Y1, -FILL), (Y1, -FILL - 0.20), (d31[5], -FILL - 0.20), (d31[5], ZB), (d31[3], ZB), (d31[3], -FILL - 0.18),
                 (d19[5], -FILL - 0.18), (d19[5], ZB), (d19[3], ZB)])
    sv.brick_r(T104[1], -FILL, T104[3], A.beam_soffit(d19[1]))               # βόρειος τοίχος (τούβλο) κάτω από τη Δ1.4
    sv.fill_r(T104[3], T206[1])
    sv.fill_r(BY1, Y1)
    # ντουλάπα Υπν.2 (τομή)
    wsof = A.beam_soffit(d19[1])
    sv.poly([(WARD[1], 0), (WARD[3], 0), (WARD[3], LV_BED), (d19[5], LV_BED), (d19[5], wsof), (WARD[1], wsof)], fill=WOOD, stroke=WOOD_S, lw=0.8)
    sv.line(WARD[1], 0, WARD[3], wsof, color=WOOD_S, lw=0.3); sv.line(WARD[1], wsof, WARD[3], 0, color=WOOD_S, lw=0.3)
    sv.rect(d19[5], LV_BED, WARD[3], SOF3, fill=WOOD, stroke=WOOD_S, lw=0.5)
    sv.text((WARD[1] + WARD[3]) / 2, 1.70, "ΝΤΟΥΛΑΠΑ ΥΠΝ.2", size=6.0, color=WOOD_S, font="Inter-Bold", rot=90, bg=True)
    # οροφές
    sv.board(WARD[3], d31[3], LV_BED)
    sv.rect(d31[3] - 0.0125, LV_B50 - 0.0125, d31[3], LV_BED, fill=WHITE, stroke=DARK, lw=0.6)          # μετώπη στη δοκό
    sv.rect(d31[3], LV_B50 - 0.0125, T206[1], LV_B50, fill=WHITE, stroke=DARK, lw=0.6)                   # γυψοσανίδα περασιά κάτω από τη Δ3.1
    sv.board(BY1, Y1, LV_STRIP)
    # τοίχος Τ2-06 + κανάλι γωνίας
    sv.gyp_r(T206[1], -FILL, T206[3], A.beam_soffit(d31[1]))
    sv.rect(BY0, -FILL, BY1, LV_STRIP, fill=WHITE)
    sv.rect(BY1 - 0.0125, -FILL, BY1, LV_STRIP + 0.0125, fill=MAG_F, stroke=MAG, lw=0.8)
    # μονάδα · στόμιο επιστροφής · θυρίδα
    sv.rect(UY0, U_BOT, UY1, U_TOP, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.2)
    sv.text((UY0 + UY1) / 2 + 0.10, (U_BOT + U_TOP) / 2 + 0.035, "ΚΜ1", size=9, font="Inter-Bold", color=BLUE)
    sv.text((UY0 + UY1) / 2 + 0.10, (U_BOT + U_TOP) / 2 - 0.065, "το μηχάνημα", size=5.2, color=BLUE)
    sv.rect(RET[1], LV_STRIP - 0.004, RET[3], LV_STRIP + 0.0165, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.8)
    k = RET[1] + 0.06
    while k < RET[3]:
        sv.line(k, LV_STRIP - 0.004, k + 0.03, LV_STRIP + 0.0165, color=GREEN, lw=0.4); k += 0.07
    sv.rect(HATCH[1], LV_STRIP - 0.004, HATCH[3], LV_STRIP + 0.0165, fill=WHITE, stroke=DARK, lw=0.7, dash=[2, 1.2])
    # ---- σωλήνες
    yr, yc = BY0 + 0.020, BY0 + 0.046              # μέσα στο κανάλι (στην πραγματικότητα δίπλα-δίπλα – εδώ μετατοπισμένοι για να φαίνονται και οι δύο)
    sv.pipe([(EXIT_Y, Z_REF), (EXIT_Y, EXIT_Z)], MAG, 1.6, dash=[2.5, 2])                                 # αυλάκι στον πεσσό (πίσω από τη ντουλάπα)
    sv.pipe([(UY0, Z_C_VOID_START), (yc, Z_C_VOID_END), (yc, Z_C_START + R_CON), (COND_TURN_Y, Z_C_TURN + R_CON)], ORANGE, 1.9)
    sv.pipe([(UY0, Z_R_VOID), (yr, Z_R_VOID), (yr, Z_REF), (EXIT_Y, Z_REF)], MAG, 2.3)
    cross_mark(sv, EXIT_Y, Z_REF, MAG); cross_mark(sv, COND_TURN_Y, Z_C_TURN + R_CON, ORANGE)
    # ---- κείμενα χώρων / δοκάρια
    sv.text(3.10, 1.42, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=11, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(7.10, 1.42, "ΚΑΘΙΣΤΙΚΟ", size=11, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(7.10, 1.28, "λωρίδα εισόδου", size=6.5, color=(0.62, 0.62, 0.66))
    sv.text(0.345, 1.45, "ΒΟΡΕΙΑ ΟΨΗ", size=5.2, color=GREY, rot=90)
    sv.text((d31[3] + d31[5]) / 2, 2.83, "ΔΟΚΑΡΙ", size=5.6, font="Inter-Bold", color=WHITE)
    sv.text((d31[3] + d31[5]) / 2, 2.72, "Δ3.1", size=7.0, font="Inter-Bold", color=WHITE)
    sv.text((d31[3] + d31[5]) / 2, 2.62, "30/50", size=5.2, font="Inter-SemiBold", color=WHITE)
    sv.text((d19[3] + d19[5]) / 2, 2.72, "Δ1.4", size=6.0, font="Inter-Bold", color=WHITE)
    sv.text(3.00, 2.89, "ΠΛΑΚΑ Π3 (πάχος 18)", size=5.6, font="Inter-SemiBold", color=WHITE)
    sv.text(6.90, 2.88, "ΠΛΑΚΑ Π8 (πάχος 20)", size=5.6, font="Inter-SemiBold", color=WHITE)
    # ---- στάθμες
    sv.level(Y1, TOP, right=True, note="πάνω από την πλάκα")
    sv.level(Y1, SOF8, right=True, note="κάτω από την πλάκα")
    sv.level(Y1, LV_STRIP, right=True, note="οροφή λωρίδας εισόδου")
    sv.level(Y1, 0.0, right=True, note="δάπεδο")
    sv.level(Y1, -FILL, right=True, note="πλάκα (γέμισμα 12 cm)")
    sv.level(2.52, LV_BED, right=True, below=True, note="οροφή Υπν.2 – κανένας σωλήνας της ΚΜ1 εδώ πάνω")
    sv.level(d31[3] - 0.03, LV_B50, right=False, lead=8, note="κάτω από το δοκάρι")
    # ---- οδηγοί / βήματα
    sv.badge(UY0 + 0.16, (U_BOT + U_TOP) / 2, 1)
    sv.leader(((RET[1] + RET[3]) / 2, LV_STRIP - 0.01), ((RET[1] + RET[3]) / 2, 2.27), ["στόμιο επιστροφής"], anchor="c", size=5.4, color=GREEN, dot=False)
    sv.leader(((HATCH[1] + HATCH[3]) / 2, LV_STRIP - 0.01), ((HATCH[1] + HATCH[3]) / 2 + 0.02, 2.31), ["θυρίδα 60×60"], anchor="c", size=5.4, color=DARK, dot=False)
    sv.badge(5.82, Z_R_VOID, 2)
    sv.leader((6.00, Z_R_VOID), (6.42, 2.10), ["ψυκτικά (ψηλά, δίπλα στον τοίχο)"], anchor="l", size=5.6, color=MAG)
    sv.leader((6.12, Z_C_VOID_START - 0.008), (6.42, 1.93), ["συμπυκνώματα Ø 32 – κλίση προς το κανάλι"], anchor="l", size=5.6, color=ORANGE)
    sv.badge(BY0 - 0.13, 1.62, 3)
    sv.leader((BY1, 1.62), (BY1 + 0.10, 1.82), ["ΚΑΝΑΛΙ ΓΩΝΙΑΣ ΚΓ:", "οι σωλήνες κατεβαίνουν"], anchor="l", size=5.8, color=MAG, dot=False)
    sv.badge((T206[1] + T206[3]) / 2, -FILL - 0.095, 4)
    sv.badge(3.40, -FILL - 0.095, 5)
    sv.badge(EXIT_Y - 0.14, 0.14, 6)
    sv.leader((EXIT_Y, 0.20), (1.50, 0.60), ["στον πεσσό (πίσω από τη ντουλάπα):", "τα ψυκτικά ανεβαίνουν ως %s" % lv(EXIT_Z), "και βγαίνουν στον εξώστη → ΤΟΜΗ Γ-Γ"], anchor="l", size=5.6, color=MAG, dot=False)
    sv.badge((EM[1] + EM[3]) / 2, 0.92, 7, r=6)
    sv.text((EM[1] + EM[3]) / 2 + 0.11, 0.92, "εξωτ. μονάδα (έξω, στον εξώστη)", size=5.2, color=BLUE, anchor="l", bg=True)
    # ---- ΤΟ ΜΗΝΥΜΑ
    X, Y = sv.p(3.20, 2.46)
    h = msg_box(c, X, Y, 172, "ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ ΔΕΝ ΠΕΡΝΑ ΤΙΠΟΤΑ", ["στην οροφή. Οι σωλήνες κατεβαίνουν στο κανάλι", "και περνούν από το ΔΑΠΕΔΟ, κάτω από τον τοίχο."])
    arrow(c, X + 172, Y - 12, sv.p(d31[3] + 0.10, 0)[0], sv.p(0, LV_B50 - 0.035)[1], color=RED, lw=0.9)
    arrow(c, X + 150, Y - h, sv.p(4.98, 0)[0], sv.p(0, 0.04)[1], color=RED, lw=0.9)
    # ---- διαστάσεις
    sv.dim_h(ZB, [T104[1], WARD[1], WARD[3], T206[1], T206[3], BY1, UY0, UY1], dy=-13, above=False)
    sv.dim_h(ZB, [EXIT_Y, BYC], dy=-32, above=False, color=MAG, fmt=lambda v_: "%s m μέσα στο ΔΑΠΕΔΟ του Υπν.2" % mm2(v_), size=6.0)
    sv.dim_h(ZB, [BYC, UY0], dy=-32, above=False, color=MAG, fmt=lambda v_: "%s m στην ψευδοροφή" % mm2(v_), size=6.0)
    sv.cut_mark(Y1, ZB, TOP)
    # ---- το δάπεδο σε μεγέθυνση (ίδια οριζόντια κλίμακα, ύψη × 3)
    fz = Sec(c, 44, 248, S, u0=Y0, sz=S * 3)
    c.setFont("Inter-Bold", 8.5); c.setFillColorRGB(*DARK); c.drawString(44, 300, "ΤΟ ΔΑΠΕΔΟ ΣΕ ΜΕΓΕΘΥΝΣΗ")
    c.setFont("Inter", 6.6); c.setFillColorRGB(*GREY)
    c.drawString(168, 300, "ίδιες θέσεις με την τομή από πάνω · τα ύψη × 3, για να φαίνονται οι σωλήνες μέσα στο γέμισμα των 12 cm")
    zb = -0.30
    fz.concrete_r(d19[3], zb, Y1, -FILL)
    fz.brick_r(T104[1], -FILL, T104[3], 0.035)
    fz.rect(T104[3], -FILL, T206[1], 0, fill=FILLC); fz.dots(T104[3], -FILL, T206[1], 0, step=6)
    fz.rect(BY1, -FILL, Y1, 0, fill=FILLC); fz.dots(BY1, -FILL, Y1, 0, step=6)
    fz.gyp_r(T206[1], -FILL, T206[3], 0.035)
    fz.rect(BY0, -FILL, BY1, 0.035, fill=WHITE)
    fz.rect(BY1 - 0.0125, -FILL, BY1, 0.035, fill=MAG_F, stroke=MAG, lw=0.8)
    fz.rect(WARD[1], 0, WARD[3], 0.035, fill=WOOD, stroke=WOOD_S, lw=0.7)
    fz.line(T104[3], 0, T206[1], 0, color=DARK, lw=1.0); fz.line(BY1, 0, Y1, 0, color=DARK, lw=1.0)
    band_r = [(yr + 0.02, Z_REF - R_GAS), (EXIT_Y, Z_REF - R_GAS), (EXIT_Y, Z_REF + R_GAS), (yr + 0.02, Z_REF + R_GAS)]
    band_c = [(yc, Z_C_START), (COND_TURN_Y, Z_C_TURN), (COND_TURN_Y, Z_C_TURN + 2 * R_CON), (yc, Z_C_START + 2 * R_CON)]
    c.saveState(); c.setFillAlpha(0.55); fz.poly(band_r, fill=MAG_F); c.restoreState()
    fz.poly(band_r, stroke=MAG, lw=1.0)
    fz.pipe([(yr, 0.035), (yr, Z_REF)], MAG, 2.2)
    c.saveState(); c.setFillAlpha(0.60); fz.poly(band_c, fill=ORANGE_F); c.restoreState()
    fz.poly(band_c, stroke=ORANGE, lw=1.0)
    fz.pipe([(yc + 0.012, 0.035), (yc + 0.012, Z_C_START + R_CON)], ORANGE, 1.8)
    cross_mark(fz, EXIT_Y, Z_REF, MAG, 4.2); cross_mark(fz, COND_TURN_Y, Z_C_TURN + R_CON, ORANGE, 4.2)
    fz.text(6.75, -FILL / 2, "γέμισμα καθιστικού – εδώ δεν περνά σωλήνας", size=5.8, color=FILL_H, font="Inter-SemiBold", bg=True)
    fz.text(6.75, -0.215, "ΠΛΑΚΑ", size=6, color=WHITE, font="Inter-Bold")
    fz.text(2.9, -0.255, "ΠΛΑΚΑ", size=6, color=WHITE, font="Inter-Bold")
    fz.level(Y1, 0.0, right=True, note="τελικό δάπεδο")
    fz.level(Y1, -FILL, right=True, note="πλάκα")
    fz.leader((3.95, Z_REF + 0.004), (3.95, 0.068), ["ΨΥΚΤΙΚΑ: πάνω στην πλάκα, μέσα σε σπιράλ προστασίας, χωρίς ενώσεις"], anchor="c", size=5.8, color=MAG, dot=False)
    fz.leader((2.05, cond_inv(BYC - 2.05) + R_CON), (2.05, 0.068), ["ΣΥΜΠΥΚΝΩΜΑΤΑ Ø 32: κλίση 1 % προς τον εξώστη"], anchor="c", size=5.8, color=ORANGE, dot=False)
    X, Y = fz.p(2.90, cond_inv(BYC - 2.90) + R_CON)
    arrow(c, X + 20, Y + 0.6, X - 20, Y - 0.6, color=ORANGE, lw=1.0, head=5)
    fz.leader((yc + 0.03, Z_C_START), (5.45, -0.165), ["αρχή: ροή %s" % lv(Z_C_START, 3), "(ράχη %s cm κάτω από το δάπεδο)" % cm(COVER)], anchor="l", size=5.4, color=ORANGE)
    fz.leader((COND_TURN_Y, Z_C_TURN), (1.06, -0.205), ["εδώ ροή %s · στην υδρορροή %s" % (lv(Z_C_TURN, 3), lv(Z_C_END, 3)), "(%s cm πάνω από την πλάκα)" % cm(FILL + Z_C_END)],
              anchor="l", size=5.4, color=ORANGE)
    fz.text((T206[1] + T206[3]) / 2 - 0.02, 0.068, "τοίχος", size=5.0, color=GYP_S, font="Inter-SemiBold", anchor="r")
    fz.text(BY1 + 0.03, 0.068, "ΚΓ", size=5.6, color=MAG, font="Inter-Bold", anchor="l")
    fz.text((WARD[1] + WARD[3]) / 2, 0.068, "ντουλάπα", size=5.2, color=WOOD_S, font="Inter-SemiBold")
    fz.badge((T206[1] + T206[3]) / 2, -FILL - 0.07, 4, r=6)
    fz.badge(3.80, -FILL - 0.07, 5, r=6)
    fz.cut_mark(Y1, zb, 0.03)
    X, Y = fz.p(Y0 + 0.14, -FILL / 2)
    c.saveState(); c.translate(X, Y); c.rotate(90); c.setFont("Inter-SemiBold", 5.4); c.setFillColorRGB(*DIMC)
    c.drawCentredString(0, 0, "γέμισμα 12 cm"); c.restoreState()
    # τίτλος / υπόμνημα
    big_title(c, 44, 806, "ΤΟΜΗ Α-Α · κατά μήκος της διαδρομής", "κοιτάμε προς ανατολή (τοίχος εισόδου · τοίχος Υπν.2) · αριστερά ο βορράς και ο ΒΑ εξώστης, δεξιά το καθιστικό")
    legend(c, 640, 812, LEG_PIPES[:2] + [("badge", 3, "βήμα της διαδρομής (όπως στην κάτοψη ΚΜ-01)")], size=5.8, w=250, title="")
    legend(c, 900, 812, LEG_PIPES[4:], size=5.8, w=262, title="")
    frame(c, "ΚΜ-02", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Α-Α", "Κατά μήκος της διαδρομής: μηχάνημα → κανάλι γωνίας → δάπεδο Υπν.2", "Κλίμακα 1:25 · A3")


# ================================================================ ΚΜ-03 τομή Β-Β (μέσα από το μηχάνημα, κοιτάμε βόρεια)
def sheet_bb(c):
    S = scale(10)
    X0, X1 = 7.80, 10.22
    ZB = -0.36
    sv = Sec(c, 44, 214, S, u0=X0, brk=(0.32, 1.60, 16))
    d91 = BEAM["Δ9.1"]
    b_sof = A.beam_soffit(d91[1])
    # ---- φόντο (βόρειος τοίχος του καθιστικού / κλιμακοστάσιο, πίσω)
    sv.rect(X0, 0, STRIP_X, LV_LIV, fill=WALL_BG)
    sv.rect(STRIP_X, 0, T6A1[0], LV_STRIP, fill=WALL_BG)
    sv.rect(T6A1[2], 0, X1, LV_STAIR, fill=(0.975, 0.975, 0.975))
    sv.rect(BX0, 0, BX1, LV_STRIP, fill=MAG_F, stroke=MAG, lw=0.8)           # κανάλι γωνίας (πίσω, στη ΒΑ γωνία)
    sv.pipe([(KX + 0.014, LV_STRIP), (KX + 0.014, 0.0)], MAG, 1.6, dash=[3, 2], halo=False)
    sv.pipe([(CX, LV_STRIP), (CX, 0.0)], ORANGE, 1.4, dash=[3, 2], halo=False)
    # ---- φέρων οργανισμός
    sv.concrete([(X0, SOF8), (d91[2], SOF8), (d91[2], b_sof), (d91[4], b_sof), (d91[4], SOF6), (X1, SOF6), (X1, TOP), (X0, TOP)])
    sv.concrete([(X0, -FILL), (X1, -FILL), (X1, -FILL - 0.15), (d91[4], -FILL - 0.15), (d91[4], ZB), (d91[2], ZB), (d91[2], -FILL - 0.20), (X0, -FILL - 0.20)])
    sv.fill_r(X0, T6A1[0])
    sv.fill_r(T6A1[2], X1)
    cross_mark(sv, KX + 0.014, Z_REF, MAG, 4.5); cross_mark(sv, CX, Z_C_START + R_CON, ORANGE, 4.5)
    # τοίχος εισόδου Τ6Α
    sv.gyp_r(T6A1[0], -FILL, T6A1[2], b_sof, lw=0.8)
    sv.line(T6A1[0] + 0.025, -FILL, T6A1[0] + 0.025, b_sof, color=GYP_S, lw=0.35); sv.line(T6A1[2] - 0.025, -FILL, T6A1[2] - 0.025, b_sof, color=GYP_S, lw=0.35)
    # οροφές: καθιστικό · μετώπη · λωρίδα (με το slot) · ψευδοδοκός + οροφή κλιμακοστασίου
    sx0, sx1 = SLOT[0]["rect"][0], SLOT[0]["rect"][2]
    sv.board(X0, STRIP_X, LV_LIV)
    sv.rect(STRIP_X - 0.0125, LV_STRIP, STRIP_X, LV_LIV + 0.0125, fill=WHITE, stroke=DARK, lw=0.7)
    sv.board(STRIP_X, sx0, LV_STRIP); sv.board(sx1, RET[0], LV_STRIP)
    sv.rect(RET[0], LV_STRIP - 0.004, RET[2], LV_STRIP + 0.0165, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.9)
    k = RET[0] + 0.03
    while k < RET[2] - 0.01:
        sv.line(k, LV_STRIP - 0.004, k + 0.015, LV_STRIP + 0.0165, color=GREEN, lw=0.45); k += 0.035
    sv.board(RET[2], T6A1[0], LV_STRIP)
    sv.board(T6A1[2], 9.95, LV_PSB)
    sv.rect(9.95 - 0.0125, LV_PSB, 9.95, LV_STAIR + 0.0125, fill=WHITE, stroke=DARK, lw=0.7)
    sv.board(9.95, X1, LV_STAIR)
    # plenum + slot + μονάδα
    pz0, pz1 = LV_STRIP + 0.07, LV_STRIP + 0.27
    sv.rect(PLEN[0], pz0, PLEN[2], pz1, fill=BLUE_F, stroke=BLUE, lw=0.8)
    sv.rect(sx0, LV_STRIP - 0.003, sx1, pz0, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.7)
    sv.rect(PLEN[2], U_BOT + 0.03, UX0, U_TOP - 0.03, fill=BLUE_F, stroke=BLUE, lw=0.6)
    sv.rect(UX0, U_BOT, UX1, U_TOP, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.3)
    sv.text((UX0 + UX1) / 2 - 0.06, (U_BOT + U_TOP) / 2 + 0.03, "ΚΜ1", size=13, font="Inter-Bold", color=BLUE)
    sv.text((UX0 + UX1) / 2 - 0.06, (U_BOT + U_TOP) / 2 - 0.045, "το μηχάνημα (ύψος ως %s cm)" % cm(UNIT["hmax"]), size=6.0, color=BLUE)
    for xx in (UX0 + 0.08, UX1 - 0.08):
        sv.line(xx, U_TOP, xx, SOF8, color=DARK, lw=0.9)
    sv.text((PLEN[0] + PLEN[2]) / 2, (pz0 + pz1) / 2, "plenum", size=5.6, color=BLUE, font="Inter-SemiBold")
    sv.text((PLEN[0] + PLEN[2]) / 2, pz1 + 0.04, "κενό %s cm" % cm(SOF8 - LV_STRIP), size=5.8, color=DIMC, font="Inter-SemiBold")
    # ροές αέρα
    for dz in (0.0, 0.05):
        sv.arrow(sx0 - 0.01, LV_STRIP - 0.03 - dz, sx0 - 0.42, LV_STRIP - 0.09 - dz * 1.5, color=BLUE, lw=1.0)
    sv.text(sx0 - 0.25, LV_STRIP - 0.215, "κρύος αέρας προς το καθιστικό", size=6.0, color=BLUE, anchor="c")
    sv.arrow((RET[0] + RET[2]) / 2, LV_STRIP - 0.17, (RET[0] + RET[2]) / 2, LV_STRIP - 0.02, color=GREEN, lw=1.0)
    sv.text((RET[0] + RET[2]) / 2, LV_STRIP - 0.20, "επιστροφή αέρα", size=5.8, color=GREEN)
    # σωλήνες βόρεια της μονάδας (πίσω από την τομή) – σε πραγματική διάμετρο, μέσα στα 10 cm ως τον τοίχο
    gx_ = (UX1 + T6A1[0]) / 2 + 0.004
    sv.circle(gx_, Z_R_VOID, R_GAS, fill=MAG_F, stroke=MAG, lw=1.3)
    sv.circle(gx_, Z_R_VOID + R_GAS + R_LIQ + 0.006, R_LIQ, fill=MAG_F, stroke=MAG, lw=1.2)
    sv.circle(CX, Z_C_VOID_END + 0.004, A.COND_PIPE["od"] / 2, stroke=ORANGE, lw=1.3, dash=[2.5, 1.5])
    # καλώδια στον ψευδοδοκό του κλιμακοστασίου
    for dx in (0.0, 0.05, 0.10):
        sv.circle(9.75 + dx, LV_PSB + 0.0125 + 0.016, 0.016, fill=CABLE, stroke=CABLE)
    # ---- κείμενα
    sv.text(8.04, 1.82, "ΚΑΘΙΣΤΙΚΟ", size=12, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(9.90, 0.16, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=8, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(8.40, 0.16, "ΚΑΘΙΣΤΙΚΟ", size=8, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text((T6A1[0] + T6A1[2]) / 2, 2.02, "ΤΟΙΧΟΣ ΕΙΣΟΔΟΥ (γυψοσανίδα 15 cm)", size=5.8, color=GYP_S, font="Inter-SemiBold", rot=90)
    sv.text((d91[2] + d91[4]) / 2, 2.82, "ΔΟΚΑΡΙ", size=6.6, font="Inter-Bold", color=WHITE)
    sv.text((d91[2] + d91[4]) / 2, 2.73, "Δ9.1", size=8.5, font="Inter-Bold", color=WHITE)
    sv.text((d91[2] + d91[4]) / 2, 2.65, "30/50", size=6.2, font="Inter-SemiBold", color=WHITE)
    sv.text(8.25, 2.885, "ΠΛΑΚΑ Π8 (πάχος 20)", size=6.4, font="Inter-SemiBold", color=WHITE)
    sv.leader((BX0, 1.80), (9.02, 1.80), ["ΚΑΝΑΛΙ ΓΩΝΙΑΣ ΚΓ (πίσω, στη γωνία)", "οι σωλήνες κατεβαίνουν στο δάπεδο"], anchor="r", size=6.2, color=MAG, dot=False)
    sv.leader((gx_ - R_GAS, Z_R_VOID + 0.03), (9.26, TOP + 0.075), ["ψυκτικά: στα 10 cm ανάμεσα στο μηχάνημα και τον τοίχο (πάνε βόρεια, προς το κανάλι)"], anchor="r", size=5.8, color=MAG)
    sv.leader((CX - 0.03, Z_C_VOID_END - 0.012), (8.90, 2.275), ["συμπυκνώματα Ø 32 (πίσω από την τομή, προς το κανάλι)"], anchor="r", size=5.8, color=ORANGE)
    sv.leader((9.80, LV_PSB + 0.035), (9.98, 2.26), ["καλώδια του shaft", "(ψευδοδοκός)"], anchor="c", size=5.6, color=CABLE)
    sv.leader(((sx0 + sx1) / 2, LV_STRIP + 0.035), (8.20, 2.57), ["slot"], anchor="r", size=5.8, color=BLUE)
    sv.leader((gx_ - 0.05, -0.03), (8.92, 0.245), ["μπαίνουν στο γέμισμα και φεύγουν προς το Υπν.2 (βόρεια, πίσω από την τομή)"], anchor="r", size=5.8, color=MAG)
    sv.text(8.42, -FILL / 2, "στο δάπεδο του καθιστικού δεν περνά σωλήνας", size=5.8, color=FILL_H, font="Inter-SemiBold", bg=True)
    # ---- στάθμες
    sv.level(X1, TOP, right=True, lead=8)
    sv.level(X1, LV_STAIR, right=True, lead=8, note="οροφή κλιμακοστασίου")
    sv.level(X1, b_sof, right=True, lead=8, note="κάτω από το δοκάρι")
    sv.line(d91[4], b_sof, X1, b_sof, color=DARK, lw=0.4, dash=[2, 1.5])
    sv.level(X1, 0.0, right=True, lead=8, note="δάπεδο")
    sv.level(X1, -FILL, right=True, lead=8, note="πλάκα")
    sv.level(7.86, LV_LIV, right=True, below=True, note="οροφή καθιστικού")
    sv.level(8.62, LV_STRIP, right=True, below=True, note="οροφή λωρίδας")
    # ---- διαστάσεις
    sv.dim_h(2.13, [STRIP_X, UX0, UX1, T6A1[0]], above=True, size=6.2)
    sv.dim_h(2.03, [STRIP_X, T6A1[0]], above=False, size=6.4, fmt=lambda v_: "ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ %s" % mm2(v_))
    sv.break_band(X0, X1)
    sv.cut_mark(X0, ZB, TOP); sv.cut_mark(X1, ZB, TOP)
    # ---- μήνυμα
    X, Y = sv.p(9.60, 2.08)
    msg_box(c, X, Y, 150, "ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ:", ["κανένας σωλήνας του κλιματιστικού.", "Μόνο τα καλώδια του shaft, πάνω από", "την πόρτα εισόδου (όπως ήταν)."], size=6.0)
    arrow(c, X + 8, Y, sv.p(9.585, 0)[0], sv.p(0, LV_PSB + 0.03)[1], color=RED, lw=0.9)
    # ---- δεξιά στήλη
    x, w = 852, 308
    big_title(c, 44, 806, "ΤΟΜΗ Β-Β · μέσα από το μηχάνημα", "κοιτάμε προς βορρά · αριστερά το καθιστικό, δεξιά το κλιμακοστάσιο")
    y = head(c, x, 800, "ΤΙ ΔΕΙΧΝΕΙ Η ΤΟΜΗ")
    y = bullets(c, x, y, w, [
        "Η λωρίδα της εισόδου: χαμηλή οροφή %s, πλάτος 1,10 από τον τοίχο της εισόδου. Κενό %s cm ανάμεσα στην οροφή και την πλάκα." % (lv(LV_STRIP), cm(SOF8 - LV_STRIP)),
        "Μέσα στο κενό: slot και plenum (0,30) · το μηχάνημα ΚΜ1 (0,70) · 10 cm ως τον τοίχο. Το μηχάνημα κρέμεται από την πλάκα.",
        "Ο αέρας βγαίνει από το slot προς το καθιστικό και γυρνά από το στόμιο επιστροφής κάτω από το μηχάνημα.",
        "Το δοκάρι Δ9.1 είναι πάνω από τον τοίχο της εισόδου. Οι σωλήνες του κλιματιστικού ΔΕΝ περνούν από κάτω του: μένουν μέσα στο σαλόνι, πάνε προς "
        "βορρά δίπλα στον τοίχο και κατεβαίνουν στο κανάλι της γωνίας.",
        "Η κουζίνα (πίσω από εμάς) έχει την ίδια οροφή %s με τη λωρίδα – ενιαία, χωρίς δόντι. Τα 5 cm από το δοκάρι ως την οροφή είναι μόνο για τα "
        "καλώδια του shaft πάνω από την πόρτα εισόδου." % lv(LV_STRIP)])
    y = head(c, x, y - 6, "ΤΟ ΜΗΧΑΝΗΜΑ")
    y = bullets(c, x, y, w, [
        "Καναλάτη 24.000 Btu/h τύπου slim: ύψος ως %s cm (περιθώριο %s cm), βάθος ως 70 cm." % (cm(UNIT["hmax"]), cm(SOF8 - LV_STRIP - UNIT["hmax"] - A.HANG - A.SYSTEM)),
        "Συνδέσεις ψυκτικών, έξοδος συμπυκνωμάτων και ηλεκτρικό κουτί στο ΒΟΡΕΙΟ άκρο (προς το κανάλι). Εκεί και η θυρίδα επίσκεψης 60×60.",
        "Έξοδος συμπυκνωμάτων του μηχανήματος τουλάχιστον στο %s, για να κυλάνε μόνα τους ως το κανάλι (χωρίς αντλία)." % A.COND_OUT_TXT])
    legend(c, x, y - 8, [("box", ((0.80, 0.88, 0.97), BLUE), "μηχάνημα ΚΜ1 · plenum · slot"), ("box", ((0.86, 0.95, 0.91), GREEN), "στόμιο επιστροφής με φίλτρο")] + LEG_PIPES[:2] + LEG_PIPES[4:], w=w)
    frame(c, "ΚΜ-03", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Β-Β", "Εγκάρσια στη λωρίδα της εισόδου, μέσα από το μηχάνημα", "Κλίμακα 1:10 · A3")


# ================================================================ ΚΜ-04 τομή Γ-Γ (έξοδος στον ΒΑ εξώστη, κοιτάμε βόρεια)
def sheet_gg(c):
    S = scale(10)
    X0, X1 = 8.95, 11.52
    ZB = -0.36
    sv = Sec(c, 96, 206, S, u0=X0, brk=(1.05, 2.20, 16))
    d95 = BEAM["Δ9.5"]
    b_sof = A.beam_soffit(d95[1])
    in_face = T306[0]                                # εσωτερική παρειά (επένδυση) 9,395
    br0, br1 = T105[0], T105[2]                      # τούβλο 9,449–9,699
    et1 = BALC[0]                                    # εξωτερική παρειά θερμοπρόσοψης 9,80
    # ---- φόντο: βόρειο στηθαίο του εξώστη (πίσω) · υδρορροή ΥΔ1 (πίσω από τις πλάκες των εξωστών, μέσα στη θερμοπρόσοψη)
    sv.rect(et1, BALC_Z, PAR_E[0], 0.68, fill=CONC_L, stroke=(0.72, 0.72, 0.75), lw=0.4)
    sv.text(10.07, 0.60, "στηθαίο (πίσω)", size=5.2, color=GREY)
    # ---- φέρων οργανισμός
    sv.concrete([(X0, SOF3), (d95[2], SOF3), (d95[2], b_sof), (d95[4], b_sof), (d95[4], SOF3), (BALC[2], SOF3), (BALC[2], TOP), (X0, TOP)])
    sv.concrete([(X0, -FILL), (BALC[2], -FILL), (BALC[2], -FILL - 0.18), (d95[4], -FILL - 0.18), (d95[4], ZB), (d95[2], ZB), (d95[2], -FILL - 0.18), (X0, -FILL - 0.18)])
    sv.concrete_r(PAR_E[0], -FILL, PAR_E[2], 0.68)
    sv.rect(PAR_E[0] + 0.08, 0.68, PAR_E[0] + 0.10, 1.05, fill=(0.80, 0.90, 0.96), stroke=(0.45, 0.60, 0.72), lw=0.4)
    sv.etics_r(br1, BALC_Z, et1, SOF3)               # θερμοπρόσοψη (συνεχής στην όψη)
    sv.brick_r(br0, -FILL, br1, b_sof)               # τούβλο πεσσού
    sv.gyp_r(in_face, -FILL, br0, b_sof)             # επένδυση
    sv.fill_r(X0, in_face)
    sv.rect(et1, -FILL, PAR_E[0], BALC_Z, fill=(0.90, 0.90, 0.86)); sv.dots(et1, -FILL, PAR_E[0], BALC_Z, color=(0.62, 0.62, 0.58))
    sv.line(et1, BALC_Z, PAR_E[0], BALC_Z, color=DARK, lw=0.9)
    sv.rect(br1, -FILL, et1, BALC_Z, fill=(0.90, 0.90, 0.86))
    # ντουλάπα Υπν.2 (τομή)
    sv.rect(X0, 0, in_face, LV_BED, fill=WOOD, stroke=WOOD_S, lw=0.9)
    for zz in (0.08, 0.62, 2.32):
        sv.line(X0, zz, in_face - 0.02, zz, color=WOOD_S, lw=0.35)
    sv.rect(X0, LV_BED, in_face, SOF3, fill=WOOD, stroke=WOOD_S, lw=0.5)
    sv.text(9.17, 2.56, "ΝΤΟΥΛΑΠΑ ΥΠΝ.2", size=7, font="Inter-Bold", color=WOOD_S)
    sv.text(9.17, 2.49, "(μέσα της οι σωλήνες)", size=5.4, color=WOOD_S)
    # εξωτερική μονάδα
    sv.rect(EM[0], 0.06, EM[2], 0.76, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=1.2)
    sv.circle(EM[2] - 0.34, 0.41, 0.26, stroke=BLUE, lw=0.7)
    sv.circle(EM[2] - 0.34, 0.41, 0.04, fill=BLUE)
    sv.rect(EM[0] + 0.05, BALC_Z, EM[0] + 0.13, 0.06, fill=DARK); sv.rect(EM[2] - 0.13, BALC_Z, EM[2] - 0.05, 0.06, fill=DARK)
    sv.text((EM[0] + EM[2]) / 2, 0.90, "ΕΞΩΤΕΡΙΚΗ ΜΟΝΑΔΑ", size=8, font="Inter-Bold", color=BLUE)
    sv.text((EM[0] + EM[2]) / 2, 0.82, "(θέση ενδεικτική – κατά τη μελέτη ψύξης)", size=5.6, color=BLUE)
    # ---- υδρορροή ΥΔ1 (μέσα στη θερμοπρόσοψη, ανάμεσα στις πλάκες) + σιφώνι εξώστη με τον Φ50
    sv.rect(YD1[0] - 0.0375, -FILL - 0.02, YD1[0] + 0.0375, SOF3, fill=(0.80, 0.90, 0.99), stroke=RAIN, lw=1.0)
    gx = GULLY[0][0]
    sv.poly([(gx - 0.07, BALC_Z), (gx + 0.07, BALC_Z), (gx + 0.035, BALC_Z - 0.045), (gx - 0.035, BALC_Z - 0.045)], fill=WHITE, stroke=RAIN, lw=0.9)
    sv.pipe([(gx, BALC_Z - 0.045), (gx, -FILL + 0.027), (YD1[0] + 0.0375, -FILL + 0.027)], RAIN, 3.0)
    # ---- σωλήνες
    zs = EXIT_Z + 0.07                                # ψυκτικά split, λίγο πάνω από της ΚΜ1
    xs = in_face - 0.035
    sv.pipe([(xs, SOF3 - 0.03), (xs, zs), (EM[0], zs)], BLUE2, 1.8, dash=[5, 2.5])
    sv.pipe([(CX, Z_C_TURN + R_CON), (YD1[0] - 0.0375, Z_C_END + R_CON)], ORANGE, 2.6)
    sv.pipe([(KX, Z_REF), (br0 - 0.03, Z_REF + 0.012), (br0 + 0.03, Z_REF + 0.07), (br0 + 0.03, EXIT_Z), (EM[0], EXIT_Z)], MAG, 3.0)
    sv.circle(KX, Z_REF, R_GAS, fill=MAG_F, stroke=MAG, lw=1.3)
    sv.circle(CX, Z_C_TURN + R_CON, R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.3)
    # ---- κείμενα
    sv.text((d95[2] + d95[4]) / 2, 2.82, "ΔΟΚΑΡΙ", size=6.6, font="Inter-Bold", color=WHITE)
    sv.text((d95[2] + d95[4]) / 2, 2.73, "Δ9.5", size=8.5, font="Inter-Bold", color=WHITE)
    sv.text((d95[2] + d95[4]) / 2, 2.65, "30/55", size=6.2, font="Inter-SemiBold", color=WHITE)
    sv.text((br0 + br1) / 2, 0.66, "ΠΕΣΣΟΣ Τ1-05 (τούβλο 25 cm)", size=6.4, font="Inter-Bold", color=WHITE, rot=90)
    sv.text(10.80, 2.66, "ΒΑ ΕΞΩΣΤΗΣ", size=12, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text((br1 + et1) / 2, 0.74, "θερμοπρόσοψη", size=5.0, color=ETICS_S, rot=90)
    sv.leader((YD1[0] + 0.04, 0.985), (9.90, 0.985), ["ΥΔ1 υδρορροή (μέσα στη θερμοπρόσοψη)"], anchor="l", size=6.0, color=RAIN)
    sv.leader((gx + 0.03, BALC_Z - 0.03), (10.22, -0.215), ["σιφώνι εξώστη → σωλήνας Φ50 → υδρορροή ΥΔ1"], anchor="l", size=6.0, color=RAIN)
    sv.leader((9.58, Z_C_END + R_CON + 0.002), (9.40, -0.235), ["ΣΥΜΠΥΚΝΩΜΑΤΑ Ø 32: από τη βάση του τοίχου", "στον Φ50 του σιφωνιού → υδρορροή"], anchor="r", size=6.0, color=ORANGE)
    sv.leader((br0 + 0.03, 0.12), (9.34, 0.50), ["ΨΥΚΤΙΚΑ ΚΜ1: αυλάκι στο", "τούβλο ως %s και έξω" % lv(EXIT_Z)], anchor="r", size=6.0, color=MAG)
    sv.leader((10.08, EXIT_Z), (9.90, 0.52), ["ψυκτικά → εξωτερική μονάδα"], anchor="l", size=5.8, color=MAG, dot=False)
    sv.leader((xs, 0.82), (9.32, 0.88), ["ψυκτικά split ΚΜ2 / ΚΜ3:", "κατεβαίνουν ΜΕΣΑ στη", "ντουλάπα, βγαίνουν χαμηλά"], anchor="r", size=5.8, color=BLUE2)
    sv.leader((CX - R_CON, Z_C_TURN + R_CON), (8.98, 0.20), ["οι σωλήνες της ΚΜ1 έρχονται", "μέσα στο γέμισμα, κολλητά", "στον τοίχο"], anchor="l", size=5.6, color=DARK)
    # ---- στάθμες
    sv.level(X0, TOP, right=False, lead=8)
    sv.level(X0, LV_BED, right=False, lead=8, note="οροφή Υπν.2")
    sv.level(X0, 0.0, right=False, lead=8, note="δάπεδο")
    sv.level(X0, -FILL, right=False, lead=8, note="πλάκα")
    sv.level(X1, BALC_Z, right=True, lead=8, note="δάπεδο εξώστη")
    sv.level(9.93, b_sof, right=True, lead=8, note="κάτω από το δοκάρι Δ9.5")
    sv.line(d95[4], b_sof, 9.93, b_sof, color=DARK, lw=0.4, dash=[2, 1.5])
    sv.level(10.12, EXIT_Z, txt=lv(EXIT_Z), right=True, lead=6, color=MAG)
    # βήματα
    sv.badge(KX - 0.02, Z_REF + 0.085, 5)
    sv.badge(br0 + 0.13, 0.36, 6)
    sv.badge(EM[0] - 0.13, 0.70, 7)
    sv.break_band(X0, X1)
    sv.cut_mark(X0, ZB, TOP)
    # ---- μήνυμα
    X, Y = sv.p(10.50, 2.52)
    h = msg_box(c, X, Y, 172, "ΨΗΛΑ, ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ: ΤΙΠΟΤΑ", ["Όλοι οι σωλήνες βγαίνουν ΧΑΜΗΛΑ από το τούβλο,", "πίσω από την εξωτερική μονάδα."], size=6.0)
    arrow(c, X, Y - h + 5, sv.p(9.66, 0)[0], sv.p(0, b_sof - 0.07)[1], color=RED, lw=0.9)
    # ---- δεξιά στήλη
    x, w = 858, 302
    big_title(c, 44, 806, "ΤΟΜΗ Γ-Γ · έξοδος στον ΒΑ εξώστη", "κοιτάμε προς βορρά · αριστερά η ντουλάπα του Υπν.2, δεξιά ο εξώστης")
    y = steps_panel(c, x, 800, w, only=(5, 6, 7), title="ΤΑ ΤΕΛΕΥΤΑΙΑ ΒΗΜΑΤΑ", size=7.0)
    y = head(c, x, y - 6, "ΠΡΟΣΟΧΗ ΣΤΗΝ ΚΑΤΑΣΚΕΥΗ")
    y = bullets(c, x, y, w, [
        "Στο χτίσιμο του πεσσού Τ1-05 αφήνεται κενό στην πρώτη σειρά (για τα συμπυκνώματα) και αυλάκι 12 × 6 cm ως τα 30 cm (για τα ψυκτικά). "
        "Η έξοδος σφραγίζεται και στεγανώνεται πριν από τη θερμοπρόσοψη.",
        "Ψυκτικά μέσα στο δάπεδο: προμονωμένος χαλκός ΧΩΡΙΣ ενώσεις, μέσα σε σπιράλ. Δοκιμή με άζωτο ΠΡΙΝ πέσει το γέμισμα.",
        "Συμπυκνώματα Ø 32 κολλητό PVC με κλίση 1 % σε όλο το μήκος: δοκιμή με νερό πριν από το γέμισμα. Συμβολή 45° στον Φ50 του σιφωνιού του εξώστη.",
        "Η θέση και ο τύπος της εξωτερικής μονάδας ορίζονται από τη μελέτη ψύξης – η έξοδος των σωλήνων μετακινείται ανάλογα πάνω στον ίδιο πεσσό."], size=7.0)
    legend(c, x, y - 8, LEG_PIPES[:4] + LEG_PIPES[5:], w=w)
    frame(c, "ΚΜ-04", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Γ-Γ", "Έξοδος των σωλήνων στον ΒΑ εξώστη, χαμηλά από τον πεσσό", "Κλίμακα 1:10 · A3")


# ================================================================ ΚΜ-05 λεπτομέρειες 1:5
def sheet_det(c):
    S = scale(5)
    # ---------------- (α) κάτοψη καναλιού γωνίας
    x0, y0, x1, y1 = 8.90, 5.02, 9.72, 5.52
    ox, oyt = 40, 768                                 # πάνω-αριστερά γωνία του παραθύρου σε pt
    v = View(c, ox - x0 * S, PAGE_H - oyt - y0 * S, S)
    X0, Y0 = v.p(x0, y1); X1, Y1 = v.p(x1, y0)
    c.saveState()
    pth = c.beginPath(); pth.rect(X0, Y0, X1 - X0, Y1 - Y0); c.clipPath(pth, stroke=0, fill=0)
    c.setFillColorRGB(1, 1, 1); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=0, fill=1)
    v.rect(x0, T206[3], T6A3[0], y1, fill=(0.975, 0.97, 0.96))                               # καθιστικό
    v.rect(x0, y0, T206[2], T206[1], fill=(0.975, 0.97, 0.96))                               # Υπν.2
    v.rect(T6A3[2], K3[3], x1, y1, fill=(0.955, 0.955, 0.955))                               # κλιμακοστάσιο
    v.rect(K3[0], y0, K3[2], K3[3], fill=CONC)                                               # κολόνα Κ3
    v.hatch([[K3[0], y0], [K3[2], y0], [K3[2], K3[3]], [K3[0], K3[3]]], 0.02, 45, CONC_H, 0.35)
    v.rect(K3[0], y0, K3[2], K3[3], stroke=DARK, lw=0.9)
    v.rect(K3[0] - 0.034, y0, K3[0], T206[1], fill=GYP, stroke=GYP_S, lw=0.5)                # Τ9-03 κολλητή γυψοσανίδα (Υπν.2)
    for (a, b) in ((T206[1], T206[1] + 0.025), (T206[3] - 0.025, T206[3])):                  # τοίχος Τ2-06: 2 + 2 γυψοσανίδες, CW 50
        v.rect(x0, a, T206[2], b, fill=GYP, stroke=GYP_S, lw=0.6)
        v.line(x0, (a + b) / 2, T206[2], (a + b) / 2, color=GYP_S, lw=0.3)
    v.rect(x0, T206[1] + 0.025, T206[2], T206[3] - 0.025, fill=(0.97, 0.97, 0.93))
    for xs in (9.00, 9.355):
        v.rect(xs, T206[1] + 0.025, xs + 0.006, T206[3] - 0.025, fill=(0.55, 0.60, 0.68))
        v.rect(xs, T206[1] + 0.025, xs + 0.04, T206[1] + 0.031, fill=(0.55, 0.60, 0.68)); v.rect(xs, T206[3] - 0.031, xs + 0.04, T206[3] - 0.025, fill=(0.55, 0.60, 0.68))
    for (a, b) in ((T6A3[0], T6A3[0] + 0.025), (T6A3[2] - 0.025, T6A3[2])):                  # πεσσός Τ6Α-03: 2 + 2 πυράντοχες, CW 100
        v.rect(a, T6A3[1], b, DOOR[0], fill=(0.74, 0.86, 0.78), stroke=(0.25, 0.45, 0.35), lw=0.6)
    v.rect(T6A3[0] + 0.025, T6A3[1], T6A3[2] - 0.025, DOOR[0], fill=(0.98, 0.95, 0.80))
    v.hatch([[T6A3[0] + 0.025, T6A3[1]], [T6A3[2] - 0.025, T6A3[1]], [T6A3[2] - 0.025, DOOR[0]], [T6A3[0] + 0.025, DOOR[0]]], 0.012, 60, (0.80, 0.70, 0.35), 0.3)
    v.rect(T6A3[0] - 0.02, DOOR[0] - 0.02, T6A3[2] + 0.02, DOOR[0] + 0.045, fill=(0.80, 0.72, 0.60), stroke=WOOD_S, lw=0.7)      # κάσα
    v.rect(x0, DOOR[0], T6A3[0] - 0.02, DOOR[0] + 0.06, fill=(0.93, 0.89, 0.82), stroke=WOOD_S, lw=0.9)                          # φύλλο ανοιχτό 90°
    v.rect(BX0, BY0, BX1, BY1, fill=WHITE)                                                   # κανάλι γωνίας
    v.rect(BX0, BY1 - 0.0125, BX1, BY1, fill=MAG_F, stroke=MAG, lw=0.9)
    v.rect(BX0, BY0, BX0 + 0.0125, BY1, fill=MAG_F, stroke=MAG, lw=0.9)
    v.rect(BX0 + 0.0125, BY0, BX0 + 0.0185, BY1 - 0.0125, fill=(0.55, 0.60, 0.68))
    v.rect(BX0 + 0.0125, BY1 - 0.0185, BX1, BY1 - 0.0125, fill=(0.75, 0.78, 0.84))
    yc_ = BY0 + 0.028
    pg, pl, pc, pk = (KX + 0.016, yc_), (KX - 0.026, yc_ - 0.006), (CX, yc_ - 0.004), (BX0 + 0.043, yc_ - 0.008)
    v.circle(pg[0], pg[1], R_GAS, fill=MAG_F, stroke=MAG, lw=1.0); v.circle(pg[0], pg[1], 0.0159 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
    v.circle(pl[0], pl[1], R_LIQ, fill=MAG_F, stroke=MAG, lw=1.0); v.circle(pl[0], pl[1], 0.0095 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
    v.circle(pc[0], pc[1], R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.2)
    v.circle(pk[0], pk[1], 0.010, fill=(0.80, 0.92, 0.85), stroke=CABLE, lw=1.0)
    c.restoreState()
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    v.text(9.56, 5.08, "ΚΟΛΟΝΑ Κ3", size=8, font="Inter-Bold", color=WHITE)
    v.text(9.12, 5.10, "ΤΟΙΧΟΣ Τ2-06 (γυψοσανίδα 10 cm)", size=6.2, color=GYP_S, font="Inter-SemiBold", bg=True)
    v.text(8.92, 5.035, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=6.5, color=GREY, font="Inter-SemiBold", anchor="l")
    v.text(8.92, 5.20, "ΚΑΘΙΣΤΙΚΟ", size=6.5, color=GREY, font="Inter-SemiBold", anchor="l")
    v.text(9.635, 5.44, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=6.0, color=GREY, font="Inter-SemiBold")
    v.text(9.635, 5.225, "πεσσός", size=5.8, color=(0.25, 0.45, 0.35), font="Inter-SemiBold"); v.text(9.635, 5.245, "Τ6Α-03", size=5.8, color=(0.25, 0.45, 0.35))
    v.text(9.02, 5.33, "ΦΥΛΛΟ ΠΟΡΤΑΣ ΕΙΣΟΔΟΥ (ανοιχτό)", size=6.2, color=WOOD_S, font="Inter-SemiBold")
    v.text(9.475, 5.36, "κάσα", size=5.4, color=WOOD_S)
    for (pt_, rr, yy, txt, col) in ((pk, 0.010, 5.395, "καλώδιο εντολής", CABLE), (pc, R_CON, 5.425, "συμπυκνώματα PVC Ø 32", ORANGE),
                                    (pl, R_LIQ, 5.455, "υγρού 3/8″ με τη μόνωση (Ø %d)" % math.ceil(R_LIQ * 2000 - 1e-6), MAG),
                                    (pg, R_GAS, 5.485, "αερίου 5/8″ με μόνωση 13 mm (Ø %d)" % round(R_GAS * 2000), MAG)):
        Xa, Ya = v.p(pt_[0], pt_[1] + rr); Xb, Yb = v.p(pt_[0], yy)
        c.setStrokeColorRGB(*col); c.setLineWidth(0.5); c.line(Xa, Ya, Xb, Yb)
        w_ = pdfmetrics.stringWidth(txt, "Inter-SemiBold", 6.0)
        c.setFillColorRGB(1, 1, 1); c.rect(Xb - w_ - 4.5, Yb - 3.4, w_ + 3, 8.2, stroke=0, fill=1)
        c.setFont("Inter-SemiBold", 6.0); c.setFillColorRGB(*col); c.drawRightString(Xb - 3, Yb - 2.2, txt)
    vdim(v, "H", 5.2625, [BX0, BX1], size=6.4, side=1, fmt=lambda q: "%s cm" % cm(q))
    vdim(v, "V", 9.12, [BY0, BY1, DOOR[0]], size=6.0, side=-1)
    vdim(v, "V", 9.585, [T6A3[1], DOOR[0]], size=6.0, side=1)
    c.setFont("Inter-Bold", 10); c.setFillColorRGB(*DARK); c.drawString(40, 790, "α · ΚΑΝΑΛΙ ΓΩΝΙΑΣ ΚΓ – κάτοψη 1:5")
    c.setFont("Inter", 7); c.setFillColorRGB(*GREY)
    c.drawString(40, 779.5, "κουτί γυψοσανίδας %s στη ΒΑ γωνία του καθιστικού, πίσω από το φύλλο της πόρτας εισόδου (διαστάσεις σε cm)" % A.BOX["size"])
    # ---------------- (β) τομή δαπέδου Υπν.2 (Δ–Α, κοιτάμε βόρεια) στο y = 3,50
    yq = 3.50
    u0, u1 = 8.82, 9.72
    sv = Sec(c, 40, 306, S, u0=u0)
    zb = -0.30
    zc = cond_inv(BYC - yq)                          # ροή συμπυκνωμάτων σε αυτή τη θέση
    wall_face = K3[0] - 0.034
    sv.rect(u0, 0, wall_face, 0.24, fill=(0.975, 0.97, 0.96))
    sv.concrete_r(u0, zb, K3[0], -FILL)
    sv.concrete_r(K3[0], zb, u1, 0.24)
    sv.gyp_r(wall_face, -FILL, K3[0], 0.24)
    strip0 = wall_face - 0.20
    sv.rect(u0, -FILL, strip0, -FILL + 0.03, fill=(0.80, 0.88, 0.96), stroke=(0.45, 0.55, 0.70), lw=0.4)      # ενδοδαπέδια (ενδεικτικά)
    sv.rect(u0, -FILL + 0.03, strip0, -0.015, fill=FILLC); sv.dots(u0, -FILL + 0.03, strip0, -0.015, step=6)
    k = u0 + 0.06
    while k < strip0 - 0.04:
        sv.circle(k, -FILL + 0.03 + 0.012, 0.008, fill=(0.95, 0.60, 0.55), stroke=RED, lw=0.6); k += 0.15
    sv.rect(strip0, -FILL, wall_face, -0.015, fill=FILLC); sv.dots(strip0, -FILL, wall_face, -0.015, step=6)
    sv.rect(u0, -0.015, wall_face, 0.0, fill=(0.86, 0.72, 0.52), stroke=WOOD_S, lw=0.5)
    sv.line(u0, 0.0, wall_face, 0.0, color=DARK, lw=1.0)
    sv.line(strip0, -FILL, strip0, -0.015, color=RED, lw=0.5, dash=[3, 2])
    gx_, lx_ = KX + 0.016, KX - 0.026
    sv.circle(gx_, -FILL + R_GAS + 0.004, R_GAS + 0.004, stroke=(0.5, 0.5, 0.5), lw=0.5, dash=[1.5, 1.2])
    sv.circle(gx_, -FILL + R_GAS + 0.004, R_GAS, fill=MAG_F, stroke=MAG, lw=1.1); sv.circle(gx_, -FILL + R_GAS + 0.004, 0.0159 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
    sv.circle(lx_, -FILL + R_LIQ + 0.004, R_LIQ + 0.004, stroke=(0.5, 0.5, 0.5), lw=0.5, dash=[1.5, 1.2])
    sv.circle(lx_, -FILL + R_LIQ + 0.004, R_LIQ, fill=MAG_F, stroke=MAG, lw=1.1); sv.circle(lx_, -FILL + R_LIQ + 0.004, 0.0095 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
    sv.circle(CX, zc + R_CON, R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.3)
    sv.text(9.56, 0.03, "ΚΟΛΟΝΑ Κ3", size=8, font="Inter-Bold", color=WHITE)
    sv.text(9.05, -0.225, "ΠΛΑΚΑ", size=8, font="Inter-Bold", color=WHITE)
    sv.text(8.84, 0.205, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=7, font="Inter-Bold", color=GREY, anchor="l")
    sv.leader((8.94, -FILL + 0.045), (8.84, 0.045), ["ενδοδαπέδια (ενδεικτικά): μόνωση · σωλήνες · κονίαμα · ξύλο"], anchor="l", size=5.8, color=RED)
    sv.leader((gx_ - 0.006, -FILL + 2 * R_GAS + 0.004), (9.345, 0.155), ["ψυκτικά ΚΜ1 πάνω στην πλάκα, μέσα σε σπιράλ"], anchor="r", size=6.0, color=MAG)
    sv.leader((CX - 0.004, zc + 2 * R_CON), (9.225, 0.10), ["συμπυκνώματα Ø 32 (εδώ ροή %s)" % lv(zc, 3)], anchor="r", size=6.0, color=ORANGE)
    sv.dim_h(-FILL, [strip0, wall_face], dy=-58, above=False, fmt=lambda v_: "λωρίδα %s cm χωρίς ενδοδαπέδια" % cm(v_), size=6.2)
    sv.dim_v(u0 + 0.045, [-FILL, 0.0], left=True, fmt=lambda v_: "γέμισμα %s cm" % cm(v_), size=6.0)
    sv.level(u0 + 0.30, 0.0, right=True, lead=8)
    c.setFont("Inter-Bold", 10); c.setFillColorRGB(*DARK); c.drawString(40, 468, "β · ΟΙ ΣΩΛΗΝΕΣ ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ ΤΟΥ ΥΠΝ.2 – τομή 1:5")
    c.setFont("Inter", 7); c.setFillColorRGB(*GREY)
    c.drawString(40, 457.5, "εγκάρσια στον ανατολικό τοίχο, κοιτάμε προς βορρά · οι τρεις σωλήνες μέσα στο γέμισμα των 12 cm, σε λωρίδα 20 cm κολλητά στον τοίχο")
    # ---------------- δεξιά στήλη
    x, w = 640, 520
    y = head(c, x, 790, "ΚΑΝΑΛΙ ΓΩΝΙΑΣ – ΤΙ ΕΙΝΑΙ")
    y = bullets(c, x, y, w, [
        "Ένα κουτί γυψοσανίδας %s (σκελετός 50 + γυψοσανίδα), κολλητά στον βόρειο τοίχο του καθιστικού, στη γωνία με τον τοίχο της εισόδου." % A.BOX["size"],
        "Πηγαίνει από το δάπεδο ως την ψευδοροφή της λωρίδας και είναι ανοιχτό επάνω, μέσα στο κενό – εκεί μπαίνουν οι σωλήνες από το μηχάνημα.",
        "Είναι πίσω από το φύλλο της πόρτας εισόδου όταν ανοίγει: μένουν %s cm ως το φύλλο και ως το άνοιγμα της πόρτας – δεν εμποδίζει ούτε την κάσα "
        "ούτε το άνοιγμα." % cm(DOOR[0] - BY1),
        "Αν μπει έπιπλο / ντουλάπα εισόδου σε αυτόν τον τοίχο, το κατέβασμα κρύβεται μέσα του και το κουτί δεν χρειάζεται.",
        "Αν το εγκρίνεις, μπαίνει στα σχέδια τοιχοποιιών (Α΄ · Β΄ · Γ΄ και Δ΄)."], size=7.4)
    y = head(c, x, y - 8, "ΔΑΠΕΔΟ ΥΠΝ.2 – ΤΙ ΠΡΟΣΕΧΟΥΜΕ")
    y = bullets(c, x, y, w, [
        "Οι σωλήνες στρώνονται πάνω στην πλάκα ΠΡΙΝ από το γέμισμα και πριν από τα ενδοδαπέδια, κολλητά στον ανατολικό τοίχο.",
        "Σε αυτή τη λωρίδα των 20 cm δεν μπαίνει σωλήνας ενδοδαπέδιας (η μονωτική πλάκα κόβεται εκεί).",
        "Συμπυκνώματα: ξεκινούν με τη ράχη %s cm κάτω από το τελικό δάπεδο και κατεβαίνουν 1 cm ανά μέτρο· στο τέλος μένει %s cm πάνω από την πλάκα – "
        "χωράει, αλλά χωρίς περιθώριο για λάθος κλίση." % (cm(COVER), cm(FILL + Z_C_END)),
        "Κάτω από τη βάση του γυψότοιχου Τ2-06 κόβεται τοπικά ο κάτω στρωτήρας για να περάσουν.",
        "Φωτογραφία και δοκιμές (άζωτο στα ψυκτικά, νερό στα συμπυκνώματα) πριν σκεπαστούν."], size=7.4)
    legend(c, x, y - 8, [("box", (MAG_F, MAG), "ψυκτικός σωλήνας με τη μόνωσή του (μέσα ο χαλκός)"), ("box", (ORANGE_F, ORANGE), "συμπυκνώματα PVC Ø 32"),
                         ("box", (GYP, GYP_S), "γυψοσανίδα"), ("hatch", (CONC, DARK), "σκυρόδεμα"), ("box", (FILLC, FILL_H), "γέμισμα δαπέδου")], w=w)
    frame(c, "ΚΜ-05", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΛΕΠΤΟΜΕΡΕΙΕΣ", "Κανάλι γωνίας (κάτοψη) · σωλήνες μέσα στο γέμισμα δαπέδου (τομή)", "Κλίμακα 1:5 · A3")


# ================================================================ ΚΜ-06 ισόγειο – κάτοψη διαδρομής
def sheet_gf(c):
    s = scale(40)
    clip = (3.95, -0.05, 11.95, 9.62)
    ox = 34 - clip[0] * s
    oy = PAGE_H - 815 - clip[1] * s
    v = plan_bg(c, G, ox, oy, s, clip)
    beams_plan(v, G, ("Δ3.1", "Δ9.1", "Δ4.4", "Δ9.5", "Δ1.4"),
               {"Δ3.1": (5.60, 5.00, 0), "Δ9.1": (9.55, 7.80, 90), "Δ4.4": (6.60, 9.30, 0), "Δ9.5": (9.55, 2.62, 90), "Δ1.4": (7.90, 0.65, 0)})
    ac_unit_plan(v, G)
    em = G.OUTDOOR_T
    c.setDash([3, 1.5]); v.rect(*em, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=0.8); c.setDash([])
    vpipe(v, G.SPLIT_ROUTE, BLUE2, 1.1, dash=[4, 2], halo=False)
    vpipe(v, G.COND_ROUTE, ORANGE, 1.9)
    vpipe(v, G.KM1_VOID, MAG, 2.2)
    vpipe(v, G.KM1_FLOOR, MAG, 2.4, dash=[1.4, 1.9])
    u = G.UNITS[0]["rect"]
    v.text((u[0] + u[2]) / 2, (u[1] + u[3]) / 2 + 0.25, "ΚΜ1", size=8, font="Inter-Bold", color=BLUE, bg=True)
    v.text(4.60, 7.20, "ΚΑΘΙΣΤΙΚΟ", size=9, font="Inter-Bold", color=GREY)
    v.text(8.30, 7.60, "ΚΟΥΖΙΝΑ", size=8, font="Inter-Bold", color=GREY)
    v.text(8.30, 7.80, "χαμηλή οροφή %s" % G.fmt(2.65), size=5.6, color=GREY)
    v.text(7.85, 2.40, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=9, font="Inter-Bold", color=GREY)
    v.text(8.70, 5.20, "WC", size=7.5, font="Inter-Bold", color=GREY)
    v.text(10.62, 2.25, "ΒΑ ΒΕΡΑΝΤΑ", size=7.5, font="Inter-Bold", color=GREY)
    v.text((em[0] + em[2]) / 2, (em[1] + em[3]) / 2, "εξωτ. μονάδα", size=5.4, color=BLUE, font="Inter-SemiBold")
    v.text((em[0] + em[2]) / 2, em[3] + 0.12, "(θέση ενδεικτική)", size=4.8, color=BLUE, bg=True)
    v.text(10.75, 6.55, "ΧΩΛ ΚΤΙΡΙΟΥ", size=7.5, font="Inter-Bold", color=GREY)
    x1d, y1d = G.KM1_VOID[-1]
    vlabel(v, 10.00, 5.62, ["ΚΑΤΕΒΑΣΜΑ ΜΕΣΑ ΣΤΟΝ ΓΥΨΟΤΟΙΧΟ", "του WC (Τ2-06) – όχι κάτω από δοκάρι"], color=MAG, to=(x1d + 0.04, y1d), size=6.0)
    vlabel(v, 8.45, 3.40, ["ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ (γέμισμα)", "λωρίδα 25 cm στον τοίχο,", "χωρίς ενδοδαπέδια"], anchor="r", color=MAG, to=(9.27, 3.30), size=6.0)
    vlabel(v, 7.05, 5.82, ["συμπυκνώματα ΚΜ1 →", "μέσα στον Τ2-06 → σιφώνι WC"], anchor="r", color=ORANGE, to=(8.02, 5.60), size=5.6)
    vlabel(v, 6.35, 4.62, ["ψυκτικά split: ψευδοροφή →", "κατέβασμα μέσα στη ντουλάπα"], anchor="r", color=BLUE2, to=(7.20, 4.20), size=5.6)
    vbadge(v, (u[0] + u[2]) / 2, u[3] - 0.22, 1)
    vbadge(v, 7.615, 5.55, 2, dy=12)
    vbadge(v, x1d, y1d, 3, dx=-2, dy=-13)
    vbadge(v, 7.75, 5.32, 4, dx=13)
    vbadge(v, 8.55, 4.55, 5, dy=-11)
    vbadge(v, 9.30, 2.30, 5, dx=12)
    vbadge(v, 9.575, 1.20, 6, dy=-12)
    vbadge(v, 10.05, 1.75, 7)
    c.restoreState()
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    x, w = X1 + 24, 1160 - (X1 + 24)
    big_title(c, x, 800, "ΙΣΟΓΕΙΟ – ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1", "Ίδια αρχή με τους ορόφους: τίποτα κάτω από δοκάρι")
    y = 764
    gsteps = [
        ("ΤΟ ΜΗΧΑΝΗΜΑ ΜΕΝΕΙ ΠΑΝΩ ΑΠΟ ΤΗΝ ΚΟΥΖΙΝΑ", "ΚΜ1 στη χαμηλή οροφή της κουζίνας (%s), όπως ήταν. Συνδέσεις στο βόρειο άκρο, ανατολικό πλάι." % G.fmt(2.65)),
        ("0,6 m ΜΕΣΑ ΣΤΗΝ ΨΕΥΔΟΡΟΦΗ", "Τα ψυκτικά πάνε ως τον τοίχο του WC. Εκεί δεν υπάρχει δοκάρι."),
        ("ΚΑΤΕΒΑΣΜΑ ΜΕΣΑ ΣΤΟΝ ΓΥΨΟΤΟΙΧΟ ΤΟΥ WC", "Κατεβαίνουν μέσα στον τοίχο Τ2-06 (WC / κουζίνα) ως το δάπεδο – δεν χρειάζεται κουτί."),
        ("ΔΑΠΕΔΟ ΤΟΥ WC, ΚΑΤΩ ΑΠΟ ΤΟΝ ΤΟΙΧΟ", "Μέσα στο γέμισμα, δίπλα στην πόρτα του WC, και κάτω από τη βάση του τοίχου προς το Υπν.2 (το δοκάρι Δ3.1 είναι ψηλά)."),
        ("ΚΑΤΩ ΑΠΟ ΤΗ ΝΤΟΥΛΑΠΑ ΚΑΙ ΚΟΛΛΗΤΑ ΣΤΟΝ ΤΟΙΧΟ", "Κάτω από τη ντουλάπα του Υπν.2 και μετά κατά μήκος του ανατολικού τοίχου του (λωρίδα 25 cm χωρίς ενδοδαπέδια). "
         "Εκεί έρχονται και τα ψυκτικά των split, που κατεβαίνουν μέσα στη ντουλάπα."),
        ("ΠΕΣΣΟΣ ΔΙΠΛΑ ΣΤΗ ΜΠΑΛΚΟΝΟΠΟΡΤΑ – ΕΞΟΔΟΣ ΧΑΜΗΛΑ", "Αυλάκι στο τούβλο ως +0,25 και έξω."),
        ("ΒΑ ΒΕΡΑΝΤΑ", "Εξωτερική μονάδα. Τα συμπυκνώματα της ΚΜ1 στο ισόγειο πάνε στο σιφώνι του WC (όπως ήταν)."),
    ]
    y = head(c, x, y, "Η ΔΙΑΔΡΟΜΗ ΒΗΜΑ – ΒΗΜΑ")
    for i, (t, d) in enumerate(gsteps, 1):
        badge(c, x + 7, y + 2.5, i, 7.0)
        c.setFont("Inter-Bold", 7.2); c.setFillColorRGB(*DARK); c.drawString(x + 20, y, t)
        y -= 10.2
        y = para(c, x + 20, y, w - 22, d, size=6.8) - 3.5
    y = head(c, x, y - 6, "ΤΙ ΑΛΛΑΞΕ ΣΤΟ ΙΣΟΓΕΙΟ", 9.5)
    y = para(c, x, y, w, "Μόνο η διαδρομή των ψυκτικών: πριν περνούσαν κάτω από το δοκάρι Δ3.1 μέσα από τη ντουλάπα του καθιστικού. Το μηχάνημα, οι οροφές και τα "
             "συμπυκνώματα έμειναν όπως ήταν.", size=7.0)
    legend(c, x, y - 10, [("line", MAG, "ψυκτικά ΚΜ1 μέσα στην ΨΕΥΔΟΡΟΦΗ"), ("dash", MAG, "ψυκτικά μέσα στο ΔΑΠΕΔΟ (γέμισμα)"),
                          ("line", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 (ψευδοροφή → τοίχος → σιφώνι WC)"), ("ddash", BLUE2, "ψυκτικά split (ψευδοροφή)"),
                          ("hatch", ((0.86, 0.75, 0.68), BEAMC), "δοκάρια (δεν περνάμε από κάτω τους)")], w=w)
    north_arrow(c, X1 - 20, Y1 - 24, 9)
    frame(c, "ΚΜ-06", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΙΣΟΓΕΙΟ", "Κάτοψη διαδρομής · γυψότοιχος WC → δάπεδο → ΒΑ βεράντα", "Κλίμακα 1:40 · A3",
          floor="ΙΣΟΓΕΙΟ – ΙΣ1")


SHEETS = [sheet_plan, sheet_aa, sheet_bb, sheet_gg, sheet_det, sheet_gf]


def build(out):
    for m in (A, G):                                 # οι τομές βγαίνουν μόνο από μοντέλα χωρίς αποκλίσεις
        sheets.bind(m)
        bad = [r for r in checks.run() if r[5] == "ΑΠΟΚΛΙΣΗ"]
        assert not bad, bad
    c = new_canvas(out, "Κλιματιστικό σαλονιού ΚΜ1 – τομές – Κωνσταντινουπόλεως 12")
    c.setPageCompression(1)
    for fn in SHEETS:
        fn(c); c.showPage()
    c.save()
    print("OK", os.path.abspath(out), "· φύλλα", len(SHEETS))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTDIR, "ΚΛΙΜΑΤΙΣΤΙΚΟ_ΣΑΛΟΝΙΟΥ_ΚΜ1_ΤΟΜΕΣ_%s.pdf" % REV))
