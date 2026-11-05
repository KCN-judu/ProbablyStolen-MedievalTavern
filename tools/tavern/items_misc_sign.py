"""Shop signs of the tavern (the `items_sign` sprites): the department signs become painted hanging boards in an oak
frame with iron corner studs, each with one pictogram in cream paint; the neon lamps become iron-hooded glass lanterns
whose glass is dark when off and glows purple, teal or amber when lit. Lettering (hiring, water) uses the 5x7 font.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image

import font
from itemkit_misc import conform, PURPLE, RUST, TEAL, Shape, bitmap, fill, five, part, rivet, stud
from palette import BRASS, FLAME, IRON, MOSS, NAVY, OAK, PARCHMENT, SHADOW, WINE, WOOD
from pix import Pix, Ramp, mix

CREAM = PARCHMENT[4]
ICON: Final[Mapping[str, tuple[str, ...]]] = {
    "grapes": ("....3.33..", "...3333...", ".12112112.", ".11211211.", "..121121..", "..112112..", "...1211...", "...1121...", "....11....", "....1....."),
    "loaf": ("...111111...", "..12222221..", ".1221221221.", "122222222221", "122222222221", "111111111111", ".1222222221.", "..11111111.."),
    "mug": ("..1111111...", "..1222221111", "..1222221..1", "..1222221..1", "..1222221..1", "..1222221111", "..1222221...", "...111111..."),
    "crossbow": ("11..........11", "11........11.", ".11......11..", "..11....11...", "...111111....", ".....22......", ".....22......", ".....22......", "....1221.....", "....1111....."),
    "pot": ("..11111111..", ".1111111111.", "1.12222221.1", "1.22222222.1", ".1222222221.", ".1222222221.", "..11111111..", "..11....11.."),
    "ingot": ("..1111111...", ".122222221..", "12.......21.", "1....12....1", ".....12.....", ".....12.....", ".....12.....", ".....12.....", ".....11....."),
    "cross": ("....111....", "....121....", "....121....", "1111121111.", "12222222221", "1111121111.", "....121....", "....121....", "....111...."),
    "bottle": ("...1111...", "...1221...", "...1221...", "..122221..", ".12222221.", ".12222221.", ".12122121.", ".12222221.", ".12222221.", ".12222221.", ".11111111."),
    "pick": ("..11111111..", ".12222222211", "11.......221", "1.....12..11", "......12....", "......12....", "......12....", "......12....", "......11...."),
}


def board(w: int, h: int, field: Ramp, seed: int) -> Pix:
    """A painted board: a rounded oak frame, a coloured field with a sheen, iron corner studs."""
    p = Pix(w, h, seed=seed)
    part(p, OAK, lambda s: s.rrect(0, 1, w, h - 2).px(0, 2, False))
    p.px(0, 2, SHADOW)
    inner = Shape(w, h).rrect(3, 4, w - 6, h - 8)
    fill(p, inner, five(field), outline=SHADOW, soft=0.7)
    p.dither(5, 6, w - 14, 4, five(field)[4], 0.3)
    for x, y in ((1, 2), (w - 3, 2), (1, h - 4), (w - 3, h - 4)):
        stud(p, x, y, IRON)
    return p


def paint(p: Pix, name: str, x: int, y: int, ink: Ramp, scale: int = 2) -> None:
    """The pictogram: dark drop shade first, then cream paint with a light core."""
    rows = ICON[name]
    shade = {"1": SHADOW, "2": SHADOW, "3": SHADOW}
    bitmap(p, rows, x + 1, y + 1, shade, scale)
    bitmap(p, rows, x, y, {"1": CREAM, "2": PARCHMENT[2], "3": MOSS[3]}, scale)


def sign(icon_name: str, field: Ramp, ink: Ramp, seed: int, size: tuple[int, int] = (32, 32)) -> Image.Image:
    p = board(size[0], size[1], field, seed)
    rows = ICON[icon_name]
    w, h = len(rows[0]) * 2, len(rows) * 2
    paint(p, icon_name, (size[0] - w) // 2, (size[1] - h) // 2, ink)
    return p.im


def long_crossbow() -> Image.Image:
    """The rifle sign: a crossbow seen from the side (stock, prod, string and a laid bolt) on a wide wine-red board."""
    p = board(64, 32, WINE, 70)
    for dx, dy, c in ((1, 1, SHADOW), (0, 0, None)):
        def ink(col, c=c):
            return c if c is not None else col
        p.line(49 + dx, 7 + dy, 55 + dx, 16 + dy, ink(CREAM))
        p.line(55 + dx, 16 + dy, 49 + dx, 25 + dy, ink(CREAM))
        p.line(50 + dx, 7 + dy, 56 + dx, 16 + dy, ink(PARCHMENT[2]))
        p.line(56 + dx, 16 + dy, 50 + dx, 25 + dy, ink(PARCHMENT[2]))
        p.rect(9 + dx, 14 + dy, 36, 5, ink(WOOD[4]))
        p.poly([(5 + dx, 12 + dy), (11 + dx, 14 + dy), (11 + dx, 22 + dy), (5 + dx, 22 + dy)], ink(WOOD[3]))
    p.hline(9, 14, 36, WOOD[4])
    p.hline(9, 15, 36, WOOD[3])
    p.hline(9, 17, 36, WOOD[2])
    p.hline(9, 18, 36, WOOD[1])
    p.line(50, 7, 41, 16, PARCHMENT[1])
    p.line(41, 16, 50, 25, PARCHMENT[1])
    p.hline(24, 13, 30, CREAM)
    p.px(54, 13, PARCHMENT[2])
    p.rect(26, 19, 3, 5, IRON[3])
    p.rect(26, 24, 5, 1, IRON[3])
    return p.im


def lettered(text: str, field: Ramp, seed: int, size: tuple[int, int], scale: int = 2, ink=CREAM) -> Image.Image:
    p = board(size[0], size[1], field, seed)
    tw, th = font.width(text, scale), 7 * scale
    x, y = (size[0] - tw) // 2, (size[1] - th) // 2
    font.write(p, x + 1, y + 1, text, SHADOW, scale)
    font.write(p, x, y, text, ink, scale)
    return p.im


def water_plain() -> Image.Image:
    """The unlit water sign is lettered boldly (the word is the picture)."""
    p = Pix(64, 32, seed=75)
    part(p, OAK, lambda s: s.rrect(0, 1, 63, 30))
    inner = Shape(64, 32).rrect(2, 3, 59, 26)
    fill(p, inner, five(TEAL), outline=SHADOW, soft=0.7)
    tw = font.width("WATER", 2)
    x = (63 - tw) // 2 + 1
    font.write(p, x + 1, 10, "WATER", SHADOW, 2)
    font.write(p, x, 9, "WATER", CREAM, 2)
    return p.im


def lamp(glass: Ramp | None, alt: bool = False, seed: int = 1) -> Image.Image:
    """An iron-hooded standing lantern 26x40: cone hood, glass case with a candle, stem and foot; lit glass glows `glass`."""
    p = Pix(32, 48, seed=seed)
    lit = glass is not None
    if lit:
        # light spills round the case under the hood
        p.glow(16, 29, 12, glass[3] if not alt else glass[4], 0.75 if not alt else 0.5)
    hood = part(p, IRON, lambda s: s.poly([(14, 5), (17, 5), (28, 21), (4, 21)]))
    p.hline(5, 20, 22, BRASS[3] if lit else IRON[3])
    p.hline(5, 21, 22, SHADOW)
    p.rect(14, 5, 4, 1, BRASS[3])
    # glass case
    case = Shape(32, 48).rect(8, 22, 16, 12)
    fill(p, case, five(glass) if lit else (IRON[0], IRON[1], IRON[1], IRON[2], IRON[3]), soft=0.6 if lit else 0.4)
    if lit:
        g = five(glass)
        p.rect(10, 24, 12, 8, g[3] if not alt else g[4])
        p.dither(10, 24, 12, 8, g[4], 0.5)
        p.rect(14, 25, 4, 6, FLAME[3])
        p.rect(15, 26, 2, 3, FLAME[4])
    else:
        p.rect(10, 24, 12, 8, IRON[0])
        p.dither(10, 24, 5, 4, IRON[2], 0.4)
    for x in (8, 15, 22):
        p.vline(x, 22, 12, IRON[2])
    p.vline(8, 22, 12, IRON[3])
    p.hline(8, 33, 16, IRON[1])
    part(p, IRON, lambda s: s.rect(14, 34, 4, 4), soft=1.0)
    part(p, IRON, lambda s: s.ellipse(8, 37, 17, 5), soft=1.0)
    p.hline(11, 38, 7, IRON[4])
    return p.im


def _assets() -> dict[str, Callable[[], Image.Image]]:
    a: dict[str, Callable[[], Image.Image]] = {}

    def add(name: str, fn: Callable[[], Image.Image]) -> None:
        a[f"items~items_sign@{name}.png"] = fn

    add("berry_sign", partial(sign, "grapes", PURPLE, PURPLE, 60))
    add("food_sign", partial(sign, "loaf", RUST, RUST, 61))
    add("gun_sign", partial(sign, "crossbow", WINE, WINE, 62))
    add("gun_sign2", long_crossbow)
    add("household_sign", partial(sign, "pot", TEAL, TEAL, 63))
    add("material_sign", partial(sign, "ingot", RUST, RUST, 64))
    add("medical_sign", partial(sign, "cross", MOSS, MOSS, 65))
    add("water_sign", partial(sign, "bottle", TEAL, TEAL, 66, (32, 48)))
    add("water_on", water_plain)
    add("hiring_sign", partial(lettered, "HIRING", RUST, 71, (96, 32), 2))
    add("items_sign_1", partial(lettered, "HIRING", WINE, 72, (96, 32), 2, PARCHMENT[3]))
    add("black_lamp", partial(lamp, None, False, 80))
    glows = (PURPLE, TEAL, RUST)
    for i, g in enumerate(glows, 1):
        add(f"black_lamp_on_{i}", partial(lamp, g, False, 80 + i))
        add(f"black_lamp_on_alt_{i}", partial(lamp, g, True, 84 + i))
    return a


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = conform(_assets())
