"""Τελικός έλεγχος ΑΝΟΨΕΩΝ πέρα από το checks.py (μοντέλα code/anopseis/*_anopsi.py):
  1 ΔΙΑΣΤΑΣΕΙΣ: κάθε σημείο κάθε αλυσίδας (DIMS_AN01 / 02 / 03) πρέπει να πέφτει πάνω σε πραγματικό στοιχείο δίπλα στην αλυσίδα
    (παρειά τοίχου / υποστυλώματος, ακμή ζώνης, κουρτινόθηκη, ντουλάπα έως οροφή, μονάδα, αεραγωγός, στόμιο, θυρίδα, split, spot,
    κρεμαστό, ανιχνευτής, ράγα, αναμονή) – αλλιώς είναι διάσταση που έμεινε από παλιά έκδοση
  2 ντουλάπες «έως οροφή» / κουζίνα της ανόψης = ντουλάπες / εξοπλισμός των τοιχοποιιών (ίδια ορθογώνια)
  3 η ετικέτα «Βάση» γράφει την τρέχουσα αναθεώρηση των τοιχοποιιών
Χρήση: python3 qa_anopseis.py [gf b1 f4 s]   → κωδικός 1 αν υπάρχει ΛΑΘΟΣ."""
import importlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "anopseis"))
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
MODELS = {"gf": "gf_anopsi", "b1": "b1_anopsi", "f4": "f4_anopsi", "s": "s_anopsi"}
TOL = 0.006          # m
NEAR = 1.50          # πόσο μακριά από το στοιχείο μπορεί να περνά η αλυσίδα
rows = []


def cands(A):
    """(άξονας, συντεταγμένη, lo, hi, όνομα): άξονας 'x' = κατακόρυφη ακμή στο x (lo…hi σε y) · 'y' = οριζόντια ακμή."""
    W = A.W
    out = []

    def rect(r, nm):
        x0, y0, x1, y1 = r
        out.extend([("x", x0, y0, y1, nm), ("x", x1, y0, y1, nm), ("y", y0, x0, x1, nm), ("y", y1, x0, x1, nm)])

    def poly(pts, nm):
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            if abs(ax - bx) < 1e-6:
                out.append(("x", ax, min(ay, by), max(ay, by), nm))
            elif abs(ay - by) < 1e-6:
                out.append(("y", ay, min(ax, bx), max(ax, bx), nm))
            else:   # λοξή / καμπύλη: μόνο τα άκρα
                out.extend([("x", ax, ay, ay, nm), ("y", ay, ax, ax, nm)])

    def pt(x, y, nm):
        out.extend([("x", x, y, y, nm), ("y", y, x, x, nm)])

    for w in W.WALLS: poly(w["pts"], w["id"])
    for i, p in enumerate(W.COLS): poly(p, "σκυρόδεμα")
    for p in W.WINS: poly(p, "κούφωμα")
    for h, l, j in W.DOORS: pt(*h, "πόρτα"); pt(*j, "πόρτα")
    for wd in W.WARDROBES: rect(wd["r"], wd["name"])
    for e in getattr(W, "EQUIP", []): rect(e[1:5], "έπιπλο τοιχοποιιών " + str(e[0]))
    for b in W.BATHS:
        rect(b["counter"], "πάγκος")
        if b.get("shower"): rect(b["shower"], "ντους")
    for z in A.ZONES:
        for r in z["rects"]: rect(r, z["id"])
    for c in A.CURTAINS: rect(c["rect"], c["id"])
    for nm, r in A.TALL: rect(r, nm)
    for u in A.UNITS: rect(u["rect"], u["id"])
    for nm, r in A.DUCTS: rect(r, "αεραγωγός")
    for nm, r in getattr(A, "RETURN_BOX", []): rect(r, "κιβώτιο επιστροφής")
    for d in A.DIFFUSERS: rect(d["rect"], d["id"])
    for h in A.HATCHES: rect(h["rect"], h["id"])
    for u in getattr(A, "SPLITS", []): rect(u["rect"], u["id"])
    for it in getattr(A, "KITCHEN", []): rect(it[1:5], "κουζίνα")
    for r in getattr(A, "UPPER_CAB", []): rect(r, "επάνω ντουλάπια")
    for r in getattr(A, "VOIDS", []): rect(r, "άνοιγμα πλάκας")
    for rh in getattr(A, "ROOF_HATCH", []): rect(rh["rect"], rh["id"])
    for u in getattr(A, "WALL_UNITS", []):
        rect(u["void"], u["id"])
        (fx0, fy), (fx1, _) = u["face"]; pt(fx0, fy, u["id"]); pt(fx1, fy, u["id"])
        if "supply" in u: pt(u["supply"]["x"][0], fy, u["id"]); pt(u["supply"]["x"][1], fy, u["id"])
        if "hatch" in u: pt(u["hatch"]["x"][0], fy, u["id"]); pt(u["hatch"]["x"][1], fy, u["id"])
    for s in A.SPOTS: pt(s[2], s[3], s[0])
    for p in A.PENDANTS: pt(p[1], p[2], p[0])
    for d in A.DETECTORS: pt(d[2], d[3], d[0])
    for l in A.LED: pt(*l[1], l[0]); pt(*l[2], l[0])
    for t in getattr(A, "TRACKS", []): pt(*t["a"], t["id"]); pt(*t["b"], t["id"])
    for w in getattr(A, "WALL_LIGHTS", []): pt(w[2], w[3], w[0])
    for sb in getattr(A, "STUBS", []): pt(*sb["at"], sb["id"])
    for b in A.BEAMS: rect(b[2:], b[0])
    return out


