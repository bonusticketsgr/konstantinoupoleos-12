"""Φύλλο Λ-03 – ΚΡΥΦΟΣ ΦΩΤΙΣΜΟΣ: κατόψεις των δύο λουτρών με κάθε γραμμή LED + τρεις ενδεικτικές λεπτομέρειες 1:5."""
import math
import lt_typ as T
import lt_sheets as S
from lt_draw import (V2, S25, fm, PAGE_W, PAGE_H, DARK, GREY, DIMC, frame_and_title, north_arrow,
                     TILE, JOINT, GLASS, MIRROR, SAN, WALLG, WHITE, RED)

LED, LED_F = S.LED, S.LED_F
S5 = S25 * 5                      # 1:5
GYP = (0.97, 0.97, 0.95)
CORE = (0.86, 0.86, 0.87)
RAY = (0.98, 0.80, 0.25)


def _len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))


def _lead(c, v, a, b, ta, tb, lines, anchor="l", size=5.6):
    """Κείμενο-οδηγός: τελεία στο (a, b), γραμμή ως το (ta, tb), κείμενο εκεί."""
    X, Y = v.p(a, b); X2, Y2 = v.p(ta, tb)
    c.setStrokeColorRGB(*GREY); c.setLineWidth(0.4); c.line(X, Y, X2, Y2)
    c.setFillColorRGB(*DARK); c.circle(X, Y, 1.3, stroke=0, fill=1)
    for i, s in enumerate(lines):
        c.setFont("Inter-SemiBold" if i == 0 else "Inter", size if i == 0 else size - 0.6)
        c.setFillColorRGB(*(DARK if i == 0 else GREY))
        y = Y2 - 2 - i * (size + 1.2)
        (c.drawString if anchor == "l" else c.drawRightString)(X2 + (3 if anchor == "l" else -3), y, s)


def _title(c, x, y, no, title, sub):
    c.setFillColorRGB(*DARK); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.8)
    c.circle(x + 9, y + 5, 9, stroke=1, fill=0)
    c.setFont("Inter-Bold", 8.6); c.drawCentredString(x + 9, y + 2, no)
    c.setFont("Inter-Bold", 8.4); c.drawString(x + 24, y + 6.5, title)
    c.setFont("Inter", 6.0); c.setFillColorRGB(*GREY); c.drawString(x + 24, y - 2.5, sub)


def _wall(v, a0, b0, a1, b1):
    v.rect(a0, b0, a1, b1, fill=WALLG, stroke=DARK, lw=0.6)
    v.hatch([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], step_pt=5, color=(0.62, 0.62, 0.65), lw=0.3)


def _rays(v, a, b, targets):
    for ta, tb in targets:
        v.line(a, b, ta, tb, color=RAY, lw=0.5, dash=[3, 2])


