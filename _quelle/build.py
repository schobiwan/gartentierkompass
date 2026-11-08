# -*- coding: utf-8 -*-
"""Statischer Generator für gartentierkompass.de (Aufbau wie Waldtierkompass)."""
import json, os, re, html, hashlib, datetime
from urllib.parse import quote_plus
from data_species import S, GROUPS, GROUP_FORMS, HABS, ROLE, EXTRA
from data_vk import MERKMALE, RATGEBER, GESCHENKE, GESCHENKE_OHNE, LINKS
from data_more import PAIRS, DAMAGE, DAMAGE_STEPS, MONTH_EVENTS, MONTH_PRODS, ICONS, PRODUCTS, GEAR_SECTIONS, HOME_GEAR
from assets import LOGO_SYMBOL

OUT = "out"
SITE = "Gartentierkompass"
BASE = "https://gartentierkompass.de/"
TAG = "schobiwan-21"
NOW = 11  # Monat für die statische Vorbelegung (JS korrigiert live)
MN = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
MS = ["januar", "februar", "maerz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember"]
MA = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
ACT = {"tag": ("tagaktiv", "i-sun"), "daemmerung": ("dämmerungsaktiv", "i-dusk"), "nacht": ("nachtaktiv", "i-moon")}
SIZES = [("s", "winzig (bis 1 cm)"), ("m", "klein (1–5 cm)"), ("l", "mittel (5–20 cm)"), ("xl", "größer als 20 cm")]
SISTERS = [("https://vogelkompass.de/", "Vogelkompass: Vögel bestimmen"), ("https://waldtierkompass.de/", "Waldtierkompass: Tiere im Wald"),
           ("https://meereskompass.de/", "Meereskompass: Tiere an der Küste")]
# Echte Fotos: key -> (Urheber, Lizenz, Lizenz-URL, Commons-Datei-URL). Leer = Platzhalter-Illustration.
PHOTOS = {}
if os.path.exists("photos.json"):
    PHOTOS = {k: tuple(v) for k, v in json.load(open("photos.json")).items()}

PPHOTOS = {k: tuple(v) for k, v in json.load(open("pphotos.json")).items()} if os.path.exists("pphotos.json") else {}
e = lambda t: html.escape(str(t), quote=True)
SP = {s["key"]: s for s in S}
NAMES = {**{s["key"]: s["name"] for s in S}, **{k: v[0] for k, v in EXTRA.items()}}
LATIN = {**{s["key"]: s["latin"] for s in S}, **{k: v[1] for k, v in EXTRA.items()}}
for s in S:
    m = s["mid"]
    s["sz"] = "s" if m <= 1 else "m" if m <= 5 else "l" if m <= 20 else "xl"
    s["acts"] = s["act"].split("|")
GSLUG = {g: slug for g, slug, _ in GROUPS}

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def ver(path):
    return hashlib.md5(open(os.path.join(OUT, path), "rb").read()).hexdigest()[:8]

# ---------------------------------------------------------------- Bausteine
ICON_DEFS = ('<symbol id="i-sun" viewBox="0 0 16 16"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4"/></symbol>'
             '<symbol id="i-dusk" viewBox="0 0 16 16"><path d="M2 11.5h12M4 11.5a4 4 0 0 1 8 0M8 3.5v2M3.2 6.2l1.3 1.1M12.8 6.2l-1.3 1.1"/></symbol>'
             '<symbol id="i-moon" viewBox="0 0 16 16"><path d="M10.5 2.5a5.5 5.5 0 1 0 3 9.6A6 6 0 0 1 10.5 2.5z" fill="currentColor" stroke="none"/></symbol>')
SEARCH_ICO = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>'
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"></path></svg>'
NEWWIN = '<span class="sr-only"> (öffnet in neuem Fenster)</span>'

ORG_ID = BASE + "#org"
def head(R, title, desc, path, og_type="website", og_img="photos/og.jpg", og_alt="Gartentierkompass", extra="", ld=None):
    css = ver("assets/site.css")
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
    c2 = [("ratgeber/nuetzlinge/index.html", "Nützlinge fördern"), ("ratgeber/schnecken/index.html", "Schnecken ohne Gift"), ("schadbilder/index.html", "Was frisst an meiner Pflanze?"),
          ("ausruestung/index.html", "Ausrüstung"), ("geschenke/index.html", "Geschenke für Gartenfreunde")]
    c3 = [("gartenjahr/index.html", "Gartenjahr und Kalender"), ("links/index.html", "Weiterführende Websites")] + [(u, t) for u, t in SISTERS]
    c4 = [("ueber/index.html", f"Über den {SITE}"), ("impressum/index.html", "Impressum"), ("datenschutz/index.html", "Datenschutz"), ("bildnachweis/index.html", "Bildnachweis und Lizenzen")]
    return (f'<footer> <div class="wrap"> <a class="flogo" href="{R}index.html"><svg class="logo" aria-hidden="true"><use href="#logo-mark"></use></svg><span>{SITE}</span></a> <div class="fcols"> '
            f'{col("Bestimmen", c1)} {col("Im Garten", c2)} {col("Mehr entdecken", c3)} {col("Rechtliches", c4)} </div> '
            f'<p class="footnote">Fotos: Wikimedia Commons, unter freien Lizenzen. Mit * markierte Links sind Werbelinks. Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.</p> </div> </footer> '
            f'<script type="module" src="{R}assets/{script}?v={ver("assets/" + script)}"></script> </body> </html>')

def cred_short(R, key):
    if key in PHOTOS:
        a, lic, _, _ = PHOTOS[key]
        return f'<a class="cred" href="{R}bildnachweis/index.html#f-{key}">Foto: {e(a)}, {e(lic)}<span class="sr-only"> – Lizenzangaben im Bildnachweis</span></a>'
    return f'<a class="cred" href="{R}bildnachweis/index.html#f-{key}">Illustration, Foto folgt<span class="sr-only"> – mehr im Bildnachweis</span></a>'

def cred_long(key, cropped=True):
    if key in PHOTOS:
        a, lic, lurl, src = PHOTOS[key]
        licpart = f'<a href="{lurl}" target="_blank" rel="noopener license">{e(lic)}<span class="sr-only"> (Lizenztext, öffnet in neuem Fenster)</span></a>' if lurl else e(lic)
        return (f'Foto: <a href="{src}" target="_blank" rel="noopener">{e(a)}<span class="sr-only"> (Quelle, öffnet in neuem Fenster)</span></a>, {licpart}, Wikimedia Commons'
                + (", zugeschnitten" if cropped else ""))
    return "Illustration: Gartentierkompass"

def img(R, key, sizes, w=720, h=576, eager=False, alt=""):
    return (f'<img src="{R}photos/{key}.webp" srcset="{R}photos/{key}-400.webp 400w, {R}photos/{key}.webp 720w" sizes="{sizes}" alt="{e(alt)}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}" decoding="async">')

def acts_html(s):
    return "".join(f'<span class="act" title="{ACT[a][0]}"><svg aria-hidden="true"><use href="#{ACT[a][1]}"></use></svg><span class="sr-only">{ACT[a][0]}</span></span>' for a in s["acts"])

def act_text(s):
    return " und ".join(ACT[a][0] for a in s["acts"])

def search_text(s):
    return " ".join([s["name"], s["latin"], s["grp"], GROUP_FORMS[s["grp"]], s["alias"], ROLE[s["role"]], s["short"], act_text(s)])

def card(R, s, i, eager=False):
    return (f'<li class="bird" id="{s["key"]}" style="--i:{i}" data-key="{s["key"]}" data-name="{e(s["name"])}" data-search="{e(search_text(s))}" data-grp="{e(s["grp"])}" '
            f'data-act="{s["act"]}" data-hab="{e("|".join(s["hab"]))}" data-size="{s["sz"]}" data-mid="{s["mid"]}" data-present="{",".join(map(str, s["present"]))}" data-peak="{",".join(map(str, s["peak"]))}"> '
            f'{img(R, s["key"], "(max-width: 760px) 46vw, 320px", eager=eager)}{cred_short(R, s["key"])} <div class="txt"> <h3><a class="open" href="{R}arten/{s["key"]}/index.html">{e(s["name"])}</a></h3> '
            f'<span class="meta"><span class="latin" lang="la">{e(s["latin"])}</span><span class="size">{e(s["size"])}</span></span> <span class="row"><span class="tag status">{e(s["grp"])}</span></span> '
            f'<p class="short">{e(s["short"])}</p> </div> <span class="acts">{acts_html(s)}</span> </li>')

def amazon(q):
    return f"https://www.amazon.de/s?k={quote_plus(q)}&tag={TAG}"

def product(R, key, compact=False, why=True):
    cat, name, by, pwhy, q, ico, _, pick = PRODUCTS[key]
    tip = '<span class="ptip">Unser Tipp</span>' if pick and not compact else ""
    meta = cat + (" · Unser Tipp" if pick and compact else "")
    pcred2 = ""
    if key in PPHOTOS and compact:
        a, lic = PPHOTOS[key][0], PPHOTOS[key][1]
        pimg = f'<div class="pimg"><img src="{R}photos/p-{key}-400.webp" srcset="{R}photos/p-{key}-400.webp 400w, {R}photos/p-{key}.webp 720w" sizes="88px" alt="" width="400" height="300" loading="lazy" decoding="async"></div>'
        pcred2 = f'<a class="cred pcred2" href="{R}bildnachweis/index.html#p-{key}">Beispielfoto · Foto: {e(a)}, {e(lic)}<span class="sr-only"> – Lizenzangaben im Bildnachweis</span></a> '
    elif key in PPHOTOS:
        a, lic = PPHOTOS[key][0], PPHOTOS[key][1]
        pimg = (f'<div class="pimg"><img src="{R}photos/p-{key}-400.webp" srcset="{R}photos/p-{key}-400.webp 400w, {R}photos/p-{key}.webp 720w" sizes="(max-width: 600px) 92vw, 360px" alt="" width="400" height="300" loading="lazy" decoding="async">{tip}</div>'
                f'<a class="cred pcred" href="{R}bildnachweis/index.html#p-{key}">Beispielfoto · Foto: {e(a)}, {e(lic)}<span class="sr-only"> – Lizenzangaben im Bildnachweis</span></a>')
    else:
        pimg = f'<div class="pimg"><span class="picon"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[ico]}</svg></span>{tip}</div>'
    return (f'<li class="product{" pick" if pick else ""}"> {pimg} <div class="pbody"> '
            f'<p class="pmeta"><span>{e(meta)}</span><span class="pad">Anzeige</span></p> <h3 class="pname">{e(name)}</h3> <p class="pby">{e(by)}</p> '
            + (f'<p class="pwhy">{e(pwhy)}</p> ' if why else "") + pcred2 +
            f' <a class="plink" href="{e(amazon(q))}" target="_blank" rel="sponsored nofollow noopener"><span>Bei Amazon ansehen<span aria-hidden="true">*</span></span>{ARROW}<span class="sr-only"> {e(name)} (Werbelink, öffnet in neuem Fenster)</span></a> </div> </li>')

ADNOTE = f'<p class="adnote"><span aria-hidden="true">*</span> Werbelink: Wenn du über diesen Link etwas kaufst, erhält der {SITE} eine kleine Provision von Amazon. Für dich ändert sich am Preis nichts. Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.</p>'

