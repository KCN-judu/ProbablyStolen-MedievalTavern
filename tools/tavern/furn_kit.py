"""Shared helpers of the furniture item pictures (`furn_*` modules): clipping to the game's occupied area, a glass sight
tube, a stave-bodied cask drawn with the cask-level materials of `fxkit`, and a few small rubbish pieces."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Final

from PIL import Image, ImageChops

import fxkit as fx
from furn_masks import mask as area_mask
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, WINE, WOOD
from pix import Pix, Ramp, mix, rgb

SLOP: Final[Ramp] = (rgb("#2a170d"), rgb("#4a2a12"), rgb("#6e4218"), rgb("#97602a"), rgb("#c58c46"), rgb("#e8b868"))
ALE: Final[Ramp] = (rgb("#6a2c0e"), rgb("#a2501a"), rgb("#d78a2a"), rgb("#f0b448"), rgb("#ffe08a"), rgb("#fff4c4"))
BRASS_AGED: Final[Ramp] = (BRASS[0], mix(BRASS[0], BRASS[1], 0.5), BRASS[1], mix(BRASS[1], BRASS[2], 0.55), mix(BRASS[2], BRASS[3], 0.4))   # old, dull brass
WATER: Final[Ramp] = (rgb("#16303a"), rgb("#2a5a68"), rgb("#4a8a96"), rgb("#82bcc0"), rgb("#cbeae4"))


def clip(p: Pix, key: str) -> Image.Image:
    """Keeps the picture inside the area the game gives the item (transparent elsewhere) and returns the image."""
    m = area_mask(key, p.w)
    p.im.putalpha(ImageChops.multiply(p.im.getchannel("A"), m))
    return p.im


def sight_tube(p: Pix, x: int, top: int, bot: int, w: int, frac: float, liquid: Ramp = SLOP, ticks: int = 4,
               pipes: tuple[int, int] | None = None, pipe_to: int = 0) -> None:
    """A vertical glass tube (`w` px wide) from y `top` to `bot` (inclusive) between two brass collars, held in an iron
    cradle, with the liquid standing `frac` of the way up the glass. Brass pipes at both collars run to x `pipe_to`
    (the cask's wall) when `pipes` (the two pipe y's) is given. Scale ticks stand to the right of the glass."""
    gh = bot - top + 1
    cw = w + 4
    cx0 = x - 2
    if pipes:
        for py in pipes:
            x0, x1 = sorted((pipe_to, cx0))
            fx.brass_fill(p, (x0, py - 2, x1 - x0 + 1, 5), profile="tube", tarnish=0.3, seed=py)
            fx.brass_fill(p, (pipe_to - 1 if pipe_to < cx0 else pipe_to - 3, py - 4, 4, 9), profile="tube", tarnish=0.3, seed=py + 1)
            fx.rivet(p, pipe_to + (1 if pipe_to < cx0 else -1), py - 2, 1, BRASS)
            fx.rivet(p, pipe_to + (1 if pipe_to < cx0 else -1), py + 2, 1, BRASS)
    p.rect(x - 1, top - 1, w + 2, gh + 2, IRON[0])                      # the iron cradle behind the glass
    p.vline(x - 1, top - 1, gh + 2, IRON[3])
    for yy in range(top, bot + 1):                                       # the glass: a cylinder, lit left, dark right
        for k in range(w):
            t = (k + 0.5) / w
            i = 4 if t < 0.28 and k == 0 else 3 if t < 0.4 else 2 if t < 0.7 else 1
            p.px(x + k, yy, GLASS[i - 1] if i < 4 else GLASS[3])
    rise = round((gh - 1) * frac)
    if frac > 0 and rise >= 0:
        y0 = bot - rise
        for yy in range(y0, bot + 1):
            for k in range(w):
                t = (k + 0.5) / w
                i = 4 if (k == 0 and w > 3) else 3 if t < 0.45 else 2 if t < 0.72 else 1
                p.px(x + k, yy, liquid[i if i < 4 else 4] if k else liquid[3])
        for k in range(w):
            p.px(x + k, y0, liquid[5] if k < w - 1 else liquid[4])       # the meniscus
        if y0 + 1 <= bot:
            p.px(x + w - 1, y0 + 1, liquid[2])
        for j in range(3, rise, 7):                                      # sediment flecks
            p.px(x + 1 + (j * 3) % max(1, w - 2), bot - j, liquid[0])
    for yy in range(top + 2, bot - 3, 11):                               # a glint down the glass
        p.vline(x + 1 if w > 3 else x, yy, 4, GLASS[4])
    for cap_y, up in ((top - 4, True), (bot + 1, False)):                # brass collars
        fx.brass_fill(p, (cx0, cap_y, cw, 4), profile="tube", tarnish=0.25, seed=cap_y)
    for k in range(ticks + 1):
        ty = bot - round((gh - 1) * k / ticks)
        major = k % 2 == 0 or ticks <= 4
        p.hline(x + w + 2, ty, 4 if major else 2, SHADOW)
        p.hline(x + w + 2, ty - 1, 4 if major else 2, BRASS[3]) if k else None
    p.vline(x + w + 1, top, gh, BRASS[1])
