"""3D των καλωδίων (Β1): γράφει μία σελίδα HTML (three.js) από το ΙΔΙΟ μοντέλο με το τεύχος – τοίχοι, δοκάρια, οπές, και οι ΠΡΑΓΜΑΤΙΚΕΣ διαδρομές (κορμοί,
τροφοδοσία κάθε τοίχου, κάθε κουτί) όπως τις ελέγχει το el_route.py. Δεν σχεδιάζεται καλώδιο που δεν έχει περάσει τον έλεγχο.

ΠΡΟΒΟΛΗ ΑΝΑ ΧΩΡΟ (20/11/2026 – Γιάννης: «κάνε μου και τον κάθε χώρο ξεχωριστά σε 3D να μπορώ να τον δω αναλυτικά»): η σελίδα έχει επιλογή χώρου. Κάθε χώρος
κόβεται στο κουτί του (ROOMS3 → εσωτερικό + το πάχος των τοίχων που τον κλείνουν), δείχνει ΜΟΝΟ τα δικά του σημεία με αριθμό και ύψος, τα φώτα / ανιχνευτές /
μονάδες της οροφής του, και για κάθε σημείο τι είναι, σε ποιο κύκλωμα και από πού φτάνει το καλώδιο (ίδιο κείμενο με τις τομές ΗΛ-14).
ΠΕΡΙΗΓΗΣΗ ΜΕΣΑ (20/11 – «να μπορώ να περιηγηθώ ουσιαστικά μέσα στο σπίτι θέλω»): η σελίδα έχει και περπάτημα στο ύψος των ματιών. Το `nav_grid` βγάζει από το
μοντέλο τον κάναβο του δαπέδου που πατιέται (χώροι + ανοίγματα θυρών + μπαλκονόπορτες + εξώστες, μείον τοίχοι / κολόνες / στηθαία / έπιπλα) και ελέγχει ότι
κάθε χώρος και κάθε εξώστης φτάνεται περπατώντας από την πόρτα εισόδου.
Σε ποιον χώρο ανήκει κάθε σημείο βγαίνει ΓΕΩΜΕΤΡΙΚΑ (σε ποιον χώρο βλέπει η παρειά του) – το build σταματά αν κάποιο σημείο μείνει χωρίς χώρο.
    python3 el_3d.py [out.html]         → η σελίδα που δημοσιεύεται (ΗΛΕΚΤΡΟΛΟΓΙΚΑ/ΚΑΤΕΒΑΣΜΑΤΑ_3D.html)
    python3 el_3d.py --check            → μόνο έλεγχος δεδομένων (κάθε σημείο σε χώρο, με διαδρομή) – τρέχει και από το code/qa/run_all.py
    python3 el_3d.py --test t.html      → τοπική σελίδα δοκιμής· μετά: node el_3d_test.js t.html [desk|phone]  (κάθε σημείο κάθε χώρου επιλέγεται και φαίνεται)"""
import bisect, heapq, math
import json, os, sys
import b1_el as M
import el_route as RT
import el_drops as DR
import el_geom as G

W, A = M.W, M.A
ROOMS = [("ΣΑΛΟΝΙ", 4.9, 7.6), ("ΚΟΥΖΙΝΑ", 11.6, 8.9), ("ΧΩΛ", 4.3, 3.85), ("ΥΠΝ.1", 2.6, 1.9), ("ΥΠΝ.2", 7.9, 3.0), ("ΛΟΥΤΡΟ", 5.75, 2.0), ("ΛΟΥΤΡΟ ΓΟΝΕΩΝ", 1.9, 4.3), ("ΣΚΑΛΑ", 11.6, 6.3)]

# ---------------------------------------------------------------- χώροι της προβολής «ανά χώρο»
# (κωδικός = το #όνομα στη διεύθυνση της σελίδας · όνομα · σύντομο · ορθογώνια του ΚΑΘΑΡΟΥ εσωτερικού, από παρειά σε παρειά)
EX = "exostes"
ROOMS3 = [
    ("saloni", "Σαλόνι – τραπεζαρία", "Σαλόνι", [(1.705, 5.15, W.LIN_X, 9.115)]),
    ("kouzina", "Κουζίνα", "Κουζίνα", [(W.LIN_X, 7.75, 13.759, 9.15), (13.349, 7.66, 13.759, 7.75), (9.699, 9.15, 12.699, 10.06)]),
    ("xol", "Χωλ", "Χωλ", [(3.299, 3.35, 6.399, 4.35), (3.299, 4.35, 5.349, 5.06), (5.449, 4.35, 6.399, 5.15)]),
    ("ypn1", "Υπνοδωμάτιο 1", "Υπν. 1", [(1.135, 0.165, 4.80, 3.25)]),
    ("ypn2", "Υπνοδωμάτιο 2", "Υπν. 2", [(6.499, 0.75, 9.395, 5.05)]),
    ("loutro", "Λουτρό", "Λουτρό", [(5.05, 0.80, 6.399, 3.25)]),
    ("loutro-goneon", "Λουτρό γονέων", "Λ. γονέων", [(0.109, 3.16, 1.049, 5.05), (1.049, 3.50, 3.149, 5.05)]),
    ("platyskalo", "Πλατύσκαλο – shaft", "Πλατύσκαλο", [(9.699, 3.25, 11.049, 5.10), (9.55, 5.10, 10.90, 7.60)]),
]
# το κουτί κοπής βγαίνει από τους τοίχους (βλ. _outer)· εδώ μόνο ό,τι χρειάζεται με το χέρι: το πλατύσκαλο πιάνει ΚΑΙ το shaft πίσω από τον τοίχο-ντουλάπα
OUTER_FIX = {"platyskalo": {"N": 2.70}}
# πρόσθετες διαδρομές (EXTRA3) → σε ποιους χώρους φαίνονται
EXTRA_ROOMS = {"Λ4": ["loutro-goneon"], "LED3": ["ypn1"], "ΚΜ2": ["ypn1", "xol"], "ΚΜ1": ["saloni"], "Π59": ["kouzina"], "ΕΚ7-8": [EX, "ypn1"], "ΕΚ1-6": [EX, "saloni"],
               "ΜΕ1": ["saloni", "platyskalo"], "ΜΕ2": ["saloni"], "ΜΕ3": ["saloni"], "ΜΕ4": ["ypn2"], "ΜΕ5": ["ypn1"]}
