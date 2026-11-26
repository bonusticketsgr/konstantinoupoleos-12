"""ΠΑΡΟΥΣΙΑΣΗ 3D – πραγματικές υφές, ουρανός και μοντέλα από τη δωρεάν βιβλιοθήκη Poly Haven (άδεια CC0 – ελεύθερη χρήση, και εμπορική).

Τα αρχεία ΔΕΝ μπαίνουν στο repo (είναι εκατοντάδες MB): κατεβαίνουν μία φορά σε φάκελο-αποθήκη ΕΞΩ από το repo και ξαναχρησιμοποιούνται.
    python3 fetch_assets.py --dest <φάκελος> [--tex 2k] [--hdri 4k] [--model 2k]
Το `assets_manifest.json` (στο repo) έχει τις ακριβείς διευθύνσεις κάθε αρχείου – φτιάχνεται με `fetch_assets.py --resolve`.
Αν λείπει ένα αρχείο, η σκηνή δουλεύει με τα παλιά, υπολογιστικά υλικά (χωρίς υφές) – δεν σταματά.
Στα αιτήματα προς τη βιβλιοθήκη δεν στέλνεται κανένα στοιχείο του έργου ή του χρήστη (μόνο ένα γενικό όνομα προγράμματος)."""
import os, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "assets_manifest.json")
UA = "archviz-render-script/1.0"
API = "https://api.polyhaven.com"
RES_ORDER = ["1k", "2k", "4k", "8k"]

CFG = dict(dir=None, tex="2k", hdri="4k", model="2k")


def configure(dir=None, tex=None, hdri=None, model=None):
    CFG["dir"] = dir or os.environ.get("PAROUSIASI_ASSETS") or os.path.join(os.path.expanduser("~"), ".cache", "parousiasi_3d")
    if tex: CFG["tex"] = tex
    if hdri: CFG["hdri"] = hdri
    if model: CFG["model"] = model
    return CFG["dir"]


def manifest():
    if not os.path.exists(MANIFEST):
        return dict(textures={}, hdris={}, models={})
    return json.load(open(MANIFEST, encoding="utf-8"))


def _root():
    if CFG["dir"] is None:
        configure()
    return CFG["dir"]


def _lower(res):
    """Η ζητούμενη ανάλυση και, αν λείπει, οι χαμηλότερες."""
    i = RES_ORDER.index(res) if res in RES_ORDER else 1
    return [RES_ORDER[j] for j in range(i, -1, -1)] + [RES_ORDER[j] for j in range(i + 1, len(RES_ORDER))]


def tex_path(aid, mp, res):
    return os.path.join(_root(), "textures", aid, "%s_%s_%s.jpg" % (aid, mp, res))


def hdri_path(aid, res):
    return os.path.join(_root(), "hdris", "%s_%s.hdr" % (aid, res))


def model_dir(aid, res):
    return os.path.join(_root(), "models", aid, res)


def texture(aid):
    """{'diff': path, 'rough': path, 'disp': path} ή None αν δεν έχει κατέβει."""
    for res in _lower(CFG["tex"]):
        d = tex_path(aid, "diff", res)
        if os.path.exists(d):
            out = dict(diff=d, res=res)
            for mp in ("rough", "nor", "disp"):
                p = tex_path(aid, mp, res)
                if os.path.exists(p):
                    out[mp] = p
            return out
    return None


def hdri(aid):
    for res in _lower(CFG["hdri"]):
        p = hdri_path(aid, res)
        if os.path.exists(p):
            return p
    return None


def model(aid):
    """Διαδρομή του .blend του μοντέλου ή None."""
    for res in _lower(CFG["model"]):
        d = model_dir(aid, res)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".blend"):
                    return os.path.join(d, f)
    return None


# ---------------------------------------------------------------- κατέβασμα

