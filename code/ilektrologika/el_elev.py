"""ΗΛ-15 ΟΨΕΙΣ ΤΟΙΧΩΝ ΚΑΤΩ ΑΠΟ ΔΟΚΑΡΙΑ: κάθε τοίχος όπως τον βλέπει ο ηλεκτρολόγος από μέσα στον χώρο – το δοκάρι από πάνω του, οι οπές, τα κουτιά στο ύψος τους
και το καλώδιο ΜΕΣΑ στον τοίχο (η ίδια διαδρομή 3D που ελέγχει το el_route). Τίποτα δεν δηλώνεται εδώ: τοίχοι, δοκάρια, κολόνες, πόρτες και διαδρομές διαβάζονται από τα μοντέλα."""
import math
import el_geom as G
import el_route as RT

M = W = A = None
S30 = 72 / 25.4 * 1000 / 30.0
ZA, ZB = -0.15, 2.98
CONC = (0.62, 0.62, 0.66); BEAMF = (0.44, 0.44, 0.50); WALLF = (0.955, 0.955, 0.965); BRICKF = (0.90, 0.80, 0.72); SCREEDF = (0.93, 0.91, 0.85)
CAB = (0.82, 0.08, 0.10); FURNC = (0.55, 0.25, 0.62); FLOORC = (0.55, 0.33, 0.08); HOLEC = (0.62, 0.10, 0.62); BLUE = (0.10, 0.36, 0.72)


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A
    RT.bind(model)


def _wall(wid):
    w = [q for q in W.WALLS if q["id"] == wid][0]
    return w["type"], W.bbox(w["pts"])


