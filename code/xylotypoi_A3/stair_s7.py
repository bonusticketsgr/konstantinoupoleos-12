"""Σ7β – ΙΔΙΩΤΙΚΗ ΣΚΑΛΑ Δ1: Δ΄ ΟΡΟΦΟΣ → ΣΟΦΙΤΑ (φύλλο Α3, μία μεγάλη κάτοψη).

    python3 stair_s7.py [preview.png [dpi]]

Χάραξη όπως η μελέτη (Σ7_ΕΦ = A-10-4F / A-10-S R01): 18 ρίχτια, κλάδοι 1,00, φανάρι 0,95 × 0,50 (11,15–12,10 × 6,10–6,60),
1ο και 17ο ρίχτι στο 10,90, πλατύσκαλο-σκαλί 17 (9,70–10,90 × 5,10–6,10) πάνω στην πλάκα Π5 +16,05, 18ο ρίχτι στο 9,70
(ακμή του δαπέδου της σοφίτας). Γραμμή ανάβασης στη μέση του κλάδου (0,50 από το φανάρι): 4,471 m / 16 = 27,9 cm –
τα σφηνοειδή 6–12 ξεκινούν από τα σημεία του αρχιτέκτονα στο φανάρι (ανά 8,3 cm) και περνούν από το σημείο της γραμμής
ανάβασης ώστε το πάτημα να είναι ΙΔΙΟ σε όλα τα σκαλοπάτια (τα εξωτερικά άκρα ± 4 cm από του αρχιτέκτονα).
ΣΤΑΘΜΕΣ (Γιάννης 17/11/2026): Δ΄ γέμισμα 12 → +13,07 (πλάκα +12,95) · σοφίτα γέμισμα 20 → +16,25 (πλάκα +16,05)
→ 3,18 m = 18 × 17,67 cm. Επένδυση σκαλιών 5 (μάρμαρο 3 + λάσπη 2)· στο πλατύσκαλο 17 μένουν 2,3 cm πάνω από την πλάκα =
ξύλινο δάπεδο κολλητό (Γιάννης 17/11/2026: «στη σοφίτα μην υπολογίσεις πλακάκι, θα μπει ξύλο»).
Αρίθμηση όπως A-10-4F / A-10-S: ο αριθμός k πάνω στο πάτημα k (μετά το ρίχτι k), «18» στο δάπεδο της σοφίτας."""
import os, sys, math
import pymupdf
from shapely.geometry import LineString
import stair_s3 as S
from stair_s3 import lib, MM, FONT_R, FONT_B, BLACK, GRAY, BLUE, View, level_mark, cm, mt, lv, CONC, WALLC, RED, FIN, PLATC, DOORC

REV, DATE = "R00", "17/11/2026"
OUT = S.OUT
NAME = "Σ7β_Σκάλα_Δ_ορόφου_σοφίτας_A3_%s.pdf" % REV

N = 18                                    # ρίχτια (όπως η μελέτη)
SSL0, FFL0 = 12.95, 12.95 + S.T_FLOOR     # Δ΄: πλάκα +12,95 · τελικό +13,07 (γέμισμα 12)
SSL1, T_ATTIC = 16.05, 0.20               # σοφίτα: πλάκα +16,05 · γέμισμα 20 (Γιάννης 17/11/2026)
FFL1 = SSL1 + T_ATTIC
FFL0_STUDY, FFL1_STUDY = 13.10, 16.20     # A-10-4F +13,10 · A-10-S / Α-30 +16,20 … +16,25
T_STEP = S.T_STEP
RISE = (FFL1 - FFL0) / N
XL, WXA, WX, XE = 10.90, 11.15, 12.10, 13.10     # 1ο / 17ο ρίχτι · φανάρι 11,15–12,10 · ανατολικός τοίχος
W0, W1, YN, YS = 6.10, 6.60, 5.10, 7.60          # φανάρι 6,10–6,60 · κλάδοι 5,10–6,10 και 6,60–7,60
X18 = 9.70                                       # 18ο ρίχτι = ακμή δαπέδου σοφίτας (ευθεία της Α παρειάς της Κ3)
RW = 0.50                                        # γραμμή ανάβασης στη μέση του κλάδου 1,00
YC = (W0 + W1) / 2


