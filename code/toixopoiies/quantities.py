"""Προμέτρηση υλικών τοιχοποιιών Β1 από το μοντέλο (παραδοχές όπως το R14, βλ. φύλλο Τ-03)."""
import math
import b1_model as M

H = M.H
STUD_STEP = 0.60

# παρειές που βλέπουν σε λουτρό (ανθυγρή γυψοσανίδα): id → πλήθος παρειών
BATH_SIDES = getattr(M, "BATH_SIDES", {"T2-01": 1, "T2-02": 1, "T2-03": 1, "T2-04": 1, "T2-08": 1, "T2A-01": 1,
              "T7-01": 1, "T7-02": 1})
# υπέρθυρα πορτών (H − 2,20 = 0,70 m) – προστίθενται στο είδος του τοίχου της πόρτας
LINTELS = getattr(M, "LINTELS", {"T2": 0.70 * (0.80 + 0.70 + 0.70 + 0.80), "T6A": 0.70 * 1.00})   # R22: Β1 πόρτα εισόδου 1,00 στον Τ6Α

BRICKS = {"T1": (16.7, 0.25, 0.06), "T4": (38.5, 0.11, 0.18), "T5": (16.7, 0.10, 0.06), "T10": (16.7, 0.25, 0.06)}  # τεμ/m², πάχος, συντ. κονιάματος
FRAMES = getattr(M, "FRAMES", {"T3": ["CW30"], "T2": ["CW50"], "T2N": ["CW50"], "T2A": ["CW100"], "T7": ["CW50", "CW30"], "T7A": ["CW50"],
          "T6": ["CW30", "CW30"], "T6A": ["CW100"], "T8": ["CW50"]})   # R22: Τ6 διπλός σκελετός CW 30 + κενό 5 + CW 30 (16 cm) σε όλους τους ορόφους
LAYERS = {"T3": 2, "T9": 1, "T2": 4, "T2N": 3, "T2A": 4, "T7": 4, "T7A": 4, "T6": 4, "T6A": 4, "T8": 2}


def studs(L):
    return math.ceil(L / STUD_STEP) + 1


def per_type(model=None):
    """R11: model = μοντέλο ορόφου (προεπιλογή το M του module) – για το ενιαίο φύλλο προμέτρησης ισογείου + Β1."""
    M = model or globals()["M"]
    H = M.H
    BATH_SIDES = getattr(M, "BATH_SIDES", globals()["BATH_SIDES"])
    LINTELS = getattr(M, "LINTELS", globals()["LINTELS"])
    FRAMES = getattr(M, "FRAMES", globals()["FRAMES"])
    rows = []
    for t in M.TYPE_ORDER:
        ws = M.walls_of(t)
        L = sum(M.wall_length(w) for w in ws)
        area = L * H + LINTELS.get(t, 0)
        r = dict(type=t, n=len(ws), ids=[w["id"] for w in ws], L=L, area=area,
                 gyp=0, gyp_h2=0, gyp_f=0, cw={}, uw={}, rock=0, bricks=0, mortar=0, glue=0)
        if t in BRICKS:
            k, th, mf = BRICKS[t]
            r["bricks"] = area * k; r["mortar"] = area * th * mf
        if t in LAYERS:
            lay = LAYERS[t]
            if t in ("T6", "T6A"):
                r["gyp_f"] = area * lay
            else:
                h2 = 0.0
                for w in ws:
                    sides = BATH_SIDES.get(w["id"], 0)
                    if sides:
                        a = M.wall_length(w) * H
                        h2 += a * 2 * sides if t != "T3" else a * 2
                # Τ7-01: πλευρά ντουλάπας 1 φύλλο (R15) → 3 φύλλα συνολικά
                total = area * lay
                if t == "T7":
                    total -= sum(M.wall_length(w) * H for w in ws if w["id"] == "T7-01")
                r["gyp_h2"] = min(h2, total); r["gyp"] = total - r["gyp_h2"]
            for fr in FRAMES.get(t, []):
                n = sum(studs(M.wall_length(w)) for w in ws)
                r["cw"][fr] = n * H
                r["uw"]["UW" + fr[2:]] = 2 * L
            if t in ("T2A", "T6A"):
                r["rock"] = area
        if t == "T9":
            r["glue"] = area * 4.0
        rows.append(r)
    return rows