ROLE_ICO = {
    "nuetzling": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "bestaeuber": '<circle cx="12" cy="12" r="2.5"/><path d="M12 9.5C10 6 10 3.5 12 3.5s2 2.5 0 6M14.5 12c3.5-2 6-2 6 0s-2.5 2-6 0M12 14.5c2 3.5 2 6 0 6s-2-2.5 0-6M9.5 12c-3.5 2-6 2-6 0s2.5-2 6 0"/>',
    "schaedling": '<path d="M12 21c-5-3-8-7.5-8-12.5C4 6 6 4 8.5 4 10 4 11.3 4.7 12 6c.7-1.3 2-2 3.5-2C18 4 20 6 20 8.5 20 13.5 17 18 12 21z"/><circle cx="9.5" cy="10" r="1.3"/><circle cx="14.5" cy="13" r="1.6"/>',
    "gast": '<path d="M3 11 12 4l9 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "gemischt": '<path d="M12 3 3 20h18z"/><path d="M12 10v4M12 17h0"/>',
}

def months_bar(s):
    out = []
    for m in range(1, 13):
        c = "h" if m in s["peak"] else "p" if m in s["present"] else ""
        t = "Hauptzeit" if c == "h" else "aktiv" if c == "p" else "kaum zu sehen"
        out.append(f'<span data-month="{m}" class="{c}" title="{MN[m-1]}: {t}">{MA[m-1]}</span>')
    return "".join(out)

def join_de(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " und " + xs[-1]

def month_range(s):
    p = sorted(s["present"])
    if len(p) == 12:
        return "das ganze Jahr über zu sehen"
    return f"von {MN[p[0]-1]} bis {MN[p[-1]-1]} zu sehen" if p == list(range(p[0], p[-1] + 1)) else "zu sehen im " + join_de(MN[m-1] for m in p)

# ---------------------------------------------------------------- Seiten
ART = {"ihn": ("der", "den", "dem"), "sie": ("die", "die", "der"), "es": ("das", "das", "dem")}
def merkmal_links_for(k):
    return [(slug, short) for slug, title, short, intro, items in MERKMALE if any(x == k for x, _ in items)]

def related_for(s):
    same = [x for x in S if x["grp"] == s["grp"] and x["key"] != s["key"]]
    hab = set(s["hab"])
    same.sort(key=lambda x: (-len(hab & set(x["hab"])), x["name"]))
    return same[:4]

def page_species(s):
    R = "../../"; k = s["key"]
    nom, akk, dat = ART[s["pron"]]
    N = s["name"]
    desc = f'{N} ({s["latin"]}): {s["short"]} Merkmale, Rolle im Garten und wann du {s["pron"]} siehst.'
    peaks = join_de(f'<a href="{R}gartenjahr/{MS[m-1]}/index.html">{MN[m-1]}</a>' for m in s["peak"])
    pres = [m for m in range(1, 13) if m in s["present"]]
    hidden_sr = f'Aktiv: {join_de(MN[m-1] for m in pres)}. Hauptzeit: {join_de(MN[m-1] for m in s["peak"])}.'
    lifes = "".join(f'<details class="fold" open data-fold><summary><h3>{e(t)}</h3></summary><p>{e(x)}</p></details>' for t, x in s["life"])
    pairs = [p for p in PAIRS if k in (p[1], p[2])]
    alike = ""
    if pairs:
        p = pairs[0]; other = p[2] if p[1] == k else p[1]
        cred = cred_long(other, cropped=False)
        more_p = [q for q in pairs[1:]]
        also = (" <p>Wird auch verwechselt mit: " + ", ".join(f'<a href="{R}unterscheiden/{q[0]}/index.html">{e(NAMES[q[2] if q[1] == k else q[1]])}</a>' for q in more_p) + "</p>") if more_p else ""
        port = f' · <a href="{R}arten/{other}/index.html">{e(NAMES[other])} im Porträt</a>' if other in SP else ""
        alike = (f'<section class="alike" aria-labelledby="h-alike"> {img(R, other, "(max-width: 600px) 92vw, 400px", alt=NAMES[other])} <div> <h2 id="h-alike">Nicht verwechseln: {e(NAMES[other])}</h2> '
                 f'<p>{e(p[4])}</p> <p class="alike-cred"><small class="cred-inline">{cred}</small></p> '
                 f'<p><a href="{R}unterscheiden/{p[0]}/index.html">{e(NAMES[p[1]])} oder {e(NAMES[p[2]])}? Alle Unterschiede</a>{port}</p>{also} </div> </section> ')
    ml = merkmal_links_for(k)
    inmerk = (f'<p class="inmerk">Auch zu finden unter: ' + " · ".join(f'<a href="{R}merkmale/{slug}/index.html">{e(short)}</a>' for slug, short in ml) + '</p>') if ml else ""
    wiki = f'https://de.wikipedia.org/wiki/{quote_plus(N.replace(" ", "_"), safe="_")}'
    more = (f'<li><a href="{wiki}" target="_blank" rel="noopener">Wikipedia: {e(N)}{NEWWIN}</a></li>'
            f'<li><a href="https://www.inaturalist.org/search?q={quote_plus(s["latin"])}" target="_blank" rel="noopener">Beobachtungen bei iNaturalist{NEWWIN}</a></li>')
    if s["grp"] in ("Säugetiere", "Amphibien & Reptilien"):
        more += '<li><a href="https://waldtierkompass.de/" rel="noopener">Mehr Wildtiere im Waldtierkompass</a></li>'
    else:
        more += '<li><a href="https://vogelkompass.de/" rel="noopener">Vögel im Garten im Vogelkompass</a></li>'
    rg = [r for r, d in RATGEBER.items() if k in d["related"]]
    rgline = (" <p>" + " · ".join(f'<a href="{R}ratgeber/{r}/index.html">{e(RATGEBER[r]["title"])}</a>' for r in rg) + "</p>") if rg else ""
    dmg = [it for _, _, _, items in DAMAGE for it in items if k in it[3]]
    dmgline = (f'<p class="yeartext">Typisches Schadbild: <a href="{R}schadbilder/index.html">{e(dmg[0][1])}</a>.</p>' if dmg else "")
    rel = related_for(s)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": f'{N} erkennen', "description": desc, "inLanguage": "de-DE",
           "isPartOf": {"@id": BASE + "#website"}, "publisher": {"@id": ORG_ID}, "author": {"@type": "Person", "name": "Nico Schober"},
           "about": {"@type": "Taxon", "name": s["latin"], "alternateName": N, "taxonRank": "species"},
           "image": f'{BASE}photos/{k}.webp', "primaryImageOfPage": {"@type": "ImageObject", "url": f'{BASE}photos/{k}.webp', "width": 720, "height": 576}}]
    body = (head(R, f'{N} erkennen · {SITE}', desc, f'arten/{k}/', "article", og_img=f'photos/{k}.webp', og_alt=N, ld=ld)
            + nav(R, "bestimmen") + '<main id="main" tabindex="-1"> ' + crumbs(R, [("Arten", "arten/"), (N, f"arten/{k}/")]) +
            f'<article class="sp wrap"> <div class="sp-top"> <figure class="sp-photo"> {img(R, k, "(max-width: 760px) 92vw, 560px", eager=True, alt=N if k in PHOTOS else "")} <figcaption>{cred_long(k)}</figcaption> </figure> '
            f'<div class="sp-intro"> <h1>{e(N)}</h1> <p class="latin" lang="la">{e(s["latin"])}</p> <p class="row"><span class="tag status">{e(s["grp"])}</span><span class="tag">{e(s["size"])}</span>'
            + "".join(f'<span class="tag act-tag"><svg aria-hidden="true"><use href="#{ACT[a][1]}"></use></svg>{ACT[a][0]}</span>' for a in s["acts"]) +
            f'</p> <p class="habs">{"".join(f"<span>{e(h)}</span>" for h in s["hab"])}</p> <p class="text">{e(s["short"])} {e(s["hl"])}</p> '
            f'<div class="trackbox rolebox"><span class="trk-img"><svg viewBox="0 0 24 24" aria-hidden="true">{ROLE_ICO[s["role"]]}</svg></span><p><b>{e(ROLE[s["role"]])}</b>{e(s["roleline"])}</p></div> </div> </div>\n'
            f'<div class="sp-cols"> <div class="sp-main"> <section aria-labelledby="h-marks"> <h2 id="h-marks">So erkennst du {akk} {e(N)}</h2> <ul class="marks">{"".join(f"<li>{e(m)}</li>" for m in s["marks"])}</ul> {inmerk} '
            f'<dl class="facts"><dt>Rolle im Garten</dt><dd>{e(ROLE[s["role"]])}</dd><dt>Wo im Garten</dt><dd>{e(s["where"])}</dd><dt>Größe</dt><dd>{e(s["size"])}</dd><dt>Aktiv</dt><dd>{act_text(s)}</dd></dl> </section> '
            f'<section aria-labelledby="h-year"> <h2 id="h-year">Wann ist {nom} {e(N)} zu sehen?</h2> <div class="months" aria-hidden="true"> {months_bar(s)} </div> <p class="legend"><span><i></i>kaum zu sehen</span><span><i class="p"></i>aktiv</span><span><i class="h"></i>beste Zeit</span></p> '
            f'<p class="sr-only">{hidden_sr}</p> <p class="yeartext">{e(N)} ist {month_range(s)}. Besonders viel los ist im {peaks}. {e(s["hl"])}</p>{dmgline} </section> '
            f'<section class="life" aria-labelledby="h-life"> <h2 id="h-life">Lebensweise</h2> {lifes} </section> '
            f'<section class="helpbox" aria-label="Tipps"> <details class="fold" open><summary><h2>{e(s["help"][0])}</h2></summary><p>{e(s["help"][1])}</p>{rgline}</details> <details class="fold" open><summary><h2>{e(s["tip"][0])}</h2></summary><p>{e(s["tip"][1])}</p></details> </section> '
            f'{alike}<section class="more" aria-labelledby="h-more"> <h2 id="h-more">Mehr erfahren</h2> <ul class="morelinks"> {more} </ul> </section> </div>\n'
            f'<aside class="sp-side" aria-label="Empfehlungen"> <section class="gearbox" aria-labelledby="h-gear"><h2 id="h-gear">Passend dazu</h2><ul class="products compact"> '
            + "".join(product(R, p, compact=True, why=False) for p in s["prods"]) +
            f' </ul>{ADNOTE}<p class="gearall"><a href="{R}ausruestung/index.html">Alle Ausrüstungstipps ansehen</a></p></section> </aside> </div> '
            f'<section class="related" aria-labelledby="h-rel"> <h2 id="h-rel">Oft in der Nähe</h2> <ul class="grid">{"".join(card(R, x, i) for i, x in enumerate(rel))}</ul> </section> </article> </main> ' + footer(R))
    write(f"arten/{k}/index.html", body)

