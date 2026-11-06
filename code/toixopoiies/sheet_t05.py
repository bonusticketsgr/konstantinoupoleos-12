"""Φύλλο προμέτρησης ΕΝΙΑΙΟΥ τεύχους (R11/R22, Γιάννης 07/11: «το τελευταίο φύλλο το θέλω περιεκτικό – τόσα τετραγωνικά τοίχοι
σε κάθε όροφο χωριστά»): ένας πίνακας ανά όροφο (m² ανά τυπολογία τοίχου + θερμοπρόσοψη) δίπλα-δίπλα, χωρίς σημειώσεις."""
import quantities as Q
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title


def f2(v, d=2):
    return ("%.*f" % (d, v)).replace(".", ",")


GROUPS = [("ΤΟΥΒΛΑ", ["T1", "T4", "T5", "T10"]), ("ΧΩΡΙΣΜΑΤΑ ΓΥΨΟΣΑΝΙΔΑΣ", ["T2", "T2N", "T2A", "T7", "T7A", "T7B", "T6", "T6A", "T8"]), ("ΕΠΕΝΔΥΣΕΙΣ", ["T3", "T9"])]


def floor_table(c, M, left, top, width):
    """Πίνακας ενός ορόφου. Επιστρέφει (y τέλους, σύνολο τοιχοποιιών, σύνολο ETICS)."""
    SH = getattr(M, "SHEET", dict(floor="Β΄ ΟΡΟΦΟΣ – Β1", floor_short="Β΄ ΟΡΟΦΟΥ", apt="Β1"))
    rows = {r["type"]: r for r in Q.per_type(M)}
    c.setFont("Inter-Bold", 12); c.setFillColorRGB(*DARK)
    c.drawString(left, top, SH["floor"] + "  ·  " + M.REV)
    c.setFont("Inter", 6.5); c.setFillColorRGB(*GREY)
    c.drawString(left, top - 12, "H = " + f2(M.H) + " m · μήκη στον άξονα, χωρίς αφαίρεση κουφωμάτων" + (" · υπέρθυρα πορτών στο είδος του τοίχου" if width > 440 else ""))
    cols = [("", 22), ("Τύπος", 40), ("Περιγραφή", width - 22 - 40 - 44 - 36 - 52 - 60), ("Πάχος cm", 44), ("Τοίχοι", 36), ("Μήκος m", 52), ("m²", 60)]
    y = top - 32; x = left
    c.setFont("Inter-SemiBold", 7.5); c.setFillColorRGB(*DARK)
    for n, w in cols:
        c.drawString(x + 4, y, n); x += w
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6); c.line(left, y - 5, left + width, y - 5)
    y -= 18
    grand = 0
    for gname, types in GROUPS:
        present = [t for t in types if t in rows]
        if not present:
            continue
        c.setFont("Inter-Bold", 6.5); c.setFillColorRGB(*GREY); c.drawString(left + 4, y, gname); y -= 12
        gsum = 0
        for t in present:
            r = rows[t]; tp = M.TYPES[t]
            area = r["L"] * M.H; gsum += area
            vals = ["", t, tp["name"], ("%g" % round(tp["thick"] * 100, 1)).replace(".", ","), str(r["n"]), f2(r["L"]), f2(area, 1)]
            x = left
            for i, ((n, w), val) in enumerate(zip(cols, vals)):
                if i == 0:
                    c.setFillColorRGB(*tp["fill"]); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.3)
                    c.rect(x + 5, y - 1, 11, 7.5, stroke=1, fill=1)
                else:
                    c.setFont("Inter-SemiBold" if i in (1, 6) else "Inter", 7.5); c.setFillColorRGB(*DARK)
                    if i == 2:
                        # περιγραφή: κόψιμο στο πλάτος της στήλης
                        s = val
                        while c.stringWidth(s, "Inter", 7.5) > w - 8 and len(s) > 3:
                            s = s[:-1]
                        c.drawString(x + 4, y, s if s == val else s.rstrip() + "…")
                    elif i >= 3:
                        c.drawRightString(x + w - 6, y, val)
                    else:
                        c.drawString(x + 4, y, val)
                x += w
            c.setStrokeColorRGB(0.82, 0.82, 0.85); c.setLineWidth(0.3); c.line(left, y - 5, left + width, y - 5)
            y -= 13.5
        c.setFont("Inter-SemiBold", 7.5); c.setFillColorRGB(*DARK)
        c.drawRightString(left + width - 6, y, f2(gsum, 1) + " m²")
        c.drawString(left + 26, y, "Σύνολο " + gname.lower())
        grand += gsum; y -= 17
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6); c.line(left, y + 8, left + width, y + 8)
    c.setFont("Inter-Bold", 9); c.drawString(left + 26, y - 4, "ΣΥΝΟΛΟ ΤΟΙΧΟΠΟΙΙΩΝ " + SH["apt"])
    c.drawRightString(left + width - 6, y - 4, f2(grand, 1) + " m²")
    y -= 30
    # θερμοπρόσοψη
    c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK); c.drawString(left, y, "ΘΕΡΜΟΠΡΟΣΟΨΗ (ETICS) – " + SH["floor_short"]); y -= 10
    c.setFont("Inter", 6); c.setFillColorRGB(*GREY)
    c.drawString(left, y, "10 cm διαμέρισμα · 5 cm πυρήνας · ύψος " + f2(M.H + 0.20) + " m (με μετώπη πλάκας)" + (" · καθαρά = όψη − κουφώματα + λαμπάδες" if width > 440 else ""))
    y -= 15
    cw = 50 if width > 440 else 44
    hdr = [("Ζώνη", width - 5 * cw), ("Μήκος m", cw), ("Μικτά m²", cw), ("Κουφώματα", cw), ("Λαμπάδες", cw), ("Καθαρά m²", cw)]
    x = left; c.setFont("Inter-SemiBold", 7); c.setFillColorRGB(*DARK)
    for n, w in hdr:
        c.drawString(x + 4, y, n); x += w
    c.setLineWidth(0.5); c.line(left, y - 5, left + width, y - 5); y -= 15
    tot = 0
    for e in Q.etics_summary(M):
        vals = ["ETICS %d cm – %s" % (round(e["th"] * 100), "διαμέρισμα" if e["th"] > 0.07 else ("κλιμακοστάσιο / πυρήνας" if width > 440 else "πυρήνας")),
                f2(e["L"]), f2(e["gross"], 1), "−" + f2(e["wins"], 1), "+" + f2(e["rev"], 1), f2(e["net"], 1)]
        x = left
        for i, ((n, w), val) in enumerate(zip(hdr, vals)):
            c.setFont("Inter-SemiBold" if i in (0, 5) else "Inter", 7.5); c.setFillColorRGB(*DARK)
            (c.drawString(x + 4, y, val) if i == 0 else c.drawRightString(x + w - 6, y, val)); x += w
        tot += e["net"]; y -= 13.5
    c.setFont("Inter-SemiBold", 7.5); c.drawString(left + 4, y, "Σύνολο ETICS " + SH["apt"]); c.drawRightString(left + width - 6, y, f2(tot, 1) + " m²")
    return y - 20, grand, tot


