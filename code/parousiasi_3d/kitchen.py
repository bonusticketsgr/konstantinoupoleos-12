"""ΠΑΡΟΥΣΙΑΣΗ 3D – κουζίνα. Οι θέσεις (στήλες, πάγκοι, νεροχύτης, πλυντήριο πιάτων, ψυγείο, εστίες) είναι του μοντέλου (scene.json: equip / furn / kitchen)·
εδώ ορίζεται μόνο η ΜΟΡΦΗ: μέτωπα χωρίς λαβές (push-to-open), ψηλά ντουλάπια σε δρυ, λευκά ματ μέτωπα, λευκός πάγκος quartz, μπαταρία σε βουρτσισμένο νίκελ.
ΕΝΔΕΙΚΤΙΚΑ: χωρισμός μετώπων, ύψη (πάγκος 0,90 · επάνω ντουλάπια από 1,55 ως την οροφή)."""
import lib as L
from lib import mbox, tube, lbox, place, rprism, cyl

CT = 0.90            # άνω στάθμη πάγκου
CTT = 0.02           # πάχος πάγκου
PL = 0.10            # μπάζα
UB = 1.55            # κάτω μέρος επάνω ντουλαπιών (το παράθυρο του πάγκου τελειώνει στο 1,53)
TH = 0.018           # πάχος μετώπου
G = "kitchen"


def front(name, a0, a1, z0, z1, plane, face, mat, gap=0.0015):
    """Μέτωπο ντουλαπιού. face = προς τα πού κοιτά ('S' νότια, 'N' βόρεια, 'W' δυτικά). plane = η γραμμή του ντουλαπιού (εξωτερική παρειά μετώπου)."""
    if face == "S":
        return mbox(name, a0 + gap, plane - TH, a1 - gap, plane, z0 + gap, z1 - gap, mat, r=0.002, seg=2, group=G)
    if face == "N":
        return mbox(name, a0 + gap, plane, a1 - gap, plane + TH, z0 + gap, z1 - gap, mat, r=0.002, seg=2, group=G)
    if face == "W":
        return mbox(name, plane, a0 + gap, plane + TH, a1 - gap, z0 + gap, z1 - gap, mat, r=0.002, seg=2, group=G)
    raise ValueError(face)


def fronts(name, xs, zs, plane, face, mat):
    for i in range(len(xs) - 1):
        for k in range(len(zs) - 1):
            front("%s_%d_%d" % (name, i, k), xs[i], xs[i + 1], zs[k], zs[k + 1], plane, face, mat)


def oven(name, x0, x1, z0, z1, plane, M):
    """Εντοιχισμένος φούρνος (μαύρο γυαλί) στη στήλη που κοιτά νότια."""
    mbox(name, x0 + 0.004, plane - TH, x1 - 0.004, plane + 0.002, z0 + 0.004, z1 - 0.004, M["black_glass"], r=0.003, seg=2, group=G)
    zt = z1 - 0.075
    tube(name + "_h", [(x0 + 0.07, plane + 0.035, zt), (x1 - 0.07, plane + 0.035, zt)], 0.007, M["nickel"], group=G)
    for x in (x0 + 0.09, x1 - 0.09):
        tube(name + "_hs", [(x, plane, zt), (x, plane + 0.035, zt)], 0.005, M["nickel"], group=G)
    mbox(name + "_d", (x0 + x1) / 2 - 0.06, plane + 0.0015, (x0 + x1) / 2 + 0.06, plane + 0.0025, z1 - 0.045, z1 - 0.025, M["display"], group=G)


