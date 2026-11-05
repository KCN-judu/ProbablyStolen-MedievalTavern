"""The main-menu picture, drawn after the composition of the game's own: a vast autumn world curving across the lower
right, seen from a great height; an aurora and cloud bank hugging its limb under a deep night sky; a moon rising behind
the limb; and, at the left centre, a floating citadel moored over the world (see mnu_planet_keep.py).

Layout of the original that is kept: the limb is a big circle (centre far below the frame) rising from the lower left to
the upper right; the night side is a ragged dark mass at the lower right; the upper left is dark; the citadel hangs at
the left centre, angled along the same diagonal; a bright glint sits on the upper right limb; the credit line is at the
bottom, left of centre. `scene(credit)` draws both files, so they differ only by the credit line.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import Final

from PIL import Image

from fxkit import clamp, noise, pick_tone, vnoise
from pix import BAYER, Color, Pix, mix, rgb

W, H = 640, 320
CX, CY, R = 400.0, 602.0, 525.0                  # the world's disc: only its upper rim is in the frame
MOON: Final = (585, 101, 16)                      # centre and radius of the moon behind the limb


def ramp(*hexes: str) -> list[Color]:
    return [rgb(h) for h in hexes]


# ------------------------------------------------------------------------------------------ palettes (dark to light)
GOLD = ramp("#6a3a22", "#8c4e2a", "#b86a30", "#d98a3c", "#f0ac52", "#fbd27e")
RUSTY = ramp("#4a2220", "#6e3228", "#924234", "#b45a3a", "#d27a48", "#e69a60")
OLIVE = ramp("#2e3220", "#464a28", "#646234", "#868040", "#aaa056", "#cdc272")
STUBBLE = ramp("#6e4a34", "#8e6844", "#b08a58", "#cfa86c", "#e6c888")
EARTH = ramp("#3a2218", "#583224", "#7a4630", "#9c5e3c", "#be7a4c")
WOOD_RED = ramp("#1e1418", "#321c1a", "#4e281e", "#6e3822", "#8e4a28", "#b0602e")
WOOD_GRN = ramp("#16221a", "#26361f", "#3e5026", "#5e6c30", "#8a8a3c")
MAPLE = ramp("#4a1c1c", "#6e2a24", "#923a28", "#b8532e", "#d8743a")
WATER = ramp("#101c34", "#1c3052", "#2e4e76", "#4a7a9c", "#86b4c0")
NIGHT_MASS = ramp("#0c0818", "#150e26", "#20143a", "#2e1c4a", "#44305e")
SKY_BG = ramp("#14111a", "#1a1624", "#221c34", "#2c2444")
BAND_BLUE = ramp("#1c2040", "#2a3260", "#3e4a82", "#5a6ea0", "#86a0c0", "#b8d0e0")
BAND_VIOLET = ramp("#241c3c", "#382c56", "#554374", "#7a6490", "#a48ab0", "#cfb4cc")
BAND_MAUVE = ramp("#2c2838", "#443f54", "#625b70", "#867c8c", "#aaa0a4", "#d0c4c0")
BAND_TEAL = ramp("#14262c", "#1f4046", "#2e6a68", "#4a9a8a", "#86c4a8", "#c0e4c4")
CLOUD_DAY = ramp("#9a5a4a", "#bc7a5a", "#dca078", "#f2c898", "#fce4b8")
BAND_ROSE = ramp("#3a1d36", "#6a2f50", "#a04a62", "#d07a7c", "#eeb0a0", "#fbdcc4")
MOON_R = ramp("#6a5a78", "#8c7a92", "#b8a4aa", "#dcc8c0", "#f4e6d4")
STONE_PALE = rgb("#e8cfa0")
STONE_DARK = rgb("#7a5a4e")
ROOF_RED = rgb("#b04030")
HAZE_DAY = rgb("#e8a060")
HAZE_DUSK = rgb("#7a5078")


def bay(x: int, y: int) -> float:
    return (BAYER[y & 3][x & 3] + 0.5) / 16


def vn(x: float, y: float, s: int) -> float:
    return vnoise(x, y, s)


def lum(c: Color) -> float:
    return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255


def at(r: Sequence[Color], v: float, x: int, y: int, crisp: float = 2.4) -> Color:
    """A colour of a ramp for v in 0..1, dithered only at the joints."""
    return pick_tone(r, clamp(v) * (len(r) - 1), x, y, crisp)


# ------------------------------------------------------------------------------------------------------------ sky
def arc(x: int, y: int) -> tuple[float, float, float]:
    """Height above the limb, distance along it, and the normalised x, for a pixel outside the world."""
    d = math.hypot(x - CX, y - CY)
    return d - R, math.atan2(x - CX, CY - y) * R, x / W


def _stars() -> list[tuple[int, int, Color, int]]:
    rng = random.Random(77)
    out: list[tuple[int, int, Color, int]] = []
    pale = (rgb("#c8c4d8"), rgb("#e4dcd0"), rgb("#9aa6d0"), rgb("#b8b0c8"), rgb("#e8c8a0"))
    for _ in range(300):
        x = rng.randrange(W)
        y = rng.randrange(0, 270)
        if rng.random() > 0.35 + 0.65 * (1 - x / W) ** 0.7 * (1 - y / 270) and rng.random() < 0.6:
            continue
        out.append((x, y, rng.choice(pale), 1 if rng.random() < 0.06 else 0))
    for x, y, c in ((68, 128, rgb("#a8f0d0")), (214, 49, rgb("#f0b080")), (52, 270, rgb("#9ad0f0")), (410, 22, rgb("#f4e8c8"))):
        out.append((x, y, c, 1))
    return out


STARS: Final = _stars()
CRATERS: Final = ((-6, -4, 5), (4, 5, 4), (7, -7, 2), (-3, 8, 3), (-9, 4, 2))     # moon craters: dx, dy, radius


def moon_pixel(x: int, y: int) -> Color | None:
    mx, my, mr = MOON
    dx, dy = (x - mx) / mr, (y - my) / mr
    if dx * dx + dy * dy > 1:
        return None
    nz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
    light = 0.5 * dx - 0.35 * dy + 0.75 * nz            # lit from the upper right, a shadowed left limb
    v = 0.3 + 0.55 * light + 0.1 * (vn(x * 0.5, y * 0.5, 31) - 0.5)
    for cx, cy, cr in CRATERS:
        d = math.hypot(x - mx - cx, y - my - cy)
        if d < cr - 0.5:
            v -= 0.22 if (x - mx - cx) * 0.6 - (y - my - cy) * 0.4 < 0 else 0.1     # pit, darker on the lit-side wall
        elif d < cr + 0.7 and (x - mx - cx) > 0:
            v += 0.12                                   # lit rim
    return at(MOON_R, v, x, y)


def sky_pixel(x: int, y: int) -> Color:
    h, s, nx = arc(x, y)
    m = moon_pixel(x, y)
    if m is not None:
        return m
    bg = at(SKY_BG, 0.12 + 0.35 * nx + min(h, 260) / 420 + 0.25 * vn(x / 70, y / 70, 3), x, y)
    thick = 44 + 82 * nx ** 1.3
    if h < thick:
        p = 1 - h / thick
        rays = vn(s / 26, h / 60, 4)
        cloud = 0.6 * vn(s / 42, h / 15, 5) + 0.4 * vn(s / 12, h / 6, 6)
        val = p ** 1.1 * (0.4 * rays + 0.8 * cloud) * 1.55 - 0.16
        val += 0.6 * max(0.0, 1 - h / 10) ** 2                   # the air glowing at the limb
        if h < 3:
            val += 0.25
        zone = 0.95 * nx + 0.5 * (vn(s / 70, h / 22, 7) - 0.5)
        accent = vn(s / 60 + 9, h / 30, 8)
        if val > 0.1:
            if accent > 0.8 and 0.15 < zone < 0.85:
                r = BAND_ROSE
            elif zone < 0.22:
                r = BAND_BLUE
            elif zone < 0.5:
                r = BAND_VIOLET if accent < 0.55 else BAND_MAUVE
            elif zone < 0.72:
                r = BAND_MAUVE
            else:
                r = BAND_TEAL if accent < 0.5 else BAND_VIOLET
            if h < 5 and zone > 0.15:
                r = BAND_ROSE if val > 0.5 else r
            c = at(r, val, x, y, 2.0)
            if val > 0.22 or bay(x, y) < val * 3:
                bg = c
    mx, my, mr = MOON                                           # halo of the moon over the band
    dm = math.hypot(x - mx, y - my)
    if mr < dm < mr + 40:
        g = (1 - (dm - mr) / 40) ** 1.9
        if g * 1.15 > bay(x, y):
            bg = at(BAND_ROSE, 0.35 + 0.8 * g, x, y)
    return bg


def sky_layer() -> Pix:
    p = Pix(W, H, seed=5)
    for y in range(H):
        for x in range(W):
            p.px(x, y, sky_pixel(x, y))
    for x, y, c, big in STARS:
        if math.hypot(x - CX, y - CY) < R - 1:
            continue
        p.px(x, y, c)
        if big:
            dim = mix(c, SKY_BG[1], 0.55)
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(x + ddx, y + ddy, dim)
    return p


# ----------------------------------------------------------------------------------------------------------- world
Terrain = tuple[float, float, float, float]   # gx, gy, nz, den


def geo(x: int, y: int) -> Terrain:
    nx, ny = (x - CX) / R, (y - CY) / R
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    den = nz * 0.8 + 0.3
    return nx / den, ny / den, nz, den


def height(gx: float, gy: float) -> float:
    return 0.5 * vn(gx * 2.2, gy * 2.2, 11) + 0.28 * vn(gx * 5.3, gy * 5.3, 12) + 0.14 * vn(gx * 12, gy * 12, 13) + 0.08 * vn(gx * 26, gy * 26, 14)


def night_depth(x: int, y: int) -> float:
    """Pixels into the shadow side (negative on the lit side): the terminator is a ragged line across the lower right."""
    line = (150 * (x - 640) + 210 * (y - 150)) / 258
    return line + 46 * (vn(x / 48, y / 48, 40) - 0.5) + 14 * (vn(x / 9, y / 9, 41) - 0.5)


def land_color(x: int, y: int, g: Terrain, shade: float) -> Color:
    gx, gy, nz, den = g
    scale = den / 1.1
    fine = vn(gx * 42, gy * 42, 20) - 0.5
    water = 0.7 * vn(gx * 3.2, gy * 3.2, 21) + 0.3 * vn(gx * 9, gy * 9, 22)
    rim = max(0.0, 1 - nz / 0.5) ** 1.6 * 0.35
    patch = (vn(gx * 4.5, gy * 4.5, 33) - 0.5) * 0.32         # broad lighter and darker tracts, as on the original
    glob = 0.04 + 0.08 * (x / W)
    if water > 0.735:
        k = (water - 0.735) * 6
        return at(WATER, 0.62 - 0.5 * min(1.0, k) + shade * 0.7 + fine * 0.2 + rim * 0.5, x, y)
    if vn(gx * 2.4 + 9, gy * 2.4, 34) > 0.46:                  # rivers run only through some of the country
        wr = vn(gx * 5.2 + 1.5 * (vn(gx * 2, gy * 2, 23) - 0.5), gy * 5.2 + 1.5 * (vn(gx * 2 + 5, gy * 2, 24) - 0.5), 25)
        if abs(wr - 0.5) < 0.007 / scale:
            return at(WATER, 0.32 + shade * 0.8 + rim * 0.5, x, y)
    shore = water > 0.715
    qx = gx * 44 + 6 * (vn(gx * 3, gy * 3, 26) - 0.5)
    qy = gy * 44 + 6 * (vn(gx * 3 + 7, gy * 3, 27) - 0.5)
    ix, iy = math.floor(qx), math.floor(qy)
    hsh = noise(ix, iy, 9)
    forest = 0.65 * vn(gx * 7, gy * 7, 28) + 0.35 * vn(gx * 19, gy * 19, 29)
    if forest > 0.6 and not shore:
        tree = 0.6 * vn(gx * 110, gy * 110, 30) + 0.4 * vn(gx * 50, gy * 50, 35)
        kind = vn(gx * 4, gy * 4, 32)
        r = WOOD_GRN if kind < 0.16 else MAPLE if kind > 0.62 else WOOD_RED
        tree = (tree - 0.5) * 2.4 + 0.5
        v = 0.3 + 0.6 * tree + shade * 1.0 + rim * 0.7 + glob + patch * 0.6
        return at(r, v, x, y, 1.8)
    r = (GOLD, GOLD, RUSTY, GOLD, EARTH, GOLD, RUSTY, GOLD, OLIVE if hsh > 0.96 else GOLD)[min(8, int(hsh * 9))]
    v = 0.55 + 0.16 * (noise(ix, iy, 10) - 0.5) + fine * 0.5 + 0.2 * (vn(gx * 120, gy * 120, 36) - 0.5) + shade + rim + glob + patch
    if r is OLIVE:
        v -= 0.08
    if hsh * 9 % 1 > 0.5 and scale > 0.5:                     # furrows
        v += 0.06 * (1 if math.sin(qy * 6.28 * 2 + 3 * (hsh > 0.5)) > 0 else -1)
    if shore:
        r, v = STUBBLE, 0.65 + shade
    return at(r, v, x, y, 2.2)


class Town:
    def __init__(self, x: int, y: int, size: float) -> None:
        self.x, self.y, self.size = x, y, size


def towns() -> list[Town]:
    rng = random.Random(404)
    out: list[Town] = []
    tries = 0
    while len(out) < 22 and tries < 600:
        tries += 1
        x, y = rng.randrange(8, W - 8), rng.randrange(95, H - 6)
        gx, gy, nz, den = geo(x, y)
        if math.hypot(x - CX, y - CY) > R - 14 or nz < 0.2:
            continue
        if any(math.hypot(t.x - x, (t.y - y) * 1.4) < 38 for t in out):
            continue
        out.append(Town(x, y, (rng.uniform(0.55, 1.0)) * (0.35 + 0.8 * nz)))
    return out


def draw_town(p: Pix, t: Town) -> None:
    rx = max(2, round(8.5 * t.size))
    ry = max(1, round(rx * 0.5))
    # walled ring: stone, lit on the right, shadow side on the left
    for yy in range(-ry - 1, ry + 2):
        for xx in range(-rx - 1, rx + 2):
            d = (xx / (rx + 0.5)) ** 2 + (yy / (ry + 0.5)) ** 2
            if d <= 1:
                X, Y = t.x + xx, t.y + yy
                if d > 0.62:
                    p.px(X, Y, STONE_PALE if xx + (-yy) * 0.3 > -rx * 0.3 else STONE_DARK)
                else:
                    p.px(X, Y, rgb("#b88858") if noise(X, Y, 5) < 0.6 else rgb("#9c6e48"))
    rng = random.Random(t.x * 31 + t.y)
    for _ in range(max(2, rx * ry // 4)):                     # roofs
        xx = rng.randint(-rx + 2, rx - 2)
        yy = rng.randint(-ry + 1, ry - 1)
        if (xx / rx) ** 2 + (yy / ry) ** 2 < 0.45:
            p.px(t.x + xx, t.y + yy, ROOF_RED)
            p.px(t.x + xx + 1, t.y + yy, rgb("#e07848"))
    if rx >= 5:                                                # keep with its shadow thrown to the left
        p.rect(t.x - 1, t.y - 2, 2, 3, rgb("#f0dcb0"))
        p.px(t.x - 2, t.y, rgb("#5a3a34"))
        p.px(t.x - 3, t.y + 1, rgb("#5a3a34"))
    for _ in range(round(rx * 2.5)):                           # farms round about
        a = rng.random() * 6.28
        xx, yy = round(math.cos(a) * rx * rng.uniform(1.3, 2.2)), round(math.sin(a) * ry * rng.uniform(1.4, 2.4))
        p.px(t.x + xx, t.y + yy, ROOF_RED)


def roads(p: Pix, ts: list[Town]) -> None:
    rng = random.Random(55)
    for i, a in enumerate(ts):
        near = sorted((t for t in ts if t is not a), key=lambda t: math.hypot(t.x - a.x, t.y - a.y))[:1]
        for b in near:
            if (i + b.x) % 3 == 0:
                continue
            mx, my = (a.x + b.x) / 2 + rng.uniform(-10, 10), (a.y + b.y) / 2 + rng.uniform(-6, 6)
            pts = [(a.x, a.y), (mx, my), (b.x, b.y)]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                n = int(max(abs(x1 - x0), abs(y1 - y0)))
                for k in range(n):
                    xx, yy = round(x0 + (x1 - x0) * k / max(1, n)), round(y0 + (y1 - y0) * k / max(1, n))
                    if (xx + yy) % 5:
                        p.px(xx, yy, rgb("#d8b27c") if (k // 3) % 2 else rgb("#c89a66"))


def world_layer(sky: Pix) -> tuple[Pix, list[Town]]:
    """The world by day, then pushed into night where the shadow falls, with its limb haze and cloud banks."""
    p = sky
    inside = [(x, y) for y in range(H) for x in range(W) if math.hypot(x - CX, y - CY) < R]
    hs: dict[tuple[int, int], float] = {}
    for x, y in inside:
        gx, gy, *_ = geo(x, y)
        hs[x, y] = height(gx, gy)
    day: dict[tuple[int, int], Color] = {}
    for x, y in inside:
        a = hs
        sx = a.get((x - 1, y), a[x, y]) - a.get((x + 1, y), a[x, y])
        sy = a.get((x, y + 1), a[x, y]) - a.get((x, y - 1), a[x, y])
        shade = clamp((sx * 1.0 + sy * 0.55) * 7.0, -0.35, 0.35) + 0.05
        g = geo(x, y)
        day[x, y] = land_color(x, y, g, shade)
    for (x, y), c in day.items():
        p.px(x, y, c)
    ts = towns()
    roads(p, ts)
    for t in ts:
        draw_town(p, t)
    return p, ts


def night_pass(p: Pix, ts: list[Town]) -> None:
    for y in range(H):
        for x in range(W):
            if math.hypot(x - CX, y - CY) >= R:
                continue
            d = night_depth(x, y)
            tt = clamp((d + 14) / 46) * 2
            if tt <= 0:
                continue
            i = int(tt)
            state = i + 1 if tt - i > bay(x, y) else i
            c = p.get(x, y)[:3]
            if state == 1:
                p.px(x, y, mix(tuple(int(v * 0.72) for v in c), rgb("#5a2c4a"), 0.32))
            elif state >= 2:
                p.px(x, y, at(NIGHT_MASS, lum(c) * 1.05 + 0.05, x, y, 1.6))
    rng = random.Random(8)
    for t in ts:                                          # lamps of the towns that lie in the dark
        d = night_depth(t.x, t.y)
        if d > 8:
            rx = max(2, round(8.5 * t.size))
            n = rx + 3
            for _ in range(n):
                xx = t.x + rng.randint(-rx + 1, rx - 1)
                yy = t.y + rng.randint(-max(1, rx // 2), max(1, rx // 2))
                p.px(xx, yy, rgb("#f0a040") if rng.random() < 0.7 else rgb("#ffd88a"))
            p.px(t.x - 1, t.y, rgb("#ffe8b0"))
    for _ in range(40):                                   # farm lights scattered over the dark
        x, y = rng.randrange(W), rng.randrange(H)
        if math.hypot(x - CX, y - CY) < R - 8 and night_depth(x, y) > 30:
            p.px(x, y, rgb("#b8702c") if rng.random() < 0.7 else rgb("#e8a448"))


def cloud_cover(x: int, y: int) -> float:
    d = math.hypot(x - CX, y - CY)
    h = R - d
    if h < 0 or h > 150:
        return 0.0
    s = math.atan2(x - CX, CY - y) * R
    base = 0.55 * vn(s / 85, h / 16, 50) + 0.3 * vn(s / 30, h / 7, 51) + 0.15 * vn(s / 11, h / 4, 52)
    thr = 0.54 + 0.2 * clamp(h / 150)
    return clamp((base - thr) * 5)


def air_pass(p: Pix) -> None:
    """Atmospheric perspective: haze thickens toward the limb, cloud banks lie along it and shadow the fields below."""
    rows = [[0.0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            rows[y][x] = cloud_cover(x, y)
    out = p.im.copy()
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - CX, y - CY)
            if d >= R:
                continue
            h = R - d
            nz = math.sqrt(max(0.0, 1 - ((x - CX) / R) ** 2 - ((y - CY) / R) ** 2))
            dn = night_depth(x, y)
            night = clamp((dn + 14) / 46)
            c = p.get(x, y)[:3]
            sh = rows[y - 4][x - 5] if y >= 4 and x >= 5 else 0.0     # shadow thrown by a cloud up-light of here
            if sh > 0.35 and rows[y][x] < 0.2:
                c = mix(c, rgb("#2a1624"), 0.42)
            haze = clamp(1 - nz / 0.38) ** 1.4 * 0.5
            if haze > bay(x, y) * 0.75:
                c = mix(c, HAZE_DAY if night < 0.45 else HAZE_DUSK, 0.45 if night < 0.45 else 0.55)
            cv = rows[y][x]
            if cv > 0.12:
                top = 0.3 + 0.3 * cv - 0.35 * night + 0.15 * vn(x / 5, y / 5, 53)
                cr = CLOUD_DAY if night < 0.5 else BAND_VIOLET
                cv *= 0.8
                if bay(x, y) < cv * 1.6:
                    c = at(cr, top * 0.9 - 0.05 + 0.2 * (1 - night) * (x / W), x, y, 2.0)
            # the rim of the world: a bright line on the lit limb, a violet one on the dark
            if h < 2.2:
                if night < 0.4:
                    near_moon = max(0.0, 1 - abs(x - MOON[0]) / 90)
                    c = rgb("#fff0b8") if h < 1.1 and (x < 300 or near_moon > 0.3 or bay(x, y) < 0.5) else rgb("#f8c060")
                else:
                    c = rgb("#a870a0") if h < 1.1 else rgb("#6a3a7a")
            elif h < 4.2 and night < 0.4 and (x < 280 or x > 500):
                c = mix(c, rgb("#ffd070"), 0.5) if bay(x, y) < 0.7 else c
            out.putpixel((x, y), (*c, 255))
    p.im.paste(out)


# ----------------------------------------------------------------------------------------------------------- text
TINY: Final[Mapping[str, Sequence[str]]] = {
    "Q": ("111", "101", "101", "111", "001"), "U": ("101", "101", "101", "101", "111"),
    "E": ("111", "100", "111", "100", "111"), "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"), "I": ("111", "010", "010", "010", "111"),
    "N": ("111", "101", "101", "101", "101"), "G": ("111", "100", "101", "101", "111"),
    "O": ("010", "101", "101", "101", "010"), "D": ("110", "101", "101", "101", "110"),
    "2": ("111", "001", "111", "100", "111"), "0": ("111", "101", "101", "101", "111"),
    "4": ("101", "101", "111", "001", "001"),
}


def credit(p: Pix, x: int, y: int, text: str) -> None:
    """A small pixel lettering, light with a dark outline, as the original's credit; 3x5 glyphs, 4 px apart."""
    cells: list[tuple[int, int]] = []
    cx = x
    for ch in text.upper():
        rows = TINY.get(ch)
        if rows:
            for j, row in enumerate(rows):
                for i, bit in enumerate(row):
                    if bit == "1":
                        cells.append((cx + i, y + j))
            cx += 4
        else:
            cx += 3
    ink = set(cells)
    for (a, b) in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (a + dx, b + dy) not in ink:
                    p.px(a + dx, b + dy, rgb("#241520"))
    for (a, b) in cells:
        p.px(a, b, rgb("#eee2d4") if b < y + 3 else rgb("#d8c4b8"))


# ----------------------------------------------------------------------------------------------------- composition
@lru_cache(maxsize=1)
def _base() -> Image.Image:
    sky = sky_layer()
    p, ts = world_layer(sky)
    night_pass(p, ts)
    air_pass(p)
    from mnu_planet_keep import draw_citadel
    draw_citadel(p)
    return p.im.copy()


def scene(lettered: bool) -> Image.Image:   # `lettered` is kept for the two file names; the credit is on both
    p = Pix(W, H, seed=1)
    p.im.paste(_base())
    credit(p, 277, 305, "Questing Goose Studio 2024")        # both originals carry the studio credit
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "MenuMockupExported.640x320.png": lambda: scene(True),
    "MenuMockupExportedNoText.640x320.png": lambda: scene(False),
}
