"""Helpers for the appraisal close-ups (first half): lit solids, bevelled plates, scratches, glyphs, clouds.

The close-ups are big and shown through a magnifier, so they need modelling, not flat fills. Every solid here is shaded
from a height field with one fixed light from the upper left, then quantised onto a colour ramp with a narrow ordered
dither at the joints, so the result stays whole pixels. Nothing here reads the game's art.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterable, Sequence
from typing import Final

from PIL import Image, ImageDraw

from pix import BAYER, Color, Pix, Ramp, mix
from palette import BRASS, IRON, PARCHMENT, SHADOW, SOOT

Point = tuple[int, int]
Mask = set[Point]
HeightFn = Callable[[int, int], float]

_L: Final = (-0.50, -0.62, 0.60)
_LN: Final = math.sqrt(sum(c * c for c in _L))
LIGHT: Final = tuple(c / _LN for c in _L)

# Steel is lighter than the shared IRON ramp: a polished plate needs a pale top end.
STEEL: Final[Ramp] = ((38, 36, 48), (64, 63, 78), (94, 94, 108), (128, 129, 141), (168, 168, 174), (212, 208, 198))
BLACKENED: Final[Ramp] = ((16, 14, 20), (30, 28, 38), (46, 44, 56), (66, 64, 76), (92, 90, 102), (124, 120, 128))
DARKWOOD: Final[Ramp] = ((22, 13, 12), (40, 24, 18), (62, 38, 26), (88, 56, 36), (116, 76, 48), (146, 100, 62))
GOLD: Final[Ramp] = ((58, 34, 22), (104, 64, 28), (160, 108, 40), (206, 156, 62), (238, 200, 108), (252, 236, 168))
RUST: Final[Ramp] = ((52, 24, 20), (92, 42, 26), (128, 66, 34), (160, 98, 52))
GRIME: Final[Ramp] = ((30, 26, 28), (48, 42, 40), (74, 66, 58), (100, 92, 78))


# ------------------------------------------------------------------ shading

def pick(ramp: Ramp, v: float, x: int, y: int, dither: bool = True) -> Color:
    """Tone for a light value 0..1: bands, with a narrow ordered dither where two bands meet."""
    f = max(0.0, min(1.0, v)) * (len(ramp) - 1)
    i = int(f)
    if i >= len(ramp) - 1:
        return ramp[-1]
    frac = f - i
    if dither:
        t = max(0.0, min(1.0, (frac - 0.30) / 0.40))
        return ramp[i + 1] if t * 16 > BAYER[y % 4][x % 4] else ramp[i]
    return ramp[i + (1 if frac > 0.5 else 0)]


def shade_value(nx: float, ny: float, nz: float, gain: float, bias: float) -> float:
    ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    d = (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / ln
    return (d + 0.45) / 1.4 * gain + bias


def solid(p: Pix, mask: Mask, hfn: HeightFn, ramp: Ramp, rim: Color | None = SHADOW, relief: float = 1.0,
          gain: float = 1.0, bias: float = 0.0, dither: bool = True, rim_ramp_lit: Color | None = None) -> None:
    """Paints a masked shape lit from the upper left. `hfn(x, y)` is its height (0 outside); `rim` outlines it outside.
    `rim_ramp_lit` colours the outline on the lit sides (top and left), so a rim reads as a catch of light."""
    heights = {pt: hfn(*pt) for pt in mask}
    for (x, y) in mask:
        hx = (heights.get((x + 1, y), 0.0) - heights.get((x - 1, y), 0.0)) * 0.5 * relief
        hy = (heights.get((x, y + 1), 0.0) - heights.get((x, y - 1), 0.0)) * 0.5 * relief
        p.px(x, y, pick(ramp, shade_value(-hx, -hy, 1.0, gain, bias), x, y, dither))
    if rim is not None:
        for (x, y) in outer_ring(mask):
            c = rim
            if rim_ramp_lit is not None and ((x + 1, y) in mask or (x, y + 1) in mask) and not ((x - 1, y) in mask or (x, y - 1) in mask):
                c = rim_ramp_lit
            p.px(x, y, c)


def outer_ring(mask: Mask) -> Mask:
    ring: Mask = set()
    for (x, y) in mask:
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + d[0], y + d[1])
            if q not in mask:
                ring.add(q)
    return ring


def distance_inside(mask: Mask) -> dict[Point, float]:
    """Distance of every masked pixel to the nearest pixel outside the mask (chamfer, two passes)."""
    if not mask:
        return {}
    x0, y0 = min(x for x, _ in mask) - 1, min(y for _, y in mask) - 1
    x1, y1 = max(x for x, _ in mask) + 1, max(y for _, y in mask) + 1
    inf = 1e9
    d = {(x, y): (inf if (x, y) in mask else 0.0) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    r2 = 1.4142
    for y in range(y0 + 1, y1 + 1):
        for x in range(x0 + 1, x1):
            if d[(x, y)]:
                d[(x, y)] = min(d[(x, y)], d[(x - 1, y)] + 1, d[(x, y - 1)] + 1, d[(x - 1, y - 1)] + r2, d[(x + 1, y - 1)] + r2)
    for y in range(y1 - 1, y0, -1):
        for x in range(x1 - 1, x0, -1):
            if d[(x, y)]:
                d[(x, y)] = min(d[(x, y)], d[(x + 1, y)] + 1, d[(x, y + 1)] + 1, d[(x + 1, y + 1)] + r2, d[(x - 1, y + 1)] + r2)
    return {pt: v for pt, v in d.items() if pt in mask}


def poly_mask(points: Sequence[Point]) -> Mask:
    xs, ys = [q[0] for q in points], [q[1] for q in points]
    x0, y0 = min(xs), min(ys)
    im = Image.new("L", (max(xs) - x0 + 1, max(ys) - y0 + 1), 0)
    ImageDraw.Draw(im).polygon([(x - x0, y - y0) for x, y in points], fill=255)
    return {(x + x0, y + y0) for x in range(im.width) for y in range(im.height) if im.getpixel((x, y))}


def rect_mask(x: int, y: int, w: int, h: int, corner: int = 0) -> Mask:
    """A rectangle; `corner` clips each corner by a diagonal of that many pixels."""
    out: Mask = set()
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            dx = min(xx - x, x + w - 1 - xx)
            dy = min(yy - y, y + h - 1 - yy)
            if dx + dy >= corner - 1 or dx >= corner or dy >= corner:
                out.add((xx, yy))
    return out


def ellipse_mask(cx: float, cy: float, rx: float, ry: float) -> Mask:
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0}


def dome(cx: float, cy: float, rx: float, ry: float, z: float) -> HeightFn:
    """Height of an ellipsoid: a ball for fruit, a pillow for a loaf."""
    def h(x: int, y: int) -> float:
        t = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
        return math.sqrt(t) * z if t > 0 else 0.0
    return h


def capsule_mask(a: tuple[float, float], b: tuple[float, float], r0: float, r1: float) -> tuple[Mask, HeightFn]:
    """A tube from a to b whose radius runs from r0 to r1, with round ends; and its height field."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    ll = vx * vx + vy * vy or 1.0

    def near(x: float, y: float) -> tuple[float, float]:
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / ll))
        r = r0 + (r1 - r0) * t
        return math.hypot(x - (ax + vx * t), y - (ay + vy * t)), r

    rmax = max(r0, r1)
    mask: Mask = set()
    for y in range(int(min(ay, by) - rmax) - 1, int(max(ay, by) + rmax) + 2):
        for x in range(int(min(ax, bx) - rmax) - 1, int(max(ax, bx) + rmax) + 2):
            d, r = near(x, y)
            if d <= r:
                mask.add((x, y))

    def h(x: int, y: int) -> float:
        d, r = near(x, y)
        t = 1.0 - (d / r) ** 2
        return math.sqrt(t) * r if t > 0 else 0.0
    return mask, h


