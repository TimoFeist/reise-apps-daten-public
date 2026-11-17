# Anleitung: Länder ergänzen

Diese Datei beschreibt, wie neue Länder in `data.json` kommen. Sie ist für die automatischen Läufe und für Handarbeit gleich.

## Ablauf pro Land

1. Nächstes Land aus `queue.json` (`todo`, von oben) nehmen.
2. Quelle finden: WebSearch `bento.travel <Englischer Ländername> apps` mit `allowed_domains: ["bento.travel","www.bento.travel"]`. Die Länderseite ist meist `https://www.bento.travel/<slug>`.
3. Länderseite mit WebFetch und genau diesem Prompt abrufen:

   > Return ONLY valid minified JSON, no prose. Schema: {"updated":"<Last updated text or empty>","note":"<one German sentence, the most important practical tip from the 'What to know' section, max 140 chars>","apps":[{"name":"","cat":"","pkg":"","ess":true,"note":"","city":""}]}. Include every app listed on the page EXCEPT: Guac, bento.travel, WhatsApp, Google Translate, Google Maps, any eSIM app. cat must be one of: entry (visa/arrival/customs), transit (city public transport), rail (trains, long-distance bus, ferries), taxi (ride hailing/taxi), carshare (car rental/sharing), micro (bike/scooter), parking, maps (navigation apps other than Google Maps), delivery (food/grocery delivery, restaurants), payment, tourism (attractions, city passes, tours), shopping, safety (emergency, weather warnings), flights, hotels, misc. pkg = the Android package id exactly as in the page's Google Play link (id=...), empty if none shown. ess = true if marked Essential. note = short German description, max 60 chars, in your own words. city = English city name if the app only works in one specific city, else empty.

4. Ergebnis als `raw/<ISO>.json` speichern und `"src": "<URL der Länderseite>"` ergänzen.
5. Gibt es keine bento-Seite: mit 2 bis 4 Suchen offizielle Quellen finden (Verkehrsbetrieb, Tourismusbehörde, Regierung) und `raw/<ISO>.json` im gleichen Format von Hand schreiben, jede App mit `src`. `pkg` nur, wenn der Paketname in einer Quelle steht. Findet sich nichts Belastbares (z. B. sehr kleine Gebiete), Land ohne Datei als erledigt markieren und im Lauf-Bericht nennen.
6. Land in `queue.json` von `todo` nach `done` verschieben.

## Nach jedem Lauf

```
pip install --break-system-packages -q pycountry
python3 merge_raw.py JJJJ-MM-TT     # heutiges Datum, Europe/Berlin
```

`merge_raw.py` ergänzt nur, löscht nichts und lässt Einträge mit `"mine": true` (Timos eigene Apps) unverändert. Danach README-Stand aktualisieren, committen, pushen.

## Regeln

* Nichts erfinden. Jede App braucht eine Quelle (`src`).
* Notizen auf Deutsch, eigene Worte, keine Gedankenstriche.
* Einreise-Hinweise beziehen sich auf deutsche Staatsbürger.
