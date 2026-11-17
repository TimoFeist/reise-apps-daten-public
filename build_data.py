#!/usr/bin/env python3
"""Baut data.json für die Reise-Apps App.
Quellen: Timos Nova-Ordner (mine=True, Paketname aus dem Backup = verifiziert)
und recherchierte Ergänzungen (mine=False, pkg nur wenn belegt, sonst Play-Store-Suche per Name)."""
import json, sys

VERSION = sys.argv[2] if len(sys.argv) > 2 else "2026-11-17"
folders = json.load(open(sys.argv[1]))

CATS = [
    ("entry", "Visa & Einreise", "🛂"),
    ("transit", "Nahverkehr & Tickets", "🚇"),
    ("rail", "Bahn, Bus & Fähre", "🚆"),
    ("taxi", "Taxi & Fahrdienste", "🚕"),
    ("carshare", "Carsharing & Mietwagen", "🚗"),
    ("micro", "Scooter & Fahrräder", "🛴"),
    ("parking", "Parken", "🅿️"),
    ("maps", "Karten & Navigation", "🗺️"),
    ("delivery", "Lieferdienste & Essen", "🍔"),
    ("payment", "Bezahlen & Banking", "💳"),
    ("tourism", "Tourismus & Stadtpässe", "🎟️"),
    ("shopping", "Einkaufen", "🛒"),
    ("safety", "Notfall & Sicherheit", "🆘"),
    ("flights", "Flüge & Flughafen", "✈️"),
    ("hotels", "Unterkünfte & Buchen", "🏨"),
    ("misc", "Sonstiges", "📱"),
]

# Kategorie je Paketname (Timos Apps)
CAT = {}
def c(cat, *pkgs):
    for p in pkgs: CAT[p] = cat
c("taxi", "com.gettaxi.android", "ee.mtakso.client", "com.cabify.rider", "me.lyft.android", "taxi.android.client",
  "com.careem.acma", "com.ubercab", "com.grabtaxi.passenger", "com.ryde_android", "com.mobi.passenger", "ride.app",
  "com.letzride", "com.customer.goosty", "ai.bliq.passenger", "tel.pingme")
c("rail", "com.thetrainline", "uk.co.icectoc.customer", "com.avantiwestcoast", "com.firstscotrail", "at.oebb.ts",
  "at.westbahn.app", "ch.sbb.mobile.android.b2c", "com.lynxspa.prontotreno", "no.flytoget.flytoget",
  "se.arlandaexpress.atrain", "de.hafas.android.irishrail", "com.aircoach.android", "de.hafas.android.cfl",
  "pl.loyaltyclub.polferriescard", "de.hafas.android.db", "de.flixbus.app", "com.goeuro.rosie")
c("transit", "uk.co.oxfordbuscompany", "uk.gov.tfl.gotfl", "koeln.kvb.ticket.app", "com.mentz.mobilnrw_cibo_app",
  "de.eos.uptrade.android.fahrinfo.hamburg", "de.hochbahn.hvvswitch", "de.hafas.android.svv", "ch.swift.willi",
  "ch.mnc.zvv.oneapp", "com.crtm.virtual", "it.atm.appmobile", "com.rsm.muoversiaroma", "com.applidium.vianavigo",
  "no.ruter.reise", "com.vaesttrafik.vaesttrafik", "se.skanetrafiken.washington", "com.sl.SLBiljetter",
  "lv.mobilly.android", "fi.hsl.app", "com.arriva.glimble", "com.themobilecompany.delijn", "de.hafas.android.cdt",
  "zbiletem.zbiletem", "com.att.android.tfa", "com.mbta.mobileapp", "sg.com.smrt.smrtconnect", "com.mpt.tallinjaapp",
  "de.eos.uptrade.android.fahrinfo.berlin", "de.mvg.more", "uk.gov.tfl.gotfl", "com.neosistec.navilensgo")
c("carshare", "de.cantamen.stadtmobil", "com.mobilityinternational.classic.client103", "com.ufodrive.app",
  "com.goget.goget", "com.flexicar.app", "au.popcar.classic.client101", "au.com.carnextdoor.app", "com.sixt.reservation",
  "com.car2go", "com.driveby.app", "com.hertz.hod", "de.billigermietwagen.app.de", "com.rentcars.rentcarscom")