def build(D, M, ceil=2.48):
    eq = {(e[0], e[5]): e for e in D["equip"]}
    K = D["kitchen"]
    fr_x0, fr_y0, fr_x1, fr_y1 = K["fridge"]
    sk_x0, sk_y0, sk_x1, sk_y1 = K["sink"]
    dw_x0, dw_y0, dw_x1, dw_y1 = K["dishw"]
    tall = [e for e in D["equip"] if e[0] == "tall" and "ΦΟΥΡΝ" in e[5]][0]
    hob = [e for e in D["equip"] if e[0] == "hob"][0]
    fn = {f["name"]: f for f in D["furn"]}
    nb = fn["κάτω ντουλάπια – βόρειος πάγκος"]["box"]          # 11.75, 7.75, 13.759, 8.35
    eb = fn["κάτω ντουλάπια – έρκερ Α"]["box"]                 # 13.159, 8.35, 13.759, 9.15
    sb = fn["κάτω ντουλάπια – νότιος πάγκος"]["box"]           # 9.70, 9.46, 12.70, 10.06
    ub = fn["επάνω ντουλάπια – βόρειος πάγκος"]["box"]         # 11.75, 7.75, 13.759, 8.10
    UD = ub[3] - ub[1]                                          # βάθος επάνω ντουλαπιών
    white, oak, body, stone = M["front"], M["oak"]["Z"], M["carcass"], M["quartz"]
    yn, yf = nb[1], nb[3]                                       # βόρειος τοίχος κουζίνας · γραμμή μετώπων βόρειου πάγκου

    # ------------------------------------------------ ΒΟΡΕΙΑ ΠΛΕΥΡΑ: πάγκος με εστίες (φούρνος από κάτω) · επάνω ντουλάπια ως την οροφή
    xe = eb[0]                                                  # 13.159: από εδώ και ανατολικά ο πάγκος γυρίζει στο έρκερ
    hx0, hx1 = hob[1], hob[3]
    no_tall = not K.get("north_tall", True)
    if no_tall:                                                 # Γιάννης 26/11: χωρίς ψηλή στήλη – πάγκος + επάνω ντουλάπια σε όλο το μήκος
        nb = [K["north_x0"], nb[1], nb[2], nb[3]]
        ub = [K["north_x0"], ub[1], ub[2], ub[3]]
    else:
        tx0, tx1 = tall[1], tall[3]
        ov0 = tx1 - 0.60
        mbox("k_tall_body", tx0, yn, tx1, yf - TH - 0.002, PL, ceil, body, group=G)
        mbox("k_tall_plinth", tx0, yn, tx1, yf - 0.06, 0, PL, white, group=G)
        half = (tx0 + ov0) / 2
        fronts("k_tall_cup", [tx0, half, ov0], [PL, 1.62, ceil - 0.004], yf, "S", oak)
        front("k_tall_dr", ov0, tx1, PL, 0.56, yf, "S", oak)
        front("k_tall_top", ov0, tx1, 1.62, ceil - 0.004, yf, "S", oak)
        oven("k_oven", ov0, tx1, 0.56, 1.16, yf, M)
        oven("k_oven2", ov0, tx1, 1.16, 1.62, yf, M)
        mbox("k_tall_side", tx0 - 0.018, yn, tx0, yf, 0, ceil, oak, group=G)
    xw = nb[0] + (TH if no_tall else 0.0)                       # τελειωμένο πλαϊνό στο ελεύθερο (δυτικό) άκρο
    if no_tall:
        mbox("k_nb_end", nb[0], yn, xw, yf, 0, CT - CTT, white, group=G)
        mbox("k_un_end", nb[0], yn, xw, ub[3], UB, ceil, white, group=G)
    mbox("k_nb_body", xw, yn, nb[2], yf - TH - 0.002, PL, CT - CTT, body, group=G)
    mbox("k_nb_plinth", xw, yn, xe, yf - 0.06, 0, PL, white, group=G)
    if no_tall:
        xm = (xw + hx0) / 2
        fronts("k_nb_dr0", [xw, xm], [PL, 0.36, 0.62, CT - CTT], yf, "S", white)
        fronts("k_nb_d0", [xm, (xm + hx0) / 2, hx0], [PL, CT - CTT], yf, "S", white)
        front("k_nb_ovd", hx0, hx1, PL, 0.275, yf, "S", white)
        oven("k_oven", hx0, hx1, 0.275, CT - CTT - 0.004, yf, M)
    else:
        front("k_nb_d1", nb[0], hx0, PL, CT - CTT, yf, "S", white)
        fronts("k_nb_dr", [hx0, hx1], [PL, 0.36, 0.62, CT - CTT], yf, "S", white)
    front("k_nb_d2", hx1, xe, PL, CT - CTT, yf, "S", white)
    mbox("k_eb_body", xe + TH + 0.002, eb[1], eb[2], eb[3], PL, CT - CTT, body, group=G)
    mbox("k_eb_plinth", xe + 0.06, yf - 0.06, eb[2], eb[3], 0, PL, white, group=G)
    ym = (eb[1] + eb[3]) / 2
    fronts("k_eb_d", [eb[1], ym, eb[3]], [PL, CT - CTT], xe, "W", white)
    # πάγκος (σχήμα Γ) + η εσοχή 9 cm πίσω από τον πάγκο στο έρκερ
    ydent = min(w["box"][3] for w in D["walls"] if w["id"] == "T4-12")
    xdent = max(w["box"][2] for w in D["walls"] if w["id"] == "T1-08")
    mbox("k_ct_n", nb[0], yn, nb[2], yf + 0.02, CT - CTT, CT, stone, group=G)
    mbox("k_ct_e", xe - 0.02, yf + 0.02, eb[2], eb[3], CT - CTT, CT, stone, group=G)
    mbox("k_ct_dent", xdent, ydent, nb[2], yn, CT - CTT, CT, stone, group=G)
    mbox("k_bs_n", nb[0], yn, xdent, yn + 0.012, CT, UB, stone, group=G)
    mbox("k_bs_dent", xdent, ydent, nb[2], ydent + 0.012, CT, UB, stone, group=G)
    mbox("k_bs_dent2", xdent, ydent, xdent + 0.012, yn, CT, UB, stone, group=G)
    we = [w for w in D["wins"] if w["name"] == "W2.04"][0]
    mbox("k_bs_e", nb[2] - 0.012, ydent + 0.012, nb[2], eb[3], CT, we["z0"], stone, group=G)
    mbox("k_hob", hx0 + 0.01, yn + 0.05, hx1 - 0.01, yf - 0.04, CT, CT + 0.005, M["black_glass"], r=0.002, seg=2, group=G)
    # επάνω ντουλάπια
    xu = nb[2] - UD
    mbox("k_un_body", xw, yn, ub[2], ub[3] - TH - 0.002, UB, ceil, body, group=G)
    mbox("k_un_fill", xdent, ydent, nb[2], yn, UB, ceil, white, group=G)
    if no_tall:
        xm = (xw + hx0) / 2
        fronts("k_un", [xw, (xw + xm) / 2, xm, (xm + hx0) / 2, hx0, hx1, (hx1 + xu) / 2, xu], [UB, ceil - 0.004], ub[3], "S", white)
    else:
        fronts("k_un", [ub[0], hx0, hx1, xu], [UB, ceil - 0.004], ub[3], "S", white)
    mbox("k_ue_body", xu + TH + 0.002, ub[3], nb[2], eb[3], UB, ceil, body, group=G)
    yu = (ub[3] + eb[3]) / 2
    fronts("k_ue", [ub[3], yu, eb[3]], [UB, ceil - 0.004], xu, "W", white)
    mbox("k_un_under", ub[0], yn, ub[2], ub[3], UB - 0.002, UB, white, group=G)
    mbox("k_ue_under", xu, ub[3], nb[2], eb[3], UB - 0.002, UB, white, group=G)
    mbox("k_led_n", ub[0] + 0.03, ub[3] - 0.07, xu - 0.02, ub[3] - 0.055, UB - 0.006, UB - 0.002, M["led"], group=G)
    mbox("k_led_e", xu + 0.055, ub[3] + 0.03, xu + 0.07, eb[3] - 0.03, UB - 0.006, UB - 0.002, M["led"], group=G)

    # ------------------------------------------------ ΝΟΤΙΟ ΕΡΚΕΡ: ψυγείο (ψηλό, εντοιχισμένο) · νεροχύτης · πλυντήριο πιάτων · παράθυρο πάνω από τον πάγκο
    ys, yb = sb[1], sb[3]                                       # γραμμή μετώπων (9,46) · νότιος τοίχος (10,06)
    mbox("k_fr_body", fr_x0, ys + TH + 0.002, fr_x1 - TH, yb, PL, ceil, body, group=G)
    mbox("k_fr_side", fr_x1 - TH, ys, fr_x1, yb, 0, ceil, oak, group=G)
    mbox("k_fr_plinth", fr_x0, ys + 0.06, sb[2], yb, 0, PL, white, group=G)
    fronts("k_fr", [fr_x0, fr_x1], [PL, 0.80, 1.87, ceil - 0.004], ys, "N", oak)
    mbox("k_sb_body", fr_x1, ys + TH + 0.002, sb[2], yb, PL, CT - CTT, body, group=G)
    fronts("k_sb_dr", [fr_x1, sk_x0], [PL, 0.36, 0.62, CT - CTT], ys, "N", white)
    fronts("k_sb_sink", [sk_x0, (sk_x0 + sk_x1) / 2, sk_x1], [PL, CT - CTT], ys, "N", white)
    front("k_sb_dw", dw_x0, dw_x1, PL, CT - CTT, ys, "N", white)
    # πάγκος με άνοιγμα για τη γούρνα
    bx0, bx1 = (sk_x0 + sk_x1) / 2 - 0.25, (sk_x0 + sk_x1) / 2 + 0.25
    by0, by1 = ys + 0.12, yb - 0.09
    for i, r in enumerate(((fr_x1, ys - 0.02, bx0, yb), (bx1, ys - 0.02, sb[2], yb), (bx0, ys - 0.02, bx1, by0), (bx0, by1, bx1, yb))):
        mbox("k_ct_s%d" % i, r[0], r[1], r[2], r[3], CT - CTT, CT, stone, group=G)
    zb = CT - 0.20
    st = M["steel"]
    mbox("k_sink_b", bx0, by0, bx1, by1, zb, zb + 0.004, st, group=G)
    for i, r in enumerate(((bx0 - 0.004, by0 - 0.004, bx0, by1 + 0.004), (bx1, by0 - 0.004, bx1 + 0.004, by1 + 0.004), (bx0, by0 - 0.004, bx1, by0), (bx0, by1, bx1, by1 + 0.004))):
        mbox("k_sink_s%d" % i, r[0], r[1], r[2], r[3], zb, CT - CTT, st, group=G)
    d = rprism("k_drain", 0.07, 0.07, 0.003, 0.035, M["nickel"], re=0.001, group=G)
    place(d, (bx0 + bx1) / 2, (by0 + by1) / 2, zb + 0.004)
    # μπαταρία
    xt, yt = (sk_x0 + sk_x1) / 2, yb - 0.045
    b = cyl("k_tap_base", 0.024, 0.022, 0.05, M["nickel"], group=G); place(b, xt, yt, CT)
    tube("k_tap", [(xt, yt, CT + 0.04), (xt, yt, CT + 0.22), (xt, yt, CT + 0.34), (xt, yt - 0.07, CT + 0.385), (xt, yt - 0.17, CT + 0.35), (xt, yt - 0.185, CT + 0.27)], 0.011, M["nickel"], group=G)
    tube("k_tap_l", [(xt + 0.022, yt, CT + 0.035), (xt + 0.085, yt, CT + 0.06)], 0.006, M["nickel"], group=G)
    # πλάτη πάγκου (ως την ποδιά του παραθύρου) και πλαϊνά
    ws = [w for w in D["wins"] if w["name"] == "W2.03"][0]
    mbox("k_bs_s", fr_x1, yb - 0.012, sb[2], yb, CT, ws["z0"], stone, group=G)
    if ws["box"][0] - fr_x1 > 0.02:
        mbox("k_bs_s2", fr_x1, yb - 0.012, ws["box"][0], yb, ws["z0"], UB, stone, group=G)
    mbox("k_bs_s3", sb[2] - 0.012, ys - 0.02, sb[2], yb - 0.012, CT, UB, stone, group=G)
    mbox("k_sill_s", ws["box"][0], yb - 0.012, ws["box"][2], yb + 0.03, ws["z0"] - 0.015, ws["z0"], stone, group=G)
    # επάνω ντουλάπια νότια
    yu0 = yb - UD
    mbox("k_us_body", fr_x1, yu0 + TH + 0.002, sb[2], yb, UB, ceil, body, group=G)
    xs = [fr_x1, (fr_x1 + sk_x0) / 2, sk_x0, (sk_x0 + sk_x1) / 2, sk_x1, sb[2]]
    fronts("k_us", xs, [UB, ceil - 0.004], yu0, "N", white)
    mbox("k_us_under", fr_x1, yu0, sb[2], yb, UB - 0.002, UB, white, group=G)
    mbox("k_led_s", fr_x1 + 0.03, yu0 + 0.055, sb[2] - 0.03, yu0 + 0.07, UB - 0.006, UB - 0.002, M["led"], group=G)
    return dict(counter_n=(nb[0], yn, xe, yf), counter_e=eb, counter_s=(fr_x1, ys, sb[2], yb), CT=CT, UB=UB, hob=(hx0, hx1), sink=(bx0, by0, bx1, by1))
