"""Skripte, Suchindex, Sitemap, llms.txt und die Zählkarte."""
import datetime, io, json, math, os, re, shutil
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *
from gtk.components import *

def copy_static():
    """Kopiert static/ (CSS, JS, Schriften, Fotos, Icons, Downloads) in den Ausgabeordner."""
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

def meta_files():
    idx = []
    for s in S:
        looks = " ".join(NAMES[p[2] if p[1] == s["key"] else p[1]] for p in PAIRS if s["key"] in (p[1], p[2]))
        idx.append([s["name"], s["key"], f'{s["name"]} {s["latin"]} {s["alias"]}', looks, f'{s["grp"]} {GROUP_FORMS[s["grp"]]} {ROLE[s["role"]]}|{s["short"]}|{act_text(s)}'])
    write("search.json", json.dumps(idx, ensure_ascii=False))
    urls = ["", "arten/", "ausruestung/", "bildnachweis/", "datenschutz/", "impressum/", "schadbilder/", "unterscheiden/", "gartenjahr/", "merkmale/", "groessen/", "ratgeber/schnecken/", "ratgeber/nuetzlinge/", "geschenke/", "ueber/", "links/", "insektensommer/"]
    urls += [f"merkmale/{m[0]}/" for m in MERKMALE]
    urls += [f"arten/{s['key']}/" for s in S] + [f"unterscheiden/{p[0]}/" for p in PAIRS] + [f"gartenjahr/{m}/" for m in MS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    write("site.webmanifest", json.dumps({"name": SITE, "short_name": SITE, "lang": "de", "start_url": "/", "display": "standalone", "background_color": "#faf7f1", "theme_color": "#4a6a4c",
           "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=1))
    write("version.txt", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))


def page_llms():
    L = [f"# {SITE}", "", f"> Tiere im Garten erkennen: {len(S)} typische Gartentiere mit Foto, Merkmalen, Rolle im Garten (Nützling, Bestäuber, Schädling) und Vorkommen im Jahresverlauf, {len(PAIRS)} Vergleiche ähnlicher Arten, Schadbilder und Ratgeber für naturnahes Gärtnern ohne Gift. Privates, unabhängiges Angebot von Nico Schober aus Bremen. Fotos von Wikimedia Commons, Steckbriefe abgeglichen mit Bestimmungsliteratur und Wikipedia.", "",
         "Sprache: Deutsch. Angaben zu Vorkommen sind grobe Richtwerte für Deutschland.", "", "## Bestimmen",
         f"- [Alle Arten von A bis Z]({BASE}arten/): Steckbriefe mit Foto und Merkmalen",
         f"- [Nach Farbe und Merkmal]({BASE}merkmale/): z. B. roter Käfer, grüne Raupe, Schnecke",
         f"- [Was frisst an meiner Pflanze?]({BASE}schadbilder/): vom Schadbild zum Verursacher",
         f"- [Ähnliche Tiere unterscheiden]({BASE}unterscheiden/): Doppelgänger im direkten Vergleich",
         f"- [Nach Größe]({BASE}groessen/)", f"- [Gartenjahr]({BASE}gartenjahr/): welche Tiere in welchem Monat aktiv sind", "",
         "## Im Garten",
         f"- [Nützlinge fördern]({BASE}ratgeber/nuetzlinge/)", f"- [Schnecken ohne Gift loswerden]({BASE}ratgeber/schnecken/)",
         f"- [Insektensommer: Insekten zählen]({BASE}insektensommer/)", f"- [Ausrüstung]({BASE}ausruestung/)", f"- [Geschenke für Gartenfreunde]({BASE}geschenke/)", "",
         "## Merkmale"] + [f"- [{t}]({BASE}merkmale/{s}/)" for s, t, *_ in MERKMALE] + ["", "## Arten"] + \
        [f"- [{s['name']}]({BASE}arten/{s['key']}/): {s['short']}" for s in sorted(S, key=lambda x: x["name"])] + ["", "## Vergleiche"] + \
        [f"- [{NAMES[p[1]]} oder {NAMES[p[2]]}?]({BASE}unterscheiden/{p[0]}/)" for p in PAIRS] + ["", "## Über die Seite",
         f"- [Über den {SITE}]({BASE}ueber/)", f"- [Bildnachweis]({BASE}bildnachweis/)", f"- [Impressum]({BASE}impressum/)", ""]
    write("llms.txt", "\n".join(L))

def zaehlkarte_html():
    sp = [SP[k] for k in IS_KEYS]
    import base64
    from PIL import Image
    def thumb(k):
        im = Image.open(os.path.join(OUT, "photos", f"{k}-400.webp")).convert("RGB"); im.thumbnail((200, 160)); buf = io.BytesIO(); im.save(buf, "JPEG", quality=72)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    rows = "".join(f'<tr><td class="ph"><img src="{thumb(s["key"])}" alt=""></td><td><b>{e(s["name"])}</b><br><span>{e(s["marks"][0])}</span></td><td class="box"></td></tr>' for s in sp)
    css = open(os.path.join(OUT, "assets", "site.css"), encoding="utf-8").read()
    faces = "".join(re.findall(r"@font-face\{[^}]*\}", css)).replace("../fonts/", "fonts/")
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>Zählkarte Insektensommer – {SITE}</title><style>{faces}
@page{{size:A4;margin:12mm 14mm}}body{{font-family:Mulish,sans-serif;color:#1d2b20;font-size:9.4pt;margin:0}}
h1{{font-family:Lora,serif;font-weight:600;color:#7a3b22;font-size:19pt;margin:0}}.sub{{margin:2mm 0 3mm;color:#4a5a4d}}
.meta{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:3mm;margin:0 0 3mm}}.meta div{{border-bottom:.6pt solid #8a9a8d;padding-top:5mm;font-size:8pt;color:#4a5a4d}}
table{{width:100%;border-collapse:collapse}}td{{border-bottom:.5pt solid #d5dccd;padding:.75mm 2mm;vertical-align:middle}}td span{{color:#4a5a4d;font-size:8.3pt}}
.ph{{width:17mm;padding-left:0}}.ph img{{width:16mm;height:12mm;object-fit:cover;border-radius:1.5mm;display:block}}.box{{width:24mm}}.box::after{{content:"";display:block;height:7mm;border:.8pt solid #4a6a4c;border-radius:1.5mm}}
.extra td{{height:9mm}}.foot{{margin-top:3mm;font-size:7.6pt;color:#4a5a4d;line-height:1.45}}</style></head><body>
<h1>Zählkarte Insektensommer</h1><p class="sub">Eine Stunde lang zählen, im Umkreis von etwa zehn Metern. Pro Art die höchste Zahl eintragen, die du gleichzeitig siehst. Melden auf insektensommer.de</p>
<div class="meta"><div>Datum</div><div>Uhrzeit von – bis</div><div>Ort</div><div>Wetter</div></div>
<table>{rows}<tr class="extra"><td></td><td><b>Weitere Art:</b></td><td class="box"></td></tr><tr class="extra"><td></td><td><b>Weitere Art:</b></td><td class="box"></td></tr></table>
<p class="foot">Gartentierkompass · gartentierkompass.de/insektensommer · Keine offizielle Zählhilfe des NABU. Den Insektensommer veranstalten NABU und LBV.<br>Fotos: Wikimedia Commons, Urheber und Lizenzen unter gartentierkompass.de/bildnachweis</p></body></html>"""
