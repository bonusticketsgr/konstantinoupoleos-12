"""Στιλ σχεδίασης αποχετεύσεων από το R16 (Γιάννης 10/11/2026: «πιο ωραίο σχέδιο, γραμμές, να φαίνεται πιο επαγγελματικό»).

Αρχές:
  · υπόβαθρο ΜΟΝΟΧΡΩΜΟ (γκρι τοίχοι, σκούρα υποστυλώματα, αχνά έπιπλα) από τα μοντέλα τοιχοποιιών του repo·
  · σωλήνες με πάχος γραμμής ανά διατομή, λευκό περίγραμμα (halo), βέλη ροής, ετικέτα διατομής πάνω στη γραμμή·
  · λίγα χρώματα: κόκκινο = λύματα · πορτοκαλί = ακάθαρτα · πράσινο διακεκομμένο = αερισμός · μπλε = όμβρια · καφέ = συλλεκτήρας·
  · σύμβολα: στήλη, πτώση, πατοσίφωνο, γραμμικό σιφώνι, κούτελο, υδρορροή, σιφώνι εξώστη, δοκός·
  · στις κατόψεις 1:60 αριθμημένες σημειώσεις (κύκλος) που εξηγούνται στη δεξιά στήλη· στις λεπτομέρειες 1:25 / 1:20 κείμενα με οδηγό.
Συντεταγμένες μοντέλου σε m (x ανατολή, y νότος)· αποστάσεις ετικετών σε pt (dx δεξιά, dy κάτω)."""
import sys, os, math, json
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toixopoiies")
sys.path.insert(0, REPO)
import b1_model as B, gf_model as G, s_model as S, f4_model as F, b_model as Y
import sheet_t01
from draw import View, new_canvas, frame_and_title, north_arrow, PAGE_W, PAGE_H, PT_PER_M_60, DARK
from reportlab.pdfbase.pdfmetrics import stringWidth as SW

C = None
REV, DATE = "R16", "10/11/2026"
SUB1 = ""
INK = (0.12, 0.13, 0.16); MUTE = (0.40, 0.41, 0.46); FAINT = (0.62, 0.63, 0.67)
SOIL = (0.74, 0.09, 0.11); WASTE = (0.90, 0.46, 0.02); VENT = (0.05, 0.52, 0.30); RAIN = (0.08, 0.36, 0.80)
MAIN = (0.42, 0.20, 0.06); BEAMC = (0.80, 0.50, 0.10); WARN = (0.80, 0.10, 0.10)
COL = {"soil": SOIL, "waste": WASTE, "vent": VENT, "rain": RAIN, "main": MAIN}
LW = {32: 0.8, 40: 0.9, 50: 1.25, 63: 1.45, 75: 1.75, 90: 2.2, 100: 2.6, 110: 2.6, 125: 3.3}
PANEL_X = 968                      # αριστερό όριο της δεξιάς στήλης (υπόμνημα / σημειώσεις)
PX, PW = PANEL_X + 12, PAGE_W - 20 - PANEL_X - 24
TOP, BOT = PAGE_H - 20, 92         # όρια χώρου σχεδίου (pt, y προς τα πάνω)


def mm_scale(den):
    return 72 / 25.4 * 1000 / den


def view(ox, oy, s, detail=False):
    v = View(C, ox, oy, s)
    v.detail = detail
    v.k = 1.55 if detail else 1.0          # πολλαπλασιαστής πάχους γραμμών
    v.t = 1.22 if detail else 1.0          # πολλαπλασιαστής κειμένων
    v.sym = 1.0 if detail else 1.30        # τα σύμβολα λίγο μεγαλύτερα στο 1:60 / 1:80
    return v


# ------------------------------------------------------------------ κείμενα (pt)
def ptext(X, Y, s, size=5.6, font="Inter-Medium", color=INK, anchor="l", rot=0, bg=True, pad=1.3):
    c = C; c.saveState(); c.translate(X, Y); c.rotate(rot)
    w = SW(s, font, size); off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
    if bg:
        c.setFillColorRGB(1, 1, 1); c.rect(off - pad, -size * 0.36 - pad, w + 2 * pad, size * 0.98 + 2 * pad, stroke=0, fill=1)
    c.setFont(font, size); c.setFillColorRGB(*color); c.drawString(off, -size * 0.36, s)
    c.restoreState()


def tag(v, x, y, s, color=INK, size=5.6, anchor="l", dx=0, dy=0, font="Inter-Medium", rot=0, bg=True):
    X, Y = v.p(x, y); ptext(X + dx, Y - dy, s, size * v.t, font, color, anchor, rot, bg)


