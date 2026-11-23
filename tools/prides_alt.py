#!/usr/bin/env python3
"""Ergänzt in info/prides.json das Feld "alt": andere Schreibweisen der Stadt (deutsch, englisch, Landessprache),
damit die Suche „München“ wie „Munich“ findet. Erneut ausführen, wenn Termine dazukommen.
Aufruf: python -X utf8 tools/prides_alt.py"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(HERE, "info", "prides.json")

# Gruppen gleichwertiger Namen; die Stadt eines Termins bekommt alle anderen Namen ihrer Gruppe
GRUPPEN = [
    "München|Munich|Monaco di Baviera", "Köln|Cologne|Colonia", "Nürnberg|Nuremberg", "Hannover|Hanover",
    "Braunschweig|Brunswick", "Frankfurt am Main|Frankfurt", "Freiburg im Breisgau|Freiburg", "Halle (Saale)|Halle",
    "Offenbach am Main|Offenbach", "Saarbrücken|Saarbruecken", "Düsseldorf|Dusseldorf", "Lübeck|Luebeck",
    "Wien|Vienna|Vienne", "Zürich|Zurich", "Genf|Geneva|Genève|Ginevra", "Bern|Berne", "Basel|Bâle|Basle",
    "Lucerne|Luzern", "Brüssel|Brussels|Bruxelles|Brussel", "Antwerpen|Antwerp|Anvers", "Gent|Ghent|Gand",
    "Liège|Lüttich|Luik", "Luxemburg-Stadt|Luxembourg|Luxemburg|Luxembourg City", "Den Haag|The Hague|'s-Gravenhage|La Haye",
    "Rom|Rome|Roma", "Mailand|Milan|Milano", "Neapel|Naples|Napoli", "Florenz|Florence|Firenze", "Venedig|Venice|Venezia",
    "Genua|Genoa|Genova", "Turin|Torino", "Lissabon|Lisbon|Lisboa", "Sevilla|Seville", "Malaga|Málaga",
    "Palma|Palma de Mallorca|Mallorca|Majorca", "Tenerife|Teneriffa", "Las Palmas de Gran Canaria|Gran Canaria|Las Palmas",
    "Ibiza|Eivissa", "Nice|Nizza", "Strasbourg|Straßburg", "Marseille|Marseilles", "Lille|Rijsel",
    "Prag|Prague|Praha", "Warschau|Warsaw|Warszawa", "Krakau|Krakow|Kraków", "Wroclaw|Breslau|Wrocław",
    "Gdansk|Danzig|Gdańsk", "Poznan|Posen|Poznań", "Brno|Brünn", "Bratislava|Pressburg", "Budapest",
    "Bukarest|Bucharest|București", "Belgrad|Belgrade|Beograd", "Sofia|Sofija", "Athen|Athens|Athina",
    "Thessaloniki|Saloniki", "Kopenhagen|Copenhagen|København", "Göteborg|Gothenburg|Goteborg", "Malmö|Malmo",
    "Reykjavík|Reykjavik", "Tromsø|Tromso", "Helsinki|Helsingfors", "Turku|Åbo", "Tallinn|Reval",
    "Vilnius|Wilna", "Kaunas|Kauen", "Riga", "Kiew|Kyiv|Kiev|Kyjiw", "Ljubljana|Laibach", "Zagreb|Agram",
    "Nicosia|Nikosia|Lefkosia", "Moskau|Moscow", "Tokio|Tokyo", "Seoul|Söul", "Taipei|Taipeh",
    "Singapore|Singapur", "Bangkok", "Delhi|Neu-Delhi|New Delhi", "Mumbai|Bombay", "Kolkata|Kalkutta|Calcutta",
    "Tel Aviv|Tel Aviv-Jaffa", "Cape Town|Kapstadt|Kaapstad", "Johannesburg|Jo'burg",
    "Mexiko-Stadt|Mexico City|Ciudad de México|CDMX", "Cancún & Riviera Maya|Cancún|Cancun|Riviera Maya",
    "Merida|Mérida", "Bogota|Bogotá", "Medellin|Medellín", "Sao Paulo|São Paulo", "Brasilia|Brasília",
    "Montreal|Montréal", "Quebec City|Québec|Quebec", "Guatemala City|Guatemala-Stadt|Ciudad de Guatemala",
    "Panama City|Panama-Stadt|Ciudad de Panamá", "San José|San Jose", "New York|New York City|NYC",
    "Washington|Washington, D.C.|Washington DC", "Los Angeles|LA", "San Francisco|SF",
    "Santiago|Santiago de Chile", "Buenos Aires", "Rio de Janeiro|Rio",
]


def main():
    d = json.load(open(P, encoding="utf-8"))
    karte = {}
    for g in GRUPPEN:
        namen = g.split("|")
        for n in namen:
            karte.setdefault(n.lower(), set()).update(namen)
    n = 0
    for e in d["items"]:
        alle = karte.get(e["city"].lower())
        alt = sorted(x for x in (alle or ()) if x != e["city"])
        if alt:
            if e.get("alt") != alt:
                e["alt"] = alt
                n += 1
        elif "alt" in e:
            del e["alt"]
            n += 1
    with open(P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{n} Termine mit neuen Namen")


if __name__ == "__main__":
    main()
