"""Οπές πλακών και shaft Η/Μ: οι ξυλότυποι εργοταξίου (xylotypoi_A3/holes_apox.py = ΑΝΤΙΓΡΑΦΟ) πρέπει να έχουν ΑΚΡΙΒΩΣ τις οπές του τρέχοντος
τεύχους αποχετεύσεων (apoxeteuseis/apox_rNN.py – το νεότερο). Συγκρίνεται ο πηγαίος κώδικας (ast), χωρίς να τρέξει το build των αποχετεύσεων:
κάθε γραμμή H(id, πλάκες, όνομα, σωλήνας, σημείο, κουτί, παρειά x, παρειά y) του πίνακα HOLES, οι σταθερές θέσεων (AP1 … RD … ROOF_G) και το SHAFT.

    python3 qa_holes.py        → «Σύνολο … · ΛΑΘΟΣ 0» αν ταυτίζονται"""
import ast, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "xylotypoi_A3", "holes_apox.py")
cands = sorted(glob.glob(os.path.join(HERE, "..", "apoxeteuseis", "apox_r[0-9]*.py")), key=lambda p: int(re.search(r"apox_r(\d+)", p).group(1)))
B = cands[-1]
CONST = ("AP1", "AP3", "AP1G", "AP3G", "AP2", "AP4", "AP4G", "RD", "ROOF_G", "S37", "SHAFT", "SHAFT_SLABS", "PIPE_OD")


def load(path):
    tree = ast.parse(open(path, encoding="utf-8").read()); env = {}; holes = None
    for node in tree.body:
        if not isinstance(node, ast.Assign): continue
        for tg, val in zip(*[(node.targets[0].elts, node.value.elts) if isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple) else ([node.targets[0]], [node.value])][0]):
            if not isinstance(tg, ast.Name): continue
            if tg.id == "HOLES": holes = val
            elif tg.id in CONST:
                try: env[tg.id] = eval(compile(ast.Expression(val), path, "eval"), {}, dict(env))
                except Exception as e: env[tg.id] = "?? %s" % e
    rows = {}
    for call in holes.elts:
        a = [eval(compile(ast.Expression(x), path, "eval"), {}, dict(env)) for x in call.args[:8]]
        rows[a[0]] = dict(slabs=tuple(a[1]), name=a[2], pipe=a[3], pt=tuple(round(v, 4) for v in a[4]), box=tuple(round(v, 4) for v in a[5]), rx=(round(a[6][0], 4), a[6][1]), ry=(round(a[7][0], 4), a[7][1]))
    return env, rows


def main():
    ea, ra = load(A); eb, rb = load(B); n = 0; bad = []
    print("ξυλότυποι: %s  ↔  αποχετεύσεις: %s" % (os.path.basename(A), os.path.basename(B)))
    for k in sorted(set(ra) | set(rb)):
        n += 1
        if ra.get(k) != rb.get(k): bad.append("Η%s: ξυλότυποι %s ≠ αποχετεύσεις %s" % (k, ra.get(k), rb.get(k)))
    for c in ("SHAFT", "SHAFT_SLABS", "PIPE_OD", "ROOF_G"):
        n += 1
        if ea.get(c) != eb.get(c): bad.append("%s: ξυλότυποι %s ≠ αποχετεύσεις %s" % (c, ea.get(c), eb.get(c)))
    for k, v in (ea.get("RD") or {}).items():
        n += 1
        if (eb.get("RD") or {}).get(k) != v: bad.append("RD[%s]: ξυλότυποι %s ≠ αποχετεύσεις %s" % (k, v, (eb.get("RD") or {}).get(k)))
    for b_ in bad: print("ΛΑΘΟΣ  " + b_)
    print("οπές Η1–Η%d · shaft %s στους %s" % (max(ra), ea.get("SHAFT"), ", ".join(ea.get("SHAFT_SLABS") or ())))
    print("Σύνολο %d έλεγχοι · ΛΑΘΟΣ %d" % (n, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
