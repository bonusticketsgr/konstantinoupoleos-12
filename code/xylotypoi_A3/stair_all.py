"""ΣΚ – ΣΚΑΛΕΣ ΥΠΟΓΕΙΟ → ΙΣΟΓΕΙΟ → Α΄ ΟΡΟΦΟΣ: ΕΝΙΑΙΑ ΤΟΜΗ (ανάπτυγμα στη γραμμή ανάβασης), Α3.

    python3 stair_all.py [preview.png [dpi]]

Δείχνει ΜΑΖΙ τις δύο σκάλες (μοντέλα stair_s2 = Σ2α και stair_s3 = Σ3β) ώστε να φαίνεται ότι δένουν στο ίδιο πλατύσκαλο του
ισογείου: ΜΠΕΤΟ +0,30 (πλάκα Π6 του Σ2_ΕΦ) / ΤΕΛΙΚΟ +0,60 (γέμισμα 30). Κόκκινο = στάθμη μπετού, καφέ = τελική στάθμη.
Αρίθμηση όπως στις κατόψεις (ο αριθμός ΠΡΙΝ από το ρίχτι του)."""
import os, sys, math
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "xylotypoi_S1_S2"))
import lib
from lib import MM, FONT_R, FONT_B, BLACK, GRAY, BLUE
import stair_s2 as A
import stair_s3 as B
from stair_s2 import View, level_mark, cm, mt, lv, lv3, CONC, RED, FIN

REV, DATE = "R09", "17/11/2026"
OUT = A.OUT
NAME = "ΣΚ_Σκάλες_υπόγειο_ισόγειο_Α_όροφος_ΤΟΜΗ_A3_%s.pdf" % REV
SC = 40
assert abs(A.FFL1 - B.FFL0) < 1e-9 and abs(A.SSL1 - B.SSL0) < 1e-9, "οι δύο σκάλες δεν δένουν στο ισόγειο"
FILLC = (0.96, 0.93, 0.84); H = 0.15

# ---------------------------------------------------------------- ανάπτυγμα (s = μήκος πάνω στη γραμμή ανάβασης, m)
S_DOOR = 0.80                                    # δάπεδο υπογείου μπροστά στην πόρτα (σχηματικά)
sA = {k: S_DOOR + A.SPOS[k] for k in range(1, A.N + 1)}      # σκάλα υπογείου: ενιαία γραμμή ανάβασης (τα σκαλιά 1…NL πάνω στο συμπαγές πλατύσκαλο)
LAND0 = 1.20                                     # πλατύσκαλο / χωλ ισογείου (πλάτος 1,20)
sB = {k: sA[A.N] + LAND0 + B.SPOS[k] for k in range(1, B.N + 1)}
LAND1 = B.XTOP - B.WALL1_X                       # πλατύσκαλο Α΄ 1,32
S_END = sB[B.N] + LAND1
Z0 = A.SSL0 - 0.30


