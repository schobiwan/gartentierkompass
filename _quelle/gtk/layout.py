"""Seitengerüst: <head>, Navigation, Brotkrumen, Footer."""
import json
from gtk.config import *
from gtk.util import *
from gtk.logo import LOGO_SYMBOL

ICON_DEFS = ('<symbol id="i-sun" viewBox="0 0 16 16"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4"/></symbol>'
             '<symbol id="i-dusk" viewBox="0 0 16 16"><path d="M2 11.5h12M4 11.5a4 4 0 0 1 8 0M8 3.5v2M3.2 6.2l1.3 1.1M12.8 6.2l-1.3 1.1"/></symbol>'
             '<symbol id="i-moon" viewBox="0 0 16 16"><path d="M10.5 2.5a5.5 5.5 0 1 0 3 9.6A6 6 0 0 1 10.5 2.5z" fill="currentColor" stroke="none"/></symbol>')

SEARCH_ICO = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>'

ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"></path></svg>'

NEWWIN = '<span class="sr-only"> (öffnet in neuem Fenster)</span>'

def head(R, title, desc, path, og_type="website", og_img="photos/og.jpg", og_alt="Gartentierkompass", extra="", ld=None):
    css = ver("assets/site.css")
    if len(title) > 60 and title.endswith(f" · {SITE}"): title = title[: -len(f" · {SITE}")]
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return (f'<!DOCTYPE html><html lang="de" data-root="{R or "./"}"> <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}"><meta name="robots" content="max-image-preview:large">'
            '<meta name="theme-color" content="#f2f7e8" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#14231a" media="(prefers-color-scheme: dark)"><meta name="color-scheme" content="light dark">'
            f'<link rel="icon" href="{R}favicon.ico" sizes="48x48"><link rel="icon" href="{R}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{R}apple-touch-icon.png"><link rel="manifest" href="{R}site.webmanifest">'
            f'<link rel="preload" href="{R}fonts/lora-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="{R}fonts/mulish-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>'
            f'<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{SITE}"><meta property="og:locale" content="de_DE"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
            f'<meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}{og_img}"><meta property="og:image:alt" content="{e(og_alt)}"><meta name="twitter:card" content="summary_large_image">'
            f'{lds}{extra}<link rel="stylesheet" href="{R}assets/site.css?v={css}"></head> <body> <svg class="logo-defs" aria-hidden="true" focusable="false">{LOGO_SYMBOL}{ICON_DEFS}</svg> <a class="skip" href="#main">Zum Inhalt springen</a> ')

CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m7 10 5 5 5-5"/></svg>'

def nav(R, cur):
    def ac(k): return ' aria-current="true"' if cur == k else ""
    best = [("index.html#arten", "Nach Name oder Aussehen", "Suchen und filtern, z. B. „rote Punkte“"),
            ("merkmale/index.html", "Nach Farbe und Merkmal", "Roter Käfer, grüne Raupe, Schnecke …"),
            ("schadbilder/index.html", "Nach Fraßspuren", "Löcher, Gespinste, Hügel im Rasen"),
            ("unterscheiden/index.html", "Ähnliche Tiere unterscheiden", f"{len(PAIRS)} Doppelgänger im Vergleich"),
            ("groessen/index.html", "Nach Größe", "Von der Blattlaus bis zum Steinmarder"),
            ("arten/index.html", "Alle Arten von A bis Z", f"{len(S)} Steckbriefe mit Foto und Merkmalen")]
    garten = [("ratgeber/nuetzlinge/index.html", RATGEBER["nuetzlinge"]["nav"], RATGEBER["nuetzlinge"]["navsub"]),
              ("ratgeber/schnecken/index.html", RATGEBER["schnecken"]["nav"], RATGEBER["schnecken"]["navsub"]),
              ("schadbilder/index.html", "Was frisst an meiner Pflanze?", "Vom Schadbild zum Verursacher"),
              ("insektensommer/index.html", "Insektensommer", "Insekten zählen im Juni und August"),
              ("ausruestung/index.html#lebensraum", "Nisthilfen und Igelhaus", "Unterschlupf für Helfer"),
              ("ausruestung/index.html", "Lupe, Bücher und Schutz", "Alle Ausrüstungstipps"),
              ("geschenke/index.html", "Geschenke für Gartenfreunde", "Ideen für jeden Anlass")]
    li = lambda items: "".join(f'<li><a href="{R}{h}"><b>{e(t)}</b><span>{e(s)}</span></a></li>' for h, t, s in items)
    return (f'<nav class="appnav" aria-label="Hauptnavigation"> <div class="wrap"> <a class="brand" href="{R}index.html"><svg class="logo" aria-hidden="true"><use href="#logo-mark"></use></svg><span>{SITE}</span><span class="sr-only">, zur Startseite</span></a> <ul class="tabs" id="tabs"> '
            f'<li class="has-menu"><a class="tab" href="{R}index.html" data-menu="bestimmen"{ac("bestimmen")}>{SEARCH_ICO}<span>Bestim&shy;men</span>{CHEV}</a><div class="mpanel" id="menu-bestimmen" hidden><p class="mintro">Wer ist das?</p><ul>{li(best)}</ul></div></li>'
            f'<li class="has-menu"><a class="tab" href="{R}ratgeber/nuetzlinge/index.html" data-menu="garten"{ac("garten")}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V11"/><path d="M12 11c0-3 2.5-5.5 6-5.5 0 3.5-2.5 5.5-6 5.5z"/><path d="M12 14c0-2.6-2-4.5-5-4.5 0 3 2 4.5 5 4.5z"/></svg><span>Im Garten</span>{CHEV}</a><div class="mpanel" id="menu-garten" hidden><p class="mintro">Helfer fördern, Pflanzen schützen</p><ul>{li(garten)}</ul></div></li>'
            f'<li><a class="tab" href="{R}gartenjahr/index.html"{ac("jahr")}><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg><span>Garten&shy;jahr</span></a></li>'
            f'<li><a class="tab" href="{R}ausruestung/index.html"{ac("gear")}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V6"/><rect x="5" y="6" width="14" height="15" rx="4"/><path d="M9 13h6M9 13v3h6v-3"/></svg><span>Aus&shy;rüstung</span></a></li> </ul> '
            f'<button class="navsearch" type="button" id="navsearch" aria-haspopup="dialog" aria-controls="sdlg">{SEARCH_ICO}<span class="sr-only">Tier suchen</span><span class="nsl" aria-hidden="true">Suchen</span></button> </div> <div class="mbackdrop" id="mbackdrop" hidden></div> </nav> '
            f'<dialog class="sdlg" id="sdlg" aria-labelledby="sdlg-title"> <form method="get" action="{R}index.html" class="sform" id="sform"><h2 class="sr-only" id="sdlg-title">Tier suchen</h2><label class="search" for="sq">{SEARCH_ICO}<span class="sr-only">Name oder Merkmal</span><input type="search" id="sq" name="q" placeholder="Name oder Merkmal, z. B. rote Punkte" autocomplete="off" enterkeyhint="search"></label><button type="button" class="sclose" id="sclose">Schließen</button></form> <p class="sr-only" id="sstatus" role="status" aria-live="polite"></p><ul class="sresults" id="sresults" aria-label="Treffer"></ul><p class="smore" id="smore" hidden><a id="smore-link" href="{R}index.html#arten">Alle Treffer mit Filtern anzeigen</a></p> </dialog> ')

