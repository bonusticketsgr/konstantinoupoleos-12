# Σ1 / Σ2 / Σ3 – Γεωμετρικά διαστασιολογημένα σχέδια 1:75 (χωρίς οπλισμούς) – γενικευμένο pipeline

Παραδοτέα (21/09/2026, όλα Α3 1:75, PDF + PNG 200 dpi):
- `Σ3_Οροφή_ισογείου_+3.65_ΓΕΩΜΕΤΡΙΑ_1-75_A3.pdf` (από το build.py του Σ3, βλ. έγγραφο «Σ3_γεωμετρία_1-80_pipeline»)
- `Σ2_Οροφή_υπογείου_+0.05_ΓΕΩΜΕΤΡΙΑ_1-75_A3.pdf`
- `Σ1_Θεμελίωση_-4.00_ΓΕΩΜΕΤΡΙΑ_1-75_A3.pdf` (2 σελίδες: κύρια κάτοψη θεμελίωσης -4,00/-3,60 και θεμελίωση υποσταθμού -6,69)

Πηγές: τα εγκεκριμένα σχέδια Fespa (1:50, 56.6929 pt/m). Κανόνας: καμία επινοημένη διάσταση — όλες οι τιμές προκύπτουν από τη διανυσματική γεωμετρία του PDF ή είναι οι αναγραφόμενες του μελετητή.

## Μέθοδος (κοινή για Σ1/Σ2)
1. `texts_dump.py` → `texts.json` (ομαδοποίηση spans σε ετικέτες, με κατεύθυνση/γραμματοσειρά/χρώμα).
2. `extract.py <pdf> geometry.json --region x0 y0 x1 y1 [--keep rects] [--stair rects]` → υποστυλώματα (κλειστοί βρόχοι 1.7), γραμμές 0.85 (χωρίς τις διακεκομμένες οπλισμού), κρυφές γραμμές 0.57, διαγραμμίσεις/διαγώνιοι 0.28, κύκλοι πλακών, μπλε φυτευτά. Τα keep-rects κρατούν λεπτές συμπαγείς γραμμές 0.57 που είναι γεωμετρία (π.χ. μπλοκ Χ στον τοίχο, αγκύλη έκτασης τοιχείου).
3. `recover_dims.py` → `dims.json`: ανάκτηση των διαστάσεων του μελετητή (γραμμή 0.28 + βέλη + πλάγια τιμή). Στο Σ1 οι διαστάσεις μήκους ράβδων οπλισμού (άκρα σε ράβδους, όχι σε δομικές γραμμές) αναγνωρίστηκαν και παραλείφθηκαν (SKIP_DIMS). Snapping άκρων σε δομικές γραμμές (±4 pt) όταν το μήκος συμφωνεί με την τιμή.
4. `lib.py` (κλάση Sheet): μετασχηματισμός 1:50→1:75, σχεδίαση γεωμετρίας, αλυσίδες διαστάσεων (hchain/vchain με λοξά ticks, staggering, περιστρεφόμενο/πλευρικό κείμενο σε στενά τμήματα), ετικέτες, κύκλοι πλακών, σύμβολα στάθμης, σημειώσεις (με προαιρετική λευκή μάσκα), κατακόρυφη πινακίδα δεξιά με κλίμακα, αυτόματος έλεγχος επικαλύψεων (κείμενο/κείμενο, κείμενο/δομική γραμμή ≥0.85, κείμενο/υποστύλωμα). `fmt`: 2 δεκαδικά, 3 μόνο σε ακριβώς μισό εκατοστό.
5. `auto.py`: ανάγνωση ετικετών (Κ, Δ, Ε.Ζ., Π, h=, στάθμες), καθαρό μήκος δοκών με ray casting από την ετικέτα (bracketing από παράλληλες γραμμές 0.85, εμπόδια = πολύγωνα υποστυλωμάτων + συγχωνευμένες συγγραμμικές γραμμές 0.85), leaders.
6. `sheet_s2.py`, `sheet_s1.py`, `sheet_s1_sub.py`: ορισμός αλυσίδων (παρειές/άξονες/συνολικά, 3 σειρές ανά πλευρά, ROW 6.5 mm), θέσεις ετικετών, εσωτερικές διαστάσεις μελετητή, σημειώσεις, πινακίδα. Παράμετροι περιβάλλοντος: OX_MM, OY_MM (κεντράρισμα), OUT, TITLE_X.
7. Έλεγχοι: επικαλύψεις 0/0 σε όλα τα φύλλα· κάθε περιμετρική τιμή του μελετητή (Σ2: 22.10/6.02/5.55/3.05/7.47, 17.03/4.58/4.10/2.70/2.05/2.75/0.85, 10.91/6.61/2.70/1.33/2.58/4.30, 18.32/4.60/5.80/4.15/3.77, 3.65 — Σ1: 22.10/6.02/5.55/3.05/7.47, 17.03/4.58/3.25/0.85/2.70/2.05/2.75/0.85, 10.91/6.61/4.30/5.70, 18.32/4.60/6.30/3.40/4.02/0.81, 3.65/0.30, υποσταθμός 9.20/0.85/2.35/0.35/2.05/2.75/0.85/3.89/4.02) επαληθεύτηκε ως άθροισμα διαδοχικών τμημάτων των αλυσίδων· κλίμακα επαληθευμένη (22.10 m = 294.6 mm).

## Παρατηρήσεις ανά σχέδιο
- Σ2: Οι φυτευτές δοκοί/τοιχία (μπλε) κρατήθηκαν. Δύο ετικέτες Κ32 και δύο Κ25 υπάρχουν στο Σ2 (δύο διαφορετικά στοιχεία το καθένα — όπως στο πρωτότυπο). Οι τομές 1-1/2-2 και οι πίνακες οπλισμών δεν μεταφέρθηκαν. Κ20 (30/45/25/50) ήταν χωρισμένο σε δύο spans στο PDF — προστέθηκε χειροκίνητα.
- Σ1: Κοιτόστρωση (h=80 στη ζώνη πυρήνα, h=40 αλλού, όπως στο Σ1)· η ζώνη h=80 δίνεται με τις μετρήσεις 0.50/0.30/0.80 από τις παρειές των υποστυλωμάτων (τιμές μελετητή). Η κοιτόστρωση προεξέχει 0.30 νότια της νοτιοδυτικής πτέρυγας και δυτικά του τοιχείου Κ20–Κ19 (λεπτό περίγραμμα, όχι τοιχείο). Το γέμισμα ράμπας ξαναδιαγραμμίστηκε ομοιόμορφα (η αρχική διαγράμμιση είχε κενά από τις αφαιρεθείσες ετικέτες οπλισμού). Σημειώσεις «Τοιχείο έως το ύψος της πλάκας…» και «Κεκλιμένο τοιχίο…» κρατήθηκαν χωρίς το τμήμα «Οπλισμός: 2#Φ8/20». Οι στάθμες Σ.Μ./Α.Δ.Σ.Ε. κρατήθηκαν όπως αναγράφονται. Οι τομές 1-1, 2-2, 3-3, 4-4 και οι λεπτομέρειες υποστυλωμάτων/αγκυρώσεων δεν μεταφέρθηκαν.
- Οι λοξοί τοίχοι (βόρειος ≈90.3°, ανατολικός ≈0.8°) δίνουν τιμές όπως 0.455/0.505 (πραγματικές αποστάσεις παρειών).

## Σ2 αναθεώρηση 24/09/2026 (13/10/2026)
- Αρχείο: `Σ2 ... rev 24-09-26.pdf` → φάκελος `s2r/` (S2r.pdf, texts.json, geometry.json, dims.json). Παραδοτέο: `Σ2_αναθ_24-09-26_Ξυλότυπος_οροφής_υπογείου_A2_1-50.pdf` (+PNG).
- Διαφορές από το αρχικό Σ2 (έλεγχος με diff κειμένων/γεωμετρίας): η δομική γεωμετρία (υποστυλώματα, δοκοί, τοίχοι) ΤΑΥΤΟΣΗΜΗ· στάθμη πλάκας +0,05 → ±0,00 (όλες οι ενδείξεις)· ύψη δοκών: Δ1.1, Δ1.4, Δ9.5, Δ7.1 30/45→30/50, Δ6.1 30/50→30/55, Δ2.1 40/40→40/50, Δ10.1 25/40→25/50, Δ23.1 30/70→30/65· μπλε φυτευτά στοιχεία μετατοπισμένα ~3 pt· οπλισμοί αλλαγμένοι (δεν μεταφέρονται).
- Εκτέλεση: `DIR=../s2r PDF=S2r.pdf A2=1 LEVELS="±0,00 / +0,30" REV="24/09/2026" OX_MM=27 OY_MM=38.2 python3 sheet_s2.py`. Η regex σταθμών δέχεται πλέον «±».
- Πρόσθετες αλυσίδες (και στο αρχικό Σ2): V3 x=2122 (ανατολική λωρίδα: βόρειος τοίχος → Δ21.1 → λωρίδα → δοκοί/λωρίδες μεταξύ Κ25/Κ32/Κ34/Κ26 → νότιος τοίχος), V4 x=1060 (δυτική ζώνη: βόρειος τοίχος → Δ8.1 → τοιχείο πτέρυγας). Μετακινήσεις: ετικέτες Κ32 (εξωτ.), Κ34, Κ26 στο x=2040, Κ28 κάτω από τον τοίχο, Δ8.1 στο x=1100, διάσταση 1.01 στο x=2142.

## Έκδοση καλουπατζή Α2 1:50 (13/10/2026)
- Παραδοτέα: `Σ2_Ξυλότυπος_οροφής_υπογείου_A2_1-50.pdf` (1 φύλλο) και `Σ1_Ξυλότυπος_θεμελίωσης_A2_1-50.pdf` (2 φύλλα, σελ. 2 υποσταθμός). Α2 594×420, κλίμακα 1:50 (K=1, 1 m = 20 mm), γραμματοσειρές ×1.25, σειρές αλυσίδων 8.5 mm, πινακίδα μόνο με τίτλο / κλίμακα (+ γραφική κλίμακα 2 m) / διεύθυνση (`Sheet.title_box`). Εκτύπωση 100 % (χωρίς προσαρμογή στη σελίδα).
- Ενεργοποίηση με `A2=1` στα sheet_s2.py / sheet_s1.py / sheet_s1_sub.py (OX_MM/OY_MM: Σ2 27/38.2, Σ1 22.6/22.5, υποσταθμός 246.6/103.6· πινακίδα TB_X=526, TB_Y=362).
- Τιμές πλέον πάντα με 2 δεκαδικά (εκατοστά, στρογγύλευση half-up) — `Sheet.fmt`.
- Πρόσθετες διαστάσεις για τον καλουπατζή: πάχος περιμετρικών τοίχων 0.25 (μία διάσταση μέσα σε κάθε τοίχο, με λευκή μάσκα), εσωτερικές καθαρές διαστάσεις πυρήνα (Σ2 1.80×1.60, Σ1 2.05×1.60), θέση Δ12.1 κάτω από τον πυρήνα (Σ2, x=1900: 2.50|0.25), συν οι εσωτερικές αλυσίδες της 21/09.

## Εσωτερικές αλυσίδες (προσθήκη 21/09/2026, «βάλε και άλλες διαστάσεις»)
- Σ2: H1 y=770 (δυτ. τοίχος → Δ6.1/Κ1 → Δ9.5/Κ3), H2 y=1386 (τοιχείο Κ20–Κ19 → Δ23.1 → Δ24.1 → γραμμή πυρήνα Κ17), V1 x=1405 (βόρ. τοίχος → Δ1.1 → Δ3.1 → Δ4.3), V1b x=1600 (Δ4.3 → νότ. τοίχος). Μετακινήσεις: κύκλοι Π3, Π12, ετικέτα Κ3, στάθμη -0,55· η διάσταση 4.35 του μελετητή καλύπτεται από τη V1 (0.30+4.05).
- Σ1: H1 y=600 (Κ1, Κ2), H2 y=968 (Κ10, Κ3, πυρήνας), H3 y=1100 (Κ20, Κ9, Κ8, Κ7), V1 x=1300 (Κ2), V2 x=1496 (πυρήνας). Μετακινήσεις: ετικέτες Κ2, Κ6, Κ7, Κ20, Κ29, Κ31, Ε.Ζ. 70/80, στάθμες κέντρου.
- Οι θέσεις επιλέχθηκαν με το strip.py ώστε η γραμμή της αλυσίδας να μη διασχίζει κείμενα, κύκλους πλακών ή μπλε φυτευτά στοιχεία (διασχίζει μόνο τις λωρίδες δοκών/τοιχίων που διαστασιολογεί, με ticks στις παρειές τους).

## texts_dump.py
```python
import pymupdf, json, sys
pdf, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf); p = doc[0]
txt = p.get_text("dict")
spans=[]
for b in txt["blocks"]:
    for l in b.get("lines",[]):
        d=l["dir"]
        for s in l["spans"]:
            x0,y0,x1,y1=s["bbox"]
            spans.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,size=s["size"],font=s["font"],dir=(round(d[0],3),round(d[1],3)),text=s["text"],color=s["color"]))
horiz=[s for s in spans if s["dir"]==(1.0,0.0)]
vert=[s for s in spans if s["dir"]==(0.0,-1.0)]
other=[s for s in spans if s["dir"] not in ((1.0,0.0),(0.0,-1.0))]
def group(items, axis):
    if axis=='h': items=sorted(items,key=lambda s:(round(s["y1"]),s["x0"]))
    else: items=sorted(items,key=lambda s:(round(s["x0"]),-s["y1"]))
    out=[]
    for s in items:
        if out:
            g=out[-1]
            if axis=='h' and abs(g["y1"]-s["y1"])<3.5 and s["x0"]-g["x1"]<5 and s["x0"]-g["x1"]>-3:
                g["text"]+=s["text"]; g["x1"]=max(g["x1"],s["x1"]); g["y0"]=min(g["y0"],s["y0"]); g["fonts"].add(s["font"]); continue
            if axis=='v' and abs(g["x0"]-s["x0"])<3.5 and g["y0"]-s["y1"]<5 and g["y0"]-s["y1"]>-3:
                g["text"]+=s["text"]; g["y0"]=min(g["y0"],s["y0"]); g["x1"]=max(g["x1"],s["x1"]); g["fonts"].add(s["font"]); continue
        out.append(dict(x0=s["x0"],y0=s["y0"],x1=s["x1"],y1=s["y1"],text=s["text"],fonts={s["font"]},size=s["size"],color=s["color"],dir=s["dir"]))
    return out
allg=group(horiz,'h')+group(vert,'v')+[dict(x0=s["x0"],y0=s["y0"],x1=s["x1"],y1=s["y1"],text=s["text"],fonts={s["font"]},size=s["size"],color=s["color"],dir=s["dir"]) for s in other]
for g in allg: g["fonts"]=sorted(g["fonts"])
json.dump(allg, open(out,"w"), ensure_ascii=False, indent=0)
print(len(allg))

```

