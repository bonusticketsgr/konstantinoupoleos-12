"""ΠΑΡΟΥΣΙΑΣΗ 3D – βοηθητικά για το Blender (bpy): γεωμετρικά σχήματα και υλικά.
Όλες οι συναρτήσεις τοποθέτησης δέχονται συντεταγμένες ΜΟΝΤΕΛΟΥ (m, x → ανατολή, y → νότος, z από το δάπεδο)· στο Blender: X = x, Y = −y, Z = z."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

RNG = random.Random(12)
_COLL = {}


def srgb(r, g, b):
    """sRGB 0..255 → γραμμικό RGBA."""
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1.0)


def coll(name):
    if name not in _COLL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        _COLL[name] = c
    return _COLL[name]


def P(x, y, z=0.0):
    return Vector((x, -y, z))


# ------------------------------------------------------------------ πλέγματα
def obj_from(name, verts, faces, mat=None, smooth=None, group="misc", fix_normals=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    if fix_normals:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(me); bm.free()
    if smooth is not None:
        if isinstance(smooth, bool):
            smooth = [smooth] * len(me.polygons)
        me.polygons.foreach_set("use_smooth", smooth)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll(group).objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob


def _box_vf(w, d, h):
    x, y, z = w / 2, d / 2, h / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return v, f


def _rbox_vf(w, d, h, r, seg):
    hx, hy, hz = w / 2, d / 2, h / 2
    r = min(r, hx, hy, hz)

    def axis(hh):
        inner = hh - r
        offs = [r * math.tan(math.radians(45.0 * i / seg)) for i in range(seg + 1)]
        neg = [-(inner + o) for o in reversed(offs)]
        pos = [inner + o for o in offs]
        return neg + (pos[1:] if inner < 1e-7 else pos)

    X, Y, Z = axis(hx), axis(hy), axis(hz)
    nx, ny, nz = len(X), len(Y), len(Z)
    idx, verts = {}, []

    def vid(i, j, k):
        key = (i, j, k)
        if key not in idx:
            px, py, pz = X[i], Y[j], Z[k]
            ix = max(-(hx - r), min(hx - r, px)); iy = max(-(hy - r), min(hy - r, py)); iz = max(-(hz - r), min(hz - r, pz))
            dx, dy, dz = px - ix, py - iy, pz - iz
            L = math.sqrt(dx * dx + dy * dy + dz * dz)
            s = r / L if L > 1e-12 else 0.0
            idx[key] = len(verts); verts.append((ix + dx * s, iy + dy * s, iz + dz * s))
        return idx[key]

    faces = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            faces.append((vid(i, j, 0), vid(i, j + 1, 0), vid(i + 1, j + 1, 0), vid(i + 1, j, 0)))
            faces.append((vid(i, j, nz - 1), vid(i + 1, j, nz - 1), vid(i + 1, j + 1, nz - 1), vid(i, j + 1, nz - 1)))
    for i in range(nx - 1):
        for k in range(nz - 1):
            faces.append((vid(i, 0, k), vid(i + 1, 0, k), vid(i + 1, 0, k + 1), vid(i, 0, k + 1)))
            faces.append((vid(i, ny - 1, k), vid(i, ny - 1, k + 1), vid(i + 1, ny - 1, k + 1), vid(i + 1, ny - 1, k)))
    for j in range(ny - 1):
        for k in range(nz - 1):
            faces.append((vid(0, j, k), vid(0, j, k + 1), vid(0, j + 1, k + 1), vid(0, j + 1, k)))
            faces.append((vid(nx - 1, j, k), vid(nx - 1, j + 1, k), vid(nx - 1, j + 1, k + 1), vid(nx - 1, j, k + 1)))
    return verts, faces


def mbox(name, x0, y0, x1, y1, z0, z1, mat, r=0.0, seg=3, group="arch", rot=0.0):
    """Κουτί από συντεταγμένες μοντέλου· r > 0 → στρογγυλεμένες ακμές. rot = στροφή γύρω από τον κατακόρυφο άξονα (μοίρες, αριστερόστροφα σε κάτοψη Blender)."""
    w, d, h = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    if r > 0:
        v, f = _rbox_vf(w, d, h, r, seg)
        ob = obj_from(name, v, f, mat, smooth=True, group=group)
    else:
        v, f = _box_vf(w, d, h)
        ob = obj_from(name, v, f, mat, smooth=False, group=group, fix_normals=False)
    ob.location = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if rot:
        ob.rotation_euler = Euler((0, 0, math.radians(rot)))
    return ob


def lbox(name, w, d, h, mat, r=0.0, seg=3, group="furn"):
    """Κουτί γύρω από την αρχή (τοπικό) – τοποθετείται μετά με το place()."""
    if r > 0:
        v, f = _rbox_vf(w, d, h, r, seg)
        return obj_from(name, v, f, mat, smooth=True, group=group)
    v, f = _box_vf(w, d, h)
    return obj_from(name, v, f, mat, smooth=False, group=group, fix_normals=False)


def place(ob, x, y, z, rz=0.0, rx=0.0, ry=0.0):
    ob.location = P(x, y, z)
    ob.rotation_euler = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), "XYZ")
    return ob


def prism(name, pts, z0, z1, mat, group="arch"):
    """Πρίσμα από πολύγωνο κάτοψης (συντεταγμένες μοντέλου)."""
    n = len(pts)
    v = [P(x, y, z0) for x, y in pts] + [P(x, y, z1) for x, y in pts]
    f = [tuple(range(n)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return obj_from(name, v, f, mat, smooth=False, group=group)


def _ring(w, d, rc, segc, inset=0.0, scale=1.0):
    hx0, hy0 = w / 2 - inset, d / 2 - inset
    r0 = max(min(rc - inset, hx0, hy0), 0.0)
    hx, hy, r = hx0 * scale, hy0 * scale, r0 * scale
    pts = []
    for cx, cy, a0 in ((hx - r, hy - r, 0), (-(hx - r), hy - r, 90), (-(hx - r), -(hy - r), 180), (hx - r, -(hy - r), 270)):
        for i in range(segc + 1):
            a = math.radians(a0 + 90.0 * i / segc)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rprism(name, w, d, h, rc, mat, re=0.004, segc=8, sege=2, taper=1.0, group="furn"):
    """Πρίσμα με στρογγυλεμένες γωνίες κάτοψης (rc) και μαλακές ακμές πάνω / κάτω (re). w = d και rc = w/2 → κύλινδρος. taper = κλίμακα στην κορυφή.
    Τοπικό: η βάση στο z = 0."""
    rings = []
    if re > 1e-6:
        for j in range(sege + 1):
            t = math.radians(90.0 * j / sege)
            rings.append((re * (1 - math.sin(t)), re * (1 - math.cos(t))))
        for j in range(sege, -1, -1):
            t = math.radians(90.0 * j / sege)
            rings.append((re * (1 - math.sin(t)), h - re * (1 - math.cos(t))))
    else:
        rings = [(0.0, 0.0), (0.0, h)]
    verts, faces, smooth = [], [], []
    N = 4 * (segc + 1)
    for inset, z in rings:
        s = 1.0 + (taper - 1.0) * (z / h)
        verts += [(x, y, z) for x, y in _ring(w, d, rc, segc, inset, s)]
    faces.append(tuple(range(N - 1, -1, -1))); smooth.append(False)
    for k in range(len(rings) - 1):
        a, b = k * N, (k + 1) * N
        for i in range(N):
            faces.append((a + i, a + (i + 1) % N, b + (i + 1) % N, b + i)); smooth.append(True)
    top = (len(rings) - 1) * N
    faces.append(tuple(range(top, top + N))); smooth.append(False)
    return obj_from(name, verts, faces, mat, smooth=smooth, group=group, fix_normals=False)


def cyl(name, r0, r1, h, mat, re=0.002, seg=6, group="furn"):
    return rprism(name, 2 * r0, 2 * r0, h, r0, mat, re=re, segc=seg, sege=2, taper=r1 / r0, group=group)


def cushion(name, w, d, h, mat, r=None, bulge=0.02, seg=5, group="furn", sag=0.0):
    """Μαξιλάρι καθίσματος: στρογγυλεμένο κουτί που φουσκώνει στη μέση (πάνω και λίγο μπροστά)."""
    r = r if r is not None else min(h * 0.42, 0.06)
    v, f = _rbox_vf(w, d, h, r, seg)
    hx, hy, hz = w / 2, d / 2, h / 2
    out = []
    for x, y, z in v:
        u, t = x / hx, y / hy
        k = max(0.0, 1 - u * u) ** 0.8 * max(0.0, 1 - t * t) ** 0.8
        if z > 0:
            z += bulge * k * (z / hz)
        else:
            z += -sag * k * (-z / hz)
        out.append((x, y, z))
    return obj_from(name, out, f, mat, smooth=True, group=group)


def pillow(name, w, t, mat, n=14, group="decor"):
    """Διακοσμητικό μαξιλάρι (τετράγωνο w × w, πάχος t στη μέση) – τοπικό, στο επίπεδο XY."""
    verts, faces = [], []
    def prof(u, v):
        return (max(0.0, 1 - abs(u) ** 2.6) * max(0.0, 1 - abs(v) ** 2.6)) ** 0.55
    for side in (1, -1):
        for i in range(n + 1):
            for j in range(n + 1):
                u, v = -1 + 2 * i / n, -1 + 2 * j / n
                pinch = 1 - 0.06 * (abs(u) ** 3) * (abs(v) ** 3)
                verts.append((u * w / 2 * pinch, v * w / 2 * pinch, side * (t / 2 * prof(u, v) + 0.004)))
    off = (n + 1) * (n + 1)
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            faces.append((a, a + n + 1, a + n + 2, a + 1))
            faces.append((off + a, off + a + 1, off + a + n + 2, off + a + n + 1))
    for i in range(n):                                   # ραφή γύρω-γύρω
        for a, b in ((i * (n + 1), (i + 1) * (n + 1)), (i * (n + 1) + n, (i + 1) * (n + 1) + n), (i, i + 1), (n * (n + 1) + i, n * (n + 1) + i + 1)):
            faces.append((a, b, off + b, off + a))
    return obj_from(name, verts, faces, mat, smooth=True, group=group)


def tube(name, pts, radius, mat, group="furn", res=8, cyclic=False, bevel_res=3):
    """Σωλήνας κατά μήκος σημείων (συντεταγμένες μοντέλου) – καμπύλη με στρογγυλή διατομή."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"; cu.bevel_depth = radius; cu.bevel_resolution = bevel_res; cu.resolution_u = res; cu.use_fill_caps = True
    sp = cu.splines.new("NURBS" if len(pts) > 2 else "POLY")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        v = P(*q); p.co = (v.x, v.y, v.z, 1.0)
    if len(pts) > 2:
        sp.use_endpoint_u = True; sp.order_u = min(4, len(pts))
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    coll(group).objects.link(ob)
    if mat is not None:
        cu.materials.append(mat)
    return ob


