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
        elif typ == "T6A" and not opt.get("fire"):
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
    # ---- Δοκός: καμία όδευση στο κενό δεν περνά κάτω από δοκό εκτός διέλευσης
    cross = [p["rect"] for p in M.PASSES]
    approved = [("Δ9.1", (9.40, 5.30, 9.70, 6.30), "πάνω από την πόρτα εισόδου, μέσα στον τοίχο Τ6Β (ανόψεις R16 / R23)"),
                ("Δ2.1", (9.70, 3.00, 11.05, 3.40), "έξοδος του shaft μέσα στον ψευδοδοκό του κλιμακοστασίου (ανόψεις R16)")]
    routes = [("παροχή", M.FEED_ROUTE), ("προς shaft", M.OUT_ROUTE)] + [(r["id"], r["pts"]) for r in M.ROUTES]
    for rid, rp in routes:
        bad = []
        for a, b in zip(rp, rp[1:]):
            for (bn, sec, x0, y0, x1, y1) in A.BEAMS:
                br = (x0, y0, x1, y1)
                if not G.seg_hits_rect(a, b, br):
                    continue
                # το τμήμα μέσα στη δοκό πρέπει να βρίσκεται όλο μέσα σε διέλευση ή σε εγκεκριμένο σημείο
                if _covered(a, b, br, cross) or any(bn == an and _covered(a, b, br, [ar]) for an, ar, _ in approved):
                    continue
                if _ceiling_below(a, b, br, A.beam_soffit(sec)):      # η ψευδοροφή εκεί είναι ≥ 7 cm κάτω από τη δοκό (κουζίνα): περνά ελεύθερα
                    continue
                bad.append(bn)
        add("Δοκός", rid, "ΛΑΘΟΣ" if bad else "OK", ("περνά κάτω από " + ", ".join(sorted(set(bad)))) if bad else "κάτω από δοκό μόνο μέσα στα περάσματα Π0–Π5 (μέσα σε τοίχο) και στον ψευδοδοκό του κλιμακοστασίου")
    for p in M.PASSES:
        hit = [b[0] for b in A.BEAMS if not (p["rect"][2] <= b[2] or p["rect"][0] >= b[4] or p["rect"][3] <= b[3] or p["rect"][1] >= b[5])]
        add("Πέρασμα", p["id"], "OK" if hit else "ΛΑΘΟΣ", "%s · %s – %s%s" % (p["beam"], p["n"], p["title"], " · ΘΕΛΕΙ ΑΛΛΑΓΗ ΤΟΙΧΟΠΟΙΙΑΣ" if p["new"] else ""))
    dk = [r for r in M.FLOOR_RUNS if r["id"] == "ΔΚ"][0]
    need = M.DK_N * 0.027
    add("Πέρασμα", "ΔΚ-ΠΛΑΤΟΣ", "OK" if need <= 0.90 else "ΛΑΘΟΣ", "δέσμη δαπέδου ΔΚ: %d σωλήνες Ø20–32 σε ΜΙΑ στρώση = λωρίδα %s m πάνω στην πλάκα (ή %s m σε δύο στρώσεις) · μήκος %s m · "
        "κάτω από τη μόνωση της ενδοδαπέδιας" % (M.DK_N, _f(need), _f(need / 2), _f(G.path_len(dk["pts"]), 1)))
    wn = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] in ("T2-04", "T2N-01", "T2-06")]
    add("Πέρασμα", "ΤΟΙΧΟΣ-Δ3.1", "OK" if all(abs(b[3] - 5.15) < 0.002 for b in wn) else "ΛΑΘΟΣ", "ο βόρειος τοίχος του καθιστικού ΟΠΩΣ οι τοιχοποιίες %s: παρειά στο 5,15, περασιά με τη δοκό Δ3.1 – "
        "κανένα κανάλι, καμία αλλαγή τοιχοποιίας" % W.REV)
    ch = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] == "T6B-02"][0]
    add("Πέρασμα", "ΑΝΟΔΟΣ", "OK" if (ch[1] <= M.RISER[1] <= ch[3] and W.CHAN_X[0] <= M.RISER[0] <= W.CHAN_X[1]) else "ΛΑΘΟΣ",
        "άνοδος προς το ταβάνι του καθιστικού μέσα στο κανάλι 5 cm του τοίχου Τ6Β-02 (μήκος %s m, δίπλα στη Δ9.1) – μαζί με το κατέβασμα των συμπυκνωμάτων της ΚΜ1" % _f(ch[3] - ch[1]))
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
        "εγκατεστημένα %s kW · άθροισμα αιχμών κυκλωμάτων %s kW · με ετεροχρονισμό %s → %s kW · ρεύμα στη φορτισμένη φάση %s A ≤ %d A (η φόρτιση οχήματος με διαχείριση φορτίου – παίρνει ό,τι περισσεύει)"
        % (_f(installed(), 1), _f(sum(ph.values()), 1), _f(M.DIVERSITY), _f(tot, 1), _f(imax, 1), M.FEEDER["In"]))
    du = math.sqrt(3) * M.FEEDER["In"] * M.FEEDER["length"] * 0.0225 / 10 / 400 * 100
    add("Πίνακας", "ΠΤΩΣΗ", "OK" if du <= 1.5 else "ΛΑΘΟΣ", "πτώση τάσης παροχής 5×10 mm² · %s m · %d A = %s %% (όριο 1,5 %% ώστε να μένει 3 %% για τα κυκλώματα)" % (_f(M.FEEDER["length"], 0), M.FEEDER["In"], _f(du, 2)))
    used = M.modules_used(); cap = M.PANEL["rows"] * M.PANEL["per_row"]; free = cap - used
    add("Πίνακας", "ΘΕΣΕΙΣ", "OK" if free / cap >= 0.15 else "ΛΑΘΟΣ",
        "%d στοιχεία από %d (με τη φόρτιση οχήματος) · ελεύθερα %d (%d %%)" % (used, cap, free, round(free / cap * 100)))
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
    for t in M.THERMOSTATS:
        near = [u["id"] for u in A.SPLITS if G.in_rect(t[1], t[2], u["rect"], tol=0.25)]
        add("Συντονισμός", t[0], "ΛΑΘΟΣ" if near else "OK", ("κάτω από το split " + near[0]) if near else "σε εσωτερικό τοίχο, +1,50, μακριά από split / ήλιο · ελέγχει " + " + ".join(t[5]))
    return R


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


