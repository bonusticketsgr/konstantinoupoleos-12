"""3D μοντέλο των λουτρών: η σκηνή βγαίνει από το ίδιο μοντέλο (lt_typ) με τα φύλλα όψεων.

scene(R) → dict με απλά στοιχεία (τετράπλευρα τοίχων, πρίσματα, πολύγωνα οροφής, γραμμές αρμών, ετικέτες, φώτα, λήψεις)
σε συντεταγμένες μοντέλου (x → ανατολή, y → νότος, z → πάνω). Η σελίδα-προβολέας (viewer_template.html, three.js) τη σχεδιάζει.
Κάθε τοίχος είναι μία «ομάδα» με σημείο και κάθετο διάνυσμα προς τα μέσα: όταν η κάμερα βρεθεί πίσω του, κρύβεται (κουκλόσπιτο).
"""
import math
import lt_typ as T

HT, ZC = T.HT, T.ZC
ZU = ZC + 0.10                       # πάνω κλείσιμο της σκοτίας
SLOT = 0.095                         # σκοτία 8 cm + πάχος κατεβάσματος
EPS = 1e-4


def _inside(pt, poly):
    x, y = pt; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def _clip(a, b, poly, step=0.005):
    """Τα κομμάτια του ευθύγραμμου τμήματος a–b που είναι μέσα στο πολύγωνο (δειγματοληψία ανά 5 mm)."""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(2, int(L / step))
    out = []; start = None
    for i in range(n + 1):
        t = i / n; p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        ins = _inside(p, poly)
        if ins and start is None: start = p
        if (not ins or i == n) and start is not None:
            end = p if ins else (a[0] + (b[0] - a[0]) * (i - 1) / n, a[1] + (b[1] - a[1]) * (i - 1) / n)
            if math.hypot(end[0] - start[0], end[1] - start[1]) > 0.02: out.append((start, end))
            start = None
    return out


def _minus(a, b, cuts):
    """Το διάστημα [a, b] χωρίς τα διαστήματα cuts."""
    segs = [(a, b)]
    for c0, c1 in cuts:
        nxt = []
        for s0, s1 in segs:
            if c1 <= s0 + EPS or c0 >= s1 - EPS: nxt.append((s0, s1)); continue
            if c0 > s0 + EPS: nxt.append((s0, c0))
            if c1 < s1 - EPS: nxt.append((c1, s1))
        segs = nxt
    return segs


