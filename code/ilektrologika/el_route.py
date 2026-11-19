"""ΠΡΑΓΜΑΤΙΚΕΣ ΔΙΑΔΡΟΜΕΣ ΚΑΛΩΔΙΩΝ ΣΕ 3D (R14) – και έλεγχος ότι κάθε εκατοστό τους περνά από εκεί που ΓΙΝΕΤΑΙ.

Κάθε διαδρομή είναι τεθλασμένη [(x, y, z, μέσο)] – το «μέσο» ισχύει για το τμήμα που ΞΕΚΙΝΑ από το σημείο (ή πλειάδα μέσων = οποιοδήποτε από αυτά):
    void    κενό ψευδοροφής: πάνω από το φύλλο της οροφής, κάτω από την πλάκα. Κάτω από δοκάρι ΜΟΝΟ αν η οροφή είναι ≥ 6 cm κάτω από την κάτω παρειά του
    wall    κοιλότητα τοίχου γυψοσανίδας / επένδυσης, από το δάπεδο ως την κορυφή του. Αν από πάνω έχει δοκάρι, κορυφή = κάτω παρειά του δοκαριού
    header  υπέρθυρο γυψοσανίδας πάνω από πόρτα
    brick   αυλάκι / τρύπα σε τούβλο – ποτέ πάνω από την κάτω παρειά δοκαριού
    furn    μέσα / πίσω από έπιπλο έως οροφή ή ντουλάπι κουζίνας
    floor   πάνω στην πλάκα, μέσα στο γέμισμα – ποτέ μέσα από κολόνα ή τούβλο
    hole    μέσα σε χιτώνιο οπής δοκαριού (ΟΠ1 … ΟΠ5)
    shaft   μέσα στο shaft Η/Μ
    ext     έξω από το κτίριο (εξώστης)
ΠΟΥΘΕΝΑ: μέσα σε σκυρόδεμα δοκαριού / κολόνας / πλάκας, μέσα σε κουρτινόθηκη (είναι ανοιχτή ως την πλάκα), κάτω από δοκάρι με οροφή περασιά.

    python3 el_route.py            → τυπώνει τον έλεγχο όλων των διαδρομών"""
import math, re
import el_geom as G

M = W = A = None
R = 0.012             # μισό πάχος καλωδίου / σπιράλ που ελέγχεται (m)
BOARD = 0.0125        # φύλλο γυψοσανίδας οροφής
MIN_UNDER = 0.06      # ελάχιστο καθαρό ανάμεσα στο φύλλο της οροφής και την κάτω παρειά δοκαριού για να περάσει καλώδιο από κάτω του
STUD = ("T2", "T2N", "T2A", "T7", "T7A", "T6", "T6A", "T6B", "T8", "T3")
BRICK = ("T1", "T4", "T4A", "T5", "T10")
SLAB_TOP = 2.98
SLAB_DEF = 2.78       # κάτω παρειά πλάκας όπου δεν ορίζεται ζώνη (h20 – το δυσμενέστερο)
DOOR_H = 2.25         # πάνω από την κάσα (πόρτες 2,20)
SHAFT_SPACE = (9.70, 2.85, 11.05, 3.15)
ZONE_FIX = [((1.135, 3.16, 3.15, 3.25), "Ζ7")]      # το ορθογώνιο της Ζ6 (λουτρό γονέων) μπαίνει 9 cm μέσα στο Υπν.1 – εκεί ισχύει η Ζ7
_C = {}


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A
    _C.clear()
    walls = []
    for w in W.WALLS:
        poly = None
        if not G.is_rect(w["pts"]):
            from shapely.geometry import Polygon
            poly = Polygon(w["pts"])
        walls.append((w["id"], w["type"], tuple(W.bbox(w["pts"])), poly))
    _C["walls"] = walls
    _C["cols"] = [tuple(W.bbox(p)) for p in W.COLS] + [tuple(W.bbox(p)) for p in getattr(W, "COLS2", [])]
    _C["beams"] = [(b[0], (b[2], b[3], b[4], b[5]), A.beam_soffit(b[1])) for b in A.BEAMS]
    zones = []
    for z in A.ZONES:
        for r in z["rects"]:
            lab = z["slab"]
            for pr, pl in z.get("slab_parts") or []:
                if tuple(pr) == tuple(r):
                    lab = pl
            m = re.search(r"h(\d+)", lab)
            zones.append((z["id"], z["level"], round(SLAB_TOP - int(m.group(1)) / 100.0, 3) if m else SLAB_DEF, tuple(r)))
    _C["zones"] = zones
    _C["rec"] = [tuple(c["rect"]) for c in A.CURTAINS]
    doors = []
    for (hx, hy), _, (jx, jy) in W.DOORS:
        horiz = abs(hy - jy) < 1e-6
        for wid, typ, b, poly in walls:
            if poly is not None:
                continue
            if horiz and (abs(b[0] - hx) < 0.02 or abs(b[2] - hx) < 0.02 or abs(b[0] - jx) < 0.02 or abs(b[2] - jx) < 0.02) and b[1] - 0.02 <= hy <= b[3] + 0.02 and (b[2] - b[0]) >= 0.045:
                doors.append((min(hx, jx), b[1], max(hx, jx), b[3])); break
            if not horiz and (abs(b[1] - hy) < 0.02 or abs(b[3] - hy) < 0.02 or abs(b[1] - jy) < 0.02 or abs(b[3] - jy) < 0.02) and b[0] - 0.02 <= hx <= b[2] + 0.02:
                doors.append((b[0], min(hy, jy), b[2], max(hy, jy))); break
    assert len(doors) == len(W.DOORS), "el_route: δεν βρέθηκε ο τοίχος κάποιας πόρτας (%d από %d)" % (len(doors), len(W.DOORS))
    _C["doors"] = doors
    furn = [(wd["name"], tuple(wd["r"]), 0.0, None) for wd in W.WARDROBES] + [tuple(f) for f in getattr(M, "KITCHEN_FURN", [])]
    _C["furn"] = furn
    holes = []
    for h in M.HOLES:
        nm, br, zs = [b for b in _C["beams"] if b[0] == h["beam"]][0]
        holes.append((h["id"], h["x"], h["y"], (br[2] - br[0]) > (br[3] - br[1]), br))        # True → δοκάρι Α–Δ, η οπή τρέχει κατά y
    _C["holes"] = holes


