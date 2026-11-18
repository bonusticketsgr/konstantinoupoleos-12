"""Στρώσεις σχεδίασης και υπόμνημα για τις κατόψεις της ηλεκτρολογικής μελέτης (A3, 1:50). Τα φύλλα είναι στο el_sheets.py.
Υπόβαθρο: μονόχρωμη κάτοψη από το μοντέλο τοιχοποιιών (apox_pro.base). Καμία σημείωση πάνω στην κάτοψη – υπόμνημα και πίνακες στη δεξιά στήλη."""
import math
import el_draw as D
from el_draw import P, PWR, LGT, SWC, DAT, FIR, HVC, AUT, FEED, BEAMC, INK, MUTE, FAINT, PAGE_W, PAGE_H, SW, ptext
import el_checks as CK
import el_geom as G

M = W = A = None
S = D.S50
OX, OY = 96.9, 67.7
PANEL_X = 900.0
FLOORC = (0.50, 0.33, 0.12)       # οδεύσεις στο γέμισμα δαπέδου
WALLC = (0.10, 0.36, 0.72)        # οριζόντιες οδεύσεις μέσα σε τοίχο
SLABC = (0.80, 0.50, 0.10)


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A
    CK.bind(model)
    P.PANEL_X = PANEL_X; P.PX = PANEL_X + 12; P.PW = PAGE_W - 20 - PANEL_X - 24
    P.REV, P.DATE = M.REV, M.DATE
    P.SUB1 = "%s · %s" % (M.REV, M.STATUS)


def C():
    return P.C


def _plan(fn, title):
    P.begin_plan(); v = P.view(OX, OY, S); v.sym = 1.0
    P.base(v, W, site=False, rooms=True, furniture=True)
    fn(v)
    P.end_plan()
    P.view_title(title, "Κλίμακα 1:50"); P.scale_bar(50)
    return v


def _finish(no, theme, sub2):
    P.finish(no, theme, sub2, M.BASE_TXT, "Κλίμακα 1:50 · A3")


def _opt(t, i):
    return t[i] if len(t) > i else {}


# ================================================================ στρώσεις σχεδίασης
def panel(v, lab=True):
    D.zone(v, M.TN, FEED, alpha=0.06, dash=(2.2, 1.4), lw=0.6)
    p = M.PANEL
    D.panel(v, (p["x"] - 0.10, p["y0"], p["x"], p["y1"]), lab="ΓΠ" if lab else None, lab_off=(0.42, -0.02), anchor="l")
    if lab:
        D.halo_text(v, (M.TN[0] + M.TN[2]) / 2 - 0.03, M.TN[1] + 0.13, "ΤΝ", size=4.6, color=FEED)


def lights(v, labels=False, groups=False, faint=False):
    col = (0.93, 0.74, 0.42) if faint else LGT
    for q in M.STAIR_SPOTS:
        D.spot(v, q[2], q[3], q[1], col=(0.70, 0.70, 0.74))
    for q in M.SPOTS:
        D.spot(v, q[2], q[3], q[1], col=col, lab=q[0] if labels else None, lab_off=SPOT_LAB.get(q[0], (0.0, -0.13)))
    for (n, x, y, g, t) in M.PENDANTS:
        D.pendant(v, x, y, col=col, lab=n if labels else None)
    tr = M.TRACK
    D.track(v, tr["a"], tr["b"], heads=tr["heads"], col=col, lab=(tr["id"] + " ράγα 2,40 m") if labels else None)
    for (n, a, b, g, t) in M.LED:
        D.led_line(v, a, b, col=col, lab=(n if (labels and t) else None))
    for l in M.WALL_LIGHTS:
        D.wall_light(v, l[1], l[2], l[3], col=col, kind=l[4], lab=l[0] if labels else None, lab_off=WL_LAB.get(l[0]))
    for e in M.EMERGENCY:
        D.wall_dev(v, e[1], e[2], e[3], "Α", col=(0.15, 0.55, 0.25) if not faint else (0.6, 0.8, 0.65), lab=e[0] if labels else None)
    if groups:
        for g, x, y in GROUP_TAGS:
            X, Y = v.p(x, y)
            P.pill(X, Y, g, None, LGT, "c", 5.6)


