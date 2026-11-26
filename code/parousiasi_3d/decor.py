"""ΠΑΡΟΥΣΙΑΣΗ 3D – διακοσμητικά: φυτά, κάδρα, βιβλία, βάζα, μικροαντικείμενα κουζίνας, κουρτίνες. Όλα ΕΝΔΕΙΚΤΙΚΑ (δεν είναι μέρος της μελέτης)."""
import math
import bpy
import numpy as np
from mathutils import Vector, Euler
import lib as L
from lib import mbox, lbox, place, rprism, cyl, tube, P, RNG, obj_from, srgb

G = "decor"


def lathe(name, profile, mat, seg=40, group=G):
    """Σώμα εκ περιστροφής: profile = [(r, z), ...] (τοπικό, άξονας Z). r = 0 στην αρχή / στο τέλος → κλείνει σε σημείο."""
    verts, faces, rings = [], [], []
    for r, z in profile:
        if r < 1e-6:
            rings.append([len(verts)]); verts.append((0.0, 0.0, z))
        else:
            rings.append(list(range(len(verts), len(verts) + seg)))
            verts += [(r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z) for i in range(seg)]
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                faces.append((a[0], b[i], b[j]))
            elif len(b) == 1:
                faces.append((a[i], a[j], b[0]))
            else:
                faces.append((a[i], a[j], b[j], b[i]))
    return obj_from(name, verts, faces, mat, smooth=True, group=group)


def sphere(name, r, mat, group=G, squash=1.0):
    n = 10
    prof = [(r * math.sin(math.pi * i / n), -r * squash * math.cos(math.pi * i / n)) for i in range(n + 1)]
    prof[0] = (0.0, -r * squash); prof[-1] = (0.0, r * squash)
    return lathe(name, prof, mat, seg=20, group=group)


# ------------------------------------------------------------------ φύλλα / φυτά
def _leaf(verts, faces, p, t, up, Ln, Wd, droop=0.1):
    t = t.normalized()
    s = t.cross(up)
    if s.length < 1e-4:
        s = t.cross(Vector((1, 0, 0)))
    s.normalize()
    n = s.cross(t).normalized()
    m1 = p + t * (0.35 * Ln) - n * (0.02 * Ln)
    m2 = p + t * (0.70 * Ln) - n * (droop * 0.5 * Ln)
    tip = p + t * Ln - n * (droop * Ln)
    i = len(verts)
    verts += [p, m1, m2, tip, m1 - s * (0.5 * Wd) + n * (0.12 * Wd), m1 + s * (0.5 * Wd) + n * (0.12 * Wd),
              m2 - s * (0.4 * Wd) + n * (0.10 * Wd), m2 + s * (0.4 * Wd) + n * (0.10 * Wd)]
    faces += [(i, i + 5, i + 1), (i, i + 1, i + 4), (i + 1, i + 5, i + 7, i + 2), (i + 1, i + 2, i + 6, i + 4), (i + 2, i + 7, i + 3), (i + 2, i + 3, i + 6)]


def _dir(az, el):
    return Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))


def pot(name, x, y, z, r_top, r_bot, h, mat, M):
    prof = [(0.0, 0.0), (r_bot, 0.0), (r_bot + 0.004, 0.012), (r_top, h - 0.006), (r_top, h), (r_top - 0.012, h), (r_top - 0.014, h - 0.03), (0.0, h - 0.03)]
    o = lathe(name, prof, mat, seg=36); place(o, x, y, z)
    s = rprism(name + "_soil", 2 * (r_top - 0.013), 2 * (r_top - 0.013), 0.01, r_top - 0.013, M["soil"], re=0.0, segc=8, group=G); place(s, x, y, z + h - 0.035)
    return z + h - 0.025


