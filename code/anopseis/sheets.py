"""Φύλλα ανόψης οροφής – A3, 1:50 – για κάθε όροφο (μοντέλο *_anopsi.py):
ΑΝ-01 στάθμες · ΑΝ-02 κλιματισμός · ΑΝ-03 φωτισμός/πυρανίχνευση · ΑΝ-04 έλεγχος.
Χρήση: sheets.bind(μοντέλο) και μετά sheet_an01(c, no) … (οι αριθμοί φύλλων δίνονται από το build)."""
import math
import checks
import sheet_t01                                   # code/toixopoiies (το μοντέλο βάζει τη διαδρομή)
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow
from reportlab.pdfbase import pdfmetrics

S = 72 / 25.4 * 1000 / 50          # 1:50 → 56,693 pt/m
OX, OY = 215.43, 87.87              # ίδια θέση με το R10

ORANGE = (0.80, 0.47, 0.05)
RED = (0.78, 0.10, 0.12)
BLUE = (0.05, 0.36, 0.66)
BLUE2 = (0.25, 0.55, 0.75)
BLUE_F = (0.86, 0.92, 0.98)
GREEN = (0.05, 0.52, 0.42)
GREEN_F = (0.86, 0.95, 0.91)
MAG = (0.80, 0.10, 0.50)
CABLE_C = (0.10, 0.45, 0.30)
BEAM = (0.62, 0.30, 0.16)
COLORS = dict(MAG=MAG, BLUE=BLUE, BLUE2=BLUE2, GREEN=GREEN, ORANGE=ORANGE, RED=RED, GREY=GREY, DARK=DARK, BEAM=BEAM)
FILLS = [(0.985, 0.98, 0.97), (0.965, 0.955, 0.93), (0.94, 0.91, 0.85), (0.91, 0.87, 0.79), (0.86, 0.81, 0.71), (0.82, 0.76, 0.65)]
NEUTRAL = (0.965, 0.96, 0.95)
EXPOSED_F = (0.93, 0.93, 0.94)
POCKET_F = (0.88, 0.93, 0.98)
THROW = {"Ν": "νότια", "Β": "βόρεια", "Α": "ανατολικά", "Δ": "δυτικά"}
THROW_V = {"Ν": (0, 1), "Β": (0, -1), "Α": (1, 0), "Δ": (-1, 0)}

A = None
LEVEL_FILL = {}


def bind(model):
    global A, LEVEL_FILL
    A = model
    checks.bind(model)
    if hasattr(A, "LEVEL_FILL"):
        LEVEL_FILL = dict(A.LEVEL_FILL)
    else:   # ψηλότερη στάθμη = ανοιχτότερη
        lv = sorted({z["level"] for z in A.ZONES if not z.get("exposed")}, reverse=True)
        LEVEL_FILL = {l: FILLS[min(i, len(FILLS) - 1)] for i, l in enumerate(lv)}
    return model


def _wrap(s, font, size, w):
    out, cur = [], ""
    for wd in s.split(" "):
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) > w and cur:
            out.append(cur); cur = wd
        else:
            cur = t
    return out + [cur]


def fmt(v):
    return ("%+.2f" % v).replace(".", ",")


def lfmt(v):
    return A.LEVEL_FMT(v) if hasattr(A, "LEVEL_FMT") else fmt(v)


def view(c):
    return View(c, OX, OY, S)


def zones_fill(v, colored=True):
    for z in A.ZONES:
        if z.get("exposed"):
            col = EXPOSED_F if colored else NEUTRAL
        else:
            col = LEVEL_FILL[z["level"]] if colored else NEUTRAL
        for r in z["rects"]:
            v.rect(*r, fill=col)
        if z.get("box"):
            for r in z["rects"]:
                v.hatch([[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]], 0.10, 45, (0.70, 0.62, 0.50), 0.3)
    for r in getattr(A, "VOIDS", []):      # ανοίγματα πλάκας (διπλό ύψος) – χωρίς ψευδοροφή
        v.rect(*r, fill=(1, 1, 1))
        v.hatch([[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]], 0.15, -45, (0.75, 0.75, 0.78), 0.3)


def slope_lines(v, labels=True):
    """Ισοϋψείς της κεκλιμένης πλάκας (σοφίτα): A.SLOPE_LINES = [(y, ετικέτα)], A.SLOPE_X = (x0, x1)."""
    x0, x1 = getattr(A, "SLOPE_X", (0, 0))
    for y, lab in getattr(A, "SLOPE_LINES", []):
        v.line(x0, y, x1, y, color=(0.55, 0.45, 0.30), lw=0.45, dash=[6, 2, 1, 2])
    if labels:
        for y, lab in getattr(A, "SLOPE_LINES", []):
            for lx in getattr(A, "SLOPE_LAB_X", [(x0 + x1) / 2]):
                v.text(lx, y - 0.06, lab, size=4.2, color=(0.45, 0.35, 0.20), font="Inter-SemiBold", bg=True)


def split_sym(v, u, colored=True):
    """Split τοίχου σε κάτοψη: σώμα μονάδας στον τοίχο (+ βέλη ρίψης στο ΑΝ-02)."""
    x0, y0, x1, y1 = u["rect"]
    col = BLUE if colored else (0.55, 0.65, 0.80)
    v.rect(x0, y0, x1, y1, fill=(0.80, 0.88, 0.97) if colored else (1, 1, 1), stroke=col, lw=0.8 if colored else 0.5)
    tx, ty = THROW_V[u["throw"]]
    # περσίδα στη μπροστινή παρειά
    if tx:
        xf = x1 if tx > 0 else x0
        v.line(xf - tx * 0.05, y0 + 0.04, xf - tx * 0.05, y1 - 0.04, color=col, lw=0.6)
    else:
        yf = y1 if ty > 0 else y0
        v.line(x0 + 0.04, yf - ty * 0.05, x1 - 0.04, yf - ty * 0.05, color=col, lw=0.6)


def plan(v):
    """Τοιχοποιίες του ορόφου ως υπόβαθρο (χωρίς περιβάλλοντα χώρο)· στο Β1 η κουζίνα του EPIPLA αντικαθίσταται από τη διάταξη του μοντέλου."""
    W = A.W
    keys = ("FURN_MASKS", "EXTRA_LINES", "FURN_WHITEOUT", "SITE")
    saved = {k: getattr(W, k) for k in keys if hasattr(W, k)}
    W.FURN_MASKS = list(getattr(W, "FURN_MASKS", [])) + list(getattr(A, "PLAN_MASKS", []))
    if getattr(A, "PLAN_CLEAR_EXTRA", False):
        W.EXTRA_LINES, W.FURN_WHITEOUT = [], []
    if hasattr(W, "SITE"):
        W.SITE = None
    sheet_t01.M = W
    try:
        sheet_t01.draw_plan(v, with_labels=False, with_dims=False, with_furniture=True, with_text=False)
    finally:
        for k, val in saved.items():
            setattr(W, k, val)
    for item in getattr(A, "KITCHEN", []):
        sheet_t01.equip(v, item, False)
    v.c.setDash([3, 1.5])
    for r in getattr(A, "UPPER_CAB", []):
        v.rect(*r, stroke=(0.45, 0.45, 0.50), lw=0.5)
    v.c.setDash([])


def tall_marks(v):
    for name, (x0, y0, x1, y1) in A.TALL:
        if name.startswith("τοίχος κλιματιστικού"):
            continue
        v.text((x0 + x1) / 2, (y0 + y1) / 2, "έως οροφή", size=3.8, color=GREY, font="Inter-Medium", bg=True)


def level_tag(v, x, y, lvl, size=6.2, sub=None, txt=None):
    s = txt or lfmt(lvl)
    v.text(x, y, s, size=size, font="Inter-Bold", color=DARK, bg=True)
    X, Y = v.p(x, y)
    w = pdfmetrics.stringWidth(s, "Inter-Bold", size)
    c = v.c
    c.setFillColorRGB(*DARK)
    p = c.beginPath(); tx = X - w / 2 - 6; ty = Y - 1.5
    p.moveTo(tx - 2.6, ty + 3.4); p.lineTo(tx + 2.6, ty + 3.4); p.lineTo(tx, ty - 0.8); p.close()
    c.drawPath(p, stroke=0, fill=1)
    if sub:
        v.text(x, y + 0.17, sub, size=4.2, color=GREY)