def capsule(p: Pix, a: tuple[float, float], b: tuple[float, float], r0: float, r1: float, ramp: Ramp,
            rim: Color | None = SHADOW, **kw: float) -> Mask:
    mask, h = capsule_mask(a, b, r0, r1)
    solid(p, mask, h, ramp, rim, **kw)  # type: ignore[arg-type]
    return mask


def plate(p: Pix, points: Sequence[Point], ramp: Ramp, rim: Color | None = SHADOW, bevel: float = 3.0,
          bulge: HeightFn | None = None, relief: float = 1.0, **kw: float) -> Mask:
    """A flat plate with bevelled edges (light on the top and left, shade on the bottom and right) and an optional bulge."""
    mask = poly_mask(points)
    dist = distance_inside(mask)

    def h(x: int, y: int) -> float:
        d = dist.get((x, y), 0.0)
        base = min(d, bevel) * 0.9
        return base + (bulge(x, y) if bulge else 0.0)
    solid(p, mask, h, ramp, rim, relief=relief, **kw)  # type: ignore[arg-type]
    return mask


def plate_rect(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, rim: Color | None = SHADOW, bevel: float = 2.0,
               corner: int = 0, **kw: float) -> Mask:
    mask = rect_mask(x, y, w, h, corner)
    dist = distance_inside(mask)
    solid(p, mask, lambda xx, yy: min(dist.get((xx, yy), 0.0), bevel) * 0.9, ramp, rim, **kw)  # type: ignore[arg-type]
    return mask


