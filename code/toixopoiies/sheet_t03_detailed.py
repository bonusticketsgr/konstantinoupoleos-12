"""Φύλλο Τ-03: προμέτρηση υλικών τοιχοποιιών Β1 (πίνακας ανά είδος, λίστα παραγγελίας, παραδοχές, ETICS, σημειώσεις)."""
import b1_model as M
import quantities as Q
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title
from sheet_t02 import wrap


def fmt(v, d=1):
    if v is None or v == 0:
        return "–"
    s = ("%.*f" % (d, v))
    if d == 0:
        s = "{:,.0f}".format(v).replace(",", ".")
    return s.replace(".", ",") if d else s


def sheet_t03(c):
    rows = Q.per_type()
    m = 20; left = m + 10; top = PAGE_H - m - 24
    c.setFont("Inter-Bold", 13); c.setFillColorRGB(*DARK)
    c.drawString(left, top, "ΠΡΟΜΕΤΡΗΣΗ ΥΛΙΚΩΝ ΤΟΙΧΟΠΟΙΙΩΝ – Β΄ ΟΡΟΦΟΣ – Β1")
    c.setFont("Inter", 6.5); c.setFillColorRGB(*GREY)
    c.drawString(left, top - 13, "από την κάτοψη Τ-01 · H = 2,90 m (δάπεδο πλάκας – κάτω παρειά πλάκας) · μήκη στον άξονα κάθε τοίχου, χωρίς αφαίρεση κουφωμάτων (οι τοίχοι ορίζονται μεταξύ ανοιγμάτων) · R15")
    # ---- πίνακας
    cols = [("Είδος", 40), ("Περιγραφή", 230), ("Τοίχοι", 34), ("Μήκος m", 44), ("Επιφ. m²", 46),
            ("Γυψοσ. κοινή m²", 62), ("Γυψοσ. ανθυγρή m²", 66), ("Γυψοσ. πυράντ. m²", 66),
            ("Σκελετός CW m", 62), ("Οδηγός UW m", 56), ("Πετροβάμβ. m²", 58), ("Θερμοτούβλα τεμ.", 62),
            ("Κονίαμα m³", 50), ("Κόλλα kg", 46)]
    y = top - 36
    x = left
    c.setFont("Inter-SemiBold", 6); c.setFillColorRGB(*DARK)
    for name, w in cols:
        c.drawString(x + 3, y, name); x += w
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.5); c.line(left, y - 4, left + sum(w for _, w in cols), y - 4)
    y -= 16
    for r in rows:
        t = M.TYPES[r["type"]]
        vals = [r["type"], ("%s · %g cm" % (t["name"], round(t["thick"] * 100, 2))).replace(".", ","), str(r["n"]),
                fmt(r["L"], 2), fmt(r["area"], 2), fmt(r["gyp"]), fmt(r["gyp_h2"]), fmt(r["gyp_f"]),
                fmt(sum(r["cw"].values())), fmt(sum(r["uw"].values())), fmt(r["rock"]), fmt(r["bricks"], 0),
                fmt(r["mortar"], 2), fmt(r["glue"])]
        x = left
        for (name, w), val in zip(cols, vals):
            if name == "Είδος":
                c.setFillColorRGB(*t["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.3)
                c.rect(x + 3, y - 1, 10, 7, stroke=1, fill=1)
                c.setFont("Inter-SemiBold", 6.5); c.setFillColorRGB(*DARK); c.drawString(x + 16, y, val)
            else:
                c.setFont("Inter", 6.2); c.setFillColorRGB(*DARK); c.drawString(x + 3, y, val)
            x += w
        c.setFont("Inter", 4.6); c.setFillColorRGB(*GREY)
        c.drawString(left + 43, y - 6, ", ".join(r["ids"]))
        c.setStrokeColorRGB(0.8, 0.8, 0.82); c.setLineWidth(0.3); c.line(left, y - 9, left + sum(w for _, w in cols), y - 9)
        y -= 16
    # ---- λίστα παραγγελίας (αριστερά)
    y -= 14
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK)
    c.drawString(left, y, "ΛΙΣΤΑ ΠΑΡΑΓΓΕΛΙΑΣ (με φύρα: γυψοσανίδες +10 %, προφίλ +5 %)")
    y -= 14
    for name, val, unit, note in Q.order_list(rows):
        c.setFont("Inter", 6.5); c.setFillColorRGB(*DARK); c.drawString(left, y, name)
        d = 0 if unit in ("τεμ.",) or val > 1000 else (2 if unit == "m³" else 1)
        c.setFont("Inter-SemiBold", 6.5); c.drawRightString(left + 560, y, "%s %s" % (fmt(val, d), unit))
        c.setFont("Inter", 6); c.setFillColorRGB(*GREY); c.drawString(left + 570, y, note)
        c.setStrokeColorRGB(0.85, 0.85, 0.87); c.setLineWidth(0.3); c.line(left, y - 3, left + 640, y - 3)
        y -= 10.5
    # ---- σημειώσεις κάτοψης
    y -= 8
    c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK); c.drawString(left, y, "ΣΗΜΕΙΩΣΕΙΣ ΚΑΤΟΨΗΣ")
    y -= 10
    for n in M.NOTES:
        for ln in wrap(c, "• " + n, "Inter", 5.4, 640):
            c.setFont("Inter", 5.4); c.setFillColorRGB(*DARK); c.drawString(left, y, ln); y -= 6.6
            if y < 110: break
        if y < 110: break
    # ---- παραδοχές + ETICS (δεξιά)
    xr = left + 700; y = top - 36 - 16 * (len(rows) + 1) - 14
    c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK); c.drawString(xr, y, "ΠΑΡΑΔΟΧΕΣ"); y -= 10
    for a in Q.ASSUMPTIONS:
        for ln in wrap(c, "• " + a, "Inter", 5.4, PAGE_W - m - 10 - xr):
            c.setFont("Inter", 5.4); c.setFillColorRGB(*DARK); c.drawString(xr, y, ln); y -= 6.6
    y -= 8
    c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK); c.drawString(xr, y, "ΘΕΡΜΟΠΡΟΣΟΨΗ (ETICS) 10 cm"); y -= 8
    c.setFont("Inter", 5.2); c.setFillColorRGB(*GREY)
    c.drawString(xr, y, "ύψος ορόφου 3,10 m (με τη μετώπη πλάκας) · ύψη κουφωμάτων από τα label · όπως R14 (τα κουφώματα δεν άλλαξαν)"); y -= 10
    for i, (k, v) in enumerate(Q.ETICS):
        if i % 2 == 0:
            c.setFillColorRGB(0.99, 0.95, 0.80); c.rect(xr - 2, y - 2.5, PAGE_W - m - 8 - xr, 9.5, stroke=0, fill=1)
        c.setFont("Inter", 6.2); c.setFillColorRGB(*DARK); c.drawString(xr, y, k)
        c.setFont("Inter-SemiBold", 6.2); c.drawRightString(PAGE_W - m - 12, y, v)
        y -= 9.5
    frame_and_title(c, "Τ-03", "ΠΡΟΜΕΤΡΗΣΗ ΥΛΙΚΩΝ – Β΄ ΟΡΟΦΟΣ",
                    "Γυψοσανίδες · σκελετοί · τούβλα · αναλώσιμα", "Β΄ ΟΡΟΦΟΣ – Β1",
                    "Βάση: κάτοψη τοιχοποιιών Τ-01 · είδη Τ-02", "— · A3", M.REV, M.DATE)
