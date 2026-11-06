"""ΕΝΙΑΙΟ τεύχος τοιχοποιιών ΙΣΟΓΕΙΟΥ (νησίδα) + Β΄ ΟΡΟΦΟΥ (Β1) – Γιάννης 07/11/2026: «δώσ' μου σε ένα pdf τοιχοποιίες ισογείου και
Β ορόφου (ισόγειο με νησίδα μόνο) … το τελευταίο φύλλο περιεκτικό, τόσα τετραγωνικά τοίχοι σε κάθε όροφο χωριστά».
Φύλλα: Τ-01 κάτοψη ισογείου · Τ-02 είδη ισογείου · Τ-03 κάτοψη Β1 · Τ-04 είδη Β1 · Τ-05 κάτοψη σοφίτας · Τ-06 είδη σοφίτας · Τ-07 προμέτρηση ανά όροφο (07/11: + σοφίτα).
(Το φύλλο περιβάλλοντος χώρου 1:100 του ισογείου δεν τυπώνεται πια.)
Χρήση: python3 build_all.py [out.pdf]"""
import sys, os
import b1_model as B
import gf_model as G
import s_model as S
from draw import new_canvas
import sheet_t01, sheet_t02, quantities
from sheet_t05 import sheet_t05


def use(model):
    """Τα φύλλα γράφτηκαν με `import b1_model as M` – εδώ αλλάζει το μοντέλο ανά φύλλο."""
    for mod in (sheet_t01, sheet_t02, quantities):
        mod.M = model
    sheet_t01.OX, sheet_t01.OY = getattr(model, "OX", 309.5), getattr(model, "OY", 99.8)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΤΟΙΧΟΠΟΙΙΕΣ",
    "ΤΟΙΧΟΠΟΙΙΕΣ_ΙΣΟΓΕΙΟ_%s_Β1_%s_ΣΟΦΙΤΑ_%s.pdf" % (G.REV, B.REV, S.REV))
c = new_canvas(OUT, "Τοιχοποιίες ισογείου %s + Β1 %s + σοφίτας %s" % (G.REV, B.REV, S.REV))
c.setPageCompression(1)
use(G)
sheet_t01.sheet_t01(c, "Τ-01"); c.showPage()
sheet_t02.sheet_t02(c, "Τ-02"); c.showPage()
use(B)
sheet_t01.sheet_t01(c, "Τ-03"); c.showPage()
sheet_t02.sheet_t02(c, "Τ-04"); c.showPage()
use(S)
sheet_t01.sheet_t01(c, "Τ-05"); c.showPage()
sheet_t02.sheet_t02(c, "Τ-06"); c.showPage()
sheet_t05(c, [G, B, S], "Τ-07", "ΙΣ %s · Β1 %s · ΣΟΦ %s" % (G.REV, B.REV, S.REV), G.DATE); c.showPage()
c.save()
print("OK", os.path.abspath(OUT))
