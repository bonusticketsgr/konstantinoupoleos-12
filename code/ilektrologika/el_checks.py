"""Έλεγχοι και προμέτρηση της ηλεκτρολογικής μελέτης (τρέχουν μέσα στο build – πρέπει 0 ΛΑΘΟΣ).

    python3 el_checks.py            → τυπώνει τον έλεγχο του Β1

Ομάδες: Τοίχος (κάθε σημείο κάθεται σε παρειά τοίχου που δέχεται κουτί – ποτέ σε σκυρόδεμα) · Πόρτα (όχι πίσω από ανοιχτό φύλλο, ο διακόπτης στην
πλευρά της κλειδαριάς) · Έπιπλο (όχι πίσω από ντουλάπα) · Λουτρό (ζώνες ΕΛΟΤ 60364-7-701) · Δοκός (καμία όδευση κάτω από δοκό – μόνο στις διελεύσεις) ·
Κύκλωμα (In ≤ Iz, φορτίο ≤ In) · Πίνακας (φάσεις, αιχμή, θέσεις, εφεδρεία, χωρά στον τοίχο) · Συντονισμός (ανόψεις, αποστάσεις κουτιών)."""
import math, sys, os
import el_geom as G

M = None      # μοντέλο ηλεκτρολογικών (b1_el)
W = None      # τοιχοποιίες
A = None      # ανόψεις


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A
    return model


def _f(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",")


# ---------------------------------------------------------------- όλα τα εντοιχισμένα σημεία σε μία λίστα
def wall_points():
    """[(id, x, y, d, ύψος, είδος, επιλογές)] – ό,τι θέλει κουτί σε τοίχο."""
    out = []
    for s in M.SOCKETS:
        opt = s[10] if len(s) > 10 else {}
        out.append((s[0], s[1], s[2], s[3], s[6], "ρευματοδότης", opt))
    for f in M.FIXED:
        out.append((f[0], f[1], f[2], f[3], f[4], "παροχή", {}))
    for s in M.SWITCHES:
        opt = s[7] if len(s) > 7 else {}
        out.append((s[0], s[1], s[2], s[3], opt.get("h", M.H_SW), "διακόπτης", opt))
    for sh in M.SHUTTERS:
        out.append(("ρολό " + sh["win"], sh["motor"][0], sh["motor"][1], sh["motor"][2], M.H_HI, "παροχή ρολού", {}))
    for l in M.WALL_LIGHTS:
        out.append((l[0], l[1], l[2], l[3], l[5], "φωτιστικό τοίχου", {}))
    for d in M.DATA:
        out.append((d[0], d[1], d[2], d[3], d[5], "λήψη data", {}))
    for t in M.TV:
        out.append((t[0], t[1], t[2], t[3], t[4], "λήψη TV", {}))
    for t in M.THERMOSTATS:
        out.append((t[0], t[1], t[2], t[3], M.H_TH, "θερμοστάτης", {}))
    out.append((M.AC_CTRL[0], M.AC_CTRL[1], M.AC_CTRL[2], M.AC_CTRL[3], M.H_TH, "χειριστήριο", {}))
    for d in M.WALL_DEV:
        out.append((d[0], d[1], d[2], d[3], d[5], "συσκευή τοίχου", {}))
    return out


SHOWER_HEADS = {"ΛΟΥ": (5.05, 1.285), "ΛΓ": (0.11, 4.415)}       # θέση κεφαλής ντους (τεύχος λουτρών R02)
BATH_RECT = {"ΛΟΥ": [(5.05, 0.80, 6.399, 3.25)], "ΛΓ": [(0.11, 3.16, 1.049, 5.05), (1.049, 3.50, 3.149, 5.05)]}
INSIDE_OK = {"Π11", "Π12", "Π13", "Π14"}                          # μέσα στην εσοχή του πλυντηρίου / στην τεχνική ντουλάπα – εκεί ανήκουν
DOOR_SW = {"Δ1": 4, "Δ7": 0, "Δ11": 3, "Δ6": 1, "Δ10": 2}         # διακόπτης πόρτας → δείκτης στο W.DOORS