def crumbs(R, trail):
    lis, ld = [f'<li><a href="{R}index.html">Start</a></li>'], [{"@type": "ListItem", "position": 1, "name": "Start", "item": BASE}]
    for i, (name, path) in enumerate(trail):
        last = i == len(trail) - 1
        lis.append(f'<li><span aria-current="page">{e(name)}</span></li>' if last else f'<li><a href="{R}{path}index.html">{e(name)}</a></li>')
        ld.append({"@type": "ListItem", "position": i + 2, "name": name, "item": BASE + path})
    return (f'<nav class="crumbs wrap" aria-label="Brotkrumen"><ol> {" ".join(lis)} </ol></nav>'
            f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld}, ensure_ascii=False)}</script> ')

def footer(R, script="app.js"):
    col = lambda title, items: f'<nav aria-label="{e(title)}"><p class="fhead">{e(title)}</p><ul>' + "".join(
        f'<li><a href="{h if h.startswith("http") else R + h}"{" rel=\"noopener\"" if h.startswith("http") else ""}>{e(t)}</a></li>' for h, t in items) + '</ul></nav>'
    c1 = [("index.html#arten", "Nach Name oder Aussehen"), ("merkmale/index.html", "Nach Farbe und Merkmal"), ("schadbilder/index.html", "Nach Fraßspuren"),
          ("unterscheiden/index.html", "Ähnliche Tiere unterscheiden"), ("groessen/index.html", "Nach Größe"), ("arten/index.html", "Alle Arten von A bis Z")]
    c2 = [("ratgeber/nuetzlinge/index.html", "Nützlinge fördern"), ("ratgeber/schnecken/index.html", "Schnecken ohne Gift"), ("insektensommer/index.html", "Insektensommer: Insekten zählen"), ("schadbilder/index.html", "Was frisst an meiner Pflanze?"),
          ("ausruestung/index.html", "Ausrüstung"), ("geschenke/index.html", "Geschenke für Gartenfreunde")]
    c3 = [("gartenjahr/index.html", "Gartenjahr und Kalender"), ("links/index.html", "Weiterführende Websites")] + [(u, t) for u, t in SISTERS]
    c4 = [("ueber/index.html", f"Über den {SITE}"), ("impressum/index.html", "Impressum"), ("datenschutz/index.html", "Datenschutz"), ("bildnachweis/index.html", "Bildnachweis und Lizenzen")]
    return (f'<footer> <div class="wrap"> <a class="flogo" href="{R}index.html"><svg class="logo" aria-hidden="true"><use href="#logo-mark"></use></svg><span>{SITE}</span></a> <div class="fcols"> '
            f'{col("Bestimmen", c1)} {col("Im Garten", c2)} {col("Mehr entdecken", c3)} {col("Rechtliches", c4)} </div> '
            f'<p class="footnote">Fotos: Wikimedia Commons, unter freien Lizenzen. Mit * markierte Links sind Werbelinks. Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.</p> </div> </footer> '
            f'<script type="module" src="{R}assets/{script}?v={ver("assets/" + script)}"></script> </body> </html>')

ADNOTE = f'<p class="adnote"><span aria-hidden="true">*</span> Werbelink: Wenn du über diesen Link etwas kaufst, erhält der {SITE} eine kleine Provision von Amazon. Für dich ändert sich am Preis nichts. Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.</p>'

ADBANNER = '<p class="adbanner"><b>Werbung:</b> Diese Seite enthält Werbelinks zu Amazon, gekennzeichnet mit einem Sternchen. Kaufst du darüber, erhalte ich eine kleine Provision, für dich ändert sich am Preis nichts.</p>'