# κουφώματα: πλάτος → όνομα από το W.WIN_SIZES· ποδιά / πρέκι από τον πίνακα κουφωμάτων A-50-02 (πλάτος / ποδιά / πρέκι), + 3 cm για το γέμισμα 12 αντί 15
WIN_SILL = {"W2.03": (1.03, 1.53), "W2.04": (1.03, 1.53), "W2.05": (0.18, 1.53), "W2.07": (1.53, 2.43), "W2.09": (1.13, 2.43)}
WIN_FULL = (0.0, 2.43)
Z_EXT_LAMP = 2.72            # επίτοιχα κυλινδρικά φωτιστικά στο ταβάνι των εξωστών (πλάκα h20: κάτω παρειά +2,78)
NRM = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
# ΠΕΡΙΗΓΗΣΗ ΜΕΣΑ ΣΤΟ ΣΠΙΤΙ (20/11 – Γιάννης: «να μπορώ να περιηγηθώ ουσιαστικά μέσα στο σπίτι θέλω»): κάναβος «πατιέται / δεν πατιέται»
NAV_C, NAV_R = 0.10, 0.17                    # κελί 10 cm · ο άνθρωπος κρατά 17 cm από κάθε τοίχο / κολόνα / έπιπλο (πόρτα 70 → περνά από 36 cm)
NAV_BOX = (-1.2, -0.3, 14.0, 11.3)
NAV_START = (8.85, 5.80, -90.0)              # μόλις μέσα από την πόρτα εισόδου, κοιτώντας δυτικά (μέσα στο σαλόνι) – x, y, μοίρες από τον βορρά δεξιόστροφα
EX_STAND = (6.0, 10.2)                       # «Εξώστες»: στον νότιο εξώστη, μπροστά στη συρόμενη του σαλονιού
Z_PARAPET = 1.05                             # στηθαία / τοιχία εξωστών (COLS2): ΕΝΔΕΙΚΤΙΚΟ ύψος – μόνο για να φαίνεται το εμπόδιο


def soffit_over(x, y):
    s = [A.beam_soffit(b[1]) for b in A.BEAMS if G.in_rect(x, y, b[2:6], tol=0.005)]
    return min(s) if s else None


def _p3(pts):
    return [[round(q[0], 3), round(q[1], 3), round(q[2], 3)] for q in pts]


def _r4(r):
    return [round(q, 3) for q in r]


# ---------------------------------------------------------------- σε ποιον χώρο ανήκει ένα σημείο
def room_at(x, y, tol=0.0):
    for rid, _, _, rects in ROOMS3:
        if any(G.in_rect(x, y, r, tol=tol) for r in rects):
            return rid
    return None


def rooms_of(x, y, d):
    """Σημείο τοίχου που βλέπει προς d: ο χώρος μέσα στον οποίο βλέπει. Αν βλέπει έξω (εξώστης) → «Εξώστες» ΚΑΙ ο χώρος πίσω από τον τοίχο του
    (από εκεί έρχεται το καλώδιό του – φαίνεται και στις δύο προβολές)."""
    nx, ny = NRM[d]
    r = room_at(x + nx * 0.06, y + ny * 0.06)
    if r:
        return [r]
    for t in (0.12, 0.20, 0.28, 0.36, 0.44, 0.52):
        h = room_at(x - nx * t, y - ny * t)
        if h:
            return [EX, h]
    return [EX]


def _outer(rid, bb):
    """Κουτί κοπής ενός χώρου: το καθαρό εσωτερικό + σε κάθε πλευρά το πάχος των τοίχων / κολονών που τον κλείνουν (ως 0,45 m) + 10 cm,
    ώστε να φαίνεται ολόκληρος ο τοίχος (και ό,τι περνά μέσα του) και τα σημεία της εξωτερικής του παρειάς."""
    x0, y0, x1, y1 = bb
    solids = [W.bbox(w["pts"]) for w in W.WALLS] + [W.bbox(p) for p in W.COLS]
    CAP, PAD = 0.45, 0.10

    def grow(side):
        lim = {"W": x0, "E": x1, "N": y0, "S": y1}[side]
        cur = lim
        for _ in range(3):
            nxt = None
            for r in solids:
                along = (min(r[3], y1) - max(r[1], y0)) if side in "WE" else (min(r[2], x1) - max(r[0], x0))       # πόσο μήκος της πλευράς πιάνει
                across = (r[2] - r[0]) if side in "WE" else (r[3] - r[1])                                           # πάχος κάθετα στην πλευρά
                if along < 0.15 or (across > 0.40 and along < 0.60):       # κάθετος τοίχος που τη διασχίζει / κολόνα στη γωνία: δεν την κλείνει
                    continue
                lo, hi = (r[0], r[2]) if side in "WE" else (r[1], r[3])
                if side in "WN" and lo < cur - 0.005 and hi > cur - 0.05 and lo < lim:
                    nxt = lo if nxt is None else min(nxt, lo)
                if side in "ES" and hi > cur + 0.005 and lo < cur + 0.05 and hi > lim:
                    nxt = hi if nxt is None else max(nxt, hi)
            if nxt is None:
                break
            if abs(nxt - lim) > CAP:
                cur = lim - CAP if side in "WN" else lim + CAP
                break
            cur = nxt
        v = cur - PAD if side in "WN" else cur + PAD
        return OUTER_FIX.get(rid, {}).get(side, v)
    return [round(grow("W"), 3), round(grow("N"), 3), round(grow("E"), 3), round(grow("S"), 3)]


