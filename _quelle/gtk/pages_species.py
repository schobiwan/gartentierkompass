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

def species_title(s):
    """Seitentitel nach Suchabsicht: Schädlinge werden gesucht, um sie loszuwerden, Nützlinge, um sie zu verstehen."""
    if s.get("seo_title"): return s["seo_title"]
    N = s["name"]
    opts = {"schaedling": [f"{N}: erkennen und ohne Gift bekämpfen", f"{N}: erkennen und vorbeugen"],
            "gemischt": [f"{N}: Nützling oder Schädling?"],
            "nuetzling": [f"{N} im Garten: erkennen und fördern", f"{N}: erkennen und fördern"],
            "bestaeuber": [f"{N} im Garten: erkennen und fördern", f"{N}: erkennen und fördern"],
            "gast": [f"{N} im Garten: erkennen und verstehen", f"{N} im Garten erkennen"]}[s["role"]]
    t = next((x for x in opts if len(x) <= 60), opts[-1])
    return t + f" · {SITE}" if len(t) + len(SITE) + 3 <= 60 else t

def species_desc(s):
    """Vollständige Beschreibung ohne Abbruch, höchstens 158 Zeichen."""
    N = s["name"]
    tail = {"schaedling": " Mit Schadbild und sanften Mitteln.", "gemischt": " Mit Merkmalen und Tipps."}.get(s["role"], " Mit Merkmalen, Nahrung und Tipps.")
    for c in (f'{N} im Garten erkennen: {s["short"]}{tail}', f'{N} im Garten erkennen: {s["short"]}',
              f'{N} erkennen: {s["roleline"]}.{tail} Wann und wo du {decline(N, "akk", s["pron"]).split(" ", 1)[0]} am besten siehst.',
              f'{N} erkennen: {s["roleline"]}.{tail}', f'{N} erkennen: {s["roleline"]}.'):
        if len(c) <= 158: return c
    return c

