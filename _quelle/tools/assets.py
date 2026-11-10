# -*- coding: utf-8 -*-
"""Erzeugt Favicons, App-Icons, OG-Bild und Platzhalter-Illustrationen.

ACHTUNG: main() überschreibt die echten Fotos in static/photos mit Platzhaltern.
Nur gezielt einzelne Jobs rendern (siehe og_svg / favicon_svg). Aufruf aus src/: python -m tools.assets
"""
import json, os, subprocess, hashlib, io, shutil
from PIL import Image
from data.species import S, EXTRA

OUT = "static"
TMP = "tmp_png"

CHROME = "#24412f"; INK = "#f6f1e3"; GOLD = "#f2b53a"

# Blatt im Kompassring (48er Raster)
from gtk.logo import LEAF, LOGO_SYMBOL

def favicon_svg(pad=True):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            f'<rect width="48" height="48" rx="11" fill="{CHROME}"/>'
            f'<circle cx="24" cy="25" r="17.5" fill="none" stroke="{INK}" stroke-width="2.4"/>'
            f'<g fill="{INK}" transform="translate(0 1)">{LEAF}</g>'
            f'<path d="M24 4.5 27 10.5H21z" fill="{GOLD}"/></svg>')

def maskable_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            f'<rect width="48" height="48" fill="{CHROME}"/>'
            f'<g transform="translate(9.6 9.6) scale(.6)"><circle cx="24" cy="25" r="17.5" fill="none" stroke="{INK}" stroke-width="2.4"/>'
            f'<g fill="{INK}" transform="translate(0 1)">{LEAF}</g><path d="M24 4.5 27 10.5H21z" fill="{GOLD}"/></g></svg>')

# ---------------------------------------------------------- Motive je Gruppe

MOTIF_OF = {
 "tigerschnegel": "snail", "weinbergschnecke": "snail", "spanische-wegschnecke": "snail",
 "tagpfauenauge": "butterfly", "zitronenfalter": "butterfly", "grosser-kohlweissling": "butterfly", "taubenschwaenzchen": "butterfly",
 "buchsbaumzuensler": "butterfly", "apfelwickler": "butterfly", "kleiner-frostspanner": "butterfly", "x-kleiner-kohlweissling": "butterfly",
 "regenwurm": "worm", "gartenkreuzspinne": "spider", "maulwurf": "paw", "schermaus": "paw", "eichhoernchen": "paw", "steinmarder": "paw",
 "blindschleiche": "lizard", "zauneidechse": "lizard", "x-waldeidechse": "lizard", "x-ringelnatter": "lizard",
}
BUTTER_COL = {"tagpfauenauge": ("#b5452e", "#2c3a6a"), "zitronenfalter": ("#e8cf3a", "#c98a1c"), "taubenschwaenzchen": ("#8a6a4a", "#e08a2a"),
              "buchsbaumzuensler": ("#f2efe6", "#8a5a3a"), "apfelwickler": ("#8b8a86", "#a0602a"), "kleiner-frostspanner": ("#9a8f7d", "#6d6455")}

