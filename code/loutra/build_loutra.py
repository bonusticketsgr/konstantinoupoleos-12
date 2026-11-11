"""Τεύχος λουτρών τυπικού ορόφου: python3 build_loutra.py  →  ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ/ΛΟΥΤΡΑ/…pdf + έλεγχος κομματιών."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "toixopoiies"))
import lt_typ as T
import lt_sheets as S
from lt_draw import new_canvas, frame_and_title, north_arrow, fm, PAGE_W, PAGE_H, DARK, GREY
import b1_model as M

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_DIR = os.path.join(ROOT, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΛΟΥΤΡΑ")
NOTES_DIR = os.path.join(ROOT, "λουτρά")
OUT = os.path.join(OUT_DIR, "ΛΟΥΤΡΑ_ΤΥΠΙΚΟΥ_ΟΡΟΦΟΥ_ΟΨΕΙΣ_ΠΛΑΚΑΚΙΑ_%s.pdf" % T.REV)
BASE = "Τοιχοποιίες Β1 R26 / Δ΄ R05 · ανόψεις R16 · αποχετεύσεις R22"

# θέσεις στο φύλλο: κάτοψη (ox, oy = πάνω αριστερά) · όψεις (ox, oy = αριστερό άκρο στη στάθμη δαπέδου) · υπόμνημα
LAYOUT = {
    "Λ1": dict(plan=(82, 760), elev={"Α": (455, 497), "Δ": (698, 497), "Γ": (455, 142), "Β": (698, 142)},
               legend=(1022, 800), key=(1022, 610), north=(398, 790)),
    "Λ2": dict(plan=(82, 760), elev={"Α": (588, 497), "Γ": (112, 142), "Δ": (548, 142), "Β": (835, 142)},
               legend=(1000, 800), key=(1000, 600), north=(546, 790)),
}
KEY = [("Πλακάκι", "60 × 120 όρθιο"), ("Αρμός", "2 mm · βήμα 0,60 / 1,20"),
       ("Ύψος", "2 ολόκληρα ως το +2,40"), ("Οροφή", "+2,40 έως +2,50"),
       ("Δάπεδο", "αρμοί = αρμοί τοίχων"), ("Γωνίες", "φάλτσο 45°"), ("Πάγκος", "κτιστός +0,75")]


def sheet(c, R):
    L = LAYOUT[R["id"]]
    S.draw_plan(c, R, M, *L["plan"])
    by = {e["id"]: e for e in R["elevs"]}
    for k, (ox, oy) in L["elev"].items():
        S.draw_elev(c, by[k], ox, oy)
    S.legend(c, L["legend"][0], L["legend"][1], R)
    S.keybox(c, *L["key"], KEY)
    north_arrow(c, *L["north"], r=9)
    frame_and_title(c, R["sheet"], "%s – ΟΨΕΙΣ · ΕΣΟΧΕΣ · ΠΛΑΚΑΚΙΑ" % R["name"],
                    "Α΄ · Β΄ · Γ΄ · Δ΄ όροφος · " + R["sub_short"],
                    "πλακάκι 60 × 120 ως +2,40 · σκοτία ως την οροφή · ΠΡΟΤΑΣΗ προς έγκριση",
                    BASE, "ΚΛΙΜΑΚΑ 1:25 · A3", T.REV, T.DATE)
    c.showPage()


# ------------------------------------------------------------------------------------------------ έλεγχος
def check(R, out):
    bad = 0
    out.append("=" * 100)
    out.append("%s  %s – %s" % (R["sheet"], R["name"], R["sub"]))
    tot_whole = tot_cut = 0; area = 0.0; mos = 0.0
    WX, WY = set(), set()
    for E in R["elevs"]:
        ps = S.pieces(E)
        ax, o, sg = E["map"]
        for u in E.get("jv", []):
            (WX if ax == "x" else WY).add(round(o + sg * u, 3))
        whole = sum(1 for p in ps if p["whole"]); cut = len(ps) - whole
        tot_whole += whole; tot_cut += cut; area += sum(p["area"] for p in ps); mos += S.mosaic_area(E)
        out.append("  ΟΨΗ %s  %-46s μήκος %s · %d ολόκληρα · %d κομμένα / με εγκοπή%s" % (
            E["id"], E["title"][:46], fm(E["w"]), whole, cut, " · μικρό πλακάκι %.1f m²" % S.mosaic_area(E) if E.get("mosaic") else ""))
        us, _ = S.cells(E)
        out.append("        πλάτη: " + " | ".join("μικρό πλακάκι %s" % fm(b - a) if S.in_mosaic(E, (a + b) / 2) else fm(b - a) for a, b in zip(us[:-1], us[1:])))
        sp = E.get("special", {})
        for p in ps:
            key = next((k for k in sp if abs(k[0] - p["u0"]) < 2e-3 and abs(k[1] - p["u1"]) < 2e-3), None)
            if p["minleg"] < 0.20 - 1e-6:
                tag = "ΕΙΔΙΚΟ (%s)" % sp[key] if key else ("ΕΓΚΟΠΗ" if p["notched"] and p["minleg"] >= 0.10 - 1e-6 else "ΣΤΕΝΟ < 20 cm")
                if tag.startswith("ΣΤΕΝΟ"): bad += 1
                out.append("        %s–%s × %s–%s: στενότερο σημείο %s → %s" % (fm(p["u0"]), fm(p["u1"]), fm(p["z0"]), fm(p["z1"]), fm(p["minleg"]), tag))
        for it in E.get("items", []):
            if it[0] in ("wc_front", "mixer", "tap"):
                u = it[1]; on = any(abs(u - j) < 2e-3 for j in E.get("jv", []))
                mid = any(abs(u - (a + b) / 2) < 2e-3 for a, b in zip(us[:-1], us[1:]))
                out.append("        άξονας %-9s u = %s → %s" % (it[0], fm(u), "σε αρμό" if on else ("στο κέντρο πλακιδίου" if mid else "ελεύθερη θέση")))
    out.append("  ΔΑΠΕΔΟ")
    FX, FY = set(), set()
    for f in R["fields"]:
        a0, b0, a1, b1 = f["r"]
        xs = sorted(set([a0, a1] + list(f["xc"]))); ys = sorted(set([b0, b1] + list(f["yc"])))
        FX |= set(round(x, 3) for x in f["xc"]); FY |= set(round(y, 3) for y in f["yc"])
        dims = ["%s × %s" % (fm(xb - xa), fm(yb - ya)) for ya, yb in zip(ys[:-1], ys[1:]) for xa, xb in zip(xs[:-1], xs[1:])]
        out.append("        %-8s %s" % (f.get("name", "κυρίως"), " | ".join(dims)))
        for xa, xb in zip(xs[:-1], xs[1:]):
            for ya, yb in zip(ys[:-1], ys[1:]):
                if min(xb - xa, yb - ya) < 0.20 - 1e-6:
                    bad += 1; out.append("        ΣΤΕΝΟ κομμάτι δαπέδου %s × %s" % (fm(xb - xa), fm(yb - ya)))
    pts = R["floor"]; n = len(pts)
    farea = abs(sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))) / 2
    fx = sorted(x for x in FX if not any(abs(x - w) < 3e-3 for w in WX))
    fy = sorted(y for y in FY if not any(abs(y - w) < 3e-3 for w in WY))
    out.append("        αρμοί δαπέδου που ΔΕΝ συνεχίζουν σε τοίχο 60 × 120: x %s · y %s" % ([fm(x) for x in fx] or "κανένας", [fm(y) for y in fy] or "κανένας"))
    out.append("  ΣΥΝΟΛΟ τοίχων: %d ολόκληρα · %d κομμένα / με εγκοπή · πλακάκι 60 × 120 τοίχων %.1f m²%s · δαπέδου %.1f m² (καθαρά, χωρίς φύρα)" % (
        tot_whole, tot_cut, area, " · μικρό πλακάκι %.1f m²" % mos if mos else "", farea))
    return bad


def main():
    os.makedirs(OUT_DIR, exist_ok=True); os.makedirs(NOTES_DIR, exist_ok=True)
    c = new_canvas(OUT, "Λουτρά τυπικού ορόφου – όψεις, εσοχές, πλακάκια %s" % T.REV)
    out = ["ΕΛΕΓΧΟΣ ΚΟΜΜΑΤΙΩΝ – λουτρά τυπικού ορόφου %s (%s) · πλακάκι 60 × 120 · κανόνας: κανένα κομμάτι κάτω από 20 cm" % (T.REV, T.DATE)]
    bad = 0
    for R in T.ROOMS:
        sheet(c, R)
        bad += check(R, out)
    c.save()
    out.append("=" * 100)
    out.append("ΣΤΕΝΑ ΚΟΜΜΑΤΙΑ (< 20 cm, εκτός ειδικών): %d" % bad)
    txt = "\n".join(out)
    open(os.path.join(NOTES_DIR, "Έλεγχος_κομματιών_%s.txt" % T.REV), "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    print("→", OUT)


if __name__ == "__main__":
    main()