def faq_ld(s):
    """FAQPage aus den Fragen der Lebensweise, Sichtungszeit und Hilfe-Tipp."""
    N, pron = s["name"], s["pron"]
    qa = []
    for t, x in s["life"]:
        if t.startswith("Was frisst "): t = f"Was frisst {decline(N, 'nom', pron)}?"
        if t.endswith("?"): qa.append((t, x))
    p = sorted(s["present"])
    zeit = "ganzjährig" if len(p) == 12 else f"von {MN[p[0]-1]} bis {MN[p[-1]-1]}" if p == list(range(p[0], p[-1] + 1)) else "im " + join_de(MN[m-1] for m in p)
    qa.append((f"Wann ist {decline(N, 'nom', pron)} im Garten zu sehen?", f"{decline(N, 'nom', pron)[0].upper()}{decline(N, 'nom', pron)[1:]} ist {zeit} zu sehen, am besten im {join_de(MN[m-1] for m in s['peak'])}. {s['hl']}"))
    qa.append((f"Wo lebt {decline(N, 'nom', pron)} im Garten?", f"Typische Orte im Garten: {s['where']}."))
    ht = s["help"][0]
    if ht.startswith("So hilfst du"): ht = f"Wie hilft man {decline(N, 'dat', pron)}?"
    elif ht in ("Sanft vorbeugen", "Früh erkennen"): ht = f"Was hilft gegen {decline(N, 'akk', pron)}?"
    else: ht = f"{ht}: Was ist zu tun?"
    qa.append((ht, s["help"][1]))
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def page_species(s):
    R = "../../"; k = s["key"]
    nom, akk, dat = ART[s["pron"]]
    N = s["name"]
    desc = species_desc(s)
    title = species_title(s)
    peaks = join_de(f'<a href="{R}gartenjahr/{MS[m-1]}/index.html">{MN[m-1]}</a>' for m in s["peak"])
    pres = [m for m in range(1, 13) if m in s["present"]]
    hidden_sr = f'Aktiv: {join_de(MN[m-1] for m in pres)}. Hauptzeit: {join_de(MN[m-1] for m in s["peak"])}.'
    life_title = lambda t: f"Was frisst {decline(N, 'nom', s['pron'])}?" if t.startswith("Was frisst ") else t   # einheitlich mit vollem Artnamen
    lifes = "".join(f'<details class="fold" open data-fold><summary><h3>{e(life_title(t))}</h3></summary><p>{e(x)}</p></details>' for t, x in s["life"])
    help_title = s["help"][0] if not s["help"][0].startswith("So hilfst du") else f"So hilfst du {decline(N, 'dat', s['pron'])}"
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
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title, "name": f'{N} im Garten', "description": desc, "inLanguage": "de-DE",
           "mainEntityOfPage": f"{BASE}arten/{k}/", "isPartOf": {"@id": BASE + "#website"}, "publisher": {"@id": ORG_ID},
           "author": {"@type": "Person", "name": "Nico Schober", "url": BASE + "ueber/"}, "datePublished": s.get("published", "2026-11-07"), "dateModified": STAND_ISO,
           "about": {"@type": "Taxon", "name": s["latin"], "alternateName": [N] + ([s["alias"].split()[0]] if s["alias"].split()[0] != N else []), "taxonRank": "species"},
           "image": {"@type": "ImageObject", "url": f'{BASE}photos/{k}.webp', "width": 720, "height": 576}},
          faq_ld(s)]
    body = (head(R, title, desc, f'arten/{k}/', "article", og_img=f'photos/{k}.webp', og_alt=N, ld=ld)
            + nav(R, "bestimmen") + '<main id="main" tabindex="-1"> ' + crumbs(R, [("Arten", "arten/"), (N, f"arten/{k}/")]) +
            f'<article class="sp wrap"> <div class="sp-top"> <figure class="sp-photo"> {img(R, k, "(max-width: 760px) 92vw, 560px", eager=True, alt=N if k in PHOTOS else "")} <figcaption>{cred_long(k)}</figcaption> </figure> '
            f'<div class="sp-intro"> <h1>{e(N)}</h1> <p class="latin" lang="la">{e(s["latin"])}</p> <p class="row">{role_badge(s)}{grp_tag(s)}<span class="tag">{e(s["size"])}</span>'
            + "".join(f'<span class="tag act-tag"><svg aria-hidden="true"><use href="#{ACT[a][1]}"></use></svg>{ACT[a][0]}</span>' for a in s["acts"]) +
            f'</p> <p class="habs">{"".join(f"<span>{e(h)}</span>" for h in s["hab"])}</p> <p class="text">{e(s["short"])} {e(s["hl"])}</p> '
            f'</div> </div>\n'
            f'<div class="sp-cols"> <aside class="sp-side" aria-label="Auf einen Blick"> {tldr(s)} </aside> <div class="sp-main"> <section aria-labelledby="h-marks"> <h2 id="h-marks">So erkennst du {e(decline(N, "akk", s["pron"]))}</h2> <ul class="marks">{"".join(f"<li>{e(m)}</li>" for m in s["marks"])}</ul> {inmerk} </section> '
            f'<section aria-labelledby="h-year"> <h2 id="h-year">Wann ist {e(decline(N, "nom", s["pron"]))} zu sehen?</h2> <div class="months" aria-hidden="true"> {months_bar(s)} </div> <p class="legend"><span><i></i>kaum zu sehen</span><span><i class="p"></i>aktiv</span><span><i class="h"></i>beste Zeit</span></p> '
            f'<p class="sr-only">{hidden_sr}</p> <p class="yeartext">{e(decline(N, "nom", s["pron"])[0].upper() + decline(N, "nom", s["pron"])[1:])} ist {month_range(s)}. Besonders viel los ist im {peaks}. {e(s["hl"])}</p>{dmgline} </section> '
            f'<section class="life" aria-labelledby="h-life"> <h2 id="h-life">Lebensweise</h2> {lifes} </section> '
            f'<section class="helpbox" aria-label="Tipps"> <details class="fold" open><summary><h2>{e(help_title)}</h2></summary><p>{e(s["help"][1])}</p>{rgline}</details> <details class="fold" open><summary><h2>{e(s["tip"][0])}</h2></summary><p>{e(s["tip"][1])}</p></details> </section> '
            f'<section class="gearbox" aria-labelledby="h-gear"><h2 id="h-gear">Passend dazu</h2><ul class="products"> '
            + "".join(product(R, p) for p in s["prods"]) +
            f' </ul>{ADNOTE}<p class="gearall"><a href="{R}ausruestung/index.html">Alle Ausrüstungstipps ansehen</a></p></section> '
            f'{alike}<section class="more" aria-labelledby="h-more"> <h2 id="h-more">Mehr erfahren</h2> <ul class="morelinks"> {more} </ul> <p class="stand">Von <a href="{R}ueber/index.html" rel="author">Nico Schober</a> · Stand: {STAND_DE} · Angaben abgeglichen mit Wikipedia und gängiger Bestimmungsliteratur</p> </section> </div>\n'
            f'</div> '
            f'<section class="related" aria-labelledby="h-rel"> <h2 id="h-rel">Oft in der Nähe</h2> <ul class="grid">{"".join(card(R, x, i) for i, x in enumerate(rel))}</ul> </section> {pager(R, s)} </article> </main> ' + footer(R))
    write(f"arten/{k}/index.html", body)
