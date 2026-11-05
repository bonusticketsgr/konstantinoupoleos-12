"""Automatic label helpers: column labels, beam labels with computed clear length L, slab labels, level marks."""
import re, math, json
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
S = 56.6929

def parse_labels(T, region):
    X0, Y0, X1, Y1 = region
    def inr(t, pad=60): return X0 - pad <= (t["x0"] + t["x1"]) / 2 <= X1 + pad and Y0 - pad <= (t["y0"] + t["y1"]) / 2 <= Y1 + pad
    cols = [t for t in T if re.match(r"^Κ\d+\s+[\d/]+$", t["text"].strip()) and inr(t)]
    beams = [t for t in T if re.match(r"^Δ\s*\d+\.\d+\s+\d+/\d+", t["text"].strip()) and inr(t, 0)]
    ez = [t for t in T if t["text"].strip().startswith("Ε.Ζ.") and inr(t, 0)]
    slabs = [t for t in T if re.match(r"^Π\d*$", t["text"].strip()) and inr(t, 0)]
    hs = [t for t in T if re.match(r"^h=\s*\d+$", t["text"].strip()) and inr(t, 0)]
    levels = [t for t in T if re.match(r"^[+±-]\d,\d\d$", t["text"].strip()) and inr(t, 0)]
    return dict(cols=cols, beams=beams, ez=ez, slabs=slabs, hs=hs, levels=levels)

def beam_length(G, t, b_cm):
    """clear length of the beam labelled by text t (source coords) by ray casting along the beam axis."""
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    horiz = abs(t["dir"][1]) < 0.2
    ux, uy = (1, 0) if horiz else (0, 1)
    nx, ny = (0, 1) if horiz else (1, 0)
    bw = b_cm / 100 * S
    # beam edges: parallel 0.85 solid lines near the label
    par = []
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 5: continue
        if horiz and abs(dy) > 0.02 * Ln + 0.1: continue
        if not horiz and abs(dx) > 0.02 * Ln + 0.1: continue
        # perpendicular offset from label centre
        off = (l["y0"] - cy) if horiz else (l["x0"] - cx)
        # label centre must be within the segment's along-extent (with slack)
        a0, a1 = (min(l["x0"], l["x1"]), max(l["x0"], l["x1"])) if horiz else (min(l["y0"], l["y1"]), max(l["y0"], l["y1"]))
        c_along = cx if horiz else cy
        if not (a0 - 15 <= c_along <= a1 + 15): continue
        if abs(off) <= bw + 8: par.append(off)
    neg = [o for o in par if o < 0]; pos = [o for o in par if o > 0]
    if neg and pos: centre_off = (max(neg) + min(pos)) / 2
    else: centre_off = 0.0
    px, py = (cx, cy + centre_off) if horiz else (cx + centre_off, cy)
    # obstacles: column polygons, open 1.7 chains, perpendicular 0.85 solid segments
    obst = [Polygon(c).exterior for c in G["columns"]] + [LineString(c) for c in G.get("open17", []) if len(c) > 1]
    for l in G["lines"]:
        if l["w"] not in (0.85, 1.7) or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 4: continue
        perp = (abs(dx) <= 0.05 * Ln + 0.1) if horiz else (abs(dy) <= 0.05 * Ln + 0.1)
        if perp:
            e = bw / 2 + 3; k_ = e / Ln
            obst.append(LineString([(l["x0"] - dx * k_, l["y0"] - dy * k_), (l["x1"] + dx * k_, l["y1"] + dy * k_)]))
    def cast(sign):
        ray = LineString([(px, py), (px + sign * ux * 3000, py + sign * uy * 3000)])
        best = None
        for o in obst:
            inter = ray.intersection(o)
            if inter.is_empty: continue
            pts = []
            if inter.geom_type == "Point": pts = [inter]
            elif inter.geom_type == "MultiPoint": pts = list(inter.geoms)
            elif inter.geom_type in ("LineString", "MultiLineString"):
                for g in getattr(inter, "geoms", [inter]): pts += [Point(c) for c in g.coords]
            for q in pts:
                d = math.hypot(q.x - px, q.y - py)
                if d > 1.0 and (best is None or d < best[0]): best = (d, q)
        return best
    a = cast(+1); b = cast(-1)
    if not a or not b: return None, (px, py), (a, b)
    return (a[0] + b[0]) / S, (px, py), (a[1], b[1])

def thin_solid_segments(pdf, region):
    """0.57 black solid segments (leaders) from the raw drawing within region."""
    import pymupdf
    X0, Y0, X1, Y1 = region
    doc = pymupdf.open(pdf); dr = doc[0].get_drawings(); segs = []
    for d in dr:
        if round(d.get("width") or 0, 2) != 0.57 or (d.get("color") or (0, 0, 0))[2] > 0.5: continue
        for it in d["items"]:
            if it[0] != 'l': continue
            a, b = it[1], it[2]; Ln = math.hypot(b.x - a.x, b.y - a.y)
            if Ln < 6: continue
            if X0 <= a.x <= X1 and Y0 <= a.y <= Y1: segs.append(((a.x, a.y), (b.x, b.y)))
    return segs

