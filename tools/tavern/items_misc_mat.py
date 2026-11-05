"""Raw materials of the tavern (the `items_material` sprites): alchemist's flasks, clockwork brass, gems, crossbow parts,
bandage linen and herbs, an iron ingot, a tar barrel, ore lumps, a spool of blue thread, scrap iron, small crates.

Each picture is a little still life on the same footprint as the original's group of objects.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image

from itemkit_misc import (conform, CLAY, CLEAR_GLASS, PURPLE, RUST, SILVER, SKY, STEEL, TEAL, Shape, bitmap, fill, five, grain,
                          inside, part, rivet, scribble, stud, wax_seal)
from palette import (BRASS, FLAME, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, STONE, WINE,
                     WOOD)
from pix import Pix, Ramp

LEA = five(LEATHER)
LIN = five(LINEN)


def vial(p: Pix, x: int, y: int, w: int, h: int, liquid: Ramp, cork: bool = True, round_: bool = False) -> None:
    """A glass vial or round flask: pale glass, a coloured liquid in its lower part, a cork."""
    neck = max(2, w // 3)
    nx = x + (w - neck) // 2
    s = Shape(p.w, p.h)
    if round_:
        s.ellipse(x, y + h - w, w, w).rect(nx, y + 2, neck, h - w)
    else:
        s.rrect(x, y + 4, w, h - 4).rect(nx, y + 2, neck, 4)
    fill(p, s, CLEAR_GLASS)
    top = y + (h - w // 2 - 2 if round_ else y + 4 + (h - 4) // 3)
    lq = five(liquid)
    for yy in range(top, y + h):
        for xx in range(x, x + w):
            if s.has(xx, yy) and all(s.has(xx + dx, yy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                p.px(xx, yy, lq[3] if xx < x + w // 2 else lq[2])
    if top < y + h:
        for xx in range(x, x + w):
            if s.has(xx, top) and s.has(xx, top + 1):
                p.px(xx, top, lq[4])
    for yy in range(y + 5, y + h - 2):
        if s.has(x + 1, yy) and s.has(x, yy):
            p.px(x + 1, yy, CLEAR_GLASS[4]) if yy < top else None
    if cork:
        c = Shape(p.w, p.h).rect(nx, y, neck, 3)
        fill(p, c, WOOD)


def gear(p: Pix, cx: int, cy: int, r: int, teeth: int, ramp: Ramp = BRASS) -> None:
    s = Shape(p.w, p.h).ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1)
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        s.rect(cx + round((r + 1) * math.cos(a)) - 1, cy + round((r + 1) * math.sin(a)) - 1, 3, 3)
    fill(p, s, ramp)
    h = max(1, r // 3)
    p.ellipse(cx - h, cy - h, 2 * h + 1, 2 * h + 1, SHADOW)
    p.px(cx - h, cy - h, ramp[1])


def tray(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A shallow oak tray the things stand on."""
    s = part(p, WOOD, lambda s: s.rrect(x, y, w, h), soft=1.0)
    p.hline(x + 1, y + 1, w - 2, WOOD[4])
    grain(p, s, x, y + 2, w, h - 2, WOOD[1], count=4)


def spring(p: Pix, x: int, y: int, w: int, ramp: Ramp = STEEL) -> None:
    for i in range(0, w, 2):
        p.vline(x + i, y, 4, ramp[3])
        p.px(x + i, y + 3, ramp[1])
        p.vline(x + i + 1, y + 1, 3, ramp[2])


