"""ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1 – κάτοψη διαδρομής + ΤΟΜΕΣ (τυπικός όροφος Α΄ · Β΄ · Γ΄ · Δ΄ και ισόγειο) – R02.

Ιδιοκτήτης 18/11/2026: «φτιάξε εσύ το μηχάνημα στο σαλόνι όπως καλύτερα πιστεύεις · μην θεωρήσεις ότι θα περάσεις κάτω από δοκάρια · επίσης
κάνε μου τομές να καταλάβω διαδρομή» → R00 (κανάλι γωνίας πίσω από την πόρτα, συμπυκνώματα στον ΒΑ εξώστη).
R01 (ιδιοκτήτης 18/11/2026: «στα σπίτια που φτιάχνεις το τοιχάκι πίσω από την πόρτα να δούμε άλλη λύση όπου θα φουσκώσεις τον τοίχο της πόρτας όσους
πόντους χρειάζεται μέσα στο σπίτι και έτσι θα έχουμε περάσματα · την αποχέτευση του aircon του σαλονιού να τη συνδέσεις με το σιφώνι του μπροστινού
μπαλκονιού»): οι σωλήνες κατεβαίνουν ΜΕΣΑ στην επένδυση Τ3Α 7,5 cm του τοίχου της πόρτας εισόδου (ψυκτικά βόρεια της πόρτας → δάπεδο Υπν.2 → ΒΑ εξώστης ·
συμπυκνώματα νότια της πόρτας → δάπεδο κατά μήκος του τοίχου → πεσσός Τ1-10 → σιφώνι του μπροστινού εξώστη → ΥΔ2).
R02 (ιδιοκτήτης 18/11/2026 βράδυ: «τον τοίχο που φουσκώσαμε απλά κάνε έναν μεγάλο τοίχο, μην βάζεις πρόσθετο · τα slot να μην φυσάνε προς τα κάτω αλλά προς
τα μπρος»): ο τοίχος της πόρτας σχεδιάζεται ΕΝΑΣ τοίχος Τ6Β 22,5 cm με διπλό σκελετό (όχι Τ6Α 15 + επένδυση 7,5 – ίδια παρειά, ίδια διαδρομή σωλήνων μέσα στο
κανάλι του) · τα slot του μηχανήματος στη ΜΕΤΩΠΗ της λωρίδας (το κατακόρυφο σκαλοπάτι της οροφής): ο αέρας βγαίνει ΟΡΙΖΟΝΤΙΑ προς το καθιστικό.

Όλα διαβάζονται από τα μοντέλα των ανόψεων (b1_anopsi R23 · gf_anopsi R10) και των τοιχοποιιών (Β1 R30) – αν αλλάξει η όδευση εκεί, οι τομές ξαναχτίζονται.
Φύλλα A3: ΚΜ-01 κάτοψη διαδρομής 1:40 · ΚΜ-02 τομή Α-Α κατά μήκος του τοίχου της πόρτας 1:30 (+ το δάπεδο σε μεγέθυνση) · ΚΜ-03 τομή Β-Β μέσα από το
μηχάνημα 1:10 · ΚΜ-04 τομή Γ-Γ έξοδος των ψυκτικών στον ΒΑ εξώστη 1:10 · ΚΜ-05 έξοδος των συμπυκνωμάτων στο μπροστινό μπαλκόνι 1:10 (τομή + κάτοψη) ·
ΚΜ-06 λεπτομέρειες 1:5 (ο τοίχος της πόρτας · ο σωλήνας στο γέμισμα) · ΚΜ-07 ισόγειο.

Χρήση: python3 tomes_km1.py [out.pdf]  →  ΑΝΟΨΕΙΣ/ΚΛΙΜΑΤΙΣΤΙΚΟ_ΣΑΛΟΝΙΟΥ_ΚΜ1_ΤΟΜΕΣ_<REV>.pdf
Συντεταγμένες: m του κοινού συστήματος (x ανατολή, y νότος) · στάθμες από το τελικό δάπεδο του ορόφου (γέμισμα 12 cm).
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import b1_anopsi as A
import gf_anopsi as G
import checks, sheets
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow, new_canvas
from reportlab.pdfbase import pdfmetrics

REV, DATE = "R03", "24/11/2026"
SHOW_NOTES = False   # 24/11/2026 (Γιάννης: «βγάλε από όλα τα σχέδια τις σημειώσεις, να υπάρχουν μόνο σχέδια») – κείμενα / βήματα / πλαίσια-μηνύματα εκτός, μένουν σχέδια + υπόμνημα
OUTDIR = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΑΝΟΨΕΙΣ")
import f4_anopsi as F4
BASE = "Ανόψεις Β1 %s · Δ΄ %s · ισόγειο %s · τοιχοποιίες Β1 %s · γέμισμα δαπέδων 12 cm" % (A.REV, F4.REV, G.REV, A.W.REV)

MM = 72 / 25.4


def scale(n):
    return MM * 1000.0 / n


# ---------------------------------------------------------------- χρώματα
MAG = (0.80, 0.10, 0.50)
MAG_F = (0.97, 0.80, 0.90)
ORANGE = (0.86, 0.45, 0.04)
ORANGE_F = (0.99, 0.88, 0.70)
BLUE = (0.05, 0.36, 0.66)
BLUE2 = (0.25, 0.55, 0.75)
BLUE_F = (0.82, 0.90, 0.98)
RAIN = (0.15, 0.45, 0.80)
GREEN = (0.05, 0.52, 0.42)
CABLE = (0.10, 0.45, 0.30)
BEAMC = (0.62, 0.30, 0.16)
RED = (0.78, 0.10, 0.12)
CONC = (0.74, 0.74, 0.76)
CONC_H = (0.50, 0.50, 0.53)
CONC_L = (0.90, 0.90, 0.92)
BRICK = (0.86, 0.56, 0.42)
BRICK_H = (0.62, 0.32, 0.22)
GYP = (0.80, 0.87, 0.95)
GYP_S = (0.30, 0.42, 0.58)
FILLC = (0.94, 0.90, 0.80)
FILL_H = (0.70, 0.62, 0.45)
ETICS = (0.99, 0.94, 0.70)
ETICS_S = (0.72, 0.60, 0.20)
WOOD = (0.97, 0.94, 0.88)
WOOD_S = (0.62, 0.52, 0.38)
LIN_F = (0.74, 0.90, 0.88)                     # ο τοίχος της πόρτας εισόδου (Τ6Β) – οι γυψοσανίδες του προς το σπίτι
LIN_S = (0.08, 0.48, 0.48)
WALL_BG = (0.965, 0.962, 0.955)
WHITE = (1, 1, 1)

# ---------------------------------------------------------------- στοιχεία από τα μοντέλα (τυπικός όροφος)
W = A.W
FILL = A.COND_FILL["fill"]                      # γέμισμα δαπέδου 12 cm
TOP = A.TOP_SLAB                                # πάνω παρειά πλάκας οροφής +2,98
SOF8, SOF3, SOF6 = A.SLABS["Π8 h20"], A.SLABS["Π3 h18"], A.SLABS["Π6 h15"]
BEAM = {b[0]: b for b in A.BEAMS}
ZL = {z["id"]: z["level"] for z in A.ZONES}
LV_LIV, LV_STRIP, LV_BED, LV_B50, LV_STAIR, LV_PSB = ZL["Ζ1"], ZL["Ζ2"], ZL["Ζ10"], ZL["Ζ11"], ZL["Ζ12"], ZL["Ζ13"]
UNIT = A.UNITS[0]
UX0, UY0, UX1, UY1 = UNIT["rect"]
U_TOP = SOF8 - A.HANG
U_BOT = U_TOP - UNIT["hmax"]
PLEN = A.DUCTS[0][1]
SLOT = [d for d in A.DIFFUSERS if d["kind"] == "front"]      # R02: slot στη ΜΕΤΩΠΗ της λωρίδας (φυσάνε οριζόντια)
SLOT_Z = A.SLOT_Z                                # κάτω / πάνω άκρο του slot μέσα στη μετώπη (+2,52 … +2,64)
RET = [d for d in A.DIFFUSERS if d["kind"] == "ret"][0]["rect"]
HATCH = A.HATCHES[0]["rect"]
LIN_X, LIN_CAV = A.LIN_X, A.LIN_CAV                # παρειά του τοίχου της πόρτας προς το σπίτι (9,325) · καθαρό βάθος του καναλιού του (5 cm)
DR, DC = A.DROP_R, A.DROP_C                    # κατεβάσματα μέσα στον τοίχο: ψυκτικά (βόρεια παραστάδα) · συμπυκνώματα (νότια παραστάδα)
KX, CX = A.KM1_X, A.COND_X                      # άξονες μέσα στο γέμισμα: ψυκτικά (Α τοίχος Υπν.2) · συμπυκνώματα (τοίχος της εισόδου)
STRIP_X = A.STRIP_X
WARD = [r for n, r in A.TALL if n == "ντουλάπα Υπν.2"][0]
KR2 = [c for c in A.CURTAINS if c["id"] == "ΚΡ2"][0]["rect"]
EM = A.OUTDOOR_T
GULLY_NE = [(9.93, 0.98), (9.75, 0.90), (9.75, 0.615)]     # σιφώνι ΒΑ εξώστη → ΥΔ1 (τεύχος αποχετεύσεων) – μόνο ως υπόβαθρο
YD1 = (9.75, 0.57)                              # υδρορροή ΥΔ1
GS = A.GULLY_S                                  # σιφώνι του μπροστινού (νότιου) εξώστη – εκεί καταλήγουν τα συμπυκνώματα
GULLY = A.EXIT_GULLY                            # Φ50 του σιφωνιού → ΥΔ2
YD2 = (GULLY[-1][0], 9.51)                      # υδρορροή ΥΔ2
EXIT_Y = A.KM1_FLOOR[2][1]                      # y εξόδου των ψυκτικών από τον πεσσό Τ1-05 (1,20)
EXIT_Z = A.KM1_EXIT_Z
PX, PY0, PY1 = A.COND_WALL                      # διέλευση συμπυκνωμάτων από τη βάση του πεσσού Τ1-10: x · εσωτ. παρειά · έξω από τη θερμοπρόσοψη
R_GAS, R_LIQ, R_CON = A.REFR_PIPE["od"] / 2, A.REFR_PIPE["od_liq"] / 2, A.COND_FILL["od"] / 2
Z_REF = -FILL + R_GAS + 0.004                   # άξονας ψυκτικών μέσα στο γέμισμα (πάνω στην πλάκα, μέσα σε σπιράλ)
COVER, SLOPE = A.COND_FILL["cover"], A.COND_FILL["slope"]


def wall(i, model=None):
    w = [w_ for w_ in (model or W).WALLS if w_["id"] == i][0]
    xs = [p[0] for p in w["pts"]]; ys = [p[1] for p in w["pts"]]
    return round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)


T206, T105, T306, T104 = wall("T2-06"), wall("T1-05"), wall("T3-06"), wall("T1-04")
T106 = wall("T1-06")
# R02: ο τοίχος της πόρτας εισόδου είναι ΕΝΑΣ τοίχος Τ6Β 22,5 cm (τοιχοποιίες Β1 R30) – βόρεια / νότια παραστάδα. Στρώσεις από το σπίτι προς το κλιμακοστάσιο:
# 2 γυψοσανίδες (LIN_X … +0,025) · ΚΑΝΑΛΙ = σκελετός CW 50 (… BF) · κενό 2,5 (BF … +0,025) · σκελετός CW 100 με πετροβάμβακα · 2 πυράντοχες (… WE)
WALL_N, WALL_S = wall("T6B-01"), wall("T6B-02")
BF = A.W.CHAN_X[1]                              # 9,40: δυτική παρειά της δοκού Δ9.1 = ανατολικό άκρο του καναλιού
WE = WALL_S[2]                                  # 9,55: παρειά του τοίχου προς το κλιμακοστάσιο
BRD, GAPW = 0.025, 0.025                        # δύο γυψοσανίδες · κενό ανάμεσα στους δύο σκελετούς
assert abs(WALL_S[0] - LIN_X) < 1e-9 and abs(BF - LIN_X - BRD - LIN_CAV) < 1e-9 and abs(WE - BF - GAPW - 0.10 - BRD) < 1e-9
WU_N, WU_S = (BF, WALL_N[1], WE, WALL_N[3]), (BF, WALL_S[1], WE, WALL_S[3])         # το μέρος του τοίχου ΚΑΤΩ από τη δοκό (κενό + CW 100 + πυράντοχες)
WC_N, WC_S = (LIN_X, WALL_N[1], BF, WALL_N[3]), (LIN_X, WALL_S[1], BF, WALL_S[3])   # το μέρος ΔΙΠΛΑ στη δοκό (2 γυψοσανίδες + κανάλι)
ROCK, ROCK_H = (0.98, 0.95, 0.80), (0.80, 0.70, 0.35)                                # σκελετός με πετροβάμβακα
FIRE_F, FIRE_S = (0.74, 0.86, 0.78), (0.25, 0.45, 0.35)                               # πυράντοχη γυψοσανίδα
T110, T309 = wall("T1-10"), wall("T3-09")       # πεσσός τούβλου ανάμεσα στο W2.02 και την Κ8 · η επένδυσή του
K3 = (9.40, 3.00, 9.70, 5.15)
K8 = (9.00, 9.15, 9.70, 9.45)
FIN = (8.95, 9.55, 9.15, 11.15)                 # τοιχείο του μπροστινού εξώστη (σκυρόδεμα)
W206 = (9.45, 1.38, 9.70, 2.38)                 # μπαλκονόπορτα W2.06
W202 = (4.10, 9.20, 8.85, 9.45)                 # μπαλκονόπορτα καθιστικού W2.02
DOOR = (5.30, 6.30)                             # πόρτα εισόδου (y)
BALC = (9.80, 0.65, 11.45, 2.70)                # δάπεδο ΒΑ εξώστη
PAR_E = (11.25, 0.85, 11.45, 2.65)              # ανατολικό στηθαίο (σκυρόδεμα)
PAR_N = (9.80, 0.65, 11.45, 0.85)               # βόρειο στηθαίο
BALC_Z = -0.02                                  # τελικό δάπεδο εξώστη ως προς το εσωτερικό (εξώστες 2 cm χαμηλότερα – παραδοχή)
ET_S = 9.55                                     # εξωτερική παρειά της θερμοπρόσοψης στη νότια όψη

# συμπυκνώματα μέσα στο γέμισμα: μήκος κατά μήκος της όδευσης ↔ προβολή y (η όδευση πάει μονότονα προς νότο)
_CF = A.COND_FLOOR
_CD = [0.0]
for _a, _b in zip(_CF, _CF[1:]):
    _CD.append(_CD[-1] + math.hypot(_b[0] - _a[0], _b[1] - _a[1]))


def cond_inv(d):
    """Ροή (κάτω παρειά) των συμπυκνωμάτων μέσα στο γέμισμα σε μήκος d από το κατέβασμα, από το τελικό δάπεδο."""
    return -(COVER + 2 * R_CON + SLOPE * d)


def cond_d(y):
    """Μήκος της όδευσης στο γέμισμα ως το σημείο με προβολή y."""
    for a_, b_, d0 in zip(_CF, _CF[1:], _CD):
        if a_[1] - 1e-9 <= y <= b_[1] + 1e-9:
            t = 0.0 if abs(b_[1] - a_[1]) < 1e-9 else (y - a_[1]) / (b_[1] - a_[1])
            return d0 + t * math.hypot(b_[0] - a_[0], b_[1] - a_[1])
    return _CD[-1] if y > _CF[-1][1] else 0.0


def cond_zy(y):
    return cond_inv(cond_d(y))


Z_C_START = cond_inv(0)                         # ροή στην αρχή (ράχη 3 cm κάτω από το τελικό δάπεδο)
Z_C_WALL = cond_zy(PY0)                         # ροή στην εσωτερική παρειά του νότιου τοίχου
Z_C_END = A.COND_END                            # ροή στο σιφώνι του εξώστη
assert 0.033 <= FILL + cond_zy(8.80) and FILL + cond_zy(7.75) <= 0.046, "άλλαξε το ύψος του Ø 32 στο άνοιγμα της κουζίνας – διόρθωσε το κείμενο «3,5 – 4,5 cm»"
Z_C_VOID_END = LV_STRIP + 0.0125 + A.COND_PIPE["od"] / 2      # άξονας συμπυκνωμάτων στο κενό, στο κατέβασμα
Z_C_VOID_START = Z_C_VOID_END + 0.01 * A._CLEN                # στην έξοδο της μονάδας (κλίση 1 %)
Z_R_VOID = 2.63                                                # άξονας ψυκτικών στο κενό (δεμένα ψηλά)
R_VOID_LEN = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(A.KM1_VOID, A.KM1_VOID[1:]))
R_FLOOR_LEN = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(A.KM1_FLOOR[:3], A.KM1_FLOOR[1:3]))
C_FLOOR_LEN = _CD[-1]


def cm(v):
    return ("%.1f" % (v * 100)).rstrip("0").rstrip(".").replace(".", ",")


def mm2(v):
    return ("%.2f" % (v + 1e-9)).replace(".", ",")


def lv(v, nd=2):
    s = ("%+." + str(nd) + "f") % v
    if abs(v) < 0.5 * 10 ** -nd:
        s = "±" + ("%." + str(nd) + "f") % 0
    return s.replace(".", ",")


# ================================================================ όψη τομής
class Sec:
    """Τομή: u οριζόντια θέση (m), z στάθμη από το τελικό δάπεδο (m, προς τα πάνω). sz = κατακόρυφη κλίμακα (αν διαφέρει)."""

    def __init__(self, c, ox, oy, s, u0=0.0, sz=None, brk=None):
        self.c, self.ox, self.oy, self.s, self.u0, self.sz = c, ox, oy, s, u0, sz or s
        self.brk = brk          # (zl, zh, gap): το ύψος zl…zh παραλείπεται (σπάσιμο τομής), gap σε pt

    def p(self, u, z):
        X = self.ox + (u - self.u0) * self.s
        if not self.brk:
            return X, self.oy + z * self.sz
        zl, zh, gap = self.brk
        if z <= zl:
            return X, self.oy + z * self.sz
        if z >= zh:
            return X, self.oy + zl * self.sz + gap + (z - zh) * self.sz
        return X, self.oy + zl * self.sz + gap * (z - zl) / (zh - zl)

    def break_band(self, u0, u1, ext=14):
        """Λευκή λωρίδα + δύο γραμμές σπασίματος εκεί που παραλείπεται το ύψος."""
        c = self.c
        zl, zh, gap = self.brk
        X0, Y0 = self.p(u0, zl); X1, Y1 = self.p(u1, zh)
        c.setFillColorRGB(1, 1, 1); c.rect(X0 - ext, Y0, X1 - X0 + 2 * ext, Y1 - Y0, stroke=0, fill=1)
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.6)
        for Y in (Y0, Y1):
            pth = c.beginPath(); x = X0 - ext; pth.moveTo(x, Y); k = 0
            while x < X1 + ext:
                x += 9; pth.lineTo(min(x, X1 + ext), Y + (2.2 if k % 2 == 0 else -2.2)); k += 1
            c.drawPath(pth, stroke=1, fill=0)
        c.setFont("Inter", 5.2); c.setFillColorRGB(*GREY)
        c.drawRightString(X1 - 6, (Y0 + Y1) / 2 - 1.8, "(το ενδιάμεσο ύψος του χώρου παραλείπεται)")

    def rect(self, u0, z0, u1, z1, fill=None, stroke=None, lw=0.5, dash=None):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0), stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def poly(self, pts, fill=None, stroke=None, lw=0.5, close=True, dash=None):
        c = self.c
        pth = c.beginPath()
        pth.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*self.p(*q))
        if close: pth.close()
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.drawPath(pth, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def line(self, u0, z0, u1, z1, color=DARK, lw=0.5, dash=None):
        c = self.c
        c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        c.line(*self.p(u0, z0), *self.p(u1, z1))
        c.setDash([])

    def pipe(self, pts, color, lw=2.0, dash=None, halo=True):
        c = self.c
        c.saveState(); c.setLineJoin(1); c.setLineCap(1)
        for col, w_, d_ in ((WHITE, lw + 1.8, None), (color, lw, dash)) if halo else ((color, lw, dash),):
            pth = c.beginPath(); pth.moveTo(*self.p(*pts[0]))
            for q in pts[1:]:
                pth.lineTo(*self.p(*q))
            c.setStrokeColorRGB(*col); c.setLineWidth(w_); c.setDash(d_ or [])
            c.drawPath(pth, stroke=1, fill=0)
        c.restoreState()

    def circle(self, u, z, r, fill=None, stroke=None, lw=0.6, dash=None, pt=False):
        c = self.c
        X, Y = self.p(u, z)
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.circle(X, Y, r if pt else r * self.s, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def text(self, u, z, s, size=6, font="Inter", color=DARK, anchor="c", rot=0, bg=False, dx=0, dy=0):
        c = self.c
        X, Y = self.p(u, z)
        c.saveState(); c.translate(X + dx, Y + dy); c.rotate(rot)
        w = pdfmetrics.stringWidth(s, font, size)
        off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
        if bg:
            c.setFillColorRGB(1, 1, 1); c.rect(off - 1.6, -size * 0.36 - 1.4, w + 3.2, size + 2.2, stroke=0, fill=1)
        c.setFont(font, size); c.setFillColorRGB(*color)
        c.drawString(off, -size * 0.36, s)
        c.restoreState()

    def hatch(self, u0, z0, u1, z1, step=5.0, ang=45, color=CONC_H, lw=0.3):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        c.saveState()
        pth = c.beginPath(); pth.rect(x0, y0, x1 - x0, y1 - y0); c.clipPath(pth, stroke=0, fill=0)
        c.setStrokeColorRGB(*color); c.setLineWidth(lw)
        t = math.tan(math.radians(ang))
        h = y1 - y0
        k = x0 - h / t - step
        while k < x1 + step:
            c.line(k, y0, k + h / t, y1)
            k += step
        c.restoreState()

    def dots(self, u0, z0, u1, z1, step=5.0, color=FILL_H, r=0.35):
        c = self.c
        x0, y0 = self.p(u0, z0); x1, y1 = self.p(u1, z1)
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        c.saveState()
        pth = c.beginPath(); pth.rect(x0, y0, x1 - x0, y1 - y0); c.clipPath(pth, stroke=0, fill=0)
        c.setFillColorRGB(*color)
        j = 0
        yy = y0 + step / 2
        while yy < y1:
            xx = x0 + (step / 2 if j % 2 else step)
            while xx < x1:
                c.circle(xx, yy, r, stroke=0, fill=1)
                xx += step
            yy += step * 0.8; j += 1
        c.restoreState()

    def bricks(self, u0, z0, u1, z1, course=0.065, color=BRICK_H, lw=0.25):
        z = z0
        while z < z1 - 1e-6:
            self.line(u0, z, u1, z, color=color, lw=lw)
            z += course

    # ---- υλικά
    def concrete(self, pts):
        self.poly(pts, fill=CONC)
        us = [q[0] for q in pts]; zs = [q[1] for q in pts]
        c = self.c
        c.saveState()
        pth = c.beginPath(); pth.moveTo(*self.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*self.p(*q))
        pth.close(); c.clipPath(pth, stroke=0, fill=0)
        self.hatch(min(us), min(zs), max(us), max(zs), step=5.5)
        c.restoreState()
        self.poly(pts, stroke=DARK, lw=0.8)

    def concrete_r(self, u0, z0, u1, z1):
        self.concrete([(u0, z0), (u1, z0), (u1, z1), (u0, z1)])

    def fill_r(self, u0, u1, z0=None, z1=0.0):
        z0 = -FILL if z0 is None else z0
        self.rect(u0, z0, u1, z1, fill=FILLC)
        self.dots(u0, z0, u1, z1)
        self.line(u0, z1, u1, z1, color=DARK, lw=0.9)

    def brick_r(self, u0, z0, u1, z1):
        self.rect(u0, z0, u1, z1, fill=BRICK)
        self.bricks(u0, z0, u1, z1)
        self.rect(u0, z0, u1, z1, stroke=DARK, lw=0.7)

    def gyp_r(self, u0, z0, u1, z1, lw=0.6):
        self.rect(u0, z0, u1, z1, fill=GYP, stroke=GYP_S, lw=lw)

    def etics_r(self, u0, z0, u1, z1):
        self.rect(u0, z0, u1, z1, fill=ETICS, stroke=ETICS_S, lw=0.5)

    def board(self, u0, u1, z, down=True, t=0.0125):
        """Γυψοσανίδα οροφής (τελική στάθμη z = κάτω επιφάνεια) + σκελετός από πάνω."""
        self.rect(u0, z, u1, z + t, fill=WHITE, stroke=DARK, lw=0.7)
        self.line(u0, z + t + 0.027, u1, z + t + 0.027, color=GYP_S, lw=0.35, dash=[3, 1.2])

    # ---- διαστάσεις / στάθμες / σημάνσεις
    def dim_h(self, z, us, size=5.6, above=True, color=DIMC, fmt=mm2, dy=0, tick=3.0, bg=False):
        c = self.c
        us = sorted(us)
        X0, Y = self.p(us[0], z); X1, _ = self.p(us[-1], z)
        Y += dy
        c.setStrokeColorRGB(*color); c.setLineWidth(0.4); c.line(X0, Y, X1, Y)
        for u in us:
            X, _ = self.p(u, z)
            c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(us[:-1], us[1:]):
            s = fmt(b - a)
            Xa, _ = self.p(a, z); Xb, _ = self.p(b, z)
            w = pdfmetrics.stringWidth(s, "Inter", size)
            c.setFont("Inter", size); c.setFillColorRGB(*color)
            if w <= (Xb - Xa) - 3 or bg:
                yt = Y + (2.2 if above else -size - 0.6)
                if bg:          # λευκό φόντο πίσω από την τιμή (όταν η διάσταση περνά πάνω από διαγράμμιση)
                    c.setFillColorRGB(1, 1, 1); c.rect((Xa + Xb) / 2 - w / 2 - 1.5, yt - 1.2, w + 3, size + 1.4, stroke=0, fill=1); c.setFillColorRGB(*color)
                c.drawCentredString((Xa + Xb) / 2, yt, s)
            else:
                c.saveState(); c.translate((Xa + Xb) / 2 + size * 0.35, Y + (4 if above else -4 - w)); c.rotate(90)
                c.drawString(0, 0, s); c.restoreState()

    def dim_v(self, u, zs, size=5.6, left=True, color=DIMC, fmt=mm2, dx=0, tick=3.0):
        c = self.c
        zs = sorted(zs)
        X, Y0 = self.p(u, zs[0]); _, Y1 = self.p(u, zs[-1])
        X += dx
        c.setStrokeColorRGB(*color); c.setLineWidth(0.4); c.line(X, Y0, X, Y1)
        for z in zs:
            _, Y = self.p(u, z)
            c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(zs[:-1], zs[1:]):
            s = fmt(b - a)
            _, Ya = self.p(u, a); _, Yb = self.p(u, b)
            w = pdfmetrics.stringWidth(s, "Inter", size)
            c.setFont("Inter", size); c.setFillColorRGB(*color)
            if w <= (Yb - Ya) - 3:
                c.saveState(); c.translate(X + (-2.2 if left else size + 0.4), (Ya + Yb) / 2); c.rotate(90)
                c.drawCentredString(0, 0, s); c.restoreState()
            else:
                (c.drawRightString if left else c.drawString)(X + (-4 if left else 4), (Ya + Yb) / 2 - size * 0.35, s)

    def level(self, u, z, txt=None, right=True, size=6.2, color=DARK, lead=14, note=None, below=False):
        """Σύμβολο στάθμης: τρίγωνο πάνω στη στάθμη + τιμή (below=True: κάτω από τη γραμμή – για οροφές)."""
        c = self.c
        X, Y = self.p(u, z)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.5)
        d = 1 if right else -1
        k = -1 if below else 1
        if not below:
            c.line(X, Y, X + d * lead, Y)
        c.setFillColorRGB(*color)
        pth = c.beginPath(); pth.moveTo(X + d * 3.2, Y); pth.lineTo(X + d * 6.2, Y + k * 4.2); pth.lineTo(X + d * 0.2, Y + k * 4.2); pth.close()
        c.drawPath(pth, stroke=0, fill=1)
        s = txt or lv(z)
        c.setFont("Inter-Bold", size)
        w = pdfmetrics.stringWidth(s, "Inter-Bold", size)
        if below:
            lead = 7
        tx = X + d * (lead + 2) if right else X - lead - 2 - w
        ty = Y - size - 0.6 if below else Y + 0.6
        c.setFillColorRGB(1, 1, 1); c.rect(tx - 1, ty - 1.4, w + 2, size + 1.6, stroke=0, fill=1)
        c.setFillColorRGB(*color); c.drawString(tx, ty, s)
        if note:
            c.setFont("Inter", size - 1.2); c.setFillColorRGB(*GREY)
            wn = pdfmetrics.stringWidth(note, "Inter", size - 1.2)
            if below:
                c.setFillColorRGB(1, 1, 1)
                c.rect((tx + w + 2) if right else (tx - 4 - wn), ty - 1.2, wn + 3, size + 0.6, stroke=0, fill=1)
                c.setFillColorRGB(*GREY)
            if right:
                c.drawString(tx + w + 3, ty + 0.2, note)
            else:
                c.drawRightString(tx - 3, ty + 0.2, note)

    def badge(self, u, z, n, r=7.0, dx=0, dy=0):
        badge(self.c, self.p(u, z)[0] + dx, self.p(u, z)[1] + dy, n, r)

    def leader(self, a, b, lines, anchor="l", size=6.0, color=DARK, font="Inter-Medium", lh=None, dot=True):
        """Οδηγός από το σημείο a (u, z) ως το b (u, z) και κείμενο στο b (γραμμές προς τα κάτω)."""
        c = self.c
        X0, Y0 = self.p(*a); X1, Y1 = self.p(*b)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.line(X0, Y0, X1, Y1)
        if dot:
            c.setFillColorRGB(*color); c.circle(X0, Y0, 1.3, stroke=0, fill=1)
        lh = lh or size + 1.8
        for i, s in enumerate(lines if isinstance(lines, (list, tuple)) else [lines]):
            f = font if i == 0 else "Inter"
            w = pdfmetrics.stringWidth(s, f, size)
            tx = X1 + 3 if anchor == "l" else (X1 - 3 - w if anchor == "r" else X1 - w / 2)
            ty = Y1 - size * 0.36 - i * lh
            c.setFillColorRGB(1, 1, 1); c.rect(tx - 1.2, ty - 1.2, w + 2.4, size + 2.0, stroke=0, fill=1)
            c.setFont(f, size); c.setFillColorRGB(*color); c.drawString(tx, ty, s)

    def arrow(self, u0, z0, u1, z1, color=BLUE, lw=0.8, head=5.0):
        arrow(self.c, *self.p(u0, z0), *self.p(u1, z1), color=color, lw=lw, head=head)

    def cut_mark(self, u, z0, z1):
        """Γραμμή αποκοπής (η τομή συνεχίζει)."""
        c = self.c
        X, Y0 = self.p(u, z0); _, Y1 = self.p(u, z1)
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.6); c.setDash([7, 2, 1.5, 2]); c.line(X, Y0 - 6, X, Y1 + 6); c.setDash([])


# ---------------------------------------------------------------- βοηθητικά σελίδας
def wall_core(sv, z0, z1, lw=0.7):
    """Τομή του ΕΝΙΑΙΟΥ τοίχου της πόρτας στο μέρος του κάτω από το δοκάρι (x BF…WE): κενό 2,5 cm (ενιαίο με το κανάλι) · σκελετός CW 100 με
    πετροβάμβακα · 2 πυράντοχες γυψοσανίδες προς το κλιμακοστάσιο. Οι 2 γυψοσανίδες προς το σπίτι και το κανάλι σχεδιάζονται από τον καλούντα."""
    sv.rect(BF, z0, BF + GAPW, z1, fill=WHITE)
    sv.rect(BF + GAPW, z0, WE - BRD, z1, fill=ROCK)
    sv.hatch(BF + GAPW, z0, WE - BRD, z1, step=4, ang=60, color=ROCK_H)
    sv.rect(BF + GAPW, z0, WE - BRD, z1, stroke=GYP_S, lw=0.35)
    sv.rect(WE - BRD, z0, WE, z1, fill=FIRE_F, stroke=FIRE_S, lw=lw)
    sv.line(WE - BRD / 2, z0, WE - BRD / 2, z1, color=FIRE_S, lw=0.3)


def arrow(c, x0, y0, x1, y1, color=BLUE, lw=0.8, head=5.0):
    c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash([])
    c.line(x0, y0, x1, y1)
    a = math.atan2(y1 - y0, x1 - x0)
    c.setFillColorRGB(*color)
    pth = c.beginPath(); pth.moveTo(x1, y1)
    pth.lineTo(x1 - head * math.cos(a - 0.38), y1 - head * math.sin(a - 0.38))
    pth.lineTo(x1 - head * math.cos(a + 0.38), y1 - head * math.sin(a + 0.38)); pth.close()
    c.drawPath(pth, stroke=0, fill=1)


def badge(c, X, Y, n, r=7.0, color=DARK):
    c.setFillColorRGB(*color); c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(1.0)
    c.circle(X, Y, r, stroke=1, fill=1)
    c.setFillColorRGB(1, 1, 1); c.setFont("Inter-Bold", r * 1.25)
    c.drawCentredString(X, Y - r * 0.44, str(n))


def wrap(s, font, size, w):
    out, cur = [], ""
    for wd in s.split(" "):
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) > w and cur:
            out.append(cur); cur = wd
        else:
            cur = t
    return out + [cur]


def para(c, x, y, w, s, size=7.0, font="Inter", color=DARK, lead=None, indent=0):
    if not SHOW_NOTES:
        return y
    lead = lead or size + 2.4
    for i, l in enumerate(wrap(s, font, size, w - indent)):
        c.setFont(font, size); c.setFillColorRGB(*color)
        c.drawString(x + indent, y, l); y -= lead
    return y


def head(c, x, y, s, size=9.5, color=DARK):
    if not SHOW_NOTES:
        return y
    return _head(c, x, y, s, size, color)


def _head(c, x, y, s, size=9.5, color=DARK):
    c.setFont("Inter-Bold", size); c.setFillColorRGB(*color); c.drawString(x, y, s)
    return y - size - 5


STEPS = [
    ("ΤΟ ΜΗΧΑΝΗΜΑ ΣΤΗ ΛΩΡΙΔΑ ΤΗΣ ΕΙΣΟΔΟΥ", "ΚΜ1 καναλάτη slim, μέσα στη χαμηλή οροφή 1,10 δίπλα στον τοίχο της εισόδου (οροφή %s = περασιά με τα δοκάρια, κενό %s cm). "
     "Οι συνδέσεις στο βόρειο άκρο της. Ο αέρας βγαίνει ΟΡΙΖΟΝΤΙΑ από τα slot στη μετώπη της λωρίδας, προς το καθιστικό." % (lv(LV_STRIP), cm(SOF8 - LV_STRIP))),
    ("Ο ΤΟΙΧΟΣ ΤΗΣ ΠΟΡΤΑΣ: ΕΝΑΣ ΤΟΙΧΟΣ %s cm" % cm(WE - LIN_X), "Ο τοίχος της πόρτας εισόδου χτίζεται ΕΝΑΣ, χοντρός, με διπλό σκελετό (όχι τοίχος και "
     "πρόσθετη επένδυση), και στις δύο πλευρές της πόρτας. Προς το σπίτι έχει μέσα του κανάλι %s cm από το δάπεδο ως την ψευδοροφή – ΔΙΠΛΑ στο δοκάρι, όχι κάτω του." % cm(LIN_CAV)),
    ("ΨΥΚΤΙΚΑ: ΚΑΤΕΒΑΙΝΟΥΝ ΒΟΡΕΙΑ ΤΗΣ ΠΟΡΤΑΣ", "Από το μηχάνημα %s m μέσα στην ψευδοροφή της λωρίδας και κάτω, μέσα στο κανάλι του τοίχου, "
     "στη βόρεια παραστάδα της πόρτας." % mm2(R_VOID_LEN)),
    ("ΨΥΚΤΙΚΑ: ΔΑΠΕΔΟ ΥΠΝ.2 → ΒΑ ΕΞΩΣΤΗΣ", "Μέσα στο γέμισμα, κάτω από τη βάση του γυψότοιχου Τ2-06 και κολλητά στον ανατολικό τοίχο του Υπν.2 "
     "(%s m, λωρίδα 20 cm χωρίς ενδοδαπέδια). Στον πεσσό μέσα στη ντουλάπα ανεβαίνουν ως %s και βγαίνουν στην εξωτερική μονάδα." % (mm2(R_FLOOR_LEN), lv(EXIT_Z))),
    ("ΣΥΜΠΥΚΝΩΜΑΤΑ: ΚΑΤΕΒΑΙΝΟΥΝ ΝΟΤΙΑ ΤΗΣ ΠΟΡΤΑΣ", "Ο σωλήνας Ø 32 του μηχανήματος μπαίνει στο κανάλι του τοίχου αμέσως νότια της πόρτας "
     "και κατεβαίνει στο δάπεδο."),
    ("ΣΥΜΠΥΚΝΩΜΑΤΑ: %s m ΣΤΟ ΔΑΠΕΔΟ, ΚΟΛΛΗΤΑ ΣΤΟΝ ΤΟΙΧΟ" % mm2(C_FLOOR_LEN), "Μέσα στο γέμισμα 12 cm κατά μήκος του τοίχου της εισόδου, "
     "μπροστά από το άνοιγμα της κουζίνας, με κλίση 1 % προς το μπροστινό μπαλκόνι."),
    ("ΒΓΑΙΝΟΥΝ ΑΠΟ ΤΟ ΤΟΥΒΛΟ ΔΙΠΛΑ ΣΤΗ ΜΠΑΛΚΟΝΟΠΟΡΤΑ", "Από τη βάση του πεσσού (τούβλο) ανάμεσα στη μπαλκονόπορτα του σαλονιού και την κολόνα. "
     "Σκυρόδεμα δεν τρυπιέται."),
    ("ΣΙΦΩΝΙ ΤΟΥ ΜΠΡΟΣΤΙΝΟΥ ΜΠΑΛΚΟΝΙΟΥ", "Μέσα στην επίστρωση του μπαλκονιού ως το σιφώνι του → υδρορροή ΥΔ2. Με φυσική ροή, χωρίς αντλία."),
]


def steps_panel(c, x, y, w, only=None, size=7.2, title="Η ΔΙΑΔΡΟΜΗ ΒΗΜΑ – ΒΗΜΑ"):
    if not SHOW_NOTES:
        return y
    y = head(c, x, y, title)
    for i, (t, d) in enumerate(STEPS, 1):
        if only and i not in only:
            continue
        badge(c, x + 7, y + 2.5, i, 7.0)
        c.setFont("Inter-Bold", size); c.setFillColorRGB(*DARK); c.drawString(x + 20, y, t)
        y -= size + 3.0
        y = para(c, x + 20, y, w - 20, d, size=size - 0.4) - 3.5
    return y


def legend(c, x, y, items, size=6.4, w=250, title="ΥΠΟΜΝΗΜΑ"):
    y = _head(c, x, y, title, 8.5)
    for kind, col, txt in items:
        yy = y + 2
        if kind == "line":
            c.setStrokeColorRGB(*col); c.setLineWidth(2.0); c.setDash([]); c.line(x, yy, x + 22, yy)
        elif kind == "dash":
            c.setStrokeColorRGB(*col); c.setLineWidth(1.6); c.setDash([1.4, 1.8]); c.line(x, yy, x + 22, yy); c.setDash([])
        elif kind == "ddash":
            c.setStrokeColorRGB(*col); c.setLineWidth(1.2); c.setDash([4, 2]); c.line(x, yy, x + 22, yy); c.setDash([])
        elif kind == "box":
            c.setFillColorRGB(*col[0]); c.setStrokeColorRGB(*col[1]); c.setLineWidth(0.7); c.rect(x + 3, yy - 4, 16, 8, stroke=1, fill=1)
        elif kind == "hatch":
            c.setFillColorRGB(*col[0]); c.setStrokeColorRGB(*col[1]); c.setLineWidth(0.7); c.rect(x + 3, yy - 4, 16, 8, stroke=1, fill=1)
            c.setLineWidth(0.3)
            for k in range(4):
                c.line(x + 3 + k * 4, yy - 4, x + 7 + k * 4, yy + 4)
        elif kind == "badge":
            badge(c, x + 11, yy, col, 5.5)
        c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        ls = wrap(txt, "Inter", size, w - 30)
        for j, l in enumerate(ls):
            c.drawString(x + 30, y - j * (size + 1.8), l)
        y -= (size + 1.8) * len(ls) + 3.2
    return y


LEG_PIPES = [("line", MAG, "ψυκτικά ΚΜ1 (αερίου 5/8″ + υγρού 3/8″, προμονωμένος χαλκός)"),
             ("line", ORANGE, "συμπυκνώματα ΚΜ1 – PVC Ø 32, φυσική ροή"),
             ("ddash", BLUE2, "ψυκτικά split ΚΜ2 / ΚΜ3 (υπνοδωματίων)"),
             ("line", RAIN, "υδρορροή · σωλήνας σιφωνιού εξώστη Φ50"),
             ("box", (LIN_F, LIN_S), "ο τοίχος της πόρτας – ένας, %s cm: προς το σπίτι 2 γυψοσανίδες και κανάλι %s cm" % (cm(WE - LIN_X), cm(LIN_CAV))),
             ("hatch", (CONC, DARK), "σκυρόδεμα: πλάκες, δοκάρια, κολόνες – δεν τρυπιέται, δεν περνάμε από κάτω του")]


def frame(c, no, theme, sub, scale_txt, floor="Α΄ · Β΄ · Γ΄ · Δ΄ ΟΡΟΦΟΣ (ίδια διαδρομή σε όλους)"):
    frame_and_title(c, no, theme, sub, floor, BASE, scale_txt, REV, DATE)


def big_title(c, x, y, t, sub=None):
    c.setFont("Inter-Bold", 13); c.setFillColorRGB(*DARK); c.drawString(x, y, t)
    if sub:
        c.setFont("Inter", 8); c.setFillColorRGB(*GREY); c.drawString(x, y - 12, sub)


def sec_marker(c, X, Y, letter, dx, dy, r=8.5):
    """Άκρο γραμμής τομής: κύκλος με γράμμα + βέλος προς τη φορά που κοιτάμε (dx, dy μοναδιαίο, σε pt σελίδας)."""
    c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(*RED); c.setLineWidth(1.2); c.circle(X, Y, r, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("Inter-Bold", 9.5); c.drawCentredString(X, Y - 3.4, letter)
    arrow(c, X + dx * (r + 1), Y + dy * (r + 1), X + dx * (r + 13), Y + dy * (r + 13), color=RED, lw=1.2, head=5.5)


# ================================================================ ΚΜ-01 κάτοψη διαδρομής (τυπικός όροφος)
def plan_bg(c, model, ox, oy, s, clip):
    """Υπόβαθρο: κάτοψη τοιχοποιιών του ορόφου (όπως στα φύλλα ανόψεων), κομμένη στο παράθυρο clip = (x0, y0, x1, y1) σε m."""
    sheets.bind(model)
    v = View(c, ox, oy, s)
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.saveState()
    pth = c.beginPath(); pth.rect(X0, Y0, X1 - X0, Y1 - Y0); c.clipPath(pth, stroke=0, fill=0)
    c.setFillColorRGB(1, 1, 1); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=0, fill=1)
    sheets.zones_fill(v, colored=False)
    sheets.plan(v)
    return v


def beams_plan(v, model, names, lab=None):
    c = v.c
    for name, sec, x0, y0, x1, y1 in model.BEAMS:
        if name not in names:
            continue
        c.saveState(); c.setFillAlpha(0.30)
        v.rect(x0, y0, x1, y1, fill=BEAMC)
        c.restoreState()
        v.hatch([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], 0.09, 45, BEAMC, 0.35)
        c.setDash([5, 2]); v.rect(x0, y0, x1, y1, stroke=BEAMC, lw=0.9); c.setDash([])
    for name, (x, y, r) in (lab or {}).items():
        sec = [b[1] for b in model.BEAMS if b[0] == name][0]
        v.text(x, y, "ΔΟΚΑΡΙ %s %s" % (name, sec), size=6.0, rot=r, color=BEAMC, font="Inter-Bold", bg=True)


def vpipe(v, pts, color, lw=2.0, dash=None, halo=True):
    c = v.c
    c.saveState(); c.setLineJoin(1); c.setLineCap(1 if not dash else 0)
    for col, w_, d_ in ((WHITE, lw + 1.6, None), (color, lw, dash)) if halo else ((color, lw, dash),):
        pth = c.beginPath(); pth.moveTo(*v.p(*pts[0]))
        for q in pts[1:]:
            pth.lineTo(*v.p(*q))
        c.setStrokeColorRGB(*col); c.setLineWidth(w_); c.setDash(d_ or [])
        c.drawPath(pth, stroke=1, fill=0)
    c.restoreState()


def vbadge(v, x, y, n, r=7.0, dx=0, dy=0):
    X, Y = v.p(x, y)
    badge(v.c, X + dx, Y + dy, n, r)


def vlabel(v, x, y, lines, anchor="l", size=6.0, color=DARK, to=None, font="Inter-SemiBold"):
    c = v.c
    X, Y = v.p(x, y)
    if to:
        X0, Y0 = v.p(*to)
        c.setStrokeColorRGB(*color); c.setLineWidth(0.45); c.line(X0, Y0, X, Y)
        c.setFillColorRGB(*color); c.circle(X0, Y0, 1.3, stroke=0, fill=1)
    for i, s_ in enumerate(lines):
        f = font if i == 0 else "Inter"
        w = pdfmetrics.stringWidth(s_, f, size)
        tx = X + 3 if anchor == "l" else (X - 3 - w if anchor == "r" else X - w / 2)
        ty = Y - size * 0.36 - i * (size + 1.8)
        c.setFillColorRGB(1, 1, 1); c.rect(tx - 1.2, ty - 1.2, w + 2.4, size + 2.0, stroke=0, fill=1)
        c.setFont(f, size); c.setFillColorRGB(*color); c.drawString(tx, ty, s_)


def vdim(v, orient, pos, pts, size=6.0, side=1, fmt=None, color=DIMC, tick=2.8):
    """Αλυσίδα διαστάσεων σε κάτοψη (View) με στοιχεία σε pt – για κλίμακες 1:5 / 1:10. side: +1 κείμενο νότια / ανατολικά της γραμμής."""
    c = v.c
    fmt = fmt or cm
    pts = sorted(pts)
    c.setStrokeColorRGB(*color); c.setFillColorRGB(*color)
    if orient == "H":
        X0, Y = v.p(pts[0], pos); X1, _ = v.p(pts[-1], pos)
        c.setLineWidth(0.4); c.line(X0, Y, X1, Y)
        for q in pts:
            X, _ = v.p(q, pos); c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(pts[:-1], pts[1:]):
            Xa, _ = v.p(a, pos); Xb, _ = v.p(b, pos)
            c.setFont("Inter-SemiBold", size); c.drawCentredString((Xa + Xb) / 2, Y - size - 1.5 if side > 0 else Y + 2.2, fmt(b - a))
    else:
        X, Y0 = v.p(pos, pts[0]); _, Y1 = v.p(pos, pts[-1])
        c.setLineWidth(0.4); c.line(X, Y0, X, Y1)
        for q in pts:
            _, Y = v.p(pos, q); c.setLineWidth(0.6); c.line(X - tick, Y - tick, X + tick, Y + tick)
        for a, b in zip(pts[:-1], pts[1:]):
            _, Ya = v.p(pos, a); _, Yb = v.p(pos, b)
            c.saveState(); c.translate(X + (size + 1.0 if side > 0 else -2.4), (Ya + Yb) / 2); c.rotate(90)
            c.setFont("Inter-SemiBold", size); c.drawCentredString(0, 0, fmt(b - a)); c.restoreState()


def ac_unit_plan(v, model, slot_lab=True):
    """Μονάδα, plenum, slot, επιστροφή, θυρίδα και το όριο της χαμήλωσης (από το μοντέλο ανόψεων)."""
    c = v.c
    for r in getattr(model, "AC_OUTLINE", []):
        if isinstance(r[0], (tuple, list)):
            for a_, b_ in zip(r, r[1:]):
                v.line(*a_, *b_, color=(0.55, 0.42, 0.22), lw=0.9, dash=[5, 2.5])
    for name, r in model.DUCTS:
        v.rect(*r, fill=BLUE_F, stroke=BLUE, lw=0.5)
    for d in model.DIFFUSERS:
        x0, y0, x1, y1 = d["rect"]
        if d["kind"] in ("slot", "front"):
            if d["kind"] == "front":         # R02: slot στη ΜΕΤΩΠΗ της χαμήλωσης – χοντρή γραμμή πάνω στην ακμή, ο αέρας φεύγει οριζόντια
                v.rect(x0 - 0.014, y0, x0 + 0.014, y1, fill=BLUE, stroke=BLUE, lw=0.6)
            else:
                v.rect(x0, y0, x1, y1, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.6)
            n = 4
            for k in range(n):
                yy = y0 + (k + 0.5) * (y1 - y0) / n
                X0, Y0 = v.p(x0 - 0.03, yy); X1, Y1 = v.p(x0 - (0.55 if d["kind"] == "front" else 0.42), yy)
                arrow(c, X0, Y0, X1, Y1, color=BLUE, lw=0.8 if d["kind"] == "front" else 0.7, head=4.5)
        elif d["kind"] == "ret":
            v.rect(x0, y0, x1, y1, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.8)
    for u in model.UNITS:
        x0, y0, x1, y1 = u["rect"]
        v.rect(x0, y0, x1, y1, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.1)
        v.line(x0, y0, x1, y1, color=BLUE, lw=0.4); v.line(x0, y1, x1, y0, color=BLUE, lw=0.4)
    for h in model.HATCHES:
        c.setDash([2, 1.2]); v.rect(*h["rect"], stroke=DARK, lw=0.6); c.setDash([])


def section_line(v, a, b, letter, look, off=10):
    """Γραμμή τομής από a ως b (m) με κύκλους-γράμματα στα άκρα· look = φορά που κοιτάμε σε pt σελίδας (dx, dy)."""
    c = v.c
    X0, Y0 = v.p(*a); X1, Y1 = v.p(*b)
    c.setStrokeColorRGB(*RED); c.setLineWidth(1.1); c.setDash([9, 2.5, 1.5, 2.5]); c.line(X0, Y0, X1, Y1); c.setDash([])
    L = math.hypot(X1 - X0, Y1 - Y0)
    ux, uy = (X1 - X0) / L, (Y1 - Y0) / L
    sec_marker(c, X0 - ux * off, Y0 - uy * off, letter, *look)
    sec_marker(c, X1 + ux * off, Y1 + uy * off, letter, *look)


def section_ends(v, pts, letter, look, stub=0.30, off=10):
    """Τεθλασμένη γραμμή τομής που φαίνεται ΜΟΝΟ στα άκρα και στις γωνίες της (για να μη σκεπάζει τους σωλήνες)."""
    c = v.c
    c.setStrokeColorRGB(*RED); c.setLineWidth(1.1); c.setDash([9, 2.5, 1.5, 2.5])
    def seg(a, b, t0, t1):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-9:
            return
        p0 = (a[0] + (b[0] - a[0]) * t0 / L, a[1] + (b[1] - a[1]) * t0 / L); p1 = (a[0] + (b[0] - a[0]) * t1 / L, a[1] + (b[1] - a[1]) * t1 / L)
        c.line(*v.p(*p0), *v.p(*p1))
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L <= 2 * stub + 1e-6:
            seg(a, b, 0, L)
        else:
            seg(a, b, 0, stub); seg(a, b, L - stub, L)
    c.setDash([])
    for a, b in ((pts[0], pts[1]), (pts[-1], pts[-2])):
        X0, Y0 = v.p(*a); X1, Y1 = v.p(*b)
        L = math.hypot(X1 - X0, Y1 - Y0)
        sec_marker(c, X0 - (X1 - X0) / L * off, Y0 - (Y1 - Y0) / L * off, letter, *look)


def lining_plan(v):
    """Έμφαση στον ενιαίο τοίχο της πόρτας εισόδου Τ6Β (τα ίδια τα ορθογώνια σχεδιάζονται από το μοντέλο τοιχοποιιών)."""
    for r in (WALL_N, WALL_S):
        v.rect(*r, fill=LIN_F, stroke=LIN_S, lw=1.2)


def sheet_plan(c):
    s = scale(40)
    clip = (3.25, 0.40, 11.95, 10.12)
    ox = 34 - clip[0] * s
    oy = PAGE_H - 815 - clip[1] * s
    v = plan_bg(c, A, ox, oy, s, clip)
    # δοκάρια που κλείνουν το καθιστικό
    beams_plan(v, A, ("Δ3.1", "Δ9.1", "Δ4.4", "Δ9.5", "Δ1.4"),
               {"Δ3.1": (7.45, 5.00, 0), "Δ9.1": (9.55, 8.35, 90), "Δ4.4": (6.60, 9.30, 0), "Δ9.5": (9.55, 2.62, 90), "Δ1.4": (7.75, 0.65, 0)})
    ac_unit_plan(v, A)
    lining_plan(v)
    # εξωτερική μονάδα · σιφώνια εξωστών · υδρορροές
    c.setDash([3, 1.5]); v.rect(*EM, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=0.8); c.setDash([])
    vpipe(v, GULLY, RAIN, 1.6, halo=False)
    v.rect(GS[0] - 0.07, GS[1] - 0.07, GS[0] + 0.07, GS[1] + 0.07, fill=WHITE, stroke=RAIN, lw=1.1)
    v.line(GS[0] - 0.07, GS[1] - 0.07, GS[0] + 0.07, GS[1] + 0.07, color=RAIN, lw=0.5); v.line(GS[0] - 0.07, GS[1] + 0.07, GS[0] + 0.07, GS[1] - 0.07, color=RAIN, lw=0.5)
    v.circle(YD2[0], YD2[1], 0.045, fill=RAIN, stroke=RAIN)
    # split (υπνοδωματίων)
    for a_, b_ in A.SPLIT_DRAW:
        vpipe(v, [a_, b_], BLUE2, 1.1, dash=[4, 2], halo=False)
    # οδεύσεις ΚΜ1: στην ψευδοροφή συνεχής γραμμή, στο δάπεδο κουκκίδες
    vpipe(v, A.COND_ROUTE, ORANGE, 1.9)
    vpipe(v, A.KM1_VOID, MAG, 2.2)
    vpipe(v, A.COND_FLOOR, ORANGE, 2.0, dash=[1.4, 1.9])
    vpipe(v, A.KM1_FLOOR, MAG, 2.4, dash=[1.4, 1.9])
    v.circle(DR[0], DR[1], 0.040, fill=MAG, stroke=WHITE, lw=0.8); v.circle(DC[0], DC[1], 0.040, fill=ORANGE, stroke=WHITE, lw=0.8)
    # ετικέτες
    v.text((UX0 + UX1) / 2, (UY0 + UY1) / 2 - 0.10, "ΚΜ1", size=8, font="Inter-Bold", color=BLUE, bg=True)
    v.text((UX0 + UX1) / 2, (UY0 + UY1) / 2 + 0.12, "μηχάνημα", size=5.4, color=BLUE, bg=True)
    v.text(6.30, 7.30, "ΚΑΘΙΣΤΙΚΟ", size=9, font="Inter-Bold", color=GREY)
    v.text(6.30, 7.52, "οροφή %s" % lv(LV_LIV), size=6, color=GREY)
    v.text(7.75, 3.10, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=9, font="Inter-Bold", color=GREY)
    v.text(7.75, 3.32, "οροφή %s" % lv(LV_BED), size=5.6, color=GREY)
    v.text(7.75, 3.47, "(κανένας σωλήνας της ΚΜ1 στην οροφή του)", size=5.2, color=GREY)
    v.text(4.85, 3.85, "ΧΩΛ", size=7.5, font="Inter-Bold", color=GREY)
    v.text(5.72, 2.00, "ΛΟΥΤΡΟ", size=6.5, font="Inter-Bold", color=GREY)
    v.text(10.62, 2.25, "ΒΑ ΕΞΩΣΤΗΣ", size=7.5, font="Inter-Bold", color=GREY)
    v.text((EM[0] + EM[2]) / 2, (EM[1] + EM[3]) / 2, "εξωτ. μονάδα", size=5.4, color=BLUE, font="Inter-SemiBold")
    v.text((EM[0] + EM[2]) / 2, EM[3] + 0.12, "(θέση ενδεικτική)", size=4.8, color=BLUE, bg=True)
    v.text(11.00, 6.05, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=7.5, font="Inter-Bold", color=GREY)
    v.text(11.20, 8.85, "ΚΟΥΖΙΝΑ", size=8, font="Inter-Bold", color=GREY)
    v.text(11.20, 9.04, "οροφή %s (ενιαία με τη λωρίδα)" % lv(LV_STRIP), size=5.4, color=GREY)
    v.text(5.60, 9.85, "ΜΠΡΟΣΤΙΝΟ ΜΠΑΛΚΟΝΙ", size=7.5, font="Inter-Bold", color=GREY)
    v.text(STRIP_X - 0.13, 7.05, "ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ 1,10 · οροφή %s" % lv(LV_STRIP), size=5.6, rot=90, color=(0.45, 0.33, 0.15), font="Inter-SemiBold", bg=True)
    v.text(7.95, 1.05, "ντουλάπα Υπν.2", size=5.6, color=GREY, bg=True)
    vlabel(v, 10.02, 4.98, ["ΨΥΚΤΙΚΑ: ΚΑΤΕΒΑΙΝΟΥΝ ΜΕΣΑ", "ΣΤΟΝ ΤΟΙΧΟ ΤΗΣ ΠΟΡΤΑΣ", "(βόρεια της πόρτας)"], color=MAG, to=(DR[0] + 0.03, DR[1]), size=6.2)
    vlabel(v, 10.02, 6.66, ["ΣΥΜΠΥΚΝΩΜΑΤΑ: ΚΑΤΕΒΑΙΝΟΥΝ", "ΜΕΣΑ ΣΤΟΝ ΤΟΙΧΟ ΤΗΣ ΠΟΡΤΑΣ", "(νότια της πόρτας)"], color=ORANGE, to=(DC[0] + 0.03, DC[1]), size=6.2)
    vlabel(v, 10.02, 7.36, ["Ο ΤΟΙΧΟΣ ΤΗΣ ΠΟΡΤΑΣ: ΕΝΑΣ, %s cm" % cm(WE - LIN_X), "(μέσα του κανάλι %s cm για τους σωλήνες)" % cm(LIN_CAV)], color=LIN_S,
           to=(LIN_X + 0.04, 7.36), size=6.2)
    vlabel(v, 7.60, 6.52, ["Ο ΑΕΡΑΣ ΒΓΑΙΝΕΙ ΟΡΙΖΟΝΤΙΑ, ΜΠΡΟΣΤΑ", "από τα slot στη ΜΕΤΩΠΗ της λωρίδας"], anchor="r", color=BLUE, to=(STRIP_X - 0.50, 6.37), size=6.0)
    vlabel(v, 8.05, 4.42, ["ΨΥΚΤΙΚΑ ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ", "λωρίδα 20 cm στον τοίχο,", "χωρίς ενδοδαπέδια"], anchor="r", color=MAG, to=(KX - 0.03, 4.30), size=6.0)
    vlabel(v, 8.05, 5.72, ["ΨΥΚΤΙΚΑ ΜΕΣΑ ΣΤΗΝ ΨΕΥΔΟΡΟΦΗ", "%s m ως τον τοίχο της πόρτας" % mm2(R_VOID_LEN)], anchor="r", color=MAG, to=(A.KM1_VOID[0][0] - 0.03, 5.72), size=6.0)
    vlabel(v, 8.05, 8.28, ["ΣΥΜΠΥΚΝΩΜΑΤΑ ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ", "Ø 32 · κλίση 1 % · κολλητά στον τοίχο"], anchor="r", color=ORANGE, to=(CX - 0.03, 8.28), size=6.0)
    vlabel(v, 8.25, 9.66, ["βγαίνουν από τη βάση του τούβλου", "δίπλα στη μπαλκονόπορτα"], anchor="r", color=ORANGE, to=(PX - 0.03, 9.36), size=5.8)
    vlabel(v, 8.25, 9.96, ["ΣΙΦΩΝΙ ΜΠΡΟΣΤΙΝΟΥ ΜΠΑΛΚΟΝΙΟΥ → ΥΔ2"], anchor="r", color=RAIN, to=(GS[0] - 0.08, GS[1] + 0.04), size=6.0)
    vlabel(v, 9.72, 9.98, ["ΥΔ2 υδρορροή"], color=RAIN, to=(YD2[0] + 0.03, YD2[1] + 0.02), size=5.8)
    vlabel(v, 8.55, 2.05, ["ψυκτικά split ΚΜ2 / ΚΜ3:", "κατεβαίνουν μέσα στη ντουλάπα"], anchor="r", color=BLUE2, to=(A.SPLIT_DROP[0] - 0.04, A.SPLIT_DROP[1] + 0.02), size=5.6)
    # βήματα
    vbadge(v, (UX0 + UX1) / 2 - 0.02, UY1 - 0.20, 1)
    vbadge(v, LIN_X, 7.62, 2, dx=-9)
    vbadge(v, 9.17, DR[1], 3, dy=9)
    vbadge(v, KX, 3.40, 4, dx=12)
    vbadge(v, 9.15, DC[1], 5, dx=-12, dy=8)
    vbadge(v, CX, 7.95, 6, dx=-11)
    vbadge(v, PX, 9.33, 7, dx=13)
    vbadge(v, GS[0], GS[1], 8, dx=-15, dy=2)
    # γραμμές τομών
    c.restoreState()
    section_ends(v, [(9.30, 0.72), (9.30, 8.80), (PX, 8.80), (PX, 10.02)], "Α", (1, 0))
    section_line(v, (7.80, 7.15), (10.22, 7.15), "Β", (0, 1))
    section_line(v, (8.95, 1.25), (11.52, 1.25), "Γ", (0, 1))
    # πλαίσιο κάτοψης
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    # δεξιά στήλη
    x, w = X1 + 26, 1160 - (X1 + 26)
    big_title(c, x, 800, "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1 – ΔΙΑΔΡΟΜΗ ΣΩΛΗΝΩΝ", "Κάτοψη τυπικού ορόφου (Α΄ · Β΄ · Γ΄ · Δ΄) · οι τομές Α-Α, Β-Β, Γ-Γ στα επόμενα φύλλα")
    y = 766
    y = head(c, x, y, "ΓΙΑΤΙ ΕΤΣΙ", 9.5, RED)
    y = para(c, x, y, w / 2 - 12, "Το σαλόνι κλείνεται γύρω-γύρω από δοκάρια (καφέ στην κάτοψη): Δ3.1 προς τα δωμάτια, Δ9.1 προς την είσοδο και την κουζίνα, "
             "Δ4.4 και Δ7.1 στις τζαμαρίες. Ό,τι φύγει από την ψευδοροφή του πρέπει να περάσει κάτω από δοκάρι.", size=7.0)
    y = para(c, x, y - 3, w / 2 - 14, "Για να ΜΗΝ περάσει τίποτα κάτω από δοκάρι, ο τοίχος της πόρτας εισόδου χτίζεται ΕΝΑΣ τοίχος %s cm, %s cm πιο μέσα στο σπίτι "
             "από το δοκάρι. Μέσα στο κανάλι του οι σωλήνες κατεβαίνουν ΔΙΠΛΑ στο δοκάρι και φεύγουν από το ΔΑΠΕΔΟ. Δοκάρι δεν τρυπιέται πουθενά."
             % (cm(WE - LIN_X), cm(BF - LIN_X)), size=7.0, font="Inter-SemiBold")
    y2 = 766
    x2 = x + w / 2 + 6
    y2 = head(c, x2, y2, "ΤΙ ΑΛΛΑΖΕΙ ΣΤΟ ΣΠΙΤΙ", 9.5)
    for t in ["Ο τοίχος της πόρτας εισόδου είναι ΕΝΑΣ τοίχος %s cm (όχι τοίχος + πρόσθετη επένδυση), και στις δύο πλευρές της πόρτας. Κουτί πίσω από την πόρτα "
              "δεν υπάρχει." % cm(WE - LIN_X),
              "Ο αέρας του μηχανήματος βγαίνει ΟΡΙΖΟΝΤΙΑ, από slot στη ΜΕΤΩΠΗ της λωρίδας (το κατακόρυφο σκαλοπάτι της οροφής) – όχι προς τα κάτω.",
              "Ψυκτικά: από το δάπεδο του Υπν.2 στον ΒΑ εξώστη (λωρίδα 20 cm δίπλα στον τοίχο χωρίς ενδοδαπέδια).",
              "Συμπυκνώματα: στο σιφώνι του ΜΠΡΟΣΤΙΝΟΥ μπαλκονιού (υδρορροή ΥΔ2), μέσα στο δάπεδο κατά μήκος του τοίχου της εισόδου.",
              "Οροφή λωρίδας εισόδου και κουζίνας %s = ΠΕΡΑΣΙΑ ΜΕ ΤΑ ΔΟΚΑΡΙΑ (το φύλλο περνά κάτω από το δοκάρι) – ενιαία, χωρίς δόντι. Η λωρίδα 1,10 μετριέται "
              "από τον τοίχο. Μηχάνημα slim ως %s cm ύψος. Εξωτερική μονάδα στον ΒΑ εξώστη." % (lv(LV_STRIP), cm(UNIT["hmax"]))]:
        if SHOW_NOTES:
            c.setFillColorRGB(*DARK); c.circle(x2 + 2.5, y2 + 2.4, 1.3, stroke=0, fill=1)
        y2 = para(c, x2 + 9, y2, w / 2 - 20, t, size=6.8) - 2
    y = min(y, y2) - 10
    if SHOW_NOTES:
        c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.5); c.line(x, y + 6, x + w, y + 6)
    y -= 8
    yl = steps_panel(c, x, y, w, size=6.8)
    legend(c, x, yl - 4, [("line", MAG, "ψυκτικά ΚΜ1 μέσα στην ΨΕΥΔΟΡΟΦΗ"),
                                  ("dash", MAG, "ψυκτικά ΚΜ1 μέσα στο ΔΑΠΕΔΟ (γέμισμα)"),
                                  ("line", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 στην ψευδοροφή"),
                                  ("dash", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 στο δάπεδο, κλίση 1 %"),
                                  ("ddash", BLUE2, "ψυκτικά split υπνοδωματίων (ψευδοροφή)"),
                                  ("line", RAIN, "σωλήνας σιφωνιού εξώστη → υδρορροή ΥΔ2"),
                                  ("box", (LIN_F, LIN_S), "ο τοίχος της πόρτας εισόδου – ένας, %s cm" % cm(WE - LIN_X)),
                                  ("hatch", ((0.86, 0.75, 0.68), BEAMC), "δοκάρια (δεν περνάμε από κάτω τους)"),
                                  ("badge", 3, "βήμα της διαδρομής (ίδιοι αριθμοί στις τομές)")], w=w, size=6.0)
    north_arrow(c, X1 - 20, Y1 - 24, 9)
    frame(c, "ΚΜ-01", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΔΙΑΔΡΟΜΗ", "Σωλήνες μέσα στον τοίχο της πόρτας · ο αέρας μπροστά, από τη μετώπη", "Κλίμακα 1:40 · A3")


# ================================================================ ΚΜ-02 τομή Α-Α (κατά μήκος της διαδρομής, κοιτάμε ανατολικά)
def cross_mark(sv, u, z, col, r=3.6):
    """Σύμβολο «ο σωλήνας στρίβει και φεύγει προς τα μέσα (μακριά μας)»."""
    c = sv.c
    sv.circle(u, z, r, fill=WHITE, stroke=col, lw=1.0, pt=True)
    X, Y = sv.p(u, z)
    k = r * 0.62
    c.setStrokeColorRGB(*col); c.setLineWidth(0.9); c.line(X - k, Y - k, X + k, Y + k); c.line(X - k, Y + k, X + k, Y - k)


def msg_box(c, X, Y, w, title, lines, size=6.2):
    """Κόκκινο πλαίσιο-μήνυμα· (X, Y) = πάνω-αριστερά."""
    if not SHOW_NOTES:
        return 0
    h = 13 + len(lines) * (size + 2.2) + 4
    c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(*RED); c.setLineWidth(1.0); c.roundRect(X, Y - h, w, h, 4, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("Inter-Bold", size + 0.8); c.drawString(X + 6, Y - 11, title)
    c.setFont("Inter", size); c.setFillColorRGB(*DARK)
    for i, l in enumerate(lines):
        c.drawString(X + 6, Y - 11 - (i + 1) * (size + 2.2), l)
    return h


def bullets(c, x, y, w, items, size=7.2):
    if not SHOW_NOTES:
        return y
    for t in items:
        c.setFillColorRGB(*DARK); c.circle(x + 2.5, y + 2.6, 1.4, stroke=0, fill=1)
        y = para(c, x + 10, y, w - 12, t, size=size) - 4
    return y


def sheet_aa(c):
    S = scale(30)
    Y0, Y1 = 0.28, 10.32
    ZB = -0.36
    sv = Sec(c, 40, 452, S, u0=Y0)
    d19, d31, d44 = BEAM["Δ1.4"], BEAM["Δ3.1"], BEAM["Δ4.4"]
    sof = lambda b_: A.beam_soffit(b_[1])
    s55, s50 = A.beam_soffit("30/55"), A.beam_soffit("30/50")
    WS0 = T309[1]                                    # νότιος τοίχος στη θέση της εξόδου: παρειά της επένδυσης προς το καθιστικό (9,115)
    gy = GS[1]                                       # σιφώνι του μπροστινού εξώστη
    cys = [DC[1], _CF[1][1], _CF[2][1], PY0, PY1, gy - 0.04]         # σημεία της όδευσης των συμπυκνωμάτων στο γέμισμα (προβολή y)
    # ---- φόντο: ό,τι βλέπουμε πίσω από την τομή (προς ανατολή)
    sv.rect(WARD[3], 0, T206[1], LV_BED, fill=WALL_BG)                       # τοίχος Υπν.2
    sv.rect(WARD[3], s55, 3.00, LV_BED, fill=CONC_L)                         # Δ9.5 πάνω από τη μπαλκονόπορτα
    sv.rect(K3[1], 0, T206[1], LV_BED, fill=CONC_L, stroke=(0.7, 0.7, 0.72), lw=0.4)      # κολόνα Κ3
    sv.text((K3[1] + T206[1]) / 2, 1.02, "ΚΟΛΟΝΑ Κ3", size=6.2, color=GREY, font="Inter-SemiBold")
    sv.text((K3[1] + T206[1]) / 2, 0.89, "(πίσω)", size=5.2, color=GREY)
    sv.rect(W206[1], 0, W206[3], s55, fill=(0.90, 0.95, 0.99), stroke=(0.35, 0.45, 0.60), lw=0.8)        # μπαλκονόπορτα W2.06
    sv.rect(W206[1] + 0.06, 0.06, W206[3] - 0.06, s55 - 0.06, stroke=(0.35, 0.45, 0.60), lw=0.4)
    sv.text((W206[1] + W206[3]) / 2, 1.78, "μπαλκονόπορτα", size=5.6, color=(0.30, 0.40, 0.55), font="Inter-SemiBold")
    sv.text((W206[1] + W206[3]) / 2, 1.65, "προς τον ΒΑ εξώστη", size=5.0, color=(0.30, 0.40, 0.55))
    sv.rect(EM[1], 0.08, EM[3], 0.78, fill=(0.95, 0.97, 1.0), stroke=BLUE, lw=0.7, dash=[3, 1.5])          # εξωτερική μονάδα (έξω, στον εξώστη)
    # ο ενιαίος τοίχος της πόρτας εισόδου (όψη από το καθιστικό): από τον βόρειο τοίχο του καθιστικού ως το άνοιγμα της κουζίνας
    sv.rect(T206[3], 0, WU_S[3], LV_STRIP, fill=LIN_F, stroke=LIN_S, lw=0.6)
    sv.rect(DOOR[0], 0, DOOR[1], 2.20, fill=(0.93, 0.89, 0.82), stroke=WOOD_S, lw=0.9)                    # πόρτα εισόδου
    sv.rect(DOOR[0] + 0.05, 0.05, DOOR[1] - 0.05, 2.15, stroke=WOOD_S, lw=0.4)
    sv.circle(DOOR[1] - 0.10, 1.02, 2.2, fill=WOOD_S, pt=True)
    sv.text((DOOR[0] + DOOR[1]) / 2, 1.05, "ΠΟΡΤΑ ΕΙΣΟΔΟΥ", size=6.0, color=WOOD_S, font="Inter-Bold")
    sv.text((DOOR[0] + DOOR[1]) / 2, 0.92, "1,00 × 2,20", size=5.2, color=WOOD_S)
    sv.rect(WU_S[3], 0, WS0, LV_STRIP, fill=WHITE)                                                         # άνοιγμα κουζίνας
    sv.text((WU_S[3] + WS0) / 2, 1.08, "άνοιγμα", size=6.0, color=GREY, font="Inter-SemiBold"); sv.text((WU_S[3] + WS0) / 2, 0.95, "κουζίνας", size=6.0, color=GREY, font="Inter-SemiBold")
    sv.rect(T206[3], s50, K8[1], SOF8, fill=CONC_L)                                                        # Δ9.1 πίσω από τον τοίχο, μέσα στο κενό
    sv.text(8.42, 2.70, "δοκάρι Δ9.1 (πίσω από τον τοίχο)", size=4.6, color=GREY)
    sv.rect(ET_S, BALC_Z, Y1, 1.05, fill=CONC_L, stroke=(0.72, 0.72, 0.75), lw=0.4)                        # τοιχείο του εξώστη (πίσω)
    sv.text((ET_S + Y1) / 2 + 0.02, 0.62, "τοιχείο εξώστη", size=4.8, color=GREY); sv.text((ET_S + Y1) / 2 + 0.02, 0.51, "(πίσω)", size=4.8, color=GREY)
    # ---- φέρων οργανισμός (τομή)
    sv.etics_r(0.40, ZB, 0.50, TOP + 0.02)
    sv.concrete([(d19[3], sof(d19)), (d19[5], sof(d19)), (d19[5], SOF3), (d31[3], SOF3), (d31[3], sof(d31)), (d31[5], sof(d31)), (d31[5], SOF8),
                 (d44[3], SOF8), (d44[3], sof(d44)), (d44[5], sof(d44)), (d44[5], SOF8), (Y1, SOF8), (Y1, TOP), (d19[3], TOP)])
    sv.concrete([(d19[3], -FILL), (Y1, -FILL), (Y1, -FILL - 0.20), (d44[5], -FILL - 0.20), (d44[5], ZB), (d44[3], ZB), (d44[3], -FILL - 0.20),
                 (d31[5], -FILL - 0.20), (d31[5], ZB), (d31[3], ZB), (d31[3], -FILL - 0.18), (d19[5], -FILL - 0.18), (d19[5], ZB), (d19[3], ZB)])
    sv.brick_r(T104[1], -FILL, T104[3], sof(d19))                             # βόρειος τοίχος (τούβλο) κάτω από τη Δ1.4
    sv.fill_r(T104[3], T206[1])
    sv.fill_r(T206[3], WS0)
    # νότιος τοίχος στη θέση της εξόδου (η τομή στρίβει στον πεσσό Τ1-10) + μπροστινό μπαλκόνι
    sv.gyp_r(T309[1], -FILL, T309[3], sof(d44))
    sv.brick_r(T110[1], -FILL, T110[3], sof(d44))
    sv.etics_r(T110[3], BALC_Z, ET_S, SOF8)
    sv.rect(T110[3], -FILL, Y1, BALC_Z, fill=(0.90, 0.90, 0.86)); sv.dots(T110[3], -FILL, Y1, BALC_Z, color=(0.62, 0.62, 0.58))
    sv.line(ET_S, BALC_Z, Y1, BALC_Z, color=DARK, lw=0.9)
    sv.poly([(gy - 0.07, BALC_Z), (gy + 0.07, BALC_Z), (gy + 0.04, BALC_Z - 0.055), (gy - 0.04, BALC_Z - 0.055)], fill=WHITE, stroke=RAIN, lw=0.9)
    # ντουλάπα Υπν.2 (τομή)
    wsof = sof(d19)
    sv.poly([(WARD[1], 0), (WARD[3], 0), (WARD[3], LV_BED), (d19[5], LV_BED), (d19[5], wsof), (WARD[1], wsof)], fill=WOOD, stroke=WOOD_S, lw=0.8)
    sv.line(WARD[1], 0, WARD[3], wsof, color=WOOD_S, lw=0.3); sv.line(WARD[1], wsof, WARD[3], 0, color=WOOD_S, lw=0.3)
    sv.rect(d19[5], LV_BED, WARD[3], SOF3, fill=WOOD, stroke=WOOD_S, lw=0.5)
    sv.text((WARD[1] + WARD[3]) / 2, 1.70, "ΝΤΟΥΛΑΠΑ ΥΠΝ.2", size=5.6, color=WOOD_S, font="Inter-Bold", rot=90, bg=True)
    # οροφές
    sv.board(WARD[3], d31[3], LV_BED)
    sv.rect(d31[3] - 0.0125, LV_B50 - 0.0125, d31[3], LV_BED, fill=WHITE, stroke=DARK, lw=0.6)          # μετώπη στη δοκό
    sv.rect(d31[3], LV_B50 - 0.0125, T206[1], LV_B50, fill=WHITE, stroke=DARK, lw=0.6)                   # γυψοσανίδα περασιά κάτω από τη Δ3.1
    sv.board(T206[3], KR2[1], LV_STRIP)
    sv.rect(KR2[1] - 0.0125, LV_STRIP, KR2[1], SOF8, fill=WHITE, stroke=DARK, lw=0.6)                    # μετώπη της κουρτινόθηκης ΚΡ2 (ανοιχτή ως την πλάκα)
    sv.gyp_r(T206[1], -FILL, T206[3], sof(d31))                                                          # τοίχος Τ2-06
    # μονάδα · στόμιο επιστροφής · θυρίδα
    sv.rect(UY0, U_BOT, UY1, U_TOP, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.2)
    sv.text((UY0 + UY1) / 2 + 0.10, (U_BOT + U_TOP) / 2 + 0.04, "ΚΜ1", size=8.5, font="Inter-Bold", color=BLUE)
    sv.text((UY0 + UY1) / 2 + 0.10, (U_BOT + U_TOP) / 2 - 0.07, "το μηχάνημα", size=5.0, color=BLUE)
    sv.rect(RET[1], LV_STRIP - 0.004, RET[3], LV_STRIP + 0.0165, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.8)
    k = RET[1] + 0.06
    while k < RET[3]:
        sv.line(k, LV_STRIP - 0.004, k + 0.03, LV_STRIP + 0.0165, color=GREEN, lw=0.4); k += 0.07
    sv.rect(HATCH[1], LV_STRIP - 0.004, HATCH[3], LV_STRIP + 0.0165, fill=WHITE, stroke=DARK, lw=0.7, dash=[2, 1.2])
    # ---- σωλήνες: μέσα στον τοίχο της πόρτας διακεκομμένοι (κρυμμένοι πίσω από τη γυψοσανίδα)
    sv.pipe([(EXIT_Y, Z_REF), (EXIT_Y, EXIT_Z)], MAG, 1.6, dash=[2.5, 2])                                 # αυλάκι στον πεσσό Τ1-05 (πίσω από τη ντουλάπα)
    sv.pipe([(UY0, Z_R_VOID), (DR[1], Z_R_VOID)], MAG, 2.3)
    sv.pipe([(DR[1], Z_R_VOID), (DR[1], Z_REF)], MAG, 2.0, dash=[3.2, 2.4])
    sv.pipe([(DR[1], Z_REF), (EXIT_Y, Z_REF)], MAG, 2.3)
    sv.pipe([(UY0, Z_C_VOID_START), (DC[1], Z_C_VOID_END)], ORANGE, 1.9)
    sv.pipe([(DC[1], Z_C_VOID_END), (DC[1], Z_C_START + R_CON)], ORANGE, 1.8, dash=[3.2, 2.4])
    sv.pipe([(y_, cond_zy(y_) + R_CON) for y_ in cys], ORANGE, 1.9)
    cross_mark(sv, EXIT_Y, Z_REF, MAG)
    sv.circle(gy, -FILL + 0.032, 3.0, fill=WHITE, stroke=RAIN, lw=1.0, pt=True)                           # Φ50 του σιφωνιού (φεύγει ανατολικά → ΥΔ2)
    # ---- κείμενα χώρων / δοκάρια
    sv.text(3.10, 1.42, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=10, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(7.05, 1.42, "ΚΑΘΙΣΤΙΚΟ", size=10, font="Inter-Bold", color=(0.45, 0.60, 0.60))
    sv.text(7.115, 1.27, "ο τοίχος της πόρτας – ένας τοίχος %s cm" % cm(WE - LIN_X), size=5.0, color=LIN_S, font="Inter-SemiBold")
    sv.text(7.115, 1.16, "(τον βλέπουμε από μέσα – οι σωλήνες είναι μέσα του)", size=4.6, color=LIN_S)
    sv.text(9.98, 1.42, "ΜΠΡΟΣΤΙΝΟ", size=6.6, font="Inter-Bold", color=(0.62, 0.62, 0.66)); sv.text(9.98, 1.30, "ΜΠΑΛΚΟΝΙ", size=6.6, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(0.345, 1.45, "ΒΟΡΕΙΑ ΟΨΗ", size=5.0, color=GREY, rot=90)
    for b_, nm in ((d31, "Δ3.1"), (d44, "Δ4.4")):
        sv.text((b_[3] + b_[5]) / 2, 2.84, "ΔΟΚΑΡΙ", size=5.0, font="Inter-Bold", color=WHITE)
        sv.text((b_[3] + b_[5]) / 2, 2.72, nm, size=6.4, font="Inter-Bold", color=WHITE)
    sv.text((d19[3] + d19[5]) / 2, 2.72, "Δ1.4", size=5.6, font="Inter-Bold", color=WHITE)
    sv.text(3.00, 2.89, "ΠΛΑΚΑ Π3 (πάχος 18)", size=5.4, font="Inter-SemiBold", color=WHITE)
    sv.text(7.60, 2.88, "ΠΛΑΚΑ Π8 (πάχος 20)", size=5.4, font="Inter-SemiBold", color=WHITE)
    sv.text((T110[1] + T110[3]) / 2, 1.20, "ΠΕΣΣΟΣ (τούβλο)", size=5.0, font="Inter-Bold", color=WHITE, rot=90)
    # ---- στάθμες
    sv.level(Y1, TOP, right=True, note="πάνω από την πλάκα")
    sv.level(Y1, SOF8, right=True, note="κάτω από την πλάκα")
    sv.level(Y1, BALC_Z, right=True, note="δάπεδο μπαλκονιού")
    sv.level(Y1, -FILL, right=True, note="πλάκα (γέμισμα 12 cm)")
    sv.level(8.20, LV_STRIP, right=True, below=True, note="οροφή λωρίδας εισόδου – περασιά με το δοκάρι")
    sv.level(2.52, LV_BED, right=True, below=True, note="οροφή Υπν.2 – κανένας σωλήνας της ΚΜ1 εδώ πάνω")
    sv.level(d31[3] - 0.03, LV_B50, right=False, lead=8, note="κάτω από το δοκάρι")
    sv.level(8.20, 0.0, right=True, lead=8, note="δάπεδο")
    # ---- οδηγοί / βήματα
    sv.badge(UY0 + 0.18, (U_BOT + U_TOP) / 2, 1)
    sv.leader(((RET[1] + RET[3]) / 2, LV_STRIP - 0.01), ((RET[1] + RET[3]) / 2, 2.27), ["στόμιο επιστροφής"], anchor="c", size=5.2, color=GREEN, dot=False)
    sv.badge(7.05, 0.98, 2)
    sv.badge(DR[1] - 0.16, 1.36, 3)
    sv.leader((DR[1], 1.72), (4.98, 1.66), ["ΨΥΚΤΙΚΑ: κατεβαίνουν μέσα στον τοίχο", "της πόρτας, βόρεια της πόρτας"], anchor="r", size=5.6, color=MAG)
    sv.badge(3.40, -FILL - 0.105, 4)
    sv.badge(DC[1] + 0.17, 1.78, 5)
    sv.leader((DC[1], 2.02), (6.62, 2.14), ["ΣΥΜΠΥΚΝΩΜΑΤΑ: κατεβαίνουν μέσα στον", "τοίχο της πόρτας, νότια της πόρτας"], anchor="l", size=5.6, color=ORANGE)
    sv.badge(7.90, -FILL - 0.105, 6)
    sv.badge((WS0 + T110[3]) / 2, -FILL - 0.105, 7)
    sv.badge(gy, 0.16, 8)
    sv.leader((gy + 0.03, BALC_Z - 0.02), (9.70, 0.36), ["σιφώνι → ΥΔ2"], anchor="l", size=5.4, color=RAIN)
    sv.leader((EXIT_Y, 0.20), (1.50, 0.60), ["στον πεσσό (πίσω από τη ντουλάπα):", "τα ψυκτικά ανεβαίνουν ως %s" % lv(EXIT_Z), "και βγαίνουν στον ΒΑ εξώστη → ΤΟΜΗ Γ-Γ"],
              anchor="l", size=5.4, color=MAG)
    sv.text((EM[1] + EM[3]) / 2 + 0.26, 0.92, "εξωτ. μονάδα (έξω, στον εξώστη)", size=5.0, color=BLUE, anchor="l", bg=True)
    # ---- ΤΟ ΜΗΝΥΜΑ
    X, Y = sv.p(2.55, 2.46)
    h = msg_box(c, X, Y, 178, "ΚΑΤΩ ΑΠΟ ΔΟΚΑΡΙ ΔΕΝ ΠΕΡΝΑ ΤΙΠΟΤΑ", ["Οι σωλήνες κατεβαίνουν ΜΕΣΑ στον τοίχο της πόρτας", "(δίπλα στο δοκάρι) και φεύγουν από το ΔΑΠΕΔΟ."])
    arrow(c, X + 178, Y - 12, sv.p(d31[3] + 0.08, 0)[0], sv.p(0, LV_B50 - 0.035)[1], color=RED, lw=0.9)
    arrow(c, X + 160, Y - h, sv.p(4.98, 0)[0], sv.p(0, 0.04)[1], color=RED, lw=0.9)
    # ---- διαστάσεις
    sv.dim_h(ZB, [T104[1], WARD[1], WARD[3], T206[1], T206[3], DOOR[0], DOOR[1], UY0, UY1, WS0, T110[3], gy], dy=-13, above=False, size=5.2)
    sv.dim_h(ZB, [EXIT_Y, DR[1]], dy=-31, above=False, color=MAG, fmt=lambda v_: "ΨΥΚΤΙΚΑ: %s m μέσα στο ΔΑΠΕΔΟ του Υπν.2" % mm2(R_FLOOR_LEN), size=5.8)
    sv.dim_h(ZB, [DC[1], gy], dy=-31, above=False, color=ORANGE, fmt=lambda v_: "ΣΥΜΠΥΚΝΩΜΑΤΑ: %s m μέσα στο ΔΑΠΕΔΟ, κλίση 1 %% → σιφώνι" % mm2(C_FLOOR_LEN), size=5.8)
    sv.cut_mark(Y1, ZB, TOP)
    # ---- το δάπεδο σε μεγέθυνση (ίδια οριζόντια κλίμακα, ύψη × 3)
    fz = Sec(c, 40, 262, S, u0=Y0, sz=S * 3)
    c.setFont("Inter-Bold", 8.5); c.setFillColorRGB(*DARK); c.drawString(40, 318, "ΤΟ ΔΑΠΕΔΟ ΣΕ ΜΕΓΕΘΥΝΣΗ")
    c.setFont("Inter", 6.6); c.setFillColorRGB(*GREY)
    c.drawString(164, 318, "ίδιες θέσεις με την τομή από πάνω · τα ύψη × 3, για να φαίνονται οι σωλήνες μέσα στο γέμισμα των 12 cm")
    zb = -0.30
    fz.concrete_r(d19[3], zb, Y1, -FILL)
    fz.brick_r(T104[1], -FILL, T104[3], 0.035)
    fz.rect(T104[3], -FILL, T206[1], 0, fill=FILLC); fz.dots(T104[3], -FILL, T206[1], 0, step=6)
    fz.rect(T206[3], -FILL, WS0, 0, fill=FILLC); fz.dots(T206[3], -FILL, WS0, 0, step=6)
    fz.gyp_r(T206[1], -FILL, T206[3], 0.035)
    fz.gyp_r(T309[1], -FILL, T309[3], 0.035)
    fz.brick_r(T110[1], -FILL, T110[3], 0.035)
    fz.etics_r(T110[3], BALC_Z, ET_S, 0.035)
    fz.rect(T110[3], -FILL, Y1, BALC_Z, fill=(0.90, 0.90, 0.86)); fz.dots(T110[3], -FILL, Y1, BALC_Z, step=6, color=(0.62, 0.62, 0.58))
    fz.rect(WARD[1], 0, WARD[3], 0.035, fill=WOOD, stroke=WOOD_S, lw=0.7)
    fz.line(T104[3], 0, T206[1], 0, color=DARK, lw=1.0); fz.line(T206[3], 0, WS0, 0, color=DARK, lw=1.0); fz.line(ET_S, BALC_Z, Y1, BALC_Z, color=DARK, lw=1.0)
    fz.poly([(gy - 0.07, BALC_Z), (gy + 0.07, BALC_Z), (gy + 0.045, -FILL + 0.012), (gy - 0.045, -FILL + 0.012)], fill=WHITE, stroke=RAIN, lw=1.0)
    band_r = [(DR[1], Z_REF - R_GAS), (EXIT_Y, Z_REF - R_GAS), (EXIT_Y, Z_REF + R_GAS), (DR[1], Z_REF + R_GAS)]
    band_c = [(y_, cond_zy(y_)) for y_ in cys] + [(y_, cond_zy(y_) + 2 * R_CON) for y_ in reversed(cys)]
    c.saveState(); c.setFillAlpha(0.55); fz.poly(band_r, fill=MAG_F); c.restoreState()
    fz.poly(band_r, stroke=MAG, lw=1.0)
    fz.pipe([(DR[1], 0.035), (DR[1], Z_REF)], MAG, 2.0, dash=[3.2, 2.4])
    c.saveState(); c.setFillAlpha(0.60); fz.poly(band_c, fill=ORANGE_F); c.restoreState()
    fz.poly(band_c, stroke=ORANGE, lw=1.0)
    fz.pipe([(DC[1], 0.035), (DC[1], Z_C_START + R_CON)], ORANGE, 1.8, dash=[3.2, 2.4])
    cross_mark(fz, EXIT_Y, Z_REF, MAG, 4.2)
    fz.text(6.30, -0.225, "ΠΛΑΚΑ", size=6, color=WHITE, font="Inter-Bold")
    fz.text(2.9, -0.255, "ΠΛΑΚΑ", size=6, color=WHITE, font="Inter-Bold")
    fz.level(Y1, BALC_Z, right=True, note="δάπεδο μπαλκονιού")
    fz.level(Y1, -FILL, right=True, note="πλάκα")
    fz.level(8.05, 0.0, right=True, lead=8, note="τελικό δάπεδο")
    fz.leader((3.60, Z_REF + 0.004), (3.60, 0.068), ["ΨΥΚΤΙΚΑ: πάνω στην πλάκα, μέσα σε σπιράλ προστασίας, χωρίς ενώσεις"], anchor="c", size=5.6, color=MAG, dot=False)
    fz.leader((7.55, cond_zy(7.55) + R_CON), (7.40, 0.068), ["ΣΥΜΠΥΚΝΩΜΑΤΑ Ø 32: κλίση 1 % προς το μπροστινό μπαλκόνι"], anchor="c", size=5.6, color=ORANGE, dot=False)
    X, Y = fz.p(8.30, cond_zy(8.30) + R_CON)
    arrow(c, X - 20, Y + 0.6, X + 20, Y - 0.6, color=ORANGE, lw=1.0, head=5)
    fz.leader((DC[1] + 0.03, Z_C_START), (6.62, -0.185), ["αρχή: ροή %s" % lv(Z_C_START, 3), "(ράχη %s cm κάτω από το δάπεδο)" % cm(COVER)], anchor="l", size=5.2, color=ORANGE)
    fz.leader((gy - 0.05, Z_C_END), (9.02, -0.215), ["στο σιφώνι: ροή %s" % lv(Z_C_END, 3), "(%s cm πάνω από την πλάκα)" % cm(FILL + Z_C_END)], anchor="r", size=5.2, color=ORANGE)
    fz.text((T206[1] + T206[3]) / 2 - 0.02, 0.068, "τοίχος Τ2-06", size=4.8, color=GYP_S, font="Inter-SemiBold", anchor="r")
    fz.text(DR[1] + 0.04, 0.068, "τοίχος πόρτας", size=4.8, color=LIN_S, font="Inter-SemiBold", anchor="l")
    fz.text((WARD[1] + WARD[3]) / 2, 0.068, "ντουλάπα", size=5.0, color=WOOD_S, font="Inter-SemiBold")
    fz.text((T309[1] + T110[3]) / 2, 0.068, "πεσσός", size=4.8, color=BRICK_H, font="Inter-SemiBold")
    fz.text(gy, 0.05, "σιφώνι", size=4.8, color=RAIN, font="Inter-SemiBold")
    fz.badge(3.80, -FILL - 0.07, 4, r=6)
    fz.badge(7.90, -FILL - 0.07, 6, r=6)
    fz.badge((WS0 + T110[3]) / 2, -FILL - 0.07, 7, r=6)
    fz.badge(gy + 0.22, -FILL / 2, 8, r=6)
    fz.cut_mark(Y1, zb, 0.03)
    X, Y = fz.p(Y0 + 0.14, -FILL / 2)
    c.saveState(); c.translate(X, Y); c.rotate(90); c.setFont("Inter-SemiBold", 5.4); c.setFillColorRGB(*DIMC)
    c.drawCentredString(0, 0, "γέμισμα 12 cm"); c.restoreState()
    # τίτλος / υπόμνημα
    big_title(c, 40, 806, "ΤΟΜΗ Α-Α · κατά μήκος του τοίχου της πόρτας",
              "κοιτάμε προς ανατολή · αριστερά ο βορράς (Υπν.2), δεξιά ο νότος (μπροστινό μπαλκόνι) · στο νότιο άκρο η τομή στρίβει στον πεσσό της εξόδου")
    legend(c, 640, 812, LEG_PIPES[:2] + [("badge", 3, "βήμα της διαδρομής (όπως στην κάτοψη ΚΜ-01)")], size=5.8, w=250, title="")
    legend(c, 900, 812, LEG_PIPES[4:], size=5.8, w=262, title="")
    frame(c, "ΚΜ-02", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Α-Α", "Ψυκτικά → δάπεδο Υπν.2 → ΒΑ εξώστης · συμπυκνώματα → μπροστινό μπαλκόνι",
          "Κλίμακα 1:30 · A3")


# ================================================================ ΚΜ-03 τομή Β-Β (μέσα από το μηχάνημα, κοιτάμε βόρεια)
def cables_inset(c, ox, oy):
    """ΚΜ-03, δεξιά κάτω: τομή 1:10 ΠΑΝΩ ΑΠΟ ΤΗΝ ΠΟΡΤΑ ΕΙΣΟΔΟΥ (κοιτάμε βόρεια). Τα καλώδια του shaft περνούν τον τοίχο της πόρτας κάτω από το
    δοκάρι (όπως R16) και ανεβαίνουν ΜΕΣΑ στο κανάλι του, δίπλα στο δοκάρι – γι' αυτό η οροφή του σπιτιού πάει περασιά με το δοκάρι (R22).
    R02: ο τοίχος είναι ΕΝΑΣ (Τ6Β 22,5 cm) – κάτω από το δοκάρι ο σκελετός των 10 cm με πετροβάμβακα και οι 2 πυράντοχες γυψοσανίδες."""
    S = scale(10)
    U0, U1, Z0 = 9.07, 10.02, 2.13
    iv = Sec(c, ox, oy - Z0 * S, S, u0=U0)
    d91 = BEAM["Δ9.1"]
    b_sof = A.beam_soffit(d91[1])
    DH, FR = 2.20, 0.05                                  # πόρτα 2,20 + κάσα
    # φόντο
    iv.rect(U0, Z0, LIN_X, LV_STRIP, fill=WALL_BG)
    iv.rect(WU_S[2], Z0, U1, LV_STAIR, fill=(0.975, 0.975, 0.975))
    # σκυρόδεμα: πλάκα Π8 – δοκάρι Δ9.1 – πλάκα κλιμακοστασίου
    iv.concrete([(U0, SOF8), (d91[2], SOF8), (d91[2], b_sof), (d91[4], b_sof), (d91[4], SOF6), (U1, SOF6), (U1, TOP), (U0, TOP)])
    # ο ενιαίος τοίχος της πόρτας πάνω από την κάσα (το μέρος του κάτω από το δοκάρι) + κάσα
    wall_core(iv, DH + FR, b_sof)
    iv.rect(WU_S[0], DH, WU_S[2], DH + FR, fill=WOOD, stroke=WOOD_S, lw=0.8)
    iv.rect(WU_S[0] + 0.02, Z0, WU_S[0] + 0.08, DH, fill=WOOD, stroke=WOOD_S, lw=0.6)          # φύλλο πόρτας (κλειστό)
    # το μέρος του τοίχου προς το σπίτι, πάνω από την πόρτα: 2 γυψοσανίδες + κανάλι 5 cm, ανοιχτό επάνω δίπλα στο δοκάρι
    iv.rect(LIN_X + 0.025, DH + 0.025, WU_S[0], LV_STRIP + 0.0125, fill=WHITE)
    iv.rect(LIN_X, DH, LIN_X + 0.025, LV_STRIP + 0.0125, fill=LIN_F, stroke=LIN_S, lw=0.9)
    iv.rect(LIN_X, DH, WU_S[0], DH + 0.025, fill=LIN_F, stroke=LIN_S, lw=0.9)
    iv.rect(LIN_X + 0.025, LV_STRIP + 0.0125, WU_S[0], SOF8, stroke=GYP_S, lw=0.4, dash=[2, 1.5])
    # οροφές: σπίτι (περασιά με το δοκάρι) · ψευδοδοκός + οροφή κλιμακοστασίου
    iv.board(U0, LIN_X, LV_STRIP)
    iv.board(WU_S[2], 9.95, LV_PSB)
    iv.rect(9.95 - 0.0125, LV_PSB, 9.95, LV_STAIR + 0.0125, fill=WHITE, stroke=DARK, lw=0.7)
    iv.board(9.95, U1, LV_STAIR)
    iv.line(d91[4], b_sof, 9.95 - 0.0125, b_sof, color=DARK, lw=0.4, dash=[2, 1.5])
    # καλώδια: μέσα στον ψευδοδοκό → κάτω από το δοκάρι μέσα από τον τοίχο → ΜΕΣΑ στο κανάλι του → πάνω δίπλα στο δοκάρι → κενό της οροφής
    zc = LV_PSB + 0.0125 + 0.017
    xk = (LIN_X + 0.025 + WU_S[0]) / 2
    for dx in (0.0, 0.05):
        iv.circle(9.84 + dx, zc + 0.045, 0.016, fill=CABLE, stroke=CABLE)
    iv.pipe([(9.82, zc), (xk + 0.012, zc), (xk, zc + 0.014), (xk, 2.585), (xk - 0.03, 2.625), (U0 + 0.10, 2.625)], CABLE, 2.4)
    X, Y = iv.p(U0 + 0.10, 2.625)
    arrow(c, X + 8, Y, X - 3, Y, color=CABLE, lw=1.6, head=5.5)
    # κείμενα
    iv.text((d91[2] + d91[4]) / 2, 2.80, "ΔΟΚΑΡΙ", size=5.6, font="Inter-Bold", color=WHITE)
    iv.text((d91[2] + d91[4]) / 2, 2.73, "Δ9.1", size=7.2, font="Inter-Bold", color=WHITE)
    iv.text(9.21, 2.885, "ΠΛΑΚΑ", size=5.6, font="Inter-SemiBold", color=WHITE)
    iv.text(9.17, 2.25, "ΣΠΙΤΙ", size=7.0, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    iv.text(9.84, 2.25, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=6.0, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    iv.text((WU_S[0] + WU_S[2]) / 2, DH + FR / 2, "κάσα", size=4.4, color=WOOD_S)
    iv.text((WU_S[0] + WU_S[2]) / 2, 2.15, "πόρτα", size=4.6, color=WOOD_S)
    iv.text(9.215, 2.665, "καλώδια", size=5.6, font="Inter-SemiBold", color=CABLE)
    iv.leader((9.63, zc), (9.78, 2.345), ["κάτω από το δοκάρι, μέσα από τον τοίχο", "(καθαρό 37,5 mm – σπιράλ ως Ø 32)"], anchor="c", size=5.0, color=CABLE)
    iv.leader((LIN_X + 0.012, 2.33), (9.285, 2.375), ["ο τοίχος", "(ένας)"], anchor="r", size=5.2, color=LIN_S, dot=False)
    iv.text(9.83, 2.63, "ψευδοδοκός", size=4.8, color=GREY)
    iv.level(U0 + 0.02, LV_STRIP, right=True, below=True, lead=5, size=5.8, note="οροφή")
    iv.level(U1 - 0.07, LV_PSB, right=True, below=True, lead=5, size=5.4)
    iv.level(U1 - 0.07, LV_STAIR, right=True, below=True, lead=5, size=5.4)
    iv.cut_mark(U0, Z0, TOP); iv.cut_mark(U1, Z0, TOP)


def sheet_bb(c):
    S = scale(10)
    X0, X1 = 7.80, 10.22
    ZB = -0.36
    sv = Sec(c, 44, 214, S, u0=X0, brk=(0.32, 1.60, 16))
    d91 = BEAM["Δ9.1"]
    b_sof = A.beam_soffit(d91[1])
    # ---- φόντο (βόρειος τοίχος του καθιστικού / κλιμακοστάσιο, πίσω)
    sv.rect(X0, 0, STRIP_X, LV_LIV, fill=WALL_BG)
    sv.rect(STRIP_X, 0, LIN_X, LV_STRIP, fill=WALL_BG)
    sv.rect(WU_S[2], 0, X1, LV_STAIR, fill=(0.975, 0.975, 0.975))
    # ---- φέρων οργανισμός
    sv.concrete([(X0, SOF8), (d91[2], SOF8), (d91[2], b_sof), (d91[4], b_sof), (d91[4], SOF6), (X1, SOF6), (X1, TOP), (X0, TOP)])
    sv.concrete([(X0, -FILL), (X1, -FILL), (X1, -FILL - 0.15), (d91[4], -FILL - 0.15), (d91[4], ZB), (d91[2], ZB), (d91[2], -FILL - 0.20), (X0, -FILL - 0.20)])
    sv.fill_r(X0, LIN_X)
    sv.fill_r(WU_S[2], X1)
    zc_b = cond_zy(7.15)                              # ροή των συμπυκνωμάτων στη θέση της τομής
    sv.circle(CX, zc_b + R_CON, R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.3)                 # συμπυκνώματα μέσα στο γέμισμα (τα κόβει η τομή)
    # ο ΕΝΙΑΙΟΣ τοίχος της πόρτας εισόδου (Τ6Β 22,5 cm): κάτω από το δοκάρι ο σκελετός των 10 cm με πετροβάμβακα + 2 πυράντοχες γυψοσανίδες
    wall_core(sv, -FILL, b_sof, lw=0.8)
    # το μέρος του προς το σπίτι: 2 γυψοσανίδες + ΚΑΝΑΛΙ (σκελετός 5 cm) – ανοιχτό επάνω, ΔΙΠΛΑ στη δοκό
    sv.rect(LIN_X + 0.025, -FILL, WU_S[0], LV_STRIP + 0.0125, fill=WHITE)
    sv.rect(LIN_X, -FILL, LIN_X + 0.025, LV_STRIP + 0.0125, fill=LIN_F, stroke=LIN_S, lw=0.9)
    sv.line(LIN_X + 0.0125, -FILL, LIN_X + 0.0125, LV_STRIP + 0.0125, color=LIN_S, lw=0.3)
    sv.rect(LIN_X + 0.025, LV_STRIP + 0.0125, WU_S[0], SOF8, stroke=GYP_S, lw=0.4, dash=[2, 1.5])          # ορθοστάτης ως την πλάκα (χωρίς γυψοσανίδα πάνω από την οροφή)
    # οροφές: καθιστικό · ΜΕΤΩΠΗ με το slot (R02: το slot στο κατακόρυφο σκαλοπάτι της οροφής – φυσά οριζόντια) · λωρίδα · ψευδοδοκός + οροφή κλιμακοστασίου
    sz0, sz1 = SLOT_Z
    sv.board(X0, STRIP_X, LV_LIV)
    sv.rect(STRIP_X - 0.0125, LV_STRIP, STRIP_X, sz0, fill=WHITE, stroke=DARK, lw=0.7)                 # μετώπη κάτω από το slot
    sv.rect(STRIP_X - 0.0125, sz1, STRIP_X, LV_LIV + 0.0125, fill=WHITE, stroke=DARK, lw=0.7)          # μετώπη πάνω από το slot
    sv.board(STRIP_X, RET[0], LV_STRIP)
    sv.rect(RET[0], LV_STRIP - 0.004, RET[2], LV_STRIP + 0.0165, fill=(0.86, 0.95, 0.91), stroke=GREEN, lw=0.9)
    k = RET[0] + 0.03
    while k < RET[2] - 0.01:
        sv.line(k, LV_STRIP - 0.004, k + 0.015, LV_STRIP + 0.0165, color=GREEN, lw=0.45); k += 0.035
    sv.board(RET[2], LIN_X, LV_STRIP)
    sv.board(WU_S[2], 9.95, LV_PSB)
    sv.rect(9.95 - 0.0125, LV_PSB, 9.95, LV_STAIR + 0.0125, fill=WHITE, stroke=DARK, lw=0.7)
    sv.board(9.95, X1, LV_STAIR)
    # plenum (πίσω από τη μετώπη) + slot στη μετώπη + μονάδα
    pz0, pz1 = sz0, sz0 + 0.20
    assert pz0 >= LV_STRIP + A.SYSTEM - 1e-9 and pz1 <= SOF8 - 0.03, "το plenum δεν χωρά ανάμεσα στην οροφή της λωρίδας και την πλάκα"
    sv.rect(PLEN[0], pz0, PLEN[2], pz1, fill=BLUE_F, stroke=BLUE, lw=0.8)
    sv.rect(STRIP_X - 0.018, sz0, PLEN[0], sz1, fill=(0.30, 0.45, 0.75), stroke=BLUE, lw=0.8)          # το slot μέσα στη μετώπη
    sv.line(STRIP_X - 0.018, (sz0 + sz1) / 2, PLEN[0], (sz0 + sz1) / 2, color=WHITE, lw=0.6)          # οι 2 σχισμές του
    sv.rect(PLEN[2], max(pz0, U_BOT + 0.03), UX0, min(pz1, U_TOP - 0.03), fill=BLUE_F, stroke=BLUE, lw=0.6)
    sv.rect(UX0, U_BOT, UX1, U_TOP, fill=(0.80, 0.88, 0.97), stroke=BLUE, lw=1.3)
    sv.text((UX0 + UX1) / 2 - 0.06, (U_BOT + U_TOP) / 2 + 0.03, "ΚΜ1", size=13, font="Inter-Bold", color=BLUE)
    sv.text((UX0 + UX1) / 2 - 0.06, (U_BOT + U_TOP) / 2 - 0.045, "το μηχάνημα (ύψος ως %s cm)" % cm(UNIT["hmax"]), size=6.0, color=BLUE)
    for xx in (UX0 + 0.08, UX1 - 0.08):
        sv.line(xx, U_TOP, xx, SOF8, color=DARK, lw=0.9)
    sv.text((PLEN[0] + PLEN[2]) / 2, (pz0 + pz1) / 2, "plenum", size=5.6, color=BLUE, font="Inter-SemiBold")
    sv.text((PLEN[0] + PLEN[2]) / 2, pz1 + 0.04, "κενό %s cm" % cm(SOF8 - LV_STRIP), size=5.8, color=DIMC, font="Inter-SemiBold")
    # ροές αέρα: ΟΡΙΖΟΝΤΙΑ από το slot της μετώπης, κολλητά στην οροφή του καθιστικού (R02 – όχι προς τα κάτω)
    for zz in (sz0 + 0.03, sz1 - 0.03):
        sv.arrow(STRIP_X - 0.03, zz, STRIP_X - 0.36, zz, color=BLUE, lw=1.2)
    sv.text(STRIP_X - 0.205, sz0 - 0.045, "ο αέρας φεύγει ΟΡΙΖΟΝΤΙΑ", size=6.2, color=BLUE, anchor="c", font="Inter-SemiBold")
    sv.text(STRIP_X - 0.205, sz0 - 0.085, "προς το καθιστικό", size=6.0, color=BLUE, anchor="c")
    sv.arrow((RET[0] + RET[2]) / 2, LV_STRIP - 0.17, (RET[0] + RET[2]) / 2, LV_STRIP - 0.02, color=GREEN, lw=1.0)
    sv.text((RET[0] + RET[2]) / 2, LV_STRIP - 0.20, "επιστροφή αέρα", size=5.8, color=GREEN)
    # σωλήνες (πίσω από την τομή, στο βόρειο άκρο της μονάδας): μπαίνουν στο κανάλι του τοίχου και κατεβαίνουν – ΔΙΠΛΑ στη δοκό
    xr_, xc_ = DC[0] + 0.011, DC[0] - 0.012          # στην πραγματικότητα σε διαφορετικές παραστάδες – εδώ δίπλα-δίπλα για να φαίνονται και οι δύο
    sv.pipe([(UX1 + 0.012, Z_R_VOID), (xr_, Z_R_VOID), (xr_, Z_REF)], MAG, 1.7, dash=[3.2, 2.2], halo=False)
    sv.pipe([(UX1 + 0.012, Z_C_VOID_START), (xc_, Z_C_VOID_END), (xc_, zc_b + R_CON)], ORANGE, 1.5, dash=[3.2, 2.2], halo=False)
    # καλώδια στον ψευδοδοκό του κλιμακοστασίου
    for dx in (0.0, 0.05, 0.10):
        sv.circle(9.75 + dx, LV_PSB + 0.0125 + 0.016, 0.016, fill=CABLE, stroke=CABLE)
    # ---- κείμενα
    sv.text(8.04, 1.82, "ΚΑΘΙΣΤΙΚΟ", size=12, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(9.90, 0.16, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=8, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(8.40, 0.16, "ΚΑΘΙΣΤΙΚΟ", size=8, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text((BF + GAPW + WE - BRD) / 2, 1.98, "ΤΟΙΧΟΣ ΠΟΡΤΑΣ – ΕΝΑΣ, %s cm" % cm(WE - LIN_X), size=5.8, color=(0.45, 0.38, 0.12), font="Inter-SemiBold", rot=90, bg=True)
    sv.text((d91[2] + d91[4]) / 2, 2.82, "ΔΟΚΑΡΙ", size=6.6, font="Inter-Bold", color=WHITE)
    sv.text((d91[2] + d91[4]) / 2, 2.73, "Δ9.1", size=8.5, font="Inter-Bold", color=WHITE)
    sv.text((d91[2] + d91[4]) / 2, 2.65, "30/50", size=6.2, font="Inter-SemiBold", color=WHITE)
    sv.text(8.25, 2.885, "ΠΛΑΚΑ Π8 (πάχος 20)", size=6.4, font="Inter-SemiBold", color=WHITE)
    sv.leader((LIN_X + 0.012, 1.80), (9.20, 1.80), ["ΤΟ ΚΑΝΑΛΙ ΤΟΥ ΤΟΙΧΟΥ (%s cm)" % cm(LIN_CAV), "πίσω από τις 2 γυψοσανίδες:", "μέσα του κατεβαίνουν οι σωλήνες"],
              anchor="r", size=6.2, color=LIN_S, dot=False)
    sv.leader((xr_ - 0.04, Z_R_VOID + 0.006), (9.30, TOP + 0.075), ["ψυκτικά (πίσω από την τομή): από το βόρειο άκρο του μηχανήματος μέσα στο κανάλι του τοίχου – ΔΙΠΛΑ στο δοκάρι"],
              anchor="r", size=5.8, color=MAG)
    sv.leader((xc_ - 0.03, Z_C_VOID_END + 0.004), (8.90, LV_STRIP - 0.155), ["συμπυκνώματα Ø 32 (πίσω από την τομή): μπαίνουν στο κανάλι του τοίχου"], anchor="r", size=5.8, color=ORANGE)
    sv.leader((9.80, LV_PSB + 0.035), (9.98, 2.26), ["καλώδια του shaft", "(ψευδοδοκός)"], anchor="c", size=5.6, color=CABLE)
    sv.leader((STRIP_X - 0.004, sz1 - 0.012), (8.06, LV_LIV + 0.045), ["SLOT ΣΤΗ ΜΕΤΩΠΗ"], anchor="r", size=6.0, color=BLUE, font="Inter-SemiBold")
    sv.leader((CX - R_CON, zc_b + R_CON), (8.92, 0.245), ["συμπυκνώματα Ø 32 μέσα στο γέμισμα, κολλητά στον τοίχο → μπροστινό μπαλκόνι"], anchor="r", size=5.8, color=ORANGE)
    sv.text(8.40, -FILL / 2, "λωρίδα 20 cm στον τοίχο χωρίς ενδοδαπέδια", size=5.8, color=FILL_H, font="Inter-SemiBold", bg=True)
    # ---- στάθμες
    sv.level(X1, TOP, right=True, lead=8)
    sv.level(X1, LV_STAIR, right=True, lead=8, note="οροφή κλιμακοστασίου")
    sv.level(X1, b_sof, right=True, lead=8, note="κάτω από το δοκάρι")
    sv.line(d91[4], b_sof, X1, b_sof, color=DARK, lw=0.4, dash=[2, 1.5])
    sv.level(X1, 0.0, right=True, lead=8, note="δάπεδο")
    sv.level(X1, -FILL, right=True, lead=8, note="πλάκα")
    sv.level(7.86, LV_LIV, right=True, below=True, note="οροφή καθιστικού")
    sv.level(8.62, LV_STRIP, right=True, below=True, note="οροφή λωρίδας – περασιά με το δοκάρι")
    # ---- διαστάσεις
    sv.dim_h(2.13, [STRIP_X, UX0, UX1, LIN_X], above=True, size=6.2)
    sv.dim_h(2.03, [STRIP_X, LIN_X], above=False, size=6.4, fmt=lambda v_: "ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ %s" % mm2(v_))
    sv.dim_h(2.30, [LIN_X, WE], above=True, size=5.8, fmt=lambda v_: "τοίχος %s" % cm(v_), bg=True)
    sv.dim_v(STRIP_X - 0.44, [LV_STRIP, LV_LIV], left=True, fmt=lambda v_: "μετώπη %s cm" % cm(v_), size=5.6)
    sv.break_band(X0, X1)
    sv.cut_mark(X0, ZB, TOP); sv.cut_mark(X1, ZB, TOP)
    # ---- μήνυμα
    X, Y = sv.p(9.60, 2.08)
    msg_box(c, X, Y, 150, "ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ:", ["κανένας σωλήνας του κλιματιστικού.", "Μόνο τα καλώδια του shaft, πάνω από", "την πόρτα εισόδου – βλ. μικρή τομή δεξιά."], size=6.0)
    arrow(c, X + 8, Y, sv.p(9.585, 0)[0], sv.p(0, LV_PSB + 0.03)[1], color=RED, lw=0.9)
    # ---- δεξιά στήλη
    x, w = 852, 308
    big_title(c, 44, 806, "ΤΟΜΗ Β-Β · μέσα από το μηχάνημα", "κοιτάμε προς βορρά · αριστερά το καθιστικό, δεξιά το κλιμακοστάσιο")
    y = head(c, x, 800, "ΤΙ ΔΕΙΧΝΕΙ Η ΤΟΜΗ")
    y = bullets(c, x, y, w, [
        "Η λωρίδα της εισόδου: οροφή %s = ΠΕΡΑΣΙΑ με τα δοκάρια, πλάτος 1,10 από τον τοίχο της πόρτας, κενό %s cm ως την πλάκα. Μέσα στο κενό: plenum (0,30) · "
        "το μηχάνημα ΚΜ1 (0,70) · 10 cm ως τον τοίχο." % (lv(LV_STRIP), cm(SOF8 - LV_STRIP)),
        "ΤΑ SLOT ΦΥΣΑΝΕ ΜΠΡΟΣΤΑ: είναι στη ΜΕΤΩΠΗ της λωρίδας – το κατακόρυφο σκαλοπάτι της οροφής, %s cm (από %s ως %s) – στο %s…%s. Ο αέρας βγαίνει "
        "οριζόντια προς το καθιστικό, κολλητά στην οροφή του· όχι προς τα κάτω. Στην οροφή της λωρίδας μένει μόνο η επιστροφή."
        % (cm(LV_LIV - LV_STRIP), lv(LV_STRIP), lv(LV_LIV), lv(SLOT_Z[0]), lv(SLOT_Z[1])),
        "Ο ΤΟΙΧΟΣ ΤΗΣ ΠΟΡΤΑΣ ΕΙΝΑΙ ΕΝΑΣ, %s cm, με διπλό σκελετό (όχι τοίχος + πρόσθετη επένδυση): προς το κλιμακοστάσιο 2 πυράντοχες γυψοσανίδες και σκελετός "
        "10 cm με πετροβάμβακα, κάτω από το δοκάρι· προς το σπίτι το ΚΑΝΑΛΙ %s cm και 2 γυψοσανίδες (πυράντοχες κι αυτές)." % (cm(WE - LIN_X), cm(LIN_CAV)),
        "Το κανάλι είναι ΔΙΠΛΑ στο δοκάρι Δ9.1 και ανοιχτό επάνω: οι σωλήνες μπαίνουν από την ψευδοροφή και κατεβαίνουν στο δάπεδο χωρίς να περάσουν κάτω από "
        "δοκάρι. Στο δάπεδο, κολλητά στον τοίχο, τα συμπυκνώματα πάνε προς το μπροστινό μπαλκόνι.",
        "Η κουζίνα έχει την ίδια οροφή %s – ενιαία, χωρίς δόντι. Και τα καλώδια από το κλιμακοστάσιο ανεβαίνουν μέσα στο κανάλι του τοίχου – γι' αυτό η "
        "οροφή δεν χρειάζεται να κατέβει." % lv(LV_STRIP)], size=7.0)
    y = head(c, x, y - 4, "ΤΟ ΜΗΧΑΝΗΜΑ")
    y = bullets(c, x, y, w, [
        "Καναλάτη 24.000 Btu/h τύπου SLIM: ύψος ως %s cm (περιθώριο %s cm – τα slim είναι συνήθως 20–21 cm), βάθος ως 70 cm. Κρέμεται κολλητά στην πλάκα."
        % (cm(UNIT["hmax"]), cm(SOF8 - LV_STRIP - UNIT["hmax"] - A.HANG - A.SYSTEM)),
        "Συνδέσεις ψυκτικών, έξοδος συμπυκνωμάτων (τουλάχιστον στο %s, για να κυλάνε χωρίς αντλία) και ηλεκτρικό κουτί στο ΒΟΡΕΙΟ άκρο. Εκεί και η θυρίδα "
        "60×60." % A.COND_OUT_TXT,
        "Slot μετώπης 2 σχισμών, ύψος ως 12 cm (2 × 1,75 m στη σειρά)· πίσω τους plenum 25 × 20 cm. Μέγεθος / ρύθμιση ρίψης από τον ψυκτικό."], size=7.0)
    # υπόμνημα σε δύο στήλες (για να μένει χώρος για τη μικρή τομή των καλωδίων από κάτω)
    yl = legend(c, x, y - 6, [("box", ((0.80, 0.88, 0.97), BLUE), "μηχάνημα ΚΜ1 · plenum"), ("box", ((0.30, 0.45, 0.75), BLUE), "slot στη μετώπη: αέρας οριζόντια"),
                              ("box", ((0.86, 0.95, 0.91), GREEN), "στόμιο επιστροφής με φίλτρο"), ("box", (LIN_F, LIN_S), "τοίχος πόρτας: 2 γυψοσανίδες + κανάλι")],
                w=w / 2 - 4, size=6.0)
    yr = legend(c, x + w / 2 + 4, y - 6, [("box", (ROCK, ROCK_H), "τοίχος πόρτας: σκελετός 10 cm, πετροβάμβακας"), ("box", (FIRE_F, FIRE_S), "τοίχος πόρτας: 2 πυράντοχες"),
                                          ("line", MAG, "ψυκτικά ΚΜ1"), ("line", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32")], w=w / 2 - 4, size=6.0, title="")
    assert min(yl, yr) > 412, "ΚΜ-03: η δεξιά στήλη πέφτει πάνω στη μικρή τομή των καλωδίων (%.0f)" % min(yl, yr)
    # R01: μικρή τομή πάνω από την πόρτα – τα καλώδια του shaft μέσα από το κανάλι του τοίχου, η οροφή περασιά με το δοκάρι
    yi = 400
    yi = head(c, x, yi, "ΤΑ ΚΑΛΩΔΙΑ – ΤΟΜΗ ΠΑΝΩ ΑΠΟ ΤΗΝ ΠΟΡΤΑ 1:10")
    para(c, x, yi, w, "Κοιτάμε προς βορρά. Τα καλώδια του shaft περνούν τον τοίχο κάτω από το δοκάρι (πάνω από την κάσα, όπως ήταν), μπαίνουν στο κανάλι του "
         "και ανεβαίνουν μέσα του, ΔΙΠΛΑ στο δοκάρι, ως το κενό της οροφής. Έτσι η οροφή του σπιτιού πάει περασιά με το δοκάρι.", size=6.6, color=GREY)
    cables_inset(c, x + 22, 106)
    frame(c, "ΚΜ-03", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Β-Β", "Εγκάρσια στη λωρίδα της εισόδου, μέσα από το μηχάνημα · slot στη μετώπη", "Κλίμακα 1:10 · A3")


# ================================================================ ΚΜ-04 τομή Γ-Γ (έξοδος στον ΒΑ εξώστη, κοιτάμε βόρεια)
def sheet_gg(c):
    S = scale(10)
    X0, X1 = 8.95, 11.52
    ZB = -0.36
    sv = Sec(c, 96, 206, S, u0=X0, brk=(1.05, 2.20, 16))
    d95 = BEAM["Δ9.5"]
    b_sof = A.beam_soffit(d95[1])
    in_face = T306[0]                                # εσωτερική παρειά (επένδυση) 9,395
    br0, br1 = T105[0], T105[2]                      # τούβλο 9,449–9,699
    et1 = BALC[0]                                    # εξωτερική παρειά θερμοπρόσοψης 9,80
    # ---- φόντο: βόρειο στηθαίο του εξώστη (πίσω) · υδρορροή ΥΔ1 (πίσω από τις πλάκες των εξωστών, μέσα στη θερμοπρόσοψη)
    sv.rect(et1, BALC_Z, PAR_E[0], 0.68, fill=CONC_L, stroke=(0.72, 0.72, 0.75), lw=0.4)
    sv.text(10.07, 0.60, "στηθαίο (πίσω)", size=5.2, color=GREY)
    # ---- φέρων οργανισμός
    sv.concrete([(X0, SOF3), (d95[2], SOF3), (d95[2], b_sof), (d95[4], b_sof), (d95[4], SOF3), (BALC[2], SOF3), (BALC[2], TOP), (X0, TOP)])
    sv.concrete([(X0, -FILL), (BALC[2], -FILL), (BALC[2], -FILL - 0.18), (d95[4], -FILL - 0.18), (d95[4], ZB), (d95[2], ZB), (d95[2], -FILL - 0.18), (X0, -FILL - 0.18)])
    sv.concrete_r(PAR_E[0], -FILL, PAR_E[2], 0.68)
    sv.rect(PAR_E[0] + 0.08, 0.68, PAR_E[0] + 0.10, 1.05, fill=(0.80, 0.90, 0.96), stroke=(0.45, 0.60, 0.72), lw=0.4)
    sv.etics_r(br1, BALC_Z, et1, SOF3)               # θερμοπρόσοψη (συνεχής στην όψη)
    sv.brick_r(br0, -FILL, br1, b_sof)               # τούβλο πεσσού
    sv.gyp_r(in_face, -FILL, br0, b_sof)             # επένδυση
    sv.fill_r(X0, in_face)
    sv.rect(et1, -FILL, PAR_E[0], BALC_Z, fill=(0.90, 0.90, 0.86)); sv.dots(et1, -FILL, PAR_E[0], BALC_Z, color=(0.62, 0.62, 0.58))
    sv.line(et1, BALC_Z, PAR_E[0], BALC_Z, color=DARK, lw=0.9)
    sv.rect(br1, -FILL, et1, BALC_Z, fill=(0.90, 0.90, 0.86))
    # ντουλάπα Υπν.2 (τομή)
    sv.rect(X0, 0, in_face, LV_BED, fill=WOOD, stroke=WOOD_S, lw=0.9)
    for zz in (0.08, 0.62, 2.32):
        sv.line(X0, zz, in_face - 0.02, zz, color=WOOD_S, lw=0.35)
    sv.rect(X0, LV_BED, in_face, SOF3, fill=WOOD, stroke=WOOD_S, lw=0.5)
    sv.text(9.17, 2.56, "ΝΤΟΥΛΑΠΑ ΥΠΝ.2", size=7, font="Inter-Bold", color=WOOD_S)
    sv.text(9.17, 2.49, "(μέσα της οι σωλήνες)", size=5.4, color=WOOD_S)
    # εξωτερική μονάδα
    sv.rect(EM[0], 0.06, EM[2], 0.76, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=1.2)
    sv.circle(EM[2] - 0.34, 0.41, 0.26, stroke=BLUE, lw=0.7)
    sv.circle(EM[2] - 0.34, 0.41, 0.04, fill=BLUE)
    sv.rect(EM[0] + 0.05, BALC_Z, EM[0] + 0.13, 0.06, fill=DARK); sv.rect(EM[2] - 0.13, BALC_Z, EM[2] - 0.05, 0.06, fill=DARK)
    sv.text((EM[0] + EM[2]) / 2, 0.90, "ΕΞΩΤΕΡΙΚΗ ΜΟΝΑΔΑ", size=8, font="Inter-Bold", color=BLUE)
    sv.text((EM[0] + EM[2]) / 2, 0.82, "(θέση ενδεικτική – κατά τη μελέτη ψύξης)", size=5.6, color=BLUE)
    # ---- υδρορροή ΥΔ1 (μέσα στη θερμοπρόσοψη, ανάμεσα στις πλάκες) + σιφώνι εξώστη με τον Φ50
    sv.rect(YD1[0] - 0.0375, -FILL - 0.02, YD1[0] + 0.0375, SOF3, fill=(0.80, 0.90, 0.99), stroke=RAIN, lw=1.0)
    gx = GULLY_NE[0][0]
    sv.poly([(gx - 0.07, BALC_Z), (gx + 0.07, BALC_Z), (gx + 0.035, BALC_Z - 0.045), (gx - 0.035, BALC_Z - 0.045)], fill=WHITE, stroke=RAIN, lw=0.9)
    sv.pipe([(gx, BALC_Z - 0.045), (gx, -FILL + 0.027), (YD1[0] + 0.0375, -FILL + 0.027)], RAIN, 3.0)
    # ---- σωλήνες
    zs = EXIT_Z + 0.07                                # ψυκτικά split, λίγο πάνω από της ΚΜ1
    xs = in_face - 0.035
    sv.pipe([(xs, SOF3 - 0.03), (xs, zs), (EM[0], zs)], BLUE2, 1.8, dash=[5, 2.5])
    sv.pipe([(KX, Z_REF), (br0 - 0.03, Z_REF + 0.012), (br0 + 0.03, Z_REF + 0.07), (br0 + 0.03, EXIT_Z), (EM[0], EXIT_Z)], MAG, 3.0)
    sv.circle(KX, Z_REF, R_GAS, fill=MAG_F, stroke=MAG, lw=1.3)
    # ---- κείμενα
    sv.text((d95[2] + d95[4]) / 2, 2.82, "ΔΟΚΑΡΙ", size=6.6, font="Inter-Bold", color=WHITE)
    sv.text((d95[2] + d95[4]) / 2, 2.73, "Δ9.5", size=8.5, font="Inter-Bold", color=WHITE)
    sv.text((d95[2] + d95[4]) / 2, 2.65, "30/55", size=6.2, font="Inter-SemiBold", color=WHITE)
    sv.text((br0 + br1) / 2, 0.66, "ΠΕΣΣΟΣ Τ1-05 (τούβλο 25 cm)", size=6.4, font="Inter-Bold", color=WHITE, rot=90)
    sv.text(10.80, 2.66, "ΒΑ ΕΞΩΣΤΗΣ", size=12, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text((br1 + et1) / 2, 0.74, "θερμοπρόσοψη", size=5.0, color=ETICS_S, rot=90)
    sv.leader((YD1[0] + 0.04, 0.985), (9.90, 0.985), ["ΥΔ1 υδρορροή (μέσα στη θερμοπρόσοψη)"], anchor="l", size=6.0, color=RAIN)
    sv.leader((gx + 0.03, BALC_Z - 0.03), (10.22, -0.215), ["σιφώνι εξώστη → σωλήνας Φ50 → υδρορροή ΥΔ1"], anchor="l", size=6.0, color=RAIN)
    sv.leader((br0 + 0.03, 0.12), (9.34, 0.50), ["ΨΥΚΤΙΚΑ ΚΜ1: αυλάκι στο", "τούβλο ως %s και έξω" % lv(EXIT_Z)], anchor="r", size=6.0, color=MAG)
    sv.leader((10.08, EXIT_Z), (9.90, 0.52), ["ψυκτικά → εξωτερική μονάδα"], anchor="l", size=5.8, color=MAG, dot=False)
    sv.leader((xs, 0.82), (9.32, 0.88), ["ψυκτικά split ΚΜ2 / ΚΜ3:", "κατεβαίνουν ΜΕΣΑ στη", "ντουλάπα, βγαίνουν χαμηλά"], anchor="r", size=5.8, color=BLUE2)
    sv.leader((KX - R_GAS, Z_REF), (8.98, 0.20), ["τα ψυκτικά της ΚΜ1 έρχονται", "μέσα στο γέμισμα, κολλητά", "στον τοίχο"], anchor="l", size=5.8, color=MAG)
    # ---- στάθμες
    sv.level(X0, TOP, right=False, lead=8)
    sv.level(X0, LV_BED, right=False, lead=8, note="οροφή Υπν.2")
    sv.level(X0, 0.0, right=False, lead=8, note="δάπεδο")
    sv.level(X0, -FILL, right=False, lead=8, note="πλάκα")
    sv.level(X1, BALC_Z, right=True, lead=8, note="δάπεδο εξώστη")
    sv.level(9.93, b_sof, right=True, lead=8, note="κάτω από το δοκάρι Δ9.5")
    sv.line(d95[4], b_sof, 9.93, b_sof, color=DARK, lw=0.4, dash=[2, 1.5])
    sv.level(10.12, EXIT_Z, txt=lv(EXIT_Z), right=True, lead=6, color=MAG)
    # βήματα
    sv.badge(KX - 0.02, Z_REF + 0.085, 4)
    sv.break_band(X0, X1)
    sv.cut_mark(X0, ZB, TOP)
    # ---- μήνυμα
    X, Y = sv.p(10.50, 2.52)
    h = msg_box(c, X, Y, 172, "ΨΗΛΑ, ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ: ΤΙΠΟΤΑ", ["Όλοι οι σωλήνες βγαίνουν ΧΑΜΗΛΑ από το τούβλο,", "πίσω από την εξωτερική μονάδα."], size=6.0)
    arrow(c, X, Y - h + 5, sv.p(9.66, 0)[0], sv.p(0, b_sof - 0.07)[1], color=RED, lw=0.9)
    # ---- δεξιά στήλη
    x, w = 858, 302
    big_title(c, 44, 806, "ΤΟΜΗ Γ-Γ · έξοδος των ψυκτικών στον ΒΑ εξώστη", "κοιτάμε προς βορρά · αριστερά η ντουλάπα του Υπν.2, δεξιά ο ΒΑ εξώστης")
    y = steps_panel(c, x, 800, w, only=(4,), title="ΤΑ ΨΥΚΤΙΚΑ ΒΓΑΙΝΟΥΝ ΣΤΟΝ ΒΑ ΕΞΩΣΤΗ", size=7.0)
    y = head(c, x, y - 6, "ΠΡΟΣΟΧΗ ΣΤΗΝ ΚΑΤΑΣΚΕΥΗ")
    y = bullets(c, x, y, w, [
        "Στο χτίσιμο του πεσσού Τ1-05 αφήνεται αυλάκι 12 × 6 cm ως τα 30 cm πάνω από το δάπεδο, μέσα στη ντουλάπα – όχι σκάψιμο μετά.",
        "Η έξοδος σφραγίζεται και στεγανώνεται πριν από τη θερμοπρόσοψη.",
        "Ψυκτικά μέσα στο δάπεδο: προμονωμένος χαλκός ΧΩΡΙΣ ενώσεις, μέσα σε σπιράλ. Δοκιμή με άζωτο ΠΡΙΝ πέσει το γέμισμα.",
        "Από εδώ βγαίνουν ΜΟΝΟ τα ψυκτικά. Τα συμπυκνώματα της ΚΜ1 πάνε στο σιφώνι του μπροστινού μπαλκονιού (φύλλο ΚΜ-05).",
        "Η θέση και ο τύπος της εξωτερικής μονάδας ορίζονται από τη μελέτη ψύξης – η έξοδος των σωλήνων μετακινείται ανάλογα πάνω στον ίδιο πεσσό."])
    legend(c, x, y - 8, LEG_PIPES[:1] + LEG_PIPES[2:4] + LEG_PIPES[5:], w=w)
    frame(c, "ΚΜ-04", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΤΟΜΗ Γ-Γ", "Έξοδος των ψυκτικών στον ΒΑ εξώστη, χαμηλά από τον πεσσό", "Κλίμακα 1:10 · A3")


# ================================================================ ΚΜ-05 έξοδος των συμπυκνωμάτων στο μπροστινό μπαλκόνι (τομή + κάτοψη 1:10)
def sheet_dd(c):
    S = scale(10)
    Yd0, Yd1 = 8.30, 10.30
    ZB, ZT = -0.40, 0.62
    sv = Sec(c, 74, 588, S, u0=Yd0)
    d44 = BEAM["Δ4.4"]
    gy = GS[1]
    ys = [Yd0, _CF[2][1], PY0, PY1, gy - 0.045]
    # ---- φόντο
    sv.rect(Yd0, 0, T309[1], ZT, fill=WALL_BG)
    sv.rect(ET_S, BALC_Z, Yd1, ZT, fill=CONC_L, stroke=(0.72, 0.72, 0.75), lw=0.4)                       # τοιχείο του εξώστη (πίσω)
    # ---- φέρων οργανισμός: πλάκα · δοκάρι Δ4.4 κάτω από τον τοίχο · πλάκα μπαλκονιού
    sv.concrete([(Yd0, -FILL), (Yd1, -FILL), (Yd1, -FILL - 0.20), (d44[5], -FILL - 0.20), (d44[5], ZB), (d44[3], ZB), (d44[3], -FILL - 0.20), (Yd0, -FILL - 0.20)])
    sv.fill_r(Yd0, T309[1])
    # τοίχος στη θέση της εξόδου: επένδυση Τ3-09 · πεσσός τούβλου Τ1-10 · θερμοπρόσοψη
    sv.gyp_r(T309[1], -FILL, T309[3], ZT)
    sv.brick_r(T110[1], -FILL, T110[3], ZT)
    sv.etics_r(T110[3], BALC_Z + 0.10, ET_S, ZT)
    sv.rect(T110[3], -FILL, ET_S, BALC_Z + 0.10, fill=(0.84, 0.84, 0.82), stroke=DARK, lw=0.4)             # ζώνη στεγάνωσης / σοβατεπί
    # επίστρωση μπαλκονιού + σιφώνι
    sv.rect(ET_S, -FILL, Yd1, BALC_Z, fill=(0.90, 0.90, 0.86)); sv.dots(ET_S, -FILL, Yd1, BALC_Z, color=(0.62, 0.62, 0.58))
    sv.rect(ET_S, BALC_Z - 0.015, Yd1, BALC_Z, fill=(0.80, 0.74, 0.66), stroke=DARK, lw=0.4)             # πλακάκι
    sv.poly([(gy - 0.075, BALC_Z), (gy + 0.075, BALC_Z), (gy + 0.05, -FILL + 0.008), (gy - 0.05, -FILL + 0.008)], fill=WHITE, stroke=RAIN, lw=1.2)
    for k in range(-2, 3):
        sv.line(gy + k * 0.025, BALC_Z, gy + k * 0.025, BALC_Z - 0.012, color=RAIN, lw=0.7)              # σχάρα
    sv.circle(gy, -FILL + 0.008 + 0.025, 0.025, fill=(0.80, 0.90, 0.99), stroke=RAIN, lw=1.2)             # Φ50 του σιφωνιού (φεύγει ανατολικά → ΥΔ2)
    # ο σωλήνας Ø 32 σε πραγματικό πάχος, με την κλίση του · χιτώνιο / σφράγιση στη διέλευση
    band = [(y_, cond_zy(y_)) for y_ in ys] + [(y_, cond_zy(y_) + 2 * R_CON) for y_ in reversed(ys)]
    sv.rect(T309[1], cond_zy(PY0) - 0.012, ET_S, cond_zy(PY0) + 2 * R_CON + 0.008, fill=WHITE, stroke=DARK, lw=0.5, dash=[2, 1.5])
    sv.poly(band, fill=ORANGE_F, stroke=ORANGE, lw=1.3)
    X, Y = sv.p(8.66, cond_zy(8.66) + R_CON)
    arrow(c, X - 24, Y + 0.8, X + 24, Y - 0.8, color=ORANGE, lw=1.0, head=5)
    # ---- κείμενα
    sv.text(8.66, 0.47, "ΚΑΘΙΣΤΙΚΟ", size=11, font="Inter-Bold", color=(0.62, 0.62, 0.66))
    sv.text(9.93, 0.47, "ΜΠΡΟΣΤΙΝΟ ΜΠΑΛΚΟΝΙ", size=9, font="Inter-Bold", color=(0.55, 0.55, 0.60))
    sv.text(9.93, 0.385, "(τοιχείο του εξώστη πίσω)", size=5.6, color=GREY)
    sv.text((T110[1] + T110[3]) / 2, 0.30, "ΠΕΣΣΟΣ Τ1-10 (τούβλο 25)", size=6.2, font="Inter-Bold", color=WHITE, rot=90)
    sv.text((T110[3] + ET_S) / 2, 0.40, "θερμοπρόσοψη", size=5.0, color=ETICS_S, rot=90)
    sv.text((d44[3] + d44[5]) / 2, -0.355, "ΔΟΚΑΡΙ Δ4.4", size=6.0, font="Inter-Bold", color=WHITE)
    sv.text(8.72, -0.225, "ΠΛΑΚΑ", size=7.5, font="Inter-Bold", color=WHITE); sv.text(9.98, -0.225, "ΠΛΑΚΑ ΜΠΑΛΚΟΝΙΟΥ", size=6.4, font="Inter-Bold", color=WHITE)
    sv.leader((8.50, cond_zy(8.50) + 2 * R_CON), (8.36, 0.26), ["ΣΥΜΠΥΚΝΩΜΑΤΑ Ø 32 μέσα στο γέμισμα", "κλίση 1 % προς το μπαλκόνι"], anchor="l", size=6.0, color=ORANGE)
    sv.leader(((T110[1] + T110[3]) / 2 - 0.06, cond_zy(PY0) + 2 * R_CON), (8.36, 0.115), ["περνά από την ΠΡΩΤΗ ΣΕΙΡΑ του τούβλου, πάνω από την πλάκα",
              "(χιτώνιο + σφράγιση) – σκυρόδεμα δεν τρυπιέται"], anchor="l", size=6.0, color=DARK, dot=False)
    sv.leader((gy + 0.035, BALC_Z - 0.035), (9.84, 0.27), ["ΣΙΦΩΝΙ του μπροστινού μπαλκονιού:", "ο Ø 32 μπαίνει πλάγια στο σώμα του"], anchor="l", size=5.8, color=RAIN)
    sv.leader((gy + 0.026, -FILL + 0.033), (9.90, 0.11), ["Φ50 του σιφωνιού → ΥΔ2", "(φεύγει ανατολικά – βλ. κάτοψη)"], anchor="l", size=5.8, color=RAIN)
    sv.badge(8.37, -0.375, 6, r=6)
    sv.text(8.43, -0.375, "ροή εδώ %s (ράχη %s cm κάτω από το δάπεδο)" % (lv(cond_zy(8.37), 3), cm(-cond_zy(8.37) - 2 * R_CON)), size=5.8, color=ORANGE, anchor="l", font="Inter-SemiBold")
    sv.badge((T110[1] + T110[3]) / 2, 0.555, 7, r=6)
    sv.badge(gy, 0.075, 8, r=6)
    sv.text(9.50, -0.375, "στο σιφώνι: ροή %s = %s cm πάνω από την πλάκα" % (lv(Z_C_END, 3), cm(FILL + Z_C_END)), size=5.8, color=ORANGE, anchor="l", font="Inter-SemiBold")
    # ---- στάθμες / διαστάσεις
    sv.level(Yd0, 0.0, right=False, lead=8)
    sv.level(Yd1, BALC_Z, right=True, lead=8, note="μπαλκόνι")
    sv.level(Yd1, -FILL, right=True, lead=8, note="πλάκα")
    sv.dim_h(ZB, [T309[1], T309[3], T110[3], ET_S, gy], dy=-13, above=False, size=6.0, fmt=cm)
    sv.text(Yd0 + 0.03, -FILL / 2 + 0.035, "γέμισμα %s cm" % cm(FILL), size=5.6, color=FILL_H, font="Inter-SemiBold", anchor="l")
    sv.cut_mark(Yd0, ZB, ZT); sv.cut_mark(Yd1, ZB, ZT)
    X, Y = sv.p(8.36, 0.60)
    big_title(c, 44, 806, "ΕΞΟΔΟΣ ΤΩΝ ΣΥΜΠΥΚΝΩΜΑΤΩΝ ΣΤΟ ΜΠΡΟΣΤΙΝΟ ΜΠΑΛΚΟΝΙ", "τομή κατά μήκος του σωλήνα (το νότιο άκρο της τομής Α-Α σε 1:10), κοιτάμε προς ανατολή · δεξιά η κάτοψη")
    # ---- κάτοψη 1:10 (δεξιά)
    clip = (8.36, 8.52, 9.84, 10.14)
    v = plan_bg(c, A, 734 - clip[0] * S, PAGE_H - 772 - clip[1] * S, S, clip)
    lining_plan(v)
    v.rect(*T110, stroke=BRICK_H, lw=1.4)
    vpipe(v, GULLY, RAIN, 5.0, halo=False)
    v.rect(GS[0] - 0.075, GS[1] - 0.075, GS[0] + 0.075, GS[1] + 0.075, fill=WHITE, stroke=RAIN, lw=1.4)
    v.line(GS[0] - 0.075, GS[1] - 0.075, GS[0] + 0.075, GS[1] + 0.075, color=RAIN, lw=0.6); v.line(GS[0] - 0.075, GS[1] + 0.075, GS[0] + 0.075, GS[1] - 0.075, color=RAIN, lw=0.6)
    v.circle(YD2[0], YD2[1], 0.0375, fill=(0.80, 0.90, 0.99), stroke=RAIN, lw=1.4)
    vpipe(v, [(CX, clip[1]), _CF[2], _CF[3], _CF[4], (GS[0] + 0.05, GS[1] - 0.045)], ORANGE, 4.5)
    v.text(8.62, 8.70, "ΚΑΘΙΣΤΙΚΟ", size=9, font="Inter-Bold", color=GREY)
    v.text(9.62, 8.70, "άνοιγμα", size=6.0, color=GREY); v.text(9.62, 8.80, "κουζίνας", size=6.0, color=GREY)
    v.text(8.62, 10.04, "ΜΠΡΟΣΤΙΝΟ ΜΠΑΛΚΟΝΙ", size=7.5, font="Inter-Bold", color=GREY)
    v.text((K8[0] + K8[2]) / 2 + 0.05, (K8[1] + K8[3]) / 2, "ΚΟΛΟΝΑ Κ8", size=7.5, font="Inter-Bold", color=WHITE)
    vlabel(v, 8.40, 9.02, ["Ø 32 μέσα στο γέμισμα", "του καθιστικού"], color=ORANGE, to=(CX - 0.14, 8.92), size=6.0)
    vlabel(v, 8.40, 9.33, ["ΠΕΣΣΟΣ Τ1-10 (τούβλο):", "ο Ø 32 περνά από τη βάση του"], color=BRICK_H, to=(T110[0] + 0.01, 9.36), size=6.0)
    vlabel(v, 8.40, 9.92, ["ΣΙΦΩΝΙ μπαλκονιού"], color=RAIN, to=(GS[0] - 0.08, GS[1] + 0.03), size=6.2)
    vlabel(v, 9.44, 9.95, ["ΥΔ2 υδρορροή", "(στο κενό δίπλα στην κολόνα)"], color=RAIN, to=(YD2[0] + 0.035, YD2[1] + 0.02), size=6.0)
    vlabel(v, 9.22, 10.08, ["τοιχείο του εξώστη"], color=GREY, to=(FIN[2] - 0.05, 10.02), size=5.6)
    vdim(v, "H", 9.085, [T110[0], PX, T110[2]], size=6.0, side=-1)
    c.restoreState()
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(X0, Y1 + 8, "ΚΑΤΟΨΗ 1:10 – ο πεσσός, το σιφώνι και η υδρορροή ΥΔ2")
    north_arrow(c, X1 - 18, Y1 - 22, 8)
    # ---- κείμενα (κάτω από την τομή)
    x, w = 44, 300
    y = steps_panel(c, x, 432, w, only=(6, 7, 8), title="ΤΑ ΤΕΛΕΥΤΑΙΑ ΒΗΜΑΤΑ ΤΩΝ ΣΥΜΠΥΚΝΩΜΑΤΩΝ", size=7.0)
    legend(c, x, y - 6, LEG_PIPES[1:2] + LEG_PIPES[3:4] + LEG_PIPES[5:], w=w, size=6.0)
    x2, w2 = 372, 300
    y2 = head(c, x2, 432, "ΠΡΟΣΟΧΗ ΣΤΗΝ ΚΑΤΑΣΚΕΥΗ")
    bullets(c, x2, y2, w2, [
        "Στο χτίσιμο του πεσσού Τ1-10 αφήνεται κενό (ή χιτώνιο Ø 50) στην πρώτη σειρά, πάνω στην πλάκα. Δεν τρυπιέται ούτε η κολόνα ούτε το δοκάρι.",
        "Η διέλευση σφραγίζεται και στεγανώνεται μαζί με τη στεγάνωση του μπαλκονιού, πριν από τη θερμοπρόσοψη.",
        "Ο σωλήνας στρώνεται χαμηλά: στο σιφώνι η ροή είναι %s cm πάνω από την πλάκα. Στο μπαλκόνι μένει μέσα στην επίστρωση, κάτω από το πλακάκι." % cm(FILL + Z_C_END),
        "Σύνδεση στο σιφώνι: πλάγια είσοδος στο σώμα του (σιφώνι με πλαϊνή είσοδο) ή συμβολή 45° στον Φ50 του αμέσως μετά – το διαλέγει ο υδραυλικός.",
        "Το νερό πάει σε υδρορροή ομβρίων (ΥΔ2): δεν χρειάζεται οσμοπαγίδα.",
        "Το δάπεδο του μπαλκονιού θεωρήθηκε 2 cm χαμηλότερα από το εσωτερικό· και χαμηλότερο να γίνει, ο σωλήνας χωρά (είναι δίπλα στην πλάκα).",
        "Δοκιμή με νερό πριν από το γέμισμα."], size=6.8)
    frame(c, "ΚΜ-05", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΕΞΟΔΟΣ ΣΥΜΠΥΚΝΩΜΑΤΩΝ", "Στο σιφώνι του μπροστινού μπαλκονιού → ΥΔ2 · από τη βάση του πεσσού Τ1-10", "Κλίμακα 1:10 · A3")


# ================================================================ ΚΜ-06 λεπτομέρειες 1:5
def _jamb_plan(c, oxl, oyt, y0, y1, north):
    """Κάτοψη 1:5 του τοίχου της πόρτας σε μία παραστάδα (north: βόρεια με τα ψυκτικά – αλλιώς νότια με τα συμπυκνώματα). (oxl, oyt) = πάνω-αριστερά σε pt."""
    S = scale(5)
    x0, x1 = 8.98, 9.72
    v = View(c, oxl - x0 * S, PAGE_H - oyt - y0 * S, S)
    X0, Y0 = v.p(x0, y1); X1, Y1 = v.p(x1, y0)
    c.saveState()
    pth = c.beginPath(); pth.rect(X0, Y0, X1 - X0, Y1 - Y0); c.clipPath(pth, stroke=0, fill=0)
    c.setFillColorRGB(1, 1, 1); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=0, fill=1)
    FB, FS, STUD = (0.74, 0.86, 0.78), (0.25, 0.45, 0.35), (0.50, 0.55, 0.63)
    ya, yb = (WC_N[1], WC_N[3]) if north else (WC_S[1], y1)            # τμήμα του τοίχου μέσα στο παράθυρο
    dy_ = DOOR[0] if north else DOOR[1]                                # λαμπάς της πόρτας
    v.rect(x0, T206[3] if north else y0, LIN_X, y1, fill=(0.975, 0.97, 0.96))                          # καθιστικό
    v.rect(WU_S[2], K3[3] if north else y0, x1, y1, fill=(0.955, 0.955, 0.955))                         # κλιμακοστάσιο
    if north:
        v.rect(x0, y0, T206[2], T206[1], fill=(0.975, 0.97, 0.96))                                      # Υπν.2
        v.rect(K3[0], y0, K3[2], K3[3], fill=CONC)                                                      # κολόνα Κ3
        v.hatch([[K3[0], y0], [K3[2], y0], [K3[2], K3[3]], [K3[0], K3[3]]], 0.02, 45, CONC_H, 0.35)
        v.rect(K3[0], y0, K3[2], K3[3], stroke=DARK, lw=0.9)
        v.rect(K3[0] - 0.034, y0, K3[0], T206[1], fill=GYP, stroke=GYP_S, lw=0.5)                       # Τ9-03 κολλητή γυψοσανίδα (Υπν.2)
        for (a, b) in ((T206[1], T206[1] + 0.025), (T206[3] - 0.025, T206[3])):                         # τοίχος Τ2-06: 2 + 2 γυψοσανίδες, CW 50
            v.rect(x0, a, T206[2], b, fill=GYP, stroke=GYP_S, lw=0.6)
        v.rect(x0, T206[1] + 0.025, T206[2], T206[3] - 0.025, fill=(0.97, 0.97, 0.93))
    # ο ΕΝΙΑΙΟΣ τοίχος Τ6Β: προς το κλιμακοστάσιο 2 πυράντοχες γυψοσανίδες · σκελετός CW 100 με πετροβάμβακα · κενό 2,5 cm (ενιαίο με το κανάλι)
    v.rect(WE - BRD, ya, WE, yb, fill=FB, stroke=FS, lw=0.6)
    v.line(WE - BRD / 2, ya, WE - BRD / 2, yb, color=FS, lw=0.3)
    v.rect(BF, ya, BF + GAPW, yb, fill=WHITE)
    v.rect(BF + GAPW, ya, WE - BRD, yb, fill=ROCK)
    v.hatch([[BF + GAPW, ya], [WE - BRD, ya], [WE - BRD, yb], [BF + GAPW, yb]], 0.012, 60, ROCK_H, 0.3)
    v.line(BF + GAPW, ya, BF + GAPW, yb, color=STUD, lw=0.5)
    # προς το σπίτι: 2 γυψοσανίδες + ΚΑΝΑΛΙ (σκελετός CW 50, 5 cm) · επιστροφή γυψοσανίδας στη λαμπά της πόρτας · ορθοστάτης δίπλα της
    v.rect(LIN_X + 0.025, ya, WU_S[0], yb, fill=WHITE)
    v.rect(LIN_X, ya, LIN_X + 0.025, yb, fill=LIN_F, stroke=LIN_S, lw=0.9)
    v.line(LIN_X + 0.0125, ya, LIN_X + 0.0125, yb, color=LIN_S, lw=0.3)
    e0, e1 = (dy_ - 0.0125, dy_) if north else (dy_, dy_ + 0.0125)
    v.rect(LIN_X, e0, WU_S[0], e1, fill=LIN_F, stroke=LIN_S, lw=0.9)
    s0 = e0 - 0.05 if north else e1                                    # ορθοστάτης CW 50: κορμός στο πλάτος του κενού, πέλματα 5 cm κατά μήκος του τοίχου
    wy = s0 + 0.044 if north else s0
    v.rect(LIN_X + 0.025, wy, WU_S[0], wy + 0.006, fill=STUD)
    v.rect(LIN_X + 0.025, s0, LIN_X + 0.031, s0 + 0.05, fill=STUD); v.rect(WU_S[0] - 0.006, s0, WU_S[0], s0 + 0.05, fill=STUD)
    # κάσα της πόρτας ασφαλείας (στην πλευρά του κλιμακοστασίου, στον σκελετό των 10 cm) + φύλλο
    f0, f1 = (dy_, dy_ + 0.045) if north else (dy_ - 0.045, dy_)
    v.rect(WU_S[0] - 0.012, f0, WU_S[2] + 0.02, f1, fill=(0.80, 0.72, 0.60), stroke=WOOD_S, lw=0.7)
    if north:
        v.rect(x0, f1, WU_S[0] - 0.012, f1 + 0.055, fill=(0.93, 0.89, 0.82), stroke=WOOD_S, lw=0.9)                # φύλλο ανοιχτό 90° (μεντεσές βόρεια)
    # σωλήνες μέσα στο κενό (πραγματικές διάμετροι)
    labs = []
    if north:
        pg = (DR[0], s0 - 0.004 - R_GAS); pl = (DR[0], WC_N[1] + 0.006 + R_LIQ); pk = (LIN_X + 0.025 + 0.012, (pg[1] - R_GAS + pl[1] + R_LIQ) / 2)
        v.circle(pg[0], pg[1], R_GAS, fill=MAG_F, stroke=MAG, lw=1.0); v.circle(pg[0], pg[1], 0.0159 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
        v.circle(pl[0], pl[1], R_LIQ, fill=MAG_F, stroke=MAG, lw=1.0); v.circle(pl[0], pl[1], 0.0095 / 2, fill=(0.85, 0.55, 0.30), stroke=MAG, lw=0.6)
        v.circle(pk[0], pk[1], 0.006, fill=(0.80, 0.92, 0.85), stroke=CABLE, lw=1.0)
        labs = [(pl, R_LIQ, 5.185, "υγρού 3/8″ με τη μόνωση (Ø %d)" % math.ceil(R_LIQ * 2000 - 1e-6), MAG),
                (pg, R_GAS, 5.245, "αερίου 5/8″ με μόνωση 13 mm (Ø %d)" % round(R_GAS * 2000), MAG),
                (pk, 0.006, 5.305, "καλώδιο εντολής", CABLE)]
    else:
        pc = DC
        c.setDash([1.5, 1.2]); v.circle(pc[0], pc[1], R_CON + 0.006, stroke=ORANGE, lw=0.5); c.setDash([])
        v.circle(pc[0], pc[1], R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.2)
        labs = [(pc, R_CON, y1 - 0.045, "συμπυκνώματα PVC Ø 32 (με μόνωση 6 mm: Ø 44)", ORANGE)]
    c.restoreState()
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    for (pt_, rr, yy, txt, col) in labs:
        Xa, Ya = v.p(pt_[0] - rr, pt_[1]); Xb, Yb = v.p(9.26, yy)
        c.setStrokeColorRGB(*col); c.setLineWidth(0.5); c.line(Xa, Ya, Xb, Yb)
        w_ = pdfmetrics.stringWidth(txt, "Inter-SemiBold", 6.0)
        c.setFillColorRGB(1, 1, 1); c.rect(Xb - w_ - 4.5, Yb - 3.4, w_ + 3, 8.2, stroke=0, fill=1)
        c.setFont("Inter-SemiBold", 6.0); c.setFillColorRGB(*col); c.drawRightString(Xb - 3, Yb - 2.2, txt)
    v.text(9.645, (y1 - 0.03) if north else (WC_S[1] + y1) / 2 + 0.06, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=6.0, color=GREY, font="Inter-SemiBold")
    v.text(9.00, (y1 - 0.03) if north else (y0 + 0.035), "ΚΑΘΙΣΤΙΚΟ", size=6.5, color=GREY, font="Inter-SemiBold", anchor="l")
    if north:
        v.text(9.56, 5.085, "ΚΟΛΟΝΑ Κ3", size=8, font="Inter-Bold", color=WHITE)
        v.text(9.00, 5.10, "ΤΟΙΧΟΣ Τ2-06", size=6.0, color=GYP_S, font="Inter-SemiBold", bg=True, anchor="l")
        v.text(9.14, 5.375, "ΦΥΛΛΟ ΠΟΡΤΑΣ ΕΙΣΟΔΟΥ (ανοιχτό)", size=6.0, color=WOOD_S, font="Inter-SemiBold")
        v.text(9.63, 5.325, "κάσα", size=5.4, color=WOOD_S)
        vdim(v, "V", 9.585, [WC_N[1], DOOR[0]], size=6.0, side=1)
        vdim(v, "H", y1 - 0.022, [LIN_X, WE], size=6.2, side=-1, fmt=lambda v_: "ένας τοίχος %s cm" % cm(v_))
    else:
        v.text(9.63, 6.275, "κάσα", size=5.4, color=WOOD_S)
        v.text(9.475, 6.238, "ΑΝΟΙΓΜΑ ΠΟΡΤΑΣ", size=5.6, color=WOOD_S, font="Inter-SemiBold")
        vdim(v, "V", 9.60, [DOOR[1], DC[1]], size=6.0, side=1)
        vdim(v, "H", y1 - 0.022, [LIN_X, LIN_X + BRD, BF, BF + GAPW, WE - BRD, WE], size=5.4, side=-1, fmt=cm)
    return v


def sheet_det(c):
    S = scale(5)
    # ---------------- (α) κάτοψη του τοίχου της πόρτας στις δύο παραστάδες
    c.setFont("Inter-Bold", 10); c.setFillColorRGB(*DARK); c.drawString(40, 792, "α · Ο ΤΟΙΧΟΣ ΤΗΣ ΠΟΡΤΑΣ – ΕΝΑΣ ΤΟΙΧΟΣ %s cm – κάτοψη 1:5" % cm(WE - LIN_X))
    c.setFont("Inter", 7); c.setFillColorRGB(*GREY)
    c.drawString(40, 781.5, "πάνω: βόρεια της πόρτας (ψυκτικά) · κάτω: νότια της πόρτας (συμπυκνώματα) · ανάμεσα το άνοιγμα της πόρτας 1,00")
    _jamb_plan(c, 40, 770, 5.04, 5.44, True)
    _jamb_plan(c, 40, 526, 6.22, 6.62, False)
    c.setFont("Inter-SemiBold", 6.4); c.setFillColorRGB(*GREY); c.drawCentredString(250, 532, "· · ·  άνοιγμα πόρτας εισόδου 1,00  · · ·")
    y = head(c, 40, 280, "ΤΙ ΒΛΕΠΟΥΜΕ", 8.5)
    bullets(c, 40, y, 420, [
        "ΕΝΑΣ τοίχος %s cm με διπλό σκελετό – όχι τοίχος και πρόσθετη επένδυση. Στρώσεις (κάτω κάτοψη): 2,5 · 5 · 2,5 · 10 · 2,5 cm." % cm(WE - LIN_X),
        "Πράσινο: 2 πυράντοχες γυψοσανίδες προς το κλιμακοστάσιο. Κίτρινο: σκελετός 10 cm με πετροβάμβακα (κάτω από το δοκάρι), εκεί και η κάσα της πόρτας.",
        "Γαλαζοπράσινο: 2 γυψοσανίδες προς το σπίτι (πυράντοχες)· στη λαμπά της πόρτας γυρίζουν και κλείνουν. Λευκό: το ΚΑΝΑΛΙ (σκελετός %s cm) – εκεί κατεβαίνουν οι "
        "σωλήνες, σχεδιασμένοι στο πραγματικό τους πάχος: χωράνε." % cm(LIN_CAV),
        "Το φύλλο της πόρτας ανοίγει 90° μπροστά από τη λαμπά – δεν βρίσκει πουθενά."], size=6.8)
    # ---------------- (β) τομή δαπέδου στον τοίχο της πόρτας (Δ–Α, κοιτάμε βόρεια) στο y = 7,15
    u0, u1 = 8.80, 9.72
    sv = Sec(c, 520, 590, S, u0=u0)
    zb, zt = -0.34, 0.26
    zc = cond_zy(7.15)
    strip0 = LIN_X - 0.20
    d91 = BEAM["Δ9.1"]
    sv.rect(u0, 0, LIN_X, zt, fill=(0.975, 0.97, 0.96))
    sv.rect(WU_S[2], 0, u1, zt, fill=(0.955, 0.955, 0.955))
    sv.concrete([(u0, -FILL), (u1, -FILL), (u1, -FILL - 0.15), (d91[4], -FILL - 0.15), (d91[4], zb), (d91[2], zb), (d91[2], -FILL - 0.20), (u0, -FILL - 0.20)])
    sv.rect(u0, -FILL, strip0, -FILL + 0.03, fill=(0.80, 0.88, 0.96), stroke=(0.45, 0.55, 0.70), lw=0.4)      # ενδοδαπέδια (ενδεικτικά)
    sv.rect(u0, -FILL + 0.03, strip0, -0.015, fill=FILLC); sv.dots(u0, -FILL + 0.03, strip0, -0.015, step=6)
    k = u0 + 0.06
    while k < strip0 - 0.04:
        sv.circle(k, -FILL + 0.03 + 0.012, 0.008, fill=(0.95, 0.60, 0.55), stroke=RED, lw=0.6); k += 0.15
    sv.rect(strip0, -FILL, LIN_X, -0.015, fill=FILLC); sv.dots(strip0, -FILL, LIN_X, -0.015, step=6)
    sv.rect(u0, -0.015, LIN_X, 0.0, fill=(0.86, 0.72, 0.52), stroke=WOOD_S, lw=0.5)
    sv.line(u0, 0.0, LIN_X, 0.0, color=DARK, lw=1.0)
    sv.line(strip0, -FILL, strip0, -0.015, color=RED, lw=0.5, dash=[3, 2])
    # ο ενιαίος τοίχος Τ6Β: 2 γυψοσανίδες + κανάλι 5 cm (στρωτήρας πάνω στην πλάκα) · κενό 2,5 · σκελετός 10 cm με πετροβάμβακα · 2 πυράντοχες
    sv.rect(LIN_X + 0.025, -FILL, WU_S[0], zt, fill=WHITE)
    sv.rect(LIN_X, -FILL, LIN_X + 0.025, zt, fill=LIN_F, stroke=LIN_S, lw=0.9); sv.line(LIN_X + 0.0125, -FILL, LIN_X + 0.0125, zt, color=LIN_S, lw=0.3)
    sv.rect(LIN_X + 0.025, -FILL, WU_S[0], -FILL + 0.03, stroke=(0.45, 0.50, 0.58), lw=0.9)
    wall_core(sv, -FILL, zt, lw=0.6)
    sv.rect(BF + GAPW, -FILL, WE - BRD, -FILL + 0.03, stroke=(0.45, 0.50, 0.58), lw=0.9)
    sv.fill_r(WU_S[2], u1)
    sv.circle(CX, zc + R_CON, R_CON, fill=ORANGE_F, stroke=ORANGE, lw=1.4)
    sv.text((d91[2] + d91[4]) / 2, -0.265, "ΔΟΚΑΡΙ Δ9.1", size=7, font="Inter-Bold", color=WHITE)
    sv.text((d91[2] + d91[4]) / 2, -0.30, "(του κάτω ορόφου)", size=5.4, color=WHITE)
    sv.text(9.05, -0.225, "ΠΛΑΚΑ", size=8, font="Inter-Bold", color=WHITE)
    sv.text(8.82, 0.20, "ΚΑΘΙΣΤΙΚΟ", size=7, font="Inter-Bold", color=GREY, anchor="l")
    sv.text(9.635, 0.20, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=6, font="Inter-Bold", color=GREY)
    sv.leader((8.94, -FILL + 0.045), (8.82, 0.075), ["ενδοδαπέδια (ενδεικτικά): μόνωση · σωλήνες · κονίαμα · δάπεδο"], anchor="l", size=5.8, color=GREY)
    sv.leader((CX, zc + 2 * R_CON), (9.24, 0.135), ["συμπυκνώματα Ø 32 (εδώ ροή %s)" % lv(zc, 3)], anchor="r", size=6.0, color=ORANGE)
    sv.leader((LIN_X + 0.05, 0.215), (9.30, 0.285), ["προς το σπίτι: 2 γυψοσανίδες + ΚΑΝΑΛΙ %s cm" % cm(LIN_CAV)], anchor="r", size=6.0, color=LIN_S)
    sv.leader(((BF + GAPW + WE - BRD) / 2, 0.215), (9.50, 0.285), ["σκελετός 10 cm με πετροβάμβακα", "+ 2 πυράντοχες γυψοσανίδες"], anchor="l", size=6.0, color=(0.25, 0.45, 0.35))
    sv.dim_h(zb, [strip0, LIN_X], dy=-12, above=False, fmt=lambda v_: "λωρίδα %s cm χωρίς ενδοδαπέδια" % cm(v_), size=6.2)
    sv.dim_h(zb, [LIN_X, WE], dy=-12, above=False, fmt=lambda v_: "ένας τοίχος %s cm" % cm(v_), size=6.2)
    sv.dim_v(u0 + 0.045, [-FILL, 0.0], left=True, fmt=lambda v_: "γέμισμα %s cm" % cm(v_), size=6.0)
    sv.level(u0 + 0.30, 0.0, right=True, lead=8)
    c.setFont("Inter-Bold", 10); c.setFillColorRGB(*DARK); c.drawString(520, 792, "β · Ο ΣΩΛΗΝΑΣ ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ, ΚΟΛΛΗΤΑ ΣΤΟΝ ΤΟΙΧΟ ΤΗΣ ΠΟΡΤΑΣ – τομή 1:5")
    c.setFont("Inter", 7); c.setFillColorRGB(*GREY)
    c.drawString(520, 781.5, "εγκάρσια στον τοίχο της πόρτας, κοιτάμε προς βορρά · ίδια λωρίδα 20 cm και στον ανατολικό τοίχο του Υπν.2 για τα ψυκτικά")
    # ---------------- δεξιά στήλη
    x, w = 520, 640
    y = head(c, x, 356, "Ο ΤΟΙΧΟΣ ΤΗΣ ΠΟΡΤΑΣ – ΤΙ ΑΛΛΑΖΕΙ")
    y = bullets(c, x, y, w, [
        "Ο τοίχος της πόρτας εισόδου χτίζεται ΕΝΑΣ τοίχος %s cm με διπλό σκελετό – δεν είναι τοίχος και πρόσθετη επένδυση, ενδιάμεσα φύλλα δεν μπαίνουν. "
        "Προς το κλιμακοστάσιο: 2 πυράντοχες γυψοσανίδες και σκελετός 10 cm με πετροβάμβακα. Προς το σπίτι: σκελετός 5 cm (το κανάλι) και 2 γυψοσανίδες – πυράντοχες κι αυτές, όπως ο τοίχος των 15 cm που αντικαθιστά." % cm(WE - LIN_X),
        "Ίδιο πάχος και στις δύο πλευρές της πόρτας (για να κάτσει σωστά η κάσα) και πάνω από την πόρτα. Δεν υπάρχει κουτί ούτε δόντι.",
        "Το κανάλι πηγαίνει από την πλάκα του δαπέδου ως την πλάκα της οροφής, δίπλα στο δοκάρι Δ9.1 (όχι κάτω του), και είναι ανοιχτό μέσα στο κενό της "
        "ψευδοροφής – εκεί μπαίνουν οι σωλήνες. Αφού περάσουν, το άνοιγμα σφραγίζεται με πετροβάμβακα γύρω τους (είναι τοίχος προς το κλιμακοστάσιο – να το "
        "επιβεβαιώσει ο μελετητής πυροπροστασίας).",
        "Η κάσα της πόρτας ασφαλείας στην πλευρά του κλιμακοστασίου (ορθοστάτες του σκελετού των 10 cm)· προς το σπίτι γίνεται λαμπάς %s cm (να το ξέρει ο "
        "προμηθευτής της πόρτας)." % cm(BF - LIN_X)], size=7.0)
    y = head(c, x, y - 6, "ΔΑΠΕΔΟ – ΤΙ ΠΡΟΣΕΧΟΥΜΕ")
    y = bullets(c, x, y, w, [
        "Οι σωλήνες στρώνονται πάνω στην πλάκα ΠΡΙΝ από το γέμισμα και πριν από τα ενδοδαπέδια, κολλητά στον τοίχο. Στη λωρίδα των 20 cm δεν μπαίνει "
        "σωλήνας ενδοδαπέδιας· μπροστά στο άνοιγμα της κουζίνας οι σωλήνες της ενδοδαπέδιας περνούν ΚΑΤΩ από τον Ø 32 (εκεί είναι 3,5 – 4,5 cm πάνω από την πλάκα).",
        "Συμπυκνώματα: ξεκινούν με τη ράχη %s cm κάτω από το τελικό δάπεδο και κατεβαίνουν 1 cm ανά μέτρο· στο σιφώνι η ροή είναι %s cm πάνω από την πλάκα."
        % (cm(COVER), cm(FILL + Z_C_END)),
        "Στη βάση του τοίχου κόβεται τοπικά η γυψοσανίδα (μέσα στο ύψος του γεμίσματος) για να βγουν οι σωλήνες από το κανάλι στο δάπεδο.",
        "Φωτογραφία και δοκιμές (άζωτο στα ψυκτικά, νερό στα συμπυκνώματα) πριν σκεπαστούν."], size=7.0)
    # υπόμνημα σε δύο στήλες (για να μένει πάνω από την πινακίδα)
    yl = legend(c, x, y - 6, [("box", (MAG_F, MAG), "ψυκτικός σωλήνας με τη μόνωσή του (μέσα ο χαλκός)"), ("box", (ORANGE_F, ORANGE), "συμπυκνώματα PVC Ø 32"),
                              ("hatch", (CONC, DARK), "σκυρόδεμα"), ("box", (FILLC, FILL_H), "γέμισμα δαπέδου")], w=300, size=6.0)
    yr = legend(c, x + 320, y - 6, [("box", (LIN_F, LIN_S), "τοίχος πόρτας: 2 πυράντοχες γυψοσανίδες προς το σπίτι"),
                                    ("box", (FIRE_F, FIRE_S), "τοίχος πόρτας: 2 πυράντοχες προς το κλιμακοστάσιο"),
                                    ("box", (ROCK, ROCK_H), "τοίχος πόρτας: σκελετός 10 cm με πετροβάμβακα")], w=300, size=6.0, title="")
    assert min(yl, yr) > 96, "ΚΜ-06: το υπόμνημα πέφτει πάνω στην πινακίδα (%.0f)" % min(yl, yr)
    frame(c, "ΚΜ-06", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΛΕΠΤΟΜΕΡΕΙΕΣ", "Ο τοίχος της πόρτας – ένας τοίχος 22,5 cm (κάτοψη) · ο σωλήνας μέσα στο γέμισμα (τομή)", "Κλίμακα 1:5 · A3")


# ================================================================ ΚΜ-07 ισόγειο – κάτοψη διαδρομής
GF_LIV = [z_["level"] for z_ in G.ZONES if z_["id"] == "Ζ1"][0]      # οροφή καθιστικού ισογείου (+2,89)


def sheet_gf(c):
    s = scale(40)
    clip = (3.95, -0.05, 11.95, 9.62)
    ox = 34 - clip[0] * s
    oy = PAGE_H - 815 - clip[1] * s
    v = plan_bg(c, G, ox, oy, s, clip)
    beams_plan(v, G, ("Δ3.1", "Δ9.1", "Δ4.4", "Δ9.5", "Δ1.4"),
               {"Δ3.1": (5.60, 5.00, 0), "Δ9.1": (9.55, 7.80, 90), "Δ4.4": (6.60, 9.30, 0), "Δ9.5": (9.55, 2.62, 90), "Δ1.4": (7.90, 0.65, 0)})
    ac_unit_plan(v, G)
    em = G.OUTDOOR_T
    c.setDash([3, 1.5]); v.rect(*em, fill=(0.93, 0.95, 0.99), stroke=BLUE, lw=0.8); c.setDash([])
    vpipe(v, G.SPLIT_ROUTE, BLUE2, 1.1, dash=[4, 2], halo=False)
    vpipe(v, G.COND_ROUTE, ORANGE, 1.9)
    vpipe(v, G.KM1_VOID, MAG, 2.2)
    vpipe(v, G.KM1_FLOOR, MAG, 2.4, dash=[1.4, 1.9])
    u = G.UNITS[0]["rect"]
    v.text((u[0] + u[2]) / 2, (u[1] + u[3]) / 2 + 0.25, "ΚΜ1", size=8, font="Inter-Bold", color=BLUE, bg=True)
    v.text(4.60, 7.20, "ΚΑΘΙΣΤΙΚΟ", size=9, font="Inter-Bold", color=GREY)
    v.text(8.30, 7.60, "ΚΟΥΖΙΝΑ", size=8, font="Inter-Bold", color=GREY)
    v.text(8.30, 7.80, "χαμηλή οροφή %s" % G.fmt(2.65), size=5.6, color=GREY)
    v.text(7.85, 2.40, "ΥΠΝΟΔΩΜΑΤΙΟ 2", size=9, font="Inter-Bold", color=GREY)
    v.text(8.70, 5.20, "WC", size=7.5, font="Inter-Bold", color=GREY)
    v.text(10.62, 2.25, "ΒΑ ΒΕΡΑΝΤΑ", size=7.5, font="Inter-Bold", color=GREY)
    v.text((em[0] + em[2]) / 2, (em[1] + em[3]) / 2, "εξωτ. μονάδα", size=5.4, color=BLUE, font="Inter-SemiBold")
    v.text((em[0] + em[2]) / 2, em[3] + 0.12, "(θέση ενδεικτική)", size=4.8, color=BLUE, bg=True)
    v.text(10.75, 6.55, "ΧΩΛ ΚΤΙΡΙΟΥ", size=7.5, font="Inter-Bold", color=GREY)
    x1d, y1d = G.KM1_VOID[-1]
    vlabel(v, 10.00, 5.62, ["ΚΑΤΕΒΑΣΜΑ ΜΕΣΑ ΣΤΟΝ ΓΥΨΟΤΟΙΧΟ", "του WC (Τ2-06) – όχι κάτω από δοκάρι"], color=MAG, to=(x1d + 0.04, y1d), size=6.0)
    vlabel(v, 8.45, 3.40, ["ΜΕΣΑ ΣΤΟ ΔΑΠΕΔΟ (γέμισμα)", "λωρίδα 25 cm στον τοίχο,", "χωρίς ενδοδαπέδια"], anchor="r", color=MAG, to=(9.27, 3.30), size=6.0)
    vlabel(v, 7.05, 5.82, ["συμπυκνώματα ΚΜ1 →", "μέσα στον Τ2-06 → σιφώνι WC"], anchor="r", color=ORANGE, to=(8.02, 5.60), size=5.6)
    vlabel(v, 6.35, 4.62, ["ψυκτικά split: ψευδοροφή →", "κατέβασμα μέσα στη ντουλάπα"], anchor="r", color=BLUE2, to=(7.20, 4.20), size=5.6)
    vlabel(v, 5.95, 7.62, ["Ο ΑΕΡΑΣ ΒΓΑΙΝΕΙ ΟΡΙΖΟΝΤΙΑ, ΜΠΡΟΣΤΑ", "από τα slot στη ΜΕΤΩΠΗ της χαμηλής οροφής"], anchor="r", color=BLUE, to=(G.DIFFUSERS[1]["rect"][0] - 0.50, 7.5125), size=6.0)
    vbadge(v, (u[0] + u[2]) / 2, u[3] - 0.22, 1)
    vbadge(v, 7.615, 5.55, 2, dy=12)
    vbadge(v, x1d, y1d, 3, dx=-2, dy=-13)
    vbadge(v, 7.75, 5.32, 4, dx=13)
    vbadge(v, 8.55, 4.55, 5, dy=-11)
    vbadge(v, 9.30, 2.30, 5, dx=12)
    vbadge(v, 9.575, 1.20, 6, dy=-12)
    vbadge(v, 10.05, 1.75, 7)
    c.restoreState()
    X0, Y0 = v.p(clip[0], clip[3]); X1, Y1 = v.p(clip[2], clip[1])
    c.setStrokeColorRGB(*LIGHT); c.setLineWidth(0.6); c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1, fill=0)
    x, w = X1 + 24, 1160 - (X1 + 24)
    big_title(c, x, 800, "ΙΣΟΓΕΙΟ – ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ ΚΜ1", "Ίδια αρχή με τους ορόφους: τίποτα κάτω από δοκάρι")
    y = 764
    gsteps = [
        ("ΤΟ ΜΗΧΑΝΗΜΑ ΜΕΝΕΙ ΠΑΝΩ ΑΠΟ ΤΗΝ ΚΟΥΖΙΝΑ", "ΚΜ1 στη χαμηλή οροφή της κουζίνας (%s), όπως ήταν. Συνδέσεις στο βόρειο άκρο, ανατολικό πλάι. Ο αέρας βγαίνει "
         "ΟΡΙΖΟΝΤΙΑ από τα slot στη ΜΕΤΩΠΗ της χαμηλής οροφής (το κατακόρυφο σκαλοπάτι %s → %s, %s cm), προς το καθιστικό."
         % (G.fmt(2.65), G.fmt(2.65), G.fmt(GF_LIV), cm(GF_LIV - 2.65))),
        ("0,6 m ΜΕΣΑ ΣΤΗΝ ΨΕΥΔΟΡΟΦΗ", "Τα ψυκτικά πάνε ως τον τοίχο του WC. Εκεί δεν υπάρχει δοκάρι."),
        ("ΚΑΤΕΒΑΣΜΑ ΜΕΣΑ ΣΤΟΝ ΓΥΨΟΤΟΙΧΟ ΤΟΥ WC", "Κατεβαίνουν μέσα στον τοίχο Τ2-06 (WC / κουζίνα) ως το δάπεδο – δεν χρειάζεται κουτί."),
        ("ΔΑΠΕΔΟ ΤΟΥ WC, ΚΑΤΩ ΑΠΟ ΤΟΝ ΤΟΙΧΟ", "Μέσα στο γέμισμα, δίπλα στην πόρτα του WC, και κάτω από τη βάση του τοίχου προς το Υπν.2 (το δοκάρι Δ3.1 είναι ψηλά)."),
        ("ΚΑΤΩ ΑΠΟ ΤΗ ΝΤΟΥΛΑΠΑ ΚΑΙ ΚΟΛΛΗΤΑ ΣΤΟΝ ΤΟΙΧΟ", "Κάτω από τη ντουλάπα του Υπν.2 και μετά κατά μήκος του ανατολικού τοίχου του (λωρίδα 25 cm χωρίς ενδοδαπέδια). "
         "Εκεί έρχονται και τα ψυκτικά των split, που κατεβαίνουν μέσα στη ντουλάπα."),
        ("ΠΕΣΣΟΣ ΔΙΠΛΑ ΣΤΗ ΜΠΑΛΚΟΝΟΠΟΡΤΑ – ΕΞΟΔΟΣ ΧΑΜΗΛΑ", "Αυλάκι στο τούβλο ως +0,25 και έξω."),
        ("ΒΑ ΒΕΡΑΝΤΑ", "Εξωτερική μονάδα. Τα συμπυκνώματα της ΚΜ1 στο ισόγειο πάνε στο σιφώνι του WC (όπως ήταν)."),
    ]
    y = head(c, x, y, "Η ΔΙΑΔΡΟΜΗ ΒΗΜΑ – ΒΗΜΑ")
    for i, (t, d) in enumerate(gsteps if SHOW_NOTES else [], 1):
        badge(c, x + 7, y + 2.5, i, 7.0)
        c.setFont("Inter-Bold", 7.2); c.setFillColorRGB(*DARK); c.drawString(x + 20, y, t)
        y -= 10.2
        y = para(c, x + 20, y, w - 22, d, size=6.8) - 3.5
    y = head(c, x, y - 6, "ΤΙ ΑΛΛΑΞΕ ΣΤΟ ΙΣΟΓΕΙΟ", 9.5)
    y = para(c, x, y, w, "Η διαδρομή των ψυκτικών: πριν περνούσαν κάτω από το δοκάρι Δ3.1 μέσα από τη ντουλάπα του καθιστικού. Και τα slot: από την οροφή της "
             "χαμήλωσης πήγαν στη ΜΕΤΩΠΗ της (στο %s…%s), για να φυσάνε μπροστά και όχι προς τα κάτω. Το μηχάνημα, οι οροφές και τα συμπυκνώματα έμειναν όπως ήταν."
             % (G.fmt(G.SLOT_Z[0]), G.fmt(G.SLOT_Z[1])), size=7.0)
    legend(c, x, y - 10, [("line", MAG, "ψυκτικά ΚΜ1 μέσα στην ΨΕΥΔΟΡΟΦΗ"), ("dash", MAG, "ψυκτικά μέσα στο ΔΑΠΕΔΟ (γέμισμα)"),
                          ("line", ORANGE, "συμπυκνώματα ΚΜ1 Ø 32 (ψευδοροφή → τοίχος → σιφώνι WC)"), ("ddash", BLUE2, "ψυκτικά split (ψευδοροφή)"),
                          ("hatch", ((0.86, 0.75, 0.68), BEAMC), "δοκάρια (δεν περνάμε από κάτω τους)")], w=w)
    north_arrow(c, X1 - 20, Y1 - 24, 9)
    frame(c, "ΚΜ-07", "ΚΛΙΜΑΤΙΣΤΙΚΟ ΣΑΛΟΝΙΟΥ – ΙΣΟΓΕΙΟ", "Κάτοψη διαδρομής · γυψότοιχος WC → δάπεδο → ΒΑ βεράντα", "Κλίμακα 1:40 · A3",
          floor="ΙΣΟΓΕΙΟ – ΙΣ1")


SHEETS = [sheet_plan, sheet_aa, sheet_bb, sheet_gg, sheet_dd, sheet_det, sheet_gf]


def build(out):
    for m in (A, G):                                 # οι τομές βγαίνουν μόνο από μοντέλα χωρίς αποκλίσεις
        sheets.bind(m)
        bad = [r for r in checks.run() if r[5] == "ΑΠΟΚΛΙΣΗ"]
        assert not bad, bad
    c = new_canvas(out, "Κλιματιστικό σαλονιού ΚΜ1 – τομές – Κωνσταντινουπόλεως 12")
    c.setPageCompression(1)
    for fn in SHEETS:
        fn(c); c.showPage()
    c.save()
    print("OK", os.path.abspath(out), "· φύλλα", len(SHEETS))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTDIR, "ΚΛΙΜΑΤΙΣΤΙΚΟ_ΣΑΛΟΝΙΟΥ_ΚΜ1_ΤΟΜΕΣ_%s.pdf" % REV))
