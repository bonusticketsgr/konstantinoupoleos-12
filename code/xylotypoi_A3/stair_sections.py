"""ΣΚ-Τ – ΤΟΜΕΣ ΚΛΙΜΑΚΟΣΤΑΣΙΟΥ ΥΠΟΓΕΙΟ → ΙΣΟΓΕΙΟ → Α΄ (πραγματικές τομές, όχι ανάπτυγμα), 6 φύλλα Α3 όρθια, 1:20.

    python3 stair_sections.py [preview_prefix [dpi]]

Α-Α  κατά μήκος του ΝΟΤΙΟΥ κλάδου (y 7,00), βλέποντας βόρεια      Β-Β  κατά μήκος του ΒΟΡΕΙΟΥ κλάδου (y 5,70), βλέποντας βόρεια
Γ-Γ  κάθετα, μέσα από το πλατύσκαλο του υπογείου (x 10,30)         Δ-Δ  κάθετα, μέσα από τους δύο κλάδους (x 11,30)
Ε-Ε  κάθετα, μέσα από τη στροφή (x 12,50) – όλες οι κάθετες βλέποντας ανατολικά

Τα μοντέλα είναι τα stair_s2 (Σ2α, υπόγειο → ισόγειο) και stair_s3 (Σ3β, ισόγειο → Α΄): κάθε πάτημα = πολύγωνο ανάμεσα σε δύο ρίχτια·
η τομή είναι η τομή της ευθείας με τα πολύγωνα. Κάτω παρειά πλάκας σκάλας: h = 15 κάθετα στην τοπική κλίση (όπως το headroom() του
stair_all) – σχηματικά, τη λεπτομέρεια τη δίνει ο μελετητής."""
import os, sys, math
import pymupdf
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import substring
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "xylotypoi_S1_S2"))
import lib
from lib import MM, FONT_R, FONT_B, BLACK, GRAY, BLUE
import stair_s2 as A
import stair_s3 as B
from stair_s2 import View, cm, mt, lv, CONC, RED, FIN

REV, DATE = "R00", "17/11/2026"
OUT = A.OUT
NAME = "ΣΚ_Σκάλες_ΤΟΜΕΣ_A3_%s.pdf" % REV
FINAL = "ΣΚΑΛΕΣ_υπόγειο_ισόγειο_Α_όροφος_ΤΕΛΙΚΟ_A3.pdf"
SC = 20; H = 0.15
Z0, ZT = -3.25, 4.00
FILLC = (0.96, 0.93, 0.84); BUILTC = (0.87, 0.80, 0.64); WALLC = (0.90, 0.90, 0.90); GYPS = (0.80, 0.86, 0.93); GROUND = (0.86, 0.86, 0.86)
HEADC = (0.05, 0.35, 0.70); BACK = (0.55, 0.55, 0.55)
LAND0 = B.SSL0 - H                       # κάτω παρειά πλατύσκαλου ισογείου
LAND1 = B.SSL1 - H                       # κάτω παρειά πλατύσκαλου Α΄
BEAM_B = A.SSL1_STUDY - 0.50             # κάτω παρειά δοκών 50 της οροφής υπογείου (Δ9.1 30/50 · Δ12.1 25/50)
PERIM = A.PERIM

CUTS = [  # όνομα, άξονας που μένει σταθερός, τιμή, εύρος του άλλου άξονα, περιγραφή
    ("Α", "y", 7.00, (9.15, 13.50), "κατά μήκος του ΝΟΤΙΟΥ κλάδου, στη γραμμή ανάβασης", "βλέποντας ΒΟΡΕΙΑ"),
    ("Β", "y", 5.70, (9.15, 13.50), "κατά μήκος του ΒΟΡΕΙΟΥ κλάδου, στη γραμμή ανάβασης", "βλέποντας ΒΟΡΕΙΑ"),
    ("Γ", "x", 10.30, (4.60, 8.10), "κάθετα, μέσα από το πλατύσκαλο του υπογείου", "βλέποντας ΑΝΑΤΟΛΙΚΑ"),
    ("Δ", "x", 11.30, (4.60, 8.10), "κάθετα, μέσα από τους δύο κλάδους", "βλέποντας ΑΝΑΤΟΛΙΚΑ"),
    ("Ε", "x", 12.50, (4.60, 8.10), "κάθετα, μέσα από τη στροφή", "βλέποντας ΑΝΑΤΟΛΙΚΑ"),
    ("ΣΤ", "y", 7.45, (9.15, 13.50), "κατά μήκος του ΝΟΤΙΟΥ κλάδου, 15 cm από τη δοκό – εδώ είναι το ΜΙΚΡΟΤΕΡΟ ύψος", "βλέποντας ΒΟΡΕΙΑ"),
]
LONG_S = ("Α", "ΣΤ")                     # τομές κατά μήκος του νότιου κλάδου


def hm(h): return ("%.2f" % (math.floor(h * 100 + 1e-6) / 100)).replace(".", ",")      # ελεύθερο ύψος: κόβεται προς τα κάτω

# ---------------------------------------------------------------- πολύγωνα πατημάτων
OUTER = LineString([(A.WALL_X, A.Y1), (A.WALL_X, A.YS), (A.XE, A.YS), (A.XE, A.YN), (A.XL, A.YN)])
INNERL = LineString([(A.XL, A.W0), (A.XL, A.W1), (A.WX, A.W1), (A.WX, A.W0), (A.XL, A.W0)])


