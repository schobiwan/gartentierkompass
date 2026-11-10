"""Startseite und Artenliste."""
import json, math, os, re
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *
from gtk.components import *

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
    nowsp = [s for s in S if NOW in s["peak"]] + [s for s in S if NOW in s["present"] and NOW not in s["peak"]]
    pool = [s for s in nowsp if s["key"] in SPOT]
    spot = min(pool, key=lambda s: SPOT.index(s["key"]) + (0 if NOW in s["peak"] else 100)) if pool else (nowsp[0] if nowsp else S[0])
    order = sorted(nowsp, key=lambda s: POPRANK[s["key"]]) + [s for s in S if s not in nowsp]
    ncards = "".join(
        f'<li{spot_attr(s)} data-peak="{",".join(map(str, s["peak"]))}" data-present="{",".join(map(str, s["present"]))}" data-k="{s["key"]}" data-pop="{POPRANK[s["key"]]}" data-name="{e(s["name"])}" data-hl="{e(s["hl"])}"{"" if (s in nowsp and s is not spot) else " hidden"}>'
        f'<a href="arten/{s["key"]}/index.html"><img src="photos/{s["key"]}-400.webp" alt="" width="400" height="300" loading="{"eager" if i < 5 else "lazy"}" decoding="async"><span class="nc-ov"><b>{e(s["name"])}</b><i>Hauptzeit</i></span></a>{cred_pop(cred_short(R, s["key"]))}</li>'
        for i, s in enumerate(order))
    grid = "".join(card(R, s, i, eager=i < 4) for i, s in enumerate(sorted(S, key=lambda x: (NOW not in x["present"], POPRANK[x["key"]]))))
    empty_groups = "".join(f'<button type="button" class="chip" data-sgrp="{e(g)}">{e(g)}</button>' for g, _, _ in GROUPS)
    explore = (f'<li><a href="schadbilder/index.html"><b>Was frisst an meiner Pflanze?</b><span>Löcher, Buchten, Gespinste und Hügel: vom Schadbild zum Verursacher, mit sanften Lösungen.</span></a></li>'
               f'<li><a href="unterscheiden/index.html"><b>Doppelgänger unterscheiden</b><span>Marienkäfer oder Asiatischer Marienkäfer, Schwebfliege oder Wespe: {len(PAIRS)} Vergleiche.</span></a></li>'
               f'<li><a href="gartenjahr/index.html"><b>Das Gartenjahr</b><span>Krötenwanderung, Schneckenzeit, Leimring: was im Garten wann passiert, Monat für Monat.</span></a></li>'
               f'<li><a href="merkmale/index.html"><b>Nach Aussehen bestimmen</b><span>Roter Käfer, grüne Raupe, weißer Schmetterling: {len(MERKMALE)} Merkmale führen zur Art.</span></a></li>'
               f'<li><a href="ratgeber/nuetzlinge/index.html"><b>Nützlinge fördern</b><span>Wildbienenhotel, Igelhaus, Totholz und Teich: so holst du Helfer in den Garten.</span></a></li>'
               f'<li><a href="ratgeber/schnecken/index.html"><b>Schnecken ohne Gift</b><span>Schneckenzaun, Absammeln, Nematoden und Laufenten im Vergleich.</span></a></li>'
               f'<li><a href="insektensommer/index.html"><b>Insektensommer</b><span>Im Juni und August Insekten zählen: die häufigsten Arten und eine Zählkarte zum Ausdrucken.</span></a></li>'
               f'<li><a href="groessen/index.html"><b>Größenvergleich</b><span>Von der Blattlaus bis zum Steinmarder auf einer Skala.</span></a></li>'
               f'<li><a href="ausruestung/index.html"><b>Ausrüstung</b><span>Nützlinge, Schneckenzaun, Nisthilfen und Lupe für einen naturnahen Garten.</span></a></li>'
               f'<li><a href="https://vogelkompass.de/" rel="noopener"><b>Vögel im Garten?</b><span>Meise, Rotkehlchen und Co. findest du auf der Schwesterseite Vogelkompass.</span></a></li>'
               f'<li><a href="https://waldtierkompass.de/" rel="noopener"><b>Fuchs, Reh oder Dachs?</b><span>Größere Wildtiere und ihre Spuren findest du auf der Schwesterseite Waldtierkompass.</span></a></li>')
    body = (head(R, f"{SITE} – Tiere im Garten bestimmen", desc, "", ld=ld) + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> <header class="hero6"> <div class="wrap hero6-in"> <div class="h6-text"> '
            f'<p class="h6-kicker"><svg class="buoy" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V11" stroke="#4a6a4c" stroke-width="1.8" stroke-linecap="round"/><path d="M12 11c0-3 2.5-5.5 6-5.5 0 3.5-2.5 5.5-6 5.5z" fill="#6b9a3c"/><path d="M12 14c0-2.6-2-4.5-5-4.5 0 3 2 4.5 5 4.5z" fill="#8fbf55"/></svg><span>Naturgarten</span><span aria-hidden="true">·</span><span>{len(S)} Gartentiere</span></p> '
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