def wrap(s, font, size, w):
    out, cur = [], ""
    for wd in s.split():
        t = (cur + " " + wd).strip()
        if SW(t, font, size) > w and cur:
            out.append(cur); cur = wd
        else:
            cur = t
    out.append(cur)
    return out


# ------------------------------------------------------------------ υπόβαθρο (μονόχρωμη κάτοψη από το μοντέλο τοιχοποιιών)
WALLF = (0.83, 0.83, 0.85); WALLS_ = (0.30, 0.31, 0.35); COLF = (0.36, 0.37, 0.42); FIX = (0.42, 0.44, 0.50)


def _toilet(v, pos, facing, col=FIX, lw=0.55):
    x, y = pos
    ux, uy = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}[facing]
    px, py = -uy, ux
    def P(a, b):
        return (x + ux * a + px * b, y + uy * a + py * b)
    v.poly([P(0, -0.20), P(0.15, -0.20), P(0.15, 0.20), P(0, 0.20)], stroke=col, lw=lw, fill=(1, 1, 1))
    cx, cy = P(0.42, 0)
    v.poly([P(0.15, -0.19), P(0.42, -0.19), P(0.42, 0.19), P(0.15, 0.19)], fill=(1, 1, 1))
    v.circle(cx, cy, 0.19, stroke=col, lw=lw, fill=(1, 1, 1))
    v.line(*P(0.15, -0.19), *P(0.42, -0.19), color=col, lw=lw); v.line(*P(0.15, 0.19), *P(0.42, 0.19), color=col, lw=lw)
    v.poly([P(0.16, -0.18), P(0.43, -0.18), P(0.43, 0.18), P(0.16, 0.18)], fill=(1, 1, 1))


def base(v, M, site=True, rooms=True, furniture=True, parking=False, clip=None):
    """Η κάτοψη ως υπόβαθρο: ό,τι δεν είναι δίκτυο σχεδιάζεται γκρι."""
    sheet_t01.M = M
    c = v.c
    for poly in M.FLOORS:
        v.poly(poly, fill=(0.965, 0.965, 0.96))
    if site:
        if clip:
            c.saveState(); cp = c.beginPath(); (ax, ay), (bx, by) = v.p(clip[0], clip[3]), v.p(clip[2], clip[1])
            cp.rect(ax, ay, bx - ax, by - ay); c.clipPath(cp, stroke=0, fill=0)
        sheet_t01.draw_site(v)
        if clip:
            c.restoreState()
    if furniture:
        for key, col, lw in [("(0.3, 0.3, 0.34)|0.60", (0.45, 0.45, 0.5), 0.5), ("(0.4, 0.4, 0.44)|0.70", (0.5, 0.5, 0.55), 0.5),
                             ("(0.55, 0.55, 0.58)|0.50", (0.6, 0.6, 0.64), 0.4), ("(0.1, 0.11, 0.13)|1.10", (0.3, 0.3, 0.34), 0.8),
                             ("(0.5, 0.62, 0.5)|0.40", (0.62, 0.66, 0.62), 0.35)]:
            sheet_t01.draw_strokes(v, key, col, lw)
        sheet_t01.draw_strokes(v, "(0.8, 0.8, 0.82)|0.30", (0.78, 0.78, 0.8), 0.3, masks=M.FURN_MASKS)
        sheet_t01.draw_strokes(v, "(0.72, 0.72, 0.75)|0.35", (0.72, 0.72, 0.75), 0.35, masks=M.FURN_MASKS)
        for wx0, wy0, wx1, wy1 in getattr(M, "FURN_WHITEOUT", []):
            v.rect(wx0, wy0, wx1, wy1, fill=(1, 1, 1))
        for ln in getattr(M, "EXTRA_LINES", []):
            (ax, ay), (bx, by) = ln[0], ln[1]
            v.line(ax, ay, bx, by, color=(0.72, 0.72, 0.75), lw=0.35)
        sheet_t01.draw_core(v)
        for item in getattr(M, "EQUIP", []):
            sheet_t01.equip(v, item, parking)
        for wd in M.WARDROBES:
            sheet_t01.wardrobe(v, wd["r"], washing=wd.get("washing", False), depth=wd["depth"], joinery=wd.get("joinery", False), poly=wd.get("poly"))
    # πέπλο: ό,τι προηγήθηκε γίνεται αχνό
    c.saveState(); c.setFillColorRGB(1, 1, 1); c.setFillAlpha(0.50); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1); c.restoreState()
    for poly in list(M.ETICS) + list(M.ETICS5):
        v.poly(poly, fill=(0.945, 0.945, 0.95), stroke=(0.66, 0.66, 0.70), lw=0.3)
    for poly in M.COLS2:               # στηθαία εξωστών: λεπτή λωρίδα 5 cm στην εξωτερική ακμή (γυάλινο στηθαίο)
        x0, y0, x1, y1 = M.bbox(poly)
        if (x1 - x0) >= (y1 - y0):
            yo = y0 if (y0 + y1) / 2 < 5.2 else y1
            v.rect(x0, yo if yo == y0 else yo - 0.05, x1, yo + 0.05 if yo == y0 else yo, fill=(0.45, 0.46, 0.50))
        else:
            xo = x0 if (x0 + x1) / 2 < 6.5 else x1
            v.rect(xo if xo == x0 else xo - 0.05, y0, xo + 0.05 if xo == x0 else xo, y1, fill=(0.45, 0.46, 0.50))
    for w in M.WALLS:
        v.poly(w["pts"], fill=WALLF, stroke=WALLS_, lw=0.45 * v.k)
    for poly in M.COLS:
        v.poly(poly, fill=COLF, stroke=INK, lw=0.5 * v.k)
    kinds = getattr(M, "WIN_KINDS", {})
    for i, poly in enumerate(M.WINS, 1):
        sheet_t01.draw_window(v, poly, kinds.get(i))
    for h, l, j in M.DOORS:
        v.door(h, l, j, arc=(h != j))
    for b in M.BATHS:
        v.rect(*b["counter"], stroke=FIX, lw=0.55 * v.k, fill=(1, 1, 1))
        x0, y0, x1, y1 = b["counter"]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        v.circle(cx, cy, 0.14, stroke=FIX, lw=0.45 * v.k)
        _toilet(v, *b["toilet"], lw=0.55 * v.k)
        if b.get("shower"):
            sx0, sy0, sx1, sy1 = b["shower"]
            for (ax, ay, bx, by) in [(sx0, sy0, sx1, sy0), (sx1, sy0, sx1, sy1), (sx1, sy1, sx0, sy1), (sx0, sy1, sx0, sy0)]:
                v.line(ax, ay, bx, by, color=FIX, lw=0.4 * v.k, dash=[2, 1.5])
            (gx0, gy0), (gx1, gy1) = b["screen"]
            v.line(gx0, gy0, gx1, gy1, color=(0.25, 0.40, 0.62), lw=1.2 * v.k)
    if rooms:
        for name, area, (x, y) in M.ROOMS:
            nm = name.split(" ≈")[0]
            v.text(x, y, nm, size=(5.4 if not v.detail else 7.5), font="Inter-SemiBold", color=FAINT)


