"""Appraisal close-ups: the glass phial in an iron-and-brass sleeve, its wear overlays, and the four liquid colours.

The phial is the cartridge: a clear glass body (transparent here, as in the game's picture) between two ferrules.
Overlays keep the series: wear (light scuffs), heavy_wear (grime along the rims, cracked ferrules, verdigris), reinforced (two
iron rails and two hoops), screws (four rivet heads), crack1 (a split in the glass). The liquid colours are cloud banks in a
leaded frame: normal (blue-teal), high_quality (violet-rose), poor1 (ash grey), poor2 (murky green).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from PIL import Image

from appraisalkit_a import BRASS, STEEL, Mask, distance_inside, fbm, poly_mask, rect_mask, solid, stain
from palette import SHADOW, SOOT
from pix import Color, Pix, Ramp

W, H = 319, 124
IRON_D: Ramp = ((24, 20, 30), (46, 40, 52), (76, 68, 82), (110, 100, 110), (150, 140, 142), (196, 184, 170))


def ferrule(p: Pix, left: bool, wear: int, rng: random.Random) -> None:
    """One end cap: two small stepped rings and a tall main barrel with flanges, brass bands on dark iron."""
    def X(x0: int, w: int) -> int:
        return x0 if left else W - x0 - w
    # (x offset, width, y top, y bottom, ramp)
    rings = ((0, 9, 16, 108, IRON_D), (8, 7, 10, 114, IRON_D), (14, 30, 0, 124, IRON_D))
    for (x0, w, y0, y1, ramp) in rings:
        x = X(x0, w)
        m = rect_mask(x, y0, w, y1 - y0, 2)
        cy, r = (y0 + y1 - 1) / 2, (y1 - y0) / 2
        solid(p, m, lambda xx, yy, cy=cy, r=r: math.sqrt(max(0.0, 1 - ((yy - cy) / r) ** 2)) * (r * 0.28) + (min(xx - x, 3) * 0.3 if left else 0),
              ramp, SHADOW, relief=1.4, gain=1.25, bias=-0.1, dither=False)
    # brass bands round the barrel and a flange line at its inner edge
    bx = X(14, 30)
    for xo, wd in ((4, 4), (21, 4)):
        for y in range(2, 122):
            c = BRASS[3] if 28 < y < 60 else (BRASS[2] if y < 96 else BRASS[1])
            if y < 12 or y > 112:
                c = BRASS[1]
            for k in range(wd):
                p.px(bx + xo + k, y, c if k else BRASS[4] if 20 < y < 50 else c)
    inner = X(14, 30) + (30 if left else -1)
    for y in range(0, 124):
        p.px(inner if left else bx, y, IRON_D[0])
    # a glint on the iron between the bands
    for y in range(34, 56):
        p.px(bx + 12, y, IRON_D[5])
        p.px(bx + 13, y, IRON_D[4])
    for y in range(78, 92):
        p.px(bx + 15, y, IRON_D[4])
    if wear:
        for _ in range(wear * 6):
            x, y = bx + rng.randint(0, 29), rng.randint(2, 121)
            p.px(x, y, IRON_D[1])
            p.px(x + 1, y, IRON_D[4])


def phial(wear: int, seed: int, cracked_ferrules: bool = False) -> Image.Image:
    """wear 0 clean, 1 worn, 2 heavily worn."""
    rng = random.Random(seed)
    p = Pix(W, H, seed=seed)
    x0, x1 = 44, 275
    # glass rims: a dark outer line and a pale inner one at the top and bottom of the body
    for x in range(x0, x1):
        p.px(x, 3, (46, 40, 60))
        p.px(x, 4, (46, 40, 60))
        p.px(x, 5, (116, 142, 140) if x % 7 else (170, 190, 180))
        p.px(x, 6, (82, 100, 104))
        p.px(x, 120, (46, 40, 60))
        p.px(x, 119, (46, 40, 60))
        p.px(x, 118, (108, 130, 130))
        p.px(x, 117, (78, 94, 98))
    ferrule(p, True, wear, rng)
    ferrule(p, False, wear, rng)
    # long glints where light runs down the glass (kept as lines so the body stays see-through)
    cream, grey = (222, 216, 186), (172, 178, 164)
    glints = [(42, x0 + 1, x1 - 1, 2, cream), (62, x0 + 1, x0 + 120, 1, grey), (81, x0 + 1, x1 - 1, 2, grey), (62, x1 - 70, x1 - 24, 1, cream), (98, x1 - 90, x1 - 40, 1, grey)]
    if wear:
        glints = [(42, x0 + 1, x1 - 1, 1, cream), (62, x0 + 1, x0 + 70, 1, grey), (81, x0 + 1, x0 + 130, 1, grey), (81, x1 - 100, x1 - 60, 1, cream),
                  (53, x1 - 50, x1 - 20, 1, grey)]
    for (y, xa, xb, th, c) in glints:
        for x in range(xa, xb):
            for k in range(th):
                p.px(x, y + k, c)
    if wear >= 1:
        for _ in range(8 + 10 * wear):                      # fine scuffs in the glass
            x, y = rng.randint(x0 + 6, x1 - 30), rng.randint(14, 108)
            for i in range(rng.randint(5, 16)):
                p.px(x + i, y, (150, 156, 148) if rng.random() < 0.7 else (200, 196, 170))
        for _ in range(2 * wear):                           # small chips along the rims
            x = rng.randint(x0 + 10, x1 - 10)
            p.px(x, 7, (182, 186, 170))
            p.px(x + 1, 8, (140, 150, 140))
    if wear == 2:
        # grime and moss creeping along the top and bottom edge, thickest near the ferrules
        for edge_y, dirn in ((7, 1), (116, -1)):
            for x in range(x0, x1):
                near = min(x - x0, x1 - x) / 80.0
                if rng.random() < 0.38 * (1.2 - min(1.0, near)) + 0.04:
                    n = rng.randint(1, 4 + int((1 - min(1.0, near)) * 5))
                    for k in range(n):
                        p.px(x, edge_y + dirn * k, (74, 90, 62) if k < n - 1 else (46, 56, 44))
        for cx, cy in ((x0 + 8, 90), (x1 - 12, 30)):
            stain(p, {(x, y) for x in range(cx - 14, cx + 15) for y in range(cy - 14, cy + 15)}, rng, cx, cy, 12, ((60, 76, 56), (90, 104, 70)), 0.7)
        # cracks in the ferrules and verdigris on the brass
        for (sx, sy) in ((32, 36), (W - 40, 76)):
            x, y = sx, sy
            for k in range(22):
                p.px(x, y, SHADOW)
                p.px(x + 1, y, IRON_D[4]) if k % 2 else None
                x += rng.choice((-1, 0, 1))
                y += 1
        for _ in range(60):
            x = rng.choice((14 + 4, 14 + 21, W - 14 - 30 + 4, W - 14 - 30 + 21)) + rng.randint(0, 3)
            p.px(x, rng.randint(5, 118), (84, 130, 104))
    return p.im


def reinforced() -> Image.Image:
    p = Pix(W, H, seed=61)
    for y0 in (15, 98):                                      # two rails
        m = rect_mask(41, y0 + 1, 237, 8, 1)
        cy = y0 + 4.5
        solid(p, m, lambda x, y, cy=cy: math.sqrt(max(0.0, 1 - ((y - cy) / 5.5) ** 2)) * 3.0, STEEL, SHADOW, relief=1.4, gain=1.2, bias=-0.35, dither=False)
        for x in range(48, 274, 22):
            p.rect(x, y0 + 3, 3, 3, BRASS[3])
            p.px(x, y0 + 3, BRASS[4])
    for x0 in (88, 217):                                     # two hoops, tall and curved
        m = rect_mask(x0 + 1, 2, 12, 120, 2)
        cx = x0 + 6.5
        solid(p, m, lambda x, y, cx=cx: math.sqrt(max(0.0, 1 - ((x - cx) / 7.5) ** 2)) * 4.0, IRON_D, SHADOW, relief=1.5, gain=1.2, bias=-0.1, dither=False)
        for y in (6, 117):
            p.rect(x0 + 4, y - 1, 5, 3, BRASS[3])
            p.px(x0 + 4, y - 1, BRASS[4])
        for y in range(44, 58):
            p.px(x0 + 4, y, IRON_D[5])
    return p.im


def screws() -> Image.Image:
    p = Pix(W, H, seed=62)
    for (x, y) in ((23, 23), (290, 23), (23, 94), (290, 94)):
        m = {(x + 1 + i, y + 1 + j) for i in range(4) for j in range(4)}
        solid(p, m, lambda xx, yy, x=x, y=y: max(0.0, 1 - ((xx - x - 2.5) ** 2 + (yy - y - 2.5) ** 2) / 9.0) ** 0.5 * 2.5, BRASS, SHADOW, relief=1.0, dither=False, bias=-0.1)
        p.hline(x + 1, y + 3, 4, BRASS[0])
    return p.im


def crack() -> Image.Image:
    p = Pix(W, H, seed=63)
    rng = p.rng
    ox, oy = 53, 77
    pale, dark = (230, 222, 190), (70, 64, 70)
    stems = [(7, 0), (28, 0), (50, 0)]
    for sx, sy in stems:
        x, y = ox + sx, oy + sy
        for k in range(rng.randint(30, 42)):
            if oy <= y < oy + 43 and ox <= x < ox + 61:
                p.px(x, y, pale)
                p.px(x + 1, y, dark)
            x += rng.choice((-1, 0, 0, 1)) + (1 if sx < 28 else 0 if sx == 28 else -1) * (1 if k % 5 == 0 else 0)
            y += 1
            if k % 9 == 8:
                bx, by = x, y
                for j in range(rng.randint(6, 12)):
                    if oy <= by < oy + 43 and ox <= bx < ox + 61:
                        p.px(bx, by, pale)
                    bx += rng.choice((1, 1, 0)) * (1 if sx != 50 else -1)
                    by += rng.choice((0, 1))
    return p.im


# ------------------------------------------------------------------ liquid colour clouds

CLOUDS: dict[str, tuple[tuple[Color, ...], Color, int]] = {
    "normal": (((22, 34, 62), (30, 62, 92), (40, 104, 112), (62, 150, 150), (112, 198, 182)), (228, 226, 196), 3),
    "high_quality": (((38, 20, 50), (92, 34, 90), (142, 50, 122), (198, 86, 152), (236, 152, 190)), (252, 234, 204), 5),
    "poor1": (((46, 44, 50), (76, 74, 78), (110, 108, 106), (148, 146, 138), (190, 188, 170)), (222, 216, 192), 7),
    "poor2": (((26, 54, 56), (36, 88, 82), (54, 124, 106), (86, 160, 120), (130, 190, 130)), (222, 226, 182), 9),
}


def cloud(kind: str) -> Image.Image:
    cols, streak, seed = CLOUDS[kind]
    p = Pix(W, H, seed=seed)
    ox, oy, w, h = 31, 10, 254, 104
    # a leaded frame, dark with a lit top-left edge
    frame = rect_mask(ox, oy, w, h, 2)
    for (x, y) in frame:
        p.px(x, y, (30, 24, 34))
    for x in range(ox + 1, ox + w - 1):
        p.px(x, oy + 1, (96, 86, 96))
        p.px(x, oy + 2, (58, 50, 62))
    for y in range(oy + 1, oy + h - 1):
        p.px(ox + 1, y, (96, 86, 96))
        p.px(ox + 2, y, (58, 50, 62))
    n1 = fbm(seed, 34, 20, 4)
    n2 = fbm(seed + 5, 90, 40, 2)
    cx, cy = ox + w / 2, oy + h / 2
    for y in range(oy + 3, oy + h - 3):
        for x in range(ox + 3, ox + w - 3):
            dx, dy = (x - cx) / (w / 2), (y - cy) / (h / 2)
            r = math.hypot(dx * 0.85, dy * 1.0)
            v = 1.15 - r * 1.05 + (n1(x, y) - 0.5) * 0.85 + (n2(x, y) - 0.5) * 0.35
            idx = 0 if v < 0.18 else 1 if v < 0.38 else 2 if v < 0.56 else 3 if v < 0.74 else 4
            # cloud contours: a one-pixel darker edge where a band meets the next
            p.px(x, y, cols[idx])
    # faint darker contour lines between bands
    snap = p.im.copy()
    for y in range(oy + 4, oy + h - 4):
        for x in range(ox + 4, ox + w - 4):
            c = snap.getpixel((x, y))
            if c[:3] != snap.getpixel((x + 1, y))[:3] or c[:3] != snap.getpixel((x, y + 1))[:3]:
                i = cols.index(c[:3]) if c[:3] in cols else 0
                if i > 0 and (x + y) % 2:
                    p.px(x, y, cols[i - 1])
    # the bright vein through the middle, a wavering line with a soft shoulder
    rng = random.Random(seed)
    y = round(cy)
    for x in range(round(cx) - 62, round(cx) + 66):
        y += rng.choice((-1, 0, 0, 0, 1)) if x % 3 == 0 else 0
        y = max(round(cy) - 4, min(round(cy) + 4, y))
        p.px(x, y, streak)
        if abs(x - cx) < 40:
            p.px(x, y - 1, cols[4])
            p.px(x, y + 1, cols[4])
    return p.im


ASSETS: dict[str, Callable[[], Image.Image]] = {
    "cartridge.319x124.png": lambda: phial(0, 71),
    "condition_wear.319x124.png": lambda: phial(1, 72),
    "condition_heavy_wear.319x124.png": lambda: phial(2, 73),
    "condition_reinforced.319x124.png": reinforced,
    "condition_screws.319x124.png": screws,
    "condition_crack1.319x124.png": crack,
}
for _k in ("normal", "high_quality", "poor1", "poor2"):
    ASSETS[f"color_{_k}.319x124.png"] = (lambda k=_k: cloud(k))
