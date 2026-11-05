"""Helpers for the tavern's liquid vessels: a glass vessel described by its outline, drawn empty, and the layers that
the game stacks over it (a liquid at some fill level in three colours, and a highlight layer).

The game draws a container as an empty base picture plus transparent layers cut to the same cell: `<name>_<colour>_<level>`
is only the liquid, bottom aligned, and `<name>_hl_<level>` the small lit marks.  A `Vessel` holds the outline rows and
the parts around it; the same description makes every state, so a series always reads as one object.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Final

from PIL import Image

from palette import BRASS, GLASS, IRON, LEATHER, PALE_WOOD, SHADOW, WINE
from pix import Color, Pix, Ramp, rgb

Rows = dict[int, tuple[int, int]]            # y -> (x0, x1) with x1 not included
Deco = Callable[[Pix], None]

# Liquids, dark to light; the last tone is the lit meniscus.  blue = spring water, dark = brown ale, red = rose tincture.
LIQUIDS: Final[dict[str, Ramp]] = {
    "blue": (rgb("#1d4a66"), rgb("#2d7898"), rgb("#58aec4"), rgb("#9fdce0"), rgb("#e4f6ec")),
    "dark": (rgb("#2c1509"), rgb("#55290f"), rgb("#8a4a14"), rgb("#c47d22"), rgb("#f1d28a")),
    "red": (rgb("#4e1022"), rgb("#8a2036"), rgb("#c33f45"), rgb("#ec7f70"), rgb("#ffd6b4")),
}
LEVELS: Final[tuple[int, ...]] = (10, 25, 50, 75, 90, 100)
SHARE: Final[dict[int, float]] = {10: 0.25, 25: 0.38, 50: 0.60, 75: 0.80, 90: 0.93, 100: 1.0}
CREAM: Final[Color] = rgb("#f3e6bd")


def rows_from(points: Sequence[tuple[int, int, int]], round_bottom: int = 0) -> Rows:
    """Outline rows from key rows (y, x0, x1), straight between them; the last rows can be rounded off."""
    rows: Rows = {}
    for (ya, xa0, xa1), (yb, xb0, xb1) in zip(points, points[1:]):
        for y in range(ya, yb + 1):
            t = (y - ya) / max(1, yb - ya)
            rows[y] = (round(xa0 + (xb0 - xa0) * t), round(xa1 + (xb1 - xa1) * t))
    cuts = {0: [], 1: [1], 2: [2, 1], 3: [2, 1, 1], 4: [3, 2, 1, 1]}[round_bottom]
    last = max(rows)
    for i, cut in enumerate(cuts):
        x0, x1 = rows[last - i]
        rows[last - i] = (x0 + cut, x1 - cut)
    return rows


@dataclass(frozen=True)
class Vessel:
    """A glass body plus what is around it.  `top100` is the highest row the liquid reaches."""
    size: tuple[int, int]
    rows: Rows
    top100: int
    under: Deco = lambda p: None             # handles, feet: behind the body
    over: Deco = lambda p: None              # stoppers, rims: on top of the body, outside the liquid
    front: Deco = lambda p: None             # wicker, iron posts: in front of the liquid too
    seed: int = 0
    inner: frozenset[tuple[int, int]] = field(init=False)
    ring: frozenset[tuple[int, int]] = field(init=False)
    edge: frozenset[tuple[int, int]] = field(init=False)

    def __post_init__(self) -> None:
        outer = {(x, y) for y, (x0, x1) in self.rows.items() for x in range(x0, x1)}
        edge = {q for q in outer if any((q[0] + dx, q[1] + dy) not in outer for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        rest = outer - edge
        ring = {q for q in rest if any((q[0] + dx, q[1] + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        object.__setattr__(self, "edge", frozenset(edge))
        object.__setattr__(self, "ring", frozenset(ring))
        object.__setattr__(self, "inner", frozenset(rest - ring))

    @property
    def bottom(self) -> int:
        return max((y for _, y in self.inner), default=0)

    def top(self, level: int) -> int:
        span = self.bottom - self.top100 + 1
        return self.bottom - max(2, round(SHARE[level] * span)) + 1


def _glass_body(p: Pix, v: Vessel) -> None:
    for x, y in v.edge:
        p.px(x, y, SHADOW)
    for x, y in v.ring:
        if (x - 1, y) in v.edge:
            c = GLASS[4]
        elif (x + 1, y) in v.edge or (x, y + 1) in v.edge:
            c = GLASS[2]
        else:
            c = GLASS[3]
        p.px(x, y, c)
    xs = [x for x, _ in v.inner] or [0]
    x_lo, x_hi = min(xs), max(xs)
    for x, y in v.inner:
        c = GLASS[2]
        if x - x_lo < 2 and (x + y) % 2 == 0:
            c = GLASS[3]
        elif x_hi - x < 2:
            c = GLASS[1] if (x + y) % 2 == 0 else GLASS[2]
        p.px(x, y, c)
    for y in range(v.top100 + 2, v.bottom - 2):          # the sheen of the glass, in broken streaks
        if (x_lo + 1, y) in v.inner and (y - v.top100) % 5 != 4:
            p.px(x_lo + 1, y, GLASS[4])


def base(v: Vessel) -> Image.Image:
    """The empty vessel."""
    p = Pix(*v.size, seed=v.seed)
    v.under(p)
    _glass_body(p, v)
    v.over(p)
    v.front(p)
    return p.im


def liquid(v: Vessel, colour: str, level: int) -> Image.Image:
    """Only the liquid at a fill level, lit from the upper left with a bright meniscus."""
    ramp = LIQUIDS[colour]
    p = Pix(*v.size, seed=v.seed)
    top = v.top(level)
    cells = sorted((q for q in v.inner if q[1] >= top), key=lambda q: (q[1], q[0]))
    xs = [x for x, _ in cells]
    x_lo, x_hi = min(xs), max(xs)
    for x, y in cells:
        depth = y - top
        row = [cx for cx, cy in cells if cy == y]
        left, right = x - min(row), max(row) - x
        c = ramp[2]
        if left == 0:
            c = ramp[3]
        elif right == 0:
            c = ramp[1]
        elif right == 1 and (x + y) % 2 == 0:
            c = ramp[1]
        if y >= v.bottom - 1 and right < 2 or y == v.bottom:
            c = ramp[0] if y == v.bottom else ramp[1]
        elif depth > 0 and left == 1 and depth % 4 < 2:
            c = ramp[3]
        p.px(x, y, c)
    for x in range(x_lo, x_hi + 1):                        # the meniscus: a lit top row and a soft row below it
        if (x, top) in v.inner:
            p.px(x, top, ramp[4])
            if (x, top + 1) in v.inner and (x - x_lo) < (x_hi - x_lo) * 0.7 + 1:
                p.px(x, top + 1, ramp[3])
    v.front(p)
    return p.im


def highlight(v: Vessel, level: int, ticks: bool = False) -> Image.Image:
    """The lit marks of a state: a sheen on the glass and a glint at the surface (or tally ticks on a measure)."""
    p = Pix(*v.size, seed=v.seed)
    top = v.top(level)
    xs = [x for x, y in v.inner if y == top] or [x for x, _ in v.inner]
    x_lo, x_hi = min(xs), max(xs)
    if ticks:
        for i, y in enumerate(range(v.top100 + 3, v.bottom - 1, 3)):
            long_tick = i % 2 == 0
            for x in range(x_hi - (2 if long_tick else 1) + 1, x_hi + 1):
                if (x, y) in v.inner:
                    p.px(x, y, CREAM)
        for x in range(x_lo, min(x_hi, x_lo + 3) + 1):
            p.px(x, top, BRASS[4])
        return p.im
    for y in range(top + 2, min(v.bottom - 1, top + 9)):
        if (x_lo + 1, y) in v.inner and (y - top) % 4 != 3:
            p.px(x_lo + 1, y, CREAM)
    for x in range(x_lo + 2, min(x_hi - 1, x_lo + 4) + 1):
        p.px(x, top, CREAM)
    return p.im


def column(v: Vessel, colour: str, x: int, y0: int, y1: int) -> Image.Image:
    """A pipette's liquid: a single lit column."""
    p = Pix(*v.size, seed=v.seed)
    ramp = LIQUIDS[colour]
    for y in range(y0, y1):
        p.px(x, y, ramp[3])
    p.px(x, y0, ramp[4])
    return p.im


