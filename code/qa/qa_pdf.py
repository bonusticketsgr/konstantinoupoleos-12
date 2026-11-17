"""Τελικός έλεγχος παραδοτέων PDF (ανεξάρτητος από τα μοντέλα – διαβάζει το ίδιο το PDF που θα τυπωθεί):
  (α) κείμενα που πέφτουν το ένα πάνω στο άλλο (δυσανάγνωστα),
  (β) κείμενα έξω από τη σελίδα ή πάνω στο περιθώριο εκτύπωσης,
  (γ) μέγεθος / προσανατολισμός σελίδων και ενσωματωμένες γραμματοσειρές.
Χρήση:  python3 qa_pdf.py <pdf> [<pdf> …] [--png <φάκελος>] [--min 0.25]
  --png: σώζει μεγέθυνση κάθε ευρήματος (για να κοιταχτεί)· --min: ελάχιστο ποσοστό επικάλυψης του μικρότερου κειμένου·
  --hidden: τυπώνει και τα κείμενα που υπάρχουν στο PDF αλλά ΔΕΝ φαίνονται (κομμένα από παράθυρο λεπτομέρειας ή σκεπασμένα από άλλο στοιχείο).
Επιστρέφει κωδικό 1 αν υπάρχει εύρημα (β). Τα (α) είναι για ΟΠΤΙΚΟ έλεγχο: δύο κείμενα μπορεί να ακουμπούν χωρίς να κρύβονται.
"""
import os, sys
import numpy as np
import pymupdf

MARGIN_MM = 4.0          # τίποτα πιο κοντά από τόσο στην άκρη του χαρτιού
PT = 72 / 25.4


ZOOM = 3.0


def _visible(img, bbox, color):
    """Φαίνεται το κείμενο στη σελίδα; (όχι κομμένο από παράθυρο λεπτομέρειας / σκεπασμένο): υπάρχουν στο ορθογώνιό του
    εικονοστοιχεία στο χρώμα του κειμένου."""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = [int(round(v * ZOOM)) for v in bbox]
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(w, x1 + 1), min(h, y1 + 1)
    if x1 <= x0 or y1 <= y0:
        return False
    reg = img[y0:y1, x0:x1, :3].astype(np.int32)
    col = np.array([(color >> 16) & 255, (color >> 8) & 255, color & 255], dtype=np.int32)
    if col.min() >= 235:        # λευκά γράμματα (πάνω σε χρωματιστή ετικέτα): φαίνονται μόνο αν υπάρχει το χρωματιστό φόντο τους
        return bool((np.abs(reg - 255).max(axis=2) > 40).mean() >= 0.30)
    ink = np.abs(reg - col).max(axis=2) <= 70
    # γράμματα = μελάνι σκορπισμένο σε όλο το ορθογώνιο· μια γραμμή πλαισίου / διάστασης που το διασχίζει πιάνει λίγες στήλες ή γραμμές
    return bool(ink.any(axis=0).mean() >= 0.45 and ink.any(axis=1).mean() >= 0.45)


HIDDEN = []            # (σελίδα, κείμενο, bbox) – κείμενα που υπάρχουν στο PDF αλλά δεν φαίνονται (κομμένα από παράθυρο ή ΣΚΕΠΑΣΜΕΝΑ)


def lines_of(page):
    out = []
    pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    d = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            if not txt:
                continue
            x0, y0, x1, y1 = ln["bbox"]
            if not _visible(img, ln["bbox"], ln["spans"][0]["color"]):
                HIDDEN.append((page.number + 1, txt, tuple(round(v_, 1) for v_ in ln["bbox"])))
                continue                    # κείμενο εκτός παραθύρου (clip) ή σκεπασμένο – δεν τυπώνεται
            dx, dy = ln["dir"]
            size = max(s["size"] for s in ln["spans"])
            vert = abs(dy) > abs(dx)
            # «σώμα» του κειμένου: χωρίς τα κενά πάνω / κάτω από τα γράμματα
            if vert:
                w = x1 - x0; core = (x0 + 0.22 * w, y0, x1 - 0.22 * w, y1)
            else:
                h = y1 - y0; core = (x0, y0 + 0.22 * h, x1, y1 - 0.22 * h)
            out.append(dict(txt=txt, bbox=(x0, y0, x1, y1), core=core, size=size, vert=vert, diag=min(abs(dx), abs(dy)) > 0.2,
                            img=img, color=ln["spans"][0]["color"]))
    return out


