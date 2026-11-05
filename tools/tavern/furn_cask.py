"""Stave casks and rubbish for the furniture pictures (`furn_*`): a cask standing on end drawn with the cask-level
materials of `fxkit` (own tone per stave, wandering grain, knots, joints that follow the belly, iron hoops with lit
edges and rivets, damp foot), its head, and a set of small scraps."""

from __future__ import annotations

import math
from typing import Final

import fxkit as fx
from palette import LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import Pix, Ramp, rgb

SHELL: Final[Ramp] = (rgb("#6d5a3c"), rgb("#8f7a52"), rgb("#c2ad7e"), rgb("#ecdcae"))


class Cask:
    """Geometry of a stave cask standing on end: centred on x `cx`, the axis running from y `top` (the head's centre) to
    y `bot` (the foot's centre), `half` wide at the belly, ends `ry` px of ellipse above and below."""

    def __init__(self, cx: float, top: float, bot: float, half: float, ry: float, ends: float = 0.88) -> None:
        self.cx, self.top, self.bot, self.half, self.ry, self.ends = cx, top, bot, half, ry, ends

    def hw(self, yc: float) -> float:
        t = max(0.0, min(1.0, (yc - self.top) / (self.bot - self.top)))
        return self.half * (self.ends + (1 - self.ends) * (1 - (2 * t - 1) ** 2))

    def axis(self, x: float, y: float) -> tuple[float, float]:
        """(height on the axis, t across the width -1..1) of a pixel, undoing the ellipse curve of the ends."""
        yc, t = y, 0.0
        for _ in range(4):
            t = max(-1.0, min(1.0, (x - self.cx) / self.hw(yc)))
            yc = y - self.ry * math.sqrt(1 - t * t)
        return yc, t

    def outline(self) -> list[tuple[int, int]]:
        pts: list[tuple[int, int]] = []
        n = int(self.bot - self.top)
        for i in range(n + 1):
            y = self.top + i
            pts.append((round(self.cx - self.hw(y)), round(y)))
        wb = self.hw(self.bot)
        for k in range(-int(wb), int(wb) + 1):
            pts.append((round(self.cx + k), round(self.bot + self.ry * math.sqrt(max(0.0, 1 - (k / wb) ** 2)))))
        for i in range(n, -1, -1):
            y = self.top + i
            pts.append((round(self.cx + self.hw(y)), round(y)))
        return pts

    def hoop(self, p: Pix, hy: float, thick: int = 5, rivets: int = 13, rust: float = 0.25, seed: int = 0) -> None:
        w = self.hw(hy)
        pts = [(self.cx + k, hy + self.ry * math.sqrt(max(0.0, 1 - (k / w) ** 2))) for k in range(-int(w) + 1, int(w))]
        for x, y in pts:                                                 # the shadow the hoop throws on the staves below
            for j in range(thick, thick + 2):
                fx.over(p, round(x), round(y) + j, SHADOW, 120 if j == thick else 55)
        fx.iron_band(p, pts, thick, rivets=rivets, rust=rust, hammer=0.3, seed=seed)


def cask_body(p: Pix, c: Cask, hoops: tuple[float, ...], staves: int = 13, seed: int = 1, damp: float = 0.6,
              hoop_thick: int = 5) -> None:
    """The staves and the iron hoops that follow the ellipse of the belly. The head is added by `head`."""
    stave_w = c.half * math.pi / staves

    def curve(x: int, y: int) -> tuple[float, float]:
        yc, t = c.axis(x, y)
        return yc - c.top, (math.asin(t) + math.pi / 2) / math.pi * staves * stave_w

    def light(x: int, y: int) -> float:
        _, t = c.axis(x, y)
        th = math.asin(t)
        return 1.25 * (0.55 * math.cos(th) - 0.95 * math.sin(th) - 0.3)

    fx.wood_fill(p, c.outline(), "v", WOOD, board=stave_w, curve=curve, light_fn=light, light=0.0, seed=seed, knots=1.4,
                 joints=False, nails=False, scratches=1.6, wear_amount=0.12, damp=damp, damp_from="bottom")
    for k, hy in enumerate(hoops):
        c.hoop(p, hy, hoop_thick, seed=seed * 10 + k)


def head(p: Pix, c: Cask, seed: int = 2) -> tuple[tuple[float, float, float, float], list[tuple[int, int]]]:
    """The top of a cask: a ring of stave ends (the lip). Returns the opening's ellipse (cx, cy, rx, ry) and its polygon."""
    rx = c.hw(c.top)
    fx.wood_fill(p, fx.ellipse(c.cx, c.top, rx, c.ry), 30, PALE_WOOD, board=4, light=0.4, seed=seed, knots=0.3,
                 joints=False, nails=False, scratches=1.0)
    op = (c.cx, c.top + 0.6, rx - 3.2, c.ry - 2.6)
    return op, fx.ellipse(*op)


# ---------------------------------------------------------------------------------------------- rubbish


def _outlined(p: Pix, pts: list[tuple[int, int]]) -> None:
    """A one-pixel dark rim round a small object, so it reads against its neighbours."""
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        p.poly([(x + dx, y + dy) for x, y in pts], SHADOW)