## extract.py
```python
"""Generic extraction of the non-rebar geometry of a Fespa formwork sheet (vector PDF, 1:50).
usage: python3 extract.py <pdf> <out.json> --region x0 y0 x1 y1 [--keep x0 y0 x1 y1 ...] [--stair x0 y0 x1 y1 ...]
All coordinates in source PDF points."""
import pymupdf, json, math, collections, statistics, argparse

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("out")
ap.add_argument("--region", nargs=4, type=float, required=True)
ap.add_argument("--keep", nargs="*", type=float, default=[])     # rects where thin solid 0.57 lines are geometry
ap.add_argument("--stair", nargs="*", type=float, default=[])    # rects where 0.28 non-axis lines are geometry (treads)
ap.add_argument("--diag_min", type=float, default=50)            # min length of 0.28 diagonals to keep (slab diagonals)
ap.add_argument("--x57_min", type=float, default=100)            # min length of 0.57 solid diagonals to keep (X crosses)
ap.add_argument("--keep_hatch", type=int, default=1)             # keep original 45-degree hatch lines (walls, fills, planted)
a = ap.parse_args()
X0, Y0, X1, Y1 = a.region
KEEP_RECTS = [tuple(a.keep[i:i+4]) for i in range(0, len(a.keep), 4)]
STAIRS = [tuple(a.stair[i:i+4]) for i in range(0, len(a.stair), 4)]

doc = pymupdf.open(a.pdf); page = doc[0]
dr = page.get_drawings()
def inreg(d):
    r = d["rect"]; return not (r.x1 < X0 or r.x0 > X1 or r.y1 < Y0 or r.y0 > Y1)
def W(d): return round(d.get("width") or 0, 2)
def BLUE(d): return (d.get("color") or (0, 0, 0))[2] > 0.5
def seg_len(p, q): return math.hypot(q.x - p.x, q.y - p.y)
def ang(p, q): return math.degrees(math.atan2(q.y - p.y, q.x - p.x)) % 180.0
def is_axis(p, q, tol=1.0):
    g = ang(p, q); return g < tol or abs(g - 90) < tol or g > 180 - tol
def in_rect(p, r): return r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]

out = dict(columns=[], lines=[], curves=[], circles=[], region=[X0, Y0, X1, Y1])

# ---------- 1.7 : column outlines -> closed loops ----------
segs17 = []
for d in dr:
    if inreg(d) and W(d) == 1.7:
        for it in d["items"]:
            if it[0] == 'l': segs17.append((it[1], it[2]))
            elif it[0] == 'c': out["curves"].append(dict(w=1.7, blue=False, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
def key(p): return (round(p.x, 1), round(p.y, 1))
adj = collections.defaultdict(list)
for i, (p, q) in enumerate(segs17): adj[key(p)].append(i); adj[key(q)].append(i)
used = set(); loops = []; open_chains = []
for i in range(len(segs17)):
    if i in used: continue
    p, q = segs17[i]; used.add(i); poly = [p, q]; cur = q; closed = False
    while True:
        nxt = [j for j in adj[key(cur)] if j not in used]
        if not nxt: break
        j = nxt[0]; used.add(j); c, d2 = segs17[j]
        cur = d2 if key(c) == key(cur) else c
        if key(cur) == key(poly[0]): closed = True; break
        poly.append(cur)
    (loops if closed else open_chains).append([(round(pp.x, 2), round(pp.y, 2)) for pp in poly])
out["columns"] = loops
out["open17"] = open_chains
print("columns (closed 1.7 loops):", len(loops), " open 1.7 chains:", len(open_chains))

# ---------- 0.85 : structural lines (drop rebar-style dashed runs: piece ~2.8pt / gap 1.7) ----------
segs85 = []
for d in dr:
    if inreg(d) and W(d) == 0.85:
        for it in d["items"]:
            if it[0] == 'l': segs85.append((it[1], it[2], BLUE(d)))
            elif it[0] == 'c': out["curves"].append(dict(w=0.85, blue=BLUE(d), pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
def run_groups(segs):
    groups = collections.defaultdict(list)
    for idx, (p, q, bl) in enumerate(segs):
        if abs(p.y - q.y) < 0.05: groups[('H', round(p.y, 1))].append((min(p.x, q.x), max(p.x, q.x), idx))
        elif abs(p.x - q.x) < 0.05: groups[('V', round(p.x, 1))].append((min(p.y, q.y), max(p.y, q.y), idx))
    runs = []
    for k, ivs in groups.items():
        ivs.sort(); cur = [ivs[0]]
        for iv in ivs[1:]:
            if iv[0] <= cur[-1][1] + 8: cur.append(iv)
            else: runs.append(cur); cur = [iv]
        runs.append(cur)
    return runs
drop85 = set(); dashed85 = set()
for run in run_groups(segs85):
    if len(run) >= 3:
        med = statistics.median([b - a_ for a_, b, i in run])
        if med < 3.5:
            for a_, b, i in run: drop85.add(i)
        elif med < 10:
            for a_, b, i in run: dashed85.add(i)
for idx, (p, q, bl) in enumerate(segs85):
    if idx in drop85: continue
    out["lines"].append(dict(w=0.85, blue=bl, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), dashed=(idx in dashed85)))
print("0.85 kept", len(segs85) - len(drop85), "dropped(rebar dashes)", len(drop85))

# ---------- 0.57 blue : planted elements -> keep all ----------
nb = 0
for d in dr:
    if inreg(d) and W(d) == 0.57 and BLUE(d):
        for it in d["items"]:
            if it[0] == 'l': out["lines"].append(dict(w=0.57, blue=True, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2))); nb += 1
            elif it[0] == 'c': out["curves"].append(dict(w=0.57, blue=True, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
print("blue 0.57 lines", nb)

# ---------- 0.57 black : dashed hidden lines kept; dotted (extension) dropped; solid only X-crosses / keep-rects ----------
def line_key(p, q):
    dx, dy = q.x - p.x, q.y - p.y; L = math.hypot(dx, dy)
    if L < 1e-6: return None
    g = round((math.degrees(math.atan2(dy, dx)) % 180.0) / 2.0) * 2.0 % 180
    r = math.radians(g); nx, ny = -math.sin(r), math.cos(r)
    return (g, round(p.x * nx + p.y * ny))
paths57 = [d for d in dr if inreg(d) and W(d) == 0.57 and not BLUE(d)]
groups = collections.defaultdict(list); singles = []
for d in paths57:
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        p, q = its[0][1], its[0][2]; k = line_key(p, q)
        if k is None: continue
        g = k[0]; r = math.radians(g); ux, uy = math.cos(r), math.sin(r)
        t0, t1 = p.x*ux + p.y*uy, q.x*ux + q.y*uy
        groups[k].append((min(t0, t1), max(t0, t1), p, q))
    else: singles.append(d)
kept57 = 0
for (g, off), segs in groups.items():
    segs.sort(key=lambda s: s[0]); runs = []; cur = [segs[0]]
    for s in segs[1:]:
        if s[0] <= cur[-1][1] + 8: cur.append(s)
        else: runs.append(cur); cur = [s]
    runs.append(cur)
    for run in runs:
        med = statistics.median([b - a_ for a_, b, _, _ in run])
        style = 'dotted' if (len(run) >= 3 and med < 1.8) else ('dashed' if (len(run) >= 3 and med < 10) else 'solid')
        for a_, b, p, q in run:
            keep = False
            if style == 'dashed': keep = not (not is_axis(p, q) and (run[-1][1] - run[0][0]) < 20)
            elif style == 'solid':
                if (b - a_) > a.x57_min and not is_axis(p, q): keep = True
                if any(in_rect(p, r) and in_rect(q, r) for r in KEEP_RECTS): keep = True
            if keep:
                kept57 += 1
                out["lines"].append(dict(w=0.57, blue=False, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), dashed=(style == 'dashed')))
for d in singles:   # curves: keep only big arcs (stairs); small circles = bar markers
    r = d["rect"]
    if max(r.width, r.height) > 20:
        for it in d["items"]:
            if it[0] == 'c': out["curves"].append(dict(w=0.57, blue=False, pts=[(round(p.x,2), round(p.y,2)) for p in it[1:5]]))
            elif it[0] == 'l': out["lines"].append(dict(w=0.57, blue=False, x0=round(it[1].x,2), y0=round(it[1].y,2), x1=round(it[2].x,2), y1=round(it[2].y,2)))
print("0.57 black kept", kept57)

# ---------- 0.28 : slab diagonals, stair treads, slab-label circles ----------
def in_poly(px, py, poly):
    inside = False; n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i+1) % n]
        if (y0 > py) != (y1 > py):
            xi = x0 + (py - y0) * (x1 - x0) / (y1 - y0)
            if xi > px: inside = not inside
    return inside
def in_any_column(px, py): return any(in_poly(px, py, c) for c in out["columns"])
kept28 = 0
for d in dr:
    if not (inreg(d) and W(d) == 0.28): continue
    its = d["items"]
    if len(its) == 1 and its[0][0] == 'l':
        p, q = its[0][1], its[0][2]; L = seg_len(p, q)
        g = ang(p, q); hatch = (abs(g - 45) < 2.5 or abs(g - 135) < 2.5) and L > 4.0
        keep = (L > a.diag_min and not is_axis(p, q)) or any(in_rect(p, r) and in_rect(q, r) and not is_axis(p, q, 0.5) and L > 5 for r in STAIRS)
        if hatch and a.keep_hatch: keep = True
        if keep and not (hatch and a.keep_hatch) and in_any_column((p.x + q.x) / 2, (p.y + q.y) / 2): keep = False
        if keep and hatch: pass
        if keep:
            kept28 += 1; out["lines"].append(dict(w=0.28, blue=False, x0=round(p.x,2), y0=round(p.y,2), x1=round(q.x,2), y1=round(q.y,2), hatch=hatch))
    elif all(it[0] == 'c' for it in its) and len(its) == 4:
        r = d["rect"]
        if 22 < max(r.width, r.height) < 28:
            out["circles"].append(dict(cx=round((r.x0+r.x1)/2,2), cy=round((r.y0+r.y1)/2,2), r=round(r.width/2,2)))
print("0.28 kept", kept28, "circles", len(out["circles"]))
json.dump(out, open(a.out, "w"), ensure_ascii=False)

```

## recover_dims.py
```python
"""Recover the designer's dimension lines (0.28 lines with arrowheads + italic value) inside a region of a Fespa sheet.
Output: list of dims {x0,y0,x1,y1 (source pts), value (text), dir 'H'/'V', text_side, ext: [(x,y,x,y)...] extension line stubs}."""
import pymupdf, json, math, re, sys, collections

def recover(pdf, texts, region, tol_val=0.02):
    X0, Y0, X1, Y1 = region
    doc = pymupdf.open(pdf); page = doc[0]; dr = page.get_drawings()
    S = 56.6929
    def inreg(p): return X0 <= p.x <= X1 and Y0 <= p.y <= Y1
    segs = []   # 0.28 single-line segments
    for d in dr:
        if round(d.get("width") or 0, 2) != 0.28: continue
        its = d["items"]
        if len(its) == 1 and its[0][0] == 'l':
            a, b = its[0][1], its[0][2]
            if inreg(a) or inreg(b): segs.append((a, b))
    def L(a, b): return math.hypot(b.x - a.x, b.y - a.y)
    def ang(a, b): return math.degrees(math.atan2(b.y - a.y, b.x - a.x)) % 180
    # arrowhead strokes: short, oblique (10..40 deg off axis)
    tips = []
    for a, b in segs:
        l = L(a, b)
        if 1.5 <= l <= 7.0:
            g = ang(a, b); off = min(g % 90, 90 - g % 90)
            if 8 <= off <= 40: tips.append(a); tips.append(b)
    # axis-aligned candidate dim pieces
    H = [(a, b) for a, b in segs if abs(a.y - b.y) <= 0.02 * L(a, b) + 0.05 and L(a, b) >= 3]
    V = [(a, b) for a, b in segs if abs(a.x - b.x) <= 0.02 * L(a, b) + 0.05 and L(a, b) >= 3]
    dims = []
    vals = [t for t in texts if any("Italic" in f for f in t["fonts"]) and re.match(r"^\d+\.\d\d$", t["text"])
            and X0 <= (t["x0"] + t["x1"]) / 2 <= X1 and Y0 <= (t["y0"] + t["y1"]) / 2 <= Y1]
    for t in vals:
        v = float(t["text"]); cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
        horiz = abs(t["dir"][1]) < 0.2
        best = None
        if horiz:
            # dim line is horizontal, near (below or above) the text: |y - cy| <= 12, and text centre within the line's x-extent (merged)
            cands = [(a, b) for a, b in H if abs(a.y - cy) <= 12]
            # group by y (round 0.5) and merge pieces within 40 pt gaps
            groups = collections.defaultdict(list)
            for a, b in cands: groups[round(a.y * 2) / 2].append((min(a.x, b.x), max(a.x, b.x)))
            for y, ivs in groups.items():
                ivs.sort(); runs = []; cur = list(ivs[0])
                for a_, b_ in ivs[1:]:
                    if a_ <= cur[1] + 40: cur[1] = max(cur[1], b_)
                    else: runs.append(tuple(cur)); cur = [a_, b_]
                runs.append(tuple(cur))
                for a_, b_ in runs:
                    slack = 5 if v >= 0.3 else 30
                    if not (a_ - slack <= cx <= b_ + slack): continue
                    # arrow tips on this line near the run ends
                    on = [p.x for p in tips if abs(p.y - y) <= 2.5 and a_ - 6 <= p.x <= b_ + 6]
                    if len(on) < 2: continue
                    # choose the pair of tips (left of cx, right of cx) whose distance matches v
                    lefts = sorted(set(round(x, 1) for x in on if x < cx)); rights = sorted(set(round(x, 1) for x in on if x > cx))
                    for xl in lefts:
                        for xr in rights:
                            if abs((xr - xl) / S - v) <= tol_val:
                                d = abs(cy - y)
                                if best is None or d < best[0]: best = (d, xl, y, xr, y)
        else:
            cands = [(a, b) for a, b in V if abs(a.x - cx) <= 12]
            groups = collections.defaultdict(list)
            for a, b in cands: groups[round(a.x * 2) / 2].append((min(a.y, b.y), max(a.y, b.y)))
            for x, ivs in groups.items():
                ivs.sort(); runs = []; cur = list(ivs[0])
                for a_, b_ in ivs[1:]:
                    if a_ <= cur[1] + 40: cur[1] = max(cur[1], b_)
                    else: runs.append(tuple(cur)); cur = [a_, b_]
                runs.append(tuple(cur))
                for a_, b_ in runs:
                    slack = 5 if v >= 0.3 else 30
                    if not (a_ - slack <= cy <= b_ + slack): continue
                    on = [p.y for p in tips if abs(p.x - x) <= 2.5 and a_ - 6 <= p.y <= b_ + 6]
                    if len(on) < 2: continue
                    ups = sorted(set(round(yv, 1) for yv in on if yv < cy)); downs = sorted(set(round(yv, 1) for yv in on if yv > cy))
                    for yu in ups:
                        for yd in downs:
                            if abs((yd - yu) / S - v) <= tol_val:
                                d = abs(cx - x)
                                if best is None or d < best[0]: best = (d, x, yu, x, yd)
        if best:
            d, x0, y0, x1, y1 = best
            side = -1 if (cy < y0 if horiz else cx < x0) else +1   # text above/left = -1
            dims.append(dict(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2), value=t["text"], dir="H" if horiz else "V", side=side,
                             tx=round(cx, 1), ty=round(cy, 1)))
        else:
            dims.append(dict(value=t["text"], dir="H" if horiz else "V", tx=round(cx, 1), ty=round(cy, 1), unresolved=True))
    return dims

if __name__ == "__main__":
    pdf, texts, out = sys.argv[1], sys.argv[2], sys.argv[3]
    region = [float(v) for v in sys.argv[4:8]]
    T = json.load(open(texts))
    dims = recover(pdf, T, region)
    ok = [d for d in dims if not d.get("unresolved")]
    print("dimension texts:", len(dims), "resolved:", len(ok))
    for d in dims:
        if d.get("unresolved"): print("  UNRESOLVED", d["value"], d["dir"], "at", d["tx"], d["ty"])
    json.dump(dims, open(out, "w"), indent=0)

```