def area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def inter(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def check(path, min_ov=0.25, png=None):
    doc = pymupdf.open(path)
    name = os.path.basename(path)
    finds, hard = [], 0
    sizes = {}
    for pno, page in enumerate(doc, 1):
        R = page.rect
        key = "%d×%d mm" % (round(R.width / PT), round(R.height / PT))
        sizes[key] = sizes.get(key, 0) + 1
        L = lines_of(page)
        m = MARGIN_MM * PT
        for a in L:
            x0, y0, x1, y1 = a["bbox"]
            if x0 < m - 0.5 or y0 < m - 0.5 or x1 > R.width - m + 0.5 or y1 > R.height - m + 0.5:
                # το κομμάτι του κειμένου που πέφτει στο περιθώριο πρέπει να ΦΑΙΝΕΤΑΙ εκεί (όχι κομμένο από παράθυρο)
                bands = [(x0, y0, min(x1, m), y1), (max(x0, R.width - m), y0, x1, y1), (x0, y0, x1, min(y1, m)), (x0, max(y0, R.height - m), x1, y1)]
                if any(b_[2] - b_[0] > 1 and b_[3] - b_[1] > 1 and _visible(a["img"], b_, a["color"]) for b_ in bands):
                    finds.append((pno, "ΕΚΤΟΣ", 1.0, a["txt"], "", a["bbox"])); hard += 1
        for i in range(len(L)):
            a = L[i]
            if a["diag"]:
                continue
            for j in range(i + 1, len(L)):
                b = L[j]
                if b["diag"]:
                    continue
                r = inter(a["core"], b["core"])
                ar = area(r)
                if ar <= 0:
                    continue
                ov = ar / max(1e-9, min(area(a["core"]), area(b["core"])))
                big = ar >= 1.2 * min(a["size"], b["size"]) ** 2      # μεγάλη επικάλυψη σε απόλυτο μέγεθος (μακρύ κείμενο που μπαίνει σε άλλο)
                if ov < min_ov and not big:
                    continue
                if a["txt"] == b["txt"] and area(inter(a["bbox"], b["bbox"])) > 0.9 * area(a["bbox"]):
                    continue                # το ίδιο κείμενο γραμμένο δύο φορές στο ίδιο σημείο
                u = (min(a["bbox"][0], b["bbox"][0]), min(a["bbox"][1], b["bbox"][1]), max(a["bbox"][2], b["bbox"][2]), max(a["bbox"][3], b["bbox"][3]))
                finds.append((pno, "ΕΠΙΚΑΛΥΨΗ", ov, a["txt"], b["txt"], u))
    fonts = set()
    for pno in range(len(doc)):
        for f in doc.get_page_fonts(pno):
            fonts.add((f[3], f[2], bool(f[1])))        # (όνομα, τύπος, ενσωματωμένη = έχει επέκταση αρχείου)
    not_emb = sorted(n for n, t, e in fonts if not e)
    print("%s · %d σελίδες · %s · γραμματοσειρές %d%s" % (name, len(doc), ", ".join("%s ×%d" % kv for kv in sizes.items()), len(fonts),
                                                         (" · ΜΗ ΕΝΣΩΜΑΤΩΜΕΝΕΣ: " + ", ".join(not_emb)) if not_emb else " (όλες ενσωματωμένες)"))
    finds.sort(key=lambda f: (f[0], -f[2]))
    for k, (pno, kind, ov, ta, tb, u) in enumerate(finds, 1):
        print("  σελ. %2d %-10s %3d%%  «%s»%s" % (pno, kind, round(ov * 100), ta[:60], ("  ×  «%s»" % tb[:60]) if tb else ""))
        if png:
            os.makedirs(png, exist_ok=True)
            page = doc[pno - 1]
            pad = 40
            clip = pymupdf.Rect(u[0] - pad, u[1] - pad, u[2] + pad, u[3] + pad) & page.rect
            pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=clip)
            pix.save(os.path.join(png, "%s_p%02d_%03d.png" % (os.path.splitext(name)[0][:28], pno, k)))
    print("  → επικαλύψεις κειμένων: %d · εκτός περιθωρίου: %d" % (sum(1 for f in finds if f[1] == "ΕΠΙΚΑΛΥΨΗ"), hard))
    if SHOW_HIDDEN:
        for pno, txt, bb in HIDDEN:
            print("  σελ. %2d ΑΦΑΝΕΣ      «%s»  %s" % (pno, txt[:70], bb))
    del HIDDEN[:]
    return finds, hard


SHOW_HIDDEN = False

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--hidden" in args:          # λίστα και των κειμένων που δεν φαίνονται (σε φύλλα χωρίς παράθυρα λεπτομερειών = σκεπασμένες ετικέτες)
        args.remove("--hidden"); SHOW_HIDDEN = True
    png = None; min_ov = 0.25
    if "--png" in args:
        i = args.index("--png"); png = args[i + 1]; del args[i:i + 2]
    if "--min" in args:
        i = args.index("--min"); min_ov = float(args[i + 1]); del args[i:i + 2]
    bad = 0
    for p in args:
        _, h = check(p, min_ov, os.path.join(png, os.path.splitext(os.path.basename(p))[0][:24]) if png else None)
        bad += h
    sys.exit(1 if bad else 0)