def walk_path():
    pts = [(XL, W1 + RW), (WX, W1 + RW)]
    for i in range(1, 46): a = math.radians(90 - 2 * i); pts.append((WX + RW * math.cos(a), W1 + RW * math.sin(a)))
    for i in range(0, 46): a = math.radians(-2 * i); pts.append((WX + RW * math.cos(a), W0 + RW * math.sin(a)))
    pts.append((XL, W0 - RW))
    return LineString(pts)


WALK = walk_path()
G = (2 * (WX - XL) + math.pi * RW + (W1 - W0)) / 16          # 27,9 cm – ίδιο σε όλα τα σκαλοπάτια
INNER_PT = {6: (WX, W1), 7: (WX, W1 - 1 * (W1 - W0) / 6), 8: (WX, W1 - 2 * (W1 - W0) / 6), 9: (WX, YC),
            10: (WX, W1 - 4 * (W1 - W0) / 6), 11: (WX, W1 - 5 * (W1 - W0) / 6), 12: (WX, W0)}       # σημεία αρχιτέκτονα στο φανάρι


def _make_risers():
    out = {}; r3 = lambda v_: round(v_, 3)
    for k in range(1, 18):
        s = (k - 1) * G
        if k <= 5: x = r3(XL + s); out[k] = ((x, W1), (x, YS))
        elif k >= 13: x = r3(XL + (16 * G - s)); out[k] = ((x, W0), (x, YN))
        else:
            ix, iy = INNER_PT[k]; w = WALK.interpolate(WALK.length * s / (16 * G)); dx, dy = w.x - ix, w.y - iy; cand = []
            if dy > 1e-9: cand.append((YS - iy) / dy)
            if dy < -1e-9: cand.append((YN - iy) / dy)
            if dx > 1e-9: cand.append((XE - ix) / dx)
            t = min(cand); ox, oy = ix + t * dx, iy + t * dy
            out[k] = ((ix, r3(iy)), (XE, r3(oy)) if abs(ox - XE) < 1e-6 else (r3(ox), oy))
    out[18] = ((X18, YN), (X18, W0))
    return out


RISERS = _make_risers()
SPOS = {}
for k_ in range(1, 18):
    ip = WALK.intersection(LineString(RISERS[k_])); SPOS[k_] = WALK.project(ip if ip.geom_type == "Point" else ip.centroid)
GOING = {k: SPOS[k + 1] - SPOS[k] for k in range(1, 17)}
FFL = {k: FFL0 + k * RISE for k in range(0, N + 1)}
SSL = {k: FFL[k] - T_STEP for k in range(1, 17)}; SSL[17] = SSL1          # το πλατύσκαλο-σκαλί 17 είναι η πλάκα Π5 +16,05
T17 = FFL[17] - SSL1                                                       # επένδυση που μένει στο πλατύσκαλο 17
assert max(GOING.values()) - min(GOING.values()) < 0.004, GOING
assert RISE <= 0.18 and min(GOING.values()) >= 0.25 and 0.60 <= 2 * RISE + G <= 0.66
lv3 = S.lv3


def arc(v, cx, cy, r, a0, a1, w, color, dashes=None):
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 24)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    v.poly(pts, w, color, None, dashes, close=False)