def _u_inner(M, k):
    if M is A: return A.U[k]
    x, y = M.RISERS[k][0]
    if abs(y - M.W1) < 1e-9: return (M.W1 - M.W0) + (x - M.XL)
    if abs(y - M.W0) < 1e-9: return PERIM / 2 + (M.W1 - M.W0) + (M.WX - x)
    return (M.W1 - M.W0) + (M.WX - M.XL) + (M.W1 - y)


def treads(M):
    out = {}
    for k in range(1, M.N):
        (ia, a), (ib, b) = M.RISERS[k], M.RISERS[k + 1]
        s0, s1 = OUTER.project(Point(a)), OUTER.project(Point(b))
        oc = list(substring(OUTER, s0, s1).coords) if s1 > s0 + 1e-9 else [a, b]
        u0, u1 = _u_inner(M, k), _u_inner(M, k + 1)
        ic = list(substring(INNERL, u0, u1).coords) if u1 > u0 + 1e-9 else [ia, ib]
        out[k] = Polygon([ia] + oc + ic[::-1]).buffer(0)
    return out


TRA, TRB = treads(A), treads(B)
TR = {A: TRA, B: TRB}


def ssl_v(M, k): return M.FFL0 + k * M.RISE - M.T_STEP          # στάθμη μπετού «χωρίς κόψιμο» (k = 0: νοητή γωνία κάτω από το 1ο πάτημα)


def _dline(p, seg):
    (x0, y0), (x1, y1) = seg; L = math.hypot(x1 - x0, y1 - y0)
    return abs((x1 - x0) * (y0 - p[1]) - (x0 - p[0]) * (y1 - y0)) / L


def soffit(M, k, x, y):
    """κάτω παρειά της πλάκας της σκάλας κάτω από το σημείο (x, y) του πατήματος k"""
    if M is A and k <= A.NL: return A.SSL0                                   # συμπαγές πλατύσκαλο πάνω στην κοιτόστρωση
    d0, d1 = _dline((x, y), M.RISERS[k]), _dline((x, y), M.RISERS[k + 1]); g = max(d0 + d1, 1e-6)
    z = ssl_v(M, k - 1) + d0 / g * M.RISE - H * math.hypot(1.0, M.RISE / g)
    z = min(z, M.SSL[k] - H)
    return max(z, A.SSL0) if M is A else z


def ceil_A(x, y):
    """ό,τι έχει πάνω από το κεφάλι του όποιος στέκεται στο (x, y) της σκάλας / του χωλ υπογείου"""
    vals = []
    if x < A.XL - 1e-6:
        vals.append(LAND0)
        if x < 9.70: vals.append(BEAM_B)
    else:
        for j, poly in TRB.items():
            if poly.buffer(1e-6).contains(Point(x, y)): vals.append(soffit(B, j, x, y))
    return min(vals) if vals else None


def cut_runs(M, axis, c, t0, t1):
    line = LineString([(t0, c), (t1, c)]) if axis == "y" else LineString([(c, t0), (c, t1)])
    segs = []
    for k, poly in TR[M].items():
        g = poly.intersection(line)
        if g.is_empty: continue
        geoms = [g] if g.geom_type == "LineString" else [h for h in getattr(g, "geoms", []) if h.geom_type == "LineString"]
        for h in geoms:
            cs = list(h.coords); ts = sorted((p[0] if axis == "y" else p[1]) for p in (cs[0], cs[-1]))
            if ts[1] - ts[0] > 1e-4: segs.append((round(ts[0], 4), round(ts[1], 4), k))
    segs.sort(); runs = []
    for s in segs:
        if runs and abs(runs[-1][-1][1] - s[0]) < 2e-3: runs[-1].append(s)
        else: runs.append([s])
    return runs


# ---------------------------------------------------------------- σχεδίαση
def vtext(sh, x, y, s, size, color, bold=False):
    """κείμενο στραμμένο 90°, κεντραρισμένο στο (x, y)"""
    w = (FONT_B if bold else FONT_R).text_length(s, fontsize=size)
    sh.otext(x + size * 0.36, y + w / 2, s, size=size, bold=bold, rot=90, color=color, mask=True)


