"""ΠΑΡΟΥΣΙΑΣΗ 3D – έπιπλα σαλονιού / τραπεζαρίας. ΥΦΟΣ (Γιάννης 26/11/2026: «πιο ζεστά … σαν τα render του ISV … cosy»): ζεστός μινιμαλισμός –
χαμηλός καναπές σε κρεμ μπουκλέ, φυσική δρυς και σκούρα (καπνιστή) δρυς, τραβερτίνης, δέρμα κονιάκ, λινά, μπρούντζινες λεπτομέρειες.
Οι ΘΕΣΕΙΣ και οι διαστάσεις κάτοψης είναι του σχεδίου (scene.json: sofa · coffee · table · equip)· τα ύψη και η μορφή είναι ΕΝΔΕΙΚΤΙΚΑ."""
import math
import bpy
from mathutils import Vector, Euler
import lib as L
from lib import mbox, lbox, place, rprism, cyl, cushion, pillow, tube, P, RNG, obj_from

G = "furn"


def _loc(ob, x, y, z, rx=0.0, ry=0.0, rz=0.0):
    """Τοποθέτηση σε ΤΟΠΙΚΕΣ συντεταγμένες Blender (για συναρμολογήματα που μετά στρέφονται όλα μαζί)."""
    ob.location = Vector((x, y, z))
    ob.rotation_euler = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), "XYZ")
    return ob


