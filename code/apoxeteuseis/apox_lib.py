"""Κοινά βοηθητικά για τα φύλλα αποχετεύσεων (ReportLab πάνω στις κατόψεις τοιχοποιιών του repo)."""
import sys, os
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toixopoiies")
sys.path.insert(0, REPO)
import b1_model as B, gf_model as G, s_model as S, f4_model as F, b_model as Y
import sheet_t01
from draw import View, new_canvas, frame_and_title, north_arrow, PAGE_W, PAGE_H, PT_PER_M_60, DARK, GREY

REV, DATE = "R14", "10/11/2026"
RED = (0.80, 0.08, 0.12); ORG = (0.90, 0.45, 0.00); GRN = (0.00, 0.55, 0.30); BLU = (0.05, 0.35, 0.80)
PUR = (0.50, 0.15, 0.65); BEAM = (0.95, 0.55, 0.10); GHOST = (0.55, 0.55, 0.55)

# ---------------- θέσεις στηλών (m μοντέλου: x ανατολικά, y νότια) – ίδιες σε όλους τους ορόφους
ST = {"ΑΠ1": (6.33, 0.87), "ΑΠ2": (9.31, 4.78), "ΑΠ3": (2.30, 4.78), "ΑΠ4": (13.03, 7.93)}
MECH = {"ΑΠ1": (6.29, 0.80), "ΑΠ2": (9.34, 4.93), "ΑΠ3": (2.30, 4.93), "ΑΠ4": (13.05, 7.84), "ΥΔ3": (1.25, 5.50)}
RD = {"ΥΔ1": (9.86, 0.59), "ΥΔ2": (9.32, 9.60), "ΥΔ3": (1.10, 5.33)}
DIA = {}                      # διατομή ανά στήλη (προεπιλογή 100)
GHOST_LBL = "Θέση μηχανολόγου όπου μετακινήθηκε (διακεκομμένη)"
YD_LBL = "Υδρορροή ΥΔ Φ75 – έξω από πλάκα / γέμισμα"
C = None
BEAMS = [("Δ6.1 30/55", (0.80, 1.20, 1.10, 4.85), (0.95, 2.55), 90),
         ("Δ3.1 30/50", (1.70, 4.85, 9.40, 5.15), (5.9, 5.25), 0),
         ("Δ12.2 25/40", (11.45, 7.60, 13.10, 7.85), (11.9, 7.48), 0),
         ("Δ10.2", (13.10, 5.80, 13.35, 7.85), (13.55, 6.7), 90),
         ("Δ4.6 30/40", (9.70, 9.15, 12.70, 9.45), (11.2, 9.05), 0)]

def use(model):
    sheet_t01.M = model
    sheet_t01.OX, sheet_t01.OY = getattr(model, "OX", 309.5), getattr(model, "OY", 99.8)
    return View(C, sheet_t01.OX, sheet_t01.OY, getattr(model, "PT_PER_M", PT_PER_M_60))

def fade(v, alpha=0.45):
    C.saveState(); C.setFillColorRGB(1, 1, 1); C.setFillAlpha(alpha)
    C.rect(20, 92, PAGE_W - 40, PAGE_H - 112, stroke=0, fill=1); C.restoreState()

def pipe(v, pts, col, lw, dash=None):
    c = v.c; c.saveState(); c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.setLineCap(1); c.setLineJoin(1)
    c.setDash(dash or [])
    p = c.beginPath(); p.moveTo(*v.p(*pts[0]))
    for q in pts[1:]: p.lineTo(*v.p(*q))
    c.drawPath(p, stroke=1, fill=0); c.restoreState()

def tag(v, x, y, s, col, size=5.2, anchor="l", font="Inter-SemiBold", rot=0):
    v.text(x, y, s, size=size, font=font, color=col, anchor=anchor, bg=True, rot=rot)