def arrow(v, x0, y0, x1, y1, color=BLUE, lw=0.6, head=0.06):
    v.line(x0, y0, x1, y1, color=color, lw=lw)
    a = math.atan2(y1 - y0, x1 - x0)
    for s_ in (+1, -1):
        v.line(x1, y1, x1 - head * math.cos(a + s_ * 0.45), y1 - head * math.sin(a + s_ * 0.45), color=color, lw=lw)


def legend(c, items, x=1010, y=740, title="ΥΠΟΜΝΗΜΑ", w=140, size=5.3):
    """Υπόμνημα στη δεξιά στήλη: items = [(draw_fn(c, x, y), κείμενο)] · επιστρέφει το y κάτω από το υπόμνημα."""
    c.setFont("Inter-SemiBold", 6.4); c.setFillColorRGB(*DARK); c.drawString(x, y, title)
    yy = y - 12
    for fn, txt in items:
        fn(c, x + 6, yy + 2)
        c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        for j, l in enumerate(_wrap(txt, "Inter", size, w)):
            c.drawString(x + 18, yy - j * (size + 1.5), l)
        yy -= (size + 1.5) * len(_wrap(txt, "Inter", size, w)) + 3.5
    return yy - 6


def clip_on(c):
    c.saveState()
    p = c.beginPath(); p.rect(22, 94, 1004 - 22, 819 - 94)
    c.clipPath(p, stroke=0, fill=0)


def clip_off(c):
    c.restoreState()


def _sw(fill=None, stroke=None, hatch=False):
    def f(c, x, y):
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(0.5)
        c.rect(x - 5, y - 3, 10, 6, stroke=1 if stroke else 0, fill=1 if fill else 0)
    return f


def side_notes(c, lines, x=1010, y=740, w=150, title="ΣΗΜΕΙΩΣΕΙΣ", size=5.2):
    c.setFont("Inter-SemiBold", 6.4); c.setFillColorRGB(*DARK); c.drawString(x, y, title)
    yy = y - 10
    for s in lines:
        words, cur, out = s.split(" "), "", []
        for wd in words:
            t = (cur + " " + wd).strip()
            if pdfmetrics.stringWidth(t, "Inter", size) > w and cur:
                out.append(cur); cur = wd
            else:
                cur = t
        out.append(cur)
        c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        for j, l in enumerate(out):
            c.drawString(x + (0 if j == 0 else 6), yy, l); yy -= size + 1.6
        yy -= 2.5
    return yy


def title(c, no, theme, sub, scale="Κλίμακα 1:50 · A3"):
    north_arrow(c, 1150, 795)
    frame_and_title(c, no, theme, sub, A.SHEET_FLOOR, A.BASE_TXT, scale, A.REV, A.DATE)


def texts(v, items):
    """Ελεύθερα κείμενα του μοντέλου: (x, y, κείμενο, {size, color, font, rot, anchor, bg})."""
    for it in items:
        x, y, s = it[:3]
        kw = dict(it[3]) if len(it) > 3 else {}
        if isinstance(kw.get("color"), str):
            kw["color"] = COLORS[kw["color"]]
        kw.setdefault("size", 4.4)
        v.text(x, y, s, **kw)


def dims(v, chains, size=4.4):
    for o, p, pts in chains:
        v.dim_chain(o, p, pts, size=size, side=-1)


def wall_unit_block(v, detailed=False):
    """Καναλάτη τοίχου (σοφίτα R03): μπλοκ «τοίχος κλιματιστικού» ΤΚ σε κάτοψη· detailed → μονάδα, στόμιο, ρίψη, θυρίδα."""
    c = v.c
    for u in getattr(A, "WALL_UNITS", []):
        bx0, by0, bx1, by1 = u["box"]
        v.rect(bx0, by0, bx1, by1, fill=(0.93, 0.95, 0.99) if detailed else (0.97, 0.97, 0.98), stroke=BLUE if detailed else GREY,
               lw=0.9 if detailed else 0.6)
        vx0, vy0, vx1, vy1 = u["void"]
        c.setDash([3, 1.5]); v.rect(vx0 + 0.025, vy0, vx1 - 0.025, vy1, stroke=BLUE if detailed else GREY, lw=0.45); c.setDash([])
        (fx0, fy), (fx1, _) = u["face"]
        sx0, sx1 = u["supply"]["x"]
        if not detailed:
            v.text((bx0 + bx1) / 2, (by0 + by1) / 2 - 0.04, "ΤΚ %s" % u["id"], size=4.2, color=(0.40, 0.48, 0.62), font="Inter-SemiBold", bg=True)
            v.text((bx0 + bx1) / 2, (by0 + by1) / 2 + 0.12, "έως οροφή", size=3.6, color=GREY, bg=True)
            v.line(sx0, fy, sx1, fy, color=(0.55, 0.65, 0.80), lw=1.4)
            continue
        ux0, ux1 = u["unit"]["x"]
        v.rect(ux0, vy0 + 0.025, ux1, vy1 - 0.025, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=0.6)
        v.line(ux0, vy0 + 0.025, ux1, vy1 - 0.025, color=BLUE, lw=0.3); v.line(ux0, vy1 - 0.025, ux1, vy0 + 0.025, color=BLUE, lw=0.3)
        v.line(sx0, fy, sx1, fy, color=BLUE, lw=2.4)
        tx, ty = THROW_V[u["throw"]]
        for k in range(5):
            xx = sx0 + 0.08 + k * (sx1 - sx0 - 0.16) / 4
            arrow(v, xx, fy + ty * 0.04, xx, fy + ty * 0.80)
        hx0, hx1 = u["hatch"]["x"]
        c.setDash([2, 1.2]); v.rect(hx0, fy - 0.10, hx1, fy - 0.01, stroke=DARK, lw=0.6); c.setDash([])
        v.text((bx0 + bx1) / 2, by0 + 0.12, "ΤΚ τοίχος 1,00 · κενό 0,30", size=4.0, color=BLUE, font="Inter-SemiBold", bg=True)
        lx, ly, lr = u["lab_at"]
        v.text(lx, ly, u["label"], size=4.6, rot=lr, color=BLUE, font="Inter-SemiBold", bg=True)
        v.text((hx0 + hx1) / 2 + 0.30, fy + 0.13, "ΘΕ %s" % u["hatch"]["size"], size=4.0, font="Inter-SemiBold", bg=True)


def roof_hatch(v, detailed=False):
    """Καταπακτή πρόσβασης στη στέγη μέσα στην ψευδοροφή (Δ΄ – lobby ανελκυστήρα, κατά αρχιτέκτονα)."""
    c = v.c
    for rh in getattr(A, "ROOF_HATCH", []):
        x0, y0, x1, y1 = rh["opening"]
        c.setDash([1.5, 1.5]); v.rect(x0, y0, x1, y1, stroke=GREY, lw=0.4); c.setDash([])
        x0, y0, x1, y1 = rh["rect"]
        v.rect(x0, y0, x1, y1, fill=(1, 1, 1), stroke=DARK, lw=0.7)
        v.line(x0, y0, x1, y1, color=DARK, lw=0.3); v.line(x0, y1, x1, y0, color=DARK, lw=0.3)
        lx, ly, lr = rh["lab_at"]
        v.text(lx, ly, rh["label"], size=4.0, rot=lr, font="Inter-SemiBold", bg=True)


def cables(v):
    """Όδευση καλωδίων shaft → διαμέρισμα μέσα στην ψευδοροφή του κλιμακοστασίου."""
    for cb in getattr(A, "CABLE_DRAW", []):
        for a_, b_ in zip(cb["pts"], cb["pts"][1:]):
            v.line(*a_, *b_, color=CABLE_C, lw=1.6, dash=[6, 1.5, 1.5, 1.5])
        X, Y = v.p(*cb["pts"][0])
        v.c.setFillColorRGB(*CABLE_C); v.c.rect(X - 2.6, Y - 2.6, 5.2, 5.2, stroke=0, fill=1)
        lx, ly, lr = cb["lab_at"]
        v.text(lx, ly, cb["label"], size=4.2, rot=lr, color=CABLE_C, font="Inter-SemiBold", bg=True)