def parent_all(name, objs, group="furn"):
    """Ομάδα αντικειμένων κάτω από ένα κενό (για κοινή μετακίνηση / στροφή)."""
    e = bpy.data.objects.new(name, None)
    coll(group).objects.link(e)
    for o in objs:
        o.parent = e
    return e


# ------------------------------------------------------------------ υλικά
_MATS = {}


def _new(name):
    m = bpy.data.materials.new(name)
    try:
        if not m.node_tree:
            m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


def _set(node, **kw):
    for k, v in kw.items():
        key = k.replace("_", " ")
        if key in node.inputs:
            node.inputs[key].default_value = v
        else:
            cand = [i for i in node.inputs if i.name.lower() == key.lower()]
            if cand:
                cand[0].default_value = v


def _mix(nt, a, b, fac):
    """Μίξη χρωμάτων: a, b, fac = υποδοχές ή τιμές → υποδοχή εξόδου."""
    n = nt.nodes.new("ShaderNodeMix"); n.data_type = "RGBA"
    for key, val in (("Factor_Float", fac), ("A_Color", a), ("B_Color", b)):
        s = [i for i in n.inputs if i.identifier == key][0]
        if hasattr(val, "is_linked") or isinstance(val, bpy.types.NodeSocket):
            nt.links.new(val, s)
        else:
            s.default_value = val
    return [o for o in n.outputs if o.identifier == "Result_Color"][0]


