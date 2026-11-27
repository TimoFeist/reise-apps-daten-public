#!/usr/bin/env python3
# © 2026 Timo Feist. Alle Rechte vorbehalten.
"""Landeskunde (Reisewarnungen, Dos, Don'ts, Gesetze, Fakten) pflegen.

  python3 tools/kunde.py einspielen <datei.json> [...]   Einträge {"CC": [{"art","de","city","src"}]} prüfen und
                                                         in info/landeskunde.json übernehmen (ersetzt das Land ganz)
  python3 tools/kunde.py fehlend [<ziel.json>]           deutsche Texte ohne Übersetzung je Sprache auflisten
  python3 tools/kunde.py uebersetzung <datei.json> <sprache>   {"deutscher Text": "Übersetzung"} einspielen
  python3 tools/kunde.py pruefen                         alles prüfen (Format, Quellen, Übersetzungen)

Übersetzungen liegen in info/landeskunde_i18n/<sprache>.json (Schlüssel = deutscher Text).
Ein geänderter deutscher Text braucht eine neue Übersetzung; verwaiste Schlüssel räumt "pruefen --aufraeumen" weg.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KUNDE = os.path.join(HERE, "info", "landeskunde.json")
I18N = os.path.join(HERE, "info", "landeskunde_i18n")
LANGS = ["bg", "cs", "da", "el", "en", "es", "et", "fi", "fr", "ga", "hr", "hu", "is", "it", "lt",
         "lv", "mt", "nb", "nl", "pl", "pt", "ro", "ru", "sk", "sl", "sq", "sr", "sv", "tr", "uk"]
ARTEN = {"warnung", "do", "dont", "gesetz", "fakt"}
MAXLEN = 200


def lade(p, leer):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else leer


def schreibe(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    open(p, "a", encoding="utf-8", newline="\n").write("\n")


def staedte():
    d = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
    return {c["code"]: {ci["name"] for ci in c.get("cities", [])} for c in d["countries"]}


def fehler_eintrag(cc, e, st):
    f = []
    if e.get("art") not in ARTEN:
        f.append("art ungültig: %r" % e.get("art"))
    t = (e.get("de") or "").strip()
    if not t:
        f.append("de leer")
    if len(t) > MAXLEN:
        f.append("de länger als %d Zeichen" % MAXLEN)
    if "–" in t or "—" in t or " - " in t:
        f.append("Gedankenstrich im Text")
    if not re.match(r"^https://[^\s]+$", e.get("src") or ""):
        f.append("src fehlt oder nicht https")
    c = e.get("city") or ""
    if c and c not in st.get(cc, set()):
        f.append("Stadt %r gibt es im Land nicht" % c)
    return f


def einspielen(dateien):
    k = lade(KUNDE, {"countries": {}})
    st = staedte()
    n = 0
    for p in dateien:
        neu = json.load(open(p, encoding="utf-8"))
        for cc, liste in neu.items():
            cc = cc.upper()
            if cc not in st:
                print("übersprungen, Land unbekannt:", cc)
                continue
            gut, gesehen = [], set()
            for e in liste or []:
                f = fehler_eintrag(cc, e, st)
                if f:
                    print("  %s verworfen (%s): %s" % (cc, ", ".join(f), (e.get("de") or "")[:70]))
                    continue
                t = e["de"].strip()
                if t in gesehen:
                    continue
                gesehen.add(t)
                x = {"art": e["art"], "de": t, "src": e["src"].strip()}
                if e.get("city"):
                    x["city"] = e["city"]
                gut.append(x)
            if gut:
                k["countries"][cc] = gut
                n += len(gut)
    k["_quelle"] = "Eigene Zusammenfassung in eigenen Worten. Quelle je Eintrag im Feld src (vor allem Auswärtiges Amt, offizielle Tourismusseiten, Wikipedia)."
    k["countries"] = dict(sorted(k["countries"].items()))
    schreibe(KUNDE, {"_quelle": k["_quelle"], "countries": k["countries"]})
    print("übernommen:", n, "Einträge, Länder gesamt:", len(k["countries"]))


def texte():
    k = lade(KUNDE, {"countries": {}})
    return sorted({e["de"] for l in k["countries"].values() for e in l})


def fehlend(ziel=None):
    alle = texte()
    out = {}
    for l in LANGS:
        m = lade(os.path.join(I18N, l + ".json"), {})
        f = [t for t in alle if not m.get(t)]
        if f:
            out[l] = f
    print("%d Texte; ohne Übersetzung: %s" % (len(alle), ", ".join("%s %d" % (l, len(v)) for l, v in out.items()) or "keine"))
    if ziel:
        # Für die Übersetzung reicht eine Liste je Sprache; meist fehlen überall dieselben Texte
        schreibe(ziel, out)


def uebersetzung(p, lang):
    if lang not in LANGS:
        sys.exit("unbekannte Sprache " + lang)
    neu = json.load(open(p, encoding="utf-8"))
    alle = set(texte())
    zp = os.path.join(I18N, lang + ".json")
    m = lade(zp, {})
    n = 0
    for de, tr in neu.items():
        if de in alle and isinstance(tr, str) and tr.strip():
            m[de] = tr.strip()
            n += 1
    schreibe(zp, dict(sorted(m.items())))
    print(lang, "übernommen:", n)


def pruefen(aufraeumen=False):
    k = lade(KUNDE, {"countries": {}})
    st = staedte()
    fehler = 0
    for cc, liste in k["countries"].items():
        for e in liste:
            f = fehler_eintrag(cc, e, st)
            if f:
                fehler += 1
                print(cc, ", ".join(f), e.get("de", "")[:60])
    alle = set(texte())
    for l in LANGS:
        zp = os.path.join(I18N, l + ".json")
        m = lade(zp, {})
        alt = [x for x in m if x not in alle]
        if alt and aufraeumen:
            schreibe(zp, {a: b for a, b in sorted(m.items()) if a in alle})
        elif alt:
            print(l, len(alt), "verwaiste Übersetzungen (pruefen --aufraeumen)")
    fehlend()
    print("Fehler:", fehler)
    return fehler


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "einspielen":
        einspielen(a[1:])
    elif a[0] == "fehlend":
        fehlend(a[1] if len(a) > 1 else None)
    elif a[0] == "uebersetzung":
        uebersetzung(a[1], a[2])
    elif a[0] == "pruefen":
        sys.exit(1 if pruefen("--aufraeumen" in a) else 0)
    else:
        sys.exit(__doc__)
