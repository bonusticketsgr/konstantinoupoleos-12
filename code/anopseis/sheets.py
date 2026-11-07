"""Φύλλα ανόψης οροφής Β1 (Α΄·Β΄·Γ΄) – A3, 1:50 · ΑΝ-01 στάθμες · ΑΝ-02 κλιματισμός · ΑΝ-03 φωτισμός/πυρανίχνευση · ΑΝ-04 έλεγχος."""
import math
import b1_anopsi as A
import checks
import sheet_t01                                   # code/toixopoiies (το b1_anopsi βάζει τη διαδρομή)
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow
from reportlab.pdfbase import pdfmetrics

S = 72 / 25.4 * 1000 / 50          # 1:50 → 56,693 pt/m
OX, OY = 215.43, 87.87              # ίδια θέση με το R10
BASE_TXT = "Βάση: τοιχοποιίες Β1 R25 · ξυλότυπος Σ5 (+9,85) · ανόψη R10"
SHEET_FLOOR = "Α΄ · Β΄ · Γ΄ ΟΡΟΦΟΣ – Β1 (τυπικός όροφος)"

ORANGE = (0.80, 0.47, 0.05)
RED = (0.78, 0.10, 0.12)
BLUE = (0.05, 0.36, 0.66)
BLUE_F = (0.86, 0.92, 0.98)
GREEN = (0.05, 0.52, 0.42)
GREEN_F = (0.86, 0.95, 0.91)
MAG = (0.80, 0.10, 0.50)
BEAM = (0.62, 0.30, 0.16)
LEVEL_FILL = {2.67: (0.985, 0.98, 0.97), 2.65: (0.985, 0.98, 0.97), 2.55: (0.94, 0.91, 0.85), 2.45: (0.91, 0.87, 0.79),
              2.40: (0.86, 0.81, 0.71)}
NEUTRAL = (0.965, 0.96, 0.95)
POCKET_F = (0.88, 0.93, 0.98)

ZONE_LABEL_AT = {"Ζ1": (5.20, 7.95), "Ζ2": (3.10, 5.62), "Ζ3": (11.45, 8.95), "Ζ4": (4.00, 4.12), "Ζ5": (5.72, 1.62),
                 "Ζ6": (1.95, 4.62), "Ζ7": (2.75, 2.05), "Ζ8": (3.55, 0.40), "Ζ9": (4.50, 2.75), "Ζ10": (7.90, 2.95),
                 "Ζ11": (7.90, 4.95)}


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


def view(c):
    return View(c, OX, OY, S)


def zones_fill(v, colored=True):
    for z in A.ZONES:
        col = LEVEL_FILL[z["level"]] if colored else NEUTRAL
        for r in z["rects"]:
            v.rect(*r, fill=col)
        if z.get("box"):
            for r in z["rects"]:
                v.hatch([[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]], 0.10, 45, (0.70, 0.62, 0.50), 0.3)


def plan(v):
    sheet_t01.M = A.W
    sheet_t01.draw_plan(v, with_labels=False, with_dims=False, with_furniture=True, with_text=False)


def tall_marks(v):
    for name, (x0, y0, x1, y1) in A.TALL:
        v.text((x0 + x1) / 2, (y0 + y1) / 2 + (0.0 if (x1 - x0) > 1 else 0), "έως οροφή", size=3.8, color=GREY, font="Inter-Medium", bg=True)


def level_tag(v, x, y, lvl, size=6.2, sub=None):
    s = "▼ " + fmt(lvl)
    v.text(x, y, fmt(lvl), size=size, font="Inter-Bold", color=DARK, bg=True)
    X, Y = v.p(x, y)
    w = pdfmetrics.stringWidth(fmt(lvl), "Inter-Bold", size)
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
    frame_and_title(c, no, theme, sub, SHEET_FLOOR, BASE_TXT, scale, A.REV, A.DATE)


