"""Zweiter Durchgang für Apps ohne Paketnamen (queue/pkg-pruefung.json): sucht Belege in den eigenen Quellen.

  quelle   Die Quellseite (src/url) verlinkt den Play-Eintrag direkt (play.google.com/...id= oder market://), und der
           Play-Titel enthält den Namen bzw. umgekehrt (der Treffer muss eindeutig sein).
  bundle   Die iPhone-Version (src apps.apple.com oder info/ios.json) hat als Bundle-ID genau diesen Paketnamen und
           der Play-Titel passt.
  apple    Play-Entwickler gleich Apple-Anbieter (bzw. gleiche Domain wie dessen Webseite) und der Play-Titel passt.
Ergebnis nach info/pkg.json (gleiches Format wie tools/pkg_suche.py), Gefundenes fliegt aus der Prüfliste.
Aufruf: python3 tools/pkg_quelle.py   © 2026 Timo Feist
"""
import datetime, json, os, re, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.argv = sys.argv[:1] + ["0"]  # pkg_suche nur als Bibliothek laden (keine Suche starten)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "tools"))
import pkg_suche as ps  # noqa: E402  (läuft mit Limit 0 leer durch)

REVIEW = ps.REVIEW
review = json.load(open(REVIEW, encoding="utf-8"))
res = json.load(open(ps.OUT, encoding="utf-8"))["apps"]
today = datetime.date.today().isoformat()
PLAY = re.compile(r"(?:play\.google\.com/store/apps/details\?(?:[^\"'<>\s]*?&(?:amp;)?)?id=|market://details\?id=)([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)")

ent = {}
for c in ps.data["countries"]:
    for lst in [c["apps"]] + [ci["apps"] for ci in c.get("cities", [])]:
        for a in lst:
            ent.setdefault(a["name"] + "|" + c["code"], a)


def loose(title, name):
    t, n = ps.norm(title), ps.norm(name)
    return bool(t and n and len(n) >= 3 and (n in t or (len(t) >= 4 and t in n)))


def apple(a, k):
    ids = []
    m = re.search(r"apps\.apple\.com/.*?id(\d{6,})", (a.get("src") or "") + " " + (a.get("url") or ""))
    if m:
        ids.append(m.group(1))
    i = ps.ios.get(k, {}).get("id")
    if i and str(i) not in ids:
        ids.append(str(i))
    for i in ids:
        b = ps.get("https://itunes.apple.com/lookup?id=" + i)
        try:
            r = json.loads(b)["results"][0]
            return {"bundle": r.get("bundleId", ""), "seller": r.get("sellerName", ""), "sellerUrl": r.get("sellerUrl") or "",
                    "name": r.get("trackName", "")}
        except Exception:
            continue
    return None


def one(k):
    a = ent.get(k)
    if not a:
        return k, None
    name = a["name"]
    cc = k.rsplit("|", 1)[1]
    gl = cc if len(cc) == 2 and cc != "WW" else "US"
    # 1) Quellseiten
    for f in ("url", "src"):
        u = a.get(f) or ""
        h = ps.host(u)
        if not u or "apple.com" in h:
            continue
        b = ps.get(u)
        if not b:
            continue
        ids = list(dict.fromkeys(PLAY.findall(b)))
        if not ids:
            continue
        ok = []
        for p in ids[:40]:
            d = ps.details(p, gl)
            if d and loose(d["title"], name):  # Titel muss passen (Zeitungsseiten verlinken sonst ihre eigene App)
                ok.append(p)
        if len(ok) == 1:
            return k, {"pkg": ok[0], "how": "quelle"}
    # 2) iPhone-Version
    ap = apple(a, k)
    if ap:
        if ap["bundle"]:
            d = ps.details(ap["bundle"], gl)
            if d and (ps.title_ok(d["title"], name) or loose(d["title"], name) or loose(d["title"], ap["name"])):
                return k, {"pkg": ap["bundle"], "how": "bundle"}
        cands = [c["pkg"] for c in review["apps"].get(k, []) if c.get("pkg")]
        for c in review["apps"].get(k, []):
            if c.get("vorschlag"):
                cands.insert(0, c["vorschlag"])
        b = ps.get("https://play.google.com/store/search?q=%s&c=apps&gl=%s&hl=en" % (urllib.parse.quote(ap["name"] or name), gl))
        for m in re.finditer(r"/store/apps/details\?id=([A-Za-z0-9_.]+)", b or ""):
            if m.group(1) not in cands:
                cands.append(m.group(1))
        sdom = ps.regdom(ps.host(ap["sellerUrl"])) if ap["sellerUrl"] else ""
        hits = []
        for p in cands[:8]:
            d = ps.details(p, gl)
            if not d or not (loose(d["title"], name) or loose(d["title"], ap["name"])):
                continue
            if (ps.norm(ap["seller"])[:10] and ps.norm(ap["seller"])[:10] == ps.norm(d["dev"])[:10]) or (sdom and sdom in d["doms"]):
                hits.append(p)
        if len(set(hits)) == 1:
            return k, {"pkg": hits[0], "how": "apple"}
    return k, None


todo = [k for k in review["apps"] if not res.get(k, {}).get("abgelehnt")]
print("prüfe", len(todo), flush=True)
n = 0
with ThreadPoolExecutor(5) as ex:
    for i, (k, hit) in enumerate(ex.map(one, todo)):
        if hit:
            res[k] = {"pkg": hit["pkg"], "how": hit["how"], "checked": today}
            review["apps"].pop(k, None)
            n += 1
            print(k, "->", hit["pkg"], hit["how"], flush=True)
json.dump({"apps": dict(sorted(res.items()))}, open(ps.OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
json.dump(review, open(REVIEW, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("gefunden:", n, "offen:", len(review["apps"]))
