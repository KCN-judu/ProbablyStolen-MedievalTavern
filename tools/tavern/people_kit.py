"""Masks, shading and colour ramps for drawing people: the small toolkit under the figure generator.

A figure is built from masks (single-channel pictures, 255 inside a shape). `paint` fills a mask from a ramp and shades
it by itself: a lighter rim where the upper left edge is, a darker band with a dithered joint where the lower right edge
is, and an inside outline. That one routine gives clothes, skin and hair the same light (from the upper left) without
hand-placing every highlight. Figures are drawn on a canvas taller than the picture (`CH`) so the shapes that run off
the bottom do not get a shaded rim there; the last rows are cropped away.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from functools import lru_cache, reduce
from typing import Final

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from palette import FLAME, SHADOW
from pix import BAYER, Color, Pix, Ramp, mix, rgb

W: Final = 288                  # the width of every portrait frame
H: Final = 211                  # and its height
CH: Final = 260                 # the drawing canvas is taller, so nothing is rimmed at the bottom edge
CX: Final = 144                 # the figure is symmetrical about the line between columns 143 and 144

Mask = Image.Image


# ---------------------------------------------------------------------------------------------- masks


def blank() -> Mask:
    """An empty mask the size of the drawing canvas."""
    return Image.new("L", (W, CH), 0)


def poly(points: Sequence[tuple[float, float]]) -> Mask:
    """The mask of a polygon."""
    m = blank()
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for x, y in points], fill=255)
    return m


def rect(x0: int, y0: int, x1: int, y1: int) -> Mask:
    """The mask of a rectangle; both corners are inside it."""
    m = blank()
    ImageDraw.Draw(m).rectangle((x0, y0, x1, y1), fill=255)
    return m


def oval(cx: float, cy: float, rx: float, ry: float) -> Mask:
    """The mask of an ellipse with its centre and radii (pixel centres), edges hard."""
    m = blank()
    ImageDraw.Draw(m).ellipse((round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)), fill=255)
    return m


def stroke(points: Sequence[tuple[float, float]], width: int = 1) -> Mask:
    """The mask of a polyline of the given width."""
    m = blank()
    ImageDraw.Draw(m).line([(round(x), round(y)) for x, y in points], fill=255, width=width)
    return m


def union(*masks: Mask) -> Mask:
    """Everything that is in any of the masks."""
    return reduce(ImageChops.lighter, masks)


def minus(a: Mask, *others: Mask) -> Mask:
    """What is in `a` but in none of the others."""
    for o in others:
        a = ImageChops.subtract(a, o)
    return a


def both(a: Mask, b: Mask) -> Mask:
    """What is in both masks."""
    return ImageChops.darker(a, b)


def shift(m: Mask, dx: int, dy: int) -> Mask:
    """The mask moved by whole pixels; what leaves the canvas is lost, nothing wraps."""
    out = blank()
    out.paste(m, (dx, dy))
    return out


def grow(m: Mask, n: int = 1) -> Mask:
    """The mask expanded by n pixels in every direction (square brush)."""
    return m.filter(ImageFilter.MaxFilter(2 * n + 1)) if n else m


def shrink(m: Mask, n: int = 1) -> Mask:
    """The mask eroded by n pixels."""
    return m.filter(ImageFilter.MinFilter(2 * n + 1)) if n else m


def mirror(m: Mask) -> Mask:
    """The mask reflected about the figure's axis."""
    return m.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


@lru_cache(maxsize=None)
def bayer(level: int) -> Mask:
    """An ordered-dither mask covering `level` sixteenths of the canvas."""
    m = blank()
    px = m.load()
    assert px is not None
    for y in range(CH):
        for x in range(W):
            if BAYER[y % 4][x % 4] < level:
                px[x, y] = 255
    return m


def checker(period: int = 2, phase: int = 0) -> Mask:
    """A chessboard of pixels, for mail and weave."""
    m = blank()
    px = m.load()
    assert px is not None
    for y in range(CH):
        for x in range(W):
            if (x + y + phase) % period == 0:
                px[x, y] = 255
    return m


def columns(fn: Callable[[int], tuple[float, float] | None]) -> Mask:
    """A mask built column by column: `fn(x)` gives (top, bottom) rows covered (bottom not included) or None."""
    m = blank()
    px = m.load()
    assert px is not None
    for x in range(W):
        r = fn(x)
        if r is not None:
            for y in range(max(0, round(r[0])), min(CH, round(r[1]))):
                px[x, y] = 255
    return m


# ---------------------------------------------------------------------------------------------- colour


