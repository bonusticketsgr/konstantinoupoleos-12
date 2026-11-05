"""Σ1 – Ξυλότυπος θεμελίωσης (-4,00 / -3,60): clean, fully dimensioned, 1:75 A3 (page 1 = main plan)."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels, beam_length2, thin_solid_segments

A2 = os.environ.get("A2") == "1"            # A2 sheet at 1:50 (carpenter's version) instead of A3 at 1:75
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 32)); OY = float(os.environ.get("OY_MM", 30))
OUT = os.environ.get("OUT", "../s1/S1_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

# ---- texts: merge labels that Fespa split into several spans on one baseline ('Δ' '6.1' '25/50 Ανεστρ.', 'Κ' '7  65/30')
T0 = json.load(open("../s1/texts.json"))
def merge_split(T):
    T = [dict(t) for t in T]
    changed = True
    while changed:
        changed = False
        for p in T:
            if not (abs(p["dir"][1]) < 0.2 and re.match(r"^(Δ|Κ)(\s*\d+\.?\d*)?$", p["text"].strip())): continue
            for t in T:
                if t is p or abs(t["dir"][1]) >= 0.2 or p["fonts"] != t["fonts"]: continue
                if abs(p["y1"] - t["y1"]) < 1.5 and 0 <= t["x0"] - p["x1"] <= 3.5:
                    sep = "" if re.match(r"^(Δ|Κ)$", p["text"].strip()) else " "
                    p["text"] = p["text"].rstrip() + sep + t["text"].lstrip(); p["x1"] = t["x1"]; p["y0"] = min(p["y0"], t["y0"])
                    T.remove(t); changed = True; break
            if changed: break
    return T
T = merge_split(T0)

sh = Sheet("../s1/geometry.json", T, scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G = sh.G
# ramp fill zone (Γέμισμα για ράμπα οχημάτων): the original hatch is interrupted by the (removed) rebar labels -> re-hatched uniformly
from shapely.geometry import Polygon as _Poly, Point as _Pt
RAMP = [(1645.48, 796.9), (1835.2, 796.9), (1837.52, 966.84), (1645.48, 966.84)]
_ramp = _Poly(RAMP)
sh.draw_geometry(rehatch_columns=False, drop=lambda l: l.get("hatch") and _ramp.contains(_Pt((l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2)))
sh.hatch_polygon(RAMP, spacing=3.2, w=0.18)
lab = parse_labels(T, G["region"])
segs = thin_solid_segments("../s1/S1.pdf", G["region"])

# ------------------------------------------------------------------ perimeter chains (source coords)
# North (outer face skewed: K11 530.02 -> K15 522.93)
top = sh.Y(522.93)
xsN = [592.58, 618.22, 934.00, 962.35, 1248.64, 1276.99, 1421.55, 1450.03, 1819.81, 1845.32]
extN = {592.58: 530.02, 618.22: 529.88, 934.00: 527.89, 962.35: 527.89, 1248.64: 526.05, 1276.99: 526.05, 1421.55: 525.20, 1450.03: 525.20, 1819.81: 523.07, 1845.32: 522.93}
sh.hchain(xsN, top - ROW, -1, ext=extN, narrow_perp=True)
axN = [605.40, 948.18, 1262.82, 1435.79, 1832.78]
sh.hchain(axN, top - 2 * ROW, -1, ext={605.40: 529.95, 948.18: 527.89, 1262.82: 526.05, 1435.79: 525.20, 1832.78: 523.0}, narrow_perp=True)
sh.hchain([592.58, 1845.32], top - 3 * ROW, -1)
# South (outer face 1488.41; strip corner 783.76, K19 notch 820.61, X-block 1645.48-1677.2)
bot = sh.Y(1488.41)
xsS = [783.76, 800.77, 820.61, 834.79, 1053.05, 1081.40, 1410.21, 1438.56, 1631.31, 1645.48, 1677.20, 1831.01, 1859.35]
extS = {x: 1488.41 for x in xsS}; extS[800.77] = 1471.40
sh.hchain(xsS, bot + ROW, +1, ext=extS, narrow_perp=True)
axS = [817.78, 1067.23, 1424.39, 1638.40, 1845.18]
sh.hchain(axS, bot + 2 * ROW, +1, ext={x: 1488.41 for x in axS}, narrow_perp=True)
sh.hchain([783.76, 820.61, 1859.35], bot + 3 * ROW, +1, narrow_perp=True)
# South-west wing (strip bottom 1165.26) : 0.45 | 2.90 | 0.30  and 3.65 (designer)
ysw = sh.Y(1165.26)
sh.hchain([593.71, 619.21, 783.76, 800.77], ysw + ROW, +1, ext={593.71: 1165.26, 619.21: 1148.26}, narrow_perp=True)
sh.hchain([593.71, 800.77], ysw + 2 * ROW, +1)
# thickness of the strip / wall between K20 and K19 (designer: 0.30 at y=1441)
sh.hchain([783.76, 800.77, 814.94], sh.Y(1441.0), -1, size=6.4, narrow_perp=True)
# West
west = sh.X(592.58)
ysW = [529.88, 555.53, 875.98, 904.48, 1122.74, 1134.08, 1148.26, 1165.26, 1488.27]
extW = {529.88: 592.58, 555.53: 592.58, 875.98: 593.14, 904.48: 593.14, 1122.74: 593.57, 1134.08: 593.57, 1148.26: 593.71, 1165.26: 593.71, 1488.27: 783.76}
sh.vchain(ysW, west - ROW, -1, ext=extW, narrow_h=True)
axW = [542.78, 890.23, 1135.50]
sh.vchain(axW, west - 2 * ROW, -1, ext={542.78: 592.58, 890.23: 593.14, 1135.50: 593.6}, narrow_h=True)
sh.vchain([529.88, 1148.26, 1165.26, 1488.27], west - 3 * ROW, -1, narrow_h=True)
# East (outer face skewed: K15 1845.75 -> K28 1859.35); rows pushed out to leave room for the wall note
east = sh.X(1859.35); E0 = (14.0 if A2 else 12.0) * MM
ysE = [522.93, 548.73, 782.45, 811.07, 966.84, 995.32, 1015.03, 1043.51, 1167.95, 1196.59, 1284.04, 1312.52, 1411.88, 1440.37, 1474.24, 1488.41]
extE = {522.93: 1845.32, 548.73: 1845.75, 782.45: 1849.43, 811.07: 1849.43, 966.84: 1852.12, 995.32: 1852.12, 1015.03: 1852.83, 1043.51: 1852.83,
        1167.95: 1855.10, 1196.59: 1855.10, 1284.04: 1856.80, 1312.52: 1856.80, 1411.88: 1858.64, 1440.37: 1858.64, 1474.24: 1859.35, 1488.41: 1859.35}
sh.vchain(ysE, east + E0, +1, ext=extE, narrow_h=True)
axE = [535.83, 796.76, 981.08, 1029.27, 1182.27, 1298.28, 1426.13, 1481.33]
sh.vchain(axE, east + E0 + ROW, +1, ext={535.83: 1845.5, 796.76: 1849.43, 981.08: 1852.12, 1029.27: 1852.83, 1182.27: 1855.10, 1298.28: 1856.80, 1426.13: 1858.64, 1481.33: 1859.35}, narrow_h=True)
sh.vchain([522.93, 1488.41], east + E0 + 2 * ROW, +1)

# ------------------------------------------------------------------ interior locating chains (columns / core inside the raft)
# H1 (y=600): W wall inner face -> Κ1 -> Κ2 -> E wall inner face
sh.hchain([607.31, 934.00, 951.01, 1149.43, 1262.81, 1832.3], sh.Y(600.0), -1, size=6.6, narrow_perp=True,
          ext={934.00: 640.99, 951.01: 640.99, 1149.43: 640.99, 1262.81: 640.99})
# H2 (y=968): W wall -> Κ10 -> Κ3 -> core (Κ4/Κ5/Κ6) -> core line
sh.hchain([607.74, 934.00, 985.02, 1421.55, 1438.56, 1515.09, 1645.48], sh.Y(968.0), -1, size=6.6, narrow_perp=True,
          ext={934.00: 904.48, 985.02: 904.48, 1421.55: 904.48, 1438.56: 904.48, 1515.09: 901.64})
# H3 (y=1100): W wall -> Κ20 -> Κ9 -> Κ8 -> Κ7
sh.hchain([607.74, 789.43, 814.94, 968.02, 1081.40, 1398.87, 1438.56, 1608.63, 1631.31], sh.Y(1100.0), -1, size=6.6, narrow_perp=True,
          ext={789.43: 1131.25, 814.94: 1131.25, 968.02: 1131.25, 1081.40: 1131.25, 1398.87: 1128.41, 1438.56: 1128.41, 1608.63: 1131.25})
# V1 (x=1300): N wall inner face -> Κ2 -> S wall inner face ;  V2 (x=1496): N wall -> core / Κ3 -> S wall
sh.vchain([540.1, 640.99, 658.01, 1474.24], sh.X(1300.0), +1, size=6.6, narrow_h=True)
sh.vchain([539.1, 782.73, 901.64, 1474.24], sh.X(1496.0), +1, size=6.6, narrow_h=True, ext={782.73: 1515.09, 901.64: 1515.09})
# perimeter wall thickness (0.25) – one dimension across each wall, written inside the wall band
def wall_faces_v(y):   # x of the two E/W wall face lines crossing height y (nearly vertical 0.85 lines)
    xs = []
    for l in G["lines"]:
        if l["w"] >= 0.85 and not l.get("dashed") and abs(l["x1"] - l["x0"]) < 6 and min(l["y0"], l["y1"]) <= y <= max(l["y0"], l["y1"]):
            xs.append(l["x0"] + (l["x1"] - l["x0"]) * (y - l["y0"]) / ((l["y1"] - l["y0"]) or 1))
    return xs
def wall_faces_h(x):
    ys = []
    for l in G["lines"]:
        if l["w"] >= 0.85 and not l.get("dashed") and abs(l["y1"] - l["y0"]) < 6 and min(l["x0"], l["x1"]) <= x <= max(l["x0"], l["x1"]):
            ys.append(l["y0"] + (l["y1"] - l["y0"]) * (x - l["x0"]) / ((l["x1"] - l["x0"]) or 1))
    return ys
wW = sorted(v for v in wall_faces_v(700.0) if 585 < v < 615); wE = sorted(v for v in wall_faces_v(880.0) if 1825 < v < 1860)
wN = sorted(v for v in wall_faces_h(1100.0) if 520 < v < 560); wS = [1474.24, 1488.41]
sh.hchain([wW[0], wW[-1]], sh.Y(700.0), -1, size=6.4, narrow_perp=True, mask=True)      # W wall
sh.vchain([wN[0], wN[-1]], sh.X(1100.0), -1, size=6.4, narrow_h=True, mask=True)        # N wall
sh.hchain([wE[0], wE[-1]], sh.Y(880.0), -1, size=6.4, narrow_perp=True, mask=True)      # E wall
sh.vchain(wS, sh.X(1250.0), -1, size=6.4, narrow_h=True, mask=True)                     # S wall
# core (Κ4/Κ5/Κ6) inner clear dimensions
sh.hchain([1515.09, 1631.31], sh.Y(872.0), -1, size=6.6)
sh.vchain([796.90, 887.47], sh.X(1618.0), -1, size=6.6)

# ------------------------------------------------------------------ designer's interior dimensions (recovered; rebar-length dims skipped)
dims = json.load(open("../s1/dims.json"))
FOOT = (560, 500, 1880, 1500)
# rebar bar-length dimensions (both ends on bar ends) and dims replaced by the chains -> skipped
SKIP_DIMS = {("1.60", 1343, 559), ("1.15", 1504, 607), ("1.85", 1253, 672), ("1.30", 1132, 855), ("1.60", 1186, 1349), ("1.15", 974, 1398),
             ("1.60", 733, 764), ("1.15", 790, 926), ("0.50", 1038, 1162), ("4.30", 1045, 1026), ("4.65", 1045, 773), ("1.85", 1078, 830), ("1.30", 1162, 1007),
             ("3.65", 697, 1184), ("0.30", 634, 1157), ("0.30", 792, 1433), ("0.81", 1654, 1503), ("5.70", 740, 1310)}
TPOS = {("0.50", 1645, 808): (1661.5, 813.0), ("0.50", 1577, 783): (1587.5, 766.5), ("0.50", 1582, 902): (1592.5, 924.0)}
# snap endpoints to structural lines (arrow-tip detection may return the arrowhead base)
VX = []; HY = []
for l in G["lines"]:
    if l["w"] < 0.85 or l.get("dashed"): continue
    if abs(l["x0"] - l["x1"]) < 0.6: VX.append((l["x0"], min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
    elif abs(l["y0"] - l["y1"]) < 0.6: HY.append((l["y0"], min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
for c in G["columns"]:
    n = len(c)
    for i in range(n):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % n]
        if abs(x0 - x1) < 0.6: VX.append((x0, min(y0, y1), max(y0, y1)))
        elif abs(y0 - y1) < 0.6: HY.append((y0, min(x0, x1), max(x0, x1)))
def snap_x(x, y, tol=4.0):
    c = [vx for vx, a, b in VX if abs(vx - x) <= tol and a - 300 <= y <= b + 300]
    return min(c, key=lambda v: abs(v - x)) if c else None
def snap_y(y, x, tol=4.0):
    c = [hy for hy, a, b in HY if abs(hy - y) <= tol and a - 300 <= x <= b + 300]
    return min(c, key=lambda v: abs(v - y)) if c else None
for d in dims:
    if d.get("unresolved"): continue
    if not (FOOT[0] <= d["x0"] <= FOOT[2] and FOOT[1] <= d["y0"] <= FOOT[3] and FOOT[0] <= d["x1"] <= FOOT[2] and FOOT[1] <= d["y1"] <= FOOT[3]): continue
    key = (d["value"], round(d["tx"]), round(d["ty"]))
    if key in SKIP_DIMS: continue
    v = float(d["value"]); x0, y0, x1, y1 = d["x0"], d["y0"], d["x1"], d["y1"]
    if d["dir"] == "H":
        sx0, sx1 = snap_x(x0, y0), snap_x(x1, y1)
        if sx0 is not None and sx1 is not None and abs((sx1 - sx0) / S - v) <= 0.015: x0, x1 = sx0, sx1
    else:
        sy0, sy1 = snap_y(y0, x0), snap_y(y1, x1)
        if sy0 is not None and sy1 is not None and abs((sy1 - sy0) / S - v) <= 0.015: y0, y1 = sy0, sy1
    sh.dim_generic(x0, y0, x1, y1, d["value"], text_side=d["side"], size=6.4, tpos=TPOS.get(key), mask=_ramp.contains(_Pt(d["tx"], d["ty"])))
# designer's dims the automatic recovery could not resolve (verified against the drawing lines)
sh.dim_generic(1795.0, 1167.95, 1795.0, 1176.60, "0.15", text_side=-1, size=6.0, tpos=(1797.0, 1165.5))   # Δ6.1 visible strip
sh.dim_generic(1673.5, 1290.00, 1673.5, 1298.49, "0.15", text_side=-1, size=6.0, tpos=(1676.0, 1308.0))   # Δ7.1 visible strip
sh.dim_generic(1684.88, 1195.2, 1693.40, 1195.2, "0.15", text_side=-1, size=6.0, tpos=(1650.0, 1197.5))   # Δ9.1 visible strip

# ------------------------------------------------------------------ column labels
COL_POS = {  # name -> (x, y_baseline, rot)   (perimeter columns moved inside the building; east wall labels rotated along the wall)
    "Κ11": (624.0, 566.0, 0), "Κ12": (968.0, 558.0, 0), "Κ13": (1282.0, 556.0, 0), "Κ14": (1362.0, 553.0, 0), "Κ15": (1728.0, 564.0, 0),
    "Κ22": (616.0, 884.0, 0), "Κ21": (626.0, 1118.0, 0), "Κ20": (696.0, 1129.0, 0), "Κ10": (846.0, 882.0, 0), "Κ5": (1662.0, 842.0, 0, True), "Κ1": (846.0, 632.0, 0),
    "Κ2": (1150.0, 634.0, 0), "Κ6": (1530.0, 936.0, 0), "Κ31": (1380.0, 1468.0, 0),
    "Κ19": (838.0, 1468.0, 0), "Κ30": (1085.0, 1468.0, 0), "Κ31": (1442.0, 1468.0, 0), "Κ18": (1572.0, 1504.0, 0), "Κ28": (1768.0, 1504.0, 0),
    "Κ16": (1831.0, 778.0, 90), "Κ24": (1831.0, 962.0, 90, True), "Κ25": (1831.0, 1103.0, 90), "Κ32": (1831.0, 1256.0, 90), "Κ34": (1822.0, 1374.0, 90), "Κ26": (1831.0, 1396.0, 90),
    "Κ29": (1571.0, 990.0, 0), "Κ27": (1571.0, 1011.0, 0), "Κ7": (1571.0, 1163.0, 0), "Κ23": (1571.0, 1206.0, 0), "Κ33": (1571.0, 1278.0, 0), "Κ17": (1571.0, 1422.0, 0),
}
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", re.sub(r"^Κ\s+", "Κ", t["text"].strip())); name = s.split()[0]
    pos = COL_POS.get(name)
    if pos is None: pos = (t["x0"], t["y1"] - 1.5, 0)
    sh.col_label(pos[0], pos[1], s, rot=pos[2], size=7.6, mask=(len(pos) > 3 and pos[3]))

# ------------------------------------------------------------------ beam labels
def best_slot(G, horiz, perp, a0, a1, w_src, bw, margin=4.0):
    return (a0 + a1) / 2
L_OVERRIDE = {"Δ6.1": (1840.50 - 1645.48) / S, "Δ7.1": (1842.20 - 1645.48) / S, "Δ9.1": (1284.31 - 1182.27) / S}   # K23->K32, K33->K34, Δ6.1->Δ7.1
POS_OVERRIDE = {"Δ6.1": (1663.0, 1164.0, 0, 6.4), "Δ7.1": (1712.0, 1310.0, 0, 6.4), "Δ9.1": (1696.5, 1282.3, 90, 5.4)}
COMPACT = {"Δ9.1"}   # single-spaced label written inside the beam band (white mask behind it)
for t in lab["beams"]:
    s = re.sub(r"\s+", " ", re.sub(r"^Δ\s+", "Δ", t["text"].strip()))
    m = re.match(r"^Δ\s*(\d+\.\d+)\s+(\d+)/(\d+)\s*(.*)$", s)
    name, b, h, rest = "Δ" + m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()
    L = L_OVERRIDE.get(name); ends = None; horiz = abs(t["dir"][1]) < 0.2; how = "manual"
    if L is None: L, c, horiz, how, br, ends = beam_length2(G, t, b, segs)
    txt = "%s  %d/%s%s  L=%s" % (name, b, h, ("  " + rest) if rest else "", ("%.2f" % L) if L else "?")
    if name in COMPACT: txt = re.sub(r"\s+", " ", txt)
    print("BEAM", txt, how, ends)
    size = 6.4; w_src = sh.tw(txt, size) / sh.K
    if name in POS_OVERRIDE: x, y, rot, size = POS_OVERRIDE[name]
    elif ends and horiz: x, y, rot = (ends[0][0] + ends[1][0]) / 2 - w_src / 2, t["y1"] - 1.5, 0
    elif ends: x, y, rot = t["x1"] - 1.0, (ends[0][1] + ends[1][1]) / 2 + w_src / 2, 90
    elif horiz: x, y, rot = t["x0"], t["y1"] - 1.5, 0
    else: x, y, rot = t["x1"] - 1.0, t["y1"], 90
    sh.beam_label(x, y, txt, rot=rot, size=size, mask=(name in COMPACT))
for t in lab["ez"]:
    s = re.sub(r"\s+", "  ", t["text"].strip())
    vert = abs(t["dir"][1]) >= 0.2
    if s.startswith("Ε.Ζ.  70/80"): sh.beam_label(1463.0, 946.0, s, rot=90, size=6.2); continue   # beside the E.Z. strip, clear of the chains
    if vert: sh.beam_label(t["x1"] - 1.0, t["y1"], s, rot=90, size=6.2)
    else: sh.beam_label(t["x0"], t["y1"] - 1.5, s, size=6.2)

# slabs
def nearest(items, cx, cy, maxd=60):
    best = None
    for t in items:
        d = math.hypot((t["x0"] + t["x1"]) / 2 - cx, (t["y0"] + t["y1"]) / 2 - cy)
        if d < maxd and (best is None or d < best[0]): best = (d, t)
    return best[1] if best else None
CIRC_MOVE = {(1744, 1361): (1780.0, 1390.0)}
for c in G["circles"]:
    pt = nearest(lab["slabs"], c["cx"], c["cy"], 40); ht = nearest(lab["hs"], c["cx"], c["cy"], 40)
    name = pt["text"].strip() if pt else "Π"; h = re.sub(r"\D", "", ht["text"]) if ht else "?"
    cx, cy = CIRC_MOVE.get((round(c["cx"]), round(c["cy"])), (c["cx"], c["cy"]))
    sh.slab_label(cx, cy, name, h, r=2.8 * MM)

# levels: value (Bookman) + tag (Σ.Μ. / Α.Δ.Σ.Ε.) right below it
tags = [t for t in T if t["text"].strip() in ("Σ.Μ.", "Α.Δ.Σ.Ε.")]
LEV_MOVE = {(1212, 975): (1212.0, 1005.0), (1212, 1011): (1212.0, 1041.0)}   # centre pair moved below the chain H2
for t in lab["levels"]:
    s = t["text"].strip()
    tag = nearest(tags, (t["x0"] + t["x1"]) / 2, t["y1"] + 8, 20)
    x0, y1 = LEV_MOVE.get((round(t["x0"]), round(t["y1"])), (t["x0"], t["y1"]))
    sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)
    if tag: sh.stext(x0 + 0.5, y1 + 8.5, tag["text"].strip(), size=5.6)

# notes (rebar parts of the notes omitted)
NOTES = [(1659.0, 640.0, ["Πλάκα κοιτό-", "στρωσης h=40 cm."], 6.0, 0, False),
         (1193.0, 939.0, ["Πλάκα γενικής", "κοιτόστρωσης h=80 cm."], 6.0, 0, False),
         (1182.0, 1255.0, ["Πλάκα κοιτό-", "στρωσης h=40 cm."], 6.0, 0, False),
         (1668.0, 864.0, ["Γέμισμα για ράμπα οχημάτων"], 6.0, 0, True),
         (1721.0, 1341.0, ["Κεκλιμένο τοιχίο για", "στήριξη της πλάκας."], 6.0, 0, False),
         (1884.0, 1300.0, ["Τοιχείο έως το ύψος της πλάκας για στήριξή της."], 5.8, 90, True)]
for x, y, lines, size, rot, mask in NOTES: sh.note(x, y, lines, size=size, rot=rot, mask=mask)
sh.sline(1719.0, 1338.0, 1695.4, 1277.8, 0.3)   # leader of the inclined-wall note (designer's target point)

# ------------------------------------------------------------------ title
if A2:
    TB = sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "(-4,00 / -3,60)"],
                      ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
  sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "(-4,00 / -3,60)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                ["Εγκεκριμένο σχέδιο Σ1", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ1 – ΓΕΩΜΕΤΡΙΑ 1:%d (1/2)" % SCALE, width_mm=420 - 8 - TITLE_X,
                legend=["Διαστάσεις σε m · b/h σε cm", "h πλάκας σε cm", "L = καθαρό μήκος δοκού", "μεταξύ παρειών στηρίξεων", "Ανεστρ. = ανεστραμμένη δοκός", "Σ.Μ. / Α.Δ.Σ.Ε.: στάθμες κατά Σ1", "Οπλισμοί κατά Σ1"])
sh.save(OUT, meta={"title": "Σ1 – Ξυλότυπος θεμελίωσης – Γεωμετρία/Διαστασιολόγηση 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts("../s1/texts_out.json")
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

