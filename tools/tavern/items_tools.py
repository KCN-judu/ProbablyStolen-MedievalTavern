"""Tool-family items, part 4 (and the entry module of the family): the things of the `itematlas` sheet: books, pages, a news
sheet, the wanted poster, a medal, powder kegs, smoke and flash pots, the unknown-item tile.

The rest of the family lives in items_tools_power (batteries, chips, modules, boosters), items_tools_hand (hand tools,
cases, hands, piles) and items_tools_mach (machines, bays, hoppers); the helpers are in itemkit_tools."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

import font
from itemkit_tools import (AMETHYST, COPPER, INK, SLATE, TEAL, ball, bitmap, corners, finish, grain, hcyl, r5, ring, rivets, slab,
                           solid, sparkle, strap_h, strap_v, vcyl)
from palette import BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, STONE, WINE, WOOD
from pix import CLEAR, Pix, Ramp, mix, rgb

INKB = rgb("#2e2a3e")


def tome(cover: Ramp, thick: int, ribbon: bool, seed: int, w: int, h: int, x0: int, y0: int, name: str = "") -> Image.Image:
    """A bound book seen from the front: leather spine and brass corners, a brass title plate, a block of page edges."""
    p = Pix(32, 48, seed=seed)
    x, y = x0 + 1, y0 + 1
    bw, bh = w - 2, h - 2
    # the page block shows under and to the right of the cover
    p.rect(x + 2, y + 2, bw - 1, bh - 1, LINEN[2])
    for k in range(thick):
        p.hline(x + 3, y + bh - 1 - k, bw - 2, LINEN[3] if k % 2 == 0 else LINEN[1])
    slab(p, x, y, bw - thick, bh - thick, cover)
    c = r5(cover)
    p.rect(x, y, 5, bh - thick, c[1])                                  # spine
    p.vline(x, y, bh - thick, c[2])
    p.vline(x + 4, y, bh - thick, c[0])
    for yy in (y + 4, y + bh - thick - 5):
        p.hline(x, yy, 5, BRASS[2])
        p.hline(x, yy + 1, 5, BRASS[1])
    p.hline(x + 7, y + 2, bw - thick - 10, c[3])
    # title plate with an engraved line of marks
    px_, py_ = x + 8, y + 8
    slab(p, px_, py_, bw - thick - 13, 8, BRASS)
    for i in range(0, bw - thick - 17, 3):
        p.hline(px_ + 2 + i, py_ + 3, 2, BRASS[0])
        p.px(px_ + 2 + i, py_ + 5, BRASS[1])
    rivets(p, ((px_ + 1, py_ + 1), (px_ + bw - thick - 15, py_ + 1)))
    # lower emblem: a cross of stitching
    cx, cy = x + 5 + (bw - thick - 5) // 2, y + 22
    for dx, dy in ((0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (-3, 0), (-2, 0), (-1, 0), (1, 0), (2, 0), (3, 0)):
        p.px(cx + dx, cy + dy, c[4] if dx + dy < 0 else c[3])
    p.px(x + bw - thick - 3, y + bh - thick - 3, BRASS[3])
    p.px(x + 6, y + bh - thick - 3, BRASS[3])
    p.px(x + bw - thick - 3, y + 2, BRASS[3])
    if ribbon:
        p.vline(x + bw - 12, y + bh - thick, 3, WINE[3])
        p.vline(x + bw - 11, y + bh - thick, 3, WINE[2])
    return finish(p)


def book1() -> Image.Image:
    return tome(TEAL, 2, False, 1, 28, 43, 2, 3)


def tutorial_book(full: bool) -> Image.Image:
    return tome(NAVY, 3 if not full else 5, full, 2, 28, 38, 2, 5)


def page(tutorial: bool) -> Image.Image:
    """A loose sheet: ruled lines and a wine margin; the tutorial page has a heading block and ticked bullets."""
    p = Pix(32, 32, seed=3 + tutorial)
    solid(p, [(7, 3), (24, 3), (26, 5), (26, 28), (7, 28)], PARCHMENT)
    p.rect(8, 4, 17, 24, PARCHMENT[3])
    p.dither(8, 4, 17, 24, PARCHMENT[2], 0.15)
    p.vline(11, 4, 24, WINE[3] if not tutorial else NAVY[3])
    p.poly([(23, 3), (26, 5), (23, 7)], PARCHMENT[1])
    p.line(23, 4, 25, 6, PARCHMENT[0])
    rows = (8, 11, 14, 17, 20, 23, 26)
    if tutorial:
        p.rect(13, 6, 9, 3, NAVY[2])
        p.hline(13, 6, 9, NAVY[3])
        for y in (12, 16, 20, 24):
            p.px(13, y, NAVY[3])
            p.px(14, y + 1, NAVY[3])
            p.hline(16, y + 1, 6 if y != 20 else 4, INK)
    else:
        for y in rows:
            ln = 12 if y not in (14, 26) else 8
            p.hline(13, y, ln, INK)
            p.hline(13, y + 1, ln, mix(INK, PARCHMENT[3], 0.78))
    return finish(p)


def news() -> Image.Image:
    """A town-crier's broadsheet: a heavy masthead, a woodcut and columns of small print, folded once."""
    p = Pix(48, 32, seed=5)
    slab(p, 3, 3, 42, 27, PARCHMENT)
    p.rect(4, 4, 40, 25, PARCHMENT[3])
    p.dither(4, 4, 40, 25, PARCHMENT[2], 0.15)
    x = 12
    for dx in (0, 1):                                               # a heavy masthead: the 5x7 face struck twice
        font.write(p, 11 + dx, 7, "NEWS", INK, 1)
    p.hline(10, 15, 26, INK)
    p.hline(5, 5, 38, INK)
    p.hline(5, 17, 38, INK)
    p.hline(5, 18, 38, mix(INK, PARCHMENT[3], 0.5))
    slab(p, 6, 20, 11, 8, PARCHMENT)
    p.rect(7, 21, 9, 6, PARCHMENT[2])
    p.ellipse(9, 22, 4, 4, INK)
    p.hline(7, 26, 9, INK)
    for y in (20, 22, 24, 26):
        p.hline(19, y, 10, INK if y % 4 == 0 else mix(INK, PARCHMENT[3], 0.4))
        p.hline(31, y, 11, mix(INK, PARCHMENT[3], 0.2 if y % 4 else 0))
    p.vline(30, 20, 8, PARCHMENT[1])
    p.vline(24, 4, 25, PARCHMENT[2]) if False else None
    p.hline(5, 28, 38, PARCHMENT[1])
    return finish(p)


