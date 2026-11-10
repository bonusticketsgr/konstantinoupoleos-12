"""Έλεγχος πριν από κάθε παραδοτέο:  python3 check.py <φάκελος πηγών>
Για κάθε φύλλο: κάθε διάσταση του μελετητή που ξανασχεδιάζεται πρέπει να έχει μήκος γραμμής = αναγραφόμενη τιμή (± 1,25 cm)
και δεν πρέπει να μένει διάσταση χωρίς γραμμή («αναπάντητες»)."""
import sys, os, math, pymupdf
import xsheet, build

bad_total = 0
for k in build.ORDER:
    cfg = dict(build.SHEETS[k]); page = pymupdf.open(os.path.join(sys.argv[1], cfg["file"]))[0]
    D = xsheet.prep(page, page.get_drawings(), cfg)
    bad = [(d["value"], round(math.hypot(d["x1"] - d["x0"], d["y1"] - d["y0"]) / xsheet.S, 3)) for d in D["dims"]
           if abs(math.hypot(d["x1"] - d["x0"], d["y1"] - d["y0"]) / xsheet.S - float(d["value"])) > 0.0125]
    un = [d["value"] for d in D["unres"]]
    bad_total += len(bad) + (0 if cfg.get("hide_unresolved") else len(un))
    print("%-4s διαστάσεις μελετητή %3d | μήκος ≠ τιμή: %s | χωρίς γραμμή: %s | εκτός (μέση υποστυλώματος / μήκη ράβδων): %d"
          % (k, len(D["dims"]), bad, un, len(D["dropped"])))
print("ΣΥΝΟΛΟ ΑΠΟΚΛΙΣΕΩΝ:", bad_total)