def filter_bar():
    def chips(g, vals):
        return "".join(f'<button class="chip" type="button" data-g="{g}" data-v="{e(v)}" aria-pressed="false">{e(l)}</button>' for v, l in vals)
    return (f'<div class="bar" id="arten"> <div class="wrap barrow" role="search" aria-label="Arten suchen und filtern"> <label class="search" for="q">{SEARCH_ICO}<span class="sr-only">Art suchen</span> '
            f'<input type="search" id="q" placeholder="Tier suchen, z. B. Schnecke" autocomplete="off" enterkeyhint="search"></label> <button class="chip ftoggle" id="f-toggle" type="button" aria-expanded="false" aria-controls="fpanel"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4"></path></svg>Filter<b class="fcount" id="fcount" hidden></b></button> '
            f'<label class="sortsel" for="sort"><span>Sortieren</span> <select id="sort"><option value="now">Jetzt aktiv zuerst</option><option value="az">Name A–Z</option><option value="size">Größe, klein zuerst</option></select></label> <span class="rcount" id="rcount" aria-live="polite">{len(S)} Arten</span> </div> '
            f'<div class="fpanel" id="fpanel" hidden> <div class="wrap fgrid"> <fieldset><legend>Gruppe</legend><div class="fchips">{chips("grp", [(g, g) for g, _, _ in GROUPS])}</div></fieldset>'
            f'<fieldset><legend>Aktiv</legend><div class="fchips">{chips("act", [(k, v[0]) for k, v in ACT.items()])}</div></fieldset>'
            f'<fieldset><legend>Wo im Garten</legend><div class="fchips">{chips("hab", [(h, h) for h in HABS])}</div></fieldset>'
            f'<fieldset><legend>Größe</legend><div class="fchips">{chips("size", SIZES)}</div></fieldset>'
            f'<fieldset><legend>Außerdem</legend><div class="fchips"><button class="chip" type="button" data-g="flag" data-v="now" aria-pressed="false">Jetzt im <span data-now-name>{MN[NOW-1]}</span> aktiv</button></div></fieldset> '
            f'<div class="factions"><button class="btn ghost" id="f-reset" type="button">Alle Filter zurücksetzen</button><button class="btn" id="f-done" type="button">Ergebnisse anzeigen</button></div> </div> </div> <div class="wrap active" id="active" hidden></div> </div>')

SPOT = ["siebenpunkt-marienkaefer", "tagpfauenauge", "igel", "erdhummel", "eichhoernchen", "zitronenfalter", "taubenschwaenzchen", "rote-mauerbiene",
        "hainschwebfliege", "zauneidechse", "erdkroete", "honigbiene", "gartenkreuzspinne", "teichmolch", "weinbergschnecke", "blindschleiche"]
def spot_attr(s):
    return f' data-spot="{SPOT.index(s["key"]) + 1}"' if s["key"] in SPOT else ""

def spot_cred(k):
    if k in PHOTOS:
        a, lic, lurl, src = PHOTOS[k]
        l = f'<a href="{lurl}" target="_blank" rel="noopener license">{e(lic)}</a>' if lurl else e(lic)
        return f'Foto: <a href="{src}" target="_blank" rel="noopener">{e(a)}</a>, {l}'
    return "Illustration"

def page_home():
    R = ""
    desc = f"Gartentiere bestimmen: {len(S)} Nützlinge, Schädlinge und Gartengäste mit Merkmalen, Schadbildern, Doppelgängern und Gartenjahr."
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "#website", "name": SITE, "url": BASE, "inLanguage": "de-DE", "publisher": {"@id": ORG_ID}, "description": "Tiere im Garten bestimmen: Nützlinge, Schädlinge, Schadbilder und Gartenjahr.",
           "potentialAction": {"@type": "SearchAction", "target": BASE + "?q={search_term_string}", "query-input": "required name=search_term_string"}},
          {"@context": "https://schema.org", "@type": "Organization", "@id": ORG_ID, "name": SITE, "url": BASE, "logo": BASE + "icon-512.png", "email": "info@nicoschober.com", "founder": {"@type": "Person", "name": "Nico Schober"}}]
    chips = "".join(f'<button type="button" class="hchip" data-hgrp="{e(g)}">{e(g)}<span class="sr-only"> ({sum(1 for s in S if s["grp"] == g)})</span></button>' for g, _, _ in GROUPS)
    events = "".join(f'<ul class="h5-events" data-m="{m}"{"" if m == NOW else " hidden"}>{"".join(f"<li>{e(x)}</li>" for x in MONTH_EVENTS[m])}</ul>' for m in range(1, 13))
    nowsp = [s for s in S if NOW in s["peak"]] + [s for s in S if NOW in s["present"] and NOW not in s["peak"]]
    pool = [s for s in nowsp if s["key"] in SPOT]
    spot = min(pool, key=lambda s: SPOT.index(s["key"]) + (0 if NOW in s["peak"] else 100)) if pool else (nowsp[0] if nowsp else S[0])
    rank = lambda s: SPOT.index(s["key"]) if s["key"] in SPOT else (90 if s["key"] == "regenwurm" else 50)
    order = sorted(nowsp, key=rank) + [s for s in S if s not in nowsp]
    ncards = "".join(
        f'<li{spot_attr(s)} data-peak="{",".join(map(str, s["peak"]))}" data-present="{",".join(map(str, s["present"]))}" data-k="{s["key"]}" data-name="{e(s["name"])}" data-hl="{e(s["hl"])}"{"" if (s in nowsp and s is not spot) else " hidden"}>'
        f'<a href="arten/{s["key"]}/index.html"><img src="photos/{s["key"]}-400.webp" alt="" width="400" height="300" loading="{"eager" if i < 5 else "lazy"}" decoding="async"><span class="nc-ov"><b>{e(s["name"])}</b><i>Hauptzeit</i></span></a>{cred_short(R, s["key"])}</li>'
        for i, s in enumerate(order))
    grid = "".join(card(R, s, i, eager=i < 4) for i, s in enumerate(sorted(S, key=lambda x: x["name"])))
    empty_groups = "".join(f'<button type="button" class="chip" data-sgrp="{e(g)}">{e(g)}</button>' for g, _, _ in GROUPS)
    explore = (f'<li><a href="schadbilder/index.html"><b>Was frisst an meiner Pflanze?</b><span>Löcher, Buchten, Gespinste und Hügel: vom Schadbild zum Verursacher, mit sanften Lösungen.</span></a></li>'
               f'<li><a href="unterscheiden/index.html"><b>Doppelgänger unterscheiden</b><span>Marienkäfer oder Asiatischer Marienkäfer, Schwebfliege oder Wespe: {len(PAIRS)} Vergleiche.</span></a></li>'
               f'<li><a href="gartenjahr/index.html"><b>Das Gartenjahr</b><span>Krötenwanderung, Schneckenzeit, Leimring: was im Garten wann passiert, Monat für Monat.</span></a></li>'
               f'<li><a href="merkmale/index.html"><b>Nach Aussehen bestimmen</b><span>Roter Käfer, grüne Raupe, weißer Schmetterling: {len(MERKMALE)} Merkmale führen zur Art.</span></a></li>'
               f'<li><a href="ratgeber/nuetzlinge/index.html"><b>Nützlinge fördern</b><span>Wildbienenhotel, Igelhaus, Totholz und Teich: so holst du Helfer in den Garten.</span></a></li>'
               f'<li><a href="ratgeber/schnecken/index.html"><b>Schnecken ohne Gift</b><span>Schneckenzaun, Absammeln, Nematoden und Laufenten im Vergleich.</span></a></li>'
               f'<li><a href="groessen/index.html"><b>Größenvergleich</b><span>Von der Blattlaus bis zum Steinmarder auf einer Skala.</span></a></li>'
               f'<li><a href="ausruestung/index.html"><b>Ausrüstung</b><span>Nützlinge, Schneckenzaun, Nisthilfen und Lupe für einen naturnahen Garten.</span></a></li>'
               f'<li><a href="https://vogelkompass.de/" rel="noopener"><b>Vögel im Garten?</b><span>Meise, Rotkehlchen und Co. findest du auf der Schwesterseite Vogelkompass.</span></a></li>'
               f'<li><a href="https://waldtierkompass.de/" rel="noopener"><b>Fuchs, Reh oder Dachs?</b><span>Größere Wildtiere und ihre Spuren findest du auf der Schwesterseite Waldtierkompass.</span></a></li>')
    body = (head(R, f"{SITE} – Tiere im Garten bestimmen", desc, "", ld=ld) + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> <header class="hero6"> <div class="wrap hero6-in"> <div class="h6-text"> '
            f'<p class="h6-kicker"><svg class="buoy" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V11" stroke="#2f6b3f" stroke-width="1.8" stroke-linecap="round"/><path d="M12 11c0-3 2.5-5.5 6-5.5 0 3.5-2.5 5.5-6 5.5z" fill="#6b9a3c"/><path d="M12 14c0-2.6-2-4.5-5-4.5 0 3 2 4.5 5 4.5z" fill="#8fbf55"/></svg><span>Naturgarten</span><span aria-hidden="true">·</span><span>{len(S)} Gartentiere</span></p> '
            '<h1 class="h6-title h6-single">Wer lebt in deinem Garten?</h1> '
            '<p class="lede">Nützlinge, Bestäuber und Schädlinge im Garten bestimmen: am Foto, an den Fraßspuren und an wenigen sicheren Merkmalen.</p> '
            f'<form class="hsearch" id="hsearch" role="search" aria-label="Tier suchen"> <label for="hq"><span class="sr-only">Tier suchen</span>{SEARCH_ICO}<input type="search" id="hq" placeholder="Name oder Aussehen, z. B. Marienkäfer" autocomplete="off" enterkeyhint="search"></label> <button class="hsearch-btn" type="submit">Suchen</button> </form> '
            f'<div class="hchips" role="group" aria-label="Nach Gruppe zeigen">{chips}<a class="hchip hchip-all" href="arten/index.html">Alle Gruppen</a></div> </div> '
            f'<figure class="spot6" id="spot"> <a href="arten/{spot["key"]}/index.html" id="spot-link" class="s6-link"><span class="s6-photo"><img id="spot-img" src="photos/{spot["key"]}.webp" srcset="photos/{spot["key"]}-400.webp 400w, photos/{spot["key"]}.webp 720w" sizes="(max-width: 900px) 92vw, 480px" alt="" width="720" height="576" fetchpriority="high"></span> '
            f'<span class="s6-label"><span class="spot-tag">Jetzt zu sehen · <span data-now-name>{MN[NOW-1]}</span></span><b id="spot-name">{e(spot["name"])}</b><span id="spot-hl">{e(spot["hl"])}</span></span></a> '
            f'<small class="spot-cred" id="spot-cred">{spot_cred(spot["key"])}</small> </figure> </div> '
            '<svg class="h6-ripples" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true" focusable="false"><polyline points="0,18.0 12,22.6 24,24.1 36,22.6 48,21.0 60,21.8 72,24.4 84,25.5 96,23.0 108,18.2 120,14.4 132,13.9 144,15.4 156,15.7 168,13.4 180,10.2 192,9.7 204,12.9 216,17.5 228,20.1 240,19.7 252,18.6 264,19.8 276,23.4 288,26.6 300,26.3 312,22.8 324,18.9 336,17.7 348,18.8 360,19.1 372,16.5 384,12.1 396,9.3 408,10.3 420,13.8 432,16.3 444,16.2 456,14.8 468,15.5 480,19.4 492,24.0 504,26.1 516,24.5 528,21.6 540,20.6 552,22.0 564,23.2 576,21.4 588,16.8 600,12.4 612,11.2 624,13.0 636,14.9 648,14.3 660,12.0 672,11.2 684,14.1 696,19.0 708,22.7 720,22.9 732,21.2 744,20.7 756,22.9 768,25.6 780,25.7 792,22.1 804,17.3 816,14.8 828,15.4 840,16.5 852,15.5 864,12.1 876,9.4 888,10.1 900,14.1 912,18.0 924,19.2 936,18.2 948,17.9 960,20.4 972,24.6 984,27.0 996,25.5 1008,21.6 1020,18.9 1032,19.0 1044,20.2 1056,19.4 1068,15.5 1080,11.1 1092,9.5 1104,11.5 1116,14.7 1128,15.9 1140,14.7 1152,13.7 1164,15.7 1176,20.4 1188,24.6 1200,25.4 1212,23.2 1224,21.1 1236,21.5 1248,23.5 1260,23.9 1272,20.8 1284,15.7 1296,12.3 1308,12.4 1320,14.3 1332,15.0 1344,13.1 1356,10.7 1368,11.1 1380,15.0 1392,19.9 1404,22.2 1416,21.5 1428,20.1 1440,21.1"/><polyline points="0,42.2 12,44.9 24,43.8 36,40.4 48,38.7 60,39.1 72,38.3 84,34.8 96,31.5 108,31.9 120,34.8 132,36.4 144,35.9 156,36.5 168,40.1 180,43.8 192,44.1 204,41.7 216,40.3 228,41.1 240,40.7 252,37.2 264,33.1 276,32.2 288,34.1 300,35.2 312,34.2 324,34.1 336,37.4 348,41.7 360,43.2 372,41.8 384,41.0 396,42.4 408,42.9 420,40.0 432,35.5 444,33.6 456,34.5 468,35.0 480,33.3 492,32.2 504,34.7 516,39.1 528,41.5 540,40.9 552,40.6 564,42.7 576,44.4 588,42.5 600,38.2 612,35.6 624,35.9 636,36.0 648,33.6 660,31.3 672,32.6 684,36.5 696,39.2 708,39.1 720,39.2 732,41.8 744,44.7 756,44.1 768,40.6 780,37.9 792,37.9 804,37.8 816,35.1 828,31.7 840,31.5 852,34.5 864,37.1 876,37.1 888,37.1 900,39.9 912,43.7 924,44.7 936,42.1 948,39.8 960,39.9 972,40.1 984,37.3 996,33.2 1008,31.6 1020,33.5 1032,35.5 1044,35.3 1056,34.8 1068,37.3 1080,41.7 1092,43.9 1104,42.6 1116,40.9 1128,41.4 1140,42.2 1152,40.0 1164,35.5 1176,32.8 1188,33.6 1200,35.0 1212,34.2 1224,32.9 1236,34.7 1248,39.1 1260,42.2 1272,41.9 1284,40.9 1296,42.0 1308,43.7 1320,42.5 1332,38.3 1344,34.9 1356,34.8 1368,35.5 1380,34.2 1392,31.9 1404,32.5 1416,36.4 1428,39.9 1440,40.3"/></svg> </header>\n'
            f'<section class="nowband" aria-labelledby="now-h"> <div class="wrap"> <div class="now-head"><h2 id="now-h">Jetzt im <span data-now-name>{MN[NOW-1]}</span> im Garten</h2><div class="now-nav"><a href="gartenjahr/index.html" data-now-link>Alle im <span data-now-name>{MN[NOW-1]}</span></a>'
            '<button class="cbtn" type="button" id="now-prev" aria-controls="nowcards" aria-label="Vorherige Tiere" disabled><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 6-6 6 6 6"/></svg></button><button class="cbtn" type="button" id="now-next" aria-controls="nowcards" aria-label="Weitere Tiere"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 6 6 6-6 6"/></svg></button></div></div> '
            f'<ul class="nowcards" id="nowcards">{ncards}</ul> </div> </section>\n' + filter_bar() + '\n'
            '<section class="sub" aria-labelledby="arten-h"> <div class="wrap"> <h2 class="sr-only" id="arten-h">Arten</h2> <p class="actlegend" aria-hidden="true"><span><svg aria-hidden="true"><use href="#i-sun"></use></svg> tagaktiv</span><span><svg aria-hidden="true"><use href="#i-dusk"></use></svg> dämmerungsaktiv</span><span><svg aria-hidden="true"><use href="#i-moon"></use></svg> nachtaktiv</span></p> '
            f'<ul class="grid" id="grid"> {grid} </ul> <div class="empty" id="empty" hidden><p id="empty-msg">Kein Tier passt zu deiner Suche oder Auswahl.</p><p id="empty-suggest" hidden></p><div class="empty-groups" aria-label="Stattdessen eine Gruppe ansehen">{empty_groups}</div><button class="btn ghost" type="button" id="empty-reset">Suche und Filter zurücksetzen</button></div> </div> </section>\n'
            f'<section class="gearband" aria-labelledby="h-gear"><div class="wrap"><div class="head-row"><h2 id="h-gear">Gut ausgerüstet für den Naturgarten</h2><a class="gearmore" href="ausruestung/index.html">Alle Empfehlungen ansehen</a></div><ul class="products">{"".join(product(R, p) for p in HOME_GEAR)}</ul>{ADNOTE}</div></section>\n'
            f'<section class="block"> <div class="wrap"> <h2>Weiter entdecken</h2> <ul class="explore"> {explore} </ul> </div> </section> </main> ' + footer(R, "home.js"))
    write("index.html", body)

