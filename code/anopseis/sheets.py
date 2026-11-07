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
        v.text((x0 + x1) / 2, (y0 + y1) / 2, "έως οροφή", size=3.8, color=GREY, font="Inter-Medium", bg=True)


def level_tag(v, x, y, lvl, size=6.2, sub=None):
    s = lfmt(lvl)
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


# ======================================================================== ΑΝ-01 στάθμες
def sheet_an01(c, no="ΑΝ-01"):
    v = view(c)
    clip_on(c)
    zones_fill(v, colored=True)
    for cu in A.CURTAINS:
        v.rect(*cu["rect"], fill=POCKET_F)
    plan(v)
    tall_marks(v)
    # κουρτινόθηκες: οδηγοί
    for cu in A.CURTAINS:
        x0, y0, x1, y1 = cu["rect"]
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
                v.line(x0 + 0.02, yy, x1 - 0.02, yy, color=(0.35, 0.42, 0.50), lw=0.5, dash=[4, 1.2, 1, 1.2])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lab = "%s · %s · %d×%d" % (cu["id"], cu["win"], round(cu["width"] * 100), round(cu["depth"] * 100))
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
        level_tag(v, x, y, z["level"], sub=z.get("tag_sub", sub))
    texts(v, getattr(A, "TEXTS_AN01", []))
    dims(v, getattr(A, "DIMS_AN01", []))
    clip_off(c)
    yl = side_notes(c, A.NOTES_AN01, y=770)
    items = []
    for key, txt in A.LEGEND_AN01:
        if key == "pocket":
            items.append((_sw(POCKET_F, (0.35, 0.42, 0.50)), txt))
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
    clip_off(c)
    yl = side_notes(c, A.NOTES_AN02, y=770)
    legend(c, [
        (lambda c_, x, y: (c_.setFillColorRGB(0.80, 0.88, 0.97), c_.setStrokeColorRGB(*BLUE), c_.rect(x - 5, y - 3, 10, 6, stroke=1, fill=1)), A.LEG_UNIT),
        (_sw(BLUE_F, BLUE), "αεραγωγός / plenum προσαγωγής (μονωμένος, στο κενό)"),
        (_sw((0.30, 0.45, 0.75), BLUE), A.LEG_SLOT),
        (_sw(BLUE, BLUE), A.LEG_WALL),
        (_sw(GREEN_F, GREEN), "Ε στόμιο / κιβώτιο επιστροφής με φίλτρο"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*DARK), c_.setDash([2, 1.2]), c_.rect(x - 4, y - 4, 8, 8), c_.setDash([])), "ΘΕ θυρίδα επίσκεψης (αφανής, βαφόμενη)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*MAG), c_.rect(x - 3, y - 3, 6, 6)), "Χ κατέβασμα / έξοδος σωληνώσεων – καμία οπή σε σκυρόδεμα"),
    ], y=yl)
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
    plan(v)
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
    legend(c, [
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1, fill=1)), A.LEG_SPOT),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2.8, y, x + 2.8, y)), "χωνευτό spot IP44 (λουτρά)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2, y - 2, x + 2, y + 2), c_.line(x - 2, y + 2, x + 2, y - 2)), "χωνευτό spot IP65 (πάνω από ντους)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 4), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1.6, fill=1)), "ΚΡΕΜ παροχή οροφής (κουτί + ενίσχυση ανάρτησης)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.line(x - 3, y - 3, x + 3, y + 3), c_.line(x - 3, y + 3, x + 3, y - 3)), "ΑΚ ανιχνευτής καπνού (ΕΠ04 · EN 54-7)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.setFillColorRGB(*RED), c_.circle(x, y, 1.1, fill=1)), "ΑΘ θερμοδιαφορικός ανιχνευτής (κουζίνα · EN 54-5)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(0.9, 0.55, 0.55), c_.setDash([1.5, 1.5]), c_.circle(x, y, 4), c_.setDash([])), "ακτίνα 0,50 m γύρω από ανιχνευτή – κανένας τοίχος / φωτιστικό μέσα"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.setDash([4, 2]), c_.line(x - 5, y, x + 5, y), c_.setDash([])), A.LEG_LED),
    ], y=yl)
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


SHEETS = (sheet_an01, sheet_an02, sheet_an03, sheet_an04)