def alchemy(a: Ramp, b: Ramp, c: Ramp, flip: bool, seed: int) -> Image.Image:
    """Chemicals as an alchemist's set: a round retort flask, a rack of three phials and a small mortar on a tray."""
    p = Pix(48, 32, seed=seed)
    tray(p, 3, 25, 42, 6)
    fx, rx = (6, 22) if not flip else (28, 4)
    vial(p, fx, 5, 15, 21, a, round_=True)
    # the rack: a plank with three drilled holes holding the phials
    part(p, PALE_WOOD, lambda s: s.rect(rx, 21, 22, 5), soft=1.0)
    for i, liq in enumerate((b, c, a)):
        vial(p, rx + 1 + i * 7, 7 + (i % 2) * 2, 6, 15 - (i % 2) * 2, liq)
    for i in range(3):
        p.px(rx + 4 + i * 7, 23, SHADOW)
    if not flip:
        s = part(p, STONE, lambda s: s.poly([(38, 17), (45, 17), (44, 25), (39, 25)]), soft=1.0)
        p.hline(39, 18, 5, STONE[0])
        p.line(41, 13, 44, 20, WOOD[3])
    else:
        s = part(p, STONE, lambda s: s.poly([(21, 17), (28, 17), (27, 25), (22, 25)]), soft=1.0)
        p.hline(22, 18, 5, STONE[0])
    return p.im


def clockwork() -> Image.Image:
    """Electronics as clockwork: brass wheels of three sizes, a coiled spring, a few pins and a small dial."""
    p = Pix(48, 32, seed=101)
    gear(p, 14, 18, 11, 10)
    gear(p, 33, 12, 8, 8, SILVER)
    gear(p, 38, 25, 5, 7)
    spring(p, 22, 27, 12)
    for x, y in ((3, 28), (6, 30), (44, 4)):
        p.rect(x, y, 3, 1, STEEL[3])
        p.px(x, y, STEEL[4])
    return p.im


def wire_and_nails() -> Image.Image:
    """Electronics as the smith's small stock: a coil of copper wire, a reel of fine thread and a bunch of nails."""
    p = Pix(48, 32, seed=102)
    for i, (x, y) in enumerate(((3, 12), (4, 15))):
        s = Shape(48, 32).ellipse(x, y, 22, 14)
        fill(p, s, RUST if i == 0 else RUST)
    ring = Shape(48, 32).ellipse(8, 15, 12, 7)
    fill(p, ring, (SHADOW, SHADOW, RUST[0], RUST[1], RUST[0]), outline=SHADOW)
    for y in range(17, 27, 3):
        p.hline(6, y, 16, RUST[1])
    # a reel of thread
    part(p, WOOD, lambda s: s.rect(30, 6, 14, 3), soft=1.0)
    part(p, WOOD, lambda s: s.rect(30, 21, 14, 3), soft=1.0)
    part(p, NAVY, lambda s: s.rect(32, 9, 10, 12), soft=1.0)
    for y in range(10, 21, 2):
        p.hline(32, y, 10, NAVY[1])
    # nails
    for i in range(5):
        x = 28 + i * 3
        p.vline(x, 26, 5, IRON[3])
        p.hline(x - 1, 25, 3, IRON[4])
    return p.im


def gems() -> Image.Image:
    """Electronics as jeweller's stock: three cut gems, a silver ring, a chain and a pouch of beads."""
    p = Pix(48, 32, seed=103)
    part(p, LEA, lambda s: s.poly([(30, 12), (44, 12), (46, 28), (28, 28)]), soft=1.0)
    p.hline(30, 15, 15, SHADOW)
    p.hline(30, 14, 15, LEA[1])
    for x, y in ((33, 11), (36, 9), (39, 11)):
        part(p, SILVER, lambda s, x=x, y=y: s.ellipse(x, y, 3, 4), soft=1.0)
    for (x, y, ramp) in ((4, 8, TEAL), (13, 14, WINE), (6, 19, PURPLE)):
        part(p, ramp, lambda s, x=x, y=y: s.poly([(x + 3, y), (x + 9, y), (x + 12, y + 4), (x + 6, y + 10), (x, y + 4)]), soft=1.2)
        p.px(x + 4, y + 2, ramp[4])
        p.hline(x + 3, y + 4, 6, ramp[3])
    ring = Shape(48, 32).ellipse(19, 21, 10, 8)
    ring.ellipse(22, 23, 4, 4, on=False)
    fill(p, ring, SILVER)
    p.rect(22, 20, 4, 3, SILVER[4])
    p.px(23, 20, WINE[4])
    for i in range(7):
        p.px(3 + i * 3, 29 - (i % 2), SILVER[3])
    return p.im