def draw_plan(sh):
    v = View(sh, 30.0, 33.0, 8.95, 4.72, 20); yb = 4.85; sh_ = sh
    LIGHT = (0.955, 0.955, 0.93); WBLUE = (0.80, 0.86, 0.93)
    # δάπεδα: σοφίτα (δυτικά του 9,70) · πλατύσκαλο-σκαλί 17 · ξεκίνημα στον Δ΄
    v.rect(8.95, 5.15, X18, W0, 0, (1, 1, 1), (0.93, 0.95, 0.90)); v.rect(X18, YN, XL, W0, 0, (1, 1, 1), PLATC); v.rect(9.40, W1, XL, YS, 0, (1, 1, 1), LIGHT)
    # σκυρόδεμα: Κ3 · Κ6 · ανατολικός τοίχος
    v.rect(9.40, yb, 9.70, 5.15, 1.3, BLACK, CONC); v.rect(11.05, 4.85, 13.35, YN, 1.3, BLACK, CONC); v.rect(XE, YN, 13.35, 7.85, 0.9, BLACK, WALLC)
    # τοίχοι Δ΄: διαμερίσματος 9,40–9,55 (κάτω από το πλατύσκαλο 17) και Τ6Α-02 ανάμεσα στο κοινόχρηστο και την ιδιωτική σκάλα (παρειά σκάλας 6,60)
    v.rect(9.55, 6.45, WXA, W1, 0.5, BLACK, WBLUE); v.rect(WXA, 6.45, WX, W1, 0.3, GRAY, WBLUE)
    # νότιος τοίχος σοφίτας (WS.02) πάνω από το πλατύσκαλο 17 · πεσσός 10,70–11,15
    v.rect(8.95, W0, 10.70, 6.35, 0.4, GRAY, (0.96, 0.96, 0.96)); v.rect(10.70, W0, WXA, 6.35, 0.6, BLACK, CONC)
    # δοκός Δ12.2 / τοίχος κουζίνας
    for y in (YS, 7.85): v.line((10.45, y), (XE, y), 0.8)
    v.line((9.40, YS), (10.45, YS), 0.3, GRAY, "[3 2] 0")
    # τοιχείο κλιμακοστασίου σοφίτας (από +16,05, πάνω από το 1ο πάτημα) – διακεκομμένο
    v.line((XL, 6.35), (XL, 7.25), 0.5, GRAY, "[4 2.5] 0"); v.line((WXA, 6.60), (WXA, 7.25), 0.5, GRAY, "[4 2.5] 0")
    arc(v, 11.50, 7.25, 0.60, 180, 90, 0.5, GRAY, "[4 2.5] 0"); arc(v, 11.50, 7.25, 0.35, 180, 90, 0.5, GRAY, "[4 2.5] 0")
    # ρίχτια
    for k, (a, b) in RISERS.items(): v.line(a, b, 0.85 if k in (1, 17, 18) else 0.55)
    v.line((XL, YN), (XL, W0), 0.85)
    # φανάρι
    v.rect(WXA, W0, WX, 6.45, 0.85, BLACK, (1, 1, 1)); v.line((WXA, 6.45), (WXA, W1), 0.85); v.line((WX, 6.45), (WX, W1), 0.85); v.line((WXA, W1), (WX, W1), 0.85)
    v.line((WXA, W0), (WXA, W0 - 0.0), 0.85); v.line((XL, W0), (WXA, W0), 0.85)
    # γραμμή ανάβασης
    sh.shape.draw_polyline([pymupdf.Point(v.X(x), v.Y(y)) for x, y in WALK.coords]); sh.shape.finish(width=0.45, color=BLUE, dashes="[6 2 1 2] 0", closePath=False)
    v.line((XL - 0.34, W1 + RW), (XL, W1 + RW), 0.45, BLUE); v.line((XL, W0 - RW), (X18 - 0.22, W0 - RW), 0.45, BLUE, "[6 2 1 2] 0")
    ax, ay = v.X(X18 - 0.24), v.Y(W0 - RW)
    sh.shape.draw_polyline([pymupdf.Point(ax, ay), pymupdf.Point(ax + 7, ay - 2.6), pymupdf.Point(ax + 7, ay + 2.6)]); sh.shape.finish(width=0.3, color=BLUE, fill=BLUE, closePath=True)
    sh.flush()
    # αρίθμηση (όπως A-10-4F / A-10-S: k πάνω στο πάτημα k) + στάθμες μπετού / τελικές
    def num(cx, cy, lab): sh.ocircle(v.X(cx), v.Y(cy), 5.6, 0.5, BLACK, (1, 1, 1)); sh.otext(v.X(cx), v.Y(cy) + 2.7, str(lab), size=7.6, bold=True, align="center")
    for k in range(1, 17):
        s = SPOS[k] + GOING[k] / 2; p = WALK.interpolate(s); q = WALK.interpolate(s + 0.02); q0 = WALK.interpolate(s - 0.02)
        tx, ty = q.x - q0.x, q.y - q0.y; L = math.hypot(tx, ty) or 1; nx, ny = ty / L, -tx / L
        if (p.x + nx - WX) ** 2 + (p.y + ny - YC) ** 2 < (p.x - nx - WX) ** 2 + (p.y - ny - YC) ** 2: nx, ny = -nx, -ny
        num(p.x, p.y, k)
        lx, ly = p.x + nx * 0.27, p.y + ny * 0.27
        sh.otext(v.X(lx), v.Y(ly) + 0.2, lv(SSL[k]), size=6.2, bold=True, color=RED, align="center", mask=True)
        sh.otext(v.X(lx), v.Y(ly) + 6.4, "(%s)" % lv(FFL[k]), size=5.4, color=FIN, align="center", mask=True)
    num(10.52, W0 - RW, 17); num(9.33, W0 - RW, 18)
    # πλατύσκαλο-σκαλί 17
    v.text(10.30, 5.25, "ΠΛΑΤΥΣΚΑΛΟ ΣΟΦΙΤΑΣ = ΣΚΑΛΙ 17", size=6.6, bold=True, align="center")
    v.text(10.30, 5.25, "πόρτα ασανσέρ ↑", size=5.6, dy=7.0, align="center", color=DOORC)
    level_mark(sh, v.X(9.78), v.Y(5.93), lv(SSL1) + " μπετό (πλάκα Π5)", 6.6, RED)
    v.text(9.80, 5.93, "τελικό %s · ξύλο κολλητό %s cm" % (lv3(FFL[17]), cm(T17)), size=5.8, bold=True, dy=7.0, color=FIN)
    v.text(9.33, 5.38, "ΣΟΦΙΤΑ", size=6.6, bold=True, align="center"); v.text(9.33, 5.38, "τελικό %s" % lv(FFL1), size=5.8, bold=True, dy=7.2, align="center", color=FIN)
    v.text(9.33, 5.38, "μπετό %s" % lv(SSL1), size=5.8, bold=True, dy=14.0, align="center", color=RED)
    v.text(9.33, 5.99, "γέμισμα %s cm · ξύλο" % cm(T_ATTIC, 0), size=5.4, align="center", color=GRAY)
    sh.otext(v.X(X18) - 2.4, v.Y(5.62) + 30, "ρίχτι 18 = ακμή γεμίσματος", size=5.2, rot=90, color=GRAY)
    # ξεκίνημα στον Δ΄
    v.text(10.15, 6.84, "Δ΄ ΟΡΟΦΟΣ – ΞΕΚΙΝΗΜΑ", size=7.0, bold=True, align="center"); v.text(10.15, 6.84, "μέσα στο διαμέρισμα Δ1", size=5.6, dy=7.2, align="center", color=GRAY)
    level_mark(sh, v.X(9.55), v.Y(7.42), lv(SSL0) + " μπετό", 7.0, RED); v.text(10.02, 7.42, "(τελικό %s)" % lv(FFL0), size=6.4, bold=True, dy=-6.6, color=FIN)
    v.text(10.15, 7.53, "γέμισμα %s cm (μελέτη: τελικό %s)" % (cm(FFL0 - SSL0, 0), lv(FFL0_STUDY)), size=5.4, align="center", color=GRAY)
    v.text(XL - 0.42, W1 + RW - 0.05, "ΑΝΟΔΟΣ", size=6.0, color=BLUE, align="center")
    v.text(10.33, 6.525 + 0.02, "τοίχος Δ΄ ορόφου (κοινόχρηστο ↑ | ιδιωτική σκάλα ↓)", size=4.6, align="center", color=GRAY)
    v.text(11.625, 6.30, "ΦΑΝΑΡΙ", size=6.4, bold=True, align="center"); v.text(11.625, 6.30, "%s × %s" % (mt(WX - WXA), mt(W1 - W0)), size=5.8, dy=7.0, align="center")
    v.text(9.80, 6.225 + 0.02, "νότιος τοίχος σοφίτας (WS.02)", size=4.8, align="center", color=GRAY)
    sh.otext(v.X(11.025) + 2.0, v.Y(7.02), "τοιχείο σοφίτας", size=4.8, rot=90, color=GRAY)
    v.text(9.55, 5.02, "Κ3", size=8.5, bold=True, align="center"); v.text(12.20, 4.975, "Κ6  230/25", size=8.5, bold=True, align="center", dy=3)
    sh.otext(v.X(13.225) + 2.6, v.Y(6.35) + 40, "τοίχος / Δ10.2 25/40", size=6.2, rot=90)
    v.text(11.90, 7.725, "Δ12.2  25/40", size=7.6, bold=True, align="center", dy=2.6)
    v.text(12.80, 7.50, "Π5  h=15", size=7.6, bold=True, align="center", mask=True)
    # πλάτος σκαλιών ΣΤΟ ΦΑΝΑΡΙ (cm)
    for k in range(1, 17):
        a, b = RISERS[k][0], RISERS[k + 1][0]
        if k in (2, 3, 4, 5): sh.otext(v.X((a[0] + b[0]) / 2), v.Y(W1) - 1.6, cm(b[0] - a[0]), size=6.0, bold=True, align="center")
        elif k in (12, 13, 14, 15): sh.otext(v.X((a[0] + b[0]) / 2), v.Y(W0) + 6.2, cm(a[0] - b[0]), size=6.0, bold=True, align="center")
        elif 6 <= k <= 11:
            xq = WX + 0.10; ya, yb_ = [r_[0][1] + (r_[1][1] - r_[0][1]) * (xq - r_[0][0]) / (r_[1][0] - r_[0][0]) for r_ in (RISERS[k], RISERS[k + 1])]
            sh.otext(v.X(xq), v.Y((ya + yb_) / 2) + 2.0, cm(abs(b[1] - a[1])), size=5.4, bold=True, align="center")
    # διαστάσεις
    sx = sorted(b[0] for k, (a, b) in RISERS.items() if abs(b[1] - YS) < 1e-9)
    nx_ = sorted(b[0] for k, (a, b) in RISERS.items() if abs(b[1] - YN) < 1e-9 and k != 18)
    ey = sorted(b[1] for a, b in RISERS.values() if abs(b[0] - XE) < 1e-9)
    v.hdim([X18] + nx_ + [XE, 13.35], yb, off=-13)
    v.hdim([X18, XL, WXA, WX, XE], yb, off=-27, vals=[mt(XL - X18) + " πλατύσκαλο", mt(WXA - XL), mt(WX - WXA) + " φανάρι", mt(XE - WX)])
    v.hdim([X18] + sx + [XE], 7.85, off=15, side=1)
    v.vdim([4.85, YN, W0, W1, YS, 7.85], 8.95, off=-10, tight=True)
    v.vdim([YN] + ey + [YS], 13.35, off=17, side=1)
    for x in sx: sh.oline(v.X(x), v.Y(7.85) + 2, v.X(x), v.Y(7.85) + 17, 0.2, GRAY)
    sh.oline(v.X(X18), v.Y(YS), v.X(X18), v.Y(7.85) + 17, 0.2, GRAY, "[1 1.5] 0")
    for y in ey: sh.oline(v.X(13.35) + 2, v.Y(y), v.X(13.35) + 19, v.Y(y), 0.2, GRAY)
    for y in (YN, W0, W1, YS): sh.oline(v.X(8.95) - 12, v.Y(y), v.X(9.40) - 1, v.Y(y), 0.2, GRAY, "[1 1.5] 0")
    sh.flush()


