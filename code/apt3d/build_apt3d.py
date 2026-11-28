"""3D ΠΕΡΙΗΓΗΣΗ ΤΟΥ ΔΙΑΜΕΡΙΣΜΑΤΟΣ Β1 (τυπικός όροφος) – χωρίς καλωδιώσεις: τοιχοποιίες, κουφώματα αλουμινίου, ψευδοροφές με τα spots,
διακόπτες, έπιπλα, λουτρά, εξώστες. Γιάννης 28/11/2026: «θέλω να μου κάνει το διαμέρισμα σε 3D να μπορώ να κινούμαι μέσα – όχι να φαίνονται
καλωδιώσεις, μόνο τοιχοποιίες, αλουμίνια, οροφές και διακόπτες και έπιπλα, σε όσο καλύτερη ανάλυση μπορείς».

Όλη η γεωμετρία βγαίνει από τα ΙΔΙΑ μοντέλα με τα τεύχη: τοιχοποιίες `toixopoiies/b1_model.py` (τοίχοι, κολόνες, κουφώματα, πόρτες, έπιπλα,
ντουλάπες, λουτρά, εξώστες), ανόψεις `anopseis/b1_anopsi.py` (ζώνες ψευδοροφής με στάθμες, spots, LED, ανιχνευτές), ηλεκτρολογικά
`ilektrologika/b1_el.py` (διακόπτες, ρευματοδότες, έπιπλα κουζίνας με ύψη, εξωτερικά φωτιστικά, πίνακας).

    python3 build_apt3d.py [out.html]   → ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ/3D/ΔΙΑΜΕΡΙΣΜΑ_Β1_3D_<REV>.html

Η σελίδα (apt3d_template.html, three.js) φορτώνει το JSON που γράφεται εδώ: «πρίσματα» (πολύγωνο + z0 + z1 + υλικό), δίσκοι φωτιστικών,
πλακέτες διακοπτών, κάναβος «πού πατιέται» για το περπάτημα (5 cm) και σημεία στάσης ανά χώρο.
Σύστημα: x ανατολή, y νότος, z ύψος από το τελικό δάπεδο του ορόφου (όπως όλα τα μοντέλα)."""
import base64, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("toixopoiies", "anopseis", "ilektrologika", "apoxeteuseis"):
    sys.path.insert(0, os.path.join(HERE, "..", d))
import b1_model as W            # noqa: E402
import b1_anopsi as A           # noqa: E402
import b1_el as M               # noqa: E402
import el_geom as G             # noqa: E402
from shapely.geometry import Polygon, box as sbox, Point, LineString   # noqa: E402
from shapely.ops import unary_union                                 # noqa: E402

REV = "R00"
DATE = "28/11/2026"
TOP = A.TOP_SLAB                    # 2,98 – κάτω παρειά πλάκας από το τελικό δάπεδο
BALC_CEIL = 2.78                    # ταβάνι εξωστών (πλάκα h20)
DOOR_H = 2.20
WIN_FULL = (0.0, 2.43)
# κουφώματα: δείκτης στη W.WINS → (όνομα, ποδιά, πρέκι) – ποδιές / πρέκια από τον πίνακα A-50-02, όπως το el_3d
WIN_INFO = {0: ("W2.08", 0.0, 2.43), 1: ("W2.09", 1.13, 2.43), 2: ("W2.06", 0.0, 2.43), 3: ("W2.05", 0.18, 1.53), 4: ("W2.04", 1.03, 1.53),
            5: ("W2.02", 0.0, 2.43), 6: ("W2.01", 0.0, 2.43), 7: ("W2.07", 1.53, 2.43), 8: ("W2.03", 1.03, 1.53)}
SLIDING = {"W2.01", "W2.02"}
NAV_C, NAV_R = 0.05, 0.22
NAV_BOX = (-2.0, -0.4, 14.2, 11.5)
# στάσεις περιήγησης: (όνομα, x, y, προς τα πού κοιτάς – μοίρες, 0 = ανατολή, 90 = νότος)
STOPS = [("Είσοδος", 8.85, 5.80, 180), ("Σαλόνι", 6.6, 6.2, 215), ("Τραπεζαρία", 5.2, 8.3, 20), ("Κουζίνα", 9.8, 8.88, 0), ("Χωλ", 5.9, 3.85, 180),
         ("Υπν. 1", 3.2, 2.9, 250), ("Υπν. 2", 7.9, 4.2, 280), ("Λουτρό", 6.1, 2.25, 195), ("Λουτρό γονέων", 2.35, 4.15, 235),
         ("Εξώστης νότιος", 5.5, 10.4, 180), ("Εξώστης δυτικός", 0.2, 7.3, 90), ("Εξώστης Υπν. 1", 0.35, 2.0, 270), ("Εξώστης Υπν. 2", 10.5, 1.7, 180)]