# ---------------------------------------------------------------- περιήγηση: πού μπορείς να πατήσεις
def _in_poly(x, y, poly):
    ins = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def nav_grid(wins):
    """Το δάπεδο που πατιέται: μέσα σε χώρο, σε άνοιγμα πόρτας, σε μπαλκονόπορτα ή σε εξώστη – ΚΑΙ τουλάχιστον NAV_R από τοίχο, κολόνα, στηθαίο, έπιπλο, παράθυρο
    με ποδιά. Επιστρέφει και το σημείο όπου «στέκεσαι» σε κάθε χώρο. Σταματά αν κάποιος χώρος δεν φτάνεται περπατώντας από την είσοδο."""
    x0, y0, x1, y1 = NAV_BOX
    nx, ny = int(round((x1 - x0) / NAV_C)), int(round((y1 - y0) / NAV_C))
    region = [r for _, _, _, rects in ROOMS3 for r in rects] + [tuple(d) for d in RT._C["doors"]]
    for w in wins:                               # μπαλκονόπορτα (ως το δάπεδο) = πέρασμα, με 10 cm εκατέρωθεν για να δένει με τον χώρο και τον εξώστη
        if w[4] <= 0.01:
            region.append((w[0] - 0.10, w[1] - 0.10, w[2] + 0.10, w[3] + 0.10))
    balc = [[(round(q[0], 3), round(q[1], 3)) for q in poly] for poly in W.FLOORS]
    solids = ([W.bbox(w["pts"]) for w in W.WALLS] + [W.bbox(q) for q in W.COLS] + [W.bbox(q) for q in W.COLS2] + [f[1] for f in RT._C["furn"]]
              + [tuple(w[:4]) for w in wins if w[4] > 0.01])
    free = [[False] * nx for _ in range(ny)]
    for j in range(ny):
        y = y0 + (j + 0.5) * NAV_C
        for i in range(nx):
            x = x0 + (i + 0.5) * NAV_C
            if (any(G.in_rect(x, y, r) for r in region) or any(_in_poly(x, y, q) for q in balc)) and not any(G.in_rect(x, y, q, tol=NAV_R) for q in solids):
                free[j][i] = True

    def cell(x, y):
        return int((x - x0) // NAV_C), int((y - y0) // NAV_C)

    def near(x, y, rmax=1.5, ok=None):
        i0, j0 = cell(x, y); best, bd = None, 1e9; R = int(rmax / NAV_C) + 1
        for j in range(max(0, j0 - R), min(ny, j0 + R + 1)):
            for i in range(max(0, i0 - R), min(nx, i0 + R + 1)):
                if free[j][i] and (ok is None or ok[j][i]):
                    d = (x0 + (i + 0.5) * NAV_C - x) ** 2 + (y0 + (j + 0.5) * NAV_C - y) ** 2
                    if d < bd:
                        bd, best = d, (i, j)
        return best
    # απόσταση περπατήματος από την είσοδο (8 γείτονες, χωρίς να «κόβεις» γωνία)· ό,τι δεν φτάνεται δεν πατιέται (π.χ. λωρίδα πίσω από έπιπλο)
    si, sj = near(NAV_START[0], NAV_START[1], 0.5)
    INF = 1e9
    dist = [[INF] * nx for _ in range(ny)]; dist[sj][si] = 0.0; heap = [(0.0, si, sj)]
    while heap:
        d, i, j = heapq.heappop(heap)
        if d > dist[j][i] + 1e-9:
            continue
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                a, b = i + di, j + dj
                if (di or dj) and 0 <= a < nx and 0 <= b < ny and free[b][a] and (not (di and dj) or (free[j][a] and free[b][i])):
                    nd = d + (1.4142 if di and dj else 1.0) * NAV_C
                    if nd < dist[b][a] - 1e-9:
                        dist[b][a] = nd; heapq.heappush(heap, (nd, a, b))
    for j in range(ny):
        for i in range(nx):
            free[j][i] = free[j][i] and dist[j][i] < INF

    def cxy(c):
        return x0 + (c[0] + 0.5) * NAV_C, y0 + (c[1] + 0.5) * NAV_C

    def sees(p, q):                              # ευθεία μόνο πάνω από δάπεδο που πατιέται (δεν περνά τοίχο, κολόνα, έπιπλο)
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / 0.05))
        for k in range(n + 1):
            i, j = cell(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n)
            if not (0 <= i < nx and 0 <= j < ny and free[j][i]):
                return False
        return True

    def view_point(inroom, name, same=None):
        """Πού στέκεσαι όταν πας σε έναν χώρο: μόλις μπεις από την πόρτα του (ως 1 m μέσα), εκεί και προς τα εκεί που φαίνεται το περισσότερο δάπεδό του
        (παράθυρο 90°). Επιστρέφει [x, y, μοίρες από τον βορρά δεξιόστροφα]."""
        cells = [(i, j) for j in range(ny) for i in range(nx) if free[j][i] and inroom(*cxy((i, j)))]
        assert cells, "3D περιήγηση: ο χώρος «%s» δεν φτάνεται περπατώντας από την είσοδο" % name
        e = min(cells, key=lambda c: dist[c[1]][c[0]])
        if same:                                 # εξώστες: μόνο ο εξώστης όπου βγαίνεις πρώτα
            poly = next(q for q in same if _in_poly(*cxy(e), q))
            cells = [c for c in cells if _in_poly(*cxy(c), poly)]
        d0 = dist[e[1]][e[0]]
        cand = [e] + [c for c in cells if c[0] % 2 == 0 and c[1] % 2 == 0 and 0.25 <= dist[c[1]][c[0]] - d0 <= 1.0]
        samp = [cxy(c) for c in cells if c[0] % 3 == 0 and c[1] % 3 == 0]
        best = None
        for c in cand:
            pt = cxy(c); bins = [0] * 36
            for q in samp:
                if math.hypot(q[0] - pt[0], q[1] - pt[1]) >= 0.25 and sees(pt, q):
                    bins[int((math.degrees(math.atan2(q[0] - pt[0], -(q[1] - pt[1]))) % 360) // 10) % 36] += 1
            for k in range(36):
                sc = sum(bins[(k + m) % 36] for m in range(-4, 5))
                if best is None or sc > best[0]:
                    best = (sc, pt, k * 10 + 5)
        yaw = (best[2] + 180) % 360 - 180
        return [round(best[1][0], 3), round(best[1][1], 3), round(yaw, 1)]
    stand = {}
    for rid, name, _, rects in ROOMS3:
        stand[rid] = view_point(lambda x, y, rects=rects: any(G.in_rect(x, y, q) for q in rects), name)
    assert near(EX_STAND[0], EX_STAND[1], 1.0), "3D περιήγηση: ο νότιος εξώστης δεν φτάνεται από τη συρόμενη του σαλονιού"
    stand[EX] = view_point(lambda x, y: any(_in_poly(x, y, q) for q in balc), "Εξώστες", same=balc)
    for k, poly in enumerate(balc):              # κάθε εξώστης πρέπει να φτάνεται από τη μπαλκονόπορτά του
        assert any(free[j][i] and _in_poly(x0 + (i + 0.5) * NAV_C, y0 + (j + 0.5) * NAV_C, poly) for j in range(ny) for i in range(nx)), "3D περιήγηση: ο εξώστης %d δεν φτάνεται" % (k + 1)
    rows = []
    for j in range(ny):
        bits = "".join("1" if q else "0" for q in free[j]); bits += "0" * (-len(bits) % 4)
        rows.append("".join("%x" % int(bits[k:k + 4], 2) for k in range(0, len(bits), 4)))
    return dict(x0=x0, y0=y0, c=NAV_C, nx=nx, ny=ny, rows=rows, balc=balc, start=[NAV_START[0], NAV_START[1], NAV_START[2]],
                n=sum(q for r in free for q in r)), stand


def loose():
    """Έπιπλα χώρου για την περιήγηση – ΕΝΔΕΙΚΤΙΚΑ: οι θέσεις είναι του σχεδίου τοιχοποιιών (EQUIP: καναπές, τραπέζια, κρεβάτια, γραφείο· BATHS: πάγκοι, λεκάνες, γυαλιά
    ντους), τα ύψη τα βάζει η σελίδα (τυπικά). Δεν εμποδίζουν το περπάτημα. Η κουζίνα και οι ντουλάπες έως οροφή είναι ήδη στα έπιπλα του el_route (με ύψη)."""
    out, glass = [], []
    for e in W.EQUIP:
        k, x0, y0, x1, y1 = e[:5]; tag = e[5] if len(e) > 5 else ""
        if x0 > W.LIN_X + 0.3 or k in ("tall", "hob", "appl", "sink"):
            continue
        if k == "sofa":
            kind, side = "sofa", (e[6] if len(e) > 6 else "N")
        elif k in ("arm", "chair", "bed"):
            kind, side = k, tag or {"arm": "E", "chair": "N", "bed": "N"}[k]
        elif k == "tv":
            kind, side = "tv", ""
        elif k == "rect":
            kind, side = ("table" if ("ΤΡΑΠΕΖ" in tag or "ΓΡΑΦ" in tag) else "side" if max(x1 - x0, y1 - y0) <= 0.5 else "low"), ""
        else:
            continue
        out.append([round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3), kind, side])
    for b in W.BATHS:
        if b.get("counter"):
            out.append([round(v, 3) for v in b["counter"]] + ["counter", ""])
        if b.get("toilet"):
            (x, y), d = b["toilet"]; w, dp = 0.38, 0.56
            r = {"E": (x, y - w / 2, x + dp, y + w / 2), "W": (x - dp, y - w / 2, x, y + w / 2), "S": (x - w / 2, y, x + w / 2, y + dp), "N": (x - w / 2, y - dp, x + w / 2, y)}[d]
            out.append([round(v, 3) for v in r] + ["wc", ""])
        if b.get("screen"):
            (ax, ay), (bx, by) = b["screen"]
            glass.append([round(min(ax, bx), 3), round(min(ay, by), 3), round(max(ax, bx), 3), round(max(ay, by), 3)])
    return out, glass


def plate(wins):
    """Το πάτωμα του ορόφου σε ορθογώνια που ΔΕΝ επικαλύπτονται: χώροι, ανοίγματα θυρών, τοίχοι, κολόνες, κουφώματα, έπιπλα, εξώστες – και ό,τι κλείνεται
    ολόγυρα από αυτά. Στην περιήγηση είναι το δάπεδο, η πλάκα από κάτω και η πλάκα από πάνω (έξω από το σπίτι δεν υπάρχει πάτωμα)."""
    rects = ([r for _, _, _, rr in ROOMS3 for r in rr] + [tuple(d) for d in RT._C["doors"]] + [W.bbox(w["pts"]) for w in W.WALLS] + [W.bbox(q) for q in W.COLS]
             + [W.bbox(q) for q in W.COLS2] + [tuple(w[:4]) for w in wins] + [f[1] for f in RT._C["furn"]])
    polys = [list(q) for q in W.FLOORS]
    for q in polys:                              # οι εξώστες είναι ορθογωνικά πολύγωνα – αλλιώς η κάλυψη θα ήταν κατά προσέγγιση
        assert all(abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6 for a, b in zip(q, q[1:] + q[:1])), "3D: εξώστης με λοξή πλευρά – θέλει άλλο τρόπο για το δάπεδο"
    R3 = lambda v: round(v, 3)
    xs = sorted({R3(v) for r in rects for v in (r[0], r[2])} | {R3(pt[0]) for q in polys for pt in q})
    ys = sorted({R3(v) for r in rects for v in (r[1], r[3])} | {R3(pt[1]) for q in polys for pt in q})
    nx, ny = len(xs) + 1, len(ys) + 1            # +1 στήλη / γραμμή «έξω» γύρω-γύρω (δείκτες 0 και n)
    mark = [[False] * (nx + 1) for _ in range(ny + 1)]
    for r in rects:
        i0, i1 = bisect.bisect_left(xs, R3(r[0])), bisect.bisect_left(xs, R3(r[2]))
        j0, j1 = bisect.bisect_left(ys, R3(r[1])), bisect.bisect_left(ys, R3(r[3]))
        for j in range(j0, j1):
            for i in range(i0, i1):
                mark[j + 1][i + 1] = True
    for q in polys:
        for j in range(len(ys) - 1):
            for i in range(len(xs) - 1):
                if not mark[j + 1][i + 1] and _in_poly((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2, q):
                    mark[j + 1][i + 1] = True
    out = [[False] * (nx + 1) for _ in range(ny + 1)]; todo = [(0, 0)]; out[0][0] = True      # ό,τι δεν φτάνεται απ' έξω είναι κλεισμένο μέσα στο σπίτι → πάτωμα
    while todo:
        i, j = todo.pop()
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a <= nx and 0 <= b <= ny and not out[b][a] and not mark[b][a]:
                out[b][a] = True; todo.append((a, b))
    runs = {}                                    # ίδια λωρίδα σε διαδοχικές γραμμές → ένα ορθογώνιο
    res = []
    for j in range(len(ys) - 1):
        row = []; i = 0
        while i < len(xs) - 1:
            if not out[j + 1][i + 1]:
                k = i
                while k < len(xs) - 1 and not out[j + 1][k + 1]:
                    k += 1
                row.append((i, k)); i = k
            else:
                i += 1
        nxt = {}
        for a in row:
            if a in runs:
                nxt[a] = runs.pop(a)
            else:
                nxt[a] = j
        for a, j0 in runs.items():
            res.append([xs[a[0]], ys[j0], xs[a[1]], ys[j]])
        runs = nxt
    for a, j0 in runs.items():
        res.append([xs[a[0]], ys[j0], xs[a[1]], ys[-1]])
    return res


# ---------------------------------------------------------------- τι είναι κάθε σημείο (τίτλος · περιγραφή · κύκλωμα) – από τους πίνακες του μοντέλου
N_TXT = {1: "μονός", 2: "διπλός", 3: "τριπλός", 4: "2 διπλοί"}
SW_TXT = {"1": "απλός", "2": "αλέ-ρετούρ", "X": "ενδιάμεσος", "D": "dimmer", "R": "ρολό"}
CIRC = {c["id"]: c for c in M.CIRCUITS}


def circ_txt(cid):
    c = CIRC.get(cid)
    return ("%s – %s · %s · %s A" % (cid, c["name"], c["cable"], c["In"])) if c else cid


def _cap(s):
    return s[:1].upper() + s[1:] if s else s


def point_info():
    """{id: (κατηγορία, τίτλος, περιγραφή, κύκλωμα, ομάδες φώτων)} για κάθε σημείο τοίχου."""
    I = {}
    for s in M.SOCKETS:
        pid, n, kind, circ, room, desc = s[0], s[4], s[5], s[7], s[8], s[9]
        opt = s[10] if len(s) > 10 else {}
        if kind == "fix":
            t = "Έξοδος καλωδίου – μόνιμη σύνδεση"
        else:
            t = "Ρευματοδότης %s" % N_TXT.get(n, "%d θέσεων" % n)
            t += {"usb": " με USB-C", "ip": " στεγανός %s" % ("IP55" if room == "ΕΞ" else "IP44"), "ded": " – αποκλειστική γραμμή"}.get(kind, "")
        extra = [q for q in ("επιφανειακά ΜΕΣΑ στο ντουλάπι – όχι κουτί στον τοίχο" if opt.get("surf") else "", "ΠΥΡΑΝΤΟΧΟ κουτί" if opt.get("fire") else "") if q]
        I[pid] = ("sock", t, " · ".join([_cap(desc)] + extra), circ_txt(circ), [])
    for f in M.FIXED:
        I[f[0]] = ("sock", "Παροχή μηχανήματος", _cap(f[7]), circ_txt(f[5]), [])
    for s in M.SWITCHES:
        keys = s[4]
        parts = ["%s: %s %s" % (g, SW_TXT[k], M.GROUPS[g]["name"]) for k, g in keys]
        cs = sorted(set(M.GROUPS[g]["c"] for _, g in keys))
        I[s[0]] = ("sw", "Διακόπτης – %s" % ("1 πλήκτρο" if len(keys) == 1 else "%d πλήκτρα" % len(keys)), _cap(s[6]) + " · " + " · ".join(parts),
                   " · ".join(circ_txt(c) for c in cs), [g for _, g in keys])
    for l in M.WALL_LIGHTS:
        I[l[0]] = ("lt", "Φως τοίχου", _cap(l[8]), circ_txt(M.GROUPS[l[6]]["c"]), [l[6]])
    for d in M.DATA:
        I[d[0]] = ("data", "Λήψη data – %d × RJ45 Cat 6A" % d[4], _cap(d[7]), "ασθενή – σε αστέρα από το κέντρο ασθενών (ντουλάπα χωλ)", [])
    for t in M.TV:
        I[t[0]] = ("data", "Λήψη TV (κεραία)", "Ομοαξονικό από τη διανομή TV του κέντρου ασθενών", "ασθενή – από το κέντρο ασθενών (ντουλάπα χωλ)", [])
    for t in M.THERMOSTATS:
        I[t[0]] = ("oth", "Θερμοστάτης", _cap(t[6]) + " · κυκλώματα ενδοδαπέδιας " + " · ".join(t[5]), circ_txt("ΕΝ"), [])
    I[M.AC_CTRL[0]] = ("oth", "Χειριστήριο κλιματιστικού", _cap(M.AC_CTRL[4]), "καλώδιο επικοινωνίας από τη μονάδα ΚΜ1", [])
    for d in M.WALL_DEV:
        I[d[0]] = ("data" if d[6] == "data" else "oth", _cap(d[7].split(" – ")[0].split(" (")[0]), _cap(d[7]),
                   {"data": "ασθενή – από το κέντρο ασθενών", "alarm": "συναγερμός – από τον πίνακα συναγερμού (ντουλάπα χωλ)", "fire": "πυρανίχνευση – από τον πίνακα (ντουλάπα χωλ)"}[d[6]], [])
    for e in M.EMERGENCY:
        I[e[0]] = ("lt", "Φωτιστικό ασφαλείας", _cap(e[4]), "δικό του καλώδιο 3×1,5, χωρίς διακόπτη (περνά από την ΟΠ4)", [])
    for pid in M.FIRE_BOXES:                                # κουτιά μέσα στον πυράντοχο τοίχο της εισόδου
        k, t, d, c, lg = I[pid]
        I[pid] = (k, t, d + " · ΠΥΡΑΝΤΟΧΟ κουτί (τοίχος προς το κλιμακοστάσιο)", c, lg)
    return I


def build():
    RT.bind(M); DR.bind(M)
    bad = [r for r in RT.check() if r[1] != "OK"]
    assert not bad, "3D: υπάρχουν διαδρομές που δεν περνούν τον έλεγχο – δεν βγαίνει 3D: %s" % bad[:2]
    B = RT.build()
    out = dict(rev=M.REV, date=M.DATE, walls=[], cols=[], beams=[], holes=[], rooms=ROOMS)
    for w in W.WALLS:
        if G.is_rect(w["pts"]):
            b = W.bbox(w["pts"]); s = soffit_over((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            out["walls"].append([round(q, 3) for q in b] + [s or 2.78, "b" if w["type"] in DR.BRICK else ("g" if w["type"] == "T9" else ("l" if w["type"] == "T3" else "s"))])
    for p in W.COLS:
        if G.is_rect(p):
            out["cols"].append([round(q, 3) for q in W.bbox(p)])
    for b in A.BEAMS:
        out["beams"].append([b[0]] + list(b[2:6]) + [A.beam_soffit(b[1]), b[1]])
    for h in M.HOLES:
        r = [b for b in A.BEAMS if b[0] == h["beam"]][0][2:6]
        out["holes"].append(dict(id=h["id"], x=h["x"], y=h["y"], ax="y" if (r[2] - r[0]) > (r[3] - r[1]) else "x", z=2.73, use=h["use"]))
    out["zones"] = [[round(q, 3) for q in r] + [z["level"]] for z in A.ZONES for r in z["rects"]]
    K = getattr(M, "KOUT", None)                                                 # R15: κατακόρυφη παρειά του κούτελου δίπλα στη Δ3.1 (Υπν.2), από το +2,48 ως την οροφή του δωματίου
    out["vfaces"] = [[K["x0"], K["y0"], K["x1"], round(K["y0"] + 0.0125, 4), K["lv"], round([z["level"] for z in A.ZONES if z["id"] == "Ζ10"][0] + 0.0125, 4)]] if K else []
    out["furn"] = [[round(q, 3) for q in f[1]] + [f[2], f[3] if f[3] is not None else 2.46, f[0]] for f in RT._C["furn"]]
    out["doors"] = [[round(q, 3) for q in d] for d in RT._C["doors"]]
    mode = {d["id"]: d["mode"] for d in M.DROPS}
    out["trunks"] = [dict(id=t["id"], k=t["kind"], pts=_p3(t["pts"])) for t in B["trunks"]]

    # ---- χώροι: εσωτερικό, κουτί κοπής
    out["rooms3"] = []
    for rid, name, short, rects in ROOMS3:
        bb = [min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects)]
        out["rooms3"].append(dict(id=rid, name=name, short=short, rects=[_r4(r) for r in rects], box=_r4(bb), out=_outer(rid, bb)))
    out["rooms3"].append(dict(id=EX, name="Εξώστες", short="Εξώστες", rects=[], box=None, out=None))

    # ---- σημεία τοίχου: τι είναι, σε ποιον χώρο, από ποια τροφοδοσία
    info = point_info()
    dev = {d["id"]: d for d in B["devs"]}
    xtra = {e["id"]: e for e in B["extra"]}
    items, tails = [], {}
    for pid, x, y, d, h, kind, opt in RT.devices():
        assert pid in info, "3D: το σημείο %s δεν έχει περιγραφή" % pid
        k, t, s, c, lg = info[pid]
        rs = rooms_of(x, y, d)
        if pid in dev:
            g, f = dev[pid]["grp"], dev[pid]["feed"]
            tails[pid] = _p3(dev[pid]["pts"][dev[pid]["nfeed"] - 1:])
        else:
            assert pid in xtra, "3D: το σημείο %s δεν έχει διαδρομή" % pid
            g, f = xtra[pid]["grp"], None
        items.append(dict(id=pid, k=k, x=round(x, 3), y=round(y, 3), z=round(h, 3), d=d, rooms=rs, t=t, s=s, c=c, g=g, f=f, m=mode[g], lg=lg, w=1))
    # παροχές των μονάδων που δεν κάθονται σε τοίχο (υπέρθυρο / κενό οροφής) και επαφές συναγερμού: το άκρο της πρόσθετης διαδρομής τους
    for fid, x, y, circ, desc in M.FIXED_FREE:
        e = xtra[fid]["pts"][-1]
        items.append(dict(id=fid, k="sock", x=round(e[0], 3), y=round(e[1], 3), z=round(e[2], 3), d=None, rooms=EXTRA_ROOMS[fid][:1], t="Παροχή κλιματιστικού", s=_cap(desc),
                          c=circ_txt(circ), g=xtra[fid]["grp"], f=None, m=mode[xtra[fid]["grp"]], lg=[], w=1, x3=fid))
    for cid, win, x, y, z, grp, desc in M.CONTACTS:
        items.append(dict(id=cid, k="oth", x=x, y=y, z=z, d=None, rooms=EXTRA_ROOMS[cid], t="Μαγνητική επαφή συναγερμού – προεγκατάσταση", s="%s: %s" % (win, desc),
                          c="συναγερμός – από τον πίνακα συναγερμού (ντουλάπα χωλ)", g=grp, f=None, m=mode[grp], lg=[], w=1, x3=cid))
    no_room = [it["id"] for it in items if not it["rooms"]]
    assert not no_room, "3D: σημεία χωρίς χώρο: %s" % no_room

    # ---- οροφή: spots, ανιχνευτές, LED, μονάδες (θέσεις από το ίδιο μοντέλο – τα καλώδιά τους τρέχουν ελεύθερα στο κενό της οροφής, δεν σχεδιάζονται ένα-ένα)
    def lvl(x, y):
        z = RT.zone_at(x, y)
        return z[1] if z else None
    sw_of = {}
    for s in M.SWITCHES:
        for k, g in s[4]:
            sw_of.setdefault(g, []).append("%s (%s)" % (s[0], SW_TXT[k]))
    SK = {"s": "Χωνευτό spot", "s44": "Χωνευτό spot IP44", "s65": "Χωνευτό spot IP65 (ντους)"}
    for sp in M.SPOTS:
        nm, kind, x, y, g, role = sp[:6]
        z = lvl(x, y); r = room_at(x, y)
        assert z is not None and r, "3D: το spot %s δεν είναι κάτω από ζώνη οροφής / μέσα σε χώρο" % nm
        items.append(dict(id=nm, k="spot", x=x, y=y, z=z, d=None, rooms=[r], t=SK[kind], s="%s · ομάδα %s: %s · ανάβει από %s" % (
            _cap(role), g, M.GROUPS[g]["name"], ", ".join(sw_of.get(g, ["—"]))), c=circ_txt(M.GROUPS[g]["c"]), g=None, f=None, m=None, lg=[g], w=0))
    for sp in M.STAIR_SPOTS:
        z = lvl(sp[2], sp[3])
        items.append(dict(id=sp[0], k="spot", x=sp[2], y=sp[3], z=z or 2.73, d=None, rooms=["platyskalo"], t="Χωνευτό spot κλιμακοστασίου",
                          s="Κοινόχρηστος φωτισμός με αισθητήρα – ΔΕΝ είναι στον πίνακα του διαμερίσματος", c="κοινόχρηστος πίνακας", g=None, f=None, m=None, lg=[], w=0))
    for nm, x, y, g, desc in M.EXT_SPOTS:
        items.append(dict(id=nm, k="spot", x=x, y=y, z=Z_EXT_LAMP, d=None, rooms=[EX], t="Φωτιστικό οροφής εξώστη (επίτοιχο, στεγανό)", s="%s · ομάδα %s: %s · ανάβει από %s" % (
            _cap(desc), g, M.GROUPS[g]["name"], ", ".join(sw_of.get(g, ["—"]))), c=circ_txt(M.GROUPS[g]["c"]), g=None, f=None, m=None, lg=[g], w=0))
    for dt in M.DETECTORS:
        nm, kind, x, y, txt = dt[:5]
        items.append(dict(id=nm, k="det", x=x, y=y, z=lvl(x, y) or 2.68, d=None, rooms=[room_at(x, y)], t="Ανιχνευτής %s" % ("καπνού" if kind == "smoke" else "θερμοδιαφορικός"),
                          s=_cap(txt), c="πυρανίχνευση – βρόχος από τον πίνακα (ντουλάπα χωλ)", g=None, f=None, m=None, lg=[], w=0))
    for nm, x, y, txt in M.MOTION:
        items.append(dict(id=nm, k="det", x=x, y=y, z=lvl(x, y) or 2.68, d=None, rooms=[room_at(x, y)], t="Ανιχνευτής κίνησης συναγερμού", s=_cap(txt),
                          c="συναγερμός – από τον πίνακα συναγερμού (ντουλάπα χωλ)", g=None, f=None, m=None, lg=[], w=0))
    led_done = set()
    for l in M.LED:
        if l[0] in led_done:
            continue
        led_done.add(l[0])
        g = "θ" if l[0] == "LED3" else "ε2"
        mx, my = (l[1][0] + l[2][0]) / 2, (l[1][1] + l[2][1]) / 2
        items.append(dict(id=l[0], k="spot", x=round(mx, 3), y=round(my, 3), z=2.66 if l[0] == "LED3" else 1.43, d=None, rooms=[room_at(mx, my) or ("ypn1" if l[0] == "LED3" else "kouzina")],
                          t="Κρυφή ταινία LED", s="%s · ομάδα %s: %s · ανάβει από %s" % (_cap(l[4] or M.GROUPS[g]["name"]), g, M.GROUPS[g]["name"], ", ".join(sw_of.get(g, ["—"]))),
                          c=circ_txt(M.GROUPS[g]["c"]), g=None, f=None, m=None, lg=[g], w=0))
    P = M.PANEL
    items.append(dict(id=P["id"], k="pan", x=round(P["x"], 3), y=(P["y0"] + P["y1"]) / 2, z=(P["z0"] + P["z1"]) / 2, d=P["d"], rooms=["xol"], t="Γενικός πίνακας διαμερίσματος",
                      s=_cap(P["txt"]) + " · όλα τα καλώδια μπαίνουν από πάνω", c="παροχή %s από τον μετρητή, μέσω shaft" % M.FEEDER["cable"], g="1", f=None, m=None, lg=[], w=0))
    no_room = [it["id"] for it in items if not it["rooms"] or None in it["rooms"]]
    assert not no_room, "3D: σημεία οροφής χωρίς χώρο: %s" % no_room
    for it in items:
        if "x3" not in it and it["f"] is None:
            if it["id"] in xtra:
                it["x3"] = it["id"]
            elif it["id"].startswith("ΕΚ"):
                n = int(it["id"][2:])
                rng = [e for e in xtra if e.startswith("ΕΚ") and int(e[2:].split("-")[0]) <= n <= int(e[2:].split("-")[1])]
                assert len(rng) == 1, "3D: το φωτιστικό %s δεν έχει διαδρομή" % it["id"]
                it["x3"] = rng[0]
    for it in items:
        it["x"], it["y"], it["z"] = round(it["x"], 3), round(it["y"], 3), round(it["z"], 3)
    seen = set()                                           # u = μοναδικό κλειδί (το «Χ1» είναι ΚΑΙ spot του χωλ ΚΑΙ το χειριστήριο της ΚΜ1 – στη σελίδα φαίνεται το id)
    for it in items:
        it["u"] = it["id"] if it["id"] not in seen else "%s#%s" % (it["id"], it["k"])
        assert it["u"] not in seen, "3D: διπλό κλειδί σημείου %s" % it["u"]
        seen.add(it["u"])
    assert all(it["u"] == it["id"] for it in items if it["w"]), "3D: δύο σημεία τοίχου με το ίδιο όνομα"
    out["items"] = items
    out["tails"] = tails

    # ---- τροφοδοσίες τοίχων και πρόσθετες διαδρομές: σε ποιους χώρους φαίνονται
    by_feed = {}
    for it in items:
        if it["f"]:
            by_feed.setdefault(it["f"], set()).update(it["rooms"])
    out["feeds"] = [dict(id=f["id"], g=f["grp"], m=mode[f["grp"]], pts=_p3(f["feed"]), rooms=sorted(by_feed.get(f["id"], []))) for f in M.FEEDS]
    assert set(e["id"] for e in B["extra"]) == set(EXTRA_ROOMS), "3D: οι πρόσθετες διαδρομές άλλαξαν – ενημέρωσε το EXTRA_ROOMS"
    out["extra"] = []
    lamps = {}
    for nm, x, y, g, desc in M.EXT_SPOTS:
        lamps[(round(x, 3), round(y, 3))] = nm
    for e in B["extra"]:
        pts = [tuple(q[:3]) for q in e["pts"]]
        last = pts[-1]
        if (round(last[0], 3), round(last[1], 3)) in lamps and last[2] < Z_EXT_LAMP:       # φώτα εξωστών: η διαδρομή βγαίνει από το τούβλο κάτω από το δοκάρι –
            rise = [last + ("ext",), (last[0], last[1], Z_EXT_LAMP, "")]                    # από εκεί ανεβαίνει στην όψη ως το ταβάνι του εξώστη (ελέγχεται κι αυτό)
            assert not RT.check_path(rise), "3D: η άνοδος προς το φωτιστικό του εξώστη δεν γίνεται (%s)" % e["id"]
            pts.append(rise[1][:3])
        out["extra"].append(dict(id=e["id"], g=e["grp"], m=mode[e["grp"]], pts=_p3(pts), rooms=EXTRA_ROOMS[e["id"]], n=e["n"]))

    # ---- οι 17 τοίχοι (= τομές ΗΛ-14): τίτλος και τρόπος, για το πλαίσιο κάθε χώρου
    import el_sheets as SH
    out["nums"] = [[d["id"], SH.NUM_AT[d["id"]][0], SH.NUM_AT[d["id"]][1], d["mode"], d["title"]] for d in M.DROPS]
    out["drops"] = {d["id"]: dict(t=d["title"], how=d["how"], what=d.get("what", ""), txt=d["txt"]) for d in M.DROPS}
    out["groups"] = {g: dict(name=v["name"], c=v["c"], dim=v["dim"], sw=sw_of.get(g, [])) for g, v in M.GROUPS.items()}

    # ---- σταθερά της οροφής / του χώρου που δεν είναι «σημεία»: μονάδες A/C, LED, πίνακας, shaft, κουφώματα
    fx = dict(units=[], led=[], win=[], boxes=[])
    for u in A.UNITS:
        zid, lv, sb = [(z[0], z[1], z[2]) for z in RT._C["zones"] if z[0] == u["zone"]][0]      # (ζώνη, στάθμη οροφής, κάτω παρειά πλάκας)
        assert sb - u["hmax"] >= lv + 0.0125 - 1e-6, "3D: η καναλάτη δεν χωρά πάνω από την οροφή της"
        fx["units"].append(_r4(u["rect"]) + [round(sb - u["hmax"], 3), round(sb, 3), "%s καναλάτη %s" % (u["id"], u["btu"])])
    for s in A.SPLITS:
        fx["units"].append(_r4(s["rect"]) + [s["bottom"], round(s["bottom"] + s["h"], 3), "%s split %s" % (s["id"], s["btu"])])
    for l in M.LED:
        z = 2.66 if l[0] == "LED3" else 1.43
        fx["led"].append([l[0], l[1][0], l[1][1], l[2][0], l[2][1], z])
    fx["panel"] = [round(P["x"], 3), P["y0"], round(P["x"] + 0.03, 3), P["y1"], P["z0"], P["z1"]]
    fx["shaft"] = _r4(RT.SHAFT_SPACE)
    fx["boxes"].append(_r4(M.HP_RECT) + [0.0, 1.0, "Αντλία θερμότητας (ενδεικτικά)"])
    fx["boxes"].append(_r4(M.AC_OUT) + [1.05, 1.85, "Εξωτερική μονάδα A/C (ενδεικτικά)"])
    sizes = {round(s[1], 2): s[0] for s in W.WIN_SIZES}
    for p in W.WINS:
        b = W.bbox(p)
        L = round(max(b[2] - b[0], b[3] - b[1]), 2)
        nm = sizes.get(L) or min(W.WIN_SIZES, key=lambda s: abs(s[1] - L))[0]
        z0, z1 = WIN_SILL.get(nm, WIN_FULL)
        fx["win"].append(_r4(b) + [z0, z1, nm])
    fx["par"] = [_r4(W.bbox(q)) + [0.0, Z_PARAPET] for q in W.COLS2]
    fx["plate"] = plate(fx["win"])
    fx["loose"], fx["glass"] = loose()
    out["fx"] = fx
    out["nav"], stand = nav_grid(fx["win"])
    for r in out["rooms3"]:
        r["stand"] = stand[r["id"]]
    out["nchk"] = sum(1 for _ in RT.check())
    return out


TEMPLATE = open(os.path.join(M.HERE, "el_3d_template.html"), encoding="utf-8").read() if os.path.exists(os.path.join(M.HERE, "el_3d_template.html")) else ""
CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
# ο σκελετός με τον οποίο το claude.ai σερβίρει ένα artifact (μόνο για την τοπική δοκιμή – το αρχείο που δημοσιεύεται ΔΕΝ τον έχει)
SKEL = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}'
        'img{max-width:100%}[hidden]{display:none!important}</style></head><body>@@PAGE@@</body></html>')


def page(data):
    return TEMPLATE.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))