def _vchain(c, x, ys, labels=True, size=4.6, side=-1):
    """Κατακόρυφη αλυσίδα διαστάσεων σε pt σελίδας: ys = [(Y pt, τιμή m)]."""
    c.setStrokeColorRGB(*DIMC); c.setLineWidth(0.4)
    c.line(x, ys[0][0], x, ys[-1][0])
    for Y, _ in ys:
        c.line(x - 2.2, Y - 2.2, x + 2.2, Y + 2.2)
    if labels:
        c.setFont("Inter", size); c.setFillColorRGB(*DIMC)
        for (Y0, a), (Y1, b) in zip(ys[:-1], ys[1:]):
            s_ = ("%.2f" % (b - a)).replace(".", ",")
            c.saveState(); c.translate(x + side * 3.0, (Y0 + Y1) / 2); c.rotate(90)
            c.drawCentredString(0, 0, s_) if (Y1 - Y0) > 14 else None
            c.restoreState()
            if (Y1 - Y0) <= 14:
                c.drawRightString(x - 4, (Y0 + Y1) / 2 - 1.5, s_) if side < 0 else c.drawString(x + 4, (Y0 + Y1) / 2 - 1.5, s_)


def wall_unit_elev(c, u, X0=70, Y0=300, k=72 / 25.4 * 1000 / 25):
    """Όψη του τοίχου ΤΚ από το υπνοδωμάτιο, 1:25 (αριστερό περιθώριο του ΑΝ-02 σοφίτας)."""
    bx0, bx1 = u["box"][0], u["box"][2]
    fy = u["face"][0][1]
    ceil = min(checks.ceil_at(x, fy) for x in u["supply"]["x"])

    def P(x, z):
        return X0 + (x - bx0) * k, Y0 + z * k

    W_ = (bx1 - bx0) * k
    top = Y0 + ceil * k
    c.setFont("Inter-Bold", 6.6); c.setFillColorRGB(*DARK)
    c.drawString(X0 - 40, top + 46, "ΟΨΗ ΤΟΙΧΟΥ ΤΚ – %s" % u["id"])
    c.setFont("Inter", 5.2)
    c.drawString(X0 - 40, top + 37, "από το υπνοδωμάτιο · 1:25 · παρειά Τ2N-01")
    c.drawString(X0 - 40, top + 29, "x %s–%s · κενό %s" % (("%.2f" % bx0).replace(".", ","), ("%.2f" % bx1).replace(".", ","),
                                                         ("%.2f" % (u["void"][3] - u["void"][1])).replace(".", ",")))
    # δάπεδο / πλάκα
    c.setStrokeColorRGB(*DARK); c.setLineWidth(1.0); c.line(X0 - 22, Y0, X0 + W_ + 22, Y0)
    c.setFillColorRGB(0.82, 0.82, 0.84); c.rect(X0 - 22, top, W_ + 44, 0.12 * k, stroke=0, fill=1)
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.8); c.line(X0 - 22, top, X0 + W_ + 22, top)
    c.setFont("Inter", 4.6); c.setFillColorRGB(*DARK)
    c.drawString(X0 - 22, top + 0.12 * k + 3, "πλάκα Σ8 (κεκλιμένη) – εδώ %s" % fmt(ceil))
    c.drawString(X0 - 22, Y0 - 9, "τελικό δάπεδο ±0,00")
    # παρειά τοίχου
    c.setFillColorRGB(0.96, 0.97, 0.99); c.setStrokeColorRGB(*BLUE); c.setLineWidth(0.9)
    c.rect(X0, Y0, W_, ceil * k, stroke=1, fill=1)
    # επιστροφή
    rx0, rx1 = u["ret"]["x"]; rz0, rz1 = u["ret"]["z"]
    X, Y = P(rx0, rz0); X2, Y2 = P(rx1, rz1)
    c.setFillColorRGB(*GREEN_F); c.setStrokeColorRGB(*GREEN); c.setLineWidth(0.7); c.rect(X, Y, X2 - X, Y2 - Y, stroke=1, fill=1)
    for i in range(1, 12):
        xx = X + i * (X2 - X) / 12; c.setLineWidth(0.3); c.line(xx, Y, xx, Y2)
    # μονάδα (κρυφή) + plenum προσαγωγής
    ux0, ux1 = u["unit"]["x"]; uz0, uz1 = u["unit"]["z"]
    X, Y = P(ux0, uz0); X2, Y2 = P(ux1, uz1)
    c.setDash([3, 1.5]); c.setStrokeColorRGB(*BLUE); c.setLineWidth(0.7); c.rect(X, Y, X2 - X, Y2 - Y, stroke=1, fill=0)
    sx0, sx1 = u["supply"]["x"]; sz0, sz1 = u["supply"]["z"]
    PX, PY = P(sx0 + 0.10, uz1); PX2, PY2 = P(sx1 - 0.10, sz0)
    c.setLineWidth(0.5); c.rect(PX, PY, PX2 - PX, PY2 - PY, stroke=1, fill=0); c.setDash([])
    c.setFont("Inter-SemiBold", 4.8); c.setFillColorRGB(*BLUE)
    c.drawCentredString((X + X2) / 2, (Y + Y2) / 2 + 2, "μονάδα (κρυφή)")
    c.setFont("Inter", 4.2); c.drawCentredString((X + X2) / 2, (Y + Y2) / 2 - 5, "κατακόρυφα")
    c.drawCentredString((PX + PX2) / 2, (PY + PY2) / 2, "plenum ↑")
    # προσαγωγή
    X, Y = P(sx0, sz0); X2, Y2 = P(sx1, sz1)
    c.setFillColorRGB(0.30, 0.45, 0.75); c.setStrokeColorRGB(*BLUE); c.rect(X, Y, X2 - X, Y2 - Y, stroke=1, fill=1)
    c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(0.4)
    for j in (1, 2):
        c.line(X + 2, Y + j * (Y2 - Y) / 3, X2 - 2, Y + j * (Y2 - Y) / 3)
    # θυρίδα
    hx0, hx1 = u["hatch"]["x"]; hz0, hz1 = u["hatch"]["z"]
    X, Y = P(hx0, hz0); X2, Y2 = P(hx1, hz1)
    c.setDash([2, 1.2]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.7); c.rect(X, Y, X2 - X, Y2 - Y, stroke=1, fill=0); c.setDash([])
    c.setLineWidth(0.3); c.line(X, Y, X2, Y2); c.line(X, Y2, X2, Y)
    # ετικέτες δεξιά
    lab = [((sz0 + sz1) / 2, "προσαγωγή %s" % u["supply"]["size"]), (uz1 + 0.02, "μονάδα %s" % u["unit"]["txt"].replace("μονάδα ", "")),
           ((hz0 + hz1) / 2, "ΘΕ %s – πλευρά ηλεκτρικών" % u["hatch"]["size"]), ((rz0 + rz1) / 2, u["ret"]["size"])]
    c.setFont("Inter", 4.4); c.setFillColorRGB(*DARK)
    for z, t in lab:
        Y = Y0 + z * k
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.3); c.line(X0 + W_ - 6, Y, X0 + W_ + 8, Y)
        ls = _wrap(t, "Inter", 4.4, 70)
        for j, l in enumerate(ls):
            c.drawString(X0 + W_ + 10, Y - 1.5 - j * 5.4, l)
    # διαστάσεις
    zs = sorted({0.0, rz0, rz1, hz0, hz1, sz0, sz1, round(ceil, 3)})
    _vchain(c, X0 - 12, [(Y0 + z * k, z) for z in zs])
    c.setStrokeColorRGB(*DIMC); c.setLineWidth(0.4); c.line(X0, Y0 - 16, X0 + W_, Y0 - 16)
    for xx in (X0, X0 + W_):
        c.line(xx - 2.2, Y0 - 18.2, xx + 2.2, Y0 - 13.8)
    c.setFont("Inter", 4.6); c.setFillColorRGB(*DIMC); c.drawCentredString(X0 + W_ / 2, Y0 - 24, "1,00")


