"""Ξυλότυποι εργοταξίου Α3 (χωρίς οπλισμούς) από τους ξυλοτύπους εφαρμογής Σ1–Σ7_ΕΦ και Σ8 του μελετητή (Fespa, 1:50).

    python3 build.py <φάκελος με S1_EF.pdf … S7_EF.pdf, S8.pdf> [Σ4 Σ5 …]

Παράγει ένα PDF ανά φύλλο + ενιαίο τεύχος στο ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ/ΞΥΛΟΤΥΠΟΙ/ΕΡΓΟΤΑΞΙΟΥ_A3/ και PNG ελέγχου στο <φάκελος>/../out.
Οι περιοχές (region) είναι σε pt του αρχικού PDF."""
import sys, os, pymupdf
import xsheet

REV, DATE = "R00", "10/11/2026"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΞΥΛΟΤΥΠΟΙ", "ΕΡΓΟΤΑΞΙΟΥ_A3")
SIFONI = "Στις Ε.Ζ. των προβόλων: η υποδοχή για το σιφώνι και η υδρορροή να προβλεφθούν ΠΡΙΝ τη σκυροδέτηση, για να μην κόψει ο υδραυλικός τον οπλισμό της Ε.Ζ. (σημείωση μελετητή)."
STAIRW = "Το διαγραμμισμένο τοιχείο δίπλα στη σκάλα (διάσταση 0,60) φτάνει έως το ύψος της σκάλας, για στήριξή της (σημείωση μελετητή)."