def draw_stair(sh, v, M, runs, axis, c):
    P = (lambda t: (t, c)) if axis == "y" else (lambda t: (c, t))
    onr = lambda k, t: LineString(M.RISERS[k]).distance(Point(P(t))) < 3e-3
    out = []
    for run in runs:
        top = []; sof = []
        for (ta, tb, k) in run:
            top += [(ta, M.SSL[k]), (tb, M.SSL[k])]
            n = max(2, int((tb - ta) / 0.01) + 1)
            pts = [(ta + (tb - ta) * i / n, soffit(M, k, *P(ta + (tb - ta) * i / n))) for i in range(n + 1)]
            if sof and abs(sof[-1][0] - pts[0][0]) < 2e-3:
                z = min(sof[-1][1], pts[0][1]); sof[-1] = (sof[-1][0], z); pts[0] = (pts[0][0], z)
            sof += pts
        v.poly(top + sof[::-1], 0.9, BLACK, CONC)
        ts, te = run[0][0], run[-1][1]
        if M is B and onr(1, ts) and sof[0][1] > B.SSL0 + 0.01:               # πόδι της σκάλας μέσα στο γέμισμα του χωλ
            v.poly([(ts, B.SSL0), (ts, sof[0][1]), (ts - (sof[0][1] - B.SSL0) / (B.RISE / B.G), B.SSL0)], 0.9, BLACK, CONC)
        for (ta, tb, k) in run:
            bu = A.BUILT.get(k, 0.0) if M is A else 0.0
            if bu > 0.003: v.poly([(ta, M.SSL[k]), (tb, M.SSL[k]), (tb, M.SSL[k] + bu), (ta, M.SSL[k] + bu)], 0.3, BLACK, BUILTC)
            v.poly([(ta, M.SSL[k] + bu), (tb, M.SSL[k] + bu), (tb, M.FFL[k]), (ta, M.FFL[k])], 0, FILLC, FILLC)
        fin = []
        if onr(1, ts): fin.append((ts, M.FFL0))
        if onr(M.N, ts): fin.append((ts, M.FFL1))
        for (ta, tb, k) in run: fin += [(ta, M.FFL[k]), (tb, M.FFL[k])]
        if onr(1, te): fin.append((te, M.FFL0))
        if onr(M.N, te): fin.append((te, M.FFL1))
        v.poly(top, 0.9, BLACK, None, close=False); v.poly(fin, 0.8, FIN, None, close=False)
        out.append((run, sof))
    return out


def label_steps(sh, v, M, run):
    for (ta, tb, k) in run:
        wpt = (tb - ta) * v.k; xm = (v.X(ta) + v.X(tb)) / 2; y = v.Y(M.FFL[k])
        if wpt < 13: continue
        if wpt > 110:                                                         # πλατύ πάτημα (τομή κατά μήκος του σκαλιού): οριζόντια
            sh.ocircle(xm - 46, y - 8.5, 5.2, 0.45, BLACK, (1, 1, 1)); sh.otext(xm - 46, y - 6.0, str(k + 1), size=6.8, bold=True, align="center")
            sh.otext(xm - 36, y - 6.0, lv(M.SSL[k]) + " μπετό", size=6.6, bold=True, color=RED, mask=True)
            sh.otext(xm + 12, y - 6.0, lv(M.FFL[k]) + " τελικό", size=6.6, color=FIN, mask=True)
            continue
        sh.ocircle(xm, y - 7.2, 4.8, 0.4, BLACK, (1, 1, 1)); sh.otext(xm, y - 4.9, str(k + 1), size=6.2, bold=True, align="center")
        if wpt >= 26:
            vtext(sh, xm - 4.2, y - 26.5, lv(M.SSL[k]), 5.8, RED, True); vtext(sh, xm + 3.6, y - 26.5, lv(M.FFL[k]), 5.8, FIN)


def head_dims(sh, v, run, axis, c, dry=False, hmin=None):
    """ελεύθερο ύψος πάνω από κάθε σκαλί της σκάλας υπογείου: από το τελικό πάτημα ως το μπετό από πάνω"""
    P = (lambda t: (t, c)) if axis == "y" else (lambda t: (c, t)); res = []
    for i, (ta, tb, k) in enumerate(run):
        prv = run[i - 1][2] if i > 0 else None; nxt = run[i + 1][2] if i + 1 < len(run) else None
        if tb - ta > 0.6: t = (ta + tb) / 2
        elif prv is not None and prv < k: t = ta
        elif nxt is not None and nxt < k: t = tb
        elif nxt is not None: t = ta
        elif prv is not None: t = tb
        else: t = (ta + tb) / 2
        tq = [t]
        if axis == "y" and ta < 9.70 - 0.02 and tb > 9.70 + 0.10 and t > 9.70: tq.insert(0, (ta + 9.70) / 2)     # και κάτω από τη δοκό Δ9.1
        for t in tq:
          cs = ceil_A(*P(min(max(t, ta + 0.004), tb - 0.004)))
          if cs is None: continue
          z0, z1 = A.FFL[k], cs; res.append((k, z1 - z0))
          if dry: continue
          low = z1 - z0 < 2.30; col = RED if low else HEADC
          x = v.X(t); sh.oline(x, v.Y(z0), x, v.Y(z1), 0.7 if low else 0.35, col, "[2 1.5] 0"); sh.tick(x, v.Y(z0), col); sh.tick(x, v.Y(z1), col)
          vtext(sh, x, v.Y(z0 + (z1 - z0) * (0.56 if i % 2 else 0.44)), hm(z1 - z0) + ("  ΕΛΑΧΙΣΤΟ" if low and hmin is not None and z1 - z0 < hmin + 0.005 else ""), 8.4 if low else 6.6, col, True)
    return res


def simple_dim(sh, v, t, z0, z1, s=None, color=HEADC, frac=0.5):
    x = v.X(t); sh.oline(x, v.Y(z0), x, v.Y(z1), 0.35, color, "[2 1.5] 0"); sh.tick(x, v.Y(z0), color); sh.tick(x, v.Y(z1), color)
    vtext(sh, x, v.Y(z0 + (z1 - z0) * frac), s or hm(z1 - z0), 6.6, color, True)


def floor_tag(sh, v, t, name, zf, zc, align="left"):
    x = v.X(t); y = v.Y(zf)
    sh.otext(x, y - 23, name, size=7.4, bold=True, align=align, mask=True)
    sh.otext(x, y - 14, lv(zf) + " τελικό", size=7.0, bold=True, color=FIN, align=align, mask=True)
    sh.otext(x, y - 5.5, lv(zc) + " μπετό", size=7.0, bold=True, color=RED, align=align, mask=True)


