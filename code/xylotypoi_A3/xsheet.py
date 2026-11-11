"""Σχεδίαση «εργοταξιακού» φύλλου ξυλοτύπου Α3 (χωρίς οπλισμούς): γεωμετρία + διαστάσεις μελετητή + ετικέτες + στάθμες."""
import sys, os, math, json, re, datetime
import pymupdf
from shapely.geometry import box, LineString, Polygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "xylotypoi_S1_S2"))
import lib                                  # κλάση Sheet (αλυσίδες, ετικέτες, σύμβολα)
from lib import MM, S, BLUE, BLACK, GRAY, FONT_R, FONT_B
from xdims import recover
import xextract as X

A3W, A3H = 420.0, 297.0
SCALES = [50, 60, 75, 80, 100]
COLFILL = (0.80, 0.80, 0.80)
# μεγέθη κειμένων στο χαρτί (pt): (στόχος, ελάχιστο)
# R01 (Γιάννης 10/11/2026: «μίκρυνε λίγο τις γραμματοσειρές, μάζεψέ το λίγο») – περίπου 10–12 % μικρότερα από το R00
SZ = dict(col=(10.0, 7.6), beam=(8.0, 6.2), ez=(7.4, 6.0), dim=(7.8, 6.2), slab=(7.8, 6.4), h=(6.6, 5.6), level=(9.2, 7.2),
          other=(6.8, 5.6), cutmark=(8.4, 6.6), hole=(7.0, 6.0), fill=(7.6, 6.2))
FILLC = dict(hatch=(0.97, 0.93, 0.80), seed=(0.95, 0.85, 0.66))      # γέμισμα (διαγραμμισμένο του μελετητή) · μπάζωμα («φελιζόλ» του μελετητή)
HOLEC = (0.80, 0.0, 0.50)
SHAFTC = (0.0, 0.45, 0.40)          # άνοιγμα shaft Η/Μ


class Placer:
    """Τοποθέτηση κειμένων με έλεγχο συγκρούσεων (κείμενο/κείμενο, κείμενο/δομική γραμμή, κείμενο/γραμμή διάστασης)."""
    def __init__(self, sh, G, dims, extra=None):
        self.sh = sh; self.rects = []; self.pending = {}
        geoms = []
        for l in G["lines"]:
            if l["w"] >= 0.85 and not l.get("dashed"):
                geoms.append(LineString([(sh.X(l["x0"]), sh.Y(l["y0"])), (sh.X(l["x1"]), sh.Y(l["y1"]))]))
        for c in G["columns"]:
            geoms.append(Polygon([(sh.X(x), sh.Y(y)) for x, y in c]).exterior)
        self.n_struct = len(geoms)
        for d in dims:
            geoms.append(LineString([(sh.X(d["x0"]), sh.Y(d["y0"])), (sh.X(d["x1"]), sh.Y(d["y1"]))]))
        self.n_dims = len(geoms)
        for (ax, ay), (bx, by) in (extra or []):
            geoms.append(LineString([(sh.X(ax), sh.Y(ay)), (sh.X(bx), sh.Y(by))]))
        self.geoms = geoms; self.tree = STRtree(geoms) if geoms else None

    @staticmethod
    def rect(cx, cy, w, size, vert):
        h = size * 0.74
        return (cx - h / 2, cy - w / 2, cx + h / 2, cy + w / 2) if vert else (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    def clashes(self, r, skip=None, pad=0.6, own=None):
        b = box(r[0] + pad, r[1] + pad, r[2] - pad, r[3] - pad); n = 0
        if self.tree is not None:
            for i in self.tree.query(b):
                if skip is not None and i == skip: continue
                if self.geoms[i].intersects(b): n += 1
        for q in self.rects:
            if not (r[2] - pad <= q[0] or r[0] + pad >= q[2] or r[3] - pad <= q[1] or r[1] + pad >= q[3]): n += 1
        for k, q in self.pending.items():
            if k == own: continue
            if not (r[2] - pad <= q[0] or r[0] + pad >= q[2] or r[3] - pad <= q[1] or r[1] + pad >= q[3]): n += 1
        return n

    def place(self, cx, cy, text, kind, vert=False, bold=False, anchor=None, skip=None, sizes=None, own=None, nudge=None):
        """anchor: None = κέντρο, ή (dx,dy,h0): η πλευρά του κειμένου προς αυτή τη διεύθυνση μένει σταθερή (τιμές διαστάσεων).
        nudge: «along» = μετατόπιση μόνο κατά μήκος του κειμένου (τιμές διαστάσεων), «any» = και κάθετα."""
        tgt, mn = sizes or SZ[kind]
        best = None
        cand = []; s = tgt
        while s >= mn - 1e-6:
            cand.append(s); s -= 0.4
        font = FONT_B if bold else FONT_R
        def trial(s, dx, dy):
            w = font.text_length(text, fontsize=s)
            x, y = cx + dx, cy + dy
            if anchor is not None:
                h0 = anchor[2]
                x += -anchor[0] * (s * 0.74 - h0) / 2; y += -anchor[1] * (s * 0.74 - h0) / 2
            r = self.rect(x, y, w, s, vert); return (self.clashes(r, skip, own=own), s, x, y, w, r)
        for s in cand:
            t = trial(s, 0, 0)
            if best is None or t[0] < best[0]: best = t
            if t[0] == 0: break
        if best[0] > 0 and nudge:
            offs = []
            for d in (3, 6, 9, 12, 16, 20, 26, 32):
                al = [(0, -d), (0, d)] if vert else [(-d, 0), (d, 0)]
                pp = [(-d, 0), (d, 0)] if vert else [(0, -d), (0, d)]
                if d > 20 and nudge != "any": continue
                offs += al + (pp if nudge == "any" and d <= 16 else [])
            done = False
            for s in (cand[0], cand[len(cand) // 2], cand[-1]):
                for dx, dy in offs:
                    t = trial(s, dx, dy)
                    if t[0] == 0: best = t; done = True; break
                if done: break
        n, s, x, y, w, r = best
        self.rects.append(r)
        if own is not None: self.pending.pop(own, None)
        return s, x, y, w, n


def otext_c(sh, cx, cy, s, size, bold=False, vert=False, color=BLACK, mask=False):
    """κείμενο με κέντρο (cx,cy) σε συντεταγμένες χαρτιού."""
    w = (FONT_B if bold else FONT_R).text_length(s, fontsize=size)
    if vert: sh.otext(cx + size * 0.36, cy + w / 2, s, size=size, bold=bold, rot=90, color=color, mask=mask)
    else: sh.otext(cx - w / 2, cy + size * 0.36, s, size=size, bold=bold, color=color, mask=mask)


def otext_rot(sh, cx, cy, s, size, ang_deg, color=BLACK):
    sh.flush()
    w = FONT_R.text_length(s, fontsize=size)
    tw = pymupdf.TextWriter(sh.page.rect)
    p = pymupdf.Point(cx, cy)
    tw.append(pymupdf.Point(cx - w / 2, cy + size * 0.36), s, font=FONT_R, fontsize=size)
    tw.write_text(sh.page, color=color, morph=(p, pymupdf.Matrix(1, 0, 0, 1, 0, 0).prerotate(ang_deg)))


def _with_round(G):
    """αντίγραφο του G όπου τα στρογγυλά υποστυλώματα μπαίνουν ως τετράγωνα (παρειές = άκρα διαμέτρου) – για τις αλυσίδες."""
    G2 = dict(G); G2["columns"] = list(G["columns"]) + [[(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)] for cx, cy, r in G["rcols"]]
    return G2


def face_chains(G, depth_m=4.0, tol=1.0):
    """Αλυσίδες παρειών υποστυλωμάτων ανά πλευρά (πάνω / κάτω / αριστερά / δεξιά), μετρημένες από τη γεωμετρία του σχεδίου.
    Μπαίνουν τα υποστυλώματα που «φαίνονται» από την πλευρά (όχι κρυμμένα πίσω από άλλο) και απέχουν έως depth_m από το ακραίο.
    Επιστρέφει {πλευρά: [(συντεταγμένη, κοντινότερο άκρο στοιχείου), ...]} σε pt πηγής, με τα ακραία όρια του φορέα στα άκρα."""
    cols = []
    for c in G["columns"]:
        xs = [p[0] for p in c]; ys = [p[1] for p in c]
        cols.append(dict(poly=c, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys)))
    if not cols: return {}
    sx = [v for l in G["lines"] if l["w"] >= 0.85 and not l.get("dashed") and not l["blue"] for v in (l["x0"], l["x1"])] + [c["x0"] for c in cols] + [c["x1"] for c in cols]
    sy = [v for l in G["lines"] if l["w"] >= 0.85 and not l.get("dashed") and not l["blue"] for v in (l["y0"], l["y1"])] + [c["y0"] for c in cols] + [c["y1"] for c in cols]
    ext = dict(x0=min(sx), x1=max(sx), y0=min(sy), y1=max(sy))
    D = depth_m * S
    def uncovered(c, others, lo, hi):
        """ποσοστό του [lo,hi] που δεν καλύπτεται από άλλα στοιχεία"""
        ivs = sorted((max(lo, a), min(hi, b)) for a, b in others if b > lo and a < hi)
        cov = 0; cur = lo
        for a, b in ivs:
            if b <= cur: continue
            cov += b - max(a, cur); cur = b
        return 1 - cov / max(hi - lo, 1e-6)
    out = {}
    for side in ("top", "bottom", "left", "right"):
        horiz = side in ("top", "bottom")
        lo_k, hi_k = ("x0", "x1") if horiz else ("y0", "y1")
        if side == "top": edge = min(c["y0"] for c in cols); near = lambda c: c["y0"] - edge; front = lambda c, o: o["y1"] <= c["y0"] + tol
        elif side == "bottom": edge = max(c["y1"] for c in cols); near = lambda c: edge - c["y1"]; front = lambda c, o: o["y0"] >= c["y1"] - tol
        elif side == "left": edge = min(c["x0"] for c in cols); near = lambda c: c["x0"] - edge; front = lambda c, o: o["x1"] <= c["x0"] + tol
        else: edge = max(c["x1"] for c in cols); near = lambda c: edge - c["x1"]; front = lambda c, o: o["x0"] >= c["x1"] - tol
        pts = {}
        for c in cols:
            if near(c) > D: continue
            others = [(o[lo_k], o[hi_k]) for o in cols if o is not c and front(c, o)]
            if uncovered(c, others, c[lo_k], c[hi_k]) < 0.5: continue
            for (x, y) in c["poly"]:
                v, w = (x, y) if horiz else (y, x)
                k = None
                for kk in pts:
                    if abs(kk - v) <= tol: k = kk; break
                if k is None: pts[v] = w
                else:
                    better = (w < pts[k]) if side in ("top", "left") else (w > pts[k])
                    if better: pts[k] = w
        a, b = (ext["x0"], ext["x1"]) if horiz else (ext["y0"], ext["y1"])
        for v in (a, b):
            if not any(abs(kk - v) <= tol for kk in pts): pts[v] = None
        out[side] = sorted(pts.items())
    out["_ext"] = ext
    return out


RED = (0.78, 0.08, 0.08)


def find_datum(G, T, name="Κ1", corner="NW"):
    """Σταθερό σημείο = γωνία υποστυλώματος (προεπιλογή: ΒΔ γωνία του Κ1). Επιστρέφει (x, y) σε pt πηγής ή None."""
    labs = [t for t in T if t["kind"] == "col" and re.match(r"^%s\s" % re.escape(name), t["text"])]
    if not labs or not G["columns"]: return None
    t = labs[0]; best = None
    for c in G["columns"]:
        d = Polygon(c).distance(box(t["x0"], t["y0"], t["x1"], t["y1"]))
        if best is None or d < best[0]: best = (d, c)
    if best[0] > 120: return None
    xs = [p[0] for p in best[1]]; ys = [p[1] for p in best[1]]
    return (min(xs) if "W" in corner else max(xs), min(ys) if "N" in corner else max(ys))


def inner_chains(G, window_m=2.0, cross_m=1.0, tol=1.0, include=None):
    """Εσωτερικές αλυσίδες «γωνία με γωνία» κατά μήκος κάθε σειράς υποστυλωμάτων (οριζόντιες και κατακόρυφες).
    Σειρά = υποστυλώματα που η αρχή τους (πάνω / αριστερή παρειά) απέχει έως window_m (οριζόντιες) ή cross_m (κατακόρυφες).
    Επιστρέφει [dict(horiz, pts=[(συντεταγμένη, παρειά_min, παρειά_max)], lo, hi)] σε pt πηγής."""
    cols = []
    for c in G["columns"]:
        xs = [p[0] for p in c]; ys = [p[1] for p in c]
        if include is not None and not include(min(xs), min(ys), max(xs), max(ys)): continue
        cols.append(dict(poly=c, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys)))
    out = []
    for horiz in (True, False):
        k0, k1, a0, a1 = ("y0", "y1", "x0", "x1") if horiz else ("x0", "x1", "y0", "y1")
        W = (window_m if horiz else cross_m) * S
        cs = sorted(cols, key=lambda c: c[k0]); groups = []; cur = []
        for c in cs:
            if cur and (c[k0] - cur[0][k0] <= W or (not horiz and c[k0] < cur[0][k1] - 2)): cur.append(c)      # κατακόρυφες: και όταν επικαλύπτονται σε x
            else:
                if cur: groups.append(cur)
                cur = [c]
        if cur: groups.append(cur)
        for g in groups:
            if len(g) < 2: continue
            if max(c[a1] for c in g) - min(c[a0] for c in g) < 1.5 * S: continue      # στοιχεία του ίδιου πυρήνα – όχι αλυσίδα
            pts = {}
            for c in g:
                for (px, py) in c["poly"]:
                    v, w = (px, py) if horiz else (py, px)
                    kk = next((q for q in pts if abs(q - v) <= tol), None)
                    if kk is None: pts[v] = [w, w]
                    else: pts[kk] = [min(pts[kk][0], w), max(pts[kk][1], w)]
            out.append(dict(horiz=horiz, pts=sorted((v, w[0], w[1]) for v, w in pts.items()), lo=min(c[k0] for c in g), hi=max(c[k1] for c in g)))
    return out


def draw_cum(sh, pts, pos, horiz, inner, datum_v):
    """μικροί κόκκινοι αριθμοί σε κάθε παύλα της εξωτερικής αλυσίδας = απόσταση από το σταθερό σημείο (προς την πλευρά της κάτοψης)."""
    sz = 6.6
    for v in pts:
        dist = abs(v - datum_v) / S
        s = "0" if dist < 0.004 else sh.fmt(dist)
        w = FONT_B.text_length(s, fontsize=sz)
        if horiz:
            xo, yo = sh.X(v), sh.Y(pos)
            xb = xo + sz * 0.36 + 3.2
            yb = yo + (2.6 + w if inner > 0 else -2.6)       # rot=90: (x,y) = αρχή γραμμής βάσης, το κείμενο ανεβαίνει
            sh.otext(xb, yb, s, size=sz, bold=True, rot=90, color=RED, mask=True)
        else:
            xo, yo = sh.X(pos), sh.Y(v)
            xb = xo + 2.6 if inner > 0 else xo - 2.6 - w
            sh.otext(xb, yo - 1.6, s, size=sz, bold=True, color=RED, mask=True)


# ====================================================================================================================
# R01 (10/11/2026): ζώνες Ε.Ζ. εκτός, μπάζωμα / γέμισμα, μήκη δοκών, οπές αποχέτευσης / υδρορροών
# ====================================================================================================================
def _runs(lines, gap=8.0):
    """ένωση συγγραμμικών κομματιών (οριζόντιων / κατακόρυφων) σε διαδρομές: [dict(tag, k, a, b, idx)]"""
    H = {}; V = {}
    for i, l in lines:
        if abs(l["y0"] - l["y1"]) < 0.3: H.setdefault(round(l["y0"], 1), []).append((min(l["x0"], l["x1"]), max(l["x0"], l["x1"]), i))
        elif abs(l["x0"] - l["x1"]) < 0.3: V.setdefault(round(l["x0"], 1), []).append((min(l["y0"], l["y1"]), max(l["y0"], l["y1"]), i))
    out = []
    for D_, tag in ((H, "H"), (V, "V")):
        for k, iv in D_.items():
            iv.sort(); cur = [iv[0]]
            for it in iv[1:]:
                if it[0] <= max(c[1] for c in cur) + gap: cur.append(it)
                else: out.append(dict(tag=tag, k=k, a=cur[0][0], b=max(c[1] for c in cur), idx=[c[2] for c in cur])); cur = [it]
            out.append(dict(tag=tag, k=k, a=cur[0][0], b=max(c[1] for c in cur), idx=[c[2] for c in cur]))
    return out


def remove_ez(G, T, log, all_=False):
    """Ο Γιάννης (10/11/2026): «δεν με νοιάζει να φαίνονται ζώνες». Φεύγουν οι ετικέτες Ε.Ζ. και οι διακεκομμένες 0.85 που τις ορίζουν
    (διαδρομές δίπλα σε ετικέτα Ε.Ζ. + τα κλεισίματά τους). Ό,τι διακεκομμένο 0.85 μένει γράφεται στο log (KEPT DASHED)."""
    cand = [(i, l) for i, l in enumerate(G["lines"]) if l["w"] == 0.85 and l.get("dashed") and not l.get("band") and not l["blue"]]
    runs = _runs(cand) if cand else []
    ez = [t for t in T if t["kind"] == "ez"]
    for r in runs:
        if r["tag"] == "H": r["ez"] = all_ or any(abs(t["cy"] - r["k"]) <= 48 and r["a"] - 30 <= t["cx"] <= r["b"] + 30 for t in ez)
        else: r["ez"] = all_ or any(abs(t["cx"] - r["k"]) <= 48 and r["a"] - 30 <= t["cy"] <= r["b"] + 30 for t in ez)
    changed = True
    while changed:
        changed = False
        for r in runs:
            if r["ez"]: continue
            def on(v): return any(q["ez"] and q["tag"] != r["tag"] and abs(q["k"] - v) < 2.5 and q["a"] - 2.5 <= r["k"] <= q["b"] + 2.5 for q in runs)
            if on(r["a"]) and on(r["b"]): r["ez"] = True; changed = True
    kill = set(i for r in runs if r["ez"] for i in r["idx"])
    for r in runs:
        if not r["ez"]: log.append("KEPT DASHED %s %.0f [%.0f-%.0f]" % (r["tag"], r["k"], r["a"], r["b"]))
    G["lines"] = [l for i, l in enumerate(G["lines"]) if i not in kill]
    for t in T:
        if t["kind"] == "ez": t["kind"] = "drop"


def fill_regions(G, cfg):
    """Περιοχές γεμίσματος: (α) οι διαγραμμισμένες ζώνες του μελετητή («Γέμισμα μέχρι τη στ. …») = ένωση των μεγάλων γραμμών διαγράμμισης
    εκτός υποστυλωμάτων / τοιχείων, (β) ρητά πολύγωνα cfg["fills"] (π.χ. «φελιζόλ» του Σ2 = ΜΠΑΖΩΜΑ, οριοθετημένο από τα κρυφά τοιχία)."""
    out = []
    if cfg.get("fill_hatch", True):
        cb = [(min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c), Polygon(c)) for c in G["columns"]]
        hl = []
        for l in G["lines"]:
            if not l.get("hatch") or math.hypot(l["x1"] - l["x0"], l["y1"] - l["y0"]) <= cfg.get("fill_hatch_min", 20): continue
            mx, my = (l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2
            if any(b[0] <= mx <= b[2] and b[1] <= my <= b[3] and b[4].contains(Point(mx, my)) for b in cb): continue
            hl.append(LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])]).buffer(5.6, cap_style=2))        # διαγράμμιση γεμίσματος ανά ~9 pt
        if hl:
            u = unary_union(hl).buffer(-4.6).buffer(-9.5).buffer(9.5)        # άνοιγμα: φεύγουν λωρίδες στενότερες από ~0,33 m (τοιχεία, τοιχία)
            for g in (u.geoms if hasattr(u, "geoms") else [u]):
                if g.area > cfg.get("fill_min_m2", 0.6) * S * S: out.append(dict(poly=g.simplify(0.8), kind="hatch", label=cfg.get("fill_label")))
    for f in cfg.get("fills", []): out.append(dict(poly=Polygon(f["poly"]), kind="seed", label=f.get("label"), at=f.get("at")))
    return out