# ------------------------------------------------------------------ σωλήνες
def _arrow(X, Y, ang, a, col):
    c = C; c.saveState(); c.translate(X, Y); c.rotate(ang)
    p = c.beginPath(); p.moveTo(a * 0.9, 0); p.lineTo(-a * 0.7, a * 0.62); p.lineTo(-a * 0.7, -a * 0.62); p.close()
    c.setFillColorRGB(*col); c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(0.45); c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def pipe(v, pts, kind, dia, dash=None, arrow=True, lab=None, seg=None, side=1, ov=False, halo=True, lsize=5.0, apos=0.55, lpos=0.5):
    """Σωλήνας. pts: σημεία με τη φορά ροής. lab: ετικέτα (π.χ. «Φ50») πάνω στο τμήμα seg (προεπιλογή το μακρύτερο)·
    ov=True → η ετικέτα φαίνεται και στην κάτοψη 1:60. dash: π.χ. [4, 2] για αγωγό σε άλλο επίπεδο."""
    c = v.c; col = COL.get(kind, kind); lw = LW[dia] * v.k
    P = [v.p(*q) for q in pts]
    def stroke(w, color, dsh):
        c.saveState(); c.setStrokeColorRGB(*color); c.setLineWidth(w); c.setLineCap(0 if dsh else 1); c.setLineJoin(1); c.setDash(dsh or [])
        p = c.beginPath(); p.moveTo(*P[0])
        for q in P[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0); c.restoreState()
    if halo:
        stroke(lw + 1.7 * v.k, (1, 1, 1), None)
    stroke(lw, col, [d * v.k for d in dash] if dash else None)
    segs = []
    for i in range(len(P) - 1):
        (x0, y0), (x1, y1) = P[i], P[i + 1]
        segs.append((math.hypot(x1 - x0, y1 - y0), i))
    if arrow:
        which = arrow if isinstance(arrow, (list, tuple)) else [i for L, i in segs if L >= 24 * v.k]
        for i in which:
            (x0, y0), (x1, y1) = P[i], P[i + 1]
            _arrow(x0 + (x1 - x0) * apos, y0 + (y1 - y0) * apos, math.degrees(math.atan2(y1 - y0, x1 - x0)), max(2.6 * v.k, lw * 1.25), col)
    if lab and (v.detail or ov):
        i = seg if seg is not None else max(segs)[1]
        (x0, y0), (x1, y1) = P[i], P[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        if ang > 90 or ang <= -90:
            ang += 180
        a = math.radians(ang); nx, ny = -math.sin(a), math.cos(a)
        d = (lw / 2 + 4.6 * v.t) * side
        ptext(x0 + (x1 - x0) * lpos + nx * d, y0 + (y1 - y0) * lpos + ny * d, lab, lsize * v.t, "Inter-SemiBold", col, "c", ang)


# ------------------------------------------------------------------ σύμβολα
def pill(X, Y, a, b, col, anchor="l", size=6.4):
    """Ετικέτα-κάψουλα [ΑΠ1 | Φ100]. (X, Y) = μέσο της αριστερής (anchor l) / δεξιάς (r) / κέντρο (c) πλευράς."""
    c = C
    wa = SW(a, "Inter-Bold", size) + 6.5; wb = (SW(b, "Inter-SemiBold", size - 0.7) + 6.5) if b else 0; h = size + 4.2
    x0 = {"l": X, "r": X - wa - wb, "c": X - (wa + wb) / 2}[anchor]; y0 = Y - h / 2
    c.saveState()
    c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(2.2); c.roundRect(x0, y0, wa + wb, h, 2.2, stroke=1, fill=1)
    c.setFillColorRGB(*col); c.setStrokeColorRGB(*col); c.setLineWidth(0.7); c.roundRect(x0, y0, wa + wb, h, 2.2, stroke=1, fill=1)
    if b:
        c.setFillColorRGB(1, 1, 1); c.roundRect(x0 + wa, y0 + 0.7, wb - 0.7, h - 1.4, 1.6, stroke=0, fill=1)
        c.rect(x0 + wa, y0 + 0.7, 2, h - 1.4, stroke=0, fill=1)
        c.setFont("Inter-SemiBold", size - 0.7); c.setFillColorRGB(*col); c.drawCentredString(x0 + wa + wb / 2, Y - (size - 0.7) * 0.36, b)
    c.setFont("Inter-Bold", size); c.setFillColorRGB(1, 1, 1); c.drawCentredString(x0 + wa / 2, Y - size * 0.36, a)
    c.restoreState()
    return x0, y0, x0 + wa + wb, y0 + h


def _leader(X, Y, TX, TY, col, lw=0.5):
    C.saveState(); C.setStrokeColorRGB(1, 1, 1); C.setLineWidth(lw + 1.2); C.line(X, Y, TX, TY)
    C.setStrokeColorRGB(*col); C.setLineWidth(lw); C.line(X, Y, TX, TY); C.restoreState()


def stack(v, x, y, name, dia, kind="soil", off=(10, -10), anchor="l", sub=None, hollow=False, r=None, size=6.4):
    """Κατακόρυφη στήλη: γεμάτος κύκλος + κάψουλα. hollow: η στήλη περνά / σταματά (κενός κύκλος)."""
    col = COL.get(kind, kind); X, Y = v.p(x, y); r = (r or 0.062) * v.sym
    if name:
        TX, TY = X + off[0], Y - off[1]
        _leader(X, Y, TX, TY, col)
    v.circle(x, y, r + 1.1 / v.s, fill=(1, 1, 1))
    v.circle(x, y, r, fill=(1, 1, 1) if hollow else col, stroke=col if hollow else INK, lw=(0.9 if hollow else 0.5) * v.k)
    if not hollow:
        v.circle(x, y, r * 0.38, fill=(1, 1, 1))
    if name:
        sz = size * (1.12 if v.detail else 1.0)
        x0, y0, x1, y1 = pill(TX, TY, name, ("Φ%s" % dia) if dia else None, col, anchor, sz)
        if sub:
            ptext(x0 if anchor != "r" else x1, y0 - 5.2 * v.t, sub, 4.9 * v.t, "Inter", MUTE, "l" if anchor != "r" else "r")


def drop(v, x, y, kind="soil", r=0.055):
    """Πτώση στον κάτω όροφο (κύκλος με Χ)."""
    col = COL.get(kind, kind); r *= v.sym
    v.circle(x, y, r + 0.9 / v.s, fill=(1, 1, 1))
    v.circle(x, y, r, fill=(1, 1, 1), stroke=col, lw=0.9 * v.k)
    d = r * 0.68
    v.line(x - d, y - d, x + d, y + d, color=col, lw=0.7 * v.k); v.line(x - d, y + d, x + d, y - d, color=col, lw=0.7 * v.k)


def trap(v, x, y, name=None, off=(8, -8), anchor="l"):
    """Πατοσίφωνο (σιφώνι δαπέδου) 15×15: τετράγωνο + κύκλος + σχάρα."""
    a = 0.075 * v.sym
    v.rect(x - a, y - a, x + a, y + a, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0 * v.k)
    v.rect(x - a, y - a, x + a, y + a, fill=(1, 1, 1), stroke=WASTE, lw=0.9 * v.k)
    v.circle(x, y, a * 0.62, stroke=WASTE, lw=0.6 * v.k)
    v.line(x - a * 0.62, y, x + a * 0.62, y, color=WASTE, lw=0.45 * v.k); v.line(x, y - a * 0.62, x, y + a * 0.62, color=WASTE, lw=0.45 * v.k)
    if name:
        tag(v, x, y, name, WASTE, 5.8, anchor, off[0], off[1], "Inter-Bold")


def linear(v, x0, y0, x1, y1, name=None, off=(6, 0), anchor="l", w=0.07):
    """Γραμμικό σιφώνι ντους: στενό ορθογώνιο με σχάρα."""
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux; h = w / 2 * (v.sym if not v.detail else 1.0)
    pts = [(x0 + nx * h, y0 + ny * h), (x1 + nx * h, y1 + ny * h), (x1 - nx * h, y1 - ny * h), (x0 - nx * h, y0 - ny * h)]
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0 * v.k)
    v.poly(pts, fill=(1, 1, 1), stroke=WASTE, lw=0.8 * v.k)
    n = max(3, int(L / 0.07))
    for i in range(1, n):
        t = L * i / n
        v.line(x0 + ux * t + nx * h, y0 + uy * t + ny * h, x0 + ux * t - nx * h, y0 + uy * t - ny * h, color=WASTE, lw=0.35 * v.k)
    if name:
        tag(v, (x0 + x1) / 2, (y0 + y1) / 2, name, WASTE, 5.8, anchor, off[0], off[1], "Inter-Bold")


