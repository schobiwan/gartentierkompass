"""Wiederverwendbare Bausteine: Bilder, Karten, Produkte, Monatsleiste."""
from urllib.parse import quote_plus
from gtk.config import *
from gtk.util import *
from gtk.layout import *

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

def cred_small(k):
    return f'<small class="cred"><span>{cred_long(k, cropped=False)}</span></small>'

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
            f'<span class="meta"><span class="latin" lang="la">{e(s["latin"])}</span><span class="size">{e(s["size"])}</span></span> <span class="row">{role_badge(s)}{grp_tag(s)}</span> '
            f'<p class="short">{e(s["short"])}</p> </div> <span class="acts">{acts_html(s)}</span> </li>')

def mcard(R, href, imgkey, name, why, meta=""):
    return (f'<li class="mcard"><a href="{href}"> {img(R, imgkey, "(max-width: 600px) 92vw, 300px")} <span class="mname">{e(name)}</span><span class="mwhy">{e(why)}</span>'
            + (f'<span class="mmeta">{e(meta)}</span>' if meta else "") + f' </a>{cred_small(imgkey)}</li>')

GUIDE_FOR = {}

def guide_map():
    if not GUIDE_FOR:
        for slug, d in sorted(RATGEBER.items(), key=lambda x: x[0] != "nuetzlinge"):
            for sec in d["sections"]:
                for p in sec[6]:
                    GUIDE_FOR.setdefault(p, (slug, d["nav"]))
    return GUIDE_FOR

def product(R, key, compact=False, why=True, guide=True):
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
            f' <a class="plink" href="{e(amazon(q))}" target="_blank" rel="sponsored nofollow noopener"><span>Bei Amazon ansehen<span aria-hidden="true">*</span></span>{ARROW}<span class="sr-only"> {e(name)} (Werbelink, öffnet in neuem Fenster)</span></a> ' + (f'<a class="pguide" href="{R}ratgeber/{guide_map()[key][0]}/index.html">Ratgeber: {e(guide_map()[key][1])}</a> ' if guide and key in guide_map() else "") + '</div> </li>')

ROLE_ICO = {
    "nuetzling": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "bestaeuber": '<circle cx="12" cy="12" r="2.5"/><path d="M12 9.5C10 6 10 3.5 12 3.5s2 2.5 0 6M14.5 12c3.5-2 6-2 6 0s-2.5 2-6 0M12 14.5c2 3.5 2 6 0 6s-2-2.5 0-6M9.5 12c-3.5 2-6 2-6 0s2.5-2 6 0"/>',
    "schaedling": '<path d="M12 21c-5-3-8-7.5-8-12.5C4 6 6 4 8.5 4 10 4 11.3 4.7 12 6c.7-1.3 2-2 3.5-2C18 4 20 6 20 8.5 20 13.5 17 18 12 21z"/><circle cx="9.5" cy="10" r="1.3"/><circle cx="14.5" cy="13" r="1.6"/>',
    "gast": '<path d="M3 11 12 4l9 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "gemischt": '<path d="M12 3 3 20h18z"/><path d="M12 10v4M12 17h0"/>',
}

ROLE_SHORT = {"gemischt": "Teils Nützling"}   # kurze Fassung für Schilder

def grp_tag(s):
    """Gruppe als neutrales Schild – nur wenn sie nicht schon in der Rolle steckt (Nützlinge, Schädlinge, Bestäuber)."""
    return "" if s["grp"] in ("Nützlinge", "Schädlinge", "Bestäuber") else f'<span class="tag grp">{e(s["grp"])}</span>'

def role_badge(s):
    """Farbiges Rollen-Schild mit Symbol: Nützling, Bestäuber, Schädling, Gartengast."""
    r = s["role"]
    title = f' title="{e(ROLE[r])}"' if r in ROLE_SHORT else ""
    return (f'<span class="role role-{r}"{title}><svg viewBox="0 0 24 24" aria-hidden="true">{ROLE_ICO[r]}</svg>'
            f'{e(ROLE_SHORT.get(r, ROLE[r]))}</span>')

def months_bar(s):
    out = []
    for m in range(1, 13):
        c = "h" if m in s["peak"] else "p" if m in s["present"] else ""
        t = "Hauptzeit" if c == "h" else "aktiv" if c == "p" else "kaum zu sehen"
        out.append(f'<span data-month="{m}" class="{c}" title="{MN[m-1]}: {t}">{MA[m-1]}</span>')
    return "".join(out)

def month_range(s):
    p = sorted(s["present"])
    if len(p) == 12:
        return "das ganze Jahr über zu sehen"
    return f"von {MN[p[0]-1]} bis {MN[p[-1]-1]} zu sehen" if p == list(range(p[0], p[-1] + 1)) else "zu sehen im " + join_de(MN[m-1] for m in p)


def pair_fig(R, key, sizes, eager, big=False):
    lat = f' <i lang="la">{e(LATIN[key])}</i>' if big else ""
    return (f'<figure>{img(R, key, sizes, eager=eager, alt=NAMES[key] if (big and key in PHOTOS) else "")}<figcaption>{e(NAMES[key])}{lat}<small>{cred_long(key, cropped=big)}</small></figcaption></figure>')

def pair_card(R, p, h="h2"):
    slug, a, b, intro, short, rows, merk = p
    return (f'<li class="pair"> <div class="ph"> {pair_fig(R, a, "(max-width: 600px) 46vw, 240px", False)}{pair_fig(R, b, "(max-width: 600px) 46vw, 240px", False)} </div> <div class="pb"> '
            f'<{h}><a class="pair-link" href="{R}unterscheiden/{slug}/index.html">{e(NAMES[a])} oder {e(NAMES[b])}?</a></{h}> <p>{e(short)}</p> <span class="to" aria-hidden="true">Alle Unterschiede</span> </div> </li>')

def rlist(items, cls):
    return f'<ul class="rlist {cls}">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"
