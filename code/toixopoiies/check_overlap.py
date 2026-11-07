"""Έλεγχος επικαλύψεων (Γιάννης 07/11/2026: «τοίχους να μην καβαλάνε ο ένας τον άλλον»).
Για κάθε ζεύγος ορθογωνίων τοίχων (και τοίχος–υποστύλωμα / τοίχος–κούφωμα) υπολογίζει την τομή. Επιτρεπτή είναι ΜΟΝΟ η
επικάλυψη γωνίας / ταυ ανάμεσα σε κάθετους τοίχους (τομή ≤ πάχος × πάχος). Αναφέρει:
  (α) παράλληλοι / συγγραμμικοί τοίχοι που επικαλύπτονται (διπλομέτρηση, «καβάλημα»)
  (β) κάθετοι τοίχοι που μπαίνουν ο ένας μέσα στον άλλο πέρα από τη γωνία
  (γ) τοίχος πάνω σε υποστύλωμα / τοιχείο ή πάνω σε κούφωμα
Χρήση: python3 check_overlap.py [gf|b1|s]   → πρέπει να βγάζει 0."""
import sys, importlib
name = sys.argv[1] if len(sys.argv) > 1 else "gf"
M = importlib.import_module({"gf": "gf_model", "b1": "b1_model", "s": "s_model", "f4": "f4_model", "b": "b_model"}[name])
EPS = 0.003


def inter(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1]); x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    return (x1 - x0, y1 - y0) if x1 - x0 > EPS and y1 - y0 > EPS else None


walls = [(w["id"], M.bbox(w["pts"])) for w in M.WALLS if M.is_rect(w["pts"])]
cols = [("ΥΠΟΣΤ.%d" % i, M.bbox(p)) for i, p in enumerate(M.COLS, 1)]
wins = [("ΚΟΥΦ.%d" % i, M.bbox(p)) for i, p in enumerate(M.WINS, 1) if M.is_rect(p)]
probs = []
for i, (ia, a) in enumerate(walls):
    ta = min(a[2] - a[0], a[3] - a[1]); ha = (a[2] - a[0]) >= (a[3] - a[1])   # πάχος, οριζόντιος;
    for ib, b in walls[i + 1:]:
        q = inter(a, b)
        if not q:
            continue
        tb = min(b[2] - b[0], b[3] - b[1]); hb = (b[2] - b[0]) >= (b[3] - b[1])
        if ha == hb:
            probs.append("(α) παράλληλοι %s / %s επικαλύπτονται %.2f × %.2f" % (ia, ib, q[0], q[1]))
        elif q[0] > max(ta, tb) + EPS or q[1] > max(ta, tb) + EPS:
            probs.append("(β) %s / %s τομή %.2f × %.2f πέρα από τη γωνία" % (ia, ib, q[0], q[1]))
    for ib, b in cols + wins:
        q = inter(a, b)
        if q:
            probs.append("(γ) %s πάνω σε %s: %.2f × %.2f" % (ia, ib, q[0], q[1]))
for p in probs:
    print(p)
print("%s: %d επικαλύψεις" % (name, len(probs)))