def landing(v, ta, tb, zc, zf, slab=True):
    if slab: v.poly([(ta, zc - H), (tb, zc - H), (tb, zc), (ta, zc)], 0.9, BLACK, CONC)
    v.poly([(ta, zc), (tb, zc), (tb, zf), (ta, zf)], 0, FILLC, FILLC); v.line((ta, zf), (tb, zf), 0.8, FIN)


def section(sh, cut):
    name, axis, c, (t0, t1), desc, look = cut
    w_mm = (t1 - t0) * 1000 / SC; x0_mm = 6 + (285 - w_mm) / 2 + 3
    v = View(sh, x0_mm, 373.0 - 0.0, t0, Z0, SC, flip=True)
    runsA, runsB = cut_runs(A, axis, c, t0, t1), cut_runs(B, axis, c, t0, t1)
    # ---------------- κοιτόστρωση
    v.poly([(t0, Z0), (t1, Z0), (t1, A.SSL0), (t0, A.SSL0)], 0, GROUND, GROUND); v.line((t0, A.SSL0), (t1, A.SSL0), 0.9)
    if axis == "y":                                                           # ---------------- τομές Α–Δ (οριζόντιος άξονας = x)
        door = A.DOOR_Y[0] < c < A.DOOR_Y[1]
        # ανατολικό τοιχείο / τοίχος σε όλο το ύψος
        v.poly([(A.XE, A.SSL0), (13.35, A.SSL0), (13.35, ZT), (A.XE, ZT)], 0.9, BLACK, CONC)
        # υπόγειο: τοίχος γυψοσανίδας 9,40–9,50 (με την πόρτα του parking), δάπεδο
        if door:
            v.poly([(9.40, A.FFL0 + 2.10), (9.50, A.FFL0 + 2.10), (9.50, BEAM_B), (9.40, BEAM_B)], 0.5, BLACK, GYPS)
            v.line((9.40, A.FFL0), (9.40, A.FFL0 + 2.10), 0.3, GRAY, "[2 2] 0"); v.line((9.50, A.FFL0), (9.50, A.FFL0 + 2.10), 0.3, GRAY, "[2 2] 0")
        else: v.poly([(9.40, A.SSL0), (9.50, A.SSL0), (9.50, BEAM_B), (9.40, BEAM_B)], 0.5, BLACK, GYPS)
        if not any(r[0][0] < 9.6 for r in runsA): landing(v, 9.50, A.XL, A.SSL0, A.FFL0, slab=False)
        v.poly([(t0, A.SSL0), (9.40, A.SSL0), (9.40, A.FFL0), (t0, A.FFL0)], 0, FILLC, FILLC); v.line((t0, A.FFL0), (9.40, A.FFL0), 0.8, FIN)
        # οροφή υπογείου: δοκός Δ9.1, πλάκα διαμερίσματος δυτικά, πλατύσκαλο ισογείου Π6 με το γέμισμα
        v.poly([(t0, A.SSL1_STUDY - 0.18), (9.40, A.SSL1_STUDY - 0.18), (9.40, A.SSL1_STUDY), (t0, A.SSL1_STUDY)], 0.9, BLACK, CONC)
        v.poly([(t0, A.SSL1_STUDY), (9.54, A.SSL1_STUDY), (9.54, 0.45), (t0, 0.45)], 0, FILLC, FILLC); v.line((t0, 0.45), (9.54, 0.45), 0.8, FIN)
        landing(v, 9.70, A.XL, B.SSL0, B.FFL0)
        v.poly([(9.40, BEAM_B), (9.70, BEAM_B), (9.70, A.SSL1_STUDY), (9.40, A.SSL1_STUDY)], 0.9, BLACK, CONC)
        v.poly([(9.54, A.SSL1_STUDY), (9.70, A.SSL1_STUDY), (9.70, B.SSL1 - 0.50), (9.54, B.SSL1 - 0.50)], 0.5, BLACK, WALLC)      # τοίχος ισογείου Τ6 / Τ7
        # οροφή ισογείου: δοκός, πλατύσκαλο Α΄, τοίχος Α΄ (με την πόρτα του διαμερίσματος)
        v.poly([(t0, B.SSL1 - 0.18), (9.40, B.SSL1 - 0.18), (9.40, B.SSL1), (t0, B.SSL1)], 0.9, BLACK, CONC)
        v.poly([(t0, B.SSL1), (9.40, B.SSL1), (9.40, B.FFL1), (t0, B.FFL1)], 0, FILLC, FILLC); v.line((t0, B.FFL1), (9.40, B.FFL1), 0.8, FIN)
        landing(v, 9.70, A.XL, B.SSL1, B.FFL1)
        v.poly([(9.40, B.SSL1 - 0.50), (9.70, B.SSL1 - 0.50), (9.70, B.SSL1), (9.40, B.SSL1)], 0.9, BLACK, CONC)
        v.poly([(9.55, B.SSL1), (9.70, B.SSL1), (9.70, B.FFL1), (9.55, B.FFL1)], 0, FILLC, FILLC); v.line((9.55, B.FFL1), (9.70, B.FFL1), 0.8, FIN)
        if not (5.30 < c < 6.30): v.poly([(9.40, B.SSL1), (9.55, B.SSL1), (9.55, ZT), (9.40, ZT)], 0.5, BLACK, WALLC)
        else: v.poly([(9.40, B.SSL1), (9.55, B.SSL1), (9.55, B.FFL1), (9.40, B.FFL1)], 0, FILLC, FILLC); v.line((9.40, B.FFL1), (9.55, B.FFL1), 0.8, FIN)
    else:                                                                     # ---------------- τομές Γ–Ε (οριζόντιος άξονας = y)
        shaft = c >= 11.05                                                    # βόρεια: τοιχείο Κ6 του ανελκυστήρα (αλλιώς χωλ ανελκυστήρα)
        if shaft: v.poly([(4.85, A.SSL0), (A.YN, A.SSL0), (A.YN, ZT), (4.85, ZT)], 0.9, BLACK, CONC)
        # νότια: δοκοί Δ12.1 / Δ13.1 και οι πλάκες πίσω τους
        for (zt_, hb, zf_) in ((A.SSL1_STUDY, 0.50, B.FFL0), (B.SSL1, 0.40, B.FFL1)):
            v.poly([(7.85, zt_ - H), (t1, zt_ - H), (t1, zt_), (7.85, zt_)], 0.9, BLACK, CONC)
            v.poly([(A.YS, zt_ - hb), (7.85, zt_ - hb), (7.85, zt_), (A.YS, zt_)], 0.9, BLACK, CONC)
            v.poly([(A.YS, zt_), (t1, zt_), (t1, zf_), (A.YS, zf_)], 0, FILLC, FILLC); v.line((A.YS if c < A.XL else 7.70, zf_), (t1, zf_), 0.8, FIN)
        if c >= 10.40: v.poly([(A.YS, A.SSL0), (7.70, A.SSL0), (7.70, BEAM_B), (A.YS, BEAM_B)], 0.5, BLACK, GYPS)                 # τοίχος μηχανοστασίου
        else: v.poly([(A.YS, A.FFL0 + 2.10), (7.70, A.FFL0 + 2.10), (7.70, BEAM_B), (A.YS, BEAM_B)], 0.5, BLACK, GYPS)
        if c >= A.XL:
            v.poly([(A.YS, A.SSL1_STUDY), (7.70, A.SSL1_STUDY), (7.70, B.SSL1 - 0.40), (A.YS, B.SSL1 - 0.40)], 0.5, BLACK, WALLC)   # τοίχος σκάλας / εισόδου
            v.poly([(A.YS, B.SSL1), (7.70, B.SSL1), (7.70, ZT), (A.YS, ZT)], 0.5, BLACK, WALLC)
        v.poly([(7.70 if c >= 10.40 else A.YS, A.SSL0), (t1, A.SSL0), (t1, A.FFL0), (7.70 if c >= 10.40 else A.YS, A.FFL0)], 0, FILLC, FILLC)
        v.line((7.70 if c >= 10.40 else A.YS, A.FFL0), (t1, A.FFL0), 0.8, FIN)
        if c < A.XL:                                                          # πλατύσκαλα + χωλ ανελκυστήρα βόρεια
            landing(v, t0, A.Y1, A.SSL0, A.FFL0, slab=False)
            landing(v, t0, A.YS, B.SSL0, B.FFL0); landing(v, t0, A.YS, B.SSL1, B.FFL1)
        else:                                                                 # δάπεδο υπογείου κάτω από τον βόρειο κλάδο
            ya = min([r[0][0] for r in runsA if any(k > A.NL for _, _, k in r)] + [A.YS])
    # ---------------- ό,τι φαίνεται πίσω από την τομή (αχνά) – πριν από τις σκάλες, που το σκεπάζουν
    if name in LONG_S:
        for M in (A, B):
            ks = [k for k in range(1, M.N + 1) if abs(M.RISERS[k][0][1] - M.W0) < 1e-9 and (M is B or k >= 13)]
            xs = {k: M.RISERS[k][0][0] for k in ks}; pts = []
            for k in ks[:-1]: pts += [(xs[k], M.FFL[k]), (xs[k + 1], M.FFL[k])]
            pts += [(xs[ks[-1]], M.FFL[ks[-1] - 1]), (xs[ks[-1]], M.FFL1)]
            v.poly(pts, 0.45, BACK, None, "[3 2] 0", close=False)
    if name == "Γ":
        for M, rng in ((A, range(5, 11)), (B, range(1, 9))):
            zs = []
            for k in rng:
                ys = sorted(p[1] for p in M.RISERS[k])
                if ys[0] < A.W1 - 1e-6: continue
                v.line((A.W1, M.FFL[k]), (A.YS, M.FFL[k]), 0.35, BACK); zs.append(M.FFL[k])
            v.line((A.W1, zs[0] - M.RISE), (A.W1, zs[-1]), 0.35, BACK)
    # ---------------- οι δύο σκάλες
    dA = draw_stair(sh, v, A, runsA, axis, c); dB = draw_stair(sh, v, B, runsB, axis, c)
    sh.flush()
    # ---------------- ετικέτες σκαλιών, στάθμες, ελεύθερα ύψη
    for run, _ in dA: label_steps(sh, v, A, run)
    for run, _ in dB: label_steps(sh, v, B, run)
    hr = []
    for run, _ in dA: hr += head_dims(sh, v, run, axis, c, dry=True)
    hmin = min(h for _, h in hr) if hr else None
    for run, _ in dA: head_dims(sh, v, run, axis, c, hmin=hmin)
    tl = t0 + 0.02
    if axis == "y":
        floor_tag(sh, v, t0 - 0.02, "ΥΠΟΓΕΙΟ", A.FFL0, A.SSL0, "right"); floor_tag(sh, v, t0 - 0.02, "ΙΣΟΓΕΙΟ (χωλ)", B.FFL0, B.SSL0, "right")
        floor_tag(sh, v, t0 - 0.02, "Α΄ ΟΡΟΦΟΣ", B.FFL1, B.SSL1, "right")
        v.text(10.30, B.SSL0 - H / 2, "Π6 h=15", size=6.0, bold=True, dy=2.2, align="center"); v.text(10.30, (B.SSL0 + B.FFL0) / 2, "γέμισμα %s" % cm(B.FFL0 - B.SSL0, 0), size=6.2, dy=2.2, align="center")
        v.text(10.30, B.SSL1 - H / 2, "Π6 h=15", size=6.0, bold=True, dy=2.2, align="center")
        v.text(9.55, (BEAM_B + A.SSL1_STUDY) / 2, "Δ9.1", size=5.6, bold=True, dy=0, align="center"); v.text(9.55, (BEAM_B + A.SSL1_STUDY) / 2, "30/50", size=5.2, dy=6, align="center")
        sh.otext(v.X(13.225) + 2.6, v.Y(-1.2), "τοιχείο / τοίχος κλιμακοστασίου", size=6.0, rot=90, mask=True)
        simple_dim(sh, v, 10.30, B.FFL0, LAND1)                                # ύψος χωλ ισογείου κάτω από το πλατύσκαλο του Α΄
        if not any(r[0][0] < 9.6 for r in runsA):
            simple_dim(sh, v, 10.30, A.FFL0, LAND0); simple_dim(sh, v, 9.60, A.FFL0, BEAM_B, frac=0.3)
            if door: sh.otext(v.X(9.45) + 2.4, v.Y(A.FFL0 + 1.05) + 28, "ΠΟΡΤΑ parking 0,90 × 2,10", size=6.0, bold=True, rot=90, color=(0.10, 0.35, 0.60), mask=True)
            v.text(10.20, A.FFL0, "δάπεδο πόρτας / ασανσέρ", size=6.0, dy=-4, align="center", color=GRAY)
        if name in LONG_S:
            v.text(12.45, 2.95, "βόρειος κλάδος (πίσω από την τομή)", size=5.8, color=BACK, align="center"); v.text(12.45, -0.28, "βόρειος κλάδος (πίσω)", size=5.8, color=BACK, align="center")
            v.text(10.55, A.SSL0, "συμπαγές πλατύσκαλο", size=5.8, dy=-10, align="center", bold=True); v.text(12.30, A.SSL0, "χώρος κάτω από τη σκάλα", size=6.0, dy=-12, align="center", color=GRAY)
            v.text(10.60, B.SSL0, "πόδι σκάλας", size=5.2, dy=-13, align="right"); v.text(10.60, B.SSL0, "μέσα στο γέμισμα", size=5.2, dy=-7, align="right")
        if name == "Β":
            v.text(12.20, A.SSL0, "χώρος κάτω από τον βόρειο κλάδο", size=6.0, dy=-12, align="center", color=GRAY)
            if A.BUILT:
                v.text(10.30, 0.635, "σκαλιά %d–%d: χτιστά πάνω στην πλάκα →" % (A.KL + 2, A.N), size=5.8, bold=True, align="center")
            v.text(9.475, B.FFL1 + 0.10, "πόρτα Α΄", size=5.6, align="center", color=GRAY)
    else:
        tx = t0 - 0.02 if c >= 11.05 else t0 - 0.02
        floor_tag(sh, v, tx, "ΥΠΟΓΕΙΟ", A.FFL0, A.SSL0, "right"); floor_tag(sh, v, tx, "ΙΣΟΓΕΙΟ (χωλ)", B.FFL0, B.SSL0, "right"); floor_tag(sh, v, tx, "Α΄ ΟΡΟΦΟΣ", B.FFL1, B.SSL1, "right")
        v.text(7.725, A.SSL1_STUDY - 0.25, "Δ12.1", size=5.4, bold=True, dy=0, align="center"); v.text(7.725, A.SSL1_STUDY - 0.25, "25/50", size=5.0, dy=6, align="center")
        v.text(7.725, B.SSL1 - 0.20, "Δ13.1", size=5.4, bold=True, dy=0, align="center"); v.text(7.725, B.SSL1 - 0.20, "25/40", size=5.0, dy=6, align="center")
        sh.otext(v.X(7.95), v.Y(B.FFL0) - 5, "είσοδος κτηρίου", size=5.8, color=GRAY, align="center"); sh.otext(v.X(7.95), v.Y(A.FFL0) + 9, "μηχανοστάσιο", size=5.8, color=GRAY, align="center")
        if shaft:
            sh.otext(v.X(4.975) + 2.4, v.Y(0.4), "τοιχείο ανελκυστήρα Κ6", size=6.0, rot=90, mask=True)
            if c < A.WX:
                sh.otext(v.X((A.W0 + A.W1) / 2) + 2.2, v.Y(-2.55), "φανάρι", size=5.6, rot=90, color=GRAY)
                sh.oline(v.X(A.W0), v.Y(A.SSL0), v.X(A.W0), v.Y(ZT), 0.2, GRAY, "[1 2.5] 0"); sh.oline(v.X(A.W1), v.Y(A.SSL0), v.X(A.W1), v.Y(ZT), 0.2, GRAY, "[1 2.5] 0")
            v.text(5.70, A.SSL0, "χώρος κάτω από τη σκάλα", size=6.0, dy=-12, align="center", color=GRAY)
        else:
            v.text(4.85, A.FFL0, "χωλ ανελκυστήρα", size=5.8, dy=-4, align="center", color=GRAY); v.text(4.85, B.FFL0, "χωλ ανελκυστήρα", size=5.8, dy=-4, align="center", color=GRAY)
            v.text(6.35, B.SSL0 - H / 2, "πλατύσκαλο ισογείου Π6 h=15", size=6.0, bold=True, dy=2.2, align="center"); v.text(6.35, (B.SSL0 + B.FFL0) / 2, "γέμισμα %s" % cm(B.FFL0 - B.SSL0, 0), size=6.2, dy=2.2, align="center")
            v.text(6.35, B.SSL1 - H / 2, "πλατύσκαλο Α΄ Π6 h=15", size=6.0, bold=True, dy=2.2, align="center")
            simple_dim(sh, v, 5.60, A.FFL0, LAND0); simple_dim(sh, v, 5.60, B.FFL0, LAND1)
            v.text(5.70, A.FFL0, "δάπεδο πόρτας parking", size=6.0, dy=-4, align="center", color=GRAY)
            v.text(6.95, A.SSL0, "συμπαγές πλατύσκαλο – σκαλιά 1–%d" % A.NL, size=5.8, dy=-8, align="center", bold=True)
            sh.otext(v.X(7.00), v.Y(-0.80), "σκαλιά 6…11 του νότιου κλάδου (από μπροστά)", size=5.6, color=BACK, align="center", mask=True)
            v.text(7.00, 2.55, "σκάλα προς Α΄ (από μπροστά)", size=5.6, color=BACK, align="center")
            v.line((A.YS, A.FFL0), (A.YS, A.FFL0 + 2.10), 0.3, RED, "[2 2] 0"); v.line((7.70, A.FFL0), (7.70, A.FFL0 + 2.10), 0.3, RED, "[2 2] 0")
            sh.otext(v.X(7.80) + 2.6, v.Y(-2.85), "ΠΟΡΤΑ ΜΗΧΑΝΟΣΤΑΣΙΟΥ (όπως είναι στα σχέδια):", size=6.4, bold=True, rot=90, color=RED)
            sh.otext(v.X(7.93) + 2.6, v.Y(-2.85), "την κλείνει το πλατύσκαλο – ΝΑ ΑΛΛΑΞΕΙ ΘΕΣΗ", size=6.4, bold=True, rot=90, color=RED)
    sh.flush()
    return hr


