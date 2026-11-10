"""Im Garten: Gartenjahr, Ausrüstung, Ratgeber, Geschenke, Insektensommer."""
import json, math, os, re
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *
from gtk.components import *

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

def page_ratgeber():
    for slug, d in RATGEBER.items():
        R = "../../"
        toc = "".join(f'<a href="#{sid}">{e(t)}</a>' for sid, t, *_ in d["sections"]) + '<a href="#tipps">Tipps</a><a href="#fragen">Fragen</a>'
        th = "".join(f'<th scope="col">{e(h)}</th>' for h in d["table_head"])
        trs = "".join(f'<tr><th scope="row"><a href="#{rid}">{e(name)}</a></th>' + "".join(f"<td>{e(c)}</td>" for c in cells) + "</tr>" for rid, name, cells in d["rows"])
        secs = []
        for sid, t, verdict, plus, minus, species, prods in d["sections"]:
            sp = ('<p class="rbirds"><span>Passende Arten:</span> ' + ", ".join(f'<a href="{R}arten/{k}/index.html">{e(SP[k]["name"])}</a>' for k in species) + "</p>") if species else ""
            pr = (f'<ul class="products">{"".join(product(R, p, guide=False) for p in prods)}</ul>{ADNOTE}') if prods else ""
            secs.append(f'<section class="block rtype" id="{sid}" aria-labelledby="h-{sid}"> <div class="wrap"> <h2 id="h-{sid}">{e(t)}</h2> <p class="rverdict"><b>{e(verdict)}</b></p> '
                        f'<div class="rcols"> <div><h3>Vorteile</h3>{rlist(plus, "plus")}</div> <div><h3>Nachteile</h3>{rlist(minus, "minus")}</div> </div> {sp} {pr} </div> </section>')
        tips = "".join(f"<li><b>{e(a)}</b><span>{e(x)}</span></li>" for a, x in d["tips"])
        faq = "".join(f'<details class="fold faqi" open data-fold><summary><h3>{e(q)}</h3></summary><p>{e(a)}</p></details>' for q, a in d["faq"])
        rel = "".join(card(R, SP[k], i) for i, k in enumerate(d["related"]))
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": d["title"], "inLanguage": "de-DE", "author": {"@type": "Person", "name": "Nico Schober"}, "publisher": {"@id": ORG_ID}, "datePublished": "2026-11-08", "dateModified": STAND_ISO},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}]
        body = (head(R, f'{d["title"]} · {SITE}', d["desc"], f"ratgeber/{slug}/", "article", ld=ld) + nav(R, "garten") +
                '<main id="main" tabindex="-1"> ' + crumbs(R, [("Im Garten", "ratgeber/nuetzlinge/") if slug != "nuetzlinge" else ("Ratgeber", "ratgeber/nuetzlinge/"), (d["nav"], f"ratgeber/{slug}/")] if slug != "nuetzlinge" else [(d["nav"], f"ratgeber/{slug}/")]) +
                f'<section class="block page"> <div class="wrap"> <h1>{e(d["title"])}</h1> <p class="intro">{e(d["intro"])}</p> {ADBANNER} <p>{d["short"]}</p> <nav class="toc" aria-label="Auf dieser Seite">{toc}</nav> </div> </section> '
                f'<section class="block" id="vergleich" aria-labelledby="h-vgl"> <div class="wrap"> <h2 id="h-vgl">Im Vergleich</h2> <div class="cmp-wrap" tabindex="0" role="region" aria-label="Vergleichstabelle, seitlich scrollbar"><table class="cmp"> <thead><tr><td></td>{th}</tr></thead> <tbody>{trs}</tbody> </table></div> <p class="thumbnote">Preise sind grobe Richtwerte, Stand November 2026.</p> </div> </section> '
                + "".join(secs) +
                f'<section class="block" id="tipps" aria-labelledby="h-tipps"> <div class="wrap"> <h2 id="h-tipps">{e(d["tips_title"])}</h2> <ul class="tips">{tips}</ul> </div> </section> '
                f'<section class="block" id="fragen" aria-labelledby="h-faq"> <div class="wrap"> <h2 id="h-faq">Häufige Fragen</h2> <div class="faq">{faq}</div> <p class="stand">Von <a href="{R}ueber/index.html" rel="author">Nico Schober</a> · Stand: {STAND_DE}</p> </div> </section> '
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

def page_insektensommer():
    R = "../"
    sp = [SP[k] for k in IS_KEYS]
    cards = "".join(mcard(R, f"{R}arten/{s['key']}/index.html", s["key"], s["name"], s["marks"][0], f'{s["size"]} · {ROLE[s["role"]]}') for s in sp)
    tips = "".join(f"<li><b>{e(a)}</b><span>{e(x)}</span></li>" for a, x in IS_TIPS)
    prods = ["becherlupe", "makroclip", "buch"]
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "Insekten für den Insektensommer", "numberOfItems": len(sp),
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["name"], "url": f"{BASE}arten/{s['key']}/"} for i, s in enumerate(sp)]}]
    body = (head(R, f"Insektensommer: Insekten im Garten zählen · {SITE}", "Beim NABU-Insektensommer im Juni und August Insekten zählen: die häufigsten Arten im Garten mit Foto, Zähltipps und Zählkarte zum Ausdrucken.", "insektensommer/", ld=ld, og_img="photos/erdhummel.webp", og_alt="Erdhummel") + nav(R, "garten") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Insektensommer", "insektensommer/")]) +
            f'<section class="block page"> <div class="wrap is-head"> <div> <p class="season">Im Juni und im August</p> <h1>Insektensommer: Insekten im Garten zählen</h1> '
            f'<p class="intro">Beim Insektensommer zählen jedes Jahr tausende Menschen eine Stunde lang Insekten und melden sie dem NABU. Mitmachen kann jede und jeder, im Garten, auf dem Balkon oder im Park. Hier findest du die {len(sp)} Insekten, die du im Garten am häufigsten siehst, und eine Zählkarte zum Ausdrucken.</p> '
            '<p class="isdate">Gezählt wird in zwei Zeiträumen von jeweils rund zehn Tagen, meist Anfang Juni und Anfang August. Die genauen Termine nennt der NABU auf <a href="https://www.insektensommer.de/" target="_blank" rel="noopener">insektensommer.de' + NEWWIN + '</a>.</p> '
            f'<p class="wlinks"><a class="btn" href="{R}downloads/zaehlkarte-insektensommer.pdf" download>Zählkarte als PDF (A4)</a> <a class="btn ghost" href="#arten">Arten ansehen</a></p> </div> '
            f'<figure class="is-fig"> {img(R, "erdhummel", "(max-width: 760px) 92vw, 480px", eager=True, alt="Erdhummel auf einer Blüte")} <figcaption>{cred_long("erdhummel")}</figcaption> </figure> </div> </section> '
            f'<section class="block" id="arten" aria-labelledby="h-arten"> <div class="wrap"> <h2 id="h-arten">Diese Insekten siehst du im Garten oft</h2> <p class="intro">Die Auswahl zeigt häufige Gartenarten. Gemeldet werden darf jedes Insekt, das du entdeckst. Spinnen, Schnecken und Regenwürmer sind keine Insekten und zählen nicht mit.</p> <ul class="mlist">{cards}</ul> </div> </section> '
            f'<section class="block" id="zaehlen" aria-labelledby="h-zaehlen"> <div class="wrap"> <h2 id="h-zaehlen">So zählst du richtig</h2> <ul class="tips">{tips}</ul> '
            f'<p class="printcard"><a class="btn" href="{R}downloads/zaehlkarte-insektensommer.pdf" download>Zählkarte zum Ausdrucken (PDF, A4)</a> <span>Die Karte zeigt alle {len(sp)} Arten mit Erkennungsmerkmal und einem Feld für die Anzahl. Sie ist ein Angebot des {SITE} und nicht die offizielle Zählhilfe des NABU.</span></p> </div> </section> '
            f'<section class="block" aria-labelledby="h-gear"> <div class="wrap"> <h2 id="h-gear">Hilfreich beim Zählen</h2> <ul class="products">{"".join(product(R, p) for p in prods)}</ul>{ADNOTE} </div> </section> '
            f'<section class="block" aria-labelledby="h-mehr"> <div class="wrap"> <h2 id="h-mehr">Mehr Insekten im Garten</h2> <ul class="explore"> '
            f'<li><a href="{R}ratgeber/nuetzlinge/index.html"><b>Nützlinge fördern</b><span>Wildbienenhotel, Totholz und heimische Blumen holen Insekten in den Garten.</span></a></li>'
            f'<li><a href="{R}merkmale/gelb-schwarz-gestreift/index.html"><b>Gelb-schwarz gestreift?</b><span>Hummel, Biene, Schwebfliege oder Wespe sicher unterscheiden.</span></a></li>'
            f'<li><a href="{R}unterscheiden/hainschwebfliege-oder-wespe/index.html"><b>Schwebfliege oder Wespe?</b><span>Die wichtigsten Unterschiede auf einen Blick.</span></a></li> </ul> </div> </section> </main> ' + footer(R))
    write("insektensommer/index.html", body)
