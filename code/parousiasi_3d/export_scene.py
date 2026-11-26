"""ΠΑΡΟΥΣΙΑΣΗ 3D (σαλόνι – κουζίνα τυπικού ορόφου Β1): βγάζει τη γεωμετρία του διαμερίσματος από τα ΙΔΙΑ μοντέλα με τα τεύχη
(τοιχοποιίες b1_model · ανόψεις b1_anopsi · ηλεκτρολογικά b1_el + πρόταση φωτισμού R18) σε ένα αρχείο scene.json.
Το scene.json το διαβάζει το scene.py (Blender) – εκεί ΔΕΝ γράφεται καμία διάσταση του κτιρίου με το χέρι.

    python3 export_scene.py [scene.json]

Συντεταγμένες μοντέλου: m, x → ανατολή, y → νότος, z από το τελικό δάπεδο."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ilektrologika"))
import b1_el as M
import b1_el_r18 as R18

R18.apply()                      # πρόταση R18: τοίχος του Δ18, χωρίς κουρτινόξυλα, καναπές γωνία, νέα φώτα
import el_route as RT
import el_geom as G

RT.bind(M)
W, A = M.W, M.A
SLAB = 2.78                      # κάτω παρειά πλάκας h20 από το τελικό δάπεδο
WIN_SILL = {"W2.03": (1.03, 1.53), "W2.04": (1.03, 1.53), "W2.05": (0.18, 1.53), "W2.07": (1.53, 2.43), "W2.09": (1.13, 2.43)}
WIN_FULL = (0.0, 2.43)
DOOR_H = 2.20
NORTH_TALL = False               # βόρεια πλευρά κουζίνας χωρίς ψηλή στήλη (Γιάννης 26/11 – βλ. main)
r3 = lambda v: round(float(v), 4)


def bb(p):
    return [r3(v) for v in W.bbox(p)]


def inside(b, r, tol=0.002):
    return b[0] >= r[0] - tol and b[1] >= r[1] - tol and b[2] <= r[2] + tol and b[3] <= r[3] + tol


def wall_top(b):
    """Τοίχος που είναι ΟΛΟΚΛΗΡΟΣ κάτω από δοκάρι σταματά στην κάτω παρειά του· αλλιώς φτάνει στην πλάκα (οι επενδύσεις περνούν μπροστά από το δοκάρι)."""
    s = [A.beam_soffit(q[1]) for q in A.BEAMS if inside(b, q[2:6])]
    return r3(min(s)) if s else SLAB


def main(out):
    d = dict(rev=M.REV, proposal="%s %s" % (R18.REV, R18.VERSION), date=R18.DATE, slab=SLAB)
    d["walls"] = []
    for w in W.WALLS:
        b = bb(w["pts"])
        rect = G.is_rect(w["pts"])
        d["walls"].append(dict(id=w["id"], type=w["type"], box=b, top=wall_top(b), pts=None if rect else [[r3(x), r3(y)] for x, y in w["pts"]]))
    d["cols"] = [dict(box=bb(p), pts=None if G.is_rect(p) else [[r3(x), r3(y)] for x, y in p]) for p in W.COLS]
    d["cols2"] = [bb(p) for p in W.COLS2]
    d["beams"] = [dict(id=q[0], sec=q[1], box=[r3(v) for v in q[2:6]], soffit=r3(A.beam_soffit(q[1]))) for q in A.BEAMS]
    d["zones"] = [dict(id=z["id"], level=r3(z["level"]), rects=[[r3(v) for v in r] for r in z["rects"]]) for z in A.ZONES]
    sizes = {round(s[1], 2): s[0] for s in W.WIN_SIZES}
    d["wins"] = []
    for p in W.WINS:
        b = bb(p)
        L = round(max(b[2] - b[0], b[3] - b[1]), 2)
        nm = sizes.get(L) or min(W.WIN_SIZES, key=lambda s: abs(s[1] - L))[0]
        z0, z1 = WIN_SILL.get(nm, WIN_FULL)
        d["wins"].append(dict(name=nm, box=b, z0=z0, z1=z1, ax="x" if (b[2] - b[0]) > (b[3] - b[1]) else "y"))
    d["doors"] = []
    for r, dd in zip(RT._C["doors"], W.DOORS):
        (hx, hy), (ox, oy), (jx, jy) = dd
        d["doors"].append(dict(box=[r3(v) for v in r], h=DOOR_H, hinge=[r3(hx), r3(hy)], open=[r3(ox), r3(oy)], jamb=[r3(jx), r3(jy)]))
    d["balconies"] = [[[r3(x), r3(y)] for x, y in q] for q in W.FLOORS]
    d["equip"] = [list(e[:5]) + [e[5] if len(e) > 5 else ""] for e in W.EQUIP]
    d["furn"] = [dict(name=f[0], box=[r3(v) for v in f[1]], z0=f[2], z1=f[3]) for f in RT._C["furn"]]
    d["sofa"] = dict(main=[r3(v) for v in R18.SOFA], ret=[r3(v) for v in R18.SOFA_RET], depth=R18.SOFA_D)
    d["coffee"] = [r3(v) for v in R18.COFFEE]
    d["table"] = [r3(v) for v in R18.TABLE]
    # ΑΛΛΑΓΗ ΓΙΑΝΝΗ 26/11/2026 (πάνω στις δοκιμαστικές εικόνες): «στην κουζίνα βγάλε ψυγείο φούρνο· σε εκείνη τη μεριά θα είναι μόνο πάγκος με ψηλά ντουλάπια»
    # → στη βόρεια πλευρά ΟΧΙ ψηλή στήλη: πάγκος + επάνω ντουλάπια σε όλο το μήκος της (από εκεί που άρχιζε η στήλη ως το έρκερ). ΔΕΝ έχει περάσει ακόμη στα
    # μοντέλα των τευχών (b1_model / b1_el: στήλη φούρνου, πρίζες Π51 / Π52) – εδώ αλλάζει μόνο για την παρουσίαση. Ερμηνείες Claude: «εκείνη η μεριά» = η
    # βόρεια (εκεί ήταν η στήλη «ψυγείου + φούρνου») · ο φούρνος κάτω από τις εστίες · το ψυγείο μένει στη ΝΔ γωνία του νότιου έρκερ (R17).
    tall = [e for e in W.EQUIP if e[0] == "tall" and "ΦΟΥΡΝ" in (e[5] if len(e) > 5 else "")][0]
    d["kitchen"] = dict(fridge=list(M.FRIDGE), sink=list(M.SINK), dishw=list(M.DISHW), north_tall=NORTH_TALL, north_x0=r3(tall[1]))
    d["spots"] = [dict(id=s[0], kind=s[1], x=r3(s[2]), y=r3(s[3]), grp=s[4], z=(RT.zone_at(s[2], s[3]) or (None, None))[1]) for s in M.SPOTS]
    d["ext_spots"] = [dict(id=s[0], x=r3(s[1]), y=r3(s[2])) for s in M.EXT_SPOTS]
    d["led"] = [dict(id=l[0], a=list(l[1]), b=list(l[2])) for l in M.LED]
    d["diffusers"] = [dict(id=q["id"], kind=q["kind"], rect=[r3(v) for v in q["rect"]], z=list(q.get("z", ()))) for q in A.DIFFUSERS]
    d["hatches"] = [dict(id=h["id"], rect=[r3(v) for v in h["rect"]]) for h in A.HATCHES]
    d["detectors"] = [dict(id=t[0], kind=t[1], x=r3(t[2]), y=r3(t[3])) for t in M.DETECTORS]
    d["sockets"] = [dict(id=s[0], x=r3(s[1]), y=r3(s[2]), d=s[3], n=s[4], kind=s[5], h=s[6], surf=bool(len(s) > 10 and s[10].get("surf"))) for s in M.SOCKETS]
    d["switches"] = [dict(id=s[0], x=r3(s[1]), y=r3(s[2]), d=s[3], n=len(s[4])) for s in M.SWITCHES]
    d["thermostats"] = [dict(id=t[0], x=r3(t[1]), y=r3(t[2]), d=t[3]) for t in M.THERMOSTATS]
    json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("scene.json:", len(d["walls"]), "τοίχοι ·", len(d["wins"]), "κουφώματα ·", len(d["doors"]), "πόρτες ·", len(d["spots"]), "spots  →", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "scene.json"))