def beam_lengths(G, T, log):
    """Καθαρό μήκος κάθε δοκού (Γιάννης 10/11/2026: «παντού θέλω και τα μήκη δοκαριών»): από την ετικέτα βρίσκεται η λωρίδα της δοκού
    (δύο παράλληλες δομικές γραμμές σε απόσταση = πλάτος) και ο άξονάς της προεκτείνεται ως την πρώτη παρειά υποστυλώματος / τοιχείου ή
    την πρώτη δομική γραμμή που τον κόβει (παρειά δοκού στήριξης), προς τις δύο μεριές. t["L"] σε m."""
    cols = [Polygon(c) for c in G["columns"]] + [Point(cx, cy).buffer(r) for cx, cy, r in G["rcols"]]
    seen = {}
    for t in T:
        if t["kind"] != "beam": continue
        m = re.search(r"(\d+)/(\d+)", t["text"])
        if not m: continue
        blue = t.get("color", 0) != 0
        segs = [(l["x0"], l["y0"], l["x1"], l["y1"]) for l in G["lines"] if l["w"] >= 0.85 and not l.get("dashed") and (blue or not l["blue"])]
        for c in G["columns"]: segs += [(a[0], a[1], b[0], b[1]) for a, b in zip(c, c[1:] + c[:1])]
        bw = int(m.group(1)) / 100.0 * S
        ux, uy = t["dir"]; n_ = math.hypot(ux, uy) or 1.0; ux, uy = ux / n_, uy / n_; nx, ny = -uy, ux
        cx, cy = t["cx"], t["cy"]
        offs = []; offs_all = []
        for x0, y0, x1, y1 in segs:
            dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
            if L < 6 or abs(dx * nx + dy * ny) / L > 0.035: continue
            a0 = (x0 - cx) * ux + (y0 - cy) * uy; a1 = (x1 - cx) * ux + (y1 - cy) * uy
            if min(a0, a1) > 14 or max(a0, a1) < -14: continue
            offs.append((x0 - cx) * nx + (y0 - cy) * ny); offs_all.append(offs[-1])
        offs = sorted(set(round(o, 1) for o in offs if abs(o) <= bw + 16))
        far = sorted(set(round(o, 1) for o in offs_all if abs(o) <= bw + 50))
        best = None
        for lst in (offs, far):                      # πρώτα κοντά στην ετικέτα, μετά (ετικέτα δίπλα στη δοκό) έως 0,9 m μακριά
            for i, o1 in enumerate(lst):
                for o2 in lst[i + 1:]:
                    if abs((o2 - o1) - bw) <= 2.6:
                        d = 0 if o1 <= 0 <= o2 else min(abs(o1), abs(o2))
                        if best is None or d < best[0]: best = (d, o1, o2)
            if best is not None: break
        if best is not None and best[0] > 16: log.append("BEAM FAR STRIP |%s| %.2f m από την ετικέτα" % (t["text"], best[0] / S))
        if best is None: log.append("BEAM NO STRIP |%s| (%.0f,%.0f)" % (t["text"], cx, cy)); continue
        om = (best[1] + best[2]) / 2; px, py = cx + nx * om, cy + ny * om; hw = (best[2] - best[1]) / 2
        touch = {1: [], -1: []}                    # άκρα κάθετων γραμμών πάνω στις δύο ακμές της λωρίδας: {πλευρά: [s κατά μήκος]}
        for x0, y0, x1, y1 in segs:
            dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
            if L < 3 or abs(dx * ux + dy * uy) / L > 0.5: continue
            for ex_, ey_ in ((x0, y0), (x1, y1)):
                oe = (ex_ - px) * nx + (ey_ - py) * ny
                for sd_ in (1, -1):
                    if abs(oe - sd_ * hw) < 1.6: touch[sd_].append((ex_ - px) * ux + (ey_ - py) * uy)
        both = [a_ for a_ in touch[1] if any(abs(a_ - b_) < 2.0 for b_ in touch[-1])]
        ends = []
        for sgn in (1, -1):
            R = 16 * S; ex, ey = px + sgn * ux * R, py + sgn * uy * R; ray = LineString([(px, py), (ex, ey)]); dmin = None
            for c in cols:
                g = ray.intersection(c)
                if not g.is_empty:
                    d = Point(px, py).distance(g)
                    if dmin is None or d < dmin: dmin = d
            dcol = dmin
            for x0, y0, x1, y1 in segs:
                dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
                if L < 3: continue
                den = dx * (sgn * uy) - dy * (sgn * ux)
                if abs(den) / L < 0.5: continue                       # σχεδόν παράλληλη με τον άξονα
                # px + s*u = x0 + q*(dx,dy)
                s_ = ((x0 - px) * (-dy) + (y0 - py) * dx) / (sgn * ux * (-dy) + sgn * uy * dx)
                qx, qy = px + s_ * sgn * ux, py + s_ * sgn * uy
                on = min(x0, x1) - 0.6 <= qx <= max(x0, x1) + 0.6 and min(y0, y1) - 0.6 <= qy <= max(y0, y1) + 0.6
                if on and s_ > 1.0 and (dmin is None or s_ < dmin): dmin = s_
            for a_ in both:
                if sgn * a_ > 1.0 and (dmin is None or sgn * a_ < dmin): dmin = sgn * a_
            if dmin is not None and (dcol is None or dmin < dcol - 1.0):      # όχι όταν η δοκός τελειώνει σε υποστύλωμα / τοιχείο
                one = [sgn * a_ for sd_ in (1, -1) for a_ in touch[sd_] if 1.0 < sgn * a_ < dmin - 6 and dmin - sgn * a_ <= 0.65 * S]
                if one:
                    inner = min(one)                 # μόνο αν ανάμεσα στην ετικέτα και στο σημείο δεν υπάρχει άλλη συμβολή (δευτερεύουσα δοκός)
                    if not any(1.0 < sgn * a_ < inner - 3 for sd_ in (1, -1) for a_ in touch[sd_]): dmin = inner
            ends.append(dmin)
        if None in ends or min(ends) < 0.5: log.append("BEAM NO END |%s| (%.0f,%.0f) %s" % (t["text"], cx, cy, ends)); continue
        L = (ends[0] + ends[1]) / S
        if not (0.25 <= L <= 14.0): log.append("BEAM ODD L=%.2f |%s|" % (L, t["text"])); continue
        key = (round(px + ux * ends[0]), round(py + uy * ends[0]), round(px - ux * ends[1]), round(py - uy * ends[1]))
        if key in seen: log.append("BEAM SAME SPAN |%s| = |%s| L=%.2f" % (t["text"], seen[key], L))
        seen[key] = t["text"]
        t["L"] = L; t["span"] = key
        if abs(ux) > 0.999: t["faces"] = ("H", cy + best[1] * nx * 0 + best[1] * ny, cy + best[2] * ny)        # οριζόντια δοκός: οι δύο παρειές (y)
        elif abs(uy) > 0.999: t["faces"] = ("V", cx + best[1] * nx, cx + best[2] * nx)                        # κατακόρυφη δοκός: οι δύο παρειές (x)


def calibrate(G):
    """Αρχή του κοινού συστήματος συντεταγμένων των κατόψεων (m· βλ. CLAUDE.md §10Γ) σε pt πηγής, από τα Κ2 200/30 (4,60–6,60 × 0,50–0,80)
    και Κ3 30/215 (9,40–9,70 × 3,00–5,15) που υπάρχουν σε όλους τους ξυλοτύπους."""
    k2 = []; k3 = []
    for c in G["columns"]:
        xs = [p[0] for p in c]; ys = [p[1] for p in c]; w = (max(xs) - min(xs)) / S; h = (max(ys) - min(ys)) / S
        if abs(w - 2.0) < 0.03 and abs(h - 0.30) < 0.03: k2.append((min(xs) - 4.60 * S, min(ys) - 0.50 * S))
        if abs(w - 0.30) < 0.03 and abs(h - 2.15) < 0.03: k3.append((min(xs) - 9.40 * S, min(ys) - 3.00 * S))
    for a in k2:
        for b in k3:
            if abs(a[0] - b[0]) < 1.5 and abs(a[1] - b[1]) < 1.5: return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return None