def _get(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    if shutil.which("curl"):
        r = subprocess.run(["curl", "-sS", "-L", "--fail", "--retry", "3", "-A", UA, "-o", tmp, url], capture_output=True, text=True)
        ok = r.returncode == 0
    else:
        import urllib.request
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            ok = True
        except Exception:
            ok = False
    if ok and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
        os.replace(tmp, dest)
        return True
    if os.path.exists(tmp):
        os.remove(tmp)
    return False


def _api(path):
    r = subprocess.run(["curl", "-sS", "--fail", "-A", UA, API + path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("API: " + path + " " + r.stderr[:200])
    return json.loads(r.stdout)


def resolve(textures=(), hdris=(), models=(), res=("1k", "2k", "4k"), hres=("1k", "2k", "4k", "8k"), mres=("1k", "2k")):
    """Ρωτά τη βιβλιοθήκη για τις διευθύνσεις των αρχείων και ενημερώνει το manifest (τρέχει μία φορά, όταν αλλάζει η λίστα)."""
    M = manifest()
    for aid in textures:
        f = _api("/files/" + aid)
        dk = "Diffuse" if "Diffuse" in f else next(k for k in f if "diff" in k.lower() or k.lower().startswith("col"))
        rk = "Rough" if "Rough" in f else next((k for k in f if "rough" in k.lower()), None)
        hk = "Displacement" if "Displacement" in f else next((k for k in f if "disp" in k.lower()), None)
        e = {}
        for r in res:
            e[r] = {}
            for mp, k in (("diff", dk), ("rough", rk), ("disp", hk)):
                if k and r in f[k] and "jpg" in f[k][r]:
                    e[r][mp] = dict(url=f[k][r]["jpg"]["url"], size=f[k][r]["jpg"]["size"])
        M["textures"][aid] = e
    for aid in hdris:
        f = _api("/files/" + aid)
        M["hdris"][aid] = {r: dict(url=f["hdri"][r]["hdr"]["url"], size=f["hdri"][r]["hdr"]["size"]) for r in hres if r in f["hdri"]}
    for aid in models:
        f = _api("/files/" + aid)
        e = {}
        for r in mres:
            if r not in f.get("blend", {}):
                continue
            b = f["blend"][r]["blend"]
            e[r] = dict(url=b["url"], size=b["size"], include={k: dict(url=v["url"], size=v["size"]) for k, v in b.get("include", {}).items()})
        M["models"][aid] = e
    json.dump(M, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    return M


def jobs(tex=None, hdri_res=None, model_res=None, only=None):
    """Λίστα (url, dest, size) για ό,τι λείπει από την αποθήκη."""
    M = manifest()
    tex = tex or CFG["tex"]; hdri_res = hdri_res or CFG["hdri"]; model_res = model_res or CFG["model"]
    out = []
    for aid, e in M["textures"].items():
        if only and aid not in only: continue
        r = next((x for x in _lower(tex) if x in e), None)
        if r:
            for mp, v in e[r].items():
                out.append((v["url"], tex_path(aid, mp, r), v["size"]))
    for aid, e in M["hdris"].items():
        if only and aid not in only: continue
        r = next((x for x in _lower(hdri_res) if x in e), None)
        if r:
            out.append((e[r]["url"], hdri_path(aid, r), e[r]["size"]))
    for aid, e in M["models"].items():
        if only and aid not in only: continue
        r = next((x for x in _lower(model_res) if x in e), None)
        if r:
            d = model_dir(aid, r)
            out.append((e[r]["url"], os.path.join(d, os.path.basename(e[r]["url"])), e[r]["size"]))
            for k, v in e[r]["include"].items():
                out.append((v["url"], os.path.join(d, k), v["size"]))
    return [j for j in out if not (os.path.exists(j[1]) and os.path.getsize(j[1]) == j[2])]


def fetch(tex=None, hdri_res=None, model_res=None, only=None, workers=8, log=print):
    from concurrent.futures import ThreadPoolExecutor
    J = jobs(tex, hdri_res, model_res, only)
    tot = sum(j[2] for j in J)
    log("αποθήκη: %s · %d αρχεία προς λήψη, %.0f MB" % (_root(), len(J), tot / 1e6))
    bad = []
    with ThreadPoolExecutor(workers) as ex:
        for j, ok in zip(J, ex.map(lambda j: _get(j[0], j[1]), J)):
            if not ok:
                bad.append(j[0])
    log("έτοιμο · αποτυχίες: %d" % len(bad))
    for b in bad:
        log("  ΔΕΝ κατέβηκε: " + b)
    return bad