c("micro", "co.bird.android", "com.superpedestrian.link", "hr.infoart.epk", "io.voiapp.voi", "com.limebike",
  "com.tier.app", "com.escooterapp")
c("parking", "com.elparking.elparking", "group.flowbird.mpp", "au.com.secureparking.production",
  "au.gov.nsw.onegov.parknpay.release", "net.easypark.android", "is.parka.parka")
c("delivery", "com.ubercab.eats", "uk.takeaway.android", "com.glovo", "com.justeat.app.it", "se.onlinepizza",
  "com.deliveroo.orderapp", "com.pickery.app", "com.wedely", "com.bolt.deliveryclient", "com.food.ordering",
  "com.wolt.android", "com.grubhub.android", "com.dd.doordash", "com.global.foodpanda.android", "com.oddleeatsapp",
  "com.mcdonalds.app.uk", "com.tacobelluk.app", "es.burgerking.android", "es.tacobell.app", "com.yourvoice.ccApp",
  "it.burgerking.android", "com.md.mcdonalds.gomcdo", "com.mcdo.mcdonalds", "se.caspeco.bstl.tacobar",
  "com.slics.joos", "com.app.tgtg", "com.lafourchette.lafourchette")
c("payment", "uk.co.walkinapp.prod", "com.satispay.customer", "se.bankgirot.swish", "com.bankid.bus",
  "com.mls.nets.reader", "com.ocbc.mobile", "com.revolut.revolut", "com.paypal.android.p2pmobile")
c("tourism", "com.gocitypass", "com.todaytix.TodayTix", "uk.eventim.mobile.app.Android", "com.ticketswap.ticketswap",
  "com.feverup.fever", "com.ticketmaster.mobile.android.uk", "com.EuropaParkMackKG.EPGuide", "org.sagradafamilia.droid",
  "it.prometheus.onepass", "com.bigbustours.bbt", "no.wtw.visitoslo.oslopass.android", "se.liseberg.liseberg",
  "com.viator.mobile.android", "com.klook", "com.aurorareach.app", "com.helloaurora", "com.solinor.loyaltybeacon",
  "com.tomorrowland.oneworldradio", "lu.vdl", "com.visit_greece", "com.hornblower.hornblower",
  "com.universalstudios.orlandoresort", "com.seaworld.mobile", "com.xcaret.xcaret_parques", "kr.co.waug.waug",
  "com.getyourguide.android", "com.tiqets.tiqetsapp", "com.civitatis.civitatis", "com.ticketmaster.tickets.international")
c("shopping", "es.dia", "com.target.ui", "com.wholefoods.wholefoodsmarket", "com.cvs.launchers.cvs")
c("flights", "com.changiairport.cagapp", "com.iberia.android", "com.brusselsairlines.bmobile", "com.redmadrobot.pins")
c("hotels", "otg.thonhotel")

# Ländercode, Name, Flagge, Nova-Ordner
COUNTRIES = [
    ("GB", "Großbritannien", "🇬🇧", ["Großbritannien"]),
    ("DE", "Deutschland", "🇩🇪", ["Deutschland"]),
    ("AT", "Österreich", "🇦🇹", ["Österreich"]),
    ("CH", "Schweiz", "🇨🇭", ["Schweiz & Österreich"]),
    ("ES", "Spanien", "🇪🇸", ["Spain"]),
    ("IT", "Italien", "🇮🇹", ["Italien"]),
    ("PT", "Portugal", "🇵🇹", ["Portugal"]),
    ("FR", "Frankreich", "🇫🇷", ["Frankreich"]),
    ("NO", "Norwegen", "🇳🇴", ["Norwegen"]),
    ("SE", "Schweden", "🇸🇪", ["Schweden"]),
    ("FI", "Finnland", "🇫🇮", ["Finnland"]),
    ("EE", "Estland", "🇪🇪", ["Baltikum"]),
    ("LV", "Lettland", "🇱🇻", ["Baltikum"]),
    ("LT", "Litauen", "🇱🇹", ["Baltikum"]),
    ("NL", "Niederlande", "🇳🇱", ["Niederlande"]),
    ("BE", "Belgien", "🇧🇪", ["Belgien"]),
    ("LU", "Luxemburg", "🇱🇺", ["Luxemburg"]),
    ("PL", "Polen", "🇵🇱", ["Polen"]),
    ("IS", "Island", "🇮🇸", ["Island"]),
    ("IE", "Irland", "🇮🇪", ["Irland"]),
    ("GR", "Griechenland", "🇬🇷", ["Griechenland"]),
    ("MT", "Malta", "🇲🇹", ["Malta"]),
    ("US", "USA", "🇺🇸", ["USA"]),
    ("MX", "Mexiko", "🇲🇽", ["Mexico"]),
    ("AU", "Australien", "🇦🇺", ["Australien"]),
    ("SG", "Singapur", "🇸🇬", ["Singapur"]),
    ("AE", "Vereinigte Arabische Emirate", "🇦🇪", ["Persischer Golf"]),
]
# "Afrika" ist ein Kontinent-Ordner: Apps landen bei Südafrika und Kenia nur mit Hinweis
AFRICA = [("ZA", "Südafrika", "🇿🇦"), ("KE", "Kenia", "🇰🇪")]

