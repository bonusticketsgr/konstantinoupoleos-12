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
        D.halo_text(v, 11.62, 2.62, "shaft → EV φόρτιση οχήματος (υπόγειο) · ΗΛ boiler (δώμα) · ΑΠ αποθήκη", size=4.6, color=INK, font="Inter-Bold")
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
    for k in ("Κ1", "Κ2", "Κ3", "Κ4", "Κ5", "Π1", "Π2", "ΑΘ", "ΚΛ", "ΑΚ", "ΕΝ", "ΕΞ", "ΚΑ", "ΣΠ", "ΗΛ", "ΑΠ", "EV"):
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
    PL._finish(no, "ΔΙΑΚΟΠΤΕΣ – ΥΨΗ ΚΑΙ ΑΠΟΣΤΑΣΕΙΣ", "Δ1–Δ15 · αλέ-ρετούρ · dimmers · ομάδες φωτιστικών")


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
        chain([1.905] + list(M.LIV_X) + [8.225], 8.66, True)
        chain([5.15] + list(M.LIV_Y) + [8.915], 2.20, False)
        chain([6.50] + list(M.B2_X) + [9.365], 3.25, True)
        chain([1.35] + list(M.B2_Y) + [4.85], 9.10, False)
        PL.lights(v, labels=True, groups=True)
        PL.panel(v, lab=False)
    PL._plan(fn, "ΦΩΤΙΣΜΟΣ ΜΟΝΟ ΜΕ SPOTS – ΣΥΜΜΕΤΡΙΚΟΣ ΚΑΝΑΒΟΣ, ΟΜΑΔΕΣ")
    y = P.legend(["e_spot", "e_spot44", "e_spot65", "e_led", "e_ext", "e_grp", "e_det"])
    rows = []
    for q in M.SPOTS:
        a, b = _ceil_dist(q[2], q[3])
        rows.append([q[0], SPOT_KIND[q[1]], a, b, q[5]])
    y = D.table(P.PX - 4, y - 2, [24, 40, 28, 28, P.PW - 120 + 8], rows, head=["", "ΕΙΔΟΣ", "ΑΠΟ", "ΑΠΟ", "ΤΙ ΦΩΤΙΖΕΙ"], size=4.9, lead=5.9, pad=1.35, bold_first=True)
    txt(P.PX - 2, y - 8, "ΑΠΟ: m από τον κοντινότερο τοίχο / ντουλάπα (Β βόρεια · Ν νότια · Δ δυτικά · Α ανατολικά).", size=5.2, color=MUTE)
    PL._finish(no, "ΦΩΤΙΣΜΟΣ – ΚΑΤΟΨΗ", "Μόνο χωνευτά spots · κάναβος · ομάδες · θέσεις από τοίχους")