def extra_motif(kind, key, dx, rot):
    if kind == "snail":
        bg = "#e6ead6"
        body = "#c8692f" if key == "spanische-wegschnecke" else "#b9ab8e"
        m = (f'<g transform="translate({330+dx} 330) rotate({rot//2})"><path d="M-230 90C-230 40 120 30 200 50c40 10 60 40 40 60-30 10-430 10-440-20z" fill="{body}"/>'
             f'<path d="M190 55c10-40 0-80-10-110M215 60c20-40 25-80 25-115" stroke="{body}" stroke-width="12" stroke-linecap="round" fill="none"/>'
             '<circle cx="180" cy="-58" r="12" fill="#22301f"/><circle cx="240" cy="-58" r="12" fill="#22301f"/>')
        if key == "tigerschnegel":
            m += "".join(f'<ellipse cx="{x}" cy="{70+(x%3)*6}" rx="18" ry="8" fill="#4a4136"/>' for x in range(-190, 170, 45))
        if key != "spanische-wegschnecke" and key != "tigerschnegel":
            m += '<circle cx="-20" cy="-30" r="120" fill="#9a6a3a"/><path d="M-20-30m-80 0a80 80 0 1 1 80 80 50 50 0 1 1-50-50 25 25 0 1 1 25 25" fill="none" stroke="#6b4422" stroke-width="12"/>'
        return bg, m + '</g>'
    if kind == "butterfly":
        bg = "#f0ead2"
        c1, c2 = BUTTER_COL.get(key, ("#f6f3ea", "#22301f"))
        m = (f'<g transform="translate({360+dx} 290) rotate({rot})"><path d="M0-20C-60-200-260-200-240-80-230 0-120 20 0 10Z" fill="{c1}" stroke="#5b4a3a" stroke-width="4"/>'
             f'<path d="M0-20C60-200 260-200 240-80 230 0 120 20 0 10Z" fill="{c1}" stroke="#5b4a3a" stroke-width="4"/>'
             f'<path d="M0 10C-40 40-200 80-170 170-110 210-30 120 0 40ZM0 10C40 40 200 80 170 170 110 210 30 120 0 40Z" fill="{c1}" stroke="#5b4a3a" stroke-width="4"/>'
             f'<circle cx="-160" cy="-100" r="38" fill="{c2}"/><circle cx="160" cy="-100" r="38" fill="{c2}"/><circle cx="-120" cy="130" r="24" fill="{c2}"/><circle cx="120" cy="130" r="24" fill="{c2}"/>'
             '<ellipse cx="0" cy="20" rx="14" ry="120" fill="#3a3027"/><path d="M-6-95c-20-50-40-70-60-80M6-95c20-50 40-70 60-80" stroke="#3a3027" stroke-width="6" fill="none"/></g>')
        return bg, m
    if kind == "worm":
        return "#e9dfcf", (f'<g transform="translate({360+dx} 300) rotate({rot})"><path d="M-260 40C-200-80-80 120 0 0S200-80 260 40" fill="none" stroke="#c77a6e" stroke-width="56" stroke-linecap="round"/>'
                           + "".join(f'<path d="M{x} -40v80" stroke="#a65d52" stroke-width="4" opacity=".6"/>' for x in range(-220, 240, 40)) +
                           '<path d="M-140 0v1" stroke="#e4b3a6" stroke-width="70" stroke-linecap="round"/><path d="M-300 160H300" stroke="#8a6a4a" stroke-width="10" opacity=".4"/></g>')
    if kind == "spider":
        web = "".join(f'<path d="M0 0L{int(330*__import__("math").cos(a/57.3))} {int(330*__import__("math").sin(a/57.3))}" stroke="#fff" stroke-width="3" opacity=".8"/>' for a in range(0, 360, 30))
        rings = "".join(f'<circle r="{r}" fill="none" stroke="#fff" stroke-width="2.5" opacity=".7"/>' for r in range(60, 330, 55))
        legs = "".join(f'<path d="M0 0Q{sx*90} {dy-60} {sx*150} {dy+40}" stroke="#4a3626" stroke-width="12" fill="none" stroke-linecap="round"/>' for sx in (-1, 1) for dy in (-60, -20, 20, 60))
        return "#cfdac4", (f'<g transform="translate(360 288)">{web}{rings}<g transform="rotate({rot})">{legs}<ellipse cx="0" cy="-40" rx="46" ry="40" fill="#4a3626"/>'
                           '<ellipse cx="0" cy="60" rx="80" ry="95" fill="#8a5a2c"/><path d="M0 20v90M-34 60h68" stroke="#f6f1e3" stroke-width="12" stroke-linecap="round" stroke-dasharray="2 20"/></g></g>')
    if kind == "paw":
        return "#ece2d2", (f'<g transform="translate({360+dx} 300) rotate({rot})" fill="#7a5a3c"><ellipse cx="0" cy="60" rx="110" ry="95"/>'
                           '<ellipse cx="-130" cy="-50" rx="42" ry="58"/><ellipse cx="-50" cy="-120" rx="42" ry="60"/><ellipse cx="50" cy="-120" rx="42" ry="60"/><ellipse cx="130" cy="-50" rx="42" ry="58"/></g>')
    if kind == "lizard" and key in ("blindschleiche", "x-ringelnatter"):
        col = "#a07a46" if key == "blindschleiche" else "#55604a"
        extra = '<path d="M170-28c14-6 26-6 34 4" stroke="#e8d36a" stroke-width="14" fill="none"/>' if key == "x-ringelnatter" else ""
        return "#e7e6d0", (f'<g transform="translate({360+dx} 300) rotate({rot})"><path d="M-280 80C-200-40-100 120 0 40S170-60 230-10" fill="none" stroke="{col}" stroke-width="46" stroke-linecap="round"/>'
                           f'<path d="M-280 80C-200-40-100 120 0 40S170-60 230-10" fill="none" stroke="#fff" stroke-width="6" opacity=".35" transform="translate(0 -10)"/>{extra}<circle cx="222" cy="-16" r="7" fill="#22301f"/></g>')
    if kind == "lizard":
        col = "#7a8a3c" if key == "zauneidechse" else "#9a7a4a"
        return "#e7e6d0", (f'<g transform="translate({360+dx} 300) rotate({rot})"><path d="M-300 120C-200 140-120 40-40 30S120 60 200-10c30-25 70-20 90 0-20 25-50 40-90 40-70 0-140 60-240 40" fill="{col}"/>'
                           f'<path d="M-40 34l-40 70M60 38l-30 70M60 38 100 -30M-40 30 -70-40" stroke="{col}" stroke-width="22" stroke-linecap="round"/><circle cx="255" cy="0" r="8" fill="#22301f"/></g>')
    return None