# Stadtzuordnung für Timos Apps: pkg -> (Land, Stadt)
CITY_OF = {
    "uk.co.oxfordbuscompany": ("GB", "Oxford"), "uk.gov.tfl.gotfl": ("GB", "London"),
    "koeln.kvb.ticket.app": ("DE", "Köln"), "com.mentz.mobilnrw_cibo_app": ("DE", "Nordrhein-Westfalen"),
    "de.eos.uptrade.android.fahrinfo.hamburg": ("DE", "Hamburg"), "de.hochbahn.hvvswitch": ("DE", "Hamburg"),
    "com.EuropaParkMackKG.EPGuide": ("DE", "Rust (Europa-Park)"), "de.cantamen.stadtmobil": None,
    "de.hafas.android.svv": ("AT", "Salzburg"),
    "ch.mnc.zvv.oneapp": ("CH", "Zürich"),
    "com.crtm.virtual": ("ES", "Madrid"), "org.sagradafamilia.droid": ("ES", "Barcelona"),
    "it.atm.appmobile": ("IT", "Mailand"), "com.rsm.muoversiaroma": ("IT", "Rom"),
    "com.applidium.vianavigo": ("FR", "Paris"),
    "no.wtw.visitoslo.oslopass.android": ("NO", "Oslo"), "no.flytoget.flytoget": ("NO", "Oslo"), "no.ruter.reise": ("NO", "Oslo"),
    "com.vaesttrafik.vaesttrafik": ("SE", "Göteborg"), "se.liseberg.liseberg": ("SE", "Göteborg"),
    "se.arlandaexpress.atrain": ("SE", "Stockholm"), "com.sl.SLBiljetter": ("SE", "Stockholm"),
    "se.skanetrafiken.washington": ("SE", "Malmö"),
    "fi.hsl.app": ("FI", "Helsinki"),
    "lv.mobilly.android": ("LV", "Riga"),
    "com.themobilecompany.delijn": None,
    "lu.vdl": ("LU", "Luxemburg-Stadt"),
    "com.att.android.tfa": ("GR", "Athen"),
    "com.mbta.mobileapp": ("US", "Boston"), "com.universalstudios.orlandoresort": ("US", "Orlando"),
    "com.seaworld.mobile": ("US", "Orlando"), "com.todaytix.TodayTix": None, "com.hornblower.hornblower": None,
    "au.gov.nsw.onegov.parknpay.release": ("AU", "Sydney"),
    "com.xcaret.xcaret_parques": ("MX", "Cancún & Riviera Maya"),
}

