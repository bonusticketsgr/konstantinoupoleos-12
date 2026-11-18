"""Φύλλα λουτρών: κάτοψη με κάναβο δαπέδου + όλες οι όψεις με κάναβο τοίχων, εσοχές / ντουλάπια, είδη (A3, 1:25)."""
import math
from lt_draw import (V2, S25, fm, lvl, marker, PAGE_W, PAGE_H, DARK, GREY, DIMC, frame_and_title, north_arrow,
                     TILE, TILE_CUT, JOINT, NICHE, NICHE_IN, GLASS, GLASS_F, WOOD, MIRROR, SAN, PRE, PRE_F, WALLG, COLG,
                     ETICSG, HID, RED, WHITE)

STONE = (0.93, 0.91, 0.87)
CAB = (0.90, 0.85, 0.76)
METAL = (0.30, 0.30, 0.33)
LED = (0.95, 0.60, 0.05)            # κρυφός φωτισμός
LED_F = (1.00, 0.94, 0.70)
MOS = (0.945, 0.905, 0.84)          # ψηφίδα kit-kat
MOS_L = (0.74, 0.67, 0.57)
MOSC = (0.62, 0.42, 0.20)
BAND = (0.89, 0.89, 0.90)           # σκοτία πάνω από το πλακάκι ως την ψευδοροφή
TOP = 2.50
EPS = 2e-3


def bbox(p):
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    return min(xs), min(ys), max(xs), max(ys)


def in_mosaic(E, u):
    return any(a - EPS <= u <= b + EPS for a, b in E.get("mosaic", []))


# ======================================================================================================== ΑΝΑΛΥΣΗ ΚΟΜΜΑΤΙΩΝ
def cells(E):
    us = sorted(set([0.0, E["w"]] + list(E.get("jv", []))))
    zs = [0.0] + [z for z in E.get("jh", [1.20]) if z < E["h"] - 1e-6] + [E["h"]]
    return us, zs


def pieces(E):
    """Κομμάτια πλακιδίου 60 × 120 της όψης μετά την αφαίρεση ανοιγμάτων / ντουλαπιών / καθρεπτών / εσοχών (χωρίς τις ζώνες ψηφίδας).
    minleg = το στενότερο «πόδι» του κομματιού (m) – για τον έλεγχο «κανένα κομμάτι κάτω από 20 cm»."""
    us, zs = cells(E)
    out = []
    for u0, u1 in zip(us[:-1], us[1:]):
        if in_mosaic(E, (u0 + u1) / 2):
            continue
        for z0, z1 in zip(zs[:-1], zs[1:]):
            vs = [v for v in E.get("voids", []) if v["u0"] < u1 - EPS and v["u1"] > u0 + EPS and v["z0"] < z1 - EPS and v["z1"] > z0 + EPS]
            ucut = sorted(set([u0, u1] + [min(max(v[k], u0), u1) for v in vs for k in ("u0", "u1")]))
            zcut = sorted(set([z0, z1] + [min(max(v[k], z0), z1) for v in vs for k in ("z0", "z1")]))
            ucut = [a for i, a in enumerate(ucut) if i == 0 or a - ucut[i - 1] > EPS]
            zcut = [a for i, a in enumerate(zcut) if i == 0 or a - zcut[i - 1] > EPS]
            free = [[not any(v["u0"] <= (a0 + a1) / 2 <= v["u1"] and v["z0"] <= (b0 + b1) / 2 <= v["z1"] for v in vs)
                     for a0, a1 in zip(ucut[:-1], ucut[1:])] for b0, b1 in zip(zcut[:-1], zcut[1:])]
            area = sum((ucut[i + 1] - ucut[i]) * (zcut[j + 1] - zcut[j]) for j in range(len(zcut) - 1) for i in range(len(ucut) - 1) if free[j][i])
            if area < 1e-5:
                continue
            legs = []
            for j in range(len(zcut) - 1):          # οριζόντιες λωρίδες → πλάτη
                run = 0.0
                for i in range(len(ucut) - 1):
                    if free[j][i]: run += ucut[i + 1] - ucut[i]
                    elif run > 0: legs.append(run); run = 0.0
                if run > 0: legs.append(run)
            for i in range(len(ucut) - 1):          # κατακόρυφες λωρίδες → ύψη
                run = 0.0
                for j in range(len(zcut) - 1):
                    if free[j][i]: run += zcut[j + 1] - zcut[j]
                    elif run > 0: legs.append(run); run = 0.0
                if run > 0: legs.append(run)
            full = abs(u1 - u0 - 0.60) < EPS and abs(z1 - z0 - 1.20) < EPS
            out.append(dict(u0=u0, u1=u1, z0=z0, z1=z1, area=area, minleg=min(legs), full=full,
                            whole=full and abs(area - 0.72) < 1e-4, notched=bool(vs)))
    return out


def mosaic_area(E):
    a = 0.0
    for u0, u1 in E.get("mosaic", []):
        a += (u1 - u0) * E["h"]
        for v in E.get("voids", []):
            du = min(u1, v["u1"]) - max(u0, v["u0"]); dz = min(E["h"], v["z1"]) - max(0, v["z0"])
            if du > 0 and dz > 0: a -= du * dz
    return a