def report(data):
    """Τι έχει κάθε χώρος – για έλεγχο στο τερματικό. Επιστρέφει τον αριθμό των λαθών."""
    from collections import Counter
    bad = 0
    for r in data["rooms3"]:
        its = [it for it in data["items"] if r["id"] in it["rooms"]]
        c = Counter(it["k"] for it in its)
        print("  %-22s σημεία τοίχου %2d · οροφής %2d  %s  κουτί %s" % (r["name"], sum(it["w"] for it in its), sum(1 - it["w"] for it in its), dict(c), r["out"]))
        bad += 0 if its else 1
    feeds, extra = {f["id"] for f in data["feeds"]}, {e["id"] for e in data["extra"]}
    for it in data["items"]:
        if it["w"] and not ((it["f"] in feeds and it["u"] in data["tails"]) or it.get("x3") in extra):
            print("  ΛΑΘΟΣ: το σημείο %s δεν έχει διαδρομή στο 3D" % it["id"]); bad += 1
        if it["g"] and it["g"] not in data["drops"]:
            print("  ΛΑΘΟΣ: το σημείο %s δείχνει σε τοίχο %s που δεν υπάρχει στο ΗΛ-14" % (it["id"], it["g"])); bad += 1
    nv = data["nav"]
    print("  περιήγηση: %d κελιά %d cm που πατιούνται (%.1f m²) · όλοι οι χώροι και οι εξώστες φτάνονται από την είσοδο" % (nv["n"], round(nv["c"] * 100), nv["n"] * nv["c"] ** 2))
    print("3D ανά χώρο: %d σημεία (%d τοίχου με διαδρομή ως το κουτί, %d οροφής) σε %d προβολές · κάθε σημείο σε χώρο · %d ΛΑΘΟΣ" % (
        len(data["items"]), sum(it["w"] for it in data["items"]), sum(1 - it["w"] for it in data["items"]), len(data["rooms3"]), bad))
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    data = build()
    if "--check" in args:                       # μόνο έλεγχος των δεδομένων (τρέχει και από το code/qa/run_all.py)
        sys.exit(1 if report(data) else 0)
    if "--test" in args:                        # τοπική σελίδα δοκιμής: σκελετός του claude.ai + three.js από το repo (για το el_3d_test.js)
        dst = args[args.index("--test") + 1]
        vendor = os.path.abspath(os.path.join(M.HERE, "..", "loutra", "vendor", "three-r128.min.js"))
        open(dst, "w", encoding="utf-8").write(SKEL.replace("@@PAGE@@", page(data).replace(CDN, "file://" + vendor)))
        print("σελίδα δοκιμής →", os.path.normpath(dst))
        sys.exit(0)
    dst = args[0] if args else os.path.join(M.HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΚΑΤΕΒΑΣΜΑΤΑ_3D.html")
    assert CDN in TEMPLATE, "3D: το πρότυπο δεν φορτώνει το three.js από το cdnjs"
    open(dst, "w", encoding="utf-8").write(page(data))
    report(data)
    print("→", os.path.normpath(dst))
