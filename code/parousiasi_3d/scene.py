"""ΠΑΡΟΥΣΙΑΣΗ 3D – ΣΑΛΟΝΙ / ΚΟΥΖΙΝΑ τυπικού ορόφου (Β1): φωτορεαλιστικές εικόνες για παρουσίαση σε πελάτες (Blender Cycles).

    python3 export_scene.py                         → scene.json (γεωμετρία από τα μοντέλα των τευχών – τοιχοποιίες, ανόψεις, ηλεκτρολογικά + πρόταση R18)
    <python με bpy> scene.py --views all --res 1920x1080 --samples 400 --out <φάκελος>

Το κτίριο (τοίχοι, κολόνες, δοκάρια, στάθμες οροφής, κουφώματα, κουζίνα, θέσεις επίπλων, φώτα, διακόπτες / πρίζες) διαβάζεται από το scene.json.
Έπιπλα, υφάσματα, διακοσμητικά, φυτά, κουρτίνες, ό,τι φαίνεται έξω από τα τζάμια: ΕΝΔΕΙΚΤΙΚΑ (ύφος παρουσίασης – δεν είναι μέρος της μελέτης)."""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import lib as L
from lib import mbox, prism, place, rprism, cyl, tube, P, srgb, obj_from, RNG
import kitchen as KT
import furniture as FU
import decor as DC
import exterior as EX

EPS = 0.0006
LIVING = ("Ζ1", "Ζ2")
SHOWN = ("Ζ1", "Ζ2", "Ζ3", "Ζ4", "Ζ9")             # χώροι που φαίνονται: σαλόνι – τραπεζαρία, κουζίνα, χωλ


def materials():
    M = {}
    M["wall"] = L.paint("wall", srgb(236, 233, 226))
    M["ceil"] = L.paint("ceil", srgb(244, 243, 239), bump=0.012)
    M["white"] = L.plain("white_lacq", srgb(236, 235, 231), rough=0.38)
    M["front"] = L.plain("front", srgb(227, 223, 214), rough=0.45)
    M["carcass"] = L.plain("carcass", srgb(74, 72, 68), rough=0.6)
    M["oak"] = {a: L.wood("oak_" + a, a) for a in "XYZ"}
    M["floor"] = L.wood("oak_floor", "X", c_dark=(178, 152, 120), c_light=(214, 194, 164), rough=0.36, attr="plank", tone_var=0.075, scale=0.8)
    M["floor_gap"] = L.plain("floor_gap", srgb(64, 50, 38), rough=0.85)
    M["quartz"] = L.stone("quartz")
    M["black"] = L.plain("black", srgb(30, 30, 30), rough=0.42)
    M["black_glass"] = L.plain("black_glass", srgb(12, 12, 13), rough=0.06)
    M["screen"] = L.plain("screen", srgb(9, 9, 10), rough=0.13)
    M["display"] = L.emit("display", (0.6, 0.8, 1.0, 1), 0.5)
    M["nickel"] = L.plain("nickel", (0.72, 0.70, 0.66, 1), rough=0.28, metal=1.0)
    M["steel"] = L.plain("steel", (0.62, 0.62, 0.62, 1), rough=0.32, metal=1.0)
    M["alu"] = L.plain("alu_bronze", srgb(60, 54, 48), rough=0.45, metal=0.55)
    M["glass"] = L.glass()
    M["glass_clear"] = L.glass("glass_clear", view=(0.9, 0.93, 0.92, 1.0))
    M["sheer"] = L.sheer()
    M["sofa"] = L.fabric("sofa", srgb(176, 166, 150), weave=520.0, bump=0.35, sheen=0.4, boucle=True)
    M["rug"] = L.fabric("rug", srgb(224, 216, 200), weave=240.0, bump=0.9, sheen=0.5, boucle=True, mottle=0.10)
    M["cord"] = L.fabric("cord", srgb(206, 192, 164), weave=380.0, bump=0.5, sheen=0.1)
    M["p_sage"] = L.fabric("p_sage", srgb(132, 148, 124), weave=600.0, bump=0.3)
    M["p_cream"] = L.fabric("p_cream", srgb(230, 223, 208), weave=420.0, bump=0.5, boucle=True)
    M["p_rust"] = L.fabric("p_rust", srgb(178, 106, 72), weave=600.0, bump=0.3)
    M["p_mustard"] = L.fabric("p_mustard", srgb(200, 162, 88), weave=500.0, bump=0.4)
    M["shade"] = L.leaf("shade", srgb(238, 230, 212), srgb(238, 230, 212), rough=0.85, trans=0.6)
    M["ceramic"] = L.plain("ceramic", srgb(232, 228, 220), rough=0.35)
    M["ceramic_sand"] = L.plain("ceramic_sand", srgb(198, 178, 152), rough=0.6)
    M["soil"] = L.plain("soil", srgb(52, 42, 34), rough=0.95)
    M["bark"] = L.plain("bark", srgb(94, 76, 60), rough=0.8)
    M["stem"] = L.plain("stem", srgb(88, 112, 70), rough=0.6)
    M["leaf"] = L.leaf("leaf", srgb(62, 92, 54), srgb(94, 122, 70))
    M["leaf2"] = L.leaf("leaf2", srgb(58, 100, 60), srgb(98, 136, 80))
    M["leaf_euca"] = L.leaf("leaf_euca", srgb(120, 142, 124), srgb(152, 168, 148), trans=0.15)
    M["grass"] = L.leaf("grass", srgb(98, 122, 70), srgb(144, 154, 96), trans=0.2)
    M["paper"] = L.plain("paper", srgb(242, 238, 230), rough=0.8)
    M["wax"] = L.plain("wax", srgb(240, 234, 220), rough=0.5)
    M["lemon"] = L.plain("lemon", srgb(228, 192, 62), rough=0.45)
    M["amber"] = L.plain("amber", srgb(118, 72, 34), rough=0.12)
    M["bk_sand"] = L.plain("bk_sand", srgb(206, 190, 160), rough=0.6)
    M["bk_sage"] = L.plain("bk_sage", srgb(130, 146, 128), rough=0.6)
    M["bk_char"] = L.plain("bk_char", srgb(58, 58, 60), rough=0.6)
    M["bk_rust"] = L.plain("bk_rust", srgb(172, 102, 72), rough=0.6)
    M["bk_white"] = L.plain("bk_white", srgb(236, 232, 224), rough=0.6)
    M["balc_tile"] = L.plain("balc_tile", srgb(202, 192, 174), rough=0.5)
    M["ext_white"] = L.paint("ext_white", srgb(240, 238, 232), bump=0.05)
    M["bld"] = L.building()
    M["foliage"] = L.foliage()
    M["ground"] = L.plain("ground", srgb(126, 124, 116), rough=1.0)
    M["plate"] = L.plain("plate", srgb(242, 242, 240), rough=0.3)
    M["grille"] = L.plain("grille", srgb(40, 40, 40), rough=0.6)
    M["jute"] = L.fabric("jute", srgb(198, 176, 140), weave=160.0, bump=1.0, sheen=0.1, mottle=0.12)
    M["mirror"] = L.plain("mirror", (0.92, 0.92, 0.92, 1), rough=0.0, metal=1.0)
    return M


