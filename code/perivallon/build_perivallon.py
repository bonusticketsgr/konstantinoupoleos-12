# -*- coding: utf-8 -*-
"""ΠΕΡΙΒΑΛΛΩΝ ΧΩΡΟΣ ΙΣΟΓΕΙΟΥ – τεύχος 4 φύλλων A3: ΠΧ-01 κάτοψη 1:80 · ΠΧ-02 τομές Α-Α/Β-Β/ΣΤ-ΣΤ/Γ-Γ 1:50 · ΠΧ-03 τομές Δ-Δ/Ε-Ε +
λεπτομέρειες σκαλών 1:25 · ΠΧ-04 πίνακες. Χρήση: python3 build_perivallon.py [out.pdf]  (τρέχει πρώτα τον έλεγχο px_check.py)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import px_model as PM
import px_check
from draw import new_canvas
import px_sheets, px_sections, px_tables

n_err = px_check.run()
if n_err:
    sys.exit("ΕΛΕΓΧΟΣ: %d ευρήματα – δεν χτίζεται το τεύχος" % n_err)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΠΕΡΙΒΑΛΛΩΝ_ΧΩΡΟΣ",
                                                           "ΠΕΡΙΒΑΛΛΩΝ_ΧΩΡΟΣ_ΙΣΟΓΕΙΟΥ_%s.pdf" % PM.REV)
c = new_canvas(OUT, "Περιβάλλων χώρος ισογείου %s – διαμόρφωση, τοιχία, μπαζώματα, σκάλες" % PM.REV)
c.setPageCompression(1)
px_sheets.sheet_plan(c, "ΠΧ-01"); c.showPage()
px_sections.sheet_sections_1(c, "ΠΧ-02"); c.showPage()
px_sections.sheet_sections_2(c, "ΠΧ-03"); c.showPage()
px_tables.sheet_tables(c, "ΠΧ-04"); c.showPage()
c.save()
print("OK →", os.path.abspath(OUT))