def stack(v, k, sub=None, dx=0.12, dy=-0.22, anchor="l", ghost=True, box=None):
    x, y = ST[k]
    if box:
        v.rect(*box, stroke=GREY, lw=0.5, fill=(0.93, 0.93, 0.93))
    v.circle(x, y, 0.055, fill=RED, stroke=(0.35, 0, 0), lw=0.5)
    tag(v, x + dx, y + dy, "%s Φ%s" % (k, DIA.get(k, "100")), RED, 5.6, anchor)
    if sub: tag(v, x + dx, y + dy + 0.20, sub, (0.35, 0.05, 0.05), 4.3, anchor, "Inter")
    if ghost and k in MECH and (abs(MECH[k][0] - x) > 0.03 or abs(MECH[k][1] - y) > 0.03):
        mx, my = MECH[k]
        v.circle(mx, my, 0.055, stroke=GHOST, lw=0.4)
        v.line(mx, my, x, y, color=GHOST, lw=0.35, dash=[1, 1])

def downpipe(v, k, sub=None, dx=0.12, dy=-0.22, anchor="l"):
    x, y = RD[k]
    v.circle(x, y, 0.04, fill=BLU, stroke=(0, 0.1, 0.4), lw=0.5)
    tag(v, x + dx, y + dy, "%s Φ75" % k, BLU, 5.4, anchor)
    if sub: tag(v, x + dx, y + dy + 0.19, sub, (0.05, 0.15, 0.45), 4.2, anchor, "Inter")
    if k in MECH:
        mx, my = MECH[k]; v.circle(mx, my, 0.04, stroke=GHOST, lw=0.4); v.line(mx, my, x, y, color=GHOST, lw=0.35, dash=[1, 1])

def grate(v, x, y, to=None, lbl=None, dx=0.12, dy=0.20, anchor="l"):
    v.circle(x, y, 0.08, stroke=BLU, lw=0.7, fill=(0.85, 0.92, 1.0))
    v.line(x - 0.05, y, x + 0.05, y, color=BLU, lw=0.4); v.line(x, y - 0.05, x, y + 0.05, color=BLU, lw=0.4)
    if to: pipe(v, [(x, y)] + to, BLU, 0.9, [2, 1.2])
    if lbl: tag(v, x + dx, y + dy, lbl, BLU, 4.3, anchor, "Inter")

def trap(v, x, y, lbl="ΣΔ"):
    v.rect(x - 0.075, y - 0.075, x + 0.075, y + 0.075, fill=(1, 1, 1), stroke=PUR, lw=0.7)
    v.line(x - 0.075, y - 0.075, x + 0.075, y + 0.075, color=PUR, lw=0.5)
    if lbl: tag(v, x + 0.11, y + 0.02, lbl, PUR, 4.3, "l", "Inter-Medium")

def beams(v, which=None):
    for name, (x0, y0, x1, y1), (lx, ly), rot in BEAMS:
        if which and name.split()[0] not in which: continue
        C.saveState(); C.setFillAlpha(0.18); v.rect(x0, y0, x1, y1, fill=BEAM); C.restoreState()
        v.rect(x0, y0, x1, y1, stroke=BEAM, lw=0.5)
        v.text(lx, ly, name, size=4.2, font="Inter-Medium", color=(0.75, 0.40, 0.0), rot=rot, bg=True)

