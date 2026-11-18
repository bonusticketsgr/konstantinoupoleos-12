"""Σχεδιασμένα φύλλα χωρίς κάτοψη: ΗΛ-10 μονογραμμικό σχέδιο και όψη του πίνακα «ΓΠ» · ΗΛ-16 λεπτομέρειες
(τομή διέλευσης δοκού ΔΠ · ο πίνακας στον τοίχο των 70 cm σε κάτοψη και όψη · ύψη τοποθέτησης · πίνακες διελεύσεων και οδεύσεων).
Όλη η γεωμετρία / τα κυκλώματα από τα μοντέλα (b1_el.py · τοιχοποιίες · ανόψεις)."""
import math
import el_draw as D
from el_draw import P, INK, MUTE, FAINT, PAGE_W, PAGE_H, SW, wrap, PWR, LGT, SWC, DAT, FIR, HVC, AUT, FEED
import el_checks as CK
import el_geom as G
import el_docs as DC
from el_docs import X0, X1, YT, YB, fz, Flow

M = A = W = None
CONC = (0.62, 0.62, 0.65)
GYP = (0.86, 0.86, 0.88)
SLABC = (0.80, 0.50, 0.10)
RCDC = (0.08, 0.33, 0.70)
RCBOC = (0.47, 0.20, 0.72)


def bind(model):
    global M, A, W
    M, A, W = model, model.A, model.W
    CK.bind(model)


def C():
    return P.C


