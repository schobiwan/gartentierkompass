"""Kleine Helfer: Escaping, Dateien schreiben, Cache-Busting, Aufzählungen."""

import hashlib, html, os
from urllib.parse import quote_plus
from gtk.config import ART, OUT, TAG

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


ADJ_START = ("Asiatischer", "Großer", "Kleiner", "Gemeiner", "Gefurchter", "Goldglänzender", "Dunkle", "Spanische", "Rote", "Schwarze", "Weiße", "Gemeine", "Blauschwarze", "Grünes")

def decline(name, case, pron):
    """Artname mit Artikel im Fall: decline("Großer Kohlweißling", "akk", "ihn") -> "den Großen Kohlweißling"."""
    art = dict(zip(("nom", "akk", "dat"), ART[pron]))[case]
    first, _, rest = name.partition(" ")
    if rest and first in ADJ_START:
        if pron == "ihn" and first.endswith("er"):          # der Große, den/dem Großen
            first = first[:-1] if case == "nom" else first[:-2] + "en"
        elif pron == "sie" and case == "dat" and first.endswith("e"):
            first += "n"
        elif pron == "es" and first.endswith("es"):           # das Grüne, dem Grünen
            first = first[:-1] if case != "dat" else first[:-2] + "en"
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

def fit_desc(text, limit=158):
    """Meta-Description ohne Abbruch mitten im Satz: ganze Sätze, solange sie passen."""
    import re as _re
    out = ""
    for sent in _re.split(r"(?<=[.!?])\s+", text.strip()):
        if len(out) + len(sent) + (1 if out else 0) > limit: break
        out = f"{out} {sent}".strip()
    return out or text[:limit].rsplit(" ", 1)[0]

def fit_title(*opts, limit=60):
    """Erster Titelvorschlag, der passt; Seitenname wird angehängt, wenn Platz ist."""
    from gtk.config import SITE
    t = next((x for x in opts if len(x) <= limit), opts[-1])
    return t + f" · {SITE}" if len(t) + len(SITE) + 3 <= limit else t
