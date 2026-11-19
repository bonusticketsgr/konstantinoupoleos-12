"""ΗΛ-14 ΚΑΤΕΒΑΣΜΑΤΑ ΣΤΟΥΣ ΤΟΙΧΟΥΣ: μία τομή σε κάθε τοίχο που έχει πρίζες / διακόπτες – από πού μπαίνουν τα καλώδια στον τοίχο.
Η γεωμετρία κάθε τομής (τοίχοι, δοκάρια, στάθμες οροφής) διαβάζεται από τα μοντέλα τοιχοποιιών / ανόψεων· το M.DROPS λέει μόνο ΠΩΣ μπαίνουν.
env() το χρησιμοποιούν και οι έλεγχοι (el_checks) και το φύλλο."""
import math
import el_geom as G

M = W = A = None
WIN = 0.46            # μισό πλάτος τομής (m)
Z0, ZS, ZT = 2.215, 2.78, 2.98
BRICK = ("T1", "T4", "T4A", "T5", "T10")
MIN_GAP = 0.06        # ελάχιστο καθαρό κάτω από δοκάρι, πάνω από το φύλλο της οροφής, για να περάσει καλώδιο (ίδιο με el_route.MIN_UNDER)


def bind(model):
    global M, W, A
    M = model; W = model.W; A = model.A


def _lvl(x, y):
    l = [z["level"] for z in A.ZONES for r in z["rects"] if G.in_rect(x, y, r)]
    return min(l) if l else None


def env(d):
    """Τι υπάρχει στην τομή του κατεβάσματος d, κάθετα στον τοίχο. c = συντεταγμένη κάθετα στον τοίχο (A = μικρό c: βόρεια / δυτικά)."""
    x, y, f = d["pt"]
    horiz = f in ("N", "S")                       # τοίχος Α–Δ → η τομή είναι Β–Ν, c = y
    al = x if horiz else y
    pt = (lambda c: (al, c)) if horiz else (lambda c: (c, al))
    ci = (lambda r: (r[1], r[3])) if horiz else (lambda r: (r[0], r[2]))
    ai = (lambda r: (r[0], r[2])) if horiz else (lambda r: (r[1], r[3]))
    wb = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] == d["walls"][0]][0]
    w0, w1 = ci(wb); wc = (w0 + w1) / 2
    c0, c1 = wc - WIN, wc + WIN
    walls = []
    for w in W.WALLS:
        if not G.is_rect(w["pts"]):
            continue
        b = W.bbox(w["pts"]); a0, a1 = ai(b); q0, q1 = ci(b)
        if a0 - 0.005 <= al <= a1 + 0.005 and q1 > c0 and q0 < c1:
            walls.append((w["id"], w["type"], max(q0, c0), min(q1, c1)))
    cols = []
    for p in W.COLS:
        if G.is_rect(p):
            b = W.bbox(p); a0, a1 = ai(b); q0, q1 = ci(b)
            if a0 <= al <= a1 and q1 > c0 and q0 < c1:
                cols.append((max(q0, c0), min(q1, c1)))
    beams = []
    for b in A.BEAMS:
        r = b[2:6]; a0, a1 = ai(r); q0, q1 = ci(r)
        if a0 - 0.005 <= al <= a1 + 0.005 and q1 > c0 and q0 < c1:
            beams.append((b[0], b[1], q0, q1, A.beam_soffit(b[1])))
    over = [b for b in beams if b[2] - 0.005 <= wc <= b[3] + 0.005]     # δοκάρι πάνω από τον τοίχο
    solid = [(q0, q1) for _, _, q0, q1 in walls] + cols
    ceil = []                                                           # [(ca, cb, στάθμη)]
    rec = []                                                            # [(ca, cb)] κουρτινόθηκες
    n = int(round((c1 - c0) / 0.01))
    for i in range(n):
        c = c0 + (i + 0.5) * 0.01
        if any(q0 - 1e-6 <= c <= q1 + 1e-6 for q0, q1 in solid):
            continue
        if any(G.in_rect(*(pt(c) + (k_["rect"],))) for k_ in A.CURTAINS):          # κουρτινόθηκη: ανοιχτή ως την πλάκα – δεν είναι κενό οροφής
            if rec and abs(rec[-1][1] - (c - 0.005)) < 1e-6:
                rec[-1] = (rec[-1][0], c + 0.005)
            else:
                rec.append((c - 0.005, c + 0.005))
            continue
        lv = [z["level"] for z in A.ZONES for r in z["rects"] if G.in_rect(*(pt(c) + (r,)))]
        if len(lv) > 1:                              # οι ζώνες των ανόψεων «μπαίνουν» κάτω από τους τοίχους: κοντά στον τοίχο ισχύει η ζώνη του χώρου της ίδιας πλευράς
            lv2 = [z["level"] for z in A.ZONES for r in z["rects"] if G.in_rect(*(pt(w0 - 0.15 if c < wc else w1 + 0.15) + (r,)))]
            lv = [q for q in lv if q in lv2] or lv
        L = min(lv) if lv else None
        if L is None:
            continue
        if ceil and abs(ceil[-1][1] - (c - 0.005)) < 1e-6 and ceil[-1][2] == L:
            ceil[-1] = (ceil[-1][0], c + 0.005, L)
        else:
            ceil.append((c - 0.005, c + 0.005, L))
    furn = []
    for f_ in W.WARDROBES:
        r = f_["r"]; a0, a1 = ai(r); q0, q1 = ci(r)
        if a0 <= al <= a1 and q1 > c0 and q0 < c1:
            furn.append((max(q0, c0), min(q1, c1)))

    def side_level(s):
        """Στάθμη της οροφής ακριβώς δίπλα στον τοίχο (και κάτω από το δοκάρι, αν προεξέχει) στην πλευρά s."""
        seg = [q for q in ceil if (q[1] <= w0 + 0.03 if s == "A" else q[0] >= w1 - 0.03)]
        if not seg:
            return None
        q = max(seg, key=lambda q: q[1]) if s == "A" else min(seg, key=lambda q: q[0])
        if any((r_[1] > q[1] - 1e-6 and r_[1] <= w0 + 0.03) if s == "A" else (r_[0] < q[0] + 1e-6 and r_[0] >= w1 - 0.03) for r_ in rec):
            return None                                                 # ανάμεσα στην οροφή και τον τοίχο μεσολαβεί κουρτινόθηκη
        return q[2]
    return dict(horiz=horiz, al=al, w0=w0, w1=w1, wc=wc, c0=c0, c1=c1, walls=walls, cols=cols, beams=beams, over=over, ceil=ceil, rec=rec, furn=furn,
                LA=side_level("A"), LB=side_level("B"), type=[w for w in W.WALLS if w["id"] == d["walls"][0]][0]["type"])


