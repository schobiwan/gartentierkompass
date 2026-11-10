"""Bestimmen: Vergleiche, Schadbilder, Merkmale, Größen."""
import json, math, os, re
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *
from gtk.components import *

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

def page_merkmale():
    R = "../"
    cards = []
    for slug, title, short, intro, items in MERKMALE:
        names = [SP[k]["name"] for k, _ in items]
        cards.append(mcard(R, f"{R}merkmale/{slug}/index.html", items[0][0], short, f'Zum Beispiel {join_de(names[:2])}', count=f'{len(items)} Arten'))
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
                f'<h2 class="h3 mt">Andere Merkmale</h2> <ul class="morelinks">{ol}<li><a href="{R}merkmale/index.html">Alle Merkmale ansehen</a></li></ul> </div> </section> </main> ' + footer(R))
        write(f"merkmale/{slug}/index.html", body)

def size_range(s):
    t = s["size"].replace("plus Schwanz", "").replace("Spannweite", "").replace("Gehäuse", "").replace("Raupe bis", "").strip()
    unit = 0.1 if "mm" in t else 1.0
    nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:,\d+)?", t)]
    lo, hi = (nums[0], nums[-1]) if len(nums) > 1 else (nums[0] * 0.8, nums[0])
    return lo * unit, hi * unit

def page_sizes():
    R = "../"
    lo_all, hi_all = math.log10(0.08), math.log10(160)
    pos = lambda v: (math.log10(v) - lo_all) / (hi_all - lo_all) * 100
    rows = []
    for i, s in enumerate(sorted(S, key=lambda x: -size_range(x)[1])):
        lo, hi = size_range(s)
        l, r = pos(lo), pos(hi)
        rows.append(f'<div class="srow" role="listitem"><a class="n" href="{R}arten/{s["key"]}/index.html">{e(s["name"])}</a> <div class="track"><span class="rng{' lft' if r > 76 else ''}" style="left:{l:.2f}%;width:{max(r - l, 1.2):.2f}%;--i:{i}"><span>{e(s["size"])}</span></span></div> </div>')
    ticks = [(0.1, "1 mm"), (1, "1 cm"), (10, "10 cm"), (50, "50 cm")]
    marks = "".join(f'<span style="left:{pos(v):.2f}%">{lab}</span>' for v, lab in ticks)
    grid = ",".join(f"linear-gradient(to right,transparent calc({pos(v):.2f}% - 1px),var(--grid-line) calc({pos(v):.2f}% - 1px),var(--grid-line) calc({pos(v):.2f}% + 1px),transparent calc({pos(v):.2f}% + 1px))" for v, _ in ticks)
    axis = f'<div class="srow saxis" aria-hidden="true"><span class="n"></span><div class="track">{marks}</div></div>'
    body = (head(R, f"Größenvergleich: wie groß sind Gartentiere? · {SITE}", "Von der winzigen Blattlaus bis zum Steinmarder: alle Gartentiere im Größenvergleich.", "groessen/") + nav(R, "bestimmen") +
            '<main id="main" tabindex="-1"> ' + crumbs(R, [("Größenvergleich", "groessen/")]) +
            '<section class="block page"> <div class="wrap"> <h1>Wie groß ist welches Gartentier?</h1> <p class="intro">Körperlänge, bei Schmetterlingen die Flügelspannweite, bei der Weinbergschnecke das Gehäuse. Weil eine Blattlaus und ein Steinmarder so verschieden sind, wächst die Skala in Zehnerschritten: 1 mm, 1 cm, 10 cm.</p> '
            f'<p class="swipe">Seitlich wischen, um die ganze Skala zu sehen.</p> <div class="scale"><div class="scale-inner" role="list" style="--grid:{grid}"> {axis} {"".join(rows)} {axis} </div></div> </div> </section> </main> ' + footer(R))
    write("groessen/index.html", body)
