"""Τεύχος ηλεκτρολογικής μελέτης εφαρμογής – Β1 (τυπικός όροφος Α΄ · Β΄ · Γ΄).

    python3 build_el.py [out.pdf]

Τρέχει πρώτα τους ελέγχους (el_checks.py) – σταματά αν υπάρχει ΛΑΘΟΣ – και μετά τυπώνει τα φύλλα ΗΛ-01 … ΗΛ-14 (el_sheets.py, el_det.py, el_docs.py).
R21: ΜΟΝΟ ΚΑΤΟΨΕΙΣ – με SHOW_SECTIONS = False δεν τυπώνονται οι τομές περασμάτων, το κατακόρυφο διάγραμμα, τα κατεβάσματα (el_drops.py) και οι όψεις τοίχων (el_elev.py)·
με SHOW_HVAC = False ούτε το κούτελο (el_kout.py). ΗΛ-06 γενική κάτοψη περασμάτων 1:50 + ΗΛ-07 / 08 / 09 μεγεθύνσεις (βόρεια ζώνη · σαλόνι – εξώστες · κουζίνα – είσοδος).
    --NN = μόνο το φύλλο NN (π.χ. --02 --03)."""
import os, sys
import b1_el as M
import el_checks as CK
import el_draw as D
from el_draw import P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else os.path.join(
    HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ_Β1_ΤΥΠΙΚΟΣ_ΟΡΟΦΟΣ_%s.pdf" % M.REV)


def main():
    CK.bind(M)
    R, bad = CK.report()
    for g, c, st, t in R:
        if st != "OK":
            print("%-12s %-10s %-6s %s" % (g, c, st, t))
    print("%d έλεγχοι · %d ΛΑΘΟΣ" % (len(R), len(bad)))
    if bad:
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    P.C = P.new_canvas(OUT, "Ηλεκτρολογική μελέτη εφαρμογής Β1 %s – Κωνσταντινουπόλεως 12, Αργυρούπολη" % M.REV)
    P.C.setPageCompression(1)
    import el_sheets as SH
    import el_docs as DC
    import el_det as DT
    import el_drops as DR
    import el_elev as EV
    import el_kout as KO
    SH.bind(M); DR.bind(M); EV.bind(M); KO.bind(M)
    only = [a[2:] for a in sys.argv if a.startswith("--")]
    # R21: μόνο κατόψεις – οι τομές (ΗΛ-07 παλιό), το κατακόρυφο (ΗΛ-13), τα κατεβάσματα (ΗΛ-14), οι όψεις (ΗΛ-15) και το κούτελο (ΗΛ-16) τυπώνονται μόνο με SHOW_SECTIONS / SHOW_HVAC
    sec = M.SHOW_SECTIONS
    sheets = [(k, f) for k, f in (("01", SH.sheet_01), ("02", SH.sheet_02), ("03", SH.sheet_03), ("04", SH.sheet_04), ("05", SH.sheet_05),
                                  ("06", SH.sheet_06), ("07", SH.sheet_zoom_n), ("08", SH.sheet_zoom_liv), ("09", SH.sheet_zoom_kit),
                                  ("10", SH.sheet_08), ("11", DT.sheet_10), ("12", DC.sheet_11), ("13", SH.sheet_11), ("14", SH.sheet_12),
                                  ("15", SH.sheet_07 if sec else None), ("16", SH.sheet_13 if sec else None), ("17", DR.sheet if sec else None), ("18", EV.sheet if sec else None),
                                  ("19", KO.sheet if M.SHOW_HVAC else None)) if f]
    for no, fn in sheets:
        if only and no not in only:
            continue
        fn("ΗΛ-" + no)
    P.C.save()
    print("→", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
