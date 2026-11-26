"""ΠΑΡΟΥΣΙΑΣΗ 3D – ΣΑΛΟΝΙ / ΚΟΥΖΙΝΑ τυπικού ορόφου (Β1): φωτορεαλιστικές εικόνες για παρουσίαση σε πελάτες (Blender Cycles).

    python3 export_scene.py                         → scene.json (γεωμετρία από τα μοντέλα των τευχών – τοιχοποιίες, ανόψεις, ηλεκτρολογικά + πρόταση R18)
    <python με bpy> scene.py --views all --res 1920x1080 --samples 400 --out <φάκελος>

Το κτίριο (τοίχοι, κολόνες, δοκάρια, στάθμες οροφής, κουφώματα, κουζίνα, θέσεις επίπλων, φώτα, διακόπτες / πρίζες) διαβάζεται από το scene.json.
Έπιπλα, υφάσματα, διακοσμητικά, φυτά, κουρτίνες, ό,τι φαίνεται έξω από τα τζάμια: ΕΝΔΕΙΚΤΙΚΑ (ύφος παρουσίασης – δεν είναι μέρος της μελέτης).

ΥΦΟΣ (Γιάννης 26/11/2026: «πολύ παιδικά … πιο ζεστά … ξύλο δρύινο … σαν τα render του ISV … cosy … 7000/μέτρο» · «φαρδιά σανίδα»): ζεστός μινιμαλισμός –
φυσική δρυς σε φαρδιά σανίδα, καπλαμάς δρυός, τραβερτίνης, κρεμ μπουκλέ, λινά, δέρμα κονιάκ, μπρούντζος, ήλιος απογεύματος.
Πραγματικές υφές / ουρανός / μοντέλα φυτών από την αποθήκη (assets.py · fetch_assets.py)· αν λείπουν, η σκηνή βγαίνει με τα απλά υπολογιστικά υλικά."""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import assets as A
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
    pbr = L.pbr
    M["wall"] = pbr("wall", "white_stucco", color=(240, 234, 224), size=2.0, rough=0.9, bump=0.10, bump_dist=0.004, vary=False, tex_mix=0.30,
                    fallback=lambda: L.paint("wall", srgb(240, 234, 224)))
    M["ceil"] = L.paint("ceil", srgb(248, 246, 241), bump=0.012)
    M["white"] = L.plain("white_lacq", srgb(240, 235, 226), rough=0.42)
    M["carcass"] = L.plain("carcass", srgb(46, 40, 35), rough=0.6)
    # δρυς: φυσική (καπλαμάς επίπλων / κουζίνας) · σκούρα καπνιστή (τραπέζι, λεπτομέρειες)
    M["oak"] = {a: pbr("oak_" + a, "oak_veneer_05", color=(188, 150, 108), proj="grain", axis=a, rough_mul=0.95, bump=0.25, bump_dist=0.0008,
                       fallback=(lambda a=a: L.wood("oak_" + a, a, c_dark=(160, 124, 86), c_light=(202, 168, 126)))) for a in "XYZ"}
    M["oak_dark"] = {a: pbr("oakd_" + a, "oak_veneer_01", color=(86, 62, 44), proj="grain", axis=a, rough_mul=0.9, bump=0.3, bump_dist=0.0008, size=1.3,
                            fallback=(lambda a=a: L.wood("oakd_" + a, a, c_dark=(62, 44, 32), c_light=(104, 78, 56)))) for a in "XYZ"}
    # δάπεδο: φυσική δρυς σε ΦΑΡΔΙΑ σανίδα, ματ λάδι – άλλα νερά και ελαφρά άλλος τόνος σε κάθε σανίδα
    M["floor"] = pbr("oak_floor", "oak_veneer_01", color=(192, 158, 118), proj="grain", axis="X", rough_mul=0.9, bump=0.35, bump_dist=0.0008, attr="plank", tone_var=0.10,
                     sat=0.92, fallback=lambda: L.wood("oak_floor", "X", c_dark=(170, 136, 98), c_light=(206, 176, 136), rough=0.4, attr="plank", tone_var=0.075, scale=0.8))
    M["floor_gap"] = L.plain("floor_gap", srgb(58, 42, 30), rough=0.85)
    M["quartz"] = L.travertine("k_stone", color=(224, 212, 192), dark=(202, 186, 162), rough=0.30, axis="X", pits=0.25)      # πάγκος / πλάτη κουζίνας
    M["travertine"] = L.travertine("travertine", color=(218, 204, 182), dark=(190, 172, 146), rough=0.40, axis="X")
    M["travertine_z"] = L.travertine("travertine_z", color=(218, 204, 182), dark=(190, 172, 146), rough=0.40, axis="Z")
    M["black"] = L.plain("black", srgb(28, 27, 26), rough=0.42)
    M["black_glass"] = L.plain("black_glass", srgb(12, 12, 13), rough=0.06)
    M["screen"] = L.plain("screen", srgb(9, 9, 10), rough=0.13)
    M["display"] = L.emit("display", (1.0, 0.85, 0.6, 1), 0.4)
    M["bronze"] = L.plain("bronze", (0.48, 0.36, 0.22, 1), rough=0.30, metal=1.0)
    M["tap"] = M["bronze"]
    M["nickel"] = M["bronze"]
    M["steel"] = L.plain("steel", (0.62, 0.62, 0.62, 1), rough=0.32, metal=1.0)
    M["alu"] = L.plain("alu_bronze", srgb(52, 46, 40), rough=0.45, metal=0.55)
    M["glass"] = L.glass()
    M["glass_clear"] = L.glass("glass_clear", view=(0.9, 0.93, 0.92, 1.0))
    M["sheer"] = L.sheer(color=(0.96, 0.94, 0.89, 1.0), opacity=0.60)
    # υφάσματα
    M["sofa"] = pbr("sofa", "curly_teddy_natural", color=(226, 216, 198), bump=1.0, bump_dist=0.005, sheen=0.35, vary=False,
                    fallback=lambda: L.fabric("sofa", srgb(226, 216, 198), weave=520.0, bump=0.35, sheen=0.4, boucle=True))
    M["rug"] = pbr("rug", "poly_wool_herringbone", color=(224, 214, 196), size=0.62, bump=1.0, bump_dist=0.006, sheen=0.4, vary=False,
                   fallback=lambda: L.fabric("rug", srgb(224, 214, 196), weave=240.0, bump=0.9, sheen=0.5, boucle=True, mottle=0.10))
    M["chair"] = pbr("chair", "rough_linen", color=(212, 201, 182), bump=0.8, bump_dist=0.002, sheen=0.3, vary=False,
                     fallback=lambda: L.fabric("chair", srgb(212, 201, 182), weave=520.0, bump=0.4))
    M["drape"] = pbr("drape", "rough_linen", color=(204, 192, 172), size=0.4, bump=0.8, bump_dist=0.002, sheen=0.3, vary=False,
                     fallback=lambda: L.fabric("drape", srgb(204, 192, 172), weave=420.0, bump=0.4))
    M["p_olive"] = pbr("p_olive", "velour_velvet", color=(98, 100, 72), bump=0.6, sheen=0.7, vary=False, fallback=lambda: L.fabric("p_olive", srgb(98, 100, 72), weave=600.0, bump=0.3))
    M["p_cream"] = pbr("p_cream", "curly_teddy_natural", color=(238, 230, 214), bump=1.0, bump_dist=0.005, sheen=0.35, size=0.26, vary=False,
                       fallback=lambda: L.fabric("p_cream", srgb(238, 230, 214), weave=420.0, bump=0.5, boucle=True))
    M["p_caramel"] = pbr("p_caramel", "hessian_230", color=(158, 110, 76), bump=0.8, sheen=0.3, vary=False, fallback=lambda: L.fabric("p_caramel", srgb(158, 110, 76), weave=500.0, bump=0.4))
    M["p_taupe"] = pbr("p_taupe", "rough_linen", color=(146, 130, 112), bump=0.8, sheen=0.3, vary=False, fallback=lambda: L.fabric("p_taupe", srgb(146, 130, 112), weave=600.0, bump=0.3))
    M["throw"] = pbr("throw", "hessian_230", color=(206, 188, 160), size=0.2, bump=1.0, bump_dist=0.004, sheen=0.4, vary=False,
                     fallback=lambda: L.fabric("throw", srgb(206, 188, 160), weave=300.0, bump=0.6))
    M["shade"] = L.leaf("shade", srgb(240, 230, 208), srgb(236, 226, 204), rough=0.85, trans=0.6)
    M["ceramic"] = L.plain("ceramic", srgb(234, 229, 220), rough=0.35)
    M["ceramic_sand"] = L.plaster("ceramic_sand", srgb(196, 176, 150), rough=0.65)
    M["ceramic_m"] = L.plaster("ceramic_m", srgb(236, 231, 222), rough=0.7)
    M["plaster"] = L.plaster("plaster", srgb(244, 241, 235), rough=0.92)
    M["soil"] = L.plain("soil", srgb(52, 42, 34), rough=0.95)
    M["bark"] = L.plain("bark", srgb(94, 76, 60), rough=0.8)
    M["stem"] = L.plain("stem", srgb(88, 112, 70), rough=0.6)
    M["leaf"] = L.leaf("leaf", srgb(72, 92, 60), srgb(104, 122, 82))
    M["leaf2"] = L.leaf("leaf2", srgb(66, 96, 60), srgb(104, 132, 84))
    M["leaf_euca"] = L.leaf("leaf_euca", srgb(120, 142, 124), srgb(152, 168, 148), trans=0.15)
    M["grass"] = L.leaf("grass", srgb(96, 112, 70), srgb(150, 148, 98), trans=0.2)
    M["dry"] = L.plain("dry", srgb(176, 152, 112), rough=0.8)
    M["dry_plume"] = L.leaf("dry_plume", srgb(222, 204, 170), srgb(198, 176, 138), rough=0.9, trans=0.35)
    M["paper"] = L.plain("paper", srgb(240, 235, 226), rough=0.85)
    M["wax"] = L.plain("wax", srgb(240, 234, 220), rough=0.5)
    M["lemon"] = L.plain("lemon", srgb(222, 186, 70), rough=0.5)
    M["amber"] = L.plain("amber", srgb(118, 72, 34), rough=0.12)
    M["bk_sand"] = L.plain("bk_sand", srgb(206, 190, 160), rough=0.7)
    M["bk_olive"] = L.plain("bk_olive", srgb(112, 114, 88), rough=0.7)
    M["bk_char"] = L.plain("bk_char", srgb(52, 50, 48), rough=0.7)
    M["bk_umber"] = L.plain("bk_umber", srgb(128, 92, 66), rough=0.7)
    M["bk_white"] = L.plain("bk_white", srgb(236, 231, 222), rough=0.7)
    M["balc_tile"] = L.plain("balc_tile", srgb(204, 194, 176), rough=0.55)
    M["ext_white"] = L.paint("ext_white", srgb(240, 236, 228), bump=0.05)
    M["bld"] = L.building()
    M["foliage"] = L.foliage()
    M["ground"] = L.plain("ground", srgb(104, 108, 88), rough=1.0)
    M["plate"] = L.plain("plate", srgb(242, 240, 236), rough=0.3)
    M["grille"] = L.plain("grille", srgb(40, 40, 40), rough=0.6)
    # κουζίνα: κάτω ντουλάπια ζεστό γκρεζ ματ · επάνω + στήλη ψυγείου καπλαμάς δρυός · μπάζα σκούρα
    M["k_low"] = L.plain("k_low", srgb(184, 174, 158), rough=0.5)
    M["k_up"] = M["oak"]["Z"]
    M["k_plinth"] = L.plain("k_plinth", srgb(50, 44, 39), rough=0.55)
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
    """Δρύινο δάπεδο σε ΦΑΡΔΙΑ σανίδα 24 × 220 cm (Γιάννης 26/11: «φαρδιά σανίδα») κατά μήκος του σαλονιού (Α–Δ), με τυχαία μετάθεση ανά σειρά."""
    lv = zone_rect(D, "Ζ1"); k1 = zone_rect(D, "Ζ3", 0); k2 = zone_rect(D, "Ζ3", 1); h = zone_rect(D, "Ζ4")
    wy = [w for w in D["walls"] if w["id"] == "T2-04"][0]["box"][1]              # βόρεια παρειά του βόρειου τοίχου του σαλονιού (5,05)
    xk = [w for w in D["walls"] if w["id"] == "T6A-01"][0]["box"][2]             # 9,55
    rects = [(1.399, wy, xk, 9.45), (xk, 7.60, 13.87, 9.45), (9.589, 9.45, 12.81, 10.17), (h[0] - 0.001, h[1] - 0.10, 6.5, wy)]
    PW, PL, GP = 0.24, 2.20, 0.0011
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
    zc = [z for z in D["zones"] if z["id"] == "Ζ1"][0]["level"]
    FU.sofa(D, M)
    ch = FU.coffee_table(D, M)
    s0 = D["sofa"]["main"]; s1 = D["sofa"]["ret"]; cf = D["coffee"]
    FU.rug(D, M, (s0[0] - 0.10, s0[3] - 0.42, s1[2] + 0.25, cf[3] + 0.95))
    tvu = [e for e in D["equip"] if e[0] == "tv"][0]
    wall_y = tvu[4]
    xw = zone_rect(D, "Ζ1")[0]                                      # δυτικός τοίχος
    cx = (max(tvu[1], xw + 0.01) + tvu[3]) / 2                      # η TV στο κέντρο της σύνθεσης
    tv = FU.tv_wall(D, M, max(tvu[1], xw + 0.012), tvu[3] - 0.004, wall_y, zc, cx)
    FU.dining_table(D, M)
    FU.chairs(D, M)
    lamp = FU.floor_lamp(M, s0[0] - 0.22, s0[1] + 0.36)
    # πολυθρόνα (δέρμα κονιάκ) στη ΝΑ πλευρά της παρέας, γυρισμένη προς τον καναπέ + βοηθητικό
    FU.lounge_chair(M, 4.78, 8.22, rz=LOUNGE_RZ)
    hs = FU.side_table(M, 5.52, 8.62)
    DC.vase("side_vase", M, 5.50, 8.60, hs, kind=3, scale=0.62, rz=20)
    # ελιά σε γλάστρα στη ΝΔ γωνία, δίπλα στη σύνθεση της TV (μοντέλο· αλλιώς το απλό φυτό)
    tx, ty = xw + 0.42, wall_y - 0.62
    zt = DC.pot("tree_pot", tx, ty, 0.0, 0.25, 0.20, 0.46, M["ceramic_sand"], M)
    if L.model("island_tree_03", tx - 0.08, ty + 0.05, zt - 0.03, rz=TREE_RZ, scale=0.74, name="olive", group="decor", recenter=False,
               pick=lambda n: n == "island_tree_03_LOD0") is None:
        DC.tree("tree", M, tx, ty, 0.0, height=1.95)
    # πίνακας πάνω από τον καναπέ (ένας μεγάλος αφηρημένος καμβάς)
    ya = zone_rect(D, "Ζ1")[1]
    cxs = (s0[0] + s0[2]) / 2 - 0.12
    DC.picture("art1", M, cxs, 1.60, 1.70, 1.05, ya, DC.art_image("abstract"), frame_mat=M["oak"]["Z"])
    # τραπεζάκι σαλονιού: βιβλία, κερί, ξύλινο μπολ, γλαστράκι
    cmx, cmy = (cf[0] + cf[2]) / 2, (cf[1] + cf[3]) / 2
    zt = DC.books("ct_book", M, cf[0] + 0.28, cmy + 0.03, ch, ((0.25, 0.32, 0.03, "bk_sand"), (0.23, 0.30, 0.026, "bk_char"), (0.20, 0.27, 0.02, "bk_white")), rz=8)
    DC.candle("ct_candle", M, cf[0] + 0.28, cmy + 0.03, zt, r=0.034, h=0.07)
    if L.model("wooden_bowl_01", cf[2] - 0.30, cmy - 0.03, ch, rz=25, scale=0.95, name="ct_bowl", group="decor") is None:
        DC.bowl("ct_bowl", M, cf[2] - 0.30, cmy - 0.03, ch, r=0.135, h=0.06, mat=M["ceramic_sand"])
    DC.potted("ct_plant", M, cmx + 0.04, cmy + 0.12, ch, "small", rz=70)
    # έπιπλο TV: βάζα, βιβλία, πορτατίφ
    ym = (tv["y0"] + tv["y1"]) / 2
    zv = DC.vase("tv_vase", M, tv["x1"] - 0.28, ym, tv["top"], kind=2, scale=1.0, rz=30)
    DC.dry_stems("tv_stems", M, tv["x1"] - 0.28, ym, zv - 0.07, n=9, h=0.62, spread=0.5, seed=4)
    DC.vase("tv_vase2", M, tv["x1"] - 0.58, ym + 0.04, tv["top"], kind=1, scale=0.62, rz=80)
    DC.books("tv_book", M, tv["x0"] + 0.62, ym + 0.01, tv["top"], ((0.25, 0.32, 0.03, "bk_char"), (0.23, 0.30, 0.026, "bk_sand"), (0.20, 0.27, 0.02, "bk_olive")), rz=96)
    tl = FU.table_lamp(M, tv["x0"] + 0.24, ym + 0.02, tv["top"])
    # τραπεζαρία: βάζο με ξερά στάχυα + μπολ
    t = D["table"]
    tcx, tcy = (t[0] + t[2]) / 2, (t[1] + t[3]) / 2
    zv = DC.vase("dt_vase", M, tcx + 0.12, tcy, 0.75, kind=2, scale=1.15, rz=10)
    DC.dry_stems("dt_stems", M, tcx + 0.12, tcy, zv - 0.08, n=12, h=0.78, spread=0.6, seed=11)
    DC.bowl("dt_bowl", M, tcx - 0.42, tcy + 0.04, 0.75, r=0.13, h=0.055, mat=M["ceramic_sand"])
    # ανάγλυφο «λευκό σε λευκό» στον βόρειο τοίχο, δίπλα στην τραπεζαρία (ο μπουφές έφυγε – Γιάννης 26/11: «βγάλε το μπουφέ»)
    DC.relief("art2", M, tcx - 0.05, 1.58, 0.84, 1.14, ya)
    DC.kitchen_items(M, K)
    return dict(lamp=lamp, tlamp=tl)