SPOT_LAB = {}
WL_LAB = {}
GROUP_TAGS = [("α", 4.86, 5.80), ("β", 8.47, 5.65), ("γ", 7.98, 7.25), ("ε", 11.85, 8.86), ("ζ", 2.75, 1.85), ("η", 4.20, 4.10), ("θ", 4.38, 0.36),
              ("κ", 7.83, 2.45), ("λ", 5.40, 8.45), ("μ", 6.05, 1.25), ("ν", 2.05, 4.42), ("ε2", 12.75, 8.22), ("ζ1", 1.42, 0.98), ("ζ2", 3.90, 0.98),
              ("κ1", 7.08, 1.56), ("μ2", 5.40, 3.06), ("ν2", 2.86, 4.78), ("ξ1", 5.60, 9.90), ("ξ2", 0.42, 3.08), ("ξ3", 10.10, 2.76)]


def switches(v, labels=False, func=False, faint=False):
    col = (0.55, 0.68, 0.86) if faint else SWC
    for s in M.SWITCHES:
        kinds = tuple(k for k, g in s[4])
        lab = None
        if labels:
            lab = s[0] + ((" " + "·".join(g for k, g in s[4] if not g.startswith("W"))) if func else "")
        D.switch(v, s[1], s[2], s[3], kinds, col=col, lab=lab, lab_off=SW_LAB.get(s[0]))


SW_LAB = {"Δ1": (-0.62, -0.02), "Δ3": (-0.72, 0.04), "Δ2": (0.10, 0.50), "Δ4": (-0.42, 0.30), "Δ5": (0.48, 0.02), "Δ6": (0.0, 0.46), "Δ7": (0.22, -0.42),
          "Δ8": (0.06, 0.52), "Δ9": (-0.06, 0.52), "Δ10": (-0.02, -0.44), "Δ11": (0.56, 0.06), "Δ12": (0.60, 0.10), "Δ13": (-0.62, 0.10),
          "Δ14": (0.60, 0.12), "Δ15": (-0.42, -0.34), "Δ16": (0.62, 0.16)}


def sockets(v, labels=False, faint=False, circ=False):
    col = (0.90, 0.60, 0.60) if faint else PWR
    for s in M.SOCKETS:
        opt = _opt(s, 10)
        lab = None
        if labels:
            lab = s[0][1:] if not circ else "%s·%s" % (s[0][1:], s[7])
        if s[5] == "fix":
            D.fixed_out(v, s[1], s[2], s[3], col=col, lab=lab, lab_off=SOCK_LAB.get(s[0], opt.get("lab_off")))
        else:
            D.socket(v, s[1], s[2], s[3], n=s[4], col=col, kind=s[5], lab=lab, lab_off=SOCK_LAB.get(s[0], opt.get("lab_off")))
    for f in M.FIXED:
        D.fixed_out(v, f[1], f[2], f[3], col=HVC if not faint else (0.78, 0.68, 0.88), lab=f[0] if labels else None, lab_off=FIX_LAB.get(f[0]))
    for f in M.FIXED_FREE:
        x, y = f[1], f[2]
        v.rect(x - 0.06, y - 0.06, x + 0.06, y + 0.06, fill=HVC if not faint else (0.78, 0.68, 0.88), stroke=(1, 1, 1), lw=0.8)


SOCK_LAB = {"Π55": (0.0, -0.30), "Π54": (0.0, 0.42), "Π51": (-0.02, 0.36), "Π52": (0.16, 0.36), "Π50": (0.0, 0.36), "Π12": (0.42, 0.06), "Π11": (0.42, -0.02),
            "Π13": (0.0, -0.36), "Π14": (-0.02, -0.34), "Π08": (-0.36, -0.20), "Π60": (0.02, 0.38), "Π44": (-0.44, 0.10), "Π63": (0.44, -0.10),
            "Π31": (-0.40, 0.0), "Π33": (-0.40, 0.0), "Π24": (0.42, 0.12), "Π62": (-0.42, -0.06), "Π04": (0.40, -0.10), "Π61": (-0.42, 0.10)}
FIX_LAB = {"ΑΘ": (0.42, -0.06), "ΚΛ": (0.42, 0.06), "ΚΜ3": (0.46, 0.0)}


def shutters(v, labels=False, faint=False):
    col = (0.72, 0.78, 0.90) if faint else SWC
    for sh in M.SHUTTERS:
        x, y, d = sh["motor"]
        nx, ny = D.VEC[d]
        mx, my = x + nx * 0.02, y + ny * 0.02
        D.wall_dev(v, x, y, d, "Μ", col=col, r=0.06, lab=None)