def info_a3(sh, x, y0, y1, scale_txt):
    sh.orect(x, y0, x + 40 * MM, y1, 0.9); xx = x + 2.4 * MM; y = y0 + 11 * MM
    sh.otext(xx, y, "Σ7β", size=26, bold=True); y += 8 * MM
    for ln in ("ΣΚΑΛΑ Δ΄ ΟΡΟΦΟΥ", "→ ΣΟΦΙΤΑΣ"): sh.otext(xx, y, ln, size=9.6, bold=True); y += 4.4 * MM
    sh.otext(xx, y + 1, "ιδιωτική της Δ1 · ΚΑΤΟΨΗ", size=7.0); y += 8 * MM
    sh.otext(xx, y, "ΚΛΙΜΑΚΑ", size=5.8, color=GRAY); y += 5.2 * MM; sh.otext(xx, y, scale_txt, size=13, bold=True); y += 3.6 * MM
    sh.otext(xx, y, "Α3 – εκτύπωση 100 %", size=5.8, color=GRAY); y += 3.2 * MM
    k = 1000.0 / float(scale_txt.split(":")[1].replace(",", ".")) * MM * 0.4
    yb = y + 2.2 * MM; sh.oline(xx, yb, xx + k, yb, 0.8)
    for i in range(0, 5): sh.oline(xx + k * i / 4, yb, xx + k * i / 4, yb - (5 if i in (0, 4) else 2.8), 0.4)
    sh.otext(xx, yb + 7.2, "0", size=5.6); sh.otext(xx + k / 2, yb + 7.2, "20", size=5.6, align="center"); sh.otext(xx + k, yb + 7.2, "40 cm", size=5.6, align="right")
    y = yb + 9 * MM; sh.oline(x, y - 4 * MM, x + 40 * MM, y - 4 * MM, 0.4)
    def blk(head, lines, color=BLACK):
        nonlocal y
        sh.otext(xx, y, head, size=7.0, bold=True, color=color); y += 3.5 * MM
        for ln in lines: sh.otext(xx, y, ln, size=6.5); y += 3.2 * MM
        y += 2.0 * MM
    blk("%d ΡΙΧΤΙΑ × %s cm" % (N, cm(RISE, 2)), ("χάραξη όπως η μελέτη", "ΠΑΤΗΜΑ %s ΠΑΝΤΟΥ" % cm(G), "κλάδοι / στροφή 1,00", "2υ + π = %s" % cm(2 * RISE + G)))
    blk("Δ΄ ΟΡΟΦΟΣ (κάτω)", ("ΤΕΛΙΚΟ %s · ΜΠΕΤΟ %s" % (lv(FFL0), lv(SSL0)), "γέμισμα %s cm" % cm(FFL0 - SSL0, 0)))
    blk("ΣΟΦΙΤΑ (πάνω)", ("ΤΕΛΙΚΟ %s · ΜΠΕΤΟ %s" % (lv(FFL1), lv(SSL1)), "γέμισμα %s cm" % cm(T_ATTIC, 0)))
    blk("ΠΛΑΤΥΣΚΑΛΟ = ΣΚΑΛΙ 17", ("πλάκα Π5 %s · τελικό %s" % (lv(SSL1), lv3(FFL[17])), "μένουν %s cm → ΞΥΛΙΝΟ δάπεδο" % cm(T17), "κολλητό στην πλάκα (σοφίτα:", "ξύλο, όχι πλακάκι)", "ίδια στάθμη το lobby ασανσέρ"), RED)
    blk("ΦΑΝΑΡΙ %s × %s" % (mt(WX - WXA), mt(W1 - W0)), ("μέσα / δίπλα: πλάτος κάθε", "σκαλιού στο φανάρι (cm)"))
    blk("ΚΟΚΚΙΝΟ", ("στάθμη ΜΠΕΤΟΥ πατήματος", "(τελικό − %s cm:" % cm(T_STEP), "μάρμαρο 3 + λάσπη 2)"), RED)
    blk("ΚΑΦΕ (σε παρένθεση)", ("ΤΕΛΙΚΗ στάθμη πατήματος",), FIN)
    blk("ΜΠΛΕ", ("γραμμή ανάβασης στη μέση", "του κλάδου · πάτημα %s cm" % cm(G)), BLUE)
    blk("ΜΕΤΩΠΑ ΚΑΛΟΥΠΙΟΥ", ("1ο %s · 2ο–16ο %s" % (cm(SSL[1] - SSL0), cm(RISE, 2)), "17ο %s (ως την πλάκα)" % cm(SSL1 - SSL[16]), "18ο: μέσα στο γέμισμα"))
    y = y1 - 18.5 * MM; sh.oline(x, y - 4.2 * MM, x + 40 * MM, y - 4.2 * MM, 0.4)
    for ln in ("ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12", "& ΑΓ. ΒΑΡΒΑΡΑΣ", "ΑΡΓΥΡΟΥΠΟΛΗ"): sh.otext(xx, y, ln, size=6.6, bold=True); y += 3.3 * MM
    sh.otext(xx, y + 1.2 * MM, "Βάση: Σ7_ΕΦ · A-10-4F · A-10-S", size=5.4, color=GRAY); sh.otext(xx, y + 4.2 * MM, "%s · %s" % (REV, DATE), size=5.8, color=GRAY)