# ------------------------------------------------------------------ καναπές γωνία (χαμηλός, πάνω σε χωνευτή βάση – χωρίς πόδια)
def sofa(D, M):
    x0, y0, x1, y1 = D["sofa"]["main"]
    rx0, ry0, rx1, ry1 = D["sofa"]["ret"]
    fab = M["sofa"]
    y0 += 0.03                                   # 3 cm από τον τοίχο
    ZP, ZB, ZS = 0.05, 0.23, 0.44                # χωνευτή βάση · σώμα · άνω στάθμη καθίσματος
    BT, AT = 0.21, 0.21                          # πάχος πλάτης · μπράτσου
    BH, AH = 0.63, 0.57                          # ύψος πλάτης · μπράτσου
    xb = x1 - BT                                 # εσωτερική παρειά της ανατολικής πλάτης
    yb = y0 + BT                                 # εσωτερική παρειά της βόρειας πλάτης
    # χωνευτή σκούρα βάση (σκιά κάτω από τον καναπέ)
    mbox("sofa_plinth", x0 + 0.07, y0 + 0.05, x1 - 0.07, y1 - 0.07, 0, ZP, M["black"], group=G)
    mbox("sofa_plinth_r", rx0 + 0.07, y1 - 0.07, rx1 - 0.07, ry1 - 0.07, 0, ZP, M["black"], group=G)
    # σώμα
    mbox("sofa_base", x0, y0, x1, y1, ZP, ZB, fab, r=0.028, seg=4, group=G)
    mbox("sofa_base_r", rx0, y1 - 0.06, rx1, ry1, ZP, ZB, fab, r=0.028, seg=4, group=G)
    # πλάτες και μπράτσο (ίσια, χαμηλά)
    mbox("sofa_back_n", x0, y0, x1, yb, ZB - 0.03, BH, fab, r=0.05, seg=5, group=G)
    mbox("sofa_back_e", xb, yb - 0.07, x1, ry1, ZB - 0.03, BH, fab, r=0.05, seg=5, group=G)
    mbox("sofa_arm", x0, yb - 0.07, x0 + AT, y1, ZB - 0.03, AH, fab, r=0.05, seg=5, group=G)
    # μαξιλάρια καθίσματος: δύο στο κύριο σώμα, ένα στη γωνία, ένα στο γύρισμα
    sx0 = x0 + AT
    wseat = (rx0 - sx0) / 2
    for i in range(2):
        c = cushion("sofa_seat%d" % i, wseat - 0.014, (y1 - yb) - 0.012, ZS - ZB, fab, r=0.045, bulge=0.02, seg=6, group=G)
        place(c, sx0 + wseat * (i + 0.5), (yb + y1) / 2 + 0.006, (ZB + ZS) / 2, rz=RNG.uniform(-0.3, 0.3))
    c = cushion("sofa_seat_c", (xb - rx0) - 0.014, (y1 - yb) - 0.012, ZS - ZB, fab, r=0.045, bulge=0.02, seg=6, group=G)
    place(c, (rx0 + xb) / 2, (yb + y1) / 2 + 0.006, (ZB + ZS) / 2)
    c = cushion("sofa_seat_r", (xb - rx0) - 0.014, (ry1 - y1) - 0.012, ZS - ZB, fab, r=0.045, bulge=0.02, seg=6, group=G)
    place(c, (rx0 + xb) / 2, (y1 + ry1) / 2, (ZB + ZS) / 2)
    # μαξιλάρια πλάτης (μεγάλα, μαλακά, ελαφρά γερμένα)
    BW, BHh, BTh = None, 0.47, 0.20
    n = 3
    bw = (xb - sx0) / n
    for i in range(n):
        c = cushion("sofa_bk%d" % i, bw - 0.024, BHh, BTh, fab, r=0.085, bulge=0.04, seg=6, group=G)
        place(c, sx0 + bw * (i + 0.5), yb + 0.115, ZS + 0.225, rx=80 + RNG.uniform(-2, 2), rz=RNG.uniform(-1.0, 1.0))
    bl = (ry1 - (yb + 0.26)) / 2
    for i in range(2):
        c = cushion("sofa_bke%d" % i, bl - 0.03, BHh, BTh, fab, r=0.085, bulge=0.04, seg=6, group=G)
        place(c, xb - 0.115, yb + 0.26 + bl * (i + 0.5), ZS + 0.225, rx=80 + RNG.uniform(-2, 2), rz=-90 + RNG.uniform(-1.0, 1.0))
    # διακοσμητικά μαξιλάρια
    pil = [("p_olive", sx0 + 0.27, yb + 0.25, 0.50, 60, 10), ("p_cream", sx0 + 0.66, yb + 0.23, 0.44, 64, -8), ("p_caramel", xb - 0.22, yb + 0.64, 0.46, 62, -100),
           ("p_taupe", xb - 0.21, ry1 - 0.50, 0.44, 66, -84), ("p_cream", sx0 + 1.52, yb + 0.22, 0.42, 66, 4)]
    for i, (mk, px, py, w, rxx, rzz) in enumerate(pil):
        which = "pillow02" if i % 2 == 0 else "pillow01"            # έτοιμα μαξιλάρια (με τσακίσεις) ντυμένα με τα δικά μας υφάσματα· αλλιώς τα απλά
        o = L.model("throw_pillows_01", px, py, ZS - 0.02, rz=rzz - (0 if which == "pillow02" else 25), scale=w / 0.60, name="pillow%d" % i, group="decor",
                    pick=lambda n, which=which: n.endswith(which), mats={"throw_pillows": M[mk]})
        if o is None:
            p = pillow("pillow%d" % i, w, 0.16, M[mk], group="decor")
            place(p, px, py, ZS + w / 2 * math.sin(math.radians(rxx)) + 0.03, rx=rxx, rz=rzz)
    # διπλωμένο ριχτάρι στην άκρη του γυρίσματος
    t = cushion("throw", 0.56, 0.38, 0.05, M["throw"], r=0.022, bulge=0.008, seg=4, group="decor")
    place(t, (rx0 + xb) / 2 - 0.02, ry1 - 0.27, ZS + 0.04, rz=5)
    t2 = cushion("throw2", 0.53, 0.35, 0.04, M["throw"], r=0.018, bulge=0.006, seg=4, group="decor")
    place(t2, (rx0 + xb) / 2 - 0.03, ry1 - 0.275, ZS + 0.082, rz=2)
    return dict(seat=ZS, back=BH)


# ------------------------------------------------------------------ τραπεζάκι σαλονιού (τραβερτίνης), χαλί
def coffee_table(D, M):
    x0, y0, x1, y1 = D["coffee"]
    st = M["travertine"]
    H, TT = 0.33, 0.065
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    top = rprism("coffee_top", x1 - x0, y1 - y0, TT, 0.05, st, re=0.008, segc=10, sege=3, group=G)
    place(top, cx, cy, H - TT)
    for sx in (-1, 1):
        leg = rprism("coffee_leg", 0.30, 0.30, H - TT, 0.15, M["travertine_z"], re=0.004, segc=12, sege=2, group=G)
        place(leg, cx + sx * ((x1 - x0) / 2 - 0.25), cy, 0)
    return H


def rug(D, M, rect):
    x0, y0, x1, y1 = rect
    r = rprism("rug", x1 - x0, y1 - y0, 0.018, 0.02, M["rug"], re=0.008, segc=6, sege=3, group=G)
    place(r, (x0 + x1) / 2, (y0 + y1) / 2, 0.0005)


