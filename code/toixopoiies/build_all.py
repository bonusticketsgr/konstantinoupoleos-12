"""ΕΝΙΑΙΟ τεύχος τοιχοποιιών ΙΣΟΓΕΙΟΥ (νησίδα) + Β΄ ΟΡΟΦΟΥ (Β1) – Γιάννης 07/11/2026: «δώσ' μου σε ένα pdf τοιχοποιίες ισογείου και
Β ορόφου (ισόγειο με νησίδα μόνο) … το τελευταίο φύλλο περιεκτικό, τόσα τετραγωνικά τοίχοι σε κάθε όροφο χωριστά».
Φύλλα (07/11 βράδυ): Τ-01 κάτοψη ισογείου · Τ-02 κάτοψη Α΄/Β΄/Γ΄ (Β1) · Τ-03 κάτοψη Δ΄ · Τ-04 κάτοψη σοφίτας · Τ-05 είδη τοιχοποιιών (όλοι οι όροφοι, μία σελίδα) · Τ-06 προμέτρηση ανά όροφο.
R35 (27/11): + Τ-08 τετραγωνικά ΑΝΑ ΤΟΙΧΟ (sheet_walls.py) στο τέλος – ο αριθμός φύλλων (TOTAL) υπολογίζεται από τη σελιδοποίησή του.
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
from sheet_walls import sheet_walls, n_pages


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
# R36 (27/11 βράδυ): ανά όροφο κάτοψη + φύλλα ΧΑΡΑΞΗΣ (τούβλα / γυψοσανίδες – ή ένα κοινό όταν η μία φάση έχει < 3 τοίχους),
# μετά είδη, προμέτρηση, m² ανά τοίχο. Η αρίθμηση των φύλλων και οι παραπομπές υπολογίζονται εδώ.
from sheet_xaraxi import sheet_xaraxi, phases_for
MODELS = [Y, G, B, F, S]
seq = []                                   # [("plan", M) | ("xar", M, phase)]
for M_ in MODELS:
    seq.append(("plan", M_))
    for ph in phases_for(M_):
        seq.append(("xar", M_, ph))
n_plan = len(seq)
TOTAL = n_plan + 3 - 1 + n_pages(MODELS)   # + είδη + προμέτρηση + φύλλα ανά τοίχο
NO = lambda k: "Τ-%02d" % k
sheet_t01.REFS = {"types": NO(n_plan + 1), "qty": NO(n_plan + 2), "walls": NO(n_plan + 3)}
plan_no = {}
for k, item in enumerate(seq, 1):
    if item[0] == "plan":
        use(item[1]); plan_no[id(item[1])] = NO(k); sheet_t01.sheet_t01(c, NO(k), total=TOTAL); c.showPage()
    else:
        use(item[1]); sheet_xaraxi(c, item[1], item[2], NO(k), total=TOTAL, plan_ref=plan_no[id(item[1])]); c.showPage()
DATE_ALL = max((m.DATE for m in MODELS), key=lambda d: d.split("/")[::-1])   # ημερομηνία της νεότερης αναθεώρησης
REVS = "ΥΠ %s · ΙΣ %s · Β1 %s · Δ %s · ΣΟΦ %s" % (Y.REV, G.REV, B.REV, F.REV, S.REV)
PLANS = "%s…%s" % (NO(1), NO(n_plan))
use(B); sheet_t02.sheet_t02_all(c, MODELS, NO(n_plan + 1), REVS, DATE_ALL, total=TOTAL, plans=PLANS); c.showPage()
sheet_t05(c, MODELS, NO(n_plan + 2), REVS, DATE_ALL, total=TOTAL, plans=PLANS, types_no=NO(n_plan + 1)); c.showPage()
sheet_walls(c, MODELS, n_plan + 3, REVS, DATE_ALL, total=TOTAL, plans=PLANS, types_no=NO(n_plan + 1), qty_no=NO(n_plan + 2))
c.save()
print("OK", os.path.abspath(OUT), "φύλλα:", TOTAL)