def order_list(rows):
    g = sum(r["gyp"] for r in rows); h2 = sum(r["gyp_h2"] for r in rows) + 6.1; f = sum(r["gyp_f"] for r in rows)
    cw = {}; uw = {}
    for r in rows:
        for k, v in r["cw"].items(): cw[k] = cw.get(k, 0) + v
        for k, v in r["uw"].items(): uw[k] = uw.get(k, 0) + v
    rock = sum(r["rock"] for r in rows); glue = sum(r["glue"] for r in rows)
    gyp_total = g + h2 + f
    items = [
        ("Γυψοσανίδα κοινή 12,5 mm 1,20 × 3,00", g * 1.10, "m²", "%d φύλλα" % math.ceil(g * 1.10 / 3.6)),
        ("Γυψοσανίδα ανθυγρή (H2) 12,5 mm 1,20 × 3,00 – λουτρά: τοίχοι + οροφές (6,1 m² οροφές)", h2 * 1.10, "m²", "%d φύλλα" % math.ceil(h2 * 1.10 / 3.6)),
        ("Γυψοσανίδα πυράντοχη (F) 12,5 mm 1,20 × 3,00 – κλιμακοστάσιο", f * 1.10, "m²", "%d φύλλα" % math.ceil(f * 1.10 / 3.6)),
    ]
    for k in ["CW50", "CW30", "CW100"]:
        v = cw.get(k, 0) * 1.05; items.append(("Προφίλ %s (3,00 m)" % k, v, "m", "%d τεμ." % math.ceil(v / 3)))
    for k in ["UW50", "UW30", "UW100"]:
        v = uw.get(k, 0) * 1.05; items.append(("Προφίλ %s (3,00 m)" % k, v, "m", "%d τεμ." % math.ceil(v / 3)))
    items += [
        ("Προφίλ CD60 (3,00 m) – ψευδοροφές λουτρών", 20.4, "m", "7 τεμ."),
        ("Προφίλ UD28 (3,00 m) – ψευδοροφές λουτρών", 15.1, "m", "6 τεμ."),
        ("Πετροβάμβακας 50 / 100 mm (Τ2Α, Τ6)", rock, "m²", ""),
        ("Γυψόκολλα για κολλητή γυψοσανίδα (Τ9) ≈ 4 kg/m²", glue, "kg", "%d σακιά 25 kg" % math.ceil(glue / 25)),
        ("Βίδες γυψοσανίδας TN 25 / 35 ≈ 22 τεμ/m² φύλλου", gyp_total * 22, "τεμ.", "%d κουτιά 1.000" % math.ceil(gyp_total * 22 / 1000)),
        ("Στόκος αρμών ≈ 0,45 kg/m² τελικής επιφάνειας", gyp_total / 2 * 0.45, "kg", "%d σακιά 25 kg" % math.ceil(gyp_total / 2 * 0.45 / 25)),
        ("Ταινία αρμών ≈ 1,6 m/m² τελικής επιφάνειας", gyp_total / 2 * 1.6, "m", "%d ρολά 90 m" % math.ceil(gyp_total / 2 * 1.6 / 90)),
        ("Αναρτήσεις ψευδοροφής λουτρών (≈ 1,3 / m²)", 8, "τεμ.", ""),
    ]
    for r in rows:
        if r["type"] == "T1": items.append(("Θερμοτούβλο κάθετων οπών 25 (30 × 25 × 19) – Τ1", r["bricks"] * 1.05, "τεμ.", "+5 % σπασίματα"))
        if r["type"] == "T5": items.append(("Θερμοτούβλο κάθετων οπών 10 (30 × 10 × 19) – Τ5 πυρήνα", r["bricks"] * 1.05, "τεμ.", "+5 % σπασίματα"))
        if r["type"] == "T4": items.append(("Απλό τούβλο 6οπο 9 × 12 × 19 – Τ4 έρκερ", r["bricks"] * 1.05, "τεμ.", "+5 % σπασίματα"))
    items.append(("Κονίαμα δόμησης", sum(r["mortar"] for r in rows), "m³", ""))
    return items


def _poly_area(pts):
    a = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    return abs(a) / 2

# κουφώματα: (πλάτος, ύψος, ζώνη θερμοπρόσοψης)
WIN_SIZES = getattr(M, "WIN_SIZES", [("W2.01", 3.50, 2.40, 10), ("W2.02", 4.75, 2.40, 10), ("W2.03", 2.05, 0.50, 10), ("W2.04", 1.35, 0.50, 10),
             ("W2.05", 0.70, 1.35, 5), ("W2.06", 1.00, 2.40, 10), ("W2.07", 0.60, 0.90, 10), ("W2.08", 1.50, 2.40, 10),
             ("W2.09", 0.50, 1.30, 10)])
ETICS_H = M.H + 0.20   # ύψος ορόφου με τη μετώπη πλάκας

