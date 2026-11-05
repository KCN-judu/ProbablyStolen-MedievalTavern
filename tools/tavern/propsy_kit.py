"""Shared helpers of the `propsy_` modules: drawing a plane of the shop by inverse mapping, and shadows.

A plane that recedes toward the shop's vanishing point `VP` is painted pixel by pixel: for every screen pixel the helper
works out the plane's own coordinates (depth `u`, lateral position in near-edge pixels), and a colour function says what
lies there. That way grain, rims and inlays follow the perspective instead of being drawn as flat shapes and sheared.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from PIL import Image, ImageDraw

from pix import Color, Pix
from shopx_persp import VP, overlay_shadow

Point = tuple[float, float]


def scale_to_vp(pt: Point, s: float) -> Point:
    """The point moved along its line to VP so that it sits at `s` of its distance (s = 1 is where it is)."""
    return VP[0] + (pt[0] - VP[0]) * s, VP[1] + (pt[1] - VP[1]) * s


def round_pts(pts: Sequence[Point]) -> list[tuple[int, int]]:
    return [(round(x), round(y)) for x, y in pts]


def mask_of(size: tuple[int, int], pts: Sequence[Point]) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(round_pts(pts), fill=255)
    return m


def fill_poly(p: Pix, pts: Sequence[Point], colour_at: Callable[[int, int], Color | None]) -> None:
    """Calls `colour_at(x, y)` for each pixel inside the polygon and paints what it returns (None leaves it alone)."""
    m = mask_of((p.w, p.h), pts)
    x0, y0, x1, y1 = m.getbbox() or (0, 0, 0, 0)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if m.getpixel((x, y)):
                c = colour_at(x, y)
                if c is not None:
                    p.px(x, y, c)


def cast_shadow(p: Pix, footprint: Sequence[Point], shift: tuple[float, float], bbox: tuple[int, int, int, int],
                strength: float = 0.9, alpha: int = 200) -> None:
    """A soft contact shadow on what is below: the footprint of an object pushed along `shift` in steps, strongest
    next to the object and weaker the farther it reaches. Only transparent pixels get it, and only inside `bbox`."""
    x0, y0, x1, y1 = bbox
    steps = (0.2, 0.45, 0.7, 1.0)
    masks = [mask_of((p.w, p.h), [(x + shift[0] * t, y + shift[1] * t) for x, y in footprint]) for t in steps]

    def level(x: int, y: int) -> float:
        for t, m in zip(steps, masks):
            if m.getpixel((x, y)):
                return strength * (1.15 - t)
        return 0.0

    overlay_shadow(p, x0, y0, x1, y1, level, alpha=alpha)


def clamp_to_bbox(img: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    """Makes everything outside the rectangle transparent (the game's layer only fills its own area)."""
    x0, y0, x1, y1 = bbox
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img.crop(bbox), (x0, y0))
    return out


def ellipse_ry(width: float, y: float, k: float = 0.2) -> int:
    """Half height of a horizontal circle of this width on a surface at screen row `y`."""
    return max(1, round(width * (y - VP[1]) / 2000 * 2 * k * 5 / 2))


__all__ = ["scale_to_vp", "round_pts", "mask_of", "fill_poly", "cast_shadow", "clamp_to_bbox", "ellipse_ry", "math"]
