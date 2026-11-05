"""fxkit: the shared material kit of the tavern, so every fixture can be dressed to the standard of the cask.

Each material is a pure function that paints into a region of a `Pix`. A region is given as a *shape*:
  - a polygon (list of (x, y)),
  - a rectangle `(x, y, w, h)` of four numbers,
  - a Pillow image (an "L" mask, or an RGBA picture whose alpha is the shape) of the canvas's size,
  - a `Region` (built once with `region()` and reused), or None for the whole canvas.
The materials draw only whole pixels, shade with ramps and ordered dither, take their randomness from the canvas's
seeded rng (so a picture is the same every time) and scale their feature sizes with the region, so the same call works
on a 24 px handle and on a 300 px counter. Light comes from the upper left.

Index of the kit (all coordinates are canvas pixels):
  regions   region, ellipse, Region, as_polygon
  wood      wood_fill, belly (a bellied surface), wood_box (a Cuboid of propsy_fx or anything with its face methods)
  paper     paper_fill
  rope      rope, hang_curve, coil, chain, sample_path
  metal     iron_fill, iron_band, brass_fill, rivet
  glass     glass_pane
  cloth     cloth_fill
  shadows   contact_shadow, wall_shadow, cast_shadow
  wear      wear
  helpers   noise, vnoise, pick_tone, over
"""

from __future__ import annotations

import math
import random
from bisect import bisect_right
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Final, Protocol

from PIL import Image, ImageChops, ImageDraw

from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, OAK, PALE_WOOD, PARCHMENT, PLASTER, SHADOW, SOOT, WINE, WOOD
from pix import BAYER, Color, Pix, Ramp, mix, rgb

# ---------------------------------------------------------------------------------------------- extra ramps

ROPE: Final[Ramp] = (rgb("#2e2114"), rgb("#58421f"), rgb("#8a6a38"), rgb("#b4915a"), rgb("#d6b97e"))   # hemp, dark to light
RUST: Final[Ramp] = (rgb("#3a1c12"), rgb("#6a321b"), rgb("#8c4a22"), rgb("#b0662d"))                   # iron oxide
VERDIGRIS: Final[Ramp] = (rgb("#1f3a33"), rgb("#2f5c4c"), rgb("#4a8068"))                              # tarnished brass
TAPE: Final[Ramp] = (rgb("#8f7a4a"), rgb("#b39c62"), rgb("#d2bd82"), rgb("#e6d6a2"))                  # old paper tape
FOXING: Final[Color] = rgb("#8a5026")
INK: Final[Ramp] = (rgb("#1a1214"), rgb("#2c2024"), rgb("#4a3a36"))
LIGHT: Final[tuple[float, float, float]] = (-0.55, -0.6, 0.58)       # the direction to the light: upper left, toward us

Shape = Any   # polygon | (x, y, w, h) | Image | Region | None

# ---------------------------------------------------------------------------------------------- noise


def _lattice(seed: int) -> list[float]:
    r = random.Random(seed * 7919 + 13)
    return [r.random() for _ in range(4096)]


_TAB: Final = _lattice(1)


def noise(x: int, y: int, s: int = 0) -> float:
    """A repeatable 0..1 value for an integer pixel; independent of drawing order."""
    return _TAB[((x * 0x9E37) ^ (y * 0x85EB) ^ (s * 0xC2B3) ^ ((x * y) >> 3)) & 4095]


