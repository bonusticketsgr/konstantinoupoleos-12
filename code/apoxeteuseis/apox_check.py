"""Έλεγχος διαστάσεων του δικτύου αποχέτευσης / ομβρίων (Γιάννης 10/11/2026: «check διαστάσεις τα πάντα»).

Δουλεύει πάνω στο μητρώο apox_pro.REG που γεμίζει όταν σχεδιάζονται οι κατόψεις 1:60 / 1:80 – ελέγχεται δηλαδή ΑΚΡΙΒΩΣ
ό,τι τυπώνεται.  run(...) επιστρέφει λίστα (κατάσταση, ομάδα, κείμενο) με κατάσταση OK / ΟΡΙΑΚΟ / ΛΑΘΟΣ.
Παραδοχές (γράφονται και στο φύλλο ελέγχου): τοίχος λεκάνης Τ7 = 2 γυψ. 2,5 + CW 50 + ΚΕΝΟ 12 + CW 30 + 2 γυψ. 2,5 από την
πλευρά του λουτρού · εξωτ. διάμετροι Φ100 → 110, Φ90 → 90, Φ75 → 75, Φ50 → 50, Φ40 → 40 mm · κλίση ακαθάρτων 2 % ·
γέμισμα δαπέδου 15 cm (σοφίτα 20), ωφέλιμο για σωλήνες = γέμισμα − 3 cm · πρέκια ισογείου +2,85 (0,45 + 2,40)."""
import math

OD = {32: 0.032, 40: 0.040, 50: 0.050, 63: 0.063, 75: 0.075, 90: 0.090, 100: 0.110, 110: 0.110, 125: 0.125}
FILL = {"gf": 0.15, "typ": 0.15, "d4": 0.15, "attic": 0.20}
LINTEL = 2.85
GR = lambda z, n=3: ("%.*f" % (n, z)).replace(".", ",").replace("-", "−")
CM = lambda z: ("%.1f" % (z * 100)).replace(".", ",").replace("-", "−")


def bbox(poly):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def in_poly(pt, poly):
    x, y = pt; ins = False; n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            ins = not ins
    return ins


def d_pt_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(a[0] + t * dx - p[0], a[1] + t * dy - p[1])