## lib.py
```python
"""Shared drawing library for the clean formwork sheets (A3, 1:SCALE) built from Fespa 1:50 vector PDFs."""
import pymupdf, json, math, datetime, os, re
from shapely.geometry import Polygon, LineString, Point

S = 56.6929                      # source pt per metre (1:50)
MM = 72 / 25.4
FONT_R = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
FONT_B = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
BLUE = (0, 0.43, 0.85); BLACK = (0, 0, 0); GRAY = (0.35, 0.35, 0.35)
DIM_SIZE = 7.2
TICK = 2.2 * MM
ROW = 8.0 * MM

class Sheet:
    def __init__(self, geometry, texts, scale=75, ox_mm=45, oy_mm=24, page_w=420, page_h=297, sx0=None, sy0=None, fs=1.0):
        self.FS = fs                     # font scale applied to every text size (A2 sheets use ~1.25)
        self.G = json.load(open(geometry)) if isinstance(geometry, str) else geometry
        self.T = json.load(open(texts)) if isinstance(texts, str) else texts
        self.SCALE = scale; self.K = 50.0 / scale
        self.PAGE_W, self.PAGE_H = page_w * MM, page_h * MM
        self.OX, self.OY = ox_mm * MM, oy_mm * MM
        self.SX0 = sx0 if sx0 is not None else self.G["region"][0]
        self.SY0 = sy0 if sy0 is not None else self.G["region"][1]
        self.doc = pymupdf.open(); self.page = self.doc.new_page(width=self.PAGE_W, height=self.PAGE_H)
        self.shape = self.page.new_shape()
        self.texts_out = []      # (rect, text) for overlap checks

    # ---------------- transforms
    def X(self, x): return self.OX + (x - self.SX0) * self.K
    def Y(self, y): return self.OY + (y - self.SY0) * self.K
    def P(self, x, y): return pymupdf.Point(self.X(x), self.Y(y))
    def flush(self):
        self.shape.commit(); self.shape = self.page.new_shape()

    # ---------------- primitives (output coords)
    def oline(self, x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
        self.shape.draw_line(pymupdf.Point(x0, y0), pymupdf.Point(x1, y1))
        self.shape.finish(width=w, color=color, dashes=dashes, lineCap=0)
    def sline(self, x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
        self.oline(self.X(x0), self.Y(y0), self.X(x1), self.Y(y1), w, color, dashes)
    def orect(self, x0, y0, x1, y1, w=0.5, color=BLACK, fill=None):
        self.shape.draw_rect(pymupdf.Rect(x0, y0, x1, y1)); self.shape.finish(width=w, color=color, fill=fill)
    def ocircle(self, x, y, r, w=0.35, color=BLACK, fill=None):
        self.shape.draw_circle(pymupdf.Point(x, y), r); self.shape.finish(width=w, color=color, fill=fill)
    @staticmethod
    def text_w(s, size, bold=False): return (FONT_B if bold else FONT_R).text_length(s, fontsize=size)
    def tw(self, s, size, bold=False): return self.text_w(s, size * self.FS, bold)    # width as drawn (font scale applied)

    def otext(self, x, y, s, size=7, bold=False, rot=0, align="left", color=BLACK, mask=False):
        """(x,y) = baseline start (left) / centre / right end. rot=90 -> reads bottom-to-top from (x,y), glyphs left of x.
        mask=True paints a white box behind the text (hides hatch / crossing thin lines)."""
        size = size * self.FS
        font = FONT_B if bold else FONT_R
        w = font.text_length(s, fontsize=size)
        off = -w / 2 if align == "center" else (-w if align == "right" else 0)
        if mask:
            if rot == 0: self.orect(x + off - 0.8, y - size * 0.8, x + off + w + 0.8, y + size * 0.26, 0, (1, 1, 1), (1, 1, 1))
            else: self.orect(x - size * 0.8, y - w - 0.8, x + size * 0.26, y + 0.8, 0, (1, 1, 1), (1, 1, 1))
        self.flush()
        tw = pymupdf.TextWriter(self.page.rect)
        tw.append(pymupdf.Point(x + off, y), s, font=font, fontsize=size)
        if rot == 0:
            tw.write_text(self.page, color=color)
            self.texts_out.append((pymupdf.Rect(x + off, y - size * 0.75, x + off + w, y + size * 0.22), s))
        else:
            m = pymupdf.Matrix(1, 0, 0, 1, 0, 0).prerotate(rot)
            tw.write_text(self.page, color=color, morph=(pymupdf.Point(x, y), m))
            self.texts_out.append((pymupdf.Rect(x - size * 0.75, y - w, x + size * 0.22, y), s))
        return w
    def stext(self, x, y, s, **kw): return self.otext(self.X(x), self.Y(y), s, **kw)

    def hatch_polygon(self, pts_src, spacing=2.6, angle=45, w=0.25, color=BLACK):
        poly = Polygon([(self.X(x), self.Y(y)) for x, y in pts_src])
        if not poly.is_valid: poly = poly.buffer(0)
        minx, miny, maxx, maxy = poly.bounds
        d = max(maxx - minx, maxy - miny) * 2; cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        a = math.radians(angle); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        n = int(d / spacing) + 1
        for i in range(-n, n + 1):
            ox, oy = cx + nx * i * spacing, cy + ny * i * spacing
            inter = LineString([(ox - ux * d, oy - uy * d), (ox + ux * d, oy + uy * d)]).intersection(poly)
            for g in getattr(inter, "geoms", [inter]):
                if g.is_empty or g.geom_type != "LineString": continue
                c = list(g.coords); self.oline(c[0][0], c[0][1], c[-1][0], c[-1][1], w, color)

    # ---------------- geometry from extraction
    def draw_geometry(self, rehatch_columns=False, wmap=None, drop=None):
        G = self.G
        WMAP = wmap or {1.7: 1.1, 0.85: 0.6, 0.57: 0.3, 0.28: 0.22}
        for poly in G["columns"]:
            if rehatch_columns: self.hatch_polygon(poly)
            pts = [self.P(x, y) for x, y in poly] + [self.P(*poly[0])]
            self.shape.draw_polyline(pts); self.shape.finish(width=1.1, color=BLACK)
        for ch in G.get("open17", []):
            self.shape.draw_polyline([self.P(x, y) for x, y in ch]); self.shape.finish(width=1.1, color=BLACK)
        for l in G["lines"]:
            if rehatch_columns and l.get("hatch") and self._in_column((l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2): continue
            if drop and drop(l): continue
            self.sline(l["x0"], l["y0"], l["x1"], l["y1"], w=WMAP[l["w"]], color=BLUE if l["blue"] else BLACK)
        for c in G["curves"]:
            p = [self.P(x, y) for x, y in c["pts"]]
            self.shape.draw_bezier(*p); self.shape.finish(width=WMAP.get(c["w"], 0.6), color=BLUE if c["blue"] else BLACK)
    def _in_column(self, px, py):
        for poly in self.G["columns"]:
            if Polygon(poly).contains(Point(px, py)): return True
        return False

    # ---------------- dimensioning
    @staticmethod
    def fmt(v):
        c = int(math.floor(v * 100 + 0.5 + 1e-9))      # centimetres, half-up
        return "%d.%02d" % (c // 100, c % 100)
    def tick(self, xo, yo, color=BLACK):
        self.oline(xo - TICK / 2 * 0.7071, yo + TICK / 2 * 0.7071, xo + TICK / 2 * 0.7071, yo - TICK / 2 * 0.7071, 0.6, color)

    def hchain(self, xs, y_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True, values=None, narrow_perp=False, mask=False):
        X, Y = self.X, self.Y
        xs = sorted(xs); x0, x1 = X(xs[0]), X(xs[-1])
        self.oline(x0 - 1.0 * MM, y_out, x1 + 1.0 * MM, y_out, 0.35, color)
        for x in xs:
            xo = X(x); self.tick(xo, y_out, color)
            if ext and x in ext:
                ys = Y(ext[x]); gap = 0.8 * MM
                if ys < y_out: self.oline(xo, ys + gap, xo, y_out + ext_over, 0.25, color)
                else: self.oline(xo, ys - gap, xo, y_out - ext_over, 0.25, color)
        last1 = -1e9
        for i, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
            s = self.fmt((b - a) / S) if not values else values[i]
            if s == "": continue
            sz = size * self.FS
            w = self.text_w(s, sz); mid = (X(a) + X(b)) / 2; L = X(b) - X(a)
            lvl = 0
            if stagger and w + 1.5 > L:
                lvl = 1
                if mid - w / 2 < last1 + 1.0: lvl = 2
            if lvl == 1: last1 = mid + w / 2
            if narrow_perp and lvl > 0:
                # vertical (rotated) text centred on the narrow segment, just off the line
                xb = mid + sz * 0.36
                yb = y_out - 1.2 * MM if text_side < 0 else y_out + 1.2 * MM + w
                self.otext(xb, yb, s, size=size, rot=90, color=color, mask=mask); continue
            dy = 0.6 * MM + lvl * (sz * 0.72 + 1.6)
            yb = y_out - dy if text_side < 0 else y_out + dy + sz * 0.72
            self.otext(mid, yb, s, size=size, align="center", color=color, mask=mask)

    def vchain(self, ys, x_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True, narrow_h=False, values=None, mask=False):
        X, Y = self.X, self.Y
        ys = sorted(ys); y0, y1 = Y(ys[0]), Y(ys[-1])
        self.oline(x_out, y0 - 1.0 * MM, x_out, y1 + 1.0 * MM, 0.35, color)
        for y in ys:
            yo = Y(y); self.tick(x_out, yo, color)
            if ext and y in ext:
                xs_ = X(ext[y]); gap = 0.8 * MM
                if xs_ > x_out: self.oline(xs_ - gap, yo, x_out - ext_over, yo, 0.25, color)
                else: self.oline(xs_ + gap, yo, x_out + ext_over, yo, 0.25, color)
        last1 = -1e9
        for i, (a, b) in enumerate(zip(ys[:-1], ys[1:])):
            s = self.fmt((b - a) / S) if not values else values[i]
            if s == "": continue
            sz = size * self.FS
            w = self.text_w(s, sz); mid = (Y(a) + Y(b)) / 2; L = Y(b) - Y(a)
            lvl = 0
            if stagger and w + 1.5 > L:
                lvl = 1
                if mid - w / 2 < last1 + 1.0: lvl = 2
            if lvl == 1: last1 = mid + w / 2
            if narrow_h and lvl > 0:
                xh = x_out - 1.5 * MM - w if text_side < 0 else x_out + 1.5 * MM
                self.otext(xh, mid + sz * 0.36, s, size=size, color=color, mask=mask); continue
            dx = 0.6 * MM + lvl * (sz * 0.72 + 1.6)
            xb = x_out - dx if text_side < 0 else x_out + dx + sz * 0.72
            self.otext(xb, mid + w / 2, s, size=size, rot=90, color=color, mask=mask)

    def idim_h(self, xs, y_src, side=-1, ext_to=None, size=6.8, values=None):
        self.hchain(xs, self.Y(y_src), side, size=size, ext=ext_to, ext_over=0.8 * MM, values=values)
    def idim_v(self, ys, x_src, side=-1, ext_to=None, narrow_h=True, size=6.8, values=None):
        self.vchain(ys, self.X(x_src), side, size=size, ext=ext_to, ext_over=0.8 * MM, narrow_h=narrow_h, values=values)

    def dim_generic(self, x0, y0, x1, y1, value, text_side=-1, size=6.8, ext=None, narrow_h=True, tpos=None, trot=0, mask=False):
        """single dimension between two source points (horizontal or vertical), value string given (designer's).
        tpos=(x,y) source: write the value there (baseline-left) instead of the automatic position."""
        v = [value] if tpos is None else [""]
        if abs(y1 - y0) < 0.5:
            self.hchain([x0, x1], self.Y(y0), text_side, size=size, values=v, ext=ext, ext_over=0.8 * MM, mask=mask)
        else:
            self.vchain([y0, y1], self.X(x0), text_side, size=size, values=v, ext=ext, ext_over=0.8 * MM, narrow_h=narrow_h, mask=mask)
        if tpos is not None: self.stext(tpos[0], tpos[1], value, size=size, rot=trot, mask=mask)

    def dump_texts(self, path):
        """placed texts as source-coordinate rects (for probing)."""
        out = []
        for r, t in self.texts_out:
            out.append(([self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K, self.SX0 + (r.x1 - self.OX) / self.K, self.SY0 + (r.y1 - self.OY) / self.K], t))
        json.dump(out, open(path, "w"))

    # ---------------- labels
    def col_label(self, x, y, s, rot=0, align="left", size=8.4, mask=False): self.stext(x, y, s, size=size, bold=True, rot=rot, align=align, mask=mask)
    def beam_label(self, x, y, s, rot=0, size=7.2, align="left", mask=False): self.stext(x, y, s, size=size, rot=rot, align=align, mask=mask)
    def slab_label(self, cx, cy, name, h, r=3.0 * MM):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.35, BLACK, (1, 1, 1))
        self.oline(c.x - r, c.y, c.x + r, c.y, 0.35)
        self.otext(c.x, c.y - 1.1 * self.FS, name, size=6.8, bold=True, align="center")
        self.otext(c.x, c.y + 5.8 * self.FS, "h=%s" % h, size=6.0, align="center")
    def level_mark(self, cx, cy, s, r=1.5 * MM, color=BLACK, textpos=None, rot=0, size=7.4):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.35, color, (1, 1, 1))
        for a0 in (90, 270):
            pts = [c]
            for kk in range(0, 91, 10):
                a = math.radians(a0 + kk); pts.append(pymupdf.Point(c.x + r * math.cos(a), c.y - r * math.sin(a)))
            self.shape.draw_polyline(pts + [c]); self.shape.finish(width=0, color=color, fill=color)
        self.oline(c.x - r * 1.4, c.y, c.x + r * 1.4, c.y, 0.3, color); self.oline(c.x, c.y - r * 1.4, c.x, c.y + r * 1.4, 0.3, color)
        if textpos is None: textpos = (c.x + r + 1.5, c.y + 2.4)
        self.otext(textpos[0], textpos[1], s, size=size, bold=True, rot=rot, color=color)
    def marker(self, cx, cy, num, r=2.0 * MM):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.6, BLACK, (1, 1, 1))
        self.otext(c.x, c.y + 2.6, str(num), size=7.2, bold=True, align="center")
    def note(self, x_src, y_src, lines, size=6.2, rot=0, mask=False):
        """lines of text at a source point; mask=True paints a white box behind each line (interrupts crossing lines)."""
        sz = size * self.FS; lh = sz * 1.25
        for i, ln in enumerate(lines):
            w = self.text_w(ln, sz)
            if rot == 0:
                x, y = self.X(x_src), self.Y(y_src) + i * lh
                if mask: self.orect(x - 1.0, y - sz * 0.8, x + w + 1.0, y + sz * 0.28, 0, (1, 1, 1), (1, 1, 1))
                self.otext(x, y, ln, size=size)
            else:
                x, y = self.X(x_src) + i * lh, self.Y(y_src)
                if mask: self.orect(x - sz * 0.8, y - w - 1.0, x + sz * 0.28, y + 1.0, 0, (1, 1, 1), (1, 1, 1))
                self.otext(x, y, ln, size=size, rot=90)

    # ---------------- sheet frame
    def title_block(self, theme_lines, base_lines, number, legend=None, project=None):
        MMv = MM; TB_Y0, TB_Y1 = 262 * MMv, 289 * MMv
        self.orect(10 * MMv, TB_Y0, 410 * MMv, TB_Y1, 0.8)
        cols = [10 * MMv, 140 * MMv, 250 * MMv, 330 * MMv, 370 * MMv, 410 * MMv]
        for cx in cols[1:-1]: self.oline(cx, TB_Y0, cx, TB_Y1, 0.5)
        def cell(x, y, label, lines, lsize=5.6, vsize=7.0, bold=True):
            self.otext(x + 2 * MMv, y + 3.2 * MMv, label, size=lsize, color=GRAY)
            for i, ln in enumerate(lines): self.otext(x + 2 * MMv, y + 7.2 * MMv + i * (vsize + 2.2), ln, size=vsize, bold=bold)
        cell(cols[0], TB_Y0, "ΕΡΓΟ", project or ["ΑΝΕΓΕΡΣΗ ΠΕΝΤΑΟΡΟΦΟΥ ΚΤΗΡΙΟΥ ΚΑΤΟΙΚΙΩΝ ΜΕ ΥΠΟΓΕΙΟ, ΣΟΦΙΤΑ ΚΑΙ ΔΩΜΑ",
                                            "ΟΔΟΣ ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ – Ο.Τ. 103-15, ΔΗΜΟΣ ΕΛΛΗΝΙΚΟΥ-ΑΡΓΥΡΟΥΠΟΛΗΣ"], vsize=6.6)
        self.otext(cols[0] + 2 * MMv, TB_Y0 + 20.5 * MMv, "ΕΡΓΟΔΟΤΗΣ: ARKAD Ι.Κ.Ε.     ΜΕΛΕΤΗΤΗΣ ΣΤΑΤΙΚΩΝ: ΓΙΩΡΓΟΣ ΚΟΓΙΑΣ, ΠΟΛΙΤΙΚΟΣ ΜΗΧΑΝΙΚΟΣ", size=6.2)
        cell(cols[1], TB_Y0, "ΘΕΜΑ ΣΧΕΔΙΟΥ", theme_lines, vsize=8.0)
        if legend: self.otext(cols[1] + 2 * MMv, TB_Y0 + 22.5 * MMv, legend, size=5.4, color=GRAY)
        cell(cols[2], TB_Y0, "ΒΑΣΗ", base_lines, vsize=6.6, bold=False)
        cell(cols[3], TB_Y0, "ΚΛΙΜΑΚΑ", ["1:%d" % self.SCALE, "A3"], vsize=11.0)
        cell(cols[4], TB_Y0, "ΑΡ. ΣΧΕΔΙΟΥ / ΗΜΕΡΟΜΗΝΙΑ", [number, datetime.date.today().strftime("%d/%m/%Y")], vsize=8.6)
        # scale bar
        sbx, sby = 336 * MMv, 254 * MMv; u = S * self.K
        for i in range(5): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.6 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(6): self.otext(sbx + i * u, sby - 1.2 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx + 5.4 * u, sby + 1.4 * MMv, "m  (1:%d)" % self.SCALE, size=5.5)

    def save(self, path, meta=None):
        self.flush()
        if meta: self.doc.set_metadata(meta)
        self.doc.save(path, garbage=4, deflate=True)
        json.dump(dict(K=self.K, OX=self.OX, OY=self.OY, SX0=self.SX0, SY0=self.SY0), open(path + ".meta.json", "w"))

    # ---------------- checks
    def check(self, exclude_y_above=None):
        """text/text overlaps and text over solid structural lines or columns (output coords)."""
        import itertools
        from shapely.geometry import box
        def shrink(r, f=0.12):
            h = min(r.width, r.height) * f; return pymupdf.Rect(r.x0 + h, r.y0 + h, r.x1 - h, r.y1 - h)
        spans = self.texts_out
        n = 0
        for (r1, t1), (r2, t2) in itertools.combinations(spans, 2):
            if shrink(r1).intersects(shrink(r2)): n += 1; print("TEXT OVERLAP:", t1, "|", t2, [round(v) for v in r1])
        lines = [(LineString([(self.X(l["x0"]), self.Y(l["y0"])), (self.X(l["x1"]), self.Y(l["y1"]))]), l) for l in self.G["lines"] if l["w"] >= 0.85 and not l.get("dashed")]
        cols = [Polygon([(self.X(x), self.Y(y)) for x, y in c]) for c in self.G["columns"]]
        bad = 0
        for r, t in spans:
            if exclude_y_above and r.y0 > exclude_y_above: continue
            h = min(r.width, r.height) * 0.2
            bb = box(r.x0 + h, r.y0 + h, r.x1 - h, r.y1 - h)
            hit = [l for ln, l in lines if ln.intersects(bb)]
            if hit:
                bad += 1; l = hit[0]
                print("|%s| crosses a solid structural line at src (%.0f,%.0f): line (%.1f,%.1f)-(%.1f,%.1f) w=%s%s" % (t, self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K, l["x0"], l["y0"], l["x1"], l["y1"], l["w"], " blue" if l["blue"] else ""))
            if any(bb.intersects(c) for c in cols): bad += 1; print("|%s| over a column at src (%.0f,%.0f)" % (t, self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K))
        print("text overlaps:", n, " structural conflicts:", bad)
        return n, bad

    def title_box(self, x0_mm, y0_mm, w_mm, title_lines, address_lines, scale_label=None, bar_m=2):
        """minimal title box (top-left corner at x0,y0 in mm): drawing title, scale (+ scale bar on its own line), address."""
        MMv = MM; x0, x1 = x0_mm * MMv, (x0_mm + w_mm) * MMv
        tsz, asz, ssz = 9.6, 7.6, 10.0
        th, ah, sh_ = tsz * self.FS, asz * self.FS, ssz * self.FS
        y0 = y0_mm * MMv
        y = y0 + 3.5 * MMv + th * 0.75
        for ln in title_lines: self.otext(x0 + 3 * MMv, y, ln, size=tsz, bold=True); y += th + 3
        y_sep1 = y - th * 0.75 - 1.0 * MMv + th * 0.75 - 2.0
        y_sep1 = y - 1.0 * MMv - 3
        y = y_sep1 + 3.0 * MMv + sh_ * 0.75
        self.otext(x0 + 3 * MMv, y, scale_label or ("ΚΛΙΜΑΚΑ 1:%d" % self.SCALE), size=ssz, bold=True)
        u = S * self.K; sbx = x0 + 3 * MMv; sby = y + 2.2 * MMv
        n = min(bar_m, int((x1 - 4 * MMv - sbx) / u))
        for i in range(n): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.8 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(n + 1): self.otext(sbx + i * u, sby + 1.8 * MMv + 2.8 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx + n * u + 2.0 * MMv, sby + 1.8 * MMv + 2.8 * MMv, "m", size=5.5)
        y_sep2 = sby + 1.8 * MMv + 2.8 * MMv + 2.0 * MMv
        y = y_sep2 + 3.0 * MMv + ah * 0.75
        for ln in address_lines: self.otext(x0 + 3 * MMv, y, ln, size=asz, bold=False); y += ah + 2.5
        y1 = y - ah - 2.5 + ah * 0.3 + 3.0 * MMv
        self.orect(x0, y0, x1, y1, 0.8); self.oline(x0, y_sep1, x1, y_sep1, 0.4); self.oline(x0, y_sep2, x1, y_sep2, 0.4)
        return (x0, y0, x1, y1)

    def title_column(self, x0_mm, theme_lines, base_lines, number, legend=None, width_mm=50, y0_mm=10, y1_mm=287):
        """vertical title block at the right edge (for wide plans)."""
        MMv = MM; x0, x1 = x0_mm * MMv, (x0_mm + width_mm) * MMv; y0, y1 = y0_mm * MMv, y1_mm * MMv
        self.orect(x0, y0, x1, y1, 0.8)
        def block(y, label, lines, vsize=6.4, bold=True, lh=None):
            self.otext(x0 + 2 * MMv, y + 3.0 * MMv, label, size=5.4, color=GRAY)
            lh = lh or (vsize + 2.0)
            for i, ln in enumerate(lines): self.otext(x0 + 2 * MMv, y + 6.6 * MMv + i * lh, ln, size=vsize, bold=bold)
            return y + 6.6 * MMv + len(lines) * lh + 1.5 * MMv
        y = y0
        y = block(y, "ΕΡΓΟ", ["ΑΝΕΓΕΡΣΗ ΠΕΝΤΑΟΡΟΦΟΥ ΚΤΗΡΙΟΥ", "ΚΑΤΟΙΚΙΩΝ ΜΕ ΥΠΟΓΕΙΟ,", "ΣΟΦΙΤΑ ΚΑΙ ΔΩΜΑ"], vsize=6.6)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΘΕΣΗ", ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ – Ο.Τ. 103-15", "ΔΗΜΟΣ ΕΛΛΗΝΙΚΟΥ-ΑΡΓΥΡΟΥΠΟΛΗΣ"], vsize=6.2, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΕΡΓΟΔΟΤΗΣ", ["ARKAD Ι.Κ.Ε."], vsize=6.6)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΜΕΛΕΤΗΤΗΣ ΣΤΑΤΙΚΩΝ", ["ΓΙΩΡΓΟΣ ΚΟΓΙΑΣ", "ΠΟΛΙΤΙΚΟΣ ΜΗΧΑΝΙΚΟΣ"], vsize=6.4, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΘΕΜΑ ΣΧΕΔΙΟΥ", theme_lines, vsize=7.4)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΒΑΣΗ", base_lines, vsize=6.2, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΚΛΙΜΑΚΑ", ["1:%d   (A3)" % self.SCALE], vsize=11.0)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΑΡ. ΣΧΕΔΙΟΥ / ΗΜΕΡΟΜΗΝΙΑ", [number, datetime.date.today().strftime("%d/%m/%Y")], vsize=8.0)
        self.oline(x0, y, x1, y, 0.4)
        if legend:
            yy = y + 3.0 * MMv
            for ln in legend: self.otext(x0 + 2 * MMv, yy, ln, size=5.4, color=GRAY); yy += 6.6
            y = yy + 1 * MMv
            self.oline(x0, y, x1, y, 0.4)
        # scale bar
        sbx, sby = x0 + 3 * MMv, y1 - 9 * MMv; u = S * self.K
        n = int((width_mm - 8) * MMv / u)
        for i in range(n): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.6 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(n + 1): self.otext(sbx + i * u, sby - 1.2 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx, sby + 5.5 * MMv, "m  (1:%d)" % self.SCALE, size=5.5)

```