def tree(name, M, x, y, z=0.0, height=1.9, seed=3):
    """Φυτό δαπέδου (τύπου φίκου / ελιάς εσωτερικού χώρου) σε γλάστρα."""
    rnd = __import__("random").Random(seed)
    zt = pot(name + "_pot", x, y, z, 0.20, 0.155, 0.36, M["ceramic"], M)
    base = P(x, y, zt)
    # κορμός
    tr = [base + Vector((0, 0, 0))]
    cur = base.copy()
    for i in range(6):
        cur = cur + Vector((rnd.uniform(-0.025, 0.025), rnd.uniform(-0.025, 0.025), (height * 0.50) / 6))
        tr.append(cur.copy())
    tube(name + "_trunk", [(p.x, -p.y, p.z) for p in tr], 0.015, M["bark"], group=G)
    verts, faces = [], []
    up = Vector((0, 0, 1))
    nb = 9
    for b in range(nb):
        t = 0.45 + 0.55 * b / (nb - 1)
        k = t * (len(tr) - 1); i0 = min(int(k), len(tr) - 2)
        st = tr[i0].lerp(tr[i0 + 1], k - i0)
        az = b * 2.399 + rnd.uniform(-0.3, 0.3)
        el = math.radians(rnd.uniform(38, 70) if b < nb - 1 else 85)
        ln = rnd.uniform(0.42, 0.70) * (height / 1.9)
        d = _dir(az, el)
        pts = [st + d * (ln * s) + up * (0.10 * ln * s * s) for s in (0, 0.33, 0.66, 1.0)]
        tube(name + "_br%d" % b, [(p.x, -p.y, p.z) for p in pts], 0.0055, M["bark"], group=G, bevel_res=2)
        twigs = [(pts, 0.25)]
        for q in range(3):
            s0 = rnd.uniform(0.35, 0.8)
            a = pts[1].lerp(pts[3], s0)
            d2 = _dir(az + rnd.uniform(-1.3, 1.3), math.radians(rnd.uniform(20, 65)))
            l2 = ln * rnd.uniform(0.35, 0.55)
            tw = [a + d2 * (l2 * s) for s in (0, 0.5, 1.0)]
            tube(name + "_tw%d_%d" % (b, q), [(p.x, -p.y, p.z) for p in tw], 0.003, M["bark"], group=G, bevel_res=1)
            twigs.append((tw, 0.1))
        for tw, s_start in twigs:
            n = max(4, int(sum((tw[i + 1] - tw[i]).length for i in range(len(tw) - 1)) / 0.032))
            for j in range(n):
                s = s_start + (1 - s_start) * (j + rnd.random() * 0.6) / n
                k = min(s, 0.999) * (len(tw) - 1); i0 = int(k)
                p = tw[i0].lerp(tw[i0 + 1], k - i0)
                ax = (tw[i0 + 1] - tw[i0]).normalized()
                side = ax.cross(up)
                if side.length < 1e-3:
                    side = Vector((1, 0, 0))
                side.normalize()
                ang = rnd.uniform(0, 2 * math.pi)
                out = (side * math.cos(ang) + ax.cross(side) * math.sin(ang))
                t = (ax * rnd.uniform(0.3, 0.9) + out * rnd.uniform(0.6, 1.0) + up * rnd.uniform(-0.25, 0.15))
                _leaf(verts, faces, p, t, up, rnd.uniform(0.075, 0.115), rnd.uniform(0.032, 0.046), droop=rnd.uniform(0.05, 0.25))
    obj_from(name + "_leaves", verts, faces, M["leaf"], smooth=True, group=G, fix_normals=False)


def small_plant(name, M, x, y, z, r=0.085, h=0.13, n=22, size=0.17, seed=5, potmat=None):
    rnd = __import__("random").Random(seed)
    zt = pot(name + "_pot", x, y, z, r, r * 0.8, h, potmat or M["ceramic"], M)
    base = P(x, y, zt)
    verts, faces = [], []
    up = Vector((0, 0, 1))
    for i in range(n):
        az = i * 2.399 + rnd.uniform(-0.3, 0.3)
        el = math.radians(rnd.uniform(25, 80))
        d = _dir(az, el)
        st = base + Vector((d.x, d.y, 0)) * rnd.uniform(0.0, r * 0.5)
        ln = rnd.uniform(0.35, 0.9) * size
        stem = [st, st + d * (ln * 0.5) + up * 0.01, st + d * ln]
        tube(name + "_st%d" % i, [(p.x, -p.y, p.z) for p in stem], 0.0022, M["stem"], group=G, bevel_res=1)
        _leaf(verts, faces, stem[2], d * 0.8 + Vector((d.x, d.y, 0)) * 0.6 - up * 0.1, up, rnd.uniform(0.6, 1.0) * size * 0.75, rnd.uniform(0.45, 0.6) * size * 0.55, droop=rnd.uniform(0.15, 0.4))
    obj_from(name + "_leaves", verts, faces, M["leaf2"], smooth=True, group=G, fix_normals=False)