def dims(k, A):
    C = cands(A)
    for nm in ("DIMS_AN01", "DIMS_AN02", "DIMS_AN03", "DIMS_AN05"):
        chains = getattr(A, nm, [])
        bad = []
        n = 0
        for ch in chains:
            o, pos, pts = ch[:3]
            for q in pts:
                n += 1
                ax = "x" if o == "H" else "y"          # οριζόντια αλυσίδα: τα σημεία είναι x → ψάχνω κατακόρυφες ακμές στο x
                hit = [c for c in C if c[0] == ax and abs(c[1] - q) <= TOL and c[2] - NEAR <= pos <= c[3] + NEAR]
                if not hit:
                    far = [c for c in C if c[0] == ax and abs(c[1] - q) <= TOL]
                    bad.append("%s %s σημείο %s%s" % (o, ("%.2f" % pos).replace(".", ","), ("%.3f" % q).rstrip("0").replace(".", ","),
                                                      (" (μόνο μακριά: %s)" % far[0][4]) if far else ""))
        if chains:
            rows.append((k, "Διαστάσεις", "%s – %d αλυσίδες · %d σημεία" % (nm, len(chains), n),
                         "όλα πάνω σε στοιχείο" if not bad else "ΧΩΡΙΣ ΣΤΟΙΧΕΙΟ: " + " · ".join(bad), "OK" if not bad else "ΛΑΘΟΣ"))


def tall(k, A):
    W = A.W
    ref = [tuple(wd["r"]) for wd in W.WARDROBES] + [tuple(e[1:5]) for e in getattr(W, "EQUIP", [])]
    for nm, r in A.TALL:
        if nm.startswith("τοίχος κλιματιστικού"):
            continue
        # ένωση ντουλαπών τοιχοποιιών που καλύπτει το ορθογώνιο
        from shapely.geometry import box
        from shapely.ops import unary_union
        u = unary_union([box(*q) for q in ref]) if ref else None
        g = box(*r)
        miss = g.area - (g.intersection(u).area if u else 0)
        ok = miss <= 0.03 * g.area + 0.005
        if any(s_ in nm for s_ in ("επάνω ντουλάπια",)):      # κρεμαστά: δεν υπάρχουν στην κάτοψη τοιχοποιιών (μόνο ο πάγκος από κάτω)
            ok = True
        rows.append((k, "Ντουλάπες", nm, "= ντουλάπα / εξοπλισμός των τοιχοποιιών" if ok else "ΔΕΝ υπάρχει στις τοιχοποιίες (%.0f %% εκτός) %s" % (100 * miss / g.area, r),
                     "OK" if ok else "ΛΑΘΟΣ"))


def base(k, A):
    W = A.W
    m = re.search(r"τοιχοποιίες[^·]*?(R\d+)", A.BASE_TXT)
    ok = bool(m) and m.group(1) == W.REV
    rows.append((k, "Βάση", A.BASE_TXT, "τοιχοποιίες %s" % W.REV, "OK" if ok else "ΛΑΘΟΣ"))


def run(keys):
    for k in keys:
        A = importlib.import_module(MODELS[k])
        dims(k, A); tall(k, A); base(k, A)
    bad = [r for r in rows if r[4] == "ΛΑΘΟΣ"]
    for r in rows:
        print("%-3s %-6s %-11s %-46s | %s" % (r[0], r[4], r[1], r[2][:46], r[3]))
    print("\nΣύνολο %d έλεγχοι · ΛΑΘΟΣ %d" % (len(rows), len(bad)))
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if run(sys.argv[1:] or list(MODELS)) else 0)
