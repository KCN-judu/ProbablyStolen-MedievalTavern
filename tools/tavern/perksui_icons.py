"""The 49 small item icons of the main menu's network sheet (`networkIcons.682x493`): 36x36 tiles, each a dark plate carrying
a medieval stand-in of the game's item (hats, cloaks, masks, spectacles, flasks, chests, cracked panes, fish, crossbows,
cheese and wine). Each icon is one function of at most a few shapes, shaded by `perksui_shape.paint` (light from the upper
left), then given a dark rim and laid on the plate.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Final

from PIL import Image

import font
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, MOSS, PALE_WOOD, PARCHMENT, SHADOW, STONE, WINE, WOOD, LINEN
from perksui_shape import Mask, paint, rim, thick
from pix import Color, Pix, Ramp, mix

S: Final = 36
CREAM: Final[Color] = (240, 225, 190)


def ramp(base: Color) -> Ramp:
    """Five tones round a base colour: ink, shade, body, light, highlight."""
    return (mix(base, SHADOW, 0.7), mix(base, SHADOW, 0.38), base, mix(base, CREAM, 0.24), mix(base, CREAM, 0.5))


def M() -> Mask:
    return Mask(S, S)


def sh(p: Pix, m: Mask, r: Ramp, split: float | None = None, edge: bool = True) -> None:
    if edge:
        rim(p, m, r[0])
    paint(p, m, r, split=split)


def new(seed: int) -> Pix:
    return Pix(S, S, seed=seed)


# ---------------------------------------------------------------------------------------------- shared pieces


def flames(p: Pix, cx: int, base_y: int, k: float = 1.0) -> None:
    """A little fire: three tongues, red at the root and pale at the tip."""
    for dx, hgt in ((-4, 8), (0, 12), (4, 7)):
        hh = round(hgt * k)
        p.poly([(cx + dx - 3, base_y), (cx + dx, base_y - hh), (cx + dx + 3, base_y)], FLAME[1])
        p.poly([(cx + dx - 2, base_y), (cx + dx, base_y - hh + 3), (cx + dx + 2, base_y)], FLAME[2])
        p.poly([(cx + dx - 1, base_y), (cx + dx, base_y - hh // 2), (cx + dx + 1, base_y)], FLAME[4])


def chest(wood: Color, seed: int, fire: bool = True) -> Pix:
    """An open iron-bound chest with fire in it: the back of the lid, the glow, the front of the box with straps and a lock."""
    p = new(seed)
    wr = ramp(wood)
    lid = M().poly([(9, 7), (28, 7), (27, 17), (8, 17)])
    sh(p, lid, wr, split=0.7)
    p.vline(14, 8, 9, IRON[2])
    p.vline(22, 8, 9, IRON[2])
    p.rect(10, 17, 18, 3, FLAME[1])                                # the glow in the opening
    p.dither(10, 17, 18, 3, FLAME[3], 0.5)
    if fire:
        flames(p, 19, 18, 1.0)
    front = M().rrect(6, 19, 24, 12, 1)
    sh(p, front, wr, split=0.7)
    for x in (10, 24):
        p.rect(x, 19, 3, 12, IRON[2])
        p.vline(x, 19, 12, IRON[4])
        p.px(x + 1, 22, BRASS[4])
        p.px(x + 1, 28, BRASS[4])
    p.rect(16, 21, 5, 5, BRASS[3])
    p.hline(16, 21, 5, BRASS[4])
    p.px(18, 23, SHADOW)
    p.vline(18, 24, 1, SHADOW)
    p.outline(SHADOW)
    return p


def hat(base: Color, band: Color, seed: int, tall: bool = False) -> Pix:
    """A felt hat in three-quarter view: a wide oval brim, a dented crown and a band."""
    p = new(seed)
    r = ramp(base)
    crown = M().poly([(11, 21), (12, 10), (15, 7), (22, 7), (25, 10), (26, 21)] if tall else
                     [(11, 21), (12, 12), (15, 9), (22, 9), (25, 12), (26, 21)])
    brim = M().oval(4, 19, 29, 11)
    sh(p, brim, r, split=0.6)
    sh(p, crown, r, split=0.6)
    top = 7 if tall else 9
    p.hline(16, top + 1, 6, r[1])                                   # the dent
    p.px(17, top + 2, r[1])
    br = ramp(band)
    p.rect(11, 17, 15, 3, br[2])
    p.hline(11, 17, 15, br[3])
    p.hline(11, 19, 15, br[1])
    p.rect(21, 16, 3, 5, BRASS[3])                                   # buckle
    p.px(22, 18, SHADOW)
    p.outline(SHADOW)
    return p


def cloak(base: Color, seed: int) -> Pix:
    """A rolled travelling cloak: a long bolt with a lit top, a leather strap and a brass clasp."""
    p = new(seed)
    r = ramp(base)
    body = M().poly([(8, 28), (7, 10), (11, 5), (20, 5), (23, 10), (29, 26), (26, 31), (14, 31)])
    sh(p, body, r, split=0.62)
    for k in range(3):                                              # folds
        p.line(12 + k * 4, 8, 11 + k * 5, 28, r[1])
    p.line(11, 9, 24, 12, r[3])
    p.rect(13, 14, 9, 3, LEATHER[2])
    p.hline(13, 14, 9, LEATHER[3])
    p.rect(17, 13, 3, 5, BRASS[3])
    p.px(18, 14, BRASS[4])
    p.outline(SHADOW)
    return p


def mask_icon(base: Color, seed: int) -> Pix:
    """A half-mask worn at a masquerade or by a cutpurse: eye holes, a nose notch and tie ribbons."""
    p = new(seed)
    r = ramp(base)
    shape = M().poly([(5, 14), (11, 11), (18, 13), (25, 11), (31, 14), (30, 20), (24, 24), (20, 20), (16, 20), (12, 24), (6, 20)])
    sh(p, shape, r, split=0.55)
    for cx in (12, 24):
        p.ellipse(cx - 3, 15, 7, 4, SHADOW)
        p.px(cx - 1, 16, (40, 30, 50))
    p.hline(14, 13, 8, r[3])
    p.line(5, 15, 2, 13, r[1])
    p.line(31, 15, 34, 13, r[1])
    p.outline(SHADOW)
    return p


def spectacles(lens: Color, seed: int, shine: bool) -> Pix:
    """Two round lenses in a brass wire with bridge and hooked temples."""
    p = new(seed)
    for cx in (11, 25):
        ring = M().oval(cx - 7, 12, 14, 14)
        sh(p, ring, ramp(BRASS[3]), edge=True)
        glass = M().oval(cx - 5, 14, 10, 10)
        paint(p, glass, ramp(lens))
        p.px(cx - 3, 16, CREAM)
        p.px(cx - 2, 15, CREAM)
        if shine:
            p.hline(cx - 1, 20, 4, ramp(lens)[4])
    p.hline(17, 17, 3, BRASS[2])
    p.px(18, 16, BRASS[4])
    p.line(4, 17, 2, 22, BRASS[2])
    p.line(32, 17, 34, 22, BRASS[2])
    p.outline(SHADOW)
    return p


def flask(liquid: Color, seed: int, smoke: bool = False) -> Pix:
    """A round-bellied flask with a cork; optional rising vapour."""
    p = new(seed)
    glass = M().poly([(15, 8), (21, 8), (21, 15), (28, 24), (26, 30), (10, 30), (8, 24), (15, 15)])
    sh(p, glass, ramp(GLASS[3]))
    fill = M().poly([(11, 22), (16, 19), (21, 20), (26, 23), (25, 28), (11, 28)])
    paint(p, fill, ramp(liquid), split=0.55)
    p.px(13, 20, CREAM)
    p.vline(12, 22, 4, CREAM)
    p.rect(15, 5, 7, 4, LEATHER[3])
    p.hline(15, 5, 7, LEATHER[3])
    p.hline(15, 8, 7, LEATHER[1])
    if smoke:
        for x, y, rr in ((26, 8, 4), (30, 13, 3), (23, 13, 3), (29, 5, 3)):
            p.ellipse(x - rr, y - rr, rr * 2, rr * 2, ramp(liquid)[3])
            p.px(x - 1, y - 1, ramp(liquid)[4])
    p.outline(SHADOW)
    return p


def imp(seed: int) -> Pix:
    """A red imp with horns, bat wings and a flaming tail."""
    p = new(seed)
    r = ramp((190, 52, 40))
    for sx in (-1, 1):
        wing = M().poly([(18 + sx * 5, 15), (18 + sx * 15, 6), (18 + sx * 13, 14), (18 + sx * 16, 20), (18 + sx * 9, 19), (18 + sx * 5, 22)])
        sh(p, wing, ramp((110, 28, 34)))
    body = M().poly([(12, 30), (12, 20), (15, 16), (21, 16), (24, 20), (24, 30)])
    sh(p, body, r, split=0.6)
    head = M().oval(12, 8, 12, 11)
    sh(p, head, r, split=0.6)
    for sx in (-1, 1):
        horn = M().poly([(18 + sx * 4, 9), (18 + sx * 5, 3), (18 + sx * 7, 9)])
        sh(p, horn, ramp(CREAM))
    p.px(15, 13, FLAME[4])
    p.px(21, 13, FLAME[4])
    p.px(15, 14, SHADOW)
    p.px(21, 14, SHADOW)
    p.hline(16, 17, 4, SHADOW)
    flames(p, 18, 34, 0.6)
    p.outline(SHADOW)
    return p


def quill(ink: Color, seed: int) -> Pix:
    """A quill laid on a diagonal with a drop of coloured ink falling from its nib."""
    p = new(seed)
    feather = M().poly([(30, 3), (32, 8), (26, 16), (18, 22), (14, 24), (16, 18), (22, 10)])
    sh(p, feather, ramp(ink), split=0.5)
    p.line(30, 4, 14, 24, ramp(ink)[4])
    for k in range(5):
        p.line(27 - k * 3, 8 + k * 3, 24 - k * 3 + 1, 10 + k * 3 + 1, ramp(ink)[1])
    p.line(14, 24, 9, 29, CREAM)
    p.px(9, 29, SHADOW)
    ro = ramp(ink)
    p.poly([(8, 31), (6, 34), (10, 34)], ro[3])
    p.ellipse(6, 32, 5, 3, ro[3])
    p.px(7, 32, ro[4])
    p.outline(SHADOW)
    return p


def rocks(seed: int) -> Pix:
    """A heap of four grey ore stones."""
    p = new(seed)
    for pts, tone in (([(4, 28), (6, 17), (14, 13), (19, 20), (17, 29)], 3), ([(15, 29), (17, 20), (24, 15), (31, 21), (30, 29)], 2),
                      ([(12, 16), (14, 8), (21, 5), (25, 11), (21, 17)], 4), ([(24, 14), (26, 7), (31, 8), (32, 15)], 3)):
        m = M().poly(pts)
        sh(p, m, ramp(mix(STONE[tone], (130, 130, 150), 0.25)), split=0.6)
    p.line(8, 21, 12, 25, STONE[0])
    p.line(20, 22, 24, 26, STONE[0])
    p.outline(SHADOW)
    return p


def receipt(seed: int) -> Pix:
    """A parchment bill: curled top, ruled lines of writing, a red wax seal."""
    p = new(seed)
    sheet = M().poly([(8, 5), (27, 5), (28, 27), (24, 31), (9, 31)])
    sh(p, sheet, ramp(PARCHMENT[3]), split=0.8)
    for y in range(9, 26, 3):
        p.hline(11, y, 12 if y % 2 else 9, PARCHMENT[1])
    p.ellipse(19, 21, 8, 8, WINE[3])
    p.ellipse(20, 22, 6, 6, WINE[2])
    p.px(21, 23, WINE[4])
    p.vline(23, 24, 3, WINE[1])
    p.outline(SHADOW)
    return p


def tag(seed: int) -> Pix:
    """A red tax tag with a punched hole, a cord and the letters TAX."""
    p = new(seed)
    body = M().poly([(4, 11), (27, 11), (32, 18), (27, 25), (4, 25)])
    sh(p, body, ramp((170, 40, 46)), split=0.7)
    font.write(p, 8, 14, "TAX", CREAM)
    p.ellipse(25, 16, 4, 4, SHADOW)
    p.line(27, 18, 33, 6, LINEN[2])
    p.outline(SHADOW)
    return p


def coins(light: bool, seed: int) -> Pix:
    """A trio of gold coins, each with a crowned head."""
    p = new(seed)
    base = BRASS[3] if light else BRASS[2]
    for cx, cy in ((11, 12), (25, 15), (14, 26)):
        m = M().oval(cx - 7, cy - 7, 14, 14)
        sh(p, m, ramp(base), split=0.58)
        p.ellipse(cx - 5, cy - 5, 10, 10, ramp(base)[2])
        p.px(cx - 2, cy - 2, ramp(base)[4])
        p.hline(cx - 2, cy - 3, 4, ramp(base)[1])             # crown
        p.px(cx - 2, cy - 4, ramp(base)[1])
        p.px(cx + 1, cy - 4, ramp(base)[1])
        p.hline(cx - 2, cy, 4, ramp(base)[1])
        p.px(cx - 1, cy + 2, ramp(base)[1])
        p.hline(cx - 1, cy + 3, 3, ramp(base)[1])
    p.outline(SHADOW)
    return p


def book(base: Color, seed: int) -> Pix:
    """A thick leather book standing a little askew: page block, brass corners and a clasp."""
    p = new(seed)
    pages = M().poly([(9, 8), (27, 6), (28, 28), (10, 31)])
    sh(p, pages, ramp(PARCHMENT[4]))
    for k in range(4):
        p.line(11, 29 - k * 2, 27, 27 - k * 2, PARCHMENT[2])
    cover = M().poly([(6, 7), (23, 5), (25, 29), (7, 31)])
    sh(p, cover, ramp(base), split=0.7)
    p.vline(10, 8, 22, ramp(base)[1])
    p.line(7, 8, 22, 6, ramp(base)[4])
    p.rect(14, 14, 7, 7, BRASS[3])
    p.hline(14, 14, 7, BRASS[4])
    p.px(17, 17, SHADOW)
    for x, y in ((7, 8), (22, 6), (8, 29), (24, 27)):
        p.rect(x - 1, y - 1, 3, 3, BRASS[3])
    p.outline(SHADOW)
    return p


def beret(base: Color, seed: int) -> Pix:
    """A soft round cap with a stalk."""
    p = new(seed)
    cap = M().poly([(5, 24), (6, 17), (12, 11), (22, 10), (30, 15), (31, 23), (25, 27), (12, 27)])
    sh(p, cap, ramp(base), split=0.6)
    p.rect(17, 7, 3, 4, ramp(base)[1])
    p.hline(6, 24, 24, ramp(base)[0])
    p.hline(7, 25, 22, ramp(base)[1])
    p.dither(8, 13, 18, 6, ramp(base)[3], 0.25)
    p.outline(SHADOW)
    return p


def herbs(seed: int) -> Pix:
    """A bundle of three dried herb stalks tied with twine, a few bubbles of steam round it."""
    p = new(seed)
    for x, tone in ((10, MOSS[3]), (17, (170, 160, 110)), (24, MOSS[2])):
        stem = M().poly([(x - 2, 6), (x + 2, 6), (x + 3, 30), (x - 1, 30)])
        sh(p, stem, ramp(tone), split=0.5)
        for y in range(9, 27, 5):
            p.hline(x - 2, y, 5, ramp(tone)[1])
    p.rect(8, 21, 20, 3, LEATHER[3])
    p.hline(8, 21, 20, LEATHER[3])
    p.hline(8, 23, 20, LEATHER[1])
    for x, y in ((31, 8), (5, 12), (30, 17)):
        p.ellipse(x - 2, y - 2, 5, 5, GLASS[4])
        p.px(x - 1, y - 1, CREAM)
    p.outline(SHADOW)
    return p


def rope(seed: int) -> Pix:
    """A coil of rope with a scrap of iron."""
    p = new(seed)
    scrap = M().poly([(18, 6), (30, 10), (32, 20), (24, 24), (18, 18), (21, 13)])
    sh(p, scrap, ramp(IRON[3]), split=0.5)
    p.line(21, 10, 28, 14, IRON[4])
    for k in range(3):
        m = M().oval(4 + k, 15 + k * 2, 24 - k * 2, 13 - k)
        sh(p, m, ramp((176, 140, 90)), split=0.9)
    inner = M().oval(10, 20, 12, 5)
    p.draw.ellipse((10, 20, 21, 25), fill=(30, 22, 30))
    for x in range(6, 28, 3):
        p.px(x, 16 + abs(x - 16) // 4, (130, 100, 60))
    p.line(24, 27, 31, 31, WINE[3])
    p.outline(SHADOW)
    return p


def sprout(seed: int) -> Pix:
    """A seedling in a pool of water with a packet of seeds beside it."""
    p = new(seed)
    water = M().poly([(3, 25), (9, 21), (17, 24), (25, 20), (33, 24), (33, 33), (3, 33)])
    sh(p, water, ramp((60, 150, 140)), split=0.6)
    p.hline(6, 26, 8, GLASS[4])
    p.hline(20, 28, 9, GLASS[4])
    p.vline(11, 14, 10, MOSS[2])
    for pts in ([(11, 15), (4, 11), (6, 17)], [(11, 14), (18, 7), (17, 15)]):
        m = M().poly(pts)
        sh(p, m, ramp(MOSS[3]))
    pk = M().poly([(21, 4), (31, 6), (30, 20), (20, 18)])
    sh(p, pk, ramp(PARCHMENT[3]))
    p.ellipse(23, 8, 5, 5, WINE[3])
    p.px(24, 9, WINE[4])
    p.hline(22, 15, 7, PARCHMENT[1])
    p.outline(SHADOW)
    return p


def vials(seed: int) -> Pix:
    """Two corked test tubes of green liquid in front of a purple coral."""
    p = new(seed)
    coral = M().poly([(2, 20), (6, 8), (9, 14), (12, 3), (16, 12), (20, 6), (22, 18), (30, 10), (33, 22), (28, 30), (4, 30)])
    sh(p, coral, ramp((140, 60, 150)), split=0.6)
    for x in (9, 20):
        tube = M().rrect(x, 8, 8, 24, 3)
        sh(p, tube, ramp(GLASS[4]))
        liquid = M().rect(x + 1, 17, 6, 14)
        paint(p, liquid, ramp((70, 190, 90)))
        p.px(x + 2, 12, CREAM)
        p.vline(x + 2, 18, 5, CREAM)
        p.rect(x + 1, 5, 6, 4, LEATHER[3])
    p.outline(SHADOW)
    return p


def pane(glass: Color, cracks: Color, seed: int, frame: Color = IRON[2]) -> Pix:
    """A cracked pane of leaded glass: a stone-grey frame, a star-shaped break."""
    p = new(seed)
    outer = M().poly([(5, 6), (30, 4), (32, 29), (6, 31)])
    sh(p, outer, ramp(frame))
    inner = M().poly([(8, 9), (28, 7), (29, 26), (9, 28)])
    paint(p, inner, ramp(glass), split=0.7)
    p.draw.line((8, 9, 29, 26), fill=ramp(glass)[4])
    for x1, y1 in ((8, 12), (12, 28), (22, 7), (29, 14), (28, 26), (20, 28)):
        p.line(19, 17, x1, y1, cracks)
    p.line(19, 17, 24, 22, cracks)
    for r in (3, 6):
        p.px(19 + r, 17 - r // 2, cracks)
    p.px(19, 17, CREAM)
    p.outline(SHADOW)
    return p


def lantern_spark(seed: int) -> Pix:
    """An iron-bound oil canister with a glowing green band and sparks leaping off it."""
    p = new(seed)
    body = M().poly([(11, 28), (11, 11), (14, 8), (22, 8), (25, 11), (25, 28), (22, 31), (14, 31)])
    sh(p, body, ramp(IRON[2]), split=0.6)
    band = M().rect(11, 17, 14, 6)
    paint(p, band, ramp((70, 190, 90)))
    p.hline(12, 18, 10, (200, 255, 170))
    p.rect(15, 5, 6, 3, BRASS[3])
    for pts in ([(4, 8), (8, 14), (6, 14), (9, 20)], [(31, 6), (28, 12), (30, 12), (26, 19)]):
        thick(p, pts, 1, FLAME[4])
    p.px(4, 20, FLAME[3])
    p.px(32, 22, FLAME[3])
    p.outline(SHADOW)
    return p


def framed(shine: bool, seed: int) -> Pix:
    """A framed mirror with green arrows pointing out of two of its corners."""
    p = new(seed)
    fr = M().rrect(6, 9, 22, 20, 1)
    sh(p, fr, ramp((120, 96, 120)), split=0.7)
    glass = M().rect(9, 12, 16, 14)
    paint(p, glass, ramp(GLASS[2]))
    p.line(10, 24, 16, 14, GLASS[4])
    p.line(14, 25, 20, 15, GLASS[3])
    if shine:
        p.hline(11, 13, 6, CREAM)
    for pts, tip in (([(25, 12), (31, 6)], (31, 6)), ([(9, 26), (3, 32)], (3, 32))):
        thick(p, pts, 2, (110, 220, 100))
    p.poly([(26, 4), (33, 4), (33, 11)], (110, 220, 100))
    p.poly([(2, 34), (2, 27), (9, 34)], (110, 220, 100))
    p.outline(SHADOW)
    return p


def tube(seed: int) -> Pix:
    """A teal glass phial lying on a slant, brass-capped, with bubbles round it."""
    p = new(seed)
    t = M().poly([(8, 27), (6, 21), (22, 7), (28, 10), (31, 17), (14, 30)])
    sh(p, t, ramp((70, 170, 160)), split=0.55)
    p.line(10, 24, 22, 11, CREAM)
    for x, y in ((9, 4), (4, 9), (30, 27), (26, 31), (31, 6)):
        p.ellipse(x - 2, y - 2, 5, 5, GLASS[4])
        p.px(x - 1, y - 1, CREAM)
    p.poly([(21, 5), (25, 4), (30, 9), (28, 12)], BRASS[3])
    p.outline(SHADOW)
    return p


def fish_pic(count: int, seed: int) -> Pix:
    """One fish, a pair chasing each other, or three swimming in a ring."""
    p = new(seed)
    spots = {1: [(18, 18, 0)], 2: [(14, 12, 0), (21, 25, 1)], 3: [(18, 8, 0), (9, 23, 1), (26, 24, 2)]}[count]
    big = count == 1
    for cx, cy, k in spots:
        w, h = (28, 13) if big else (17, 9)
        flip = k % 2 == 1
        body = M().oval(cx - w // 2, cy - h // 2, w, h)
        sh(p, body, ramp((168, 184, 200)), split=0.5)
        belly = M().oval(cx - w // 2 + 2, cy + 1, w - 6, h // 2 - 1)
        paint(p, belly, ramp(CREAM))
        tx = cx + (w // 2 - 1 if flip else -w // 2 + 1)
        d = 1 if flip else -1
        p.poly([(tx, cy), (tx + d * 6, cy - h // 2 - 1), (tx + d * 6, cy + h // 2 + 1)], (140, 156, 176))
        ex = cx + (-w // 4 if flip else w // 4)
        p.px(ex, cy - 1, SHADOW)
        p.px(ex - (1 if not flip else -1), cy - 2, CREAM)
        p.hline(cx - 3, cy - h // 2 + 1, 6, (110, 130, 160))
    p.outline(SHADOW)
    return p


def cabinet(base: Color, glass: bool, seed: int) -> Pix:
    """An apothecary cupboard: a painted case, a panel of little drawers or a glazed front with shelves of jars."""
    p = new(seed)
    case = M().rrect(8, 3, 21, 30, 1)
    sh(p, case, ramp(base), split=0.75)
    if glass:
        win = M().rect(11, 6, 15, 16)
        paint(p, win, ramp(GLASS[2]))
        for y, col in ((10, WINE[3]), (15, (230, 190, 70)), (20, (70, 190, 90))):
            p.hline(11, y + 2, 15, PALE_WOOD[3])
            for x in (13, 18, 23):
                p.rect(x - 1, y - 2, 4, 4, col)
                p.px(x - 1, y - 2, CREAM)
        p.hline(12, 7, 5, CREAM)
    else:
        for yy in (6, 13):
            for xx in (11, 19):
                d = M().rect(xx, yy, 7, 6)
                paint(p, d, ramp(mix(base, CREAM, 0.1)))
                p.hline(xx + 2, yy + 3, 3, BRASS[3])
    p.rect(11, 24, 15, 7, ramp(base)[1])
    p.hline(11, 24, 15, ramp(base)[3])
    p.rect(14, 26, 9, 3, BRASS[2])
    p.px(18, 27, BRASS[4])
    p.outline(SHADOW)
    return p


def crate(base: Color, seed: int) -> Pix:
    """A lidded purple-painted coffer seen from the front and above."""
    p = new(seed)
    top = M().poly([(5, 14), (13, 8), (31, 8), (31, 14)])
    sh(p, top, ramp(mix(base, CREAM, 0.15)))
    front = M().rect(5, 14, 26, 15)
    sh(p, front, ramp(base), split=0.7)
    for x in (8, 26):
        p.rect(x, 14, 3, 15, IRON[2])
        p.px(x + 1, 17, BRASS[4])
        p.px(x + 1, 26, BRASS[4])
    p.rect(16, 16, 5, 6, BRASS[3])
    p.hline(16, 16, 5, BRASS[4])
    p.px(18, 19, SHADOW)
    p.outline(SHADOW)
    return p


def kettle(seed: int) -> Pix:
    """A teal-glazed cask on a trestle with a bung and a brass tap."""
    p = new(seed)
    cask = M().poly([(8, 6), (28, 6), (31, 17), (28, 28), (8, 28), (5, 17)])
    sh(p, cask, ramp((50, 140, 130)), split=0.6)
    for y in (10, 24):
        p.hline(7, y, 22, IRON[2])
        p.hline(7, y - 1, 22, IRON[4])
    p.vline(14, 7, 21, ramp((50, 140, 130))[1])
    p.vline(22, 7, 21, ramp((50, 140, 130))[3])
    p.ellipse(16, 14, 5, 5, WOOD[1])
    p.rect(30, 20, 4, 3, BRASS[3])
    p.poly([(5, 30), (31, 30), (29, 33), (7, 33)], WOOD[3])
    p.outline(SHADOW)
    return p


def vine(seed: int) -> Pix:
    """A climbing vine twisting round a pale string, with leaves."""
    p = new(seed)
    for t in range(0, 30):
        y = 3 + t
        x1 = round(18 + 7 * math.sin(t / 3.2))
        x2 = round(18 - 7 * math.sin(t / 3.2))
        p.px(x1, y, MOSS[3])
        p.px(x1 + 1, y, MOSS[2])
        p.px(x2, y, (200, 190, 150))
        p.px(x2 - 1, y, (150, 140, 100))
    for x, y, d in ((14, 9, -1), (22, 15, 1), (13, 22, -1), (23, 27, 1)):
        m = M().poly([(x, y), (x + d * 8, y - 4), (x + d * 9, y + 2), (x + d * 3, y + 5)])
        sh(p, m, ramp(MOSS[3]))
    p.poly([(15, 33), (21, 33), (20, 30), (16, 30)], LEATHER[2])
    p.outline(SHADOW)
    return p


def emblem(seed: int) -> Pix:
    """A red ringed seal: a target ring with a shield and a flask in it."""
    p = new(seed)
    ring = M().oval(3, 3, 30, 30)
    sh(p, ring, ramp((170, 44, 50)), split=0.6)
    inner = M().oval(8, 8, 20, 20)
    p.draw.ellipse((8, 8, 27, 27), fill=(40, 24, 34))
    p.hline(1, 18, 5, (240, 120, 100))
    p.hline(30, 18, 5, (240, 120, 100))
    p.vline(18, 1, 5, (240, 120, 100))
    p.vline(18, 30, 5, (240, 120, 100))
    sh(p, M().poly([(12, 11), (17, 11), (17, 21), (14, 24), (11, 21)]), ramp(IRON[3]), edge=False)
    sh(p, M().poly([(18, 17), (25, 17), (26, 24), (18, 24)]), ramp(WOOD[3]), edge=False)
    p.hline(19, 14, 5, ramp(WOOD[3])[1])
    p.outline(SHADOW)
    return p


def crossbow(bolts: int, seed: int) -> Pix:
    """A small crossbow with iron prod and wooden stock, and `bolts` quarrels beside it."""
    p = new(seed)
    stock = M().poly([(4, 21), (20, 16), (33, 19), (33, 23), (18, 25), (8, 29), (4, 26)])
    sh(p, stock, ramp(WOOD[3]), split=0.6)
    prod = M().poly([(8, 8), (11, 7), (13, 22), (10, 22)])
    sh(p, prod, ramp(IRON[3]))
    p.line(10, 8, 22, 18, LINEN[2])
    p.line(10, 22, 22, 18, LINEN[2])
    p.hline(20, 17, 12, IRON[4])
    for k in range(bolts):
        x = 22 + k * 3
        p.line(x, 29, x - 1, 33, BRASS[3])
        p.px(x, 28, IRON[4])
        p.px(x - 1, 33, WINE[3])
    p.outline(SHADOW)
    return p


def cheese(seed: int) -> Pix:
    """A wedge and a block of hard cheese with holes."""
    p = new(seed)
    blk = M().poly([(15, 16), (30, 14), (31, 28), (16, 30)])
    sh(p, blk, ramp((236, 190, 70)), split=0.6)
    wedge = M().poly([(3, 24), (12, 11), (22, 16), (22, 29), (3, 29)])
    sh(p, wedge, ramp((250, 214, 100)), split=0.6)
    for x, y in ((8, 22), (14, 24), (25, 20), (26, 25)):
        p.ellipse(x, y, 3, 2, (170, 120, 40))
    p.hline(4, 24, 18, (200, 150, 50))
    p.outline(SHADOW)
    return p


def wine(seed: int) -> Pix:
    """A tilted goblet pouring red wine, with a bunch of grapes."""
    p = new(seed)
    for x, y in ((6, 22), (11, 22), (16, 22), (8, 27), (13, 27), (10, 31), (4, 27)):
        g = M().oval(x - 3, y - 3, 7, 7)
        sh(p, g, ramp((110, 40, 120)), edge=False)
        p.px(x - 1, y - 1, (200, 150, 210))
    p.line(10, 19, 12, 14, MOSS[3])
    cup = M().poly([(18, 4), (31, 8), (29, 15), (23, 18), (17, 13)])
    sh(p, cup, ramp(GLASS[4]))
    p.poly([(21, 8), (28, 10), (27, 14), (23, 16), (20, 12)], (150, 40, 52))
    p.line(24, 18, 22, 27, GLASS[4])
    p.hline(19, 28, 8, GLASS[4])
    p.line(18, 5, 14, 3, (180, 40, 50))
    p.line(14, 3, 12, 8, (180, 40, 50))
    p.outline(SHADOW)
    return p


# ---------------------------------------------------------------------------------------------- the sheet

GREY, CREAMH, PURPLE = (120, 116, 124), (200, 190, 166), (130, 70, 150)

# the 49 cells in reading order: (x, y, drawing)
CELLS: Final[Sequence[tuple[int, int, Callable[[], Pix]]]] = (
    (16, 16, lambda: chest((200, 170, 120), 1)),
    (16, 64, lambda: hat(GREY, WINE[3], 2)),
    (64, 64, lambda: hat(CREAMH, MOSS[3], 3)),
    (112, 64, lambda: hat(PURPLE, BRASS[3], 4)),
    (276, 44, lambda: imp(5)),
    (331, 44, lambda: flask((80, 190, 70), 6, True)),
    (386, 44, lambda: quill((150, 80, 170), 7)),
    (441, 44, lambda: rocks(8)),
    (496, 44, lambda: spectacles((120, 200, 200), 9, False)),
    (551, 44, lambda: spectacles((120, 200, 200), 10, True)),
    (276, 121, lambda: receipt(11)),
    (331, 121, lambda: tag(12)),
    (386, 121, lambda: coins(True, 13)),
    (441, 121, lambda: coins(False, 14)),
    (496, 121, lambda: cloak(GREY, 15)),
    (551, 121, lambda: cloak(CREAMH, 16)),
    (606, 121, lambda: cloak(PURPLE, 17)),
    (277, 198, lambda: book((170, 50, 50), 18)),
    (332, 198, lambda: mask_icon((50, 50, 60), 19)),
    (387, 198, lambda: beret((170, 40, 46), 20)),
    (438, 197, lambda: mask_icon(CREAMH, 21)),
    (495, 197, lambda: mask_icon(PURPLE, 22)),
    (276, 275, lambda: hat((176, 44, 52), (60, 120, 170), 23, True)),
    (331, 275, lambda: herbs(24)),
    (386, 275, lambda: chest((176, 56, 52), 25)),
    (441, 275, lambda: rope(26)),
    (496, 275, lambda: sprout(27)),
    (551, 275, lambda: vials(28)),
    (172, 332, lambda: pane((150, 190, 210), (240, 240, 255), 29, STONE[3])),
    (223, 332, lambda: pane((170, 150, 130), (250, 235, 200), 30, STONE[3])),
    (276, 352, lambda: pane((50, 70, 120), (250, 190, 90), 31)),
    (331, 352, lambda: lantern_spark(32)),
    (386, 352, lambda: framed(False, 33)),
    (441, 352, lambda: framed(True, 34)),
    (496, 352, lambda: tube(35)),
    (551, 352, lambda: tube(36)),
    (114, 380, lambda: fish_pic(1, 37)),
    (168, 380, lambda: fish_pic(2, 38)),
    (223, 380, lambda: fish_pic(3, 39)),
    (11, 429, lambda: cabinet((130, 60, 140), False, 40)),
    (64, 429, lambda: cabinet((150, 90, 150), True, 41)),
    (114, 429, lambda: crate((120, 60, 140), 42)),
    (168, 429, lambda: kettle(43)),
    (223, 429, lambda: vine(44)),
    (277, 429, lambda: emblem(45)),
    (332, 429, lambda: crossbow(1, 46)),
    (387, 429, lambda: crossbow(2, 47)),
    (442, 429, lambda: crossbow(3, 48)),
    (496, 429, lambda: cheese(49)),
    (550, 429, lambda: wine(50)),
)

PLATE: Final = ((22, 15, 25), (34, 25, 38), (48, 38, 52))


def plate(icon: Pix) -> Image.Image:
    """A dark tile (a lit top-left edge, a deep bottom-right edge) carrying the icon."""
    t = Pix(S, S, fill=PLATE[1])
    t.dither(1, 1, S - 2, S - 2, PLATE[0], 0.12)
    t.hline(0, 0, S, PLATE[2])
    t.vline(0, 0, S, PLATE[2])
    t.hline(0, S - 1, S, PLATE[0])
    t.vline(S - 1, 0, S, PLATE[0])
    t.paste(icon, 0, 0)
    return t.im


def network_icons() -> Image.Image:
    sheet = Pix(682, 493)
    for x, y, draw in CELLS:
        sheet.paste(plate(draw()), x, y)
    return sheet.im