# ---------------------------------------------------------------- τι υπάρχει σε κάτοψη
def col_at(x, y, tol=-0.002):
    return any(G.in_rect(x, y, c, tol=tol) for c in _C["cols"])


def over(x, y, pad=R - 0.002):
    """Το δοκάρι πάνω από το σημείο (όνομα, κάτω παρειά) – το χαμηλότερο· pad = πόσο κοντά στην παρειά του μετράει."""
    best = None
    for nm, r, zs in _C["beams"]:
        if G.in_rect(x, y, r, tol=pad) and (best is None or zs < best[1]):
            best = (nm, zs)
    return best


def walls_at(x, y, tol=0.006):
    out = []
    for wid, typ, b, poly in _C["walls"]:
        if not G.in_rect(x, y, b, tol=tol):
            continue
        if poly is not None:
            from shapely.geometry import Point
            if poly.distance(Point(x, y)) > tol:
                continue
        out.append((wid, typ))
    return out


def door_at(x, y, tol=0.006):
    return any(G.in_rect(x, y, d, tol=tol) for d in _C["doors"])


def zone_at(x, y):
    hits = [(zid, lv, sb) for zid, lv, sb, r in _C["zones"] if G.in_rect(x, y, r)]
    if len(hits) > 1:
        for fr, keep in ZONE_FIX:
            if G.in_rect(x, y, fr):
                hits = [h for h in hits if h[0] == keep] or hits
    if not hits:
        return None
    return min(hits, key=lambda h: h[1])


def zone_near(x, y, dist=(0.08, 0.16, 0.30)):
    """Για σημεία πάνω σε ίχνος τοίχου / υπέρθυρου / στην άκρη ζώνης: (χαμηλότερη στάθμη οροφής, χαμηλότερη κάτω παρειά πλάκας) των διπλανών χώρων."""
    hits = []
    for d in dist:
        for k in range(8):
            a = math.pi / 4 * k
            px, py = x + d * math.cos(a), y + d * math.sin(a)
            if col_at(px, py):
                continue
            z = zone_at(px, py)
            if z:
                hits.append(z)
        if hits:
            break
    if not hits:
        return None
    return (min(h[1] for h in hits), min(h[2] for h in hits))


def slab_bottom(x, y):
    z = zone_at(x, y)
    if z:
        return z[2]
    zn = zone_near(x, y)
    return zn[1] if zn else SLAB_DEF