class Scene:
    def __init__(self, R):
        self.R = R
        self.quads = []; self.prisms = []; self.polys = []; self.lines = {}; self.groups = []; self.lights = []; self.labels = []

    def group(self, p, n):
        self.groups.append(dict(p=[round(p[0], 4), round(p[1], 4), 1.2], n=[n[0], n[1], 0]))
        return len(self.groups) - 1

    def quad(self, pts, n, m, g=-1):
        self.quads.append(dict(p=[[round(c, 4) for c in q] for q in pts], n=[round(c, 4) for c in n], m=m, g=g))

    def prism(self, outline, z0, z1, m, g=-1, e=False):
        self.prisms.append(dict(o=[[round(x, 4), round(y, 4)] for x, y in outline], z0=round(z0, 4), z1=round(z1, 4), m=m, g=g, e=e))

    def poly(self, outline, z, m, down=True):
        self.polys.append(dict(o=[[round(x, 4), round(y, 4)] for x, y in outline], z=z, m=m, down=down))

    def line(self, a, b, m, g=-1):
        self.lines.setdefault("%s|%d" % (m, g), []).extend([round(c, 4) for c in a] + [round(c, 4) for c in b])

    def strip(self, pts, w, z0, z1, m, g=-1):
        for a, b in zip(pts[:-1], pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 1e-6: continue
            px, py = -(b[1] - a[1]) / L * w / 2, (b[0] - a[0]) / L * w / 2
            self.prism([(a[0] + px, a[1] + py), (b[0] + px, b[1] + py), (b[0] - px, b[1] - py), (a[0] - px, a[1] - py)], z0, z1, m, g)

    def data(self, views):
        R = self.R
        xs = [p[0] for p in R["floor"]]; ys = [p[1] for p in R["floor"]]
        return dict(id=R["id"], name=R["name"], label={"Λ1": "Λουτρό", "Λ2": "Λουτρό γονέων"}[R["id"]], quads=self.quads, prisms=self.prisms, polys=self.polys, lines=self.lines,
                    groups=self.groups, lights=self.lights, labels=self.labels, views=views,
                    box=[min(xs), min(ys), max(xs), max(ys)])


# ------------------------------------------------------------------------------------------------ τοίχος
def wall(sc, p, q, n, E=None, default="tile", curve=False):
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    d = ((q[0] - p[0]) / L, (q[1] - p[1]) / L)
    g = sc.group(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), n)

    def P(t, z, dep=0.0):                 # dep > 0 = μέσα στον τοίχο, dep < 0 = μέσα στον χώρο
        return (p[0] + d[0] * t - n[0] * dep, p[1] + d[1] * t - n[1] * dep, z)

    def O(t, dep):
        return (p[0] + d[0] * t - n[0] * dep, p[1] + d[1] * t - n[1] * dep)

    axis = "x" if abs(d[0]) > abs(d[1]) else "y"
    mos, voids, jv = [], [], []
    if E is not None and E["map"][0] == axis and not curve:
        _, o, sg = E["map"]
        tt = lambda u: ((o + sg * u) - (p[0] if axis == "x" else p[1])) * (d[0] if axis == "x" else d[1])
        for a, b in E.get("mosaic", []):
            ta, tb = sorted((tt(a), tt(b))); ta, tb = max(ta, 0.0), min(tb, L)
            if tb - ta > 1e-3: mos.append((ta, tb))
        for v in E.get("voids", []):
            ta, tb = sorted((tt(v["u0"]), tt(v["u1"])))
            if ta >= -2e-3 and tb <= L + 2e-3: voids.append((max(ta, 0.0), min(tb, L), v))
        jv = [tt(u) for u in E.get("jv", []) if 2e-3 < tt(u) < L - 2e-3]
    elif default == "mosaic":
        mos = [(0.0, L)]
    in_mos = lambda t: any(a - EPS <= t <= b + EPS for a, b in mos)

    # ---- επιφάνεια πλακιδίων (κελιά γύρω από τα ανοίγματα)
    tc = sorted(set([0.0, L] + [x for a, b, _ in voids for x in (a, b)] + [x for a, b in mos for x in (a, b)]))
    tc = [x for i, x in enumerate(tc) if i == 0 or x - tc[i - 1] > 1e-3]
    zc = sorted(set([0.0, HT] + [min(max(v[k], 0.0), HT) for _, _, v in voids for k in ("z0", "z1")]))
    zc = [x for i, x in enumerate(zc) if i == 0 or x - zc[i - 1] > 1e-3]
    n3 = (n[0], n[1], 0)
    for t0, t1 in zip(tc[:-1], tc[1:]):
        for z0, z1 in zip(zc[:-1], zc[1:]):
            tm, zm = (t0 + t1) / 2, (z0 + z1) / 2
            if any(a <= tm <= b and v["z0"] <= zm <= min(v["z1"], HT) for a, b, v in voids): continue
            sc.quad([P(t0, z0), P(t1, z0), P(t1, z1), P(t0, z1)], n3, "mosaic" if in_mos(tm) else "tile", g)
    sc.quad([P(0, HT), P(L, HT), P(L, ZU), P(0, ZU)], n3, "paint", g)
    sc.line(P(0, ZU), P(L, ZU), "edge", g)

    # ---- αρμοί
    off = -0.0015
    vz = lambda t: [(v["z0"], min(v["z1"], HT)) for a, b, v in voids if a + EPS < t < b - EPS]
    vt = lambda z: [(a, b) for a, b, v in voids if v["z0"] + EPS < z < min(v["z1"], HT) - EPS]
    tile_zones = _minus(0.0, L, mos)
    for t in jv:
        if in_mos(t) and not any(abs(t - e) < 2e-3 for a, b in mos for e in (a, b)): continue
        for z0, z1 in _minus(0.0, HT, vz(t)): sc.line(P(t, z0, off), P(t, z1, off), "joint", g)
    for a, b in tile_zones:
        for t0, t1 in _minus(a, b, vt(1.20)): sc.line(P(t0, 1.20, off), P(t1, 1.20, off), "joint", g)
    for a, b in mos:
        if curve:
            sc.line(P(a, 0, off), P(a, HT, off), "mjoint", g)
        else:
            k = 1
            while a + k * 0.05 < b - 0.01:
                t = a + k * 0.05
                for z0, z1 in _minus(0.0, HT, vz(t)): sc.line(P(t, z0, off), P(t, z1, off), "mjoint", g)
                k += 1
        k = 1
        while k * 0.15 < HT - 0.01:
            z = k * 0.15
            for t0, t1 in _minus(a, b, vt(z)): sc.line(P(t0, z, off), P(t1, z, off), "mjoint", g)
            k += 1
        for e in (a, b):
            if 2e-3 < e < L - 2e-3: sc.line(P(e, 0, off), P(e, HT, off), "joint", g)

    # ---- ανοίγματα / ντουλάπια / καθρέπτες / εσοχές
    def reveal(ta, tb, z0, z1, dep, m, sill=True, back=False):
        sc.quad([P(ta, z0), P(ta, z1), P(ta, z1, dep), P(ta, z0, dep)], (d[0], d[1], 0), m, g)
        sc.quad([P(tb, z0), P(tb, z1), P(tb, z1, dep), P(tb, z0, dep)], (-d[0], -d[1], 0), m, g)
        sc.quad([P(ta, z1), P(tb, z1), P(tb, z1, dep), P(ta, z1, dep)], (0, 0, -1), m, g)
        if sill: sc.quad([P(ta, z0), P(tb, z0), P(tb, z0, dep), P(ta, z0, dep)], (0, 0, 1), m, g)
        if back: sc.quad([P(ta, z0, dep), P(tb, z0, dep), P(tb, z1, dep), P(ta, z1, dep)], n3, m, g)

    def box(ta, tb, d0, d1, z0, z1, m, e=False):
        sc.prism([O(ta, d0), O(tb, d0), O(tb, d1), O(ta, d1)], z0, z1, m, g, e)

    for ta, tb, v in voids:
        z0, z1 = v["z0"], min(v["z1"], HT); k = v["kind"]; tm = (ta + tb) / 2
        if k == "window":
            reveal(ta, tb, z0, z1, 0.12, "paint")
            box(ta + 0.03, tb - 0.03, 0.09, 0.10, z0 + 0.03, z1 - 0.03, "sky")
            for a_, b_ in (((ta, z0), (tb, z0)), ((tb, z0), (tb, z1)), ((tb, z1), (ta, z1)), ((ta, z1), (ta, z0))):
                sc.line(P(a_[0], a_[1], 0.088), P(b_[0], b_[1], 0.088), "dark", g)
        elif k == "door":
            reveal(ta, tb, z0, z1, 0.10, "paint", sill=False)
            box(ta + 0.02, tb - 0.02, 0.04, 0.08, 0.0, z1 - 0.02, "door", True)
            th = ta + 0.10
            box(th - 0.01, th + 0.11, -0.035, 0.04, 1.03, 1.05, "chrome")
        elif k == "cabinet":
            box(ta, tb, -0.014, 0.0, z0, z1, "cab", True)
            nd = v.get("doors", 2)
            for i in range(1, nd):
                t = ta + (tb - ta) * i / nd
                sc.line(P(t, z0, -0.0155), P(t, z1, -0.0155), "dark", g)
        elif k == "mirror":
            box(ta, tb, -0.006, 0.0, z0, z1, "mirror", True)
        elif k == "niche":
            reveal(ta, tb, z0, z1, 0.12, "niche", back=True)
            for zz in v.get("shelf", []):
                box(ta, tb, 0.004, 0.118, zz - 0.005, zz + 0.005, "shelf")
            if v.get("led"):
                box(ta + 0.015, tb - 0.015, 0.02, 0.034, z1 - 0.012, z1 - 0.003, "led")
    return g


