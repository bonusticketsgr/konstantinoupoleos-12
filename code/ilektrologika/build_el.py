"""Τεύχος ηλεκτρολογικής μελέτης εφαρμογής – Β1 (τυπικός όροφος Α΄ · Β΄ · Γ΄).

    python3 build_el.py [out.pdf]

Τρέχει πρώτα τους ελέγχους (el_checks.py) – σταματά αν υπάρχει ΛΑΘΟΣ – και μετά τυπώνει τα φύλλα ΗΛ-00 … ΗΛ-16."""
import os, sys
import b1_el as M
import el_checks as CK
import el_draw as D
from el_draw import P
import el_plans as PL

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
    PL.bind(M)
    only = [a[2:] for a in sys.argv if a.startswith("--")]
    import el_docs as DC
    import el_det as DT
    DC.bind(M); DT.bind(M)
    sheets = [("00", DC.sheet_00), ("01", PL.sheet_01), ("02", PL.sheet_02), ("03", PL.sheet_03), ("04", PL.sheet_04), ("05", PL.sheet_05),
              ("06", PL.sheet_06), ("07", PL.sheet_07), ("08", PL.sheet_08), ("09", PL.sheet_09), ("10", DT.sheet_10), ("11", DC.sheet_11),
              ("12", DC.sheet_12), ("13", DC.sheet_13), ("14", DC.sheet_14), ("15", DC.sheet_15), ("16", DT.sheet_16)]
    for no, fn in sheets:
        if only and no not in only:
            continue
        fn("ΗΛ-" + no)
    P.C.save()
    print("→", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