def etics_summary(model=None):
    """Μήκη από τα πολύγωνα (εμβαδόν / πάχος), καθαρά m² = μήκος × 3,10 − κουφώματα + λαμπάδες (0,11 × περίμετρος)."""
    M = model or globals()["M"]
    WIN_SIZES = getattr(M, "WIN_SIZES", globals()["WIN_SIZES"])
    ETICS_H = M.H + 0.20
    out = []
    for th, polys in ((0.10, M.ETICS), (0.05, M.ETICS5)):
        L = sum(_poly_area(p) for p in polys) / th
        wins = [w for w in WIN_SIZES if w[3] == int(th * 100)]
        wa = sum(w * h for _, w, h, _ in wins); rev = sum(2 * (w + h) for _, w, h, _ in wins) * 0.11
        L += sum(w for _, w, _, _ in wins)            # οι λωρίδες της κάτοψης κόβονται στα κουφώματα → μήκος όψης με τα κουφώματα
        gross = L * ETICS_H; net = gross - wa + rev
        out.append(dict(th=th, L=L, gross=gross, wins=wa, rev=rev, net=net, n_win=len(wins)))
    return out

ETICS = [  # όπως R14 (τα κουφώματα δεν άλλαξαν διαστάσεις) – ΜΟΝΟ 10 cm, δεν χρησιμοποιείται πλέον στο Τ-03
    ("Περίμετρος όψεων", "47,76 m"), ("Κουφώματα (9 ανοίγματα)", "−29,61 m²"),
    ("Λαμπάδες + ανώφλια (βάθος ≈ 0,15)", "+6,63 m²"), ("ΚΑΘΑΡΗ ΕΠΙΦΑΝΕΙΑ", "125,1 m²"),
    ("Πλάκα EPS γραφιτούχο 10 cm (+5 %) · 263 πλ. 1,00×0,50", "131,3 m²"),
    ("Κόλλα – βασικός σοβάς ≈ 9 kg/m² · 46 σακιά", "1.126 kg"),
    ("Υαλόπλεγμα 160 g ≈ 1,15 m²/m² · 3 ρολά 50 m²", "143,8 m²"),
    ("Βύσματα ETICS ≈ 6 / m²", "750 τεμ."), ("Γωνιόκρανα με πλέγμα (κουφώματα)", "46,4 m"),
    ("Αστάρι ≈ 0,25 kg/m²", "31 kg"), ("Τελικός σοβάς ≈ 2,5 kg/m²", "313 kg"),
]

ASSUMPTIONS = [
    "Γυψοσανίδες 12,5 mm σε φύλλα 1,20 × 3,00 (ένα φύλλο καθ' ύψος για H = 2,90). Ανθυγρή όπου η πλευρά βλέπει λουτρό / WC, πυράντοχη στον Τ6.",
    "Ορθοστάτες CW ανά 60 cm (+1 ανά τοίχο), οδηγοί UW δάπεδο + οροφή. Τ7: δύο σκελετοί (CW 50 + CW 30). Τ3: σκελετός 3άρι μίας πλευράς. Τ9: χωρίς σκελετό, σε γυψόκολλα.",
    "R15/R16: στην πλευρά ντουλάπας ένα φύλλο (Τ2N-01, Τ2N-02, Τ7-01 προς Υπν.1) – αφαιρέθηκε από τα m² γυψοσανίδας.",
    "Υπέρθυρα πάνω από τις πόρτες (H − 2,20) προστέθηκαν στο είδος του τοίχου της πόρτας: 5 πόρτες.",
    "Τούβλα: Τ1 / Τ5 θερμομονωτικά κάθετων οπών (30 × 19 → ≈ 16,7 τεμ/m²) · Τ4 έρκερ απλό τούβλο 6οπο 9 × 12 × 19 δρομικό (≈ 38,5 τεμ/m²). ΠΡΟΣ ΕΠΙΒΕΒΑΙΩΣΗ οι διαστάσεις του προμηθευτή.",
    "ΛΟΥΤΡΑ: ό,τι είναι μέσα στο λουτρό (τοίχοι και οροφή) με ανθυγρή. Ψευδοροφές λουτρών: 1 × ανθυγρή 12,5 σε CD 60 / UD 28 (Λουτρό 3,06 m² · Λουτρό Γονέων 3,02 m²). Λοιπές ψευδοροφές στο τεύχος ανόψεων.",
    "Δεν περιλαμβάνονται: σοβάδες, πλακάκια, γωνιόκρανα γυψοσανίδας, κάσες / πρέκια, ηχομονωτικές ταινίες περιμέτρου.",
    "Όπου πλακάκι ή ντουλάπα: χωρίς γυψοσανίδα σε τούβλο / μπετό – ήδη εξαιρέθηκαν από την προμέτρηση.",
]

if __name__ == "__main__":
    rows = per_type()
    for r in rows:
        print(r["type"], r["n"], round(r["L"], 2), round(r["area"], 1), round(r["gyp"], 1), round(r["gyp_h2"], 1), round(r["gyp_f"], 1),
              {k: round(v, 1) for k, v in r["cw"].items()}, {k: round(v, 1) for k, v in r["uw"].items()}, round(r["rock"], 1), round(r["bricks"]), round(r["mortar"], 2), round(r["glue"], 1))
    for it in order_list(rows):
        print(it)
