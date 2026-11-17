# Anleitung: Länder ergänzen

Diese Datei beschreibt, wie neue Länder in `data.json` kommen. Sie ist für die automatischen Läufe und für Handarbeit gleich.

## Ablauf pro Land

1. Nächstes Land aus `queue.json` (`todo`, von oben) nehmen. Steht `"recheck": true` dabei, ist das Land schon drin und wird mit den aktuellen Regeln neu abgerufen.
2. Quelle finden: WebSearch `bento.travel <Englischer Ländername> apps` mit `allowed_domains: ["bento.travel","www.bento.travel"]`. Die Länderseite ist meist `https://www.bento.travel/<slug>`.
3. Länderseite mit WebFetch und genau diesem Prompt abrufen:

   > Return ONLY valid minified JSON, no prose. Schema: {"updated":"<Last updated text or empty>","note":"<one German sentence, the most important practical tip from the 'What to know' section, max 140 chars>","apps":[{"name":"","cat":"","pkg":"","ess":true,"note":"","city":"","use":"ok","req":""}]}. Include every app listed on the page EXCEPT: Guac, bento.travel, WhatsApp, Google Translate, Google Maps, any eSIM app. cat must be one of: entry (visa/arrival/customs), transit (city public transport), rail (trains, long-distance bus, ferries), taxi (ride hailing/taxi), carshare (car rental/sharing), micro (bike/scooter), parking, maps (navigation apps other than Google Maps), delivery (food/grocery delivery, restaurants), payment, tourism (attractions, city passes, tours), shopping, safety (emergency, weather warnings), flights, hotels, misc. pkg = the Android package id exactly as in the page's Google Play link (id=...), empty if none shown. ess = true if marked Essential. note = short German description, max 60 chars, in your own words. city = English city name if the app only works in one specific city, else empty. use = "no" if the page says a foreign visitor cannot really use it (needs a local phone number, local bank account, local ID, residence or local SIM), "limited" if usable with conditions (e.g. guest mode only, NFC card needed, some features need a local number), otherwise "ok". req = short German note naming the condition (e.g. "Lokale Telefonnummer nötig", "Nur mit lokalem Bankkonto"), empty if use is ok.

4. **Nutzbarkeit für Ausländer prüfen.** Ziel: Für jede App ist klar, ob ein Tourist mit deutscher Handynummer und deutscher Karte sie nutzen kann. Bei Bezahl-Apps, Banking und allen Apps, bei denen die Quelle nichts zur Registrierung sagt, aber eine lokale Nummer, ein lokales Konto oder ein Ausweis typisch ist, mit einer kurzen Suche nachprüfen. Bedingungen in `req` eintragen, `use` entsprechend setzen. Apps mit `use: "no"` bleiben drin, die App zeigt sie ganz unten unter „Nur mit Voraussetzungen“; `req` muss dann sagen, was nötig ist (z. B. „Norwegische Telefonnummer nötig“).
5. Ergebnis als `raw/<ISO>.json` speichern und `"src": "<URL der Länderseite>"` ergänzen.
6. **Städte ergänzen.** Für die 3 bis 5 meistbesuchten Städte des Landes je eine Suche nach der offiziellen ÖPNV-App, dem offiziellen Stadtpass bzw. der Tourismus-App und, falls üblich, der Park-App. Nur aufnehmen, wenn eine offizielle Quelle (Verkehrsbetrieb, Stadt, Tourismusbehörde) die App nennt und `use`/`req` wie in Punkt 4 gesetzt sind. Einträge mit `"city": "<englischer Stadtname>"` und eigenem `"src"` in dieselbe `raw/<ISO>.json` schreiben.
7. Gibt es keine bento-Seite: mit 2 bis 4 Suchen offizielle Quellen finden (Verkehrsbetrieb, Tourismusbehörde, Regierung) und `raw/<ISO>.json` im gleichen Format von Hand schreiben, jede App mit `src`. `pkg` nur, wenn der Paketname in einer Quelle steht. Findet sich nichts Belastbares (z. B. sehr kleine Gebiete), Land ohne Datei als erledigt markieren und im Lauf-Bericht nennen.
8. **Bestehende Einträge des Landes prüfen** (nur wenn das Land schon in `data.json` steht): Einträge ohne `src` und ohne `"mine": true` nachprüfen und entweder mit Quelle bestätigen oder entfernen. Bei Timos eigenen Apps (`"mine": true`) nur prüfen, ob Ausländer sie nutzen können, und dann `use`/`req` direkt in `data.json` setzen. Eigene Apps nie löschen.
9. Land in `queue.json` von `todo` nach `done` verschieben.

## Nach jedem Lauf

```
pip install --break-system-packages -q pycountry
python3 merge_raw.py JJJJ-MM-TT     # heutiges Datum, Europe/Berlin
```

`merge_raw.py` ergänzt nur, löscht nichts und lässt Einträge mit `"mine": true` (Timos eigene Apps) unverändert. Danach README-Stand aktualisieren, committen, pushen.

## Regeln

* Nichts erfinden. Jede App braucht eine Quelle (`src`).
* Bei jeder App klarstellen, ob Ausländer sie nutzen können: `use` (ok, limited, no) und `req` (was nötig ist). Nicht nutzbare Apps nicht löschen, sondern mit `use: "no"` markieren.
* Notizen auf Deutsch, eigene Worte, keine Gedankenstriche.
* Einreise-Hinweise beziehen sich auf deutsche Staatsbürger.

## Copyright

© 2026 Timo Feist. Alle Rechte vorbehalten. App-Namen und Marken gehören den jeweiligen Inhabern. Die Quellen stehen je Eintrag im Feld `src`.