def in_sleeve(x, y, z, ext=0.012, dz=None):
    """Μέσα σε χιτώνιο οπής (ext = πόσο έξω από τις παρειές του δοκαριού μετράει ακόμη ως στόμιο)."""
    dz = (M.HOLE_IN / 2 - R + 0.002) if dz is None else dz
    for hid, hx, hy, horiz, br in _C["holes"]:
        if abs(z - 2.73) > dz + 1e-9:
            continue
        if horiz and abs(x - hx) <= 0.0205 and br[1] - ext <= y <= br[3] + ext:
            return hid
        if (not horiz) and abs(y - hy) <= 0.0205 and br[0] - ext <= x <= br[2] + ext:
            return hid
    return None


# ---------------------------------------------------------------- επιτρέπεται καλώδιο στο (x, y, z) μέσα στο μέσο med;  None = ναι, αλλιώς ο λόγος
def _top(x, y):
    b = over(x, y)
    return (b[1], "το δοκάρι %s" % b[0]) if b else (slab_bottom(x, y), "την πλάκα")


def void_iv(x, y):
    """Το ύψος που έχει ελεύθερο ένα καλώδιο στο κενό οροφής πάνω από το (x, y): (από, ως, None) – ή (None, None, λόγος) αν εκεί δεν υπάρχει κενό."""
    if col_at(x, y):
        return None, None, "μέσα σε κολόνα"
    wh = walls_at(x, y, tol=0.0)
    for wid, typ in wh:
        if typ in BRICK:
            return None, None, "κενό οροφής μέσα από τούβλο (%s)" % wid.replace("T", "Τ")
    if any(G.in_rect(x, y, r, tol=-0.004) for r in _C["rec"]):
        return None, None, "μέσα σε κουρτινόθηκη (ανοιχτή ως την πλάκα – δεν είναι κενό οροφής)"
    zh = zone_at(x, y)
    if zh is None or wh or door_at(x, y, tol=0.0):
        zn = zone_near(x, y) if (wh or door_at(x, y, tol=0.0)) else zone_near(x, y, dist=(0.05, 0.10))     # έξω από τοίχο: μόνο ως 10 cm από την άκρη ζώνης
        if zn is None and zh is None:
            return None, None, "εκτός κενού ψευδοροφής"
        L = min([q for q in ((zn[0] if zn else None), (zh[1] if zh else None)) if q is not None])
        sb = min([q for q in ((zn[1] if zn else None), (zh[2] if zh else None)) if q is not None])
    else:
        L, sb = zh[1], zh[2]
    b = over(x, y)
    top = sb
    if b:
        gap = b[1] - (L + BOARD)
        if gap < MIN_UNDER - 1e-6:
            return None, None, ("το δοκάρι %s κατεβαίνει ως την οροφή – δεν υπάρχει κενό από κάτω του" % b[0]) if gap <= 0.001 else \
                ("κάτω από το δοκάρι %s το κενό είναι μόνο %.1f cm (θέλει ≥ %d) – δεν περνά" % (b[0], gap * 100, MIN_UNDER * 100))
        top = b[1]
    return L + BOARD + R, top - R, (b[0] if b else None)


def _void(x, y, z):
    if over(x, y) and in_sleeve(x, y, z, ext=0.04, dz=0.03):
        return None
    lo, hi, why = void_iv(x, y)
    if lo is None:
        return why
    if z < lo - 1e-6:
        return "κάτω από το φύλλο της οροφής (+%.2f)" % (lo - BOARD - R)
    if z > hi + 1e-6:
        return "μέσα στο μπετό – πάνω από την κάτω παρειά %s (+%.2f)" % (("του δοκαριού " + why) if why else "της πλάκας", hi + R)
    return None


def _inwall(x, y, z, types, name):
    hit = [w for w in walls_at(x, y) if w[1] in types]
    if not hit:
        return "εκτός %s" % name
    top, what = _top(x, y)
    if z > top - R + 1e-6:
        return "ο τοίχος %s τελειώνει στο +%.2f (%s) – το καλώδιο είναι πιο πάνω, μέσα στο μπετό" % (hit[0][0].replace("T", "Τ"), top, what.replace("το δοκάρι", "κάτω παρειά του δοκαριού").replace("την πλάκα", "πλάκα"))
    if z < -M.SCREED - 1e-6:
        return "κάτω από την πλάκα"
    return None


