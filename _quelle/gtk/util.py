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


def join_de(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " und " + xs[-1]

def amazon(q):
    return f"https://www.amazon.de/s?k={quote_plus(q)}&tag={TAG}"
