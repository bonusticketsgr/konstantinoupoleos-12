"""Φύλλο Τ-01Α: ΧΑΡΑΞΗ ΤΟΙΧΟΠΟΙΙΩΝ – κάτοψη 1:60 χωρίς έπιπλα, με αλυσίδες κατά μήκος κάθε γραμμής τοίχου
(άκρα τοίχων + παρειές υποστυλωμάτων) και πίνακα συντεταγμένων παρειών κάθε τοίχου, για χάραξη από τον εργολάβο."""
import b1_model as M
from draw import View, PT_PER_M_60, DARK, GREY, DIMC, frame_and_title, north_arrow, PAGE_W, PAGE_H
from sheet_t01 import draw_plan

OX, OY = 160.0, 99.8     # η κάτοψη πιο αριστερά – δεξιά ο πίνακας συντεταγμένων
SKIP = ("T3", "T9")      # επενδύσεις: δεν χαράσσονται (ακολουθούν τους τοίχους / κολόνες)


def _bands(walls, horiz):
    """Ομαδοποίηση τοίχων σε γραμμές (ίδιος άξονας): επιστρέφει [(a0, a1, [walls])] στον κάθετο άξονα."""
    items = []
    for w in walls:
        if not M.is_rect(w["pts"]) or w["type"] in SKIP:
            continue
        x0, y0, x1, y1 = M.bbox(w["pts"])
        if ((x1 - x0) >= (y1 - y0)) != horiz:
            continue
        a0, a1 = (y0, y1) if horiz else (x0, x1)
        items.append((a0, a1, w))
    items.sort(key=lambda it: (it[0], it[1]))
    bands = []
    for a0, a1, w in items:
        if bands and a0 < bands[-1][1] + 0.02 and a1 > bands[-1][0] - 0.02:
            bands[-1][0] = min(bands[-1][0], a0); bands[-1][1] = max(bands[-1][1], a1); bands[-1][2].append(w)
        else:
            bands.append([a0, a1, [w]])
    return bands


def chains(horiz):
    """Για κάθε γραμμή τοίχων: σημεία = άκρα τοίχων + παρειές κολονών που τέμνουν τη γραμμή."""
    out = []
    for a0, a1, ws in _bands(M.WALLS, horiz):
        pts = set()
        lo, hi = 99, -99
        for w in ws:
            x0, y0, x1, y1 = M.bbox(w["pts"])
            p0, p1 = (x0, x1) if horiz else (y0, y1)
            pts.update([round(p0, 3), round(p1, 3)]); lo, hi = min(lo, p0), max(hi, p1)
        mid = (a0 + a1) / 2
        for col in M.COLS + M.COLS2:
            x0, y0, x1, y1 = M.bbox(col)
            c0, c1 = (y0, y1) if horiz else (x0, x1)
            if c0 - 0.01 <= mid <= c1 + 0.01:
                p0, p1 = (x0, x1) if horiz else (y0, y1)
                if p1 >= lo - 0.6 and p0 <= hi + 0.6:
                    pts.update([round(p0, 3), round(p1, 3)])
        pts = sorted(pts)
        # συγχώνευση σημείων < 2 cm
        merged = []
        for p in pts:
            if merged and p - merged[-1] < 0.02:
                continue
            merged.append(p)
        if len(merged) >= 2 and merged[-1] - merged[0] >= 0.4:
            out.append((a0, a1, merged, ws))
    return out


