"""Startseite und Artenliste."""

import math
from data.more import HOME_GEAR, PAIRS
from data.species import GROUPS, HABS, S
from data.vk import MERKMALE
from gtk.components import GENERIC_GEAR, card, cred_pop, cred_short, gearband, product
from gtk.config import AUTHOR, ACT, BASE, MN, NOW, ORG_ID, PHOTOS, PLATE, POPRANK, SITE, SIZES, SP, SPOT
from gtk.layout import ADNOTE, crumbs, footer, head, nav, SEARCH_ICO
from gtk.util import e, fit_title, write

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
        l = f'<a href="{lurl}" target="_blank" rel="noopener license">{e(lic)}<span class="sr-only"> (Lizenztext, öffnet in neuem Fenster)</span></a>' if lurl else e(lic)
        return f'Foto: <a href="{src}" target="_blank" rel="noopener">{e(a)}<span class="sr-only"> (Quelle, öffnet in neuem Fenster)</span></a>, {l}'
    return "Illustration"

def size_plate():
    """Größentafel: ausgewählte Arten mit logarithmischem Balken (0,1 cm bis 1 m)."""
    rows = "".join(
        f'<li><a href="arten/{k}/index.html"><b>{e(SP[k]["name"])}</b><span class="pbar" aria-hidden="true"><i style="--w:{max(4, round((math.log10(SP[k]["mid"]) + 1) / 3 * 100))}%"></i></span>'
        f'<span class="psz">{e(SP[k]["size"].replace(" plus Schwanz", ""))}</span></a></li>' for k in PLATE)
    return ('<section class="plate" aria-labelledby="plate-h"> <div class="wrap"> <div class="plate-head"><h2 id="plate-h">Größentafel</h2>'
            '<p>Von der Bohnenlaus bis zum Fuchs: so groß sind Gartentiere wirklich.</p><a href="groessen/index.html">Größenvergleich ansehen</a></div> '
            f'<ol>{rows}</ol> <p class="pscale">Die Balken wachsen logarithmisch, sonst wäre die Bohnenlaus neben dem Fuchs unsichtbar.</p> </div> </section>')