def elevation(x0, ybase, spec):
    """Σχεδιάζει μία όψη. spec: axis ("x" → ο τοίχος τρέχει Α–Δ) · c (συντεταγμένη του επιπέδου του) · a0, a1 · walls · front (η παρειά που βλέπουμε: N/S/E/W) · title · sub
    · rooms [(a0, a1, στάθμη οροφής, όνομα)] ο χώρος μπροστά · marks [(a, z, κείμενο, πλευρά)] · behind [(a0, a1, z1, όνομα)] έπιπλα / τοίχοι πίσω · infront το ίδιο για μπροστά."""
    import el_sheets as SH
    from el_det import Sec, txt, ln, box
    import el_draw as D
    ax = spec["axis"]; c0 = spec["c"]; a0, a1 = spec["a0"], spec["a1"]
    A_ = (lambda r: (r[0], r[2])) if ax == "x" else (lambda r: (r[1], r[3]))          # κατά μήκος
    C_ = (lambda r: (r[1], r[3])) if ax == "x" else (lambda r: (r[0], r[2]))          # κάθετα
    sc = Sec(x0, ybase, S30, a0, ZA)
    cv = SH.C()
    # πλάκες, γέμισμα
    sb = spec.get("slab", 2.78)
    sc.rect(a0, sb, a1, 2.98, fill=CONC, lw=0.4)
    sc.rect(a0, -M.SCREED - 0.08, a1, -M.SCREED, fill=CONC, lw=0.4)
    sc.rect(a0, -M.SCREED, a1, 0.0, fill=SCREEDF, lw=0.3)
    # έπιπλα / τοίχοι ΠΙΣΩ από τον τοίχο (διακεκομμένα)
    # τοίχοι του επιπέδου
    tops = {}
    for wid in spec["walls"]:
        typ, b = _wall(wid); q0, q1 = max(A_(b)[0], a0), min(A_(b)[1], a1)
        cuts = sorted(set([q0, q1] + [v for nm, br, zs in RT._C["beams"] for v in A_(br) if q0 < v < q1 and C_(br)[0] - 0.005 <= c0 <= C_(br)[1] + 0.005]))
        for u0, u1 in zip(cuts, cuts[1:]):
            um = (u0 + u1) / 2
            ov = [zs for nm, br, zs in RT._C["beams"] if A_(br)[0] - 1e-6 <= um <= A_(br)[1] + 1e-6 and C_(br)[0] - 0.005 <= c0 <= C_(br)[1] + 0.005]
            top = min(ov) if ov else sb
            sc.rect(u0, 0.0, u1, top, fill=BRICKF if typ in RT.BRICK else WALLF, lw=0.5)
        tops[wid] = (q0, q1)
    # υπέρθυρα θυρών πάνω στο επίπεδο
    for dr in RT._C["doors"]:
        if C_(dr)[0] - 0.01 <= c0 <= C_(dr)[1] + 0.01 and A_(dr)[1] > a0 and A_(dr)[0] < a1:
            u0, u1 = A_(dr)
            ov = [zs for nm, br, zs in RT._C["beams"] if A_(br)[0] - 1e-6 <= (u0 + u1) / 2 <= A_(br)[1] + 1e-6 and C_(br)[0] - 0.005 <= c0 <= C_(br)[1] + 0.005]
            sc.rect(u0, RT.DOOR_H - 0.05, u1, min(ov) if ov else sb, fill=WALLF, lw=0.5)
            sc.rect(u0, 0.0, u1, RT.DOOR_H - 0.05, fill=(1, 1, 1), lw=0.5)
            sc.line(u0, 0.0, u1, RT.DOOR_H - 0.05, col=SH.FAINT, lw=0.4); sc.line(u0, RT.DOOR_H - 0.05, u1, 0.0, col=SH.FAINT, lw=0.4)
            sc.text((u0 + u1) / 2, 1.20, "ΠΟΡΤΑ", size=5.4, font="Inter-Bold", color=SH.MUTE, anchor="c")
    for u0, u1, top, nm in spec.get("openings", []):
        sc.rect(u0, 0.0, u1, top, fill=(1, 1, 1), lw=0.5)
        sc.text((u0 + u1) / 2, 1.20, nm, size=5.2, font="Inter-Bold", color=SH.MUTE, anchor="c")
    # κολόνες στο επίπεδο
    for cb in RT._C["cols"]:
        if C_(cb)[0] - 0.005 <= c0 <= C_(cb)[1] + 0.005 and A_(cb)[1] > a0 and A_(cb)[0] < a1:
            u0, u1 = max(A_(cb)[0], a0), min(A_(cb)[1], a1)
            sc.rect(u0, 0.0, u1, sb, fill=BEAMF, lw=0.5)
            if u1 - u0 > 0.12:
                X, Y = sc.p((u0 + u1) / 2, 1.30); cv.saveState(); cv.translate(X, Y); cv.rotate(90); cv.setFont("Inter-Bold", 5.2); cv.setFillColorRGB(1, 1, 1); cv.drawCentredString(0, -2, "ΚΟΛΟΝΑ"); cv.restoreState()
    # δοκάρια πάνω από το επίπεδο
    for nm, br, zs in RT._C["beams"]:
        if C_(br)[0] - 0.005 <= c0 <= C_(br)[1] + 0.005 and A_(br)[1] > a0 and A_(br)[0] < a1:
            u0, u1 = max(A_(br)[0], a0), min(A_(br)[1], a1)
            sc.rect(u0, zs, u1, 2.98, fill=BEAMF, lw=0.6)
            sec = [b_[1] for b_ in A.BEAMS if b_[0] == nm][0]
            if u1 - u0 > 0.9:
                bl = spec.get("beam_lab", "l")
                sc.text(u0 + 0.12 if bl == "l" else (bl if isinstance(bl, float) else (u0 + u1) / 2), (zs + 2.98) / 2 - 0.03, "ΔΟΚΑΡΙ %s %s · κάτω παρειά +%s" % (nm, sec, G.fmt(zs)), size=5.6, font="Inter-Bold", color=(1, 1, 1),
                        anchor="l" if bl == "l" else "c")
            elif u1 - u0 > 0.2:
                sc.text((u0 + u1) / 2, (zs + 2.98) / 2 - 0.03, nm, size=4.6, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    # οπές
    for hid, hx, hy, horiz, br in RT._C["holes"]:
        ha = hx if ax == "x" else hy
        if C_(br)[0] - 0.005 <= c0 <= C_(br)[1] + 0.005 and a0 < ha < a1 and ((ax == "x") == horiz):
            X, Y = sc.p(ha, 2.73); r = M.HOLE_D / 2 * S30
            cv.saveState(); cv.setFillColorRGB(1, 1, 1); cv.setStrokeColorRGB(*HOLEC); cv.setLineWidth(1.1); cv.circle(X, Y, r, stroke=1, fill=1)
            cv.setFillColorRGB(*HOLEC); cv.circle(X, Y, r * 0.38, stroke=0, fill=1); cv.restoreState()
            txt(X, Y + r + 2.2, hid, size=4.8, font="Inter-Bold", color=(1, 1, 1), anchor="c")
    # οροφή του χώρου μπροστά
    for u0, u1, lv, nm in spec.get("rooms", []):
        sc.line(u0, lv, u1, lv, col=BLUE, lw=0.5, dash=[3, 1.5])
        Xc, Yc = sc.p(u1 - 0.04, lv + 0.035); SH.ptext(Xc, Yc, "οροφή %s +%s" % (nm, G.fmt(lv)), 4.4, "Inter-SemiBold", BLUE, "r", 0, True, pad=0.7)
    for fq in spec.get("furn", []):
        u0, u1, z0_, z1_, nm, front = fq[:6]
        sc.rect(u0, z0_, u1, z1_, fill=None, stroke=FURNC, lw=0.5, dash=[2.2, 1.4] if not front else None)
        if nm:
            la, lz = fq[6] if len(fq) > 6 else ((u0 + u1) / 2, (z0_ + z1_) / 2 - 0.02 if z1_ - z0_ > 1.2 else z0_ + 0.05)
            sc.text(la, lz, nm, size=4.4, color=FURNC, anchor="c")
    # καλώδια: τα τμήματα των διαδρομών που είναι μέσα στο επίπεδο του τοίχου
    B = RT.build(); tol = spec.get("tol", 0.08); devs = [d for d in B["devs"] if (d["wall"] in spec["walls"] and d["wall"] not in spec.get("nodev", ())) or d["id"] in spec.get("also", ()) or d["id"] in spec.get("paths", ())]
    paths = [(d["pts"], d["id"]) for d in devs] + [(e["pts"], e["id"]) for e in B["extra"] if e["id"] in spec.get("extra", ())]
    seen = set()
    for pts, pid in paths:
        for p, q in zip(pts, pts[1:]):
            m = p[3][0] if isinstance(p[3], (tuple, list)) else p[3]
            pa, pc = (p[0], p[1]) if ax == "x" else (p[1], p[0]); qa, qc = (q[0], q[1]) if ax == "x" else (q[1], q[0])
            inplane = abs(pc - c0) <= tol and abs(qc - c0) <= tol
            near = abs(pc - c0) <= spec.get("tolf", 0.0) and abs(qc - c0) <= spec.get("tolf", 0.0)
            if not (inplane and m in ("wall", "header", "brick", "floor")) and not (near and m in ("furn", "void") and spec.get("tolf")):
                continue
            if abs(pa - qa) < 1e-6 and abs(p[2] - q[2]) < 1e-6:
                continue
            if not (min(pa, qa) >= a0 - 1e-6 and max(pa, qa) <= a1 + 1e-6):
                continue
            key = (round(pa, 3), round(p[2], 3), round(qa, 3), round(q[2], 3))
            if key in seen or (key[2], key[3], key[0], key[1]) in seen:
                continue
            seen.add(key)
            if isinstance(p[3], (tuple, list)) and set(p[3]) == {"void", "furn"} and abs(pa - qa) < 1e-6 and spec.get("ceil_z"):
                zc = spec["ceil_z"]; zt_, zb_ = max(p[2], q[2]), min(p[2], q[2])
                for (za, zb2, mm) in ((zt_, max(zc, zb_), "void"), (min(zc, zt_), zb_, "furn")):
                    if za - zb2 < 1e-6:
                        continue
                    Xa, Ya = sc.p(pa, za); Xb, Yb = sc.p(pa, zb2)
                    cv.saveState(); cv.setLineCap(0 if mm == "void" else 1); cv.setStrokeColorRGB(1, 1, 1); cv.setLineWidth(2.6); cv.line(Xa, Ya, Xb, Yb)
                    cv.setStrokeColorRGB(*(CAB if mm == "void" else FURNC)); cv.setLineWidth(1.25)
                    if mm == "void":
                        cv.setDash([3, 1.6])
                    cv.line(Xa, Ya, Xb, Yb); cv.restoreState()
                continue
            col = FLOORC if m == "floor" else (FURNC if m == "furn" else CAB)
            X0_, Y0_ = sc.p(pa, p[2]); X1_, Y1_ = sc.p(qa, q[2])
            cv.saveState(); cv.setLineCap(0 if m == "void" else 1)
            cv.setStrokeColorRGB(1, 1, 1); cv.setLineWidth(2.6); cv.line(X0_, Y0_, X1_, Y1_)
            cv.setStrokeColorRGB(*col); cv.setLineWidth(1.25)
            if m == "void":
                cv.setDash([3, 1.6])
            cv.line(X0_, Y0_, X1_, Y1_); cv.restoreState()
    # κουτιά
    nrm = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    lab_off = spec.get("lab", {})
    for dev in RT.devices():
        pid, x, y, f, h, kind, opt = dev
        wid = G.face_of(W, x, y, f)[1]
        if (wid not in spec["walls"] or wid in spec.get("nodev", ())) and pid not in spec.get("also", ()):
            continue
        a = x if ax == "x" else y
        if not (a0 <= a <= a1):
            continue
        front = (f == spec["front"])
        X, Y = sc.p(a, h); r = 2.6
        col = D.SWC if kind == "διακόπτης" else (D.DAT if kind.startswith("λήψη") or kind in ("συσκευή τοίχου",) else (D.AUT if kind in ("θερμοστάτης", "χειριστήριο") else D.PWR))
        cv.saveState(); cv.setStrokeColorRGB(*col); cv.setLineWidth(0.9); cv.setFillColorRGB(*(col if front else (1, 1, 1)))
        cv.rect(X - r, Y - r, 2 * r, 2 * r, stroke=1, fill=1); cv.restoreState()
        dx, dy, an = lab_off.get(pid, (0, -1, "c"))
        txt(X + dx * 7.5, Y + (5.2 if dy < 0 else -8.6) if dx == 0 else Y - 1.8, pid, size=4.5, font="Inter-SemiBold", color=col, anchor=an)
    # σημάνσεις (από πού φτάνει το καλώδιο στο επίπεδο): (a, z, κείμενο, dx pt, dy pt, στοίχιση)
    for a, z, s, dx, dy, an in spec.get("marks", []):
        X, Y = sc.p(a, z)
        cv.saveState(); cv.setStrokeColorRGB(*CAB); cv.setFillColorRGB(1, 1, 1); cv.setLineWidth(1.1); cv.circle(X, Y, 3.6, stroke=1, fill=1); cv.setFillColorRGB(*CAB); cv.circle(X, Y, 1.3, stroke=0, fill=1); cv.restoreState()
        for i, l_ in enumerate(s.split("\n") if s else []):
            SH.ptext(X + dx, Y + dy - i * 6.0, l_, 4.8, "Inter-Bold", CAB, an, 0, True, pad=0.6)
    # στάθμες αριστερά
    for z, s in spec.get("levels", [(0.0, "±0,00 δάπεδο"), (M.ZR, "+2,30 καλώδια"), (2.48, "+2,48"), (2.98, "+2,98")]):
        X, Y = sc.p(a0, z); ln(X - 14, Y, X, Y, col=SH.MUTE, lw=0.4); txt(X - 15, Y - 1.8, s, size=4.6, color=SH.MUTE, anchor="r")
    for u0, u1, z, s in spec.get("dims", []):
        sc.dimh(u0, u1, z, s)
    for a, z, s in spec.get("notes", []):
        for i, l_ in enumerate(s.split("\n")):
            X, Y = sc.p(a, z); SH.ptext(X, Y - i * 6.0, l_, 4.8, "Inter-Bold", CAB, "l", 0, True, pad=0.6)
    # τίτλος
    Xt, Yt = sc.p(a0, ZB)
    txt(Xt, Yt + 27, spec["title"], size=7.4, font="Inter-Bold")
    txt(Xt, Yt + 18.5, spec["sub"], size=5.4, color=SH.MUTE)
    return sc


def specs():
    zr = M.ZR
    A1 = dict(axis="x", c=5.10, a0=1.52, a1=9.78, front="S", walls=["T2-04", "T2N-01", "T2-06"], slab=2.78,
              title="Α · ΒΟΡΕΙΟΣ ΤΟΙΧΟΣ ΣΑΛΟΝΙΟΥ (τοίχοι 8 · 9 · 10) – όπως φαίνεται από το σαλόνι", sub="όλος κάτω από το δοκάρι Δ3.1, περασιά · γεμάτο τετράγωνο = κουτί σε αυτή την πλευρά · άδειο = στην πίσω πλευρά (λουτρό γονέων, ντουλάπα χωλ, Υπν.2)",
              openings=[(5.449, 6.349, 2.48, "ΑΝΟΙΓΜΑ ΠΡΟΣ ΧΩΛ")],
              rooms=[(1.905, 8.30, 2.68, "σαλονιού"), (8.30, 9.40, 2.48, "λωρίδας")],
              furn=[(3.90, 5.349, 0.0, 2.44, "ντουλάπα χωλ – ΠΙΣΩ από τον τοίχο", False, (4.62, 0.78)), (3.30, 3.90, 0.0, 2.44, "πλυντήριο", False, (3.60, 0.78))],
              marks=[(M.XP, zr, "ΑΠΟ ΤΟΝ ΤΟΙΧΟ ΤΟΥ ΠΙΝΑΚΑ\n(κάθετος, πίσω από αυτόν – τομή 1)", 7, -9, "l"), (6.449, zr, "ΑΠΟ ΤΟΝ ΤΟΙΧΟ 4\n(χωλ | Υπν.2, πίσω)", -7, -9, "r"),
                     (1.78, -0.10, "πάτωμα 30 cm → τοίχος 15", 7, -1.8, "l"), (4.95, -0.10, "πάτωμα → τοίχος TV (14)", 7, -1.8, "l")],
              paths=("Δ17",), notes=[(4.62, 0.13, "Π02 · D2: από πίσω, μέσα από την τεχνική ντουλάπα του χωλ")],
              lab={"Π30": (1, 0, "l"), "ΚΘΡ1": (1, 0, "l"), "Π13": (1, 0, "l"), "Π14": (-1, 0, "r"), "D2": (1, 0, "l"), "Π02": (-1, 0, "r"), "Θ1": (-1, 0, "r"), "Χ1": (1, 0, "l"), "Θ3": (1, 0, "l"),
                   "Π41": (-1, 0, "r"), "Π03": (1, 0, "l"), "D5": (-1, 0, "r"), "TV3": (1, 0, "l"), "Π42": (-1, 0, "r"), "Δ2": (1, 0, "l"), "Π01": (1, 0, "l"), "Π43": (1, 0, "l")},
              dims=[(1.70, 4.80, 3.02, "3,10"), (4.80, 5.20, 3.02, "0,40"), (5.20, 8.60, 3.02, "3,40"), (8.60, 9.40, 3.02, "0,80")])
    B1 = dict(axis="y", c=9.475, a0=5.00, a1=9.30, front="W", walls=["T6A-03", "T6A-01"], slab=2.78, also=("ΦΑ1",),
              title="Β · ΤΟΙΧΟΣ ΕΙΣΟΔΟΥ (τοίχος 12) – από το σαλόνι", sub="κάτω από το δοκάρι Δ9.1, περασιά · άδειο τετράγωνο = στην πλευρά της σκάλας",
              openings=[(7.75, 9.15, 2.48, "ΑΝΟΙΓΜΑ ΚΟΥΖΙΝΑΣ")], rooms=[(5.15, 9.15, 2.48, "λωρίδας")], beam_lab=6.95,
              marks=[(7.675, zr, "ΑΠΟ ΤΟΝ ΤΟΙΧΟ ΤΗΣ ΚΟΥΖΙΝΑΣ\n(γυρίζει τη γωνία – όψη Γ)", 7, -9, "l")],
              lab={"ΘΤ": (-1, 0, "r"), "ΠΛ": (1, 0, "l"), "ΚΟ": (-1, 0, "r"), "Δ1": (1, 0, "l"), "ΦΕ": (0, 1, "c"), "ΦΑ1": (-1, 0, "r"), "Δ3": (-1, 0, "r"), "Π07": (1, 0, "l")},
              dims=[(5.15, 5.95, 3.02, "0,80"), (5.95, 7.95, 3.02, "2,00"), (7.95, 9.15, 3.02, "1,20")])
    C1 = dict(axis="x", c=7.675, a0=9.35, a1=13.42, front="S", walls=["T6A-01", "T6A-02", "T1-08"], nodev=("T6A-01",), paths=("Π07",), slab=2.83, tol=0.02, tolf=0.30, also=("Π50", "Π51", "Π52", "Π55"),
              title="Γ · ΤΟΙΧΟΣ ΚΟΥΖΙΝΑΣ – ΣΚΑΛΑΣ (τοίχος 11) – από την κουζίνα", sub="κάτω από το δοκάρι Δ12.2 · η οροφή της κουζίνας είναι 10 cm ΚΑΤΩ από το δοκάρι: εκεί περνά το καλώδιο",
              rooms=[(9.70, 13.10, 2.48, "κουζίνας")], beam_lab="c", ceil_z=2.4925,
              furn=[(10.45, 11.75, 0.0, 2.48, "στήλη ψυγείου – φούρνου", True, (11.10, 1.20)), (11.75, 13.10, 0.0, 0.90, "κάτω ντουλάπια", True, (12.10, 0.40)), (11.75, 13.10, 1.45, 2.48, "επάνω ντουλάπια", True, (12.80, 1.52))],
              marks=[(9.95, M.ZK, "", 0, 0, "c"), (11.95, M.ZK, "", 0, 0, "c"), (12.45, M.ZK, "", 0, 0, "c"), (9.475, zr, "→ τοίχος εισόδου\n(όψη Β)", 3, -11, "l")],
              notes=[(10.10, 2.36, "μπαίνει στον τοίχο ΚΑΤΩ από το δοκάρι,\nστο κενό των 10 cm πάνω από την οροφή")],
              lab={"Π50": (0, 1, "c"), "Π51": (-1, 0, "r"), "Π52": (1, 0, "l"), "Π55": (1, 0, "l"), "Π53": (1, 0, "l"), "Π54": (1, 0, "l")},
              levels=[(0.0, "±0,00"), (zr, "+2,30"), (2.48, "+2,48 οροφή"), (2.58, "+2,58 δοκάρι"), (2.98, "+2,98")])
    return A1, B1, C1


def sheet(no="ΗΛ-15"):
    import el_docs as DC
    import el_sheets as SH
    import el_draw as D
    from el_det import txt, ln
    y = DC.title("ΟΨΕΙΣ ΤΟΙΧΩΝ ΚΑΤΩ ΑΠΟ ΔΟΚΑΡΙΑ – ΠΟΥ ΠΕΡΝΑ ΤΟ ΚΑΛΩΔΙΟ", "κόκκινη γραμμή = καλώδιο ΜΕΣΑ στον τοίχο · πάντα κάτω από το δοκάρι · το δοκάρι το περνούν μόνο οι οπές Ø75 · 1:30")
    A1, B1, C1 = specs()
    h = (ZB - ZA) * S30
    yb1 = y - 30 - h
    elevation(DC.X0 + 62, yb1, A1)
    yb2 = yb1 - 42 - h
    assert yb2 + ZA * 0 >= DC.YB + 2, "ΗΛ-15: οι όψεις δεν χωρούν (%.0f)" % (yb2 - DC.YB)
    elevation(DC.X0 + 62, yb2, B1)
    xC = DC.X0 + 62 + (B1["a1"] - B1["a0"]) * S30 + 78
    elevation(xC, yb2, C1)
    # δεξιά στήλη: τι δείχνουν οι όψεις
    xr = DC.X0 + 62 + (A1["a1"] - A1["a0"]) * S30 + 26
    f = DC.Flow(xr, y - 6, DC.X1 - xr, size=6.2, name="ΗΛ-15")
    Bq = dict(bullet="•", size=6.2)
    f.h("Ο ΚΑΝΟΝΑΣ", fill=SH.CABLE)
    f.p("Σε τοίχο που είναι κάτω από δοκάρι το καλώδιο ΔΕΝ μπαίνει ποτέ από πάνω – από πάνω είναι μπετό.", **Bq)
    f.p("Κατεβαίνει σε διπλανό τοίχο που δεν έχει δοκάρι, ως το +2,30, και από εκεί τρέχει οριζόντια ΜΕΣΑ στον τοίχο, από τις τρύπες των ορθοστατών, 18 cm κάτω από το δοκάρι.", **Bq)
    f.p("Το +2,30 είναι η κανονική ζώνη οριζόντιας όδευσης (15–45 cm κάτω από την οροφή). Κατακόρυφα μόνο πάνω από το κουτί.", **Bq)
    f.h("ΟΨΗ Α – ΒΟΡΕΙΟΣ ΤΟΙΧΟΣ ΣΑΛΟΝΙΟΥ")
    f.p("Δυτικό κομμάτι (τοίχος 8): από τον πίνακα, μέσα στον τοίχο του, στο +2,30 → Π30, καθρέπτης, Π01. Στο άκρο κατεβαίνει ως το πάτωμα για τα 30 cm της ΒΔ γωνίας.", **Bq)
    f.p("Μεσαίο κομμάτι (τοίχος 9): οι πρίζες του καναπέ από πίσω, μέσα από την τεχνική ντουλάπα του χωλ.", **Bq)
    f.p("Ανατολικό κομμάτι (τοίχος 10): κάτω στον τοίχο χωλ | Υπν.2 και οριζόντια ως 2,7 m. Περίπου 10 καλώδια: μοιράζονται σε δύο σειρές τρυπών ή ανοίγονται επιπλέον τρύπες Ø25 στους ορθοστάτες.", **Bq)
    f.p("Οπές: ΟΠ5 παροχή + ασθενή · ΟΠ1 ισχυρά · ΟΠ2 αποχέτευση + ψυκτικά κλιματιστικού.", **Bq)
    f.h("ΟΨΕΙΣ Β · Γ – ΕΙΣΟΔΟΣ ΚΑΙ ΚΟΥΖΙΝΑ")
    f.p("Η κουζίνα είναι το μόνο σημείο όπου καλώδιο περνά κάτω από δοκάρι μέσα στο ταβάνι: το δοκάρι της είναι +2,58 και η οροφή +2,48 – μένουν 9 cm καθαρά.", **Bq)
    f.p("Από εκεί μπαίνει στον τοίχο κουζίνας – σκάλας (Π53, εστίες) και, στο +2,30, γυρίζει τη γωνία μέσα στον τοίχο της εισόδου: διακόπτες, Π07, θυροτηλεόραση, κουδούνι, φως ασφαλείας μέσα στο υπέρθυρο.", **Bq)
    f.p("Ψυγείο, φούρνος, μικροκύματα, απορροφητήρας: από το ταβάνι ίσια μέσα στα ντουλάπια (μοβ).", **Bq)
    f.p("Οι δύο τοίχοι είναι πυράντοχοι: πυράντοχα κουτιά, σφράγιση με πυράντοχη μαστίχη όπου μπαίνει το καλώδιο.", **Bq)
    f.h("ΟΙ ΑΛΛΟΙ ΤΟΙΧΟΙ ΚΑΤΩ ΑΠΟ ΔΟΚΑΡΙ")
    f.p("Τοίχος TV (14) και ΒΔ γωνία (15): από το πάτωμα. Κεφαλάρι Υπν.1 (13): πίσω από τη ντουλάπα. ΒΑ εξώστης (17): μέσα από τη ντουλάπα του Υπν.2. Τομές στο ΗΛ-14.", **Bq)
    DC.finish(no, "ΟΨΕΙΣ ΤΟΙΧΩΝ ΚΑΤΩ ΑΠΟ ΔΟΚΑΡΙΑ", "βόρειος τοίχος σαλονιού · τοίχος εισόδου · τοίχος κουζίνας – σκάλας", "Όψεις 1:30 · A3")