def prep_holes(G, T, cfg, log):
    """Οπές πλάκας για αποχετεύσεις / υδρορροές από το τεύχος αποχετεύσεων (holes_r19.py = αντίγραφο του apox_r19.py): cfg["holes"] = "Σ2" …
    Κάθε οπή = κουτί 20 × 20 σε m του κοινού συστήματος → pt πηγής με τη βαθμονόμηση Κ2 / Κ3. Έλεγχος: το κουτί δεν κόβει υποστύλωμα
    ούτε το διασχίζει δομική γραμμή (παρειά δοκού)· «κολλητά» επιτρέπεται."""
    slab = cfg.get("holes")
    if not slab: return []
    import holes_apox as HR
    cal = calibrate(G)
    if cal is None: log.append("HOLES: NO CALIBRATION (Κ2 / Κ3)"); return []
    def PX(x): return cal[0] + x * S
    def PY(y): return cal[1] + y * S
    cols = [Polygon(c) for c in G["columns"]]
    struct = [LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])]) for l in G["lines"] if l["w"] >= 0.85 and not l.get("dashed") and not l["blue"]]
    def dtxt(d):
        d = abs(d)
        if d < 0.995: return HR.cm(d) + " cm"
        t = "%.3f" % d
        return (t[:-1] if t.endswith("0") else t).replace(".", ",") + " m"
    def face_wit(f, q, vface):
        """Βοηθητική γραμμή από την παρειά αναφοράς ως τη γραμμή διάστασης, όταν η διάσταση ΔΕΝ ακουμπά στην ίδια την παρειά (π.χ. Η1 / Η2 του Σ2:
        τα 15 cm μετριούνται από την ευθεία της Δ παρειάς της Κ2, νότια της κολόνας). vface: κατακόρυφη παρειά x = f, διάσταση στο y = q."""
        segs = []
        for pi_, pool in enumerate(([list(g.exterior.coords) for g in cols], [list(g.coords) for g in struct])):
            for pts in pool:
                for (ax, ay), (bx_, by_) in zip(pts[:-1], pts[1:]):
                    if vface and abs(ax - f) < 1.0 and abs(bx_ - f) < 1.0: lo, hi = sorted((ay, by_))
                    elif (not vface) and abs(ay - f) < 1.0 and abs(by_ - f) < 1.0: lo, hi = sorted((ax, bx_))
                    else: continue
                    if hi - lo >= 3.0: segs.append((pi_, lo, hi))
        if not segs or any(lo - 0.5 <= q <= hi + 0.5 for _, lo, hi in segs): return None      # η διάσταση ακουμπά ήδη στην παρειά (κολόνας ή δοκού)
        end = min((hi if q > hi else lo for _, lo, hi in segs), key=lambda e_: abs(q - e_))
        return (f, end, f, q) if vface else (end, f, q, f)
    out = []
    for h in HR.for_slab(slab):
        x0, y0, x1, y1 = h["box"]; bx = box(PX(x0), PY(y0), PX(x1), PY(y1)); inner = bx.buffer(-0.02 * S)
        cut = [g for g in cols if g.intersection(inner).area > 1.0]            # κόβει υποστύλωμα / τοιχείο = ΛΑΘΟΣ
        edge = [g for g in struct if g.intersects(inner)]                        # γραμμή ξυλοτύπου (ακμή πλάκας / παρειά δοκού) ΜΕΣΑ από το κουτί
        dmin = min([bx.distance(g) for g in struct] + [bx.distance(g) for g in cols] + [1e9])
        links = []; wits = []
        d, e = HR.edge_d(x0, x1, h["rx"][0]); yy = h["dxy"] if h["dxy"] is not None else (y0 + y1) / 2
        if yy > y1: yy = y1 + 0.09                       # R05: 9 cm έξω από το κουτί
        elif yy < y0: yy = y0 - 0.09
        if abs(d) > 1e-6: links.append((PX(h["rx"][0]), PY(yy), PX(e), PY(yy), dtxt(d))); wits.append(face_wit(PX(h["rx"][0]), PY(yy), True))
        d, e = HR.edge_d(y0, y1, h["ry"][0]); xx = h["dyx"] if h["dyx"] is not None else (x0 + x1) / 2
        if abs(d) > 1e-6: links.append((PX(xx), PY(h["ry"][0]), PX(xx), PY(e), dtxt(d))); wits.append(face_wit(PY(h["ry"][0]), PX(xx), False))
        out.append(dict(name="Η%d" % h["id"], what="%s %s" % (h["name"], h["pipe"]), x=PX(h["x"]), y=PY(h["y"]), r=HR.PIPE_OD[h["pipe"]] / 2 * S,
                        box=(PX(x0), PY(y0), PX(x1), PY(y1)), pos=HR.hole_pos(h), links=links, wits=[w_ for w_ in wits if w_], clear=(-1.0 if cut else dmin / S), onedge=bool(edge)))
        log.append("HOLE Η%-2d %-22s %s · %s" % (h["id"], out[-1]["what"], out[-1]["pos"], "ΚΟΒΕΙ ΥΠΟΣΤΥΛΩΜΑ  <-- ΛΑΘΟΣ" if cut else "ΓΡΑΜΜΗ ΞΥΛΟΤΥΠΟΥ ΜΕΣΑ ΑΠΟ ΤΟ ΚΟΥΤΙ (ακμή πλάκας / παρειά δοκού)  <-- ΝΑ ΕΛΕΓΧΘΕΙ" if edge else "καθαρό %.1f cm" % (dmin / S * 100)))
    ex = []
    if slab in ("Σ3", "Σ4", "Σ5", "Σ6"):
        for (gx0, gy0, gx1, gy1), nm, tx in HR.GAPS:
            ex.append(dict(kind="gap", name=nm, text=tx, x=PX(HR.RD[nm][0]), y=PY(HR.RD[nm][1]), box=(PX(gx0), PY(gy0), PX(gx1), PY(gy1))))
    if slab == "Σ2":
        b = HR.EXIT_BOX; ex.append(dict(kind="exit", name="Χ1", text=HR.EXIT_TXT, x=PX(-0.75), y=PY(15.30), box=(PX(b[0]), PY(b[1]), PX(b[2]), PY(b[3]))))
    cfg["_hole_extra"] = ex; cfg["_hole_sheet"] = HR.SHEET.get(slab, ""); cfg["_hole_src"] = HR.SOURCE; cfg["_shaft"] = None
    if slab in HR.SHAFT_SLABS:
        x0, y0, x1, y1 = HR.SHAFT; rk3, rk4, rb = HR.SHAFT_REF
        bx = box(PX(x0), PY(y0), PX(x1), PY(y1)); inner = bx.buffer(-0.02 * S)
        cut = [g for g in cols if g.intersection(inner).area > 1.0]; edge = [g for g in struct if g.intersects(inner)]
        cfg["_shaft"] = dict(box=(PX(x0), PY(y0), PX(x1), PY(y1)), xs=[PX(rk3), PX(x0), PX(x1), PX(rk4)], ych=PY(y0 - 0.13), yb=PY(rb),
                             vals=[HR.cm(x0 - rk3) + " cm", HR.cm(x1 - x0) + " cm", HR.cm(rk4 - x1) + " cm"], depth=HR.cm(y1 - y0) + " cm",
                             text="άνοιγμα %s × %s στη μέση Κ3 – ανελκυστήρα: %s cm από την Α παρ. Κ3 και %s cm από το τοιχείο Κ4 · κολλητά στη Β παρ. Δ2.1 · βάθος %s ως την εσωτ. παρειά του τοίχου Τ5-01"
                                  % (HR.cm(x1 - x0), HR.cm(y1 - y0), HR.cm(x0 - rk3), HR.cm(rk4 - x1), HR.cm(y1 - y0)), cut=bool(cut), onedge=bool(edge))
        log.append("SHAFT S1 %s × %s · %s" % (HR.cm(x1 - x0), HR.cm(y1 - y0), "ΚΟΒΕΙ ΥΠΟΣΤΥΛΩΜΑ  <-- ΛΑΘΟΣ" if cut else "γραμμή ξυλοτύπου μέσα από το άνοιγμα  <-- ΝΑ ΕΛΕΓΧΘΕΙ" if edge else "καθαρό"))
    return out


def plan_chains(cfg, D):
    """Αλυσίδες παρειών του φύλλου: (GC, FC εξωτερικές ανά πλευρά, sides, inner εσωτερικές, datum)."""
    G = D["G"]
    GC = _with_round(G) if cfg.get("chain_round") else G
    FC = face_chains(GC, cfg.get("chain_depth", 4.0), tol=cfg.get("chain_tol", 1.0)) if cfg.get("chains", True) else {}
    sides = [sd for sd in cfg.get("chain_sides", ("top", "bottom", "left", "right")) if sd in FC]
    datum = find_datum(G, D["T"], *cfg["datum"]) if (cfg.get("chains", True) and cfg.get("datum")) else None
    inc = cfg.get("inner_include")
    if cfg.get("inner_names"):        # εσωτερικές αλυσίδες μόνο για τα υποστυλώματα με αυτά τα ονόματα
        labs = [t for t in D["T"] if t["kind"] == "col"]
        ok_boxes = []
        for c in G["columns"]:
            pc = Polygon(c)
            if not labs: break
            t = min(labs, key=lambda t: pc.distance(box(t["x0"], t["y0"], t["x1"], t["y1"])))
            if re.match(cfg["inner_names"], t["text"]): ok_boxes.append((min(p[0] for p in c), min(p[1] for p in c)))
        inc = lambda x0, y0, x1, y1: any(abs(x0 - bx_) < 0.5 and abs(y0 - by_) < 0.5 for bx_, by_ in ok_boxes)
    inner = inner_chains(GC, include=inc, tol=cfg.get("chain_tol", 1.0)) if cfg.get("inner", True) and cfg.get("chains", True) else []
    return GC, FC, sides, inner, datum


