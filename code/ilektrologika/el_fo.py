"""ΦΥΛΛΟ ΕΡΓΑΣΙΑΣ «ΦΩΤΙΣΜΟΣ – ΠΡΟΤΑΣΗ R18» (Γιάννης 26/11/2026) – ΕΚΤΟΣ ΤΕΥΧΟΥΣ.

Δύο φύλλα A3:
  ΦΩ-01  κάτοψη 1:50 – όλα τα φώτα με όνομα και ομάδα, ο νέος τοίχος του Δ18, χωρίς κουρτινόξυλα · δεξιά: τι άλλαξε, ποιος διακόπτης ανάβει τι
  ΦΩ-02  σαλόνι – τραπεζαρία 1:30 με αποστάσεις κάθε φωτιστικού από τοίχους · δεξιά: πώς σκέφτηκα τον φωτισμό + τι δείχνουν τα προοπτικά

Τα δεδομένα της πρότασης είναι στο `b1_el_r18.py` (αλλάζει στη μνήμη το μοντέλο R17). ΔΕΝ ελέγχονται διαδρομές καλωδίων («διελεύσεις στο τέλος»).

    python3 el_fo.py        → ΗΛΕΚΤΡΟΛΟΓΙΚΑ/ΦΩΤΙΣΜΟΣ_Β1_ΠΡΟΤΑΣΗ_R18.pdf
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
import b1_el as M
import b1_el_r18 as R
R.apply()
M.W.ROOMS = [((r[0], r[1], (5.55, 8.12)) if r[0].startswith("ΚΑΘΙΣΤΙΚΟ") else r) for r in M.W.ROOMS]
import el_draw as D
import el_plans as PL
import el_sheets as SH
PL.SW_LAB["Δ18"] = (-0.34, -0.16)
from el_draw import P, LGT, SWC, INK, MUTE, FIR, HVC, SW

A, W = M.A, M.W
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΗΛΕΚΤΡΟΛΟΓΙΚΑ", "ΦΩΤΙΣΜΟΣ_Β1_ΠΡΟΤΑΣΗ_%s.pdf" % R.REV)
IMG = os.path.join(HERE, "img")
RED = (0.82, 0.10, 0.10)
fz = SH.fz

# πού γράφεται το όνομα κάθε φωτιστικού (dx, dy σε m)· προεπιλογή: από πάνω
LAB = {"ΤΡ3": (0, 0.14), "ΤΡ4": (0, 0.14), "Χ2": (0.22, 0.0), "Ε3": (0.24, 0.0), "Γ3": (0.25, 0.0), "Γ4": (0.25, 0.0), "Λ1": (0.22, 0), "Λ2": (0.22, 0), "Λ3": (0.22, 0),
       "ΕΚ5": (-0.05, -0.13), "ΕΚ6": (0.05, -0.13), "ΕΚ3": (-0.05, -0.13), "ΕΚ4": (0.05, -0.13), "ΕΚ7": (-0.06, -0.13), "ΕΚ8": (0.08, -0.13),
       "ΕΚ9": (-0.05, -0.13), "ΕΚ10": (0.09, -0.13), "ΕΚ1": (-0.05, -0.13), "ΕΚ2": (0.05, -0.13), "Υ7": (0, 0.14), "Υ8": (0, 0.14)}
# ετικέτες ομάδων (γράμμα) πάνω στην κάτοψη
TAGS = [("β", 8.52, 5.40), ("τ", R.TC[0], R.TC[1]), ("σ", R.CC[0], 7.36), ("π", R.SOFA_RET[0] + 0.40, 5.50), ("γ", 6.20, 8.60), ("γ", 2.25, 7.75), ("η", 4.12, 4.12), ("μ3", 6.02, 2.62),
        ("ε", 11.85, 8.86), ("ζ", 2.75, 1.85), ("θ", 4.38, 0.36), ("κ", 7.93, 3.05), ("μ", 6.02, 1.25), ("ν", 2.05, 4.42), ("μ2", 5.40, 3.06), ("ν2", 2.86, 4.78),
        ("ε2", 12.75, 8.22), ("ξ1", 3.10, 10.30), ("ξ1", 0.20, 7.60), ("ξ2", 0.35, 2.05), ("ξ3", 10.575, 1.42)]


def C():
    return P.C


def pool(v, r, lab=None, at=None):
    """Η «λίμνη φωτός» μιας ομάδας – αχνό πορτοκαλί πάνω από το έπιπλο που φωτίζει."""
    C().saveState(); C().setFillAlpha(0.13); v.rect(*r, fill=LGT); C().restoreState()
    if lab:
        D.halo_text(v, at[0], at[1], lab, size=4.0 * getattr(v, "t", 1.0), color=LGT, font="Inter-Bold", bg=False)


SOFA_COL = (0.38, 0.38, 0.45)
POOL = (R.SOFA[0] - 0.12, 5.15, R.SOFA[2] + 0.12, R.SOFA_RET[3] + 0.42)      # «λίμνη» σαλονιού: καναπές γωνία + τραπεζάκι


def corner_sofa(v, lab=False):
    """Καναπές γωνία (σχήμα Γ): πλάτη 0,20 στον βόρειο τοίχο και ανατολικά, μπράτσο δυτικά, το γύρισμα χωρίς μπράτσο."""
    (x0, y0, x1, y1), (rx0, ry0, rx1, ry1) = R.SOFA, R.SOFA_RET
    C().saveState(); C().setFillAlpha(0.60); v.rect(x0, y0, x1, y1, fill=(1, 1, 1)); v.rect(rx0, ry0, rx1, ry1, fill=(1, 1, 1)); C().restoreState()
    k = dict(color=SOFA_COL, lw=0.8)
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, ry1)), ((x1, ry1), (rx0, ry1)), ((rx0, ry1), (rx0, y1)), ((rx0, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        v.line(a[0], a[1], b[0], b[1], **k)
    k = dict(color=SOFA_COL, lw=0.4)
    v.line(x0, y0 + 0.20, x1 - 0.20, y0 + 0.20, **k); v.line(x1 - 0.20, y0 + 0.20, x1 - 0.20, ry1, **k)      # πλάτες
    v.line(x0 + 0.15, y0 + 0.20, x0 + 0.15, y1, **k)                                                        # μπράτσο
    for x in (x0 + 0.15 + (rx0 - x0 - 0.15) / 2, rx0):
        v.line(x, y0 + 0.20, x, y1, **k)                                                                    # μαξιλάρια
    v.line(rx0, y1, x1 - 0.20, y1, **k)
    D.halo_text(v, (x0 + rx0) / 2 + 0.08, y0 + 0.58, "ΚΑΝΑΠΕΣ ΓΩΝΙΑ " + R.SOFA_TXT, size=4.6 if lab else 3.4, color=SOFA_COL, font="Inter-Bold", bg=False)


def new_wall(v, lab=True):
    x0, y0, x1, y1 = R.NEW_WALL
    c = C(); c.saveState(); c.setDash([2.2, 1.4]); v.rect(x0, y0, R.WALL_OLD, y1, stroke=RED, lw=1.1); c.restoreState()
    if lab:
        v.line((x0 + R.WALL_OLD) / 2, y1 + 0.02, (x0 + R.WALL_OLD) / 2 + 0.30, y1 + 0.48, color=RED, lw=0.5)
        D.halo_text(v, (x0 + R.WALL_OLD) / 2 + 0.34, y1 + 0.56, "ΝΕΟΣ ΤΟΙΧΟΣ +0,55", size=4.4 * getattr(v, "t", 1.0), color=RED, anchor="l")


def ceiling(v, names=True):
    D.zone(v, R.STRIP, LGT, alpha=0.05, dash=(3, 2), lw=0.45)
    for u in A.UNITS:
        D.unit_rect(v, u["rect"], col=(0.78, 0.68, 0.88), dashed=True, alpha=0.10)
    for h in A.HATCHES:
        C().saveState(); C().setDash([1.5, 1.5]); v.rect(*h["rect"], stroke=(0.6, 0.6, 0.65), lw=0.4); C().restoreState()
    if names:
        D.halo_text(v, (R.STRIP[0] + R.STRIP[2]) / 2, 8.64, "χαμηλή οροφή +2,48", size=3.6 * getattr(v, "t", 1.0), color=MUTE, font="Inter-Medium")


def lights(v, size=1.0):
    for q in M.STAIR_SPOTS:
        D.spot(v, q[2], q[3], q[1], col=(0.70, 0.70, 0.74))
    for (n, a, b, g, t) in M.LED:
        new = n in ("LED5", "LED6")
        D.led_line(v, a, b, col=RED if new else LGT, lab=(n if t else None), lab_off={"LED5": (-0.20, 0.0), "LED6": (-1.55, 0.13)}.get(n, (0, -0.10)))
    for q in M.SPOTS:
        D.spot(v, q[2], q[3], q[1], col=LGT, lab=q[0], lab_off=LAB.get(q[0], (0.0, -0.13)))
    for (n, x, y, g, t) in M.EXT_SPOTS:
        D.spot(v, x, y, "s65", col=LGT, lab=n, lab_off=LAB.get(n, (0.0, -0.13)))
    for l in M.WALL_LIGHTS:
        D.wall_light(v, l[1], l[2], l[3], col=LGT, kind=l[4], lab=l[0])
    for g, x, y in TAGS:
        X, Y = v.p(x, y)
        P.pill(X, Y, g, None, LGT, "c", 5.6 * size)


def chain(v, vals, at, horiz, side=1):
    for a_, b_ in zip(vals, vals[1:]):
        pa, pb = ((a_, at), (b_, at)) if horiz else ((at, a_), (at, b_))
        D.dim_chain(v, pa, pb, fz(b_ - a_), side=side, size=3.9 * getattr(v, "t", 1.0))


def _para(y, s, size=5.9, col=INK, bold=None, bullet=None):
    return D.para(P.PX - 2, y, s, P.PW + 4, size=size, font="Inter-Medium", color=col, lead=size + 1.7, bold=bold, bullet=bullet)


def _who():
    who = {}
    for s in M.SWITCHES:
        for k, g in s[4]:
            if k != "R":
                who.setdefault(g, []).append(s[0] + (" dimmer" if k == "D" else ""))
    return who


def _count(g):
    n = sum(1 for s in M.SPOTS if s[4] == g) + sum(1 for e in M.EXT_SPOTS if e[3] == g) + sum(1 for l in M.WALL_LIGHTS if l[6] == g)
    led = any(l[3] == g for l in M.LED)
    return ("%d" % n if n else "") + (" + LED" if (led and n) else ("LED" if led else ""))


# ================================================================ ΦΩ-01
def sheet1(no="ΦΩ-01"):
    def fn(v):
        ceiling(v)
        pool(v, (R.TABLE[0] - 0.30, R.TABLE[1] - 0.62, R.TABLE[2] + 0.02, R.TABLE[3] + 0.62))
        pool(v, POOL)
        corner_sofa(v)
        PL.detectors(v, faint=True)
        PL.switches(v, labels=True)
        new_wall(v)
        lights(v)
        PL.panel(v, lab=False)
        # φώτα εξωστών: αποστάσεις
        chain(v, [9.55, R.SOUTH_Y], 6.75, False)
        chain(v, [4.0994, M.EXT_SPOTS[0][1], M.EXT_SPOTS[1][1], R.WALL_X0], 10.62, True)
        chain(v, [-1.00, M.EXT_SPOTS[2][1], M.EXT_SPOTS[3][1], 1.30], 10.62, True)
        chain(v, [5.65, 6.50], -0.38, False)
        chain(v, [1.30, 2.75], 9.86, True)
    PL._plan(fn, "ΦΩΤΙΣΜΟΣ – ΠΡΟΤΑΣΗ: ΟΛΑ ΤΑ ΦΩΤΑ ΜΕ ΟΝΟΜΑ · ΓΡΑΜΜΑ = ΟΜΑΔΑ ΠΟΥ ΑΝΑΒΕΙ ΜΑΖΙ")

    y = 800.0
    y = P._head(y, "ΤΙ ΑΛΛΑΞΑ (όπως το ζήτησες 26/11) – %s" % R.VERSION) or y
    items = [
        ("Τοίχος του Δ18:", "μεγάλωσε 55 cm (κόκκινο διακεκομμένο) και τελειώνει περασιά με τη χαμηλή οροφή. Η νότια συρόμενη γίνεται 4,20 (ήταν 4,75)."),
        ("Κουρτινόξυλα:", "έφυγαν όλα – η γυψοσανίδα φτάνει ως τον τοίχο σε σαλόνι και υπνοδωμάτια."),
        ("ΝΕΟ – Καναπές γωνία 2,90 × 2,00:", "τα 2,90 στον τοίχο, 44 cm από τον πλαϊνό τοίχο και 40 cm πριν από το πέρασμα του χωλ. Το γύρισμα προς την τραπεζαρία."),
        ("ΝΕΟ – Ε2 έφυγε.", "Στη χαμηλή οροφή της εισόδου μένει μόνο το Ε1."),
        ("ΝΕΟ – Ε1 και Ε3 στην ίδια ευθεία:", "50 cm από τον τοίχο. Το Ε3 ήταν 10 cm πιο κάτω χωρίς λόγο – δικό μου λάθος."),
        ("ΝΕΟ – Κάτι ακόμα στον καναπέ:", "κρυφό LED6 στην οροφή, σε όλο τον τοίχο πίσω από τον καναπέ (κόκκινη γραμμή). Φως στον τοίχο, όχι spot πάνω από το κεφάλι. Με dimmer στον Δ2."),
        ("Σαλόνι:", "όχι σειρές – ομάδες πάνω από τα έπιπλα: τραπεζαρία (τ), τραπεζάκι (σ), κουρτίνες (γ). Αναλυτικά στο ΦΩ-02."),
        ("Χωλ:", "τρίτο spot Χ3, μπροστά στη ντουλάπα."),
        ("Λουτρό:", "κρυφό LED5 στην οροφή, σε όλο τον δεξιό (ανατολικό) τοίχο – δικό του πλήκτρο στον Δ6."),
        ("Μπαλκόνια:", "τα φώτα όπως στα προοπτικά του αρχιτέκτονα: ζεύγη στη μέση του βάθους του εξώστη + ένα χαμηλό φωτιστικό τοίχου ΕΤ1 έξω από τον τοίχο της TV."),
    ]
    for i, (b, s) in enumerate(items):
        y = _para(y, s, 5.7, bold=b, bullet="%d" % (i + 1))
    who = _who()
    rows = []
    for g, d in M.GROUPS.items():
        nm = d["name"]
        rows.append([(g, dict(color=LGT, font="Inter-Bold")), nm, _count(g), " · ".join(who.get(g, ["—"]))])
    y = D.table(P.PX - 4, y - 6, [16, P.PW - 16 - 22 - 62 + 8, 22, 62], rows, head=["ΟΜ.", "ΤΙ ΑΝΑΒΕΙ", "ΤΕΜ.", "ΑΠΟ ΠΟΙΟΝ ΔΙΑΚΟΠΤΗ"], size=5.3, lead=6.3, pad=1.5, aligns={2: "c"})
    y = P._head(y - 10, "ΠΩΣ ΜΟΥ ΑΠΑΝΤΑΣ") or y
    y = _para(y, "Με το όνομα ή το γράμμα, π.χ.: «τ οκ» · «Γ3 όχι» · «Σ σε τετράγωνο» · «θέλω άλλο ένα στο …» · «το γύρισμα του καναπέ από την άλλη».", 5.8)
    y = P._head(y - 6, "ΔΙΚΕΣ ΜΟΥ ΕΠΙΛΟΓΕΣ – ΠΕΣ ΜΟΥ") or y
    qs = ["Καναπές: έβαλα το γύρισμα ΑΝΑΤΟΛΙΚΑ (προς την τραπεζαρία) – κοιτά την TV, μένουν ελεύθερα η δυτική μπαλκονόπορτα και το πέρασμα προς το χωλ. Αν το θες προς το μπαλκόνι, πες μου.",
          "Στον καναπέ διάλεξα κρυφό φως στον τοίχο και όχι spots, γιατί τα spots πάνω από τον καναπέ δεν σου άρεσαν. Αν δεν το θες κρυφό, πες μου τι άλλο (απλίκες τοίχου, κρεμαστό πάνω από το τραπεζάκι).",
          "Η πρίζα Π02 πέφτει πίσω από τη γωνία του καναπέ – θα τη δούμε με τις πρίζες.",
          "Κουρτινόξυλα = οι εσοχές κουρτινών της γυψοσανίδας. Τις έβγαλα παντού (και στα υπνοδωμάτια).",
          "Ο νέος τοίχος μικραίνει τη συρόμενη της πρόσοψης κατά 55 cm → να το δει ο αρχιτέκτονας (όψη) και να μπει στην παραγγελία κουφωμάτων.",
          "Το κρυφό LED μόνο στο κοινό λουτρό. Να μπει και στο λουτρό γονέων;",
          "Διαδρομές καλωδίων δεν κοίταξα – στο τέλος, όπως είπες."]
    for i, s in enumerate(qs):
        y = _para(y, s, 5.6, bullet="%d" % (i + 1))
    assert y > P.BOT + 6, "ΦΩ-01: η δεξιά στήλη ξεχειλίζει κατά %.0f pt" % (P.BOT + 6 - y)
    n = len(M.SPOTS) + len(M.EXT_SPOTS)
    PL._finish(no, "ΦΩΤΙΣΜΟΣ – ΠΡΟΤΑΣΗ (ΦΥΛΛΟ ΕΡΓΑΣΙΑΣ)", "%d spots μέσα · %d εξωστών · %d κρυφά LED" % (len(M.SPOTS), len(M.EXT_SPOTS) + 1, len({l[0] for l in M.LED})))


# ================================================================ ΦΩ-02
BOX = (1.00, 4.72, 10.20, 11.55)          # περιοχή του μοντέλου στο 1:30


def sheet2(no="ΦΩ-02"):
    s = P.mm_scale(30)
    P.begin_plan()
    v = P.view(26 - BOX[0] * s, 62 - BOX[1] * s, s); v.sym = 1.0; v.t = 1.30; v.k = 1.3
    _txt = v.text                      # το «ΑΝΟΔΟΣ» της σκάλας πέφτει κάτω από τη δεξιά στήλη (κομμένο, αλλά μένει στο κείμενο του PDF)
    v.text = lambda x_, y_, s_, **k: None if s_ == "ΑΝΟΔΟΣ" else _txt(x_, y_, s_, **k)
    P.base(v, W, site=False, rooms=False, furniture=True)
    v.text = _txt
    ceiling(v)
    pool(v, (R.TABLE[0] - 0.30, R.TABLE[1] - 0.62, R.TABLE[2] + 0.02, R.TABLE[3] + 0.62), "ΤΡΑΠΕΖΑΡΙΑ", (R.TC[0], R.TABLE[1] - 0.50))
    pool(v, POOL, "ΣΑΛΟΝΙ", (R.SOFA_RET[0] + 0.45, POOL[3] - 0.14))
    corner_sofa(v, lab=True)
    for nm, x_, y_ in (("τραπεζάκι", R.CC[0], 6.63), ("TV", 2.90, 8.92), ("τραπέζι", R.TC[0], 6.88)):
        D.halo_text(v, x_, y_, nm, size=4.6, color=MUTE, font="Inter-Medium", bg=False)
    PL.detectors(v, faint=True)
    PL.switches(v, labels=True)
    new_wall(v)
    # αποστάσεις – οριζόντιες
    chain(v, [1.705, R.CC[0] - R.S_PITCH, R.CC[0], R.CC[0] + R.S_PITCH, R.SOFA_RET[0]], R.CC[1] + 0.17, True, side=-1)
    chain(v, [R.TC[0] - R.PITCH / 2, R.TC[0] + R.PITCH / 2, R.WALL_X0], 7.00 - 0.17, True)
    chain(v, [1.705, R.SOFA[0], R.SOFA[2], 5.45], 5.15 + 0.34, True, side=-1)          # θέση του καναπέ στον τοίχο
    chain(v, [5.15, R.SOFA_RET[3]], R.SOFA[2] + 0.14, False, side=-1)
    chain(v, [1.705, R.X_CURT, 5.15, 7.25, R.WALL_X0], R.Y_CURT + 0.17, True, side=-1)
    chain(v, [R.WALL_X0, 8.85, A.LIN_X], R.Y_ENT + 0.17, True, side=-1)
    chain(v, [5.45, R.X_HALL, 6.40], R.Y_ENT + 0.17, True, side=-1)
    c_ = C(); c_.saveState(); c_.setDash([1.2, 2.2]); v.line(6.82, R.Y_ENT, 8.85 - 0.16, R.Y_ENT, color=LGT, lw=0.45); c_.restoreState()   # ίδια ευθεία
    D.halo_text(v, 7.35, R.Y_ENT - 0.09, "Ε1 – Ε3 στην ίδια ευθεία", size=4.4, color=LGT, font="Inter-Medium")
    # κατακόρυφες
    chain(v, [5.15, R.Y_W[0], R.Y_W[1], 9.115], R.X_CURT - 0.31, False)
    chain(v, [R.SOFA[3], R.CC[1]], R.CC[0] + R.S_PITCH + 0.24, False, side=-1)
    chain(v, [5.15, R.Y_ENT], R.X_HALL + 0.20, False, side=-1)
    chain(v, [5.15, 7.00, 7.50, 9.115], 7.85 + 0.20, False, side=-1)
    chain(v, [R.Y_CURT, 9.115], 5.15 - 0.17, False)
    chain(v, [5.15, R.Y_ENT], 9.12, False, side=-1)
    # εξώστης
    chain(v, [9.55, R.SOUTH_Y], 6.72, False, side=-1)
    chain(v, [4.0994, M.EXT_SPOTS[0][1], M.EXT_SPOTS[1][1], R.WALL_X0], R.SOUTH_Y + 0.22, True, side=-1)
    chain(v, [1.30, 2.75], 9.80, True, side=-1)
    chain(v, [4.0994, R.WALL_X0, 8.999], 9.325, True)
    lights(v, size=1.25)
    D.halo_text(v, 2.75, 10.02, "ΕΤ1: +0,55 από το δάπεδο του εξώστη", size=4.6, color=LGT, font="Inter-Medium")
    P.end_plan()
    P.view_title("ΣΑΛΟΝΙ ΜΕ ΚΑΝΑΠΕ ΓΩΝΙΑ – ΤΡΑΠΕΖΑΡΙΑ: ΚΑΘΕ ΦΩΤΙΣΤΙΚΟ ΜΕ ΑΠΟΣΤΑΣΕΙΣ ΑΠΟ ΤΟΥΣ ΤΟΙΧΟΥΣ", "Κλίμακα 1:30"); P.scale_bar(30, marks=(0, 1, 2, 3))

    y = 800.0
    y = P._head(y, "ΠΩΣ ΣΚΕΦΤΗΚΑ ΤΟ ΣΑΛΟΝΙ") or y
    y = _para(y, "Όχι φως παντού το ίδιο. Κάθε ομάδα φωτίζει ένα πράγμα και ανάβει μόνη της· έτσι το ταβάνι «διαβάζεται» ως τραπεζαρία και σαλόνι, "
                 "και το βράδυ ανάβεις μόνο ό,τι χρειάζεσαι. Όλα χωνευτά spots, όλα με dimmer.", 5.8)
    grp = [("π · ΚΑΝΑΠΕΣ – ΚΡΥΦΟ LED6.", "Η γυψοσανίδα σταματά 8 cm πριν από τον τοίχο πίσω από τον καναπέ και μέσα κρύβεται ταινία LED, σε όλο το μήκος του τοίχου (3,75 m). Φωτίζει τον τοίχο από πάνω προς τα κάτω: απαλό φως γύρω από τον καναπέ, χωρίς spot πάνω από το κεφάλι και χωρίς να φαίνεται λάμπα. Χαμηλά = φως για TV."),
           ("τ · ΤΡΑΠΕΖΑΡΙΑ – ΤΡ1–ΤΡ4.", "Τετράγωνο 50 × 50 cm ακριβώς πάνω από το κέντρο του τραπεζιού. Δουλεύει σαν πολύφωτο: το τραπέζι φωτεινό, γύρω πιο ήρεμα. ≈ 400 lx στο τραπέζι στο 100 %."),
           ("σ · ΣΑΛΟΝΙ – Σ1–Σ3.", "Τρία στη σειρά πάνω από το τραπεζάκι, στη μέση της γωνίας του καναπέ. Αυτά ορίζουν το σαλόνι στο ταβάνι."),
           ("γ · ΚΟΥΡΤΙΝΕΣ – Γ1–Γ4.", "Ρυθμιζόμενα, 50 cm από τις τζαμαρίες: το βράδυ η κουρτίνα φωτίζεται και ο χώρος δείχνει μεγαλύτερος. Τα Γ3, Γ4 της δυτικής είναι 1,20 m νότια από τον καναπέ."),
           ("β · ΕΙΣΟΔΟΣ – Ε1, Ε3.", "Ένα στην πόρτα και ένα στο πέρασμα προς το χωλ, στην ίδια ευθεία, 50 cm από τον τοίχο: περνάς το σπίτι χωρίς να ανάψεις το σαλόνι. Το Ε2 έφυγε.")]
    for b, s_ in grp:
        y = _para(y - 1.5, s_, 5.6, bold=b)
    y = _para(y - 2, "Μπροστά στην TV δεν έβαλα τίποτα (καθρεφτίζεται στην οθόνη). Τα 13 spots δίνουν ≈ 190 lx μέσο στο σαλόνι, συν το κρυφό του καναπέ – εκτίμηση με το χέρι, όχι υπολογισμός με πρόγραμμα. "
                     "Spots 9 W / 850 lm, 2700 K, βαθιά χωνευτά για να μη θαμπώνουν.", 5.4, MUTE)
    rows = [["Φαγητό", "τ 100 % · π χαμηλά"], ["Παρέα", "σ · π · γ στο 60 %"], ["TV", "π στο 20 % · όλα τα άλλα σβηστά"], ["Καθάρισμα", "όλα στο 100 %"]]
    y = D.table(P.PX - 4, y - 4, [52, P.PW - 52 + 8], rows, head=["ΣΕΝΑΡΙΟ", "ΤΙ ΑΝΑΒΕΙΣ"], size=5.5, lead=6.5, pad=1.6, bold_first=True)

    y = P._head(y - 10, "ΜΠΑΛΚΟΝΙΑ – ΤΙ ΔΕΙΧΝΟΥΝ ΤΑ ΠΡΟΟΠΤΙΚΑ") or y
    c = C(); wI = P.PW + 4; x0 = P.PX - 2

    def img(name, w, h, marks, cap, x=x0):
        nonlocal y
        y0 = y - h + 4
        c.drawImage(os.path.join(IMG, name), x, y0, w, h)
        c.saveState(); c.setStrokeColorRGB(*RED); c.setLineWidth(1.0)
        for (mx, my, rx, ry) in marks:
            c.ellipse(x + mx - rx, y0 + h - my - ry, x + mx + rx, y0 + h - my + ry)
        c.restoreState()
        y = y0 - 9
        y = _para(y, cap, 5.4, MUTE)

    img("render_notia.jpg", wI, wI * 369 / 1000, [(161 * wI / 246, 8, 13, 6), (56 * wI / 246, 67, 6, 9)],
        "Όψη Κωνσταντινουπόλεως: ζεύγος στην οροφή πάνω από το κέντρο της συρόμενης (ΕΚ1, ΕΚ2) · χαμηλό φωτιστικό στον τοίχο της TV, απ' έξω (ΕΤ1).")
    img("render_dytika.jpg", wI, wI * 456 / 900, [(103 * wI / 246, 28, 15, 7)],
        "Δυτικός εξώστης: ζεύγος στη μέση του βάθους, στο βόρειο άκρο της συρόμενης (ΕΚ5, ΕΚ6). Ίδιο ζεύγος στη ΝΔ γωνία (ΕΚ3, ΕΚ4).")
    y = _para(y - 1, "Στο R17 τα είχα 45 cm από την όψη και σε λάθος θέση κατά μήκος. Ο εξώστης του Υπν.2 δεν φαίνεται σε προοπτικό – ζεύγος στο κέντρο της μπαλκονόπορτας.", 5.4, MUTE)
    assert y > P.BOT + 4, "ΦΩ-02: η δεξιά στήλη ξεχειλίζει κατά %.0f pt" % (P.BOT + 4 - y)
    P.finish(no, "ΣΑΛΟΝΙ: ΦΩΤΙΣΜΟΣ ΜΕ ΑΠΟΣΤΑΣΕΙΣ", "%d spots + κρυφό LED καναπέ · φώτα νότιου εξώστη" % sum(1 for q in M.SPOTS if q[4] in "βτσγ"),
             M.BASE_TXT, "Κλίμακα 1:30 · A3")


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    P.C = P.new_canvas(OUT, "Φωτισμός – πρόταση %s – Β1 – Κωνσταντινουπόλεως 12, Αργυρούπολη" % R.REV)
    P.C.setPageCompression(1)
    SH.bind(M)
    P.SUB1 = "%s · %s" % (R.REV, R.STATUS)
    sheet1(); sheet2()
    P.C.save()
    print("→", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
