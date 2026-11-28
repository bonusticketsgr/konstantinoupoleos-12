"""Βοηθητικά για φύλλα κειμένου / πινάκων (τίτλος, στήλες κειμένου που σταματούν το build αν ξεχειλίσουν) και ο πίνακας κυκλωμάτων και προστασιών.
Όλοι οι αριθμοί (φορτία, μήκη, πτώση τάσης) διαβάζονται από το μοντέλο b1_el.py / el_checks.py."""
import math
import el_draw as D
from el_draw import P, INK, MUTE, PAGE_W, PAGE_H, SW, wrap, PWR, LGT, SWC, DAT, FIR, HVC, AUT, FEED
import el_checks as CK
import el_geom as G

M = A = None
X0, X1 = 36.0, PAGE_W - 36.0
YT, YB = PAGE_H - 36.0, 100.0
WARNC = (0.70, 0.08, 0.10)


def bind(model):
    global M, A
    M, A = model, model.A
    CK.bind(model)


def C():
    return P.C


def fz(v, n=1):
    return ("%.*f" % (n, v)).replace(".", ",")


def title(s, sub=None):
    c = C(); c.setFont("Inter-Bold", 13); c.setFillColorRGB(*INK); c.drawString(X0, YT - 6, s)
    w = SW(s, "Inter-Bold", 13); c.setStrokeColorRGB(*INK); c.setLineWidth(1.2); c.line(X0, YT - 11, X0 + w, YT - 11)
    if sub and M.SHOW_NOTES:                                   # R20: ο υπότιτλος-επεξήγηση είναι σημείωση
        c.setFont("Inter", 8); c.setFillColorRGB(*MUTE); c.drawString(X0 + w + 14, YT - 6, sub)
    return YT - 30


def finish(no, theme, sub2, scale="Χωρίς κλίμακα · A3"):
    for t_, f_, z_ in ((theme, "Inter-Bold", 11), (P.SUB1, "Inter-Medium", 7.5), (sub2, "Inter-Medium", 7.5)):
        assert SW(t_, f_, z_) <= 282, "πινακίδα %s: «%s» = %.0f pt > 282" % (no, t_, SW(t_, f_, z_))
    P.frame_and_title(C(), no, theme, P.SUB1, sub2, M.BASE_TXT, scale, M.REV, M.DATE)
    C().showPage()


class Flow:
    """Στήλη κειμένου: επικεφαλίδες, παράγραφοι, πίνακες – από πάνω προς τα κάτω. Σταματά το build αν δεν χωρά."""
    def __init__(self, x, y, w, size=6.5, name=""):
        self.x, self.y, self.w, self.size, self.name = x, y, w, size, name

    def _chk(self):
        assert self.y >= YB - 2, "στήλη «%s»: το κείμενο ξεχειλίζει %.0f pt κάτω από το όριο" % (self.name, YB - self.y)

    def h(self, s, fill=INK, size=7.4):
        if not M.SHOW_NOTES:                                   # R20: επικεφαλίδες κειμένου δεν τυπώνονται (οι πίνακες έχουν δική τους κεφαλίδα)
            return
        self.y = D.heading(self.x, self.y - 5, s, w=self.w, size=size, fill=fill) - 4
        self._chk()

    def p(self, s, bold=None, bullet=None, size=None, color=INK, gap=1.2):
        if not M.SHOW_NOTES:                                   # R20: καμία παράγραφος πάνω στα φύλλα
            return
        self.y = D.para(self.x + 1, self.y, s, self.w - 2, size=size or self.size, bold=bold, bullet=bullet, color=color) - gap
        self._chk()

    def gap(self, d=4):
        self.y -= d

    def table(self, widths, rows, **kw):
        sc = self.w / float(sum(widths))
        self.y = D.table(self.x, self.y + 5, [w * sc for w in widths], rows, **kw) - 9
        self._chk()


def cols(n, y, gap=20, name=""):
    w = (X1 - X0 - gap * (n - 1)) / n
    return [Flow(X0 + i * (w + gap), y, w, name="%s/%d" % (name, i + 1)) for i in range(n)]


# ================================================================ ΗΛ-11 ΠΙΝΑΚΑΣ ΚΥΚΛΩΜΑΤΩΝ ΚΑΙ ΠΡΟΣΤΑΣΙΩΝ
CONDUIT = {"3×1,5": "Ø16", "3×2,5": "Ø20", "3×4": "Ø25", "3×6": "Ø25", "5×2,5": "Ø25", "5×6": "Ø32"}
GRP_TXT = {"ΔΔΡ-1": "ομάδα ΔΔΡ-1", "ΔΔΡ-2": "ομάδα ΔΔΡ-2", "ΔΔΡ-3": "ομάδα ΔΔΡ-3", "RCBO A": "ατομικό ΔΔΡ 30 mA · A", "RCBO F": "ατομικό ΔΔΡ 30 mA · F",
           "ΔΔΡ EV": "ΔΔΡ 4P 30 mA · A-EV"}
