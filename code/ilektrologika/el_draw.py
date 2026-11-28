"""Σύμβολα και βοηθητικά σχεδίασης για τα ηλεκτρολογικά φύλλα (A3 οριζόντιο, 1:50).

Στιλ: το εγκεκριμένο στιλ των δικτύων (αποχετεύσεις R16+, `apoxeteuseis/apox_pro.py`): μονόχρωμο γκρι υπόβαθρο από το μοντέλο
τοιχοποιιών, χρωματιστό δίκτυο, υπόμνημα στη δεξιά στήλη, ΚΑΜΙΑ σημείωση πάνω στις κατόψεις (τα κείμενα στα φύλλα κειμένου και στο .md).

Συντεταγμένες μοντέλου σε m (x ανατολή, y νότος). Κάθε εντοιχισμένο σημείο έχει «d» = η πλευρά του χώρου προς την οποία βλέπει
(N / S / E / W = το σύμβολο προεξέχει προς βορρά / νότο / ανατολή / δύση από την παρειά του τοίχου)."""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "apoxeteuseis"))
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
sys.path.insert(0, os.path.join(HERE, "..", "anopseis"))
import apox_pro as P
from apox_pro import INK, MUTE, FAINT, PAGE_W, PAGE_H, SW, ptext, wrap

# ---------------------------------------------------------------- χρώματα ανά δίκτυο
PWR = (0.76, 0.10, 0.12)        # ρευματοδότες / ισχυρά
LGT = (0.86, 0.50, 0.02)        # φωτισμός
SWC = (0.08, 0.33, 0.70)        # διακόπτες / χειρισμοί
DAT = (0.02, 0.50, 0.42)        # data / ασθενή
FIR = (0.80, 0.05, 0.30)        # πυρανίχνευση
HVC = (0.47, 0.20, 0.72)        # κλιματισμός / αντλία θερμότητας
AUT = (0.05, 0.45, 0.58)        # θερμοστάτες / αυτοματισμοί
FEED = (0.10, 0.10, 0.12)       # κεντρική παροχή
BEAMC = (0.80, 0.50, 0.10)
VEC = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
S50 = 72 / 25.4 * 1000 / 50     # 56,693 pt/m


def C():
    return P.C


def _n(d):
    return VEC[d]


def _t(d):                       # εφαπτομενική (κατά μήκος του τοίχου)
    nx, ny = VEC[d]
    return (-ny, nx)


def halo_text(v, x, y, s, size=4.6, color=INK, font="Inter-SemiBold", anchor="c", rot=0, dx=0, dy=0, bg=True):
    X, Y = v.p(x, y)
    ptext(X + dx, Y - dy, s, size, font, color, anchor, rot, bg, pad=0.8)


# ---------------------------------------------------------------- ρευματοδότες
def socket(v, x, y, d, n=1, col=PWR, kind="std", lab=None, r=0.085, lab_off=None):
    """Ρευματοδότης σούκο στον τοίχο: ημικύκλιο πάνω στην παρειά + στέλεχος. n = πλήθος θέσεων (1/2/3) · kind: std · ip (στεγανός IP44/55) ·
    ded (αποκλειστική γραμμή συσκευής – γεμάτο) · hi (ψηλά, για συσκευή / A/C) · usb. lab: ετικέτα (π.χ. αριθμός κυκλώματος)."""
    c = v.c; nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    pts = []
    for i in range(0, 13):
        a = math.pi * i / 12
        pts.append((x + tx * r * math.cos(a) + nx * r * math.sin(a), y + ty * r * math.cos(a) + ny * r * math.sin(a)))
    fill = col if kind == "ded" else (1, 1, 1)
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0)
    v.poly(pts, fill=fill, stroke=col, lw=0.9)
    # στελέχη: ένα ανά θέση
    offs = {1: [0], 2: [-0.035, 0.035], 3: [-0.05, 0, 0.05], 4: [-0.06, -0.02, 0.02, 0.06]}[min(n, 4)]
    for o in offs:
        ax, ay = x + tx * o + nx * r, y + ty * o + ny * r
        v.line(ax, ay, ax + nx * r * 0.75, ay + ny * r * 0.75, color=col, lw=0.8)
    if kind == "ip":
        v.line(x - tx * r, y - ty * r, x + tx * r, y + ty * r, color=col, lw=1.6)
        v.circle(x + nx * r * 0.45, y + ny * r * 0.45, r * 0.22, fill=col)
    elif kind == "hi":
        v.line(x - tx * r * 0.55 + nx * r * 0.42, y - ty * r * 0.55 + ny * r * 0.42, x + tx * r * 0.55 + nx * r * 0.42, y + ty * r * 0.55 + ny * r * 0.42, color=col, lw=0.6)
    elif kind == "usb":
        v.circle(x + nx * r * 0.45, y + ny * r * 0.45, r * 0.2, stroke=col, lw=0.5)
    if lab:
        ox, oy = lab_off if lab_off else (nx * (r * 1.75 + 0.07), ny * (r * 1.75 + 0.07))
        halo_text(v, x + ox, y + oy, lab, size=4.3 * getattr(v, "t", 1.0), color=col)


