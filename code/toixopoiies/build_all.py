"""ΕΝΙΑΙΟ τεύχος τοιχοποιιών ΙΣΟΓΕΙΟΥ (νησίδα) + Β΄ ΟΡΟΦΟΥ (Β1) – Γιάννης 07/11/2026: «δώσ' μου σε ένα pdf τοιχοποιίες ισογείου και
Β ορόφου (ισόγειο με νησίδα μόνο) … το τελευταίο φύλλο περιεκτικό, τόσα τετραγωνικά τοίχοι σε κάθε όροφο χωριστά».
Φύλλα (07/11 βράδυ): Τ-01 κάτοψη ισογείου · Τ-02 κάτοψη Α΄/Β΄/Γ΄ (Β1) · Τ-03 κάτοψη Δ΄ · Τ-04 κάτοψη σοφίτας · Τ-05 είδη τοιχοποιιών (όλοι οι όροφοι, μία σελίδα) · Τ-06 προμέτρηση ανά όροφο.
(Το φύλλο περιβάλλοντος χώρου 1:100 του ισογείου δεν τυπώνεται πια.)
Χρήση: python3 build_all.py [out.pdf]"""
import sys, os
import b1_model as B
import gf_model as G
import s_model as S
import f4_model as F
import b_model as Y
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
    "ΤΟΙΧΟΠΟΙΙΕΣ_ΥΠΟΓΕΙΟ_%s_ΙΣΟΓΕΙΟ_%s_Β1_%s_Δ_%s_ΣΟΦΙΤΑ_%s.pdf" % (Y.REV, G.REV, B.REV, F.REV, S.REV))
c = new_canvas(OUT, "Τοιχοποιίες υπογείου %s + ισογείου %s + Β1 %s + Δ΄ %s + σοφίτας %s" % (Y.REV, G.REV, B.REV, F.REV, S.REV))
c.setPageCompression(1)
# R25 / Δ R02 (Γιάννης 07/11): «κατόψεις στις πρώτες σελίδες, μετά είδη τοιχοποιιών μία σελίδα και μετά η προμέτρηση»
# 07/11 βράδυ: + ΥΠΟΓΕΙΟ (b_model) ως πρώτο φύλλο
use(Y); sheet_t01.sheet_t01(c, "Τ-01"); c.showPage()
use(G); sheet_t01.sheet_t01(c, "Τ-02"); c.showPage()
use(B); sheet_t01.sheet_t01(c, "Τ-03"); c.showPage()
use(F); sheet_t01.sheet_t01(c, "Τ-04"); c.showPage()
use(S); sheet_t01.sheet_t01(c, "Τ-05"); c.showPage()
DATE_ALL = max((m.DATE for m in (Y, G, B, F, S)), key=lambda d: d.split("/")[::-1])   # ημερομηνία της νεότερης αναθεώρησης
REVS = "ΥΠ %s · ΙΣ %s · Β1 %s · Δ %s · ΣΟΦ %s" % (Y.REV, G.REV, B.REV, F.REV, S.REV)
use(B); sheet_t02.sheet_t02_all(c, [Y, G, B, F, S], "Τ-06", REVS, DATE_ALL); c.showPage()
sheet_t05(c, [Y, G, B, F, S], "Τ-07", REVS, DATE_ALL); c.showPage()
c.save()
print("OK", os.path.abspath(OUT))