# ================================================================ ΗΛ-06 ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ
def sheet_06(no="ΗΛ-06"):
    def fn(v):
        PL.beams(v, names=True)
        v.rect(9.925, 2.85, 10.825, 3.00, fill=(0.75, 0.90, 0.86), stroke=DAT, lw=0.7)
        D.halo_text(v, 10.375, 2.64, "shaft Η/Μ", size=4.8, color=DAT)
        PL.sockets(v, faint=True); PL.switches(v, faint=True)
        for r in M.WALL_RUNS:
            D.route(v, r["pts"], col=PL.WALLC, lw=1.5, dash=[2.6, 1.6])
        for r in M.FLOOR_RUNS:
            D.route(v, r["pts"], col=PL.FLOORC, lw=2.0, dash=[0.9, 1.7], lab="%s  %s" % (r["id"], r["n"]), lsize=4.6)
        for r in M.ROUTES:
            col = HVC if r["kind"] == "hvac" else PWR
            D.route(v, r["pts"], col=col, lw=2.2 if r["n"].startswith("κορμός") else 1.5, arrows=True, lab=r["n"] or None)
        D.route(v, M.OUT_ROUTE, col=FEED, lw=1.3, dash=[3, 1.5], arrows=True, lab="προς shaft", seg=2, lsize=4.4)
        D.route(v, M.FEED_ROUTE, col=FEED, lw=2.6, arrows=True, lab="ΠΑΡΟΧΗ 5×10", seg=0)
        for p in M.PASSES:
            D.pass_zone(v, p["rect"], lab=p["id"], lab_at=p["lab"])
        PL.panel(v)
        D.halo_text(v, 5.70, 5.52, "ΔΚ: δέσμη πάνω στην πλάκα, πριν από το γέμισμα", size=4.6, color=PL.FLOORC, font="Inter-Bold")
        D.halo_text(v, 9.02, 6.98, "ΑΝΟΔΟΣ", size=4.4, color=CHANC, font="Inter-Bold", anchor="r")
        D.halo_text(v, 9.02, 7.10, "στο κανάλι", size=4.2, color=CHANC, anchor="r")
    PL._plan(fn, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΟΛΑ ΜΕΤΑ ΤΟ ΜΠΕΤΟ · Ο ΤΟΙΧΟΣ ΤΟΥ ΣΑΛΟΝΙΟΥ ΠΕΡΑΣΙΑ ΜΕ ΤΟ ΔΟΚΑΡΙ")
    y = P.legend(["e_feed", "e_out", "e_trunk", "e_hvacr", "e_pass", "e_wallrun", "e_floor", "beam", "e_tn"])
    rows = [[p["id"], p["beam"], p["title"] + ": " + p["how"] + "."] for p in M.PASSES]
    colors = {i: (1.0, 0.93, 0.80) for i, p in enumerate(M.PASSES) if p["new"]}
    y = D.table(P.PX - 4, y - 2, [18, 30, P.PW - 48 + 8], rows, head=["", "ΔΟΚΟΣ", "ΠΕΡΑΣΜΑ – ΠΩΣ ΠΕΡΝΟΥΝ ΤΑ ΚΑΛΩΔΙΑ ΚΑΤΩ ΑΠΟ ΤΗ ΔΟΚΟ"], size=5.2, lead=6.3, pad=2.0, bold_first=True, colors=colors, zebra=False)
    rows = [[r["id"], r["n"] + "\n%s m" % fz(G.path_len(r["pts"]), 1), ("ΝΕΟ. " if r["new"] else "") + r["short"] + "."] for r in M.FLOOR_RUNS]
    y = D.table(P.PX - 4, y - 5, [18, 34, P.PW - 52 + 8], rows, head=["", "ΣΩΛΗΝΕΣ", "ΠΑΝΩ ΣΤΗΝ ΠΛΑΚΑ, ΠΡΙΝ ΑΠΟ ΤΟ ΓΕΜΙΣΜΑ (δεν σκάβεται τίποτα)"], size=5.2, lead=6.3, pad=2.0, bold_first=True)
    txt(P.PX - 2, y - 9, "Καμία αλλαγή τοιχοποιίας. Η δέσμη ΔΚ θέλει το ΟΚ σου (Ε1). Τομές: ΗΛ-07.", size=5.4, color=MUTE)
    PL._finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΚΑΤΟΨΗ", "Παροχή από το shaft · δέσμη δαπέδου ΔΚ · κορμοί · περάσματα")


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


def sec_dk(x, ytop):
    """Τομή Β–Ν στον βόρειο τοίχο του καθιστικού (x ≈ 4,5, βλέπουμε προς ανατολή): ντουλάπα χωλ | τοίχος περασιά με τη Δ3.1 | καθιστικό – το δάπεδο."""
    _cap(x, ytop, "ΔΚ · ΠΙΝΑΚΑΣ → ΚΑΘΙΣΤΙΚΟ (πάνω στην πλάκα)", "τομή Β–Ν στον βόρειο τοίχο του καθιστικού · το δάπεδο · 1:12,5")
    a, b = 4.55, 5.72; zb = -0.36; sc = Sec(x, ytop - 322, S12, a, zb)
    FILLC = (0.93, 0.90, 0.84)
    sc.rect(a, -0.32, b, -0.12, fill=CONC)                                   # πλάκα
    sc.rect(a, -0.12, 5.06, 0.0, fill=FILLC, lw=0.3); sc.rect(5.15, -0.12, b, 0.0, fill=FILLC, lw=0.3)
    sc.rect(5.15, -0.09, b, -0.06, fill=(0.80, 0.88, 0.96), lw=0.3)            # μόνωση ενδοδαπέδιας
    sc.rect(5.15, -0.015, b, 0.0, fill=(0.72, 0.60, 0.46), lw=0.3)             # τελικό δάπεδο
    for i_ in range(6):
        hx = 5.27 + i_ * 0.07
        sc.rect(hx, -0.058, hx + 0.016, -0.042, fill=(0.86, 0.30, 0.20), stroke=None, lw=0)      # σωλήνες ενδοδαπέδιας
    sc.rect(5.06, -0.12, 5.0725, 0.58, fill=GYP, lw=0.4)                     # 1 γυψ. προς τη ντουλάπα
    sc.rect(5.0725, -0.12, 5.125, 0.58, fill=(1, 1, 1), stroke=MUTE, lw=0.4, dash=[1.5, 1.2])   # CW 50
    sc.rect(5.125, -0.12, 5.15, 0.58, fill=GYP, lw=0.4)                      # 2 γυψ. προς το καθιστικό
    for i_ in range(8):
        hx = 5.19 + i_ * 0.031
        sc.rect(hx, -0.119, hx + 0.025, -0.094, fill=tint(CABLE, 0.35), stroke=CABLE, lw=0.5)     # η δέσμη, κομμένη κάθετα
    sc.rect(5.125, 0.27, 5.15, 0.33, fill=PWR, lw=0.4)                        # κουτί ρευματοδότη +0,30
    _path(sc, [(5.19, -0.107), (5.10, -0.107), (5.10, 0.30), (5.125, 0.30)], lw=1.6)
    sc.text(a + 0.02, 0.40, "ΝΤΟΥΛΑΠΑ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 0.34, "ΧΩΛ", size=5.8, font="Inter-Bold")
    sc.text(5.30, 0.40, "ΚΑΘΙΣΤΙΚΟ", size=5.8, font="Inter-Bold")
    sc.text(5.20, 0.29, "ρευματοδότης +0,30:", size=5.2, color=PWR); sc.text(5.20, 0.235, "ο σωλήνας ανεβαίνει", size=5.2, color=PWR); sc.text(5.20, 0.18, "μέσα στον τοίχο", size=5.2, color=PWR)
    sc.text(5.30, 0.03, "±0,00 τελικό δάπεδο", size=5.2, color=MUTE, dy=2)
    sc.text(b - 0.01, 0.09, "από πάνω: μόνωση + ενδοδαπέδια", size=5.0, color=MUTE, anchor="r")
    sc.text(5.45, -0.20, "ΔΕΣΜΗ ΔΚ πάνω στην πλάκα", size=5.6, font="Inter-Bold", color=CABLE)
    sc.text(5.45, -0.255, "σε στρώση εξομάλυνσης 3 cm", size=5.2, color=CABLE)
    sc.line(5.30, -0.118, 5.44, -0.19, col=CABLE, lw=0.5)
    sc.text(a + 0.02, -0.235, "πλάκα h20 (−0,12 … −0,32)", size=5.2, color=(1, 1, 1))
    sc.dimv(b + 0.02, -0.12, 0.0, "12", off=4)
    sc.text(a + 0.02, 0.66, "↑ ο τοίχος συνεχίζει ως τη δοκό Δ3.1 (+2,48), ΠΕΡΑΣΙΑ με την παρειά της –", size=5.2, color=MUTE)
    sc.text(a + 0.02, 0.61, "   δίπλα στη δοκό δεν υπάρχει χώρος: από εδώ τίποτα δεν ανεβαίνει στο ταβάνι", size=5.2, color=MUTE)


def sec_p2(x, ytop):
    """Τομή Δ–Α στο Π2 (y ≈ 7,68, βλέπουμε προς βορρά): λωρίδα εισόδου | κανάλι Τ6Β | Δ9.1 | τοίχος Τ6Α-02 → κουζίνα."""
    _cap(x, ytop, "Π2 · ΛΩΡΙΔΑ ΕΙΣΟΔΟΥ ↔ ΚΟΥΖΙΝΑ (δοκός Δ9.1)", "τομή Δ–Α στη γωνία των τοίχων Τ6Β-02 / Τ6Α-02 · 1:12,5")
    a, b = 9.02, 10.22; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.78, 9.40, 2.98, fill=CONC); sc.rect(9.70, 2.58, b, 2.98, fill=tint(CONC, 0.35)); _beam(sc, 9.40, 9.70, 2.48, "Δ9.1", "30/50")
    sc.text(9.96, 2.80, "Δ12.2 (πάνω από τον τοίχο)", size=5.0, color=MUTE, anchor="c")
    sc.rect(a, 2.48, 9.325, 2.4925, fill=GYP, lw=0.4)                        # οροφή λωρίδας
    sc.rect(9.55, Z0, b, 2.48, fill=tint(GYP, 0.55), stroke=None); sc.rect(9.70, 2.48, b, 2.58, fill=tint(GYP, 0.55), stroke=None)      # Τ6Α-02 σε μήκος
    sc.rect(9.325, Z0, 9.35, 2.48, fill=GYP, lw=0.4)
    sc.rect(9.35, Z0, 9.40, 2.78, fill=tint(CHANC, 0.70), stroke=CHANC, lw=0.6)
    sc.rect(9.425, Z0, 9.525, 2.48, fill=(1, 1, 1), stroke=MUTE, lw=0.4, dash=[1.5, 1.2])
    sc.rect(9.525, Z0, 9.55, 2.48, fill=GYP, lw=0.4)
    sc.line(9.70, 2.4925, b, 2.4925, col=MUTE, lw=0.5, dash=[2, 1.5])
    _path(sc, [(a + 0.02, 2.70), (9.28, 2.70), (9.375, 2.62), (9.375, 2.30), (9.92, 2.30), (9.92, 2.515)])
    x_, y_ = sc.p(9.92, 2.537); C().setFillColorRGB(1, 1, 1); C().setStrokeColorRGB(*CABLE); C().setLineWidth(1.0); C().circle(x_, y_, 4.2, stroke=1, fill=1)
    C().setFillColorRGB(*CABLE); C().circle(x_, y_, 1.5, stroke=0, fill=1)
    sc.text(9.95, 2.527, "→ κενό κουζίνας", size=5.2, font="Inter-Bold", color=CABLE, dx=5)
    sc.text(b - 0.01, 2.435, "οροφή κουζίνας +2,48 (μπροστά)", size=5.0, color=MUTE, anchor="r")
    sc.text(a + 0.01, 2.985, "+2,98", size=5.2, color=MUTE, dy=3)
    sc.text(a + 0.02, 2.435, "+2,48 οροφή λωρίδας", size=5.2, color=MUTE)
    sc.text(a + 0.02, 2.27, "ΛΩΡΙΔΑ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.205, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold")
    sc.text(9.74, 2.06, "ΤΟΙΧΟΣ Τ6Α-02", size=5.6, font="Inter-Bold"); sc.text(9.74, 2.00, "κουζίνας – σκάλας (σε μήκος)", size=5.2, color=MUTE)
    sc.text(9.74, 2.24, "+2,30", size=5.2, color=CABLE)
    sc.text(9.29, 1.96, "ΚΑΝΑΛΙ", size=5.6, font="Inter-Bold", color=CHANC, anchor="r"); sc.text(9.29, 1.90, "του Τ6Β", size=5.2, color=CHANC, anchor="r")
    sc.line(9.30, 1.955, 9.372, 1.985, col=CHANC, lw=0.5)


def sec_p0(x, ytop):
    """Τομή Δ–Α στο Π0 (άξονας πόρτας εισόδου, βλέπουμε προς βορρά): λωρίδα | τοίχος Τ6Β πάνω από την κάσα | Δ9.1 | ψευδοδοκός κλιμακοστασίου."""
    _cap(x, ytop, "Π0 · SHAFT → ΔΙΑΜΕΡΙΣΜΑ (πάνω από την πόρτα)", "τομή Δ–Α στον άξονα της πόρτας εισόδου · 1:12,5")
    a, b = 9.02, 10.22; sc = Sec(x, ytop - 322, S12, a, Z0)
    sc.rect(a, 2.78, 9.40, 2.98, fill=CONC); sc.rect(9.70, 2.83, b, 2.98, fill=CONC); _beam(sc, 9.40, 9.70, 2.48, "Δ9.1", "30/50")
    sc.rect(a, 2.48, 9.325, 2.4925, fill=GYP, lw=0.4)                        # οροφή λωρίδας
    sc.rect(9.55, 2.43, 9.95, 2.4425, fill=GYP, lw=0.4); sc.rect(9.95, 2.43, 9.9625, 2.73, fill=GYP, lw=0.4); sc.rect(9.95, 2.73, b, 2.7425, fill=GYP, lw=0.4)   # ψευδοδοκός + οροφή κλιμακοστασίου
    sc.rect(9.325, 2.25, 9.35, 2.48, fill=GYP, lw=0.4)
    sc.rect(9.35, 2.25, 9.40, 2.78, fill=tint(CHANC, 0.70), stroke=CHANC, lw=0.6)
    sc.rect(9.425, 2.25, 9.525, 2.48, fill=(1, 1, 1), stroke=MUTE, lw=0.4, dash=[1.5, 1.2])
    sc.rect(9.525, 2.25, 9.55, 2.43, fill=GYP, lw=0.4)
    sc.rect(9.325, 2.20, 9.55, 2.25, fill=(0.30, 0.30, 0.34), lw=0.4)         # κάσα
    sc.line(9.325, Z0, 9.325, 2.20, col=MUTE, lw=0.5, dash=[2, 1.5]); sc.line(9.55, Z0, 9.55, 2.20, col=MUTE, lw=0.5, dash=[2, 1.5])
    _path(sc, [(b - 0.02, 2.461), (9.56, 2.461), (9.375, 2.461), (9.375, 2.70), (9.22, 2.70), (a + 0.02, 2.70)])
    sc.text(9.4375, 2.02, "ΠΟΡΤΑ", size=5.8, font="Inter-Bold", anchor="c"); sc.text(9.4375, 1.955, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold", anchor="c")
    sc.text(a + 0.01, 2.985, "+2,98", size=5.2, color=MUTE, dy=3)
    sc.text(a + 0.02, 2.435, "+2,48 οροφή λωρίδας", size=5.2, color=MUTE)
    sc.text(a + 0.02, 2.27, "ΛΩΡΙΔΑ", size=5.8, font="Inter-Bold"); sc.text(a + 0.02, 2.205, "ΕΙΣΟΔΟΥ", size=5.8, font="Inter-Bold")
    sc.text(9.30, 2.215, "+2,25 κάσα", size=5.2, color=MUTE, anchor="r", dy=-9)
    sc.text(9.62, 2.365, "37,5 mm κάτω από τη δοκό", size=5.2, font="Inter-Bold", color=CABLE)
    sc.text(9.62, 2.27, "ΚΛΙΜΑΚΟΣΤΑΣΙΟ", size=5.8, font="Inter-Bold"); sc.text(9.62, 2.21, "ψευδοδοκός καλωδίων +2,43", size=5.2, color=MUTE); sc.text(9.62, 2.155, "από το shaft Η/Μ", size=5.2, color=MUTE)
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
    y = DC.title("ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "όλα γίνονται μετά τη σκυροδέτηση · καμία οπή σε δοκό · κανένας σωλήνας μέσα στην πλάκα")
    X0 = DC.X0
    xs = [X0, X0 + 283, X0 + 573, X0 + 863]
    sec_dk(xs[0], y); sec_p2(xs[1], y); sec_p0(xs[2], y); det_panel(xs[3], y)
    yb = y - 350
    ln(X0, yb + 6, DC.X1, yb + 6, col=FAINT, lw=0.5)
    w = 265
    f = [DC.Flow(xs[i], yb, w, size=6.2, name="ΗΛ-07/%d" % i) for i in range(4)]
    B = dict(bullet="•", size=6.2)
    f[0].h("ΔΚ – ΤΙ ΚΑΤΑΣΚΕΥΑΖΕΤΑΙ", fill=CABLE)
    f[0].p("Ο βόρειος τοίχος του καθιστικού μένει όπως είναι στις τοιχοποιίες, περασιά με το δοκάρι. Δίπλα στο δοκάρι δεν υπάρχει χώρος, άρα από τον τοίχο τίποτα δεν ανεβαίνει στο ταβάνι.", **B)
    f[0].p("Από τον πίνακα προς καθιστικό και κουζίνα τα σπιράλ στρώνονται ΠΑΝΩ στην πλάκα, πριν από το γέμισμα: ≈ %d σωλήνες, λωρίδα ≈ 65 cm σε μία στρώση. Δεν σκάβεται τίποτα." % M.DK_N, **B)
    f[0].p("Οι πρίζες και οι διακόπτες των τοίχων τροφοδοτούνται από κάτω: ο σωλήνας γυρίζει στη βάση του τοίχου και ανεβαίνει μέσα του.", **B)
    f[0].p("Ό,τι είναι στο ταβάνι (spots, ανιχνευτές, κλιματιστικό) ανεβαίνει από το κανάλι του τοίχου της πόρτας εισόδου – το μόνο σημείο του σαλονιού με χώρο δίπλα σε δοκάρι.", **B)
    f[0].p("Η ενδοδαπέδια περνά από πάνω: στρώση εξομάλυνσης 3 cm στη λωρίδα της δέσμης, μετά μόνωση και σωλήνες (Ε5).", **B)
    f[1].h("Π2 – ΤΙ ΚΑΤΑΣΚΕΥΑΖΕΤΑΙ", fill=BEAMC)
    f[1].p("Τίποτα καινούριο: χρησιμοποιείται το κανάλι 5 cm του τοίχου της πόρτας εισόδου (Τ6Β) που ήδη υπάρχει στις τοιχοποιίες R30.", **B)
    f[1].p("Τα σπιράλ της κουζίνας ανεβαίνουν από τη βάση του καναλιού, στο νότιο άκρο του τοίχου (τα τελευταία 30 cm πριν από το άνοιγμα της κουζίνας).", **B)
    f[1].p("Στο +2,30 γυρίζουν ανατολικά, περνούν κάτω από τη δοκό μέσα στον τοίχο και συνεχίζουν 30–40 cm μέσα στον τοίχο κουζίνας – σκάλας (Τ6Α-02).", **B)
    f[1].p("Ανεβαίνουν και βγαίνουν από την παρειά της κουζίνας πάνω από την ψευδοροφή της (+2,49 … +2,58). Προς το κλιμακοστάσιο δεν ανοίγεται καμία τρύπα· σφράγιση με πυράντοχη μαστίχη (Ε6).", **B)
    f[2].h("Π0 – ΤΙ ΚΑΤΑΣΚΕΥΑΖΕΤΑΙ", fill=INK)
    f[2].p("Όπως έχει εγκριθεί στις ανόψεις: τα καλώδια έρχονται από το shaft μέσα στον ψευδοδοκό του κλιμακοστασίου.", **B)
    f[2].p("Περνούν πάνω από την κάσα της πόρτας, μέσα από τον τοίχο, κάτω από τη δοκό: 37,5 mm καθαρά → σωλήνες ως Ø32 δίπλα-δίπλα, η παροχή 5×10 και η φόρτιση 5×6 χωρίς σωλήνα.", **B)
    f[2].p("Μπαίνουν στο κανάλι του τοίχου: η παροχή και οι γραμμές του shaft κατεβαίνουν στη βάση του και συνεχίζουν με τη δέσμη ΔΚ ως τον πίνακα. Σφράγιση στον πυράντοχο τοίχο.", **B)
    f[3].h("ΠΙΝΑΚΑΣ", fill=FEED)
    f[3].p("Στο δυτικό άκρο του χωλ, στον τοίχο προς το λουτρό γονέων (15 cm: 2 γυψοσανίδες + σκελετός 10 cm + 2 ανθυγρές). Κεντραρισμένος στον άξονα του χωλ.", **B)
    f[3].p("Μέσα στον τοίχο υπάρχουν 12,5 cm: χωρά ολόκληρος και ο πίνακας των 7 cm και ο συνηθισμένος των 9 cm. Τα φύλλα και το πλακάκι του λουτρού δεν αγγίζονται.", **B)
    f[3].p("Γύρω από το άνοιγμα πλαίσιο από προφίλ UA. Το κατέβασμα των συμπυκνωμάτων του split του Υπν.1, που είναι στον ίδιο τοίχο, πάει 30 cm νοτιότερα (Ε3).", **B)
    f[3].p("Προς τα βόρεια δωμάτια τα σπιράλ ανεβαίνουν μέσα στον τοίχο στο κενό του χωλ· προς το καθιστικό κατεβαίνουν στη βάση του (δέσμη ΔΚ).", **B)
    yc = min(q.y for q in f) - 10
    rows = [[p["id"], p["beam"], p["title"], p["how"] + ".", p["what"], p["n"]] for p in M.PASSES]
    rows += [[r["id"], "δάπεδο", r["short"].split(" – ")[0].split(":")[0], ("ΝΕΟ: " if r["new"] else "") + r["short"] + ".", r["txt"].split(": ", 1)[-1], r["n"]] for r in M.FLOOR_RUNS]
    colors = {i: (1.0, 0.93, 0.80) for i, p in enumerate(M.PASSES) if p["new"]}
    widths = [24, 46, 150, 420, 330, 110]; sc_ = (DC.X1 - X0) / float(sum(widths))
    yy = D.table(X0, yc, [w_ * sc_ for w_ in widths], rows, head=["", "ΔΟΚΟΣ", "ΑΠΟ ↔ ΠΡΟΣ", "ΠΩΣ ΠΕΡΝΟΥΝ", "ΤΙ ΠΕΡΝΑ", "ΣΩΛΗΝΕΣ"], size=5.9, lead=7.0, pad=2.2, bold_first=True, colors=colors, zebra=False)
    assert yy >= DC.YB - 2, "ΗΛ-07: ο πίνακας περασμάτων ξεχειλίζει %.0f pt" % (DC.YB - yy)
    DC.finish(no, "ΠΕΡΑΣΜΑΤΑ ΚΑΛΩΔΙΩΝ – ΤΟΜΕΣ", "ΔΚ δέσμη δαπέδου · Π2 κουζίνα · Π0 shaft · ο πίνακας στον τοίχο", "Τομές και κάτοψη τοίχου 1:12,5 · A3")


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
          ("ΗΛ-08", "Κέντρο ασθενών · Ethernet · συναγερμός · πυρανίχνευση · θερμοστάτες"), ("ΗΛ-09", "Μονογραμμικό σχέδιο – όψη πίνακα"), ("ΗΛ-10", "Πίνακας κυκλωμάτων και προστασιών")]


def sheet_00(no="ΗΛ-00"):
    y = DC.title("ΗΛΕΚΤΡΟΛΟΓΙΚΗ ΜΕΛΕΤΗ – Β1 (Α΄ · Β΄ · Γ΄ ΟΡΟΦΟΣ) – %s" % M.REV, "πρόταση προς έγκριση · τι άλλαξε με τις οδηγίες της 19/11 · τι χρειάζεται απόφαση")
    a, b, c_ = DC.cols(3, y, name="ΗΛ-00")
    n = CK.counts(); F = CK.feeder_calc()
    B = dict(size=7.7)
    a.h("ΤΙ ΑΛΛΑΞΕ ΜΕ ΤΙΣ ΟΔΗΓΙΕΣ ΤΗΣ 19/11")
    a.p("Κανονικός, συμμετρικός κάναβος σε κάθε χώρο: καθιστικό 4 × 3, υπνοδωμάτια 2 × 2. Καμία ράγα, κανένα κρεμαστό, καμία απλίκα (ΗΛ-04, ΗΛ-05).", bold="1 · Φωτισμός μόνο με spots.", **B)
    a.p("Τα 4 spots συμμετρικά στους άξονες του δωματίου – όχι ένα πάνω από το γραφείο.", bold="2 · Υπνοδωμάτιο 2.", **B)
    a.p("Ο βόρειος τοίχος του σαλονιού μένει όπως είναι στις τοιχοποιίες, περασιά με το δοκάρι. Το κανάλι του R01 καταργήθηκε· καμία αλλαγή τοιχοποιίας.", bold="3 · Τοίχος χωρίς +5,5 cm.", **B)
    a.p("Στο δυτικό άκρο του χωλ, στον τοίχο του λουτρού γονέων (12,5 cm διαθέσιμα μέσα στον τοίχο). Λεπτομέρεια: ΗΛ-07.", bold="4 · Πίνακας.", **B)
    a.p("Κανένα ρολό: έφυγαν 2 κυκλώματα, 4 μοτέρ και 4 πλήκτρα.", bold="5 · Χωρίς ηλεκτρικά ρολά.", **B)
    a.p("Εστίες με τριφασική γραμμή 5×2,5.", bold="6 · Τριφασικές εστίες.", **B)
    a.h("ΑΠΟ ΤΟ R01 ΜΕΝΟΥΝ")
    a.p("Κανένα σπιράλ μέσα στην πλάκα · σε κάθε σημείο ύψος και απόσταση · φόρτιση αυτοκινήτου 11 kW με διαχείριση φορτίου · κέντρο ασθενών στην τεχνική ντουλάπα του χωλ · "
        "Ethernet σε κάθε δωμάτιο (%d θύρες) · χωρίς KNX." % sum(d[4] for d in M.DATA), **B)
    a.h("ΤΟ ΔΙΑΜΕΡΙΣΜΑ ΣΕ ΑΡΙΘΜΟΥΣ")
    a.table([250, 100], [["Κυκλώματα πίνακα (+ 2 εφεδρικά)", "%d" % len(M.CIRCUITS)], ["Θέσεις ρευματοδοτών / μηχανισμοί", "%d / %d" % (n["sock_pts"], n["sock_out"])],
                         ["Πλαίσια διακοπτών / πλήκτρα", "%d / %d" % (n["sw_plates"], sum(n["sw"].values()))],
                         ["Χωνευτά spots", "%d" % sum(n["spots"].values())], ["Λήψεις Ethernet / TV", "%d / %d" % (sum(d[4] for d in M.DATA), len(M.TV))],
                         ["Ανιχνευτές πυρανίχνευσης · θερμοστάτες", "%d · %d" % (len(M.DETECTORS), len(M.THERMOSTATS))],
                         ["Μέγιστη ζήτηση (χωρίς τη φόρτιση)", "%s kW · %s A στη φάση" % (fz(F["dem"], 1), fz(F["imax"], 0))]], size=7.4, lead=8.8, pad=2.6, aligns={1: "r"})
    b.h("ΤΙ ΦΕΡΝΕΙ Ο ΤΟΙΧΟΣ ΠΕΡΑΣΙΑ ΜΕ ΤΟ ΔΟΚΑΡΙ", fill=CHANC)
    b.p("Οι ψευδοροφές είναι περασιά με τα δοκάρια: από το ταβάνι του χωλ δεν περνά καλώδιο στο ταβάνι του σαλονιού. Με τον τοίχο περασιά με το δοκάρι δεν υπάρχει ούτε "
        "χώρος δίπλα του για να ανέβουν. Χωρίς σπιράλ στο μπετό μένει ένας δρόμος:", **B)
    b.p("από τον πίνακα προς σαλόνι και κουζίνα τα σπιράλ στρώνονται ΠΑΝΩ στην πλάκα, πριν από το γέμισμα (≈ %d σωλήνες, 9 m). Δεν σκάβεται τίποτα – ΕΡΩΤΗΣΗ Ε1." % M.DK_N,
        bold="ΔΚ – δέσμη δαπέδου:", **B)
    b.p("πρίζες και διακόπτες τροφοδοτούνται από κάτω, μέσα στον τοίχο τους.", bold="Τοίχοι του σαλονιού:", **B)
    b.p("spots, ανιχνευτές και κλιματιστικό ανεβαίνουν από το κανάλι που ήδη έχει ο τοίχος της πόρτας εισόδου.", bold="Ταβάνι του σαλονιού:", **B)
    b.p("όπως στο R01, από τη γωνία του τοίχου της πόρτας (Π2).", bold="Κουζίνα:", **B)
    b.p("όπως στο R01, από το ταβάνι του χωλ – ο πίνακας είναι τώρα στην ίδια πλευρά.", bold="Υπνοδωμάτια, λουτρά, χωλ:", **B)
    b.h("ΤΙ ΑΛΛΑΖΕΙ ΣΤΑ ΑΛΛΑ ΤΕΥΧΗ (ΑΝ ΕΓΚΡΙΘΕΙ)")
    b.table([70, 280], [["Τοιχοποιίες", "ΚΑΜΙΑ αλλαγή"],
                        ["Ανόψεις Β1 → R24", "ο φωτισμός με spots: κάναβος καθιστικού 4 × 3, Υπν.2, χωρίς παροχές κρεμαστών, ανιχνευτής ΑΚ1"],
                        ["Αποχετεύσεις → R29", "κατέβασμα συμπυκνωμάτων του split Υπν.1 30 cm νοτιότερα (πίσω του μπαίνει ο πίνακας)"],
                        ["Ξυλότυποι", "ΚΑΜΙΑ αλλαγή – τίποτα δεν μπαίνει στο μπετό"]], size=7.2, lead=8.6, pad=2.6, bold_first=True)
    b.h("ΠΕΡΙΕΧΟΜΕΝΑ")
    b.table([40, 310], [[s_[0], s_[1]] for s_ in SHEETS], size=7.4, lead=8.8, pad=2.4, bold_first=True)
    c_.h("ΑΝΟΙΚΤΑ – ΧΡΕΙΑΖΟΜΑΙ ΑΠΑΝΤΗΣΗ", fill=DC.WARNC)
    c_.table([24, 64, 262], [[o[0], o[1], o[2]] for o in M.OPEN], size=7.0, lead=8.3, pad=2.6, bold_first=True)
    c_.h("ΔΕΝ ΕΧΕΙ ΓΙΝΕΙ ΑΚΟΜΗ")
    c_.p("Ισόγειο, Δ΄ όροφος, σοφίτα και κοινόχρηστα – με την ίδια λογική, αφού εγκριθεί ο τυπικός όροφος.", bullet="•", **B)
    c_.p("Τεχνικές προδιαγραφές υλικών, λίστα υλικών με ποσότητες και οδηγίες για τον ηλεκτρολόγο: βγαίνουν από το ίδιο μοντέλο μόλις κλειδώσουν οι θέσεις (τα είχε το R00 – "
         "δεν ξανατυπώθηκαν για να μείνει το τεύχος απλό).", bullet="•", **B)
    c_.p("Φωτοτεχνικός υπολογισμός με λογισμικό – εδώ η μέση στάθμη υπολογίστηκε με τη μέθοδο της φωτεινής ροής.", bullet="•", **B)
    DC.finish(no, "ΣΥΝΟΨΗ – ΤΙ ΑΛΛΑΞΕ, ΤΙ ΧΡΕΙΑΖΕΤΑΙ ΑΠΟΦΑΣΗ", "Οδηγίες 19/11 · περάσματα μετά το μπετό · %d ανοικτά" % len(M.OPEN))


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
