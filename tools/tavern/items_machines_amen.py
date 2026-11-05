"""Machinery sprites, part 3: the gadgets and small goods that sit with the machines (the game's "amenities").

Medieval stand-ins that keep each thing's job: cassettes become ballad tablets (a wooden case with two ribbon bobbins),
scanners become scrying slates in a frame, rolls of tissue become rolls of linen, tubes and bottles become corked glass,
test strips stay parchment strips with dyed bands, the UV tube becomes a brass lamp tube. Numbered variants share one
drawing and differ only in colour and markings. Each sprite is drawn one pixel inside the original's occupied area and
then given a dark outline, so it never leaves that area.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial

from PIL import Image, ImageChops

from itemkit_machines import (Mask, cylinder, ellipse_mask, gear, pipe, rects, rim, rust, shade_mask, valve)
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, STONE, WINE, WOOD
from pix import Color, Pix, Ramp, mix, rgb

Draw = Callable[[], Image.Image]
ASSETS: dict[str, Draw] = {}


def ramp_of(hex6: str) -> Ramp:
    """Five tones from one colour: a violet-brown shadow, the colour, a warm light."""
    base = rgb(hex6)
    return (mix(base, rgb("#170f12"), 0.7), mix(base, rgb("#170f12"), 0.42), base, mix(base, rgb("#ffe6b0"), 0.28), mix(base, rgb("#ffe6b0"), 0.55))


def finish(p: Pix) -> Image.Image:
    p.outline(SHADOW)
    return p.im


# occupied areas (x0, y0, x1, y1; x1/y1 excluded) of the pictures whose outline would otherwise stray past them
AREA: dict[str, tuple[int, int, int, int]] = {
    "aquascan": (3, 6, 29, 43), "cig_red": (7, 2, 25, 30), "genetic_scanner": (3, 6, 29, 44), "genetic_scanner_on": (3, 6, 29, 44),
    "lottery": (1, 6, 15, 26), "lottery_old": (1, 6, 15, 26), "lottery_teared": (1, 6, 15, 26), "metal_scanner": (1, 3, 61, 45),
    "portable_water_purifier": (2, 4, 30, 28), "skincare_cream": (4, 4, 28, 29), "toilet_paper": (3, 1, 29, 31),
    "toothpaste": (0, 1, 47, 16), "uv": (1, 1, 79, 15), "water_filter": (2, 2, 14, 30), "water_filter_adv": (2, 6, 14, 42),
    "water_tablet": (1, 3, 15, 14), "water_tablet_container": (2, 5, 14, 44), "water_test_strip": (5, 1, 10, 31),
    "strip0": (5, 2, 11, 30), "strip1": (5, 2, 11, 30), "strip2": (5, 2, 11, 30), "strip3": (5, 2, 11, 30), "strip4": (5, 2, 11, 30),
    "strip5": (5, 2, 11, 30), "strip_new": (5, 2, 11, 30), "strip_used": (5, 2, 11, 30),
}


def fit(fn: Draw, area: tuple[int, int, int, int]) -> Draw:
    """Slides a picture into its occupied area (and clips what still overhangs by a pixel)."""
    def run() -> Image.Image:
        im = fn()
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if bb is None:
            return im
        dx = area[0] - bb[0] if bb[0] < area[0] else min(0, area[2] - bb[2])
        dy = area[1] - bb[1] if bb[1] < area[1] else min(0, area[3] - bb[3])
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.paste(im, (dx, dy))
        clip = Image.new("L", im.size, 0)
        clip.paste(255, area)
        out.putalpha(ImageChops.multiply(out.getchannel("A"), clip))
        return out
    return run


def add(name: str, fn: Draw) -> None:
    ASSETS[f"items~items_amenities@{name}.png"] = fit(fn, AREA[name]) if name in AREA else fn


def band_rows(p: Pix, x: int, y: int, w: int, colours: Sequence[Color], h: int = 2) -> None:
    for i, c in enumerate(colours):
        p.rect(x, y + i * h, w, h, c)


# ---------------------------------------------------------------------------------------------- ballad tablets (cassettes)


def tablet(body: str, label: str, stripes: Sequence[str], seed: int, worn: bool = False) -> Image.Image:
    """A flat wooden case with a parchment label above two ribbon bobbins in a window."""
    p = Pix(32, 32, seed=seed)
    r = ramp_of(body)
    shade_mask(p, rects((3, 7, 28, 24)) - {(3, 7), (28, 7), (3, 24), (28, 24)}, r, base=2)
    p.hline(5, 8, 22, r[4])
    lab = ramp_of(label)
    p.rect(6, 9, 20, 7, lab[3])
    p.hline(6, 9, 20, lab[4])
    p.hline(6, 15, 20, lab[1])
    for i, s in enumerate(stripes):
        c = rgb(s)
        p.rect(7, 11 + i * 2, 18, 1, c)
        p.px(7, 11 + i * 2, mix(c, SHADOW, 0.3))
    p.rect(6, 17, 20, 6, SOOT[0])                                    # the window
    p.hline(6, 17, 20, SHADOW)
    for cx in (11, 21):
        p.ellipse(cx - 3, 18, 7, 5, LINEN[2])
        p.ellipse(cx - 2, 19, 5, 3, SOOT[1])
        p.px(cx, 20, BRASS[3])
        p.px(cx - 3, 20, LINEN[3])
    p.hline(13, 21, 6, IRON[2])
    for x, y in ((4, 8), (27, 8), (4, 23), (27, 23)):
        p.px(x, y, BRASS[3])
    if worn:
        for x in range(8, 24, 3):
            p.px(x, 13, mix(lab[3], SHADOW, 0.35))
    return finish(p)


TABLETS = (
    ("cassette1", "#b3a88c", "#d4cab0", ()),
    ("cassette3", "#3b3a43", "#d4cab0", ("#5e8250", "#3e5e38")),
    ("cassette4", "#4d5058", "#9a9588", ("#2f4c70",)),
    ("cassette5", "#b0652c", "#d4cab0", ("#7a272b", "#e0842c")),
    ("cassette6", "#9a3a62", "#d4cab0", ("#521a20", "#c25b49")),
    ("cassette7", "#2b2027", "#d4cab0", ("#a13a38", "#2b2027", "#a13a38")),
    ("cassette8", "#5a9aa0", "#cfe0d0", ("#2f5266", "#8ab0b8")),
    ("cassette8b", "#6a4a86", "#b9a8c4", ("#3f2150", "#a272c0")),
    ("cassette9", "#3e8250", "#d4cab0", ("#16231a", "#86a86a")),
    ("cassette9b", "#a65a3a", "#c4a8b8", ("#5f3578", "#e0842c")),
    ("cassette10", "#26252c", "#d4cab0", ("#a13a38", "#5e8250", "#e0cb8e", "#2f4c70")),
    ("cassette10b", "#a13a38", "#d4cab0", ("#521a20", "#d0a847")),
    ("cassette11b", "#4a8a96", "#d4cab0", ("#1c3140", "#c25b49")),
    ("cassette12b", "#b3a88c", "#d4cab0", ("#3e5e38", "#5e8250")),
    ("cassette13b", "#c9ab6a", "#2f4c70", ("#8ab0b8", "#d4cab0")),
    ("cassette14b", "#3a2c27", "#4a8a96", ("#a13a38", "#7a272b", "#2f5266")),
)
for n, body, label, stripes in TABLETS:
    add(n, partial(tablet, body, label, stripes, 300 + len(n) * 3 + ord(n[-1])))


# ---------------------------------------------------------------------------------------------- scrying slates (scanners)


def slate(frame: str, seed: int, glow: bool = False, rings: bool = True) -> Image.Image:
    """A hand-held slate: coloured frame, a pane of dark glass, a brass hanging ring on top and a button plate below."""
    p = Pix(32, 48, seed=seed)
    r = ramp_of(frame)
    body = ellipse_mask(15.5, 25, 12, 18)
    body = rects((5, 9, 26, 42)) - {(5, 9), (26, 9), (5, 42), (26, 42), (6, 9), (25, 9), (5, 10), (26, 10), (6, 42), (25, 42), (5, 41), (26, 41)}
    shade_mask(p, body, r, base=2)
    p.vline(7, 14, 22, r[3])
    if rings:
        p.ellipse(12, 5, 8, 6, BRASS[2])
        p.ellipse(14, 7, 4, 2, SOOT[0])
        p.hline(13, 5, 5, BRASS[4])
    pane = rects((8, 14, 23, 34)) - {(8, 14), (23, 14), (8, 34), (23, 34)}
    shade_mask(p, pane, GLASS, base=1)
    p.rect(9, 15, 14, 19, GLASS[0] if not glow else rgb("#24100e"))
    p.hline(9, 15, 14, SOOT[0])
    p.hline(10, 16, 6, GLASS[2] if not glow else rgb("#40201a"))
    p.vline(9, 17, 6, GLASS[1] if not glow else rgb("#40201a"))
    if glow:                                                         # amber runes on the lit pane
        for y in (18, 22, 26, 30):
            for x in range(10, 22, 3):
                if (x + y) % 2 == 0 or y == 22:
                    p.rect(x, y, 2, 1, FLAME[3])
                p.px(x, y + 1, FLAME[1]) if (x * y) % 3 == 0 else None
        p.glow(16, 24, 8, FLAME[1], 0.35)
    p.rect(11, 37, 10, 3, BRASS[2])
    p.hline(11, 37, 10, BRASS[4])
    p.hline(11, 39, 10, BRASS[0])
    for x in (13, 16, 19):
        p.px(x, 38, SHADOW)
    p.px(7, 11, BRASS[4])
    p.px(24, 11, BRASS[2])
    return finish(p)


add("aquascan", partial(slate, "#5a9aa0", 321))
add("chem_scanner", partial(slate, "#c8bfa4", 322))
add("genetic_scanner", partial(slate, "#8a4ca0", 323))
add("genetic_scanner_on", partial(slate, "#8a4ca0", 323, True))


def dowsing_ring() -> Image.Image:
    """The metal scanner: a dowsing staff with a leather grip, a brass compass box and a big spoked iron hoop."""
    p = Pix(64, 48, seed=330)
    cx, cy = 47, 24
    ring = ellipse_mask(cx, cy, 13, 19) - ellipse_mask(cx, cy, 9, 15)
    shade_mask(p, ring, IRON, base=2)
    for a in range(-1, 2):                                          # three spokes and a hub
        p.line(cx, cy, cx + a * 8, cy - 14, IRON[2])
        p.line(cx, cy, cx + a * 8, cy + 14, IRON[1])
    p.hline(cx - 9, cy, 19, IRON[2])
    p.rect(cx - 2, cy - 2, 5, 5, BRASS[2])
    p.hline(cx - 2, cy - 2, 5, BRASS[4])
    p.px(cx, cy, SHADOW)
    for k in range(5):                                              # lit upper-left arc
        p.px(cx - 11 + k, cy - 11 + k * 0 - k, IRON[4])
    for d in (-1, 0, 1):                                            # the staff
        p.line(14, 42 + d, 36, 28 + d, (IRON[3], IRON[2], IRON[1])[d + 1])
    p.line(38, 28, 38, 24, IRON[2])
    p.rect(36, 24, 4, 7, BRASS[2])
    p.hline(36, 24, 4, BRASS[4])
    p.line(8, 40, 18, 44, LEATHER[1])                               # grip wrapped in leather
    p.line(9, 39, 19, 43, LEATHER[2])
    p.line(8, 41, 18, 45, LEATHER[0])
    for x in range(9, 18, 3):
        p.line(x, 40 + (x - 9) // 3, x + 1, 43 + (x - 9) // 3, LEATHER[3])
    box = rects((8, 7, 24, 22)) - {(8, 7), (24, 7), (8, 22), (24, 22)}
    shade_mask(p, box, BRASS, base=2)
    p.rect(10, 9, 12, 8, GLASS[1])
    p.hline(10, 9, 12, GLASS[4])
    p.frame(10, 9, 12, 8, SHADOW)
    p.rect(11, 10, 10, 6, PARCHMENT[3])
    p.line(16, 15, 19, 11, SHADOW)
    p.px(16, 15, EMBER_RED)
    for x in (11, 15, 19):
        p.px(x, 19, BRASS[4])
        p.px(x + 1, 19, BRASS[0])
    p.vline(16, 22, 10, IRON[1])
    p.line(16, 31, 14, 41, IRON[1])
    return finish(p)


EMBER_RED = rgb("#b2402a")
add("metal_scanner", dowsing_ring)


# ---------------------------------------------------------------------------------------------- boxes, pouches, papers


def tally_box() -> Image.Image:
    """The tampon box: a painted wooden box with a leaf on its lid and a lettered plaque."""
    p = Pix(48, 48, seed=340)
    shade_mask(p, rects((7, 6, 40, 41)), NAVY, base=2)
    p.rect(8, 7, 32, 3, NAVY[3])
    p.hline(8, 7, 32, NAVY[3])
    p.hline(8, 10, 32, NAVY[0])
    for x in range(10, 38, 4):
        p.px(x, 8, BRASS[3])
    p.ellipse(11, 14, 20, 13, MOSS[2])                              # leaf
    p.ellipse(13, 14, 16, 8, MOSS[3])
    p.line(12, 26, 28, 16, MOSS[0])
    p.poly([(14, 29), (30, 29), (36, 36), (20, 38)], LEATHER[3])
    p.poly([(16, 31), (30, 31), (34, 35), (22, 36)], LEATHER[2])
    p.rect(11, 31, 6, 2, PARCHMENT[3])                              # lettering as bars
    for x, w in ((19, 3), (24, 4), (30, 3)):
        p.rect(x, 21, w, 4, PARCHMENT[3])
        p.rect(x, 21, w, 1, PARCHMENT[4])
    p.vline(36, 15, 10, PARCHMENT[2])
    p.hline(34, 14, 4, PARCHMENT[2])
    p.px(34, 16, PARCHMENT[3])
    p.rect(8, 38, 32, 3, NAVY[1])
    p.hline(8, 38, 32, NAVY[0])
    p.px(10, 40, BRASS[2])
    p.px(37, 40, BRASS[2])
    p.speckle(9, 11, 30, 26, (NAVY[1], NAVY[3]), 0.04)
    return finish(p)


def tobacco_pouch() -> Image.Image:
    """cig_red: a wine-red cloth pouch of pipe tobacco, mouth cinched with a cord and a parchment tag."""
    p = Pix(32, 32, seed=345)
    body = ellipse_mask(15.5, 20, 8.5, 9.5) | rects((9, 8, 22, 12))
    shade_mask(p, body, WINE, grain=0.08, base=2)
    p.vline(10, 14, 10, WINE[4])
    p.vline(11, 14, 8, WINE[3])
    p.rect(9, 7, 14, 3, WINE[1])                                     # gathered mouth
    p.hline(9, 7, 14, WINE[3])
    for x in range(10, 22, 2):
        p.vline(x, 4, 4, WINE[2] if x % 4 else WINE[3])
    p.hline(8, 10, 16, BRASS[2])                                     # cord
    p.hline(8, 11, 16, BRASS[0])
    p.px(23, 12, BRASS[3])
    p.line(23, 12, 25, 16, BRASS[2])
    p.rect(11, 15, 11, 9, PARCHMENT[3])
    p.frame(11, 15, 11, 9, PARCHMENT[1])
    p.hline(11, 15, 11, PARCHMENT[4])
    p.rect(15, 17, 3, 3, BRASS[2])
    p.px(15, 17, BRASS[4])
    p.hline(13, 22, 7, WINE[2])
    p.px(24, 25, WINE[0])
    return finish(p)


def ticket(state: str) -> Image.Image:
    """A draw ticket: parchment slip, red header, number grid; old = browned and folded, teared = ripped corner."""
    p = Pix(16, 32, seed=350 + len(state))
    paper = PARCHMENT if state == "new" else (rgb("#4a3a1c"), rgb("#7a5f2c"), rgb("#a8884a"), rgb("#c9ab6a"), rgb("#d6c080"))
    m = rects((2, 7, 13, 25))
    if state == "torn":
        m -= {(13, 7), (13, 8), (12, 7), (11, 7), (13, 9), (12, 8), (2, 25), (3, 25), (2, 24)}
        m |= set()
    if state == "old":
        m -= {(2, 7), (3, 7), (2, 8), (13, 25), (12, 25)}
    shade_mask(p, m, paper, base=3)
    p.rect(3, 8, 10, 3, WINE[2])
    p.hline(3, 8, 10, WINE[3])
    p.px(5, 9, PARCHMENT[4])
    p.px(8, 9, PARCHMENT[4])
    p.px(10, 9, PARCHMENT[4])
    for y in range(13, 24, 3):
        for x in (4, 7, 10):
            p.rect(x, y, 2, 2, mix(paper[2], SHADOW, 0.3))
    if state == "old":
        p.line(2, 16, 13, 18, paper[1])
        p.line(2, 17, 13, 19, paper[4])
        p.dither(3, 20, 9, 5, paper[1], 0.5)
        p.px(5, 14, WINE[1])
    if state == "torn":
        for x, y in ((11, 9), (10, 8), (12, 10)):
            p.px(x, y, paper[1])
        p.line(2, 21, 6, 24, SHADOW)
    return finish(p)


add("box_tampon", tally_box)
add("cig_red", tobacco_pouch)
add("lottery", partial(ticket, "new"))
add("lottery_old", partial(ticket, "old"))
add("lottery_teared", partial(ticket, "torn"))


def packet() -> Image.Image:
    """pack_condom: a flat navy packet, sealed with a crowned wax seal and striped in brass and teal."""
    p = Pix(32, 48, seed=360)
    shade_mask(p, rects((5, 5, 26, 42)), NAVY, base=2)
    p.frame(6, 6, 20, 36, BRASS[1])
    for i, c in enumerate((GLASS[4], BRASS[3], WINE[3], GLASS[3])):
        for k in range(18):
            p.px(7 + k, 40 - k - i * 5, c) if 7 + k < 25 and 28 - k - i * 5 > 8 else None
    p.ellipse(10, 9, 12, 9, WINE[2])                                 # seal with crown
    p.ellipse(11, 10, 10, 7, WINE[3])
    p.rect(12, 14, 8, 2, BRASS[3])
    for x in (12, 15, 19):
        p.rect(x, 11, 1, 3, BRASS[3])
        p.px(x, 10, BRASS[4])
    p.rect(7, 38, 18, 2, NAVY[3])
    p.px(24, 40, WINE[4])
    p.px(23, 39, WINE[3])
    p.hline(6, 5, 20, NAVY[3])
    for x in range(7, 25, 2):
        p.px(x, 6, NAVY[1])
    return finish(p)


add("pack_condom", packet)


def roll(w: int, h: int, cx: int, seed: int, tall: bool) -> Image.Image:
    """A roll of linen cloth on its paper core, loose end curling off the bottom right."""
    p = Pix(32, 48 if tall else 32, seed=seed)
    x0 = cx - w // 2
    y0 = 4
    body = rects((x0, y0 + 2, x0 + w - 1, y0 + h - 2))
    shade_mask(p, body, LINEN, base=2)
    cylinder(p, x0, y0 + 2, w, h - 4, LINEN)
    p.ellipse(x0, y0, w, 7, LINEN[3])                                # top face with the core hole
    p.ellipse(x0 + 1, y0 + 1, w - 2, 5, LINEN[3])
    p.ellipse(x0 + w // 2 - 3, y0 + 2, 6, 3, PALE_WOOD[2])
    p.ellipse(x0 + w // 2 - 2, y0 + 2, 4, 2, SOOT[0])
    p.hline(x0 + 2, y0 + 1, 5, LINEN[3])
    for y in range(y0 + 9, y0 + h - 3, 4):                           # woven lines
        p.hline(x0 + 2, y, w - 5, LINEN[1])
    tail = [(x0 + w - 4, y0 + h - 8), (x0 + w + 2, y0 + h - 10), (x0 + w + 3, y0 + h), (x0 + w - 2, y0 + h - 1), (x0 + w - 5, y0 + h - 3)]
    p.poly(tail, LINEN[2])
    p.line(x0 + w + 2, y0 + h - 8, x0 + w + 3, y0 + h - 1, LINEN[1])
    p.line(x0 + w - 4, y0 + h - 3, x0 + w - 1, y0 + h - 2, LINEN[0])
    for k in range(3):
        p.px(x0 + w + 2, y0 + h - 1 + (k % 2), LINEN[1] if k % 2 else LINEN[3])
    return finish(p)


add("paper_towel", partial(roll, 18, 40, 15, 365, True))
add("toilet_paper", partial(roll, 22, 27, 14, 366, False))


# ---------------------------------------------------------------------------------------------- bottles and jars


def glass_bottle(p: Pix, x: int, y: int, w: int, h: int, liquid: Ramp, fill: float = 0.75) -> Mask:
    m = rects((x, y, x + w - 1, y + h - 1)) - {(x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)}
    shade_mask(p, m, GLASS, base=2)
    top = y + 2 + round((h - 4) * (1 - fill))
    for yy in range(top, y + h - 1):
        for xx in range(x + 1, x + w - 1):
            k = (xx - x) / max(1, w - 1)
            p.px(xx, yy, liquid[3] if k < 0.3 else liquid[2] if k < 0.7 else liquid[1])
    p.hline(x + 1, top, w - 2, liquid[4])
    p.vline(x + 1, y + 2, h - 4, GLASS[4])
    p.px(x + 1, top + 1, liquid[4])
    return m


def perfume(liquid: str, seed: int) -> Image.Image:
    p = Pix(32, 32, seed=seed)
    lr = ramp_of(liquid)
    glass_bottle(p, 8, 11, 16, 17, lr, 0.8)
    p.rect(11, 17, 10, 6, PARCHMENT[3])                               # label
    p.hline(11, 17, 10, PARCHMENT[4])
    p.hline(11, 22, 10, PARCHMENT[1])
    p.hline(13, 19, 6, SHADOW)
    p.hline(13, 20, 6, lr[1])
    p.rect(13, 7, 6, 4, BRASS[2])                                    # collar and stopper
    p.hline(13, 7, 6, BRASS[4])
    p.vline(13, 7, 4, BRASS[3])
    p.hline(13, 10, 6, BRASS[0])
    p.rect(11, 3, 10, 4, BRASS[3])
    p.hline(11, 3, 10, BRASS[4])
    p.hline(11, 6, 10, BRASS[1])
    p.px(13, 4, SHADOW)
    p.px(18, 4, BRASS[1])
    return finish(p)


add("perfume1", partial(perfume, "#c27a3a", 370))
add("perfume2", partial(perfume, "#b23a3a", 371))


def shampoo() -> Image.Image:
    p = Pix(32, 48, seed=375)
    glass_bottle(p, 8, 12, 16, 32, ramp_of("#8cb89a"), 0.85)
    p.rect(12, 5, 8, 8, PALE_WOOD[2])                                 # cork
    p.hline(12, 5, 8, PALE_WOOD[4])
    p.vline(12, 5, 8, PALE_WOOD[3])
    p.vline(19, 5, 8, PALE_WOOD[0])
    p.speckle(13, 6, 6, 6, (PALE_WOOD[1], PALE_WOOD[4]), 0.2)
    p.rect(10, 17, 12, 22, PARCHMENT[3])
    p.hline(10, 17, 12, PARCHMENT[4])
    p.vline(10, 17, 22, PARCHMENT[4])
    p.vline(21, 17, 22, PARCHMENT[1])
    p.hline(10, 38, 12, PARCHMENT[1])
    p.ellipse(13, 19, 6, 5, GLASS[3])                                 # eye of the herb mark
    p.px(16, 21, SHADOW)
    p.line(16, 37, 16, 28, MOSS[1])                                   # herb sprig
    for y, dx in ((34, 3), (31, 3), (28, 2)):
        p.line(16, y + 1, 16 - dx, y - 1, MOSS[3])
        p.line(16, y + 1, 16 + dx, y - 1, MOSS[2])
    return finish(p)


def cream_jar() -> Image.Image:
    p = Pix(32, 32, seed=380)
    body = rects((5, 15, 26, 27)) - {(5, 27), (26, 27), (5, 15), (26, 15)}
    shade_mask(p, body, LINEN, base=2)
    cylinder(p, 5, 15, 22, 13, LINEN)
    p.rect(6, 22, 20, 3, GLASS[3])                                    # glass band
    p.hline(6, 22, 20, GLASS[4])
    p.hline(6, 24, 20, GLASS[1])
    p.ellipse(4, 8, 24, 11, PALE_WOOD[1])                             # wooden lid
    p.ellipse(5, 8, 22, 9, PALE_WOOD[3])
    p.ellipse(8, 9, 16, 6, PALE_WOOD[2])
    p.hline(8, 9, 10, PALE_WOOD[4])
    for k in range(3):
        p.line(10 + k * 4, 14, 14 + k * 4, 9, PALE_WOOD[1])
    p.rect(11, 11, 10, 2, BRASS[2])
    p.hline(11, 11, 10, BRASS[4])
    return finish(p)


add("shampoo", shampoo)
add("skincare_cream", cream_jar)


def purifier() -> Image.Image:
    """Portable water purifier: an oak crate with a funnel, a glass settling chamber and a brass tap."""
    p = Pix(32, 32, seed=385)
    shade_mask(p, rects((3, 13, 28, 27)), OAK, grain=0.1, base=3)
    p.rect(5, 15, 10, 9, GLASS[1])                                    # glass chamber
    p.frame(5, 15, 10, 9, SHADOW)
    p.rect(6, 19, 8, 4, rgb("#4f7c8c"))
    p.hline(6, 19, 8, rgb("#8ab0b8"))
    p.vline(6, 16, 7, GLASS[4])
    p.rect(17, 15, 9, 9, IRON[2])
    p.hline(17, 15, 9, IRON[4])
    p.vline(17, 15, 9, IRON[3])
    p.hline(17, 23, 9, IRON[0])
    valve(p, 21, 19, 2)
    p.px(25, 17, BRASS[4])
    p.poly([(6, 12), (23, 12), (19, 6), (10, 6)], BRASS[2])           # funnel
    p.hline(10, 6, 10, BRASS[4])
    p.hline(6, 12, 18, BRASS[1])
    p.line(8, 11, 11, 7, BRASS[3])
    p.rect(14, 4, 3, 2, BRASS[0])
    pipe(p, 22, 24, 6, thick=2)
    p.vline(27, 24, 3, BRASS[1])
    p.px(27, 27, WATER_DROP)
    p.hline(5, 25, 22, OAK[1])
    return finish(p)


WATER_DROP = rgb("#8ab0b8")
add("portable_water_purifier", purifier)


# ---------------------------------------------------------------------------------------------- strips, tubes and small things


STRIPS = {
    "strip0": ("#5e8250", "#5e8250", "#8a9a4a", "#c9ab6a"),
    "strip1": ("#5e8250", "#8a9a4a", "#c9ab6a", "#c9ab6a"),
    "strip2": ("#8a9a4a", "#c9ab6a", "#c9ab6a", "#b0652c"),
    "strip3": ("#8a9a4a", "#c9ab6a", "#b0652c", "#b0652c"),
    "strip4": ("#c9ab6a", "#b0652c", "#a13a38", "#a13a38"),
    "strip5": ("#b0652c", "#a13a38", "#7a272b", "#521a20"),
    "strip_new": ("#d4cab0", "#d4cab0", "#cfe0d0", "#d4cab0"),
    "strip_used": ("#4a5a3a", "#6a5a3a", "#5a3a2a", "#3a2a2a"),
}


def strip(colours: Sequence[str], seed: int) -> Image.Image:
    """A test strip: parchment with dyed pads near the tip and an iron-grey handle."""
    p = Pix(16, 32, seed=seed)
    shade_mask(p, rects((6, 3, 9, 29)), PARCHMENT, base=3)
    for i, c in enumerate(colours):
        col = rgb(c)
        p.rect(7, 5 + i * 4, 2, 3, col)
        p.hline(7, 5 + i * 4, 2, mix(col, rgb("#ffe6b0"), 0.35))
        p.hline(7, 7 + i * 4, 2, mix(col, SHADOW, 0.4))
    p.rect(7, 22, 2, 6, IRON[2])
    p.vline(7, 22, 6, IRON[3])
    p.vline(8, 22, 6, IRON[1])
    p.hline(6, 21, 4, PARCHMENT[0])
    return finish(p)


for n, cols in STRIPS.items():
    add(n, partial(strip, cols, 390 + len(n)))


def toothpaste() -> Image.Image:
    """A pewter tube of tooth powder: brass nozzle with a cork, crimped flat at the far end."""
    p = Pix(48, 16, seed=400)
    body = poly = rects((11, 4, 38, 12))
    shade_mask(p, body, LINEN, base=2)
    p.hline(12, 5, 26, LINEN[3])
    p.hline(12, 6, 26, LINEN[3])
    p.hline(12, 11, 26, LINEN[1])
    p.rect(5, 6, 7, 5, BRASS[2])                                      # shoulder and nozzle
    p.hline(5, 6, 7, BRASS[4])
    p.hline(5, 10, 7, BRASS[1])
    p.rect(1, 7, 5, 3, PALE_WOOD[2])
    p.hline(1, 7, 5, PALE_WOOD[4])
    p.hline(1, 9, 5, PALE_WOOD[0])
    p.rect(38, 3, 8, 10, LINEN[2])                                    # crimped end
    for x in range(39, 46, 2):
        p.vline(x, 3, 10, LINEN[1])
        p.vline(x + 1, 3, 10, LINEN[3])
    p.rect(20, 5, 12, 6, WINE[2])                                     # printed band
    p.hline(20, 5, 12, WINE[4])
    p.hline(20, 10, 12, WINE[0])
    p.hline(22, 7, 8, PARCHMENT[3])
    p.hline(23, 8, 6, PARCHMENT[2])
    return finish(p)


def lamp_tube() -> Image.Image:
    """The UV lamp: a long glass tube with a glowing amber filament, held in two iron-and-brass end caps."""
    p = Pix(80, 16, seed=405)
    p.rect(8, 4, 64, 9, GLASS[1])
    p.hline(8, 4, 64, GLASS[4])
    p.hline(8, 5, 64, GLASS[3])
    p.hline(8, 12, 64, GLASS[0])
    p.rect(9, 7, 62, 3, FLAME[1])
    p.hline(9, 8, 62, FLAME[3])
    for x in range(12, 70, 9):
        p.px(x, 8, FLAME[4])
    p.hline(9, 6, 62, mix(rgb("#4f7c8c"), FLAME[1], 0.4))
    p.hline(9, 10, 62, mix(rgb("#1c3140"), FLAME[0], 0.5))
    for x0 in (2, 66):
        p.rect(x0, 2, 12, 12, IRON[2])
        p.hline(x0, 2, 12, IRON[4])
        p.vline(x0, 2, 12, IRON[3])
        p.hline(x0, 13, 12, IRON[0])
        p.vline(x0 + 11, 2, 12, IRON[1])
        p.rect(x0 + 2, 5, 8, 2, BRASS[2])
        p.hline(x0 + 2, 5, 8, BRASS[4])
        p.px(x0 + 3, 11, BRASS[4])
        p.px(x0 + 8, 11, BRASS[3])
    p.rect(12, 1, 3, 2, BRASS[2])                                      # hanging loops
    p.rect(65, 1, 3, 2, BRASS[2])
    for x in range(30, 52, 7):
        p.px(x, 13, SHADOW)
    return finish(p)


add("toothpaste", toothpaste)
add("uv", lamp_tube)


def candle_filter(adv: bool) -> Image.Image:
    """A ceramic filter candle: a tall stoneware cone with a collar; the advanced one is banded in brass and taller."""
    h = 36 if adv else 28
    p = Pix(16, 48 if adv else 32, seed=410 + adv)
    top = 7 if adv else 3
    clay = (PALE_WOOD[1], PALE_WOOD[2], PALE_WOOD[3], PALE_WOOD[4], rgb("#e6cf94")) if adv else (STONE[2], STONE[3], rgb("#a8a090"), rgb("#c8c0ac"), rgb("#e0d8c0"))
    m = rects((3, top + 6, 12, top + h - 3)) | rects((5, top, 10, top + 6)) | rects((4, top + h - 3, 11, top + h - 2))
    m -= {(3, top + 6), (12, top + 6)}
    shade_mask(p, m, clay, grain=0.05, base=2)
    cylinder(p, 3, top + 8, 10, h - 12, clay, round_top=False)
    p.rect(3, top + 5, 10, 3, clay[1])                                 # collar
    p.hline(3, top + 5, 10, clay[3])
    p.hline(3, top + 7, 10, clay[0])
    p.rect(6, top + 1, 4, 2, IRON[2])                                  # brass cap
    if adv:
        for y in (top + 14, top + 24):
            p.rect(3, y, 10, 2, BRASS[2])
            p.hline(3, y, 10, BRASS[4])
        p.rect(5, top - 1, 6, 3, BRASS[3])
        p.hline(5, top - 1, 6, BRASS[4])
        p.vline(8, top + 16, 6, SHADOW)
    else:
        p.rect(5, top, 6, 2, BRASS[2])
        p.hline(5, top, 6, BRASS[4])
        p.speckle(4, top + 9, 8, 14, (clay[1],), 0.1)
    return finish(p)


add("water_filter", partial(candle_filter, False))
add("water_filter_adv", partial(candle_filter, True))


def lozenge() -> Image.Image:
    p = Pix(16, 16, seed=415)
    m = ellipse_mask(8, 8, 6, 4)
    shade_mask(p, m, STONE, base=3)
    p.ellipse(4, 5, 8, 5, STONE[3])
    p.hline(6, 6, 4, STONE[4])
    p.line(5, 9, 11, 7, STONE[1])
    p.px(6, 6, PARCHMENT[3])
    return finish(p)


def tube_bottle(kind: str) -> Image.Image:
    """water_tablet_container (tall, corked, banded label) and water_test_container (short vial holding strips)."""
    tall = kind == "tablet"
    p = Pix(16, 48 if tall else 32, seed=420 + tall)
    x, y, w, h = (3, 9, 10, 34) if tall else (3, 8, 10, 22)
    g = glass_bottle(p, x, y, w, h, ramp_of("#6ab0a4"), 0.7)
    cork = rects((x + 1, y - 5, x + w - 2, y))
    shade_mask(p, cork, PALE_WOOD, base=2)
    p.hline(x + 1, y - 4, w - 2, PALE_WOOD[4])
    p.px(x + 4, y - 2, PALE_WOOD[0])
    p.rect(x + 1, y + 6, w - 2, 12 if tall else 9, PARCHMENT[3])
    p.hline(x + 1, y + 6, w - 2, PARCHMENT[4])
    p.hline(x + 1, y + 6 + (11 if tall else 8), w - 2, PARCHMENT[1])
    p.rect(x + 2, y + 9, w - 4, 2, GLASS[3])
    p.rect(x + 2, y + 13 if tall else y + 12, w - 4, 1, WINE[2])
    if not tall:
        for i, c in enumerate(("#5e8250", "#c9ab6a", "#a13a38")):
            p.rect(x + 2 + i * 2, y + 14, 2, 6, rgb(c))
            p.vline(x + 2 + i * 2, y + 14, 6, mix(rgb(c), rgb("#ffe6b0"), 0.3))
    if tall:
        p.rect(x + 2, y + 24, w - 4, 6, PARCHMENT[2])
        p.hline(x + 2, y + 24, w - 4, PARCHMENT[3])
    del g
    return finish(p)


def test_strip() -> Image.Image:
    p = Pix(16, 32, seed=425)
    cols = ("#d8a0c8", "#e6c0d8", "#e8a070", "#b8b860", "#9acaa0", "#78d0b8")
    m = rects((6, 2, 8, 29))
    shade_mask(p, m, PARCHMENT, base=3)
    for i, c in enumerate(cols):
        col = rgb(c)
        p.rect(7, 3 + i * 4, 1, 4, col)
        p.hline(7, 3 + i * 4, 1, mix(col, rgb("#ffe6b0"), 0.3))
        p.px(7, 6 + i * 4, mix(col, SHADOW, 0.3))
    return finish(p)


add("water_tablet", lozenge)
add("water_tablet_container", partial(tube_bottle, "tablet"))
add("water_test_container", partial(tube_bottle, "test"))
add("water_test_strip", test_strip)
_ = (gear, rim, rust, LEATHER, FLAME, MOSS)
