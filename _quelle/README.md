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
| `css/site.css` | Lesbare Stylesheet-Quelle. Nach Änderungen `npm --prefix tools/css run build` (minifiziert nach `static/assets/site.css`) |
| `static/` | Unveränderte Dateien: minifiziertes CSS, JavaScript, Schriften, Fotos, Icons, PDF |
| `tools/` | `check.py` (Links, JSON-LD, Titel), `zaehlkarte.py` (PDF), `shot.py` (Screenshots), `assets.py` (Icons/OG-Bild) |

## Bauen

```bash
cd _quelle
python3 build.py                 # -> _quelle/out
GTK_OUT=.. python3 build.py      # direkt in den Hauptordner (Website) schreiben
python3 -m tools.check           # prüft den Ausgabeordner
```

Nach inhaltlichen Änderungen `STAND_ISO` und `STAND_DE` in `gtk/config.py` anpassen.
Gestaltung ändern: `css/site.css` bearbeiten, dann `npm --prefix tools/css run build` und `build.py`. Die Seiten hängen automatisch einen neuen `?v=`-Hash an.
Ungenutzte Regeln finden: `npm --prefix tools/css run unused` schreibt eine bereinigte Fassung nach `css/site.purged.css` zum Vergleichen.

`tools/assets.py` nicht komplett ausführen: `main()` überschreibt die echten Fotos mit Platzhaltern.

## Redaktionsregeln

`python3 -m tools.check` prüft die Regeln, die sich automatisch prüfen lassen.

**Überschriften**
- Jede Seite hat genau eine `h1`; Ebenen werden nicht übersprungen (h1 → h2 → h3).
- Satzschreibung, kein Punkt am Ende. Fragen nur, wenn die Seite die Frage beantwortet („Was frisst der Igel?“, „Maulwurf oder Schermaus?“).
- Artseiten nennen die Art immer mit vollem Namen und richtig gebeugt: „So erkennst du den Großen Kohlweißling“, „Wann ist der Große Kohlweißling zu sehen?“, „Was frisst der Große Kohlweißling?“, „So hilfst du der Dunklen Erdhummel“. Dafür sorgt `decline()` in `gtk/util.py`; neue Artnamen mit Adjektiv vorn in `ADJ_START` eintragen.
- Merkmalseiten: „{Merkmal} im Garten“ (Ausnahmen, wo es nicht passt: „Winzige Insekten an Pflanzen“, „Tiere am Gartenteich“).
- Seitentitel (`<title>`) höchstens 60 Zeichen; der Zusatz „· Gartentierkompass“ entfällt, wenn es sonst länger wird.

**Links**
- Interne Links: im selben Fenster, Linktext sagt, wohin es geht („Alle Merkmale ansehen“, „Maulwurf oder Schermaus? Alle Unterschiede“), nie „hier“.
- Sammel-Links enden einheitlich auf „… ansehen“ („Alle Ausrüstungstipps ansehen“).
- Fremde Seiten (Wikipedia, NABU, Wikimedia …): neues Fenster, `rel="noopener"`, Screenreader-Hinweis „(öffnet in neuem Fenster)“ – am einfachsten mit `ext_link()`.
- Schwesterseiten (Vogel-, Waldtier-, Meereskompass): im selben Fenster, ohne Hinweis.
- Amazon-Partnerlinks: immer „Bei Amazon ansehen*“, neues Fenster, `rel="sponsored nofollow noopener"`, Werbehinweis auf der Seite.
- Fotonachweise: Urheber verlinkt auf die Commons-Seite, Lizenzkürzel auf den Lizenztext (beides neues Fenster mit Hinweis).
