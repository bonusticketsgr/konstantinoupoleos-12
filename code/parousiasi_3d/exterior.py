"""ΠΑΡΟΥΣΙΑΣΗ 3D – ό,τι φαίνεται έξω από τις μπαλκονόπορτες: εξώστης (δάπεδο και πλάκα από το μοντέλο), γυάλινα στηθαία, ζαρντινιέρες με φυτά,
και ένα ουδέτερο φόντο (γειτονικά κτίρια, δέντρα). ΕΝΔΕΙΚΤΙΚΑ: θέση / ύψος ζαρντινιερών και στηθαίων (όπως φαίνονται στα προοπτικά του αρχιτέκτονα), όλο το φόντο."""
import math
import lib as L
from lib import mbox, prism, place, P, obj_from
import decor as DC

G = "ext"
Z_BALC = -0.02          # τελικό δάπεδο εξώστη
H_RAIL = 1.05
GROUND = -6.9           # στάθμη δρόμου κάτω από τον Β΄ όροφο


def build(D, M):
    slab = D["slab"]
    big = max(D["balconies"], key=lambda q: max(p[0] for p in q) - min(p[0] for p in q))      # ο εξώστης σαλονιού (δυτικά + νότια)
    prism("balc_floor", big, -0.30, Z_BALC, M["balc_tile"], group=G)
    prism("balc_slab", big, slab, slab + 0.20, M["ext_white"], group=G)
    xs = [p[0] for p in big]; ys = [p[1] for p in big]
    xw, ye = min(xs), max(ys)                    # δυτική ακμή (x) · νότια ακμή (y)
    yn = min(ys)                                 # βόρεια ακμή του δυτικού τμήματος
    xe = max(xs)                                 # ανατολική ακμή του νότιου τμήματος
    for i, b in enumerate(D["cols2"]):
        mbox("parapet%d" % i, b[0], b[1], b[2], b[3], -0.30, H_RAIL, M["ext_white"], group=G)
    # ζαρντινιέρες (λευκές) – νότια: μπροστά στο ανατολικό μέρος της συρόμενης · δυτικά: στο βόρειο μέρος
    PW = 0.62
    ps = (6.35, ye - PW, xe, ye)
    pw = (xw, yn, xw + PW, 7.80)
    for nm, r in (("planter_s", ps), ("planter_w", pw)):
        mbox(nm, r[0], r[1], r[2], r[3], Z_BALC, 0.92, M["ext_white"], group=G)
        mbox(nm + "_soil", r[0] + 0.07, r[1] + 0.07, r[2] - 0.07, r[3] - 0.07, 0.90, 0.925, M["soil"], group=G)
    k = 0
    x = ps[0] + 0.28
    while x < ps[2] - 0.2:
        DC.grass("grass_s%d" % k, M, x, (ps[1] + ps[3]) / 2, 0.92, n=150, h=0.62 if k % 2 else 0.5, seed=20 + k); k += 1
        x += 0.42
    y = pw[1] + 0.28
    while y < pw[3] - 0.2:
        DC.grass("grass_w%d" % k, M, (pw[0] + pw[2]) / 2, y, 0.92, n=150, h=0.6 if k % 2 else 0.48, seed=20 + k); k += 1
        y += 0.42
    # γυάλινα στηθαία με σκούρα κουπαστή
    def rail(a, b):
        (x0, y0), (x1, y1) = a, b
        horiz = abs(x1 - x0) > abs(y1 - y0)
        t = 0.008
        if horiz:
            mbox("rail_g", min(x0, x1), y0 - t, max(x0, x1), y0 + t, 0.04, H_RAIL - 0.03, M["glass_clear"], group=G)
            mbox("rail_t", min(x0, x1), y0 - 0.025, max(x0, x1), y0 + 0.025, H_RAIL - 0.03, H_RAIL, M["alu"], group=G)
            mbox("rail_b", min(x0, x1), y0 - 0.02, max(x0, x1), y0 + 0.02, Z_BALC, 0.04, M["alu"], group=G)
            n = max(1, round(abs(x1 - x0) / 1.4))
            for i in range(n + 1):
                xx = min(x0, x1) + abs(x1 - x0) * i / n
                mbox("rail_p", xx - 0.02, y0 - 0.02, xx + 0.02, y0 + 0.02, Z_BALC, H_RAIL - 0.03, M["alu"], group=G)
        else:
            mbox("rail_g", x0 - t, min(y0, y1), x0 + t, max(y0, y1), 0.04, H_RAIL - 0.03, M["glass_clear"], group=G)
            mbox("rail_t", x0 - 0.025, min(y0, y1), x0 + 0.025, max(y0, y1), H_RAIL - 0.03, H_RAIL, M["alu"], group=G)
            mbox("rail_b", x0 - 0.02, min(y0, y1), x0 + 0.02, max(y0, y1), Z_BALC, 0.04, M["alu"], group=G)
            n = max(1, round(abs(y1 - y0) / 1.4))
            for i in range(n + 1):
                yy = min(y0, y1) + abs(y1 - y0) * i / n
                mbox("rail_p", x0 - 0.02, yy - 0.02, x0 + 0.02, yy + 0.02, Z_BALC, H_RAIL - 0.03, M["alu"], group=G)
    rail((xw + 0.03, pw[3]), (xw + 0.03, ye - 0.03))
    rail((xw + 0.03, ye - 0.03), (ps[0], ye - 0.03))
    # φωτιστικά οροφής εξώστη (θέσεις του μοντέλου)
    for s in D["ext_spots"]:
        c = L.cyl("ext_lamp", 0.04, 0.04, 0.085, M["ext_white"], group=G); place(c, s["x"], s["y"], slab - 0.085)
    # φόντο: έδαφος, γειτονικά κτίρια, δέντρα (ουδέτερα – δεν είναι αποτύπωση της γειτονιάς)
    mbox("ground", -300, -300, 300, 300, GROUND - 0.5, GROUND, M["ground"], group=G)
    rnd = __import__("random").Random(11)
    blds = [(-36, -8, 14, 16, 8.2), (-40, 12, 16, 14, 9.6), (-33, 32, 15, 15, 7.4), (-13, 37, 16, 13, 8.6), (7, 39, 18, 14, 9.8), (29, 37, 16, 15, 8.0), (-64, 20, 18, 30, 13.5),
            (-16, 62, 30, 16, 13.0), (24, 64, 28, 16, 11.5), (-60, -24, 16, 22, 10.5), (52, 44, 16, 18, 12.0), (-52, 54, 18, 16, 11.0), (-90, 40, 30, 24, 15.0), (10, 92, 40, 20, 15.0)]
    for i, (bx, by, w, d, h) in enumerate(blds):
        mbox("bld%d" % i, bx, by, bx + w, by + d, GROUND, GROUND + h, M["bld"], group=G)
    for i in range(46):
        if rnd.random() < 0.5:
            tx, ty = rnd.uniform(-45, -13), rnd.uniform(-10, 40)
        else:
            tx, ty = rnd.uniform(-20, 40), rnd.uniform(22, 52)
        r = rnd.uniform(2.2, 3.4)
        zc = GROUND + rnd.uniform(1.2, 2.6)
        for k in range(11):                                          # κόμη από πολλές μικρές σφαίρες – όχι τέλεια μπάλα
            rr = r * rnd.uniform(0.32, 0.55)
            s = DC.sphere("tree%d_%d" % (i, k), rr, M["foliage"], group=G, squash=rnd.uniform(0.8, 1.1))
            place(s, tx + rnd.uniform(-0.7, 0.7) * r, ty + rnd.uniform(-0.7, 0.7) * r, zc + rnd.uniform(-0.3, 0.4) * r)