MINI = {"W": ("#.#", "#.#", "#.#", "###", "#.#"), "A": (".#.", "#.#", "###", "#.#", "#.#"),
        "N": ("#.#", "###", "###", "#.#", "#.#"), "T": ("###", ".#.", ".#.", ".#.", ".#."),
        "E": ("###", "#..", "##.", "#..", "###"), "D": ("##.", "#.#", "#.#", "#.#", "##.")}


def wanted() -> Image.Image:
    """A wanted poster: tacked parchment, WANTED in heavy ink, six portrait frames with hooded silhouettes."""
    p = Pix(32, 48, seed=6)
    slab(p, 2, 4, 28, 40, PARCHMENT)
    p.rect(3, 5, 26, 38, PARCHMENT[3])
    p.dither(3, 5, 26, 38, PARCHMENT[2], 0.15)
    for k, ch in enumerate("WANTED"):
        bitmap(p, 5 + k * 4, 8, MINI[ch], {"#": INK})
    p.hline(4, 15, 24, INK)
    for j in range(3):
        for i in range(2):
            x, y = 5 + i * 12, 17 + j * 8
            p.rect(x, y, 10, 7, PARCHMENT[1])
            p.hline(x, y, 10, PARCHMENT[0])
            p.vline(x, y, 7, PARCHMENT[0])
            p.ellipse(x + 3, y + 1, 4, 4, INKB)
            p.rect(x + 2, y + 5, 6, 2, INKB)
            p.px(x + 4, y + 3, PARCHMENT[3]) if (i + j) % 2 else None
            p.px(x + 9, y, EMBER)
    for x, y in ((4, 5), (27, 5), (4, 41), (27, 41)):
        p.px(x, y, BRASS[3])
    return finish(p)


