"""3D των κατεβασμάτων (Β1): γράφει μία σελίδα HTML (three.js) από το ίδιο μοντέλο με το τεύχος – τοίχοι, δοκάρια, οπές, οδεύσεις ταβανιού, κατέβασμα κάθε σημείου.
    python3 el_3d.py [out.html]"""
import json, math, os, sys
import b1_el as M
import el_checks as CK
import el_drops as DR
import el_geom as G

W, A = M.W, M.A
ZV = 2.74
VIA = {"T2-06": ((6.449, 5.10), 2.30), "T6A-01": ((9.475, 7.675), 2.30), "T3-03": ((1.15, 3.375), None), "T1-03": ((1.15, 3.375), None)}
NRM = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
ROOMS = [("ΣΑΛΟΝΙ", 4.9, 7.2), ("ΚΟΥΖΙΝΑ", 11.6, 8.9), ("ΧΩΛ", 4.6, 3.85), ("ΥΠΝ.1", 2.6, 1.9), ("ΥΠΝ.2", 7.9, 3.0), ("ΛΟΥΤΡΟ", 5.75, 2.0), ("ΛΟΥΤΡΟ ΓΟΝΕΩΝ", 1.9, 4.3), ("ΣΚΑΛΑ", 11.6, 6.3)]


def soffit_over(x, y):
    s = [A.beam_soffit(b[1]) for b in A.BEAMS if G.in_rect(x, y, b[2:6], tol=0.005)]
    return min(s) if s else None


def nearest(pt, lines):
    best = None
    for pts in lines:
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
            t = 0 if L2 == 0 else max(0.0, min(1.0, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / L2))
            q = (a[0] + dx * t, a[1] + dy * t); dd = math.hypot(pt[0] - q[0], pt[1] - q[1])
            if best is None or dd < best[0]:
                best = (dd, q)
    return best[1]


def build():
    CK.bind(M); DR.bind(M)
    out = dict(rev=M.REV, date=M.DATE, walls=[], cols=[], beams=[], holes=[], routes=[], drops=[], rooms=ROOMS)
    for w in W.WALLS:
        if G.is_rect(w["pts"]):
            b = W.bbox(w["pts"]); s = soffit_over((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            out["walls"].append([round(q, 3) for q in b] + [s or 2.78, "b" if w["type"] in DR.BRICK else ("g" if w["type"] == "T9" else ("l" if w["type"] == "T3" else "s"))])
    for p in W.COLS:
        if G.is_rect(p):
            out["cols"].append([round(q, 3) for q in W.bbox(p)])
    for b in A.BEAMS:
        out["beams"].append([b[0]] + list(b[2:6]) + [A.beam_soffit(b[1]), b[1]])
    for h in M.HOLES:
        r = [b for b in A.BEAMS if b[0] == h["beam"]][0][2:6]
        out["holes"].append(dict(id=h["id"], x=h["x"], y=h["y"], ax="y" if (r[2] - r[0]) > (r[3] - r[1]) else "x", z=2.73, use=h["use"]))
    out["zones"] = [[round(q, 3) for q in r] + [z["level"]] for z in A.ZONES for r in z["rects"]]
    lines = []
    for r in M.ROUTES:
        out["routes"].append(dict(k=r["kind"], pts=[(x, y, ZV) for x, y in r["pts"]])); lines.append(r["pts"])
    out["routes"].append(dict(k="feed", pts=[(x, y, ZV) for x, y in M.FEED_ROUTE])); lines.append(M.FEED_ROUTE)
    mode_of = {}
    for d in M.DROPS:
        for w_ in d["walls"]:
            mode_of[w_] = d
    runs = {f["id"]: f for f in M.FLOOR_RUNS}
    for pid, x, y, f, h, kind, _ in CK.wall_points():
        wid = G.face_of(W, x, y, f)[1]
        d = mode_of.get(wid); m = d["mode"] if d else "top"
        nx, ny = NRM[f]; p = (x - nx * 0.04, y - ny * 0.04)
        if wid in VIA:
            m = "via"; (j, hr) = VIA[wid]; hr = hr or h
            path = [(j[0], j[1], ZV), (j[0], j[1], hr), (p[0], p[1], hr), (p[0], p[1], h)]
        elif m in ("top", "side"):
            s = soffit_over(*p); zt = (s - 0.02) if s else ZV
            path = [(p[0], p[1], zt), (p[0], p[1], h)]
        elif m == "back":
            q = (p[0], 4.75); path = [(q[0], q[1], 2.66), (q[0], q[1], h), (p[0], p[1], h)]
        elif m == "furn" and wid == "T3-04":
            path = [(4.72, 1.25, 2.66), (4.72, 1.25, 0.5), (4.40, 0.80, 0.5), (4.40, 0.14, 0.5), (p[0], 0.14, 0.5), (p[0], 0.14, h)]
        elif m == "furn":
            path = [(9.30, 1.05, 2.66), (9.30, 1.05, h), (p[0], p[1], h)]
        else:
            fr = runs[d["run"]]; e = fr["pts"][-1]; z0 = 2.66 if fr["id"] == "Δ-TV" else 2.46
            path = [(fr["pts"][0][0], fr["pts"][0][1], z0)] + [(a, b, 0.02) for a, b in fr["pts"]] + [(e[0], e[1], h), (p[0], p[1], h)]
        path.append((x, y, h))
        q = nearest(path[0][:2], lines)
        if math.hypot(q[0] - path[0][0], q[1] - path[0][1]) > 0.03:
            path.insert(0, (q[0], q[1], ZV))
        k = "sock" if kind in ("ρευματοδότης", "παροχή") else ("sw" if kind == "διακόπτης" else ("data" if kind.startswith("λήψη") else "oth"))
        out["drops"].append(dict(id=pid, m=m, k=k, h=h, pts=[[round(c, 3) for c in q_] for q_ in path]))
    return out


TEMPLATE = open(os.path.join(M.HERE, "el_3d_template.html"), encoding="utf-8").read() if os.path.exists(os.path.join(M.HERE, "el_3d_template.html")) else ""

if __name__ == "__main__":
    data = build()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(M.HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΚΑΤΕΒΑΣΜΑΤΑ_3D.html")
    open(dst, "w", encoding="utf-8").write(TEMPLATE.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False)))
    from collections import Counter
    print(Counter(d["m"] for d in data["drops"]), "→", os.path.normpath(dst))