SEC = dict(sections=True, cuts=True, strip_w=38, title_w=60)
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
    "Σ2": dict(file="S2_EF.pdf", region=(790, 455, 2295, 1590), chain_sides=("bottom", "left"), chain_tol=8.0, inner_names=r"^Κ([1-9]|10)\s",
               exclude=[(690, 1500, 840, 1545)], hide_unresolved=True, move=[("Κ1 30/70", -52, 30)],
               retext=[("19", None), ("h=18 cm. Οπλισμός", "h=18 cm."), ("ζόλ h=18 cm. Οπλι-", "ζόλ h=18 cm.")],
               number="Σ2", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ"], level_table=False, level_txt="±0,00 / +0,30",
               notes=["Διαγραμμισμένες ζώνες: γέμισμα μέχρι τη στάθμη +0,30 (όπως γράφει ο μελετητής).", "Βόρεια και ανατολική πλευρά λοξές (όριο οικοπέδου): ισχύουν οι διαστάσεις του μελετητή κατά μήκος τους."],
               base="Σ2_ΕΦ.pdf – ξυλότυπος οροφής υπογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ2_Οροφή_υπογείου"),
    "Σ3": dict(file="S3_EF.pdf", region=(700, 480, 1720, 1300), stairs=[(1480, 870, 1640, 1040)], skip_dims=[(797, 555), (1279, 1254), (752, 466)], chain_sides=("top", "bottom", "right"),
               sections=True, cuts=True, strip_w=35, title_w=59, pad=4,
               number="Σ3", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΙΣΟΓΕΙΟΥ"], level=3.65, level_txt="+3,65",
               notes=[SIFONI, STAIRW, "Τα φυτευτά Κ23–Κ25 και τα φυτευτά τοιχεία της εισόδου (εκτός κάτοψης) στο φύλλο Σ3α."],
               base="Σ3_ΕΦ.pdf – ξυλότυπος οροφής ισογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ3_Οροφή_ισογείου_+3.65"),
    "Σ3α": dict(file="S3_EF.pdf", region=(490, 455, 1760, 1500), stairs=[(1480, 870, 1640, 1040)], exclude=[(380, 1340, 940, 1500)], chains=False,
               manual_dims=[(502.0, 499.5, 502.0, 798.3, "5.27", 500.3, 649.1)],
               number="Σ3α", title=["ΟΡΟΦΗ ΙΣΟΓΕΙΟΥ –", "ΓΕΝΙΚΗ ΔΙΑΤΑΞΗ ΜΕ", "ΤΑ ΦΥΤΕΥΤΑ"], level=3.65, level_txt="+3,65", level_table=False,
               notes=["Γενική κάτοψη με τα φυτευτά στοιχεία στη θέση τους: Κ23–Κ25 (δυτικά) και τοιχεία εισόδου (νότια). Η κάτοψη σε μεγαλύτερη κλίμακα στο φύλλο Σ3."],
               base="Σ3_ΕΦ.pdf – ξυλότυπος οροφής ισογείου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ3α_Οροφή_ισογείου_γενική_φυτευτά"),
    "Σ4": dict(file="S4_EF.pdf", region=(400, 680, 1380, 1560), stairs=[(1150, 1040, 1300, 1200)], exclude=[(1335, 680, 1380, 735)], **SEC,
               number="Σ4", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Α΄ ΟΡΟΦΟΥ"], level=6.75, level_below=3.65, level_txt="+6,75", notes=[SIFONI, STAIRW],
               base="Σ4_ΕΦ.pdf – ξυλότυπος οροφής Α΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ4_Οροφή_Α_ορόφου_+6.75"),
    "Σ5": dict(file="S5_EF.pdf", region=(380, 685, 1345, 1510), stairs=[(1120, 1040, 1280, 1200)], **SEC,
               number="Σ5", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Β΄ ΟΡΟΦΟΥ"], level=9.85, level_below=6.75, level_txt="+9,85", notes=[SIFONI, STAIRW],
               base="Σ5_ΕΦ.pdf – ξυλότυπος οροφής Β΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ5_Οροφή_Β_ορόφου_+9.85"),
    "Σ6": dict(file="S6_EF.pdf", region=(335, 685, 1330, 1510), stairs=[(1120, 1040, 1280, 1200)], pad=3, sections=True, cuts=True, strip_w=36, title_w=58,
               number="Σ6", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Γ΄ ΟΡΟΦΟΥ"], level=12.95, level_below=9.85, level_txt="+12,95", notes=[SIFONI, STAIRW],
               base="Σ6_ΕΦ.pdf – ξυλότυπος οροφής Γ΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ6_Οροφή_Γ_ορόφου_+12.95"),
    "Σ7": dict(file="S7_EF.pdf", region=(265, 795, 1235, 1580), stairs=[(1000, 1150, 1160, 1320)],
               number="Σ7", title=["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "Δ΄ ΟΡΟΦΟΥ"], level=16.05, level_below=12.95, level_txt="+16,05", notes=[SIFONI],
               insets=[dict(region=(1235, 1130, 1480, 1380), title=["ΛΕΠΤΟΜΕΡΕΙΑ ΜΕΛΕΤΗΤΗ", "πλάκα στη στάθμη +17,36"], chains=False)],
               base="Σ7_ΕΦ.pdf – ξυλότυπος οροφής Δ΄ ορόφου, Γ. Κόγιας (Drive 19/10/2026).", out="Σ7_Οροφή_Δ_ορόφου_+16.05"),
    "Σ8": dict(file="S8.pdf", region=(470, 775, 1345, 1510), chain_round=True,
               number="Σ8", title=["ΞΥΛΟΤΥΠΟΣ ΣΟΦΙΤΑΣ", "(ΣΤΕΓΗ)"], level_table=False, level_txt="+18,49 έως +19,72", notes=[SIFONI, "Στέγη κεκλιμένη: οι στάθμες (μπλε) στις λωρίδες-τομές της κάτοψης. «Ανεστρ.» = ανεστραμμένη δοκός (πάνω από την πλάκα)."],
               base="Σ8.pdf – ξυλότυπος σοφίτας, Γ. Κόγιας (οριστική μελέτη 02/2026, Drive 06/11/2026).", out="Σ8_Στέγη_σοφίτας"),
}
ORDER = ["Σ1", "Σ1α", "Σ2", "Σ3", "Σ3α", "Σ4", "Σ5", "Σ6", "Σ7", "Σ8"]


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
        book.save(os.path.join(OUT, "..", "ΞΥΛΟΤΥΠΟΙ_ΕΡΓΟΤΑΞΙΟΥ_Σ1-Σ8_A3_%s.pdf" % REV), garbage=4, deflate=True)


if __name__ == "__main__":
    main()