def soffit(base, z_from, z_to, s_end):
    """κάτω παρειά πλάκας σκάλας h=15 (κάθετα) από τη γραμμή των εσωτερικών γωνιών base=[(s, z)]· ξεκινά στη στάθμη z_from
    (άνω παρειά του κάτω δαπέδου) και καταλήγει στην κάτω παρειά z_to του πάνω πλατύσκαλου."""
    off = []
    for i, (s, z) in enumerate(base):
        a = base[max(0, i - 1)]; b = base[min(len(base) - 1, i + 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); off.append((s + H * math.sin(ang), z - H * math.cos(ang)))
    mid = [p for p in off if z_from + 1e-3 < p[1] < z_to - 1e-3]
    i0 = off.index(mid[0]); i1 = off.index(mid[-1])
    def cut(p, q, z): return (p[0] + (z - p[1]) * (q[0] - p[0]) / (q[1] - p[1]), z)
    lo = cut(off[i0 - 1], off[i0], z_from) if i0 > 0 else cut(off[i0], off[i0 + 1], z_from)
    hi = cut(off[i1], off[i1 + 1], z_to) if i1 + 1 < len(off) else cut(off[i1 - 1], off[i1], z_to)
    return [lo] + mid + [hi, (s_end, z_to)]


def draw(sh):
    v = View(sh, 22.0, 268.0, 0.0, Z0, SC, flip=True)
    def poly(pts, w, color, fill): v.poly(pts, w, color, fill)
    # ---------- κοιτόστρωση υπογείου
    poly([(0, A.SSL0), (sA[A.NL + 1] + 2.2, A.SSL0), (sA[A.NL + 1] + 2.2, Z0), (0, Z0)], 0, (1, 1, 1), (0.86, 0.86, 0.86)); v.line((0, A.SSL0), (sA[A.NL + 1] + 2.2, A.SSL0), 0.9)
    v.text(sA[A.NL + 1] + 1.1, A.SSL0 - 0.20, "ΚΟΙΤΟΣΤΡΩΣΗ ΥΠΟΓΕΙΟΥ", size=5.6, color=GRAY, align="center")
    # ---------- σκάλα υπογείου: σκαλί + υπερυψωμένο πλατύσκαλο (γέμισμα μπετού) + σκάλα + Π6 ισογείου
    s3 = sA[A.NL + 1]; sN = sA[A.N]; e0 = sN + LAND0
    lob_c = [(sA[1], A.SSL0)]; lob_f = [(0, A.FFL0), (sA[1], A.FFL0)]
    for k in range(1, A.NL + 1):
        nx = sA[k + 1]; lob_c += [(sA[k], A.SSL[k]), (nx, A.SSL[k])]; lob_f += [(sA[k], A.FFL[k]), (nx, A.FFL[k])]
    poly(lob_c + [(s3, A.SSL0)], 0.9, BLACK, (0.88, 0.86, 0.80))
    top = [(s3, A.SSL[A.NL])]
    for k in range(A.NL + 1, A.N):
        top += [(sA[k], A.SSL[k]), (sA[k + 1], A.SSL[k])]
    top += [(sN, A.SSL1), (e0, A.SSL1)]
    base = [(sA[k], A.SSL[k - 1]) for k in range(A.NL + 1, A.N + 1)]
    und = soffit(base, A.SSL[A.NL], A.SSL1 - H, e0)
    poly(top + und[::-1], 1.0, BLACK, CONC)
    # ---------- σκάλα ισογείου → Α΄ (πάνω στην Π6 +0,30) + Π6 Α΄
    e1 = S_END
    top = [(e0, B.SSL0), (sB[1], B.SSL0)]
    for k in range(1, B.N):
        top += [(sB[k], B.SSL[k]), (sB[k + 1], B.SSL[k])]
    top += [(sB[B.N], B.SSL1), (e1, B.SSL1)]
    base = [(sB[k], B.SSL[1] - B.RISE if k == 1 else B.SSL[k - 1]) for k in range(1, B.N + 1)]      # k=1: νοητή γωνία, ώστε η πλάκα να έχει σταθερή κλίση
    def fill(pts): poly(pts, 0, FILLC, FILLC)
    fill([(sN, A.SSL1), (sB[1], A.SSL1), (sB[1], A.FFL1), (sN, A.FFL1)])                           # γέμισμα χωλ ισογείου (πριν από τη σκάλα: το πόδι της περνά μέσα του)
    kick = B.SSL[1] - B.RISE - H > B.SSL0 + 1e-6            # χοντρό γέμισμα: η πλάκα της σκάλας ξεκινά ΠΑΝΩ από την πλάκα του χωλ, με πόδι μέσα στο γέμισμα
    und = soffit(base, B.SSL0 if kick else B.SSL0 - H, B.SSL1 - H, e1)
    poly(top + und[::-1] + ([] if kick else [(e0, B.SSL0 - H)]), 1.0, BLACK, CONC)
    # ---------- γεμίσματα / επενδύσεις (ανάμεσα στο μπετό και το τελικό)
    fill([(0, A.SSL0), (sA[1], A.SSL0), (sA[1], A.FFL0), (0, A.FFL0)])
    for k in range(1, A.N): fill([(sA[k], A.SSL[k]), (sA[k + 1], A.SSL[k]), (sA[k + 1], A.FFL[k]), (sA[k], A.FFL[k])])
    for k in range(1, B.N): fill([(sB[k], B.SSL[k]), (sB[k + 1], B.SSL[k]), (sB[k + 1], B.FFL[k]), (sB[k], B.FFL[k])])
    fill([(sB[B.N], B.SSL1), (e1, B.SSL1), (e1, B.FFL1), (sB[B.N], B.FFL1)])
    # ξαναπερνάμε τις γραμμές μπετού που σκεπάστηκαν και σχεδιάζουμε το τελικό
    conc = [(0, A.SSL0)] + lob_c
    for k in range(A.NL + 1, A.N): conc += [(sA[k], A.SSL[k]), (sA[k + 1], A.SSL[k])]
    conc += [(sN, A.SSL1), (sB[1], B.SSL0)]
    for k in range(1, B.N): conc += [(sB[k], B.SSL[k]), (sB[k + 1], B.SSL[k])]
    conc += [(sB[B.N], B.SSL1), (e1, B.SSL1)]
    v.poly(conc, 1.0, BLACK, None, close=False)
    fin = lob_f
    for k in range(A.NL + 1, A.N): fin += [(sA[k], A.FFL[k]), (sA[k + 1], A.FFL[k])]
    fin += [(sN, A.FFL1), (sB[1], B.FFL0)]
    for k in range(1, B.N): fin += [(sB[k], B.FFL[k]), (sB[k + 1], B.FFL[k])]
    fin += [(sB[B.N], B.FFL1), (e1, B.FFL1)]
    v.poly(fin, 0.7, FIN, None, close=False)
    sh.flush()

    # ---------- αρίθμηση (όπως οι κατόψεις) + στάθμες ανά πάτημα: κόκκινο μπετό, καφέ τελικό
    def num(s, z, lab): sh.ocircle(v.X(s), v.Y(z) - 6.6, 4.5, 0.4, BLACK, (1, 1, 1)); sh.otext(v.X(s), v.Y(z) - 4.4, str(lab), size=6.0, bold=True, align="center")
    def tread(sa, sb, zc, zf, lab):
        xm = (v.X(sa) + v.X(sb)) / 2; y = v.Y(zf)
        num((sa + sb) / 2, zf, lab)
        sh.otext(xm - 1.2, y - 13.5, lv(zc), size=6.0, bold=True, color=RED, rot=90)
        sh.otext(xm + 6.2, y - 13.5, lv(zf), size=6.0, color=FIN, rot=90)
    num(sA[1] - 0.22, A.FFL0, 1)
    for k in range(1, A.N): tread(sA[k], sA[k + 1], A.SSL[k], A.FFL[k], k + 1)
    num(sB[1] - 0.22, B.FFL0, 1)
    for k in range(1, B.N): tread(sB[k], sB[k + 1], B.SSL[k], B.FFL[k], k + 1)
    # ---------- στάθμες δαπέδων / πλατύσκαλων (πάντα και οι δύο: μπετό + τελικό)
    def two(s, zc, zf, right=True, dy=0):
        level_mark(sh, v.X(s), v.Y(zf), lv(zf) + " τελικό", 7.4, FIN, right=right)
        x = v.X(s) + (40 if right else -40) * 0 ; yy = v.Y(zc) + 12 + dy
        sh.otext(v.X(s) + (0 if right else 0), yy, lv(zc) + " μπετό", size=7.4, bold=True, color=RED, align="left" if right else "right")
    sh.otext(v.X(0.02), v.Y(A.FFL0) - 25, lv(A.FFL0) + " τελικό", size=7.4, bold=True, color=FIN); sh.otext(v.X(0.02), v.Y(A.FFL0) - 15.5, lv(A.SSL0) + " μπετό", size=7.4, bold=True, color=RED)
    sh.otext(v.X(0.02), v.Y(A.FFL0) - 35, "ΥΠΟΓΕΙΟ", size=7.6, bold=True)
    v.text((sA[1] + s3) / 2, A.SSL0, "συμπαγές 1–%d" % A.NL, size=5.0, bold=True, dy=-5, align="center")
    # ισόγειο: το ΚΟΙΝΟ πλατύσκαλο των δύο σκαλών
    xm = (sN + sB[1]) / 2
    sh.orect(v.X(sN) + 3, v.Y(A.FFL1) - 53, v.X(sB[1]) - 3, v.Y(A.FFL1) - 17, 0.9, RED, (1, 1, 1))
    v.text(xm, A.FFL1, "ΧΩΛ ΙΣΟΓΕΙΟΥ", size=7.6, bold=True, dy=-43, align="center")
    v.text(xm, A.FFL1, lv(A.FFL1) + " τελικό", size=7.6, bold=True, color=FIN, dy=-33, align="center")
    v.text(xm, A.FFL1, lv(A.SSL1) + " μπετό", size=7.6, bold=True, color=RED, dy=-23, align="center")
    v.text(xm, (A.SSL1 + A.FFL1) / 2, "γέμισμα %s" % cm(A.FFL1 - A.SSL1, 0), size=5.8, dy=2.0, align="center")
    v.text(xm, A.SSL1 - H / 2, "Π6 h=15", size=5.6, bold=True, dy=2.0, align="center")
    # Α΄ όροφος
    xm = (sB[B.N] + e1) / 2
    v.text(xm, B.FFL1, "ΠΛΑΤΥΣΚΑΛΟ Α΄", size=7.6, bold=True, dy=-27, align="center")
    v.text(xm, B.FFL1, lv(B.FFL1) + " τελικό", size=7.6, bold=True, color=FIN, dy=-17, align="center")
    v.text(xm, B.FFL1, lv(B.SSL1) + " μπετό", size=7.6, bold=True, color=RED, dy=-7, align="center")
    v.text(xm, (B.SSL1 + B.FFL1) / 2, "γέμισμα %s" % cm(B.FFL1 - B.SSL1, 0), size=5.6, dy=2.0, align="center")
    v.text(xm, B.SSL1 - H / 2, "Π6 h=15", size=5.6, bold=True, dy=2.0, align="center")
    # ---------- ρίχτια ΜΠΕΤΟΥ που διαφέρουν (πρώτο / τελευταίο κάθε σκάλας)
    def rz(s, za, zb, side=1):
        xo = v.X(s) + side * 3.2; sh.oline(xo, v.Y(za), xo, v.Y(zb), 0.4, RED); sh.tick(xo, v.Y(za), RED); sh.tick(xo, v.Y(zb), RED)
        t = cm(zb - za); sh.otext(xo + (2.0 if side > 0 else -2.0), (v.Y(za) + v.Y(zb)) / 2 + 2.2, t, size=5.6, bold=True, color=RED, align="left" if side > 0 else "right")
    rz(sA[1], A.SSL0, A.SSL[1], -1)                             # 1ο ρίχτι μπετού της σκάλας υπογείου (από την κοιτόστρωση)
    rz(sA[A.KL + 1], A.SSL[A.KL], A.SSL1, 1)        # τελευταίο ρίχτι μπετού της σκάλας υπογείου (φτάνει στην πλάκα)
    if A.BUILT: v.text(sA[A.N] - 0.05, A.SSL1 - H - 0.16, "σκαλιά %d–%d χτιστά πάνω στην πλάκα" % (A.KL + 2, A.N), size=5.0, bold=True, dy=0, align="left")
    rz(sB[1], B.SSL0, B.SSL[1], 1)                              # 1ο ρίχτι μπετού της σκάλας προς Α΄
    rz(sB[B.N], B.SSL[B.N - 1], B.SSL1, 1)
    # το ρίχτι 19 της σκάλας υπογείου γίνεται μέσα στο γέμισμα
    # ---------- διαστάσεις
    yb = Z0
    v.hdim([sA[1], s3], yb, off=10, side=1, vals=["%d × %s" % (A.NL, cm(A.G))], size=6.6)
    v.hdim([s3, sN], yb, off=10, side=1, vals=["%d πατήματα × %s = %s m στη γραμμή ανάβασης" % (A.NS - 1, cm(A.G), mt(round(sN - s3, 3)))], size=6.8)
    v.hdim([sN, sB[1]], yb, off=10, side=1, vals=[mt(LAND0)], size=6.6)
    v.hdim([sB[1], sB[B.N]], yb, off=10, side=1, vals=["%d πατήματα × %s = %s m στη γραμμή ανάβασης" % (B.N - 1, cm(B.G), mt(round(sB[B.N] - sB[1], 3)))], size=6.8)
    v.hdim([sB[B.N], e1], yb, off=10, side=1, vals=[mt(LAND1)], size=6.6)
    for s in (sA[1], s3, sN, sB[1], sB[B.N], e1): sh.oline(v.X(s), v.Y(yb) + 12, v.X(s), v.Y(yb) + 2, 0.2, GRAY)
    for s, z in ((sN, A.SSL1 - H), (sB[1], A.SSL1 - H), (sB[B.N], B.SSL1 - H), (e1, B.SSL1 - H)): sh.oline(v.X(s), v.Y(yb) + 2, v.X(s), v.Y(z) + 3, 0.18, GRAY, "[1 2.5] 0")
    v.vdim([A.FFL0, A.FFL1], e1, off=14, side=1, color=FIN, vals=["ΥΠΟΓΕΙΟ → ΙΣΟΓΕΙΟ:  %d ρίχτια × %s = %s m" % (A.N, cm(A.RISE, 2), mt(A.FFL1 - A.FFL0))])
    v.vdim([B.FFL0, B.FFL1], e1, off=14, side=1, color=FIN, vals=["ΙΣΟΓΕΙΟ → Α΄:  %d ρίχτια × %s = %s m" % (B.N, cm(B.RISE, 2), mt(B.FFL1 - B.FFL0))])
    for z in (A.FFL0, A.FFL1, B.FFL1): sh.oline(v.X(s3 + 0.9) if z == A.FFL0 else v.X(e1), v.Y(z), v.X(e1) + 17, v.Y(z), 0.18, FIN, "[1 2.5] 0")
    sh.oline(v.X(e0), v.Y(A.FFL1), v.X(e1), v.Y(A.FFL1), 0.18, FIN, "[1 2.5] 0")
    sh.flush()
    # ---------- τίτλος (πάνω αριστερά, στο κενό) – ελάχιστα στοιχεία
    x = 12 * MM; y = 20 * MM
    sh.otext(x, y, "ΣΚ", size=26, bold=True)
    sh.otext(x + 21 * MM, y - 4.6 * MM, "ΣΚΑΛΕΣ  ΥΠΟΓΕΙΟ → ΙΣΟΓΕΙΟ → Α΄ ΟΡΟΦΟΣ", size=11.5, bold=True)
    sh.otext(x + 21 * MM, y, "ΕΝΙΑΙΑ ΤΟΜΗ στη γραμμή ανάβασης · 1:%d · Α3 100 %%" % SC, size=8.0)
    y += 9 * MM
    sh.otext(x, y, "ΚΟΚΚΙΝΟ = στάθμη ΜΠΕΤΟΥ", size=7.6, bold=True, color=RED); sh.otext(x + 49 * MM, y, "ΚΑΦΕ = ΤΕΛΙΚΗ στάθμη", size=7.6, bold=True, color=FIN)
    y += 6.5 * MM
    rows = (("", "ρίχτια", "ρίχτι", "πάτημα", "πλάτη"),
            ("Υπόγειο → ισόγειο  (Σ2α)", "%d" % A.N, cm(A.RISE, 2), cm(A.G), "1,20 παντού"),
            ("Ισόγειο → Α΄  (Σ3β)", "%d" % B.N, cm(B.RISE, 2), cm(B.G), "1,20 παντού"),
            ("Έξω, είσοδος κτιρίου  (−0,45 → %s)" % lv(A.FFL1), "7", cm((A.FFL1 + 0.45) / 7, 1), "", "μελέτη: 5 × 18"))
    cx = (0, 47, 62, 77, 92)
    for i, r in enumerate(rows):
        for j, t in enumerate(r): sh.otext(x + cx[j] * MM, y + i * 4.6 * MM, t, size=7.4 if i else 6.2, bold=bool(i) and j > 0, color=BLACK if i else GRAY)
    y += len(rows) * 4.6 * MM + 1.5 * MM
    for ln in ("Πάτημα στη γραμμή ανάβασης ίδιο σε όλα τα σκαλοπάτια κάθε σκάλας: υπόγειο %s · προς Α΄ %s cm." % (cm(A.G), cm(B.G)), "Οι δύο σκάλες δένουν στο ΙΔΙΟ πλατύσκαλο ισογείου:", "πλάκα Π6 (μπετό) %s  →  γέμισμα %s cm  →  τελικό %s" % (lv(A.SSL1), cm(A.FFL1 - A.SSL1, 0), lv(A.FFL1)),
               "(μελέτη: πλάκα %s · τελικό %s → χωλ %s cm ψηλότερα, 2 σκαλιά ακόμη στην εξωτερική σκάλα)" % (lv(A.SSL1_STUDY), lv(A.FFL_STUDY), cm(A.FFL1 - A.FFL_STUDY, 0))):
        sh.otext(x, y, ln, size=7.0, bold=ln.startswith("πλάκα")); y += 4.0 * MM
    sh.otext(12 * MM, 289 * MM - 4, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓ. ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ  ·  κατόψεις: Σ2α %s · Σ3β %s  ·  %s · %s" % (A.REV, B.REV, REV, DATE), size=6.0, color=GRAY)
    sh.orect(6 * MM, 6 * MM, 414 * MM, 291 * MM, 0.6)
    sh.flush()


FINAL = "ΣΚΑΛΕΣ_υπόγειο_ισόγειο_Α_όροφος_ΤΕΛΙΚΟ_A3.pdf"


def check():
    """τελικός έλεγχος σταθμών / διαστάσεων και των δύο σκαλών – σταματά αν κάτι δεν δένει."""
    e = 1e-6; T = A.T_STEP
    assert abs(A.FFL0 + A.N * A.RISE - A.FFL1) < e and abs(B.FFL0 + B.N * B.RISE - B.FFL1) < e, "άθροισμα ριχτιών"
    assert abs(A.FFL1 - B.FFL0) < e and abs(A.SSL1 - B.SSL0) < e, "πλατύσκαλο ισογείου"
    assert B.RISE <= 0.18 + e and A.RISE <= 0.19 + e, "ρίχτι"       # υπόγειο: 20 ρίχτια × 18,7 (απόφαση Γιάννη 16/11/2026 για μεγαλύτερο πάτημα)
    for M in (A, B):
        g_ = list(M.GOING.values()); assert max(g_) - min(g_) < 0.0015, "πάτημα όχι ίδιο: %s %.4f … %.4f" % (M.__name__, min(g_), max(g_))
    gs = list(A.GOING.values()) + list(B.GOING.values())
    for M in (A, B):
        for k in range(1, M.N): assert abs(M.FFL[k] - (M.FFL0 + k * M.RISE)) < e and abs(M.SSL[k] - min(M.FFL[k] - T, M.SSL1)) < e, (M.__name__, k)
        assert abs(M.XE - M.WX - 1.20) < e and abs(M.YS - M.W1 - 1.20) < e and abs(M.W0 - M.YN - 1.20) < e, "κλάδοι / στροφή 1,20"
        assert min(M.INNER.values()) >= 0.07 - e, "πλάτος στο φανάρι < 7"
    assert B.STRAIGHT[1] - B.WALL_X >= 1.20 - e and B.XTOP - 9.70 >= 1.20 - e and A.RISERS[A.N][0][0] - 9.70 >= 1.20 - e, "πλατύσκαλα 1,20"
    assert min(A.INNER.values()) >= 0.08 - e, "υπόγειο: φάλτσο < 8 cm στο φανάρι"
    hr = headroom(); assert min(v_ for _, v_ in hr) >= 2.20, "ελεύθερο ύψος < 2,20"
    print("ελεύθερο ύψος πάνω από τις μύτες της σκάλας υπογείου (κάτω από τη σκάλα προς Α΄): " + " · ".join("%s %.2f" % (n_, v_) for n_, v_ in hr))
    print("ΕΛΕΓΧΟΣ ΟΚ: ρίχτια %d × %.2f / %d × %.2f cm · πάτημα %.1f–%.1f cm · ισόγειο μπετό %+.2f / τελικό %+.2f · Α΄ %+.2f / %+.2f" % (
        A.N, A.RISE * 100, B.N, B.RISE * 100, min(gs) * 100, max(gs) * 100, A.SSL1, A.FFL1, B.SSL1, B.FFL1))


def headroom():
    """ελεύθερο ύψος πάνω από τις μύτες των σκαλιών της σκάλας υπογείου: κάτω παρειά της σκάλας προς Α΄ (Π9 h=15 κάθετα) / του
    πλατύσκαλου ισογείου, σε 3 διαδρομές γύρω από το φανάρι (60 cm = γραμμή ανάβασης · 30 cm · 2 cm = κολλητά στο φανάρι)."""
    from shapely.geometry import LineString
    out = []
    for name, d in (("γραμμή ανάβασης", 0.60), ("30 cm από το φανάρι", 0.30), ("στο φανάρι", 0.02)):
        pts = [(A.XL, A.W1 + d), (A.WX, A.W1 + d)]
        pts += [(A.WX + d * math.cos(math.radians(90 - i)), A.W1 + d * math.sin(math.radians(90 - i))) for i in range(1, 91)]
        pts += [(A.WX + d * math.cos(math.radians(-i)), A.W0 + d * math.sin(math.radians(-i))) for i in range(0, 91)] + [(A.XL, A.W0 - d)]
        path = LineString(pts)
        def pos(M):
            q = {}
            for k, (a, b) in M.RISERS.items():
                ip = path.intersection(LineString([a, b]))
                if not ip.is_empty: q[k] = path.project(ip if ip.geom_type == "Point" else ip.centroid)
            return q
        qa, qb = pos(A), pos(B); land = B.SSL0 - H
        cor = sorted((qb[j], B.SSL[1] - B.RISE if j == 1 else B.SSL[j - 1]) for j in qb)       # εσωτερικές γωνίες της σκάλας προς Α΄
        def soff(q):
            if q <= cor[0][0]: return land
            for (q0, z0), (q1, z1) in zip(cor[:-1], cor[1:]):
                if q <= q1: return max(land, z0 + (z1 - z0) * (q - q0) / (q1 - q0) - H * math.hypot(q1 - q0, z1 - z0) / (q1 - q0))
            return B.SSL1 - H
        out.append((name, min((soff(qa[k]) if k in qa else land) - A.FFL[k] for k in range(1, A.N))))
    # σκαλιά που πέφτουν (έστω εν μέρει) κάτω από το πλατύσκαλο ισογείου (x < 10,90) και κάτω από τη δοκό Δ9.1 30/50 (λωρίδα 9,50–9,70 στον τοίχο)
    land = B.SSL0 - H; beam = A.SSL1_STUDY - 0.50
    xmin = {k: min(p[0] for p in A._tread_poly(k)) for k in range(1, A.N)}
    out.append(("κάτω από το πλατύσκαλο ισογείου", min(land - A.FFL[k] for k in xmin if xmin[k] < A.XL - 1e-6)))
    out.append(("κάτω από τη Δ9.1 (20 cm στον τοίχο)", min(beam - A.FFL[k] for k in xmin if xmin[k] < 9.70 - 1e-6)))
    return out


def merge(path_sk):
    """ένα PDF Α3 για εκτύπωση: κάτοψη υπογείου · κάτοψη ισογείου → Α΄ · ενιαία τομή (ανάπτυγμα) · τομές Α-Α … ΣΤ-ΣΤ (stair_sections.py, αν έχουν βγει)."""
    out = pymupdf.open()
    extra = sorted(os.path.join(OUT, f) for f in os.listdir(OUT) if f.startswith("ΣΚ_Σκάλες_ΤΟΜΕΣ_A3_") and f.endswith(".pdf"))
    for p_ in [os.path.join(OUT, A.NAME), os.path.join(OUT, B.NAME), path_sk] + extra[-1:]: out.insert_pdf(pymupdf.open(p_))
    out.set_metadata(dict(title="Σκάλες υπόγειο → ισόγειο → Α΄ όροφος – τελικό (Σ2α %s · Σ3β %s · ΣΚ %s)" % (A.REV, B.REV, REV), author="ARKAD Ι.Κ.Ε."))
    out.save(os.path.join(OUT, FINAL), garbage=4, deflate=True); print("->", FINAL, "(%d φύλλα)" % out.page_count)


def main():
    sh = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=SC, page_w=420, page_h=297, sx0=0, sy0=0)
    draw(sh)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, NAME)
    sh.doc.set_metadata(dict(title="ΣΚ – Σκάλες υπόγειο → ισόγειο → Α΄, ενιαία τομή", author="ARKAD Ι.Κ.Ε."))
    sh.doc.save(path, garbage=4, deflate=True)
    print("->", NAME, "· μήκος αναπτύγματος %.2f m = %.0f mm" % (S_END, S_END / SC * 1000))
    print("ισόγειο: μπετό %+.2f · τελικό %+.2f | ρίχτια μπετού Σ2α τελευταίο %.1f · Σ3β 1ο %.1f / τελευταίο %.1f" % (A.SSL1, A.FFL1, (A.SSL1 - A.SSL[A.KL]) * 100, (B.SSL[1] - B.SSL0) * 100, (B.SSL1 - B.SSL[B.N - 1]) * 100))
    check(); merge(path)
    if len(sys.argv) > 1: pymupdf.open(path)[0].get_pixmap(dpi=int(sys.argv[2]) if len(sys.argv) > 2 else 110).save(sys.argv[1])


if __name__ == "__main__":
    main()