def detail_cove(c, ox, oy):
    """Λ1 – σκοτία οροφής με κρυφό LED (κατακόρυφη τομή στον τοίχο του ντους)."""
    zc = T.ZC
    v = V2(c, ox, oy, S5, a0=-0.10, b0=2.20)
    _wall(v, -0.10, 2.20, 0.0, 2.62)
    v.rect(0.0, 2.20, 0.015, 2.40, fill=TILE, stroke=JOINT, lw=0.5)                 # πλακάκι ως +2,40
    v.rect(0.0, 2.40, 0.006, zc + 0.10, fill=GYP, stroke=GREY, lw=0.3)              # βαμμένο πάνω από το πλακάκι (μέσα στη σκοτία)
    v.rect(0.095, zc, 0.33, zc + 0.0125, fill=GYP, stroke=DARK, lw=0.6)             # ψευδοροφή
    v.rect(0.095, zc, 0.1075, zc + 0.10, fill=GYP, stroke=DARK, lw=0.6)             # κατέβασμα (ποδιά)
    v.rect(0.0, zc + 0.10, 0.1075, zc + 0.1125, fill=GYP, stroke=DARK, lw=0.6)      # κλείσιμο από πάνω
    _rays(v, 0.078, zc + 0.045, [(0.018, 2.38), (0.02, 2.30), (0.035, 2.215), (0.07, 2.22)])
    v.rect(0.078, zc + 0.036, 0.095, zc + 0.054, fill=LED, stroke=DARK, lw=0.4)     # προφίλ LED πάνω στο κατέβασμα
    v.chain_h([0.015, 0.095], zc, off=-13, size=6.2, labels=["8"])
    v.line(0.015, 2.40, 0.33, 2.40, color=GREY, lw=0.3, dash=[2, 2])
    v.text(0.33, 2.40, "+2,40", size=5.6, font="Inter-SemiBold", anchor="r", dy=-6)
    _lead(c, v, 0.0075, 2.30, 0.14, 2.285, ["πλακάκι 60 × 120 ως +2,40"])
    _lead(c, v, 0.055, zc - 0.005, 0.14, 2.345, ["ΣΚΟΤΙΑ 8 cm – ανοιχτή σχισμή", "από εδώ πέφτει το φως στον τοίχο"])
    _lead(c, v, 0.087, zc + 0.045, 0.19, zc + 0.075, ["ΤΑΙΝΙΑ LED σε προφίλ", "κρυφή πίσω από το κατέβασμα 10 cm"])
    _lead(c, v, 0.25, zc + 0.006, 0.19, zc + 0.155, ["ψευδοροφή +2,40 … +2,50", "ανθυγρή γυψοσανίδα"])
    _title(c, ox, oy + (2.62 - 2.20) * S5 + 14, "1", "ΣΚΟΤΙΑ ΟΡΟΦΗΣ ΝΤΟΥΣ – Φ1", "κατακόρυφη τομή · το LED δεν φαίνεται, φαίνεται μόνο το φως στον τοίχο")


def detail_niche(c, ox, oy):
    """Εσοχή ντους (Λ1) – πάνω μέρος με το κρυφό LED και το ράφι."""
    v = V2(c, ox, oy, S5, a0=-0.265, b0=1.46)
    zt = 1.88
    _wall(v, -0.265, 1.46, -0.015, zt)
    v.rect(-0.12, 1.46, -0.015, 1.83, fill=WHITE)                                    # το κενό της εσοχής
    v.rect(-0.015, 1.80, 0.0, zt, fill=TILE, stroke=JOINT, lw=0.5)                  # πλακάκι τοίχου πάνω από την εσοχή (κατεβαίνει 3 cm)
    v.rect(-0.132, 1.46, -0.12, 1.83, fill=TILE, stroke=JOINT, lw=0.5)              # πλάτη εσοχής
    v.rect(-0.12, 1.83, -0.015, 1.842, fill=TILE, stroke=JOINT, lw=0.5)             # ταβάνι εσοχής
    v.rect(-0.118, 1.494, -0.004, 1.506, fill=(0.80, 0.88, 0.93), stroke=GLASS, lw=0.5)   # ράφι +1,50
    _rays(v, -0.036, 1.822, [(-0.118, 1.72), (-0.118, 1.60), (-0.07, 1.508), (-0.02, 1.508)])
    v.rect(-0.046, 1.814, -0.026, 1.83, fill=LED, stroke=DARK, lw=0.4)
    v.line(-0.265, 1.46, 0.0, 1.46, color=GREY, lw=0.5, dash=[6, 2, 1, 2])
    v.chain_h([-0.12, 0.0], 1.46, off=-13, size=6.2, labels=["12"])
    v.chain_v([1.80, 1.83], 0.0, off=14, size=6.2, labels=["3"])
    v.text(0.0, 1.80, "+1,80", size=5.6, font="Inter-SemiBold", anchor="l", dx=30, dy=-2)
    _lead(c, v, -0.036, 1.822, 0.06, 1.87, ["ΤΑΙΝΙΑ LED στο ταβάνι της εσοχής", "πίσω από το πλακάκι που κατεβαίνει 3 cm"])
    _lead(c, v, -0.05, 1.50, 0.06, 1.56, ["ράφι +1,50 (γυαλί ή πλακάκι)"])
    _lead(c, v, -0.126, 1.66, 0.06, 1.68, ["εσοχή 30 × 60, βάθος 12", "ντυμένη με το ίδιο πλακάκι · φάλτσο 45°"])
    _lead(c, v, -0.20, 1.52, 0.06, 1.485, ["τοίχος λεκάνης Τ7 – η εσοχή μέσα στο κενό"])
    _title(c, ox, oy + (zt - 1.46) * S5 + 14, "2", "ΕΣΟΧΗ ΝΤΟΥΣ – Φ2", "κατακόρυφη τομή · πάνω μέρος της εσοχής (συνεχίζει ως +1,20)")


