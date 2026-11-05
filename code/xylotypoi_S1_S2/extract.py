"""Generic extraction of the non-rebar geometry of a Fespa formwork sheet (vector PDF, 1:50).
usage: python3 extract.py <pdf> <out.json> --region x0 y0 x1 y1 [--keep x0 y0 x1 y1 ...] [--stair x0 y0 x1 y1 ...]
All coordinates in source PDF points."""
import pymupdf, json, math, collections, statistics, argparse

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("out")
ap.add_argument("--region", nargs=4, type=float, required=True)
ap.add_argument("--keep", nargs="*", type=float, default=[])     # rects where thin solid 0.57 lines are geometry
ap.add_argument("--stair", nargs="*", type=float, default=[])    # rects where 0.28 non-axis lines are geometry (treads)
ap.add_argument("--diag_min", type=float, default=50)            # min length of 0.28 diagonals to keep (slab diagonals)
ap.add_argument("--x57_min", type=float, default=100)            # min length of 0.57 solid diagonals to keep (X crosses)
ap.add_argument("--keep_hatch", type=int, default=1)             # keep original 45-degree hatch lines (walls, fills, planted)
a = ap.parse_args()
X0, Y0, X1, Y1 = a.region
KEEP_RECTS = [tuple(a.keep[i:i+4]) for i in range(0, len(a.keep), 4)]
STAIRS = [tuple(a.stair[i:i+4]) for i in range(0, len(a.stair), 4)]

doc = pymupdf.open(a.pdf); page = doc[0]
dr = page.get_drawings()
def inreg(d):
    r = d["rect"]; return not (r.x1 < X0 or r.x0 > X1 or r.y1 < Y0 or r.y0 > Y1)
def W(d): return round(d.get("width") or 0, 2)
def BLUE(d): return (d.get("color") or (0, 0, 0))[2] > 0.5
def seg_len(p, q): return math.hypot(q.x - p.x, q.y - p.y)
def ang(p, q): return math.degrees(math.atan2(q.y - p.y, q.x - p.x)) % 180.0
def is_axis(p, q, tol=1.0):
    g = ang(p, q); return g < tol or abs(g - 90) < tol or g > 180 - tol
def in_rect(p, r): return r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]

out = dict(columns=[], lines=[], curves=[], circles=[], region=[X0, Y0, X1, Y1])