def tone(base: Color) -> Ramp:
    """A five-tone ramp around `base` (the third): warm violet-brown shadows, amber lights, never black or white."""
    b = (base[0], base[1], base[2])
    return (mix(b, SHADOW, 0.78), mix(b, SHADOW, 0.46), b, mix(b, FLAME[3][:3], 0.2), mix(b, FLAME[3][:3], 0.42))


def skin_tone(base: Color) -> Ramp:
    """A skin ramp: shadows go to a warm red-brown, lights to amber, so every skin tone stays alive."""
    b = (base[0], base[1], base[2])
    return (mix(b, (52, 22, 36), 0.72), mix(b, (112, 44, 54), 0.42), b, mix(b, (255, 222, 160), 0.3), mix(b, (255, 232, 180), 0.52))


def hx(code: str) -> Ramp:
    """A tone ramp from a '#rrggbb' base."""
    return tone(rgb(code))


SKINS: Final[tuple[Ramp, ...]] = tuple(skin_tone(rgb(c)) for c in (
    "#e6bc98",      # 0 fair
    "#dca27c",      # 1 light, ruddy
    "#c99468",      # 2 olive
    "#b57c4e",      # 3 tan
    "#93603a",      # 4 brown
    "#6e432a",      # 5 deep brown
    "#4d2e20",      # 6 deep
    "#efcfb2",      # 7 pale
))

HAIRS: Final[dict[str, Ramp]] = {
    "black": hx("#2a2226"), "dark": hx("#43302a"), "brown": hx("#6a4630"), "chestnut": hx("#8a5434"),
    "ginger": hx("#b8622e"), "blond": hx("#c8a45a"), "straw": hx("#dcc27c"), "grey": hx("#8f8a88"),
    "white": hx("#cfc8c0"), "auburn": hx("#9a4a2a"),
}


# ---------------------------------------------------------------------------------------------- painting


def put(p: Pix, m: Mask, c: Color) -> None:
    """Fills a mask with one colour."""
    p.im.paste(c if len(c) == 4 else (*c, 255), mask=m)


def paint(p: Pix, m: Mask, ramp: Ramp, d: int = 3, edge: Color | None = None, soft: bool = True) -> None:
    """Fills `m` with the ramp's middle tone and shades it: a light rim on the upper left, a shadow band on the lower
    right with a dithered joint, and an inside outline (`edge`, default the ramp's darkest)."""
    put(p, m, ramp[2])
    lo = minus(m, shift(m, -d, -d))
    if soft:
        wide = minus(m, shift(m, -2 * d - 1, -2 * d - 1), lo)
        put(p, both(wide, bayer(6)), ramp[1])
    put(p, lo, ramp[1])
    hi = minus(m, shift(m, max(1, d - 1), max(1, d - 1)))
    put(p, hi, ramp[3])
    if soft:
        put(p, both(minus(m, shift(m, 2 * d, 2 * d), hi), bayer(3)), ramp[3])
    rim = minus(m, shrink(m))
    put(p, rim, edge if edge is not None else ramp[0])


def overlay(p: Pix, m: Mask, c: Color, level: int = 8) -> None:
    """Lays a colour over a mask in an ordered dither of `level` sixteenths."""
    put(p, both(m, bayer(level)), c)


def pattern(p: Pix, m: Mask, c: Color, period: int = 2, phase: int = 0) -> None:
    """A chessboard of one colour over a mask (mail, weave, felt)."""
    put(p, both(m, checker(period, phase)), c)


def strands(p: Pix, m: Mask, ramp: Ramp, origin: tuple[int, int], n: int, seed: int, spread: float = 1.0) -> None:
    """Hair or fur flow: short lines radiating from `origin`, light and dark, kept inside `m`."""
    layer = blank()
    dark = blank()
    ld, dd = ImageDraw.Draw(layer), ImageDraw.Draw(dark)
    rng = random.Random(seed)
    x0, y0, x1, y1 = m.getbbox() or (0, 0, 1, 1)
    for i in range(n):
        tx = rng.uniform(x0, x1)
        ty = rng.uniform(y0, y1)
        ang = math.atan2(ty - origin[1], tx - origin[0])
        ln = rng.randint(4, 9)
        sx = tx - math.cos(ang) * ln * spread
        sy = ty - math.sin(ang) * ln * spread
        (ld if i % 2 else dd).line((round(sx), round(sy), round(tx), round(ty)), fill=255)
    put(p, both(layer, shrink(m)), ramp[3])
    put(p, both(dark, shrink(m)), ramp[1])


def outline_all(p: Pix, c: Color = SHADOW) -> None:
    """A one-pixel rim of `c` around everything drawn (outside it), so the figure stands out from any ground."""
    a = p.im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
    ring = minus(grow(a), a)
    put(p, ring, c)
