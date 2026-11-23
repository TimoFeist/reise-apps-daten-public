"""Lädt die gesetzlichen Feiertage aller Länder für dieses und nächstes Jahr von date.nager.at.

Schreibt info/feiertage.json: {"src": ..., "fetched": "JJJJ-MM-TT", "countries": {"DE": [{"d": "2026-12-25", "n": "Erster Weihnachtstag", "e": "Christmas Day"}, ...]}}
"r": 1 heißt: nur in einzelnen Regionen. merge_raw.py hängt die Liste als info.holidays an jedes Land.
Läuft höchstens einmal pro Woche neu (sonst nichts zu tun). © 2026 Timo Feist
"""
import datetime, json, os, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "feiertage.json")
SRC = "https://date.nager.at"
today = datetime.date.today()
old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
if "--force" not in sys.argv and old.get("fetched"):
    if (today - datetime.date.fromisoformat(old["fetched"])).days < 7:
        print("feiertage.json ist aktuell")
        sys.exit(0)


def get(path):
    req = urllib.request.Request(SRC + path, headers={"User-Agent": "LocalAppFinder-Daten/1.0 (+https://localappfinder.uk)"})
    for v in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=30)
            body = r.read().decode("utf-8")
            return json.loads(body) if body.strip() else []
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                return []
            time.sleep(5 * (v + 1))
        except Exception:
            time.sleep(5 * (v + 1))
    return None


avail = {c["countryCode"] for c in (get("/api/v3/AvailableCountries") or [])}
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
res = {}
for c in data["countries"]:
    cc = c["code"]
    if cc not in avail:
        continue
    lst = []
    for y in (today.year, today.year + 1):
        r = get("/api/v3/PublicHolidays/%d/%s" % (y, cc))
        if r is None:  # Fehler: alten Stand behalten
            lst = old.get("countries", {}).get(cc, [])
            break
        for h in r:
            if not set(h.get("types") or []) & {"Public", "Bank"}:
                continue
            e = {"d": h["date"], "n": h.get("localName") or h.get("name", ""), "e": h.get("name", "")}
            if not h.get("global", True):
                e["r"] = 1
            if e["e"] == e["n"]:
                del e["e"]
            if e not in lst:
                lst.append(e)
        time.sleep(0.2)
    if lst:
        res[cc] = lst
json.dump({"src": SRC, "fetched": today.isoformat(), "countries": res},
          open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, separators=(",", ":"))
print("Feiertage für", len(res), "Länder")