def page_home():
    R = ""
    desc = f"Gartentiere bestimmen: {len(S)} Nützlinge, Schädlinge und Gartengäste mit Merkmalen, Schadbildern, Doppelgängern und Gartenjahr."
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "#website", "name": SITE, "url": BASE, "inLanguage": "de-DE", "publisher": {"@id": ORG_ID}, "description": "Tiere im Garten bestimmen: Nützlinge, Schädlinge, Schadbilder und Gartenjahr.",
           "potentialAction": {"@type": "SearchAction", "target": BASE + "?q={search_term_string}", "query-input": "required name=search_term_string"}},
          {"@context": "https://schema.org", "@type": "Organization", "@id": ORG_ID, "name": SITE, "url": BASE, "logo": BASE + "icon-512.png", "email": "info@nicoschober.com", "founder": AUTHOR}]
    chips = "".join(f'<button type="button" class="hchip" data-hgrp="{e(g)}">{e(g)} <span class="hn">{sum(1 for s in S if s["grp"] == g)}</span></button>' for g, _, _ in GROUPS)
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
               f'<li><a href="https://waldtierkompass.de/" rel="noopener"><b>Reh, Dachs oder Wildschwein?</b><span>Größere Wildtiere und ihre Spuren findest du auf der Schwesterseite Waldtierkompass.</span></a></li>')
    body = (head(R, f"{SITE} – Tiere im Garten bestimmen", desc, "", ld=ld) + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> <header class="hero6"> <div class="wrap hero6-in"> <div class="h6-text"> '
            f'<p class="h6-kicker">{len(S)} Tiere aus deutschen Gärten, mit Foto und Größe</p> '
            '<h1 class="h6-title h6-single">Wer lebt in deinem Garten?</h1> '
            '<p class="lede">Nützlinge, Bestäuber und Schädlinge im Garten bestimmen: am Foto, an den Fraßspuren und an wenigen sicheren Merkmalen.</p> '
            f'<form class="hsearch" id="hsearch" role="search" aria-label="Tier suchen"> <label for="hq"><span class="sr-only">Tier suchen</span>{SEARCH_ICO}<input type="search" id="hq" placeholder="Name oder Aussehen, z. B. Marienkäfer" autocomplete="off" enterkeyhint="search"></label> <button class="hsearch-btn" type="submit">Suchen</button> </form> '
            f'<div class="hchips" role="group" aria-label="Nach Gruppe zeigen">{chips}<a class="hchip hchip-all" href="arten/index.html">Alle Gruppen</a></div> </div> '
            f'<figure class="spot6" id="spot"> <a href="arten/{spot["key"]}/index.html" id="spot-link" class="s6-link"><span class="s6-photo"><img id="spot-img" src="photos/{spot["key"]}.webp" srcset="photos/{spot["key"]}-400.webp 400w, photos/{spot["key"]}.webp 720w" sizes="(max-width: 900px) 92vw, 480px" alt="" width="720" height="576" fetchpriority="high"></span> '
            f'<span class="s6-label"><span class="spot-tag">Jetzt zu sehen · <span data-now-name>{MN[NOW-1]}</span></span><b id="spot-name">{e(spot["name"])}</b><span id="spot-hl">{e(spot["hl"])}</span></span></a> '
            f'<small class="spot-cred" id="spot-cred">{spot_cred(spot["key"])}</small> </figure> </div> '
            ' </header>\n' + size_plate() + '\n'
            f'<section class="nowband" aria-labelledby="now-h"> <div class="wrap"> <div class="now-head"><h2 id="now-h">Jetzt im <span data-now-name>{MN[NOW-1]}</span> im Garten</h2><div class="now-nav"><a href="gartenjahr/index.html" data-now-link>Alle im <span data-now-name>{MN[NOW-1]}</span></a>'
            '<button class="cbtn" type="button" id="now-prev" aria-controls="nowcards" aria-label="Vorherige Tiere" disabled><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 6-6 6 6 6"/></svg></button><button class="cbtn" type="button" id="now-next" aria-controls="nowcards" aria-label="Weitere Tiere"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 6 6 6-6 6"/></svg></button></div></div> '
            f'<ul class="nowcards" id="nowcards">{ncards}</ul> </div> </section>\n' + filter_bar() + '\n'
            '<section class="sub" aria-labelledby="arten-h"> <div class="wrap"> <h2 class="sr-only" id="arten-h">Arten</h2> <p class="actlegend" aria-hidden="true"><span><svg aria-hidden="true"><use href="#i-sun"></use></svg> tagaktiv</span><span><svg aria-hidden="true"><use href="#i-dusk"></use></svg> dämmerungsaktiv</span><span><svg aria-hidden="true"><use href="#i-moon"></use></svg> nachtaktiv</span></p> '
            f'<ul class="grid" id="grid"> {grid} </ul> <div class="empty" id="empty" hidden><p id="empty-msg">Kein Tier passt zu deiner Suche oder Auswahl.</p><p id="empty-suggest" hidden></p><div class="empty-groups" aria-label="Stattdessen eine Gruppe ansehen">{empty_groups}</div><button class="btn ghost" type="button" id="empty-reset">Suche und Filter zurücksetzen</button></div> </div> </section>\n'
            f'<section class="gearband" aria-labelledby="h-gear"><div class="wrap"><div class="head-row"><h2 id="h-gear">Gut ausgerüstet für den Naturgarten</h2><a class="gearmore" href="ausruestung/index.html">Alle Ausrüstungstipps ansehen</a></div><ul class="products">{"".join(product(R, p) for p in HOME_GEAR)}</ul>{ADNOTE}</div></section>\n'
            f'<section class="block"> <div class="wrap"> <h2>Weiter entdecken</h2> <ul class="explore"> {explore} </ul> </div> </section> </main> ' + footer(R, "home.js"))
    write("index.html", body)

def page_arten():
    R = "../"
    parts = []
    for g, slug, d in GROUPS:
        lst = sorted([s for s in S if s["grp"] == g], key=lambda x: x["name"])
        parts.append(f'<h2 class="h3 grp-h" id="g-{slug}">{e(g)}</h2><ul class="grid">{"".join(card(R, s, i, eager=(g == GROUPS[0][0] and i < 4)) for i, s in enumerate(lst))}</ul>')
    body = (head(R, fit_title(f"Alle Gartentiere von A bis Z: {len(S)} Steckbriefe"), f"Alle {len(S)} Gartentiere im Überblick: Nützlinge, Bestäuber, Schädlinge, Säugetiere, Amphibien, Reptilien und Krabbeltiere, jeweils mit Foto und Merkmalen.", "arten/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Arten", "arten/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Alle Gartentiere</h1> <p class="actlegend" aria-hidden="true"><span><svg aria-hidden="true"><use href="#i-sun"></use></svg> tagaktiv</span><span><svg aria-hidden="true"><use href="#i-dusk"></use></svg> dämmerungsaktiv</span><span><svg aria-hidden="true"><use href="#i-moon"></use></svg> nachtaktiv</span></p> '
            f'<p class="intro">{len(S)} Arten, nach Gruppen geordnet. Zum Suchen und Filtern geht es zur <a href="../index.html#arten">Startseite</a>.</p> {"".join(parts)} </div> </section> ' + gearband(R, "Zum Beobachten und Bestimmen", GENERIC_GEAR) + '</main> ' + footer(R))
    write("arten/index.html", body)
