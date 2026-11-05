"""Shared machinery of the portrait painter: a canvas with direct pixel access, lighting, and shaded fills.

Where `people_kit.paint` shades a mask by its distance to the edge, here every pixel of a shape gets a light value from a
small normal model (a dome, a cylinder), the value is cut into four bands, and each band is a tone of a ramp. The hard
bands, with no dither, are what the game's own busts do; a little ordered dither is kept for cloth and hair texture.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence

from people_kit import CH, W, Mask, blank
from pix import BAYER, Color, Pix, Ramp, mix

LIGHT = (-0.52, -0.56, 0.64)         # upper left, towards the viewer
CUTS = (0.10, 0.38, 0.62, 0.90)       # light values that start tones 1..4 of a ramp

Shade = Callable[[int, int], float]


def pixels(m: Mask) -> Iterable[tuple[int, int]]:
    """Every (x, y) inside a mask, row by row."""
    box = m.getbbox()
    if box is None:
        return
    px = m.load()
    assert px is not None
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if px[x, y]:
                yield x, y


def inside(m: Mask, x: int, y: int) -> bool:
    px = m.load()
    return 0 <= x < W and 0 <= y < CH and px is not None and px[x, y] > 0


def band(v: float, cuts: Sequence[float] = CUTS) -> int:
    """The index of the tone for a light value."""
    return sum(v > c for c in cuts)


def dome(cx: float, cy: float, rx: float, ry: float, flat: float = 0.0) -> Shade:
    """Light on an ellipsoid: bright towards the upper left, dark on the lower right."""
    def f(x: int, y: int) -> float:
        nx = max(-1.0, min(1.0, (x + 0.5 - cx) / rx))
        ny = max(-1.0, min(1.0, (y + 0.5 - cy) / ry))
        nz = math.sqrt(max(0.05, 1 - (nx * nx) * (1 - flat) - 0.45 * ny * ny))
        return nx * LIGHT[0] + ny * LIGHT[1] * 0.7 + nz * LIGHT[2]
    return f


def cylinder(cx: float, r: float, y0: float = 0, y1: float = 0, base: float = 0.0) -> Shade:
    """Light on a vertical cylinder around column `cx`; optionally darker towards the bottom (y0 to y1)."""
    def f(x: int, y: int) -> float:
        nx = max(-1.0, min(1.0, (x + 0.5 - cx) / r))
        nz = math.sqrt(max(0.05, 1 - nx * nx))
        v = nx * LIGHT[0] + nz * LIGHT[2] + 0.26 + base
        if y1 > y0:
            v -= 0.34 * max(0.0, min(1.0, (y - y0) / (y1 - y0)))
        return v
    return f


def fill(p: Pix, m: Mask, ramp: Ramp, shade: Shade, cuts: Sequence[float] = CUTS, texture: float = 0.0) -> None:
    """Paints a mask with one ramp, each pixel by its light value; `texture` (0-0.3) jitters the value by an ordered
    pattern so cloth and hair do not look like plastic."""
    pa = p.im.load()
    assert pa is not None
    top = len(ramp) - 1
    for x, y in pixels(m):
        v = shade(x, y)
        if texture:
            v += (BAYER[y % 4][x % 4] / 15 - 0.5) * texture * 0.6
        i = min(top, band(v, cuts))
        c = ramp[i]
        pa[x, y] = c if len(c) == 4 else (*c, 255)


def flat(p: Pix, m: Mask, c: Color) -> None:
    """Fills a mask with one colour."""
    p.im.paste(c if len(c) == 4 else (*c, 255), mask=m)


def put_px(pa: object, x: int, y: int, c: Color) -> None:
    if 0 <= x < W and 0 <= y < CH:
        pa[x, y] = c if len(c) == 4 else (*c, 255)  # type: ignore[index]


def hl(p: Pix, x: int, y: int, n: int, c: Color) -> None:
    """A horizontal run of pixels (clipped)."""
    for i in range(n):
        p.px(x + i, y, c)


def vl(p: Pix, x: int, y: int, n: int, c: Color) -> None:
    for i in range(n):
        p.px(x, y + i, c)


def trace(p: Pix, pts: Sequence[tuple[float, float]], c: Color, m: Mask | None = None) -> None:
    """A one-pixel polyline through the points (Bresenham between them), kept inside `m` when given."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(n) + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            if m is None or inside(m, x, y):
                p.px(x, y, c)


def curve(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], n: int = 14) -> list[tuple[float, float]]:
    """Points of a quadratic bezier from a to c bending towards b."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0],
                    (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]))
    return pts


def tint(c: Color, toward: Color, t: float) -> Color:
    return mix(c, toward, t)


def mirror_x(x: int) -> int:
    """The column mirrored about the figure's axis (between columns 143 and 144)."""
    return 287 - x


def sym(m: Mask) -> Mask:
    """The union of a mask and its mirror image."""
    from PIL import ImageChops
    return ImageChops.lighter(m, m.transpose(0))  # FLIP_LEFT_RIGHT


__all__ = ["CH", "W", "LIGHT", "CUTS", "blank", "pixels", "inside", "band", "dome", "cylinder", "fill", "flat", "hl", "vl",
           "trace", "curve", "tint", "mirror_x", "sym", "put_px"]