# ======================================================================== ΑΝ-01 στάθμες
def sheet_an01(c, no="ΑΝ-01"):
    v = view(c)
    clip_on(c)
    zones_fill(v, colored=True)
    for cu in A.CURTAINS:
        if not cu.get("rail"):
            v.rect(*cu["rect"], fill=POCKET_F)
    slope_lines(v, labels=False)
    plan(v)
    wall_unit_block(v)
    roof_hatch(v)
    tall_marks(v)
    slope_lines(v, labels=True)
    # κουρτινόθηκες: οδηγοί
    for cu in A.CURTAINS:
        x0, y0, x1, y1 = cu["rect"]
        if not cu.get("rail"):
            v.rect(x0, y0, x1, y1, stroke=(0.35, 0.42, 0.50), lw=0.6)
        vert = (y1 - y0) > (x1 - x0)
        offs = (0.07, 0.14) if cu["width"] < 0.21 else (0.10, 0.17)
        glass = cu.get("glass") or ("W" if (vert and x0 < 5) else ("E" if vert else "S"))
        for o in offs:
            if vert:
                xx = x0 + o if glass == "W" else x1 - o
                v.line(xx, y0 + 0.02, xx, y1 - 0.02, color=(0.35, 0.42, 0.50), lw=0.5, dash=[4, 1.2, 1, 1.2])
            else:
                yy = y1 - o if glass == "S" else y0 + o
                if cu.get("rail"):
                    v.line(x0 + 0.02, yy, x1 - 0.02, yy, color=(0.25, 0.32, 0.45), lw=0.9)
                else:
                    v.line(x0 + 0.02, yy, x1 - 0.02, yy, color=(0.35, 0.42, 0.50), lw=0.5, dash=[4, 1.2, 1, 1.2])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lab = "%s · %s · %d×%d" % (cu["id"], cu["win"], round(cu["width"] * 100), round(cu["depth"] * 100))
        if cu.get("rail"):
            lab = "%s · %s · διπλή ράγα κουρτίνας στην πλάκα (7 / 14 cm)" % (cu["id"], cu["win"])
        if "lab_at" in cu:
            lx, ly, lr = cu["lab_at"]
            v.text(lx, ly, lab, size=4.6, rot=lr, color=(0.25, 0.35, 0.50), font="Inter-Medium", bg=True)
        elif vert:
            v.text(x0 - 0.14 if glass == "W" else x1 + 0.14, cy + 0.6, lab, size=4.6, rot=90, color=(0.25, 0.35, 0.50), font="Inter-Medium", bg=True)
        else:
            v.text(cx - 1.2, y0 - 0.12, lab, size=4.6, color=(0.25, 0.35, 0.50), font="Inter-Medium", bg=True)
    # δοκοί
    for name, sec, x0, y0, x1, y1 in A.BEAMS:
        v.rect(x0, y0, x1, y1, stroke=BEAM, lw=0.55)
        c.setDash([])
    c.setDash([5, 2])
    for name, sec, x0, y0, x1, y1 in A.BEAMS:
        v.rect(x0, y0, x1, y1, stroke=BEAM, lw=0.55)
    c.setDash([])
    for name, sec, *_ in A.BEAMS:
        if name in A.BEAM_LABELS:
            x, y, r = A.BEAM_LABELS[name]
            v.text(x, y, "%s %s · Κ.Π. %s" % (name, sec, lfmt(A.beam_soffit(sec))), size=4.4, rot=r, color=BEAM, font="Inter-Medium", bg=True)
    # ετικέτες στάθμης
    for z in A.ZONES:
        if z["id"] not in A.ZONE_LABEL_AT:
            continue
        x, y = A.ZONE_LABEL_AT[z["id"]]
        if z.get("exposed"):
            sub = "%s · εμφανής πλάκα" % z["id"]
        elif z.get("box"):
            sub = "κουτί ντουλάπας"
        else:
            sub = "%s · κενό %d cm" % (z["id"], round((A.SLABS[z["slab"]] - z["level"]) * 100))
        level_tag(v, x, y, z["level"], sub=z.get("tag_sub", sub), txt=z.get("tag_txt"))
    texts(v, getattr(A, "TEXTS_AN01", []))
    dims(v, getattr(A, "DIMS_AN01", []))
    clip_off(c)
    yl = side_notes(c, A.NOTES_AN01, y=770)
    items = []
    for key, txt in A.LEGEND_AN01:
        if key == "pocket":
            items.append((_sw(POCKET_F, (0.35, 0.42, 0.50)), txt))
        elif key == "rail":
            items.append((lambda c_, x, y: (c_.setStrokeColorRGB(0.25, 0.32, 0.45), c_.setLineWidth(0.9), c_.line(x - 6, y - 1.5, x + 6, y - 1.5),
                                            c_.line(x - 6, y + 1.5, x + 6, y + 1.5), c_.setLineWidth(0.5)), txt))
        elif key == "beam":
            items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*BEAM), c_.setDash([5, 2]), c_.rect(x - 5, y - 3, 10, 6), c_.setDash([])), txt))
        elif key == "exposed":
            items.append((_sw(EXPOSED_F, (0.6, 0.6, 0.6)), txt))
        else:
            items.append((_sw(LEVEL_FILL[key], (0.6, 0.6, 0.6)), txt))
    legend(c, items, y=yl)
    title(c, no, "ΑΝΟΨΗ – ΣΤΑΘΜΕΣ · ΔΟΚΟΙ · ΚΟΥΡΤΙΝΕΣ", A.SUB_AN01)