def zone_rect(D, zid, i=0):
    return [z for z in D["zones"] if z["id"] == zid][0]["rects"][i]


def zone_level(D, x, y):
    for z in D["zones"]:
        for r in z["rects"]:
            if r[0] - 1e-3 <= x <= r[2] + 1e-3 and r[1] - 1e-3 <= y <= r[3] + 1e-3:
                return z["level"], z["id"]
    return None, None


def soffit_at(D, b):
    s = [q["soffit"] for q in D["beams"] if q["box"][0] - 2e-3 <= b[0] and q["box"][1] - 2e-3 <= b[1] and b[2] <= q["box"][2] + 2e-3 and b[3] <= q["box"][3] + 2e-3]
    return min(s) if s else D["slab"]


# ====================================================================== ΚΤΙΡΙΟ
def arch(D, M):
    slab = D["slab"]
    for w in D["walls"]:
        if w["pts"]:
            prism("w_" + w["id"], w["pts"], 0, w["top"], M["wall"])
        else:
            b = w["box"]
            mbox("w_" + w["id"], b[0], b[1], b[2], b[3], 0, w["top"], M["wall"])
    for i, c in enumerate(D["cols"]):
        if c["pts"]:
            prism("col%d" % i, c["pts"], 0, slab, M["wall"])
        else:
            b = c["box"]; mbox("col%d" % i, b[0], b[1], b[2], b[3], 0, slab, M["wall"])
    for q in D["beams"]:
        b = q["box"]; mbox("beam_" + q["id"], b[0], b[1], b[2], b[3], q["soffit"], slab + 0.2, M["wall"])
    # ποδιές / πρέκια κουφωμάτων + επένδυση του δοκαριού πάνω από τις συρόμενες (περασιά με τον τοίχο)
    z1r = zone_rect(D, "Ζ1")
    for w in D["wins"]:
        b = w["box"]
        if w["z0"] > 0.01:
            mbox("sill_" + w["name"], b[0], b[1], b[2], b[3], 0, w["z0"], M["wall"])
        top = soffit_at(D, b)
        if w["z1"] < top - 0.005:
            mbox("lint_" + w["name"], b[0], b[1], b[2], b[3], w["z1"], top, M["wall"])
        beam = [q for q in D["beams"] if q["box"][0] - 2e-3 <= b[0] and q["box"][1] - 2e-3 <= b[1] and b[2] <= q["box"][2] + 2e-3 and b[3] <= q["box"][3] + 2e-3]
        if w["name"] == "W2.01" and beam:
            mbox("hd_" + w["name"], beam[0]["box"][2], b[1], z1r[0], b[3], w["z1"], slab, M["wall"])
        if w["name"] == "W2.02" and beam:
            mbox("hd_" + w["name"], b[0], z1r[3], b[2], beam[0]["box"][1], w["z1"], slab, M["wall"])
    # οροφές (συμπαγείς ως την πλάκα – οι αλλαγές στάθμης βγαίνουν μόνες τους ως μετώπες)
    rects = [(z["id"], z["level"], r) for z in D["zones"] for r in z["rects"]]

    def free(r, side):
        for _, _, o in rects:
            if o is r:
                continue
            if side in "WE":
                edge = abs(o[2] - r[0]) < 2e-3 if side == "W" else abs(o[0] - r[2]) < 2e-3
                if edge and min(o[3], r[3]) - max(o[1], r[1]) > 0.01:
                    return False
            else:
                edge = abs(o[3] - r[1]) < 2e-3 if side == "N" else abs(o[1] - r[3]) < 2e-3
                if edge and min(o[2], r[2]) - max(o[0], r[0]) > 0.01:
                    return False
        return True
    E = 0.03
    for i, (zid, lv, r) in enumerate(rects):
        if soffit_at(D, r) <= lv + 1e-3:                             # όλη η ζώνη κάτω από δοκάρι περασιά (άνοιγμα χωλ): οροφή είναι η ίδια η κάτω παρειά του δοκαριού
            continue
        mbox("ceil_%s_%d" % (zid, i), r[0] - (E if free(r, "W") else 0), r[1] - (E if free(r, "N") else 0), r[2] + (E if free(r, "E") else 0), r[3] + (E if free(r, "S") else 0),
             lv - EPS, slab + 0.01, M["ceil"])
    # πλάκες (πάνω και κάτω)
    for i, r in enumerate(((-0.15, -0.2, 13.95, 5.15), (-0.15, 5.15, 1.3996, 5.599), (1.3996, 5.15, 9.589, 9.4494), (9.589, 5.15, 13.95, 10.2))):
        mbox("slab_top%d" % i, r[0], r[1], r[2], r[3], slab, slab + 0.2, M["ext_white"])
        mbox("slab_bot%d" % i, r[0], r[1], r[2], r[3], -0.30, -0.016, M["floor_gap"])


