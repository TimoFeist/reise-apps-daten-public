# Anleitung: Länder ergänzen

Diese Datei beschreibt, wie neue Länder in `data.json` kommen. Sie ist für die automatischen Läufe und für Handarbeit gleich.

## Ablauf pro Land

1. Nächstes Land aus der Warteliste deines Kontinents `queue/<kontinent>.json` (`todo`, von oben) nehmen. Steht `"recheck": true` dabei, ist das Land schon drin und wird mit den aktuellen Regeln neu abgerufen.
2. Quelle finden: WebSearch `bento.travel <Englischer Ländername> apps` mit `allowed_domains: ["bento.travel","www.bento.travel"]`. Die Länderseite ist meist `https://www.bento.travel/<slug>`.
3. Länderseite mit WebFetch und genau diesem Prompt abrufen:

   > Return ONLY valid minified JSON, no prose. Schema: {"updated":"<Last updated text or empty>","note":"<one German sentence, the most important practical tip from the 'What to know' section, max 140 chars>","apps":[{"name":"","cat":"","pkg":"","ess":true,"note":"","city":"","use":"ok","req":""}]}. Include every app listed on the page EXCEPT: Guac, bento.travel, WhatsApp, Google Translate, Google Maps, any eSIM app. cat must be one of: entry (visa/arrival/customs), transit (city public transport), rail (trains, long-distance bus, ferries), taxi (ride hailing/taxi), carshare (car rental/sharing), micro (bike/scooter), parking, maps (navigation apps other than Google Maps), delivery (food/grocery delivery, restaurants), payment, tourism (attractions, city passes, tours), shopping, safety (emergency, weather warnings), flights, hotels, lgbtq (LGBTQ+ community, dating, gay/queer travel guides), misc. pkg = the Android package id exactly as in the page's Google Play link (id=...), empty if none shown. ess = true if marked Essential. note = short German description, max 60 chars, in your own words. city = English city name if the app only works in one specific city, else empty. use = "no" if the page says a foreign visitor cannot really use it (needs a local phone number, local bank account, local ID, residence or local SIM), "limited" if usable with conditions (e.g. guest mode only, NFC card needed, some features need a local number), otherwise "ok". req = short German note naming the condition (e.g. "Lokale Telefonnummer nötig", "Nur mit lokalem Bankkonto"), empty if use is ok.

4. **Nutzbarkeit für Ausländer prüfen.** Ziel: Für jede App ist klar, ob ein Tourist mit deutscher Handynummer und deutscher Karte sie nutzen kann. Bei Bezahl-Apps, Banking und allen Apps, bei denen die Quelle nichts zur Registrierung sagt, aber eine lokale Nummer, ein lokales Konto oder ein Ausweis typisch ist, mit einer kurzen Suche nachprüfen. Bedingungen in `req` eintragen, `use` entsprechend setzen. Apps mit `use: "no"` bleiben drin, die App zeigt sie ganz unten unter „Nur mit Voraussetzungen“; `req` muss dann sagen, was nötig ist (z. B. „Norwegische Telefonnummer nötig“).
5. Ergebnis als `raw/<ISO>.json` speichern und `"src": "<URL der Länderseite>"` ergänzen.
6. **Fehlende Kategorien gezielt suchen.** Die Länderseite listet oft nur das Wichtigste. Deshalb pro Land zusätzlich je eine Suche (mode standard, bei dünnem Ergebnis extended) für:
   * Carsharing und Mietwagen per App (`carshare`)
   * E-Scooter und Leihräder (`micro`)
   * Taxi und Fahrdienste (`taxi`), falls die Länderseite weniger als 2 nennt
   * Essens- und Lebensmittellieferung (`delivery`), falls die Länderseite weniger als 2 nennt
   Bevorzugt Betreiberseiten, offizielle Stadt- oder Tourismusseiten und aktuelle Artikel (2025/2026). Nur Apps, die es laut Quelle aktuell gibt, mit `use`/`req` wie in Punkt 4 (bei Carsharing typisch: Führerschein-Prüfung in der App, Mindestalter, Kreditkarte). Treffer mit eigenem `src` in dieselbe `raw/<ISO>.json` schreiben.
7. **LGBTQ+ (Kategorie `lgbtq`).**
   * Rechtslage und Sicherheit für LGBTQ+-Reisende prüfen, bevorzugt in den Reise- und Sicherheitshinweisen des Auswärtigen Amts (Abschnitt zu besonderen Strafrechtsbestimmungen) oder bei ILGA World. Ergebnis als ein sachlicher deutscher Satz in `"lgbtq_note"` und Quelle in `"lgbtq_src"` in `raw/<ISO>.json` (z. B. „Gleichgeschlechtliche Handlungen sind strafbar, Dating-Apps werden von der Polizei überwacht.“ oder „Keine strafrechtlichen Einschränkungen, offene Szene in den Großstädten.“).
   * Ist eine weltweite Dating-App (z. B. Grindr) im Land gesperrt oder gefährlich, einen Eintrag mit gleichem `name`/`pkg`, `cat: "lgbtq"`, `use: "no"` und passendem `req` schreiben.
   * Lokale LGBTQ+-Apps und offizielle Pride-/Community-Guides der großen Städte nur mit Quelle aufnehmen.
