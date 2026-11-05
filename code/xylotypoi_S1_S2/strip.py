"""strip.py geometry.json texts_out.json H|V pos a0 a1 [halfwidth]: what crosses a horizontal (y=pos, x in a0..a1) or vertical strip (x=pos, y in a0..a1)."""
import json, sys, math
from shapely.geometry import box, LineString, Polygon, Point
G = json.load(open(sys.argv[1])); TO = json.load(open(sys.argv[2]))
mode, pos, a0, a1 = sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
hw = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
bb = box(a0, pos - hw, a1, pos + hw) if mode == "H" else box(pos - hw, a0, pos + hw, a1)
items = []
for l in G["lines"]:
    if l.get("hatch"): continue
    ln = LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])])
    if not ln.intersects(bb): continue
    dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; L = math.hypot(dx, dy)
    perp = (abs(dx) < 0.02 * L + 0.5) if mode == "H" else (abs(dy) < 0.02 * L + 0.5)   # crossing element face (tick position)
    kind = "PERP-FACE" if perp else "ALONG/OBLIQUE"
    items.append(("%s w=%s%s%s (%.1f,%.1f)-(%.1f,%.1f)" % (kind, l["w"], " blue" if l["blue"] else "", " dashed" if l.get("dashed") else "", l["x0"], l["y0"], l["x1"], l["y1"]), min(l["x0"], l["x1"]) if mode == "H" else min(l["y0"], l["y1"])))
for c in G["columns"]:
    if Polygon(c).intersects(bb):
        xs = [p[0] for p in c]; ys = [p[1] for p in c]
        items.append(("COLUMN %.1f-%.1f x %.1f-%.1f" % (min(xs), max(xs), min(ys), max(ys)), min(xs) if mode == "H" else min(ys)))
for c in G.get("circles", []):
    if Point(c["cx"], c["cy"]).buffer(c["r"]).intersects(bb): items.append(("CIRCLE (%.1f,%.1f)" % (c["cx"], c["cy"]), c["cx"] if mode == "H" else c["cy"]))
for r, t in TO:
    if box(*r).intersects(bb): items.append(("TEXT |%s| (%.0f,%.0f)-(%.0f,%.0f)" % (t, *r), r[0] if mode == "H" else r[1]))
for s, k in sorted(items, key=lambda it: it[1]): print(s)

