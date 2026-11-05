"""The body of a bust: shoulders and torso as masks, lit by cylinders, and the small parts garments are made of.

A garment gets a `Ctx` (the canvas, the masks and the colour ramps) and paints in layers: a shaded base, panels, seams,
folds, collars, buttons. Light comes from the upper left, so left sleeves are lit and the right side falls into shadow.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from people_kit import CH, Mask, W, blank, both, minus, oval, poly, rect, shift, shrink, union, grow, tone, hx
from people_look import Look
from pface_core import CUTS, cylinder, fill, flat, hl, inside, pixels, trace, vl, curve
from pface_head import CX, Geo
from pix import Color, Pix, Ramp, mix, rgb

BRASS_R: Ramp = tone(rgb("#c8a040"))
IRON_R: Ramp = tone(rgb("#7c7a86"))
STEEL_R: Ramp = tone(rgb("#9aa0aa"))
LEATHER_R: Ramp = tone(rgb("#7a4a2a"))
LINEN_R: Ramp = tone(rgb("#d2c6aa"))
CLOTH_CUTS = (0.04, 0.40, 0.82, 1.12)


@dataclass
class Ctx:
    """Everything a garment needs."""

    p: Pix
    look: Look
    g: Geo
    torso: Mask
    main: Ramp
    second: Ramp
    trim: Ramp
    sw: int
    yn: int                 # the row where the neck meets the shoulders
    nk: int                 # half the neck's width at its foot
    rng: random.Random = field(default_factory=random.Random)
    neck: object = None     # a snapshot of the picture with only the neck drawn

    @property
    def arm_in(self) -> int:
        """Columns from the centre where the arms begin."""
        return self.sw - 25


def torso_mask(sw: int, yn: int, nk: int, drop: float = 0.34, bottom: int = CH) -> Mask:
    """Shoulders and chest: the neck line, the sloping trapezius, the rounded shoulder, then straight down."""
    pts: list[tuple[float, float]] = []
    x_end = sw - 11
    y_end = yn + drop * (x_end - nk)
    right = [(nk, yn - 6), (nk + 2, yn - 1), (x_end - 8, y_end - 2), (x_end - 2, y_end + 1), (sw - 5, y_end + 4), (sw - 1, y_end + 9),
             (sw, y_end + 17), (sw, bottom)]
    for x, y in right:
        pts.append((CX + x, y))
    for x, y in reversed(right):
        pts.append((CX - x, y))
    return poly(pts)


def torso_light(c: Ctx, base: float = 0.0):
    """Light on the torso as one cylinder and two arm cylinders, darker towards the bottom."""
    sw = c.sw
    chest = cylinder(CX, sw * 0.80, c.yn + 30, 215, base)
    arm_l = cylinder(CX - sw + 11, 15, c.yn + 30, 215, base)
    arm_r = cylinder(CX + sw - 11, 15, c.yn + 30, 215, base - 0.12)
    ai = c.arm_in

    def f(x: int, y: int) -> float:
        dx = x + 0.5 - CX
        if dx < -ai:
            v = arm_l(x, y)
        elif dx > ai:
            v = arm_r(x, y)
        else:
            v = chest(x, y)
        if y < c.yn + 22:                      # the shoulders catch the lantern
            v += 0.12 * (c.yn + 22 - y) / 22
        return v
    return f


def paint_base(c: Ctx, m: Mask | None = None, ramp: Ramp | None = None, texture: float = 0.1, base: float = 0.0) -> None:
    """The torso (or part of it) in a ramp, lit."""
    fill(c.p, m if m is not None else c.torso, ramp or c.main, torso_light(c, base), cuts=CLOTH_CUTS, texture=texture)


def panel(c: Ctx, m: Mask, ramp: Ramp, texture: float = 0.1, base: float = 0.0) -> None:
    """A garment panel on the torso, lit like the torso itself."""
    fill(c.p, both(m, c.torso), ramp, torso_light(c, base), cuts=CLOTH_CUTS, texture=texture)


def seam(c: Ctx, pts: list[tuple[float, float]], ramp: Ramp, lit: bool = True, clip: Mask | None = None) -> None:
    """A stitched seam or fold: a dark line with a light line beside it (towards the light)."""
    m = clip if clip is not None else c.torso
    trace(c.p, pts, ramp[0] if len(ramp) > 1 else ramp[0], m)
    if lit:
        trace(c.p, [(x - 1, y) for x, y in pts], ramp[3], m)


def fold(c: Ctx, pts: list[tuple[float, float]], ramp: Ramp, clip: Mask | None = None, dark: int = 1) -> None:
    """A soft fold: a mid-dark line with a lit edge on its upper left."""
    m = clip if clip is not None else c.torso
    trace(c.p, [(x + 1, y + 1) for x, y in pts], ramp[3], m)
    trace(c.p, pts, ramp[dark], m)


def drape(c: Ctx, x0: float, y0: float, x1: float, y1: float, bow: float, ramp: Ramp, clip: Mask | None = None) -> None:
    """A curved fold from (x0, y0) to (x1, y1) bowing sideways."""
    mid = ((x0 + x1) / 2 + bow, (y0 + y1) / 2)
    fold(c, curve((x0, y0), mid, (x1, y1), 14), ramp, clip)


def button(p: Pix, x: int, y: int, r: Ramp = BRASS_R) -> None:
    """A 2x2 domed button with a catchlight."""
    p.px(x, y, r[4])
    p.px(x + 1, y, r[3])
    p.px(x, y + 1, r[2])
    p.px(x + 1, y + 1, r[1])


def rivet(p: Pix, x: int, y: int, r: Ramp = BRASS_R) -> None:
    p.px(x, y, r[4])
    p.px(x + 1, y + 1, r[0] if len(r) else r[0])


def quilt(c: Ctx, m: Mask, ramp: Ramp, step: int = 7) -> None:
    """Gambeson: diagonal stitch lines crossing in diamonds, the rows between them puffed (lit on the upper left)."""
    pa = c.p.im.load()
    assert pa is not None
    for x, y in pixels(m):
        a = (x + y) % step
        b = (x - y) % step
        if (a == 0 or b == 0) and (x + y) % 3 != 0:
            c.p.px(x, y, ramp[1])


def mail_texture(c: Ctx, m: Mask, ramp: Ramp) -> None:
    """Rings of chain mail: a staggered dot pattern, the rows alternating light and dark, lit from the upper left."""
    for x, y in pixels(m):
        if (x + y) % 2 == 0 and y % 2 == 0:
            c.p.px(x, y, ramp[3])
        elif (x + y) % 2 == 1 and y % 2 == 1:
            c.p.px(x, y, ramp[1])


def edge_band(c: Ctx, m: Mask, ramp: Ramp, width: int = 2) -> None:
    """A trim along the inside of a mask's edge."""
    inner = shrink(m, width)
    ring = minus(m, inner)
    fill(c.p, ring, ramp, torso_light(c), cuts=CLOTH_CUTS)


