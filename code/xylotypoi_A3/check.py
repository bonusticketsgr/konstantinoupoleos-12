"""Έλεγχος πριν από κάθε παραδοτέο:  python3 check.py <φάκελος πηγών>
(α) κάθε διάσταση του μελετητή που ξανασχεδιάζεται πρέπει να έχει μήκος γραμμής = αναγραφόμενη τιμή (± 1,25 cm) και να μη μένει
    διάσταση χωρίς γραμμή· (β) αλυσίδες παρειών: το άθροισμα κάθε εξωτερικής / εσωτερικής αλυσίδας = απόσταση των ακραίων σημείων της και
    κανένα τμήμα μηδενικό ή αρνητικό· (γ) μήκη δοκών (L): τυπώνονται ανά φύλλο, και όπου η δοκός έχει το ίδιο όνομα σε διαδοχικούς
    τυπικούς ορόφους (Σ3–Σ6) το L πρέπει να συμφωνεί (± 2 cm)· (δ) οπές 20 × 20 και shaft του τεύχους αποχετεύσεων: κανένα κουτί δεν κόβει υποστύλωμα / παρειά δοκού («κολλητά» επιτρέπεται)· (ε) ΚΑΛΥΨΗ: κάθε
    ακμή δοκού / πλάκας ≥ 0,45 m δένεται από διάσταση ή είναι η άλλη παρειά δοκού γνωστού πλάτους – αλλιώς μπαίνει συμπληρωματική διάσταση."""
import sys, os, math, re, pymupdf
import xsheet, build

bad_total = 0; LL = {}
for k in build.ORDER:
    cfg = dict(build.SHEETS[k]); page = pymupdf.open(os.path.join(sys.argv[1], cfg["file"]))[0]
    D = xsheet.prep(page, page.get_drawings(), cfg); G = D["G"]
    GC, FC, sides, inner, datum = xsheet.plan_chains(cfg, D)
    clog = []; left = xsheet.cover_dims(D, FC, sides, inner, clog)          # (ε) κάλυψη ακμών + συμπληρωματικές διαστάσεις
    nextra = sum(1 for d in D["dims"] if d.get("extra")); bad_total += len(left)
    bad = [(d["value"], round(math.hypot(d["x1"] - d["x0"], d["y1"] - d["y0"]) / xsheet.S, 3)) for d in D["dims"]
           if abs(math.hypot(d["x1"] - d["x0"], d["y1"] - d["y0"]) / xsheet.S - float(d["value"])) > 0.0125]
    un = [d["value"] for d in D["unres"]]
    bad_total += len(bad) + (0 if cfg.get("hide_unresolved") else len(un))
    print("%-4s διαστάσεις μελετητή %3d | μήκος ≠ τιμή: %s | χωρίς γραμμή: %s | εκτός (μέση υποστυλώματος / μήκη ράβδων): %d"
          % (k, len(D["dims"]) - nextra, bad, un, len(D["dropped"])))
    print("     ΚΑΛΥΨΗ ακμών δοκών / πλακών: συμπληρωματικές διαστάσεις %d | ακάλυπτες ακμές: %d%s" % (nextra, len(left), "  <-- ΛΑΘΟΣ" if left else ""))
    # (β) αλυσίδες
    nch = 0; badch = 0
    if cfg.get("chains", True):
        chains = [[v for v, w in FC[sd]] for sd in sides] + [[p[0] for p in ch["pts"]] for ch in inner]
        for vals in chains:
            nch += 1; seg = [b - a for a, b in zip(vals[:-1], vals[1:])]
            tot = sum(int(math.floor(s_ / xsheet.S * 100 + 0.5 + 1e-9)) for s_ in seg) / 100.0
            if min(seg) <= 0.3 or abs(tot - (vals[-1] - vals[0]) / xsheet.S) > 0.005 * len(seg) + 0.005: badch += 1
    bad_total += badch
    # (γ) μήκη δοκών
    bl = sorted((t["text"], t.get("L")) for t in D["T"] if t["kind"] == "beam" and t.get("L"))
    nol = [t["text"] for t in D["T"] if t["kind"] == "beam" and not t.get("L")]
    for name, L in bl:
        m = re.match(r"^(Δ ?[0-9]+[.][0-9]+)", name)
        if m and k in ("Σ3", "Σ4", "Σ5", "Σ6"): LL.setdefault(m.group(1), {})[k] = L
    # (δ) οπές
    hb = [h["name"] for h in D["holes"] if h["clear"] < 0] + (["S1 shaft"] if (cfg.get("_shaft") or {}).get("cut") else [])
    bad_total += len(hb)
    print("     αλυσίδες %d (λάθος άθροισμα: %d) | δοκοί με L: %d, χωρίς L: %s | οπές %d (κόβουν υποστύλωμα: %s · γραμμή ξυλοτύπου μέσα από το κουτί – να ελεγχθεί: %s)"
          % (nch, badch, len(bl), nol, len(D["holes"]), hb, [h["name"] for h in D["holes"] if h.get("onedge")]))
for name, d in sorted(LL.items()):
    v = list(d.values())
    if max(v) - min(v) > 0.02: print("     ΔΙΑΦΟΡΑ L %s ανά όροφο: %s" % (name, {a: round(b, 2) for a, b in d.items()}))
print("ΣΥΝΟΛΟ ΑΠΟΚΛΙΣΕΩΝ:", bad_total)