def keyplan(sh, x_mm, y_mm, cur):
    v = View(sh, x_mm, y_mm, 9.30, 4.75, 100)
    v.rect(9.40, 4.75, 9.70, 5.15, 0.6, BLACK, CONC); v.rect(11.05, 4.85, 13.35, A.YN, 0.6, BLACK, CONC); v.rect(A.XE, A.YN, 13.35, 7.85, 0.6, BLACK, CONC)
    v.rect(9.40, 5.15, 9.50, A.DOOR_Y[0], 0.3, BLACK, GYPS); v.rect(9.40, A.DOOR_Y[1], 9.50, 7.85, 0.3, BLACK, GYPS); v.rect(9.50, A.YS, A.XE, 7.85, 0.5, BLACK, (1, 1, 1))
    for k, (a, b) in A.RISERS.items(): v.line(a, b, 0.25, GRAY)
    v.rect(A.XL, A.W0, A.WX, A.W1, 0.5, BLACK, (1, 1, 1))
    for (nm, axis, c, (t0, t1), _, _) in CUTS:
        on = nm == cur; col = RED if on else (0.55, 0.55, 0.55); w = 1.1 if on else 0.35
        if axis == "y": a, b = (9.30, c), (13.45, c); d = (0, -1)
        else: a, b = (c, 4.80), (c, 7.95); d = (1, 0)
        v.line(a, b, w, col, "[5 2 1 2] 0")
        for p in (a, b):
            px, py = v.X(p[0]), v.Y(p[1])
            if on:
                q = (px + d[0] * 7, py + d[1] * 7); n = (-d[1], d[0])
                sh.shape.draw_polyline([pymupdf.Point(*q), pymupdf.Point(px + n[0] * 2.4, py + n[1] * 2.4), pymupdf.Point(px - n[0] * 2.4, py - n[1] * 2.4)]); sh.shape.finish(width=0.3, color=col, fill=col, closePath=True)
        lx, ly = (v.X(a[0]) - 5, v.Y(a[1]) + 2.4) if axis == "y" else (v.X(a[0]), v.Y(a[1]) - 3)
        sh.otext(lx, ly, nm, size=7.2 if on else 5.6, bold=True, color=col, align="center")
    sh.otext(v.X(13.45) + 7, v.Y(4.9) + 4, "Β", size=6.0, bold=True, align="center"); sh.oline(v.X(13.45) + 7, v.Y(4.9) + 6, v.X(13.45) + 7, v.Y(4.9) + 15, 0.5)
    sh.shape.draw_polyline([pymupdf.Point(v.X(13.45) + 7, v.Y(4.9) + 5.5), pymupdf.Point(v.X(13.45) + 5, v.Y(4.9) + 9), pymupdf.Point(v.X(13.45) + 9, v.Y(4.9) + 9)]); sh.shape.finish(width=0.3, color=BLACK, fill=BLACK, closePath=True)