# ======================================================================================================== ΟΨΗ
def draw_elev(c, E, ox, oy, s=S25):
    v = V2(c, ox, oy, s)
    W, H = E["w"], E["h"]
    us, zs = cells(E)
    # ---- πλακάκια
    for u0, u1 in zip(us[:-1], us[1:]):
        mos = in_mosaic(E, (u0 + u1) / 2)
        for z0, z1 in zip(zs[:-1], zs[1:]):
            full = abs(u1 - u0 - 0.60) < EPS and abs(z1 - z0 - 1.20) < EPS
            v.rect(u0, z0, u1, z1, fill=MOS if mos else (TILE if full else TILE_CUT))
    # ---- μικρό πλακάκι στο ντους με την καμπύλη (ενδεικτικά 5 × 15 cm – όχι απαραίτητα kit-kat)
    for u0, u1 in E.get("mosaic", []):
        c.saveState()
        X0, Y0 = v.p(u0, 0); X1, Y1 = v.p(u1, H)
        pth = c.beginPath(); pth.rect(X0, Y0, X1 - X0, Y1 - Y0); c.clipPath(pth, stroke=0, fill=0)
        c.setStrokeColorRGB(*MOS_L)
        c.setLineWidth(0.22)
        n = int(round((u1 - u0) / 0.05)); st = (u1 - u0) / max(n, 1)
        for i in range(1, n):
            c.line(*v.p(u0 + i * st, 0), *v.p(u0 + i * st, H))
        c.setLineWidth(0.28)
        z = 0.15
        while z < H - 1e-6:
            c.line(*v.p(u0, z), *v.p(u1, z)); z += 0.15
        c.restoreState()
    for u in us[1:-1]:
        v.line(u, 0, u, H, color=JOINT, lw=0.55)
    for z in zs[1:-1]:
        v.line(0, z, W, z, color=JOINT, lw=0.55)
    for u in E.get("breaks", []):          # γωνία (αλλαγή επιπέδου)
        v.line(u, 0, u, H, color=DARK, lw=1.0)
    # ---- κρυφά (πίσω από το πλακάκι)
    for it in E.get("items", []):
        if it[0] == "hidden":
            v.rect(it[1], 0, it[2], H, stroke=HID, lw=0.55, dash=[2.2, 2.2])
            v.text((it[1] + it[2]) / 2, 0.62, it[3], size=5.0, font="Inter-Medium", color=HID, rot=90, bg=TILE)
        elif it[0] == "curve_mark":
            v.line(it[1], 0, it[1], H, color=MOSC, lw=0.5, dash=[5, 2.5])
            v.text(it[1], 0.34, it[2], size=4.6, color=MOSC, font="Inter-Medium", rot=90, dx=-3.6, bg=MOS)
    # ---- ανοίγματα / ντουλάπια / καθρέπτες / εσοχές
    for vd in E.get("voids", []):
        u0, u1, z0, z1 = vd["u0"], vd["u1"], vd["z0"], vd["z1"]
        cu, cz = (u0 + u1) / 2, (z0 + z1) / 2
        k = vd["kind"]
        if k == "window":
            v.rect(u0, z0, u1, z1, fill=WHITE, stroke=DARK, lw=0.9)
            v.rect(u0 + 0.035, z0 + 0.035, u1 - 0.035, z1 - 0.035, stroke=DARK, lw=0.45)
            v.rect(u0 + 0.075, z0 + 0.075, u1 - 0.075, z1 - 0.075, fill=GLASS_F, stroke=GLASS, lw=0.4)
            v.text(cu, cz + 0.05, vd["label"], size=6.4, font="Inter-SemiBold", color=GLASS)
            v.text(cu, cz - 0.07, "%s × %s" % (fm(u1 - u0), fm(z1 - z0)), size=5.2, color=GLASS)
        elif k == "door":
            v.rect(u0, z0, u1, z1, fill=WHITE, stroke=DARK, lw=0.9)
            v.rect(u0 + 0.04, z0, u1 - 0.04, z1 - 0.04, fill=(0.975, 0.97, 0.955), stroke=GREY, lw=0.45)
            hu = u0 + 0.11 if vd.get("handle", "l") == "l" else u1 - 0.11
            v.rect(hu - 0.012, 0.99, hu + 0.012, 1.11, fill=METAL)
            v.text(cu, 1.45, vd["label"], size=6.4, font="Inter-SemiBold", color=GREY)
            v.text(cu, 1.33, "%s × %s" % (fm(u1 - u0), fm(z1 - z0)), size=5.6, color=GREY)
        elif k == "cabinet":
            v.rect(u0, z0, u1, z1, fill=CAB, stroke=DARK, lw=0.8)
            n = vd.get("doors", 2); dw = (u1 - u0) / n
            for i in range(n):
                a0, a1 = u0 + i * dw, u0 + (i + 1) * dw
                if i: v.line(a0, z0, a0, z1, color=DARK, lw=0.6)
                hinge = a0 if i < n / 2 else a1; free = a1 if i < n / 2 else a0   # σύμβολο ανοίγματος (διακεκομμένο)
                v.line(hinge, z0, free, cz, color=GREY, lw=0.3, dash=[3, 2]); v.line(hinge, z1, free, cz, color=GREY, lw=0.3, dash=[3, 2])
            v.text(cu, cz + 0.07, vd["label"] + " ΚΛΕΙΣΤΟ", size=5.8, font="Inter-SemiBold", bg=CAB)
            v.text(cu, cz - 0.05, "%d φύλλα × %s · βάθος 15" % (n, fm(dw)), size=5.2, bg=CAB)
            v.text(cu, cz - 0.15, "%s × %s" % (fm(u1 - u0), fm(z1 - z0)), size=5.2, bg=CAB)
        elif k == "mirror":
            v.rect(u0, z0, u1, z1, fill=MIRROR, stroke=DARK, lw=0.7)
            for d in (0.0, 0.07):
                v.line(u0 + 0.08 + d, z1 - 0.34, u0 + 0.30 + d, z1 - 0.08, color=WHITE, lw=1.1)
            v.text(cu, cz + 0.05, vd["label"], size=5.8, font="Inter-SemiBold", color=(0.25, 0.40, 0.50))
            v.text(cu, cz - 0.07, "%s × %s" % (fm(u1 - u0), fm(z1 - z0)), size=5.2, color=(0.25, 0.40, 0.50))
        elif k == "niche":
            v.rect(u0, z0, u1, z1, fill=NICHE_IN, stroke=DARK, lw=0.8)
            v.rect(u0, z1 - 0.045, u1, z1, fill=NICHE); v.rect(u0, z0, u0 + 0.03, z1, fill=NICHE)
            for zz in vd.get("shelf", []):
                v.line(u0, zz, u1, zz, color=DARK, lw=1.3)
            if vd.get("led"):
                v.line(u0 + 0.035, z1 - 0.055, u1 - 0.01, z1 - 0.055, color=LED, lw=1.5)
            v.rect(u0, z0, u1, z1, stroke=DARK, lw=0.8)
            zm = vd.get("shelf", [cz])[0]
            v.text(cu + 0.012, (zm + z1 - 0.045) / 2 - 0.02, vd["label"], size=4.9, font="Inter-SemiBold")
            v.text(cu + 0.012, (z0 + zm) / 2 + 0.035, "%s×%s" % (fm(u1 - u0), fm(z1 - z0)), size=4.6)
            v.text(cu + 0.012, (z0 + zm) / 2 - 0.045, "ράφι · LED", size=4.2, color=GREY)
    # ---- είδη
    for it in E.get("items", []):
        k = it[0]
        if k == "wc_front":
            u = it[1]
            v.rect(u - 0.25, 0, u + 0.25, 1.12, stroke=HID, lw=0.5, dash=[2.2, 2.2])
            v.text(u + 0.245, 0.60, "πλαίσιο καζανακιού", size=4.6, color=HID, rot=90, dx=-3.2)
            v.rrect(u - 0.123, 1.05 - 0.082, u + 0.123, 1.05 + 0.082, 0.012, fill=(0.94, 0.94, 0.94), stroke=DARK, lw=0.55)
            v.circle(u - 0.055, 1.05, 0.034, stroke=DARK, lw=0.4); v.circle(u + 0.045, 1.05, 0.046, stroke=DARK, lw=0.4)
            v.rrect(u - 0.18, 0.10, u + 0.18, 0.42, 0.11, fill=SAN, stroke=DARK, lw=0.7)
            v.rect(u - 0.18, 0.36, u + 0.18, 0.42, fill=SAN, stroke=DARK, lw=0.7)
            v.line(u, -0.02, u, 1.20, color=RED, lw=0.35, dash=[6, 2, 1, 2])
        elif k == "wc_side":
            u, d = it[1], it[2]
            pts = [(0, 0.42), (0.54, 0.42), (0.545, 0.36), (0.50, 0.24), (0.40, 0.13), (0.18, 0.10), (0, 0.10)]
            v.poly([(u + d * a, b) for a, b in pts], fill=SAN, stroke=DARK, lw=0.7)
            v.rect(u, 0.42, u + d * 0.50, 0.445, fill=SAN, stroke=DARK, lw=0.6)
            v.rect(u, 1.05 - 0.082, u + d * 0.012, 1.05 + 0.082, fill=METAL)
        elif k == "counter_front":          # κτιστός πάγκος: πλάκα 12 cm ντυμένη με το ίδιο πλακάκι, ανοιχτός από κάτω, κρυφό LED
            u0, u1, ub = it[1], it[2], it[3]
            op = it[4] if len(it) > 4 else {}
            v.rect(u0, 0.63, u1, 0.75, fill=TILE, stroke=DARK, lw=0.9)
            v.rrect(ub - 0.24, 0.75, ub + 0.24, 0.88, 0.025, fill=SAN, stroke=DARK, lw=0.7)
            v.line(u0 + 0.03, 0.615, u1 - 0.03, 0.615, color=LED, lw=1.4)
            lu = op.get("label_u", (u0 + u1) / 2)
            v.text(lu, 0.545, "ΚΤΙΣΤΟΣ ΠΑΓΚΟΣ +0,75", size=4.6, font="Inter-SemiBold", bg=TILE)
            v.text(lu, 0.475, "νιπτήρας από πάνω · LED από κάτω", size=4.2, bg=TILE)
            for pu, ps in op.get("parts", []):
                v.text(pu, 0.545, ps, size=4.3, font="Inter-SemiBold", bg=MOS if in_mosaic(E, pu) else TILE)
        elif k == "counter_side":
            u, d, dep = it[1], it[2], it[3]
            v.rect(u, 0.63, u + d * dep, 0.75, fill=TILE, stroke=DARK, lw=0.9)
            v.rrect(u + d * 0.08, 0.75, u + d * 0.44, 0.88, 0.025, fill=SAN, stroke=DARK, lw=0.7)
            v.line(u + d * 0.04, 0.615, u + d * (dep - 0.06), 0.615, color=LED, lw=1.4)
        elif k == "tap":
            u, z = it[1], it[2]
            v.circle(u, z, 0.024, fill=METAL); v.rect(u - 0.011, z - 0.012, u + 0.011, z + 0.012, fill=METAL)
            v.circle(u + 0.11, z, 0.024, fill=METAL)
            v.text(u + 0.055, z + 0.082, "μπαταρία τοίχου %s" % lvl(z), size=4.6, bg=TILE)
            v.line(u, 0.60, u, 1.20, color=RED, lw=0.35, dash=[6, 2, 1, 2])
        elif k == "tap_side":
            u, d, z = it[1], it[2], it[3]
            v.rect(u, z - 0.02, u + d * 0.19, z + 0.012, fill=METAL)
        elif k == "mirror_side":
            u, d = it[1], it[2]
            v.rect(u, 1.20, u + d * 0.012, 2.40, fill=GLASS)
        elif k == "mixer":
            u, z = it[1], it[2]
            v.circle(u, z, 0.075, fill=(0.94, 0.94, 0.94), stroke=DARK, lw=0.6)
            v.circle(u, z, 0.028, fill=METAL)
            v.circle(u, z - 0.17, 0.022, fill=METAL)
            v.text(u + 0.10, z - 0.17, "μίκτης %s" % lvl(z), size=4.8, anchor="l", bg=TILE)
            v.line(u, -0.02, u, H, color=RED, lw=0.35, dash=[6, 2, 1, 2])
        elif k == "head_front":
            u, z = it[1], it[2]
            v.circle(u, z, 0.03, fill=METAL)
            v.rect(u - 0.125, z - 0.075, u + 0.125, z - 0.055, fill=METAL)
            v.text(u + 0.15, z - 0.03, "κεφαλή %s" % lvl(z), size=4.8, anchor="l", bg=MOS if in_mosaic(E, u) else TILE)
        elif k == "head_side":
            u, d, z = it[1], it[2], it[3]
            v.line(u, z, u + d * 0.40, z, color=METAL, lw=1.4)
            v.line(u + d * 0.40, z, u + d * 0.40, z - 0.055, color=METAL, lw=1.4)
            v.rect(u + d * 0.40 - 0.125, z - 0.075, u + d * 0.40 + 0.125, z - 0.055, fill=METAL)
        elif k == "mixer_side":
            u, d, z = it[1], it[2], it[3]
            v.rect(u, z - 0.075, u + d * 0.045, z + 0.075, fill=(0.80, 0.80, 0.82), stroke=DARK, lw=0.5)
            if len(it) > 4:
                v.text(u + d * 0.08, z, it[4], size=4.6, anchor="r" if d < 0 else "l", bg=MOS if in_mosaic(E, u + d * 0.2) else TILE)
        elif k == "glass_edge":
            u = it[1]
            v.rect(u - 0.007, 0, u + 0.007, 2.10, fill=GLASS)
            v.text(u + 0.045, it[2] if len(it) > 2 else 0.52, "γυαλί 0,70 × 2,10", size=4.8, color=GLASS, font="Inter-Medium", rot=90)
        elif k == "drain_lin":
            v.rect(it[1], 0, it[2], 0.02, fill=METAL)
            v.text((it[1] + it[2]) / 2, 0.075, "γραμμικό σιφώνι %s" % fm(it[2] - it[1]), size=4.8, bg=MOS if in_mosaic(E, it[1]) else TILE)
        elif k == "drain_end":
            v.rect(it[1], 0, it[2], 0.02, fill=METAL)
        elif k == "ledge_cut":             # το ράφι του ντους (συνέχεια του πάγκου) κομμένο από το επίπεδο της όψης
            v.rect(it[1], 0.63, it[2], 0.75, fill=TILE, stroke=DARK, lw=0.9)
            v.hatch([(it[1], 0.63), (it[2], 0.63), (it[2], 0.75), (it[1], 0.75)], step_pt=3.0, color=JOINT, lw=0.3)
            v.text((it[1] + it[2]) / 2, 0.80, it[3] + " +0,75", size=4.6, font="Inter-SemiBold", bg=MOS)
    # ---- σκοτία πάνω από το πλακάκι ως την ψευδοροφή (+2,40 … +2,50) · κρυφό LED όπου cove
    v.rect(0, H, W, TOP, fill=BAND)
    cv = E.get("cove")
    if cv:
        a, b = (0.0, W) if cv is True else cv
        v.rect(a, H, b, TOP, fill=LED_F)
        v.line(a + 0.02, H + 0.03, b - 0.02, H + 0.03, color=LED, lw=1.6)
        v.text(a + 0.04, (H + TOP) / 2 + 0.012, "κρυφό LED", size=4.4, font="Inter-SemiBold", color=LED, anchor="l")
    lab_c = "σκοτία ως την ψευδοροφή +2,40 … +2,50" if W > 1.6 else "ψευδοροφή +2,40…+2,50"
    if cv and cv is not True and cv[1] >= W - 0.01:
        v.text(0.03, (H + TOP) / 2, lab_c, size=4.3, color=GREY, anchor="l")
    else:
        v.text(W - 0.03, (H + TOP) / 2, lab_c, size=4.3, color=GREY, anchor="r")
    # ---- περίγραμμα
    v.line(-0.06, 0, W + 0.06, 0, color=DARK, lw=1.5)
    v.line(0, H, W, H, color=DARK, lw=0.7)
    v.line(-0.06, TOP, W + 0.06, TOP, color=DARK, lw=1.1)
    v.line(0, 0, 0, TOP, color=DARK, lw=1.1); v.line(W, 0, W, TOP, color=DARK, lw=1.1)
    # ---- διαστάσεις
    lab = ["μικρό πλακάκι %s" % fm(b - a) if in_mosaic(E, (a + b) / 2) else fm(b - a) for a, b in zip(us[:-1], us[1:])]
    v.chain_h(us, 0, off=-15, labels=lab)
    zones = E.get("zones", [0, W])
    v.chain_h(zones, 0, off=-31, size=6.0, color=GREY, ext=False)
    for i, nm in enumerate(E.get("zone_names", [])):
        if nm:
            v.text((zones[i] + zones[i + 1]) / 2, 0, nm, size=5.4, font="Inter-SemiBold", color=GREY, dy=-41)
    v.chain_v(zs, W, off=17)
    if E.get("zmarks"):
        v.chain_v(E["zmarks"], 0, off=-17, size=6.0, color=GREY)
    # ---- τίτλος
    X, Y = v.p(0, TOP)
    c.setFillColorRGB(*DARK); c.setStrokeColorRGB(*DARK); c.setLineWidth(0.8)
    c.circle(X + 8, Y + 14, 8, stroke=1, fill=0)
    c.setFont("Inter-Bold", 9.5); c.drawCentredString(X + 8, Y + 10.6, E["id"])
    c.setFont("Inter-Bold", 8.6); c.drawString(X + 21, Y + 15.5, "ΟΨΗ %s  ·  %s" % (E["id"], E["title"]))
    c.setFont("Inter", 6.0); c.setFillColorRGB(*GREY); c.drawString(X + 21, Y + 6.2, E.get("note", ""))