def medal() -> Image.Image:
    """A bronze medal on a wine-and-linen ribbon with a star in relief."""
    p = Pix(16, 32, seed=7)
    for x, c in ((5, WINE[2]), (6, WINE[3]), (7, LINEN[3]), (8, LINEN[3]), (9, WINE[3]), (10, WINE[1])):
        p.vline(x, 2, 13, c)
    p.hline(4, 2, 8, BRASS[2])
    p.hline(5, 14, 6, WINE[0])
    p.rect(7, 14, 2, 2, BRASS[2])
    ball(p, 2, 17, 12, COPPER)
    p.ellipse(4, 19, 8, 8, COPPER[1])
    p.ellipse(5, 20, 6, 6, COPPER[3])
    for x, y in ((8, 20), (7, 22), (8, 22), (9, 22), (6, 22), (10, 22), (7, 24), (9, 24), (8, 21)):
        p.px(x, y, COPPER[4])
    return finish(p)


def keg_bundle() -> Image.Image:
    """The explosive as three powder kegs lashed together with a rope and a burning fuse."""
    p = Pix(48, 48, seed=8)
    for x, y, h in ((3, 14, 27), (29, 14, 27), (16, 9, 32)):
        vcyl(p, x, y, 16, h, WOOD)
        p.ellipse(x, y - 3, 16, 7, WOOD[3])
        p.ellipse(x + 2, y - 2, 12, 4, WOOD[1])
        for yy in (y + 5, y + h - 7):
            p.hline(x, yy, 16, IRON[2])
            p.hline(x, yy + 1, 16, IRON[0])
            p.px(x + 2, yy, IRON[4])
        for xx in (x + 5, x + 10):
            p.vline(xx, y + 8, h - 16, WOOD[1])
        p.hline(x + 1, y + h - 1, 14, WOOD[0])
    for k, y in enumerate((24, 25, 26)):                              # lashing rope across all three
        p.hline(4, y + k, 40, LEATHER[3] if k != 1 else LEATHER[2])
    for x in range(5, 43, 3):
        p.px(x, 25, LINEN[1])
    p.rect(21, 14, 6, 5, PARCHMENT[3])
    p.hline(22, 16, 4, INK)
    p.px(23, 17, EMBER)
    p.line(24, 8, 28, 6, LINEN[2])                                       # fuse
    p.line(28, 6, 30, 7, LINEN[1])
    sparkle(p, 31, 6, FLAME[4])
    p.px(33, 4, FLAME[3])
    p.px(29, 3, FLAME[2])
    return finish(p)


def swatches() -> Image.Image:
    """A dyer's colour card: a wooden slip with four stripes of dyed wool."""
    p = Pix(16, 16, seed=9)
    slab(p, 3, 2, 10, 12, PALE_WOOD)
    for i, c in enumerate((WINE, MOSS, NAVY, (rgb("#3a2a10"), rgb("#7a5a1a"), rgb("#b08a2a"), rgb("#d8b456")))):
        p.rect(4 + i * 2, 3, 2, 10, r5(c)[3 if i % 2 == 0 else 2])
        p.vline(4 + i * 2, 3, 10, r5(c)[4])
    p.hline(3, 5, 10, PALE_WOOD[1])
    p.hline(3, 11, 10, PALE_WOOD[1])
    p.px(8, 2, BRASS[3])
    return finish(p)


