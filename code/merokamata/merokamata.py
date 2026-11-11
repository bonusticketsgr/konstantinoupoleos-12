#!/usr/bin/env python3
"""Καταγραφή μεροκάματων εργοταξίου – Κωνσταντινουπόλεως 12.

Δεδομένα: μεροκάματα/YYYY-MM.csv (ημερομηνία;συνεργείο;άτομα;σημείωση)
Προαιρετικά: μεροκάματα/τιμές.json  {"καλούπια": 70, "σιδεράδες": 80}  (€/μεροκάματο)

Χρήση:
  merokamata.py add 2026-11-11 "καλούπια=5, σιδεράδες=3" [--note "κείμενο"]
  merokamata.py add 2026-11-15 0            # αργία / δεν δούλεψε κανείς
  merokamata.py show 2026-11                # όλες οι μέρες του μήνα
  merokamata.py month 2026-11               # σύνολο μήνα ανά συνεργείο
  merokamata.py year 2026                   # σύνολα ανά μήνα
"""
import csv, json, re, sys
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "μεροκάματα"
RATES = DATA / "τιμές.json"
FIELDS = ["ημερομηνία", "συνεργείο", "άτομα", "σημείωση"]

ALIASES = {
    "καλουπια": "καλούπια", "καλουπατζηδες": "καλούπια", "καλουπατζήδες": "καλούπια", "ξυλοτυποι": "καλούπια",
    "σιδεραδες": "σιδεράδες", "σιδερας": "σιδεράδες", "σιδεράς": "σιδεράδες", "οπλισμος": "σιδεράδες",
    "εργατες": "εργάτες", "εργατης": "εργάτες", "εργάτης": "εργάτες",
    "μπετα": "μπετά", "μπετο": "μπετά", "μπετόν": "μπετά", "σκυροδεμα": "μπετά",
    "κτιστες": "κτίστες", "κτιστης": "κτίστες", "χτιστες": "κτίστες",
    "υδραυλικοι": "υδραυλικοί", "υδραυλικος": "υδραυλικοί",
    "ηλεκτρολογοι": "ηλεκτρολόγοι", "ηλεκτρολογος": "ηλεκτρολόγοι",
    "σοβατζηδες": "σοβατζήδες", "σοβατζης": "σοβατζήδες",
}

def norm_crew(s):
    s = s.strip().lower()
    key = "".join(c for c in __import__("unicodedata").normalize("NFD", s) if not __import__("unicodedata").combining(c))
    return ALIASES.get(key, ALIASES.get(s, s))

def month_file(ym):
    return DATA / f"{ym}.csv"

def read_month(ym):
    f = month_file(ym)
    if not f.exists():
        return []
    with f.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))

def write_month(ym, rows):
    DATA.mkdir(exist_ok=True)
    rows.sort(key=lambda r: (r["ημερομηνία"], r["συνεργείο"]))
    with month_file(ym).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter=";")
        w.writeheader()
        w.writerows(rows)

def parse_crews(text):
    """'καλούπια=5, σιδεράδες 3' -> OrderedDict. '0' -> κενό (αργία)."""
    text = text.strip()
    out = OrderedDict()
    if text in ("0", "-", "", "αργία", "αργια"):
        return out
    for part in re.split(r"[,·;\n]+", text):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s*[=:]?\s*(\d+)\s*(?:άτομα|ατομα|α)?$", part) or re.match(r"^(\d+)\s*(?:άτομα|ατομα)?\s+(.*)$", part)
        if not m:
            sys.exit(f"Δεν κατάλαβα το «{part}» – γράψε π.χ. «καλούπια=5»")
        a, b = m.groups()
        crew, n = (a, b) if a and not a.isdigit() else (b, a)
        out[norm_crew(crew)] = out.get(norm_crew(crew), 0) + int(n)
    return out

def load_rates():
    if RATES.exists():
        return json.loads(RATES.read_text(encoding="utf-8"))
    return {}