# ------------------------------------------------------------------------------------------------ δωμάτιο
SPEC = {"Λ1": ["Α", "Β", "Γ", "Δ", "T", "Δ"],
        "Λ2": ["Α", "M", "Α", "Β", "Γ", "T", "Γ", "M", "Γ"] + ["C"] * 18 + ["Δ"]}


def _loc(base, d, n):
    return lambda s, o: (base[0] + d[0] * s + n[0] * o, base[1] + d[1] * s + n[1] * o)


def _round_rect(cx, cy, hx, hy, r=0.05, k=4):
    pts = []
    for (sx, sy, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ox, oy = cx + sx * (hx - r), cy + sy * (hy - r)
        for i in range(k + 1):
            a = math.radians(a0 + 90 * i / k)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def _ceiling(R):
    """Πολύγωνο ψευδοροφής (με τη σκοτία ανοιχτή στους τοίχους με κρυφό LED) + η γραμμή του κατεβάσματος."""
    if R["id"] == "Λ1":
        y = T.Y0 + SLOT
        return ([(T.X0, y), (T.X1, y), (T.X1, T.Y1), (T.XV, T.Y1), (T.XV, T.Y_VAN), (T.X0, T.Y_VAN)], [(T.X0, y), (T.X1, y)])
    r = T.RC - SLOT
    arc = [(T.CX - r * math.cos(math.radians(f)), T.CY + r * math.sin(math.radians(f))) for f in range(90, -1, -5)]
    edge = [(T.XKW, T.CY + r)] + arc + [(T.AX0 + SLOT, T.AYN)]
    return ([(T.XP, T.AYN), (T.XP, T.AYM), (T.AX1, T.AYM), (T.AX1, T.AYS), (T.XK, T.AYS), (T.XK, T.AYC), (T.XKW, T.AYC)] + edge, edge)


def scene(R, views, labels):
    sc = Scene(R)
    F = R["floor"]; nF = len(F)
    area = sum(F[i][0] * F[(i + 1) % nF][1] - F[(i + 1) % nF][0] * F[i][1] for i in range(nF)) / 2
    sgn = 1 if area > 0 else -1
    by = {e["id"]: e for e in R["elevs"]}
    spec = SPEC[R["id"]]
    assert len(spec) == nF, (len(spec), nF)
    # ---- δάπεδο
    sc.prism(F, -0.05, 0.0, "floor")
    for f in R["fields"]:
        a0, b0, a1, b1 = f["r"]
        segs = [((a0, b0), (a1, b0)), ((a1, b0), (a1, b1)), ((a1, b1), (a0, b1)), ((a0, b1), (a0, b0))]
        segs += [((x, b0), (x, b1)) for x in f["xc"]] + [((a0, y), (a1, y)) for y in f["yc"]]
        for a, b in segs:
            for s, e in _clip(a, b, F):
                sc.line((s[0], s[1], 0.002), (e[0], e[1], 0.002), "joint")
    # ---- τοίχοι
    for i in range(nF):
        p, q = F[i], F[(i + 1) % nF]
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        if L < 1e-4: continue
        d = ((q[0] - p[0]) / L, (q[1] - p[1]) / L)
        n = (-d[1] * sgn, d[0] * sgn)
        s = spec[i]
        wall(sc, p, q, n, by.get(s), default="mosaic" if s in ("M", "C") else "tile", curve=(s == "C"))
    # ---- ψευδοροφή με τη σκοτία
    ceil, edge = _ceiling(R)
    sc.poly(ceil, ZC, "ceiling"); sc.poly(F, ZU, "paint")
    cx = sum(p[0] for p in ceil) / len(ceil); cy = sum(p[1] for p in ceil) / len(ceil)
    for a, b in zip(edge[:-1], edge[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        if nx * (cx - a[0]) + ny * (cy - a[1]) > 0: nx, ny = -nx, -ny           # προς τον τοίχο
        sc.quad([(a[0], a[1], ZC), (b[0], b[1], ZC), (b[0], b[1], ZU), (a[0], a[1], ZU)], (nx, ny, 0), "paint")
    # ---- λεκάνη + πλακέτο
    for w in R.get("wc", []):
        if w["wall"] == "W": base, d, n = (w["face"], w["axis"]), (0, 1), (1, 0)
        else: base, d, n = (w["axis"], w["face"]), (1, 0), (0, 1)
        lc = _loc(base, d, n); Lw = T.WC_L
        out = [lc(-0.18, 0), lc(-0.18, Lw - 0.18)] + [lc(-0.18 * math.cos(math.radians(a)), Lw - 0.18 + 0.18 * math.sin(math.radians(a))) for a in range(15, 180, 15)] + [lc(0.18, Lw - 0.18), lc(0.18, 0)]
        sc.prism(out, 0.10, 0.385, "white"); sc.prism(out, 0.385, 0.42, "white2", e=True)
        g = sc.group(base, n)
        sc.prism([lc(-0.123, 0), lc(0.123, 0), lc(0.123, 0.012), lc(-0.123, 0.012)], T.Z_MIX - 0.082, T.Z_MIX + 0.082, "plate", g, True)
    # ---- κτιστός πάγκος + νιπτήρας από πάνω + μπαταρία τοίχου
    for vn in R.get("vanity", []):
        r = vn["r"]
        out = vn.get("poly") or [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
        sc.prism(out, 0.63, 0.75, "counter", e=True)
        bx, by_ = vn["basin"]
        hx, hy = (0.17, 0.24) if vn["wall"] == "W" else (0.24, 0.17)
        sc.prism(_round_rect(bx, by_, hx, hy), 0.75, 0.88, "white", e=True)
        sc.prism(_round_rect(bx, by_, hx - 0.025, hy - 0.025, r=0.035), 0.8795, 0.8815, "basin")
        if vn["wall"] == "W": base, d, n = (r[0], by_), (0, 1), (1, 0)
        else: base, d, n = (bx, r[3]), (1, 0), (0, -1)
        lc = _loc(base, d, n); g = sc.group(base, n)
        sc.prism([lc(-0.012, 0), lc(0.012, 0), lc(0.012, 0.17), lc(-0.012, 0.17)], T.Z_MIX - 0.012, T.Z_MIX + 0.012, "chrome", g)
        sc.prism([lc(0.09, 0), lc(0.13, 0), lc(0.13, 0.05), lc(0.09, 0.05)], T.Z_MIX - 0.02, T.Z_MIX + 0.02, "chrome", g)
    # ---- γυαλί ντους
    for a, b in R.get("glass", []):
        sc.strip([a, b], 0.01, 0.0, 2.10, "glass")
    # ---- ντους: μίκτης, βραχίονας, κεφαλή · γραμμικό σιφώνι
    for sh in R.get("shower", []):
        mx, my = sh["mix"]; n = sh.get("mix_dir", (1, 0)); d = (-n[1], n[0])
        lc = _loc((mx, my), d, n); g = sc.group((mx, my), n)
        sc.prism([lc(-0.075, 0), lc(0.075, 0), lc(0.075, 0.012), lc(-0.075, 0.012)], T.Z_MIX - 0.075, T.Z_MIX + 0.075, "plate", g, True)
        sc.prism([lc(-0.022, 0.012), lc(0.022, 0.012), lc(0.022, 0.045), lc(-0.022, 0.045)], T.Z_MIX - 0.022, T.Z_MIX + 0.022, "chrome", g)
        ax, ay = sh["arm_from"]; hx, hy = sh["head"]
        L = math.hypot(hx - ax, hy - ay); g2 = sc.group((ax, ay), ((hx - ax) / L, (hy - ay) / L))
        sc.strip([(ax, ay), (hx, hy)], 0.02, T.Z_HEAD - 0.01, T.Z_HEAD + 0.01, "chrome", g2)
        sc.prism([(hx + 0.125 * math.cos(math.radians(a)), hy + 0.125 * math.sin(math.radians(a))) for a in range(0, 360, 15)], T.Z_HEAD - 0.07, T.Z_HEAD - 0.05, "chrome", g2)
        sc.prism([(hx - 0.012, hy - 0.012), (hx + 0.012, hy - 0.012), (hx + 0.012, hy + 0.012), (hx - 0.012, hy + 0.012)], T.Z_HEAD - 0.05, T.Z_HEAD, "chrome", g2)
    for r in R.get("lin", []):
        sc.prism([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])], 0.0, 0.004, "dark")
    # ---- κρυφός φωτισμός: ταινίες + σημειακά φώτα κατά μήκος τους
    for Lg in R.get("lights", []):
        k = Lg["kind"]; pts = Lg["pts"]
        z = {"cove": ZC + 0.04, "niche": 1.80 - 0.012, "counter": 0.618}[k]
        if k != "niche": sc.strip(pts, 0.016, z, z + 0.01, "led")
        zl = {"cove": ZC - 0.02, "niche": 1.66, "counter": 0.52}[k]
        acc = 0.0; step = 0.42 if k != "niche" else 9
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
        nl = max(1, int(round(total / step))); targets = [(i + 0.5) * total / nl for i in range(nl)]
        for a, b in zip(pts[:-1], pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            for tg in targets:
                if acc <= tg < acc + L:
                    f = (tg - acc) / L
                    sc.lights.append(dict(p=[round(a[0] + (b[0] - a[0]) * f, 3), round(a[1] + (b[1] - a[1]) * f, 3), zl], k=k))
            acc += L
    sc.labels = labels
    return sc.data(views)


# ------------------------------------------------------------------------------------------------ λήψεις και ετικέτες
VIEWS = {
    "Λ1": {"dol": dict(name="Από πάνω", pos=[9.75, 6.05, 5.85], target=[5.66, 2.02, 1.15], fov=24),
           "alt": dict(name="Άλλη πλευρά", pos=[9.70, -2.30, 5.70], target=[5.66, 2.02, 1.15], fov=24),
           "in": dict(name="Από μέσα", pos=[6.24, 3.12, 1.60], target=[5.15, 1.70, 1.15], fov=88)},
    "Λ2": {"dol": dict(name="Από πάνω", pos=[5.75, 0.25, 5.95], target=[1.60, 4.16, 1.10], fov=25),
           "alt": dict(name="Άλλη πλευρά", pos=[5.90, 8.55, 5.90], target=[1.60, 4.16, 1.10], fov=25),
           "in": dict(name="Από μέσα", pos=[3.03, 3.78, 1.62], target=[0.85, 4.62, 0.92], fov=74)},
}
LABELS = {
    "Λ1": [dict(p=[5.72, T.Y0 + 0.04, ZC + 0.02], t="Κρυφό LED στη σκοτία της οροφής", k="led", n=[0, 1]),
           dict(p=[T.X0 - 0.05, 1.285, 1.50], t="Εσοχή ντους με ράφι και LED", k="led", n=[1, 0]),
           dict(p=[T.XV + 0.45, 3.00, 0.62], t="Κτιστός πάγκος μέσα στον τοίχο · LED από κάτω", k="led"),
           dict(p=[T.X0, 2.035, 2.20], t="Ντουλάπι κλειστό", n=[1, 0]),
           dict(p=[T.XV, 2.835, 2.05], t="Καθρέπτης", n=[1, 0]),
           dict(p=[T.X0 + T.WC_L + 0.39, 2.035, 0.02], t="78 cm μπροστά στη λεκάνη")],
    "Λ2": [dict(p=[T.AX0 + 0.04, 3.80, ZC + 0.02], t="Κρυφό LED στη σκοτία της οροφής", k="led", n=[1, 0]),
           dict(p=[2.75, T.YV + 0.05, 0.60], t="Κρυφό LED κάτω από πάγκο και ράφι", k="led"),
           dict(p=[0.99, T.YV + 0.12, 0.76], t="Ράφι ντους: ο πάγκος συνεχίζει ευθεία"),
           dict(p=[0.26, 4.89, 1.75], t="Καμπύλη γωνία με μικρό πλακάκι"),
           dict(p=[2.735, T.AYM + T.WC_L + 0.24, 0.02], t="48 cm από τη λεκάνη ως τον πάγκο"),
           dict(p=[2.735, T.AYM, 2.20], t="Ντουλάπι κλειστό", n=[0, 1]),
           dict(p=[2.20, T.AYS, 2.05], t="Καθρέπτης", n=[0, -1])],
}


def all_scenes():
    return [scene(R, VIEWS[R["id"]], LABELS[R["id"]]) for R in T.ROOMS]
