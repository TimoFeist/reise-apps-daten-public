"""Sucht für Apps ohne Paketnamen den passenden Google-Play-Eintrag und schreibt ihn nach info/pkg.json.

Übernommen wird ein Treffer nur, wenn der Play-Titel zum Namen passt UND ein Beleg dazukommt:
  domain   Webseite oder E-Mail des Entwicklers bei Google Play gehört zur selben Domain wie url/src des Eintrags
  gov      beide Domains sind Behördendomains desselben Landes (z. B. *.gov.kw)
  daten    derselbe Name (mind. 4 Zeichen) hat in einem anderen Land schon genau diesen Paketnamen (Titel egal)
  apple    die iPhone-Version (info/ios.json) hat denselben Anbieter wie der Play-Entwickler
  anbieter Titel und Entwicklername beginnen beide mit dem App-Namen (mind. 4 Zeichen) und nur ein Treffer erfüllt das
Alles andere landet ohne Zuordnung in queue/pkg-pruefung.json (mit Kandidaten) zur Prüfung von Hand.
info/pkg.json: {"apps": {"<Name>|<Land>": {"pkg": "...", "how": "...", "checked": "JJJJ-MM-TT"}}}
"pkg": "" = nichts Sicheres gefunden (nach 30 Tagen neu). "fix": true = von Hand gesetzt, wird nie überschrieben.
Schwache Belege (daten, anbieter) kommen ohne --alle nur als "vorschlag" auf die Prüfliste.
Aufruf: python3 tools/pkg_suche.py [max. Anzahl] [--alle]   © 2026 Timo Feist
"""
import datetime, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info", "pkg.json")
REVIEW = os.path.join(HERE, "queue", "pkg-pruefung.json")
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
res = json.load(open(OUT, encoding="utf-8"))["apps"] if os.path.exists(OUT) else {}
ios = json.load(open(os.path.join(HERE, "info", "ios.json"), encoding="utf-8")).get("apps", {})
today = datetime.date.today()
ARGS = [x for x in sys.argv[1:] if not x.startswith("--")]
LIMIT = int(ARGS[0]) if ARGS else 100000
WEAK_OK = "--alle" in sys.argv  # schwache Belege (daten, anbieter) nur nach Durchsicht von Hand übernehmen
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}
GENERIC = {"apple.com", "google.com", "bento.travel", "wikipedia.org", "facebook.com", "instagram.com", "x.com", "twitter.com",
           "linkedin.com", "youtube.com", "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "github.io", "medium.com",
           "tripadvisor.com", "timeout.com", "reddit.com", "lonelyplanet.com", "culturetrip.com", "blogspot.com", "wordpress.com"}
SLD = {"co", "com", "gov", "org", "net", "ac", "edu", "go", "or", "ne", "gob", "gouv", "govt", "nic", "mil", "info"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def host(u):
    try:
        h = urllib.parse.urlparse(u if "://" in u else "http://" + u).hostname or ""
    except ValueError:
        return ""
    return h.lower().removeprefix("www.")


def regdom(h):
    p = h.split(".")
    if len(p) >= 3 and p[-2] in SLD and len(p[-1]) == 2:
        return ".".join(p[-3:])
    return ".".join(p[-2:])


def govsuffix(h):
    p = h.split(".")
    if len(p) >= 3 and p[-2] in ("gov", "gob", "gouv", "govt", "go") and len(p[-1]) == 2:
        return ".".join(p[-2:])
    return ""


def title_ok(title, name):
    t, n = norm(title), norm(name)
    if not n or not t:
        return False
    if t == n:
        return True
    first = re.split(r"\s+[-–—:|·]\s+|:\s|\s\|\s|\(", title)[0]
    return norm(first) == n


def get(url):
    req = urllib.request.Request(url, headers=UA)
    for v in range(3):
        try:
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (v + 1))
        except Exception:
            time.sleep(3)
    return False


_details = {}


def details(pkg, gl):
    if pkg in _details:
        return _details[pkg]
    b = None
    for g in ("US", gl):
        b = get("https://play.google.com/store/apps/details?id=%s&hl=en&gl=%s" % (pkg, g))
        if b:
            break
    if not b:
        _details[pkg] = None
        return None
    m = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', b, re.S)
    try:
        j = json.loads(m.group(1)) if m else {}
    except ValueError:
        j = {}
    au = j.get("author") or {}
    doms = {regdom(host(au.get("url", "")))} if au.get("url") else set()
    hosts = {host(au.get("url", ""))} if au.get("url") else set()
    for e in re.findall(r"mailto:([^\"\s<>?]+)", b)[:3]:
        hosts.add(e.split("@")[-1].lower())
        doms.add(regdom(e.split("@")[-1].lower()))
    r = {"title": j.get("name", ""), "dev": au.get("name", ""), "doms": doms - {""} - GENERIC, "hosts": hosts - {""}}
    _details[pkg] = r
    return r