def legend(x=1022, y=770, extra=()):
    rows = [(RED, "●", "Στήλη λυμάτων ΑΠ (Φ100 / ΑΠ4 Φ75) · αερισμός συνεχίζει"),
            (GHOST, "○", GHOST_LBL),
            (RED, "━", "Λεκάνη → στήλη Φ90 / Φ100"),
            (ORG, "━", "Ποτισόφωνο / σιφώνι → στήλη Φ50–Φ75"),
            (GRN, "━", "Ντους / πλυντήριο Φ50 · νιπτήρας Φ40 · νεροχύτης Φ50"),
            (PUR, "■", "Ποτισόφωνο ΠΣ (σιφώνι δαπέδου)"),
            (BLU, "●", YD_LBL),
            (BLU, "◎", "Σιφώνι ομβρίων εξώστη · διακεκ. = πλευρική έξοδος"),
            (BEAM, "▭", "Δοκός (Σ4/Σ5) – καμία οπή")] + list(extra)
    C.setFillColorRGB(1, 1, 1); C.rect(x - 6, y - 14 * len(rows) - 22, 160, 14 * len(rows) + 30, stroke=0, fill=1)
    C.setFont("Inter-Bold", 6.5); C.setFillColorRGB(*DARK); C.drawString(x, y, "ΥΠΟΜΝΗΜΑ")
    for i, (col, sym, t) in enumerate(rows):
        yy = y - 14 - i * 14
        C.saveState(); C.setStrokeColorRGB(*col); C.setFillColorRGB(*col)
        if sym == "━": C.setLineWidth(1.8); C.line(x, yy + 2.5, x + 8, yy + 2.5)
        elif sym == "●": C.circle(x + 4, yy + 2.5, 2.6, stroke=0, fill=1)
        elif sym == "○": C.setLineWidth(0.6); C.circle(x + 4, yy + 2.5, 2.6, stroke=1, fill=0)
        elif sym == "■": C.setLineWidth(0.7); C.rect(x + 1.5, yy, 5, 5, stroke=1, fill=0); C.line(x + 1.5, yy, x + 6.5, yy + 5)
        elif sym == "◎": C.setLineWidth(0.7); C.circle(x + 4, yy + 2.5, 3, stroke=1, fill=0); C.setDash([1.5, 1]); C.line(x + 7, yy + 2.5, x + 11, yy + 2.5)
        elif sym == "▭": C.setFillAlpha(0.25); C.setLineWidth(0.6); C.rect(x, yy, 9, 5, stroke=1, fill=1)
        C.restoreState()
        C.setFont("Inter", 4.9); C.setFillColorRGB(*DARK)
        # σπάσιμο γραμμής
        words, cur, lines = t.split(), "", []
        for w in words:
            tt = (cur + " " + w).strip()
            if C.stringWidth(tt, "Inter", 4.9) > 138 and cur: lines.append(cur); cur = w
            else: cur = tt
        lines.append(cur)
        for j, ln in enumerate(lines): C.drawString(x + 12, yy + 1 - j * 5.6, ln)

def notes(title, items, x=1022, y=None, w=132):
    y = y or 470
    C.setFillColorRGB(1, 1, 1); C.rect(x - 6, 96, w + 12, y - 96 + 12, stroke=0, fill=1)
    C.setFont("Inter-Bold", 6.5); C.setFillColorRGB(*DARK); C.drawString(x, y, title)
    yy = y - 11
    for it in items:
        words, cur, lines = it.split(), "", []
        for wd in words:
            tt = (cur + " " + wd).strip()
            if C.stringWidth(tt, "Inter", 5.0) > w and cur: lines.append(cur); cur = wd
            else: cur = tt
        lines.append(cur)
        for j, ln in enumerate(lines):
            C.setFont("Inter", 5.0); C.setFillColorRGB(*DARK); C.drawString(x + (0 if j == 0 else 6), yy, ln); yy -= 6.3
        yy -= 2.5

SUB1 = "Αποχετεύσεις λυμάτων · υδρορροές · κατά μηχανολογική μελέτη αδείας"
def page(sheet, theme, sub2, base, scale="Κλίμακα 1:60 · A3"):
    C.setFillColorRGB(1, 1, 1); C.rect(20, 20, PAGE_W - 40, 72, stroke=0, fill=1)
    frame_and_title(C, sheet, theme, SUB1, sub2,
                    base, scale, REV, DATE)
    north_arrow(C, 1150, 795)