## auto.py
```python
"""Automatic label helpers: column labels, beam labels with computed clear length L, slab labels, level marks."""
import re, math, json
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
S = 56.6929

def parse_labels(T, region):
    X0, Y0, X1, Y1 = region
    def inr(t, pad=60): return X0 - pad <= (t["x0"] + t["x1"]) / 2 <= X1 + pad and Y0 - pad <= (t["y0"] + t["y1"]) / 2 <= Y1 + pad
    cols = [t for t in T if re.match(r"^Κ\d+\s+[\d/]+$", t["text"].strip()) and inr(t)]
    beams = [t for t in T if re.match(r"^Δ\s*\d+\.\d+\s+\d+/\d+", t["text"].strip()) and inr(t, 0)]
    ez = [t for t in T if t["text"].strip().startswith("Ε.Ζ.") and inr(t, 0)]
    slabs = [t for t in T if re.match(r"^Π\d*$", t["text"].strip()) and inr(t, 0)]
    hs = [t for t in T if re.match(r"^h=\s*\d+$", t["text"].strip()) and inr(t, 0)]
    levels = [t for t in T if re.match(r"^[+±-]\d,\d\d$", t["text"].strip()) and inr(t, 0)]
    return dict(cols=cols, beams=beams, ez=ez, slabs=slabs, hs=hs, levels=levels)

def beam_length(G, t, b_cm):
    """clear length of the beam labelled by text t (source coords) by ray casting along the beam axis."""
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    horiz = abs(t["dir"][1]) < 0.2
    ux, uy = (1, 0) if horiz else (0, 1)
    nx, ny = (0, 1) if horiz else (1, 0)
    bw = b_cm / 100 * S
    # beam edges: parallel 0.85 solid lines near the label
    par = []
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 5: continue
        if horiz and abs(dy) > 0.02 * Ln + 0.1: continue
        if not horiz and abs(dx) > 0.02 * Ln + 0.1: continue
        # perpendicular offset from label centre
        off = (l["y0"] - cy) if horiz else (l["x0"] - cx)
        # label centre must be within the segment's along-extent (with slack)
        a0, a1 = (min(l["x0"], l["x1"]), max(l["x0"], l["x1"])) if horiz else (min(l["y0"], l["y1"]), max(l["y0"], l["y1"]))
        c_along = cx if horiz else cy
        if not (a0 - 15 <= c_along <= a1 + 15): continue
        if abs(off) <= bw + 8: par.append(off)
    neg = [o for o in par if o < 0]; pos = [o for o in par if o > 0]
    if neg and pos: centre_off = (max(neg) + min(pos)) / 2
    else: centre_off = 0.0
    px, py = (cx, cy + centre_off) if horiz else (cx + centre_off, cy)
    # obstacles: column polygons, open 1.7 chains, perpendicular 0.85 solid segments
    obst = [Polygon(c).exterior for c in G["columns"]] + [LineString(c) for c in G.get("open17", []) if len(c) > 1]
    for l in G["lines"]:
        if l["w"] not in (0.85, 1.7) or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 4: continue
        perp = (abs(dx) <= 0.05 * Ln + 0.1) if horiz else (abs(dy) <= 0.05 * Ln + 0.1)
        if perp:
            e = bw / 2 + 3; k_ = e / Ln
            obst.append(LineString([(l["x0"] - dx * k_, l["y0"] - dy * k_), (l["x1"] + dx * k_, l["y1"] + dy * k_)]))
    def cast(sign):
        ray = LineString([(px, py), (px + sign * ux * 3000, py + sign * uy * 3000)])
        best = None
        for o in obst:
            inter = ray.intersection(o)
            if inter.is_empty: continue
            pts = []
            if inter.geom_type == "Point": pts = [inter]
            elif inter.geom_type == "MultiPoint": pts = list(inter.geoms)
            elif inter.geom_type in ("LineString", "MultiLineString"):
                for g in getattr(inter, "geoms", [inter]): pts += [Point(c) for c in g.coords]
            for q in pts:
                d = math.hypot(q.x - px, q.y - py)
                if d > 1.0 and (best is None or d < best[0]): best = (d, q)
        return best
    a = cast(+1); b = cast(-1)
    if not a or not b: return None, (px, py), (a, b)
    return (a[0] + b[0]) / S, (px, py), (a[1], b[1])

def thin_solid_segments(pdf, region):
    """0.57 black solid segments (leaders) from the raw drawing within region."""
    import pymupdf
    X0, Y0, X1, Y1 = region
    doc = pymupdf.open(pdf); dr = doc[0].get_drawings(); segs = []
    for d in dr:
        if round(d.get("width") or 0, 2) != 0.57 or (d.get("color") or (0, 0, 0))[2] > 0.5: continue
        for it in d["items"]:
            if it[0] != 'l': continue
            a, b = it[1], it[2]; Ln = math.hypot(b.x - a.x, b.y - a.y)
            if Ln < 6: continue
            if X0 <= a.x <= X1 and Y0 <= a.y <= Y1: segs.append(((a.x, a.y), (b.x, b.y)))
    return segs

def follow_leader(t, segs, pad=30):
    """from a label bbox, follow a chain of thin segments to its far end. Returns (x,y) or None."""
    x0, y0, x1, y1 = t["x0"] - pad, t["y0"] - pad, t["x1"] + pad, t["y1"] + pad
    def near_box(p): return x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    start = None
    cands = []
    for a, b in segs:
        if math.hypot(b[0]-a[0], b[1]-a[1]) < 12: continue
        if near_box(a) and not near_box(b): cands.append((a, b))
        elif near_box(b) and not near_box(a): cands.append((b, a))
    if not cands: return None
    # nearest start point to the label centre
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    start = min(cands, key=lambda s: math.hypot(s[0][0]-cx, s[0][1]-cy))
    cur = start[1]; used = {start}
    for _ in range(6):
        nxt = None
        for sgm in segs:
            if sgm in used: continue
            a, b = sgm
            if math.hypot(a[0] - cur[0], a[1] - cur[1]) < 1.5: nxt = (sgm, b); break
            if math.hypot(b[0] - cur[0], b[1] - cur[1]) < 1.5: nxt = (sgm, a); break
        if not nxt: break
        used.add(nxt[0]); cur = nxt[1]
    return cur

def bracket(G, px, py, horiz, bw):
    """parallel 0.85 solid lines bracketing point (px,py) within bw+8; returns (neg, pos) offsets or None"""
    par = []
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 5: continue
        if horiz and abs(dy) > 0.02 * Ln + 0.1: continue
        if not horiz and abs(dx) > 0.02 * Ln + 0.1: continue
        off = (l["y0"] - py) if horiz else (l["x0"] - px)
        a0, a1 = (min(l["x0"], l["x1"]), max(l["x0"], l["x1"])) if horiz else (min(l["y0"], l["y1"]), max(l["y0"], l["y1"]))
        c_along = px if horiz else py
        if not (a0 - 12 <= c_along <= a1 + 12): continue
        if abs(off) <= bw + 6: par.append(off)
    neg = [o for o in par if o < 0]; pos = [o for o in par if o > 0]
    if neg and pos and (min(pos) - max(neg)) <= bw + 6: return max(neg), min(pos)
    return None

def beam_length2(G, t, b_cm, segs=None):
    """beam clear length; handles labels inside the beam and leader labels (segs = thin solid segments)."""
    cx, cy = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
    bw = b_cm / 100 * S
    horiz = abs(t["dir"][1]) < 0.2
    br = bracket(G, cx, cy, horiz, bw)
    px, py = cx, cy; how = "inside"
    if br is None and segs:
        end = follow_leader(t, segs)
        if end:
            px, py = end; how = "leader"
            brH = bracket(G, px, py, True, bw); brV = bracket(G, px, py, False, bw)
            if brH and not brV: horiz = True; br = brH
            elif brV and not brH: horiz = False; br = brV
            elif brH and brV: horiz = (brH[1] - brH[0]) <= (brV[1] - brV[0]); br = brH if horiz else brV
    if br:
        if horiz: py = py + (br[0] + br[1]) / 2
        else: px = px + (br[0] + br[1]) / 2
    ux, uy = (1, 0) if horiz else (0, 1)
    obst = [Polygon(c).exterior for c in G["columns"]] + [LineString(c) for c in G.get("open17", []) if len(c) > 1]
    for seg in merged_runs(G, not horiz):   # perpendicular runs, merged across junction gaps
        obst.append(LineString(seg))
    def cast(sign):
        ray = LineString([(px, py), (px + sign * ux * 3000, py + sign * uy * 3000)])
        best = None
        for o in obst:
            inter = ray.intersection(o)
            if inter.is_empty: continue
            pts = []
            if inter.geom_type == "Point": pts = [inter]
            elif inter.geom_type == "MultiPoint": pts = list(inter.geoms)
            else:
                for g in getattr(inter, "geoms", [inter]): pts += [Point(c) for c in g.coords]
            for q in pts:
                d = math.hypot(q.x - px, q.y - py)
                if d > 1.0 and (best is None or d < best[0]): best = (d, q)
        return best
    a = cast(+1); b = cast(-1)
    if not a or not b: return None, (px, py), horiz, how, br, None
    return (a[0] + b[0]) / S, (px, py), horiz, how, br, ((b[1].x, b[1].y), (a[1].x, a[1].y))

def merged_runs(G, horizontal, gap=20.0):
    """0.85 solid black segments, axis-aligned, merged along collinear runs across gaps <= gap."""
    import collections
    groups = collections.defaultdict(list)
    for l in G["lines"]:
        if l["w"] != 0.85 or l.get("dashed") or l["blue"]: continue
        dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; Ln = math.hypot(dx, dy)
        if Ln < 3: continue
        if horizontal and abs(dy) <= 0.02 * Ln + 0.1: groups[round(l["y0"] * 2) / 2].append((min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
        elif (not horizontal) and abs(dx) <= 0.02 * Ln + 0.1: groups[round(l["x0"] * 2) / 2].append((min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
    runs = []
    for k, ivs in groups.items():
        ivs.sort(); cur = list(ivs[0])
        for a_, b_ in ivs[1:]:
            if a_ <= cur[1] + gap: cur[1] = max(cur[1], b_)
            else: runs.append((k, cur[0], cur[1])); cur = [a_, b_]
        runs.append((k, cur[0], cur[1]))
    return [([(a_, k), (b_, k)] if horizontal else [(k, a_), (k, b_)]) for k, a_, b_ in runs]

```

