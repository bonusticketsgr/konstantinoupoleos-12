"""Φύλλα ΧΑΡΑΞΗΣ ανά όροφο (R36 – Γιάννης 27/11/2026: «βάλε τις απαραίτητες διαστάσεις ώστε όταν έρθουν οι μάστορες να χαραχτούν οι
τοίχοι – πρώτα τούβλα, μετά γυψοσανίδες · οι διαστάσεις και οι ετικέτες μην είναι πάνω στους τοίχους»).
Δύο φάσεις: "brick" = τοίχοι από τούβλο (Τ1 / Τ4 / Τ4Α / Τ5 / Τ10) πάνω στο γυμνό σκυρόδεμα · "gyp" = χωρίσματα και επενδύσεις γυψοσανίδας
πάνω σε σκυρόδεμα + χτισμένα τούβλα. Σε κάθε φάση: μόνο οι τοίχοι της φάσης χρωματιστοί (οι άλλοι αχνοί), χωρίς έπιπλα, ετικέτες ΔΙΠΛΑ στους
τοίχους, και για κάθε ΓΡΑΜΜΗ τοίχων: (α) αλυσίδα ΚΑΤΑ ΜΗΚΟΣ (άκρα τοίχων + παρειές κολονών που τέμνει) δίπλα στη γραμμή, (β) αλυσίδα ΘΕΣΗΣ
κάθετα στη γραμμή από την κοντινότερη παρειά αναφοράς (σκυρόδεμα· στη φάση γυψοσανίδας και τούβλο) ως τις δύο παρειές του τοίχου.
Όλα από το μοντέλο – καμία χειροκίνητη διάσταση."""
import math
import b1_model as M
from draw import View, PT_PER_M_60, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow
import sheet_t01

BRICK = ("T1", "T4", "T4A", "T5", "T10")
GYP = ("T2", "T2N", "T2A", "T7", "T7A", "T6", "T6A", "T6B", "T8", "T3", "T3M", "T9")
CLAD = ("T3", "T3M", "T9")
PHASE = {"brick": dict(types=BRICK, title="ΧΑΡΑΞΗ ΤΟΙΧΩΝ ΑΠΟ ΤΟΥΒΛΟ", sub="Φάση 1 – οπτοπλινθοδομές πάνω στον φέροντα οργανισμό", who="χτίστης"),
         "gyp": dict(types=GYP, title="ΧΑΡΑΞΗ ΧΩΡΙΣΜΑΤΩΝ ΓΥΨΟΣΑΝΙΔΑΣ", sub="Φάση 2 – χωρίσματα και επενδύσεις γυψοσανίδας (μετά τα τούβλα)", who="γυψοσανιδάς"),
         "all": dict(types=BRICK + GYP, title="ΧΑΡΑΞΗ ΤΟΙΧΩΝ", sub="Όλοι οι τοίχοι του ορόφου (λίγοι τοίχοι – μία φάση)", who="συνεργείο")}
FADE = (0.90, 0.90, 0.91)


def phase_walls(model, phase):
    ts = PHASE[phase]["types"]
    return [w for w in model.WALLS if w["type"] in ts]


def _rects(model, phase):
    """Παρειές αναφοράς: σκυρόδεμα (ορθογώνια) + στη φάση γυψοσανίδας τα τούβλα."""
    out = [model.bbox(p) for p in model.COLS if model.is_rect(p)]
    if phase != "brick":
        out += [model.bbox(w["pts"]) for w in model.WALLS if w["type"] in BRICK and model.is_rect(w["pts"])]
    return out


def bands(model, walls, horiz):
    items = []
    for w in walls:
        if not model.is_rect(w["pts"]):
            continue
        x0, y0, x1, y1 = model.bbox(w["pts"])
        if ((x1 - x0) >= (y1 - y0)) != horiz:
            continue
        a0, a1 = (y0, y1) if horiz else (x0, x1)
        items.append((a0, a1, w))
    items.sort(key=lambda it: (it[0], it[1]))
    out = []
    for a0, a1, w in items:
        if out and a0 < out[-1][1] + 0.015 and a1 > out[-1][0] - 0.015:
            out[-1][0] = min(out[-1][0], a0); out[-1][1] = max(out[-1][1], a1); out[-1][2].append(w)
        else:
            out.append([a0, a1, [w]])
    return out


