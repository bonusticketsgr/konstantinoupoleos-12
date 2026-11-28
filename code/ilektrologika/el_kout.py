"""ΗΛ-16 ΚΟΥΤΕΛΟ ΔΙΠΛΑ ΣΤΟ ΔΟΚΑΡΙ Δ3.1 – ΑΠΟΧΕΤΕΥΣΗ ΚΛΙΜΑΤΙΣΤΙΚΟΥ ΣΑΛΟΝΙΟΥ (R15, ιδιοκτήτης 20/11/2026).

Τομή Α: κάθετα στο δοκάρι, μέσα από την ΟΠ2 (1:7,5) · Τομή Β: κατά μήκος του δοκαριού, μέσα από το κούτελο, από την ΟΠ2 ως το πλυντήριο (1:20).
Όλη η γεωμετρία διαβάζεται από τα μοντέλα: M.KOUT, η διαδρομή «ΣΥ» (TRUNKS3), οι ζώνες οροφής (A.ZONES με τις αλλαγές R15), τοίχοι / ντουλάπες των τοιχοποιιών."""
import math
import el_geom as G

M = W = A = None
S75 = 72 / 25.4 * 1000 / 7.5
S20 = 72 / 25.4 * 1000 / 20.0
CONC = (0.62, 0.62, 0.66); BEAMF = (0.44, 0.44, 0.50); GYP = (0.86, 0.86, 0.88); WALLF = (0.955, 0.955, 0.965); FRAME = (0.72, 0.76, 0.82)
PIPE = (0.50, 0.16, 0.70); REFR = (0.05, 0.50, 0.55); HOLEC = (0.62, 0.10, 0.62); BLUE = (0.10, 0.36, 0.72); FURNC = (0.55, 0.25, 0.62); KFILL = (0.95, 0.90, 0.98)


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A


def _f(v, n=2):
    return G.fmt(v, n) if n != 2 else G.fmt(v)


def _wall(wid):
    return W.bbox([q for q in W.WALLS if q["id"] == wid][0]["pts"])


def _zone(zid):
    return [z for z in A.ZONES if z["id"] == zid][0]


def _sy():
    return [t for t in M.TRUNKS3 if t["id"] == "ΣΥ"][0]["pts"]


def _circle(cv, X, Y, r, fill, stroke, lw=0.8):
    cv.saveState(); cv.setFillColorRGB(*fill); cv.setStrokeColorRGB(*stroke); cv.setLineWidth(lw); cv.circle(X, Y, r, stroke=1, fill=1); cv.restoreState()


def _band(cv, P_, w, col):
    cv.saveState(); cv.setLineJoin(1); cv.setLineCap(0)
    for wd, cl in ((w + 1.6, (1, 1, 1)), (w, col)):
        cv.setStrokeColorRGB(*cl); cv.setLineWidth(wd)
        p = cv.beginPath(); p.moveTo(*P_[0])
        for q in P_[1:]:
            p.lineTo(*q)
        cv.drawPath(p, stroke=1, fill=0)
    cv.restoreState()