def page_arten():
    R = "../"
    parts = []
    for g, slug, d in GROUPS:
        lst = sorted([s for s in S if s["grp"] == g], key=lambda x: x["name"])
        parts.append(f'<h2 class="h3 grp-h" id="g-{slug}">{e(g)}</h2><ul class="grid">{"".join(card(R, s, i, eager=(g == GROUPS[0][0] and i < 4)) for i, s in enumerate(lst))}</ul>')
    body = (head(R, f"Alle Gartentiere · {SITE}", f"Alle {len(S)} Gartentiere im Überblick: Nützlinge, Bestäuber, Schädlinge, Säugetiere, Amphibien und Reptilien.", "arten/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Arten", "arten/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Alle Gartentiere</h1> <p class="actlegend" aria-hidden="true"><span><svg aria-hidden="true"><use href="#i-sun"></use></svg> tagaktiv</span><span><svg aria-hidden="true"><use href="#i-dusk"></use></svg> dämmerungsaktiv</span><span><svg aria-hidden="true"><use href="#i-moon"></use></svg> nachtaktiv</span></p> '
            f'<p class="intro">{len(S)} Arten, nach Gruppen geordnet. Zum Suchen und Filtern geht es zur <a href="../index.html#arten">Startseite</a>.</p> {"".join(parts)} </div> </section> </main> ' + footer(R))
    write("arten/index.html", body)

def pair_fig(R, key, sizes, eager, big=False):
    lat = f' <i lang="la">{e(LATIN[key])}</i>' if big else ""
    return (f'<figure>{img(R, key, sizes, eager=eager, alt=NAMES[key] if (big and key in PHOTOS) else "")}<figcaption>{e(NAMES[key])}{lat}<small>{cred_long(key, cropped=big)}</small></figcaption></figure>')

def pair_card(R, p, h="h2"):
    slug, a, b, intro, short, rows, merk = p
    return (f'<li class="pair"> <div class="ph"> {pair_fig(R, a, "(max-width: 600px) 46vw, 240px", False)}{pair_fig(R, b, "(max-width: 600px) 46vw, 240px", False)} </div> <div class="pb"> '
            f'<{h}><a class="pair-link" href="{R}unterscheiden/{slug}/index.html">{e(NAMES[a])} oder {e(NAMES[b])}?</a></{h}> <p>{e(short)}</p> <span class="to" aria-hidden="true">Alle Unterschiede</span> </div> </li>')

def page_pairs():
    R = "../"
    body = (head(R, f"Doppelgänger im Garten unterscheiden · {SITE}", "Marienkäfer oder Asiatischer Marienkäfer, Schwebfliege oder Wespe, Maulwurf oder Schermaus: die entscheidenden Merkmale im Vergleich.", "unterscheiden/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Doppelgänger", "unterscheiden/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Doppelgänger unterscheiden</h1> <p class="intro">Manche Gartentiere sehen sich zum Verwechseln ähnlich, und oft ist der eine ein Helfer, der andere ein Schädling. Diese Merkmale helfen beim Unterscheiden.</p> '
            f'<ul class="pairs">{"".join(pair_card(R, p) for p in PAIRS)}</ul> </div> </section> </main> ' + footer(R))
    write("unterscheiden/index.html", body)
    R = "../../"
    for i, p in enumerate(PAIRS):
        slug, a, b, intro, short, rows, merk = p
        na, nb = NAMES[a], NAMES[b]
        trs = "".join(f'<tr><th scope="row">{e(r[0])}</th><td data-label="{e(na)}">{e(r[1])}</td><td data-label="{e(nb)}">{e(r[2])}</td></tr>' for r in rows)
        btns = " ".join(f'<a class="btn{" ghost" if j else ""}" href="{R}arten/{k}/index.html">{e(NAMES[k])} im Porträt</a>' for j, k in enumerate([x for x in (a, b) if x in SP]))
        rel = [PAIRS[(i + d) % len(PAIRS)] for d in (1, 2, 3)]
        body = (head(R, f"{na} oder {nb}? · {SITE}", f"{na} oder {nb}? {intro}", f"unterscheiden/{slug}/", "article") + nav(R, "bestimmen") +
                '<main id="main" tabindex="-1"> ' + crumbs(R, [("Doppelgänger", "unterscheiden/"), (f"{na} oder {nb}", f"unterscheiden/{slug}/")]) +
                f'<article class="wrap pairpage"> <h1>{e(na)} oder {e(nb)}?</h1> <p class="intro">{e(intro)}</p> <div class="ph big"> {pair_fig(R, a, "(max-width: 760px) 92vw, 560px", True, True)}{pair_fig(R, b, "(max-width: 760px) 92vw, 560px", True, True)} </div> '
                f'<section aria-labelledby="h-cmp"> <h2 id="h-cmp">Die Unterschiede</h2> <div class="cmp-wrap"><table class="cmp cmp-pair"> <thead><tr><td></td><th scope="col">{e(na)}</th><th scope="col">{e(nb)}</th></tr></thead> <tbody>{trs}</tbody> </table></div> '
                f'<p class="merksatz"><b>Merkhilfe:</b> {e(merk)}</p> <p class="actions"> {btns} </p> </section> '
                f'<section class="related" aria-labelledby="h-more"> <h2 id="h-more">Weitere Doppelgänger</h2> <ul class="pairs three">{"".join(pair_card(R, q, "h3") for q in rel)}</ul> </section> </article> </main> ' + footer(R))
        write(f"unterscheiden/{slug}/index.html", body)

DMG_ICO = {
 "holes": '<path d="M50 8C80 22 86 66 50 92 14 66 20 22 50 8Z"/><circle cx="38" cy="40" r="7" fill="var(--surface)"/><circle cx="60" cy="58" r="9" fill="var(--surface)"/><circle cx="44" cy="70" r="5" fill="var(--surface)"/><path d="M70 30q8 10 0 22" fill="none" stroke="var(--surface)" stroke-width="3"/>',
 "notch": '<path d="M50 8C80 22 86 66 50 92 14 66 20 22 50 8Z"/><circle cx="22" cy="44" r="7" fill="var(--surface)"/><circle cx="20" cy="62" r="6" fill="var(--surface)"/><circle cx="79" cy="40" r="7" fill="var(--surface)"/><circle cx="76" cy="62" r="6" fill="var(--surface)"/>',
 "caterpillar": '<circle cx="22" cy="58" r="10"/><circle cx="38" cy="50" r="10"/><circle cx="54" cy="48" r="10"/><circle cx="70" cy="52" r="10"/><circle cx="84" cy="60" r="11"/><circle cx="86" cy="57" r="2.5" fill="var(--surface)"/><path d="M14 74h76" stroke="currentColor" stroke-width="4"/>',
 "curl": '<path d="M20 80C20 40 45 18 80 18 82 45 66 64 44 64 54 52 56 42 52 36 38 46 32 62 28 82Z"/><circle cx="62" cy="34" r="3.5" fill="var(--surface)"/><circle cx="70" cy="40" r="3.5" fill="var(--surface)"/><circle cx="56" cy="44" r="3.5" fill="var(--surface)"/>',
 "cloud": '<path d="M50 30C80 42 84 74 50 92 16 74 20 42 50 30Z"/><path d="M30 18l6 4M48 8v7M66 16l-5 5M24 30l7 1M76 28l-7 2" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>',
 "lily": '<path d="M50 90V40"/><path d="M50 40C30 30 18 14 22 6c14 4 26 16 28 34zM50 40c20-10 32-26 28-34-14 4-26 16-28 34z"/><ellipse cx="62" cy="62" rx="9" ry="6"/><path d="M50 90V40" stroke="currentColor" stroke-width="5"/>',
 "web": '<circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="26" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="12" fill="none" stroke="currentColor" stroke-width="3"/><path d="M50 10v80M10 50h80M22 22l56 56M78 22 22 78" stroke="currentColor" stroke-width="3"/>',
 "spun": '<path d="M30 86C20 56 36 26 60 14c10 24 2 52-20 66"/><path d="M40 80C60 70 80 54 86 30" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="3 4"/><path d="M28 70l40-30M32 54l28-24" stroke="var(--surface)" stroke-width="2.5"/>',
 "apple": '<path d="M50 28c-10-8-34-6-34 22 0 22 16 40 34 40s34-18 34-40c0-28-24-30-34-22z"/><path d="M50 28c0-10 4-16 10-20" stroke="currentColor" stroke-width="4" fill="none"/><circle cx="62" cy="54" r="6" fill="var(--surface)"/><circle cx="70" cy="64" r="2" fill="var(--surface)"/><circle cx="66" cy="68" r="2" fill="var(--surface)"/>',
 "berry": '<path d="M50 30c24 0 34 14 30 30-4 18-18 30-30 32-12-2-26-14-30-32-4-16 6-30 30-30z"/><path d="M38 30l12-14 12 14" fill="none" stroke="currentColor" stroke-width="5"/><circle cx="58" cy="56" r="10" fill="var(--surface)"/>',
 "molehill": '<path d="M8 82h84"/><path d="M14 82C20 50 36 34 50 34s30 16 36 48z"/><ellipse cx="50" cy="82" rx="8" ry="5" fill="var(--surface)"/><path d="M8 82h84" stroke="currentColor" stroke-width="4"/>',
 "flathill": '<path d="M6 82C16 66 34 60 54 62s30 8 40 20z"/><ellipse cx="82" cy="78" rx="6" ry="7" fill="var(--surface)"/><path d="M30 66l-4-10M42 63l2-12M56 63l-2-10" stroke="currentColor" stroke-width="3"/><path d="M4 82h92" stroke="currentColor" stroke-width="4"/>',
 "lawn": '<path d="M6 84h88" stroke="currentColor" stroke-width="4"/><path d="M12 84l3-18 3 18M24 84l3-22 3 22M74 84l3-20 3 20M86 84l3-16 3 16"/><path d="M36 84c4-6 24-6 28 0z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M42 40a12 12 0 1 1 14 12" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><circle cx="58" cy="52" r="5"/>',
 "pot": '<path d="M24 50h52l-6 40H30z"/><path d="M50 50V30c-10-2-18-10-20-20 10 0 18 6 20 14 2-8 10-14 20-14-2 10-10 18-20 20" fill="none" stroke="currentColor" stroke-width="4"/><path d="M42 72a7 7 0 1 1 9 6" fill="none" stroke="var(--surface)" stroke-width="5" stroke-linecap="round"/>',
}

def page_damage():
    R = "../"
    secs = []
    for sid, title, intro, items in DAMAGE:
        lis = []
        for ico, t, txt, causes in items:
            k = causes[0]
            lis.append(f'<li class="trk"><a href="{R}arten/{k}/index.html"><span class="trk-img"><svg class="ico" viewBox="0 0 100 100" aria-hidden="true" fill="currentColor">{DMG_ICO[ico]}</svg></span>'
                       f'<span class="trk-t"><b>{e(t)}</b><span>{e(txt)}</span><span class="cause">Verursacher: {e(NAMES[k])}</span></span></a></li>')
        secs.append(f'<section class="block" aria-labelledby="h-{sid}" id="g-{sid}"><div class="wrap"><h2 id="h-{sid}">{e(title)}</h2><p class="intro">{e(intro)}</p><ul class="trkgrid">{"".join(lis)}</ul></div></section>')
    steps = "".join(f'<li><b>{e(a)}</b> {e(b)}</li>' for a, b in DAMAGE_STEPS)
    jump = "".join(f'<li><a href="#g-{sid}">{e(t)}</a></li>' for sid, t, _, _ in DAMAGE) + '<li><a href="#h-help">Helfer im Garten</a></li>'
    helpers = [s for s in S if s["role"] == "nuetzling"][:8]
    hl = "".join(f'<li><a href="{R}arten/{s["key"]}/index.html"><b>{e(s["name"])}</b><span>{e(s["roleline"])}</span></a></li>' for s in helpers)
    prods = ["schneckenzaun", "kulturschutznetz", "nematoden-dickmaul", "leimring", "becherlupe", "marienkaeferlarven"]
    body = (head(R, f"Was frisst an meiner Pflanze? Schadbilder erkennen · {SITE}", "Löcher in Blättern, Gespinste im Buchs, Hügel im Rasen: Schadbilder im Garten erkennen, den Verursacher finden und sanft gegensteuern.", "schadbilder/") + nav(R, "schaden") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Was frisst?", "schadbilder/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Was frisst an meiner Pflanze?</h1> <p class="intro">Oft sieht man den Täter nicht, nur das, was er hinterlässt. Schau dir das Schadbild an, finde den Verursacher und erfahre, wie du ohne Gift gegensteuern kannst.</p> '
            f'<ol class="steps">{steps}</ol> <nav class="jump" aria-label="Zu den Bereichen springen"><ul class="pills">{jump}</ul></nav> </div> </section> {"".join(secs)}'
            f'<section class="block" aria-labelledby="h-help"><div class="wrap"><h2 id="h-help">Helfer im Garten</h2><p class="intro">Diese Tiere fressen viele der Verursacher. Je mehr von ihnen im Garten leben, desto seltener musst du eingreifen.</p><ul class="explore">{hl}</ul></div></section>'
            f'<section class="block" aria-labelledby="h-gear"><div class="wrap"><h2 id="h-gear">Sanfte Helfer gegen Schäden</h2><ul class="products">{"".join(product(R, p) for p in prods)}</ul>{ADNOTE}</div></section> </main> ' + footer(R))
    write("schadbilder/index.html", body)

def cal_table(R):
    head_ = "".join(f'<th scope="col" data-month="{m}"><a href="{R}gartenjahr/{MS[m-1]}/index.html"><abbr title="{MN[m-1]}">{MA[m-1]}</abbr></a></th>' for m in range(1, 13))
    rows = []
    for g, _, _ in GROUPS:
        rows.append(f'<tr class="grow"><th scope="rowgroup" colspan="13"><span>{e(g)}</span></th></tr>')
        for s in sorted([s for s in S if s["grp"] == g], key=lambda x: x["name"]):
            tds = []
            for m in range(1, 13):
                c = "h" if m in s["peak"] else "p" if m in s["present"] else ""
                t = "Hauptzeit" if c == "h" else "aktiv" if c == "p" else "kaum zu sehen"
                tds.append(f'<td data-month="{m}" class="m {c}".strip() title="{e(s["name"])}, {MN[m-1]}: {t}"><span class="sr-only">{MN[m-1]}: {t}</span></td>'.replace('".strip()', '"').replace('class="m "', 'class="m"'))
            rows.append(f'<tr><th scope="row" class="n"><a href="{R}arten/{s["key"]}/index.html">{e(s["name"])}</a></th> {"".join(tds)}</tr>')
    return (f'<div class="cal-wrap" tabindex="0" role="region" aria-label="Kalender: wann welche Art aktiv ist"><table class="cal"> <caption class="sr-only">Aktivität aller Arten nach Monaten</caption> '
            f'<thead><tr><th scope="col"><span class="sr-only">Art</span></th> {head_}</tr></thead> <tbody> {"".join(rows)} </tbody></table></div>')

def page_year():
    R = "../"
    ml = "".join(f'<li data-month="{m}"><a href="{R}gartenjahr/{MS[m-1]}/index.html"><b>{MN[m-1]}</b><span>{sum(1 for s in S if m in s["present"])} aktiv, {sum(1 for s in S if m in s["peak"])} in Hauptzeit</span></a></li>' for m in range(1, 13))
    yl = "".join(f'<li data-month="{m}"><b>{MN[m-1]}</b><span>{e(MONTH_EVENTS[m][0])}</span></li>' for m in range(1, 13))
    legend = '<p class="legend"><span><i></i>kaum zu sehen</span><span><i class="p"></i>aktiv</span><span><i class="h"></i>beste Zeit</span><span><i class="now"></i>aktueller Monat</span></p>'
    body = (head(R, f"Das Gartenjahr: wer ist wann im Garten? · {SITE}", "Krötenwanderung, Schneckenzeit, Leimring und Winterquartier: was im Garten wann passiert, mit Kalender für alle Arten.", "gartenjahr/") + nav(R, "jahr") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Gartenjahr", "gartenjahr/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Das Gartenjahr</h1> <p class="intro">Was im Garten wann passiert: Krötenwanderung, Schneckenzeit, Winterquartier. Wähle einen Monat, um zu sehen, wer dann unterwegs ist und was jetzt zu tun ist.</p> '
            f'<ul class="monthlinks">{ml}</ul> </div> </section>\n<section class="block" aria-labelledby="h-ev"> <div class="wrap"> <h2 id="h-ev">Das Wichtigste im Jahreslauf</h2> <ul class="yearline">{yl}</ul> </div> </section>\n'
            f'<section class="block" aria-labelledby="h-cal"> <div class="wrap"> <h2 id="h-cal">Wann siehst du wen?</h2> <p class="intro">Monate, in denen die Art aktiv ist, und wann sie besonders gut zu beobachten ist.</p> {legend} <p class="swipe">Seitlich wischen, um alle Monate zu sehen.</p> {cal_table(R)} </div> </section> </main> ' + footer(R))
    write("gartenjahr/index.html", body)
    R = "../../"
    for m in range(1, 13):
        pk = sorted([s for s in S if m in s["peak"]], key=lambda x: x["name"])
        pr = sorted([s for s in S if m in s["present"] and m not in s["peak"]], key=lambda x: x["name"])
        pv, nx = (m - 2) % 12 + 1, m % 12 + 1
        sec_pk = (f'<section class="block" aria-labelledby="h-pk"><div class="wrap"><h2 id="h-pk">Jetzt besonders gut zu beobachten</h2><ul class="grid">{"".join(card(R, s, i, eager=i < 4) for i, s in enumerate(pk))}</ul></div></section>' if pk else "")
        sec_pr = (f'<section class="block" aria-labelledby="h-pr"><div class="wrap"><h2 id="h-pr">Außerdem unterwegs</h2><ul class="grid">{"".join(card(R, s, i) for i, s in enumerate(pr))}</ul></div></section>' if pr else "")
        body = (head(R, f"Der Garten im {MN[m-1]} · {SITE}", f"Was im {MN[m-1]} im Garten los ist: {MONTH_EVENTS[m][0]} {len(pk)} Arten haben jetzt Hauptzeit.", f"gartenjahr/{MS[m-1]}/") + nav(R, "jahr") +
                '<main id="main" tabindex="-1"> ' + crumbs(R, [("Gartenjahr", "gartenjahr/"), (MN[m-1], f"gartenjahr/{MS[m-1]}/")]) +
                f'<section class="block page"> <div class="wrap"> <h1>Der Garten im {MN[m-1]}</h1> <p class="intro">{len(pk) + len(pr)} der {len(S)} Arten sind im {MN[m-1]} aktiv, {len(pk)} davon in ihrer Hauptzeit.</p> '
                f'<ul class="evlist">{"".join(f"<li>{e(x)}</li>" for x in MONTH_EVENTS[m])}</ul> <p class="actions"><a class="btn ghost" href="{R}gartenjahr/{MS[pv-1]}/index.html">← {MN[pv-1]}</a> <a class="btn ghost" href="{R}gartenjahr/{MS[nx-1]}/index.html">{MN[nx-1]} →</a></p> </div> </section>\n'
                f'{sec_pk}{sec_pr}<section class="gearband" aria-labelledby="h-gear"><div class="wrap"><div class="head-row"><h2 id="h-gear">Passend zum {MN[m-1]}</h2></div><ul class="products">{"".join(product(R, p) for p in MONTH_PRODS[m])}</ul>{ADNOTE}</div></section> </main> ' + footer(R))
        write(f"gartenjahr/{MS[m-1]}/index.html", body)

def page_gear():
    R = "../"
    secs = "".join(f'<h2 class="h3 gear-h">{e(t)}</h2><ul class="products">{"".join(product(R, k) for k, v in PRODUCTS.items() if v[6] == sid)}</ul>' for sid, t in GEAR_SECTIONS)
    body = (head(R, f"Ausrüstung für den Naturgarten · {SITE}", "Nützlinge, Schneckenzaun, Kulturschutznetz, Nisthilfen und Becherlupe: was im naturnahen Garten wirklich hilft.", "ausruestung/") + nav(R, "gear") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Ausrüstung", "ausruestung/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Ausrüstung für den Naturgarten</h1> <p class="intro">Ein naturnaher Garten braucht vor allem Geduld und ein paar wilde Ecken. Diese Dinge helfen dir, Tiere zu beobachten, Helfer anzusiedeln und Gemüse ohne Gift zu schützen.</p> '
            f'{secs}{ADNOTE} </div> </section> </main> ' + footer(R))
    write("ausruestung/index.html", body)

def prose_page(path, title, crumb, inner, desc):
    R = "../"
    body = (head(R, f"{title} · {SITE}", desc, path) + nav(R, "") + '<main id="main" tabindex="-1"> ' + crumbs(R, [(crumb, path)]) +
            f'<section class="block page"> <div class="wrap prose"> {inner} </div> </section> </main> ' + footer(R))
    write(path + "index.html", body)

def legal_pages():
    prose_page("impressum/", "Impressum", "Impressum", f'''<h1>Impressum</h1> <h2>Angaben gemäß § 5 DDG und § 18 Abs. 1 MStV</h2> <p>Nico Schober<br>Herzogin-Cecilie-Allee 10<br>28217 Bremen<br>Deutschland</p> <h2>Kontakt</h2> <p>E-Mail: <a href="mailto:info@nicoschober.com">info@nicoschober.com</a></p> <h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2> <p>Nico Schober, Anschrift wie oben.</p> <h2>Art des Angebots</h2> <p>Der {SITE} ist ein privates Informationsangebot. Er verkauft selbst keine Waren oder Dienstleistungen. Einige Seiten enthalten gekennzeichnete Werbelinks zum Amazon-Partnerprogramm; kaufst du über einen solchen Link ein, erhält der Betreiber eine Provision. Als Amazon-Partner verdiene ich an qualifizierten Verkäufen.</p> <h2>Haftung für Inhalte</h2> <p>Die Inhalte wurden mit Sorgfalt erstellt. Für Richtigkeit, Vollständigkeit und Aktualität kann jedoch keine Gewähr übernommen werden. Angaben zu Aktivitätszeiten und Verbreitung sind grobe Richtwerte und können regional abweichen. Die Seite ersetzt keine fachliche Pflanzenschutzberatung. Hinweise zu Pflanzenschutz- und Nützlingsprodukten ersetzen nicht die Gebrauchsanleitung des Herstellers.</p> <h2>Haftung für Links</h2> <p>Diese Seite enthält Links zu externen Websites, auf deren Inhalte kein Einfluss besteht. Für diese Inhalte ist der jeweilige Anbieter verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße erkennbar. Werden Rechtsverletzungen bekannt, wird der betreffende Link umgehend entfernt.</p> <h2>Urheberrecht</h2> <p>Texte, Illustrationen, Zeichnungen und Gestaltung dieser Seite stammen vom Betreiber. Fotos Dritter stehen unter freien Lizenzen; Urheber und Lizenzen sind aufgeführt unter <a href="../bildnachweis/index.html">Bildnachweis und Lizenzen</a>.</p>''', f"Impressum des {SITE}.")
    prose_page("datenschutz/", "Datenschutz", "Datenschutz", f'''<h1>Datenschutzerklärung</h1> <p class="stand">Stand: November 2026</p> <h2>1. Verantwortlicher</h2> <p>Verantwortlich für die Datenverarbeitung auf dieser Website ist der im <a href="../impressum/index.html">Impressum</a> genannte Betreiber.</p> <h2>2. Das Wichtigste in Kürze</h2> <ul> <li>Es gibt keine Registrierung, keine Cookies, kein Tracking und keine Reichweitenmessung. Werbung gibt es nur in Form gekennzeichneter Links zu Amazon, die erst beim Anklicken eine Verbindung aufbauen.</li> <li>Die Seite speichert nichts in deinem Browser.</li> <li>Schriftarten, Bilder und Zeichnungen werden vom selben Server geladen wie die Seite selbst. Es findet keine Verbindung zu Google Fonts oder anderen Drittanbietern statt.</li> </ul> <h2>3. Hosting und Server-Protokolle</h2> <p>Diese Website wird bei statichost.eu gehostet, einem Dienst von Variable Object Assignment, c/o Knackeriet, Svartmangatan 9, 111 29 Stockholm, Schweden. Die Server stehen nach Angaben des Anbieters in der Europäischen Union; eine Übermittlung in Drittländer findet nicht statt.</p> <p>Beim Aufruf der Seite verarbeitet der Anbieter deine IP-Adresse sowie technisch notwendige Angaben zur Anfrage (abgerufene Datei, Zeitpunkt, Browser), um dir die Seite ausliefern zu können. Nach Angaben des Anbieters wird die IP-Adresse dabei nur für die Dauer der Anfrage im Arbeitsspeicher verarbeitet und nicht protokolliert. Für die Abrechnung werden technische Protokolle ohne personenbezogene Daten (vor allem die übertragene Datenmenge) höchstens sieben Tage aufbewahrt. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO; das berechtigte Interesse liegt in der zuverlässigen und sicheren Bereitstellung der Website. statichost.eu ist Auftragsverarbeiter im Sinne von Art. 28 DSGVO; der Anbieter stellt dafür einen eigenen Vertrag zur Auftragsverarbeitung bereit. Weitere Informationen: <a href="https://www.statichost.eu/privacy/" rel="noopener">Datenschutzerklärung von statichost.eu</a>.</p> <h2>4. Werbelinks zum Amazon-Partnerprogramm</h2> <p>Einige Seiten enthalten mit einem Sternchen gekennzeichnete Links zu Produkten bei Amazon.de. Der Betreiber nimmt am Partnerprogramm von Amazon Europe Core S.à r.l. teil und erhält eine Provision, wenn du über einen solchen Link einkaufst. Auf dieser Website werden dafür keine Skripte, Bilder oder Cookies von Amazon geladen. Erst wenn du einen Werbelink anklickst, wirst du zu Amazon weitergeleitet; Amazon kann dann Cookies setzen, um die Herkunft der Bestellung zuzuordnen. Einzelheiten findest du in der <a href="https://www.amazon.de/gp/help/customer/display.html?nodeId=201909010" target="_blank" rel="noopener">Datenschutzerklärung von Amazon{NEWWIN}</a>.</p> <h2>5. Externe Links</h2> <p>Die Seite verlinkt auf externe Angebote wie Wikipedia oder die Schwesterseiten Vogelkompass, Waldtierkompass und Meereskompass. Erst wenn du einen solchen Link anklickst, wird eine Verbindung zum jeweiligen Anbieter aufgebaut.</p> <h2>6. Kontakt per E-Mail</h2> <p>Wenn du mir eine E-Mail schreibst, verarbeite ich deine Adresse und den Inhalt der Nachricht, um dir zu antworten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Die Nachricht wird gelöscht, sobald dein Anliegen erledigt ist und keine gesetzlichen Aufbewahrungspflichten entgegenstehen.</p> <h2>7. Deine Rechte</h2> <p>Du hast das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21). Wende dich dafür an die im Impressum genannte Adresse. Außerdem kannst du dich bei einer Datenschutz-Aufsichtsbehörde beschweren (Art. 77 DSGVO). Für den Betreiber zuständig ist die Landesbeauftragte für Datenschutz und Informationsfreiheit der Freien Hansestadt Bremen.</p>''', f"Datenschutzerklärung des {SITE}.")
    # Bildnachweis
    keys = sorted(list(SP) + list(EXTRA), key=lambda k: NAMES[k])
    rows = []
    for k in keys:
        if k in PHOTOS:
            a, lic, lurl, src = PHOTOS[k]
            licc = f'<a href="{lurl}" target="_blank" rel="noopener license">{e(lic)}<span class="sr-only"> (Lizenztext, öffnet in neuem Fenster)</span></a>' if lurl else e(lic)
            rows.append(f'<tr id="f-{k}"><th scope="row">{e(NAMES[k])}</th><td>{e(a)}</td><td>{licc}</td><td><a href="{src}" target="_blank" rel="noopener">Quelle{NEWWIN}</a></td></tr>')
        else:
            rows.append(f'<tr id="f-{k}"><th scope="row">{e(NAMES[k])}</th><td>Gartentierkompass</td><td>eigene Illustration</td><td>–</td></tr>')
    for k in PRODUCTS:
        if k in PPHOTOS:
            a, lic, lurl, src = PPHOTOS[k]
            licc = f'<a href="{lurl}" target="_blank" rel="noopener license">{e(lic)}<span class="sr-only"> (Lizenztext, öffnet in neuem Fenster)</span></a>' if lurl else e(lic)
            rows.append(f'<tr id="p-{k}"><th scope="row">{e(PRODUCTS[k][1])} (Beispielfoto)</th><td>{e(a)}</td><td>{licc}</td><td><a href="{src}" target="_blank" rel="noopener">Quelle{NEWWIN}</a></td></tr>')
    photos_intro = ("Die Fotos stammen von Wikimedia Commons und stehen unter den genannten freien Lizenzen. Für die Seite wurden sie verkleinert und zugeschnitten. Bearbeitete Fotos unter einer Share-alike-Lizenz (BY-SA) stehen unter derselben Lizenz wie das Original. "
                    if PHOTOS else "") + "Wo noch kein Foto vorhanden ist, zeigt die Seite eine eigene, vereinfachte Illustration der Tiergruppe."
    R = "../"
    body = (head(R, f"Bildnachweis und Lizenzen · {SITE}", f"Bildnachweis, Fotolizenzen und Schriftlizenzen des {SITE}.", "bildnachweis/") + nav(R, "") + '<main id="main" tabindex="-1"> ' + crumbs(R, [("Bildnachweis", "bildnachweis/")]) +
            f'<section class="block page"> <div class="wrap prose"> <h1>Bildnachweis und Lizenzen</h1> <h2>Bilder</h2> <p>{photos_intro}</p> </div> '
            f'<div class="wrap"><div class="cmp-wrap" tabindex="0" role="region" aria-label="Bildnachweis der Tierbilder"><table class="cmp"><thead><tr><th scope="col">Art</th><th scope="col">Urheber</th><th scope="col">Lizenz</th><th scope="col">Quelle</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div> '
            '<div class="wrap prose"> <h2>Zeichnungen und Symbole</h2> <p>Logo, Schadbild-Zeichnungen, Produktsymbole und Illustrationen sind eigene Grafiken des Betreibers. Produktfotos sind Beispielbilder von Wikimedia Commons und zeigen nicht das konkrete Angebot; wo kein Foto vorhanden ist, steht ein neutrales Symbol. Das konkrete Angebot siehst du bei Amazon.</p> '
            '<h2>Schriften</h2> <p>Lora (Copyright 2011 The Lora Project Authors) und Mulish (Copyright 2016 The Mulish Project Authors) stehen unter der SIL Open Font License 1.1. Die Lizenztexte: <a href="../fonts/LICENSE-Lora.txt">Lora</a>, <a href="../fonts/LICENSE-Mulish.txt">Mulish</a>.</p> </div> </section> </main> ' + footer(R))
    write("bildnachweis/index.html", body)

def scripts():
    for f in ("app.js", "home.js"):
        s = open(f"../ref/{f}", encoding="utf-8").read()
        s = s.replace("waldjahr/", "gartenjahr/")
        wald = ('wald:{url:"https://waldtierkompass.de/",name:"Waldtierkompass",what:"Wildtiere aus dem Wald",words:["reh","hirsch","rothirsch","damhirsch","wildschwein","fuchs","rotfuchs","dachs","luchs","wolf","wildkatze","baummarder","hermelin","feldhase","hase","kaninchen","feuersalamander","salamander","kreuzotter","hirschkaefer","waldameise","fledermaus","siebenschlaefer","haselmaus","waschbaer"]},')
        s = s.replace('vogel:{url:"https://vogelkompass.de/"', wald + 'vogel:{url:"https://vogelkompass.de/"', 1)
        s = s.replace('let s=n[0]||a[0];', 'let s=[...n,...a].filter(l=>l.dataset.spot).sort((x,y)=>(x.dataset.spot-(n.includes(x)?100:0))-(y.dataset.spot-(n.includes(y)?100:0)))[0]||n[0]||a[0];')
        assert "waldtierkompass" in s
        write(f"assets/{f}", s)

def meta_files():
    idx = []
    for s in S:
        looks = " ".join(NAMES[p[2] if p[1] == s["key"] else p[1]] for p in PAIRS if s["key"] in (p[1], p[2]))
        idx.append([s["name"], s["key"], f'{s["name"]} {s["latin"]} {s["alias"]}', looks, f'{s["grp"]} {GROUP_FORMS[s["grp"]]} {ROLE[s["role"]]}|{s["short"]}|{act_text(s)}'])
    write("search.json", json.dumps(idx, ensure_ascii=False))
    urls = ["", "arten/", "ausruestung/", "bildnachweis/", "datenschutz/", "impressum/", "schadbilder/", "unterscheiden/", "gartenjahr/", "merkmale/", "groessen/", "ratgeber/schnecken/", "ratgeber/nuetzlinge/", "geschenke/", "ueber/", "links/"]
    urls += [f"merkmale/{m[0]}/" for m in MERKMALE]
    urls += [f"arten/{s['key']}/" for s in S] + [f"unterscheiden/{p[0]}/" for p in PAIRS] + [f"gartenjahr/{m}/" for m in MS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    write("site.webmanifest", json.dumps({"name": SITE, "short_name": SITE, "lang": "de", "start_url": "/", "display": "standalone", "background_color": "#f5f2e7", "theme_color": "#24412f",
           "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=1))
    write("version.txt", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))


# ================================================================ Vogelkompass-Standard: neue Seiten
ADBANNER = '<p class="adbanner"><b>Werbung:</b> Diese Seite enthält Werbelinks zu Amazon, gekennzeichnet mit einem Sternchen. Kaufst du darüber, erhalte ich eine kleine Provision, für dich ändert sich am Preis nichts.</p>'

def cred_small(k):
    return f'<small class="cred"><span>{cred_long(k, cropped=False)}</span></small>'

def mcard(R, href, imgkey, name, why, meta=""):
    return (f'<li class="mcard"><a href="{href}"> {img(R, imgkey, "(max-width: 600px) 92vw, 300px")} <span class="mname">{e(name)}</span><span class="mwhy">{e(why)}</span>'
            + (f'<span class="mmeta">{e(meta)}</span>' if meta else "") + f' </a>{cred_small(imgkey)}</li>')

def crumb_ld(trail):
    return None

def page_merkmale():
    R = "../"
    cards = []
    for slug, title, short, intro, items in MERKMALE:
        names = [SP[k]["name"] for k, _ in items]
        cards.append(mcard(R, f"{R}merkmale/{slug}/index.html", items[0][0], title, f'{len(items)} Arten, zum Beispiel {join_de(names[:2])}'))
    body = (head(R, f"Gartentiere nach Aussehen bestimmen · {SITE}", "Roter Käfer, grüne Raupe, Schnecke oder weißer Schmetterling? Gartentiere nach dem auffälligsten Merkmal bestimmen.", "merkmale/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Nach Aussehen", "merkmale/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Gartentiere nach Aussehen bestimmen</h1> <p class="intro">Du hast ein Tier im Garten entdeckt, kennst aber den Namen nicht? Wähle das auffälligste Merkmal. Auf jeder Seite findest du die passenden Arten mit Foto und dem Merkmal, an dem du sie erkennst.</p> '
            f'<ul class="mlist">{"".join(cards)}</ul> </div> </section> </main> ' + footer(R))
    write("merkmale/index.html", body)
    R = "../../"
    for slug, title, short, intro, items in MERKMALE:
        lis = "".join(mcard(R, f"{R}arten/{k}/index.html", k, SP[k]["name"], why, f'{SP[k]["size"]} · {ROLE[SP[k]["role"]]}') for k, why in items)
        ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": title, "numberOfItems": len(items),
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": SP[k]["name"], "url": f"{BASE}arten/{k}/"} for i, (k, _) in enumerate(items)]}]
        others = [m for m in MERKMALE if m[0] != slug][:6]
        ol = "".join(f'<li><a href="{R}merkmale/{m[0]}/index.html">{e(m[1])}</a></li>' for m in others)
        body = (head(R, f"{title} – was ist das? · {SITE}", intro[:155], f"merkmale/{slug}/", ld=ld, og_img=f"photos/{items[0][0]}.webp", og_alt=SP[items[0][0]]["name"]) + nav(R, "bestimmen") +
                '<main id="main" tabindex="-1"> ' + crumbs(R, [("Nach Aussehen", "merkmale/"), (title, f"merkmale/{slug}/")]) +
                f'<section class="block page"> <div class="wrap"> <h1>{e(title)}</h1> <p class="intro">{e(intro)}</p> <ul class="mlist">{lis}</ul> '
                f'<h2 class="h3 mt">Andere Merkmale</h2> <ul class="morelinks">{ol}<li><a href="{R}merkmale/index.html">Alle Merkmale</a></li></ul> </div> </section> </main> ' + footer(R))
        write(f"merkmale/{slug}/index.html", body)

def size_range(s):
    t = s["size"].replace("plus Schwanz", "").replace("Spannweite", "").replace("Gehäuse", "").replace("Raupe bis", "").strip()
    unit = 0.1 if "mm" in t else 1.0
    nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:,\d+)?", t)]
    lo, hi = (nums[0], nums[-1]) if len(nums) > 1 else (nums[0] * 0.8, nums[0])
    return lo * unit, hi * unit

def page_sizes():
    R = "../"
    import math
    lo_all, hi_all = math.log10(0.08), math.log10(160)
    pos = lambda v: (math.log10(v) - lo_all) / (hi_all - lo_all) * 100
    rows = []
    for i, s in enumerate(sorted(S, key=lambda x: -size_range(x)[1])):
        lo, hi = size_range(s)
        l, r = pos(lo), pos(hi)
        rows.append(f'<div class="srow" role="listitem"><a class="n" href="{R}arten/{s["key"]}/index.html">{e(s["name"])}</a> <div class="track"><span class="rng" style="left:{l:.2f}%;width:{max(r - l, 1.2):.2f}%;--i:{i}"><span>{e(s["size"])}</span></span></div> </div>')
    marks = "".join(f'<span style="position:absolute;left:{pos(v):.2f}%;top:0;transform:translateX(-50%);white-space:nowrap;font-size:.72rem;color:var(--muted)">{lab}</span>' for v, lab in [(0.1, "1 mm"), (1, "1 cm"), (10, "10 cm"), (50, "50 cm")])
    body = (head(R, f"Größenvergleich: wie groß sind Gartentiere? · {SITE}", "Von der winzigen Blattlaus bis zum Steinmarder: alle Gartentiere im Größenvergleich.", "groessen/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Größenvergleich", "groessen/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Wie groß ist welches Gartentier?</h1> <p class="intro">Körperlänge, bei Schmetterlingen die Flügelspannweite, bei der Weinbergschnecke das Gehäuse. Weil eine Blattlaus und ein Steinmarder so verschieden sind, wächst die Skala in Zehnerschritten: 1 mm, 1 cm, 10 cm.</p> '
            f'<p class="swipe">Seitlich wischen, um die ganze Skala zu sehen.</p> <div class="scale"><div class="scale-inner" role="list"> <div class="srow" aria-hidden="true"><span class="n"></span><div class="track" style="position:relative;height:1.2em;background:none">{marks}</div></div> {"".join(rows)} </div></div> </div> </section> </main> ' + footer(R))
    write("groessen/index.html", body)

def rlist(items, cls):
    return f'<ul class="rlist {cls}">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"

def page_ratgeber():
    for slug, d in RATGEBER.items():
        R = "../../"
        toc = "".join(f'<a href="#{sid}">{e(t)}</a>' for sid, t, *_ in d["sections"]) + '<a href="#tipps">Tipps</a><a href="#fragen">Fragen</a>'
        th = "".join(f'<th scope="col">{e(h)}</th>' for h in d["table_head"])
        trs = "".join(f'<tr><th scope="row"><a href="#{rid}">{e(name)}</a></th>' + "".join(f"<td>{e(c)}</td>" for c in cells) + "</tr>" for rid, name, cells in d["rows"])
        secs = []
        for sid, t, verdict, plus, minus, species, prods in d["sections"]:
            sp = (f'<p class="rbirds"><span>Passende Arten:</span> ' + ", ".join(f'<a href="{R}arten/{k}/index.html">{e(SP[k]["name"])}</a>' for k in species) + "</p>") if species else ""
            pr = (f'<ul class="products">{"".join(product(R, p) for p in prods)}</ul>{ADNOTE}') if prods else ""
            secs.append(f'<section class="block rtype" id="{sid}" aria-labelledby="h-{sid}"> <div class="wrap"> <h2 id="h-{sid}">{e(t)}</h2> <p class="rverdict"><b>{e(verdict)}</b></p> '
                        f'<div class="rcols"> <div><h3>Vorteile</h3>{rlist(plus, "plus")}</div> <div><h3>Nachteile</h3>{rlist(minus, "minus")}</div> </div> {sp} {pr} </div> </section>')
        tips = "".join(f"<li><b>{e(a)}</b><span>{e(x)}</span></li>" for a, x in d["tips"])
        faq = "".join(f"<dt>{e(q)}</dt><dd>{e(a)}</dd>" for q, a in d["faq"])
        rel = "".join(card(R, SP[k], i) for i, k in enumerate(d["related"]))
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": d["title"], "inLanguage": "de-DE", "author": {"@type": "Person", "name": "Nico Schober"}, "publisher": {"@id": ORG_ID}, "datePublished": "2026-11-08"},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}]
        body = (head(R, f'{d["title"]} · {SITE}', d["desc"], f"ratgeber/{slug}/", "article", ld=ld) + nav(R, "garten") +
                '<main id="main" tabindex="-1"> ' + crumbs(R, [("Im Garten", "ratgeber/nuetzlinge/") if slug != "nuetzlinge" else ("Ratgeber", "ratgeber/nuetzlinge/"), (d["nav"], f"ratgeber/{slug}/")] if slug != "nuetzlinge" else [(d["nav"], f"ratgeber/{slug}/")]) +
                f'<section class="block page"> <div class="wrap"> <h1>{e(d["title"])}</h1> <p class="intro">{e(d["intro"])}</p> {ADBANNER} <p>{d["short"]}</p> <nav class="toc" aria-label="Auf dieser Seite">{toc}</nav> </div> </section> '
                f'<section class="block" id="vergleich" aria-labelledby="h-vgl"> <div class="wrap"> <h2 id="h-vgl">Im Vergleich</h2> <div class="cmp-wrap" tabindex="0" role="region" aria-label="Vergleichstabelle, seitlich scrollbar"><table class="cmp"> <thead><tr><td></td>{th}</tr></thead> <tbody>{trs}</tbody> </table></div> <p class="thumbnote">Preise sind grobe Richtwerte, Stand November 2026.</p> </div> </section> '
                + "".join(secs) +
                f'<section class="block" id="tipps" aria-labelledby="h-tipps"> <div class="wrap"> <h2 id="h-tipps">{e(d["tips_title"])}</h2> <ul class="tips">{tips}</ul> </div> </section> '
                f'<section class="block" id="fragen" aria-labelledby="h-faq"> <div class="wrap"> <h2 id="h-faq">Häufige Fragen</h2> <dl class="faq">{faq}</dl> </div> </section> '
                f'<section class="block related" aria-labelledby="h-rel"> <div class="wrap"> <h2 id="h-rel">Passende Arten</h2> <ul class="grid">{rel}</ul> </div> </section> </main> ' + footer(R))
        write(f"ratgeber/{slug}/index.html", body)

def page_gifts():
    R = "../"
    toc = "".join(f'<a href="#{sid}">{e(t)}</a>' for sid, t, _, _ in GESCHENKE) + '<a href="#ohne">Ohne Kaufen</a>'
    secs = "".join(f'<section class="block" id="{sid}" aria-labelledby="h-{sid}"><div class="wrap"><h2 id="h-{sid}">{e(t)}</h2> <p class="intro">{e(txt)}</p> <ul class="products">{"".join(product(R, p) for p in prods)}</ul>{ADNOTE}</div></section> ' for sid, t, txt, prods in GESCHENKE)
    ohne = "".join(f"<li><b>{e(a)}</b>: {e(x)}</li>" for a, x in GESCHENKE_OHNE)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": "Geschenke für Gartenfreunde", "inLanguage": "de-DE", "description": "Geschenkideen für Naturgärtner, Kinder und Technikfreunde."}]
    body = (head(R, f"Geschenke für Gartenfreunde und Naturgärtner · {SITE}", "Geschenkideen für Gartenfreunde: Nisthilfe, Igelhaus, Hochbeet, Becherlupe und Wildkamera, für Einsteiger, Kinder und Naturgärtner.", "geschenke/", ld=ld) + nav(R, "garten") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Ausrüstung", "ausruestung/"), ("Geschenke", "geschenke/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Geschenke für Gartenfreunde</h1> <p class="intro">Wer gern im Garten ist, freut sich über Dinge, die wirklich benutzt werden: eine Nisthilfe, in die im Frühling Wildbienen einziehen, ein Igelhaus für den Winter oder eine Lupe, mit der jeder Käfer spannend wird. Hier findest du Ideen für jeden Kenntnisstand.</p> '
            f'{ADBANNER} <nav class="toc" aria-label="Auf dieser Seite">{toc}</nav> </div> </section> {secs}'
            f'<section class="block" aria-labelledby="h-ohne" id="ohne"> <div class="wrap"> <h2 id="h-ohne">Geschenke ohne Kaufen</h2> <div class="advice"> <ul>{ohne}</ul> </div> </div> </section> </main> ' + footer(R))
    write("geschenke/index.html", body)

def page_about():
    n_pairs = len(PAIRS)
    sis = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{e(t.split(":")[0])}{NEWWIN}</a>: {e(t.split(": ", 1)[1])}</li>' for u, t in SISTERS)
    inner = (f'<h1>Über den {SITE}</h1> <p class="intro">Der {SITE} hilft dir, die Tiere zu erkennen, die in deinem Garten leben: Nützlinge, Bestäuber, Schädlinge und Gäste wie Igel oder Erdkröte. Er zeigt {len(S)} typische Arten mit Foto und Merkmalen, erklärt in {n_pairs} Vergleichen die häufigsten Verwechslungen und führt vom Schadbild zum Verursacher.</p> '
             f'<h2>Wer den {SITE} macht</h2> <p>Den {SITE} betreibt Nico Schober aus Bremen als privates, unabhängiges Angebot. Texte, Auswahl der Arten und Gestaltung stammen von ihm. Die Seite gehört zu keinem Verband und keinem Hersteller. Die Kontaktdaten stehen im <a href="../impressum/index.html">Impressum</a>.</p> '
             '<h2>Woher die Inhalte stammen</h2> <ul> <li><b>Steckbriefe:</b> Merkmale, Größe, Nahrung und Lebensweise sind mit gängigen Bestimmungsliteratur und der deutschsprachigen Wikipedia abgeglichen. Jede Artseite verlinkt weiterführende Quellen unter „Mehr erfahren“.</li> '
             '<li><b>Jahreszeiten:</b> Die Angaben, wann eine Art zu sehen ist, sind grobe Richtwerte für Deutschland. Je nach Region und Wetter weichen sie ab.</li> '
             '<li><b>Fotos:</b> von Wikimedia Commons, unter freien Lizenzen, mit Namen der Fotografinnen und Fotografen an jedem Bild.</li> </ul> '
             '<p>Alle Urheber und Lizenzen stehen gesammelt unter <a href="../bildnachweis/index.html">Bildnachweis und Lizenzen</a>.</p> '
             f'<h2>Wie sich die Seite finanziert</h2> <p>Der {SITE} ist kostenlos und ohne Anmeldung nutzbar. Einige Seiten empfehlen Nisthilfen, Schneckenzäune oder Bücher mit Werbelinks zu Amazon, die mit * gekennzeichnet sind. Kaufst du über einen solchen Link, erhält der Betreiber eine kleine Provision, für dich ändert sich am Preis nichts. Die Empfehlungen sind nicht selbst getestet, wenn es nicht ausdrücklich dabeisteht, und Hersteller haben keinen Einfluss auf die Auswahl.</p> '
             f'<h2>Deine Daten</h2> <p>Der {SITE} setzt keine Tracking-Cookies und speichert nichts in deinem Browser. Mehr dazu in der <a href="../datenschutz/index.html">Datenschutzerklärung</a>.</p> '
             '<h2>Fehler gefunden?</h2> <p>Wenn dir eine falsche Angabe oder ein falsch zugeordnetes Foto auffällt, schreib gern an <a href="mailto:info@nicoschober.com">info@nicoschober.com</a>. Hinweise werden geprüft und eingearbeitet.</p> '
             f'<h2>Schwesterseiten</h2> <ul>{sis}</ul>')
    prose_page("ueber/", f"Über den {SITE}", "Über", inner, f"Wer den {SITE} macht, woher die Inhalte stammen und wie sich die Seite finanziert.")

def page_links():
    groups = "".join(f'<div class="lg"><h2 class="h3">{e(t)}</h2><ul class="weblist">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{e(n)}{NEWWIN}</a><span>{e(d)}</span></li>' for u, n, d in items) + "</ul></div>" for t, items in LINKS)
    R = "../"
    body = (head(R, f"Weiterführende Websites · {SITE}", "Seriöse Anlaufstellen zum Bestimmen von Gartentieren, für naturnahes Gärtnern und zum Mitmachen.", "links/") + nav(R, "") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Links", "links/")]) +
            f'<section class="block page legal"> <div class="wrap"> <h1>Weiterführende Websites</h1> <p class="intro">Seriöse Anlaufstellen zum Bestimmen, Mitmachen und Weiterlesen. Alle Links öffnen sich in einem neuen Fenster.</p> <div class="linkgroups">{groups}</div> </div> </section> </main> ' + footer(R))
    write("links/index.html", body)

if __name__ == "__main__":
    scripts()
    for s in S:
        page_species(s)
    page_home(); page_arten(); page_pairs(); page_damage(); page_year(); page_gear(); legal_pages()
    page_merkmale(); page_sizes(); page_ratgeber(); page_gifts(); page_about(); page_links(); meta_files()
    print("fertig")