CITY_MATCH = {
    "London": ["London", "Greater London"], "Oxford": ["Oxford", "Oxfordshire"],
    "Köln": ["Köln", "Cologne"], "Nordrhein-Westfalen": ["Nordrhein-Westfalen", "North Rhine-Westphalia"],
    "Hamburg": ["Hamburg"], "Rust (Europa-Park)": ["Rust", "Ortenaukreis"], "Berlin": ["Berlin"], "München": ["München", "Munich"],
    "Salzburg": ["Salzburg"], "Wien": ["Wien", "Vienna"], "Zürich": ["Zürich", "Zurich"], "Basel": ["Basel"],
    "Madrid": ["Madrid"], "Barcelona": ["Barcelona"], "Mailand": ["Mailand", "Milano", "Milan"], "Rom": ["Rom", "Roma", "Rome"],
    "Florenz": ["Florenz", "Firenze", "Florence"],
    "Paris": ["Paris", "Île-de-France", "Ile-de-France"], "Oslo": ["Oslo"], "Göteborg": ["Göteborg", "Gothenburg", "Västra Götaland"],
    "Stockholm": ["Stockholm"], "Malmö": ["Malmö", "Skåne"], "Helsinki": ["Helsinki", "Uusimaa"], "Riga": ["Riga", "Rīga"],
    "Luxemburg-Stadt": ["Luxembourg", "Luxemburg"], "Athen": ["Athen", "Athens", "Athina", "Attica", "Attika"],
    "Boston": ["Boston"], "Orlando": ["Orlando", "Orange County"], "New York": ["New York"], "Sydney": ["Sydney"],
    "Melbourne": ["Melbourne"], "Cancún & Riviera Maya": ["Cancún", "Cancun", "Quintana Roo", "Playa del Carmen"],
    "Dubai": ["Dubai"], "Lissabon": ["Lissabon", "Lisboa", "Lisbon"], "Porto": ["Porto"], "Amsterdam": ["Amsterdam"],
    "Brüssel": ["Brüssel", "Brussels", "Bruxelles", "Brussel"], "Dublin": ["Dublin"], "Reykjavík": ["Reykjavík", "Reykjavik", "Capital Region"],
    "Edinburgh": ["Edinburgh"], "Wien": ["Wien", "Vienna"],
}

NOTE = {
    "com.gocitypass": "Stadtpass für viele Städte", "com.crtm.virtual": "Virtuelle Madrider ÖPNV-Karte",
    "com.applidium.vianavigo": "Île-de-France Mobilités (Navigo, Tickets)", "ch.swift.willi": "ÖBB-Mobilitäts-App (wegfinder)",
    "hr.infoart.epk": "bmove", "com.redmadrobot.pins": "airBaltic", "com.solinor.loyaltybeacon": "Cluby",
    "com.tomorrowland.oneworldradio": "Tomorrowland", "it.prometheus.onepass": "OnePass",
}

def entry(name, pkg=None, cat=None, note="", mine=False, src=None, url=None):
    d = {"name": name, "cat": cat or CAT.get(pkg, "misc")}
    if pkg: d["pkg"] = pkg
    if url: d["url"] = url
    if note: d["note"] = note
    if mine: d["mine"] = True
    if src: d["src"] = src
    return d

def is_web(pkg):
    return pkg is None or pkg.startswith("org.chromium.webapk") or pkg in ("com.android.chrome", "org.mozilla.firefox")