def sheet_t05(c, models, sheet_no="Τ-05", rev="", date="", K=None):
    """K: μεγέθυνση των πινάκων (μεγάλα γράμματα – το φύλλο αλλιώς μένει μισοάδειο)· με 3 ορόφους 1,05 ώστε να χωράνε οι στήλες."""
    if K is None:
        K = 1.32 if len(models) <= 2 else 1.05
    m = 20
    c.saveState(); c.scale(K, K)
    left = (m + 14) / K; top = (PAGE_H - m - 26) / K
    c.setFont("Inter-Bold", 14); c.setFillColorRGB(*DARK)
    c.drawString(left, top, "ΠΡΟΜΕΤΡΗΣΗ ΤΟΙΧΟΠΟΙΙΩΝ – ΤΕΤΡΑΓΩΝΙΚΑ ΑΝΑ ΤΥΠΟΛΟΓΙΑ ΚΑΙ ΑΝΑ ΟΡΟΦΟ")
    gap = 30; width = (PAGE_W / K - 2 * left - gap * (len(models) - 1)) / len(models)
    totals = []
    ymin = top
    for i, M in enumerate(models):
        y, g, e = floor_table(c, M, left + i * (width + gap), top - 30, width)
        totals.append((M, g, e)); ymin = min(ymin, y)
    # συγκεντρωτικά
    y = ymin - 6
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.8); c.line(left, y + 14, PAGE_W / K - left, y + 14)
    c.setFont("Inter-Bold", 10); c.setFillColorRGB(*DARK)
    c.drawString(left, y, "ΣΥΝΟΛΑ ΤΕΥΧΟΥΣ")
    x = left + 130
    for M, g, e in totals:
        SH = getattr(M, "SHEET", dict(apt="Β1"))
        c.setFont("Inter-SemiBold", 9); c.drawString(x, y, SH["apt"] + ": τοιχοποιίες " + f2(g, 1) + " m²  ·  ETICS " + f2(e, 1) + " m²")
        x += min(260, width + gap)
    c.setFont("Inter-Bold", 10)
    c.drawString(left + 130, y - 16, "ΟΛΟΙ ΟΙ ΟΡΟΦΟΙ ΤΟΥ ΤΕΥΧΟΥΣ: τοιχοποιίες " + f2(sum(g for _, g, _ in totals), 1) + " m²  ·  ETICS " + f2(sum(e for _, _, e in totals), 1) + " m²")
    c.restoreState()
    names = " · ".join(getattr(M, "SHEET", dict(apt="Β1"))["apt"].upper() for M in models)
    plans = " / ".join("Τ-%02d" % (2 * i + 1) for i in range(len(models))); kinds = " / ".join("Τ-%02d" % (2 * i + 2) for i in range(len(models)))
    frame_and_title(c, sheet_no, "ΠΡΟΜΕΤΡΗΣΗ ΤΟΙΧΟΠΟΙΙΩΝ – " + names,
                    "Τετραγωνικά ανά τυπολογία τοίχου, χωριστά ανά όροφο", "θερμοπρόσοψη 10 / 5 cm",
                    "Βάση: κατόψεις τοιχοποιιών " + plans + " · είδη " + kinds, "— · A3", rev, date)