def _wall(x, y, z):
    return _inwall(x, y, z, STUD, "τοίχου γυψοσανίδας / επένδυσης")


def _brick(x, y, z):
    return _inwall(x, y, z, BRICK, "τούβλου")


def _header(x, y, z):
    if not door_at(x, y):
        return "εκτός υπέρθυρου"
    top, what = _top(x, y)
    if z < DOOR_H + R - 1e-6:
        return "μέσα στο άνοιγμα της πόρτας (κάτω από +%.2f)" % DOOR_H
    if z > top - R + 1e-6:
        return "πάνω από το υπέρθυρο – μέσα στο μπετό (%s, +%.2f)" % (what, top)
    return None


def _furn(x, y, z):
    hit = [f for f in _C["furn"] if G.in_rect(x, y, f[1], tol=0.012)]
    if not hit:
        return "εκτός επίπλου"
    top, what = _top(x, y)
    for nm, r, z0, z1 in hit:
        if z0 - 1e-6 <= z <= (z1 if z1 is not None else top - R) + 1e-6 and z <= top - R + 1e-6:
            return None
    return "έξω από το ύψος του επίπλου «%s» ή μέσα στο μπετό (%s, +%.2f)" % (hit[0][0], what, top)


def _floor(x, y, z):
    if not (-M.SCREED - 1e-6 <= z <= 1e-6):
        return "εκτός γεμίσματος δαπέδου"
    if col_at(x, y):
        return "δάπεδο μέσα από κολόνα"
    for wid, typ in walls_at(x, y, tol=0.0):
        if typ in BRICK:
            return "δάπεδο μέσα από τούβλο (%s)" % wid.replace("T", "Τ")
    return None


def _hole(x, y, z):
    return None if in_sleeve(x, y, z) else "εκτός χιτωνίου οπής"


def _shaft(x, y, z):
    if not G.in_rect(x, y, SHAFT_SPACE, tol=0.006):
        return "εκτός shaft"
    top, what = _top(x, y)
    return None if z <= top - R + 1e-6 else "μέσα στο μπετό (%s)" % what


def _ext(x, y, z):
    return "μέσα σε κολόνα" if col_at(x, y) else None


MEDIA = {"void": _void, "wall": _wall, "header": _header, "brick": _brick, "furn": _furn, "floor": _floor, "hole": _hole, "shaft": _shaft, "ext": _ext}
MED_TXT = {"void": "κενό οροφής", "wall": "μέσα σε τοίχο", "header": "υπέρθυρο", "brick": "τούβλο", "furn": "έπιπλο", "floor": "δάπεδο", "hole": "οπή", "shaft": "shaft", "ext": "έξω"}


def ok(p, med):
    """None αν το σημείο p = (x, y, z) γίνεται σε κάποιο από τα μέσα med, αλλιώς ο λόγος (του πρώτου μέσου)."""
    meds = med if isinstance(med, (tuple, list)) else (med,)
    first = None
    for m in meds:
        r = MEDIA[m](p[0], p[1], p[2])
        if r is None:
            return None
        first = first or r
    return first


def check_path(pts, step=0.01):
    """[(τμήμα, (x, y, z), μέσο, λόγος)] – το πρώτο σημείο κάθε τμήματος που ΔΕΝ γίνεται."""
    bad = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        L = math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3)))
        n = max(1, int(math.ceil(L / step)))
        for k in range(n + 1):
            t = k / float(n)
            p = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
            r = ok(p, a[3])
            if r is not None:
                bad.append((i, tuple(round(q, 3) for q in p), a[3], r)); break
    return bad


def plen(pts):
    return sum(math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3))) for a, b in zip(pts, pts[1:]))


def med_len(pts, meds):
    """Μήκος της διαδρομής μέσα στα μέσα meds (με βάση το δηλωμένο μέσο κάθε τμήματος – για πλειάδα μετρά το πρώτο)."""
    t = 0.0
    for a, b in zip(pts, pts[1:]):
        m = a[3][0] if isinstance(a[3], (tuple, list)) else a[3]
        if m in meds:
            t += math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3)))
    return t


# ---------------------------------------------------------------- σημεία και διαδρομές
def devices():
    """Όλα τα σημεία τοίχου (ό,τι θέλει καλώδιο μέσα σε τοίχο): (id, x, y, πρόσωπο, ύψος, είδος, επιλογές)."""
    import el_checks as CK
    CK.bind(M)
    out = list(CK.wall_points())
    for e in M.EMERGENCY:
        out.append((e[0], e[1], e[2], e[3], 2.35, "φωτιστικό ασφαλείας", {}))
    return out


