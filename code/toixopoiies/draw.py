"""Βοηθητικά σχεδίασης (ReportLab) για τα φύλλα τοιχοποιιών – A3 οριζόντιο."""
import os, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = landscape(A3)          # 1190.55 × 841.89 pt
PT_PER_M_60 = 72 / 25.4 * 1000 / 60      # 47,244 pt/m (1:60)

for name, f in [("Inter", "Inter-Regular.ttf"), ("Inter-Medium", "Inter-Medium.ttf"),
                ("Inter-SemiBold", "Inter-SemiBold.ttf"), ("Inter-Bold", "Inter-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", f)))

DARK = (0.10, 0.11, 0.13)
GREY = (0.45, 0.45, 0.50)
LIGHT = (0.80, 0.80, 0.82)
DIMC = (0.20, 0.20, 0.22)
BLUE = (0.30, 0.40, 0.60)


class View:
    """Μετασχηματισμός μοντέλου (m, y προς νότο) → σελίδα (pt, y προς τα πάνω)."""
    def __init__(self, c, ox, oy, s):
        self.c, self.ox, self.oy, self.s = c, ox, oy, s

    def p(self, x, y):
        return self.ox + x * self.s, PAGE_H - (self.oy + y * self.s)

    # ---- βασικά
    def poly(self, pts, fill=None, stroke=None, lw=0.3, close=True):
        c = self.c
        path = c.beginPath()
        x, y = self.p(*pts[0]); path.moveTo(x, y)
        for q in pts[1:]:
            path.lineTo(*self.p(*q))
        if close:
            path.close()
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.drawPath(path, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def rect(self, x0, y0, x1, y1, **kw):
        self.poly([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], **kw)

    def line(self, x0, y0, x1, y1, color=DARK, lw=0.5, dash=None):
        c = self.c; c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.line(*self.p(x0, y0), *self.p(x1, y1))
        c.setDash([])

    def circle(self, x, y, r, fill=None, stroke=None, lw=0.4):
        c = self.c; X, Y = self.p(x, y)
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.circle(X, Y, r * self.s, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def arc(self, cx, cy, r, a0, a1, color=GREY, lw=0.35):
        """Τόξο (μοίρες, μαθηματική φορά στο μοντέλο: 0 = +x, 90 = +y δηλ. νότος)."""
        c = self.c; c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        path = c.beginPath()
        n = 24
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            X, Y = self.p(cx + r * math.cos(a), cy + r * math.sin(a))
            (path.moveTo if i == 0 else path.lineTo)(X, Y)
        c.drawPath(path, stroke=1, fill=0)

    def text(self, x, y, s, size=5, font="Inter", color=DARK, anchor="c", rot=0, dy=0, bg=False):
        """anchor: c / l / r (οριζόντια), κατακόρυφα κεντραρισμένο· rot 90 = κείμενο προς τα πάνω· bg: λευκό φόντο."""
        c = self.c; X, Y = self.p(x, y)
        c.saveState(); c.translate(X, Y); c.rotate(rot)
        c.setFont(font, size); c.setFillColorRGB(*color)
        w = pdfmetrics.stringWidth(s, font, size)
        off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
        if bg:
            c.setFillColorRGB(1, 1, 1); c.rect(off - 1.5, -size * 0.35 + dy - 1.5, w + 3, size + 2, stroke=0, fill=1)
            c.setFillColorRGB(*color)
        c.drawString(off, -size * 0.35 + dy, s)
        c.restoreState()

    def text_w(self, s, size, font="Inter"):
        return pdfmetrics.stringWidth(s, font, size) / self.s

    # ---- διαγράμμιση με αποκοπή
    def hatch(self, pts, spacing, angle_deg, color, lw=0.3, grid=False):
        c = self.c; c.saveState()
        path = c.beginPath()
        path.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            path.lineTo(*self.p(*q))
        path.close(); c.clipPath(path, stroke=0, fill=0)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        d = math.hypot(x1 - x0, y1 - y0)
        angles = [angle_deg, angle_deg + 90] if grid else [angle_deg]
        for ang in angles:
            a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            k = -d
            while k <= d:
                px, py = cx + nx * k, cy + ny * k
                c.line(*self.p(px - ux * d, py - uy * d), *self.p(px + ux * d, py + uy * d))
                k += spacing
        c.restoreState()

    def brick(self, pts, course=0.065, brick_len=0.13, color=(0.55, 0.30, 0.20), lw=0.25):
        """Τούβλα: οριζόντιες στρώσεις + κατακόρυφοι αρμοί σε δρομική διάταξη (κατά τον άξονα)."""
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        horiz = (x1 - x0) >= (y1 - y0)
        c = self.c; c.saveState()
        path = c.beginPath(); path.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            path.lineTo(*self.p(*q))
        path.close(); c.clipPath(path, stroke=0, fill=0)
        c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        if horiz:
            y = y0; i = 0
            while y < y1 + course:
                c.line(*self.p(x0, y), *self.p(x1, y))
                xx = x0 + (brick_len / 2 if i % 2 else 0)
                while xx < x1:
                    c.line(*self.p(xx, y), *self.p(xx, min(y + course, y1)))
                    xx += brick_len
                y += course; i += 1
        else:
            x = x0; i = 0
            while x < x1 + course:
                c.line(*self.p(x, y0), *self.p(x, y1))
                yy = y0 + (brick_len / 2 if i % 2 else 0)
                while yy < y1:
                    c.line(*self.p(x, yy), *self.p(min(x + course, x1), yy))
                    yy += brick_len
                x += course; i += 1
        c.restoreState()

    # ---- ετικέτα τοίχου
    def label(self, x, y, s, size=4.8, rot=0, font="Inter-Medium", pad=0.05):
        c = self.c; X, Y = self.p(x, y)
        w = pdfmetrics.stringWidth(s, font, size) + 2 * pad * self.s
        h = size + 2.2
        c.saveState(); c.translate(X, Y); c.rotate(rot)
        c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.3)
        c.rect(-w / 2, -h / 2, w, h, stroke=1, fill=1)
        c.setFont(font, size); c.setFillColorRGB(*DARK)
        c.drawCentredString(0, -size * 0.35, s)
        c.restoreState()

    # ---- αλυσίδα διαστάσεων
    def dim_chain(self, orient, pos, pts, size=5.0, color=DIMC, tick=0.08, side=-1, ext=0.0, font="Inter"):
        """orient 'H': γραμμή στο y=pos, σημεία x· 'V': γραμμή στο x=pos, σημεία y.
        side: -1 κείμενο προς βορρά/δύση της γραμμής, +1 προς νότο/ανατολή."""
        pts = sorted(pts)
        c = self.c
        a, b = pts[0], pts[-1]
        if orient == "H":
            self.line(a, pos, b, pos, color=color, lw=0.4)
        else:
            self.line(pos, a, pos, b, color=color, lw=0.4)
        for q in pts:
            if orient == "H":
                self.line(q - tick / 2, pos + tick / 2, q + tick / 2, pos - tick / 2, color=color, lw=0.5)
                if ext:
                    self.line(q, pos, q, pos + ext, color=(0.55, 0.55, 0.58), lw=0.25)
            else:
                self.line(pos - tick / 2, q + tick / 2, pos + tick / 2, q - tick / 2, color=color, lw=0.5)
                if ext:
                    self.line(pos, q, pos + ext, q, color=(0.55, 0.55, 0.58), lw=0.25)
        off = 0.10 * size / 5.0
        for q0, q1 in zip(pts[:-1], pts[1:]):
            L = q1 - q0
            s = ("%.2f" % (L + 1e-6)).replace(".", ",")
            w = self.text_w(s, size, font)
            mid = (q0 + q1) / 2
            if orient == "H":
                if w <= L - 0.04:
                    self.text(mid, pos + side * off, s, size=size, font=font, color=color)
                else:   # κοντό τμήμα: κείμενο κάθετα δίπλα στη γραμμή
                    self.text(mid, pos + side * (off + w / 2 + 0.02), s, size=size, font=font, color=color, rot=90)
            else:
                if w <= L - 0.04:
                    self.text(pos + side * off, mid, s, size=size, font=font, color=color, rot=90)
                else:
                    self.text(pos + side * (off + 0.02), mid, s, size=size, font=font, color=color)

    # ---- πόρτα
    def door(self, hinge, leaf_end, jamb, arc=True):
        hx, hy = hinge; lx, ly = leaf_end; jx, jy = jamb
        self.line(hx, hy, lx, ly, color=DARK, lw=0.9)
        if not arc or (hx, hy) == (jx, jy):
            return
        r = math.hypot(lx - hx, ly - hy)
        a0 = math.degrees(math.atan2(ly - hy, lx - hx))
        a1 = math.degrees(math.atan2(jy - hy, jx - hx))
        d = (a1 - a0 + 540) % 360 - 180
        self.arc(hx, hy, r, a0, a0 + d, color=GREY, lw=0.35)


def new_canvas(path, title):
    c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(title); c.setAuthor("ARKAD Ι.Κ.Ε. – Claude")
    return c


def frame_and_title(c, sheet_no, theme, sub1, sub2, base, scale_txt, rev, date):
    """Πλαίσιο σελίδας και υπόμνημα τίτλου (κάτω λωρίδα), όπως το R14."""
    m = 20
    c.setStrokeColorRGB(*DARK); c.setLineWidth(1.0)
    c.rect(m, m, PAGE_W - 2 * m, PAGE_H - 2 * m, stroke=1, fill=0)
    y0, hgt = m, 72
    c.setLineWidth(0.6); c.line(m, y0 + hgt, PAGE_W - m, y0 + hgt)
    xs = [m, 425, 725, 1000, PAGE_W - m]
    for x in xs[1:-1]:
        c.line(x, y0, x, y0 + hgt)
    def t(x, y, s, font="Inter", size=8, color=DARK):
        c.setFont(font, size); c.setFillColorRGB(*color); c.drawString(x, y, s)
    top = y0 + hgt - 14
    t(xs[0] + 10, top, "ΕΡΓΟ", "Inter-Medium", 6.5, GREY)
    t(xs[0] + 10, top - 16, "ΠΕΝΤΑΟΡΟΦΟ ΚΤΗΡΙΟ ΚΑΤΟΙΚΙΩΝ – ΑΡΓΥΡΟΥΠΟΛΗ", "Inter-SemiBold", 8)
    t(xs[0] + 10, top - 28, "Κωνσταντινουπόλεως 12 & Αγ. Βαρβάρας · Ο.Τ. 103-15", "Inter", 8)
    t(xs[0] + 10, top - 40, "Εργοδότης: INTERKAT Α.Ε. · Κατασκευή: ARKAD Ι.Κ.Ε.", "Inter", 8)
    t(xs[1] + 10, top, "ΘΕΜΑ ΣΧΕΔΙΟΥ", "Inter-Medium", 6.5, GREY)
    t(xs[1] + 10, top - 18, theme, "Inter-Bold", 11)
    t(xs[1] + 10, top - 31, sub1, "Inter-Medium", 7.5)
    t(xs[1] + 10, top - 42, sub2, "Inter-Medium", 7.5)
    t(xs[2] + 10, top, "ΒΑΣΗ", "Inter-Medium", 6.5, GREY)
    t(xs[2] + 10, top - 16, base, "Inter", 7.2)
    t(xs[3] + 10, top, "ΑΡ. ΣΧΕΔΙΟΥ", "Inter-Medium", 6.5, GREY)
    t(xs[3] + 10, top - 28, sheet_no, "Inter-Bold", 22)
    t(xs[3] + 10, top - 42, scale_txt, "Inter-SemiBold", 8)
    t(xs[3] + 10, top - 54, "%s · %s" % (date, rev), "Inter", 7.5)


def north_arrow(c, x, y, r=10):
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.8)
    c.circle(x, y, r, stroke=1, fill=0)
    c.setFillColorRGB(*DARK)
    p = c.beginPath(); p.moveTo(x, y + r * 0.8); p.lineTo(x - r * 0.35, y - r * 0.4)
    p.lineTo(x, y - r * 0.1); p.lineTo(x + r * 0.35, y - r * 0.4); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFont("Inter-SemiBold", 10); c.drawCentredString(x, y + r + 4, "Β")
