# Reise-Apps: Daten

Datendatei für die App **Reise-Apps**. Die App lädt `data.json` beim Start (höchstens einmal am Tag) und über den Knopf „Daten aktualisieren“.

## Aufbau von `data.json`

```json
{
  "schema": 1,
  "version": "2026-11-17",
  "categories": [{ "id": "transit", "name": "Nahverkehr & Tickets", "icon": "🚇" }],
  "countries": [{
    "code": "ES", "name": "Spanien", "flag": "🇪🇸",
    "apps":   [{ "name": "Renfe", "cat": "rail", "note": "...", "pkg": "...", "mine": true, "src": "https://..." }],
    "cities": [{ "name": "Madrid", "match": ["Madrid"], "apps": [ ... ] }]
  }]
}
```

* `version` muss bei jeder Änderung höher werden (Datum im Format JJJJ-MM-TT), sonst übernimmt die App die Datei nicht.
* `code` ist der ISO-Ländercode (so liefert ihn auch die Standortbestimmung). `WW` = Weltweit.
* `pkg` ist der Android-Paketname. Nur eintragen, wenn er belegt ist. Ohne `pkg` sucht die App im Play Store nach dem Namen.
* `url` statt `pkg` für reine Web-Angebote.
* `mine: true` = stammt aus Timos eigenen Ordnern (Stern in der App).
* `src` = Quelle der Recherche.
* `match` = Ortsnamen, an denen die App die Stadt beim Standort erkennt (Deutsch, Englisch, Landessprache).

## Stand

* Etappe 1: 27 Länder aus den Nova-Ordnern + Weltweit + Südafrika/Kenia (aus dem Afrika-Ordner).
* Weitere Länder folgen in Etappen. Monatlich werden Links und Apps geprüft.
