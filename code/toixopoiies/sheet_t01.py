"""Φύλλο Τ-01: κάτοψη τοιχοποιιών Β΄ ορόφου (Β1), A3, 1:60."""
import math
import b1_model as M
from draw import View, PT_PER_M_60, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, BLUE, frame_and_title, north_arrow

B1_SHEET = dict(floor="Β΄ ΟΡΟΦΟΣ – Β1", floor_short="Β΄ ΟΡΟΦΟΥ", apt="Β1",
                base="Βάση: κάτοψη A-10-2F (μελέτη εφαρμογής) · ξυλότυποι Σ · R14 + αλλαγές 05/11", arch="A-10-2F")
OX, OY = getattr(M, "OX", 309.5), getattr(M, "OY", 99.8)   # όπως το R14 (αρχή μοντέλου σε pt, y προς τα κάτω)


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


def _draw_paths(v, paths, color_fn, clip_building=None, lw=(0.25, 0.4, 0.6)):
    """Σχεδίαση διανυσματικών paths του αρχιτεκτονικού (m μοντέλου): l / c / re / qu. clip_building: πολύγωνο που
    εξαιρείται (even-odd clip: πλαίσιο σελίδας − πολύγωνο)."""
    c = v.c; c.saveState()
    if clip_building:
        p = c.beginPath(); p.rect(20, 20, PAGE_W - 40, PAGE_H - 40)
        p.moveTo(*v.p(*clip_building[0]))
        for q in clip_building[1:]:
            p.lineTo(*v.p(*q))
        p.close()
        from reportlab.pdfgen.canvas import FILL_EVEN_ODD
        c.clipPath(p, stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    for d in paths:
        if d["f"]:
            c.setFillColorRGB(*color_fn(d["f"]))
        if d["c"]:
            c.setStrokeColorRGB(*color_fn(d["c"]))
        w = d["w"]; c.setLineWidth(lw[0] if w < 0.5 else (lw[1] if w < 1.0 else lw[2]))
        pth = c.beginPath(); cur = None
        for it in d["items"]:
            if it[0] == "l":
                a = v.p(it[1], it[2]); b = v.p(it[3], it[4])
                if cur != a:
                    pth.moveTo(*a)
                pth.lineTo(*b); cur = b
            elif it[0] == "c":
                a = v.p(it[1], it[2]); p1 = v.p(it[3], it[4]); p2 = v.p(it[5], it[6]); b = v.p(it[7], it[8])
                if cur != a:
                    pth.moveTo(*a)
                pth.curveTo(p1[0], p1[1], p2[0], p2[1], b[0], b[1]); cur = b
            elif it[0] == "re":
                x0, y0 = v.p(it[1], it[2]); x1, y1 = v.p(it[3], it[4])
                pth.rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)); cur = None
            elif it[0] == "qu":
                q = [v.p(it[i], it[i + 1]) for i in (1, 3, 5, 7)]
                pth.moveTo(*q[0])
                for z in q[1:]:
                    pth.lineTo(*z)
                pth.close(); cur = None
        if d["closed"]:
            pth.close()
        c.drawPath(pth, stroke=1 if d["c"] else 0, fill=1 if d["f"] else 0)
    c.restoreState()


def draw_site(v):
    """Περιβάλλων χώρος (ισόγειο): η διανυσματική γεωμετρία του αρχιτεκτονικού χωρίς κείμενα / διαστάσεις, αχνά,
    κομμένη έξω από το περίγραμμα του κτιρίου."""
    S = getattr(M, "SITE", None)
    if not S:
        return
    import json
    k = S.get("fade", 0.5)
    _draw_paths(v, json.load(open(S["json"])), lambda rgb: tuple(1 - (1 - ch) * k for ch in rgb), clip_building=S["building"])