GRP_FILL = (0.86, 0.88, 0.93)


def breaker_txt(c):
    pol = {1: "1P", 2: "1P+N", 3: "3P", 4: "3P+N"}[c["poles"]]
    return "%s%d %s" % (c["curve"], c["In"], pol)


def positions():
    """Θέση κάθε στοιχείου στη ράγα του πίνακα από το PANEL_ROWS: {κωδικός: "Σ2 · 5–6"} (σειρά, πρώτο–τελευταίο στοιχείο των 18)."""
    pos = {}
    for ri, row in enumerate(M.PANEL_ROWS, 1):
        k = 1
        for lab, n, kind in row:
            cid = lab.split()[0] if lab else ""
            if cid and kind in ("mcb", "rcbo", "rcd", "main"):
                pos[cid] = "Σ%d · %s" % (ri, ("%d" % k) if n == 1 else "%d–%d" % (k, k + n - 1))
            k += n
    return pos


def sheet_11(no="ΗΛ-11"):
    """R21: πραγματικός πίνακας κυκλωμάτων – ένας μικροαυτόματος ανά γραμμή, με τη θέση του στη ράγα, σε μεγάλα γράμματα, όλη η σελίδα."""
    y = title("ΠΙΝΑΚΑΣ ΚΥΚΛΩΜΑΤΩΝ – ΓΕΝΙΚΟΣ ΠΙΝΑΚΑΣ «ΓΠ» ΔΙΑΜΕΡΙΣΜΑΤΟΣ (τριφασική παροχή 3 × 35 A)")
    T = CK.circuit_table(); F = CK.feeder_calc(); pos = positions()
    head = ["ΘΕΣΗ\nΣΤΗ ΡΑΓΑ", "ΚΥΚΛ.", "ΤΙ ΤΡΟΦΟΔΟΤΕΙ", "ΦΑΣΗ", "ΜΙΚΡΟΑΥΤΟΜΑΤΟΣ", "ΠΡΟΣΤΑΣΙΑ ΔΙΑΡΡΟΗΣ 30 mA", "ΚΑΛΩΔΙΟ\nmm²", "ΣΩΛΗΝΑΣ", "ΙΣΧΥΣ\nkW", "Ib\nA", "ΜΗΚΟΣ\nm", "ΔU\n%"]
    widths = [50, 36, 250, 32, 78, 118, 50, 42, 40, 34, 42, 34]
    rows, colors = [], {}
    def grp_row(txt):
        colors[len(rows)] = GRP_FILL
        rows.append([("", {}), ("", {}), (txt, dict(font="Inter-Bold"))] + [""] * 9)
    rows.append([(pos.get("Γ.Δ.", "Σ1 · 1–4"), {}), ("Γ.Δ.", {}), ("Γενικός διακόπτης φορτίου 4P 40 A · ενδεικτικές λυχνίες · απαγωγός υπερτάσεων T2 3P+N (Σ1 · 6–9)", {}), "—", "—", "—", M.FEEDER["cable"].replace("J1VV-R ", "").replace(" mm²", ""), "Ø40", "—", fz(F["imax"], 1), fz(F["L"], 0), fz(F["du"], 2)])
    last = None
    for r in T:
        c = r["c"]
        g = c["grp"] if c["grp"].startswith("ΔΔΡ-") else ("EV" if c["id"] == "EV" else "RCBO")
        if g != last:
            if g.startswith("ΔΔΡ-"):
                rc = [x for x in M.RCDS if x["id"] == g][0]
                grp_row("%s – %s · %s · θέση %s" % (g, rc["name"], rc["spec"], pos.get(g, "")))
            elif g == "RCBO":
                grp_row("ΑΤΟΜΙΚΑ ΔΔΡ ΜΕ ΜΙΚΡΟΑΥΤΟΜΑΤΟ (RCBO 1P+N, 30 mA) – ανεξάρτητα κυκλώματα, σειρά 5")
            else:
                grp_row("ΦΟΡΤΙΣΗ ΟΧΗΜΑΤΟΣ – δικό της ΔΔΡ 4P 40 A / 30 mA τύπου A-EV")
            last = g
        cells = [pos.get(c["id"], "—"), c["id"], c["name"], c["ph"], breaker_txt(c), GRP_TXT.get(c["grp"], c["grp"]), c["cable"], CONDUIT.get(c["cable"], "—"),
                 fz(c["P"], 2), fz(r["ib"], 1), fz(r["L"], 1), fz(r["du"], 2)]
        rows.append([(x, {}) for x in cells])
    rows.append([(pos.get("ΕΦ1", "—") + " / " + pos.get("ΕΦ2", "—").split("· ")[-1], {}), ("ΕΦ1–2", {}), ("Εφεδρικοί μικροαυτόματοι (μελλοντικός φωτισμός / αυτοματισμοί)", {}), "—", "B10 1P", "ομάδα ΔΔΡ-1", "—", "—", "—", "—", "—", "—"])
    rows.append([(pos.get("Δ/Λ", "—"), {}), ("Δ/Λ", {}), ("Διακόπτης με λυχνία για τον boiler ηλιακού (ΗΛ)", {}), "—", "—", "—", "—", "—", "—", "—", "—", "—"])
    al = {i: "c" for i in (0, 3, 4, 6, 7, 8, 9, 10, 11)}
    sc = (X1 - X0) / float(sum(widths))
    y = D.table(X0, y + 4, [w * sc for w in widths], rows, head=head, size=8.0, lead=9.8, pad=1.8, bold_first=True, aligns=al, colors=colors, zebra=True)
    # ---------------- κάτω: δύο πίνακες δεδομένων (ισοζύγιο – παροχή) σε μεγάλα γράμματα
    y -= 14
    w2 = (X1 - X0 - 40) / 2.0
    ph = F["ph"]
    rws = [["Εγκατεστημένη ισχύς (με φορτιστή οχήματος 11 kW)", "%s kW" % fz(CK.installed(), 1)],
           ["Άθροισμα αιχμών κυκλωμάτων  L1 / L2 / L3", "%s / %s / %s kW" % (fz(ph["L1"], 2), fz(ph["L2"], 2), fz(ph["L3"], 2))],
           ["Ετεροχρονισμός μεταξύ κυκλωμάτων", fz(M.DIVERSITY, 2)],
           ["Μέγιστη ταυτόχρονη ζήτηση", "%s kW" % fz(F["dem"], 1)],
           ["Ρεύμα της πιο φορτισμένης φάσης", "%s A  (ασφάλεια 35 A)" % fz(F["imax"], 1)],
           ["Ασυμμετρία φάσεων", "%s %%" % fz((max(ph.values()) - min(ph.values())) / (sum(ph.values()) / 3) * 100, 0)]]
    ya = D.table(X0, y, [w2 * 0.66, w2 * 0.34], rws, head=["ΙΣΟΖΥΓΙΟ ΦΑΣΕΩΝ – ΖΗΤΗΣΗ", ""], size=8.0, lead=9.8, pad=1.8, aligns={1: "r"}, zebra=True)
    rws = [["Καλώδιο παροχής", M.FEEDER["cable"]], ["Προστασία", "ασφάλειες 3 × 35 A στην αποθήκη · Γ.Δ. 4P 40 A"],
           ["Ικανότητα καλωδίου Iz (σε σωλήνα, 3 φορτισμένοι)", "%d A ≥ 35 A" % F["iz"]],
           ["Μήκος από τον μετρητή μέσω αποθήκης (εκτίμηση, %s)" % F["fl"], "%s m" % fz(F["L"], 0)],
           ["Πτώση τάσης στην παροχή με 35 A", "%s %%" % fz(F["du"], 2)],
           ["Δυσμενέστερο κύκλωμα + παροχή", "%s %% ≤ 5 %%" % fz(max(r["du"] for r in T) + F["du"], 2)]]
    yb = D.table(X0 + w2 + 40, y, [w2 * 0.56, w2 * 0.44], rws, head=["ΚΕΝΤΡΙΚΗ ΠΑΡΟΧΗ", ""], size=8.0, lead=9.8, pad=1.8, aligns={1: "r"}, zebra=True)
    y = min(ya, yb)
    if M.SHOW_NOTES:
        c_ = Flow(X0, y - 8, X1 - X0, name="ΗΛ-11/παραδοχές")
        c_.p("Ib = ρεύμα του εγκατεστημένου φορτίου του κυκλώματος (cos φ 0,95). Iz = ικανότητα καλωδίου χαλκού PVC σε σωλήνα μέσα σε κοίλο τοίχο / ψευδοροφή "
             "(μέθοδος B2, 30 °C). Έλεγχος: Ib ≤ In ≤ Iz σε όλα τα κυκλώματα. ΔU = πτώση τάσης από τον πίνακα ως το ΜΑΚΡΙΝΟΤΕΡΟ σημείο του κυκλώματος με το Ib.", size=6.6)
    assert y > YB, "ΗΛ-12: ο πίνακας κυκλωμάτων ξεχειλίζει (%.0f)" % y
    finish(no, "ΠΙΝΑΚΑΣ ΚΥΚΛΩΜΑΤΩΝ «ΓΠ»", "Θέση στη ράγα · μικροαυτόματος · ΔΔΡ · καλώδιο · φορτίο · μήκος · ΔU")
