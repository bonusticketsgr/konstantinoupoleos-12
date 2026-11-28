"""Φύλλα της ηλεκτρολογικής μελέτης Β1 (A3 οριζόντιο) – ΑΠΛΟΠΟΙΗΜΕΝΟ ΤΕΥΧΟΣ (Γιάννης 18/11: «απλοποίησε τα σχέδια»):

  ΗΛ-00 σύνοψη · ΗΛ-01 πίνακας και ζώνες · ΗΛ-02 ρευματοδότες με ύψη / αποστάσεις · ΗΛ-03 διακόπτες με ύψη / αποστάσεις ·
  ΗΛ-04 φωτισμός (κάτοψη) · ΗΛ-05 φωτισμός (τεκμηρίωση, φωτιστικά) · ΗΛ-06 περάσματα καλωδίων (κάτοψη) · ΗΛ-07 περάσματα (τομές) ·
  ΗΛ-08 κέντρο ασθενών / δίκτυο / συναγερμός / πυρανίχνευση / θερμοστάτες · ΗΛ-09 μονογραμμικό (el_det) · ΗΛ-10 πίνακας κυκλωμάτων (el_docs).

Κάθε κάτοψη δείχνει ΕΝΑ θέμα. Όλα τα σημεία, οι αποστάσεις και οι πίνακες βγαίνουν από το μοντέλο b1_el.py."""
import math
import el_draw as D
from el_draw import P, PWR, LGT, SWC, DAT, FIR, HVC, AUT, FEED, BEAMC, INK, MUTE, FAINT, PAGE_W, PAGE_H, SW, ptext, wrap
import el_checks as CK
import el_route as RT
import el_geom as G
import el_plans as PL
import el_docs as DC
import el_det as DT
from el_det import Sec, txt, ln, box, tint

M = W = A = None
CHANC = (0.05, 0.50, 0.42)
DIMC = (0.30, 0.30, 0.34)
ALARMC = (0.45, 0.30, 0.10)


def bind(model):
    global M, W, A
    M, W, A = model, model.W, model.A
    PL.bind(model); DC.bind(model); DT.bind(model); RT.bind(model)


def C():
    return P.C


def fz(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",")


# ================================================================ αποστάσεις σημείων τοίχου από γωνία χώρου / κάσα πόρτας
def _obs():
    return [G.bbox(w["pts"]) for w in W.WALLS] + [G.bbox(p) for p in W.COLS] + [G.bbox(p) for p in getattr(W, "COLS2", [])]


def _openings():
    pts = []
    for d in W.DOORS:
        pts += [(d[0], "κάσα"), (d[2], "κάσα")]
    for w in W.WINS:
        x0, y0, x1, y1 = G.bbox(w)
        if (x1 - x0) >= (y1 - y0):
            pts += [((x0, (y0 + y1) / 2), "κούφωμα"), ((x1, (y0 + y1) / 2), "κούφωμα")]
        else:
            pts += [(((x0 + x1) / 2, y0), "κούφωμα"), (((x0 + x1) / 2, y1), "κούφωμα")]
    return pts


_CACHE = {}


def ref_of(x, y, d, maxd=3.2):
    """Το κοντινότερο σταθερό σημείο κατά μήκος του τοίχου: (απόσταση m, φορά ±1 στην εφαπτομένη, είδος) ή None."""
    key = (round(x, 3), round(y, 3), d)
    if key in _CACHE:
        return _CACHE[key]
    if "obs" not in _CACHE:
        _CACHE["obs"] = _obs(); _CACHE["ops"] = _openings()
    obs, ops = _CACHE["obs"], _CACHE["ops"]
    n = D.VEC[d]; t = (-n[1], n[0])
    px, py = x + n[0] * 0.04, y + n[1] * 0.04
    best = None
    for sgn in (1, -1):
        hit = None; s = 0.02
        while s <= maxd:
            qx, qy = px + t[0] * s * sgn, py + t[1] * s * sgn
            if any(r[0] <= qx <= r[2] and r[1] <= qy <= r[3] for r in obs):
                hit = s; break
            s += 0.005
        cand = [(hit, "γωνία")] if hit is not None else []
        for wl in W.WALLS:                                   # ελεύθερο άκρο του τοίχου όπου κάθεται το σημείο (άνοιγμα χωρίς πόρτα)
            if not G.is_rect(wl["pts"]):
                continue
            wb = G.bbox(wl["pts"])
            if not (wb[0] - 0.02 <= x <= wb[2] + 0.02 and wb[1] - 0.02 <= y <= wb[3] + 0.02):
                continue
            ex, ey = (wb[2] if t[0] * sgn > 0 else wb[0] if t[0] * sgn < 0 else x), (wb[3] if t[1] * sgn > 0 else wb[1] if t[1] * sgn < 0 else y)
            al = abs((ex - x) * t[0] + (ey - y) * t[1])
            tx_, ty_ = ex + t[0] * sgn * 0.04 - n[0] * 0.04, ey + t[1] * sgn * 0.04 - n[1] * 0.04
            if al > 0.03 and (hit is None or al < hit - 0.03) and not any(r[0] <= tx_ <= r[2] and r[1] <= ty_ <= r[3] for r in obs):
                cand.append((al, "άκρο"))
        for (o, kind) in ops:
            off = (o[0] - x) * n[0] + (o[1] - y) * n[1]; al = ((o[0] - x) * t[0] + (o[1] - y) * t[1]) * sgn
            if -0.40 <= off <= 0.03 and 0.03 < al <= (hit if hit is not None else maxd) + 0.01:
                cand.append((al, kind))
        if cand:
            c_ = min(cand)
            if best is None or c_[0] < best[0]:
                best = (round(c_[0], 2), sgn, c_[1])
    _CACHE[key] = best
    return best


SIDE = {"N": 1, "S": -1, "E": -1, "W": 1}


def dims(v, pts, off=0.36):
    """Αλυσίδα διαστάσεων για σημεία τοίχου: pts = [(x, y, d)]. Από το σταθερό σημείο (γωνία / κάσα) ως τον άξονα κάθε κουτιού."""
    groups = {}
    for (x, y, d) in pts:
        r = ref_of(x, y, d)
        if not r:
            continue
        dist, sgn, kind = r
        n = D.VEC[d]; t = (-n[1], n[0])
        rx, ry = x + t[0] * dist * sgn, y + t[1] * dist * sgn
        groups.setdefault((d, round(rx, 2), round(ry, 2)), []).append((dist, x, y))
    for (d, rx, ry), items in groups.items():
        n = D.VEC[d]
        items = sorted(set(items)); prev = (rx, ry); prevd = 0.0
        v.line(rx + n[0] * (off - 0.07), ry + n[1] * (off - 0.07), rx + n[0] * (off + 0.04), ry + n[1] * (off + 0.04), color=DIMC, lw=0.35)
        for dist, x, y in items:
            if dist - prevd < 0.04:
                continue
            a = (prev[0] + n[0] * off, prev[1] + n[1] * off); b = (x + n[0] * off, y + n[1] * off)
            D.dim_chain(v, a, b, fz(dist - prevd), col=DIMC, side=SIDE[d])
            prev = (x, y); prevd = dist


def tag(v, x, y, d, s, col, off=0.235, size=4.2, at=None):
    """Ετικέτα σημείου τοίχου (αριθμός – ύψος): παράλληλα στον τοίχο, ανάμεσα στο σύμβολο και τη γραμμή διάστασης."""
    n = D.VEC[d]
    if at:
        D.halo_text(v, x + at[0], y + at[1], s, size=size, color=col)
        return
    D.halo_text(v, x + n[0] * off, y + n[1] * off, s, size=size, color=col, rot=90 if d in ("E", "W") else 0)


def ref_txt(x, y, d):
    r = ref_of(x, y, d)
    return "—" if not r else "%s %s" % (fz(r[0]), {"γωνία": "γων.", "κάσα": "κάσα", "κούφωμα": "κούφ.", "άκρο": "άκρο"}[r[2]])


# ================================================================ ΗΛ-01 ΠΙΝΑΚΑΣ ΚΑΙ ΖΩΝΕΣ
ZC = {"Ρ1": (0.96, 0.58, 0.16), "Ρ2": (0.45, 0.70, 0.25), "Ρ8": (0.20, 0.55, 0.85), "Ρ3": (0.78, 0.40, 0.72), "Ρ4": (0.10, 0.62, 0.58), "Ρ5": (0.88, 0.36, 0.36),
      "Ρ6": (0.80, 0.66, 0.10)}
ZONES_P = {
    "Ρ1": [(1.705, 5.15, 6.35, 7.10), (3.30, 3.35, 6.40, 4.35), (5.449, 4.35, 6.349, 5.15)], "Ρ2": [(1.705, 7.10, 6.35, 9.0946)], "Ρ8": [(6.35, 5.15, 9.40, 9.0946)],
    "Ρ3": [(1.135, 0.165, 4.80, 3.25)], "Ρ4": [(6.50, 0.75, 9.395, 5.05)], "Ρ5": [(5.05, 0.80, 6.40, 3.25), (0.11, 3.16, 1.05, 5.05), (1.05, 3.50, 3.15, 5.05)],
    "Ρ6": [(9.70, 7.75, 13.76, 9.15), (9.70, 9.15, 12.70, 10.06)]}
ZTAG = {"Ρ1": (3.60, 6.15), "Ρ2": (3.60, 8.20), "Ρ8": (7.80, 8.55), "Ρ3": (2.60, 2.75), "Ρ4": (8.00, 3.05), "Ρ5": (5.72, 2.35), "Ρ6": (12.60, 8.62)}
ZTAG2 = [("Ρ1", 4.10, 3.60), ("Ρ5", 2.10, 4.05)]
LZ = [("Φ1", [(1.76, 5.21, 9.27, 9.06)], (5.80, 7.55)), ("Φ2", [(9.76, 7.81, 13.70, 9.09)], (10.50, 8.62)), ("Φ3", [(1.19, 0.22, 4.74, 3.19), (6.56, 0.81, 9.33, 4.99), (3.36, 3.41, 6.34, 4.29)], (2.60, 1.95)),
      ("Φ4", [(5.11, 0.86, 6.34, 3.19), (0.17, 3.56, 3.09, 4.99)], (5.72, 1.55))]
LTAG2 = [("Φ3", 8.00, 2.25), ("Φ3", 4.90, 3.60), ("Φ4", 2.10, 4.55)]
DED = [("Κ4", 10.05, 9.62), ("Κ2 · Κ5 φούρνοι", 11.45, 8.05), ("Κ1 εστίες 3Φ", 12.62, 8.02), ("Κ3", 12.40, 9.86), ("Π1 · Π2 πλυντ. – στεγν.", 3.66, 4.47),
       ("ΑΘ αντλία θερμ.", 10.65, 2.31), ("ΚΛ κλιματισμός", 10.82, 1.40), ("ΕΝ ενδοδαπέδια", 4.32, 4.84)]


def panel_face(x0, ytop, mw=12.6, rh=30.0, rg=6.0, colors=True):
    """Όψη πίνακα (σειρές × στοιχεία) – επιστρέφει το y κάτω από αυτήν."""
    c = C()
    H = 5 * rh + 4 * rg
    box(x0 - 6, ytop - H - 6, 18 * mw + 12, H + 12, fill=(0.97, 0.97, 0.98), stroke=INK, lw=1.0)
    cc = {q["id"]: q for q in M.CIRCUITS}
    for ri, row in enumerate(M.PANEL_ROWS):
        ry = ytop - ri * (rh + rg) - rh
        xx = x0
        for lab, mods, kind in row:
            w_ = mods * mw
            key = lab.split(" ")[0]
            if kind == "free":
                box(xx + 0.8, ry + 0.8, w_ - 1.6, rh - 1.6, stroke=(0.72, 0.72, 0.75), lw=0.5, dash=[1.5, 1.5])
                txt(xx + w_ / 2, ry + rh / 2 - 2, "ελεύθ. %d" % mods, size=4.6, color=MUTE, anchor="c")
            else:
                fill, tc = (1, 1, 1), INK
                if kind == "main":
                    fill, tc = (0.25, 0.25, 0.28), (1, 1, 1)
                elif kind == "rcd":
                    fill, tc = tint(SWC, 0.75), SWC
                elif kind == "rcbo":
                    fill, tc = tint(HVC, 0.80), HVC
                if colors and key in ZC:
                    fill = tint(ZC[key], 0.45)
                elif colors and key.startswith("Φ"):
                    fill = tint(LGT, 0.60)
                box(xx + 0.6, ry + 0.6, w_ - 1.2, rh - 1.2, fill=fill, stroke=INK if kind in ("main", "mcb") else tc, lw=0.6)
                if len(lab) == 1:
                    txt(xx + w_ / 2, ry + rh / 2 - 2, lab, size=5.2, font="Inter-Bold", color=tc, anchor="c")
                elif mods <= 2:
                    c.saveState(); c.translate(xx + w_ / 2 + 1.9, ry + rh / 2); c.rotate(90); c.setFont("Inter-Bold", 5.2); c.setFillColorRGB(*tc); c.drawCentredString(0, 0, lab); c.restoreState()
                else:
                    ls = lab.split(" ", 1) if (SW(lab, "Inter-Bold", 5.2) > w_ - 3) else [lab]
                    for j, s_ in enumerate(ls):
                        txt(xx + w_ / 2, ry + rh / 2 - 2 + (len(ls) - 1) * 3.2 - j * 6.4, s_, size=5.2, font="Inter-Bold", color=tc, anchor="c")
            xx += w_
    return ytop - H - 6


def sheet_01(no="ΗΛ-01"):
    def fn(v):
        for k, rects in ZONES_P.items():
            for r in rects:
                D.zone(v, r, ZC[k], alpha=0.22, stroke=False)
        for k, rects, tg in LZ:
            for r in rects:
                C().saveState(); C().setDash([4, 2]); v.rect(*r, stroke=LGT, lw=1.1); C().restoreState()
        PL.ac_units(v, faint=True)
        if M.SHOW_HVAC:
            D.unit_rect(v, M.HP_RECT, col=HVC, dashed=True, alpha=0.10)
        PL.sockets(v, faint=True)
        for k, (x, y) in ZTAG.items():
            X, Y = v.p(x, y); P.pill(X, Y, k, None, ZC[k], "c", 8.4)
        for k, x, y in ZTAG2:
            X, Y = v.p(x, y); P.pill(X, Y, k, None, ZC[k], "c", 6.6)
        for k, rects, (x, y) in LZ:
            X, Y = v.p(x, y); P.pill(X, Y, k, None, LGT, "c", 8.4)
        for k, x, y in LTAG2:
            X, Y = v.p(x, y); P.pill(X, Y, k, None, LGT, "c", 6.6)
        for s_, x, y in DED:
            if not M.SHOW_HVAC and s_.split()[0] in M.HVAC_CIRC:
                continue
            D.halo_text(v, x, y, s_, size=4.6, color=HVC if s_[0] in "ΑΚΕ" and not s_.startswith("Κ") or s_.startswith("ΚΛ") else PWR, font="Inter-Bold")
        D.halo_text(v, 2.60, 9.90, "ΕΞ  εξώστες: φώτα + πρίζα νότιου εξώστη" if M.SHOW_NOTES else "ΕΞ εξώστες", size=4.8, color=PWR, font="Inter-Bold")
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        D.halo_text(v, 11.62, 2.62, "shaft: ΠΑΡΟΧΗ από τον πίνακα της αποθήκης (ΗΛ-11) · ΗΛ boiler (δώμα) · ασθενή" if M.SHOW_NOTES else "shaft Η/Μ", size=4.6, color=INK, font="Inter-Bold")
        PL.panel(v)
        D.halo_text(v, 5.10, 4.86, "ΚΑ · ΣΠ", size=4.4, color=DAT, font="Inter-Bold")
    PL._plan(fn, "ΗΛΕΚΤΡΙΚΟΣ ΠΙΝΑΚΑΣ ΚΑΙ ΖΩΝΕΣ ΚΥΚΛΩΜΑΤΩΝ")
    # ---- δεξιά στήλη: όψη πίνακα + πίνακες ζωνών
    y = P._head(P.TOP - 22, "ΟΨΗ ΠΙΝΑΚΑ «ΓΠ» – 5 ΣΕΙΡΕΣ × 18 ΣΤΟΙΧΕΙΑ")
    y = panel_face(P.PX + 6, y + 4, mw=12.6)
    used = M.modules_used(); tot = M.PANEL["rows"] * M.PANEL["per_row"]
    for j, s_ in enumerate(["Χωνευτός στο δυτικό άκρο του χωλ (τοίχος λουτρού γονέων)",
                            "Άνοιγμα ≈ 52 × 93 cm · από +1,02 ως +1,95 από το δάπεδο",
                            "Σε χρήση %d στοιχεία · ελεύθερα %d" % (used, tot - used)] if M.SHOW_NOTES else []):
        txt(P.PX - 2, y - 9 - j * 7.6, s_, size=5.8, font="Inter-SemiBold" if j == 2 else "Inter")
    y -= 36 if M.SHOW_NOTES else 12
    cc = {q["id"]: q for q in M.CIRCUITS}
    rows, colors = [], {}
    for k in ("Ρ1", "Ρ2", "Ρ8", "Ρ3", "Ρ4", "Ρ5", "Ρ6"):
        q = cc[k]
        rows.append([("", dict(fill=tint(ZC[k], 0.30))), k, q["name"].replace("Ρευματοδότες ", "").replace("Ρευματοδότες", ""), "%s%d" % (q["curve"], q["In"]), q["cable"]])
    for k in ("Φ1", "Φ2", "Φ3", "Φ4"):
        q = cc[k]
        rows.append([("", dict(fill=tint(LGT, 0.45))), k, q["name"], "%s%d" % (q["curve"], q["In"]), q["cable"]])
    y = D.table(P.PX - 4, y, [10, 18, P.PW - 10 - 18 - 24 - 28 + 8, 24, 28], rows, head=["", "", "ΖΩΝΕΣ: ΡΕΥΜΑΤΟΔΟΤΕΣ (χρώμα) · ΦΩΤΙΣΜΟΣ (πλαίσιο)", "ΑΣΦ.", "mm²"], size=5.3, lead=6.5, pad=2.0, zebra=False)
    rows = []
    for k in ("Κ1", "Κ2", "Κ3", "Κ4", "Κ5", "Π1", "Π2", "ΑΘ", "ΚΛ", "ΑΚ", "ΕΝ", "ΕΞ", "ΚΑ", "ΣΠ", "ΗΛ"):
        if not M.SHOW_HVAC and k in M.HVAC_CIRC:
            continue                                   # R20: κλιματισμός / ενδοδαπέδια σε δικά τους φύλλα (τα κυκλώματα μένουν στο ΗΛ-09 / ΗΛ-10)
        q = cc[k]
        nm = q["name"].split(" – ")[0].split(" (")[0]
        rows.append([k, nm, "%s%d" % (q["curve"], q["In"]), q["cable"]])
    D.table(P.PX - 4, y - 5, [22, P.PW - 22 - 24 - 28 + 8, 24, 28], rows, head=["", "ΑΠΟΚΛΕΙΣΤΙΚΕΣ ΓΡΑΜΜΕΣ", "ΑΣΦ.", "mm²"], size=5.3, lead=6.4, pad=1.7, bold_first=True)
    PL._finish(no, "ΠΙΝΑΚΑΣ ΚΑΙ ΖΩΝΕΣ", "Θέση και διάταξη πίνακα · ποιο κύκλωμα τροφοδοτεί ποιον χώρο")