def floor(D, M):
    """Δρύινο δάπεδο σε σανίδες 19 × 190 cm κατά μήκος του σαλονιού (Α–Δ), με τυχαία μετάθεση ανά σειρά."""
    lv = zone_rect(D, "Ζ1"); k1 = zone_rect(D, "Ζ3", 0); k2 = zone_rect(D, "Ζ3", 1); h = zone_rect(D, "Ζ4")
    wy = [w for w in D["walls"] if w["id"] == "T2-04"][0]["box"][1]              # βόρεια παρειά του βόρειου τοίχου του σαλονιού (5,05)
    xk = [w for w in D["walls"] if w["id"] == "T6A-01"][0]["box"][2]             # 9,55
    rects = [(1.399, wy, xk, 9.45), (xk, 7.60, 13.87, 9.45), (9.589, 9.45, 12.81, 10.17), (h[0] - 0.001, h[1] - 0.10, 6.5, wy)]
    PW, PL, GP = 0.19, 1.90, 0.0007
    x_min, x_max = min(r[0] for r in rects), max(r[2] for r in rects)
    y_min, y_max = min(r[1] for r in rects), max(r[3] for r in rects)
    verts, faces, vals = [], [], []
    y = y_min
    while y < y_max:
        x = x_min - RNG.uniform(0, PL)
        while x < x_max:
            pid = RNG.random()
            bx0, bx1, by0, by1 = x + GP, x + PL - GP, y + GP, y + PW - GP
            for r in rects:
                cx0, cy0, cx1, cy1 = max(bx0, r[0]), max(by0, r[1]), min(bx1, r[2]), min(by1, r[3])
                if cx1 - cx0 > 0.004 and cy1 - cy0 > 0.004:
                    i = len(verts)
                    verts += [P(cx0, cy0, 0), P(cx1, cy0, 0), P(cx1, cy1, 0), P(cx0, cy1, 0), P(cx0, cy0, -0.004), P(cx1, cy0, -0.004), P(cx1, cy1, -0.004), P(cx0, cy1, -0.004)]
                    faces += [(i, i + 1, i + 2, i + 3), (i, i + 4, i + 5, i + 1), (i + 1, i + 5, i + 6, i + 2), (i + 2, i + 6, i + 7, i + 3), (i + 3, i + 7, i + 4, i)]
                    vals += [pid] * 5
            x += PL
        y += PW
    ob = obj_from("floor", verts, faces, M["floor"], smooth=False, group="arch")
    at = ob.data.attributes.new("plank", "FLOAT", "FACE")
    at.data.foreach_set("value", vals)
    for i, r in enumerate(rects):
        mbox("floor_base%d" % i, r[0], r[1], r[2], r[3], -0.016, -0.0035, M["floor_gap"])


def window(D, M, w, n_sash=2, small=False):
    """Κούφωμα αλουμινίου (συρόμενο επάλληλο): κάσα στη μέση του τοίχου, φύλλα σε δύο οδηγούς, τζάμι."""
    b = w["box"]; z0, z1 = w["z0"], w["z1"]
    horiz = w["ax"] == "x"
    Lw = (b[2] - b[0]) if horiz else (b[3] - b[1])
    depth = (b[3] - b[1]) if horiz else (b[2] - b[0])
    mid = (b[1] + b[3]) / 2 if horiz else (b[0] + b[2]) / 2
    a0 = b[0] if horiz else b[1]
    FW, SW = (0.04, 0.045) if small else (0.055, 0.062)
    FD = min(0.13, depth - 0.02)
    alu, gl = M["alu"], M["glass"]

    def bx(name, u0, u1, v0, v1, za, zb, mat):
        if horiz:
            mbox(name, a0 + u0, mid + v0, a0 + u1, mid + v1, za, zb, mat, group="win")
        else:
            mbox(name, mid + v0, a0 + u0, mid + v1, a0 + u1, za, zb, mat, group="win")
    nm = "win_" + w["name"]
    bx(nm + "_jl", 0, FW, -FD / 2, FD / 2, z0, z1, alu)
    bx(nm + "_jr", Lw - FW, Lw, -FD / 2, FD / 2, z0, z1, alu)
    bx(nm + "_hd", FW, Lw - FW, -FD / 2, FD / 2, z1 - FW, z1, alu)
    bx(nm + "_tr", FW, Lw - FW, -FD / 2, FD / 2, z0, z0 + (0.03 if not small else FW), alu)
    zb0 = z0 + (0.03 if not small else FW); zb1 = z1 - FW
    clear = Lw - 2 * FW
    sw = (clear + (n_sash - 1) * SW) / n_sash
    for i in range(n_sash):
        u0 = FW + i * (sw - SW); u1 = u0 + sw
        v = 0.024 if i % 2 == 0 else -0.024
        sd = 0.042
        bx("%s_s%d_l" % (nm, i), u0, u0 + SW, v - sd / 2, v + sd / 2, zb0, zb1, alu)
        bx("%s_s%d_r" % (nm, i), u1 - SW, u1, v - sd / 2, v + sd / 2, zb0, zb1, alu)
        bx("%s_s%d_t" % (nm, i), u0 + SW, u1 - SW, v - sd / 2, v + sd / 2, zb1 - SW, zb1, alu)
        bx("%s_s%d_b" % (nm, i), u0 + SW, u1 - SW, v - sd / 2, v + sd / 2, zb0, zb0 + SW * 1.15, alu)
        bx("%s_s%d_g" % (nm, i), u0 + SW, u1 - SW, v - 0.009, v + 0.009, zb0 + SW * 1.15, zb1 - SW, gl)
    return dict(horiz=horiz, a0=a0, L=Lw, mid=mid, z0=z0, z1=z1)