def junk(p: Pix, x: int, y: int, kind: int, seed: int = 0) -> None:
    """One piece of kitchen and tavern rubbish with its top left corner near (x, y), about 10 px across: a bone, a cabbage
    leaf, a crumpled note, a fish skeleton, a wine-red rag, an apple core, a potsherd, an eggshell."""
    k = kind % 8
    if k == 0:                                                           # a gnawed bone
        _outlined(p, [(x, y + 2), (x + 10, y + 2), (x + 10, y + 5), (x, y + 5)])
        p.rect(x + 1, y + 2, 8, 3, PARCHMENT[3])
        p.hline(x + 1, y + 2, 8, PARCHMENT[4])
        p.hline(x + 1, y + 4, 8, PARCHMENT[1])
        for kx in (x - 1, x + 8):
            p.rect(kx, y + 1, 3, 5, PARCHMENT[3])
            p.px(kx, y + 1, PARCHMENT[4])
            p.hline(kx, y + 5, 3, PARCHMENT[1])
    elif k == 1:                                                         # a cabbage leaf with a pale rib
        pts = [(x, y + 5), (x + 2, y + 1), (x + 7, y), (x + 11, y + 3), (x + 9, y + 7), (x + 4, y + 8)]
        _outlined(p, pts)
        p.poly(pts, MOSS[2])
        p.poly([(x + 1, y + 5), (x + 3, y + 2), (x + 7, y + 1)], MOSS[3])
        p.line(x + 1, y + 5, x + 10, y + 4, PARCHMENT[2])
        p.line(x + 5, y + 4, x + 7, y + 7, MOSS[1])
        p.hline(x + 4, y + 8, 5, MOSS[0])
    elif k == 2:                                                         # a crumpled note
        pts = [(x, y + 3), (x + 4, y), (x + 9, y + 1), (x + 10, y + 6), (x + 5, y + 8), (x + 1, y + 7)]
        _outlined(p, pts)
        fx.paper_fill(p, pts, folds=(1, 1), stains=0.5, seed=seed + 3, ink=0.5)
    elif k == 3:                                                         # a fish skeleton
        _outlined(p, [(x - 1, y + 3), (x + 13, y + 3), (x + 13, y + 8), (x - 1, y + 8)])
        p.rect(x - 1, y + 4, 14, 4, SHADOW)
        p.hline(x + 1, y + 6, 10, PARCHMENT[3])
        for i in range(3, 11, 2):
            p.vline(x + i, y + 4, 4, PARCHMENT[2])
            p.px(x + i, y + 4, PARCHMENT[4])
        p.poly([(x - 1, y + 4), (x + 2, y + 6), (x - 1, y + 8)], PARCHMENT[3])
        p.px(x, y + 6, SHADOW)
        p.poly([(x + 11, y + 5), (x + 13, y + 4), (x + 13, y + 8), (x + 11, y + 7)], PARCHMENT[2])
    elif k == 4:                                                         # a wine-red rag
        pts = [(x, y + 4), (x + 4, y), (x + 10, y + 1), (x + 11, y + 6), (x + 6, y + 8), (x + 1, y + 7)]
        _outlined(p, pts)
        fx.cloth_fill(p, pts, WINE, "wool", folds=2, fray="b", seed=seed + 4)
    elif k == 5:                                                         # an apple core, gnawed to the pips
        pts = [(x + 2, y), (x + 8, y), (x + 9, y + 4), (x + 8, y + 8), (x + 2, y + 8), (x + 1, y + 4)]
        _outlined(p, pts)
        p.poly(pts, PARCHMENT[3])
        p.rect(x + 3, y + 2, 4, 4, PARCHMENT[1])
        p.rect(x + 4, y + 3, 2, 3, LEATHER[1])
        p.hline(x + 2, y, 4, WINE[3])
        p.line(x + 5, y - 1, x + 7, y - 3, LEATHER[1])
    elif k == 6:                                                         # a potsherd
        pts = [(x, y + 6), (x + 3, y + 1), (x + 10, y), (x + 9, y + 5), (x + 4, y + 8)]
        _outlined(p, pts)
        p.poly(pts, PALE_WOOD[2])
        p.poly([(x + 1, y + 5), (x + 3, y + 2), (x + 9, y + 1)], PALE_WOOD[3])
        p.line(x + 3, y + 6, x + 8, y + 4, PALE_WOOD[0])
        p.hline(x + 4, y + 7, 3, PALE_WOOD[0])
    else:                                                                # an eggshell
        pts = [(x + 1, y + 3), (x + 4, y), (x + 9, y + 1), (x + 9, y + 6), (x + 5, y + 8), (x + 2, y + 6)]
        _outlined(p, pts)
        p.poly(pts, SHELL[3])
        p.poly([(x + 3, y + 3), (x + 5, y + 2), (x + 8, y + 3), (x + 7, y + 6), (x + 4, y + 6)], SHELL[1])
        p.px(x + 4, y + 1, SHELL[3])