# ---------- Recherchierte Ergänzungen (Etappe 1, Stand 17.11.2026) ----------
# pkg nur dort, wo das Paket aus Timos Backup stammt. Sonst sucht die App im Play Store nach dem Namen.
R = {
    "GB": [
        entry("UK ETA", cat="entry", note="Offizielle App des Home Office für die ETA. Ob du eine brauchst: gov.uk/electronic-travel-authorisation", src="https://www.gov.uk/electronic-travel-authorisation"),
    ],
    "US": [
        entry("ESTA Mobile", cat="entry", note="Offizielle CBP-App für ESTA (Visa Waiver Program)", src="https://esta.cbp.dhs.gov/"),
    ],
    "AU": [
        entry("eVisitor (ImmiAccount, Web)", cat="entry", url="https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/evisitor-651",
              note="Deutsche Pässe: eVisitor 651 kostenlos über ImmiAccount, nicht über die ETA-App", src="https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/evisitor-651"),
        entry("Opal Travel", cat="transit", note="Offizielle App von Transport for NSW", src="https://transportnsw.info/plan/transport-apps/opal-travel-app"),
        entry("Uber", "com.ubercab", "taxi"),
    ],
    "SG": [
        entry("MyICA Mobile", cat="entry", note="SG Arrival Card, innerhalb von 3 Tagen vor Ankunft, kostenlos", src="https://www.ica.gov.sg/enter-depart/entry_requirements/sg-arrival-card"),
        entry("MyTransport.SG", cat="transit", note="Offizielle LTA-App: Bus- und MRT-Ankunftszeiten", src="https://www.bento.travel/singapore/transit"),
        entry("SimplyGo", cat="transit", note="Fahrpreise, Karte; Bezahlen geht auch direkt mit Visa/Mastercard"),
        entry("Grab", "com.grabtaxi.passenger", "taxi", note="Wichtigster Fahrdienst, kein Uber in Singapur"),
        entry("Gojek", cat="taxi", note="Alternative zu Grab, zum Preisvergleich"),
        entry("CDG Zig", cat="taxi", note="Taxis von ComfortDelGro"),
    ],
    "AE": [
        entry("S'hail", cat="transit", note="Offizieller RTA-Planer für Metro, Tram, Bus, Wassertaxi in Dubai", src="https://www.bento.travel/united-arab-emirates/transit"),
        entry("nol Pay", cat="transit", note="nol-Karte per NFC aufladen (Dubai)"),
    ],
    "FR": [
        entry("SNCF Connect", cat="rail", note="Offizielle App der französischen Bahn"),
        entry("Bonjour RATP", cat="transit", note="Offizielle RATP-App für Metro, RER, Bus in Paris"),
        entry("G7 Taxi", cat="taxi", note="Lizenzierte Taxis in Paris und vielen Städten"),
    ],
    "IT": [
        entry("Italo", cat="rail", note="Privater Hochgeschwindigkeitszug, oft günstiger als Frecciarossa"),
        entry("Moovit", cat="maps", note="Bus und Metro in vielen italienischen Städten"),
        entry("FREE NOW", "taxi.android.client", "taxi"),
        entry("itTaxi", cat="taxi", note="Taxi-App, besonders gut in Florenz"),
    ],
    "ES": [
        entry("Renfe", cat="rail", note="Spanische Staatsbahn"),
        entry("iryo", cat="rail", note="Privater Hochgeschwindigkeitszug"),
        entry("OUIGO España", cat="rail", note="Günstiger Hochgeschwindigkeitszug"),
        entry("ALSA", cat="rail", note="Fernbusse in Spanien"),
        entry("FREE NOW", "taxi.android.client", "taxi", note="Laut Quellen beste Taxi-App in Barcelona"),
    ],
    "PT": [
        entry("CP Comboios de Portugal", cat="rail", note="Offizielle Bahn-App, z. B. Lissabon–Porto"),
        entry("Rede Expressos", cat="rail", note="Fernbusse in Portugal"),
        entry("Moovit", cat="maps", note="ÖPNV in Lissabon und Porto"),
    ],
    "NL": [
        entry("NS", cat="rail", note="Offizielle App der niederländischen Bahn"),
        entry("9292", cat="transit", note="ÖPNV-Planer für alle Verkehrsbetriebe in den Niederlanden"),
        entry("OVpay", cat="transit", note="Check-in/out mit Bankkarte oder Handy, ohne Registrierung"),
    ],
    "NO": [
        entry("Entur", cat="transit", note="Alle Busse, Züge, Fähren in Norwegen, Tickets"),
        entry("Vy", cat="rail", note="Züge und Busse"),
        entry("Vipps", cat="payment", note="Braucht eine norwegische Nummer, Karte reicht meist"),
        entry("EasyPark", "net.easypark.android", "parking"),
        entry("Yr", cat="misc", note="Wetter vom norwegischen Wetterdienst"),
    ],
    "SE": [
        entry("SJ", cat="rail", note="Schwedische Bahn"),
        entry("EasyPark", "net.easypark.android", "parking"),
    ],
    "FI": [],
    "DE": [
        entry("DB Navigator", "de.hafas.android.db", "rail", mine=True),
        entry("FlixBus", "de.flixbus.app", "rail", mine=True),
        entry("BahnBonus", "com.deutschebahn.bahnbonus", "rail", mine=True),
    ],
    "AT": [
        entry("WienMobil", cat="transit", note="Offizielle App der Wiener Linien"),
        entry("ÖBB Scotty", cat="rail", note="Fahrplanauskunft ÖBB"),
    ],
    "CH": [
        entry("TWINT", cat="payment", note="Schweizer Bezahl-App, nicht für jeden Besucher nutzbar"),
    ],
    "IS": [
        entry("112 Iceland", cat="safety", note="Offizielle Notruf-App, sendet Standort an 112", src="https://www.bento.travel/iceland"),
        entry("SafeTravel", cat="safety", note="ICE-SAR: Warnungen, Straßenzustand, Reiseplan hinterlegen"),
        entry("Veður", cat="misc", note="Isländischer Wetterdienst mit Warnungen"),
        entry("Klappið", cat="transit", note="Strætó-Busse im Großraum Reykjavík"),
    ],
    "IE": [
        entry("TFI Live", cat="transit", note="Offizieller Planer für Bus, Luas, Irish Rail", src="https://www.bento.travel/ireland/transit"),
    ],
    "PL": [
        entry("Jakdojade", cat="transit", note="ÖPNV und Tickets in über 130 polnischen Städten", src="https://www.bento.travel/poland/transit"),
        entry("Koleo", cat="rail", note="Zugtickets in Polen"),
    ],
    "MT": [
        entry("eCabs", cat="taxi", note="Fahrdienst in Malta (nicht auf Gozo)"),
        entry("Gozo Channel", cat="rail", note="Fähre Malta–Gozo"),
    ],
}
R_CITY = {
    ("DE", "München"): [entry("MVGO", "de.mvg.more", "transit", mine=True)],
    ("DE", "Berlin"): [entry("Fahrinfo Berlin", "de.eos.uptrade.android.fahrinfo.berlin", "transit", mine=True)],
    ("ES", "Madrid"): [entry("Metro de Madrid", cat="transit", note="Offizielle Metro-App"), entry("EMT Madrid", cat="transit", note="Stadtbusse Madrid")],
    ("ES", "Barcelona"): [entry("TMB App", cat="transit", note="Metro und Bus Barcelona"),
                          entry("Smou", cat="parking", note="Städtische Mobilitäts-App: Parken, Bicing, Laden")],
    ("AT", "Wien"): [entry("WienMobil", cat="transit", note="Offizielle App der Wiener Linien")],
    ("FR", "Paris"): [entry("Bonjour RATP", cat="transit", note="Offizielle RATP-App für Metro, RER, Bus")],
    ("IT", "Florenz"): [entry("itTaxi", cat="taxi", note="Taxi-App, in Florenz besonders verbreitet")],
    ("PT", "Lissabon"): [entry("Carris Metropolitana", cat="transit", note="Busse im Großraum Lissabon"),
                         entry("navegante", cat="transit", note="Echtzeitinfo für ÖPNV im Großraum Lissabon")],
    ("AE", "Dubai"): [entry("S'hail", cat="transit", note="Offizieller RTA-Planer"), entry("nol Pay", cat="transit", note="nol-Karte aufladen")],
    ("AU", "Sydney"): [entry("Opal Travel", cat="transit", note="Offizielle Transport-for-NSW-App")],
    ("IS", "Reykjavík"): [entry("Klappið", cat="transit", note="Strætó-Busse, digitale Tickets")],
    ("IE", "Dublin"): [entry("Leap Top-Up", cat="transit", note="Leap Card aufladen")],
}

