"""Παραγωγή τεύχους ΙΣΟΓΕΙΟΥ τοιχοποιιών: Τ-01 κάτοψη · Τ-02 είδη · Τ-03 προμέτρηση.
Τα φύλλα (sheet_t0x.py, quantities.py) γράφτηκαν για το b1_model· εδώ το gf_model μπαίνει στη θέση του.
Χρήση: python3 build_gftx.py [out.pdf]"""
import sys, os
import gf_model as G
sys.modules["b1_model"] = G          # τα sheets κάνουν `import b1_model as M` → παίρνουν το μοντέλο ισογείου
from draw import new_canvas
from sheet_t01 import sheet_t01
from sheet_t02 import sheet_t02
from sheet_t03 import sheet_t03

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΤΟΙΧΟΠΟΙΙΕΣ",
    "ΙΣΟΓΕΙΟ_ΤΟΙΧΟΠΟΙΙΕΣ_Τ-01_Τ-03_%s.pdf" % G.REV)
c = new_canvas(OUT, "Ισόγειο Τοιχοποιίες Τ-01/Τ-03 %s" % G.REV)
sheet_t01(c); c.showPage()
sheet_t02(c); c.showPage()
sheet_t03(c); c.showPage()
c.save()
print("OK", os.path.abspath(OUT))