def run():
    R = []

    def add(grp, code, st, txt):
        R.append((grp, code, st, txt))

    pts = wall_points()
    # ---- Τοίχος
    for pid, x, y, d, h, kind, opt in pts:
        if opt.get("surf"):
            add("Τοίχος", pid, "OK", "%s επιφανειακά μέσα σε ερμάριο / έπιπλο – κανένα κουτί στον τοίχο" % kind)
            continue
        what, wid, typ = G.face_of(W, x, y, d)
        if what is None:
            add("Τοίχος", pid, "ΛΑΘΟΣ", "%s (%s / %s → %s): δεν κάθεται σε παρειά τοίχου του μοντέλου" % (kind, _f(x, 3), _f(y, 3), d))
        elif what == "col" or typ in G.BOX_NO:
            add("Τοίχος", pid, "ΛΑΘΟΣ", "%s πάνω σε ΣΚΥΡΟΔΕΜΑ (%s) – δεν χωρά κουτί" % (kind, wid))
        elif typ == "T6A" and not (opt.get("fire") or pid in M.FIRE_BOXES):
            add("Τοίχος", pid, "ΛΑΘΟΣ", "%s στον πυράντοχο τοίχο %s χωρίς πρόβλεψη πυράντοχου κουτιού" % (kind, wid))
        else:
            add("Τοίχος", pid, "OK", "%s στον %s (%s)%s" % (kind, wid.replace("T", "Τ"), G.BOX_OK.get(typ, typ), " – πυράντοχο κουτί" if opt.get("fire") else ""))
    # ---- Πόρτα
    for pid, x, y, d, h, kind, opt in pts:
        for i, door in enumerate(W.DOORS):
            if G.leaf_covers(door, x, y):
                add("Πόρτα", pid, "ΛΑΘΟΣ", "%s πίσω από το ανοιχτό φύλλο της πόρτας #%d" % (kind, i + 1))
    for sid, di in DOOR_SW.items():
        s = [q for q in M.SWITCHES if q[0] == sid][0]
        door = W.DOORS[di]
        dj = math.hypot(s[1] - door[2][0], s[2] - door[2][1]); dh = math.hypot(s[1] - door[0][0], s[2] - door[0][1])
        ok = dj < dh and dj <= 0.45
        add("Πόρτα", sid, "OK" if ok else "ΛΑΘΟΣ", "διακόπτης στην πλευρά της κλειδαριάς, %s m από την παραστάδα (άρθρωση στα %s m)" % (_f(dj), _f(dh)))
    # ---- Έπιπλο
    for pid, x, y, d, h, kind, opt in pts:
        if pid in INSIDE_OK or opt.get("surf"):
            continue
        for wd in W.WARDROBES:
            r = wd["r"]
            if G.in_rect(x, y, r, tol=-0.005) or (G.in_rect(x, y, r, tol=0.012) and not wd.get("joinery") and _faces_into(x, y, d, r)):
                add("Έπιπλο", pid, "ΛΑΘΟΣ", "%s πίσω από «%s»" % (kind, wd["name"]))
    add("Έπιπλο", "ΝΤΟΥΛ", "OK", "κανένα σημείο πίσω από ντουλάπα / πλυντήριο (εκτός από όσα ανήκουν στην εσοχή πλυντηρίου και στην τεχνική ντουλάπα)")
    # ---- Λουτρό
    for s in M.SOCKETS:
        if s[8] in SHOWER_HEADS:
            hx, hy = SHOWER_HEADS[s[8]]
            dist = math.hypot(s[1] - hx, s[2] - hy)
            add("Λουτρό", s[0], "OK" if dist >= 1.20 else "ΛΑΘΟΣ", "%s m από την κεφαλή του ντους (ζώνη 1 = 1,20 m) · IP44 · ΔΔΡ 30 mA" % _f(dist))
    for s in M.SWITCHES:
        for k, rs in BATH_RECT.items():
            if any(G.in_rect(s[1], s[2], r, tol=-0.02) for r in rs):
                add("Λουτρό", s[0], "ΛΑΘΟΣ", "διακόπτης μέσα στο λουτρό")
    add("Λουτρό", "ΔΙΑΚ", "OK", "οι διακόπτες των λουτρών έξω από την πόρτα· μέσα στα λουτρά μόνο ρευματοδότης καθρέπτη, φωτιστικά IP44 / IP65 και πρόβλεψη πετσετοκρεμάστρας")
    # ---- Διαδρομή (R14): κάθε καλώδιο είναι πραγματική διαδρομή σε 3D, ελεγμένη ανά 1 cm – ποτέ μέσα σε μπετό, ποτέ κάτω από δοκάρι με οροφή περασιά
    import el_route as RT
    RT.bind(M)
    for code, st, txt_ in RT.check():
        add("Διαδρομή", code, st, txt_)
    vf = RT.visible_faces()
    add("Διαδρομή", "ΟΡΑΤΟ", "ΛΑΘΟΣ" if vf else "OK", ("κουτιά χωρίς ορατή παρειά 8 cm: " + " · ".join("%s (%s)" % q for q in vf)) if vf else
        "κάθε κουτί έχει ορατή παρειά τοίχου 8 cm (κανένα πίσω από άλλον τοίχο / κολόνα ή μέσα σε άνοιγμα πόρτας)")
    for code, st, txt_ in RT.ceiling_reach():
        add("Διαδρομή", code, st, txt_)
    for p in M.PASSES:
        hit = [b[0] for b in A.BEAMS if not (p["rect"][2] <= b[2] or p["rect"][0] >= b[4] or p["rect"][3] <= b[3] or p["rect"][1] >= b[5])]
        add("Πέρασμα", p["id"], "OK" if hit else "ΛΑΘΟΣ", "%s · %s – %s%s" % (p["beam"], p["n"], p["title"], " · ΟΠΕΣ ΣΤΟ ΚΑΛΟΥΠΙ (ξυλότυποι)" if p["new"] else ""))
    z9 = [z for z in A.ZONES if z["id"] == "Ζ9"][0]
    soff = [A.beam_soffit(b[1]) for b in A.BEAMS if b[0] == "Δ3.1"][0]
    z4 = [z for z in A.ZONES if z["id"] == "Ζ4"][0]
    add("Πέρασμα", "ΧΩΛ-2,48", "OK" if abs(z9["level"] - soff) < 0.002 and abs(z4["level"] - soff) < 0.002 else "ΛΑΘΟΣ", "ΟΛΟ το χωλ και το άνοιγμα χωλ → σαλόνι στο +%s, περασιά με το δοκάρι Δ3.1 "
        "(ιδιοκτήτης 20/11) – κανένα δόντι στο άνοιγμα· τα καλώδια περνούν από τις οπές ΟΠ5 / ΟΠ1" % _f(z4["level"]))
    K = M.KOUT
    kz = [z for z in A.ZONES if z["id"] == "Ζ15"][0]; sbk = A.SLABS[kz["slab"]]
    b31 = [b for b in A.BEAMS if b[0] == "Δ3.1"][0]
    okk = abs(K["y1"] - b31[3]) < 0.002 and abs(kz["level"] - soff) < 0.002 and K["clear"] >= 0.15 - 1e-6 and not any(
        G.in_rect(x_, K["y0"] + 0.02, W.bbox(p_), tol=-0.002) for p_ in W.COLS for x_ in (K["x0"] + 0.05, (K["x0"] + K["x1"]) / 2, K["x1"] - 0.05))
    add("Πέρασμα", "ΚΟΥΤΕΛΟ", "OK" if okk else "ΛΑΘΟΣ", "κούτελο γυψοσανίδας κολλητά στη βόρεια παρειά της Δ3.1, στο Υπν.2 σε όλο το πλάτος του (x %s–%s): κενό %s cm καθαρό × %s cm ύψος "
        "(+%s ως την πλάκα +%s) · κάτω παρειά +%s = κάτω παρειά του δοκαριού · με σκελετό και φύλλο βγαίνει %s cm από το δοκάρι (ιδιοκτήτης 20/11: «κενό πάχους 15 και ύψους 30»)"
        % (_f(K["x0"]), _f(K["x1"], 3), _f(K["clear"] * 100, 0), _f((sbk - kz["level"]) * 100, 0), _f(kz["level"]), _f(sbk), _f(kz["level"]), _f((K["y1"] - K["y0"]) * 100, 0)))
    wn = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] in ("T2-04", "T2N-01", "T2-06")]
    add("Πέρασμα", "ΤΟΙΧΟΣ-Δ3.1", "OK" if all(abs(b[3] - 5.15) < 0.002 for b in wn) else "ΛΑΘΟΣ", "ο βόρειος τοίχος του καθιστικού ΟΠΩΣ οι τοιχοποιίες %s: παρειά στο 5,15, περασιά με τη δοκό Δ3.1 – "
        "κανένα κανάλι, καμία αλλαγή τοιχοποιίας" % W.REV)
    z6 = [z for z in A.ZONES if z["id"] == "Ζ6"][0]
    d8 = [d_ for d_ in M.DROPS if "T2-04" in d_["walls"]][0]
    add("Πέρασμα", "Τ2-04", "OK" if d8["mode"] == "via" else "ΛΑΘΟΣ", "δυτικό μισό του βόρειου τοίχου του σαλονιού: η οροφή του λουτρού γονέων (+%s) είναι μόνο %s cm κάτω από τη δοκό – ΔΕΝ περνά καλώδιο εκεί· "
        "ο τοίχος τροφοδοτείται ΜΕΣΑ από τον τοίχο του πίνακα, οριζόντια στο +%s (R14)" % (_f(z6["level"]), _f((soff - z6["level"] - 0.0125) * 100, 1), _f(M.ZR)))
    H = holes()
    for h in H:
        notes = []
        st = "OK"
        if not h["ok_z"]:
            st = "ΟΡΙΑΚΟ" if h["under"] <= 0.0201 and h["over"] <= 1e-6 else "ΛΑΘΟΣ"
            notes.append("το κάτω μέρος της οπής πέφτει %s cm μέσα στο φύλλο της οροφής του %s (+%s) → η οροφή εκεί 2 cm χαμηλότερα" % (_f(h["under"] * 100, 2), h["lo_room"], _f(h["lo"] - 0.0125)))
        if not (h["ok_d"] and h["ok_sup"] and h["ok_fill"] and h["ok_sp"] and h["ok_pair"]):
            st = "ΛΑΘΟΣ"
        add("Οπή δοκού", h["id"], st, "%s %s · χιτώνιο Ø%d · κέντρο +%s = μέση του ύψους (%s cm κάτω από την άνω στάθμη της πλάκας) · %s m από τη στήριξη (≥ %s) · Ø / ύψος = 1/%s · "
            "%s: %d καλώδια, πληρότητα %d %% (≤ %d) · %s → %s · χώρος πάνω από τις οροφές +%s … +%s%s"
            % (h["beam"], h["sec"], M.HOLE_D * 1000, _f(h["z"]), _f(h["h"] * 50, 0), _f(h["dsup"]), _f(1.5 * h["h"]), _f(h["h"] / M.HOLE_D, 1), h["use"], h["ncab"], round(h["fill"] * 100),
               M.HOLE_FILL * 100, h["frm"], h["to"], _f(h["lo"], 3), _f(h["hi"]), (" · " + " · ".join(notes)) if notes else ""))
    for bn in sorted(set(h["beam"] for h in H)):
        hb = [h for h in H if h["beam"] == bn]
        mixed = [h_["id"] for h_ in hb if {"P", "W"} <= set(l_[3] for l_ in h_["lines"])]
        add("Οπή δοκού", "ΑΣΘΕΝΗ-" + bn, "OK" if not mixed else "ΛΑΘΟΣ",
            "%s: %d οπές, ανά %s m (≥ 3 Ø = 22,5 cm) · κανένα ασθενές καλώδιο γυμνό μέσα σε χιτώνιο με ισχυρά – όπου συνυπάρχουν είναι σε δικό του σπιράλ (%s)"
            % (bn, len(hb), _f(min(h["sp"] for h in hb), 2), " · ".join("%s %s" % (h["id"], h["use"].lower()) for h in hb)))
    import math as _m
    c = M.COND
    hc = [h for h in H if h["id"] == c["hole"]][0]
    L = sum(_m.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(c["route"], c["route"][1:]))
    z_unit = c["slab"] - c["d"]                                         # ροή στην κορυφή της ανύψωσης, κολλητά στην πλάκα
    z_in = z_unit - c["slope"] * L                                      # ροή όταν φτάνει στο δοκάρι
    lo, hi = hc["z"] - M.HOLE_IN / 2, hc["z"] + M.HOLE_IN / 2 - c["d"]
    add("Συμπυκνώματα", "ΚΜ1-" + c["hole"], "OK" if lo - 1e-6 <= z_in <= hi + 1e-6 else "ΛΑΘΟΣ", "Ø32 από την αντλία του μηχανήματος: ροή +%s κολλητά στην πλάκα → %s m με 1 %% → +%s στο δοκάρι · "
        "μέσα στο χιτώνιο χωρά με ροή από +%s ως +%s" % (_f(z_unit, 3), _f(L), _f(z_in, 3), _f(lo, 3), _f(hi, 3)))
    need = c["ceil_liv"] + 0.0125 + c["ins"]
    add("Συμπυκνώματα", "ΚΜ1-ΛΩΡΙΔΑ", "OK" if z_in >= need - 1e-6 else "ΛΑΘΟΣ", "κενό της λωρίδας εισόδου (οροφή +%s): ο Ø32 με μόνωση 9 mm θέλει ροή ≥ +%s · έχει +%s στο χαμηλότερο σημείο"
        % (_f(c["ceil_liv"]), _f(need, 3), _f(z_in, 3)))
    sy = [t for t in M.TRUNKS3 if t["id"] == "ΣΥ"][0]["pts"]
    runs = [(a_, b_) for a_, b_ in zip(sy, sy[1:]) if _m.hypot(b_[0] - a_[0], b_[1] - a_[1]) > 0.02]
    slopes = [(a_[2] - b_[2]) / _m.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in runs]
    kr = [(a_, b_) for a_, b_ in runs if abs(a_[1] - b_[1]) < 1e-6 and abs(a_[1] - (K["y1"] - K["clear"] / 2)) < 0.002]
    Lk = sum(abs(a_[0] - b_[0]) for a_, b_ in kr); zend = min(b_[2] for a_, b_ in kr)
    in_k = sum(max(0.0, min(max(a_[0], b_[0]), K["x1"]) - max(min(a_[0], b_[0]), K["x0"])) for a_, b_ in kr)
    needk = kz["level"] + 0.0125 + c["ins"]
    okc = bool(kr) and min(slopes) >= 0.0099 and zend >= needk - 1e-6 and c["d"] + 2 * c["ins"] <= K["clear"] - 0.04 and all(h_["id"] != "ΟΠ1" or not any("αποχέτευση" in l_[0] for l_ in h_["lines"]) for h_ in M.HOLES)
    add("Συμπυκνώματα", "ΚΜ1-ΚΟΥΤΕΛΟ", "OK" if okc else "ΛΑΘΟΣ", "μετά την ΟΠ2 ο Ø32 τρέχει κολλητά στη βόρεια παρειά του δοκαριού: %s m μέσα στο κούτελο του Υπν.2 και %s m στο κενό του χωλ, κλίση παντού ≥ 1 %% "
        "(στη λωρίδα %s %%, μετά την ΟΠ2 2,6 %%) · ροή +%s στην ΟΠ2 → +%s πάνω από το πλυντήριο (θέλει ≥ +%s, περιθώριο %s cm) · με τη μόνωση Ø%d mm μέσα σε κενό %d cm"
        % (_f(in_k), _f(Lk - in_k), _f(min(slopes) * 100, 1), _f(max(a_[2] for a_, b_ in kr), 3), _f(zend, 3), _f(needk, 3), _f((zend - needk) * 100, 1), round((c["d"] + 2 * c["ins"]) * 1000), round(K["clear"] * 100)))
    ka, kb = max(kr, key=lambda q: abs(q[0][0] - q[1][0]))
    cl = []
    for h_ in H:
        if h_["beam"] == "Δ3.1" and h_["id"] != c["hole"] and min(ka[0], kb[0]) <= h_["x"] <= max(ka[0], kb[0]):
            zt = ka[2] + (kb[2] - ka[2]) * (h_["x"] - ka[0]) / (kb[0] - ka[0]) + c["d"] + c["ins"]
            cl.append((h_["id"], (h_["z"] - M.HOLE_D / 2) - zt))
    add("Συμπυκνώματα", "ΚΜ1-ΣΤΟΜΙΑ", "OK" if cl and min(q[1] for q in cl) >= 0.01 - 1e-6 else "ΛΑΘΟΣ", "στο χωλ ο Ø32 περνά μπροστά από τα χιτώνια %s: με τη μόνωσή του μένει %s cm ΚΑΤΩ από το κάτω άκρο τους – "
        "τα καλώδια βγαίνουν ελεύθερα από πάνω του" % (" · ".join(q[0] for q in cl), " · ".join(_f(q[1] * 100, 1) for q in cl)))
    add("Συμπυκνώματα", "ΚΜ1-ΚΑΤΕΒΑΣΜΑ", "OK" if G.in_rect(c["drop"][0], c["drop"][1], c["drop_in"]) else "ΛΑΘΟΣ",
        "πέφτει μέσα στην εσοχή του πλυντηρίου (όχι σε σκυρόδεμα, όχι στο πάτωμα) → σιφώνι πλυντηρίου")
    for fr in M.FLOOR_RUNS:                                             # R13: στο δάπεδο ΜΟΝΟ ό,τι αποφάσισε ο ιδιοκτήτης
        hit = [k for k, p in enumerate(W.COLS) if G.is_rect(p) and any(G.seg_hits_rect(a_, b_, W.bbox(p)) for a_, b_ in zip(fr["pts"], fr["pts"][1:]))]
        dmax = max(t[1] for t in fr["tubes"]) / 1000.0
        okf = not hit and dmax <= M.SCREED - 0.03
        add("Πέρασμα", "ΔΑΠΕΔΟ " + fr["id"], "ΛΑΘΟΣ" if not okf else "OK",
            "%s: %s πάνω στην πλάκα, %s m, μέσα στο γέμισμα %s cm · %s" % (fr["short"].split(":")[0], " + ".join("Ø%d" % t[1] for t in fr["tubes"]), _f(G.path_len(fr["pts"]), 1),
            _f(M.SCREED * 100, 0), "απόφαση ιδιοκτήτη 20/11" if fr["id"] == "Δ-TV" else "δεν υπάρχει άλλο πέρασμα (ιδιοκτήτης 20/11: «αν δεν σου βγαίνει πήγαινε από πάτωμα»)"))
    import el_drops as DR
    DR.bind(M)
    covered = set(w_ for d_ in M.DROPS for w_ in d_["walls"])
    for d_ in M.DROPS:
        e_ = DR.env(d_); okd, vd, gap = DR.verdict(d_, e_)
        lazy = d_["mode"] in ("via", "back", "floor", "out") and not e_["over"]            # δηλώνεται πλάγιος τρόπος ενώ ο τοίχος δεν είναι καν κάτω από δοκάρι
        add("Κατέβασμα", "ΤΟΜΗ " + d_["id"], "ΛΑΘΟΣ" if (not okd or lazy) else "OK", "%s (%s): %s" % (d_["title"], " · ".join(d_["walls"]), vd))
    miss = sorted(set(G.face_of(W, p[1], p[2], p[3])[1] for p in wall_points()) - covered - {None})
    add("Κατέβασμα", "ΚΑΛΥΨΗ", "OK" if not miss else "ΛΑΘΟΣ", "κάθε τοίχος με πρίζα / διακόπτη έχει τομή κατεβάσματος στο ΗΛ-14" + ((" – ΛΕΙΠΟΥΝ: " + ", ".join(miss)) if miss else ""))
    add("Πέρασμα", "ΠΛΑΚΑ", "OK", "κανένας σωλήνας μέσα σε πλάκα ή δοκό – όλα τα περάσματα γίνονται μετά τη σκυροδέτηση")
    # ---- Κύκλωμα
    for c in M.CIRCUITS:
        sec = c["cable"].split("×")[1]
        loaded = 3 if c["ph"] == "3Φ" else 2
        iz = M.IZ[(sec, loaded)]
        ib = c["P"] * 1000 / (400 * math.sqrt(3) if c["ph"] == "3Φ" else 230)
        st = "OK" if (c["In"] <= iz and ib <= c["In"] + 1e-6) else "ΛΑΘΟΣ"
        add("Κύκλωμα", c["id"], st, "%s %s%d · %s mm² Iz %s A · φορτίο %s kW → %s A" % (c["ph"], c["curve"], c["In"], c["cable"], _f(iz, 1), _f(c["P"], 2), _f(ib, 1)))
    # ---- Πίνακας
    ph = phases()
    mx, mn = max(ph.values()), min(ph.values())
    add("Πίνακας", "ΦΑΣΕΙΣ", "OK" if (mx - mn) / mx <= 0.20 else "ΛΑΘΟΣ",
        "αιχμή ανά φάση L1 %s · L2 %s · L3 %s kW – ασυμμετρία %d %%" % (_f(ph["L1"], 1), _f(ph["L2"], 1), _f(ph["L3"], 1), round((mx - mn) / mx * 100)))
    tot = sum(ph.values()) * M.DIVERSITY; imax = mx * M.DIVERSITY * 1000 / 230
    add("Πίνακας", "ΑΙΧΜΗ", "OK" if imax <= M.FEEDER["In"] else "ΛΑΘΟΣ",
        "εγκατεστημένα %s kW · άθροισμα αιχμών κυκλωμάτων %s kW · με ετεροχρονισμό %s → %s kW · ρεύμα στη φορτισμένη φάση %s A ≤ %d A (η φόρτιση οχήματος είναι στον πίνακα της αποθήκης, με διαχείριση φορτίου – παίρνει ό,τι περισσεύει)"
        % (_f(installed(), 1), _f(sum(ph.values()), 1), _f(M.DIVERSITY), _f(tot, 1), _f(imax, 1), M.FEEDER["In"]))
    T = circuit_table(); FL = feeder_lengths()
    dul = max(r["du"] for r in T if r["c"]["id"].startswith("Φ")); duo = max(r["du"] for r in T if not r["c"]["id"].startswith("Φ"))
    for q in FL:
        okv = q["du"] + dul <= 3.0 and q["du"] + duo <= 5.0
        add("Πίνακας", "ΠΤΩΣΗ-" + q["fl"], "OK" if okv else "ΛΑΘΟΣ", "παροχή %s: μετρητής → αποθήκη %s %s m → πίνακας σπιτιού %s m = %s m · %d A → %s %% · με το χειρότερο κύκλωμα: φωτισμός %s %% ≤ 3 · λοιπά %s %% ≤ 5"
            % (M.FEEDER["cable"].split()[-2], q["st"], _f(q["L1"], 0), _f(q["L2"], 0), _f(q["L"], 0), M.FEEDER["In"], _f(q["du"], 2), _f(q["du"] + dul, 2), _f(q["du"] + duo, 2)))
        add("Φόρτιση", "EV-" + q["fl"], "OK" if q["duev"] <= 5.0 else "ΛΑΘΟΣ", "φορτιστής %s kW στη %s: γραμμή 5×6 %s m από τον πίνακα της αποθήκης %s · δικό του ΔΔΡ τύπου A-EV · πτώση τάσης από τον μετρητή %s %%"
            % (_f(M.EV_KW, 0), q["park"], _f(q["Lev"], 0), q["st"], _f(q["duev"], 2)))
    used = M.modules_used(); cap = M.PANEL["rows"] * M.PANEL["per_row"]; free = cap - used
    add("Πίνακας", "ΘΕΣΕΙΣ", "OK" if free / cap >= 0.15 else "ΛΑΘΟΣ",
        "%d στοιχεία από %d · ελεύθερα %d (%d %%)" % (used, cap, free, round(free / cap * 100)))
    add("Πίνακας", "ΒΑΘΟΣ", "OK" if M.PANEL_DEPTH <= M.WALL_CLEAR else "ΛΑΘΟΣ",
        "βάθος εντοιχισμού %s cm ≤ %s cm καθαρά μέσα στον τοίχο (2 γυψ. + CW 100) – τα φύλλα της πλευράς του λουτρού γονέων μένουν ακέραια" % (_f(M.PANEL_DEPTH * 100, 0), _f(M.WALL_CLEAR * 100, 1)))
    wb = W.bbox([w for w in W.WALLS if w["id"] == M.PANEL_WALL][0]["pts"])
    clear = (wb[3] - wb[1]) - 2 * 0.05
    add("Πίνακας", "ΤΟΙΧΟΣ", "OK" if M.PANEL["box"][0] <= clear and wb[1] + 0.05 <= M.PANEL["y0"] and M.PANEL["y1"] <= wb[3] - 0.05 else "ΛΑΘΟΣ",
        "τοίχος %s μήκους %s m · καθαρό ανάμεσα στους ακραίους ορθοστάτες %s m ≥ κουτί %s m · μπροστά του το χωλ σε μήκος %s m (χώρος χειρισμού ≥ 0,70)"
        % (M.PANEL_WALL.replace("T", "Τ"), _f(wb[3] - wb[1]), _f(clear), _f(M.PANEL["box"][0]), _f(6.399 - wb[2])))
    kd = abs(M.KM2_DROP_NEW - (M.PANEL["y0"] + M.PANEL["y1"]) / 2) - M.PANEL["box"][0] / 2
    add("Πίνακας", "ΣΥΜΠ-ΚΜ2", "OK" if kd >= 0.10 else "ΛΑΘΟΣ", "το κατέβασμα των συμπυκνωμάτων του split ΚΜ2 μέσα στον ίδιο τοίχο: σήμερα στο y %s (πίσω από τον πίνακα) → στο y %s, %s cm από το κουτί – "
        "ΑΛΛΑΓΗ στο τεύχος αποχετεύσεων" % (_f(M.KM2_DROP_NOW), _f(M.KM2_DROP_NEW), _f(kd * 100, 0)))
    # ---- Συντονισμός
    names = {d[0] for d in A.DETECTORS}
    add("Συντονισμός", "ΑΝΙΧΝ", "OK" if all(d[0] in names for d in M.DETECTORS) else "ΛΑΘΟΣ",
        "%d ανιχνευτές διαμερίσματος = θέσεις των ανόψεων %s (συντονισμένες με φωτιστικά / στόμια)" % (len(M.DETECTORS), A.REV))
    # ---- Φωτισμός: κάθε φωτιστικό οροφής μέσα σε ζώνη ψευδοροφής, μακριά από μονάδες / στόμια / θυρίδες / κουρτινόθηκες / ντουλάπια / ανιχνευτές
    zones = [(z["id"], r, z["level"]) for z in A.ZONES for r in z["rects"] if not z.get("beam_board") and not z.get("box")]
    block = [(u["id"], u["rect"]) for u in A.UNITS] + [(h["id"], h["rect"]) for h in A.HATCHES] + [(d["id"], d["rect"]) for d in A.DIFFUSERS if d["kind"] != "front"] \
        + [(c["id"], c["rect"]) for c in A.CURTAINS] + [("ντουλάπα", w_["r"]) for w_ in W.WARDROBES]
    tall = [("ντουλάπι κουζίνας", (e[1], e[2], e[3], e[4])) for e in W.EQUIP if e[0] == "tall"]
    det = [(d[0], d[2], d[3]) for d in M.DETECTORS] + [(m[0], m[1], m[2]) for m in M.MOTION]
    beds = [(e[1], e[2], e[3], e[4], e[5]) for e in W.EQUIP if e[0] == "bed"]
    pts_l = [(q[0], q[2], q[3]) for q in M.SPOTS] + [(q[0], q[1], q[2]) for q in M.PENDANTS]
    for nm, x, y in pts_l:
        zz = [zid for zid, r, lv in zones if G.in_rect(x, y, r, tol=-0.10)]
        bad = [bid for bid, r in block + tall if G.in_rect(x, y, r, tol=0.08)]
        near = [did for did, dx, dy in det if math.hypot(x - dx, y - dy) < 0.50]
        pil = []
        for (x0, y0, x1, y1, hd) in beds:                       # ζώνη μαξιλαριού: 0,80 m από το κεφαλάρι
            pr = {"N": (x0, y0, x1, y0 + 0.80), "S": (x0, y1 - 0.80, x1, y1), "W": (x0, y0, x0 + 0.80, y1), "E": (x1 - 0.80, y0, x1, y1)}[hd]
            if G.in_rect(x, y, pr, tol=0.05):
                pil.append("μαξιλάρι")
        st = "OK" if (zz and not bad and not near and not pil) else "ΛΑΘΟΣ"
        add("Φωτισμός", nm, st, ("οροφή %s" % zz[0] if zz else "ΕΚΤΟΣ ζώνης ψευδοροφής") + ((" · πάνω σε " + ", ".join(bad)) if bad else "")
            + ((" · < 0,50 m από " + ", ".join(near)) if near else "") + (" · πάνω από μαξιλάρι" if pil else ""))
    close = [(a[0], b[0]) for i_, a in enumerate(M.SPOTS) for b in M.SPOTS[i_ + 1:] if math.hypot(a[2] - b[2], a[3] - b[3]) < 0.60]
    add("Φωτισμός", "ΑΠΟΣΤ", "ΛΑΘΟΣ" if close else "OK", ("spots πιο κοντά από 0,60 m: %s" % close) if close else "κανένα ζεύγος spots πιο κοντά από 0,60 m")
    for nm, xs, ys, zid in (("ΚΑΝΑΒΟΣ-ΚΑΘ", M.LIV_X, M.LIV_Y, "Ζ1"), ("ΚΑΝΑΒΟΣ-ΥΠ2", M.B2_X, M.B2_Y, "Ζ10")):
        r = [r_ for z_, r_, lv in zones if z_ == zid][0]
        sx = abs((xs[0] - r[0]) - (r[2] - xs[-1])); sy = abs((ys[0] - r[1]) - (r[3] - ys[-1]))
        ex = max(abs((b - a) - (xs[1] - xs[0])) for a, b in zip(xs, xs[1:])); ey = max(abs((b - a) - (ys[1] - ys[0])) for a, b in zip(ys, ys[1:]))
        add("Φωτισμός", nm, "OK" if max(sx, sy, ex, ey) < 0.011 else "ΛΑΘΟΣ", "κάναβος %d × %d συμμετρικός στην οροφή %s: στήλες ανά %s m, %s m από τις άκρες · σειρές ανά %s m, %s m από τις άκρες"
            % (len(xs), len(ys), zid, _f(xs[1] - xs[0]), _f(xs[0] - r[0]), _f(ys[1] - ys[0]), _f(ys[0] - r[1])))
    add("Φωτισμός", "ΜΟΝΟ-SPOT", "OK" if (not M.PENDANTS and M.TRACK is None and all(l[4] in ("ext", "mir") for l in M.WALL_LIGHTS)) else "ΛΑΘΟΣ",
        "μόνο χωνευτά spots (%d τεμ.) – καμία ράγα, κρεμαστό, απλίκα· + 2 καθρέπτες με φως, τα 2 κρυφά LED των ανόψεων, %d φωτιστικά οροφής εξωστών" % (len(M.SPOTS), len(M.EXT_SPOTS)))
    from shapely.geometry import Polygon, Point
    fl = [Polygon(f).buffer(-0.05) for f in W.FLOORS]
    outb = [e[0] for e in M.EXT_SPOTS if not any(f.contains(Point(e[1], e[2])) for f in fl)]
    add("Φωτισμός", "ΕΞΩΣΤΕΣ", "ΛΑΘΟΣ" if outb else "OK", ("εκτός δαπέδου εξώστη: " + ", ".join(outb)) if outb else "%d φωτιστικά οροφής εξωστών σε ζεύγη ανά %s m, όλα πάνω από δάπεδο εξώστη – θέσεις κατά τα προοπτικά (εκτίμηση)" % (len(M.EXT_SPOTS), _f(M.EXT_PAIR)))
    names_a = {q[0]: (q[2], q[3]) for q in A.SPOTS}
    moved = [q[0] for q in M.SPOTS if q[0] not in names_a or math.hypot(q[2] - names_a[q[0]][0], q[3] - names_a[q[0]][1]) > 0.01]
    gone = [n_ for n_ in names_a if n_ not in {q[0] for q in M.SPOTS} and not n_.startswith("ΚΛ")]
    add("Φωτισμός", "ΑΝΟΨΕΙΣ", "OK", "διαφορές από τις ανόψεις %s (περνούν εκεί ΜΕΤΑ την έγκριση): νέα θέση %s · καταργούνται %s και οι παροχές κρεμαστών ΚΡΕΜ0 / ΚΡΕΜ1 · ΑΚ1 στο κέντρο φατνώματος"
        % (A.REV, ", ".join(moved) or "—", ", ".join(gone) or "—"))
    # κουτιά στον ίδιο τοίχο: ίδιο ύψος → ≥ 7,1 cm μεταξύ κέντρων (ή κοινό πλαίσιο)
    clash = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            if a[3] != b[3] or abs(a[4] - b[4]) > 0.10:
                continue
            dd = math.hypot(a[1] - b[1], a[2] - b[2])
            if dd < 0.071 and not (a[0].startswith("ρολό") or b[0].startswith("ρολό")):
                clash.append("%s/%s" % (a[0], b[0]))
    add("Συντονισμός", "ΚΟΥΤΙΑ", "ΛΑΘΟΣ" if clash else "OK", ("κουτιά το ένα πάνω στο άλλο: " + ", ".join(clash)) if clash else "κανένα ζεύγος κουτιών στο ίδιο ύψος πιο κοντά από 7,1 cm (βήμα πολλαπλών πλαισίων)")
    # θερμοστάτες: όχι κάτω από split, όχι δίπλα σε πόρτα μπαλκονιού
    # R16 (ιδιοκτήτης 20/11: «θερμοστάτες και θυροτηλέφωνα τα θέλω κοντά στις πόρτες»): κάθε θερμοστάτης στον άξονα του διακόπτη της πόρτας του, +1,50
    for t in M.THERMOSTATS:
        sw = min(M.SWITCHES, key=lambda q: math.hypot(q[1] - t[1], q[2] - t[2])); dsw = math.hypot(sw[1] - t[1], sw[2] - t[2])
        add("Συντονισμός", t[0] + "-ΠΟΡΤΑ", "OK" if dsw < 0.02 and sw[3] == t[3] else "ΛΑΘΟΣ", "θερμοστάτης δίπλα στην πόρτα: ακριβώς πάνω από τον διακόπτη %s, στο +%s (ο διακόπτης στο +%s)"
            % (sw[0], _f(M.H_TH), _f((sw[7] if len(sw) > 7 else {}).get("h", M.H_SW))) if dsw < 0.02 and sw[3] == t[3] else "θερμοστάτης μακριά από τον διακόπτη της πόρτας (%s στα %s m)" % (sw[0], _f(dsw)))
        under = [u for u in A.SPLITS if G.in_rect(t[1], t[2], u["rect"], tol=0.0)]
        near = [u for u in A.SPLITS if G.in_rect(t[1], t[2], u["rect"], tol=0.25)]
        if under:
            add("Συντονισμός", t[0], "ΛΑΘΟΣ", "ακριβώς κάτω από το split " + under[0]["id"])
        elif near:
            u = near[0]
            add("Συντονισμός", t[0], "ΟΡΙΑΚΟ", "δίπλα στην πόρτα (ιδιοκτήτης 20/11) = στην άκρη του split %s, που είναι πάνω από την πόρτα: %s m κάτω από τη μονάδα, έξω από το περίγραμμά της· "
                "η μονάδα ρίχνει μέσα στο δωμάτιο, όχι στον τοίχο · ελέγχει %s" % (u["id"], _f(u["bottom"] - M.H_TH), " + ".join(t[5])))
        else:
            add("Συντονισμός", t[0], "OK", "σε εσωτερικό τοίχο, +1,50, μακριά από split / ήλιο · ελέγχει " + " + ".join(t[5]))
    # θυροτηλεόραση: πάνω από τον διακόπτη της πόρτας εισόδου
    tt = [d for d in M.WALL_DEV if d[0] == "ΘΤ"][0]; d1 = [q for q in M.SWITCHES if q[0] == "Δ1"][0]; door = W.DOORS[DOOR_SW["Δ1"]]
    dj = math.hypot(tt[1] - door[2][0], tt[2] - door[2][1])
    add("Συντονισμός", "ΘΤ-ΠΟΡΤΑ", "OK" if abs(tt[2] - d1[2]) < 0.02 and dj <= 0.45 else "ΛΑΘΟΣ", "θυροτηλεόραση δίπλα στην πόρτα εισόδου: πάνω από τον διακόπτη Δ1, %s m από την παραστάδα (πλευρά κλειδαριάς), +%s"
        % (_f(dj), _f(tt[5])))
    # R16: ρευματοδότης εξώστη = πάνω σε παρειά που βλέπει ΣΤΟΝ εξώστη (όλο το κουτί μπροστά σε δάπεδο εξώστη – όχι μέσα στη γωνία με άλλον τοίχο, όχι έξω από τον εξώστη)
    for s_ in M.SOCKETS:
        if s_[8] != "ΕΞ":
            continue
        nx, ny = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}[s_[3]]
        ok = all(any(_in_poly(s_[1] + nx * 0.15 - ny * e, s_[2] + ny * 0.15 + nx * e, f) for f in W.FLOORS) for e in (-0.07, 0.0, 0.07))
        add("Συντονισμός", s_[0] + "-ΕΞΩΣΤΗΣ", "OK" if ok else "ΛΑΘΟΣ", "ρευματοδότης εξώστη: όλο το κουτί (± 7 cm) βλέπει σε δάπεδο εξώστη" if ok else
            "ρευματοδότης εξώστη ΕΚΤΟΣ εξώστη / μέσα στη γωνία με άλλον τοίχο (%s / %s)" % (_f(s_[1], 3), _f(s_[2], 3)))
    return R