# ------------------------------------------------------------------ σύνθεση TV: επένδυση τοίχου σε δρυ (φύλλα + πηχάκια), κρεμαστό έπιπλο, κρυφό LED ΜΕΣΑ ΣΤΟ ΕΠΙΠΛΟ
def tv_wall(D, M, x0, x1, wall_y, zc, cx):
    """Όλος ο τοίχος της TV (x0…x1) ντυμένος με ξυλουργικό: είναι ΕΠΙΠΛΟ (ενδεικτικό), όχι τελείωμα του κτιρίου.
    Οι δύο κατακόρυφες φωτεινές σχισμές και η ταινία κάτω από το κρεμαστό είναι φωτισμός του επίπλου – καμία νέα σταθερή φωτιστική θέση του κτιρίου."""
    oak, oakx, dark = M["oak"]["Z"], M["oak"]["X"], M["carcass"]
    T = 0.036                                                      # πάχος επένδυσης
    ya, yw = wall_y - T, wall_y
    zt = zc - 0.012
    mbox("tvw_back", x0, ya + 0.022, x1, yw, 0.0, zt, dark, group=G)
    SL, GP = 0.020, 0.006                                          # πλάτος φωτεινής σχισμής · αρμός
    wing = 0.46                                                    # οι δύο ακραίες ζώνες με πηχάκια
    xa, xb = x0 + wing, x1 - wing
    # πηχάκια (κατακόρυφα, 26 mm ανά 12 mm) στις δύο ακραίες ζώνες
    for nm, a, b in (("L", x0 + 0.004, xa - SL), ("R", xb + SL, x1 - 0.004)):
        n = int((b - a + 0.012) / 0.038)
        step = (b - a + 0.012) / n
        for i in range(n):
            xs = a + i * step
            mbox("tvw_sl%s%d" % (nm, i), xs, ya - 0.006, xs + step - 0.012, ya + 0.024, 0.0, zt, oak, r=0.003, seg=1, group=G)
    # φωτεινές σχισμές
    for nm, xs in (("L", xa - SL), ("R", xb)):
        mbox("tvw_led" + nm, xs + 0.003, ya + 0.016, xs + SL - 0.003, ya + 0.020, 0.06, zt - 0.06, M["led_soft"], group=G)
    # λεία φύλλα καπλαμά στη μέση (3 φύλλα με λεπτό αρμό)
    n = 3
    w = (xb - xa) / n
    for i in range(n):
        mbox("tvw_p%d" % i, xa + i * w + GP / 2, ya, xa + (i + 1) * w - GP / 2, ya + 0.024, 0.0, zt, oak, r=0.0015, seg=1, group=G)
    # κρεμαστό έπιπλο
    ux0, ux1 = xa - 0.10, xb + 0.10
    y1 = ya
    y0 = y1 - 0.40
    z0, z1 = 0.26, 0.52
    mbox("tv_body", ux0 + 0.004, y0 + 0.02, ux1 - 0.004, y1, z0 + 0.004, z1 - 0.004, dark, group=G)
    mbox("tv_top", ux0, y0, ux1, y1, z1 - 0.022, z1, M["travertine"], r=0.004, seg=2, group=G)
    mbox("tv_bot", ux0, y0 + 0.003, ux1, y1, z0, z0 + 0.018, oakx, r=0.004, seg=2, group=G)
    for xx in (ux0, ux1 - 0.02):
        mbox("tv_side", xx, y0 + 0.003, xx + 0.02, y1, z0 + 0.018, z1 - 0.022, oak, r=0.003, seg=2, group=G)
    nd = 4
    wd = (ux1 - ux0 - 0.04) / nd
    for i in range(nd):
        mbox("tv_door%d" % i, ux0 + 0.02 + i * wd + 0.0015, y0 + 0.003, ux0 + 0.02 + (i + 1) * wd - 0.0015, y0 + 0.022, z0 + 0.020, z1 - 0.024, oakx, r=0.002, seg=2, group=G)
    mbox("tv_glow", ux0 + 0.06, y1 - 0.05, ux1 - 0.06, y1 - 0.035, z0 - 0.004, z0 - 0.001, M["led_soft"], group=G)
    # τηλεόραση
    tw, th = 1.45, 0.83
    tz = 0.92
    mbox("tv_frame", cx - tw / 2, ya - 0.030, cx + tw / 2, ya - 0.002, tz, tz + th, M["black"], r=0.004, seg=2, group=G)
    mbox("tv_screen", cx - tw / 2 + 0.008, ya - 0.0315, cx + tw / 2 - 0.008, ya - 0.029, tz + 0.012, tz + th - 0.008, M["screen"], group=G)
    return dict(top=z1, y0=y0, y1=y1, x0=ux0, x1=ux1)