def vase_branches(name, M, x, y, z, seed=8, scale=1.0, mat=None):
    rnd = __import__("random").Random(seed)
    s = scale
    prof = [(0.0, 0.0), (0.05 * s, 0.0), (0.078 * s, 0.035 * s), (0.092 * s, 0.10 * s), (0.08 * s, 0.17 * s), (0.045 * s, 0.225 * s), (0.036 * s, 0.26 * s), (0.043 * s, 0.275 * s),
            (0.034 * s, 0.272 * s), (0.03 * s, 0.24 * s), (0.0, 0.235 * s)]
    v = lathe(name, prof, mat or M["ceramic_sand"], seg=40); place(v, x, y, z)
    base = P(x, y, z + 0.25 * s)
    verts, faces = [], []
    up = Vector((0, 0, 1))
    for b in range(6):
        az = b * 2.399 + rnd.uniform(-0.4, 0.4)
        el = math.radians(rnd.uniform(62, 84))
        ln = rnd.uniform(0.38, 0.62) * s
        d = _dir(az, el)
        pts = [base + d * (ln * q) + Vector((d.x, d.y, 0)) * (0.10 * ln * q * q) for q in (0, 0.3, 0.65, 1.0)]
        tube(name + "_b%d" % b, [(p.x, -p.y, p.z) for p in pts], 0.0022, M["bark"], group=G, bevel_res=1)
        for j in range(12):
            q = 0.25 + 0.75 * j / 12
            k = q * 2.999; i0 = int(k)
            p = pts[i0].lerp(pts[i0 + 1], k - i0)
            ax = (pts[i0 + 1] - pts[i0]).normalized()
            side = ax.cross(up).normalized() if ax.cross(up).length > 1e-3 else Vector((1, 0, 0))
            sgn = 1 if j % 2 else -1
            t = side * sgn * 0.9 + ax * 0.35 + up * 0.1
            _leaf(verts, faces, p, t, up, rnd.uniform(0.035, 0.05) * s, rnd.uniform(0.03, 0.04) * s, droop=0.05)
    obj_from(name + "_leaves", verts, faces, M["leaf_euca"], smooth=True, group=G, fix_normals=False)


def grass(name, M, x, y, z, n=140, h=0.55, spread=0.10, seed=1):
    """Καλλωπιστικό αγρωστώδες για τις ζαρντινιέρες των εξωστών."""
    rnd = __import__("random").Random(seed)
    verts, faces = [], []
    base = P(x, y, z)
    for b in range(n):
        az = rnd.uniform(0, 2 * math.pi)
        o = base + Vector((math.cos(az), math.sin(az), 0)) * rnd.uniform(0, spread)
        ln = h * rnd.uniform(0.55, 1.1)
        el0 = math.radians(rnd.uniform(60, 88)); bend = rnd.uniform(0.6, 1.5)
        w = rnd.uniform(0.008, 0.014)
        side = Vector((-math.sin(az), math.cos(az), 0))
        p = o.copy(); i0 = len(verts); ns = 6
        for sgm in range(ns + 1):
            s = sgm / ns
            ww = w * (1 - s) ** 0.7
            verts += [p - side * ww, p + side * ww]
            el = el0 - bend * s * s
            p = p + _dir(az, el) * (ln / ns)
        for sgm in range(ns):
            a = i0 + 2 * sgm
            faces.append((a, a + 1, a + 3, a + 2))
    return obj_from(name, verts, faces, M["grass"], smooth=True, group="ext", fix_normals=False)


