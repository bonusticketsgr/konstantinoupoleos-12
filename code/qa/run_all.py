"""ΤΕΛΙΚΟΣ ΕΛΕΓΧΟΣ ΟΛΩΝ ΤΩΝ ΤΕΥΧΩΝ (Γιάννης 17/11/2026: «να τα τσεκάρεις όλα, τελικό τσεκ διαστάσεων»).

    python3 run_all.py [<φάκελος με S2_EF.pdf … S7_EF.pdf, S8.pdf>]

Τρέχει με τη σειρά – και σταματά να μετρά «καθαρό» αν κάτι βγάλει εύρημα:
  1 τοιχοποιίες: check_dims · check_overlap · check_corners (b gf b1 f4 s) + qa_toixoi.py (πόρτες, έπιπλα ↔ τοίχοι, σκάλες, εμβαδά)
  2 ανόψεις: checks.py (gf b1 f4 s → 0 ΑΠΟΚΛΙΣΕΙΣ) + qa_anopseis.py (σημεία αλυσίδων ↔ στοιχεία, ντουλάπες, «Βάση»)
  3 σκάλες: stair_all.check() (ρίχτια, πατήματα, 1,20, ελεύθερο ύψος) + export_stairs.py --check (stairs.json = μοντέλα σκαλών)
  4 ξυλότυποι Σ2–Σ8: check.py (μόνο αν δοθεί ο φάκελος με τα PDF του μελετητή) + qa_holes.py (οπές / shaft = τρέχον τεύχος αποχετεύσεων)
  5 PDF: qa_pdf.py σε ΚΑΘΕ τρέχον παραδοτέο (κείμενα το ένα πάνω στο άλλο · κείμενα εκτός περιθωρίου · γραμματοσειρές)
Οι αποχετεύσεις ελέγχονται μέσα στο build τους (apox_r28.py → apox_check.py: 0 ΛΑΘΟΣ) – εδώ ελέγχεται μόνο το PDF τους.
Ό,τι βγάζει το qa_pdf στα φύλλα ΛΕΠΤΟΜΕΡΕΙΩΝ των αποχετεύσεων (παράθυρα με κομμένα κείμενα) θέλει ματιά – δεν είναι αυτόματα λάθος."""
import glob, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(HERE, "..")
DEL = os.path.join(CODE, "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ")
res = []


def run(title, cmd, cwd, ok_if=None, bad_if=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    last = out.splitlines()[-1] if out else ""
    ok = (r.returncode == 0) if ok_if is None else ok_if(out)
    if bad_if and bad_if(out):
        ok = False
    res.append((title, ok, last[:110]))
    print("%-4s %-44s %s" % ("OK" if ok else "ΛΑΘΟΣ", title, last[:110]))
    return out


def main():
    py = sys.executable
    tx = os.path.join(CODE, "toixopoiies")
    for k in ("b", "gf", "b1", "f4", "s"):
        run("τοιχοποιίες %s – διαστάσεις" % k, [py, "check_dims.py", k], tx, ok_if=lambda o: "χωρίς αντιστοιχία: 0" in o)
        run("τοιχοποιίες %s – επικαλύψεις" % k, [py, "check_overlap.py", k], tx, ok_if=lambda o: ": 0 επικαλύψεις" in o)
        run("τοιχοποιίες %s – γωνίες" % k, [py, "check_corners.py", k], tx, ok_if=lambda o: "κλειστές τρύπες: 0" in o and "εγκοπές (ομάδες ~10 cm): 0" in o)
    run("τοιχοποιίες – πόρτες / έπιπλα / σκάλες / εμβαδά", [py, "qa_toixoi.py"], HERE)
    an = os.path.join(CODE, "anopseis")
    for k in ("gf", "b1", "f4", "s"):
        run("ανόψεις %s – checks.py" % k, [py, "checks.py", k], an, ok_if=lambda o: "ΑΠΟΚΛΙΣΗ" not in o.splitlines()[-1])
    run("ανόψεις – διαστάσεις / ντουλάπες / βάση", [py, "qa_anopseis.py"], HERE)
    xa = os.path.join(CODE, "xylotypoi_A3")
    run("σκάλες – stair_all.check()", [py, "-c", "import stair_all; stair_all.check()"], xa, ok_if=lambda o: "ΕΛΕΓΧΟΣ ΟΚ" in o)
    run("σκάλες – stairs.json ενήμερο", [py, "export_stairs.py", "--check"], xa)
    if len(sys.argv) > 1:
        run("ξυλότυποι Σ2–Σ8 – check.py", [py, "check.py", sys.argv[1]], xa, ok_if=lambda o: "ΣΥΝΟΛΟ ΑΠΟΚΛΙΣΕΩΝ: 0" in o)
    run("ξυλότυποι – οπές / shaft = τεύχος αποχετεύσεων", [py, "qa_holes.py"], HERE)
    pdfs = []
    for pat in ("ΤΟΙΧΟΠΟΙΙΕΣ/ΤΟΙΧΟΠΟΙΙΕΣ_*.pdf", "ΑΝΟΨΕΙΣ/ΑΝΟΨΕΙΣ_*.pdf", "ΑΝΟΨΕΙΣ/ΚΛΙΜΑΤΙΣΤΙΚΟ_*.pdf", "ΞΥΛΟΤΥΠΟΙ/ΣΚΑΛΕΣ_ΤΕΥΧΟΣ_A3.pdf", "ΞΥΛΟΤΥΠΟΙ/ΞΥΛΟΤΥΠΟΙ_ΕΡΓΟΤΑΞΙΟΥ_*.pdf",
                "ΑΠΟΧΕΤΕΥΣΕΙΣ_ΥΔΡΟΡΡΟΕΣ/ΑΠΟΧΕΤΕΥΣΕΙΣ_ΥΔΡΟΡΡΟΕΣ_ΤΕΥΧΟΣ_*.pdf"):
        pdfs += sorted(glob.glob(os.path.join(DEL, pat)))
    for p in pdfs:
        run("PDF %s" % os.path.basename(p)[:38], [py, "qa_pdf.py", p], HERE,
            ok_if=lambda o: "εκτός περιθωρίου: 0" in o and ("επικαλύψεις κειμένων: 0" in o or "ΑΠΟΧΕΤΕΥΣΕΙΣ" in o))
    bad = [r for r in res if not r[1]]
    print("\n%d έλεγχοι · %d με εύρημα" % (len(res), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
