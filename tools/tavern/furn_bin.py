"""`trashcan0|25|50|75|100` (96x144): the bin as a hooped oak slop-cask with a glass sight tube on its flank.

What it is: a tavern's slop barrel, an open-headed cask the scullery tips scraps into. The gauge: a glass tube between two
brass collars, plumbed into the cask by brass pipes near the foot and the head, shows how high the slop stands; the scale
has a tick at 0, 25, 50, 75 and 100 per cent. Inside the open head the rubbish rises with the same share and at 100 it
heaps over the lip. The five pictures share one silhouette and differ only in the fill."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image, ImageChops, ImageDraw

import fxkit as fx
from furn_cask import Cask, cask_body, head, junk
from furn_kit import SLOP, clip, sight_tube
from palette import LEATHER, MOSS, OAK, PARCHMENT, SHADOW, SOOT, WINE
from pix import Pix, mix

CX, TOP, BOT, HALF, RY = 40, 31, 118, 31, 10
TUBE_X, TUBE_TOP, TUBE_BOT, TUBE_W = 77, 50, 109, 5          # glass rows 50..109: 60 px, 15 per quarter
HOOPS: Final = (TOP + 3, TOP + 21, BOT - 24, BOT - 6)


def _contents(level: int, op: tuple[float, float, float, float]) -> Image.Image:
    """The opening seen from above and in front: the inner rear wall of the staves, and the scraps inside lying at a
    depth that follows `level` (their surface is the opening's ellipse slid down by the depth, clipped to the opening)."""
    ox, oy, orx, ory = op
    p = Pix(96, 144, seed=70 + level)
    wall = fx.ellipse(ox, oy, orx, ory)
    fx.wood_fill(p, wall, "v", OAK, board=5, light=0.2, bias=-1.4, seed=7, knots=0.3, joints=False, nails=False)
    for yy in range(round(oy), round(oy + ory) + 1):                     # the dark gathers toward the well
        for xx in range(round(ox - orx), round(ox + orx) + 1):
            if p.get(xx, yy)[3] and (xx + yy) % 2 == 0:
                p.px(xx, yy, SOOT[0])
    depth = {0: 99.0, 25: ory * 1.55, 50: ory * 0.95, 75: ory * 0.38, 100: -0.5}[level]
    wmask = Image.new("L", (96, 144), 0)
    ImageDraw.Draw(wmask).polygon(wall, fill=255)
    if depth < ory * 2:
        rim = fx.region(p, wall)
        s = fx.region(p, fx.ellipse(ox, oy + depth, orx, ory))
        top_y = round(oy + depth) - round(ory)
        for x, y in s.pixels():
            if not rim.inside(x, y):
                continue
            n = fx.noise(x // 2, y // 2, 11)
            n2 = fx.vnoise(x / 3, y / 2, 5)
            c = LEATHER[1] if n2 < 0.3 else MOSS[1] if n2 < 0.55 else LEATHER[2] if n2 < 0.8 else WINE[1]
            if n < 0.12:
                c = PARCHMENT[2]
            elif n > 0.93:
                c = MOSS[2]
            if y - top_y < 2:
                c = mix(c[:3], SOOT[0][:3], 0.35)                        # the far edge lies in the lip's shade
            p.px(x, y, c)
        for i in range(5 if level < 100 else 8):                         # scraps lying on the surface
            jx = round(ox + (fx.noise(i, 3, 9) - 0.5) * orx * 1.3) - 5
            jy = round(oy + depth + (fx.noise(i, 5, 9) - 0.5) * ory * 0.8) - 4
            j = Pix(96, 144, seed=i)
            junk(j, jx, jy, i + level // 25, seed=i)
            j.im.putalpha(ImageChops.multiply(j.im.getchannel("A"), wmask))
            p.paste(j, 0, 0)
    return p.im


def _heap(p: Pix, level: int, c: Cask) -> None:
    """The scraps that rise over the lip: 75 % shows a few pieces, 100 % a proper heap, back pieces first."""
    if level < 75:
        return
    spots = ((-9, -4, 3), (6, -5, 0), (-2, -8, 5), (12, -1, 1)) if level == 75 else (
        (-17, 0, 2), (-6, -10, 4), (6, -14, 1), (16, -6, 7), (-11, -6, 6), (0, -5, 3), (10, -1, 0), (-19, 5, 5), (19, 3, 4),
        (-3, -17, 2), (-9, 5, 1), (4, 4, 6), (14, 6, 2), (-13, 8, 4))
    for i, (dx, dy, kind) in enumerate(sorted(spots, key=lambda s: s[1])):
        junk(p, round(c.cx) + dx - 5, round(c.top) + dy - 4, kind, seed=i)


def trash(level: int) -> Image.Image:
    p = Pix(96, 144, seed=40 + level)
    c = Cask(CX, TOP, BOT, HALF, RY)
    fx.contact_shadow(p, fx.ellipse(CX, BOT + 3, HALF * 0.9, RY * 0.9), shift=(3, 1), spread=5, strength=1.0)
    body = Pix(96, 144, seed=3)
    cask_body(body, c, HOOPS, staves=13, seed=5)
    op, opoly = head(body, c, seed=6)
    p.paste(body, 0, 0)
    inner = _contents(level, op)
    m = Image.new("L", (96, 144), 0)
    ImageDraw.Draw(m).polygon(opoly, fill=255)
    inner.putalpha(ImageChops.multiply(inner.getchannel("A"), m))
    p.paste(inner, 0, 0)
    ox, oy, orx, ory = op
    for x in range(round(ox - orx) + 1, round(ox + orx)):                # where the front lip drops into the well
        t = (x - ox) / orx
        y = round(oy + ory * math.sqrt(max(0.0, 1 - t * t)))
        p.px(x, y + 1, SHADOW)
        fx.over(p, x, y + 2, SHADOW, 70)
    _heap(p, level, c)
    # the sight tube on the right flank, plumbed into the cask near the head and at the foot
    sight_tube(p, TUBE_X, TUBE_TOP, TUBE_BOT, TUBE_W, level / 100, SLOP, ticks=4, pipes=(TUBE_TOP - 6, TUBE_BOT + 6), pipe_to=CX + 29)
    for y in (TUBE_TOP + 22, TUBE_TOP + 44):                             # iron straps hold the cradle to the cask
        fx.iron_fill(p, (CX + 33, y, TUBE_X - CX - 35, 3), rust=0.1, seed=y)
    return clip(p, "trash")


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    f"items~items_furniture@trashcan{lv}.png": partial(trash, lv) for lv in (0, 25, 50, 75, 100)}