def door(D, M, d, entry=False):
    b = d["box"]; h = d["h"]
    horiz = (b[2] - b[0]) > (b[3] - b[1])
    top = soffit_at(D, b)
    mbox("door_hd", b[0], b[1], b[2], b[3], h, top, M["wall"])
    J, T = 0.035, 0.045 if entry else 0.04
    wh = M["white"]
    if horiz:
        ym = (b[1] + b[3]) / 2
        mbox("door_leaf", b[0] + J, ym - T / 2, b[2] - J, ym + T / 2, 0.006, h - J, wh, r=0.002, seg=1)
        mbox("door_jl", b[0], b[1], b[0] + J, b[3], 0, h, wh); mbox("door_jr", b[2] - J, b[1], b[2], b[3], 0, h, wh); mbox("door_jt", b[0] + J, b[1], b[2] - J, b[3], h - J, h, wh)
        for yy0, yy1 in ((b[1] - 0.008, b[1]), (b[3], b[3] + 0.008)):
            mbox("door_cl", b[0] - 0.045, yy0, b[0] + 0.02, yy1, 0, h + 0.045, wh); mbox("door_cr", b[2] - 0.02, yy0, b[2] + 0.045, yy1, 0, h + 0.045, wh)
            mbox("door_ct", b[0] + 0.02, yy0, b[2] - 0.02, yy1, h - 0.02, h + 0.045, wh)
        hx = b[0] + J + 0.07 if abs(d["hinge"][0] - b[2]) < abs(d["hinge"][0] - b[0]) else b[2] - J - 0.07
        for sgn in (-1, 1):
            yy = ym + sgn * (T / 2)
            tube("door_hn", [(hx, yy, 1.05), (hx, yy + sgn * 0.045, 1.05), (hx + (0.11 if hx < (b[0] + b[2]) / 2 else -0.11), yy + sgn * 0.05, 1.05)], 0.008, M["nickel"], group="arch")
    else:
        xm = (b[0] + b[2]) / 2
        mbox("door_leaf", xm - T / 2, b[1] + J, xm + T / 2, b[3] - J, 0.006, h - J, wh, r=0.002, seg=1)
        mbox("door_jl", b[0], b[1], b[2], b[1] + J, 0, h, wh); mbox("door_jr", b[0], b[3] - J, b[2], b[3], 0, h, wh); mbox("door_jt", b[0], b[1] + J, b[2], b[3] - J, h - J, h, wh)
        for xx0, xx1 in ((b[0] - 0.008, b[0]), (b[2], b[2] + 0.008)):
            mbox("door_cl", xx0, b[1] - 0.045, xx1, b[1] + 0.02, 0, h + 0.045, wh); mbox("door_cr", xx0, b[3] - 0.02, xx1, b[3] + 0.045, 0, h + 0.045, wh)
            mbox("door_ct", xx0, b[1] + 0.02, xx1, b[3] - 0.02, h - 0.02, h + 0.045, wh)
        hy = b[1] + J + 0.07 if abs(d["hinge"][1] - b[3]) < abs(d["hinge"][1] - b[1]) else b[3] - J - 0.07
        for sgn in (-1, 1):
            xx = xm + sgn * (T / 2)
            tube("door_hn", [(xx, hy, 1.05), (xx + sgn * 0.045, hy, 1.05), (xx + sgn * 0.05, hy + (0.11 if hy < (b[1] + b[3]) / 2 else -0.11), 1.05)], 0.008, M["nickel"], group="arch")


def skirting(D, M):
    lv = zone_rect(D, "Ζ1"); st = zone_rect(D, "Ζ2")
    x0, y0, x1, y1 = lv[0], lv[1], st[2], lv[3]
    H, T = 0.07, 0.012
    w1 = [w for w in D["wins"] if w["name"] == "W2.01"][0]["box"]; w2 = [w for w in D["wins"] if w["name"] == "W2.02"][0]["box"]
    hall = [z for z in D["zones"] if z["id"] == "Ζ9"][0]["rects"][0]
    ed = [d for d in D["doors"] if abs(d["box"][0] - x1) < 0.01][0]["box"]
    ko = [w for w in D["walls"] if w["id"] == "T6A-01"][0]["box"][3]
    ke = [w for w in D["walls"] if w["id"] == "T9-05"][0]["box"][2]
    sk = M["white"]
    for a, b in ((x0, hall[0]), (hall[2], x1)):
        mbox("sk_n", a, y0, b, y0 + T, 0, H, sk)
    for a, b in ((y0, ed[1] - 0.05), (ed[3] + 0.05, ko)):
        mbox("sk_e", x1 - T, a, x1, b, 0, H, sk)
    for a, b in ((x0, w2[0]), (w2[2], ke)):
        mbox("sk_s", a, y1 - T, b, y1, 0, H, sk)
    mbox("sk_w", x0, y0, x0 + T, w1[1], 0, H, sk)


