"""Γεωμετρικά βοηθητικά για τα ηλεκτρολογικά: σε ποιον τοίχο κάθεται ένα σημείο, αποστάσεις από γωνίες χώρου, τομές οδεύσεων με δοκούς.
Δουλεύει πάνω στα μοντέλα τοιχοποιιών (toixopoiies/*_model.py) και ανόψεων (anopseis/*_anopsi.py) – δεν ορίζει δική του γεωμετρία."""
import math

TOL = 0.016          # ανοχή «πάνω στην παρειά»
# τι αντέχει χωνευτό κουτί (βάθος 47–60 mm) χωρίς να αγγιχτεί σκυρόδεμα
BOX_OK = {"T2": "γυψοσανίδα CW 50", "T2N": "γυψοσανίδα CW 50", "T2A": "γυψοσανίδα CW 100", "T7": "τοίχος λεκάνης (πλευρά σκελετού)",
          "T7A": "τοίχος λεκάνης", "T6": "διπλός σκελετός", "T6A": "ΠΥΡΑΝΤΟΧΟΣ τοίχος κλιμακοστασίου – πυράντοχο κουτί",
          "T6B": "τοίχος πόρτας εισόδου – μέσα στο κανάλι CW 50", "T8": "μέτωπο shaft",
          "T3": "επένδυση CW 30 (κουτί 47 mm – το τούβλο πίσω της σκάβεται 1–2 cm αν χρειαστεί)",
          "T1": "τούβλο 25 – αυλάκι", "T4": "τούβλο 11 – αυλάκι ως 3 cm", "T4A": "τούβλο 30 – αυλάκι", "T5": "τούβλο 10 – αυλάκι", "T10": "τούβλο 15"}
BOX_NO = {"T9": "κολλητή γυψοσανίδα πάνω σε ΣΚΥΡΟΔΕΜΑ (3,5 cm) – δεν χωρά κουτί, το σκυρόδεμα δεν σκάβεται"}


def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def is_rect(pts):
    return len(pts) == 4 or (len(pts) == 5 and pts[0] == pts[-1])


def face_of(M, x, y, d):
    """Ο τοίχος (ή το υποστύλωμα) του μοντέλου M στου οποίου την παρειά κάθεται το σημείο (x, y) που βλέπει προς d.
    Επιστρέφει (είδος, id, τύπος) – είδος: "wall" / "col" / None."""
    def on(b):
        x0, y0, x1, y1 = b
        if d == "S":
            return abs(y - y1) <= TOL and x0 - TOL <= x <= x1 + TOL
        if d == "N":
            return abs(y - y0) <= TOL and x0 - TOL <= x <= x1 + TOL
        if d == "E":
            return abs(x - x1) <= TOL and y0 - TOL <= y <= y1 + TOL
        return abs(x - x0) <= TOL and y0 - TOL <= y <= y1 + TOL
    best = None
    for w in M.WALLS:
        if not is_rect(w["pts"]):
            continue
        if on(bbox(w["pts"])):
            # προτίμηση: επένδυση / γυψοσανίδα μπροστά από τούβλο (η παρειά που φαίνεται)
            rank = 0 if w["type"] in ("T3", "T9") else 1
            if best is None or rank < best[0]:
                best = (rank, ("wall", w["id"], w["type"]))
    if best:
        return best[1]
    for i, p in enumerate(M.COLS):
        if is_rect(p) and on(bbox(p)):
            return ("col", "Κ#%d" % (i + 1), "COL")
    return (None, None, None)


def in_rect(x, y, r, tol=0.0):
    return r[0] - tol <= x <= r[2] + tol and r[1] - tol <= y <= r[3] + tol


def seg_hits_rect(a, b, r, shrink=0.01):
    """Τέμνει το ευθύγραμμο τμήμα a–b το εσωτερικό του ορθογωνίου r; (δειγματοληψία ανά 1 cm – αρκεί για ορθογώνιες οδεύσεις)"""
    x0, y0, x1, y1 = r[0] + shrink, r[1] + shrink, r[2] - shrink, r[3] - shrink
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(L / 0.01))
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if x0 <= x <= x1 and y0 <= y <= y1:
            return True
    return False


def path_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def door_zone(door, pad=0.0):
    """Το τεταρτοκύκλιο που σαρώνει το φύλλο μιας πόρτας (άρθρωση, άκρο ανοιχτού φύλλου, άλλη παραστάδα) ως bbox."""
    (hx, hy), (lx, ly), (jx, jy) = door
    xs = [hx, lx, jx]; ys = [hy, ly, jy]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def dist_seg(p, a, b):
    """Απόσταση σημείου από ευθύγραμμο τμήμα."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def leaf_covers(door, x, y, clear=0.12):
    """Σκεπάζει το ΑΝΟΙΧΤΟ (90°) φύλλο της πόρτας το σημείο του τοίχου; (σημείο σε απόσταση < clear από το ανοιχτό φύλλο)"""
    return dist_seg((x, y), door[0], door[1]) < clear


def fmt(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",")