def _in_poly(x, y, poly):
    n = len(poly); c = False
    for i in range(n):
        x1, y1 = poly[i][0], poly[i][1]; x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def _faces_into(x, y, d, r):
    """Το σημείο βλέπει προς το εσωτερικό του ορθογωνίου r (είναι δηλαδή στην πλάτη / στο πλάι του επίπλου);"""
    nx, ny = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}[d]
    return G.in_rect(x + nx * 0.05, y + ny * 0.05, r, tol=-0.002)


def _ceiling_below(a, b, beam, soffit, need=0.07):
    """Στο κομμάτι του a–b κάτω από τη δοκό η ψευδοροφή είναι τουλάχιστον need κάτω από την κάτω παρειά της (καθαρό κενό για σωλήνες);"""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 0.01)); seen = False
    for i in range(n + 1):
        t = i / n; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if not G.in_rect(x, y, beam, tol=-0.01):
            continue
        seen = True
        lv = [z["level"] for z in A.ZONES for r in z["rects"] if G.in_rect(x, y, r)]
        if not lv or min(lv) > soffit - need - 0.0125:
            return False
    return seen


def _covered(a, b, beam, rects):
    """Όλο το κομμάτι του a–b που πέφτει μέσα στη δοκό βρίσκεται μέσα σε κάποιο από τα rects;"""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 0.01))
    for i in range(n + 1):
        t = i / n; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if G.in_rect(x, y, beam, tol=-0.01) and not any(G.in_rect(x, y, r, tol=0.005) for r in rects):
            return False
    return True


