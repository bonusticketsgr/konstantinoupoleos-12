# -*- coding: utf-8 -*-
"""Φύλλο ΠΧ-04: πίνακες τοιχίων, μπαζωμάτων, χωμάτων, σκαλών (A3)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toixopoiies"))
import px_model as PM
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title

KIND_TXT = {"fence": "βάση περίφραξης", "lobby": "τοίχος εσοχής εισόδου", "bound": "μάντρα ορίου / στηθαίο", "ret": "τοιχίο αντιστήριξης",
            "curb": "κράσπεδο", "s2": "υπάρχον κατά Σ2"}


def _f(v, plus=True):
    if v is None:
        return "–"
    s = ("%+.2f" % v) if plus else ("%.2f" % v)
    return s.replace(".", ",").replace("+0,00", "±0,00").replace("-", "−")


def table(c, X, Y, cols, rows, title, fs=6.0, rh=10.5, title_fs=8):
    """cols: [(τίτλος, πλάτος, στοίχιση)] · rows: λίστες κειμένων. Επιστρέφει το Y κάτω από τον πίνακα."""
    c.setFont("Inter-Bold", title_fs); c.setFillColorRGB(*DARK); c.drawString(X, Y, title); Y -= 6
    W = sum(w for _, w, _ in cols)
    c.setFillColorRGB(0.92, 0.92, 0.94); c.rect(X, Y - rh, W, rh, stroke=0, fill=1)
    x = X
    c.setFont("Inter-SemiBold", fs); c.setFillColorRGB(*DARK)
    for name, w, al in cols:
        (c.drawString if al == "l" else c.drawRightString)(x + (3 if al == "l" else w - 3), Y - rh + 3, name); x += w
    Y -= rh
    c.setStrokeColorRGB(0.6, 0.6, 0.63); c.setLineWidth(0.3)
    for i, r in enumerate(rows):
        if i % 2:
            c.setFillColorRGB(0.975, 0.975, 0.98); c.rect(X, Y - rh, W, rh, stroke=0, fill=1)
        x = X
        for (name, w, al), val in zip(cols, r):
            bold = isinstance(val, tuple)
            if bold:
                val = val[0]
            c.setFont("Inter-SemiBold" if bold else "Inter", fs); c.setFillColorRGB(*DARK)
            txt = str(val)
            while c.stringWidth(txt, "Inter", fs) > w - 6 and len(txt) > 3:
                txt = txt[:-2]
            (c.drawString if al == "l" else c.drawRightString)(x + (3 if al == "l" else w - 3), Y - rh + 3, txt); x += w
        Y -= rh
        c.line(X, Y, X + W, Y)
    c.setStrokeColorRGB(*DARK); c.setLineWidth(0.5); c.rect(X, Y, W, (len(rows) + 1) * rh, stroke=1, fill=0)
    return Y - 14


def sheet_tables(c, sheet_no="ΠΧ-04"):
    top = PAGE_H - 40
    # --- τοιχία
    rows = []
    tot_new = 0.0
    for r in PM.wall_rows():
        pos = "x %s–%s · y %s–%s" % (_f(r["x"][0], False), _f(r["x"][1], False), _f(r["y"][0], False), _f(r["y"][1], False))
        if r["id"] == "ΤΧ-02":
            pos = "τόξο R 4,00 (κέντρο −1,20 / 11,45) από (−5,20 / 11,45) ως (−1,20 / 15,45)"
        rows.append([(r["id"],), KIND_TXT[r["kind"]], pos, _f(r["L"], False), ("%d" % round(r["th"] * 100)) if r["id"] != "ΤΧ-02" else "22",
                     _f(r["base"]) if r["base"] is not None else "–", r["top"], ("%.2f" % r["h"]).replace(".", ",") if r["base"] is not None else "–", r["note"]])
        if r["kind"] != "s2":
            tot_new += r["L"]
    cols = [("ID", 36, "l"), ("ΕΙΔΟΣ", 86, "l"), ("ΘΕΣΗ (m μοντέλου)", 150, "l"), ("ΜΗΚΟΣ", 36, "r"), ("ΠΑΧΟΣ cm", 40, "r"),
            ("ΕΔΡΑΣΗ", 44, "r"), ("ΚΟΡΥΦΗ", 92, "r"), ("ΥΨΟΣ", 34, "r"), ("ΠΑΡΑΤΗΡΗΣΗ", 630, "l")]
    Y = table(c, 20, top, cols, rows, "ΤΟΙΧΙΑ ΠΟΥ ΣΗΚΩΝΟΝΤΑΙ ΠΑΝΩ ΣΤΗΝ ΠΛΑΚΑ ΟΡΟΦΗΣ ΥΠΟΓΕΙΟΥ (Σ2)  –  νέα: ΤΧ-01 … ΤΧ-28 (σύνολο μήκους %s m) · υπάρχοντα κατά Σ2: Δ23.1, Δ24.1, ΘΑ, ΘΒ, ΘΓ" % ("%.1f" % tot_new).replace(".", ","), fs=5.6, rh=9.6)
    # --- μπαζώματα
    rows = []; vol = 0.0
    for r in PM.fill_rows():
        rows.append([(r["id"],), r["name"], ("%.1f" % r["area"]).replace(".", ","), _f(r["slab"]), _f(r["fill_top"]) if r["fill_top"] is not None else "κάτω από τα σκαλιά",
                     ("%d" % round(r["thick"] * 100)) + (" (μέσο)" if r["fill_top"] is None else ""), _f(r["final"]) if r["final"] is not None else "σκαλιά",
                     ("%.1f" % r["vol"]).replace(".", ","),
                     "μπάζωμα + πλάκα h18 (Σ2) + επίστρωση 10" if r["pocket"] else ("μπάζωμα + επίστρωση 10" if r["fill_top"] is not None else "σκαλιά σκυροδέματος επί μπαζώματος")])
        vol += r["vol"]
    cols2 = [("ID", 36, "l"), ("ΖΩΝΗ", 200, "l"), ("m²", 36, "r"), ("ΠΛΑΚΑ Σ2", 48, "r"), ("ΚΟΡΥΦΗ ΜΠΑΖ.", 90, "r"), ("ΠΑΧΟΣ cm", 60, "r"),
             ("ΤΕΛΙΚΟ", 44, "r"), ("m³", 34, "r"), ("ΔΟΜΗ", 200, "l")]
    Y = table(c, 20, Y, cols2, rows, "ΜΠΑΖΩΜΑΤΑ  –  σύνολο ≈ %s m³ (συμπυκνωμένο αδρανές / 3Α · στους θύλακες Α-Β-Γ ο μελετητής είχε «φελιζόλ» – ελαφρύ υλικό ή έγκριση φορτίου από Κόγια)" % ("%.1f" % vol).replace(".", ","), fs=5.8, rh=10)
    # --- σκάλες (όλο το πλάτος)
    rows = []
    for st in PM.STAIRS:
        rows.append([(st["id"],), st["name"], "%d" % st["n"], ("%.1f" % (st["riser"] * 100)).replace(".", ","), "%d" % round(st["tread"] * 100),
                     ("%.2f" % (st["x1"] - st["x0"])).replace(".", ","), _f(st["bottom"]), _f(st["top"]), ("%.2f" % (st["top"] - st["bottom"])).replace(".", ","),
                     "ρίχτια στα y %s (πάνω) … %s (κάτω) · 2υ+π = %s" % (_f(st["y_top"], False), _f(st["y_bot"], False), ("%.1f" % ((2 * st["riser"] + st["tread"]) * 100)).replace(".", ","))])
    cols4 = [("ID", 36, "l"), ("ΣΚΑΛΑ", 250, "l"), ("ΡΙΧΤΙΑ", 40, "r"), ("ΥΨΟΣ cm", 46, "r"), ("ΠΑΤΗΜΑ cm", 56, "r"), ("ΠΛΑΤΟΣ", 44, "r"),
             ("ΑΠΟ", 44, "r"), ("ΕΩΣ", 44, "r"), ("ΥΨΟΣ", 40, "r"), ("ΘΕΣΗ", 330, "l")]
    Y = table(c, 20, Y, cols4, rows, "ΣΚΑΛΕΣ ΑΝΟΔΟΥ ΣΤΟ ΙΣΟΓΕΙΟ (σκαλιά σκυροδέματος επί μπαζώματος, επένδυση μάρμαρο 3 + λάσπη 2)", fs=5.8, rh=10)
    # --- χώματα (αριστερά) + πεζοδρόμια (δεξιά)
    rows = []
    for r in PM.soil_rows():
        rows.append([(r["id"],), r["name"], ("%.1f" % r["area"]).replace(".", ","), _f(r["slab"]) if r["slab"] is not None else "έδαφος / Π17",
                     _f(r["top"]), ("%d" % round(r["thick"] * 100)) if r["thick"] is not None else "ως +0,30", r["note"] or ("βότσαλο πάνω σε χώμα, χωρίς γέμισμα" if r["id"] == "Ζ16" else "")])
    cols3 = [("ID", 36, "l"), ("ΧΩΡΟΣ", 214, "l"), ("m²", 36, "r"), ("ΠΛΑΚΑ Σ2", 70, "r"), ("ΑΝΩ ΣΤΑΘΜΗ", 60, "r"), ("ΧΩΜΑ cm", 46, "r"), ("ΠΑΡΑΤΗΡΗΣΗ", 262, "l")]
    table(c, 20, Y, cols3, rows, "ΦΥΤΕΜΕΝΟΙ ΧΩΡΟΙ – ΧΩΜΑ (άνω στάθμη +0,30 = 10 cm κάτω από βεράντες / διαδρόμους)", fs=5.8, rh=10)
    rows = []
    for x in (-1.20, 2.0, 4.30, 6.50, 9.75, 10.95, 13.35, 16.87):
        sw = PM.sw_south(x)
        rows.append(["Κωνσταντινουπόλεως", "x = %s" % _f(x, False), _f(sw), _f(PM.FENCE_BASE - sw, False) if x < 4.31 else "–"])
    for y in (-1.45, 0.0, 1.24, 3.82, 7.5, 11.46):
        sw = PM.sw_west(y)
        rows.append(["Αγ. Βαρβάρας", "y = %s" % _f(y, False), _f(sw), _f(PM.FENCE_BASE - sw, False) if y >= 3.8 else "–"])
    cols5 = [("ΔΡΟΜΟΣ", 100, "l"), ("ΘΕΣΗ", 66, "l"), ("ΠΕΖΟΔΡΟΜΙΟ", 66, "r"), ("ΒΑΣΗ +0,81 ΠΑΝΩ ΑΠΟ ΤΟ ΠΕΖΟΔΡ.", 176, "r")]
    XR = 20 + sum(w for _, w, _ in cols3) + 16
    table(c, XR, Y, cols5, rows, "ΠΕΖΟΔΡΟΜΙΑ (Α-40: Ε +0,40 · Β −0,11 · Α −0,60 · Ζ −0,21, γραμμική παρεμβολή)", fs=5.8, rh=10, title_fs=7)
    frame_and_title(c, sheet_no, "ΠΕΡΙΒΑΛΛΩΝ ΧΩΡΟΣ ΙΣΟΓΕΙΟΥ – ΠΙΝΑΚΕΣ",
                    "Τοιχία (θέση, έδραση, κορυφή, ύψος) · μπαζώματα (πάχος, όγκος) · χώματα · σκάλες · πεζοδρόμια",
                    "Αναφορές στην κάτοψη ΠΧ-01 και στις τομές ΠΧ-02 / ΠΧ-03",
                    "Βάση: Σ2_ΕΦ · A-10-GF R01 · Α-40 · A-80-02/03/04", "–", PM.REV, PM.DATE)