def chase(v, x0, y0, x1, y1, sp=0.045):
    """Κούτελο (κλειστό κανάλι γυψοσανίδας / θερμοπρόσοψης γύρω από αγωγό)."""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    v.poly(pts, fill=(1, 1, 1))
    v.hatch(pts, sp if v.detail else sp * 1.4, 45, (0.45, 0.46, 0.5), 0.3 * v.k)
    v.poly(pts, stroke=INK, lw=0.9 * v.k)


def vent(v, x, y, name, off=(8, -8), anchor="l", dia="75", sub=None):
    """Απόληξη / άνοδος αερισμού."""
    stack(v, x, y, name, dia, "vent", off, anchor, sub, r=0.045, size=5.8)


def downpipe(v, x, y, name, off=(8, -8), anchor="l", dia="75", sub=None):
    stack(v, x, y, name, dia, "rain", off, anchor, sub, r=0.05, size=5.8)


def gully(v, x, y, to=None):
    """Σιφώνι ομβρίων εξώστη + πλευρική έξοδος προς την υδρορροή."""
    if to:
        pipe(v, [(x, y)] + to, "rain", 50, dash=[2.2, 1.4], arrow=False, halo=False)
    r = 0.075 * v.sym
    v.circle(x, y, r, stroke=RAIN, lw=0.8 * v.k, fill=(1, 1, 1))
    v.line(x - r * 0.6, y, x + r * 0.6, y, color=RAIN, lw=0.45 * v.k); v.line(x, y - r * 0.6, x, y + r * 0.6, color=RAIN, lw=0.45 * v.k)


