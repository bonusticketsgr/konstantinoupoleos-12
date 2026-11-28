"""Φωτισμός καθιστικού – τραπεζαρίας – κουζίνας τυπικού ορόφου (Β1) ΧΩΡΙΣ κρυφούς φωτισμούς – υπολογισμός lumen + διάταξη.
R00 (28/11/2026 – Γιάννης: «θέλω να δούμε τον φωτισμό μια φορά ακόμα στο σαλόνι / κουζίνα / τραπεζαρία· υπολόγισε πόσα lumen θα
χρειαστούν και βγάλε τον απαραίτητο φωτισμό χωρίς κρυφούς» + φωτογραφίες: σειρές χωνευτών spot, ράγα στο τζάμι, κρεμαστά τραπεζαρίας).
R01 (28/11/2026 – Γιάννης: «στην κουζίνα θα μπουν και κάτω από τα ντουλάπια LED · δούλεψε και με διπλά spot αν θεωρείς θα βγει πιο ωραίο ·
αυτά τα lumen στο τραπέζι και κουζίνα φτάνουν · την τραπεζαρία κούνησέ την λίγο να μην είναι κάτω από τη χαμηλή οροφή»): LED4 ξανά κάτω από τα
ντουλάπια (πρόσθετο στα 7 spots της κουζίνας) · ΔΙΠΛΑ spot στα «αντικείμενα»: τοίχος TV (ΔΣ1), μπροστά στο τζάμι της τραπεζαρίας (ΔΣ2), πάνω από
το τραπέζι (ΔΤ) – ο γενικός φωτισμός μένει μονά 60° · τραπεζαρία 0,30 δυτικότερα (6,40–8,20 – ολόκληρη κάτω από την οροφή +2,68, η λωρίδα
+2,48 αρχίζει στο 8,30) – η μετακίνηση πρέπει να περάσει και στο EQUIP των τοιχοποιιών (Β1 / Δ΄) και στο TABLE_C των ανόψεων με το ΟΚ.
ΠΡΟΤΑΣΗ προς έγκριση – ΔΕΝ έχει περάσει στις ανόψεις (b1_anopsi.SPOTS / LED4) ούτε στα ηλεκτρολογικά.
Χρήση: python3 fotismos_b1.py → ΑΝΟΨΕΙΣ/ΦΩΤΙΣΜΟΣ_ΚΑΘΙΣΤΙΚΟ_ΚΟΥΖΙΝΑ_Β1_<REV>.pdf (Φ-01 κάτοψη 1:40 · Φ-02 υπολογισμός / πίνακας φωτιστικών).
Μέθοδος: γενικός φωτισμός με τη μέθοδο των lumen Φ = E·A / (UF·MF) · φωτισμός εργασίας (τραπέζι, πάγκος) με τη ροή μέσα στη δέσμη."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import b1_anopsi as A
import sheets
from sheets import ORANGE, RED, GREY, DARK, zones_fill, plan, ac_outline, level_tag, tall_marks, legend
from draw import View, PAGE_W, PAGE_H, frame_and_title, north_arrow, new_canvas
from reportlab.pdfbase import pdfmetrics

REV, DATE = "R01", "28/11/2026"
W = A.W
sheets.bind(A)
OUTDIR = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΑΝΟΨΕΙΣ")
OUT = os.path.join(OUTDIR, "ΦΩΤΙΣΜΟΣ_ΚΑΘΙΣΤΙΚΟ_ΚΟΥΖΙΝΑ_Β1_%s.pdf" % REV)

# ------------------------------------------------------------------ γεωμετρία (από τα μοντέλα)
WX0, SOUTH, NORTH = 1.705, A.SOUTH, 5.15          # καθιστικό: δυτικός τοίχος · νότιος (Τ3 / Τ3Μ 9,095) · βόρειος (καναπές)
STRIP_X, LIN_X, KY = A.STRIP_X, A.LIN_X, A.KITCH_Y  # λωρίδα ΚΜ1 8,30–9,40 · κουζίνα από 7,70
K_E, BAY_S = 13.76, 10.06                          # ανατολική παρειά κουζίνας (έρκερ Α) · νότια παρειά έρκερ Ν
TABLE_DX = -0.30                                   # R01: τραπεζαρία 0,30 δυτικότερα – έξω από τη λωρίδα +2,48 (8,30)
TABLE = (6.70 + TABLE_DX, 6.80, 8.50 + TABLE_DX, 7.70)   # τραπεζαρία 1,80 × 0,90 (τοιχοποιίες Β1 R31: 6,70–8,50 → R01: 6,40–8,20)
# το υπόβαθρο της κάτοψης διαβάζει τα έπιπλα από το W.EQUIP → τραπέζι + 6 καρέκλες μετατοπισμένα ΜΟΝΟ για αυτό το τεύχος (στο ΟΚ περνά στο μοντέλο)
W.EQUIP = [(e[0], e[1] + TABLE_DX, e[2], e[3] + TABLE_DX, e[4]) + tuple(e[5:]) if (6.2 < e[1] < 9.0 and 6.2 < e[2] < 8.3 and e[0] in ("rect", "chair")) else e
           for e in W.EQUIP]
COUNTER_N = (10.45, KY, 13.76, 8.30)               # βόρειος πάγκος (εστίες 12,15–12,75)
COUNTER_E = (13.16, 8.30, 13.76, 9.15)             # πάγκος έρκερ Α
COUNTER_S = (10.40, 9.46, 12.70, 10.06)            # πάγκος έρκερ Ν (νεροχύτης 11,30–12,10, πλ. πιάτων)
H_LIV, H_AC = 2.68, A.LV_AC                        # στάθμες οροφής (καθιστικό · λωρίδα / κουζίνα)
WP_GEN, WP_TASK = 0.75, 0.90                       # επίπεδο αναφοράς: γενικός 0,75 · πάγκος 0,90 (τραπέζι 0,75)

# ------------------------------------------------------------------ φωτιστικά
# ένα σώμα, δύο οπτικές: Α = 60° (γενικός), Β = 36° (τραπέζι / πάγκος) · Τ = ΔΙΠΛΟ χωνευτό (2 κεφαλές 36° ρυθμιζόμενες, ορθογώνιο)
# 9 W · 850 lm ανά κεφαλή · 2700 K · CRI ≥ 90 · UGR < 19 · dimmable · σώμα ≤ 75 mm
LM, WATT = 850, 9
FIX = {"A": dict(beam=60, f_beam=0.70, heads=1, txt="χωνευτό LED spot, δέσμη 60°, γενικός φωτισμός"),
       "B": dict(beam=36, f_beam=0.65, heads=1, txt="χωνευτό LED spot, δέσμη 36°, φωτισμός εργασίας (πάγκοι)"),
       "T": dict(beam=36, f_beam=0.65, heads=2, txt="ΔΙΠΛΟ χωνευτό spot 2 × 36° ρυθμιζόμενο (τοίχος TV · τζάμι τραπεζαρίας · τραπέζι)")}
TWIN_HALF = 0.11                 # απόσταση κεφαλής από το κέντρο του διπλού (ορθογώνιο ≈ 0,34 × 0,17 εξωτερικά)
RY_N, RY_S = 6.60, 8.40          # σειρές καθιστικού: 0,50 μπροστά από τον καναπέ (6,10) · 0,695 από τον νότιο τοίχο (τζάμι / τοίχος TV)
COLS = (2.40, 3.90, 5.40)        # στήλες της βόρειας σειράς ανά 1,50 (0,695 από τον δυτικό τοίχο)
TV_X = (1.70 + 4.10) / 2         # 2,90: άξονας του επίπλου TV
TY = (TABLE[1] + TABLE[3]) / 2   # άξονας τραπεζιού 7,25
TX = (TABLE[0] + TABLE[2]) / 2   # κέντρο τραπεζιού 7,30
GLASS_X = 6.15                   # διπλό μπροστά στο τζάμι W2.02 (4,10–8,30), στην πλευρά της τραπεζαρίας
KN_Y, KS_Y, KE_X = KY + 0.55, BAY_S - 0.55, K_E - 0.55     # 0,55 από τον τοίχο = πάνω από τη μπροστινή ζώνη του πάγκου, έξω από τα κρεμαστά (0,35)
# (id, τύπος, x, y, κύκλωμα, ζώνη[, άξονας διπλού "H" / "V"])
SPOTS = [
    ("Σ1", "A", COLS[0], RY_N, "σ1", "ΚΑΘ"), ("Σ2", "A", COLS[1], RY_N, "σ1", "ΚΑΘ"), ("Σ3", "A", COLS[2], RY_N, "σ1", "ΚΑΘ"),
    ("ΔΣ1", "T", TV_X, RY_S, "σ2", "ΚΑΘ", "H"), ("ΔΣ2", "T", GLASS_X, RY_S, "σ2", "ΚΑΘ", "H"),
    ("ΔΤ", "T", TX, TY, "τ", "ΚΑΘ", "H"),
    ("Ε1", "A", 8.85, 5.65, "β", "ΚΑΘ"), ("Ε2", "A", 8.85, RY_S, "β", "ΚΑΘ"),
    ("Κ1", "B", 10.95, KN_Y, "ε1", "ΚΟΥΖ"), ("Κ2", "B", 11.85, KN_Y, "ε1", "ΚΟΥΖ"), ("Κ3", "B", 12.75, KN_Y, "ε1", "ΚΟΥΖ"), ("Κ4", "B", KE_X, 8.72, "ε1", "ΚΟΥΖ"),
    ("Κ5", "B", 10.95, KS_Y, "ε2", "ΚΟΥΖ"), ("Κ6", "B", 11.70, KS_Y, "ε2", "ΚΟΥΖ"), ("Κ7", "B", 12.45, KS_Y, "ε2", "ΚΟΥΖ"),
]
def heads(sp):
    """Θέσεις κεφαλών ενός φωτιστικού (το διπλό έχει δύο)."""
    sid, kind, x, y = sp[:4]
    if kind != "T":
        return [(x, y)]
    ax = sp[6] if len(sp) > 6 else "H"
    return [(x - TWIN_HALF, y), (x + TWIN_HALF, y)] if ax == "H" else [(x, y - TWIN_HALF), (x, y + TWIN_HALF)]
N_HEADS = sum(FIX[s[1]]["heads"] for s in SPOTS)
LED4 = [l for l in A.LED if l[0] == "LED4"]        # R01: ταινία LED κάτω από τα επάνω ντουλάπια (ανόψεις Β1 R27) – πρόσθετη στα spots
LED4_LEN = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for _, a, b, _, _ in LED4)
LED4_LMM, LED4_WM = 800, 9.6                        # lm / m και W / m της ταινίας (24 V, 3000 K, CRI ≥ 90, σε προφίλ με κάλυμμα)
CIRCUITS = {"σ1": "καθιστικό – σειρά μπροστά από τον καναπέ, μονά 60° (dimmer)", "σ2": "καθιστικό – διπλά στον τοίχο TV και στο τζάμι (dimmer)",
            "τ": "τραπεζαρία – διπλό πάνω από το τραπέζι (dimmer)", "β": "είσοδος – λωρίδα ΚΜ1", "ε1": "κουζίνα – βόρειος πάγκος + έρκερ Α",
            "ε2": "κουζίνα – πάγκος νεροχύτη (έρκερ Ν)", "ε3": "κουζίνα – LED κάτω από τα ντουλάπια (%s m)" % ("%.1f" % LED4_LEN).replace(".", ",")}
CIRC_AT = {"σ1": (4.65, 6.60), "σ2": (4.50, 8.40), "τ": (TABLE[0] + 0.35, TY), "β": (8.85, 5.15 + 0.22), "ε1": (12.30, 8.25), "ε2": (12.08, 9.51)}
DETECTORS = [d for d in A.DETECTORS if d[0] in ("ΑΚ1", "ΑΘ5")]
NO_GO = [("καναπές", W.SOFA), ("καναπές (γύρισμα)", W.SOFA_RET), ("ΚΜ1", A.UNITS[0]["rect"]), ("plenum ΚΜ1", A.DUCTS[0][1]),
         ("επιστροφή Ε1", A.DIFFUSERS[2]["rect"]), ("θυρίδα ΘΕ1", A.HATCHES[0]["rect"])] + [(n, r) for n, r in A.TALL]

# ------------------------------------------------------------------ υπολογισμός
def rect_area(r):
    return (r[2] - r[0]) * (r[3] - r[1])

ZONES = [   # (κωδ., όνομα, εμβαδόν, μήκος, πλάτος, ύψος οροφής, επίπεδο, στόχος lx, UF, κυκλώματα που μετρούν)
    dict(id="ΚΑΘ", name="Καθιστικό – τραπεζαρία – είσοδος (ενιαίος χώρος, Ζ1 + Ζ2)", L=LIN_X - WX0, Wd=SOUTH - NORTH,
         A=(LIN_X - WX0) * (SOUTH - NORTH), h=H_LIV, wp=WP_GEN, E=150, UF=0.60, circ=("σ1", "σ2", "τ", "β")),
    dict(id="ΚΟΥΖ", name="Κουζίνα (Ζ3, με τα έρκερ)", L=K_E - LIN_X, Wd=None,
         A=(K_E - LIN_X) * (9.15 - KY) + (12.70 - 9.70) * (BAY_S - 9.15), h=H_AC, wp=WP_GEN, E=200, UF=0.50, circ=("ε1", "ε2")),
]
MF = 0.80
for z in ZONES:
    if z["Wd"] is None:
        z["Wd"] = z["A"] / z["L"]
    hm = z["h"] - z["wp"]
    z["k"] = z["L"] * z["Wd"] / (hm * (z["L"] + z["Wd"]))
    z["need"] = z["E"] * z["A"] / (z["UF"] * MF)
    z["n"] = sum(FIX[s[1]]["heads"] for s in SPOTS if s[4] in z["circ"])
    z["inst"] = z["n"] * LM
    z["Eavg"] = z["inst"] * z["UF"] * MF / z["A"]

def task(rect, h_ceiling, plane, n, capture):
    """Μέση ένταση πάνω σε επιφάνεια εργασίας από n spots 36° ακριβώς από πάνω: ροή μέσα στη δέσμη × ποσοστό που πέφτει στην επιφάνεια / εμβαδόν."""
    hm = h_ceiling - plane
    r = hm * math.tan(math.radians(FIX["B"]["beam"] / 2))
    pool = math.pi * r * r
    return dict(hm=hm, r=r, pool=pool, n=n, Eres=n * LM * FIX["B"]["f_beam"] * capture / rect_area(rect), Ec=LM * FIX["B"]["f_beam"] / pool)

def _n(*ids):
    return sum(FIX[s[1]]["heads"] for s in SPOTS if s[0] in ids)
TASKS = [
    dict(name="Τραπεζαρία 1,80 × 0,90 (ΔΤ – 2 κεφαλές στραμμένες στα άκρα)", rect=TABLE, E=300, **task(TABLE, H_LIV, 0.75, _n("ΔΤ"), 0.85)),
    dict(name="Βόρειος πάγκος κουζίνας 3,31 × 0,60 (Κ1 – Κ3)", rect=COUNTER_N, E=500, **task(COUNTER_N, H_AC, WP_TASK, _n("Κ1", "Κ2", "Κ3"), 0.70)),
    dict(name="Πάγκος έρκερ Α 0,60 × 0,85 (Κ4)", rect=COUNTER_E, E=500, **task(COUNTER_E, H_AC, WP_TASK, _n("Κ4"), 0.60)),
    dict(name="Πάγκος νεροχύτη 2,30 × 0,60 (Κ5 – Κ7)", rect=COUNTER_S, E=500, **task(COUNTER_S, H_AC, WP_TASK, _n("Κ5", "Κ6", "Κ7"), 0.70)),
]

# ------------------------------------------------------------------ έλεγχοι
def in_rect(x, y, r, m=0.0):
    return r[0] - m <= x <= r[2] + m and r[1] - m <= y <= r[3] + m

def checks_all():
    rows = []
    def ok(code, txt, good, val=""):
        rows.append((code, txt, "OK" if good else "ΛΑΘΟΣ", val))
    zone_rects = {"ΚΑΘ": [(WX0, NORTH, LIN_X, SOUTH)], "ΚΟΥΖ": [(LIN_X, KY, K_E, 9.15), (9.70, 9.15, 12.70, BAY_S)]}
    for sp in SPOTS:
        sid, kind, x, y, circ, zone = sp[:6]
        hs = heads(sp)
        ok("ΖΩΝ-%s" % sid, "μέσα στη ζώνη οροφής του", all(any(in_rect(hx, hy, r) for r in zone_rects[zone]) for hx, hy in hs))
        hit = [n for n, r in NO_GO for hx, hy in hs if in_rect(hx, hy, r, A.SPOT_R)]
        ok("ΕΜΠ-%s" % sid, "όχι πάνω σε καναπέ / ντουλάπι έως οροφή / μονάδα ΚΜ1 / plenum / θυρίδα", not hit, ", ".join(hit))
        for bid, sec, x0, y0, x1, y1 in A.BEAMS:
            if in_rect(x, y, (x0, y0, x1, y1), A.SPOT_R):
                lvl = H_LIV if zone == "ΚΑΘ" and x < STRIP_X else H_AC
                ok("ΔΟΚ-%s" % sid, "κάτω από τη δοκό %s: χωρά το σώμα" % bid, A.beam_soffit(sec) - lvl >= A.SPOT_BODY + 0.01)
        for did, dk, dx, dy, room in DETECTORS:
            d_ = math.hypot(x - dx, y - dy)
            ok("ΑΝΙΧ-%s-%s" % (sid, did), "≥ 0,50 από τον ανιχνευτή %s" % did, d_ >= 0.50, "%.2f" % d_)
    pts = [(s[2], s[3]) for s in SPOTS]      # κέντρα φωτιστικών (το διπλό μετρά ως ένα)
    dmin = min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
    ok("ΤΡΑΠ", "τραπέζι ολόκληρο κάτω από την οροφή +2,68 (δυτικά της λωρίδας %s)" % fm(STRIP_X), TABLE[2] <= STRIP_X - 0.05, "ανατ. άκρο %s" % fm(TABLE[2]))
    ok("ΤΡΑΠ-ΚΑΝ", "καρέκλες τραπεζαρίας ≥ 0,90 από το γύρισμα του καναπέ", TABLE[0] - 0.45 - W.SOFA_RET[2] >= 0.90, fm(TABLE[0] - 0.45 - W.SOFA_RET[2]))
    ok("ΑΠΟΣΤ", "ελάχιστη απόσταση μεταξύ spots ≥ 0,60", dmin >= 0.60, "%.2f" % dmin)
    void = A.TOP_SLAB - 0.20 - H_LIV
    ok("ΚΕΝΟ-ΚΑΘ", "σώμα spot ≤ 75 mm χωρά στο κενό του καθιστικού (10 cm)", void >= A.SPOT_BODY + 0.02, "%.2f" % void)
    for z in ZONES:
        ok("LM-%s" % z["id"], "εγκατεστημένα lumen ≥ 95 %% των απαιτούμενων (%d lx)" % z["E"], z["inst"] >= 0.95 * z["need"], "%.0f / %.0f lm" % (z["inst"], z["need"]))
    for t in TASKS:
        ok("ΕΡΓ", "%s ≥ %d lx" % (t["name"], t["E"]), t["Eres"] >= t["E"], "%.0f lx" % t["Eres"])
    ok("LED4", "LED4 κάτω από όλα τα επάνω ντουλάπια (3 τμήματα των ανόψεων)", len(LED4) == 3, "%.1f m" % LED4_LEN)
    return rows

# ------------------------------------------------------------------ σχεδίαση
S40 = 72 / 25.4 * 1000 / 40
X0M, X1M, Y0M, Y1M = 1.20, 14.25, 4.70, 10.30     # περιοχή κάτοψης (m)
PX0 = 36.0
OX = PX0 - X0M * S40
OY = 118.0 - Y0M * S40

def fm(v, d=2):
    return ("%.*f" % (d, v)).replace(".", ",")

def spot_sym(v, kind, x, y, ax="H"):
    r = 0.06
    if kind == "T":
        hw, hh = (TWIN_HALF + 0.06, 0.085) if ax == "H" else (0.085, TWIN_HALF + 0.06)
        X0, Y0 = v.p(x - hw, y + hh); X1, Y1 = v.p(x + hw, y - hh)
        v.c.setFillColorRGB(1, 1, 1); v.c.setStrokeColorRGB(*ORANGE); v.c.setLineWidth(0.8)
        v.c.roundRect(X0, Y0, X1 - X0, Y1 - Y0, 2.2, stroke=1, fill=1)
        for hx, hy in ((x - TWIN_HALF, y), (x + TWIN_HALF, y)) if ax == "H" else ((x, y - TWIN_HALF), (x, y + TWIN_HALF)):
            v.circle(hx, hy, 0.05, stroke=ORANGE, lw=0.6); v.circle(hx, hy, 0.028, stroke=ORANGE, lw=0.5); v.circle(hx, hy, 0.012, fill=ORANGE)
        return
    v.circle(x, y, r, fill=(1, 1, 1), stroke=ORANGE, lw=0.8)
    if kind == "A":
        v.circle(x, y, 0.02, fill=ORANGE)
    else:
        v.circle(x, y, 0.035, stroke=ORANGE, lw=0.6); v.circle(x, y, 0.014, fill=ORANGE)

def badge(c, X, Y, txt):
    w = max(9.0, pdfmetrics.stringWidth(txt, "Inter-SemiBold", 5.4) + 4)
    c.setFillColorRGB(*ORANGE); c.roundRect(X - w / 2, Y - 4, w, 8, 1.6, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1); c.setFont("Inter-SemiBold", 5.4); c.drawCentredString(X, Y - 2, txt)

def sheet_f01(c):
    v = View(c, OX, OY, S40)
    c.saveState()
    p = c.beginPath(); p.rect(PX0 - 10, PAGE_H - 118 - (Y1M - Y0M) * S40, (X1M - X0M) * S40 + 20, (Y1M - Y0M) * S40 + 4); c.clipPath(p, stroke=0, fill=0)
    zones_fill(v, colored=True)
    plan(v)
    tall_marks(v)
    ac_outline(v)
    # πάγκοι / τραπέζι / καναπές: λεπτή σήμανση (ήδη στο υπόβαθρο) – επιφάνειες υπολογισμού με διακεκομμένο
    c.setDash([2.2, 1.4])
    for r in (TABLE, COUNTER_N, COUNTER_E, COUNTER_S):
        v.rect(*r, stroke=(0.35, 0.58, 0.40), lw=0.55)
    c.setDash([])
    # στόμια / θυρίδα ΚΜ1 για συντονισμό
    for d in A.DIFFUSERS:
        v.rect(*d["rect"], stroke=(0.55, 0.65, 0.80), lw=0.45, **({"fill": (0.55, 0.65, 0.80)} if d["kind"] == "front" else {}))
    c.setDash([2, 1.2]); v.rect(*A.HATCHES[0]["rect"], stroke=GREY, lw=0.4); c.setDash([])
    v.rect(*A.UNITS[0]["rect"], stroke=(0.55, 0.65, 0.80), lw=0.5)
    v.text(8.95, 7.15, "ΚΜ1", size=4.2, color=(0.45, 0.55, 0.70), rot=90)
    # στάθμες
    level_tag(v, 3.30, 7.75, H_LIV, size=6.0, sub="Ζ1 καθιστικό")
    level_tag(v, 8.85, 9.00 - 0.20, H_AC, size=5.2)
    level_tag(v, 11.30, 8.86, H_AC, size=5.2, sub="Ζ3 κουζίνα")
    # ανιχνευτές (συντονισμός)
    for did, kind, x, y, room in DETECTORS:
        c.setDash([1.5, 1.5]); v.circle(x, y, 0.50, stroke=(0.90, 0.55, 0.55), lw=0.4); c.setDash([])
        v.rect(x - 0.07, y - 0.07, x + 0.07, y + 0.07, fill=(1, 1, 1), stroke=RED, lw=0.8)
        if kind == "smoke":
            v.line(x - 0.07, y - 0.07, x + 0.07, y + 0.07, color=RED, lw=0.6); v.line(x - 0.07, y + 0.07, x + 0.07, y - 0.07, color=RED, lw=0.6)
        else:
            v.circle(x, y, 0.025, fill=RED)
        v.text(x + 0.12, y - 0.14, did, size=4.4, color=RED, font="Inter-SemiBold", anchor="l", bg=True)
    # διαστάσεις θέσης (από παρειές τοίχων)
    DC = (0.25, 0.25, 0.30)
    v.dim_chain("H", NORTH - 0.22, [WX0] + list(COLS) + [8.85, LIN_X], size=4.6, side=-1, color=DC)
    v.dim_chain("H", SOUTH + 0.26, [WX0, TV_X, GLASS_X, 8.85, LIN_X], size=4.6, side=+1, color=DC)
    v.dim_chain("H", TY, [TX, STRIP_X, LIN_X], size=4.4, side=+1, color=DC)
    v.dim_chain("V", WX0 - 0.22, [NORTH, RY_N, TY, RY_S, SOUTH], size=4.6, side=-1, color=DC)
    v.dim_chain("H", KY - 0.22, [LIN_X, 10.95, 11.85, 12.75, KE_X, K_E], size=4.4, side=-1, color=DC)
    v.dim_chain("H", BAY_S + 0.22, [9.70, 10.95, 11.70, 12.45, 12.70], size=4.4, side=+1, color=DC)
    v.dim_chain("V", K_E + 0.30, [KY, KN_Y, 8.72, 9.15], size=4.4, side=+1, color=DC)
    v.dim_chain("V", 12.70 + 0.22, [9.15, KS_Y, BAY_S], size=4.4, side=+1, color=DC)
    # spots
    for lid, a_, b_, circ, txt in LED4:
        v.line(*a_, *b_, color=ORANGE, lw=1.6, dash=[4, 2])
    v.text(12.10, 7.86, "LED4 κάτω από τα ντουλάπια", size=3.9, color=ORANGE, bg=True)
    for sp in SPOTS:
        sid, kind, x, y = sp[:4]
        spot_sym(v, kind, x, y, sp[6] if len(sp) > 6 else "H")
        dx = TWIN_HALF + 0.11 if kind == "T" else 0.09
        v.text(x + dx, y - 0.12, sid, size=4.2, color=ORANGE, font="Inter-SemiBold", anchor="l", bg=True)
    for circ, (x, y) in CIRC_AT.items():
        X, Y = v.p(x, y); badge(c, X, Y, circ)
    # ονόματα χώρων
    for txt, x, y in (("ΚΑΘΙΣΤΙΚΟ", 3.30, 7.42), ("ΤΡΑΠΕΖΑΡΙΑ", 7.60, 7.95), ("ΚΟΥΖΙΝΑ", 11.30, 8.70), ("ΕΙΣΟΔΟΣ", 8.85, 6.00)):
        v.text(x, y, txt, size=4.6, color=GREY, font="Inter-Medium", bg=True)
    c.restoreState()
    # υπόμνημα
    items = [
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 3.2), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 1.1, fill=1)),
         "τύπος Α: %s · %d W / %d lm · 2700 K · CRI ≥ 90 · UGR < 19 · dimmable · οπή Ø 75 · σώμα ≤ 75 mm" % (FIX["A"]["txt"], WATT, LM)),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.circle(x, y, 3.2), c_.circle(x, y, 1.9), c_.setFillColorRGB(*ORANGE), c_.circle(x, y, 0.8, fill=1)),
         "τύπος Β: %s · ίδιο σώμα, %d W / %d lm" % (FIX["B"]["txt"], WATT, LM)),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.roundRect(x - 8.5, y - 3.6, 17, 7.2, 1.6), c_.circle(x - 3.6, y, 2.2), c_.circle(x + 3.6, y, 2.2),
                           c_.setFillColorRGB(*ORANGE), c_.circle(x - 3.6, y, 0.8, fill=1), c_.circle(x + 3.6, y, 0.8, fill=1)),
         "τύπος Τ: %s · 2 × %d W / 2 × %d lm" % (FIX["T"]["txt"], WATT, LM)),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*ORANGE), c_.setLineWidth(1.6), c_.setDash([4, 2]), c_.line(x - 6, y, x + 6, y), c_.setDash([]), c_.setLineWidth(0.5)),
         "LED4 ταινία κάτω από τα επάνω ντουλάπια της κουζίνας (%s m · 24 V · 3000 K · CRI ≥ 90 · προφίλ με κάλυμμα) – κύκλωμα ε3" % ("%.1f" % LED4_LEN).replace(".", ",")),
        (lambda c_, x, y: badge(c_, x, y, "σ1"), "κύκλωμα φωτισμού · σ1 / σ2 / τ με dimmer · β είσοδος · ε1 / ε2 / ε3 κουζίνα"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(0.35, 0.58, 0.40), c_.setDash([2.2, 1.4]), c_.rect(x - 5, y - 3, 10, 6), c_.setDash([])),
         "επιφάνεια εργασίας του υπολογισμού (τραπέζι 0,75 · πάγκοι 0,90)"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(*RED), c_.rect(x - 3, y - 3, 6, 6), c_.line(x - 3, y - 3, x + 3, y + 3), c_.line(x - 3, y + 3, x + 3, y - 3)),
         "ΑΚ1 ανιχνευτής καπνού · ΑΘ5 θερμοδιαφορικός (ανόψεις) – ακτίνα 0,50 ελεύθερη"),
        (lambda c_, x, y: (c_.setStrokeColorRGB(0.55, 0.65, 0.80), c_.rect(x - 5, y - 2, 10, 4)), "ΚΜ1 καναλάτη · plenum · slot μετώπης Π1 / Π2 · επιστροφή Ε1 · θυρίδα ΘΕ1 (ανόψεις Β1 %s)" % A.REV),
        (lambda c_, x, y: (c_.setFillColorRGB(*sheets.LEVEL_FILL[H_LIV]), c_.rect(x - 5, y - 3, 10, 6, stroke=0, fill=1)), "οροφή +2,68 (καθιστικό, κενό 10 cm)"),
        (lambda c_, x, y: (c_.setFillColorRGB(*sheets.LEVEL_FILL[H_AC]), c_.rect(x - 5, y - 3, 10, 6, stroke=0, fill=1)), "οροφή +2,48 (λωρίδα ΚΜ1 · κουζίνα, κενό 30 cm)"),
    ]
    legend(c, items, x=985, y=790, w=160, size=5.0)
    north_arrow(c, 1150, 795)
    frame_and_title(c, "Φ-01", "ΦΩΤΙΣΜΟΣ ΚΑΘΙΣΤΙΚΟΥ – ΤΡΑΠΕΖΑΡΙΑΣ – ΚΟΥΖΙΝΑΣ · ΚΑΤΟΨΗ ΟΡΟΦΗΣ",
                    "%d φωτιστικά (%d μονά + %d διπλά = %d κεφαλές) + LED κάτω από τα ντουλάπια · θέσεις από παρειές τοίχων"
                    % (len(SPOTS), sum(1 for s_ in SPOTS if s_[1] != "T"), sum(1 for s_ in SPOTS if s_[1] == "T"), N_HEADS), A.SHEET_FLOOR,
                    "Βάση: τοιχοποιίες Β1 %s · ανόψεις Β1 %s · ξυλότυπος Σ5" % (W.REV, A.REV), "Κλίμακα 1:40 · A3", REV, DATE, total=2)

def table(c, x, y, cols, rows, head, size=6.6, rh=13.5, zebra=True, bold_last=False):
    """Απλός πίνακας: cols = [(τίτλος, πλάτος, στοίχιση)] · επιστρέφει το y κάτω από τον πίνακα."""
    c.setFont("Inter-SemiBold", size + 0.6); c.setFillColorRGB(*DARK)
    xx = x
    for t, w_, al in cols:
        c.drawString(xx + 3, y - rh + 3.2, t) if al == "l" else c.drawRightString(xx + w_ - 3, y - rh + 3.2, t)
        xx += w_
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.7); c.line(x, y - rh, x + sum(w_ for _, w_, _ in cols), y - rh)
    yy = y - rh
    for i, r in enumerate(rows):
        if zebra and i % 2 == 1:
            c.setFillColorRGB(0.965, 0.96, 0.95); c.rect(x, yy - rh, sum(w_ for _, w_, _ in cols), rh, stroke=0, fill=1)
        xx = x
        f = "Inter-SemiBold" if (bold_last and i == len(rows) - 1) else "Inter"
        c.setFont(f, size); c.setFillColorRGB(*DARK)
        for (t, w_, al), val in zip(cols, r):
            if al == "l":
                c.drawString(xx + 3, yy - rh + 3.2, str(val))
            else:
                c.drawRightString(xx + w_ - 3, yy - rh + 3.2, str(val))
            xx += w_
        yy -= rh
    c.setLineWidth(0.4); c.line(x, yy, x + sum(w_ for _, w_, _ in cols), yy)
    return yy

def sheet_f02(c):
    def H(x, y, s):
        c.setFont("Inter-SemiBold", 8.2); c.setFillColorRGB(*DARK); c.drawString(x, y, s)
    x0, y = 36, PAGE_H - 44
    H(x0, y, "1. ΓΕΝΙΚΟΣ ΦΩΤΙΣΜΟΣ – ΜΕΘΟΔΟΣ ΤΩΝ LUMEN   Φ = E · A / (UF · MF)   ·   MF %.2f   ·   ανακλάσεις οροφή 0,70 / τοίχοι 0,50 / δάπεδο 0,20" % MF)
    cols = [("Ζώνη", 300, "l"), ("A m²", 54, "r"), ("οροφή", 54, "r"), ("Hm m", 52, "r"), ("k", 44, "r"), ("E στόχος lx", 72, "r"), ("UF", 44, "r"),
            ("Φ απαιτ. lm", 78, "r"), ("spots", 60, "r"), ("Φ εγκατ. lm", 78, "r"), ("E μέση lx", 70, "r")]
    rows = []
    for z in ZONES:
        rows.append((z["name"], fm(z["A"], 1), "+" + fm(z["h"]), fm(z["h"] - z["wp"]), fm(z["k"]), z["E"], fm(z["UF"]), "%d" % round(z["need"], -1),
                     "%d × %d" % (z["n"], LM), "%d" % z["inst"], "%d" % round(z["Eavg"])))
    rows.append(("Κουζίνα – πρόσθετα: LED4 κάτω από τα ντουλάπια %s m × %d lm/m (δεν μετρά στον γενικό)" % (("%.1f" % LED4_LEN).replace(".", ","), LED4_LMM),
                 "", "", "", "", "", "", "", "ταινία", "%d" % round(LED4_LEN * LED4_LMM, -1), ""))
    y = table(c, x0, y - 8, cols, rows, "")
    y -= 16
    H(x0, y, "2. ΦΩΤΙΣΜΟΣ ΕΡΓΑΣΙΑΣ – spots 36° ακριβώς πάνω από την επιφάνεια   (ροή μέσα στη δέσμη %d %% · ποσοστό πάνω στην επιφάνεια κατά τη γεωμετρία)" % round(FIX["B"]["f_beam"] * 100))
    cols = [("Επιφάνεια", 300, "l"), ("A m²", 54, "r"), ("ύψος πάνω από την επιφάνεια m", 150, "r"), ("Ø κηλίδας m", 72, "r"), ("E στόχος lx", 72, "r"),
            ("spots", 60, "r"), ("E στο κέντρο κηλίδας lx", 128, "r"), ("E μέση στην επιφάνεια lx", 136, "r")]
    rows = []
    for t in TASKS:
        rows.append((t["name"], fm(rect_area(t["rect"])), fm(t["hm"]), fm(2 * t["r"]), t["E"], t["n"], "%d" % round(t["Ec"], -1), "%d" % round(t["Eres"], -1)))
    y = table(c, x0, y - 8, cols, rows, "")
    y -= 16
    H(x0, y, "3. ΦΩΤΙΣΤΙΚΑ – ΘΕΣΕΙΣ (m, από παρειές τοίχων) · ΚΥΚΛΩΜΑΤΑ")
    cols = [("φωτιστικό", 56, "l"), ("τύπος", 44, "l"), ("x", 46, "r"), ("y", 46, "r"), ("από δυτικό τοίχο", 100, "r"), ("από βόρειο τοίχο", 100, "r"),
            ("από νότιο τοίχο", 100, "r"), ("κύκλωμα", 60, "l"), ("χώρος / ρόλος", 420, "l")]
    role = {"Σ1": "καθιστικό – 0,50 μπροστά από τον καναπέ, δυτικά του τραπεζιού (μονό 60°)", "Σ2": "καθιστικό – πάνω από το τραπεζάκι (μονό 60°)", "Σ3": "καθιστικό – πέρασμα χωλ → καθιστικό (μονό 60°)",
            "ΔΣ1": "διπλό στον άξονα του επίπλου TV, 0,70 από τον τοίχο – κεφαλές στραμμένες στον τοίχο της TV (wall-wash)",
            "ΔΣ2": "διπλό μπροστά στο τζάμι W2.02, πλευρά τραπεζαρίας – κεφαλές κάτω / προς τις κουρτίνες",
            "ΔΤ": "διπλό στο κέντρο του τραπεζιού (6,40–8,20) – κεφαλές στραμμένες στα δύο άκρα του", "Ε1": "είσοδος – μπροστά στην πόρτα (λωρίδα +2,48)",
            "Ε2": "λωρίδα ΚΜ1 νότια της μονάδας – συνέχεια της σειράς στο τζάμι", "Κ1": "βόρειος πάγκος", "Κ2": "βόρειος πάγκος", "Κ3": "βόρειος πάγκος – εστίες",
            "Κ4": "πάγκος έρκερ Α", "Κ5": "πάγκος έρκερ Ν – δίπλα στο ψυγείο", "Κ6": "πάγκος έρκερ Ν – νεροχύτης", "Κ7": "πάγκος έρκερ Ν – πλυντήριο πιάτων"}
    rows = []
    for sp in SPOTS:
        sid, kind, x, yv, circ, zone = sp[:6]
        if zone == "ΚΑΘ":
            dw, dn, ds = x - WX0, yv - NORTH, SOUTH - yv
        else:
            dw, dn, ds = x - LIN_X, yv - KY, (BAY_S if yv > 9.15 else 9.15) - yv
        rows.append((sid, kind, fm(x), fm(yv), fm(dw), fm(dn), fm(ds), circ, role[sid]))
    y = table(c, x0, y - 8, cols, rows, "", size=6.0, rh=12.0)
    # κυκλώματα + σύνολα (δεξιά, κάτω από τον 2ο πίνακα δεν χωρά – εδώ δίπλα στον 3ο αν υπάρχει χώρος αλλιώς από κάτω)
    y -= 14
    H(x0, y, "4. ΚΥΚΛΩΜΑΤΑ · ΣΥΝΟΛΑ")
    cols = [("κύκλωμα", 66, "l"), ("περιγραφή", 400, "l"), ("φωτιστικά (κεφαλές)", 110, "r"), ("W", 50, "r"), ("lm", 60, "r")]
    rows = []
    for k_ in ("σ1", "σ2", "τ", "β", "ε1", "ε2"):
        n = sum(FIX[s[1]]["heads"] for s in SPOTS if s[4] == k_)
        nf = sum(1 for s in SPOTS if s[4] == k_)
        rows.append((k_, CIRCUITS[k_], "%d (%d)" % (nf, n), n * WATT, n * LM))
    rows.append(("ε3", CIRCUITS["ε3"], "ταινία", round(LED4_LEN * LED4_WM), round(LED4_LEN * LED4_LMM, -1)))
    rows.append(("ΣΥΝΟΛΟ", "καθιστικό – τραπεζαρία – είσοδος – κουζίνα · φωτιστικά (κεφαλές) + LED", "%d (%d)" % (len(SPOTS), N_HEADS),
                 N_HEADS * WATT + round(LED4_LEN * LED4_WM), N_HEADS * LM + round(LED4_LEN * LED4_LMM, -1)))
    table(c, x0, y - 8, cols, rows, "", bold_last=True)
    frame_and_title(c, "Φ-02", "ΦΩΤΙΣΜΟΣ ΚΑΘΙΣΤΙΚΟΥ – ΤΡΑΠΕΖΑΡΙΑΣ – ΚΟΥΖΙΝΑΣ · ΥΠΟΛΟΓΙΣΜΟΣ LUMEN · ΠΙΝΑΚΑΣ ΦΩΤΙΣΤΙΚΩΝ",
                    "στόχοι: καθιστικό 150 lx · κουζίνα 200 lx · τραπέζι 300 lx · πάγκοι 500 lx (spots) + LED κάτω από τα ντουλάπια", A.SHEET_FLOOR,
                    "Βάση: τοιχοποιίες Β1 %s · ανόψεις Β1 %s" % (W.REV, A.REV), "– · A3", REV, DATE, total=2)

if __name__ == "__main__":
    rows = checks_all()
    bad = [r for r in rows if r[2] != "OK"]
    for r in rows:
        print("%-7s %-22s %-78s %s" % (r[2], r[0], r[1], r[3]))
    if bad:
        sys.exit("ΛΑΘΟΣ στον έλεγχο – διόρθωσε πριν το παραδοτέο.")
    c = new_canvas(OUT, "Φωτισμός καθιστικού – κουζίνας Β1 – Κωνσταντινουπόλεως 12")
    sheet_f01(c); c.showPage()
    sheet_f02(c); c.showPage()
    c.save()
    print("OK", os.path.abspath(OUT), "· %d φωτιστικά / %d κεφαλές · %d W · %d lm + LED4 %.1f m" % (len(SPOTS), N_HEADS, N_HEADS * WATT, N_HEADS * LM, LED4_LEN))