# ================================================================ ΗΛ-02 ΡΕΥΜΑΤΟΔΟΤΕΣ
SOCK_AT = {"Π01": (0.42, 0.50), "Π62": (-0.40, -0.22), "Π24": (0.62, -0.04), "Π31": (-0.44, -0.12), "Π30": (-0.50, -0.13), "Π63": (0.44, -0.08), "Π44": (-0.40, 0.10), "Π08": (-0.34, -0.22), "Π60": (0.30, 0.20), "Π54": (0.0, 0.34), "Π55": (0.0, 0.20), "Π51": (-0.10, 0.20), "Π52": (0.12, 0.34), "Π50": (0.0, 0.20), "Π13": (-0.20, -0.20), "Π14": (0.0, -0.20),
           "Π11": (0.36, -0.03), "Π12": (0.36, 0.04), "Π59": (0.0, -0.20)}


def sheet_02(no="ΗΛ-02"):
    def fn(v):
        PL.ac_units(v, faint=True)
        PL.sockets(v)
        pts = []
        for s in M.SOCKETS:
            if not M.drawn(s[0]):
                continue
            opt = PL._opt(s, 10)
            inside = opt.get("surf") or s[0] in CK.INSIDE_OK
            tag(v, s[1], s[2], s[3], s[0][1:] if inside else "%s · %s" % (s[0][1:], fz(s[6])), PWR, at=SOCK_AT.get(s[0]))
            if not inside and s[8] != "ΕΞ":
                pts.append((s[1], s[2], s[3]))
        for f in (M.FIXED if M.SHOW_HVAC else []):
            tag(v, f[1], f[2], f[3], "%s · %s" % (f[0], fz(f[4])), HVC, at={"ΑΘ": (0.48, -0.07), "ΚΛ": (0.48, 0.07), "ΚΜ3": (0.50, 0.0)}[f[0]])
        dims(v, pts)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΡΕΥΜΑΤΟΔΟΤΕΣ – ΘΕΣΕΙΣ, ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ")
    y = P.legend(["e_sock", "e_sock2", "e_usb", "e_sockip", "e_ded", "e_fix"] + (["e_fixm"] if M.SHOW_HVAC else []) + ["e_dim"])
    if M.SHOW_NOTES:
        txt(P.PX - 2, y + 2, "Ετικέτα: αριθμός · ύψος άξονα κουτιού από το τελικό δάπεδο (m).", size=5.6, font="Inter-SemiBold")
    rows = []
    for s in M.SOCKETS:
        if not M.drawn(s[0]):
            continue
        opt = PL._opt(s, 10)
        inside = opt.get("surf") or s[0] in CK.INSIDE_OK
        rows.append([s[0][1:], fz(s[6]), "ερμάριο" if inside else ("όψη" if s[8] == "ΕΞ" else ref_txt(s[1], s[2], s[3])), s[7], ("%d× " % s[4] if s[4] > 1 else "") + s[9].split(" – ")[0].split(" (")[0]])
    for f in (M.FIXED if M.SHOW_HVAC else []):
        rows.append([f[0], fz(f[4]), "—", f[5], f[7].split(" – ")[0]])
    D.table(P.PX - 4, y - 8, [18, 22, 40, 20, P.PW - 100 + 8], rows, head=["Π", "ΥΨΟΣ", "ΑΠΟ", "ΚΥΚΛ.", "ΧΡΗΣΗ"], size=5.1, lead=6.2, pad=1.55, bold_first=True, aligns={1: "r"})
    PL._finish(no, "ΡΕΥΜΑΤΟΔΟΤΕΣ – ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ", "Π01–Π60 · ύψος από το δάπεδο · απόσταση από γωνία / κάσα")


# ================================================================ ΗΛ-03 ΔΙΑΚΟΠΤΕΣ
KIND_TXT = {"1": "απλός", "2": "αλέ-ρετούρ", "X": "ενδιάμεσος", "D": "dimmer", "R": "ρολό ▲▼"}
SW_AT = {"Δ10": (0.66, -0.06), "Δ16": (0.40, 0.16), "Δ15": (-0.40, -0.30), "Δ14": (0.80, -0.16), "Δ13": (-0.42, 0.20), "Δ2": (0.16, 0.30), "Δ6": (0.0, 0.30)}


def sheet_03(no="ΗΛ-03"):
    def fn(v):
        PL.lights(v, faint=True, groups=True)
        PL.shutters(v, faint=True)
        PL.switches(v)
        pts = []
        for s in M.SWITCHES:
            h = PL._opt(s, 7).get("h", M.H_SW)
            tag(v, s[1], s[2], s[3], "%s · %s" % (s[0], fz(h)), SWC, off=0.30, at=SW_AT.get(s[0]))
            pts.append((s[1], s[2], s[3]))
        dims(v, pts, off=0.44)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΔΙΑΚΟΠΤΕΣ – ΘΕΣΕΙΣ, ΥΨΗ, ΑΠΟΣΤΑΣΕΙΣ ΚΑΙ ΤΙ ΑΝΑΒΕΙ Ο ΚΑΘΕΝΑΣ")
    y = P.legend(["e_sw", "e_sw2", "e_swx", "e_dimmer", "e_roll", "e_motor", "e_grp", "e_dim"])
    rows = []
    for s in M.SWITCHES:
        opt = PL._opt(s, 7)
        fn_ = " · ".join("%s %s" % (KIND_TXT[k], g) for k, g in s[4])
        rows.append([s[0], fz(opt.get("h", M.H_SW)), ref_txt(s[1], s[2], s[3]), s[6].split(" (")[0] + ": " + fn_])
    y = D.table(P.PX - 4, y - 2, [20, 22, 40, P.PW - 82 + 8], rows, head=["", "ΥΨΟΣ", "ΑΠΟ", "ΘΕΣΗ: ΠΛΗΚΤΡΑ → ΟΜΑΔΑ"], size=5.1, lead=6.2, pad=1.8, bold_first=True, aligns={1: "r"})
    rows = [[g, d["name"], d["c"], "ναι" if d["dim"] else "—"] for g, d in M.GROUPS.items()]
    D.table(P.PX - 4, y - 5, [18, P.PW - 18 - 22 - 22 + 8, 22, 22], rows, head=["ΟΜ.", "ΤΙ ΑΝΑΒΕΙ", "ΚΥΚΛ.", "DIM"], size=5.0, bold_first=True, lead=6.1, pad=1.8)
    PL._finish(no, "ΔΙΑΚΟΠΤΕΣ – ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ", "%d πλαίσια · αλέ-ρετούρ · dimmers · ομάδες φωτιστικών" % len(M.SWITCHES))


# ================================================================ ΗΛ-04 ΦΩΤΙΣΜΟΣ – ΚΑΤΟΨΗ
def _ceil_dist(x, y):
    """Αποστάσεις φωτιστικού οροφής από τις κοντινότερες παρειές (τοίχος / ντουλάπα ως την οροφή): (Β ή Ν, Δ ή Α)."""
    if "obs" not in _CACHE:
        _CACHE["obs"] = _obs(); _CACHE["ops"] = _openings()
    obs = _CACHE["obs"] + [w_["r"] for w_ in W.WARDROBES] + [(e[1], e[2], e[3], e[4]) for e in W.EQUIP if e[0] == "tall"] + [G.bbox(w_) for w_ in W.WINS]
    for d_ in W.DOORS:
        obs.append((min(d_[0][0], d_[2][0]) - 0.03, min(d_[0][1], d_[2][1]) - 0.03, max(d_[0][0], d_[2][0]) + 0.03, max(d_[0][1], d_[2][1]) + 0.03))
    out = {}
    for nm, (dx, dy) in (("Β", (0, -1)), ("Ν", (0, 1)), ("Δ", (-1, 0)), ("Α", (1, 0))):
        s = 0.01
        while s < 8:
            qx, qy = x + dx * s, y + dy * s
            if any(r[0] <= qx <= r[2] and r[1] <= qy <= r[3] for r in obs):
                break
            s += 0.005
        out[nm] = s
    a = "Β" if out["Β"] <= out["Ν"] else "Ν"; b = "Δ" if out["Δ"] <= out["Α"] else "Α"
    return "%s %s" % (a, fz(out[a])), "%s %s" % (b, fz(out[b]))


SPOT_KIND = {"s": "σταθερό", "t": "ΔΙΠΛΟ 2 × 36°", "adj": "ρυθμιζόμενο", "s44": "IP44", "s65": "IP65"}


def sheet_04(no="ΗΛ-04"):
    def fn(v):
        for cu in A.CURTAINS:
            v.rect(*cu["rect"], fill=(0.93, 0.93, 0.95), stroke=(0.75, 0.75, 0.78), lw=0.3)
        D.zone(v, (A.STRIP_X, 5.15, A.LIN_X, 8.915), LGT, alpha=0.05, dash=(3, 2), lw=0.4)
        for u in (A.UNITS if M.SHOW_HVAC else []):
            D.unit_rect(v, u["rect"], col=(0.78, 0.68, 0.88), dashed=True, alpha=0.10)
        for h in (A.HATCHES if M.SHOW_HVAC else []):
            C().saveState(); C().setDash([1.5, 1.5]); v.rect(*h["rect"], stroke=(0.6, 0.6, 0.65), lw=0.4); C().restoreState()
        PL.detectors(v, faint=True)
        PL.switches(v, faint=True)
        # άξονες του κανάβου (καθιστικό, Υπν.2)
        for xs, ys in ((M.LIV_X, M.LIV_Y), (M.B2_X, M.B2_Y)):
            for x_ in xs:
                D.route(v, [(x_, ys[0] - 0.22), (x_, ys[-1] + 0.22)], col=LGT, lw=0.35, halo=False, dash=[1.2, 1.6])
            for y_ in ys:
                D.route(v, [(xs[0] - 0.22, y_), (xs[-1] + 0.22, y_)], col=LGT, lw=0.35, halo=False, dash=[1.2, 1.6])
        D.route(v, [(M.LIV_SYM, M.LIV_Y[0] - 0.45), (M.LIV_SYM, M.LIV_Y[-1] + 0.45)], col=LGT, lw=0.5, halo=False, dash=[3, 1.5])
        spot_dims(v)                                       # R21: αλυσίδες από τους τοίχους σε κάθε σειρά / στήλη φωτιστικών (και στους εξώστες)
        PL.lights(v, labels=True, groups=True)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΦΩΤΙΣΜΟΣ – ΚΑΤΟΨΗ ΜΕ ΔΙΑΣΤΑΣΕΙΣ (ΟΠΩΣ ΟΙ ΑΝΟΨΕΙΣ %s · ΜΕΛΕΤΗ ΦΩΤΙΣΜΟΥ R04)" % A.REV)
    y = P.legend(["e_spot", "e_spot44", "e_spot65", "e_extc", "e_ext", "e_led", "e_mir", "e_grp", "e_det", "e_dimspot"])
    rows = []
    for q in M.SPOTS:
        a, b = _ceil_dist(q[2], q[3])
        rows.append([q[0], SPOT_KIND[q[1]], a, b, q[5]])
    y = D.table(P.PX - 4, y - 2, [24, 40, 28, 28, P.PW - 120 + 8], rows, head=["", "ΕΙΔΟΣ", "ΑΠΟ", "ΑΠΟ", "ΤΙ ΦΩΤΙΖΕΙ"], size=4.9, lead=5.9, pad=1.35, bold_first=True)
    if M.SHOW_NOTES:
        txt(P.PX - 2, y - 8, "ΑΠΟ: m από τον κοντινότερο τοίχο / ντουλάπα (Β βόρεια · Ν νότια · Δ δυτικά · Α ανατολικά).", size=5.2, color=MUTE)
    PL._finish(no, "ΦΩΤΙΣΜΟΣ – ΚΑΤΟΨΗ ΜΕ ΔΙΑΣΤΑΣΕΙΣ", "Spots μονά / διπλά · φώτα εξωστών · ομάδες · αποστάσεις από τοίχους")


# ================================================================ R21: διαστάσεις φωτιστικών από τους τοίχους (ΗΛ-04)
def _hit(x, y, dx, dy, obs, maxd=4.5, skip=0.08, step=0.01):
    """Απόσταση ως το πρώτο εμπόδιο (ορθογώνιο) κατά τη φορά (dx, dy) ή None – ακριβής ως την παρειά του."""
    s_ = skip
    while s_ <= maxd:
        qx, qy = x + dx * s_, y + dy * s_
        for r in obs:
            if r[0] <= qx <= r[2] and r[1] <= qy <= r[3]:
                if dx > 0:
                    return round(r[0] - x, 4)
                if dx < 0:
                    return round(x - r[2], 4)
                if dy > 0:
                    return round(r[1] - y, 4)
                return round(y - r[3], 4)
        s_ += step
    return None


def _dim_obs():
    """Εμπόδια για τις διαστάσεις των φωτιστικών: τοίχοι, κολόνες, στηθαία + τα ανοίγματα πορτών (η γραμμή του τοίχου συνεχίζει)
    + τα κουφώματα, μεγαλωμένα ως την εσωτερική παρειά της επένδυσης (10,5 cm) προς τη μεριά του σπιτιού."""
    if "dobs" in _CACHE:
        return _CACHE["dobs"], _CACHE["dwins"]
    from shapely.geometry import Polygon, Point
    fl = [Polygon(f) for f in W.FLOORS]
    obs = _obs()
    for d in W.DOORS:
        (hx, hy), _, (jx, jy) = d
        obs.append((min(hx, jx) - 0.05, min(hy, jy) - 0.05, max(hx, jx) + 0.05, max(hy, jy) + 0.05))
    if getattr(M, "LINTEL", None):
        obs.append(tuple(M.LINTEL))                          # το άνοιγμα χωλ – καθιστικού (χωρίς πόρτα): η γραμμή του τοίχου συνεχίζει
    wb = [G.bbox(w["pts"]) for w in W.WALLS]

    def lining(lo, hi, a0, a1, horiz, inward):
        """Παρειά της επένδυσης δίπλα στο κούφωμα προς τη μεριά του σπιτιού: ο πιο μέσα τοίχος που ακουμπά στη γραμμή του τούβλου."""
        best = 0.055
        for b in wb:
            if horiz:
                adj = b[2] >= a0 - 0.30 and b[0] <= a1 + 0.30
                if inward > 0 and adj and abs(b[1] - hi) < 0.02 and b[3] - hi <= 0.16:
                    best = max(best, b[3] - hi)
                if inward < 0 and adj and abs(b[3] - lo) < 0.02 and lo - b[1] <= 0.16:
                    best = max(best, lo - b[1])
            else:
                adj = b[3] >= a0 - 0.30 and b[1] <= a1 + 0.30
                if inward > 0 and adj and abs(b[0] - hi) < 0.02 and b[2] - hi <= 0.16:
                    best = max(best, b[2] - hi)
                if inward < 0 and adj and abs(b[2] - lo) < 0.02 and lo - b[0] <= 0.16:
                    best = max(best, lo - b[0])
        return best
    wins = []
    for w in W.WINS:
        x0, y0, x1, y1 = G.bbox(w)
        if (x1 - x0) >= (y1 - y0):                           # οριζόντιο κούφωμα: ποια πλευρά είναι έξω (δάπεδο εξώστη);
            cx = (x0 + x1) / 2
            out_s = any(f.contains(Point(cx, y1 + 0.25)) for f in fl)
            e = lining(y0, y1, x0, x1, True, -1 if out_s else 1)
            r = (x0, y0 - (e if out_s else 0), x1, y1 + (0 if out_s else e))
        else:
            cy = (y0 + y1) / 2
            out_e = any(f.contains(Point(x1 + 0.25, cy)) for f in fl)
            e = lining(x0, x1, y0, y1, False, -1 if out_e else 1)
            r = (x0 - (e if out_e else 0), y0, x1 + (0 if out_e else e), y1)
        wins.append(r)
    _CACHE["dobs"] = obs + wins; _CACHE["dwins"] = [G.bbox(w) for w in W.WINS]; _CACHE["dbase"] = obs
    return _CACHE["dobs"], _CACHE["dwins"]


def _ends(x, y, dx, dy):
    """Παρειά τοίχου / κολόνας / στηθαίου / κουφώματος κατά τη φορά· στους εξώστες, αν δεν υπάρχει, η λαμπά του κουφώματος
    μπροστά στο οποίο είναι το φωτιστικό (η ακτίνα ρίχνεται στο ύψος του κουφώματος)."""
    obs, wins = _dim_obs()
    base = _CACHE["dbase"]
    h = _hit(x, y, dx, dy, obs)
    if h is None and dy == 0:
        for (x0, y0, x1, y1) in wins:
            if x0 <= x <= x1 and (x1 - x0) > (y1 - y0):
                h = _hit(x, (y0 + y1) / 2, dx, 0, base, skip=0.02)
                break
    elif h is None and dx == 0:
        for (x0, y0, x1, y1) in wins:
            if y0 <= y <= y1 and (y1 - y0) > (x1 - x0):
                h = _hit((x0 + x1) / 2, y, 0, dy, base, skip=0.02)
                break
    return h


def _clear(a, b, y=None, x=None):
    """Καμία παρειά ανάμεσα στα δύο φωτιστικά της ίδιας σειράς (y) / στήλης (x)."""
    obs, _ = _dim_obs()
    if y is not None:
        h = _hit(a, y, 1, 0, obs, maxd=b - a)
    else:
        h = _hit(x, a, 0, 1, obs, maxd=b - a)
    return h is None


DIM_FLIP = {"Λ1"}          # στήλες φωτιστικών που η αλυσίδα τους μπαίνει δυτικά (δεξιά πέφτει πάνω στο όνομα του χώρου)


def spot_dims(v, off=0.30):
    """Αλυσίδες διαστάσεων για κάθε σειρά (ίδιο y) και κάθε στήλη (ίδιο x) φωτιστικών: από την παρειά του τοίχου ως τον άξονα κάθε φωτιστικού
    και ως την απέναντι παρειά. Ένα φωτιστικό μόνο του σε σειρά μετριέται μόνο αν είναι το πρώτο της στήλης του (και αντίστροφα)."""
    pts = [(q[0], q[2], q[3]) for q in M.SPOTS] + [(e[0], e[1], e[2]) for e in M.EXT_SPOTS]
    ext = {e[0] for e in M.EXT_SPOTS}
    rows, cols = {}, {}
    for n, x, y in pts:
        rows.setdefault(round(y, 2), []).append((x, n)); cols.setdefault(round(x, 2), []).append((y, n))

    def runs(items, fixed, horiz):
        items = sorted(items); out = [[items[0]]]
        for a, b in zip(items, items[1:]):
            ok_ = _clear(a[0], b[0], y=fixed) if horiz else _clear(a[0], b[0], x=fixed)
            if ok_ and b[0] - a[0] < 4.0:
                out[-1].append(b)
            else:
                out.append([b])
        return out
    rrun, crun = {}, {}                                      # φωτιστικό → (θέση στο run, μήκος run)
    rruns = [(y, r) for y, items in rows.items() for r in runs(items, y, True)]
    cruns = [(x, r) for x, items in cols.items() for r in runs(items, x, False)]
    for _, r in rruns:
        for i, q in enumerate(r):
            rrun[q[1]] = (i, len(r))
    for _, r in cruns:
        for i, q in enumerate(r):
            crun[q[1]] = (i, len(r))

    def chain(vals, at, horiz, side=1):
        for a_, b_ in zip(vals, vals[1:]):
            if b_ - a_ < 0.03:
                continue
            pa, pb = ((a_, at), (b_, at)) if horiz else ((at, a_), (at, b_))
            D.dim_chain(v, pa, pb, fz(b_ - a_), side=side)
    done = []
    for y, run in rruns:
        if len(run) == 1 and crun[run[0][1]][1] >= 2 and crun[run[0][1]][0] != 0:
            continue
        xs = [q[0] for q in run]
        w_ = _ends(xs[0], y, -1, 0); e_ = _ends(xs[-1], y, 1, 0)
        vals = ([round(xs[0] - w_, 3)] if w_ else []) + xs + ([round(xs[-1] + e_, 3)] if e_ else [])
        key = tuple(round(q, 2) for q in vals)
        if len(vals) >= 2 and not any(k == key and abs(yy - y) < 0.6 for k, yy in done):
            o = -off if all(q[1] in ext for q in run) else off           # εξώστες: η αλυσίδα προς την όψη, όχι πάνω στο «ΕΞΩΣΤΗΣ»
            chain(vals, y + o, True, side=1 if o > 0 else -1); done.append((key, y))
    done = []
    for x, run in cruns:
        if len(run) == 1 and rrun[run[0][1]][1] >= 2 and rrun[run[0][1]][0] != 0:
            continue
        ys = [q[0] for q in run]
        n_ = _ends(x, ys[0], 0, -1); s_ = _ends(x, ys[-1], 0, 1)
        vals = ([round(ys[0] - n_, 3)] if n_ else []) + ys + ([round(ys[-1] + s_, 3)] if s_ else [])
        key = tuple(round(q, 2) for q in vals)
        if len(vals) >= 2 and not any(k == key and abs(xx - x) < 0.6 for k, xx in done):
            o = -off if any(q[1] in DIM_FLIP for q in run) else off
            chain(vals, x + o, False, side=-1 if o > 0 else 1); done.append((key, x))


