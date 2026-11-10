"""Artseiten (Steckbriefe)."""
import json, math, os, re
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *
from gtk.components import *

def merkmal_links_for(k):
    return [(slug, short) for slug, title, short, intro, items in MERKMALE if any(x == k for x, _ in items)]

def related_for(s):
    same = [x for x in S if x["grp"] == s["grp"] and x["key"] != s["key"]]
    hab = set(s["hab"])
    same.sort(key=lambda x: (-len(hab & set(x["hab"])), x["name"]))
    return same[:4]

def tldr(s):
    p = sorted(s["present"])
    if len(p) == 12: rng = "Ganzjährig"
    elif p == list(range(p[0], p[-1] + 1)): rng = f"Von {MN[p[0]-1]} bis {MN[p[-1]-1]}"
    else: rng = "Im " + join_de(MN[m-1] for m in p)
    best = join_de(MN[m-1] for m in s["peak"])
    return (f'<section class="tldr" aria-labelledby="h-tldr"><h2 id="h-tldr">Kurz gesagt</h2><dl>'
            f'<dt>Zu sehen</dt><dd>{e(rng)}, am besten im {e(best)}</dd>'
            f'<dt>Wo im Garten</dt><dd>{e(s["where"])}</dd>'
            f'<dt>Größe</dt><dd>{e(s["size"])}</dd>'
            f'<dt>Aktiv</dt><dd>{act_text(s)}</dd>'
            f'<dt>Rolle</dt><dd>{e(ROLE[s["role"]])}: {e(s["roleline"])}</dd></dl></section>')

def pager(R, s):
    al = sorted(S, key=lambda x: x["name"]); i = al.index(s)
    pv, nx = al[i - 1], al[(i + 1) % len(al)]
    return (f'<nav class="pager" aria-label="Weitere Arten"> <a rel="prev" href="{R}arten/{pv["key"]}/index.html"><span>Vorherige Art</span><b>{e(pv["name"])}</b></a> '
            f'<a rel="next" href="{R}arten/{nx["key"]}/index.html"><span>Nächste Art</span><b>{e(nx["name"])}</b></a> </nav>')

def page_species(s):
    R = "../../"; k = s["key"]
    nom, akk, dat = ART[s["pron"]]
    N = s["name"]
    desc = f'{N} sicher erkennen: {s["short"]} Mit Merkmalen, Rolle im Garten und Jahreszeiten.'
    if len(desc) > 158: desc = desc[:155].rsplit(" ", 1)[0].rstrip(",.:;") + " …"
    has_pair = any(k in (p[1], p[2]) for p in PAIRS)
    title = f'{N}: Merkmale, Rolle im Garten und Doppelgänger' if has_pair else f'{N} erkennen: Merkmale und Rolle im Garten'
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
    inmerk = ('<p class="inmerk">Auch zu finden unter: ' + " · ".join(f'<a href="{R}merkmale/{slug}/index.html">{e(short)}</a>' for slug, short in ml) + '</p>') if ml else ""
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
           "isPartOf": {"@id": BASE + "#website"}, "publisher": {"@id": ORG_ID}, "author": {"@type": "Person", "name": "Nico Schober", "url": BASE + "ueber/"}, "datePublished": "2026-11-07", "dateModified": STAND_ISO,
           "about": {"@type": "Taxon", "name": s["latin"], "alternateName": N, "taxonRank": "species"},
           "image": f'{BASE}photos/{k}.webp', "primaryImageOfPage": {"@type": "ImageObject", "url": f'{BASE}photos/{k}.webp', "width": 720, "height": 576}}]
    body = (head(R, title, desc, f'arten/{k}/', "article", og_img=f'photos/{k}.webp', og_alt=N, ld=ld)
            + nav(R, "bestimmen") + '<main id="main" tabindex="-1"> ' + crumbs(R, [("Arten", "arten/"), (N, f"arten/{k}/")]) +
            f'<article class="sp wrap"> <div class="sp-top"> <figure class="sp-photo"> {img(R, k, "(max-width: 760px) 92vw, 560px", eager=True, alt=N if k in PHOTOS else "")} <figcaption>{cred_long(k)}</figcaption> </figure> '
            f'<div class="sp-intro"> <h1>{e(N)}</h1> <p class="latin" lang="la">{e(s["latin"])}</p> <p class="row">{role_badge(s)}{grp_tag(s)}<span class="tag">{e(s["size"])}</span>'
            + "".join(f'<span class="tag act-tag"><svg aria-hidden="true"><use href="#{ACT[a][1]}"></use></svg>{ACT[a][0]}</span>' for a in s["acts"]) +
            f'</p> <p class="habs">{"".join(f"<span>{e(h)}</span>" for h in s["hab"])}</p> <p class="text">{e(s["short"])} {e(s["hl"])}</p> '
            f'</div> </div>\n'
            f'<div class="sp-cols"> <aside class="sp-side" aria-label="Auf einen Blick"> {tldr(s)} </aside> <div class="sp-main"> <section aria-labelledby="h-marks"> <h2 id="h-marks">So erkennst du {akk} {e(N)}</h2> <ul class="marks">{"".join(f"<li>{e(m)}</li>" for m in s["marks"])}</ul> {inmerk} </section> '
            f'<section aria-labelledby="h-year"> <h2 id="h-year">Wann ist {nom} {e(N)} zu sehen?</h2> <div class="months" aria-hidden="true"> {months_bar(s)} </div> <p class="legend"><span><i></i>kaum zu sehen</span><span><i class="p"></i>aktiv</span><span><i class="h"></i>beste Zeit</span></p> '
            f'<p class="sr-only">{hidden_sr}</p> <p class="yeartext">{e(N)} ist {month_range(s)}. Besonders viel los ist im {peaks}. {e(s["hl"])}</p>{dmgline} </section> '
            f'<section class="life" aria-labelledby="h-life"> <h2 id="h-life">Lebensweise</h2> {lifes} </section> '
            f'<section class="helpbox" aria-label="Tipps"> <details class="fold" open><summary><h2>{e(s["help"][0])}</h2></summary><p>{e(s["help"][1])}</p>{rgline}</details> <details class="fold" open><summary><h2>{e(s["tip"][0])}</h2></summary><p>{e(s["tip"][1])}</p></details> </section> '
            f'<section class="gearbox" aria-labelledby="h-gear"><h2 id="h-gear">Passend dazu</h2><ul class="products"> '
            + "".join(product(R, p) for p in s["prods"]) +
            f' </ul>{ADNOTE}<p class="gearall"><a href="{R}ausruestung/index.html">Alle Ausrüstungstipps ansehen</a></p></section> '
            f'{alike}<section class="more" aria-labelledby="h-more"> <h2 id="h-more">Mehr erfahren</h2> <ul class="morelinks"> {more} </ul> <p class="stand">Von <a href="{R}ueber/index.html" rel="author">Nico Schober</a> · Stand: {STAND_DE} · Angaben abgeglichen mit Wikipedia und gängiger Bestimmungsliteratur</p> </section> </div>\n'
            f'</div> '
            f'<section class="related" aria-labelledby="h-rel"> <h2 id="h-rel">Oft in der Nähe</h2> <ul class="grid">{"".join(card(R, x, i) for i, x in enumerate(rel))}</ul> </section> {pager(R, s)} </article> </main> ' + footer(R))
    write(f"arten/{k}/index.html", body)
