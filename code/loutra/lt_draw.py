"""Βοηθητικά σχεδίασης για τα φύλλα λουτρών (όψεις / κάτοψη / κάναβος πλακιδίων) – A3 οριζόντιο, 1:25.

Δύο συστήματα: κάτοψη (x → ανατολή, y → νότος, όπως όλα τα μοντέλα του έργου) και όψη (u → δεξιά, z → πάνω).
"""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
from draw import PAGE_W, PAGE_H, DARK, GREY, DIMC, frame_and_title, new_canvas, north_arrow   # noqa: E402 (γραμματοσειρές Inter)
from reportlab.pdfbase import pdfmetrics   # noqa: E402

S25 = 72 / 25.4 * 1000 / 25          # 113,386 pt/m (1:25)

# ---- χρώματα
TILE = (0.965, 0.950, 0.925)         # ολόκληρο πλακάκι
TILE_CUT = (0.905, 0.880, 0.835)     # κομμένο κομμάτι
JOINT = (0.42, 0.38, 0.33)           # αρμός
NICHE = (0.70, 0.64, 0.56)           # εσοχή (βάθος)
NICHE_IN = (0.84, 0.80, 0.74)
GLASS = (0.25, 0.50, 0.80)
GLASS_F = (0.86, 0.92, 0.97)
WOOD = (0.86, 0.79, 0.67)            # έπιπλο νιπτήρα
MIRROR = (0.83, 0.90, 0.94)
SAN = (1, 1, 1)                      # είδη υγιεινής
PRE = (0.93, 0.50, 0.12)             # προτοίχισμα (πρόταση)
PRE_F = (0.99, 0.88, 0.74)
WALLG = (0.80, 0.80, 0.82)           # τοιχοποιία (υπόβαθρο)
COLG = (0.42, 0.42, 0.45)            # σκυρόδεμα
ETICSG = (0.94, 0.93, 0.88)
HID = (0.55, 0.30, 0.55)             # κρυφά (καζανάκι, στήλη)
RED = (0.75, 0.12, 0.10)
WHITE = (1, 1, 1)


def fm(v):
    """Μήκος σε m με κόμμα: 0,60 · 0,485 (τρίτο δεκαδικό μόνο όταν χρειάζεται)."""
    v = round(v + 1e-9, 3)
    if abs(v * 100 - round(v * 100)) < 0.05:
        return ("%.2f" % v).replace(".", ",")
    return ("%.3f" % v).replace(".", ",")


def lvl(z):
    return ("+%.2f" % z).replace(".", ",")