def plates(D, M):
    """Πρίζες / διακόπτες / θερμοστάτες του σαλονιού και της κουζίνας στις θέσεις της μελέτης."""
    nrm = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    inside = [r for z in D["zones"] if z["id"] in ("Ζ1", "Ζ2", "Ζ3") for r in z["rects"]]

    def ok(x, y, d):
        nx, ny = nrm[d]
        px, py = x + 0.25 * nx, y + 0.25 * ny
        return any(r[0] <= px <= r[2] and r[1] <= py <= r[3] for r in inside)

    kit = [r for z in D["zones"] if z["id"] == "Ζ3" for r in z["rects"]]

    def plate(name, x, y, d, z, w, h=0.082, mat=None):
        nx, ny = nrm[d]
        if any(r[0] <= x + 0.25 * nx <= r[2] and r[1] <= y + 0.25 * ny <= r[3] for r in kit) and 0.9 < z < 1.6:     # πάνω στην πλάτη του πάγκου
            x, y = x + 0.0125 * nx, y + 0.0125 * ny
        if nx == 0:
            mbox(name, x - w / 2, y + (0 if ny > 0 else -0.009), x + w / 2, y + (0.009 if ny > 0 else 0), z - h / 2, z + h / 2, mat or M["plate"], r=0.003, seg=2, group="arch")
        else:
            mbox(name, x + (0 if nx > 0 else -0.009), y - w / 2, x + (0.009 if nx > 0 else 0), y + w / 2, z - h / 2, z + h / 2, mat or M["plate"], r=0.003, seg=2, group="arch")
    for s in D["sockets"]:
        if not s["surf"] and ok(s["x"], s["y"], s["d"]):
            plate("sock_" + s["id"], s["x"], s["y"], s["d"], s["h"], 0.082 + 0.071 * (min(s["n"], 2) - 1))
    for s in D["switches"]:
        if ok(s["x"], s["y"], s["d"]):
            plate("sw_" + s["id"], s["x"], s["y"], s["d"], 1.10, 0.082 if s["n"] <= 2 else 0.153)
    for s in D["thermostats"]:
        if ok(s["x"], s["y"], s["d"]):
            plate("th_" + s["id"], s["x"], s["y"], s["d"], 1.50, 0.086, 0.086)