def data(v, labels=False, faint=False):
    col = (0.55, 0.80, 0.74) if faint else DAT
    c_ = M.DATA_CAB
    D.cabinet(v, c_, col=col, lab="ΚΑ" if labels else None, lab_off=(0.0, -0.36))
    for d in M.DATA:
        D.data_out(v, d[1], d[2], d[3], n=d[4], col=col, lab=d[0] if labels else None, lab_off=DATA_LAB.get(d[0]))
    for t in M.TV:
        D.data_out(v, t[1], t[2], t[3], col=col, kind="tv", lab=t[0] if labels else None, lab_off=DATA_LAB.get(t[0]))
    for d in M.WALL_DEV:
        cc = {"data": col, "alarm": (0.45, 0.30, 0.10) if not faint else (0.80, 0.72, 0.60), "fire": FIR if not faint else (0.92, 0.65, 0.72)}[d[6]]
        D.wall_dev(v, d[1], d[2], d[3], d[4], col=cc, lab=d[0] if labels else None, lab_off=DEV_LAB.get(d[0]))
    for m in M.MOTION:
        D.ceil_dev(v, m[1], m[2], "Κ", col=(0.45, 0.30, 0.10) if not faint else (0.80, 0.72, 0.60), r=0.085, lab=m[0] if labels else None)


DATA_LAB = {"D1": (-0.10, -0.42), "TV1": (0.16, -0.42), "D3": (-0.06, -0.40), "TV2": (0.20, -0.40), "D5": (-0.06, -0.40), "TV3": (0.22, -0.40),
            "D2": (0.06, 0.42), "D4": (0.10, 0.42), "D6": (0.46, -0.04)}
DEV_LAB = {"ΘΤ": (-0.50, -0.02), "ΠΛ": (-0.50, 0.06), "ΚΟ": (0.46, 0.06), "ΦΕ": (0.46, -0.06)}


def detectors(v, labels=False, ring=False, faint=False):
    col = (0.93, 0.62, 0.72) if faint else FIR
    for (n, k, x, y, t) in A.DETECTORS:
        common = (n == "ΑΚ6")
        D.detector(v, x, y, kind=k, col=(0.70, 0.70, 0.74) if common else col, lab=(n if labels else None), ring=(A.CRIT["det_wall"] if (ring and not common) else None))


def thermostats(v, labels=False, faint=False):
    col = (0.50, 0.74, 0.82) if faint else AUT
    for t in M.THERMOSTATS:
        D.wall_dev(v, t[1], t[2], t[3], "Θ", col=col, lab=t[0] if labels else None, lab_off=TH_LAB.get(t[0]), off=_opt(t, 7).get("off", 0.0))
    a = M.AC_CTRL
    D.wall_dev(v, a[1], a[2], a[3], "Χ", col=HVC if not faint else (0.78, 0.68, 0.88), lab=a[0] if labels else None, lab_off=(0.12, 0.44))
    D.cabinet(v, M.MANIFOLD, col=col, lab="ΣΛ+ΚΖ" if labels else None, lab_off=(-0.10, -0.38))


TH_LAB = {"Θ1": (-0.10, 0.44), "Θ2": (0.02, -0.44), "Θ3": (0.0, -0.44), "Θ4": (-0.06, 0.44), "Θ5": (0.30, -0.36)}


def ac_units(v, labels=False, faint=False):
    col = (0.78, 0.68, 0.88) if faint else HVC
    for u in A.UNITS:
        D.unit_rect(v, u["rect"], col=col, lab=u["id"] if labels else None, dashed=True)
    for u in A.SPLITS:
        D.unit_rect(v, u["rect"], col=col, lab=u["id"] if labels else None, alpha=0.35, lab_off=(0.0, -0.32) if u["id"] == "ΚΜ2" else (0.62, 0.0))
    D.unit_rect(v, M.AC_OUT, col=col, lab="ΕΜ multi-split 12 kW" if labels else None, dashed=True, alpha=0.08, size=5.0)
    D.unit_rect(v, M.HP_RECT, col=col, lab="ΑΘ 9 kW" if labels else None, dashed=True, alpha=0.08, size=5.0, lab_off=(0.40, 0.12))


def beams(v, names=False):
    for (bn, sec, x0, y0, x1, y1) in A.BEAMS:
        lp = A.BEAM_LABELS.get(bn) if names else None
        P.beam(v, (x0, y0, x1, y1), ("%s %s" % (bn, sec)) if lp else None, (lp[0], lp[1]) if lp else None, lp[2] if lp else 0)


