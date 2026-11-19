"""Τεύχος ηλεκτρολογικής μελέτης εφαρμογής – Β1 (τυπικός όροφος Α΄ · Β΄ · Γ΄).

    python3 build_el.py [out.pdf]

Τρέχει πρώτα τους ελέγχους (el_checks.py) – σταματά αν υπάρχει ΛΑΘΟΣ – και μετά τυπώνει τα φύλλα ΗΛ-00 … ΗΛ-14 (el_sheets.py).
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
    SH.bind(M); DR.bind(M)
    only = [a[2:] for a in sys.argv if a.startswith("--")]
    sheets = [(k, f) for k, f in (("00", getattr(SH, "sheet_00", None)), ("01", SH.sheet_01), ("02", SH.sheet_02), ("03", SH.sheet_03), ("04", SH.sheet_04),
                                  ("05", getattr(SH, "sheet_05", None)), ("06", getattr(SH, "sheet_06", None)), ("07", getattr(SH, "sheet_07", None)),
                                  ("08", getattr(SH, "sheet_08", None)), ("09", DT.sheet_10), ("10", DC.sheet_11), ("11", SH.sheet_11), ("12", SH.sheet_12), ("13", SH.sheet_13), ("14", DR.sheet)) if f]
    for no, fn in sheets:
        if only and no not in only:
            continue
        fn("ΗΛ-" + no)
    P.C.save()
    print("→", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
