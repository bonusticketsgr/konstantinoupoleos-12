# -*- coding: utf-8 -*-
"""Φύλλο ΠΧ-01: ΚΑΤΟΨΗ ΔΙΑΜΟΡΦΩΣΗΣ ΠΕΡΙΒΑΛΛΟΝΤΟΣ ΧΩΡΟΥ ΙΣΟΓΕΙΟΥ – A3 οριζόντιο, 1:75.
Υπόβαθρο: η κάτοψη τοιχοποιιών ισογείου (gf_model R15) + ο περιβάλλων χώρος του αρχιτέκτονα αχνά (gf_site.json). Πάνω της:
ζώνες με τελικές στάθμες (χρώμα ανά είδος), ΜΠΑΖΩΜΑΤΑ (διαγράμμιση), τοιχία που σηκώνονται (κόκκινα) και υπάρχοντα του Σ2
(σκούρα), σκάλες ανόδου, πύλες, στάθμες, διαστάσεις, ίχνη τομών."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, "..", "toixopoiies")
sys.path.insert(0, TX)
import px_model as PM
from draw import View, PAGE_W, PAGE_H, DARK, GREY, LIGHT, DIMC, frame_and_title, north_arrow
import sheet_t01
import gf_model as G
import b_model as Y

PT_PER_M = 72 / 25.4 * 1000 / 80          # 1:80 → 33,07 pt/m (στο 1:75 δεν χωρούσε με τις διαστάσεις και τους δρόμους)
OX = 34 + 6.6 * PT_PER_M                  # x = −6,60 m στα 34 pt από αριστερά
OY = 36 + 2.35 * PT_PER_M                 # y = −2,35 m στα 36 pt από πάνω
COL_X = 34 + 25.3 * PT_PER_M              # αρχή δεξιάς στήλης (x ≈ 18,7 m)

# χρώματα
C_SOIL = (0.84, 0.91, 0.78); C_GRAVEL = (0.92, 0.92, 0.88); C_PAV = (0.97, 0.94, 0.85); C_PATH = (0.90, 0.90, 0.92)
C_STAIR = (0.99, 0.89, 0.76); C_RAMP = (0.94, 0.94, 0.97); C_STRUCT = (0.86, 0.86, 0.88); C_LAND = (0.99, 0.86, 0.68)
C_FILL = (0.80, 0.48, 0.12)               # διαγράμμιση μπαζώματος
C_NEW = (0.80, 0.16, 0.14)                # νέα τοιχία
C_S2 = (0.38, 0.38, 0.42)                 # υπάρχοντα κατά Σ2
C_BASE = (0.55, 0.55, 0.58)               # τοιχεία υπογείου (έδραση)
C_LEVEL = (0.10, 0.11, 0.13)
C_FENCE = (0.45, 0.22, 0.52)              # βάσεις περίφραξης (μοβ-κόκκινο)
C_BOUND = (0.30, 0.35, 0.55)              # μάντρες ορίων / στηθαία ράμπας

ZONE_FILL = {"pav": C_PAV, "pocket": C_PAV, "path": C_PATH, "stair": C_STAIR, "soil": C_SOIL, "gravel": C_GRAVEL,
             "ramp": C_RAMP, "struct": C_STRUCT}
WALL_FILL = {"fence": C_FENCE, "lobby": C_FENCE, "bound": C_BOUND, "ret": C_NEW, "curb": C_NEW, "s2": C_S2}

# ετικέτες ζωνών: id → (x, y, στροφή, γραμμές)
def _lv(v): return ("%+.2f" % v).replace(".", ",")
LABELS = {
    "Ζ01": (-0.45, 8.55, 90, ["ΔΥΤΙΚΗ ΒΕΡΑΝΤΑ  +0,40", "ΜΠΑΖΩΜΑ 30 (±0,00 → +0,30) + 10"]),
    "Ζ02": (2.35, 10.22, 0, ["+0,40", "μπάζ. 30"]),
    "Ζ03": (4.95, 10.15, 0, ["ΒΕΡΑΝΤΑ ΙΣ1  +0,40", "θύλ. Α: μπάζ. 52 + h18 + 10"]),
    "Ζ04": (7.75, 9.85, 0, ["+0,40 · θύλ. Β"]),
    "Ζ05": (10.92, 10.15, 0, ["ΠΛΑΤΥΣΚΑΛΟ  +0,74", "θύλ. Γ: μπάζ. 1,01 + h18 + 10"]),
    "Ζ06": (10.42, 1.55, 90, ["ΒΑ ΒΕΡΑΝΤΑ +0,40 · μπάζ. 30"]),
    "Ζ07": (-2.55, -0.25, 0, ["Θ.Σ.Ι.1  +0,40", "ΜΠΑΖΩΜΑ 30 + βιομ. δάπεδο 10"]),
    "Ζ08": (-4.68, 2.53, 90, ["ΚΑΔΟΙ +0,40"]),
    "Ζ09": (0.30, 3.0, 90, ["ΛΩΡΙΔΑ +0,40 · μπάζ. 30"]),
    "Ζ10": (5.5, 13.35, 0, ["ΔΙΑΔΡΟΜΟΣ ΙΣ1", "−0,30"]),
    "Ζ11": (5.5, 14.95, 0, ["−0,30"]),
    "Ζ12": (10.92, 13.62, 0, ["ΔΙΑΔΡΟΜΟΣ  −0,45"]),
    "Ζ13": (10.35, 14.95, 0, ["−0,45"]),
    "Ζ16": (5.2, 0.1, 0, ["βότσαλο +0,30"]),
    "Κ1": (-3.6, 7.6, 90, ["ΚΗΠΟΣ – χώμα +0,30 (30 cm στην πλάκα ±0,00)"]),
    "Κ2": (1.2, 13.55, 0, ["ΚΗΠΟΣ ΙΣ1 (αποκλ. χρήσης) – χώμα +0,30", "δυτικά του x −1,25 φυσικό έδαφος"]),
    "Κ3": (7.75, 12.3, 90, ["Φ.Χ.3  +0,30"]),
    "Κ4": (9.27, 12.4, 90, ["Φ.Χ.4 +0,30"]),
    "Κ5": (12.72, 11.45, 90, ["Φ.Χ.5  +0,30"]),
    "Κ6": (8.0, 14.85, 0, ["Φ.Χ.7  −0,20"]),
    "Κ7": (11.85, 14.85, 0, ["Φ.Χ.6 −0,35"]),
    "Κ8": (14.3, 1.0, 0, ["ΚΗΠΟΣ Β–ΒΑ – χώμα +0,30", "(30 cm στην πλάκα ±0,00)"]),
    "Ρ": (15.1, 9.2, 90, ["ΡΑΜΠΑ Ι.Χ. κατά Σ2 – κλίση 16,12 %"]),
    "Σ2": (15.1, 3.65, 0, ["Π15 +1,35 (Σ2)"]),
}

# θέσεις ετικετών τοιχίων: id → (x, y, στροφή)· όσα λείπουν μπαίνουν στο κέντρο
WLAB = {
    "ΤΧ-01": (-5.55, 7.6, 90), "ΤΧ-02": (-3.75, 14.3, -45), "ΤΧ-03": (1.5, 15.78, 0), "ΤΧ-04": (3.95, 14.85, 90),
    "ΤΧ-05": (7.9, 14.1, 0), "ΤΧ-06": (12.0, 14.1, 0), "ΤΧ-07": (12.85, 13.95, 90), "ΤΧ-08": (6.3, 14.85, 90),
    "ΤΧ-09": (9.95, 14.85, 90), "ΤΧ-10": (8.0, 15.78, 0), "ΤΧ-11": (11.9, 15.78, 0), "ΤΧ-12": (13.15, 14.85, 90),
    "ΤΧ-13": (17.3, 6.5, 90), "ΤΧ-14": (6.0, -1.62, 0), "ΤΧ-15": (13.225, 11.2, 90), "ΤΧ-16": (-2.6, 8.8, 90),
    "ΤΧ-17": (-1.2, 5.0, 0), "ΤΧ-18": (0.9, 11.75, 0), "ΤΧ-19": (-0.35, 2.2, 90), "ΤΧ-20": (-2.3, 1.62, 0),
    "ΤΧ-21": (10.5, 0.1, 0), "ΤΧ-22": (11.4, 1.6, 90), "ΤΧ-23": (4.05, 12.8, 90), "ΤΧ-24": (6.95, 11.0, 90),
    "ΤΧ-25": (8.55, 10.9, 90), "ΤΧ-26": (9.3, 11.0, 90), "ΤΧ-27": (12.6, 12.6, 90), "ΤΧ-28": (12.62, 13.45, 0),
    "Δ23.1": (3.25, 13.0, 90), "Δ24.1": (9.55, 13.4, 90), "ΘΑ": (3.85, 11.22, 0), "ΘΒ": (7.75, 10.22, 0), "ΘΓ": (11.75, 10.95, 0),
}

SECTIONS = [  # (όνομα, (x0, y0), (x1, y1)) – ίχνη τομών της ΠΧ-02 / ΠΧ-03
    ("Α", (10.30, 7.9), (10.30, 16.65)), ("Β", (5.55, 7.9), (5.55, 16.65)), ("Γ", (-6.4, 7.5), (2.6, 7.5)),
    ("Δ", (-6.4, 0.8), (1.6, 0.8)), ("Ε", (8.4, 1.5), (17.8, 1.5)), ("ΣΤ", (2.0, 8.5), (2.0, 16.65)),
]


def poly_fill(v, poly, fill, stroke=None, lw=0.3):
    v.poly(poly, fill=fill, stroke=stroke, lw=lw)


def draw_underlay(v):
    """Περιβάλλων χώρος του αρχιτέκτονα αχνά (έξω από το κτήριο) + η κάτοψη τοιχοποιιών ισογείου."""
    site = json.load(open(os.path.join(TX, "data", "gf_site.json")))
    k = 0.42
    sheet_t01._draw_paths(v, site, lambda rgb: tuple(1 - (1 - ch) * k for ch in rgb), clip_building=G.BUILDING, lw=(0.2, 0.3, 0.45))
    sheet_t01.M = G
    sheet_t01.OX, sheet_t01.OY = OX, OY
    sheet_t01.draw_plan(v, with_labels=False, with_dims=False, with_furniture=False, with_text=False)
    sheet_t01.draw_core(v)


def draw_basement_walls(v):
    """Τα τοιχεία του υπογείου έξω από το κτήριο (έδραση των μαντρών / περίφραξης) – γκρι διαγράμμιση."""
    for poly in Y.COLS:
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        if 0.7 <= min(xs) and max(xs) <= 13.45 and 0.4 <= min(ys) and max(ys) <= 9.55:
            continue                      # μέσα στο κτήριο (τα δείχνει η κάτοψη τοιχοποιιών)
        v.poly(poly, fill=(0.93, 0.93, 0.94), stroke=C_BASE, lw=0.4)
        v.hatch(poly, 0.10, 45, (0.78, 0.78, 0.80), 0.25)


def draw_zones(v):
    for z in PM.ZONES:
        v.poly(z["poly"], fill=ZONE_FILL[z["kind"]])
    # πλατύσκαλο εισόδου πιο έντονο
    v.poly(PM.ZONE["Ζ05"]["poly"], fill=C_LAND)
    for z in PM.ZONES:
        if z["kind"] in ("pav", "pocket"):
            v.hatch(z["poly"], 0.22, 45, C_FILL, 0.35)
        if z["kind"] == "stair":
            v.hatch(z["poly"], 0.22, 45, C_FILL, 0.25)
        v.poly(z["poly"], stroke=(0.62, 0.62, 0.65), lw=0.35)
    # ράμπα: βέλος καθόδου
    v.line(15.1, 15.2, 15.1, 4.4, color=(0.5, 0.5, 0.6), lw=0.6)
    v.line(15.1, 4.4, 14.85, 4.9, color=(0.5, 0.5, 0.6), lw=0.6); v.line(15.1, 4.4, 15.35, 4.9, color=(0.5, 0.5, 0.6), lw=0.6)


def draw_walls(v):
    for w in PM.WALLS:
        col = WALL_FILL[w["kind"]]
        v.poly(w["poly"], fill=col, stroke=DARK, lw=0.45)
    for w in PM.WALLS:
        x, y, rot = WLAB.get(w["id"], (sum(p[0] for p in w["poly"]) / len(w["poly"]), sum(p[1] for p in w["poly"]) / len(w["poly"]), 0))
        s = w["id"]
        v.text(x, y, s, size=4.6 if w["kind"] != "s2" else 4.2, font="Inter-SemiBold", color=(WALL_FILL[w["kind"]] if w["kind"] != "ret" and w["kind"] != "curb" else C_NEW),
               rot=rot, bg=True)


def draw_stairs(v):
    for s in PM.STAIRS:
        for i, yy in enumerate(s["risers"]):
            v.line(s["x0"], yy, s["x1"], yy, color=DARK, lw=0.7)
        # βέλος ανόδου (από κάτω προς τα πάνω = νότος → βορράς)
        xm = (s["x0"] + s["x1"]) / 2
        y0 = s["y_bot"] + 0.25; y1 = s["y_top"] - 0.35
        v.line(xm, y0, xm, y1, color=DARK, lw=0.6)
        v.line(xm, y1, xm - 0.12, y1 + 0.22, color=DARK, lw=0.6); v.line(xm, y1, xm + 0.12, y1 + 0.22, color=DARK, lw=0.6)
        v.circle(xm, y0, 0.07, stroke=DARK, lw=0.5)
        txt = "%s  %d × %s / %d" % (s["id"], s["n"], ("%.1f" % (s["riser"] * 100)).replace(".", ","), round(s["tread"] * 100))
        v.text(xm + 0.55 if s["id"] == "ΣΚ-Α" else xm - 0.55, (y0 + y1) / 2, txt, size=5.0, font="Inter-Bold", rot=90, bg=True)
        # στάθμες των πατημάτων (μικρά)
        for i, lv in enumerate(s["levels"][:-1]):
            v.text(s["x0"] + 0.22 if s["id"] == "ΣΚ-Α" else s["x1"] - 0.22, s["risers"][i] + s["tread"] / 2, _lv(lv), size=3.6, color=GREY, font="Inter-Medium")


def draw_gates(v):
    for g in PM.GATES:
        (x0, y0), (x1, y1) = g["pts"]
        v.line(x0, y0, x1, y1, color=(0.2, 0.45, 0.25), lw=1.6)
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        if x0 == x1:
            v.text(x0 - 0.22, ym, g["id"], size=4.4, font="Inter-SemiBold", color=(0.2, 0.45, 0.25), rot=90, bg=True)
        else:
            v.text(xm, ym + 0.33, g["id"], size=4.4, font="Inter-SemiBold", color=(0.2, 0.45, 0.25), bg=True)


def draw_labels(v):
    for zid, (x, y, rot, lines) in LABELS.items():
        n = len(lines)
        for i, ln in enumerate(lines):
            off = (i - (n - 1) / 2) * 0.24
            if rot == 90:
                v.text(x + off, y, ln, size=5.4 if i == 0 else 4.4, font="Inter-SemiBold" if i == 0 else "Inter", color=DARK if i == 0 else (0.35, 0.35, 0.4), rot=90, bg=True)
            else:
                v.text(x, y + off, ln, size=5.4 if i == 0 else 4.4, font="Inter-SemiBold" if i == 0 else "Inter", color=DARK if i == 0 else (0.35, 0.35, 0.4), bg=True)
    for x, y, s in PM.LEVELS:
        v.text(x, y, s, size=5.2, font="Inter-Bold", color=C_LEVEL, bg=True)
    for x, y, s in PM.STREET_LEVELS:
        v.text(x, y, s, size=4.8, font="Inter-Medium", color=(0.3, 0.3, 0.35), bg=True, rot=90 if x < -5.5 or x > 17.5 else 0)
    # ονόματα δρόμων
    v.text(14.2, 16.6, "ΟΔΟΣ ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ  πλ. 14,00 (πεζοδρόμιο Β −0,11 → Α −0,60)", size=5.8, font="Inter-Medium", color=(0.3, 0.3, 0.35))
    v.text(-6.4, 4.2, "ΟΔΟΣ ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ  πλ. 14,00", size=5.8, font="Inter-Medium", color=(0.3, 0.3, 0.35), rot=90)
    v.text(5.5, -2.2, "ΓΕΙΤΟΝΑΣ – βόρειο όριο (Ε +0,40 → Ζ −0,21)", size=5.0, font="Inter-Medium", color=(0.3, 0.3, 0.35))
    v.text(18.3, 7.0, "ΓΕΙΤΟΝΑΣ – ανατολικό όριο (Ζ −0,21 → Α −0,60)", size=5.0, font="Inter-Medium", color=(0.3, 0.3, 0.35), rot=90)
    # ΑΜΕΑ
    v.rect(11.20, 12.95, 12.10, 14.35, stroke=(0.3, 0.3, 0.6), lw=0.5)
    v.text(11.65, 13.65, "ΑΜΕΑ 0,90 × 1,40", size=3.8, color=(0.3, 0.3, 0.6), rot=90)


def draw_dims(v):
    S = 5.0
    v.dim_chain("H", 16.2, [-1.20, 4.30, 4.50, 6.50, 9.70, 12.15, 13.35, 16.82, 17.12], size=S, side=-1)
    v.dim_chain("H", -1.9, [-5.20, -4.995, -0.10, 0.70, 9.80, 11.05, 13.45, 16.87], size=S, side=-1)
    v.dim_chain("V", -5.95, [-1.45, -1.26, 1.24, 1.44, 3.62, 3.82, 5.35, 11.35, 11.46], size=S, side=-1)
    v.dim_chain("V", 17.75, [-1.58, 3.30, 4.01, 9.55, 15.45], size=S, side=+1)
    v.dim_chain("V", 14.0, [9.55, 11.07, 12.87, 13.35, 13.55, 14.25, 14.45, 15.45], size=4.4, side=+1)
    v.dim_chain("V", 3.75, [9.55, 11.35, 12.25, 14.25, 14.45, 15.45], size=4.4, side=-1)
    v.dim_chain("H", 9.35, [3.40, 6.50, 6.70, 8.85, 9.00, 9.55, 9.70, 12.15, 12.35, 13.10, 13.35], size=4.0, side=-1)


def draw_sections(v):
    for name, (x0, y0), (x1, y1) in SECTIONS:
        v.line(x0, y0, x1, y1, color=(0.1, 0.2, 0.5), lw=0.5, dash=[6, 3])
        for (x, y) in ((x0, y0), (x1, y1)):
            v.circle(x, y, 0.19, fill=(1, 1, 1), stroke=(0.1, 0.2, 0.5), lw=0.6)
            v.text(x, y, name, size=4.4, font="Inter-Bold", color=(0.1, 0.2, 0.5))


def legend(c, x, y, width=285):
    """Υπόμνημα στη δεξιά στήλη (pt) – τα κείμενα αναδιπλώνονται στο πλάτος της στήλης."""
    def wrap(s, font, size, w):
        out, cur = [], ""
        for wd in s.split(" "):
            tt = (cur + " " + wd).strip()
            if c.stringWidth(tt, font, size) > w and cur:
                out.append(cur); cur = wd
            else:
                cur = tt
        return out + [cur]
    def t(X, Y, s, font="Inter", size=6.2, color=DARK):
        c.setFont(font, size); c.setFillColorRGB(*color)
        lines = wrap(s, font, size, width - (X - x))
        for i, ln in enumerate(lines):
            c.drawString(X, Y - i * (size + 1.6), ln)
        return len(lines)
    def box(X, Y, fill, hatch=None, stroke=(0.6, 0.6, 0.63)):
        c.setFillColorRGB(*fill); c.setStrokeColorRGB(*stroke); c.setLineWidth(0.4); c.rect(X, Y, 22, 11, stroke=1, fill=1)
        if hatch:
            c.saveState(); p = c.beginPath(); p.rect(X, Y, 22, 11); c.clipPath(p, stroke=0, fill=0)
            c.setStrokeColorRGB(*hatch); c.setLineWidth(0.4)
            for k in range(-12, 24, 4):
                c.line(X + k, Y, X + k + 11, Y + 11)
            c.restoreState()
    t(x, y, "ΥΠΟΜΝΗΜΑ", "Inter-Bold", 8); y -= 16
    rows = [
        (C_PAV, C_FILL, "ΠΛΑΚΟΣΤΡΩΤΟ +0,40 ΜΕ ΜΠΑΖΩΜΑ (±0,00 → +0,30) + επίστρωση 10"),
        (C_LAND, C_FILL, "ΠΛΑΤΥΣΚΑΛΟ ΕΙΣΟΔΟΥ +0,74: μπάζωμα ως +0,46 + πλάκα h18 + 10"),
        (C_STAIR, C_FILL, "ΣΚΑΛΕΣ ΕΠΙ ΜΠΑΖΩΜΑΤΟΣ (ΣΚ-Α 7 × 17,0 / 30 · ΣΚ-Β 4 × 17,5 / 30)"),
        (C_PATH, None, "ΔΙΑΔΡΟΜΟΙ ΣΤΗ ΣΤΑΘΜΗ ΤΟΥ ΔΡΟΜΟΥ: επίστρωση 10 στην πλάκα (−0,30 / −0,45)"),
        (C_SOIL, None, "ΦΥΤΕΜΕΝΟ: χώμα ως +0,30 (30 cm στην πλάκα ±0,00 · 70–85 στις ζαρντινιέρες)"),
        (C_GRAVEL, None, "ΒΟΤΣΑΛΟ +0,30 (βόρεια λωρίδα – χωρίς γέμισμα)"),
        (C_RAMP, None, "ΡΑΜΠΑ / ΣΤΟΜΙΟ κατά Σ2 (δεν αλλάζει)"),
    ]
    for fill, hatch, s in rows:
        box(x, y - 3, fill, hatch); n = t(x + 28, y, s, size=5.8); y -= 9 + 7.4 * n
    y -= 4
    t(x, y, "ΤΟΙΧΙΑ ΠΟΥ ΣΗΚΩΝΟΝΤΑΙ ΠΑΝΩ ΣΤΗΝ ΠΛΑΚΑ Σ2", "Inter-Bold", 7); y -= 14
    rows2 = [
        (C_FENCE, "ΤΧ-01…03 βάση περίφραξης: κορυφή +0,81 + περσίδες 1,25 → +2,06"),
        (C_FENCE, "ΤΧ-04…07 εσοχή πυλών: τοίχος σκυροδέματος ως +2,06 (στέγαστρο A-80-02)"),
        (C_BOUND, "ΤΧ-13…15 μάντρες ορίων / στηθαίο ράμπας: κορυφή +1,20"),
        (C_NEW, "ΤΧ-16…22 κράσπεδα βεραντών – Θ.Σ.Ι.1: 0,15, κορυφή +0,40"),
        (C_NEW, "ΤΧ-23…28 τοιχία σκαλών / ζαρντινιέρων: κορυφή +0,40 (ΤΧ-26/27: +0,74 → +0,57 → +0,40)"),
        (C_S2, "ΥΠΑΡΧΟΝΤΑ ΚΑΤΑ Σ2: Δ23.1 (κορυφή ±0,00) · Δ24.1 ανεστρ. (−0,05) · τοιχία θυλάκων ΘΑ/ΘΒ/ΘΓ"),
        ((0.93, 0.93, 0.94), "τοιχεία υπογείου 30 / 25 (Σ2) – έδραση περίφραξης και μαντρών"),
    ]
    for fill, s in rows2:
        box(x, y - 3, fill, None if fill != (0.93, 0.93, 0.94) else (0.78, 0.78, 0.80), stroke=DARK); n = t(x + 28, y, s, size=5.8); y -= 9 + 7.4 * n
    y -= 4
    t(x, y, "ΣΤΑΘΜΕΣ ΠΛΑΚΑΣ ΟΡΟΦΗΣ ΥΠΟΓΕΙΟΥ (Σ2_ΕΦ)", "Inter-Bold", 7); y -= 13
    for s in ["±0,00  δυτικά της Δ23.1 (x 3,40), βόρεια, ΒΑ, Θ.Σ.Ι.1 – Π11 / Π12–Π14 / Π16 / Π17",
              "−0,40  x 3,40 – 9,40 (είσοδος ΙΣ1, Φ.Χ.3/4) – ανάμεσα στις Δ23.1 και Δ24.1",
              "−0,55  x 9,70 – 13,10 (είσοδος κτηρίου, Φ.Χ.5) – Π19 h=25",
              "κτήριο +0,30 · πεζοδρόμια: Ε +0,40 · Β −0,11 · Α −0,60 · Ζ −0,21"]:
        n = t(x, y, s, size=5.8); y -= 4 + 7.4 * n
    y -= 6
    t(x, y, "ΤΕΛΙΚΕΣ ΣΤΑΘΜΕΣ", "Inter-Bold", 7); y -= 13
    for s in ["ΙΣ1 +0,42 · χωλ κτηρίου +0,74 · βεράντες / Θ.Σ.Ι.1 / λωρίδες +0,40",
              "κήπος +0,30 · διάδρομος ΙΣ1 −0,30 · διάδρομος εισόδου −0,45",
              "είσοδος κτηρίου: −0,45 → 7 × 17,0 → +0,74 (ΣΚ-Α) · ΙΣ1: −0,30 → 4 × 17,5 → +0,40 (ΣΚ-Β)",
              "τομές Α-Α … ΣΤ-ΣΤ στα φύλλα ΠΧ-02 / ΠΧ-03 · πίνακες τοιχίων και μπαζωμάτων στο ΠΧ-04"]:
        n = t(x, y, s, size=5.8); y -= 4 + 7.4 * n
    return y


def sheet_plan(c, sheet_no="ΠΧ-01"):
    v = View(c, OX, OY, PT_PER_M)
    draw_zones(v)
    draw_underlay(v)
    draw_basement_walls(v)
    # ξανά οι ζώνες μόνο ως περιγράμματα + διαγράμμιση πάνω από το υπόβαθρο (το υπόβαθρο είναι αχνό)
    for z in PM.ZONES:
        if z["kind"] in ("pav", "pocket", "stair"):
            v.hatch(z["poly"], 0.22, 45, C_FILL, 0.35)
        v.poly(z["poly"], stroke=(0.55, 0.55, 0.58), lw=0.4)
    draw_walls(v)
    draw_stairs(v)
    draw_gates(v)
    draw_sections(v)
    draw_labels(v)
    draw_dims(v)
    # δεξιά στήλη
    c.setFillColorRGB(1, 1, 1); c.rect(COL_X, 92, PAGE_W - 20 - COL_X, PAGE_H - 112, stroke=0, fill=1)
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.6); c.line(COL_X, 92, COL_X, PAGE_H - 20)
    legend(c, COL_X + 10, PAGE_H - 36, width=PAGE_W - 30 - COL_X - 10)
    north_arrow(c, PAGE_W - 48, 130, 12)
    frame_and_title(c, sheet_no, "ΠΕΡΙΒΑΛΛΩΝ ΧΩΡΟΣ ΙΣΟΓΕΙΟΥ – ΔΙΑΜΟΡΦΩΣΗ",
                    "Κάτοψη: στάθμες, τοιχία που σηκώνονται, μπαζώματα, σκάλες ανόδου στο ισόγειο",
                    "Τελικό ΙΣ1 +0,42 · χωλ +0,74 · βεράντες +0,40 · κήπος +0,30",
                    "Βάση: Σ2_ΕΦ (στάθμες πλάκας) · A-10-GF R01 · Α-30-ΑΑ/ΒΒ · Α-40 · A-80-02/03/04 · τοιχοποιίες ΙΣ R15 · τεύχος σκαλών",
                    "ΚΛΙΜΑΚΑ 1:80 (A3)", PM.REV, PM.DATE)
