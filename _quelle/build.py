#!/usr/bin/env python3
"""Baut gartentierkompass.de als statische Website.

Aufruf aus diesem Ordner:  python3 build.py            -> schreibt nach ./out
                            GTK_OUT=/pfad python3 build.py
Danach optional:           python3 -m tools.zaehlkarte  (PDF neu erzeugen, braucht Chrome + Playwright)
                            python3 -m tools.check      (Links und strukturierte Daten prüfen)
"""
from gtk.config import S
from gtk.meta import copy_static, meta_files, page_llms
from gtk.pages_species import page_species
from gtk.pages_home import page_home, page_arten
from gtk.pages_bestimmen import page_pairs, page_damage, page_merkmale, page_sizes
from gtk.pages_garten import page_year, page_gear, page_ratgeber, page_gifts, page_insektensommer
from gtk.pages_info import legal_pages, page_about, page_links


def main():
    copy_static()               # zuerst: Cache-Hashes (?v=) lesen site.css und app.js aus dem Ausgabeordner
    for s in S:
        page_species(s)
    page_home(); page_arten()
    page_pairs(); page_damage(); page_merkmale(); page_sizes()
    page_year(); page_gear(); page_ratgeber(); page_gifts(); page_insektensommer()
    legal_pages(); page_about(); page_links()
    page_llms(); meta_files()
    print("fertig")


if __name__ == "__main__":
    main()
