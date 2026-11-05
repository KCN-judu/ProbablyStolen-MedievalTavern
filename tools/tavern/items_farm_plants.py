"""Garden plants of the farm sprites: seed packets, mushrooms, cabbage, reeds, cotton, vines, tubers, and the garden gear."""

from __future__ import annotations

import math

from PIL import Image

from itemkit_farm import (
    BONE, BRASSR, BROWN, CLAY, CREAM, IRONR, LEAF, LEAF_DK, LEAF_YEL, LINEN_R, OAKR, PALER, PEWTER, PURPLE, RED, SOIL, STRAW,
    TEAL, WINER, WAX_RED, Shape, box, edge, ell, flat, grow, line_set, mk, only, part, poly, shade, shift, stroke, tube,
)
from palette import BRASS, FLAME, GLASS, IRON, SHADOW, STONE, WOOD
from pix import Pix, mix, rgb

HI = rgb("#fff0c0")


# ---------------------------------------------------------------------- small helpers

def leaf(p: Pix, x0: float, y0: float, x1: float, y1: float, wd: float, ramp, vein: bool = True, outline: bool = True) -> Shape:
    """A pointed leaf from its stalk (x0, y0) to its tip (x1, y1), `wd` wide, with a pale midrib."""
    knots = []
    n = 8
    for i in range(n + 1):
        t = i / n
        r = max(0.5, wd / 2 * math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.7)
        knots.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r))
    s = tube(knots)
    part(p, s, ramp, outline=SHADOW if outline else None, grad=0.6)
    if vein and wd >= 4:
        v = line_set(x0, y0, x0 + (x1 - x0) * 0.85, y0 + (y1 - y0) * 0.85)
        stroke(p, v, ramp[4], s)
    return s


