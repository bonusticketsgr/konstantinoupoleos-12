# -*- coding: utf-8 -*-
"""Προσφορά πώλησης 12/11/2026: Β (2ος) 590.000 € ή Γ (3ος) με μία θέση στάθμευσης 650.000 €.
python3 prosfora_B_G.py  → ../../ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ/ΠΩΛΗΣΕΙΣ/ΠΡΟΣΦΟΡΑ_Β_Γ_12-11-2026.pdf"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "toixopoiies", "fonts")
pdfmetrics.registerFont(TTFont("DV", os.path.join(FONTS, "Inter-Regular.ttf")))
pdfmetrics.registerFont(TTFont("DVB", os.path.join(FONTS, "Inter-SemiBold.ttf")))

OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΠΩΛΗΣΕΙΣ",
                   "ΠΡΟΣΦΟΡΑ_Β_Γ_12-11-2026.pdf")

DARK = colors.HexColor("#1f2a37")
ACC = colors.HexColor("#b08d57")
GREY = colors.HexColor("#6b7280")
LIGHT = colors.HexColor("#f3f1ec")

def P(t, size=9.2, bold=False, color=DARK, lead=None, align=0, sb=0, sa=0):
    return Paragraph(t, ParagraphStyle("x", fontName="DVB" if bold else "DV", fontSize=size,
                     leading=lead or size * 1.28, textColor=color, alignment=align,
                     spaceBefore=sb, spaceAfter=sa))

def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=13*mm, bottomMargin=11*mm,
                            title="Προσφορά πώλησης – Κωνσταντινουπόλεως 12, Αργυρούπολη")
    W = A4[0] - 32*mm
    s = []
    # κεφαλίδα
    head = Table([[P("arkad.", 20, True, DARK),
                   P("ΠΡΟΣΦΟΡΑ ΠΩΛΗΣΗΣ<br/><font size=8 color='#6b7280'>Αρ. 2026-11-01 · Αργυρούπολη, 12 Νοεμβρίου 2026 · Ισχύς έως 27 Νοεμβρίου 2026</font>",
                     11, True, DARK, align=2)]], colWidths=[W*0.4, W*0.6])
    head.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                              ("LINEBELOW", (0,0), (-1,0), 1.2, ACC), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    s += [head, Spacer(1, 5)]
    s.append(P("<b>Κωνσταντινουπόλεως 12 &amp; Αγίας Βαρβάρας, Αργυρούπολη</b> — πενταόροφο κτήριο πέντε κατοικιών, "
               "μία ανά όροφο, με υπόγειο γκαράζ, αποθήκες και ιδιωτικούς εξώστες. Έναρξη 06/2026 · εκτιμώμενη παράδοση 06/2028.", 9.2))
    s.append(P("Προς: ____________________________________", 9.2, sb=5, sa=4))
    s.append(P("Σε συνέχεια της επικοινωνίας μας, σας προτείνουμε δύο επιλογές για τον τυπικό όροφο (95,3 τ.μ., 2 υπνοδωμάτια, "
               "2 λουτρά, ενιαίο καθιστικό–κουζίνα, 3 εξώστες). Οι τιμές ισχύουν για υπογραφή προσυμφώνου έως 27/11/2026.", 9.2, sa=6))

    # πίνακας επιλογών
    rows = [[P("", 9), P("<b>ΕΠΙΛΟΓΗ Α</b><br/><font size=8.2>Διαμέρισμα Β — 2ος όροφος</font>", 10, color=DARK, align=1),
             P("<b>ΕΠΙΛΟΓΗ Β</b><br/><font size=8.2>Διαμέρισμα Γ — 3ος όροφος</font>", 10, color=DARK, align=1)],
            [P("Εμβαδόν κατοικίας"), P("95,3 τ.μ.", align=1), P("95,3 τ.μ.", align=1)],
            [P("Αποθήκες"), P("ΑΠ4 9,25 τ.μ. <b>+ αποθήκη υπογείου 7,65 τ.μ.</b>", align=1), P("ΑΠ2 9,25 τ.μ.", align=1)],
            [P("Στάθμευση (υπόγειο, με υποδομή EV)"), P("1 θέση — Θ.Σ.Υ. 6", align=1), P("1 θέση — Θ.Σ.Υ. 3", align=1)],
            [P("Τιμή καταλόγου 01/09/2026"), P("610.000 €", align=1, color=GREY), P("690.000 € <font size=7.5>(με 2 θέσεις)</font>", align=1, color=GREY)],
            [P("<b>ΤΙΜΗ ΠΡΟΣΦΟΡΑΣ</b>", 10.5, True), P("<b>590.000 €</b>", 13, True, align=1), P("<b>650.000 €</b>", 13, True, align=1)],
            [P("Προαιρετικά"), P("Επιλογή τελειωμάτων ανώτερης κατηγορίας<br/>χωρίς επιβάρυνση (πλακίδια, δάπεδα, χρώματα)", align=1),
             P("2η θέση στάθμευσης Θ.Σ.Υ. 4: <b>+25.000 €</b><br/>Επιλογή τελειωμάτων ανώτερης κατηγορίας χωρίς επιβάρυνση", align=1)]]
    t = Table(rows, colWidths=[W*0.30, W*0.35, W*0.35])
    t.setStyle(TableStyle([
        ("BACKGROUND", (1,0), (-1,0), LIGHT), ("BACKGROUND", (0,5), (-1,5), LIGHT),
        ("LINEBELOW", (0,0), (-1,0), 0.8, ACC), ("LINEABOVE", (0,5), (-1,5), 0.8, ACC), ("LINEBELOW", (0,5), (-1,5), 0.8, ACC),
        ("GRID", (0,1), (-1,-1), 0.25, colors.HexColor("#d9d4c7")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    s += [t, Spacer(1, 7)]

    # πληρωμές + προδιαγραφές δίπλα-δίπλα
    pay = [[P("<b>Τρόπος πληρωμής</b>", 9.5)], 
           [P("• 10 % με το προσύμφωνο (έως 27/11/2026)<br/>"
              "• 20 % με το οριστικό συμβόλαιο (εντός 30 ημερών)<br/>"
              "• 20 % με την ολοκλήρωση του φέροντος οργανισμού<br/>"
              "• 20 % με επιχρίσματα και κουφώματα<br/>"
              "• 20 % με δάπεδα και κουζίνα<br/>"
              "• 10 % με την παράδοση και τη σύνδεση παροχών", 8.6, lead=12.5)]]
    spec = [[P("<b>Τι περιλαμβάνεται</b>", 9.5)],
            [P("• Ενεργειακή κλάση Α, θερμοπρόσοψη 10 cm, υαλοπίνακες low-e<br/>"
               "• Αντλία θερμότητας, ενδοδαπέδια θέρμανση–δροσισμός, κλιματισμός<br/>"
               "• Κουφώματα αλουμινίου ELVIAL με θερμοδιακοπή, ηλεκτρικά ρολά<br/>"
               "• Πόρτα ασφαλείας, προεγκατάσταση συναγερμού, πυρανίχνευση<br/>"
               "• Ηχομόνωση δαπέδων, γυάλινα στηθαία, υδραυλικός ανελκυστήρας 900 kg<br/>"
               "• Επιλογή τελειωμάτων από τον αγοραστή πριν τα δίκτυα (έως 06/2027)", 8.6, lead=12.5)]]
    tp = Table(pay, colWidths=[W*0.46]); ts = Table(spec, colWidths=[W*0.50])
    for x in (tp, ts):
        x.setStyle(TableStyle([("BACKGROUND", (0,0), (0,0), LIGHT), ("LINEBELOW", (0,0), (0,0), 0.6, ACC),
                               ("BOX", (0,0), (-1,-1), 0.25, colors.HexColor("#d9d4c7")),
                               ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    s += [Table([[tp, ts]], colWidths=[W*0.48, W*0.52], style=[("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0)]), Spacer(1, 7)]

    s.append(P("<b>Όροι</b>", 9.5, sa=2))
    s.append(P("Οι τιμές είναι τελικές τιμές πώλησης και περιλαμβάνουν το διαμέρισμα, τις αποθήκες και τη θέση στάθμευσης που αναφέρονται. "
               "Φόρος μεταβίβασης, συμβολαιογραφικά και έξοδα μεταγραφής βαρύνουν τον αγοραστή. Κάθε φάση πληρωμής παραλαμβάνεται με πρωτόκολλο. "
               "Η προσφορά αφορά ένα από τα δύο διαμερίσματα και παύει να ισχύει αν το διαμέρισμα διατεθεί σε τρίτο πριν την υπογραφή προσυμφώνου. "
               "Μετά τις 27/11/2026 ισχύει ο τιμοκατάλογος.", 8.6, lead=12))
    s.append(Spacer(1, 10))
    foot = Table([[P("<b>ARKAD Ι.Κ.Ε.</b> · info@arkadconstructions.com · 6950370259 · 6944522134 · 2102207012", 8.4, color=GREY),
                   P("Για την ARKAD Ι.Κ.Ε.<br/><br/>______________________", 8.4, color=DARK, align=2)]], colWidths=[W*0.6, W*0.4])
    foot.setStyle(TableStyle([("LINEABOVE", (0,0), (-1,0), 1.0, ACC), ("TOPPADDING", (0,0), (-1,-1), 6), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    s.append(foot)
    doc.build(s)
    print(OUT)

if __name__ == "__main__":
    build()
