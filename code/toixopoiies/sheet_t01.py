"""Φύλλο Τ-01: κάτοψη τοιχοποιιών Β΄ ορόφου (Β1), A3, 1:60."""
import math
import b1_model as M
from draw import View, PT_PER_M_60, DARK, GREY, LIGHT, DIMC, BLUE, frame_and_title, north_arrow

OX, OY = 309.5, 99.8   # όπως το R14 (αρχή μοντέλου σε pt, y προς τα κάτω)


def in_mask(seg_pts, masks):
    xs = [p[0] for p in seg_pts]; ys = [p[1] for p in seg_pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    return any(m[0] <= cx <= m[2] and m[1] <= cy <= m[3] for m in masks)


def draw_strokes(v, key, color, lw, masks=None, bbox_filter=None):
    """Σχεδίαση ομάδας γραμμών του R14 (έπιπλα, εξώστες κ.λπ.) εκτός των μασκών."""
    for path in M.GEOM["strokes"].get(key, []):
        pts = []
        for s in path:
            pts += [s[1], s[2]] if s[0] != "c" else [s[1], s[4]]
        if not pts:
            continue
        if masks and in_mask(pts, masks):
            continue
        if bbox_filter and not bbox_filter(pts):
            continue
        for s in path:
            if s[0] == "l":
                v.line(s[1][0], s[1][1], s[2][0], s[2][1], color=color, lw=lw)
            elif s[0] == "re":
                v.rect(s[1][0], s[1][1], s[2][0], s[2][1], stroke=color, lw=lw)
            elif s[0] == "c":
                # bezier → πολυγωνική
                p0, p1, p2, p3 = s[1], s[2], s[3], s[4]
                prev = p0
                for i in range(1, 7):
                    t = i / 6
                    x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
                    y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
                    v.line(prev[0], prev[1], x, y, color=color, lw=lw); prev = (x, y)


def wall_label_pose(w):
    x0, y0, x1, y1 = M.bbox(w["pts"])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = M.wall_length(w)
    vertical = (y1 - y0) > (x1 - x0)
    if not M.is_rect(w["pts"]):   # καμπύλο: ετικέτα στη γωνία του bbox προς τα έξω
        return cx, cy, 0, L
    return cx, cy, (90 if vertical else 0), L


def toilet(v, pos, facing):
    """Λεκάνη: καζανάκι 0,40×0,15 στον τοίχο + λεκάνη οβάλ 0,38×0,55. facing: κατεύθυνση ανοίγματος."""
    x, y = pos
    col = (0.72, 0.72, 0.75)
    if facing == "E":      # τοίχος δυτικά (x = σταθερό), λεκάνη προς +x
        v.rect(x, y - 0.20, x + 0.15, y + 0.20, stroke=col, lw=0.45)
        v.circle(x + 0.15 + 0.27, y, 0.19, stroke=col, lw=0.45)
        v.line(x + 0.15, y - 0.19, x + 0.42, y - 0.19, color=col, lw=0.45)
        v.line(x + 0.15, y + 0.19, x + 0.42, y + 0.19, color=col, lw=0.45)
    else:                  # facing S: τοίχος βόρεια (y = σταθερό), λεκάνη προς +y
        v.rect(x - 0.20, y, x + 0.20, y + 0.15, stroke=col, lw=0.45)
        v.circle(x, y + 0.15 + 0.27, 0.19, stroke=col, lw=0.45)
        v.line(x - 0.19, y + 0.15, x - 0.19, y + 0.42, color=col, lw=0.45)
        v.line(x + 0.19, y + 0.15, x + 0.19, y + 0.42, color=col, lw=0.45)


def wardrobe(v, r, washing=False, depth=0.60):
    x0, y0, x1, y1 = r
    col = (0.62, 0.62, 0.66)
    v.rect(x0, y0, x1, y1, stroke=col, lw=0.4)
    if washing:
        v.rect(x0 + 0.02, y0 + 0.05, x1 - 0.02, y1 - 0.05, stroke=col, lw=0.3)
        v.circle((x0 + x1) / 2, (y0 + y1) / 2, 0.20, stroke=col, lw=0.3)
        v.text((x0 + x1) / 2, (y0 + y1) / 2, "ΠΛ", size=4.2, color=col)
        return
    horiz = (x1 - x0) >= (y1 - y0)
    L = (x1 - x0) if horiz else (y1 - y0)
    n = max(1, round(L / 0.60)); step = L / n
    for i in range(n):
        if horiz:
            a, b = x0 + i * step, x0 + (i + 1) * step
            v.line(a, y0, b, y1, color=col, lw=0.3); v.line(a, y1, b, y0, color=col, lw=0.3)
            if i: v.line(a, y0, a, y1, color=col, lw=0.3)
        else:
            a, b = y0 + i * step, y0 + (i + 1) * step
            v.line(x0, a, x1, b, color=col, lw=0.3); v.line(x0, b, x1, a, color=col, lw=0.3)
            if i: v.line(x0, a, x1, a, color=col, lw=0.3)


def draw_plan(v, with_labels=True, with_dims=True, with_furniture=True, with_text=True, highlight=None):
    """Η κάτοψη. highlight: τύπος → μόνο αυτός χρωματιστός (για τα mini-plans του Τ-02)."""
    # θερμοπρόσοψη
    for poly in M.ETICS:
        v.poly(poly, fill=M.ETICS_FILL if not highlight else (0.96, 0.96, 0.96),
               stroke=(0.55, 0.45, 0.20) if not highlight else LIGHT, lw=0.5 if not highlight else 0.3)
    # εξώστες, κάγκελα, ζαρντινιέρες, σκίαστρο (από R14)
    if with_furniture:
        draw_strokes(v, "(0.3, 0.3, 0.34)|0.60", (0.30, 0.30, 0.34), 0.6)
        draw_strokes(v, "(0.4, 0.4, 0.44)|0.70", (0.40, 0.40, 0.44), 0.7)
        draw_strokes(v, "(0.55, 0.55, 0.58)|0.50", (0.55, 0.55, 0.58), 0.5)
        draw_strokes(v, "(0.1, 0.11, 0.13)|1.10", DARK, 1.1)
        draw_strokes(v, "(0.5, 0.62, 0.5)|0.40", (0.50, 0.62, 0.50), 0.4)
        # έπιπλα αχνά (εκτός μασκών) + εξοπλισμός EPIPLA
        draw_strokes(v, "(0.8, 0.8, 0.82)|0.30", LIGHT, 0.3, masks=M.FURN_MASKS)
        draw_strokes(v, "(0.72, 0.72, 0.75)|0.35", (0.72, 0.72, 0.75), 0.35, masks=M.FURN_MASKS)
        # R15: ντουλάπες χωνευτές + λουτρά
        for wd in M.WARDROBES:
            wardrobe(v, wd["r"], washing=wd.get("washing", False), depth=wd["depth"])
        for b in M.BATHS:
            v.rect(*b["counter"], stroke=(0.72, 0.72, 0.75), lw=0.45)
            toilet(v, *b["toilet"])
            (x0, y0), (x1, y1) = b["screen"]
            v.line(x0, y0, x1, y1, color=(0.30, 0.40, 0.60), lw=0.9)
            if with_text:
                v.text(b["shower_label"][0], b["shower_label"][1], "ΝΤΟΥΣ", size=4.6, color=GREY, font="Inter-Medium")
    # κολόνες / τοιχεία
    for poly in M.COLS:
        v.poly(poly, fill=M.COL_FILL if not highlight else (0.80, 0.80, 0.82), stroke=DARK, lw=0.6)
        if not highlight:
            v.hatch(poly, 0.075, 45, (0.75, 0.75, 0.78), 0.3)
    for poly in M.COLS2:
        v.poly(poly, fill=M.COL2_FILL if not highlight else (0.86, 0.86, 0.88), stroke=DARK, lw=0.6)
    # τοίχοι
    for w in M.WALLS:
        t = M.TYPES[w["type"]]
        if highlight and w["type"] != highlight:
            v.poly(w["pts"], fill=(0.88, 0.88, 0.90), stroke=(0.70, 0.70, 0.72), lw=0.25)
            continue
        v.poly(w["pts"], fill=t["fill"], stroke=DARK, lw=0.6 if not highlight else 0.4)
        if not highlight and w["type"] in ("T1", "T4", "T5"):
            v.brick(w["pts"], course=0.062 if w["type"] != "T4" else 0.05,
                    brick_len=0.13 if w["type"] != "T4" else 0.10)
    # κουφώματα
    for poly in M.WINS:
        x0, y0, x1, y1 = M.bbox(poly)
        v.poly(poly, fill=M.WIN_FILL, stroke=(0.55, 0.60, 0.70), lw=0.3)
        if not highlight:
            if (x1 - x0) >= (y1 - y0):
                ym = (y0 + y1) / 2
                v.line(x0, ym - 0.03, x1, ym - 0.03, color=BLUE, lw=0.6)
                v.line(x0, ym + 0.03, x1, ym + 0.03, color=BLUE, lw=0.6)
            else:
                xm = (x0 + x1) / 2
                v.line(xm - 0.03, y0, xm - 0.03, y1, color=BLUE, lw=0.6)
                v.line(xm + 0.03, y0, xm + 0.03, y1, color=BLUE, lw=0.6)
    if highlight:
        return
    # πόρτες
    for h, l, j in M.DOORS:
        v.door(h, l, j, arc=(h != j))
    # ετικέτες τοίχων
    if with_labels:
        for w in M.WALLS:
            cx, cy, rot, L = wall_label_pose(w)
            if w["id"] in M.LABEL_POS:
                x, y, r, plain = M.LABEL_POS[w["id"]]
                col = {"T3": (0.30, 0.45, 0.75), "T9": (0.45, 0.40, 0.65)}.get(w["type"], DARK)
                if plain or w["type"] in ("T3", "T9"):
                    v.text(x, y, w["id"], size=4.2, rot=r, color=col, font="Inter-Medium")
                else:
                    v.label(x, y, w["id"], rot=r)
                continue
            if w["type"] == "T3" or w["type"] == "T9":
                # επενδύσεις: λεπτές – ετικέτα μπλε χωρίς κουτί, δίπλα στον τοίχο
                x0, y0, x1, y1 = M.bbox(w["pts"])
                if (y1 - y0) > (x1 - x0):
                    v.text(x0 - 0.12 if w["type"] == "T3" else x1 + 0.12, cy, w["id"], size=4.6, rot=90,
                           color=(0.30, 0.45, 0.75) if w["type"] == "T3" else (0.45, 0.40, 0.65), font="Inter-Medium")
                else:
                    v.text(cx, y0 - 0.12 if cy < 5 else y1 + 0.12, w["id"], size=4.6,
                           color=(0.30, 0.45, 0.75) if w["type"] == "T3" else (0.45, 0.40, 0.65), font="Inter-Medium")
                continue
            if L < 0.30 and w["type"] in ("T2", "T4", "T1", "T5"):
                v.text(cx, cy, w["id"], size=3.8, rot=rot, font="Inter-Medium")
            else:
                v.label(cx, cy, w["id"], rot=rot)
    # κείμενα χώρων / κουφωμάτων
    if with_text:
        for name, area, (x, y) in M.ROOMS:
            v.text(x, y, name, size=6.8 if area else 6.4, font="Inter-SemiBold", color=(0.35, 0.35, 0.38))
            if area:
                v.text(x, y + 0.22, area, size=5.6, color=(0.45, 0.45, 0.50))
        for lab, dim, (x, y) in M.WINDOWS:
            v.text(x, y, "%s  %s" % (lab, dim), size=5.2, font="Inter-Medium", color=(0.30, 0.45, 0.75), anchor="l")
        v.text(-1.47, 1.40, "αρχιτεκτονικό στοιχείο – σταθερό σύστημα σκίασης", size=5.6, font="Inter-Medium", color=GREY, rot=90)
        v.text(-1.52, 7.35, "ζαρντινιέρα", size=5.6, font="Inter-Medium", color=(0.40, 0.55, 0.40), rot=90)
        v.text(7.55, 11.90, "ζαρντινιέρα", size=5.6, font="Inter-Medium", color=(0.40, 0.55, 0.40))
    # διαστάσεις
    if with_dims:
        for orient, pos, pts in M.DIMS_IN:
            v.dim_chain(orient, pos, pts, size=5.0, color=DIMC, side=-1)
        for orient, pos, pts in M.DIMS_OUT:
            v.dim_chain(orient, pos, pts, size=5.4 if len(pts) > 2 else 6.2, color=DIMC, side=-1, ext=0.0)
        for x, y, s, horiz in M.THICK_NOTES:
            v.text(x, y, s, size=4.4, color=DIMC, rot=0 if horiz else 90)


def sheet_t01(c):
    v = View(c, OX, OY, PT_PER_M_60)
    draw_plan(v)
    north_arrow(c, 1135, 770)
    frame_and_title(c, "Τ-01", "ΚΑΤΟΨΗ ΤΟΙΧΟΠΟΙΙΩΝ – Β΄ ΟΡΟΦΟΣ",
                    "Είδη τοιχοποιιών · διαστάσεις χάραξης · κουφώματα · εξώστες", "Β΄ ΟΡΟΦΟΣ – Β1",
                    "Βάση: κάτοψη A-10-2F (μελέτη εφαρμογής) · ξυλότυποι Σ · R14 + αλλαγές 05/11",
                    "Κλίμακα 1:60 · A3", M.REV, M.DATE)
    # υπόμνημα αλλαγών R15 (πάνω δεξιά)
    x, y = 905, 800
    c.setFont("Inter-SemiBold", 6.5); c.setFillColorRGB(*DARK)
    c.drawString(x, y, "ΑΛΛΑΓΕΣ R15 (05/11/2026)")
    c.setFont("Inter", 5.6)
    for i, s in enumerate([
        "· Ντουλάπες χωνευτές: δωματίων 0,60 · πλυντηρίου 0,70",
        "· Τ1-05 κομμένος στο 1,35 · Τ3-06 καταργήθηκε · W2.06 → 1,35–2,35 (*)",
        "· Υπν.1: κουτί Τ2-09 (x 4,30–4,40) για χωνευτή ντουλάπα",
        "· Τ2-05 → Τ2N-02 (1 φύλλο προς ντουλάπα)",
        "· Λουτρά: πάγκος 0,50 · λεκάνη · 1 διαχωριστικό ντους",
        "· Αλυσίδες διαστάσεων μέσα στους χώρους (χάραξη)",
        "(*) προς επιβεβαίωση από τον αρχιτέκτονα (όψη)"]):
        c.drawString(x, y - 9 - i * 8, s)