# ======================================================================== ΑΝ-01 στάθμες
def sheet_an01(c):
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
        for o in offs:
            if vert:
                xx = x0 + o if x0 < 5 else x1 - o
                v.line(xx, y0 + 0.02, xx, y1 - 0.02, color=(0.35, 0.42, 0.50), lw=0.5, dash=[4, 1.2, 1, 1.2])
            else:
                yy = y1 - o
                v.line(x0 + 0.02, yy, x1 - 0.02, yy, color=(0.35, 0.42, 0.50), lw=0.5, dash=[4, 1.2, 1, 1.2])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lab = "%s · %s · %d×%d" % (cu["id"], cu["win"], round(cu["width"] * 100), round(cu["depth"] * 100))
        if vert:
            v.text(x0 - 0.14 if x0 < 5 else x1 + 0.14, cy + 0.6, lab, size=4.6, rot=90, color=(0.25, 0.35, 0.50), font="Inter-Medium", bg=True)
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
    BL = {"Δ1.1": (1.95, 0.66, 0), "Δ1.4": (8.00, 0.62, 0), "Δ9.5": (9.88, 1.90, 90), "Δ6.1": (0.95, 3.95, 90),
          "Δ3.1": (2.55, 5.00, 0), "Δ9.1": (9.55, 6.95, 90), "Δ7.1": (1.55, 7.20, 90), "Δ4.4": (6.20, 9.32, 0),
          "Δ4.6": (11.10, 9.32, 0), "Δ12.2": (11.40, 7.72, 0), "Δ10.2": (13.48, 6.40, 90), "Δ10.1": (13.22, 8.50, 90)}
    for name, sec, *_ in A.BEAMS:
        x, y, r = BL[name]
        v.text(x, y, "%s %s · Κ.Π. %s" % (name, sec, fmt(A.beam_soffit(sec))), size=4.4, rot=r, color=BEAM, font="Inter-Medium", bg=True)
    # ετικέτες στάθμης
    for z in A.ZONES:
        x, y = ZONE_LABEL_AT[z["id"]]
        void = round((A.SLABS[z["slab"]] - z["level"]) * 100)
        level_tag(v, x, y, z["level"], sub="%s · κενό %d cm" % (z["id"], void) if not z.get("box") else "κουτί ντουλάπας")
    v.text(3.10, 5.87, "ΧΑΜΗΛΩΣΗ ΚΑΝΑΛΑΤΟΥ ΚΜ1", size=4.6, color=GREY, font="Inter-Medium")
    v.text(7.90, 4.80, "σανίδα κάτω από Δ3.1", size=4.0, color=GREY)
    # διαστάσεις ζωνών
    for o, p, pts in [("V", 8.30, [5.15, 6.30]), ("V", 4.40, [0.165, 0.80]), ("H", 1.30, [4.20, 4.80]),
                      ("V", 6.80, [4.85, 5.05]), ("H", 8.70, [1.705, 1.905, 9.40]), ("V", 1.60, [0.80, 3.25]),
                      ("H", 0.95, [9.145, 9.365])]:
        v.dim_chain(o, p, pts, size=4.4, side=-1)
    clip_off(c)
    yl = side_notes(c, [
        "Στάθμες από το τελικό δάπεδο του ορόφου (Β΄ +6,90). Πάνω παρειά πλάκας +2,95· κάτω παρειά Π3 h18 +2,77 · Π8 h20 +2,75 · Π10 h15 +2,80.",
        "Κανόνας: πουθενά ψευδοροφή κάτω από κάτω παρειά δοκού· όπου «περασιά» η γυψοσανίδα στη δοκό προσθέτει ≈ 1,5 cm.",
        "Αλλαγές στάθμης ΜΟΝΟ: χαμήλωση ΚΜ1 · γραμμή δοκού Δ9.1 (καθιστικό → κουζίνα) · γραμμή Δ1.1 (κεφαλάρι) · μετώπη ντουλάπας Υπν.1 (Π3) · σανίδα κάτω από Δ3.1 στο Υπν.2.",
        "Κουρτινόθηκες: 20 × 10 cm (ΚΡ4 22 cm για το ανοιγοανακλινόμενο W2.06), σε όλο το μήκος του τοίχου, δίπλα (όχι κάτω) από τις δοκούς όψης.",
        "R11: Υπν.1 ως το μέτωπο ντουλάπας 4,20 · λουτρό 5,05–6,40 · ΚΡ4 από 1,35.",
    ], y=770)
    legend(c, [
        (_sw(LEVEL_FILL[2.67], (0.6, 0.6, 0.6)), "+2,65 / +2,67 βασική = 10 cm κάτω από την πλάκα (spot σώμα ≤ 75 mm)"),
        (_sw(LEVEL_FILL[2.55], (0.6, 0.6, 0.6)), "+2,55 περασιά με δοκό 40 (κεφαλάρι Υπν.1)"),
        (_sw(LEVEL_FILL[2.45], (0.6, 0.6, 0.6)), "+2,45 περασιά με δοκό 50: χαμήλωση ΚΜ1 · χωλ · λουτρό · κουζίνα"),
        (_sw(LEVEL_FILL[2.40], (0.6, 0.6, 0.6)), "+2,40 περασιά με δοκό 55 (λουτρό γονέων)"),
        (_sw(POCKET_F, (0.35, 0.42, 0.50)), "ΚΡ εσοχή κουρτίνας ανοιχτή ως την πλάκα · 2 οδηγοί"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*BEAM), c_.setDash([5, 2]), c_.rect(x - 5, y - 3, 10, 6), c_.setDash([])), "δοκός (Σ5) · Κ.Π. = κάτω παρειά από Τ.Δ."),
    ], y=yl)
    title(c, "ΑΝ-01", "ΑΝΟΨΗ – ΣΤΑΘΜΕΣ · ΔΟΚΟΙ · ΚΟΥΡΤΙΝΕΣ", "Στάθμες ψευδοροφής · δοκοί Σ5 · εσοχές κουρτινών")


