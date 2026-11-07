"""Φύλλο Τ-02: είδη τοιχοποιιών – τομές 1:4, περιγραφή, mini-κάτοψη, μήκη / εμβαδά ανά είδος."""
import b1_model as M
import quantities as Q
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, frame_and_title
from sheet_t01 import draw_plan

PT_PER_M_4 = 72 / 25.4 * 1000 / 4     # 1:4
SEC_H = 0.11                            # ύψος τομής στο μοντέλο (m) → 78 pt
GYP = 0.0125


def section(c, x, y_top, typ):
    """Τομή 1:4 του είδους: στρώσεις από αριστερά προς δεξιά (πάχος σε m)."""
    t = M.TYPES[typ]; th = t["thick"]
    s = PT_PER_M_4
    layers = []
    for name in t["layers"]:
        if name.startswith("brick"):
            layers.append(("brick", th))
        elif name == "gyp":
            layers.append(("gyp", GYP))
        elif name == "glue":
            layers.append(("glue", 0.0125))
        elif name.startswith("cw"):
            layers.append(("cw", int(name[2:]) / 1000))
        elif name.startswith("gap"):
            # "gap5" = κενό 5 cm · "gap" = υπόλοιπο πάχους μετά 4 γυψοσανίδες + CW 50 + CW 30 (Τ7: 25 − 5 − 5 − 3 = 12)
            layers.append(("gap", int(name[3:]) / 100 if len(name) > 3 else th - 4 * GYP - 0.05 - 0.03))
    tot = sum(w for _, w in layers)
    x0 = x
    H = SEC_H * s
    for kind, w in layers:
        W = w * s
        if kind == "brick":
            c.setFillColorRGB(*t["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.5)
            c.rect(x0, y_top - H, W, H, stroke=1, fill=1)
            c.setStrokeColorRGB(0.55, 0.30, 0.20); c.setLineWidth(0.25)
            # πλέγμα τούβλου
            step = 0.019 * s if typ not in ("T4", "T4A") else 0.012 * s
            yy = y_top - step
            while yy > y_top - H:
                c.line(x0, yy, x0 + W, yy); yy -= step
            xx = x0 + step
            while xx < x0 + W:
                c.line(xx, y_top, xx, y_top - H); xx += step
        elif kind in ("gyp", "glue"):
            c.setFillColorRGB(0.93, 0.93, 0.95) if kind == "gyp" else c.setFillColorRGB(0.80, 0.78, 0.70)
            c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
            c.rect(x0, y_top - H, W, H, stroke=1, fill=1)
        elif kind == "cw":
            c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
            c.rect(x0, y_top - H, W, H, stroke=1, fill=0)
            # προφίλ C
            c.setLineWidth(0.6)
            ym = y_top - H / 2
            c.line(x0 + 1.5, ym - 6, x0 + 1.5, ym + 6); c.line(x0 + 1.5, ym + 6, x0 + W - 1.5, ym + 6)
            c.line(x0 + 1.5, ym - 6, x0 + W - 1.5, ym - 6)
            c.setLineWidth(0.3)
            if W > 20:
                c.setFillColorRGB(0.82, 0.82, 0.84)
                c.rect(x0 + 2, y_top - H + 10, W - 4, H - 20, stroke=0, fill=1)   # πετροβάμβακας / κενό
        elif kind == "gap":
            c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
            c.rect(x0, y_top - H, W, H, stroke=1, fill=0)
            c.setFillColorRGB(0.88, 0.85, 0.93); c.rect(x0 + 0.5, y_top - H + 0.5, W - 1, H - 1, stroke=0, fill=1)
        x0 += W
    # διάσταση πάχους
    y = y_top - H - 8
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
    c.line(x, y, x + tot * s, y); c.line(x, y - 3, x, y + 3); c.line(x + tot * s, y - 3, x + tot * s, y + 3)
    c.setFont("Inter-Medium", 6); c.setFillColorRGB(*DARK)
    c.drawCentredString(x + tot * s / 2, y - 9, ("%g" % round(th * 100, 2)).replace(".", ","))
    return tot * s


def wrap(c, text, font, size, width):
    from reportlab.pdfbase import pdfmetrics
    words = text.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def card(c, x, y, w, h, typ, row):
    t = M.TYPES[typ]
    c.setStrokeColorRGB(0.75, 0.75, 0.78); c.setLineWidth(0.4); c.rect(x, y, w, h, stroke=1, fill=0)
    # τίτλος
    c.setFillColorRGB(*t["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
    c.rect(x + 8, y + h - 20, 12, 9, stroke=1, fill=1)
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(x + 24, y + h - 19, typ)
    c.setFont("Inter-Medium", 6); c.drawString(x + 24 + len(typ) * 6.5 + 4, y + h - 18.5, t["name"])
    c.setFont("Inter", 5.5); c.setFillColorRGB(*GREY); c.drawRightString(x + w - 8, y + h - 18.5, "1:4")
    c.setFont("Inter-SemiBold", 6.5); c.setFillColorRGB(*DARK)
    c.drawString(x + 8, y + h - 31, ("πάχος %g cm" % round(t["thick"] * 100, 2)).replace(".", ","))
    # τομή
    sec_w = t["thick"] * PT_PER_M_4
    section(c, x + (w - sec_w) / 2, y + h - 42, typ)
    # περιγραφή
    c.setFont("Inter", 5.2); c.setFillColorRGB(*DARK)
    yy = y + h - 42 - SEC_H * PT_PER_M_4 - 26
    for ln in wrap(c, t["desc"], "Inter", 5.2, w - 16)[:7]:
        c.drawString(x + 8, yy, ln); yy -= 6.4
    # mini κάτοψη
    ms = getattr(M, "PLAN_MS", 7.2)   # pt/m
    y1 = getattr(M, "PLAN_Y1", 10.3)
    v = View(c, x + 16 + getattr(M, "PLAN_X_SHIFT", 0) * ms, PAGE_H - (y + 46 + y1 * ms) + 0, ms)
    # View: Y = PAGE_H - (oy + y*s)· θέλουμε το μοντέλο y∈[0,y1] μέσα στο [y+46, y+46+y1*ms] από κάτω
    v.oy = PAGE_H - (y + 46 + y1 * ms)
    draw_plan(v, highlight=typ, with_furniture=False, with_text=False, with_dims=False, with_labels=False)
    # λίστα τοίχων + σύνολα
    c.setFont("Inter", 5); c.setFillColorRGB(*GREY)
    ids = "Τοίχοι: " + ", ".join(row["ids"])
    yy = y + 30
    for ln in wrap(c, ids, "Inter", 5, w - 16)[:2]:
        c.drawString(x + 8, yy, ln); yy -= 6
    c.setFont("Inter-SemiBold", 6.2); c.setFillColorRGB(*DARK)
    c.drawString(x + 8, y + 9, ("Μήκος %.2f m · επιφάνεια ≈ %.1f m²" % (row["L"], row["L"] * M.H)).replace(".", ","))


def sheet_t02(c, sheet_no="Τ-02"):
    rows = {r["type"]: r for r in Q.per_type()}
    m = 20; top = PAGE_H - m - 12; left = m + 10
    W = (PAGE_W - 2 * m - 20 - 5 * 6) / 6; Hc = 335
    for i, typ in enumerate(M.TYPE_ORDER[:6]):
        card(c, left + i * (W + 6), top - Hc, W, Hc, typ, rows[typ])
    for i, typ in enumerate(M.TYPE_ORDER[6:]):
        card(c, left + i * (W + 6), top - 2 * Hc - 8, W, Hc, typ, rows[typ])
    c.setFont("Inter", 5.6); c.setFillColorRGB(*GREY)
    c.drawString(left, min(top - 2 * Hc - 20, 102),
                 "Επιφάνειες ενδεικτικές: μήκος × ύψος " + ("%.2f" % M.H).replace(".", ",") + " m (τελικό δάπεδο – πλάκα) – οι τοίχοι ορίζονται μεταξύ ανοιγμάτων, χωρίς αφαίρεση κασών. "
                 "Τ3 = επένδυση στην εσωτερική παρειά των Τ1 · Τ9 = περίμετρος υποστυλώματος × ύψος. "
                 "R15: Τ2N = 1 φύλλο στην πλευρά ντουλάπας (Τ2N-01, Τ2N-02) · Τ7-01 1 φύλλο προς Υπν.1.")
    SH = getattr(M, "SHEET", dict(floor="Β΄ ΟΡΟΦΟΣ – Β1", floor_short="Β΄ ΟΡΟΦΟΥ", arch="A-10-2F"))
    frame_and_title(c, sheet_no, "ΕΙΔΗ ΤΟΙΧΟΠΟΙΙΩΝ – " + ("Β΄ ΟΡΟΦΟΣ" if SH["floor_short"] == "Β΄ ΟΡΟΦΟΥ" else SH["floor_short"]),
                    "Είδη τοιχοποιιών · " + SH["floor"], "τομές 1:4 · μήκη – εμβαδά ανά είδος",
                    "Βάση: κάτοψη τοιχοποιιών Τ-01 · κάτοψη " + SH["arch"], "Κλίμακα 1:4 · A3", M.REV, M.DATE)


# ---------------------------------------------------------------- R25 / Δ R02 (Γιάννης 07/11): ΕΝΑ φύλλο ειδών για όλο το τεύχος
ALL_ORDER = ["T1", "T4", "T4A", "T5", "T10", "T3", "T9", "T2", "T2N", "T2A", "T7", "T7A", "T6", "T6A", "T8"]


def card_all(c, x, y, w, h, typ, per_floor):
    """Κάρτα είδους για το ενιαίο φύλλο: τομή 1:4 + περιγραφή + μήκη / m² ανά όροφο (χωρίς mini-κάτοψη)."""
    t = M.TYPES[typ]
    c.setStrokeColorRGB(0.75, 0.75, 0.78); c.setLineWidth(0.4); c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFillColorRGB(*t["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4)
    c.rect(x + 8, y + h - 20, 12, 9, stroke=1, fill=1)
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(x + 24, y + h - 19, typ)
    c.setFont("Inter-Medium", 6); c.drawString(x + 24 + len(typ) * 6.5 + 4, y + h - 18.5, t["name"])
    c.setFont("Inter", 5.5); c.setFillColorRGB(*GREY); c.drawRightString(x + w - 8, y + h - 18.5, "1:4")
    c.setFont("Inter-SemiBold", 6.5); c.setFillColorRGB(*DARK)
    c.drawString(x + 8, y + h - 31, ("πάχος %g cm" % round(t["thick"] * 100, 2)).replace(".", ","))
    sec_w = t["thick"] * PT_PER_M_4
    section(c, x + (w - sec_w) / 2, y + h - 40, typ)
    c.setFont("Inter", 5.2); c.setFillColorRGB(*DARK)
    yy = y + h - 40 - SEC_H * PT_PER_M_4 - 24
    for ln in wrap(c, t["desc"], "Inter", 5.2, w - 16)[:5]:
        c.drawString(x + 8, yy, ln); yy -= 6.4
    # μήκη / εμβαδά ανά όροφο
    yy = y + 8 + 6.6 * (len(per_floor) + 1) - 2
    c.setStrokeColorRGB(0.75, 0.75, 0.78); c.line(x + 8, yy + 7, x + w - 8, yy + 7)
    tot_L = tot_A = 0.0
    for apt, L, A in per_floor:
        c.setFont("Inter", 5.6); c.setFillColorRGB(*GREY); c.drawString(x + 8, yy, apt)
        c.setFont("Inter-Medium", 5.6); c.setFillColorRGB(*DARK)
        c.drawRightString(x + w - 8, yy, ("%.2f m · %.1f m²" % (L, A)).replace(".", ","))
        tot_L += L; tot_A += A; yy -= 6.6
    c.setFont("Inter-SemiBold", 6.2); c.setFillColorRGB(*DARK)
    c.drawString(x + 8, yy, "Σύνολο τεύχους")
    c.drawRightString(x + w - 8, yy, ("%.2f m · %.1f m²" % (tot_L, tot_A)).replace(".", ","))


def sheet_t02_all(c, models, sheet_no, rev, date):
    """Όλα τα είδη του τεύχους σε ΜΙΑ σελίδα (3 × 5 κάρτες), με μήκη / m² ανά όροφο."""
    global M
    rows = {}   # typ → [(apt, L, area)]
    for mdl in models:
        apt = getattr(mdl, "SHEET", dict(apt="Β1"))["apt"]
        for r in Q.per_type(mdl):
            rows.setdefault(r["type"], []).append((apt, r["L"], r["L"] * mdl.H))
    order = [t for t in ALL_ORDER if t in rows] + sorted(t for t in rows if t not in ALL_ORDER)
    M = models[0]
    m = 20; top = PAGE_H - m - 12; left = m + 10
    ncol = 5; nrow = (len(order) + ncol - 1) // ncol
    W = (PAGE_W - 2 * m - 20 - (ncol - 1) * 6) / ncol
    Hc = (top - 106 - (nrow - 1) * 6) / nrow
    for i, typ in enumerate(order):
        r, k = divmod(i, ncol)
        card_all(c, left + k * (W + 6), top - (r + 1) * Hc - r * 6, W, Hc, typ, rows[typ])
    c.setFont("Inter", 5.6); c.setFillColorRGB(*GREY)
    c.drawString(left, 100, "Επιφάνειες ενδεικτικές: μήκος × ύψος ορόφου (ισόγειο 3,00 · όροφοι 2,90 · σοφίτα 2,65) – οι τοίχοι ορίζονται μεταξύ ανοιγμάτων, "
                 "χωρίς αφαίρεση κασών. Τ3 = επένδυση στην εσωτερική παρειά των Τ1 · Τ9 = περίμετρος υποστυλώματος × ύψος. "
                 "Το Β1 μετράται μία φορά (τυπικός όροφος Α΄/Β΄/Γ΄ – ×3 για όλο το κτήριο).")
    names = " · ".join(getattr(mdl, "SHEET", dict(apt="Β1"))["apt"].upper() for mdl in models)
    frame_and_title(c, sheet_no, "ΕΙΔΗ ΤΟΙΧΟΠΟΙΙΩΝ – ΟΛΟΙ ΟΙ ΟΡΟΦΟΙ", "Είδη τοιχοποιιών · " + names,
                    "τομές 1:4 · μήκη – εμβαδά ανά είδος και όροφο",
                    "Βάση: κατόψεις Τ-01…Τ-%02d" % len(models), "Κλίμακα 1:4 · A3", rev, date)