def fixed_out(v, x, y, d, col=PWR, lab=None, r=0.07, lab_off=None):
    """Έξοδος καλωδίου / μόνιμη σύνδεση συσκευής (εστίες, A/C, θερμοσίφωνας, ρολό): γεμάτο τετράγωνο στον τοίχο."""
    nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    pts = [(x - tx * r, y - ty * r), (x + tx * r, y + ty * r), (x + tx * r + nx * 2 * r, y + ty * r + ny * 2 * r), (x - tx * r + nx * 2 * r, y - ty * r + ny * 2 * r)]
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0)
    v.poly(pts, fill=col, stroke=col, lw=0.6)
    if lab:
        ox, oy = lab_off if lab_off else (nx * (2 * r + 0.10), ny * (2 * r + 0.10))
        halo_text(v, x + ox, y + oy, lab, size=4.3 * getattr(v, "t", 1.0), color=col)


# ---------------------------------------------------------------- διακόπτες
def switch(v, x, y, d, kinds=("1",), col=SWC, lab=None, r=0.05, lab_off=None):
    """Διακόπτης / πλαίσιο διακοπτών στον τοίχο. kinds: ένα στοιχείο ανά πλήκτρο –
    "1" απλός · "2" αλέ-ρετούρ · "X" ενδιάμεσος · "D" dimmer (ροοστάτης) · "P" μπουτόν / πλήκτρο σκηνών · "R" ρολό (πάνω – κάτω) · "T" χρονοδιακόπτης."""
    nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    cx, cy = x + nx * (r + 0.015), y + ny * (r + 0.015)
    v.circle(cx, cy, r + 0.012, fill=(1, 1, 1))
    v.circle(cx, cy, r, fill=(1, 1, 1), stroke=col, lw=0.9)
    n = len(kinds)
    for i, k in enumerate(kinds):
        # κάθε πλήκτρο: μια «σημαία» που φεύγει από τον κύκλο λοξά προς τον χώρο
        ang = (i - (n - 1) / 2.0) * 0.55
        ux, uy = nx * math.cos(ang) + tx * math.sin(ang), ny * math.cos(ang) + ty * math.sin(ang)
        px, py = -uy, ux
        L = r * 2.3
        ax, ay = cx + ux * r, cy + uy * r
        bx, by = cx + ux * (r + L), cy + uy * (r + L)
        v.line(ax, ay, bx, by, color=col, lw=0.8)
        f = r * 0.9
        if k in ("1", "D", "T"):
            v.line(bx, by, bx + px * f, by + py * f, color=col, lw=0.8)
        if k in ("2", "X"):
            v.line(bx, by, bx + px * f, by + py * f, color=col, lw=0.8)
            v.line(ax, ay, ax - px * f, ay - py * f, color=col, lw=0.8)
        if k == "X":
            v.line(bx, by, bx - px * f, by - py * f, color=col, lw=0.8)
        if k == "D":
            v.circle(bx + px * f, by + py * f, r * 0.35, fill=col)
        if k == "P":
            v.circle(bx, by, r * 0.45, fill=(1, 1, 1), stroke=col, lw=0.7)
        if k == "R":
            v.poly([(bx + px * f, by + py * f), (bx - px * f, by - py * f), (bx + ux * f * 1.3, by + uy * f * 1.3)], fill=col)
        if k == "T":
            v.circle(bx + px * f, by + py * f, r * 0.4, stroke=col, lw=0.6, fill=(1, 1, 1))
    if lab:
        ox, oy = lab_off if lab_off else (nx * (r * 4.6 + 0.07) , ny * (r * 4.6 + 0.07))
        halo_text(v, x + ox, y + oy, lab, size=4.2 * getattr(v, "t", 1.0), color=col)


