"""Helpers for the gear, medicine and weapon sprites: masks, pillow-shaded volumes, rim light, stitching and rivets.

A sprite is built from masks (sets of pixels). `puff` shades a mask like a rounded cushion lit from the upper left, so any
polygon gets a lit edge, a core and a shaded edge in 3 to 5 tones of one ramp; `finish` adds the rim light and the dark
outline last, and small details (rivets, stitches, labels) are drawn on top.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Sequence

from PIL import Image, ImageDraw

from palette import (BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, STONE,
                     WINE, WOOD)
from pix import BAYER, Color, Pix, Ramp, mix, rgb

Mask = set[tuple[int, int]]
Point = tuple[int, int]

# Extra ramps (dark to light) for the things the shared palette lacks.
BONE: Ramp = (rgb("#5b4a3c"), rgb("#8d7861"), rgb("#bba88a"), rgb("#dccdae"), rgb("#efe3c6"))
PLUM: Ramp = (rgb("#2a1530"), rgb("#4a2650"), rgb("#6e3d72"), rgb("#935a92"))
ROSE: Ramp = (rgb("#4a2024"), rgb("#7e3a3d"), rgb("#b2605a"), rgb("#d58f7c"))
SEA: Ramp = (rgb("#10282a"), rgb("#1f4a4c"), rgb("#337672"), rgb("#52a09a"))
AMBER: Ramp = (rgb("#3a1c0c"), rgb("#7a3c14"), rgb("#b8701f"), rgb("#e0a23a"), rgb("#f6d070"))
SKY: Ramp = (rgb("#10203a"), rgb("#1f3f6a"), rgb("#2f66a0"), rgb("#5a95c8"))
OCHRE: Ramp = (rgb("#4a2c10"), rgb("#7e5018"), rgb("#b47c26"), rgb("#dca848"))
STEEL: Ramp = (rgb("#25242d"), rgb("#4a4955"), rgb("#7a7d8a"), rgb("#a9adb8"), rgb("#d6d9de"))
FLESH: Ramp = (rgb("#4a1a22"), rgb("#7c2b33"), rgb("#a84246"), rgb("#cf6a62"), rgb("#e8998a"))
LIVER: Ramp = (rgb("#2e1218"), rgb("#4e1f26"), rgb("#74333a"), rgb("#98504c"))
LUNG: Ramp = (rgb("#4a2128"), rgb("#7c3a42"), rgb("#aa5c5c"), rgb("#d08a82"))
KIDNEY: Ramp = (rgb("#3a1620"), rgb("#62263a"), rgb("#8c3f52"), rgb("#b2646c"))


# ---------------------------------------------------------------------------------------------------- masks

def _bounds(pts: Iterable[Point]) -> tuple[int, int, int, int]:
    xs, ys = zip(*pts)
    return min(xs), min(ys), max(xs), max(ys)


def _raster(x0: int, y0: int, x1: int, y1: int, paint) -> Mask:
    img = Image.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
    paint(ImageDraw.Draw(img), -x0, -y0)
    data = img.load()
    return {(x0 + x, y0 + y) for y in range(img.height) for x in range(img.width) if data[x, y]}


def rect_m(x: int, y: int, w: int, h: int) -> Mask:
    return {(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)}


def rrect_m(x: int, y: int, w: int, h: int, r: int = 1) -> Mask:
    """A rectangle with each corner cut diagonally (r pixels deep)."""
    m = rect_m(x, y, w, h)
    for i in range(r):
        for k in range(r - i):
            for cx, cy, sx, sy in ((x, y, 1, 1), (x + w - 1, y, -1, 1), (x, y + h - 1, 1, -1), (x + w - 1, y + h - 1, -1, -1)):
                m.discard((cx + sx * k, cy + sy * i))
    return m


def ell_m(x: int, y: int, w: int, h: int) -> Mask:
    return _raster(x, y, x + w - 1, y + h - 1, lambda d, ox, oy: d.ellipse((x + ox, y + oy, x + w - 1 + ox, y + h - 1 + oy), fill=255))


def poly_m(pts: Sequence[Point]) -> Mask:
    x0, y0, x1, y1 = _bounds(pts)
    return _raster(x0, y0, x1, y1, lambda d, ox, oy: d.polygon([(a + ox, b + oy) for a, b in pts], fill=255))


def line_m(pts: Sequence[Point], width: int = 1) -> Mask:
    x0, y0, x1, y1 = _bounds(pts)
    return _raster(x0 - 1, y0 - 1, x1 + 1, y1 + 1,
                   lambda d, ox, oy: d.line([(a + ox, b + oy) for a, b in pts], fill=255, width=width))


def flip_m(m: Mask, axis_x: int) -> Mask:
    """Mirror a mask about the vertical line x = axis_x / 2 (so x -> axis_x - x)."""
    return {(axis_x - x, y) for x, y in m}


def move_m(m: Mask, dx: int, dy: int) -> Mask:
    return {(x + dx, y + dy) for x, y in m}


# ---------------------------------------------------------------------------------------------------- shading

LIGHT = (-0.55, -0.65, 0.55)


def puff(p: Pix, m: Mask, ramp: Ramp | Callable[[int, int], Ramp], r: int = 3, bias: float = 0.0, flat: float = 0.0) -> None:
    """Paints a mask as a rounded cushion lit from the upper left. `r` is how far the roundness reaches in from the edge
    (more is rounder), `bias` pushes the tones lighter (+) or darker (-). Ordered dither joins the tone bands."""
    if not m:
        return
    dist: dict[Point, int] = {}
    q: deque[Point] = deque()
    for (x, y) in m:
        if any((x + dx, y + dy) not in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            dist[(x, y)] = 1
            q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in m and n not in dist:
                dist[n] = dist[(x, y)] + 1
                q.append(n)

    def h(x: int, y: int) -> float:
        return min(dist.get((x, y), 0), r) / r

    lx, ly, lz = LIGHT
    for (x, y) in m:
        gx = h(x + 1, y) - h(x - 1, y)
        gy = h(x, y + 1) - h(x, y - 1)
        nx, ny, nz = -gx * (1 - flat) * 1.6, -gy * (1 - flat) * 1.6, 1.0
        norm = (nx * nx + ny * ny + nz * nz) ** 0.5
        v = (nx * lx + ny * ly + nz * lz) / norm        # about 0 (dark) .. 0.9 (lit)
        t = max(0.0, min(1.0, (v + 0.12) / 0.95 + bias))
        rp = ramp(x, y) if callable(ramp) else ramp
        n = len(rp)
        pos = t * (n - 1)
        lo = int(pos)
        frac = pos - lo
        k = lo + (1 if lo < n - 1 and (frac > 0.62 or (frac > 0.38 and BAYER[y % 4][x % 4] < 8)) else 0)
        p.px(x, y, rp[min(n - 1, k)])


def paint(p: Pix, m: Mask, c: Color) -> None:
    for x, y in m:
        p.px(x, y, c)


def bands_v(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp) -> None:
    """A vertical cylinder (a tube standing up): light on the left, shaded on the right."""
    n = len(ramp)
    for i in range(w):
        t = i / max(1, w - 1)
        if w >= 5 and i == 0:
            k = n - 2
        else:
            k = max(0, min(n - 1, n - 1 - round(max(0.0, t - 0.15) / 0.85 * (n - 1))))
        p.vline(x + i, y, h, ramp[k])


def bands_h(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp) -> None:
    """A horizontal cylinder (a tube lying down): light on top, shaded below."""
    n = len(ramp)
    for j in range(h):
        t = j / max(1, h - 1)
        if h >= 5 and j == 0:
            k = n - 2
        else:
            k = max(0, min(n - 1, n - 1 - round(max(0.0, t - 0.15) / 0.85 * (n - 1))))
        p.hline(x, y + j, w, ramp[k])


def rim_light(p: Pix, lit: float = 0.22, dark: float = 0.30) -> None:
    """Lightens pixels on the upper-left silhouette edge and darkens those on the lower-right edge."""
    src = p.im.copy()
    px = src.load()

    def solid(x: int, y: int) -> bool:
        return 0 <= x < p.w and 0 <= y < p.h and px[x, y][3] > 8

    for y in range(p.h):
        for x in range(p.w):
            if px[x, y][3] <= 8:
                continue
            c = px[x, y][:3]
            if not solid(x - 1, y) or not solid(x, y - 1):
                p.px(x, y, mix(c, (255, 226, 170), lit))
            elif not solid(x + 1, y) or not solid(x, y + 1):
                p.px(x, y, mix(c, SHADOW, dark))


def finish(p: Pix, rim: bool = True) -> Image.Image:
    if rim:
        rim_light(p)
    p.outline(SHADOW)
    return p.im


def outline_only(p: Pix) -> Image.Image:
    p.outline(SHADOW)
    return p.im


# ---------------------------------------------------------------------------------------------------- details

def stud(p: Pix, x: int, y: int) -> None:
    """A brass rivet head: bright pixel with a dark one beside it."""
    p.px(x, y, BRASS[4])
    p.px(x + 1, y + 1, BRASS[0])
    p.px(x + 1, y, BRASS[2])
    p.px(x, y + 1, BRASS[2])


def dots(p: Pix, pts: Iterable[Point], c: Color) -> None:
    for x, y in pts:
        p.px(x, y, c)


def stitches(p: Pix, x0: int, y0: int, x1: int, y1: int, c: Color, gap: int = 2) -> None:
    """A dashed seam between two points."""
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(0, n + 1, gap):
        t = i / max(1, n)
        p.px(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)


def label(p: Pix, x: int, y: int, w: int, h: int, ink: Color = PARCHMENT[0], band: Color | None = None) -> None:
    """A parchment label with a line or two of scribble (and an optional coloured band)."""
    p.rect(x, y, w, h, PARCHMENT[3])
    p.hline(x, y, w, PARCHMENT[4])
    p.hline(x, y + h - 1, w, PARCHMENT[2])
    if band is not None and h >= 4:
        p.hline(x + 1, y + 1, w - 2, band)
        for i in range(2, h - 1, 2):
            p.hline(x + 1, y + i, max(1, w - 2 - (i // 2) % 2), ink)
    else:
        for i in range(1, h - 1, 2):
            p.hline(x + 1, y + i, max(1, w - 3 + (i // 2) % 2), ink)


def seal(p: Pix, cx: int, cy: int, ramp: Ramp = WINE) -> None:
    """A wax seal: a blob with a lit edge and a stamped dent."""
    m = ell_m(cx - 1, cy - 1, 4, 4)
    puff(p, m, ramp, r=2)
    p.px(cx + 1, cy + 1, ramp[0])


def glass_sheen(p: Pix, x: int, y: int, h: int) -> None:
    """A bright vertical streak on glass."""
    p.vline(x, y, h, GLASS[4])
    if h > 3:
        p.px(x, y + h, GLASS[3])


__all__ = [n for n in dir() if not n.startswith("_")]