# ======================================================================== ΑΝ-02 κλιματισμός
def sheet_an02(c):
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
        v.rect(x0, y0, x1, y1, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=0.8)
        v.line(x0, y0, x1, y1, color=BLUE, lw=0.4); v.line(x0, y1, x1, y0, color=BLUE, lw=0.4)
        v.text((x0 + x1) / 2, (y0 + y1) / 2 - 0.08, u["id"], size=5.6, font="Inter-Bold", color=BLUE, bg=True)
        v.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.10, u["btu"].replace(".000 Btu/h", "k"), size=4.4, color=BLUE, bg=True)
    for d in A.DIFFUSERS:
        x0, y0, x1, y1 = d["rect"]
        if d["kind"] == "slot":
            v.rect(x0, y0, x1, y1, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.6)
            v.line(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, color=(1, 1, 1), lw=0.5)
            for k in range(5):
                xx = x0 + 0.20 + k * (x1 - x0 - 0.40) / 4
                arrow(v, xx, y1 + 0.02, xx, y1 + 0.40)
            v.text((x0 + x1) / 2, y1 + 0.70, "%s · %s · ρίψη νότια" % (d["id"], d["size"]), size=4.6, color=BLUE, font="Inter-Medium", bg=True)
        elif d["kind"] == "wall":
            v.rect(x0, y0, x1, y1, fill=BLUE, stroke=BLUE, lw=1.0)
            sgn = -1 if d["throw"] == "Δ" else 1
            xs = x0 if sgn < 0 else x1
            for yy in (y0 + 0.25, y1 - 0.25):
                arrow(v, xs, yy, xs + sgn * 0.42, yy)
            v.text(xs + sgn * 0.30, (y0 + y1) / 2, "%s 1000×150" % d["id"], size=4.6, rot=90, color=BLUE, font="Inter-Medium", bg=True)
        else:
            v.rect(x0, y0, x1, y1, fill=None if d.get("access") else GREEN_F, stroke=GREEN, lw=0.8)
            if (x1 - x0) > (y1 - y0):
                for k in range(1, 6):
                    xx = x0 + k * (x1 - x0) / 6
                    v.line(xx, y0, xx, y1, color=GREEN, lw=0.3)
    v.text(7.28, 5.20, "Ε1 1350×300 ανοιγόμενη = θυρίδα ΚΜ1", size=4.4, color=GREEN, font="Inter-Medium", bg=True)
    v.text(3.75, 3.12, "Ε2 600×150", size=4.2, color=GREEN, font="Inter-Medium", bg=True)
    v.text(6.70, 3.85, "Ε3 600×150", size=4.2, color=GREEN, font="Inter-Medium", rot=90, bg=True)
    for h in A.HATCHES:
        x0, y0, x1, y1 = h["rect"]
        c.setDash([2, 1.2]); v.rect(x0, y0, x1, y1, stroke=DARK, lw=0.6); c.setDash([])
        v.line(x0, y0, x1, y1, color=DARK, lw=0.3); v.line(x0, y1, x1, y0, color=DARK, lw=0.3)
        v.text((x0 + x1) / 2, y0 - 0.08 if h["id"] in ("ΘΕ4", "ΘΕ5") else (y0 + y1) / 2 + 0.36, "%s %s" % (h["id"], h["size"]), size=4.4,
               font="Inter-SemiBold", bg=True)
    for r in A.ROUTES:
        x, y = r["at"]
        X, Y = v.p(x, y)
        c.setStrokeColorRGB(*MAG); c.setFillColorRGB(1, 1, 1); c.setLineWidth(0.8)
        p = c.beginPath(); p.moveTo(X, Y + 5); p.lineTo(X + 5, Y); p.lineTo(X, Y - 5); p.lineTo(X - 5, Y); p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.setFont("Inter-SemiBold", 4.4); c.setFillColorRGB(*MAG); c.drawCentredString(X, Y - 1.5, r["id"])
    v.text(9.30, 7.20, "Χ1 κατέβασμα ψυκτικών ΚΜ1 – ΑΝΟΙΚΤΟ Α1 (ΑΝ-04)", size=4.4, color=MAG, font="Inter-SemiBold", anchor="r", bg=True)
    v.text(10.10, 0.35, "Χ3 πεσσός Τ1-05 → εξωτ. μονάδα ΒΑ εξώστη", size=4.4, color=MAG, font="Inter-Medium", anchor="l", bg=True)
    # διαδρομές ψυκτικών ΚΜ2 / ΚΜ3 (ενδεικτικά, στο κενό)
    for (a, b) in [((4.60, 3.42), (4.60, 3.30)), ((5.83, 3.42), (5.83, 3.20)), ((5.83, 3.20), (6.30, 3.20)), ((6.30, 3.20), (6.30, 0.92)),
                   ((6.30, 0.92), (9.30, 0.92)), ((9.30, 0.92), (9.57, 0.65))]:
        v.line(*a, *b, color=(0.25, 0.55, 0.75), lw=0.5, dash=[4, 1.2, 1, 1.2])
    v.text(7.80, 1.05, "2 ζεύγη ψυκτικών ΚΜ2 / ΚΜ3 (στο κενό χωλ → λουτρού → πάνω από τη ντουλάπα Υπν.2)", size=4.0, color=(0.25, 0.55, 0.75), bg=True)
    for o, p, pts in [("H", 6.62, [1.905, 2.70, 4.70, 5.30, 7.30, 9.40]), ("H", 5.08, [6.60, 7.80, 7.95, 9.40]),
                      ("H", 4.22, [3.30, 4.295, 4.895, 5.525, 6.125, 6.40]), ("V", 3.95, [0.80, 1.20, 2.20, 3.25]),
                      ("V", 6.80, [1.35, 2.00, 3.00]), ("H", 2.62, [5.05, 5.90, 6.30, 6.40])]:
        v.dim_chain(o, p, pts, size=4.4, side=-1)
    clip_off(c)
    yl = side_notes(c, [
        "Χώρος μονάδων (προδ. 1): χαμήλωση ΚΜ1 +2,45 κάτω από Π8 +2,75 = 30 cm· χωλ +2,45 κάτω από Π3 +2,77 = 32 cm.",
        "ΚΜ1: μονάδα ≤ 245 mm + στηρίγματα 10 mm + σκελετός/γυψοσανίδα 40 mm = 295 ≤ 300 → ΟΡΙΑΚΟ (5 mm). Μονάδα με πλαϊνά στηρίγματα ανάρτησης· προτιμότερο ύψος ≤ 235 mm.",
        "ΚΜ2 / ΚΜ3: 200 + 10 + 40 = 250 ≤ 320 → περιθώριο 70 mm (κλίση συμπυκνωμάτων / αντλία).",
        "Πρόσβαση: ΚΜ1 από την ανοιγόμενη Ε1 · ΚΜ2 / ΚΜ3 από ΘΕ2 / ΘΕ3 60×60 ακριβώς κάτω από τις μονάδες.",
        "R11: αεραγωγός ΚΜ2 4,25–4,75 και Π3 στο μέτωπο της ντουλάπας 4,20 (ντουλάπα R18 4,20–4,80) · ΘΕ4 έξω από το ντους.",
        "Συμπυκνώματα με αντλία μονάδας μαζί με τα ψυκτικά → σιφώνι / υδρορροή εξώστη (επιβεβαίωση υδραυλικού).",
    ], y=770)
    legend(c, [
        (lambda c_, x, y: (c_.setFillColorRGB(0.80, 0.88, 0.97), c_.setStrokeColorRGB(*BLUE), c_.rect(x - 5, y - 3, 10, 6, stroke=1, fill=1)), "ΚΜ καναλάτη μονάδα (slim: ΚΜ1 ≤ 245 mm · ΚΜ2/ΚΜ3 ≤ 200 mm)"),
        (_sw(BLUE_F, BLUE), "αεραγωγός / plenum προσαγωγής (μονωμένος, στο κενό)"),
        (_sw((0.30, 0.45, 0.75), BLUE), "Π1 / Π2 γραμμικό slot οροφής 2 σχισμών, ρυθμιζόμενη ρίψη"),
        (_sw(BLUE, BLUE), "Π3 / Π4 γραμμικό στόμιο 1000×150 σε μετώπη / τοίχο (εγκεκριμένο)"),
        (_sw(GREEN_F, GREEN), "Ε στόμιο / κιβώτιο επιστροφής με φίλτρο"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*DARK), c_.setDash([2, 1.2]), c_.rect(x - 4, y - 4, 8, 8), c_.setDash([])), "ΘΕ θυρίδα επίσκεψης (αφανής, βαφόμενη)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*MAG), c_.rect(x - 3, y - 3, 6, 6)), "Χ κατέβασμα / έξοδος σωληνώσεων – καμία οπή σε σκυρόδεμα"),
    ], y=yl)
    title(c, "ΑΝ-02", "ΑΝΟΨΗ – ΚΛΙΜΑΤΙΣΜΟΣ · ΘΥΡΙΔΕΣ", "Καναλάτες μονάδες · αεραγωγοί · στόμια · θυρίδες επίσκεψης · ψυκτικά")


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


