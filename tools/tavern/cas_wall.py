"""`wall` and `wall2` with the display-case window cut into them: a timber lintel, a stone sill, a timber jamb on the
right, a plaster edge on the left, and the opening itself (the street seen through, see cas_kit)."""

from __future__ import annotations

from collections.abc import Callable

from PIL import Image

import cas_kit
from cas_kit import H, OPEN, W
from materials import beam
from palette import BRASS, IRON, OAK, PLASTER, SHADOW, STONE
from fxkit import contact_shadow, noise, pick_tone, rivet
from pix import Pix, mix
from shop import wall
from shopx_persp import blend, stepped

LINTEL = (103, 104, 296, 120)         # x0, y0, x1, y1: oak header across the opening, bearing into the wall at the left
SILL = (106, 260, 296, 268)           # a stone slab under it
JAMB = (289, 120, 296, 260)           # the right-hand timber stud, against the post


def _stone_slab(p: Pix, x0: int, y0: int, x1: int, y1: int) -> None:
    """A dressed sill: a lit top face seen from above, a front face in the middle tone, a dark drip edge, hairline joints."""
    top = 3
    for y in range(y0, y1):
        for x in range(x0, x1):
            if y < y0 + top:
                v = 3.4 - (y - y0) * 0.35 + (noise(x, y, 5) - 0.5) * 1.6
            else:
                v = 2.0 - (y - y0 - top) * 0.28 + (noise(x, y, 6) - 0.5) * 1.8
            p.px(x, y, pick_tone(STONE, v, x, y))
    p.hline(x0, y0, x1 - x0, STONE[4])
    p.hline(x0, y0 + top, x1 - x0, STONE[1])
    p.hline(x0, y1 - 1, x1 - x0, STONE[0])
    p.vline(x0, y0, y1 - y0, STONE[4])
    p.vline(x1 - 1, y0, y1 - y0, STONE[0])
    for jx in (x0 + 61, x0 + 128):                           # two joints between slabs
        p.vline(jx, y0 + 1, y1 - y0 - 1, STONE[0])
        p.vline(jx + 1, y0 + 1, top - 1, STONE[4])


def _lintel(p: Pix) -> None:
    x0, y0, x1, y1 = LINTEL
    # the shade the header throws up on the plaster is nil (light comes from above); below it the opening is dark
    contact_shadow(p, (x0, y0, x1 - x0, y1 - y0), shift=(2, 3), spread=3, strength=0.7)
    beam(p, x0, y0, x1 - x0, y1 - y0, OAK, vertical=False)
    for y in range(y0 + 2, y1 - 2):                          # the end grain at the left end: rings and a check
        p.px(x0 + 1, y, OAK[1])
    p.hline(x0 + 2, y0 + 5, 3, OAK[1])
    p.hline(x0 + 2, y0 + 9, 3, OAK[1])
    for nx in (x0 + 12, x0 + 58, x1 - 18):                   # pegs that hold the joints
        p.rect(nx, y0 + 6, 3, 3, OAK[0])
        p.px(nx, y0 + 6, OAK[4])
    for sx in (x0 + 34, x1 - 40):                            # iron straps nailed over the timber
        p.rect(sx, y0, 22, y1 - y0, IRON[2])
        p.hline(sx, y0, 22, IRON[4])
        p.hline(sx, y1 - 1, 22, IRON[0])
        p.vline(sx + 21, y0, y1 - y0, IRON[1])
        for rx in (sx + 4, sx + 17):
            rivet(p, rx, y0 + (y1 - y0) // 2, 1, BRASS)


def _jamb(p: Pix) -> None:
    x0, y0, x1, y1 = JAMB
    contact_shadow(p, (x0, y0, x1 - x0, y1 - y0), shift=(2, 1), spread=2, strength=0.5)
    beam(p, x0, y0, x1 - x0, y1 - y0, OAK, vertical=True)
    p.vline(x0, y0, y1 - y0, OAK[0])                         # its left edge is a gap against the case frame: dark
    for ny in (y0 + 20, y0 + 70, y0 + 120):
        rivet(p, x0 + 3, ny, 1, BRASS)


def _sill(p: Pix) -> None:
    x0, y0, x1, y1 = SILL
    for y in range(y1, y1 + 7):                              # the slab's shade on the plaster below it
        for x in range(x0 - 1, x1):
            if stepped(0.6 * (1 - (y - y1) / 7), x, y):
                blend(p, x, y, SHADOW, 0.6)
    _stone_slab(p, x0, y0, x1, y1)


def _left_edge(p: Pix) -> None:
    """The plaster stops at a lit rounded edge; a chipped corner shows the lath."""
    x0, y0, x1, y1 = OPEN
    p.vline(x0 - 1, y0, y1 - y0, PLASTER[4])
    p.vline(x0 - 2, y0, y1 - y0, PLASTER[3])
    for y in range(y0, y1):
        if noise(2, y, 9) < 0.18:
            p.px(x0 - 1, y, PLASTER[2])
        if stepped(0.5, x0 - 3, y):
            p.px(x0 - 3, y, PLASTER[1])
    p.px(x0 - 3, y1 - 1, OAK[1])


def _cut(variant: int) -> Image.Image:
    p = Pix(W, H, seed=211 + variant)
    p.paste(wall(variant), 0, 0)
    x0, y0, x1, y1 = OPEN
    p.erase(x0, y0, x1 - x0, y1 - y0)
    if cas_kit.STREET:
        p.paste(cas_kit.street().im.crop((x0, y0, x1, y1)), x0, y0)
    _left_edge(p)
    _jamb(p)
    _lintel(p)
    _sill(p)
    # the lintel's shade into the opening: a few rows of dither down the top of the view
    if cas_kit.STREET:
        for y in range(y0, y0 + 8):
            for x in range(x0, x1):
                if stepped(0.8 * (1 - (y - y0) / 8), x, y):
                    blend(p, x, y, SHADOW, 0.7)
    return p.finish()


ASSETS: dict[str, Callable[[], Image.Image]] = {
    "wall.960x540.png": lambda: _cut(0),
    "wall2.960x540.png": lambda: _cut(1),
}
