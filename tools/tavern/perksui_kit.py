"""Helpers for the white perk glyphs: a small logical canvas, ASCII pixel art, and placement into the game's frame.

The game tints these pictures itself, so a glyph is white with light grey for inner detail and nothing in between: every
pixel is fully opaque or fully clear. A glyph is drawn on a small logical canvas (one logical pixel is `k` real pixels
for the 100 and 256 pixel pictures, so a big icon keeps the chunky look of a 32 pixel one) and then placed so that its
middle sits on the middle of the occupied area of the original.
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import Final

from PIL import Image

from pix import CLEAR, Color, Pix

W: Final[Color] = (255, 255, 255, 255)
G: Final[Color] = (186, 186, 196, 255)          # light grey: inner detail
LAYOUT: Final = Path(__file__).resolve().parent / "layout.tsv"


@cache
def bbox_of(file: str) -> tuple[int, int, int, int]:
    """x0 y0 x1 y1 of the opaque area of the game's original (the area a replacement should fill)."""
    with LAYOUT.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["file"] == file:
                x0, y0, x1, y1 = map(int, r["bbox"].split())
                return x0, y0, x1, y1
    raise KeyError(file)


class Ic:
    """A logical canvas with white shapes, grey detail and cut-outs."""

    def __init__(self, w: int, h: int) -> None:
        self.p = Pix(w, h)

    def rect(self, x: int, y: int, w: int, h: int, c: Color = W) -> None:
        self.p.rect(x, y, w, h, c)

    def cut(self, x: int, y: int, w: int, h: int) -> None:
        self.p.rect(x, y, w, h, CLEAR)

    def px(self, x: int, y: int, c: Color = W) -> None:
        self.p.px(x, y, c)

    def poly(self, pts: Sequence[tuple[int, int]], c: Color = W) -> None:
        self.p.poly(pts, c)

    def disc(self, x: int, y: int, w: int, h: int, c: Color = W) -> None:
        self.p.ellipse(x, y, w, h, c)

    def ring(self, x: int, y: int, w: int, h: int, t: int = 2, c: Color = W) -> None:
        self.p.ellipse(x, y, w, h, c)
        self.p.ellipse(x + t, y + t, w - 2 * t, h - 2 * t, CLEAR)

    def bar(self, x0: int, y0: int, x1: int, y1: int, t: int = 2, c: Color = W) -> None:
        """A straight stroke `t` pixels thick."""
        self.p.draw.line((x0, y0, x1, y1), fill=c, width=t)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: Color = G) -> None:
        self.p.line(x0, y0, x1, y1, c)

    def art(self, x: int, y: int, rows: Sequence[str], mirror: bool = False) -> None:
        """ASCII pixels: # white, o grey, x cut out, anything else leaves the canvas alone. `mirror` completes a drawing
        given as its left half including the middle column."""
        for j, row in enumerate(rows):
            full = row + row[-2::-1] if mirror else row
            for i, ch in enumerate(full):
                if ch == "#":
                    self.p.px(x + i, y + j, W)
                elif ch == "o":
                    self.p.px(x + i, y + j, G)
                elif ch == "x":
                    self.p.px(x + i, y + j, CLEAR)

    def mirrored(self) -> Ic:
        out = Ic(self.p.w, self.p.h)
        out.p.im = self.p.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return out

    def content(self) -> Image.Image:
        im = self.p.im
        box = im.getbbox()
        return im.crop(box) if box else im


def place(canvas: Pix, ic: Ic, box: tuple[int, int, int, int], k: int = 1, at: tuple[int, int] = (0, 0)) -> None:
    """Scales the glyph's content by `k` and centres it on `box` (x0 y0 x1 y1), shifted by `at` (a cell's corner)."""
    img = ic.content()
    if k > 1:
        img = img.resize((img.width * k, img.height * k), Image.Resampling.NEAREST)
    cx, cy = (box[0] + box[2]) // 2 + at[0], (box[1] + box[3]) // 2 + at[1]
    canvas.paste(img, cx - img.width // 2, cy - img.height // 2)


def hard(im: Image.Image) -> Image.Image:
    """Every pixel fully opaque or fully clear."""
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: 255 if v >= 128 else 0)))
