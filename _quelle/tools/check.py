"""Prüft den gebauten Ausgabeordner: interne Links, JSON-LD, doppelte Titel, Titellänge,
Überschriften- und Link-Regeln (siehe README, Abschnitt „Redaktionsregeln“).

Aufruf aus src/:  python3 -m tools.check
"""
import glob, json, os, re, sys
from gtk.config import OUT
from gtk.util import FAMILY


def policy(rel, h):
    """Überschriften: genau eine h1, keine übersprungene Ebene. Links: extern -> neues Fenster mit Hinweis,
    Schwesterseiten im selben Fenster, Amazon-Partnerlinks mit rel=sponsored nofollow."""
    out = []
    levels = [int(x) for x in re.findall(r"<h([1-6])[\s>]", h)]
    if levels.count(1) != 1:
        out.append(f"{rel}: {levels.count(1)} h1-Überschriften")
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            out.append(f"{rel}: Überschrift springt von h{a} auf h{b}")
    for attrs, inner in re.findall(r"<a\s([^>]*)>(.*?)</a>", h, re.S):
        href = (re.search(r'href="([^"]*)"', attrs) or [None, ""])[1]
        if not href.startswith("http"):
            continue
        dom = re.sub(r"^https?://(www\.)?", "", href).split("/")[0]
        partner = "amazon." in dom and "tag=" in href
        if partner and not ("sponsored" in attrs and "nofollow" in attrs):
            out.append(f"{rel}: Partnerlink ohne rel=sponsored nofollow -> {href[:60]}")
        if dom in FAMILY:
            if 'target="_blank"' in attrs:
                out.append(f"{rel}: Schwesterseite öffnet neues Fenster -> {dom}")
        elif 'target="_blank"' not in attrs:
            out.append(f"{rel}: externer Link ohne neues Fenster -> {dom}")
        elif "neuem Fenster" not in inner and "neuem Fenster" not in attrs:
            out.append(f"{rel}: neues Fenster ohne Hinweis -> {dom}")
    return out


def main():
    bad, titles, errors = set(), {}, []
    for f in glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        h = open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, OUT)
        for u in re.findall(r'(?:href|src)="([^"#?]+)', h):
            if not u.startswith(("http", "mailto", "data:")) and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), u))):
                bad.add((rel, u))
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(m)
            except ValueError as ex:
                errors.append(f"{rel}: JSON-LD {ex}")
        errors += policy(rel, h)
        t = re.search(r"<title>(.*?)</title>", h)
        if t:
            titles.setdefault(t.group(1), []).append(rel)
    for rel, u in sorted(bad):
        errors.append(f"{rel}: Link ins Leere -> {u}")
    errors += [f"Titel doppelt: {t} ({', '.join(v)})" for t, v in titles.items() if len(v) > 1]
    long = [t for t in titles if len(t) > 70]
    print(f"{len(titles)} Seiten geprüft, {len(errors)} Fehler, {len(long)} Titel über 70 Zeichen")
    for x in errors:
        print(" -", x)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