def txt(x, y, s, size=6.0, font="Inter", color=INK, anchor="l"):
    c = C(); c.setFont(font, size); c.setFillColorRGB(*color)
    {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[anchor](x, y, s)


def vtext(x, ytop, s, font="Inter", size=5.6, color=INK):
    """Κατακόρυφο κείμενο (διαβάζεται από κάτω προς τα πάνω) που ΤΕΛΕΙΩΝΕΙ στο ytop."""
    c = C(); c.saveState(); c.translate(x, ytop); c.rotate(90); c.setFont(font, size); c.setFillColorRGB(*color); c.drawRightString(0, 0, s); c.restoreState()


def ln(x0, y0, x1, y1, col=INK, lw=0.9, dash=None):
    c = C(); c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.setDash(dash or []); c.line(x0, y0, x1, y1); c.setDash([])


def box(x, y, w, h, fill=None, stroke=INK, lw=0.7, dash=None):
    c = C()
    if fill:
        c.setFillColorRGB(*fill)
    if stroke:
        c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
    c.setDash(dash or []); c.rect(x, y, w, h, stroke=1 if stroke else 0, fill=1 if fill else 0); c.setDash([])


def tint(col, k=0.86):
    return tuple(1 - (1 - v) * (1 - k) for v in col)


# ================================================================ ΗΛ-10 ΜΟΝΟΓΡΑΜΜΙΚΟ
def _breaker(xc, ytop, label, col=INK, rcbo=False, dash=None, w=19.0, h=13.0):
    box(xc - w / 2, ytop - h, w, h, fill=(1, 1, 1), stroke=col, lw=0.9, dash=dash)
    if rcbo:
        box(xc - w / 2 + 1.6, ytop - h + 1.6, w - 3.2, h - 3.2, stroke=col, lw=0.35)
    txt(xc, ytop - h / 2 - 1.9, label, size=5.4, font="Inter-Bold", color=col, anchor="c")


def sheet_10(no="ΗΛ-10"):
    y = DC.title("ΜΟΝΟΓΡΑΜΜΙΚΟ ΣΧΕΔΙΟ ΓΕΝΙΚΟΥ ΠΙΝΑΚΑ ΔΙΑΜΕΡΙΣΜΑΤΟΣ «ΓΠ»", "τριφασική παροχή 3 × 35 A · 400 / 230 V · %d κυκλώματα + %d εφεδρικά + πρόβλεψη φόρτισης οχήματος" % (len(M.CIRCUITS) - 1, M.SPARE_MCB))
    c = C()
    cc = {q["id"]: q for q in M.CIRCUITS}
    groups = []
    for r in M.RCDS:
        ids = [q["id"] for q in M.CIRCUITS if q["grp"] == r["id"]]
        if r["id"] == "ΔΔΡ-1":
            ids += ["ΕΦ1", "ΕΦ2"]
        groups.append((r["id"], r, ids))
    groups.append(("RCBO", None, [q["id"] for q in M.CIRCUITS if q["grp"].startswith("RCBO")]))
    groups.append(("EV", None, ["EV"]))
    GAP = 0.75
    nslots = sum(len(g[2]) for g in groups) + GAP * (len(groups) - 1)
    xL = X0 + 172.0
    slot = (X1 - 14 - xL) / nslots
    ytop = y + 2
    xin = X0 + 26
    yb = ytop - 92            # κύριος ζυγός
    ys = yb - 44              # ζυγός ομάδας
    # ---- είσοδος: παροχή → Γ.Δ. → ασφάλειες → ζυγός
    ln(xin, ytop, xin, yb, lw=1.8)
    c.setFillColorRGB(*INK); p = c.beginPath(); p.moveTo(xin - 3.5, ytop - 6); p.lineTo(xin + 3.5, ytop - 6); p.lineTo(xin, ytop - 13); p.close(); c.drawPath(p, stroke=0, fill=1)
    txt(xin + 12, ytop - 7, "ΑΠΟ ΤΟΝ ΜΕΤΡΗΤΗ (ισόγειο)", size=6.2, font="Inter-Bold")
    txt(xin + 12, ytop - 15, "%s · 3Φ + N + PE · ≈ %s m" % (M.FEEDER["cable"], fz(M.FEEDER["length"], 0)), size=5.7)
    box(xin - 13, ytop - 42, 26, 16, fill=(1, 1, 1), lw=1.1); txt(xin, ytop - 36.5, "Γ.Δ.", size=5.8, font="Inter-Bold", anchor="c")
    txt(xin + 18, ytop - 33, "Γενικός διακόπτης φορτίου", size=5.7); txt(xin + 18, ytop - 40, "4P 40 A", size=5.7, font="Inter-SemiBold")
    box(xin - 13, ytop - 70, 26, 16, fill=(1, 1, 1), lw=1.1); ln(xin - 8, ytop - 62, xin + 8, ytop - 62, lw=0.8); box(xin - 4, ytop - 64.5, 8, 5, fill=(1, 1, 1), lw=0.7)
    txt(xin + 18, ytop - 61, "Ασφαλειοαποζεύκτης 3P", size=5.7); txt(xin + 18, ytop - 68, "φυσίγγια 3 × 35 A gG", size=5.7, font="Inter-SemiBold")
    ln(xin, yb, X1 - 14, yb, lw=2.2)
    txt(xL, yb + 4, "ζυγός L1 · L2 · L3 · N    (PE σε ξεχωριστή μπάρα)", size=5.4, color=MUTE)
    # ---- απαγωγός υπερτάσεων και λυχνίες
    xs_ = X0 + 96
    ln(xs_, yb, xs_, yb - 12); box(xs_ - 17, yb - 28, 34, 16, fill=(1, 1, 1), stroke=FIR, lw=1.0); txt(xs_, yb - 22.5, "SPD T2", size=5.6, font="Inter-Bold", color=FIR, anchor="c")
    ln(xs_, yb - 28, xs_, yb - 38)
    for i, hw in enumerate((7, 4.6, 2.2)):
        ln(xs_ - hw, yb - 38 - i * 2.4, xs_ + hw, yb - 38 - i * 2.4, lw=0.8)
    txt(xs_, yb - 52, "απαγωγός υπερτάσεων", size=5.2, color=MUTE, anchor="c"); txt(xs_, yb - 58.5, "3P+N · με τη δική του προστασία", size=5.2, color=MUTE, anchor="c")
    xl_ = X0 + 140
    ln(xl_, yb, xl_, yb - 12); c.setStrokeColorRGB(*INK); c.setLineWidth(0.8); c.circle(xl_, yb - 18, 6, stroke=1, fill=0)
    ln(xl_ - 4.2, yb - 22.2, xl_ + 4.2, yb - 13.8, lw=0.6); ln(xl_ - 4.2, yb - 13.8, xl_ + 4.2, yb - 22.2, lw=0.6)
    txt(xl_, yb - 31, "λυχνίες", size=5.2, color=MUTE, anchor="c"); txt(xl_, yb - 37.5, "3 φάσεων", size=5.2, color=MUTE, anchor="c")
    # ---- ομάδες
    x = xL + slot / 2
    ytx = ys - 33
    low = ytx
    for gi, (gid, rcd, ids) in enumerate(groups):
        xs = [x + i * slot for i in range(len(ids))]
        if rcd:
            ln(xs[0], yb, xs[0], yb - 10, lw=1.2)
            box(xs[0] - 12, yb - 27, 44, 17, fill=tint(RCDC), stroke=RCDC, lw=1.1)
            txt(xs[0] + 10, yb - 21, gid, size=6.0, font="Inter-Bold", color=RCDC, anchor="c")
            txt(xs[0] + 38, yb - 17, rcd["name"], size=5.9, font="Inter-Bold", color=RCDC)
            txt(xs[0] + 38, yb - 24.5, "διακόπτης διαρροής " + rcd["spec"], size=5.5, color=RCDC)
            ln(xs[0], yb - 27, xs[0], ys, lw=1.2)
            ln(xs[0], ys, xs[-1], ys, lw=1.6)
        elif gid == "RCBO":
            txt(xs[0] - 10, yb + 14.5, "ΑΤΟΜΙΚΑ ΔΔΡ ΜΕ ΜΙΚΡΟΑΥΤΟΜΑΤΟ", size=5.9, font="Inter-Bold", color=RCBOC)
            txt(xs[0] - 10, yb + 7, "1P+N · 30 mA · τύπου A (τύπου F στα μηχανήματα με inverter)", size=5.5, color=RCBOC)
        for xc, cid in zip(xs, ids):
            q = cc.get(cid)
            if gid == "EV":
                ln(xc, yb, xc, ys - 8, col=MUTE, lw=0.9, dash=[2.5, 2])
                _breaker(xc, ys - 8, "ΔΔΡ B", col=MUTE, dash=[2, 1.5], w=24)
                ln(xc, ys - 21, xc, ys - 29, col=MUTE, lw=0.9, dash=[2.5, 2])
                vtext(xc - 1, ytx, "EV · 3Φ · %s  –  ΠΡΟΒΛΕΨΗ" % q["cable"], font="Inter-Bold", size=5.9, color=MUTE)
                vtext(xc + 6, ytx, "φόρτιση οχήματος: σωλήνας Ø32 ως το shaft", size=5.5, color=MUTE)
                vtext(xc + 12.5, ytx, "+ 8 δεσμευμένα στοιχεία στον πίνακα", size=5.5, color=MUTE)
                continue
            if q is None:                                  # εφεδρικός
                ln(xc, ys, xc, ys - 8, col=MUTE, lw=0.8)
                _breaker(xc, ys - 8, "B10", col=MUTE)
                vtext(xc - 1, ytx, "%s · εφεδρικός" % cid, font="Inter-Bold", size=5.9, color=MUTE)
                continue
            rc = gid == "RCBO"
            col = RCBOC if rc else INK
            ln(xc, yb if rc else ys, xc, ys - 8, col=INK, lw=0.9)
            _breaker(xc, ys - 8, "%s%d" % (q["curve"], q["In"]) + ("·3P" if q["poles"] == 3 else ""), col=col, rcbo=rc, w=24 if q["poles"] == 3 else 19)
            if rc:
                txt(xc + 12, ys - 12, q["grp"][-1], size=5.0, font="Inter-Bold", color=RCBOC)
            ln(xc, ys - 21, xc, ys - 27, lw=0.9)
            p = c.beginPath(); p.moveTo(xc - 2.4, ys - 26); p.lineTo(xc + 2.4, ys - 26); p.lineTo(xc, ys - 30.5); p.close(); c.setFillColorRGB(*INK); c.drawPath(p, stroke=0, fill=1)
            vtext(xc - 1, ytx, "%s · %s · %s" % (q["id"], q["ph"], q["cable"]), font="Inter-Bold", size=5.9)
            nm = wrap(q["name"], "Inter", 5.5, 200)[:2]
            for j, s_ in enumerate(nm):
                vtext(xc + 6 + j * 6.5, ytx, s_, size=5.5)
                low = min(low, ytx - SW(s_, "Inter", 5.5))
            low = min(low, ytx - SW("%s · %s · %s" % (q["id"], q["ph"], q["cable"]), "Inter-Bold", 5.9))
        x = xs[-1] + slot * (1 + GAP)
    # ---- κάτω ζώνη: όψη πίνακα · λογική · υπόμνημα
    yl = low - 16
    assert yl > YB + 250, "ΗΛ-10: τα ονόματα των κυκλωμάτων κατεβαίνουν πολύ (%.0f)" % yl
    ln(X0, yl + 6, X1, yl + 6, col=FAINT, lw=0.5)
    # όψη πίνακα
    yy = D.heading(X0, yl - 6, "ΟΨΗ ΠΙΝΑΚΑ – ΔΙΑΤΑΞΗ ΣΤΟΙΧΕΙΩΝ (5 σειρές × 18)", w=268, size=7.4)
    mw, rh, rg = 14.0, 40.0, 9.0
    px0 = X0 + 14; py = yy - 6
    box(px0 - 8, py - 5 * rh - 4 * rg - 8, 18 * mw + 16, 5 * rh + 4 * rg + 16, fill=(0.97, 0.97, 0.98), stroke=INK, lw=1.0)
    KCOL = {"main": ((0.25, 0.25, 0.28), (1, 1, 1)), "rcd": (tint(RCDC, 0.75), RCDC), "mcb": ((1, 1, 1), INK), "rcbo": (tint(RCBOC, 0.78), RCBOC),
            "ev": ((0.93, 0.93, 0.94), MUTE), "free": (None, MUTE)}
    for ri, row in enumerate(M.PANEL_ROWS):
        ry = py - ri * (rh + rg) - rh
        txt(px0 - 11.5, ry + rh / 2 - 2, "%d" % (ri + 1), size=5.6, color=MUTE, anchor="r")
        xx = px0
        for lab, mods, kind in row:
            fill, tc = KCOL[kind]
            w_ = mods * mw
            if kind == "free":
                box(xx + 0.8, ry + 0.8, w_ - 1.6, rh - 1.6, stroke=(0.72, 0.72, 0.75), lw=0.5, dash=[1.5, 1.5])
                txt(xx + w_ / 2, ry + rh / 2 - 2, "ελεύθερα %d" % mods, size=5.0, color=MUTE, anchor="c")
            else:
                box(xx + 0.6, ry + 0.6, w_ - 1.2, rh - 1.2, fill=fill, stroke=tc if kind != "main" else INK, lw=0.6, dash=[2, 1.5] if kind == "ev" else None)
                if len(lab) == 1:
                    txt(xx + w_ / 2, ry + rh / 2 - 2, lab, size=5.6, font="Inter-Bold", color=tc, anchor="c")
                elif mods == 1 or (mods == 2 and len(lab) > 3):
                    c.saveState(); c.translate(xx + w_ / 2 + 2, ry + rh / 2); c.rotate(90); c.setFont("Inter-Bold", 5.6); c.setFillColorRGB(*tc); c.drawCentredString(0, 0, lab); c.restoreState()
                else:
                    ls = lab.split(" ", 1) if (SW(lab, "Inter-Bold", 5.6) > w_ - 3) else [lab]
                    for j, s_ in enumerate(ls):
                        txt(xx + w_ / 2, ry + rh / 2 - 2 + (len(ls) - 1) * 3.4 - j * 6.8, s_, size=5.6, font="Inter-Bold", color=tc, anchor="c")
            xx += w_
    pb = py - 5 * rh - 4 * rg - 8
    used = M.modules_used(); tot = M.PANEL["rows"] * M.PANEL["per_row"]
    txt(X0, pb - 10, "Σε χρήση %d στοιχεία · δεσμευμένα για φόρτιση οχήματος %d · ελεύθερα %d  (σύνολο %d)" % (used, M.EV_RESERVED, tot - used - M.EV_RESERVED, tot), size=5.9, font="Inter-SemiBold")
    txt(X0, pb - 18, "Κουτί ≈ 52 × 93 × 10,5 cm · κάτω άκρο +1,02 · πάνω άκρο +1,95 · στον τοίχο Τ2N-02 του χωλ (ΗΛ-16).", size=5.7, color=MUTE)
    assert pb - 20 > YB, "ΗΛ-10: η όψη του πίνακα δεν χωρά"
    # λογική
    xm = X0 + 300; wm = 420
    f = Flow(xm, yl - 1, wm, name="ΗΛ-10/λογική")
    f.h("Η ΛΟΓΙΚΗ ΤΟΥ ΠΙΝΑΚΑ")
    B = dict(bullet="•", size=6.7)
    f.p("Τρεις ομάδες διαφορικής προστασίας ανά χρήση – φωτισμός, ρευματοδότες, κουζίνα / πλυντήρια: μια διαρροή σε συσκευή δεν σβήνει τα φώτα και δεν ρίχνει όλο το σπίτι "
        "(η μελέτη αδείας είχε δύο).", bold="Διαχωρισμός.", **B)
    f.p("Ψυγείο, ερμάριο ασθενών (internet), αντλία θερμότητας, κλιματισμός, boiler, εξώστες και αποθήκη έχουν δικό τους ΔΔΡ με μικροαυτόματο: δεν πέφτουν από διαρροή "
        "άλλου κυκλώματος – ούτε ρίχνουν άλλα (π.χ. υγρασία σε ρευματοδότη εξώστη).", bold="Ατομικά ΔΔΡ.", **B)
    f.p("Τύπου A παντού (ηλεκτρονικά φορτία)· τύπου F στα μηχανήματα με inverter. Οριστικά κατά το φύλλο του κατασκευαστή κάθε μηχανήματος (Ε10).", bold="Τύποι ΔΔΡ.", **B)
    f.p("Αμέσως μετά τον γενικό διακόπτη· προστατεύει αντλία, inverter, δίκτυο, τροφοδοτικά LED.", bold="Απαγωγός υπερτάσεων.", **B)
    f.p("Οι εστίες τριφασικές, τα δύο μηχανήματα του εξώστη σε διαφορετικές φάσεις, ο boiler στην τρίτη: άθροισμα αιχμών %s / %s / %s kW." % tuple(fz(v, 1) for v in CK.phases().values()),
        bold="Ισοζύγιο φάσεων.", **B)
    f.p("Όταν εγκατασταθεί φορτιστής 11 kW, μπαίνει με δικό του ΔΔΡ τύπου B (ή A-EV) και με διαχείριση φορτίου, γιατί μαζί με το σπίτι ξεπερνά τα 3 × 35 A.", bold="Φόρτιση οχήματος.", **B)
    f.p("Ο πίνακας συναγερμού – πυρανίχνευσης έχει δικούς του συσσωρευτές (24 h)· το κέντρο ζωνών της ενδοδαπέδιας έχει δικό του κύκλωμα (ΕΝ).", bold="Ασφάλεια.", **B)
    # υπόμνημα + ισοζύγιο
    xr = xm + wm + 24; wr = X1 - xr
    g = Flow(xr, yl - 1, wr, name="ΗΛ-10/υπόμνημα")
    g.h("ΥΠΟΜΝΗΜΑ")
    yy = g.y - 4
    def leg(drawfn, s):
        nonlocal yy
        drawfn(xr + 14, yy + 9)
        for j, l_ in enumerate(wrap(s, "Inter", 6.0, wr - 36)):
            txt(xr + 34, yy + 1 - j * 7.4, l_, size=6.0)
        yy -= max(1, len(wrap(s, "Inter", 6.0, wr - 36))) * 7.4 + 9
    leg(lambda x_, y_: _breaker(x_, y_, "B10"), "Μικροαυτόματος: καμπύλη και ονομαστικό ρεύμα (B10 = καμπύλη B, 10 A)")
    leg(lambda x_, y_: _breaker(x_, y_, "C25", col=RCBOC, rcbo=True), "ΔΔΡ με μικροαυτόματο 1P+N, 30 mA (το γράμμα δίπλα = τύπος A ή F)")
    leg(lambda x_, y_: box(x_ - 12, y_ - 13, 24, 13, fill=tint(RCDC), stroke=RCDC, lw=1.0), "Διακόπτης διαρροής ομάδας 4P 40 A / 30 mA τύπου A")
    leg(lambda x_, y_: _breaker(x_, y_, "B10", col=MUTE), "Εφεδρικός μικροαυτόματος / πρόβλεψη (γκρι)")
    g.y = yy - 2
    g.h("ΚΑΛΩΔΙΟ ΑΝΑ ΚΥΚΛΩΜΑ")
    g.p("Το κείμενο κάτω από κάθε μικροαυτόματο: κωδικός · φάση · καλώδιο (αγωγοί × mm²) και τι τροφοδοτεί. Φορτία, μήκη και πτώση τάσης: ΗΛ-11. "
        "Οδεύσεις: ΗΛ-05. Οι κωδικοί γράφονται στις ετικέτες του πίνακα και στα άκρα των καλωδίων.", size=6.0)
    DC.finish(no, "ΜΟΝΟΓΡΑΜΜΙΚΟ ΣΧΕΔΙΟ ΠΙΝΑΚΑ", "Γενικός πίνακας «ΓΠ» · διάταξη στοιχείων · λογική προστασιών")


# ================================================================ ΗΛ-16 ΛΕΠΤΟΜΕΡΕΙΕΣ
class Sec:
    """Τομή: οριζόντια συντεταγμένη h (m) → δεξιά, στάθμη z (m από το τελικό δάπεδο) → πάνω."""
    def __init__(self, ox, oy, s, h0, z0):
        self.ox, self.oy, self.s, self.h0, self.z0 = ox, oy, s, h0, z0

    def p(self, h, z):
        return self.ox + (h - self.h0) * self.s, self.oy + (z - self.z0) * self.s

    def rect(self, h0, z0, h1, z1, fill=None, stroke=INK, lw=0.6, dash=None):
        x0, y0 = self.p(h0, z0); x1, y1 = self.p(h1, z1)
        box(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0), fill=fill, stroke=stroke, lw=lw, dash=dash)

    def line(self, h0, z0, h1, z1, col=INK, lw=0.7, dash=None):
        ln(*self.p(h0, z0), *self.p(h1, z1), col=col, lw=lw, dash=dash)

    def text(self, h, z, s, size=5.8, font="Inter", color=INK, anchor="l", dx=0, dy=0):
        x, y = self.p(h, z); txt(x + dx, y + dy, s, size=size, font=font, color=color, anchor=anchor)

    def level(self, h, z, s, right=True, color=INK):
        x, y = self.p(h, z)
        ln(x, y, x + (26 if right else -26), y, col=color, lw=0.5)
        txt(x + (28 if right else -28), y - 2, s, size=5.6, font="Inter-SemiBold", color=color, anchor="l" if right else "r")

    def dimh(self, h0, h1, z, s, off=0):
        x0, y0 = self.p(h0, z); x1, _ = self.p(h1, z); y0 += off
        ln(x0, y0, x1, y0, lw=0.45)
        for x in (x0, x1):
            ln(x - 2, y0 - 2, x + 2, y0 + 2, lw=0.6)
        txt((x0 + x1) / 2, y0 + 2.5, s, size=5.6, font="Inter-SemiBold", anchor="c")

    def dimv(self, h, z0, z1, s, off=0):
        x0, y0 = self.p(h, z0); _, y1 = self.p(h, z1); x0 += off
        ln(x0, y0, x0, y1, lw=0.45)
        for yv in (y0, y1):
            ln(x0 - 2, yv - 2, x0 + 2, yv + 2, lw=0.6)
        c = C(); c.saveState(); c.translate(x0 - 2.5, (y0 + y1) / 2); c.rotate(90); c.setFont("Inter-SemiBold", 5.6); c.setFillColorRGB(*INK); c.drawCentredString(0, 0, s); c.restoreState()


