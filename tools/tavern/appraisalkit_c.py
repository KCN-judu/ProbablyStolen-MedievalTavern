"""Helpers for the appraisal reference pictures and the opened tools: shapes with a bevel, grain, cloth, rivets, glass.

A `Shape` is a mask (what a part covers). `bevel` paints its rim the way the rest of the pack lights things: a dark line
on the silhouette, a lit pixel on the edges that face the upper left, a shaded one on the others. Everything is whole
pixels; random streaks come from the canvas's seeded source, so a picture is the same every time.
"""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image, ImageChops, ImageDraw

from palette import BRASS, GLASS, IRON, LEATHER, LINEN, OAK, PARCHMENT, SHADOW, WOOD
from pix import Color, Pix, Ramp, mix

Point = tuple[int, int]
VIOLET: Color = (38, 30, 44)            # the dark felt and the deepest shade: brown that is nearly violet
OAK_LIT: Ramp = WOOD                    # frames and trays are the lighter, waxed oak


class Shape:
    """A mask the size of a picture. Coordinates are inclusive pixel corners, like the rest of the drawing code."""

    def __init__(self, w: int, h: int) -> None:
        self.w, self.h = w, h
        self.im = Image.new("L", (w, h), 0)
        self._d = ImageDraw.Draw(self.im)
        self._px = self.im.load()

    def rect(self, x0: int, y0: int, x1: int, y1: int, on: bool = True) -> Shape:
        self._d.rectangle((x0, y0, x1, y1), fill=255 if on else 0)
        return self

    def rrect(self, x0: int, y0: int, x1: int, y1: int, r: int, on: bool = True) -> Shape:
        self._d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255 if on else 0)
        return self

    def ellipse(self, x0: int, y0: int, x1: int, y1: int, on: bool = True) -> Shape:
        self._d.ellipse((x0, y0, x1, y1), fill=255 if on else 0)
        return self

    def poly(self, pts: Sequence[Point], on: bool = True) -> Shape:
        self._d.polygon(list(pts), fill=255 if on else 0)
        return self

    def inter(self, other: Shape) -> Shape:
        """A new shape: where both cover."""
        out = Shape(self.w, self.h)
        out.im = ImageChops.multiply(self.im, other.im)
        out._d, out._px = ImageDraw.Draw(out.im), out.im.load()
        return out

    def minus(self, other: Shape) -> Shape:
        """A new shape: where this covers and the other does not."""
        out = Shape(self.w, self.h)
        out.im = ImageChops.subtract(self.im, other.im)
        out._d, out._px = ImageDraw.Draw(out.im), out.im.load()
        return out

    def has(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self._px[x, y] > 0

    def cells(self):
        for y in range(self.h):
            for x in range(self.w):
                if self._px[x, y]:
                    yield x, y

    def box(self) -> tuple[int, int, int, int]:
        b = self.im.getbbox()
        return b if b else (0, 0, 0, 0)


def reach(s: Shape, x: int, y: int, dx: int, dy: int, cap: int) -> int:
    """How many steps from (x, y) in a direction stay inside the shape (capped): 0 means the next pixel is outside."""
    n = 0
    while n < cap and s.has(x + dx * (n + 1), y + dy * (n + 1)):
        n += 1
    return n


def bevel(p: Pix, s: Shape, hi: Color, lo: Color, line: Color | None, width: int = 1, hi2: Color | None = None) -> None:
    """Rim of a part, painted inside its mask: outline, then the lit edge (upper left) or the shaded edge (lower right).
    `hi2` colours a second, softer lit row."""
    off = 1 if line is not None else 0
    for x, y in s.cells():
        a, b = reach(s, x, y, -1, 0, 4), reach(s, x, y, 0, -1, 4)
        c, d = reach(s, x, y, 1, 0, 4), reach(s, x, y, 0, 1, 4)
        if line is not None and min(a, b, c, d) == 0:
            p.px(x, y, line)
        elif min(c, d) < width + off and min(a, b) >= width + off:
            p.px(x, y, lo)
        elif min(a, b) < width + off:
            p.px(x, y, hi)
        elif hi2 is not None and min(a, b) == width + off:
            p.px(x, y, hi2)


def fill(p: Pix, s: Shape, c: Color) -> None:
    for x, y in s.cells():
        p.px(x, y, c)


def grain(p: Pix, s: Shape, ramp: Ramp, vertical: bool, seed_tones: Sequence[int] = (1, 2, 2, 3, 3), base: int = 2) -> None:
    """Wood grain: long runs along the board in a few tones, over a base tone. Cells outside the mask are left alone."""
    rng = p.rng
    x0, y0, x1, y1 = s.box()
    along = (y0, y1) if vertical else (x0, x1)
    across = (x0, x1) if vertical else (y0, y1)
    for x, y in s.cells():
        p.px(x, y, ramp[base])
    for i in range(across[0], across[1]):
        a = along[0] - rng.randrange(0, 20)
        while a < along[1]:
            n = rng.randrange(5, 28)
            t = rng.choice(seed_tones)
            if t != base and rng.random() < 0.55:
                for k in range(n):
                    xx, yy = (i, a + k) if vertical else (a + k, i)
                    if s.has(xx, yy):
                        p.px(xx, yy, ramp[t])
            a += n + rng.randrange(0, 8)


def knot(p: Pix, x: int, y: int, ramp: Ramp = WOOD) -> None:
    for dx, dy, c in ((0, 0, ramp[0]), (1, 0, ramp[1]), (-1, 0, ramp[1]), (0, 1, ramp[1]), (0, -1, ramp[3]), (2, 0, ramp[1]),
                      (-2, 0, ramp[2]), (0, 2, ramp[2])):
        p.px(x + dx, y + dy, c)


def rivet(p: Pix, x: int, y: int, ramp: Ramp = BRASS, shade: Color = (44, 26, 18)) -> None:
    """A domed rivet head, 2x2 with a cast shadow below right."""
    p.px(x, y, ramp[4])
    p.px(x + 1, y, ramp[3])
    p.px(x, y + 1, ramp[3])
    p.px(x + 1, y + 1, ramp[2])
    p.px(x + 2, y + 1, shade)
    p.px(x + 1, y + 2, shade)
    p.px(x + 2, y + 2, shade)


def bolt(p: Pix, cx: int, cy: int, ramp: Ramp = BRASS, shade: Color = (44, 26, 18)) -> None:
    """A round bolt head 5x5 with a screwdriver slot."""
    for dx, dy in ((-1, -2), (0, -2), (1, -2), (-2, -1), (-2, 0), (-2, 1), (2, -1), (2, 0), (2, 1), (-1, 2), (0, 2), (1, 2)):
        p.px(cx + dx, cy + dy, ramp[1] if dx + dy > 0 else ramp[3])
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            p.px(cx + dx, cy + dy, ramp[3] if dx + dy < 0 else ramp[2])
    p.px(cx - 1, cy - 1, ramp[4])
    p.line(cx - 1, cy + 1, cx + 1, cy - 1, ramp[0])
    for dx, dy in ((3, 0), (3, 1), (2, 2), (1, 3), (0, 3), (-1, 3)):
        p.px(cx + dx, cy + dy, shade)


def metal_plate(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = BRASS, rivets: bool = True, wear: int = 0) -> None:
    """A flat metal plate: dark line, lit edge, shaded edge, a streak of sheen, and a rivet in each corner."""
    s = Shape(p.w, p.h).rect(x, y, x + w - 1, y + h - 1)
    fill(p, s, ramp[2])
    p.hline(x + 1, y + 1, w - 2, ramp[4])
    p.vline(x + 1, y + 1, h - 2, ramp[3])
    p.hline(x + 1, y + h - 2, w - 2, ramp[1])
    p.vline(x + w - 2, y + 1, h - 2, ramp[1])
    p.frame(x, y, w, h, ramp[0])
    for k in range(wear):
        xx, yy = x + 3 + p.rng.randrange(max(1, w - 6)), y + 3 + p.rng.randrange(max(1, h - 6))
        p.px(xx, yy, ramp[1] if k % 2 else ramp[3])
    if rivets and w >= 10 and h >= 8:
        for xx, yy in ((x + 2, y + 2), (x + w - 5, y + 2), (x + 2, y + h - 5), (x + w - 5, y + h - 5)):
            rivet(p, xx, yy, ramp)


def stitch(p: Pix, x0: int, y0: int, x1: int, y1: int, c: Color, gap: int = 3) -> None:
    """Dashed stitching along a straight run."""
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(0, n + 1):
        if i % gap < gap - 1:
            p.px(x0 + (x1 - x0) * i // max(1, n), y0 + (y1 - y0) * i // max(1, n), c)


def cloth(p: Pix, x: int, y: int, w: int, h: int, base: Color, vertical_only: bool = False) -> None:
    """A woven wool swatch: base tone, a lit left edge, a shaded right edge and warp threads. Plain warp (vertical lines)
    when `vertical_only`, so a picture that is stretched downwards in the game still looks like cloth."""
    dark = mix(base, VIOLET, 0.28)
    dark2 = mix(base, VIOLET, 0.5)
    light = mix(base, (255, 224, 150), 0.22)
    light2 = mix(base, (255, 224, 150), 0.4)
    p.rect(x, y, w, h, base)
    for i in range(w):
        if i % 2 == 1:
            p.vline(x + i, y, h, mix(base, dark, 0.45))
    if not vertical_only:
        for j in range(h):
            for i in range(w):
                if (i + j) % 4 == 0:
                    p.px(x + i, y + j, mix(base, light, 0.6))
                elif (i + j) % 4 == 2 and (i % 2 == 0):
                    p.px(x + i, y + j, mix(base, dark, 0.25))
    for i in range(0, w):
        # a thread that sticks out a little brighter now and then keeps it from looking printed
        if p.rng.random() < 0.16:
            j = p.rng.randrange(h)
            p.px(x + i, y + j, light)
            if h > 6 and p.rng.random() < 0.5:
                p.px(x + i, y + min(h - 1, j + 1), light)
    p.vline(x, y, h, light2)
    if w > 4:
        p.vline(x + 1, y, h, light)
    p.vline(x + w - 1, y, h, dark2)
    if w > 4:
        p.vline(x + w - 2, y, h, dark)


def dye_edge(p: Pix, x: int, y: int, w: int, h: int, base: Color) -> None:
    """The top hem and bottom shadow of a swatch card."""
    p.hline(x, y, w, mix(base, (255, 224, 150), 0.3))
    p.hline(x, y + h - 1, w, mix(base, VIOLET, 0.55))


def ink_ramp(c: Color) -> tuple[Color, Color, Color]:
    """Ink, as three tones: body, a lit edge and a shaded edge (for lettering)."""
    return mix(c, VIOLET, 0.5), c, mix(c, (255, 224, 150), 0.25)


def vial(p: Pix, x: int, y: int, w: int, h: int, liquid: Ramp, level: float, cap: bool = True, ticks: bool = True) -> None:
    """A glass vial: lit left side, liquid up to `level` (0 to 1) with a bright meniscus, brass cap and cork on top, and
    graduation ticks. Liquid is a 4-tone ramp dark to light."""
    body = Shape(p.w, p.h).rrect(x, y + 3, x + w - 1, y + h - 1, 2 if w > 4 else 1)
    fill(p, body, GLASS[1])
    top = y + 3 + round((h - 3) * (1 - level))
    for xx, yy in body.cells():
        if yy >= top:
            p.px(xx, yy, liquid[1])
    for yy in range(top, y + h - 1):
        for xx in range(x + 1, x + w - 1):
            if body.has(xx, yy):
                p.px(xx, yy, liquid[2] if xx < x + w - 2 else liquid[1])
    if level > 0:
        for xx in range(x + 1, x + w - 1):
            p.px(xx, top, liquid[3])
    bevel(p, body, GLASS[4], GLASS[0], GLASS[0])
    p.vline(x + 1, y + 5, max(1, h - 9), GLASS[4])
    if ticks and w >= 7:
        for k in range(1, 5):
            yy = y + 3 + (h - 3) * k // 5
            p.hline(x + w - 4, yy, 2, GLASS[0])
    if cap:
        p.rect(x - 1, y + 2, w + 2, 3, BRASS[2])
        p.hline(x - 1, y + 2, w + 2, BRASS[4])
        p.hline(x - 1, y + 4, w + 2, BRASS[0])
        p.rect(x + 1, y, w - 2, 2, LEATHER[3])
        p.hline(x + 1, y, w - 2, LEATHER[3])
        p.px(x + 1, y, mix(LEATHER[3], (255, 224, 150), 0.3))


def wax_blob(p: Pix, cx: int, cy: int, r: int, ramp: Ramp, stamp: bool = True, seed: int = 0) -> None:
    """A round wax seal: ragged edge, lit upper left, a pressed ring and a cross in the middle."""
    s = Shape(p.w, p.h).ellipse(cx - r, cy - r, cx + r, cy + r)
    rng = p.rng
    for k in range(r * 3):
        ang = k / (r * 3) * 6.283
        if rng.random() < 0.45:
            from math import cos, sin
            s.rect(round(cx + cos(ang) * (r + 1)), round(cy + sin(ang) * (r + 1)), round(cx + cos(ang) * (r + 1)),
                   round(cy + sin(ang) * (r + 1)))
    fill(p, s, ramp[2])
    bevel(p, s, ramp[4], ramp[1], ramp[0])
    if stamp and r >= 6:
        ring = Shape(p.w, p.h).ellipse(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3)
        ring.ellipse(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5, on=False)
        for x, y in ring.cells():
            p.px(x, y, ramp[1] if x + y > 2 * cx - 1 + 2 * (cy - cx) else ramp[3])
        p.vline(cx, cy - 2, 5, ramp[1])
        p.hline(cx - 2, cy, 5, ramp[1])
        p.px(cx - 1, cy - 1, ramp[3])


def parchment_card(p: Pix, x: int, y: int, w: int, h: int, tone: int = 3) -> None:
    """A parchment card with a lit top-left, a shaded bottom-right and a few fibres."""
    p.rect(x, y, w, h, PARCHMENT[tone])
    p.hline(x, y, w, PARCHMENT[min(4, tone + 1)])
    p.vline(x, y, h, PARCHMENT[min(4, tone + 1)])
    p.hline(x, y + h - 1, w, PARCHMENT[tone - 2])
    p.vline(x + w - 1, y, h, PARCHMENT[tone - 2])
    for _ in range(w * h // 30):
        p.px(x + 1 + p.rng.randrange(max(1, w - 2)), y + 1 + p.rng.randrange(max(1, h - 2)), PARCHMENT[tone - 1])


def linen_stripe(p: Pix, x: int, y: int, w: int, h: int, tone: int = 3) -> None:
    p.rect(x, y, w, h, LINEN[tone])
    for i in range(0, w, 2):
        p.vline(x + i, y, h, LINEN[tone - 1])


def iron_band(p: Pix, x: int, y: int, w: int, h: int, vertical: bool = False) -> None:
    """A strap of black iron with a lit edge and rivets."""
    p.rect(x, y, w, h, IRON[2])
    if vertical:
        p.vline(x, y, h, IRON[4])
        p.vline(x + w - 1, y, h, IRON[0])
        for yy in range(y + 3, y + h - 2, 9):
            rivet(p, x + (w - 3) // 2, yy, BRASS)
    else:
        p.hline(x, y, w, IRON[4])
        p.hline(x, y + h - 1, w, IRON[0])
        for xx in range(x + 3, x + w - 2, 9):
            rivet(p, xx, y + (h - 3) // 2, BRASS)


__all__ = ["Shape", "bevel", "fill", "grain", "knot", "rivet", "bolt", "metal_plate", "stitch", "cloth", "dye_edge",
           "ink_ramp", "vial", "wax_blob", "parchment_card", "linen_stripe", "iron_band", "VIOLET", "OAK_LIT", "OAK",
           "SHADOW", "reach"]