def flash_pot() -> Image.Image:
    """A flash-powder pot: green-glazed clay with a corked neck and a lit fuse."""
    p = Pix(16, 32, seed=10)
    p.ellipse(3, 11, 11, 18, MOSS[1])
    vcyl(p, 3, 15, 11, 10, MOSS)
    p.ellipse(3, 11, 11, 10, MOSS[2])
    p.ellipse(3, 19, 11, 10, MOSS[1])
    vcyl(p, 3, 16, 11, 9, MOSS)
    p.rect(6, 7, 5, 6, MOSS[2])
    p.vline(6, 7, 6, MOSS[3])
    p.rect(5, 5, 7, 3, LEATHER[3])
    p.hline(5, 5, 7, LEATHER[3])
    p.hline(5, 7, 7, LEATHER[1])
    p.line(9, 4, 11, 2, LINEN[2])
    sparkle(p, 12, 2, FLAME[4])
    p.hline(4, 20, 9, MOSS[0])
    p.hline(5, 21, 7, MOSS[3])
    p.px(5, 14, MOSS[3])
    p.px(5, 15, MOSS[3])
    for x, y in ((7, 18), (10, 24)):
        p.px(x, y, mix(MOSS[3], (255, 240, 200), 0.3))
    return finish(p)


def smoke_pot() -> Image.Image:
    """A smoke pot: pale clay with a wine band, a corked top and a grey wisp."""
    p = Pix(16, 32, seed=11)
    vcyl(p, 3, 9, 10, 20, LINEN)
    p.ellipse(3, 7, 10, 5, LINEN[2])
    p.ellipse(4, 8, 8, 3, LINEN[1])
    p.rect(3, 17, 10, 6, WINE[2])
    for x in range(3, 13):
        p.vline(x, 17, 6, [WINE[3], WINE[3], WINE[2], WINE[2], WINE[2], WINE[2], WINE[1], WINE[1], WINE[0], WINE[0]][x - 3])
    p.hline(3, 17, 10, WINE[4])
    p.hline(3, 28, 10, LINEN[0])
    p.rect(6, 4, 4, 4, LEATHER[3])
    p.hline(6, 4, 4, LEATHER[3])
    p.hline(6, 7, 4, LEATHER[1])
    for x, y, c in ((8, 3, STONE[3]), (9, 2, STONE[4]), (7, 2, STONE[3]), (10, 1, STONE[3])):
        p.px(x, y, c)
    return finish(p)


def unknown() -> Image.Image:
    """An unknown item: a pale slate tile with an inked violet question mark."""
    p = Pix(16, 16, seed=12)
    slab(p, 3, 3, 10, 10, (rgb("#2b3a4e"), rgb("#4a6682"), rgb("#7a96b0"), rgb("#a4bcd0"), rgb("#d0e0ea")))
    corners(p, 3, 3, 10, 10, 1)
    bitmap(p, 6, 4, ("..##.", ".#..#", "....#", "...#.", "..#..", "..#..", ".....", "..#.."), {"#": AMETHYST[1]})
    return finish(p)


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "items~itematlas@book1.png": book1,
    "items~itematlas@c4.png": keg_bundle,
    "items~itematlas@cigarette_color_guide.png": swatches,
    "items~itematlas@newspaper.png": news,
    "items~itematlas@page3.png": partial(page, False),
    "items~itematlas@paper_wanted.png": wanted,
    "items~itematlas@scav_medal.png": medal,
    "items~itematlas@small_flash.png": flash_pot,
    "items~itematlas@small_smoke.png": smoke_pot,
    "items~itematlas@tutorial_book.png": partial(tutorial_book, False),
    "items~itematlas@tutorial_book_full.png": partial(tutorial_book, True),
    "items~itematlas@tutorial_page.png": partial(page, True),
    "items~itematlas@unknown.png": unknown,
}
