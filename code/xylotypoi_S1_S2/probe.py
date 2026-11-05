"""probe.py geometry.json texts_out.json x0 y0 x1 y1 : list geometry lines and placed texts intersecting a SOURCE rect."""
import json, sys
from shapely.geometry import box, LineString
G = json.load(open(sys.argv[1])); TO = json.load(open(sys.argv[2]))
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
bb = box(x0, y0, x1, y1)
for l in G["lines"]:
    ln = LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])])
    if ln.intersects(bb):
        print("LINE w=%s%s%s (%.1f,%.1f)-(%.1f,%.1f)" % (l["w"], " blue" if l["blue"] else "", " dashed" if l.get("dashed") else "", l["x0"], l["y0"], l["x1"], l["y1"]))
for c in G["columns"]:
    from shapely.geometry import Polygon
    if Polygon(c).intersects(bb): print("COLUMN", [(round(x), round(y)) for x, y in c])
for r, t in TO:
    if box(*r).intersects(bb): print("TEXT |%s| at (%.0f,%.0f)-(%.0f,%.0f)" % (t, *r))

