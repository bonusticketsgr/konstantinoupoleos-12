"""Έλεγχοι συντονισμού ψευδοροφής – προδιαγραφές ιδιοκτήτη 07/11/2026 – για κάθε όροφο (μοντέλο *_anopsi.py).

Κάθε έλεγχος επιστρέφει γραμμή: (κωδ., ομάδα, στοιχείο, κριτήριο, μέτρηση, κατάσταση)
κατάσταση: OK · ΟΡΙΑΚΟ (≤ 1 cm περιθώριο) · ΑΠΟΚΛΙΣΗ · ΕΓΚΕΚΡ. (εγκεκριμένη απόκλιση από τον ιδιοκτήτη)
Χρήση: python3 checks.py [b1|f4|s|gf]  → τυπώνει όλους τους ελέγχους και το σύνολο αποκλίσεων (πρέπει 0).
Από κώδικα: checks.bind(μοντέλο); checks.run()
"""
import importlib, sys
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union

A = W = C = None
WALLS = TALL = SHOWERS = None
ZONES = {}


def _box(r):
    return box(*r)


def bind(model):
    """Δένει τους ελέγχους σε ένα μοντέλο ανόψης (b1_anopsi, f4_anopsi, s_anopsi, gf_anopsi)."""
    global A, W, C, WALLS, TALL, ZONES, SHOWERS
    A, W, C = model, model.W, model.CRIT
    WALLS = unary_union([Polygon(w["pts"]) for w in W.WALLS] + [Polygon(p) for p in W.COLS])
    TALL = unary_union([_box(r) for _, r in A.TALL]) if A.TALL else Polygon()
    ZONES = {z["id"]: dict(z, geom=unary_union([_box(r) for r in z["rects"]])) for z in A.ZONES}
    SHOWERS = [_box(b["shower"]) for b in W.BATHS if b.get("shower")]
    return model


def zone_at(x, y):
    p = Point(x, y)
    hits = [z for z in ZONES.values() if z["geom"].buffer(1e-6).contains(p)]
    # προτεραιότητα στις μικρές ζώνες (κουτί ντουλάπας, σανίδα δοκού, κεφαλάρι)
    return sorted(hits, key=lambda z: z["geom"].area)[0] if hits else None


def slab_at(z, x, y):
    s = A.SLABS[z["slab"]]
    for r, sl in z.get("slab_parts", []):          # τμήματα ζώνης κάτω από άλλη πλάκα (π.χ. νότιος έρκερ κουζίνας Β1: Π14)
        if r[0] <= x <= r[2] and r[1] <= y <= r[3]:
            s = min(s, A.SLABS[sl])
    for name, sec, x0, y0, x1, y1 in A.BEAMS:
        if x0 <= x <= x1 and y0 <= y <= y1:
            s = min(s, A.beam_soffit(sec))
    return s


def edge_dist(z, x, y):
    """Απόσταση από την άκρη της ζώνης ή από τοίχο (όποια μικρότερη)."""
    p = Point(x, y)
    return min(z["geom"].boundary.distance(p), WALLS.distance(p))


def lower_edges(z):
    """Ακμές της ζώνης όπου συνορεύει με χαμηλότερη ζώνη (λειτουργούν σαν «δοκός» για τους ανιχνευτές)."""
    out = []
    for o in ZONES.values():
        if o is z or o["level"] >= z["level"] - 1e-6:
            continue
        inter = z["geom"].boundary.intersection(o["geom"].buffer(0.005))
        if not inter.is_empty and inter.length > 0.05:
            out.append((o, inter))
    return out


