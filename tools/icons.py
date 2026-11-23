"""Sucht zu jeder App (Paketname) die Adresse ihres Logos bei Google Play und schreibt sie nach info/icons.json.

Es werden keine Bilder gespeichert: merge_raw.py setzt nur "ic" (der Teil hinter https://play-lh.googleusercontent.com/)
an jede App, App und Web-Version laden das Logo direkt von Google Play (so entsteht kein Datenverkehr auf unseren Servern).
info/icons.json: {"apps": {"<paket>": {"u": "<bildpfad>", "checked": "JJJJ-MM-TT"}}}
"u" fehlt = kein Logo gefunden (wird nach 14 Tagen neu versucht). Gefundene werden alle 30 Tage aufgefrischt.
Die Logos sind Marken der jeweiligen Anbieter und werden nur zur Kennzeichnung der verlinkten App gezeigt.
Aufruf: python3 tools/icons.py [max. Anzahl]   © 2026 Timo Feist
"""
import datetime, json, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "icons.json")
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
idx = json.load(open(OUT, encoding="utf-8"))["apps"] if os.path.exists(OUT) else {}
today = datetime.date.today()
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}
PKG = re.compile(r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+$")
IMG = re.compile(rb'"image":\s*"https://play-lh\.googleusercontent\.com/([A-Za-z0-9_\-/]+)')

pkgs = {}
for c in data["countries"]:
    for lst in [c["apps"]] + [ci["apps"] for ci in c.get("cities", [])]:
        for a in lst:
            p = a.get("pkg")
            if p and PKG.match(p) and not a.get("dl"):
                pkgs.setdefault(p, set()).add(c["code"])


def due(p):
    e = idx.get(p)
    if not e:
        return True
    try:
        age = (today - datetime.date.fromisoformat(e.get("checked", "2000-01-01"))).days
    except ValueError:
        return True
    return age > (30 if e.get("u") else 14)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    for v in range(3):
        try:
            return urllib.request.urlopen(req, timeout=25).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (v + 1))
        except Exception:
            time.sleep(3)
    return False


def one(p):
    failed = False
    for gl in ["US", "DE"] + sorted(x for x in pkgs[p] if len(x) == 2 and x != "WW")[:2]:
        body = get("https://play.google.com/store/apps/details?id=%s&hl=en&gl=%s" % (p, gl))
        if body is False:
            failed = True
            continue
        m = IMG.search(body or b"")
        if m:
            return p, m.group(1).decode(), False
    return p, None, failed


todo = [p for p in sorted(pkgs) if due(p)][:LIMIT]
print("zu prüfen:", len(todo), "von", len(pkgs), flush=True)
with ThreadPoolExecutor(6) as ex:
    for i, (p, u, failed) in enumerate(ex.map(one, todo)):
        if u:
            idx[p] = {"u": u, "checked": today.isoformat()}
        elif not failed:
            idx[p] = {"checked": today.isoformat()}
        if i % 200 == 0:
            print(i, p, "ok" if u else "-", flush=True)
for p in list(idx):
    if p not in pkgs:
        idx.pop(p)
json.dump({"apps": dict(sorted(idx.items()))}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
print("mit Logo:", sum(1 for v in idx.values() if v.get("u")), "von", len(idx))
