"""Φύλλο Τ-08 «ΤΕΤΡΑΓΩΝΙΚΑ ΑΝΑ ΤΟΙΧΟ» (R35 – Γιάννης 27/11/2026: «θέλω και στο τέλος φύλλο τετραγωνικών ανά τοίχο»):
κάθε τοίχος του τεύχους σε μία γραμμή – κωδικός · είδος · πάχος · μήκος · m² (= μήκος × ύψος ορόφου, στον άξονα, χωρίς αφαίρεση
κουφωμάτων – ίδια βάση με το Τ-07, ώστε τα σύνολα να ταυτίζονται). Ανά όροφο, με τη σειρά του TYPE_ORDER, υποσύνολο ανά είδος και
σύνολο ορόφου. Οι γραμμές ρέουν σε 4 στήλες ανά φύλλο· αν δεν χωρούν, συνεχίζουν σε επόμενο φύλλο (Τ-08, Τ-09 …)."""
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title

NCOL = 4            # στήλες ανά φύλλο
RH = 8.0            # ύψος γραμμής (pt)
FS = 6.0            # γράμματα
MARG = 34
TOP = PAGE_H - 20 - 32          # κάτω από τον τίτλο του φύλλου
BOTTOM = 20 + 72 + 10           # πάνω από την πινακίδα
# πλάτη υποστηλών (pt): κωδικός · είδος · πάχος · μήκος · m²
CW = [40, 0, 34, 40, 42]


def f2(v, d=2):
    return ("%.*f" % (d, v)).replace(".", ",")


def _rows(models):
    """Λίστα γραμμών: ("floor", τίτλος, υπότιτλος) · ("type", είδος, όνομα) · ("wall", id, πάχος, L, A) · ("sub", κείμενο, A) · ("tot", κείμενο, A, mult) · ("gap",)"""
    rows = []
    for M in models:
        SH = getattr(M, "SHEET", dict(floor="Β΄ ΟΡΟΦΟΣ – Β1", apt="Β1"))
        mult = getattr(M, "MULT", 1)
        rows.append(("floor", SH["floor"] + "  ·  " + M.REV, "H = " + f2(M.H) + " m"))
        grand = 0.0
        for t in M.TYPE_ORDER:
            ws = M.walls_of(t)
            if not ws:
                continue
            tp = M.TYPES[t]
            rows.append(("type", t, tp["name"] + " · " + ("%g" % round(tp["thick"] * 100, 2)).replace(".", ",") + " cm"))
            sub = 0.0
            for w in sorted(ws, key=lambda w_: int(w_["id"].split("-")[-1])):
                L = M.wall_length(w); A = L * M.H; sub += A
                rows.append(("wall", w["id"], ("%g" % round(tp["thick"] * 100, 2)).replace(".", ","), L, A))
            rows.append(("sub", "Σύνολο " + t + " (%d)" % len(ws), sub)); grand += sub
        rows.append(("tot", "ΣΥΝΟΛΟ " + SH["apt"] + (" (ανά όροφο)" if mult > 1 else ""), grand, mult))
        rows.append(("gap",))
    return rows


def _draw_row(c, r, x, y, w):
    cw = list(CW); cw[1] = w - sum(cw)
    xc = [x]
    for v in cw:
        xc.append(xc[-1] + v)
    k = r[0]
    if k == "floor":
        c.setFillColorRGB(*DARK); c.rect(x, y - 2.2, w, RH + 1.5, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont("Inter-Bold", FS + 0.6); c.drawString(x + 4, y, r[1])
        c.setFont("Inter", FS - 0.4); c.drawRightString(x + w - 4, y, r[2])
    elif k == "type":
        c.setFillColorRGB(0.90, 0.90, 0.91); c.rect(x, y - 2.2, w, RH + 1.0, stroke=0, fill=1)
        c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", FS); c.drawString(x + 4, y, r[1])
        c.setFont("Inter", FS - 0.6); s = r[2]
        while c.stringWidth(s, "Inter", FS - 0.6) > w - 34 and len(s) > 3:
            s = s[:-1]
        c.drawString(x + 30, y, s if s == r[2] else s.rstrip() + "…")
    elif k == "wall":
        c.setFillColorRGB(*DARK)
        c.setFont("Inter-Medium", FS); c.drawString(xc[0] + 4, y, r[1])
        c.setFont("Inter", FS)
        c.drawRightString(xc[3] - 5, y, r[2]); c.drawRightString(xc[4] - 5, y, f2(r[3])); c.drawRightString(xc[5] - 4, y, f2(r[4], 1))
        c.setStrokeColorRGB(0.86, 0.86, 0.88); c.setLineWidth(0.25); c.line(x, y - 2.4, x + w, y - 2.4)
    elif k == "sub":
        c.setFillColorRGB(*DARK); c.setFont("Inter-SemiBold", FS); c.drawString(xc[0] + 4, y, r[1])
        c.drawRightString(xc[5] - 4, y, f2(r[2], 1))
        c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4); c.line(x, y + RH - 2.4, x + w, y + RH - 2.4)
    elif k == "tot":
        c.setStrokeColorRGB(*DARK); c.setLineWidth(0.7); c.line(x, y + RH - 2.0, x + w, y + RH - 2.0)
        c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", FS + 0.4); c.drawString(xc[0] + 4, y, r[1])
        c.drawRightString(xc[5] - 4, y, f2(r[2], 1) + " m²")
        if r[3] > 1:
            c.setFont("Inter", FS - 0.4); c.drawString(xc[0] + 4, y - RH, "× %d όροφοι (Α΄ · Β΄ · Γ΄)" % r[3])
            c.setFont("Inter-SemiBold", FS); c.drawRightString(xc[5] - 4, y - RH, f2(r[2] * r[3], 1) + " m²")