def along_chains(model, walls, horiz):
    """[(a0, a1, pts)] – για κάθε γραμμή: άκρα τοίχων + παρειές σκυροδέματος που τέμνουν τη γραμμή (μέσα στο εύρος της)."""
    out = []
    for a0, a1, ws in bands(model, walls, horiz):
        pts = set(); lo, hi = 99, -99
        for w in ws:
            x0, y0, x1, y1 = model.bbox(w["pts"])
            p0, p1 = (x0, x1) if horiz else (y0, y1)
            pts.update([round(p0, 3), round(p1, 3)]); lo, hi = min(lo, p0), max(hi, p1)
        mid = (a0 + a1) / 2
        for col in model.COLS:
            if not model.is_rect(col):
                continue
            x0, y0, x1, y1 = model.bbox(col)
            c0, c1 = (y0, y1) if horiz else (x0, x1)
            if c0 - 0.01 <= mid <= c1 + 0.01:
                p0, p1 = (x0, x1) if horiz else (y0, y1)
                if p1 >= lo - 0.3 and p0 <= hi + 0.3:
                    pts.update([round(p0, 3), round(p1, 3)])
        pts = sorted(pts); merged = []
        for p in pts:
            if merged and p - merged[-1] < 0.015:
                continue
            merged.append(p)
        if len(merged) >= 2:
            out.append((a0, a1, merged, ws))
    return out


def position_chain(model, phase, a0, a1, ws, horiz, taken):
    """Αλυσίδα θέσης κάθετα στη γραμμή: [παρειά αναφοράς, a0, a1] στη μέση του μεγαλύτερου τοίχου της γραμμής.
    Αναφορά = η κοντινότερη παρειά σκυροδέματος (ή τούβλου) που «βλέπει» ο τοίχος κάθετα, ως 6 m."""
    w = max(ws, key=model.wall_length)
    x0, y0, x1, y1 = model.bbox(w["pts"])
    u = (x0 + x1) / 2 if horiz else (y0 + y1) / 2
    # μην πέσει πάνω σε άλλη αλυσίδα θέσης της ίδιας γραμμής-συντεταγμένης
    for tu, ta in taken:
        if abs(tu - u) < 0.35 and (ta[0] <= a1 + 0.5 and ta[1] >= a0 - 0.5):
            u += 0.40
    below, above = None, None
    for rx0, ry0, rx1, ry1 in _rects(model, phase):
        c0, c1, f0, f1 = (rx0, rx1, ry0, ry1) if horiz else (ry0, ry1, rx0, rx1)
        if not (c0 - 0.005 <= u <= c1 + 0.005):
            continue
        if f1 <= a0 + 0.005 and (below is None or f1 > below):
            below = f1
        if f0 >= a1 - 0.005 and (above is None or f0 < above):
            above = f0
    cands = []
    if below is not None and a0 - below > 0.02:
        cands.append((a0 - below, [below, a0, a1], -1))
    if above is not None and above - a1 > 0.02:
        cands.append((above - a1, [a0, a1, above], +1))
    cands = [c for c in cands if c[0] <= 6.0]
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    d, pts, side = cands[0]
    taken.append((u, (a0, a1)))
    return u, pts, side


def draw_phase(v, model, phase):
    """Υπόβαθρο: σκυρόδεμα όπως στην κάτοψη, τοίχοι της φάσης χρωματιστοί, υπόλοιποι αχνοί, κουφώματα, πόρτες· χωρίς έπιπλα."""
    ts = PHASE[phase]["types"]
    for poly in model.ETICS + model.ETICS5:
        v.poly(poly, fill=(0.97, 0.97, 0.97), stroke=LIGHT, lw=0.25)
    for poly in model.COLS:
        v.poly(poly, fill=model.COL_FILL, stroke=DARK, lw=0.85)
        v.hatch(poly, 0.075, 45, (0.75, 0.75, 0.78), 0.3)
    for w in model.WALLS:
        t = model.TYPES[w["type"]]
        if w["type"] in ts:
            v.poly(w["pts"], fill=t["fill"], stroke=DARK, lw=0.75 if t["thick"] >= 0.09 else 0.55)
            if w["type"] in ("T1", "T4", "T4A", "T5", "T10"):
                v.brick(w["pts"], course=0.062 if w["type"] not in ("T4", "T4A") else 0.05, brick_len=0.13 if w["type"] not in ("T4", "T4A") else 0.10)
        else:
            v.poly(w["pts"], fill=FADE if w["type"] in BRICK else (0.95, 0.95, 0.96), stroke=(0.62, 0.62, 0.65), lw=0.3)
    kinds = getattr(model, "WIN_KINDS", {})
    for i, poly in enumerate(model.WINS, 1):
        sheet_t01.draw_window(v, poly, kinds.get(i))
    if phase != "brick":
        sheet_t01.draw_jamb_linings(v)
    for h, l, j in model.DOORS:
        v.door(h, l, j, arc=(h != j))