def beam(v, r, name=None, lpos=None, rot=0):
    x0, y0, x1, y1 = r
    C.saveState(); C.setFillAlpha(0.13); v.rect(x0, y0, x1, y1, fill=BEAMC); C.restoreState()
    C.saveState(); C.setDash([3, 1.6]); v.rect(x0, y0, x1, y1, stroke=BEAMC, lw=0.55); C.restoreState()
    if name and lpos:
        v.text(lpos[0], lpos[1], name, size=4.8 * v.t, font="Inter-SemiBold", color=(0.62, 0.36, 0.02), rot=rot, bg=True)


def key(v, x, y, n, off=(14, -14), both=False):
    """Αριθμημένη σημείωση (μόνο στην κάτοψη 1:60· both=True και στη λεπτομέρεια): οδηγός + κύκλος με αριθμό."""
    if v.detail and not both:
        return
    X, Y = v.p(x, y); TX, TY = X + off[0], Y - off[1]
    _leader(X, Y, TX, TY, INK, 0.45)
    C.saveState(); C.setFillColorRGB(*INK); C.circle(X, Y, 1.1, stroke=0, fill=1)
    C.setStrokeColorRGB(1, 1, 1); C.setLineWidth(1.4); C.circle(TX, TY, 5.6, stroke=1, fill=1)
    C.setFont("Inter-Bold", 6.6); C.setFillColorRGB(1, 1, 1); C.drawCentredString(TX, TY - 2.35, str(n)); C.restoreState()