def title(sh, cut, n, hr):
    name, axis, c, _, desc, look = cut
    PW, PH = 297 * MM, 420 * MM; m = 6 * MM
    sh.orect(m, m, PW - m, PH - m, 0.6); y0 = PH - m - 38 * MM; sh.oline(m, y0, PW - m, y0, 0.9)
    keyplan(sh, 10.0, (y0 / MM) + 3.0, name)
    sh.oline(m + 52 * MM, y0, m + 52 * MM, PH - m, 0.4); x = m + 55 * MM
    sh.otext(x, y0 + 11 * MM, "ΤΟΜΗ %s-%s" % (name, name), size=22, bold=True)
    sh.otext(x + (58 if len(name) > 1 else 52) * MM, y0 + 6.2 * MM, desc, size=8.6 if len(desc) < 60 else 7.6, bold=True); sh.otext(x + (58 if len(name) > 1 else 52) * MM, y0 + 10.6 * MM, "%s = %s · %s" % ("y" if axis == "y" else "x", mt(c), look), size=7.6)
    sh.otext(x, y0 + 17 * MM, "ΣΚΑΛΕΣ ΥΠΟΓΕΙΟ → ΙΣΟΓΕΙΟ → Α΄ ΟΡΟΦΟΣ · κλίμακα 1:%d · Α3 όρθιο, εκτύπωση 100 %%" % SC, size=7.4)
    yy = y0 + 22.5 * MM
    sh.otext(x, yy, "ΚΟΚΚΙΝΟ = στάθμη ΜΠΕΤΟΥ", size=7.0, bold=True, color=RED); sh.otext(x + 44 * MM, yy, "ΚΑΦΕ = ΤΕΛΙΚΗ στάθμη", size=7.0, bold=True, color=FIN)
    sh.otext(x + 84 * MM, yy, "ΜΠΛΕ = ΕΛΕΥΘΕΡΟ ΥΨΟΣ (τελικό σκαλί → μπετό από πάνω)", size=7.0, bold=True, color=HEADC)
    yy += 4.6 * MM
    if hr:
        k, h = min(hr, key=lambda q: q[1])
        sh.otext(x, yy, "Μικρότερο ελεύθερο ύψος σε αυτή την τομή: %s m στο σκαλί %d (όριο 2,20)." % (hm(h), k + 1), size=7.4, bold=True)
    sh.otext(x, yy + 4.4 * MM, "Αριθμοί σκαλιών όπως στις κατόψεις Σ2α %s / Σ3β %s. Κάτω παρειά σκάλας σχηματικά (h = 15) – λεπτομέρεια μελετητή." % (A.REV, B.REV), size=6.4, color=GRAY)
    sh.otext(x, PH - m - 2.2 * MM, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓ. ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ", size=6.6, bold=True)
    sh.otext(PW - m - 2.5 * MM, PH - m - 2.2 * MM, "ΣΚ-Τ%d · %s · %s" % (n, REV, DATE), size=6.4, align="right", color=GRAY)


def main():
    doc = pymupdf.open(); allhr = {}
    for n, cut in enumerate(CUTS, 1):
        sh = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=SC, page_w=297, page_h=420, sx0=0, sy0=0)
        hr = section(sh, cut); title(sh, cut, n, hr); sh.flush()
        doc.insert_pdf(sh.doc); allhr[cut[0]] = hr
    os.makedirs(OUT, exist_ok=True); path = os.path.join(OUT, NAME)
    doc.set_metadata(dict(title="ΣΚ-Τ – Τομές κλιμακοστασίου υπόγειο → ισόγειο → Α΄ (Α-Α … ΣΤ-ΣΤ)", author="ARKAD Ι.Κ.Ε."))
    doc.save(path, garbage=4, deflate=True); print("->", NAME, "(%d φύλλα)" % doc.page_count)
    for nm, hr in allhr.items():
        print("τομή %s: ελεύθερα ύψη" % nm, " ".join("%d:%.2f" % (k + 1, h) for k, h in hr))
    parts = [os.path.join(OUT, A.NAME), os.path.join(OUT, B.NAME)] + [os.path.join(OUT, f) for f in sorted(os.listdir(OUT)) if f.startswith("ΣΚ_Σκάλες_υπόγειο") and f.endswith(".pdf")] + [path]
    if all(os.path.exists(p) for p in parts):
        fin = pymupdf.open()
        for p in parts: fin.insert_pdf(pymupdf.open(p))
        fin.set_metadata(dict(title="Σκάλες υπόγειο → ισόγειο → Α΄ όροφος – κατόψεις, ανάπτυγμα και τομές", author="ARKAD Ι.Κ.Ε."))
        fin.save(os.path.join(OUT, FINAL), garbage=4, deflate=True); print("->", FINAL, "(%d φύλλα)" % fin.page_count)
    if len(sys.argv) > 1:
        d = pymupdf.open(path)
        for i in range(d.page_count): d[i].get_pixmap(dpi=int(sys.argv[2]) if len(sys.argv) > 2 else 110).save("%s_%s.png" % (sys.argv[1], CUTS[i][0]))


if __name__ == "__main__":
    main()