def draw_furn(v):
    """Έπιπλα από το layer EPIPLA του αρχιτεκτονικού (ισόγειο): αχνά, ενιαίο γκρι, όπως τα έπιπλα του Β1."""
    F = getattr(M, "FURN_PATHS", None)
    if not F:
        return
    import json
    col = F.get("color", (0.72, 0.72, 0.75))
    paths = json.load(open(F["json"]))
    # R05: μετατόπιση ομάδων επίπλων (π.χ. καναπές / τραπεζαρία όταν μετακινείται τοίχος): [((x0, y0, x1, y1), dx, dy), ...]
    for (bx0, by0, bx1, by1), dx, dy in F.get("shift", []):
        for d in paths:
            xs = [c for it in d["items"] for c in it[1::2]]; ys = [c for it in d["items"] for c in it[2::2]]
            if xs and bx0 <= min(xs) and max(xs) <= bx1 and by0 <= min(ys) and max(ys) <= by1:
                for it in d["items"]:
                    for i in range(1, len(it), 2):
                        it[i] += dx; it[i + 1] += dy
    _draw_paths(v, paths, lambda rgb: col, lw=(0.3, 0.35, 0.4))


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
    elif facing == "W":    # τοίχος ανατολικά (x = σταθερό), λεκάνη προς −x
        v.rect(x - 0.15, y - 0.20, x, y + 0.20, stroke=col, lw=0.45)
        v.circle(x - 0.15 - 0.27, y, 0.19, stroke=col, lw=0.45)
        v.line(x - 0.15, y - 0.19, x - 0.42, y - 0.19, color=col, lw=0.45)
        v.line(x - 0.15, y + 0.19, x - 0.42, y + 0.19, color=col, lw=0.45)
    elif facing == "N":    # τοίχος νότια (y = σταθερό), λεκάνη προς −y
        v.rect(x - 0.20, y - 0.15, x + 0.20, y, stroke=col, lw=0.45)
        v.circle(x, y - 0.15 - 0.27, 0.19, stroke=col, lw=0.45)
        v.line(x - 0.19, y - 0.15, x - 0.19, y - 0.42, color=col, lw=0.45)
        v.line(x + 0.19, y - 0.15, x + 0.19, y - 0.42, color=col, lw=0.45)
    else:                  # facing S: τοίχος βόρεια (y = σταθερό), λεκάνη προς +y
        v.rect(x - 0.20, y, x + 0.20, y + 0.15, stroke=col, lw=0.45)
        v.circle(x, y + 0.15 + 0.27, 0.19, stroke=col, lw=0.45)
        v.line(x - 0.19, y + 0.15, x - 0.19, y + 0.42, color=col, lw=0.45)
        v.line(x + 0.19, y + 0.15, x + 0.19, y + 0.42, color=col, lw=0.45)