def sheet_an03(c):
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
        if d["kind"] in ("slot", "ret") and (d["rect"][2] - d["rect"][0]) > 0.5:
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
        v.text((a[0] + b[0]) / 2, a[1] + 0.14, "%s κρυφό LED πίσω από το κρεβάτι (σχισμή 8 cm)" % lid, size=4.2, color=ORANGE, bg=True)
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
    for txt, x, y in [("α", 4.30, 7.85), ("β", 9.15, 5.75), ("γ", 7.95, 7.25), ("ε", 12.30, 8.80), ("ζ", 2.75, 1.85), ("η", 4.45, 4.65),
                      ("θ", 4.40, 0.42), ("κ", 7.83, 2.30), ("μ", 6.05, 1.25), ("ν", 2.05, 4.75)]:
        X, Y = v.p(x, y)
        c.setFillColorRGB(*ORANGE); c.roundRect(X - 3.6, Y - 3.6, 7.2, 7.2, 1.5, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont("Inter-SemiBold", 5.2); c.drawCentredString(X, Y - 1.8, txt)
    v.text(5.20, 8.35, "ΚΑΘΙΣΤΙΚΟ – ΤΡΑΠΕΖΑΡΙΑ: χωρίς spots – παροχές ΚΡΕΜ0 / ΚΡΕΜ1 (απόφαση ιδιοκτήτη R02, επιβεβαίωση 07/11)",
           size=4.6, color=GREY, font="Inter-Medium", bg=True)
    for o, p, pts in [("H", 2.10, [1.335, 1.765, 3.77, 4.20]), ("V", 2.30, [0.80, 1.55, 2.65, 3.25]),
                      ("H", 3.05, [6.50, 7.13, 8.53, 9.145]), ("V", 8.90, [1.35, 1.85, 4.25, 4.85]),
                      ("H", 3.62, [3.30, 3.65, 5.21, 6.40]), ("V", 6.25, [4.35, 4.70, 5.05]), ("V", 3.40, [3.35, 3.85, 4.35]),
                      ("V", 5.25, [0.80, 1.25, 2.05, 2.85, 3.25]), ("H", 4.42, [0.11, 0.47, 1.60, 2.50, 3.15]),
                      ("V", 9.12, [5.15, 5.50, 6.05, 6.30]), ("H", 8.15, [9.40, 10.95, 11.85, 12.75, 13.76]),
                      ("H", 9.88, [9.70, 11.20, 12.20, 12.70]), ("H", 7.45, [1.905, 4.30, 7.60, 9.40]), ("V", 7.60, [6.30, 7.25, 8.915])]:
        v.dim_chain(o, p, pts, size=4.2, side=-1)
    clip_off(c)
    yl = side_notes(c, [
        "Κατανομή: Υπν. 2 × 2 spots συμμετρικά στην ελεύθερη οροφή · λουτρά 3 (IP65 στο ντους) · κουζίνα μπροστά από τα επάνω ντουλάπια + έρκερ · χωλ / είσοδος στον άξονα της διαδρομής. Σύνολο 24 spots + 2 παροχές + LED3.",
        "Πυρανίχνευση (προδ. 4): σε κάθε κύριο χώρο και στο χωλ· ≥ 0,50 από τοίχους / δοκούς / φωτιστικά, ≥ 1,00 από στόμια προσαγωγής· λουτρά χωρίς ανιχνευτή καπνού (υδρατμοί).",
        "R11 χωλ: ΑΚ4 στον άξονα του διαδρόμου 1,00 (0,50 από τους δύο τοίχους, ανάμεσα στις ΘΕ2 / ΘΕ3)· Χ1 στον άξονα, Χ2 στο κέντρο του περάσματος. Στο R10 ο ΑΚ4 ήταν 0,29 από την ακμή και ≈ 0,30 από spot.",
        "R11: Υ1–Υ4 0,43 από ΚΡ3 / μέτωπο ντουλάπας 4,20 · ΚΡΕΜ1 στο κέντρο της τραπεζαρίας R23.",
        "Οπή spot Ø 75–80 ανάμεσα στα προφίλ CD (όχι πάνω τους)· όπου πέφτει σε προφίλ, μετατόπιση του προφίλ – όχι του spot.",
    ], y=770)
    legend(c, [
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1, fill=1)), "χωνευτό spot LED 7–9 W, 2700 K, CRI ≥ 90, UGR < 19, σώμα ≤ 75 mm"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2.8, y, x + 2.8, y)), "χωνευτό spot IP44 (λουτρά)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 2.8), c_.line(x - 2, y - 2, x + 2, y + 2), c_.line(x - 2, y + 2, x + 2, y - 2)), "χωνευτό spot IP65 (πάνω από ντους)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 4), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1.6, fill=1)), "ΚΡΕΜ παροχή οροφής (κουτί + ενίσχυση ανάρτησης)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.line(x - 3, y - 3, x + 3, y + 3), c_.line(x - 3, y + 3, x + 3, y - 3)), "ΑΚ ανιχνευτής καπνού (ΕΠ04 · EN 54-7)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.setFillColorRGB(*RED), c_.circle(x, y, 1.1, fill=1)), "ΑΘ θερμοδιαφορικός ανιχνευτής (κουζίνα · EN 54-5)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(0.9, 0.55, 0.55), c_.setDash([1.5, 1.5]), c_.circle(x, y, 4), c_.setDash([])), "ακτίνα 0,50 m γύρω από ανιχνευτή – κανένας τοίχος / φωτιστικό μέσα"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.setDash([4, 2]), c_.line(x - 5, y, x + 5, y), c_.setDash([])), "LED3 κρυφό γραμμικό 3000 K"),
    ], y=yl)
    title(c, "ΑΝ-03", "ΑΝΟΨΗ – ΦΩΤΙΣΜΟΣ · ΠΥΡΑΝΙΧΝΕΥΣΗ", "Χωνευτά spots · παροχές · κρυφό LED · ανιχνευτές · Wi-Fi")


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


