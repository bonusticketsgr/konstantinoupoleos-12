"""Φύλλα της ηλεκτρολογικής μελέτης Β1 (A3 οριζόντιο) – ΑΠΛΟΠΟΙΗΜΕΝΟ ΤΕΥΧΟΣ (Γιάννης 18/11: «απλοποίησε τα σχέδια»):

  ΗΛ-00 σύνοψη · ΗΛ-01 πίνακας και ζώνες · ΗΛ-02 ρευματοδότες με ύψη / αποστάσεις · ΗΛ-03 διακόπτες με ύψη / αποστάσεις ·
  ΗΛ-04 φωτισμός (κάτοψη) · ΗΛ-05 φωτισμός (τεκμηρίωση, φωτιστικά) · ΗΛ-06 περάσματα καλωδίων (κάτοψη) · ΗΛ-07 περάσματα (τομές) ·
  ΗΛ-08 κέντρο ασθενών / δίκτυο / συναγερμός / πυρανίχνευση / θερμοστάτες · ΗΛ-09 μονογραμμικό (el_det) · ΗΛ-10 πίνακας κυκλωμάτων (el_docs).

Κάθε κάτοψη δείχνει ΕΝΑ θέμα. Όλα τα σημεία, οι αποστάσεις και οι πίνακες βγαίνουν από το μοντέλο b1_el.py."""
import math
import el_draw as D
from el_draw import P, PWR, LGT, SWC, DAT, FIR, HVC, AUT, FEED, BEAMC, INK, MUTE, FAINT, PAGE_W, PAGE_H, SW, ptext, wrap
import el_checks as CK
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
    PL.bind(model); DC.bind(model); DT.bind(model)


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
      "Ρ6": (0.80, 0.66, 0.10), "Ρ7": (0.52, 0.44, 0.85)}
ZONES_P = {
    "Ρ1": [(1.705, 5.15, 6.35, 7.10), (3.30, 3.35, 6.40, 4.35), (5.449, 4.35, 6.349, 5.15)], "Ρ2": [(1.705, 7.10, 6.35, 9.115)], "Ρ8": [(6.35, 5.15, 9.325, 9.115)],
    "Ρ3": [(1.135, 0.165, 4.80, 3.25)], "Ρ4": [(6.50, 0.75, 9.395, 5.05)], "Ρ5": [(5.05, 0.80, 6.40, 3.25), (0.11, 3.16, 1.05, 5.05), (1.05, 3.50, 3.15, 5.05)],
    "Ρ6": [(9.70, 7.75, 13.76, 8.90)], "Ρ7": [(9.70, 8.90, 13.76, 9.15), (9.70, 9.15, 12.70, 10.06)]}
ZTAG = {"Ρ1": (3.60, 6.15), "Ρ2": (3.60, 8.20), "Ρ8": (7.80, 8.55), "Ρ3": (2.60, 2.75), "Ρ4": (8.00, 3.05), "Ρ5": (5.72, 2.35), "Ρ6": (12.60, 8.62), "Ρ7": (11.20, 9.42)}
ZTAG2 = [("Ρ1", 4.10, 3.60), ("Ρ5", 2.10, 4.05)]
LZ = [("Φ1", [(1.76, 5.21, 9.27, 9.06)], (5.80, 7.55)), ("Φ2", [(9.76, 7.81, 13.70, 9.09)], (10.50, 8.62)), ("Φ3", [(1.19, 0.22, 4.74, 3.19), (6.56, 0.81, 9.33, 4.99), (3.36, 3.41, 6.34, 4.29)], (2.60, 1.95)),
      ("Φ4", [(5.11, 0.86, 6.34, 3.19), (0.17, 3.56, 3.09, 4.99)], (5.72, 1.55))]
