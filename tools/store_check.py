"""Wöchentliche Store-Prüfung: ruft jeden Paketnamen aus data.json bei Google Play ab.

Schreibt queue/store-pruefung.json mit
  "fehlt":  Apps, die es weder für das eigene Land noch für US/DE gibt (404),
  "titel":  Apps, deren Play-Titel nicht mehr zum Namen passt (Hinweis auf Umbenennung).
Ändert data.json und raw/ nicht. © 2026 Timo Feist
"""
import datetime, difflib, html, json, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))

apps = {}
for c in data["countries"]:
    for city, lst in [("", c["apps"])] + [(ci["name"], ci["apps"]) for ci in c.get("cities", [])]:
        for a in lst:
            p = a.get("pkg")
            if p and not a.get("nostore") and not a.get("dl"):
                e = apps.setdefault(p, {"name": a["name"], "orte": []})
                e["orte"].append(c["code"] + ("/" + city if city else ""))


def fetch(pkg, gl):
    url = "https://play.google.com/store/apps/details?id=%s&hl=en&gl=%s" % (pkg, gl)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
    for versuch in range(3):
        try:
            body = urllib.request.urlopen(req, timeout=25).read(300000).decode("utf-8", "replace")
            m = re.search(r'og:title" content="([^"]*)"', body)
            return 200, html.unescape(m.group(1)).replace(" - Apps on Google Play", "") if m else ""
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, ""
            time.sleep(10 * (versuch + 1))
        except Exception:
            time.sleep(5)
    return 0, ""


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def check(item):
    pkg, e = item
    laender = sorted({o.split("/")[0] for o in e["orte"] if o[:2] not in ("WW", "AL")})
    for gl in ["US", "DE"] + laender[:3]:
        code, title = fetch(pkg, gl)
        if code == 200:
            n, t = norm(e["name"]), norm(title)
            aehnlich = difflib.SequenceMatcher(None, n, t).ratio()
            if title and n[:4] not in t and t[:4] not in n and aehnlich < 0.45:
                return pkg, {"art": "titel", "name": e["name"], "play_titel": title, "orte": e["orte"]}
            return pkg, None
        if code == 0:
            return pkg, None  # Netzfehler: nicht melden
    return pkg, {"art": "fehlt", "name": e["name"], "orte": e["orte"]}


with ThreadPoolExecutor(4) as ex:
    found = {p: r for p, r in ex.map(check, sorted(apps.items())) if r}

out_path = os.path.join(HERE, "queue", "store-pruefung.json")
alt = {}
if os.path.exists(out_path):
    try:
        alt = {x["pkg"]: x for x in json.load(open(out_path, encoding="utf-8")).get("offen", [])}
    except Exception:
        alt = {}
heute = datetime.date.today().isoformat()
offen = []
for p, r in sorted(found.items()):
    r = dict(r, pkg=p, seit=alt.get(p, {}).get("seit", heute))
    offen.append(r)
json.dump({"geprueft": heute, "pakete": len(apps), "offen": offen},
          open(out_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("geprüft %d Pakete, %d auffällig (%d fehlen, %d Titel)" % (
    len(apps), len(offen), sum(1 for x in offen if x["art"] == "fehlt"), sum(1 for x in offen if x["art"] == "titel")))
