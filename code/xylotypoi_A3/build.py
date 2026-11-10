"""Ξυλότυποι εργοταξίου Α3 (χωρίς οπλισμούς) από τους ξυλοτύπους εφαρμογής Σ1–Σ7_ΕΦ και Σ8 του μελετητή (Fespa, 1:50).

    python3 build.py <φάκελος με S1_EF.pdf … S7_EF.pdf, S8.pdf> [Σ4 Σ5 …]

Παράγει ένα PDF ανά φύλλο + ενιαίο τεύχος (Σ2–Σ8) στο ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ/ΞΥΛΟΤΥΠΟΙ/ΕΡΓΟΤΑΞΙΟΥ_A3/ και PNG ελέγχου στο <φάκελος>/../out.
Οι περιοχές (region) είναι σε pt του αρχικού PDF."""
import sys, os, pymupdf
import xsheet

REV, DATE = "R02", "10/11/2026"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΞΥΛΟΤΥΠΟΙ", "ΕΡΓΟΤΑΞΙΟΥ_A3")
SIFONI = "Πρόβολοι: υποδοχή σιφωνιού και υδρορροή ΠΡΙΝ το μπετό, να μην κοπεί οπλισμός (μελετητής)."
STAIRW = "Διαγραμμισμένο τοιχείο δίπλα στη σκάλα (0,60): έως το ύψος της σκάλας (μελετητής)."

# ΟΠΕΣ ΠΛΑΚΩΝ αποχέτευσης / υδρορροών: holes="Σ2" … → πίνακας HOLES του τεύχους αποχετεύσεων R19 (holes_r19.py = αντίγραφο του
# code/apoxeteuseis/apox_r19.py, branch apoxeteuseis-r14). Το R01 είχε πάρει ΛΑΘΟΣ τις θέσεις του παλιού R12 – διορθώθηκε στο R02.
SEC = dict(sections=True, cuts=True, strip_w=38)
LEG_F = [("Κ1 30/70", "υποστύλωμα / τοιχείο – διατομή σε cm"), ("Δ1.1 30/40", "δοκός – πλάτος / ύψος σε cm"), ("Π1  h=15", "πλάκα – πάχος σε cm"),
         ("Σ.Μ.", "στάθμη μπετόν (m)"), ("Α.Δ.Σ.Ε.", "ανώτατη δυνατή στάθμη εκσκαφής (m)"), ("- - -", "κρυφή ακμή / στοιχείο από κάτω")]