8. **Städte ergänzen.** Für die 3 bis 5 meistbesuchten Städte des Landes je eine Suche nach der offiziellen ÖPNV-App, dem offiziellen Stadtpass bzw. der Tourismus-App und, falls üblich, der Park-App. Nur aufnehmen, wenn eine offizielle Quelle (Verkehrsbetrieb, Stadt, Tourismusbehörde) die App nennt und `use`/`req` wie in Punkt 4 gesetzt sind. Einträge mit `"city": "<englischer Stadtname>"` und eigenem `"src"` in dieselbe `raw/<ISO>.json` schreiben.
9. Gibt es keine bento-Seite: mit 2 bis 4 Suchen offizielle Quellen finden (Verkehrsbetrieb, Tourismusbehörde, Regierung) und `raw/<ISO>.json` im gleichen Format von Hand schreiben, jede App mit `src`. `pkg` nur, wenn der Paketname in einer Quelle steht. Findet sich nichts Belastbares (z. B. sehr kleine Gebiete), Land ohne Datei als erledigt markieren und im Lauf-Bericht nennen.
10. **Bestehende Einträge des Landes prüfen** (nur wenn das Land schon in `data.json` steht): Einträge ohne `src` und ohne `"mine": true` nachprüfen: bestätigen (als Eintrag mit `src` in `raw/<ISO>.json`) oder, wenn es die App nicht mehr gibt, unter `discontinued` eintragen. Bei Timos eigenen Apps (`"mine": true`) nur prüfen, ob Ausländer sie nutzen können, und das Ergebnis als Eintrag mit gleichem `name`/`pkg` und `use`/`req` in `raw/<ISO>.json` schreiben; `merge_raw.py` übernimmt dann nur diesen Hinweis. Eigene Apps nie löschen.
11. In `raw/<ISO>.json` `"fetched": "<heutiges Datum>"` setzen. Apps, die laut Quelle eingestellt wurden, in `"discontinued": [{"name": "", "pkg": "", "src": ""}]` eintragen; `merge_raw.py` entfernt sie (eigene Apps werden nur markiert).
12. Land in `queue/<kontinent>.json` von `todo` nach `done` verschieben.

## Weltweite Apps (Land „WW“)

Apps unter `WW` erscheinen in der App zusätzlich bei jedem Land, in dem sie funktionieren:
* `"where": "all"`: überall nutzbar (Buchung, Flüge, Touren, Karten, Revolut usw.).
* `"countries": ["DE", ...]`: nur in diesen Ländern, mit `src` als Beleg (z. B. Länderliste des Anbieters oder bento.travel/apps/<app>).
* Ohne beides wird die App nur angezeigt, wo die Länderdaten sie selbst enthalten.
Im Pflege-Modus pro Lauf eine weltweite App ohne Länderliste (z. B. Lime, Voi, Wolt, Uber Eats, FlixBus, Omio, EasyPark) anhand der offiziellen Standortseite des Anbieters mit `countries` und `src` ergänzen.

## Parallel arbeiten (mehrere Aufgaben gleichzeitig)

* Eine alte `queue.json` im Hauptordner ist veraltet: ignorieren und, falls vorhanden, mit `git rm queue.json` entfernen. Länder darin, die schon eine aktuelle `raw/<ISO>.json` haben, gelten als erledigt.

* Jede Aufgabe arbeitet nur mit ihrem Kontinent: `queue/europa.json`, `nordamerika`, `suedamerika`, `asien`, `afrika`, `ozeanien`.
* Aufgaben schreiben **nur** `raw/<ISO>.json` und ihre eigene `queue/<kontinent>.json`. **Nie `data.json` committen**, die baut die GitHub Action „Daten zusammenführen“ nach jedem Push automatisch neu.
* Vor dem Commit prüfen: `python3 merge_raw.py --check` muss ohne Fehler durchlaufen. Danach `git checkout -- data.json`, falls sich etwas geändert hat.
* Hochladen mit Wiederholung, weil andere Aufgaben gleichzeitig pushen:

```
git add raw queue
git commit -m "Länder ergänzt: <ISO-Codes>"
for i in 1 2 3 4 5; do git fetch --depth=50 origin main && git rebase origin/main && git push origin HEAD:main && break; sleep $((i*10)); done
```

## Pflege-Modus (2-Wochen-Rhythmus)

Wenn alle Wartelisten leer sind, übernimmt eine Pflege-Aufgabe. Jedes Land in `data.json` hat ein Feld `checked`.
* In **geraden** Kalenderwochen (ISO): Europa, Nordamerika, Südamerika.
* In **ungeraden** Kalenderwochen: Asien, Afrika, Ozeanien.
* Pro Lauf die Länder der Wochengruppe mit dem ältesten oder fehlenden `checked` nehmen (Länderliste je Kontinent: `done` in `queue/<kontinent>.json`) und genau wie oben neu abrufen (Schritte 2 bis 11). Die alte `raw/<ISO>.json` wird ersetzt.
* Dazu pro Lauf eine weltweite App ohne Länderliste ergänzen (siehe oben).
So ist jedes Land etwa alle 2 Wochen frisch geprüft.

## Nach jedem Lauf

Siehe „Parallel arbeiten“: prüfen, nur `raw/` und `queue/` committen, mit Wiederholung pushen. `data.json` und die Version (Zeitstempel) setzt die GitHub Action.

## Regeln

* Nichts erfinden. Jede App braucht eine Quelle (`src`).
* Bei jeder App klarstellen, ob Ausländer sie nutzen können: `use` (ok, limited, no) und `req` (was nötig ist). Nicht nutzbare Apps nicht löschen, sondern mit `use: "no"` markieren.
* Notizen auf Deutsch, eigene Worte, keine Gedankenstriche.
* Einreise-Hinweise beziehen sich auf deutsche Staatsbürger.

## Copyright

© 2026 Timo Feist. Alle Rechte vorbehalten. App-Namen und Marken gehören den jeweiligen Inhabern. Die Quellen stehen je Eintrag im Feld `src`.