def detail_counter(c, ox, oy):
    """Κτιστός πάγκος με τον νιπτήρα από πάνω και κρυφό LED από κάτω."""
    v = V2(c, ox, oy, S5, a0=-0.10, b0=0.50)
    zt = 0.93
    _wall(v, -0.10, 0.50, 0.0, zt)
    v.rect(0.0, 0.50, 0.015, 0.63, fill=TILE, stroke=JOINT, lw=0.5)
    v.rect(0.0, 0.75, 0.015, zt, fill=TILE, stroke=JOINT, lw=0.5)
    v.rect(0.0, 0.63, 0.50, 0.75, fill=TILE, stroke=DARK, lw=0.8)                    # πάγκος ντυμένος
    v.rect(0.015, 0.645, 0.485, 0.735, fill=CORE, stroke=GREY, lw=0.4)               # πυρήνας
    v.hatch([(0.015, 0.645), (0.485, 0.645), (0.485, 0.735), (0.015, 0.735)], step_pt=6, color=(0.70, 0.70, 0.72), lw=0.3)
    v.rrect(0.07, 0.75, 0.43, 0.88, 0.02, fill=SAN, stroke=DARK, lw=0.7)             # νιπτήρας από πάνω
    _rays(v, 0.44, 0.632, [(0.39, 0.505), (0.44, 0.505), (0.49, 0.505), (0.55, 0.515)])
    v.rect(0.43, 0.63, 0.45, 0.645, fill=LED, stroke=DARK, lw=0.4)
    v.chain_h([0.0, 0.45, 0.50], 0.50, off=-13, size=6.2, labels=["0,45", "5"])
    v.chain_v([0.63, 0.75], 0.50, off=16, size=6.2, labels=["12"])
    v.text(0.50, 0.75, "+0,75", size=5.6, font="Inter-SemiBold", anchor="l", dx=30, dy=-2)
    v.text(0.50, 0.63, "+0,63", size=5.6, font="Inter-SemiBold", anchor="l", dx=30, dy=-2)
    _lead(c, v, 0.43, 0.637, 0.335, 0.575, ["ΤΑΙΝΙΑ LED χωνευτή στο κάτω μέρος", "5 cm πίσω από το μέτωπο · φωτίζει το δάπεδο"], anchor="r")
    v.text(0.25, 0.70, "ΚΤΙΣΤΟΣ ΠΑΓΚΟΣ · πάχος 12", size=5.6, font="Inter-SemiBold", bg=CORE)
    v.text(0.25, 0.675, "ντυμένος με το ίδιο πλακάκι · φάλτσο 45° στο μέτωπο", size=5.0, color=GREY, bg=CORE)
    v.text(0.25, 0.825, "νιπτήρας από πάνω", size=5.6, font="Inter-SemiBold")
    v.text(0.25, 0.80, "χείλος ≈ +0,88", size=5.0, color=GREY)
    _title(c, ox, oy + (zt - 0.50) * S5 + 14, "3", "ΚΤΙΣΤΟΣ ΠΑΓΚΟΣ – Φ3", "κατακόρυφη τομή · ίδια και στο ράφι του ντους στο λουτρό γονέων (εκεί βάθος 30)")


