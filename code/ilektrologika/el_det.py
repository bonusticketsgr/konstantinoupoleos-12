"""Μονογραμμικό σχέδιο του πίνακα (με την όψη του) και βοηθητικά τομών (κλάση Sec) για τα φύλλα της ηλεκτρολογικής μελέτης."""
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
    y = DC.title("ΜΟΝΟΓΡΑΜΜΙΚΟ ΣΧΕΔΙΟ ΓΕΝΙΚΟΥ ΠΙΝΑΚΑ «ΓΠ» – ΔΙΑΤΑΞΗ ΠΙΝΑΚΑ", "τριφασική παροχή 3 × 35 A · 400 / 230 V · %d κυκλώματα + %d εφεδρικά" % (len(M.CIRCUITS), M.SPARE_MCB))
    c = C()
    cc = {q["id"]: q for q in M.CIRCUITS}
    groups = []
    for r in M.RCDS:
        ids = [q["id"] for q in M.CIRCUITS if q["grp"] == r["id"]]
        if r["id"] == "ΔΔΡ-1":
            ids += ["ΕΦ1", "ΕΦ2"]
        groups.append((r["id"], r, ids))
    groups.append(("RCBO", None, [q["id"] for q in M.CIRCUITS if q["grp"].startswith("RCBO")]))
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
    txt(xin + 12, ytop - 7, "ΑΠΟ ΤΟΝ ΠΙΝΑΚΑ ΤΗΣ ΑΠΟΘΗΚΗΣ (ΗΛ-13)", size=6.2, font="Inter-Bold")
    txt(xin + 12, ytop - 15, "%s · 3Φ + N + PE · ασφάλειες 3 × 35 A στην αποθήκη" % M.FEEDER["cable"], size=5.7)
    box(xin - 13, ytop - 42, 26, 16, fill=(1, 1, 1), lw=1.1); txt(xin, ytop - 36.5, "Γ.Δ.", size=5.8, font="Inter-Bold", anchor="c")
    txt(xin + 18, ytop - 33, "Γενικός διακόπτης φορτίου", size=5.7); txt(xin + 18, ytop - 40, "4P 40 A", size=5.7, font="Inter-SemiBold")
    txt(xin + 18, ytop - 61, "Οι ασφάλειες 3 × 35 A της παροχής", size=5.7); txt(xin + 18, ytop - 68, "είναι στον πίνακα της αποθήκης", size=5.7)
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
                ln(xc, yb, xc, ys + 22, col=INK, lw=0.9)
                _breaker(xc, ys + 22, "ΔΔΡ EV", col=RCDC, w=30)
                ln(xc, ys + 9, xc, ys - 8, col=INK, lw=0.9)
                _breaker(xc, ys - 8, "C20·4P", col=INK, w=30)
                ln(xc, ys - 21, xc, ys - 27, lw=0.9)
                vtext(xc - 1, ytx, "EV · 3Φ · %s" % q["cable"], font="Inter-Bold", size=5.9)
                vtext(xc + 6, ytx, "φόρτιση οχήματος 11 kW με διαχείριση φορτίου", size=5.5)
                vtext(xc + 12.5, ytx, "ΔΔΡ 4P 40 A / 30 mA τύπου A-EV · μέσω shaft", size=5.5)
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
            "free": (None, MUTE)}
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
    if M.SHOW_NOTES:
        txt(X0, pb - 10, "Σε χρήση %d στοιχεία (με τη φόρτιση οχήματος) · ελεύθερα %d · σύνολο %d" % (used, tot - used, tot), size=5.9, font="Inter-SemiBold")
        txt(X0, pb - 18, "Άνοιγμα ≈ 52 × 93 cm · βάθος εντοιχισμού 7–9 cm · +1,02 … +1,95 · δυτικό άκρο του χωλ, τοίχος λουτρού γονέων.", size=5.7, color=MUTE)
    assert pb - 20 > YB, "ΗΛ-10: η όψη του πίνακα δεν χωρά"
    # λογική
    xm = X0 + 300; wm = 420
    f = Flow(xm, yl - 1, wm, name="ΗΛ-10/λογική")
    f.h("Η ΛΟΓΙΚΗ ΤΟΥ ΠΙΝΑΚΑ")
    B = dict(bullet="•", size=6.7)
    f.p("Τρεις ομάδες διαφορικής προστασίας ανά χρήση – φωτισμός, ρευματοδότες, κουζίνα / πλυντήρια: μια διαρροή σε συσκευή δεν σβήνει τα φώτα και δεν ρίχνει όλο το σπίτι "
        "(η μελέτη αδείας είχε δύο).", bold="Διαχωρισμός.", **B)
    f.p("Ψυγείο, κέντρο ασθενών (internet), πυρανίχνευση, αντλία θερμότητας, κλιματισμός, boiler και εξώστες έχουν δικό τους ΔΔΡ με μικροαυτόματο: δεν πέφτουν από διαρροή "
        "άλλου κυκλώματος – ούτε ρίχνουν άλλα (π.χ. υγρασία σε ρευματοδότη εξώστη).", bold="Ατομικά ΔΔΡ.", **B)
    f.p("Τύπου A παντού (ηλεκτρονικά φορτία)· τύπου F στα μηχανήματα με inverter. Οριστικά κατά το φύλλο του κατασκευαστή κάθε μηχανήματος (Ε9).", bold="Τύποι ΔΔΡ.", **B)
    f.p("Αμέσως μετά τον γενικό διακόπτη· προστατεύει αντλία, inverter, δίκτυο, τροφοδοτικά LED.", bold="Απαγωγός υπερτάσεων.", **B)
    f.p("Οι εστίες τριφασικές, τα δύο μηχανήματα του εξώστη σε διαφορετικές φάσεις, ο boiler στην τρίτη: άθροισμα αιχμών %s / %s / %s kW." % tuple(fz(v, 1) for v in CK.phases().values()),
        bold="Ισοζύγιο φάσεων.", **B)
    f.p("Δεν είναι πια σε αυτόν τον πίνακα: ο φορτιστής και η αποθήκη τροφοδοτούνται από τον πίνακα της αποθήκης (ΗΛ-11), με ΔΙΑΧΕΙΡΙΣΗ ΦΟΡΤΙΟΥ που μετρά εκεί όλη την παροχή.", bold="Φόρτιση οχήματος.", **B)
    f.p("Ο πίνακας συναγερμού – πυρανίχνευσης έχει δικό του ρελέ και δικούς του συσσωρευτές (24 h)· το κέντρο ζωνών της ενδοδαπέδιας έχει δικό του κύκλωμα (ΕΝ).", bold="Ασφάλεια.", **B)
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
    leg(lambda x_, y_: _breaker(x_, y_, "B10", col=MUTE), "Εφεδρικός μικροαυτόματος (γκρι)")
    g.y = yy - 2
    g.h("ΚΑΛΩΔΙΟ ΑΝΑ ΚΥΚΛΩΜΑ")
    g.p("Το κείμενο κάτω από κάθε μικροαυτόματο: κωδικός · φάση · καλώδιο (αγωγοί × mm²) και τι τροφοδοτεί. Φορτία, μήκη και πτώση τάσης: ΗΛ-10. "
        "Περάσματα καλωδίων: ΗΛ-06. Οι κωδικοί γράφονται στις ετικέτες του πίνακα και στα άκρα των καλωδίων.", size=6.0)
    DC.finish(no, "ΜΟΝΟΓΡΑΜΜΙΚΟ ΣΧΕΔΙΟ – ΟΨΗ ΠΙΝΑΚΑ", "Γενικός πίνακας «ΓΠ» · διάταξη στοιχείων · λογική προστασιών")


# ================================================================ τομές
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