def verdict(d, e=None):
    """(ok, σύντομη ετυμηγορία, καθαρό κενό m ή None) – ελέγχει ότι ο τρόπος που δηλώνει το M.DROPS γίνεται με τη γεωμετρία των μοντέλων."""
    e = e or env(d)
    m = d["mode"]; over = e["over"]
    if m == "top":
        L = e["LA"] if d["frm"] == "A" else e["LB"]
        ok = not over and L is not None and L <= ZS - 0.03
        return ok, "ΑΠΟ ΤΟ ΤΑΒΑΝΙ, ΙΣΙΑ", (ZS - L - 0.0125) if L else None
    if m == "side":
        L = e["LA"] if d["frm"] == "A" else e["LB"]
        if not over or L is None:
            return False, "δεν είναι κάτω από δοκάρι / δεν υπάρχει οροφή", None
        gap = over[0][4] - L - 0.0125
        return gap >= MIN_GAP - 1e-6, "ΚΑΤΩ ΑΠΟ ΤΟ ΔΟΚΑΡΙ – κενό %s cm" % G.fmt(gap * 100, 1 if abs(gap * 100 - round(gap * 100)) > 0.05 else 0), gap
    if m == "via":
        src = [q for q in M.DROPS if d["src"] in q["walls"]]
        a = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] == d["walls"][0]][0]; b = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] == d["src"]][0]
        touch = a[0] <= b[2] + 0.02 and b[0] <= a[2] + 0.02 and a[1] <= b[3] + 0.02 and b[1] <= a[3] + 0.02
        ok = bool(src) and src[0]["mode"] in ("top", "side") and verdict(src[0])[0] and touch
        return ok, ("ΟΡΙΖΟΝΤΙΑ ΜΕΣΑ ΣΤΟΝ ΤΟΙΧΟ στο +%s, από τον τοίχο %s" % (G.fmt(M.ZR), src[0]["id"])) if src else ";", None
    if m in ("back", "furn"):
        r = d["inn"]; pts = [(r[0] + (r[2] - r[0]) * i / 6.0, r[1] + (r[3] - r[1]) * j / 6.0) for i in range(1, 6) for j in range(1, 6)]
        free = [p for p in pts if not any(G.in_rect(p[0], p[1], b[2:6]) for b in A.BEAMS)]
        return bool(free), "ΜΕΣΑ ΑΠΟ ΤΗ ΝΤΟΥΛΑΠΑ" if m == "back" or e["furn"] else "ΠΙΣΩ ΑΠΟ ΤΗ ΝΤΟΥΛΑΠΑ → ΜΕΣΑ ΣΤΗΝ ΕΠΕΝΔΥΣΗ", None
    if m == "floor":
        fr = [q for q in M.FLOOR_RUNS if q["id"] == d["run"]]
        if not fr:
            return False, "λείπει η όδευση δαπέδου", None
        b = [W.bbox(w["pts"]) for w in W.WALLS if w["id"] == fr[0]["wall"]][0]
        ok = G.in_rect(fr[0]["pts"][-1][0], fr[0]["pts"][-1][1], b, tol=0.03) and fr[0]["wall"] in d["walls"]
        return ok, "ΑΠΟ ΤΟ ΠΑΤΩΜΑ", None
    return False, ";", None