def _height(r):
    if r[0] == "gap":
        return RH * 0.9
    if r[0] == "tot" and r[3] > 1:
        return RH * 2
    return RH


def paginate(models):
    rows = _rows(models)
    cap = TOP - BOTTOM
    pages, col, used = [[]], [], 0.0
    for r in rows:
        h = _height(r)
        if used + h > cap and col:
            pages[-1].append(col); col, used = [], 0.0
            if len(pages[-1]) == NCOL:
                pages.append([])
        if r[0] == "gap" and not col:
            continue            # κενό στην αρχή στήλης δεν χρειάζεται
        col.append(r); used += h
    if col:
        pages[-1].append(col)
    return [p for p in pages if p]


def n_pages(models):
    return len(paginate(models))


def sheet_walls(c, models, first_no=8, rev="", date="", total=None, plans="Τ-01…Τ-05", types_no="Τ-06", qty_no="Τ-07"):
    """Σχεδιάζει όλα τα φύλλα «ανά τοίχο» (showPage ανάμεσα). Επιστρέφει πόσα φύλλα έγραψε."""
    pages = paginate(models)
    gap = 18
    colw = (PAGE_W - 2 * MARG - gap * (NCOL - 1)) / NCOL
    names = " · ".join(getattr(M, "SHEET", dict(apt="Β1"))["apt"].upper() for M in models)
    grand = sum(sum(M.wall_length(w) for w in M.WALLS) * M.H * getattr(M, "MULT", 1) for M in models)
    for pi, page in enumerate(pages):
        c.setFont("Inter-Bold", 13); c.setFillColorRGB(*DARK)
        c.drawString(MARG, PAGE_H - 20 - 22, "ΤΕΤΡΑΓΩΝΙΚΑ ΑΝΑ ΤΟΙΧΟ" + (" (συνέχεια)" if pi else ""))
        c.setFont("Inter", 6.6); c.setFillColorRGB(*GREY)
        c.drawString(MARG + 190, PAGE_H - 20 - 22, "m² = μήκος στον άξονα × ύψος ορόφου (πλάκα με πλάκα), χωρίς αφαίρεση κουφωμάτων · ίδια βάση με το " + qty_no + " · αρίθμηση τοίχων όπως οι κατόψεις")
        if pi == len(pages) - 1:
            c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK)
            c.drawRightString(PAGE_W - MARG, PAGE_H - 20 - 22, "ΟΛΟ ΤΟ ΚΤΗΡΙΟ: " + f2(grand, 1) + " m² τοιχοποιίες")
        for ci, col in enumerate(page):
            x = MARG + ci * (colw + gap); y = TOP - RH
            # επικεφαλίδα στηλών
            cw = list(CW); cw[1] = colw - sum(cw); xc = [x]
            for v in cw:
                xc.append(xc[-1] + v)
            c.setFont("Inter-SemiBold", FS - 0.4); c.setFillColorRGB(*GREY)
            c.drawString(xc[0] + 4, y, "Κωδικός"); c.drawString(xc[1] + 4, y, "Είδος")
            c.drawRightString(xc[3] - 5, y, "cm"); c.drawRightString(xc[4] - 5, y, "Μήκος m"); c.drawRightString(xc[5] - 4, y, "m²")
            c.setStrokeColorRGB(*DARK); c.setLineWidth(0.5); c.line(x, y - 2.6, x + colw, y - 2.6)
            y -= RH + 2
            for r in col:
                h = _height(r)
                if r[0] != "gap":
                    _draw_row(c, r, x, y - (h - RH) if r[0] != "tot" else y, colw)
                y -= h
        no = "Τ-%02d" % (first_no + pi)
        frame_and_title(c, no, "ΠΡΟΜΕΤΡΗΣΗ ΑΝΑ ΤΟΙΧΟ – " + names + ("  (%d/%d)" % (pi + 1, len(pages)) if len(pages) > 1 else ""),
                        "Τετραγωνικά κάθε τοίχου, ανά όροφο και είδος", "μήκος στον άξονα × ύψος ορόφου",
                        "Βάση: κατόψεις %s · είδη %s · σύνολα %s" % (plans, types_no, qty_no), "— · A3", rev, date, total=total)
        c.showPage()
    return len(pages)