# ================================================================ ΗΛ-06 ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ
HOLEC = (0.62, 0.10, 0.62)
FLOORC = (0.55, 0.33, 0.08)
HOLE_LAB = {"ΟΠ5": (-0.34, -0.40), "ΟΠ1": (0.20, -0.62), "ΟΠ2": (0.40, -0.38), "ΟΠ3": (0.62, 0.0), "ΟΠ4": (0.62, 0.0)}


def _holes(v, labels=True):
    """Οπές Ø75 στα δοκάρια: γραμμή μέσα από το πλάτος της δοκού + ετικέτα."""
    c = C()
    for h in CK.holes():
        if not M.SHOW_HVAC and h["kind"] == "hvac":
            continue                                   # R20: η ΟΠ2 (αποχέτευση + ψυκτικά ΚΜ1) στο φύλλο κλιματισμού
        a_, b_ = ((h["x"], h["y"] - 0.15), (h["x"], h["y"] + 0.15)) if h["horiz"] else ((h["x"] - 0.15, h["y"]), (h["x"] + 0.15, h["y"]))
        (X0, Y0), (X1, Y1) = v.p(*a_), v.p(*b_)
        c.saveState(); c.setLineCap(0)
        c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(4.6); c.line(X0, Y0, X1, Y1)
        c.setStrokeColorRGB(*HOLEC); c.setLineWidth(2.6); c.line(X0, Y0, X1, Y1); c.restoreState()
        if labels:
            dx, dy = HOLE_LAB[h["id"]]
            v.line(h["x"], h["y"], h["x"] + dx, h["y"] + dy, color=HOLEC, lw=0.5)
            X2, Y2 = v.p(h["x"] + dx, h["y"] + dy); P.pill(X2, Y2, h["id"], None, HOLEC, "c", 5.2)
FURNC = (0.55, 0.25, 0.62)
EXTC = (0.30, 0.42, 0.52)                               # έξω: στο ταβάνι του εξώστη, μέσα στο φινίρισμα
MODEC = {"top": (0.10, 0.55, 0.30), "side": (0.05, 0.50, 0.60), "via": (0.85, 0.50, 0.02), "back": (0.50, 0.28, 0.75), "furn": (0.66, 0.28, 0.58), "floor": (0.55, 0.33, 0.08), "out": (0.30, 0.42, 0.52)}
MODET = {"top": "από το ταβάνι, ίσια", "side": "κάτω από το δοκάρι (κενό ≥ 6 cm)", "via": "οριζόντια ΜΕΣΑ στον τοίχο", "back": "από πίσω, μέσα από ντουλάπα", "furn": "μέσα / πίσω από ντουλάπα", "floor": "ΑΠΟ ΤΟ ΠΑΤΩΜΑ", "out": "ΑΠΟ ΕΞΩ, από το ταβάνι του εξώστη"}
NUM_AT = {"1": (3.52, 4.22), "4": (6.17, 4.55), "8": (2.44, 5.36), "9": (4.55, 5.40), "10": (7.90, 5.36), "12": (9.12, 6.95), "15": (2.02, 5.50), "16": (10.02, 9.72), "7": (1.42, 2.90), "13": (1.55, 0.40),
          "14": (3.75, 8.50), "2": (5.05, 3.56), "3": (6.72, 2.15), "5": (5.28, 2.60), "6": (2.55, 3.02), "11": (11.95, 8.02), "17": (9.20, 1.52), "18": (9.05, 2.62)}
NUM_MORE = {"18": [(8.62, 8.72)]}             # η ίδια τομή ισχύει και για το τοιχάκι του Δ18


def _draw3(v, pts, col=PWR, lw=1.0):
    """Προβολή μιας διαδρομής 3D στην κάτοψη, ανά μέσο: κενό οροφής συνεχής · μέσα σε τοίχο / τούβλο διακεκομμένη μπλε · έπιπλο διακεκομμένη μοβ · δάπεδο καφέ."""
    runs = []
    for a, b in zip(pts, pts[1:]):
        if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
            if abs(a[2] - b[2]) > 0.35 and (a[3] if not isinstance(a[3], tuple) else a[3][0]) != "void":
                D.drop(v, a[0], a[1], col=PL.WALLC if b[2] < a[2] else FLOORC, r=0.042, up=b[2] > a[2])
            continue
        m = a[3][0] if isinstance(a[3], (tuple, list)) else a[3]
        cls = "void" if m in ("void", "hole", "shaft") else ("ext" if m == "ext" else ("floor" if m == "floor" else ("furn" if m == "furn" else "wall")))
        if runs and runs[-1][0] == cls and runs[-1][1][-1] == (a[0], a[1]):
            runs[-1][1].append((b[0], b[1]))
        else:
            runs.append((cls, [(a[0], a[1]), (b[0], b[1])]))
    for cls, p2 in runs:
        if cls == "void":
            D.route(v, p2, col=col, lw=lw)
        elif cls == "wall":
            D.route(v, p2, col=PL.WALLC, lw=1.7, dash=[2.6, 1.6])
        elif cls == "furn":
            D.route(v, p2, col=FURNC, lw=1.7, dash=[2.6, 1.6])
        elif cls == "ext":
            D.route(v, p2, col=EXTC, lw=1.0, dash=[1.2, 1.4])
        else:
            D.route(v, p2, col=FLOORC, lw=2.4, dash=[5, 1.6, 1, 1.6])


def _routes(v, tags=True, zoom=False):
    """Κάτοψη όλων των διαδρομών – προβολή των ΙΔΙΩΝ 3D διαδρομών που ελέγχει το el_route (κορμοί, τροφοδοσία κάθε τοίχου, γραμμές διανομής μέσα στους τοίχους).
    zoom (R21, μεγεθύνσεις ΗΛ-07 … ΗΛ-09): και η διαδρομή ως ΚΑΘΕ κουτί (κατέβασμα + κοντό τμήμα), με τα σύμβολα και τους αριθμούς των σημείων."""
    PL.beams(v, names=True)
    if M.SHOW_HVAC:
        v.rect(*M.KOUT["rect"], fill=(0.93, 0.86, 0.97), stroke=HVC, lw=0.6)               # R15: κούτελο δίπλα στη Δ3.1 (Υπν.2)
        D.halo_text(v, 7.35, M.KOUT["y0"] - 0.10, "ΚΟΥΤΕΛΟ +2,48 · κενό 15 × 32 cm (ΗΛ-16)", size=4.6, color=HVC)
    if M.SHOW_NOTES:
        D.halo_text(v, 5.92, 4.14, "ΧΩΛ: οροφή +2,48", size=4.6, color=HVC)
    v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
    D.halo_text(v, 10.375, 2.64, "shaft Η/Μ", size=4.8, color=DAT)
    if zoom:
        PL.lights(v, faint=True)
        PL.sockets(v, labels=True); PL.switches(v, labels=True); PL.shutters(v)
        for l in M.WALL_LIGHTS:
            D.wall_light(v, l[1], l[2], l[3], col=LGT, kind=l[4], lab=l[0], lab_off=PL.WL_LAB.get(l[0]))
    else:
        PL.sockets(v, faint=True); PL.switches(v, faint=True)
    B = RT.build()
    for e in B["extra"]:
        _draw3(v, e["pts"], col=PWR, lw=0.8)
    if zoom:
        for d in B["devs"]:
            _draw3(v, d["pts"][d["nfeed"] - 1:], col=PL.WALLC, lw=0.7)
    for f in M.FEEDS:
        ds = [d for d in B["devs"] if d["feed"] == f["id"]]
        _draw3(v, f["feed"], col=PWR, lw=1.0)
        axis, c, zr, med = f["run"]
        m1 = med[0] if isinstance(med, (tuple, list)) else med
        if m1 == "void" or not ds:
            continue                                   # γραμμή διανομής πάνω από τον τοίχο, μέσα στο κενό: δεν σχεδιάζεται (ο τοίχος είναι ανοιχτός από πάνω)
        us = [(d["pts"][-1][0] if axis == "x" else d["pts"][-1][1]) for d in ds] + [f["feed"][-1][0] if axis == "x" else f["feed"][-1][1]]
        a0, a1 = min(us), max(us)
        _draw3(v, [((a0, c, zr, med) if axis == "x" else (c, a0, zr, med)), ((a1, c, zr, "") if axis == "x" else (c, a1, zr, ""))])
    for r in M.ROUTES:
        if not M.SHOW_HVAC and r["kind"] == "hvac":
            continue
        col = HVC if r["kind"] == "hvac" else (DAT if r["kind"] == "weak" else PWR)
        D.route(v, r["pts"], col=col, lw=2.2 if r["n"].startswith("κορμός") else 1.5, arrows=True, lab=r["n"] or None, dash=[4, 1.6] if r["kind"] == "weak" else None)
    D.route(v, M.OUT_ROUTE, col=FEED, lw=1.3, dash=[3, 1.5], arrows=True, lab=None)
    D.route(v, M.FEED_ROUTE, col=FEED, lw=2.6, arrows=True, lab="ΠΑΡΟΧΗ 5×16", seg=0)
    for p in M.PASSES:
        if p["new"] and (M.SHOW_HVAC or not p.get("hvac")):
            D.pass_zone(v, p["rect"], lab=p["id"], lab_at=p["lab"])
    PL.panel(v)
    _holes(v)
    if tags:
        for d in M.DROPS:
            x, y = NUM_AT[d["id"]]
            for x, y in [(x, y)] + NUM_MORE.get(d["id"], []):
                X, Y = v.p(x, y); P.pill(X, Y, d["id"], None, MODEC[d["mode"]], "c", 6.0)


def _leg_routes():
    L = P.LEG
    L["e_num"] = ("Αριθμός τοίχου · χρώμα = από πού μπαίνει το καλώδιο (πίνακας δεξιά)", lambda v: P.pill(v.p(0.21, 0)[0], v.p(0.21, 0)[1], "8", None, MODEC["via"], "c", 5.6))
    L["e_wallrun"] = ("ΜΕΣΑ σε τοίχο / τούβλο – πάντα ΚΑΤΩ από το δοκάρι (οριζόντια στο +2,30 ή χαμηλά)", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=PL.WALLC, lw=1.7, dash=[2.6, 1.6], halo=False))
    L["e_furnrun"] = ("Μέσα / πίσω από ντουλάπα έως οροφή", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FURNC, lw=1.7, dash=[2.6, 1.6], halo=False))
    L["e_floor"] = ("ΠΑΤΩΜΑ: σπιράλ πάνω στην πλάκα, πριν από το γέμισμα", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=FLOORC, lw=2.2, dash=[5, 1.6, 1, 1.6], halo=False))
    L["e_drop"] = ("Κατέβασμα μέσα σε τοίχο / ντουλάπα (τελεία) · άνοδος από το πάτωμα (σταυρός)", lambda v: D.drop(v, 0.21, 0, col=PL.WALLC, r=0.05))
    L["e_ext"] = ("Έξω: στο ταβάνι του εξώστη, μέσα στο φινίρισμα → φωτιστικά οροφής εξωστών", lambda v: D.route(v, [(0.03, 0), (0.40, 0)], col=EXTC, lw=1.0, dash=[1.2, 1.4], halo=False))