# ======================================================================== ΑΝ-02 κλιματισμός
def sheet_an02(c, no="ΑΝ-02"):
    v = view(c)
    clip_on(c)
    zones_fill(v, colored=False)
    plan(v)
    wall_unit_block(v, detailed=True)
    tall_marks(v)
    for name, r in A.DUCTS:
        v.rect(*r, fill=BLUE_F, stroke=BLUE, lw=0.5)
    for name, r in A.RETURN_BOX:
        v.rect(*r, fill=GREEN_F, stroke=GREEN, lw=0.5)
    for u in A.UNITS:
        x0, y0, x1, y1 = u["rect"]
        if u.get("concealed"):
            c.setDash([3, 1.5])
        v.rect(x0, y0, x1, y1, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=0.8)
        c.setDash([])
        v.line(x0, y0, x1, y1, color=BLUE, lw=0.4); v.line(x0, y1, x1, y0, color=BLUE, lw=0.4)
        v.text((x0 + x1) / 2, (y0 + y1) / 2 - 0.08, u["id"], size=5.6, font="Inter-Bold", color=BLUE, bg=True)
        v.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.10, u["btu"].replace(".000 Btu/h", "k"), size=4.4, color=BLUE, bg=True)
    for d in A.DIFFUSERS:
        x0, y0, x1, y1 = d["rect"]
        horiz = (x1 - x0) >= (y1 - y0)
        if d["kind"] in ("slot", "wall"):
            tx, ty = THROW_V[d["throw"]]
            if d["kind"] == "slot":
                v.rect(x0, y0, x1, y1, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.6)
                if horiz:
                    v.line(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, color=(1, 1, 1), lw=0.5)
                else:
                    v.line((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, color=(1, 1, 1), lw=0.5)
            else:
                v.rect(x0, y0, x1, y1, fill=BLUE, stroke=BLUE, lw=1.0)
            n = 5 if max(x1 - x0, y1 - y0) > 1.5 else 2
            for k in range(n):
                if n > 2:
                    t_ = 0.20 + k * ((x1 - x0 if horiz else y1 - y0) - 0.40) / (n - 1)
                else:
                    t_ = 0.25 if k == 0 else (x1 - x0 if horiz else y1 - y0) - 0.25
                if d["kind"] == "slot":     # από την ακμή + 0,02 ως ακμή + 0,40
                    if horiz:
                        e = y1 if ty > 0 else y0
                        arrow(v, x0 + t_, e + ty * 0.02, x0 + t_, e + ty * 0.40)
                    else:
                        e = x1 if tx > 0 else x0
                        arrow(v, e + tx * 0.02, y0 + t_, e + tx * 0.40, y0 + t_)
                else:                       # στόμιο τοίχου: από την παρειά, μήκος 0,42
                    if horiz:
                        e = y1 if ty > 0 else y0
                        arrow(v, x0 + t_, e, x0 + t_, e + ty * 0.42)
                    else:
                        e = x1 if tx > 0 else x0
                        arrow(v, e, y0 + t_, e + tx * 0.42, y0 + t_)
            lab = d.get("label", "%s · %s · ρίψη %s" % (d["id"], d["size"], THROW[d["throw"]]))
            if "lab_at" in d:
                lx, ly, lr = d["lab_at"]
            elif horiz:
                lx, ly, lr = (x0 + x1) / 2, (y1 + 0.70) if ty > 0 else (y0 - 0.62), 0
            else:
                lx, ly, lr = (x1 + 0.55) if tx > 0 else (x0 - 0.55), (y0 + y1) / 2, 90
            v.text(lx, ly, lab, size=4.6, rot=lr, color=BLUE, font="Inter-Medium", bg=True)
        else:
            v.rect(x0, y0, x1, y1, fill=None if d.get("access") else GREEN_F, stroke=GREEN, lw=0.8)
            if horiz:
                for k in range(1, 6):
                    xx = x0 + k * (x1 - x0) / 6
                    v.line(xx, y0, xx, y1, color=GREEN, lw=0.3)
    for h in A.HATCHES:
        x0, y0, x1, y1 = h["rect"]
        c.setDash([2, 1.2]); v.rect(x0, y0, x1, y1, stroke=DARK, lw=0.6); c.setDash([])
        v.line(x0, y0, x1, y1, color=DARK, lw=0.3); v.line(x0, y1, x1, y0, color=DARK, lw=0.3)
        lx, ly = h.get("lab_at", ((x0 + x1) / 2, (y0 + y1) / 2 + 0.36))
        v.text(lx, ly, "%s %s" % (h["id"], h["size"]), size=4.4, font="Inter-SemiBold", bg=True)
    for u in getattr(A, "SPLITS", []):
        split_sym(v, u)
        x0, y0, x1, y1 = u["rect"]
        tx, ty = THROW_V[u["throw"]]
        for k in (0.25, 0.75):
            if tx:
                xf = x1 if tx > 0 else x0
                yy = y0 + k * (y1 - y0)
                arrow(v, xf + tx * 0.03, yy, xf + tx * 0.75, yy)
            else:
                yf = y1 if ty > 0 else y0
                xx = x0 + k * (x1 - x0)
                arrow(v, xx, yf + ty * 0.03, xx, yf + ty * 0.75)
        lx, ly, lr = u["lab_at"]
        v.text(lx, ly, u.get("label", "%s split %s · %s…%s" % (u["id"], u["btu"].replace(".000 Btu/h", "k"), lfmt(u["bottom"]),
                                                               lfmt(u["bottom"] + u["h"]))),
               size=4.6, rot=lr, color=BLUE, font="Inter-SemiBold", bg=True)
    for od in getattr(A, "OUTDOOR", []):
        x0, y0, x1, y1 = od["rect"]
        c.setDash([3, 1.5]); v.rect(x0, y0, x1, y1, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=0.6); c.setDash([])
        lx, ly, lr = od["lab_at"]
        v.text(lx, ly, od["label"], size=4.2, rot=lr, color=BLUE, font="Inter-Medium", bg=True)
    for r in A.ROUTES:
        x, y = r["at"]
        X, Y = v.p(x, y)
        c.setStrokeColorRGB(*MAG); c.setFillColorRGB(1, 1, 1); c.setLineWidth(0.8)
        p = c.beginPath(); p.moveTo(X, Y + 5); p.lineTo(X + 5, Y); p.lineTo(X, Y - 5); p.lineTo(X - 5, Y); p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.setFont("Inter-SemiBold", 4.4); c.setFillColorRGB(*MAG); c.drawCentredString(X, Y - 1.5, r["id"])
    for rd in A.REFR_DRAW:
        col = COLORS[rd.get("color", "MAG")]
        for (a, b) in zip(rd["pts"], rd["pts"][1:]):
            v.line(*a, *b, color=col, lw=rd.get("lw", 0.9), dash=[4, 1.2, 1, 1.2])
    texts(v, getattr(A, "TEXTS_AN02", []))
    dims(v, getattr(A, "DIMS_AN02", []))
    for u in getattr(A, "WALL_UNITS", []):
        wall_unit_elev(c, u)
    clip_off(c)
    yl = side_notes(c, A.NOTES_AN02, y=770)
    kinds = {d["kind"] for d in A.DIFFUSERS}
    items = []
    if A.UNITS:
        items.append((lambda c_, x, y: (c_.setFillColorRGB(0.80, 0.88, 0.97), c_.setStrokeColorRGB(*BLUE), c_.rect(x - 5, y - 3, 10, 6, stroke=1, fill=1)), A.LEG_UNIT))
    if getattr(A, "SPLITS", []):
        items.append((lambda c_, x, y: (c_.setFillColorRGB(0.80, 0.88, 0.97), c_.setStrokeColorRGB(*BLUE), c_.rect(x - 5, y - 2, 10, 4, stroke=1, fill=1),
                                        c_.line(x - 4, y - 1, x + 4, y - 1)), A.LEG_SPLIT))
    if getattr(A, "WALL_UNITS", []):
        items.append((lambda c_, x, y: (c_.setFillColorRGB(0.93, 0.95, 0.99), c_.setStrokeColorRGB(*BLUE), c_.rect(x - 5, y - 3, 10, 6, stroke=1, fill=1),
                                        c_.setLineWidth(2), c_.line(x - 4, y - 3, x + 4, y - 3), c_.setLineWidth(0.5)), A.LEG_WALLUNIT))
    if A.DUCTS:
        items.append((_sw(BLUE_F, BLUE), "αεραγωγός / plenum προσαγωγής (μονωμένος, στο κενό)"))
    if "slot" in kinds:
        items.append((_sw((0.30, 0.45, 0.75), BLUE), A.LEG_SLOT))
    if "wall" in kinds:
        items.append((_sw(BLUE, BLUE), A.LEG_WALL))
    if "ret" in kinds:
        items.append((_sw(GREEN_F, GREEN), "Ε στόμιο / κιβώτιο επιστροφής με φίλτρο"))
    if A.HATCHES or getattr(A, "WALL_UNITS", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*DARK), c_.setDash([2, 1.2]), c_.rect(x - 4, y - 4, 8, 8), c_.setDash([])),
                      "ΘΕ θυρίδα επίσκεψης τετράγωνη – ΜΟΝΟ στην καναλάτη, στην πλευρά του ηλεκτρικού κουτιού (ιδιοκτήτης 09/11)"))
    if getattr(A, "OUTDOOR", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*BLUE), c_.setDash([3, 1.5]), c_.rect(x - 5, y - 3, 10, 6), c_.setDash([])), "εξωτερική μονάδα"))
    items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*MAG), c_.rect(x - 3, y - 3, 6, 6)), "Χ κατέβασμα / έξοδος σωληνώσεων – καμία οπή σε σκυρόδεμα"))
    legend(c, items, y=yl)
    title(c, no, "ΑΝΟΨΗ – ΚΛΙΜΑΤΙΣΜΟΣ · ΘΥΡΙΔΕΣ", A.SUB_AN02)


# ======================================================================== ΑΝ-03 φωτισμός / πυρανίχνευση
def spot_sym(v, kind, x, y):
    r = 0.05
    v.circle(x, y, r, fill=(1, 1, 1), stroke=ORANGE, lw=0.7)
    if kind == "s":
        v.circle(x, y, 0.017, fill=ORANGE)
    elif kind == "s44":
        v.line(x - r, y, x + r, y, color=ORANGE, lw=0.6)
    else:
        d = r * 0.7
        v.line(x - d, y - d, x + d, y + d, color=ORANGE, lw=0.6); v.line(x - d, y + d, x + d, y - d, color=ORANGE, lw=0.6)