SHEETS = {
    "Σ1": dict(file="S1_EF.pdf", region=(455, 425, 1990, 1590), dim_touch="strict", chain_sides=("bottom", "left"), chain_tol=8.0, inner_names=r"^Κ([1-9]|10)\s",
               hide_unresolved=True,
               number="Σ1", title=["ΞΥΛΟΤΥΠΟΣ", "ΘΕΜΕΛΙΩΣΗΣ"], level_table=False, level_txt="-4,00 / -3,60",
               legend=LEG_F, notes=["Η θεμελίωση του υποσταθμού (-6,69) στο φύλλο Σ1α.", "Βόρεια και ανατολική πλευρά λοξές (όριο οικοπέδου): ισχύουν οι διαστάσεις του μελετητή κατά μήκος τους."],
               base="Σ1_ΕΦ.pdf – ξυλότυπος θεμελίωσης, Γ. Κόγιας (Drive 19/10/2026).", out="Σ1_Θεμελίωση"),
    "Σ1α": dict(file="S1_EF.pdf", region=(2330, 880, 2790, 1560), dim_touch="strict", chains=False,
               number="Σ1α", title=["ΘΕΜΕΛΙΩΣΗ", "ΥΠΟΣΤΑΘΜΟΥ"], level_table=False, level_txt="-6,69 / -6,24",
               legend=LEG_F, base="Σ1_ΕΦ.pdf – ξυλότυπος θεμελίωσης υποσταθμού, Γ. Κόγιας (Drive 19/10/2026).", out="Σ1α_Θεμελίωση_υποσταθμού"),
    "Σ2": dict(file="S2_EF.pdf", region=(790, 455, 2295, 1590), chain_sides=("bottom",), chain_tol=8.0, inner_names=r"^Κ([1-9]|10)\s",
               exclude=[(690, 1500, 840, 1545)], hide_unresolved=True, move=[("Κ1 30/70", -52, 30)],
               retext=[("19", None), ("h=18 cm. Οπλισμός", None), ("ζόλ h=18 cm. Οπλι-", None), ("Πλάκα επί του φελιζόλ", None), ("Γέμισμα μέχρι", None), ("τη στ. +0,30", None), ("Πλάκα επί του φελι-", None)],
               # «φελιζόλ» του μελετητή = ΜΠΑΖΩΜΑ (Γιάννης 10/11/2026)· ο χώρος οριοθετείται από τη δοκό και τα κρυφά τοιχία (εσωτερικές παρειές)
               fills=[dict(poly=[(1395.8, 1153.7), (1690.6, 1153.7), (1690.6, 1190.6), (1568.7, 1190.6), (1568.7, 1247.3), (1395.8, 1247.3)], label=["ΜΠΑΖΩΜΑ", "+ πλάκα h=18 από πάνω"], at=(1625, 1172)),
                      dict(poly=[(1753.0, 1153.8), (1891.2, 1153.8), (1891.2, 1232.6), (1753.0, 1232.6)], label=["ΜΠΑΖΩΜΑ", "+ πλάκα h=18"], at=(1838, 1200))],
               fill_label="ΓΕΜΙΣΜΑ έως +0,30", fill_legend="γέμισμα έως τη στάθμη +0,30 (πλάκα ±0,00)", holes="Σ2",
               number="Σ2", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ"], level_table=False, level_txt="±0,00 / +0,30",
               notes=["Β και Α πλευρά λοξές (όριο οικοπέδου): ισχύουν οι διαστάσεις του μελετητή κατά μήκος τους."],
               base="Σ2_ΕΦ.pdf – ξυλότυπος οροφής υπογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ2_Οροφή_υπογείου"),
    "Σ3": dict(file="S3_EF.pdf", region=(700, 480, 1720, 1300), stairs=[(1480, 870, 1640, 1040)], skip_dims=[(797, 555), (1279, 1254), (752, 466)], chain_sides=("top", "bottom", "right"),
               sections=True, cuts=True, strip_w=35, pad=4, holes="Σ3",
               number="Σ3", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΙΣΟΓΕΙΟΥ"], level=3.65, level_txt="+3,65",
               notes=[SIFONI, STAIRW, "Φυτευτά Κ23–Κ25 και τοιχεία εισόδου: φύλλο Σ3α."],
               base="Σ3_ΕΦ.pdf – ξυλότυπος οροφής ισογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ3_Οροφή_ισογείου_+3.65"),
    "Σ3α": dict(file="S3_EF.pdf", region=(490, 455, 1760, 1500), stairs=[(1480, 870, 1640, 1040)], exclude=[(380, 1340, 940, 1500)], chains=False,
               manual_dims=[(502.0, 499.5, 502.0, 798.3, "5.27", 500.3, 649.1)],
               number="Σ3α", title=["ΟΡΟΦΗ ΙΣΟΓΕΙΟΥ –", "ΓΕΝΙΚΗ ΔΙΑΤΑΞΗ ΜΕ", "ΤΑ ΦΥΤΕΥΤΑ"], level=3.65, level_txt="+3,65", level_table=False,
               notes=["Γενική κάτοψη με τα φυτευτά: Κ23–Κ25 (δυτικά), τοιχεία εισόδου (νότια). Μεγαλύτερη κλίμακα: Σ3."], beam_len=False,
               base="Σ3_ΕΦ.pdf – ξυλότυπος οροφής ισογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ3α_Οροφή_ισογείου_γενική_φυτευτά"),
    "Σ4": dict(file="S4_EF.pdf", region=(400, 680, 1380, 1560), stairs=[(1150, 1040, 1300, 1200)], exclude=[(1335, 680, 1380, 735)], holes="Σ4", **SEC,
               number="Σ4", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Α΄ ΟΡΟΦΟΥ"], level=6.75, level_below=3.65, level_txt="+6,75",
               # Γιάννης 10/11/2026: «Σ4 – Τομή 2-2: η μετόπη από +6,45 έως +6,95, ώστε όπως στο Σ5 να προκύπτει προβολή ύψους 50 cm στην όψη»
               # (ο μελετητής στο Σ4_ΕΦ: +6,45 … +6,90 = 45 cm). Αλλάζει η στάθμη στέψης στην τομή και στην κάτοψη (μπλε).
               sec_retext={"2-2": [("+6,90", "+6,95", "level")]}, retext=[("+6,90", "+6,95", "level")],
               notes=["ΤΟΜΗ 2-2: μετόπη +6,45 έως +6,95 (ύψος 0,50 όπως Σ5) – αλλαγή 10/11/2026· ο μελετητής είχε +6,90. Να ενημερωθεί ο στατικός.", SIFONI, STAIRW],
               base="Σ4_ΕΦ.pdf – ξυλότυπος οροφής Α΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ4_Οροφή_Α_ορόφου_+6.75"),
    "Σ5": dict(file="S5_EF.pdf", region=(380, 685, 1345, 1510), stairs=[(1120, 1040, 1280, 1200)], holes="Σ5", **SEC,
               number="Σ5", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Β΄ ΟΡΟΦΟΥ"], level=9.85, level_below=6.75, level_txt="+9,85", notes=[SIFONI, STAIRW],
               base="Σ5_ΕΦ.pdf – ξυλότυπος οροφής Β΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ5_Οροφή_Β_ορόφου_+9.85"),
    "Σ6": dict(file="S6_EF.pdf", region=(335, 685, 1330, 1510), stairs=[(1120, 1040, 1280, 1200)], pad=3, sections=True, cuts=True, strip_w=36, holes="Σ6",
               number="Σ6", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Γ΄ ΟΡΟΦΟΥ"], level=12.95, level_below=9.85, level_txt="+12,95", notes=[SIFONI, STAIRW],
               base="Σ6_ΕΦ.pdf – ξυλότυπος οροφής Γ΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ6_Οροφή_Γ_ορόφου_+12.95"),
    "Σ7": dict(file="S7_EF.pdf", region=(265, 795, 1235, 1580), stairs=[(1000, 1150, 1160, 1320)], title_w=55,
               number="Σ7", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Δ΄ ΟΡΟΦΟΥ"], level=16.05, level_below=12.95, level_txt="+16,05", notes=[SIFONI], holes="Σ7", fill_label="ΓΕΜΙΣΜΑ έως +16,40", fill_legend="γέμισμα έως τη στάθμη +16,40",
               insets=[dict(region=(1235, 1130, 1480, 1380), title=["ΛΕΠΤΟΜΕΡΕΙΑ ΜΕΛΕΤΗΤΗ", "πλάκα στη στάθμη +17,36"], chains=False)],
               base="Σ7_ΕΦ.pdf – ξυλότυπος οροφής Δ΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ7_Οροφή_Δ_ορόφου_+16.05"),
    "Σ8": dict(file="S8.pdf", region=(470, 775, 1345, 1510), chain_round=True, holes="Σ8",
               number="Σ8", title=["ΞΥΛΟΤΥΠΟΣ ΣΟΦΙΤΑΣ", "(ΣΤΕΓΗ)"], level_table=False, level_txt="+18,49 έως +19,72", notes=[SIFONI, "Στέγη κεκλιμένη: στάθμες (μπλε) στις τομές επί τόπου. «Ανεστρ.» = ανεστραμμένη δοκός."],
               base="Σ8.pdf – ξυλότυπος σοφίτας, Γ. Κόγιας (οριστική μελέτη 02/2026, Drive 06/11/2026).", out="Σ8_Στέγη_σοφίτας"),
}
# R01: ο Γιάννης δεν χρειάζεται τον Σ1 (θεμελίωση) – οι ρυθμίσεις Σ1 / Σ1α μένουν, δεν τυπώνονται (python3 build.py <πηγές> Σ1 για να βγουν)
ORDER = ["Σ2", "Σ3", "Σ3α", "Σ4", "Σ5", "Σ6", "Σ7", "Σ8"]


