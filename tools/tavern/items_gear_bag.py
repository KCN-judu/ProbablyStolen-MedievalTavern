"""Leather rucksacks, a belt pouch, a satchel, and two children's packs (a wine-red one and an ochre bear)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_gear import (OCHRE, ROSE, dots, ell_m, finish, line_m, poly_m, puff, rect_m, rrect_m, stitches, stud, BONE)
from palette import BRASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, SHADOW, WINE, WOOD
from pix import Pix, Ramp

Draw = Callable[[], Image.Image]


def _f(n: str) -> str:
    return f"items~items_backpack2@{n}.png"


def buckle(p: Pix, x: int, y: int) -> None:
    p.rect(x, y, 5, 4, BRASS[2])
    p.frame(x, y, 5, 4, BRASS[1])
    p.hline(x, y, 5, BRASS[4])
    p.px(x + 2, y + 2, SHADOW)


def strap_v(p: Pix, x: int, y0: int, y1: int, w: int = 3) -> None:
    p.rect(x, y0, w, y1 - y0, LEATHER[1])
    p.vline(x, y0, y1 - y0, LEATHER[3])
    p.vline(x + w - 1, y0, y1 - y0, LEATHER[0])


def rucksack(w: int, h: int, box: tuple[int, int, int, int], leather: Ramp, seed: int, roll: str = "", side: bool = False,
             tall_pocket: bool = True) -> Image.Image:
    """A frame rucksack seen from the front: shoulder straps at the sides, a flap with two buckled straps, a front pocket;
    optionally side pouches and a bedroll lashed on top (roll='top') or underneath (roll='bottom')."""
    p = Pix(w, h, seed=seed)
    x0, y0, x1, y1 = box
    bw = x1 - x0
    top_pad = 12 if roll == "top" else 0
    bot_pad = 12 if roll == "bottom" else 0
    by0, by1 = y0 + top_pad + 5, y1 - bot_pad
    if roll == "top":
        puff(p, rrect_m(x0 + 4, y0 + 1, bw - 8, 13, 5), LINEN, r=5)
    if roll == "bottom":
        puff(p, rrect_m(x0 + 2, y1 - 11, bw - 4, 11, 5), LINEN, r=5)
    if side:
        puff(p, rrect_m(x0, by0 + (by1 - by0) // 2, 9, (by1 - by0) // 2 - 3, 3), leather, r=3)
        puff(p, rrect_m(x1 - 9, by0 + (by1 - by0) // 2, 9, (by1 - by0) // 2 - 3, 3), leather, r=3)
    sx = 4 if side else 0
    puff(p, rrect_m(x0 + sx, by0, bw - 2 * sx, by1 - by0 - 1, 5), leather, r=5, flat=0.2)
    puff(p, rrect_m(x0 + sx + 2, by0 - 3, bw - 2 * sx - 4, 5, 2), leather, r=2, bias=0.1)   # carrying loop base
    flap_h = (by1 - by0) * 5 // 12
    puff(p, poly_m([(x0 + sx + 1, by0 + 1), (x1 - sx - 2, by0 + 1), (x1 - sx - 2, by0 + flap_h - 2),
                    ((x0 + x1) // 2, by0 + flap_h + 3), (x0 + sx + 1, by0 + flap_h - 2)]), leather, r=4, bias=0.15)
    pk_y = by0 + flap_h + 6
    puff(p, rrect_m(x0 + sx + 4, pk_y, bw - 2 * sx - 8, by1 - pk_y - 5, 3), leather, r=3, bias=0.05)
    p = finish(p) and p
    cx = (x0 + x1) // 2
    for off in (-bw // 5, bw // 5):
        strap_v(p, cx + off - 1, by0 + 1, by0 + flap_h + 5)
        buckle(p, cx + off - 2, by0 + flap_h)
    stitches(p, x0 + sx + 4, pk_y + 1, x1 - sx - 5, pk_y + 1, LEATHER[0], 2)
    stitches(p, x0 + sx + 3, by0 + 2, x0 + sx + 3, by1 - 6, LEATHER[0], 3)
    stitches(p, x1 - sx - 4, by0 + 2, x1 - sx - 4, by1 - 6, LEATHER[0], 3)
    if tall_pocket:
        p.hline(cx - 5, pk_y + 4, 10, LEATHER[0])
        stud(p, x0 + sx + 6, pk_y + 3)
        stud(p, x1 - sx - 8, pk_y + 3)
    if roll:
        ry = y0 + 6 if roll == "top" else y1 - 6
        for x in (cx - bw // 5, cx + bw // 5):
            p.vline(x, ry - 5, 10, LEATHER[1])
            p.vline(x + 1, ry - 5, 10, LEATHER[3])
        p.vline(x0 + 8, ry - 4, 8, LINEN[1])
    return p.im


def pouch() -> Image.Image:
    """The fanny pack becomes a belt pouch: a belt across the top, a rounded flap, a brass buckle (48x32)."""
    p = Pix(48, 32, seed=5)
    puff(p, rrect_m(2, 3, 44, 5, 2), LEATHER, r=2)                           # belt
    puff(p, rrect_m(5, 7, 38, 23, 8), LEATHER, r=6, flat=0.1)
    puff(p, poly_m([(6, 8), (42, 8), (42, 15), (24, 21), (6, 15)]), LEATHER, r=4, bias=0.15)
    p = finish(p) and p
    stitches(p, 8, 10, 40, 10, LEATHER[0], 2)
    p.hline(3, 5, 42, LEATHER[3])
    p.hline(3, 7, 42, LEATHER[0])
    for x in (12, 36):
        stud(p, x, 4)
    p.rect(21, 17, 6, 6, BRASS[2])
    p.frame(21, 17, 6, 6, BRASS[1])
    p.hline(21, 17, 6, BRASS[4])
    p.rect(23, 19, 2, 2, SHADOW)
    p.vline(24, 13, 5, LEATHER[1])
    return p.im


def satchel() -> Image.Image:
    """A messenger satchel: a deep body, a flap with a buckle strap, a long shoulder strap looping over the top (48x48)."""
    p = Pix(48, 48, seed=6)
    puff(p, line_m([(8, 18), (12, 6), (24, 3), (36, 6), (40, 18)], 3), LEATHER, r=2)
    puff(p, rrect_m(3, 17, 42, 29, 4), LEATHER, r=6, flat=0.15)
    puff(p, poly_m([(4, 18), (44, 18), (44, 28), (24, 35), (4, 28)]), LEATHER, r=4, bias=0.15)
    p = finish(p) and p
    stitches(p, 6, 20, 42, 20, LEATHER[0], 2)
    p.hline(4, 28, 12, LEATHER[0])
    p.rect(21, 29, 6, 9, LEATHER[1])
    p.vline(21, 29, 9, LEATHER[3])
    buckle(p, 21, 33)
    stitches(p, 6, 43, 42, 43, LEATHER[0], 2)
    stud(p, 7, 30)
    stud(p, 39, 30)
    return p.im


def kid_pack(ramp: Ramp, seed: int, bear: bool) -> Image.Image:
    """A child's pack with a stitched face patch. The wine one is a round cat-face, the ochre one a bear with ears and paws."""
    h = 64 if bear else 48
    p = Pix(48, h, seed=seed)
    top = 8 if bear else 3
    if bear:
        for ex in (6, 30):
            puff(p, ell_m(ex, 2, 12, 12), ramp, r=4)
            puff(p, ell_m(ex + 3, 5, 6, 6), ROSE, r=2)
        for ex in (10, 28):
            puff(p, ell_m(ex, 55, 9, 6), ramp, r=3)
    puff(p, rrect_m(5, top, 38, h - top - (6 if bear else 2), 10), ramp, r=7)
    if not bear:
        for ex in (6, 32):
            puff(p, poly_m([(ex, 8), (ex + 8, 8), (ex + 4, 1)]), ramp, r=2)
    p = finish(p) and p
    cy = top + 18
    face = BONE if not bear else (200, 150, 90)
    p.rect(12, cy - 6, 24, 18, face if bear else ramp[3])
    p.frame(12, cy - 6, 24, 18, ramp[0])
    for ex in (17, 29):                                       # eyes
        p.rect(ex, cy, 3, 3, SHADOW)
        p.px(ex, cy, BONE[4])
    p.hline(22, cy + 6, 4, SHADOW)
    p.rect(22, cy + 3, 4, 2, ROSE[1])
    dots(p, [(14, cy + 5), (15, cy + 5), (33, cy + 5), (32, cy + 5)], ROSE[2])
    stitches(p, 10, cy + 14, 38, cy + 14, ramp[0], 2)
    buckle(p, 22, h - 14 if bear else h - 12)
    return p.im


ASSETS: Mapping[str, Draw] = {
    _f("fanny_pack"): pouch,
    _f("satchel"): satchel,
    _f("junor_backpack1"): partial(kid_pack, WINE, 1, False),
    _f("junor_backpack2"): partial(kid_pack, OCHRE, 2, True),
    _f("simple_backpack"): partial(rucksack, 48, 64, (3, 2, 45, 62), LEATHER, 3),
    _f("simple_backpack_medium"): partial(rucksack, 64, 80, (5, 3, 59, 77), LEATHER, 4, "top", True),
    _f("simple_backpack_large"): partial(rucksack, 64, 96, (2, 6, 62, 90), LEATHER, 5, "bottom", True),
}
