# Auftrag: Dos, Don'ts, Gesetze und Fakten je Land (LocalAppFinder)

Die Reise-App LocalAppFinder zeigt je Land/Stadt Apps für Urlauber. Neu: kurze, belegte Hinweise für Urlauber aus Deutschland.

## Was je Land sammeln
* `do`: Benimmregeln, die man befolgen sollte (Begrüßung, Schuhe ausziehen, Kleidung in Kirchen/Moscheen/Tempeln, Ramadan, Fotografieren nur mit Erlaubnis …).
* `dont`: Was man lassen sollte (Gesten, Themen, Verhalten, das als unhöflich gilt).
* `gesetz`: Gesetze/Regeln, die Touristen überraschen (Drogen, Alkohol in der Öffentlichkeit, E-Zigaretten-Verbot, Kaugummi, Drohnen, Fotografierverbote an Militär/Behörden, Kleiderordnung am Strand, Ausweispflicht, Bußgelder, Einfuhr von Medikamenten, LGBTQ-Strafrecht nur falls nicht trivial).
* `warnung`: Reisewarnung oder Teilreisewarnung des Auswärtigen Amts (ein Satz, welche Gebiete).
* `fakt`: Lustige oder überraschende, aber belegte Fakten über das Land oder die Stadt.
Trinkgeld nur, wenn das Land in `C:\Win11\Reise-Apps-Daten\info\trinkgeld.json` fehlt.

Umfang: große Reiseländer (viele Apps und Städte in data.json) 8 bis 12 Einträge, dazu für die dort genannten Städte/Urlaubsregionen je 1 bis 3 Einträge mit `city`. Mittlere Länder 5 bis 8. Sehr kleine Gebiete 2 bis 4. Findet sich nichts Belastbares: leere Liste und im Bericht nennen.

## Quellen (Pflicht, jede Zeile eine eigene `src`)
1. Auswärtiges Amt, Reise- und Sicherheitshinweise des Landes (https://www.auswaertiges-amt.de/de/service/laender/<land>-node/<land>sicherheit-...); Abschnitte „Besondere Strafrechtsbestimmungen“, „Hinweise“, „Reiseinfos“. Für Gebiete ohne eigene Seite die Seite des Mutterlandes.
2. Offizielle Tourismusseiten (visit…, Tourismusbehörde), Regierungsseiten, Stadtseiten, UNESCO.
3. Für Fakten auch Wikipedia (Artikel-URL als `src`) oder Guinness World Records.
Nur übernehmen, was du auf der abgerufenen Seite selbst gelesen hast (WebFetch). Nichts aus dem Gedächtnis, nichts erfinden, nichts übertreiben. Ist ein Gesetz geändert worden, den aktuellen Stand nehmen.

## Text
* Deutsch, eigene Worte (nicht abschreiben), höchstens 160 Zeichen, ein bis zwei Sätze, sachlich, freundlich.
* Keine Gedankenstriche (– oder —) und keine Bindestriche als Satzzeichen. Keine Anführungszeichen-Zitate.
* Keine anderen Apps/Projekte erwähnen.
* Zahlen und Bußgelder nur, wenn in der Quelle.

## Ausgabe
Datei `<Notizordner>\kunde\<batch>.json` schreiben (UTF-8), Format:
```
{"DE": [{"art": "do", "de": "…", "city": "", "src": "https://…"}, …], "AT": [...]}
```
`city` = genau der englische Stadtname wie unter `cities` in data.json, sonst leer. Für jedes Land des Auftrags einen Schlüssel (auch leer). Danach `python3 tools/kunde.py einspielen <datei>`.
Zwischendurch speichern (nach je 3 bis 5 Ländern die Datei neu schreiben), damit nichts verloren geht.
Am Ende kurzer Bericht: Anzahl Einträge je Land, Länder ohne Ergebnis.