# ======================================================================================================== ΚΑΤΟΨΗ
def _polyline(c, v, pts, color, lw, dash=None):
    c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
    pth = c.beginPath(); pth.moveTo(*v.p(*pts[0]))
    for q in pts[1:]:
        pth.lineTo(*v.p(*q))
    c.drawPath(pth, stroke=1, fill=0); c.setDash([])


def draw_plan(c, R, M, ox, oy, s=S25, light=False):
    x0, y0, x1, y1 = R["view"]
    v = V2(c, ox, oy, s, ydown=True, a0=x0, b0=y0)
    Wp, Hp = (x1 - x0) * s, (y1 - y0) * s
    c.saveState()
    path = c.beginPath(); path.rect(ox, oy - Hp, Wp, Hp); c.clipPath(path, stroke=0, fill=0)
    # ---- υπόβαθρο από το μοντέλο τοιχοποιιών
    for p in list(M.ETICS) + list(getattr(M, "ETICS5", [])):
        v.poly(p, fill=ETICSG)
    for w in M.WALLS:
        v.poly(w["pts"], fill=WALLG, stroke=(0.55, 0.55, 0.58), lw=0.35)
    for p in M.COLS:
        v.poly(p, fill=COLG, stroke=DARK, lw=0.4)
    for p in M.WINS:
        b = bbox(p)
        v.poly(p, fill=WHITE, stroke=DARK, lw=0.4)
        if b[2] - b[0] >= b[3] - b[1]:
            v.line(b[0], (b[1] + b[3]) / 2, b[2], (b[1] + b[3]) / 2, color=GLASS, lw=1.0)
        else:
            v.line((b[0] + b[2]) / 2, b[1], (b[0] + b[2]) / 2, b[3], color=GLASS, lw=1.0)
    # ---- προτάσεις (αλλαγές στην τοιχοποιία)
    for kind, r in ([] if light else R.get("patches", [])):
        if kind == "remove":
            v.rect(*r, fill=WHITE, stroke=PRE, lw=0.6, dash=[2, 1.5])
        else:
            v.rect(*r, fill=PRE_F, stroke=PRE, lw=0.6); v.hatch([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])])
    for pr in ([] if light else R.get("pre", [])):
        r = pr["r"]
        v.rect(*r, fill=PRE_F, stroke=PRE, lw=0.5); v.hatch([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])])
    # ---- δάπεδο: κάναβος πλακιδίων (αποκοπή στο τελικό περίγραμμα)
    c.saveState()
    fp = c.beginPath(); P = [v.p(*q) for q in R["floor"]]
    fp.moveTo(*P[0])
    for q in P[1:]: fp.lineTo(*q)
    fp.close(); c.clipPath(fp, stroke=0, fill=0)
    for f in R["fields"]:
        a0, b0, a1, b1 = f["r"]
        xs = sorted(set([a0, a1] + list(f["xc"]))); ys = sorted(set([b0, b1] + list(f["yc"])))
        for xa, xb in zip(xs[:-1], xs[1:]):
            for ya, yb in zip(ys[:-1], ys[1:]):
                d = sorted([xb - xa, yb - ya])
                full = abs(d[0] - 0.60) < 0.012 and abs(d[1] - 1.20) < EPS
                v.rect(xa, ya, xb, yb, fill=TILE if (full or light) else TILE_CUT)
    jc, jl = ((0.80, 0.78, 0.74), 0.3) if light else (JOINT, 0.6)
    for f in R["fields"]:
        a0, b0, a1, b1 = f["r"]
        v.rect(a0, b0, a1, b1, stroke=jc, lw=jl)
        for x in f["xc"]: v.line(x, b0, x, b1, color=jc, lw=jl)
        for y in f["yc"]: v.line(a0, y, a1, y, color=jc, lw=jl)
    c.restoreState()
    v.poly(R["floor"], stroke=DARK, lw=0.9)
    # ---- ψηφίδα στους τοίχους του ντους (γραμμή πάνω στην τελική παρειά)
    if R.get("mosaic_line") and not light:
        _polyline(c, v, R["mosaic_line"], MOSC, 2.2)
    # ---- εσοχές / ντουλάπια μέσα στους τοίχους · ραφάκια
    for n in R.get("niches", []):
        v.rect(*n["r"], fill=CAB if n.get("cab") else NICHE_IN, stroke=DARK, lw=0.6)
    # ---- αποχέτευση
    for r in R.get("lin", []):
        v.rect(*r, fill=METAL)
    for x, y, nm in ([] if light else R.get("traps", [])):
        v.rect(x - 0.05, y - 0.05, x + 0.05, y + 0.05, fill=WHITE, stroke=DARK, lw=0.6)
        v.line(x - 0.05, y - 0.05, x + 0.05, y + 0.05, lw=0.35); v.line(x - 0.05, y + 0.05, x + 0.05, y - 0.05, lw=0.35)
        v.text(x, y + 0.115, nm, size=4.8, font="Inter-Medium")
    for x, y, nm in ([] if light else R.get("stacks", [])):
        v.circle(x, y, 0.055, stroke=HID, lw=0.7, dash=[2, 1.5], fill=WHITE)
        v.text(x, y, nm, size=3.6, color=HID, font="Inter-SemiBold")
    # ---- είδη
    for w in R.get("wc", []):
        if w["wall"] == "W":
            v.rrect(w["face"], w["axis"] - 0.18, w["face"] + 0.54, w["axis"] + 0.18, 0.16, fill=SAN, stroke=DARK, lw=0.7)
            v.rect(w["face"], w["axis"] - 0.18, w["face"] + 0.14, w["axis"] + 0.18, fill=SAN, stroke=DARK, lw=0.7)
            v.line(w["face"] - 0.30, w["axis"], w["face"] + 0.75, w["axis"], color=RED, lw=0.35, dash=[6, 2, 1, 2])
        elif w["wall"] == "N":
            v.rrect(w["axis"] - 0.18, w["face"], w["axis"] + 0.18, w["face"] + 0.54, 0.16, fill=SAN, stroke=DARK, lw=0.7)
            v.rect(w["axis"] - 0.18, w["face"], w["axis"] + 0.18, w["face"] + 0.14, fill=SAN, stroke=DARK, lw=0.7)
            v.line(w["axis"], w["face"] - 0.30, w["axis"], w["face"] + 0.75, color=RED, lw=0.35, dash=[6, 2, 1, 2])
    for vn in R.get("vanity", []):
        if vn.get("poly"):
            v.poly(vn["poly"], fill=TILE if vn.get("built") else STONE, stroke=DARK, lw=0.9)
        else:
            v.rect(*vn["r"], fill=TILE if vn.get("built") else STONE, stroke=DARK, lw=0.9)
        bx, by = vn["basin"]
        if vn["wall"] == "W":
            v.rrect(bx - 0.17, by - 0.24, bx + 0.17, by + 0.24, 0.05, fill=WHITE, stroke=DARK, lw=0.5)
            v.rect(vn["r"][0], by - 0.012, vn["r"][0] + 0.17, by + 0.012, fill=METAL)
            v.line(vn["r"][0] - 0.10, by, vn["r"][2] + 0.12, by, color=RED, lw=0.35, dash=[6, 2, 1, 2])
        else:
            v.rrect(bx - 0.24, by - 0.17, bx + 0.24, by + 0.17, 0.05, fill=WHITE, stroke=DARK, lw=0.5)
            v.rect(bx - 0.012, vn["r"][3] - 0.17, bx + 0.012, vn["r"][3], fill=METAL)
            v.line(bx, vn["r"][1] - 0.12, bx, vn["r"][3] + 0.10, color=RED, lw=0.35, dash=[6, 2, 1, 2])
    for sh in R.get("shower", []):
        mx, my = sh["mix"]; hx, hy = sh["head"]; ax, ay = sh["arm_from"]; dx, dy = sh.get("mix_dir", (1, 0))
        v.line(ax, ay, hx, hy, color=METAL, lw=1.0)
        v.circle(hx, hy, 0.125, stroke=METAL, lw=0.6, dash=[2.5, 1.5])
        v.circle(mx + dx * 0.02, my + dy * 0.02, 0.03, fill=METAL)
    for a, b in R.get("glass", []):
        v.line(a[0], a[1], b[0], b[1], color=GLASS, lw=2.2)
    for hinge, leaf, jamb in R.get("doors", []):
        v.line(hinge[0], hinge[1], leaf[0], leaf[1], color=DARK, lw=1.0)
        r = math.hypot(leaf[0] - hinge[0], leaf[1] - hinge[1])
        a0 = math.degrees(math.atan2(-(leaf[1] - hinge[1]), leaf[0] - hinge[0]))
        a1 = math.degrees(math.atan2(-(jamb[1] - hinge[1]), jamb[0] - hinge[0]))
        d = (a1 - a0 + 540) % 360 - 180
        c.setStrokeColorRGB(*GREY); c.setLineWidth(0.35)
        pth = c.beginPath()
        for i in range(25):
            t = math.radians(a0 + d * i / 24)
            X, Y = v.p(hinge[0] + r * math.cos(t), hinge[1] - r * math.sin(t))
            (pth.moveTo if i == 0 else pth.lineTo)(X, Y)
        c.drawPath(pth, stroke=1, fill=0)
    if light:
        # ---- ΚΡΥΦΟΣ ΦΩΤΙΣΜΟΣ: κάθε γραμμή LED με τη λάμψη της και τον αριθμό της
        c.setLineCap(1); c.setLineJoin(1)
        for L in R.get("lights", []):
            _polyline(c, v, L["pts"], LED_F, 0.11 * s)
        for L in R.get("lights", []):
            _polyline(c, v, L["pts"], LED, 2.4)
        c.setLineCap(0); c.setLineJoin(0)
        for s_, (lx, ly), size in R.get("labels", []) + R.get("light_labels", []):
            v.text(lx, ly, s_.split(" 1,")[0], size=5.0, font="Inter-SemiBold", color=GREY)
        for L in R.get("lights", []):
            X, Y = v.p(*L["tag"]); X2, Y2 = v.p(*L["to"])
            c.setStrokeColorRGB(*LED); c.setLineWidth(0.7); c.line(X, Y, X2, Y2)
            c.setFillColorRGB(*LED); c.circle(X2, Y2, 1.8, stroke=0, fill=1)
            c.setFillColorRGB(1, 1, 1); c.setLineWidth(1.1); c.circle(X, Y, 9.5, stroke=1, fill=1)
            c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 8.4); c.drawCentredString(X, Y - 3.0, L["id"])
        c.restoreState()
        c.setStrokeColorRGB(0.75, 0.75, 0.78); c.setLineWidth(0.4); c.setDash([4, 3]); c.rect(ox, oy - Hp, Wp, Hp, stroke=1, fill=0); c.setDash([])
        c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 8.6)
        c.drawString(ox, oy + 17, "ΚΑΤΟΨΗ ΚΡΥΦΟΥ ΦΩΤΙΣΜΟΥ  ·  %s" % R["name"])
        c.setFont("Inter", 6.2); c.setFillColorRGB(*GREY)
        c.drawString(ox, oy + 7, "πορτοκαλί γραμμή = ταινία LED · ο αριθμός παραπέμπει στον πίνακα και στις λεπτομέρειες")
        return v
    # ---- κρυφό LED στη σκοτία της οροφής
    for pl in R.get("led", []):
        _polyline(c, v, pl, LED, 1.5, dash=[4, 2])
    # ---- καθαρές αποστάσεις (λεκάνη ↔ απέναντι)
    for kind, pos, vals in R.get("clear", []):
        if kind == "v":
            v.chain_v(vals, pos, off=0, color=RED, size=6.4, font="Inter-Bold")
        else:
            v.chain_h(vals, pos, off=0, color=RED, size=6.4, font="Inter-Bold", ext=False)
    # ---- κείμενα μέσα στην κάτοψη
    for s_, (lx, ly), rot in R.get("plan_notes2", []):
        v.text(lx, ly, s_, size=3.9, font="Inter-SemiBold", color=GREY, rot=rot)
    for f in R["fields"]:
        if f.get("slope"):
            a0, b0, a1, b1 = f["r"]
            cx, cy = f["slope"][2] if len(f["slope"]) > 2 else ((a0 + a1) / 2, (b0 + b1) / 2 + 0.12)
            X0, Y0 = v.p(cx + 0.17, cy); X1, Y1 = v.p(cx - 0.17, cy)
            c.setStrokeColorRGB(*GLASS); c.setFillColorRGB(*GLASS); c.setLineWidth(0.7)
            c.line(X0, Y0, X1, Y1)
            pth = c.beginPath(); pth.moveTo(X1 - 4, Y1); pth.lineTo(X1 + 2.5, Y1 + 2.4); pth.lineTo(X1 + 2.5, Y1 - 2.4); pth.close()
            c.drawPath(pth, stroke=0, fill=1)
            v.text(cx, cy + 0.085, f["slope"][1], size=4.8, color=GLASS, font="Inter-Medium")
    for s_, (lx, ly), size in R.get("labels", []):
        v.text(lx, ly, s_, size=size, font="Inter-SemiBold", color=GREY)
    for n in R.get("niches", []):
        if n.get("lp"):
            v.text(n["lp"][0], n["lp"][1], n["label"], size=4.8, font="Inter-SemiBold", color=DARK, bg=WHITE)
    if R.get("mosaic_label"):
        s_, (lx, ly), rot = R["mosaic_label"]
        v.text(lx, ly, s_, size=5.0, font="Inter-SemiBold", color=MOSC, rot=rot, bg=WHITE)
    for s_, (lx, ly), rot in R.get("plan_notes", []):
        v.text(lx, ly, s_, size=4.8, font="Inter-SemiBold", color=PRE, rot=rot, bg=WHITE)
    for letter, (mx, my), ang in R.get("markers", []):
        X, Y = v.p(mx, my)
        marker(c, X, Y, letter, ang, r=6.4)
    c.restoreState()
    # ---- πλαίσιο αποσπάσματος + αλυσίδες τελικών διαστάσεων
    c.setStrokeColorRGB(0.75, 0.75, 0.78); c.setLineWidth(0.4); c.setDash([4, 3]); c.rect(ox, oy - Hp, Wp, Hp, stroke=1, fill=0); c.setDash([])
    yr, xs = R["dims_x"]
    v.chain_h(xs, yr, off=(oy + 13) - v.p(0, yr)[1], ext=False)
    xr, ys = R["dims_y"]
    v.chain_v(ys, xr, off=(ox + Wp + 13) - v.p(xr, 0)[0])
    if R.get("dims_y2"):
        xr, ys = R["dims_y2"]
        v.chain_v(ys, xr, off=(ox - 13) - v.p(xr, 0)[0])
    c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 8.6)
    c.drawString(ox, oy + 45, "ΚΑΤΟΨΗ  ·  ΚΑΝΑΒΟΣ ΔΑΠΕΔΟΥ 60 × 120")
    c.setFont("Inter", 6.2); c.setFillColorRGB(*GREY)
    c.drawString(ox, oy + 36, "τελικές διαστάσεις (παρειά πλακιδίου) · οι αρμοί του δαπέδου συνεχίζουν στους τοίχους")
    return v