def ceiling_items(D, M):
    """Ό,τι φαίνεται στην οροφή: spots (πρόταση φωτισμού), στόμια και επιστροφή της καναλάτης, θυρίδα, ανιχνευτής."""
    shown = [r for z in D["zones"] if z["id"] in SHOWN for r in z["rects"]]
    out = []
    for s in D["spots"]:
        if s["z"] is None or not any(r[0] <= s["x"] <= r[2] and r[1] <= s["y"] <= r[3] for r in shown):
            continue
        z = s["z"] - EPS
        a = rprism("spot_ring", 0.086, 0.086, 0.003, 0.043, M["plate"], re=0.001, segc=8, sege=1, group="lights"); place(a, s["x"], s["y"], z - 0.003)
        b = rprism("spot_in", 0.064, 0.064, 0.001, 0.032, M["black"], re=0.0, segc=8, group="lights"); place(b, s["x"], s["y"], z - 0.0036)
        c = rprism("spot_led", 0.040, 0.040, 0.001, 0.020, M["spot_on"], re=0.0, segc=8, group="lights"); place(c, s["x"], s["y"], z - 0.0042)
        out.append(s)
    for q in D["diffusers"]:
        r = q["rect"]
        if q["kind"] == "front":                                    # slot στη μετώπη της χαμηλής λωρίδας – φυσά οριζόντια
            xf = r[0]
            mbox("slot_" + q["id"], xf - 0.004, r[1] + 0.02, xf + 0.001, r[3] - 0.02, q["z"][0], q["z"][1], M["grille"], group="arch")
            mbox("slot_d_" + q["id"], xf - 0.006, r[1] + 0.02, xf + 0.001, r[3] - 0.02, (q["z"][0] + q["z"][1]) / 2 - 0.007, (q["z"][0] + q["z"][1]) / 2 + 0.007, M["plate"], group="arch")
            for za, zb in ((q["z"][0] - 0.012, q["z"][0]), (q["z"][1], q["z"][1] + 0.012)):
                mbox("slot_f_" + q["id"], xf - 0.006, r[1] + 0.008, xf + 0.001, r[3] - 0.008, za, zb, M["plate"], group="arch")
            for ya, yb in ((r[1] + 0.008, r[1] + 0.02), (r[3] - 0.02, r[3] - 0.008)):
                mbox("slot_f_" + q["id"], xf - 0.006, ya, xf + 0.001, yb, q["z"][0] - 0.012, q["z"][1] + 0.012, M["plate"], group="arch")
        else:                                                       # επιστροφή με περσίδες στο ταβάνι της λωρίδας
            lv, _ = zone_level(D, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
            z = lv - EPS
            mbox("ret_bg", r[0] + 0.01, r[1] + 0.01, r[2] - 0.01, r[3] - 0.01, z - 0.002, z + 0.0, M["grille"], group="arch")
            for ya, yb in ((r[1], r[1] + 0.015), (r[3] - 0.015, r[3])):
                mbox("ret_f", r[0], ya, r[2], yb, z - 0.006, z, M["plate"], group="arch")
            for xa, xb in ((r[0], r[0] + 0.015), (r[2] - 0.015, r[2])):
                mbox("ret_f", xa, r[1], xb, r[3], z - 0.006, z, M["plate"], group="arch")
            n = int((r[3] - r[1] - 0.03) / 0.022)
            for i in range(n):
                yy = r[1] + 0.015 + (i + 0.5) * (r[3] - r[1] - 0.03) / n
                mbox("ret_l", r[0] + 0.015, yy - 0.006, r[2] - 0.015, yy + 0.006, z - 0.005, z - 0.003, M["plate"], group="arch")
    for hh in D["hatches"]:
        r = hh["rect"]
        lv, zid = zone_level(D, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
        if zid not in SHOWN:
            continue
        z = lv - EPS
        for rr in ((r[0], r[1], r[2], r[1] + 0.003), (r[0], r[3] - 0.003, r[2], r[3]), (r[0], r[1], r[0] + 0.003, r[3]), (r[2] - 0.003, r[1], r[2], r[3])):
            mbox("hatch", rr[0], rr[1], rr[2], rr[3], z - 0.0006, z, M["grille"], group="arch")
    for t in D["detectors"]:
        lv, zid = zone_level(D, t["x"], t["y"])
        if zid in SHOWN:
            c = rprism("det_" + t["id"], 0.10, 0.10, 0.034, 0.05, M["plate"], re=0.008, segc=8, sege=3, group="arch"); place(c, t["x"], t["y"], lv - EPS - 0.034)
    return out


# ====================================================================== ΕΠΙΠΛΑ / ΔΙΑΚΟΣΜΗΣΗ
def furnish(D, M, K):
    sf = FU.sofa(D, M)
    ch = FU.coffee_table(D, M)
    s0 = D["sofa"]["main"]; s1 = D["sofa"]["ret"]; cf = D["coffee"]
    FU.rug(D, M, (s0[0] - 0.15, s0[3] - 0.38, s1[2] - 0.12, cf[3] + 0.85))
    tvu = [e for e in D["equip"] if e[0] == "tv"][0]
    wall_y = tvu[4]
    cx = (cf[0] + cf[2]) / 2                                        # η TV στον άξονα του τραπεζιού σαλονιού
    cx = min(max(cx, tvu[1] + 1.02), tvu[3] - 0.92)
    tv = FU.tv_unit(D, M, cx - 0.90, cx + 0.90, wall_y)
    FU.dining_table(D, M)
    FU.chairs(D, M)
    lamp = FU.floor_lamp(M, s0[0] - 0.22, s0[1] + 0.36)
    # φυτό δαπέδου στη ΝΔ γωνία, δίπλα στο έπιπλο της TV
    DC.tree("tree", M, tvu[1] + 0.27, wall_y - 0.33, 0.0, height=1.95)
    # κάδρα πάνω από τον καναπέ
    ya = zone_rect(D, "Ζ1")[1]
    cxs = (s0[0] + s0[2]) / 2 - 0.10
    DC.picture("art1", M, cxs - 0.44, 1.62, 0.70, 1.00, ya, DC.art_image("hills"))
    DC.picture("art2", M, cxs + 0.44, 1.62, 0.70, 1.00, ya, DC.art_image("arches"))
    # τραπεζάκι σαλονιού: βιβλία, μπολ, κερί
    zt = DC.books("ct_book", M, cf[0] + 0.30, (cf[1] + cf[3]) / 2 + 0.03, ch, ((0.24, 0.31, 0.028, "bk_sand"), (0.22, 0.29, 0.024, "bk_char")), rz=8)
    DC.candle("ct_candle", M, cf[0] + 0.30, (cf[1] + cf[3]) / 2 + 0.03, zt, r=0.032, h=0.07)
    DC.bowl("ct_bowl", M, cf[2] - 0.30, (cf[1] + cf[3]) / 2 - 0.04, ch, r=0.135, h=0.06, mat=M["ceramic_sand"])
    DC.books("ct_shelf", M, (cf[0] + cf[2]) / 2 + 0.05, (cf[1] + cf[3]) / 2, 0.148, ((0.26, 0.33, 0.03, "bk_white"), (0.23, 0.30, 0.025, "bk_sage"), (0.21, 0.28, 0.02, "bk_rust")), rz=92)
    # έπιπλο TV: βάζο με κλαδιά, βιβλία, φυτό
    DC.vase_branches("tv_vase", M, cx + 0.72, (tv["y0"] + tv["y1"]) / 2, tv["top"], seed=4, scale=0.95)
    DC.books("tv_book", M, cx - 0.66, (tv["y0"] + tv["y1"]) / 2 + 0.01, tv["top"], ((0.25, 0.32, 0.03, "bk_char"), (0.23, 0.30, 0.026, "bk_sand"), (0.20, 0.27, 0.02, "bk_white")), rz=96)
    # τραπεζαρία: βάζο με ευκάλυπτο στο κέντρο
    t = D["table"]
    DC.vase_branches("dt_vase", M, (t[0] + t[2]) / 2 + 0.10, (t[1] + t[3]) / 2, 0.75, seed=11, scale=1.1, mat=M["ceramic"])
    DC.bowl("dt_bowl", M, (t[0] + t[2]) / 2 - 0.42, (t[1] + t[3]) / 2 + 0.05, 0.75, r=0.12, h=0.055, mat=M["ceramic_sand"])
    # στρογγυλός καθρέπτης στον βόρειο τοίχο, δίπλα στην τραπεζαρία (ο μπουφές έφυγε – Γιάννης 26/11: «βγάλε το μπουφέ»)
    FU.mirror_round(M, (t[0] + t[2]) / 2, 1.50, 0.80, ya)
    DC.kitchen_items(M, K)
    return dict(lamp=lamp)


def curtains(D, M):
    lv = zone_rect(D, "Ζ1")
    zc = [z for z in D["zones"] if z["id"] == "Ζ1"][0]["level"]
    w1 = [w for w in D["wins"] if w["name"] == "W2.01"][0]["box"]; w2 = [w for w in D["wins"] if w["name"] == "W2.02"][0]["box"]
    xt = lv[0] + 0.095; yt = lv[3] - 0.095
    mbox("track_w", xt - 0.011, lv[1] + 0.04, xt + 0.011, lv[3] - 0.01, zc - 0.016, zc - EPS, M["white"])
    mbox("track_s", w2[0] - 0.02, yt - 0.011, w2[2] + 0.06, yt + 0.011, zc - 0.016, zc - EPS, M["white"])
    z0, z1 = 0.012, zc - 0.016
    DC.curtain("cur_w1", M, "y", w1[1] - 0.38, w1[1] + 1.30, xt, z0, z1, wave=0.115, amp=0.032, seed=1)
    DC.curtain("cur_w2", M, "y", w1[3] - 0.36, w1[3] - 0.05, xt, z0, z1, wave=0.055, amp=0.045, seed=2)
    DC.curtain("cur_s1", M, "x", w2[0] + 0.02, w2[0] + 0.40, yt, z0, z1, wave=0.055, amp=0.045, seed=3)
    DC.curtain("cur_s2", M, "x", w2[2] - 0.34, w2[2] + 0.04, yt, z0, z1, wave=0.055, amp=0.045, seed=4)


# ====================================================================== ΦΩΤΑ
MOODS = {
    #            ήλιος: ύψος, αζιμούθιο (από βορρά δεξιόστροφα), ένταση · ουρανός · έκθεση · spots (W) · φωτιστικό δαπέδου (W) · LED κουζίνας
    "day": dict(sun_el=20.0, sun_az=260.0, sun=4.2, sun_col=(1.0, 0.89, 0.76), sky=0.32, exposure=1.40, spot=14.0, lamp=10.0, led=18.0, spot_emit=10.0),
    "evening": dict(sun_el=2.5, sun_az=262.0, sun=0.0, sun_col=(1.0, 0.6, 0.4), sky=0.05, exposure=3.6, spot=10.0, lamp=9.0, led=9.0, spot_emit=5.0),
}
WARM = (1.0, 0.80, 0.58)


def lights(D, M, mood, spots, extra):
    S = MOODS[mood]
    sc = bpy.context.scene
    w = bpy.data.worlds.new("world"); sc.world = w
    try:
        if not w.node_tree:
            w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld"); bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    for st in ("MULTIPLE_SCATTERING", "NISHITA"):                   # Blender 5.x · 4.x
        try:
            sky.sky_type = st; break
        except Exception:
            continue
    sky.sun_disc = False
    sky.sun_elevation = math.radians(max(S["sun_el"], 1.0)); sky.sun_rotation = math.radians(SKY_ROT(S["sun_az"]))
    try:
        sky.aerosol_density = 1.4; sky.ozone_density = 1.2
    except Exception:
        pass
    nt.links.new(sky.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = S["sky"]
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if S["sun"] > 0:
        sun = bpy.data.lights.new("sun", "SUN"); sun.energy = S["sun"]; sun.color = S["sun_col"]; sun.angle = math.radians(1.2)
        so = bpy.data.objects.new("sun", sun); L.coll("lights").objects.link(so)
        el, az = math.radians(S["sun_el"]), math.radians(S["sun_az"])
        to_sun = Vector((math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)))
        so.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    # πύλες φωτός στα ανοίγματα (βοηθούν τη δειγματοληψία του ουρανού)
    for wn in D["wins"]:
        if wn["name"] not in ("W2.01", "W2.02", "W2.03", "W2.04"):
            continue
        b = wn["box"]; horiz = wn["ax"] == "x"
        a = bpy.data.lights.new("portal_" + wn["name"], "AREA"); a.shape = "RECTANGLE"
        a.size = (b[2] - b[0]) if horiz else (b[3] - b[1]); a.size_y = wn["z1"] - wn["z0"]
        a.cycles.is_portal = True
        o = bpy.data.objects.new("portal_" + wn["name"], a); L.coll("lights").objects.link(o)
        cx, cy, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, (wn["z0"] + wn["z1"]) / 2
        lv = zone_rect(D, "Ζ1")
        inward = Vector((0, 1, 0)) if (horiz and cy > 8) else Vector((1, 0, 0)) if (not horiz and cx < 5) else Vector((0, 1, 0)) if horiz else Vector((-1, 0, 0))
        o.location = P(cx, cy, cz)
        o.rotation_euler = inward.to_track_quat("-Z", "Y").to_euler()
    # spots οροφής
    for s in spots:
        l = bpy.data.lights.new("spot_" + s["id"], "SPOT"); l.energy = S["spot"]; l.color = WARM
        l.spot_size = math.radians(82); l.spot_blend = 0.75; l.shadow_soft_size = 0.02
        o = bpy.data.objects.new("spot_" + s["id"], l); L.coll("lights").objects.link(o)
        o.location = P(s["x"], s["y"], s["z"] - 0.02)
        d = Vector((0, 0, -1))
        if s["kind"] == "adj":                                       # ρυθμιζόμενα προς την κουρτίνα
            lv = zone_rect(D, "Ζ1")
            tw = Vector((-1, 0, 0)) if s["x"] - lv[0] <= lv[3] - s["y"] + 1e-6 else Vector((0, -1, 0))
            d = (Vector((0, 0, -1)) + tw * 0.42).normalized()
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    # φωτιστικό δαπέδου
    lx, ly, lz = extra["lamp"]
    l = bpy.data.lights.new("floor_lamp", "POINT"); l.energy = S["lamp"]; l.color = WARM; l.shadow_soft_size = 0.05
    o = bpy.data.objects.new("floor_lamp", l); L.coll("lights").objects.link(o); o.location = P(lx, ly, lz)
    return S


def SKY_ROT(az_deg):
    """Γωνία sun_rotation της υφής ουρανού για αζιμούθιο ήλιου az (από βορρά, δεξιόστροφα) – βλ. calibrate.py."""
    return az_deg


# ====================================================================== ΚΑΜΕΡΕΣ
VIEWS = {
    # όνομα: (θέση x, y, z · στόχος x, y, z · φακός mm · shift_y)
    "01_saloni_apo_eisodo": ((9.10, 6.30, 1.40), (2.6, 8.15, 1.40), 16.0, -0.07),
    "02_saloni_pros_kouzina": ((1.95, 7.75, 1.36), (9.4, 6.8, 1.36), 16.0, -0.07),
    # Γιάννης 26/11: «μην μου βγάλεις τον καναπέ μόνο του και το χωλ» → καμία λήψη μόνο του καναπέ, καμία του χωλ
    "03_trapezaria": ((5.35, 8.60, 1.36), (9.3, 6.45, 1.36), 16.5, -0.07),
    "04_kouzina": ((9.50, 8.92, 1.45), (13.6, 8.42, 1.45), 14.0, -0.06),
    "05_kouzina_pros_saloni": ((13.25, 8.78, 1.45), (8.6, 8.55, 1.45), 14.5, -0.06),
}


def camera(name, res):
    pos, tgt, lens, shy = VIEWS[name]
    cam = bpy.data.cameras.new(name); cam.lens = lens; cam.sensor_width = 36.0; cam.shift_y = shy; cam.clip_start = 0.05; cam.clip_end = 600
    o = bpy.data.objects.new(name, cam); L.coll("cams").objects.link(o)
    o.location = P(*pos)
    d = P(*tgt) - P(*pos)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = o
    return o


def render_setup(res, samples, S, device="cpu"):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.device = "CPU"
    if device == "gpu":                                             # κάρτα γραφικών (Mac: Metal · PC: OptiX / CUDA / HIP / oneAPI)
        try:
            pr = bpy.context.preferences.addons["cycles"].preferences
            for t in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):
                try:
                    pr.compute_device_type = t; break
                except Exception:
                    continue
            try:
                pr.refresh_devices()
            except Exception:
                pr.get_devices()
            for dv in pr.devices:
                dv.use = True
            c.device = "GPU"
            print("GPU:", pr.compute_device_type, [dv.name for dv in pr.devices if dv.use])
        except Exception as e:
            print("GPU δεν βρέθηκε – απόδοση με επεξεργαστή:", e)
    c.samples = samples; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.015; c.adaptive_min_samples = 64
    c.max_bounces = 10; c.diffuse_bounces = 5; c.glossy_bounces = 5; c.transmission_bounces = 8; c.transparent_max_bounces = 24
    c.caustics_reflective = False; c.caustics_refractive = False
    c.sample_clamp_indirect = 8.0; c.sample_clamp_direct = 0.0
    c.use_denoising = True
    for dn in ("OPENIMAGEDENOISE",):
        try:
            c.denoiser = dn
        except Exception as e:
            print("denoiser:", e)
    try:
        c.denoising_input_passes = "RGB_ALBEDO_NORMAL"; c.denoising_prefilter = "ACCURATE"
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.threads_mode = "AUTO"
    sc.render.film_transparent = False
    vs = sc.view_settings
    for vt in ("AgX", "Filmic", "Standard"):
        try:
            vs.view_transform = vt; break
        except Exception:
            continue
    for lk in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Base Contrast", "None"):
        try:
            vs.look = lk; break
        except Exception:
            continue
    vs.exposure = S["exposure"]; vs.gamma = 1.0
    print("view:", vs.view_transform, "| look:", vs.look, "| denoiser:", c.denoiser if c.use_denoising else "-")


def build(mood="day"):
    D = json.load(open(os.path.join(HERE, "scene.json"), encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    S = MOODS[mood]
    M["led"] = L.emit("led", (WARM[0], WARM[1], WARM[2], 1), S["led"])
    M["spot_on"] = L.emit("spot_on", (WARM[0], WARM[1], WARM[2], 1), S["spot_emit"])
    arch(D, M)
    floor(D, M)
    for w in D["wins"]:
        if w["name"] in ("W2.01", "W2.02"):
            window(D, M, w)
        elif w["name"] in ("W2.03", "W2.04"):
            window(D, M, w, small=True)
    for d in D["doors"]:
        door(D, M, d, entry=abs(d["box"][0] - zone_rect(D, "Ζ2")[2]) < 0.01)
    skirting(D, M)
    plates(D, M)
    spots = ceiling_items(D, M)
    K = KT.build(D, M, ceil=[z for z in D["zones"] if z["id"] == "Ζ3"][0]["level"])
    extra = furnish(D, M, K)
    curtains(D, M)
    EX.build(D, M)
    lights(D, M, mood, spots, extra)
    return D, M, S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--views", default="all")
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", type=int, default=400)
    ap.add_argument("--mood", default="day")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--blend", default="")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--device", default="cpu", choices=("cpu", "gpu"))
    ap.add_argument("--format", default="png", choices=("png", "jpg"))
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])     # και μέσα από το Blender: blender -b -P scene.py -- …
    res = tuple(int(v) for v in a.res.split("x"))
    t0 = time.time()
    D, M, S = build(a.mood)
    render_setup(res, a.samples, S, a.device)
    print("σκηνή: %d αντικείμενα · %.1f s" % (len(bpy.data.objects), time.time() - t0))
    if a.blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.blend))
    os.makedirs(a.out, exist_ok=True)
    names = list(VIEWS) if a.views == "all" else [n for n in VIEWS if any(n.startswith(v) or v in n for v in a.views.split(","))]
    sc = bpy.context.scene
    for n in names:
        camera(n, res)
        if a.format == "jpg":                                       # κατευθείαν το τελικό αρχείο με το ελληνικό του όνομα
            from names import NAMES
            sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 95
            sc.render.filepath = os.path.join(a.out, NAMES.get(n, n) + a.suffix + ".jpg")
        else:
            sc.render.image_settings.file_format = "PNG"
            sc.render.filepath = os.path.join(a.out, n + a.suffix + ".png")
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("ΕΙΚΟΝΑ %s: %.0f s → %s" % (n, time.time() - t1, sc.render.filepath), flush=True)


if __name__ == "__main__":
    main()
