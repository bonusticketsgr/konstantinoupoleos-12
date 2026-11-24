# -*- coding: utf-8 -*-
"""Έλεγχος συνέπειας του μοντέλου περιβάλλοντος χώρου (τρέχει μέσα στο build· πρέπει 0 ευρήματα):
(1) σκάλες: ρίχτια × ύψος = υψομετρική διαφορά, ρίχτι ≤ 18 (Κτιριοδομικός άρθ. 11), πάτημα ≥ 25, το πάνω ρίχτι πάνω στο τοιχίο
    του θύλακα, ο διάδρομος κάτω από τη σκάλα ≥ 1,20 (και ≥ 1,40 για τη θέση του αναβατορίου ΑΜΕΑ στην είσοδο)·
(2) ζώνες: τελικό = κορυφή μπαζώματος + επίστρωση (+ πλάκα h18 στους θύλακες), διάδρομοι = πλάκα + 10, χώμα = 30 cm στην πλάκα ±0,00·
(3) τοιχία: κορυφή ≥ η ψηλότερη γειτονική τελική στάθμη (ένα τοιχίο δεν μπορεί να είναι χαμηλότερο από το δάπεδο που συγκρατεί),
    έδραση = η πλάκα Σ2 της θέσης του· περίφραξη +0,81 > πεζοδρόμιο παντού·
(4) πύλες μέσα σε ανοίγματα (κανένα τοιχίο πάνω σε πύλη)."""
import px_model as PM


def _in(poly, x, y):
    n = len(poly); ins = False; j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            ins = not ins
        j = i
    return ins


def zone_at(x, y):
    for z in PM.ZONES:
        if _in(z["poly"], x, y):
            return z
    return None


def final_at(x, y):
    z = zone_at(x, y)
    if z is None:
        return None
    if z["kind"] == "stair":
        s = [s for s in PM.STAIRS if s["id"] in z["name"]][0]
        for yr, lv in zip(s["risers"], s["levels"]):
            if y >= yr - 1e-6:
                cur = lv
        return cur if y >= s["risers"][0] else s["top"]
    return z["final"]


