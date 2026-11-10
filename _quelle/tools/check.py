"""Prüft den gebauten Ausgabeordner: interne Links, JSON-LD, doppelte Titel, Titellänge.

Aufruf aus src/:  python3 -m tools.check
"""
import glob, json, os, re, sys
from gtk.config import OUT


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