def cover_dims(D, FC, sides, inner, log, add=True):
    """Έλεγχος ΚΑΛΥΨΗΣ για τον καλουπατζή (Γιάννης 11/11/2026: «οι διαστάσεις να είναι όσες πρέπει για τους καλουπατζήδες»): κάθε ακμή
    δοκού / πλάκας του ξυλοτύπου (συνεχής δομική γραμμή ≥ 0,45 m) πρέπει να «δένεται» από κάποια διάσταση – άκρο διάστασης μελετητή ή
    αλυσίδας παρειών στην ίδια συντεταγμένη, ή να είναι η άλλη παρειά δοκού με γνωστό πλάτος (ετικέτα) που η μία της παρειά δένεται.
    Για ό,τι μένει ακάλυπτο προστίθεται ΣΥΜΠΛΗΡΩΜΑΤΙΚΗ διάσταση ως την κοντινότερη δεμένη παράλληλη ακμή (extra=True).
    Επιστρέφει [(τύπος, συντεταγμένη)] που έμειναν ακάλυπτες."""
    G = D["G"]; Xc = []; Yc = []
    for d in D["dims"]:
        if d.get("slant"): continue
        if d["dir"] == "H": Xc += [d["x0"], d["x1"]]
        else: Yc += [d["y0"], d["y1"]]
    for sd in sides: (Xc if sd in ("top", "bottom") else Yc).extend(v for v, w in FC[sd])
    for ch in inner: (Xc if ch["horiz"] else Yc).extend(q[0] for q in ch["pts"])
    def cov(v, L): return any(abs(v - q) <= 1.3 for q in L)
    def beam_implied():
        ch_ = True
        while ch_:
            ch_ = False
            for t in D["T"]:
                f = t.get("faces")
                if not f: continue
                L = Yc if f[0] == "H" else Xc
                if cov(f[1], L) != cov(f[2], L): L.append(f[2] if cov(f[1], L) else f[1]); ch_ = True
    beam_implied()
    segs = {"V": [], "H": []}
    for l in G["lines"]:
        if l["w"] < 0.85 or l.get("dashed") or l["blue"]: continue
        if abs(l["x0"] - l["x1"]) < 0.3: segs["V"].append((l["x0"], min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
        elif abs(l["y0"] - l["y1"]) < 0.3: segs["H"].append((l["y0"], min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
    for c in G["columns"]:
        for (ax, ay), (bx_, by_) in zip(c, c[1:] + c[:1]):
            if abs(ax - bx_) < 0.3: segs["V"].append((ax, min(ay, by_), max(ay, by_)))
            elif abs(ay - by_) < 0.3: segs["H"].append((ay, min(ax, bx_), max(ax, bx_)))
    left = []
    for tp in ("V", "H"):
        L = Xc if tp == "V" else Yc
        cand = sorted([s_ for s_ in segs[tp] if s_[2] - s_[1] >= 0.45 * S], key=lambda s_: -(s_[2] - s_[1]))
        for v, a, b in cand:
            if cov(v, L): continue
            near = sorted(set(round(q, 1) for q in L if 2.0 < abs(q - v) <= 6.0 * S), key=lambda q: abs(q - v))
            pick = None
            for c_ in near[:8]:
                ov = [(max(a, s_[1]), min(b, s_[2])) for s_ in segs[tp] if abs(s_[0] - c_) <= 1.3 and min(b, s_[2]) - max(a, s_[1]) > 6]
                if ov:
                    o = max(ov, key=lambda o_: o_[1] - o_[0]); pick = (c_, (o[0] + o[1]) / 2); break
            if pick is None and near: pick = (near[0], (a + b) / 2)
            if pick is None or not add: left.append((tp, v)); continue
            c_, m = pick; lo, hi = min(v, c_), max(v, c_); val = lib.Sheet.fmt((hi - lo) / S)
            if tp == "H": D["dims"].append(dict(x0=m, y0=lo, x1=m, y1=hi, value=val, dir="V", tx=m - 6, ty=(lo + hi) / 2, side=-1, extra=True))
            else: D["dims"].append(dict(x0=lo, y0=m, x1=hi, y1=m, value=val, dir="H", tx=(lo + hi) / 2, ty=m - 6, side=-1, extra=True))
            L.append(v); beam_implied()
            log.append("ΣΥΜΠΛΗΡΩΜΑΤΙΚΗ ΔΙΑΣΤΑΣΗ %s για ακμή %s στο (%.0f, %.0f)" % (val, "πλάκας/δοκού κατακόρυφη" if tp == "V" else "πλάκας/δοκού οριζόντια", v if tp == "V" else m, m if tp == "V" else v))
    return left


def choose_layout(bb, force_scale=None, force_layout=None, title_w=60.0, title_h=30.0, margin=6.0):
    """bb = (x0,y0,x1,y1) σε pt πηγής (1:50). Επιστρέφει (κλίμακα, διάταξη, διαθέσιμο ορθογώνιο σε mm)."""
    wm = (bb[2] - bb[0]) / S * 1000 / 1.0; hm = (bb[3] - bb[1]) / S * 1000        # mm στην πραγματικότητα
    opts = []
    for lay in (("right",) if force_layout == "right" else ("bottom",) if force_layout == "bottom" else ("right", "bottom")):
        if lay == "right": aw, ah = A3W - 2 * margin - title_w - 2, A3H - 2 * margin
        else: aw, ah = A3W - 2 * margin, A3H - 2 * margin - title_h - 2
        for sc in ([force_scale] if force_scale else SCALES):
            if wm / sc <= aw and hm / sc <= ah: opts.append((sc, lay, aw, ah)); break
    opts.sort(key=lambda o: (o[0], o[1] != "right"))
    return opts[0]


def prep(page, DR, cfg, S_loc=S):
    """Εξαγωγή μιας περιοχής: γεωμετρία, κείμενα, διαστάσεις μελετητή και όρια περιεχομένου (pt πηγής)."""
    region = cfg["region"]
    regs = [tuple(region)] if isinstance(region[0], (int, float)) else [tuple(r) for r in region]
    G = X.extract_geometry(page, regs, keep=cfg.get("keep", ()), stairs=cfg.get("stairs", ()), sections=cfg.get("cuts", False),
                           diag_min=cfg.get("diag_min", 50), drawings=DR, section_mode=cfg.get("section", False))
    EXC = [tuple(r) for r in cfg.get("exclude", [])]
    def exc(x, y): return any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in EXC)
    if EXC:
        G["lines"] = [l for l in G["lines"] if not ((exc(l["x0"], l["y0"]) and exc(l["x1"], l["y1"])) or exc((l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2))]
        G["ext"] = [l for l in G["ext"] if not (exc(l["x0"], l["y0"]) or exc(l["x1"], l["y1"]))]
        G["cuts"] = [l for l in G["cuts"] if not (exc(l["x0"], l["y0"]) and exc(l["x1"], l["y1"]))]
        G["columns"] = [c for c in G["columns"] if not all(exc(x, y) for x, y in c)]
        G["curves"] = [c for c in G["curves"] if not exc(*c["pts"][0])]
        G["circles"] = [c for c in G["circles"] if not exc(c["cx"], c["cy"])]
        G["rcols"] = [c for c in G["rcols"] if not exc(c[0], c[1])]
    T = [t for t in X.load_texts(page, regs) if not exc(t["cx"], t["cy"])]
    for t in T: t["kind"] = X.classify(t)
    if cfg.get("section"):
        lv = [t for t in T if t["kind"] == "level"]
        ob = G.get("outline_box", [])
        xcut = max(b[2] for b in ob) if ob else None; ymin = min(b[1] for b in ob) if ob else 0; ymax = max(b[3] for b in ob) if ob else 0
        for l in G["thin"]:
            horiz = abs(l["y0"] - l["y1"]) < 0.05
            under = horiz and any(t["x0"] - 14 <= min(l["x0"], l["x1"]) and max(l["x0"], l["x1"]) <= t["x1"] + 14 and -1 <= l["y0"] - t["y1"] <= 4 for t in lv)
            cut = xcut is not None and abs((l["x0"] + l["x1"]) / 2 - xcut) <= 12 and ymin - 25 <= (l["y0"] + l["y1"]) / 2 <= ymax + 25 and abs(l["x0"] - l["x1"]) < 14
            if under or cut: G["lines"].append(l)
        for t in T:
            if t["kind"] == "other": t["kind"] = "drop"
        # τρίγωνα στάθμης: μόνο όσα είναι κοντά σε κείμενο στάθμης
        G["lines"] = [l for l in G["lines"] if not l.get("tri") or any(t["x0"] - 16 <= l["x0"] <= t["x1"] + 16 and -2 <= l["y0"] - t["y1"] <= 12 for t in lv)]
    for fix in cfg.get("retext", []):          # (παλιό κείμενο, νέο κείμενο ή None = σβήσιμο, είδος)
        for t in T:
            if t["text"] == fix[0]:
                if fix[1] is None: t["kind"] = "drop"
                else: t["text"] = fix[1]; t["kind"] = fix[2] if len(fix) > 2 else "other"
    for mv in cfg.get("move", []):             # (κείμενο, dx, dy) σε pt πηγής: μετακίνηση ετικέτας που πέφτει πάνω σε άλλα
        for t in T:
            if t["text"] == mv[0]:
                for k_ in ("cx", "x0", "x1"): t[k_] += mv[1]
                for k_ in ("cy", "y0", "y1"): t[k_] += mv[2]
    log0 = []; fills = []; holes = []
    if not cfg.get("section"):
        if not cfg.get("show_ez"): remove_ez(G, T, log0, all_=cfg.get("ez_all", False))
        fills = fill_regions(G, cfg)
        if cfg.get("beam_len", True): beam_lengths(G, T, log0)
        holes = prep_holes(G, T, cfg, log0)
    bbr = (min(r[0] for r in regs), min(r[1] for r in regs), max(r[2] for r in regs), max(r[3] for r in regs))
    dims_all = recover(DR, [t for t in T if t["kind"] == "dim"], (bbr[0] - 30, bbr[1] - 30, bbr[2] + 30, bbr[3] + 30), S=S_loc)
    skipd = cfg.get("skip_dims", [])
    def skipped(d): return any(abs(d["tx"] - sx) < 6 and abs(d["ty"] - sy) < 6 for sx, sy in skipd)
    dims = [d for d in dims_all if not d.get("unresolved") and not skipped(d)]
    unres = [d for d in dims_all if d.get("unresolved") and not skipped(d)]
    if cfg.get("dim_touch", True):
        # κρατιούνται μόνο οι διαστάσεις που τα δύο άκρα τους πατάνε σε δομική γραμμή (οι άλλες είναι μήκη ράβδων οπλισμού)
        vx, hy = [], []
        for l in G["lines"]:
            if l.get("hatch"): continue
            if abs(l["x0"] - l["x1"]) < 0.6: vx.append((l["x0"], min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
            if abs(l["y0"] - l["y1"]) < 0.6: hy.append((l["y0"], min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
        for c in G["columns"]:
            for (ax, ay), (bx_, by_) in zip(c, c[1:] + c[:1]):
                if abs(ax - bx_) < 0.6: vx.append((ax, min(ay, by_), max(ay, by_)))
                if abs(ay - by_) < 0.6: hy.append((ay, min(ax, bx_), max(ax, bx_)))
        R = cfg.get("dim_touch_range", 500)
        for cx_, cy_, r_ in G["rcols"]:
            vx += [(cx_ - r_, cy_ - r_, cy_ + r_), (cx_ + r_, cy_ - r_, cy_ + r_), (cx_, cy_ - r_, cy_ + r_)]
            hy += [(cy_ - r_, cx_ - r_, cx_ + r_), (cy_ + r_, cx_ - r_, cx_ + r_), (cy_, cx_ - r_, cx_ + r_)]
        cb = [(min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c)) for c in G["columns"]]
        def tx_(xe, y): return any(abs(v - xe) < 1.6 and a_ - R <= y <= b_ + R for v, a_, b_ in vx)
        def ty_(ye, x_): return any(abs(v - ye) < 1.6 and a_ - R <= x_ <= b_ + R for v, a_, b_ in hy)
        def inside_col(d):
            """διάσταση που «κόβει» ένα υποστύλωμα (π.χ. 0,60 | 0,63 ως το κέντρο του Κ2): και τα δύο άκρα μέσα στο πλάτος του ίδιου
            στοιχείου, χωρίς να είναι το πλήρες πλάτος του."""
            for c in cb:
                if d["dir"] == "H":
                    lo, hi, p0, p1, near = c[0], c[2], d["x0"], d["x1"], c[1] - 160 <= d["y0"] <= c[3] + 160
                else:
                    lo, hi, p0, p1, near = c[1], c[3], d["y0"], d["y1"], c[0] - 160 <= d["x0"] <= c[2] + 160
                if near and lo - 1.6 <= p0 and p1 <= hi + 1.6 and not (abs(p0 - lo) < 1.6 and abs(p1 - hi) < 1.6): return True
            return False
        strict = cfg.get("dim_touch") == "strict"
        def ok(d):
            """strict: και τα δύο άκρα σε δομική γραμμή (αλλιώς είναι μήκος ράβδου – θεμελίωση). Κανονικά: φεύγουν μόνο οι διαστάσεις
            που αναφέρονται στη ΜΕΣΗ υποστυλώματος (ο Γιάννης 10/11/2026: αναφορά οι γωνίες των κολόνων, όχι η μέση τους)."""
            if d.get("slant"): return True
            if strict:
                if d["dir"] == "H": return all(tx_(xe, d["y0"]) for xe in (d["x0"], d["x1"]))
                return all(ty_(ye, d["x0"]) for ye in (d["y0"], d["y1"]))
            if d["dir"] == "H": touch_all = all(tx_(xe, d["y0"]) for xe in (d["x0"], d["x1"]))
            else: touch_all = all(ty_(ye, d["x0"]) for ye in (d["y0"], d["y1"]))
            return touch_all or not inside_col(d)
        D_drop = [d for d in dims if not ok(d)]
        dims = [d for d in dims if ok(d)]
    for m in cfg.get("manual_dims", []):       # (x0, y0, x1, y1, "τιμή", tx, ty): διάσταση μελετητή που δεν αναγνωρίστηκε αυτόματα
        dims.append(dict(x0=m[0], y0=m[1], x1=m[2], y1=m[3], value=m[4], dir="H" if abs(m[1] - m[3]) < 0.5 else "V", tx=m[5], ty=m[6], side=-1))
        unres = [u for u in unres if not (abs(u["tx"] - m[5]) < 6 and abs(u["ty"] - m[6]) < 6)]
    xs, ys = [], []
    for c in G["columns"]:
        xs += [p[0] for p in c]; ys += [p[1] for p in c]
    for l in G["lines"]:
        xs += [l["x0"], l["x1"]]; ys += [l["y0"], l["y1"]]
    for c in G["curves"]:
        xs += [p[0] for p in c["pts"]]; ys += [p[1] for p in c["pts"]]
    for d in dims:
        xs += [d["x0"], d["x1"], d["tx"]]; ys += [d["y0"], d["y1"], d["ty"]]
    for t in T:
        if t["kind"] in ("col", "beam", "ez", "level", "slab", "other", "title"):
            xs += [t["x0"], t["x1"]]; ys += [t["y0"], t["y1"]]
    pad = cfg.get("pad", 10)
    bb = (max(min(xs) - pad, bbr[0] - 40), max(min(ys) - pad, bbr[1] - 40), min(max(xs) + pad, bbr[2] + 40), min(max(ys) + pad, bbr[3] + 40))
    return dict(G=G, T=T, dims=dims, unres=unres, bb=bb, cfg=cfg, dropped=locals().get("D_drop", []), fills=fills, holes=holes, log0=log0)


def draw(sh, D, bb_in, FC=None, sides=(), log=None, datum=None, inner=()):
    """Σχεδίαση μιας περιοχής με τον τρέχοντα μετασχηματισμό του sh (OX, OY, SX0, SY0, K)."""
    G, T, dims, unres, cfg = D["G"], D["T"], D["dims"], D["unres"], D["cfg"]
    K = sh.K; bb = D.get("bb_out", bb_in); log = log if log is not None else []
    sh.G = G
    if cfg.get("section"): return draw_section(sh, D, log)
    def inbb(t): return bb_in[0] <= t["cx"] <= bb_in[2] and bb_in[1] <= t["cy"] <= bb_in[3]
    EXTC = (0.5, 0.5, 0.5)
    log += D.get("log0", [])
    # ---------------- γέμισμα / μπάζωμα (κάτω από όλα)
    for f in D.get("fills", []):
        gs = f["poly"].geoms if hasattr(f["poly"], "geoms") else [f["poly"]]
        for g in gs:
            sh.shape.draw_polyline([sh.P(x, y) for x, y in g.exterior.coords]); sh.shape.finish(width=0, color=None, fill=FILLC[f["kind"]])
            for hole_ in g.interiors:
                sh.shape.draw_polyline([sh.P(x, y) for x, y in hole_.coords]); sh.shape.finish(width=0, color=None, fill=(1, 1, 1))
    # ---------------- γεωμετρία
    for c in G["columns"]:
        sh.shape.draw_polyline([sh.P(x, y) for x, y in c] + [sh.P(*c[0])]); sh.shape.finish(width=0, color=None, fill=COLFILL)
    for cx, cy, r in G["rcols"]:
        sh.ocircle(sh.X(cx), sh.Y(cy), r * K, 0, None, COLFILL)
    dpts = [(d["x0"], d["y0"]) for d in dims] + [(d["x1"], d["y1"]) for d in dims]
    def near_dim(e):
        if abs(e["x0"] - e["x1"]) < 0.5:
            return any(abs(px - e["x0"]) < 1.5 and min(e["y0"], e["y1"]) - 6 <= py <= max(e["y0"], e["y1"]) + 6 for px, py in dpts)
        return any(abs(py - e["y0"]) < 1.5 and min(e["x0"], e["x1"]) - 6 <= px <= max(e["x0"], e["x1"]) + 6 for px, py in dpts)
    for e in G["ext"]:
        if not near_dim(e): continue
        sh.sline(max(bb[0], min(bb[2], e["x0"])), max(bb[1], min(bb[3], e["y0"])), max(bb[0], min(bb[2], e["x1"])), max(bb[1], min(bb[3], e["y1"])),
                 w=0.22, color=EXTC, dashes="[0.7 1.9] 0")
    sh.draw_geometry(wmap={1.7: 1.25, 0.85: 0.7 if not cfg.get("section") else 1.0, 0.57: 0.35, 0.28: 0.2}, drop=lambda l: l.get("band"))
    for l in G["lines"]:
        if l.get("band"): sh.sline(l["x0"], l["y0"], l["x1"], l["y1"], w=0.55, dashes="[2.6 1.8] 0")
    for f in D.get("fills", []):
        if f["kind"] == "seed":
            pts = [sh.P(x, y) for x, y in f["poly"].exterior.coords]
            sh.shape.draw_polyline(pts); sh.shape.finish(width=1.1, color=(0.45, 0.25, 0.0), dashes="[5 2.5] 0")
    for c in G["columns"]:
        sh.shape.draw_polyline([sh.P(x, y) for x, y in c] + [sh.P(*c[0])]); sh.shape.finish(width=1.25, color=BLACK)
    for l in G["cuts"]:
        sh.sline(l["x0"], l["y0"], l["x1"], l["y1"], w=0.7, color=(0.35, 0.35, 0.35))
    sh.flush()
    # ---------------- γραμμές αναφοράς των αλυσίδων παρειών
    rowpos = {}
    for sd in sides:
        off = (7.4 if datum else 4.2) * MM / K
        rowpos[sd] = (bb_in[1] - off) if sd == "top" else (bb_in[3] + off) if sd == "bottom" else (bb_in[0] - off) if sd == "left" else (bb_in[2] + off)
        for v, w in FC[sd]:
            if w is None: w = FC["_ext"]["y0" if sd == "top" else "y1" if sd == "bottom" else "x0" if sd == "left" else "x1"]
            if sd in ("top", "bottom"): sh.sline(v, w, v, rowpos[sd], w=0.22, color=EXTC, dashes="[0.7 1.9] 0")
            else: sh.sline(w, v, rowpos[sd], v, w=0.22, color=EXTC, dashes="[0.7 1.9] 0")
    sh.flush()
    # ---------------- εσωτερικές αλυσίδες «γωνία με γωνία» κατά μήκος των σειρών υποστυλωμάτων
    ich = []
    if inner:
        trects = []
        for t in T:
            if t["kind"] in ("col", "beam", "ez", "level", "slab", "other") and inbb(t):
                e_ = 0.25 * (max(t["x1"] - t["x0"], t["y1"] - t["y0"])) if t["kind"] == "col" else 0      # οι ετικέτες Κ μεγαλώνουν στο χαρτί
                for _ in range(3 if t["kind"] == "col" else 1): trects.append((t["x0"] - 2 - e_, t["y0"] - 2 - e_, t["x1"] + 2 + e_, t["y1"] + 2 + e_))
        for d in dims: trects.append((min(d["x0"], d["x1"], d["tx"] - 8) - 2, min(d["y0"], d["y1"], d["ty"] - 5) - 2, max(d["x0"], d["x1"], d["tx"] + 8) + 2, max(d["y0"], d["y1"], d["ty"] + 5) + 2))
        for c in G["circles"]: trects.append((c["cx"] - 13, c["cy"] - 13, c["cx"] + 13, c["cy"] + 13))
        cpol = [Polygon(c) for c in G["columns"]]
        hboxes = [box(h["box"][0] - 0.30 * S, h["box"][1] - 0.30 * S, h["box"][2] + 0.30 * S, h["box"][3] + 0.30 * S) for h in D.get("holes", [])]
        if cfg.get("_shaft"): q_ = cfg["_shaft"]["box"]; hboxes.append(box(q_[0] - 0.15 * S, q_[1] - 0.45 * S, q_[2] + 0.15 * S, q_[3] + 0.15 * S))
        allx = [p[0] for c in G["columns"] for p in c]; ally = [p[1] for c in G["columns"] for p in c]
        mid_all = ((min(allx) + max(allx)) / 2, (min(ally) + max(ally)) / 2)        # οι αλυσίδες προτιμούν την πλευρά προς το εσωτερικό
        taken = []
        for ch in inner:
            a, b = ch["pts"][0][0], ch["pts"][-1][0]; best = None
            for off_m in (0.42, -0.42, 0.66, -0.66, 0.9, -0.9, 1.15, -1.15, 1.45, -1.45):
                pos = (ch["hi"] + off_m * S) if off_m > 0 else (ch["lo"] + off_m * S)
                band = (a, pos - 13 / K, b, pos + 3 / K) if ch["horiz"] else (pos - 13 / K, a, pos + 3 / K, b)
                n = sum(1 for r in trects if not (r[2] < band[0] or r[0] > band[2] or r[3] < band[1] or r[1] > band[3]))
                ln = LineString([(a, pos), (b, pos)] if ch["horiz"] else [(pos, a), (pos, b)])
                n += 4 * sum(1 for p in cpol if p.intersects(ln))
                n += 10 * sum(1 for hb in hboxes if hb.intersects(ln))       # R05: καμία αλυσίδα μέσα από κουτί οπής / shaft ή από τις διαστάσεις τους
                n += 3 * sum(1 for hz, r in taken if hz == ch["horiz"] and not (r[2] < band[0] or r[0] > band[2] or r[3] < band[1] or r[1] > band[3]))
                n += 1.2 * abs(off_m)
                # όχι πάνω σε παρειά δοκού / τοιχείου (συγγραμμική δομική γραμμή) ούτε μέσα σε δοκό
                ov = 0.0
                for l in G["lines"]:
                    if l["w"] < 0.85 or l.get("dashed"): continue
                    if ch["horiz"] and abs(l["y0"] - l["y1"]) < 0.5 and abs(l["y0"] - pos) < 9 / K: ov += max(0, min(b, max(l["x0"], l["x1"])) - max(a, min(l["x0"], l["x1"])))
                    if not ch["horiz"] and abs(l["x0"] - l["x1"]) < 0.5 and abs(l["x0"] - pos) < 9 / K: ov += max(0, min(b, max(l["y0"], l["y1"])) - max(a, min(l["y0"], l["y1"])))
                n += 6.0 * ov / max(b - a, 1)
                n += 0.6 if (pos - mid_all[1 if ch["horiz"] else 0]) * (pos - (ch["lo"] + ch["hi"]) / 2) < 0 and abs(pos - mid_all[1 if ch["horiz"] else 0]) > abs((ch["lo"] + ch["hi"]) / 2 - mid_all[1 if ch["horiz"] else 0]) else 0
                if best is None or n < best[0]: best = (n, pos, band)
            ch = dict(ch); ch["pos"] = best[1]; ich.append(ch); taken.append((ch["horiz"], best[2]))
            for v, w0, w1 in ch["pts"]:
                w = w1 if best[1] > w1 else w0 if best[1] < w0 else None
                if w is None: continue
                if ch["horiz"]: sh.sline(v, w, v, best[1], w=0.22, color=EXTC, dashes="[0.7 1.9] 0")
                else: sh.sline(w, v, best[1], v, w=0.22, color=EXTC, dashes="[0.7 1.9] 0")
        sh.flush()
        for ch in ich:
            vals = [p[0] for p in ch["pts"]]
            if ch["horiz"]: sh.hchain(vals, sh.Y(ch["pos"]), values=[""] * (len(vals) - 1))
            else: sh.vchain(vals, sh.X(ch["pos"]), values=[""] * (len(vals) - 1))
        sh.flush()

    # ---------------- γραμμές διαστάσεων μελετητή (με λοξές παύλες αντί για βέλη)
    for d in dims:
        if d.get("slant"):
            ax, ay, bx_, by_ = sh.X(d["x0"]), sh.Y(d["y0"]), sh.X(d["x1"]), sh.Y(d["y1"])
            sh.oline(ax, ay, bx_, by_, 0.35)
            for px, py in ((ax, ay), (bx_, by_)): sh.tick(px, py)
        elif d["dir"] == "H": sh.hchain([d["x0"], d["x1"]], sh.Y(d["y0"]), values=[""])
        else: sh.vchain([d["y0"], d["y1"]], sh.X(d["x0"]), values=[""])
    sh.flush()

    # ---------------- κείμενα
    pl = Placer(sh, G, dims, extra=[((ch["pts"][0][0], ch["pos"]), (ch["pts"][-1][0], ch["pos"])) if ch["horiz"] else ((ch["pos"], ch["pts"][0][0]), (ch["pos"], ch["pts"][-1][0])) for ch in ich])
    def orig_rect(t, text=None, size=None):
        vert = (t["dir"] == (0.0, -1.0)); sz = (size or t.get("size", 7.9)) * K
        w = FONT_R.text_length(text or t["text"], fontsize=sz)
        return Placer.rect(sh.X(t["cx"]), sh.Y(t["cy"]), w, sz, vert)
    def straight(t): return t["dir"] in ((1.0, 0.0), (0.0, -1.0))
    for t in T:
        if t["kind"] in ("col", "beam", "ez", "level", "other") and inbb(t) and straight(t): pl.pending[id(t)] = orig_rect(t)
    for i, c in enumerate(G["circles"]):          # οι κύκλοι των πλακών μπαίνουν αργότερα – κρατούν τη θέση τους
        rr = max(4.1 * MM * min(1.0, 0.72 + 0.28 * K), 12.5 * K); pl.pending[("circ", i)] = (sh.X(c["cx"]) - rr, sh.Y(c["cy"]) - rr, sh.X(c["cx"]) + rr, sh.Y(c["cy"]) + rr)
    # ---------------- οπές 20 × 20 και shaft Η/Μ του τεύχους αποχετεύσεων – ΚΑΘΑΡΕΣ διαστάσεις (R04): κάθε απόσταση = γραμμή διάστασης με
    # παύλες από την παρειά σκυροδέματος ως την ακμή του κουτιού, τιμή με μονάδα πάνω σε λευκό φόντο· αν δεν χωρά ανάμεσα, η γραμμή
    # προεκτείνεται έξω από την παρειά αναφοράς και η τιμή γράφεται εκεί. Μπαίνουν ΠΡΙΝ από τα υπόλοιπα κείμενα (εκείνα τις αποφεύγουν).
    HSZ = 7.4
    def hole_dim(ax, ay, bx_, by_, tx_, color=HOLEC):
        A = sh.P(ax, ay); B = sh.P(bx_, by_); horiz = abs(A.y - B.y) < 0.5
        w = FONT_B.text_length(tx_, fontsize=HSZ); L = abs(B.x - A.x) if horiz else abs(B.y - A.y)
        sh.oline(A.x, A.y, B.x, B.y, 0.55, color)
        for q in (A, B): sh.tick(q.x, q.y, color)
        pl.rects.append((min(A.x, B.x) - 1.6, min(A.y, B.y) - 1.6, max(A.x, B.x) + 1.6, max(A.y, B.y) + 1.6))
        fits = L >= w + 6
        if not fits and not horiz:                     # κοντή κατακόρυφη: οριζόντια τιμή δίπλα στη γραμμή, προς την πλευρά του κουτιού (όχι μέσα στο σκυρόδεμα)
            best = None; yc_ = (A.y + B.y) / 2 + (3.0 if B.y > A.y else -3.0)
            for sd in (1, -1):
                cx = A.x + sd * (w / 2 + 4.5); r = Placer.rect(cx, yc_, w, HSZ, False); n = pl.clashes(r)
                if best is None or n < best[0]: best = (n, cx, r)
            otext_c(sh, best[1], yc_, tx_, HSZ, bold=True, color=color, mask=True); r = best[2]; pl.rects.append((r[0] - 2, r[1] - 2, r[2] + 2, r[3] + 2)); return
        off = HSZ * 0.37 + 2.0; best = None
        if not fits:                                   # κοντή: προέκταση της γραμμής έξω από την παρειά αναφοράς (ή, αν εκεί δεν χωρά, έξω από το κουτί) και η τιμή εκεί
            sg0 = (-1 if B.x > A.x else 1) if horiz else (-1 if B.y > A.y else 1); ends = ((A, sg0), (B, -sg0))
        else: ends = ((None, 0),)
        for Q, sg in ends:
            if Q is None: E = None; m = pymupdf.Point((A.x + B.x) / 2, (A.y + B.y) / 2)
            else:
                E = pymupdf.Point(Q.x + sg * (w + 8), Q.y) if horiz else pymupdf.Point(Q.x, Q.y + sg * (w + 8)); m = pymupdf.Point((Q.x + E.x) / 2, (Q.y + E.y) / 2)
            for sd in (-1, 1):                         # πάνω / κάτω από τη γραμμή (ή αριστερά / δεξιά): όπου πέφτει σε λιγότερα
                cx, cy = (m.x, m.y + sd * off) if horiz else (m.x + sd * off, m.y)
                r = Placer.rect(cx, cy, w, HSZ, not horiz); n = pl.clashes(r) + (0.5 if Q is B else 0)
                if best is None or n < best[0]: best = (n, cx, cy, r, Q, E)
        n, cx, cy, r, Q, E = best
        if E is not None: sh.oline(Q.x, Q.y, E.x, E.y, 0.55, color)
        otext_c(sh, cx, cy, tx_, HSZ, bold=True, vert=not horiz, color=color, mask=True); pl.rects.append((r[0] - 2, r[1] - 2, r[2] + 2, r[3] + 2))
    for h in D.get("holes", []):
        a = sh.P(h["box"][0], h["box"][1]); b = sh.P(h["box"][2], h["box"][3]); c = sh.P(h["x"], h["y"])
        for ax, ay, bx_, by_, tx_ in h["links"]:       # προέκταση της ακμής του κουτιού ως τη γραμμή διάστασης όταν αυτή περνά έξω από το κουτί
            if abs(ay - by_) < 0.01 and not (h["box"][1] <= ay <= h["box"][3]): sh.sline(bx_, h["box"][1] if ay < h["box"][1] else h["box"][3], bx_, ay, w=0.3, color=HOLEC, dashes="[1.2 1.0] 0")
            if abs(ax - bx_) < 0.01 and not (h["box"][0] <= ax <= h["box"][2]): sh.sline(h["box"][0] if ax < h["box"][0] else h["box"][2], by_, ax, by_, w=0.3, color=HOLEC, dashes="[1.2 1.0] 0")
        sh.orect(a.x, a.y, b.x, b.y, 1.1, HOLEC, fill=(1, 1, 1)); sh.oline(a.x, a.y, b.x, b.y, 0.3, HOLEC); sh.oline(a.x, b.y, b.x, a.y, 0.3, HOLEC)
        sh.ocircle(c.x, c.y, h["r"] * K, 0, HOLEC, HOLEC)
        pl.rects.append((a.x - 1.5, a.y - 1.5, b.x + 1.5, b.y + 1.5))
    for e in cfg.get("_hole_extra", []):
        a = sh.P(e["box"][0], e["box"][1]); b = sh.P(e["box"][2], e["box"][3]); c = sh.P(e["x"], e["y"])
        if e["kind"] == "gap": sh.orect(a.x, a.y, b.x, b.y, 0.5, HOLEC, fill=(1.0, 0.90, 0.96)); sh.ocircle(c.x, c.y, 1.4, 0, HOLEC, HOLEC)
        else: sh.orect(a.x, a.y, b.x, b.y, 1.0, HOLEC, fill=(1, 1, 1)); sh.ocircle(c.x, c.y, 2.0, 0, HOLEC, HOLEC)
        pl.rects.append((a.x - 1, a.y - 1, b.x + 1, b.y + 1))
    SHF = cfg.get("_shaft")
    if SHF:
        a = sh.P(SHF["box"][0], SHF["box"][1]); b = sh.P(SHF["box"][2], SHF["box"][3])
        sh.orect(a.x, a.y, b.x, b.y, 1.2, SHAFTC, fill=(1, 1, 1)); sh.oline(a.x, a.y, b.x, b.y, 0.35, SHAFTC); sh.oline(a.x, b.y, b.x, a.y, 0.35, SHAFTC)
        pl.rects.append((a.x - 1.5, a.y - 1.5, b.x + 1.5, b.y + 1.5))
    sh.flush()
    for h in D.get("holes", []):                       # R05: ευθεία της παρειάς αναφοράς (διακεκομμένη) από τη γωνία της κολόνας ως τη γραμμή διάστασης, πάνω από τα κουτιά
        for wx0, wy0, wx1, wy1 in h.get("wits", []):
            sg = 1 if (wy1 > wy0 or wx1 > wx0) else -1; ex, ey = (0.0, sg * 4.0 / K) if abs(wx0 - wx1) < 0.01 else (sg * 4.0 / K, 0.0)
            sh.sline(wx0, wy0, wx1 + ex, wy1 + ey, w=0.45, color=HOLEC, dashes="[3.0 1.6] 0")
    sh.flush()
    for h in D.get("holes", []):
        for ax, ay, bx_, by_, tx_ in h["links"]: hole_dim(ax, ay, bx_, by_, tx_)
    if SHF:                                            # αλυσίδα Κ3 | shaft | Κ4 βόρεια του ανοίγματος + βάθος στα δεξιά
        xs = SHF["xs"]; yc = SHF["ych"]
        for xq in xs: sh.sline(xq, SHF["yb"] if xq in (xs[0], xs[3]) else SHF["box"][1], xq, yc, w=0.3, color=SHAFTC, dashes="[1.2 1.0] 0")
        A = sh.P(xs[0], yc); B = sh.P(xs[3], yc); sh.oline(A.x, A.y, B.x, B.y, 0.55, SHAFTC)
        for xq in xs: sh.tick(sh.X(xq), sh.Y(yc), SHAFTC)
        for (xa, xb), tx_ in zip(zip(xs[:-1], xs[1:]), SHF["vals"]):
            w = FONT_B.text_length(tx_, fontsize=HSZ); cx = (sh.X(xa) + sh.X(xb)) / 2; cy = sh.Y(yc) - HSZ * 0.37 - 2.0
            otext_c(sh, cx, cy, tx_, HSZ, bold=True, color=SHAFTC, mask=True); pl.rects.append(Placer.rect(cx, cy, w, HSZ, False))
    def early_label(s_, x_src, y_src, color, bx_=None):
        fs = SZ["hole"][0]; w_ = FONT_B.text_length(s_, fontsize=fs); cx0, cy0 = sh.X(x_src) + 5 + w_ / 2, sh.Y(y_src)
        if bx_ is not None:                            # R05: δοκιμή θέσεων γύρω από το κουτί (δεξιά, δεξιά-πάνω / κάτω, αριστερά, αριστερά-πάνω / κάτω, πάνω, κάτω) – η πρώτη ελεύθερη
            xl, yt, xr, yb = sh.X(bx_[0]), sh.Y(bx_[1]), sh.X(bx_[2]), sh.Y(bx_[3]); ym = (yt + yb) / 2; dv = fs * 0.5 + 4
            for cx, cy in ((xr + 5 + w_ / 2, ym), (xr + 5 + w_ / 2, yt - dv), (xr + 5 + w_ / 2, yb + dv), (xl - 5 - w_ / 2, ym), (xl - 5 - w_ / 2, yt - dv),
                           (xl - 5 - w_ / 2, yb + dv), ((xl + xr) / 2, yt - dv - 3), ((xl + xr) / 2, yb + dv + 3), (xr + 5 + w_ / 2, yt - dv - 9), (xl - 5 - w_ / 2, yt - dv - 9)):
                if pl.clashes(Placer.rect(cx, cy, w_, fs, False)) == 0: cx0, cy0 = cx, cy; break
        s2, x2, y2, w2, n2 = pl.place(cx0, cy0, s_, "hole", False, True, nudge="any")
        otext_c(sh, x2, y2, s_, s2, bold=True, color=color, mask=True)
    for h in D.get("holes", []) + cfg.get("_hole_extra", []):
        early_label(h["name"] + (" " + h["what"].split(" –")[0] if h.get("what") else " – κενό, καμία οπή" if h.get("kind") == "gap" else ""), h["box"][2], (h["box"][1] + h["box"][3]) / 2, HOLEC, bx_=h["box"])
    if SHF:
        s_ = "S1 SHAFT Η/Μ – άνοιγμα 90 × 15 cm"; w_ = FONT_B.text_length(s_, fontsize=SZ["hole"][0])
        early_label(s_, (SHF["box"][0] + SHF["box"][2]) / 2 - (5 + w_ / 2) / K, SHF["ych"] - 13 / K, SHAFTC)
    sh.flush()
    dtexts = []
    for d in dims:
        t = dict(cx=d["tx"], cy=d["ty"], dir=(1.0, 0.0) if d["dir"] == "H" else (0.0, -1.0), text=d["value"], size=7.9)
        dtexts.append(t); pl.pending[id(t)] = orig_rect(t)
    def P(t, kind, text=None, bold=False, color=BLACK, mask=True, anchor=None, skip=None, sizes=None, nudge=None):
        vert = (t["dir"] == (0.0, -1.0))
        s, x, y, w, n = pl.place(sh.X(t["cx"]), sh.Y(t["cy"]), text or t["text"], kind, vert, bold, anchor, skip, sizes, own=id(t), nudge=nudge)
        otext_c(sh, x, y, text or t["text"], s, bold=bold, vert=vert, color=color, mask=mask)
        if n: log.append("CLASH %d |%s| at src (%.0f,%.0f)" % (n, text or t["text"], t["cx"], t["cy"]))
        return s, x, y, w
    def georgia(t): return any("Georgia" in f for f in t["fonts"])
    def rot_of(t): return -math.degrees(math.atan2(t["dir"][1], t["dir"][0]))

    # 1. υποστυλώματα
    for t in T:
        if t["kind"] == "col" and inbb(t): P(t, "col", bold=True, mask=False, nudge="any")
    # 2. στάθμες
    for t in T:
        if t["kind"] != "level" or not inbb(t): continue
        blue = t["color"] != 0
        if not straight(t): otext_rot(sh, sh.X(t["cx"]), sh.Y(t["cy"]), t["text"], 8.0, rot_of(t), color=BLUE if blue else BLACK); continue
        if blue or not georgia(t) or t["dir"] != (1.0, 0.0):
            s_, x_, y_, w_ = P(t, "level", bold=True, color=BLUE if blue else BLACK, mask=not blue, sizes=(8.4, 6.6) if blue else None)
            if georgia(t) and not blue:          # κατακόρυφη στάθμη με σύμβολο: το σύμβολο κάτω από την αρχή του κειμένου
                level_symbol(sh, pymupdf.Point(x_, y_ + w_ / 2 + 2.0 * MM + 2.2), pl)
        else:
            r = 2.0 * MM
            w0 = FONT_B.text_length(t["text"], fontsize=SZ["level"][0])
            cx = t["x0"] + (w0 / 2 + r) / K
            s_, x_, y_, w_, n_ = pl.place(sh.X(cx), sh.Y(t["cy"]), t["text"], "level", False, True, own=id(t))
            otext_c(sh, x_, y_, t["text"], s_, bold=True, mask=True)
            level_symbol(sh, pymupdf.Point(x_ - w_ / 2 - r - 2.2, y_), pl)
    # 3. τιμές διαστάσεων
    blank = cfg.get("inner_blank", []); blank_cal = (calibrate(G) or (0, 0)) if blank else (0, 0)      # τμήματα εσωτερικής αλυσίδας χωρίς τιμή: (οριζόντια;, από m, έως m) στο κοινό σύστημα
    nd = pl.n_struct
    for i, d in enumerate(dims):
        horiz = d["dir"] == "H"; t = dtexts[i]
        h0 = 7.9 * K * 0.74
        if horiz: an = (0, 1 if d["ty"] < d["y0"] else -1, h0)       # κείμενο πάνω από τη γραμμή: σταθερή η κάτω πλευρά
        else: an = (1 if d["tx"] < d["x0"] else -1, 0, h0)
        P(t, "dim", anchor=an, skip=nd + i, nudge="along")
    for ci, ch in enumerate(ich):
        vals = [p[0] for p in ch["pts"]]
        for a, b in zip(vals[:-1], vals[1:]):
            s_ = sh.fmt((b - a) / S); sz = 7.6
            if any(hz == ch["horiz"] and abs(a - (blank_cal[0 if hz else 1] + m0 * S)) < 2 and abs(b - (blank_cal[0 if hz else 1] + m1 * S)) < 2 for hz, m0, m1 in blank): continue
            if ch["horiz"]:
                t = dict(cx=(a + b) / 2, cy=ch["pos"] - (1.9 + sz * 0.37) / K, dir=(1.0, 0.0), text=s_)
            else:
                t = dict(cx=ch["pos"] - (1.9 + sz * 0.37) / K, cy=(a + b) / 2, dir=(0.0, -1.0), text=s_)
            P(t, "dim", sizes=(7.6, 6.0), skip=pl.n_dims + ci, nudge="along")
    for d in unres:
        t = dict(cx=d["tx"], cy=d["ty"], dir=(1.0, 0.0) if d["dir"] == "H" else (0.0, -1.0), text=d["value"])
        if not inbb(t) or cfg.get("hide_unresolved"): log.append("hidden unresolved %s (%.0f,%.0f)" % (d["value"], d["tx"], d["ty"])); continue
        P(t, "dim"); log.append("UNRESOLVED DIM %s at (%.0f,%.0f)" % (d["value"], d["tx"], d["ty"]))
    # 4. πλάκες: κύκλος + Π + h
    slabs = [t for t in T if t["kind"] == "slab" and inbb(t)]; hs = [t for t in T if t["kind"] == "h" and inbb(t)]
    for t in slabs:
        cand = [h for h in hs if abs(h["cx"] - t["cx"]) < 8 and 4 < h["cy"] - t["cy"] < 16]
        h = min(cand, key=lambda q: abs(q["cy"] - t["cy"])) if cand else None
        circ = [c for c in G["circles"] if math.hypot(c["cx"] - t["cx"], c["cy"] - (t["cy"] + 5)) < 9]
        cx, cy = (circ[0]["cx"], circ[0]["cy"]) if circ else (t["cx"], t["cy"] + 5.5)
        c = sh.P(cx, cy); r = max(4.1 * MM * min(1.0, 0.72 + 0.28 * K), 12.5 * K)
        sh.ocircle(c.x, c.y, r, 0.45, BLACK, (1, 1, 1)); sh.oline(c.x - r, c.y, c.x + r, c.y, 0.35)
        otext_c(sh, c.x, c.y - r * 0.42, t["text"], 7.8 if K > 0.8 else 7.2, bold=True)
        if h: otext_c(sh, c.x, c.y + r * 0.45, h["text"].replace(" ", ""), 6.8 if K > 0.8 else 6.2)
        pl.rects.append((c.x - r, c.y - r, c.x + r, c.y + r))
    # 5. δοκοί, Ε.Ζ.
    for t in T:
        if t["kind"] in ("beam", "ez") and inbb(t):
            txt = t["text"] + ("  L=%s" % sh.fmt(t["L"]) if t.get("L") else "")
            if not straight(t): otext_rot(sh, sh.X(t["cx"]), sh.Y(t["cy"]), txt, SZ[t["kind"]][1] + 0.6, rot_of(t))
            else: P(t, t["kind"], text=txt, bold=(t["kind"] == "beam"), mask=True, nudge="along")
    # 5β. ετικέτες γεμίσματος / μπαζώματος και οπών
    for f in D.get("fills", []):
        if not f.get("label"): continue
        if f["kind"] == "hatch" and f["poly"].area < cfg.get("fill_label_min_m2", 2.0) * S * S: continue
        rp = f.get("at") or (f["poly"].representative_point().x, f["poly"].representative_point().y)
        lines_ = f["label"] if isinstance(f["label"], list) else [f["label"]]
        for i, ln in enumerate(lines_):
            t = dict(cx=rp[0], cy=rp[1] + (i - (len(lines_) - 1) / 2) * 9.5 / K, dir=(1.0, 0.0), text=ln)
            P(t, "fill", bold=True, color=(0.40, 0.22, 0.0), nudge="any")
    # 6. λοιπά (σημειώσεις μελετητή), τίτλοι ενθέτων, σημάδια τομών
    for t in T:
        if t["kind"] == "other" and inbb(t):
            if not straight(t): otext_rot(sh, sh.X(t["cx"]), sh.Y(t["cy"]), t["text"], 7.0, rot_of(t), color=BLUE if t["color"] != 0 else BLACK)
            else: P(t, "other", color=BLUE if t["color"] != 0 else BLACK, nudge="along")
            log.append("OTHER |%s| (%.0f,%.0f) %s" % (t["text"], t["cx"], t["cy"], t["fonts"]))
        elif t["kind"] == "cutmark" and inbb(t) and cfg.get("cuts"):
            P(t, "cutmark", bold=True, mask=False)
    # ---------------- σταθερό σημείο (γωνία υποστυλώματος)
    if datum:
        c = sh.P(*datum); r = 3.0
        sh.ocircle(c.x, c.y, r + 1.6, 0.9, RED, None); sh.ocircle(c.x, c.y, 1.3, 0, RED, RED)
        sh.oline(c.x - r - 4.5, c.y, c.x + r + 4.5, c.y, 0.5, RED); sh.oline(c.x, c.y - r - 4.5, c.x, c.y + r + 4.5, 0.5, RED)
        sh.otext(c.x - r - 3, c.y - r - 3.5, "Σ.Σ.", size=7.4, bold=True, color=RED, align="right", mask=True)
        for sd in sides:
            vals = [v for v, w in FC[sd]]
            if sd in ("top", "bottom"): draw_cum(sh, vals, rowpos[sd], True, +1 if sd == "top" else -1, datum[0])
            else: draw_cum(sh, vals, rowpos[sd], False, +1 if sd == "left" else -1, datum[1])
    # ---------------- αλυσίδες παρειών υποστυλωμάτων (εξωτερική σειρά κάθε πλευράς)
    for sd in sides:
        vals = [v for v, w in FC[sd]]
        if sd == "top": sh.hchain(vals, sh.Y(rowpos[sd]), text_side=-1, size=7.0, mask=True)
        elif sd == "bottom": sh.hchain(vals, sh.Y(rowpos[sd]), text_side=+1, size=7.0, mask=True)
        elif sd == "left": sh.vchain(vals, sh.X(rowpos[sd]), text_side=-1, size=7.0, mask=True)
        else: sh.vchain(vals, sh.X(rowpos[sd]), text_side=+1, size=7.0, mask=True)
    sh.flush()
    return log


def section_layout(D):
    """Τομή μετώπης: περίγραμμα σκυροδέματος + στάθμες. Επιστρέφει (xmin, xmax(=κομμένο άκρο), ymin, ymax, στάθμες[(y, κείμενο, πλευρά)])."""
    G, T = D["G"], D["T"]
    ol = [l for l in G["lines"] if l["w"] == 0.85]
    if not ol: return None
    xs = [v for l in ol for v in (l["x0"], l["x1"])]; ys = [v for l in ol for v in (l["y0"], l["y1"])]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    hy = sorted(set(round(l["y0"], 1) for l in ol if abs(l["y0"] - l["y1"]) < 0.3))       # στάθμες οριζόντιων ακμών του περιγράμματος
    tri = [l for l in G["lines"] if l.get("tri")]
    levels = []
    for t in T:
        if t["kind"] != "level": continue
        tl = [l for l in tri if t["x0"] - 16 <= l["x0"] <= t["x1"] + 16 and -2 <= l["y0"] - t["y1"] <= 12]
        y = max(l["y0"] for l in tl) if tl else t["y1"] + 8
        if hy: y = min(hy, key=lambda v: abs(v - y)) if min(abs(v - y) for v in hy) < 9 else y     # κούμπωμα στην ακμή που δείχνει
        levels.append((y, t["text"], "R" if t["cx"] > (xmin + xmax) / 2 else "L"))
    return xmin, xmax, ymin, ymax, levels


def section_size(D, k):
    lay = section_layout(D)
    if lay is None: return 0, 0, 0
    xmin, xmax, ymin, ymax, levels = lay
    wl = max([FONT_B.text_length(t, fontsize=8.2) for y, t, s in levels] + [0]) + 8
    return wl + (xmax - xmin) * k + 7, (ymax - ymin) * k + 26, wl


def section_fit_k(D, width, kmax=0.5):
    lay = section_layout(D)
    if lay is None: return kmax
    xmin, xmax, ymin, ymax, levels = lay
    wl = section_size(D, 1.0)[2]
    return max(0.2, min(kmax, (width - wl - 7) / max(xmax - xmin, 1)))


def draw_section(sh, D, log):
    """σχεδίαση τομής στη θέση (sh.OX, sh.OY) = πάνω-αριστερή γωνία του ενθέτου. Όλες οι στάθμες γράφονται αριστερά."""
    lay = section_layout(D)
    if lay is None: log.append("SECTION: no outline"); return log
    G, k = D["G"], sh.K
    xmin, xmax, ymin, ymax, levels = lay
    w, h, wl = section_size(D, k)
    ox, oy = sh.OX + wl, sh.OY + 18                      # αρχή του περιγράμματος στο χαρτί
    def PX(x): return ox + (x - xmin) * k
    def PY(y): return oy + (y - ymin) * k
    ol = [l for l in G["lines"] if l["w"] == 0.85]
    cuts = [(xmax if sd == "R" else xmin, sd) for sd in G.get("cut_sides", ["R"])]
    def ends_at(xe): return sorted([(l["x0"], l["y0"]) for l in ol if abs(l["x0"] - xe) < 1.0] + [(l["x1"], l["y1"]) for l in ol if abs(l["x1"] - xe) < 1.0], key=lambda p: p[1])
    try:                                                 # γέμισμα σκυροδέματος: κλείσιμο του περιγράμματος στα κομμένα άκρα
        from shapely.ops import polygonize, unary_union
        segs = [LineString([(round(l["x0"], 0), round(l["y0"], 0)), (round(l["x1"], 0), round(l["y1"], 0))]) for l in ol]
        for xe, sd in cuts:
            ends = ends_at(xe)
            if len(ends) >= 2: segs.append(LineString([(round(ends[0][0], 0), round(ends[0][1], 0)), (round(ends[-1][0], 0), round(ends[-1][1], 0))]))
        for poly in polygonize(unary_union(segs)):
            sh.shape.draw_polyline([pymupdf.Point(PX(a_), PY(b_)) for a_, b_ in poly.exterior.coords]); sh.shape.finish(width=0, color=None, fill=COLFILL)
    except Exception as e: log.append("SECTION fill: %s" % e)
    for l in ol: sh.oline(PX(l["x0"]), PY(l["y0"]), PX(l["x1"]), PY(l["y1"]), 1.0)
    for xe, sd in cuts:                                  # σημάδι κοπής στα κομμένα άκρα
        ce = [p[1] for p in ends_at(xe)]
        if len(ce) < 2: continue
        xc = PX(xe) + (2.2 if sd == "R" else -2.2); y0, y1 = PY(ce[0]) - 5, PY(ce[-1]) + 5; ym = (y0 + y1) / 2
        sh.shape.draw_polyline([pymupdf.Point(xc, y0), pymupdf.Point(xc, ym - 2.5), pymupdf.Point(xc - 2.5, ym - 1), pymupdf.Point(xc + 2.5, ym + 1), pymupdf.Point(xc, ym + 2.5), pymupdf.Point(xc, y1)])
        sh.shape.finish(width=0.3, color=BLACK)
    sh.flush()
    for d in D["dims"]:                                  # πλάτη (διαστάσεις μελετητή πάνω από τις μετώπες)
        if d["dir"] != "H": continue
        ya = PY(ymin) - 5.5
        sh.oline(PX(d["x0"]), ya, PX(d["x1"]), ya, 0.3)
        for xx in (d["x0"], d["x1"]):
            sh.oline(PX(xx) - 1.6, ya + 1.6, PX(xx) + 1.6, ya - 1.6, 0.5); sh.oline(PX(xx), ya - 1.5, PX(xx), PY(ymin) - 1, 0.2)
        otext_c(sh, (PX(d["x0"]) + PX(d["x1"])) / 2, ya - 4.2, d["value"], 7.0)
    # στάθμες: μία ετικέτα ανά στάθμη, αριστερά· διακεκομμένη γραμμή ως την πιο δεξιά οριζόντια ακμή αυτής της στάθμης
    seen = {}
    for y, txt, side in sorted(levels):
        if txt in seen and abs(seen[txt] - y) < 3: continue
        seen[txt] = y
    used = []
    for txt, y in sorted(seen.items(), key=lambda kv: kv[1]):
        yy = PY(y)
        while any(abs(yy - u) < 7.8 for u in used): yy += 1.0
        used.append(yy)
        hs = [l for l in ol if abs(l["y0"] - l["y1"]) < 0.3 and abs(l["y0"] - y) < 1.5]
        xr = max([max(l["x0"], l["x1"]) for l in hs] + [xmin])
        xl = min([min(l["x0"], l["x1"]) for l in hs] + [xmin])
        if xl > xmin + 1: sh.oline(PX(xmin) - 5, PY(y), PX(xl), PY(y), 0.3, (0.25, 0.25, 0.25), dashes="[1.4 1.4] 0")
        if any(sd == "L" for xe, sd in cuts): sh.oline(PX(xmin) - 5.5, PY(y), PX(xmin) - 4.6, PY(y), 0.3)
        sh.oline(PX(xmin) - 5, PY(y), PX(xmin) - 0.8, PY(y), 0.4)
        if abs(yy - PY(y)) > 0.5: sh.oline(PX(xmin) - 7, yy, PX(xmin) - 5, PY(y), 0.3)
        chg = txt in D["cfg"].get("changed", [])          # στάθμη που άλλαξε με εντολή εργοδότη (cfg["sec_retext"]) – κόκκινη, υπογραμμισμένη
        sh.otext(PX(xmin) - 7.5, yy + 2.9, txt, size=8.2, bold=True, align="right", color=RED if chg else BLACK)
        if chg: sh.oline(PX(xmin) - 7.5 - FONT_B.text_length(txt, fontsize=8.2), yy + 4.4, PX(xmin) - 7.5, yy + 4.4, 0.7, RED)
    sh.flush()
    return log


def level_symbol(sh, c, pl=None, r=2.0 * MM):
    sh.ocircle(c.x, c.y, r, 0.4, BLACK, (1, 1, 1))
    for a0 in (90, 270):
        pts = [c] + [pymupdf.Point(c.x + r * math.cos(math.radians(a0 + k)), c.y - r * math.sin(math.radians(a0 + k))) for k in range(0, 91, 10)]
        sh.shape.draw_polyline(pts + [c]); sh.shape.finish(width=0, color=BLACK, fill=BLACK)
    sh.oline(c.x - r * 1.5, c.y, c.x + r * 1.5, c.y, 0.35); sh.oline(c.x, c.y - r * 1.5, c.x, c.y + r * 1.5, 0.35)
    if pl is not None: pl.rects.append((c.x - r, c.y - r, c.x + r, c.y + r))


def build(cfg, out_pdf=None, date=None):
    global A3W, A3H
    A3W, A3H = cfg.get("paper_mm", (420.0, 297.0))          # R03: και Α2 (594 × 420) – ο Γιάννης: «μεγάλωσε το φύλλο αν θες, δεν χωράνε»
    doc = pymupdf.open(cfg["pdf"]); page = doc[0]
    DR = page.get_drawings()
    D = prep(page, DR, cfg)
    G = D["G"]; bb0 = D["bb"]
    GC, FC, sides, inner, datum = plan_chains(cfg, D)
    cover_left = cover_dims(D, FC, sides, inner, D["log0"]) if cfg.get("cover", True) else []
    for tp, v in cover_left: D["log0"].append("ΑΚΑΛΥΠΤΗ ΑΚΜΗ %s %.0f" % (tp, v))
    ROW_MM = 12.6 if datum else 8.6; TW = cfg.get("title_w", 46.0)
    insets = list(cfg.get("insets", []))
    if cfg.get("sections"):
        for name, reg in X.find_sections(page):
            insets.append(dict(region=reg, section=True, src_scale=2.5, k=cfg.get("sec_k", 0.4), title="ΤΟΜΗ " + name, pad=4,
                               retext=cfg.get("sec_retext", {}).get(name, []), changed=[r[1] for r in cfg.get("sec_retext", {}).get(name, [])]))
    STRIP = cfg.get("strip_w", 0.0)
    def grow(bb_, sc):
        rw = ROW_MM * MM * sc / 50.0          # πλάτος σειράς αλυσίδας σε pt πηγής
        return (bb_[0] - (rw if "left" in sides else 0), bb_[1] - (rw if "top" in sides else 0),
                bb_[2] + (rw if "right" in sides else 0), bb_[3] + (rw if "bottom" in sides else 0))
    lay = None
    for sc in ([cfg["scale"]] if cfg.get("scale") else SCALES):
        try: lay = choose_layout(grow(bb0, sc), sc, cfg.get("layout"), title_w=TW + STRIP); break
        except IndexError: continue
    if lay is None: raise RuntimeError("δεν χωράει σε Α3")
    scale, layout, aw, ah = lay
    K = 50.0 / scale; bb = grow(bb0, scale)
    cw, ch = (bb[2] - bb[0]) * K / MM, (bb[3] - bb[1]) * K / MM
    margin = 6.0
    ox = margin + (aw - cw) / 2; oy = margin + (ah - ch) / 2
    sh = lib.Sheet(G, [], scale=scale, ox_mm=ox, oy_mm=oy, sx0=bb[0], sy0=bb[1], page_w=A3W, page_h=A3H)
    D["bb_out"] = bb
    log = draw(sh, D, bb0, FC, sides, datum=datum, inner=inner)
    for d in D["dropped"]: log.append("DROPPED DIM %s %s at (%.0f,%.0f)" % (d["value"], d["dir"], d["tx"], d["ty"]))
    if cfg.get("datum") and not datum: log.append("NO DATUM FOUND")
    info = dict(scale=scale, layout=layout, bb=bb, K=K, log=log, G=G, T=D["T"], dims=D["dims"], FC=FC, aw=aw, ah=ah, margin=margin, TW=TW, datum=datum, inner=inner,
                holes=D.get("holes", []), fills=D.get("fills", []))
    title_block(sh, cfg, info, date)
    # ---------------- ένθετα (λεπτομέρειες / τομές / φυτευτά) στον ελεύθερο χώρο της πινακίδας ή σε ρητή θέση
    main_tr = (sh.OX, sh.OY, sh.SX0, sh.SY0, sh.K)
    free = list(info.get("free", (0, 0, 0, 0)))
    if STRIP:
        PW, PH = A3W * MM, A3H * MM
        free = [PW - (margin + TW + STRIP) * MM, margin * MM + 4, PW - (margin + TW + 2) * MM, PH - margin * MM]
    preps = [prep(page, DR, ins, S_loc=S * ins.get("src_scale", 1.0)) for ins in insets]   # τομές 1:20 στο αρχικό: 2.5 × 56.69 pt/m
    secs = [(ins, Di) for ins, Di in zip(insets, preps) if ins.get("section")]
    if secs and STRIP:
        for ins, Di in secs: ins["k"] = section_fit_k(Di, free[2] - free[0])       # σκαριφήματα: όσο μεγαλύτερα χωράνε στη λωρίδα
        while sum(section_size(Di, ins["k"])[1] + 21 for ins, Di in secs) > free[3] - free[1] - 22:
            for ins, Di in secs: ins["k"] *= 0.95
        sh.otext((free[0] + free[2]) / 2, free[1] + 6, "ΤΟΜΕΣ ΜΕΤΩΠΩΝ", size=7.2, bold=True, align="center")
        sh.otext((free[0] + free[2]) / 2, free[1] + 14, "(σκαρίφημα χωρίς κλίμακα)", size=5.8, align="center"); free[1] += 20
    for ins, Di in zip(insets, preps):
        bi = Di["bb"]; Ki = ins.get("k", K)               # συντελεστής pt πηγής -> pt χαρτιού
        if ins.get("section"): w, h, _ = section_size(Di, Ki)
        else: w, h = (bi[2] - bi[0]) * Ki, (bi[3] - bi[1]) * Ki
        th = 11.0 if ins.get("title") else 0
        if ins.get("at"): x0, y0 = ins["at"][0] * MM, ins["at"][1] * MM
        else:
            x0 = free[0] + max(0, ((free[2] - free[0]) - w) / 2); y0 = free[1] + 4 + th
            free[1] = y0 + h + 6
        if ins.get("title"):
            for i, ln in enumerate(ins["title"] if isinstance(ins["title"], list) else [ins["title"]]):
                sh.otext((free[0] + free[2]) / 2 if not ins.get("at") else x0, y0 - th + 7 + i * 8, ln, size=7.4, bold=True, align="center" if not ins.get("at") else "left")
        sh.OX, sh.OY, sh.SX0, sh.SY0, sh.K = x0, y0, bi[0], bi[1], Ki
        Di["bb_out"] = bi
        log += ["   [inset] " + l for l in draw(sh, Di, bi)]
        if not ins.get("at") and free[1] > free[3]: log.append("INSET OVERFLOW %s" % (ins.get("title"),))
        if not ins.get("at") and w > free[2] - free[0] + 1: log.append("INSET TOO WIDE %s %.0f > %.0f" % (ins.get("title"), w, free[2] - free[0]))
    sh.OX, sh.OY, sh.SX0, sh.SY0, sh.K = main_tr
    sh.G = G
    return sh, info


def _wrap(text, size, width, bold=False):
    f = FONT_B if bold else FONT_R; out = []; cur = ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.text_length(t, fontsize=size) <= width or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def levels_table(cfg, T):
    """Πάτοι καλουπιών από τη στάθμη άνω πλάκας: πλάκα h → στάθμη − h · δοκός b/h → στάθμη − h (το ύψος δοκού μαζί με την πλάκα)."""
    top = cfg.get("level"); low = cfg.get("level_below")
    if top is None: return None
    hs = sorted(set(int(re.sub(r"\D", "", t["text"])) for t in T if t["kind"] == "h"))
    bh = set()
    for t in T:
        if t["kind"] in ("beam", "ez") and "Ανεστρ" not in t["text"]:
            m = re.search(r"(\d+)/(\d+)", t["text"])
            if m and t["kind"] == "beam" and re.match("^Δ ?[0-9]+[.][0-9]", t["text"]) and t["color"] == 0: bh.add(int(m.group(2)))
    def lv(v): return ("%+.2f" % v).replace(".", ",")
    rows = []
    for h in hs: rows.append(("Πλάκα h=%d" % h, lv(top - h / 100.0), ("%.2f" % (top - h / 100.0 - low)).replace(".", ",") if low is not None else None))
    for h in sorted(bh): rows.append(("Δοκός ύψους %d" % h, lv(top - h / 100.0), ("%.2f" % (top - h / 100.0 - low)).replace(".", ",") if low is not None else None))
    return rows


class _Scaled:
    """Σχεδίαση της πινακίδας μεγεθυμένης κατά F γύρω από την πάνω-αριστερή γωνία της (Α2: ίδια διάταξη, μεγαλύτερα γράμματα)."""
    def __init__(self, sh, x0, y0, F): self.sh, self.x0, self.y0, self.F = sh, x0, y0, F
    def _x(self, x): return self.x0 + (x - self.x0) * self.F
    def _y(self, y): return self.y0 + (y - self.y0) * self.F
    def otext(self, x, y, t, size=7, **kw): self.sh.otext(self._x(x), self._y(y), t, size=size * self.F, **kw)
    def oline(self, x0, y0, x1, y1, w=0.5, *a, **kw): self.sh.oline(self._x(x0), self._y(y0), self._x(x1), self._y(y1), w, *a, **kw)
    def orect(self, x0, y0, x1, y1, w=0.5, *a, **kw): self.sh.orect(self._x(x0), self._y(y0), self._x(x1), self._y(y1), w, *a, **kw)
    def ocircle(self, x, y, r, *a, **kw): self.sh.ocircle(self._x(x), self._y(y), r * self.F, *a, **kw)
    def flush(self): self.sh.flush()


def title_block(sh, cfg, info, date=None):
    date = date or datetime.date.today().strftime("%d/%m/%Y")
    m = info["margin"] * MM
    PW, PH = A3W * MM, A3H * MM
    sh.orect(m * 0.6, m * 0.6, PW - m * 0.6, PH - m * 0.6, 0.6)
    if info["layout"] == "right":
        x0 = PW - m - info["TW"] * MM; x1 = PW - m; y0 = m; y1 = PH - m
    else:
        x0 = m; x1 = PW - m; y0 = PH - m - 30 * MM; y1 = PH - m
    sh.orect(x0, y0, x1, y1, 0.9)
    pad = 2.4 * MM
    def lab(x, y, s): sh.otext(x, y, s, size=5.6, color=GRAY)
    scale_txt = "1:%d" % info["scale"]
    u = S * info["K"]
    def scalebar(x, y, n):
        for i in range(n): sh.orect(x + i * u, y, x + (i + 1) * u, y + 1.6 * MM, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(n + 1): sh.otext(x + i * u, y + 1.6 * MM + 6.5, str(i), size=5.6, align="center")
        sh.otext(x + n * u + 5, y + 1.6 * MM + 6.5, "m", size=5.6)
    legend = cfg.get("legend") or [
        ("Κ1 30/70", "υποστύλωμα / τοιχείο – διατομή σε cm"),
        ("Δ1.1 30/40", "δοκός – πλάτος / ύψος σε cm (το ύψος ΜΑΖΙ με την πλάκα)"),
        ("Π3  h=15", "πλάκα – πάχος σε cm"),
        ("Ε.Ζ.", "ενισχυμένη ζώνη μέσα στο πάχος της πλάκας (χωρίς καλούπι δοκού)"),
        ("+0,00", "στάθμη άνω επιφάνειας σκυροδέματος (m)"),
        ("μπλε", "φυτευτά στοιχεία και οι στάθμες τους"),
        ("- - -", "κρυφή ακμή / στοιχείο από κάτω"),
    ]
    notes = cfg.get("notes") or []
    rows = levels_table(cfg, info["T"]) if cfg.get("level_table", True) else None
    if info["layout"] == "right":
        # R01 (Γιάννης 10/11/2026: «μάζεψε τις σημειώσεις και γενικά όλο τον πίνακα δεξιά»): στενή στήλη, μικρά γράμματα, μόνο τα απαραίτητα
        TF = cfg.get("title_fs", 1.0); sh_real = sh; rx1, ry1 = x1, y1
        if TF != 1.0:                       # εικονικές συντεταγμένες: όλα παρακάτω σχεδιάζονται × TF γύρω από το (x0, y0)
            sh = _Scaled(sh_real, x0, y0, TF); x1 = x0 + (x1 - x0) / TF; y1 = y0 + (y1 - y0) / TF; u = u / TF
        pad = 1.8 * MM; W = x1 - x0 - 2 * pad; x = x0 + pad; y = y0 + 3.4 * MM; fs = 5.7; lh = 6.7
        def para(txt, bold=False, size=fs, color=BLACK, indent=0):
            nonlocal y
            for ln in _wrap(txt, size, W - indent, bold): sh.otext(x + indent, y, ln, size=size, bold=bold, color=color); y += lh * size / fs
        def rule():
            nonlocal y
            y += 1.0; sh.oline(x0, y, x1, y, 0.4); y += 3.0 * MM
        para("ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓ. ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ – ARKAD Ι.Κ.Ε.", True, 5.6)
        para("Ξυλότυπος εργοταξίου – χωρίς οπλισμούς", False, 5.4, GRAY)
        rule(); y += 9
        nw = FONT_B.text_length(cfg["number"], fontsize=20)
        sh.otext(x1 - pad - nw, y + 6, cfg["number"], size=20, bold=True)
        tsz = 9.0
        while tsz > 6.5 and max(FONT_B.text_length(ln, fontsize=tsz) for ln in cfg["title"]) > W - nw - 3: tsz -= 0.5
        y -= 4
        for ln in cfg["title"]: sh.otext(x, y, ln, size=tsz, bold=True); y += tsz + 1.6
        y += 3
        if cfg.get("level_txt"):
            sh.otext(x, y, "ΣΤΑΘΜΗ ΑΝΩ ΠΛΑΚΑΣ", size=5.0, color=GRAY); y += 10.5
            lsz = 12.0
            while lsz > 8 and FONT_B.text_length(cfg["level_txt"], fontsize=lsz) > W: lsz -= 0.5
            sh.otext(x, y, cfg["level_txt"], size=lsz, bold=True); y += 4
        y += 7.5
        sh.otext(x, y, "ΚΛΙΜΑΚΑ " + scale_txt, size=10.5, bold=True); sh.otext(x1 - pad, y, "%s · 100 %%" % cfg.get("paper", "Α3"), size=5.2, align="right", color=GRAY)
        y += 4; scalebar(x + 1, y, max(1, min(4, int((W - 12) / u)))); y += 1.6 * MM + 9
        rule()
        kw = 31.0
        leg = cfg.get("legend") or [
            ("Κ1 30/70", "υποστύλωμα / τοιχείο (cm)"),
            ("Δ1.1 30/40", "δοκός: πλάτος / ύψος (το ύψος μαζί με την πλάκα)"),
            ("L=3.50", "καθαρό μήκος δοκού, παρειά με παρειά"),
            ("Π3 h=15", "πλάκα – πάχος (cm)"),
            ("+0,30", "στάθμη άνω μπετού (m)"),
            ("μπλε", "τομές επί τόπου / φυτευτά και οι στάθμες τους"),
        ]
        for k, v in leg:
            sh.otext(x, y, k, size=fs, bold=True, color=BLUE if k == "μπλε" else BLACK)
            for ln in _wrap(v, fs, W - kw): sh.otext(x + kw, y, ln, size=fs); y += lh
        kinds = set(f["kind"] for f in info.get("fills", []))
        for kd, v in (("hatch", cfg.get("fill_legend", "γέμισμα (διαγραμμισμένο)")), ("seed", "ΜΠΑΖΩΜΑ («φελιζόλ» του μελετητή) κάτω από πλάκα")):
            if kd in kinds:
                sh.orect(x + 1, y - 5, x + kw - 8, y + 0.6, 0.3, fill=FILLC[kd])
                for ln in _wrap(v, fs, W - kw): sh.otext(x + kw, y, ln, size=fs); y += lh
        if info.get("holes"):
            sh.orect(x + 2, y - 5.6, x + 8.4, y + 0.8, 0.8, HOLEC, fill=(1, 1, 1)); sh.oline(x + 2, y - 5.6, x + 8.4, y + 0.8, 0.3, HOLEC); sh.oline(x + 2, y + 0.8, x + 8.4, y - 5.6, 0.3, HOLEC)
            for ln in _wrap("οπή πλάκας 20 × 20 (αποχέτευση / υδρορροή)", fs, W - kw): sh.otext(x + kw, y, ln, size=fs); y += lh
            if cfg.get("_shaft"):
                sh.orect(x + 1, y - 4.4, x + 12, y - 0.4, 0.8, SHAFTC, fill=(1, 1, 1)); sh.oline(x + 1, y - 4.4, x + 12, y - 0.4, 0.3, SHAFTC); sh.oline(x + 1, y - 0.4, x + 12, y - 4.4, 0.3, SHAFTC)
                for ln in _wrap("άνοιγμα shaft Η/Μ στην πλάκα", fs, W - kw): sh.otext(x + kw, y, ln, size=fs); y += lh
        para("Διαστάσεις σε m, από γωνία / παρειά κολόνας σε γωνία κολόνας." + (" Οι αλυσίδες παρειών μετρήθηκαν από τη γεωμετρία του σχεδίου, οι υπόλοιπες είναι του μελετητή." if info["FC"] else ""))
        rule()
        if rows:
            low = cfg.get("level_below")
            sh.otext(x, y, "ΠΑΤΟΙ ΚΑΛΟΥΠΙΩΝ", size=5.0, color=GRAY); c2, c3 = x + W * 0.52, x + W * 0.80
            sh.otext(c2, y, "στάθμη", size=5.0, color=GRAY)
            if low is not None: sh.otext(c3, y, "ύψος*", size=5.0, color=GRAY)
            y += 7.6
            for a, b, c in rows:
                sh.otext(x, y, a, size=6.2); sh.otext(c2, y, b, size=6.6, bold=True)
                if c: sh.otext(c3, y, c, size=6.6, bold=True)
                y += 7.8
            para(("* από την πλάκα του κάτω ορόφου (%s). " % ("%+.2f" % low).replace(".", ",") if low is not None else "") + "Υπολογισμένα (στάθμη − ύψος)· όχι για ανεστραμμένες δοκούς / φυτευτά.", size=5.2, color=GRAY)
            rule()
        if info.get("holes"):
            sh.otext(x, y, "ΟΠΕΣ ΠΛΑΚΑΣ – ΚΟΥΤΙ 20 × 20 · SHAFT", size=5.0, color=GRAY); y += 6.4
            para("Θέση σε cm ως την ΑΚΜΗ του κουτιού, από παρειές σκυροδέματος.", size=5.2, color=GRAY); y += 1.5
            for h in info["holes"]:
                sh.otext(x, y, h["name"], size=6.2, bold=True, color=HOLEC); sh.otext(x + 15, y, h["what"], size=5.8, bold=True); y += 6.6
                for ln in _wrap(h["pos"], 5.4, W - 4): sh.otext(x + 4, y, ln, size=5.4); y += 6.2
                y += 1.4
            for e in cfg.get("_hole_extra", []):
                sh.otext(x, y, e["name"], size=6.2, bold=True, color=HOLEC)
                for i_, ln in enumerate(_wrap(e["text"] + (" – ΚΑΜΙΑ οπή" if e["kind"] == "gap" else ""), 5.4, W - 15)): sh.otext(x + 15, y, ln, size=5.4); y += 6.2
                y += 1.4
            if cfg.get("_shaft"):
                sh.otext(x, y, "S1", size=6.2, bold=True, color=SHAFTC); sh.otext(x + 15, y, "SHAFT Η/Μ", size=5.8, bold=True); y += 6.6
                for ln in _wrap(cfg["_shaft"]["text"], 5.4, W - 4): sh.otext(x + 4, y, ln, size=5.4); y += 6.2
                y += 1.4
            para("Τεύχος αποχετεύσεων %s, φύλλο %s. Καμία οπή σε δοκό, καμία αναμονή σε στηθαίο." % (cfg.get("_hole_src", ""), cfg.get("_hole_sheet", "")), True, 5.3, HOLEC)
            rule()
        if notes:
            sh.otext(x, y, "ΣΗΜΕΙΩΣΕΙΣ", size=5.0, color=GRAY); y += 7.6
            for n in notes: para("· " + n, size=5.5); y += 0.8
            rule()
        info["title_y_free"] = y
        yb = y1 - 13.5 * MM
        sh.oline(x0, yb, x1, yb, 0.4); y = yb + 3.2 * MM
        para("Βάση: " + cfg["base"], size=5.2); para("Οπλισμοί ΜΟΝΟ από το σχέδιο του μελετητή.", True, 5.2)
        sh.otext(x, y1 - 1.8 * MM, "Έκδοση %s – %s" % (cfg.get("rev", "R00"), date), size=6.0, bold=True)
        info["title_rect"] = (x0, y0, rx1, ry1); info["free"] = (x0, y0 + (info["title_y_free"] - y0) * TF, rx1, y0 + (yb - y0) * TF)
        sh = sh_real
    else:
        cols = [x0, x0 + 78 * MM, x0 + 190 * MM, x0 + 290 * MM, x1]
        for cx in cols[1:-1]: sh.oline(cx, y0, cx, y1, 0.4)
        x = cols[0] + pad; y = y0 + 4.2 * MM
        lab(x, y, "ΣΧΕΔΙΟ ΕΡΓΟΤΑΞΙΟΥ – ΞΥΛΟΤΥΠΟΣ ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ"); y += 13
        nw = FONT_B.text_length(cfg["number"], fontsize=24)
        sh.otext(cols[1] - pad - nw, y1 - 3 * MM, cfg["number"], size=24, bold=True)
        for ln in cfg["title"]: sh.otext(x, y, ln, size=10.5, bold=True); y += 12.5
        if cfg.get("level_txt"): sh.otext(x, y + 2, "Στάθμη: " + cfg["level_txt"], size=9.5, bold=True); y += 12
        sh.otext(x, y1 - 7.6 * MM, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓ. ΒΑΡΒΑΡΑΣ,", size=6.0); sh.otext(x, y1 - 4.9 * MM, "ΑΡΓΥΡΟΥΠΟΛΗ – ARKAD Ι.Κ.Ε.", size=6.0)
        sh.otext(x, y1 - 2.0 * MM, "Έκδοση %s – %s" % (cfg.get("rev", "R00"), date), size=6.4, bold=True)
        x = cols[1] + pad; y = y0 + 4.2 * MM; W = cols[2] - cols[1] - 2 * pad
        lab(x, y, "ΥΠΟΜΝΗΜΑ"); y += 8.6
        for k, v in legend:
            sh.otext(x, y, k, size=6.6, bold=True, color=BLUE if k == "μπλε" else BLACK)
            sh.otext(x + 44, y, v, size=6.0); y += 8.2
        x = cols[2] + pad; y = y0 + 4.2 * MM; W = cols[3] - cols[2] - 2 * pad
        lab(x, y, "ΣΗΜΕΙΩΣΕΙΣ"); y += 8.6
        allnotes = ["Διαστάσεις σε m."] + (["Η εξωτερική αλυσίδα κάθε πλευράς (παρειές υποστυλωμάτων) μετρήθηκε από τη γεωμετρία του σχεδίου· οι υπόλοιπες διαστάσεις είναι του μελετητή."] if info["FC"] else []) + notes
        for n in allnotes:
            for ln in _wrap(n, 6.0, W): sh.otext(x, y, ln, size=6.0); y += 7.2
            y += 1.2
        x = cols[3] + pad; y = y0 + 4.2 * MM; W = cols[4] - cols[3] - 2 * pad
        lab(x, y, "ΚΛΙΜΑΚΑ"); y += 15
        sh.otext(x, y, scale_txt, size=17, bold=True); sh.otext(x + 62, y, "(Α3 – εκτύπωση 100 %)", size=6.4)
        y += 5; scalebar(x + 1, y, min(5, int((W - 12) / u))); y += 1.6 * MM + 16
        lab(x, y, "ΒΑΣΗ"); y += 8
        for ln in _wrap(cfg["base"] + " Οι οπλισμοί ΜΟΝΟ από το σχέδιο του μελετητή.", 6.0, W): sh.otext(x, y, ln, size=6.0); y += 7.2
        info["title_rect"] = (x0, y0, x1, y1)
    sh.flush()