# ------------------------------------------------------------------ τραπεζαρία: σκούρα δρυς, δύο πόδια-φύλλα
def dining_table(D, M):
    x0, y0, x1, y1 = D["table"]
    H, TT = 0.75, 0.045
    dk = M["oak_dark"]
    top = rprism("dt_top", x1 - x0, y1 - y0, TT, 0.035, dk["X"], re=0.010, segc=8, sege=3, group=G)
    place(top, (x0 + x1) / 2, (y0 + y1) / 2, H - TT)
    cy = (y0 + y1) / 2
    for sx in (-1, 1):
        xx = (x0 + x1) / 2 + sx * ((x1 - x0) / 2 - 0.36)
        mbox("dt_leg", xx - 0.04, y0 + 0.13, xx + 0.04, y1 - 0.13, 0.0, H - TT, dk["Z"], r=0.008, seg=2, group=G)
    mbox("dt_rail", (x0 + x1) / 2 - ((x1 - x0) / 2 - 0.40), cy - 0.02, (x0 + x1) / 2 + ((x1 - x0) / 2 - 0.40), cy + 0.02, H - TT - 0.16, H - TT, dk["X"], r=0.006, seg=2, group=G)
    return H


def _arc_band(name, R, a0, a1, z0, z1, th, mat, n=20, bevel=0.006):
    """Καμπύλη πλάτη καρέκλας: ζώνη σε τόξο (τοπικές συντεταγμένες, κέντρο τόξου στην αρχή)."""
    verts, faces = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        for rr in (R - th / 2, R + th / 2):
            for z in (z0, z1):
                verts.append((rr * math.cos(a), rr * math.sin(a), z))
    for i in range(n):
        a, b = 4 * i, 4 * (i + 1)
        faces += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3), (a, a + 2, b + 2, b)]
    faces += [(0, 1, 3, 2), (4 * n, 4 * n + 2, 4 * n + 3, 4 * n + 1)]
    ob = obj_from(name, verts, faces, mat, smooth=True, group=G)
    bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 4; bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(50)
    try:
        bv.harden_normals = True
    except Exception:
        pass
    return ob


def chair(name, M, x, y, face_deg):
    """Καρέκλα τραπεζαρίας ντυμένη με ύφασμα (πλάτη-αγκαλιά), σκούρα λεπτά πόδια. face_deg: προς τα πού κοιτά – 0 = βόρεια (+Y Blender), 180 = νότια."""
    fab, leg = M["chair"], M["oak_dark"]["Z"]
    parts = []
    SH = 0.47
    for sx in (-1, 1):
        for sy, ry_ in ((1, 3.0), (-1, -3.0)):
            l = cyl(name + "_l", 0.011, 0.017, 0.40, leg, group=G); _loc(l, sx * 0.175, sy * 0.165, 0, rx=sy * 3.0, ry=-sx * 3.0); parts.append(l)
    base = lbox(name + "_base", 0.46, 0.44, 0.05, fab, r=0.02, seg=3, group=G); _loc(base, 0, 0.0, 0.385); parts.append(base)
    st = cushion(name + "_seat", 0.45, 0.43, 0.075, fab, r=0.03, bulge=0.012, seg=5, group=G); _loc(st, 0, 0.005, SH - 0.0375); parts.append(st)
    bk = _arc_band(name + "_back", 0.245, 196, 344, 0.38, 0.80, 0.055, fab, n=24, bevel=0.022); _loc(bk, 0, 0.03, 0); parts.append(bk)
    e = L.parent_all(name, parts, group=G)
    e.location = P(x, y, 0)
    e.rotation_euler = Euler((0, 0, math.radians(face_deg)))
    return e


