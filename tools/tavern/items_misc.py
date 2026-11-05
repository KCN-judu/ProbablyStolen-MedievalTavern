"""Paper, tokens and curios of the tavern (the `items_misc` sprites): guild tags for the keycards, plaques for the small
cards, bound tomes and stitched manuals, sealed sheets, framed certificates, bottles, the signet coin.

A keycard becomes a painted guild tag with a brass seal; a magnetic card, a stamped plaque; a booklet, a parchment
sheet with a wax seal. Each picture keeps the size and the occupied area of the original it replaces.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image

from itemkit_misc import (conform, CLAY, CLEAR_GLASS, INK, PURPLE, RUST, SILVER, SKY, SLATE, STEEL, TEAL, Shape, bitmap, fill, five, grain, icon,
                          inside, part, rivet, scribble, stud, wax_seal)
from palette import (BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE,
                     WOOD)
from pix import Color, Pix, Ramp, mix

Box = tuple[int, int, int, int]


# ---------------------------------------------------------------------------------------------- tags and plaques

def brass_medallion(p: Pix, cx: int, cy: int, r: int = 3) -> None:
    """The round brass seal that stands where the original has its chip."""
    s = Shape(p.w, p.h)
    s.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1)
    fill(p, s, BRASS)
    p.px(cx, cy, BRASS[1])
    p.px(cx - 1, cy - 1, BRASS[4])
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        if r >= 3:
            p.px(cx + dx * 2, cy + dy * 2, BRASS[1])


def guild_tag(ramp: Ramp, emblem: str | None, accent: Color, bars: int = 0, seed: int = 1, flat: bool = False) -> Image.Image:
    """A 26x18 painted guild tag: coloured field, engraved emblem, brass seal, a stamped line of marks, rivets."""
    ramp = five(ramp)
    p = Pix(32, 32, seed=seed)
    part(p, ramp, lambda s: s.rrect(3, 7, 26, 18), soft=1.0 if not flat else 0.5)
    # a pale sheen across the upper left, as on lacquer
    p.dither(5, 9, 10, 3, ramp[3], 0.35)
    p.frame(5, 9, 22, 14, ramp[1])
    if emblem is not None:
        icon(p, emblem, 7, 10, PARCHMENT[3], PARCHMENT[4], ramp[0])
    for i in range(bars):
        p.rect(8 + i * 3, 11, 2, 8, ramp[4])
        p.rect(9 + i * 3, 12, 1, 8, ramp[0])
    brass_medallion(p, 23, 13)
    for i in range(5):
        p.hline(7 + i * 3, 20, 2, ramp[1])
        p.hline(7 + i * 3, 21, 2, ramp[3])
    for x, y in ((6, 10), (26, 10), (6, 22), (26, 22)):
        rivet(p, x, y)
    _ = accent
    return p.im


def blank_tag(wip: bool = False) -> Image.Image:
    p = Pix(32, 32, seed=7)
    part(p, SKY, lambda s: s.rrect(3, 7, 26, 18), soft=1.0)
    p.dither(5, 9, 12, 3, SKY[4], 0.4)
    p.frame(5, 9, 22, 14, SKY[2])
    brass_medallion(p, 23, 13)
    p.hline(7, 20, 12, SKY[2])
    for x, y in ((6, 10), (26, 10), (6, 22), (26, 22)):
        rivet(p, x, y)
    if wip:
        # a moss-green pennant tied to the left edge marks the unfinished tag
        part(p, MOSS, lambda s: s.poly([(2, 14), (8, 15), (8, 22), (5, 20), (2, 22)]))
        p.px(4, 16, MOSS[3])
    return p.im


def small_plaque(ramp: Ramp, emblem: str, seed: int = 1, ink: Color | None = None) -> Image.Image:
    """A 24x14 stamped plaque for the small cards: field, inner frame, one pictogram."""
    ramp = five(ramp)
    p = Pix(32, 16, seed=seed)
    part(p, ramp, lambda s: s.rrect(4, 1, 24, 14))
    p.frame(6, 3, 20, 10, ramp[1])
    p.dither(7, 4, 8, 2, ramp[3], 0.4)
    c = ink or ramp[4]
    icon(p, emblem, 11, 4, c, c, ramp[0])
    for x, y in ((5, 2), (26, 2), (5, 13), (26, 13)):
        rivet(p, x, y)
    return p.im


def permit(n: int) -> Image.Image:
    """Hunting permit: wine-red tag with tally bars (one, two, three) and a crossbow burned in."""
    p = Pix(32, 32, seed=30 + n)
    part(p, WINE, lambda s: s.rrect(3, 7, 26, 18))
    p.dither(5, 9, 12, 3, WINE[4], 0.3)
    p.frame(5, 9, 22, 14, WINE[1])
    for i in range(n):
        p.rect(8 + i * 4, 11, 2, 9, WINE[4])
        p.rect(9 + i * 4, 12, 1, 9, WINE[0])
        p.px(8 + i * 4, 11, PARCHMENT[3])
    brass_medallion(p, 23, 13)
    p.hline(16, 20, 8, WINE[1])
    p.hline(16, 21, 8, WINE[3])
    for x, y in ((6, 10), (26, 10), (6, 22), (26, 22)):
        rivet(p, x, y)
    return p.im


def ticket(stack: bool = False) -> Image.Image:
    """Scratch lot: a purple ticket with a gold border, a gilt crest and three silver scratch discs."""
    p = Pix(32, 32, seed=11)

    def one(x: int, y: int, h: int) -> None:
        part(p, PURPLE, lambda s: s.rrect(x, y, 26, h))
        p.frame(x + 2, y + 2, 22, h - 4, BRASS[2])
        p.frame(x + 3, y + 3, 20, h - 6, BRASS[1])
        p.px(x + 3, y + 3, BRASS[3])
        if h > 12:
            icon(p, "crown", x + 9, y + 5, BRASS[3], BRASS[4], PURPLE[0])
            for i in range(3):
                s = Shape(32, 32)
                s.ellipse(x + 6 + i * 6, y + h - 9, 5, 5)
                fill(p, s, SILVER, outline=PURPLE[0])
    if stack:
        one(3, 12, 17)
        one(3, 7, 17)
        one(3, 3, 26)
    else:
        one(3, 5, 22)
    return p.im


# ---------------------------------------------------------------------------------------------- books

def tome(ramp: Ramp, seed: int, mark: str) -> Image.Image:
    """A bound tome 28x43: spine bands on the left, brass corners, a title plate, page edges below."""
    ramp = five(ramp)
    p = Pix(32, 48, seed=seed)
    # the page block shows under the cover, at the bottom and right edge
    part(p, PARCHMENT, lambda s: s.rect(4, 41, 25, 5))
    for y in (43, 45):
        p.hline(5, y, 23, PARCHMENT[1])
    part(p, ramp, lambda s: s.rrect(2, 3, 28, 40))
    part(p, ramp, lambda s: s.rect(2, 3, 5, 40), soft=1.2, bias=-1)
    for y in (8, 17, 26, 35):
        p.hline(3, y, 3, ramp[4])
        p.hline(3, y + 1, 3, ramp[0])
    p.vline(7, 4, 38, ramp[0])
    p.frame(9, 6, 18, 33, ramp[1])
    part(p, PARCHMENT, lambda s: s.rect(11, 9, 14, 9), soft=0.5)
    scribble(p, 12, 11, 12, 3, INK, gap=3, seed=seed)
    icon(p, mark, 13, 22, ramp[4], ramp[4], ramp[0])
    for x, y in ((9, 4), (27, 4), (9, 40), (27, 40)):
        p.rect(x - 1, y - 1, 3, 3, BRASS[2])
        p.px(x - 1, y - 1, BRASS[4])
        p.px(x + 1, y + 1, BRASS[0])
    return p.im


def manual(ramp: Ramp, seed: int, mark: str) -> Image.Image:
    """A stitched manual 28x39: a limp cover laced with a leather thong along the left edge."""
    ramp = five(ramp)
    p = Pix(32, 48, seed=seed)
    part(p, PARCHMENT, lambda s: s.rect(5, 40, 24, 4))
    p.hline(6, 42, 22, PARCHMENT[1])
    part(p, ramp, lambda s: s.rrect(2, 5, 28, 37))
    p.frame(8, 8, 19, 31, ramp[1])
    part(p, PARCHMENT, lambda s: s.rect(10, 11, 15, 8), soft=0.5)
    scribble(p, 11, 13, 13, 3, INK, gap=2, seed=seed)
    icon(p, mark, 13, 23, ramp[4], ramp[4], ramp[0])
    for y in range(8, 40, 5):
        p.rect(3, y, 4, 2, LEATHER[1])
        p.hline(3, y, 4, LEATHER[3])
        p.px(5, y + 1, SHADOW)
        p.vline(4, y + 2, 2, LEATHER[2])
    return p.im


# ---------------------------------------------------------------------------------------------- sheets

def sheet(seal: Ramp | None = None, ribbon: Ramp | None = None, heading: bool = True, seed: int = 1,
          bullets: Ramp | None = NAVY) -> Image.Image:
    """A parchment guide 21x30 with a heading, columns of unreadable writing and a seal in the corner."""
    p = Pix(32, 32, seed=seed)
    part(p, PARCHMENT, lambda s: s.rect(5, 1, 21, 30), soft=0.6)
    p.px(5, 1, PARCHMENT[0])
    p.px(25, 1, PARCHMENT[0])
    if heading:
        p.rect(8, 4, 15, 2, INK)
        p.hline(10, 7, 11, PARCHMENT[0])
    scribble(p, 8, 10, 15, 3, PARCHMENT[0], gap=3, seed=seed)
    if bullets is not None:
        for j in range(2):
            p.rect(8, 20 + j * 3, 2, 1, bullets[2])
            p.hline(11, 20 + j * 3, 9 - j * 3, bullets[1])
    scribble(p, 8, 19, 15, 0, INK)
    if ribbon is not None:
        p.vline(14, 0, 4, ribbon[3])
        p.vline(15, 0, 4, ribbon[3])
        p.rect(13, 3, 4, 2, ribbon[2])
    if seal is not None:
        wax_seal(p, 20, 26, 3, seal)
    return p.im


def deed() -> Image.Image:
    p = Pix(32, 32, seed=21)
    part(p, PARCHMENT, lambda s: s.rect(6, 1, 21, 30), soft=0.6)
    p.rect(9, 4, 15, 2, INK)
    p.hline(11, 7, 11, PARCHMENT[0])
    scribble(p, 9, 10, 15, 5, PARCHMENT[0], gap=3, seed=5)
    # a flourished signature
    p.line(9, 27, 12, 25, INK)
    p.line(12, 25, 14, 28, INK)
    p.hline(9, 28, 6, PARCHMENT[1])
    p.hline(9, 29, 6, PARCHMENT[1])
    wax_seal(p, 21, 25, 3, WINE)
    p.vline(20, 29, 2, WINE[3])
    p.vline(22, 29, 2, WINE[2])
    return p.im


def handnote() -> Image.Image:
    """A scrap torn from a ledger, curled at the corners, with a few lines of pencil."""
    p = Pix(32, 32, seed=22)
    pts = [(7, 4), (13, 3), (18, 4), (25, 3), (26, 10), (25, 17), (26, 24), (22, 28), (16, 27), (11, 28), (6, 25), (7, 17), (6, 10)]
    part(p, PARCHMENT, lambda s: s.poly(pts), soft=0.5)
    scribble(p, 9, 7, 13, 6, PARCHMENT[0], gap=3, seed=9)
    p.dither(18, 20, 7, 7, PARCHMENT[1], 0.4)
    p.px(8, 4, PARCHMENT[4])
    p.px(25, 27, PARCHMENT[0])
    return p.im


def slip() -> Image.Image:
    """A paper receipt strip 12x16 with a torn edge below and two stamped bars."""
    p = Pix(16, 16, seed=23)
    part(p, PARCHMENT, lambda s: s.poly([(2, 0), (13, 0), (13, 14), (11, 15), (9, 14), (7, 15), (5, 14), (3, 15), (2, 14)]), soft=0.5)
    p.rect(4, 2, 8, 2, INK)
    scribble(p, 4, 6, 8, 3, PARCHMENT[0], gap=2, seed=2)
    p.rect(4, 12, 4, 1, INK)
    return p.im


def sec_slip() -> Image.Image:
    p = Pix(32, 16, seed=24)
    part(p, PARCHMENT, lambda s: s.rect(1, 1, 30, 14), soft=0.6)
    p.frame(3, 3, 26, 10, PARCHMENT[1])
    scribble(p, 5, 5, 14, 3, PARCHMENT[0], gap=3, seed=4)
    p.line(7, 11, 15, 11, INK)
    wax_seal(p, 24, 8, 4, WINE)
    p.vline(22, 12, 3, WINE[3])
    p.vline(26, 12, 3, WINE[2])
    return p.im


def cert(frame: Ramp, seal: Ramp, seed: int) -> Image.Image:
    """A framed certificate 40x30: moulded frame, parchment with a heading, writing lines and a seal with ribbon."""
    p = Pix(48, 32, seed=seed)
    part(p, frame, lambda s: s.rect(4, 1, 40, 30))
    p.frame(6, 3, 36, 26, frame[1])
    part(p, PARCHMENT, lambda s: s.rect(7, 4, 34, 24), soft=0.5)
    p.rect(14, 7, 20, 2, INK)
    p.hline(17, 10, 14, PARCHMENT[0])
    scribble(p, 11, 13, 26, 4, PARCHMENT[0], gap=3, seed=seed)
    p.line(11, 25, 16, 25, INK)
    p.px(13, 24, INK)
    wax_seal(p, 33, 24, 3, seal)
    p.vline(32, 26, 2, seal[3])
    p.vline(34, 26, 2, seal[2])
    for x, y in ((5, 2), (42, 2), (5, 29), (42, 29)):
        stud(p, x - 1 if x > 20 else x, y - 1 if y < 10 else y - 1, BRASS)
    return p.im


# ---------------------------------------------------------------------------------------------- curios

def perfume() -> Image.Image:
    """A scent bottle 20x40: faceted glass, amber essence, brass collar, cork and a silk tag."""
    p = Pix(32, 48, seed=31)
    part(p, CLEAR_GLASS, lambda s: s.rrect(6, 17, 20, 27), soft=1.0)
    part(p, CLEAR_GLASS, lambda s: s.rect(12, 11, 8, 7), soft=1.0)
    # the essence fills the lower three quarters
    for y in range(22, 43):
        for x in range(8, 24):
            if p.get(x, y)[3]:
                p.px(x, y, FLAME[1] if (x + y) % 5 == 0 and y > 36 else (FLAME[2] if x < 14 else FLAME[1]))
    p.hline(8, 22, 16, FLAME[3])
    p.vline(8, 23, 18, FLAME[3])
    p.vline(9, 24, 14, FLAME[3])
    p.hline(8, 42, 16, FLAME[0])
    p.vline(23, 24, 18, FLAME[0])
    p.dither(16, 25, 7, 16, FLAME[0], 0.3)
    p.vline(10, 19, 3, CLEAR_GLASS[4])
    part(p, BRASS, lambda s: s.rect(10, 8, 12, 4), soft=1.0)
    part(p, WOOD, lambda s: s.rrect(11, 4, 10, 5), soft=0.8)
    grain(p, Shape(32, 48).rect(11, 4, 10, 5), 11, 4, 10, 5, WOOD[1], count=2)
    part(p, PARCHMENT, lambda s: s.rect(11, 29, 10, 9), soft=0.5)
    scribble(p, 12, 31, 8, 2, INK, gap=3, seed=6)
    return p.im


def luck_bottle() -> Image.Image:
    """An empty tall glass phial, corked, with a bright rim and a long reflection."""
    p = Pix(16, 32, seed=32)
    part(p, CLEAR_GLASS, lambda s: s.rrect(2, 9, 12, 23), soft=1.0)
    part(p, CLEAR_GLASS, lambda s: s.rect(5, 3, 6, 7), soft=1.0)
    part(p, WOOD, lambda s: s.rrect(5, 0, 6, 4), soft=0.8)
    p.rect(4, 8, 8, 2, BRASS[2])
    p.hline(4, 8, 8, BRASS[4])
    p.vline(4, 12, 15, CLEAR_GLASS[4])
    p.vline(5, 13, 8, CLEAR_GLASS[4])
    p.dither(9, 12, 4, 18, CLEAR_GLASS[1], 0.5)
    p.hline(3, 30, 10, CLEAR_GLASS[4])
    p.px(6, 4, WOOD[4])
    return p.im


def luck_label() -> Image.Image:
    """The loose parts of the luck charm: a red silk bow above and a parchment label with a clover below."""
    p = Pix(16, 32, seed=33)
    part(p, WINE, lambda s: s.poly([(2, 3), (7, 5), (8, 4), (9, 5), (14, 3), (13, 10), (9, 8), (8, 9), (7, 8), (3, 10)]))
    p.px(8, 6, WINE[1])
    part(p, WINE, lambda s: s.rect(6, 9, 4, 7), soft=1.0, bias=-1)
    part(p, PARCHMENT, lambda s: s.poly([(2, 17), (14, 16), (13, 24), (14, 26), (3, 26), (2, 22)]), soft=0.5)
    for x, y in ((6, 19), (9, 19), (6, 22), (9, 22)):
        p.rect(x, y, 2, 2, MOSS[3])
    p.vline(8, 21, 4, MOSS[1])
    p.px(5, 18, MOSS[1])
    return p.im


def torch() -> Image.Image:
    """A pitch torch lying on its side: a leather-wrapped haft and a tarred head, ember-lit at the tip."""
    p = Pix(48, 16, seed=34)
    part(p, WOOD, lambda s: s.rect(3, 6, 28, 5), soft=1.0, bias=1)
    for x in range(6, 28, 5):
        p.rect(x, 6, 2, 5, LEATHER[2])
        p.px(x, 6, LEATHER[3])
        p.px(x + 1, 10, LEATHER[0])
    part(p, IRON, lambda s: s.rect(31, 3, 5, 11), soft=1.0)
    p.vline(33, 4, 9, IRON[4])
    part(p, WOOD, lambda s: s.poly([(36, 2), (44, 1), (45, 4), (45, 12), (44, 15), (36, 14)]), soft=1.0, bias=-1)
    p.dither(37, 3, 7, 10, SHADOW, 0.4)
    for y in (4, 7, 10, 13):
        p.hline(37, y, 7, FLAME[0])
    p.vline(44, 4, 9, FLAME[1])
    p.vline(45, 5, 7, FLAME[2])
    p.px(45, 8, FLAME[3])
    p.px(37, 3, FLAME[1])
    p.rect(4, 7, 2, 1, WOOD[4])
    return p.im


def food_stamp() -> Image.Image:
    p = Pix(32, 32, seed=35)
    part(p, SKY, lambda s: s.rrect(3, 8, 26, 19))
    p.frame(5, 10, 22, 15, SKY[1])
    p.dither(6, 11, 10, 3, SKY[4], 0.4)
    icon(p, "loaf", 11, 13, LEATHER[3], FLAME[3], LEATHER[0])
    p.hline(8, 23, 16, SKY[1])
    for x, y in ((6, 11), (25, 11), (6, 23), (25, 23)):
        rivet(p, x, y)
    return p.im


def folio() -> Image.Image:
    """A red leather document folio 40x28 with a tab, a strap and a brass clasp."""
    p = Pix(48, 32, seed=36)
    part(p, WINE, lambda s: s.rrect(4, 6, 40, 24))
    part(p, WINE, lambda s: s.poly([(4, 6), (4, 3), (18, 2), (22, 6)]), bias=1)
    p.frame(6, 9, 36, 19, WINE[1])
    p.dither(7, 10, 14, 4, WINE[4], 0.3)
    part(p, LEATHER, lambda s: s.rect(30, 6, 5, 24), soft=1.0)
    p.vline(32, 8, 20, LEATHER[3])
    part(p, BRASS, lambda s: s.rect(29, 14, 7, 6), soft=1.0)
    p.px(32, 17, BRASS[0])
    p.hline(30, 15, 5, BRASS[4])
    for x, y in ((7, 9), (41, 9), (7, 27), (41, 27)):
        rivet(p, x, y)
    return p.im


def abacus() -> Image.Image:
    """The exchange directive as a counting frame 30x42: a wooden frame with six wires of coloured beads."""
    p = Pix(32, 48, seed=37)
    part(p, WOOD, lambda s: s.rect(1, 3, 30, 42))
    part(p, PARCHMENT, lambda s: s.rect(4, 6, 24, 9), soft=0.5)
    scribble(p, 6, 8, 20, 2, INK, gap=3, seed=3)
    cols = (WINE, BRASS, MOSS, WINE, BRASS, MOSS)
    for i in range(6):
        y = 19 + i * 4
        p.hline(3, y + 1, 26, IRON[1])
        base = cols[i]
        n = 3 + (i * 2) % 5
        x = 4
        for _ in range(n):
            s = Shape(32, 48)
            s.rrect(x, y - 1, 4, 4)
            fill(p, s, base, outline=SHADOW, soft=1.0)
            x += 4
        x2 = 26 - 4 * (7 - n)
        for _ in range(min(2, 7 - n)):
            s = Shape(32, 48)
            s.rrect(x2, y - 1, 4, 4)
            fill(p, s, base, outline=SHADOW, soft=1.0)
            x2 += 4
    grain(p, Shape(32, 48).rect(1, 3, 30, 3), 1, 3, 30, 3, WOOD[1], count=3)
    return p.im


def checker() -> Image.Image:
    """A small iron plaque with a brass crest of studs (the mark that is checked)."""
    p = Pix(16, 16, seed=38)
    part(p, IRON, lambda s: s.poly([(2, 3), (13, 3), (13, 10), (8, 14), (2, 10)]))
    for x, y in ((7, 5), (6, 7), (8, 7), (5, 9), (7, 9), (9, 9)):
        p.px(x, y, BRASS[3])
    p.px(7, 5, BRASS[4])
    return p.im


def horn() -> Image.Image:
    """The relay as a brass signal horn: a curled tube that widens into a bell."""
    p = Pix(16, 16, seed=39)
    part(p, BRASS, lambda s: s.poly([(1, 10), (3, 8), (9, 5), (13, 3), (14, 7), (13, 12), (9, 12), (4, 13), (1, 12)]))
    p.px(14, 7, SHADOW)
    part(p, BRASS, lambda s: s.ellipse(11, 3, 4, 9), bias=-1)
    p.vline(13, 5, 5, BRASS[0])
    p.hline(4, 9, 6, BRASS[4])
    p.px(2, 11, BRASS[0])
    return p.im


def coin() -> Image.Image:
    """The coin: a stamped gold disc, ridged rim, a raised field and a crowned crest, lit upper left."""
    p = Pix(16, 16, seed=40)
    s = Shape(16, 16)
    s.ellipse(1, 1, 14, 14)
    fill(p, s, BRASS)
    ring = Shape(16, 16).ellipse(3, 3, 10, 10)
    inner = Shape(16, 16).ellipse(4, 4, 8, 8)
    for y in range(16):
        for x in range(16):
            if ring.has(x, y):
                p.px(x, y, BRASS[3] if inner.has(x, y) else (BRASS[1] if x + y > 14 else BRASS[2]))
    bitmap(p, ["1.11.1", "111111", "122221", "111111"], 5, 6, {"1": BRASS[1], "2": BRASS[2]})
    for x, y in ((4, 3), (3, 4), (2, 6), (6, 2)):
        p.px(x, y, BRASS[4])
    p.px(13, 11, BRASS[0])
    p.px(11, 13, BRASS[0])
    return p.im


# ---------------------------------------------------------------------------------------------- the catalog

def _assets() -> dict[str, Callable[[], Image.Image]]:
    a: dict[str, Callable[[], Image.Image]] = {}

    def add(name: str, fn: Callable[[], Image.Image]) -> None:
        a[f"items~items_misc@{name}.png"] = fn

    tags = {
        "command_keycard": (NAVY, "crown"), "eng_card": (RUST, "hammer"), "med_card": (TEAL, "cross"),
        "sci_card": (PURPLE, "flask"), "ser_card": (MOSS, "mug"), "sup_card": (SLATE, "barrel"),
        "sec_keycard": (WINE, "sword"),
    }
    for i, (name, (ramp, emb)) in enumerate(tags.items()):
        add(name, partial(guild_tag, ramp, emb, BRASS[3], 0, 50 + i))
    add("blank_card", partial(blank_tag, False))
    add("blank_card_wip", partial(blank_tag, True))
    for n in (1, 2, 3):
        add(f"permit_gun_{n}", partial(permit, n))
    add("scratch", partial(ticket, False))
    add("scratch_stack", partial(ticket, True))
    plaques = {
        "card_brewer": (WINE, "mug", PARCHMENT[3]), "card_chem": (PARCHMENT, "flask", WINE[2]),
        "card_mining": (SLATE, "pick", BRASS[3]), "card_pharma": (LINEN, "cross", MOSS[2]),
        "card_rev": (MOSS, "banner", PARCHMENT[3]), "card_wild": (IRON, "crown", FLAME[2]),
    }
    for i, (name, (ramp, emb, ink)) in enumerate(plaques.items()):
        add(name, partial(small_plaque, ramp, emb, 60 + i, ink))
    books = {
        "book1": TEAL, "book2": CLAY, "book3": MOSS, "book4": SLATE, "book5": PURPLE,
    }
    for i, (name, ramp) in enumerate(books.items()):
        add(name, partial(tome, ramp, 70 + i, ("cross", "wheat", "pick", "key", "flask")[i]))
    for i, (name, ramp) in enumerate({"manual1": TEAL, "manual4": SLATE, "manual5": CLAY}.items()):
        add(name, partial(manual, ramp, 80 + i, ("hammer", "key", "wheat")[i]))
    add("guide0", partial(sheet, None, None, True, 90))
    add("guide1", partial(sheet, WINE, None, True, 91))
    add("guide2", partial(sheet, TEAL, None, True, 92))
    add("guide3", partial(sheet, MOSS, None, True, 93))
    add("guide5", partial(sheet, PURPLE, None, True, 94))
    add("aug_id_guide", partial(sheet, None, WINE, True, 95))
    add("deed", deed)
    add("handnote", handnote)
    add("slip", slip)
    add("sec_slip", sec_slip)
    add("cert1", partial(cert, OAK, WINE, 101))
    add("cert2", partial(cert, PALE_WOOD, WINE, 102))
    add("cert3", partial(cert, WOOD, NAVY, 103))
    add("cert4", partial(cert, BRASS, TEAL, 104))
    add("eleanor_perfume", perfume)
    add("liquid_luck_bottle", luck_bottle)
    add("liquid_luck_label", luck_label)
    add("flashlight3", torch)
    add("food_stamp", food_stamp)
    add("intel_sec", folio)
    add("exchange_directive", abacus)
    add("republic_logo_checker", checker)
    add("republic_transmitter", horn)
    add("the_coin", coin)
    return a


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = conform(_assets())
