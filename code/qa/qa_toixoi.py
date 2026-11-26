"""Τελικός έλεγχος τοιχοποιιών ΠΕΡΑ από τα check_dims / check_overlap / check_corners (μοντέλα code/toixopoiies/*_model.py):
  1 πόρτες: πλάτος ανοίγματος, φύλλο κάθετο στον τοίχο, μεντεσές / παραστάδα πάνω σε παρειά, τόξο χωρίς τοίχο / ντουλάπα / είδη υγιεινής μέσα
  2 ντουλάπες · πάγκοι · είδη υγιεινής · έπιπλα του μοντέλου: δεν μπαίνουν μέσα σε τοίχο / υποστύλωμα
  3 σκάλες: κανένας τοίχος μέσα στους κλάδους · οι τοίχοι γύρω από τη σκάλα στις θέσεις που θεωρεί το τεύχος σκαλών (stairs.json ενήμερο)
  4 εμβαδά στις ετικέτες χώρων («≈ … m²») έναντι του μοντέλου (γέμισμα 1 cm ανάμεσα σε τοίχους / κουφώματα / πόρτες)
Χρήση: python3 qa_toixoi.py [b gf b1 f4 s]   → κωδικός 1 αν υπάρχει ΛΑΘΟΣ."""
import importlib, json, math, os, re, subprocess, sys
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, "..", "toixopoiies")
sys.path.insert(0, TX)
MODELS = {"b": "b_model", "gf": "gf_model", "b1": "b1_model", "f4": "f4_model", "s": "s_model"}
DOOR_W = (0.70, 0.80, 0.90, 1.00, 1.10, 1.20)
# κλάδοι σκάλας που πρέπει να μένουν ελεύθεροι από τοίχους (m): κοινόχρηστη 10,90–13,10 × 5,10–7,60 · Δ΄: ιδιωτική 6,60–7,60 + κοινόχρηστη 5,10–6,45
FLIGHTS = {"b": [(10.90, 5.10, 13.10, 7.60)], "gf": [(10.90, 5.10, 13.10, 7.60)], "b1": [(10.90, 5.10, 13.10, 7.60)],
           "f4": [(10.90, 6.60, 13.10, 7.60), (10.90, 5.10, 13.10, 6.45)], "s": [(11.15, 5.10, 13.10, 7.60)]}
# νοητοί διαχωρισμοί ανοιχτών χώρων για τον έλεγχο εμβαδών (εκεί που ο χώρος επικοινωνεί χωρίς πόρτα)
SEPS = {"b1": [((5.449, 5.10), (6.349, 5.10)), ((9.475, 7.70), (9.475, 9.15))],   # R32: κουζίνα από το 7,70 (Τ2-10)
        "f4": [((5.449, 5.10), (6.349, 5.10)), ((9.475, 6.60), (9.475, 9.15)), ((9.40, 7.70), (10.45, 7.70))],
        "gf": [((5.50, 4.15), (6.50, 4.15)), ((4.50, 4.15), (5.50, 4.15)), ((5.50, 4.95), (6.50, 4.95))], "s": [((5.50, 2.40), (6.50, 2.40)), ((5.50, 3.0875), (6.50, 3.0875)), ((6.55, 3.85), (6.55, 4.65))], "b": []}
rows = []


def add(k, grp, item, val, st):
    rows.append((k, grp, item, val, st))


def geom(M):
    walls = unary_union([Polygon(w["pts"]) for w in M.WALLS])
    cols = unary_union([Polygon(p) for p in M.COLS])
    wins = unary_union([Polygon(p) for p in M.WINS]) if M.WINS else Polygon()
    return walls, cols, wins


