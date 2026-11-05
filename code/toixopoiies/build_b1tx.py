"""Παραγωγή τεύχους Β1 τοιχοποιιών: Τ-01 κάτοψη · Τ-02 είδη · Τ-03 προμέτρηση.
Χρήση: python3 build_b1tx.py [out.pdf]
"""
import sys, os
import b1_model as M
from draw import new_canvas
from sheet_t01 import sheet_t01
from sheet_t01a import sheet_t01a
from sheet_t02 import sheet_t02
from sheet_t03 import sheet_t03

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΤΟΙΧΟΠΟΙΙΕΣ",
    "Β1_ΤΟΙΧΟΠΟΙΙΕΣ_Τ-01_Τ-03_%s.pdf" % M.REV)

c = new_canvas(OUT, "Β1 Τοιχοποιίες Τ-01/Τ-03 %s" % M.REV)
sheet_t01(c); c.showPage()
sheet_t01a(c); c.showPage()
sheet_t02(c); c.showPage()
sheet_t03(c); c.showPage()
c.save()
print("OK", os.path.abspath(OUT))
