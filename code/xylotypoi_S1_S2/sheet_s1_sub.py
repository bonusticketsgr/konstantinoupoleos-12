"""Σ1 – Ξυλότυπος θεμελίωσης υποσταθμού (-6,69): clean, fully dimensioned, 1:75 A3 (page 2 of Σ1)."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels

A2 = os.environ.get("A2") == "1"
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 150)); OY = float(os.environ.get("OY_MM", 60))
OUT = os.environ.get("OUT", "../s1/S1_sub_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

T = json.load(open("../s1/texts.json"))
sh = Sheet("../s1/geom_sub.json", T, scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G = sh.G
sh.draw_geometry(rehatch_columns=False)
lab = parse_labels(T, G["region"])

# ------------------------------------------------------------------ perimeter chains
# West wall (x 2468.08) – column faces / axes / overall
west = sh.X(2468.08)
ysW = [966.84, 995.18, 1015.03, 1057.54, 1131.25, 1148.26, 1167.95, 1196.30, 1284.17, 1312.52, 1411.88, 1440.22, 1460.06, 1488.41]
sh.vchain(ysW, west - ROW, -1, ext={y: 2468.08 for y in ysW}, narrow_h=True)
axW = [981.01, 1036.29, 1139.76, 1182.13, 1298.35, 1426.05, 1474.24]
sh.vchain(axW, west - 2 * ROW, -1, ext={y: 2468.08 for y in axW}, narrow_h=True)
sh.vchain([966.84, 1488.41], west - 3 * ROW, -1)
# East wall (skewed: 2688.47 at the top -> 2696.12 at the bottom)
east = sh.X(2696.12)
ysE = [966.84, 995.32, 1015.03, 1043.51, 1167.95, 1196.59, 1284.04, 1312.52, 1411.88, 1440.37, 1474.24, 1488.41]
extE = {966.84: 2688.47, 995.32: 2688.9, 1015.03: 2689.18, 1043.51: 2689.6, 1167.95: 2691.45, 1196.59: 2691.87, 1284.04: 2693.15, 1312.52: 2693.57,
        1411.88: 2694.99, 1440.37: 2695.42, 1474.24: 2696.12, 1488.41: 2696.12}
sh.vchain(ysE, east + ROW, +1, ext=extE, narrow_h=True)
axE = [981.08, 1029.27, 1182.27, 1298.28, 1426.13, 1481.33]
sh.vchain(axE, east + 2 * ROW, +1, ext={981.08: 2688.7, 1029.27: 2689.4, 1182.27: 2691.7, 1298.28: 2693.4, 1426.13: 2695.2, 1481.33: 2696.12}, narrow_h=True)
sh.vchain([966.84, 1488.41], east + 3 * ROW, +1)
# North (top wall outer face 966.84): 0.25 | 3.39 | 0.25  and 3.89 (designer)
top = sh.Y(966.84)
sh.hchain([2468.08, 2482.25, 2674.30, 2688.47], top - ROW, -1, ext={x: 966.84 for x in [2468.08, 2482.25, 2674.30, 2688.47]}, narrow_perp=True)
sh.hchain([2468.08, 2688.47], top - 2 * ROW, -1)
# South (bottom wall outer face 1488.41): 0.25 | 3.27 | 0.50  and 4.02 (designer)
bot = sh.Y(1488.41)
sh.hchain([2468.08, 2482.25, 2667.78, 2696.12], bot + ROW, +1, ext={x: 1488.41 for x in [2468.08, 2482.25, 2667.78, 2696.12]}, narrow_perp=True)
sh.hchain([2468.08, 2696.12], bot + 2 * ROW, +1)
# interior: walls at -3,64 (1015.03-1029.20 and 1426.05-1440.22) and the clear spans between the walls
sh.vchain([966.84, 981.01, 1015.03, 1029.20, 1426.05, 1440.22, 1474.24, 1488.41], sh.X(2600.0), -1, size=6.4, ext={y: 2600.0 for y in []}, narrow_h=True)

# ------------------------------------------------------------------ column labels (inside the walls)
COL_POS = {"Κ29": (2488.0, 990.0), "Κ27": (2488.0, 1052.0), "Κ7": (2488.0, 1145.0), "Κ23": (2488.0, 1191.0), "Κ33": (2488.0, 1307.0), "Κ17": (2488.0, 1422.0), "Κ18": (2488.0, 1470.0),
           "Κ24": (2614.0, 990.0), "Κ25": (2614.0, 1052.0), "Κ32": (2616.0, 1191.0), "Κ34": (2618.0, 1307.0), "Κ26": (2620.0, 1422.0), "Κ28": (2606.0, 1470.0)}
seen = set()
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", re.sub(r"^Κ\s+", "Κ", t["text"].strip())); name = s.split()[0]
    if name in seen or name not in COL_POS: continue
    seen.add(name); x, y = COL_POS[name]
    sh.col_label(x, y, s, size=7.6)

# levels + notes
for x0, y1, s, tag in [(2562.0, 1145.0, "-6,24", "Σ.Μ."), (2562.0, 1181.0, "-6,69", "Α.Δ.Σ.Ε.")]:
    sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)
    sh.stext(x0 + 0.5, y1 + 8.5, tag, size=5.6)
sh.note(2513.0, 1110.0, ["Πλάκα γενικής", "κοιτόστρωσης h=35 cm."], size=6.0)
sh.note(2531.0, 1062.0, ["Άνω στ. τοιχίου -3,64."], size=6.0); sh.sline(2572.0, 1054.0, 2582.0, 1030.5, 0.3)   # leader to the wall 1015-1029
sh.note(2532.0, 1403.0, ["Άνω στ. τοιχίου -3,64."], size=6.0); sh.sline(2572.0, 1405.5, 2582.0, 1425.0, 0.3)   # leader to the wall 1426-1440
# plan title under the plan
sh.stext(2468.08, 1488.41 + 3 * ROW / sh.K + 10 / sh.K, "ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ ΥΠΟΣΤΑΘΜΟΥ (-6,69)", size=8.0, bold=True)

# ------------------------------------------------------------------ title
if A2:
    sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "ΥΠΟΣΤΑΘΜΟΥ (-6,69)"],
                 ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
  sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "ΥΠΟΣΤΑΘΜΟΥ (-6,69)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                ["Εγκεκριμένο σχέδιο Σ1", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ1 – ΓΕΩΜΕΤΡΙΑ 1:%d (2/2)" % SCALE, width_mm=420 - 8 - TITLE_X,
                legend=["Διαστάσεις σε m · b/h σε cm", "Σ.Μ. / Α.Δ.Σ.Ε.: στάθμες κατά Σ1", "Οπλισμοί κατά Σ1"])
sh.save(OUT, meta={"title": "Σ1 – Ξυλότυπος θεμελίωσης υποσταθμού – Γεωμετρία 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts("../s1/texts_out_sub.json")
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

