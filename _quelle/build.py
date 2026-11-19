#!/usr/bin/env python3
"""Baut gartentierkompass.de als statische Website.

Aufruf aus diesem Ordner:  python3 build.py            -> schreibt nach ./out
                            GTK_OUT=/pfad python3 build.py
                            python3 build.py --preview  -> Links behalten index.html (für die Vorschau im Chat,
                                                           die keine Ordner-Adressen kennt)
Danach optional:           python3 -m tools.zaehlkarte  (PDF neu erzeugen, braucht Chrome + Playwright)
                            python3 -m tools.check      (Links und strukturierte Daten prüfen)
"""
import os, re, sys
from gtk.config import S, OUT
from gtk.meta import copy_static, meta_files, page_llms
from gtk.pages_species import page_species
from gtk.pages_home import page_home, page_arten
from gtk.pages_bestimmen import page_pairs, page_damage, page_merkmale, page_sizes
from gtk.pages_garten import page_year, page_gear, page_ratgeber, page_gifts, page_insektensommer
from gtk.pages_info import legal_pages, page_about, page_links


PREVIEW = "--preview" in sys.argv
# Interne Links auf …/index.html (auch mit #Anker) -> kurze Ordner-Adresse …/ ; externe Links bleiben unberührt
CLEAN_LINK = re.compile(r'(href|action)="(?![a-z]+:|#|//)([^"]*?)index\.html(#[^"]*)?"')


def clean_links():
    """Live-Seite: kurze Adressen ohne index.html und data-clean, damit auch die Skripte so verlinken."""
    for d, _, fs in os.walk(OUT):
        if os.path.basename(d) == "_quelle" or "/_quelle" in d:
            continue
        for f in fs:
            if f.endswith(".html"):
                fp = os.path.join(d, f)
                t = open(fp, encoding="utf-8").read()
                t = CLEAN_LINK.sub(lambda m: f'{m.group(1)}="{m.group(2) or "./"}{m.group(3) or ""}"', t)
                t = t.replace('<html lang="de" data-root=', '<html lang="de" data-clean data-root=', 1)
                open(fp, "w", encoding="utf-8").write(t)


def main():
    copy_static()               # zuerst: Cache-Hashes (?v=) lesen site.css und app.js aus dem Ausgabeordner
    for s in S:
        page_species(s)
    page_home(); page_arten()
    page_pairs(); page_damage(); page_merkmale(); page_sizes()
    page_year(); page_gear(); page_ratgeber(); page_gifts(); page_insektensommer()
    legal_pages(); page_about(); page_links()
    page_llms(); meta_files()
    if not PREVIEW:
        clean_links()
    print("fertig")


if __name__ == "__main__":
    main()
