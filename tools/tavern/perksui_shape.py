"""Shape helpers for the small pictures of `perksui_pics`: a shape is a mask painted with a ramp, lit from the upper left.

A mask is an `L` image; `paint` fills it in one tone, adds a lit rim on the sides that face the light and a shaded rim on the
sides that face away, so every little object (a flask, a hat, a coin) gets a bevel without hand-placed highlights.
"""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image, ImageDraw

from pix import Color, Pix, Ramp

Point = tuple[float, float]


class Mask:
    """A drawable 1-bit area the size of the canvas."""

    def __init__(self, w: int, h: int) -> None:
        self.im = Image.new("L", (w, h), 0)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h

    def poly(self, pts: Sequence[Point]) -> Mask:
        self.d.polygon([(round(x), round(y)) for x, y in pts], fill=255)
        return self

    def rect(self, x: int, y: int, w: int, h: int) -> Mask:
        self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=255)
        return self

    def rrect(self, x: int, y: int, w: int, h: int, r: int = 2) -> Mask:
        self.d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=r, fill=255)
        return self

    def oval(self, x: int, y: int, w: int, h: int) -> Mask:
        self.d.ellipse((x, y, x + w - 1, y + h - 1), fill=255)
        return self

    def line(self, x0: int, y0: int, x1: int, y1: int, width: int = 1) -> Mask:
        self.d.line((x0, y0, x1, y1), fill=255, width=width)
        return self

    def cut(self, other: Mask) -> Mask:
        self.im.paste(0, mask=other.im)
        return self

    def at(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self.im.getpixel((x, y)) > 0


def paint(p: Pix, m: Mask, ramp: Ramp, grain: float = 0.0, split: float | None = None) -> None:
    """Fills `m` with `ramp[2]`, a lit rim `ramp[3]` on the top-left edges, a dark rim `ramp[1]` on the bottom-right edges.

    `split` (0 to 1) shades the right part of the shape one tone darker, in a dithered seam, to round it."""
    box = m.im.getbbox()
    if box is None:
        return
    x0, y0, x1, y1 = box
    top = len(ramp) - 1
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not m.at(x, y):
                continue
            c = ramp[min(2, top)]
            if not m.at(x - 1, y) or not m.at(x, y - 1):
                c = ramp[min(3, top)]
            elif not m.at(x + 1, y) or not m.at(x, y + 1):
                c = ramp[1]
            elif split is not None:
                k = (x - x0) / max(1, x1 - x0 - 1)
                if k > split + 0.12 or (k > split and (x + y) % 2 == 0):
                    c = ramp[1]
            if grain and p.rng.random() < grain and c == ramp[min(2, top)]:
                c = ramp[min(3, top)] if p.rng.random() < 0.5 else ramp[1]
            p.px(x, y, c)


def rim(p: Pix, m: Mask, c: Color) -> None:
    """A one-pixel dark edge around a mask, on its outside."""
    box = m.im.getbbox()
    if box is None:
        return
    for y in range(box[1] - 1, box[3] + 1):
        for x in range(box[0] - 1, box[2] + 1):
            if not m.at(x, y) and (m.at(x + 1, y) or m.at(x - 1, y) or m.at(x, y + 1) or m.at(x, y - 1)):
                p.px(x, y, c)


def thick(p: Pix, pts: Sequence[Point], width: int, c: Color) -> None:
    """A polyline of whole pixels, `width` wide, round-jointed."""
    pts_i = [(round(x), round(y)) for x, y in pts]
    p.draw.line(pts_i, fill=c, width=width, joint="curve")
    r = width // 2
    for x, y in (pts_i[0], pts_i[-1]):
        if width > 2:
            p.draw.ellipse((x - r, y - r, x + r - (1 - width % 2), y + r - (1 - width % 2)), fill=c)