def follow_leader(t, segs, pad=30):
    """from a label bbox, follow a chain of thin segments to its far end. Returns (x,y) or None."""
    x0, y0, x1, y1 = t["x0"] - pad, t["y0"] - pad, t["x1"] + pad, t["y1"] + pad
    def near_box(p): return x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    start = None
    cands = []
    for a, b in segs:
        if math.hypot(b[0]-a[0], b[1]-a[1]) < 12: continue
        if near_box(a) and not near_box(b): cands.append((a, b))
        elif near_box(b) and not near_box(a): cands.append((b, a))
    if not cands: return None
    # nearest start point to the label centre
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    start = min(cands, key=lambda s: math.hypot(s[0][0]-cx, s[0][1]-cy))
    cur = start[1]; used = {start}
    for _ in range(6):
        nxt = None
        for sgm in segs:
            if sgm in used: continue
            a, b = sgm
            if math.hypot(a[0] - cur[0], a[1] - cur[1]) < 1.5: nxt = (sgm, b); break
            if math.hypot(b[0] - cur[0], b[1] - cur[1]) < 1.5: nxt = (sgm, a); break
        if not nxt: break
        used.add(nxt[0]); cur = nxt[1]
    return cur

def bracket(G, px, py, horiz, bw):
    """parallel 0.85 solid lines bracketing point (px,py) within bw+8; returns (neg, pos) offsets or None"""
    par = []
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 5: continue
        if horiz and abs(dy) > 0.02 * Ln + 0.1: continue
        if not horiz and abs(dx) > 0.02 * Ln + 0.1: continue
        off = (l["y0"] - py) if horiz else (l["x0"] - px)
        a0, a1 = (min(l["x0"], l["x1"]), max(l["x0"], l["x1"])) if horiz else (min(l["y0"], l["y1"]), max(l["y0"], l["y1"]))
        c_along = px if horiz else py
        if not (a0 - 12 <= c_along <= a1 + 12): continue
        if abs(off) <= bw + 6: par.append(off)
    neg = [o for o in par if o < 0]; pos = [o for o in par if o > 0]
    if neg and pos and (min(pos) - max(neg)) <= bw + 6: return max(neg), min(pos)
    return None

def beam_length2(G, t, b_cm, segs=None):
    """beam clear length; handles labels inside the beam and leader labels (segs = thin solid segments)."""
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    bw = b_cm / 100 * S
    horiz = abs(t["dir"][1]) < 0.2
    br = bracket(G, cx, cy, horiz, bw)
    px, py = cx, cy; how = "inside"
    if br is None and segs:
        end = follow_leader(t, segs)
        if end:
            px, py = end; how = "leader"
            brH = bracket(G, px, py, True, bw); brV = bracket(G, px, py, False, bw)
            if brH and not brV: horiz = True; br = brH
            elif brV and not brH: horiz = False; br = brV
            elif brH and brV: horiz = (brH[1] - brH[0]) <= (brV[1] - brV[0]); br = brH if horiz else brV
    if br:
        if horiz: py = py + (br[0] + br[1]) / 2
        else: px = px + (br[0] + br[1]) / 2
    ux, uy = (1, 0) if horiz else (0, 1)
    obst = [Polygon(c).exterior for c in G["columns"]] + [LineString(c) for c in G.get("open17", []) if len(c) > 1]
    for seg in merged_runs(G, not horiz):   # perpendicular runs, merged across junction gaps
        obst.append(LineString(seg))
    def cast(sign):
        ray = LineString([(px, py), (px + sign * ux * 3000, py + sign * uy * 3000)])
        best = None
        for o in obst:
            inter = ray.intersection(o)
            if inter.is_empty: continue
            pts = []
            if inter.geom_type == "Point": pts = [inter]
            elif inter.geom_type == "MultiPoint": pts = list(inter.geoms)
            else:
                for g in getattr(inter, "geoms", [inter]): pts += [Point(c) for c in g.coords]
            for q in pts:
                d = math.hypot(q.x - px, q.y - py)
                if d > 1.0 and (best is None or d < best[0]): best = (d, q)
        return best
    a = cast(+1); b = cast(-1)
    if not a or not b: return None, (px, py), horiz, how, br, None
    return (a[0] + b[0]) / S, (px, py), horiz, how, br, ((b[1].x, b[1].y), (a[1].x, a[1].y))

def merged_runs(G, horizontal, gap=20.0):
    """0.85 solid black segments, axis-aligned, merged along collinear runs across gaps <= gap."""
    import collections
    groups = collections.defaultdict(list)
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 3: continue
        if horizontal and abs(dy) <= 0.02 * Ln + 0.1: groups[round(l["y0"] * 2) / 2].append((min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
        elif (not horizontal) and abs(dx) <= 0.02 * Ln + 0.1: groups[round(l["x0"] * 2) / 2].append((min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
    runs = []
    for k, ivs in groups.items():
        ivs.sort(); cur = list(ivs[0])
        for a_, b_ in ivs[1:]:
            if a_ <= cur[1] + gap: cur[1] = max(cur[1], b_)
            else: runs.append((k, cur[0], cur[1])); cur = [a_, b_]
        runs.append((k, cur[0], cur[1]))
    return [([(a_, k), (b_, k)] if horizontal else [(k, a_), (k, b_)]) for k, a_, b_ in runs]