# ---------- 1.7 : column outlines -> closed loops ----------
segs17 = []
for d in dr:
    if inreg(d) and W(d) == 1.7:
        for it in d["items"]:
            if it[0] == 'l': segs17.append((it[1], it[2]))
            elif it[0] == 'c': out["curves"].append(dict(w=1.7, blue=False, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
def key(p): return (round(p.x, 1), round(p.y, 1))
adj = collections.defaultdict(list)
for i, (p, q) in enumerate(segs17): adj[key(p)].append(i); adj[key(q)].append(i)
used = set(); loops = []; open_chains = []
for i in range(len(segs17)):
    if i in used: continue
    p, q = segs17[i]; used.add(i); poly = [p, q]; cur = q; closed = False
    while True:
        nxt = [j for j in adj[key(cur)] if j not in used]
        if not nxt: break
        j = nxt[0]; used.add(j); c, d2 = segs17[j]
        cur = d2 if key(c) == key(cur) else c
        if key(cur) == key(poly[0]): closed = True; break
        poly.append(cur)
    (loops if closed else open_chains).append([(round(pp.x, 2), round(pp.y, 2)) for pp in poly])
out["columns"] = loops
out["open17"] = open_chains
print("columns (closed 1.7 loops):", len(loops), " open 1.7 chains:", len(open_chains))

# ---------- 0.85 : structural lines (drop rebar-style dashed runs: piece ~2.8pt / gap 1.7) ----------
segs85 = []
for d in dr:
    if inreg(d) and W(d) == 0.85:
        for it in d["items"]:
            if it[0] == 'l': segs85.append((it[1], it[2], BLUE(d)))
            elif it[0] == 'c': out["curves"].append(dict(w=0.85, blue=BLUE(d), pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
def run_groups(segs):
    groups = collections.defaultdict(list)
    for idx, (p, q, bl) in enumerate(segs):
        if abs(p.y - q.y) < 0.05: groups[('H', round(p.y, 1))].append((min(p.x, q.x), max(p.x, q.x), idx))
        elif abs(p.x - q.x) < 0.05: groups[('V', round(p.x, 1))].append((min(p.y, q.y), max(p.y, q.y), idx))
    runs = []
    for k, ivs in groups.items():
        ivs.sort(); cur = [ivs[0]]
        for iv in ivs[1:]:
            if iv[0] <= cur[-1][1] + 8: cur.append(iv)
            else: runs.append(cur); cur = [iv]
        runs.append(cur)
    return runs
drop85 = set(); dashed85 = set()
for run in run_groups(segs85):
    if len(run) >= 3:
        med = statistics.median([b - a_ for a_, b, i in run])
        if med < 3.5:
            for a_, b, i in run: drop85.add(i)
        elif med < 10:
            for a_, b, i in run: dashed85.add(i)
for idx, (p, q, bl) in enumerate(segs85):
    if idx in drop85: continue
    out["lines"].append(dict(w=0.85, blue=bl, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), dashed=(idx in dashed85)))
print("0.85 kept", len(segs85) - len(drop85), "dropped(rebar dashes)", len(drop85))

# ---------- 0.57 blue : planted elements -> keep all ----------
nb = 0
for d in dr:
    if inreg(d) and W(d) == 0.57 and BLUE(d):
        for it in d["items"]:
            if it[0] == 'l': out["lines"].append(dict(w=0.57, blue=True, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2))); nb += 1
            elif it[0] == 'c': out["curves"].append(dict(w=0.57, blue=True, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
print("blue 0.57 lines", nb)

# ---------- 0.57 black : dashed hidden lines kept; dotted (extension) dropped; solid only X-crosses / keep-rects ----------
def line_key(p, q):
    dx, dy = q.x - p.x, q.y - p.y; L = math.hypot(dx, dy)
    if L < 1e-6: return None
    g = round((math.degrees(math.atan2(dy, dx)) % 180.0) / 2.0) * 2.0 % 180
    r = math.radians(g); nx, ny = -math.sin(r), math.cos(r)
    return (g, round(p.x * nx + p.y * ny))
paths57 = [d for d in dr if inreg(d) and W(d) == 0.57 and not BLUE(d)]
groups = collections.defaultdict(list); singles = []
for d in paths57:
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        p, q = its[0][1], its[0][2]; k = line_key(p, q)
        if k is None: continue
        g = k[0]; r = math.radians(g); ux, uy = math.cos(r), math.sin(r)
        t0, t1 = p.x*ux + p.y*uy, q.x*ux + q.y*uy
        groups[k].append((min(t0, t1), max(t0, t1), p, q))
    else: singles.append(d)
kept57 = 0
for (g, off), segs in groups.items():
    segs.sort(key=lambda s: s[0]); runs = []; cur = [segs[0]]
    for s in segs[1:]:
        if s[0] <= cur[-1][1] + 8: cur.append(s)
        else: runs.append(cur); cur = [s]
    runs.append(cur)
    for run in runs:
        med = statistics.median([b - a_ for a_, b, _, _ in run])
        style = 'dotted' if (len(run) >= 3 and med < 1.8) else ('dashed' if (len(run) >= 3 and med < 10) else 'solid')
        for a_, b, p, q in run:
            keep = False
            if style == 'dashed': keep = not (not is_axis(p, q) and (run[-1][1] - run[0][0]) < 20)
            elif style == 'solid':
                if (b - a_) > a.x57_min and not is_axis(p, q): keep = True
                if any(in_rect(p, r) and in_rect(q, r) for r in KEEP_RECTS): keep = True
            if keep:
                kept57 += 1
                out["lines"].append(dict(w=0.57, blue=False, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), dashed=(style == 'dashed')))
for d in singles:   # curves: keep only big arcs (stairs); small circles = bar markers
    r = d["rect"]
    if max(r.width, r.height) > 20:
        for it in d["items"]:
            if it[0] == 'c': out["curves"].append(dict(w=0.57, blue=False, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
            elif it[0] == 'l': out["lines"].append(dict(w=0.57, blue=False, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2)))
print("0.57 black kept", kept57)

# ---------- 0.28 : slab diagonals, stair treads, slab-label circles ----------
def in_poly(px, py, poly):
    inside = False; n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i+1) % n]
        if (y0 > py) != (y1 > py):
            xi = x0 + (py - y0) * (x1 - x0) / (y1 - y0)
            if xi > px: inside = not inside
    return inside
def in_any_column(px, py): return any(in_poly(px, py, c) for c in out["columns"])
kept28 = 0
for d in dr:
    if not (inreg(d) and W(d) == 0.28): continue
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        p, q = its[0][1], its[0][2]; L = seg_len(p, q)
        g = ang(p, q); hatch = (abs(g - 45) < 2.5 or abs(g - 135) < 2.5) and L > 4.0
        keep = (L > a.diag_min and not is_axis(p, q)) or any(in_rect(p, r) and in_rect(q, r) and not is_axis(p, q, 0.5) and L > 5 for r in STAIRS)
        if hatch and a.keep_hatch: keep = True
        if keep and not (hatch and a.keep_hatch) and in_any_column((p.x + q.x) / 2, (p.y + q.y) / 2): keep = False
        if keep and hatch: pass
        if keep:
            kept28 += 1; out["lines"].append(dict(w=0.28, blue=False, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), hatch=hatch))
    elif all(it[0] == 'c' for it in its) and len(its) == 4:
        r = d["rect"]
        if 22 < max(r.width, r.height) < 28:
            out["circles"].append(dict(cx=round((r.x0+r.x1)/2,2), cy=round((r.y0+r.y1)/2,2), r=round(r.width/2,2)))
print("0.28 kept", kept28, "circles", len(out["circles"]))
json.dump(out, open(a.out, "w"), ensure_ascii=False)