def sheet_an03(c, no="ΑΝ-03"):
    v = view(c)
    clip_on(c)
    zones_fill(v, colored=False)
    slope_lines(v, labels=False)
    plan(v)
    wall_unit_block(v)
    roof_hatch(v)
    cables(v)
    tall_marks(v)
    # ζώνες κάλυψης / απόστασης ανιχνευτών 0,50
    for did, kind, x, y, room in A.DETECTORS:
        c.setDash([1.5, 1.5]); v.circle(x, y, 0.50, stroke=(0.90, 0.55, 0.55), lw=0.4); c.setDash([])
    for h in A.HATCHES:
        x0, y0, x1, y1 = h["rect"]
        c.setDash([2, 1.2]); v.rect(x0, y0, x1, y1, stroke=GREY, lw=0.4); c.setDash([])
    for d in A.DIFFUSERS:
        if d["kind"] == "slot" or (d["kind"] == "ret" and (d["rect"][2] - d["rect"][0]) > 0.5):
            v.rect(*d["rect"], stroke=(0.55, 0.65, 0.80), lw=0.4)
    for sid, kind, x, y, circ in A.SPOTS:
        spot_sym(v, kind, x, y)
        v.text(x + 0.08, y - 0.10, sid, size=3.8, color=ORANGE, anchor="l")
    for u in getattr(A, "SPLITS", []):
        split_sym(v, u, colored=False)
        x0, y0, x1, y1 = u["rect"]
        v.text((x0 + x1) / 2 + (0 if (x1 - x0) > (y1 - y0) else 0.0), (y0 + y1) / 2, u["id"], size=3.8, color=(0.45, 0.55, 0.70),
               rot=0 if (x1 - x0) > (y1 - y0) else 90)
    for t in getattr(A, "TRACKS", []):
        (ax, ay), (bx, by) = t["a"], t["b"]
        v.line(ax, ay, bx, by, color=ORANGE, lw=2.4)
        v.line(ax, ay, bx, by, color=(1, 1, 1), lw=0.6)
        X, Y = v.p(ax, ay)
        c.setFillColorRGB(*ORANGE); c.rect(X - 2.6, Y - 2.6, 5.2, 5.2, stroke=0, fill=1)
        n = t["n"]
        Lx, Ly = bx - ax, by - ay
        for k in range(n):
            f = (k + 0.5) / n
            hx, hy = ax + f * Lx, ay + f * Ly
            v.circle(hx, hy, 0.045, fill=(1, 1, 1), stroke=ORANGE, lw=0.7)
            v.circle(hx, hy, 0.016, fill=ORANGE)
        lx, ly, lr = t["lab_at"]
        v.text(lx, ly, t.get("label", "%s ράγα %s m · %d κεφαλές" % (t["id"], ("%.2f" % math.hypot(Lx, Ly)).replace(".", ","), n)),
               size=4.4, rot=lr, color=ORANGE, font="Inter-SemiBold", bg=True)
    for wid, kind, x, y, circ, txt in getattr(A, "WALL_LIGHTS", []):
        v.circle(x, y, 0.06, fill=(1, 1, 1), stroke=ORANGE, lw=0.8)
        v.circle(x, y, 0.025, fill=ORANGE)
        if kind == "w65":
            v.line(x - 0.06, y, x + 0.06, y, color=ORANGE, lw=0.5); v.line(x, y - 0.06, x, y + 0.06, color=ORANGE, lw=0.5)
        v.text(x, y - 0.13, wid, size=3.8, color=ORANGE, font="Inter-Medium", bg=True)
    for pid, x, y, circ, txt in A.PENDANTS:
        v.circle(x, y, 0.09, fill=(1, 1, 1), stroke=ORANGE, lw=0.8)
        v.circle(x, y, 0.035, fill=ORANGE)
        v.text(x, y - 0.22, pid, size=4.8, font="Inter-SemiBold", color=ORANGE, bg=True)
    for lid, a, b, circ, txt in A.LED:
        v.line(*a, *b, color=ORANGE, lw=1.4, dash=[4, 2])
        if txt:
            v.text((a[0] + b[0]) / 2, a[1] + 0.14, "%s %s" % (lid, txt), size=4.2, color=ORANGE, bg=True)
    for did, kind, x, y, room in A.DETECTORS:
        if kind == "smoke":
            v.rect(x - 0.07, y - 0.07, x + 0.07, y + 0.07, fill=(1, 1, 1), stroke=RED, lw=0.8)
            v.line(x - 0.07, y - 0.07, x + 0.07, y + 0.07, color=RED, lw=0.6); v.line(x - 0.07, y + 0.07, x + 0.07, y - 0.07, color=RED, lw=0.6)
        else:
            v.rect(x - 0.07, y - 0.07, x + 0.07, y + 0.07, fill=(1, 1, 1), stroke=RED, lw=0.8)
            v.circle(x, y, 0.025, fill=RED)
        v.text(x + 0.12, y + 0.14, "%s (%s · %s)" % (did, ("%.2f" % x).replace(".", ","), ("%.2f" % y).replace(".", ",")), size=4.2,
               color=RED, font="Inter-SemiBold", anchor="l", bg=True)
    for name, x, y, txt in A.AP:
        v.circle(x, y, 0.07, fill=(1, 1, 1), stroke=(0.20, 0.22, 0.55), lw=0.7); v.circle(x, y, 0.035, stroke=(0.20, 0.22, 0.55), lw=0.5)
        v.text(x, y + 0.16, "WiFi", size=4.0, color=(0.20, 0.22, 0.55))
    # κυκλώματα
    for txt, x, y in A.CIRCUITS:
        X, Y = v.p(x, y)
        c.setFillColorRGB(*ORANGE); c.roundRect(X - 3.6, Y - 3.6, 7.2, 7.2, 1.5, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont("Inter-SemiBold", 5.2); c.drawCentredString(X, Y - 1.8, txt)
    texts(v, getattr(A, "TEXTS_AN03", []))
    dims(v, getattr(A, "DIMS_AN03", []), size=4.2)
    clip_off(c)
    yl = side_notes(c, A.NOTES_AN03, y=770)
    sk = {s_[1] for s_ in A.SPOTS}
    items = []
    if "s" in sk:
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1, fill=1)), A.LEG_SPOT))
    if "s44" in sk:
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2.8, y, x + 2.8, y)), "χωνευτό spot IP44 (λουτρά)"))
    if "s65" in sk:
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2, y - 2, x + 2, y + 2), c_.line(x - 2, y + 2, x + 2, y - 2)), "χωνευτό spot IP65 (πάνω από ντους)"))
    if getattr(A, "TRACKS", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.setLineWidth(2.2), c_.line(x - 6, y, x + 6, y), c_.setLineWidth(0.5),
                                        c_.setFillColorRGB(*ORANGE), c_.rect(x - 7.5, y - 1.8, 3.6, 3.6, stroke=0, fill=1)), A.LEG_TRACK))
    if getattr(A, "WALL_LIGHTS", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 3.2), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1.3, fill=1)), A.LEG_WALLLIGHT))
    if getattr(A, "SPLITS", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(0.55, 0.65, 0.80), c_.rect(x - 5, y - 2, 10, 4)), "split τοίχου (για συντονισμό – βλ. φύλλο κλιματισμού)"))
    if getattr(A, "WALL_UNITS", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*GREY), c_.rect(x - 5, y - 3, 10, 6), c_.setStrokeColorRGB(0.55, 0.65, 0.80),
                                        c_.setLineWidth(1.4), c_.line(x - 4, y - 3, x + 4, y - 3), c_.setLineWidth(0.5)),
                      "ΤΚ τοίχος καναλάτης – στόμιο προσαγωγής (για συντονισμό – βλ. φύλλο κλιματισμού)"))
    if A.PENDANTS:
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 4), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1.6, fill=1)), "ΚΡΕΜ παροχή οροφής (κουτί + ενίσχυση ανάρτησης)"))
    if getattr(A, "CABLE_DRAW", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*CABLE_C), c_.setLineWidth(1.6), c_.setDash([6, 1.5, 1.5, 1.5]), c_.line(x - 7, y, x + 7, y),
                                        c_.setDash([]), c_.setLineWidth(0.5), c_.setFillColorRGB(*CABLE_C), c_.rect(x - 9, y - 2, 4, 4, stroke=0, fill=1)),
                      "καλώδια από το shaft Η/Μ (■ έξοδος πάνω από το μέτωπο-ντουλάπα Τ8-01) → ψευδοροφή κλιμακοστασίου → διαμέρισμα"))
    if getattr(A, "ROOF_HATCH", []):
        items.append((lambda c_, x, y: (c_.setStrokeColorRGB(*DARK), c_.rect(x - 4, y - 4, 8, 8), c_.line(x - 4, y - 4, x + 4, y + 4), c_.line(x - 4, y + 4, x + 4, y - 4)),
                      "καταπακτή πρόσβασης στη στέγη στο επίπεδο της ψευδοροφής (αρχιτέκτονας)"))
    led_item = [(lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.setDash([4, 2]), c_.line(x - 5, y, x + 5, y), c_.setDash([])), A.LEG_LED)] if A.LED else []
    legend(c, items + [
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.line(x - 3, y - 3, x + 3, y + 3), c_.line(x - 3, y + 3, x + 3, y - 3)), "ΑΚ ανιχνευτής καπνού (ΕΠ04 · EN 54-7)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.setFillColorRGB(*RED), c_.circle(x, y, 1.1, fill=1)), "ΑΘ θερμοδιαφορικός ανιχνευτής (κουζίνα · EN 54-5)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(0.9, 0.55, 0.55), c_.setDash([1.5, 1.5]), c_.circle(x, y, 4), c_.setDash([])), "ακτίνα 0,50 m γύρω από ανιχνευτή – κανένας τοίχος / φωτιστικό μέσα"),
    ] + led_item, y=yl)
    title(c, no, "ΑΝΟΨΗ – ΦΩΤΙΣΜΟΣ · ΠΥΡΑΝΙΧΝΕΥΣΗ", A.SUB_AN03)