# ---------------------------------------------------------------- φορτία
def phases():
    ph = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
    for c in M.CIRCUITS:
        p = c["P"] * c["g"]
        if c["ph"] == "3Φ":
            for k in ph:
                ph[k] += p / 3
        else:
            ph[c["ph"]] += p
    return ph


def installed():
    return sum(c["P"] for c in M.CIRCUITS)


# ---------------------------------------------------------------- μήκη καλωδίων (ενδεικτικά)
CEIL = 2.75


def _man(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def path_to(pt, zone):
    """Μήκος όδευσης από τον πίνακα ως πάνω από το σημείο (m). Όλα φεύγουν από την κορυφή του πίνακα, μέσα από τις ψευδοροφές."""
    P0 = (3.34, 4.10)
    if zone == "N":
        return 1.0 + _man((3.40, 3.72), pt)
    if zone in ("S", "F"):   # ταβάνι και τοίχοι του καθιστικού: από την οπή ΟΠ1
        return 1.0 + _man(P0, M.GATE1) + _man(M.GATE1, pt)
    if zone == "K":          # κουζίνα: ΟΠ1 → κενό καθιστικού / λωρίδας → ΟΠ4
        return 1.0 + _man(P0, M.GATE3) + _man(M.GATE3, (9.28, 7.95)) + _man((9.28, 7.95), M.GATE_K) + _man(M.GATE_K, pt)
    return _man(P0, pt)


def _fits(h):
    """Οι δύο μεγαλύτερες διατομές χωρούν δίπλα-δίπλα μέσα στο χιτώνιο (d1 + d2 ≤ καθαρή Ø)."""
    ds = sorted([l[1] for l in h["lines"] for _ in range(l[2])], reverse=True)
    return len(ds) < 2 or ds[0] + ds[1] <= M.HOLE_IN * 1000 + 1e-6


def holes():
    """Οπές δοκών (R06, εγκεκριμένες από τον στατικό): Ø60, κέντρο στη ΜΕΣΗ ΤΟΥ ΥΨΟΥΣ της δοκού. Ελέγχονται: (α) το στόμιο βγαίνει πάνω από την ψευδοροφή και κάτω από την
    πλάκα και στις δύο πλευρές · (β) Ø ≤ ύψος / 5 · (γ) ≥ 1,5 ύψος από την παρειά της στήριξης · (δ) αποστάσεις μεταξύ τους ≥ 3 Ø · (ε) πληρότητα · (στ) κανένας τοίχος μπροστά στο στόμιο."""
    import math
    out = []
    for h in M.HOLES:
        bn, sec, x0, y0, x1, y1 = [b for b in A.BEAMS if b[0] == h["beam"]][0]
        hh = int(sec.split("/")[1]) / 100.0; soff = A.beam_soffit(sec)
        x, y = h["x"], h["y"]
        horiz = (x1 - x0) > (y1 - y0)
        side = [(x, y0 - 0.12), (x, y1 + 0.12)] if horiz else [(x0 - 0.12, y), (x1 + 0.12, y)]
        lo, hi, lo_room = soff, A.TOP_SLAB - 0.15, ""
        for (px, py) in side:
            for zz in A.ZONES:
                if any(G.in_rect(px, py, r) for r in zz["rects"]):
                    if zz["level"] + 0.0125 > lo:
                        lo = zz["level"] + 0.0125; lo_room = {"Ζ4": "χωλ", "Ζ10": "Υπν.2", "Ζ11": "Υπν.2"}.get(zz["id"], zz["id"])
                    hi = min(hi, A.SLABS.get(zz.get("slab"), hi))
        z = soff + hh / 2
        dsup = min(x - x0, x1 - x) if horiz else min(y - y0, y1 - y)
        others = [o for o in M.HOLES if o["beam"] == h["beam"] and o["id"] != h["id"]]
        sp = min([math.hypot(o["x"] - x, o["y"] - y) for o in others] or [9.0])
        area = sum(math.pi * (l[1] / 2.0) ** 2 * l[2] for l in h["lines"]); fill = area / (math.pi * (M.HOLE_IN * 500) ** 2)
        free = True
        out.append(dict(h, sec=sec, z=z, h=hh, lo=lo, hi=hi, lo_room=lo_room, horiz=horiz, dsup=dsup, sp=sp, fill=fill, ncab=sum(l[2] for l in h["lines"]),
                        under=max(0.0, lo - (z - M.HOLE_D / 2)), over=max(0.0, (z + M.HOLE_D / 2) - hi),
                        ok_z=(z - M.HOLE_D / 2 >= lo - 1e-6 and z + M.HOLE_D / 2 <= hi + 1e-6), ok_d=M.HOLE_D <= hh / 5 + 1e-9, ok_sup=dsup >= 1.5 * hh - 1e-6, ok_pair=_fits(h),
                        ok_sp=sp >= 3 * M.HOLE_D - 1e-6, ok_fill=fill <= M.HOLE_FILL + 1e-6, ok_free=free))
    return out


def feeder_lengths():
    """Ανά όροφο: μήκη μετρητής → πίνακας αποθήκης (L1) → πίνακας σπιτιού (L2), γραμμή φορτιστή (Lev), πτώσεις τάσης. ΕΚΤΙΜΗΣΗ από τα σχέδια."""
    out = []
    ceil_gf = M.LV_GF + 2.55; tray = M.LV_B + M.H_B
    for q in M.STORES:
        tl = G.path_len(q["tray"])
        L1 = (1.5 + _man(M.METERS, M.SHAFT) + (ceil_gf - tray) + tl + (M.H_B - 1.5)) * 1.10
        L2 = ((M.H_B - 1.5) + tl + (M.FLOOR_LV[q["fl"]] + 2.55 - tray) + G.path_len(M.FEED_ROUTE) + 1.0) * 1.10
        Lev = ((M.H_B - 1.5) + G.path_len(q["evr"]) + (M.H_B - 1.2)) * 1.10
        S = M.FEEDER["sec"]; k = (3 ** 0.5) * RHO / 400 * 100
        du = k * (L1 + L2) * M.FEEDER["In"] / S
        iev = M.EV_KW * 1000 / (3 ** 0.5 * 400)
        duev = k * L1 * M.FEEDER["In"] / S + k * Lev * iev / 6.0
        out.append(dict(fl=q["fl"], st=q["st"], park=q["park"], L1=L1, L2=L2, L=L1 + L2, Lev=Lev, du=du, duev=duev))
    return out


ROOM_ZONE = {"ΚΟΥΖ": "K", "ΥΠ1": "N", "ΥΠ2": "N", "ΧΩΛ": "N", "ΛΟΥ": "N", "ΛΓ": "N"}


def zone_of(room, x, y):
    if room in ROOM_ZONE:
        return ROOM_ZONE[room]
    if room == "ΚΑΘ":
        return "F"
    if room == "ΕΞ":
        return "S" if (y > 9.0 and x > 5.0) else "N"
    return "N"


def circuit_lengths():
    """{κύκλωμα: m καλωδίου} – αλυσίδα από σημείο σε σημείο + κατακόρυφα + πίνακας, × 1,10."""
    dev = {}
    for s in M.SOCKETS:
        dev.setdefault(s[7], []).append((s[1], s[2], s[6], zone_of(s[8], s[1], s[2])))
    for f in M.FIXED:
        dev.setdefault(f[5], []).append((f[1], f[2], f[4], "N"))
    for f in M.FIXED_FREE:
        dev.setdefault(f[3], []).append((f[1], f[2], 2.6, "S" if f[0] == "ΚΜ1" else "N"))
    for sh in M.SHUTTERS:
        x, y, d = sh["motor"]
        dev.setdefault(sh["c"], []).append((x, y, M.H_HI, zone_of(sh.get("room", "ΥΠ1"), x, y)))
    for l in M.WALL_LIGHTS:
        c = M.GROUPS[l[6]]["c"]
        dev.setdefault(c, []).append((l[1], l[2], l[5], zone_of(l[7], l[1], l[2])))
    spot_c = {g: M.GROUPS[g]["c"] for g in M.GROUPS}
    for q in M.SPOTS:
        x, y, g = q[2], q[3], q[4]
        if g in spot_c:
            dev.setdefault(spot_c[g], []).append((x, y, CEIL, "K" if g == "ε" else ("S" if g in ("β", "α", "λ", "γ") else "N")))
    for s in M.SWITCHES:
        opt = s[7] if len(s) > 7 else {}
        for kind, g in s[4]:
            if g in M.GROUPS:
                dev.setdefault(M.GROUPS[g]["c"], []).append((s[1], s[2], opt.get("h", M.H_SW), zone_of(s[5], s[1], s[2])))
                break
    out = {}
    for c in M.CIRCUITS:
        ds = dev.get(c["id"], [])
        if c["zone"] == "B":                              # προς shaft: ως την έξοδο του διαμερίσματος
            out[c["id"]] = round((path_to((9.28, 5.80), "S") + 6.0 + 1.5) * 1.10, 1)
            continue
        if not ds:
            out[c["id"]] = 0.0
            continue
        ds = sorted(ds, key=lambda q: path_to((q[0], q[1]), q[3]))
        L = 1.5 + path_to((ds[0][0], ds[0][1]), ds[0][3])
        for a, b in zip(ds, ds[1:]):
            L += min(_man((a[0], a[1]), (b[0], b[1])), path_to((b[0], b[1]), b[3]))
        L += sum((CEIL - q[2]) + 0.15 for q in ds if q[2] < CEIL)
        if any(k == c["id"] for k in ("Φ1", "Φ2", "Φ3", "Φ4")):
            L *= 1.25                                     # επιστροφές διακοπτών / αλέ-ρετούρ
        out[c["id"]] = round(L * 1.10, 1)
    return out


RUN_B = {"ΗΛ": 40.0}     # ΕΚΤΙΜΗΣΗ: ως το δώμα / την αποθήκη / τη θέση στάθμευσης από τον δυσμενέστερο τυπικό όροφο
RHO = 0.0225                                       # Ω·mm²/m, χαλκός στους 70 °C


def circuit_runs():
    """{κύκλωμα: m ως το ΜΑΚΡΙΝΟΤΕΡΟ σημείο του} – για την πτώση τάσης."""
    dev = {}
    for s in M.SOCKETS:
        dev.setdefault(s[7], []).append((s[1], s[2], s[6], zone_of(s[8], s[1], s[2])))
    for f in M.FIXED:
        dev.setdefault(f[5], []).append((f[1], f[2], f[4], "N"))
    for f in M.FIXED_FREE:
        dev.setdefault(f[3], []).append((f[1], f[2], 2.6, "S" if f[0] == "ΚΜ1" else "N"))
    for sh in M.SHUTTERS:
        x, y, d = sh["motor"]
        dev.setdefault(sh["c"], []).append((x, y, M.H_HI, zone_of(sh.get("room", "ΥΠ1"), x, y)))
    for l in M.WALL_LIGHTS:
        dev.setdefault(M.GROUPS[l[6]]["c"], []).append((l[1], l[2], l[5], zone_of(l[7], l[1], l[2])))
    for q in M.SPOTS:
        x, y, g = q[2], q[3], q[4]
        if g in M.GROUPS:
            dev.setdefault(M.GROUPS[g]["c"], []).append((x, y, CEIL, "K" if g == "ε" else ("S" if g in ("β", "α", "λ", "γ") else "N")))
    out = {}
    for c in M.CIRCUITS:
        if c["id"] in RUN_B:
            out[c["id"]] = RUN_B[c["id"]]
            continue
        ds = dev.get(c["id"], [])
        if not ds:
            out[c["id"]] = 3.0                           # μέσα στην τεχνική ντουλάπα
            continue
        out[c["id"]] = round(max(1.5 + path_to((q[0], q[1]), q[3]) + max(0.0, CEIL - q[2]) for q in ds) * 1.10, 1)
    return out


def circuit_table():
    """Γραμμές του πίνακα κυκλωμάτων: dict με Ib (ρεύμα φορτίου), Iz (ικανότητα καλωδίου), ΔU % ως το μακρινότερο σημείο (χωρίς την παροχή)."""
    runs = circuit_runs(); tot = circuit_lengths()
    rows = []
    for c in M.CIRCUITS:
        three = c["ph"] == "3Φ"
        sec = c["cable"].split("×")[1]
        ib = c["P"] * 1000 / ((3 ** 0.5) * 400 * 0.95) if three else c["P"] * 1000 / (230 * 0.95)
        ib = min(ib, c["In"])
        iz = M.IZ.get((sec, 3 if three else 2))
        S = float(sec.replace(",", "."))
        L = runs[c["id"]]
        du = ((3 ** 0.5) * L * ib * RHO / S / 400 if three else 2 * L * ib * RHO / S / 230) * 100
        rows.append(dict(c=c, ib=ib, iz=iz, L=L, tot=tot.get(c["id"], 0.0), du=du, ok=(iz is not None and c["In"] <= iz and ib <= c["In"])))
    return rows


def feeder_calc():
    """Κεντρική παροχή: ζήτηση, ρεύμα, πτώση τάσης."""
    ph = phases()
    peak = sum(ph.values()); dem = peak * M.DIVERSITY
    imax = max(ph.values()) * M.DIVERSITY * 1000 / 230
    FL = feeder_lengths(); w = max(FL, key=lambda q: q["du"])
    return dict(ph=ph, peak=peak, dem=dem, imax=imax, du=w["du"], iz=M.IZ[("16", 3)], L=w["L"], fl=w["fl"], rows=FL)


def weak_lengths():
    hub = ((M.DATA_CAB[0] + M.DATA_CAB[2]) / 2, 4.62)
    cat = 0.0; n_ports = 0
    for d in M.DATA:
        z = zone_of(d[6], d[1], d[2])
        base = _man(hub, (d[1], d[2])) if z == "N" else (path_to((d[1], d[2]), z))
        cat += d[4] * (base + (CEIL - d[5]) + 1.5) * 1.10; n_ports += d[4]
    cat += (path_to((9.375, 6.80), "S") + 1.3 + 1.5) * 1.10; n_ports += 1          # θυροτηλεόραση
    coax = sum(((_man(hub, (t[1], t[2])) if zone_of(t[5], t[1], t[2]) == "N" else path_to((t[1], t[2]), zone_of(t[5], t[1], t[2]))) + CEIL + 1.5) * 1.10 for t in M.TV)
    bus = sum((_man((4.32, 4.62), (t[1], t[2])) + (CEIL - M.H_TH) + 1.5) * 1.10 for t in M.THERMOSTATS)
    det = {d[0]: (d[2], d[3]) for d in M.DETECTORS}
    fire = 1.5
    prev = (4.90, 4.62)
    for k in M.FIRE_LOOP[1:]:
        fire += _man(prev, det[k]) + (1.9 if k in ("ΑΚ1", "ΑΘ5") else 0); prev = det[k]
    return dict(cat6a=round(cat, 0), ports=n_ports, coax=round(coax, 0), bus=round(bus, 0), fire=round(fire * 1.10, 0))


def counts():
    n = {}
    n["sock_pts"] = len(M.SOCKETS)
    n["sock_out"] = sum(s[4] for s in M.SOCKETS if s[5] != "fix")
    n["sock_std"] = sum(1 for s in M.SOCKETS if s[5] in ("std", "usb", "ded") and not (len(s) > 10 and s[10].get("surf")))
    n["sock_ip"] = sum(1 for s in M.SOCKETS if s[5] == "ip")
    n["sock_usb"] = sum(1 for s in M.SOCKETS if s[5] == "usb")
    n["sock_surf"] = sum(1 for s in M.SOCKETS if len(s) > 10 and s[10].get("surf"))
    n["fix"] = sum(1 for s in M.SOCKETS if s[5] == "fix") + len(M.FIXED) + len(M.FIXED_FREE)
    k = {}
    for s in M.SWITCHES:
        for kind, g in s[4]:
            k[kind] = k.get(kind, 0) + 1
    n["sw"] = k; n["sw_plates"] = len(M.SWITCHES)
    kinds = {}
    for q in M.SPOTS:
        kinds[q[1]] = kinds.get(q[1], 0) + 1
    n["spots"] = kinds
    n["led_m"] = round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for (_, a, b, g, t) in M.LED), 1)
    n["boxes"] = len([p for p in wall_points() if not p[6].get("surf")])
    return n