def motif(group, key):
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    rot = (h % 25) - 12
    dx = (h >> 5) % 60 - 30
    kind = MOTIF_OF.get(key)
    if kind:
        bg, m = extra_motif(kind, key, dx, rot)
        dots = "".join(f'<circle cx="{(i*97)%720}" cy="{(i*61)%576}" r="{2+(i%3)}" fill="#fff" opacity=".35"/>' for i in range(60))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 576"><defs><radialGradient id="g" cx="50%" cy="45%" r="70%">'
                f'<stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
                f'<rect width="720" height="576" fill="{bg}"/><rect width="720" height="576" fill="url(#g)"/>{dots}{m}</svg>')
    if group == "Nützlinge":
        bg, c1 = "#dfe8cf", "#c0412c"
        m = (f'<g transform="translate({360+dx} 300) rotate({rot})">'
             '<ellipse cx="0" cy="24" rx="150" ry="165" fill="#c0412c"/>'
             '<path d="M0-140V188" stroke="#22301f" stroke-width="8"/>'
             '<path d="M-92-118a92 72 0 0 1 184 0z" fill="#22301f"/>'
             '<circle cx="-42" cy="-150" r="14" fill="#f6f1e3"/><circle cx="42" cy="-150" r="14" fill="#f6f1e3"/>'
             '<circle cx="-70" cy="-20" r="30" fill="#22301f"/><circle cx="70" cy="-20" r="30" fill="#22301f"/>'
             '<circle cx="-85" cy="80" r="26" fill="#22301f"/><circle cx="85" cy="80" r="26" fill="#22301f"/>'
             '<circle cx="-40" cy="140" r="20" fill="#22301f"/><circle cx="40" cy="140" r="20" fill="#22301f"/>'
             '<circle cx="0" cy="-80" r="24" fill="#22301f"/></g>')
    elif group == "Bestäuber":
        bg = "#f4e6bd"
        petals = "".join(f'<ellipse cx="0" cy="-110" rx="62" ry="105" fill="#f2b53a" transform="rotate({a})"/>' for a in range(0, 360, 45))
        m = (f'<g transform="translate({360+dx} 290) rotate({rot})">{petals}'
             '<circle r="78" fill="#8a5418"/><circle r="78" fill="none" stroke="#6b3f10" stroke-width="10" stroke-dasharray="4 14"/></g>')
    elif group == "Schädlinge":
        bg = "#e4ead5"
        m = (f'<g transform="translate({360+dx} 290) rotate({rot-20})">'
             '<path d="M0-230C150-170 175 60 0 230C-175 60-150-170 0-230Z" fill="#6f8f3c"/>'
             '<path d="M0-210V230" stroke="#4f6a27" stroke-width="9"/>'
             '<path d="M0-90 85-150M0-10 105-60M0 70 95 30M0-90-85-150M0-10-105-60M0 70-95 30" stroke="#4f6a27" stroke-width="6"/>'
             '<circle cx="-60" cy="-40" r="24" fill="#e4ead5"/><circle cx="55" cy="40" r="30" fill="#e4ead5"/><circle cx="-40" cy="110" r="18" fill="#e4ead5"/>'
             '<path d="M105-120a30 30 0 0 1 30 40 40 40 0 0 1-30-40z" fill="#e4ead5"/></g>')
    elif group == "Säugetiere":
        bg = "#ece2d2"
        import math
        sp_ = []
        for i in range(15):
            a = math.pi * (0.06 + 0.86 * i / 14)
            x, y = -10 - 205 * math.cos(a), 50 - 150 * math.sin(a)
            nx, ny = -math.cos(a), -math.sin(a)
            tx, ty = x + nx * 70, y + ny * 70
            px, py = -ny * 20, nx * 20
            sp_.append(f'<path d="M{x-px:.1f} {y-py:.1f}L{tx:.1f} {ty:.1f}L{x+px:.1f} {y+py:.1f}z" fill="#5d432c"/>')
        m = (f'<g transform="translate({360+dx} 330) rotate({rot//2})">' + "".join(sp_) +
             '<path d="M-215 50A205 150 0 0 1 195 50Z" fill="#7a5a3c"/>'
             '<path d="M120 0c60 5 110 40 125 80-40 18-100 18-150 0z" fill="#c9a77e"/>'
             '<circle cx="248" cy="78" r="13" fill="#22301f"/><circle cx="175" cy="38" r="9" fill="#22301f"/>'
             '<path d="M-150 50v40M-60 50v40M40 50v40M120 50v35" stroke="#5d432c" stroke-width="22" stroke-linecap="round"/></g>')
    else:
        bg = "#d8e5dc"
        m = (f'<g transform="translate({360+dx} 310) rotate({rot})">'
             '<ellipse cx="0" cy="40" rx="210" ry="150" fill="#5f8a4e"/>'
             '<circle cx="-110" cy="-90" r="70" fill="#5f8a4e"/><circle cx="110" cy="-90" r="70" fill="#5f8a4e"/>'
             '<circle cx="-110" cy="-95" r="42" fill="#f6f1e3"/><circle cx="110" cy="-95" r="42" fill="#f6f1e3"/>'
             '<circle cx="-104" cy="-92" r="22" fill="#22301f"/><circle cx="104" cy="-92" r="22" fill="#22301f"/>'
             '<path d="M-120 40q120 70 240 0" fill="none" stroke="#3f6634" stroke-width="12" stroke-linecap="round"/>'
             '<circle cx="-60" cy="110" r="14" fill="#7aa665"/><circle cx="70" cy="125" r="18" fill="#7aa665"/><circle cx="10" cy="80" r="10" fill="#7aa665"/></g>')
    dots = "".join(f'<circle cx="{(i*97)%720}" cy="{(i*61)%576}" r="{2+(i%3)}" fill="#fff" opacity=".35"/>' for i in range(60))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 576"><defs><radialGradient id="g" cx="50%" cy="45%" r="70%">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="720" height="576" fill="{bg}"/><rect width="720" height="576" fill="url(#g)"/>{dots}{m}</svg>')

EXTRA_GROUP = {"x-wespe": "Bestäuber", "x-grasfrosch": "Amphibien & Reptilien", "x-waldeidechse": "Amphibien & Reptilien",
               "x-kolibri": "Bestäuber", "x-maikaefer": "Schädlinge", "x-kleiner-kohlweissling": "Schädlinge", "x-ringelnatter": "Amphibien & Reptilien"}

def og_svg():
    G="#2f6b3f"; D="#24402c"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
            '<defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e7f2d6"/><stop offset="1" stop-color="#fbfaf4"/></linearGradient></defs>'
            '<rect width="1200" height="630" fill="url(#b)"/><circle cx="1080" cy="40" r="330" fill="#f9d36b" opacity=".35"/>'
            f'<g transform="translate(80 195) scale(5)"><circle cx="24" cy="24" r="21" fill="none" stroke="{D}" stroke-width="2.2"/>'
            f'<g fill="{G}">{LEAF}</g><path d="M24 1.8 26.6 7.4H21.4z" fill="{GOLD}"/></g>'
            f'<text x="370" y="300" font-family="Young Serif" font-size="74" fill="{D}">Gartentierkompass</text>'
            f'<text x="373" y="370" font-family="Atkinson Hyperlegible Next" font-weight="700" font-size="38" fill="{G}">Wer lebt in deinem Garten?</text>'
            f'<text x="373" y="425" font-family="Atkinson Hyperlegible Next" font-size="29" fill="#5b6b5e">Nützlinge, Schädlinge und Gartengäste bestimmen</text></svg>')

