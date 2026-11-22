#!/usr/bin/env python3
# © 2026 Timo Feist. Alle Rechte vorbehalten.
"""Holt Länder-Infos aus Wikidata (Lizenz CC0) und schreibt info/wikidata.json.

Pro Land (ISO-Code): Notrufnummern, Steckdosen-Typen, Netzspannung, Währung,
Straßenseite, Ländervorwahl. Nur Werte, die in Wikidata stehen, nichts ergänzt.
Läuft von Hand (python3 info/wikidata.py), das Ergebnis wird mit eingecheckt.
merge_raw.py übernimmt es dann als "info" in data.json.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "wikidata.json")
ENDPOINT = "https://query.wikidata.org/sparql"
UA = "LaenderInfoScript/1.0 (python-urllib)"

# Jede Abfrage liefert ?iso und einen Wert. Länder/Gebiete über ISO 3166-1 alpha-2 (P297).
QUERIES = {
    "emergency": """
SELECT ?iso ?v WHERE {
  ?c wdt:P297 ?iso; wdt:P2852 ?n.
  ?n rdfs:label ?v. FILTER(LANG(?v) = "en")
}""",
    "plugs": """
SELECT ?iso ?v WHERE {
  ?c wdt:P297 ?iso; wdt:P2853 ?p.
  ?p rdfs:label ?v. FILTER(LANG(?v) = "en")
}""",
    "voltage": """
SELECT ?iso ?v WHERE {
  ?c wdt:P297 ?iso; p:P2884/psv:P2884/wikibase:quantityAmount ?v.
}""",
    "currency": """
SELECT ?iso ?v ?name WHERE {
  ?c wdt:P297 ?iso; p:P38 ?st.
  ?st ps:P38 ?cur.
  FILTER NOT EXISTS { ?st pq:P582 ?end }
  ?cur wdt:P498 ?v.
  OPTIONAL { ?cur rdfs:label ?name. FILTER(LANG(?name) = "de") }
}""",
    "drive": """
SELECT ?iso ?v WHERE {
  ?c wdt:P297 ?iso; p:P1622 ?st.
  ?st ps:P1622 ?side.
  FILTER NOT EXISTS { ?st pq:P582 ?end }
  BIND(IF(?side = wd:Q11920728, "links", IF(?side = wd:Q14565199, "rechts", "")) AS ?v)
}""",
    "calling": """
SELECT ?iso ?v WHERE {
  ?c wdt:P297 ?iso; wdt:P474 ?v.
}""",
}


def run(q):
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:
            print("  Fehler:", e, "→ neuer Versuch", file=sys.stderr)
            time.sleep(70)
    raise SystemExit("Wikidata nicht erreichbar")


# Wikidata nennt die Steckernormen, Reisende kennen die Typ-Buchstaben (IEC World Plugs).
PLUG_NAMES = [
    (r"NEMA 1-15", "A"), (r"NEMA 5-15", "B"), (r"Europlug|CEE 7/16", "C"),
    (r"BS 546.*15|15 ?A.*BS 546|SANS 164-1", "M"), (r"BS 546", "D"),
    (r"CEE 7/5|French", "E"), (r"Schuko|CEE 7/4", "F"), (r"BS 1363", "G"),
    (r"SI 32|Israel", "H"), (r"AS/NZS 3112|AS 3112|Australian", "I"), (r"SEV 1011|SN 441011|Swiss", "J"),
    (r"Section 107|Danish", "K"), (r"CEI 23-50|Italian", "L"), (r"NBR 14136|IEC 60906-1|Brazil", "N"),
    (r"TIS 166|Thai", "O"),
]
UNMAPPED = set()


def plug(label):
    m = re.search(r"\btype\s+([A-O])\b", label, re.I)
    if m:
        return m.group(1).upper()
    for pat, letter in PLUG_NAMES:
        if re.search(pat, label, re.I):
            return letter
    UNMAPPED.add(label)
    return None


def main():
    info = {}

    def add(iso, field, value, multi):
        iso = iso.upper()
        if not re.fullmatch(r"[A-Z]{2}", iso) or value in (None, ""):
            return
        d = info.setdefault(iso, {})
        if multi:
            lst = d.setdefault(field, [])
            if value not in lst:
                lst.append(value)
        else:
            d.setdefault(field, value)

    for field, q in QUERIES.items():
        print("Abfrage:", field)
        rows = run(q)
        for r in rows:
            iso = r["iso"]["value"]
            v = r.get("v", {}).get("value", "")
            if field == "emergency":
                v = v.strip()
                if re.fullmatch(r"[0-9 ]{2,6}", v):
                    add(iso, "emergency", v.replace(" ", ""), True)
            elif field == "plugs":
                add(iso, "plugs", plug(v), True)
            elif field in ("voltage", "frequency"):
                try:
                    n = float(v)
                except ValueError:
                    continue
                if field == "voltage" and 90 <= n <= 260:
                    add(iso, "voltage", int(round(n)), True)
                if field == "frequency" and n in (50, 60):
                    add(iso, "hz", int(n), True)
            elif field == "currency":
                if re.fullmatch(r"[A-Z]{3}", v):
                    name = r.get("name", {}).get("value", "")
                    d = info.setdefault(iso.upper(), {})
                    cur = d.setdefault("currency", [])
                    if all(c["code"] != v for c in cur):
                        cur.append({"code": v, "name": name} if name else {"code": v})
            elif field == "drive":
                add(iso, "drive", v, False)
            elif field == "calling":
                v = v.strip().replace(" ", "")
                if re.fullmatch(r"\+[0-9-]{1,8}", v):
                    add(iso, "calling", v, True)
        time.sleep(65)  # Wikidata erlaubt derzeit nur 1 Abfrage pro Minute

    for d in info.values():
        for k in ("emergency", "plugs", "voltage", "hz", "calling"):
            if k in d:
                d[k] = sorted(d[k], key=lambda x: (len(str(x)), str(x)))
        if "currency" in d:
            d["currency"].sort(key=lambda c: c["code"])
    out = {
        "_quelle": "Wikidata (https://www.wikidata.org), Lizenz CC0. Erzeugt mit info/wikidata.py.",
        "_stand": time.strftime("%Y-%m-%d"),
        "countries": dict(sorted(info.items())),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(len(info), "Länder geschrieben nach", OUT)
    if UNMAPPED:
        print("Nicht zugeordnete Steckernormen:", sorted(UNMAPPED))


if __name__ == "__main__":
    main()