# ---------------------------------------------------------------- φωτιστικά
def spot(v, x, y, kind="s", col=LGT, r=0.062, lab=None, lab_off=(0.0, -0.13)):
    """Χωνευτό spot: s κανονικό · s44 IP44 (οριζόντια γραμμή) · s65 IP65 (Χ) · adj ρυθμιζόμενο (βέλος)."""
    r = r * getattr(v, "sym", 1.0)
    v.circle(x, y, r + 0.012, fill=(1, 1, 1))
    v.circle(x, y, r, fill=(1, 1, 1), stroke=col, lw=0.9)
    if kind == "s44":
        v.line(x - r, y, x + r, y, color=col, lw=0.8)
    elif kind == "s65":
        d = r * 0.7
        v.line(x - d, y - d, x + d, y + d, color=col, lw=0.8); v.line(x - d, y + d, x + d, y - d, color=col, lw=0.8)
    elif kind == "t":                                   # διπλό spot: ένα σώμα ≈ 0,34 × 0,17, δύο κεφαλές 36° ρυθμιζόμενες
        hx = 0.11 * getattr(v, "sym", 1.0)
        v.rect(x - hx - r, y - r, x + hx + r, y + r, fill=(1, 1, 1), stroke=col, lw=0.9)
        for sx in (-hx, hx):
            v.circle(x + sx, y, r * 0.72, fill=(1, 1, 1), stroke=col, lw=0.7)
            v.circle(x + sx, y, r * 0.30, fill=col)
    elif kind == "adj":
        v.circle(x, y, r * 0.30, fill=col)
        v.line(x + r * 0.45, y - r * 0.45, x + r * 1.45, y - r * 1.45, color=col, lw=0.8)
    else:
        v.circle(x, y, r * 0.33, fill=col)
    if lab:
        halo_text(v, x + lab_off[0], y + lab_off[1], lab, size=3.9 * getattr(v, "t", 1.0), color=col, font="Inter-Medium")


def pendant(v, x, y, col=LGT, r=0.10, lab=None, lab_off=(0.0, -0.19)):
    """Παροχή οροφής για κρεμαστό / διακοσμητικό φωτιστικό."""
    r = r * getattr(v, "sym", 1.0)
    v.circle(x, y, r + 0.012, fill=(1, 1, 1))
    v.circle(x, y, r, fill=(1, 1, 1), stroke=col, lw=1.0)
    v.circle(x, y, r * 0.55, stroke=col, lw=0.7)
    d = r * 0.39
    v.line(x - d, y - d, x + d, y + d, color=col, lw=0.7); v.line(x - d, y + d, x + d, y - d, color=col, lw=0.7)
    if lab:
        halo_text(v, x + lab_off[0], y + lab_off[1], lab, size=4.4 * getattr(v, "t", 1.0), color=col)


def wall_light(v, x, y, d, col=LGT, r=0.075, lab=None, kind="ap", lab_off=None):
    """Απλίκα / παροχή τοίχου (ap) · φωτιστικό καθρέπτη (mir) · στεγανό εξωτερικό (ext)."""
    nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    pts = []
    for i in range(0, 13):
        a = math.pi * i / 12
        pts.append((x + tx * r * math.cos(a) + nx * r * math.sin(a), y + ty * r * math.cos(a) + ny * r * math.sin(a)))
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0)
    v.poly(pts, fill=col if kind == "ext" else (1, 1, 1), stroke=col, lw=0.9)
    cx, cy = x + nx * r * 0.45, y + ny * r * 0.45; q = r * 0.3
    cc = (1, 1, 1) if kind == "ext" else col
    v.line(cx - q, cy - q, cx + q, cy + q, color=cc, lw=0.7); v.line(cx - q, cy + q, cx + q, cy - q, color=cc, lw=0.7)
    if kind == "mir":
        v.line(x - tx * r * 1.9, y - ty * r * 1.9, x + tx * r * 1.9, y + ty * r * 1.9, color=col, lw=1.6)
    if lab:
        ox, oy = lab_off if lab_off else (nx * (r + 0.11), ny * (r + 0.11))
        halo_text(v, x + ox, y + oy, lab, size=4.0 * getattr(v, "t", 1.0), color=col, font="Inter-Medium")


