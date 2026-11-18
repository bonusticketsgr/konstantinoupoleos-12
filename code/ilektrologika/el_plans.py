"""Φύλλα κατόψεων της ηλεκτρολογικής μελέτης (A3, 1:50): ΗΛ-01 γενική · ΗΛ-02 διακόπτες · ΗΛ-03 ρευματοδότες · ΗΛ-04 φωτισμός ·
ΗΛ-05 οδεύσεις · ΗΛ-06 κλιματισμός · ΗΛ-07 data / ασθενή · ΗΛ-08 πυρανίχνευση · ΗΛ-09 θερμοστάτες / αυτοματισμοί.
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


def lights(v, labels=False, groups=False, faint=False, track=True):
    col = (0.93, 0.74, 0.42) if faint else LGT
    for (n, k, x, y, g) in A.SPOTS:
        c_ = (0.70, 0.70, 0.74) if g == "ΚΧ" else col
        D.spot(v, x, y, k, col=c_, lab=n if (labels and g != "ΚΧ") else None)
    for (n, x, y, g, t) in A.PENDANTS:
        if n == "ΚΡΕΜ0" and track:
            tr = M.TRACK
            D.track(v, tr["a"], tr["b"], heads=tr["heads"], col=col, lab=(tr["id"] + " ράγα 2,40 (ή κρεμαστό)") if labels else None)
        else:
            D.pendant(v, x, y, col=col, lab=n if labels else None)
    for (n, a, b, g, t) in A.LED:
        D.led_line(v, a, b, col=col, lab=(n if (labels and t) else None))
    for l in M.WALL_LIGHTS:
        D.wall_light(v, l[1], l[2], l[3], col=col, kind=l[4], lab=l[0] if labels else None)
    for e in M.EMERGENCY:
        D.wall_dev(v, e[1], e[2], e[3], "Α", col=(0.15, 0.55, 0.25) if not faint else (0.6, 0.8, 0.65), lab=e[0] if labels else None)
    if groups:
        for g, x, y in GROUP_TAGS:
            X, Y = v.p(x, y)
            P.pill(X, Y, g, None, LGT, "c", 5.6)


GROUP_TAGS = [("α", 4.15, 7.12), ("β", 8.50, 5.70), ("γ", 7.98, 7.25), ("ε", 11.85, 8.86), ("ζ", 2.75, 1.85), ("η", 4.20, 4.10), ("θ", 4.38, 0.36),
              ("κ", 7.83, 2.45), ("λ", 5.45, 8.12), ("μ", 6.05, 1.25), ("ν", 2.05, 4.42), ("ε2", 12.75, 8.22), ("ζ1", 1.62, 0.48), ("ζ2", 3.68, 0.48),
              ("κ1", 6.82, 1.64), ("μ2", 5.36, 2.84), ("ν2", 2.435, 4.80), ("ξ1", 5.60, 9.90), ("ξ2", 0.42, 3.08), ("ξ3", 10.10, 2.76)]


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
    D.cabinet(v, c_, col=col, lab="ΚΔ" if labels else None, lab_off=(0.0, -0.36))
    for d in M.DATA:
        D.data_out(v, d[1], d[2], d[3], n=d[4], col=col, lab=d[0] if labels else None, lab_off=DATA_LAB.get(d[0]))
    for t in M.TV:
        D.data_out(v, t[1], t[2], t[3], col=col, kind="tv", lab=t[0] if labels else None, lab_off=DATA_LAB.get(t[0]))
    for a in M.AP:
        D.ceil_dev(v, a[1], a[2], "AP", col=col, lab=a[0] if labels else None)
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


def crossings(v, labels=True):
    for c in M.CROSSINGS:
        n = c["n25"] + c["n32"] + c["n40"]
        D.crossing(v, c["rect"], col=SLABC if c["kind"] == "pwr" else DAT, lab=c["id"] if labels else None, lab_off=c["lab_off"], anchor="c",
                   n=min(n, 9), vertical=(c["axis"] == "NS"))


# ================================================================ ΗΛ-01 ΓΕΝΙΚΗ ΚΑΤΟΨΗ
def sheet_01(no="ΗΛ-01"):
    def fn(v):
        ac_units(v, faint=True)
        lights(v)
        detectors(v)
        thermostats(v)
        data(v)
        shutters(v)
        sockets(v)
        switches(v)
        panel(v)
    _plan(fn, "ΓΕΝΙΚΗ ΚΑΤΟΨΗ ΗΛΕΚΤΡΟΛΟΓΙΚΩΝ ΕΓΚΑΤΑΣΤΑΣΕΩΝ")
    y = P.legend(["e_panel", "e_tn", "e_sock", "e_sock2", "e_sockip", "e_ded", "e_fix", "e_sw", "e_sw2", "e_dim", "e_roll", "e_motor", "e_spot", "e_spot44", "e_pend",
                  "e_track", "e_led", "e_ap", "e_mir", "e_ext", "e_emerg", "e_data", "e_tv", "e_wap", "e_cab", "e_det", "e_heat", "e_th", "e_unit", "e_cross"])
    n = CK.counts(); wl = CK.weak_lengths()
    rows = [["Σημεία ρευματοδοτών / θέσεις", "%d / %d" % (n["sock_pts"], n["sock_out"])], ["Πλαίσια διακοπτών / πλήκτρα", "%d / %d" % (n["sw_plates"], sum(n["sw"].values()))],
            ["Χωνευτά spots · ράγα · κρεμαστό · LED", "%d · 1 · 1 · %s m" % (sum(n["spots"].values()), ("%.1f" % n["led_m"]).replace(".", ","))],
            ["Λήψεις RJ45 Cat 6A (με AP, θυροτηλ.)", "%d" % wl["ports"]], ["Ανιχνευτές (καπνού + θερμοδιαφορικός)", "%d + 1" % (len(M.DETECTORS) - 1)],
            ["Θερμοστάτες / κυκλώματα ενδοδαπέδιας", "%d / 7" % len(M.THERMOSTATS)], ["Κυκλώματα πίνακα (χωρίς εφεδρικά)", "%d" % len(M.CIRCUITS)],
            ["Κουτιά σε τοίχους (σύνολο)", "%d" % n["boxes"]]]
    y = D.table(P.PX - 4, y - 2, [P.PW - 56 + 8, 56], rows, head=["ΣΥΝΟΨΗ – Β1", ""], size=5.8, aligns={1: "r"})
    _finish(no, "ΓΕΝΙΚΗ ΚΑΤΟΨΗ ΗΛΕΚΤΡΟΛΟΓΙΚΩΝ", "Πίνακας · φωτισμός · διακόπτες · ρευματοδότες · ασθενή · πυρανίχνευση")


# ================================================================ ΗΛ-02 ΔΙΑΚΟΠΤΕΣ
KIND_TXT = {"1": "απλός", "2": "αλέ-ρετούρ", "X": "ενδιάμεσος", "D": "dimmer", "R": "ρολό ▲▼"}


def sheet_02(no="ΗΛ-02"):
    def fn(v):
        lights(v, faint=True, groups=True)
        shutters(v, faint=True)
        switches(v, labels=True)
        panel(v, lab=False)
    _plan(fn, "ΘΕΣΕΙΣ ΔΙΑΚΟΠΤΩΝ – ΧΕΙΡΙΣΜΟΙ ΦΩΤΙΣΜΟΥ ΚΑΙ ΡΟΛΩΝ")
    y = P.legend(["e_sw", "e_sw2", "e_swx", "e_dim", "e_roll", "e_grp", "e_motor"])
    rows = []
    for s in M.SWITCHES:
        opt = _opt(s, 7)
        fn_ = " · ".join("%s %s" % (KIND_TXT[k], g) for k, g in s[4])
        rows.append([s[0], s[6], fn_, ("%.2f" % opt.get("h", M.H_SW)).replace(".", ",")])
    y = D.table(P.PX - 4, y - 2, [22, 78, P.PW - 22 - 78 - 24 + 8, 24], rows, head=["", "ΘΕΣΗ", "ΠΛΗΚΤΡΑ → ΟΜΑΔΑ", "ΥΨΟΣ"], size=5.2, bold_first=True, aligns={3: "r"})
    rows = [[g, d["name"], d["c"], "ναι" if d["dim"] else "—"] for g, d in M.GROUPS.items()]
    D.table(P.PX - 4, y - 6, [20, P.PW - 20 - 24 - 26 + 8, 24, 26], rows, head=["ΟΜ.", "ΦΩΤΙΣΤΙΚΑ", "ΚΥΚΛ.", "DIM"], size=5.0, bold_first=True, lead=6.2, pad=2.2)
    _finish(no, "ΚΑΤΟΨΗ ΘΕΣΕΩΝ ΔΙΑΚΟΠΤΩΝ", "Πλαίσια Δ1–Δ16 · αλέ-ρετούρ · dimmers · πλήκτρα ρολών · ύψος 1,10")


# ================================================================ ΗΛ-03 ΡΕΥΜΑΤΟΔΟΤΕΣ
def sheet_03(no="ΗΛ-03"):
    def fn(v):
        ac_units(v, faint=True)
        shutters(v, faint=True)
        sockets(v, labels=True)
        panel(v, lab=False)
    _plan(fn, "ΘΕΣΕΙΣ ΡΕΥΜΑΤΟΔΟΤΩΝ ΚΑΙ ΜΟΝΙΜΩΝ ΠΑΡΟΧΩΝ")
    y = P.legend(["e_sock", "e_sock2", "e_usb", "e_sockip", "e_ded", "e_fix", "e_fixm"])
    rows = []
    for s in M.SOCKETS:
        opt = _opt(s, 10)
        rows.append([s[0][1:], ("%.2f" % s[6]).replace(".", ","), s[7], ("%d× " % s[4] if s[4] > 1 else "") + s[9]])
    for f in M.FIXED:
        rows.append([f[0], ("%.2f" % f[4]).replace(".", ","), f[5], f[7]])
    for f in M.FIXED_FREE:
        rows.append([f[0], "οροφή", f[3], f[4]])
    D.table(P.PX - 4, y - 2, [20, 24, 20, P.PW - 64 + 8], rows, head=["Π", "ΥΨΟΣ", "ΚΥΚΛ.", "ΘΕΣΗ – ΧΡΗΣΗ"], size=5.3, lead=6.5, pad=1.75, bold_first=True, aligns={1: "r"})
    _finish(no, "ΚΑΤΟΨΗ ΘΕΣΕΩΝ ΡΕΥΜΑΤΟΔΟΤΩΝ", "Ρευματοδότες Π01–Π63 · αποκλειστικές γραμμές · μόνιμες παροχές")


# ================================================================ ΗΛ-04 ΦΩΤΙΣΜΟΣ
def sheet_04(no="ΗΛ-04"):
    def fn(v):
        D.zone(v, (A.STRIP_X, 5.15, A.LIN_X, 8.915), LGT, alpha=0.05, dash=(3, 2), lw=0.4)
        switches(v, faint=True)
        lights(v, labels=True, groups=True)
        panel(v, lab=False)
    _plan(fn, "ΦΩΤΙΣΜΟΣ – ΦΩΤΙΣΤΙΚΑ ΣΩΜΑΤΑ ΚΑΙ ΟΜΑΔΕΣ ΑΦΗΣ")
    y = P.legend(["e_spot", "e_spot44", "e_spot65", "e_pend", "e_track", "e_led", "e_ap", "e_mir", "e_ext", "e_emerg", "e_grp", "e_strip"])
    rows = []
    for r in CK.lighting_table():
        rows.append([r[0], ("%.1f" % r[1]).replace(".", ","), "%d" % r[4], "%d" % (round(r[3] / 10) * 10), "%d K" % r[7]])
    y = D.table(P.PX - 4, y - 2, [P.PW - 120 + 8, 28, 30, 30, 32], rows, head=["ΧΩΡΟΣ", "m²", "ΣΤΟΧΟΣ lx", "ΥΠΟΛ. lx", "ΧΡΩΜΑ"], size=5.4, aligns={1: "r", 2: "r", 3: "r", 4: "r"})
    rows = [["Καθιστικό ΚΘ1–ΚΘ7", "36° ρυθμιζόμενα ±25° προς κουρτίνες / τοίχο TV"], ["Ράγα Ρ1", "2 × 24° στο τραπεζάκι · 1 × 36° στον τοίχο του καναπέ · 1 γραμμικό διάχυτο"],
            ["Τραπεζαρία", "κρεμαστό με διάχυση προς τα κάτω, κάτω άκρο +1,55 από το δάπεδο"], ["Υπνοδωμάτια", "36–40° σταθερά, βαθιά χωνευτά (UGR < 19)"],
            ["Χωλ · είσοδος", "60°"], ["Κουζίνα", "50–60° · LED πάγκου 120° σε προφίλ με οπάλ κάλυμμα"], ["Λουτρά", "60° IP44 · IP65 πάνω από το ντους"]]
    D.table(P.PX - 4, y - 6, [70, P.PW - 70 + 8], rows, head=["ΓΩΝΙΕΣ ΔΕΣΜΗΣ", ""], size=5.2, bold_first=True)
    _finish(no, "ΚΑΤΟΨΗ ΦΩΤΙΣΜΟΥ", "Spots · ράγα · κρεμαστό · απλίκες · LED · ομάδες αφής · στάθμες")


# ================================================================ ΗΛ-05 ΟΔΕΥΣΕΙΣ
def routes(v, labels=True):
    # οριζόντιες μέσα σε τοίχο (κάτω από δοκό)
    for r in M.WALL_RUNS:
        D.route(v, r["pts"], col=WALLC, lw=1.5, dash=[2.6, 1.6], lab=r["id"] if labels else None, lsize=4.4)
    for r in M.FLOOR_RUNS:
        D.route(v, r["pts"], col=FLOORC, lw=1.9, dash=[0.9, 1.7], lab=("%s %s" % (r["id"], r["n"])) if labels else None, lsize=4.4)
    for r in M.ROUTES:
        col = HVC if r["kind"] == "hvac" else PWR
        D.route(v, r["pts"], col=col, lw=2.2 if r["n"].startswith("κορμός") else 1.5, arrows=True, lab=(r["n"] or None) if labels else None)
    D.route(v, M.FEED_ROUTE, col=FEED, lw=2.6, arrows=True, lab="ΠΑΡΟΧΗ 5×10" if labels else None, seg=3)
    for (x, y) in M.DROPS:
        D.drop(v, x, y, col=INK)


def sheet_05(no="ΗΛ-05"):
    def fn(v):
        beams(v, names=True)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)          # άνοιγμα shaft S1
        D.halo_text(v, 10.375, 2.64, "shaft Η/Μ S1", size=4.6, color=DAT)
        crossings(v)
        sockets(v, faint=True); switches(v, faint=True)
        routes(v)
        panel(v)
    _plan(fn, "ΟΔΕΥΣΕΙΣ ΚΑΛΩΔΙΩΝ ΚΑΙ ΣΩΛΗΝΩΣΕΩΝ")
    y = P.legend(["e_feed", "e_trunk", "e_hvacr", "e_wallrun", "e_floor", "e_cross", "e_crossw", "e_drop", "beam", "e_tn"])
    rows = []
    for c in M.CROSSINGS:
        parts = []
        if c["n25"]: parts.append("%d×Ø25" % c["n25"])
        if c["n32"]: parts.append("%d×Ø32" % c["n32"])
        if c["n40"]: parts.append("%d×Ø40" % c["n40"])
        rows.append([c["id"], c["beam"], " + ".join(parts), c["short"]])
    y = D.table(P.PX - 4, y - 2, [30, 24, 78, P.PW - 132 + 8], rows, head=["ΔΙΕΛ.", "ΔΟΚΟΣ", "ΣΩΛΗΝΕΣ ΣΤΗΝ ΠΛΑΚΑ", "ΑΠΟ ↔ ΠΡΟΣ"], size=5.3, bold_first=True)
    rows = [[r["id"], r["n"], ("ΝΕΑ – " if r["new"] else "") + r["short"]] for r in M.FLOOR_RUNS]
    y = D.table(P.PX - 4, y - 5, [30, 36, P.PW - 66 + 8], rows, head=["ΔΑΠΕΔΟ", "ΣΩΛΗΝΕΣ", "ΠΡΟΣ – ΠΩΣ"], size=5.3, bold_first=True)
    rows = [[r["id"], r["short"]] for r in M.WALL_RUNS]
    D.table(P.PX - 4, y - 5, [30, P.PW - 30 + 8], rows, head=["ΤΟΙΧΟΣ", "ΟΡΙΖΟΝΤΙΑ ΜΕΣΑ ΣΕ ΤΟΙΧΟ ΚΑΤΩ ΑΠΟ ΔΟΚΟ"], size=5.3, bold_first=True)
    _finish(no, "ΚΑΤΟΨΗ ΟΔΕΥΣΕΩΝ", "Παροχή από το shaft · κορμοί στα κενά · διελεύσεις δοκών · δάπεδο")


# ================================================================ ΗΛ-06 ΚΛΙΜΑΤΙΣΜΟΣ
def sheet_06(no="ΗΛ-06"):
    MAG, ORA, BL2 = (0.80, 0.10, 0.50), (0.86, 0.50, 0.02), (0.25, 0.55, 0.75)
    def fn(v):
        beams(v)
        # ψυκτικά / συμπυκνώματα από τις ανόψεις (για τον συντονισμό)
        D.route(v, A.KM1_VOID, col=MAG, lw=0.9, halo=False)
        D.route(v, A.KM1_FLOOR, col=MAG, lw=1.3, dash=A.FLOOR_DASH, halo=False)
        D.route(v, A.COND_ROUTE, col=ORA, lw=0.9, halo=False)
        D.route(v, A.COND_FLOOR, col=ORA, lw=1.3, dash=A.FLOOR_DASH, halo=False)
        for a, b in A.SPLIT_DRAW:
            D.route(v, [a, b], col=BL2, lw=0.8, halo=False)
        ac_units(v, labels=True)
        km = [r for r in M.ROUTES if r["id"] == "ΚΜ"][0]
        D.route(v, [M.P_TOP, (5.70, 4.62), (5.70, 3.72)] + km["pts"][1:], col=HVC, lw=2.0, arrows=True, lab="ΑΘ 3×6 · ΚΛ 3×6 · ΑΚ 3×1,5 · έλεγχος", seg=5)
        D.route(v, [r for r in M.WALL_RUNS if r["id"] == "Τ-ΒΑ"][0]["pts"], col=HVC, lw=1.6, dash=[2.6, 1.6])
        # κλάδοι προς εσωτερικές μονάδες
        D.route(v, [(5.70, 3.72), (3.65, 3.72), (3.65, 3.19)], col=HVC, lw=1.0, lab="ΑΚ → ΚΜ2", lsize=4.2)
        D.route(v, [(6.20, 2.60), (6.499, 2.60)], col=HVC, lw=1.0)
        D.route(v, [(6.20, 5.35), (6.60, 5.62), (8.875, 5.62), (8.875, 6.42)], col=HVC, lw=1.0, lab="ΑΚ → ΚΜ1 (ΔΠ1-Ι)", lsize=4.2, seg=1)
        D.route(v, [(8.875, 6.42), (8.875, 5.50), (7.20, 5.50), (6.94, 5.20)], col=HVC, lw=0.7, dash=[1.5, 1.5])
        for f in M.FIXED:
            D.fixed_out(v, f[1], f[2], f[3], col=HVC, lab=f[0], lab_off=FIX_LAB.get(f[0]))
        for f in M.FIXED_FREE:
            v.rect(f[1] - 0.06, f[2] - 0.06, f[1] + 0.06, f[2] + 0.06, fill=HVC, stroke=(1, 1, 1), lw=0.8)
        a = M.AC_CTRL
        D.wall_dev(v, a[1], a[2], a[3], "Χ", col=HVC, lab="Χ1", lab_off=(0.12, 0.44))
        D.drop(v, 9.30, 1.05, col=HVC)
        crossings(v, labels=False)
        panel(v)
    _plan(fn, "ΗΛΕΚΤΡΙΚΕΣ ΠΑΡΟΧΕΣ ΚΛΙΜΑΤΙΣΜΟΥ ΚΑΙ ΑΝΤΛΙΑΣ ΘΕΡΜΟΤΗΤΑΣ")
    y = P.legend(["e_unit", "e_fixm", "e_hvacr", "e_wallrun", "e_refr", "e_refrf", "e_cond", "e_ctrl", "beam"])
    cc = {c["id"]: c for c in M.CIRCUITS}
    def row(cid, what, where):
        c = cc[cid]
        return [cid, what, "%s%d %dP" % (c["curve"], c["In"], c["poles"]), c["cable"], c["grp"].replace("RCBO ", "ΔΔΡ ").replace("ΔΔΡ-", "ομάδα "), where]
    rows = [row("ΑΘ", "Αντλία θερμότητας 9 kW, 1~", "ΒΑ εξώστης, διακόπτης IP65"), row("ΚΛ", "Εξωτ. multi-split 12 kW, 1~", "ΒΑ εξώστης, διακόπτης IP65"),
            row("ΑΚ", "ΚΜ1 24k · ΚΜ2 12k · ΚΜ3 9k", "παροχή σε κάθε εσωτερική"), row("ΕΝ", "Κέντρο ζωνών · κυκλοφορητής", "ντουλάπα χωλ")]
    y = D.table(P.PX - 4, y - 2, [18, 62, 30, 24, 34, P.PW - 168 + 8], rows, head=["", "ΦΟΡΤΙΟ", "ΑΣΦ.", "mm²", "ΔΔΡ", "ΘΕΣΗ"], size=5.3, bold_first=True)
    rows = [["ΕΜ → ΚΜ1", "4×1,5 + θωρακισμένο 2×0,75, μαζί με τα ψυκτικά: πεσσός Τ1-05 → γέμισμα Υπν.2 → κανάλι Τ6Β → λωρίδα"],
            ["ΕΜ → ΚΜ2 / ΚΜ3", "4×1,5 + 2×0,75, μαζί με τα ψυκτικά: ντουλάπα Υπν.2 → κενό λουτρού → χωλ"],
            ["ΚΜ1 → Χ1", "θωρακισμένο 2×0,75 ως το χειριστήριο τοίχου (ΔΠ1-Α → Τ2-07 → Τ2-06)"],
            ["ΑΘ → ΚΖ", "7×1,0 θωρακισμένο (ζήτηση · θέρμανση / ψύξη · βλάβη) + καλώδιο χειριστηρίου, στην όδευση των παροχών"]]
    D.table(P.PX - 4, y - 5, [48, P.PW - 48 + 8], rows, head=["ΕΝΤΟΛΕΣ", "ΚΑΛΩΔΙΟ – ΟΔΕΥΣΗ"], size=5.3, bold_first=True)
    _finish(no, "ΚΑΤΟΨΗ ΠΑΡΟΧΩΝ ΚΛΙΜΑΤΙΣΜΟΥ", "Αντλία θερμότητας · multi-split · εσωτερικές · συντονισμός με ψυκτικά")


# ================================================================ ΗΛ-07 DATA – ΑΣΘΕΝΗ
WEAK_ROUTES = [
    [(5.10, 4.62), (4.50, 4.62), (4.50, 5.80), (9.375, 5.80)],               # ΔΠ1-Α → καθιστικό → τοίχος εισόδου (θυροτηλεόραση, πληκτρολόγιο)
    [(5.20, 5.80), (5.20, 6.45)], [(5.20, 6.45), (4.70, 6.95), (4.70, 7.75)],   # AP2 · ανιχνευτής κίνησης
    [(5.10, 4.62), (5.10, 3.60), (2.85, 3.60), (2.85, 3.30)],                 # κενό χωλ → AP1 → νότιος τοίχος Υπν.1
    [(2.85, 3.30), (2.85, 0.95), (2.65, 0.40), (3.94, 0.24)],                 # ΔΠ3 → κομοδίνο
    [(5.10, 3.60), (6.95, 3.60), (6.95, 1.40), (6.52, 1.40)],                 # Υπν.2 κομοδίνο
    [(6.95, 3.60), (6.95, 4.40), (6.47, 4.40)],                               # → Τ2-07 → Τ2-06 (γραφείο)
]


def sheet_07(no="ΗΛ-07"):
    def fn(v):
        crossings(v, labels=False)
        for r in WEAK_ROUTES:
            D.route(v, r, col=DAT, lw=1.2)
        D.route(v, [(6.47, 4.40), (6.47, 5.10), (8.90, 5.10)], col=DAT, lw=1.1, dash=[2.6, 1.6])
        D.route(v, [(5.10, 5.10), (5.12, 5.10)], col=DAT, lw=1.1, dash=[2.6, 1.6])
        D.route(v, [(3.82, 5.06), (3.82, 9.115)], col=FLOORC, lw=1.7, dash=[0.9, 1.7], lab="Δ-TV (δάπεδο)", lsize=4.4)
        rs = [(q[0] + 0.12, q[1]) if i < 2 else (q[0], q[1] + 0.12) for i, q in enumerate(M.FEED_ROUTE[:4])]
        D.route(v, [(10.375, 2.93), (9.945, 3.05)] + [(9.945, 5.74), (9.375, 5.74), (4.62, 5.74), (4.62, 4.62), (5.10, 4.62)], col=DAT, lw=1.9, arrows=True,
                lab="ΑΝΕΡΧΟΜΕΝΕΣ: οπτική ίνα · UTP · κεραία · θυροτηλεόραση", seg=3)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        data(v, labels=True)
        for sh in M.SHUTTERS:
            x, y, d = sh["motor"]; nx, ny = D.VEC[d]
            v.circle(x + nx * 0.06, y + ny * 0.06, 0.05, fill=(0.45, 0.30, 0.10), stroke=(1, 1, 1), lw=0.6)
        v.circle(9.40, 5.42, 0.05, fill=(0.45, 0.30, 0.10), stroke=(1, 1, 1), lw=0.6)
        D.cabinet(v, M.ALARM_PANEL, col=(0.45, 0.30, 0.10), lab="ΠΣ", lab_off=(-0.36, -0.10))
        panel(v, lab=False)
    _plan(fn, "ΔΙΚΤΥΟ ΔΕΔΟΜΕΝΩΝ ΚΑΙ ΑΣΘΕΝΗ ΡΕΥΜΑΤΑ")
    y = P.legend(["e_cab", "e_data", "e_data2", "e_tv", "e_wap", "e_wdev", "e_alarm", "e_contact", "e_weak", "e_wallrun", "e_floor", "e_crossw"])
    rows = [[d[0], "%d × RJ45" % d[4], ("%.2f" % d[5]).replace(".", ","), d[7]] for d in M.DATA]
    rows += [[t[0], "ομοαξονικό", ("%.2f" % t[4]).replace(".", ","), "TV / δορυφορική"] for t in M.TV]
    rows += [[a[0], "RJ45 PoE", "οροφή", a[3]] for a in M.AP]
    rows += [[d[0], {"data": "RJ45 PoE", "alarm": "δίαυλος", "fire": "2×1,5"}[d[6]] if d[0] != "ΚΟ" else "2×0,8", ("%.2f" % d[5]).replace(".", ","), d[7]] for d in M.WALL_DEV]
    rows += [[m[0], "6×0,22", "οροφή", m[3]] for m in M.MOTION]
    y = D.table(P.PX - 4, y - 2, [22, 42, 24, P.PW - 88 + 8], rows, head=["", "ΛΗΨΗ", "ΥΨΟΣ", "ΘΕΣΗ – ΧΡΗΣΗ"], size=5.3, bold_first=True, aligns={2: "r"})
    _finish(no, "ΚΑΤΟΨΗ DATA – ΑΣΘΕΝΩΝ ΡΕΥΜΑΤΩΝ", "Ερμάριο ΚΔ · Cat 6A σε αστέρα · AP · TV · θυροτηλεόραση · συναγερμός")


# ================================================================ ΗΛ-08 ΠΥΡΑΝΙΧΝΕΥΣΗ
def sheet_08(no="ΗΛ-08"):
    det = {d[0]: (d[2], d[3]) for d in A.DETECTORS}
    def fn(v):
        crossings(v, labels=False)
        lights(v, faint=True)
        loop = [(4.90, 4.62), (5.21, 4.62), det["ΑΚ4"], (2.70, 3.85), det["ΑΚ2"]]
        D.route(v, loop, col=FIR, lw=1.3, arrows=True)
        D.route(v, [det["ΑΚ4"], (7.83, 3.85)], col=FIR, lw=1.3, arrows=True)
        D.route(v, [(4.90, 4.62), (4.62, 4.62), (4.62, 5.95), det["ΑΚ1"]], col=FIR, lw=1.3, arrows=True)
        D.route(v, [det["ΑΚ1"], (7.00, 8.50), (9.20, 8.50), (9.90, 8.50), (10.855, 8.50), det["ΑΘ5"]], col=FIR, lw=1.3, arrows=True)
        fe = [d for d in M.WALL_DEV if d[0] == "ΦΕ"][0]
        D.route(v, [(4.62, 5.74), (9.375, 5.74), (9.375, fe[2]), (fe[1], fe[2])], col=FIR, lw=0.9, dash=[2, 1.5])
        D.cabinet(v, M.ALARM_PANEL, col=FIR, lab="ΠΣ", lab_off=(-0.36, -0.10))
        detectors(v, labels=True, ring=True)
        for d in M.WALL_DEV:
            if d[6] in ("fire", "alarm"):
                D.wall_dev(v, d[1], d[2], d[3], d[4], col=FIR if d[6] == "fire" else (0.45, 0.30, 0.10), lab=d[0], lab_off=DEV_LAB.get(d[0]))
        for e in M.EMERGENCY:
            D.wall_dev(v, e[1], e[2], e[3], "Α", col=(0.15, 0.55, 0.25), lab=e[0], lab_off=(-0.42, -0.02))
        D.ceil_dev(v, 5.21, 4.36, "Σ", col=FIR, r=0.085, lab="σειρήνα", lab_off=(0.0, -0.20), fill=True)
        panel(v, lab=False)
    _plan(fn, "ΠΥΡΑΝΙΧΝΕΥΣΗ – ΦΩΤΙΣΜΟΣ ΑΣΦΑΛΕΙΑΣ")
    y = P.legend(["e_det", "e_heat", "e_ring", "e_fpanel", "e_floop", "e_siren", "e_rep", "e_emerg", "e_detc"])
    rows = [[d[0], "καπνού φωτοηλεκτρικός" if d[1] == "smoke" else "θερμοδιαφορικός", ("%.2f / %.2f" % (d[2], d[3])).replace(".", ","), d[4].split(" (")[0].split(" – ")[0]] for d in M.DETECTORS]
    y = D.table(P.PX - 4, y - 2, [22, 66, 44, P.PW - 132 + 8], rows, head=["", "ΤΥΠΟΣ", "ΘΕΣΗ x / y", "ΧΩΡΟΣ"], size=5.0, bold_first=True)
    rows = [["Κανονισμός", "Π.Δ. 41/2018, άρθρο 1 «Κατοικία» · εγκεκριμένη μελέτη ενεργητικής πυροπροστασίας ΕΠ04: αυτόματη πυρανίχνευση σε όλους τους χώρους πλην WC"],
            ["Σύστημα", "συμβατικό (ζωνών), ΕΛΟΤ EN 54 · πίνακας συναγερμού – πυρανίχνευσης ΠΣ του διαμερίσματος μέσα στην ΤΝ · 1 ζώνη · συσσωρευτής ≥ 24 h ηρεμίας + 30 min συναγερμού"],
            ["Καλώδιο", "βρόχος 2×1,5 mm² πυράντοχο (FE180 / E30), κόκκινο, σε δικό του σωλήνα Ø16 – όχι μαζί με ισχυρά"],
            ["Αναγγελία", "σειρήνα μέσα στο διαμέρισμα (οροφή χωλ) · φωτεινός επαναλήπτης ΦΕ στο πλατύσκαλο · φαροσειρήνα ορόφου από τον κοινόχρηστο πίνακα"],
            ["Λουτρά", "χωρίς ανιχνευτή (υδρατμοί – ΕΠ04 «πλην WC»)"],
            ["Αποστάσεις", "≥ 0,50 m από τοίχους / δοκούς / φωτιστικά · ≥ 1,00 m από στόμια και split (ανόψεις R23)"]]
    D.table(P.PX - 4, y - 5, [44, P.PW - 44 + 8], rows, head=["ΑΠΑΙΤΗΣΕΙΣ", ""], size=5.0, bold_first=True)
    _finish(no, "ΚΑΤΟΨΗ ΠΥΡΑΝΙΧΝΕΥΣΗΣ", "Ανιχνευτές · βρόχος · πίνακας ΠΣ · σειρήνα · φωτισμός ασφαλείας")


# ================================================================ ΗΛ-09 ΘΕΡΜΟΣΤΑΤΕΣ – ΑΥΤΟΜΑΤΙΣΜΟΙ
LOOPS = [("Κ1", "Καθιστικό", (1.705, 5.15, 6.20, 9.115), "Θ1"), ("Κ2", "Τραπεζαρία", (6.20, 5.15, 9.325, 9.115), "Θ1"), ("Κ3", "Κουζίνα", (9.59, 7.75, 13.76, 10.06), "Θ1"),
         ("Κ4", "Υπνοδωμάτιο 2", (6.50, 1.35, 9.395, 5.05), "Θ3"), ("Κ5", "Λουτρό", (5.05, 0.80, 6.40, 3.25), "Θ4"),
         ("Κ6", "Υπνοδωμάτιο 1", (1.135, 0.165, 4.20, 3.25), "Θ2"), ("Κ7", "Λουτρό γονέων", (0.11, 3.50, 3.15, 5.05), "Θ5")]
ZCOL = {"Θ1": (0.95, 0.55, 0.15), "Θ2": (0.20, 0.55, 0.85), "Θ3": (0.25, 0.65, 0.35), "Θ4": (0.65, 0.35, 0.75), "Θ5": (0.85, 0.30, 0.45)}
LOOP_TAG = {"Κ1": (3.20, 7.80), "Κ2": (7.60, 8.05), "Κ3": (11.30, 9.05), "Κ4": (8.30, 3.40), "Κ5": (5.90, 1.90), "Κ6": (2.40, 2.40), "Κ7": (1.60, 4.30)}


def sheet_09(no="ΗΛ-09"):
    def fn(v):
        for k, name, r, th in LOOPS:
            D.zone(v, r, ZCOL[th], alpha=0.13, dash=(2.5, 1.5), lw=0.5)
            X, Y = v.p(*LOOP_TAG[k]); P.pill(X, Y, k, th, ZCOL[th], "c", 6.2)
        kz = ((M.MANIFOLD[0] + M.MANIFOLD[2]) / 2, 4.62)
        tp = {t[0]: (t[1], t[2]) for t in M.THERMOSTATS}
        paths = {"Θ1": [kz, (6.20, 4.62), (tp["Θ1"][0], 4.62), (tp["Θ1"][0], 5.10)], "Θ2": [kz, (4.32, 3.72), (tp["Θ2"][0], 3.72), (tp["Θ2"][0], 3.30)],
                 "Θ3": [kz, (6.20, 4.62), (6.90, 4.62), (tp["Θ3"][0], 4.70), (tp["Θ3"][0], 5.02)],
                 "Θ4": [kz, (4.32, 3.72), (tp["Θ4"][0], 3.72), (tp["Θ4"][0], 3.40)], "Θ5": [kz, (4.32, 3.72), (3.55, 3.72), (3.23, 3.40), (1.95, 3.375), (tp["Θ5"][0], 3.375)]}
        for th, pth in paths.items():
            D.route(v, pth, col=AUT, lw=0.9, dash=[2.2, 1.4])
        # αισθητήρια δαπέδου λουτρών
        D.route(v, [(5.26, 3.35), (5.40, 3.10), (5.80, 2.70)], col=AUT, lw=0.7, dash=[0.8, 1.2]); v.circle(5.80, 2.70, 0.045, fill=AUT)
        D.route(v, [(tp["Θ5"][0], 3.30), (1.125, 3.60), (1.60, 4.10)], col=AUT, lw=0.7, dash=[0.8, 1.2]); v.circle(1.60, 4.10, 0.045, fill=AUT)
        ac_units(v, faint=True)
        D.unit_rect(v, M.HP_RECT, col=HVC, lab="ΑΘ 9 kW", dashed=True, alpha=0.10, size=5.4, lab_off=(0.40, 0.12))
        km = [r for r in M.ROUTES if r["id"] == "ΚΜ"][0]
        D.route(v, [kz, (5.70, 4.62), (5.70, 3.72)] + km["pts"][1:] + [(9.80, 1.05), (10.20, 1.92)], col=HVC, lw=1.1, dash=[3, 1.5], lab="ΚΖ ↔ ΑΘ: έλεγχος", seg=6, lsize=4.4)
        thermostats(v, labels=True)
        D.wall_dev(v, 5.349, 4.86, "W", "ΧΑ", col=HVC, r=0.07, lab="χειρ. ΑΘ", lab_off=(-0.10, -0.30))
        panel(v)
    _plan(fn, "ΘΕΡΜΟΣΤΑΤΕΣ ΧΩΡΩΝ ΚΑΙ ΑΥΤΟΜΑΤΙΣΜΟΣ ΕΝΔΟΔΑΠΕΔΙΑΣ")
    y = P.legend(["e_th", "e_man", "e_loop", "e_bus", "e_fsens", "e_ctrl", "e_unit"])
    rows = [[t[0], t[6], " + ".join(t[5]), "%d" % len(t[5])] for t in M.THERMOSTATS]
    y = D.table(P.PX - 4, y - 2, [20, P.PW - 20 - 50 - 26 + 8, 50, 26], rows, head=["", "ΖΩΝΗ", "ΚΥΚΛΩΜΑΤΑ", "ΚΙΝ."], size=5.0, bold_first=True, aligns={3: "r"})
    rows = [["ΚΖ", "Κέντρο ζωνών 8 καναλιών θέρμανσης / ψύξης, 230 V τροφοδοσία (κύκλωμα ΕΝ), έξοδοι κινητήρων 24 V, λογική κυκλοφορητή και «ζήτησης» προς την αντλία θερμότητας"],
            ["Θερμοστάτες", "5 ψηφιακοί τοίχου +1,50, δίαυλος 2×2×0,8 σε ΑΣΤΕΡΑ προς το ΚΖ (σωλήνας Ø16) – κάθε θερμοστάτης ανοίγει / κλείνει τους κινητήρες της ζώνης ΤΟΥ"],
            ["Κινητήρες", "7 ηλεκτροθερμικοί (ένας ανά κύκλωμα) πάνω στον συλλέκτη επιστροφής, κανονικά κλειστοί"],
            ["Ψύξη", "είσοδος αλλαγής θέρμανση / ψύξη από την αντλία · αισθητήριο σημείου δρόσου στον συλλέκτη · στην ψύξη τα λουτρά (Κ5, Κ7) κλειστά"],
            ["Λουτρά", "θερμοστάτες Θ4 / Θ5 ΕΞΩ από την πόρτα, με αισθητήριο δαπέδου (σωλήνας Ø16 στο γέμισμα, 0,5 m μέσα στο λουτρό)"],
            ["Έξυπνο σπίτι", "το ΚΖ με θύρα δικτύου / Modbus στο ερμάριο ΚΔ – έλεγχος από κινητό χωρίς άλλη καλωδίωση"]]
    D.table(P.PX - 4, y - 5, [44, P.PW - 44 + 8], rows, head=["ΑΡΧΙΤΕΚΤΟΝΙΚΗ", ""], size=5.0, bold_first=True)
    _finish(no, "ΚΑΤΟΨΗ ΘΕΡΜΟΣΤΑΤΩΝ – ΑΥΤΟΜΑΤΙΣΜΩΝ", "5 ζώνες · 7 κυκλώματα · κέντρο ζωνών στον συλλέκτη · έλεγχος αντλίας")


# ================================================================ υπόμνημα (προσθήκες στο P.LEG)
def _leg():
    L = P.LEG
    L["e_panel"] = ("ΓΠ ηλεκτρικός πίνακας διαμερίσματος – χωνευτός στον τοίχο Τ2N-02 του χωλ", lambda v: D.panel(v, (0.08, -0.07, 0.34, 0.07)))
    L["e_tn"] = ("ΤΝ τεχνική ντουλάπα (τμήμα της ντουλάπας χωλ): πλάτη πίνακα, ερμάριο ασθενών, πίνακας συναγερμού", lambda v: D.zone(v, (0.04, -0.08, 0.38, 0.08), FEED, alpha=0.08))
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
    L["e_dim"] = ("Dimmer – ροοστάτης LED (τελεία)", lambda v: D.switch(v, 0.16, 0.09, "N", ("D",)))
    L["e_roll"] = ("Πλήκτρο ρολού ▲▼", lambda v: D.switch(v, 0.16, 0.09, "N", ("R",)))
    L["e_motor"] = ("Μ παροχή μοτέρ ρολού, ψηλά στην παραστάδα (+2,35)", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Μ", col=SWC, r=0.06))
    L["e_grp"] = ("Ομάδα αφής (γράμμα) – τα φωτιστικά που ανάβουν μαζί", lambda v: P.pill(v.p(0.21, 0)[0], v.p(0.21, 0)[1], "λ", None, LGT, "c", 5.6))
    L["e_spot"] = ("Χωνευτό spot LED 8 W, CRI ≥ 90, UGR < 19", lambda v: D.spot(v, 0.21, 0))
    L["e_spot44"] = ("Χωνευτό spot IP44 (λουτρά)", lambda v: D.spot(v, 0.21, 0, "s44"))
    L["e_spot65"] = ("Χωνευτό spot IP65 (πάνω από το ντους)", lambda v: D.spot(v, 0.21, 0, "s65"))
    L["e_pend"] = ("Παροχή οροφής κρεμαστού (τραπεζαρία)", lambda v: D.pendant(v, 0.21, 0, r=0.085))
    L["e_track"] = ("Ράγα φωτισμού Ρ1 μαγνητική 48 V, χωνευτή – ΠΡΟΤΑΣΗ στη θέση της παροχής ΚΡΕΜ0", lambda v: D.track(v, (0.03, 0), (0.40, 0), heads=3))
    L["e_led"] = ("Γραμμικό LED: κεφαλάρι Υπν.1 · κάτω από τα ντουλάπια κουζίνας (μόνα κρυφά)", lambda v: D.led_line(v, (0.03, 0), (0.40, 0)))
    L["e_ap"] = ("Απλίκα ανάγνωσης κομοδίνου, +1,15", lambda v: D.wall_light(v, 0.21, 0.06, "N"))
    L["e_mir"] = ("Γραμμικό φωτιστικό καθρέπτη, +2,00", lambda v: D.wall_light(v, 0.21, 0.06, "N", kind="mir"))
    L["e_ext"] = ("Στεγανό φωτιστικό τοίχου εξώστη IP65, +2,10", lambda v: D.wall_light(v, 0.21, 0.06, "N", kind="ext"))
    L["e_emerg"] = ("Α φωτιστικό ασφαλείας αυτόνομο 1 h (πάνω από την πόρτα εισόδου)", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Α", col=(0.15, 0.55, 0.25)))
    L["e_strip"] = ("Λωρίδα εισόδου με την καναλάτη ΚΜ1 (οροφή +2,48) – ανόψεις R23", lambda v: D.zone(v, (0.04, -0.08, 0.38, 0.08), LGT, alpha=0.08))
    L["e_data"] = ("Λήψη δικτύου RJ45 Cat 6A", lambda v: D.data_out(v, 0.21, 0.07, "N"))
    L["e_data2"] = ("Διπλή λήψη RJ45 (γραμμή)", lambda v: D.data_out(v, 0.21, 0.07, "N", n=2))
    L["e_tv"] = ("Λήψη TV / δορυφορική (ομοαξονικό)", lambda v: D.data_out(v, 0.21, 0.07, "N", kind="tv"))
    L["e_wap"] = ("AP λήψη οροφής για σημείο ασύρματης πρόσβασης (PoE) – μόνο καλώδιο", lambda v: D.ceil_dev(v, 0.21, 0, "AP", r=0.085))
    L["e_cab"] = ("ΚΔ ερμάριο ασθενών μέσα στην ΤΝ (οπτική ίνα, router, switch PoE, διανομή TV)", lambda v: D.cabinet(v, (0.06, -0.07, 0.36, 0.07)))
    L["e_wdev"] = ("ΘΤ θυροτηλεόραση · Κ μπουτόν κουδουνιού", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "ΘΤ", col=DAT))
    L["e_alarm"] = ("Συναγερμός (προεγκατάσταση): Π πληκτρολόγιο · Κ ανιχνευτής κίνησης · ΠΣ πίνακας", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Π", col=(0.45, 0.30, 0.10)))
    L["e_contact"] = ("Μαγνητική επαφή κουφώματος / πόρτας εισόδου – καλώδιο 4×0,22 μαζί με του ρολού", lambda v: v.circle(0.21, 0, 0.05, fill=(0.45, 0.30, 0.10)))
    L["e_weak"] = ("Όδευση ασθενών στο κενό της ψευδοροφής – χωριστοί σωλήνες, ≥ 10 cm από τα ισχυρά", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=DAT, lw=1.2, halo=False))
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
    L["e_loop"] = ("Κύκλωμα ενδοδαπέδιας Κ1–Κ7 και ο θερμοστάτης που το ελέγχει (χρώμα = ζώνη)", lambda v: P.pill(v.p(0.21, 0)[0], v.p(0.21, 0)[1], "Κ6", "Θ2", ZCOL["Θ2"], "c", 5.4))
    L["e_bus"] = ("Δίαυλος θερμοστάτη 2×2×0,8 σε αστέρα προς το ΚΖ", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=AUT, lw=0.9, dash=[2.2, 1.4], halo=False))
    L["e_fsens"] = ("Αισθητήριο θερμοκρασίας δαπέδου (λουτρά)", lambda v: v.circle(0.21, 0, 0.045, fill=AUT))
    L["e_ctrl"] = ("Χ ενσύρματο χειριστήριο καναλάτης ΚΜ1 / καλώδια εντολών μηχανημάτων", lambda v: D.wall_dev(v, 0.21, 0.07, "N", "Χ", col=HVC))
    L["e_unit"] = ("Μονάδα κλιματισμού / αντλία θερμότητας (θέσεις: ανόψεις R23, εξωτερικές ενδεικτικά)", lambda v: D.unit_rect(v, (0.04, -0.07, 0.38, 0.07), dashed=True))
    L["e_cross"] = ("ΔΠ διέλευση δοκού: σπιράλ εγκιβωτισμένα στην πλάκα – ΠΡΙΝ τη σκυροδέτηση", lambda v: D.crossing(v, (0.06, -0.08, 0.36, 0.08), n=5))
    L["e_crossw"] = ("ΔΠ διέλευση δοκού για ασθενή (χωριστή δέσμη)", lambda v: D.crossing(v, (0.06, -0.08, 0.36, 0.08), col=DAT, n=5))
    L["e_feed"] = ("Κεντρική παροχή 5×10 mm² από το shaft (ψευδοδοκός κλιμακοστασίου → τοίχος Τ6Β)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FEED, lw=2.6, halo=False))
    L["e_trunk"] = ("Κορμός κυκλωμάτων στο κενό της ψευδοροφής (σπιράλ πάνω από τον σκελετό)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=PWR, lw=2.2, halo=False))
    L["e_hvacr"] = ("Παροχές μηχανημάτων κλιματισμού στο κενό της ψευδοροφής", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=HVC, lw=2.0, halo=False))
    L["e_wallrun"] = ("Οριζόντια όδευση ΜΕΣΑ σε τοίχο (τοίχος κάτω από δοκό)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=WALLC, lw=1.5, dash=[2.6, 1.6], halo=False))
    L["e_floor"] = ("Σπιράλ στο ΓΕΜΙΣΜΑ ΔΑΠΕΔΟΥ – μόνο 3 σημεία", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FLOORC, lw=1.9, dash=[0.9, 1.7], halo=False))
    L["e_drop"] = ("Κατέβασμα από το κενό μέσα σε τοίχο (κατακόρυφα πάνω από τα κουτιά)", lambda v: D.drop(v, 0.21, 0))
    L["e_refr"] = ("Ψυκτικά ΚΜ1 / split στο κενό της ψευδοροφής (ανόψεις R23)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.80, 0.10, 0.50), lw=0.9, halo=False))
    L["e_refrf"] = ("Ψυκτικά ΚΜ1 στο γέμισμα δαπέδου (ανόψεις R23)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.80, 0.10, 0.50), lw=1.3, dash=[1.3, 1.5], halo=False))
    L["e_cond"] = ("Συμπυκνώματα ΚΜ1 (αποχετεύσεις R28)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=(0.86, 0.50, 0.02), lw=1.3, dash=[1.3, 1.5], halo=False))


_leg()
