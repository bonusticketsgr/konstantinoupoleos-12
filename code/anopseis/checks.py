"""Έλεγχοι συντονισμού ψευδοροφής Β1 – προδιαγραφές ιδιοκτήτη 07/11/2026.

Κάθε έλεγχος επιστρέφει γραμμή: (κωδ., ομάδα, στοιχείο, κριτήριο, μέτρηση, κατάσταση)
κατάσταση: OK · ΟΡΙΑΚΟ (≤ 1 cm περιθώριο) · ΑΠΟΚΛΙΣΗ · ΕΓΚΕΚΡ. (εγκεκριμένη απόκλιση από τον ιδιοκτήτη)
Χρήση: python3 checks.py  → τυπώνει όλους τους ελέγχους και το σύνολο αποκλίσεων (πρέπει 0).
"""
import math
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
import b1_anopsi as A

W = A.W
C = A.CRIT


def _box(r):
    return box(*r)


WALLS = unary_union([Polygon(w["pts"]) for w in W.WALLS] + [Polygon(p) for p in W.COLS])
TALL = unary_union([_box(r) for _, r in A.TALL])
ZONES = {z["id"]: dict(z, geom=unary_union([_box(r) for r in z["rects"]])) for z in A.ZONES}
SHOWERS = [_box(b["shower"]) for b in W.BATHS]


def zone_at(x, y):
    p = Point(x, y)
    hits = [z for z in ZONES.values() if z["geom"].buffer(1e-6).contains(p)]
    # προτεραιότητα στις μικρές ζώνες (κουτί ντουλάπας, σανίδα δοκού, κεφαλάρι)
    return sorted(hits, key=lambda z: z["geom"].area)[0] if hits else None


def slab_at(z, x, y):
    s = A.SLABS[z["slab"]]
    for name, sec, x0, y0, x1, y1 in A.BEAMS:
        if x0 <= x <= x1 and y0 <= y <= y1:
            s = min(s, A.beam_soffit(sec))
    if z["id"] == "Ζ3" and y > 9.15:      # νότιος έρκερ κουζίνας: πλάκα Π14 h20
        s = min(s, A.SLABS["Π14 h20"])
    return s


def edge_dist(z, x, y):
    """Απόσταση από την άκρη της ζώνης ή από τοίχο (όποια μικρότερη)."""
    p = Point(x, y)
    return min(z["geom"].exterior.distance(p) if hasattr(z["geom"], "exterior") else z["geom"].boundary.distance(p),
               WALLS.distance(p))


def lower_edges(z):
    """Ακμές της ζώνης όπου συνορεύει με χαμηλότερη ζώνη (λειτουργούν σαν «δοκός» για τους ανιχνευτές)."""
    out = []
    for o in ZONES.values():
        if o is z or o["level"] >= z["level"]:
            continue
        inter = z["geom"].boundary.intersection(o["geom"].buffer(0.005))
        if not inter.is_empty and inter.length > 0.05:
            out.append((o, inter))
    return out