def main():
    tmp = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=20, page_w=594, page_h=420, sx0=0, sy0=0)
    draw_plan(tmp); tmp.flush()
    bb = pymupdf.Rect()
    for d in tmp.page.get_drawings(): bb |= d["rect"]
    for r, _ in tmp.texts_out: bb |= r
    bb = bb + (-2, -2, 2, 2)
    PW, PH = 420 * MM, 297 * MM; m = 8 * MM; col = 40 * MM; gap = 3 * MM
    aw, ah = PW - 2 * m - col - gap, PH - 2 * m
    f = min(aw / bb.width, ah / bb.height)
    for sc in (10, 12.5, 15, 20):
        if 20.0 / sc <= f + 1e-6: f = 20.0 / sc; break
    scale_txt = "1:" + ("%g" % sc).replace(".", ",")
    sh = lib.Sheet({"region": (0, 0, 0, 0)}, [], scale=sc, page_w=420, page_h=297, sx0=0, sy0=0)
    w, h = bb.width * f, bb.height * f; x0 = m + (aw - w) / 2; y0 = m + (ah - h) / 2
    src = pymupdf.open("pdf", tmp.doc.tobytes())
    sh.page.show_pdf_page(pymupdf.Rect(x0, y0, x0 + w, y0 + h), src, 0, clip=bb)
    sh.shape = sh.page.new_shape()
    sh.orect(m - 2 * MM, m - 2 * MM, PW - m + 2 * MM, PH - m + 2 * MM, 0.6)
    info_a3(sh, PW - m - col, m, PH - m, scale_txt); sh.flush()
    path = os.path.join(OUT, NAME)
    sh.doc.set_metadata(dict(title="Σ7β – Ιδιωτική σκάλα Δ΄ ορόφου → σοφίτας, κάτοψη", author="ARKAD Ι.Κ.Ε."))
    sh.doc.save(path, garbage=4, deflate=True)
    print("->", NAME, "· κλίμακα", scale_txt)
    print("ρίχτι %.4f · πάτημα (cm):" % RISE, " ".join("%d:%.1f" % (k, GOING[k] * 100) for k in range(1, 17)))
    print("ρίχτια:", " ".join("%d:(%.3f,%.3f)-(%.3f,%.3f)" % (k, a[0], a[1], b[0], b[1]) for k, (a, b) in RISERS.items()))
    print("μπετό:", " ".join("%d:%+.3f" % (k, SSL[k]) for k in range(1, 18)), "· τελικό 17: %+.3f" % FFL[17])
    print("μέτωπα: 1ο %.1f · 17ο %.1f · επένδυση 17: %.1f cm" % ((SSL[1] - SSL0) * 100, (SSL1 - SSL[16]) * 100, T17 * 100))
    if len(sys.argv) > 1: pymupdf.open(path)[0].get_pixmap(dpi=int(sys.argv[2]) if len(sys.argv) > 2 else 110).save(sys.argv[1])


if __name__ == "__main__":
    main()
