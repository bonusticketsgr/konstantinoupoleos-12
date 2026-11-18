"""3D λουτρών: python3 build_3d.py  →  ΛΟΥΤΡΑ/ΛΟΥΤΡΑ_3D.html (σελίδα που περιστρέφεται) + ΛΟΥΤΡΑ/3D/*.jpg (λήψεις για τα φύλλα Λ-04 / Λ-05).

Η σελίδα φορτώνει το three.js r128 από το cdnjs· για τις λήψεις (headless Chromium μέσω playwright) χρησιμοποιείται το τοπικό
αντίγραφο vendor/three-r128.min.js και οι γραμματοσειρές Inter του έργου."""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lt_typ as T
import lt_3d as D3

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_DIR = os.path.join(ROOT, "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΛΟΥΤΡΑ")
PAGE = os.path.join(OUT_DIR, "ΛΟΥΤΡΑ_3D.html")
SHOT_DIR = os.path.join(OUT_DIR, "3D")
CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
W, H = 1110, 670
SHOTS = [dict(room=i, view=v, night=n, tags=t, name="%s_%s" % (rid, nm), w=W, h=H)
         for i, rid in enumerate(("L1", "L2"))
         for v, n, t, nm in (("dol", 0, 1, "1_apo_pano"), ("alt", 0, 1, "2_alli_plevra"), ("in", 0, 0, "3_apo_mesa"), ("dol", 1, 1, "4_kryfos_fotismos"))]


def page(three_src, local=False):
    s = open(os.path.join(HERE, "viewer_template.html"), encoding="utf-8").read()
    s = s.replace("/*__SCENE__*/", json.dumps(D3.all_scenes(), ensure_ascii=False, separators=(",", ":")))
    s = s.replace("__THREE__", three_src).replace("__REV__", T.REV)
    if local:
        fonts = os.path.join(HERE, "..", "toixopoiies", "fonts")
        face = "".join('@font-face{font-family:"Inter";font-weight:%d;src:url("file://%s")}' % (w, os.path.abspath(os.path.join(fonts, f)))
                       for w, f in ((400, "Inter-Regular.ttf"), (500, "Inter-Medium.ttf"), (600, "Inter-SemiBold.ttf")) if os.path.exists(os.path.join(fonts, f)))
        link = s[s.index('<link rel="stylesheet"'):s.index("<style>")]
        s = s.replace(link, "<style>%s</style>\n" % face)
        s = '<!doctype html><html lang="el"><head><meta charset="utf-8"><style>html,body{margin:0}[hidden]{display:none!important}</style></head><body>' + s + "</body></html>"
    return s


def main(shots=True):
    os.makedirs(SHOT_DIR, exist_ok=True)
    open(PAGE, "w", encoding="utf-8").write(page(CDN))
    print("→", PAGE, "(%d KB)" % (os.path.getsize(PAGE) // 1024))
    if not shots:
        return
    tmp = tempfile.mkdtemp(prefix="loutra3d_")
    local = os.path.join(tmp, "page.html")
    open(local, "w", encoding="utf-8").write(page("file://" + os.path.join(HERE, "vendor", "three-r128.min.js"), local=True))
    r = subprocess.run(["node", os.path.join(HERE, "shots.js"), local, SHOT_DIR, json.dumps(SHOTS)], capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip()[-2000:])
    if r.returncode:
        raise SystemExit("οι λήψεις 3D απέτυχαν")


if __name__ == "__main__":
    main(shots="--no-shots" not in sys.argv)