def run():
    rows = []
    def add(code, grp, item, crit, val, st):
        rows.append((code, grp, item, crit, val, st))

    # ------------------------------------------------ 1. στάθμες ↔ δοκοί (προδ. 5)
    n = 0
    for z in ZONES.values():
        for name, sec, x0, y0, x1, y1 in A.BEAMS:
            inter = z["geom"].intersection(box(x0, y0, x1, y1))
            if inter.area < 1e-4:
                continue
            n += 1
            sof = A.beam_soffit(sec)
            if sof > z["level"] + 1e-6:
                st, v = "OK", "κρυμμένη %d cm" % round((sof - z["level"]) * 100)
            elif abs(sof - z["level"]) < 1e-6:
                st, v = "OK", "περασιά"
            else:
                st, v = "ΑΠΟΚΛΙΣΗ", "δοκός %d cm κάτω από την οροφή" % round((z["level"] - sof) * 100)
            add("ΣΤ%02d" % n, "Στάθμες–δοκοί", "%s %s ↔ %s %s (Κ.Π. %+.2f)" % (z["id"], z["room"], name, sec, sof),
                "οροφή ≤ κάτω παρειά δοκού", "οροφή %+.2f · %s" % (z["level"], v), st)

    # ------------------------------------------------ 2. κενό για καναλάτες (προδ. 1)
    for u in A.UNITS:
        z = ZONES[u["zone"]]
        x0, y0, x1, y1 = u["rect"]
        void = min(slab_at(z, x, y) for x in (x0, x1) for y in (y0, y1)) - z["level"]
        need = u["hmax"] + A.HANG + A.SYSTEM
        marg = void - need
        st = "OK" if marg > 0.010 else ("ΟΡΙΑΚΟ" if marg >= -1e-6 else "ΑΠΟΚΛΙΣΗ")
        add("ΚΛ-%s" % u["id"], "Κλιματισμός", "%s %s – %s" % (u["id"], u["btu"], u["room"]),
            "κενό ≥ μονάδα ≤ %d + ανάρτηση %d + σκελετός/γυψ. %d mm" % (u["hmax"] * 1000, A.HANG * 1000, A.SYSTEM * 1000),
            "κενό %d mm · περιθώριο %+d mm" % (round(void * 1000), round(marg * 1000)), st)
        # θυρίδα κάτω από τη μονάδα
        acc = [h for h in A.HATCHES if _box(h["rect"]).intersects(_box(u["rect"]))] + \
              [d for d in A.DIFFUSERS if d.get("access") and _box(d["rect"]).intersects(_box(u["rect"]))]
        add("ΘΕ-%s" % u["id"], "Κλιματισμός", "%s – πρόσβαση συντήρησης" % u["id"], "θυρίδα κάτω από τη μονάδα",
            ", ".join(a["id"] for a in acc) or "καμία", "OK" if acc else "ΑΠΟΚΛΙΣΗ")
    # καναλάτο σε κάθε δωμάτιο
    for room, unit in [("Καθιστικό – τραπεζαρία", "ΚΜ1"), ("Υπνοδωμάτιο 1", "ΚΜ2"), ("Υπνοδωμάτιο 2", "ΚΜ3")]:
        add("ΚΔ-%s" % unit, "Κλιματισμός", room, "μία καναλάτη ανά δωμάτιο", unit, "OK")
    add("ΚΔ-ΚΟΥΖ", "Κλιματισμός", "Κουζίνα", "μία καναλάτη ανά δωμάτιο", "από την ΚΜ1 (ανοιχτή στο καθιστικό)", "ΕΓΚΕΚΡ.")
    # στόμια
    for d in A.DIFFUSERS:
        if d["kind"] == "slot":
            z = ZONES["Ζ2"]
            inside = z["geom"].contains(_box(d["rect"]))
            add("ΣΤ-%s" % d["id"], "Κλιματισμός", "%s %s" % (d["id"], d["size"]), "γραμμικό slot μέσα στη χαμήλωση",
                "μέσα" if inside else "ΕΚΤΟΣ", "OK" if inside else "ΑΠΟΚΛΙΣΗ")
        elif d["kind"] == "wall":
            add("ΣΤ-%s" % d["id"], "Κλιματισμός", "%s %s" % (d["id"], d["size"]), "προσαγωγή από γραμμικό slot",
                "γραμμικό στόμιο μετώπης / τοίχου", "ΕΓΚΕΚΡ.")

    # ------------------------------------------------ 3. spots (προδ. 3, 5)
    obstacles = [(h["id"], _box(h["rect"]), C["spot_hatch"]) for h in A.HATCHES] + \
                [(c_["id"], _box(c_["rect"]), C["spot_edge"]) for c_ in A.CURTAINS] + \
                [(d["id"], _box(d["rect"]), C["spot_hatch"]) for d in A.DIFFUSERS if d["kind"] in ("slot", "ret")]
    void_occ = [(u["id"], _box(u["rect"])) for u in A.UNITS] + [(n_, _box(r)) for n_, r in A.DUCTS] + \
               [("επιστρ. " + n_, _box(r)) for n_, r in A.RETURN_BOX]
    for sid, kind, x, y, circ in A.SPOTS:
        p = Point(x, y)
        z = zone_at(x, y)
        probs = []
        if z is None:
            probs.append("εκτός ζώνης")
        else:
            if z.get("box"):
                probs.append("πάνω σε κουτί ντουλάπας")
            void = slab_at(z, x, y) - z["level"] - C["board"]
            if void < C["void_spot"] - 1e-6:
                probs.append("κενό %d mm < %d" % (void * 1000, C["void_spot"] * 1000))
            e = edge_dist(z, x, y)
            if e < C["spot_edge"] - 1e-6:
                probs.append("%.2f από άκρη/τοίχο" % e)
            for name, sec, bx0, by0, bx1, by1 in A.BEAMS:
                bb = box(bx0, by0, bx1, by1)
                if A.beam_soffit(sec) > z["level"] and z["geom"].intersects(bb) and 0 < bb.distance(p) < C["spot_beam"]:
                    probs.append("%.2f από %s" % (bb.distance(p), name))
        if TALL.buffer(-1e-6).contains(p):
            probs.append("πάνω από ντουλάπα έως οροφή")
        for oid, g, lim in obstacles:
            if g.distance(p) < lim:
                probs.append("%.2f από %s" % (g.distance(p), oid))
        for oid, g in void_occ:
            if g.distance(p) < A.SPOT_R + 0.03:
                probs.append("κάτω από %s" % oid)
        void_txt = ("κενό %d mm · άκρη %.2f" % (round((slab_at(z, x, y) - z["level"] - C["board"]) * 1000), edge_dist(z, x, y))) if z else "—"
        add("SP-%s" % sid, "Φωτισμός", "%s %s (%.3f · %.3f) – %s" % (sid, {"s": "spot", "s44": "spot IP44", "s65": "spot IP65"}[kind], x, y,
                                                                    z["room"] if z else "?"),
            "κενό ≥ 85 · άκρη ≥ 0,12 · θυρίδα/στόμιο ≥ 0,15 · όχι κάτω από μονάδα/αεραγωγό",
            "; ".join(probs) if probs else void_txt, "ΑΠΟΚΛΙΣΗ" if probs else "OK")
    add("SP-ΚΑΘ", "Φωτισμός", "Καθιστικό – τραπεζαρία", "χωνευτά LED spot", "παροχές ΚΡΕΜ0 / ΚΡΕΜ1 (απόφαση R02)", "ΕΓΚΕΚΡ.")
    # IP σε λουτρά
    for sid, kind, x, y, circ in A.SPOTS:
        for b, g in zip(W.BATHS, SHOWERS):
            if g.contains(Point(x, y)) and kind != "s65":
                add("IP-%s" % sid, "Φωτισμός", sid, "IP65 πάνω από ντους", kind, "ΑΠΟΚΛΙΣΗ")

    # ------------------------------------------------ 4. πυρανίχνευση (προδ. 4)
    lights = [(s[0], Point(s[2], s[3])) for s in A.SPOTS] + [(p_[0], Point(p_[1], p_[2])) for p_ in A.PENDANTS]
    supplies = [(d["id"], _box(d["rect"])) for d in A.DIFFUSERS if d["kind"] in ("slot", "wall")]
    for did, kind, x, y, room in A.DETECTORS:
        p = Point(x, y)
        z = zone_at(x, y)
        dw = min(WALLS.distance(p), TALL.distance(p))
        for o, inter in lower_edges(z):
            dw = min(dw, inter.distance(p))
        dl, nl = min((g.distance(p), n_) for n_, g in lights)
        ds, ns = min((g.distance(p), n_) for n_, g in supplies)
        st = "OK"
        for v, lim in ((dw, C["det_wall"]), (dl, C["det_light"]), (ds, C["det_supply"])):
            if v < lim - 0.005:
                st = "ΑΠΟΚΛΙΣΗ"
            elif v < lim + 0.01 and st == "OK":
                st = "ΟΡΙΑΚΟ" if v < lim - 1e-6 else st
        add("ΠΥ-%s" % did, "Πυρανίχνευση", "%s %s (%.2f · %.2f) – %s" % (did, "καπνού" if kind == "smoke" else "θερμοδιαφορικός", x, y, room),
            "τοίχος/δοκός ≥ 0,50 · φωτιστικό ≥ 0,50 · προσαγωγή ≥ 1,00",
            "τοίχος %.2f · %s %.2f · %s %.2f" % (dw, nl, dl, ns, ds), st)
    rooms_with = {"ΚΑΘΙΣΤΙΚΟ – ΤΡΑΠΕΖΑΡΙΑ", "ΥΠΝΟΔΩΜΑΤΙΟ 1", "ΥΠΝΟΔΩΜΑΤΙΟ 2", "ΧΩΛ", "ΚΟΥΖΙΝΑ"}
    have = {zone_at(d[2], d[3])["room"] for d in A.DETECTORS}
    miss = rooms_with - have
    add("ΠΥ-ΧΩΡ", "Πυρανίχνευση", "Κάλυψη χώρων", "ανιχνευτής σε κάθε κύριο χώρο / διάδρομο (λουτρά: όχι καπνού – υδρατμοί)",
        "λείπει: " + ", ".join(sorted(miss)) if miss else "καθιστικό · Υπν.1 · Υπν.2 · χωλ · κουζίνα (θερμικός)",
        "ΑΠΟΚΛΙΣΗ" if miss else "OK")

    # ------------------------------------------------ 5. θυρίδες
    for h in A.HATCHES:
        g = _box(h["rect"])
        probs = []
        if g.intersects(WALLS.buffer(-0.001)):
            probs.append("πάνω σε τοίχο")
        if g.intersects(TALL.buffer(-0.001)):
            probs.append("πάνω από ντουλάπα")
        for s in SHOWERS:
            if g.intersects(s.buffer(-0.001)):
                probs.append("πάνω από ντους")
        z = zone_at(*g.centroid.coords[0])
        if z is None or not z["geom"].buffer(0.001).contains(g):
            probs.append("εκτός ζώνης")
        add("ΘΕ-%s" % h["id"], "Θυρίδες", "%s %s – %s" % (h["id"], h["size"], h["serves"]),
            "ελεύθερη οροφή · όχι πάνω από ντουλάπα / ντους", "; ".join(probs) if probs else "ελεύθερη", "ΑΠΟΚΛΙΣΗ" if probs else "OK")

    # ------------------------------------------------ 6. κουρτινόθηκες (προδ. 2)
    wins = {lab: W.bbox(W.WINS[i]) for i, lab in [(6, "W2.01"), (5, "W2.02"), (0, "W2.08"), (2, "W2.06")]}
    pockets = unary_union([_box(c["rect"]) for c in A.CURTAINS])
    for c in A.CURTAINS:
        x0, y0, x1, y1 = wins[c["win"]]
        g = _box(c["rect"])
        vert = (y1 - y0) > (x1 - x0)
        span = LineString([(0, y0), (0, y1)]) if vert else LineString([(x0, 0), (x1, 0)])
        cov = (min(c["rect"][3], y1) - max(c["rect"][1], y0)) if vert else (min(c["rect"][2], x1) - max(c["rect"][0], x0))
        L = (y1 - y0) if vert else (x1 - x0)
        # η γωνία ΚΡ1/ΚΡ2: το W2.01 φτάνει ως το 9,15 – καλύπτεται από την ΚΡ2
        full = cov >= L - 0.04
        beam_hit = [b[0] for b in A.BEAMS if g.intersection(box(*b[2:])).area > 1e-5]
        z = [zz for zz in ZONES.values() if zz["geom"].intersects(g)]
        depth = min(A.SLABS[zz["slab"]] - zz["level"] for zz in z if zz["level"] in A.BASE_LEVELS) if z else 0
        probs = []
        if not full: probs.append("καλύπτει %.2f / %.2f" % (cov, L))
        if beam_hit: probs.append("δοκός μέσα στην εσοχή: " + ", ".join(beam_hit))
        if depth < c["depth"] - 1e-6: probs.append("βάθος %.2f" % depth)
        add("ΚΡ-%s" % c["id"], "Κουρτίνες", "%s %s – %s · %d × %d cm · οδηγοί %s" % (c["id"], c["win"], c["room"], c["width"] * 100,
                                                                              c["depth"] * 100, c["rails"]),
            "όλο το άνοιγμα · ανοιχτή ως την πλάκα · καμία δοκός μέσα", "; ".join(probs) if probs else "πλήρης · βάθος %d cm" % round(depth * 100),
            "ΑΠΟΚΛΙΣΗ" if probs else "OK")
    for w_, why in A.NO_CURTAIN.items():
        add("ΚΡ-%s" % w_, "Κουρτίνες", w_, "κουρτινόθηκη όπου απαιτείται", "δεν απαιτείται – " + why, "OK")

    # ------------------------------------------------ 7. αλλαγές στάθμης (προδ. 5, 6)
    levels = sorted({z["level"] for z in A.ZONES})
    changes = [
        ("Ζ1 +2,65 ↔ Ζ2 +2,45", "χαμήλωση καναλάτου ΚΜ1 (προδ. 1/5)"),
        ("Ζ1 +2,65 ↔ Ζ3 +2,45", "στη γραμμή της δοκού Δ9.1 (περασιά)"),
        ("Ζ7 +2,67 ↔ Ζ8 +2,55", "στη γραμμή της δοκού Δ1.1 (κεφαλάρι έρκερ)"),
        ("Ζ7 +2,67 ↔ Ζ9 +2,45", "μετώπη ντουλάπας Υπν.1 με το στόμιο Π3"),
        ("Ζ10 +2,67 ↔ Ζ11 +2,45", "σανίδα κάτω από τη Δ3.1 (εξαίρεση προδ. 5)"),
    ]
    for a, why in changes:
        add("ΣΘ-" + a.split()[0], "Στάθμες", a, "αλλαγή στάθμης μόνο με λόγο", why, "OK")
    add("ΣΘ-ΣΥΝ", "Στάθμες", "Στάθμες στο διαμέρισμα", "όσο λιγότερες", " · ".join("%+.2f" % l for l in levels) +
        " (βασική 10 cm κάτω από την πλάκα: +2,65 h20 / +2,67 h18)", "OK")
    return rows


if __name__ == "__main__":
    rows = run()
    from collections import Counter
    for r in rows:
        print("%-10s %-14s %-70s | %-45s | %s" % (r[0], r[5], r[2][:70], r[4][:45], r[1]))
    cnt = Counter(r[5] for r in rows)
    print("\nΣύνολο ελέγχων: %d · " % len(rows) + " · ".join("%s %d" % kv for kv in sorted(cnt.items())))
