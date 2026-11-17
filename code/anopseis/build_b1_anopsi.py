"""Ανόψη οροφής Β1 (Α΄ · Β΄ · Γ΄ όροφος) – 4 φύλλα A3: ΑΝ-01 στάθμες · ΑΝ-02 κλιματισμός · ΑΝ-03 φωτισμός/πυρανίχνευση · ΑΝ-04 έλεγχος.
Χρήση: python3 build_b1_anopsi.py [out.pdf]   (πρώτα: python3 checks.py b1 → 0 ΑΠΟΚΛΙΣΕΙΣ)
Το ενιαίο τεύχος όλων των ορόφων: build_anopseis.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b1_anopsi as A
import checks
from draw import new_canvas
import sheets

sheets.bind(A)
rows = checks.run()
bad = [r for r in rows if r[5] == "ΑΠΟΚΛΙΣΗ"]
if bad:
    for r in bad:
        print("ΑΠΟΚΛΙΣΗ", r)
    sys.exit("Υπάρχουν αποκλίσεις – διόρθωσε το μοντέλο πριν το παραδοτέο.")

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΑΝΟΨΕΙΣ", "ΑΝΟΨΗ_ΟΡΟΦΗΣ_Α_Β_Γ_ΟΡΟΦΟΥ_Β1_%s.pdf" % A.REV)
c = new_canvas(OUT, "Ανόψη οροφής Β1 – Α΄ · Β΄ · Γ΄ όροφος (%s)" % A.REV)
c.setPageCompression(1)
for i, fn in enumerate(sheets.SHEETS):
    fn(c, "ΑΝ-%02d" % (i + 1)); c.showPage()
c.save()
print("OK", os.path.abspath(OUT), "· έλεγχοι", len(rows))
