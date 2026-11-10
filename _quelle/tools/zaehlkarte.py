"""Erzeugt static/downloads/zaehlkarte-insektensommer.pdf (A4) aus gtk.meta.zaehlkarte_html().

Aufruf aus src/ nach einem Build:  python3 -m tools.zaehlkarte
Braucht Playwright und Google Chrome. Danach build.py erneut laufen lassen, damit das PDF in out/ landet.
"""
import os
from playwright.sync_api import sync_playwright
from gtk.config import OUT, STATIC
from gtk.meta import zaehlkarte_html

CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")


def main():
    tmp = os.path.join(OUT, "_zaehlkarte.html")       # im Ausgabeordner, damit fonts/ relativ gefunden wird
    open(tmp, "w", encoding="utf-8").write(zaehlkarte_html())
    dst = os.path.join(STATIC, "downloads", "zaehlkarte-insektensommer.pdf")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            pg = b.new_page()
            pg.goto("file://" + os.path.abspath(tmp))
            pg.wait_for_timeout(800)
            pg.pdf(path=dst, format="A4", print_background=True, prefer_css_page_size=True)
            b.close()
    finally:
        os.remove(tmp)
    print("PDF:", dst)


if __name__ == "__main__":
    main()
