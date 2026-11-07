"""Ανόψεις οροφής – ενιαίο τεύχος όλων των ορόφων (ισόγειο · Α΄/Β΄/Γ΄ · Δ΄ · σοφίτα), 4 φύλλα A3 ανά όροφο:
ΑΝ στάθμες · κλιματισμός · φωτισμός/πυρανίχνευση · έλεγχος. Το υπόγειο δεν έχει ψευδοροφή (εμφανές σκυρόδεμα).
Χρήση: python3 build_anopseis.py            → ΑΝΟΨΕΙΣ/ΑΝΟΨΕΙΣ_<όροφοι + αναθεωρήσεις>.pdf
       python3 build_anopseis.py f4 out.pdf → μόνο ένας όροφος (gf | b1 | f4 | s)
Πριν από κάθε παραδοτέο: python3 checks.py <όροφος> → 0 ΑΠΟΚΛΙΣΕΙΣ (το build σταματά αν υπάρχει απόκλιση)."""
import importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import checks
import sheets
from draw import new_canvas

ORDER = [("gf", "ΙΣΟΓΕΙΟ"), ("b1", "Β1"), ("f4", "Δ"), ("s", "ΣΟΦΙΤΑ")]
OUTDIR = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΑΝΟΨΕΙΣ")


def models(keys):
    out = []
    for k in keys:
        m = importlib.import_module(checks.MODELS[k])
        sheets.bind(m)
        rows = checks.run()
        bad = [r for r in rows if r[5] == "ΑΠΟΚΛΙΣΗ"]
        if bad:
            for r in bad:
                print("ΑΠΟΚΛΙΣΗ", k, r)
            sys.exit("Υπάρχουν αποκλίσεις στο %s – διόρθωσε το μοντέλο πριν το παραδοτέο." % k)
        out.append((k, m, len(rows)))
    return out


if __name__ == "__main__":
    keys = [sys.argv[1]] if len(sys.argv) > 1 else [k for k, _ in ORDER]
    ms = models(keys)
    if len(sys.argv) > 2:
        out = sys.argv[2]
    else:
        name = "_".join("%s_%s" % (lab, importlib.import_module(checks.MODELS[k]).REV) for k, lab in ORDER if k in keys)
        out = os.path.join(OUTDIR, "ΑΝΟΨΕΙΣ_%s.pdf" % name)
    c = new_canvas(out, "Ανόψεις οροφής – Κωνσταντινουπόλεως 12")
    c.setPageCompression(1)
    n = 0
    for k, m, nrows in ms:
        sheets.bind(m)
        for fn in sheets.SHEETS:
            n += 1
            fn(c, "ΑΝ-%02d" % n); c.showPage()
        print("  %-3s %-45s %d έλεγχοι" % (k, m.SHEET_FLOOR, nrows))
    c.save()
    print("OK", os.path.abspath(out), "· φύλλα", n)
