"""Extract the kept (non-rebar) geometry of the Σ3 plan from the vector PDF.
All coordinates are in the original PDF points (scale 1:50, 56.6929 pt/m)."""
import pymupdf, json, math, collections, statistics

S = 56.6929  # pt per metre @1:50
doc = pymupdf.open("S3.pdf"); page = doc[0]
dr = page.get_drawings()

# plan region (excludes the legend sections around it)
X0, Y0, X1, Y1 = 560, 495, 1700, 1236
def inreg(d):
    r = d["rect"]
    return not (r.x1 < X0 or r.x0 > X1 or r.y1 < Y0 or r.y0 > Y1)

def W(d): return round(d.get("width") or 0, 2)
def BLUE(d): return (d.get("color") or (0, 0, 0))[2] > 0.5

def seg_len(a, b): return math.hypot(b.x - a.x, b.y - a.y)
def ang(a, b):
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x)) % 180.0
def is_axis(a, b, tol=1.0):
    g = ang(a, b); return g < tol or abs(g - 90) < tol or g > 180 - tol

out = dict(columns=[], lines=[], curves=[], labels=[], circles=[], levels=[])

# ---------- 1.7 : column outlines -> closed loops ----------
segs17 = []
for d in dr:
    if inreg(d) and W(d) == 1.7:
        for it in d["items"]:
            if it[0] == 'l': segs17.append((it[1], it[2]))
# chain segments into loops
def key(p): return (round(p.x, 1), round(p.y, 1))
adj = collections.defaultdict(list)
for i, (a, b) in enumerate(segs17):
    adj[key(a)].append(i); adj[key(b)].append(i)
used = set(); loops = []
for i in range(len(segs17)):
    if i in used: continue
    a, b = segs17[i]; used.add(i)
    poly = [a, b]
    cur = b
    while True:
        nxt = [j for j in adj[key(cur)] if j not in used]
        if not nxt: break
        j = nxt[0]; used.add(j)
        c, d2 = segs17[j]
        cur = d2 if key(c) == key(cur) else c
        if key(cur) == key(poly[0]): break
        poly.append(cur)
    loops.append([(round(p.x, 2), round(p.y, 2)) for p in poly])
out["columns"] = loops

# ---------- 0.85 : structural lines (drop rebar-style dashed runs) ----------
segs85 = []
for d in dr:
    if inreg(d) and W(d) == 0.85:
        for it in d["items"]:
            if it[0] == 'l': segs85.append((it[1], it[2], BLUE(d)))
            elif it[0] == 'c': out["curves"].append(dict(w=0.85, blue=BLUE(d), pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
# group collinear runs to find rebar-style dashes (piece ~2.8pt, gap 1.7)
def run_groups(segs):
    groups = collections.defaultdict(list)
    for idx, (a, b, bl) in enumerate(segs):
        if abs(a.y - b.y) < 0.05: groups[('H', round(a.y, 1))].append((min(a.x, b.x), max(a.x, b.x), idx))
        elif abs(a.x - b.x) < 0.05: groups[('V', round(a.x, 1))].append((min(a.y, b.y), max(a.y, b.y), idx))
    runs = []
    for k, ivs in groups.items():
        ivs.sort(); cur = [ivs[0]]
        for iv in ivs[1:]:
            if iv[0] <= cur[-1][1] + 8: cur.append(iv)
            else: runs.append(cur); cur = [iv]
        runs.append(cur)
    return runs
drop85 = set()
for run in run_groups(segs85):
    if len(run) >= 3:
        lens = [b - a for a, b, i in run]
        if statistics.median(lens) < 3.5:  # rebar-style dashed line
            for a, b, i in run: drop85.add(i)
for idx, (a, b, bl) in enumerate(segs85):
    if idx in drop85: continue
    out["lines"].append(dict(w=0.85, blue=bl, x0=round(a.x,2), y0=round(a.y,2), x1=round(b.x,2), y1=round(b.y,2)))
print("0.85 segments kept", len(segs85) - len(drop85), "dropped", len(drop85))

# ---------- 0.57 blue : planted walls hatch + level arrows -> keep all ----------
for d in dr:
    if inreg(d) and W(d) == 0.57 and BLUE(d):
        for it in d["items"]:
            if it[0] == 'l': out["lines"].append(dict(w=0.57, blue=True, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2)))
            elif it[0] == 'c': out["curves"].append(dict(w=0.57, blue=True, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))

# ---------- 0.57 black ----------
# group single-line paths into runs (dotted / dashed / solid)
def line_key(a, b):
    dx, dy = b.x - a.x, b.y - a.y; L = math.hypot(dx, dy)
    if L < 1e-6: return None
    g = round((math.degrees(math.atan2(dy, dx)) % 180.0) / 2.0) * 2.0 % 180
    r = math.radians(g); nx, ny = -math.sin(r), math.cos(r)
    return (g, round(a.x * nx + a.y * ny))
paths57 = [d for d in dr if inreg(d) and W(d) == 0.57 and not BLUE(d)]
groups = collections.defaultdict(list); singles = []
for d in paths57:
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        a, b = its[0][1], its[0][2]; k = line_key(a, b)
        if k is None: continue
        g = k[0]; r = math.radians(g); ux, uy = math.cos(r), math.sin(r)
        t0, t1 = a.x*ux + a.y*uy, b.x*ux + b.y*uy
        groups[k].append((min(t0, t1), max(t0, t1), a, b))
    else:
        singles.append(d)
KEEP_RECTS = [  # regions where thin solid 0.57 lines are geometry (hatched wall under stair, core inner detail, stair symbol)
    (1616, 946, 1634, 1020), (1515, 770, 1619, 863), (1490, 940, 1552, 955)]
def in_rect(p, r): return r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]
kept57 = 0
for (g, off), segs in groups.items():
    segs.sort(key=lambda s: s[0])
    runs = []; cur = [segs[0]]
    for s in segs[1:]:
        if s[0] <= cur[-1][1] + 8: cur.append(s)
        else: runs.append(cur); cur = [s]
    runs.append(cur)
    for run in runs:
        lens = [b - a for a, b, _, _ in run]
        med = statistics.median(lens)
        if len(run) >= 3 and med < 1.8:
            style = 'dotted'      # dimension extension lines -> drop
        elif len(run) >= 3 and med < 10:
            style = 'dashed'      # hidden lines -> keep
        else:
            style = 'solid'
        for a, b, pa, pb in run:
            keep = False
            if style == 'dashed':
                keep = not (not is_axis(pa, pb) and (run[-1][1]-run[0][0]) < 20)
            elif style == 'solid':
                L = b - a
                if L > 100 and not is_axis(pa, pb): keep = True         # X cross
                if any(in_rect(pa, r) and in_rect(pb, r) for r in KEEP_RECTS): keep = True
            if keep:
                kept57 += 1
                out["lines"].append(dict(w=0.57, blue=False, x0=round(pa.x,2), y0=round(pa.y,2), x1=round(pb.x,2), y1=round(pb.y,2), dashed=(style=='dashed')))