# ------------------------------------------------------------------ κάδρα
def _fbm(rs, H, W, base, octaves=5):
    """Μαλακός θόρυβος (άθροισμα παρεμβεβλημένων τυχαίων πλεγμάτων) 0..1."""
    out = np.zeros((H, W), np.float32); amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = rs.rand(n + 2, int(n * W / H) + 2).astype(np.float32)
        yy = np.linspace(0, n, H, endpoint=False); xx = np.linspace(0, g.shape[1] - 2, W, endpoint=False)
        y0 = yy.astype(int); x0 = xx.astype(int); fy = (yy - y0)[:, None]; fx = (xx - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        v = (g[y0][:, x0] * (1 - fy) * (1 - fx) + g[y0 + 1][:, x0] * fy * (1 - fx) + g[y0][:, x0 + 1] * (1 - fy) * fx + g[y0 + 1][:, x0 + 1] * fy * fx)
        out += v * amp; tot += amp; amp *= 0.5
    return out / tot


def art_image(kind="abstract", W=1100, H=700, seed=7):
    """Αφηρημένος πίνακας σε ζεστούς ουδέτερους τόνους (λευκό του λινού, άμμος, τοπ, κάρβουνο, λίγη ώχρα) – σαν τοπίο από στρώσεις."""
    rs = np.random.RandomState(seed)
    v, u = np.mgrid[0:H, 0:W].astype(np.float32)
    u /= W; v /= H                                       # v = 0 κάτω
    linen, sand, taupe, umber, coal, ochre = (0.93, 0.905, 0.86), (0.80, 0.72, 0.60), (0.58, 0.51, 0.43), (0.36, 0.29, 0.23), (0.17, 0.16, 0.15), (0.72, 0.53, 0.26)
    img = np.ones((H, W, 3), np.float32) * np.array(linen, np.float32)
    n1 = _fbm(rs, H, W, 3); n2 = _fbm(rs, H, W, 6); n3 = _fbm(rs, H, W, 14); n4 = _fbm(rs, H, W, 2)

    def layer(mask, col, k=1.0):
        m = np.clip(mask, 0, 1)[..., None] * k
        img[:] = img * (1 - m) + np.array(col, np.float32) * m
    layer((n4 - 0.42) * 2.2 * (v > 0.5), (0.88, 0.85, 0.80), 0.7)                       # αχνά «σύννεφα» επάνω
    h1 = 0.46 + 0.16 * (n1 - 0.5)                                                       # πλατιά ζώνη άμμου
    layer((h1 - v) * 14 + (n3 - 0.5) * 1.6, sand, 0.92)
    h2 = 0.36 + 0.20 * (n2 - 0.5)
    layer((h2 - v) * 18 + (n3 - 0.5) * 2.2, taupe, 0.85)
    band = np.exp(-((v - (0.40 + 0.10 * (n1 - 0.5))) / 0.035) ** 2)                     # σκούρα «γραμμή ορίζοντα», σπασμένη
    layer(band * (n2 > 0.47) * 1.3 + (n3 - 0.62) * 2, umber, 0.9)
    h3 = 0.17 + 0.16 * (n2 - 0.5)
    layer((h3 - v) * 16 + (n3 - 0.5) * 2.0, coal, 0.88)
    gl = np.exp(-((v - (0.52 + 0.05 * (n2 - 0.5))) / 0.008) ** 2) * (u > 0.18) * (u < 0.74) * (n3 > 0.42)
    layer(gl, ochre, 0.85)                                                              # λεπτή χρυσή γραμμή
    img *= (0.94 + 0.12 * _fbm(rs, H, W, 40, 3))[..., None]                             # πινελιά / καμβάς
    img += (rs.rand(H, W, 1).astype(np.float32) - 0.5) * 0.025
    img = np.clip(img, 0, 1)
    rgba = np.concatenate([img, np.ones((H, W, 1), np.float32)], axis=2)
    im = bpy.data.images.new("art_" + kind + str(seed), W, H, alpha=False)
    im.pixels.foreach_set(rgba.ravel())
    im.pack()
    return im


def relief(name, M, cx, zc, w, h, wall_y, seed=3):
    """Ανάγλυφο «λευκό σε λευκό» (γύψινο) σε λεπτή δρύινη κορνίζα, σε τοίχο που κοιτά νότια."""
    rnd = __import__("random").Random(seed)
    fm = M["oak"]["Z"]
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, zc - h / 2, zc + h / 2
    bd, d = 0.018, 0.05
    mbox(name + "_fl", x0, wall_y, x0 + bd, wall_y + d, z0, z1, fm, r=0.002, seg=1, group=G)
    mbox(name + "_fr", x1 - bd, wall_y, x1, wall_y + d, z0, z1, fm, r=0.002, seg=1, group=G)
    mbox(name + "_ft", x0 + bd, wall_y, x1 - bd, wall_y + d, z1 - bd, z1, M["oak"]["X"], r=0.002, seg=1, group=G)
    mbox(name + "_fb", x0 + bd, wall_y, x1 - bd, wall_y + d, z0, z0 + bd, M["oak"]["X"], r=0.002, seg=1, group=G)
    pl = M["plaster"]
    yb = wall_y + 0.018
    mbox(name + "_bg", x0 + bd, wall_y, x1 - bd, yb, z0 + bd, z1 - bd, pl, group=G)
    # ομόκεντρα τόξα που «ανατέλλουν» από κάτω + κατακόρυφες ραβδώσεις
    ax, az = cx + 0.06 * w, z0 + bd + 0.30 * h
    for k in range(6):
        R = (0.10 + 0.085 * k) * w * 1.25
        pts = []
        for i in range(25):
            a = math.pi * i / 24
            px, pz = ax + R * math.cos(a), az + R * math.sin(a) * 0.95
            if x0 + bd + 0.03 < px < x1 - bd - 0.03 and pz < z1 - bd - 0.03:
                pts.append((px, yb + 0.004, pz))
        if len(pts) > 3:
            tube(name + "_arc%d" % k, pts, 0.011, pl, group=G, res=10, bevel_res=4)
    n = 9
    for i in range(n):
        px = x0 + bd + 0.06 + (w - 2 * bd - 0.12) * i / (n - 1)
        hh = (0.10 + 0.14 * rnd.random()) * h
        tube(name + "_rib%d" % i, [(px, yb + 0.004, z0 + bd + 0.035), (px, yb + 0.004, z0 + bd + 0.035 + hh)], 0.010, pl, group=G, bevel_res=4)


def picture(name, M, cx, zc, w, h, wall_y, img, frame_mat=None, border=0.014, mat_w=0.012):
    """Κάδρο σε τοίχο που κοιτά νότια (βόρειος τοίχος χώρου), κέντρο (cx, zc)."""
    fm = frame_mat or M["oak"]["Z"]
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, zc - h / 2, zc + h / 2
    d = 0.045
    mbox(name + "_fl", x0, wall_y, x0 + border, wall_y + d, z0, z1, fm, r=0.002, seg=1, group=G)
    mbox(name + "_fr", x1 - border, wall_y, x1, wall_y + d, z0, z1, fm, r=0.002, seg=1, group=G)
    mbox(name + "_ft", x0 + border, wall_y, x1 - border, wall_y + d, z1 - border, z1, M["oak"]["X"] if frame_mat is None else fm, r=0.002, seg=1, group=G)
    mbox(name + "_fb", x0 + border, wall_y, x1 - border, wall_y + d, z0, z0 + border, M["oak"]["X"] if frame_mat is None else fm, r=0.002, seg=1, group=G)
    mbox(name + "_mat", x0 + border, wall_y, x1 - border, wall_y + 0.012, z0 + border, z1 - border, M["black"], group=G)
    ix0, ix1, iz0, iz1 = x0 + border + mat_w, x1 - border - mat_w, z0 + border + mat_w, z1 - border - mat_w
    mbox(name + "_cv", ix0, wall_y + 0.012, ix1, wall_y + 0.034, iz0, iz1, M["paper"], group=G)
    yy = wall_y + 0.0345
    me = bpy.data.meshes.new(name + "_img")
    me.from_pydata([tuple(P(ix0, yy, iz0)), tuple(P(ix1, yy, iz0)), tuple(P(ix1, yy, iz1)), tuple(P(ix0, yy, iz1))], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for li, uv in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uvl.data[li].uv = uv
    me.materials.append(L.image_mat(name + "_m", img, rough=0.85))
    ob = bpy.data.objects.new(name + "_img", me)
    L.coll(G).objects.link(ob)


# ------------------------------------------------------------------ μικροαντικείμενα
def book(name, M, x, y, z, w, d, t, cover, rz=0.0):
    parts = []
    pg = lbox(name + "_pg", w - 0.008, d - 0.006, t - 0.006, M["paper"], group=G); pg.location = Vector((0.002, 0, t / 2)); parts.append(pg)
    for zz in (0.0015, t - 0.0015):
        c = lbox(name + "_c", w, d, 0.003, cover, group=G); c.location = Vector((0, 0, zz)); parts.append(c)
    sp = lbox(name + "_sp", 0.003, d, t, cover, group=G); sp.location = Vector((-w / 2 + 0.0015, 0, t / 2)); parts.append(sp)
    e = L.parent_all(name, parts, group=G)
    e.location = P(x, y, z); e.rotation_euler = Euler((0, 0, math.radians(rz)))
    return z + t


def books(name, M, x, y, z, covers, rz=0.0):
    for i, (w, d, t, mk) in enumerate(covers):
        z = book("%s%d" % (name, i), M, x + RNG.uniform(-0.008, 0.008), y + RNG.uniform(-0.008, 0.008), z, w, d, t, M[mk], rz + RNG.uniform(-6, 6))
    return z


def bowl(name, M, x, y, z, r=0.13, h=0.07, mat=None):
    prof = [(0.0, 0.0), (r * 0.45, 0.0), (r * 0.85, h * 0.45), (r, h), (r - 0.006, h), (r * 0.82, h * 0.5), (r * 0.42, 0.012), (0.0, 0.012)]
    o = lathe(name, prof, mat or M["ceramic"], seg=40); place(o, x, y, z)
    return z + 0.012


def candle(name, M, x, y, z, r=0.035, h=0.09):
    c = cyl(name, r, r, h, M["wax"], re=0.004, group=G); place(c, x, y, z)
    tube(name + "_w", [(x, y, z + h), (x, y, z + h + 0.012)], 0.0012, M["black"], group=G, bevel_res=1)


def potted(name, M, x, y, z, kind="small", rz=0.0, scale=1.0):
    """Γλαστράκι: έτοιμο μοντέλο αν υπάρχει στην αποθήκη, αλλιώς το απλό υπολογιστικό φυτό."""
    aid = {"small": "potted_plant_04", "medium": "potted_plant_02"}[kind]
    o = L.model(aid, x, y, z, rz=rz, scale=scale, name=name, group=G, mats={"_pot": M["ceramic_m"]} if kind == "medium" else None)
    if o is None:
        small_plant(name, M, x, y, z, r=0.07 if kind == "small" else 0.12, h=0.12 if kind == "small" else 0.2, n=24, size=0.15 if kind == "small" else 0.3, seed=int(x * 10))
    return o


def vase(name, M, x, y, z, kind=2, scale=1.0, rz=0.0):
    """Κεραμικό βάζο (μοντέλο 1…4)· αλλιώς ένα απλό εκ περιστροφής. Επιστρέφει το ύψος του χείλους."""
    aid = "ceramic_vase_0%d" % kind
    o = L.model(aid, x, y, z, rz=rz, scale=scale, name=name, group=G)
    if o is not None:
        return z + o["size"][2] * scale
    s = scale
    prof = [(0.0, 0.0), (0.06 * s, 0.0), (0.10 * s, 0.05 * s), (0.11 * s, 0.14 * s), (0.085 * s, 0.24 * s), (0.055 * s, 0.29 * s), (0.06 * s, 0.31 * s), (0.048 * s, 0.305 * s), (0.0, 0.30 * s)]
    v = lathe(name, prof, M["ceramic_m"], seg=40); place(v, x, y, z)
    return z + 0.31 * s


def dry_stems(name, M, x, y, z, n=11, h=0.75, spread=0.5, seed=2):
    """Ξερά στάχυα / πάμπας μέσα σε βάζο: λεπτά κοτσάνια με αφράτο φούντωμα στην κορυφή."""
    rnd = __import__("random").Random(seed)
    base = P(x, y, z)
    up = Vector((0, 0, 1))
    verts, faces = [], []
    for i in range(n):
        az = i * 2.399 + rnd.uniform(-0.4, 0.4)
        lean = rnd.uniform(0.05, spread) * 0.42
        ln = h * rnd.uniform(0.72, 1.05)
        d = Vector((math.cos(az) * lean, math.sin(az) * lean, 1.0)).normalized()
        bend = Vector((math.cos(az), math.sin(az), 0)) * (0.10 * ln * rnd.uniform(0.4, 1.2))
        pts = [base + d * (ln * q) + bend * (q * q) for q in (0, 0.35, 0.7, 1.0)]
        tube(name + "_s%d" % i, [(p.x, -p.y, p.z) for p in pts], 0.0016, M["dry"], group=G, bevel_res=1)
        # φούντα: πολλά λεπτά «πούπουλα» γύρω από το πάνω τρίτο
        ax = (pts[3] - pts[2]).normalized()
        side = ax.cross(up)
        side = side.normalized() if side.length > 1e-3 else Vector((1, 0, 0))
        pl = ln * rnd.uniform(0.22, 0.32)
        for j in range(46):
            q = rnd.random()
            p = pts[3] - ax * (pl * q) + ax * (pl * 0.25)
            ang = rnd.uniform(0, 2 * math.pi)
            o = side * math.cos(ang) + ax.cross(side) * math.sin(ang)
            t = ax * rnd.uniform(0.6, 1.0) + o * rnd.uniform(0.25, 0.6) * (0.4 + q)
            _leaf(verts, faces, p, t, up, rnd.uniform(0.04, 0.075), rnd.uniform(0.006, 0.011), droop=rnd.uniform(0.1, 0.5))
    obj_from(name + "_plumes", verts, faces, M["dry_plume"], smooth=True, group=G, fix_normals=False)


def kitchen_items(M, K):
    CT = K["CT"]
    x0, y0, x1, y1 = K["counter_n"]
    hx0, hx1 = K["hob"]
    # ξύλα κοπής ακουμπισμένα στην πλάτη του πάγκου, δεξιά από τις εστίες
    for i, (w, h, dx, tilt) in enumerate(((0.26, 0.38, 0.0, 9), (0.20, 0.30, 0.10, 12))):
        b = rprism("board%d" % i, w, 0.018, h, 0.009, M["oak_dark"]["Z"] if i == 0 else M["oak"]["Z"], re=0.004, segc=4, sege=2, group=G)
        place(b, hx1 + 0.22 + dx, y0 + 0.035 + i * 0.022, CT + 0.001, rx=-tilt)
    # βάζο με ξύλινες κουτάλες, αριστερά από τις εστίες
    jx, jy = hx0 - 0.20, y0 + 0.14
    j = lathe("jar", [(0.0, 0.0), (0.055, 0.0), (0.06, 0.02), (0.06, 0.15), (0.052, 0.15), (0.05, 0.02), (0.0, 0.02)], M["ceramic_sand"], seg=32); place(j, jx, jy, CT)
    for i, (dx, dy) in enumerate(((0.02, 0.01), (-0.018, 0.015), (0.0, -0.02))):
        tube("spoon%d" % i, [(jx + dx * 0.4, jy + dy * 0.4, CT + 0.03), (jx + dx * 2.2, jy + dy * 2.2, CT + 0.30)], 0.005, M["oak"]["Z"], group=G, bevel_res=2)
    # μπολ με λεμόνια στον πάγκο του έρκερ (κάτω από το ανατολικό παράθυρο)
    ex0, ey0, ex1, ey1 = K["counter_e"]
    bx, by = (ex0 + ex1) / 2 + 0.03, (ey0 + ey1) / 2 + 0.12
    zb = bowl("fruit_bowl", M, bx, by, CT, r=0.15, h=0.075, mat=M["ceramic_m"])
    for i, (dx, dy, dz) in enumerate(((0.0, 0.0, 0.0), (0.062, 0.02, 0.0), (-0.05, 0.04, 0.0), (0.0, -0.062, 0.0), (0.012, 0.012, 0.052))):
        s = sphere("lemon%d" % i, 0.031, M["lemon"], squash=1.22)
        place(s, bx + dx, by + dy, zb + 0.034 + dz, rx=90, rz=40 * i)
    potted("herb", M, (ex0 + ex1) / 2 + 0.10, ey0 + 0.22, CT, "small", rz=30)
    # δυτικό άκρο του βόρειου πάγκου: βάζο με ξερά κλαδιά, δίσκος με κανάτα και φλιτζάνια
    zv = vase("k_vase", M, x0 + 0.24, y0 + 0.20, CT, kind=4, scale=0.95, rz=40)
    dry_stems("k_stems", M, x0 + 0.24, y0 + 0.20, zv - 0.06, n=7, h=0.48, spread=0.45, seed=5)
    tx, ty = x0 + 0.86, (y0 + y1) / 2 + 0.03
    tr = rprism("tray", 0.40, 0.27, 0.014, 0.03, M["oak_dark"]["X"], re=0.004, segc=6, sege=2, group=G); place(tr, tx, ty, CT)
    jg = lathe("jug", [(0.0, 0.0), (0.05, 0.0), (0.062, 0.03), (0.066, 0.10), (0.05, 0.17), (0.04, 0.20), (0.046, 0.215), (0.038, 0.212), (0.036, 0.19), (0.0, 0.185)], M["ceramic_m"], seg=36)
    place(jg, tx - 0.09, ty + 0.01, CT + 0.014)
    for i, (dx, dy) in enumerate(((0.07, -0.05), (0.12, 0.055))):
        cp = lathe("cup%d" % i, [(0.0, 0.0), (0.028, 0.0), (0.038, 0.02), (0.04, 0.07), (0.035, 0.07), (0.033, 0.022), (0.0, 0.012)], M["ceramic_sand"], seg=28)
        place(cp, tx + dx, ty + dy, CT + 0.014)
    # δίπλα στον νεροχύτη: μπουκάλι σαπουνιού + γλαστράκι
    sx0, sy0, sx1, sy1 = K["counter_s"]
    kx0, ky0, kx1, ky1 = K["sink"]
    bt = lathe("soap", [(0.0, 0.0), (0.028, 0.0), (0.03, 0.01), (0.03, 0.12), (0.012, 0.145), (0.012, 0.17), (0.0, 0.17)], M["amber"], seg=28); place(bt, kx1 + 0.10, sy1 - 0.09, CT)
    potted("herb2", M, kx0 - 0.42, sy1 - 0.16, CT, "small", rz=110)


# ------------------------------------------------------------------ κουρτίνες
def curtain(name, M, ax, a0, a1, c, z0, z1, wave=0.12, amp=0.035, mat=None, seed=0):
    """Διάφανη κουρτίνα με πτυχές. ax = 'x' (κατά μήκος x, στο y = c) ή 'y' (κατά μήκος y, στο x = c)."""
    rnd = __import__("random").Random(seed)
    n = max(8, int((a1 - a0) / wave * 10))
    rows = 7
    ph = rnd.uniform(0, 6.28)
    verts, faces = [], []
    for k in range(rows + 1):
        s = k / rows
        z = z1 + (z0 - z1) * s
        for i in range(n + 1):
            t = i / n
            a = a0 + (a1 - a0) * t
            am = amp * (0.55 + 0.6 * s) * (1 + 0.25 * math.sin(5.1 * t + ph))
            off = am * math.sin(2 * math.pi * (a - a0) / wave + ph + 0.35 * s * math.sin(9 * t)) + 0.012 * s * math.sin(2.3 * t * 6.28 + ph)
            verts.append(P(a, c + off, z) if ax == "x" else P(c + off, a, z))
    for k in range(rows):
        for i in range(n):
            p = k * (n + 1) + i
            faces.append((p, p + 1, p + n + 2, p + n + 1))
    return obj_from(name, verts, faces, mat or M["sheer"], smooth=True, group=G, fix_normals=False)