def main():
    src = sys.argv[1]; which = sys.argv[2:] or ORDER
    os.makedirs(OUT, exist_ok=True)
    prev = os.path.join(src, "..", "out"); os.makedirs(prev, exist_ok=True)
    for k in which:
        cfg = dict(SHEETS[k]); cfg["pdf"] = os.path.join(src, cfg["file"]); cfg["rev"] = REV
        sh, info = xsheet.build(cfg, None, DATE)
        name = "%s_A3_1-%d_%s.pdf" % (cfg["out"], info["scale"], REV)
        for f in os.listdir(OUT):
            if f.startswith(cfg["out"] + "_A3_") and f.endswith(".pdf"): os.remove(os.path.join(OUT, f))
        path = os.path.join(OUT, name)
        sh.flush(); sh.doc.set_metadata(dict(title="%s – %s (ξυλότυπος εργοταξίου)" % (k, " ".join(cfg["title"])), author="ARKAD Ι.Κ.Ε."))
        sh.doc.save(path, garbage=4, deflate=True)
        pymupdf.open(path)[0].get_pixmap(dpi=130).save(os.path.join(prev, k + ".png"))
        print("==", k, "1:%d" % info["scale"], info["layout"], "dims", len(info["dims"]), "->", name)
        for l in info["log"]: print("   ", l)
    # ενιαίο τεύχος
    if not sys.argv[2:]:
        book = pymupdf.open()
        for k in ORDER:
            fs = [f for f in os.listdir(OUT) if f.startswith(SHEETS[k]["out"] + "_A3_")]
            if fs: book.insert_pdf(pymupdf.open(os.path.join(OUT, fs[0])))
        book.save(os.path.join(OUT, "..", "ΞΥΛΟΤΥΠΟΙ_ΕΡΓΟΤΑΞΙΟΥ_Σ2-Σ8_A3_%s.pdf" % REV), garbage=4, deflate=True)


if __name__ == "__main__":
    main()
