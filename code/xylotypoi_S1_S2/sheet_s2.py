"""Σ2 – Ξυλότυπος οροφής υπογείου (+0,05/+0,30): clean, fully dimensioned, 1:75 A3."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels, beam_length2, thin_solid_segments

DIR = os.environ.get("DIR", "../s2")          # data directory (../s2 = original Σ2, ../s2r = revision 24/09/2026)
A2 = os.environ.get("A2") == "1"            # A2 sheet at 1:50 (carpenter's version) instead of A3 at 1:75
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 40)); OY = float(os.environ.get("OY_MM", 30))
OUT = os.environ.get("OUT", DIR + "/S2_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

sh = Sheet(DIR + "/geometry.json", DIR + "/texts.json", scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G, T = sh.G, sh.T
sh.draw_geometry(rehatch_columns=False)
lab = parse_labels(T, G["region"])
segs = thin_solid_segments(DIR + "/" + os.environ.get("PDF", "S2.pdf"), G["region"])

# ------------------------------------------------------------------ perimeter chains (source coords)
top = sh.Y(528.46)
xsN = [906.86, 932.51, 1248.28, 1276.77, 1562.92, 1591.41, 1735.97, 1764.32, 2133.95, 2159.88]
extN = {906.86: 535.40, 932.51: 535.5, 1248.28: 533.42, 1276.77: 533.42, 1562.92: 531.58, 1591.41: 531.58, 1735.97: 530.73, 1764.32: 530.73, 2133.95: 528.46, 2159.88: 528.46}
sh.hchain(xsN, top - ROW, -1, ext=extN, narrow_perp=True)
axN = [919.69, 1262.53, 1577.17, 1750.15, 2146.92]
sh.hchain(axN, top - 2 * ROW, -1, ext={919.69: 535.4, 1262.53: 533.42, 1577.17: 531.58, 1750.15: 530.73, 2146.92: 528.46}, narrow_perp=True)
sh.hchain([906.86, 2159.88], top - 3 * ROW, -1)
bot = sh.Y(1493.94)
xsS = [1115.06, 1134.90, 1149.07, 1367.48, 1395.82, 1724.63, 1752.98, 1945.59, 1959.77, 2145.14, 2173.49]
extS = {x: 1493.94 for x in xsS}; extS[1115.06] = 1476.93
sh.hchain(xsS, bot + ROW, +1, ext=extS, narrow_perp=True)
axS = [1132.07, 1381.65, 1738.81, 1952.68, 2159.32]
sh.hchain(axS, bot + 2 * ROW, +1, ext={x: 1493.94 for x in axS}, narrow_perp=True)
sh.hchain([1115.06, 1134.90, 2173.49], bot + 3 * ROW, +1, narrow_perp=True)
xsSW = [907.99, 933.50, 1103.72, 1115.06]
sh.hchain(xsSW, sh.Y(1153.79) + ROW, +1, ext={907.99: 1153.79, 933.50: 1153.79, 1103.72: 1153.79, 1115.06: 1165.12}, narrow_perp=True)
sh.hchain([907.99, 1115.06], sh.Y(1153.79) + 2 * ROW, +1)
west = sh.X(906.86)
ysW = [535.40, 546.89, 561.06, 688.19, 699.53, 823.26, 834.60, 881.65, 910.01, 1128.13, 1153.79]
sh.vchain(ysW, west - ROW, -1, ext={y: 906.86 for y in ysW}, narrow_h=True)
axW = [548.23, 693.86, 828.93, 895.83, 1140.96]
sh.vchain(axW, west - 2 * ROW, -1, ext={y: 906.86 for y in axW}, narrow_h=True)
sh.vchain([535.40, 1153.79], west - 3 * ROW, -1)
east = sh.X(2173.49)
ysE = [528.46, 554.26, 787.97, 816.60, 1020.55, 1049.04, 1173.62, 1202.11, 1289.56, 1318.19, 1417.40, 1445.90, 1479.77, 1493.94]
extE = {528.46: 2159.88, 554.26: 2159.88, 787.97: 2163.71, 816.60: 2163.71, 1020.55: 2167.11, 1049.04: 2167.11, 1173.62: 2169.24, 1202.11: 2169.24,
        1289.56: 2170.94, 1318.19: 2170.94, 1417.40: 2172.78, 1445.90: 2172.78, 1479.77: 2173.49, 1493.94: 2173.49}
sh.vchain(ysE, east + ROW, +1, ext=extE, narrow_h=True)
axE = [541.36, 802.29, 1034.80, 1187.87, 1303.88, 1431.65, 1486.86]
sh.vchain(axE, east + 2 * ROW, +1, ext={541.36: 2159.88, 802.29: 2163.71, 1034.80: 2167.11, 1187.87: 2169.24, 1303.88: 2170.94, 1431.65: 2172.78, 1486.86: 2173.49}, narrow_h=True)
sh.vchain([528.46, 1493.94], east + 3 * ROW, +1)

# ------------------------------------------------------------------ interior locating chains (walls / beams / columns inside the plan)
# H1 (north half, y=770): W wall inner face -> Δ6.1/Κ1 line -> Δ9.5/Κ3 line
sh.hchain([921.5, 1248.43, 1265.44, 1735.97, 1752.98], sh.Y(770.0), -1, size=6.6, narrow_perp=True)
# H2 (south half, y=1386): wall Κ20-Κ19 -> Δ23.1 -> Δ24.1 -> core line Κ17
sh.hchain([1129.23, 1378.80, 1395.82, 1735.97, 1752.98, 1945.59, 1959.77], sh.Y(1386.0), -1, size=6.6, narrow_perp=True)
# V1 (x=1405): N wall inner face -> Δ1.1 -> Δ3.1 -> Δ4.3 ;  V1b (x=1600): Δ4.3 -> S wall inner face
sh.vchain([546.7, 646.52, 663.53, 893.00, 910.01, 1136.60, 1153.60], sh.X(1405.0), +1, size=6.6, narrow_h=True)
sh.vchain([1153.60, 1479.77], sh.X(1600.0), +1, size=6.6, narrow_h=True)
# V2 (x=1900): core bottom face -> Δ12.1 (position of the beam below the core)
sh.vchain([907.17, 1048.90, 1063.10], sh.X(1900.0), +1, size=6.6, narrow_h=True)
# V3 (x=2122): east strip – N wall inner face -> Δ21.1 -> strip -> beams/strips between the east-wall columns -> S wall inner face
sh.vchain([544.8, 788.26, 805.26, 845.09, 1020.55, 1031.80, 1173.62, 1182.13, 1289.84, 1304.02, 1434.40, 1445.80, 1479.77], sh.X(2122.0), +1, size=6.6, narrow_h=True)
# V4 (x=1060): west band – N wall inner face -> Δ8.1 -> south wall of the SW wing
sh.vchain([548.5, 893.00, 910.01, 1139.60, 1153.79], sh.X(1060.0), -1, size=6.6, narrow_h=True)
# perimeter wall thickness (0.25) – one dimension across each wall, written inside the wall band
sh.hchain([907.3, 921.5], sh.Y(760.0), -1, size=6.4, narrow_perp=True, mask=True)       # W wall
sh.vchain([534.6, 548.7], sh.X(1100.0), -1, size=6.4, narrow_h=True, mask=True)         # N wall
sh.hchain([2147.8, 2161.95], sh.Y(700.0), -1, size=6.4, narrow_perp=True, mask=True)    # E wall
sh.vchain([1479.77, 1493.94], sh.X(1250.0), -1, size=6.4, narrow_h=True, mask=True)     # S wall
# core (Κ4/Κ5/Κ6) inner clear dimensions
sh.hchain([1843.54, 1945.59], sh.Y(850.0), -1, size=6.6)
sh.vchain([802.42, 892.99], sh.X(1930.0), -1, size=6.6)

# ------------------------------------------------------------------ designer's interior dimensions (recovered)
dims = json.load(open(DIR + "/dims.json"))
FOOT = (900, 525, 2180, 1500)
SKIP_DIMS = {("3.65", 1011, 1189), ("4.35", 1396, 770)}   # covered by the SW chain (0.45 | 3.00 | 0.20 = 3.65) and by V1 (4.05 + 0.30 = 4.35)
TPOS = {("0.20", 2007, 1201): (2016.5, 1213.5)}        # 20 cm wall: value written beside the wall instead of across it
for d in dims:
    if d.get("unresolved"): continue
    if not (FOOT[0] <= d["x0"] <= FOOT[2] and FOOT[1] <= d["y0"] <= FOOT[3] and FOOT[0] <= d["x1"] <= FOOT[2] and FOOT[1] <= d["y1"] <= FOOT[3]): continue
    key = (d["value"], round(d["tx"]), round(d["ty"]))
    if key in SKIP_DIMS: continue
    sh.dim_generic(d["x0"], d["y0"], d["x1"], d["y1"], d["value"], text_side=d["side"], size=6.4, tpos=TPOS.get(key))
# designer's dims that the automatic recovery could not resolve (verified against the drawing lines):
sh.dim_generic(2142.0, 788.26, 2142.0, 845.09, "1.01", text_side=-1, size=6.4, narrow_h=False)      # beam top -> strip bottom (designer: 1.01 at the east wall)
sh.dim_generic(2053.9, 1173.62, 2053.9, 1182.13, "0.15", text_side=-1, size=6.0, tpos=(2056.5, 1171.0))   # strip 1173.62-1182.13
sh.dim_generic(2049.6, 1295.51, 2049.6, 1304.02, "0.15", text_side=-1, size=6.0, tpos=(2052.5, 1313.5))   # strip 1295.51-1304.02
sh.dim_generic(2014.5, 975.2, 2014.5, 980.86, "0.10", text_side=-1, size=6.0)                        # 1.20 + 0.10 = 1.30 at the K6 leg

# ------------------------------------------------------------------ column labels
COL_POS = {  # name -> (x, y_baseline, rot)   (perimeter columns moved inside the building)
    "Κ11": (938.0, 570.0, 0), "Κ12": (1282.0, 570.0, 0), "Κ13": (1596.0, 570.0, 0), "Κ14": (1676.0, 561.0, 0), "Κ15": (2040.0, 580.0, 0),
    "Κ25": None, "Κ24": (966.0, 698.0, 0), "Κ23": (966.0, 833.0, 0), "Κ22": (930.0, 886.0, 0), "Κ21": (940.0, 1123.0, 0),
    "Κ19": (1153.0, 1473.0, 0), "Κ30": (1399.0, 1473.0, 0), "Κ31": (1757.0, 1473.0, 0), "Κ28": (2082.0, 1510.0, 0),
    "Κ16": (2062.0, 861.0, 0), "Κ34": (2040.0, 1330.0, 0), "Κ26": (2040.0, 1412.0, 0), "Κ1": (1194.0, 631.5, 0),
    "Κ18": (1966.0, 1462.0, 0), "Κ5": (1962.0, 828.0, 0), "Κ3": (1676.0, 802.0, 0),
}
K25_POS = {930: (966.0, 526.0, 0), 2176: (2092.0, 1046.0, 0)}   # two different K25 labels (planted 95/20 at the west wall, 25/50 at the east wall)
K32_POS = {1896: (1888.0, 1186.0, 0), 1960: (1888.0, 1186.0, 0), 2176: (2040.0, 1198.0, 0)}   # inner label (x0 1896 orig. / 1960 rev.), outer label
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", t["text"].strip()); name = s.split()[0]
    pos = None
    if name == "Κ25": pos = K25_POS.get(round(t["x0"]))
    elif name == "Κ32": pos = K32_POS.get(round(t["x0"]))
    elif name in COL_POS: pos = COL_POS[name]
    if pos is None: pos = (t["x0"], t["y1"] - 1.5, 0)
    sh.col_label(pos[0], pos[1], s, rot=pos[2], size=7.6)
sh.col_label(1136.0, 1186.0, "Κ20  30/45/25/50", size=7.6)   # label split in two spans in the source ('Κ' + '20  30/45/25/50')

# ------------------------------------------------------------------ beam labels (centred on the beam's clear span, avoiding blue planted elements)
def best_slot(G, horiz, perp, a0, a1, w_src, bw, margin=4.0):
    """centre of the longest blue-free interval along the beam that fits the label; None if none fits."""
    occ = []
    for l in G["lines"]:
        if not l["blue"] or l["w"] < 0.57: continue
        if horiz:
            if min(l["y0"], l["y1"]) - bw <= perp <= max(l["y0"], l["y1"]) + bw or abs(l["y0"] - perp) <= bw:
                occ.append((min(l["x0"], l["x1"]) - margin, max(l["x0"], l["x1"]) + margin))
        else:
            if min(l["x0"], l["x1"]) - bw <= perp <= max(l["x0"], l["x1"]) + bw or abs(l["x0"] - perp) <= bw:
                occ.append((min(l["y0"], l["y1"]) - margin, max(l["y0"], l["y1"]) + margin))
    occ = [o for o in occ if o[1] > a0 and o[0] < a1]
    occ.sort(); free = []; cur = a0
    for o0, o1 in occ:
        if o0 > cur: free.append((cur, min(o0, a1)))
        cur = max(cur, o1)
    if cur < a1: free.append((cur, a1))
    free = [f for f in free if f[1] - f[0] >= w_src + 2]
    if not free: return None
    f = max(free, key=lambda f: f[1] - f[0])
    return (f[0] + f[1]) / 2

L_OVERRIDE = {"Δ2.1": 1.35, "Δ21.1": 3.34}
POS_OVERRIDE = {"Δ21.1": (1964.0, 802.5, 0, 6.4), "Δ4.4": (1824.0, 1132.0, 0, 6.4), "Δ8.1": (1100.0, 907.5, 0, 6.4),
                "Δ10.1": (1836.0, 891.0, 90, 5.8), "Δ17.1": (1576.0, 644.0, 90, 6.0)}
MULTI_LINE = {"Δ2.1": (1758.0, 757.0, 6.0)}   # label in three lines above the beam (no room beside the planted elements)
for t in lab["beams"]:
    s = re.sub(r"\s+", " ", t["text"].strip())
    m = re.match(r"^Δ\s*(\d+\.\d+)\s+(\d+)/(\d+)\s*(.*)$", s)
    name, b, h, rest = "Δ" + m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()
    L = L_OVERRIDE.get(name); ends = None; horiz = abs(t["dir"][1]) < 0.2
    if L is None:
        L, c, horiz, how, br, ends = beam_length2(G, t, b, segs)
    txt = "%s  %d/%s%s  L=%s" % (name, b, h, ("  " + rest) if rest else "", ("%.2f" % L) if L else "?")
    if name in MULTI_LINE:
        x, y, size = MULTI_LINE[name]; lh = size * 1.25 / sh.K
        parts = [name, "%d/%s" % (b, h)] + ([rest] if rest else []) + ["L=%s" % (("%.2f" % L) if L else "?")]
        for i, p in enumerate(parts): sh.beam_label(x, y + i * lh, p, size=size)
        continue
    if name in POS_OVERRIDE:
        x, y, rot, size = POS_OVERRIDE[name]
    else:
        size = 6.4; c = None
        if ends:
            a0 = min(ends[0][0], ends[1][0]) if horiz else min(ends[0][1], ends[1][1])
            a1 = max(ends[0][0], ends[1][0]) if horiz else max(ends[0][1], ends[1][1])
            perp = (t["y0"] + t["y1"]) / 2 if horiz else (t["x0"] + t["x1"]) / 2
            for size in (6.4, 6.0, 5.6, 5.2):
                w_src = sh.tw(txt, size) / sh.K   # text length in source pt
                c = best_slot(G, horiz, perp, a0, a1, w_src, b / 100 * S)
                if c is not None: break
            if c is None: size = 6.4; w_src = sh.tw(txt, size) / sh.K; c = (a0 + a1) / 2; print("NO FREE SLOT for", name)
            if horiz: x, y, rot = c - w_src / 2, t["y1"] - 1.5, 0
            else: x, y, rot = t["x1"] - 1.0, c + w_src / 2, 90
        elif horiz: x, y, rot = t["x0"], t["y1"] - 1.5, 0
        else: x, y, rot = t["x1"] - 1.0, t["y1"], 90
    sh.beam_label(x, y, txt, rot=rot, size=size)

# strengthened zones
EZ_POS = {(1785, 895): (1760.0, 903.5, 0)}
for t in lab["ez"]:
    s = re.sub(r"\s+", "  ", t["text"].strip())
    key = (round(t["x0"]), round(t["y0"]))
    if key in EZ_POS:
        x, y, rot = EZ_POS[key]; sh.beam_label(x, y, s, rot=rot, size=6.2); continue
    vert = abs(t["dir"][1]) >= 0.2
    if vert: sh.beam_label(t["x1"] - 1.0, t["y1"], s, rot=90, size=6.2)
    else: sh.beam_label(t["x0"], t["y1"] - 1.5, s, size=6.2)

# slabs
def nearest(items, cx, cy, maxd=60):
    best = None
    for t in items:
        d = math.hypot((t["x0"] + t["x1"]) / 2 - cx, (t["y0"] + t["y1"]) / 2 - cy)
        if d < maxd and (best is None or d < best[0]): best = (d, t)
    return best[1] if best else None
CIRC_MOVE = {(2055, 825): (2034.0, 819.5), (1500, 778): (1470.0, 805.0), (1414, 598): (1372.0, 598.0)}   # Π15 out of the planted element; Π3/Π12 off the interior chains
for c in G["circles"]:
    pt = nearest(lab["slabs"], c["cx"], c["cy"], 40); ht = nearest(lab["hs"], c["cx"], c["cy"], 40)
    name = pt["text"].strip() if pt else "Π"; h = re.sub(r"\D", "", ht["text"]) if ht else "?"
    cx, cy = CIRC_MOVE.get((round(c["cx"]), round(c["cy"])), (c["cx"], c["cy"]))
    sh.slab_label(cx, cy, name, h, r=2.8 * MM)

# levels
LEV_MOVE = {(1794, 1382): (1794.0, 1370.0)}   # -0,55 (Π19): clear of the interior chain H2
for t in lab["levels"]:
    s = t["text"].strip(); blue = t["color"] not in (0, 0x000000); vert = abs(t["dir"][1]) >= 0.2
    if blue:
        if vert: sh.stext(t["x1"] - 1.0, t["y1"], s, size=6.6, bold=True, rot=90, color=BLUE)
        else: sh.stext(t["x0"], t["y1"] - 1.5, s, size=6.6, bold=True, color=BLUE)
    else:
        if vert: sh.level_mark(t["x1"] - 6.0, t["y1"] + 8.0, s, r=1.3 * MM, rot=90, textpos=(sh.X(t["x1"]) - 1.5, sh.Y(t["y1"])))
        else:
            x0, y1 = LEV_MOVE.get((round(t["x0"]), round(t["y1"])), (t["x0"], t["y1"]))
            sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)

# notes
NOTES = [(1210.0, 1236.0, ["Γέμισμα μέχρι τη στ. +0,30"], 6.0, 0),
         (1762.0, 630.0, ["Γέμισμα μέχρι", "τη στ. +0,30"], 6.0, 0),
         (1966.0, 1040.0, ["Τμήμα τοιχείου έως το", "ύψος της σκάλας."], 6.0, 0),
         (1578.0, 1128.0, ["Πλάκα επί του φελιζόλ h=18 cm."], 6.0, 90),
         (1622.0, 1240.0, ["Φελιζόλ"], 6.0, 90)]
for x, y, lines, size, rot in NOTES: sh.note(x, y, lines, size=size, rot=rot)

# ------------------------------------------------------------------ title
LEVELS = os.environ.get("LEVELS", "+0,05 / +0,30"); REV = os.environ.get("REV", "")
if A2:
    TB = sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ (%s)" % LEVELS] + (["αναθ. %s" % REV] if REV else []),
                      ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
    sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ (+0,05 / +0,30)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                    ["Εγκεκριμένο σχέδιο Σ2", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ2 – ΓΕΩΜΕΤΡΙΑ 1:%d" % SCALE, width_mm=420 - 8 - TITLE_X,
                    legend=["Διαστάσεις σε m · b/h σε cm", "h πλάκας σε cm", "L = καθαρό μήκος δοκού", "μεταξύ παρειών στηρίξεων", "Ανεστρ. = ανεστραμμένη δοκός", "Οπλισμοί κατά Σ2"])
sh.save(OUT, meta={"title": "Σ2 – Ξυλότυπος οροφής υπογείου – Γεωμετρία/Διαστασιολόγηση 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts(DIR + "/texts_out.json")
# content bbox (for centering)
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