# ---------- Weltweit ----------
WW_PKGS = ["com.google.android.apps.maps", "com.rome2rio.www.rome2rio", "com.ubercab", "ee.mtakso.client", "com.booking",
           "com.airbnb.android", "com.getyourguide.android", "com.klook", "com.tiqets.tiqetsapp", "com.viator.mobile.android",
           "com.flightradar24free", "com.tripit", "com.skypicker.main", "com.revolut.revolut", "com.lufthansa.android.lufthansa",
           "com.plannet.milesandmoreapp", "com.prioritypass3", "com.staralliance.navigator", "com.limebike", "io.voiapp.voi",
           "com.wolt.android", "com.ubercab.eats", "de.flixbus.app", "com.goeuro.rosie", "net.easypark.android"]
WW_NAMES = {"com.google.android.apps.maps": ("Google Maps", "maps"), "com.rome2rio.www.rome2rio": ("Rome2Rio", "maps"),
            "com.ubercab": ("Uber", "taxi"), "ee.mtakso.client": ("Bolt", "taxi"), "com.booking": ("Booking.com", "hotels"),
            "com.airbnb.android": ("Airbnb", "hotels"), "com.getyourguide.android": ("GetYourGuide", "tourism"),
            "com.klook": ("Klook", "tourism"), "com.tiqets.tiqetsapp": ("Tiqets", "tourism"), "com.viator.mobile.android": ("Viator", "tourism"),
            "com.flightradar24free": ("Flightradar24", "flights"), "com.tripit": ("TripIt", "flights"), "com.skypicker.main": ("Kiwi.com", "flights"),
            "com.revolut.revolut": ("Revolut", "payment"), "com.lufthansa.android.lufthansa": ("Lufthansa", "flights"),
            "com.plannet.milesandmoreapp": ("Miles & More", "flights"), "com.prioritypass3": ("Priority Pass", "flights"),
            "com.staralliance.navigator": ("Star Alliance", "flights"), "com.limebike": ("Lime", "micro"), "io.voiapp.voi": ("Voi", "micro"),
            "com.wolt.android": ("Wolt", "delivery"), "com.ubercab.eats": ("Uber Eats", "delivery"), "de.flixbus.app": ("FlixBus", "rail"),
            "com.goeuro.rosie": ("Omio", "rail"), "net.easypark.android": ("EasyPark", "parking")}