# ================================================================ υπόμνημα (προσθήκες στο P.LEG)
def _leg():
    L = P.LEG
    L["e_panel"] = ("ΓΠ ηλεκτρικός πίνακας – χωνευτός, βάθος ≤ 7 cm, στο μάγουλο της ντουλάπας του χωλ", lambda v: D.panel(v, (0.08, -0.07, 0.34, 0.07)))
    L["e_tn"] = ("ΤΝ τεχνική ντουλάπα = ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ (modem, δίκτυο, συναγερμός)", lambda v: D.zone(v, (0.04, -0.08, 0.38, 0.08), FEED, alpha=0.08))
    L["e_sock"] = ("Ρευματοδότης σούκο 16 A, ύψος 0,30 (ή όπως ο πίνακας)", lambda v: D.socket(v, 0.21, 0.06, "N"))
    L["e_sock2"] = ("Διπλός / πολλαπλός ρευματοδότης (ένα στέλεχος ανά θέση)", lambda v: D.socket(v, 0.21, 0.06, "N", n=2))
    L["e_usb"] = ("Διπλός ρευματοδότης με φόρτιση USB-C", lambda v: D.socket(v, 0.21, 0.06, "N", n=2, kind="usb"))
    L["e_sockip"] = ("Ρευματοδότης στεγανός IP44 (λουτρό) / IP55 (εξώστης)", lambda v: D.socket(v, 0.21, 0.06, "N", kind="ip"))
    L["e_ded"] = ("Ρευματοδότης αποκλειστικής γραμμής (συσκευή)", lambda v: D.socket(v, 0.21, 0.06, "N", kind="ded"))
    L["e_fix"] = ("Μόνιμη παροχή – έξοδος καλωδίου (εστίες, πετσετοκρεμάστρα, κέντρο ζωνών)", lambda v: D.fixed_out(v, 0.21, 0.07, "N"))
    L["e_fixm"] = ("Παροχή μηχανήματος κλιματισμού / διακόπτης απομόνωσης", lambda v: D.fixed_out(v, 0.21, 0.07, "N", col=HVC))
    L["e_sw"] = ("Διακόπτης απλός – ένα στέλεχος ανά πλήκτρο, ύψος 1,10", lambda v: D.switch(v, 0.16, 0.09, "N", ("1",)))
    L["e_sw2"] = ("Αλέ-ρετούρ (σημαία και στα δύο άκρα)", lambda v: D.switch(v, 0.16, 0.09, "N", ("2",)))
    L["e_swx"] = ("Ενδιάμεσος αλέ-ρετούρ (τρίτη θέση)", lambda v: D.switch(v, 0.16, 0.09, "N", ("X",)))
    L["e_dimmer"] = ("Dimmer – ροοστάτης LED (τελεία)", lambda v: D.switch(v, 0.16, 0.09, "N", ("D",)))
    L["e_roll"] = ("Πλήκτρο ρολού ▲▼", lambda v: D.switch(v, 0.16, 0.09, "N", ("R",)))
    L["e_motor"] = ("Μ παροχή μοτέρ ρολού, ψηλά στην παραστάδα (+2,35)", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Μ", col=SWC, r=0.06))
    L["e_grp"] = ("Ομάδα αφής (γράμμα) – τα φωτιστικά που ανάβουν μαζί", lambda v: P.pill(v.p(0.21, 0)[0], v.p(0.21, 0)[1], "λ", None, LGT, "c", 5.6))
    L["e_spot"] = ("Χωνευτό spot LED 8 W σταθερό, βαθιά χωνευτό (χωρίς θάμβωση)", lambda v: D.spot(v, 0.21, 0))
    L["e_spot44"] = ("Χωνευτό spot IP44 (λουτρά)", lambda v: D.spot(v, 0.21, 0, "s44"))
    L["e_spot65"] = ("Χωνευτό spot IP65 (πάνω από το ντους)", lambda v: D.spot(v, 0.21, 0, "s65"))
    L["e_pend"] = ("Κρεμαστό τραπεζαρίας (παροχή οροφής)", lambda v: D.pendant(v, 0.21, 0, r=0.085))
    L["e_track"] = ("Ράγα φωτισμού Ρ1 μαγνητική 48 V, χωνευτή, 2,40 m – πάνω από τον καναπέ", lambda v: D.track(v, (0.03, 0), (0.40, 0), heads=3))
    L["e_led"] = ("Γραμμικό LED: κεφαλάρι Υπν.1 · κάτω από τα ντουλάπια κουζίνας (τα μόνα κρυφά)", lambda v: D.led_line(v, (0.03, 0), (0.40, 0)))
    L["e_ap"] = ("Απλίκα ανάγνωσης κομοδίνου, +1,15", lambda v: D.wall_light(v, 0.21, 0.06, "N"))
    L["e_mir"] = ("Παροχή φωτιζόμενου καθρέπτη, +1,90", lambda v: D.wall_light(v, 0.21, 0.06, "N", kind="mir"))
    L["e_ext"] = ("Στεγανό φωτιστικό τοίχου εξώστη IP65, +2,10", lambda v: D.wall_light(v, 0.21, 0.06, "N", kind="ext"))
    L["e_emerg"] = ("Α φωτιστικό ασφαλείας αυτόνομο 1 h (πάνω από την πόρτα εισόδου)", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Α", col=(0.15, 0.55, 0.25)))
    L["e_strip"] = ("Λωρίδα εισόδου με την καναλάτη ΚΜ1 (οροφή +2,48) – ανόψεις R23", lambda v: D.zone(v, (0.04, -0.08, 0.38, 0.08), LGT, alpha=0.08))
    L["e_data"] = ("Λήψη δικτύου RJ45 Cat 6A", lambda v: D.data_out(v, 0.21, 0.07, "N"))
    L["e_data2"] = ("Διπλή λήψη RJ45 (γραμμή)", lambda v: D.data_out(v, 0.21, 0.07, "N", n=2))
    L["e_tv"] = ("Λήψη TV / δορυφορική (ομοαξονικό)", lambda v: D.data_out(v, 0.21, 0.07, "N", kind="tv"))
    L["e_cab"] = ("ΚΑ κέντρο ασθενών μέσα στην ΤΝ: modem – router, switch, διανομή TV", lambda v: D.cabinet(v, (0.06, -0.07, 0.36, 0.07)))
    L["e_wdev"] = ("ΘΤ θυροτηλεόραση · Κ μπουτόν κουδουνιού", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "ΘΤ", col=DAT))
    L["e_alarm"] = ("Συναγερμός (προεγκατάσταση): Π πληκτρολόγιο · Κ ανιχνευτής κίνησης · ΠΣ πίνακας", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Π", col=(0.45, 0.30, 0.10)))
    L["e_contact"] = ("Μαγνητική επαφή κουφώματος / πόρτας εισόδου – καλώδιο 4×0,22 μαζί με του ρολού", lambda v: v.circle(0.21, 0, 0.05, fill=(0.45, 0.30, 0.10)))
    L["e_weak"] = ("Καλώδια ασθενών σε αστέρα από το κέντρο ασθενών – χωριστοί σωλήνες από τα ισχυρά", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=DAT, lw=1.2, halo=False))
    L["e_det"] = ("Ανιχνευτής καπνού φωτοηλεκτρικός (ΕΛΟΤ EN 54-7)", lambda v: D.detector(v, 0.21, 0, r=0.07))
    L["e_heat"] = ("Ανιχνευτής θερμοδιαφορικός – κουζίνα (EN 54-5)", lambda v: D.detector(v, 0.21, 0, kind="heat", r=0.07))
    L["e_detc"] = ("Ανιχνευτής / φωτιστικά κλιμακοστασίου – κοινόχρηστος πίνακας (γκρι)", lambda v: D.detector(v, 0.21, 0, col=(0.70, 0.70, 0.74), r=0.07))
    L["e_ring"] = ("Ακτίνα 0,50 m γύρω από ανιχνευτή – χωρίς τοίχο / φωτιστικό", lambda v: (C().saveState(), C().setDash([1.5, 1.5]), v.circle(0.21, 0, 0.09, stroke=FIR, lw=0.4), C().restoreState()))
    L["e_fpanel"] = ("ΠΣ πίνακας συναγερμού – πυρανίχνευσης του διαμερίσματος (στην ΤΝ)", lambda v: D.cabinet(v, (0.06, -0.07, 0.36, 0.07), col=FIR))
    L["e_floop"] = ("Βρόχος ανιχνευτών 2×1,5 πυράντοχο, στο κενό της ψευδοροφής", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FIR, lw=1.3, halo=False))
    L["e_siren"] = ("Σ σειρήνα συναγερμού μέσα στο διαμέρισμα", lambda v: D.ceil_dev(v, 0.21, 0, "Σ", col=FIR, r=0.075, fill=True))
    L["e_rep"] = ("Φ φωτεινός επαναλήπτης στο πλατύσκαλο", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Φ", col=FIR))
    L["e_th"] = ("Θ θερμοστάτης χώρου, +1,50", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Θ", col=AUT))
    L["e_man"] = ("ΣΛ συλλέκτης ενδοδαπέδιας 7 κυκλωμάτων + ΚΖ κέντρο ζωνών (ντουλάπα χωλ, κατά Θ03)", lambda v: D.cabinet(v, (0.06, -0.07, 0.36, 0.07), col=AUT))
    L["e_loop"] = ("Κύκλωμα ενδοδαπέδιας Κ1–Κ7 και ο θερμοστάτης που το ελέγχει (χρώμα = ζώνη)", lambda v: P.pill(v.p(0.21, 0)[0], v.p(0.21, 0)[1], "Κ6", "Θ2", (0.20, 0.55, 0.85), "c", 5.4))
    L["e_bus"] = ("Δίαυλος θερμοστάτη 2×2×0,8 σε αστέρα προς το ΚΖ", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=AUT, lw=0.9, dash=[2.2, 1.4], halo=False))
    L["e_fsens"] = ("Αισθητήριο θερμοκρασίας δαπέδου (λουτρά)", lambda v: v.circle(0.21, 0, 0.045, fill=AUT))
    L["e_ctrl"] = ("Χ ενσύρματο χειριστήριο καναλάτης ΚΜ1 / καλώδια εντολών μηχανημάτων", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Χ", col=HVC))
    L["e_unit"] = ("Μονάδα κλιματισμού / αντλία θερμότητας (θέσεις: ανόψεις R23, εξωτερικές ενδεικτικά)", lambda v: D.unit_rect(v, (0.04, -0.07, 0.38, 0.07), dashed=True))
    L["e_feed"] = ("Κεντρική παροχή 5×10 mm² από το shaft", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FEED, lw=2.6, halo=False))
    L["e_trunk"] = ("Κορμός κυκλωμάτων στο κενό της ψευδοροφής", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=PWR, lw=2.2, halo=False))
    L["e_hvacr"] = ("Παροχές μηχανημάτων κλιματισμού στο κενό της ψευδοροφής", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=HVC, lw=2.0, halo=False))
    L["e_wallrun"] = ("Μέσα σε τοίχο / έπιπλο, χαμηλά (κάτω από δοκό)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=WALLC, lw=1.5, dash=[2.6, 1.6], halo=False))
    L["e_floor"] = ("Σπιράλ πάνω στην πλάκα, πριν από το γέμισμα δαπέδου – μόνο 3 σημεία", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FLOORC, lw=1.9, dash=[0.9, 1.7], halo=False))
    L["e_refr"] = ("Ψυκτικά ΚΜ1 / split στο κενό της ψευδοροφής (ανόψεις R23)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.80, 0.10, 0.50), lw=0.9, halo=False))
    L["e_refrf"] = ("Ψυκτικά ΚΜ1 στο γέμισμα δαπέδου (ανόψεις R23)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.80, 0.10, 0.50), lw=1.3, dash=[1.3, 1.5], halo=False))
    L["e_cond"] = ("Συμπυκνώματα ΚΜ1 (αποχετεύσεις R28)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.86, 0.50, 0.02), lw=1.3, dash=[1.3, 1.5], halo=False))

    L["e_spotadj"] = ("Χωνευτό spot LED 8 W ΡΥΘΜΙΖΟΜΕΝΟ ±30° – σκοπεύει κουρτίνα / ντουλάπα", lambda v: D.spot(v, 0.21, 0, "adj"))
    L["e_pass"] = ("Π πέρασμα καλωδίων κάτω από δοκό, μέσα σε τοίχο (μετά το μπετό)", lambda v: D.pass_zone(v, (0.06, -0.08, 0.36, 0.08)))
    L["e_chan"] = ("Κανάλι 3 cm στον βόρειο τοίχο του καθιστικού (ο τοίχος +5,5 cm)", lambda v: D.channel(v, (0.04, -0.035, 0.38, 0.035)))
    L["e_out"] = ("Προς το shaft: φόρτιση οχήματος · boiler δώματος · αποθήκη", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FEED, lw=1.3, dash=[3, 1.5], halo=False))
    L["e_dim"] = ("Απόσταση (m) από τη γωνία του χώρου ή την κάσα της πόρτας – στον άξονα του κουτιού", lambda v: D.dim_chain(v, (0.05, 0), (0.37, 0), "0,45"))


_leg()
