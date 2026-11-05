"""A small pixel-art toolkit on Pillow: a canvas with hard-edged drawing, ordered dithering, and light.

Everything draws without anti-aliasing, so a picture stays made of whole pixels. A `Pix` is a canvas; the methods paint
into it (replacing pixels, alpha included) and return nothing. The rest of the package is pure functions that take
sizes and a seed and return a `Pix` or an `Image`, so the same input always gives the same picture.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Sequence
from typing import Final, TypeAlias

from PIL import Image, ImageChops, ImageDraw

Color: TypeAlias = tuple[int, int, int] | tuple[int, int, int, int]
Ramp: TypeAlias = Sequence[Color]       # dark to light

CLEAR: Final[Color] = (0, 0, 0, 0)
BAYER: Final = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def rgb(hex6: str) -> Color:
    """'#rrggbb' to a colour."""
    h = hex6.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(a: Color, b: Color, t: float) -> Color:
    """A point t of the way from a to b (0 gives a, 1 gives b), opaque."""
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


class Pix:
    """A canvas of `w` x `h` pixels, transparent unless given a fill, with a seeded random source."""

    def __init__(self, w: int, h: int, fill: Color = CLEAR, seed: int = 0) -> None:
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), fill if len(fill) == 4 else (*fill, 255))
        self.draw = ImageDraw.Draw(self.im)
        self.rng = random.Random(seed)

    # ------------------------------------------------------------------ plain shapes

    def px(self, x: int, y: int, c: Color) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), c if len(c) == 4 else (*c, 255))

    def get(self, x: int, y: int) -> tuple[int, int, int, int]:
        return self.im.getpixel((x, y))  # type: ignore[return-value]

    def rect(self, x: int, y: int, w: int, h: int, c: Color) -> None:
        if w > 0 and h > 0:
            self.draw.rectangle((x, y, x + w - 1, y + h - 1), fill=c)

    def frame(self, x: int, y: int, w: int, h: int, c: Color) -> None:
        if w > 0 and h > 0:
            self.draw.rectangle((x, y, x + w - 1, y + h - 1), outline=c)

    def hline(self, x: int, y: int, w: int, c: Color) -> None:
        self.rect(x, y, w, 1, c)

    def vline(self, x: int, y: int, h: int, c: Color) -> None:
        self.rect(x, y, 1, h, c)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: Color) -> None:
        self.draw.line((x0, y0, x1, y1), fill=c)

    def poly(self, points: Sequence[tuple[int, int]], c: Color) -> None:
        self.draw.polygon(list(points), fill=c)

    def ellipse(self, x: int, y: int, w: int, h: int, c: Color) -> None:
        self.draw.ellipse((x, y, x + w - 1, y + h - 1), fill=c)

    def erase(self, x: int, y: int, w: int, h: int) -> None:
        """Makes a rectangle transparent (a window cut out of a wall)."""
        self.rect(x, y, w, h, CLEAR)

    def paste(self, other: Pix | Image.Image, x: int, y: int) -> None:
        """Lays another picture over this one, honouring its transparency."""
        image = other.im if isinstance(other, Pix) else other
        x0, y0 = max(0, -x), max(0, -y)
        x1, y1 = min(image.width, self.w - x), min(image.height, self.h - y)
        if x1 > x0 and y1 > y0:
            self.im.alpha_composite(image.crop((x0, y0, x1, y1)), (x + x0, y + y0))

    # ------------------------------------------------------------------ texture

    def dither(self, x: int, y: int, w: int, h: int, c: Color, density: float) -> None:
        """Paints `c` on a share `density` (0 to 1) of the pixels of a rectangle, in an ordered pattern."""
        level = round(density * 16)
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                if BAYER[yy % 4][xx % 4] < level:
                    self.px(xx, yy, c)

    def speckle(self, x: int, y: int, w: int, h: int, colors: Sequence[Color], share: float) -> None:
        """Random single pixels: a share of the rectangle, each in one of the colours."""
        for _ in range(round(w * h * share)):
            self.px(x + self.rng.randrange(w), y + self.rng.randrange(h), self.rng.choice(list(colors)))

    def gradient(self, x: int, y: int, w: int, h: int, top: Color, bottom: Color, steps: int = 6) -> None:
        """Vertical shading in a few bands with dithered joints, so it reads as pixel art and not as a smooth blend."""
        for i in range(steps):
            y0, y1 = y + h * i // steps, y + h * (i + 1) // steps
            self.rect(x, y0, w, y1 - y0, mix(top, bottom, i / max(1, steps - 1)))
            if i:
                self.dither(x, y0, w, 1, mix(top, bottom, (i - 1) / max(1, steps - 1)), 0.5)

    def glow(self, cx: int, cy: int, r: int, c: Color, strength: float = 1.0) -> None:
        """A pool of light: concentric dithered rings, strongest at the centre, laid over what is there."""
        for yy in range(max(0, cy - r), min(self.h, cy + r + 1)):
            for xx in range(max(0, cx - r), min(self.w, cx + r + 1)):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if d <= r:
                    level = (1 - d / r) ** 1.6 * strength
                    if BAYER[yy % 4][xx % 4] < round(level * 16):
                        self.px(xx, yy, c)

    def outline(self, c: Color, inside: bool = False) -> None:
        """A one-pixel rim around every opaque shape (on the transparent side, or just inside it)."""
        src = self.im.copy()
        for y in range(self.h):
            for x in range(self.w):
                here = src.getpixel((x, y))[3] > 8  # type: ignore[index]
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    there = 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 8  # type: ignore[index]
                    if (not inside and not here and there) or (inside and here and not there):
                        self.px(x, y, c)
                        break

    def bevel(self, x: int, y: int, w: int, h: int, light: Color, dark: Color) -> None:
        """A one-pixel highlight on the top and left edges of a rectangle and a shadow on the bottom and right."""
        self.hline(x, y, w, light)
        self.vline(x, y, h, light)
        self.hline(x, y + h - 1, w, dark)
        self.vline(x + w - 1, y, h, dark)

    def clip(self, points: Sequence[tuple[int, int]]) -> None:
        """Keeps only what lies inside a polygon; everything outside becomes transparent."""
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).polygon(list(points), fill=255)
        self.im.putalpha(ImageChops.multiply(self.im.getchannel("A"), mask))
        self.draw = ImageDraw.Draw(self.im)

    def fade_alpha(self, x: int, y: int, w: int, h: int, top: int, bottom: int) -> None:
        """Scales the alpha of a rectangle from `top` (0 to 255) at its first row to `bottom` at its last."""
        for yy in range(max(0, y), min(self.h, y + h)):
            k = (top + (bottom - top) * (yy - y) / max(1, h - 1)) / 255
            for xx in range(max(0, x), min(self.w, x + w)):
                r, g, b, a = self.get(xx, yy)
                if a:
                    self.im.putpixel((xx, yy), (r, g, b, round(a * k)))

    def finish(self) -> Image.Image:
        return self.im


def tile(size: tuple[int, int], draw: Callable[[Pix], object]) -> Image.Image:
    """Builds a picture of `size` by handing a fresh `Pix` to `draw` (a function of one Pix)."""
    p = Pix(*size)
    draw(p)
    return p.im


def scale_ramp(ramp: Ramp, amount: float) -> list[Color]:
    """The same ramp pushed toward black (amount < 0) or white (amount > 0)."""
    target: Color = (255, 255, 255) if amount > 0 else (0, 0, 0)
    return [mix(c if len(c) == 3 else c[:3], target, abs(amount)) for c in ramp]


def pick(rng: random.Random, items: Iterable[Color]) -> Color:
    return rng.choice(list(items))