# 0.57 singles: keep only the two big stair arcs (size > 20)
for d in singles:
    r = d["rect"]
    if max(r.width, r.height) > 20:
        for it in d["items"]:
            if it[0] == 'c': out["curves"].append(dict(w=0.57, blue=False, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
            elif it[0] == 'l': out["lines"].append(dict(w=0.57, blue=False, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2)))
print("0.57 black kept lines", kept57)

# ---------- 0.28 : slab diagonals, stair treads, circles ----------
STAIR = (1490, 874, 1668, 1172)
kept28 = 0
def in_poly(px, py, poly):
    inside = False; n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i+1) % n]
        if (y0 > py) != (y1 > py):
            xi = x0 + (py - y0) * (x1 - x0) / (y1 - y0)
            if xi > px: inside = not inside
    return inside
def in_any_column(px, py): return any(in_poly(px, py, c) for c in out["columns"])
for d in dr:
    if not (inreg(d) and W(d) == 0.28): continue
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        a, b = its[0][1], its[0][2]; L = seg_len(a, b)
        keep = False
        if L > 50 and not is_axis(a, b): keep = True
        if in_rect(a, STAIR) and in_rect(b, STAIR) and not is_axis(a, b, 0.5) and L > 5: keep = True
        if keep and in_any_column((a.x+b.x)/2, (a.y+b.y)/2): keep = False
        if keep:
            kept28 += 1
            out["lines"].append(dict(w=0.28, blue=False, x0=round(a.x,2), y0=round(a.y,2), x1=round(b.x,2), y1=round(b.y,2)))
    elif all(it[0] == 'c' for it in its) and len(its) == 4:
        r = d["rect"]
        if 22 < max(r.width, r.height) < 28:   # slab label circles
            out["circles"].append(dict(cx=round((r.x0+r.x1)/2,2), cy=round((r.y0+r.y1)/2,2), r=round(r.width/2,2)))
        elif 6 < max(r.width, r.height) < 14:  # level symbols
            out["levels"].append(dict(cx=round((r.x0+r.x1)/2,2), cy=round((r.y0+r.y1)/2,2)))
print("0.28 kept lines", kept28, "circles", len(out["circles"]), "level symbols", len(out["levels"]))

# ---------- texts ----------
texts = json.load(open("texts.json"))
out["texts"] = [t for t in texts if X0 <= t["x0"] <= X1 and Y0 <= t["y0"] <= Y1]
json.dump(out, open("geometry.json", "w"), ensure_ascii=False, indent=1)
print("columns", len(out["columns"]), [len(c) for c in out["columns"]])
print("levels", out["levels"])
print("circles", [(c["cx"], c["cy"]) for c in out["circles"]])