def feed_for(pid, wid):
    for f in M.FEEDS:
        if pid in f.get("devs", ()) or pid in f.get("extra", ()):
            return f
    for f in M.FEEDS:
        if "devs" not in f and wid in f.get("walls", ()):
            return f
    return None


def dev_path(f, dev):
    pid, x, y, d, h = dev[:5]
    axis, c, zr, med = f["run"]
    a = x if axis == "x" else y
    at = f.get("at", {}).get(pid, a)
    pt = (lambda u, cc, z: (u, cc, z)) if axis == "x" else (lambda u, cc, z: (cc, u, z))
    drop = f.get("drop", "wall"); stub = f.get("stub", ("wall", "brick", "furn")); hop = f.get("hop")
    P = [tuple(q) for q in f["feed"]]
    e = P[-1]
    ec = e[1] if axis == "x" else e[0]
    assert abs(ec - c) < 0.003 and abs(e[2] - zr) < 0.003, "τροφοδοσία %s: το τέλος της δεν είναι πάνω στη γραμμή διανομής" % f["id"]
    P[-1] = e[:3] + (med,)
    P.append(pt(at, c, zr) + ((hop[1] if hop else drop),))
    cc = c
    if hop:
        cc = hop[0]
        P.append(pt(at, cc, zr) + (drop,))
    P.append(pt(at, cc, h) + ((drop if abs(at - a) > 1e-6 else stub),))
    if abs(at - a) > 1e-6:
        P.append(pt(a, cc, h) + (stub,))
    P.append((x, y, h, ""))
    out = [P[0]]
    for q in P[1:]:                                     # χωρίς μηδενικά τμήματα
        if math.sqrt(sum((q[k] - out[-1][k]) ** 2 for k in range(3))) < 1e-6:
            out[-1] = out[-1][:3] + (q[3],)
        else:
            out.append(q)
    return out


def build():
    """Όλες οι διαδρομές: κορμοί, ένα μονοπάτι ανά σημείο τοίχου (από τον κορμό ως το κουτί), πρόσθετες (φώτα σε απομονωμένα κενά, έξοδοι εξωστών)."""
    devs, missing = [], []
    for dev in devices():
        pid, x, y, d, h, kind, opt = dev
        wid = G.face_of(W, x, y, d)[1]
        f = feed_for(pid, wid)
        if f is None:
            if pid not in [e["id"] for e in M.EXTRA3]:          # π.χ. η Π59: έχει δική της πρόσθετη διαδρομή
                missing.append(pid)
            continue
        devs.append(dict(id=pid, grp=f["grp"], feed=f["id"], kind=kind, h=h, wall=wid, nfeed=len(f["feed"]), pts=dev_path(f, dev)))
    return dict(trunks=M.TRUNKS3, devs=devs, extra=M.EXTRA3, missing=missing)


def _dist_seg3(p, a, b):
    d = [b[k] - a[k] for k in range(3)]; L2 = sum(q * q for q in d)
    t = 0 if L2 == 0 else max(0.0, min(1.0, sum((p[k] - a[k]) * d[k] for k in range(3)) / L2))
    return math.sqrt(sum((p[k] - (a[k] + d[k] * t)) ** 2 for k in range(3)))


def attached(p, lines, tol=0.03):
    return any(_dist_seg3(p, a, b) <= tol for pts in lines for a, b in zip(pts, pts[1:]))


def panel_top(p):
    return abs(p[0] - M.XP) < 0.02 and M.PANEL["y0"] - 0.02 <= p[1] <= M.PANEL["y1"] + 0.02 and abs(p[2] - M.PANEL_TOP_Z) < 0.02


