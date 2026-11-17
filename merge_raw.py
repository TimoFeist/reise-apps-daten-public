#!/usr/bin/env python3
"""Führt recherchierte Länderdaten aus raw/<ISO>.json in data.json zusammen.

Regeln:
* data.json ist die Hauptdatei. Nichts wird gelöscht, Einträge mit "mine": true bleiben unverändert.
* Pro Land werden fehlende Apps ergänzt (Abgleich über pkg, sonst über den Namen).
* Apps mit "city" landen in der passenden Stadt (Abgleich über "match"), neue Städte werden angelegt.
* "version" wird auf das übergebene Datum gesetzt.

Aufruf: python3 merge_raw.py 2026-11-17
Format raw/<ISO>.json:
{"src": "https://...", "updated": "...", "note": "Tipp für das Land",
 "apps": [{"name": "", "cat": "", "pkg": "", "ess": true, "note": "", "city": ""}]}
"""
import glob, json, os, sys

import pycountry, gettext  # pip install pycountry

HERE = os.path.dirname(os.path.abspath(__file__))
DE = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["de"])

# Deutsche Namen für Städte (Anzeige). Englischer Name bleibt immer in "match".
EXONYM = {
    "Prague": "Prag", "Copenhagen": "Kopenhagen", "Rome": "Rom", "Milan": "Mailand", "Vienna": "Wien", "Munich": "München",
    "Cologne": "Köln", "Lisbon": "Lissabon", "Brussels": "Brüssel", "Warsaw": "Warschau", "Moscow": "Moskau", "Athens": "Athen",
    "Venice": "Venedig", "Florence": "Florenz", "Naples": "Neapel", "Belgrade": "Belgrad", "Bucharest": "Bukarest",
    "Tokyo": "Tokio", "Beijing": "Peking", "Gothenburg": "Göteborg", "Zurich": "Zürich", "Geneva": "Genf", "Krakow": "Krakau",
    "Kraków": "Krakau", "Seville": "Sevilla", "Nuremberg": "Nürnberg", "The Hague": "Den Haag", "Antwerp": "Antwerpen",
    "Ghent": "Gent", "Bruges": "Brügge", "Turin": "Turin", "Genoa": "Genua", "Saint Petersburg": "Sankt Petersburg",
    "Kyiv": "Kiew", "Mexico City": "Mexiko-Stadt", "Cairo": "Kairo", "Tunis": "Tunis", "Marrakesh": "Marrakesch",
    "Singapore": "Singapur", "Seoul": "Seoul", "Bangkok": "Bangkok", "Hanoi": "Hanoi", "Reykjavik": "Reykjavík",
}

VALID_CATS = None


def flag(code):
    return "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in code.upper()) if len(code) == 2 else "🏳️"


def key(a):
    return (a.get("pkg") or a["name"]).strip().lower()


def clean_app(a, src):
    out = {"name": a["name"].strip(), "cat": a.get("cat") or "misc"}
    if out["cat"] not in VALID_CATS:
        out["cat"] = "misc"
    pkg = (a.get("pkg") or "").strip()
    if pkg and "." in pkg and " " not in pkg:
        out["pkg"] = pkg
    if a.get("note"):
        out["note"] = a["note"].strip()
    if a.get("ess"):
        out["ess"] = True
    if a.get("url"):
        out["url"] = a["url"]
    out["src"] = a.get("src") or src
    return out


def find_city(country, name):
    n = name.strip().lower()
    for c in country["cities"]:
        names = [c["name"].lower()] + [m.lower() for m in c.get("match", [])]
        if n in names:
            return c
    return None


def merge(data, code, raw):
    code = code.upper()
    country = next((c for c in data["countries"] if c["code"] == code), None)
    if country is None:
        pc = pycountry.countries.get(alpha_2=code)
        name = DE.gettext(pc.name) if pc else code
        country = {"code": code, "name": name, "flag": flag(code), "apps": [], "cities": []}
        data["countries"].append(country)
    country.setdefault("cities", [])
    src = raw.get("src")
    if raw.get("note"):
        country["note"] = raw["note"].strip()
    if src:
        country["src"] = src
    added = 0
    for a in raw.get("apps", []):
        app = clean_app(a, src)
        city_name = (a.get("city") or "").strip()
        if city_name:
            city = find_city(country, city_name)
            if city is None:
                display = EXONYM.get(city_name, city_name)
                city = {"name": display, "match": sorted({city_name, display}), "apps": []}
                country["cities"].append(city)
            target = city["apps"]
        else:
            target = country["apps"]
        existing = {key(x): x for x in target}
        k = key(app)
        if k in existing:
            old = existing[k]
            if old.get("mine"):
                if app.get("ess"):
                    old["ess"] = True
                continue
            # Recherchierten Eintrag aktualisieren (Notiz, Kategorie, Paket)
            for f in ("cat", "note", "pkg", "src", "ess"):
                if f in app:
                    old[f] = app[f]
            continue
        # Gleicher Name ohne Paket vorhanden? Dann Paket nachtragen
        same_name = next((x for x in target if x["name"].strip().lower() == app["name"].lower()), None)
        if same_name is not None:
            if "pkg" in app and not same_name.get("pkg"):
                same_name["pkg"] = app["pkg"]
            if app.get("ess"):
                same_name["ess"] = True
            continue
        target.append(app)
        added += 1
    country["cities"].sort(key=lambda c: c["name"])
    return added


def main():
    global VALID_CATS
    version = sys.argv[1] if len(sys.argv) > 1 else None
    path = os.path.join(HERE, "data.json")
    data = json.load(open(path, encoding="utf-8"))
    VALID_CATS = {c["id"] for c in data["categories"]}
    total = 0
    for f in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        code = os.path.splitext(os.path.basename(f))[0]
        raw = json.load(open(f, encoding="utf-8"))
        n = merge(data, code, raw)
        total += n
        print(f"{code}: +{n}")
    if version:
        data["version"] = version
    # Grundprüfung
    for c in data["countries"]:
        assert c["code"] and c["name"] and "apps" in c, c
        for a in c["apps"] + [x for ci in c.get("cities", []) for x in ci["apps"]]:
            assert a["name"] and a["cat"] in VALID_CATS, (c["code"], a)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_apps = sum(len(c["apps"]) + sum(len(ci["apps"]) for ci in c.get("cities", [])) for c in data["countries"])
    print(f"neu: {total} · {len(data['countries'])} Länder · {n_apps} Einträge · Stand {data['version']}")


if __name__ == "__main__":
    main()