def call(v, x, y, off, lines, anchor="l", color=INK, always=False):
    """Κείμενο με οδηγό (μόνο στις λεπτομέρειες, εκτός αν always). lines: η πρώτη γραμμή έντονη."""
    if not v.detail and not always:
        return
    if isinstance(lines, str):
        lines = [lines]
    X, Y = v.p(x, y); TX, TY = X + off[0], Y - off[1]
    sz = 5.6 * v.t; lead = sz + 1.9
    _leader(X, Y, TX, TY, MUTE, 0.45)
    C.saveState(); C.setFillColorRGB(*MUTE); C.circle(X, Y, 1.2, stroke=0, fill=1); C.restoreState()
    tx = TX + (2.5 if anchor == "l" else -2.5)
    for i, ln in enumerate(lines):
        ptext(tx, TY - i * lead, ln, sz, "Inter-SemiBold" if i == 0 else "Inter", color if i == 0 else MUTE, anchor)


def level(v, x, y, s, color=MAIN, off=(6, 0), anchor="l"):
    """Στάθμη ροής (π.α.) με τριγωνάκι."""
    X, Y = v.p(x, y); X += off[0]; Y -= off[1]
    w = SW(s, "Inter-SemiBold", 5.4 * v.t)
    if anchor == "r":
        X -= w + 7
    C.saveState(); C.setFillColorRGB(1, 1, 1); C.rect(X - 1.5, Y - 3.6, w + 10, 7.4, stroke=0, fill=1)
    C.setFillColorRGB(*color); p = C.beginPath(); p.moveTo(X, Y + 2.4); p.lineTo(X + 5, Y + 2.4); p.lineTo(X + 2.5, Y - 2.0); p.close(); C.drawPath(p, stroke=0, fill=1)
    C.restoreState(); ptext(X + 7, Y, s, 5.4 * v.t, "Inter-SemiBold", color, "l", bg=False)


# ------------------------------------------------------------------ σελίδα
def begin_plan():
    C.saveState(); p = C.beginPath(); p.rect(20, BOT, PANEL_X - 20, TOP - BOT); C.clipPath(p, stroke=0, fill=0)


def end_plan():
    C.restoreState()


def view_title(s, scale, x=34, y=None):
    y = y or TOP - 22
    w = SW(s, "Inter-Bold", 11)
    C.setFillColorRGB(1, 1, 1); C.rect(x - 6, y - 10, w + 22 + SW(scale, "Inter-Medium", 8), 24, stroke=0, fill=1)
    C.setFont("Inter-Bold", 11); C.setFillColorRGB(*INK); C.drawString(x, y, s)
    C.setFont("Inter-Medium", 8); C.setFillColorRGB(*MUTE); C.drawString(x + w + 10, y, scale)
    C.setStrokeColorRGB(*INK); C.setLineWidth(1.2); C.line(x, y - 5, x + w, y - 5)


def scale_bar(den, x=34, y=BOT + 16, marks=(0, 1, 2, 5)):
    s = mm_scale(den); C.saveState(); C.setFillColorRGB(1, 1, 1); C.rect(x - 8, y - 5, marks[-1] * s + 26, 22, stroke=0, fill=1)
    C.setStrokeColorRGB(*INK); C.setLineWidth(0.6)
    for i in range(len(marks) - 1):
        a, b = x + marks[i] * s, x + marks[i + 1] * s
        C.setFillColorRGB(*(INK if i % 2 == 0 else (1, 1, 1))); C.rect(a, y, b - a, 3.2, stroke=1, fill=1)
    C.restoreState()
    for m_ in marks:
        ptext(x + m_ * s, y + 8.5, ("%d" % m_) + (" m" if m_ == marks[-1] else ""), 5.6, "Inter-Medium", INK, "c", bg=False)


