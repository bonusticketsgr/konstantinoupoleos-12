"""3D των καλωδίων (Β1): γράφει μία σελίδα HTML (three.js) από το ΙΔΙΟ μοντέλο με το τεύχος – τοίχοι, δοκάρια, οπές, και οι ΠΡΑΓΜΑΤΙΚΕΣ διαδρομές (κορμοί,
τροφοδοσία κάθε τοίχου, κάθε κουτί) όπως τις ελέγχει το el_route.py. Δεν σχεδιάζεται τίποτα που δεν έχει περάσει τον έλεγχο.
    python3 el_3d.py [out.html]"""
import json, os, sys
import b1_el as M
import el_route as RT
import el_drops as DR
import el_geom as G

W, A = M.W, M.A
ROOMS = [("ΣΑΛΟΝΙ", 4.9, 7.6), ("ΚΟΥΖΙΝΑ", 11.6, 8.9), ("ΧΩΛ", 4.3, 3.85), ("ΥΠΝ.1", 2.6, 1.9), ("ΥΠΝ.2", 7.9, 3.0), ("ΛΟΥΤΡΟ", 5.75, 2.0), ("ΛΟΥΤΡΟ ΓΟΝΕΩΝ", 1.9, 4.3), ("ΣΚΑΛΑ", 11.6, 6.3)]


def soffit_over(x, y):
    s = [A.beam_soffit(b[1]) for b in A.BEAMS if G.in_rect(x, y, b[2:6], tol=0.005)]
    return min(s) if s else None


def _p3(pts):
    return [[round(q[0], 3), round(q[1], 3), round(q[2], 3)] for q in pts]


def build():
    RT.bind(M); DR.bind(M)
    bad = [r for r in RT.check() if r[1] != "OK"]
    assert not bad, "3D: υπάρχουν διαδρομές που δεν περνούν τον έλεγχο – δεν βγαίνει 3D: %s" % bad[:2]
    B = RT.build()
    out = dict(rev=M.REV, date=M.DATE, walls=[], cols=[], beams=[], holes=[], rooms=ROOMS)
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
    out["furn"] = [[round(q, 3) for q in f[1]] + [f[2], f[3] if f[3] is not None else 2.46, f[0]] for f in RT._C["furn"]]
    out["doors"] = [[round(q, 3) for q in d] for d in RT._C["doors"]]
    mode = {d["id"]: d["mode"] for d in M.DROPS}
    out["trunks"] = [dict(id=t["id"], k=t["kind"], pts=_p3(t["pts"])) for t in B["trunks"]]
    out["feeds"] = [dict(id=f["id"], g=f["grp"], m=mode[f["grp"]], pts=_p3(f["feed"])) for f in M.FEEDS]
    out["tails"] = []
    for d in B["devs"]:
        k = "sock" if d["kind"] in ("ρευματοδότης", "παροχή") else ("sw" if d["kind"] == "διακόπτης" else ("data" if d["kind"].startswith("λήψη") else "oth"))
        out["tails"].append(dict(id=d["id"], g=d["grp"], m=mode[d["grp"]], k=k, pts=_p3(d["pts"][d["nfeed"] - 1:])))
    out["extra"] = [dict(id=e["id"], g=e["grp"], m=mode[e["grp"]], pts=_p3(e["pts"])) for e in B["extra"]]
    import el_sheets as SH
    out["nums"] = [[d["id"], SH.NUM_AT[d["id"]][0], SH.NUM_AT[d["id"]][1], d["mode"], d["title"]] for d in M.DROPS]
    out["nchk"] = sum(1 for _ in RT.check())
    return out


TEMPLATE = open(os.path.join(M.HERE, "el_3d_template.html"), encoding="utf-8").read() if os.path.exists(os.path.join(M.HERE, "el_3d_template.html")) else ""

if __name__ == "__main__":
    data = build()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(M.HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΚΑΤΕΒΑΣΜΑΤΑ_3D.html")
    open(dst, "w", encoding="utf-8").write(TEMPLATE.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False)))
    from collections import Counter
    print(Counter(d["m"] for d in data["tails"]), "→", os.path.normpath(dst))