def led_line(v, a, b, col=LGT, lab=None, lab_off=(0, -0.10)):
    c = v.c; c.saveState(); c.setLineCap(1)
    v.line(a[0], a[1], b[0], b[1], color=(1, 1, 1), lw=3.0)
    v.line(a[0], a[1], b[0], b[1], color=col, lw=1.5, dash=[3.2, 1.8])
    c.restoreState()
    if lab:
        halo_text(v, (a[0] + b[0]) / 2 + lab_off[0], (a[1] + b[1]) / 2 + lab_off[1], lab, size=4.0 * getattr(v, "t", 1.0), color=col, font="Inter-Medium")


def track(v, a, b, heads=3, col=LGT, lab=None, lab_off=(0, -0.14), w=0.045):
    """Ράγα φωτισμού (μαγνητική 48 V, χωνευτή στην ψευδοροφή) με κινητές κεφαλές."""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; px, py = -uy, ux
    pts = [(a[0] + px * w, a[1] + py * w), (b[0] + px * w, b[1] + py * w), (b[0] - px * w, b[1] - py * w), (a[0] - px * w, a[1] - py * w)]
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.2)
    v.poly(pts, fill=(0.22, 0.22, 0.25), stroke=col, lw=0.8)
    for i in range(heads):
        t = L * (i + 0.5) / heads
        v.circle(a[0] + ux * t, a[1] + uy * t, w * 1.25, fill=col, stroke=(1, 1, 1), lw=0.5)
    if lab:
        halo_text(v, (a[0] + b[0]) / 2 + lab_off[0], (a[1] + b[1]) / 2 + lab_off[1], lab, size=4.2 * getattr(v, "t", 1.0), color=col)


# ---------------------------------------------------------------- πίνακας, κουτιά, οδεύσεις
def panel(v, r, col=FEED, lab=None, lab_off=(0.0, 0.0), anchor="c"):
    """Ηλεκτρικός πίνακας (χωνευτός): ορθογώνιο μισό γεμάτο."""
    x0, y0, x1, y1 = r
    v.rect(x0, y0, x1, y1, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.4)
    v.rect(x0, y0, x1, y1, fill=(1, 1, 1), stroke=col, lw=1.0)
    if (x1 - x0) < (y1 - y0):
        v.poly([(x0, y0), (x1, y0), (x0, y1)], fill=col)
    else:
        v.poly([(x0, y0), (x1, y0), (x0, y1)], fill=col)
    if lab:
        X, Y = v.p((x0 + x1) / 2 + lab_off[0], (y0 + y1) / 2 + lab_off[1])
        P.pill(X, Y, lab, None, col, anchor, 6.2 * getattr(v, "t", 1.0))


def cabinet(v, r, col=DAT, lab=None, lab_off=(0.0, 0.0), anchor="c", hatch=True):
    """Ερμάριο ασθενών / συλλέκτης / κέντρο καλωδίωσης: ορθογώνιο με διαγράμμιση."""
    x0, y0, x1, y1 = r
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.2)
    if hatch:
        v.hatch(pts, 0.05, 45, col, 0.35)
    v.poly(pts, stroke=col, lw=0.9)
    if lab:
        X, Y = v.p((x0 + x1) / 2 + lab_off[0], (y0 + y1) / 2 + lab_off[1])
        P.pill(X, Y, lab, None, col, anchor, 5.6 * getattr(v, "t", 1.0))


def jbox(v, x, y, col=INK, r=0.045):
    """Κουτί διακλάδωσης μέσα στο κενό της ψευδοροφής (επισκέψιμο από οπή φωτιστικού / θυρίδα)."""
    r = r * getattr(v, "sym", 1.0)
    v.rect(x - r, y - r, x + r, y + r, fill=(1, 1, 1), stroke=col, lw=0.8)
    v.line(x - r, y - r, x + r, y + r, color=col, lw=0.5)


def drop(v, x, y, col=INK, r=0.05, up=False):
    """Κατέβασμα (ή άνοδος) όδευσης μέσα σε τοίχο / τεχνική ζώνη: κύκλος με τελεία (κάτω) ή με σταυρό (πάνω)."""
    r = r * getattr(v, "sym", 1.0)
    v.circle(x, y, r + 0.012, fill=(1, 1, 1))
    v.circle(x, y, r, fill=(1, 1, 1), stroke=col, lw=0.9)
    if up:
        q = r * 0.6
        v.line(x - q, y, x + q, y, color=col, lw=0.7); v.line(x, y - q, x, y + q, color=col, lw=0.7)
    else:
        v.circle(x, y, r * 0.42, fill=col)