def panel_rule():
    C.setStrokeColorRGB(*INK); C.setLineWidth(0.6); C.line(PANEL_X, BOT, PANEL_X, TOP)


def _head(y, s):
    C.setFillColorRGB(*INK); C.rect(PX - 4, y - 3.2, PW + 8, 11.5, stroke=0, fill=1)
    C.setFont("Inter-Bold", 7.2); C.setFillColorRGB(1, 1, 1); C.drawString(PX, y, s)
    return y - 15


LEG = {
    "soil": ("Λύματα: λεκάνη Φ90 · στήλη / αγωγός Φ100", lambda v: pipe(v, [(0, 0), (0.42, 0)], "soil", 100, arrow=[0], halo=False, apos=0.6)),
    "waste": ("Ακάθαρτα: Φ40 νιπτήρας · Φ50 ντους, νεροχύτης, πλυντήριο · Φ75 έξοδος πατοσίφωνου", lambda v: pipe(v, [(0, 0), (0.42, 0)], "waste", 50, arrow=[0], halo=False, apos=0.6)),
    "offs": ("Αγωγός στην οροφή του ορόφου (μετατόπιση στήλης 2×45°)", lambda v: pipe(v, [(0, 0), (0.42, 0)], "soil", 100, dash=[3, 1.6], arrow=False, halo=False)),
    "vent": ("Αερισμός ΚΑ Φ75 (βγαίνει έξω και ανεβαίνει στη θερμοπρόσοψη)", lambda v: pipe(v, [(0, 0), (0.42, 0)], "vent", 75, dash=[3, 1.6], arrow=False, halo=False)),
    "rain": ("Όμβρια: συλλεκτήρας / αγωγός", lambda v: pipe(v, [(0, 0), (0.42, 0)], "rain", 110, arrow=[0], halo=False, apos=0.6)),
    "rainhi": ("Συλλεκτήρας ομβρίων ΨΗΛΑ +3,30 (οροφή προβόλων Α΄)", lambda v: pipe(v, [(0, 0), (0.42, 0)], "rain", 110, dash=[5, 2], arrow=False, halo=False)),
    "main": ("Συλλεκτήρας / κλάδοι υπογείου, κρεμαστοί κάτω από τις δοκούς", lambda v: pipe(v, [(0, 0), (0.42, 0)], "main", 125, arrow=[0], halo=False, apos=0.6)),
    "stack": ("Κατακόρυφη στήλη λυμάτων ΑΠ", lambda v: stack(v, 0.21, 0, None, None)),
    "pass": ("Στήλη που περνά / σταματά (χωρίς σύνδεση στον όροφο)", lambda v: stack(v, 0.21, 0, None, None, hollow=True)),
    "drop": ("Πτώση στον κάτω όροφο", lambda v: drop(v, 0.21, 0)),
    "trap": ("Πατοσίφωνο ΠΣ (σιφώνι δαπέδου με σχάρα)", lambda v: trap(v, 0.21, 0)),
    "lin": ("Γραμμικό σιφώνι ντους ΓΣ → πατοσίφωνο", lambda v: linear(v, 0.02, 0, 0.40, 0)),
    "chase": ("Κούτελο (κλειστό κανάλι γύρω από αγωγό)", lambda v: chase(v, 0.06, -0.085, 0.36, 0.085)),
    "ventp": ("Άνοδος αερισμού στη θερμοπρόσοψη", lambda v: stack(v, 0.21, 0, None, None, "vent", r=0.045)),
    "dp": ("Υδρορροή ΥΔ Φ75 μέσα στη θερμοπρόσοψη", lambda v: stack(v, 0.21, 0, None, None, "rain", r=0.05)),
    "gully": ("Σιφώνι ομβρίων εξώστη, πλευρική έξοδος", lambda v: gully(v, 0.10, 0, [(0.40, 0)])),
    "beam": ("Δοκός (ξυλότυποι Σ2–Σ7) – ΚΑΜΙΑ οπή", lambda v: beam(v, (0.02, -0.07, 0.40, 0.07))),
    "key": ("Αριθμημένη σημείωση – βλ. ΣΗΜΕΙΩΣΕΙΣ", lambda v: key(v, 0.05, 0.05, 1, (9, -3))),
    "low": ("Χαμηλή ζώνη οροφής υπογείου – καμία σωλήνωση", None),
}


