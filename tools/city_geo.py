"""Ermittelt die Koordinaten aller Städte aus data.json über die Ortssuche von Open-Meteo (Daten: GeoNames, CC BY 4.0).

Schreibt info/stadt-koordinaten.json: {"cities": {"DE|Berlin": [52.517, 13.389], ...}}
merge_raw.py setzt daraus "ll": [lat, lon] an jeder Stadt (für die Karte in der Web-Version).
Nur neue Städte werden abgefragt, höchstens 1 Abfrage pro Sekunde.
Ortsdaten: GeoNames (geonames.org, CC BY 4.0) über geocoding-api.open-meteo.com. © 2026 Timo Feist
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "stadt-koordinaten.json")
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
res = json.load(open(OUT, encoding="utf-8"))["cities"] if os.path.exists(OUT) else {}
UA = "LocalAppFinder-Daten/1.0 (+https://localappfinder.uk)"


def ask(name, cc):
    q = urllib.parse.urlencode({"name": name, "count": 20, "language": "en"})
    req = urllib.request.Request("https://geocoding-api.open-meteo.com/v1/search?" + q, headers={"User-Agent": UA})
    r = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8")).get("results", [])
    time.sleep(1.1)
    r = [x for x in r if x.get("country_code", "").upper() == cc]
    if not r:
        return None
    best = max(r, key=lambda x: (x.get("population") or 0, x.get("feature_code", "").startswith("PPLC")))
    return [round(best["latitude"], 4), round(best["longitude"], 4)]


neu = 0
for c in data["countries"]:
    if len(c["code"]) != 2 or c["code"] == "WW":
        continue
    for ci in c.get("cities", []):
        key = c["code"] + "|" + ci["name"]
        if key in res:
            continue
        ll = None
        for name in [ci["name"]] + [m for m in ci.get("match", []) if m != ci["name"]]:
            try:
                ll = ask(name, c["code"])
            except Exception as e:
                print("Fehler", key, e)
            if ll:
                break
        if ll:
            res[key] = ll
            neu += 1
        else:
            print("nicht gefunden:", key)
json.dump({"cities": dict(sorted(res.items()))}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
print("neu:", neu, "gesamt:", len(res))