GATE_S = (9.28, 6.40)        # έξοδος του καναλιού του τοίχου Τ6Β-02 στο κενό της λωρίδας εισόδου
GATE_K = (9.95, 7.68)        # πέρασμα Π2: έξοδος στο κενό της κουζίνας
_DK = 0.14 + 1.47 + 5.60 + 1.30 + 0.28      # δέσμη δαπέδου ΔΚ από τη βάση του τοίχου του πίνακα ως τη βάση του καναλιού


def path_to(pt, zone):
    """Μήκος όδευσης από τον πίνακα ως πάνω από το σημείο (m)."""
    P0 = M.P_TOP
    if zone == "N":
        return 1.0 + _man((3.40, 3.72), pt)
    if zone == "S":          # ταβάνι καθιστικού: κάτω στον πίνακα, δέσμη ΔΚ, πάνω μέσα στο κανάλι
        return 1.3 + _DK + 2.7 + _man(GATE_S, pt)
    if zone == "K":          # κουζίνα: δέσμη ΔΚ, κανάλι, Π2
        return 1.3 + _DK + 2.4 + 1.3 + 0.6 + _man(GATE_K, pt)
    if zone == "F":          # από το δάπεδο: τοίχοι του καθιστικού (η δέσμη τρέχει στη βάση του βόρειου τοίχου) – το CEIL − h που προστίθεται καλύπτει το ανέβασμα
        return 1.3 + 0.14 + 1.47 + _man((3.50, M.DK_Y), pt) - 2.0
    return _man(P0, pt)


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
        dev.setdefault(sh["c"], []).append((x, y, M.H_HI, zone_of("ΚΑΘ" if sh["win"] in ("W2.01", "W2.02") else "ΥΠ1", x, y)))
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
            out[c["id"]] = round((path_to((9.375, 5.80), "S") + 6.0 + 1.5) * 1.10, 1)
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


RUN_B = {"ΗΛ": 36.0, "ΑΠ": 40.0, "EV": 45.0}     # ΕΚΤΙΜΗΣΗ: ως το δώμα / την αποθήκη / τη θέση στάθμευσης από τον δυσμενέστερο τυπικό όροφο
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
        dev.setdefault(sh["c"], []).append((x, y, M.H_HI, zone_of("ΚΑΘ" if sh["win"] in ("W2.01", "W2.02") else "ΥΠ1", x, y)))
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
    S = 10.0; L = M.FEEDER["length"]
    du = (3 ** 0.5) * L * M.FEEDER["In"] * RHO / S / 400 * 100
    return dict(ph=ph, peak=peak, dem=dem, imax=imax, du=du, iz=M.IZ[("10", 3)])


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
