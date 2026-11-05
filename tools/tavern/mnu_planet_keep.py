"""The floating citadel of the main-menu picture, in the place and at the angle of the original's orbital station.

Why it floats: the island is a stone the old masters hollowed and hung under four patched lift-envelopes (gas bags of
oiled canvas, moored with ropes to the island's rim); two great wind-wheels on outriggers are its sails and keep it
turning to the wind (they stand where the station has its solar arrays). Where people live: the long Hall (west) is the
barracks and kitchen, the East Hall is the lord's, the round Hub Tower is the lift-winch and watch with a wooden Dock
Ring round it where airships tie up (the station's docking ring), the Beacon Tower with its masts and pennants stands
in the upper right (the antennas), farms and an orchard grow on the lower-left end, and casks of water and ballast hang
on chains under the rim (the tanks).

Geometry: everything is placed in a frame (u along the keep's axis toward the upper right, v across it toward the
viewer, h up) and projected to the screen with `pt3`; faces are parallelograms painted pixel by pixel. Light comes from
the right and above, so right faces are lit and left faces shaded.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from typing import Final

from PIL import Image, ImageDraw

from fxkit import clamp, noise, pick_tone, vnoise
from pix import BAYER, Color, Pix, mix, rgb

OX, OY = 178.0, 163.0
UX, UY = 0.86, -0.775
VX, VY = 0.68, 0.76
HS: Final = 0.95


def r_(*hexes: str) -> list[Color]:
    return [rgb(h) for h in hexes]


ROCK = r_("#231c2c", "#382e3e", "#51444e", "#6e6064", "#8e7d78", "#b49c88")
EARTH = r_("#2e2418", "#4a3a22", "#665228", "#827034", "#a28c46")
GRASS = r_("#2a2c1c", "#444626", "#62602c", "#847c36", "#a89a48")
SLATE = r_("#1a182a", "#2a2842", "#3e3e5c", "#585a78", "#7c829e")
TILE = r_("#341420", "#58202a", "#823230", "#ac4c38", "#d2764a", "#eca06a")
VERD = r_("#1c3630", "#2c5848", "#468066", "#74ac8e", "#a8d0b0")
STONE = r_("#2c2830", "#443f46", "#5e5858", "#7a736c", "#9a9084", "#bcb09c")
PLAS = r_("#4a3c34", "#6e5a48", "#92795a", "#b49a70", "#d2bc8c")
TIMBER = r_("#1c120e", "#32201a", "#4c3022", "#684428", "#8a5c32")
DECK = r_("#2c1c14", "#46301c", "#644426", "#845e34", "#a67c46", "#c89c5c")
CANVAS = r_("#4e4658", "#756c78", "#a0958e", "#cabba2", "#ecdcb8")
WINE = r_("#2a0e18", "#4c1822", "#722a2c", "#9a4036", "#c0664a")
BRASS = r_("#3a2a12", "#6b4c1c", "#a07a2c", "#d0a847", "#f0d27a")
IRON = r_("#16141c", "#2a2830", "#44424c", "#625f68", "#86838c")
ROPE = r_("#3a2a1a", "#6a5030", "#9a7c4c", "#c4a470", "#e4cc98")
LIGHT_WIN = (rgb("#ff9a3a"), rgb("#ffc860"), rgb("#ffe8a0"))
OUTLINE = rgb("#150e16")


def pt3(u: float, v: float, h: float) -> tuple[float, float]:
    return OX + u * UX + v * VX, OY + u * UY + v * VY - h * HS


def vn(x: float, y: float, s: int = 0) -> float:
    return vnoise(x, y, s)


def tone(r: Sequence[Color], v: float, x: int, y: int, crisp: float = 2.4) -> Color:
    return pick_tone(r, clamp(v) * (len(r) - 1), x, y, crisp)


def bay(x: int, y: int) -> float:
    return (BAYER[y & 3][x & 3] + 0.5) / 16


# ------------------------------------------------------------------------------------------------ painting primitives
def _mask(p: Pix, poly: Sequence[tuple[float, float]]) -> tuple[Image.Image, int, int, int, int]:
    pts = [(round(x), round(y)) for x, y in poly]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    x0, x1, y0, y1 = max(0, min(xs)), min(p.w - 1, max(xs)), max(0, min(ys)), min(p.h - 1, max(ys))
    m = Image.new("L", (p.w, p.h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m, x0, x1, y0, y1


def fill(p: Pix, poly: Sequence[tuple[float, float]], fn: Callable[[int, int], Color | None]) -> None:
    """Paints every pixel inside the polygon with whatever fn(x, y) returns (None leaves it)."""
    m, x0, x1, y0, y1 = _mask(p, poly)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if m.getpixel((x, y)):
                c = fn(x, y)
                if c is not None:
                    p.px(x, y, c)


def quad(p: Pix, a: tuple[float, float], b: tuple[float, float], d: tuple[float, float],
         fn: Callable[[float, float, int, int], Color | None]) -> None:
    """A parallelogram a, b, b+d-a, d painted by fn(s, t, x, y), s from a toward b and t from a toward d."""
    sx, sy, tx, ty = b[0] - a[0], b[1] - a[1], d[0] - a[0], d[1] - a[1]
    det = sx * ty - sy * tx
    if abs(det) < 1e-6:
        return
    poly = [a, b, (b[0] + tx, b[1] + ty), d]

    def f(x: int, y: int) -> Color | None:
        dx, dy = x + 0.5 - a[0], y + 0.5 - a[1]
        s = (dx * ty - dy * tx) / det
        t = (sx * dy - sy * dx) / det
        return fn(min(1.0, max(0.0, s)), min(1.0, max(0.0, t)), x, y)

    fill(p, poly, f)


def circ3(u: float, v: float, h: float, r: float, n: int = 32) -> list[tuple[float, float]]:
    return [pt3(u + r * math.cos(2 * math.pi * k / n), v + r * math.sin(2 * math.pi * k / n), h) for k in range(n)]


def shade_poly(p: Pix, poly: Sequence[tuple[float, float]], amount: float, only_world: bool = True, soft: bool = True) -> None:
    """Darkens what is under the polygon (a cast shadow), dithered, never on the sky."""
    dark = rgb("#1a0e22")
    m, x0, x1, y0, y1 = _mask(p, poly)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if m.getpixel((x, y)) and (not only_world or math.hypot(x - 400.0, y - 602.0) < 524):
                if not soft or amount > bay(x, y) * 0.9 or amount >= 1:
                    c = p.get(x, y)[:3]
                    p.px(x, y, mix(c, dark, 0.62 if amount >= 1 else 0.36))


def line(p: Pix, a: tuple[float, float], b: tuple[float, float], c: Color) -> None:
    p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), c)


def edge_lit(p: Pix, poly: Sequence[tuple[float, float]], lit: Color, dark: Color) -> None:
    """A one-pixel rim round a polygon, lit where the edge faces the right or the top, dark elsewhere."""
    n = len(poly)
    cx = sum(q[0] for q in poly) / n
    cy = sum(q[1] for q in poly) / n
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
        c = lit if mx - my * 0.7 > 0 else dark
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), c)


# ------------------------------------------------------------------------------------------------------------ pieces
def shadow_of_all(p: Pix, outline: list[tuple[float, float]]) -> None:
    """What the citadel throws on the world below: the island, the envelopes and the wheels, thrown down and to the left
    (the light is up and to the right). The shadow is dark violet with a dithered edge, like the original's dark pools."""
    big = [(x - 30, y + 40) for x, y in outline]
    shade_poly(p, big, 0.55, soft=False)
    core = [(x - 27 + (cx_ - x) * 0.06, y + 36) for x, y in outline for cx_ in (178,)]
    shade_poly(p, core, 1.0)
    for (u, v, h, rx, ry) in BALLOONS:
        cx, cy = pt3(u, v, h)
        poly = [(cx - 24 + rx * math.cos(a) * 0.9, cy + 38 + (ry + 3) * math.sin(a) * 0.9) for a in [i * math.pi / 8 for i in range(16)]]
        shade_poly(p, poly, 1.0)
    for sign in (-1, 1):
        c = pt3(0, sign * 66, 22)
        poly = [(c[0] - 26 + 15 * math.cos(a), c[1] + 42 + 18 * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
        shade_poly(p, poly, 0.8, soft=False)


def island_outline() -> list[tuple[float, float]]:
    """The island's top edge in the frame: a lens with lumpy sides."""
    rng = random.Random(21)
    pts_far, pts_near = [], []
    us = [-86 + i * 6 for i in range(0, 29)]
    for u in us:
        w = 32 * max(0.0, 1 - (u / 90) ** 2) ** 0.55 + 4
        bump = 3.5 * math.sin(u / 7.0) + rng.uniform(-1.5, 1.5)
        mid = 3 * math.sin(u / 26)
        pts_far.append(pt3(u, mid - w + bump * 0.5, 0))
        pts_near.append(pt3(u, mid + w * 0.92 + bump, 0))
    return pts_far + pts_near[::-1]


def draw_island(p: Pix, outline: list[tuple[float, float]]) -> None:
    m, x0, x1, y0, y1 = _mask(p, outline)
    # the cliff: below the lowest edge pixel of every column, deepest at the middle, with strata and a ragged bottom
    cx = pt3(-4, 0, 0)[0]
    for x in range(x0, x1 + 1):
        col = [y for y in range(y0, y1 + 1) if m.getpixel((x, y))]
        if not col:
            continue
        ybot = max(col)
        k = (x - cx) / ((x1 - x0) / 2)
        depth = round(5 + 21 * max(0.0, 1 - k * k) ** 0.8 + 5 * vn(x / 5.0, 0.5, 60) + 3 * math.sin(x / 4.0))
        for d in range(1, depth + 1):
            y = ybot + d
            f = d / depth
            strata = vn(x / 9.0, d / 3.0, 61)
            lit = 0.25 + 0.45 * clamp((x - x0) / (x1 - x0))
            facet = math.sin(x / 5.5 + 3 * vn(x / 14.0, 1.5, 64))
            v = 0.86 - 0.62 * f ** 0.85 + lit * 0.4 - 0.28 + 0.34 * (strata - 0.5) + 0.2 * facet * (1 - f * 0.5) + 0.14 * (noise(x, y, 3) - 0.5)
            if d == 1:
                v = 0.12                                    # shadow lip under the turf
            c = tone(ROCK, v, x, y, 2.0)
            if f > 0.55 and bay(x, y) < (f - 0.5) * 0.9:    # light bounced up from the sunlit world below
                c = mix(c, rgb("#d08040"), 0.45)
            if strata > 0.8 and d > 2:
                c = tone(ROCK, v - 0.3, x, y)               # a dark crack
            p.px(x, y, c)
        # roots and rock needles dangling below the cliff
        if noise(x, 7, 5) > 0.93:
            for d in range(depth + 1, depth + 3 + int(noise(x, 8, 5) * 7)):
                p.px(x, ybot + d, tone(ROCK, 0.25 + 0.1 * noise(x, d, 3), x, ybot + d))
    # turf
    def turf(x: int, y: int) -> Color | None:
        n = 0.5 * vn(x / 7.0, y / 5.0, 62) + 0.5 * vn(x / 2.5, y / 2.0, 63)
        edge = 0.0
        fu, fv = to_frame(x, y)
        field = noise(int(fu // 11), int(fv // 9), 4)
        r = GRASS if n > 0.38 else EARTH
        if field > 0.7:
            r = r_("#4a3216", "#7a521e", "#a8782c", "#d2a040", "#ecc46a")          # a stubble field
        elif field < 0.2:
            r = r_("#3a1a14", "#5e2a1e", "#8a3e28", "#b0583a", "#d27a4c")          # a ploughed one
        if abs(fv - 2 * math.sin(fu / 9)) < 1.3 and -60 < fu < 40:
            return tone(r_("#4a4038", "#76685a", "#a09078", "#c4b49a"), 0.45 + 0.4 * n, x, y)     # the paved way along the keep
        return tone(r, 0.2 + n * 0.65 + edge + 0.15 * (x - x0) / (x1 - x0), x, y, 2.0)

    fill(p, outline, turf)
    # the lit rim of the turf on the right, the dark rim on the left (a lip that overhangs the rock)
    n = len(outline)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        line(p, a, b, tone(GRASS, 0.75, round(a[0]), round(a[1])) if (a[1] < OY + 10 or a[0] > OX) else tone(EARTH, 0.1, round(a[0]), round(a[1])))


def tree(p: Pix, x: int, y: int, r: int, kind: int) -> None:
    ramps = (TILE, r_("#4a2a14", "#78441a", "#a8641e", "#d08a2c", "#eab04c"), GRASS, r_("#2a1818", "#4a2420", "#7a3a26", "#b0562c", "#d87a3a"))
    rr = ramps[kind % len(ramps)]
    p.ellipse(x - r + 1, y + 1, 2 * r, r + 1, tone(rr, 0.05, x, y))                       # shadow thrown to the left
    for yy in range(-r, r + 1):
        for xx in range(-r, r + 1):
            d = math.hypot(xx, yy * 1.05)
            if d <= r + 0.3:
                lit = 0.45 + 0.35 * (xx / r) - 0.3 * (yy / r) + 0.15 * (noise(x + xx, y + yy, 9) - 0.5)
                p.px(x + xx, y + yy, tone(rr, lit, x + xx, y + yy, 2.0))


def draw_trees(p: Pix, outline: list[tuple[float, float]]) -> None:
    m, x0, x1, y0, y1 = _mask(p, outline)
    rng = random.Random(33)
    keep_zone = [pt3(0, 0, 0), pt3(-42, 0, 0), pt3(38, 0, 0)]
    for _ in range(260):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1)
        if not m.getpixel((x, y)) or not m.getpixel((x, min(p.h - 1, y + 3))) or not m.getpixel((max(0, x - 3), y)):
            continue
        fu, fv = to_frame(x, y)
        if abs(fv) < 17 and -68 < fu < 56 or abs(fv) < 26 and abs(fu) < 28 or (fu < -52 and abs(fv) < 14):
            continue
        tree(p, x, y, rng.choice((2, 2, 3)), rng.randrange(4))


def tiles(r: Sequence[Color], lit: float, rows_px: float, tw: float = 3.0, seed: int = 0) -> Callable[[float, float, int, int], Color | None]:
    """Roof covering for a parallelogram: rows of shingles with a shadow line under each and staggered joints."""
    def fn(s: float, t: float, x: int, y: int) -> Color | None:
        row = t * rows_px
        ri = int(row)
        fr = row - ri
        col = s * 60 / tw + (ri % 2) * 0.5
        ci = int(col)
        v = lit + 0.18 * (noise(ci, ri, seed) - 0.5) - (0.28 if fr < 0.3 else 0.0) + 0.1 * fr
        if col - ci < 0.12:
            v -= 0.12
        return tone(r, v, x, y, 2.2)
    return fn


def masonry(r: Sequence[Color], lit: float, seed: int = 0, course: float = 3.0, bw: float = 4.0, length: float = 60) -> Callable[[float, float, int, int], Color | None]:
    def fn(s: float, t: float, x: int, y: int) -> Color | None:
        row = t * 12 / course * 3
        ri = int(row)
        col = s * length / bw + (ri % 2) * 0.5
        ci = int(col)
        v = lit + 0.25 * (noise(ci, ri, seed) - 0.5)
        if row - ri < 0.25:
            v -= 0.25
        elif col - ci < 0.12:
            v -= 0.18
        elif row - ri > 0.75:
            v += 0.06
        return tone(r, v, x, y, 2.0)
    return fn


def wall(lit: float, length: float, windows: Sequence[float], door: float | None, seed: int = 0, stone: float = 0.3) -> Callable[[float, float, int, int], Color | None]:
    """A hall wall: masonry plinth, timber-framed plaster above with lit windows and a warm door."""
    base = masonry(STONE, lit * 0.9, seed, length=length)

    def fn(s: float, t: float, x: int, y: int) -> Color | None:
        pos = s * length
        if t > 1 - stone:
            if door is not None and abs(pos - door) < 1.6 and t > 1 - stone + 0.1:
                return tone(LIGHT_WIN, 0.2 + 0.9 * (1 - t) * 2, x, y) if abs(pos - door) < 1.0 else tone(TIMBER, 0.2, x, y)
            return base(s, (t - (1 - stone)) / stone, x, y)
        tt = t / (1 - stone)
        post = (pos % 6.0) < 0.9 or tt < 0.14 or tt > 0.9
        for w in windows:
            if abs(pos - w) < 2.1 and 0.2 < tt < 0.82:
                warm = 0.3 + 0.6 * (1 - tt)
                return tone(LIGHT_WIN, warm * 2.2, x, y) if abs(pos - w) < 1.5 and 0.3 < tt < 0.74 else tone(TIMBER, 0.3, x, y)
        if post:
            return tone(TIMBER, 0.3 + lit * 0.4, x, y)
        return tone(PLAS, lit * 0.95 + 0.12 * (noise(int(pos), int(tt * 8), seed) - 0.5), x, y)
    return fn


def hall(p: Pix, u0: float, u1: float, vh: float, wallh: float, roof: float, seed: int, lit_windows: Sequence[float], roof_ramp: Sequence[Color], door: float | None = None, chimney: float | None = None, vc: float = 0.0) -> None:
    """A long timber-framed hall: plinth, plaster storey, gabled roof of tiles with a chimney."""
    length = u1 - u0
    # end wall (faces down-left, in shade), near wall (faces the viewer, lit)
    quad(p, pt3(u0, vc - vh, wallh), pt3(u0, vc + vh, wallh), pt3(u0, vc - vh, 0), wall(0.22, 2 * vh, [vh * 0.4 + vh], None, seed + 1))
    quad(p, pt3(u0, vc + vh, wallh), pt3(u1, vc + vh, wallh), pt3(u0, vc + vh, 0), wall(0.62, length, lit_windows, door, seed))
    o = 1.2
    rh = roof
    # far slope, then the gable end, then near slope
    quad(p, pt3(u0 - o, vc - vh - o, wallh), pt3(u1 + o, vc - vh - o, wallh), pt3(u0 - o, vc, wallh + rh), tiles(roof_ramp, 0.34, max(3, rh * 0.85 / 2.4), seed=seed))
    gable = [pt3(u0 - 0.3, vc - vh, wallh), pt3(u0 - 0.3, vc + vh, wallh), pt3(u0 - 0.3, vc, wallh + rh)]
    fill(p, gable, lambda x, y: tone(PLAS, 0.28 + 0.1 * noise(x, y, seed), x, y))
    quad(p, pt3(u0 - o, vc + vh + o, wallh), pt3(u1 + o, vc + vh + o, wallh), pt3(u0 - o, vc, wallh + rh), tiles(roof_ramp, 0.66, max(3, rh * 0.85 / 2.4), seed=seed + 2))
    # ridge cap and eave lines
    line(p, pt3(u0 - o, vc, wallh + rh), pt3(u1 + o, vc, wallh + rh), tone(roof_ramp, 0.9, 0, 0))
    line(p, pt3(u0 - o, vc + vh + o, wallh), pt3(u1 + o, vc + vh + o, wallh), tone(roof_ramp, 0.08, 0, 0))
    line(p, pt3(u0 - o, vc - vh - o, wallh), pt3(u0 - o, vc + vh + o, wallh), tone(roof_ramp, 0.12, 0, 0))
    line(p, pt3(u0 - 0.3, vc - vh, wallh), pt3(u0 - 0.3, vc, wallh + rh), tone(TIMBER, 0.7, 0, 0))
    line(p, pt3(u0 - 0.3, vc + vh, wallh), pt3(u0 - 0.3, vc, wallh + rh), tone(TIMBER, 0.3, 0, 0))
    if chimney is not None:
        cx, cy = pt3(chimney, vc + 0.5, wallh + rh * 0.55)
        p.rect(round(cx) - 1, round(cy) - 6, 3, 7, tone(STONE, 0.5, 0, 0))
        p.rect(round(cx) + 1, round(cy) - 6, 1, 7, tone(STONE, 0.78, 0, 0))
        p.rect(round(cx) - 2, round(cy) - 7, 5, 1, tone(STONE, 0.3, 0, 0))
        smoke(p, round(cx), round(cy) - 8, seed)
    # light spilling from the windows onto the ground in front
    for w in lit_windows:
        gx, gy = pt3(u0 + w, vc + vh + 3, 0)
        for dy in range(-2, 3):
            for dx in range(-4, 5):
                if abs(dx) + abs(dy) * 2 < 6 and bay(round(gx) + dx, round(gy) + dy) < 0.3:
                    p.px(round(gx) + dx, round(gy) + dy, mix(p.get(round(gx) + dx, round(gy) + dy)[:3], rgb("#f0a040"), 0.4))


def smoke(p: Pix, x: int, y: int, seed: int) -> None:
    """A thread of chimney smoke drifting to the left, away from the light (the wind blows from the right)."""
    for k in range(18):
        xx, yy = x - k * 1.3 + 0.6 * math.sin(k / 2), y - k * 0.45
        w = 1 + k // 6
        for dx in range(w):
            if bay(round(xx) + dx, round(yy)) < 0.8 - k * 0.04:
                c = mix(rgb("#8a7a88"), rgb("#4a4058"), k / 18)
                over = p.get(round(xx) + dx, round(yy))[:3]
                p.px(round(xx) + dx, round(yy), mix(over, c, 0.7))


def cyl_stack(p: Pix, u: float, v: float, h0: float, h1: float, r0: float, r1: float,
              fn: Callable[[float, float, int, int, float], Color | None]) -> None:
    """A tower or a cone drawn as a stack of one-pixel slices; fn(tx, th, x, y, hh) with tx -1..1 across and th 0..1 up."""
    steps = max(1, round((h1 - h0) / 0.55))
    for i in range(steps + 1):
        th = i / steps
        hh = h0 + (h1 - h0) * th
        r = r0 + (r1 - r0) * th
        poly = circ3(u, v, hh, r)
        cx, cy = pt3(u, v, hh)
        xs = [q[0] for q in poly]
        rx = max(1.0, (max(xs) - min(xs)) / 2)
        fill(p, poly, lambda x, y, rx=rx, cx=cx, th=th, hh=hh: fn((x + 0.5 - cx) / rx, th, x, y, hh))


def tower_fn(r: Sequence[Color], seed: int, windows: Sequence[float] = (), bw: float = 4.0, crenel: bool = False) -> Callable[[float, float, int, int, float], Color | None]:
    def fn(tx: float, th: float, x: int, y: int, hh: float) -> Color | None:
        lit = 0.2 + 0.5 * (tx + 1) / 2 + 0.2 * math.cos(tx * 1.6 - 0.7)
        ang = math.asin(max(-1.0, min(1.0, tx)))
        row = hh / 3.2
        ri = int(row)
        col = ang * 5.0 + (ri % 2) * 0.5 + 40
        ci = int(col)
        v = lit + 0.22 * (noise(ci, ri, seed) - 0.5)
        if row - ri < 0.22:
            v -= 0.2
        elif col - ci < 0.12:
            v -= 0.14
        for wh in windows:
            if abs(hh - wh) < 1.4 and abs(tx - 0.25) < 0.17:
                return tone(LIGHT_WIN, 1.3, x, y)
            if abs(hh - wh) < 1.8 and abs(tx - 0.25) < 0.26:
                return tone(TIMBER, 0.2, x, y)
        return tone(r, v, x, y, 2.0)
    return fn


def cone_fn(r: Sequence[Color], seed: int) -> Callable[[float, float, int, int, float], Color | None]:
    def fn(tx: float, th: float, x: int, y: int, hh: float) -> Color | None:
        lit = 0.28 + 0.5 * (tx + 1) / 2 + 0.12 * (1 - th)
        row = hh / 2.2
        ri = int(row)
        col = tx * 4 + (ri % 2) * 0.5 + 40
        v = lit + 0.12 * (noise(int(col), ri, seed) - 0.5) - (0.2 if row - ri < 0.3 else 0.0)
        return tone(r, v, x, y, 2.2)
    return fn


# ----------------------------------------------------------------------------------------------------- the dock ring
def dock_ring(p: Pix, u: float, v: float, hr: float, ro: float, ri: float) -> None:
    """The wooden gallery round the hub: radial deck planks, a thick rim beam, rail posts with lanterns, and braces
    that run down to the tower so it visibly hangs from something."""
    # braces under the near side (seen below the rim)
    for ang in (-0.5, 0.45, 1.2, 1.95, 2.7):
        a = pt3(u + (ro - 1) * math.cos(ang), v + (ro - 1) * math.sin(ang), hr - 3)
        b = pt3(u + 8 * math.cos(ang), v + 8 * math.sin(ang), hr - 14)
        if a[1] > pt3(u, v, hr)[1]:
            line(p, a, b, tone(TIMBER, 0.2, 0, 0))
            line(p, (a[0] + 1, a[1]), (b[0] + 1, b[1]), tone(TIMBER, 0.55, 0, 0))
    # outer fascia (a thick beam round the rim), stacked slices
    for k in range(4, -1, -1):
        poly = circ3(u, v, hr - 3 + k * 0.7, ro)
        fill(p, poly, lambda x, y, k=k: tone(TIMBER, 0.12 + 0.12 * (4 - k) + 0.3 * (x > OX + 4) * 0.6 + 0.12 * noise(x // 3, y, 2), x, y))
    deck = circ3(u, v, hr, ro)
    cx, cy = pt3(u, v, hr)

    def planks(x: int, y: int) -> Color | None:
        dx, dy = x + 0.5 - cx, (y + 0.5 - cy) / 0.78
        ang = math.atan2(dy, dx)
        rad = math.hypot(dx, dy)
        pi = int((ang + math.pi) / (2 * math.pi) * 44)
        seam = abs(((ang + math.pi) / (2 * math.pi) * 44) % 1 - 0.5) > 0.44
        ring = (rad / ro)
        v = 0.62 + 0.25 * (dx / ro) - 0.15 * (dy / ro) + 0.3 * (noise(pi, 1, 4) - 0.5)
        if seam:
            v -= 0.22
        if ring > 0.9:
            v += 0.18                                   # the lit edge of the rim beam
        if 0.62 < ring < 0.66:
            v -= 0.12                                   # a hoop beam round the middle
        return tone(DECK, v, x, y, 2.0)

    fill(p, deck, planks)
    # shadow of the tower on the deck, thrown to the left
    shade_poly(p, [(cx - 12, cy + 2), (cx - 4, cy - 6), (cx + 6, cy + 5), (cx - 6, cy + 10)], 0.7, only_world=False)
    # the hole round the tower
    hole = circ3(u, v, hr, ri)
    fill(p, hole, lambda x, y: tone(TIMBER, 0.05 + 0.08 * noise(x, y, 7), x, y))
    # rail: posts every 24 degrees with a lantern on some, and a rope rail between them
    posts: list[tuple[float, float, float, float]] = []
    for k in range(15):
        a = 2 * math.pi * k / 15 + 0.2
        base = pt3(u + ro * math.cos(a), v + ro * math.sin(a), hr)
        top = pt3(u + ro * math.cos(a), v + ro * math.sin(a), hr + 4)
        posts.append((base[0], base[1], top[0], top[1]))
    order = sorted(range(len(posts)), key=lambda i: posts[i][1])
    for i in order:
        bx, by, tx_, ty_ = posts[i]
        near = by > cy
        if near:
            continue
        line(p, (bx, by), (tx_, ty_), tone(TIMBER, 0.5, 0, 0))
    for i in range(len(posts)):
        j = (i + 1) % len(posts)
        if posts[i][1] <= cy and posts[j][1] <= cy:
            line(p, (posts[i][2], posts[i][3]), (posts[j][2], posts[j][3]), tone(ROPE, 0.35, 0, 0))


def dock_ring_front(p: Pix, u: float, v: float, hr: float, ro: float) -> None:
    """The near half of the rail, drawn after the tower, with its lanterns."""
    cy = pt3(u, v, hr)[1]
    posts = []
    for k in range(15):
        a = 2 * math.pi * k / 15 + 0.2
        posts.append((pt3(u + ro * math.cos(a), v + ro * math.sin(a), hr), pt3(u + ro * math.cos(a), v + ro * math.sin(a), hr + 4)))
    for i, (b, t) in enumerate(posts):
        if b[1] > cy:
            line(p, b, t, tone(TIMBER, 0.55, round(b[0]), 0))
            p.px(round(t[0]), round(t[1]) - 1, LIGHT_WIN[2] if i % 3 == 0 else tone(BRASS, 0.8, 0, 0))
            if i % 3 == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -2)):
                    p.px(round(t[0]) + dx, round(t[1]) - 1 + dy, mix(p.get(round(t[0]) + dx, round(t[1]) - 1 + dy)[:3], rgb("#ffa040"), 0.6))
    for i in range(len(posts)):
        j = (i + 1) % len(posts)
        if posts[i][0][1] > cy and posts[j][0][1] > cy:
            line(p, posts[i][1], posts[j][1], tone(ROPE, 0.5, 0, 0))


# --------------------------------------------------------------------------------------------------------- airships
def airship(p: Pix, cx: float, cy: float, ang: float, length: float, seed: int, stripe: Sequence[Color]) -> None:
    """A small moored airship: a clinker hull slung under a canvas envelope, lit on the right."""
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(a: float, b: float) -> tuple[float, float]:
        return cx + a * ca - b * sa, cy + a * sa + b * ca

    hull = [rot(a, b) for a, b in ((-length * 0.5, 0), (-length * 0.3, 2.4), (length * 0.3, 2.6), (length * 0.55, 0.2), (length * 0.3, -2.2), (-length * 0.3, -2.4))]
    fill(p, hull, lambda x, y: tone(TIMBER, 0.45 + 0.25 * ((x - cx) / length) + (0.18 if (y + x // 2) % 3 == 0 else 0), x, y))
    edge_lit(p, hull, tone(TIMBER, 0.9, 0, 0), tone(TIMBER, 0.05, 0, 0))
    ex, ey = rot(0, -3.8)
    env = [rot(a, b) for a, b in ((-length * 0.55, -3.8), (-length * 0.3, -6.2), (length * 0.2, -6.4), (length * 0.6, -3.8), (length * 0.2, -1.6), (-length * 0.3, -1.6))]
    shade_poly(p, [(x - 6, y + 9) for x, y in env], 0.6, only_world=False)

    def cloth(x: int, y: int) -> Color | None:
        t = ((x - ex) * ca + (y - ey) * sa) / length
        gore = int((t + 0.6) * 9)
        light = 0.42 + 0.3 * (x - ex) / length - 0.1 * (y - ey) / 3
        return tone(stripe if gore % 2 else CANVAS, light, x, y, 2.0)

    fill(p, env, cloth)
    edge_lit(p, env, tone(CANVAS, 1.0, 0, 0), tone(CANVAS, 0.0, 0, 0))
    for off in (-0.25, 0.1, 0.35):                      # rigging from envelope to hull
        line(p, rot(length * off, -2.0), rot(length * off * 0.8, 0.5), tone(ROPE, 0.3, 0, 0))
    fx, fy = rot(-length * 0.5, 0)
    p.px(round(fx), round(fy), LIGHT_WIN[1])


# ------------------------------------------------------------------------------------------------ wind-wheel and rigging
def windwheel(p: Pix, v: float, hc: float, radius: float, phase: float, side: int, cloth_ramp: Sequence[Color], hub_front: bool) -> None:
    """A sail wheel on an outrigger: the beam is its axle; the wheel stands in the (u, h) plane. Four blades of canvas
    on lattice spars, with a brass hub."""
    cu = 0.0
    c = pt3(cu, v, hc)
    for k in range(4):
        ph = phase + k * math.pi / 2
        dh, dv = math.cos(ph), math.sin(ph)           # radial direction in the (u, h) plane
        nh, nv = -dv, dh
        a = (cu + dh * 3.5, hc + dv * 3.5)
        b = (cu + dh * radius, hc + dv * radius)
        d = (a[0] + nh * 9.5, a[1] + nv * 9.5)
        A, B, D = pt3(a[0], v, a[1]), pt3(b[0], v, b[1]), pt3(d[0], v, d[1])

        def fn(s: float, t: float, x: int, y: int, k=k) -> Color | None:
            if t < 0.1:
                return tone(TIMBER, 0.55 - 0.3 * t * 4 + (0.2 if (int(s * 14) % 2) else 0), x, y)       # the spar
            rib = (s * 7.0) % 1 < 0.14
            patch = noise(int(s * 4), k, 7) > 0.78
            lit = 0.5 + 0.28 * (x - c[0]) / radius - 0.12 * t + 0.1 * (noise(x // 2, y // 2, k) - 0.5)
            if rib:
                lit -= 0.25
            r = WINE if patch or (int(s * 4) % 2 and k % 2) else cloth_ramp
            return tone(r, lit + 0.12, x, y, 2.0)

        quad(p, A, B, D, fn)
        # outer batten
        line(p, B, pt3(b[0] + nh * 9.5, v, b[1] + nv * 9.5), tone(TIMBER, 0.3, 0, 0))
        # a brace from the spar tip back to the hub ring (rope)
    ring = [pt3(cu + 5 * math.cos(a), v, hc + 5 * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
    fill(p, ring, lambda x, y: tone(IRON, 0.3 + 0.4 * (x - c[0] + 5) / 10, x, y))
    if hub_front:
        hx, hy = round(c[0]), round(c[1])
        p.ellipse(hx - 2, hy - 2, 5, 5, tone(BRASS, 0.35, hx, hy))
        p.ellipse(hx - 1, hy - 2, 3, 3, tone(BRASS, 0.75, hx, hy))
        p.px(hx + 1, hy - 1, tone(BRASS, 1.0, hx, hy))


def beam(p: Pix, a: tuple[float, float], b: tuple[float, float], w: int, ramp: Sequence[Color] = TIMBER) -> None:
    """A timber of w px: dark underside, mid body, lit upper edge."""
    for i, k in enumerate(range(-(w // 2), w - w // 2)):
        c = tone(ramp, 0.2 if i == w - 1 else 0.85 if i == 0 else 0.5, 0, 0)
        line(p, (a[0], a[1] + k), (b[0], b[1] + k), c)


def pennant(p: Pix, x: float, y: float, length: float, c: Sequence[Color], seed: int) -> None:
    """A swallow-tailed pennant streaming to the left, rippling, with a lit upper half."""
    for i in range(int(length)):
        t = i / length
        yy = y + 0.9 * math.sin(i / 2.2 + seed) + t * 1.2
        half = 2.4 * (1 - t) + 0.4
        for j in range(-round(half), round(half) + 1):
            if t > 0.8 and abs(j) < 1:
                continue
            tt = 0.55 + 0.35 * (j < 0) - 0.15 * t + (0.1 if i % 4 < 2 else 0)
            p.px(round(x - i), round(yy + j), tone(c, tt, round(x - i), round(yy + j), 2.0))


def mast(p: Pix, u: float, v: float, h0: float, h1: float, flag: Sequence[Color] | None, seed: int, stays: bool = True) -> None:
    a, b = pt3(u, v, h0), pt3(u, v, h1)
    # shade of the mast on the roof is a short dark streak down-left
    line(p, (a[0] - 1, a[1]), (b[0] - 1, b[1]), tone(TIMBER, 0.15, 0, 0))
    line(p, a, b, tone(TIMBER, 0.5, 0, 0))
    line(p, (a[0] + 1, a[1]), (b[0] + 1, b[1]), tone(TIMBER, 0.95, 0, 0))
    # yard arm and a gilded finial
    ya = pt3(u, v, h0 + (h1 - h0) * 0.8)
    line(p, (ya[0] - 4, ya[1] - 2), (ya[0] + 4, ya[1] + 2), tone(TIMBER, 0.45, 0, 0))
    p.px(round(b[0]), round(b[1]) - 1, tone(BRASS, 1.0, 0, 0))
    p.px(round(b[0]), round(b[1]) - 2, tone(BRASS, 0.7, 0, 0))
    if stays:
        for du, dv in ((-8, 4), (6, 7), (5, -6)):
            e = pt3(u + du, v + dv, h0)
            line(p, (b[0], b[1] + 3), e, tone(ROPE, 0.25, 0, 0))
    if flag:
        pennant(p, b[0] - 1, b[1] + 1, 12 + seed % 3 * 2, flag, seed)


BLADDERS: Final = (          # u, v, h, half length, half width: the lift-envelopes, long axes along the keep
    (-92, 6, 20, 16, 8), (-46, -46, 22, 15, 8), (-44, 47, 24, 15, 8), (44, 46, 22, 14, 7.5), (88, -6, 14, 10, 6))
BALLOONS: Final = tuple((u, v, h, la, lb) for u, v, h, la, lb in BLADDERS)


def bladder(p: Pix, u: float, v: float, h: float, la: float, lb: float, seed: int,
            anchors: Sequence[tuple[float, float, float]], palette: Sequence[Color]) -> None:
    """A lift-envelope: a long gas bag of oiled canvas in gores, with hemp patches, a net of cords, a leather nose cap and
    mooring ropes to the island's rim. It lies with its axis along the keep, lit on the right."""
    cx, cy = pt3(u, v, h)
    ang = math.atan2(UY, UX)
    ca, sa = math.cos(ang), math.sin(ang)
    la_, lb_ = la * 0.95, lb * 1.1
    for au, av, ah in anchors:
        e = pt3(au, av, ah)
        a0 = (cx + (e[0] - cx) * 0.2, cy + (e[1] - cy) * 0.2 + 2)
        n = 10
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            sag = lambda t: 3.5 * math.sin(math.pi * t)
            line(p, (a0[0] + (e[0] - a0[0]) * t0, a0[1] + (e[1] - a0[1]) * t0 + sag(t0)), (a0[0] + (e[0] - a0[0]) * t1, a0[1] + (e[1] - a0[1]) * t1 + sag(t1)), tone(ROPE, 0.35, 0, 0))
        p.rect(round(e[0]) - 1, round(e[1]) - 1, 3, 2, tone(IRON, 0.7, 0, 0))

    def fn(x: int, y: int) -> Color | None:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        a, b = (dx * ca + dy * sa) / la_, (-dx * sa + dy * ca) / lb_
        taper = 1 - 0.28 * max(0.0, -a) ** 2          # fuller at the nose (toward the upper right), slimmer at the tail
        b = b / taper
        d2 = a * a + b * b
        if d2 > 1:
            return None
        nz = math.sqrt(1 - d2)
        nxs, nys = a * ca - b * sa, a * sa + b * ca
        light = 0.52 * nxs - 0.45 * nys + 0.5 * nz
        ang_b = math.asin(max(-1.0, min(1.0, b)))
        gp = (ang_b / math.pi + 0.5) * 8
        gore = int(gp)
        seam = abs(gp % 1 - 0.5) > 0.45
        base = palette if gore % 2 else CANVAS
        v_ = 0.08 + 0.9 * clamp(light) ** 1.05 + 0.08 * (noise(x // 2, y // 2, seed) - 0.5)
        if seam:
            v_ -= 0.2
        ring = (a + 1) * 5.0
        if abs(ring % 1 - 0.5) > 0.46:
            v_ -= 0.16                                  # a hoop cord round the bag
        if noise(gore, int(ring), seed + 3) > 0.84:
            base, v_ = ROPE, v_ * 0.85                  # a patch of hempen cloth
        if d2 > 0.84:
            v_ += 0.07 if light > 0.45 else -0.12
        return tone(base, v_, x, y, 2.0)

    poly = []
    for i in range(36):
        t = i * math.pi / 18
        a, b = math.cos(t), math.sin(t)
        b *= 1 - 0.28 * max(0.0, -a) ** 2
        poly.append((cx + (a * la_) * ca - (b * lb_) * sa, cy + (a * la_) * sa + (b * lb_) * ca))
    fill(p, poly, fn)
    edge_lit(p, poly, tone(CANVAS, 1.0, 0, 0), tone(WINE, 0.0, 0, 0))
    nx_, ny_ = cx + la_ * ca, cy + la_ * sa                    # the leather nose cap
    p.rect(round(nx_) - 2, round(ny_) - 1, 3, 3, tone(TIMBER, 0.5, 0, 0))
    p.px(round(nx_), round(ny_) - 1, tone(BRASS, 0.9, 0, 0))


def cask(p: Pix, cx: int, cy: int, w: int, h: int, seed: int) -> None:
    """A small hanging cask: staves in two tones, two iron hoops with a lit edge, a bung, a dark foot."""
    p.ellipse(cx - w // 2 + 1, cy + h - 2, w, 3, tone(TIMBER, 0.0, 0, 0))
    for yy in range(h):
        k = 1 - abs(yy - h / 2) / (h / 2)
        half = w / 2 * (0.78 + 0.22 * k)
        for xx in range(-int(half), int(half) + 1):
            f = (xx + half) / (2 * half)
            stave = int((xx + half) / 1.6)
            v = 0.15 + 0.75 * f ** 0.9 + 0.1 * (noise(stave, seed, 3) - 0.5)
            if abs(((xx + half) / 1.6) % 1 - 0.0) < 0.12:
                v -= 0.15
            p.px(cx + xx, cy + yy, tone(DECK, v, cx + xx, cy + yy, 2.0))
    for yy in (1, h - 2):
        for xx in range(-w // 2, w // 2 + 1):
            if p.get(cx + xx, cy + yy)[3]:
                p.px(cx + xx, cy + yy, tone(IRON, 0.85 if xx > 0 else 0.2, 0, 0))
    p.px(cx + 1, cy + h // 2, tone(BRASS, 0.8, 0, 0))


def hang(p: Pix, rim: tuple[float, float], drop: int, seed: int, w: int = 7, h: int = 8) -> None:
    """A cask on a chain from a bracket on the island's rim, swinging a little to the left."""
    x, y = rim
    p.rect(round(x) - 1, round(y) - 1, 3, 2, tone(IRON, 0.7, 0, 0))
    ex = x - 3
    for i in range(drop):
        t = i / drop
        xx, yy = round(x + (ex - x) * t * t), round(y + i)
        p.px(xx, yy, tone(IRON, 0.75 if i % 2 else 0.35, 0, 0))
        if i % 2 == 0:
            p.px(xx + 1, yy, tone(IRON, 0.25, 0, 0))
    cask(p, round(ex), round(y + drop + 1), w, h, seed)


def beacon(p: Pix, u: float, v: float) -> None:
    """The beacon tower: a square stone tower with a pyramid roof and an iron fire basket at the top."""
    s, hgt = 6.0, 30.0
    quad(p, pt3(u - s, v - s, hgt), pt3(u - s, v + s, hgt), pt3(u - s, v - s, 0), masonry(STONE, 0.28, 9, length=22))
    quad(p, pt3(u - s, v + s, hgt), pt3(u + s, v + s, hgt), pt3(u - s, v + s, 0), wall(0.66, 2 * s, [s * 0.7], None, 4, stone=1.0))
    top = pt3(u, v, hgt + 14)
    for sign, lit in ((-1, 0.32), (1, 0.66)):
        quad(p, pt3(u - s - 1, v + sign * (s + 1), hgt), pt3(u + s + 1, v + sign * (s + 1), hgt), pt3(u - s - 1, v, hgt + 14), tiles(TILE, lit + 0.1, 6, seed=3 if sign < 0 else 4))
    quad(p, pt3(u - s - 1, v - s - 1, hgt), pt3(u - s - 1, v + s + 1, hgt), pt3(u, v, hgt + 14), lambda s_, t, x, y: tone(TILE, 0.15 + 0.1 * noise(x, y, 1), x, y))
    # lit slit windows
    for hh in (10, 20):
        a = pt3(u - s + 1.5, v + s, hh)
        p.rect(round(a[0]), round(a[1]), 1, 3, LIGHT_WIN[1])
    # fire basket on a pole above the roof
    b = pt3(u, v, hgt + 14)
    line(p, b, (b[0], b[1] - 7), tone(TIMBER, 0.4, 0, 0))
    bx, by = round(b[0]), round(b[1]) - 8
    p.rect(bx - 2, by + 1, 5, 2, tone(IRON, 0.6, 0, 0))
    for dx, dy, c in ((0, -1, LIGHT_WIN[2]), (0, -2, LIGHT_WIN[1]), (-1, -1, LIGHT_WIN[1]), (1, -1, LIGHT_WIN[0]), (0, -3, LIGHT_WIN[0])):
        p.px(bx + dx, by + dy, c)
    for rr in (5, 3):
        for yy in range(-rr, rr + 1):
            for xx in range(-rr, rr + 1):
                if math.hypot(xx, yy) <= rr and bay(bx + xx, by + yy) < 0.28 * (1 - math.hypot(xx, yy) / (rr + 1)) * 2:
                    p.px(bx + xx, by + yy, mix(p.get(bx + xx, by + yy)[:3], rgb("#ffb050"), 0.55))


def farm(p: Pix) -> None:
    """The lower-left end: a barn with a hay loft, haystacks and a small windmill's worth of sheds."""
    hall(p, -78, -62, 6, 9, 6, 41, [4, 11], TILE, door=8, chimney=None)
    for (u, v) in ((-56, 14), (-50, -18), (-46, 18)):
        x, y = pt3(u, v, 0)
        x, y = round(x), round(y)
        for yy in range(-4, 1):                                   # haystack: a lit golden dome with a shadow to the left
            half = round(3.2 * math.sqrt(max(0.0, 1 - (yy / 4.5) ** 2)))
            for xx in range(-half, half + 1):
                p.px(x + xx, y + yy, tone(GRASS, 0.55 + 0.4 * (xx / 3) + 0.2 * (yy / 4), x + xx, y + yy))
                if xx > 0 and yy < 0:
                    p.px(x + xx, y + yy, tone(r_("#a8741c", "#d49a30", "#f0c458"), 0.55 + 0.4 * (xx / 3), x + xx, y + yy))
        p.px(x - 4, y + 1, tone(EARTH, 0.1, 0, 0))
        p.px(x - 3, y + 1, tone(EARTH, 0.1, 0, 0))


def to_frame(x: float, y: float) -> tuple[float, float]:
    """The island's (u, v) of a screen point on its top surface."""
    dx, dy = x - OX, y - OY
    det = UX * VY - UY * VX
    return (dx * VY - dy * VX) / det, (UX * dy - UY * dx) / det


def draw_citadel(p: Pix) -> None:
    outline = island_outline()
    shadow_of_all(p, outline)
    draw_island(p, outline)
    draw_trees(p, outline)
    for (u, v, drop, w, h, s) in ((-60, 33, 11, 7, 8, 1), (-24, 36, 15, 8, 9, 2), (14, 41, 9, 7, 8, 3), (52, 30, 12, 7, 8, 4)):
        rim = pt3(u, v, -2)
        hang(p, (rim[0], rim[1] + 2), drop, s, w, h)
    teal = r_("#1c3a40", "#2e6a68", "#4a9a8a", "#86c4a8")
    blue = r_("#1c2a40", "#2e4a68", "#4a729a", "#86a4c4")
    # the far wheel and its far envelope
    beam(p, pt3(0, -22, 20), pt3(0, -68, 20), 3)
    windwheel(p, -68, 22, 19, 0.5, -1, CANVAS, False)
    beam(p, pt3(0, -68, 20), pt3(0, -71, 22), 3, BRASS)
    bladder(p, -46, -46, 22, 15, 8, 2, [(-58, -34, 0), (-40, -30, 0), (-48, -32, 0)], WINE)
    # far cottages, then the beacon, its masts and the halls
    hall(p, -56, -45, 5.5, 8, 6, 51, [3, 8], TILE, vc=-20, chimney=-50)
    hall(p, 34, 44, 5, 8, 6, 52, [4], TILE, vc=-20)
    beacon(p, 62, -3)
    mast(p, 42, -2, 14, 62, WINE, 1)
    mast(p, 74, 7, 8, 52, teal, 2)
    mast(p, 50, 8, 12, 46, r_("#6b4c1c", "#a07a2c", "#d0a847", "#f0d27a"), 3, stays=False)
    hall(p, 24, 52, 8, 13, 10, 11, [6, 11, 17, 23], SLATE, door=None, chimney=40)
    hall(p, -64, -22, 9, 14, 11, 21, [5, 11, 18, 25, 32, 38], TILE, door=14, chimney=-52)
    farm(p)
    # the dock ring and the hub tower
    dock_ring(p, 0, 0, 14, 23, 12)
    cyl_stack(p, 0, 0, 14, 34, 8.6, 8.2, tower_fn(STONE, 5, windows=(22, 29)))
    cyl_stack(p, 0, 0, 34, 35.6, 10.4, 10.4, tower_fn(TIMBER, 6))
    cyl_stack(p, 0, 0, 35.6, 50, 10.8, 0.6, cone_fn(VERD, 7))
    top = pt3(0, 0, 50)
    line(p, top, (top[0], top[1] - 6), tone(TIMBER, 0.5, 0, 0))
    pennant(p, top[0], top[1] - 6, 12, WINE, 5)
    p.px(round(top[0]), round(top[1]) - 7, tone(BRASS, 1.0, 0, 0))
    dock_ring_front(p, 0, 0, 14, 22)
    airship(p, *pt3(-2, 30, 22), -0.62, 20, 3, WINE)
    airship(p, *pt3(26, -20, 22), 0.4, 14, 4, teal)
    # the near wheel, on the viewer's side
    beam(p, pt3(0, 22, 20), pt3(0, 64, 20), 3)
    windwheel(p, 66, 22, 19, 0.75, 1, CANVAS, True)
    # the envelopes at the island's near edge and the ends
    bladder(p, -92, 6, 20, 16, 8, 1, [(-84, 8, 0), (-76, 16, 0), (-80, 2, 0)], WINE)
    bladder(p, -44, 47, 24, 15, 8, 4, [(-54, 33, 0), (-34, 36, 0), (-44, 34, 0)], blue)
    bladder(p, 44, 46, 22, 14, 7.5, 3, [(36, 34, 0), (52, 30, 0), (44, 33, 0)], teal)
    bladder(p, 88, -6, 14, 10, 6, 5, [(78, -4, 0), (82, 6, 0)], WINE)