## sheet_s2.py
```python
"""Σ2 – Ξυλότυπος οροφής υπογείου (+0,05/+0,30): clean, fully dimensioned, 1:75 A3."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels, beam_length2, thin_solid_segments

DIR = os.environ.get("DIR", "../s2")          # data directory (../s2 = original Σ2, ../s2r = revision 24/09/2026)
A2 = os.environ.get("A2") == "1"            # A2 sheet at 1:50 (carpenter's version) instead of A3 at 1:75
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 40)); OY = float(os.environ.get("OY_MM", 30))
OUT = os.environ.get("OUT", DIR + "/S2_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

sh = Sheet(DIR + "/geometry.json", DIR + "/texts.json", scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G, T = sh.G, sh.T
sh.draw_geometry(rehatch_columns=False)
lab = parse_labels(T, G["region"])
segs = thin_solid_segments(DIR + "/" + os.environ.get("PDF", "S2.pdf"), G["region"])

# ------------------------------------------------------------------ perimeter chains (source coords)
top = sh.Y(528.46)
xsN = [906.86, 932.51, 1248.28, 1276.77, 1562.92, 1591.41, 1735.97, 1764.32, 2133.95, 2159.88]
extN = {906.86: 535.40, 932.51: 535.5, 1248.28: 533.42, 1276.77: 533.42, 1562.92: 531.58, 1591.41: 531.58, 1735.97: 530.73, 1764.32: 530.73, 2133.95: 528.46, 2159.88: 528.46}
sh.hchain(xsN, top - ROW, -1, ext=extN, narrow_perp=True)
axN = [919.69, 1262.53, 1577.17, 1750.15, 2146.92]
sh.hchain(axN, top - 2 * ROW, -1, ext={919.69: 535.4, 1262.53: 533.42, 1577.17: 531.58, 1750.15: 530.73, 2146.92: 528.46}, narrow_perp=True)
sh.hchain([906.86, 2159.88], top - 3 * ROW, -1)
bot = sh.Y(1493.94)
xsS = [1115.06, 1134.90, 1149.07, 1367.48, 1395.82, 1724.63, 1752.98, 1945.59, 1959.77, 2145.14, 2173.49]
extS = {x: 1493.94 for x in xsS}; extS[1115.06] = 1476.93
sh.hchain(xsS, bot + ROW, +1, ext=extS, narrow_perp=True)
axS = [1132.07, 1381.65, 1738.81, 1952.68, 2159.32]
sh.hchain(axS, bot + 2 * ROW, +1, ext={x: 1493.94 for x in axS}, narrow_perp=True)
sh.hchain([1115.06, 1134.90, 2173.49], bot + 3 * ROW, +1, narrow_perp=True)
xsSW = [907.99, 933.50, 1103.72, 1115.06]
sh.hchain(xsSW, sh.Y(1153.79) + ROW, +1, ext={907.99: 1153.79, 933.50: 1153.79, 1103.72: 1153.79, 1115.06: 1165.12}, narrow_perp=True)
sh.hchain([907.99, 1115.06], sh.Y(1153.79) + 2 * ROW, +1)
west = sh.X(906.86)
ysW = [535.40, 546.89, 561.06, 688.19, 699.53, 823.26, 834.60, 881.65, 910.01, 1128.13, 1153.79]
sh.vchain(ysW, west - ROW, -1, ext={y: 906.86 for y in ysW}, narrow_h=True)
axW = [548.23, 693.86, 828.93, 895.83, 1140.96]
sh.vchain(axW, west - 2 * ROW, -1, ext={y: 906.86 for y in axW}, narrow_h=True)
sh.vchain([535.40, 1153.79], west - 3 * ROW, -1)
east = sh.X(2173.49)
ysE = [528.46, 554.26, 787.97, 816.60, 1020.55, 1049.04, 1173.62, 1202.11, 1289.56, 1318.19, 1417.40, 1445.90, 1479.77, 1493.94]
extE = {528.46: 2159.88, 554.26: 2159.88, 787.97: 2163.71, 816.60: 2163.71, 1020.55: 2167.11, 1049.04: 2167.11, 1173.62: 2169.24, 1202.11: 2169.24,
        1289.56: 2170.94, 1318.19: 2170.94, 1417.40: 2172.78, 1445.90: 2172.78, 1479.77: 2173.49, 1493.94: 2173.49}
sh.vchain(ysE, east + ROW, +1, ext=extE, narrow_h=True)
axE = [541.36, 802.29, 1034.80, 1187.87, 1303.88, 1431.65, 1486.86]
sh.vchain(axE, east + 2 * ROW, +1, ext={541.36: 2159.88, 802.29: 2163.71, 1034.80: 2167.11, 1187.87: 2169.24, 1303.88: 2170.94, 1431.65: 2172.78, 1486.86: 2173.49}, narrow_h=True)
sh.vchain([528.46, 1493.94], east + 3 * ROW, +1)

# ------------------------------------------------------------------ interior locating chains (walls / beams / columns inside the plan)
# H1 (north half, y=770): W wall inner face -> Δ6.1/Κ1 line -> Δ9.5/Κ3 line
sh.hchain([921.5, 1248.43, 1265.44, 1735.97, 1752.98], sh.Y(770.0), -1, size=6.6, narrow_perp=True)
# H2 (south half, y=1386): wall Κ20-Κ19 -> Δ23.1 -> Δ24.1 -> core line Κ17
sh.hchain([1129.23, 1378.80, 1395.82, 1735.97, 1752.98, 1945.59, 1959.77], sh.Y(1386.0), -1, size=6.6, narrow_perp=True)
# V1 (x=1405): N wall inner face -> Δ1.1 -> Δ3.1 -> Δ4.3 ;  V1b (x=1600): Δ4.3 -> S wall inner face
sh.vchain([546.7, 646.52, 663.53, 893.00, 910.01, 1136.60, 1153.60], sh.X(1405.0), +1, size=6.6, narrow_h=True)
sh.vchain([1153.60, 1479.77], sh.X(1600.0), +1, size=6.6, narrow_h=True)
# V2 (x=1900): core bottom face -> Δ12.1 (position of the beam below the core)
sh.vchain([907.17, 1048.90, 1063.10], sh.X(1900.0), +1, size=6.6, narrow_h=True)
# V3 (x=2122): east strip – N wall inner face -> Δ21.1 -> strip -> beams/strips between the east-wall columns -> S wall inner face
sh.vchain([544.8, 788.26, 805.26, 845.09, 1020.55, 1031.80, 1173.62, 1182.13, 1289.84, 1304.02, 1434.40, 1445.80, 1479.77], sh.X(2122.0), +1, size=6.6, narrow_h=True)
# V4 (x=1060): west band – N wall inner face -> Δ8.1 -> south wall of the SW wing
sh.vchain([548.5, 893.00, 910.01, 1139.60, 1153.79], sh.X(1060.0), -1, size=6.6, narrow_h=True)
# perimeter wall thickness (0.25) – one dimension across each wall, written inside the wall band
sh.hchain([907.3, 921.5], sh.Y(760.0), -1, size=6.4, narrow_perp=True, mask=True)       # W wall
sh.vchain([534.6, 548.7], sh.X(1100.0), -1, size=6.4, narrow_h=True, mask=True)         # N wall
sh.hchain([2147.8, 2161.95], sh.Y(700.0), -1, size=6.4, narrow_perp=True, mask=True)    # E wall
sh.vchain([1479.77, 1493.94], sh.X(1250.0), -1, size=6.4, narrow_h=True, mask=True)     # S wall
# core (Κ4/Κ5/Κ6) inner clear dimensions
sh.hchain([1843.54, 1945.59], sh.Y(850.0), -1, size=6.6)
sh.vchain([802.42, 892.99], sh.X(1930.0), -1, size=6.6)

# ------------------------------------------------------------------ designer's interior dimensions (recovered)
dims = json.load(open(DIR + "/dims.json"))
FOOT = (900, 525, 2180, 1500)
SKIP_DIMS = {("3.65", 1011, 1189), ("4.35", 1396, 770)}   # covered by the SW chain (0.45 | 3.00 | 0.20 = 3.65) and by V1 (4.05 + 0.30 = 4.35)
TPOS = {("0.20", 2007, 1201): (2016.5, 1213.5)}        # 20 cm wall: value written beside the wall instead of across it
for d in dims:
    if d.get("unresolved"): continue
    if not (FOOT[0] <= d["x0"] <= FOOT[2] and FOOT[1] <= d["y0"] <= FOOT[3] and FOOT[0] <= d["x1"] <= FOOT[2] and FOOT[1] <= d["y1"] <= FOOT[3]): continue
    key = (d["value"], round(d["tx"]), round(d["ty"]))
    if key in SKIP_DIMS: continue
    sh.dim_generic(d["x0"], d["y0"], d["x1"], d["y1"], d["value"], text_side=d["side"], size=6.4, tpos=TPOS.get(key))
# designer's dims that the automatic recovery could not resolve (verified against the drawing lines):
sh.dim_generic(2142.0, 788.26, 2142.0, 845.09, "1.01", text_side=-1, size=6.4, narrow_h=False)      # beam top -> strip bottom (designer: 1.01 at the east wall)
sh.dim_generic(2053.9, 1173.62, 2053.9, 1182.13, "0.15", text_side=-1, size=6.0, tpos=(2056.5, 1171.0))   # strip 1173.62-1182.13
sh.dim_generic(2049.6, 1295.51, 2049.6, 1304.02, "0.15", text_side=-1, size=6.0, tpos=(2052.5, 1313.5))   # strip 1295.51-1304.02
sh.dim_generic(2014.5, 975.2, 2014.5, 980.86, "0.10", text_side=-1, size=6.0)                        # 1.20 + 0.10 = 1.30 at the K6 leg

# ------------------------------------------------------------------ column labels
COL_POS = {  # name -> (x, y_baseline, rot)   (perimeter columns moved inside the building)
    "Κ11": (938.0, 570.0, 0), "Κ12": (1282.0, 570.0, 0), "Κ13": (1596.0, 570.0, 0), "Κ14": (1676.0, 561.0, 0), "Κ15": (2040.0, 580.0, 0),
    "Κ25": None, "Κ24": (966.0, 698.0, 0), "Κ23": (966.0, 833.0, 0), "Κ22": (930.0, 886.0, 0), "Κ21": (940.0, 1123.0, 0),
    "Κ19": (1153.0, 1473.0, 0), "Κ30": (1399.0, 1473.0, 0), "Κ31": (1757.0, 1473.0, 0), "Κ28": (2082.0, 1510.0, 0),
    "Κ16": (2062.0, 861.0, 0), "Κ34": (2040.0, 1330.0, 0), "Κ26": (2040.0, 1412.0, 0), "Κ1": (1194.0, 631.5, 0),
    "Κ18": (1966.0, 1462.0, 0), "Κ5": (1962.0, 828.0, 0), "Κ3": (1676.0, 802.0, 0),
}
K25_POS = {930: (966.0, 526.0, 0), 2176: (2092.0, 1046.0, 0)}   # two different K25 labels (planted 95/20 at the west wall, 25/50 at the east wall)
K32_POS = {1896: (1888.0, 1186.0, 0), 1960: (1888.0, 1186.0, 0), 2176: (2040.0, 1198.0, 0)}   # inner label (x0 1896 orig. / 1960 rev.), outer label
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", t["text"].strip()); name = s.split()[0]
    pos = None
    if name == "Κ25": pos = K25_POS.get(round(t["x0"]))
    elif name == "Κ32": pos = K32_POS.get(round(t["x0"]))
    elif name in COL_POS: pos = COL_POS[name]
    if pos is None: pos = (t["x0"], t["y1"] - 1.5, 0)
    sh.col_label(pos[0], pos[1], s, rot=pos[2], size=7.6)
sh.col_label(1136.0, 1186.0, "Κ20  30/45/25/50", size=7.6)   # label split in two spans in the source ('Κ' + '20  30/45/25/50')

# ------------------------------------------------------------------ beam labels (centred on the beam's clear span, avoiding blue planted elements)
def best_slot(G, horiz, perp, a0, a1, w_src, bw, margin=4.0):
    """centre of the longest blue-free interval along the beam that fits the label; None if none fits."""
    occ = []
    for l in G["lines"]:
        if not l["blue"] or l["w"] < 0.57: continue
        if horiz:
            if min(l["y0"], l["y1"]) - bw <= perp <= max(l["y0"], l["y1"]) + bw or abs(l["y0"] - perp) <= bw:
                occ.append((min(l["x0"], l["x1"]) - margin, max(l["x0"], l["x1"]) + margin))
        else:
            if min(l["x0"], l["x1"]) - bw <= perp <= max(l["x0"], l["x1"]) + bw or abs(l["x0"] - perp) <= bw:
                occ.append((min(l["y0"], l["y1"]) - margin, max(l["y0"], l["y1"]) + margin))
    occ = [o for o in occ if o[1] > a0 and o[0] < a1]
    occ.sort(); free = []; cur = a0
    for o0, o1 in occ:
        if o0 > cur: free.append((cur, min(o0, a1)))
        cur = max(cur, o1)
    if cur < a1: free.append((cur, a1))
    free = [f for f in free if f[1] - f[0] >= w_src + 2]
    if not free: return None
    f = max(free, key=lambda f: f[1] - f[0])
    return (f[0] + f[1]) / 2

L_OVERRIDE = {"Δ2.1": 1.35, "Δ21.1": 3.34}
POS_OVERRIDE = {"Δ21.1": (1964.0, 802.5, 0, 6.4), "Δ4.4": (1824.0, 1132.0, 0, 6.4), "Δ8.1": (1100.0, 907.5, 0, 6.4),
                "Δ10.1": (1836.0, 891.0, 90, 5.8), "Δ17.1": (1576.0, 644.0, 90, 6.0)}
MULTI_LINE = {"Δ2.1": (1758.0, 757.0, 6.0)}   # label in three lines above the beam (no room beside the planted elements)
for t in lab["beams"]:
    s = re.sub(r"\s+", " ", t["text"].strip())
    m = re.match(r"^Δ\s*(\d+\.\d+)\s+(\d+)/(\d+)\s*(.*)$", s)
    name, b, h, rest = "Δ" + m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()
    L = L_OVERRIDE.get(name); ends = None; horiz = abs(t["dir"][1]) < 0.2
    if L is None:
        L, c, horiz, how, br, ends = beam_length2(G, t, b, segs)
    txt = "%s  %d/%s%s  L=%s" % (name, b, h, ("  " + rest) if rest else "", ("%.2f" % L) if L else "?")
    if name in MULTI_LINE:
        x, y, size = MULTI_LINE[name]; lh = size * 1.25 / sh.K
        parts = [name, "%d/%s" % (b, h)] + ([rest] if rest else []) + ["L=%s" % (("%.2f" % L) if L else "?")]
        for i, p in enumerate(parts): sh.beam_label(x, y + i * lh, p, size=size)
        continue
    if name in POS_OVERRIDE:
        x, y, rot, size = POS_OVERRIDE[name]
    else:
        size = 6.4; c = None
        if ends:
            a0 = min(ends[0][0], ends[1][0]) if horiz else min(ends[0][1], ends[1][1])
            a1 = max(ends[0][0], ends[1][0]) if horiz else max(ends[0][1], ends[1][1])
            perp = (t["y0"] + t["y1"]) / 2 if horiz else (t["x0"] + t["x1"]) / 2
            for size in (6.4, 6.0, 5.6, 5.2):
                w_src = sh.tw(txt, size) / sh.K   # text length in source pt
                c = best_slot(G, horiz, perp, a0, a1, w_src, b / 100 * S)
                if c is not None: break
            if c is None: size = 6.4; w_src = sh.tw(txt, size) / sh.K; c = (a0 + a1) / 2; print("NO FREE SLOT for", name)
            if horiz: x, y, rot = c - w_src / 2, t["y1"] - 1.5, 0
            else: x, y, rot = t["x1"] - 1.0, c + w_src / 2, 90
        elif horiz: x, y, rot = t["x0"], t["y1"] - 1.5, 0
        else: x, y, rot = t["x1"] - 1.0, t["y1"], 90
    sh.beam_label(x, y, txt, rot=rot, size=size)

# strengthened zones
EZ_POS = {(1785, 895): (1760.0, 903.5, 0)}
for t in lab["ez"]:
    s = re.sub(r"\s+", "  ", t["text"].strip())
    key = (round(t["x0"]), round(t["y0"]))
    if key in EZ_POS:
        x, y, rot = EZ_POS[key]; sh.beam_label(x, y, s, rot=rot, size=6.2); continue
    vert = abs(t["dir"][1]) >= 0.2
    if vert: sh.beam_label(t["x1"] - 1.0, t["y1"], s, rot=90, size=6.2)
    else: sh.beam_label(t["x0"], t["y1"] - 1.5, s, size=6.2)

# slabs
def nearest(items, cx, cy, maxd=60):
    best = None
    for t in items:
        d = math.hypot((t["x0"] + t["x1"]) / 2 - cx, (t["y0"] + t["y1"]) / 2 - cy)
        if d < maxd and (best is None or d < best[0]): best = (d, t)
    return best[1] if best else None
CIRC_MOVE = {(2055, 825): (2034.0, 819.5), (1500, 778): (1470.0, 805.0), (1414, 598): (1372.0, 598.0)}   # Π15 out of the planted element; Π3/Π12 off the interior chains
for c in G["circles"]:
    pt = nearest(lab["slabs"], c["cx"], c["cy"], 40); ht = nearest(lab["hs"], c["cx"], c["cy"], 40)
    name = pt["text"].strip() if pt else "Π"; h = re.sub(r"\D", "", ht["text"]) if ht else "?"
    cx, cy = CIRC_MOVE.get((round(c["cx"]), round(c["cy"])), (c["cx"], c["cy"]))
    sh.slab_label(cx, cy, name, h, r=2.8 * MM)

# levels
LEV_MOVE = {(1794, 1382): (1794.0, 1370.0)}   # -0,55 (Π19): clear of the interior chain H2
for t in lab["levels"]:
    s = t["text"].strip(); blue = t["color"] not in (0, 0x000000); vert = abs(t["dir"][1]) >= 0.2
    if blue:
        if vert: sh.stext(t["x1"] - 1.0, t["y1"], s, size=6.6, bold=True, rot=90, color=BLUE)
        else: sh.stext(t["x0"], t["y1"] - 1.5, s, size=6.6, bold=True, color=BLUE)
    else:
        if vert: sh.level_mark(t["x1"] - 6.0, t["y1"] + 8.0, s, r=1.3 * MM, rot=90, textpos=(sh.X(t["x1"]) - 1.5, sh.Y(t["y1"])))
        else:
            x0, y1 = LEV_MOVE.get((round(t["x0"]), round(t["y1"])), (t["x0"], t["y1"]))
            sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)

# notes
NOTES = [(1210.0, 1236.0, ["Γέμισμα μέχρι τη στ. +0,30"], 6.0, 0),
         (1762.0, 630.0, ["Γέμισμα μέχρι", "τη στ. +0,30"], 6.0, 0),
         (1966.0, 1040.0, ["Τμήμα τοιχείου έως το", "ύψος της σκάλας."], 6.0, 0),
         (1578.0, 1128.0, ["Πλάκα επί του φελιζόλ h=18 cm."], 6.0, 90),
         (1622.0, 1240.0, ["Φελιζόλ"], 6.0, 90)]
for x, y, lines, size, rot in NOTES: sh.note(x, y, lines, size=size, rot=rot)

# ------------------------------------------------------------------ title
LEVELS = os.environ.get("LEVELS", "+0,05 / +0,30"); REV = os.environ.get("REV", "")
if A2:
    TB = sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ (%s)" % LEVELS] + (["αναθ. %s" % REV] if REV else []),
                      ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
    sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΟΡΟΦΗΣ", "ΥΠΟΓΕΙΟΥ (+0,05 / +0,30)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                    ["Εγκεκριμένο σχέδιο Σ2", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ2 – ΓΕΩΜΕΤΡΙΑ 1:%d" % SCALE, width_mm=420 - 8 - TITLE_X,
                    legend=["Διαστάσεις σε m · b/h σε cm", "h πλάκας σε cm", "L = καθαρό μήκος δοκού", "μεταξύ παρειών στηρίξεων", "Ανεστρ. = ανεστραμμένη δοκός", "Οπλισμοί κατά Σ2"])
sh.save(OUT, meta={"title": "Σ2 – Ξυλότυπος οροφής υπογείου – Γεωμετρία/Διαστασιολόγηση 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts(DIR + "/texts_out.json")
# content bbox (for centering)
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

```

