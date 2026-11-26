"""Vollständigkeit: wählt Länder aus, deren Kategorien komplett durchsucht werden sollen (alle Apps, die Touristen
dort nutzen können, nicht nur eine je Kategorie), und schreibt sie mit den schon vorhandenen Apps nach queue/tiefe.json.

Reihenfolge: Länder mit vielen Einträgen und Städten (große Reiseziele) zuerst; ein Land kommt erst 90 Tage nach
seiner letzten Vollständigkeitsprüfung wieder dran (info/tiefe-versuche.json: {"laender": {"<ISO>": "JJJJ-MM-TT"}}).

Aufruf: python3 tools/tiefe.py 8              (die nächsten 8 Länder nach queue/tiefe.json)
        python3 tools/tiefe.py --erledigt DE FR  (Prüfung für diese Länder heute eintragen)
© 2026 Timo Feist
"""
import datetime, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERS = os.path.join(HERE, "info", "tiefe-versuche.json")
OUT = os.path.join(HERE, "queue", "tiefe.json")
KAT = ["transit", "rail", "taxi", "carshare", "micro", "parking", "delivery", "payment", "tourism", "safety", "entry",
       "maps", "flights", "hotels", "shopping", "lgbtq", "misc"]
today = datetime.date.today()
vers = json.load(open(VERS, encoding="utf-8")) if os.path.exists(VERS) else {"laender": {}}


def save():
    json.dump({"laender": dict(sorted(vers["laender"].items()))}, open(VERS, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)


if len(sys.argv) > 1 and sys.argv[1] == "--erledigt":
    for cc in sys.argv[2:]:
        vers["laender"][cc.upper()] = today.isoformat()
    save()
    print("eingetragen:", " ".join(sys.argv[2:]))
    sys.exit(0)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
ww = next((c for c in data["countries"] if c["code"] == "WW"), {"apps": []})
cand = []
for c in data["countries"]:
    cc = c["code"]
    if cc == "WW":
        continue
    last = vers["laender"].get(cc)
    if last and (today - datetime.date.fromisoformat(last)).days < 90:
        continue
    weight = len(c["apps"]) + sum(len(ci["apps"]) for ci in c.get("cities", [])) + 5 * len(c.get("cities", []))
    cand.append((weight, cc, c))
cand.sort(key=lambda x: (-x[0], x[1]))
out = []
for _, cc, c in cand[:n]:
    have = {k: [] for k in KAT}
    for a in c["apps"]:
        have.setdefault(a["cat"], []).append(a["name"])
    for ci in c.get("cities", []):
        for a in ci["apps"]:
            have.setdefault(a["cat"], []).append(a["name"] + " (" + ci["name"] + ")")
    for a in ww["apps"]:
        if cc in a.get("countries", []) or a.get("where") == "all":
            have.setdefault(a["cat"], []).append(a["name"] + " (weltweit)")
    out.append({"cc": cc, "name": c["name"], "staedte": [ci["name"] for ci in c.get("cities", [])],
                "vorhanden": {k: sorted(set(v)) for k, v in have.items() if v or k in KAT[:11]}})
json.dump({"stand": today.isoformat(), "laender": out}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("ausgewählt:", " ".join(x["cc"] for x in out), "· noch nicht geprüft:", len(cand) - len(out))