# ======================================================================== ΑΝ-04 έλεγχος
STC = {"OK": (0.10, 0.50, 0.25), "ΟΡΙΑΚΟ": (0.85, 0.50, 0.05), "ΑΠΟΚΛΙΣΗ": RED, "ΕΓΚΕΚΡ.": (0.30, 0.40, 0.65)}


def block(c, x, y, w, head, lines, size=5.6, bullet="· "):
    c.setFont("Inter-Bold", 7.4); c.setFillColorRGB(*DARK); c.drawString(x, y, head)
    y -= 11
    for s in lines:
        col = DARK
        if isinstance(s, tuple):
            s, col = s
        ls = _wrap(bullet + s, "Inter", size, w)
        c.setFont("Inter", size); c.setFillColorRGB(*col)
        for j, l in enumerate(ls):
            c.drawString(x + (0 if j == 0 else 7), y, l); y -= size + 1.7
        y -= 1.8
    return y - 4


def sheet_an04(c, no="ΑΝ-04"):
    rows = checks.run()
    from collections import Counter
    cnt = Counter(r[5] for r in rows)
    # ---- αριστερή στήλη: προδιαγραφές
    x, y, w = 40, 805, 360
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(x, y, "ΣΥΜΜΟΡΦΩΣΗ ΜΕ ΤΙΣ ΠΡΟΔΙΑΓΡΑΦΕΣ (ιδιοκτήτης 07/11/2026)")
    y -= 14
    fs = getattr(A, "AN04_SIZE", 5.6)
    for head, txt in A.SPEC_AN04:
        c.setFont("Inter-SemiBold", 6.4); c.drawString(x, y, head)
        for j, l in enumerate(_wrap(txt, "Inter", fs, w - 70)):
            c.setFont("Inter", fs); c.drawString(x + 70, y - j * (fs + 1.7), l)
        y -= (fs + 1.7) * len(_wrap(txt, "Inter", fs, w - 70)) + 4
    y -= 4
    y = block(c, x, y, w, getattr(A, "APPROVED_TITLE", "ΕΓΚΕΚΡΙΜΕΝΕΣ ΑΠΟΚΛΙΣΕΙΣ (ιδιοκτήτης 07/11/2026)"), A.APPROVED, size=fs)
    y = block(c, x, y, w, A.CHANGES_TITLE, A.CHANGES, size=fs)
    if A.CHANGES_PREV:
        y = block(c, x, y, w, "ΠΡΟΗΓΟΥΜΕΝΗ ΑΝΑΘΕΩΡΗΣΗ", A.CHANGES_PREV, size=5.2)
    ol = []
    for code, kind, txt in A.OPEN:
        ol.append(("%s [%s] %s" % (code, kind, txt), RED if kind == "ΑΠΟΦΑΣΗ" else DARK))
    y = block(c, x, y, w, "ΑΝΟΙΚΤΑ ΣΗΜΕΙΑ", ol, size=getattr(A, "AN04_OPEN_SIZE", fs))
    # ---- δεξιά: πίνακας ελέγχων σε 2 στήλες
    X0, Y0 = 420, 805
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK)
    c.drawString(X0, Y0, "ΕΛΕΓΧΟΣ ΣΥΓΚΡΟΥΣΕΩΝ & ΣΤΑΘΜΩΝ – %d έλεγχοι · " % len(rows) +
                 " · ".join("%s %d" % (k, cnt.get(k, 0)) for k in ("OK", "ΟΡΙΑΚΟ", "ΕΓΚΕΚΡ.", "ΑΠΟΚΛΙΣΗ")))
    c.setFont("Inter", 5.4); c.setFillColorRGB(*GREY)
    c.drawString(X0, Y0 - 9, "Αυτόματος έλεγχος από το μοντέλο (code/anopseis/checks.py): στάθμες ↔ δοκοί · κενό μονάδων · θυρίδες · spots ↔ ζώνες / θυρίδες / μονάδες / "
                 "αεραγωγοί / κουρτινόθηκες · ανιχνευτές ↔ τοίχοι / φωτιστικά / στόμια · κουρτινόθηκες ↔ κουφώματα / δοκοί.")
    colw = 362; lh = 8.2 if len(rows) <= 150 else 7.6; fs_t = 5.2
    xs = [X0, X0 + colw + 12]
    half = (len(rows) + 1) // 2
    for ci, chunk in enumerate((rows[:half], rows[half:])):
        xx, yy = xs[ci], Y0 - 22
        c.setFont("Inter-SemiBold", 5.4); c.setFillColorRGB(*DARK)
        c.drawString(xx, yy, "ΚΩΔ."); c.drawString(xx + 38, yy, "ΚΑΤΑΣΤ."); c.drawString(xx + 80, yy, "ΣΤΟΙΧΕΙΟ"); c.drawString(xx + 250, yy, "ΜΕΤΡΗΣΗ")
        c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.4); c.line(xx, yy - 2, xx + colw, yy - 2)
        yy -= lh + 1
        for code, grp, item, crit, val, st in chunk:
            c.setFont("Inter", fs_t); c.setFillColorRGB(*DARK); c.drawString(xx, yy, code)
            c.setFont("Inter-SemiBold", fs_t); c.setFillColorRGB(*STC[st]); c.drawString(xx + 38, yy, st)
            c.setFont("Inter", fs_t); c.setFillColorRGB(*DARK)
            it = item
            while pdfmetrics.stringWidth(it, "Inter", fs_t) > 165: it = it[:-2]
            c.drawString(xx + 80, yy, it if it == item else it + "…")
            vv = val
            while pdfmetrics.stringWidth(vv, "Inter", fs_t) > colw - 252: vv = vv[:-2]
            c.drawString(xx + 250, yy, vv if vv == val else vv + "…")
            yy -= lh
    title(c, no, "ΑΝΟΨΗ – ΕΛΕΓΧΟΣ ΠΡΟΔΙΑΓΡΑΦΩΝ", "Συμμόρφωση · έλεγχος συγκρούσεων · αλλαγές %s · ανοικτά σημεία" % A.REV, scale="—")


# ======================================================================== ΑΝ-05 αναμονές καλωδίων στην πλάκα (σοφίτα R03)
STUB_C = (0.70, 0.12, 0.40)


def stub_sym(v, x, y, r=0.075):
    v.circle(x, y, r, fill=(1, 1, 1), stroke=STUB_C, lw=0.9)
    v.line(x - r * 1.5, y, x + r * 1.5, y, color=STUB_C, lw=0.5); v.line(x, y - r * 1.5, x, y + r * 1.5, color=STUB_C, lw=0.5)
    v.circle(x, y, 0.022, fill=STUB_C)


def _room_faces(x, y):
    """Απόσταση από τη Δ και τη Β παρειά του χώρου (ορθογώνιο της ζώνης που περιέχει το σημείο) – για έλεγχο μετά τους τοίχους."""
    for z in A.ZONES:
        for r in z["rects"]:
            if r[0] - 1e-6 <= x <= r[2] + 1e-6 and r[1] - 1e-6 <= y <= r[3] + 1e-6:
                return "%s: %s από Δ · %s από Β παρειά" % (z["room"].split(" – ")[0].capitalize(), ("%.2f" % (x - r[0])).replace(".", ","),
                                                           ("%.2f" % (y - r[1])).replace(".", ","))
    return "—"