def main():
    os.makedirs(f"{OUT}/photos", exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    jobs = []
    def job(svg, name, width):
        jobs.append({"svg": svg, "out": f"{TMP}/{name}.png", "width": width})

    keys = [(s["key"], s["grp"]) for s in S] + list(EXTRA_GROUP.items())
    for k, g in keys:
        job(motif(g, k), k, 720)
    job(favicon_svg(), "icon-512", 512); job(favicon_svg(), "icon-192", 192); job(favicon_svg(), "apple", 180)
    job(favicon_svg(), "fav48", 48); job(maskable_svg(), "maskable", 512); job(og_svg(), "og", 1200)
    json.dump(jobs, open("jobs.json", "w"))
    subprocess.run(["node", "render.mjs", "jobs.json"], check=True)

    for k, g in keys:
        im = Image.open(f"{TMP}/{k}.png").convert("RGB")
        im.save(f"{OUT}/photos/{k}.webp", "WEBP", quality=82)
        im.resize((400, 320), Image.LANCZOS).save(f"{OUT}/photos/{k}-400.webp", "WEBP", quality=80)
    shutil.copy(f"{TMP}/icon-512.png", f"{OUT}/icon-512.png")
    shutil.copy(f"{TMP}/icon-192.png", f"{OUT}/icon-192.png")
    shutil.copy(f"{TMP}/apple.png", f"{OUT}/apple-touch-icon.png")
    shutil.copy(f"{TMP}/maskable.png", f"{OUT}/icon-maskable-512.png")
    Image.open(f"{TMP}/fav48.png").save(f"{OUT}/favicon.ico", sizes=[(48, 48), (32, 32), (16, 16)])
    Image.open(f"{TMP}/og.png").convert("RGB").save(f"{OUT}/photos/og.jpg", "JPEG", quality=86)
    open(f"{OUT}/favicon.svg", "w").write(favicon_svg())
    print("ok", len(keys), "Platzhalter")

if __name__ == "__main__":
    main()