def wardrobe(v, r, washing=False, depth=0.60, joinery=False, poly=None):
    x0, y0, x1, y1 = r
    col = (0.62, 0.62, 0.66)
    if joinery:   # ξυλουργικό που συνεχίζει τη ντουλάπα (διακεκομμένο) – poly: περίγραμμα ως το γυμνό τοιχείο
        pts = poly or [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            if abs(ay - y1) < 1e-6 and abs(by - y1) < 1e-6:
                continue   # η πλευρά προς τη ντουλάπα μένει ανοιχτή
            v.line(ax, ay, bx, by, color=col, lw=0.5, dash=[2, 1.5])
        v.text(x0 + 0.10, (y0 + y1) / 2, "ΞΥΛ.", size=3.8, color=col, rot=90)
        return
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


def equip(v, item, with_text=True):
    """Εξοπλισμός κουζίνας / κρεβάτι (αχνά, R05): ("rect"|"tall"|"appl"|"hob"|"sink"|"bed"|"seat"|"sofa", x0, y0, x1, y1[, κείμενο])."""
    kind, x0, y0, x1, y1 = item[:5]
    lab = item[5] if len(item) > 5 else ""
    col = (0.62, 0.62, 0.66); tcol = (0.55, 0.55, 0.60)   # R12/R23: λίγο πιο σκούρα από τα έπιπλα του R14 (0,72) ώστε να διαβάζονται
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind != "seat":
        v.rect(x0, y0, x1, y1, stroke=col, lw=0.5 if kind != "rect" else 0.45)
    if kind == "seat":            # σκαμπό / κάθισμα νησίδας: κύκλος (R06)
        v.circle(cx, cy, min(x1 - x0, y1 - y0) / 2, stroke=col, lw=0.35)
    elif kind == "sofa":          # καναπές: πλάτη 0,20 (item[6] = πλευρά πλάτης N/W/E/S, προεπιλογή N) + μπράτσα 0,15 + διαχωριστικό μαξιλαριών (R06)
        back = item[6] if len(item) > 6 else "N"
        if back == "N":
            v.line(x0, y0 + 0.20, x1, y0 + 0.20, color=col, lw=0.3)
            v.line(x0 + 0.15, y0 + 0.20, x0 + 0.15, y1, color=col, lw=0.3); v.line(x1 - 0.15, y0 + 0.20, x1 - 0.15, y1, color=col, lw=0.3)
            v.line(cx, y0 + 0.20, cx, y1, color=col, lw=0.3)
        elif back == "S":
            v.line(x0, y1 - 0.20, x1, y1 - 0.20, color=col, lw=0.3)
            v.line(x0 + 0.15, y0, x0 + 0.15, y1 - 0.20, color=col, lw=0.3); v.line(x1 - 0.15, y0, x1 - 0.15, y1 - 0.20, color=col, lw=0.3)
            v.line(cx, y0, cx, y1 - 0.20, color=col, lw=0.3)
        else:
            bx = x0 + 0.20 if back == "W" else x1 - 0.20
            sx0, sx1 = (bx, x1) if back == "W" else (x0, bx)
            v.line(bx, y0, bx, y1, color=col, lw=0.3)
            v.line(sx0, y0 + 0.15, sx1, y0 + 0.15, color=col, lw=0.3); v.line(sx0, y1 - 0.15, sx1, y1 - 0.15, color=col, lw=0.3)
            v.line(sx0, cy, sx1, cy, color=col, lw=0.3)
    elif kind == "tall":            # ψηλό ντουλάπι (ψυγείο / φούρνος): Χ
        v.line(x0, y0, x1, y1, color=col, lw=0.3); v.line(x0, y1, x1, y0, color=col, lw=0.3)
    elif kind == "appl":          # πλυντήριο ρούχων / πιάτων: κύκλος
        v.circle(cx, cy, min(x1 - x0, y1 - y0) * 0.32, stroke=col, lw=0.3)
    elif kind == "hob":           # εστίες: 4 κύκλοι
        for fx in (0.28, 0.72):
            for fy in (0.28, 0.72):
                v.circle(x0 + fx * (x1 - x0), y0 + fy * (y1 - y0), 0.085, stroke=col, lw=0.3)
    elif kind == "sink":          # νεροχύτης: εσωτερική λεκάνη + βρύση
        horiz = (x1 - x0) >= (y1 - y0)
        if horiz:
            v.rect(x0 + 0.08, y0 + 0.10, x1 - 0.08, y1 - 0.12, stroke=col, lw=0.3); v.circle(cx, y1 - 0.06, 0.03, stroke=col, lw=0.3)
        else:
            v.rect(x0 + 0.10, y0 + 0.08, x1 - 0.12, y1 - 0.08, stroke=col, lw=0.3); v.circle(x1 - 0.06, cy, 0.03, stroke=col, lw=0.3)
    elif kind == "chair":         # καρέκλα: τετράγωνο + πλάτη (lab = πλευρά πλάτης N/S/E/W) (R12)
        side = lab or "N"; lab = ""
        if side == "N": v.line(x0, y0 + 0.06, x1, y0 + 0.06, color=col, lw=0.3)
        elif side == "S": v.line(x0, y1 - 0.06, x1, y1 - 0.06, color=col, lw=0.3)
        elif side == "W": v.line(x0 + 0.06, y0, x0 + 0.06, y1, color=col, lw=0.3)
        else: v.line(x1 - 0.06, y0, x1 - 0.06, y1, color=col, lw=0.3)
    elif kind == "arm":           # πολυθρόνα: πλάτη 0,15 (lab = πλευρά πλάτης) + μπράτσα 0,12 (R12)
        side = lab or "E"; lab = ""
        if side in ("E", "W"):
            bx = x1 - 0.15 if side == "E" else x0 + 0.15
            v.line(bx, y0, bx, y1, color=col, lw=0.3)
            sx0, sx1 = (x0, bx) if side == "E" else (bx, x1)
            v.line(sx0, y0 + 0.12, sx1, y0 + 0.12, color=col, lw=0.3); v.line(sx0, y1 - 0.12, sx1, y1 - 0.12, color=col, lw=0.3)
        else:
            by = y1 - 0.15 if side == "S" else y0 + 0.15
            v.line(x0, by, x1, by, color=col, lw=0.3)
            sy0, sy1 = (y0, by) if side == "S" else (by, y1)
            v.line(x0 + 0.12, sy0, x0 + 0.12, sy1, color=col, lw=0.3); v.line(x1 - 0.12, sy0, x1 - 0.12, sy1, color=col, lw=0.3)
    elif kind == "tv":            # έπιπλο TV: ορθογώνιο + οθόνη (λεπτή γραμμή στη μέση του μήκους) (R12)
        horiz = (x1 - x0) >= (y1 - y0)
        if horiz: v.rect(cx - 0.55, cy - 0.03, cx + 0.55, cy + 0.03, stroke=col, lw=0.3)
        else: v.rect(cx - 0.03, cy - 0.55, cx + 0.03, cy + 0.55, stroke=col, lw=0.3)
    elif kind == "bed":           # κρεβάτι: κεφαλάρι (lab = πλευρά W/E/N/S) + 2 μαξιλάρια
        side = lab or "W"; lab = ""
        if side in ("W", "E"):
            hx = x0 + 0.08 if side == "W" else x1 - 0.08
            v.line(hx + (0.40 if side == "W" else -0.40), y0, hx + (0.40 if side == "W" else -0.40), y1, color=col, lw=0.3)
            for (a, b) in ((y0 + 0.10, cy - 0.05), (cy + 0.05, y1 - 0.10)):
                v.rect(min(hx, hx + (0.32 if side == "W" else -0.32)), a, max(hx, hx + (0.32 if side == "W" else -0.32)), b, stroke=col, lw=0.3)
        else:
            hy = y0 + 0.08 if side == "N" else y1 - 0.08
            v.line(x0, hy + (0.40 if side == "N" else -0.40), x1, hy + (0.40 if side == "N" else -0.40), color=col, lw=0.3)
            for (a, b) in ((x0 + 0.10, cx - 0.05), (cx + 0.05, x1 - 0.10)):
                v.rect(a, min(hy, hy + (0.32 if side == "N" else -0.32)), b, max(hy, hy + (0.32 if side == "N" else -0.32)), stroke=col, lw=0.3)
    if lab and with_text:
        v.text(cx, cy, lab, size=3.4, color=tcol, rot=90 if (y1 - y0) > (x1 - x0) * 1.3 else 0)


def draw_core(v):
    """Σκάλα και ανελκυστήρας αχνά (γκρι)."""
    import math
    col = (0.70, 0.70, 0.74); lw = 0.35
    S = M.STAIR; x0, y0, x1, y1 = S["hall"]; lx = S["landing_x"]; wy = S["well_y"]; tr = S["tread"]
    cx, cy = S["fan_center"]
    lx0 = S.get("lower_x0", lx)                                   # σοφίτα: το κάτω σκέλος ξεκινά ανατολικά του καμπύλου τοίχου
    up_dash = None if S.get("top") else [1.5, 1.2]                # σοφίτα: όλα τα σκαλοπάτια κάτω από την τομή (η σκάλα φτάνει)
    if not S.get("no_landing_line"):
        v.line(lx, y0, lx, y1, color=col, lw=lw)                  # άκρη πλατύσκαλου
    v.line(lx0, wy, x1, wy, color=col, lw=lw)                     # διαχωριστική σκελών
    for i in range(1, S["n_lower"]):                              # κάτω σκέλος (ανεβαίνει ανατολικά)
        x = lx0 + tr * i
        if x < cx: v.line(x, wy, x, y1, color=col, lw=lw)
    for i in range(1, S["n_upper"]):                              # πάνω σκέλος (επιστρέφει δυτικά) – διακεκομμένο πάνω από την τομή
        x = cx - tr * i
        if x > lx: v.line(x, y0, x, wy, color=col, lw=lw, dash=up_dash)
    n = S["fan_steps"] + 1                                        # σφηνοειδή: ακτίνες από το κέντρο στην περίμετρο
    for k in range(n):
        a = math.radians(90 - 180 * k / (n - 1))                  # 90 = νότος … −90 = βορράς (μέσω ανατολής)
        dx, dy = math.cos(a), math.sin(a)
        ts = []
        if dx > 1e-6: ts.append((x1 - cx) / dx)
        if dy > 1e-6: ts.append((y1 - cy) / dy)
        if dy < -1e-6: ts.append((y0 - cy) / dy)
        tmin = min(ts)
        v.line(cx, cy, cx + dx * tmin, cy + dy * tmin, color=col, lw=lw, dash=None if (k < 4 or S.get("top")) else [1.5, 1.2])
    # γραμμή ανόδου με βέλος
    ya = (wy + y1) / 2
    v.line(lx - 0.5, ya, cx + 0.3, ya, color=col, lw=0.5)
    v.line(cx + 0.3, ya, cx + 0.3, (y0 + wy) / 2, color=col, lw=0.5, dash=[1.5, 1.2])
    v.line(cx + 0.3, (y0 + wy) / 2, lx + 0.4, (y0 + wy) / 2, color=col, lw=0.5, dash=[1.5, 1.2])
    v.line(lx + 0.4, (y0 + wy) / 2, lx + 0.55, (y0 + wy) / 2 - 0.08, color=col, lw=0.5)
    v.line(lx + 0.4, (y0 + wy) / 2, lx + 0.55, (y0 + wy) / 2 + 0.08, color=col, lw=0.5)
    v.circle(lx - 0.5, ya, 0.05, stroke=col, lw=0.5)
    v.text(lx - 0.25, ya - 0.15, "ΑΝΟΔΟΣ", size=3.8, color=col)
    # ανελκυστήρας: θάλαμος + συρόμενη πόρτα στη δυτική παρειά
    L = M.LIFT; sx0, sy0, sx1, sy1 = L["shaft"]; c0, c1, c2, c3 = L["cabin"]
    v.rect(c0, c1, c2, c3, stroke=col, lw=lw)
    v.line(c0, c1, c2, c3, color=col, lw=0.25); v.line(c0, c3, c2, c1, color=col, lw=0.25)
    dx_, dy0, dy1 = L["door"]      # δίφυλλη συρόμενη πόρτα 0,90 στον άξονα του μετώπου Τ10 (x 11,175)
    v.rect(dx_ - 0.03, dy0, dx_ + 0.01, (dy0 + dy1) / 2, stroke=(0.45, 0.45, 0.5), lw=0.5)
    v.rect(dx_ - 0.01, (dy0 + dy1) / 2, dx_ + 0.03, dy1, stroke=(0.45, 0.45, 0.5), lw=0.5)
    v.text(dx_ + 0.22, (dy0 + dy1) / 2, "0,90", size=3.8, color=col, rot=90)



ALU = (0.30, 0.30, 0.34)        # προφίλ αλουμινίου (κάσα / ορθοστάτες φύλλων)
LEAF = (0.86, 0.86, 0.88)       # σώμα φύλλου


def draw_window(v, poly, kind=None):
    """Κούφωμα αλουμινίου σε κάτοψη (R13/R24/R03): κάσα ≈ 9 cm στον άξονα του τοίχου με λαμπάδες (πλήρεις ορθοστάτες), φύλλα και
    τζάμι ως λεπτή μπλε γραμμή. Είδη: "S2" συρόμενο δίφυλλο επάλληλο (ELVIAL 6700 – δύο φύλλα σε δύο οδηγούς, επικάλυψη στη μέση),
    "C1" ανοιγόμενο μονόφυλλο (κλειστό), "F" σταθερό, "D" πόρτα (μόνο κάσα – το φύλλο από τα DOORS). Σύνθετο = λίστα [(είδος, μήκος)].
    Προεπιλογή: ≥ 1,20 m συρόμενο, αλλιώς ανοιγόμενο. Δουλεύει και σε λοξό κούφωμα (W2.03 Β1): τοπικοί άξονες u (κατά μήκος) / n."""
    (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = poly[:4]
    # μακριά πλευρά: p0→p1 ή p1→p2
    if math.hypot(bx - ax, by - ay) >= math.hypot(cx_ - bx, cy_ - by):
        o = ((ax + dx) / 2, (ay + dy) / 2); e = ((bx + cx_) / 2, (by + cy_) / 2); t = math.hypot(dx - ax, dy - ay)
    else:
        o = ((ax + bx) / 2, (ay + by) / 2); e = ((dx + cx_) / 2, (dy + cy_) / 2); t = math.hypot(bx - ax, by - ay)
    L = math.hypot(e[0] - o[0], e[1] - o[1]); ux, uy = (e[0] - o[0]) / L, (e[1] - o[1]) / L; nx, ny = -uy, ux

    def P(a, b):
        return [o[0] + a * ux + b * nx, o[1] + a * uy + b * ny]

    def R(a0, b0, a1, b1, **kw):
        v.poly([P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)], **kw)

    def Ln(a0, b0, a1, b1, **kw):
        p, q = P(a0, b0), P(a1, b1); v.line(p[0], p[1], q[0], q[1], **kw)

    d = min(0.09, t - 0.02)            # βάθος κάσας
    v.poly(poly, fill=(1, 1, 1), stroke=None)                      # άνοιγμα στον τοίχο
    Ln(0, -t / 2, L, -t / 2, color=(0.70, 0.70, 0.72), lw=0.25); Ln(0, t / 2, L, t / 2, color=(0.70, 0.70, 0.72), lw=0.25)   # ποδιά / πρέκι
    segs = kind if isinstance(kind, list) else [(kind or ("S2" if L >= 1.20 else "C1"), L)]
    a = 0.0
    for k, Ls in segs:
        J = 0.06                                                    # λαμπάς κάσας
        R(a, -d / 2, a + Ls, d / 2, fill=None, stroke=DARK, lw=0.35)
        R(a, -d / 2, a + J, d / 2, fill=ALU, stroke=None); R(a + Ls - J, -d / 2, a + Ls, d / 2, fill=ALU, stroke=None)
        if k == "F":
            Ln(a + J, 0, a + Ls - J, 0, color=BLUE, lw=0.7)
        elif k == "C1":
            R(a + J, -d / 2 + 0.015, a + Ls - J, d / 2 - 0.015, fill=LEAF, stroke=DARK, lw=0.3)
            R(a + J, -d / 2 + 0.015, a + J + 0.04, d / 2 - 0.015, fill=ALU, stroke=None)
            R(a + Ls - J - 0.04, -d / 2 + 0.015, a + Ls - J, d / 2 - 0.015, fill=ALU, stroke=None)
            Ln(a + J + 0.04, 0, a + Ls - J - 0.04, 0, color=BLUE, lw=0.7)
        elif k == "S2":
            m = a + Ls / 2; h = d / 2 - 0.012
            for (s0, s1, b0, b1) in ((a + J, m + 0.03, -h, -0.004), (m - 0.03, a + Ls - J, 0.004, h)):
                R(s0, b0, s1, b1, fill=LEAF, stroke=DARK, lw=0.3)
                R(s0, b0, s0 + 0.04, b1, fill=ALU, stroke=None); R(s1 - 0.04, b0, s1, b1, fill=ALU, stroke=None)
                Ln(s0 + 0.04, (b0 + b1) / 2, s1 - 0.04, (b0 + b1) / 2, color=BLUE, lw=0.7)
        # "D": μόνο κάσα – το φύλλο και το τόξο από τα DOORS
        a += Ls

def draw_plan(v, with_labels=True, with_dims=True, with_furniture=True, with_text=True, highlight=None):
    """Η κάτοψη. highlight: τύπος → μόνο αυτός χρωματιστός (για τα mini-plans του Τ-02)."""
    # δάπεδα εξωστών / βεραντών (μπεζ, όπως R14) – κάτω από τη γεωμετρία του περιβάλλοντος χώρου
    if with_furniture:
        for poly in M.FLOORS:
            v.poly(poly, fill=(0.975, 0.97, 0.95))
    if with_furniture and not highlight:
        draw_site(v)
    # θερμοπρόσοψη: 10 cm διαμερίσματα · 5 cm πυρήνας
    for poly in M.ETICS:
        v.poly(poly, fill=M.ETICS_FILL if not highlight else (0.96, 0.96, 0.96),
               stroke=(0.55, 0.45, 0.20) if not highlight else LIGHT, lw=0.5 if not highlight else 0.3)
    for poly in M.ETICS5:
        v.poly(poly, fill=M.ETICS5_FILL if not highlight else (0.96, 0.96, 0.96),
               stroke=(0.55, 0.45, 0.20) if not highlight else LIGHT, lw=0.5 if not highlight else 0.3)
    if with_text and not highlight:
        for lx, ly, lrot in getattr(M, "ETICS5_LABELS", [(12.45, 2.82, 0), (13.52, 6.70, 90)]):
            v.text(lx, ly, "ETICS 5 cm", size=3.8, color=(0.55, 0.45, 0.20), font="Inter-Medium", rot=lrot)
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
        for wx0, wy0, wx1, wy1 in getattr(M, "FURN_WHITEOUT", []):   # R22: σβήσιμο τμημάτων των επίπλων του R14 (πάγκος κουζίνας Β1)
            v.rect(wx0, wy0, wx1, wy1, fill=(1, 1, 1))
        for ln in getattr(M, "EXTRA_LINES", []):                          # R22: πρόσθετες γραμμές επίπλων (ίσιο κλείσιμο πάγκου)
            (ax, ay), (bx, by) = ln[0], ln[1]
            v.line(ax, ay, bx, by, color=(0.72, 0.72, 0.75), lw=0.35, dash=[2, 1.5] if len(ln) > 2 else None)
        draw_core(v)
        draw_furn(v)
        # απλά έπιπλα του μοντέλου (αχνά): πάγκοι κουζίνας, εξοπλισμός
        for fx0, fy0, fx1, fy1, ftxt in getattr(M, "FURN", []):
            v.rect(fx0, fy0, fx1, fy1, stroke=(0.72, 0.72, 0.75), lw=0.4)
            if ftxt and with_text:
                v.text((fx0 + fx1) / 2, (fy0 + fy1) / 2, ftxt, size=3.6, color=(0.62, 0.62, 0.66),
                       rot=90 if (fy1 - fy0) > (fx1 - fx0) else 0)
        for cx_, cy_, cr_, ctxt in getattr(M, "CIRCLES", []):      # π.χ. κύκλος περιστροφής ΑΜΕΑ (ισόγειο)
            v.circle(cx_, cy_, cr_, stroke=(0.72, 0.72, 0.75), lw=0.4)
            if ctxt and with_text:
                v.text(cx_, cy_ + cr_ + 0.12, ctxt, size=3.6, color=(0.62, 0.62, 0.66))
        for item in getattr(M, "EQUIP", []):                          # κουζίνα / κρεβάτι (ισόγειο R05)
            equip(v, item, with_text)
        # R15: ντουλάπες χωνευτές + λουτρά
        for wd in M.WARDROBES:
            wardrobe(v, wd["r"], washing=wd.get("washing", False), depth=wd["depth"], joinery=wd.get("joinery", False), poly=wd.get("poly"))
        for b in M.BATHS:
            v.rect(*b["counter"], stroke=(0.72, 0.72, 0.75), lw=0.45)
            toilet(v, *b["toilet"])
            if not b.get("shower"):
                continue
            sx0, sy0, sx1, sy1 = b["shower"]
            for (ax, ay, bx, by) in [(sx0, sy0, sx1, sy0), (sx1, sy0, sx1, sy1), (sx1, sy1, sx0, sy1), (sx0, sy1, sx0, sy0)]:
                v.line(ax, ay, bx, by, color=(0.60, 0.65, 0.75), lw=0.4, dash=[2, 1.5])
            (x0, y0), (x1, y1) = b["screen"]
            v.line(x0, y0, x1, y1, color=(0.30, 0.40, 0.60), lw=1.2)
            if with_text:
                gl = b["glass_label"]
                v.text(gl[0], gl[1], "γυαλί 0,70", size=4.2, color=(0.30, 0.40, 0.60), rot=0 if y0 == y1 else 90)
                v.text(b["shower_label"][0], b["shower_label"][1], "ΝΤΟΥΣ", size=4.6, color=GREY, font="Inter-Medium")
                v.text(b["shower_label"][0], b["shower_label"][1] + 0.16, b["shower_dim"], size=4.0, color=GREY)
    # κολόνες / τοιχεία
    for poly in M.COLS:
        v.poly(poly, fill=M.COL_FILL if not highlight else (0.80, 0.80, 0.82), stroke=DARK, lw=0.6)
        if not highlight:
            v.hatch(poly, 0.075, 45, (0.75, 0.75, 0.78), 0.3)
    for poly in M.COLS2:   # στηθαία εξωστών: λεπτή σκούρα λωρίδα 5 cm στην εξωτερική ακμή (γυάλινο στηθαίο)
        if highlight:
            continue
        x0, y0, x1, y1 = M.bbox(poly)
        if (x1 - x0) >= (y1 - y0):
            yo = y0 if (y0 + y1) / 2 < 5.2 else y1
            ya, yb = (yo, yo + 0.05) if yo == y0 else (yo - 0.05, yo)
            v.rect(x0, ya, x1, yb, fill=(0.25, 0.25, 0.28))
        else:
            xo = x0 if (x0 + x1) / 2 < 6.5 else x1
            xa, xb = (xo, xo + 0.05) if xo == x0 else (xo - 0.05, xo)
            v.rect(xa, y0, xb, y1, fill=(0.25, 0.25, 0.28))
    # τοίχοι
    for w in M.WALLS:
        t = M.TYPES[w["type"]]
        if highlight and w["type"] != highlight:
            v.poly(w["pts"], fill=(0.88, 0.88, 0.90), stroke=(0.70, 0.70, 0.72), lw=0.25)
            continue
        v.poly(w["pts"], fill=t["fill"], stroke=DARK, lw=0.6 if not highlight else 0.4)
        if not highlight and w["type"] in ("T1", "T4", "T4A", "T5"):
            v.brick(w["pts"], course=0.062 if w["type"] not in ("T4", "T4A") else 0.05,
                    brick_len=0.13 if w["type"] not in ("T4", "T4A") else 0.10)
    # κουφώματα αλουμινίου (R13/R24/R03, Γιάννης 07/11: «να δείχνεις με καλύτερο τρόπο τα αλουμίνια, τώρα είναι σαν τζάμια»)
    kinds = getattr(M, "WIN_KINDS", {})
    for i, poly in enumerate(M.WINS, 1):
        if highlight:
            v.poly(poly, fill=M.WIN_FILL, stroke=(0.55, 0.60, 0.70), lw=0.3)
            continue
        draw_window(v, poly, kinds.get(i))
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
            if L < 0.55 and M.is_rect(w["pts"]):
                # μικρός τοίχος: η ετικέτα δίπλα του (δυτικά / βόρεια), χωρίς κουτί, για να μην τον κρύβει
                x0, y0, x1, y1 = M.bbox(w["pts"])
                if rot == 90:
                    v.text(x0 - 0.10, cy, w["id"], size=3.8, rot=90, font="Inter-Medium")
                else:
                    v.text(cx, y0 - 0.10, w["id"], size=3.8, font="Inter-Medium")
            else:
                v.label(cx, cy, w["id"], rot=rot)
    # κείμενα χώρων / κουφωμάτων
    if with_text:
        for name, area, (x, y) in M.ROOMS:
            v.text(x, y, name, size=6.8 if area else 6.4, font="Inter-SemiBold", color=(0.35, 0.35, 0.38))
            if area:
                v.text(x, y + 0.22, area, size=5.6, color=(0.45, 0.45, 0.50))
        for lab, dim, (x, y) in M.WINDOWS:
            v.text(x, y, "%s  %s" % (lab, dim), size=5.2 if lab != "W2.07" else 4.4, font="Inter-Medium",
                   color=(0.30, 0.45, 0.75), anchor="l", bg=(lab == "W2.07"))
        for ex, ey, es, er in getattr(M, "EXTRA_TEXTS", [(-1.47, 1.40, "αρχιτεκτονικό στοιχείο – σταθερό σύστημα σκίασης", 90),
                                                        (-1.52, 7.35, "ζαρντινιέρα", 90), (7.55, 11.90, "ζαρντινιέρα", 0)]):
            v.text(ex, ey, es, size=5.6, font="Inter-Medium", color=(0.40, 0.55, 0.40) if "ζαρντ" in es else GREY, rot=er, bg=True)
    # διαστάσεις
    if with_dims:
        for orient, pos, pts in M.DIMS_IN:
            v.dim_chain(orient, pos, pts, size=5.0, color=DIMC, side=(+1 if (orient, pos) in getattr(M, "DIM_SIDE_PLUS", {("V", 11.48)}) else -1))
        for orient, pos, pts in M.DIMS_OUT:
            v.dim_chain(orient, pos, pts, size=5.4 if len(pts) > 2 else 6.2, color=DIMC, side=-1, ext=0.0)
        for x, y, s, horiz in M.THICK_NOTES:
            v.text(x, y, s, size=4.4, color=DIMC, rot=0 if horiz else 90)


def sheet_t01(c, sheet_no="Τ-01"):
    v = View(c, OX, OY, PT_PER_M_60)
    draw_plan(v)
    if getattr(M, "SITE", None):      # λευκό κάτω από το υπόμνημα τίτλου (το υπόβαθρο φτάνει ως εκεί)
        c.setFillColorRGB(1, 1, 1); c.rect(20, 20, PAGE_W - 40, 72, stroke=0, fill=1)
    north_arrow(c, 1150, 795)
    SH = getattr(M, "SHEET", B1_SHEET)
    frame_and_title(c, sheet_no, "ΚΑΤΟΨΗ ΤΟΙΧΟΠΟΙΙΩΝ – " + SH["floor_short"].upper() if SH["floor_short"] != "Β΄ ΟΡΟΦΟΥ" else "ΚΑΤΟΨΗ ΤΟΙΧΟΠΟΙΙΩΝ – Β΄ ΟΡΟΦΟΣ",
                    "Είδη τοιχοποιιών · διαστάσεις χάραξης · κουφώματα · εξώστες", SH["floor"],
                    SH["base"], "Κλίμακα 1:60 · A3", M.REV, M.DATE)
    # υπόμνημα αλλαγών R15 (πάνω δεξιά) – R11/R22: ΔΕΝ τυπώνεται όταν το μοντέλο έχει SHOW_LEGEND = False (Γιάννης 07/11: «τις σημειώσεις δεν τις θέλω στα σχέδια»)
    if not getattr(M, "SHOW_LEGEND", True):
        return
    # δεξιά στήλη, μετά τις εξωτερικές αλυσίδες (x 14,9 m ≈ 1013 pt), κάτω από τον βορρά
    x, y, wcol = 1022, 765, 150
    c.setFont("Inter", 5.2)
    def _wrap(txt):
        out, cur = [], ""
        for wd in txt.split(" "):
            t = (cur + " " + wd).strip()
            if c.stringWidth(t, "Inter", 5.2) > wcol and cur:
                out.append(cur); cur = wd
            else:
                cur = t
        return out + [cur]
    lines = []
    for s in getattr(M, "LEGEND", None) or [
        "· Ντουλάπες χωνευτές: δωματίων 0,60 · πλυντηρίου 0,70",
        "· Τ1-05 ως 1,38 (+0,03 περιθώριο) · Τ3-06 μένει (ισοπαχείς λαμπάδες) · W2.06 → 1,38–2,38",
        "· Υπν.1: χωρίς κουτί – ξυλουργικό συνέχεια ντουλάπας ως τον β. τοίχο",
        "· Τ2-05 → Τ2N-02 (1 φύλλο προς ντουλάπα) · διάδρομος χωλ 1,00",
        "· Λουτρά: πάγκος 0,50 · λεκάνη · γυάλινο διαχωριστικό 0,70 · ντους 0,70–1,00",
        "· Αλουμίνια στη μέση του τοίχου: Τ3 και στις δύο παραστάδες",
        "· Πόρτες: ανοίγουν μέσα στον χώρο (Υπν.1, λουτρά, Υπν.2)",
        "· W2.07 μέσα στο τοιχείο Κ2: κενό 0,60×0,90 στον ξυλότυπο (ποδιά +1,50)",
        "· Θερμοπρόσοψη: 10 cm διαμερίσματα · 5 cm κλιμακοστάσιο / πυρήνας",
        "· Τ6 15 cm · μέτωπο ανελκυστήρα Τ10 25 cm (= τοιχεία), πόρτα 0,90 · εξώστης Υπν.2 ως 2,70",
        "· Πόρτες σε γυψοσανίδα: ορθοστάτες UA 2 mm (Knauf) · είσοδος UA 100",
        "· Τ7-02: ισοπαχείς παραστάδες – λουτρό γονέων σε 25 (Τ7-03), πόρτα Υπν.1 3,30–4,10 σε 10 cm",
        "· Πόρτα εισόδου 1,00 (5,30–6,30, μεντεσές βόρεια) · R18/R19: λουτρό +10 cm (Τ7-01 4,80–5,05) · ντους λουτρού 0,80, γονέων 1,00 · Τ9-02 καταργήθηκε, Τ3-05 λεπτή (ξυλουργικό 0,40) · Τ6-02 από 9,55",
        "· Αλυσίδες διαστάσεων μέσα στους χώρους"]:
        ws = _wrap(s); lines += [ws[0]] + ["   " + l for l in ws[1:]]
    if getattr(M, "SITE", None):
        c.setFillColorRGB(1, 1, 1); c.rect(x - 6, y - 9 - len(lines) * 6.6 - 2, wcol + 14, len(lines) * 6.6 + 22, stroke=0, fill=1)
    c.setFont("Inter-SemiBold", 6.2); c.setFillColorRGB(*DARK)
    c.drawString(x, y, getattr(M, "LEGEND_TITLE", "ΑΛΛΑΓΕΣ R15 – R20 (05/11/2026)"))
    c.setFont("Inter", 5.2)
    for i, s in enumerate(lines):
        c.drawString(x, y - 9 - i * 6.6, s)
