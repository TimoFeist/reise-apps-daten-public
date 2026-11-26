"""Leihräder, E-Scooter, E-Roller und Carsharing aus den offenen GBFS-Daten (General Bikeshare Feed Specification).

Quelle: MobilityData, Liste aller öffentlichen GBFS-Systeme https://github.com/MobilityData/gbfs/blob/master/systems.csv
(Lizenz CC BY 3.0). Für jedes System wird der Feed des Betreibers gelesen: system_information nennt die
offizielle Android-App (rental_apps.android.store_uri), vehicle_types die Fahrzeugarten.
Jeder Paketname wird zusätzlich bei Google Play geprüft (Seite vorhanden, Titel = Anzeigename).

Ergebnis info/gbfs.json:
{"src": "...", "license": "CC BY 3.0", "checked": "JJJJ-MM-TT",
 "systems": [{"id", "cc", "loc", "name", "url", "pkg", "ff": ["bicycle", ...]}],
 "play": {"<paket>": {"t": "<Titel bei Google Play>", "checked": "JJJJ-MM-TT"}}}
merge_raw.py (add_gbfs) macht daraus Einträge "micro"/"carshare" je Land bzw. Stadt und ergänzt die Länderlisten
weltweiter Apps (z. B. Lime, Voi, Bolt). Es werden nur Name, Ort und App-Verweis übernommen, keine Standortdaten.
Aufruf: python3 tools/gbfs.py   © 2026 Timo Feist
"""
import csv, datetime, io, json, os, re, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "gbfs.json")
LIST = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"
UA = {"User-Agent": "LocalAppFinder-Daten/1.0 (+https://localappfinder.uk)"}
UA_PLAY = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}
PKG = re.compile(r"[?&]id=([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)")
TITLE = re.compile(rb'<meta property="og:title" content="([^"]+?)(?: - Apps on Google Play)?"')
today = datetime.date.today().isoformat()
old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}


def get(url, hdr=UA, tries=2):
    for v in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=25).read()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404, 410):
                return None
            time.sleep(3 * (v + 1))
        except Exception:
            time.sleep(2)
    return None


def getj(url):
    b = get(url)
    return json.loads(b) if b else None


def txt(x):
    """GBFS 3.0 liefert Texte als Liste [{"text", "language"}]."""
    if isinstance(x, list):
        return (x[0] or {}).get("text", "") if x else ""
    return x or ""


def feeds(g):
    d = (g or {}).get("data", {})
    if "feeds" in d:
        return d["feeds"]
    for v in d.values():  # GBFS 1.x/2.x: nach Sprache gegliedert
        if isinstance(v, dict) and "feeds" in v:
            return v["feeds"]
    return []


def system(row):
    if row.get("Authentication Type"):
        return None
    try:
        f = {x["name"]: x["url"] for x in feeds(getj(row["Auto-Discovery URL"]))}
        si = (getj(f["system_information"]) or {}).get("data", {})
    except Exception:
        return None
    m = PKG.search(((si.get("rental_apps") or {}).get("android") or {}).get("store_uri", ""))
    if not m:
        return None
    ff = set()
    if "vehicle_types" in f:
        try:
            ff = {v.get("form_factor") for v in (getj(f["vehicle_types"]) or {}).get("data", {}).get("vehicle_types", [])} - {None}
        except Exception:
            pass
    url = row.get("URL") or ""
    return {"id": row["System ID"], "cc": row["Country Code"].upper(), "loc": row["Location"].strip(),
            "name": txt(si.get("name")) or row["Name"], "url": url if url.startswith("http") else "",
            "pkg": m.group(1), "ff": sorted(ff)}


def play(p):
    for gl in ("US", "DE"):
        b = get("https://play.google.com/store/apps/details?id=%s&hl=en&gl=%s" % (p, gl), UA_PLAY, 3)
        if b:
            m = TITLE.search(b)
            if m:
                import html
                return p, html.unescape(m.group(1).decode("utf-8", "replace")).strip()
    return p, None


rows = list(csv.DictReader(io.StringIO(get(LIST).decode("utf-8"))))
print("Systeme in der Liste:", len(rows), flush=True)
with ThreadPoolExecutor(24) as ex:
    systems = [s for s in ex.map(system, rows) if s]
print("mit Android-App:", len(systems), flush=True)
if len(systems) < 0.5 * len(old.get("systems", [])):
    raise SystemExit("Zu wenige Systeme erreichbar, alte Datei bleibt.")

pl = dict(old.get("play", {}))
need = sorted({s["pkg"] for s in systems if s["pkg"] not in pl or pl[s["pkg"]].get("checked", "") < (datetime.date.today() - datetime.timedelta(days=30)).isoformat()})
with ThreadPoolExecutor(6) as ex:
    for p, t in ex.map(play, need):
        if t:
            pl[p] = {"t": t, "checked": today}
        else:
            pl.pop(p, None)  # nicht (mehr) bei Google Play
pl = {p: v for p, v in pl.items() if any(s["pkg"] == p for s in systems)}
print("Pakete bei Google Play:", len(pl), "von", len({s['pkg'] for s in systems}))
json.dump({"src": LIST, "license": "CC BY 3.0, MobilityData", "checked": today,
           "systems": sorted(systems, key=lambda s: (s["cc"], s["loc"], s["id"])), "play": dict(sorted(pl.items()))},
          open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
