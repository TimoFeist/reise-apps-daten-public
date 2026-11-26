"""Spielt Recherche-Ergebnisse zu Lücken (tools/luecken.py) in raw/<ISO>.json ein und merkt sich die Versuche.

Eingabe (eine oder mehrere Dateien):
{"apps": [{"cc", "name", "cat", "pkg", "note", "city", "use", "req", "url", "nostore", "src"}],
 "leer": [{"cc", "cat", "notiz"}]}
* Apps ohne src, mit ungültiger Kategorie oder ohne pkg/url werden verworfen (und gemeldet).
* Gedankenstriche in note/req werden durch Kommas ersetzt, note wird auf 60 Zeichen gekürzt.
* Schon vorhandene Apps (gleiches pkg bzw. gleicher Name in derselben Stadt) werden nicht doppelt angelegt.
* Jede Kombination Land|Kategorie landet in info/luecken-versuche.json (gefunden = Anzahl neuer Apps).
Aufruf: python3 tools/luecken_einspielen.py ergebnis1.json [ergebnis2.json ...]   © 2026 Timo Feist
"""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "raw")
VERS = os.path.join(HERE, "info", "luecken-versuche.json")
CATS = {c["id"] for c in json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))["categories"]}
PKG = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")
today = datetime.date.today().isoformat()
vers = json.load(open(VERS, encoding="utf-8")) if os.path.exists(VERS) else {"versuche": {}}
raws, found, bad = {}, {}, []


def raw(cc):
    if cc not in raws:
        p = os.path.join(RAW, cc + ".json")
        raws[cc] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"fetched": today, "apps": []}
        raws[cc].setdefault("apps", [])
    return raws[cc]


def clean(s):
    return re.sub(r"\s*[–—]\s*", ", ", (s or "").strip())


for f in sys.argv[1:]:
    d = json.load(open(f, encoding="utf-8"))
    for a in d.get("apps", []):
        cc = (a.get("cc") or "").upper()
        pkg = (a.get("pkg") or "").strip()
        if pkg and not PKG.match(pkg):
            pkg = ""
        if not cc or a.get("cat") not in CATS or not a.get("name") or not (a.get("src") or "").startswith("http") or not (pkg or a.get("url")):
            bad.append((cc, a.get("cat"), a.get("name")))
            continue
        e = {"name": a["name"].strip(), "cat": a["cat"]}
        if pkg:
            e["pkg"] = pkg
        note = clean(a.get("note"))
        if note:
            e["note"] = note if len(note) <= 60 else note[:59].rsplit(" ", 1)[0]
        if (a.get("city") or "").strip():
            e["city"] = a["city"].strip()
        use = a.get("use") if a.get("use") in ("ok", "limited", "no") else "ok"
        e["use"] = use
        if use != "ok" and clean(a.get("req")):
            e["req"] = clean(a.get("req"))
        if a.get("url"):
            e["url"] = a["url"]
            if a.get("nostore") and not pkg:
                e["nostore"] = True
        e["src"] = a["src"]
        r = raw(cc)
        k = (pkg or e["name"]).lower()
        if any((x.get("pkg") or x.get("name", "")).lower() == k and (x.get("city") or "") == e.get("city", "") for x in r["apps"]):
            continue
        r["apps"].append(e)
        found[cc + "|" + e["cat"]] = found.get(cc + "|" + e["cat"], 0) + 1
    for l in d.get("leer", []):
        key = (l.get("cc") or "").upper() + "|" + (l.get("cat") or "")
        if l.get("cat") in CATS and key not in found:
            vers["versuche"][key] = {"am": today, "gefunden": 0, "notiz": (l.get("notiz") or "")[:200]}

for key, n in found.items():
    vers["versuche"][key] = {"am": today, "gefunden": n, "notiz": ""}
for cc, r in raws.items():
    json.dump(r, open(os.path.join(RAW, cc + ".json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
json.dump({"versuche": dict(sorted(vers["versuche"].items()))}, open(VERS, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("neue Apps:", sum(found.values()), "in", len(found), "Lücken · leer:", sum(1 for v in vers["versuche"].values() if v["am"] == today and not v["gefunden"]), "· verworfen:", len(bad))
for b in bad:
    print("  verworfen:", *b)