def check():
    """[(κωδικός, κατάσταση, κείμενο)] – κάθε κορμός, κάθε τροφοδοσία τοίχου (όλα τα σημεία της), κάθε πρόσθετη διαδρομή."""
    B = build(); res = []

    def why(bad):
        i, p, med, r = bad[0]
        return "στο (%s / %s, +%s) – %s" % (G.fmt(p[0]), G.fmt(p[1]), G.fmt(p[2]), r)
    tl = [t["pts"] for t in B["trunks"]]
    for t in B["trunks"]:
        bad = check_path(t["pts"])
        p0 = t["pts"][0]
        src = t.get("free") or panel_top(p0) or ok(p0, "shaft") is None or attached(p0, [q for q in tl if q is not t["pts"]])
        st = "OK" if (not bad and src) else "ΛΑΘΟΣ"
        res.append(("ΚΟΡΜΟΣ " + t["id"], st, "%s: %s m%s" % (t.get("txt") or t.get("n") or t["id"], G.fmt(plen(t["pts"]), 1),
                    (" – ΔΕΝ ΓΙΝΕΤΑΙ " + why(bad)) if bad else ("" if src else " – δεν ξεκινά από πίνακα / shaft / άλλον κορμό"))))
    alll = tl + [f["feed"] for f in M.FEEDS]
    for f in M.FEEDS:
        ds = [d for d in B["devs"] if d["feed"] == f["id"]]
        bad = []
        for d in ds:
            b = check_path(d["pts"])
            if b:
                bad.append((d["id"], b))
        p0 = f["feed"][0]
        src = panel_top(p0) or attached(p0, [q for q in alll if q is not f["feed"]])
        lens = [plen(d["pts"][d["nfeed"] - 1:]) for d in ds]
        fl = med_len(f["feed"], ("floor",))
        txt = "%d σημεία (%s) · από %s · τροφοδοσία %s m%s · από εκεί ως το πιο μακρινό κουτί %s m" % (
            len(ds), ", ".join(d["id"] for d in ds), f.get("src", "—"), G.fmt(plen(f["feed"]), 1), (" (στο δάπεδο %s m)" % G.fmt(fl, 1)) if fl > 0.01 else "", G.fmt(max(lens) if lens else 0, 1))
        if bad:
            txt += " – ΔΕΝ ΓΙΝΕΤΑΙ: " + " · ".join("%s %s" % (pid, why(b)) for pid, b in bad[:3])
        if not src:
            txt += " – δεν ξεκινά από κορμό"
        if not ds:
            txt += " – κανένα σημείο"
        res.append(("ΤΟΙΧΟΣ " + f["id"], "OK" if (not bad and src and ds) else "ΛΑΘΟΣ", txt))
    for e in B["extra"]:
        bad = check_path(e["pts"])
        res.append(("ΠΡΟΣΘΕΤΗ " + e["id"], "ΛΑΘΟΣ" if bad else "OK", "%s: %s m%s" % (e["n"], G.fmt(plen(e["pts"]), 1), (" – ΔΕΝ ΓΙΝΕΤΑΙ " + why(bad)) if bad else "")))
    res.append(("ΚΑΛΥΨΗ", "ΛΑΘΟΣ" if B["missing"] else "OK", ("σημεία χωρίς διαδρομή: " + ", ".join(B["missing"])) if B["missing"] else
                "κάθε πρίζα / διακόπτης / λήψη (%d σημεία) έχει πλήρη διαδρομή από τον κορμό ως το κουτί της, ελεγμένη ανά 1 cm" % len(B["devs"])))
    return res


def visible_faces():
    """Κάθε κουτί θέλει ορατή παρειά 8 cm: [(id, λόγος)] για όσα κρύβονται πίσω από άλλον τοίχο / κολόνα ή πέφτουν σε άνοιγμα πόρτας."""
    bad = []
    nrm = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    for pid, x, y, d, h, kind, opt in devices():
        if opt.get("surf") or pid in getattr(M, "INSIDE_FURN", ()):
            continue
        nx, ny = nrm[d]; tx, ty = -ny, nx
        for s in (-0.04, 0.04):
            px, py = x + tx * s + nx * 0.02, y + ty * s + ny * 0.02
            hid = [w[0] for w in walls_at(px, py, tol=-0.002)]
            if hid or col_at(px, py):
                bad.append((pid, "η παρειά του κρύβεται από %s" % (hid[0].replace("T", "Τ") if hid else "κολόνα"))); break
            bx, by = x + tx * s - nx * 0.02, y + ty * s - ny * 0.02
            if door_at(bx, by, tol=-0.002) and h < DOOR_H:
                bad.append((pid, "πέφτει μέσα σε άνοιγμα πόρτας")); break
    return bad


GRID = 0.05


