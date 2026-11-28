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


def sheet_11(no="ΗΛ-11"):
    y = title("ΠΙΝΑΚΑΣ ΗΛΕΚΤΡΙΚΩΝ ΚΥΚΛΩΜΑΤΩΝ ΚΑΙ ΠΡΟΣΤΑΣΙΩΝ – ΓΕΝΙΚΟΣ ΠΙΝΑΚΑΣ «ΓΠ»", "τριφασική παροχή 3 × 35 A · %d κυκλώματα + %d εφεδρικά" % (len(M.CIRCUITS), M.SPARE_MCB))
    T = CK.circuit_table(); F = CK.feeder_calc()
    head = ["ΚΥΚΛ.", "ΤΙ ΤΡΟΦΟΔΟΤΕΙ", "ΦΑΣΗ", "P εγκ.\nkW", "συντ.", "P αιχμής\nkW", "Ib\nA", "ΜΙΚΡΟ-\nΑΥΤΟΜΑΤΟΣ", "ΚΑΛΩΔΙΟ\nmm²", "Iz\nA", "ΠΡΟΣΤΑΣΙΑ\nΔΙΑΡΡΟΗΣ",
            "ΣΩΛΗ-\nΝΑΣ", "L μέγ.\nm", "ΔU\n%", "ΚΑΛΩΔΙΟ\nm", "ΓΡΑΜΜΗ ΜΕΛΕΤΗΣ ΑΔΕΙΑΣ (Η09)"]
    widths = [30, 262, 28, 34, 28, 40, 30, 58, 46, 26, 96, 34, 36, 30, 44, 150]
    rows, colors = [], {}
    def grp_row(txt):
        colors[len(rows)] = GRP_FILL
        rows.append([("", {}), (txt, dict(font="Inter-Bold"))] + [""] * 14)
    last = None
    for r in T:
        c = r["c"]
        g = c["grp"] if c["grp"].startswith("ΔΔΡ-") else ("EV" if c["id"] == "EV" else "RCBO")
        if g != last:
            if g.startswith("ΔΔΡ-"):
                rc = [x for x in M.RCDS if x["id"] == g][0]
                grp_row("%s – %s · %s" % (g, rc["name"], rc["spec"]))
            elif g == "RCBO":
                grp_row("ΑΤΟΜΙΚΑ ΔΔΡ ΜΕ ΜΙΚΡΟΑΥΤΟΜΑΤΟ (RCBO 1P+N, 30 mA) – ανεξάρτητα κυκλώματα")
            else:
                grp_row("ΦΟΡΤΙΣΗ ΟΧΗΜΑΤΟΣ – δικό της ΔΔΡ 4P 40 A / 30 mA τύπου A-EV · φορτιστής με διαχείριση φορτίου (δεν προστίθεται στην αιχμή)")
            last = g
        col = {}
        cells = [c["id"], c["name"], c["ph"], fz(c["P"], 2), fz(c["g"], 1), fz(c["P"] * c["g"], 2), fz(r["ib"], 1), breaker_txt(c), c["cable"],
                 "%d" % r["iz"] if r["iz"] else "—", GRP_TXT.get(c["grp"], c["grp"]), CONDUIT.get(c["cable"], "—"), fz(r["L"], 1), fz(r["du"], 2),
                 fz(r["tot"], 0) if r["tot"] else "—", c["permit"]]
        rows.append([(x, col) for x in cells])
    rows.append([("ΕΦ1–2", {}), ("Εφεδρικοί μικροαυτόματοι στην ομάδα ΔΔΡ-1 (π.χ. μελλοντικός φωτισμός / αυτοματισμοί)", {}), "—", "—", "—", "—", "—", "B10 1P", "—", "—", "ομάδα ΔΔΡ-1", "—", "—", "—", "—", "30 · 31 (εφεδρικές)"])
    al = {i: "c" for i in (2, 3, 4, 5, 6, 9, 11, 12, 13, 14)}
    sc = (X1 - X0) / float(sum(widths))
    y = D.table(X0, y + 4, [w * sc for w in widths], rows, head=head, size=6.5, lead=7.8, pad=2.5, bold_first=True, aligns=al, colors=colors, zebra=False)
    # ---------------- κάτω: ισοζύγιο – παροχή – παραδοχές
    y -= 8
    w3 = (X1 - X0 - 40) / 3.0
    a = Flow(X0, y, w3, name="ΗΛ-11/α"); b = Flow(X0 + w3 + 20, y, w3, name="ΗΛ-11/β"); c_ = Flow(X0 + 2 * (w3 + 20), y, w3, name="ΗΛ-11/γ")
    ph = F["ph"]
    a.h("ΙΣΟΖΥΓΙΟ ΦΑΣΕΩΝ – ΖΗΤΗΣΗ")
    rws = [["Εγκατεστημένη ισχύς (με φορτιστή οχήματος 11 kW)", "%s kW" % fz(CK.installed(), 1)],
           ["Άθροισμα αιχμών κυκλωμάτων  L1 / L2 / L3", "%s / %s / %s kW" % (fz(ph["L1"], 2), fz(ph["L2"], 2), fz(ph["L3"], 2))],
           ["Ετεροχρονισμός μεταξύ κυκλωμάτων", fz(M.DIVERSITY, 2)],
           ["Μέγιστη ταυτόχρονη ζήτηση", "%s kW" % fz(F["dem"], 1)],
           ["Ρεύμα της πιο φορτισμένης φάσης", "%s A  (ασφάλεια 35 A)" % fz(F["imax"], 1)],
           ["Ασυμμετρία φάσεων", "%s %%" % fz((max(ph.values()) - min(ph.values())) / (sum(ph.values()) / 3) * 100, 0)]]
    a.table([220, 130], rws, size=6.6, aligns={1: "r"})
    b.h("ΚΕΝΤΡΙΚΗ ΠΑΡΟΧΗ")
    rws = [["Καλώδιο (η άδεια είχε 5×10 χωρίς την αποθήκη)", M.FEEDER["cable"]], ["Προστασία", "ασφάλειες 3 × 35 A στην αποθήκη · Γ.Δ. 4P 40 A"],
           ["Ικανότητα καλωδίου Iz (σε σωλήνα, 3 φορτισμένοι)", "%d A ≥ 35 A" % F["iz"]],
           ["Μήκος από τον μετρητή μέσω αποθήκης (εκτίμηση, %s)" % F["fl"], "%s m" % fz(F["L"], 0)],
           ["Πτώση τάσης στην παροχή με 35 A", "%s %%" % fz(F["du"], 2)],
           ["Δυσμενέστερο κύκλωμα + παροχή", "%s %% ≤ 5 %%" % fz(max(r["du"] for r in T) + F["du"], 2)]]
    b.table([220, 130], rws, size=6.6, aligns={1: "r"})
    c_.h("ΠΑΡΑΔΟΧΕΣ")
    c_.p("Ib = ρεύμα του εγκατεστημένου φορτίου του κυκλώματος (cos φ 0,95). Iz = ικανότητα καλωδίου χαλκού PVC σε σωλήνα μέσα σε κοίλο τοίχο / ψευδοροφή "
         "(μέθοδος B2, 30 °C). Έλεγχος: Ib ≤ In ≤ Iz σε όλα τα κυκλώματα.", size=6.6)
    c_.p("ΔU = πτώση τάσης από τον πίνακα ως το ΜΑΚΡΙΝΟΤΕΡΟ σημείο του κυκλώματος με το Ib (χαλκός 70 °C). «L μέγ.» από τις οδεύσεις του ΗΛ-06· για το ΗΛ "
         "είναι εκτίμηση ως το δώμα από τον δυσμενέστερο όροφο. Στις ψευδοροφές τα καλώδια απλώνονται σε μία στρώση (σχάρα), όχι σε δέμα.", size=6.6)
    c_.p("«Καλώδιο m» = ενδεικτικό συνολικό μήκος του κυκλώματος μέσα στο διαμέρισμα (με 10 % φύρα). Ικανότητα διακοπής μικροαυτομάτων 6 kA – να επιβεβαιωθεί "
         "με το ρεύμα βραχυκυκλώσεως στον μετρητή.", size=6.6)
    finish(no, "ΠΙΝΑΚΑΣ ΚΥΚΛΩΜΑΤΩΝ ΚΑΙ ΠΡΟΣΤΑΣΙΩΝ", "Φορτία · φάσεις · μικροαυτόματοι · καλώδια · ΔΔΡ · πτώση τάσης")