LOUNGE_RZ = 215.0          # στροφή της πολυθρόνας (μοίρες, αριστερόστροφα σε κάτοψη Blender)
TREE_RZ = 200.0


def curtains(D, M):
    """Διάφανα λινά από οροφή ως δάπεδο σε ράγα οροφής (χωρίς κουρτινόξυλο) + λινές κουρτίνες μαζεμένες στις άκρες."""
    lv = zone_rect(D, "Ζ1")
    zc = [z for z in D["zones"] if z["id"] == "Ζ1"][0]["level"]
    w1 = [w for w in D["wins"] if w["name"] == "W2.01"][0]["box"]; w2 = [w for w in D["wins"] if w["name"] == "W2.02"][0]["box"]
    xt = lv[0] + 0.10; yt = lv[3] - 0.10
    mbox("track_w", xt - 0.011, lv[1] + 0.04, xt + 0.011, lv[3] - 0.01, zc - 0.016, zc - EPS, M["white"])
    mbox("track_s", w2[0] - 0.02, yt - 0.011, w2[2] + 0.06, yt + 0.011, zc - 0.016, zc - EPS, M["white"])
    z0, z1 = 0.012, zc - 0.016
    # δυτική συρόμενη: διάφανο απλωμένο στα 2/3 (ο ήλιος του απογεύματος περνά μέσα του), μαζεμένο στο νότιο άκρο
    DC.curtain("cur_w1", M, "y", w1[1] - 0.30, w1[1] + 2.25, xt, z0, z1, wave=0.125, amp=0.034, seed=1)
    DC.curtain("cur_w2", M, "y", w1[3] - 0.34, w1[3] - 0.03, xt, z0, z1, wave=0.055, amp=0.045, seed=2)
    # νότια συρόμενη: διάφανα στα δύο άκρα, ανοιχτή στη μέση προς το πράσινο
    DC.curtain("cur_s1", M, "x", w2[0] + 0.02, w2[0] + 1.20, yt, z0, z1, wave=0.12, amp=0.034, seed=3)
    DC.curtain("cur_s2", M, "x", w2[2] - 1.05, w2[2] + 0.04, yt, z0, z1, wave=0.12, amp=0.034, seed=4)
    # λινές κουρτίνες (πιο βαριές) μαζεμένες, σε δεύτερη ράγα προς το δωμάτιο
    xd = xt + 0.075; yd = yt - 0.075
    DC.curtain("drape_w", M, "y", w1[1] - 0.34, w1[1] - 0.02, xd, z0, z1, wave=0.07, amp=0.04, mat=M["drape"], seed=7)
    DC.curtain("drape_s", M, "x", w2[2] - 0.30, w2[2] + 0.06, yd, z0, z1, wave=0.07, amp=0.04, mat=M["drape"], seed=8)


