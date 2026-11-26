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
    Hat eine App einen neuen Paketnamen oder gibt es sie nur noch im Web bzw. als APK, in `"replace": [{"old": "<alter pkg>", "pkg": "<neuer pkg>", "name": "", "note": "", "url": "", "nostore": false, "src": ""}]` eintragen. Das gilt auch für Timos eigene Einträge; den neuen Paketnamen vorher auf play.google.com prüfen.
12. Land in `queue/<kontinent>.json` von `todo` nach `done` verschieben.

## Weitere Quellen, wenn nichts Spezielles zu finden ist

Findet sich bei bento.travel, beim Betreiber oder bei Stadt und Tourismusbehörde nichts, der Reihe nach weitersuchen. Erst wenn alle Stufen leer sind, gilt ein Land oder eine Stadt als „nichts Belegtes“.
1. **Google Play Suche:** `https://play.google.com/store/search?q=<Ort>+<Begriff>&c=apps&gl=<ISO>` (Begriffe: taxi, bus, metro, transit, ferry, parking, tourism, visa, weather, delivery). Treffer zählen nur, wenn der Entwickler der Betreiber, die Stadt, die Behörde oder ein bekanntes Unternehmen ist.
2. **Apple App Store:** Suchschnittstelle `https://itunes.apple.com/search?term=<Begriff>+<Ort>&country=<iso klein>&entity=software&limit=25` (Felder `trackName`, `sellerName`, `trackViewUrl`, `primaryGenreName`). Gibt es den Ländercode im App Store nicht (Antwort 400), mit `country=us` und dem Ortsnamen im Suchbegriff suchen. Die App-Store-Seite darf `src` sein, wenn `sellerName` der Betreiber ist. Für die Android-App trotzdem den Paketnamen bei Google Play suchen und prüfen; gibt es keine Android-Version, nur mit Web-Angebot (`url` + `nostore: true`) aufnehmen.
3. **Huawei AppGallery:** `https://appgallery.huawei.com/search/<Begriff>` (wichtig vor allem für China und Länder, in denen Google-Dienste fehlen). Wie beim App Store: als Beleg nutzbar, Eintrag braucht Play-Paket oder Web-Angebot.
4. **Weitere Belege:** Seiten des Auswärtigen Amts (Einreise, Notfall), Flughafen-Seiten (Taxi, Transfer), Fährgesellschaften, nationale Wetterdienste, Seiten von Mobilfunkanbietern (Bezahl-Apps) und aktuelle Reiseartikel 2025/2026.
5. **Weltweite Apps prüfen:** Ist in einem Land wirklich kein lokaler Anbieter belegbar, prüfen, ob weltweite Apps dort laut Anbieter-Standortliste funktionieren (Uber, Bolt, inDrive, Yango, Careem, Grab, Moovit, Rome2Rio, Wolt, Glovo usw.), und dann beim Eintrag in `WW` das Land in `countries` ergänzen.

Alle Regeln gelten weiter: nichts erfinden, Paketnamen selbst prüfen, `use`/`req` ehrlich setzen.

## Automatische Store-Prüfung (wöchentlich)

Die GitHub Action „Store-Prüfung“ ruft jeden Montag alle Paketnamen bei Google Play ab (`tools/store_check.py`) und schreibt Auffälligkeiten nach `queue/store-pruefung.json`: Apps, die es nicht mehr gibt, und Apps, deren Play-Titel sich stark geändert hat. Jeder Pflege-Lauf arbeitet diese Liste zuerst ab: Nachfolger oder Web-Angebot suchen und per `replace` eintragen, sonst `discontinued`. Erledigte Einträge aus der Liste entfernen.

## iPhone-Versionen (täglich, automatisch)

Die GitHub Action „iPhone-Apps zuordnen“ sucht zu jeder App die iPhone-Version über die Apple-Suche (`tools/ios_ids.py`, bis zu 1200 Apps pro Tag) und schreibt sie nach `info/ios.json`. Zugeordnet wird nur, wenn Bundle-ID gleich Paketname ist oder Name und Anbieter (laut Google Play) zusammenpassen. `merge_raw.py` setzt daraus `"ios": <App-Store-ID>` an jeder App. Apps ohne Treffer stehen mit `"id": 0` drin und werden nach 30 Tagen neu gesucht. Eine falsche Zuordnung von Hand in `info/ios.json` auf `"id": 0, "fix": true` setzen (oder die richtige ID mit `"fix": true`). `ios` nie in `raw/` eintragen.

## Feiertage und Stadt-Koordinaten (automatisch)

Dieselbe tägliche Action lädt einmal pro Woche die gesetzlichen Feiertage aller Länder für dieses und nächstes Jahr (`tools/feiertage.py`, Quelle date.nager.at, nach `info/feiertage.json`) und sucht Koordinaten für neue Städte (`tools/city_geo.py`, Open-Meteo/GeoNames CC BY 4.0, nach `info/stadt-koordinaten.json`). `merge_raw.py` setzt daraus `info.holidays` (ab gestern etwa 400 Tage) und `ll` an jeder Stadt. Falsche Koordinaten von Hand in `info/stadt-koordinaten.json` korrigieren. Nichts davon in `raw/` eintragen.