def _grid():
    """Τα κενά οροφής ως «διαμερίσματα»: κάναβος 5 cm, δύο γειτονικά σημεία επικοινωνούν αν έχουν κοινό ελεύθερο ύψος. Οι οπές των δοκαριών τα ενώνουν."""
    if "grid" in _C:
        return _C["grid"]
    iv = {}
    nx, ny = int(round(14.2 / GRID)), int(round(10.4 / GRID))
    for i in range(-4, nx + 1):
        for j in range(-4, ny + 1):
            x, y = i * GRID, j * GRID
            if over(x, y) and in_sleeve(x, y, 2.73, ext=0.04, dz=0.03):
                iv[(i, j)] = (2.70, 2.76); continue
            lo, hi, why = void_iv(x, y)
            if lo is not None and hi - lo >= -1e-9:
                iv[(i, j)] = (lo, hi)
    comp = {}; n = 0
    for k in iv:
        if k in comp:
            continue
        n += 1; comp[k] = n; st = [k]
        while st:
            c = st.pop(); a = iv[c]
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (c[0] + d[0], c[1] + d[1])
                if q in iv and q not in comp and min(a[1], iv[q][1]) - max(a[0], iv[q][0]) >= -1e-9:
                    comp[q] = n; st.append(q)
    _C["grid"] = (iv, comp)
    return _C["grid"]


def comp_at(x, y):
    iv, comp = _grid()
    best = None
    for di in (0, 1, -1):
        for dj in (0, 1, -1):
            k = (int(round(x / GRID)) + di, int(round(y / GRID)) + dj)
            if k in comp:
                d = math.hypot(k[0] * GRID - x, k[1] * GRID - y)
                if best is None or d < best[0]:
                    best = (d, comp[k])
    return best[1] if best else None


def ceiling_reach():
    """Κάθε φωτιστικό / ανιχνευτής οροφής πρέπει να βρίσκεται σε κενό οροφής όπου φτάνει κάποια διαδρομή (κορμός, τροφοδοσία ή πρόσθετη)."""
    B = build(); fed = set()
    for pts in [t["pts"] for t in B["trunks"]] + [d["pts"] for d in B["devs"]] + [e["pts"] for e in B["extra"]]:
        for a, b in zip(pts, pts[1:]):
            meds = a[3] if isinstance(a[3], (tuple, list)) else (a[3],)
            if "void" not in meds and "hole" not in meds:
                continue
            L = math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3))); n = max(1, int(L / 0.025))
            for k in range(n + 1):
                t = k / float(n); c = comp_at(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                if c:
                    fed.add(c)
    items = [(q[0], q[2], q[3]) for q in M.SPOTS] + [(q[0], q[2], q[3]) for q in M.DETECTORS] + [(q[0], q[1], q[2]) for q in M.MOTION] \
        + [(q[0], (q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2) for q in M.LED if q[0] == "LED3"] + [(q[0] + " (παροχή)", q[1], q[2]) for q in M.FIXED_FREE if q[0] == "ΚΜ1"]
    bad = []; comps = {}
    for nm, x, y in items:
        c = comp_at(x, y)
        if c is None or c not in fed:
            bad.append(nm)
        comps.setdefault(c, []).append(nm)
    big = max(comps.values(), key=len) if comps else []
    oth = ["%s" % ", ".join(v) for k, v in comps.items() if v is not big and k in fed]
    txt = "%d σημεία οροφής (spots, ανιχνευτές, LED κεφαλαριού, καναλάτη): όλα σε κενό οροφής όπου φτάνει διαδρομή · %d στο ενιαίο κενό που ενώνουν οι 5 οπές%s" % (
        len(items), len(big), (" · σε απομονωμένο κενό πίσω από δοκάρι, με δική τους διαδρομή: " + " · ".join(oth)) if oth else "")
    return [("ΤΑΒΑΝΙ", "ΛΑΘΟΣ" if bad else "OK", ("σημεία οροφής σε κενό όπου ΔΕΝ φτάνει καμία διαδρομή: " + ", ".join(bad)) if bad else txt)]


if __name__ == "__main__":
    import b1_el
    bind(b1_el)
    n = 0
    for code, st, txt in check():
        print("%-7s %-14s %s" % (st, code, txt)); n += st != "OK"
    for pid, why_ in visible_faces():
        print("ΛΑΘΟΣ   ΟΡΑΤΟ %s: %s" % (pid, why_)); n += 1
    for code, st, txt in ceiling_reach():
        print("%-7s %-14s %s" % (st, code, txt)); n += st != "OK"
    print("\n%d ΛΑΘΟΣ" % n)
