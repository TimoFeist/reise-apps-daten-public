"""Ordnet Apps aus data.json ihre iPhone-Version im Apple App Store zu.

Schreibt info/ios.json: {"apps": {"<pkg oder Name|Land>": {"id": 123, "name": "...", "seller": "...", "checked": "JJJJ-MM-TT"}}}
Mit "fix": true von Hand festgelegt (wird nie neu gesucht). Ein Eintrag mit "id": 0 heißt: keine passende iPhone-App gefunden (wird nach 30 Tagen neu gesucht).
Zuordnung nur, wenn Name UND Anbieter passen (Anbieter laut Google Play) oder die Bundle-ID gleich dem Paketnamen ist.
Die Apple-Suche erlaubt etwa 20 Abfragen pro Minute, deshalb läuft das Skript langsam.
© 2026 Timo Feist
"""
import datetime, difflib, html, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "ios.json")
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
old = json.load(open(OUT, encoding="utf-8"))["apps"] if os.path.exists(OUT) else {}
today = datetime.date.today()
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100000

# Welche Apps, in welchen Ländern
apps = {}
for c in data["countries"]:
    for lst in [c["apps"]] + [ci["apps"] for ci in c.get("cities", [])]:
        for a in lst:
            if a.get("mine") and a.get("dl"):
                continue
            if a.get("pkg"):
                key = a["pkg"]
            elif not a.get("url"):
                key = a["name"] + "|" + c["code"]
            else:
                continue
            e = apps.setdefault(key, {"name": a["name"], "pkg": a.get("pkg"), "countries": []})
            if c["code"] not in ("WW", "ALL") and c["code"] not in e["countries"]:
                e["countries"].append(c["code"])


def due(key):
    o = old.get(key)
    if not o:
        return True
    if o.get("id") or o.get("fix"):
        return False  # gefunden oder von Hand festgelegt
    try:
        return (today - datetime.date.fromisoformat(o.get("checked", "2000-01-01"))).days > 30
    except ValueError:
        return True


todo = [k for k in apps if due(k)][:LIMIT]
print("zu suchen:", len(todo), "von", len(apps), flush=True)


def play_author(pkg):
    url = "https://play.google.com/store/apps/details?id=%s&hl=en&gl=US" % pkg
    try:
        body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25).read().decode("utf-8", "replace")
    except Exception:
        return "", ""
    t = re.search(r'og:title" content="([^"]*)"', body)
    m = re.search(r'"author":\s*\{[^}]*"name":\s*"([^"]+)"', body)
    return (html.unescape(t.group(1)).replace(" - Apps on Google Play", "") if t else "",
            html.unescape(m.group(1)) if m else "")


with ThreadPoolExecutor(5) as ex:
    authors = dict(zip([k for k in todo if apps[k]["pkg"]],
                       ex.map(play_author, [apps[k]["pkg"] for k in todo if apps[k]["pkg"]])))

STOP = {"app", "the", "official", "mobile", "my", "and", "for", "go", "plus", "inc", "ltd", "llc", "gmbh", "sa", "as", "ab", "oy", "co", "company", "limited", "technologies", "technology"}


def norm(s):
    s = re.split(r"\s[:|\-–—]\s|:\s", s)[0]
    return re.sub(r"[^a-z0-9]", "", s.lower())


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1}


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a)):
        return 0.9
    return difflib.SequenceMatcher(None, a, b).ratio()


def seller_ok(seller, author):
    if not author:
        return False
    if sim(seller, author) >= 0.6:
        return True
    return len(words(seller) & words(author)) > 0


def itunes(term, country):
    q = urllib.parse.urlencode({"term": term, "country": country, "entity": "software", "limit": 15})
    for v in range(4):
        try:
            r = urllib.request.urlopen("https://itunes.apple.com/search?" + q, timeout=30)
            return json.loads(r.read().decode("utf-8")).get("results", [])
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return None  # Land gibt es im App Store nicht
            print("Apple drosselt (%d), warte" % e.code, flush=True)
            time.sleep(60 * (v + 1))  # 403/429: Drosselung
        except Exception:
            time.sleep(10)
    return False  # Fehler: nichts eintragen, nächstes Mal neu versuchen


res = dict(old)
for i, key in enumerate(todo):
    e = apps[key]
    title, author = authors.get(key, ("", ""))
    found = None
    failed = False
    for cc in (e["countries"][:1] or []) + ["us"]:
        results = itunes(e["name"], cc.lower())
        time.sleep(3.2)
        if results is None:
            continue
        if results is False:
            failed = True
            break
        for r in results:
            if e["pkg"] and r.get("bundleId", "").lower() == e["pkg"].lower():
                found = r
                break
            ns = max(sim(r["trackName"], e["name"]), sim(r["trackName"], title) if title else 0)
            if e["pkg"]:
                if ns >= 0.75 and seller_ok(r.get("sellerName", ""), author):
                    found = r
                    break
            elif ns >= 0.95:
                found = r
                break
        if found or results:
            break
    if failed:
        continue
    res[key] = ({"id": found["trackId"], "name": found["trackName"], "seller": found.get("sellerName", ""), "checked": today.isoformat()}
                if found else {"id": 0, "checked": today.isoformat()})
    if i % 50 == 0:
        print(i, key, "->", res[key].get("name", "-"), flush=True)
        json.dump({"apps": res}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

json.dump({"apps": res}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("fertig:", sum(1 for v in res.values() if v.get("id")), "mit iPhone-App von", len(res))