## Fehlende Paketnamen (automatisch)

Dieselbe Action sucht für Apps ohne `pkg` (außer `nostore`/`dl`) den Google-Play-Eintrag (`tools/pkg_suche.py`, bis zu 400 pro Tag, nach `info/pkg.json`). Übernommen wird nur, wenn der Play-Titel zum Namen passt und ein Beleg dazukommt: gleiche Domain wie `url`/`src` (`domain`), Behördendomain desselben Landes (`gov`), gleicher Name mit diesem Paket in einem anderen Land (`daten`), gleicher Anbieter wie die iPhone-Version (`apple`) oder Titel und Entwickler beginnen eindeutig mit dem Namen (`anbieter`). Die beiden schwachen Belege `daten` und `anbieter` trägt der tägliche Lauf nicht selbst ein, sondern setzt sie als `vorschlag` auf die Prüfliste (Erstlauf am 23.11.2026 mit `--alle` und Durchsicht von Hand, 33 Fehlgriffe als `abgelehnt` gesperrt). `merge_raw.py` setzt daraus `pkg`, wenn der Eintrag keinen hat. Alles ohne sicheren Treffer steht mit Kandidaten in `queue/pkg-pruefung.json`; den richtigen Paketnamen dann von Hand in `info/pkg.json` als `{"pkg": "...", "fix": true}` eintragen (oder direkt in `raw/`). Falsche Zuordnung: `{"pkg": "", "fix": true}`.

## App-Logos (automatisch)

Dieselbe Action sucht zu jeder App mit Paketname die Adresse ihres Logos auf der Google-Play-Seite (`tools/icons.py`, nach `info/icons.json`, gefundene alle 30 Tage, fehlende alle 14 Tage neu). Es werden keine Bilder gespeichert oder über unsere Server verteilt: `merge_raw.py` setzt nur `"ic"` (Pfad hinter `https://play-lh.googleusercontent.com/`) an jede App, App und Web-Version laden das Logo direkt von Google Play. `ic` nie in `raw/` eintragen.

## Leihräder, E-Scooter und Carsharing aus GBFS (automatisch)

Dieselbe tägliche Action liest die offene Liste aller GBFS-Systeme von MobilityData (`tools/gbfs.py`, Lizenz CC BY 3.0, nach `info/gbfs.json`). Aus dem Feed jedes Betreibers kommen nur Name, Ort, Fahrzeugarten und die offizielle Android-App; jeder Paketname wird bei Google Play geprüft. `merge_raw.py` (`add_gbfs`) baut daraus bei jedem Lauf neu Einträge mit `"auto": "gbfs"`: Kategorie `micro` (bei reinen Auto-Systemen `carshare` mit Hinweis Führerscheinprüfung), in der Stadt, wenn das System nur in einer unserer Städte fährt, sonst auf Landesebene mit den Orten in `note` (höchstens 12 je Land, Systeme mit vielen Orten zuerst). Steht die App im Land schon (gleicher Paketname), passiert nichts; weltweite Apps mit Länderliste (z. B. Lime, Voi, Bolt) bekommen nur das Land dazu. `auto`-Einträge nie in `raw/` kopieren oder von Hand ändern; Korrekturen als normaler Eintrag mit gleichem `pkg` in `raw/<ISO>.json`, der hat Vorrang.

## Lücken füllen (wöchentlich, Aufgabe „laf-luecken-fuellen“)

`python3 tools/luecken.py` schreibt alle Länder mit einer leeren Kernkategorie nach `queue/luecken.json` (transit, rail, taxi, carshare, micro, parking, delivery, payment, tourism, safety, entry; `entry` nicht für EU/EWR/Schweiz). Weltweite Apps zählen nur mit Länderliste. Länder mit vielen Einträgen kommen zuerst. Wer eine Lücke ohne Ergebnis gesucht hat, trägt sie als leer ein; sie ruht dann 120 Tage (`info/luecken-versuche.json`).

Ablauf je Lauf: Liste erzeugen, die ersten etwa 120 Lücken recherchieren (Regeln wie oben: offizielle Quellen, Paketname bei Google Play geprüft, `use`/`req` ehrlich, `note` max. 60 Zeichen ohne Gedankenstriche, nur iPhone = weglassen), Ergebnis als
`{"apps": [{"cc","name","cat","pkg","note","city","use","req","url","nostore","src"}], "leer": [{"cc","cat","notiz"}]}`
speichern und mit `python3 tools/luecken_einspielen.py <datei>` einspielen. Das Werkzeug prüft die Einträge, schreibt `raw/<ISO>.json` und merkt sich die Versuche. Danach `merge_raw.py`, `tools/luecken.py` neu, committen und pushen.

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
* Vorher `queue/store-pruefung.json` abarbeiten (siehe „Automatische Store-Prüfung“).
* Dazu pro Lauf eine weltweite App ohne Länderliste ergänzen (siehe oben).
* Länder oder Städte ohne Einträge mit den „Weiteren Quellen“ erneut versuchen.
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
