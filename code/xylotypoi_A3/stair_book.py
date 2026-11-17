"""ΤΕΥΧΟΣ ΣΚΑΛΩΝ – όλα τα φύλλα Α3 των σκαλών σε ένα PDF για εκτύπωση (Γιάννης 17/11/2026: «στείλε μου τεύχη απ' όλα»).

    python3 stair_book.py

Παίρνει τη ΝΕΟΤΕΡΗ έκδοση κάθε φύλλου από τον φάκελο ΞΥΛΟΤΥΠΟΙ (όχι από παλαιότερες_εκδόσεις): Σ2α (υπόγειο → ισόγειο) ·
Σ3β (ισόγειο → Α΄) · Σ4β / Σ5β / Σ6β (όροφοι) · Σ7β (Δ΄ → σοφίτα) · ΣΚ ενιαία τομή · ΣΚ τομές Α-Α … ΣΤ-ΣΤ.
Τρέχει ΜΕΤΑ τα stair_s2.py · stair_s3.py (και με STAIR_FLOOR=a|b|c) · stair_s7.py · stair_all.py · stair_sections.py."""
import os, re
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΞΥΛΟΤΥΠΟΙ")
NAME = "ΣΚΑΛΕΣ_ΤΕΥΧΟΣ_A3.pdf"
PARTS = ["Σ2α_Σκάλα_υπογείου", "Σ3β_Σκάλα_ισογείου", "Σ4β_Σκάλα", "Σ5β_Σκάλα", "Σ6β_Σκάλα", "Σ7β_Σκάλα",
         "ΣΚ_Σκάλες_υπόγειο_ισόγειο_Α_όροφος_ΤΟΜΗ", "ΣΚ_Σκάλες_ΤΟΜΕΣ"]


def newest(prefix):
    fs = [f for f in os.listdir(OUT) if f.startswith(prefix) and f.endswith(".pdf")]
    assert fs, prefix
    return max(fs, key=lambda f: int(re.search(r"_R(\d+)\.pdf$", f).group(1)))


def build():
    out = pymupdf.open(); used = []
    for p in PARTS:
        f = newest(p); used.append(re.search(r"^(Σ\w+?)_.*_(R\d+)\.pdf$", f).group(1, 2)); out.insert_pdf(pymupdf.open(os.path.join(OUT, f)))
    out.set_metadata(dict(title="Τεύχος σκαλών – " + " · ".join("%s %s" % u for u in used), author="ARKAD Ι.Κ.Ε."))
    out.save(os.path.join(OUT, NAME), garbage=4, deflate=True)
    print("->", NAME, "(%d φύλλα):" % out.page_count, " · ".join("%s %s" % u for u in used))


if __name__ == "__main__":
    build()