def soil(p: Pix, cx: int, y: int, w: int, water: bool = False) -> None:
    """A low mound of earth with pebbles; `y` is the bottom row."""
    s = ell(cx, y - 1, w / 2, 3) & {(x, yy) for x in range(cx - w, cx + w) for yy in range(y - 6, y + 1)}
    part(p, s, SOIL, 2, grad=0.5)
    for k in range(w // 4):
        p.px(cx - w // 2 + 2 + k * 4 + (k % 2), y - 1 - (k % 2), SOIL[4])
    if water:
        for dx in (-w // 2 + 1, w // 2 - 3):
            p.hline(cx + dx, y + 1, 2, rgb("#4f7c8c"))


def packet_base(p: Pix, band: tuple) -> None:
    s = box(2, 2, 12, 13)
    part(p, s, LINEN_R, 3, grad=0.5)
    p.hline(2, 3, 12, LINEN_R[1])
    for x in range(2, 14, 2):                        # torn, folded top edge
        p.px(x, 2, SHADOW)
        p.px(x + 1, 3, LINEN_R[2])
    p.hline(2, 12, 12, band[2])
    p.hline(2, 13, 12, band[1])
    p.vline(2, 4, 8, mix(LINEN_R[4], (255, 255, 255), 0.0))


def emblem(p: Pix, rows: list[str], legend: dict[str, tuple], x: int, y: int) -> None:
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in legend:
                p.px(x + i, y + j, legend[ch])


G, g, Y = LEAF[3], LEAF[1], LEAF_YEL[3]
EMBLEMS = {
    "grape": (["..gg....", ".pppp...", "pphpp...", ".pppp...", "..ppp...", "...p...."], {"g": g, "p": PURPLE[1], "h": PURPLE[4]}),
    "cap": (["..kkkk..", ".kkhkkk.", "kkkkkkkk", "..ssss..", "...ss...", "..ssss.."], {"k": RED[2], "h": RED[4], "s": CREAM[3]}),
    "cabbage": (["..gGg...", ".gGhGg..", "gGGhGGg.", "gGhGhGg.", ".gGhGg..", "..ggg..."], {"g": g, "G": G, "h": CREAM[4]}),
    "reed": (["..b.b...", "..b.bb..", ".bb.b...", ".b.bb...", ".b.b.b..", "bb.b.bb."], {"b": TEAL[2]}),
    "cotton": (["..h.h...", ".hHhHh..", "hHhHhHh.", ".hHhHh..", "..gGg...", "..g.g..."], {"h": CREAM[4], "H": CREAM[2], "g": g, "G": G}),
    "tuber": (["...gg...", "..g.gg..", ".pppppp.", "pPpppppp", "pppppppp", ".pppppp."], {"g": g, "p": PURPLE[2], "P": PURPLE[4]}),
}


def seed_packet(name: str, band, star: bool = False) -> Image.Image:
    p = Pix(16, 16, seed=3)
    packet_base(p, band)
    rows, leg = EMBLEMS[name]
    emblem(p, rows, leg, 4, 5)
    if star:
        for x, y in ((11, 3), (10, 4), (11, 4), (12, 4), (11, 5)):
            p.px(x, y, BRASS[3])
        p.px(11, 4, BRASS[4])
    edge(p, box(2, 2, 12, 13))
    for x in range(2, 14, 2):                        # re-cut the notches into the outline
        p.px(x, 1, SHADOW)
    return p.im


# ---------------------------------------------------------------------- mushrooms

def mushroom(p: Pix, cx: float, by: int, cw: int, ch: int, sh: int, sw: int, cap, stem, spots: list[tuple[float, float]] = (),
             lean: float = 0.0, gill: bool = True) -> None:
    """One toadstool: stem, then a domed cap with gills under its rim. Spots are (u, v) in cap fractions."""
    cy = by - sh
    st = tube([(cx + lean, cy, sw / 2), (cx + lean * 0.4, cy + sh * 0.5, sw / 2 - 0.2), (cx, by - 1, sw / 2 + 0.9)])
    part(p, st, stem, 2, grad=0.5)
    dome = {(x, y) for x, y in ell(cx + lean, cy, cw / 2, ch) if y <= cy}
    under = {(x, y) for x, y in ell(cx + lean, cy, cw / 2 - 0.5, 1.6) if cy <= y <= cy + 1}
    part(p, under, [cap[0], cap[0], cap[1], cap[1], cap[2]], 1, grad=0.0)
    part(p, dome, cap, 2, grad=1.1)
    if gill:
        for x in range(int(cx + lean - cw / 2 + 2), int(cx + lean + cw / 2 - 1), 2):
            if (x, cy) in under:
                p.px(x, cy, cap[0])
    for u, v in spots:
        sx, sy = round(cx + lean + (u - 0.5) * cw), round(cy - v * ch)
        if (sx, sy) in dome:
            p.px(sx, sy, stem[4])
            if cw >= 12:
                p.px(sx + 1, sy, stem[3])
    # lit crescent on the upper-left of the dome
    for x, y in dome:
        if (x - 1, y - 1) not in dome and x < cx + lean:
            p.px(x, y, cap[4])


MUSH = {
    "meal": (mk("#a8703c"), mk("#d8c3a0"), [(0.3, 0.6), (0.62, 0.45)]),
    "dream": (mk("#7a62a8"), mk("#d4cbe0"), [(0.25, 0.5), (0.55, 0.7), (0.75, 0.35)]),
    "night": (mk("#9c2e30"), mk("#cfc6b6"), [(0.22, 0.45), (0.5, 0.75), (0.76, 0.4), (0.4, 0.3)]),
}


def mush_small(kind: str) -> Image.Image:
    p = Pix(16, 16, seed=5)
    cap, stem, sp = MUSH[kind]
    mushroom(p, 8, 14, 11, 6, 5, 3, cap, stem, sp)
    return p.im


def mush_tall(kind: str) -> Image.Image:
    p = Pix(16, 32, seed=5)
    cap, stem, sp = MUSH[kind]
    mushroom(p, 7.5, 29, 12, 6, 16, 3, cap, stem, sp, lean=1.0)
    return p.im


def mush_large(kind: str) -> Image.Image:
    p = Pix(32, 32, seed=5)
    cap, stem, sp = MUSH[kind]
    mushroom(p, 15, 30, 27, 12, 14, 6, cap, stem, sp)
    return p.im


def mush_patch(kind: str) -> Image.Image:
    p = Pix(48, 64, seed=7)
    cap, stem, sp = MUSH[kind]
    soil(p, 24, 47, 30, water=True)
    mushroom(p, 33, 44, 15, 8, 10, 3, cap, stem, sp, lean=1)
    mushroom(p, 10, 44, 16, 9, 14, 4, cap, stem, sp, lean=-1)
    mushroom(p, 21, 45, 22, 12, 19, 5, cap, stem, sp, lean=-1)
    mushroom(p, 38, 46, 11, 6, 7, 3, cap, stem, sp[:2])
    mushroom(p, 28, 46, 16, 9, 7, 4, cap, stem, sp)
    return p.im


# ---------------------------------------------------------------------- cabbage (fillerweed)

def cabbage_head(p: Pix, cx: int, by: int, rx: int, ry: int, tall: bool = False) -> None:
    for k, (dx, ang) in enumerate(((-0.9, -0.9), (0.9, 0.9), (-0.5, -0.45), (0.5, 0.45))):
        leaf(p, cx + dx * rx * 0.2, by - 1, cx + dx * rx * 1.15, by - ry * 1.3 + abs(dx) * 3, rx * 0.95, LEAF_DK if k < 2 else LEAF, True)
    head = ell(cx, by - ry, rx * 0.72, ry * (1.0 if tall else 0.88))
    part(p, head, LEAF_YEL, 2, grad=1.0, dith=True)
    # curled leaf creases and the pale ribs
    for i in range(-1, 2):
        stroke(p, line_set(cx + i * 2 - 1, by - ry * 1.9 + abs(i), cx + i * 3, by - 2), LEAF_YEL[4], head)
    stroke(p, line_set(cx - rx * 0.6, by - ry * 1.2, cx, by - ry * 0.9), LEAF_YEL[1], head)
    stroke(p, line_set(cx + 1, by - ry * 1.0, cx + rx * 0.6, by - ry * 1.3), LEAF_YEL[1], head)


def cabbage_16(tall: bool) -> Image.Image:
    p = Pix(16, 32 if tall else 16, seed=2)
    if tall:
        cabbage_head(p, 8, 30, 6, 13, True)
    else:
        cabbage_head(p, 8, 14, 4, 5)
    return p.im


def cabbage_32() -> Image.Image:
    p = Pix(32, 32, seed=2)
    cabbage_head(p, 15, 30, 11, 15)
    return p.im


def cabbage_plant() -> Image.Image:
    p = Pix(48, 64, seed=9)
    soil(p, 24, 47, 36)
    ang = [(-22, 22, 4), (22, 20, 4), (-14, 12, 3), (15, 11, 3), (-6, 9, 2), (6, 9, 2)]
    for ex, ey, k in ang:
        leaf(p, 24 + ex * 0.2, 44, 24 + ex, 44 - ey - 8, 15, LEAF_DK if abs(ex) > 14 else LEAF, True)
    for ex, ey in ((-12, 14), (12, 14), (0, 20)):
        leaf(p, 24 + ex * 0.2, 44, 24 + ex * 0.8, 44 - ey - 6, 13, LEAF if ex else LEAF_YEL, True)
    head = ell(24, 34, 9, 9)
    part(p, head, LEAF_YEL, 2, grad=1.0, dith=True)
    for i in range(-2, 3):
        stroke(p, line_set(24 + i * 2, 26, 24 + i * 3, 41), LEAF_YEL[4] if i % 2 else LEAF_YEL[1], head)
    return p.im


# ---------------------------------------------------------------------- reeds

def reed_blades(p: Pix, cx: int, by: int, h: int, spread: float, n: int, seed: int, heads: bool = True) -> None:
    import random
    rng = random.Random(seed)
    for i in range(n):
        t = (i / (n - 1)) * 2 - 1
        top_x = cx + t * spread + rng.uniform(-2, 2)
        top_y = by - h * (0.55 + 0.45 * (1 - abs(t) ** 1.5)) + rng.uniform(-2, 2)
        mid = (cx + t * spread * 0.45, (by + top_y) / 2)
        knots = [(cx + t * 2, by, 1.5), (mid[0], mid[1], 1.2), (top_x, top_y, 0.6)]
        s = tube(knots)
        ramp = [LEAF_DK, TEAL, LEAF][i % 3]
        part(p, s, ramp, 2, grad=0.4)
        stroke(p, line_set(cx + t * 2, by - 1, mid[0], mid[1]), ramp[4], s)
        if heads and i % 4 == 1:
            hd = ell(top_x, top_y - 1, 1.2, 3)
            part(p, hd, BROWN, 2, grad=0.5)


def reed_filter() -> Image.Image:
    p = Pix(16, 32, seed=4)
    for i, x in enumerate(range(1, 15, 3)):
        s = box(x, 2 + (i % 2), 3, 27 - (i % 2))
        part(p, s, [LEAF_DK, TEAL, LEAF][i % 3], 2, grad=0.4)
    for y in (9, 22):                                 # twine bands
        for x in range(0, 16):
            p.px(x, y, STRAW[2])
            p.px(x, y + 1, STRAW[0])
        p.px(5, y, STRAW[4])
        p.px(11, y, STRAW[4])
    for x in range(1, 15, 3):
        p.px(x + 1, 3, LEAF_YEL[3])
    p.outline(SHADOW)
    return p.im


def reed_plant() -> Image.Image:
    p = Pix(48, 64, seed=11)
    soil(p, 24, 47, 30, water=True)
    reed_blades(p, 24, 45, 33, 21, 13, 3)
    return p.im


# ---------------------------------------------------------------------- cotton

def boll(p: Pix, cx: int, cy: int, r: float = 3.0) -> None:
    calyx = poly([(cx - 2, cy + 1), (cx, cy + 3 + (r > 3)), (cx + 2, cy + 1)])
    part(p, calyx, BROWN, 1, grad=0.3)
    puff = ell(cx - 1, cy - 1, r - 0.5, r - 0.5) | ell(cx + 1, cy - 1, r - 0.5, r - 0.5) | ell(cx, cy, r, r - 0.7)
    part(p, puff, CREAM, 3, grad=1.0)
    p.px(cx, cy - 1, CREAM[1]) if r > 2.5 else None
    p.px(cx - 1, cy - 2, HI)


def cotton_sprout() -> Image.Image:
    p = Pix(16, 16, seed=1)
    part(p, tube([(8, 14, 1), (8, 8, 0.8)]), BROWN, 2, grad=0.1)
    leaf(p, 8, 10, 3, 5, 4, LEAF, False)
    leaf(p, 8, 10, 13, 4, 4, LEAF_DK, False)
    boll(p, 8, 5, 2.2)
    return p.im


def cotton_stalk(small: bool) -> Image.Image:
    p = Pix(16 if small else 32, 32, seed=1)
    cx = 7 if small else 14
    st = tube([(cx, 30, 1.3), (cx + 1, 20, 1), (cx, 8, 0.8)])
    part(p, st, BROWN, 2, grad=0.2)
    spec = [(-4, 14, -5, 10), (5, 18, 6, 15)] if small else [(-8, 17, -9, 12), (8, 21, 9, 15), (-4, 25, -8, 22), (4, 12, 5, 8)]
    for dx, y, ex, ey in spec:
        b = tube([(cx, y + 5, 0.8), (cx + dx * 0.6, y + 1, 0.7), (cx + ex, ey + 3, 0.6)])
        part(p, b, BROWN, 2, grad=0.1)
    for dx, y, ex, ey in spec:
        boll(p, cx + ex, ey, 3.0)
    boll(p, cx + 1, 6, 3.0)
    leaf(p, cx, 24, cx - 5 - (not small) * 3, 27, 4, LEAF, False)
    leaf(p, cx, 27, cx + 5 + (not small) * 3, 29, 4, LEAF_DK, False)
    return p.im


def cotton_bush() -> Image.Image:
    p = Pix(48, 64, seed=13)
    soil(p, 24, 47, 26)
    trunk = tube([(23, 45, 2.3), (24, 34, 1.8), (22, 24, 1.2)])
    part(p, trunk, BROWN, 2, grad=0.3)
    branches = [((23, 40), (9, 30)), ((24, 38), (38, 29)), ((22, 30), (12, 19)), ((24, 30), (35, 18)), ((22, 25), (23, 14))]
    for (a, b) in branches:
        part(p, tube([(a[0], a[1], 1.0), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 1, 0.9), (b[0], b[1], 0.6)]), BROWN, 2, grad=0.1)
    for (a, b) in branches:
        leaf(p, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[0] + b[0]) / 2 - 5, (a[1] + b[1]) / 2 + 2, 5, LEAF_DK, False)
        leaf(p, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[0] + b[0]) / 2 + 5, (a[1] + b[1]) / 2 + 2, 5, LEAF, False)
    for (a, b) in branches:
        boll(p, b[0], b[1], 3.4)
        boll(p, (a[0] + b[0]) // 2 + 3, (a[1] + b[1]) // 2 - 4, 3.0)
    boll(p, 17, 36, 3.0)
    boll(p, 30, 36, 3.0)
    return p.im


# ---------------------------------------------------------------------- vine and berry bush

def wood_trunk(p: Pix, pts, ramp=BROWN) -> Shape:
    s = tube(pts)
    part(p, s, ramp, 2, grad=0.4)
    for x, y in sorted(s):
        if (x + 2 * y) % 5 == 0 and (x - 1, y) in s and (x + 1, y) in s:
            p.px(x, y, ramp[1])
    return s


def vine_leaf(p: Pix, cx: float, cy: float, r: float, ramp) -> None:
    s = ell(cx, cy, r, r * 0.85)
    for a in range(0, 360, 72):                    # notches give the five-lobed outline
        s -= {(round(cx + math.cos(math.radians(a + 36)) * r), round(cy + math.sin(math.radians(a + 36)) * r * 0.85))}
    part(p, s, ramp, 2, grad=0.8)
    stroke(p, line_set(cx - r * 0.6, cy + r * 0.5, cx + r * 0.6, cy - r * 0.4), ramp[4], s)
    stroke(p, line_set(cx, cy, cx + 1, cy + r * 0.8), ramp[1], s)


def grapes(p: Pix, cx: int, top: int, rows: int, ramp, r: float = 2.0) -> None:
    for j in range(rows):
        n = max(1, rows - j - (0 if j else 1) + 1)
        width = (rows - j)
        for i in range(width):
            x = cx - (width - 1) * r + i * 2 * r
            y = top + j * r * 1.7
            s = ell(x, y, r, r)
            part(p, s, ramp, 2, grad=0.6)
            p.px(round(x - 0.5), round(y - 0.5), ramp[4])


def vine_bush(fruit: bool) -> Image.Image:
    p = Pix(48, 64, seed=17)
    sx, sy = 0.8, 0.76

    def T(x: float, y: float) -> tuple[float, float]:
        return 24 + (x - 24) * sx, 47 - (47 - y) * sy

    soil(p, 24, 47, 18)
    pts = [T(22, 46), T(20, 38), T(24, 30), T(21, 24)]
    wood_trunk(p, [(pts[0][0], pts[0][1], 2.6), (pts[1][0], pts[1][1], 2.1), (pts[2][0], pts[2][1], 1.6), (pts[3][0], pts[3][1], 1.2)])
    for a_, b_ in (((21, 36), (8, 28)), ((23, 32), (37, 26)), ((22, 26), (14, 17)), ((22, 25), (30, 16))):
        a2, b2 = T(*a_), T(*b_)
        wood_trunk(p, [(a2[0], a2[1], 1.3), ((a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2 - 2, 1.0), (b2[0], b2[1], 0.8)])
    for (x, y, r, k) in ((7, 26, 6, 1), (38, 24, 6, 0), (14, 16, 6, 0), (30, 15, 6, 1), (23, 20, 5, 0), (11, 36, 5, 0), (34, 36, 5, 1)):
        tx, ty = T(x, y)
        vine_leaf(p, tx, ty, r * 0.82, LEAF if k else LEAF_DK)
    for (x, y, r, k) in ((7, 24, 4, 0), (37, 22, 4, 1), (15, 15, 4, 1), (29, 14, 3, 0)):
        tx, ty = T(x, y)
        vine_leaf(p, tx, ty, r * 0.85, LEAF_YEL if k else LEAF)
    if fruit:
        for cx, top, rows in ((10, 31, 3), (35, 30, 3), (19, 23, 3), (28, 22, 2), (25, 33, 3)):
            tx, ty = T(cx, top)
            grapes(p, round(tx), round(ty), rows, PURPLE, 1.9)
    else:
        for x, y in ((8, 32), (35, 31), (20, 25), (28, 23), (26, 34)):                  # green flower buds
            tx, ty = T(x, y)
            tx, ty = round(tx), round(ty)
            for dx, dy in ((0, 0), (2, 1), (1, 3), (-1, 2)):
                p.px(tx + dx, ty + dy, LEAF_YEL[3])
            p.px(tx, ty + 1, LEAF_YEL[4])
    return p.im


def coffee_bush() -> Image.Image:
    p = Pix(48, 64, seed=19)
    soil(p, 24, 47, 20, water=True)
    wood_trunk(p, [(24, 46, 2.6), (24, 40, 2.0), (23, 34, 1.5)])
    import random
    rng = random.Random(8)
    blobs = [(24, 26, 11, 7, 0), (12, 30, 9, 6, 1), (36, 31, 9, 6, 1), (18, 21, 9, 6, 0), (31, 20, 9, 6, 0), (24, 17, 8, 5, 0)]
    for cx, cy, rx, ry, k in blobs:
        s = ell(cx, cy, rx, ry)
        part(p, s, LEAF_DK if k else LEAF, 2, grad=1.0, dith=True)
        for _ in range(7):                        # leaf glints
            x, y = round(cx + rng.uniform(-rx, rx) * 0.7), round(cy + rng.uniform(-ry, ry) * 0.7)
            if (x, y) in s:
                p.hline(x, y, 2, LEAF[4])
                p.px(x + 1, y + 1, LEAF[1])
    for x, y in ((13, 29), (20, 32), (30, 33), (36, 29), (24, 24), (16, 20), (31, 18), (26, 30), (9, 33), (39, 33), (21, 15), (33, 25)):
        part(p, box(x, y, 3, 3) - {(x + 2, y), (x, y + 2)}, RED, 2, grad=0.6)
        p.px(x + 1, y, HI)
    return p.im


# ---------------------------------------------------------------------- tubers (nutrifruit)

def tuber_shape(cx: float, cy: float, rx: float, ry: float, lump: float = 0.3) -> Shape:
    s = ell(cx, cy, rx, ry) | ell(cx + rx * 0.3, cy - ry * 0.15, rx * 0.8, ry * 0.9) | ell(cx - rx * 0.35, cy + ry * 0.2, rx * 0.75, ry * 0.85)
    return s


def tuber(p: Pix, cx: float, cy: float, rx: float, ry: float, ramp=PURPLE, eyes: int = 3, sprout: bool = False) -> Shape:
    s = tuber_shape(cx, cy, rx, ry)
    part(p, s, ramp, 2, grad=1.1)
    for i in range(eyes):
        x = round(cx - rx * 0.3 + i * rx * 0.35)
        y = round(cy + ((i * 5) % 3 - 1) * ry * 0.35)
        if (x, y) in s:
            p.px(x, y, ramp[0])
            p.px(x - 1, y - 1, ramp[3]) if (x - 1, y - 1) in s else None
    if rx > 5:
        for k in range(int(rx // 4)):                # dusty speckle on the skin
            x, y = round(cx + (k * 3 - rx * 0.4)), round(cy - ry * 0.4 + (k * 2) % int(ry))
            if (x, y) in s:
                p.px(x, y, ramp[1])
    p.px(round(cx - rx * 0.45), round(cy - ry * 0.5), ramp[4])
    if sprout:
        leaf(p, cx + rx * 0.4, cy - ry * 0.8, cx + rx * 0.9, cy - ry * 1.3, 3, LEAF, False)
    return s


FLESH_Y = mk("#e0a64a")


def tuber_cut(p: Pix, cx: float, cy: float, rx: float, ry: float) -> None:
    s = tuber_shape(cx, cy, rx, ry)
    part(p, s, PURPLE, 2, grad=0.8)
    inner = ell(cx + 1, cy, rx - 2, ry - 2)
    part(p, inner, FLESH_Y, 3, outline=PURPLE[0], grad=1.0)
    for dx, dy in ((-2, -1), (1, 2), (2, -2)):
        p.px(round(cx + dx), round(cy + dy), FLESH_Y[1])


def tuber_s() -> Image.Image:
    p = Pix(16, 16, seed=1)
    tuber(p, 8, 9, 5, 4.5, eyes=2, sprout=True)
    return p.im


def tubers_pair() -> Image.Image:
    p = Pix(32, 32, seed=1)
    tuber(p, 11, 17, 9, 8, eyes=3)
    tuber_cut(p, 22, 14, 8, 8)
    return p.im


def tuber_large() -> Image.Image:
    p = Pix(32, 32, seed=1)
    tuber(p, 15, 17, 12.5, 11.5, eyes=4, sprout=True)
    return p.im


def tuber_xl() -> Image.Image:
    p = Pix(48, 48, seed=1)
    s = tuber(p, 23, 25, 19.5, 18, eyes=5)
    for x, y, w in ((12, 14, 4), (27, 31, 5), (30, 16, 3), (16, 31, 3)):                # moss patches on the old skin
        flat(p, {(i, y) for i in range(x, x + w)} & s, LEAF[1])
        flat(p, {(i, y - 1) for i in range(x + 1, x + w)} & s, LEAF[2])
    leaf(p, 30, 10, 38, 5, 6, LEAF, True)
    leaf(p, 29, 11, 33, 3, 5, LEAF_DK, False)
    return p.im


def tuber_plant() -> Image.Image:
    p = Pix(48, 64, seed=21)
    soil(p, 24, 47, 36, water=True)
    for x, y, rx, ry in ((13, 43, 5, 3.5), (34, 43, 5, 3.5), (24, 44, 7, 4)):
        tuber(p, x, y, rx, ry, eyes=2)
    stem = tube([(24, 40, 1.2), (24, 28, 1.0), (25, 18, 0.8)])
    part(p, stem, LEAF_DK, 2, grad=0.2)
    for x0, y0, x1, y1, k in ((24, 36, 10, 30, 1), (24, 34, 38, 28, 0), (24, 29, 12, 21, 0), (24, 26, 37, 19, 1), (24, 22, 17, 13, 1), (25, 20, 33, 12, 0)):
        leaf(p, x0, y0, x1, y1, 8, TEAL if k else LEAF, True)
    for fx, fy in ((25, 14),):
        for dx, dy in ((0, -2), (2, -1), (2, 1), (-2, -1), (-2, 1), (0, 2)):
            p.px(fx + dx, fy + dy, rgb("#e6a0b8"))
        for dx, dy in ((0, 0), (1, 0), (0, -1), (-1, 0), (0, 1)):
            p.px(fx + dx, fy + dy, rgb("#f4d070") if (dx, dy) == (0, 0) else rgb("#f2c6d2"))
    return p.im


def tuber_sack() -> Image.Image:
    p = Pix(32, 32, seed=1)
    body = poly([(5, 9), (25, 9), (28, 30), (3, 30)]) | ell(15.5, 29, 12.5, 2)
    part(p, body, mk("#b89c66"), 2, grad=0.8, dith=True)
    mouth = poly([(6, 7), (24, 7), (25, 10), (5, 10)]) | ell(15, 6, 9, 3)
    part(p, mouth, mk("#b89c66"), 3, grad=0.4)
    for x in range(7, 24, 2):                              # gathered top
        p.vline(x, 4, 5, mk("#b89c66")[1])
    p.hline(6, 11, 19, STRAW[0])                          # string
    p.hline(6, 12, 19, STRAW[2])
    flat(p, {(14, 12), (15, 13), (13, 13), (14, 14), (16, 14)}, STRAW[3])
    label = box(9, 16, 14, 11)
    part(p, label, LINEN_R, 3, grad=0.3, outline=SHADOW)
    tuber(p, 15, 22, 5, 3.5, eyes=2)
    return p.im


def nutrient_tablet() -> Image.Image:
    p = Pix(16, 16, seed=1)
    s = ell(7.5, 8, 6.5, 4.2) | ell(8, 7, 6, 4)
    part(p, s, LEAF, 2, grad=1.0)
    stroke(p, line_set(3, 8, 12, 8), LEAF[1], s)
    p.px(5, 5, LEAF[4])
    p.px(6, 5, LEAF[4])
    p.px(9, 11, LEAF[0])
    return p.im


def nutrient_jar() -> Image.Image:
    p = Pix(16, 32, seed=1)
    jar = box(2, 10, 12, 17) | ell(8, 26, 6, 2)
    part(p, jar, mk("#9aa58c"), 2, grad=0.7)
    pills = ell(8, 22, 5, 3)
    for k, (x, y) in enumerate(((5, 22), (8, 21), (10, 23), (7, 24), (6, 19), (10, 19))):
        part(p, ell(x, y, 1.8, 1.4), LEAF, 2, outline=None, grad=0.4)
        p.px(x - 1, y - 1, LEAF[4])
    lab = box(3, 12, 10, 5)
    part(p, lab, LINEN_R, 3, grad=0.2, outline=SHADOW)
    stroke(p, line_set(5, 14, 10, 14), LEAF[2])
    p.px(7, 13, LEAF[1]), p.px(8, 15, LEAF[1])
    p.vline(3, 11, 14, mk("#9aa58c")[4])                        # glass sheen
    cork = box(3, 6, 10, 4)
    part(p, cork, PALER, 2, grad=0.8)
    for x in (5, 8, 10):
        p.px(x, 7, PALER[1])
    return p.im


def plant_frame() -> Image.Image:
    """A hand-lens in a moss-green wooden frame on small feet: the analyser."""
    p = Pix(32, 48, seed=1)
    frame = box(4, 6, 24, 34) | box(7, 4, 18, 2)
    part(p, frame, mk("#4e7040"), 2, grad=0.9)
    glass = box(8, 10, 16, 25)
    part(p, glass, GLASS, 1, outline=SHADOW, grad=0.6)
    flat(p, {(x, y) for x, y in glass if (x - 8) + (y - 10) in (4, 5, 12, 13)}, GLASS[2])
    p.vline(9, 12, 7, GLASS[4])
    p.hline(10, 11, 4, GLASS[3])
    for x, y in ((6, 8), (25, 8), (6, 37), (25, 37)):
        p.px(x, y, BRASS[3])
        p.px(x + 1, y, BRASS[1])
    for x in (7, 22):
        part(p, box(x, 39, 4, 1), OAKR, 1, outline=SHADOW)
    p.px(14, 38, BRASS[3])
    part(p, box(11, 36, 10, 2), BRASSR, 2, grad=0.5)
    return p.im


# ---------------------------------------------------------------------- hydroponic tower

def tower(on: bool) -> Image.Image:
    """A garden stand: planting tray, stone pillar with iron hoops, and a water cistern with a brass tap."""
    p = Pix(48, 64, seed=23)
    # cistern at the foot
    cist = box(2, 47, 44, 16) | ell(24, 62, 22, 2)
    part(p, cist, mk("#6a645c"), 2, grad=0.8)
    for x in range(4, 44, 8):
        p.vline(x, 53, 9, mk("#6a645c")[1])
    for y in (56, 60):
        for x in range(2, 46, 8):
            p.hline(x + (y == 60) * 4, y, 8, mk("#6a645c")[1]) if False else None
    water = box(6, 49, 36, 5)
    wr = mk("#3e8a86") if on else mk("#2d4a50")
    part(p, water, wr, 2, outline=SHADOW, grad=0.4)
    if on:
        for x in (10, 18, 27, 34):
            p.hline(x, 50, 4, wr[4])
        for x in (14, 30):
            p.hline(x, 52, 3, wr[3])
    else:
        p.hline(10, 50, 5, wr[3])
        p.hline(28, 51, 4, wr[3])
    p.hline(2, 55, 44, IRON[2])
    p.hline(2, 56, 44, IRON[1])
    for x in (5, 14, 24, 33, 42):
        p.px(x, 55, BRASS[3 if on else 2])
    tap = box(38, 58, 6, 3)
    part(p, tap, BRASSR, 2, grad=0.5)
    # pillar
    pil = box(11, 14, 26, 34)
    part(p, pil, mk("#7a736a"), 2, grad=0.9)
    for y in range(18, 46, 6):
        p.hline(11, y, 26, IRON[1])
        p.hline(11, y + 1, 26, IRON[3] if on else IRON[2])
        for x in (13, 34):
            p.px(x, y, BRASS[3 if on else 1])
    for y in range(15, 47, 6):
        for x in range(13 + (y // 6 % 2) * 4, 36, 8):
            p.vline(x, y, 2, mk("#7a736a")[1])
    edge(p, pil)
    # planting tray
    tray = ell(24, 9, 22.5, 7.5)
    part(p, tray, OAKR, 2, grad=0.9)
    bed = ell(24, 8, 19, 5)
    part(p, bed, SOIL, 1, grad=0.5)
    if on:
        for x, y in ((12, 7), (20, 5), (29, 6), (36, 8), (24, 9), (16, 10)):
            p.px(x, y, LEAF[3])
            p.px(x, y - 1, LEAF[2])
            p.px(x + 1, y - 2, LEAF_YEL[3])
            p.px(x - 1, y - 2, LEAF_YEL[3])
    else:
        for x, y in ((12, 7), (20, 5), (29, 6), (36, 8)):
            p.px(x, y, SOIL[3])
    p.hline(5, 12, 38, OAKR[1])
    return p.im


# ---------------------------------------------------------------------- scrolls (the tablets of the old data)

RIBBONS = {
    "black": mk("#35323d"), "blue": mk("#4a7cb0"), "green": mk("#4f8a45"), "orange": mk("#d0782c"), "purple": mk("#8a4a9c"),
    "red": mk("#b8322e"),
}


def scroll(color: str, full: bool) -> Image.Image:
    p = Pix(32, 16, seed=2)
    rb = RIBBONS[color]
    body = box(6, 3, 18, 11)
    part(p, body, mk("#dccb9e"), 3, grad=0.6)
    for y in (6, 8, 10):                                     # script lines
        if full:
            for x in range(8, 15, 2):
                p.hline(x, y, 1 + (x + y) % 2, mk("#6a5a40")[2])
        else:
            pass
    left = box(3, 2, 4, 13)
    right = box(23, 2, 4, 13)
    for s in (left, right):
        part(p, s, OAKR, 2, grad=0.8)
    for s in (box(2, 1, 6, 2), box(2, 14, 6, 1), box(22, 1, 6, 2), box(22, 14, 6, 1)):
        pass
    p.px(4, 2, BRASS[3]), p.px(25, 2, BRASS[3])
    p.vline(4, 4, 8, OAKR[4])
    p.vline(24, 4, 8, OAKR[4])
    band = box(14, 3, 4, 11)
    part(p, band, rb, 2, grad=0.8)
    p.px(14, 3, rb[4])
    if full:
        seal = ell(19, 11, 3, 3)
        part(p, seal, rb if color != "black" else mk("#7a2c2c"), 2, grad=1.0)
        p.px(18, 10, WARM_HI(rb)), p.px(20, 12, rb[0])
        for x in range(8, 13):
            p.px(x, 10, mk("#6a5a40")[2])
    else:
        p.vline(20, 8, 4, rb[1])
        p.px(20, 12, rb[2])
    return p.im


def WARM_HI(r):
    return r[4]


# ---------------------------------------------------------------------- alchemist's apparatus

def apparatus(working: bool) -> Image.Image:
    p = Pix(48, 48, seed=29)
    # cabinet with parchment panel and brass dials
    cab = box(3, 3, 26, 40)
    part(p, cab, WOOD, 2, grad=0.8)
    for y in (6, 40):
        p.hline(3, y, 26, WOOD[1])
    panel = box(7, 8, 18, 14)
    part(p, panel, mk("#6a4a8a") if working else mk("#3a2a50"), 2, outline=SHADOW, grad=0.4)
    if working:
        for y in (11, 14, 17):
            p.hline(9, y, 9, mk("#e0cf9f")[3])
            p.hline(9, y + 1, 4, mk("#e0cf9f")[2])
        flat(p, box(19, 11, 4, 8), FLAME[2])
        flat(p, box(20, 12, 2, 6), FLAME[4])
    else:
        p.px(9, 10, mk("#6a4a8a")[3])
        p.hline(9, 11, 3, mk("#6a4a8a")[2])
    for i, x in enumerate((9, 14, 19)):
        part(p, ell(x + 1, 28, 2.2, 2.2), BRASSR, 2, grad=0.8)
        p.px(x + 1, 27 if working else 29, SHADOW)
    p.hline(7, 33, 18, WOOD[1])
    for x in (8, 13, 18, 23):
        p.px(x, 36, BRASS[3] if working and x < 20 else IRON[3])
    # brass strap
    p.vline(4, 4, 38, WOOD[4])
    # still pot with alembic spout
    pot = ell(36, 36, 9, 8) | box(29, 28, 14, 10)
    part(p, pot, mk("#b87a38"), 2, grad=1.0)
    p.hline(30, 34, 12, mk("#b87a38")[1])
    neck = tube([(36, 28, 3), (36, 22, 2.2)])
    part(p, neck, mk("#b87a38"), 2, grad=0.8)
    spout = tube([(36, 20, 1.6), (41, 17, 1.2), (45, 22, 1.0), (45, 30, 1.0)])
    part(p, spout, mk("#b87a38"), 3, grad=0.5)
    part(p, ell(36, 19, 3.5, 2.5), mk("#b87a38"), 3, grad=0.8)
    part(p, box(41, 40, 5, 6), mk("#9aa58c"), 2, grad=0.5)
    p.px(42, 41, GLASS[4])
    if working:
        p.glow(36, 43, 8, FLAME[3], 0.7)
        for x, y in ((35, 41), (37, 40), (36, 38)):
            p.px(x, y, FLAME[3])
        for x, y in ((45, 16), (43, 12), (46, 9), (42, 7)):
            p.px(x, y, mk("#e0e0ea")[3])
            p.px(x - 1, y - 1, mk("#e0e0ea")[2])
        flat(p, {(43, 37), (44, 36)}, FLAME[4])
        flat(p, {(45, 31), (45, 33)}, LEAF[4])
    else:
        p.hline(30, 44, 12, SHADOW)
        part(p, box(33, 43, 6, 3), IRON, 2, grad=0.4)
    return p.im


def coffee_beans() -> Image.Image:
    p = Pix(16, 16, seed=1)
    cof = mk("#6a3e22")
    for x, y, a in ((3, 4, 0), (8, 3, 1), (11, 8, 0), (5, 9, 1), (9, 12, 0), (2, 12, 1), (13, 3, 1)):
        bean = ell(x + 2, y + 1.5, 2.6, 2.1)
        part(p, bean, cof, 2, grad=0.9)
        p.px(x + 2, y + 1 if a else y + 2, cof[0])                       # the crease
        p.px(x + 2, y + (2 if a else 1), cof[0])
        p.px(x + 1, y, cof[4])
    return p.im


# ---------------------------------------------------------------------- the list

PICS = {
    "bloomberry_p": lambda: vine_bush(False),
    "bloomberry_p2": lambda: vine_bush(True),
    "bloomberry_seed": lambda: seed_packet("grape", RED),
    "coffee_bean": lambda: coffee_beans(),
    "coffee_bean_p": coffee_bush,
    "dna_manipulator": lambda: apparatus(False),
    "dna_manipulator_working": lambda: apparatus(True),
    "dream_cap": lambda: mush_tall("dream"),
    "dream_cap_l": lambda: mush_large("dream"),
    "dream_cap_p": lambda: mush_patch("dream"),
    "dream_cap_s": lambda: mush_small("dream"),
    "dream_cap_seed": lambda: seed_packet("cap", PURPLE),
    "fillerweed": lambda: cabbage_16(True),
    "fillerweed_p": cabbage_plant,
    "fillerweed_s": lambda: cabbage_16(False),
    "fillerweed_seed": lambda: seed_packet("cabbage", LEAF),
    "hydroponic": lambda: tower(True),
    "hydroponic_off": lambda: tower(False),
    "hydroreed_filter": reed_filter,
    "hydroreed_p": reed_plant,
    "hydroreed_seed": lambda: seed_packet("reed", TEAL),
    "items_hydroponic_plant_1": cabbage_32,
    "kotton_fiber_p": cotton_bush,
    "kotton_plant": lambda: cotton_stalk(True),
    "kotton_plant_l": lambda: cotton_stalk(False),
    "kotton_plant_s": cotton_sprout,
    "kotton_plant_seed": lambda: seed_packet("cotton", CREAM),
    "meal_cap": lambda: mush_tall("meal"),
    "meal_cap_l": lambda: mush_large("meal"),
    "meal_cap_s": lambda: mush_small("meal"),
    "nightmare_cap": lambda: mush_tall("night"),
    "nightmare_cap_p": lambda: mush_patch("night"),
    "nutrient_tablet": nutrient_tablet,
    "nutrient_tablet_container": nutrient_jar,
    "nutrifruit": tubers_pair,
    "nutrifruit_l": tuber_large,
    "nutrifruit_modified_seed": lambda: seed_packet("tuber", BRASSR, star=True),
    "nutrifruit_p": tuber_plant,
    "nutrifruit_s": tuber_s,
    "nutrifruit_seed": lambda: seed_packet("tuber", PURPLE),
    "nutrifruit_seed_packet": tuber_sack,
    "nutrifruit_xl": tuber_xl,
    "plant_analyser": plant_frame,
}
for _color in RIBBONS:
    for _full in (False, True):
        PICS[f"dna_disk_{_color}_{'full' if _full else 'empty'}"] = (lambda c=_color, f=_full: scroll(c, f))
