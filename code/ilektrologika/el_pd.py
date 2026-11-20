"""ΦΥΛΛΟ ΕΡΓΑΣΙΑΣ «ΠΡΙΖΕΣ ΚΑΙ ΔΙΑΚΟΠΤΕΣ – ΜΕ ΑΡΙΘΜΟΥΣ» (Γιάννης 20/11/2026: «σχέδιο μόνο για πρίζες – διακόπτες, με νούμερα,
για να σου λέω ποια θέλω, ποια δεν θέλω καθόλου»).

Ένα φύλλο A3 1:50, ΕΚΤΟΣ τεύχους: στην κάτοψη ΜΟΝΟ οι ρευματοδότες (κόκκινοι) και οι διακόπτες (μπλε), καθένας με τον αριθμό του
(οι ίδιοι αριθμοί με το τεύχος: Π05, Δ3 …)· δεξιά η λίστα ανά χώρο σε απλά λόγια. Χωρίς διαστάσεις, φώτα, θερμοστάτες, data,
παροχές μηχανημάτων. Όλα διαβάζονται από το `b1_el.py` – δεν έχει δικά του δεδομένα.

    python3 el_pd.py        → ΗΛΕΚΤΡΟΛΟΓΙΚΑ/ΠΡΙΖΕΣ_ΔΙΑΚΟΠΤΕΣ_Β1_<REV>.pdf
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
import b1_el as M
import el_draw as D
import el_plans as PL
import el_sheets as SH
from el_draw import P, PWR, SWC, INK, MUTE, SW, VEC

OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΠΡΙΖΕΣ_ΔΙΑΚΟΠΤΕΣ_Β1_%s.pdf" % M.REV)

ROOMS = [("ΚΑΘ", "ΚΑΘΙΣΤΙΚΟ (ΣΑΛΟΝΙ) – ΤΡΑΠΕΖΑΡΙΑ"), ("ΚΟΥΖ", "ΚΟΥΖΙΝΑ"), ("ΧΩΛ", "ΧΩΛ"), ("ΥΠ1", "ΥΠΝΟΔΩΜΑΤΙΟ 1 (γονέων)"), ("ΛΓ", "ΛΟΥΤΡΟ ΓΟΝΕΩΝ"),
         ("ΥΠ2", "ΥΠΝΟΔΩΜΑΤΙΟ 2"), ("ΛΟΥ", "ΛΟΥΤΡΟ"), ("ΕΞ", "ΕΞΩΣΤΕΣ")]
# τι ανάβει κάθε ομάδα – σύντομα, όπως θα το έλεγε κανείς
G_TXT = {"β": "φώτα εισόδου", "α": "σαλόνι: σειρά καναπέ", "λ": "σαλόνι: μεσαία σειρά", "γ": "σαλόνι: σειρά τζαμαριών", "ε": "κουζίνα",
         "ε2": "LED πάγκου κουζίνας", "ζ": "φώτα Υπν.1", "θ": "LED κεφαλαριού", "κ": "φώτα Υπν.2", "η": "χωλ", "μ": "λουτρό", "μ2": "καθρέπτης λουτρού",
         "ν": "λουτρό γονέων", "ν2": "καθρέπτης λ. γονέων", "ξ1": "φώτα νότιου / δυτικού εξώστη", "ξ2": "φώτα εξώστη Υπν.1"}
BW, BH = 0.40, 0.21                 # κουτί ετικέτας σε m (με περιθώριο)
SIZE = 6.0
# χειροκίνητες θέσεις ετικετών (dx, dy σε m από το σημείο) όπου η αυτόματη δεν βγαίνει καθαρή
AT = {"Π50": (0.0, 0.32), "Π51": (-0.17, 0.32), "Π52": (0.05, 0.32), "Π53": (0.14, 0.32), "Π54": (0.06, 0.32), "Π55": (0.48, 0.32), "Π56": (0.0, 0.41)}


def _rect(cx, cy, w=BW, h=BH):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _points():
    pts = [(s[0], s[1], s[2], s[3], PWR) for s in M.SOCKETS] + [(s[0], s[1], s[2], s[3], SWC) for s in M.SWITCHES]
    return pts


def _place(pts, avoid):
    """Θέση ετικέτας για κάθε σημείο: πάντα προς την πλευρά του χώρου (ποτέ πάνω στον τοίχο), όσο πιο κοντά γίνεται, χωρίς να πατά σε άλλη
    ετικέτα, σε σύμβολο ή σε κείμενο του υποβάθρου. Επιστρέφει {id: (cx, cy)}."""
    sym = [(i, _rect(x + VEC[d][0] * 0.07, y + VEC[d][1] * 0.07, 0.20, 0.20)) for i, x, y, d, c in pts]
    out, used = {}, []
    # πρώτα τα σημεία που έχουν πολλούς γείτονες (οι δύσκολες γωνιές διαλέγουν πρώτες)
    def crowd(p):
        return -sum(1 for q in pts if abs(q[1] - p[1]) < 0.8 and abs(q[2] - p[2]) < 0.8)
    for i, x, y, d, c in sorted(pts, key=crowd):
        nx, ny = VEC[d]; tx, ty = -ny, nx
        if i in AT:
            cx, cy = x + AT[i][0], y + AT[i][1]
            out[i] = (cx, cy); used.append(_rect(cx, cy)); continue
        best = None
        for dn in (0.30, 0.42, 0.55, 0.70, 0.88, 1.08, 1.30):
            for dt in (0.0, 0.22, -0.22, 0.44, -0.44, 0.68, -0.68, 0.92, -0.92):
                dn_ = dn + (0.10 if nx else 0.0)            # οριζόντια η ετικέτα είναι πιο φαρδιά
                cx, cy = x + nx * dn_ + tx * dt, y + ny * dn_ + ty * dt
                r = _rect(cx, cy)
                if any(_hit(r, u) for u in used) or any(_hit(r, s) for j, s in sym if j != i) or any(_hit(r, a) for a in avoid):
                    continue
                cost = dn + abs(dt) * 1.15
                if best is None or cost < best[0]:
                    best = (cost, cx, cy)
        assert best, "δεν βρέθηκε θέση για την ετικέτα %s" % i
        out[i] = best[1:]; used.append(_rect(*best[1:]))
    return out


def _room_text_boxes():
    """Τα ονόματα / εμβαδά χώρων που γράφει το υπόβαθρο (για να μην πατούν πάνω τους οι ετικέτες)."""
    out = []
    for r in getattr(M.W, "ROOMS", []):
        x, y = r[2]
        hw = max(len(r[0]), len(r[1])) * 0.062 + 0.05
        out.append((x - hw, y - 0.20, x + hw, y + 0.32))
    return out


def sheet(no="ΠΔ-01"):
    pts = _points()
    pos = _place(pts, _room_text_boxes())

    def fn(v):
        c = v.c
        for i, x, y, d, col in pts:                      # οδηγοί
            nx, ny = VEC[d]; X0, Y0 = v.p(x + nx * 0.07, y + ny * 0.07); X1, Y1 = v.p(*pos[i])
            c.saveState(); c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(1.8); c.line(X0, Y0, X1, Y1)
            c.setStrokeColorRGB(*col); c.setLineWidth(0.55); c.line(X0, Y0, X1, Y1); c.restoreState()
        for s in M.SOCKETS:                              # σύμβολα
            if s[5] == "fix":
                D.fixed_out(v, s[1], s[2], s[3], col=PWR)
            else:
                D.socket(v, s[1], s[2], s[3], n=s[4], col=PWR, kind=s[5])
        PL.switches(v)
        PL.panel(v, lab=False)
        for i, x, y, d, col in pts:                      # αριθμοί
            X, Y = v.p(*pos[i])
            P.pill(X, Y, i, None, col, "c", SIZE)
    PL._plan(fn, "ΠΡΙΖΕΣ ΚΑΙ ΔΙΑΚΟΠΤΕΣ – ΜΕ ΑΡΙΘΜΟΥΣ")

    # ------------------------------------------------ δεξιά στήλη: λίστα ανά χώρο
    y = 800.0
    y = P._head(y, "ΠΩΣ ΜΟΥ ΑΠΑΝΤΑΣ") or y
    y = _para(y, "Γράψε μου τον αριθμό και τι θες, π.χ.:  Π05 οκ · Π23 όχι · Π41 πιο αριστερά · Δ3 να πάει δίπλα στην πόρτα · «θέλω και μία πρίζα στο …».", 5.9)
    y = _para(y - 2, "Κόκκινο Π = πρίζα · μπλε Δ = διακόπτης. Ίδιοι αριθμοί με το τεύχος %s. Ύψος = από το τελικό δάπεδο ως τη μέση του κουτιού." % M.REV, 5.4, MUTE)
    rows, colors = [], {}
    for code, name in ROOMS:
        ss = [s for s in M.SOCKETS if s[8] == code]
        if not ss:
            continue
        colors[len(rows)] = (0.90, 0.90, 0.92)
        rows.append(["", (name, dict(font="Inter-Bold")), ""])
        for s in ss:
            n = {1: "", 2: "διπλή · ", 3: "τριπλή · ", 4: "2 διπλές · "}[s[4]]
            if s[5] == "fix":
                n = "παροχή (όχι πρίζα) · "
            rows.append([(s[0], dict(color=PWR, font="Inter-Bold")), n + _short(s[9]), SH.fz(s[6])])
    y = D.table(P.PX - 4, y - 6, [26, P.PW - 26 - 26 + 8, 26], rows, head=["ΠΡΙΖΑ", "ΤΙ ΕΙΝΑΙ / ΠΟΥ", "ΥΨΟΣ"], size=5.7, lead=6.7, pad=1.4, aligns={2: "r"}, colors=colors, zebra=False)
    who = {}
    for s in M.SWITCHES:
        for k, g in s[4]:
            who.setdefault(g, []).append(s[0])
    rows = []
    for s in M.SWITCHES:
        h = PL._opt(s, 7).get("h", M.H_SW)
        keys = []
        for k, g in s[4]:
            oth = [o for o in who[g] if o != s[0]]
            ex = (["dimmer"] if k == "D" else []) + (["και από " + ", ".join(oth)] if oth else [])
            keys.append(G_TXT[g] + (" (%s)" % " · ".join(ex) if ex else ""))
        rows.append([(s[0], dict(color=SWC, font="Inter-Bold")), _short(s[6]) + ":  " + "  |  ".join(keys), SH.fz(h)])
    y = D.table(P.PX - 4, y - 7, [26, P.PW - 26 - 26 + 8, 26], rows, head=["ΔΙΑΚ.", "ΠΟΥ ΕΙΝΑΙ:  ΤΙ ΑΝΑΒΕΙ ΚΑΘΕ ΠΛΗΚΤΡΟ", "ΥΨΟΣ"], size=5.7, lead=6.7, pad=1.4, aligns={2: "r"})
    y = _para(y - 8, "Δεν φαίνονται εδώ (είναι στο τεύχος): φώτα, θερμοστάτες, θυροτηλεόραση, πρίζες internet / TV, παροχές κλιματιστικών και αντλίας "
                     "θερμότητας. Το φως του ΒΑ εξώστη ανάβει μόνο του (ανιχνευτής κίνησης) – δεν έχει διακόπτη.", 5.4, MUTE)
    assert y > P.BOT + 6, "ΠΔ: η δεξιά στήλη ξεχειλίζει κατά %.0f pt" % (P.BOT + 6 - y)
    ns = sum(1 for s in M.SOCKETS if s[5] != "fix"); nf = len(M.SOCKETS) - ns
    PL._finish(no, "ΠΡΙΖΕΣ ΚΑΙ ΔΙΑΚΟΠΤΕΣ – ΜΕ ΑΡΙΘΜΟΥΣ", "φύλλο εργασίας · %d πρίζες · %d παροχές · %d διακόπτες" % (ns, nf, len(M.SWITCHES)))


def _short(t):
    """Περιγραφή χωρίς παρενθέσεις / τεχνικές σημειώσεις."""
    import re
    t = re.sub(r"\s*\([^)]*\)", "", t)
    for a, b in ((" – ΠΡΟΒΛΕΨΗ", ""), (" – ΠΥΡΑΝΤΟΧΟ κουτί", ""), (", με USB-C", " + USB"), (" – 2 διπλοί μέσα στην ΤΝ", " (μέσα στην τεχνική ντουλάπα)"),
                 (" – κουτί σύνδεσης 3Φ μέσα στο ερμάριο", " (μέσα στο ερμάριο)"), (" – πάνω από τον συλλέκτη", " (μέσα στη ντουλάπα)"),
                 (", 10 cm από τη λαμπά", ""), (", στον δυτικό τοίχο δίπλα της", ""), (" – φώτα δυτικού / νότιου εξώστη", "")):
        t = t.replace(a, b)
    return t


def _para(y, s, size, col=INK):
    c = P.C
    for ln in P.wrap(s, "Inter-Medium", size, P.PW + 4):
        y -= size + 1.9
        c.setFont("Inter-Medium", size); c.setFillColorRGB(*col); c.drawString(P.PX - 2, y, ln)
    return y


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    P.C = P.new_canvas(OUT, "Πρίζες και διακόπτες με αριθμούς – Β1 %s – Κωνσταντινουπόλεως 12, Αργυρούπολη" % M.REV)
    P.C.setPageCompression(1)
    SH.bind(M)
    sheet()
    P.C.save()
    print("→", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