def sec_a(x, ytop):
    """Τομή Β–Ν μέσα από την ΟΠ2 (x = 8,60), βλέποντας προς ανατολή: Υπν.2 | κούτελο | Δ3.1 με το χιτώνιο | λωρίδα εισόδου."""
    import el_sheets as SH
    from el_det import Sec, txt
    K = M.KOUT; c = M.COND; cv = SH.C()
    SH._cap(x, ytop, "ΤΟΜΗ Α · ΚΑΘΕΤΑ ΣΤΟ ΔΟΚΑΡΙ, ΜΕΣΑ ΑΠΟ ΤΗΝ ΟΠ2", "0,80 m από την κολόνα Κ3 · βλέπουμε προς ανατολή · 1:7,5")
    a, b, z0 = 4.38, 5.46, 2.26
    sc = Sec(x, ytop - 30 - (3.0 - z0) * S75, S75, a, z0)
    hole = [h for h in M.HOLES if h["id"] == "ΟΠ2"][0]
    bm = [q for q in A.BEAMS if q[0] == "Δ3.1"][0]; soff = A.beam_soffit(bm[1]); y0b, y1b = bm[3], bm[5]
    sbN = A.SLABS[_zone("Ζ15")["slab"]]; sbS = A.SLABS[_zone("Ζ2")["slab"]]
    lvB = _zone("Ζ10")["level"]; lvS = _zone("Ζ2")["level"]; lvK = K["lv"]
    wb = _wall("T2-06")
    # σκυρόδεμα
    sc.rect(a, sbN, y0b, 2.98, fill=CONC); sc.rect(y1b, sbS, b, 2.98, fill=CONC); sc.rect(y0b, soff, y1b, 2.98, fill=BEAMF)
    sc.text((y0b + y1b) / 2, 2.905, "Δ3.1", size=8.0, font="Inter-Bold", color=(1, 1, 1), anchor="c"); sc.text((y0b + y1b) / 2, 2.865, "30/50", size=6.0, color=(1, 1, 1), anchor="c")
    # κενό του κούτελου
    sc.rect(K["y0"] + 0.0125, lvK, y0b, sbN, fill=KFILL, stroke=None, lw=0)
    # γυψοσανίδες: οροφή Υπν.2 · παρειά και κάτω παρειά του κούτελου (ως τον τοίχο Τ2-06) · οροφή λωρίδας
    sc.rect(a, lvB, K["y0"], lvB + 0.0125, fill=GYP, lw=0.5)
    sc.rect(K["y0"], lvK - 0.0125, K["y0"] + 0.0125, lvB + 0.0125, fill=GYP, lw=0.5)
    sc.rect(K["y0"], lvK - 0.0125, wb[1], lvK, fill=GYP, lw=0.5)
    sc.rect(y1b, lvS - 0.0125, b, lvS, fill=GYP, lw=0.5)
    # σκελετός του κούτελου (ορθοστάτης 2,7 cm ως την πλάκα + οδηγός)
    sc.rect(K["y0"] + 0.0125, lvK, K["y0"] + 0.0125 + 0.027, sbN, fill=FRAME, lw=0.3)
    sc.rect(K["y0"] + 0.0125, lvK, y0b, lvK + 0.006, fill=FRAME, lw=0.3)
    # τοίχος Τ2-06 κάτω από το δοκάρι
    sc.rect(wb[1], z0, wb[3], soff, fill=WALLF, lw=0.5)
    sc.rect(wb[1], z0, wb[1] + 0.025, soff, fill=GYP, lw=0.3); sc.rect(wb[3] - 0.025, z0, wb[3], soff, fill=GYP, lw=0.3)
    # χιτώνιο
    r = M.hole_d([h_ for h_ in M.HOLES if h_["id"] == M.COND["hole"]][0]) / 2
    sc.rect(y0b, 2.73 - r, y1b, 2.73 + r, fill=(1, 1, 1), stroke=HOLEC, lw=1.2)
    # ψυκτικά: χαμηλά στο χιτώνιο → ανεβαίνουν στο κενό του Υπν.2
    zr = 2.73 - M.HOLE_IN / 2 + 0.017
    zv = (lvB + 0.0125 + sbN) / 2
    _band(cv, [sc.p(b - 0.02, zr + 0.012), sc.p(y1b + 0.06, zr), sc.p(K["y0"] + 0.075, zr), sc.p(K["y0"] - 0.03, zv), sc.p(a + 0.02, zv)], 0.034 * S75 * 0.42, REFR)
    # αποχέτευση: ψηλά στο χιτώνιο → μέσα στο κούτελο γυρίζει δυτικά (προς εμάς)
    sy = _sy(); zin = sy[1][2]; zout = sy[2][2]; zst = sy[0][2]; yk = sy[3][1]
    hw = c["d"] / 2
    _band(cv, [sc.p(b - 0.02, zst + hw - 0.004), sc.p(y1b, zin + hw), sc.p(y0b, zout + hw), sc.p(yk, zout + hw)], c["d"] * S75, PIPE)
    X, Y = sc.p(yk, zout + hw)
    _circle(cv, X, Y, (hw + c["ins"]) * S75, (0.90, 0.84, 0.95), PIPE, 0.7); _circle(cv, X, Y, hw * S75, PIPE, (1, 1, 1), 0.8); _circle(cv, X, Y, hw * S75 * 0.30, (1, 1, 1), (1, 1, 1), 0)
    # διαστάσεις
    sc.dimh(K["y0"] + 0.0125 + 0.027, y0b, 2.545, "%d" % round(K["clear"] * 100))
    sc.dimh(K["y0"], y0b, 2.335, "%d με σκελετό και φύλλο" % round((K["y1"] - K["y0"]) * 100))
    sc.dimv(K["y0"] - 0.05, lvK, sbN, "%d" % round((sbN - lvK) * 100))
    sc.dimv(b - 0.10, soff, 2.73, "25"); sc.dimv(b - 0.10, 2.73, 2.98, "25")
    # στάθμες / κείμενα
    sc.text(a + 0.015, lvB - 0.035, "ΥΠΝ.2", size=7.0, font="Inter-Bold"); sc.text(a + 0.015, lvB - 0.065, "οροφή +%s" % _f(lvB), size=5.8, color=SH.MUTE)
    sc.text(b - 0.14, lvS - 0.045, "ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ", size=7.0, font="Inter-Bold", anchor="r"); sc.text(b - 0.14, lvS - 0.075, "οροφή +%s" % _f(lvS), size=5.8, color=SH.MUTE, anchor="r")
    sc.text((K["y0"] + wb[1]) / 2, lvK - 0.045, "ΚΟΥΤΕΛΟ +%s" % _f(lvK), size=6.6, font="Inter-Bold", color=PIPE, anchor="c")
    sc.text((K["y0"] + wb[1]) / 2, lvK - 0.072, "= κάτω παρειά του δοκαριού", size=5.4, color=PIPE, anchor="c")
    sc.text(wb[3] + 0.012, 2.30, "τοίχος Υπν.2 | σαλόνι", size=5.2, color=SH.MUTE)
    sc.text(a + 0.015, 2.985, "+2,98 άνω στάθμη πλάκας", size=5.4, color=SH.MUTE, dy=3)
    sc.text(a + 0.015, sbN + 0.02, "πλάκα h=18 · κάτω παρειά +%s" % _f(sbN), size=5.2, color=(1, 1, 1))
    sc.text((y0b + y1b) / 2, 2.73 - r - 0.03, "ΟΠ2 · χιτώνιο Ø90", size=5.6, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    sc.text((y0b + y1b) / 2, 2.73 - r - 0.055, "κέντρο +2,73", size=5.0, color=(1, 1, 1), anchor="c")
    xk = (K["y0"] + 0.04 + y0b) / 2
    sc.text(xk, 2.655, "ΑΠΟΧΕΤΕΥΣΗ", size=5.2, font="Inter-Bold", color=PIPE, anchor="c"); sc.text(xk, 2.630, "Ø32 → πλυντήριο", size=4.8, color=PIPE, anchor="c")
    sc.text(xk, 2.510, "ΚΕΝΟ", size=5.2, font="Inter-Bold", color=PIPE, anchor="c")
    sc.text(y1b + 0.02, zr - 0.040, "ψηλά: αποχέτευση Ø32", size=5.0, font="Inter-SemiBold", color=PIPE)
    sc.text(y1b + 0.02, zr - 0.064, "χαμηλά: ψυκτικά", size=5.0, font="Inter-SemiBold", color=REFR)
    sc.text(a + 0.015, lvB - 0.095, "ψυκτικά → ΒΑ εξώστης", size=5.0, color=REFR)
    return sc.oy


def sec_b(x, ytop):
    """Τομή κατά μήκος του δοκαριού μέσα από το κούτελο (y = 4,775), βλέποντας προς ΝΟΤΟ = τη βόρεια παρειά του δοκαριού: αριστερά η ΟΠ2 (ανατολή), δεξιά το πλυντήριο (δύση)."""
    import el_sheets as SH
    from el_det import Sec, txt
    K = M.KOUT; c = M.COND; cv = SH.C()
    SH._cap(x, ytop, "ΤΟΜΗ Β · ΚΑΤΑ ΜΗΚΟΣ ΤΟΥ ΔΟΚΑΡΙΟΥ, ΜΕΣΑ ΑΠΟ ΤΟ ΚΟΥΤΕΛΟ: ΑΠΟ ΤΗΝ ΟΠ2 ΩΣ ΤΟ ΠΛΥΝΤΗΡΙΟ", "όπως το βλέπεις από το Υπν.2 / το χωλ κοιτώντας το δοκάρι (προς νότο) · αριστερά ανατολή, δεξιά δύση · 1:20")
    xa, xb, z0 = 9.47, 3.10, 0.88
    sc = Sec(x, ytop - 30 - (3.0 - z0) * S20, S20, -xa, z0)
    U = lambda v: -v
    sy = _sy(); yk = sy[3][1]
    bm = [q for q in A.BEAMS if q[0] == "Δ3.1"][0]; soff = A.beam_soffit(bm[1])
    sb = A.SLABS[_zone("Ζ15")["slab"]]; lvB = _zone("Ζ10")["level"]; lvK = K["lv"]; lvH = _zone("Ζ4")["level"]
    R = lambda x0, zz0, x1, zz1, **kw: sc.rect(U(x0), zz0, U(x1), zz1, **kw)
    T = lambda xx, zz, s, **kw: sc.text(U(xx), zz, s, **kw)
    # πλάκα · δοκάρι (η βόρεια παρειά του, πίσω από το επίπεδο της τομής)
    R(xa, sb, xb, 2.98, fill=CONC, lw=0.5)
    R(min(xa, bm[4]), soff, max(xb, bm[2]), sb, fill=(0.80, 0.80, 0.84), lw=0.4)
    T(7.55, 2.535, "ΔΟΚΑΡΙ Δ3.1 30/50 (η βόρεια παρειά του) · κάτω παρειά +%s" % _f(soff), size=5.8, font="Inter-Bold", color=(0.30, 0.30, 0.36), anchor="c")
    # κολόνα Κ3 / ανατολικός τοίχος Υπν.2
    R(xa, z0, K["x1"], sb, fill=BEAMF, lw=0.5)
    # κούτελο: κενό + κάτω φύλλο· πίσω του η οροφή του Υπν.2
    R(K["x1"], lvK - 0.0125, K["x0"], lvK, fill=GYP, lw=0.5)
    # τοίχοι που κόβει η τομή
    for wid, nm in (("T2-07", "τοίχος χωλ | Υπν.2  →"), ("T2N-02", ""), ("T2A-01", "τοίχος πίνακα  →")):
        b_ = _wall(wid)
        if b_[1] - 0.01 <= yk <= b_[3] + 0.01:
            R(b_[2], z0, b_[0], sb, fill=WALLF, lw=0.5)
            if nm:
                T(b_[2] + 0.05, 1.30, nm, size=4.8, color=SH.MUTE, anchor="r")
    # οροφή χωλ +2,48 (ως τον τοίχο του πίνακα)
    h0 = _wall("T2A-01")[2]; h1 = _wall("T2-07")[0]
    R(h1, lvH - 0.0125, h0, lvH, fill=GYP, lw=0.5)
    # ντουλάπα χωλ / εσοχή πλυντηρίου (κομμένες από την τομή)
    for wd in W.WARDROBES:
        r_ = wd["r"]
        if r_[1] - 0.01 <= yk <= r_[3] + 0.01 and r_[2] > xb and r_[0] < xa and r_[1] > 4.0:
            if wd.get("washing"):
                R(r_[2], z0, r_[0], lvH - 0.0125, fill=(1, 1, 1), stroke=FURNC, lw=0.6)
                T((r_[0] + r_[2]) / 2, 1.95, "ΕΣΟΧΗ", size=5.4, font="Inter-Bold", color=FURNC, anchor="c"); T((r_[0] + r_[2]) / 2, 1.88, "ΠΛΥΝΤΗΡΙΟΥ", size=5.4, font="Inter-Bold", color=FURNC, anchor="c")
            else:
                R(r_[2], z0, r_[0], lvH - 0.0125, fill=(0.975, 0.955, 0.985), stroke=FURNC, lw=0.6)
                T((r_[0] + r_[2]) / 2, 1.70, "ΝΤΟΥΛΑΠΑ ΧΩΛ – ως την οροφή +%s" % _f(lvH), size=5.6, font="Inter-Bold", color=FURNC, anchor="c")
    # άνοιγμα χωλ → σαλόνι
    op0, op1 = _wall("T2N-02")[2], _wall("T2-07")[0]
    T((op0 + op1) / 2, 1.70, "ΑΝΟΙΓΜΑ", size=5.6, font="Inter-Bold", color=SH.MUTE, anchor="c"); T((op0 + op1) / 2, 1.62, "χωλ → σαλόνι", size=5.0, color=SH.MUTE, anchor="c")
    # Υπν.2: ο τοίχος του κάτω από το δοκάρι + η οροφή του δωματίου (μπροστά από την τομή, διακεκομμένη)
    T((K["x0"] + K["x1"]) / 2, 1.70, "ΥΠΝ.2 – τοίχος προς το σαλόνι, κάτω από το δοκάρι", size=5.6, font="Inter-Bold", color=SH.MUTE, anchor="c")
    # οπές στο δοκάρι
    for h in M.HOLES:
        if h["beam"] != "Δ3.1":
            continue
        X, Y = sc.p(U(h["x"]), 2.73); r = M.hole_d(h) / 2 * S20
        _circle(cv, X, Y, r, (1, 1, 1), HOLEC, 1.0)
        if h["id"] != c["hole"]:                                                  # η ΟΠ2 γράφεται στην ετικέτα της ροής
            txt(X, Y + r + 6, h["id"], size=5.6, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    # αποχέτευση
    hw = c["d"] / 2
    run = [p for p in sy if abs(p[1] - yk) < 1e-6]
    top = [p for p in run if p[2] > 2.5]; xs_, xe_ = top[0], top[-1]
    P_ = [sc.p(U(xs_[0]), xs_[2] + hw), sc.p(U(xe_[0]), xe_[2] + hw), sc.p(U(xe_[0]), run[-1][2])]
    _band(cv, P_, max(2.6, c["d"] * S20), PIPE)
    X, Y = sc.p(U(xe_[0]), run[-1][2]); _circle(cv, X, Y, 4.2, (1, 1, 1), PIPE, 1.2)
    T(xe_[0] + 0.07, run[-1][2] + 0.09, "σιφώνι", size=5.0, font="Inter-Bold", color=PIPE, anchor="r"); T(xe_[0] + 0.07, run[-1][2] + 0.03, "πλυντηρίου", size=5.0, font="Inter-Bold", color=PIPE, anchor="r")
    T(xe_[0] + 0.07, run[-1][2] - 0.035, "ύψος ενδεικτικό", size=4.4, color=SH.MUTE, anchor="r")
    # στάθμες ροής
    xw = _wall("T2-07")[2]
    zw = xs_[2] - (xs_[0] - xw) * (xs_[2] - xe_[2]) / (xs_[0] - xe_[0])
    for xx, zz, an in ((xs_[0], xs_[2], "c"), (xw, zw, "c"), (xe_[0], xe_[2], "c")):
        Xp, Yp = sc.p(U(xx), zz + hw)
        SH.ptext(Xp, Yp + 9, ("ΟΠ2 · " if xx == xs_[0] else "") + "ροή +%s" % _f(zz, 3), 5.0, "Inter-Bold", PIPE, an, 0, True, pad=0.8)
    xm = (xs_[0] + xw) / 2
    sl = (xs_[2] - xe_[2]) / (xs_[0] - xe_[0]) * 100
    T(xm, 2.625, "κλίση %s %%  →" % _f(sl, 1), size=5.8, font="Inter-Bold", color=PIPE, anchor="c")
    hx = [h["x"] for h in M.HOLES if h["beam"] == "Δ3.1" and h["x"] < K["x0"]]
    T(sum(hx) / len(hx), 2.535, "ο Ø32 περνά ΚΑΤΩ από τα χιτώνια ΟΠ1 / ΟΠ5", size=4.8, font="Inter-SemiBold", color=PIPE, anchor="c")
    # διαστάσεις μήκους
    zd = 2.36
    sc.dimh(U(xs_[0]), U(K["x0"]), zd, "%s m μέσα στο κούτελο" % _f(xs_[0] - K["x0"]))
    sc.dimh(U(K["x0"]), U(xe_[0]), zd, "%s m στο κενό της οροφής του χωλ, πάνω από τη ντουλάπα" % _f(K["x0"] - xe_[0]))
    sc.dimv(U(xa) - 12 / S20, lvK, sb, "%d" % round((sb - lvK) * 100))
    T(K["x1"] - 0.06, lvK - 0.075, "ΚΟΥΤΕΛΟ +%s σε όλο το πλάτος του Υπν.2" % _f(lvK), size=5.6, font="Inter-Bold", color=PIPE)
    T(h1 - 0.06, lvH - 0.075, "ΧΩΛ: όλη η οροφή +%s" % _f(lvH), size=5.6, font="Inter-Bold", color=BLUE)
    T(xa - 0.03, 2.89, "πλάκα", size=5.0, color=(1, 1, 1))
    return sc.oy


def sheet(no="ΗΛ-16"):
    import el_docs as DC
    import el_sheets as SH
    K = M.KOUT; c = M.COND
    y = DC.title("ΚΟΥΤΕΛΟ ΔΙΠΛΑ ΣΤΟ ΔΟΚΑΡΙ ΤΟΥ ΣΑΛΟΝΙΟΥ – ΑΠΟΧΕΤΕΥΣΗ ΚΛΙΜΑΤΙΣΤΙΚΟΥ", "κενό 15 × 32 cm κολλητά στη Δ3.1 · χωλ +2,48 · Ø32 από την ΟΠ2 ως το σιφώνι του πλυντηρίου")
    x0 = DC.X0 + 40
    yA = sec_a(x0, y)
    wA = (5.46 - 4.38) * S75
    sy = _sy(); run = [p for p in sy if abs(p[1] - sy[3][1]) < 1e-6 and p[2] > 2.5]
    sb = A.SLABS[_zone("Ζ15")["slab"]]
    xr = x0 + wA + 34; wr = (DC.X1 - xr - 18) / 2
    f1 = DC.Flow(xr, y - 2, wr, size=6.6, name="ΗΛ-16/1"); f2 = DC.Flow(xr + wr + 18, y - 2, wr, size=6.6, name="ΗΛ-16/2")
    Bq = dict(bullet="•", size=6.6)
    f1.h("ΤΙ ΖΗΤΗΘΗΚΕ (ιδιοκτήτης 20/11)", fill=PIPE)
    f1.p("Το δοκάρι του σαλονιού (Δ3.1) «μεγαλώνει» προς τα δωμάτια: κούτελο γυψοσανίδας κολλητά στη βόρεια παρειά του, με κενό 15 cm και ύψος 30.", **Bq)
    f1.p("Όλο το χωλ στο +%s, όπως και το κούτελο." % _f(K["lv"]), **Bq)
    f1.p("Η αποχέτευση του κλιματιστικού σαλονιού μπαίνει από την ΟΠ2, τρέχει μέσα στο κενό αυτό και πέφτει στο πλυντήριο.", **Bq)
    f1.h("ΠΩΣ ΒΓΑΙΝΕΙ")
    f1.p("Κάτω παρειά του κούτελου +%s = η κάτω παρειά του δοκαριού. Από εκεί ως την πλάκα (+%s) το κενό έχει ύψος %d cm – η πλάκα εκεί είναι 18 cm." % (_f(K["lv"]), _f(sb), round((sb - K["lv"]) * 100)), **Bq)
    f1.p("Πάχος: %d cm καθαρά από το δοκάρι ως τον σκελετό. Με τον σκελετό (2,7) και το φύλλο (1,25) το κούτελο βγαίνει %d cm από το δοκάρι." % (round(K["clear"] * 100), round((K["y1"] - K["y0"]) * 100)), **Bq)
    f1.p("Φαίνεται ΜΟΝΟ στο Υπν.2, σε όλο το πλάτος του δωματίου (από τοίχο σε τοίχο – κανένα δόντι). Μαζί με τα 20 cm του δοκαριού που ήδη προεξέχουν, η χαμηλή λωρίδα στον νότιο τοίχο του Υπν.2 γίνεται %d cm στο +%s." % (round((_wall("T2-06")[1] - K["y0"]) * 100), _f(K["lv"])), **Bq)
    f1.p("Στο χωλ δεν φαίνεται κούτελο: όλη η οροφή είναι +%s και το κενό της (32 cm) είναι ενιαίο. Η ντουλάπα του χωλ φτάνει ως το +%s." % (_f(K["lv"]), _f(K["lv"])), **Bq)
    f2.h("Η ΑΠΟΧΕΤΕΥΣΗ Ø32 – ΒΗΜΑ ΒΗΜΑ", fill=PIPE)
    L1 = math.hypot(sy[1][0] - sy[0][0], sy[1][1] - sy[0][1])
    f2.p("Η αντλία του μηχανήματος ανεβάζει το νερό κολλητά στην πλάκα της λωρίδας εισόδου (ροή +%s)." % _f(sy[0][2], 3), bold="1", size=6.6)
    f2.p("%s m με 1 %% μέσα στο κενό της λωρίδας ως το δοκάρι." % _f(L1, 1), bold="2", size=6.6)
    f2.p("Περνά από την ΟΠ2 ΨΗΛΑ στο χιτώνιο (ροή +%s). Από κάτω του, στο ίδιο χιτώνιο, τα ψυκτικά." % _f(sy[1][2], 3), bold="3", size=6.6)
    f2.p("Μέσα στο κούτελο γυρίζει δυτικά και τρέχει κολλητά στο δοκάρι: %s m στο Υπν.2, τρύπα στον τοίχο χωλ | Υπν.2, %s m στο κενό του χωλ πάνω από τη ντουλάπα. Κλίση 2,6 %% (14 cm σε 5,25 m): έτσι στο χωλ περνά 1 cm ΚΑΤΩ από τα χιτώνια ΟΠ1 / ΟΠ5 και τα καλώδια βγαίνουν ελεύθερα από πάνω του." % (_f(run[0][0] - K["x0"]), _f(K["x0"] - run[-1][0])), bold="4", size=6.6)
    f2.p("Πάνω από την εσοχή του πλυντηρίου (ροή +%s, %s cm πάνω από το φύλλο της οροφής) πέφτει ίσια στο σιφώνι του πλυντηρίου." % (_f(run[-1][2], 3), _f((run[-1][2] - K["lv"] - 0.0125) * 100, 0)), bold="5", size=6.6)
    f2.h("ΠΡΟΣΟΧΗ")
    f2.p("Στην ΟΠ2 χωρούν και τα τρία μόνο αν ο σωλήνας αερίου έχει μόνωση 9 mm (Ø34). Με 13 mm (Ø42) δεν χωρούν.", **Bq)
    f2.p("Τα ψυκτικά βγαίνουν από το χιτώνιο προς τα ανατολικά – βόρεια (προς τη ντουλάπα του Υπν.2)· η αποχέτευση προς τα δυτικά. Δεν διασταυρώνονται.", **Bq)
    f2.p("Ø32 PVC κολλητός, με μόνωση 9 mm, στηρίγματα ανά 1 m. Δοκιμή με νερό ΠΡΙΝ κλείσει το κούτελο και η οροφή του χωλ.", **Bq)
    f2.p("Σύνδεση στο σιφώνι του πλυντηρίου πάνω από την οσμοπαγίδα.", **Bq)
    f2.p("Οι αλλαγές οροφής (χωλ +2,48, κούτελο) ισχύουν εδώ· το τεύχος ανόψεων δεν έχει ξαναβγεί.", **Bq)
    yB = min(yA, f1.y, f2.y) - 22
    yb = sec_b(DC.X0 + 30, yB)
    assert yb >= DC.YB + 2, "ΗΛ-16: η τομή Β δεν χωρά (%.0f pt)" % (DC.YB - yb)
    DC.finish(no, "ΚΟΥΤΕΛΟ Δ3.1 – ΑΠΟΧΕΤΕΥΣΗ ΚΛΙΜΑΤΙΣΤΙΚΟΥ", "τομή μέσα από την ΟΠ2 · τομή κατά μήκος ως το πλυντήριο", "Τομές 1:7,5 και 1:20 · A3")