LTAG2 = [("Φ3", 8.00, 2.25), ("Φ3", 4.90, 3.60), ("Φ4", 2.10, 4.55)]
DED = [("Κ4 ψυγείο", 10.78, 8.02), ("Κ2 · Κ5 φούρνοι", 11.70, 8.20), ("Κ1 εστίες 3Φ", 12.62, 8.02), ("Κ3 πλ. πιάτων", 12.30, 9.80), ("Π1 · Π2 πλυντ. – στεγν.", 3.66, 4.47),
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
            D.halo_text(v, x, y, s_, size=4.6, color=HVC if s_[0] in "ΑΚΕ" and not s_.startswith("Κ") or s_.startswith("ΚΛ") else PWR, font="Inter-Bold")
        D.halo_text(v, 2.60, 9.90, "ΕΞ  εξώστες: ρευματοδότες IP55 + φώτα", size=4.8, color=PWR, font="Inter-Bold")
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        D.halo_text(v, 11.62, 2.62, "shaft: ΠΑΡΟΧΗ από τον πίνακα της αποθήκης (ΗΛ-11) · ΗΛ boiler (δώμα) · ασθενή", size=4.6, color=INK, font="Inter-Bold")
        PL.panel(v)
        D.halo_text(v, 5.10, 4.86, "ΚΑ · ΣΠ", size=4.4, color=DAT, font="Inter-Bold")
    PL._plan(fn, "ΗΛΕΚΤΡΙΚΟΣ ΠΙΝΑΚΑΣ ΚΑΙ ΖΩΝΕΣ ΚΥΚΛΩΜΑΤΩΝ")
    # ---- δεξιά στήλη: όψη πίνακα + πίνακες ζωνών
    y = P._head(P.TOP - 22, "ΟΨΗ ΠΙΝΑΚΑ «ΓΠ» – 5 ΣΕΙΡΕΣ × 18 ΣΤΟΙΧΕΙΑ")
    y = panel_face(P.PX + 6, y + 4, mw=12.6)
    used = M.modules_used(); tot = M.PANEL["rows"] * M.PANEL["per_row"]
    for j, s_ in enumerate(["Χωνευτός στο δυτικό άκρο του χωλ (τοίχος λουτρού γονέων)",
                            "Άνοιγμα ≈ 52 × 93 cm · από +1,02 ως +1,95 από το δάπεδο",
                            "Σε χρήση %d στοιχεία · ελεύθερα %d" % (used, tot - used)]):
        txt(P.PX - 2, y - 9 - j * 7.6, s_, size=5.8, font="Inter-SemiBold" if j == 2 else "Inter")
    y -= 36
    cc = {q["id"]: q for q in M.CIRCUITS}
    rows, colors = [], {}
    for k in ("Ρ1", "Ρ2", "Ρ8", "Ρ3", "Ρ4", "Ρ5", "Ρ6", "Ρ7"):
        q = cc[k]
        rows.append([("", dict(fill=tint(ZC[k], 0.30))), k, q["name"].replace("Ρευματοδότες ", "").replace("Ρευματοδότες", ""), "%s%d" % (q["curve"], q["In"]), q["cable"]])
    for k in ("Φ1", "Φ2", "Φ3", "Φ4"):
        q = cc[k]
        rows.append([("", dict(fill=tint(LGT, 0.45))), k, q["name"], "%s%d" % (q["curve"], q["In"]), q["cable"]])
    y = D.table(P.PX - 4, y, [10, 18, P.PW - 10 - 18 - 24 - 28 + 8, 24, 28], rows, head=["", "", "ΖΩΝΕΣ: ΡΕΥΜΑΤΟΔΟΤΕΣ (χρώμα) · ΦΩΤΙΣΜΟΣ (πλαίσιο)", "ΑΣΦ.", "mm²"], size=5.3, lead=6.5, pad=2.0, zebra=False)
    rows = []
    for k in ("Κ1", "Κ2", "Κ3", "Κ4", "Κ5", "Π1", "Π2", "ΑΘ", "ΚΛ", "ΑΚ", "ΕΝ", "ΕΞ", "ΚΑ", "ΣΠ", "ΗΛ"):
        q = cc[k]
        nm = q["name"].split(" – ")[0].split(" (")[0]
        rows.append([k, nm, "%s%d" % (q["curve"], q["In"]), q["cable"]])
    D.table(P.PX - 4, y - 5, [22, P.PW - 22 - 24 - 28 + 8, 24, 28], rows, head=["", "ΑΠΟΚΛΕΙΣΤΙΚΕΣ ΓΡΑΜΜΕΣ", "ΑΣΦ.", "mm²"], size=5.3, lead=6.4, pad=1.7, bold_first=True)
    PL._finish(no, "ΠΙΝΑΚΑΣ ΚΑΙ ΖΩΝΕΣ", "Θέση και διάταξη πίνακα · ποιο κύκλωμα τροφοδοτεί ποιον χώρο")


# ================================================================ ΗΛ-02 ΡΕΥΜΑΤΟΔΟΤΕΣ
SOCK_AT = {"Π01": (0.38, 0.36), "Π04": (0.46, -0.03), "Π61": (-0.40, 0.10), "Π62": (-0.40, -0.06), "Π24": (0.46, 0.0), "Π63": (0.44, -0.08), "Π44": (-0.40, 0.10), "Π08": (-0.34, -0.22), "Π60": (0.30, 0.20), "Π54": (0.0, 0.34), "Π55": (0.0, 0.20), "Π51": (-0.10, 0.20), "Π52": (0.12, 0.34), "Π50": (0.0, 0.20), "Π13": (-0.20, -0.20), "Π14": (0.0, -0.20),
           "Π11": (0.36, -0.03), "Π12": (0.36, 0.04), "Π59": (0.0, -0.20)}


def sheet_02(no="ΗΛ-02"):
    def fn(v):
        PL.ac_units(v, faint=True)
        PL.sockets(v)
        pts = []
        for s in M.SOCKETS:
            opt = PL._opt(s, 10)
            inside = opt.get("surf") or s[0] in CK.INSIDE_OK
            tag(v, s[1], s[2], s[3], s[0][1:] if inside else "%s · %s" % (s[0][1:], fz(s[6])), PWR, at=SOCK_AT.get(s[0]))
            if not inside and s[8] != "ΕΞ":
                pts.append((s[1], s[2], s[3]))
        for f in M.FIXED:
            tag(v, f[1], f[2], f[3], "%s · %s" % (f[0], fz(f[4])), HVC, at={"ΑΘ": (0.48, -0.07), "ΚΛ": (0.48, 0.07), "ΚΜ3": (0.50, 0.0)}[f[0]])
        dims(v, pts)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΡΕΥΜΑΤΟΔΟΤΕΣ – ΘΕΣΕΙΣ, ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ")
    y = P.legend(["e_sock", "e_sock2", "e_usb", "e_sockip", "e_ded", "e_fix", "e_fixm", "e_dim"])
    txt(P.PX - 2, y + 2, "Ετικέτα: αριθμός · ύψος άξονα κουτιού από το τελικό δάπεδο (m).", size=5.6, font="Inter-SemiBold")
    rows = []
    for s in M.SOCKETS:
        opt = PL._opt(s, 10)
        inside = opt.get("surf") or s[0] in CK.INSIDE_OK
        rows.append([s[0][1:], fz(s[6]), "ερμάριο" if inside else ("όψη" if s[8] == "ΕΞ" else ref_txt(s[1], s[2], s[3])), s[7], ("%d× " % s[4] if s[4] > 1 else "") + s[9].split(" – ")[0].split(" (")[0]])
    for f in M.FIXED:
        rows.append([f[0], fz(f[4]), "—", f[5], f[7].split(" – ")[0]])
    D.table(P.PX - 4, y - 8, [18, 22, 40, 20, P.PW - 100 + 8], rows, head=["Π", "ΥΨΟΣ", "ΑΠΟ", "ΚΥΚΛ.", "ΧΡΗΣΗ"], size=5.1, lead=6.2, pad=1.55, bold_first=True, aligns={1: "r"})
    PL._finish(no, "ΡΕΥΜΑΤΟΔΟΤΕΣ – ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ", "Π01–Π63 · ύψος από το δάπεδο · απόσταση από γωνία / κάσα")


# ================================================================ ΗΛ-03 ΔΙΑΚΟΠΤΕΣ
KIND_TXT = {"1": "απλός", "2": "αλέ-ρετούρ", "X": "ενδιάμεσος", "D": "dimmer", "R": "ρολό ▲▼"}
SW_AT = {"Δ10": (0.66, -0.06), "Δ16": (0.40, 0.16), "Δ15": (-0.40, -0.30), "Δ14": (0.52, -0.32), "Δ13": (-0.42, 0.20), "Δ2": (0.16, 0.30), "Δ6": (0.0, 0.30)}


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
    y = P.legend(["e_sw", "e_sw2", "e_swx", "e_dimmer", "e_grp", "e_dim"])
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


SPOT_KIND = {"s": "σταθερό", "adj": "ρυθμιζόμενο", "s44": "IP44", "s65": "IP65"}


def sheet_04(no="ΗΛ-04"):
    def fn(v):
        for cu in A.CURTAINS:
            v.rect(*cu["rect"], fill=(0.93, 0.93, 0.95), stroke=(0.75, 0.75, 0.78), lw=0.3)
        D.zone(v, (A.STRIP_X, 5.15, A.LIN_X, 8.915), LGT, alpha=0.05, dash=(3, 2), lw=0.4)
        for u in A.UNITS:
            D.unit_rect(v, u["rect"], col=(0.78, 0.68, 0.88), dashed=True, alpha=0.10)
        for h in A.HATCHES:
            C().saveState(); C().setDash([1.5, 1.5]); v.rect(*h["rect"], stroke=(0.6, 0.6, 0.65), lw=0.4); C().restoreState()
        PL.detectors(v, faint=True)
        PL.switches(v, faint=True)
        # άξονες του κανάβου (καθιστικό, Υπν.2)
        for xs, ys in ((M.LIV_X, M.LIV_Y), (M.B2_X, M.B2_Y)):
            for x_ in xs:
                D.route(v, [(x_, ys[0] - 0.22), (x_, ys[-1] + 0.22)], col=LGT, lw=0.35, halo=False, dash=[1.2, 1.6])
            for y_ in ys:
                D.route(v, [(xs[0] - 0.22, y_), (xs[-1] + 0.22, y_)], col=LGT, lw=0.35, halo=False, dash=[1.2, 1.6])
        def chain(vals, at, horiz):
            for a_, b_ in zip(vals, vals[1:]):
                pa, pb = ((a_, at), (b_, at)) if horiz else ((at, a_), (at, b_))
                D.dim_chain(v, pa, pb, fz(b_ - a_))
        chain([1.905] + list(M.LIV_X) + [M.A.STRIP_X], 8.66, True)
        chain([5.15] + list(M.LIV_Y) + [8.915], 2.20, False)
        chain([6.50] + list(M.B2_X) + [9.365], 3.25, True)
        chain([1.35] + list(M.B2_Y) + [4.85], 9.10, False)
        PL.lights(v, labels=True, groups=True)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΦΩΤΙΣΜΟΣ: SPOTS ΣΕ ΚΑΝΑΒΟ · ΚΑΘΡΕΠΤΕΣ ΜΕ ΦΩΣ · ΕΞΩΣΤΕΣ ΟΠΩΣ ΤΑ ΠΡΟΟΠΤΙΚΑ")
    y = P.legend(["e_spot", "e_spot44", "e_spot65", "e_extc", "e_led", "e_mir", "e_ext", "e_grp", "e_det"])
    rows = []
    for q in M.SPOTS:
        a, b = _ceil_dist(q[2], q[3])
        rows.append([q[0], SPOT_KIND[q[1]], a, b, q[5]])
    y = D.table(P.PX - 4, y - 2, [24, 40, 28, 28, P.PW - 120 + 8], rows, head=["", "ΕΙΔΟΣ", "ΑΠΟ", "ΑΠΟ", "ΤΙ ΦΩΤΙΖΕΙ"], size=4.9, lead=5.9, pad=1.35, bold_first=True)
    txt(P.PX - 2, y - 8, "ΑΠΟ: m από τον κοντινότερο τοίχο / ντουλάπα (Β βόρεια · Ν νότια · Δ δυτικά · Α ανατολικά).", size=5.2, color=MUTE)
    PL._finish(no, "ΦΩΤΙΣΜΟΣ – ΚΑΤΟΨΗ", "Μόνο χωνευτά spots · κάναβος · ομάδες · θέσεις από τοίχους")


# ================================================================ ΗΛ-06 ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ
HOLEC = (0.62, 0.10, 0.62)
HOLE_LAB = {"ΟΠ5": (-0.34, -0.40), "ΟΠ1": (0.20, -0.62), "ΟΠ2": (0.40, -0.38), "ΟΠ3": (0.62, 0.0), "ΟΠ4": (0.62, 0.0)}


def _holes(v, labels=True):
    """Οπές Ø75 στα δοκάρια: γραμμή μέσα από το πλάτος της δοκού + ετικέτα."""
    c = C()
    for h in CK.holes():
        a_, b_ = ((h["x"], h["y"] - 0.15), (h["x"], h["y"] + 0.15)) if h["horiz"] else ((h["x"] - 0.15, h["y"]), (h["x"] + 0.15, h["y"]))
        (X0, Y0), (X1, Y1) = v.p(*a_), v.p(*b_)
        c.saveState(); c.setLineCap(0)
        c.setStrokeColorRGB(1, 1, 1); c.setLineWidth(4.6); c.line(X0, Y0, X1, Y1)
        c.setStrokeColorRGB(*HOLEC); c.setLineWidth(2.6); c.line(X0, Y0, X1, Y1); c.restoreState()
        if labels:
            dx, dy = HOLE_LAB[h["id"]]
            v.line(h["x"], h["y"], h["x"] + dx, h["y"] + dy, color=HOLEC, lw=0.5)
            X2, Y2 = v.p(h["x"] + dx, h["y"] + dy); P.pill(X2, Y2, h["id"], None, HOLEC, "c", 5.2)
def _routes(v):
    if True:
        PL.beams(v, names=True)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        D.halo_text(v, 10.375, 2.64, "shaft Η/Μ", size=4.8, color=DAT)
        PL.sockets(v, faint=True); PL.switches(v, faint=True)
        for r in M.WALL_RUNS:
            D.route(v, r["pts"], col=PL.WALLC, lw=2.0 if r.get("new") else 1.5, dash=[2.6, 1.6], lab=r["id"] if r.get("new") else None, seg=r.get("lseg"), lsize=4.8)
        for r in M.ROUTES:
            col = HVC if r["kind"] == "hvac" else (DAT if r["kind"] == "weak" else PWR)
            D.route(v, r["pts"], col=col, lw=2.2 if r["n"].startswith("κορμός") else 1.5, arrows=True, lab=r["n"] or None, dash=[4, 1.6] if r["kind"] == "weak" else None)
        D.route(v, M.OUT_ROUTE, col=FEED, lw=1.3, dash=[3, 1.5], arrows=True, lab=None)
        D.route(v, M.FEED_ROUTE, col=FEED, lw=2.6, arrows=True, lab="ΠΑΡΟΧΗ 5×16", seg=0)
        for p in M.PASSES:
            D.pass_zone(v, p["rect"], lab=p["id"], lab_at=p["lab"])
        PL.panel(v)
        _holes(v)
        v.rect(3.40, 8.915, 4.10, 9.115, fill=None, stroke=CABLE, lw=0.9)
        D.halo_text(v, 4.62, 8.78, "κουρτινόθηκη", size=4.2, color=CABLE)


def sheet_06(no="ΗΛ-06"):
    PL._plan(_routes, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΟΛΑ ΑΠΟ ΤΑ ΤΑΒΑΝΙΑ ΚΑΙ ΚΑΤΩ ΣΤΟΥΣ ΤΟΙΧΟΥΣ · 5 ΟΠΕΣ Ø75 ΣΕ ΔΟΚΑΡΙΑ")
    y = P.legend(["e_feed", "e_out", "e_trunk", "e_weakr", "e_hvacr", "e_hole", "e_pass", "e_wallrun", "beam", "e_tn"])
    rows = [[p["id"], p["beam"], p["title"] + ": " + p["how"] + "."] for p in M.PASSES]
    colors = {i: (1.0, 0.93, 0.80) for i, p in enumerate(M.PASSES) if p["new"]}
    y = D.table(P.PX - 4, y - 2, [18, 30, P.PW - 48 + 8], rows, head=["", "ΔΟΚΟΣ", "ΠΕΡΑΣΜΑ – ΠΩΣ ΠΕΡΝΟΥΝ ΤΑ ΚΑΛΩΔΙΑ ΤΗ ΔΟΚΟ"], size=5.2, lead=6.3, pad=2.0, bold_first=True, colors=colors, zebra=False)
    rows = [[r["id"], r["short"] + ". Περνούν: " + r["what"] + "."] for r in M.WALL_RUNS if r.get("new")]
    y = D.table(P.PX - 4, y - 5, [18, P.PW - 18 + 8], rows, head=["", "ΤΟΙΧΟΙ ΤΟΥ ΣΑΛΟΝΙΟΥ – ΠΩΣ ΦΤΑΝΕΙ ΤΟ ΚΑΛΩΔΙΟ ΧΩΡΙΣ ΠΑΤΩΜΑ"], size=5.2, lead=6.3, pad=2.0, bold_first=True)
    txt(P.PX - 2, y - 9, "Τίποτα στο πάτωμα · κανένα πρέκι / κούτελο. Τομές: ΗΛ-07 · τι περνά από κάθε οπή: ΗΛ-12.", size=5.4, color=MUTE)
    PL._finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ", "Παροχή από το shaft · οπές Ø75 στα δοκάρια · κορμοί ισχυρών / ασθενών")


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


def _cap(x, y, s, sub):
    txt(x, y, s, size=7.6, font="Inter-Bold")
    ln(x, y - 3, x + SW(s, "Inter-Bold", 7.6), y - 3, lw=0.9)
    txt(x, y - 12, sub, size=5.8, color=MUTE)


def _beam(sc, h0, h1, zs, name, sec):
    sc.rect(h0, zs, h1, 2.98, fill=BEAMF)
    sc.text((h0 + h1) / 2, 2.74, name, size=6.4, font="Inter-Bold", color=(1, 1, 1), anchor="c"); sc.text((h0 + h1) / 2, 2.67, sec, size=5.4, color=(1, 1, 1), anchor="c")


def _hole_sec(sc, h0, h1, z):
    """Η οπή Ø75 σε τομή: χιτώνιο μέσα από το πλάτος της δοκού."""
    r = M.HOLE_D / 2
    sc.rect(h0, z - r, h1, z + r, fill=(1, 1, 1), stroke=HOLEC, lw=1.0)
    sc.line(h0 - 0.03, z, h1 + 0.03, z, col=HOLEC, lw=0.4, dash=[3, 1.2, 0.8, 1.2])


def sec_p1(x, ytop):
    """Τομή Β–Ν στην οπή ΟΠ3 (x = 5,60, βλέπουμε προς ανατολή): κενό χωλ | Δ3.1 με την οπή Ø60 στη μέση του ύψους | κενό καθιστικού."""
    _cap(x, ytop, "Π1 · ΧΩΛ ↔ ΣΑΛΟΝΙ: ΟΠ5, ΟΠ1 στη Δ3.1", "τομή Β–Ν μέσα από την οπή · 1:12,5")
    a, b = 4.38, 5.62; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.80, 4.85, 2.98, fill=CONC); sc.rect(5.15, 2.78, b, 2.98, fill=CONC); _beam(sc, 4.85, 5.15, 2.48, "Δ3.1", "30/50")
    sc.rect(a, 2.70, 4.85, 2.7125, fill=GYP, lw=0.4)                           # οροφή χωλ +2,70
    sc.rect(4.8375, 2.4675, 4.85, 2.70, fill=GYP, lw=0.4)                      # παρειά δοκού προς το χωλ
    sc.rect(4.8375, 2.4675, 5.1625, 2.48, fill=GYP, lw=0.4)                    # κάτω παρειά δοκού (άνοιγμα +2,48 – ΔΕΝ αλλάζει)
    sc.rect(5.15, 2.4675, 5.1625, 2.68, fill=GYP, lw=0.4)                      # παρειά δοκού προς το σαλόνι
    sc.rect(5.15, 2.68, b, 2.6925, fill=GYP, lw=0.4)                           # οροφή σαλονιού +2,68
    _hole_sec(sc, 4.85, 5.15, 2.73)
    _path(sc, [(a + 0.03, 2.745), (4.78, 2.745), (4.86, 2.73), (5.14, 2.73), (5.22, 2.735), (b - 0.03, 2.735)], lw=1.6)
    sc.dimv(5.30, 2.73, 2.98, "25", off=4)
    sc.dimv(5.42, 2.48, 2.73, "25", off=4)
    sc.text(a + 0.02, 2.60, "ΧΩΛ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.535, "οροφή +2,70 → +2,68", size=5.2, color=MUTE)
    sc.text(b - 0.02, 2.585, "ΣΑΛΟΝΙ", size=5.8, font="Inter-Bold", anchor="r"); sc.text(b - 0.02, 2.52, "οροφή +2,68", size=5.2, color=MUTE, anchor="r")
    sc.text(5.00, 2.40, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=6.2, font="Inter-Bold", color=HOLEC, anchor="c")
    sc.text(5.00, 2.335, "στη μέση του ύψους του δοκαριού", size=5.2, color=HOLEC, anchor="c")
    sc.text(5.00, 2.28, "25 cm από πάνω · 25 cm από κάτω", size=5.2, color=HOLEC, anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98 άνω στάθμη πλάκας", size=5.2, color=MUTE, dy=3)
    sc.text(a + 0.02, 2.14, "ΚΕΝΟ ΟΡΟΦΗΣ → ΚΕΝΟ ΟΡΟΦΗΣ", size=5.6, font="Inter-Bold")
    sc.text(a + 0.02, 2.075, "κανένα πρέκι, κανένα κούτελο – το άνοιγμα μένει +2,48", size=5.2, color=MUTE)
    sc.text(a + 0.02, 2.02, "ΟΠ5 παροχή + ασθενή 3,10 m · ΟΠ1 ισχυρά 3,50 m από τη δυτική κολόνα", size=5.2, color=MUTE)
    sc.text(a + 0.02, 1.965, "ΟΠ2 (ψυκτικά + αποχέτευση Ø32): ίδια τομή, 0,80 m από την Κ3", size=5.2, color=MUTE)


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
    sc.text(a + 0.02, 2.42, "οροφή +2,48 περασιά με το δοκάρι", size=5.2, color=MUTE)
    sc.text(9.55, 2.36, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=6.2, font="Inter-Bold", color=HOLEC, anchor="c")
    sc.text(9.55, 2.295, "στη μέση του ύψους του δοκαριού", size=5.2, color=HOLEC, anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98", size=5.2, color=MUTE, dy=3)
    sc.text(a + 0.02, 2.14, "ΠΑΝΩ ΑΠΟ ΤΟ ΑΝΟΙΓΜΑ ΤΗΣ ΚΟΥΖΙΝΑΣ", size=5.6, font="Inter-Bold")
    sc.text(a + 0.02, 2.075, "ΟΠ4: 1,20 m από την παρειά της κολόνας Κ8 (νότια)", size=5.2, color=MUTE)
    sc.text(a + 0.02, 2.02, "= 20 cm από το τέλος του τοίχου κουζίνας – σκάλας", size=5.2, color=MUTE)
    sc.text(a + 0.02, 1.965, "στη μέση του μήκους του δοκαριού από πίσω είναι η σκάλα", size=5.2, color=MUTE)


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
    sc.text(a + 0.02, 2.10, "τοίχος πόρτας 15 cm,", size=5.2, color=MUTE); sc.text(a + 0.02, 2.045, "περασιά με το δοκάρι", size=5.2, color=MUTE)
    sc.text(9.62, 2.365, "ΧΙΤΩΝΙΟ Ø75 · κέντρο +2,73", size=5.6, font="Inter-Bold", color=HOLEC)
    sc.text(9.62, 2.27, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=5.8, font="Inter-Bold"); sc.text(9.62, 2.21, "ψευδοδοκός καλωδίων +2,43", size=5.2, color=MUTE); sc.text(9.62, 2.155, "από το shaft Η/Μ", size=5.2, color=MUTE)
    sc.text(9.62, 2.10, "σφράγιση με πυράντοχη μαστίχη", size=5.2, color=MUTE)
    sc.text(b - 0.01, 2.685, "οροφή +2,73", size=5.0, color=MUTE, anchor="r")


def det_panel(x, ytop):
    """Κάτοψη 1:10 του πίνακα μέσα στον τοίχο Τ2Α-01 (ανατολή = χωλ πάνω): 2 γυψ. + CW 100 + 2 γυψ. = 15 cm."""
    _cap(x, ytop, "Ο ΠΙΝΑΚΑΣ ΣΤΟΝ ΤΟΙΧΟ ΤΟΥ ΛΟΥΤΡΟΥ ΓΟΝΕΩΝ", "κάτοψη του τοίχου · 1:12,5 · πάνω το χωλ, κάτω το λουτρό")
    s = S12
    wb = W.bbox([w for w in W.WALLS if w["id"] == M.PANEL_WALL][0]["pts"])
    xw, xe = wb[0], wb[2]
    sc = Sec(x + 14, ytop - 172, s, 3.30, xw - 0.08)       # h = y (Β → Ν), z = x (Δ → Α)
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
    sc.rect(M.KM2_DROP_NEW - 0.016, xw + 0.05, M.KM2_DROP_NEW + 0.016, xw + 0.082, fill=(0.86, 0.50, 0.90), lw=0.4)     # συμπυκνώματα ΚΜ2 – νέα θέση
    sc.text((y0w + y1w) / 2, xe + 0.075, "ΧΩΛ – δυτικό άκρο", size=5.8, font="Inter-Bold", anchor="c")
    sc.text((y0w + y1w) / 2, xw - 0.03, "ΛΟΥΤΡΟ ΓΟΝΕΩΝ (πλακάκι)", size=5.8, font="Inter-Bold", anchor="c", dy=-10)
    sc.dimh(M.PANEL["y0"], M.PANEL["y1"], xe + 0.03, "άνοιγμα 52 cm", off=3)
    sc.dimh(y0w, M.PANEL["y0"], xe + 0.03, "9", off=3)
    sc.dimv(3.31, xe - 0.07, xe, "7", off=-4)
    sc.text((y0w + y1w) / 2, xw - 0.03, "πίνακας 7 cm (ή 9) · μέσα στον τοίχο 12,5 cm", size=5.4, color=MUTE, anchor="c", dy=-22)
    sc.text((y0w + y1w) / 2, xw - 0.03, "μοβ: συμπυκνώματα split Υπν.1 – ΝΕΑ θέση", size=5.4, color=MUTE, anchor="c", dy=-31)


def sheet_07(no="ΗΛ-07"):
    y = DC.title("ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "5 οπές με χιτώνιο Ø75 σε δύο δοκάρια (3 + 2) · κανένας σωλήνας μέσα στην πλάκα · κανένα πρέκι / κούτελο · τίποτα στο πάτωμα")
    X0 = DC.X0
    xs = [X0, X0 + 283, X0 + 573, X0 + 863]
    sec_p1(xs[0], y); sec_p2(xs[1], y); sec_p0(xs[2], y); det_panel(xs[3], y)
    yb = y - 350
    ln(X0, yb + 6, DC.X1, yb + 6, col=FAINT, lw=0.5)
    w = 265
    f = [DC.Flow(xs[i], yb, w, size=6.2, name="ΗΛ-07/%d" % i) for i in range(4)]
    B = dict(bullet="•", size=6.2)
    f[0].h("ΔΟΚΑΡΙ ΣΑΛΟΝΙΟΥ (Δ3.1) – ΟΠ5, ΟΠ1, ΟΠ2", fill=HOLEC)
    f[0].p("Χιτώνιο PVC Ø75 στο καλούπι, κέντρο στη μέση του ύψους του δοκαριού (25 cm κάτω από την άνω στάθμη της πλάκας).", **B)
    f[0].p("ΟΠ5 (3,10 m από τη δυτική κολόνα): κεντρική παροχή + boiler και όλα τα ασθενή σε δικό τους σπιράλ Ø40. ΟΠ1 (3,50 m): όλα τα ισχυρά σαλονιού και κουζίνας.", **B)
    f[0].p("ΟΠ2, 0,80 m από την κολόνα Κ3: ψυκτικά και αποχέτευση Ø32 του κλιματιστικού σαλονιού. Ο Ø32 ψηλά στο χιτώνιο, με κλίση 1 % από το μηχάνημα ως τον τοίχο του λουτρού.", **B)
    f[0].p("Οροφές: χωλ +2,68 αντί +2,70 (για το στόμιο των χιτωνίων) · Υπν.2 +2,65 (για την κλίση της αποχέτευσης).", **B)
    f[1].h("ΔΟΚΑΡΙ ΚΟΥΖΙΝΑΣ (Δ9.1) – ΟΠ4", fill=HOLEC)
    f[1].p("Πάνω από το άνοιγμα της κουζίνας, 1,20 m από την κολόνα Κ8. Από το κενό της λωρίδας ίσια στο κενό της κουζίνας.", **B)
    f[1].p("Ισχυρά κουζίνας και τοίχου εισόδου· τα 5 ασθενή μέσα σε δικό τους σπιράλ Ø20, στο ίδιο χιτώνιο.", **B)
    f[1].p("Ο τοίχος της εισόδου είναι κάτω από το δοκάρι, περασιά: οι διακόπτες και η πρίζα του παίρνουν ρεύμα από το ταβάνι της κουζίνας, μέσα από τον τοίχο κουζίνας – σκάλας (Τ5).", **B)
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
    rows = [[p["id"], p["beam"], p["title"], p["how"] + ".", p["what"], p["n"]] for p in M.PASSES]
    rows += [[r["id"], "τοίχος", r["short"].split(":")[0].split(" (")[0], r["short"].split(": ", 1)[-1] + ".", r["what"], "—"] for r in M.WALL_RUNS if r.get("new")]
    colors = {i: (1.0, 0.93, 0.80) for i, p in enumerate(M.PASSES) if p["new"]}
    widths = [24, 46, 150, 420, 330, 110]; sc_ = (DC.X1 - X0) / float(sum(widths))
    yy = D.table(X0, yc, [w_ * sc_ for w_ in widths], rows, head=["", "ΔΟΚΟΣ", "ΑΠΟ ↔ ΠΡΟΣ", "ΠΩΣ ΠΕΡΝΟΥΝ", "ΤΙ ΠΕΡΝΑ", "ΣΩΛΗΝΕΣ"], size=5.9, lead=7.0, pad=2.2, bold_first=True, colors=colors, zebra=False)
    assert yy >= DC.YB - 2, "ΗΛ-07: ο πίνακας περασμάτων ξεχειλίζει %.0f pt" % (DC.YB - yy)
    DC.finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "Οπές Ø75: Π1 χωλ ↔ σαλόνι · Π2 κουζίνα · Π0 shaft · ο πίνακας στον τοίχο", "Τομές και κάτοψη τοίχου 1:12,5 · A3")


# ================================================================ ΗΛ-08 ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ – ΔΙΚΤΥΟ – ΣΥΝΑΓΕΡΜΟΣ – ΠΥΡΑΝΙΧΝΕΥΣΗ – ΘΕΡΜΟΣΤΑΤΕΣ
LOOPS = [("Κ1", (1.705, 5.15, 6.20, 9.115), "Θ1"), ("Κ2", (6.20, 5.15, 9.325, 9.115), "Θ1"), ("Κ3", (9.70, 7.75, 13.76, 10.06), "Θ1"), ("Κ4", (6.50, 1.35, 9.395, 5.05), "Θ3"),
         ("Κ5", (5.05, 0.80, 6.40, 3.25), "Θ4"), ("Κ6", (1.135, 0.165, 4.20, 3.25), "Θ2"), ("Κ7", (0.11, 3.50, 3.15, 5.05), "Θ5")]
ZCOL = {"Θ1": (0.95, 0.55, 0.15), "Θ2": (0.20, 0.55, 0.85), "Θ3": (0.25, 0.65, 0.35), "Θ4": (0.65, 0.35, 0.75), "Θ5": (0.85, 0.30, 0.45)}
LOOP_TAG = {"Κ1": (3.20, 7.60), "Κ2": (7.60, 7.95), "Κ3": (11.30, 9.05), "Κ4": (8.30, 3.20), "Κ5": (5.90, 1.80), "Κ6": (2.40, 2.30), "Κ7": (1.75, 4.30)}
WEAK_AT = {"Θ4": (-0.36, 0.14), "Θ5": (0.42, -0.36), "D2": (0.10, 0.26), "Χ1": (0.26, 0.26), "Θ1": (-0.26, 0.26), "ΚΟ": (0.44, 0.10), "ΦΕ": (0.44, -0.06), "ΘΤ": (-0.50, -0.08), "ΠΛ": (-0.50, 0.08),
           "TV1": (0.20, -0.26), "D1": (-0.22, -0.26), "TV2": (0.26, -0.26), "D3": (-0.22, -0.26), "TV3": (0.26, -0.26), "D5": (-0.20, -0.26)}


def sheet_08(no="ΗΛ-08"):
    det = {d[0]: (d[2], d[3]) for d in A.DETECTORS}
    def fn(v):
        for k, r, th in LOOPS:
            D.zone(v, r, ZCOL[th], alpha=0.10, stroke=False)
            X, Y = v.p(*LOOP_TAG[k]); P.pill(X, Y, k, th, ZCOL[th], "c", 5.6)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        D.route(v, [(10.375, 2.93), (10.06, 3.05), (10.06, 5.68), (9.375, 5.68), (9.05, 5.68), (9.05, 6.20), (4.62, 6.20), (4.62, 5.02), (5.02, 4.74)], col=DAT, lw=1.8, arrows=True,
                lab="από το shaft: οπτική ίνα · κεραία TV · θυροτηλεόραση", seg=5, side=-1)
        PL.detectors(v, labels=True)
        D.ceil_dev(v, 4.45, 3.85, "Σ", col=FIR, r=0.085, fill=True)
        PL.thermostats(v)
        PL.data(v)
        D.cabinet(v, M.ALARM_PANEL, col=ALARMC)
        for sh in M.SHUTTERS:
            x, y, d = sh["motor"]; nx, ny = D.VEC[d]
            v.circle(x + nx * 0.06, y + ny * 0.06, 0.05, fill=ALARMC, stroke=(1, 1, 1), lw=0.6)
        v.circle(9.40, 5.42, 0.05, fill=ALARMC, stroke=(1, 1, 1), lw=0.6)
        pts = []
        for d in M.DATA:
            tag(v, d[1], d[2], d[3], "%s · %s" % (d[0], fz(d[5])), DAT, off=0.26, at=WEAK_AT.get(d[0])); pts.append((d[1], d[2], d[3]))
        for t in M.TV:
            tag(v, t[1], t[2], t[3], "%s · %s" % (t[0], fz(t[4])), DAT, off=0.26, at=WEAK_AT.get(t[0])); pts.append((t[1], t[2], t[3]))
        for t in M.THERMOSTATS:
            tag(v, t[1], t[2], t[3], "%s · %s" % (t[0], fz(M.H_TH)), AUT, off=0.28, at=WEAK_AT.get(t[0]))
            if not PL._opt(t, 7).get("off"):
                pts.append((t[1], t[2], t[3]))
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
    PL._plan(fn, "ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ · ETHERNET · TV · ΣΥΝΑΓΕΡΜΟΣ · ΠΥΡΑΝΙΧΝΕΥΣΗ · ΘΕΡΜΟΣΤΑΤΕΣ")
    y = P.legend(["e_tn", "e_cab", "e_data", "e_data2", "e_tv", "e_wdev", "e_alarm", "e_contact", "e_det", "e_heat", "e_siren", "e_th", "e_man", "e_loop"])
    rows = [["Modem – router", "του παρόχου, με Wi-Fi· η οπτική ίνα έρχεται ως εδώ. Στη μέση της κάτοψης → καλύπτει όλο το σπίτι"],
            ["Δίκτυο", "πλαίσιο 12 θυρών Cat 6A + switch 8 θυρών· κάθε λήψη τοίχου έχει δικό της καλώδιο ως εδώ (αστέρας)"],
            ["TV", "διανομή κεραίας / δορυφορικής προς 3 λήψεις"],
            ["Συναγερμός – πυρανίχνευση", "πίνακας ΠΣ με μπαταρία· πληκτρολόγιο στην είσοδο, επαφές σε πόρτα και 4 κουφώματα, ανιχνευτής κίνησης"],
            ["Ρεύμα", "2 διπλοί ρευματοδότες στο κύκλωμα ΚΑ + κύκλωμα ΣΠ για τον πίνακα συναγερμού"],
            ["Κατασκευή", "το ανατολικό 0,50 m της ντουλάπας του χωλ με δική του πόρτα και περσίδα αερισμού"]]
    y = D.table(P.PX - 4, y - 2, [58, P.PW - 58 + 8], rows, head=["ΚΕΝΤΡΟ ΑΣΘΕΝΩΝ – ΤΙ ΕΧΕΙ ΜΕΣΑ", ""], size=5.1, lead=6.2, pad=1.8, bold_first=True)
    rows = [[d[0], "%d × RJ45" % d[4], fz(d[5]), ref_txt(d[1], d[2], d[3]), d[7].split(" (")[0]] for d in M.DATA]
    rows += [[t[0], "TV", fz(t[4]), ref_txt(t[1], t[2], t[3]), "κεραία / δορυφορική"] for t in M.TV]
    rows += [[d[0], {"data": "RJ45", "alarm": "δίαυλος", "fire": "2×1,5"}[d[6]] if d[0] != "ΚΟ" else "2×0,8", fz(d[5]), ref_txt(d[1], d[2], d[3]) if d[3] == "W" else "πλατύσκ.", d[7].split(" (")[0].split(" – ")[0]] for d in M.WALL_DEV]
    rows += [[t[0], "θερμοστ.", fz(M.H_TH), ref_txt(t[1], t[2], t[3]), "%s → %s" % (t[4].replace("ΚΑΘ", "καθιστικό – κουζίνα").replace("ΥΠ1", "Υπν.1").replace("ΥΠ2", "Υπν.2").replace("ΧΩΛ", "λουτρό") if t[0] != "Θ5" else "λουτρό γονέων", " · ".join(t[5]))] for t in M.THERMOSTATS]
    y = D.table(P.PX - 4, y - 5, [20, 34, 22, 40, P.PW - 116 + 8], rows, head=["", "ΛΗΨΗ", "ΥΨΟΣ", "ΑΠΟ", "ΧΡΗΣΗ"], size=5.0, lead=6.0, pad=1.5, bold_first=True, aligns={2: "r"})
    rows = [["Πυρανίχνευση", "4 ανιχνευτές καπνού (καθιστικό, Υπν.1, Υπν.2, χωλ) + 1 θερμοδιαφορικός στην κουζίνα – θέσεις των ανόψεων· σειρήνα στο χωλ, επαναλήπτης στο πλατύσκαλο"],
            ["Θερμοστάτες", "5 ζώνες: κάθε θερμοστάτης ανοίγει / κλείνει ΜΟΝΟ τα κυκλώματα της ζώνης του μέσω του κέντρου ζωνών στον συλλέκτη (7 κινητήρες)· των λουτρών έξω από την πόρτα, με αισθητήριο δαπέδου"],
            ["Χωρίς KNX", "συμβατική καλωδίωση· ό,τι «έξυπνο» χρειαστεί (θερμοστάτες, συναγερμός) δουλεύει μέσω του modem"]]
    D.table(P.PX - 4, y - 5, [48, P.PW - 48 + 8], rows, size=5.0, lead=6.0, pad=1.6, bold_first=True)
    PL._finish(no, "ΑΣΘΕΝΗ ΡΕΥΜΑΤΑ – ΘΕΡΜΟΣΤΑΤΕΣ", "Κέντρο ασθενών · Ethernet σε κάθε δωμάτιο · συναγερμός · πυρανίχνευση")


# ================================================================ ΗΛ-00 ΣΥΝΟΨΗ
SHEETS = [("ΗΛ-00", "Σύνοψη: τι άλλαξε, τι χρειάζεται απόφαση"), ("ΗΛ-01", "Ηλεκτρικός πίνακας και ζώνες κυκλωμάτων"), ("ΗΛ-02", "Ρευματοδότες – ύψη και αποστάσεις"),
          ("ΗΛ-03", "Διακόπτες – ύψη, αποστάσεις, τι ανάβει ο καθένας"), ("ΗΛ-04", "Φωτισμός – κάτοψη"), ("ΗΛ-05", "Φωτισμός – τεκμηρίωση και φωτιστικά"),
          ("ΗΛ-06", "Περάσματα καλωδίων – κάτοψη"), ("ΗΛ-07", "Περάσματα καλωδίων – τομές · ο πίνακας στον τοίχο"),
          ("ΗΛ-08", "Κέντρο ασθενών · Ethernet · συναγερμός · πυρανίχνευση · θερμοστάτες"), ("ΗΛ-09", "Μονογραμμικό σχέδιο – όψη πίνακα"), ("ΗΛ-10", "Πίνακας κυκλωμάτων και προστασιών"),
          ("ΗΛ-11", "Υπόγειο: μετρητής → πίνακας αποθήκης → φορτιστής και παροχή σπιτιού"),
          ("ΗΛ-12", "ΣΩΛΗΝΩΣΕΙΣ ορόφου: οι 5 οπές Ø75 – θέση και τι περνά από καθεμία · λοιπά περάσματα"), ("ΗΛ-13", "Κατακόρυφο διάγραμμα οικοδομής: shaft, παροχές, ασθενή")]


def sheet_00(no="ΗΛ-00"):
    y = DC.title("ΗΛΕΚΤΡΟΛΟΓΙΚΗ ΜΕΛΕΤΗ – Β1 (Α΄ · Β΄ · Γ΄ ΟΡΟΦΟΣ) – %s" % M.REV, "πρόταση προς έγκριση · τι άλλαξε με τις οδηγίες της 19/11 (R02 – R05) · τι χρειάζεται απόφαση")
    a, b, c_ = DC.cols(3, y, name="ΗΛ-00")
    n = CK.counts(); F = CK.feeder_calc()
    B = dict(size=7.7)
    a.h("ΤΙ ΑΛΛΑΞΕ ΜΕ ΤΙΣ ΟΔΗΓΙΕΣ ΤΗΣ 19/11")
    a.p("Κανονικός, συμμετρικός κάναβος σε κάθε χώρο: καθιστικό 4 × 3, υπνοδωμάτια 2 × 2. Καμία ράγα, κανένα κρεμαστό, καμία απλίκα. Στα λουτρά καθρέπτες με φως. "
        "Στους εξώστες τα φωτιστικά οροφής των προοπτικών (ΗΛ-04, ΗΛ-05).", bold="1 · Φωτισμός μόνο με spots.", **B)
    a.p("Τα 4 spots συμμετρικά στους άξονες του δωματίου – όχι ένα πάνω από το γραφείο.", bold="2 · Υπνοδωμάτιο 2.", **B)
    a.p("Ο βόρειος τοίχος του σαλονιού μένει όπως είναι στις τοιχοποιίες, περασιά με το δοκάρι. Το κανάλι του R01 καταργήθηκε· καμία αλλαγή τοιχοποιίας.", bold="3 · Τοίχος χωρίς +5,5 cm.", **B)
    a.p("Στο δυτικό άκρο του χωλ, στον τοίχο του λουτρού γονέων (12,5 cm διαθέσιμα μέσα στον τοίχο). Λεπτομέρεια: ΗΛ-07.", bold="4 · Πίνακας.", **B)
    a.p("Κανένα ρολό: έφυγαν 2 κυκλώματα, 4 μοτέρ και 4 πλήκτρα.", bold="5 · Χωρίς ηλεκτρικά ρολά.", **B)
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
    b.h("R09 – 5 ΟΠΕΣ Ø75 · ΑΠΟΧΕΤΕΥΣΗ ΚΛΙΜΑΤΙΣΤΙΚΟΥ Ø32 ΑΠΟ ΟΠΗ", fill=CHANC)
    b.p("όλα περνούν από τα ταβάνια και κατεβαίνουν μέσα στους τοίχους (ΗΛ-06, ΗΛ-07, ΗΛ-12).", bold="Κανένα καλώδιο στο πάτωμα, κανένα πρέκι / κούτελο:", **B)
    b.p("ο τοίχος της πόρτας εισόδου ξαναγίνεται 15 cm, περασιά με το δοκάρι· το κανάλι του καταργείται. Ό,τι περνούσε από εκεί περνά από οπές.", bold="Τοίχος εισόδου:", **B)
    b.p("3 στο δοκάρι του σαλονιού (ΟΠ5 παροχή + ασθενή · ΟΠ1 ισχυρά · ΟΠ2 κλιματιστικό: ψυκτικά + αποχέτευση Ø32) και 2 στο δοκάρι εισόδου – κουζίνας (ΟΠ3 από το shaft · ΟΠ4 κουζίνα). Χιτώνιο Ø75 στη μέση του ύψους. Γέμισμα 29–56 %.", bold="Οπές:", **B)
    b.p("η αντλία του μηχανήματος το ανεβάζει κολλητά στην πλάκα → ΟΠ2 → ταβάνι Υπν.2 με 1 % → μέσα στον τοίχο του λουτρού μαζί με του split → πατοσίφωνο. Τίποτα στο πάτωμα.", bold="Αποχέτευση κλιματιστικού σαλονιού Ø32:", **B)
    b.p("shaft → ψευδοδοκός κλιμακοστασίου → ΟΠ3 → λωρίδα εισόδου → ταβάνι σαλονιού → ΟΠ5 → ταβάνι χωλ → πίνακας και κέντρο ασθενών, από πάνω.", bold="Κεντρική παροχή και ασθενή:", **B)
    b.p("οι πρίζες παίρνουν ρεύμα από πίσω – από το ταβάνι του λουτρού γονέων, από τη ντουλάπα του χωλ, από τον τοίχο του Υπν.2. Ο τοίχος της TV από την κουρτινόθηκη (Ε1).", bold="Τοίχοι του σαλονιού:", **B)
    b.p("έφυγαν η πρίζα του ΝΑ πεσσού και η πρίζα δίπλα στη μπαλκονόπορτα του Υπν.2· η πρίζα του νότιου εξώστη πήγε πίσω από τον τοίχο της TV· τα φώτα των εξωστών ανάβουν από το άνοιγμα της κουζίνας.",
        bold="Τι μετακινήθηκε για να μη χρειάζεται πάτωμα:", **B)
    b.p("μετρητής → πίνακας μέσα στην αποθήκη → φορτιστής, αποθήκη και παροχή του σπιτιού (5×16). Διαδρομές και μήκη: ΗΛ-11.", bold="Φόρτιση αυτοκινήτου (λύση Β):", **B)
    b.p("τι περνά από κάθε οπή και από κάθε πέρασμα: ΗΛ-12. Κατακόρυφο διάγραμμα οικοδομής: ΗΛ-13.", bold="Σωληνώσεις:", **B)
    b.p("ο πίνακας πυρανίχνευσης πήρε δικό του ρελέ· καλώδια χαμηλού καπνού στο κλιμακοστάσιο· στις ψευδοροφές τα καλώδια απλωμένα σε μία στρώση, όχι σε δέμα.", bold="ΕΛΟΤ 60364:", **B)
    b.h("ΤΙ ΑΛΛΑΖΕΙ ΣΤΑ ΑΛΛΑ ΤΕΥΧΗ (ΑΝ ΕΓΚΡΙΘΕΙ)")
    b.table([70, 280], [["Τοιχοποιίες → Β1 R31 · Δ΄ R10", "τοίχος πόρτας εισόδου 15 cm (Τ6Α) αντί 22,5 (Τ6Β)"],
                        ["Ανόψεις Β1 → R24", "οροφή χωλ +2,68 και Υπν.2 +2,65 (για τις οπές και την κλίση της αποχέτευσης του κλιματιστικού) · λωρίδα ΚΜ1 από το 9,40 · ψυκτικά ΚΜ1 από την ΟΠ2 · ο φωτισμός με spots: κάναβος καθιστικού 4 × 3, Υπν.2, χωρίς παροχές κρεμαστών, ανιχνευτής ΑΚ1"],
                        ["Αποχετεύσεις → R29", "συμπυκνώματα ΚΜ1 Ø32: αντλία μηχανήματος → ΟΠ2 → ταβάνι Υπν.2 με 1 % → τοίχος λουτρού (Τ2-02) μαζί με το split → πατοσίφωνο λουτρού · split Υπν.1 30 cm νοτιότερα"],
                        ["Ξυλότυποι Σ4 · Σ5 · Σ6", "5 χιτώνια Ø75 στα δοκάρια Δ3.1 (3) και Δ9.1 (2) – θέσεις στο ΗΛ-12"]], size=7.2, lead=8.6, pad=2.6, bold_first=True)
    b.h("ΠΕΡΙΕΧΟΜΕΝΑ")
    b.table([40, 310], [[s_[0], s_[1]] for s_ in SHEETS], size=7.4, lead=8.8, pad=2.4, bold_first=True)
    c_.h("ΑΝΟΙΚΤΑ – ΧΡΕΙΑΖΟΜΑΙ ΑΠΑΝΤΗΣΗ", fill=DC.WARNC)
    c_.table([24, 64, 262], [[o[0], o[1], o[2]] for o in M.OPEN], size=7.0, lead=8.3, pad=2.6, bold_first=True)
    c_.h("ΔΕΝ ΕΧΕΙ ΓΙΝΕΙ ΑΚΟΜΗ")
    c_.p("Ισόγειο, Δ΄ όροφος, σοφίτα και κοινόχρηστα – με την ίδια λογική, αφού εγκριθεί ο τυπικός όροφος.", bullet="•", **B)
    c_.p("Τεχνικές προδιαγραφές υλικών, λίστα υλικών με ποσότητες και οδηγίες για τον ηλεκτρολόγο: βγαίνουν από το ίδιο μοντέλο μόλις κλειδώσουν οι θέσεις (τα είχε το R00 – "
         "δεν ξανατυπώθηκαν για να μείνει το τεύχος απλό).", bullet="•", **B)
    c_.p("Φωτοτεχνικός υπολογισμός με λογισμικό – εδώ η μέση στάθμη υπολογίστηκε με τη μέθοδο της φωτεινής ροής.", bullet="•", **B)
    DC.finish(no, "ΣΥΝΟΨΗ – ΤΙ ΑΛΛΑΞΕ, ΤΙ ΧΡΕΙΑΖΕΤΑΙ ΑΠΟΦΑΣΗ", "Οδηγίες 19/11 · τίποτα στο πάτωμα · πίνακας αποθήκης · %d ανοικτά" % len(M.OPEN))


# ================================================================ ΗΛ-05 ΦΩΤΙΣΜΟΣ – ΤΕΚΜΗΡΙΩΣΗ ΚΑΙ ΦΩΤΙΣΤΙΚΑ
def fixtures():
    """Πίνακας φωτιστικών από το μοντέλο: (κωδικός, είδος, τεμάχια, χαρακτηριστικά)."""
    n = lambda f: sum(1 for q in M.SPOTS if f(q))
    led = {}
    for (nm, a, b, g, t) in M.LED:
        led[nm] = led.get(nm, 0) + math.hypot(b[0] - a[0], b[1] - a[1])
    wl = lambda k: sum(1 for l in M.WALL_LIGHTS if l[4] == k)
    return [
        ("Φ1", "Χωνευτό spot", "%d τεμ." % n(lambda q: q[1] == "s" and q[4] != "ε"), "9 W · 850 lm · δέσμη 36–40° · 2700 K · CRI ≥ 90 · βαθιά χωνευτό (UGR < 19) · οπή Ø 75 · ύψος ≤ 75 mm · dimmable"),
        ("Φ3", "Χωνευτό spot κουζίνας", "%d τεμ." % n(lambda q: q[4] == "ε"), "10 W · 850 lm · 60° · 3000 K · CRI ≥ 90 · στον άξονα του διαδρόμου"),
        ("Φ4", "Χωνευτό spot IP44", "%d τεμ." % n(lambda q: q[1] == "s44"), "8 W · 750 lm · 60° · 3000 K · CRI ≥ 90 · λουτρά εκτός ντους"),
        ("Φ5", "Χωνευτό spot IP65", "%d τεμ." % n(lambda q: q[1] == "s65"), "8 W · 750 lm · 60° · 3000 K · πάνω από το ντους"),
        ("Φ8", "LED πάγκου κουζίνας", "%s m" % fz(led.get("LED4", 0), 1), "ταινία 24 V ≈ 10 W/m · 900 lm/m · 3000 K · CRI ≥ 90 σε προφίλ με οπάλ κάλυμμα, κάτω από τα επάνω ντουλάπια · dimmable"),
        ("Φ9", "LED κεφαλαριού Υπν.1", "%s m" % fz(led.get("LED3", 0), 1), "ταινία 24 V ≈ 5 W/m · 2700 K · έμμεσο, ως νυχτερινό φως"),
        ("Φ10", "Κυλινδρικό φωτιστικό οροφής εξώστη", "%d τεμ." % len(M.EXT_SPOTS), "επίτοιχο στο ταβάνι του εξώστη, λευκό, Ø 8–10 cm · IP65 · 7–9 W · 3000 K · σε ζεύγη ανά 0,45 m – όπως τα προοπτικά του αρχιτέκτονα"),
        ("Φ11", "Καθρέπτης με φως", "%d τεμ." % wl("mir"), "φως από μπροστά / περιμετρικά ≈ 1500 lm · 3000–4000 K · CRI ≥ 90 · IP44 · παροχή στο +1,90"),
        ("Φ12", "Στεγανό φωτιστικό τοίχου εξώστη", "%d τεμ." % wl("ext"), "IP65 · 8–10 W · 3000 K · φως προς τα κάτω (όχι προς τον γείτονα) · +2,10"),
        ("Φ13", "Φωτιστικό ασφαλείας", "%d τεμ." % len(M.EMERGENCY), "αυτόνομο 1 h, πάνω από την πόρτα εισόδου"),
    ]


def sheet_05(no="ΗΛ-05"):
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
    D.halo_text(v, mx + 0.55, my + 0.12, "στο ΙΣΟΓΕΙΟ, έξω από τον", size=4.8, color=FEED, anchor="l")
    D.halo_text(v, mx + 0.55, my + 0.40, "τοίχο της εισόδου (κατά Η02)", size=4.8, color=FEED, anchor="l")
    D.route(v, [(mx - 0.40, my), (11.60, my), (11.60, 6.20), (sx + 0.25, 6.20), (sx + 0.25, sy)], col=FEED, lw=1.6, dash=[3.5, 2], arrows=True)
    D.halo_text(v, 13.55, 7.55, "μέσα στην οροφή του χωλ ισογείου → shaft", size=4.8, color=FEED, anchor="l")
    v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.9)
    D.halo_text(v, 11.05, 2.45, "shaft Η/Μ", size=5.4, color=DAT, font="Inter-Bold", anchor="l")
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
    D.halo_text(v, 6.0, 2.25, "σχάρα καλωδίων στην οροφή του υπογείου (εμφανής)", size=4.8, color=INK, font="Inter-SemiBold")
    P.end_plan()
    P.view_title("ΥΠΟΓΕΙΟ – ΜΕΤΡΗΤΗΣ → ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ → ΦΟΡΤΙΣΤΗΣ ΚΑΙ ΠΑΡΟΧΗ ΣΠΙΤΙΟΥ", "Κλίμακα 1:80"); P.scale_bar(80)
    FL = CK.feeder_lengths()
    y = P._head(P.TOP - 22, "ΠΩΣ ΠΑΕΙ ΤΟ ΡΕΥΜΑ (ΛΥΣΗ Β)")
    steps = ["1 · Μετρητής (ισόγειο, έξω από τον τοίχο της εισόδου) → μέσα στην οροφή του χωλ εισόδου → shaft Η/Μ.",
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
    for s_ in notes:
        yy = D.para(P.PX - 2, yy, s_, P.PW + 4, size=5.4, color=MUTE, bullet="•") - 2
    assert yy > 150, "ΗΛ-11: η δεξιά στήλη ξεχειλίζει (%.0f)" % yy
    P.finish(no, "ΥΠΟΓΕΙΟ – ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ · ΦΟΡΤΙΣΗ", "Μετρητής → αποθήκη → φορτιστής · παροχή σπιτιού", M.BASE_TXT, "Κλίμακα 1:80 · A3")


# ================================================================ ΗΛ-12 ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΟΛΑ ΤΑ ΠΕΡΑΣΜΑΤΑ + ΟΠΕΣ ΔΟΚΩΝ (ΑΝ ΕΓΚΡΙΘΟΥΝ)
def _tube_txt(lst, hole=None):
    """«1 καλώδιο · 3 × Ø25 · …» – hole=True μόνο όσα πάνε από την οπή, False όσα μένουν, None όλα."""
    q = {}
    for nm, d, od, via in lst:
        if hole is not None and via != hole:
            continue
        q[d] = q.get(d, 0) + 1
    return " · ".join(("%d × Ø%d" % (q[d], d)) if d else ("%d καλώδιο 5×16" % q[d]) for d in sorted(q, key=lambda k: (k != 0, -k))) or "—"


def sheet_12(no="ΗΛ-12"):
    H = CK.holes()
    PL._plan(_routes, "ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΤΙ ΠΕΡΝΑ ΑΠΟ ΚΑΘΕ ΟΠΗ ΚΑΙ ΚΑΘΕ ΠΕΡΑΣΜΑ")
    y = P._head(P.TOP - 22, "ΧΙΤΩΝΙΑ Ø75 ΣΤΑ ΔΟΚΑΡΙΑ – ΘΕΣΗ ΓΙΑ ΤΟ ΚΑΛΟΥΠΙ")
    rows = []
    for h in H:
        bn, sec, x0, y0, x1, y1 = [b_ for b_ in M.A.BEAMS if b_[0] == h["beam"]][0]
        if h["horiz"]:
            pos = "%s m από τη δυτική κολόνα (Κ10) · %s m από την Κ3" % (fz(h["x"] - x0, 2), fz(x1 - h["x"], 2))
        else:
            pos = "%s m από την Κ3 (βόρεια) · %s m από την Κ8" % (fz(h["y"] - y0, 2), fz(y1 - h["y"], 2))
        rows.append([h["id"], h["beam"], pos])
    y = D.table(P.PX - 4, y + 2, [18, 22, P.PW - 40 + 8], rows, head=["", "ΔΟΚΟΣ", "ΚΕΝΤΡΟ ΟΠΗΣ ΚΑΤΑ ΜΗΚΟΣ ΤΟΥ ΔΟΚΑΡΙΟΥ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    txt(P.PX - 2, y - 7, "Ύψος: κέντρο 25 cm κάτω από την άνω στάθμη της πλάκας = μέση του ύψους (δοκάρια 30/50).", size=5.0, color=MUTE)
    txt(P.PX - 2, y - 13.5, "Κάθετα στο δοκάρι, σε όλο το πλάτος του. Χιτώνιο PVC Ø75 (καθαρό 70 mm).", size=5.0, color=MUTE)
    y = P._head(y - 30, "ΤΙ ΠΕΡΝΑ ΑΠΟ ΚΑΘΕ ΟΠΗ")
    rows, colors = [], {}
    for i, h in enumerate(H):
        rows.append([h["id"], h["use"] + "\n%s → %s" % (h["frm"], h["to"]), ", ".join(("%d × %s" % (n_, nm)) if n_ > 1 else nm for nm, d_, n_, k_ in h["lines"]) + ".",
                     "%d\n%d %%" % (h["ncab"], round(h["fill"] * 100))])
        colors[i] = tint(DAT, 0.86) if h["kind"] == "weak" else (tint(FEED, 0.86) if h["kind"] == "feed" else (tint(HVC, 0.86) if h["kind"] == "hvac" else tint(PWR, 0.88)))
    y = D.table(P.PX - 4, y + 2, [18, 62, P.PW - 102 + 8, 22], rows, head=["", "ΤΙ / ΑΠΟ → ΠΡΟΣ", "ΤΙ ΠΕΡΝΑ ΑΚΡΙΒΩΣ (τεμάχια × είδος)", "τεμ.\nγεμ."], size=4.9, lead=5.9, pad=1.8, bold_first=True, colors=colors, zebra=False)
    y = P._head(y - 16, "ΤΑ ΑΛΛΑ ΠΕΡΑΣΜΑΤΑ (μέσα από τοίχους / ντουλάπες)")
    rows = []
    for p_ in M.PASSES:
        if p_["id"] in M.TUBES:
            t = M.TUBES[p_["id"]]
            rows.append([p_["id"], "%d" % len(t), _tube_txt(t) + "\n" + ", ".join(q[0] for q in t) + "."])
    y = D.table(P.PX - 4, y + 2, [18, 16, P.PW - 34 + 8], rows, head=["", "τεμ.", "ΣΩΛΗΝΕΣ (σπιράλ βαρέως τύπου) – ΤΙ ΕΧΕΙ Ο ΚΑΘΕΝΑΣ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    rows = [[a_, b_ + "."] for a_, b_ in M.HOLES_NO]
    y = D.table(P.PX - 4, y - 4, [62, P.PW - 62 + 8], rows, head=["ΧΩΡΙΣ ΟΠΗ", "ΤΙ ΓΙΝΕΤΑΙ ΕΚΕΙ"], size=4.9, lead=5.9, pad=1.8, bold_first=True)
    notes = ["Γέμισμα = διατομή καλωδίων / καθαρή διατομή χιτωνίου (Ø70). Όριο 60 % (χιτώνιο 30 cm). Ασθενή δίπλα σε ισχυρά μόνο μέσα σε δικό τους σπιράλ.",
             "ΟΠ2: ο Ø32 της αποχέτευσης ΨΗΛΑ στο χιτώνιο, τα ψυκτικά από κάτω, με μόνωση 9 mm μέσα στο χιτώνιο (με 13 mm δεν χωρούν δίπλα-δίπλα) – να το δει ο ψυκτικός.",
             "Όροφοι που δεν έχουν χυθεί: χιτώνιο στο καλούπι. Αν κάποιος έχει ήδη χυθεί: καρότο με ανίχνευση σιδήρων, μόνο με τον στατικό."]
    y -= 10
    for s_ in notes:
        y = D.para(P.PX - 2, y, s_, P.PW + 4, size=5.2, color=MUTE, bullet="•") - 2
    assert y > 150, "ΗΛ-12: η δεξιά στήλη ξεχειλίζει (%.0f)" % y
    PL._finish(no, "ΣΩΛΗΝΩΣΕΙΣ ΟΡΟΦΟΥ – ΟΠΕΣ ΚΑΙ ΠΕΡΑΣΜΑΤΑ", "Χιτώνια Ø75 ΟΠ1–ΟΠ5: θέση και τι περνά · λοιπά περάσματα")


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
        if nm in ("Γ΄", "Β΄", "Α΄"):
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
        txt(xr0 + 6, yt - 26, "ψευδοδοκός κλιμακοστασίου: shaft → πόρτα διαμερίσματος", size=5.2, color=MUTE)
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
                        ["Κοινόχρηστα: φώτα κλιμακοστασίου, ανελκυστήρας", "κατά τον κοινόχρηστο πίνακα"]], size=6.0, lead=7.4, pad=2.2, aligns={1: "r"})
    f.p("Ισχυρά και ασθενή σε ΧΩΡΙΣΤΕΣ σχάρες μέσα στο shaft, στις δύο άκρες του.", **B)
    f.p("Σφράγιση του shaft σε κάθε πλάκα με πυράντοχο υλικό. Καλώδια χαμηλού καπνού, χωρίς αλογόνα.", **B)
    f.p("Το άνοιγμα 90 × 15 του shaft υπάρχει ήδη στους ξυλοτύπους Σ2 … Σ7 – δεν χρειάζεται τίποτα άλλο στο μπετό.", **B)
    f.h("ΣΕΙΡΑ ΕΡΓΑΣΙΩΝ ΤΟΥ ΗΛΕΚΤΡΟΛΟΓΟΥ")
    for j, s_ in enumerate(["Σχάρες μέσα στο shaft, από το υπόγειο ως το δώμα.", "Σχάρα στην οροφή του υπογείου: shaft → αποθήκες. Πίνακες αποθηκών.",
                            "Σε κάθε όροφο, ΠΡΙΝ κλείσουν οι γυψοσανίδες: σπιράλ στον ψευδοδοκό του κλιμακοστασίου και πάνω από την πόρτα εισόδου (Π0).",
                            "Μέσα στο σπίτι: σχάρα στο ταβάνι του χωλ, καλώδια μέσα από τις οπές των δοκαριών (ΟΠ1–ΟΠ5), κορμοί στα ταβάνια (ΗΛ-06, ΗΛ-12).",
                            "Κατεβάσματα μέσα στους τοίχους γυψοσανίδας πριν από το δεύτερο φύλλο. Τοίχοι σαλονιού από πίσω (Τ1–Τ4).",
                            "Τράβηγμα καλωδίων μετά το κλείσιμο των οροφών, από τις θυρίδες και τις τρύπες των spots."]):
        f.p(s_, bullet="%d." % (j + 1), size=6.6)
    f.h("ΤΙ ΔΕΝ ΕΧΕΙ ΜΕΛΕΤΗΘΕΙ", fill=DC.WARNC)
    f.p("Ισόγειο, Δ΄ όροφος, σοφίτα, κοινόχρηστα: εδώ φαίνονται μόνο σχηματικά. Οι αριθμοί καλωδίων του shaft είναι εκτίμηση για 5 διαμερίσματα.", **B)
    DC.finish(no, "ΚΑΤΑΚΟΡΥΦΟ ΔΙΑΓΡΑΜΜΑ ΟΙΚΟΔΟΜΗΣ", "Shaft · παροχές μέσω αποθήκης · ασθενή · σειρά εργασιών")