def chairs(D, M):
    tx0, ty0, tx1, ty1 = D["table"]
    for i, e in enumerate([q for q in D["equip"] if q[0] == "chair" and tx0 - 0.2 < q[1] < tx1 + 0.2 and ty0 - 0.8 < q[2] < ty1 + 0.8]):
        cx, cy = (e[1] + e[3]) / 2, (e[2] + e[4]) / 2
        north = e[5] == "N"                              # πλάτη βόρεια → κοιτά νότια
        pull = RNG.uniform(-0.02, 0.04)
        chair("chair%d" % i, M, cx + RNG.uniform(-0.010, 0.010), cy + (0.03 + pull if north else -0.03 - pull), (180 if north else 0) + RNG.uniform(-3, 3))


# ------------------------------------------------------------------ πολυθρόνα (δέρμα κονιάκ – έτοιμο μοντέλο· αλλιώς απλή υφασμάτινη)
def lounge_chair(M, x, y, rz):
    o = L.model("mid_century_lounge_chair", x, y, 0.0, rz=rz, scale=0.92, name="lounge", group=G)
    if o is not None:
        return o
    parts = []
    b = lbox("lounge_base", 0.78, 0.80, 0.26, M["p_olive"], r=0.06, seg=4, group=G); _loc(b, 0, 0, 0.27); parts.append(b)
    s = cushion("lounge_seat", 0.62, 0.62, 0.14, M["p_olive"], r=0.05, bulge=0.02, seg=5, group=G); _loc(s, 0, 0.04, 0.45); parts.append(s)
    k = cushion("lounge_back", 0.66, 0.50, 0.16, M["p_olive"], r=0.06, bulge=0.03, seg=5, group=G); _loc(k, 0, -0.30, 0.66, rx=78); parts.append(k)
    for sx in (-1, 1):
        a = lbox("lounge_arm", 0.12, 0.74, 0.34, M["p_olive"], r=0.05, seg=4, group=G); _loc(a, sx * 0.36, 0, 0.47); parts.append(a)
        for sy in (-1, 1):
            l = cyl("lounge_leg", 0.012, 0.018, 0.15, M["oak_dark"]["Z"], group=G); _loc(l, sx * 0.30, sy * 0.30, 0); parts.append(l)
    e = L.parent_all("lounge", parts, group=G)
    e.location = P(x, y, 0); e.rotation_euler = Euler((0, 0, math.radians(rz)))
    return e


def side_table(M, x, y, d=0.40, h=0.46):
    """Στρογγυλό βοηθητικό σε σκούρα δρυ."""
    t = rprism("side_top", d, d, 0.03, d / 2, M["oak_dark"]["X"], re=0.006, segc=12, sege=3, group=G); place(t, x, y, h - 0.03)
    c = rprism("side_col", 0.10, 0.10, h - 0.045, 0.05, M["oak_dark"]["Z"], re=0.002, segc=10, group=G); place(c, x, y, 0.015)
    b = rprism("side_base", d * 0.72, d * 0.72, 0.016, d * 0.36, M["oak_dark"]["X"], re=0.004, segc=12, sege=2, group=G); place(b, x, y, 0)
    return h


# ------------------------------------------------------------------ φωτιστικά (κινητά – μπαίνουν στην πρίζα)
def _drum(name, M, x, y, z0, r, h):
    verts, faces = [], []
    n = 48
    for i in range(n):
        a = 2 * math.pi * i / n
        verts += [(r * math.cos(a), r * math.sin(a), z0), (r * math.cos(a), r * math.sin(a), z0 + h)]
    for i in range(n):
        j = (i + 1) % n
        faces.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    sh = obj_from(name, verts, faces, M["shade"], smooth=True, group=G)
    sh.location = P(x, y, 0)
    return sh


def floor_lamp(M, x, y):
    b = rprism("lamp_base", 0.26, 0.26, 0.016, 0.13, M["bronze"], re=0.005, segc=12, group=G); place(b, x, y, 0)
    tube("lamp_stem", [(x, y, 0.016), (x, y, 1.40)], 0.008, M["bronze"], group=G)
    _drum("lamp_shade", M, x, y, 1.30, 0.20, 0.28)
    return (x, y, 1.44)


def table_lamp(M, x, y, z):
    import decor as DC
    b = DC.lathe("tl_base", [(0.0, 0.0), (0.055, 0.0), (0.07, 0.02), (0.085, 0.09), (0.075, 0.17), (0.04, 0.23), (0.016, 0.26), (0.012, 0.30), (0.0, 0.30)], M["ceramic_sand"], seg=40, group=G)
    place(b, x, y, z)
    _drum("tl_shade", M, x, y, z + 0.27, 0.15, 0.21)
    return (x, y, z + 0.37)