def _cap(x, y, s, sub=None):
    txt(x, y, s, size=7.6, font="Inter-Bold")
    w = SW(s, "Inter-Bold", 7.6); ln(x, y - 3, x + w, y - 3, lw=0.9)
    if sub:
        txt(x + w + 8, y, sub, size=6.0, color=MUTE)


def det_crossing(x, ytop):
    """Τομή Β–Ν μέσα από τη διέλευση ΔΠ1 πάνω από τη Δ3.1 (βλέπουμε προς ανατολή), 1:10."""
    _cap(x, ytop, "1 · ΔΙΕΛΕΥΣΗ ΔΟΚΟΥ «ΔΠ» – ΤΟΜΗ ΣΤΗ ΔΠ1 ΠΑΝΩ ΑΠΟ ΤΗ Δ3.1", "1:10 · βλέπουμε προς ανατολή")
    bm = [b for b in A.BEAMS if b[0] == "Δ3.1"][0]
    y0b, y1b = bm[3], bm[5]
    zt = A.TOP_SLAB; zb = A.beam_soffit(bm[1]); hs = 0.20
    S = 72 / 25.4 * 1000 / 10
    h0, z0 = 4.18, 2.24
    s = Sec(x + 6, ytop - 268, S, h0, z0)
    hN, hS = 4.20, 5.62
    s.rect(hN, zt - hs, hS, zt, fill=CONC, stroke=INK, lw=0.8)                       # πλάκα
    s.rect(y0b, zb, y1b, zt, fill=CONC, stroke=INK, lw=0.8)                          # δοκός
    s.text((y0b + y1b) / 2, zb + 0.10, "Δ3.1", size=6.4, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    s.text((y0b + y1b) / 2, zb + 0.055, "30 / 50", size=5.6, color=(1, 1, 1), anchor="c")
    s.text(hN + 0.04, zt - 0.06, "πλάκα οροφής", size=5.6, color=(1, 1, 1))
    wl = [w for w in W.WALLS if w["id"] == "T2N-01"][0]; wb = G.bbox(wl["pts"])
    s.rect(wb[1], z0, wb[3], zb, fill=GYP, stroke=INK, lw=0.6)                       # τοίχος κάτω από τη δοκό (πλάτη ντουλάπας)
    lvH, lvL = 2.70, 2.68
    s.rect(hN, lvH - 0.0125, y0b, lvH, fill=GYP, stroke=INK, lw=0.5)                 # ψευδοροφή χωλ / ΤΝ
    s.rect(y1b, lvL - 0.0125, hS, lvL, fill=GYP, stroke=INK, lw=0.5)                 # ψευδοροφή καθιστικού
    # σπιράλ: από το κενό του χωλ → μέσα στην πλάκα → πάνω από τη δοκό → κενό καθιστικού
    zc = zt - hs / 2
    pts = [(hN + 0.02, 2.745), (4.42, 2.745), (4.50, 2.80), (4.56, zc), (5.44, zc), (5.50, 2.80), (5.56, 2.735), (hS - 0.02, 2.735)]
    c = C(); c.setStrokeColorRGB(*SLABC); c.setLineWidth(0.025 * S); c.setLineCap(1); c.setLineJoin(1)
    p = c.beginPath(); p.moveTo(*s.p(*pts[0]))
    for q in pts[1:]:
        p.lineTo(*s.p(*q))
    c.drawPath(p, stroke=1, fill=0); c.setLineCap(0); c.setLineJoin(0)
    c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(0.6); c.setDash([4, 3])
    p = c.beginPath(); p.moveTo(*s.p(*pts[0]))
    for q in pts[1:]:
        p.lineTo(*s.p(*q))
    c.drawPath(p, stroke=1, fill=0); c.setDash([])
    # οπλισμοί (σχηματικά)
    for zz in (zt - 0.03, zt - hs + 0.03):
        s.line(hN + 0.01, zz, hS - 0.01, zz, col=(0.25, 0.25, 0.28), lw=0.5, dash=[5, 2])
    # χώροι
    s.text(4.50, 2.58, "ΧΩΛ – τεχνική ντουλάπα ΤΝ", size=6.0, font="Inter-SemiBold", color=MUTE, anchor="c")
    s.text(4.50, 2.54, "(πάνω από τον πίνακα)", size=5.5, color=MUTE, anchor="c")
    s.text(5.40, 2.56, "ΚΑΘΙΣΤΙΚΟ", size=6.0, font="Inter-SemiBold", color=MUTE, anchor="c")
    s.text(wb[3] + 0.015, 2.34, "τοίχος Τ2N-01", size=5.4, color=MUTE)
    s.text(wb[3] + 0.015, 2.30, "κάτω από τη δοκό", size=5.4, color=MUTE)
    # στάθμες
    s.level(hS, zt, "+%s άνω πλάκα" % fz(zt, 2)); s.level(hS, zt - hs, "+%s κάτω πλάκα" % fz(zt - hs, 2)); s.level(hS, lvL, "+%s ψευδοροφή" % fz(lvL, 2))
    s.text(hN + 0.03, lvH - 0.045, "ψευδοροφή +%s" % fz(lvH, 2), size=5.6, font="Inter-SemiBold")
    s.text(y0b - 0.02, zb - 0.035, "κάτω παρειά δοκού +%s" % fz(zb, 2), size=5.6, font="Inter-SemiBold", anchor="r")
    s.dimh(y1b, 5.50, zt, "≥ 30", off=10); s.dimh(4.50, y0b, zt, "≥ 30", off=10); s.dimh(y0b, y1b, zt, "30", off=10)
    # οδηγοί
    xa, ya = s.p(5.0, zc)
    ln(xa, ya, xa + 22, ya + 58, col=SLABC, lw=0.5); txt(xa + 25, ya + 60, "σπιράλ βαρέος τύπου Ø25 / Ø32 / Ø40 στο ΜΕΣΟ του πάχους της πλάκας,", size=5.8, font="Inter-SemiBold", color=SLABC)
    txt(xa + 25, ya + 53, "ανάμεσα στον κάτω και τον πάνω οπλισμό, κάθετα στη δοκό", size=5.8, color=SLABC)
    yb_ = s.p(0, z0)[1] - 4
    lines = ["Τα δύο άκρα βγαίνουν από την κάτω παρειά της πλάκας ≥ 30 cm από την παρειά της δοκού, μέσα στα κενά των ψευδοροφών.",
             "Τα σπιράλ μπαίνουν ένα-ένα, με απόσταση ≥ 3 διαμέτρους μεταξύ τους (όχι δεμάτι) – η δοκός ΔΕΝ τρυπιέται και δεν αδυνατίζει.",
             "Τοποθετούνται ΠΡΙΝ ΑΠΟ ΤΗ ΣΚΥΡΟΔΕΤΗΣΗ κάθε πλάκας οροφής (Σ4 · Σ5 · Σ6). ΘΕΛΕΙ ΕΓΚΡΙΣΗ ΤΟΥ ΣΤΑΤΙΚΟΥ – ανοικτό Ε2."]
    for i, l_ in enumerate(lines):
        txt(x, yb_ - 8 - i * 7.6, l_, size=5.9, font="Inter-SemiBold" if i == 2 else "Inter", color=DC.WARNC if i == 2 else INK)
    return yb_ - 8 - 3 * 7.6


def det_panel_plan(x, ytop):
    """Κάτοψη του τοίχου Τ2N-02 με τον πίνακα και την τεχνική ντουλάπα, 1:15."""
    _cap(x, ytop, "2 · Ο ΠΙΝΑΚΑΣ ΣΤΟΝ ΤΟΙΧΟ ΤΩΝ 70 cm – ΚΑΤΟΨΗ", "1:15")
    S = 72 / 25.4 * 1000 / 15
    xw0, xw1 = 4.62, 6.58
    yw0, yw1 = 4.20, 5.28
    v = P.view(x + 4 - xw0 * S, PAGE_H - (ytop - 14) - yw0 * S, S)        # View: x → δεξιά, y → κάτω
    c = C(); c.saveState(); p = c.beginPath(); p.rect(x, ytop - 14 - (yw1 - yw0) * S, (xw1 - xw0) * S + 8, (yw1 - yw0) * S); c.clipPath(p, stroke=0, fill=0)
    for w in W.WALLS:
        if G.is_rect(w["pts"]):
            b = G.bbox(w["pts"])
            if b[2] > xw0 and b[0] < xw1 and b[3] > yw0 and b[1] < yw1:
                v.rect(b[0], b[1], b[2], b[3], fill=GYP, stroke=INK, lw=0.6)
    for pl in W.COLS:
        if G.is_rect(pl):
            b = G.bbox(pl)
            if b[2] > xw0 and b[0] < xw1 and b[3] > yw0 and b[1] < yw1:
                v.rect(b[0], b[1], b[2], b[3], fill=CONC, stroke=INK, lw=0.6)
    tn = M.TN
    v.rect(tn[0], tn[1], tn[2], tn[3], fill=tint(FEED, 0.93), stroke=FEED, lw=0.7)
    v.line(4.62, 4.35, tn[0], 4.35, color=MUTE, lw=0.5, dash=[2, 2])
    pn = M.PANEL
    v.rect(pn["x"] - pn["box"][2], pn["y0"], pn["x"], pn["y1"], fill=(0.15, 0.15, 0.18), stroke=INK, lw=0.6)
    v.rect(*M.DATA_CAB, fill=tint(DAT, 0.7), stroke=DAT, lw=0.6)
    v.rect(*M.ALARM_PANEL, fill=tint(FIR, 0.7), stroke=FIR, lw=0.6)
    v.line(tn[0], 4.35, tn[0] + 0.03, 4.35, color=INK, lw=0.4)
    c.setDash([2, 1.5]); v.arc(tn[2] - 0.02, 4.35, tn[2] - tn[0] - 0.04, 180, 270, color=MUTE, lw=0.4); c.setDash([])
    c.restoreState()
    def T(xm, ym, s_, **kw):
        X, Y = v.p(xm, ym); txt(X, Y, s_, **kw)
    T(pn["x"] + 0.05, 4.56, "ΓΠ πίνακας 52 × 10,5", size=5.8, font="Inter-Bold")
    T(pn["x"] + 0.05, 4.62, "μέτωπο περασιά με τον τοίχο", size=5.4, color=MUTE)
    T((tn[0] + tn[2]) / 2 - 0.04, 4.66, "ΤΝ", size=6.6, font="Inter-Bold", color=FEED, anchor="c")
    T(M.DATA_CAB[0] + 0.03, 4.885, "ΚΔ ερμάριο ασθενών", size=5.0, color=DAT)
    T(M.ALARM_PANEL[2] + 0.02, 4.52, "ΠΣ", size=5.2, font="Inter-Bold", color=FIR)
    T(4.72, 4.72, "ντουλάπα", size=5.4, color=MUTE, anchor="c"); T(4.72, 4.78, "χωλ", size=5.4, color=MUTE, anchor="c")
    T(5.90, 4.30, "ΧΩΛ", size=6.0, font="Inter-SemiBold", color=MUTE, anchor="c")
    T(5.90, 5.24, "ΚΑΘΙΣΤΙΚΟ", size=6.0, font="Inter-SemiBold", color=MUTE, anchor="c")
    T(5.92, 5.12, "άνοιγμα χωλ – καθιστικού 0,90", size=5.6, color=MUTE, anchor="c")
    T(5.92, 4.815, "0,95 ελεύθερα μπροστά στον πίνακα", size=5.6, font="Inter-SemiBold", anchor="c")
    X0_, Y0_ = v.p(pn["x"], 4.84); X1_, _ = v.p(6.399, 4.84)
    ln(X0_, Y0_, X1_, Y0_, lw=0.45)
    for xx in (X0_, X1_):
        ln(xx - 2, Y0_ - 2, xx + 2, Y0_ + 2, lw=0.6)
    wb = G.bbox([w for w in W.WALLS if w["id"] == M.PANEL_WALL][0]["pts"])
    ybase = ytop - 14 - (yw1 - yw0) * S - 6
    txt(x, ybase - 4, "Τοίχος Τ2N-02: y %s – %s = 0,70 m · πάχος 8,75 cm (1 γυψ. · CW 50 · 2 γυψ.) · πίνακας y %s – %s (0,52), 9 cm από κάθε άκρο." %
        (fz(wb[1], 2), fz(wb[3], 2), fz(pn["y0"], 2), fz(pn["y1"], 2)), size=5.8)
    txt(x, ybase - 11.6, "Η πλάτη του πίνακα προεξέχει ≈ 2 cm μέσα στην ΤΝ· όλα τα καλώδια κατεβαίνουν ορατά μέσα στην ΤΝ και μπαίνουν από πάνω.", size=5.8)
    txt(x, ybase - 19.2, "ΤΝ = το ανατολικό 0,50 m της ντουλάπας του χωλ, με δική της πόρτα: πλάτη πίνακα · ερμάριο ασθενών ΚΔ · πίνακας συναγερμού – πυρανίχνευσης ΠΣ.", size=5.8)
    return ybase - 26


def det_panel_elev(x, ytop):
    """Όψη του τοίχου του πίνακα από το άνοιγμα (βλέπουμε προς δύση), 1:25."""
    _cap(x, ytop, "3 · ΟΨΗ ΤΟΥ ΤΟΙΧΟΥ ΤΟΥ ΠΙΝΑΚΑ", "1:30 · από το άνοιγμα, προς δύση")
    S = 72 / 25.4 * 1000 / 30
    wb = G.bbox([w for w in W.WALLS if w["id"] == M.PANEL_WALL][0]["pts"])
    pn = M.PANEL
    bm = [b for b in A.BEAMS if b[0] == "Δ3.1"][0]; zb = A.beam_soffit(bm[1])
    # h = y του μοντέλου (βορράς αριστερά όταν κοιτάμε προς δύση; όχι: κοιτώντας δύση, ο βορράς είναι ΔΕΞΙΑ) → καθρέφτισμα
    hm = lambda yv: (wb[3] + 0.36) - yv
    s = Sec(x + 34, ytop - 16 - 2.98 * S, S, 0.0, 0.0)
    L, R = hm(wb[3] + 0.36), hm(wb[1] - 0.26)
    s.rect(L, -0.06, R, 0.0, fill=CONC, stroke=None)                                   # δάπεδο
    s.line(L, 0.0, R, 0.0, lw=0.9)
    s.rect(hm(wb[3]), 0.0, hm(wb[1]), 2.70, fill=(0.95, 0.95, 0.96), stroke=INK, lw=0.7)    # ο τοίχος 0,70
    s.rect(hm(bm[5]), zb, hm(bm[3]), A.TOP_SLAB, fill=CONC, stroke=INK, lw=0.6)         # δοκός Δ3.1 (σε τομή)
    s.rect(L, A.TOP_SLAB - 0.20, R, A.TOP_SLAB, fill=CONC, stroke=INK, lw=0.6)
    s.rect(hm(bm[5]), zb, hm(bm[3]), A.TOP_SLAB, fill=CONC, stroke=INK, lw=0.6)
    s.line(hm(wb[1]), 2.70, R, 2.70, lw=0.6); s.line(L, 2.68, hm(bm[5]), 2.68, lw=0.6)
    s.rect(hm(pn["y1"]), pn["z0"], hm(pn["y0"]), pn["z1"], fill=(0.22, 0.22, 0.25), stroke=INK, lw=0.7)
    rows = pn["rows"]; rh = (pn["z1"] - pn["z0"] - 0.08) / rows
    for i in range(rows):
        z = pn["z0"] + 0.04 + i * rh
        s.rect(hm(pn["y1"]) + 0.03, z + 0.03, hm(pn["y0"]) - 0.03, z + rh - 0.03, fill=(0.93, 0.93, 0.95), stroke=None)
    s.text((hm(pn["y0"]) + hm(pn["y1"])) / 2, pn["z1"] + 0.05, "ΓΠ", size=6.4, font="Inter-Bold", anchor="c")
    s.text(hm(bm[3]) - 0.14, zb + 0.20, "Δ3.1", size=5.4, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    s.text(L + 0.02, 0.50, "ΚΑΘΙ-", size=5.2, color=MUTE); s.text(L + 0.02, 0.42, "ΣΤΙΚΟ", size=5.2, color=MUTE)
    s.text(R - 0.02, 0.46, "ΧΩΛ", size=5.2, color=MUTE, anchor="r")
    s.dimh(hm(wb[3]), hm(wb[1]), 0.0, "0,70", off=-14)
    s.dimh(hm(pn["y1"]), hm(pn["y0"]), pn["z0"], "0,52", off=-9)
    xr = R + 0.02
    s.level(xr, pn["z0"], "+%s κάτω άκρο" % fz(pn["z0"], 2)); s.level(xr, pn["z1"], "+%s πάνω άκρο" % fz(pn["z1"], 2))
    s.level(xr, (pn["z0"] + pn["z1"]) / 2, "+%s άξονας" % fz((pn["z0"] + pn["z1"]) / 2, 2), color=MUTE)
    s.level(xr, 2.70, "+2,70 ψευδοροφή"); s.level(xr, 0.0, "±0,00 δάπεδο")
    yb_ = s.p(0, -0.06)[1] - 22
    txt(x, yb_, "Όλα τα χειριστήρια ανάμεσα στο +1,05 και το +1,90.", size=5.8)
    txt(x, yb_ - 7.6, "Πάνω από τον πίνακα ο τοίχος μένει ελεύθερος ως την", size=5.8)
    txt(x, yb_ - 15.2, "ψευδοροφή: από εκεί μπαίνουν τα καλώδια (μέσα από την ΤΝ).", size=5.8)
    return yb_ - 22


HEIGHTS = [(0.30, "ρευματοδότες γενικής χρήσης · λήψεις δικτύου", PWR), (0.45, "ρευματοδότες / λήψεις πίσω από TV", PWR), (0.50, "ρευματοδότες εξωστών IP55", PWR),
           (0.70, "ρευματοδότες / λήψεις κομοδίνων", PWR), (0.90, "διακόπτες κομοδίνων", SWC), (1.00, "ρευματοδότες / λήψεις γραφείου", PWR),
           (1.10, "διακόπτες · πλήκτρα ρολών · μπουτόν κουδουνιού", SWC), (1.15, "ρευματοδότες πάγκου κουζίνας / καθρεπτών · απλίκες", PWR),
           (1.30, "πλυντήριο · στεγνωτήριο · διακόπτες μηχανημάτων εξώστη", HVC), (1.45, "θυροτηλεόραση · πληκτρολόγιο συναγερμού", DAT),
           (1.50, "θερμοστάτες · χειριστήριο καναλάτης", AUT), (2.00, "φωτιστικά καθρεπτών", LGT), (2.10, "φωτιστικά εξωστών · ρευματοδότες στήλης κουζίνας", LGT),
           (2.20, "ύψος πόρτας · φωτεινός επαναλήπτης", MUTE), (2.35, "παροχή μοτέρ ρολού", SWC), (2.45, "παροχή split", HVC)]


def det_heights(x, ytop, w):
    _cap(x, ytop, "4 · ΥΨΗ ΤΟΠΟΘΕΤΗΣΗΣ", "στον άξονα του κουτιού, από το ΤΕΛΙΚΟ δάπεδο")
    S = 72 / 25.4 * 1000 / 32
    s = Sec(x + 30, ytop - 20 - 2.75 * S, S, 0.0, 0.0)
    s.rect(0.0, 0.0, 0.10, 2.70, fill=GYP, stroke=INK, lw=0.6)
    s.rect(-0.10, -0.05, 0.60, 0.0, fill=CONC, stroke=None); s.line(-0.10, 0.0, 0.60, 0.0, lw=0.9)
    s.line(0.0, 2.70, 0.60, 2.70, lw=0.6)
    s.text(0.70, 2.68, "ψευδοροφή +2,70", size=5.4, color=MUTE); s.text(0.14, -0.04, "τελικό δάπεδο ±0,00 (γέμισμα 12 cm)", size=5.4, color=MUTE, dy=-6)
    yprev = None
    for z, lab, col in HEIGHTS:
        X, Y = s.p(0.10, z)
        box(X, Y - 2.2, 4.4, 4.4, fill=col, stroke=None)
        yt = Y - 2
        if yprev is not None and yt - yprev < 8.2:
            yt = yprev + 8.2
        ln(X + 4.4, Y, X + 22, yt + 2, col=col, lw=0.4)
        txt(X + 24, yt, "+%s" % fz(z, 2), size=6.0, font="Inter-Bold", color=col)
        txt(X + 48, yt, lab, size=5.8)
        yprev = yt
    return s.p(0, -0.05)[1] - 14


def sheet_16(no="ΗΛ-16"):
    y = DC.title("ΛΕΠΤΟΜΕΡΕΙΕΣ: ΔΙΕΛΕΥΣΗ ΔΟΚΟΥ · ΠΙΝΑΚΑΣ ΣΤΟΝ ΤΟΙΧΟ ΤΩΝ 70 cm · ΥΨΗ · ΟΔΕΥΣΕΙΣ", "η αιτιολόγηση κάθε διέλευσης και όδευσης του ΗΛ-05")
    # αριστερά: 1 και 2
    y1 = det_crossing(X0, y - 4)
    det_panel_plan(X0, y1 - 14)
    # μέση: 3 και 4
    xm = X0 + 452
    y3 = det_panel_elev(xm, y - 4)
    det_heights(xm, y3 - 12, 250)
    # δεξιά: πίνακες
    xr = X0 + 716; wr = X1 - xr
    f = Flow(xr, y + 2, wr, name="ΗΛ-16/πίνακες")
    f.h("ΔΙΕΛΕΥΣΕΙΣ ΔΟΚΩΝ «ΔΠ» – ΤΙ ΠΕΡΝΑ ΑΠΟ ΚΑΘΕ ΜΙΑ")
    rows = []
    for c_ in M.CROSSINGS:
        parts = []
        for k, d in (("n25", "Ø25"), ("n32", "Ø32"), ("n40", "Ø40")):
            if c_[k]:
                parts.append("%d×%s" % (c_[k], d))
        b = c_["rect"]
        wd = (b[2] - b[0]) if c_["axis"] == "NS" else (b[3] - b[1])
        rows.append([c_["id"], c_["beam"], " + ".join(parts) + "\nσε πλάτος %s m" % fz(wd, 2), c_["txt"] + (". Θέση: " + c_["where"] if c_.get("where") else "")])
    f.table([34, 28, 66, 258], rows, head=["", "ΔΟΚΟΣ", "ΣΠΙΡΑΛ", "ΤΙ ΠΕΡΝΑ – ΠΟΥ"], size=6.2, lead=7.4, pad=2.1, bold_first=True)
    f.h("ΟΔΕΥΣΕΙΣ ΣΤΟ ΓΕΜΙΣΜΑ ΔΑΠΕΔΟΥ – ΜΟΝΟ ΑΥΤΕΣ")
    rows = [[r["id"], r["n"] + "\n%s m" % fz(G.path_len(r["pts"]), 1), ("ΝΕΑ ζώνη. " if r["new"] else "Σε υπάρχουσα λωρίδα. ") + r["txt"]] for r in M.FLOOR_RUNS]
    f.table([34, 44, 308], rows, head=["", "ΣΠΙΡΑΛ", "ΑΠΟ – ΠΡΟΣ – ΓΙΑΤΙ"], size=6.2, lead=7.4, pad=2.1, bold_first=True)
    f.h("ΟΡΙΖΟΝΤΙΕΣ ΟΔΕΥΣΕΙΣ ΜΕΣΑ ΣΕ ΤΟΙΧΟ (τοίχοι κάτω από δοκό)")
    f.table([34, 352], [[r["id"], r["txt"]] for r in M.WALL_RUNS], size=6.2, lead=7.4, pad=2.1, bold_first=True)
    f.h("ΚΟΡΜΟΙ ΣΤΑ ΚΕΝΑ ΤΩΝ ΨΕΥΔΟΡΟΦΩΝ")
    rows = [["Παροχή", M.FEEDER["txt"]]] + [[r["id"], r["txt"]] for r in M.ROUTES]
    f.table([34, 352], rows, size=6.2, lead=7.4, pad=2.1, bold_first=True)
    DC.finish(no, "ΛΕΠΤΟΜΕΡΕΙΕΣ ΕΓΚΑΤΑΣΤΑΣΗΣ", "Διέλευση δοκού · πίνακας στον τοίχο 70 cm · ύψη · οδεύσεις", "Κλίμακες 1:10 · 1:15 · 1:30 · A3")