def _coords(nt, vary=True, attr=None):
    """Συντεταγμένες αντικειμένου (m) + τυχαία μετατόπιση ανά αντικείμενο (και ανά σανίδα, αν δοθεί attribute)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vec = tc.outputs["Object"]
    if vary:
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = "ADD"
        sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = "SCALE"
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(oi.outputs["Random"], comb.inputs[0]); nt.links.new(oi.outputs["Random"], comb.inputs[1]); nt.links.new(oi.outputs["Random"], comb.inputs[2])
        nt.links.new(comb.outputs[0], sc.inputs[0]); sc.inputs["Scale"].default_value = 37.0
        nt.links.new(vec, add.inputs[0]); nt.links.new(sc.outputs[0], add.inputs[1])
        vec = add.outputs[0]
    if attr:
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = attr
        sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = "SCALE"; sc.inputs["Scale"].default_value = 53.0
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        for i in range(3):
            nt.links.new(at.outputs["Fac"], comb.inputs[i])
        nt.links.new(comb.outputs[0], sc.inputs[0])
        add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = "ADD"
        nt.links.new(vec, add.inputs[0]); nt.links.new(sc.outputs[0], add.inputs[1])
        vec = add.outputs[0]
    return vec


def _bump(nt, height, strength=0.2, dist=0.002):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    nt.links.new(height, b.inputs["Height"])
    return b.outputs["Normal"]


def plain(name, color, rough=0.5, metal=0.0, **kw):
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, Base_Color=color, Roughness=rough, Metallic=metal, **kw)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def paint(name, color, rough=0.55, bump=0.03):
    """Βαμμένος τοίχος / οροφή: ματ, με ελάχιστη υφή ρολού."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, Base_Color=color, Roughness=rough)
    vec = _coords(nt, vary=False)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 420.0; n.inputs["Detail"].default_value = 3.0
    nt.links.new(vec, n.inputs["Vector"])
    nt.links.new(_bump(nt, n.outputs["Fac"], bump, 0.0006), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def wood(name, axis="X", c_dark=(172, 142, 106), c_light=(212, 186, 150), rough=0.42, scale=1.0, attr=None, tone_var=0.0, coat=0.0):
    """Ξύλο (δρυς) με νερά κατά τον άξονα axis του αντικειμένου. attr = attribute ανά έδρα (σανίδες δαπέδου) για διαφορετικά νερά / τόνο ανά σανίδα."""
    key = name
    if key in _MATS:
        return _MATS[key]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=True, attr=attr)
    mp = nt.nodes.new("ShaderNodeMapping")
    s = {"X": (0.55, 9.0, 9.0), "Y": (9.0, 0.55, 9.0), "Z": (9.0, 9.0, 0.55)}[axis]
    mp.inputs["Scale"].default_value = tuple(v * scale for v in s)
    nt.links.new(vec, mp.inputs["Vector"])
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    _set(n1, Scale=2.6, Detail=9.0, Roughness=0.62, Distortion=1.6)
    nt.links.new(mp.outputs[0], n1.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28; ramp.color_ramp.elements[0].color = srgb(*c_dark)
    ramp.color_ramp.elements[1].position = 0.72; ramp.color_ramp.elements[1].color = srgb(*c_light)
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    # λεπτά νερά (πόροι)
    mp2 = nt.nodes.new("ShaderNodeMapping")
    s2 = {"X": (3.0, 160.0, 160.0), "Y": (160.0, 3.0, 160.0), "Z": (160.0, 160.0, 3.0)}[axis]
    mp2.inputs["Scale"].default_value = s2
    nt.links.new(vec, mp2.inputs["Vector"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); _set(n2, Scale=1.0, Detail=4.0, Roughness=0.7)
    nt.links.new(mp2.outputs[0], n2.inputs["Vector"])
    dark = nt.nodes.new("ShaderNodeMapRange"); dark.inputs["From Min"].default_value = 0.35; dark.inputs["From Max"].default_value = 0.75
    dark.inputs["To Min"].default_value = 0.86; dark.inputs["To Max"].default_value = 1.04
    nt.links.new(n2.outputs["Fac"], dark.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "SCALE"
    nt.links.new(col, mul.inputs[0]); nt.links.new(dark.outputs[0], mul.inputs["Scale"])
    col = mul.outputs[0]
    if attr and tone_var > 0:                            # τόνος ανά σανίδα
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = attr
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - tone_var; mr.inputs["To Max"].default_value = 1 + tone_var
        nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
        mul2 = nt.nodes.new("ShaderNodeVectorMath"); mul2.operation = "SCALE"
        nt.links.new(col, mul2.inputs[0]); nt.links.new(mr.outputs[0], mul2.inputs["Scale"])
        col = mul2.outputs[0]
    nt.links.new(col, b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough - 0.06; rr.inputs["To Max"].default_value = rough + 0.08
    nt.links.new(n2.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    nt.links.new(_bump(nt, n2.outputs["Fac"], 0.12, 0.0006), b.inputs["Normal"])
    _set(b, Coat_Weight=coat, Coat_Roughness=0.25)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[key] = m
    return m


def fabric(name, color, rough=0.95, weave=700.0, bump=0.25, sheen=0.35, boucle=False, mottle=0.06):
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=False)
    if boucle:
        v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = weave
        nt.links.new(vec, v.inputs["Vector"]); h = v.outputs["Distance"]
    else:
        w1 = nt.nodes.new("ShaderNodeTexWave"); w1.wave_type = "BANDS"; w1.bands_direction = "X"; _set(w1, Scale=weave, Distortion=0.4)
        w2 = nt.nodes.new("ShaderNodeTexWave"); w2.wave_type = "BANDS"; w2.bands_direction = "Z"; _set(w2, Scale=weave, Distortion=0.4)
        w3 = nt.nodes.new("ShaderNodeTexWave"); w3.wave_type = "BANDS"; w3.bands_direction = "Y"; _set(w3, Scale=weave, Distortion=0.4)
        for w in (w1, w2, w3):
            nt.links.new(vec, w.inputs["Vector"])
        a = nt.nodes.new("ShaderNodeMath"); a.operation = "ADD"; nt.links.new(w1.outputs["Fac"], a.inputs[0]); nt.links.new(w2.outputs["Fac"], a.inputs[1])
        a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = "ADD"; nt.links.new(a.outputs[0], a2.inputs[0]); nt.links.new(w3.outputs["Fac"], a2.inputs[1])
        h = a2.outputs[0]
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=9.0, Detail=5.0, Roughness=0.6)
    nt.links.new(vec, n.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - mottle; mr.inputs["To Max"].default_value = 1 + mottle
    nt.links.new(n.outputs["Fac"], mr.inputs["Value"])
    rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = color
    mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "SCALE"
    nt.links.new(rgb.outputs[0], mul.inputs[0]); nt.links.new(mr.outputs[0], mul.inputs["Scale"])
    nt.links.new(mul.outputs[0], b.inputs["Base Color"])
    _set(b, Roughness=rough, Sheen_Weight=sheen, Sheen_Roughness=0.5)
    nt.links.new(_bump(nt, h, bump, 0.0008), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def stone(name, color=(233, 231, 226), vein=(176, 174, 170), rough=0.22, amount=0.26):
    """Τεχνητός λευκός πάγκος (quartz) με αχνά νερά."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=True)
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=1.6, Detail=10.0, Roughness=0.72, Distortion=2.2)
    nt.links.new(vec, n.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.47; e[0].color = (0, 0, 0, 1); e[1].position = 0.50; e[1].color = (1, 1, 1, 1)
    e2 = ramp.color_ramp.elements.new(0.53); e2.color = (0, 0, 0, 1)
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    f = nt.nodes.new("ShaderNodeMath"); f.operation = "MULTIPLY"; f.inputs[1].default_value = amount
    nt.links.new(ramp.outputs["Color"], f.inputs[0])
    nt.links.new(_mix(nt, srgb(*color), srgb(*vein), f.outputs[0]), b.inputs["Base Color"])
    _set(b, Roughness=rough)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def glass(name="glass", view=(0.62, 0.63, 0.63, 1.0)):
    """Τζάμι κουφωμάτων. Το ΦΩΣ (σκιές, διάχυτες ακτίνες) περνά ελεύθερα· η ΚΑΜΕΡΑ βλέπει το έξω πιο σκούρο (view) – όπως σε φωτογραφία εσωτερικού με σωστή
    έκθεση και για το μέσα και για το έξω – συν την ανάκλαση του τζαμιού. Ο δείκτης διάθλασης αντιστρέφεται στην πίσω παρειά, αλλιώς το τζάμι γίνεται καθρέφτης."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = view
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.0
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ior = nt.nodes.new("ShaderNodeMapRange")
    ior.inputs["To Min"].default_value = 1.5; ior.inputs["To Max"].default_value = 1.0 / 1.5
    nt.links.new(geo.outputs["Backfacing"], ior.inputs["Value"])
    fr = nt.nodes.new("ShaderNodeFresnel")
    nt.links.new(ior.outputs[0], fr.inputs["IOR"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(gl.outputs[0], mix.inputs[2])
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); nt.links.new(lp.outputs["Is Diffuse Ray"], mx.inputs[1])
    tr2 = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mx.outputs[0], mix2.inputs[0]); nt.links.new(mix.outputs[0], mix2.inputs[1]); nt.links.new(tr2.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def sheer(name="sheer", color=(0.95, 0.94, 0.90, 1.0), opacity=0.55):
    """Λινή διάφανη κουρτίνα."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = color
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); tl.inputs["Color"].default_value = color
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m1 = nt.nodes.new("ShaderNodeMixShader"); m1.inputs[0].default_value = 0.55
    nt.links.new(df.outputs[0], m1.inputs[1]); nt.links.new(tl.outputs[0], m1.inputs[2])
    # ύφανση: πιο αραιή ανάμεσα στις κλωστές
    vec = _coords(nt, vary=False)
    w1 = nt.nodes.new("ShaderNodeTexWave"); w1.bands_direction = "Z"; _set(w1, Scale=260.0, Distortion=0.6)
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.bands_direction = "X"; _set(w2, Scale=260.0, Distortion=0.6)
    w3 = nt.nodes.new("ShaderNodeTexWave"); w3.bands_direction = "Y"; _set(w3, Scale=260.0, Distortion=0.6)
    for w in (w1, w2, w3):
        nt.links.new(vec, w.inputs["Vector"])
    a = nt.nodes.new("ShaderNodeMath"); a.operation = "MAXIMUM"; nt.links.new(w1.outputs["Fac"], a.inputs[0]); nt.links.new(w2.outputs["Fac"], a.inputs[1])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = "MAXIMUM"; nt.links.new(a.outputs[0], a2.inputs[0]); nt.links.new(w3.outputs["Fac"], a2.inputs[1])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = opacity - 0.2; mr.inputs["To Max"].default_value = min(opacity + 0.25, 0.97)
    nt.links.new(a2.outputs[0], mr.inputs["Value"])
    m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], m2.inputs[0]); nt.links.new(tr.outputs[0], m2.inputs[1]); nt.links.new(m1.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def emit(name, color, strength):
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = color; e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def leaf(name, color, color2=None, rough=0.45, trans=0.25):
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, Roughness=rough)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    vec = _coords(nt, vary=False)
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=14.0, Detail=2.0)
    nt.links.new(vec, n.inputs["Vector"])
    col = _mix(nt, color, color2 or color, n.outputs["Fac"])
    nt.links.new(col, b.inputs["Base Color"])
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(col, tl.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.inputs[0].default_value = trans
    nt.links.new(b.outputs[0], mix.inputs[1]); nt.links.new(tl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def image_mat(name, img, rough=0.6):
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.extension = "EXTEND"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["UV"], tx.inputs["Vector"])
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    _set(b, Roughness=rough)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def building(name="bld"):
    """Γειτονικά κτίρια του φόντου: ανοιχτός σοβάς με κάναβο παραθύρων (ουδέτερο – δεν είναι αποτύπωση)."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; nt.links.new(sep.outputs["X"], add.inputs[0]); nt.links.new(sep.outputs["Y"], add.inputs[1])

    def cell(src, size, lo, hi):
        d = nt.nodes.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.inputs[1].default_value = size; nt.links.new(src, d.inputs[0])
        f = nt.nodes.new("ShaderNodeMath"); f.operation = "FRACT"; nt.links.new(d.outputs[0], f.inputs[0])
        g = nt.nodes.new("ShaderNodeMath"); g.operation = "GREATER_THAN"; g.inputs[1].default_value = lo; nt.links.new(f.outputs[0], g.inputs[0])
        l = nt.nodes.new("ShaderNodeMath"); l.operation = "LESS_THAN"; l.inputs[1].default_value = hi; nt.links.new(f.outputs[0], l.inputs[0])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; nt.links.new(g.outputs[0], mm.inputs[0]); nt.links.new(l.outputs[0], mm.inputs[1])
        return mm.outputs[0]
    wx = cell(add.outputs[0], 3.4, 0.22, 0.72)
    wz = cell(sep.outputs["Z"], 3.1, 0.28, 0.78)
    win = nt.nodes.new("ShaderNodeMath"); win.operation = "MULTIPLY"; nt.links.new(wx, win.inputs[0]); nt.links.new(wz, win.inputs[1])
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    wall = _mix(nt, srgb(236, 230, 218), srgb(214, 204, 188), oi.outputs["Random"])
    col = _mix(nt, wall, srgb(96, 98, 98), win.outputs[0])
    nt.links.new(col, b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.9; rr.inputs["To Max"].default_value = 0.15
    nt.links.new(win.outputs[0], rr.inputs["Value"]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def foliage(name="foliage"):
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=True)
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=2.2, Detail=6.0, Roughness=0.7)
    nt.links.new(vec, n.inputs["Vector"])
    nt.links.new(_mix(nt, srgb(44, 66, 38), srgb(96, 122, 66), n.outputs["Fac"]), b.inputs["Base Color"])
    _set(b, Roughness=0.9)
    n2 = nt.nodes.new("ShaderNodeTexNoise"); _set(n2, Scale=3.5, Detail=8.0, Roughness=0.8)
    nt.links.new(vec, n2.inputs["Vector"])
    nt.links.new(_bump(nt, n2.outputs["Fac"], 1.0, 0.35), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


# ------------------------------------------------------------------ υλικά με ΠΡΑΓΜΑΤΙΚΕΣ υφές (αρχεία της αποθήκης – βλ. assets.py)
import assets as A

_IMG, _MEAN = {}, {}
# πραγματικό μέγεθος μιας επανάληψης κάθε υφής (m)
TEX_SIZE = {"oak_veneer_01": 1.83, "oak_veneer_05": 1.00, "curly_teddy_natural": 0.33, "hessian_230": 0.27, "rough_linen": 0.27, "velour_velvet": 0.28,
            "poly_wool_herringbone": 0.27, "leather_white": 0.30, "white_stucco": 2.00}
TEX_GRAIN_U = {"oak_veneer_05"}                              # υφές ξύλου με τα νερά ΟΡΙΖΟΝΤΙΑ μέσα στην εικόνα (οι άλλες: κατακόρυφα)


def _image(path, data=False):
    k = (path, data)
    if k not in _IMG:
        im = bpy.data.images.load(path)
        if data:
            im.colorspace_settings.name = "Non-Color"
        _IMG[k] = im
    return _IMG[k]


def _mean(path):
    """Μέσο χρώμα της υφής (γραμμικό) – για να «βαφτεί» η υφή στο χρώμα που θέλουμε χωρίς να χαθούν τα νερά / η ύφανσή της."""
    if path not in _MEAN:
        import numpy as np
        im = bpy.data.images.load(path, check_existing=False); im.scale(24, 24)
        a = np.empty(24 * 24 * 4, np.float32); im.pixels.foreach_get(a); bpy.data.images.remove(im)
        m = a.reshape(-1, 4)[:, :3].mean(axis=0)
        _MEAN[path] = tuple(float(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in m)
    return _MEAN[path]


def _math(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _grain_uv(nt, vec, axis, swap=False):
    """Συντεταγμένες υφής ξύλου: σε ΚΑΘΕ έδρα τα νερά τρέχουν κατά τον άξονα axis του αντικειμένου (στις έδρες-σόκορα: κατά τον επόμενο άξονα)."""
    g = "XYZ".index(axis); a, b = [i for i in range(3) if i != g]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(vec, sep.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    vt = nt.nodes.new("ShaderNodeVectorTransform"); vt.vector_type = "NORMAL"; vt.convert_from = "WORLD"; vt.convert_to = "OBJECT"
    nt.links.new(geo.outputs["Normal"], vt.inputs[0])
    ab = nt.nodes.new("ShaderNodeVectorMath"); ab.operation = "ABSOLUTE"; nt.links.new(vt.outputs[0], ab.inputs[0])
    sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(ab.outputs[0], sn.inputs[0])
    Na, Nb, Ng = sn.outputs[a], sn.outputs[b], sn.outputs[g]
    isA = _math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", Na, Nb), _math(nt, "GREATER_THAN", Na, Ng))
    isG = _math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", Ng, Na), _math(nt, "GREATER_THAN", Ng, Nb))

    def pick(p, q, f):                                       # f = 0 → p · f = 1 → q
        m = nt.nodes.new("ShaderNodeMix"); m.data_type = "FLOAT"
        nt.links.new(f, m.inputs[0]); nt.links.new(p, m.inputs[2]); nt.links.new(q, m.inputs[3])
        return m.outputs[0]
    u = pick(sep.outputs[a], sep.outputs[b], isA)
    v = pick(sep.outputs[g], sep.outputs[b], isG)
    c = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u, c.inputs[1 if swap else 0]); nt.links.new(v, c.inputs[0 if swap else 1])
    return c.outputs[0]


def pbr(name, aid, color=None, size=None, proj="box", axis="Z", rough=None, rough_mul=1.0, bump=1.0, bump_dist=0.002, attr=None, tone_var=0.0,
        vary=True, sheen=0.0, coat=0.0, sat=1.0, fallback=None, metal=0.0, tex_mix=1.0):
    """Υλικό από υφή της αποθήκης (χρώμα, τραχύτητα, ανάγλυφο). color = το χρώμα-στόχος (sRGB 0..255): η υφή «βάφεται» σε αυτό κρατώντας τα νερά της.
    proj: 'box' (υφάσματα, σοβάς – χωρίς κατεύθυνση) · 'grain' (ξύλο – νερά κατά τον άξονα axis). attr = attribute ανά έδρα (σανίδες): άλλα νερά / τόνος ανά σανίδα.
    Αν η υφή δεν έχει κατέβει → fallback (το παλιό υπολογιστικό υλικό)."""
    if name in _MATS:
        return _MATS[name]
    T = A.texture(aid)
    if T is None:
        m = fallback() if callable(fallback) else fallback
        _MATS[name] = m
        return m
    size = size or TEX_SIZE.get(aid, 1.0)
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=vary, attr=attr)
    box = proj == "box"
    if not box:
        vec = _grain_uv(nt, vec, axis, swap=aid in TEX_GRAIN_U)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0 / size,) * 3
    nt.links.new(vec, mp.inputs["Vector"])

    def tex(path, data):
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = _image(path, data)
        if box:
            tx.projection = "BOX"; tx.projection_blend = 0.25
        nt.links.new(mp.outputs[0], tx.inputs["Vector"])
        return tx
    td = tex(T["diff"], False)
    col = td.outputs["Color"]
    if abs(sat - 1.0) > 1e-3:
        hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = sat
        nt.links.new(col, hsv.inputs["Color"]); col = hsv.outputs["Color"]
    if color is not None:
        mean = _mean(T["diff"]); tgt = srgb(*color)
        gain = tuple(tgt[i] / max(mean[i], 1e-3) for i in range(3))
        mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = gain
        nt.links.new(col, mul.inputs[0]); col = mul.outputs[0]
        if tex_mix < 1.0:                                    # λιγότερη αντίθεση της υφής (π.χ. σοβάς: σχεδόν ενιαίο χρώμα)
            col = _mix(nt, tgt, col, tex_mix)
    if attr and tone_var > 0:
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = attr
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - tone_var; mr.inputs["To Max"].default_value = 1 + tone_var
        nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
        sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = "SCALE"
        nt.links.new(col, sc.inputs[0]); nt.links.new(mr.outputs[0], sc.inputs["Scale"]); col = sc.outputs[0]
    nt.links.new(col, b.inputs["Base Color"])
    if rough is not None:
        b.inputs["Roughness"].default_value = rough
    elif "rough" in T:
        tr = tex(T["rough"], True)
        r = _math(nt, "MULTIPLY", tr.outputs["Color"], rough_mul)
        cl = nt.nodes.new("ShaderNodeClamp"); cl.inputs["Min"].default_value = 0.08; cl.inputs["Max"].default_value = 1.0
        nt.links.new(r, cl.inputs["Value"]); nt.links.new(cl.outputs[0], b.inputs["Roughness"])
    if bump > 0 and "disp" in T:
        th = tex(T["disp"], True)
        nt.links.new(_bump(nt, th.outputs["Color"], bump, bump_dist), b.inputs["Normal"])
    _set(b, Sheen_Weight=sheen, Sheen_Roughness=0.5, Coat_Weight=coat, Coat_Roughness=0.2, Metallic=metal)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def travertine(name, color=(214, 200, 178), dark=(186, 168, 142), rough=0.38, axis="X", pits=0.5):
    """Τραβερτίνης (υπολογιστικός): ζεστό μπεζ με μαλακές λωρίδες κατά τον άξονα axis και μικρούς πόρους."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coords(nt, vary=True)
    mp = nt.nodes.new("ShaderNodeMapping")
    s = {"X": (0.35, 3.0, 11.0), "Y": (3.0, 0.35, 11.0), "Z": (11.0, 3.0, 0.35)}[axis]
    mp.inputs["Scale"].default_value = s
    nt.links.new(vec, mp.inputs["Vector"])
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=1.0, Detail=9.0, Roughness=0.68, Distortion=1.4)
    nt.links.new(mp.outputs[0], n.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.30; e[0].color = srgb(*dark); e[1].position = 0.70; e[1].color = srgb(*color)
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    # πόροι: μικρές σκούρες κουκκίδες, μακρόστενες κατά τις λωρίδες
    mp2 = nt.nodes.new("ShaderNodeMapping")
    s2 = {"X": (60.0, 260.0, 420.0), "Y": (260.0, 60.0, 420.0), "Z": (420.0, 260.0, 60.0)}[axis]
    mp2.inputs["Scale"].default_value = s2
    nt.links.new(vec, mp2.inputs["Vector"])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 1.0
    nt.links.new(mp2.outputs[0], vo.inputs["Vector"])
    n3 = nt.nodes.new("ShaderNodeTexNoise"); _set(n3, Scale=14.0, Detail=2.0)
    nt.links.new(vec, n3.inputs["Vector"])
    thr = nt.nodes.new("ShaderNodeMapRange"); thr.inputs["From Min"].default_value = 0.52; thr.inputs["From Max"].default_value = 0.66
    thr.inputs["To Min"].default_value = 0.10; thr.inputs["To Max"].default_value = 0.30 * pits
    nt.links.new(n3.outputs["Fac"], thr.inputs["Value"])
    pit = _math(nt, "LESS_THAN", vo.outputs["Distance"], thr.outputs[0])
    col = _mix(nt, ramp.outputs["Color"], srgb(max(dark[0] - 46, 0), max(dark[1] - 46, 0), max(dark[2] - 46, 0)), _math(nt, "MULTIPLY", pit, 0.75))
    nt.links.new(col, b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough; rr.inputs["To Max"].default_value = 0.9
    nt.links.new(pit, rr.inputs["Value"]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    inv = _math(nt, "SUBTRACT", 1.0, pit)
    nt.links.new(_bump(nt, inv, 0.6, 0.0012), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


def plaster(name, color, rough=0.9):
    """Γύψινο ανάγλυφο / κεραμικό ματ με ελαφριά τραχύτητα."""
    if name in _MATS:
        return _MATS[name]
    m, nt, out = _new(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, Base_Color=color, Roughness=rough)
    vec = _coords(nt, vary=False)
    n = nt.nodes.new("ShaderNodeTexNoise"); _set(n, Scale=95.0, Detail=6.0, Roughness=0.7)
    nt.links.new(vec, n.inputs["Vector"])
    nt.links.new(_bump(nt, n.outputs["Fac"], 0.35, 0.002), b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    _MATS[name] = m
    return m


# ------------------------------------------------------------------ έτοιμα μοντέλα (.blend της αποθήκης)
_MODELS = {}


def _model_objs(aid):
    if aid not in _MODELS:
        p = A.model(aid)
        if not p:
            _MODELS[aid] = None
        else:
            with bpy.data.libraries.load(p, link=False) as (src, dst):
                dst.objects = list(src.objects)
            _MODELS[aid] = [o for o in dst.objects if o is not None and o.type == "MESH"]
    return _MODELS[aid]


def has_model(aid):
    return bool(_model_objs(aid))


def model(aid, x, y, z, rz=0.0, scale=1.0, pick=None, name=None, group="decor", mats=None, recenter=True, drop=None):
    """Τοποθετεί αντίγραφο μοντέλου (κοινά δεδομένα πλέγματος – τα πολλά αντίγραφα δεν βαραίνουν). (x, y, z) = κέντρο βάσης, συντεταγμένες ΜΟΝΤΕΛΟΥ κτιρίου.
    pick = ποια αντικείμενα του αρχείου (συνάρτηση ονόματος → bool)· mats = {κομμάτι ονόματος υλικού: νέο υλικό}· drop = κομμάτια ονόματος αντικειμένων που παραλείπονται.
    Επιστρέφει το κενό-γονέα ή None αν το μοντέλο δεν έχει κατέβει."""
    objs = _model_objs(aid)
    if not objs:
        return None
    if pick is None:
        lod = any(o.name.endswith("_LOD0") for o in objs)
        pick = (lambda n: n.endswith("_LOD0")) if lod else (lambda n: True)
    sel = [o for o in objs if pick(o.name) and not (drop and any(d in o.name for d in drop))]
    if not sel:
        return None
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in sel:
        for c in o.bound_box:
            w = o.matrix_basis @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z))); hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    off = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)) if recenter else Vector((0, 0, 0))
    root = bpy.data.objects.new(name or aid, None)
    coll(group).objects.link(root)
    for o in sel:
        c = o.copy()
        coll(group).objects.link(c)
        c.parent = root
        c.location = c.location - off
        if mats:
            for sl in c.material_slots:
                for key, nm in mats.items():
                    if sl.material is not None and key in sl.material.name:
                        sl.link = "OBJECT"; sl.material = nm
    root.location = P(x, y, z)
    root.rotation_euler = Euler((0, 0, math.radians(rz)))
    root.scale = (scale, scale, scale)
    root["size"] = (hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)
    return root