# ======================================================================================================== ΥΠΟΜΝΗΜΑ
def legend(c, x, y, R):
    c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 7.6); c.drawString(x, y, "ΥΠΟΜΝΗΜΑ")
    y -= 15
    st = dict(y=y)

    def sw(fill, stroke=JOINT, dash=None, lw=0.5):
        c.setFillColorRGB(*fill); c.setStrokeColorRGB(*stroke); c.setLineWidth(lw); c.setDash(dash or [])
        c.rect(x, st["y"] - 2, 20, 9, stroke=1, fill=1); c.setDash([])

    def ln(color, lw=1.6, dash=None):
        c.setStrokeColorRGB(*color); c.setLineWidth(lw); c.setDash(dash or [])
        c.line(x, st["y"] + 2.5, x + 20, st["y"] + 2.5); c.setDash([])

    rows = [
        (lambda: sw(TILE), "ολόκληρο πλακάκι 60 × 120"),
        (lambda: sw(TILE_CUT), "κομμένο κομμάτι"),
    ]
    if R.get("mosaic_line"):
        rows.append((lambda: sw(MOS, MOSC, lw=1.2), "μικρό πλακάκι (ντους, καμπύλη)"))
    if any(n for n in R.get("niches", []) if not n.get("cab")):
        rows.append((lambda: sw(NICHE_IN, DARK, lw=0.7), "εσοχή · βάθος 12 · ράφι · LED"))
    rows += [
        (lambda: sw(CAB, DARK, lw=0.7), "ντουλάπι κλειστό · βάθος 15"),
        (lambda: sw(MIRROR, DARK, lw=0.7), "καθρέπτης περασιά"),
        (lambda: sw(TILE, DARK, lw=0.9), "κτιστός πάγκος (ίδιο πλακάκι)"),
        (lambda: ln(LED), "κρυφό LED"),
        (lambda: sw(BAND, GREY), "σκοτία πάνω από το πλακάκι"),
        (lambda: sw(WHITE, HID, [2, 2]), "κρυφά: καζανάκι, στήλη"),
        (lambda: sw(GLASS, GLASS), "γυαλί ντους 0,70 × 2,10"),
        (lambda: sw(WHITE, RED, [6, 2, 1, 2], 0.6), "άξονας είδους σε αρμό"),
        (lambda: ln(RED, 0.9), "καθαρή απόσταση μπροστά στη λεκάνη"),
    ]
    if R.get("pre") or R.get("patches"):
        rows.append((lambda: sw(PRE_F, PRE, lw=0.7), "ΠΡΟΤΑΣΗ: αλλαγή τοιχοποιίας"))
    for f, s in rows:
        f()
        c.setFillColorRGB(*DARK); c.setFont("Inter", 6.4); c.drawString(x + 27, st["y"], s)
        st["y"] -= 13.2
    return st["y"]


def keybox(c, x, y, lines):
    c.setFillColorRGB(*DARK); c.setFont("Inter-Bold", 7.6); c.drawString(x, y, "ΚΑΝΑΒΟΣ")
    y -= 13
    for a, b in lines:
        c.setFont("Inter-SemiBold", 6.4); c.setFillColorRGB(*DARK); c.drawString(x, y, a)
        c.setFont("Inter", 6.4); c.drawString(x + 46, y, b)
        y -= 11.5
    return y
