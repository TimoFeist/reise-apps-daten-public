"""Findet Lücken: Länder, in denen eine wichtige Kategorie keine einzige App hat, und schreibt sie nach queue/luecken.json.

Zählt Landes- und Stadteinträge sowie weltweite Apps mit Länderliste ("countries"). Apps mit "use": "no" zählen mit (sie beantworten die Frage, nur mit Bedingung). Weltweite Apps mit "where": "all"
zählen nicht, sie sagen nichts über lokale Angebote.
Versuche stehen in info/luecken-versuche.json: {"versuche": {"<ISO>|<cat>": {"am": "JJJJ-MM-TT", "gefunden": 0, "notiz": ""}}}.
Eine Lücke, die ohne Ergebnis gesucht wurde, kommt erst nach 120 Tagen wieder auf die Liste.

Aufruf: python3 tools/luecken.py                (Liste neu schreiben, Übersicht ausgeben)
        python3 tools/luecken.py --versuch DE parking 2 "Notiz"   (Versuch eintragen, gefunden = Anzahl neuer Apps)
© 2026 Timo Feist
"""
import datetime, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERS = os.path.join(HERE, "info", "luecken-versuche.json")
OUT = os.path.join(HERE, "queue", "luecken.json")
KAT = ["transit", "rail", "taxi", "carshare", "micro", "parking", "delivery", "payment", "tourism", "safety", "entry"]
# Für Deutsche ohne Einreise-Formalitäten (EU, EWR, Schweiz und Kleinstaaten im Schengen-Raum): keine "entry"-Lücke
OHNE_EINREISE = set("AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK IS LI NO CH MC SM VA AD AX FO GL GI IM JE GG".split())
today = datetime.date.today()

vers = json.load(open(VERS, encoding="utf-8")) if os.path.exists(VERS) else {"versuche": {}}

if len(sys.argv) >= 5 and sys.argv[1] == "--versuch":
    cc, cat, n = sys.argv[2].upper(), sys.argv[3], int(sys.argv[4])
    vers["versuche"][cc + "|" + cat] = {"am": today.isoformat(), "gefunden": n, "notiz": " ".join(sys.argv[5:])[:200]}
    json.dump({"versuche": dict(sorted(vers["versuche"].items()))}, open(VERS, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("eingetragen", cc, cat, n)
    sys.exit(0)

data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
ww = next((c for c in data["countries"] if c["code"] == "WW"), {"apps": []})
offen, ruhend = [], 0
for c in data["countries"]:
    cc = c["code"]
    if cc == "WW":
        continue
    apps = c["apps"] + [a for ci in c.get("cities", []) for a in ci["apps"]]
    have = {a["cat"] for a in apps} | {a["cat"] for a in ww["apps"] if cc in a.get("countries", [])}
    for k in KAT:
        if k in have or (k == "entry" and cc in OHNE_EINREISE):
            continue
        v = vers["versuche"].get(cc + "|" + k)
        if v and not v.get("gefunden") and (today - datetime.date.fromisoformat(v["am"])).days < 120:
            ruhend += 1
            continue
        offen.append({"cc": cc, "name": c["name"], "cat": k, "gewicht": len(apps), "zuletzt": (v or {}).get("am", "")})
# Länder mit vielen Einträgen (meist größere Reiseziele) zuerst
offen.sort(key=lambda x: (-x["gewicht"], x["cc"], KAT.index(x["cat"])))
json.dump({"stand": today.isoformat(), "offen": offen, "ruhend": ruhend}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("offene Lücken:", len(offen), "· ruhend (ohne Ergebnis gesucht, < 120 Tage):", ruhend)