def sheet_xaraxi(c, model, phase, sheet_no, total=None, plan_ref="Τ-01"):
    sheet_t01.M = model
    ox, oy = getattr(model, "OX", 309.5), getattr(model, "OY", 99.8)
    v = View(c, ox, oy, getattr(model, "PT_PER_M", PT_PER_M_60))
    draw_phase(v, model, phase)
    walls = phase_walls(model, phase)
    bcx, bcy = sheet_t01._building_center()
    # 1) αλυσίδες κατά μήκος κάθε γραμμής – στην πλευρά προς το κέντρο του κτηρίου (μέσα στον χώρο), 0,30 από την παρειά
    taken = []
    for horiz in (True, False):
        for a0, a1, pts, ws in along_chains(model, walls, horiz):
            mid = (a0 + a1) / 2
            centre = bcy if horiz else bcx
            pos = a1 + 0.30 if mid < centre else a0 - 0.30
            side = +1 if mid < centre else -1
            if pts[-1] - pts[0] >= 0.30:
                o = "H" if horiz else "V"
                for extra in (0.0, 0.18, 0.36):          # αν τα νούμερα πέφτουν πάνω σε άλλη αλυσίδα, η γραμμή λίγο πιο μέσα
                    p_ = pos + side * extra
                    v.dry = True; rects = v.dim_chain(o, p_, pts, size=4.6, side=side, tick=0.06); v.dry = False
                    if all(v.free(r, 0.005) for r in rects):
                        break
                v.dim_chain(o, p_, pts, size=4.6, color=DIMC, side=side, tick=0.06)
    # 2) αλυσίδες θέσης (κάθετα) – σε u που δεν πέφτει πάνω σε κείμενο που υπάρχει ήδη
    for horiz in (True, False):
        for a0, a1, pts, ws in along_chains(model, walls, horiz):
            pc = position_chain(model, phase, a0, a1, ws, horiz, taken)
            if not pc:
                continue
            u, ppts, sd = pc
            o = "V" if horiz else "H"
            best = None
            for du in (0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9):
                v.dry = True; rects = v.dim_chain(o, u + du, ppts, size=4.6, side=-1, tick=0.06); v.dry = False
                if all(v.free(r, 0.01) for r in rects):
                    best = u + du; break
            if best is None:
                best = u
            v.dim_chain(o, best, ppts, size=4.6, color=DIMC, side=-1, tick=0.06)
    # 3) εξωτερικές αλυσίδες (περίγραμμα) μόνο στη φάση των τούβλων
    if phase != "gyp":
        for orient, pos, pts in model.DIMS_OUT:
            v.dim_chain(orient, pos, pts, size=5.4 if len(pts) > 2 else 6.2, color=DIMC, side=-1)
    # 4) ονόματα χώρων (αχνά) · 5) ετικέτες τοίχων της φάσης, δίπλα τους, χωρίς επικαλύψεις
    for name, area, (x, y) in model.ROOMS:
        if "ΕΞΩΣΤ" not in name:
            v.text(x, y, name, size=5.2, font="Inter-SemiBold", color=(0.62, 0.62, 0.66), bg=True)
    sheet_t01.place_labels(v, walls)
    north_arrow(c, 1150, 795)
    sheet_t01.scale_bar(c, 1055, 757, getattr(model, "PT_PER_M", PT_PER_M_60))
    SH = getattr(model, "SHEET", sheet_t01.B1_SHEET)
    P = PHASE[phase]
    frame_and_title(c, sheet_no, P["title"] + " – " + SH["floor_short"].upper(), P["sub"] + " · διαστάσεις από παρειές σκυροδέματος" + ("" if phase == "brick" else " / τούβλου"),
                    SH["floor"] + " · χωρίς έπιπλα", "Βάση: κάτοψη τοιχοποιιών " + plan_ref + " (ίδιο μοντέλο) · ξυλότυποι Σ (υποστυλώματα)",
                    getattr(model, "SCALE_TXT", "Κλίμακα 1:60 · A3"), model.REV, model.DATE, total=total)


def phases_for(model):
    """Ποια φύλλα χάραξης βγάζει ο όροφος: τούβλα + γυψοσανίδες· αν η μία φάση έχει < 3 τοίχους, ένα φύλλο «όλοι»."""
    nb = len(phase_walls(model, "brick")); ng = len(phase_walls(model, "gyp"))
    if nb < 3 or ng < 3:
        return ["all"]
    return ["brick", "gyp"]