def table(c, x, y):
    c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 7.6); c.drawString(x, y, "ΠΙΝΑΚΑΣ ΚΡΥΦΟΥ ΦΩΤΙΣΜΟΥ")
    y -= 15
    cols = [0, 22, 150, 190, 226]
    heads = ["Αρ.", "ΘΕΣΗ", "ΣΤΑΘΜΗ", "ΜΗΚΟΣ", "ΠΡΟΣΤΑΣΙΑ"]
    for R in T.ROOMS:
        c.setFont("Inter-Bold", 6.8); c.setFillColorRGB(*DARK); c.drawString(x, y, R["name"])
        y -= 10
        c.setFont("Inter-Medium", 5.4); c.setFillColorRGB(*GREY)
        for cx, h in zip(cols, heads): c.drawString(x + cx, y, h)
        y -= 3; c.setStrokeColorRGB(*GREY); c.setLineWidth(0.3); c.line(x, y, x + 292, y); y -= 9
        for L in R.get("lights", []):
            c.setFillColorRGB(*LED); c.circle(x + 6, y + 2.2, 6.2, stroke=0, fill=1)
            c.setFillColorRGB(1, 1, 1); c.setFont("Inter-Bold", 6.0); c.drawCentredString(x + 6, y, L["id"])
            c.setFillColorRGB(*DARK); c.setFont("Inter", 5.8)
            w = L["where"].split(" – ")
            c.drawString(x + cols[1], y + 2.6, w[0]); c.setFillColorRGB(*GREY); c.drawString(x + cols[1], y - 4.2, w[1] if len(w) > 1 else "")
            c.setFillColorRGB(*DARK)
            c.drawString(x + cols[2], y, L["z"]); c.drawString(x + cols[3], y, fm(round(_len(L["pts"]) + 0.004, 2)) + " m"); c.drawString(x + cols[4], y, L["ip"])
            y -= 16
        y -= 6
    c.setFont("Inter-Bold", 6.6); c.setFillColorRGB(*DARK); c.drawString(x, y, "ΤΙ ΕΙΝΑΙ"); y -= 10
    for a, b in [("Ταινία", "LED 24 V · 3000 K (θερμό) · CRI ≥ 90"), ("Προφίλ", "αλουμινίου με οπάλ κάλυμμα"),
                 ("Τροφοδοτικό", "μέσα στο ντουλάπι πάνω από τη λεκάνη"), ("Διακόπτης", "ξεχωριστός από τα σποτ")]:
        c.setFont("Inter-SemiBold", 6.0); c.setFillColorRGB(*DARK); c.drawString(x, y, a)
        c.setFont("Inter", 6.0); c.drawString(x + 56, y, b); y -= 10
    return y


def sheet(c, M, base):
    L1, L2 = T.ROOMS
    S.draw_plan(c, L1, M, 70, 778, light=True)
    S.draw_plan(c, L2, M, 400, 778, light=True)
    north_arrow(c, 372, 760, r=8)
    table(c, 868, 795)
    detail_cove(c, 62, 118)
    detail_niche(c, 352, 118)
    detail_counter(c, 716, 118)
    frame_and_title(c, "Λ-03", "ΚΡΥΦΟΣ ΦΩΤΙΣΜΟΣ ΛΟΥΤΡΩΝ",
                    "Α΄ · Β΄ · Γ΄ · Δ΄ όροφος · πού μπαίνει κάθε ταινία LED",
                    "Φ1 σκοτία οροφής · Φ2 εσοχή · Φ3 κάτω από τον πάγκο · ΠΡΟΤΑΣΗ",
                    base, "ΚΛΙΜΑΚΑ 1:25 · 1:5 · A3", T.REV, T.DATE)
    c.showPage()
