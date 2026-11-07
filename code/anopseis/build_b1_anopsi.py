"""Ανόψη οροφής Β1 (Α΄ · Β΄ · Γ΄ όροφος) – 4 φύλλα A3: ΑΝ-01 στάθμες · ΑΝ-02 κλιματισμός · ΑΝ-03 φωτισμός/πυρανίχνευση · ΑΝ-04 έλεγχος.
Χρήση: python3 build_b1_anopsi.py [out.pdf]   (πρώτα: python3 checks.py → 0 ΑΠΟΚΛΙΣΕΙΣ)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b1_anopsi as A
import checks
from draw import new_canvas
import sheets

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
for fn in (sheets.sheet_an01, sheets.sheet_an02, sheets.sheet_an03, sheets.sheet_an04):
    fn(c); c.showPage()
c.save()
print("OK", os.path.abspath(OUT), "· έλεγχοι", len(rows))