# ---------------------------------------------------------------------------------------------- parts


def cork(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A cork stopper, lit on the left, with a shaded foot."""
    p.rect(x, y, w, h, PALE_WOOD[2])
    p.vline(x + 1, y + 1, h - 2, PALE_WOOD[4])
    p.vline(x + w - 2, y + 1, h - 2, PALE_WOOD[1])
    p.hline(x + 1, y + 1, w - 2, PALE_WOOD[3])
    p.px(x + w // 2, y + h // 2, PALE_WOOD[1])
    p.frame(x, y, w, h, SHADOW)
    p.px(x, y, CLEAR_PIXEL)
    p.px(x + w - 1, y, CLEAR_PIXEL)


CLEAR_PIXEL: Final[Color] = (0, 0, 0, 0)


def wax(p: Pix, x: int, y: int, w: int, h: int, drip: int = 3) -> None:
    """A red wax seal over a stopper, with a drip down the right side."""
    p.rect(x, y, w, h, WINE[2])
    p.hline(x + 1, y + 1, w - 2, WINE[4])
    p.vline(x + 1, y + 1, h - 2, WINE[3])
    p.vline(x + w - 2, y + 1, h - 2, WINE[1])
    p.frame(x, y, w, h, SHADOW)
    for i in range(drip):
        p.px(x + w - 2, y + h + i, WINE[2] if i < drip - 1 else WINE[1])
        p.px(x + w - 1, y + h + i, SHADOW)
    p.px(x + w - 3, y + h, SHADOW)


def band(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = BRASS) -> None:
    """A metal collar or rim: lit on top, a dark foot, rivets are left to the caller."""
    p.rect(x, y, w, h, ramp[2])
    p.hline(x, y, w, ramp[4])
    p.hline(x, y + h - 1, w, ramp[1])
    p.frame(x - 1, y - 1, w + 2, h + 2, SHADOW)
    p.px(x - 1, y - 1, CLEAR_PIXEL)
    p.px(x + w, y - 1, CLEAR_PIXEL)
    p.px(x - 1, y + h, CLEAR_PIXEL)
    p.px(x + w, y + h, CLEAR_PIXEL)


def strap(p: Pix, x: int, y: int, w: int, h: int, vertical: bool = True, ramp: Ramp = IRON) -> None:
    """An iron strap with a lit edge and a shaded one."""
    p.rect(x, y, w, h, ramp[2])
    if vertical:
        p.vline(x, y, h, ramp[4])
        p.vline(x + w - 1, y, h, ramp[1])
    else:
        p.hline(x, y, w, ramp[4])
        p.hline(x, y + h - 1, w, ramp[1])


def tones(base: Color) -> Ramp:
    """A five-tone ramp from one paint colour: deep warm shadow, shade, the colour, light, amber-lit highlight."""
    from pix import mix
    return (mix(base, SHADOW, 0.72), mix(base, SHADOW, 0.42), base, mix(base, rgb("#ffcf70"), 0.28),
            mix(base, rgb("#fff0b8"), 0.52))


def blob(p: Pix, rows: Rows, ramp: Ramp, grain: bool = True) -> set[tuple[int, int]]:
    """Fills an outline given as rows with a lit left/top edge, a shaded right/bottom edge and a dark rim; returns the
    interior (the pixels inside the rim) so that details can be put on it."""
    if len(ramp) == 4:
        from pix import mix
        ramp = (*ramp, mix(ramp[3], rgb("#fff0b8"), 0.35))
    outer = {(x, y) for y, (x0, x1) in rows.items() for x in range(x0, x1)}
    nb = ((1, 0), (-1, 0), (0, 1), (0, -1))
    edge = {q for q in outer if any((q[0] + dx, q[1] + dy) not in outer for dx, dy in nb)}
    xs = [x for x, _ in outer]
    x_lo, x_hi = min(xs), max(xs)
    for x, y in outer:
        if (x, y) in edge:
            p.px(x, y, SHADOW)
            continue
        c = ramp[2]
        if (x - 1, y) in edge or (x, y - 1) in edge:
            c = ramp[4] if (x - 1, y) in edge and (x, y - 1) in edge or (x, y - 1) in edge else ramp[3]
        elif (x + 1, y) in edge or (x, y + 1) in edge:
            c = ramp[1]
        elif grain:
            if x - x_lo < 4 and (x + y) % 2 == 0:
                c = ramp[3]
            elif x_hi - x < 4 and (x + y) % 2 == 0:
                c = ramp[1]
        p.px(x, y, c)
    return outer - edge
