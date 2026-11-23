"""Prüft info/prides.json (Pride-/CSD-Termine) und listet, was zu tun ist.

Aufruf: python tools/prides_pruefen.py [--urls]
- Aufbau: Pflichtfelder, Datumsformat, Monat 1–12, Koordinaten
- vorbei: Termine mit Datum, die vorbei sind → nächstes Jahr suchen (Datum leeren, last setzen)
- offen: Termine ohne Datum in den nächsten 6 Monaten → beim Veranstalter nachsehen
- --urls: ruft jede Webseite auf und meldet tote Adressen
Ausgabe als Liste, Rückgabewert 1 bei Aufbaufehlern. © 2026 Timo Feist
"""
import datetime, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(HERE, "info", "prides.json")
d = json.load(open(P, encoding="utf-8"))
items = d.get("items", [])
today = datetime.date.today()
iso = today.isoformat()
err, past, open_soon = [], [], []
seen = set()
for i, e in enumerate(items):
    tag = f"#{i} {e.get('name')} ({e.get('city')})"
    for k in ("name", "city", "cc", "lat", "lon"):
        if e.get(k) in (None, ""):
            err.append(f"{tag}: {k} fehlt")
    st, en = e.get("start") or "", e.get("end") or ""
    for v in (st, en):
        if v and not re.match(r"^\d{4}-\d\d-\d\d$", v):
            err.append(f"{tag}: Datum {v} falsch")
    if not st and not (1 <= int(e.get("month") or 0) <= 12):
        err.append(f"{tag}: weder Datum noch Monat")
    key = (e.get("cc"), e.get("city"), (e.get("name") or "").lower())
    if key in seen:
        err.append(f"{tag}: doppelt")
    seen.add(key)
    if e.get("drop"):
        continue
    if st and (en or st) < iso:
        past.append(tag + f" war {st}")
    if not st and e.get("month"):
        m = int(e["month"])
        diff = (m - today.month) % 12
        if diff <= 6:
            open_soon.append(f"{tag}: üblich Monat {m}, zuletzt {e.get('last') or '?'}")

print(f"{len(items)} Einträge, {sum(1 for e in items if e.get('start'))} mit Datum, Stand {d.get('updated')}")
for title, lst in (("FEHLER", err), ("VORBEI (nächsten Termin suchen)", past), ("OHNE DATUM, IN DEN NÄCHSTEN 6 MONATEN", open_soon)):
    print(f"\n{title}: {len(lst)}")
    for x in lst:
        print("  " + x)

if "--urls" in sys.argv:
    def chk(u):
        try:
            r = subprocess.run(["curl", "-sSL", "-o", os.devnull, "-m", "20", "-A", "Mozilla/5.0", "-w", "%{http_code}", u],
                               capture_output=True, text=True, timeout=40)
            return u, r.stdout.strip() or "000"
        except Exception:
            return u, "000"
    urls = sorted({e["url"] for e in items if e.get("url") and not e.get("drop")})
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(chk, urls))
    bad = [(u, c) for u, c in res if c not in ("200", "403", "429")]
    print(f"\nTOTE ODER FRAGLICHE ADRESSEN: {len(bad)} von {len(urls)}")
    for u, c in bad:
        print(f"  {c} {u}")
sys.exit(1 if err else 0)
