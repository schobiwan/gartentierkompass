# Generator für gartentierkompass.de

Python-Skripte, die die statische Website im Hauptordner erzeugen.

## Aufbau

| Ordner / Datei | Inhalt |
| --- | --- |
| `build.py` | Einstieg: kopiert `static/` und schreibt alle Seiten nach `out/` (oder `GTK_OUT`) |
| `data/` | Inhalte: Arten (`species.py`), Vergleiche, Schadbilder, Produkte (`more.py`), Merkmale, Ratgeber, Geschenke, Links (`vk.py`), Fotonachweise (`photos.json`, `pphotos.json`) |
| `gtk/config.py` | Konstanten (Domain, Partner-ID, Stand-Datum) und abgeleitete Tabellen |
| `gtk/util.py`, `gtk/layout.py`, `gtk/components.py` | Helfer, Seitengerüst (Kopf, Navigation, Footer), Bausteine (Bilder, Karten, Produkte) |
| `gtk/pages_*.py` | Seiten nach Bereich: Arten, Startseite, Bestimmen, Im Garten, Info |
| `gtk/meta.py` | Suchindex, Sitemap, robots.txt, Manifest, llms.txt, Zählkarte |
| `static/` | Unveränderte Dateien: CSS, JavaScript, Schriften, Fotos, Icons, PDF |
| `tools/` | `check.py` (Links, JSON-LD, Titel), `zaehlkarte.py` (PDF), `shot.py` (Screenshots), `assets.py` (Icons/OG-Bild) |

## Bauen

```bash
cd _quelle
python3 build.py                 # -> _quelle/out
GTK_OUT=.. python3 build.py      # direkt in den Hauptordner (Website) schreiben
python3 -m tools.check           # prüft den Ausgabeordner
```

Nach inhaltlichen Änderungen `STAND_ISO` und `STAND_DE` in `gtk/config.py` anpassen.
Gestaltung ändern: `static/assets/site.css`. Die Seiten hängen automatisch einen neuen `?v=`-Hash an.

`tools/assets.py` nicht komplett ausführen: `main()` überschreibt die echten Fotos mit Platzhaltern.