def sheet_06(no="ΗΛ-06"):
    _leg_routes()
    nh = len([h for h in CK.holes() if M.SHOW_HVAC or h["kind"] != "hvac"])
    PL._plan(_routes, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ: ΚΑΝΕΝΑ ΚΑΛΩΔΙΟ ΜΕΣΑ ΑΠΟ ΔΟΚΑΡΙ (ΜΟΝΟ ΑΠΟ ΤΙΣ %d ΟΠΕΣ)" % nh)
    y = P.legend(["e_feed", "e_trunk", "e_weakr"] + (["e_hvacr"] if M.SHOW_HVAC else []) + ["e_hole", "e_wallrun", "e_furnrun", "e_floor", "e_ext", "e_drop", "e_num"])
    rows = [[d["id"], d["title"].replace("ΣΑΛΟΝΙ – ", "ΣΑΛΟΝΙ: ").replace("ΥΠΝ.1 – ", "ΥΠΝ.1: ").replace("ΚΟΥΖΙΝΑ – ", "ΚΟΥΖ.: "), d["how"] if M.SHOW_NOTES else MODET[d["mode"]]] for d in M.DROPS]
    colors = {i: tint(MODEC[d["mode"]], 0.80) for i, d in enumerate(M.DROPS) if d["mode"] != "top"}
    y = D.table(P.PX - 4, y - 2, [14, 74, P.PW - 88 + 8], rows, head=["", "ΤΟΙΧΟΣ", "ΑΠΟ ΠΟΥ ΜΠΑΙΝΕΙ ΤΟ ΚΑΛΩΔΙΟ"], size=5.0, lead=6.0, pad=1.7, bold_first=True, colors=colors, zebra=False)
    rows = [[p["id"], p["beam"], p["title"]] for p in M.PASSES if p["new"] and (M.SHOW_HVAC or not p.get("hvac"))]
    y = D.table(P.PX - 4, y - 5, [14, 24, P.PW - 38 + 8], rows, head=["", "ΔΟΚΟΣ", "ΟΠΕΣ Ø75 (ΟΠ2 Ø90) – ΤΑ ΜΟΝΑ ΣΗΜΕΙΑ ΟΠΟΥ ΚΑΛΩΔΙΟ ΠΕΡΝΑ ΔΟΚΑΡΙ" if M.SHOW_HVAC else "ΟΠΕΣ Ø75 ΣΤΑ ΔΟΚΑΡΙΑ – ΜΟΝΟ ΑΠΟ ΕΔΩ ΠΕΡΝΑ ΚΑΛΩΔΙΟ"], size=5.0, lead=6.0, pad=1.7, bold_first=True, zebra=False)
    for s_ in (("Έλεγχος: κάθε διαδρομή, από τον κορμό ως το κουτί, ελέγχθηκε ανά 1 cm – πουθενά μέσα σε δοκάρι, κολόνα ή πλάκα.",
                "Στο πάτωμα μόνο δύο κομμάτια: τοίχος TV (14) και ΒΔ γωνία (15). Τομές: ΗΛ-14 · όψεις τοίχων: ΗΛ-15 · οπές: ΗΛ-07, ΗΛ-12.") if M.SHOW_NOTES else ()):
        y = D.para(P.PX - 2, y - 7, s_, P.PW + 4, size=5.2, color=MUTE) + 2
    assert y > 150, "ΗΛ-06: η δεξιά στήλη ξεχειλίζει (%.0f)" % y
    PL._finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΓΕΝΙΚΗ ΚΑΤΟΨΗ", ("5 οπές Ø75 (ΟΠ2 Ø90)" if M.SHOW_HVAC else "%d οπές Ø75" % nh) + " · από πού μπαίνει το καλώδιο σε κάθε τοίχο · μεγέθ. ΗΛ-07/08/09")


# ================================================================ R21: ΜΕΓΕΘΥΝΣΕΙΣ ΠΕΡΑΣΜΑΤΩΝ (ΗΛ-07 · ΗΛ-08 · ΗΛ-09)
ZOOMS = {
    "n": dict(box=(-0.30, -0.25, 10.20, 5.55), den=35, title="ΠΕΡΑΣΜΑΤΑ – ΒΟΡΕΙΑ ΖΩΝΗ: ΥΠΝΟΔΩΜΑΤΙΑ · ΛΟΥΤΡΑ · ΧΩΛ · ΠΙΝΑΚΑΣ", theme="ΠΕΡΑΣΜΑΤΑ – ΒΟΡΕΙΑ ΖΩΝΗ",
              sub="Υπν.1 · λουτρά · Υπν.2 · χωλ · πίνακας – κάθε διαδρομή ως το κουτί"),
    "liv": dict(box=(-0.85, 4.60, 9.75, 11.30), den=35, title="ΠΕΡΑΣΜΑΤΑ – ΣΑΛΟΝΙ · ΤΡΑΠΕΖΑΡΙΑ · ΕΞΩΣΤΕΣ", theme="ΠΕΡΑΣΜΑΤΑ – ΣΑΛΟΝΙ – ΕΞΩΣΤΕΣ",
                sub="Καθιστικό · δυτικός / νότιος εξώστης · ΟΠ1 / ΟΠ5 – κάθε διαδρομή ως κουτί"),
    "kit": dict(box=(7.95, 2.20, 14.10, 10.40), den=32, title="ΠΕΡΑΣΜΑΤΑ – ΚΟΥΖΙΝΑ · ΕΙΣΟΔΟΣ · ΛΩΡΙΔΑ ΚΜ1 · SHAFT", theme="ΠΕΡΑΣΜΑΤΑ – ΚΟΥΖΙΝΑ – ΕΙΣΟΔΟΣ",
                sub="Κουζίνα · τοίχος εισόδου · ΟΠ3 / ΟΠ4 · παροχή από το shaft"),
}


def _sheet_zoom(no, key):
    z = ZOOMS[key]
    _leg_routes()
    PL._plan_zoom(lambda v: _routes(v, zoom=True), z["title"], z["box"], z["den"])
    y = P.legend(["e_feed", "e_trunk", "e_hole", "e_wallrun", "e_furnrun", "e_floor", "e_ext", "e_devpath", "e_drop", "e_num"])
    x0, y0, x1, y1 = z["box"]
    inside = [d for d in M.DROPS if any(x0 <= px <= x1 and y0 <= py <= y1 for px, py in [NUM_AT[d["id"]]] + NUM_MORE.get(d["id"], []))]
    rows = [[d["id"], d["title"].replace("ΣΑΛΟΝΙ – ", "ΣΑΛΟΝΙ: ").replace("ΥΠΝ.1 – ", "ΥΠΝ.1: ").replace("ΚΟΥΖΙΝΑ – ", "ΚΟΥΖ.: "), MODET[d["mode"]]] for d in inside]
    colors = {i: tint(MODEC[d["mode"]], 0.80) for i, d in enumerate(inside) if d["mode"] != "top"}
    y = D.table(P.PX - 4, y - 2, [14, 74, P.PW - 88 + 8], rows, head=["", "ΤΟΙΧΟΣ", "ΑΠΟ ΠΟΥ ΜΠΑΙΝΕΙ ΤΟ ΚΑΛΩΔΙΟ"], size=5.0, lead=6.0, pad=1.7, bold_first=True, colors=colors, zebra=False)
    fr = [f for f in M.FLOOR_RUNS if x0 <= f["pts"][-1][0] <= x1 and y0 <= f["pts"][-1][1] <= y1]
    if fr:
        rows = [[f["id"], "%d σπιράλ: " % len(f["tubes"]) + " · ".join("Ø%d %s" % (d_, t_) for t_, d_ in f["tubes"])] for f in fr]
        y = D.table(P.PX - 4, y - 5, [22, P.PW - 22 + 8], rows, head=["", "ΣΤΟ ΠΑΤΩΜΑ (μόνο εδώ) – πάνω στην πλάκα, πριν από το γέμισμα"], size=5.0, lead=6.0, pad=1.7, bold_first=True, zebra=False)
    assert y > 120, "%s: η δεξιά στήλη ξεχειλίζει (%.0f)" % (no, y)
    PL._finish(no, z["theme"], z["sub"], "Κλίμακα 1:%d · A3" % z["den"])


def sheet_zoom_n(no="ΗΛ-07"):
    _sheet_zoom(no, "n")


def sheet_zoom_liv(no="ΗΛ-08"):
    _sheet_zoom(no, "liv")


def sheet_zoom_kit(no="ΗΛ-09"):
    _sheet_zoom(no, "kit")


# ================================================================ ΗΛ-07 ΠΕΡΑΣΜΑΤΑ – ΤΟΜΕΣ
S12 = 72 / 25.4 * 1000 / 12.5
CONC, GYP = DT.CONC, DT.GYP
BEAMF = (0.50, 0.50, 0.54)
CABLE = (0.82, 0.08, 0.10)
NORTHC = (0.10, 0.36, 0.72)
Z0 = 1.74


def _path(sc, pts, col=CABLE, lw=2.2):
    c = C(); c.saveState(); c.setLineJoin(1); c.setLineCap(1)
    P_ = [sc.p(*q) for q in pts]
    for wdt, cl in ((lw + 1.6, (1, 1, 1)), (lw, col)):
        c.setStrokeColorRGB(*cl); c.setLineWidth(wdt)
        p = c.beginPath(); p.moveTo(*P_[0])
        for q in P_[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    (x0, y0), (x1, y1) = P_[-2], P_[-1]
    P._arrow(x1, y1, math.degrees(math.atan2(y1 - y0, x1 - x0)), 3.4, col)


def ntext(sc, *a, **k):
    """Επεξηγηματικό κείμενο μέσα σε τομή – μόνο με SHOW_NOTES (R20: ετικέτες / στάθμες μένουν, προτάσεις όχι)."""
    if M.SHOW_NOTES:
        sc.text(*a, **k)


def _cap(x, y, s, sub):
    txt(x, y, s, size=7.6, font="Inter-Bold")
    ln(x, y - 3, x + SW(s, "Inter-Bold", 7.6), y - 3, lw=0.9)
    txt(x, y - 12, sub, size=5.8, color=MUTE)


def _beam(sc, h0, h1, zs, name, sec):
    sc.rect(h0, zs, h1, 2.98, fill=BEAMF)
    sc.text((h0 + h1) / 2, 2.74, name, size=6.4, font="Inter-Bold", color=(1, 1, 1), anchor="c"); sc.text((h0 + h1) / 2, 2.67, sec, size=5.4, color=(1, 1, 1), anchor="c")


def _hole_sec(sc, h0, h1, z, d=None):
    """Η οπή Ø75 (ΟΠ2: Ø90) σε τομή: χιτώνιο μέσα από το πλάτος της δοκού."""
    r = (d or M.HOLE_D) / 2
    sc.rect(h0, z - r, h1, z + r, fill=(1, 1, 1), stroke=HOLEC, lw=1.0)
    sc.line(h0 - 0.03, z, h1 + 0.03, z, col=HOLEC, lw=0.4, dash=[3, 1.2, 0.8, 1.2])


def sec_p1(x, ytop):
    """Τομή Β–Ν στην οπή ΟΠ3 (x = 5,60, βλέπουμε προς ανατολή): κενό χωλ | Δ3.1 με την οπή Ø60 στη μέση του ύψους | κενό καθιστικού."""
    _cap(x, ytop, "Π1 · ΧΩΛ ↔ ΣΑΛΟΝΙ: ΟΠ5, ΟΠ1 στη Δ3.1", "τομή Β–Ν μέσα από την οπή · 1:12,5")
    a, b = 4.38, 5.62; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.80, 4.85, 2.98, fill=CONC); sc.rect(5.15, 2.78, b, 2.98, fill=CONC); _beam(sc, 4.85, 5.15, 2.48, "Δ3.1", "30/50")
    sc.rect(a, 2.4675, 5.1625, 2.48, fill=GYP, lw=0.4)                         # R15: οροφή χωλ +2,48, περασιά με την κάτω παρειά της δοκού
    sc.rect(5.15, 2.4675, 5.1625, 2.68, fill=GYP, lw=0.4)                      # παρειά δοκού προς το σαλόνι
    sc.rect(5.15, 2.68, b, 2.6925, fill=GYP, lw=0.4)                           # οροφή σαλονιού +2,68
    _hole_sec(sc, 4.85, 5.15, 2.73)
    _path(sc, [(a + 0.03, 2.745), (4.78, 2.745), (4.86, 2.73), (5.14, 2.73), (5.22, 2.735), (b - 0.03, 2.735)], lw=1.6)
    sc.dimv(5.30, 2.73, 2.98, "25", off=4)
    sc.dimv(5.42, 2.48, 2.73, "25", off=4)
    sc.text(a + 0.02, 2.60, "ΧΩΛ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.535, "οροφή +2,48 (όλο το χωλ)" if M.SHOW_NOTES else "οροφή +2,48", size=5.2, color=MUTE)
    sc.text(b - 0.02, 2.585, "ΣΑΛΟΝΙ", size=5.8, font="Inter-Bold", anchor="r"); sc.text(b - 0.02, 2.52, "οροφή +2,68", size=5.2, color=MUTE, anchor="r")
    sc.text(5.00, 2.40, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=6.2, font="Inter-Bold", color=HOLEC, anchor="c")
    ntext(sc, 5.00, 2.335, "στη μέση του ύψους του δοκαριού", size=5.2, color=HOLEC, anchor="c")
    ntext(sc, 5.00, 2.28, "25 cm από πάνω · 25 cm από κάτω", size=5.2, color=HOLEC, anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98 άνω στάθμη πλάκας" if M.SHOW_NOTES else "+2,98", size=5.2, color=MUTE, dy=3)
    ntext(sc, a + 0.02, 2.14, "ΚΕΝΟ ΟΡΟΦΗΣ → ΚΕΝΟ ΟΡΟΦΗΣ", size=5.6, font="Inter-Bold")
    ntext(sc, a + 0.02, 2.075, "χωλ και άνοιγμα +2,48, περασιά με το δοκάρι – κανένα δόντι", size=5.2, color=MUTE)
    ntext(sc, a + 0.02, 2.02, "ΟΠ5 παροχή + ασθενή 3,10 m · ΟΠ1 ισχυρά 3,50 m από τη δυτική κολόνα", size=5.2, color=MUTE)
    if M.SHOW_HVAC:
        ntext(sc, a + 0.02, 1.965, "ΟΠ2 (κλιματιστικό σαλονιού): βλ. τομή ΚΟΥΤΕΛΟ", size=5.2, color=MUTE)


def sec_p2(x, ytop):
    """Τομή Δ–Α στην οπή ΟΠ4 (y = 7,95, βλέπουμε προς βορρά): κενό λωρίδας εισόδου | Δ9.1 με την οπή | κενό κουζίνας."""
    _cap(x, ytop, "Π2 · ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ ↔ ΚΟΥΖΙΝΑ: ΟΠ4 στη Δ9.1", "τομή Δ–Α μέσα από την οπή, πάνω από το άνοιγμα της κουζίνας · 1:12,5")
    a, b = 9.02, 10.22; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.78, 9.40, 2.98, fill=CONC); sc.rect(9.70, 2.83, b, 2.98, fill=CONC); _beam(sc, 9.40, 9.70, 2.48, "Δ9.1", "30/50")
    sc.rect(a, 2.4675, b, 2.48, fill=GYP, lw=0.4)                             # ενιαία οροφή +2,48 (λωρίδα · κάτω από το δοκάρι · κουζίνα)
    _hole_sec(sc, 9.40, 9.70, 2.73)
    _path(sc, [(a + 0.03, 2.62), (9.26, 2.62), (9.37, 2.73), (9.72, 2.73), (9.83, 2.66), (b - 0.03, 2.66)], lw=1.6)
    sc.dimv(9.88, 2.73, 2.98, "25", off=4)
    sc.text(a + 0.02, 2.56, "ΛΩΡΙΔΑ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.505, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold")
    sc.text(b - 0.02, 2.56, "ΚΟΥΖΙΝΑ", size=5.8, font="Inter-Bold", anchor="r")
    sc.text(a + 0.02, 2.42, "οροφή +2,48 περασιά με το δοκάρι" if M.SHOW_NOTES else "οροφή +2,48", size=5.2, color=MUTE)
    sc.text(9.55, 2.36, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=6.2, font="Inter-Bold", color=HOLEC, anchor="c")
    ntext(sc, 9.55, 2.295, "στη μέση του ύψους του δοκαριού", size=5.2, color=HOLEC, anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98", size=5.2, color=MUTE, dy=3)
    ntext(sc, a + 0.02, 2.14, "ΠΑΝΩ ΑΠΟ ΤΟ ΑΝΟΙΓΜΑ ΤΗΣ ΚΟΥΖΙΝΑΣ", size=5.6, font="Inter-Bold")
    ntext(sc, a + 0.02, 2.075, "ΟΠ4: 1,20 m από την παρειά της κολόνας Κ8 (νότια)", size=5.2, color=MUTE)
    ntext(sc, a + 0.02, 2.02, "= 20 cm από το τέλος του τοίχου κουζίνας – σκάλας", size=5.2, color=MUTE)
    ntext(sc, a + 0.02, 1.965, "στη μέση του μήκους του δοκαριού από πίσω είναι η σκάλα", size=5.2, color=MUTE)


def sec_p0(x, ytop):
    """Τομή Δ–Α στην οπή ΟΠ3 (y = 5,95, πάνω από την πόρτα εισόδου, βλέπουμε προς βορρά): λωρίδα | τοίχος Τ6Α 15 cm κάτω από τη Δ9.1 | ψευδοδοκός κλιμακοστασίου."""
    _cap(x, ytop, "Π0 · SHAFT → ΔΙΑΜΕΡΙΣΜΑ: ΟΠ3 στη Δ9.1", "τομή Δ–Α πάνω από την πόρτα εισόδου · 1:12,5")
    a, b = 9.02, 10.22; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.78, 9.40, 2.98, fill=CONC); sc.rect(9.70, 2.83, b, 2.98, fill=CONC); _beam(sc, 9.40, 9.70, 2.48, "Δ9.1", "30/50")
    sc.rect(a, 2.4675, 9.40, 2.48, fill=GYP, lw=0.4)                         # οροφή λωρίδας +2,48 περασιά με το δοκάρι
    sc.rect(9.55, 2.43, 9.95, 2.4425, fill=GYP, lw=0.4); sc.rect(9.95, 2.43, 9.9625, 2.73, fill=GYP, lw=0.4); sc.rect(9.95, 2.73, b, 2.7425, fill=GYP, lw=0.4)   # ψευδοδοκός + οροφή κλιμακοστασίου
    sc.rect(9.40, 2.25, 9.425, 2.48, fill=GYP, lw=0.4); sc.rect(9.525, 2.25, 9.55, 2.43, fill=GYP, lw=0.4)
    sc.rect(9.425, 2.25, 9.525, 2.48, fill=(1, 1, 1), stroke=MUTE, lw=0.4, dash=[1.5, 1.2])
    sc.rect(9.40, 2.20, 9.55, 2.25, fill=(0.30, 0.30, 0.34), lw=0.4)          # κάσα
    sc.line(9.40, Z0, 9.40, 2.20, col=MUTE, lw=0.5, dash=[2, 1.5]); sc.line(9.55, Z0, 9.55, 2.20, col=MUTE, lw=0.5, dash=[2, 1.5])
    _hole_sec(sc, 9.40, 9.70, 2.73)
    _path(sc, [(b - 0.03, 2.60), (9.84, 2.60), (9.73, 2.73), (9.37, 2.73), (9.26, 2.62), (a + 0.03, 2.62)], lw=1.6)
    sc.text(9.475, 2.02, "ΠΟΡΤΑ", size=5.8, font="Inter-Bold", anchor="c"); sc.text(9.475, 1.955, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold", anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98", size=5.2, color=MUTE, dy=3)
    sc.text(a + 0.02, 2.42, "οροφή λωρίδας +2,48", size=5.2, color=MUTE)
    sc.text(a + 0.02, 2.27, "ΛΩΡΙΔΑ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.205, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold")
    ntext(sc, a + 0.02, 2.10, "τοίχος πόρτας 15 cm,", size=5.2, color=MUTE); ntext(sc, a + 0.02, 2.045, "περασιά με το δοκάρι", size=5.2, color=MUTE)
    sc.text(9.62, 2.365, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=5.6, font="Inter-Bold", color=HOLEC)
    sc.text(9.62, 2.27, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=5.8, font="Inter-Bold"); sc.text(9.62, 2.21, "ψευδοδοκός καλωδίων +2,43", size=5.2, color=MUTE); ntext(sc, 9.62, 2.155, "από το shaft Η/Μ", size=5.2, color=MUTE)
    ntext(sc, 9.62, 2.10, "σφράγιση με πυράντοχη μαστίχη", size=5.2, color=MUTE)
    sc.text(b - 0.01, 2.685, "οροφή +2,73", size=5.0, color=MUTE, anchor="r")


def det_panel(x, ytop):
    """Κάτοψη 1:10 του πίνακα μέσα στον τοίχο Τ2Α-01 (ανατολή = χωλ πάνω): 2 γυψ. + CW 100 + 2 γυψ. = 15 cm."""
    _cap(x, ytop, "Ο ΠΙΝΑΚΑΣ ΣΤΟΝ ΤΟΙΧΟ ΤΟΥ ΛΟΥΤΡΟΥ ΓΟΝΕΩΝ", "κάτοψη του τοίχου · 1:12,5 · πάνω το χωλ, κάτω το λουτρό")
    s = S12
    wb = W.bbox([w for w in W.WALLS if w["id"] == M.PANEL_WALL][0]["pts"])
    xw, xe = wb[0], wb[2]
    sc = Sec(x + 14, ytop - 106, s, 3.30, xw - 0.08)       # h = y (Β → Ν), z = x (Δ → Α)
    y0w, y1w = 3.50, 4.35
    sc.rect(3.35, xw, y0w, xe, fill=tint(GYP, 0.4), stroke=MUTE, lw=0.3)            # άκρο του Τ7-02 (σχηματικά)
    sc.rect(y0w, xe - 0.025, y1w, xe, fill=GYP, lw=0.4)                          # 2 γυψ. προς το χωλ
    sc.rect(y0w, xw + 0.025, y1w, xe - 0.025, fill=(1, 1, 1), stroke=MUTE, lw=0.4, dash=[1.5, 1.2])     # CW 100
    sc.rect(y0w, xw, y1w, xw + 0.025, fill=(0.80, 0.90, 0.86), lw=0.4)            # 2 ανθυγρές προς το λουτρό
    sc.rect(y0w, xw - 0.012, y1w, xw, fill=(0.62, 0.70, 0.76), lw=0.3)            # πλακάκι
    for yy in (y0w, M.PANEL["y0"] - 0.045, M.PANEL["y1"] + 0.005):
        sc.rect(yy, xw + 0.025, yy + 0.04, xe - 0.025, fill=(0.80, 0.82, 0.86), lw=0.3)
    sc.rect(M.PANEL["y0"], xe - M.PANEL_DEPTH, M.PANEL["y1"], xe, fill=tint(FEED, 0.55), stroke=FEED, lw=1.0)
    sc.rect(M.PANEL["y0"] - 0.02, xe, M.PANEL["y1"] + 0.02, xe + 0.02, fill=FEED, lw=0.4)      # πλαίσιο – πόρτα
    sc.text((M.PANEL["y0"] + M.PANEL["y1"]) / 2, xe - 0.04, "ΓΠ", size=7.0, font="Inter-Bold", color=(1, 1, 1), anchor="c", dy=-2)
    if M.SHOW_HVAC:
        sc.rect(M.KM2_DROP_NEW - 0.016, xw + 0.05, M.KM2_DROP_NEW + 0.016, xw + 0.082, fill=(0.86, 0.50, 0.90), lw=0.4)     # συμπυκνώματα ΚΜ2 – νέα θέση
    sc.text((y0w + y1w) / 2, xe + 0.075, "ΧΩΛ – δυτικό άκρο" if M.SHOW_NOTES else "ΧΩΛ", size=5.8, font="Inter-Bold", anchor="c")
    sc.text((y0w + y1w) / 2, xw - 0.03, "ΛΟΥΤΡΟ ΓΟΝΕΩΝ (πλακάκι)" if M.SHOW_NOTES else "ΛΟΥΤΡΟ ΓΟΝΕΩΝ", size=5.8, font="Inter-Bold", anchor="c", dy=-10)
    sc.dimh(M.PANEL["y0"], M.PANEL["y1"], xe + 0.03, "άνοιγμα 52 cm", off=3)
    sc.dimh(y0w, M.PANEL["y0"], xe + 0.03, "9", off=3)
    sc.dimv(3.31, xe - 0.07, xe, "7", off=-4)
    ntext(sc, (y0w + y1w) / 2, xw - 0.03, "πίνακας 7 cm (ή 9) · μέσα στον τοίχο 12,5 cm", size=5.4, color=MUTE, anchor="c", dy=-22)
    if M.SHOW_HVAC:
        ntext(sc, (y0w + y1w) / 2, xw - 0.03, "μοβ: συμπυκνώματα split Υπν.1 – ΝΕΑ θέση", size=5.4, color=MUTE, anchor="c", dy=-31)


def sec_t4(x, ytop):
    """Τομή Β–Ν στον τοίχο της TV, ΧΑΜΗΛΑ (R13): σπιράλ πάνω στην πλάκα μέσα στο γέμισμα → πάνω μέσα στο κενό της επένδυσης Τ3-08."""
    _cap(x, ytop, "Δ-TV · ΤΟΙΧΟΣ TV: ΑΠΟ ΤΟ ΠΑΤΩΜΑ", "τομή Β–Ν χαμηλά · 1:12,5 · πριν από το γέμισμα")
    fr = [q for q in M.FLOOR_RUNS if q["id"] == "Δ-TV"][0]
    wb = W.bbox([w for w in W.WALLS if w["id"] == fr["wall"]][0]["pts"]); bk = W.bbox([w for w in W.WALLS if w["id"] == "T1-09"][0]["pts"])
    f0, f1 = wb[1], wb[3]; t = M.SCREED
    a, z0 = 8.47, -0.26; sc = Sec(x, ytop - 196, S12, a, z0)
    sc.rect(a, -t - 0.14, bk[3], -t, fill=CONC)                                       # πλάκα
    sc.rect(a, -t, f0, 0, fill=(0.94, 0.92, 0.86), lw=0.4)                            # γέμισμα
    sc.rect(a, -t + 0.03, f0, -t + 0.06, fill=(1.0, 0.95, 0.70), lw=0.3)              # μόνωση ενδοδαπέδιας πάνω από τα σπιράλ
    sc.rect(bk[1], -t, bk[3], 0.60, fill=(0.88, 0.76, 0.68), lw=0.4)                   # τούβλο
    sc.rect(f0, -t, f1, 0.60, fill=(1, 1, 1), lw=0.4); sc.rect(f0, 0, f0 + 0.025, 0.60, fill=GYP, lw=0.4)
    hc = (f0 + 0.025 + f1) / 2
    _path(sc, [(a + 0.02, -t + 0.014), (hc - 0.03, -t + 0.014), (hc, -t + 0.05), (hc, M.H_TV)], lw=1.6)
    sc.rect(f0 - 0.004, M.H_TV - 0.035, f0 + 0.045, M.H_TV + 0.035, fill=(1, 1, 1), stroke=PWR, lw=0.9)
    _path(sc, [(hc, 0.30), (hc, 0.50), (bk[3] - 0.02, 0.50)], lw=1.0)
    sc.dimv(a + 0.10, -t, 0, "12", off=0)
    sc.text(a + 0.16, -0.035, "γέμισμα · ενδοδαπέδια" if M.SHOW_HVAC else "γέμισμα", size=5.0, color=MUTE)
    sc.text(a + 0.02, -t - 0.075, "πλάκα", size=5.0, color=(1, 1, 1))
    sc.text(f0 - 0.03, M.H_TV + 0.05, "πρίζες TV +0,45", size=5.0, font="Inter-SemiBold", anchor="r")
    sc.text(bk[3] + 0.02, 0.49, "Π60", size=5.0, font="Inter-SemiBold")
    for zz, s_ in (((0.34, "1  κατέβασμα μέσα στη ντουλάπα του χωλ"), (0.30, "2  3 σπιράλ Ø25 ΠΑΝΩ ΣΤΗΝ ΠΛΑΚΑ, 5,7 m"),
                    (0.26, "    κάτω από τη μόνωση της ενδοδαπέδιας"), (0.22, "3  πάνω, μέσα στο κενό της επένδυσης"),
                    (0.18, "4  πρίζα εξώστη Π60: τρύπα στο τούβλο")) if M.SHOW_NOTES else ()):
        sc.text(a + 0.02, zz, s_, size=5.0, color=HOLEC if "ΠΛΑΚΑ" in s_ else INK, font="Inter-Bold" if "ΠΛΑΚΑ" in s_ else "Inter")


def _what(t):
    """«Τι περνά» χωρίς τα στοιχεία κλιματισμού / ενδοδαπέδιας (R20)."""
    if M.SHOW_HVAC:
        return t
    bad = ("θερμοστάτ", "χειριστήριο", "εντολές", "ΑΘ", "ΚΛ", "ζωνών", "ΑΚ")
    return " · ".join(q for q in t.split(" · ") if not any(q.strip().startswith(k) or k in q for k in bad))


def sheet_07(no="ΗΛ-07"):
    y = DC.title("ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "5 οπές με χιτώνιο Ø75 (ΟΠ2 Ø90) σε δύο δοκάρια (3 + 2) · κανένας σωλήνας μέσα στην πλάκα · χωλ +2,48 · κούτελο στο Υπν.2 (ΗΛ-16) · ο τοίχος της TV από το πάτωμα")
    X0 = DC.X0
    xs = [X0, X0 + 283, X0 + 573, X0 + 863]
    sec_p1(xs[0], y); sec_p2(xs[1], y); sec_p0(xs[2], y); det_panel(xs[3], y); sec_t4(xs[3], y - 146)
    yb = y - 350
    ln(X0, yb + 6, DC.X1, yb + 6, col=FAINT, lw=0.5)
    w = 265
    f = [DC.Flow(xs[i], yb, w, size=6.2, name="ΗΛ-07/%d" % i) for i in range(4)]
    B = dict(bullet="•", size=6.2)
    f[0].h("ΔΟΚΑΡΙ ΣΑΛΟΝΙΟΥ (Δ3.1) – ΟΠ5, ΟΠ1, ΟΠ2", fill=HOLEC)
    f[0].p("Χιτώνιο PVC Ø75 στο καλούπι, κέντρο στη μέση του ύψους του δοκαριού (25 cm κάτω από την άνω στάθμη της πλάκας).", **B)
    f[0].p("ΟΠ5 (3,10 m από τη δυτική κολόνα): κεντρική παροχή + boiler και όλα τα ασθενή σε δικό τους σπιράλ Ø40. ΟΠ1 (3,50 m): όλα τα ισχυρά σαλονιού και κουζίνας.", **B)
    f[0].p("ΟΠ2, 0,80 m από την κολόνα Κ3: η αποχέτευση Ø32 του κλιματιστικού σαλονιού ψηλά στο χιτώνιο + τα ψυκτικά του (αερίου Ø34 με μόνωση 9 mm + υγρού Ø24).", **B)
    f[0].p("ΚΟΥΤΕΛΟ δίπλα στο δοκάρι, στο Υπν.2: κενό 15 × 32 cm, κάτω παρειά +2,48. Μέσα του η αποχέτευση τρέχει με 2,6 % ως το χωλ και πέφτει στο σιφώνι του πλυντηρίου (ΗΛ-16).", **B)
    f[0].p("Όλο το χωλ στο +2,48: τα στόμια των χιτωνίων είναι ολόκληρα μέσα στο κενό.", **B)
    f[1].h("ΔΟΚΑΡΙ ΚΟΥΖΙΝΑΣ (Δ9.1) – ΟΠ4", fill=HOLEC)
    f[1].p("Πάνω από το άνοιγμα της κουζίνας, 1,20 m από την κολόνα Κ8. Από το κενό της λωρίδας ίσια στο κενό της κουζίνας.", **B)
    f[1].p("Ισχυρά κουζίνας και τοίχου εισόδου· τα 5 ασθενή μέσα σε δικό τους σπιράλ Ø20, στο ίδιο χιτώνιο.", **B)
    f[1].p("Ο τοίχος της εισόδου είναι κάτω από το δοκάρι, περασιά: οι διακόπτες και η πρίζα του παίρνουν ρεύμα από το ταβάνι της κουζίνας, μέσα από τον τοίχο κουζίνας – σκάλας, οριζόντια στο +2,30 (τομές 11 / 12 στο ΗΛ-14, όψη στο ΗΛ-15).", **B)
    f[1].p("Μέσα στο χιτώνιο τα ισχυρά περνούν με τον μανδύα τους, χωρίς σπιράλ· το σπιράλ τους σταματά πριν και ξαναρχίζει μετά.", **B)
    f[2].h("ΔΟΚΑΡΙ ΕΙΣΟΔΟΥ (Δ9.1) – ΟΠ3", fill=HOLEC)
    f[2].p("Πάνω από την πόρτα εισόδου, 0,80 m από την κολόνα Κ3. Από τον ψευδοδοκό του κλιμακοστασίου ίσια στο κενό της λωρίδας.", **B)
    f[2].p("Κεντρική παροχή 5×16 + boiler· τα ασθενή του shaft (ίνα, κεραία, μπουτονιέρα, πυρανίχνευση) μέσα σε δικό τους σπιράλ Ø25, στο ίδιο χιτώνιο.", **B)
    f[2].p("Ο τοίχος της πόρτας ξαναγίνεται 15 cm, περασιά με το δοκάρι – το κανάλι του καταργείται. Τίποτα δεν περνά πια κάτω από το δοκάρι.", **B)
    f[2].p("Είναι τοίχος προς το κλιμακοστάσιο: το χιτώνιο σφραγίζεται με πυράντοχη μαστίχη και τα κουτιά μέσα στον τοίχο είναι πυράντοχα (Ε9).", **B)
    f[3].h("ΠΙΝΑΚΑΣ", fill=FEED)
    f[3].p("Στο δυτικό άκρο του χωλ, στον τοίχο προς το λουτρό γονέων (15 cm: 2 γυψοσανίδες + σκελετός 10 cm + 2 ανθυγρές). Κεντραρισμένος στον άξονα του χωλ.", **B)
    f[3].p("Μέσα στον τοίχο υπάρχουν 12,5 cm: χωρά ολόκληρος και ο πίνακας των 7 cm και ο συνηθισμένος των 9 cm. Τα φύλλα και το πλακάκι του λουτρού δεν αγγίζονται.", **B)
    f[3].p("Γύρω από το άνοιγμα πλαίσιο από προφίλ UA. Το κατέβασμα των συμπυκνωμάτων του split του Υπν.1, που είναι στον ίδιο τοίχο, πάει 30 cm νοτιότερα (Ε3).", **B)
    f[3].p("Όλα μπαίνουν και βγαίνουν από ΠΑΝΩ: τα σπιράλ ανεβαίνουν μέσα στον τοίχο στο κενό του χωλ, προς όλες τις κατευθύνσεις.", **B)
    yc = min(q.y for q in f) - 10
    hp = [p for p in M.PASSES if p["new"] and (M.SHOW_HVAC or not p.get("hvac"))]
    rows = [[p["id"], p["beam"], p["title"], p["how"] + ".", _what(p["what"]), p["n"]] for p in hp]
    rows += [["τοίχος " + d["id"], "τοίχος", d["title"], d["txt"], _what(d.get("what", "")), "—"] for d in M.DROPS if d["mode"] in ("via", "back", "furn", "side") or d["id"] == "7"]
    rows += [[r["id"], "ΠΑΤΩΜΑ", "τοίχος %s · %s" % (r["grp"], r["short"].split(":")[0]), r["short"].split(": ", 1)[-1] + ".", _what(r["what"]), " + ".join("Ø%d" % t[1] for t in r["tubes"])] for r in M.FLOOR_RUNS]
    colors = {i: (1.0, 0.93, 0.80) for i, p in enumerate(hp)}
    widths = [42, 40, 150, 470, 290, 88]; head = ["", "ΔΟΚΟΣ", "ΑΠΟ ↔ ΠΡΟΣ / ΤΟΙΧΟΣ", "ΠΩΣ ΠΕΡΝΟΥΝ", "ΤΙ ΠΕΡΝΑ", "ΣΩΛΗΝΕΣ"]
    if not M.SHOW_NOTES:                                        # R20: η στήλη «ΠΩΣ ΠΕΡΝΟΥΝ» είναι κείμενο – μένουν τα δεδομένα
        rows = [r_[:3] + r_[4:] for r_ in rows]; widths = [42, 40, 190, 420, 100]; head = head[:3] + head[4:]
    sc_ = (DC.X1 - X0) / float(sum(widths))
    yy = D.table(X0, yc, [w_ * sc_ for w_ in widths], rows, head=head, size=5.3, lead=6.2, pad=1.6, bold_first=True, colors=colors, zebra=False)
    assert yy >= DC.YB - 2, "ΗΛ-07: ο πίνακας περασμάτων ξεχειλίζει %.0f pt" % (DC.YB - yy)
    DC.finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "Οπές Ø75: Π1 χωλ ↔ σαλόνι · Π2 κουζίνα · Π0 shaft · ο πίνακας στον τοίχο", "Τομές και κάτοψη τοίχου 1:12,5 · A3")


# ================================================================ ΗΛ-08 ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ – ΔΙΚΤΥΟ – ΣΥΝΑΓΕΡΜΟΣ – ΠΥΡΑΝΙΧΝΕΥΣΗ – ΘΕΡΜΟΣΤΑΤΕΣ
LOOPS = [("Κ1", (1.705, 5.15, 6.20, 9.115), "Θ1"), ("Κ2", (6.20, 5.15, 9.40, 9.0946), "Θ1"), ("Κ3", (9.70, 7.75, 13.76, 10.06), "Θ1"), ("Κ4", (6.50, 1.35, 9.395, 5.05), "Θ3"),
         ("Κ5", (5.05, 0.80, 6.40, 3.25), "Θ4"), ("Κ6", (1.135, 0.165, 4.20, 3.25), "Θ2"), ("Κ7", (0.11, 3.50, 3.15, 5.05), "Θ5")]
ZCOL = {"Θ1": (0.95, 0.55, 0.15), "Θ2": (0.20, 0.55, 0.85), "Θ3": (0.25, 0.65, 0.35), "Θ4": (0.65, 0.35, 0.75), "Θ5": (0.85, 0.30, 0.45)}
LOOP_TAG = {"Κ1": (3.20, 7.60), "Κ2": (7.60, 7.95), "Κ3": (11.30, 9.05), "Κ4": (8.30, 3.20), "Κ5": (5.90, 1.80), "Κ6": (2.40, 2.30), "Κ7": (1.75, 4.30)}
WEAK_AT = {"Θ4": (-0.36, 0.14), "Θ5": (0.42, -0.36), "D2": (0.10, 0.26), "Χ1": (0.26, 0.26), "Θ1": (-0.26, 0.26), "ΚΟ": (0.44, 0.10), "ΦΕ": (0.44, -0.06), "ΘΤ": (-0.80, -0.04), "ΠΛ": (-0.80, 0.14), "Θ2": (0.36, -0.22),
           "TV1": (0.20, -0.26), "D1": (-0.22, -0.26), "TV2": (0.26, -0.26), "D3": (-0.22, -0.26), "TV3": (0.26, -0.26), "D5": (-0.20, -0.26)}


CONTACT_AT = {"ΜΕ1": (-0.20, 0.02), "ΜΕ2": (-0.22, 0.10), "ΜΕ3": (0.0, -0.16), "ΜΕ4": (0.22, 0.02), "ΜΕ5": (-0.24, -0.02)}


def sheet_08(no="ΗΛ-08"):
    det = {d[0]: (d[2], d[3]) for d in A.DETECTORS}
    def fn(v):
        for k, r, th in (LOOPS if M.SHOW_HVAC else []):
            D.zone(v, r, ZCOL[th], alpha=0.10, stroke=False)
            X, Y = v.p(*LOOP_TAG[k]); P.pill(X, Y, k, th, ZCOL[th], "c", 5.6)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        wk = [r_ for r_ in M.ROUTES if r_["id"] == "ΑΣΘΕΝΗ"][0]["pts"]
        D.route(v, wk, col=DAT, lw=1.8, arrows=True, lab="από το shaft: οπτική ίνα · κεραία TV · θυροτηλεόραση (ΟΠ3 → ΟΠ5)" if M.SHOW_NOTES else "ασθενή από το shaft", seg=max(range(len(wk) - 1), key=lambda i_: abs(wk[i_ + 1][0] - wk[i_][0])), side=-1)
        _holes(v, labels=False)
        PL.detectors(v, labels=True)
        D.ceil_dev(v, 4.45, 3.85, "Σ", col=FIR, r=0.085, fill=True)
        PL.thermostats(v)
        PL.data(v)
        D.cabinet(v, M.ALARM_PANEL, col=ALARMC)
        for c_ in M.CONTACTS:                               # μαγνητικές επαφές: το άκρο της προεγκατάστασης μέσα στην παραστάδα (διαδρομές: ΗΛ-06)
            v.circle(c_[2], c_[3], 0.05, fill=ALARMC, stroke=(1, 1, 1), lw=0.6)
            dx, dy = CONTACT_AT.get(c_[0], (0.18, 0.0))
            D.halo_text(v, c_[2] + dx, c_[3] + dy, c_[0], size=4.0, color=ALARMC)
        pts = []
        for d in M.DATA:
            tag(v, d[1], d[2], d[3], "%s · %s" % (d[0], fz(d[5])), DAT, off=0.26, at=WEAK_AT.get(d[0])); pts.append((d[1], d[2], d[3]))
        for t in M.TV:
            tag(v, t[1], t[2], t[3], "%s · %s" % (t[0], fz(t[4])), DAT, off=0.26, at=WEAK_AT.get(t[0])); pts.append((t[1], t[2], t[3]))
        for t in (M.THERMOSTATS if M.SHOW_HVAC else []):
            tag(v, t[1], t[2], t[3], "%s · %s" % (t[0], fz(M.H_TH)), AUT, off=0.28, at=WEAK_AT.get(t[0]))
            if not PL._opt(t, 7).get("off"):
                pts.append((t[1], t[2], t[3]))
        if M.SHOW_HVAC:
            a = M.AC_CTRL
            tag(v, a[1], a[2], a[3], "%s · %s" % (a[0], fz(M.H_TH)), HVC, at=WEAK_AT.get(a[0])); pts.append((a[1], a[2], a[3]))
        for d in M.WALL_DEV:
            cc = {"data": DAT, "alarm": ALARMC, "fire": FIR}[d[6]]
            tag(v, d[1], d[2], d[3], "%s · %s" % (d[0], fz(d[5])), cc, at=WEAK_AT.get(d[0]))
            if d[3] == "W":
                pts.append((d[1], d[2], d[3]))
        for m in M.MOTION:
            D.halo_text(v, m[1], m[2] - 0.20, m[0], size=4.2, color=ALARMC)
        dims(v, pts, off=0.46)
        PL.panel(v)
        D.halo_text(v, 4.28, 4.62, "ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ ▸", size=4.8, color=DAT, font="Inter-Bold")
    PL._plan(fn, "ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ · ETHERNET · TV · ΣΥΝΑΓΕΡΜΟΣ · ΠΥΡΑΝΙΧΝΕΥΣΗ" + (" · ΘΕΡΜΟΣΤΑΤΕΣ" if M.SHOW_HVAC else ""))
    y = P.legend(["e_tn", "e_cab", "e_data", "e_data2", "e_tv", "e_wdev", "e_alarm", "e_contact", "e_det", "e_heat", "e_siren"] + (["e_th", "e_man", "e_loop"] if M.SHOW_HVAC else []))
    rows = [["Modem – router", "του παρόχου, με Wi-Fi· η οπτική ίνα έρχεται ως εδώ. Στη μέση της κάτοψης → καλύπτει όλο το σπίτι"],
            ["Δίκτυο", "πλαίσιο 12 θυρών Cat 6A + switch 8 θυρών· κάθε λήψη τοίχου έχει δικό της καλώδιο ως εδώ (αστέρας)"],
            ["TV", "διανομή κεραίας / δορυφορικής προς 3 λήψεις"],
            ["Συναγερμός – πυρανίχνευση", "πίνακας ΠΣ με μπαταρία· πληκτρολόγιο στην είσοδο, επαφές σε πόρτα και 4 κουφώματα, ανιχνευτής κίνησης"],
            ["Ρεύμα", "2 διπλοί ρευματοδότες στο κύκλωμα ΚΑ + κύκλωμα ΣΠ για τον πίνακα συναγερμού"],
            ["Κατασκευή", "το ανατολικό 0,50 m της ντουλάπας του χωλ με δική του πόρτα και περσίδα αερισμού"]]
    if M.SHOW_NOTES:
        y = D.table(P.PX - 4, y - 2, [58, P.PW - 58 + 8], rows, head=["ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ – ΤΙ ΕΧΕΙ ΜΕΣΑ", ""], size=5.1, lead=6.2, pad=1.8, bold_first=True)
    rows = [[d[0], "%d × RJ45" % d[4], fz(d[5]), ref_txt(d[1], d[2], d[3]), d[7].split(" (")[0]] for d in M.DATA]
    rows += [[t[0], "TV", fz(t[4]), ref_txt(t[1], t[2], t[3]), "κεραία / δορυφορική"] for t in M.TV]
    rows += [[d[0], {"data": "RJ45", "alarm": "δίαυλος", "fire": "2×1,5"}[d[6]] if d[0] != "ΚΟ" else "2×0,8", fz(d[5]), ref_txt(d[1], d[2], d[3]) if d[3] == "W" else "πλατύσκ.", d[7].split(" (")[0].split(" – ")[0]] for d in M.WALL_DEV]
    rows += [[t[0], "θερμοστ.", fz(M.H_TH), ref_txt(t[1], t[2], t[3]), "%s → %s" % (t[4].replace("ΚΑΘ", "καθιστικό – κουζίνα").replace("ΥΠ1", "Υπν.1").replace("ΥΠ2", "Υπν.2").replace("ΧΩΛ", "λουτρό") if t[0] != "Θ5" else "λουτρό γονέων", " · ".join(t[5]))] for t in (M.THERMOSTATS if M.SHOW_HVAC else [])]
    y = D.table(P.PX - 4, y - 5, [20, 34, 22, 40, P.PW - 116 + 8], rows, head=["", "ΛΗΨΗ", "ΥΨΟΣ", "ΑΠΟ", "ΧΡΗΣΗ"], size=5.0, lead=6.0, pad=1.5, bold_first=True, aligns={2: "r"})
    rows = [["Πυρανίχνευση", "4 ανιχνευτές καπνού (καθιστικό, Υπν.1, Υπν.2, χωλ) + 1 θερμοδιαφορικός στην κουζίνα – θέσεις των ανόψεων· σειρήνα στο χωλ, επαναλήπτης στο πλατύσκαλο"],
            ["Θερμοστάτες", "5 ζώνες: κάθε θερμοστάτης ανοίγει / κλείνει ΜΟΝΟ τα κυκλώματα της ζώνης του μέσω του κέντρου ζωνών στον συλλέκτη (7 κινητήρες)· των λουτρών έξω από την πόρτα, με αισθητήριο δαπέδου"],
            ["Χωρίς KNX", "συμβατική καλωδίωση· ό,τι «έξυπνο» χρειαστεί (θερμοστάτες, συναγερμός) δουλεύει μέσω του modem"]]
    if M.SHOW_NOTES:
        D.table(P.PX - 4, y - 5, [48, P.PW - 48 + 8], rows, size=5.0, lead=6.0, pad=1.6, bold_first=True)
    PL._finish(no, "ΑΣΘΕΝΗ ΡΕΥΜΑΤΑ – ΘΕΡΜΟΣΤΑΤΕΣ" if M.SHOW_HVAC else "ΑΣΘΕΝΗ ΡΕΥΜΑΤΑ", "Κέντρο ασθενών · Ethernet σε κάθε δωμάτιο · συναγερμός · πυρανίχνευση")


# ================================================================ ΗΛ-00 ΣΥΝΟΨΗ
SHEETS = [("ΗΛ-00", "Σύνοψη: τι άλλαξε, τι χρειάζεται απόφαση"), ("ΗΛ-01", "Ηλεκτρικός πίνακας και ζώνες κυκλωμάτων"), ("ΗΛ-02", "Ρευματοδότες – ύψη και αποστάσεις"),
          ("ΗΛ-03", "Διακόπτες – ύψη, αποστάσεις, τι ανάβει ο καθένας"), ("ΗΛ-04", "Φωτισμός – κάτοψη"), ("ΗΛ-05", "Φωτισμός – τεκμηρίωση και φωτιστικά"),
          ("ΗΛ-06", "Περάσματα καλωδίων – κάτοψη"), ("ΗΛ-07", "Περάσματα καλωδίων – τομές · ο πίνακας στον τοίχο"),
          ("ΗΛ-08", "Κέντρο ασθενών · Ethernet · συναγερμός · πυρανίχνευση · θερμοστάτες"), ("ΗΛ-09", "Μονογραμμικό σχέδιο – όψη πίνακα"), ("ΗΛ-10", "Πίνακας κυκλωμάτων και προστασιών"),
          ("ΗΛ-11", "Υπόγειο: μετρητής → πίνακας αποθήκης → φορτιστής και παροχή σπιτιού"),
          ("ΗΛ-12", "ΣΩΛΗΝΩΣΕΙΣ ορόφου: οι 5 οπές Ø75 (ΟΠ2 Ø90) – θέση και τι περνά από καθεμία · λοιπά περάσματα"), ("ΗΛ-13", "Κατακόρυφο διάγραμμα οικοδομής: shaft, παροχές, ασθενή"), ("ΗΛ-14", "ΚΑΤΕΒΑΣΜΑΤΑ στους τοίχους: τομή σε κάθε τοίχο με πρίζες / διακόπτες – από πού μπαίνουν τα καλώδια"),
          ("ΗΛ-15", "ΟΨΕΙΣ των τοίχων που είναι κάτω από δοκάρια: πού περνά το καλώδιο μέσα στον τοίχο"),
          ("ΗΛ-16", "ΚΟΥΤΕΛΟ δίπλα στο δοκάρι του σαλονιού · χωλ +2,48 · αποχέτευση κλιματιστικού από την ΟΠ2 ως το πλυντήριο")]


def sheet_00(no="ΗΛ-00"):
    y = DC.title("ΗΛΕΚΤΡΟΛΟΓΙΚΗ ΜΕΛΕΤΗ – Β1 (Α΄ · Β΄ · Γ΄ ΟΡΟΦΟΣ) – %s" % M.REV, "τελικό σχέδιο προς έγκριση · τι άλλαξε με τις οδηγίες της 19–20/11 (R02 – R17) · τι χρειάζεται απόφαση")
    a, b, c_ = DC.cols(3, y, name="ΗΛ-00")
    n = CK.counts(); F = CK.feeder_calc()
    B = dict(size=7.7)
    a.h("ΤΙ ΑΛΛΑΞΕ ΜΕ ΤΙΣ ΟΔΗΓΙΕΣ ΤΗΣ 19/11")
    a.p("Κανονικός, συμμετρικός κάναβος σε κάθε χώρο: καθιστικό 4 × 3, υπνοδωμάτια 2 × 2. Καμία ράγα, κανένα κρεμαστό, καμία απλίκα. Στα λουτρά καθρέπτες με φως. "
        "Στους εξώστες τα φωτιστικά οροφής των προοπτικών (ΗΛ-04, ΗΛ-05).", bold="1 · Φωτισμός μόνο με spots.", **B)
    a.p("Τα 4 spots συμμετρικά στους άξονες του δωματίου – όχι ένα πάνω από το γραφείο.", bold="2 · Υπνοδωμάτιο 2.", **B)
    a.p("Ο βόρειος τοίχος του σαλονιού μένει όπως είναι στις τοιχοποιίες, περασιά με το δοκάρι. Το κανάλι του R01 καταργήθηκε· καμία αλλαγή τοιχοποιίας.", bold="3 · Τοίχος χωρίς +5,5 cm.", **B)
    a.p("Στο δυτικό άκρο του χωλ, στον τοίχο του λουτρού γονέων (12,5 cm διαθέσιμα μέσα στον τοίχο). Λεπτομέρεια: ΗΛ-07.", bold="4 · Πίνακας.", **B)
    a.p("Στα μεγάλα αλουμίνια του σαλονιού κανένα ρολό. Ηλεκτρικά ρολά στις δύο μπαλκονόπορτες των υπνοδωματίων (R17).", bold="5 · Ρολά μόνο στα υπνοδωμάτια.", **B)
    a.p("Εστίες με τριφασική γραμμή 5×2,5.", bold="6 · Τριφασικές εστίες.", **B)
    a.h("ΑΠΟ ΤΟ R01 ΜΕΝΟΥΝ")
    a.p("Κανένα σπιράλ μέσα στην πλάκα · σε κάθε σημείο ύψος και απόσταση · κέντρο ασθενών στην τεχνική ντουλάπα του χωλ · "
        "Ethernet σε κάθε δωμάτιο (%d θύρες) · χωρίς KNX." % sum(d[4] for d in M.DATA), **B)
    a.h("ΤΟ ΔΙΑΜΕΡΙΣΜΑ ΣΕ ΑΡΙΘΜΟΥΣ")
    a.table([250, 100], [["Κυκλώματα πίνακα (+ 2 εφεδρικά)", "%d" % len(M.CIRCUITS)], ["Θέσεις ρευματοδοτών / μηχανισμοί", "%d / %d" % (n["sock_pts"], n["sock_out"])],
                         ["Πλαίσια διακοπτών / πλήκτρα", "%d / %d" % (n["sw_plates"], sum(n["sw"].values()))],
                         ["Χωνευτά spots", "%d" % sum(n["spots"].values())], ["Λήψεις Ethernet / TV", "%d / %d" % (sum(d[4] for d in M.DATA), len(M.TV))],
                         ["Ανιχνευτές πυρανίχνευσης · θερμοστάτες", "%d · %d" % (len(M.DETECTORS), len(M.THERMOSTATS))],
                         ["Μέγιστη ζήτηση (χωρίς τη φόρτιση)", "%s kW · %s A στη φάση" % (fz(F["dem"], 1), fz(F["imax"], 0))]], size=7.4, lead=8.8, pad=2.6, aligns={1: "r"})
    a.h("ΤΙ ΑΛΛΑΖΕΙ ΣΤΑ ΑΛΛΑ ΤΕΥΧΗ (ΑΝ ΕΓΚΡΙΘΕΙ)")
    a.table([70, 280], [["Τοιχοποιίες → Β1 R31 · Δ΄ R10", "τοίχος πόρτας εισόδου 15 cm (Τ6Α) αντί 22,5 (Τ6Β) · κουζίνα: ψυγείο στη ΝΔ γωνία, πλυντήριο πιάτων δεξιά του νεροχύτη · μονό κρεβάτι στο Υπν.2"],
                        ["Κουφώματα", "ηλεκτρικά ρολά στις μπαλκονόπορτες W2.08 (Υπν.1) και W2.06 (Υπν.2) – να μπουν στην παραγγελία"],
                        ["Ανόψεις Β1 → R24", "ΟΛΟ το χωλ +2,48 · κούτελο 19 cm δίπλα στο δοκάρι Δ3.1 στο Υπν.2 (κενό 15 × 32) · λωρίδα ΚΜ1 από το 9,40 · ψυκτικά ΚΜ1 από την ΟΠ2 · ο φωτισμός με spots: κάναβος καθιστικού 4 × 3, Υπν.2, χωρίς παροχές κρεμαστών, ανιχνευτής ΑΚ1 · φώτα εξώστη Υπν.2"],
                        ["Αποχετεύσεις → R29", "συμπυκνώματα ΚΜ1 Ø32: αντλία μηχανήματος → ΟΠ2 → κούτελο Υπν.2 → κενό χωλ με 2,6 % → σιφώνι πλυντηρίου · split Υπν.1 30 cm νοτιότερα"],
                        ["Ξυλότυποι Σ4 · Σ5 · Σ6", "5 χιτώνια Ø75 (ΟΠ2 Ø90) στα δοκάρια Δ3.1 (3) και Δ9.1 (2) – θέσεις στο ΗΛ-12"]], size=7.2, lead=8.6, pad=2.6, bold_first=True)
    a.h("ΔΕΝ ΕΧΕΙ ΓΙΝΕΙ ΑΚΟΜΗ")
    a.p("Ισόγειο, Δ΄ όροφος, σοφίτα και κοινόχρηστα – με την ίδια λογική, αφού εγκριθεί ο τυπικός όροφος.", bullet="•", **B)
    a.p("Τεχνικές προδιαγραφές, λίστα υλικών με ποσότητες και οδηγίες για τον ηλεκτρολόγο: βγαίνουν από το ίδιο μοντέλο μόλις κλειδώσουν οι θέσεις.", bullet="•", **B)
    a.p("Φωτοτεχνικός υπολογισμός με λογισμικό (εδώ: μέθοδος φωτεινής ροής).", bullet="•", **B)
    b.h("R17 – ΟΙ ΑΛΛΑΓΕΣ ΣΟΥ ΠΑΝΩ ΣΤΟ ΦΥΛΛΟ ΜΕ ΤΑ ΝΟΥΜΕΡΑ", fill=(0.78, 0.10, 0.10))
    b.p("ψυγείο στη ΝΔ γωνία (η Π50 στη θέση της Π57) · πλυντήριο πιάτων δεξιά του νεροχύτη · έφυγαν Π57, Π58 και το κύκλωμα Ρ7.", bold="Κουζίνα:", **B)
    b.p("Δ3 μόνο κουζίνα · έφυγαν Δ5, Δ12 · LED κεφαλαριού από τα δύο κομοδίνα (Δ8, Δ9) · Δ11 18 cm από την κάσα, μονό κρεβάτι · νέος Δ18 στο τοιχάκι της κολόνας της κουζίνας "
        "για τα φώτα του μπαλκονιού (αλέ-ρετούρ με τον Δ17).", bold="Διακόπτες:", **B)
    b.p("ηλεκτρικά ρολά στις μπαλκονόπορτες των υπνοδωματίων (Δ14, νέος Δ19) · φώτα οροφής στον εξώστη του Υπν.2 (ΕΚ9, ΕΚ10). Δ18 / Δ19: το καλώδιο έρχεται ΑΠΟ ΕΞΩ, "
        "από το ταβάνι του εξώστη (ΗΛ-14, τομή 18) – τίποτα καινούργιο στο πάτωμα.", bold="Ρολά · εξώστες:", **B)
    b.p("κάτω από διακόπτη, στην ίδια ευθεία: Π01 (Δ17), Π03 (Δ2), Π07 (Δ3), Π10 (Δ6), Π20 (Δ8), Π21 (Δ9), Π23 (Δ7), Π24 (Δ10), Π41 (Δ11) · Π11 / Π12 στην πλάτη της εσοχής του πλυντηρίου · "
        "έφυγαν Π62, Π63.", bold="Πρίζες:", **B)
    b.h("R16 – ΘΕΡΜΟΣΤΑΤΕΣ ΚΑΙ ΘΥΡΟΤΗΛΕΟΡΑΣΗ ΔΙΠΛΑ ΣΤΙΣ ΠΟΡΤΕΣ", fill=CHANC)
    b.p("κάθε θερμοστάτης ακριβώς πάνω από τον διακόπτη της πόρτας του, +1,50 · θυροτηλεόραση πάνω από τον διακόπτη της πόρτας εισόδου, +1,45.", bold="Οδηγία 20/11:", **B)
    b.h("R15 – ΚΟΥΤΕΛΟ ΣΤΟ ΔΟΚΑΡΙ ΤΟΥ ΣΑΛΟΝΙΟΥ · ΧΩΛ +2,48 · ΑΠΟΧΕΤΕΥΣΗ ΑΠΟ ΤΗΝ ΟΠ2", fill=HVC)
    b.p("κούτελο γυψοσανίδας κολλητά στη βόρεια παρειά του δοκαριού Δ3.1, στο Υπν.2: κενό 15 × 32 cm, κάτω παρειά +2,48 · όλο το χωλ +2,48 · η αποχέτευση Ø32 του κλιματιστικού σαλονιού "
        "από την ΟΠ2, μέσα στο κενό αυτό, ως το σιφώνι του πλυντηρίου. Τομές: ΗΛ-16.", bold="Οδηγία 20/11:", **B)
    b.h("R14 – ΕΛΕΓΧΟΣ ΟΛΩΝ ΤΩΝ ΠΕΡΑΣΜΑΤΩΝ: ΚΑΝΕΝΑ ΚΑΛΩΔΙΟ ΜΕΣΑ ΑΠΟ ΔΟΚΑΡΙ", fill=CHANC)
    b.p("κάθε καλώδιο είναι πραγματική διαδρομή από τον κορμό ως το κουτί του, ελεγμένη ανά 1 cm: πουθενά μέσα σε δοκάρι, κολόνα ή πλάκα. Κάτοψη ΗΛ-06 · τομές ΗΛ-14 · όψεις ΗΛ-15.", bold="Τι ελέγχθηκε:", **B)
    b.p("το καλώδιο δεν μπαίνει ποτέ από πάνω. Μπαίνει: οριζόντια ΜΕΣΑ στον τοίχο, στο +2,30, από διπλανό τοίχο που δεν έχει δοκάρι (τοίχοι 8, 10, 12) · από πίσω, μέσα από ντουλάπα (9, 13, 17) · "
        "κάτω από το δοκάρι μόνο στην κουζίνα, όπου η οροφή είναι 10 cm χαμηλότερα (11) · από το πάτωμα (14, 15).", bold="Τοίχοι κάτω από δοκάρι:", **B)
    b.p("ο τοίχος της TV (3 σπιράλ Ø25 από τη ντουλάπα του χωλ) και 30 cm στη ΒΔ γωνία του σαλονιού (2 σπιράλ Ø20 + 1 Ø16: διακόπτης Δ17, πρίζα Π01, επαφή συναγερμού). Πουθενά αλλού.", bold="Στο πάτωμα:", **B)
    b.p("3 στο δοκάρι του σαλονιού (ΟΠ5 παροχή + ασθενή · ΟΠ1 ισχυρά · ΟΠ2 αποχέτευση + ψυκτικά) και 2 στο δοκάρι εισόδου – κουζίνας (ΟΠ3 από το shaft · ΟΠ4 κουζίνα). Χιτώνιο Ø75 – η ΟΠ2 Ø90.", bold="Οπές:", **B)
    b.h("ΠΕΡΙΕΧΟΜΕΝΑ")
    b.table([40, 310], [[s_[0], s_[1]] for s_ in SHEETS], size=7.4, lead=8.8, pad=2.4, bold_first=True)
    c_.h("ΑΝΟΙΚΤΑ – ΧΡΕΙΑΖΟΜΑΙ ΑΠΑΝΤΗΣΗ", fill=DC.WARNC)
    c_.table([24, 64, 262], [[o[0], o[1], o[2]] for o in M.OPEN], size=7.0, lead=8.3, pad=2.6, bold_first=True)
    DC.finish(no, "ΣΥΝΟΨΗ – ΤΙ ΑΛΛΑΞΕ, ΤΙ ΧΡΕΙΑΖΕΤΑΙ ΑΠΟΦΑΣΗ", "Έλεγχος περασμάτων · κανένα καλώδιο μέσα από δοκάρι · %d ανοικτά" % len(M.OPEN))


# ================================================================ ΗΛ-05 ΦΩΤΙΣΜΟΣ – ΤΕΚΜΗΡΙΩΣΗ ΚΑΙ ΦΩΤΙΣΤΙΚΑ
def fixtures():
    """Πίνακας φωτιστικών από το μοντέλο: (κωδικός, είδος, τεμάχια, χαρακτηριστικά)."""
    n = lambda f: sum(1 for q in M.SPOTS if f(q))
    led = {}
    for (nm, a, b, g, t) in M.LED:
        led[nm] = led.get(nm, 0) + math.hypot(b[0] - a[0], b[1] - a[1])
    wl = lambda k: sum(1 for l in M.WALL_LIGHTS if l[4] == k)
    return [
        ("Φ1", "Χωνευτό spot", "%d τεμ." % n(lambda q: q[1] == "s" and q[4] != "ε"), "9 W · 850 lm · δέσμη 60° (καθιστικό, είσοδος, χωλ) / 36° (υπνοδωμάτια) · 2700 K · CRI ≥ 90 · βαθιά χωνευτό (UGR < 19) · ύψος ≤ 75 mm · dimmable"),
        ("Φ2", "ΔΙΠΛΟ χωνευτό spot", "%d τεμ." % n(lambda q: q[1] == "t"), "2 κεφαλές × 9 W / 850 lm, δέσμη 36° ρυθμιζόμενες · 2700 K · CRI ≥ 90 · σώμα ≈ 34 × 17 cm, ύψος ≤ 75 mm · dimmable – καθιστικό (4) και τραπέζι (1)"),
        ("Φ3", "Χωνευτό spot κουζίνας", "%d τεμ." % n(lambda q: q[4] == "ε"), "9 W · 850 lm · 60° · 2700 K · CRI ≥ 90 · στον άξονα του διαδρόμου, ανά 1,00 m"),
        ("Φ4", "Χωνευτό spot IP44", "%d τεμ." % n(lambda q: q[1] == "s44"), "8 W · 750 lm · 60° · 3000 K · CRI ≥ 90 · λουτρά εκτός ντους"),
        ("Φ5", "Χωνευτό spot IP65", "%d τεμ." % n(lambda q: q[1] == "s65"), "8 W · 750 lm · 60° · 3000 K · πάνω από το ντους"),
        ("Φ8", "LED πάγκου κουζίνας", "%s m" % fz(led.get("LED4", 0), 1), "ταινία 24 V ≈ 9,6 W/m · 800 lm/m · 3000 K · CRI ≥ 90 σε προφίλ με οπάλ κάλυμμα, κάτω από τα επάνω ντουλάπια · dimmable"),
        ("Φ9", "LED κεφαλαριού Υπν.1", "%s m" % fz(led.get("LED3", 0), 1), "ταινία 24 V ≈ 5 W/m · 2700 K · έμμεσο, ως νυχτερινό φως"),
        ("Φ10", "Κυλινδρικό φωτιστικό οροφής εξώστη", "%d τεμ." % len(M.EXT_SPOTS), "επίτοιχο στο ταβάνι του εξώστη, λευκό, Ø 8–10 cm · IP65 · 7–9 W · 3000 K · σε ζεύγη ανά 0,45 m – όπως τα προοπτικά του αρχιτέκτονα"),
        ("Φ11", "Καθρέπτης με φως", "%d τεμ." % wl("mir"), "φως από μπροστά / περιμετρικά ≈ 1500 lm · 3000–4000 K · CRI ≥ 90 · IP44 · παροχή στο +1,90"),
        ("Φ12", "Στεγανό φωτιστικό τοίχου εξώστη", "%d τεμ." % wl("ext"), "IP65 · 8–10 W · 3000 K · φως προς τα κάτω (όχι προς τον γείτονα) · +2,10"),
        ("Φ13", "Φωτιστικό ασφαλείας", "%d τεμ." % len(M.EMERGENCY), "αυτόνομο 1 h, πάνω από την πόρτα εισόδου"),
    ]


def sheet_05(no="ΗΛ-05"):
    if not M.SHOW_NOTES:                                        # R20: μόνο οι δύο πίνακες δεδομένων (στάθμες ανά χώρο · φωτιστικά σώματα)
        y = DC.title("ΦΩΤΙΣΜΟΣ – ΣΤΑΘΜΕΣ ΑΝΑ ΧΩΡΟ ΚΑΙ ΦΩΤΙΣΤΙΚΑ ΣΩΜΑΤΑ")
        b, c_ = DC.cols(2, y, name="ΗΛ-05")
        rows = [[r[0], fz(r[1], 1), "%d" % r[4], "%d" % (round(r[3] / 10) * 10), "%d K" % r[7], r[8]] for r in CK.lighting_table()]
        b.table([62, 22, 26, 26, 30, 184], rows, head=["ΧΩΡΟΣ", "m²", "ΣΤΟΧΟΣ\nlx", "ΥΠΟΛ.\nlx", "ΧΡΩΜΑ", "ΑΠΟ ΤΙ ΒΓΑΙΝΕΙ ΤΟ ΦΩΣ"], size=6.8, lead=8.0, pad=2.2, bold_first=True, aligns={1: "r", 2: "r", 3: "r"})
        c_.table([22, 96, 34, 198], [[f[0], f[1], f[2], f[3]] for f in fixtures()], head=["", "ΕΙΔΟΣ", "ΠΟΣΟΤ.", "ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"], size=6.8, lead=8.0, pad=2.2, bold_first=True)
        DC.finish(no, "ΦΩΤΙΣΜΟΣ – ΣΤΑΘΜΕΣ ΚΑΙ ΦΩΤΙΣΤΙΚΑ", "Στάθμες ανά χώρο · φωτιστικά σώματα")
        return
    y = DC.title("ΦΩΤΙΣΜΟΣ ΜΟΝΟ ΜΕ SPOTS – ΚΑΝΟΝΕΣ ΚΑΙ ΦΩΤΙΣΤΙΚΑ ΣΩΜΑΤΑ", "πώς αποφασίστηκε κάθε θέση · στάθμες ανά χώρο · τι αλλάζει από τις ανόψεις · τύποι φωτιστικών")
    a, b, c_ = DC.cols(3, y, name="ΗΛ-05")
    a.h("ΟΙ ΚΑΝΟΝΕΣ ΤΗΣ ΜΕΛΕΤΗΣ", fill=LGT)
    for i, (hd, tx) in enumerate(M.LIGHT_RULES, 1):
        a.p(tx, bold="%d · %s" % (i, hd), size=7.5)
    a.h("ΠΗΓΕΣ")
    for sname, what in M.LIGHT_SOURCES:
        a.p(what, bold=sname + ":", size=6.6, color=MUTE)
    b.h("ΣΤΑΘΜΕΣ ΦΩΤΙΣΜΟΥ ΑΝΑ ΧΩΡΟ")
    rows = []
    for r in CK.lighting_table():
        rows.append([r[0], fz(r[1], 1), "%d" % r[4], "%d" % (round(r[3] / 10) * 10), "%d K" % r[7], r[8]])
    b.table([62, 22, 26, 26, 30, 184], rows, head=["ΧΩΡΟΣ", "m²", "ΣΤΟΧΟΣ\nlx", "ΥΠΟΛ.\nlx", "ΧΡΩΜΑ", "ΑΠΟ ΤΙ ΒΓΑΙΝΕΙ ΤΟ ΦΩΣ"], size=6.8, lead=8.0, pad=2.2, bold_first=True, aligns={1: "r", 2: "r", 3: "r"})
    b.p("Υπολογισμένο lx = μέση στάθμη του ΓΕΝΙΚΟΥ φωτισμού με όλα αναμμένα στο 100 % (μέθοδος φωτεινής ροής, συντελεστής χρησιμοποίησης 0,55, συντήρησης 0,8). "
        "Οι κύριες ομάδες έχουν dimmer – η στάθμη κατεβαίνει όσο θέλεις.", size=6.5, color=MUTE)
    b.h("ΤΙ ΑΛΛΑΖΕΙ ΑΠΟ ΤΙΣ ΑΝΟΨΕΙΣ Β1 %s" % A.REV)
    b.table([50, 300], [[k, t] for k, t in M.LIGHT_CHANGES], size=6.9, lead=8.1, pad=2.2, bold_first=True)
    b.p("Μένουν όπως ήταν: θέσεις spots σε Υπν.1, χωλ, κουζίνα, λουτρά · LED κεφαλαριού και πάγκου · οι άλλοι ανιχνευτές · στάθμες οροφών.", size=6.9)
    b.h("ΧΕΙΡΙΣΜΟΣ – ΧΩΡΙΣ KNX")
    for hd, tx in M.LIGHT_CTRL:
        b.p(tx, bold=hd, bullet="•", size=7.0)
    c_.h("ΦΩΤΙΣΤΙΚΑ ΣΩΜΑΤΑ – ΤΙ ΠΑΡΑΓΓΕΛΝΕΤΑΙ")
    c_.table([22, 96, 34, 198], [[f[0], f[1], f[2], f[3]] for f in fixtures()], head=["", "ΕΙΔΟΣ", "ΠΟΣΟΤ.", "ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"], size=6.8, lead=8.0, pad=2.2, bold_first=True)
    c_.p("Όλα τα LED της ίδιας θερμοκρασίας από την ΙΔΙΑ σειρά και παρτίδα (απόκλιση χρώματος ≤ 3 SDCM), χωρίς τρεμόπαιγμα, με τροφοδοτικό που συνεργάζεται με τον dimmer "
         "που θα μπει. Δείγμα ενός spot στο εργοτάξιο πριν από την παραγγελία.", size=6.9)
    DC.finish(no, "ΦΩΤΙΣΜΟΣ – ΤΕΚΜΗΡΙΩΣΗ ΚΑΙ ΦΩΤΙΣΤΙΚΑ", "Κανόνες · στάθμες ανά χώρο · αλλαγές από τις ανόψεις · φωτιστικά σώματα")


# ================================================================ ΗΛ-11 ΥΠΟΓΕΙΟ – ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ, ΦΟΡΤΙΣΗ ΟΧΗΜΑΤΟΣ, ΠΑΡΟΧΗ ΣΠΙΤΙΟΥ
S80 = 72 / 25.4 * 1000 / 80


def sheet_11(no="ΗΛ-11"):
    import b_model as Y
    P.begin_plan(); v = P.view(282, 122, S80); v.sym = 1.0
    P.base(v, Y, site=False, parking=True)
    mx, my = M.METERS; sx, sy = M.SHAFT
    # μετρητές (ισόγειο) → shaft, μέσα στην οροφή του χωλ εισόδου του ισογείου
    C().saveState(); C().setDash([3, 2]); v.rect(mx - 0.40, my - 0.60, mx + 0.40, my + 0.60, stroke=FEED, lw=1.0); C().restoreState()
    D.halo_text(v, mx + 0.55, my - 0.20, "6 ΜΕΤΡΗΤΕΣ ΔΕΔΔΗΕ", size=5.6, color=FEED, font="Inter-Bold", anchor="l")
    if M.SHOW_NOTES:
        D.halo_text(v, mx + 0.55, my + 0.12, "στο ΙΣΟΓΕΙΟ, έξω από τον", size=4.8, color=FEED, anchor="l")
        D.halo_text(v, mx + 0.55, my + 0.40, "τοίχο της εισόδου (κατά Η02)", size=4.8, color=FEED, anchor="l")
    D.route(v, [(mx - 0.40, my), (11.60, my), (11.60, 6.20), (sx + 0.25, 6.20), (sx + 0.25, sy)], col=FEED, lw=1.6, dash=[3.5, 2], arrows=True)
    if M.SHOW_NOTES:
        D.halo_text(v, 13.55, 7.55, "μέσα στην οροφή του χωλ ισογείου → shaft", size=4.8, color=FEED, anchor="l")
    v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.9)
    D.halo_text(v, 11.05, 2.45, "shaft Η/Μ", size=5.4, color=DAT, font="Inter-Bold", anchor="l")
    if M.SHOW_NOTES:
        D.halo_text(v, 11.05, 2.75, "κάτω: από μετρητές · πάνω: προς σπίτια", size=4.4, color=DAT, anchor="l")
    for q in M.STORES:
        col = q["col"]
        D.route(v, q["tray"], col=col, lw=2.2, arrows=False)
        D.route(v, q["evr"], col=col, lw=1.3, dash=[1.2, 1.6])
        px, py = q["pa"]
        v.rect(px - 0.16, py - 0.16, px + 0.16, py + 0.16, fill=col, stroke=INK, lw=0.6)
        ex, ey = q["ev"]
        X_, Y_ = v.p(ex, ey); C().saveState(); C().setFillColorRGB(1, 1, 1); C().setStrokeColorRGB(*col); C().setLineWidth(1.3); C().circle(X_, Y_, 5.2, stroke=1, fill=1); C().restoreState()
        ptext(X_, Y_ - 1.7, "EV", 4.6, "Inter-Bold", col, "c", bg=False)
    for (x_, y_, s_, cl, an) in ((-3.75, 0.55, "ΠΑ-Α", M.STORES[0]["col"], "c"), (0.35, -0.42, "ΠΑ-Β", M.STORES[1]["col"], "c"), (-3.55, 2.55, "ΠΑ-Γ", M.STORES[2]["col"], "c"),
                                 (0.55, 7.25, "φορτιστής Α΄", M.STORES[0]["col"], "l"), (1.60, -0.45, "φορτιστής Β΄", M.STORES[1]["col"], "l"), (-0.85, 12.75, "φορτιστής Γ΄", M.STORES[2]["col"], "l")):
        D.halo_text(v, x_, y_, s_, size=5.6, color=cl, font="Inter-Bold", anchor=an)
    D.halo_text(v, 6.0, 2.25, "σχάρα καλωδίων στην οροφή του υπογείου (εμφανής)" if M.SHOW_NOTES else "σχάρα καλωδίων", size=4.8, color=INK, font="Inter-SemiBold")
    P.end_plan()
    P.view_title("ΥΠΟΓΕΙΟ – ΜΕΤΡΗΤΗΣ → ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ → ΦΟΡΤΙΣΤΗΣ ΚΑΙ ΠΑΡΟΧΗ ΣΠΙΤΙΟΥ", "Κλίμακα 1:80"); P.scale_bar(80)
    FL = CK.feeder_lengths()
    y = P._head(P.TOP - 22, "ΠΩΣ ΠΑΕΙ ΤΟ ΡΕΥΜΑ (ΛΥΣΗ Β)") if M.SHOW_NOTES else P.TOP - 22
    steps = [] if not M.SHOW_NOTES else ["1 · Μετρητής (ισόγειο, έξω από τον τοίχο της εισόδου) → μέσα στην οροφή του χωλ εισόδου → shaft Η/Μ.",
             "2 · Κάτω μέσα στο shaft ως το υπόγειο → σχάρα στην οροφή του υπογείου → ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ «ΠΑ» (καλώδιο %s)." % M.FEEDER["cable"].split()[-2],
             "3 · Από τον ΠΑ φεύγουν τρεις γραμμές: (α) φορτιστής στη θέση στάθμευσης 5×6 · (β) φως και πρίζα της αποθήκης · (γ) ΠΑΡΟΧΗ ΤΟΥ ΣΠΙΤΙΟΥ %s." % M.FEEDER["cable"].split()[-2],
             "4 · Η παροχή του σπιτιού γυρίζει στην ίδια σχάρα ως το shaft και ανεβαίνει στον όροφο (ΗΛ-06).",
             "5 · Η διαχείριση φορτίου μετρά στον ΠΑ όλη την παροχή: ο φορτιστής παίρνει ό,τι περισσεύει από τα 3 × 35 A."]
    yy = y - 6
    for s_ in steps:
        yy = D.para(P.PX - 2, yy, s_, P.PW + 4, size=5.9) - 3
    rows = [[q["fl"], q["st"], q["park"], "%s m" % fz(q["L1"], 0), "%s m" % fz(q["L2"], 0), "%s m" % fz(q["Lev"], 0), "%s %%" % fz(q["du"], 2)] for q in FL]
    w0 = [20, 22, 44, 34, 34, 34]; w0.append(P.PW + 8 - sum(w0))
    yy = D.table(P.PX - 4, yy - 4, w0, rows, head=["", "ΑΠΟΘ.", "ΘΕΣΗ", "μετρ. → ΠΑ", "ΠΑ → σπίτι", "ΠΑ → EV", "ΔU σπιτιού"], size=5.3, lead=6.5, pad=2.0, bold_first=True,
                 colors={i: tint(q["col"], 0.82) for i, q in enumerate(M.STORES)}, zebra=False)
    yy = D.table(P.PX - 4, yy - 6, [P.PW - 22 + 8, 22], [[a_, "%d" % n_] for a_, n_ in M.PA_ROWS],
                 head=["ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ «ΠΑ» – επίτοιχος IP44, 2 × 18 στοιχεία", "στοιχ."], size=5.3, lead=6.5, pad=2.0, aligns={1: "r"})
    notes = ["Μήκη και θέσεις είναι ΕΚΤΙΜΗΣΗ από τα σχέδια (± 10 %). Η θέση των μετρητών από το σχέδιο Η02 της αδείας.",
             "Οι οδεύσεις στο υπόγειο είναι ενδεικτικές: εμφανείς, σε σχάρα / σωλήνα, κάτω από τα δοκάρια (το υπόγειο δεν έχει ψευδοροφή).",
             "Καλώδια στο shaft και στο κλιμακοστάσιο χαμηλού καπνού χωρίς αλογόνα· σφράγιση του shaft σε κάθε πλάκα.",
             "Αντιστοίχιση: Α΄ → Υ3 · Θ.Σ.Υ.5 · Β΄ → Υ4 · Θ.Σ.Υ.6 · Γ΄ → Υ2 · Θ.Σ.Υ.3 – 4 (πίνακας πωλήσεων). Δ΄ και ισόγειο: στα δικά τους τεύχη."]
    yy -= 12
    for s_ in (notes if M.SHOW_NOTES else []):
        yy = D.para(P.PX - 2, yy, s_, P.PW + 4, size=5.4, color=MUTE, bullet="•") - 2
    assert yy > 150, "ΗΛ-11: η δεξιά στήλη ξεχειλίζει (%.0f)" % yy
    P.finish(no, "ΥΠΟΓΕΙΟ – ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ · ΦΟΡΤΙΣΗ", "Μετρητής → αποθήκη → φορτιστής · παροχή σπιτιού", M.BASE_TXT, "Κλίμακα 1:80 · A3")


# ================================================================ ΗΛ-12 ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΟΛΑ ΤΑ ΠΕΡΑΣΜΑΤΑ + ΟΠΕΣ ΔΟΚΩΝ (ΑΝ ΕΓΚΡΙΘΟΥΝ)
def _hv(name):
    """Γραμμή καλωδίου που ανήκει στον κλιματισμό / στην ενδοδαπέδια (R20: δεν γράφεται στα ηλεκτρολογικά φύλλα)."""
    return (not M.SHOW_HVAC) and (name.split()[0] in M.HVAC_CIRC or name.startswith("επικοινωνία μονάδων") or name.startswith("εντολές"))


def _tube_txt(lst, hole=None):
    """«1 καλώδιο · 3 × Ø25 · …» – hole=True μόνο όσα πάνε από την οπή, False όσα μένουν, None όλα."""
    q = {}
    for nm, d, od, via in lst:
        if (hole is not None and via != hole) or _hv(nm):
            continue
        q[d] = q.get(d, 0) + 1
    return " · ".join(("%d × Ø%d" % (q[d], d)) if d else ("%d καλώδιο 5×16" % q[d]) for d in sorted(q, key=lambda k: (k != 0, -k))) or "—"


def sheet_12(no="ΗΛ-12"):
    H = [h for h in CK.holes() if M.SHOW_HVAC or h["kind"] != "hvac"]
    PL._plan(_routes, "ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΤΙ ΠΕΡΝΑ ΑΠΟ ΚΑΘΕ ΟΠΗ ΚΑΙ ΚΑΘΕ ΠΕΡΑΣΜΑ")
    y = P._head(P.TOP - 22, "ΧΙΤΩΝΙΑ Ø75 (ΟΠ2 Ø90) ΣΤΑ ΔΟΚΑΡΙΑ – ΘΕΣΗ ΓΙΑ ΤΟ ΚΑΛΟΥΠΙ" if M.SHOW_HVAC else "ΧΙΤΩΝΙΑ Ø75 ΣΤΑ ΔΟΚΑΡΙΑ – ΘΕΣΗ ΓΙΑ ΤΟ ΚΑΛΟΥΠΙ")
    rows = []
    for h in H:
        bn, sec, x0, y0, x1, y1 = [b_ for b_ in M.A.BEAMS if b_[0] == h["beam"]][0]
        if h["horiz"]:
            pos = "%s m από τη δυτική κολόνα (Κ10) · %s m από την Κ3" % (fz(h["x"] - x0, 2), fz(x1 - h["x"], 2))
        else:
            pos = "%s m από την Κ3 (βόρεια) · %s m από την Κ8" % (fz(h["y"] - y0, 2), fz(y1 - h["y"], 2))
        rows.append([h["id"], h["beam"], pos])
    y = D.table(P.PX - 4, y + 2, [18, 22, P.PW - 40 + 8], rows, head=["", "ΔΟΚΟΣ", "ΚΕΝΤΡΟ ΟΠΗΣ ΚΑΤΑ ΜΗΚΟΣ ΤΟΥ ΔΟΚΑΡΙΟΥ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    if M.SHOW_NOTES:
        txt(P.PX - 2, y - 7, "Ύψος: κέντρο 25 cm κάτω από την άνω στάθμη της πλάκας = μέση του ύψους (δοκάρια 30/50).", size=5.0, color=MUTE)
        txt(P.PX - 2, y - 13.5, "Κάθετα στο δοκάρι, σε όλο το πλάτος του. Χιτώνιο PVC Ø75 (καθαρό 70 mm) – η ΟΠ2 Ø90 (καθαρό 85).", size=5.0, color=MUTE)
    y = P._head(y - (30 if M.SHOW_NOTES else 14), "ΤΙ ΠΕΡΝΑ ΑΠΟ ΚΑΘΕ ΟΠΗ")
    rows, colors = [], {}
    for i, h in enumerate(H):
        ln_ = [q for q in h["lines"] if not _hv(q[0])]
        rows.append([h["id"], h["use"] + "\n%s → %s" % (h["frm"], h["to"]), ", ".join(("%d × %s" % (n_, nm)) if n_ > 1 else nm for nm, d_, n_, k_ in ln_) + ".",
                     "%d\n%d %%" % (h["ncab"], round(h["fill"] * 100)) if M.SHOW_HVAC else "%d" % sum(q[2] for q in ln_)])
        colors[i] = tint(DAT, 0.86) if h["kind"] == "weak" else (tint(FEED, 0.86) if h["kind"] == "feed" else (tint(HVC, 0.86) if h["kind"] == "hvac" else tint(PWR, 0.88)))
    y = D.table(P.PX - 4, y + 2, [18, 62, P.PW - 102 + 8, 22], rows, head=["", "ΤΙ / ΑΠΟ → ΠΡΟΣ", "ΤΙ ΠΕΡΝΑ ΑΚΡΙΒΩΣ (τεμάχια × είδος)", "τεμ.\nγεμ." if M.SHOW_HVAC else "τεμ."], size=4.9, lead=5.9, pad=1.8, bold_first=True, colors=colors, zebra=False)
    y = P._head(y - 16, "ΤΑ ΑΛΛΑ ΠΕΡΑΣΜΑΤΑ (μέσα από τοίχους / ντουλάπες)")
    rows = []
    for p_ in M.PASSES:
        if p_["id"] in M.TUBES:
            t = [q for q in M.TUBES[p_["id"]] if not _hv(q[0])]
            rows.append([p_["id"], "%d" % len(t), _tube_txt(t) + "\n" + ", ".join(q[0] for q in t) + "."])
    y = D.table(P.PX - 4, y + 2, [18, 16, P.PW - 34 + 8], rows, head=["", "τεμ.", "ΣΩΛΗΝΕΣ (σπιράλ βαρέως τύπου) – ΤΙ ΕΧΕΙ Ο ΚΑΘΕΝΑΣ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    rows = [[a_, b_ + "."] for a_, b_ in M.HOLES_NO]
    if M.SHOW_NOTES:
        y = D.table(P.PX - 4, y - 4, [62, P.PW - 62 + 8], rows, head=["ΧΩΡΙΣ ΟΠΗ", "ΤΙ ΓΙΝΕΤΑΙ ΕΚΕΙ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    notes = ["Γέμισμα = διατομή καλωδίων / καθαρή διατομή χιτωνίου (Ø70). Όριο 60 % (χιτώνιο 30 cm). Ασθενή δίπλα σε ισχυρά μόνο μέσα σε δικό τους σπιράλ.",
             "ΟΠ2: η αποχέτευση Ø32 ΨΗΛΑ στο χιτώνιο (για την κλίση), PVC κολλητός χωρίς ένωση μέσα του· από κάτω ο σωλήνας αερίου 5/8″ με μόνωση 9 mm (Ø34) και ο υγρού 1/4″ (Ø24). Με μόνωση 13 mm στο αέριο (Ø42) ΔΕΝ χωρούν και τα τρία.",
             "Μετά την ΟΠ2 η αποχέτευση τρέχει με 2,6 % μέσα στο κούτελο του Υπν.2 (κενό 15 × 32 cm δίπλα στο δοκάρι) και στο κενό του χωλ, και πέφτει στο σιφώνι του πλυντηρίου.",
             "Όροφοι που δεν έχουν χυθεί: χιτώνιο στο καλούπι. Αν κάποιος έχει ήδη χυθεί: καρότο με ανίχνευση σιδήρων, μόνο με τον στατικό."]
    y -= 10
    for s_ in (notes if M.SHOW_NOTES else []):
        y = D.para(P.PX - 2, y, s_, P.PW + 4, size=5.2, color=MUTE, bullet="•") - 2
    assert y > 150, "ΗΛ-12: η δεξιά στήλη ξεχειλίζει (%.0f)" % y
    PL._finish(no, "ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΟΠΕΣ ΚΑΙ ΠΕΡΑΣΜΑΤΑ", "Χιτώνια Ø75 ΟΠ1–ΟΠ5 (ΟΠ2 Ø90): θέση και τι περνά · λοιπά περάσματα" if M.SHOW_HVAC else "Χιτώνια Ø75 %s: θέση και τι περνά · λοιπά περάσματα" % " · ".join(h["id"] for h in H))


# ================================================================ ΗΛ-13 ΚΑΤΑΚΟΡΥΦΟ ΔΙΑΓΡΑΜΜΑ ΟΙΚΟΔΟΜΗΣ
def sheet_13(no="ΗΛ-13"):
    y = DC.title("ΚΑΤΑΚΟΡΥΦΟ ΔΙΑΓΡΑΜΜΑ ΟΙΚΟΔΟΜΗΣ – ΠΩΣ ΣΩΛΗΝΩΝΕΤΑΙ", "shaft Η/Μ · παροχές μέσω αποθήκης · ασθενή · σχηματικό, χωρίς κλίμακα")
    X0 = DC.X0; c = C()
    n = len(M.LEVELS); top = y - 6; rh = 76.0
    xs0, xs1 = X0 + 330, X0 + 400            # το shaft
    xa0, xa1 = X0 + 70, xs0 - 40             # ζώνη διαμερίσματος (αριστερά)
    xr0, xr1 = xs1 + 40, X0 + 720            # ζώνη κλιμακοστασίου / κοινοχρήστων (δεξιά)
    ylev = {}
    for i, (nm, lv, what) in enumerate(M.LEVELS):
        yt = top - i * rh; yb_ = yt - rh; ylev[nm] = (yt, yb_)
        box(X0, yb_, xr1 - X0, rh, fill=(0.975, 0.975, 0.98) if i % 2 else (1, 1, 1), stroke=FAINT, lw=0.4)
        ln(X0, yb_, xr1, yb_, col=(0.45, 0.45, 0.50), lw=1.6)
        txt(X0 + 4, yt - 11, nm, size=8.0, font="Inter-Bold"); txt(X0 + 4, yt - 20, ("%+.2f" % lv).replace(".", ","), size=5.8, color=MUTE)
        txt(xr1 - 4, yt - 9, what, size=5.6, color=MUTE, anchor="r")
    yt_all, yb_all = ylev["ΔΩΜΑ"][0] - 26, ylev["ΥΠΟΓΕΙΟ"][1] + 14
    box(xs0, yb_all, xs1 - xs0, yt_all - yb_all, fill=(0.86, 0.95, 0.92), stroke=DAT, lw=1.2)
    txt((xs0 + xs1) / 2, yt_all + 5, "SHAFT Η/Μ", size=7.0, font="Inter-Bold", color=DAT, anchor="c")
    txt((xs0 + xs1) / 2, yt_all - 9, "90 × 15 cm", size=5.6, color=DAT, anchor="c")
    FLO = ("Δ΄", "Γ΄", "Β΄", "Α΄", "ΙΣΟΓΕΙΟ")
    # διαμερίσματα: shaft → ψευδοδοκός κλιμακοστασίου → Π0 → πίνακας
    for k, nm in enumerate(FLO):
        yt, yb_ = ylev[nm]; yy = yt - 22
        ln(xs0, yy, xa0 + 92, yy, col=FEED, lw=2.0)
        box(xa0 + 40, yy - 9, 52, 18, fill=FEED, stroke=INK, lw=0.6); txt(xa0 + 66, yy - 2.5, "ΓΠ", size=7.0, font="Inter-Bold", color=(1, 1, 1), anchor="c")
        txt(xa0 + 100, yy + 4, "παροχή 5×16 → Π0 → ψευδοροφές", size=5.4)
        ln(xs0, yy - 14, xa0 + 150, yy - 14, col=DAT, lw=1.2, dash=[3, 1.5])
        box(xa0 + 110, yy - 22, 40, 14, fill=(1, 1, 1), stroke=DAT, lw=0.9); txt(xa0 + 130, yy - 17.5, "ΚΑ", size=6.2, font="Inter-Bold", color=DAT, anchor="c")
        txt(xa0 + 158, yy - 25, "ίνα · κεραία · θυροτηλ. · πυραν.", size=5.2, color=DAT)
        if not M.SHOW_NOTES:
            pass
        elif nm in ("Γ΄", "Β΄", "Α΄"):
            txt(xa0 + 40, yy - 40, "τυπικός όροφος: ΗΛ-06, ΗΛ-12", size=5.2, color=MUTE)
        else:
            txt(xa0 + 40, yy - 40, "ίδια λογική – ΔΕΝ έχει μελετηθεί ακόμη", size=5.2, color=(0.75, 0.25, 0.10))
    # υπόγειο: πίνακες αποθηκών
    yt, yb_ = ylev["ΥΠΟΓΕΙΟ"]; yy = yt - 20
    ln(xs0, yy, xa0 + 60, yy, col=FEED, lw=2.0)
    for j in range(5):
        xx = xa0 + j * 34
        box(xx, yy - 26, 26, 16, fill=PWR, stroke=INK, lw=0.5); ln(xx + 13, yy, xx + 13, yy - 10, col=FEED, lw=1.2)
        txt(xx + 13, yy - 20.5, "ΠΑ", size=5.6, font="Inter-Bold", color=(1, 1, 1), anchor="c")
        c.saveState(); c.setStrokeColorRGB(*PWR); c.setFillColorRGB(1, 1, 1); c.setLineWidth(1.0); c.circle(xx + 13, yy - 37, 5, stroke=1, fill=1); c.restoreState()
        txt(xx + 13, yy - 39, "EV", size=4.2, font="Inter-Bold", color=PWR, anchor="c"); ln(xx + 13, yy - 26, xx + 13, yy - 32, col=PWR, lw=0.9, dash=[1.2, 1.2])
    ln(xa0 + 13, yy, xs0, yy, col=FEED, lw=2.0)
    txt(xa0 + 176, yy + 4, "σχάρα οροφής υπογείου", size=5.4)
    txt(xa0 + 176, yy - 16, "5 πίνακες αποθηκών", size=5.4); txt(xa0 + 176, yy - 24, "→ φορτιστής + αποθήκη", size=5.4); txt(xa0 + 176, yy - 32, "→ παροχή σπιτιού (ΗΛ-11)", size=5.4)
    # ισόγειο: μετρητές
    yt, yb_ = ylev["ΙΣΟΓΕΙΟ"]; ym = yb_ + 13
    box(xr0 + 150, ym - 9, 74, 18, fill=(1, 1, 1), stroke=INK, lw=1.2); txt(xr0 + 187, ym - 2.5, "6 ΜΕΤΡΗΤΕΣ", size=6.4, font="Inter-Bold", anchor="c")
    ln(xs1, ym, xr0 + 150, ym, col=FEED, lw=2.0); txt(xr0 + 6, ym + 4, "μέσα στην οροφή του χωλ εισόδου", size=5.2)
    txt(xr0 + 232, ym - 2, "ΔΕΔΔΗΕ", size=5.6, color=MUTE)
    box(xr0 + 60, yt - 34, 70, 14, fill=(1, 1, 1), stroke=INK, lw=0.8); txt(xr0 + 95, yt - 29.5, "ΠΙΝ. ΚΟΙΝΟΧΡ.", size=5.2, font="Inter-Bold", anchor="c")
    box(xr0 + 140, yt - 34, 70, 14, fill=(1, 1, 1), stroke=FIR, lw=0.8); txt(xr0 + 175, yt - 29.5, "ΠΥΡΑΝΙΧΝΕΥΣΗ", size=5.2, font="Inter-Bold", color=FIR, anchor="c")
    ln(xs1, yt - 27, xr0 + 60, yt - 27, col=FIR, lw=1.0, dash=[3, 1.5])
    # κλιμακοστάσιο ανά όροφο
    for nm in ("Δ΄", "Γ΄", "Β΄", "Α΄"):
        yt, yb_ = ylev[nm]
        txt(xr0 + 6, yt - 26, "ψευδοδοκός κλιμακοστασίου: shaft → πόρτα διαμερίσματος" if M.SHOW_NOTES else "ψευδοδοκός κλιμακοστασίου", size=5.2, color=MUTE)
        ln(xs1, yt - 22, xr0, yt - 22, col=(0.6, 0.6, 0.64), lw=1.0)
    # δώμα
    yt, yb_ = ylev["ΔΩΜΑ"]
    box(xa0 + 150, yb_ + 12, 60, 16, fill=(1, 1, 1), stroke=HVC, lw=1.0); txt(xa0 + 180, yb_ + 17.5, "BOILER × 5", size=5.8, font="Inter-Bold", color=HVC, anchor="c")
    ln(xa0 + 210, yb_ + 20, xs0 + 14, yb_ + 20, col=HVC, lw=1.2); ln(xs0 + 14, yb_ + 20, xs0 + 14, yb_all + 4, col=HVC, lw=0.9, dash=[2, 1.5])
    box(xr0 + 30, yb_ + 12, 60, 16, fill=(1, 1, 1), stroke=DAT, lw=1.0); txt(xr0 + 60, yb_ + 17.5, "ΚΕΡΑΙΑ TV", size=5.8, font="Inter-Bold", color=DAT, anchor="c")
    ln(xs1 - 14, yb_ + 20, xr0 + 30, yb_ + 20, col=DAT, lw=1.2, dash=[3, 1.5]); ln(xs1 - 14, yb_ + 20, xs1 - 14, yb_all + 4, col=DAT, lw=0.9, dash=[3, 1.5])
    yt, yb_ = ylev["ΥΠΟΓΕΙΟ"]
    box(xr0 + 30, yb_ + 14, 90, 16, fill=(1, 1, 1), stroke=DAT, lw=1.0); txt(xr0 + 75, yb_ + 19.5, "ΚΑΤΑΝΕΜΗΤΗΣ ΟΤΕ", size=5.6, font="Inter-Bold", color=DAT, anchor="c")
    ln(xs1, yb_ + 22, xr0 + 30, yb_ + 22, col=DAT, lw=1.2, dash=[3, 1.5])
    ln((xs0 + xs1) / 2 - 8, yb_all + 4, (xs0 + xs1) / 2 - 8, yt_all - 16, col=FEED, lw=2.4)
    # δεξιά στήλη: τι έχει το shaft + σειρά εργασιών
    f = DC.Flow(X0 + 745, y, DC.X1 - X0 - 745, size=6.6, name="ΗΛ-13")
    B = dict(bullet="•", size=6.6)
    f.h("ΤΙ ΠΕΡΝΑ ΜΕΣΑ ΣΤΟ SHAFT")
    f.table([250, 80], [["Παροχές: μετρητής → αποθήκη (κάτω) και αποθήκη → σπίτι (πάνω)", "5 + 5 × 5×16"], ["Boiler ηλιακών στο δώμα (από κάθε πίνακα σπιτιού)", "5 × 3×4"],
                        ["Οπτική ίνα / τηλέφωνο από τον κατανεμητή του υπογείου", "5 × Ø20"], ["Κεραία TV από το δώμα", "1 κάθοδος + 5"],
                        ["Θυροτηλεόραση από την είσοδο", "1 × Ø25"], ["Πυρανίχνευση: βρόχος προς τον κοινόχρηστο πίνακα", "1 × Ø20"],
                        ["Κοινόχρηστα: φώτα κλιμακοστασίου, ανελκυστήρας", "κατά τον κοινόχρηστο πίνακα"]], head=None if M.SHOW_NOTES else ["ΤΙ ΠΕΡΝΑ ΜΕΣΑ ΣΤΟ SHAFT", ""], size=6.0, lead=7.4, pad=2.2, aligns={1: "r"})
    f.p("Ισχυρά και ασθενή σε ΧΩΡΙΣΤΕΣ σχάρες μέσα στο shaft, στις δύο άκρες του.", **B)
    f.p("Σφράγιση του shaft σε κάθε πλάκα με πυράντοχο υλικό. Καλώδια χαμηλού καπνού, χωρίς αλογόνα.", **B)
    f.p("Το άνοιγμα 90 × 15 του shaft υπάρχει ήδη στους ξυλοτύπους Σ2 … Σ7 – δεν χρειάζεται τίποτα άλλο στο μπετό.", **B)
    f.h("ΣΕΙΡΑ ΕΡΓΑΣΙΩΝ ΤΟΥ ΗΛΕΚΤΡΟΛΟΓΟΥ")
    for j, s_ in enumerate(["ΣΤΟ ΚΑΛΟΥΠΙ κάθε πλάκας ορόφου: τα 5 χιτώνια Ø75 (ΟΠ2 Ø90) στα δοκάρια (θέσεις: ΗΛ-12).",
                            "Σχάρες μέσα στο shaft, από το υπόγειο ως το δώμα. Σχάρα στην οροφή του υπογείου: shaft → αποθήκες. Πίνακες αποθηκών.",
                            "ΠΡΙΝ από τη μόνωση της ενδοδαπέδιας και το γέμισμα: τα σπιράλ του δαπέδου – τοίχος TV και ΒΔ γωνία σαλονιού (ΗΛ-06, ΗΛ-07).",
                            "Τοίχοι: τα καλώδια μπαίνουν ΠΡΙΝ κλείσει η δεύτερη πλευρά της γυψοσανίδας. Από πού μπαίνουν σε κάθε τοίχο: ΗΛ-06, ΗΛ-14, ΗΛ-15.",
                            "Πριν κλείσουν οι οροφές: σπιράλ στον ψευδοδοκό του κλιμακοστασίου ως την οπή πάνω από την πόρτα εισόδου (ΟΠ3) και κορμοί στα ταβάνια, μέσα από τις οπές (ΗΛ-06, ΗΛ-12).",
                            "Πριν μπουν οι ντουλάπες: τα κατεβάσματα πίσω / μέσα από αυτές (τοίχοι 9, 13, 17).",
                            "Τράβηγμα καλωδίων μετά το κλείσιμο των οροφών, από τις θυρίδες και τις τρύπες των spots."]):
        f.p(s_, bullet="%d." % (j + 1), size=6.6)
    f.h("ΤΙ ΔΕΝ ΕΧΕΙ ΜΕΛΕΤΗΘΕΙ", fill=DC.WARNC)
    f.p("Ισόγειο, Δ΄ όροφος, σοφίτα, κοινόχρηστα: εδώ φαίνονται μόνο σχηματικά. Οι αριθμοί καλωδίων του shaft είναι εκτίμηση για 5 διαμερίσματα.", **B)
    DC.finish(no, "ΚΑΤΑΚΟΡΥΦΟ ΔΙΑΓΡΑΜΜΑ ΟΙΚΟΔΟΜΗΣ", "Shaft · παροχές μέσω αποθήκης · ασθενή · σειρά εργασιών")