## sheet_s1.py
```python
"""Σ1 – Ξυλότυπος θεμελίωσης (-4,00 / -3,60): clean, fully dimensioned, 1:75 A3 (page 1 = main plan)."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels, beam_length2, thin_solid_segments

A2 = os.environ.get("A2") == "1"            # A2 sheet at 1:50 (carpenter's version) instead of A3 at 1:75
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 32)); OY = float(os.environ.get("OY_MM", 30))
OUT = os.environ.get("OUT", "../s1/S1_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

# ---- texts: merge labels that Fespa split into several spans on one baseline ('Δ' '6.1' '25/50 Ανεστρ.', 'Κ' '7  65/30')
T0 = json.load(open("../s1/texts.json"))
def merge_split(T):
    T = [dict(t) for t in T]
    changed = True
    while changed:
        changed = False
        for p in T:
            if not (abs(p["dir"][1]) < 0.2 and re.match(r"^(Δ|Κ)(\s*\d+\.?\d*)?$", p["text"].strip())): continue
            for t in T:
                if t is p or abs(t["dir"][1]) >= 0.2 or p["fonts"] != t["fonts"]: continue
                if abs(p["y1"] - t["y1"]) < 1.5 and 0 <= t["x0"] - p["x1"] <= 3.5:
                    sep = "" if re.match(r"^(Δ|Κ)$", p["text"].strip()) else " "
                    p["text"] = p["text"].rstrip() + sep + t["text"].lstrip(); p["x1"] = t["x1"]; p["y0"] = min(p["y0"], t["y0"])
                    T.remove(t); changed = True; break
            if changed: break
    return T
T = merge_split(T0)

sh = Sheet("../s1/geometry.json", T, scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G = sh.G
# ramp fill zone (Γέμισμα για ράμπα οχημάτων): the original hatch is interrupted by the (removed) rebar labels -> re-hatched uniformly
from shapely.geometry import Polygon as _Poly, Point as _Pt
RAMP = [(1645.48, 796.9), (1835.2, 796.9), (1837.52, 966.84), (1645.48, 966.84)]
_ramp = _Poly(RAMP)
sh.draw_geometry(rehatch_columns=False, drop=lambda l: l.get("hatch") and _ramp.contains(_Pt((l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2)))
sh.hatch_polygon(RAMP, spacing=3.2, w=0.18)
lab = parse_labels(T, G["region"])
segs = thin_solid_segments("../s1/S1.pdf", G["region"])

# ------------------------------------------------------------------ perimeter chains (source coords)
# North (outer face skewed: K11 530.02 -> K15 522.93)
top = sh.Y(522.93)
xsN = [592.58, 618.22, 934.00, 962.35, 1248.64, 1276.99, 1421.55, 1450.03, 1819.81, 1845.32]
extN = {592.58: 530.02, 618.22: 529.88, 934.00: 527.89, 962.35: 527.89, 1248.64: 526.05, 1276.99: 526.05, 1421.55: 525.20, 1450.03: 525.20, 1819.81: 523.07, 1845.32: 522.93}
sh.hchain(xsN, top - ROW, -1, ext=extN, narrow_perp=True)
axN = [605.40, 948.18, 1262.82, 1435.79, 1832.78]
sh.hchain(axN, top - 2 * ROW, -1, ext={605.40: 529.95, 948.18: 527.89, 1262.82: 526.05, 1435.79: 525.20, 1832.78: 523.0}, narrow_perp=True)
sh.hchain([592.58, 1845.32], top - 3 * ROW, -1)
# South (outer face 1488.41; strip corner 783.76, K19 notch 820.61, X-block 1645.48-1677.2)
bot = sh.Y(1488.41)
xsS = [783.76, 800.77, 820.61, 834.79, 1053.05, 1081.40, 1410.21, 1438.56, 1631.31, 1645.48, 1677.20, 1831.01, 1859.35]
extS = {x: 1488.41 for x in xsS}; extS[800.77] = 1471.40
sh.hchain(xsS, bot + ROW, +1, ext=extS, narrow_perp=True)
axS = [817.78, 1067.23, 1424.39, 1638.40, 1845.18]
sh.hchain(axS, bot + 2 * ROW, +1, ext={x: 1488.41 for x in axS}, narrow_perp=True)
sh.hchain([783.76, 820.61, 1859.35], bot + 3 * ROW, +1, narrow_perp=True)
# South-west wing (strip bottom 1165.26) : 0.45 | 2.90 | 0.30  and 3.65 (designer)
ysw = sh.Y(1165.26)
sh.hchain([593.71, 619.21, 783.76, 800.77], ysw + ROW, +1, ext={593.71: 1165.26, 619.21: 1148.26}, narrow_perp=True)
sh.hchain([593.71, 800.77], ysw + 2 * ROW, +1)
# thickness of the strip / wall between K20 and K19 (designer: 0.30 at y=1441)
sh.hchain([783.76, 800.77, 814.94], sh.Y(1441.0), -1, size=6.4, narrow_perp=True)
# West
west = sh.X(592.58)
ysW = [529.88, 555.53, 875.98, 904.48, 1122.74, 1134.08, 1148.26, 1165.26, 1488.27]
extW = {529.88: 592.58, 555.53: 592.58, 875.98: 593.14, 904.48: 593.14, 1122.74: 593.57, 1134.08: 593.57, 1148.26: 593.71, 1165.26: 593.71, 1488.27: 783.76}
sh.vchain(ysW, west - ROW, -1, ext=extW, narrow_h=True)
axW = [542.78, 890.23, 1135.50]
sh.vchain(axW, west - 2 * ROW, -1, ext={542.78: 592.58, 890.23: 593.14, 1135.50: 593.6}, narrow_h=True)
sh.vchain([529.88, 1148.26, 1165.26, 1488.27], west - 3 * ROW, -1, narrow_h=True)
# East (outer face skewed: K15 1845.75 -> K28 1859.35); rows pushed out to leave room for the wall note
east = sh.X(1859.35); E0 = (14.0 if A2 else 12.0) * MM
ysE = [522.93, 548.73, 782.45, 811.07, 966.84, 995.32, 1015.03, 1043.51, 1167.95, 1196.59, 1284.04, 1312.52, 1411.88, 1440.37, 1474.24, 1488.41]
extE = {522.93: 1845.32, 548.73: 1845.75, 782.45: 1849.43, 811.07: 1849.43, 966.84: 1852.12, 995.32: 1852.12, 1015.03: 1852.83, 1043.51: 1852.83,
        1167.95: 1855.10, 1196.59: 1855.10, 1284.04: 1856.80, 1312.52: 1856.80, 1411.88: 1858.64, 1440.37: 1858.64, 1474.24: 1859.35, 1488.41: 1859.35}
sh.vchain(ysE, east + E0, +1, ext=extE, narrow_h=True)
axE = [535.83, 796.76, 981.08, 1029.27, 1182.27, 1298.28, 1426.13, 1481.33]
sh.vchain(axE, east + E0 + ROW, +1, ext={535.83: 1845.5, 796.76: 1849.43, 981.08: 1852.12, 1029.27: 1852.83, 1182.27: 1855.10, 1298.28: 1856.80, 1426.13: 1858.64, 1481.33: 1859.35}, narrow_h=True)
sh.vchain([522.93, 1488.41], east + E0 + 2 * ROW, +1)

# ------------------------------------------------------------------ interior locating chains (columns / core inside the raft)
# H1 (y=600): W wall inner face -> Κ1 -> Κ2 -> E wall inner face
sh.hchain([607.31, 934.00, 951.01, 1149.43, 1262.81, 1832.3], sh.Y(600.0), -1, size=6.6, narrow_perp=True,
          ext={934.00: 640.99, 951.01: 640.99, 1149.43: 640.99, 1262.81: 640.99})
# H2 (y=968): W wall -> Κ10 -> Κ3 -> core (Κ4/Κ5/Κ6) -> core line
sh.hchain([607.74, 934.00, 985.02, 1421.55, 1438.56, 1515.09, 1645.48], sh.Y(968.0), -1, size=6.6, narrow_perp=True,
          ext={934.00: 904.48, 985.02: 904.48, 1421.55: 904.48, 1438.56: 904.48, 1515.09: 901.64})
# H3 (y=1100): W wall -> Κ20 -> Κ9 -> Κ8 -> Κ7
sh.hchain([607.74, 789.43, 814.94, 968.02, 1081.40, 1398.87, 1438.56, 1608.63, 1631.31], sh.Y(1100.0), -1, size=6.6, narrow_perp=True,
          ext={789.43: 1131.25, 814.94: 1131.25, 968.02: 1131.25, 1081.40: 1131.25, 1398.87: 1128.41, 1438.56: 1128.41, 1608.63: 1131.25})
# V1 (x=1300): N wall inner face -> Κ2 -> S wall inner face ;  V2 (x=1496): N wall -> core / Κ3 -> S wall
sh.vchain([540.1, 640.99, 658.01, 1474.24], sh.X(1300.0), +1, size=6.6, narrow_h=True)
sh.vchain([539.1, 782.73, 901.64, 1474.24], sh.X(1496.0), +1, size=6.6, narrow_h=True, ext={782.73: 1515.09, 901.64: 1515.09})
# perimeter wall thickness (0.25) – one dimension across each wall, written inside the wall band
def wall_faces_v(y):   # x of the two E/W wall face lines crossing height y (nearly vertical 0.85 lines)
    xs = []
    for l in G["lines"]:
        if l["w"] >= 0.85 and not l.get("dashed") and abs(l["x1"] - l["x0"]) < 6 and min(l["y0"], l["y1"]) <= y <= max(l["y0"], l["y1"]):
            xs.append(l["x0"] + (l["x1"] - l["x0"]) * (y - l["y0"]) / ((l["y1"] - l["y0"]) or 1))
    return xs
def wall_faces_h(x):
    ys = []
    for l in G["lines"]:
        if l["w"] >= 0.85 and not l.get("dashed") and abs(l["y1"] - l["y0"]) < 6 and min(l["x0"], l["x1"]) <= x <= max(l["x0"], l["x1"]):
            ys.append(l["y0"] + (l["y1"] - l["y0"]) * (x - l["x0"]) / ((l["x1"] - l["x0"]) or 1))
    return ys
wW = sorted(v for v in wall_faces_v(700.0) if 585 < v < 615); wE = sorted(v for v in wall_faces_v(880.0) if 1825 < v < 1860)
wN = sorted(v for v in wall_faces_h(1100.0) if 520 < v < 560); wS = [1474.24, 1488.41]
sh.hchain([wW[0], wW[-1]], sh.Y(700.0), -1, size=6.4, narrow_perp=True, mask=True)      # W wall
sh.vchain([wN[0], wN[-1]], sh.X(1100.0), -1, size=6.4, narrow_h=True, mask=True)        # N wall
sh.hchain([wE[0], wE[-1]], sh.Y(880.0), -1, size=6.4, narrow_perp=True, mask=True)      # E wall
sh.vchain(wS, sh.X(1250.0), -1, size=6.4, narrow_h=True, mask=True)                     # S wall
# core (Κ4/Κ5/Κ6) inner clear dimensions
sh.hchain([1515.09, 1631.31], sh.Y(872.0), -1, size=6.6)
sh.vchain([796.90, 887.47], sh.X(1618.0), -1, size=6.6)

# ------------------------------------------------------------------ designer's interior dimensions (recovered; rebar-length dims skipped)
dims = json.load(open("../s1/dims.json"))
FOOT = (560, 500, 1880, 1500)
# rebar bar-length dimensions (both ends on bar ends) and dims replaced by the chains -> skipped
SKIP_DIMS = {("1.60", 1343, 559), ("1.15", 1504, 607), ("1.85", 1253, 672), ("1.30", 1132, 855), ("1.60", 1186, 1349), ("1.15", 974, 1398),
             ("1.60", 733, 764), ("1.15", 790, 926), ("0.50", 1038, 1162), ("4.30", 1045, 1026), ("4.65", 1045, 773), ("1.85", 1078, 830), ("1.30", 1162, 1007),
             ("3.65", 697, 1184), ("0.30", 634, 1157), ("0.30", 792, 1433), ("0.81", 1654, 1503), ("5.70", 740, 1310)}
TPOS = {("0.50", 1645, 808): (1661.5, 813.0), ("0.50", 1577, 783): (1587.5, 766.5), ("0.50", 1582, 902): (1592.5, 924.0)}
# snap endpoints to structural lines (arrow-tip detection may return the arrowhead base)
VX = []; HY = []
for l in G["lines"]:
    if l["w"] < 0.85 or l.get("dashed"): continue
    if abs(l["x0"] - l["x1"]) < 0.6: VX.append((l["x0"], min(l["y0"], l["y1"]), max(l["y0"], l["y1"])))
    elif abs(l["y0"] - l["y1"]) < 0.6: HY.append((l["y0"], min(l["x0"], l["x1"]), max(l["x0"], l["x1"])))
for c in G["columns"]:
    n = len(c)
    for i in range(n):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % n]
        if abs(x0 - x1) < 0.6: VX.append((x0, min(y0, y1), max(y0, y1)))
        elif abs(y0 - y1) < 0.6: HY.append((y0, min(x0, x1), max(x0, x1)))
def snap_x(x, y, tol=4.0):
    c = [vx for vx, a, b in VX if abs(vx - x) <= tol and a - 300 <= y <= b + 300]
    return min(c, key=lambda v: abs(v - x)) if c else None
def snap_y(y, x, tol=4.0):
    c = [hy for hy, a, b in HY if abs(hy - y) <= tol and a - 300 <= x <= b + 300]
    return min(c, key=lambda v: abs(v - y)) if c else None
for d in dims:
    if d.get("unresolved"): continue
    if not (FOOT[0] <= d["x0"] <= FOOT[2] and FOOT[1] <= d["y0"] <= FOOT[3] and FOOT[0] <= d["x1"] <= FOOT[2] and FOOT[1] <= d["y1"] <= FOOT[3]): continue
    key = (d["value"], round(d["tx"]), round(d["ty"]))
    if key in SKIP_DIMS: continue
    v = float(d["value"]); x0, y0, x1, y1 = d["x0"], d["y0"], d["x1"], d["y1"]
    if d["dir"] == "H":
        sx0, sx1 = snap_x(x0, y0), snap_x(x1, y1)
        if sx0 is not None and sx1 is not None and abs((sx1 - sx0) / S - v) <= 0.015: x0, x1 = sx0, sx1
    else:
        sy0, sy1 = snap_y(y0, x0), snap_y(y1, x1)
        if sy0 is not None and sy1 is not None and abs((sy1 - sy0) / S - v) <= 0.015: y0, y1 = sy0, sy1
    sh.dim_generic(x0, y0, x1, y1, d["value"], text_side=d["side"], size=6.4, tpos=TPOS.get(key), mask=_ramp.contains(_Pt(d["tx"], d["ty"])))
# designer's dims the automatic recovery could not resolve (verified against the drawing lines)
sh.dim_generic(1795.0, 1167.95, 1795.0, 1176.60, "0.15", text_side=-1, size=6.0, tpos=(1797.0, 1165.5))   # Δ6.1 visible strip
sh.dim_generic(1673.5, 1290.00, 1673.5, 1298.49, "0.15", text_side=-1, size=6.0, tpos=(1676.0, 1308.0))   # Δ7.1 visible strip
sh.dim_generic(1684.88, 1195.2, 1693.40, 1195.2, "0.15", text_side=-1, size=6.0, tpos=(1650.0, 1197.5))   # Δ9.1 visible strip

# ------------------------------------------------------------------ column labels
COL_POS = {  # name -> (x, y_baseline, rot)   (perimeter columns moved inside the building; east wall labels rotated along the wall)
    "Κ11": (624.0, 566.0, 0), "Κ12": (968.0, 558.0, 0), "Κ13": (1282.0, 556.0, 0), "Κ14": (1362.0, 553.0, 0), "Κ15": (1728.0, 564.0, 0),
    "Κ22": (616.0, 884.0, 0), "Κ21": (626.0, 1118.0, 0), "Κ20": (696.0, 1129.0, 0), "Κ10": (846.0, 882.0, 0), "Κ5": (1662.0, 842.0, 0, True), "Κ1": (846.0, 632.0, 0),
    "Κ2": (1150.0, 634.0, 0), "Κ6": (1530.0, 936.0, 0), "Κ31": (1380.0, 1468.0, 0),
    "Κ19": (838.0, 1468.0, 0), "Κ30": (1085.0, 1468.0, 0), "Κ31": (1442.0, 1468.0, 0), "Κ18": (1572.0, 1504.0, 0), "Κ28": (1768.0, 1504.0, 0),
    "Κ16": (1831.0, 778.0, 90), "Κ24": (1831.0, 962.0, 90, True), "Κ25": (1831.0, 1103.0, 90), "Κ32": (1831.0, 1256.0, 90), "Κ34": (1822.0, 1374.0, 90), "Κ26": (1831.0, 1396.0, 90),
    "Κ29": (1571.0, 990.0, 0), "Κ27": (1571.0, 1011.0, 0), "Κ7": (1571.0, 1163.0, 0), "Κ23": (1571.0, 1206.0, 0), "Κ33": (1571.0, 1278.0, 0), "Κ17": (1571.0, 1422.0, 0),
}
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", re.sub(r"^Κ\s+", "Κ", t["text"].strip())); name = s.split()[0]
    pos = COL_POS.get(name)
    if pos is None: pos = (t["x0"], t["y1"] - 1.5, 0)
    sh.col_label(pos[0], pos[1], s, rot=pos[2], size=7.6, mask=(len(pos) > 3 and pos[3]))

# ------------------------------------------------------------------ beam labels
def best_slot(G, horiz, perp, a0, a1, w_src, bw, margin=4.0):
    return (a0 + a1) / 2
L_OVERRIDE = {"Δ6.1": (1840.50 - 1645.48) / S, "Δ7.1": (1842.20 - 1645.48) / S, "Δ9.1": (1284.31 - 1182.27) / S}   # K23->K32, K33->K34, Δ6.1->Δ7.1
POS_OVERRIDE = {"Δ6.1": (1663.0, 1164.0, 0, 6.4), "Δ7.1": (1712.0, 1310.0, 0, 6.4), "Δ9.1": (1696.5, 1282.3, 90, 5.4)}
COMPACT = {"Δ9.1"}   # single-spaced label written inside the beam band (white mask behind it)
for t in lab["beams"]:
    s = re.sub(r"\s+", " ", re.sub(r"^Δ\s+", "Δ", t["text"].strip()))
    m = re.match(r"^Δ\s*(\d+\.\d+)\s+(\d+)/(\d+)\s*(.*)$", s)
    name, b, h, rest = "Δ" + m.group(1), int(m.group(2)), m.group(3), m.group(4).strip()
    L = L_OVERRIDE.get(name); ends = None; horiz = abs(t["dir"][1]) < 0.2; how = "manual"
    if L is None: L, c, horiz, how, br, ends = beam_length2(G, t, b, segs)
    txt = "%s  %d/%s%s  L=%s" % (name, b, h, ("  " + rest) if rest else "", ("%.2f" % L) if L else "?")
    if name in COMPACT: txt = re.sub(r"\s+", " ", txt)
    print("BEAM", txt, how, ends)
    size = 6.4; w_src = sh.tw(txt, size) / sh.K
    if name in POS_OVERRIDE: x, y, rot, size = POS_OVERRIDE[name]
    elif ends and horiz: x, y, rot = (ends[0][0] + ends[1][0]) / 2 - w_src / 2, t["y1"] - 1.5, 0
    elif ends: x, y, rot = t["x1"] - 1.0, (ends[0][1] + ends[1][1]) / 2 + w_src / 2, 90
    elif horiz: x, y, rot = t["x0"], t["y1"] - 1.5, 0
    else: x, y, rot = t["x1"] - 1.0, t["y1"], 90
    sh.beam_label(x, y, txt, rot=rot, size=size, mask=(name in COMPACT))
for t in lab["ez"]:
    s = re.sub(r"\s+", "  ", t["text"].strip())
    vert = abs(t["dir"][1]) >= 0.2
    if s.startswith("Ε.Ζ.  70/80"): sh.beam_label(1463.0, 946.0, s, rot=90, size=6.2); continue   # beside the E.Z. strip, clear of the chains
    if vert: sh.beam_label(t["x1"] - 1.0, t["y1"], s, rot=90, size=6.2)
    else: sh.beam_label(t["x0"], t["y1"] - 1.5, s, size=6.2)

# slabs
def nearest(items, cx, cy, maxd=60):
    best = None
    for t in items:
        d = math.hypot((t["x0"] + t["x1"]) / 2 - cx, (t["y0"] + t["y1"]) / 2 - cy)
        if d < maxd and (best is None or d < best[0]): best = (d, t)
    return best[1] if best else None
CIRC_MOVE = {(1744, 1361): (1780.0, 1390.0)}
for c in G["circles"]:
    pt = nearest(lab["slabs"], c["cx"], c["cy"], 40); ht = nearest(lab["hs"], c["cx"], c["cy"], 40)
    name = pt["text"].strip() if pt else "Π"; h = re.sub(r"\D", "", ht["text"]) if ht else "?"
    cx, cy = CIRC_MOVE.get((round(c["cx"]), round(c["cy"])), (c["cx"], c["cy"]))
    sh.slab_label(cx, cy, name, h, r=2.8 * MM)

# levels: value (Bookman) + tag (Σ.Μ. / Α.Δ.Σ.Ε.) right below it
tags = [t for t in T if t["text"].strip() in ("Σ.Μ.", "Α.Δ.Σ.Ε.")]
LEV_MOVE = {(1212, 975): (1212.0, 1005.0), (1212, 1011): (1212.0, 1041.0)}   # centre pair moved below the chain H2
for t in lab["levels"]:
    s = t["text"].strip()
    tag = nearest(tags, (t["x0"] + t["x1"]) / 2, t["y1"] + 8, 20)
    x0, y1 = LEV_MOVE.get((round(t["x0"]), round(t["y1"])), (t["x0"], t["y1"]))
    sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)
    if tag: sh.stext(x0 + 0.5, y1 + 8.5, tag["text"].strip(), size=5.6)

# notes (rebar parts of the notes omitted)
NOTES = [(1659.0, 640.0, ["Πλάκα κοιτό-", "στρωσης h=40 cm."], 6.0, 0, False),
         (1193.0, 939.0, ["Πλάκα γενικής", "κοιτόστρωσης h=80 cm."], 6.0, 0, False),
         (1182.0, 1255.0, ["Πλάκα κοιτό-", "στρωσης h=40 cm."], 6.0, 0, False),
         (1668.0, 864.0, ["Γέμισμα για ράμπα οχημάτων"], 6.0, 0, True),
         (1721.0, 1341.0, ["Κεκλιμένο τοιχίο για", "στήριξη της πλάκας."], 6.0, 0, False),
         (1884.0, 1300.0, ["Τοιχείο έως το ύψος της πλάκας για στήριξή της."], 5.8, 90, True)]
for x, y, lines, size, rot, mask in NOTES: sh.note(x, y, lines, size=size, rot=rot, mask=mask)
sh.sline(1719.0, 1338.0, 1695.4, 1277.8, 0.3)   # leader of the inclined-wall note (designer's target point)

# ------------------------------------------------------------------ title
if A2:
    TB = sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "(-4,00 / -3,60)"],
                      ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
  sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "(-4,00 / -3,60)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                ["Εγκεκριμένο σχέδιο Σ1", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ1 – ΓΕΩΜΕΤΡΙΑ 1:%d (1/2)" % SCALE, width_mm=420 - 8 - TITLE_X,
                legend=["Διαστάσεις σε m · b/h σε cm", "h πλάκας σε cm", "L = καθαρό μήκος δοκού", "μεταξύ παρειών στηρίξεων", "Ανεστρ. = ανεστραμμένη δοκός", "Σ.Μ. / Α.Δ.Σ.Ε.: στάθμες κατά Σ1", "Οπλισμοί κατά Σ1"])
sh.save(OUT, meta={"title": "Σ1 – Ξυλότυπος θεμελίωσης – Γεωμετρία/Διαστασιολόγηση 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts("../s1/texts_out.json")
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

```