def sheet_t01a(c):
    v = View(c, OX, OY, PT_PER_M_60)
    draw_plan(v, with_labels=True, with_dims=False, with_furniture=False, with_text=False)
    for name, area, (x, y) in M.ROOMS:
        if area and "ΕΞΩΣΤ" not in name:
            v.text(x, y, name, size=5.6, font="Inter-SemiBold", color=(0.55, 0.55, 0.58))
    # αλυσίδες κατά μήκος γραμμών τοίχων – οριζόντιες πάνω από τη γραμμή, κατακόρυφες αριστερά
    for a0, a1, pts, ws in chains(True):
        v.dim_chain("H", a0 - 0.14, pts, size=4.2, color=DIMC, side=-1, tick=0.06)
    for a0, a1, pts, ws in chains(False):
        v.dim_chain("V", a0 - 0.14, pts, size=4.2, color=DIMC, side=-1, tick=0.06)
    for orient, pos, pts in M.DIMS_OUT:
        v.dim_chain(orient, pos, pts, size=5.4 if len(pts) > 2 else 6.2, color=DIMC, side=-1)
    north_arrow(c, 845, 790)
    # ---- πίνακας συντεταγμένων παρειών (από την αρχή: εξωτ. Β παρειά Τ4-01 / εξωτ. Δ παρειά Τ4-05)
    x0, y = 880, PAGE_H - 50
    c.setFont("Inter-Bold", 8); c.setFillColorRGB(*DARK); c.drawString(x0, y, "ΣΥΝΤΕΤΑΓΜΕΝΕΣ ΠΑΡΕΙΩΝ ΤΟΙΧΩΝ (m)")
    c.setFont("Inter", 5); c.setFillColorRGB(*GREY)
    c.drawString(x0, y - 9, "x από την εξωτ. Δ παρειά Τ4-05 (→ ανατολή) · y από την εξωτ. Β παρειά Τ4-01 (→ νότο) · χωρίς θερμοπρόσοψη")
    c.drawString(x0, y - 17, "επενδύσεις Τ3 / Τ9 δεν χαράσσονται: ακολουθούν τον τοίχο / την κολόνα που ντύνουν")
    y -= 30
    cols = [("Τοίχος", 34), ("πάχ.", 24), ("x από", 32), ("x έως", 32), ("y από", 32), ("y έως", 32), ("μήκος", 30)]
    xx = x0
    c.setFont("Inter-SemiBold", 5.4); c.setFillColorRGB(*DARK)
    for n, w in cols:
        c.drawString(xx, y, n); xx += w
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4); c.line(x0, y - 3, x0 + sum(w for _, w in cols), y - 3)
    y -= 10
    rows = [w for w in M.WALLS if w["type"] not in SKIP]
    rows.sort(key=lambda w: (M.TYPE_ORDER.index(w["type"]), w["id"]))
    for w in rows:
        bx0, by0, bx1, by1 = M.bbox(w["pts"])
        t = M.TYPES[w["type"]]
        vals = [w["id"], ("%g" % round(t["thick"] * 100, 1)).replace(".", ","),
                "%.2f" % bx0, "%.2f" % bx1, "%.2f" % by0, "%.2f" % by1, "%.2f" % M.wall_length(w)]
        if not M.is_rect(w["pts"]):
            vals[-1] += "*"
        xx = x0
        c.setFillColorRGB(*t["fill"]); c.rect(x0 - 8, y - 1, 5, 5, stroke=0, fill=1)
        c.setFont("Inter", 5.4); c.setFillColorRGB(*DARK)
        for (n, wd), val in zip(cols, vals):
            c.drawString(xx, y, val.replace(".", ",")); xx += wd
        y -= 7.4
        if y < 120:
            x0 += 240; y = PAGE_H - 80
    c.setFont("Inter", 5); c.setFillColorRGB(*GREY)
    c.drawString(880, 108, "* καμπύλο τμήμα (έρκερ): μήκος στον μέσο άξονα του τόξου · Τ6-01: δύο τμήματα (πόρτα εισόδου 5,33–6,30)")
    c.drawString(880, 100, "Οι αλυσίδες της κάτοψης δίνουν, σε κάθε γραμμή τοίχου, τα άκρα των τοίχων και τις παρειές των")
    c.drawString(880, 93, "υποστυλωμάτων ώστε η χάραξη να γίνεται με μετροταινία από τα μπετά. Ανοχή ±1 cm.")
    frame_and_title(c, "Τ-01Α", "ΧΑΡΑΞΗ ΤΟΙΧΟΠΟΙΙΩΝ – Β΄ ΟΡΟΦΟΣ",
                    "Αλυσίδες κατά μήκος κάθε γραμμής τοίχου · συντεταγμένες παρειών", "Β΄ ΟΡΟΦΟΣ – Β1 · χωρίς έπιπλα",
                    "Βάση: κάτοψη τοιχοποιιών Τ-01 · ξυλότυποι Σ (υποστυλώματα)", "Κλίμακα 1:60 · A3", M.REV, M.DATE)
