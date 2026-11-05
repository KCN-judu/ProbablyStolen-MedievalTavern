"""Four more places of the tavern world, 960x540 backdrops (catalog group `scene/backgrounds`):

* `commissary`      a market storehouse: an aisle between shelves of sacks, casks, jars and cheeses, a bright doorway at the end;
* `drjackson`       the physician's window: a timber gable around a counter, the apothecary's study behind it (physician present);
* `drjackson2`      the same place a moment later: the physician is away and a patient lies in the cot;
* `dumping_ground`  the midden behind the tavern at dusk: a heap with a broken cart, a stone wall, a lantern-lit shed.

The game puts interface over them, so each keeps the original's composition: the aisle's vanishing point and doorway in
the middle, the serving window and counter left of centre with a dark panel to the right, the heap in the centre with a
walkway in the lower right.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image

import font
from materials import beam, masonry, plaster, shadow_under
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, NIGHT, OAK, PALE_WOOD, PARCHMENT, PLASTER, SHADOW, SOOT, STONE, WINE, WOOD
from pix import Color, Pix, Ramp, mix

W, H = 960, 540
HAZE: Final[Color] = (44, 30, 40)


# ---------------------------------------------------------------------------------------------- small helpers


def dimr(r: Ramp, k: float, to: Color = HAZE) -> list[Color]:
    """A ramp pulled toward the haze of the room: things far from the lamps are dimmer."""
    return [mix(c[:3], to, min(1.0, max(0.0, k))) for c in r]


def blob(p: Pix, x: int, y: int, w: int, h: int, r: Ramp, rim: bool = True) -> None:
    """A lit ellipse: light from the upper left, a dark rim, so a sack, a cabbage or a stone reads as a round thing."""
    if w < 1 or h < 1:
        return
    for yy in range(h):
        for xx in range(w):
            nx, ny = (xx + 0.5) / w * 2 - 1, (yy + 0.5) / h * 2 - 1
            d = nx * nx + ny * ny
            if d > 1:
                continue
            light = -(nx * 0.65 + ny * 0.75)
            t = 3 if light > 0.5 else 2 if light > -0.05 else 1 if light > -0.55 else 0
            if rim and d > 0.78:
                t = 0 if (nx + ny) > -0.3 else max(0, t - 1)
            p.px(x + xx, y + yy, r[min(t, len(r) - 1)])


def strip(p: Pix, x0: int, y0: int, x1: int, y1: int, t: int, r: Ramp, steep: bool = False) -> None:
    """A straight timber from (x0,y0) to (x1,y1), t thick (measured in y, or in x when steep), lit on its upper-left edge."""
    if steep:
        pts = [(x0, y0), (x0 + t, y0), (x1 + t, y1), (x1, y1)]
        p.poly(pts, r[2])
        p.line(x0, y0, x1, y1, r[3])
        p.line(x0 + t, y0, x1 + t, y1, r[0])
    else:
        pts = [(x0, y0), (x1, y1), (x1, y1 + t), (x0, y0 + t)]
        p.poly(pts, r[2])
        p.line(x0, y0, x1, y1, r[3])
        p.line(x0, y0 + t, x1, y1 + t, r[0])


def pool(p: Pix, cx: int, cy: int, r: int, strength: float = 0.5) -> None:
    """Lamplight: a wide faint amber pool with a brighter core."""
    p.glow(cx, cy, r, FLAME[0], strength * 0.5)
    p.glow(cx, cy, r // 2, FLAME[1], strength * 0.5)
    p.glow(cx, cy, r // 5, FLAME[3], 0.8)


def vignette(p: Pix, x0: int, y0: int, x1: int, y1: int, depth: int = 90, strength: float = 0.8) -> None:
    """Darkens the edges of a rectangle in dithered bands, so the middle is where the eye goes."""
    for i in range(depth // 6):
        d = strength * (1 - i / (depth / 6))
        o = i * 6
        p.dither(x0 + o, y0, 6, y1 - y0, SOOT[0], d)
        p.dither(x1 - o - 6, y0, 6, y1 - y0, SOOT[0], d)
        p.dither(x0, y0 + o, x1 - x0, 6, SOOT[0], d * 0.9)
        p.dither(x0, y1 - o - 6, x1 - x0, 6, SOOT[0], d * 0.9)


# ---------------------------------------------------------------------------------------------- goods


def barrel(p: Pix, cx: int, by: int, s: int, k: float = 0.0) -> None:
    """A cask seen from the side, s tall: bulging staves, two iron hoops."""
    r, ir = dimr(WOOD, k), dimr(IRON, k)
    w, h = max(4, round(s * 0.78)), max(4, s)
    for yy in range(h):
        t = yy / max(1, h - 1)
        half = max(1, round(w / 2 * (0.84 + 0.16 * (1 - (2 * t - 1) ** 2))))
        for xx in range(-half, half):
            u = (xx + half) / (2 * half)
            tone = 3 if u < 0.22 else 2 if u < 0.62 else 1 if u < 0.88 else 0
            if w > 14 and (xx + half) % max(4, w // 5) == 0:
                tone = max(0, tone - 1)
            p.px(cx + xx, by - h + yy, r[tone])
    for t in (0.2, 0.8):
        yy = by - h + round(h * t)
        half = max(1, round(w / 2 * (0.84 + 0.16 * (1 - (2 * t - 1) ** 2))))
        p.hline(cx - half, yy, 2 * half, ir[3])
        if h > 18:
            p.hline(cx - half, yy + 1, 2 * half, ir[1])
    p.hline(cx - w // 2 + 1, by - h, w - 2, r[0])
    p.hline(cx - w // 2 + 1, by - 1, w - 2, r[0])


def sack(p: Pix, cx: int, by: int, s: int, k: float = 0.0, ramp: Ramp = LINEN) -> None:
    """A tied sack s tall: a round belly, a puckered neck, a cord."""
    r = dimr(ramp, k)
    w = max(4, round(s * 1.1))
    h = max(4, round(s * 0.85))
    blob(p, cx - w // 2, by - round(h * 0.7), w, round(h * 0.7), r)
    p.hline(cx - w // 2 + 1, by - 1, w - 2, r[0])
    nw = max(2, w // 3)
    p.rect(cx - nw // 2, by - h, nw, max(2, h * 2 // 5), r[2])
    p.px(cx - nw // 2, by - h, r[3])
    if h > 9:
        p.hline(cx - nw // 2 - 1, by - h + max(1, h // 5), nw + 2, dimr(LEATHER, k)[1])
        p.px(cx + nw // 2 + 1, by - h + max(2, h // 5) + 1, dimr(LEATHER, k)[1])


def crate(p: Pix, cx: int, by: int, s: int, k: float = 0.0, fruit: Ramp = WINE) -> None:
    """A slatted crate of fruit or cabbages."""
    r, f = dimr(PALE_WOOD, k), dimr(fruit, k)
    w, h = max(5, round(s * 1.1)), max(4, round(s * 0.55))
    x0 = cx - w // 2
    n = max(2, w // 4)
    for i in range(n):
        blob(p, x0 + 1 + i * (w - 2) // n, by - h - max(1, s // 6), max(3, (w - 2) // n + 1), max(3, s // 3), f)
    p.rect(x0, by - h, w, h, r[2])
    p.hline(x0, by - h, w, r[4])
    p.hline(x0, by - 1, w, r[0])
    p.vline(x0, by - h, h, r[3])
    p.vline(x0 + w - 1, by - h, h, r[0])
    if h > 6:
        p.hline(x0, by - h // 2, w, r[1])


def jar(p: Pix, cx: int, by: int, s: int, k: float = 0.0, liquid: Color = (176, 120, 40)) -> None:
    """A stoppered jar of honey, oil or herbs."""
    g = dimr(GLASS, k * 0.6)
    w, h = max(3, round(s * 0.5)), max(4, round(s * 0.8))
    lq = [mix(liquid, (20, 10, 12), v) for v in (0.55, 0.3, 0.0, -0.3)]
    lq = [mix(c, HAZE, k) for c in lq]
    x0 = cx - w // 2
    p.rect(x0, by - h, w, h, g[1])
    p.rect(x0 + 1, by - h + 1, max(1, w - 2), max(1, h - 1), lq[1])
    p.vline(x0 + 1, by - h + 1, max(1, h - 2), lq[3])
    p.vline(x0 + w - 1, by - h, h, lq[0])
    nk = max(2, w // 2)
    p.rect(cx - nk // 2, by - h - max(1, s // 6), nk, max(1, s // 6), dimr(LEATHER, k)[2])


def cheese(p: Pix, cx: int, by: int, s: int, k: float = 0.0) -> None:
    """A wheel of cheese on its edge."""
    r = dimr(BRASS, k + 0.15)
    blob(p, cx - s // 2, by - round(s * 0.7), s, round(s * 0.7), r)
    if s > 10:
        p.px(cx - s // 6, by - s // 3, r[0])
        p.px(cx + s // 5, by - s // 2, r[0])


def loaves(p: Pix, cx: int, by: int, s: int, k: float = 0.0) -> None:
    """Three round loaves."""
    r = dimr(LEATHER, k - 0.15)
    r2 = [mix(c, (200, 140, 70), 0.25) for c in r]
    w = max(3, s // 2)
    for i, dx in enumerate((-w // 2, w // 2, 0)):
        blob(p, cx + dx - w // 2, by - w * (1 if i < 2 else 2) + (0 if i < 2 else w // 3), w, max(2, w - 1), r2)


def goods(p: Pix, kind: int, cx: int, by: int, s: int, k: float) -> None:
    if kind == 0:
        sack(p, cx, by, s, k)
    elif kind == 1:
        barrel(p, cx, by, s, k)
    elif kind == 2:
        crate(p, cx, by, s, k, WINE)
    elif kind == 3:
        jar(p, cx, by, s, k)
    elif kind == 4:
        cheese(p, cx, by, s, k)
    elif kind == 5:
        sack(p, cx, by, s, k, PALE_WOOD)
    elif kind == 6:
        crate(p, cx, by, s, k, MOSS)
    elif kind == 7:
        loaves(p, cx, by, s, k)
    else:
        jar(p, cx, by, s, k, (120, 150, 60))


# ---------------------------------------------------------------------------------------------- commissary

VPX, VPY = 480, 205
ZS: Final = (1.0, 1.16, 1.36, 1.62, 1.95, 2.35, 2.85, 3.4, 4.0)
XS = 400        # the shelf fronts
YT, YF = -170, 335     # shelf top, floor


def pr(x: float, y: float, z: float) -> tuple[int, int]:
    """Aisle space to screen: x across, y down from eye level, z away from the viewer (the nearest plane is z = 1)."""
    return round(VPX + x / z), round(VPY + y / z)


def haze_k(z: float) -> float:
    return min(0.6, 0.06 + (z - 1) * 0.16)


def aisle_back(p: Pix) -> None:
    """The far end: a plastered wall with a bright doorway to the market square."""
    x0, y0 = pr(-480, -205, 4.0)
    x1, y1 = pr(480, YF, 4.0)
    plaster(p, x0, y0, x1 - x0, y1 - y0, dimr(PLASTER, 0.35), stains=False)
    dx0, dx1, dy0 = 410, 552, 192
    p.rect(dx0, dy0 + 14, dx1 - dx0, y1 - dy0 - 14, PARCHMENT[3])
    p.ellipse(dx0, dy0, dx1 - dx0, 30, PARCHMENT[3])
    p.gradient(dx0, dy0, dx1 - dx0, y1 - dy0, PARCHMENT[4], FLAME[3], 6)
    # the square beyond: a stall awning, a far wall, a tree, a passer-by
    p.rect(dx0, 252, dx1 - dx0, y1 - 252, mix(PARCHMENT[2], FLAME[1], 0.4))
    for i in range(8):
        c = WINE[3] if i % 2 == 0 else LINEN[3]
        p.poly([(dx0 + 4 + i * 8, 232), (dx0 + 12 + i * 8, 232), (dx0 + 12 + i * 8, 242 + (i % 2)), (dx0 + 4 + i * 8, 242 + (i % 2))], c)
    p.rect(dx0 + 4, 242, 66, 2, WINE[1])
    p.rect(dx0 + 6, 244, 2, 22, OAK[2])
    p.rect(dx0 + 66, 244, 2, 22, OAK[2])
    blob(p, dx0 + 88, 216, 28, 26, MOSS)
    p.rect(dx0 + 100, 240, 3, 26, WOOD[1])
    p.rect(dx0 + 120, 250, 4, 6, LEATHER[2])               # a passer-by
    p.rect(dx0 + 120, 256, 4, 10, WINE[2])
    p.hline(dx0 + 6, 266, 128, STONE[3])
    # the frame
    p.frame(dx0 - 1, dy0 - 1, dx1 - dx0 + 2, y1 - dy0 + 1, OAK[0])
    p.rect(dx0 - 6, dy0 + 12, 6, y1 - dy0 - 12, OAK[2])
    p.rect(dx1, dy0 + 12, 6, y1 - dy0 - 12, OAK[1])
    p.vline(dx0 - 6, dy0 + 12, y1 - dy0 - 12, OAK[3])
    for xx in range(dx0 - 6, dx1 + 6):
        t = (xx - (dx0 + dx1) / 2) / ((dx1 - dx0) / 2 + 6)
        yy = dy0 + 16 - round(math.sqrt(max(0.0, 1 - t * t)) * 16)
        p.rect(xx, yy - 5, 1, 5, OAK[2 if xx < 480 else 1])
        p.px(xx, yy - 5, OAK[3])
    p.glow(481, 262, 70, FLAME[3], 0.6)


def aisle_floor(p: Pix, rng: random.Random) -> None:
    """Flagstones laid in rows that shrink toward the door."""
    p.poly([pr(-480, YF, 1.0), pr(480, YF, 1.0), pr(480, YF, 4.0), pr(-480, YF, 4.0)], STONE[1])
    xs = list(range(-480, 481, 90))
    for j in range(len(ZS) - 1):
        for i in range(len(xs) - 1):
            za, zb = ZS[j], ZS[j + 1]
            tone = rng.choice((1, 2, 2, 3))
            r = [mix(c, (120, 84, 60), 0.18) for c in dimr(STONE, haze_k(za) * 0.8)]
            pts = [pr(xs[i] + 2, YF, za), pr(xs[i + 1] - 2, YF, za), pr(xs[i + 1] - 2, YF, zb - 0.02), pr(xs[i] + 2, YF, zb - 0.02)]
            p.poly(pts, r[tone])
            a, b = pts[3], pts[2]
            p.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], r[min(4, tone + 1)])      # lit near edge
            if zb < 4.0:
                p.line(a[0], a[1], b[0], b[1], r[0])
            x_mid = (pts[0][0] + pts[1][0]) // 2
            if rng.random() < 0.3:
                p.px(x_mid + rng.randrange(-4, 4), (pts[0][1] + pts[3][1]) // 2, r[0])


def aisle_ceiling(p: Pix, rng: random.Random) -> None:
    p.poly([pr(-480, -205, 1.0), pr(480, -205, 1.0), pr(480, -205, 4.0), pr(-480, -205, 4.0)], WOOD[1])
    for x in range(-480, 481, 80):
        a, b = pr(x, -205, 1.0), pr(x, -205, 4.0)
        p.line(a[0], a[1], b[0], b[1], WOOD[0])
    for z in (1.0, 1.7, 2.45, 3.3, 4.0):                   # tie beams across the aisle
        y_top, y_bot = pr(0, -205, z)[1], pr(0, -150, z)[1]
        r = dimr(OAK, haze_k(z) * 0.7)
        xl, xr = pr(-480, 0, z)[0], pr(480, 0, z)[0]
        p.rect(xl, y_top, xr - xl, max(2, y_bot - y_top), r[2])
        p.hline(xl, y_bot - 1, xr - xl, r[0])
        p.hline(xl, y_top, xr - xl, r[3])
        p.dither(xl, y_top + 1, xr - xl, max(1, y_bot - y_top - 2), r[1], 0.4)
        # braces down the walls
        for sgn in (-1, 1):
            xb = pr(sgn * 480, 0, z)[0]
            yb = pr(0, -205, z)[1] + max(2, y_bot - y_top)
            ln = max(6, round(70 / z))
            p.poly([(xb, yb), (xb - sgn * ln, yb), (xb, yb + ln)], r[1])


def hanging(p: Pix, rng: random.Random) -> None:
    """Things that hang from the tie beams: sausages, garlic, herbs, and the lanterns."""
    for z, xs in ((1.7, (-330, -140, 150, 320)), (2.45, (-260, 40, 250)), (3.3, (-170, 180))):
        for x in xs:
            sx, sy = pr(x, -150, z)
            s = round(60 / z)
            k = haze_k(z)
            kind = rng.randrange(3)
            if kind == 0:                                  # sausage links
                for i in range(3):
                    p.rect(sx - 1, sy + i * (s // 3), 1, s // 3, dimr(LEATHER, k)[1])
                    blob(p, sx - s // 8, sy + 2 + i * (s // 3), max(3, s // 4), max(4, s // 3), dimr(WINE, k))
            elif kind == 1:                                # a string of garlic
                p.vline(sx, sy, s, dimr(LEATHER, k)[1])
                for i in range(4):
                    blob(p, sx - s // 8 + (i % 2) * 2 - 1, sy + 2 + i * (s // 5), max(3, s // 4), max(3, s // 5), dimr(LINEN, k))
            else:                                          # a bunch of herbs, root up
                p.vline(sx, sy, s // 4, dimr(LEATHER, k)[1])
                p.poly([(sx - s // 10, sy + s // 4), (sx + s // 10, sy + s // 4), (sx + s // 5, sy + s * 3 // 4), (sx - s // 5, sy + s * 3 // 4)], dimr(MOSS, k)[2])
                p.line(sx, sy + s // 4, sx - s // 8, sy + s * 3 // 4, dimr(MOSS, k)[3])
    for z, x, drop in ((1.35, -150, 120), (2.2, 110, 100), (3.2, -50, 80)):          # lanterns on chains
        sx, ytop = pr(x, -205, z)
        ly = pr(0, -205 + drop, z)[1]
        p.rect(sx - 1, ytop - 1, 3, 2, IRON[3])
        s = max(6, round(46 / z))
        p.vline(sx, ytop, ly - ytop, IRON[3])
        p.rect(sx - s // 2, ly, s, s, IRON[1])
        p.frame(sx - s // 2, ly, s, s, IRON[3])
        p.rect(sx - s // 2 + 2, ly + 2, s - 4, s - 4, FLAME[3])
        p.rect(sx - s // 4, ly + s // 4, max(1, s // 2), max(1, s // 2), FLAME[4])
        pool(p, sx, ly + s // 2, round(110 / z), 0.6 if z < 2.5 else 0.5)


def shelf_side(p: Pix, sgn: int, rng: random.Random) -> None:
    """One side of the aisle: bays of shelving from far to near, each with its goods, posts and boards."""
    levels = (-150, -20, 110, 240)
    for j in range(len(ZS) - 2, -1, -1):
        z0, z1 = ZS[j], ZS[j + 1]
        zc_all = (z0 + z1) / 2
        k = haze_k(zc_all)
        q = [pr(sgn * XS, YT, z0), pr(sgn * XS, YT, z1), pr(sgn * XS, YF, z1), pr(sgn * XS, YF, z0)]
        p.poly(q, dimr(WOOD, k + 0.3)[0])
        for y in levels:
            n = 3 if z0 > 2.3 else 4
            for i in range(n):
                zc = z0 + (z1 - z0) * (i + 0.5) / n
                sx, sy = pr(sgn * (XS + 40), y + 8, zc)
                kind = rng.choice((0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 7, 8))
                s = round(66 / zc * (0.75 + 0.3 * rng.random()))
                goods(p, kind, sx, sy, s, haze_k(zc))
        for y in levels + (YF - 8,):                       # the boards
            a, b = pr(sgn * XS, y + 8, z0), pr(sgn * XS, y + 8, z1)
            thick = max(2, round(12 / z0))
            r = dimr(PALE_WOOD, k + 0.15)
            p.poly([a, b, (b[0], b[1] + max(2, round(12 / z1))), (a[0], a[1] + thick)], r[1])
            p.line(a[0], a[1], b[0], b[1], r[3])
        p.line(q[0][0], q[0][1], q[1][0], q[1][1], dimr(OAK, k)[3])
    for z in ZS:                                            # posts
        x, ytop = pr(sgn * XS, YT - 20, z)
        ybot = pr(sgn * XS, YF, z)[1]
        w = max(2, round(14 / z))
        r = dimr(OAK, haze_k(z))
        p.rect(x - w // 2, ytop, w, ybot - ytop, r[2])
        p.vline(x - w // 2, ytop, ybot - ytop, r[3])
        p.vline(x + w // 2 - 1, ytop, ybot - ytop, r[0])


def end_panel(p: Pix, left: bool) -> None:
    """The near end of the first shelf unit: a plank panel with the iron strap and a hanging price board."""
    x0 = 0 if left else W - 80
    p.rect(x0, 0, 80, H, WOOD[0])
    for i in range(0, 80, 20):
        p.vline(x0 + i, 0, H, WOOD[1])
        p.vline(x0 + i + 1, 0, H, WOOD[2])
    p.dither(x0, 0, 80, H, SOOT[0], 0.45)
    p.vline(x0 + (79 if left else 0), 0, H, OAK[3])
    for y in (60, 300):
        p.rect(x0, y, 80, 8, IRON[2])
        p.hline(x0, y, 80, IRON[4])
        for xx in (8, 30, 52, 72):
            p.px(x0 + xx, y + 3, BRASS[3])
    sx = x0 + (6 if left else 14)
    p.rect(sx, 120, 60, 40, PARCHMENT[2])
    p.frame(sx, 120, 60, 40, WOOD[1])
    font.write(p, sx + 6, 126, "FLOUR", WOOD[1])
    font.write(p, sx + 6, 138, "2 PENCE", WINE[1])
    p.hline(sx + 6, 150, 48, PARCHMENT[1])


def commissary() -> Image.Image:
    p = Pix(W, H, seed=71)
    rng = random.Random(7101)
    plaster(p, 0, 0, W, H, dimr(PLASTER, 0.3), stains=False)
    aisle_ceiling(p, rng)
    aisle_floor(p, rng)
    aisle_back(p)
    shelf_side(p, -1, rng)
    shelf_side(p, 1, rng)
    hanging(p, rng)
    p.glow(480, 400, 200, FLAME[0], 0.4)
    # an open barrel and two sacks in the near aisle, a mop bucket: things people left lying about
    barrel(p, 150, 530, 96, 0.0)
    sack(p, 215, 534, 64, 0.0)
    sack(p, 262, 536, 52, 0.0, PALE_WOOD)
    crate(p, 835, 534, 70, 0.0, MOSS)
    sack(p, 790, 536, 56, 0.0)
    end_panel(p, True)
    end_panel(p, False)
    vignette(p, 0, 0, W, H, 66, 0.45)
    return p.finish()


# ---------------------------------------------------------------------------------------------- the physician's window

OPENING: Final = [(296, 275), (296, 104), (468, 32), (640, 104), (640, 275)]


def herb_bunch(p: Pix, x: int, y: int, s: int, k: float = 0.0, flower: Color | None = None) -> None:
    """A bundle of herbs tied at the stalk and hung head down."""
    m = dimr(MOSS, k)
    p.vline(x, y, max(2, s // 5), dimr(LEATHER, k)[2])
    top = y + max(2, s // 5)
    for i in range(s):
        t = i / max(1, s - 1)
        half = round(1 + t * s * 0.22)
        for dx in range(-half, half + 1):
            tone = 3 if (dx + i) % 4 == 0 else 2 if (dx - i) % 5 else 1
            p.px(x + dx, top + i, m[tone if abs(dx) < half else 1])
    if flower:
        for i in range(0, s, 4):
            p.px(x + (i % 3) - 1, top + i + 1, mix(flower, HAZE, k))


def shelf_with_jars(p: Pix, x: int, y: int, w: int, rows: int, rng: random.Random, k: float = 0.0, gap: int = 44) -> None:
    """Open apothecary shelves: boards on two uprights, jars and pots of differing colour on each."""
    liquids = ((176, 120, 40), (120, 150, 60), (150, 50, 50), (110, 90, 150), (200, 170, 90))
    r = dimr(WOOD, k)
    p.rect(x, y, w, gap * rows + 4, r[0])
    for j in range(rows):
        by = y + gap * (j + 1)
        cx = x + 6
        while cx < x + w - 10:
            s = rng.randrange(20, 34)
            if rng.random() < 0.25:
                sack(p, cx + s // 2, by, s - 6, k, LINEN)
            else:
                jar(p, cx + s // 4, by, s, k, rng.choice(liquids))
            cx += s // 2 + rng.randrange(6, 12)
        p.rect(x - 2, by, w + 4, 5, dimr(PALE_WOOD, k)[2])
        p.hline(x - 2, by, w + 4, dimr(PALE_WOOD, k)[4])
        p.hline(x - 2, by + 4, w + 4, dimr(PALE_WOOD, k)[0])
    p.rect(x - 2, y, 4, gap * rows + 5, dimr(OAK, k)[2])
    p.rect(x + w - 2, y, 4, gap * rows + 5, dimr(OAK, k)[1])


def cot(p: Pix, x: int, y: int, w: int, occupied: bool) -> None:
    """A narrow sickbed: posts, a linen mattress, a pillow and a wine-red blanket (a patient under it when occupied)."""
    p.rect(x, y - 18, 7, 70, OAK[2])
    p.vline(x, y - 18, 70, OAK[3])
    p.rect(x + w - 7, y - 10, 7, 62, OAK[1])
    p.rect(x, y, w, 8, OAK[2])
    p.hline(x, y, w, OAK[3])
    p.rect(x + 7, y - 8, w - 14, 10, LINEN[2])
    p.hline(x + 7, y - 8, w - 14, LINEN[3])
    blob(p, x + 8, y - 16, 30, 12, LINEN)
    if occupied:
        blob(p, x + 20, y - 26, 22, 20, LEATHER)
        p.rect(x + 25, y - 20, 12, 5, (140, 100, 80))
        p.rect(x + 23, y - 18, 3, 2, SHADOW)
    p.poly([(x + 36, y - 10), (x + w - 8, y - 6), (x + w - 8, y + 10), (x + 36, y + 10)], WINE[2])
    p.poly([(x + 36, y - 10), (x + w - 8, y - 6), (x + w - 8, y - 4), (x + 36, y - 8)], WINE[4])
    for i in range(0, w - 50, 9):
        p.vline(x + 40 + i, y - 8, 17, WINE[1])


def instrument_rack(p: Pix, x: int, y: int) -> None:
    """A board on the back wall with a bone saw, shears, a probe and a bleeding bowl."""
    p.rect(x, y, 110, 6, OAK[2])
    p.hline(x, y, 110, OAK[3])
    for dx in (12, 38, 62):
        p.vline(x + dx, y + 6, 4, IRON[2])
    p.poly([(x + 8, y + 10), (x + 22, y + 10), (x + 22, y + 22), (x + 10, y + 36), (x + 8, y + 36)], IRON[3])
    for i in range(8):
        p.px(x + 8 + i * 2, y + 36 - i, IRON[0])
    p.rect(x + 8, y + 36, 4, 10, LEATHER[2])
    p.line(x + 36, y + 10, x + 46, y + 38, IRON[3])
    p.line(x + 46, y + 10, x + 38, y + 38, IRON[4])
    p.px(x + 41, y + 24, BRASS[3])
    p.rect(x + 36, y + 38, 3, 8, LEATHER[2])
    p.rect(x + 45, y + 38, 3, 8, LEATHER[2])
    p.line(x + 64, y + 10, x + 64, y + 40, IRON[4])
    p.rect(x + 62, y + 40, 5, 6, BRASS[2])
    p.ellipse(x + 80, y + 14, 26, 8, BRASS[2])
    p.hline(x + 82, y + 15, 22, BRASS[4])
    p.rect(x + 86, y + 20, 14, 3, BRASS[1])


def physician(p: Pix, cx: int, base: int) -> None:
    """The physician at the window: wide hat, leather beak mask with brass-rimmed glass eyes, a dark robe and a cape."""
    p.poly([(cx - 68, base), (cx - 58, base - 42), (cx - 30, base - 62), (cx + 30, base - 62), (cx + 58, base - 42), (cx + 68, base)], MOSS[1])
    p.poly([(cx - 68, base), (cx - 58, base - 42), (cx - 30, base - 62), (cx - 20, base - 62), (cx - 40, base)], MOSS[2])
    p.poly([(cx - 60, base - 40), (cx - 30, base - 62), (cx + 30, base - 62), (cx + 60, base - 40), (cx + 36, base - 30), (cx - 36, base - 30)], LEATHER[1])
    p.hline(cx - 30, base - 62, 60, LEATHER[3])
    p.poly([(cx - 24, base - 62), (cx + 24, base - 62), (cx, base - 36)], LINEN[2])
    p.line(cx - 24, base - 62, cx, base - 36, LINEN[3])
    for yy in range(base - 28, base, 6):
        p.px(cx, yy, BRASS[3])
    blob(p, cx - 21, base - 112, 42, 52, LEATHER)
    p.poly([(cx - 8, base - 84), (cx + 8, base - 84), (cx + 2, base - 54), (cx, base - 50), (cx - 2, base - 54)], LEATHER[3])
    p.line(cx - 8, base - 84, cx - 2, base - 54, LEATHER[3])
    p.line(cx + 8, base - 84, cx + 2, base - 54, LEATHER[1])
    for ex in (-11, 11):
        blob(p, cx + ex - 7, base - 98, 14, 14, BRASS)
        p.ellipse(cx + ex - 4, base - 95, 8, 8, GLASS[2])
        p.px(cx + ex - 3, base - 94, GLASS[4])
        p.px(cx + ex - 2, base - 94, GLASS[4])
    p.ellipse(cx - 40, base - 124, 80, 16, OAK[1])
    p.hline(cx - 34, base - 124, 56, OAK[3])
    p.rect(cx - 20, base - 150, 40, 30, OAK[2])
    p.rect(cx - 20, base - 150, 8, 30, OAK[3])
    p.rect(cx + 14, base - 150, 6, 30, OAK[0])
    p.rect(cx - 20, base - 132, 40, 6, WINE[2])
    p.rect(cx - 3, base - 133, 7, 8, BRASS[3])
    p.rect(cx - 1, base - 131, 3, 4, OAK[0])


def clutter_on_counter(p: Pix, state: int) -> None:
    """Things on the counter top: a ledger, a pair of scales, a candle; in state 2 a bell and a lit lamp."""
    p.poly([(330, 330), (392, 330), (396, 340), (326, 340)], PARCHMENT[3])
    p.line(330, 330, 392, 330, PARCHMENT[4])
    for i in range(3):
        p.hline(336, 333 + i * 2, 48 - i * 8, PARCHMENT[1])
    p.line(590, 335, 590, 316, IRON[3])
    p.line(574, 322, 606, 322, BRASS[3])
    p.hline(570, 328, 12, BRASS[2])
    p.hline(598, 328, 12, BRASS[2])
    if state == 2:
        p.rect(500, 316, 14, 24, BRASS[2])
        p.rect(502, 316, 4, 24, BRASS[4])
        p.rect(520, 320, 16, 18, GLASS[3])
        p.rect(523, 323, 10, 12, FLAME[3])
        p.rect(526, 326, 4, 6, FLAME[4])
        pool(p, 528, 328, 70, 0.7)
    else:
        p.rect(520, 326, 8, 12, LINEN[3])
        p.rect(522, 322, 4, 4, FLAME[3])
        p.px(523, 320, FLAME[4])
        pool(p, 524, 322, 60, 0.7)


def physician_room(p: Pix, state: int) -> None:
    """What lies behind the window: the study, drawn on its own canvas and clipped to the opening."""
    rng = random.Random(8100 + state)
    plaster(p, 270, 20, 400, 270, dimr(PLASTER, 0.45), stains=False)
    p.dither(270, 20, 400, 270, SOOT[0], 0.25)
    for x in (300, 468, 636):
        beam(p, x - 6, 20, 12, 270, dimr(OAK, 0.15), vertical=True)
    beam(p, 270, 112, 400, 12, dimr(OAK, 0.15), vertical=False)
    shelf_with_jars(p, 312, 130, 108, 3, rng, 0.15, 44)
    instrument_rack(p, 486, 126)
    p.rect(528, 40, 96, 62, OAK[1])
    p.gradient(532, 44, 88, 54, GLASS[3], GLASS[1], 4)
    for xx in range(532, 620, 11):
        p.vline(xx, 44, 54, IRON[1])
    for yy in range(44, 98, 11):
        p.hline(532, yy, 88, IRON[1])
    p.hline(526, 102, 100, OAK[3])
    p.line(310, 40, 640, 40, LEATHER[1])
    for x, y, s in ((340, 40, 34), (392, 42, 28), (440, 40, 24), (584, 106, 0)):
        if s:
            herb_bunch(p, x, y, s, 0.2, (210, 170, 70) if x % 2 else (190, 110, 140))
    cot(p, 520, 232, 116, occupied=(state == 2))
    p.glow(580, 70, 46, GLASS[4], 0.2)
    p.dither(268, 250, 380, 40, SOOT[0], 0.4)


def dark_panel(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A tall leaded window in an oak frame, dark: night behind it."""
    p.rect(x, y, w, h, OAK[1])
    p.gradient(x + 14, y + 14, w - 28, h - 28, NIGHT[2], NIGHT[0], 6)
    for xx in range(x + 14, x + w - 14, 22):
        for j in range(0, h - 50, 22):
            p.line(xx, y + 14 + j, xx + 22, y + 36 + j, IRON[1])
            p.line(xx + 22, y + 14 + j, xx, y + 36 + j, IRON[1])
    for t in range(0, 60, 12):
        p.line(x + 40 + t, y + 20, x + 100 + t, y + h // 2, NIGHT[3])
    p.frame(x, y, w, h, OAK[0])
    p.hline(x + 1, y + 1, w - 2, OAK[3])
    p.vline(x + 1, y + 1, h - 2, OAK[3])
    p.frame(x + 13, y + 13, w - 26, h - 26, OAK[0])
    for yy in (y + 40, y + h - 46):
        p.rect(x - 3, yy, w + 6, 6, IRON[2])
        p.hline(x - 3, yy, w + 6, IRON[4])
    shadow_under(p, x, y + h, w, 5)


def open_sign(p: Pix, x: int, y: int) -> None:
    p.vline(x + 10, y - 20, 24, IRON[3])
    p.vline(x + 76, y - 20, 24, IRON[3])
    p.rect(x, y + 2, 88, 40, PALE_WOOD[2])
    p.hline(x, y + 2, 88, PALE_WOOD[4])
    p.hline(x, y + 41, 88, PALE_WOOD[0])
    p.frame(x + 3, y + 5, 82, 34, BRASS[2])
    font.write(p, x + 17, y + 14, "OPEN", WINE[1], 2)
    for xx in (x + 5, x + 82):
        p.px(xx, y + 7, BRASS[4])
        p.px(xx, y + 36, BRASS[4])


def physician_wall(p: Pix) -> None:
    plaster(p, 0, 0, W, 450, dimr(PLASTER, 0.5, (34, 20, 30)))
    masonry(p, 0, 440, W, 100, dimr(STONE, 0.3, (40, 24, 30)), course=12)
    beam(p, 0, 430, W, 14, OAK, vertical=False)
    shadow_under(p, 0, 444, W, 6)
    for x in (0, 944):
        beam(p, x, 0, 16, 430, OAK, vertical=True)
    beam(p, 0, 0, W, 16, OAK, vertical=False)
    p.line(24, 40, 150, 54, LEATHER[2])
    for x, y, s, c in ((40, 41, 34, (210, 170, 70)), (72, 44, 28, (190, 110, 140)), (104, 47, 36, (210, 170, 70)), (132, 50, 26, None)):
        herb_bunch(p, x, y, s, 0.1, c)
    p.rect(170, 92, 66, 96, PARCHMENT[3])
    p.frame(170, 92, 66, 96, PARCHMENT[1])
    p.hline(171, 93, 64, PARCHMENT[4])
    font.write(p, 180, 98, "CURES", WOOD[1])
    p.hline(180, 108, 46, WINE[2])
    rng = random.Random(33)
    for i in range(9):
        y = 116 + i * 8
        p.hline(180, y, 18 + rng.randrange(14), PARCHMENT[0])
        p.hline(212, y, 12, WINE[2])
    p.rect(200, 88, 4, 4, IRON[3])
    p.poly([(96, 210), (166, 216), (170, 280), (136, 290), (100, 282)], WINE[1])
    p.poly([(96, 210), (166, 216), (166, 220), (96, 214)], WINE[3])
    p.ellipse(120, 234, 22, 22, BRASS[1])
    p.ellipse(124, 238, 14, 14, WINE[1])
    p.vline(131, 232, 26, BRASS[3])
    p.hline(118, 245, 26, BRASS[3])
    p.dither(96, 255, 74, 36, SOOT[0], 0.35)
    p.rect(40, 454, 150, 40, IRON[0])
    for xx in range(46, 186, 12):
        p.rect(xx, 456, 5, 36, IRON[3])
        p.vline(xx, 456, 36, IRON[4])
    p.frame(38, 452, 154, 44, IRON[2])
    dark_panel(p, 712, 58, 222, 312)
    p.rect(700, 486, 260, 12, IRON[2])
    p.hline(700, 486, 260, IRON[4])
    p.hline(700, 497, 260, IRON[0])
    for xx in (720, 800, 880):
        p.rect(xx, 480, 6, 24, IRON[1])
    p.rect(700, 494, 24, 14, IRON[2])
    p.rect(700, 504, 24, 4, IRON[0])
    p.vline(706, 508, 28, GLASS[3])
    p.dither(0, 0, W, 540, SOOT[0], 0.1)


def iron_dots(p: Pix, pts: Sequence[tuple[int, int]]) -> None:
    for x, y in pts:
        p.rect(x - 6, y - 12, 14, 24, IRON[2])
        p.hline(x - 6, y - 12, 14, IRON[4])
        p.hline(x - 6, y + 11, 14, IRON[0])
        p.px(x, y - 6, BRASS[3])
        p.px(x, y + 6, BRASS[3])


def physician_booth(p: Pix, state: int) -> None:
    room = Pix(W, H, seed=5 + state)
    physician_room(room, state)
    if state == 1:
        physician(room, 468, 290)
    room.clip(OPENING)
    p.paste(room, 0, 0)
    strip(p, 262, 108, 468, 14, 24, OAK)
    strip(p, 468, 14, 676, 108, 24, OAK)
    strip(p, 268, 96, 252, 470, 36, OAK, steep=True)
    strip(p, 640, 96, 664, 470, 36, OAK, steep=True)
    strip(p, 296, 104, 468, 36, 12, OAK)
    strip(p, 468, 36, 640, 104, 12, OAK)
    iron_dots(p, [(280, 170), (280, 330), (654, 170), (654, 330)])
    open_sign(p, 626, 36)
    p.poly([(296, 275), (640, 275), (704, 342), (232, 342)], PALE_WOOD[1])
    p.poly([(296, 275), (468, 275), (468, 342), (232, 342)], WINE[2])
    p.poly([(468, 275), (640, 275), (704, 342), (468, 342)], MOSS[2])
    for i in range(0, 230, 6):
        p.px(250 + i, 300 + (i // 6) % 3 * 12, WINE[3])
        p.px(480 + i, 296 + (i // 6) % 3 * 14, MOSS[3])
    p.hline(296, 275, 344, OAK[0])
    p.line(232, 342, 296, 275, PALE_WOOD[3])
    p.line(704, 342, 640, 275, PALE_WOOD[0])
    p.rect(232, 342, 472, 14, PALE_WOOD[2])
    p.hline(232, 342, 472, PALE_WOOD[4])
    p.hline(232, 355, 472, OAK[0])
    p.gradient(244, 356, 448, 124, SOOT[2], SOOT[0], 6)
    for xx in (330, 460, 590):
        p.vline(xx, 356, 124, OAK[0])
    p.rect(250, 440, 436, 4, OAK[1])
    clutter_on_counter(p, state)


def drjackson(state: int = 1) -> Image.Image:
    p = Pix(W, H, seed=80 + state)
    physician_wall(p)
    physician_booth(p, state)
    vignette(p, 0, 0, W, H, 60, 0.4)
    return p.finish()


# ---------------------------------------------------------------------------------------------- the midden

MOUND: Final = [(0, 470), (60, 430), (130, 400), (210, 345), (300, 285), (390, 240), (480, 218), (560, 228), (640, 258),
                (720, 305), (800, 352), (880, 430), (960, 470)]
DUSK: Final[Ramp] = ((22, 18, 38), (44, 30, 56), (80, 46, 70), (122, 66, 80), (170, 96, 88))


def mound_top(x: int) -> int:
    for (xa, ya), (xb, yb) in zip(MOUND, MOUND[1:]):
        if xa <= x <= xb:
            return round(ya + (yb - ya) * (x - xa) / (xb - xa))
    return 470


def wheel(p: Pix, cx: int, cy: int, r: int, k: float, broken: bool = False) -> None:
    """A cart wheel: iron tyre, felloe, spokes, hub; a broken one lacks a few spokes."""
    w, ir = dimr(WOOD, k), dimr(IRON, k)
    p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, ir[1])
    p.ellipse(cx - r + 3, cy - r + 3, 2 * r - 5, 2 * r - 5, w[2])
    p.ellipse(cx - r + 8, cy - r + 8, 2 * r - 15, 2 * r - 15, SOOT[1])
    for i in range(8):
        if broken and i in (2, 3, 6):
            continue
        a = i * math.pi / 4 + 0.2
        ex, ey = cx + round(math.cos(a) * (r - 4)), cy + round(math.sin(a) * (r - 4))
        p.line(cx, cy, ex, ey, w[2])
        p.line(cx + 1, cy, ex + 1, ey, w[1])
    for ang in range(0, 360, 3):
        a = math.radians(ang)
        p.px(cx + round(math.cos(a) * r), cy + round(math.sin(a) * r), ir[3] if ang < 180 else ir[0])
    p.ellipse(cx - 5, cy - 5, 11, 11, w[3])
    p.ellipse(cx - 2, cy - 2, 5, 5, ir[2])


def midden_cart(p: Pix) -> None:
    """A cart tipped on the slope of the heap, a wheel off, shafts in the air."""
    k = 0.15
    w = dimr(WOOD, k)
    pw = dimr(PALE_WOOD, k + 0.2)
    p.poly([(170, 392), (330, 366), (352, 424), (190, 452)], w[1])                      # the bed, seen from above
    for i in range(5):
        a = (170 + i * 40, 392 - i * 6)
        p.line(a[0] + 4, a[1] + 8, a[0] + 22, a[1] + 62, w[0])
    p.poly([(170, 392), (330, 366), (334, 380), (176, 408)], pw[2])                      # the near-side rail, lit
    p.line(170, 392, 330, 366, pw[4])
    p.poly([(190, 452), (352, 424), (352, 436), (192, 466)], w[0])
    for i in range(6):
        p.vline(180 + i * 28, 396 - i * 4, 10, w[0])
    p.line(170, 392, 70, 340, w[3])                                                     # shafts
    p.line(170, 404, 70, 356, w[2])
    p.line(70, 340, 70, 356, w[0])
    wheel(p, 240, 456, 40, k)
    wheel(p, 330, 462, 28, k + 0.1, broken=True)
    for x, y in ((210, 410), (260, 402), (305, 390)):                                   # sacks and a barrel in the bed
        sack(p, x, y, 28, 0.3, LEATHER)
    barrel(p, 300, 392, 30, 0.3)


def lean_to(p: Pix, x: int, y: int) -> None:
    """A watchman's lean-to against the wall, a lit window and a lantern: the one warm place."""
    r = dimr(WOOD, 0.1)
    p.rect(x, y + 14, 112, 74, r[1])
    for i in range(0, 112, 14):
        p.vline(x + i, y + 14, 74, r[0])
        p.vline(x + i + 1, y + 14, 74, r[2])
    p.poly([(x - 10, y + 18), (x + 56, y - 14), (x + 122, y + 18)], dimr(WINE, 0.1)[1])
    for i in range(0, 60, 6):
        p.line(x - 10 + i, y + 18 - i // 2, x + 56, y - 14, dimr(WINE, 0.1)[0]) if i % 12 == 0 else None
    p.line(x - 10, y + 18, x + 56, y - 14, dimr(WINE, 0.1)[3])
    p.rect(x + 40, y + 34, 32, 26, FLAME[3])
    p.rect(x + 46, y + 40, 20, 16, FLAME[4])
    p.frame(x + 38, y + 32, 36, 30, OAK[0])
    p.vline(x + 56, y + 32, 30, OAK[0])
    p.hline(x + 38, y + 47, 36, OAK[0])
    pool(p, x + 56, y + 60, 90, 0.6)
    p.rect(x + 8, y + 52, 22, 36, OAK[0])                                           # a door
    p.rect(x + 8, y + 52, 3, 36, OAK[2])


def midden() -> Image.Image:
    p = Pix(W, H, seed=90)
    rng = random.Random(9001)
    # dusk sky with the first stars and a low moon
    p.gradient(0, 0, W, 330, DUSK[0], DUSK[3], 10)
    for _ in range(70):
        p.px(rng.randrange(W), rng.randrange(150), (220, 200, 170))
    p.glow(860, 90, 80, (200, 190, 200), 0.35)
    p.ellipse(844, 74, 32, 32, (230, 222, 205))
    p.ellipse(852, 80, 8, 8, (205, 195, 185))
    p.ellipse(862, 92, 6, 6, (212, 204, 192))
    # far town: gables, chimneys, a few lit windows
    x = -10
    while x < W:
        gw, gh = rng.randrange(60, 120), rng.randrange(60, 120)
        top = 290 - gh
        p.rect(x, top + 24, gw, 140, DUSK[1])
        p.poly([(x - 4, top + 26), (x + gw // 2, top - 4), (x + gw + 4, top + 26)], DUSK[0])
        if rng.random() < 0.5:
            p.rect(x + gw - 18, top - 6, 8, 20, DUSK[0])
        for wx in range(x + 10, x + gw - 14, 26):
            for wy in range(top + 36, 276, 30):
                if rng.random() < 0.18:
                    p.rect(wx, wy, 7, 9, FLAME[2])
                    p.px(wx + 1, wy + 1, FLAME[4])
        x += gw + rng.randrange(-6, 6)
    # the tower
    tx, ty = 130, 110
    masonry(p, tx, ty + 30, 96, 230, dimr(STONE, 0.45, (30, 22, 44)), course=11)
    p.poly([(tx - 10, ty + 34), (tx + 48, ty - 24), (tx + 106, ty + 34)], dimr(WINE, 0.4, (30, 22, 44))[1])
    p.line(tx - 10, ty + 34, tx + 48, ty - 24, dimr(WINE, 0.2, (30, 22, 44))[3])
    p.rect(tx + 40, ty + 80, 8, 22, FLAME[2])
    p.rect(tx + 42, ty + 84, 4, 10, FLAME[4])
    p.vline(tx + 48, ty - 40, 18, IRON[1])
    p.poly([(tx + 48, ty - 40), (tx + 66, ty - 36), (tx + 48, ty - 31)], WINE[3])
    p.dither(tx, ty + 30, 96, 230, DUSK[0], 0.35)
    # the town wall behind the heap, with its battlements
    masonry(p, 0, 296, W, 110, dimr(STONE, 0.35, (34, 24, 40)), course=12)
    for xx in range(0, W, 36):
        p.rect(xx + 4, 280, 24, 18, dimr(STONE, 0.3, (34, 24, 40))[2])
        p.hline(xx + 4, 280, 24, dimr(STONE, 0.2, (34, 24, 40))[4])
        p.vline(xx + 27, 280, 18, dimr(STONE, 0.3, (34, 24, 40))[0])
    p.dither(0, 280, W, 130, DUSK[0], 0.3)
    shadow_under(p, 0, 296, W, 6)
    # the ground
    p.rect(0, 400, W, 140, WOOD[0])
    p.gradient(0, 400, W, 140, mix(WOOD[1][:3], DUSK[1], 0.4), SOOT[0], 8)
    for _ in range(900):
        p.px(rng.randrange(W), 400 + rng.randrange(140), rng.choice((WOOD[2], WOOD[0], STONE[1])))
    # puddles
    for x, y, w2, h2 in ((470, 500, 120, 18), (120, 510, 90, 14), (720, 470, 70, 10)):
        p.ellipse(x, y, w2, h2, DUSK[2])
        p.ellipse(x + 3, y + 2, w2 - 6, h2 - 4, DUSK[3])
        p.hline(x + 12, y + h2 // 2, w2 // 2, (230, 222, 205))
    # the heap
    p.poly(MOUND + [(960, 486), (0, 486)], WOOD[0])
    p.poly(MOUND + [(960, 480), (0, 480)], mix(WOOD[1][:3], DUSK[1], 0.3))
    grit = Pix(W, H, seed=4)
    grit.speckle(0, 200, W, 290, (WOOD[2], WOOD[0], STONE[1]), 0.3)
    grit.clip(MOUND + [(960, 480), (0, 480)])
    p.paste(grit, 0, 0)
    items = []
    for _ in range(900):
        x = rng.randrange(10, 950)
        y = rng.randrange(mound_top(x) + 6, 488) if mound_top(x) < 480 else 480
        items.append((y, x))
    for y, x in sorted(items):
        k = 0.55 - min(0.5, (y - 200) / 500)
        kind = rng.choice(("barrel", "sack", "sack", "rag", "stone", "plank", "plank", "stone", "stone", "cabbage", "bone", "straw", "rag", "crate", "cabbage"))
        s = rng.randrange(16, 46)
        if kind == "barrel":
            barrel(p, x, y, s, k)
        elif kind == "sack":
            sack(p, x, y, s, k + 0.1, rng.choice((LINEN, PALE_WOOD, LEATHER)))
        elif kind == "plank":
            a = rng.choice((-1, 1)) * rng.randrange(6, 40)
            ln = rng.randrange(30, 70)
            r2 = dimr(PALE_WOOD, k + 0.15)
            p.poly([(x, y), (x + ln, y - a), (x + ln, y - a + 5), (x, y + 5)], r2[2])
            p.line(x, y, x + ln, y - a, r2[4])
            p.line(x, y + 5, x + ln, y - a + 5, r2[0])
        elif kind == "stone":
            blob(p, x, y, s + 6, s, dimr(STONE, k))
        elif kind == "cabbage":
            blob(p, x, y, s // 2 + 6, s // 2 + 4, dimr(MOSS, k))
        elif kind == "bone":
            p.line(x, y, x + 12, y - 4, dimr(LINEN, k)[3])
            p.px(x - 1, y - 1, dimr(LINEN, k)[3])
            p.px(x + 13, y - 5, dimr(LINEN, k)[3])
        elif kind == "straw":
            for _ in range(5):
                dx = rng.randrange(-8, 8)
                p.line(x, y, x + dx, y - rng.randrange(4, 12), dimr(BRASS, k + 0.2)[2])
        elif kind == "rag":
            p.poly([(x, y), (x + 20, y - 4), (x + 16, y + 8), (x + 4, y + 10)], dimr(WINE, k)[2])
        else:
            crate(p, x, y, s, k, MOSS)
    p.dither(0, 200, W, 320, SOOT[0], 0.15)
    for i in range(len(MOUND) - 1):
        (xa, ya), (xb, yb) = MOUND[i], MOUND[i + 1]
        p.line(xa, ya, xb, yb, (150, 112, 96))
        p.line(xa, ya + 1, xb, yb + 1, (96, 66, 70))
    midden_cart(p)
    lean_to(p, 700, 322)
    # lantern on a post by the cart
    p.rect(612, 280, 4, 190, OAK[1])
    p.rect(606, 270, 16, 20, IRON[1])
    p.rect(608, 273, 12, 13, FLAME[3])
    p.rect(611, 276, 6, 7, FLAME[4])
    pool(p, 614, 280, 120, 0.7)
    # foreground right: the stone parapet and its post and rail
    cap = [(760, 396), (960, 420), (960, 448), (766, 420)]
    face = Pix(W, H, seed=3)
    masonry(face, 760, 396, 200, 150, dimr(STONE, 0.1, (40, 28, 40)), course=15)
    face.clip([(760, 410), (960, 436), (960, 540), (790, 540)])
    p.paste(face, 0, 0)
    p.poly(cap, STONE[3])
    p.line(760, 396, 960, 420, STONE[4])
    p.line(766, 420, 960, 448, STONE[1])
    for i in range(8):
        p.vline(780 + i * 24, 400 + i * 3, 24, STONE[2])
    p.dither(760, 430, 200, 110, SOOT[0], 0.25)
    # foreground left: a fence of posts and rails
    for x in (14, 120, 226):
        p.rect(x, 380 + x // 20, 14, 130, OAK[2])
        p.vline(x, 380 + x // 20, 130, OAK[3])
        p.vline(x + 13, 380 + x // 20, 130, OAK[0])
        p.rect(x - 1, 376 + x // 20, 16, 6, OAK[3])
    for y in (410, 450):
        strip(p, 0, y, 240, y + 12, 8, OAK)
    p.dither(0, 380, 250, 160, SOOT[0], 0.3)
    vignette(p, 0, 0, W, H, 42, 0.3)
    return p.finish()


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "dumping_ground.960x540.png": midden,
    "commissary.960x540.png": commissary,
    "drjackson.960x540.png": lambda: drjackson(1),
    "drjackson2.960x540.png": lambda: drjackson(2),
}