## sheet_s1_sub.py
```python
"""Σ1 – Ξυλότυπος θεμελίωσης υποσταθμού (-6,69): clean, fully dimensioned, 1:75 A3 (page 2 of Σ1)."""
import json, re, os, sys, math
from lib import Sheet, S, MM, BLUE, BLACK, GRAY
from auto import parse_labels

A2 = os.environ.get("A2") == "1"
SCALE = 50 if A2 else 75
PAGE = (594, 420) if A2 else (420, 297)
FS = 1.25 if A2 else 1.0
OX = float(os.environ.get("OX_MM", 150)); OY = float(os.environ.get("OY_MM", 60))
OUT = os.environ.get("OUT", "../s1/S1_sub_clean.pdf")
TITLE_X = float(os.environ.get("TITLE_X", 366))
ROW = (8.5 if A2 else 6.5) * MM

T = json.load(open("../s1/texts.json"))
sh = Sheet("../s1/geom_sub.json", T, scale=SCALE, ox_mm=OX, oy_mm=OY, page_w=PAGE[0], page_h=PAGE[1], fs=FS)
G = sh.G
sh.draw_geometry(rehatch_columns=False)
lab = parse_labels(T, G["region"])

# ------------------------------------------------------------------ perimeter chains
# West wall (x 2468.08) – column faces / axes / overall
west = sh.X(2468.08)
ysW = [966.84, 995.18, 1015.03, 1057.54, 1131.25, 1148.26, 1167.95, 1196.30, 1284.17, 1312.52, 1411.88, 1440.22, 1460.06, 1488.41]
sh.vchain(ysW, west - ROW, -1, ext={y: 2468.08 for y in ysW}, narrow_h=True)
axW = [981.01, 1036.29, 1139.76, 1182.13, 1298.35, 1426.05, 1474.24]
sh.vchain(axW, west - 2 * ROW, -1, ext={y: 2468.08 for y in axW}, narrow_h=True)
sh.vchain([966.84, 1488.41], west - 3 * ROW, -1)
# East wall (skewed: 2688.47 at the top -> 2696.12 at the bottom)
east = sh.X(2696.12)
ysE = [966.84, 995.32, 1015.03, 1043.51, 1167.95, 1196.59, 1284.04, 1312.52, 1411.88, 1440.37, 1474.24, 1488.41]
extE = {966.84: 2688.47, 995.32: 2688.9, 1015.03: 2689.18, 1043.51: 2689.6, 1167.95: 2691.45, 1196.59: 2691.87, 1284.04: 2693.15, 1312.52: 2693.57,
        1411.88: 2694.99, 1440.37: 2695.42, 1474.24: 2696.12, 1488.41: 2696.12}
sh.vchain(ysE, east + ROW, +1, ext=extE, narrow_h=True)
axE = [981.08, 1029.27, 1182.27, 1298.28, 1426.13, 1481.33]
sh.vchain(axE, east + 2 * ROW, +1, ext={981.08: 2688.7, 1029.27: 2689.4, 1182.27: 2691.7, 1298.28: 2693.4, 1426.13: 2695.2, 1481.33: 2696.12}, narrow_h=True)
sh.vchain([966.84, 1488.41], east + 3 * ROW, +1)
# North (top wall outer face 966.84): 0.25 | 3.39 | 0.25  and 3.89 (designer)
top = sh.Y(966.84)
sh.hchain([2468.08, 2482.25, 2674.30, 2688.47], top - ROW, -1, ext={x: 966.84 for x in [2468.08, 2482.25, 2674.30, 2688.47]}, narrow_perp=True)
sh.hchain([2468.08, 2688.47], top - 2 * ROW, -1)
# South (bottom wall outer face 1488.41): 0.25 | 3.27 | 0.50  and 4.02 (designer)
bot = sh.Y(1488.41)
sh.hchain([2468.08, 2482.25, 2667.78, 2696.12], bot + ROW, +1, ext={x: 1488.41 for x in [2468.08, 2482.25, 2667.78, 2696.12]}, narrow_perp=True)
sh.hchain([2468.08, 2696.12], bot + 2 * ROW, +1)
# interior: walls at -3,64 (1015.03-1029.20 and 1426.05-1440.22) and the clear spans between the walls
sh.vchain([966.84, 981.01, 1015.03, 1029.20, 1426.05, 1440.22, 1474.24, 1488.41], sh.X(2600.0), -1, size=6.4, ext={y: 2600.0 for y in []}, narrow_h=True)

# ------------------------------------------------------------------ column labels (inside the walls)
COL_POS = {"Κ29": (2488.0, 990.0), "Κ27": (2488.0, 1052.0), "Κ7": (2488.0, 1145.0), "Κ23": (2488.0, 1191.0), "Κ33": (2488.0, 1307.0), "Κ17": (2488.0, 1422.0), "Κ18": (2488.0, 1470.0),
           "Κ24": (2614.0, 990.0), "Κ25": (2614.0, 1052.0), "Κ32": (2616.0, 1191.0), "Κ34": (2618.0, 1307.0), "Κ26": (2620.0, 1422.0), "Κ28": (2606.0, 1470.0)}
seen = set()
for t in lab["cols"]:
    s = re.sub(r"\s+", "  ", re.sub(r"^Κ\s+", "Κ", t["text"].strip())); name = s.split()[0]
    if name in seen or name not in COL_POS: continue
    seen.add(name); x, y = COL_POS[name]
    sh.col_label(x, y, s, size=7.6)

# levels + notes
for x0, y1, s, tag in [(2562.0, 1145.0, "-6,24", "Σ.Μ."), (2562.0, 1181.0, "-6,69", "Α.Δ.Σ.Ε.")]:
    sh.level_mark(x0 - 10.0, y1 - 4.0, s, r=1.3 * MM, textpos=(sh.X(x0) + 0.5, sh.Y(y1) - 1.5), size=7.0)
    sh.stext(x0 + 0.5, y1 + 8.5, tag, size=5.6)
sh.note(2513.0, 1110.0, ["Πλάκα γενικής", "κοιτόστρωσης h=35 cm."], size=6.0)
sh.note(2531.0, 1062.0, ["Άνω στ. τοιχίου -3,64."], size=6.0); sh.sline(2572.0, 1054.0, 2582.0, 1030.5, 0.3)   # leader to the wall 1015-1029
sh.note(2532.0, 1403.0, ["Άνω στ. τοιχίου -3,64."], size=6.0); sh.sline(2572.0, 1405.5, 2582.0, 1425.0, 0.3)   # leader to the wall 1426-1440
# plan title under the plan
sh.stext(2468.08, 1488.41 + 3 * ROW / sh.K + 10 / sh.K, "ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ ΥΠΟΣΤΑΘΜΟΥ (-6,69)", size=8.0, bold=True)

# ------------------------------------------------------------------ title
if A2:
    sh.title_box(float(os.environ.get("TB_X", 526)), float(os.environ.get("TB_Y", 362)), 60, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "ΥΠΟΣΤΑΘΜΟΥ (-6,69)"],
                 ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ, ΑΡΓΥΡΟΥΠΟΛΗ"], scale_label="ΚΛΙΜΑΚΑ 1:50 (Α2)", bar_m=2)
else:
  sh.title_column(TITLE_X, ["ΞΥΛΟΤΥΠΟΣ ΘΕΜΕΛΙΩΣΗΣ", "ΥΠΟΣΤΑΘΜΟΥ (-6,69)", "ΓΕΩΜΕΤΡΙΑ – ΠΛΗΡΗΣ", "ΔΙΑΣΤΑΣΙΟΛΟΓΗΣΗ", "(ΧΩΡΙΣ ΟΠΛΙΣΜΟΥΣ)"],
                ["Εγκεκριμένο σχέδιο Σ1", "Οριστική μελέτη, 02/2024", "κλ. 1:50 (Fespa)"], "Σ1 – ΓΕΩΜΕΤΡΙΑ 1:%d (2/2)" % SCALE, width_mm=420 - 8 - TITLE_X,
                legend=["Διαστάσεις σε m · b/h σε cm", "Σ.Μ. / Α.Δ.Σ.Ε.: στάθμες κατά Σ1", "Οπλισμοί κατά Σ1"])
sh.save(OUT, meta={"title": "Σ1 – Ξυλότυπος θεμελίωσης υποσταθμού – Γεωμετρία 1:%d" % SCALE})
n, bad = sh.check(); sh.dump_texts("../s1/texts_out_sub.json")
xs = []; ys = []
for r, t in sh.texts_out:
    if (A2 and r.y0 < float(os.environ.get("TB_Y", 362)) * MM - 2) or (not A2 and r.x1 < TITLE_X * MM - 1): xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
print("text bbox mm: %.1f..%.1f x %.1f..%.1f" % (min(xs) / MM, max(xs) / MM, min(ys) / MM, max(ys) / MM))
print("saved", OUT)

```