# ====================================================================== ΦΩΤΑ
MOODS = {
    # ουρανός (HDRI της αποθήκης) · αζιμούθιο ήλιου (από βορρά δεξιόστροφα) · ένταση ουρανού · πρόσθετος ζεστός ήλιος · έκθεση · spots (W) · φωτιστικά · LED
    "day": dict(hdri="qwantani_late_afternoon_puresky", sun_az=250.0, sky=1.0, sky_tint=(1.0, 0.97, 0.93), sun=3.0, sun_col=(1.0, 0.84, 0.66), sun_el=19.0,
                exposure=1.70, spot=8.0, lamp=14.0, led=10.0, led_soft=4.0, spot_emit=8.0, wb=6350.0),
    "evening": dict(hdri="table_mountain_1_puresky", sun_az=262.0, sky=0.10, sky_tint=(1.0, 0.85, 0.75), sun=0.0, sun_col=(1.0, 0.6, 0.4), sun_el=6.0,
                    exposure=2.6, spot=10.0, lamp=12.0, led=9.0, led_soft=6.0, spot_emit=5.0, wb=6500.0),
}
WARM = (1.0, 0.83, 0.64)
# θέση του ήλιου μέσα σε κάθε εικόνα ουρανού: (u = οριζόντια θέση 0…1, ύψος σε μοίρες) – μετρημένα στην ίδια την εικόνα
HDRI_SUN = {"qwantani_late_afternoon_puresky": (0.600, 19.0), "table_mountain_1_puresky": (0.636, 13.0), "autumn_field_puresky": (0.600, 29.0)}


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
    hp = A.hdri(S["hdri"])
    sun_el = S["sun_el"]
    if hp:                                                           # πραγματικός ουρανός (φωτογραφία 360°) – στρέφεται ώστε ο ήλιος να έρχεται από το αζιμούθιο sun_az
        u, sun_el = HDRI_SUN.get(S["hdri"], (0.5, S["sun_el"]))
        env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hp)
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
        alpha = (u - 0.5) * 360.0
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(HDRI_SIGN * (90.0 - alpha + S["sun_az"])))
        nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], env.inputs["Vector"])
        mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = S["sky_tint"]
        nt.links.new(env.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = S["sky"]
    else:                                                            # χωρίς αποθήκη: υπολογιστικός ουρανός
        sky = nt.nodes.new("ShaderNodeTexSky")
        for st in ("MULTIPLE_SCATTERING", "NISHITA"):               # Blender 5.x · 4.x
            try:
                sky.sky_type = st; break
            except Exception:
                continue
        sky.sun_disc = False
        sky.sun_elevation = math.radians(max(sun_el, 1.0)); sky.sun_rotation = math.radians(S["sun_az"])
        nt.links.new(sky.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.32 * S["sky"]
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    sun_e = S["sun"] if hp else max(S["sun"], 4.2 * (1 if S["sky"] > 0.5 else 0))
    if sun_e > 0:                                                    # ζεστός ήλιος απογεύματος (πάνω από τον ήλιο του ουρανού, στην ίδια διεύθυνση)
        sun = bpy.data.lights.new("sun", "SUN"); sun.energy = sun_e; sun.color = S["sun_col"]; sun.angle = math.radians(1.6)
        so = bpy.data.objects.new("sun", sun); L.coll("lights").objects.link(so)
        el, az = math.radians(sun_el), math.radians(S["sun_az"])
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
    # φωτιστικό δαπέδου + πορτατίφ (κινητά)
    for nm in ("lamp", "tlamp"):
        if extra.get(nm):
            lx, ly, lz = extra[nm]
            l = bpy.data.lights.new(nm, "POINT"); l.energy = S["lamp"] * (1.0 if nm == "lamp" else 0.55); l.color = WARM; l.shadow_soft_size = 0.05
            o = bpy.data.objects.new(nm, l); L.coll("lights").objects.link(o); o.location = P(lx, ly, lz)
    return S


HDRI_SIGN = 1.0            # φορά στροφής του κόμβου Mapping (ελεγμένη με δοκιμαστική απόδοση: η ηλιόλουστη λωρίδα στο δάπεδο δείχνει προς ΑΒΑ)


# ====================================================================== ΚΑΜΕΡΕΣ
VIEWS = {
    # όνομα: (θέση x, y, z · στόχος x, y, z · φακός mm · shift_y)
    "01_saloni_apo_eisodo": ((9.10, 6.30, 1.40), (2.6, 8.15, 1.40), 16.0, -0.07),
    "02_saloni_pros_kouzina": ((1.95, 7.75, 1.36), (9.4, 6.8, 1.36), 16.0, -0.07),
    # Γιάννης 26/11: «μην μου βγάλεις τον καναπέ μόνο του και το χωλ» → καμία λήψη μόνο του καναπέ, καμία του χωλ
    "03_trapezaria": ((5.35, 8.60, 1.36), (9.3, 6.45, 1.36), 16.5, -0.07),
    "04_kouzina": ((9.50, 8.92, 1.45), (13.6, 8.42, 1.45), 14.0, -0.06),
    "05_kouzina_pros_saloni": ((13.30, 8.70, 1.45), (8.6, 8.47, 1.45), 14.5, -0.06),
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
    try:                                                            # ζεστή ισορροπία λευκού (Blender ≥ 4.3)
        vs.use_white_balance = True; vs.white_balance_temperature = S.get("wb", 6500.0); vs.white_balance_tint = 6.0
    except Exception:
        pass
    print("view:", vs.view_transform, "| look:", vs.look, "| denoiser:", c.denoiser if c.use_denoising else "-")


def build(mood="day"):
    D = json.load(open(os.path.join(HERE, "scene.json"), encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    S = MOODS[mood]
    M["led"] = L.emit("led", (WARM[0], WARM[1], WARM[2], 1), S["led"])
    M["led_soft"] = L.emit("led_soft", (WARM[0], WARM[1], WARM[2], 1), S["led_soft"])
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
    ap.add_argument("--assets", default="", help="φάκελος-αποθήκη υφών / ουρανού / μοντέλων (βλ. fetch_assets.py)")
    ap.add_argument("--tex", default="2k"); ap.add_argument("--hdri", default="4k"); ap.add_argument("--model", default="2k")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])     # και μέσα από το Blender: blender -b -P scene.py -- …
    res = tuple(int(v) for v in a.res.split("x"))
    t0 = time.time()
    print("αποθήκη υφών:", A.configure(a.assets or None, a.tex, a.hdri, a.model))
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
