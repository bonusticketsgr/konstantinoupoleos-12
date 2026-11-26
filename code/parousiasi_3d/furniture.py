"""ΠΑΡΟΥΣΙΑΣΗ 3D – έπιπλα σαλονιού / τραπεζαρίας (σκανδιναβικό ύφος: ανοιχτή δρυς, λινά υφάσματα, λεπτά πόδια).
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


# ------------------------------------------------------------------ καναπές γωνία
def sofa(D, M):
    x0, y0, x1, y1 = D["sofa"]["main"]
    rx0, ry0, rx1, ry1 = D["sofa"]["ret"]
    fab, oak = M["sofa"], M["oak"]["Z"]
    y0 += 0.02                                   # 2 cm από τον τοίχο
    ZL, ZB, ZS = 0.13, 0.27, 0.44                # πόδια · βάση · άνω στάθμη καθίσματος
    BT, AT = 0.20, 0.15                          # πάχος πλάτης · μπράτσου
    xb = x1 - BT                                 # εσωτερική παρειά της ανατολικής πλάτης
    yb = y0 + BT - 0.02                          # εσωτερική παρειά της βόρειας πλάτης
    # βάση
    mbox("sofa_base", x0, y0, x1, y1, ZL, ZB, fab, r=0.03, seg=4, group=G)
    mbox("sofa_base_r", rx0, y1 - 0.06, rx1, ry1, ZL, ZB, fab, r=0.03, seg=4, group=G)
    # πλάτες και μπράτσο
    mbox("sofa_back_n", x0, y0, x1, yb, ZB - 0.02, 0.74, fab, r=0.055, seg=5, group=G)
    mbox("sofa_back_e", xb, yb - 0.06, x1, ry1, ZB - 0.02, 0.74, fab, r=0.055, seg=5, group=G)
    mbox("sofa_arm", x0, yb - 0.06, x0 + AT, y1, ZB - 0.02, 0.62, fab, r=0.055, seg=5, group=G)
    # μαξιλάρια καθίσματος: δύο στο κύριο σώμα + ένα μακρύ στο γύρισμα
    sx0, sx1 = x0 + AT, rx0
    n = 2
    wseat = (sx1 - sx0) / n
    for i in range(n):
        c = cushion("sofa_seat%d" % i, wseat - 0.012, (y1 - yb) - 0.01, ZS - ZB, fab, bulge=0.022, seg=5, group=G)
        place(c, sx0 + wseat * (i + 0.5), (yb + y1) / 2 + 0.005, (ZB + ZS) / 2, rz=RNG.uniform(-0.4, 0.4))
    c = cushion("sofa_seat_r", (xb - rx0) - 0.012, (ry1 - yb) - 0.012, ZS - ZB, fab, bulge=0.022, seg=5, group=G)
    place(c, (rx0 + xb) / 2, (yb + ry1) / 2 + 0.004, (ZB + ZS) / 2)
    # μαξιλάρια πλάτης (γερμένα)
    bw = (xb - sx0) / 3
    for i in range(3):
        c = cushion("sofa_bk%d" % i, bw - 0.02, 0.40, 0.17, fab, r=0.07, bulge=0.035, seg=5, group=G)
        place(c, sx0 + bw * (i + 0.5), yb + 0.105, ZS + 0.205, rx=78 + RNG.uniform(-2, 2), rz=RNG.uniform(-1.2, 1.2))
    bl = (ry1 - (yb + 0.22)) / 2
    for i in range(2):
        c = cushion("sofa_bke%d" % i, bl - 0.03, 0.40, 0.17, fab, r=0.07, bulge=0.035, seg=5, group=G)
        place(c, xb - 0.105, yb + 0.22 + bl * (i + 0.5), ZS + 0.205, rx=78 + RNG.uniform(-2, 2), rz=-90 + RNG.uniform(-1.2, 1.2))
    # πόδια
    for (lx, ly) in ((x0 + 0.07, y0 + 0.07), (x0 + 0.07, y1 - 0.07), (rx0 - 0.03, y1 - 0.07), (rx0 + 0.07, ry1 - 0.07), (x1 - 0.07, ry1 - 0.07), (x1 - 0.07, y0 + 0.07), ((x0 + x1) / 2, y0 + 0.07)):
        c = cyl("sofa_leg", 0.015, 0.022, ZL + 0.01, oak, group=G); place(c, lx, ly, 0)
    # διακοσμητικά μαξιλάρια + ριχτάρι
    pil = [("p_sage", sx0 + 0.24, yb + 0.20, 0.47, 62, 8), ("p_cream", sx0 + 0.62, yb + 0.19, 0.42, 66, -10), ("p_rust", xb - 0.20, yb + 0.62, 0.45, 64, -98),
           ("p_cream", xb - 0.19, ry1 - 0.42, 0.42, 68, -84)]
    for i, (mk, px, py, w, rxx, rzz) in enumerate(pil):
        p = pillow("pillow%d" % i, w, 0.15, M[mk], group="decor")
        place(p, px, py, ZS + w / 2 * math.sin(math.radians(rxx)) + 0.03, rx=rxx, rz=rzz)
    t = cushion("throw", 0.52, 0.36, 0.055, M["p_mustard"], r=0.022, bulge=0.008, seg=4, group="decor")
    place(t, (rx0 + xb) / 2 - 0.02, ry1 - 0.26, ZS + 0.045, rz=6)
    t2 = cushion("throw2", 0.50, 0.34, 0.045, M["p_mustard"], r=0.02, bulge=0.006, seg=4, group="decor")
    place(t2, (rx0 + xb) / 2 - 0.03, ry1 - 0.265, ZS + 0.092, rz=3)
    return dict(seat=ZS, back=0.74)


# ------------------------------------------------------------------ τραπεζάκι σαλονιού, χαλί
def coffee_table(D, M):
    x0, y0, x1, y1 = D["coffee"]
    oak = M["oak"]["X"]
    H = 0.38
    top = rprism("coffee_top", x1 - x0, y1 - y0, 0.028, 0.09, oak, re=0.007, segc=10, sege=3, group=G)
    place(top, (x0 + x1) / 2, (y0 + y1) / 2, H - 0.028)
    sh = rprism("coffee_shelf", (x1 - x0) - 0.16, (y1 - y0) - 0.14, 0.018, 0.05, oak, re=0.004, group=G)
    place(sh, (x0 + x1) / 2, (y0 + y1) / 2, 0.13)
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = cyl("coffee_leg", 0.012, 0.019, H - 0.028, M["oak"]["Z"], group=G)
            place(leg, (x0 + x1) / 2 + sx * ((x1 - x0) / 2 - 0.11), (y0 + y1) / 2 + sy * ((y1 - y0) / 2 - 0.09), 0, rx=-sy * 4.0, ry=-sx * 4.0)
    return H


def rug(D, M, rect):
    x0, y0, x1, y1 = rect
    r = rprism("rug", x1 - x0, y1 - y0, 0.014, 0.03, M["rug"], re=0.006, segc=6, sege=3, group=G)
    place(r, (x0 + x1) / 2, (y0 + y1) / 2, 0.0005)


# ------------------------------------------------------------------ έπιπλο TV
def tv_unit(D, M, x0, x1, wall_y):
    oak, oakx = M["oak"]["Z"], M["oak"]["X"]
    y1 = wall_y - 0.012
    y0 = y1 - 0.40
    z0, z1 = 0.17, 0.53
    mbox("tv_body", x0, y0 + 0.02, x1, y1, z0, z1, M["carcass"], group=G)
    mbox("tv_top", x0 - 0.008, y0, x1 + 0.008, y1, z1, z1 + 0.022, oakx, r=0.005, seg=2, group=G)
    mbox("tv_bot", x0 - 0.008, y0, x1 + 0.008, y1, z0 - 0.022, z0, oakx, r=0.005, seg=2, group=G)
    for xx in (x0 - 0.008, x1 - 0.014):
        mbox("tv_side", xx, y0, xx + 0.022, y1, z0, z1, oak, r=0.004, seg=2, group=G)
    n = 4
    w = (x1 - x0 - 0.028) / n
    for i in range(n):
        mbox("tv_door%d" % i, x0 + 0.014 + i * w + 0.0015, y0 + 0.004, x0 + 0.014 + (i + 1) * w - 0.0015, y0 + 0.022, z0 + 0.002, z1 - 0.002, oak, r=0.002, seg=2, group=G)
    for lx in (x0 + 0.10, x1 - 0.10):
        for ly in (y0 + 0.06, y1 - 0.06):
            c = cyl("tv_leg", 0.011, 0.016, z0 - 0.02, M["black"], group=G); place(c, lx, ly, 0)
    # τηλεόραση στον τοίχο
    cx = (x0 + x1) / 2
    tw, th = 1.45, 0.83
    tz = 0.86
    mbox("tv_frame", cx - tw / 2, wall_y - 0.034, cx + tw / 2, wall_y - 0.004, tz, tz + th, M["black"], r=0.004, seg=2, group=G)
    mbox("tv_screen", cx - tw / 2 + 0.008, wall_y - 0.0355, cx + tw / 2 - 0.008, wall_y - 0.033, tz + 0.012, tz + th - 0.008, M["screen"], group=G)
    return dict(top=z1 + 0.022, y0=y0, y1=y1)


# ------------------------------------------------------------------ τραπεζαρία
def dining_table(D, M):
    x0, y0, x1, y1 = D["table"]
    H = 0.75
    top = rprism("dt_top", x1 - x0, y1 - y0, 0.032, 0.06, M["oak"]["X"], re=0.009, segc=10, sege=3, group=G)
    place(top, (x0 + x1) / 2, (y0 + y1) / 2, H - 0.032)
    ix, iy = 0.16, 0.11
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = cyl("dt_leg", 0.020, 0.031, H - 0.032, M["oak"]["Z"], seg=7, group=G)
            place(leg, (x0 + x1) / 2 + sx * ((x1 - x0) / 2 - ix), (y0 + y1) / 2 + sy * ((y1 - y0) / 2 - iy), 0, rx=-sy * 3.5, ry=-sx * 3.5)
    mbox("dt_rail_n", x0 + ix + 0.03, y0 + iy - 0.012, x1 - ix - 0.03, y0 + iy + 0.012, H - 0.105, H - 0.032, M["oak"]["X"], r=0.004, seg=2, group=G)
    mbox("dt_rail_s", x0 + ix + 0.03, y1 - iy - 0.012, x1 - ix - 0.03, y1 - iy + 0.012, H - 0.105, H - 0.032, M["oak"]["X"], r=0.004, seg=2, group=G)
    mbox("dt_rail_w", x0 + ix - 0.012, y0 + iy + 0.03, x0 + ix + 0.012, y1 - iy - 0.03, H - 0.105, H - 0.032, M["oak"]["Y"], r=0.004, seg=2, group=G)
    mbox("dt_rail_e", x1 - ix - 0.012, y0 + iy + 0.03, x1 - ix + 0.012, y1 - iy - 0.03, H - 0.105, H - 0.032, M["oak"]["Y"], r=0.004, seg=2, group=G)
    return H


def _arc_band(name, R, a0, a1, z0, z1, th, mat, n=16):
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
    bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = 0.006; bv.segments = 3; bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(50)
    try:
        bv.harden_normals = True
    except Exception:
        pass
    return ob


def chair(name, M, x, y, face_deg, seat_mat=None):
    """Καρέκλα τραπεζαρίας (δρυς, καμπύλη πλάτη, υφαντό κάθισμα). face_deg: προς τα πού κοιτά – 0 = βόρεια (+Y Blender), 180 = νότια."""
    oak = M["oak"]["Z"]
    parts = []
    SH = 0.445
    for sx in (-1, 1):                                   # μπροστινά πόδια
        l = cyl(name + "_fl", 0.012, 0.0175, SH, oak, group=G); _loc(l, sx * 0.185, 0.165, 0, rx=2.5, ry=-sx * 2.5); parts.append(l)
    for sx in (-1, 1):                                   # πίσω πόδια: ενιαία ως την πλάτη, με κλίση προς τα πίσω
        l = cyl(name + "_rl", 0.012, 0.0175, SH, oak, group=G); _loc(l, sx * 0.17, -0.17, 0, rx=-3.0, ry=-sx * 2.0); parts.append(l)
        u = cyl(name + "_ru", 0.0165, 0.012, 0.33, oak, group=G); _loc(u, sx * 0.17, -0.185, SH - 0.01, rx=11.0); parts.append(u)
    fr = lbox(name + "_frame", 0.43, 0.41, 0.03, oak, r=0.012, seg=3, group=G); _loc(fr, 0, 0, SH - 0.005); parts.append(fr)
    st = cushion(name + "_seat", 0.405, 0.385, 0.028, seat_mat or M["cord"], r=0.012, bulge=0.006, seg=3, group=G); _loc(st, 0, 0.002, SH + 0.022); parts.append(st)
    bk = _arc_band(name + "_back", 0.305, 232, 308, 0.67, 0.79, 0.022, oak); _loc(bk, 0, 0.0, 0); parts.append(bk)
    for sx in (-1, 1):                                   # πλαϊνές τραβέρσες
        r = cyl(name + "_str", 0.008, 0.008, 0.33, oak, group=G); _loc(r, sx * 0.178, -0.165, 0.20, rx=-90); parts.append(r)
    e = L.parent_all(name, parts, group=G)
    e.location = P(x, y, 0)
    e.rotation_euler = Euler((0, 0, math.radians(face_deg)))
    return e


def chairs(D, M):
    tx0, ty0, tx1, ty1 = D["table"]
    for i, e in enumerate([q for q in D["equip"] if q[0] == "chair" and tx0 - 0.2 < q[1] < tx1 + 0.2 and ty0 - 0.8 < q[2] < ty1 + 0.8]):
        cx, cy = (e[1] + e[3]) / 2, (e[2] + e[4]) / 2
        north = e[5] == "N"                              # πλάτη βόρεια → κοιτά νότια
        pull = RNG.uniform(-0.03, 0.05)
        chair("chair%d" % i, M, cx + RNG.uniform(-0.012, 0.012), cy + (0.02 + pull if north else -0.02 - pull), (180 if north else 0) + RNG.uniform(-4, 4))


# ------------------------------------------------------------------ φωτιστικό δαπέδου
def floor_lamp(M, x, y):
    b = rprism("lamp_base", 0.27, 0.27, 0.018, 0.135, M["black"], re=0.005, segc=10, group=G); place(b, x, y, 0)
    tube("lamp_stem", [(x, y, 0.018), (x, y, 1.42)], 0.007, M["black"], group=G)
    verts, faces = [], []
    n = 40
    r0, r1, z0, z1 = 0.19, 0.14, 1.36, 1.60
    for i in range(n):
        a = 2 * math.pi * i / n
        verts += [(r0 * math.cos(a), r0 * math.sin(a), z0), (r1 * math.cos(a), r1 * math.sin(a), z1)]
    for i in range(n):
        j = (i + 1) % n
        faces.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    sh = obj_from("lamp_shade", verts, faces, M["shade"], smooth=True, group=G)
    sh.location = P(x, y, 0)
    return (x, y, 1.47)


# ------------------------------------------------------------------ μπουφές στον βόρειο τοίχο της τραπεζαρίας + στρογγυλός καθρέπτης + πορτατίφ
def sideboard(M, x0, x1, wall_y, depth=0.42, z0=0.16, z1=0.74, n=3):
    oak, oakx = M["oak"]["Z"], M["oak"]["X"]
    y0 = wall_y + 0.012; y1 = y0 + depth
    mbox("sb_body", x0, y0, x1, y1 - 0.02, z0, z1, M["carcass"], group=G)
    mbox("sb_top", x0 - 0.008, y0, x1 + 0.008, y1, z1, z1 + 0.022, oakx, r=0.005, seg=2, group=G)
    mbox("sb_bot", x0 - 0.008, y0, x1 + 0.008, y1, z0 - 0.022, z0, oakx, r=0.005, seg=2, group=G)
    for xx in (x0 - 0.008, x1 - 0.014):
        mbox("sb_side", xx, y0, xx + 0.022, y1, z0, z1, oak, r=0.004, seg=2, group=G)
    w = (x1 - x0 - 0.028) / n
    for i in range(n):
        mbox("sb_door%d" % i, x0 + 0.014 + i * w + 0.0015, y1 - 0.022, x0 + 0.014 + (i + 1) * w - 0.0015, y1 - 0.004, z0 + 0.002, z1 - 0.002, oak, r=0.002, seg=2, group=G)
    for lx in (x0 + 0.10, x1 - 0.10):
        for ly in (y0 + 0.06, y1 - 0.06):
            c = cyl("sb_leg", 0.011, 0.016, z0 - 0.02, oak, group=G); place(c, lx, ly, 0)
    return dict(top=z1 + 0.022, y0=y0, y1=y1)


def mirror_round(M, cx, zc, d, wall_y):
    """Στρογγυλός καθρέπτης σε τοίχο που κοιτά νότια."""
    fr = rprism("mirror_frame", d, d, 0.022, d / 2, M["oak"]["X"], re=0.004, segc=16, sege=2, group=G)
    place(fr, cx, wall_y, zc, rx=90)                                   # δίσκος-πλάτη (το ξύλινο πλαίσιο φαίνεται γύρω-γύρω)
    gl = rprism("mirror_glass", d - 0.036, d - 0.036, 0.002, d / 2 - 0.018, M["mirror"], re=0.0, segc=16, group=G)
    place(gl, cx, wall_y + 0.0222, zc, rx=90)


def table_lamp(M, x, y, z):
    import decor as DC
    b = DC.lathe("tl_base", [(0.0, 0.0), (0.06, 0.0), (0.075, 0.03), (0.08, 0.09), (0.06, 0.17), (0.025, 0.21), (0.012, 0.23), (0.012, 0.27), (0.0, 0.27)], M["ceramic_sand"], seg=36, group=G)
    place(b, x, y, z)
    verts, faces = [], []
    n = 36
    r0, r1, za, zb = 0.15, 0.11, 0.24, 0.43
    for i in range(n):
        a = 2 * math.pi * i / n
        verts += [(r0 * math.cos(a), r0 * math.sin(a), za), (r1 * math.cos(a), r1 * math.sin(a), zb)]
    for i in range(n):
        j = (i + 1) % n
        faces.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    sh = obj_from("tl_shade", verts, faces, M["shade"], smooth=True, group=G)
    sh.location = P(x, y, z)
    return (x, y, z + 0.33)