# Bekannte Paketnamen je Name aus den Daten
byname = defaultdict(set)
todo = []
for c in data["countries"]:
    for lst in [c["apps"]] + [ci["apps"] for ci in c.get("cities", [])]:
        for a in lst:
            if a.get("pkg"):
                byname[norm(a["name"])].add(a["pkg"])
            elif not a.get("nostore") and not a.get("dl"):
                todo.append((c["code"], a))
seen = set()
items = []
for cc, a in todo:
    k = a["name"] + "|" + cc
    if k in seen:
        continue
    seen.add(k)
    e = res.get(k)
    if e and (e.get("fix") or e.get("pkg") or (today - datetime.date.fromisoformat(e.get("checked", "2000-01-01"))).days < 30):
        continue
    items.append((k, cc, a))
items = items[:LIMIT]
print("zu suchen:", len(items), flush=True)


def one(item):
    k, cc, a = item
    name = a["name"]
    gl = cc if len(cc) == 2 and cc != "WW" else "US"
    cands = []
    known = byname.get(norm(name), set())
    if len(known) == 1:
        cands.append(next(iter(known)))
        # Gleicher Name hat in den Daten schon genau diesen Paketnamen: übernehmen, wenn es die App bei Play gibt
        if len(norm(name)) >= 4 and details(cands[0], gl):
            d = details(cands[0], gl)
            return k, {"pkg": cands[0], "how": "daten"}, [{"pkg": cands[0], "title": d["title"], "dev": d["dev"], "web": sorted(d["hosts"])[:2]}], False
    b = get("https://play.google.com/store/search?q=%s&c=apps&gl=%s&hl=en" % (urllib.parse.quote(name), gl))
    if b is False:
        return k, None, [], True
    for m in re.finditer(r"/store/apps/details\?id=([A-Za-z0-9_.]+)", b or ""):
        if m.group(1) not in cands:
            cands.append(m.group(1))
        if len(cands) >= 6:
            break
    my_hosts = {host(a.get(f, "")) for f in ("url", "src") if a.get(f)} - {""}
    my_doms = {regdom(h) for h in my_hosts} - GENERIC
    my_gov = {govsuffix(h) for h in my_hosts} - {""}
    ie = ios.get(k, {})
    seen_c = []
    for pkg in cands[:6]:
        d = details(pkg, gl)
        if not d:
            continue
        seen_c.append({"pkg": pkg, "title": d["title"], "dev": d["dev"], "web": sorted(d["hosts"])[:2]})
        if not title_ok(d["title"], name):
            continue
        how = None
        if my_doms & d["doms"]:
            how = "domain"
        elif my_gov and my_gov & {govsuffix(h) for h in d["hosts"]}:
            how = "gov"
        elif pkg in known and len(known) == 1:
            how = "daten"
        elif ie.get("seller") and norm(ie["seller"])[:12] and (norm(ie["seller"])[:12] == norm(d["dev"])[:12]):
            how = "apple"
        if how:
            return k, {"pkg": pkg, "how": how}, seen_c, False
    n = norm(name)
    if len(n) >= 4:
        hits = [c["pkg"] for c in seen_c if norm(c["title"]).startswith(n) and norm(c["dev"]).startswith(n)]
        if len(hits) == 1:
            return k, {"pkg": hits[0], "how": "anbieter"}, seen_c, False
    return k, None, seen_c, False


review = {}
n_ok = 0
with ThreadPoolExecutor(5) as ex:
    for i, (k, hit, seen_c, failed) in enumerate(ex.map(one, items)):
        if failed:
            continue
        if hit and hit["how"] in ("daten", "anbieter") and not WEAK_OK:
            res[k] = {"pkg": "", "checked": today.isoformat()}
            review[k] = [{"vorschlag": hit["pkg"], "how": hit["how"]}] + seen_c[:4]
        elif hit:
            res[k] = {"pkg": hit["pkg"], "how": hit["how"], "checked": today.isoformat()}
            n_ok += 1
        else:
            res[k] = {"pkg": "", "checked": today.isoformat()}
            review[k] = seen_c[:4]
        if i % 100 == 0:
            print(i, k, hit["pkg"] if hit else "-", flush=True)
json.dump({"apps": dict(sorted(res.items()))}, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
old = json.load(open(REVIEW, encoding="utf-8")).get("apps", {}) if os.path.exists(REVIEW) else {}
old.update(review)
for k in list(old):
    if res.get(k, {}).get("pkg"):
        old.pop(k)
json.dump({"hinweis": "Apps ohne sicheren Play-Treffer (tools/pkg_suche.py). Richtigen Paketnamen von Hand in info/pkg.json mit \"fix\": true eintragen.",
           "apps": dict(sorted(old.items()))}, open(REVIEW, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("zugeordnet:", n_ok, "offen:", len(old))