def top_possible(e):
    """Γίνεται κατέβασμα από πάνω σε αυτή την τομή; (για να φαίνεται ότι όπου δηλώνεται άλλος τρόπος, πράγματι δεν γίνεται από πάνω)"""
    if not e["over"]:
        return True
    zs = e["over"][0][4]
    return any(L is not None and zs - L - 0.0125 >= MIN_GAP - 1e-6 for L in (e["LA"], e["LB"]))


# ---------------------------------------------------------------- σχεδίαση
def draw(d, x, ytop, w, h):
    import el_sheets as SH
    from el_det import Sec, txt, ln, box
    import el_draw as D
    e = env(d); ok, vd, gap = verdict(d, e)
    s = 72 / 25.4 * 1000 / 15.0
    dec = bool(d.get("run") and [q for q in M.FLOOR_RUNS if q["id"] == d["run"] and q.get("decision")])
    col_t = (0.78, 0.10, 0.10) if dec else D.INK
    txt(x, ytop - 8, "%s · %s" % (d["id"], d["title"]), size=6.6, font="Inter-Bold", color=col_t)
    txt(x, ytop - 16, "τοίχος " + " · ".join(q.replace("T", "Τ") for q in d["walls"]), size=4.9, color=D.MUTE)
    sh = (ZT - Z0) * s
    sc = Sec(x + (w - 2 * WIN * s) / 2 - 2, ytop - 22 - sh, s, e["c0"], Z0)
    c0, c1 = e["c0"], e["c1"]
    sc.rect(c0, ZS, c1, ZT, fill=SH.CONC, lw=0.4)
    for nm, sec, q0, q1, zs in e["beams"]:
        a, b = max(q0, c0), min(q1, c1)
        sc.rect(a, zs, b, ZT, fill=SH.BEAMF, lw=0.5)
        if b - a > 0.16:
            sc.text((a + b) / 2, ZT - 0.075, nm, size=5.2, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    for q0, q1 in e["cols"]:
        sc.rect(q0, Z0, q1, ZS, fill=SH.BEAMF, lw=0.4)
    for q0, q1 in e["furn"]:
        top = min([L for a, b, L in e["ceil"] if a < q1 and b > q0] or [2.70])
        cuts = sorted(set([q0, q1] + [v_ for bm in e["beams"] for v_ in (bm[2], bm[3]) if q0 < v_ < q1]))
        for a_, b_ in zip(cuts, cuts[1:]):                           # κάτω από δοκάρι το έπιπλο φτάνει ως την κάτω παρειά του
            tb = min([bm[4] for bm in e["beams"] if bm[2] - 1e-6 <= (a_ + b_) / 2 <= bm[3] + 1e-6] or [top])
            sc.rect(a_, Z0, b_, min(top, tb), fill=(0.95, 0.90, 0.80), stroke=(0.60, 0.50, 0.35), lw=0.4)
    for a, b, L in e["ceil"]:
        sc.rect(a, L, b, L + 0.0125, fill=SH.GYP, lw=0.35)
    for a, b in e["rec"]:                                            # κουρτινόθηκη: ανοιχτή σχισμή ως την πλάκα
        Lr = min([q[2] for q in e["ceil"]] or [2.70])
        zt_ = min([bm[4] for bm in e["beams"] if bm[2] < b and bm[3] > a] or [ZS])
        sc.rect(a, Lr, b, zt_, fill=(1.0, 0.97, 0.88), stroke=(0.70, 0.55, 0.20), lw=0.4, dash=[1.6, 1.2])
        if b - a > 0.12:
            sc.text((a + b) / 2, Lr - 0.055, "κουρτινόθηκη", size=4.4, color=(0.60, 0.45, 0.10), anchor="c")
    cav = {}
    for wid, ty, q0, q1 in e["walls"]:
        zt = min([b[4] for b in e["beams"] if b[2] - 0.005 <= (q0 + q1) / 2 <= b[3] + 0.005] or [ZS])
        if ty in BRICK:
            sc.rect(q0, Z0, q1, zt, fill=(0.88, 0.76, 0.68), lw=0.4)
        elif ty == "T9":
            sc.rect(q0, Z0, q1, zt, fill=SH.GYP, lw=0.4)
        elif ty == "T3":
            room_hi = any(abs(o[2] - q0) < 0.02 or abs(o[3] - q0) < 0.02 for o in e["walls"] if o[0] != wid) or any(abs(k[1] - q0) < 0.02 for k in e["cols"])
            sc.rect(q0, Z0, q1, zt, fill=(1, 1, 1), lw=0.4)
            if room_hi:
                sc.rect(q1 - 0.025, Z0, q1, zt, fill=SH.GYP, lw=0.3); cav[wid] = (q0 + q1 - 0.025) / 2
            else:
                sc.rect(q0, Z0, q0 + 0.025, zt, fill=SH.GYP, lw=0.3); cav[wid] = (q0 + 0.025 + q1) / 2
        else:
            sc.rect(q0, Z0, q1, zt, fill=(1, 1, 1), lw=0.4)
            sc.rect(q0, Z0, q0 + 0.025, zt, fill=SH.GYP, lw=0.3); sc.rect(q1 - 0.025, Z0, q1, zt, fill=SH.GYP, lw=0.3); cav[wid] = (q0 + q1) / 2
    hc = cav.get(d["walls"][0], e["wc"])
    for a, b, L in e["ceil"]:
        if b - a > 0.14:
            sc.text((a + b) / 2, L - 0.055, "+" + G.fmt(L), size=4.6, color=D.MUTE, anchor="c")
    sc.text(c0 + 0.01, Z0 + 0.015, d["la"], size=4.8, font="Inter-SemiBold"); sc.text(c1 - 0.01, Z0 + 0.015, d["lb"], size=4.8, font="Inter-SemiBold", anchor="r")
    GO, NO = (0.05, 0.50, 0.25), (0.80, 0.10, 0.10)
    m = d["mode"]; sg = -1 if d.get("frm") == "A" else 1
    if m == "top":
        L = e["LA"] if d["frm"] == "A" else e["LB"]; zv = min(ZS - 0.035, L + 0.07)
        SH._path(sc, [(hc + sg * 0.34, zv), (hc, zv), (hc, Z0 + 0.03)], lw=1.5)
    elif m == "side":
        b = e["over"][0]; L = e["LA"] if d["frm"] == "A" else e["LB"]; zg = (b[4] + L + 0.0125) / 2; hb = b[2] if d["frm"] == "A" else b[3]
        far = max(c0 + 0.02, hb - 0.16) if d["frm"] == "A" else min(c1 - 0.02, hb + 0.16)
        SH._path(sc, [(far, ZS - 0.05), (hb + sg * 0.035, ZS - 0.05), (hb + sg * 0.035, zg), (hc, zg), (hc, Z0 + 0.03)], lw=1.5)
    else:
        zx = min([b[4] for b in e["over"]] or [ZS]) - 0.05
        X, Y = sc.p(hc, zx)
        for dx, dy in ((1, 1), (1, -1)):
            ln(X - 4 * dx, Y - 4 * dy, X + 4 * dx, Y + 4 * dy, col=NO, lw=1.3)
        c = SH.C()

        def ring(h_, z_):
            X_, Y_ = sc.p(h_, z_); c.saveState(); c.setStrokeColorRGB(*SH.CABLE); c.setFillColorRGB(1, 1, 1); c.setLineWidth(1.2); c.circle(X_, Y_, 4.2, stroke=1, fill=1)
            c.setFillColorRGB(*SH.CABLE); c.circle(X_, Y_, 1.5, stroke=0, fill=1); c.restoreState()
        if m == "via":                                   # έρχεται ΚΑΤΑ ΜΗΚΟΣ του τοίχου, μέσα του, στο +2,30 (κάτω από το δοκάρι) και κατεβαίνει
            SH._path(sc, [(hc, M.ZR), (hc, Z0 + 0.03)], lw=1.5); ring(hc, M.ZR)
            side_ = 1 if (e["c1"] - hc) > (hc - e["c0"]) else -1
            sc.text(hc + side_ * 0.06, M.ZR - 0.015, "+" + G.fmt(M.ZR), size=4.8, font="Inter-Bold", color=SH.CABLE, anchor="l" if side_ > 0 else "r")
        elif m in ("back", "furn"):
            fq = e["furn"][0] if e["furn"] else None
            if fq:                                       # κατεβαίνει ΜΕΣΑ στο έπιπλο, μακριά από το δοκάρι, και περνά στον τοίχο στο ύψος κάθε κουτιού (κάτω από το σχέδιο)
                bm = e["over"][0] if e["over"] else None
                hf = (fq[0] + 0.055) if (bm and fq[0] < bm[2] - 0.02) else ((fq[1] - 0.055) if (bm and fq[1] > bm[3] + 0.02) else (fq[0] + fq[1]) / 2)
                if d.get("hf") is not None:
                    hf = d["hf"]
                ztop = min([L for a, b, L in e["ceil"] if a - 0.01 <= hf <= b + 0.01] or [2.70]) + 0.07
                SH._path(sc, [(hf, min(ztop, ZS - 0.035)), (hf, Z0 + 0.03)], lw=1.5)
                Xa, Ya = sc.p(hf, Z0 + 0.10); Xb, Yb = sc.p(hc, Z0 + 0.10)
                ln(Xa, Ya, Xb - (3 if Xb > Xa else -3), Yb, col=SH.CABLE, lw=0.9, dash=[2, 1.4])
                SH.P._arrow(Xb, Yb, 0 if Xb > Xa else 180, 2.6, SH.CABLE)
            else:                                        # το έπιπλο δεν είναι σε αυτή την τομή: εδώ το καλώδιο τρέχει ΚΑΤΑ ΜΗΚΟΣ, μέσα στην επένδυση, χαμηλά
                ring(hc, Z0 + 0.10)
                sc.text(hc + 0.07, Z0 + 0.085, "+" + G.fmt(M.ZLOW), size=4.8, font="Inter-Bold", color=SH.CABLE)
        elif m == "floor":
            SH._path(sc, [(hc, Z0 + 0.02), (hc, Z0 + 0.30)], lw=1.5)
    yy = ytop - 22 - sh - 9
    vcol = NO if dec else (GO if m in ("top", "side") else (0.75, 0.42, 0.05))
    yv = D.para(x, yy, ("ΟΧΙ ΑΠΟ ΠΑΝΩ → " if m not in ("top", "side") else "") + vd, w - 10, size=5.5, font="Inter-Bold", color=vcol if ok else NO)
    yb = D.para(x, yv + 1.0, d["txt"], w - 8, size=5.3)
    return yb


def sheet(no="ΗΛ-14"):
    import el_docs as DC
    import el_sheets as SH
    y = DC.title("ΚΑΤΕΒΑΣΜΑΤΑ ΣΤΟΥΣ ΤΟΙΧΟΥΣ – ΤΟΜΕΣ", "μία τομή σε κάθε τοίχο με πρίζες / διακόπτες: από πού μπαίνουν τα καλώδια · κόκκινη γραμμή = καλώδια · "
                 "× = από πάνω δεν γίνεται · κύκλος = τρέχουν οριζόντια μέσα στον τοίχο · βέλος από κάτω = από το πάτωμα")
    X0 = DC.X0; n = 6; cw = (DC.X1 - X0) / n
    rows = int(math.ceil(len(M.DROPS) / float(n))); rh = (y - DC.YB - 4) / rows
    for i, d in enumerate(M.DROPS):
        cx, cy = X0 + (i % n) * cw, y - (i // n) * rh
        yb = draw(d, cx, cy, cw, rh)
        assert yb >= cy - rh + 1, "ΗΛ-14: το κείμενο της τομής %s ξεχειλίζει %.0f pt" % (d["id"], cy - rh - yb)
        if i % n:
            SH.ln(cx - 5, cy - 2, cx - 5, cy - rh + 6, col=SH.FAINT, lw=0.4)
    DC.finish(no, "ΚΑΤΕΒΑΣΜΑΤΑ ΣΤΟΥΣ ΤΟΙΧΟΥΣ – ΤΟΜΕΣ", "τοίχοι, δοκάρια και στάθμες οροφής από τα σχέδια τοιχοποιιών / ανόψεων", "Τομές 1:15 · A3")
