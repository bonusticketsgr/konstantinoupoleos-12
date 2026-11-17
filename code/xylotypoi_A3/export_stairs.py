"""Εξάγει τη γεωμετρία των ΤΕΛΙΚΩΝ σκαλών (μοντέλα stair_s2 / stair_s3 / stair_s7) σε code/toixopoiies/data/stairs.json,
ώστε οι κατόψεις τοιχοποιιών (και τα υπόβαθρα ανόψεων / αποχετεύσεων) να δείχνουν ΑΚΡΙΒΩΣ τις σκάλες του τεύχους σκαλών
και όχι τη σχηματική σκάλα των 16 ριχτιών της μελέτης.

    python3 export_stairs.py            → γράφει το stairs.json
    python3 export_stairs.py --check    → συγκρίνει με το υπάρχον αρχείο (κωδικός 1 αν διαφέρει: τρέξε ξανά και ξαναχτίσε τα τεύχη)

Κλειδιά: S2 υπόγειο → ισόγειο (Σ2α) · S3 ισόγειο → Α΄ (Σ3β) · S4 τυπικός όροφος → επόμενος (Σ4β = Σ5β = Σ6β) · S7 Δ΄ → σοφίτα (Σ7β).
Ρίχτια: {αριθμός: [[x, y] στο φανάρι, [x, y] στον τοίχο / δοκό]} σε m του κοινού συστήματος."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "toixopoiies", "data", "stairs.json")

SNIP = r'''
import json, sys
import %(mod)s as M
well = [M.%(wx0)s, M.W0, M.WX, M.W1]
walk = getattr(M, "WALK", None) or (M._walk_pts() if hasattr(M, "_walk_pts") else M.walk_path())
pts = [[round(x, 4), round(y, 4)] for x, y in walk.coords]
# αραίωση της γραμμής ανάβασης (τόξα): κάθε 5ο σημείο + άκρα
walk_pts = [pts[0]] + pts[1:-1:5] + [pts[-1]]
d = dict(sheet=%(sheet)r, rev=M.REV, n=M.N, rise=round(M.RISE, 5), going=round(M.G, 5),
         ffl=[round(M.FFL0, 3), round(M.FFL1, 3)], well=[round(v, 4) for v in well], walk=walk_pts,
         risers={str(k): [[round(a[0], 4), round(a[1], 4)], [round(b[0], 4), round(b[1], 4)]] for k, (a, b) in sorted(M.RISERS.items())})
for nm in ("WALL_X", "WALL1_X", "DOOR_Y", "YN", "YS", "XE"):        # τι θεωρεί το φύλλο της σκάλας για τους γύρω τοίχους (έλεγχος με τις τοιχοποιίες)
    if hasattr(M, nm):
        v_ = getattr(M, nm); d[nm.lower()] = list(v_) if isinstance(v_, tuple) else v_
print(json.dumps(d, ensure_ascii=False))
'''
JOBS = [("S2", "stair_s2", "XL", "Σ2α", None), ("S3", "stair_s3", "XL", "Σ3β", "gf"),
        ("S4", "stair_s3", "XL", "Σ4β / Σ5β / Σ6β", "a"), ("S7", "stair_s7", "WXA", "Σ7β", None)]


def collect():
    out = {}
    for key, mod, wx0, sheet, floor in JOBS:
        env = dict(os.environ)
        env.pop("STAIR_FLOOR", None)
        if floor and floor != "gf":
            env["STAIR_FLOOR"] = floor
        r = subprocess.run([sys.executable, "-c", SNIP % dict(mod=mod, wx0=wx0, sheet=sheet)], cwd=HERE, env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit("export %s: %s" % (key, r.stderr[-800:]))
        out[key] = json.loads(r.stdout.strip().splitlines()[-1])
    return out


if __name__ == "__main__":
    data = collect()
    txt = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True)
    if "--check" in sys.argv:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        same = old.strip() == txt.strip()
        print("stairs.json:", "ΕΝΗΜΕΡΟ" if same else "ΔΙΑΦΕΡΕΙ από τα μοντέλα σκαλών – τρέξε export_stairs.py και ξαναχτίσε τοίχους / ανόψεις / αποχετεύσεις")
        sys.exit(0 if same else 1)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
    for k, d in data.items():
        print("%s %-18s %s · %d ρίχτια × %.2f cm · πάτημα %.1f cm · %+.2f → %+.2f" % (k, d["sheet"], d["rev"], d["n"], d["rise"] * 100, d["going"] * 100, d["ffl"][0], d["ffl"][1]))
    print("OK", os.path.abspath(OUT))
