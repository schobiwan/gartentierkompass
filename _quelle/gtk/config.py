"""Konstanten, Daten und abgeleitete Nachschlagetabellen."""
import json, os
from data.species import S, GROUPS, GROUP_FORMS, HABS, ROLE, EXTRA
from data.more import PAIRS, DAMAGE, DAMAGE_STEPS, MONTH_EVENTS, MONTH_PRODS, ICONS, PRODUCTS, GEAR_SECTIONS, HOME_GEAR
from data.vk import MERKMALE, RATGEBER, GESCHENKE, GESCHENKE_OHNE, LINKS

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("GTK_OUT", os.path.join(SRC, "out"))
STATIC = os.path.join(SRC, "static")

# --- Website
SITE = "Gartentierkompass"
BASE = "https://gartentierkompass.de/"
ORG_ID = BASE + "#org"
TAG = "schobiwan-21"          # Amazon-Partner-ID
NOW = 11                      # Monat für die statische Vorbelegung (JS korrigiert live)
STAND_ISO = "2026-11-10"      # Stand der Inhalte (Byline und dateModified)
STAND_DE = "10. November 2026"
SISTERS = [("https://vogelkompass.de/", "Vogelkompass: Vögel bestimmen"), ("https://waldtierkompass.de/", "Waldtierkompass: Tiere im Wald"),
           ("https://meereskompass.de/", "Meereskompass: Tiere an der Küste")]

# --- Sprache und Kalender
MN = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
MS = ["januar", "februar", "maerz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember"]
MA = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
ART = {"ihn": ("der", "den", "dem"), "sie": ("die", "die", "der"), "es": ("das", "das", "dem")}   # Artikel nach Pronomen: Nom., Akk., Dat.
ACT = {"tag": ("tagaktiv", "i-sun"), "daemmerung": ("dämmerungsaktiv", "i-dusk"), "nacht": ("nachtaktiv", "i-moon")}
SIZES = [("s", "winzig (bis 1 cm)"), ("m", "klein (1–5 cm)"), ("l", "mittel (5–20 cm)"), ("xl", "größer als 20 cm")]

# --- Fotos: key -> (Urheber, Lizenz, Lizenz-URL, Commons-Seite)
def _load(name):
    p = os.path.join(SRC, "data", name)
    return {k: tuple(v) for k, v in json.load(open(p, encoding="utf-8")).items()} if os.path.exists(p) else {}
PHOTOS = _load("photos.json")     # Arten und Vergleichsarten
PPHOTOS = _load("pphotos.json")   # Beispielfotos für Produkte

# --- Abgeleitete Tabellen
SP = {s["key"]: s for s in S}
NAMES = {**{s["key"]: s["name"] for s in S}, **{k: v[0] for k, v in EXTRA.items()}}
LATIN = {**{s["key"]: s["latin"] for s in S}, **{k: v[1] for k, v in EXTRA.items()}}
GSLUG = {g: slug for g, slug, _ in GROUPS}
for s in S:
    m = s["mid"]
    s["sz"] = "s" if m <= 1 else "m" if m <= 5 else "l" if m <= 20 else "xl"
    s["acts"] = s["act"].split("|")

# --- Auswahl-Listen
SPOT = ["siebenpunkt-marienkaefer", "tagpfauenauge", "igel", "erdhummel", "eichhoernchen", "zitronenfalter", "taubenschwaenzchen", "rote-mauerbiene",
        "hainschwebfliege", "zauneidechse", "erdkroete", "honigbiene", "gartenkreuzspinne", "teichmolch", "weinbergschnecke", "blindschleiche"]   # Startseite: Reihenfolge für das Titelbild
# Beliebtheit: Reihenfolge für „Jetzt aktiv zuerst“ und die Monatsleiste – Säugetiere und Sympathieträger vorn
POP = ["igel", "eichhoernchen", "siebenpunkt-marienkaefer", "tagpfauenauge", "maulwurf", "erdhummel", "steinmarder", "zauneidechse",
       "erdkroete", "taubenschwaenzchen", "zitronenfalter", "schermaus", "teichmolch", "blindschleiche", "honigbiene", "hainschwebfliege",
       "rote-mauerbiene", "weinbergschnecke", "gartenkreuzspinne", "goldlaufkaefer", "florfliege", "asiatischer-marienkaefer",
       "grosser-kohlweissling", "ohrwurm", "gartenlaubkaefer", "regenwurm", "lilienhaehnchen", "tigerschnegel", "spanische-wegschnecke",
       "kleiner-frostspanner", "apfelwickler", "buchsbaumzuensler", "dickmaulruessler", "schwarze-bohnenlaus", "weisse-fliege"]
POPRANK = {k: i for i, k in enumerate(POP)}

# --- Insektensommer
IS_KEYS = ["erdhummel", "honigbiene", "hainschwebfliege", "tagpfauenauge", "zitronenfalter", "grosser-kohlweissling", "taubenschwaenzchen",
           "siebenpunkt-marienkaefer", "asiatischer-marienkaefer", "florfliege", "goldlaufkaefer", "gartenlaubkaefer", "lilienhaehnchen", "ohrwurm", "schwarze-bohnenlaus"]

IS_TIPS = [("Ein Ort, eine Stunde", "Such dir einen Platz und beobachte bis zu eine Stunde lang alles im Umkreis von etwa zehn Metern, zum Beispiel ein Beet, eine Wiese oder den Balkon."),
           ("Bei gutem Wetter", "Wähle einen sonnigen, warmen und möglichst windstillen Tag. Bei Regen und Kälte verstecken sich die meisten Insekten."),
           ("Höchste Zahl notieren", "Schreib bei jeder Art auf, wie viele Tiere du höchstens gleichzeitig gesehen hast. So zählst du kein Tier doppelt."),
           ("Auch unbekannte Tiere zählen", "Was du nicht sicher bestimmen kannst, notierst du als Gruppe, etwa „Schwebfliege“ oder „Marienkäfer“."),
           ("Online melden", "Deine Zählung meldest du beim NABU über das Formular oder die Web-App auf insektensommer.de.")]