def lighting_table():
    """[(χώρος, εμβαδό, lm εγκατεστημένα, lx υπολογισμένα, στόχος, W, W/m²)] – μέθοδος φωτεινής ροής, συντελεστής χρησιμοποίησης 0,55, συντήρησης 0,8."""
    sp = {}
    for q in M.SPOTS:
        sp.setdefault(q[4], []).append(q[1])
    def lm(groups, kitchen=False):
        f = w = 0
        for g in groups:
            for kd in sp.get(g, []):
                a, b = M.LUM["kitchen" if kitchen else kd]; f += a; w += b
        return f, w
    rows = []
    led_len = {}
    for (nm, a, b, g, t) in M.LED:
        led_len[nm] = led_len.get(nm, 0) + math.hypot(b[0] - a[0], b[1] - a[1])
    data = {
        "Καθιστικό – τραπεζαρία": (lm(["α", "λ", "γ", "β"]), []),
        "Κουζίνα": (lm(["ε"], True), [(M.LUM["led_m"][0] * led_len.get("LED4", 0) * 0.5, M.LUM["led_m"][1] * led_len.get("LED4", 0))]),
        "Υπνοδωμάτιο 1": (lm(["ζ"]), []),
        "Υπνοδωμάτιο 2": (lm(["κ"]), []),
        "Χωλ": (lm(["η"]), []),
        "Λουτρό": (lm(["μ"]), [(M.LUM["mir"][0] * 0.4, M.LUM["mir"][1])]),
        "Λουτρό γονέων": (lm(["ν"]), [(M.LUM["mir"][0] * 0.4, M.LUM["mir"][1])]),
    }
    for name, area, target, cct, note in M.ROOMS_LIGHT:
        (f, w), extra = data[name]
        f += sum(e[0] for e in extra); w += sum(e[1] for e in extra)
        lx = f * 0.55 * 0.8 / area
        rows.append((name, area, f, lx, target, w, w / area, cct, note))
    return rows


def report():
    R = run()
    bad = [r for r in R if r[2] == "ΛΑΘΟΣ"]
    return R, bad


if __name__ == "__main__":
    import b1_el
    bind(b1_el)
    R, bad = report()
    for g, c, st, t in R:
        if st != "OK" or "-v" in sys.argv:
            print("%-12s %-10s %-6s %s" % (g, c, st, t))
    print("\n%d έλεγχοι · %d ΛΑΘΟΣ" % (len(R), len(bad)))
    print("στοιχεία πίνακα:", b1_el.modules_used(), "· φάσεις:", {k: round(v, 2) for k, v in phases().items()}, "· εγκατεστημένα kW:", round(installed(), 1))
    print("μήκη:", circuit_lengths())
    print("ασθενή:", weak_lengths())
    print("πλήθη:", counts())
    for r in lighting_table():
        print("  %-26s %5.1f m²  %5.0f lm  %4.0f lx (στόχος %d)  %3.0f W  %.1f W/m²" % r[:7])
    sys.exit(1 if bad else 0)