ROOM_LIGHTS = [(4.5, 7.1, 2.68), (7.3, 7.3, 2.68), (11.7, 8.5, 2.48), (4.8, 3.9, 2.48), (2.8, 1.7, 2.70), (7.9, 3.0, 2.70), (5.7, 2.0, 2.48), (1.7, 4.2, 2.43)]

PR = []     # πρίσματα


def prism(mat, pts, z0, z1, **kw):
    d = dict(m=mat, p=[[round(float(x), 4), round(float(y), 4)] for x, y in pts], z0=round(z0, 4), z1=round(z1, 4))
    d.update(kw)
    PR.append(d)


def rbox(mat, r, z0, z1, **kw):
    x0, y0, x1, y1 = r
    prism(mat, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, **kw)


def bbox(pts):
    return G.bbox(pts)


# ---------------------------------------------------------------- οροφές (από τις ανόψεις) → στάθμη σε κάθε σημείο
def ceil_at(x, y, default=2.70):
    for z in A.ZONES:
        for r in z["rects"]:
            if r[0] <= x <= r[2] and r[1] <= y <= r[3]:
                return z["level"]
    return default


def build():
    # ---- τοίχοι, κολόνες, θερμοπρόσοψη, στηθαία
    for w in W.WALLS:
        prism("wall", w["pts"], 0.0, TOP, id=w["id"])
    for c in W.COLS:
        prism("conc", c, 0.0, TOP)
    for c in W.COLS2:
        prism("conc", c, 0.0, 1.05)
    for e in list(W.ETICS) + list(getattr(W, "ETICS5", [])):
        prism("etics", e, 0.0, TOP)
    # ---- κουφώματα αλουμινίου
    wins_full = []
    for i, w in enumerate(W.WINS):
        name, sill, head = WIN_INFO[i]
        x0, y0, x1, y1 = bbox(w)
        horiz = (x1 - x0) >= (y1 - y0)
        L = (x1 - x0) if horiz else (y1 - y0)
        t = (y1 - y0) if horiz else (x1 - x0)
        if sill > 0:
            rbox("wall", (x0, y0, x1, y1), 0.0, sill)                           # ποδιά – τοίχος κάτω από το παράθυρο
        if head < TOP:
            rbox("wall", (x0, y0, x1, y1), head, TOP)                           # πρέκι
        if sill == 0:
            wins_full.append((x0, y0, x1, y1))
        # πλαίσιο: κάσα 6 cm γύρω-γύρω, βάθος 8 cm στον άξονα του τοίχου
        c = ((y0 + y1) / 2) if horiz else ((x0 + x1) / 2)
        f0, f1 = c - 0.04, c + 0.04
        F = 0.06
        def member(a0, a1, z0, z1, dd=0.0):
            if horiz:
                rbox("alu", (a0, f0 + dd, a1, f1 + dd), z0, z1)
            else:
                rbox("alu", (f0 + dd, a0, f1 + dd, a1), z0, z1)
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        member(a0, a0 + F, sill, head); member(a1 - F, a1, sill, head)
        member(a0, a1, sill, sill + F); member(a0, a1, head - F, head)
        n = 2 if L >= 1.2 else 1
        leaf = (L - 2 * F) / n
        for k in range(n):
            la0 = a0 + F + k * leaf; la1 = la0 + leaf
            dd = 0.0
            if name in SLIDING:
                dd = -0.03 if k == 0 else 0.03                                  # επάλληλα φύλλα
            member(la0, la0 + 0.05, sill + F, head - F, dd); member(la1 - 0.05, la1, sill + F, head - F, dd)
            member(la0, la1, sill + F, sill + F + 0.05, dd); member(la0, la1, head - F - 0.05, head - F, dd)
            g0, g1 = la0 + 0.05, la1 - 0.05
            if horiz:
                rbox("glass", (g0, c + dd - 0.004, g1, c + dd + 0.004), sill + F + 0.05, head - F - 0.05)
            else:
                rbox("glass", (c + dd - 0.004, g0, c + dd + 0.004, g1), sill + F + 0.05, head - F - 0.05)
            if n == 2 and k == 0 and name not in SLIDING:
                member(la1 - 0.025, la1 + 0.025, sill, head)                    # μεσαίο κολωνάκι
    # ---- πόρτες: πρέκι, κάσα, φύλλο (ανοιχτό όπως στην κάτοψη – η είσοδος κλειστή)
    doors = []
    for di, d in enumerate(W.DOORS):
        (hx, hy), (lx, ly), (jx, jy) = d
        horiz = abs(hy - jy) < 1e-6
        near = [bbox(w["pts"]) for w in W.WALLS if bbox(w["pts"])[0] - 0.03 <= hx <= bbox(w["pts"])[2] + 0.03 and bbox(w["pts"])[1] - 0.03 <= hy <= bbox(w["pts"])[3] + 0.03]
        if horiz:
            t0 = min(b[1] for b in near); t1 = max(b[3] for b in near)
            r = (min(hx, jx), t0, max(hx, jx), t1)
        else:
            t0 = min(b[0] for b in near); t1 = max(b[2] for b in near)
            r = (t0, min(hy, jy), t1, max(hy, jy))
        doors.append(r)
        rbox("wall", r, DOOR_H + 0.05, TOP)
        # κάσα
        if horiz:
            rbox("frame", (r[0], t0, r[0] + 0.05, t1), 0, DOOR_H + 0.05); rbox("frame", (r[2] - 0.05, t0, r[2], t1), 0, DOOR_H + 0.05)
            rbox("frame", r, DOOR_H, DOOR_H + 0.05)
        else:
            rbox("frame", (t0, r[1], t1, r[1] + 0.05), 0, DOOR_H + 0.05); rbox("frame", (t0, r[3] - 0.05, t1, r[3]), 0, DOOR_H + 0.05)
            rbox("frame", r, DOOR_H, DOOR_H + 0.05)
        entrance = di == len(W.DOORS) - 1
        if entrance:                                                               # πόρτα ασφαλείας κλειστή, μέσα στο άνοιγμα
            c_ = (t0 + t1) / 2
            if horiz:
                rbox("door", (r[0] + 0.05, c_ - 0.03, r[2] - 0.05, c_ + 0.03), 0.01, DOOR_H)
            else:
                rbox("door", (c_ - 0.03, r[1] + 0.05, c_ + 0.03, r[3] - 0.05), 0.01, DOOR_H)
        else:                                                                      # φύλλο ανοιχτό 90° από τον μεντεσέ ως το άκρο του
            dx, dy = lx - hx, ly - hy
            Ln = math.hypot(dx, dy); ux, uy = dx / Ln, dy / Ln; nx, ny = -uy * 0.02, ux * 0.02
            pts = [(hx + nx, hy + ny), (lx + nx, ly + ny), (lx - nx, ly - ny), (hx - nx, hy - ny)]
            prism("door", pts, 0.01, DOOR_H)
    # ---- ψευδοροφές (ζώνες των ανόψεων): το καθετί από τη στάθμη του ως την πλάκα – το σκαλοπάτι βγαίνει μόνο του
    for z in A.ZONES:
        for r in z["rects"]:
            rbox("ceil", r, z["level"], TOP, zone=z["id"])
    for r in doors:
        rbox("ceil", r, DOOR_H + 0.05, TOP)
    for f in W.FLOORS:
        prism("ceil", f, BALC_CEIL, TOP)
    # ---- δάπεδα
    rbox("wood", (0.05, 0.1, 13.95, 10.25), -0.02, 0.0)
    for b in W.BATHS:
        pass
    for rr in ((5.05, 0.8, 6.4, 3.25), (0.11, 3.16, 1.05, 5.05), (1.05, 3.5, 3.15, 5.05)):
        rbox("tile", rr, -0.015, 0.003)
    for rr in ((9.55, 3.0, 11.05, 5.15), (9.55, 5.1, 13.1, 7.7), (11.05, 3.25, 13.1, 4.85)):
        rbox("stone", rr, -0.015, 0.003)
    for f in W.FLOORS:
        prism("tile_out", f, -0.04, -0.02)
    rbox("ground", (-40, -40, 60, 60), -3.15, -3.10)
    # ---- γυάλινα στηθαία στις ελεύθερες ακμές των εξωστών
    solid = [sbox(*bbox(w["pts"])) for w in W.WALLS] + [sbox(*bbox(c)) for c in W.COLS + W.COLS2] + [Polygon(e) for e in W.ETICS]
    solid = unary_union(solid).buffer(0.12)
    for f in W.FLOORS:
        pts = list(f)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.05:
                continue
            seg = LineString([a, b])
            if solid.contains(seg.interpolate(0.5, normalized=True)):
                continue
            if seg.intersection(solid).length > 0.4 * seg.length:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * 0.008, dx / L * 0.008
            prism("glass", [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], 0.02, 1.10)
            nx, ny = -dy / L * 0.02, dx / L * 0.02
            prism("alu", [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], 1.10, 1.14)
    # ---- έπιπλα
    furn = []                                                                      # αποτυπώματα για το περπάτημα

    def fbox(mat, r, z0, z1, block=True):
        rbox(mat, r, z0, z1)
        if block:
            furn.append(r)
    for q in W.EQUIP:
        k, x0, y0, x1, y1 = q[0], q[1], q[2], q[3], q[4]
        lab = q[5] if len(q) > 5 else ""
        side = q[6] if len(q) > 6 else (lab if lab in ("N", "S", "E", "W") else "")
        if side == lab:
            lab = ""
        r = (x0, y0, x1, y1)
        kitchen = y0 >= 7.6 and x0 >= 9.6
        if k == "sofa":
            fbox("fabric", r, 0.0, 0.45)
            b = 0.22
            back = {"N": (x0, y0, x1, y0 + b), "S": (x0, y1 - b, x1, y1), "E": (x1 - b, y0, x1, y1), "W": (x0, y0, x0 + b, y1)}[side]
            rbox("fabric", back, 0.45, 0.85)
        elif k == "bed":
            fbox("wood", r, 0.0, 0.30); rbox("linen", (x0 + 0.03, y0 + 0.03, x1 - 0.03, y1 - 0.03), 0.30, 0.52)
            hb = {"N": (x0, y0, x1, y0 + 0.06), "W": (x0, y0, x0 + 0.06, y1), "S": (x0, y1 - 0.06, x1, y1), "E": (x1 - 0.06, y0, x1, y1)}[side]
            rbox("wood", hb, 0.0, 1.05)
            pw = {"N": (x0 + 0.15, y0 + 0.08, x1 - 0.15, y0 + 0.5), "W": (x0 + 0.08, y0 + 0.15, x0 + 0.5, y1 - 0.15)}.get(side)
            if pw:
                rbox("linen", pw, 0.52, 0.62)
        elif k == "chair":
            fbox("wood", (x0 + 0.03, y0 + 0.03, x1 - 0.03, y1 - 0.03), 0.42, 0.46)
            for lx_, ly_ in ((x0 + 0.03, y0 + 0.03), (x1 - 0.06, y0 + 0.03), (x0 + 0.03, y1 - 0.06), (x1 - 0.06, y1 - 0.06)):
                rbox("dark", (lx_, ly_, lx_ + 0.03, ly_ + 0.03), 0.0, 0.42)
            back = {"N": (x0 + 0.03, y0 + 0.03, x1 - 0.03, y0 + 0.06), "S": (x0 + 0.03, y1 - 0.06, x1 - 0.03, y1 - 0.03)}.get(side)
            if back:
                rbox("wood", back, 0.46, 0.90)
        elif k == "tv":
            fbox("walnut", r, 0.0, 0.45)
            cx = (x0 + x1) / 2
            rbox("dark", (cx - 0.65, y1 - 0.03, cx + 0.65, y1 - 0.005), 0.85, 1.60)
        elif k == "tall":
            fbox("cab", r, 0.0, ceil_at((x0 + x1) / 2, (y0 + y1) / 2) - 0.03)
        elif k == "hob":
            rbox("dark", (x0 + 0.02, y0 + 0.08, x1 - 0.02, y1 - 0.08), 0.90, 0.905)
        elif k == "sink":
            rbox("steel", (x0 + 0.06, y0 + 0.1, x1 - 0.06, y1 - 0.1), 0.885, 0.905)
        elif k == "appl":
            rbox("steel", (x0 + 0.01, y0 - 0.005, x1 - 0.01, y0 + 0.005), 0.1, 0.85)
        elif k == "rect":
            if kitchen:                                                            # πάγκοι κουζίνας (τοιχοποιίες R31+: μόνο πάγκος, χωρίς ψηλή στήλη)
                fbox("cab", r, 0.0, 0.90)
                rbox("counter", (x0 - 0.01, y0 - 0.01, x1 + 0.01, y1 + 0.01), 0.90, 0.93)
                continue
            if "ΤΡΑΠΕΖ" in lab or "ΓΡΑΦΕΙΟ" in lab:
                fbox("walnut", r, 0.72, 0.75)
                for lx_, ly_ in ((x0 + 0.05, y0 + 0.05), (x1 - 0.1, y0 + 0.05), (x0 + 0.05, y1 - 0.1), (x1 - 0.1, y1 - 0.1)):
                    rbox("walnut", (lx_, ly_, lx_ + 0.05, ly_ + 0.05), 0.0, 0.72)
            elif (x1 - x0) < 0.5 and (y1 - y0) < 0.5:
                fbox("walnut", r, 0.0, 0.50)                                      # κομοδίνο
            else:
                fbox("walnut", r, 0.0, 0.40)                                      # τραπεζάκι
    kit_tall = [q[1:5] for q in W.EQUIP if q[0] == "tall"]
    for t in A.TALL:
        nm, r = t[0], t[1]
        if any(abs(r[0] - k[0]) < 0.01 and abs(r[1] - k[1]) < 0.01 for k in kit_tall):
            continue                                                               # το ψυγείο μπήκε από το EQUIP
        top = ceil_at((r[0] + r[2]) / 2, (r[1] + r[3]) / 2) - 0.03
        if "επάνω" in nm:                                                          # επάνω ντουλάπια κουζίνας: από το +1,45 ως την οροφή (από κάτω το LED)
            rbox("cab", r, 1.45, top)
        else:
            fbox("cab", r, 0.0, top)
    for wd in W.WARDROBES:
        if wd.get("joinery"):
            fbox("cab", wd["r"], 0.0, 0.75)
    # ---- λουτρά
    for b in W.BATHS:
        c = b["counter"]; fbox("counter", c, 0.0, 0.75)
        cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        rbox("white", (cx - 0.22, cy - 0.17, cx + 0.22, cy + 0.17), 0.75, 0.88)
        (tx, ty), td = b["toilet"]
        n = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}[td]
        if n[0]:
            tr = (min(tx, tx + n[0] * 0.55), ty - 0.19, max(tx, tx + n[0] * 0.55), ty + 0.19)
        else:
            tr = (tx - 0.19, min(ty, ty + n[1] * 0.55), tx + 0.19, max(ty, ty + n[1] * 0.55))
        fbox("white", tr, 0.0, 0.42)
        s = b["shower"]; rbox("tile", s, 0.003, 0.02)
        (a, bb_) = b["screen"]
        dx, dy = bb_[0] - a[0], bb_[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * 0.006, dx / L * 0.006
        prism("glass", [(a[0] + nx, a[1] + ny), (bb_[0] + nx, bb_[1] + ny), (bb_[0] - nx, bb_[1] - ny), (a[0] - nx, a[1] - ny)], 0.02, 2.0)
        # καθρέπτης πάνω από τον πάγκο, στον τοίχο πίσω του
        if (c[2] - c[0]) < (c[3] - c[1]):                                            # πάγκος κατά μήκος κατακόρυφου τοίχου (λουτρό: τοίχος x 5,05)
            rbox("mirror", (c[0] + 0.004, c[1] + 0.05, c[0] + 0.012, c[3] - 0.05), 1.20, 2.20)
        else:
            rbox("mirror", (c[0] + 0.05, c[3] - 0.012, c[2] - 0.05, c[3] - 0.004), 1.20, 2.20)
    # ---- πίνακας ΓΠ (πορτάκι)
    p = M.PANEL
    rbox("plate", (p["x"] + 0.002, p["y0"], p["x"] + 0.012, p["y1"]), p["z0"], p["z1"])
    # ---- διακόπτες / ρευματοδότες (πλακέτες 8 × 8)
    NRM = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    plates = []
    for s in M.SWITCHES:
        opt = s[7] if len(s) > 7 else {}
        plates.append(dict(k="sw", x=s[1], y=s[2], d=s[3], z=opt.get("h", M.H_SW), n=len(s[4]), id=s[0]))
    for s in M.SOCKETS:
        if not M.drawn(s[0]):
            continue
        plates.append(dict(k="so", x=s[1], y=s[2], d=s[3], z=s[6], n=s[4], id=s[0]))
    # ---- φωτιστικά
    lights = []
    for q in A.SPOTS:
        n, k, x, y = q[0], q[1], q[2], q[3]
        if k == "ΚΧ" or q[4] == "ΚΧ":
            continue
        lights.append(dict(k=k, x=x, y=y, z=ceil_at(x, y), id=n))
    for q in A.SPOTS:
        if q[4] == "ΚΧ":
            lights.append(dict(k="s", x=q[2], y=q[3], z=2.73, id=q[0]))
    for e in M.EXT_SPOTS:
        lights.append(dict(k="ext", x=e[1], y=e[2], z=BALC_CEIL, id=e[0]))
    for l in M.WALL_LIGHTS:
        if l[4] == "ext":
            lights.append(dict(k="wall", x=l[1], y=l[2], z=l[5], d=l[3], id=l[0]))
    for n, a, b, g, t in A.LED:
        lights.append(dict(k="led", a=list(a), b=list(b), z=1.44 if n == "LED4" else 1.40, id=n))
    dets = [dict(x=d[2], y=d[3], z=ceil_at(d[2], d[3])) for d in A.DETECTORS if d[0] != "ΑΚ6"]
    # ---- πού πατιέται (κάναβος 5 cm)
    import el_3d as E3
    rooms = [sbox(*r) for _, _, _, rr in E3.ROOMS3 for r in rr]
    walk = unary_union(rooms + [sbox(*r) for r in doors] + [Polygon(f) for f in W.FLOORS] + [sbox(*r) for r in wins_full])
    blocks = unary_union([sbox(*r) for r in furn] + [sbox(*bbox(w["pts"])) for w in W.WALLS] + [sbox(*bbox(c)) for c in W.COLS + W.COLS2])
    walk = walk.difference(blocks.buffer(0.02)).buffer(-NAV_R)
    X0, Y0, X1, Y1 = NAV_BOX
    nx, ny = int(round((X1 - X0) / NAV_C)), int(round((Y1 - Y0) / NAV_C))
    bits = bytearray((nx * ny + 7) // 8)
    from shapely.prepared import prep
    pw = prep(walk)
    for j in range(ny):
        yy = Y0 + (j + 0.5) * NAV_C
        for i in range(nx):
            if pw.contains(Point(X0 + (i + 0.5) * NAV_C, yy)):
                k = j * nx + i; bits[k >> 3] |= 1 << (k & 7)
    stops = []
    for nm, sx, sy, yaw in STOPS:                         # αν η στάση πέφτει σε έπιπλο, το κοντινότερο σημείο που πατιέται
        if not walk.contains(Point(sx, sy)):
            best = None
            for j in range(ny):
                for i in range(nx):
                    k = j * nx + i
                    if bits[k >> 3] >> (k & 7) & 1:
                        px, py = X0 + (i + 0.5) * NAV_C, Y0 + (j + 0.5) * NAV_C
                        d = (px - sx) ** 2 + (py - sy) ** 2
                        if best is None or d < best[0]:
                            best = (d, px, py)
            assert best and best[0] < 1.0, "στάση «%s» δεν πατιέται" % nm
            sx, sy = round(best[1], 3), round(best[2], 3)
        stops.append((nm, sx, sy, yaw))
    nav = dict(x0=X0, y0=Y0, c=NAV_C, nx=nx, ny=ny, bits=base64.b64encode(bytes(bits)).decode())
    data = dict(rev=REV, date=DATE, top=TOP, prisms=PR, plates=plates, lights=lights, dets=dets, nav=nav, stops=stops, roomlights=ROOM_LIGHTS,
                base="τοιχοποιίες Β1 %s · ανόψεις Β1 %s · ηλεκτρολογικά %s" % (W.REV, A.REV, M.REV))
    return data


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "3D", "ΔΙΑΜΕΡΙΣΜΑ_Β1_3D_%s.html" % REV)
    data = build()
    tpl = open(os.path.join(HERE, "apt3d_template.html"), encoding="utf-8").read()
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":"))).replace("__REV__", REV).replace("__DATE__", DATE)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print("→ %s · %d πρίσματα · %d φωτιστικά · %d πλακέτες · %.0f KB" % (os.path.normpath(out), len(PR), len(data["lights"]), len(data["plates"]), len(html) / 1024))


if __name__ == "__main__":
    main()
