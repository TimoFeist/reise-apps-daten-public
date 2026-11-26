# Auftrag Vollständigkeit (für Unteragenten, von tools/tiefe.py genutzt)

<ARBEITSORDNER> = Scratchpad-Ordner des Laufs, N = Nummer des Unteragenten.

Du vervollständigst die Daten einer Reise-App (zeigt je Land und Stadt die Apps, die Touristen dort nutzen können). Keine Repo-Änderungen, nur deine Ergebnisdatei.

Ziel: Je Land und Kategorie ALLE relevanten Apps, die man dort als Tourist nutzen kann, nicht nur eine. Deine Länder stehen in <ARBEITSORDNER>/tiefe_N.json: je Land "staedte" (Städte, die die App kennt) und "vorhanden" (je Kategorie die Apps, die schon drin sind, Stadt in Klammern, "weltweit" = weltweite App). Ergänze nur, was FEHLT.

Kategorien: transit (ÖPNV-Tickets/Routenplaner; je Stadt aus "staedte" die offizielle App des Verkehrsbetriebs, dann city = englischer Stadtname), rail (Bahn, Fernbus, Fähre), taxi (Taxi- und Fahrdienst-Apps, auch lokale Taxi-Zentralen großer Städte), carshare (Carsharing, Mietwagen, Wohnmobil per App), micro (Leihräder, E-Scooter, E-Roller), parking (Parken per App, auch städtische), delivery (Essen, Lebensmittel, Schnelllieferung), payment (lokale Wallets/Bezahl-Apps, ehrlich mit Nutzbarkeit), tourism (offizielle Tourismus-Apps, Stadtpässe, Museumspässe, Nationalparks), safety (Notruf-, Warn-, Wetter-Apps), entry (Einreise für Deutsche, nur wenn nötig), maps (lokale Navigation/Offlinekarten, die im Land führend sind), flights (Flughafen-Apps der großen Flughäfen, nationale Airline), hotels (im Land führende Buchungs-Apps, Hütten/Camping), shopping (große Supermarktketten/Händler mit für Touristen nützlicher App, z. B. Öffnungszeiten, Angebote), misc (z. B. landestypischer Messenger, Übersetzung, eSIM NICHT).
Richtwert: in großen Ländern je Kategorie meist 3 bis 8 Apps, bei transit je Stadt eine. Keine Spielereien, nur was Reisende wirklich nutzen.

Arbeitsweise (Websuchen werden von allen Agenten geteilt, höchstens 25 eigene WebSearch-Aufrufe!):
* Hauptwerkzeug ist die Google-Play-Suche per curl/Bash (zählt nicht zum Suchkontingent): https://play.google.com/store/search?q=<begriff>&c=apps&gl=<ISO>&hl=en (Begriffe z. B. taxi, carsharing, parking, scooter, bike share, food delivery, metro <stadt>, bus <stadt>, tourism, weather warning, airport). Paket-IDs aus den Links "/store/apps/details?id=..." lesen, danach die Detailseite https://play.google.com/store/apps/details?id=<pkg>&hl=en&gl=<ISO> abrufen und Titel, Entwickler, Downloadzahl prüfen.
* Aufnehmen nur, wenn der Entwickler der Betreiber, die Stadt, die Behörde oder ein bekanntes Unternehmen ist und die App im Land aktiv ist (Downloads, aktuelle Aktualisierung 2025/2026). Kleine Nachahmer, Fan-Apps und Fahrplan-Apps von Dritten weglassen (außer sie sind im Land Standard, z. B. Moovit).
* src = Betreiberseite oder offizielle Seite, notfalls die Play-Detailseite. Kurz auf der Betreiberseite (WebFetch/curl) nachsehen, wo es geht.
* use "ok" | "limited" | "no" + req (kurze deutsche Bedingung) für deutsche Touristen mit deutscher Nummer und Karte; nur einstufen, was belegt oder offensichtlich ist (z. B. lokale ID/BankID nötig = no), sonst "ok" ohne Vermutung.
* note = kurze deutsche Beschreibung in eigenen Worten, max 60 Zeichen, KEINE Gedankenstriche (– oder —). city nur bei Stadt-Apps (englischer Name). Nichts erfinden, reine iPhone-Apps weglassen.
* Hilfsskripte nur in <ARBEITSORDNER>/agentN ablegen.

Schreibe laufend (nach jedem Land speichern) UTF-8-JSON nach <ARBEITSORDNER>/erg_N.json:
{"apps":[{"cc":"","name":"","cat":"","pkg":"","note":"","city":"","use":"ok","req":"","url":"","nostore":false,"src":""}],"laender_fertig":["DE",...]}
"laender_fertig" = Länder, die du vollständig durchgesehen hast. Antworte am Ende kurz: neue Apps je Land, Unsicherheiten, unfertige Länder.