def crate(w: int, h: int, seal: bool, seed: int) -> Image.Image:
    """A small timber crate with rope and iron strapping (the flux agent boxes); the bigger one has a wax seal."""
    size = (16, 16) if w <= 16 else (32, 32)
    p = Pix(*size, seed=seed)
    x0 = (size[0] - w) // 2
    y0 = (size[1] - h) // 2
    s = part(p, PALE_WOOD, lambda s: s.rect(x0, y0, w, h), soft=1.0)
    for y in range(y0 + 4, y0 + h - 2, 5 if w > 16 else 4):
        p.hline(x0 + 1, y, w - 2, PALE_WOOD[0])
    grain(p, s, x0, y0, w, h, PALE_WOOD[1], count=w // 2)
    for x in (x0, x0 + w - 4 if w > 16 else x0 + w - 3):
        part(p, IRON, lambda s, x=x: s.rect(x, y0, 4 if w > 16 else 3, h), soft=1.0)
        rivet(p, x + 1, y0 + 2)
        rivet(p, x + 1, y0 + h - 3)
    if seal:
        wax_seal(p, size[0] // 2, size[1] // 2, 4, MOSS)
        p.hline(x0 + 7, size[1] // 2 + 7, 12, LEA[3])
    else:
        p.hline(x0 + 4, size[1] // 2, w - 8, LEA[3])
    return p.im


def crossbow_parts() -> Image.Image:
    """Gun parts as crossbow parts: a bow prod, a trigger lock with its nut, a stock block and three bolts."""
    p = Pix(48, 32, seed=104)
    prod = Shape(48, 32).line(3, 6, 22, 3, 3).line(3, 6, 2, 13, 3)
    fill(p, prod, WOOD, soft=1.0)
    part(p, BRASS, lambda s: s.rect(5, 6, 3, 8), soft=1.0)
    p.line(3, 14, 21, 10, STEEL[2])
    part(p, WOOD, lambda s: s.poly([(25, 5), (47, 8), (47, 14), (40, 15), (30, 14), (25, 11)]), soft=1.0)
    part(p, IRON, lambda s: s.rect(30, 7, 8, 5), soft=1.0)
    p.rect(33, 8, 2, 2, BRASS[3])
    part(p, IRON, lambda s: s.poly([(4, 19), (14, 17), (17, 24), (9, 28), (4, 26)]), soft=1.0)
    p.rect(8, 21, 3, 3, BRASS[3])
    for i in range(3):
        y = 20 + i * 4
        p.hline(21, y, 24, WOOD[3])
        p.hline(21, y + 1, 24, WOOD[1])
        p.hline(43, y, 4, STEEL[3])
        p.px(45, y, STEEL[4])
        p.px(21, y, WINE[3])
        p.px(22, y - 1, WINE[3])
        p.px(22, y + 1, WINE[3])
    return p.im


def bandages(a: Ramp, b: Ramp, seed: int) -> Image.Image:
    """Medical supplies as linen: two rolled bandages, a stoppered phial, and a bundle of herbs tied with twine."""
    p = Pix(48, 32, seed=seed)
    for (x, y) in ((4, 8), (4, 18)):
        s = Shape(48, 32).rect(x, y, 15, 9)
        fill(p, s, LIN)
        e = Shape(48, 32).ellipse(x - 2, y, 7, 9)
        fill(p, e, LIN)
        p.ellipse(x - 1, y + 3, 3, 3, LIN[1])
        for xx in (x + 5, x + 9):
            p.vline(xx, y + 1, 7, LIN[1])
        p.hline(x + 2, y + 1, 12, LIN[3])
    vial(p, 24, 10, 8, 20, a)
    vial(p, 33, 14, 6, 16, b)
    # herbs
    for i in range(5):
        p.line(41 + i, 28, 40 + i * 2 - 1, 11 + i % 2 * 2, MOSS[2])
        p.px(40 + i * 2 - 1, 10 + i % 2 * 2, MOSS[3])
        p.px(39 + i * 2, 12 + i % 2 * 2, MOSS[3])
    p.hline(41, 22, 5, LEA[3])
    p.hline(41, 23, 5, LEA[1])
    return p.im


def ingot() -> Image.Image:
    """A forged iron ingot: sloped top face, flat front, dark flank, a stamped crest in the face."""
    p = Pix(48, 32, seed=105)
    part(p, SILVER, lambda s: s.poly([(8, 10), (14, 4), (44, 4), (38, 10)]), soft=0.0, bias=1)
    part(p, SILVER, lambda s: s.poly([(4, 28), (4, 12), (8, 10), (38, 10), (38, 28)]), soft=0.7)
    part(p, SILVER, lambda s: s.poly([(38, 10), (44, 4), (44, 22), (38, 28)]), soft=0.0, bias=-1)
    p.hline(10, 6, 28, SILVER[4])
    p.hline(6, 12, 30, SILVER[4])
    bitmap(p, ["1..1..1", "1111111", ".11111.", "..111.."], 15, 15, {"1": SILVER[1]})
    p.px(35, 12, SILVER[4])
    return p.im


def tar_barrel() -> Image.Image:
    """The waste barrel as a sealed tar cask: bulging oak staves, iron hoops, a green wax bung and a skull tag."""
    p = Pix(48, 64, seed=106)
    body = [(8, 8), (40, 8), (42, 20), (42, 46), (40, 58), (8, 58), (6, 46), (6, 20)]
    s = part(p, WOOD, lambda s: s.poly(body), soft=1.0)
    for x in range(12, 40, 6):
        p.vline(x, 10, 47, WOOD[0])
        p.vline(x + 1, 10, 47, WOOD[3])
    for y in (11, 24, 42, 55):
        part(p, IRON, lambda s, y=y: s.rect(6 if 20 < y < 50 else 8, y, 37 if 20 < y < 50 else 33, 4), soft=1.0)
        for x in (11, 24, 36):
            rivet(p, x, y + 1)
    top = Shape(48, 64).ellipse(6, 3, 36, 12)
    fill(p, top, WOOD, soft=1.0)
    p.ellipse(10, 5, 28, 8, WOOD[1])
    # green wax over the bung, dripping
    wax = Shape(48, 64).ellipse(14, 4, 20, 8)
    wax.rect(18, 10, 4, 10).rect(28, 10, 3, 14).rect(23, 10, 3, 6)
    fill(p, wax, MOSS, soft=1.0)
    p.hline(17, 6, 8, MOSS[3])
    p.ellipse(22, 7, 4, 3, MOSS[1])
    # skull tag
    part(p, PARCHMENT, lambda s: s.rect(17, 30, 14, 10), soft=0.5)
    bitmap(p, [".11111.", "1111111", "1.111.1", "1111111", ".11.11.", ".1.1.1."], 20, 31, {"1": SHADOW})
    p.px(21, 33, PARCHMENT[3])
    p.px(25, 33, PARCHMENT[3])
    grain(p, s, 8, 12, 32, 44, WOOD[1], horizontal=False, count=8)
    return p.im


def ore() -> Image.Image:
    """Ore: three rough lumps of grey rock with veins of copper and a glint of gold."""
    p = Pix(48, 32, seed=107)
    lumps = [
        ([(3, 28), (4, 20), (10, 13), (17, 12), (21, 18), (22, 28)], STONE),
        ([(20, 29), (22, 14), (27, 5), (34, 2), (40, 8), (44, 16), (45, 29)], STONE),
        ([(14, 14), (18, 9), (24, 8), (26, 14), (22, 18)], STONE),
    ]
    for pts, ramp in lumps:
        part(p, ramp, lambda s, pts=pts: s.poly(pts), soft=1.0)
    for pts in ([(5, 26), (10, 20), (14, 22)], [(27, 22), (33, 14), (38, 17)], [(30, 26), (36, 24), (40, 28)]):
        p.line(*pts[0], *pts[1], RUST[3])
        p.line(*pts[1], *pts[2], RUST[2])
    for x, y in ((12, 17), (34, 8), (28, 12), (41, 21)):
        p.rect(x, y, 2, 2, BRASS[4])
        p.px(x + 1, y + 1, BRASS[2])
    return p.im


def spool() -> Image.Image:
    """Printer plastic as thread: a wooden reel wound with blue wool, a loose end hanging down the front."""
    p = Pix(32, 32, seed=108)
    part(p, WOOD, lambda s: s.rrect(3, 5, 26, 5), soft=1.0)
    part(p, WOOD, lambda s: s.rrect(3, 25, 26, 5), soft=1.0)
    s = part(p, NAVY, lambda s: s.rect(6, 10, 20, 15), soft=1.0, bias=1)
    for y in range(11, 25, 2):
        p.hline(6, y, 20, NAVY[1])
        p.hline(6, y + 1, 20, NAVY[3])
    p.vline(7, 10, 15, NAVY[3])
    p.dither(17, 10, 9, 15, NAVY[0], 0.4)
    p.line(20, 22, 22, 28, NAVY[3])
    p.px(22, 29, NAVY[2])
    p.hline(5, 6, 22, WOOD[4])
    rivet(p, 5, 7)
    rivet(p, 26, 27)
    return p.im


def scrap(variant: int) -> Image.Image:
    """Scrap iron: bent plates, a horseshoe, a cracked cog and bent nails piled up; the second heap is rustier."""
    p = Pix(48, 32, seed=109 + variant)
    warm = variant == 1
    plate = RUST if warm else IRON
    plates = [
        [(2, 28), (4, 18), (16, 14), (24, 20), (22, 29)],
        [(16, 29), (20, 12), (34, 8), (44, 16), (46, 29)],
        [(8, 17), (14, 8), (26, 6), (30, 12), (20, 15)],
    ]
    for i, pts in enumerate(plates):
        part(p, plate if i != 2 else STEEL, lambda s, pts=pts: s.poly(pts), soft=1.0)
    shoe = Shape(48, 32).ellipse(30, 16, 14, 13)
    shoe.ellipse(34, 20, 6, 9, on=False)
    shoe.rect(33, 25, 8, 6, on=False)
    fill(p, shoe, STEEL if not warm else RUST)
    for x, y in ((32, 20), (41, 20), (31, 25), (43, 25)):
        p.px(x, y, SHADOW)
    gear(p, 12, 22, 5, 7, (BRASS[0], BRASS[1], BRASS[2], BRASS[3], BRASS[4]) if not warm else RUST)
    for i in range(4):
        p.line(24 + i * 3, 29, 26 + i * 3, 22 - (i % 2) * 2, IRON[3])
    return p.im


def _assets() -> dict[str, Callable[[], Image.Image]]:
    a: dict[str, Callable[[], Image.Image]] = {}

    def add(name: str, fn: Callable[[], Image.Image]) -> None:
        a[f"items~items_material@{name}.png"] = fn

    add("chemical1", partial(alchemy, MOSS, WINE, NAVY, False, 90))
    add("chemical2", partial(alchemy, PURPLE, RUST, TEAL, True, 91))
    add("electronic1", clockwork)
    add("electronic2", wire_and_nails)
    add("electronic3", gems)
    add("flux_agent", partial(crate, 14, 14, False, 92))
    add("flux_agent_advanced", partial(crate, 26, 26, True, 93))
    add("gun_part", crossbow_parts)
    add("med1", partial(bandages, TEAL, WINE, 94))
    add("med2", partial(bandages, WINE, MOSS, 95))
    add("metal_ingot", ingot)
    add("nuclear_waste", tar_barrel)
    add("ore1", ore)
    add("printer_plastic", spool)
    add("scrap_metal", partial(scrap, 0))
    add("scrap_metal_2", partial(scrap, 1))
    return a


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = conform(_assets())
