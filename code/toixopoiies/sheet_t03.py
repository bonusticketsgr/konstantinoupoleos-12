"""Φύλλο Τ-03 (απλό): τετραγωνικά ανά τυπολογία τοίχου + θερμοπρόσοψη 10 / 5 cm + σημειώσεις κάτοψης.
(Η αναλυτική προμέτρηση υλικών είναι στο sheet_t03_detailed.py – δεν τυπώνεται, Γιάννης 05/11.)"""
import b1_model as M
import quantities as Q
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title
from sheet_t02 import wrap


def f2(v, d=2):
    return ("%.*f" % (d, v)).replace(".", ",")


def sheet_t03(c):
    rows = Q.per_type()
    m = 20; left = m + 14; top = PAGE_H - m - 26
    c.setFont("Inter-Bold", 14); c.setFillColorRGB(*DARK)
    SH = getattr(M, "SHEET", dict(floor="Β΄ ΟΡΟΦΟΣ – Β1", floor_short="Β΄ ΟΡΟΦΟΥ", apt="Β1"))
    c.drawString(left, top, "ΠΡΟΜΕΤΡΗΣΗ ΤΟΙΧΟΠΟΙΙΩΝ – " + SH["floor"])
    c.setFont("Inter", 7); c.setFillColorRGB(*GREY)
    c.drawString(left, top - 14, "τετραγωνικά ανά τυπολογία τοίχου · H = " + ("%.2f" % M.H).replace(".", ",") + " m (τελικό δάπεδο – κάτω παρειά πλάκας) · μήκη στον άξονα, χωρίς αφαίρεση κουφωμάτων · " + M.REV)
    # ---- πίνακας
    cols = [("", 26), ("Τύπος", 44), ("Περιγραφή", 330), ("Πάχος cm", 60), ("Τοίχοι", 50), ("Μήκος m", 70), ("Επιφάνεια m²", 90)]
    y = top - 42; x = left
    c.setFont("Inter-SemiBold", 8); c.setFillColorRGB(*DARK)
    for n, w in cols:
        c.drawString(x + 4, y, n); x += w
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6); c.line(left, y - 5, left + sum(w for _, w in cols), y - 5)
    y -= 20
    groups = [("ΤΟΥΒΛΑ", ["T1", "T4", "T5", "T10"]), ("ΧΩΡΙΣΜΑΤΑ ΓΥΨΟΣΑΝΙΔΑΣ", ["T2", "T2N", "T2A", "T7", "T6", "T8"]), ("ΕΠΕΝΔΥΣΕΙΣ", ["T3", "T9"])]
    bytype = {r["type"]: r for r in rows}
    grand = 0
    for gname, types in groups:
        c.setFont("Inter-Bold", 7); c.setFillColorRGB(*GREY); c.drawString(left + 4, y, gname); y -= 13
        gsum = 0
        for t in types:
            if t not in bytype:
                continue
            r = bytype[t]; tp = M.TYPES[t]
            area = r["L"] * M.H; gsum += area
            vals = ["", t, tp["name"], ("%g" % round(tp["thick"] * 100, 1)).replace(".", ","), str(r["n"]), f2(r["L"]), f2(area, 1)]
            x = left
            for i, ((n, w), val) in enumerate(zip(cols, vals)):
                if i == 0:
                    c.setFillColorRGB(*tp["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.3)
                    c.rect(x + 6, y - 1, 12, 8, stroke=1, fill=1)
                else:
                    c.setFont("Inter-SemiBold" if i in (1, 6) else "Inter", 8); c.setFillColorRGB(*DARK)
                    if i >= 3:
                        c.drawRightString(x + w - 8, y, val)
                    else:
                        c.drawString(x + 4, y, val)
                x += w
            c.setStrokeColorRGB(0.82, 0.82, 0.85); c.setLineWidth(0.3); c.line(left, y - 5, left + sum(w for _, w in cols), y - 5)
            y -= 15
        c.setFont("Inter-SemiBold", 8); c.setFillColorRGB(*DARK)
        c.drawRightString(left + sum(w for _, w in cols) - 8, y, f2(gsum, 1) + " m²")
        c.drawString(left + 30, y, "Σύνολο " + gname.lower())
        grand += gsum
        y -= 20
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6); c.line(left, y + 8, left + sum(w for _, w in cols), y + 8)
    c.setFont("Inter-Bold", 9); c.drawString(left + 30, y - 4, "ΣΥΝΟΛΟ ΤΟΙΧΟΠΟΙΙΩΝ " + SH["apt"])
    c.drawRightString(left + sum(w for _, w in cols) - 8, y - 4, f2(grand, 1) + " m²")
    y -= 34
    # ---- θερμοπρόσοψη
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(left, y, "ΘΕΡΜΟΠΡΟΣΟΨΗ (ETICS)"); y -= 11
    c.setFont("Inter", 6.5); c.setFillColorRGB(*GREY)
    c.drawString(left, y, "10 cm στις όψεις των διαμερισμάτων · 5 cm στο κλιμακοστάσιο / πυρήνα · ύψος " + ("%.2f" % Q.ETICS_H).replace(".", ",") + " m (με τη μετώπη πλάκας) · καθαρά = όψη − κουφώματα + λαμπάδες/ανώφλια")
    y -= 16
    hdr = [("Ζώνη", 160), ("Μήκος όψης m", 90), ("Μικτά m²", 80), ("Κουφώματα m²", 90), ("Λαμπάδες m²", 90), ("Καθαρά m²", 90)]
    x = left; c.setFont("Inter-SemiBold", 7.5); c.setFillColorRGB(*DARK)
    for n, w in hdr:
        c.drawString(x + 4, y, n); x += w
    c.setLineWidth(0.5); c.line(left, y - 5, left + sum(w for _, w in hdr), y - 5); y -= 17
    tot = 0
    for e in Q.etics_summary():
        vals = ["ETICS %d cm – %s" % (round(e["th"] * 100), "διαμερίσματα" if e["th"] > 0.07 else "κλιμακοστάσιο / πυρήνας"),
                f2(e["L"]), f2(e["gross"], 1), "−" + f2(e["wins"], 1), "+" + f2(e["rev"], 1), f2(e["net"], 1)]
        x = left
        for i, ((n, w), val) in enumerate(zip(hdr, vals)):
            c.setFont("Inter-SemiBold" if i in (0, 5) else "Inter", 8); c.setFillColorRGB(*DARK)
            (c.drawString(x + 4, y, val) if i == 0 else c.drawRightString(x + w - 8, y, val)); x += w
        tot += e["net"]; y -= 15
    c.setFont("Inter-SemiBold", 8); c.drawString(left + 4, y, "Σύνολο ETICS"); c.drawRightString(left + sum(w for _, w in hdr) - 8, y, f2(tot, 1) + " m²")
    # ---- σημειώσεις (δεξιά)
    xr = left + 720; yy = top - 42
    if getattr(M, "SHOW_NOTES", True):
        c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(xr, yy, "ΣΗΜΕΙΩΣΕΙΣ ΚΑΤΟΨΗΣ"); yy -= 13
    for n in (M.NOTES if getattr(M, "SHOW_NOTES", True) else []):
        for ln in wrap(c, "• " + n, "Inter", 6, PAGE_W - m - 12 - xr):
            c.setFont("Inter", 6); c.setFillColorRGB(*DARK); c.drawString(xr, yy, ln); yy -= 7.6
        yy -= 2
    frame_and_title(c, "Τ-03", "ΠΡΟΜΕΤΡΗΣΗ ΤΟΙΧΟΠΟΙΙΩΝ – " + ("Β΄ ΟΡΟΦΟΣ" if SH["floor_short"] == "Β΄ ΟΡΟΦΟΥ" else SH["floor_short"]),
                    "Τετραγωνικά ανά τυπολογία τοίχου · θερμοπρόσοψη 10 / 5 cm", SH["floor"],
                    "Βάση: κάτοψη τοιχοποιιών Τ-01 · είδη Τ-02", "— · A3", M.REV, M.DATE)