def sheet_an05(c, no="ΑΝ-05"):
    v = view(c)
    c.saveState(); pth = c.beginPath(); pth.rect(22, 288, 1004 - 22, 819 - 288); c.clipPath(pth, stroke=0, fill=0)
    zones_fill(v, colored=False)
    slope_lines(v, labels=False)
    plan(v)
    wall_unit_block(v)
    slope_lines(v, labels=True)
    for t in A.TRACKS:                                   # ράγες αχνά (σε ποιο σημείο κουμπώνει η αναμονή)
        v.line(*t["a"], *t["b"], color=(0.96, 0.82, 0.62), lw=2.6)
    for did, kind, x, y, room in A.DETECTORS:
        v.rect(x - 0.07, y - 0.07, x + 0.07, y + 0.07, stroke=(0.92, 0.62, 0.62), lw=0.6)
    # γωνίες αναφοράς (σκυρόδεμα που υπάρχει κατά τη σκυροδέτηση)
    used = {sb["ref"] for sb in A.STUBS}
    for k, (rx, ry, name) in A.REFS.items():
        if k not in used:
            continue
        X, Y = v.p(rx, ry)
        c.setFillColorRGB(*STUB_C)
        pp = c.beginPath(); pp.moveTo(X, Y); pp.lineTo(X + 5, Y - 8); pp.lineTo(X - 5, Y - 8); pp.close(); c.drawPath(pp, stroke=0, fill=1)
        lx, ly = A.REF_LAB.get(k, (rx + 0.10, ry + 0.30))
        v.text(lx, ly, "▲ %s (0,00)" % name, size=4.4, color=STUB_C, font="Inter-SemiBold", anchor="l", bg=True)
    for sb in A.STUBS:
        x, y = sb["at"]
        rx, ry, _ = A.REFS[sb["ref"]]
        v.line(rx, ry, rx, y, color=(0.85, 0.55, 0.72), lw=0.35, dash=[2, 1.5])
        v.line(rx, y, x, y, color=(0.85, 0.55, 0.72), lw=0.35, dash=[2, 1.5])
        if sb.get("drop"):
            dx, dy = sb["drop"]
            v.line(x, y, dx, y, color=STUB_C, lw=0.7, dash=[5, 1.5]); v.line(dx, y, dx, dy, color=STUB_C, lw=0.7, dash=[5, 1.5])
            X, Y = v.p(dx, dy); c.setFillColorRGB(*STUB_C); c.rect(X - 2.4, Y - 2.4, 4.8, 4.8, stroke=0, fill=1)
        stub_sym(v, x, y)
        lx, ly, anc = A.STUB_LAB.get(sb["id"], (x + 0.14, y - 0.16, "l"))
        v.text(lx, ly, "%s · %s" % (sb["id"], sb["what"]), size=4.8, color=STUB_C, font="Inter-Bold", anchor=anc, bg=True)
        v.text(lx, ly + 0.16, sb["ref_txt"].split(": ")[1] + " (από " + A.REFS[sb["ref"]][2].replace("γωνία ", "γ. ") + ")", size=4.2,
               color=DARK, font="Inter-Medium", anchor=anc, bg=True)
    for dx, dy, txt, anc in getattr(A, "DROP_LAB", []):
        v.text(dx, dy, txt, size=4.0, color=STUB_C, anchor=anc, bg=True)
    texts(v, getattr(A, "TEXTS_AN05", []))
    c.restoreState()
    # ---- πίνακας
    x0, y0 = 34, 276
    cols = [(0, "ΚΩΔ."), (30, "ΤΡΟΦΟΔΟΤΕΙ"), (128, "x · y μοντέλου"), (184, "ΣΤΟ ΚΑΛΟΥΠΙ – από γωνία σκυροδέματος"),
            (382, "ΜΕΤΑ ΤΟΥΣ ΤΟΙΧΟΥΣ – από τελικές παρειές"), (560, "ΚΑΤΩ ΠΑΡΕΙΑ ΠΛΑΚΑΣ"), (636, "ΚΑΘΟΔΟΣ ΣΩΛΗΝΑ (πρόταση – κατά τα ηλεκτρολογικά)")]
    c.setFont("Inter-Bold", 7.2); c.setFillColorRGB(*DARK)
    c.drawString(x0, y0 + 10, "ΠΙΝΑΚΑΣ ΑΝΑΜΟΝΩΝ – κουτί οροφής για σκυρόδεμα Ø 80 στον ξυλότυπο + σωλήνας Ø 20 με οδηγό μέσα στην πλάκα")
    c.setFont("Inter-SemiBold", 5.4)
    for dx, t in cols:
        c.drawString(x0 + dx, y0, t)
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.5); c.line(x0, y0 - 3, 1000, y0 - 3)
    yy = y0 - 12
    c.setFont("Inter", 5.4)
    for sb in A.STUBS:
        x, y = sb["at"]
        h, h8 = checks.ceil_at(x, y), (A.SLAB8_FN(x, y) if hasattr(A, "SLAB8_FN") else None)
        drop = ("(%s · %s) %s" % (("%.2f" % sb["drop"][0]).replace(".", ","), ("%.2f" % sb["drop"][1]).replace(".", ","), sb["drop_txt"])
                if sb.get("drop") else sb["drop_txt"])
        vals = [sb["id"], sb["what"], ("%.2f · %.2f" % (x, y)).replace(".", ","), sb["ref_txt"], _room_faces(x, y),
                "%s (Σ8 %s)" % (fmt(h), fmt(h8)) if h8 else fmt(h), drop]
        for (dx, _), val in zip(cols, vals):
            c.setFillColorRGB(*(STUB_C if dx == 0 else DARK)); c.setFont("Inter-SemiBold" if dx == 0 else "Inter", 5.4)
            w = 360 if dx == 636 else ((cols[[d for d, _ in cols].index(dx) + 1][0] - dx - 4) if dx != 636 else 360)
            vv = val
            while pdfmetrics.stringWidth(vv, "Inter", 5.4) > w:
                vv = vv[:-2]
            c.drawString(x0 + dx, yy, vv if vv == val else vv + "…")
        yy -= 10.5
    yl = side_notes(c, A.NOTES_AN05, y=770)
    items = [(lambda c_, x, y: (c_.setStrokeColorRGB(*STUB_C), c_.circle(x, y, 3.2), c_.line(x - 5, y, x + 5, y), c_.line(x, y - 5, x, y + 5),
                                c_.setFillColorRGB(*STUB_C), c_.circle(x, y, 1, fill=1)), "ΑΝ αναμονή: κουτί οροφής στον ξυλότυπο (κέντρο = θέση φωτιστικού / ανιχνευτή)"),
             (lambda c_, x, y: (c_.setFillColorRGB(*STUB_C), c_.rect(x - 2.4, y - 2.4, 4.8, 4.8, stroke=0, fill=1)), "κάθοδος σωλήνα μέσα στη γραμμή του μελλοντικού τοίχου γυψοσανίδας"),
             (lambda c_, x, y: (c_.setStrokeColorRGB(*STUB_C), c_.setDash([5, 1.5]), c_.line(x - 6, y, x + 6, y), c_.setDash([])), "σωλήνας Ø 20 μέσα στην πλάκα (ορθογωνική όδευση)"),
             (lambda c_, x, y: (c_.setFillColorRGB(*STUB_C), c_.beginPath(), c_.drawPath(_tri(c_, x, y), stroke=0, fill=1)), "γωνία σκυροδέματος αναφοράς (0,00) – μέτρηση Α / Δ και Ν"),
             (lambda c_, x, y: (c_.setStrokeColorRGB(0.96, 0.82, 0.62), c_.setLineWidth(2.4), c_.line(x - 6, y, x + 6, y), c_.setLineWidth(0.5)), "ράγα (για προσανατολισμό – βλ. φύλλο φωτισμού)")]
    legend(c, items, y=yl)
    title(c, no, "ΑΝΑΜΟΝΕΣ ΚΑΛΩΔΙΩΝ ΣΤΗΝ ΠΛΑΚΑ ΣΤΕΓΗΣ Σ8", A.SUB_AN05)


def _tri(c_, x, y):
    pp = c_.beginPath(); pp.moveTo(x, y + 4); pp.lineTo(x + 4, y - 3); pp.lineTo(x - 4, y - 3); pp.close()
    return pp


SHEETS = (sheet_an01, sheet_an02, sheet_an03, sheet_an04)


def sheets_for():
    """Φύλλα του δεμένου ορόφου: ΑΝ-01…04 + ΑΝ-05 αναμονών όπου υπάρχουν (σοφίτα)."""
    return SHEETS + ((sheet_an05,) if getattr(A, "STUBS", None) else ())