def build():
    out = {"schema": 1, "version": VERSION, "categories": [{"id": a, "name": b, "icon": i} for a, b, i in CATS], "countries": []}
    ww = {"code": "WW", "name": "Weltweit", "flag": "🌍", "apps": [], "cities": []}
    for p in WW_PKGS:
        n, cat = WW_NAMES[p]
        ww["apps"].append(entry(n, p, cat, mine=True))
    out["countries"].append(ww)

    for code, name, flag, flist in COUNTRIES:
        country = {"code": code, "name": name, "flag": flag, "apps": [], "cities": []}
        cities = {}
        def add_city(cname, app):
            if cname not in cities:
                cities[cname] = {"name": cname, "match": CITY_MATCH.get(cname, [cname]), "apps": []}
            if all(a.get("pkg", a["name"]) != app.get("pkg", app["name"]) for a in cities[cname]["apps"]):
                cities[cname]["apps"].append(app)
        seen = set()
        for fname in flist:
            for (title, pkg, itype) in folders.get(fname, []):
                web = is_web(pkg)
                if web:
                    continue  # Web-Verknüpfungen ohne URL lassen sich nicht sinnvoll übernehmen
                key = pkg
                if key in seen: continue
                seen.add(key)
                label = NOTE.get(pkg, "")
                disp = "Île-de-France Mobilités" if pkg == "com.applidium.vianavigo" else title
                app = entry(disp, pkg, note="" if disp != title or pkg == "com.applidium.vianavigo" else label, mine=True)
                if pkg == "com.applidium.vianavigo": app["note"] = "Navigo, Tickets für Paris"
                where = CITY_OF.get(pkg)
                if where and where[0] == code:
                    add_city(where[1], app)
                else:
                    country["apps"].append(app)
        for app in R.get(code, []):
            k = app.get("pkg", app["name"])
            if any(a.get("pkg", a["name"]) == k for a in country["apps"]): continue
            country["apps"].append(app)
        for (cc, cname), apps in R_CITY.items():
            if cc == code:
                for a in apps: add_city(cname, a)
        # Stadt-Apps nicht doppelt auf Landesebene
        city_keys = {a.get("pkg", a["name"]) for ci in cities.values() for a in ci["apps"]}
        country["apps"] = [a for a in country["apps"] if a.get("pkg", a["name"]) not in city_keys]
        country["cities"] = sorted(cities.values(), key=lambda x: x["name"])
        if code in ("EE", "LV", "LT"):
            for a in country["apps"]:
                if a.get("mine"): a["note"] = (a.get("note", "") + " (aus deinem Baltikum-Ordner)").strip()
        out["countries"].append(country)

    for code, name, flag in AFRICA:
        apps = []
        for (title, pkg, itype) in folders.get("Afrika", []):
            if is_web(pkg): continue
            apps.append(entry(title, pkg, note="aus deinem Afrika-Ordner, Verfügbarkeit im Land prüfen", mine=True))
        out["countries"].append({"code": code, "name": name, "flag": flag, "apps": apps, "cities": []})
    return out

if __name__ == "__main__":
    d = build()
    json.dump(d, open("data.json", "w"), ensure_ascii=False, indent=1)
    n_apps = sum(len(c["apps"]) + sum(len(ci["apps"]) for ci in c["cities"]) for c in d["countries"])
    n_cities = sum(len(c["cities"]) for c in d["countries"])
    print(len(d["countries"]), "Länder,", n_cities, "Städte,", n_apps, "Einträge")
    miss = sorted({a["cat"] for c in d["countries"] for a in c["apps"] if a["cat"] == "misc" and a.get("mine")})
    print("misc (mine):", [(c["code"], a["name"], a.get("pkg")) for c in d["countries"] for a in c["apps"] if a["cat"] == "misc" and a.get("mine")])