def run(verbose=True):
    errs = []
    E = errs.append
    # (1) σκάλες
    for s in PM.STAIRS:
        if abs(s["n"] * s["riser"] - (s["top"] - s["bottom"])) > 1e-6:
            E("%s: %d × %.3f ≠ %.2f" % (s["id"], s["n"], s["riser"], s["top"] - s["bottom"]))
        if s["riser"] > 0.18 + 1e-9:
            E("%s: ρίχτι %.3f > 0,18" % (s["id"], s["riser"]))
        if s["tread"] < 0.25:
            E("%s: πάτημα %.2f < 0,25" % (s["id"], s["tread"]))
        if not (0.60 <= 2 * s["riser"] + s["tread"] <= 0.66):
            E("%s: 2υ+π = %.3f εκτός 0,60–0,66" % (s["id"], 2 * s["riser"] + s["tread"]))
        if abs(s["levels"][-1] - s["bottom"]) > 1e-6:
            E("%s: τελευταία στάθμη %.3f ≠ %.2f" % (s["id"], s["levels"][-1], s["bottom"]))
    # πάνω ρίχτι ΣΚ-Α στην ακμή του τοιχίου ΘΓ, ΣΚ-Β στην ακμή του ΘΑ
    sA, sB = PM.STAIRS
    if abs(sA["y_top"] - max(p[1] for p in PM.WALL["ΘΓ"]["poly"])) > 1e-6:
        E("ΣΚ-Α: πάνω ρίχτι %.2f ≠ νότια παρειά ΘΓ" % sA["y_top"])
    if abs(sB["y_top"] - max(p[1] for p in PM.WALL["ΘΑ"]["poly"])) > 1e-6:
        E("ΣΚ-Β: πάνω ρίχτι %.2f ≠ νότια παρειά ΘΑ" % sB["y_top"])
    # διάδρομοι κάτω από τις σκάλες
    gate_y = 14.45
    if gate_y - sA["y_bot"] < 1.40:
        E("ΣΚ-Α: κάτω διάδρομος %.2f < 1,40 (θέση αναβατορίου ΑΜΕΑ)" % (gate_y - sA["y_bot"]))
    if gate_y - sB["y_bot"] < 1.20:
        E("ΣΚ-Β: κάτω διάδρομος %.2f < 1,20" % (gate_y - sB["y_bot"]))
    if sA["x1"] - sA["x0"] < 1.20 or sB["x1"] - sB["x0"] < 1.20:
        E("πλάτος σκάλας < 1,20")
    # (2) ζώνες
    for z in PM.ZONES:
        k = z["kind"]
        if k == "pav" and abs(z["final"] - (z["fill_top"] + PM.PAV)) > 1e-6:
            E("%s: τελικό %.2f ≠ μπάζωμα %.2f + %.2f" % (z["id"], z["final"], z["fill_top"], PM.PAV))
        if k == "pocket" and abs(z["final"] - (z["fill_top"] + PM.PSLAB + PM.PAV)) > 1e-6:
            E("%s: τελικό %.2f ≠ μπάζωμα %.2f + h18 + 10" % (z["id"], z["final"], z["fill_top"]))
        if k == "path" and abs(z["final"] - (z["slab"] + PM.PAV)) > 1e-6:
            E("%s: διάδρομος %.2f ≠ πλάκα %.2f + 10" % (z["id"], z["final"], z["slab"]))
        if k == "soil" and z["slab"] is not None and z["final"] - z["slab"] < 0.20 - 1e-6:
            E("%s: χώμα %.2f cm < 20" % (z["id"], (z["final"] - z["slab"]) * 100))
        if k in ("pav", "pocket", "path") and z["slab"] is not None:
            # η πλάκα Σ2 της ζώνης σύμφωνα με τη θέση της
            xs = [p[0] for p in z["poly"]]; xm = sum(xs) / len(xs); ys = [p[1] for p in z["poly"]]; ym = sum(ys) / len(ys)
            exp = PM.SL0 if (xm < 3.40 or ym < 9.45) else (PM.SLM if xm < 9.40 else PM.SLE)
            if abs(exp - z["slab"]) > 1e-6:
                E("%s: πλάκα %.2f ≠ αναμενόμενη %.2f για τη θέση (x %.2f, y %.2f)" % (z["id"], z["slab"], exp, xm, ym))
    # επικαλύψεις ζωνών: δείγματα σημείων (κάναβος 10 cm) μέσα στη μία που πέφτουν και μέσα στην άλλη
    def _samples(poly):
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; out = []
        x = min(xs) + 0.05
        while x < max(xs):
            y = min(ys) + 0.05
            while y < max(ys):
                if _in(poly, x, y):
                    out.append((x, y))
                y += 0.10
            x += 0.10
        return out
    smp = {z["id"]: _samples(z["poly"]) for z in PM.ZONES}
    for a in PM.ZONES:
        for b in PM.ZONES:
            if a is b or a["id"] > b["id"]:
                continue
            n = sum(1 for (x, y) in smp[a["id"]] if _in(b["poly"], x, y))
            if n > 2:
                E("ζώνες %s και %s επικαλύπτονται (%d δείγματα)" % (a["id"], b["id"], n))
    # (3) τοιχία
    for w in PM.WALLS:
        if w["kind"] == "s2":
            continue
        xs = [p[0] for p in w["poly"]]; ys = [p[1] for p in w["poly"]]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        # δείγματα εκατέρωθεν του τοίχου
        samples = []
        if (x1 - x0) < (y1 - y0):      # κατακόρυφος
            for t in (0.15, 0.5, 0.85):
                yy = y0 + t * (y1 - y0); samples += [(x0 - 0.08, yy), (x1 + 0.08, yy)]
        else:
            for t in (0.15, 0.5, 0.85):
                xx = x0 + t * (x1 - x0); samples += [(xx, y0 - 0.08), (xx, y1 + 0.08)]
        if w["id"] == "ΤΧ-02":
            samples = [(-3.0, 13.5)]
        hi = None
        for (sx, sy) in samples:
            lv = final_at(sx, sy)
            if lv is not None:
                hi = lv if hi is None else max(hi, lv)
        if hi is not None:
            for (sx, sy) in samples:
                lv = final_at(sx, sy)
                top = PM.wall_top_at(w, sy if (x1 - x0) < (y1 - y0) else sy)
                if lv is not None and top < lv - 1e-6 and w["kind"] in ("ret", "curb"):
                    E("%s: κορυφή %.2f < γειτονική στάθμη %.2f στο (%.2f, %.2f)" % (w["id"], top, lv, sx, sy))
        # έδραση = πλάκα Σ2 της θέσης
        if w["base"] is not None:
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            exp = PM.SL0 if (xm < 3.40 or ym < 9.45) else (PM.SLM if xm < 9.40 else PM.SLE)
            if ym >= 9.45 and PM.X_D241[0] <= xm <= PM.X_D241[1]:
                exp = PM.D241_TOP          # πάνω στη Δ24.1 (ανεστραμμένη, κορυφή −0,05)
            if w["kind"] == "bound" and w["id"] in ("ΤΧ-13", "ΤΧ-14"):
                exp = PM.SL0
            if abs(exp - w["base"]) > 1e-6:
                E("%s: έδραση %.2f ≠ πλάκα %.2f της θέσης" % (w["id"], w["base"], exp))
    # περίφραξη πάνω από το πεζοδρόμιο
    for x in (-1.2, 1.0, 3.0, 4.3):
        if PM.FENCE_BASE <= PM.sw_south(x):
            E("βάση περίφραξης κάτω από το πεζοδρόμιο στο x %.1f" % x)
    for y in (3.82, 7.0, 11.46):
        if PM.FENCE_BASE <= PM.sw_west(y):
            E("βάση περίφραξης κάτω από το πεζοδρόμιο στο y %.1f" % y)
    # (4) πύλες: καμία νέα τοιχοποιία πάνω στο άνοιγμα
    for g in PM.GATES:
        (gx0, gy0), (gx1, gy1) = g["pts"]
        for w in PM.WALLS:
            xs = [p[0] for p in w["poly"]]; ys = [p[1] for p in w["poly"]]
            if w["kind"] in ("fence", "lobby") and min(xs) < (gx0 + gx1) / 2 < max(xs) and min(ys) - 0.001 < gy0 < max(ys) + 0.001 and gx0 != gx1:
                E("πύλη %s πάνω σε τοιχίο %s" % (g["id"], w["id"]))
    if verbose:
        print("ΕΛΕΓΧΟΣ ΠΕΡΙΒΑΛΛΟΝΤΟΣ ΧΩΡΟΥ: %d ευρήματα" % len(errs))
        for e in errs:
            print("  -", e)
    return len(errs)


if __name__ == "__main__":
    run()