def stripe(c: Ctx, pts: list[tuple[int, int]], ramp: Ramp, clip: Mask | None = None, texture: float = 0.0) -> None:
    """A filled polygon of trim cloth, lit."""
    m = poly(pts)
    fill(c.p, both(m, clip) if clip is not None else both(m, c.torso), ramp, torso_light(c), cuts=CLOTH_CUTS, texture=texture)


def wrinkles(c: Ctx, area: tuple[int, int, int, int], ramp: Ramp, n: int = 6, clip: Mask | None = None) -> None:
    """Scattered short creases (a pair of lines each) across a box of the body: cloth that has been worn."""
    x0, y0, x1, y1 = area
    y1 = min(y1, 205)
    if y1 <= y0:
        return
    for _ in range(max(1, n * 2 // 3)):
        x = c.rng.randint(x0, x1)
        y = c.rng.randint(y0, y1)
        ln = c.rng.randint(4, 9)
        bend = c.rng.choice((-2, -1, 1, 2))
        pts = [(x, y), (x + ln // 2, y + bend), (x + ln, y + bend // 2)]
        fold(c, pts, ramp, clip)


def sag(c: Ctx, x0: float, x1: float, y: float, depth: float, ramp: Ramp, clip: Mask | None = None) -> None:
    """A fold hanging between two points: a shallow curve that sags in the middle."""
    fold(c, curve((x0, y), ((x0 + x1) / 2, y + depth * 2), (x1, y), 16), ramp, clip)