def sheet_an04(c):
    rows = checks.run()
    from collections import Counter
    cnt = Counter(r[5] for r in rows)
    # ---- αριστερή στήλη: προδιαγραφές
    x, y, w = 40, 805, 360
    spec = [
        ("1 Κλιματισμός", "Καναλάτη σε καθιστικό (ΚΜ1 24k), Υπν.1 (ΚΜ2 12k), Υπν.2 (ΚΜ3 9k) · κουζίνα από την ΚΜ1 (ΕΓΚΕΚΡ.) · slot Π1/Π2 στο καθιστικό, "
         "γραμμικά Π3/Π4 στα υπνοδωμάτια (ΕΓΚΕΚΡ.) · χώρος 30 / 32 cm – ΚΜ1 οριακή (5 mm) · θυρίδες Ε1 / ΘΕ2 / ΘΕ3."),
        ("2 Κουρτίνες", "ΚΡ1–ΚΡ4 σε όλα τα ανοίγματα καθιστικού / υπνοδωματίων, 20 (22) × 10 cm, 2 οδηγοί, ανοιχτές ως την πλάκα, δίπλα στις δοκούς όψης."),
        ("3 Φωτισμός", "24 χωνευτά spots σε υπνοδωμάτια, λουτρά, χωλ, είσοδο, κουζίνα (IP44/IP65 στα λουτρά) · καθιστικό με ΚΡΕΜ0/ΚΡΕΜ1 (ΕΓΚΕΚΡ.) · κανένα "
         "spot κάτω από μονάδα / αεραγωγό / σε θυρίδα · κενό ≥ 88 mm πάνω από κάθε spot."),
        ("4 Πυρανίχνευση", "ΑΚ1–ΑΚ4 καπνού + ΑΘ5 θερμοδιαφορικός κουζίνας · όλοι ≥ 0,50 από τοίχους / δοκούς / φωτιστικά και ≥ 1,00 από στόμια προσαγωγής."),
        ("5 Κατασκευή", "Βασική 10 cm κάτω από την πλάκα · μεγαλύτερη καταβίβαση μόνο στις καναλάτες (+2,45) · περασιά με τις δοκούς · μία σανίδα κάτω "
         "από τη Δ3.1 στο Υπν.2 (εξαίρεση) · κανένα δόντι."),
        ("6 Γενική αρχή", "5 στάθμες σε όλο το διαμέρισμα, κάθε αλλαγή πάνω σε γραμμή δοκού ή μετώπη ντουλάπας."),
    ]
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(x, y, "ΣΥΜΜΟΡΦΩΣΗ ΜΕ ΤΙΣ ΠΡΟΔΙΑΓΡΑΦΕΣ (ιδιοκτήτης 07/11/2026)")
    y -= 14
    for head, txt in spec:
        c.setFont("Inter-SemiBold", 6.4); c.drawString(x, y, head)
        for j, l in enumerate(_wrap(txt, "Inter", 5.6, w - 70)):
            c.setFont("Inter", 5.6); c.drawString(x + 70, y - j * 7.3, l)
        y -= 7.3 * len(_wrap(txt, "Inter", 5.6, w - 70)) + 4
    y -= 4
    y = block(c, x, y, w, "ΕΓΚΕΚΡΙΜΕΝΕΣ ΑΠΟΚΛΙΣΕΙΣ (ιδιοκτήτης 07/11/2026)", [
        "Καθιστικό – τραπεζαρία χωρίς spots (απόφαση R02· «η νέα προδιαγραφή δεν υπερισχύει»).",
        "Κουζίνα χωρίς δική της καναλάτη – καλύπτεται από την ΚΜ1 24k.",
        "Π3 / Π4 υπνοδωματίων: γραμμικά στόμια 1000×150 σε μετώπη / τοίχο, όχι slot.",
        "Μονάδες slim ≤ 245 mm (ΚΜ1) / ≤ 200 mm (ΚΜ2, ΚΜ3) ως παραδοχή μέχρι την επιλογή μοντέλου.",
    ])
    y = block(c, x, y, w, "ΑΛΛΑΓΕΣ R10 → R11", A.CHANGES)
    ol = []
    for code, kind, txt in A.OPEN:
        ol.append(("%s [%s] %s" % (code, kind, txt), RED if kind == "ΑΠΟΦΑΣΗ" else DARK))
    y = block(c, x, y, w, "ΑΝΟΙΚΤΑ ΣΗΜΕΙΑ", ol)
    # ---- δεξιά: πίνακας ελέγχων σε 2 στήλες
    X0, Y0 = 420, 805
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK)
    c.drawString(X0, Y0, "ΕΛΕΓΧΟΣ ΣΥΓΚΡΟΥΣΕΩΝ & ΣΤΑΘΜΩΝ – %d έλεγχοι · " % len(rows) +
                 " · ".join("%s %d" % (k, cnt.get(k, 0)) for k in ("OK", "ΟΡΙΑΚΟ", "ΕΓΚΕΚΡ.", "ΑΠΟΚΛΙΣΗ")))
    c.setFont("Inter", 5.4); c.setFillColorRGB(*GREY)
    c.drawString(X0, Y0 - 9, "Αυτόματος έλεγχος από το μοντέλο (code/anopseis/checks.py): στάθμες ↔ δοκοί · κενό μονάδων · θυρίδες · spots ↔ ζώνες / θυρίδες / μονάδες / "
                 "αεραγωγοί / κουρτινόθηκες · ανιχνευτές ↔ τοίχοι / φωτιστικά / στόμια · κουρτινόθηκες ↔ κουφώματα / δοκοί.")
    colw = 362; lh = 8.2; fs = 5.2
    xs = [X0, X0 + colw + 12]
    half = (len(rows) + 1) // 2
    for ci, chunk in enumerate((rows[:half], rows[half:])):
        xx, yy = xs[ci], Y0 - 22
        c.setFont("Inter-SemiBold", 5.4); c.setFillColorRGB(*DARK)
        c.drawString(xx, yy, "ΚΩΔ."); c.drawString(xx + 38, yy, "ΚΑΤΑΣΤ."); c.drawString(xx + 80, yy, "ΣΤΟΙΧΕΙΟ"); c.drawString(xx + 250, yy, "ΜΕΤΡΗΣΗ")
        c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.4); c.line(xx, yy - 2, xx + colw, yy - 2)
        yy -= lh + 1
        for code, grp, item, crit, val, st in chunk:
            c.setFont("Inter", fs); c.setFillColorRGB(*DARK); c.drawString(xx, yy, code)
            c.setFont("Inter-SemiBold", fs); c.setFillColorRGB(*STC[st]); c.drawString(xx + 38, yy, st)
            c.setFont("Inter", fs); c.setFillColorRGB(*DARK)
            it = item
            while pdfmetrics.stringWidth(it, "Inter", fs) > 165: it = it[:-2]
            c.drawString(xx + 80, yy, it if it == item else it + "…")
            vv = val
            while pdfmetrics.stringWidth(vv, "Inter", fs) > colw - 252: vv = vv[:-2]
            c.drawString(xx + 250, yy, vv if vv == val else vv + "…")
            yy -= lh
    title(c, "ΑΝ-04", "ΑΝΟΨΗ – ΕΛΕΓΧΟΣ ΠΡΟΔΙΑΓΡΑΦΩΝ", "Συμμόρφωση · έλεγχος συγκρούσεων · αλλαγές R11 · ανοικτά σημεία", scale="—")
