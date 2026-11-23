#!/usr/bin/env python3
# © 2026 Timo Feist. Alle Rechte vorbehalten.
"""Führt recherchierte Länderdaten aus raw/<ISO>.json in data.json zusammen.

Regeln:
* data.json ist die Hauptdatei. Nichts wird gelöscht, Einträge mit "mine": true bleiben unverändert.
* Pro Land werden fehlende Apps ergänzt (Abgleich über pkg, sonst über den Namen).
* Apps mit "city" landen in der passenden Stadt (Abgleich über "match"), neue Städte werden angelegt.
* "version" wird auf das übergebene Datum gesetzt.
* "use": "ok" | "limited" | "no" und "req" (was als Ausländer nötig ist).
  Apps mit "use": "no" bleiben drin und erscheinen in der App ganz unten unter
  "Nur mit Voraussetzungen". Timos eigene Apps ("mine") bekommen nur den Hinweis.

Aufruf: python3 merge_raw.py            (Version = jetzt, UTC, "JJJJ-MM-TT HH:MM")
        python3 merge_raw.py --check    (nur prüfen, nichts schreiben)
Normalerweise läuft das automatisch per GitHub Action nach jedem Push.
Format raw/<ISO>.json:
{"src": "https://...", "fetched": "JJJJ-MM-TT", "updated": "...", "note": "Tipp für das Land",
 "discontinued": [{"name": "", "pkg": "", "src": ""}],
 "replace": [{"old": "<alter pkg>", "pkg": "<neuer pkg oder leer>", "name": "", "note": "", "url": "", "nostore": false, "src": ""}],
 "apps": [{"name": "", "cat": "", "pkg": "", "ess": true, "note": "", "city": "",
           "use": "ok", "req": ""}]}
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
    use = (a.get("use") or "ok").strip().lower()
    out["use"] = use if use in ("ok", "limited", "no") else "ok"
    if a.get("req"):
        out["req"] = a["req"].strip()
    if out["use"] == "ok":
        out.pop("use")
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
    if raw.get("lgbtq_note"):
        country["lgbtq_note"] = raw["lgbtq_note"].strip()
        if raw.get("lgbtq_src"):
            country["lgbtq_src"] = raw["lgbtq_src"]
    if raw.get("fetched"):
        country["checked"] = raw["fetched"]
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
                for f in ("use", "req"):
                    if f in app:
                        old[f] = app[f]
                continue
            # Recherchierten Eintrag aktualisieren
            for f in ("cat", "note", "pkg", "src", "ess", "use", "req"):
                if f in app:
                    old[f] = app[f]
            if "use" not in app:
                old.pop("use", None)
            if "req" not in app:
                old.pop("req", None)
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
    # Laut Quelle eingestellte Apps: recherchierte Einträge entfernen, eigene nur markieren
    for gone in raw.get("discontinued", []):
        gk = ((gone.get("pkg") or gone.get("name") or "").strip().lower())
        if not gk:
            continue
        for lst in [country["apps"]] + [ci["apps"] for ci in country["cities"]]:
            for x in list(lst):
                if key(x) == gk or x["name"].strip().lower() == (gone.get("name") or "").strip().lower():
                    if x.get("mine"):
                        x["use"] = "no"
                        x["req"] = "Laut Quelle eingestellt"
                    else:
                        lst.remove(x)
    # Geänderte Paketnamen oder Wechsel auf Web/APK: gilt auch für eigene Einträge
    for rep in raw.get("replace", []):
        old = (rep.get("old") or "").strip().lower()
        if not old:
            continue
        new = (rep.get("pkg") or "").strip()
        for lst in [country["apps"]] + [ci["apps"] for ci in country["cities"]]:
            for x in list(lst):
                if (x.get("pkg") or "").lower() != old:
                    continue
                if new and any((y.get("pkg") or "").lower() == new.lower() for y in lst):
                    lst.remove(x)  # Nachfolger steht schon in der Liste
                    continue
                if new:
                    x["pkg"] = new
                for f in ("name", "note", "url", "src"):
                    if rep.get(f):
                        x[f] = rep[f]
                if rep.get("nostore"):
                    x["nostore"] = True
                else:
                    x.pop("nostore", None)
    country["cities"].sort(key=lambda c: c["name"])
    return added


def add_continents_and_info(data):
    """Setzt "cont" (Kontinent aus queue/*.json) und "info" (info/wikidata.json + info/trinkgeld.json)."""
    cont = {}
    for f in glob.glob(os.path.join(HERE, "queue", "*.json")):
        q = json.load(open(f, encoding="utf-8"))
        for k in ("todo", "done"):
            for e in q.get(k, []):
                cont[e["code"].upper()] = q["continent"]

    def load(name):
        p = os.path.join(HERE, "info", name)
        return json.load(open(p, encoding="utf-8")).get("countries", {}) if os.path.exists(p) else {}

    wd = load("wikidata.json")
    tips = load("trinkgeld.json")
    for c in data["countries"]:
        code = c["code"]
        if code in cont:
            c["cont"] = cont[code]
        info = dict(wd.get(code, {}))
        t = tips.get(code)
        if t and t.get("tip"):
            info["tip"] = t["tip"]
            info["tip_src"] = t.get("src", "")
        if info:
            c["info"] = info
        else:
            c.pop("info", None)


def main():
    global VALID_CATS
    import datetime
    check_only = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    version = args[0] if args else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
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
    add_continents_and_info(data)
    if version:
        data["version"] = version
    # Grundprüfung
    for c in data["countries"]:
        assert c["code"] and c["name"] and "apps" in c, c
        for a in c["apps"] + [x for ci in c.get("cities", []) for x in ci["apps"]]:
            assert a["name"] and a["cat"] in VALID_CATS, (c["code"], a)
    if check_only:
        print("Prüfung ok, nichts geschrieben.")
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    n_apps = sum(len(c["apps"]) + sum(len(ci["apps"]) for ci in c.get("cities", [])) for c in data["countries"])
    print(f"neu: {total} · {len(data['countries'])} Länder · {n_apps} Einträge · Stand {data['version']}")


if __name__ == "__main__":
    main()
