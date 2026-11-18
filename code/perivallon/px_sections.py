# -*- coding: utf-8 -*-
"""Τομές περιβάλλοντος χώρου (ΠΧ-02 / ΠΧ-03) + λεπτομέρειες σκαλών. Κάθε τομή = λίστα στοιχείων (ρητά, από τις σταθερές του
μοντέλου): slab / wall / fill / soil / pav / stair / ground / level / dim / text / glass / louver / canopy. u = απόσταση κατά
μήκος της τομής (m, προς νότο ή ανατολή), z = στάθμη (m)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toixopoiies"))
import px_model as PM
from reportlab.pdfbase import pdfmetrics
from draw import PAGE_W, PAGE_H, DARK, GREY, frame_and_title

C_CONC = (0.80, 0.80, 0.83); C_NEW = (0.95, 0.72, 0.70); C_NEW_E = (0.80, 0.16, 0.14); C_S2 = (0.62, 0.62, 0.66)
C_FILL = (0.99, 0.90, 0.72); C_FILLH = (0.80, 0.48, 0.12); C_SOIL = (0.84, 0.91, 0.78); C_PAV = (0.88, 0.86, 0.80)
C_GROUND = (0.90, 0.88, 0.84); C_GLASS = (0.30, 0.45, 0.75); C_LOUV = (0.45, 0.22, 0.52)


def _f(v):
    return ("%+.2f" % v).replace(".", ",") if abs(v) > 0.004 else "±0,00"


class SV:
    """Όψη τομής: u προς τα δεξιά, z προς τα πάνω."""
    def __init__(self, c, X0, Y0, u0, z0, s):
        self.c, self.X0, self.Y0, self.u0, self.z0, self.s = c, X0, Y0, u0, z0, s

    def P(self, u, z):
        return self.X0 + (u - self.u0) * self.s, self.Y0 + (z - self.z0) * self.s

    def poly(self, pts, fill=None, stroke=None, lw=0.4, dash=None):
        c = self.c; p = c.beginPath(); p.moveTo(*self.P(*pts[0]))
        for q in pts[1:]:
            p.lineTo(*self.P(*q))
        p.close()
        if fill: c.setFillColorRGB(*fill)
        if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
        c.setDash(dash or [])
        c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill else 0); c.setDash([])

    def rect(self, u0, z0, u1, z1, **kw):
        self.poly([(u0, z0), (u1, z0), (u1, z1), (u0, z1)], **kw)

    def line(self, u0, z0, u1, z1, color=DARK, lw=0.5, dash=None):
        c = self.c; c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        c.line(*self.P(u0, z0), *self.P(u1, z1)); c.setDash([])

    def hatch(self, pts, spacing, angle, color, lw=0.3):
        c = self.c; c.saveState(); p = c.beginPath(); p.moveTo(*self.P(*pts[0]))
        for q in pts[1:]:
            p.lineTo(*self.P(*q))
        p.close(); c.clipPath(p, stroke=0, fill=0)
        us = [q[0] for q in pts]; zs = [q[1] for q in pts]
        u0, u1, z0, z1 = min(us), max(us), min(zs), max(zs)
        d = math.hypot(u1 - u0, z1 - z0); a = math.radians(angle); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        cu, cz = (u0 + u1) / 2, (z0 + z1) / 2
        c.setStrokeColorRGB(*color); c.setLineWidth(lw); k = -d
        while k <= d:
            pu, pz = cu + nx * k, cz + ny * k
            c.line(*self.P(pu - ux * d, pz - uy * d), *self.P(pu + ux * d, pz + uy * d)); k += spacing
        c.restoreState()

    def dots(self, pts, step, color, r=0.5):
        c = self.c; c.saveState(); p = c.beginPath(); p.moveTo(*self.P(*pts[0]))
        for q in pts[1:]:
            p.lineTo(*self.P(*q))
        p.close(); c.clipPath(p, stroke=0, fill=0)
        us = [q[0] for q in pts]; zs = [q[1] for q in pts]
        c.setFillColorRGB(*color)
        u = min(us); row = 0
        while u <= max(us):
            z = min(zs) + (step / 2 if row % 2 else 0)
            while z <= max(zs):
                X, Y = self.P(u, z); c.circle(X, Y, r, stroke=0, fill=1); z += step
            u += step; row += 1
        c.restoreState()

    def text(self, u, z, s, size=5, font="Inter", color=DARK, anchor="c", rot=0, bg=False, dz=0):
        c = self.c; X, Y = self.P(u, z); c.saveState(); c.translate(X, Y + dz); c.rotate(rot)
        c.setFont(font, size); c.setFillColorRGB(*color); w = pdfmetrics.stringWidth(s, font, size)
        off = {"c": -w / 2, "l": 0, "r": -w}[anchor]
        if bg:
            c.setFillColorRGB(1, 1, 1); c.rect(off - 1.5, -size * 0.35 - 1.5, w + 3, size + 2, stroke=0, fill=1); c.setFillColorRGB(*color)
        c.drawString(off, -size * 0.35, s); c.restoreState()

    # --- σύνθετα
    def level(self, u, z, txt=None, side=1, size=5.2, bold=True, col=DARK):
        """Σύμβολο στάθμης: τρίγωνο στο (u, z), κείμενο δεξιά (side +1) ή αριστερά."""
        X, Y = self.P(u, z); c = self.c; c.setFillColorRGB(*col); c.setStrokeColorRGB(*col); c.setLineWidth(0.5)
        p = c.beginPath(); p.moveTo(X, Y); p.lineTo(X - 3, Y + 5); p.lineTo(X + 3, Y + 5); p.close(); c.drawPath(p, stroke=1, fill=0)
        c.line(X - 9 if side < 0 else X, Y, X if side < 0 else X + 9, Y)
        c.setFont("Inter-Bold" if bold else "Inter", size); s = txt or _f(z)
        if side > 0:
            c.drawString(X + 4, Y + 6.5, s)
        else:
            c.drawRightString(X - 4, Y + 6.5, s)

    def vdim(self, u, z0, z1, txt=None, side=1, size=4.8):
        c = self.c; X, Y0 = self.P(u, z0); _, Y1 = self.P(u, z1)
        c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4); c.line(X, Y0, X, Y1)
        for Y in (Y0, Y1):
            c.line(X - 2.5, Y - 2.5, X + 2.5, Y + 2.5); c.line(X - 5, Y, X + 5, Y)
        c.saveState(); c.translate(X + (5 if side > 0 else -5), (Y0 + Y1) / 2); c.rotate(90); c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        s = txt or ("%.2f" % abs(z1 - z0)).replace(".", ",")
        c.drawCentredString(0, -size * 0.35 if side > 0 else size * 0.35 - size, s); c.restoreState()

    def hdim(self, u0, u1, z, txt=None, size=4.8, above=True):
        c = self.c; X0, Y = self.P(u0, z); X1, _ = self.P(u1, z)
        c.setStrokeColorRGB(*DARK); c.setLineWidth(0.4); c.line(X0, Y, X1, Y)
        for X in (X0, X1):
            c.line(X - 2.5, Y - 2.5, X + 2.5, Y + 2.5); c.line(X, Y - 5, X, Y + 5)
        c.setFont("Inter", size); c.setFillColorRGB(*DARK)
        s = txt or ("%.2f" % abs(u1 - u0)).replace(".", ",")
        c.drawCentredString((X0 + X1) / 2, Y + 2.5 if above else Y - size - 1, s)


# ------------------------------------------------------------------ στοιχειώδη σχέδια τομής
def slab(sv, u0, u1, ztop, h, label=None):
    pts = [(u0, ztop - h), (u1, ztop - h), (u1, ztop), (u0, ztop)]
    sv.poly(pts, fill=C_CONC, stroke=DARK, lw=0.5); sv.hatch(pts, 0.09, 45, (0.55, 0.55, 0.58), 0.25)
    if label:
        sv.text((u0 + u1) / 2, ztop - h / 2, label, size=4.6, color=(0.25, 0.25, 0.3), bg=True)


def conc(sv, u0, z0, u1, z1, new=False, s2=False, label=None, rot=90):
    pts = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    sv.poly(pts, fill=C_NEW if new else (C_S2 if s2 else C_CONC), stroke=C_NEW_E if new else DARK, lw=0.6 if new else 0.5)
    sv.hatch(pts, 0.08, 45 if not new else 135, (0.55, 0.55, 0.58) if not new else (0.75, 0.30, 0.28), 0.25)
    if label:
        sv.text((u0 + u1) / 2, (z0 + z1) / 2, label, size=4.6, font="Inter-SemiBold", color=C_NEW_E if new else (0.25, 0.25, 0.3), rot=rot, bg=True)


def fill(sv, u0, z0, u1, z1, label=None):
    pts = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    sv.poly(pts, fill=C_FILL, stroke=(0.6, 0.5, 0.35), lw=0.3); sv.dots(pts, 0.10, (0.75, 0.55, 0.30), 0.55)
    if label:
        sv.text((u0 + u1) / 2, (z0 + z1) / 2, label, size=4.8, font="Inter-SemiBold", color=(0.55, 0.30, 0.05), bg=True)


def soil(sv, u0, z0, u1, z1, label=None):
    pts = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    sv.poly(pts, fill=C_SOIL, stroke=(0.45, 0.6, 0.4), lw=0.3)
    if label:
        sv.text((u0 + u1) / 2, (z0 + z1) / 2, label, size=4.8, font="Inter-SemiBold", color=(0.2, 0.4, 0.2), bg=True)


def pav(sv, u0, z0, u1, z1):
    pts = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    sv.poly(pts, fill=C_PAV, stroke=DARK, lw=0.4)


def ground(sv, u0, u1, z, depth=0.6, label=None):
    """Πεζοδρόμιο / έδαφος γείτονα: γραμμή + διαγράμμιση εδάφους από κάτω."""
    pts = [(u0, z - depth), (u1, z - depth), (u1, z), (u0, z)]
    sv.poly(pts, fill=C_GROUND, stroke=None); sv.hatch(pts, 0.12, 45, (0.7, 0.68, 0.62), 0.25)
    sv.line(u0, z, u1, z, color=DARK, lw=1.0)
    if label:
        sv.text((u0 + u1) / 2, z - depth / 2, label, size=4.4, color=(0.35, 0.35, 0.38), bg=True)


def stair(sv, u_top, n, riser, tread, top, descend=+1, slab_z=None, fill_label="ΜΠΑΖΩΜΑ"):
    """Σκάλα που κατεβαίνει προς +u (descend=+1) από το (u_top, top). Μπάζωμα από slab_z ως κάτω από τα σκαλιά."""
    prof = [(u_top, top)]
    u, z = u_top, top
    for i in range(n):
        z -= riser; prof.append((u, z)); u += descend * tread; prof.append((u, z))
    if slab_z is not None:
        poly = prof + [(u, slab_z), (u_top, slab_z)]
        sv.poly(poly, fill=C_FILL, stroke=None); sv.dots(poly, 0.10, (0.75, 0.55, 0.30), 0.55)
        um = (u_top + u) / 2
        sv.text(um, slab_z + (top - riser * n - slab_z) * 0.45, fill_label, size=4.6, font="Inter-SemiBold", color=(0.55, 0.30, 0.05), bg=True)
    # σκαλιά: σκυρόδεμα 12 cm κάτω από το προφίλ + επένδυση 3 (μαρμάρινο σκαλοπάτι)
    off = [(pu, pz - 0.12) for pu, pz in prof]
    sv.poly(prof + off[::-1], fill=C_CONC, stroke=None); sv.hatch(prof + off[::-1], 0.08, 45, (0.55, 0.55, 0.58), 0.25)
    for a, b in zip(prof, prof[1:]):
        sv.line(a[0], a[1], b[0], b[1], color=DARK, lw=0.8)
    return prof


def glass(sv, u, z0, z1, label=None):
    sv.rect(u - 0.03, z0, u + 0.03, z1, fill=(0.85, 0.90, 0.97), stroke=C_GLASS, lw=0.5)
    if label:
        sv.text(u, (z0 + z1) / 2, label, size=4.4, color=C_GLASS, rot=90, bg=True, anchor="c")


def louver(sv, u0, u1, z0, z1, label="περσίδες αλουμ. 1,25 (A-80-02)"):
    sv.rect(u0, z0, u1, z1, fill=(0.93, 0.90, 0.95), stroke=C_LOUV, lw=0.5)
    z = z0 + 0.06
    while z < z1:
        sv.line(u0, z, u1, z, color=C_LOUV, lw=0.3); z += 0.115
    if label:
        sv.text(u1 + 0.08, (z0 + z1) / 2, label, size=4.2, color=C_LOUV, rot=90, anchor="c", bg=True)


def canopy(sv, u0, u1, z, label="στέγαστρο εσοχής +2,06 (A-80-02)"):
    sv.rect(u0, z, u1, z + 0.15, fill=(0.75, 0.72, 0.65), stroke=DARK, lw=0.5)
    if label:
        sv.text((u0 + u1) / 2, z + 0.26, label, size=4.2, color=(0.3, 0.3, 0.3), bg=True)


def bldg_floor(sv, u0, u1, ffl, label, slab_top=0.30, h=0.20):
    """Δάπεδο κτηρίου: πλάκα +0,30 (h20) + γέμισμα ως το τελικό."""
    slab(sv, u0, u1, slab_top, h)
    fill(sv, u0, slab_top, u1, ffl - 0.03)
    pav(sv, u0, ffl - 0.03, u1, ffl)
    sv.text((u0 + u1) / 2, ffl + 0.42, label, size=6.0, font="Inter-Bold", color=(0.25, 0.25, 0.3), bg=True)


# ------------------------------------------------------------------ οι τομές
def sec_A(sv):
    """Α-Α: x = 10,30 – είσοδος κτηρίου (χωλ +0,74 → πλατύσκαλο → ΣΚ-Α → διάδρομος −0,45 → πύλη Θ0.04 → πεζοδρόμιο −0,42)."""
    Z = PM.ZONE; H = PM.FFL_HALL
    bldg_floor(sv, 8.0, 9.15, H, "ΧΩΛ ΚΤΗΡΙΟΥ  +0,74")
    conc(sv, 9.15, -0.65, 9.45, 0.30, label="Δ4.3 30/95", rot=90)        # δοκός όψης
    conc(sv, 9.15, 3.10, 9.45, 3.28, label=None)                          # πρέκι / δοκός ορόφου (κόβεται)
    glass(sv, 9.30, H, 3.10, "ΘΥΡΑ ΕΙΣΟΔΟΥ Θ0.04 1,20 × 2,40")
    slab(sv, 9.45, 15.15, PM.SLE, 0.25, "Π19 h=25 (Σ2)  άνω −0,55")
    conc(sv, 15.15, -0.80, 15.45, PM.SLE, label=None)                     # νότιο τοιχείο υπογείου
    sv.text(15.30, -1.05, "τοιχείο 30", size=4.2, color=(0.3, 0.3, 0.35), rot=90)
    # θύλακας Γ
    z5 = Z["Ζ05"]
    fill(sv, 9.45, PM.SLE, 10.83, z5["fill_top"], "ΜΠΑΖΩΜΑ 1,01")
    conc(sv, 10.83, PM.SLE, 11.07, z5["fill_top"], s2=True, label="ΘΓ (Σ2)")
    slab(sv, 9.45, 11.07, z5["fill_top"] + PM.PSLAB, PM.PSLAB, None)
    sv.text(10.1, z5["fill_top"] + PM.PSLAB / 2, "πλάκα h18", size=4.0, color=(0.25, 0.25, 0.3), bg=True)
    pav(sv, 9.45, z5["fill_top"] + PM.PSLAB, 11.07, H)
    sv.text(10.26, H + 0.14, "ΠΛΑΤΥΣΚΑΛΟ +0,74", size=5.4, font="Inter-Bold", bg=True)
    # σκάλα
    s = PM.STAIRS[0]
    stair(sv, s["y_top"], s["n"], s["riser"], s["tread"], s["top"], +1, PM.SLE)
    sv.text(12.0, 0.95, "ΣΚ-Α  7 × 17,0 / 30", size=5.4, font="Inter-Bold", bg=True)
    # διάδρομος / πύλη / πεζοδρόμιο
    pav(sv, s["y_bot"], PM.SLE, 15.45, -0.45)
    sv.text(13.55, -0.20, "ΔΙΑΔΡΟΜΟΣ −0,45", size=4.8, font="Inter-SemiBold", bg=True)
    glass(sv, 14.35, -0.45, 1.85, "ΠΥΛΗ Θ0.04 1,20 × 2,30")
    canopy(sv, 14.10, 15.45, PM.LOBBY_TOP)
    ground(sv, 15.45, 16.7, PM.sw_south(10.30), 0.55, "πεζοδρόμιο")
    # κορυφή πλευρικών τοιχίων ΤΧ-26/27 (πίσω από το επίπεδο τομής)
    w = PM.WALL["ΤΧ-27"]
    prof = []
    for y0, y1, lv in w["top"]:
        prof += [(y0, lv), (y1, lv)]
    for a, b in zip(prof, prof[1:]):
        sv.line(a[0], a[1], b[0], b[1], color=C_NEW_E, lw=0.9, dash=[3, 2])
    sv.text(13.0, 0.62, "κορυφή ΤΧ-26 / ΤΧ-27: +0,74 → +0,57 → +0,40", size=4.4, color=C_NEW_E, bg=True)
    # στάθμες / διαστάσεις
    sv.level(8.6, H, side=-1)
    sv.level(14.05, -0.45, side=1); sv.level(16.2, PM.sw_south(10.30), "πεζοδρ. %s" % _f(PM.sw_south(10.30)), side=1)
    sv.text(11.8, 2.62, "ΔΟΜΗ ΠΛΑΤΥΣΚΑΛΟΥ: πλάκα Π19 −0,55 → ΜΠΑΖΩΜΑ ως +0,46 (1,01 m)", size=4.6, font="Inter-SemiBold", color=(0.45, 0.25, 0.05), bg=True)
    sv.text(11.8, 2.45, "→ πλάκα h18 (Σ2) ως +0,64 → επίστρωση 10 → +0,74 · διάδρομοι: επίστρωση 10 στην πλάκα", size=4.6, font="Inter-SemiBold", color=(0.45, 0.25, 0.05), bg=True)
    sv.hdim(9.45, 11.07, 1.30, "1,62"); sv.hdim(11.07, s["y_bot"], 1.30, "6 × 0,30 = 1,80"); sv.hdim(s["y_bot"], 14.45, 1.30, "1,58")
    sv.hdim(14.45, 15.45, 1.30, "1,00")
    sv.vdim(16.45, -0.45, H, "1,19 = 7 × 0,17", side=1)


def sec_B(sv):
    """Β-Β: x = 5,55 – είσοδος ΙΣ1 (ΙΣ1 +0,42 → βεράντα +0,40 → ΣΚ-Β → διάδρομος −0,30 → πύλη Θ0.02 → πεζοδρόμιο −0,29)."""
    Z = PM.ZONE
    bldg_floor(sv, 8.0, 9.15, PM.FFL_IS1, "ΙΣ1  +0,42")
    conc(sv, 9.15, -0.65, 9.45, 0.30, label="Δ4.3 30/95", rot=90)
    conc(sv, 9.15, 2.82, 9.45, 3.28, label=None)
    glass(sv, 9.30, PM.FFL_IS1, 2.82, "ΘΥΡΑ ΙΣ1 Θ0.03 1,10 × 2,40")
    slab(sv, 9.45, 15.15, PM.SLM, 0.20, "πλάκα h=20 (Σ2)  άνω −0,40")
    conc(sv, 15.15, -0.65, 15.45, PM.SLM, label=None)
    sv.text(15.30, -0.9, "τοιχείο 30", size=4.2, color=(0.3, 0.3, 0.35), rot=90)
    z3 = Z["Ζ03"]
    fill(sv, 9.45, PM.SLM, 11.10, z3["fill_top"], "ΜΠΑΖΩΜΑ 52")
    conc(sv, 11.10, PM.SLM, 11.35, z3["fill_top"], s2=True, label="ΘΑ (Σ2)")
    slab(sv, 9.45, 11.35, z3["fill_top"] + PM.PSLAB, PM.PSLAB, None)
    sv.text(10.2, z3["fill_top"] + PM.PSLAB / 2, "πλάκα h18", size=4.0, color=(0.25, 0.25, 0.3), bg=True)
    pav(sv, 9.45, z3["fill_top"] + PM.PSLAB, 11.35, PM.VER)
    sv.text(10.4, PM.VER + 0.14, "ΒΕΡΑΝΤΑ ΙΣ1 +0,40", size=5.4, font="Inter-Bold", bg=True)
    s = PM.STAIRS[1]
    stair(sv, s["y_top"], s["n"], s["riser"], s["tread"], s["top"], +1, PM.SLM)
    sv.text(12.1, 0.75, "ΣΚ-Β  4 × 17,5 / 30", size=5.4, font="Inter-Bold", bg=True)
    pav(sv, s["y_bot"], PM.SLM, 15.45, -0.30)
    sv.text(13.3, -0.06, "ΔΙΑΔΡΟΜΟΣ ΙΣ1 −0,30", size=4.8, font="Inter-SemiBold", bg=True)
    glass(sv, 14.35, -0.30, 1.90, "ΠΥΛΗ Θ0.02 1,20 × 2,40")
    canopy(sv, 14.10, 15.45, PM.LOBBY_TOP)
    ground(sv, 15.45, 16.7, PM.sw_south(5.55), 0.55, "πεζοδρόμιο")
    sv.line(11.35, PM.VER, 14.25, PM.VER, color=C_NEW_E, lw=0.9, dash=[3, 2])
    sv.text(13.0, 0.52, "κορυφή ΤΧ-23 / ΤΧ-24: +0,40", size=4.4, color=C_NEW_E, bg=True)
    sv.level(8.6, PM.FFL_IS1, side=-1)
    sv.level(14.05, -0.30, side=1); sv.level(16.2, PM.sw_south(5.55), "πεζοδρ. %s" % _f(PM.sw_south(5.55)), side=1)
    sv.text(11.8, 2.62, "ΔΟΜΗ ΒΕΡΑΝΤΑΣ (θύλακας Α): πλάκα −0,40 → ΜΠΑΖΩΜΑ ως +0,12 (0,52 m)", size=4.6, font="Inter-SemiBold", color=(0.45, 0.25, 0.05), bg=True)
    sv.text(11.8, 2.45, "→ πλάκα h18 (Σ2) ως +0,30 → επίστρωση 10 → +0,40 · διάδρομος: επίστρωση 10 στην πλάκα", size=4.6, font="Inter-SemiBold", color=(0.45, 0.25, 0.05), bg=True)
    sv.hdim(9.45, 11.35, 1.10, "1,90"); sv.hdim(11.35, s["y_bot"], 1.10, "3 × 0,30"); sv.hdim(s["y_bot"], 14.45, 1.10, "2,20"); sv.hdim(14.45, 15.45, 1.10, "1,00")
    sv.vdim(16.45, -0.30, PM.VER, "0,70 = 4 × 0,175", side=1)


def sec_ST(sv):
    """ΣΤ-ΣΤ: x = 2,00 – νότια βεράντα (Ζ02) → κράσπεδο → κήπος ΙΣ1 → περίφραξη Κωνσταντινουπόλεως → πεζοδρόμιο −0,20."""
    bldg_floor(sv, 8.5, 9.15, PM.FFL_IS1, "ΙΣ1  +0,42")
    conc(sv, 9.15, -0.20, 9.45, 3.40, label="Κ9 200/30", rot=90)
    slab(sv, 9.45, 15.15, PM.SL0, 0.20, "Π17 h=20 (Σ2)  άνω ±0,00")
    conc(sv, 15.15, -0.45, 15.45, PM.SL0, label=None)
    sv.text(15.30, -0.75, "τοιχείο 30", size=4.2, color=(0.3, 0.3, 0.35), rot=90)
    fill(sv, 9.55, PM.SL0, 11.35, 0.30, "ΜΠΑΖΩΜΑ 30")
    pav(sv, 9.55, 0.30, 11.35, PM.VER)
    sv.text(10.45, PM.VER + 0.14, "ΒΕΡΑΝΤΑ +0,40", size=5.4, font="Inter-Bold", bg=True)
    conc(sv, 11.35, PM.SL0, 11.50, PM.VER, new=True, label="ΤΧ-18")
    soil(sv, 11.50, PM.SL0, 15.25, PM.SOIL, "ΚΗΠΟΣ – χώμα 30 cm  +0,30")
    conc(sv, 15.25, PM.SL0, 15.45, PM.FENCE_BASE, new=True, label="ΤΧ-03")
    louver(sv, 15.29, 15.41, PM.FENCE_BASE, PM.FENCE_TOP)
    ground(sv, 15.45, 16.7, PM.sw_south(2.0), 0.55, "πεζοδρόμιο")
    sv.level(9.9, PM.VER, side=-1); sv.level(14.4, PM.SOIL, side=1); sv.level(15.0, PM.FENCE_BASE, "+0,81 βάση", side=-1, size=4.6)
    sv.level(15.0, PM.FENCE_TOP, "+2,06", side=-1, size=4.6); sv.level(16.2, PM.sw_south(2.0), "πεζοδρ. %s" % _f(PM.sw_south(2.0)), side=1)
    sv.hdim(9.55, 11.35, 0.95, "1,80"); sv.hdim(11.50, 15.25, 0.95, "3,75")
    sv.vdim(16.45, PM.sw_south(2.0), PM.FENCE_BASE, ("%.2f" % (PM.FENCE_BASE - PM.sw_south(2.0))).replace(".", ","), side=1)


def sec_G(sv):
    """Γ-Γ: y = 7,50 – Αγ. Βαρβάρας → περίφραξη → κήπος → κράσπεδο → δυτική βεράντα → ΙΣ1."""
    ground(sv, -6.6, -5.20, PM.sw_west(7.5), 0.55, "πεζοδρόμιο")
    conc(sv, -5.20, -0.60, -4.90, PM.SL0, label=None)
    sv.text(-5.05, -0.85, "τοιχείο 30", size=4.2, color=(0.3, 0.3, 0.35), rot=90)
    slab(sv, -4.90, 1.40, PM.SL0, 0.20, "Π16 h=20 (Σ2)  άνω ±0,00")
    conc(sv, -5.215, PM.SL0, -4.995, PM.FENCE_BASE, new=True, label="ΤΧ-01")
    louver(sv, -5.17, -5.05, PM.FENCE_BASE, PM.FENCE_TOP)
    soil(sv, -4.995, PM.SL0, -2.35, PM.SOIL, "ΚΗΠΟΣ – χώμα 30 cm  +0,30")
    conc(sv, -2.35, PM.SL0, -2.20, PM.VER, new=True, label="ΤΧ-16")
    fill(sv, -2.20, PM.SL0, 1.30, 0.30, "ΜΠΑΖΩΜΑ 30")
    pav(sv, -2.20, 0.30, 1.30, PM.VER)
    sv.text(-0.45, PM.VER + 0.14, "ΔΥΤΙΚΗ ΒΕΡΑΝΤΑ +0,40 (κλίση 1 % προς δύση)", size=5.2, font="Inter-Bold", bg=True)
    conc(sv, 1.40, -0.20, 1.65, 3.40, label="Τ1-07 / Κ", rot=90)
    sv.rect(1.30, PM.SL0, 1.40, 3.40, fill=(0.99, 0.93, 0.70), stroke=(0.55, 0.45, 0.20), lw=0.3)
    glass(sv, 1.52, PM.FFL_IS1, 2.82, "W0.01 3,50 × 2,40")
    bldg_floor(sv, 1.65, 2.6, PM.FFL_IS1, "ΙΣ1  +0,42")
    sv.level(-6.2, PM.sw_west(7.5), "πεζοδρ. %s" % _f(PM.sw_west(7.5)), side=1)
    sv.level(-4.8, PM.FENCE_BASE, "+0,81 βάση", side=1, size=4.6); sv.level(-4.8, PM.FENCE_TOP, "+2,06", side=1, size=4.6)
    sv.level(-4.6, PM.SOIL, side=1); sv.level(0.9, PM.VER, side=1)
    sv.hdim(-5.215, -4.995, 1.05, "0,22"); sv.hdim(-4.995, -2.35, 1.05, "2,65"); sv.hdim(-2.20, 1.30, 1.05, "3,50")
    sv.vdim(-6.4, PM.sw_west(7.5), PM.FENCE_BASE, ("%.2f" % (PM.FENCE_BASE - PM.sw_west(7.5))).replace(".", ","), side=-1)


def sec_D(sv):
    """Δ-Δ: y = 0,80 – Αγ. Βαρβάρας → γκαραζόπορτα Θ0.01 → θέση στάθμευσης Θ.Σ.Ι.1 +0,40 → λωρίδα → ΙΣ1."""
    ground(sv, -6.6, -5.20, PM.sw_west(0.8), 0.55, "πεζοδρόμιο")
    conc(sv, -5.20, -0.60, -4.90, PM.SL0, label=None)
    sv.text(-5.05, -0.85, "τοιχείο 30", size=4.2, color=(0.3, 0.3, 0.35), rot=90)
    slab(sv, -4.90, 0.80, PM.SL0, 0.25, "Π11 h=25 (Σ2)  άνω ±0,00")
    fill(sv, -5.20, PM.SL0, -0.10, 0.30, "ΜΠΑΖΩΜΑ 30")
    pav(sv, -5.20, 0.30, -0.10, PM.VER)
    sv.text(-2.6, PM.VER + 0.14, "Θ.Σ.Ι.1 +0,40 (βιομηχανικό δάπεδο 10)", size=5.2, font="Inter-Bold", bg=True)
    glass(sv, -5.10, PM.VER, 2.50, "ΓΚΑΡΑΖΟΠΟΡΤΑ Θ0.01 2,50 × 2,10 (συρόμενη)")
    canopy(sv, -5.60, -4.30, 2.56, "προστέγασμα +2,71 (A-80-03)")
    conc(sv, -0.10, PM.SL0, 0.05, PM.VER, new=True, label="ΤΧ-19")
    fill(sv, 0.05, PM.SL0, 0.70, 0.30); pav(sv, -0.10, 0.30, 0.70, PM.VER)
    sv.text(0.30, PM.VER + 0.14, "λωρίδα +0,40", size=4.6, font="Inter-SemiBold", bg=True)
    sv.rect(0.70, PM.SL0, 0.80, 3.40, fill=(0.99, 0.93, 0.70), stroke=(0.55, 0.45, 0.20), lw=0.3)
    conc(sv, 0.80, -0.25, 1.10, 3.40, label="Κ1 30/70", rot=90)
    bldg_floor(sv, 1.10, 1.8, PM.FFL_IS1, "ΙΣ1  +0,42")
    sv.level(-6.2, PM.sw_west(0.8), "πεζοδρ. %s" % _f(PM.sw_west(0.8)), side=1)
    sv.level(-1.1, PM.VER, side=1)
    sv.text(-2.6, -0.62, "κατώφλι γκαραζόπορτας +0,40 = πεζοδρόμιο +0,33 + 7 cm (ράμπα στο πεζοδρόμιο)", size=4.2, color=(0.3, 0.3, 0.35), bg=True)
    sv.hdim(-4.995, -0.10, 0.95, "4,90")


def sec_E(sv):
    """Ε-Ε: y = 1,50 – Υπν.2 → μπαλκονόπορτα W0.06 → ΒΑ βεράντα +0,40 → κήπος Β–ΒΑ +0,30 → ανατολική μάντρα +1,20 → γείτονας."""
    bldg_floor(sv, 8.4, 9.40, PM.FFL_IS1, "ΙΣ1 Υπν.2  +0,42")
    conc(sv, 9.40, -0.20, 9.70, 0.30, s2=True, label="Δ9.5 ανεστρ.", rot=0)
    sv.rect(9.70, PM.SL0, 9.80, 0.30, fill=(0.99, 0.93, 0.70), stroke=(0.55, 0.45, 0.20), lw=0.3)
    glass(sv, 9.55, PM.FFL_IS1, 2.82, "W0.06 1,00 × 2,40 μπαλκονόπορτα")
    conc(sv, 9.40, 2.82, 9.70, 3.40, label=None)
    slab(sv, 9.80, 16.67, PM.SL0, 0.20, "Π14 h=20 (Σ2)  άνω ±0,00")
    fill(sv, 9.80, PM.SL0, 11.05, 0.30, "ΜΠΑΖ. 30"); pav(sv, 9.80, 0.30, 11.05, PM.VER)
    sv.text(10.42, PM.VER + 0.14, "ΒΑ ΒΕΡΑΝΤΑ +0,40", size=5.0, font="Inter-Bold", bg=True)
    conc(sv, 11.05, PM.SL0, 11.20, PM.VER, new=True, label="ΤΧ-22")
    conc(sv, 11.20, PM.SL0, 11.50, 1.60, label="φρεάτιο Η/Μ", rot=90)
    soil(sv, 11.50, PM.SL0, 16.67, PM.SOIL, "ΚΗΠΟΣ Β–ΒΑ – χώμα 30 cm  +0,30")
    conc(sv, 16.67, -0.60, 16.92, PM.SL0, label=None)
    conc(sv, 16.67, PM.SL0, 16.92, PM.BOUNDARY_TOP, new=True, label="ΤΧ-13")
    ground(sv, 16.92, 17.9, PM.sw_east(1.5), 0.55, "γείτονας")
    sv.level(15.6, PM.SOIL, side=1); sv.level(16.4, PM.BOUNDARY_TOP, "+1,20 μάντρα", side=-1, size=4.6)
    sv.level(17.6, PM.sw_east(1.5), "≈ %s" % _f(PM.sw_east(1.5)), side=1, size=4.6)
    sv.hdim(9.80, 11.05, 0.85, "1,25"); sv.hdim(11.50, 16.67, 0.85, "5,17")


def det_stair(sv, s, slab_z, wall_ids):
    """Λεπτομέρεια σκάλας 1:25: προφίλ, μπάζωμα, στάθμες κάθε πατήματος, ρίχτι / πάτημα."""
    prof = stair(sv, s["y_top"], s["n"], s["riser"], s["tread"], s["top"], +1, slab_z)
    slab(sv, s["y_top"] - 0.4, s["y_bot"] + 0.9, slab_z, 0.20 if slab_z > -0.5 else 0.25, "πλάκα Σ2  άνω %s" % _f(slab_z))
    pav(sv, s["y_bot"], slab_z, s["y_bot"] + 0.9, s["bottom"])
    sv.level(s["y_bot"] + 0.6, s["bottom"], side=1)
    # πλατύσκαλο / βεράντα πάνω
    pav(sv, s["y_top"] - 0.4, s["top"] - PM.PAV, s["y_top"], s["top"])
    sv.level(s["y_top"] - 0.3, s["top"], side=-1)
    for i, lv in enumerate(s["levels"][:-1]):
        u = s["risers"][i] + s["tread"] / 2
        sv.text(u, lv + 0.06, _f(lv), size=4.2, font="Inter-Medium", color=(0.25, 0.25, 0.3))
    sv.hdim(s["y_top"], s["y_top"] + s["tread"], s["top"] + 0.35, ("%d" % round(s["tread"] * 100)) + " cm")
    sv.vdim(s["y_top"] - 0.15, s["top"] - s["riser"], s["top"], ("%.1f cm" % (s["riser"] * 100)).replace(".", ","), side=-1)
    sv.vdim(s["y_bot"] + 0.75, s["bottom"], s["top"], ("%.2f = %d × %.3f" % (s["top"] - s["bottom"], s["n"], s["riser"])).replace(".", ","), side=1)
    sv.text((s["y_top"] + s["y_bot"]) / 2, s["top"] + 0.62, "%s  –  %d ρίχτια × %s cm, πατήματα %d cm, πλάτος %s" % (
        s["id"], s["n"], ("%.1f" % (s["riser"] * 100)).replace(".", ","), round(s["tread"] * 100), ("%.2f" % (s["x1"] - s["x0"])).replace(".", ",")),
        size=5.6, font="Inter-Bold", bg=True)
    sv.text((s["y_top"] + s["y_bot"]) / 2, s["top"] + 0.48, "πλευρικά τοιχία %s · σκαλιά σκυροδέματος επί μπαζώματος, επένδυση μάρμαρο 3 + λάσπη 2" % wall_ids,
            size=4.4, color=(0.3, 0.3, 0.35), bg=True)


# ------------------------------------------------------------------ φύλλα
def _frame(sv_c, X, Y, Wd, Hd, title, sub):
    c = sv_c
    c.setStrokeColorRGB(*GREY); c.setLineWidth(0.4); c.rect(X, Y, Wd, Hd, stroke=1, fill=0)
    c.setFont("Inter-Bold", 9); c.setFillColorRGB(*DARK); c.drawString(X + 6, Y + Hd - 13, title)
    c.setFont("Inter", 6); c.setFillColorRGB(0.3, 0.3, 0.35); c.drawString(X + 6, Y + Hd - 23, sub)


def _place(c, fn, X, Y, Wd, Hd, u0, u1, z0, z1, s):
    """Τοποθέτηση τομής μέσα σε κελί: κλίπ στο κελί, αρχή κάτω-αριστερά."""
    c.saveState(); p = c.beginPath(); p.rect(X + 1, Y + 1, Wd - 2, Hd - 28); c.clipPath(p, stroke=0, fill=0)
    sv = SV(c, X + 14, Y + 14, u0, z0, s)
    fn(sv)
    c.restoreState()


S50 = 72 / 25.4 * 1000 / 50     # 56,69 pt/m
S25 = S50 * 2


def sheet_sections_1(c, sheet_no="ΠΧ-02"):
    W2 = (PAGE_W - 40 - 10) / 2
    top = PAGE_H - 24
    h1, h2 = 308, 272
    cells = [
        ("ΤΟΜΗ Α-Α  (x = 10,30 – είσοδος κτηρίου)  1:50", "χωλ +0,74 → πλατύσκαλο +0,74 (θύλακας Γ) → ΣΚ-Α 7 × 17,0 → διάδρομος −0,45 → πύλη Θ0.04 → πεζοδρόμιο",
         sec_A, 20, top - h1, W2, h1, 7.9, 16.7, -1.15, 3.3),
        ("ΤΟΜΗ Β-Β  (x = 5,55 – είσοδος ΙΣ1)  1:50", "ΙΣ1 +0,42 → βεράντα +0,40 (θύλακας Α) → ΣΚ-Β 4 × 17,5 → διάδρομος −0,30 → πύλη Θ0.02 → πεζοδρόμιο",
         sec_B, 30 + W2, top - h1, W2, h1, 7.9, 16.7, -1.15, 3.3),
        ("ΤΟΜΗ ΣΤ-ΣΤ  (x = 2,00 – νότια βεράντα, κήπος, περίφραξη)  1:50", "βεράντα +0,40 (μπάζωμα 30) → κράσπεδο ΤΧ-18 → κήπος +0,30 → ΤΧ-03 +0,81 + περσίδες → πεζοδρόμιο −0,20",
         sec_ST, 20, top - h1 - 10 - h2, W2, h2, 8.4, 16.7, -0.95, 2.95),
        ("ΤΟΜΗ Γ-Γ  (y = 7,50 – Αγ. Βαρβάρας, δυτική βεράντα)  1:50", "πεζοδρόμιο +0,13 → ΤΧ-01 +0,81 + περσίδες → κήπος +0,30 → ΤΧ-16 → βεράντα +0,40 (μπάζωμα 30) → ΙΣ1 +0,42",
         sec_G, 30 + W2, top - h1 - 10 - h2, W2, h2, -6.7, 2.6, -0.95, 2.95),
    ]
    for title, sub, fn, X, Y, Wd, Hd, u0, u1, z0, z1 in cells:
        _frame(c, X, Y, Wd, Hd, title, sub)
        _place(c, fn, X, Y, Wd, Hd, u0, u1, z0, z1, S50)
    frame_and_title(c, sheet_no, "ΠΕΡΙΒΑΛΛΩΝ ΧΩΡΟΣ – ΤΟΜΕΣ Α · Β · ΣΤ · Γ",
                    "Δομή δαπέδων (πλάκα Σ2 → μπάζωμα → πλάκα h18 → επίστρωση), τοιχία, σκάλες ανόδου", "Ίχνη τομών στην κάτοψη ΠΧ-01",
                    "Βάση: Σ2_ΕΦ · A-10-GF R01 · Α-30-ΑΑ/ΒΒ · Α-40 · A-80-02/03/04 · τοιχοποιίες ΙΣ R15", "ΚΛΙΜΑΚΑ 1:50 (A3)", PM.REV, PM.DATE)


def sheet_sections_2(c, sheet_no="ΠΧ-03"):
    W2 = (PAGE_W - 40 - 10) / 2
    top = PAGE_H - 24
    h1, h2 = 272, 334
    cells = [
        ("ΤΟΜΗ Δ-Δ  (y = 0,80 – Αγ. Βαρβάρας, θέση στάθμευσης Θ.Σ.Ι.1)  1:50", "πεζοδρόμιο +0,33 → γκαραζόπορτα → Θ.Σ.Ι.1 +0,40 (μπάζωμα 30 + βιομηχανικό δάπεδο) → λωρίδα +0,40 → ΙΣ1",
         sec_D, 20, top - h1, W2, h1, -6.7, 1.8, -0.95, 2.95),
        ("ΤΟΜΗ Ε-Ε  (y = 1,50 – ΒΑ βεράντα, κήπος Β–ΒΑ, ανατολικό όριο)  1:50", "ΙΣ1 +0,42 → W0.06 → ΒΑ βεράντα +0,40 (μπάζωμα 30) → κήπος +0,30 → μάντρα ΤΧ-13 +1,20 → γείτονας",
         sec_E, 30 + W2, top - h1, W2, h1, 8.3, 17.9, -0.95, 2.95),
    ]
    for title, sub, fn, X, Y, Wd, Hd, u0, u1, z0, z1 in cells:
        _frame(c, X, Y, Wd, Hd, title, sub)
        _place(c, fn, X, Y, Wd, Hd, u0, u1, z0, z1, S50)
    Y2 = top - h1 - 10 - h2
    sA, sB = PM.STAIRS
    _frame(c, 20, Y2, W2, h2, "ΛΕΠΤΟΜΕΡΕΙΑ ΣΚ-Α  (είσοδος κτηρίου)  1:25", "−0,45 → +0,74 · 7 ρίχτια × 17,0 cm · πατήματα 30 cm · πλάτος 2,45 (x 9,70–12,15)")
    _place(c, lambda sv: det_stair(sv, sA, PM.SLE, "ΤΧ-26 / ΤΧ-27"), 20, Y2, W2, h2, 10.6, 13.8, -1.0, 1.5, S25)
    _frame(c, 30 + W2, Y2, W2, h2, "ΛΕΠΤΟΜΕΡΕΙΑ ΣΚ-Β  (είσοδος ΙΣ1)  1:25", "−0,30 → +0,40 · 4 ρίχτια × 17,5 cm · πατήματα 30 cm · πλάτος 2,00 (x 4,50–6,50)")
    _place(c, lambda sv: det_stair(sv, sB, PM.SLM, "ΤΧ-23 / ΤΧ-24"), 30 + W2, Y2, W2, h2, 10.9, 13.3, -1.0, 1.5, S25)
    frame_and_title(c, sheet_no, "ΠΕΡΙΒΑΛΛΩΝ ΧΩΡΟΣ – ΤΟΜΕΣ Δ · Ε · ΣΚΑΛΕΣ",
                    "Θέση στάθμευσης, ΒΑ βεράντα, όρια · σκάλες ΣΚ-Α (7 × 17,0) και ΣΚ-Β (4 × 17,5)", "Ίχνη τομών στην κάτοψη ΠΧ-01",
                    "Βάση: Σ2_ΕΦ · A-10-GF R01 · Α-40 · A-80-03 · τοιχοποιίες ΙΣ R15", "ΚΛΙΜΑΚΑ 1:50 · 1:25 (A3)", PM.REV, PM.DATE)