def legend(keys, y=TOP - 22):
    y = _head(y, "ΥΠΟΜΝΗΜΑ")
    for k in keys:
        txt, fn = LEG[k]
        lines = wrap(txt, "Inter", 6.3, PW - 30)
        yc = y + 2.2
        if fn:
            lv = view(PX, PAGE_H - yc, 52.0); lv.sym = 1.25
            fn(lv)
        else:
            C.saveState(); C.setFillAlpha(0.14); C.setFillColorRGB(*WARN); C.rect(PX + 1, yc - 4, 20, 8, stroke=0, fill=1); C.restoreState()
            C.setStrokeColorRGB(*WARN); C.setLineWidth(0.5); C.rect(PX + 1, yc - 4, 20, 8, stroke=1, fill=0)
        for j, ln in enumerate(lines):
            C.setFont("Inter", 6.3); C.setFillColorRGB(*INK); C.drawString(PX + 29, y - j * 7.5, ln)
        y -= max(1, len(lines)) * 7.5 + 5.4
    return y - 4


def notes(title, items, y, numbered=True, size=6.5):
    """Σημειώσεις στη δεξιά στήλη. numbered: κύκλοι με αριθμό (ίδιοι με τους κύκλους της κάτοψης)."""
    y = _head(y, title)
    lead = size + 1.55
    for i, it in enumerate(items, 1):
        bold = None
        if isinstance(it, tuple):
            bold, it = it
        lines = wrap(((bold + " ") if bold else "") + it, "Inter-SemiBold", size, PW - 15)
        if numbered:
            C.setFillColorRGB(*INK); C.circle(PX + 4.5, y + 2.1, 4.9, stroke=0, fill=1)
            C.setFont("Inter-Bold", 5.9); C.setFillColorRGB(1, 1, 1); C.drawCentredString(PX + 4.5, y + 0.05, str(i))
        else:
            C.setFillColorRGB(*INK); C.rect(PX + 2.5, y + 0.8, 3, 3, stroke=0, fill=1)
        for j, ln in enumerate(lines):
            x = PX + 14
            if j == 0 and bold:
                C.setFont("Inter-Bold", size); C.setFillColorRGB(*INK); C.drawString(x, y, bold)
                x += SW(bold + " ", "Inter-Bold", size); ln = ln[len(bold) + 1:]
            C.setFont("Inter", size); C.setFillColorRGB(*INK); C.drawString(x, y - j * lead, ln)
        y -= len(lines) * lead + 4.0
    return y - 5


def finish(sheet, theme, sub2, base_txt, scale):
    panel_rule()
    C.setFillColorRGB(1, 1, 1); C.rect(20, 20, PAGE_W - 40, 72, stroke=0, fill=1)
    frame_and_title(C, sheet, theme, SUB1, sub2, base_txt, scale, REV, DATE)
    north_arrow(C, PAGE_W - 42, BOT + 24, r=9)
    C.showPage()


# ------------------------------------------------------------------ παράθυρο λεπτομέρειας
def viewport(fn, box, px, py, den, title, code):
    """Σχεδιάζει το fn(v) για την περιοχή box = (x0, y0, x1, y1) του μοντέλου σε κλίμακα 1:den, με πάνω αριστερή γωνία (px, py από πάνω)."""
    s = mm_scale(den); mx0, my0, mx1, my1 = box
    w, h = (mx1 - mx0) * s, (my1 - my0) * s
    v = view(px - mx0 * s, py - my0 * s, s, detail=True)
    C.saveState(); p = C.beginPath(); p.rect(px, PAGE_H - py - h, w, h); C.clipPath(p, stroke=0, fill=0)
    fn(v)
    C.restoreState()
    C.setStrokeColorRGB(*INK); C.setLineWidth(0.9); C.rect(px, PAGE_H - py - h, w, h, stroke=1, fill=0)
    yb = PAGE_H - py - h - 17
    C.setFillColorRGB(*INK); C.circle(px + 9, yb + 3.4, 8.2, stroke=0, fill=1)
    C.setFont("Inter-Bold", 8.5); C.setFillColorRGB(1, 1, 1); C.drawCentredString(px + 9, yb + 0.4, code)
    C.setFont("Inter-Bold", 9.5); C.setFillColorRGB(*INK); C.drawString(px + 23, yb, title)
    tw = SW(title, "Inter-Bold", 9.5)
    C.setFont("Inter-Medium", 7.5); C.setFillColorRGB(*MUTE); C.drawString(px + 23 + tw + 8, yb, "Κλίμακα 1:%d" % den)
    return v