def vnoise(x: float, y: float, s: int = 0) -> float:
    """Smooth value noise, 0..1. Feature size is 1 unit: divide the coordinates to make bigger blobs, and divide one
    axis more than the other for streaks (the basis of grain)."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    h = s * 0xC2B3
    t = _TAB
    a = t[((ix * 0x9E37) ^ (iy * 0x85EB) ^ h) & 4095]
    b = t[(((ix + 1) * 0x9E37) ^ (iy * 0x85EB) ^ h) & 4095]
    c = t[((ix * 0x9E37) ^ ((iy + 1) * 0x85EB) ^ h) & 4095]
    d = t[(((ix + 1) * 0x9E37) ^ ((iy + 1) * 0x85EB) ^ h) & 4095]
    top = a + (b - a) * fx
    return top + (c + (d - c) * fx - top) * fy


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else hi if v > hi else v


def pick_tone(ramp: Ramp, v: float, x: int, y: int, crisp: float = 2.4) -> Color:
    """A tone of `ramp` for a fractional index `v`: flat inside a tone, ordered dither only near the joint between two
    tones (`crisp` makes the joint narrower), so shading reads as hand-placed pixel art and not as a smooth blend."""
    top = len(ramp) - 1
    if v <= 0:
        return ramp[0]
    if v >= top:
        return ramp[top]
    i = int(v)
    f = clamp((v - i - 0.5) * crisp + 0.5)
    return ramp[i + 1] if f > (BAYER[y & 3][x & 3] + 0.5) / 16 else ramp[i]


def over(p: Pix, x: int, y: int, c: Color, alpha: int = 255) -> None:
    """Lays colour `c` of opacity `alpha` (0..255) over a pixel, alpha-correct: on a transparent pixel it leaves a
    translucent pixel, on an opaque one it blends."""
    alpha = round(alpha)
    if alpha <= 0 or not (0 <= x < p.w and 0 <= y < p.h):
        return
    if alpha >= 255:
        p.im.putpixel((x, y), (c[0], c[1], c[2], 255))
        return
    r, g, b, ea = p.im.getpixel((x, y))  # type: ignore[misc]
    if ea == 0:
        p.im.putpixel((x, y), (c[0], c[1], c[2], alpha))
        return
    fa, ef = alpha / 255, ea / 255
    oa = fa + ef * (1 - fa)
    k = ef * (1 - fa)
    p.im.putpixel((x, y), (round((c[0] * fa + r * k) / oa), round((c[1] * fa + g * k) / oa),
                           round((c[2] * fa + b * k) / oa), round(oa * 255)))


def _tint(p: Pix, x: int, y: int, c: Color, t: float) -> None:
    """Pulls an *opaque-or-not existing* pixel toward `c` by `t`, keeping its alpha; transparent pixels are untouched."""
    if 0 <= x < p.w and 0 <= y < p.h:
        r, g, b, a = p.im.getpixel((x, y))  # type: ignore[misc]
        if a:
            p.im.putpixel((x, y), (*mix((r, g, b), c[:3], t), a))


# ---------------------------------------------------------------------------------------------- regions


class Region:
    """The pixels a material will paint: a mask, its bounding box, and edge queries (how far to the shape's edge)."""

    def __init__(self, mask: Image.Image) -> None:
        self.mask = mask
        self.w, self.h = mask.size
        self.bbox: tuple[int, int, int, int] = mask.getbbox() or (0, 0, 0, 0)    # x0, y0, x1, y1 (exclusive)
        self._a = mask.load()

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def empty(self) -> bool:
        return self.width <= 0

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self._a[x, y] > 0  # type: ignore[index]

    def pixels(self) -> Iterator[tuple[int, int]]:
        x0, y0, x1, y1 = self.bbox
        a = self._a
        for y in range(y0, y1):
            for x in range(x0, x1):
                if a[x, y]:  # type: ignore[index]
                    yield x, y

    def edge(self, x: int, y: int, cap: int = 3) -> tuple[int, int, int, int]:
        """Distances to the shape's edge going up, left, down, right: 1 means the next pixel that way is outside; the
        value stops at cap + 1."""
        out = []
        for dx, dy in ((0, -1), (-1, 0), (0, 1), (1, 0)):
            d = 1
            while d <= cap and self.inside(x + dx * d, y + dy * d):
                d += 1
            out.append(d)
        return out[0], out[1], out[2], out[3]

    def corners(self) -> dict[str, tuple[int, int]]:
        x0, y0, x1, y1 = self.bbox
        return {"tl": (x0, y0), "tr": (x1 - 1, y0), "bl": (x0, y1 - 1), "br": (x1 - 1, y1 - 1)}


def ellipse(cx: float, cy: float, rx: float, ry: float, n: int = 64) -> list[tuple[int, int]]:
    """A polygon for an ellipse (to use as a shape: a footprint, a plate, a pool of damp)."""
    return [(round(cx + rx * math.cos(2 * math.pi * i / n)), round(cy + ry * math.sin(2 * math.pi * i / n))) for i in range(n)]


def region(p: Pix, shape: Shape = None) -> Region:
    """Turns a shape (polygon, rectangle (x, y, w, h), mask image, RGBA picture or Region) into a `Region` of `p`."""
    if isinstance(shape, Region):
        return shape
    size = (p.w, p.h)
    if shape is None:
        return Region(Image.new("L", size, 255))
    if isinstance(shape, Image.Image):
        m = shape.getchannel("A") if shape.mode == "RGBA" else shape.convert("L")
        if m.size != size:
            canvas = Image.new("L", size, 0)
            canvas.paste(m, (0, 0))
            m = canvas
        return Region(m.point(lambda v: 255 if v > 127 else 0))
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    if len(shape) == 4 and not isinstance(shape[0], (tuple, list)):
        x, y, w, h = shape
        d.rectangle((round(x), round(y), round(x) + round(w) - 1, round(y) + round(h) - 1), fill=255)
    else:
        d.polygon([(round(a), round(b)) for a, b in shape], fill=255)
    return Region(m)


def as_polygon(r: Region) -> list[tuple[int, int]]:
    """The bounding rectangle of a region as a polygon (handy for placing a shadow or a stain)."""
    x0, y0, x1, y1 = r.bbox
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _rng(p: Pix, seed: int) -> random.Random:
    """A private random source drawn from the canvas's (so the order of drawing keeps results repeatable)."""
    return random.Random(p.rng.getrandbits(32) ^ (seed * 2654435761 & 0xFFFFFFFF))


def _smooth_light(r: Region, x: int, y: int) -> float:
    """-0.5 .. 0.5: brighter toward the upper left of the region, darker toward the lower right."""
    x0, y0, x1, y1 = r.bbox
    return 0.5 - ((x - x0) / max(1, x1 - x0) * 0.5 + (y - y0) / max(1, y1 - y0) * 0.5)


# ---------------------------------------------------------------------------------------------- wear


def wear(p: Pix, shape: Shape = None, amount: float = 0.5, kinds: Sequence[str] = ("scratch", "dent", "chip", "dust", "soot"),
         seed: int = 0) -> None:
    """Age on what is already painted: darkens, lightens and nicks existing pixels of the shape (transparent ones are
    left alone). `amount` 0..1 scales every kind.
      scratch  short pale or dark hairlines, mostly level, a pale one often paired with a dark one beside it
      dent     small dark pits with a lit lower-right lip
      chip     light flecks on the shape's own edge, where use rubs the finish away
      dust     pale grains on upward-facing edges and on top
      soot     dark dithered tone gathering in the upper part and the crevices at the edge"""
    r = region(p, shape)
    if r.empty or amount <= 0:
        return
    rng = _rng(p, seed + 5)
    x0, y0, x1, y1 = r.bbox
    area = r.width * r.height
    if "scratch" in kinds:
        for _ in range(round(area * amount / 520 + rng.random())):
            sx, sy = rng.randrange(x0, x1), rng.randrange(y0, y1)
            n = rng.randrange(3, max(5, min(16, r.width // 3 + 4)))
            slope = rng.uniform(-0.3, 0.3)
            dark = rng.random() < 0.45
            for i in range(n):
                x, y = sx + i, sy + round(i * slope)
                if r.inside(x, y):
                    _tint(p, x, y, SHADOW if dark else (232, 205, 150), 0.42 if dark else 0.34)
                    if not dark and i % 2 == 0 and r.inside(x, y + 1):
                        _tint(p, x, y + 1, SHADOW, 0.25)
    if "dent" in kinds:
        for _ in range(round(area * amount / 650 + rng.random())):
            x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
            if r.inside(x, y) and r.inside(x + 1, y + 1):
                _tint(p, x, y, SHADOW, 0.5)
                _tint(p, x + 1, y + 1, (236, 208, 150), 0.32)
    for x, y in r.pixels():
        up, left, down, right = r.edge(x, y, 2)
        n = noise(x, y, 77)
        if "chip" in kinds and min(up, left, down, right) == 1 and n < 0.16 * amount:
            _tint(p, x, y, (226, 196, 140) if (up == 1 or left == 1) else SHADOW, 0.4)
        if "dust" in kinds and up <= 2 and n < 0.3 * amount and BAYER[y & 3][x & 3] < 8:
            _tint(p, x, y, PLASTER[4], 0.32 if up == 1 else 0.18)
        if "soot" in kinds:
            top = 1 - (y - y0) / max(1, y1 - y0)
            lvl = amount * (0.34 * top ** 2.2 + (0.2 if min(up, left, right) == 1 else 0.0))
            if BAYER[y & 3][x & 3] < round(clamp(lvl) * 16):
                _tint(p, x, y, SOOT[0], 0.5)


# ---------------------------------------------------------------------------------------------- wood


@dataclass(frozen=True)
class Belly:
    """A bellied surface (cask, barrel, jug): its outline, a `curve` that unrolls it for `wood_fill`, and a `light`
    that shades it as a cylinder. Built by `belly()`."""
    outline: list[tuple[int, int]]
    curve: Callable[[int, int], tuple[float, float]]
    light: Callable[[int, int], float]
    staves: int


def belly(cx: float, top: float, height: float, half: float, bulge: float = 0.1, staves: int = 13, turn: float = 0.0) -> Belly:
    """A barrel-shaped surface centred on x `cx`, from y `top` for `height`, `half` wide at the belly (`bulge` is how
    much wider the middle is than the ends, as a share). Use it as `wood_fill(p, b.outline, "v", curve=b.curve,
    light_fn=b.light, board=<stave width>)`; the staves then have equal angle (narrow at the sides) and their joints curve
    with the belly. `turn` rotates the cask (-1..1) to bring a different part to the front."""
    def hw(y: float) -> float:
        t = clamp((y - top) / height)
        return half / (1 + bulge) * (1 + bulge * (1 - (2 * t - 1) ** 2))

    stave_w = math.pi * half / (1 + bulge) / staves * 0.0 + (half * math.pi / staves)

    def curve(x: int, y: int) -> tuple[float, float]:
        w = hw(y)
        th = math.asin(clamp((x - cx) / max(1.0, w), -1, 1))
        return y - top, (th + math.pi / 2 + turn) / math.pi * staves * stave_w

    def light(x: int, y: int) -> float:
        w = hw(y)
        th = math.asin(clamp((x - cx) / max(1.0, w), -1, 1))
        return 0.55 * math.cos(th) - 0.95 * math.sin(th) - 0.3

    pts: list[tuple[int, int]] = []
    steps = max(8, int(height // 3))
    for i in range(steps + 1):
        y = top + height * i / steps
        pts.append((round(cx - hw(y)), round(y)))
    for i in range(steps, -1, -1):
        y = top + height * i / steps
        pts.append((round(cx + hw(y)), round(y)))
    return Belly(pts, curve, light, staves)


def wood_fill(p: Pix, shape: Shape = None, grain_dir: str | float = "h", ramp: Ramp = WOOD, board: float | None = None,
              curve: Callable[[int, int], tuple[float, float]] | None = None, light: float = 0.5, bias: float = 0.0,
              light_fn: Callable[[int, int], float] | None = None, rim: bool = True, knots: float = 1.0,
              joints: bool = True, nails: bool = True, scratches: float = 1.0, wear_amount: float = 0.3,
              damp: float = 0.0, damp_from: str = "bottom", seed: int = 0) -> Region:
    """Boards, staves or a beam, in the cask's manner. Returns the region it painted.

    Each board gets its own tone, a lit edge toward the light and a dark seam on the far side, long grain lines that
    wander along the board and bend round every knot (knots have an eye, rings and a lit lower lip), butt joints with a
    nail on each side, scratches, wear on the shape's edges, a gradient of light across the whole region and (with
    `damp`) wet stains with a darker tide line.
    grain_dir  "h" boards run left-right and stack downward; "v" run top-bottom and stack to the right; a number is
               an angle in degrees (0 = "h")
    board      the width of a board across the grain, in px; None picks one from the region (about 5 px at 20 px high
               up to 15 px for big panels)
    curve      `(x, y) -> (a, b)`: unrolls a bellied or skewed surface into material coordinates (a along the grain, b
               across it, both in px); boards are strips of b, so joints and grain follow the surface (see `belly`)
    light      strength of the gradient across the region (lit upper left); `bias` shifts every tone (in tone steps);
               `light_fn(x, y)` adds tone steps per pixel (a cylinder's shading)
    rim        paint the region's own edges: lit top and left, dark bottom and right
    knots      density multiplier (0 none); joints and nails: butt joints with nails; scratches: density multiplier
    wear_amount  chips and nicks along the edge (see `wear`); damp 0..1: wet patches (from the "bottom", "top" or "all")
    ramp       WOOD, OAK or PALE_WOOD (any ramp of 4-5 tones, dark to light)"""
    r = region(p, shape)
    if r.empty:
        return r
    rng = _rng(p, seed)
    ns = rng.randrange(1, 200)
    x0, y0, x1, y1 = r.bbox
    top = len(ramp) - 1
    sc = top / 4
    # material coordinates of every pixel
    ang = {"h": 0.0, "v": 90.0}.get(grain_dir, grain_dir) if isinstance(grain_dir, str) else float(grain_dir)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def to_ab(x: int, y: int) -> tuple[float, float]:
        if curve is not None:
            return curve(x, y)
        lx, ly = x - x0, y - y0
        if ang == 90.0:
            return ly, lx
        return lx * ca + ly * sa, -lx * sa + ly * ca

    cells = {xy: to_ab(*xy) for xy in r.pixels()}
    amin = min(v[0] for v in cells.values())
    amax = max(v[0] for v in cells.values())
    bmin = min(v[1] for v in cells.values())
    bmax = max(v[1] for v in cells.values())
    along, across = max(1.0, amax - amin), max(1.0, bmax - bmin)
    wd0 = board if board is not None else clamp(across / 6, 5, 15)
    edges = [bmin]
    while edges[-1] < bmax + 0.5:
        edges.append(edges[-1] + wd0 * rng.uniform(0.84, 1.16))
    boards = []
    jsp = clamp(along * 0.5, 26, 150)
    for k in range(len(edges) - 1):
        b0, b1 = edges[k], edges[k + 1]
        wd = b1 - b0
        info: dict[str, Any] = {
            "tone": rng.choice((1.5, 1.85, 2.1, 2.35, 2.8)) + (rng.random() - 0.5) * 0.25,
            "j": [], "k": [], "s": [], "w": rng.randrange(1, 90)}
        if joints and along > 30 and wd >= 4:
            a = amin + rng.uniform(0.2, 1.0) * jsp
            while a < amax - 4:
                info["j"].append(a)
                a += jsp * rng.uniform(0.75, 1.35)
        if wd >= 7 and knots > 0 and rng.random() < clamp(along * wd * knots / 1500, 0, 0.75):
            kr = wd * rng.uniform(0.17, 0.27)
            info["k"].append((amin + rng.uniform(kr * 2.5, max(kr * 2.6, along - kr * 2.5)), b0 + wd * rng.uniform(0.38, 0.62), kr))
        boards.append(info)
    area = len(cells)
    for _ in range(round(area / 650 * scratches * (1 if area > 200 else 0))):
        (x, y) = rng.choice(list(cells))
        a, b = cells[(x, y)]
        k = min(len(boards) - 1, max(0, bisect_right(edges, b) - 1))
        boards[k]["s"].append((a, b, rng.uniform(4, 6 + along / 14), rng.uniform(-0.12, 0.12), rng.random() < 0.5))
    nail_r = 1.1 if wd0 >= 9 else 0.5
    pa = p.im.load()
    wet_thr = 1 - 0.55 * damp
    for (x, y), (a, b) in cells.items():
        k = min(len(boards) - 1, max(0, bisect_right(edges, b) - 1))
        bd = boards[k]
        b0, b1 = edges[k], edges[k + 1]
        wd = b1 - b0
        d0, d1 = b - b0, b1 - b
        bw = b + (vnoise(a / 60, k * 1.7, ns) - 0.5) * 3.0           # grain wanders
        ring = 99.0
        for ka, kb, kr in bd["k"]:                                   # the grain bends round a knot
            ex, ey = (a - ka) / 1.7, b - kb
            dd = math.hypot(ex, ey)
            ring = min(ring, dd / kr)
            if dd < kr * 5:
                bw = kb + (bw - kb) * (1 - 0.75 * (kr * kr) / (dd * dd + kr * kr))
        v = bd["tone"]
        v += (vnoise(a / 70, bw / 5, ns + 3) - 0.5) * 1.5            # tone drifting along a board
        n1 = vnoise(a / 34, bw * 0.95, ns + 5 + bd["w"] % 3)
        n2 = vnoise(a / 13, bw * 1.7, ns + 17)
        if abs(n1 - 0.5) < 0.05:
            v -= 0.95                                                 # a long dark grain line
        elif abs(n1 - 0.78) < 0.035 or abs(n1 - 0.2) < 0.03:
            v += 0.7                                                  # and a pale one
        if abs(n2 - 0.5) < 0.025:
            v -= 0.55                                                 # a short fine line between them
        nz = noise(x, y, ns)
        v += -0.9 if nz < 0.05 else 0.6 if nz > 0.97 else 0.0         # pores and flecks
        if light:
            v += (_smooth_light(r, x, y) * 2) * light
        if light_fn is not None:
            v += light_fn(x, y)
        v += bias
        if ring < 1.6:                                                # knot: eye, rings, lit lip
            lipx, lipy = (a - ka) / 1.7, b - kb
            if ring < 0.38:
                v = 0.15
            elif ring < 0.72:
                v -= 1.5
            elif ring < 1.0:
                v -= 0.35 + 0.35 * math.sin(ring * 14)
            elif ring < 1.3:
                v += 0.45 if lipx + lipy > 0 else -0.25
        if wd >= 3.5:
            if d0 < 1.0:
                v += 1.15
            elif d0 < 2.0 and wd >= 7:
                v += 0.35
            if d1 <= 1.0:
                v = -0.6
            elif d1 < 2.0 and wd >= 6:
                v -= 0.65
        for ja in bd["j"]:                                            # a butt joint: dark gap, lit next row, nails
            da = a - ja
            if 0 <= da < 1:
                v = -0.4
            elif 1 <= da < 2:
                v += 0.9
            if nails and wd >= 5:
                bc = b0 + wd / 2
                for nx in (ja - 2.6 - nail_r, ja + 3.2 + nail_r):
                    nd = math.hypot(a - nx, b - bc)
                    if nd <= nail_r:
                        s = (a - nx) + (b - bc)
                        pa[x, y] = (*(IRON[4] if s < -0.3 else IRON[3] if s < 0.5 else IRON[1])[:3], 255)
                        v = None  # type: ignore[assignment]
                        break
            if v is None:
                break
        if v is None:
            continue
        for sa_, sb_, ln, sl, dark in bd["s"]:                        # scratches along the grain
            if 0 <= a - sa_ < ln and abs(b - (sb_ + sl * (a - sa_))) < 0.5:
                v += -1.1 if dark else 0.9
        if damp > 0:
            lx, ly = x - x0, y - y0
            val = vnoise(lx / 12, ly / 12, ns + 7) * 0.6
            if damp_from == "bottom":
                val += (ly / max(1, y1 - y0)) * 0.55
            elif damp_from == "top":
                val += (1 - ly / max(1, y1 - y0)) * 0.55
            else:
                val += 0.25
            if val > wet_thr:
                v -= 0.9
                if val > wet_thr + 0.14 and noise(x, y, ns + 11) < 0.16:
                    c = mix(ramp[min(len(ramp) - 1, max(0, int(v * sc)))][:3], MOSS[0][:3], 0.4)
                    pa[x, y] = (*c, 255)
                    continue
            elif val > wet_thr - 0.035:
                v += 0.3
        if rim:
            up, left, down, right = r.edge(x, y, 1)
            if up == 1:
                v += 0.9
            if left == 1:
                v += 0.5
            if down == 1:
                v -= 1.1
            if right == 1:
                v -= 0.8
        c = pick_tone(ramp, v * sc, x, y)
        pa[x, y] = (c[0], c[1], c[2], 255)
    if wear_amount > 0:
        wear(p, r, wear_amount, kinds=("chip",), seed=seed)
    return r


class _BoxLike(Protocol):
    h: float
    s_far: float
    y_top: float
    vp: tuple[float, float]

    def top_poly(self) -> list[tuple[float, float]]: ...
    def front_poly(self) -> list[tuple[float, float]]: ...
    def end_poly(self) -> list[tuple[float, float]]: ...
    def end_visible(self) -> bool: ...
    def top_uv(self, x: int, y: int) -> tuple[float, float]: ...
    def end_uv(self, x: int, y: int) -> tuple[float, float]: ...
    def footprint(self) -> list[tuple[float, float]]: ...


def wood_box(p: Pix, box: _BoxLike, ramp: Ramp = WOOD, seed: int = 0, top_light: float = 0.55, front_light: float = 0.0,
             end_light: float = -0.35, **kw: Any) -> dict[str, Region]:
    """Dresses a `propsy_fx.Cuboid` (or anything with its face methods) in wood: the top face with boards that run
    across it and lean to the vanishing point, the front with level boards, the end (if visible) with grain running
    into the depth. Faces are shaded top > front > end. Returns the regions by name ('top', 'front', 'end'). Extra
    keyword arguments go to `wood_fill`."""
    out: dict[str, Region] = {}
    span = max(2.0, (box.y_top - box.vp[1]) * (1 - box.s_far))

    def top_curve(x: int, y: int) -> tuple[float, float]:
        u, xn = box.top_uv(x, y)
        return xn, (1 - u) * span * 1.8

    def end_curve(x: int, y: int) -> tuple[float, float]:
        u, v = box.end_uv(x, y)
        return u * span * 1.8, v * box.h

    out["top"] = wood_fill(p, box.top_poly(), ramp=ramp, curve=top_curve, bias=top_light, seed=seed, **kw)
    out["front"] = wood_fill(p, box.front_poly(), ramp=ramp, bias=front_light, seed=seed + 1, **kw)
    if box.end_visible():
        out["end"] = wood_fill(p, box.end_poly(), ramp=ramp, curve=end_curve, bias=end_light, seed=seed + 2, **kw)
    return out


# ---------------------------------------------------------------------------------------------- shadows


def _pad(m: Image.Image, n: int) -> Image.Image:
    out = Image.new("L", (m.width + 2 * n, m.height + 2 * n), 0)
    out.paste(m, (n, n))
    return out


def _grow(m: Image.Image, horizontal: bool = True, vertical: bool = True) -> Image.Image:
    """One pixel of growth (no wrap-around: `m` must have room around the shape)."""
    out = m
    if horizontal:
        out = ImageChops.lighter(out, ImageChops.lighter(ImageChops.offset(m, 1, 0), ImageChops.offset(m, -1, 0)))
    if vertical:
        out = ImageChops.lighter(out, ImageChops.lighter(ImageChops.offset(m, 0, 1), ImageChops.offset(m, 0, -1)))
    return out


def _apply_field(p: Pix, field: Image.Image, pad: int, skip: Region | None, color: Color, alpha: int, steps: int = 4) -> None:
    """Paints a 0..255 strength field as `steps` translucent tones with dithered joints (never a hard box, never black)."""
    f = field.crop((pad, pad, pad + p.w, pad + p.h))
    bb = f.getbbox()
    if not bb:
        return
    pa = f.load()
    for y in range(bb[1], bb[3]):
        for x in range(bb[0], bb[2]):
            lv = pa[x, y]
            if not lv or (skip is not None and skip.inside(x, y)):
                continue
            v = lv / 255 * steps
            k = int(v)
            if BAYER[y & 3][x & 3] < round((v - k) * 16):
                k += 1
            if k:
                over(p, x, y, color, min(255, alpha * min(k, steps) // steps))


def _shadow(p: Pix, shape: Shape, shift: tuple[float, float], spread: int, strength: float, color: Color, alpha: int,
            squash: float, skip_inside: bool) -> None:
    r = region(p, shape)
    if r.empty or strength <= 0:
        return
    pad = spread + int(abs(shift[0]) + abs(shift[1])) + 4
    base = ImageChops.offset(_pad(r.mask, pad), round(shift[0]), round(shift[1]))
    layers = [base]
    cur = base
    for i in range(spread):
        cur = _grow(cur, True, i % max(1, round(1 / squash)) == 0 if squash < 1 else True)
        layers.append(cur)
    field = Image.new("L", (p.w + 2 * pad, p.h + 2 * pad), 0)
    for i in range(spread, -1, -1):                                  # widest and faintest first
        lvl = round(255 * strength * (1 - i / (spread + 1)) ** 1.1)
        field.paste(lvl, mask=layers[i])
    _apply_field(p, field, pad, r if skip_inside else None, color, alpha)


def contact_shadow(p: Pix, shape: Shape, shift: tuple[float, float] = (1, 1), spread: int = 3, strength: float = 0.9,
                   color: Color = SHADOW, alpha: int = 190, squash: float = 0.5, skip_inside: bool = True) -> None:
    """The dark that gathers where an object touches a counter or floor: the footprint `shape` (use `ellipse()` for a round
    foot) nudged by `shift`, strongest at the object and fading over `spread` px in four dithered steps, flatter
    vertically (`squash` < 1) as on a surface seen from above. Draw it *before* the object; `skip_inside` keeps it off the
    footprint itself. Works over opaque pixels (it darkens them) and over a transparent layer (it leaves translucent
    pixels)."""
    _shadow(p, shape, shift, spread, strength, color, alpha, squash, skip_inside)


def wall_shadow(p: Pix, shape: Shape, offset: tuple[float, float] = (3, 4), spread: int = 3, strength: float = 0.8,
                color: Color = SHADOW, alpha: int = 170, skip_inside: bool = True) -> None:
    """The shadow of something hung on a wall (a poster, a sign, a rope): the outline of `shape` pushed by `offset`
    (down and right, away from the upper-left light), with a soft edge `spread` px wide. Draw it before the object."""
    _shadow(p, shape, offset, spread, strength, color, alpha, 1.0, skip_inside)


def cast_shadow(p: Pix, shape: Shape, direction: tuple[float, float] = (1.0, 0.45), length: int = 14, strength: float = 0.8,
                color: Color = SHADOW, alpha: int = 170, skip_inside: bool = True) -> None:
    """A shadow thrown across a surface by something that stands on it: `shape` (the footprint or silhouette)
    swept along `direction` for `length` px, strongest at the object and thinning away in four dithered tones.
    Light from the upper left throws it to the lower right."""
    r = region(p, shape)
    if r.empty:
        return
    dx, dy = direction
    norm = math.hypot(dx, dy) or 1.0
    dx, dy = dx / norm, dy / norm
    pad = length + 4
    padded = _pad(r.mask, pad)
    field = Image.new("L", padded.size, 0)
    for i in range(length, -1, -1):
        lvl = round(255 * strength * (1 - i / (length + 2)))
        field.paste(lvl, mask=ImageChops.offset(padded, round(dx * i), round(dy * i)))
    _apply_field(p, field, pad, r if skip_inside else None, color, alpha)


# ---------------------------------------------------------------------------------------------- paper


def _corner_geometry(corner: str, x0: int, y0: int, x1: int, y1: int, c: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """The corner triangle that goes, and the flap that folds over (a reflection of it across the fold line)."""
    cx = x0 if "l" in corner else x1 - 1
    cy = y0 if corner[0] == "t" else y1 - 1
    sx = -1 if "l" in corner else 1          # toward the inside along x: minus of the outward sign
    sy = -1 if corner[0] == "t" else 1
    a = (cx - sx * c, cy)
    b = (cx, cy - sy * c)
    return [a, b, (cx, cy)], [a, b, (cx - sx * c, cy - sy * c)]


def paper_fill(p: Pix, shape: Shape = None, ramp: Ramp = PARCHMENT, folds: tuple[int, int] = (1, 1), stains: float = 0.5,
               foxing: float = 0.4, tear: Sequence[str] = (), curl: Sequence[str] = (), tape: Sequence[str] = (),
               nails: Sequence[str] = (), shadow: bool = True, ink: float = 0.0, seed: int = 0) -> Region:
    """Parchment or a poster sheet. Returns the region as it ended up (after tears and curls).
    Fibre grain in short strokes, an aged darker rim (the edge pixels), a lit top and left edge and a shaded bottom and
    right edge, creases that catch the light on one side and shade the other (`folds` = vertical, horizontal count),
    tide-marked stains (`stains` 0..1), brown foxing flecks (`foxing` 0..1), optional `ink` rows of scribble (0..1 density).
    tear   corners ("tl","tr","bl","br") with a jagged tear that shows pale fibre
    curl   corners whose tip is folded over: a lighter back with its own lit edge
    tape   corners (or "t" for the top middle) held by a translucent strip of tape with a highlight
    nails  corners held by a nail head (iron, lit, with its own shadow)
    shadow a soft drop shadow onto what lies behind (call on a canvas that already holds the wall)"""
    r0 = region(p, shape)
    if r0.empty:
        return r0
    rng = _rng(p, seed + 31)
    ns = rng.randrange(1, 200)
    x0, y0, x1, y1 = r0.bbox
    w, h = x1 - x0, y1 - y0
    m = r0.mask.copy()
    md = ImageDraw.Draw(m)
    unit = max(3, round(min(w, h) * 0.17))
    torn_polys: list[list[tuple[int, int]]] = []
    flaps: list[list[tuple[int, int]]] = []
    for corner in tear:                                               # a jagged bite out of the corner
        tri, _ = _corner_geometry(corner, x0, y0, x1, y1, unit)
        (ax, ay), (bx, by), (cx_, cy_) = tri
        pts = [(ax, ay)]
        for i in range(1, 5):
            t = i / 5
            j = rng.uniform(-0.12, 0.12) * unit
            pts.append((round(ax + (bx - ax) * t + j), round(ay + (by - ay) * t + j)))
        pts += [(bx, by), (cx_, cy_)]
        md.polygon(pts, fill=0)
        torn_polys.append(pts)
    for corner in curl:
        tri, flap = _corner_geometry(corner, x0, y0, x1, y1, max(3, round(unit * 0.9)))
        md.polygon(tri, fill=0)
        flaps.append(flap)
    reg = Region(m)
    flap_mask = Image.new("L", m.size, 0)
    for f in flaps:
        ImageDraw.Draw(flap_mask).polygon(f, fill=255)
    if shadow:
        both = ImageChops.lighter(m, flap_mask)
        d = 2 if min(w, h) < 40 else 3
        wall_shadow(p, Region(both), offset=(d, d + 1), spread=2 if min(w, h) < 40 else 3, strength=0.75)
    torn_mask = Image.new("L", m.size, 0)
    for pts in torn_polys:
        ImageDraw.Draw(torn_mask).polygon(pts, fill=255)
    torn_zone = _grow(_grow(torn_mask))
    pa = p.im.load()
    fx = [(x0 + (i + 1) * w / (folds[0] + 1) + rng.uniform(-0.05, 0.05) * w) for i in range(folds[0])]
    fy = [(y0 + (i + 1) * h / (folds[1] + 1) + rng.uniform(-0.05, 0.05) * h) for i in range(folds[1])]
    base = 3.0 * (len(ramp) - 1) / 4 - 0.1
    sc = (len(ramp) - 1) / 4
    wet_thr = 0.86 - 0.2 * stains
    tz = torn_zone.load()
    for x, y in reg.pixels():
        v = base + _smooth_light(reg, x, y) * 0.5
        fib = vnoise(x / 1.4, y / 5.0, ns)
        fib2 = vnoise(x / 5.0, y / 1.4, ns + 1)
        v += 0.5 if fib > 0.82 else -0.5 if fib < 0.14 else 0.0
        v += 0.35 if fib2 > 0.85 else -0.35 if fib2 < 0.12 else 0.0
        v += (vnoise(x / 22, y / 22, ns + 2) - 0.5) * 0.7
        up, left, down, right = reg.edge(x, y, 3)
        dmin = min(up, left, down, right)
        if dmin <= 3:
            v -= (4 - dmin) * 0.28 * (1 if BAYER[y & 3][x & 3] < 11 else 0.4)      # aged rim
        if up == 1 or left == 1:
            v += 0.7
        if down == 1 or right == 1:
            v -= 0.9
        wv = vnoise(x / 15, y / 15, ns + 4) * 0.7 + vnoise(x / 6, y / 6, ns + 6) * 0.3
        if stains > 0:
            if wv > wet_thr:
                v -= 0.7
            elif wv > wet_thr - 0.025:
                v -= 1.35                                                    # the tide line
        if foxing > 0 and noise(x, y, ns + 9) < 0.012 * foxing + (0.06 * foxing if wv > wet_thr - 0.1 and noise(x // 2, y, ns + 3) < 0.2 else 0):
            pa[x, y] = (*mix(ramp[1][:3], FOXING, 0.65 if noise(x, y, ns) > 0.5 else 0.4), 255)
            continue
        for cx_ in fx:                                                      # a vertical crease
            d = x - (cx_ + (vnoise(y / 18, 0, ns + 20) - 0.5) * 2.4)
            if abs(d) < 0.5 and noise(x, y // 4, ns) > 0.1:
                v = 0.9
            elif -1.6 < d <= -0.5:
                v += 0.9
            elif 0.5 <= d < 2.4 and BAYER[y & 3][x & 3] < 10:
                v -= 0.55
        for cy_ in fy:
            d = y - (cy_ + (vnoise(x / 18, 0, ns + 21) - 0.5) * 2.4)
            if abs(d) < 0.5 and noise(x // 4, y, ns) > 0.1:
                v = 0.9
            elif -1.6 < d <= -0.5:
                v += 0.9
            elif 0.5 <= d < 2.4 and BAYER[y & 3][x & 3] < 10:
                v -= 0.55
        if tz[x, y]:
            v = len(ramp) * 0.9 if noise(x, y, ns + 13) > 0.3 else v + 1.0
        c = pick_tone(ramp, v * sc, x, y)
        pa[x, y] = (c[0], c[1], c[2], 255)
    if ink > 0:                                                              # rows of scribble
        row = max(3, round(h / 11))
        yy = y0 + max(3, h // 8)
        while yy < y1 - 3:
            xx = x0 + max(3, w // 9)
            while xx < x1 - max(3, w // 9):
                n = rng.randrange(1, max(3, w // 9))
                if rng.random() < ink * 0.9 + 0.1:
                    for i in range(n):
                        if reg.inside(xx + i, yy):
                            _tint(p, xx + i, yy, INK[2] if rng.random() < 0.8 else INK[1], 0.55)
                xx += n + rng.randrange(1, 4)
            if rng.random() < 0.2:
                yy += 1
            yy += row
    for f in flaps:                                                          # the folded-over corners
        fm = Image.new("L", m.size, 0)
        ImageDraw.Draw(fm).polygon(f, fill=255)
        freg = Region(fm)
        (ax, ay), (bx, by) = f[0], f[1]
        for x, y in freg.pixels():
            dist = abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / math.hypot(bx - ax, by - ay)
            c = pick_tone(ramp, (2.9 + 0.2 * min(1, dist / max(1, unit * 0.6)) - 0.4 * (1 - min(1, dist / 3))) * sc, x, y)
            up, left, down, right = freg.edge(x, y, 1)
            if up == 1 or left == 1:
                c = ramp[-1]
            pa[x, y] = (*c[:3], 255)
        cxm = (f[0][0] + f[1][0]) // 2
        for t in range(0, 11):                                               # the crisp fold line
            fxp = round(ax + (bx - ax) * t / 10)
            fyp = round(ay + (by - ay) * t / 10)
            _tint(p, fxp, fyp, ramp[0], 0.5)
    for corner in tape:
        _tape(p, reg, corner, rng, unit)
    for corner in nails:
        cx, cy = reg.corners().get(corner, (x0 + w // 2, y0))
        ox = 3 if "l" in corner else -3 if "r" in corner else 0
        oy = 3 if corner.startswith("b") else 3 if corner.startswith("t") else 0
        oy = oy if corner.startswith("t") else -oy
        rivet(p, cx + ox, cy + oy, 1 if min(w, h) < 60 else 2, IRON, shadow=True)
    return reg


def _tape(p: Pix, reg: Region, corner: str, rng: random.Random, unit: int) -> None:
    """A strip of translucent tape across a corner (or the top middle), with a highlight and a torn zigzag end."""
    x0, y0, x1, y1 = reg.bbox
    cx, cy = reg.corners().get(corner, ((x0 + x1) // 2, y0))
    if corner == "t":
        ang = rng.uniform(-0.12, 0.12)
    else:
        ang = (math.pi / 4 if corner in ("tl", "br") else -math.pi / 4) + rng.uniform(-0.1, 0.1)
    ln = max(8, unit * 1.6)
    wd = max(3, unit * 0.5)
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy, ux
    for i in range(int(ln * 2)):
        s = i / 2 - ln / 2
        for j in range(int(wd * 2)):
            t = j / 2 - wd / 2
            x, y = round(cx + ux * s + vx * t), round(cy + uy * s + vy * t)
            ends = abs(s) > ln / 2 - 1.2 and ((int(t * 2) + i) % 2 == 0)
            if ends:
                continue
            tone = 3 if t < -wd / 2 + 1 else 1 if t > wd / 2 - 1 else 2
            over(p, x, y, TAPE[tone], 150 if tone == 2 else 185)


# ---------------------------------------------------------------------------------------------- rope and chain


def hang_curve(a: tuple[float, float], b: tuple[float, float], sag: float, n: int = 40) -> list[tuple[float, float]]:
    """A natural hanging curve (a catenary) from point `a` to point `b`, dipping `sag` px below the straight chord at its
    lowest. `n` points; feed it to `rope` or `chain`."""
    k = 1.7
    pts = []
    for i in range(n + 1):
        t = i / n
        depth = (math.cosh(k) - math.cosh(k * (2 * t - 1))) / (math.cosh(k) - 1)
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * depth))
    return pts


def sample_path(points: Sequence[tuple[float, float]], step: float = 0.5) -> list[tuple[float, float, float, float, float]]:
    """Resamples a polyline at `step` px: a list of (x, y, tangent x, tangent y, distance along)."""
    out: list[tuple[float, float, float, float, float]] = []
    s = 0.0
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        seg = math.hypot(bx - ax, by - ay)
        if seg == 0:
            continue
        tx, ty = (bx - ax) / seg, (by - ay) / seg
        t = 0.0
        while t < seg:
            out.append((ax + tx * t, ay + ty * t, tx, ty, s + t))
            t += step
        s += seg
    if points and out:
        (lx, ly), (tx, ty) = points[-1], out[-1][2:4]
        out.append((lx, ly, tx, ty, s))
    return out


def _cyl_idx(u: float, nx: float, ny: float, low: float = 0.35, high: float = 4.2) -> float:
    """Tone index for a point at `u` (-1..1) across a tube whose axis is perpendicular to the screen normal (nx, ny):
    the lit upper-left side is bright, the underside dark."""
    z = math.sqrt(max(0.0, 1 - u * u))
    d = LIGHT[0] * u * nx + LIGHT[1] * u * ny + LIGHT[2] * z
    return low + (high - low) * clamp(d * 1.05)


def _path_mask(size: tuple[int, int], pts: Sequence[tuple[float, float]], width: float) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).line([(round(x), round(y)) for x, y in pts], fill=255, width=max(1, math.ceil(width)), joint="curve")
    return m


def _ball(p: Pix, cx: float, cy: float, rad: float, ramp: Ramp, phase: float = 0.0) -> None:
    """A rope knot: a lit, wrapped ball."""
    ri = int(rad + 1)
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            d = math.hypot(dx, dy)
            if d > rad:
                continue
            nx, ny = dx / rad, dy / rad
            z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            lit = LIGHT[0] * nx + LIGHT[1] * ny + LIGHT[2] * z
            v = 0.4 + 3.9 * clamp(lit * 1.05)
            if ((dx - dy) + phase) % 3 < 0.9:
                v -= 0.9
            if d > rad - 0.8:
                v = min(v, 1.0 if lit < 0.4 else 1.8)
            x, y = round(cx + dx), round(cy + dy)
            p.px(x, y, pick_tone(ramp, v, x, y, 3.0))


def rope(p: Pix, points: Sequence[tuple[float, float]], thickness: float = 5.0, ramp: Ramp = ROPE, fray: tuple[bool, bool] = (False, False),
         knots: Sequence[float] = (), shadow: bool = True, pitch: float | None = None, seed: int = 0) -> None:
    """A twisted rope along a polyline (use `hang_curve` or `coil` for the points). The tube is lit on its upper-left
    side and dark underneath, strands run as diagonal ridges with a dark groove between them, the outermost pixels
    form a dark edge, and a soft shadow falls onto the wall behind.
    thickness  diameter in px (works from 2 px cord to 12 px hawser)
    fray       (start, end): unravel that end into wisps of loose fibre with a ragged cut
    knots      positions along the rope as shares 0..1: a wrapped ball is tied there
    shadow     cast a wall shadow of the whole path first
    pitch      the length of one strand turn in px (default from thickness)"""
    pts = list(points)
    if len(pts) < 2:
        return
    rng = _rng(p, seed + 41)
    if shadow:
        wall_shadow(p, Region(_path_mask((p.w, p.h), pts, thickness)), offset=(2, 3 if thickness > 3 else 2), spread=2,
                    strength=0.7, skip_inside=False)
    samples = sample_path(pts, 0.5)
    total = samples[-1][4]
    r = thickness / 2
    pitch = pitch or max(2.6, thickness * 1.0)
    frayl = thickness * 1.5
    ts = [-r + 0.25 + i * 0.5 for i in range(max(2, int(2 * r / 0.5)))]
    ph0 = rng.random()
    for x, y, tx, ty, s in samples:
        if fray[0] and s < frayl * 0.3 or fray[1] and s > total - frayl * 0.3:
            near = min(s, total - s) if (fray[0] and s < frayl * 0.3) else total - s
            if noise(int(x), int(y), 5) < 0.55 * (1 - near / (frayl * 0.3)):
                continue
        nx, ny = -ty, tx
        for t in ts:
            u = t / r
            idx = _cyl_idx(u, nx, ny)
            q = (s / pitch + u * 0.55 + ph0) % 1.0
            idx += 0.6 * math.cos(2 * math.pi * q)
            if abs(q - 0.5) < 0.075:
                idx -= 1.15                                             # the groove between two strands
            if abs(u) > 1 - 0.5 / max(1.0, r):
                idx = min(idx, 1.2 if (nx * u * LIGHT[0] + ny * u * LIGHT[1]) < 0 else 2.0)   # edge
            px_, py_ = round(x + nx * t), round(y + ny * t)
            p.px(px_, py_, pick_tone(ramp, idx, px_, py_, 3.2))
    for kf in knots:                                                    # knots
        i = min(len(samples) - 1, int(kf * len(samples)))
        _ball(p, samples[i][0], samples[i][1], r * 1.3 + 0.6, ramp, rng.random() * 3)
    for end, flag in ((0, fray[0]), (-1, fray[1])):                      # loose fibre at the ends
        if not flag:
            continue
        x, y, tx, ty, _ = samples[0 if end == 0 else -1]
        if end == 0:
            tx, ty = -tx, -ty
        for wsp in range(max(3, round(thickness * 0.9))):
            ang = (wsp / max(1, round(thickness * 0.9) - 1) - 0.5) * 1.1 + rng.uniform(-0.12, 0.12)
            ca, sa = math.cos(ang), math.sin(ang)
            dx, dy = tx * ca - ty * sa, tx * sa + ty * ca
            ox = (wsp / max(1, round(thickness * 0.9) - 1) - 0.5) * thickness * 0.7
            ln = rng.uniform(frayl * 0.6, frayl * 1.3)
            curl = rng.uniform(-0.04, 0.05)
            cx, cy = x - ty * ox * (1 if end else -1), y + tx * ox * (1 if end else -1)
            tone = rng.choice((2, 3, 3, 4))
            for i in range(int(ln)):
                p.px(round(cx + dx * i - dy * curl * i * i), round(cy + dy * i + dx * curl * i * i),
                     ramp[tone] if i < ln * 0.8 else ramp[min(4, tone + 1)] if rng.random() < 0.5 else ramp[1])


def coil(p: Pix, cx: float, cy: float, rx: float, ry: float, turns: int = 3, thickness: float = 5.0, ramp: Ramp = ROPE,
         tail: bool = True, seed: int = 0) -> None:
    """A coil of rope lying on a surface, seen from above-front: a spiral of `turns` loops, `rx` x `ry` at the outer loop
    with each loop a little smaller and lifted, a contact shadow under it, and a loose end that trails off to the right
    (fraying)."""
    lift = thickness * 0.55
    n = 36 * turns
    pts = []
    for i in range(n + 1):
        t = i / 36
        a = math.pi / 2 + t * 2 * math.pi
        k = 1 - 0.1 * t
        pts.append((cx + rx * k * math.cos(a), cy - lift * t + ry * k * math.sin(a)))
    contact_shadow(p, ellipse(cx + 1, cy + thickness * 0.35, rx + thickness * 0.5, ry + thickness * 0.6), spread=3, strength=0.85)
    if tail:
        sx, sy = pts[0]
        ex, ey = sx + rx * 0.55, sy + thickness * 0.5
        pts = [(ex, ey), (sx + rx * 0.3, sy + thickness * 0.55), (sx + rx * 0.1, sy + thickness * 0.1)] + pts
    rope(p, pts, thickness, ramp, fray=(tail, False), shadow=False, seed=seed)


def chain(p: Pix, points: Sequence[tuple[float, float]], link: float = 8.0, ramp: Ramp = IRON, shadow: bool = True) -> None:
    """An iron chain along a polyline (try `hang_curve` for the points): oval links alternate with links seen edge-on,
    each shaded as a bent wire (lit upper left, dark underside, a dark inner hole), with a wall shadow.
    link  the length of one link in px (4 for fine jewellery chain up to 14 for a well chain)"""
    pts = list(points)
    if len(pts) < 2:
        return
    if shadow:
        wall_shadow(p, Region(_path_mask((p.w, p.h), pts, max(2, link * 0.5))), offset=(2, 3), spread=2, strength=0.65, skip_inside=False)
    samples = sample_path(pts, 0.5)
    total = samples[-1][4]
    pitch = link * 0.74
    wire = max(1.0, link / 4.2)
    wd = link * 0.62
    k = 0
    s = link / 2
    while s < total - link * 0.3:
        x, y, tx, ty, _ = samples[min(len(samples) - 1, int(s / 0.5))]
        if k % 2 == 0:
            ri = int(link / 2 + 2)
            for dy in range(-ri, ri + 1):
                for dx in range(-ri, ri + 1):
                    u, v = dx * tx + dy * ty, -dx * ty + dy * tx
                    rho = math.hypot(u / (link / 2), v / (wd / 2))
                    inner = math.hypot(u / max(0.5, link / 2 - wire), v / max(0.5, wd / 2 - wire))
                    if rho > 1 or inner < 1:
                        continue
                    ox, oy = u / (link / 2) ** 2, v / (wd / 2) ** 2         # outward normal in the link's frame
                    nx, ny = ox * tx - oy * ty, ox * ty + oy * tx
                    nl = math.hypot(nx, ny) or 1
                    dd = (nx * LIGHT[0] + ny * LIGHT[1]) / nl
                    val = 2.0 + 2.0 * dd * (1 if rho > 0.78 else -1)
                    if rho > 0.93:
                        val -= 0.7
                    xx, yy = round(x + dx), round(y + dy)
                    p.px(xx, yy, pick_tone(ramp, val, xx, yy, 3.0))
        else:
            for i in range(int(-link * 0.32), int(link * 0.32) + 1):
                for t in range(-int(wire), int(wire) + 1):
                    u = t / max(1.0, wire + 0.5)
                    xx, yy = round(x + tx * i - ty * t), round(y + ty * i + tx * t)
                    p.px(xx, yy, pick_tone(ramp, _cyl_idx(u, -ty, tx, 0.5, 4.0) - (0.8 if abs(i) > link * 0.28 else 0), xx, yy, 3.0))
        s += pitch
        k += 1


# ---------------------------------------------------------------------------------------------- metal


def rivet(p: Pix, x: int, y: int, r: int = 2, ramp: Ramp = BRASS, shadow: bool = True) -> None:
    """A domed rivet or stud centred on (x, y), radius `r` px (1 gives a plus of five pixels, 2 a round head, 3 a boss):
    bright spot upper left, dark rim lower right, and a one-pixel shadow it throws on the surface to its lower right."""
    top = len(ramp) - 1
    rr = r + 0.35
    if shadow:
        for dy in range(-r, r + 2):
            for dx in range(-r, r + 2):
                if math.hypot(dx - 1, dy - 1) <= rr and math.hypot(dx, dy) > rr:
                    _tint(p, x + dx, y + dy, SHADOW, 0.55)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > rr:
                continue
            nx, ny = dx / (rr + 0.5), dy / (rr + 0.5)
            z = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            lit = LIGHT[0] * nx + LIGHT[1] * ny + LIGHT[2] * z
            v = top * clamp(0.18 + lit * 0.95)
            if r >= 2 and dx == -(r // 2) and dy == -(r // 2):
                v = top
            elif d > rr - 0.6 and dx + dy > 0:
                v = min(v, 0.9)
            p.px(x + dx, y + dy, ramp[max(0, min(top, round(v)))])


def _rivet_row(p: Pix, r: Region, spacing: int, rr: int, ramp: Ramp) -> None:
    x0, y0, x1, y1 = r.bbox
    horizontal = r.width >= r.height
    length = r.width if horizontal else r.height
    n = max(1, int(length // spacing))
    start = (length - (n - 1) * spacing) // 2
    for i in range(n):
        x, y = (x0 + start + i * spacing, (y0 + y1 - 1) // 2) if horizontal else ((x0 + x1 - 1) // 2, y0 + start + i * spacing)
        if r.inside(x, y):
            rivet(p, x, y, rr, ramp)


def iron_fill(p: Pix, shape: Shape = None, ramp: Ramp = IRON, hammer: float = 0.5, rust: float = 0.3, scratches: float = 0.6,
              rivets: int = 0, rivet_ramp: Ramp = BRASS, light: float = 0.5, bias: float = 0.0, seed: int = 0) -> Region:
    """Forged iron: a base tone that drifts as the smith drew it out, hammer dimples (dark upper-left, lit lower-right),
    streaks along the long axis, a lit top and left edge (two rows when the band is thick) and a dark bottom and right
    edge, rust flecks that gather on the edges and low parts, scratches and nicks.
    hammer 0..1 dimple density; rust 0..1; scratches 0..1; rivets: spacing in px of a row of rivets down the
    middle of a strap (0 none); light: strength of the upper-left gradient. Returns the region."""
    r = region(p, shape)
    if r.empty:
        return r
    rng = _rng(p, seed + 51)
    ns = rng.randrange(1, 200)
    x0, y0, x1, y1 = r.bbox
    top = len(ramp) - 1
    sc = top / 4
    thick = min(r.width, r.height)
    dents: dict[tuple[int, int], float] = {}
    for _ in range(round(r.width * r.height * hammer / 22)):
        x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
        big = rng.random() < 0.3 and thick >= 8
        for dx, dy, dv in ((-1, -1, -0.85), (0, 0, -0.25), (1, 1, 0.85), (0, -1, -0.5), (-1, 0, -0.5), (1, 0, 0.35), (0, 1, 0.35)) if big else ((-1, -1, -1.0), (0, 0, -0.15), (1, 1, 1.0)):
            dents[(x + dx, y + dy)] = dv
    horizontal = r.width >= r.height
    pa = p.im.load()
    for x, y in r.pixels():
        v = 2.0 + (_smooth_light(r, x, y) * 2) * light + bias
        v += (vnoise(x / 7, y / 7, ns) - 0.5) * 0.8
        v += (vnoise(x / 16, y / 2.2, ns + 1) - 0.5) * 0.7 if horizontal else (vnoise(x / 2.2, y / 16, ns + 1) - 0.5) * 0.7
        v += dents.get((x, y), 0.0)
        up, left, down, right = r.edge(x, y, 2)
        if up == 1:
            v += 1.9
        elif up == 2 and thick >= 6:
            v += 0.7
        if left == 1:
            v += 1.1
        if down == 1:
            v -= 2.0
        elif down == 2 and thick >= 6:
            v -= 0.55
        if right == 1:
            v -= 1.3
        edgey = min(up, left, down, right) <= 2
        c = pick_tone(ramp, v * sc, x, y, 3.0)
        rn = noise(x, y, ns + 4)
        low = (y - y0) / max(1, y1 - y0)
        if rust > 0 and (rn < rust * (0.012 + (0.05 if edgey else 0) + 0.02 * low) or
                         (vnoise(x / 5, y / 5, ns + 8) > 0.9 - 0.08 * rust and noise(x, y, ns + 9) < 0.6 and rust > 0.35)):
            c = RUST[1] if rn < rust * 0.01 else RUST[2] if (x + y) % 2 else RUST[0] if low > 0.5 else RUST[1]
        pa[x, y] = (c[0], c[1], c[2], 255)
    if rivets:
        _rivet_row(p, r, rivets, 1 if thick < 10 else 2, rivet_ramp)
    wear(p, r, scratches * 0.45, kinds=("scratch", "chip"), seed=seed + 3)
    return r


def iron_band(p: Pix, points: Sequence[tuple[float, float]], thickness: int = 5, rivets: int = 0, rivet_ramp: Ramp = BRASS,
              **kw: Any) -> Region:
    """An iron ribbon that follows a curve (a hoop round a cask, a curved strap): the polyline `points` is its upper
    edge and the band is `thickness` px tall below it. Painted by `iron_fill` (extra keywords go there), so it has the
    lit top edge and dark underside; `rivets` is the spacing in px of brass rivets along its middle (0 none)."""
    pts = [(round(x), round(y)) for x, y in points]
    poly = pts + [(x, y + thickness - 1) for x, y in reversed(pts)]
    r = iron_fill(p, poly, **kw)
    if rivets:
        samples = sample_path(points, 1.0)
        total = samples[-1][4] if samples else 0
        n = max(1, int(total // rivets))
        for i in range(n):
            s = (i + 0.5) * total / n
            x, y = next(((sx, sy) for sx, sy, _, _, ss in samples if ss >= s), samples[-1][:2])
            rivet(p, round(x), round(y) + thickness // 2, 1 if thickness < 8 else 2, rivet_ramp)
    return r


def brass_fill(p: Pix, shape: Shape = None, ramp: Ramp = BRASS, profile: str = "plate", tarnish: float = 0.5, studs: int = 0,
               light: float = 0.5, seed: int = 0) -> Region:
    """Brass with a specular highlight and tarnish. Returns the region.
    profile  "plate" flat sheet: a soft elliptical highlight at the upper left; "tube" shaded across the short side
             like a cylinder (bright stripe a third in, dark far side), for pipes, taps and handles; "dome" a boss
             lit like a sphere (highlight upper left, dark rim lower right)
    tarnish  0..1: dark, greenish tarnish in recesses (the edges and creases) and in patches
    studs    spacing in px of a row of brass studs through the middle (plate profile; 0 none)
    A one-pixel dark outline and a lit top-left rim keep the silhouette crisp."""
    r = region(p, shape)
    if r.empty:
        return r
    rng = _rng(p, seed + 61)
    ns = rng.randrange(1, 200)
    x0, y0, x1, y1 = r.bbox
    w, h = r.width, r.height
    top = len(ramp) - 1
    sc = top / 4
    horizontal = w >= h
    pa = p.im.load()
    for x, y in r.pixels():
        nx, ny = (x - x0 + 0.5) / w, (y - y0 + 0.5) / h
        if profile == "tube":
            t = ny if horizontal else nx
            v = 1.9 + 2.3 * math.exp(-((t - 0.3) / 0.15) ** 2) + 0.6 * math.exp(-((t - 0.06) / 0.05) ** 2) - 1.5 * clamp((t - 0.62) / 0.38)
            v += 0.35 * (0.5 - (nx if horizontal else ny)) * light * 2
        elif profile == "dome":
            dx, dy = (nx - 0.5) * 2, (ny - 0.5) * 2
            z = math.sqrt(max(0.0, 1 - min(1.0, dx * dx + dy * dy)))
            lit = LIGHT[0] * dx + LIGHT[1] * dy + LIGHT[2] * z
            v = 0.3 + 4.3 * clamp(lit * 1.05)
        else:
            v = 2.35 + (0.5 - (nx + ny) / 2) * 1.2 * light * 2
            v += 1.9 * math.exp(-(((nx - 0.28) / 0.22) ** 2 + ((ny - 0.3) / 0.3) ** 2))
            v -= 0.5 * clamp((nx + ny - 1.1))
        v += (vnoise(x / 4, y / 4, ns) - 0.5) * 0.4
        up, left, down, right = r.edge(x, y, 2)
        dmin = min(up, left, down, right)
        if up == 1 or left == 1:
            v += 1.0
        if down == 1 or right == 1:
            v -= 1.4
        patch = vnoise(x / 6, y / 6, ns + 2)
        if tarnish > 0 and ((dmin <= 2 and noise(x, y, ns + 3) < 0.45 * tarnish) or (patch > 0.86 - 0.16 * tarnish and noise(x, y, ns + 6) < 0.55)):
            v -= 1.2
            c = pick_tone(ramp, v * sc, x, y, 3.0)
            if noise(x, y, ns + 5) < 0.28 * tarnish:
                c = mix(c[:3], VERDIGRIS[1][:3], 0.55)
        else:
            c = pick_tone(ramp, v * sc, x, y, 3.0)
        pa[x, y] = (c[0], c[1], c[2], 255)
    if studs and profile != "tube":
        _rivet_row(p, r, studs, 1 if min(w, h) < 10 else 2, ramp)
    wear(p, r, 0.2, kinds=("scratch",), seed=seed + 7)
    return r


# ---------------------------------------------------------------------------------------------- glass


def glass_pane(p: Pix, shape: Shape = None, cols: int = 2, rows: int = 3, came: int | None = None, tint: Color = GLASS[3],
               alpha: int = 72, streaks: int = 2, back: bool = True, lead: Ramp = IRON, seed: int = 0) -> Region:
    """A leaded window pane: a grid of `cols` x `rows` panes held by lead cames (lit on the top and left, dark on the
    bottom and right), tinted glass that stays translucent (`alpha` 0..255 per pixel; paint it into a layer that
    lies over the scene and the scene shows through), diagonal reflection streaks that run across all the panes, a
    bright glint in the upper-left corner of each pane, and per-pane tone variation like hand-made crown glass.
    came    width of the lead in px (None scales with the pane size, 1 to 3)
    streaks 0..3 reflection bands
    back    show the glass's back: a dark thickness line along the lower and right edge of each pane, a faint doubled
            reflection from the rear surface, and a few seed bubbles (all translucent)"""
    r = region(p, shape)
    if r.empty:
        return r
    rng = _rng(p, seed + 71)
    x0, y0, x1, y1 = r.bbox
    w, h = r.width, r.height
    cw = came if came is not None else int(clamp(round(min(w / cols, h / rows) / 14), 1, 3))
    vx = [x0 + round(i * (w - cw) / cols) for i in range(cols + 1)]
    vy = [y0 + round(i * (h - cw) / rows) for i in range(rows + 1)]
    bands = [(0.34, 0.075, 80), (0.46, 0.022, 135), (0.60, 0.012, 95)][:max(0, streaks)]
    ptone = [rng.randrange(-8, 9) for _ in range(cols * rows)]
    bubbles = {(rng.randrange(x0, x1), rng.randrange(y0, y1)) for _ in range(round(w * h / 380))} if back else set()
    for x, y in r.pixels():
        ix = next((i for i, c in enumerate(vx) if c <= x < c + cw), None)
        iy = next((i for i, c in enumerate(vy) if c <= y < c + cw), None)
        if ix is not None or iy is not None:                         # lead came
            kx = x - vx[ix] if ix is not None else None
            ky = y - vy[iy] if iy is not None else None
            lit = (kx == 0) or (ky == 0)
            dark = (kx == cw - 1 and cw > 1) or (ky == cw - 1 and cw > 1)
            tone = 3 if lit and not dark else 0 if dark and not lit else 2 if cw > 2 or lit else 1
            if cw == 1:
                tone = 2 if (x + y) % 3 else 1
            over(p, x, y, lead[min(tone, len(lead) - 1)])
            continue
        pcol = max(0, min(cols - 1, bisect_right(vx, x) - 1))
        prow = max(0, min(rows - 1, bisect_right(vy, y) - 1))
        pj = ptone[prow * cols + pcol]
        a0 = alpha + pj + round(18 * (y - y0) / h)
        c = mix(tint[:3], GLASS[2][:3], 0.5 + 0.5 * vnoise(x / 9, y / 9, 3) - 0.3)
        over(p, x, y, c, clamp(a0 / 255) * 255 // 1 if a0 < 255 else 255)
        dg = (x - x0 + (y - y0) * 0.9) / (w + h * 0.9)
        for cen, wid, al in bands:
            if abs(dg - cen) < wid / 2:
                edge = abs(dg - cen) > wid / 2 - 0.012
                if not edge or BAYER[y & 3][x & 3] < 8:
                    over(p, x, y, GLASS[4], al)
            if back and abs(dg - (cen + 0.055)) < wid / 4 and BAYER[y & 3][x & 3] < 5:
                over(p, x, y, GLASS[3], 55)                          # the rear surface's fainter echo
        if back:
            nxt_x = any(c <= x + 1 < c + cw for c in vx) or x + 1 >= x1
            nxt_y = any(c <= y + 1 < c + cw for c in vy) or y + 1 >= y1
            if nxt_x or nxt_y:
                over(p, x, y, GLASS[0], 105)                         # glass thickness, in shade
            prev_x = any(c <= x - 1 < c + cw for c in vx)
            prev_y = any(c <= y - 1 < c + cw for c in vy)
            if (prev_x and (x - vx[ix if ix is not None else 0]) >= 0 and noise(x, y, 2) < 0.4) or (prev_y and noise(x, y, 3) < 0.4):
                over(p, x, y, GLASS[4], 70)                          # lit inner edge
            if (x, y) in bubbles:
                over(p, x, y, GLASS[4], 150)
                over(p, x + 1, y + 1, GLASS[0], 90)
        gx, gy = x - (vx[pcol] + cw), y - (vy[prow] + cw)
        gl = 1 + (min(w / cols, h / rows) > 30)
        if (gy == 0 and gx <= gl) or (gx == 0 and gy <= gl - (gl == 1)):
            over(p, x, y, GLASS[4], 225)                             # the glint in each pane's upper-left corner
    return r


# ---------------------------------------------------------------------------------------------- cloth


def cloth_fill(p: Pix, shape: Shape = None, ramp: Ramp = LINEN, kind: str = "linen", folds: int | None = None,
               fold_dir: str = "v", stitch: str = "", fray: str = "", weave: int | None = None, light: float = 0.5,
               seed: int = 0) -> Region:
    """Linen or wool. Returns the region.
    kind      "linen" a fine checker weave with slub threads; "wool" a fuzzier knit-like dither with pale fibres
    folds     number of soft folds (None: about one per 18 px); `fold_dir` "v" folds hang down, "h" run across
    fold light the left side of every fold catches the light, the right is shaded, the valleys are deep
    stitch    sides ("t","l","b","r" combined, e.g. "tb") with a hem seam 3 px in: dashes of pale thread with dark holes
    fray      sides whose edge is frayed: ragged pixels and loose threads past the edge
    weave     thread size in px (None: 1, or 2 on big pieces)
    light     the gradient across the piece (lit upper left)
    ramp      LINEN, WINE, MOSS, NAVY, LEATHER... (4 or 5 tones, dark to light)"""
    r = region(p, shape)
    if r.empty:
        return r
    rng = _rng(p, seed + 81)
    ns = rng.randrange(1, 200)
    x0, y0, x1, y1 = r.bbox
    w, h = r.width, r.height
    top = len(ramp) - 1
    cell = weave or (2 if min(w, h) > 90 else 1)
    across = w if fold_dir == "v" else h
    nf = folds if folds is not None else max(1, round(across / 18))
    per = across / nf
    pa = p.im.load()
    hem = 3 if min(w, h) > 14 else 2
    dirs = {"t": (0, -1), "l": (-1, 0), "b": (0, 1), "r": (1, 0)}
    side_idx = {"t": 0, "l": 1, "b": 2, "r": 3}
    for x, y in r.pixels():
        lx, ly = x - x0, y - y0
        b, a = (lx, ly) if fold_dir == "v" else (ly, lx)
        phase = b / per + (vnoise(a / 35, b / 30, ns) - 0.5) * 0.9 + a * 0.0025
        amp = 0.45 + 0.75 * vnoise(a / 45, 0.5, ns + 2)
        v = top * 0.58
        v += amp * 1.05 * math.cos(2 * math.pi * phase)
        if math.sin(2 * math.pi * phase) < -0.85:
            v -= 0.45
        v += (_smooth_light(r, x, y) * 2) * light
        gx, gy = lx // cell, ly // cell
        if kind == "wool":
            n = noise(gx, gy, ns)
            v += (0.2 if (gx + gy) % 2 else -0.14) + (0.55 if n > 0.9 else -0.5 if n < 0.08 else 0.0)
            if (gx * 3 + gy) % 5 == 0:
                v -= 0.18
        else:
            v += 0.11 if (gx + gy) % 2 == 0 else -0.09
            if gy % 3 == 0:
                v += 0.07
            slub = vnoise(x / 7, y / 1.2, ns + 3) if fold_dir == "v" else vnoise(x / 1.2, y / 7, ns + 3)
            if slub > 0.84:
                v += 0.35
            elif slub < 0.08:
                v -= 0.25
        edges = r.edge(x, y, hem + 1)
        skip = False
        for sd in stitch:
            d = edges[side_idx[sd]]
            if d == hem:
                dash = ((x + y) // 2) % 2 == 0
                v = top if dash else v - 1.1
            elif d < hem:
                v -= 0.28
        for sd in fray:
            d = edges[side_idx[sd]]
            if d == 1 and noise(x, y, ns + 6) < 0.45 or d == 2 and noise(x, y, ns + 7) < 0.14:
                skip = True
            elif d <= 3:
                v += 0.25 if noise(x, y, ns + 8) > 0.5 else -0.2
        if skip:
            continue
        if edges[0] == 1 or edges[1] == 1:
            v += 0.3
        if edges[2] == 1 or edges[3] == 1:
            v -= 0.6
        c = pick_tone(ramp, v, x, y, 3.0)
        pa[x, y] = (c[0], c[1], c[2], 255)
    for sd in fray:                                                  # loose threads past the edge
        dx, dy = dirs[sd]
        for x, y in r.pixels():
            if r.edge(x, y, 1)[side_idx[sd]] != 1 or noise(x, y, ns + 12) > 0.34 or not _is_painted(p, x, y):
                continue
            n = 1 + int(noise(x, y, ns + 13) * 3.5)
            col = ramp[min(top, 2 + (noise(x, y, ns + 14) > 0.5))]
            for i in range(1, n + 1):
                xx, yy = x + dx * i + (1 if (noise(x, y, ns + 15) > 0.7 and i > 1) else 0) * abs(dy), y + dy * i + (1 if (noise(x, y, ns + 15) > 0.7 and i > 1) else 0) * abs(dx)
                if not r.inside(xx, yy):
                    p.px(xx, yy, col if i < n else ramp[max(0, top - 1)])
    return r


def _is_painted(p: Pix, x: int, y: int) -> bool:
    return p.get(x, y)[3] > 0