def d_pt_poly(p, poly):
    """Απόσταση σημείου από πολύγωνο (αρνητική αν είναι μέσα)."""
    d = min(d_pt_seg(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
    return -d if in_poly(p, poly) else d


def rect_poly(r):
    x0, y0, x1, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def d_seg_poly(a, b, poly, step=0.02):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    return min(d_pt_poly((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n), poly) for i in range(n + 1))


def cavity(M, wid):
    """Το κενό 12 cm του τοίχου λεκάνης wid: (x0, y0, x1, y1), άξονας ('x' αν ο τοίχος τρέχει κατά y), πλαίσιο λεκάνης (a0, a1)."""
    w = next(w for w in M.WALLS if w["id"] == wid); x0, y0, x1, y1 = bbox(w["pts"])
    for b in M.BATHS:
        (tx, ty), face = b["toilet"]
        if abs(tx - x1) < 0.02 and y0 - 0.01 <= ty <= y1 + 0.01:      # λουτρό ανατολικά του τοίχου
            return (x1 - 0.195, y0, x1 - 0.075, y1), "x", (ty - 0.25, ty + 0.25), (x0, y0, x1, y1)
        if abs(tx - x0) < 0.02 and y0 - 0.01 <= ty <= y1 + 0.01:      # λουτρό δυτικά
            return (x0 + 0.075, y0, x0 + 0.195, y1), "x", (ty - 0.25, ty + 0.25), (x0, y0, x1, y1)
        if abs(ty - y1) < 0.02 and x0 - 0.01 <= tx <= x1 + 0.01:      # λουτρό νότια
            return (x0, y1 - 0.195, x1, y1 - 0.075), "y", (tx - 0.25, tx + 0.25), (x0, y0, x1, y1)
        if abs(ty - y0) < 0.02 and x0 - 0.01 <= tx <= x1 + 0.01:      # λουτρό βόρεια
            return (x0, y0 + 0.075, x1, y0 + 0.195), "y", (tx - 0.25, tx + 0.25), (x0, y0, x1, y1)
    raise ValueError("δεν βρέθηκε λεκάνη στον " + wid)


def run(REG, models, stacks_in_walls, holes, slab_concrete, basement, rain):
    """REG: μητρώο · models: {ctx: μοντέλο} · stacks_in_walls: [(ctx, όνομα, τοίχος)] · holes: [dict] ·
    slab_concrete: {πλάκα: (υποστυλώματα [πολύγωνα], δοκοί {όνομα: rect})} · basement: dict · rain: dict."""
    R = []
    add = lambda st, grp, txt: R.append((st, grp, txt))
    by = lambda ctx, typ: [r for r in REG if r[0] == ctx and r[1] == typ]

    # ---------- 1. στήλες λουτρών στο κενό του τοίχου λεκάνης
    for ctx, name, wid, end in stacks_in_walls:
        M = models[ctx]; (gx0, gy0, gx1, gy1), ax, frame, wb = cavity(M, wid)
        if end:                                                    # το κενό συνεχίζει στη γωνία (π.χ. Τ7-02 ως 3,30)
            wb = (wb[0], wb[1], end, wb[3]) if ax == "y" else (wb[0], wb[1], wb[2], end)
        st = [r for r in by(ctx, "stack") if r[5] == name and not r[6]]
        if not st:
            add("ΛΑΘΟΣ", "Στήλες", "%s / %s: δεν βρέθηκε η στήλη στο σχέδιο" % (ctx, name)); continue
        x, y = st[0][4]; r = OD[100] / 2
        if ax == "x":
            c0, c1, c, along, a0, a1 = gx0, gx1, x, y, wb[1], wb[3]
        else:
            c0, c1, c, along, a0, a1 = gy0, gy1, y, x, wb[0], wb[2]
        side = min(c - r - c0, c1 - (c + r))                       # περιθώριο εκατέρωθεν μέσα στο κενό
        ends = min(along - r - a0, a1 - (along + r))               # από τα άκρα του τοίχου
        fr = max(frame[0] - (along + r), (along - r) - frame[1])   # από το πλαίσιο της λεκάνης (50 cm)
        txt = "%s %s στον %s: άξονας %s, κενό %s–%s → περιθώριο %s cm εκατέρωθεν · %s cm από το άκρο του τοίχου · %s cm από το πλαίσιο της λεκάνης" % (
            {"gf": "Ισόγειο", "typ": "Όροφοι", "d4": "Δ΄"}[ctx], name, wid, GR(c), GR(c0), GR(c1), CM(side), CM(ends), CM(fr))
        add("ΛΑΘΟΣ" if side < -0.0005 or fr < 0 or ends < 0 else "ΟΡΙΑΚΟ" if ends < 0.03 or fr < 0.02 else "OK", "Στήλες στο κενό", txt)

    # ---------- 2. αγωγοί «μέσα σε τοίχο»: κάθε κορυφή τους μέσα σε τοίχο / υποστύλωμα (ανοχή 2 cm)
    for ctx, M in models.items():
        for r in by(ctx, "pipe"):
            if r[5] != "wall":
                continue
            pts = r[4]; bad = []
            for p in pts[1:]:
                if not any(d_pt_poly(p, w["pts"]) <= 0.02 for w in M.WALLS):
                    bad.append(p)
            add("ΛΑΘΟΣ" if bad else "OK", "Αγωγοί σε τοίχο", "%s Φ%d %s: %s" % (ctx, r[3], GR(plen(pts), 2) + " m", "εκτός τοίχου στο %s" % bad if bad else "μέσα σε τοίχο"))

    # ---------- 3. αγωγοί στο γέμισμα: πτώση 2 % + διάμετρος ≤ ωφέλιμο· αλυσίδα υποδοχέας → πατοσίφωνο → έξοδος
    for ctx, M in models.items():
        if ctx not in FILL:
            continue
        fill = FILL[ctx]; pipes = [r for r in by(ctx, "pipe") if r[2] in ("waste",) and r[5] == "fill"]
        worst = None
        for r in pipes:
            L = plen(r[4]); need = L * 0.02 + OD[r[3]]
            if worst is None or need > worst[0]:
                worst = (need, L, r[3])
            if need > fill - 0.03:
                add("ΛΑΘΟΣ", "Γέμισμα", "%s Φ%d %s m: θέλει %s cm > ωφέλιμο %s" % (ctx, r[3], GR(L, 2), CM(need), CM(fill - 0.03)))
        if worst:
            add("OK" if worst[0] <= fill - 0.03 else "ΛΑΘΟΣ", "Γέμισμα", "%s: δυσμενέστερος αγωγός στο γέμισμα Φ%d %s m → πτώση 2 %% + διάμετρος = %s cm (ωφέλιμο %s από γέμισμα %s)" % (
                {"gf": "Ισόγειο", "typ": "Όροφοι", "d4": "Δ΄", "attic": "Σοφίτα"}[ctx], worst[2], GR(worst[1], 2), CM(worst[0]), CM(fill - 0.03), CM(fill)))
        for t in by(ctx, "trap"):
            tp = t[4]; ins = [r for r in by(ctx, "pipe") if r[2] == "waste" and math.hypot(r[4][-1][0] - tp[0], r[4][-1][1] - tp[1]) < 0.16]
            outs = [r for r in by(ctx, "pipe") if r[2] == "waste" and math.hypot(r[4][0][0] - tp[0], r[4][0][1] - tp[1]) < 0.16]
            if not ins or not outs:
                add("ΛΑΘΟΣ", "Πατοσίφωνα", "%s %s: %d είσοδοι / %d έξοδοι" % (ctx, t[5], len(ins), len(outs))); continue
            o = outs[0]; Lo = math.hypot(o[4][1][0] - o[4][0][0], o[4][1][1] - o[4][0][1]) if o[5] == "wall" else plen(o[4])
            need = max(plen(r[4]) * 0.02 + OD[r[3]] for r in ins) + 0.02 + Lo * 0.02
            add("OK" if need <= fill - 0.015 else "ΟΡΙΑΚΟ" if need <= fill else "ΛΑΘΟΣ", "Πατοσίφωνα",
                "%s %s: %d υποδοχείς → έξοδος Φ%d · βάθος αλυσίδας %s cm σε γέμισμα %s cm" % (ctx, t[5], len(ins), o[3], CM(need), CM(fill)))
            # πατοσίφωνο όχι κάτω από λεκάνη
            for b in M.BATHS:
                (tx, ty), face = b["toilet"]; ux, uy = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}[face]
                bowl = (min(tx, tx + ux * 0.60) - abs(uy) * 0.20, min(ty, ty + uy * 0.60) - abs(ux) * 0.20,
                        max(tx, tx + ux * 0.60) + abs(uy) * 0.20, max(ty, ty + uy * 0.60) + abs(ux) * 0.20)
                if bowl[0] - 0.075 < tp[0] < bowl[2] + 0.075 and bowl[1] - 0.075 < tp[1] < bowl[3] + 0.075:
                    add("ΛΑΘΟΣ", "Πατοσίφωνα", "%s %s κάτω από τη λεκάνη" % (ctx, t[5]))

    # ---------- 4. συνδεσιμότητα: κάθε αγωγός καταλήγει σε στήλη / πτώση / πατοσίφωνο / άλλον αγωγό
    for ctx in models:
        nodes = [r[4] for r in REG if r[0] == ctx and r[1] in ("stack", "drop", "trap")]
        pp = by(ctx, "pipe"); n_ok = 0
        for r in pp:
            if r[5] in ("bury",) or r[2] == "vent":
                continue
            e = r[4][-1]
            ok = any(math.hypot(e[0] - n[0], e[1] - n[1]) < 0.17 for n in nodes) or any(
                o is not r and min(d_pt_seg(e, a, b) for a, b in zip(o[4], o[4][1:])) < 0.12 for o in pp)
            n_ok += ok
            if not ok:
                add("ΛΑΘΟΣ", "Συνδέσεις", "%s: ο αγωγός Φ%d που τελειώνει στο %s / %s δεν καταλήγει πουθενά" % (ctx, r[3], GR(e[0]), GR(e[1])))
        add("OK", "Συνδέσεις", "%s: %d αγωγοί, όλοι καταλήγουν σε στήλη / πτώση / πατοσίφωνο / αγωγό" % (ctx, n_ok))

    # ---------- 5. οπές πλακών: κουτί 20×20 (box) έξω από υποστυλώματα / δοκούς της ίδιας πλάκας, ο σωλήνας ολόκληρος μέσα στο κουτί
    for h in holes:
        x0, y0, x1, y1 = h["box"]; rr = h["od"] / 2
        mg = min(h["x"] - rr - x0, x1 - h["x"] - rr, h["y"] - rr - y0, y1 - h["y"] - rr)
        add("OK" if mg >= 0.010 else "ΛΑΘΟΣ", "Οπές", "Η%s %s %s: ο σωλήνας μέσα στο κουτί 20×20 με περιθώριο %s cm" % (h["id"], h["name"], h["pipe"], CM(mg)))
        for sl in h["slabs"]:
            if sl not in slab_concrete:
                continue
            cols, beams = slab_concrete[sl]; worst, who = 9, ""
            for nm, rc in [("υποστύλωμα", bbox(p)) for p in cols if len(p) == 4] + list(beams.items()):
                ox = min(x1, rc[2]) - max(x0, rc[0]); oy = min(y1, rc[3]) - max(y0, rc[1])
                gap = -min(ox, oy) if (ox > 0 and oy > 0) else max(-ox, -oy, 0.0) if (ox <= 0 or oy <= 0) else 0.0
                if ox > 1e-6 and oy > 1e-6:
                    gap = -min(ox, oy)
                else:
                    gap = math.hypot(max(-ox, 0.0), max(-oy, 0.0))
                if gap < worst:
                    worst, who = gap, nm
            add("ΛΑΘΟΣ" if worst < -0.004 else "OK", "Οπές", "Η%s %s (%s) κουτί %s–%s / %s–%s: %s" % (h["id"], h["name"], sl, GR(x0, 2), GR(x1, 2), GR(y0, 2), GR(y1, 2),
                ("ΚΟΛΛΗΤΑ στην παρειά (%s), δεν την κόβει" % who) if worst < 0.004 else "%s cm από %s" % (CM(worst), who)))

    # ---------- 6. υπόγειο: κρεμαστοί αγωγοί έξω από υποστυλώματα / τοιχεία και χαμηλή ζώνη· στάθμες συλλεκτήρα
    Yb = basement["model"]; lz = rect_poly(basement["low"]); dmin = 9
    for r in by("ug", "pipe"):
        if r[5] != "hang":
            continue
        rr = OD[r[3]] / 2
        for a, b in zip(r[4], r[4][1:]):
            for poly in Yb.COLS:
                dmin = min(dmin, d_seg_poly(a, b, poly) - rr)
            if d_seg_poly(a, b, lz) - rr < 0:
                add("ΛΑΘΟΣ", "Υπόγειο", "αγωγός Φ%d μέσα στη χαμηλή ζώνη" % r[3])
    add("OK" if dmin >= 0.03 else "ΛΑΘΟΣ", "Υπόγειο", "Κρεμαστοί αγωγοί: ελάχιστη απόσταση από υποστύλωμα / τοιχείο %s cm · κανένας στη χαμηλή ζώνη" % CM(dmin))
    L, ex, hd, sl = basement["L"], basement["exit"], basement["head"], basement["i"]
    add("OK" if 3.00 + ex - 0.07 >= 2.00 else "ΟΡΙΑΚΟ", "Υπόγειο", "Συλλεκτήρας Φ125: %s m × %s %% → κεφαλή %s, έξοδος %s · καθαρό ύψος κάτω από τον αγωγό στην έξοδο ≈ %s m" % (
        GR(L, 1), GR(sl * 100, 0), GR(hd, 2), GR(ex, 2), GR(3.00 + ex - 0.07, 2)))
    cl = basement["coll"]
    for nm, pt, bot in basement["beams"]:
        Lp = 0.0
        for a, b in zip(cl, cl[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1]); t = ((pt[0] - a[0]) * (b[0] - a[0]) + (pt[1] - a[1]) * (b[1] - a[1])) / (d * d)
            if -1e-6 <= t <= 1 + 1e-6 and math.hypot(a[0] + t * (b[0] - a[0]) - pt[0], a[1] + t * (b[1] - a[1]) - pt[1]) < 0.03:
                Lp += t * d; break
            Lp += d
        crown = hd - sl * Lp + 0.125; m = bot - crown
        add("OK" if m >= 0.045 else "ΟΡΙΑΚΟ" if m >= 0 else "ΛΑΘΟΣ", "Υπόγειο", "Συλλεκτήρας κάτω από %s (κάτω παρειά %s): άνω άντυγα %s → περιθώριο %s cm" % (nm, GR(bot, 2), GR(crown, 3), CM(m)))

    # ---------- 7. όμβρια ψηλά: κλίση 2 %, κάτω άντυγα έναντι πρεκιών ισογείου
    G = models["gf"]
    for nm, pts in rain["runs"].items():
        L = plen(pts); z1 = rain["z0"] - rain["i"] * L
        add("OK", "Όμβρια", "%s κλάδος: %s m × 2 %% → +3,30 → +%s (κάτω άντυγα στο τέλος +%s)" % (nm, GR(L, 1), GR(z1, 2), GR(z1 - 0.055, 3)))
        worst = None
        for wi, poly in enumerate(G.WINS, 1):
            x0, y0, x1, y1 = bbox(poly)
            for a, b in zip(pts, pts[1:]):
                n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 0.05))
                for i in range(n + 1):
                    q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                    if d_pt_poly(q, rect_poly((x0, y0, x1, y1))) < 0.45:
                        Lq = plen(pts[:pts.index(a) + 1]) + math.hypot(q[0] - a[0], q[1] - a[1])
                        zb = rain["z0"] - rain["i"] * Lq - 0.055
                        if worst is None or zb < worst[0]:
                            worst = (zb, wi, q)
        if worst:
            m = worst[0] - LINTEL
            add("OK" if m >= 0 else "ΟΡΙΑΚΟ" if m >= -0.03 else "ΛΑΘΟΣ", "Όμβρια",
                "%s κλάδος μπροστά από κουφώματα ισογείου: χαμηλότερη κάτω άντυγα %s στο %s / %s → %s cm %s το πρέκι +2,85" % (
                    nm, GR(worst[0], 3), GR(worst[2][0], 2), GR(worst[2][1], 2), CM(abs(m)), "πάνω από" if m >= 0 else "ΚΑΤΩ από"))

    # ---------- 8. υδρορροές: μέσα στη θερμοπρόσοψη· ΥΔ2 / ΥΔ3 μέσα στα κενά των πλακών
    T = models["typ"]; rr = OD[75] / 2
    for r in by("typ", "stack"):
        if r[2] != "rain" or not r[5]:
            continue
        x, y = r[4]; ins = any(in_poly((x, y), p) for p in list(T.ETICS) + list(T.ETICS5))
        if r[5] in rain.get("slot", ()):
            add("OK" if not ins else "ΛΑΘΟΣ", "Υδρορροές", "%s Φ75 %s / %s: στο κενό, κολλητά στη θερμοπρόσοψη (όχι μέσα της)" % (r[5], GR(x), GR(y)))
        else:
            add("OK" if ins else "ΟΡΙΑΚΟ", "Υδρορροές", "%s Φ75 %s / %s: %s" % (r[5], GR(x), GR(y), "μέσα στη θερμοπρόσοψη" if ins else "ΕΚΤΟΣ πολυγώνου θερμοπρόσοψης του μοντέλου"))
        if r[5] in rain["gaps"]:
            gx0, gy0, gx1, gy1 = rain["gaps"][r[5]]
            ok = gx0 <= x - rr and x + rr <= gx1 and gy0 <= y - rr and y + rr <= gy1
            add("OK" if ok else "ΛΑΘΟΣ", "Υδρορροές", "%s μέσα στο κενό των πλακών (%s–%s × %s–%s): %s" % (r[5], GR(gx0, 2), GR(gx1, 2), GR(gy0, 2), GR(gy1, 2), "ναι – καμία οπή σε εξώστη" if ok else "ΟΧΙ"))
    return R


def summary(R):
    n = {"OK": 0, "ΟΡΙΑΚΟ": 0, "ΛΑΘΟΣ": 0}
    for st, _, _ in R:
        n[st] += 1
    return n
