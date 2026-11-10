"""Kleine Helfer: Escaping, Dateien schreiben, Cache-Busting, Aufzählungen."""
import hashlib, html, os
from urllib.parse import quote_plus
from gtk.config import *

def e(t):
    """HTML-Escaping für Text und Attribute."""
    return html.escape(str(t), quote=True)

def write(path, content):
    """Schreibt eine Datei relativ zum Ausgabeordner."""
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def ver(path):
    """Kurzer Inhalts-Hash für Cache-Busting (?v=…)."""
    return hashlib.md5(open(os.path.join(OUT, path), "rb").read()).hexdigest()[:8]


ADJ_START = ("Asiatischer", "Großer", "Kleiner", "Gemeiner", "Gefurchter", "Dunkle", "Spanische", "Rote", "Schwarze", "Weiße")

def decline(name, case, pron):
    """Artname mit Artikel im Fall: decline("Großer Kohlweißling", "akk", "ihn") -> "den Großen Kohlweißling"."""
    art = dict(zip(("nom", "akk", "dat"), ART[pron]))[case]
    first, _, rest = name.partition(" ")
    if rest and first in ADJ_START:
        if pron == "ihn" and first.endswith("er"):          # der Große, den/dem Großen
            first = first[:-1] if case == "nom" else first[:-2] + "en"
        elif pron == "sie" and case == "dat" and first.endswith("e"):
            first += "n"
        name = f"{first} {rest}"
    return f"{art} {name}"

FAMILY = ("vogelkompass.de", "waldtierkompass.de", "meereskompass.de", "gartentierkompass.de")

def ext_link(url, text_html, rel="noopener"):
    """Link-Regel: fremde Seiten öffnen ein neues Fenster (mit Hinweis für Screenreader),
    die Schwesterseiten der Kompass-Familie öffnen im selben Fenster."""
    if any(d in url for d in FAMILY):
        return f'<a href="{url}" rel="{rel}">{text_html}</a>'
    return f'<a href="{url}" target="_blank" rel="{rel}">{text_html}<span class="sr-only"> (öffnet in neuem Fenster)</span></a>'

def join_de(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " und " + xs[-1]

def amazon(q):
    return f"https://www.amazon.de/s?k={quote_plus(q)}&tag={TAG}"
