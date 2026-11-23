"""Termine der NAUGHTY-Partys (naughtyparty.ticket.io) in info/prides.json aktuell halten.

© 2026 Timo Feist. Alle Rechte vorbehalten.

Liest die öffentliche Terminliste des Veranstalters bei ticket.io (strukturierte Daten nach schema.org,
die die Seite selbst mitliefert) und übernimmt je Termin Name, Datum, Ort und den Ticket-Link als
Festival-Eintrag (type "fest", cat "party"). Übernommen werden nur Fakten (Termin, Ort, Link), keine Texte
oder Bilder. Termine, die beim Veranstalter nicht mehr stehen, fallen heraus.

Aufruf: python tools/naughty.py        (ändert info/prides.json nur, wenn sich etwas geändert hat)
Rückgabe: 0 = geändert oder unverändert, 1 = Seite nicht lesbar (dann bleibt alles wie es ist)
"""
import datetime
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(HERE, "info", "prides.json")
QUELLE = "https://naughtyparty.ticket.io/dkxjqz/"


def termine():
    req = urllib.request.Request(QUELLE + "?lang=de", headers={"User-Agent": "LocalAppFinder-Termine/1.0 (+https://localappfinder.uk)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    out = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            e = json.loads(block)
        except ValueError:
            continue
        for x in (e if isinstance(e, list) else [e]):
            if not isinstance(x, dict) or not str(x.get("@type", "")).endswith("Event"):
                continue
            name = str(x.get("name") or "").strip()
            m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})\s+(.*)", name)
            if m:
                tag = "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
                name = m.group(4).strip()
            else:
                tag = str(x.get("startDate") or "")[:10]
            if not re.match(r"\d{4}-\d{2}-\d{2}$", tag) or not name:
                continue
            loc = x.get("location") or {}
            adr = loc.get("address") or {}
            geo = loc.get("geo") or {}
            url = str((x.get("offers") or {}).get("url") or "")
            if not url.startswith("https://naughtyparty.ticket.io/"):
                url = QUELLE
            try:
                lat, lon = round(float(geo["latitude"]), 3), round(float(geo["longitude"]), 3)
            except (KeyError, TypeError, ValueError):
                continue
            cc = str(adr.get("addressCountry") or "").upper()
            stadt = str(adr.get("addressLocality") or "").strip()
            if len(cc) != 2 or not stadt:
                continue
            if x.get("eventStatus", "").endswith(("EventCancelled", "EventPostponed")):
                continue
            out.append({
                "name": name if name.lower().startswith("naughty") else "Naughty " + name,
                "city": stadt, "cc": cc, "lat": lat, "lon": lon,
                "start": tag, "end": tag, "month": int(tag[5:7]),
                "url": url, "src": QUELLE, "type": "fest", "cat": "party",
            })
    return out


def main():
    try:
        neu = termine()
    except Exception as e:  # Netz/Seite: nichts ändern
        print("Seite nicht lesbar:", e)
        return 1
    d = json.load(open(P, encoding="utf-8"))
    heute = datetime.date.today().isoformat()
    alt = [x for x in d["items"] if x.get("src") == QUELLE]
    rest = [x for x in d["items"] if x.get("src") != QUELLE]
    # Leere Liste nur übernehmen, wenn vorher auch nichts Künftiges da war (Schutz gegen kaputte Seite)
    if not neu and any((x.get("end") or x.get("start") or "") >= heute for x in alt):
        print("Keine Termine gefunden, vorhandene bleiben")
        return 0
    neu.sort(key=lambda x: (x["start"], x["name"]))
    if json.dumps(sorted(alt, key=lambda x: (x["start"], x["name"])), sort_keys=True) == json.dumps(neu, sort_keys=True):
        print("Unverändert:", len(neu), "Termine")
        return 0
    d["items"] = rest + neu
    d["updated"] = heute
    with open(P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Aktualisiert:", len(neu), "Termine")
    for x in neu:
        print(" ", x["start"], x["name"], x["city"], x["url"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