def route(v, pts, col=INK, lw=1.4, dash=None, halo=True, arrows=False, lab=None, seg=None, side=1, lsize=4.6):
    """Όδευση (δέσμη σωλήνων / καλώδιο): πολυγραμμή με λευκό περίγραμμα· dash για όδευση σε άλλο επίπεδο (π.χ. μέσα σε τοίχο / δάπεδο)."""
    c = v.c; Pp = [v.p(*q) for q in pts]
    def stroke(w, color, dsh):
        c.saveState(); c.setStrokeColorRGB(*color); c.setLineWidth(w); c.setLineCap(0 if dsh else 1); c.setLineJoin(1); c.setDash(dsh or [])
        p = c.beginPath(); p.moveTo(*Pp[0])
        for q in Pp[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0); c.restoreState()
    if halo:
        stroke(lw + 1.6, (1, 1, 1), None)
    stroke(lw, col, dash)
    segs = [(math.hypot(Pp[i + 1][0] - Pp[i][0], Pp[i + 1][1] - Pp[i][1]), i) for i in range(len(Pp) - 1)]
    if arrows:
        for L, i in segs:
            if L >= 26:
                (x0, y0), (x1, y1) = Pp[i], Pp[i + 1]
                P._arrow(x0 + (x1 - x0) * 0.55, y0 + (y1 - y0) * 0.55, math.degrees(math.atan2(y1 - y0, x1 - x0)), max(2.4, lw * 1.3), col)
    if lab:
        i = seg if seg is not None else max(segs)[1]
        (x0, y0), (x1, y1) = Pp[i], Pp[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        if ang > 90 or ang <= -90:
            ang += 180
        a = math.radians(ang); nx, ny = -math.sin(a), math.cos(a)
        dd = (lw / 2 + 4.4) * side
        ptext((x0 + x1) / 2 + nx * dd, (y0 + y1) / 2 + ny * dd, lab, lsize, "Inter-SemiBold", col, "c", ang, pad=0.8)


def pass_zone(v, r, col=BEAMC, lab=None, lab_at=None):
    """Πέρασμα καλωδίων κάτω από δοκό (μέσα σε τοίχο / έπιπλο): πλαίσιο με διαγράμμιση. lab_at = θέση της ετικέτας (με οδηγό)."""
    x0, y0, x1, y1 = r
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    C().saveState(); C().setFillAlpha(0.28); v.rect(x0, y0, x1, y1, fill=col); C().restoreState()
    v.hatch(pts, 0.05, 45, col, 0.4)
    v.rect(x0, y0, x1, y1, stroke=col, lw=1.1)
    if lab:
        lx, ly = lab_at if lab_at else ((x0 + x1) / 2, (y0 + y1) / 2)
        if lab_at:
            cx = min(max(lx, x0), x1); cy = min(max(ly, y0), y1)
            v.line(lx, ly, cx, cy, color=col, lw=0.7)
        X, Y = v.p(lx, ly)
        P.pill(X, Y, lab, None, col, "c", 6.4 * getattr(v, "t", 1.0))


def channel(v, r, col=(0.05, 0.50, 0.42)):
    """Κανάλι καλωδίων μέσα σε τοίχο (ο τοίχος παχαίνει): γεμάτη λωρίδα."""
    x0, y0, x1, y1 = r
    v.rect(x0, y0, x1, y1, fill=col, stroke=col, lw=0.4)


def dim_chain(v, a, b, txt, col=(0.30, 0.30, 0.34), size=3.9, side=1):
    """Μία διάσταση a → b (σημεία μοντέλου πάνω στη γραμμή διάστασης) με λοξές παύλες και την τιμή στη μέση."""
    (X0, Y0), (X1, Y1) = v.p(*a), v.p(*b)
    c = v.c; c.saveState(); c.setStrokeColorRGB(*col); c.setLineWidth(0.4)
    c.line(X0, Y0, X1, Y1)
    for X, Y in ((X0, Y0), (X1, Y1)):
        c.line(X - 1.6, Y - 1.6, X + 1.6, Y + 1.6)
    c.restoreState()
    ang = math.degrees(math.atan2(Y1 - Y0, X1 - X0))
    if ang > 90 or ang <= -90:
        ang += 180
    r_ = math.radians(ang); nx, ny = -math.sin(r_), math.cos(r_)
    ptext((X0 + X1) / 2 + nx * 3.4 * side, (Y0 + Y1) / 2 + ny * 3.4 * side, txt, size * getattr(v, "t", 1.0), "Inter-Medium", col, "c", ang, True, pad=0.5)


def zone(v, r, col, alpha=0.10, stroke=True, dash=(3, 1.6), lw=0.55):
    x0, y0, x1, y1 = r
    C().saveState(); C().setFillAlpha(alpha); v.rect(x0, y0, x1, y1, fill=col); C().restoreState()
    if stroke:
        C().saveState(); C().setDash(list(dash)); v.rect(x0, y0, x1, y1, stroke=col, lw=lw); C().restoreState()


def beam(v, r, name=None, lpos=None, rot=0):
    P.beam(v, r, name, lpos, rot)


# ---------------------------------------------------------------- ασθενή / πυρανίχνευση / αυτοματισμοί
def data_out(v, x, y, d, n=1, col=DAT, lab=None, r=0.085, kind="data", lab_off=None):
    """Λήψη δικτύου RJ45 (τρίγωνο στον τοίχο)· n = πλήθος θυρών. kind: data · tv (ομοαξονικό / δορυφορικό – τρίγωνο γεμάτο) · fo (οπτική ίνα)."""
    nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    pts = [(x - tx * r, y - ty * r), (x + tx * r, y + ty * r), (x + nx * r * 1.55, y + ny * r * 1.55)]
    v.poly(pts, fill=(1, 1, 1), stroke=(1, 1, 1), lw=2.0)
    v.poly(pts, fill=col if kind in ("tv", "fo") else (1, 1, 1), stroke=col, lw=0.9)
    if n > 1 and kind == "data":
        v.line(x + nx * r * 0.55 - tx * r * 0.4, y + ny * r * 0.55 - ty * r * 0.4, x + nx * r * 0.55 + tx * r * 0.4, y + ny * r * 0.55 + ty * r * 0.4, color=col, lw=0.7)
    if lab:
        ox, oy = lab_off if lab_off else (nx * (r * 1.55 + 0.10), ny * (r * 1.55 + 0.10))
        halo_text(v, x + ox, y + oy, lab, size=4.2 * getattr(v, "t", 1.0), color=col)


def ceil_dev(v, x, y, txt, col=DAT, r=0.10, lab=None, lab_off=(0, -0.19), fill=False):
    """Συσκευή οροφής: κύκλος με γράμματα (AP = access point · Κ = ανιχνευτής κίνησης · Σ = σειρήνα)."""
    r = r * getattr(v, "sym", 1.0)
    v.circle(x, y, r + 0.012, fill=(1, 1, 1))
    v.circle(x, y, r, fill=col if fill else (1, 1, 1), stroke=col, lw=1.0)
    halo_text(v, x, y, txt, size=4.0 * getattr(v, "t", 1.0), color=(1, 1, 1) if fill else col, font="Inter-Bold", bg=False)
    if lab:
        halo_text(v, x + lab_off[0], y + lab_off[1], lab, size=4.2 * getattr(v, "t", 1.0), color=col)


def wall_dev(v, x, y, d, txt, col=AUT, r=0.075, lab=None, fill=False, lab_off=None, off=0.0):
    """Συσκευή τοίχου: τετράγωνο με γράμμα (Θ = θερμοστάτης · ΘΤ = θυροτηλεόραση · Π = πληκτρολόγιο συναγερμού · Χ = χειριστήριο A/C).
    off > 0: το σύμβολο σχεδιάζεται πιο μέσα στον χώρο με στέλεχος ως τον τοίχο (συσκευή πάνω από άλλη στην ίδια κατακόρυφη)."""
    nx, ny = _n(d); tx, ty = _t(d); r = r * getattr(v, "sym", 1.0)
    cx, cy = x + nx * (r + off), y + ny * (r + off)
    if off:
        v.line(x, y, cx, cy, color=(1, 1, 1), lw=1.8); v.line(x, y, cx, cy, color=col, lw=0.7)
    v.rect(cx - r - 0.012, cy - r - 0.012, cx + r + 0.012, cy + r + 0.012, fill=(1, 1, 1))
    v.rect(cx - r, cy - r, cx + r, cy + r, fill=col if fill else (1, 1, 1), stroke=col, lw=0.9)
    halo_text(v, cx, cy, txt, size=(4.2 if len(txt) < 2 else 3.4) * getattr(v, "t", 1.0), color=(1, 1, 1) if fill else col, font="Inter-Bold", bg=False)
    if lab:
        ox, oy = lab_off if lab_off else (nx * (2 * r + off + 0.10), ny * (2 * r + off + 0.10))
        halo_text(v, x + ox, y + oy, lab, size=4.2 * getattr(v, "t", 1.0), color=col)


def detector(v, x, y, kind="smoke", col=FIR, r=0.085, lab=None, lab_off=(0, -0.17), ring=None):
    """Ανιχνευτής: τετράγωνο με Χ (καπνού) ή με τελεία (θερμοδιαφορικός)· ring = ακτίνα ελεύθερης ζώνης."""
    r = r * getattr(v, "sym", 1.0)
    if ring:
        C().saveState(); C().setDash([1.5, 1.5]); v.circle(x, y, ring, stroke=col, lw=0.35); C().restoreState()
    v.rect(x - r - 0.012, y - r - 0.012, x + r + 0.012, y + r + 0.012, fill=(1, 1, 1))
    v.rect(x - r, y - r, x + r, y + r, fill=(1, 1, 1), stroke=col, lw=1.0)
    if kind == "smoke":
        v.line(x - r, y - r, x + r, y + r, color=col, lw=0.8); v.line(x - r, y + r, x + r, y - r, color=col, lw=0.8)
    else:
        v.circle(x, y, r * 0.38, fill=col)
    if lab:
        halo_text(v, x + lab_off[0], y + lab_off[1], lab, size=4.4 * getattr(v, "t", 1.0), color=col)


def unit_rect(v, r, col=HVC, lab=None, dashed=False, alpha=0.18, lab_off=(0, 0), anchor="c", size=5.6):
    x0, y0, x1, y1 = r
    C().saveState(); C().setFillAlpha(alpha); v.rect(x0, y0, x1, y1, fill=col); C().restoreState()
    C().saveState()
    if dashed:
        C().setDash([2.6, 1.5])
    v.rect(x0, y0, x1, y1, stroke=col, lw=0.9); C().restoreState()
    if lab:
        X, Y = v.p((x0 + x1) / 2 + lab_off[0], (y0 + y1) / 2 + lab_off[1])
        P.pill(X, Y, lab, None, col, anchor, size * getattr(v, "t", 1.0))


def link(v, a, b, col=SWC, lw=0.45, dash=(1.2, 1.4), bend=0.12):
    """Λεπτή καμπύλη σύνδεσης διακόπτη → φωτιστικά που ελέγχει."""
    c = v.c; (X0, Y0), (X1, Y1) = v.p(*a), v.p(*b)
    mx, my = (X0 + X1) / 2, (Y0 + Y1) / 2; dx, dy = X1 - X0, Y1 - Y0
    cxp, cyp = mx - dy * bend, my + dx * bend
    c.saveState(); c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.setDash(list(dash))
    p = c.beginPath(); p.moveTo(X0, Y0); p.curveTo(cxp, cyp, cxp, cyp, X1, Y1); c.drawPath(p, stroke=1, fill=0); c.restoreState()


def tagpt(v, x, y, s, col=INK, size=4.6, off=(8, -8), anchor="l", leader=True, font="Inter-SemiBold"):
    """Ετικέτα με οδηγό (pt offsets: δεξιά, κάτω)."""
    X, Y = v.p(x, y); TX, TY = X + off[0], Y - off[1]
    if leader:
        P._leader(X, Y, TX, TY, col, 0.45)
    ptext(TX + (1.5 if anchor == "l" else -1.5 if anchor == "r" else 0), TY, s, size * getattr(v, "t", 1.0), font, col, anchor)


# ---------------------------------------------------------------- πίνακες κειμένου (φύλλα χωρίς κάτοψη)
def table(x, y, widths, rows, head=None, size=6.2, lead=None, pad=3.0, zebra=True, head_fill=INK, bold_first=False, aligns=None, min_h=None, colors=None):
    """Πίνακας με αναδίπλωση κειμένου. (x, y) = πάνω αριστερή γωνία σε pt (y από κάτω, όπως ο καμβάς). Επιστρέφει το y κάτω από τον πίνακα.
    rows: λίστες κειμένων · ένα κελί μπορεί να είναι (κείμενο, dict(font=, color=, fill=)). colors: {αριθμός γραμμής: χρώμα φόντου}."""
    c = C(); lead = lead or size + 1.7
    W = sum(widths)
    def cell_lines(txt, w, font):
        out = []
        for part in str(txt).split("\n"):
            out += wrap(part, font, size, w - 2 * pad) if part else [""]
        return out
    if head:
        hl = [cell_lines(h, w, "Inter-Bold") for h, w in zip(head, widths)]
        hh = max(len(l) for l in hl) * lead + 2 * pad - 1
        c.setFillColorRGB(*head_fill); c.rect(x, y - hh, W, hh, stroke=0, fill=1)
        xx = x
        for lines, w in zip(hl, widths):
            for j, ln in enumerate(lines):
                c.setFont("Inter-Bold", size); c.setFillColorRGB(1, 1, 1); c.drawString(xx + pad, y - pad - size * 0.80 - j * lead, ln)
            xx += w
        y -= hh
    for ri, row in enumerate(rows):
        cells = []
        for ci, (cell, w) in enumerate(zip(row, widths)):
            opt = {}
            if isinstance(cell, tuple):
                cell, opt = cell
            font = opt.get("font", "Inter-SemiBold" if (bold_first and ci == 0) else "Inter")
            cells.append((cell_lines(cell, w, font), font, opt))
        rh = max(len(l) for l, _, _ in cells) * lead + 2 * pad - 1.2
        if min_h:
            rh = max(rh, min_h)
        fill = (colors or {}).get(ri)
        if fill is None and zebra and ri % 2 == 1:
            fill = (0.955, 0.957, 0.965)
        if fill:
            c.setFillColorRGB(*fill); c.rect(x, y - rh, W, rh, stroke=0, fill=1)
        xx = x
        for ci, ((lines, font, opt), w) in enumerate(zip(cells, widths)):
            if opt.get("fill"):
                c.setFillColorRGB(*opt["fill"]); c.rect(xx, y - rh, w, rh, stroke=0, fill=1)
            al = (aligns or {}).get(ci, "l")
            for j, ln in enumerate(lines):
                c.setFont(font, size); c.setFillColorRGB(*opt.get("color", INK))
                yy = y - pad - size * 0.80 - j * lead
                if al == "r":
                    c.drawRightString(xx + w - pad, yy, ln)
                elif al == "c":
                    c.drawCentredString(xx + w / 2, yy, ln)
                else:
                    c.drawString(xx + pad, yy, ln)
            xx += w
        c.setStrokeColorRGB(0.78, 0.78, 0.81); c.setLineWidth(0.3); c.line(x, y - rh, x + W, y - rh)
        y -= rh
    return y


def heading(x, y, s, w=None, size=8.2, fill=INK):
    c = C(); w = w or SW(s, "Inter-Bold", size) + 12
    c.setFillColorRGB(*fill); c.rect(x, y - 4, w, size + 6.5, stroke=0, fill=1)
    c.setFont("Inter-Bold", size); c.setFillColorRGB(1, 1, 1); c.drawString(x + 5, y, s)
    return y - 10


def para(x, y, s, w, size=6.6, font="Inter", color=INK, lead=None, bold=None, bullet=None):
    """Παράγραφος με αναδίπλωση· bold = έντονη αρχή · bullet = κουκκίδα / αριθμός. Επιστρέφει το y της επόμενης γραμμής."""
    c = C(); lead = lead or size + 2.0
    ind = 0
    if bullet is not None:
        c.setFont("Inter-Bold", size); c.setFillColorRGB(*color); c.drawString(x, y, bullet)
        ind = max(9, SW(bullet + " ", "Inter-Bold", size) + 2)
    lines = wrap(((bold + " ") if bold else "") + s, font, size, w - ind)
    for j, ln in enumerate(lines):
        xx = x + ind
        if j == 0 and bold:
            c.setFont("Inter-Bold", size); c.setFillColorRGB(*color); c.drawString(xx, y, bold)
            xx += SW(bold + " ", "Inter-Bold", size); ln = ln[len(bold) + 1:]
        c.setFont(font, size); c.setFillColorRGB(*color); c.drawString(xx, y - j * lead, ln)
    return y - len(lines) * lead - 1.6