class V2:
    """Μετασχηματισμός (a, b) σε m → σελίδα σε pt. ydown=True για κάτοψη (b = y προς νότο)."""

    def __init__(self, c, ox, oy, s=S25, ydown=False, a0=0.0, b0=0.0):
        self.c, self.ox, self.oy, self.s, self.ydown, self.a0, self.b0 = c, ox, oy, s, ydown, a0, b0

    def p(self, a, b):
        X = self.ox + (a - self.a0) * self.s
        Y = self.oy - (b - self.b0) * self.s if self.ydown else self.oy + (b - self.b0) * self.s
        return X, Y

    # ---- βασικά
    def _style(self, fill, stroke, lw, dash):
        c = self.c
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])

    def poly(self, pts, fill=None, stroke=None, lw=0.4, dash=None, close=True):
        c = self.c
        path = c.beginPath()
        path.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            path.lineTo(*self.p(*q))
        if close: path.close()
        self._style(fill, stroke, lw, dash)
        c.drawPath(path, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def rect(self, a0, b0, a1, b1, **kw):
        self.poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], **kw)

    def rrect(self, a0, b0, a1, b1, r, fill=None, stroke=None, lw=0.4):
        c = self.c
        X0, Y0 = self.p(a0, b0); X1, Y1 = self.p(a1, b1)
        self._style(fill, stroke, lw, None)
        c.roundRect(min(X0, X1), min(Y0, Y1), abs(X1 - X0), abs(Y1 - Y0), r * self.s, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def line(self, a0, b0, a1, b1, color=DARK, lw=0.5, dash=None):
        c = self.c; c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        c.line(*self.p(a0, b0), *self.p(a1, b1)); c.setDash([])

    def circle(self, a, b, r, fill=None, stroke=None, lw=0.4, dash=None):
        c = self.c; X, Y = self.p(a, b)
        self._style(fill, stroke, lw, dash)
        c.circle(X, Y, r * self.s, stroke=1 if stroke else 0, fill=1 if fill else 0); c.setDash([])

    def ellipse(self, a0, b0, a1, b1, fill=None, stroke=None, lw=0.4):
        c = self.c; X0, Y0 = self.p(a0, b0); X1, Y1 = self.p(a1, b1)
        self._style(fill, stroke, lw, None)
        c.ellipse(X0, Y0, X1, Y1, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def arc(self, ca, cb, r, ang0, ang1, color=GREY, lw=0.35, dash=None):
        c = self.c; c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        path = c.beginPath(); n = 28
        for i in range(n + 1):
            t = math.radians(ang0 + (ang1 - ang0) * i / n)
            X, Y = self.p(ca + r * math.cos(t), cb + r * math.sin(t))
            (path.moveTo if i == 0 else path.lineTo)(X, Y)
        c.drawPath(path, stroke=1, fill=0); c.setDash([])

    def text(self, a, b, s, size=6, font="Inter", color=DARK, anchor="c", rot=0, dx=0, dy=0, bg=None):
        c = self.c; X, Y = self.p(a, b)
        c.saveState(); c.translate(X + dx, Y + dy); c.rotate(rot)
        c.setFont(font, size)
        w = pdfmetrics.stringWidth(s, font, size)
        off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
        if bg:
            c.setFillColorRGB(*bg); c.rect(off - 1.2, -size * 0.36 - 1.0, w + 2.4, size + 1.6, stroke=0, fill=1)
        c.setFillColorRGB(*color)
        c.drawString(off, -size * 0.36, s)
        c.restoreState()

    def hatch(self, pts, step_pt=3.2, color=PRE, lw=0.35, ang=45):
        c = self.c; c.saveState()
        path = c.beginPath(); P = [self.p(*q) for q in pts]
        path.moveTo(*P[0])
        for q in P[1:]: path.lineTo(*q)
        path.close(); c.clipPath(path, stroke=0, fill=0)
        xs = [q[0] for q in P]; ys = [q[1] for q in P]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        d = (x1 - x0) + (y1 - y0)
        c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        k = -d
        while k <= d:
            c.line(x0 + k, y0, x0 + k + (y1 - y0), y1)
            k += step_pt
        c.restoreState()

    # ---- αλυσίδες διαστάσεων (η γραμμή σε απόσταση off pt από τη στάθμη b / τη θέση a)
    def chain_h(self, us, b, off=-16, size=6.4, color=DIMC, font="Inter-Medium", labels=None, ext=True):
        c = self.c; us = sorted(us)
        Y = self.p(0, b)[1] + off
        Xs = [self.p(u, b)[0] for u in us]
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.setDash([])
        c.line(Xs[0], Y, Xs[-1], Y)
        for X in Xs:
            c.setLineWidth(0.6); c.line(X - 2.6, Y - 2.6, X + 2.6, Y + 2.6)
            if ext:
                c.setLineWidth(0.2); c.line(X, Y, X, Y - off * 0.55)
        for i, (X0, X1) in enumerate(zip(Xs[:-1], Xs[1:])):
            s = labels[i] if labels else fm(us[i + 1] - us[i])
            w = pdfmetrics.stringWidth(s, font, size)
            c.setFillColorRGB(*color); c.setFont(font, size)
            if w <= (X1 - X0) - 3:
                c.drawCentredString((X0 + X1) / 2, Y + 2.2, s)
            else:   # στενό τμήμα: το κείμενο κάτω από τη γραμμή, μικρότερο
                c.setFont(font, size - 0.8)
                c.drawCentredString((X0 + X1) / 2, Y - size - 0.6, s)

    def chain_v(self, zs, a, off=16, size=6.4, color=DIMC, font="Inter-Medium", labels=None):
        c = self.c; zs = sorted(zs)
        X = self.p(a, 0)[0] + off
        Ys = sorted(self.p(a, z)[1] for z in zs)
        if self.ydown:
            zs = zs[::-1]
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.setDash([])
        c.line(X, Ys[0], X, Ys[-1])
        for Y in Ys:
            c.setLineWidth(0.6); c.line(X - 2.6, Y - 2.6, X + 2.6, Y + 2.6)
            c.setLineWidth(0.2); c.line(X, Y, X - off * 0.55, Y)
        for i, (Y0, Y1) in enumerate(zip(Ys[:-1], Ys[1:])):
            s = labels[i] if labels else fm(abs(zs[i + 1] - zs[i]))
            w = pdfmetrics.stringWidth(s, font, size)
            c.saveState(); c.setFillColorRGB(*color)
            if w <= (Y1 - Y0) - 3:
                c.translate(X - 2.4 if off > 0 else X - 2.4, (Y0 + Y1) / 2); c.rotate(90)
                c.setFont(font, size); c.drawCentredString(0, 0, s)
            else:
                c.setFont(font, size - 0.8)
                c.translate(X + (4 if off > 0 else -4), (Y0 + Y1) / 2 - (size - 0.8) * 0.36)
                (c.drawString if off > 0 else c.drawRightString)(0, 0, s)
            c.restoreState()


def marker(c, X, Y, letter, ang, r=7.2):
    """Σήμανση όψης στην κάτοψη: κύκλος με γράμμα + βέλος προς τον τοίχο που κοιτάμε (ang σε μοίρες σελίδας)."""
    t = math.radians(ang)
    c.setFillColorRGB(*DARK); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6)
    tip = (X + (r + 6.5) * math.cos(t), Y + (r + 6.5) * math.sin(t))
    b1 = (X + r * 0.95 * math.cos(t + 0.75), Y + r * 0.95 * math.sin(t + 0.75))
    b2 = (X + r * 0.95 * math.cos(t - 0.75), Y + r * 0.95 * math.sin(t - 0.75))
    path = c.beginPath(); path.moveTo(*tip); path.lineTo(*b1); path.lineTo(*b2); path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1); c.circle(X, Y, r, stroke=1, fill=1)
    c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 8.2); c.drawCentredString(X, Y - 2.9, letter)
