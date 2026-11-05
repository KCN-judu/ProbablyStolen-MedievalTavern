"""Helpers for the undercroft picture: a pure-Pillow canvas with ordered-dither shading, polygon masks, value noise and a
stroke lettering that is drawn big and thresholded, so it stays made of whole pixels."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence

from PIL import Image, ImageDraw

W, H = 640, 360
Color = tuple[int, int, int]
Ramp = Sequence[Color]
Pt = tuple[float, float]
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def hx(s: str) -> Color:
    s = s.lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def bayer(x: int, y: int) -> float:
    return (BAYER[y & 3][x & 3] + 0.5) / 16


def lerp(a: Color, b: Color, t: float) -> Color:
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


def shade(ramp: Ramp, v: float, x: int, y: int) -> Color:
    """Ramp tone for value v (0 dark to 1 light), dithered between neighbouring tones."""
    t = min(max(v, 0.0), 1.0) * (len(ramp) - 1)
    lo = int(t)
    if lo >= len(ramp) - 1:
        return ramp[-1]
    return ramp[lo + 1] if t - lo > bayer(x, y) else ramp[lo]


class Noise:
    """Smooth value noise at one feature size: a tiny random picture stretched to the canvas."""

    def __init__(self, size: float, seed: int, sx: float = 1.0, sy: float = 1.0) -> None:
        rnd = random.Random(seed)
        n = max(2, round(W / (size * sx))), max(2, round(H / (size * sy)))
        small = Image.new("L", n)
        small.putdata([rnd.randrange(256) for _ in range(n[0] * n[1])])
        self.pa = small.resize((W, H), Image.BICUBIC).load()

    def __call__(self, x: int, y: int) -> float:
        return self.pa[min(max(x, 0), W - 1), min(max(y, 0), H - 1)] / 255


def poly_mask(points: Sequence[Pt]) -> Image.Image:
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for x, y in points], fill=255)
    return m


def empty() -> Image.Image:
    return Image.new("L", (W, H), 0)


def cells(mask: Image.Image) -> list[tuple[int, int]]:
    """Every pixel set in a mask."""
    box = mask.getbbox()
    if not box:
        return []
    pa = mask.load()
    return [(x, y) for y in range(box[1], box[3]) for x in range(box[0], box[2]) if pa[x, y]]


def stroke_mask(lines: Sequence[Sequence[Pt]], width: float, closed: bool = False) -> Image.Image:
    """Polylines drawn 4x with round joints and thresholded back: crisp whole-pixel strokes."""
    big = Image.new("L", (W * 4, H * 4), 0)
    d = ImageDraw.Draw(big)
    r = width * 2
    for line in lines:
        pts = [(x * 4, y * 4) for x, y in line]
        if closed:
            pts.append(pts[0])
        d.line(pts, fill=255, width=max(1, round(width * 4)), joint="curve")
        for x, y in (pts[0], pts[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return big.resize((W, H), Image.BOX).point(lambda v: 255 if v >= 128 else 0)


def grow(mask: Image.Image, dx: int, dy: int) -> Image.Image:
    """The mask moved by (dx, dy), for offsets and outlines."""
    out = Image.new("L", (W, H), 0)
    out.paste(mask, (dx, dy))
    return out


def union(*masks: Image.Image) -> Image.Image:
    out = masks[0].copy()
    for m in masks[1:]:
        out.paste(255, mask=m)
    return out


def minus(a: Image.Image, b: Image.Image) -> Image.Image:
    out = a.copy()
    out.paste(0, mask=b)
    return out


def inside(mask: Image.Image) -> Callable[[int, int], bool]:
    pa = mask.load()
    return lambda x, y: 0 <= x < W and 0 <= y < H and pa[x, y] > 0


class Canvas:
    def __init__(self, seed: int) -> None:
        self.img = Image.new("RGB", (W, H), (0, 0, 0))
        self.pa = self.img.load()
        self.rnd = random.Random(seed)

    def put(self, x: int, y: int, c: Color) -> None:
        if 0 <= x < W and 0 <= y < H:
            self.pa[x, y] = c

    def get(self, x: int, y: int) -> Color:
        return self.pa[min(max(x, 0), W - 1), min(max(y, 0), H - 1)]

    def paint(self, mask: Image.Image, fn: Callable[[int, int], Color | None]) -> None:
        """Calls fn(x, y) for every pixel in the mask; a returned colour replaces the pixel."""
        for x, y in cells(mask):
            c = fn(x, y)
            if c is not None:
                self.pa[x, y] = c

    def flat(self, mask: Image.Image, c: Color) -> None:
        self.paint(mask, lambda x, y: c)

    def mixin(self, mask: Image.Image, c: Color, t: float) -> None:
        """Dithered wash of colour c at strength t over what is there."""
        self.paint(mask, lambda x, y: c if t > bayer(x, y) else None)

    def edges(self, mask: Image.Image, light: Color | None, dark: Color | None, lx: int = -1, ly: int = -1) -> None:
        """Lit rim on the sides of a shape facing (lx, ly) and a dark rim on the opposite sides."""
        ins = inside(mask)
        for x, y in cells(mask):
            if light and (not ins(x + lx, y) or not ins(x, y + ly)):
                self.pa[x, y] = light
            elif dark and (not ins(x - lx, y) or not ins(x, y - ly)):
                self.pa[x, y] = dark

    def outline(self, mask: Image.Image, c: Color) -> None:
        ins = inside(mask)
        box = mask.getbbox()
        if not box:
            return
        for y in range(box[1] - 1, box[3] + 1):
            for x in range(box[0] - 1, box[2] + 1):
                if not ins(x, y) and (ins(x + 1, y) or ins(x - 1, y) or ins(x, y + 1) or ins(x, y - 1)):
                    self.put(x, y, c)


# Letter strokes in a unit box (x 0..1 across, y 0..1 down). Our own forms: blunt and slightly leaning, for painted lettering.
LETTERS: dict[str, list[list[Pt]]] = {
    "A": [[(0, 1), (0.44, 0), (0.9, 1)], [(0.2, 0.64), (0.7, 0.64)]],
    "B": [[(0, 0), (0, 1)], [(0, 0), (0.68, 0.02), (0.84, 0.22), (0.68, 0.47), (0, 0.5)], [(0, 0.5), (0.74, 0.52), (0.9, 0.76), (0.72, 1), (0, 1)]],
    "D": [[(0, 0), (0, 1), (0.6, 0.98), (0.9, 0.7), (0.9, 0.3), (0.6, 0.02), (0, 0)]],
    "E": [[(0.9, 0), (0, 0), (0, 1), (0.9, 1)], [(0, 0.5), (0.64, 0.5)]],
    "I": [[(0.4, 0), (0.4, 1)]],
    "K": [[(0, 0), (0, 1)], [(0.86, 0), (0.02, 0.6)], [(0.26, 0.42), (0.92, 1)]],
    "N": [[(0, 1), (0, 0), (0.9, 1), (0.9, 0)]],
    "O": [[(0.45, 0), (0.86, 0.2), (0.92, 0.8), (0.45, 1), (0.02, 0.8), (0.04, 0.2)]],
    "R": [[(0, 1), (0, 0), (0.7, 0.02), (0.86, 0.24), (0.7, 0.5), (0, 0.5)], [(0.4, 0.5), (0.92, 1)]],
    "T": [[(0, 0), (0.96, 0)], [(0.48, 0), (0.48, 1)]],
    "U": [[(0, 0), (0, 0.72), (0.2, 1), (0.7, 1), (0.9, 0.72), (0.9, 0)]],
    "W": [[(0, 0), (0.2, 1), (0.46, 0.4), (0.72, 1), (0.92, 0)]],
}


def letters(text: str, x: float, y: float, h: float, w: float, gap: float, tilt: float = 0.0, rise: float = 0.0,
            slant: float = 0.0, jitter: float = 0.0, seed: int = 0) -> list[list[Pt]]:
    """Polylines for a word. `w` is a letter's width, `rise` the climb per letter (px), `slant` leans the tops right,
    `tilt` shears the whole line downhill (px per px of run). Spaces are a letter wide."""
    rnd = random.Random(seed)
    out: list[list[Pt]] = []
    cx = x
    for i, ch in enumerate(text):
        if ch == " ":
            cx += w + gap
            continue
        oy = y - i * rise + (cx - x) * tilt
        for line in LETTERS[ch]:
            out.append([(cx + u * w + (1 - v) * slant + rnd.uniform(-jitter, jitter),
                         oy + v * h + rnd.uniform(-jitter, jitter)) for u, v in line])
        cx += w + gap
    return out


def wobble(pts: Sequence[Pt], amount: float, rnd: random.Random) -> list[Pt]:
    return [(x + rnd.uniform(-amount, amount), y + rnd.uniform(-amount, amount)) for x, y in pts]


def arc_pts(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, n: int = 24) -> list[Pt]:
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]