def doors(k, M, solid, wins):
    frame = unary_union([solid, wins.buffer(0.01)]) if not wins.is_empty else solid
    fixed = [(wd["name"], box(*wd["r"])) for wd in M.WARDROBES if not wd.get("joinery")]
    for b in M.BATHS:
        fixed.append(("πάγκος " + b.get("name", ""), box(*b["counter"])))
        (tx, ty), f = b["toilet"]
        ux, uy = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}[f]
        fixed.append(("λεκάνη " + b.get("name", ""), Point(tx + ux * 0.42, ty + uy * 0.42).buffer(0.19).union(
            box(min(tx, tx + ux * 0.15) - abs(uy) * 0.20, min(ty, ty + uy * 0.15) - abs(ux) * 0.20, max(tx, tx + ux * 0.15) + abs(uy) * 0.20, max(ty, ty + uy * 0.15) + abs(ux) * 0.20))))
        if b.get("screen"):
            fixed.append(("γυαλί ντους " + b.get("name", ""), LineString(b["screen"]).buffer(0.01)))
    for e in getattr(M, "EQUIP", []):
        if e[0] in ("tall", "appl", "hob", "sink") or (e[0] == "rect" and len(e) > 5 and e[5] and "ΤΡΑΠΕΖ" not in e[5] and "Θ.Σ" not in e[5]):
            fixed.append(("%s %s" % (e[0], e[5] if len(e) > 5 else ""), box(*e[1:5])))
    for i, (h, l, j) in enumerate(M.DOORS, 1):
        if h == j:
            continue
        w = math.dist(h, j); leaf = math.dist(h, l)
        name = "πόρτα %d (%.2f · %.2f)" % (i, (h[0] + j[0]) / 2, (h[1] + j[1]) / 2)
        probs = []
        if min(abs(w - d) for d in DOOR_W) > 0.006:
            probs.append("πλάτος %.3f" % w)
        if abs(leaf - w) > 0.03:
            probs.append("φύλλο %.2f ≠ άνοιγμα %.2f" % (leaf, w))
        dot = (l[0] - h[0]) * (j[0] - h[0]) + (l[1] - h[1]) * (j[1] - h[1])
        if abs(dot) > 1e-6:
            probs.append("φύλλο όχι κάθετο στον τοίχο")
        for nm, p in (("μεντεσές", h), ("παραστάδα", j)):
            d = frame.distance(Point(p))
            if d > 0.012:
                probs.append("%s %.3f από τοίχο" % (nm, d))
        op = LineString([h, j])
        if op.intersection(solid.buffer(-0.004)).length > 0.01:
            probs.append("τοίχος μέσα στο άνοιγμα %.2f" % op.intersection(solid).length)
        # τόξο ανοίγματος
        a0 = math.atan2(j[1] - h[1], j[0] - h[0]); a1 = math.atan2(l[1] - h[1], l[0] - h[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        sec = Polygon([h] + [(h[0] + w * math.cos(a0 + da * t / 24), h[1] + w * math.sin(a0 + da * t / 24)) for t in range(25)])
        hit = sec.buffer(-0.02).intersection(solid).area
        if hit > 0.004:
            probs.append("το φύλλο βρίσκει σε τοίχο (%.0f cm²)" % (hit * 1e4))
        for nm, g in fixed:
            a = sec.buffer(-0.02).intersection(g).area
            if a > 0.004:
                probs.append("το φύλλο βρίσκει: %s (%.0f cm²)" % (nm.strip(), a * 1e4))
        add(k, "Πόρτες", name, "; ".join(probs) if probs else "πλάτος %.2f · φύλλο κάθετο · τόξο ελεύθερο" % w, "ΛΑΘΟΣ" if probs else "OK")


def fixtures(k, M, walls, cols):
    items = [(wd["name"], box(*wd["r"])) for wd in M.WARDROBES]
    for b in M.BATHS:
        items.append(("πάγκος νιπτήρα " + b.get("name", ""), box(*b["counter"])))
    for e in getattr(M, "EQUIP", []):
        items.append(("%s %s" % (e[0], (e[5] if len(e) > 5 and isinstance(e[5], str) else "")), box(*e[1:5])))
    bad = 0
    for nm, g in items:
        a = g.intersection(walls).area
        if a > 0.002:
            bad += 1
            add(k, "Έπιπλα–τοίχοι", nm.strip(), "μπαίνει %.0f cm² μέσα σε τοίχο %s" % (a * 1e4, tuple(round(v, 3) for v in g.bounds)), "ΛΑΘΟΣ")
        ac = g.intersection(cols).area
        if ac > 0.002:      # υποστύλωμα που προεξέχει μέσα στο ορθογώνιο του επίπλου: το έπιπλο κόβεται γύρω του – σημείωση για τον ξυλουργό
            add(k, "Έπιπλα–τοίχοι", nm.strip(), "γύρω από υποστύλωμα που προεξέχει (%.0f cm²) – εγκοπή / μικρότερο βάθος εκεί" % (ac * 1e4), "ΣΗΜ.")
    add(k, "Έπιπλα–τοίχοι", "ντουλάπες · πάγκοι · εξοπλισμός (%d)" % len(items), "κανένα μέσα σε τοίχο" if not bad else "%d ευρήματα" % bad, "OK" if not bad else "ΛΑΘΟΣ")


def stairs(k, M, walls):
    for r in FLIGHTS[k]:
        a = box(*r).buffer(-0.005).intersection(walls).area
        add(k, "Σκάλες", "κλάδοι %s × %s" % (("%.2f–%.2f" % (r[0], r[2])).replace(".", ","), ("%.2f–%.2f" % (r[1], r[3])).replace(".", ",")),
            "ελεύθεροι από τοίχους" if a < 1e-4 else "τοίχος μέσα στον κλάδο: %.0f cm²" % (a * 1e4), "OK" if a < 1e-4 else "ΛΑΘΟΣ")
    S = json.load(open(os.path.join(TX, "data", "stairs.json"), encoding="utf-8"))
    key = M.STAIR.get("model")
    add(k, "Σκάλες", "σκάλα στο σχέδιο", ("τεύχος σκαλών %s (%s · %d ρίχτια)" % (S[key]["sheet"], S[key]["rev"], S[key]["n"])) if key in S else "ΣΧΗΜΑΤΙΚΗ (όχι από το τεύχος σκαλών)",
        "OK" if key in S else "ΛΑΘΟΣ")
    if key in S:
        # τα άκρα των ριχτιών πρέπει να ακουμπούν σε τοίχο / σκυρόδεμα / φανάρι – όχι να μπαίνουν μέσα σε τοίχο
        solid = unary_union([walls] + [Polygon(p) for p in M.COLS])
        deep = []
        cut = M.STAIR.get("cut", (S[key]["n"] + 1) // 2)
        for n_, (a, b) in S[key]["risers"].items():
            if M.STAIR.get("top") or int(n_) > cut:
                continue        # πάνω από την τομή (η σκάλα περνά ΠΑΝΩ από χαμηλό τοίχο) ή σκάλα που φαίνεται από πάνω – δεν ελέγχεται
            ln = LineString([a, b])
            inside = ln.intersection(solid.buffer(-0.012)).length
            if inside > 0.02:
                deep.append("%s (%.0f cm)" % (n_, inside * 100))
        # οι τοίχοι που θεωρεί το φύλλο της σκάλας υπάρχουν στις τοιχοποιίες: παρειά τοίχου πλατύσκαλου · πόρτα (υπόγειο) · παρειές κλάδων
        d = S[key]; probs = []
        segs = []                     # όλες οι ακμές τοίχων / σκυροδέματος (και των εσωτερικών δακτυλίων της ένωσης)
        for g in (list(solid.geoms) if hasattr(solid, "geoms") else [solid]):
            for ring in [g.exterior] + list(g.interiors):
                cs = list(ring.coords); segs += list(zip(cs[:-1], cs[1:]))
        def face_x(x, y0, y1):       # υπάρχει παρειά τοίχου / σκυροδέματος στο x, κάπου μέσα στο y0…y1;
            return any(abs(ax - x) < 0.006 and abs(bx - x) < 0.006 and min(ay, by) < y1 - 0.05 and max(ay, by) > y0 + 0.05 for (ax, ay), (bx, by) in segs)
        def face_y(y, x0, x1):
            return any(abs(ay - y) < 0.006 and abs(by - y) < 0.006 and min(ax, bx) < x1 - 0.05 and max(ax, bx) > x0 + 0.05 for (ax, ay), (bx, by) in segs)
        if not M.STAIR.get("top"):
            if "wall_x" in d and key != "S7" and not face_x(d["wall_x"], 5.10, 7.60):
                probs.append("δεν υπάρχει παρειά τοίχου στο x %.2f (τοίχος πλατύσκαλου κατά το φύλλο της σκάλας)" % d["wall_x"])
            if "door_y" in d and not any(abs(min(h[1], j[1]) - d["door_y"][0]) < 0.006 and abs(max(h[1], j[1]) - d["door_y"][1]) < 0.006 and abs(h[0] - d["wall_x"]) < 0.11
                                         for h, l, j in M.DOORS):
                probs.append("η πόρτα %.2f–%.2f του φύλλου της σκάλας δεν υπάρχει στις τοιχοποιίες" % tuple(d["door_y"]))
            ys_, yn_ = d.get("ys"), d.get("yn")
            if key == "S7": ys_, yn_ = 7.60, None          # Δ΄: νότια παρειά του κάτω κλάδου της ιδιωτικής σκάλας = παρειά Τ2-10
            if ys_ is not None and not face_y(ys_, 10.90, 13.10):
                probs.append("δεν υπάρχει παρειά στο y %.2f (νότια παρειά του κλάδου)" % ys_)
            if key == "S7" and not face_y(6.60, 10.90, 12.10):
                probs.append("δεν υπάρχει παρειά στο y 6,60 (βόρεια παρειά του κάτω κλάδου – Τ6Α-02)")
        add(k, "Σκάλες", "τοίχοι γύρω από τη σκάλα = φύλλο σκάλας", "; ".join(probs) if probs else "παρειές / πόρτα όπως στο φύλλο της σκάλας", "ΛΑΘΟΣ" if probs else "OK")
        add(k, "Σκάλες", "ρίχτια ↔ τοίχοι (ως την τομή)", "κανένα ρίχτι μέσα σε τοίχο" if not deep else "ρίχτια μέσα σε τοίχο: " + ", ".join(deep), "OK" if not deep else "ΛΑΘΟΣ")


def areas(k, M, walls, cols, wins):
    res = 0.01
    polys = [Polygon(w["pts"]) for w in M.WALLS] + [Polygon(p) for p in M.COLS] + [Polygon(p) for p in M.WINS]
    x0 = min(p.bounds[0] for p in polys) - 0.5; y0 = min(p.bounds[1] for p in polys) - 0.5
    x1 = max(p.bounds[2] for p in polys) + 0.5; y1 = max(p.bounds[3] for p in polys) + 0.5
    nx, ny = int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1
    import pymupdf
    # raster με PyMuPDF (γρήγορο γέμισμα πολυγώνων)
    doc = pymupdf.open(); page = doc.new_page(width=nx, height=ny)
    sh = page.new_shape()
    def P(x, y): return pymupdf.Point((x - x0) / res, (y - y0) / res)
    for pl in polys:
        sh.draw_polyline([P(*c) for c in pl.exterior.coords]); sh.finish(fill=(0, 0, 0), color=(0, 0, 0), width=0.5)
    for h, l, j in M.DOORS:
        sh.draw_line(P(*h), P(*j)); sh.finish(color=(0, 0, 0), width=3)
    for a, b in SEPS.get(k, []):
        sh.draw_line(P(*a), P(*b)); sh.finish(color=(0, 0, 0), width=3)
    sh.commit()
    pix = page.get_pixmap(alpha=False, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width) > 128        # True = ελεύθερο
    from collections import deque
    def fill(px, py, extra_block=None):
        free = img.copy()
        if extra_block is not None:
            free &= ~extra_block
        if not (0 <= px < free.shape[1] and 0 <= py < free.shape[0]) or not free[py, px]:
            return None
        seen = np.zeros_like(free); q = deque([(px, py)]); seen[py, px] = True; n = 0; border = False
        H, W = free.shape
        while q:
            cx, cy = q.popleft(); n += 1
            if cx == 0 or cy == 0 or cx == W - 1 or cy == H - 1:
                border = True; break
            for ax, ay in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if free[ay, ax] and not seen[ay, ax]:
                    seen[ay, ax] = True; q.append((ax, ay))
        return None if border else n * res * res
    # ντουλάπες ως εμπόδιο (καθαρό δάπεδο)
    wb = np.zeros_like(img)
    for wd in M.WARDROBES:
        r = wd["r"]; wb[int((r[1] - y0) / res):int((r[3] - y0) / res) + 1, int((r[0] - x0) / res):int((r[2] - x0) / res) + 1] = True
    for name, area, (x, y) in M.ROOMS:
        m = re.search(r"≈\s*([0-9]+,[0-9]+)\s*m²", name + " " + area)
        if not m or name.startswith("ΑΝΕΛΚ") or "+ ντους" in area:      # φρεάτιο (του αρχιτέκτονα) · «+ ντους» = μόνο το κύριο τμήμα
            continue
        lab = float(m.group(1).replace(",", "."))
        px, py = int((x - x0) / res), int((y - y0) / res)
        a_all = fill(px, py); a_net = fill(px, py, wb)
        if a_all is None:
            add(k, "Εμβαδά", name, "ετικέτα %.2f · ο χώρος δεν κλείνει (ανοιχτός) – δεν ελέγχεται" % lab, "ΣΗΜ.")
            continue
        best = min((abs(a - lab), a, t) for a, t in ((a_all, "με ντουλάπες"), (a_net if a_net else a_all, "χωρίς ντουλάπες")))
        ok = best[0] <= max(0.25, 0.025 * lab)      # η μέτρηση πιάνει και τα κατώφλια των πορτών / εσοχές κουφωμάτων
        add(k, "Εμβαδά", name, "ετικέτα ≈ %.2f m² · μοντέλο %.2f (%s) · καθαρό %.2f / με ντουλάπες %.2f" % (lab, best[1], best[2], a_net or a_all, a_all),
            "OK" if ok else "ΛΑΘΟΣ")


def run(keys):
    r = subprocess.run([sys.executable, os.path.join(HERE, "..", "xylotypoi_A3", "export_stairs.py"), "--check"], capture_output=True, text=True)
    add("*", "Σκάλες", "stairs.json ↔ μοντέλα σκαλών", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:], "OK" if r.returncode == 0 else "ΛΑΘΟΣ")
    for k in keys:
        M = importlib.import_module(MODELS[k])
        walls, cols, wins = geom(M)
        solid = unary_union([walls, cols])
        doors(k, M, solid, wins); fixtures(k, M, walls, cols); stairs(k, M, walls); areas(k, M, walls, cols, wins)
    bad = [r_ for r_ in rows if r_[4] == "ΛΑΘΟΣ"]
    for r_ in rows:
        print("%-3s %-6s %-14s %-34s | %s" % (r_[0], r_[4], r_[1], r_[2][:34], r_[3]))
    print("\nΣύνολο %d έλεγχοι · ΛΑΘΟΣ %d" % (len(rows), len(bad)))
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if run(sys.argv[1:] or list(MODELS)) else 0)