## zoom.py (έλεγχος)
```python
"""zoom.py out.pdf png x0 y0 x1 y1 [zoom] [ox oy]: crop of the OUTPUT pdf given a SOURCE rectangle (pt) — uses same transform as Sheet."""
import pymupdf, sys, json
pdf, png = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
z = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
meta = json.load(open(pdf + ".meta.json"))
K, OX, OY, SX0, SY0 = meta["K"], meta["OX"], meta["OY"], meta["SX0"], meta["SY0"]
def X(x): return OX + (x - SX0) * K
def Y(y): return OY + (y - SY0) * K
doc = pymupdf.open(pdf); pg = doc[0]
clip = pymupdf.Rect(X(x0), Y(y0), X(x1), Y(y1))
pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip); pix.save(png); print(png, pix.width, pix.height)

```

## probe.py (έλεγχος)
```python
"""probe.py geometry.json texts_out.json x0 y0 x1 y1 : list geometry lines and placed texts intersecting a SOURCE rect."""
import json, sys
from shapely.geometry import box, LineString
G = json.load(open(sys.argv[1])); TO = json.load(open(sys.argv[2]))
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
bb = box(x0, y0, x1, y1)
for l in G["lines"]:
    ln = LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])])
    if ln.intersects(bb):
        print("LINE w=%s%s%s (%.1f,%.1f)-(%.1f,%.1f)" % (l["w"], " blue" if l["blue"] else "", " dashed" if l.get("dashed") else "", l["x0"], l["y0"], l["x1"], l["y1"]))
for c in G["columns"]:
    from shapely.geometry import Polygon
    if Polygon(c).intersects(bb): print("COLUMN", [(round(x), round(y)) for x, y in c])
for r, t in TO:
    if box(*r).intersects(bb): print("TEXT |%s| at (%.0f,%.0f)-(%.0f,%.0f)" % (t, *r))

```

## strip.py (έλεγχος: τι διασχίζει μια υποψήφια αλυσίδα)
```python
"""strip.py geometry.json texts_out.json H|V pos a0 a1 [halfwidth]: what crosses a horizontal (y=pos, x in a0..a1) or vertical strip (x=pos, y in a0..a1)."""
import json, sys, math
from shapely.geometry import box, LineString, Polygon, Point
G = json.load(open(sys.argv[1])); TO = json.load(open(sys.argv[2]))
mode, pos, a0, a1 = sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
hw = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
bb = box(a0, pos - hw, a1, pos + hw) if mode == "H" else box(pos - hw, a0, pos + hw, a1)
items = []
for l in G["lines"]:
    if l.get("hatch"): continue
    ln = LineString([(l["x0"], l["y0"]), (l["x1"], l["y1"])])
    if not ln.intersects(bb): continue
    dx, dy = l["x1"] - l["x0"], l["y1"] - l["y0"]; L = math.hypot(dx, dy)
    perp = (abs(dx) < 0.02 * L + 0.5) if mode == "H" else (abs(dy) < 0.02 * L + 0.5)   # crossing element face (tick position)
    kind = "PERP-FACE" if perp else "ALONG/OBLIQUE"
    items.append(("%s w=%s%s%s (%.1f,%.1f)-(%.1f,%.1f)" % (kind, l["w"], " blue" if l["blue"] else "", " dashed" if l.get("dashed") else "", l["x0"], l["y0"], l["x1"], l["y1"]), min(l["x0"], l["x1"]) if mode == "H" else min(l["y0"], l["y1"])))
for c in G["columns"]:
    if Polygon(c).intersects(bb):
        xs = [p[0] for p in c]; ys = [p[1] for p in c]
        items.append(("COLUMN %.1f-%.1f x %.1f-%.1f" % (min(xs), max(xs), min(ys), max(ys)), min(xs) if mode == "H" else min(ys)))
for c in G.get("circles", []):
    if Point(c["cx"], c["cy"]).buffer(c["r"]).intersects(bb): items.append(("CIRCLE (%.1f,%.1f)" % (c["cx"], c["cy"]), c["cx"] if mode == "H" else c["cy"]))
for r, t in TO:
    if box(*r).intersects(bb): items.append(("TEXT |%s| (%.0f,%.0f)-(%.0f,%.0f)" % (t, *r), r[0] if mode == "H" else r[1]))
for s, k in sorted(items, key=lambda it: it[1]): print(s)

```

## Εκτέλεση
```
cd xyl
python3 ../texts_dump.py ../s2/S2.pdf ../s2/texts.json   # (όπως στο Σ3)
python3 extract.py ../s2/S2.pdf ../s2/geometry.json --region 880 520 2185 1545 --stair 1880 830 2010 990
python3 recover_dims.py ../s2/S2.pdf ../s2/texts.json ../s2/dims.json 880 520 2185 1545
OUT=out.pdf OX_MM=32.75 OY_MM=31.15 python3 sheet_s2.py
python3 extract.py ../s1/S1.pdf ../s1/geometry.json --region 540 470 1900 1520 --keep 1644 1473 1679 1490 1820 1000 1880 1420
python3 extract.py ../s1/S1.pdf ../s1/geom_sub.json --region 2440 940 2730 1520
OUT=p1.pdf OX_MM=22.9 OY_MM=22.3 python3 sheet_s1.py ; OUT=p2.pdf OX_MM=151.4 OY_MM=76.9 python3 sheet_s1_sub.py  # και συνένωση σε 2σέλιδο PDF με pymupdf
```