def L(v):
    return ("%+.2f" % v).replace(".", ",")


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
    for z in A.ZONES:
        if z.get("exposed"):
            add("ΣΤ-%s" % z["id"], "Στάθμες–δοκοί", "%s %s – εμφανής πλάκα %s" % (z["id"], z["room"], L(z["level"])),
                "οροφή χωρίς δοκούς κάτω από την πλάκα", z.get("exposed_txt", "ανεστραμμένες δοκοί – επίπεδη κάτω παρειά"), "OK")

    # ------------------------------------------------ 2. κλιματισμός (προδ. 1)
    for u in A.UNITS:
        if u.get("concealed"):          # κρυφή μονάδα σε ντουλάπα / τοίχο (σοφίτα)
            cc = u["concealed"]
            avail = cc["slab"] - cc["top"]
            need = u["hmax"] + A.HANG + cc.get("board", 0.02)
            marg = avail - need
            st = "OK" if marg > 0.010 else ("ΟΡΙΑΚΟ" if marg >= -1e-6 else "ΑΠΟΚΛΙΣΗ")
            add("ΚΛ-%s" % u["id"], "Κλιματισμός", "%s %s – %s (κρυφή)" % (u["id"], u["btu"], u["room"]),
                "χώρος ≥ μονάδα ≤ %d + ανάρτηση %d + καπάκι %d mm" % (u["hmax"] * 1000, A.HANG * 1000, cc.get("board", 0.02) * 1000),
                "%s %d mm · περιθώριο %+d mm" % (cc["where"], round(avail * 1000), round(marg * 1000)), st)
            add("ΘΕ-%s" % u["id"], "Κλιματισμός", "%s – πρόσβαση συντήρησης" % u["id"], "πρόσβαση στη μονάδα / φίλτρο",
                cc["access"], "OK")
            continue
        x0, y0, x1, y1 = u["rect"]
        z = ZONES[u["zone"]]
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
    # οδεύσεις ψυκτικών στο κενό της οροφής: δέσμη ψυκτικών + συμπυκνωμάτων με μόνωση ≈ 50 mm πάνω από τον σκελετό
    beams = [box(*b[2:]) for b in A.BEAMS]
    for rt in getattr(A, "REFR_CHECK", []):
        route = LineString(rt["pts"])
        worst = 9.0
        for i in range(int(route.length / 0.05) + 1):
            pt = route.interpolate(i * 0.05)
            z = zone_at(pt.x, pt.y)
            if z is None or any(bb.buffer(0.01).contains(pt) for bb in beams):
                continue        # τοίχοι / διέλευση κάτω από δοκό: χωριστά
            worst = min(worst, slab_at(z, pt.x, pt.y) - z["level"] - A.SYSTEM)
        add(rt["id"], "Κλιματισμός", rt["text"], "καθαρό κενό πάνω από τον σκελετό ≥ 50 mm",
            "ελάχιστο %d mm" % round(worst * 1000), "OK" if worst >= 0.05 + 0.01 else ("ΟΡΙΑΚΟ" if worst >= 0.05 else "ΑΠΟΚΛΙΣΗ"))
    for cr in getattr(A, "CROSSINGS", []):
        bsec = [b for b in A.BEAMS if b[0] == cr["beam"]][0][1]
        clear = A.beam_soffit(bsec) - ZONES[cr["zone"]]["level"] - C["board"]
        marg = clear - cr["pipe_od"]
        add(cr.get("code", "ΨΥ-ΔΟΚ"), "Κλιματισμός", "Διέλευση ψυκτικών %s κάτω από τη %s (x ≈ %.2f%s)" % (cr["unit"], cr["beam"], cr["x"], cr.get("via", "")),
            "καθαρό κάτω από τη δοκό ≥ σωλήνας %s" % cr["pipe_txt"], "καθαρό %.1f mm · περιθώριο %+.1f mm" % (clear * 1000, marg * 1000),
            "OK" if marg > 0.010 else ("ΟΡΙΑΚΟ" if marg >= 0 else "ΑΠΟΚΛΙΣΗ"))
    # καναλάτο σε κάθε δωμάτιο
    for code, room, unit, st in A.ROOM_UNITS:
        add("ΚΔ-%s" % code, "Κλιματισμός", room, "μία καναλάτη ανά δωμάτιο", unit, st)
    # στόμια
    for d in A.DIFFUSERS:
        if d["kind"] == "slot":
            zid = d.get("zone") or [u["zone"] for u in A.UNITS if u["id"] == d["unit"]][0]
            z = ZONES[zid]
            inside = z["geom"].buffer(1e-6).contains(_box(d["rect"]))
            add("ΣΤ-%s" % d["id"], "Κλιματισμός", "%s %s" % (d["id"], d["size"]), d.get("crit", "γραμμικό slot μέσα στη χαμήλωση"),
                "μέσα" if inside else "ΕΚΤΟΣ", "OK" if inside else "ΑΠΟΚΛΙΣΗ")
        elif d["kind"] == "wall":
            add("ΣΤ-%s" % d["id"], "Κλιματισμός", "%s %s" % (d["id"], d["size"]), "προσαγωγή από γραμμικό slot",
                d.get("check_txt", "γραμμικό στόμιο μετώπης / τοίχου"), d.get("status", "ΕΓΚΕΚΡ."))

    # ------------------------------------------------ 3. spots (προδ. 3, 5)
    obstacles = [(h["id"], _box(h["rect"]), C["spot_hatch"]) for h in A.HATCHES] + \
                [(c_["id"], _box(c_["rect"]), C["spot_edge"]) for c_ in A.CURTAINS] + \
                [(n_, _box(r), C["spot_tall"]) for n_, r in A.TALL] + \
                [(d["id"], _box(d["rect"]), C["spot_hatch"]) for d in A.DIFFUSERS if d["kind"] in ("slot", "ret")]
    void_occ = [(u["id"], _box(u["rect"])) for u in A.UNITS if not u.get("concealed")] + [(n_, _box(r)) for n_, r in A.DUCTS] + \
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
            if not z.get("exposed"):
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
        if A.TALL and TALL.buffer(-1e-6).contains(p):
            probs.append("πάνω από ντουλάπα έως οροφή")
        for oid, g, lim in obstacles:
            if g.distance(p) < lim:
                probs.append("%.2f από %s" % (g.distance(p), oid))
        for oid, g in void_occ:
            if g.distance(p) < A.SPOT_R + 0.03:
                probs.append("κάτω από %s" % oid)
        if z and z.get("exposed"):
            void_txt = "κουτί σκυροδέματος στον ξυλότυπο · άκρη %.2f" % edge_dist(z, x, y)
        elif z:
            void_txt = "κενό %d mm · άκρη %.2f" % (round((slab_at(z, x, y) - z["level"] - C["board"]) * 1000), edge_dist(z, x, y))
        else:
            void_txt = "—"
        add("SP-%s" % sid, "Φωτισμός", "%s %s (%.3f · %.3f) – %s" % (sid, {"s": "spot", "s44": "spot IP44", "s65": "spot IP65"}[kind], x, y,
                                                                    z["room"] if z else "?"),
            "κενό ≥ 85 · άκρη ≥ 0,12 · θυρίδα/στόμιο ≥ 0,15 · όχι κάτω από μονάδα/αεραγωγό",
            "; ".join(probs) if probs else void_txt, "ΑΠΟΚΛΙΣΗ" if probs else "OK")
    for code, item, crit, val, st in getattr(A, "LIGHT_ROWS", []):
        add(code, "Φωτισμός", item, crit, val, st)
    # IP σε λουτρά
    for sid, kind, x, y, circ in A.SPOTS:
        for g in SHOWERS:
            if g.contains(Point(x, y)) and kind != "s65":
                add("IP-%s" % sid, "Φωτισμός", sid, "IP65 πάνω από ντους", kind, "ΑΠΟΚΛΙΣΗ")

    # ------------------------------------------------ 4. πυρανίχνευση (προδ. 4)
    lights = [(s[0], Point(s[2], s[3])) for s in A.SPOTS] + [(p_[0], Point(p_[1], p_[2])) for p_ in A.PENDANTS]
    supplies = [(d["id"], _box(d["rect"])) for d in A.DIFFUSERS if d["kind"] in ("slot", "wall")]
    for did, kind, x, y, room in A.DETECTORS:
        p = Point(x, y)
        z = zone_at(x, y)
        dw = min(WALLS.distance(p), TALL.distance(p)) if A.TALL else WALLS.distance(p)
        if z:
            for o, inter in lower_edges(z):
                dw = min(dw, inter.distance(p))
        lim_w = C["det_wall"]
        note = ""
        if z and z.get("corridor"):           # διάδρομος < 1,00: ανιχνευτής στον άξονα (κανόνας στενών διαδρόμων)
            lim_w = min(lim_w, z["corridor"] / 2 - 0.005)
            note = " (διάδρομος %s – άξονας)" % ("%.2f" % z["corridor"]).replace(".", ",")
        dl, nl = min((g.distance(p), n_) for n_, g in lights) if lights else (9, "—")
        ds, ns = min((g.distance(p), n_) for n_, g in supplies) if supplies else (9, "—")
        st = "OK"
        for v, lim in ((dw, lim_w), (dl, C["det_light"]), (ds, C["det_supply"])):
            if v < lim - 0.005:
                st = "ΑΠΟΚΛΙΣΗ"
            elif v < lim + 0.01 and st == "OK":
                st = "ΟΡΙΑΚΟ" if v < lim - 1e-6 else st
        add("ΠΥ-%s" % did, "Πυρανίχνευση", "%s %s (%.2f · %.2f) – %s" % (did, "καπνού" if kind == "smoke" else "θερμοδιαφορικός", x, y, room),
            "τοίχος/δοκός ≥ 0,50 · φωτιστικό ≥ 0,50 · προσαγωγή ≥ 1,00",
            "τοίχος %.2f%s · %s %.2f · %s %.2f" % (dw, note, nl, dl, ns, ds), st)
    have = {zone_at(d[2], d[3])["room"] for d in A.DETECTORS if zone_at(d[2], d[3])}
    miss = set(A.DET_ROOMS) - have
    add("ΠΥ-ΧΩΡ", "Πυρανίχνευση", "Κάλυψη χώρων", "ανιχνευτής σε κάθε κύριο χώρο / διάδρομο (λουτρά: όχι καπνού – υδρατμοί)",
        "λείπει: " + ", ".join(sorted(miss)) if miss else A.DET_ROOMS_TXT, "ΑΠΟΚΛΙΣΗ" if miss else "OK")

    # ------------------------------------------------ 5. θυρίδες
    for h in A.HATCHES:
        g = _box(h["rect"])
        probs = []
        if g.intersects(WALLS.buffer(-0.001)):
            probs.append("πάνω σε τοίχο")
        if A.TALL and g.intersects(TALL.buffer(-0.001)):
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
    for c in A.CURTAINS:
        x0, y0, x1, y1 = c["wrect"]
        g = _box(c["rect"])
        vert = (y1 - y0) > (x1 - x0)
        cov = (min(c["rect"][3], y1) - max(c["rect"][1], y0)) if vert else (min(c["rect"][2], x1) - max(c["rect"][0], x0))
        Lw = (y1 - y0) if vert else (x1 - x0)
        full = cov >= Lw - 0.04
        beam_hit = [b[0] for b in A.BEAMS if g.intersection(box(*b[2:])).area > 1e-5]
        zs = [zz for zz in ZONES.values() if zz["geom"].intersects(g) and not zz.get("exposed")]
        depth = min(slab_at(zz, (c["rect"][0] + c["rect"][2]) / 2, (c["rect"][1] + c["rect"][3]) / 2) - zz["level"] for zz in zs) if zs else 0
        probs = []
        if not full: probs.append("καλύπτει %.2f / %.2f" % (cov, Lw))
        if beam_hit: probs.append("δοκός μέσα στην εσοχή: " + ", ".join(beam_hit))
        if depth < c["depth"] - 1e-6: probs.append("βάθος %.2f" % depth)
        add("ΚΡ-%s" % c["id"], "Κουρτίνες", "%s %s – %s · %d × %d cm · οδηγοί %s" % (c["id"], c["win"], c["room"], round(c["width"] * 100),
                                                                              round(c["depth"] * 100), c["rails"]),
            "όλο το άνοιγμα · ανοιχτή ως την πλάκα · καμία δοκός μέσα", "; ".join(probs) if probs else "πλήρης · βάθος %d cm" % round(depth * 100),
            "ΑΠΟΚΛΙΣΗ" if probs else "OK")
    for w_, why in A.NO_CURTAIN.items():
        add("ΚΡ-%s" % w_, "Κουρτίνες", w_, "κουρτινόθηκη όπου απαιτείται", "δεν απαιτείται – " + why, "OK")

    # ------------------------------------------------ 7. αλλαγές στάθμης (προδ. 5, 6)
    levels = sorted({z["level"] for z in A.ZONES})
    for a, why in A.LEVEL_CHANGES:
        add("ΣΘ-" + a.split()[0], "Στάθμες", a, "αλλαγή στάθμης μόνο με λόγο", why, "OK")
    add("ΣΘ-ΣΥΝ", "Στάθμες", "Στάθμες στο διαμέρισμα", "όσο λιγότερες", " · ".join("%+.2f" % l for l in levels) + " (%s)" % A.LEVELS_NOTE, "OK")
    return rows


MODELS = {"gf": "gf_anopsi", "b1": "b1_anopsi", "f4": "f4_anopsi", "s": "s_anopsi"}

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    key = sys.argv[1] if len(sys.argv) > 1 else "b1"
    bind(importlib.import_module(MODELS[key]))
    rows = run()
    from collections import Counter
    for r in rows:
        print("%-10s %-14s %-70s | %-45s | %s" % (r[0], r[5], r[2][:70], r[4][:45], r[1]))
    cnt = Counter(r[5] for r in rows)
    print("\nΣύνολο ελέγχων: %d · " % len(rows) + " · ".join("%s %d" % kv for kv in sorted(cnt.items())))