def cmd_add(day, crews_text, note=""):
    date.fromisoformat(day)
    ym = day[:7]
    rows = [r for r in read_month(ym) if r["ημερομηνία"] != day]
    crews = parse_crews(crews_text)
    if not crews:
        rows.append({"ημερομηνία": day, "συνεργείο": "-", "άτομα": "0", "σημείωση": note or "αργία"})
    for crew, n in crews.items():
        rows.append({"ημερομηνία": day, "συνεργείο": crew, "άτομα": str(n), "σημείωση": note})
    write_month(ym, rows)
    tot = sum(crews.values())
    print(f"Καταχωρήθηκε {day}: " + (", ".join(f"{c} {n}" for c, n in crews.items()) if crews else "αργία") + f" → {tot} μεροκάματα")

def cmd_show(ym):
    rows = read_month(ym)
    if not rows:
        print(f"Καμία καταχώρηση για {ym}"); return
    byday = defaultdict(list)
    for r in rows:
        byday[r["ημερομηνία"]].append(r)
    for d in sorted(byday):
        rs = byday[d]
        parts = [f"{r['συνεργείο']} {r['άτομα']}" for r in rs if r["συνεργείο"] != "-"]
        tot = sum(int(r["άτομα"]) for r in rs)
        note = next((r["σημείωση"] for r in rs if r["σημείωση"]), "")
        print(f"{d}  {', '.join(parts) if parts else 'αργία':<40} {tot:>3}" + (f"   ({note})" if note else ""))

def month_totals(ym):
    rows = read_month(ym)
    per_crew = defaultdict(int)
    days = set()
    for r in rows:
        days.add(r["ημερομηνία"])
        if r["συνεργείο"] != "-":
            per_crew[r["συνεργείο"]] += int(r["άτομα"])
    workdays = {r["ημερομηνία"] for r in rows if r["συνεργείο"] != "-"}
    return per_crew, days, workdays

def cmd_month(ym):
    per_crew, days, workdays = month_totals(ym)
    rates = load_rates()
    if not days:
        print(f"Καμία καταχώρηση για {ym}"); return
    print(f"ΣΥΝΟΛΟ ΜΗΝΑ {ym}  ({len(days)} μέρες καταγεγραμμένες, {len(workdays)} εργάσιμες)")
    total = 0; euro = 0.0; has_rates = False
    for crew, n in sorted(per_crew.items(), key=lambda kv: -kv[1]):
        line = f"  {crew:<16} {n:>4} μεροκάματα"
        if crew in rates:
            has_rates = True; e = n * float(rates[crew]); euro += e
            line += f"   × {rates[crew]} € = {e:,.0f} €"
        print(line); total += n
    print(f"  {'ΣΥΝΟΛΟ':<16} {total:>4} μεροκάματα" + (f"   = {euro:,.0f} €" if has_rates else ""))

def cmd_year(y):
    files = sorted(DATA.glob(f"{y}-??.csv"))
    if not files:
        print(f"Καμία καταχώρηση για {y}"); return
    grand = 0
    for f in files:
        ym = f.stem
        per_crew, days, workdays = month_totals(ym)
        tot = sum(per_crew.values()); grand += tot
        print(f"{ym}: {tot:>4} μεροκάματα ({len(workdays)} εργάσιμες)  " + ", ".join(f"{c} {n}" for c, n in per_crew.items()))
    print(f"ΣΥΝΟΛΟ {y}: {grand} μεροκάματα")

def main(argv):
    if len(argv) < 2:
        print(__doc__); return
    cmd = argv[1]
    if cmd == "add":
        note = ""
        if "--note" in argv:
            i = argv.index("--note"); note = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
        cmd_add(argv[2], argv[3] if len(argv) > 3 else "0", note)
    elif cmd == "show":
        cmd_show(argv[2])
    elif cmd == "month":
        cmd_month(argv[2])
    elif cmd == "year":
        cmd_year(argv[2])
    else:
        print(__doc__)

if __name__ == "__main__":
    main(sys.argv)