# ------------------------------------------------------------------ surface wear

def scratches(p: Pix, mask: Mask, rng: random.Random, count: int, dark: Color, light: Color | None = None,
              length: tuple[int, int] = (3, 9), slope: tuple[int, int] = (2, -3)) -> None:
    """Short scuffs in one direction, only where `mask` is: the diagnostic marks of a worn piece."""
    pts = sorted(mask)
    for _ in range(count):
        x, y = rng.choice(pts)
        n = rng.randint(*length)
        sx, sy = slope
        for i in range(n):
            q = (x + (i * sx) // 3, y + (i * sy) // 3)
            if q in mask:
                p.px(q[0], q[1], dark)
                if (q[0] + 1, q[1]) in mask and rng.random() < 0.6:
                    p.px(q[0] + 1, q[1], dark)
                if light is not None and rng.random() < 0.5 and (q[0] + 1, q[1]) in mask:
                    p.px(q[0] + 1, q[1], light)


def stain(p: Pix, mask: Mask, rng: random.Random, cx: int, cy: int, r: int, colors: Sequence[Color], density: float = 0.5) -> None:
    """A ragged smudge (rust, soot, mould) inside `mask`; the centre is denser."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x, y) in mask:
                d = math.hypot(x - cx, y - cy) / r
                if d <= 1.0 and rng.random() < density * (1.05 - d):
                    p.px(x, y, colors[min(len(colors) - 1, int(d * len(colors) + rng.random() * 0.8))])


def streaks(p: Pix, mask: Mask, rng: random.Random, count: int, colors: Sequence[Color], vertical: bool = True,
            length: tuple[int, int] = (6, 24)) -> None:
    """Long lines of grain or brushing along an axis, over a masked shape."""
    pts = sorted(mask)
    for _ in range(count):
        x, y = rng.choice(pts)
        c = rng.choice(list(colors))
        for i in range(rng.randint(*length)):
            q = (x, y + i) if vertical else (x + i, y)
            if q in mask:
                p.px(q[0], q[1], c)


def mask_rows(mask: Mask) -> Iterable[int]:
    return sorted({y for _, y in mask})


# ------------------------------------------------------------------ small glyphs

def stamp(p: Pix, rows: Sequence[str], x: int, y: int, colors: dict[str, Color]) -> None:
    """Paints a picture given as text rows; '.' and ' ' are left alone."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                p.px(x + i, y + j, colors[ch])


def gear(p: Pix, cx: int, cy: int, r: int, teeth: int, ramp: Ramp, hole: Color = SOOT[0], phase: float = 0.0) -> None:
    """A toothed brass wheel seen face on: a toothed rim, three spokes, a hub. Lit from the upper left."""
    mask: Mask = set()
    inner = r * 0.58
    for y in range(cy - r - 2, cy + r + 3):
        for x in range(cx - r - 2, cx + r + 3):
            d = math.hypot(x - cx, y - cy)
            a = math.atan2(y - cy, x - cx)
            rr = r - 0.4 + (1.6 if math.cos(a * teeth + phase) > 0.0 else 0.0)
            if d > rr:
                continue
            spoke = any(abs(math.sin(a - phase - k * 2.0944)) * d < 1.3 and math.cos(a - phase - k * 2.0944) > 0 for k in range(3))
            if d >= inner or spoke or d < 2.2:
                mask.add((x, y))
    solid(p, mask, dome(cx, cy, r + 2, r + 2, r * 0.45), ramp, SHADOW, relief=1.0, dither=False)
    p.px(cx, cy, hole)


# ------------------------------------------------------------------ noise

def value_noise(seed: int, scale_x: float, scale_y: float) -> Callable[[float, float], float]:
    """Smooth 2D value noise in 0..1 (deterministic from the seed), for cloud banks and mottling."""
    def lattice(ix: int, iy: int) -> float:
        return random.Random((ix * 73856093) ^ (iy * 19349663) ^ (seed * 83492791)).random()

    def f(x: float, y: float) -> float:
        gx, gy = x / scale_x, y / scale_y
        ix, iy = math.floor(gx), math.floor(gy)
        fx, fy = gx - ix, gy - iy
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a, b = lattice(ix, iy), lattice(ix + 1, iy)
        c, d = lattice(ix, iy + 1), lattice(ix + 1, iy + 1)
        return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy
    return f


def fbm(seed: int, scale_x: float, scale_y: float, octaves: int = 3) -> Callable[[float, float], float]:
    layers = [value_noise(seed + i * 17, scale_x / (2 ** i), scale_y / (2 ** i)) for i in range(octaves)]
    weights = [0.5 ** i for i in range(octaves)]
    total = sum(weights)

    def f(x: float, y: float) -> float:
        return sum(w * n(x, y) for w, n in zip(weights, layers)) / total
    return f


# ------------------------------------------------------------------ writing

def squiggle_line(p: Pix, x: int, y: int, w: int, ink: Color, rng: random.Random, size: int = 3) -> None:
    """A line of hand-lettered fake script: little loops and strokes of random width, with word gaps."""
    cx = x
    while cx < x + w - 2:
        word = rng.randint(2, 6)
        for _ in range(word):
            gw = rng.randint(2, 3)
            kind = rng.randrange(5)
            top = y
            if kind == 0:
                p.vline(cx, top, size, ink)
            elif kind == 1:
                p.vline(cx, top, size, ink)
                p.px(cx + 1, top, ink)
            elif kind == 2:
                p.px(cx, top + size - 1, ink)
                p.px(cx + 1, top + 1, ink)
                p.vline(cx + 2, top + 1, size - 1, ink)
            elif kind == 3:
                p.vline(cx, top + 1, size - 1, ink)
                p.px(cx + 1, top + size - 1, ink)
                p.px(cx + 1, top, ink)
            else:
                p.vline(cx, top, size, ink)
                p.vline(cx + 2, top, size, ink)
                p.px(cx + 1, top + size // 2, ink)
            cx += gw + 1
        cx += 3


def blend(a: Color, b: Color, t: float) -> Color:
    return mix(a, b, t)


__all__ = [n for n in dir() if not n.startswith("_")] + ["BRASS", "IRON", "PARCHMENT"]
