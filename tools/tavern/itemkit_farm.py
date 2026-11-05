"""Shape-and-shade helpers for the farm and food sprites.

A shape is a set of (x, y) pixels. `shade` paints a shape from a dark-to-light ramp with a lit upper-left rim and a shaded
lower-right rim, `edge` rings it in the SHADOW tone, and the sprite functions stack shapes back to front. Light is always
from the upper left, as in the rest of the pack.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence

from PIL import Image, ImageDraw

from palette import SHADOW
from pix import BAYER, CLEAR, Color, Pix, Ramp, mix, rgb

Shape = set[tuple[int, int]]

DEEP: Color = (44, 18, 38)       # shadows lean violet-brown
WARM: Color = (255, 222, 160)    # highlights lean amber


def mk(mid: str, spread: float = 1.0) -> Ramp:
    """A five-tone ramp, dark to light, around a middle colour: shadows toward violet-brown, lights toward amber."""
    m = rgb(mid)
    return (mix(m, DEEP, 0.66 * spread), mix(m, DEEP, 0.34 * spread), m, mix(m, WARM, 0.26 * spread), mix(m, WARM, 0.52 * spread))


# ---------------------------------------------------------------------- shapes

def ell(cx: float, cy: float, rx: float, ry: float) -> Shape:
    out: Shape = set()
    for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 2):
        for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def box(x: int, y: int, w: int, h: int) -> Shape:
    return {(i, j) for j in range(y, y + h) for i in range(x, x + w)}


def poly(points: Sequence[tuple[float, float]]) -> Shape:
    xs = [int(p[0]) for p in points]
    ys = [int(p[1]) for p in points]
    ox, oy = min(xs) - 2, min(ys) - 2
    im = Image.new("L", (max(xs) - ox + 4, max(ys) - oy + 4), 0)
    ImageDraw.Draw(im).polygon([(px - ox, py - oy) for px, py in points], fill=255)
    return {(x + ox, y + oy) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))}


def tube(points: Sequence[tuple[float, float, float]]) -> Shape:
    """A capsule chain: (x, y, radius) knots joined by straight runs, radius interpolated (stems, eels, tails)."""
    out: Shape = set()
    for (x0, y0, r0), (x1, y1, r1) in zip(points, points[1:], strict=False):
        n = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) * 2))
        for i in range(n + 1):
            t = i / n
            r = r0 + (r1 - r0) * t
            out |= ell(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, max(0.6, r), max(0.6, r))
    return out


def wave(x0: float, x1: float, cy: float, amp: float, turns: float, r0: float, r1: float, phase: float = 0.0, steps: int = 60,
         bulge: float = 0.0) -> list[tuple[float, float, float]]:
    """Knots of a body that undulates from x0 to x1 (eel, snake): the radius runs r0 to r1 with an optional belly bulge."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        r = r0 + (r1 - r0) * t + bulge * math.sin(math.pi * t)
        pts.append((x0 + (x1 - x0) * t, cy + amp * math.sin(2 * math.pi * turns * t + phase), r))
    return pts


def mirror(s: Shape, w: int) -> Shape:
    return {(w - 1 - x, y) for x, y in s}


def shift(s: Shape, dx: int, dy: int) -> Shape:
    return {(x + dx, y + dy) for x, y in s}


def grow(s: Shape, n: int = 1) -> Shape:
    out = set(s)
    for _ in range(n):
        out |= {(x + dx, y + dy) for x, y in out for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return out


def rim(s: Shape) -> Shape:
    return grow(s) - s


def only(s: Shape, x0: int, y0: int, x1: int, y1: int) -> Shape:
    return {(x, y) for x, y in s if x0 <= x < x1 and y0 <= y < y1}


# ---------------------------------------------------------------------- painting

def shade(p: Pix, s: Shape, ramp: Ramp, base: int | None = None, grad: float = 0.9, dith: bool = False, hi: float = 1.0,
          lo: float = 1.0) -> None:
    """Fills a shape: lit upper-left rim, shaded lower-right rim, and a soft diagonal fall-off inside."""
    if not s:
        return
    n = len(ramp)
    b = n // 2 if base is None else base
    x0, x1 = min(x for x, _ in s), max(x for x, _ in s)
    y0, y1 = min(y for _, y in s), max(y for _, y in s)
    for x, y in s:
        v = float(b)
        if any((x + dx, y + dy) not in s for dx, dy in ((-1, 0), (0, -1), (-1, -1))):
            v += hi
        if any((x + dx, y + dy) not in s for dx, dy in ((1, 0), (0, 1), (1, 1))):
            v -= lo
        elif any((x + dx, y + dy) not in s for dx, dy in ((2, 1), (1, 2), (2, 2))) and x1 - x0 > 5 and y1 - y0 > 5:
            v -= 0.5 * lo
        t = ((x - x0) / max(1, x1 - x0) + (y - y0) / max(1, y1 - y0)) / 2
        v += (0.5 - t) * grad
        i = math.floor(v + (BAYER[y % 4][x % 4] / 16 if dith else 0.5))
        p.px(x, y, ramp[max(0, min(n - 1, i))])


def flat(p: Pix, s: Shape, c: Color) -> None:
    for x, y in s:
        p.px(x, y, c)


def edge(p: Pix, s: Shape, c: Color = SHADOW) -> None:
    """Rings a shape on its outside in the outline tone."""
    for x, y in rim(s):
        p.px(x, y, c)


def part(p: Pix, s: Shape, ramp: Ramp, base: int | None = None, outline: Color | None = SHADOW, **kw: object) -> None:
    shade(p, s, ramp, base, **kw)  # type: ignore[arg-type]
    if outline is not None:
        edge(p, s, outline)


def dots(p: Pix, pts: Iterable[tuple[int, int]], c: Color) -> None:
    for x, y in pts:
        p.px(x, y, c)


def clipped(s: Shape, inside: Shape) -> Shape:
    return s & inside


def line_set(x0: float, y0: float, x1: float, y1: float) -> Shape:
    n = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
    return {(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)}


def stroke(p: Pix, pts: Iterable[tuple[int, int]], c: Color, inside: Shape | None = None) -> None:
    for x, y in pts:
        if inside is None or (x, y) in inside:
            p.px(x, y, c)


def bevel_rim(p: Pix, s: Shape, light: Color, dark: Color) -> None:
    """Re-lights a flat-coloured shape: light on its upper-left rim, dark on its lower-right rim."""
    for x, y in s:
        if any((x + dx, y + dy) not in s for dx, dy in ((-1, 0), (0, -1))):
            p.px(x, y, light)
        elif any((x + dx, y + dy) not in s for dx, dy in ((1, 0), (0, 1))):
            p.px(x, y, dark)


# ---------------------------------------------------------------------- shared ramps

LEAF = mk("#4d7d3b")
LEAF_DK = mk("#2f5a3a")
LEAF_YEL = mk("#8a9a3c")
SOIL = mk("#5a3a22")
STRAW = mk("#c49a4c")
CREAM = mk("#d9c9a0")
BONE = mk("#c9b999")
OAKR = mk("#6a4428")
PALER = mk("#a07a48")
CLAY = mk("#b0602f")
PEWTER = mk("#7d8088")
IRONR = mk("#4a4a54")
BRASSR = mk("#c89a38")
RED = mk("#b8422f")
WINER = mk("#7a272b")
PURPLE = mk("#7a4a8c")
BLUE = mk("#4a6e98")
TEAL = mk("#3e8a86")
FLESH = mk("#c25b55")
PINK = mk("#e6a39a")
LINEN_R = mk("#cfc4a8")
BROWN = mk("#7a5030")
GREY = mk("#8a8480")
WAX_RED = mk("#a8302e")


def finish(p: Pix, outline: bool = False) -> Image.Image:
    if outline:
        p.outline(SHADOW)
    return p.im


# ---------------------------------------------------------------------- placing

Drawer = Callable[[], Image.Image]


def anchored(fn: Drawer, size: tuple[int, int], box_: tuple[int, int, int, int], mode: str = "b") -> Drawer:
    """Wraps a drawing so its content sits where the game's original content sits: same horizontal centre, and bottom ('b'),
    middle ('c') or top ('t') aligned inside the original's occupied box (x0, y0, x1, y1)."""

    def run() -> Image.Image:
        im = fn()
        bb = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if bb is None:
            return im
        tx0, ty0, tx1, ty1 = box_
        dx = (tx0 + tx1) // 2 - (bb[0] + bb[2]) // 2
        if mode == "b":
            dy = ty1 - bb[3]
        elif mode == "t":
            dy = ty0 - bb[1]
        else:
            dy = (ty0 + ty1) // 2 - (bb[1] + bb[3]) // 2
        out = Image.new("RGBA", size, CLEAR)
        out.paste(im, (dx, dy))
        return out

    return run
