"""Appraisal close-ups, instruments: the potion vial and its damage, indicator jewels, the lens and its frames, the card.

The vial series (base, two liquid colours, three kinds of damage) keeps the liquid, the glass, the cap and the highlight
streak where they are in every picture; only the colour or the damage differs, because that is what gets judged.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from PIL import Image

from appraisalkit_b import BRASS, CLOTH, INK, IRON, PARCH, SHADOW, Canvas, band_shade, ring
from palette import NIGHT, OAK, PALE_WOOD, STONE, WINE, WOOD, LEATHER, PLASTER
from pix import CLEAR, Color, Pix, mix, rgb

# ------------------------------------------------------------------------------------------- potion vial

# Row profile of a glass tube lit from above: tone index into the 5-step ramp for rows 1..37.
PROFILE = [1, 1, 2, 3, 3, 4, 4, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
GREEN = (rgb("#1c3a28"), rgb("#2a5a34"), rgb("#3d8040"), rgb("#7db452"), rgb("#dcd8aa"))
OLIVE = (rgb("#2a2a1c"), rgb("#4a4a2c"), rgb("#686a40"), rgb("#8c8a5c"), rgb("#dcc8bc"))
TEAL = (rgb("#1a2c3c"), rgb("#2a5468"), rgb("#3a7a8c"), rgb("#8cc4bc"), rgb("#cfe6d8"))
GLASS = (rgb("#4a4c48"), rgb("#6e706a"), rgb("#a8aea5"), rgb("#bcc0b2"), rgb("#dcdccc"))
LIQUID_END = 35 + 101        # first column of the empty glass
TUBE_X, TUBE_W, TUBE_H = 35, 196, 39


def _tube_mask(x: int, y: int) -> bool:
    """The rounded outline of the tube in picture coordinates."""
    cx = x - TUBE_X
    if not (0 <= cx < TUBE_W and 0 <= y < TUBE_H):
        return False
    cut = {0: 5, 1: 3, 2: 2, 3: 1}
    c = min(cx, TUBE_W - 1 - cx)
    return y >= cut.get(c, 0) and y < TUBE_H - cut.get(c, 0)


def vial(liquid: Sequence[Color], damage: int = 0) -> Image.Image:
    p = Canvas(231, 39, seed=200 + damage)
    for y in range(TUBE_H):
        for x in range(TUBE_X, TUBE_X + TUBE_W):
            if not _tube_mask(x, y):
                continue
            edge = y in (0, TUBE_H - 1) or x in (TUBE_X, TUBE_X + TUBE_W - 1) or not _tube_mask(x, y - 1) \
                or not _tube_mask(x, y + 1) or not _tube_mask(x - 1, y) or not _tube_mask(x + 1, y)
            if edge:
                p.px(x, y, IRON[1])
                continue
            tone = PROFILE[min(y - 1, len(PROFILE) - 1)]
            wet = x < LIQUID_END or x >= TUBE_X + TUBE_W - 9
            ramp = liquid if wet else GLASS
            p.px(x, y, ramp[tone])
    # brass bands at both ends and a pale glint along the tube
    for bx in (TUBE_X + 3, TUBE_X + TUBE_W - 13):
        for y in range(1, TUBE_H - 1):
            if _tube_mask(bx, y) and _tube_mask(bx, y - 1) and _tube_mask(bx, y + 1) and 3 <= y <= TUBE_H - 4:
                t = PROFILE[y - 1]
                p.px(bx, y, BRASS[min(4, t + 1)]); p.px(bx + 1, y, BRASS[min(4, max(1, t))]); p.px(bx + 2, y, BRASS[max(0, t - 1)])
    for x0, x1, y in ((TUBE_X + 47, TUBE_X + 103, 8), (TUBE_X + 63, TUBE_X + 90, 9), (TUBE_X + 108, TUBE_X + 122, 8)):
        p.hline(x0, y, x1 - x0, CLOTH[4])
    # a ring of wax around the cork end on the right, with its glossy lip
    for y in range(6, 33):
        p.px(TUBE_X + TUBE_W - 4, y, mix(CLOTH[4], GLASS[2], 0.4)) if y < 20 else None
    if damage == 1:
        _crack(p, 120)
    elif damage == 2:
        _scorch(p, 125)
    elif damage == 3:
        _chip(p, 119)
    return p.finish()


def _crack(p: Pix, x0: int) -> None:
    """A crack running from the top edge to the bottom, with a chipped notch above and flakes of glass below."""
    pts = [(x0, 0), (x0 + 1, 3), (x0 + 3, 6), (x0 + 3, 9), (x0 + 5, 12), (x0 + 5, 15), (x0 + 7, 18), (x0 + 8, 22),
           (x0 + 8, 26), (x0 + 10, 30), (x0 + 11, 34), (x0 + 12, 38)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        p.line(ax - 1, ay, bx - 1, by, GLASS[4])      # pale lip on the left side of the break
        p.line(ax, ay, bx, by, IRON[0])
        p.line(ax + 1, ay, bx + 1, by, IRON[2])
    for dx, dy in ((-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (-2, 0)):      # notch in the top rim
        p.px(x0 + dx, dy, IRON[3] if dx < 1 else CLEAR)
    p.rect(x0 + 4, 29, 5, 7, IRON[3]); p.rect(x0 + 4, 29, 5, 1, IRON[4]); p.rect(x0 + 5, 36, 4, 1, IRON[1])
    p.px(x0 + 7, 31, IRON[1]); p.px(x0 + 8, 33, IRON[2])


def _scorch(p: Pix, cx: int) -> None:
    """A burnt-through patch at the lower edge: soot, a rim of embers and ragged charring."""
    rng = p.rng
    for x in range(cx - 25, cx + 26):
        rel = abs(x - cx) / 25
        h = int(21 * (1 - rel) ** 0.9) + rng.randint(-1, 1)
        for k in range(h):
            y = TUBE_H - 1 - k
            if not _tube_mask(x, y):
                continue
            depth = h - k
            if depth <= 2:
                c = rgb("#a8603a") if (x + y) % 3 else rgb("#d08a4a")        # glowing rim
            elif depth <= 4:
                c = rgb("#6a3a28")
            else:
                c = rng.choice((rgb("#1c1618"), rgb("#2c2024"), rgb("#141016"), rgb("#1c1618")))
            p.px(x, y, c)
    for _ in range(14):                                                   # ember flecks on the glass beside it
        x = cx + rng.randint(-31, 31)
        y = TUBE_H - 1 - rng.randint(0, 9)
        if _tube_mask(x, y) and p.get(x, y)[:3] not in ((28, 22, 24),):
            if abs(x - cx) > 22:
                p.px(x, y, rgb("#7a4a30") if rng.random() < 0.6 else rgb("#4a3028"))


def _chip(p: Pix, x0: int) -> None:
    """A small V-shaped chip knocked out of the top, with two hairline cracks below it."""
    for r in range(0, 10):
        half = max(0, 4 - r // 2)
        for dx in range(-half - 1, half + 2):
            c = IRON[1] if abs(dx) == half + 1 or r == 9 else (IRON[4] if dx < 0 else IRON[3])
            if r <= 9:
                p.px(x0 + dx, r, c)
    for k in range(10, 18):
        p.px(x0 - 1 + (k // 6), k, IRON[1])
        p.px(x0 + (k // 6), k, GLASS[4])
    for k in range(10, 14):
        p.px(x0 + 1 + (k - 9), k, IRON[1])


# ------------------------------------------------------------------------------------------- indicator, slot


def indicator(color: str) -> Image.Image:
    p = Canvas(231, 39, seed=210)
    x, y, w, h = 200, 16, 15, 6
    p.rect(x, y, w, h, BRASS[1])
    p.hline(x, y, w, BRASS[2]); p.vline(x, y, h, BRASS[2])
    p.hline(x, y + h - 1, w, BRASS[0]); p.vline(x + w - 1, y, h, BRASS[0])
    p.rect(x + 1, y + 1, w - 2, h - 2, rgb("#20181c"))
    tones = {"green": (rgb("#3f8a40"), rgb("#9fd060")), "orange": (rgb("#a8553a"), rgb("#e6a064")),
             "red": (rgb("#5a2430"), rgb("#8a3a44"))}
    if color in tones:
        dark, light = tones[color]
        p.rect(x + 9, y + 1, 4, 4, dark)
        p.rect(x + 9, y + 2, 4, 2, light)
        p.px(x + 9, y + 2, mix(light, (255, 244, 200), 0.5))
    return p.finish()


def slot() -> Image.Image:
    """The vial dock: an iron cradle with a brass rim, a corked amber vial lying in it."""
    p = Canvas(231, 39, seed=220)
    x, y, w, h = 60, 13, 50, 13
    for dx, c in ((0, IRON[3]), (1, IRON[2])):
        p.rect(x + dx, y + dx, w - 2 * dx, h - 2 * dx, c)
    for cx, cy in ((x, y), (x + w - 2, y), (x, y + h - 2), (x + w - 2, y + h - 2)):
        p.rect(cx, cy, 2, 2, CLEAR)
    p.hline(x + 2, y, w - 4, IRON[4]); p.vline(x, y + 2, h - 4, IRON[4])
    p.rect(x + 2, y + 2, w - 4, h - 4, BRASS[2])
    p.hline(x + 2, y + 2, w - 4, BRASS[4]); p.hline(x + 2, y + h - 3, w - 4, BRASS[0])
    p.rect(x + 3, y + 3, w - 6, h - 6, rgb("#241a20"))
    amber = (rgb("#6a3a1a"), rgb("#a8602a"), rgb("#d89440"), rgb("#f0c870"))
    p.rect(x + 6, y + 4, 33, 5, amber[1])
    p.hline(x + 6, y + 4, 33, amber[3]); p.hline(x + 6, y + 5, 33, amber[2]); p.hline(x + 6, y + 8, 33, amber[0])
    p.hline(x + 9, y + 5, 14, rgb("#fbe9b0"))
    p.rect(x + 40, y + 4, 5, 5, LEATHER[3]); p.vline(x + 40, y + 4, 5, LEATHER[2]); p.hline(x + 40, y + 8, 5, LEATHER[1])
    p.vline(x + 37, y + 4, 5, BRASS[3]); p.vline(x + 38, y + 4, 5, BRASS[1])
    return p.finish()


# ------------------------------------------------------------------------------------------- lens


def lens() -> Image.Image:
    """An eyeglass: oak grip wrapped in leather, brass ferrule and rim, a bracket with garnet and emerald studs."""
    p = Canvas(242, 228, seed=230)
    cx, cy = 151.5, 76.5
    # grip: axis from the ring to the lower left
    ax0, ay0, ax1, ay1 = 100.0, 128.0, 14.0, 214.0
    dx, dy = ax1 - ax0, ay1 - ay0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length

    def along(x: int, y: int) -> tuple[float, float]:
        rx, ry = x + 0.5 - ax0, y + 0.5 - ay0
        return (rx * ux + ry * uy), (-rx * uy + ry * ux)         # distance along, signed distance across

    def hw(t: float) -> float:
        return 9.5 + 1.5 * (t / length) if t < length - 14 else 11 - (t - length + 14) * 0.25

    def in_grip(x: int, y: int) -> bool:
        t, d = along(x, y)
        return -2 <= t <= length + 4 and abs(d) <= hw(t)
    wood = WOOD
    def grip_light(x: int, y: int) -> float:
        t, d = along(x, y)
        return 0.5 + 0.55 * (-d / hw(t)) * 0.9
    band_shade(p, (0, 100, 130, 228), in_grip, grip_light, wood)
    for x in range(0, 130):
        for y in range(100, 228):
            if in_grip(x, y):
                t, d = along(x, y)
                if 26 <= t <= 100 and int(t) % 7 in (0, 1):        # leather wrap, a spiral of thongs
                    k = (0.5 + 0.5 * (-d / hw(t)))
                    p.px(x, y, LEATHER[3] if k > 0.65 else LEATHER[2] if k > 0.35 else LEATHER[1])
                    if int(t) % 7 == 0:
                        p.px(x, y, LEATHER[0] if k < 0.5 else LEATHER[2])
                elif t > length - 12:                             # brass cap
                    p.px(x, y, BRASS[3] if -d / hw(t) > 0.1 else BRASS[1])
                elif t < 16:                                       # brass ferrule
                    p.px(x, y, BRASS[4] if -d / hw(t) > 0.35 else BRASS[3] if -d / hw(t) > -0.3 else BRASS[1])
                if not (in_grip(x + 1, y) and in_grip(x - 1, y) and in_grip(x, y + 1) and in_grip(x, y - 1)):
                    p.px(x, y, SHADOW)
    # the rim: dark outline, brass with a lit upper left, dark inner lip
    for y in range(0, 160):
        for x in range(70, 242):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 64 <= d <= 76.5:
                ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                lit = 0.5 + 0.5 * math.cos(ang - math.radians(225))      # brightest toward the upper left
                if d >= 75.5:
                    c = SHADOW
                elif d <= 65.2:
                    c = SHADOW
                elif d <= 67.5:
                    c = BRASS[0]
                elif d >= 72.5:
                    c = BRASS[1] if lit < 0.55 else BRASS[2]
                else:
                    k = 1 + int(lit * 3.4)
                    c = BRASS[min(4, k)]
                    if (x + y) % 5 == 0 and lit > 0.4:
                        c = BRASS[min(4, k + 0)]
                p.px(x, y, c)
    # engraved notches around the rim
    for a in range(0, 360, 15):
        t = math.radians(a)
        p.px(cx + 70 * math.cos(t), cy + 70 * math.sin(t), BRASS[1])
    ring(p, 103, 124, 13, 0, BRASS[2]) if False else None
    # bracket on the lower right with studs
    for y in range(40, 190):
        for x in range(150, 242):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            ang = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx))
            if 76 < d <= 91 and 8 <= ang <= 78:
                edge = d > 90 or ang < 9.5 or ang > 76.5
                t = 1 + int((90.5 - d) / 15 * 2.4)
                p.px(x, y, SHADOW if edge else BRASS[min(4, t + 1)] if d < 80 else IRON[min(4, t + 1)] if d > 86 else BRASS[2])
    for ang, c in ((20, WINE[3]), (36, WINE[3]), (52, WINE[3]), (66, rgb("#3f8a50"))):
        t = math.radians(ang)
        sx, sy = cx + 83 * math.cos(t), cy + 83 * math.sin(t)
        ring(p, sx, sy, 3.6, 0, SHADOW)
        ring(p, sx, sy, 2.6, 0, c)
        p.px(sx - 1, sy - 1, mix(c, (255, 240, 220), 0.6))
    # two jewels on the left of the rim
    for sx, sy, c in ((88, 129, WINE[3]), (92, 142, rgb("#3f8a50"))):
        ring(p, sx, sy, 4, 0, SHADOW); ring(p, sx, sy, 3, 0, c)
        p.px(sx - 1, sy - 1, mix(c, (255, 240, 220), 0.6))
    # reflections inside the glass: two pale streaks
    for k in range(18):
        p.px(118 + k, 32 - k // 6, PARCH[4] if k % 5 else PARCH[3])
    for k in range(17):
        p.px(199, 76 + k // 1 if False else 74 + k, PARCH[4] if k < 15 else PARCH[3]); p.px(200, 74 + k, PARCH[3])
    return p.finish()


def lens_mask() -> Image.Image:
    p = Canvas(242, 228, seed=231)
    p.ellipse(88, 13, 127, 127, (255, 255, 255, 255))
    return p.finish()


def lens_frame() -> Image.Image:
    """The window that frames the magnified view: an oak frame with clipped corners and brass studs, hung on an iron arm."""
    p = Canvas(960, 540, seed=240)
    x0, y0, x1, y1 = 358, 34, 604, 201      # outer box (x1, y1 exclusive)
    c = 9
    def oct_in(x: int, y: int, a: int, b: int, e: int, f: int, k: int) -> bool:
        if not (a <= x < e and b <= y < f):
            return False
        rx, ry = min(x - a, e - 1 - x), min(y - b, f - 1 - y)
        return rx + ry >= k
    # the iron arm first, so the frame overlaps it
    def arm(ax: int, ay: int, bx: int, by: int, w: int) -> None:
        for k in range(w):
            p.line(ax - w // 2 + k, ay, bx - w // 2 + k, by, IRON[1] if k in (0, w - 1) else IRON[2] if k < w // 2 else IRON[3])
    arm(321, 0, 296, 46, 7)
    arm(302, 62, 358, 108, 8)
    for ang in range(360):
        pass
    ring(p, 293, 54, 17, 0, SHADOW); ring(p, 293, 54, 16, 0, BRASS[2]); ring(p, 292.5, 53.5, 14, 0, BRASS[3])
    ring(p, 293, 54, 16, 14.5, BRASS[1])
    for a in range(180, 280, 3):
        p.px(293 + 15 * math.cos(math.radians(a)), 54 + 15 * math.sin(math.radians(a)), BRASS[4])
    ring(p, 293, 54, 6, 0, SHADOW); ring(p, 293, 54, 4.5, 0, IRON[0])
    p.vline(293, 54, 21, SHADOW) if False else None
    # frame bars
    th = 8
    for y in range(y0, y1):
        for x in range(x0, x1):
            if oct_in(x, y, x0, y0, x1, y1, c) and not oct_in(x, y, x0 + th, y0 + th, x1 - th, y1 - th, c - 3):
                do = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
                di = None
                top_left = (y - y0 < th) or (x - x0 < th)
                if do == 0:
                    col = SHADOW
                elif do <= 2:
                    col = PALE_WOOD[3] if top_left else OAK[1]
                elif do <= 4:
                    col = PALE_WOOD[2] if top_left else OAK[2]
                else:
                    col = WOOD[2] if top_left else WOOD[1]
                # inner lip
                if not oct_in(x + 1, y + 1, x0 + th, y0 + th, x1 - th, y1 - th, c - 3) is False:
                    pass
                p.px(x, y, col)
    for y in range(y0 + th - 1, y1 - th + 1):
        for x in range(x0 + th - 1, x1 - th + 1):
            if oct_in(x, y, x0 + th - 1, y0 + th - 1, x1 - th + 1, y1 - th + 1, c - 3) and not oct_in(x, y, x0 + th, y0 + th, x1 - th, y1 - th, c - 3):
                p.px(x, y, BRASS[2] if (x < (x0 + x1) / 2 and y < (y0 + y1) / 2) else BRASS[1])
    # studs and corner plates
    for sx, sy in ((x0 + 4, y0 + 4), (x1 - 5, y0 + 4), (x0 + 4, y1 - 5), (x1 - 5, y1 - 5), ((x0 + x1) // 2, y0 + 3),
                   ((x0 + x1) // 2, y1 - 4), (x0 + 3, (y0 + y1) // 2), (x1 - 4, (y0 + y1) // 2)):
        p.rect(sx - 1, sy - 1, 3, 3, BRASS[3]); p.px(sx - 1, sy - 1, BRASS[4]); p.px(sx + 1, sy + 1, BRASS[0])
    # iron collar where the arm meets the frame
    p.rect(352, 100, 14, 34, IRON[2]); p.vline(352, 100, 34, IRON[4]); p.vline(365, 100, 34, IRON[0])
    for yy in range(102, 132, 5):
        p.hline(352, yy, 14, IRON[1]); p.hline(352, yy + 1, 14, IRON[3])
    # a hook at the bottom for hanging it on a nail
    p.rect(520, 201, 50, 20, IRON[2])
    p.rect(523, 201, 44, 15, CLEAR)
    p.frame(520, 201, 50, 20, IRON[1])
    p.hline(520, 218, 50, IRON[1]); p.hline(520, 219, 50, SHADOW) if False else None
    p.vline(521, 201, 18, IRON[4]); p.hline(524, 217, 42, IRON[3])
    # erase the middle of the frame (transparent window)
    return p.finish()


# ------------------------------------------------------------------------------------------- card


def card() -> Image.Image:
    """An oak-and-iron signboard card with a round medallion: a mountain and the monogram GP."""
    p = Canvas(278, 176, seed=250)
    w, h = 278, 176
    inside = lambda x, y: 0 <= x < w and 0 <= y < h and not ((min(x, w - 1 - x) + min(y, h - 1 - y)) < 3)
    p.rect(0, 0, w, h, OAK[2])
    for y in range(h):                     # long grain lines
        if y % 9 == 3:
            p.hline(0, y, w, OAK[1])
        if y % 9 == 4:
            p.dither(0, y, w, 1, OAK[3], 0.3)
    for k in range(12):
        gx = p.rng.randint(5, w - 40)
        gy = p.rng.randint(5, h - 5)
        p.hline(gx, gy, p.rng.randint(12, 40), OAK[3])
    for y in range(h):
        for x in range(w):
            if not inside(x, y):
                p.px(x, y, CLEAR)
    p.frame(0, 0, w, h, OAK[0])
    p.frame(2, 2, w - 4, h - 4, OAK[1])
    p.hline(3, 3, w - 6, OAK[4]); p.vline(3, 3, h - 6, OAK[4])
    for x, y in ((8, 8), (w - 9, 8), (8, h - 9), (w - 9, h - 9)):       # iron rivets
        p.rect(x - 2, y - 2, 5, 5, IRON[1]); p.rect(x - 1, y - 1, 3, 3, IRON[3]); p.px(x - 1, y - 1, IRON[4])
    cx, cy, r = 138, 60, 50
    ring(p, cx + .5, cy + .5, r + 3, r, BRASS[1]); ring(p, cx + .5, cy + .5, r + 3, r + 2, BRASS[2])
    for a in range(200, 290, 2):
        p.px(cx + (r + 2) * math.cos(math.radians(a)), cy + (r + 2) * math.sin(math.radians(a)), BRASS[4])
    sky = lambda x, y: math.hypot(x + .5 - cx, y + .5 - cy) < r
    band_shade(p, (cx - r, cy - r, cx + r, cy + r), sky, lambda x, y: 0.15 + 0.25 * (y - cy + r) / (2 * r), NIGHT)
    for _ in range(18):
        sx, sy = cx + p.rng.randint(-40, 40), cy + p.rng.randint(-45, -5)
        if sky(sx, sy):
            p.px(sx, sy, NIGHT[4])
    # mountain: two ridges
    def ridge(x: int) -> float:
        return cy + 10 - 36 * max(0.0, 1 - abs(x - (cx - 2)) / 44) - 10 * max(0.0, 1 - abs(x - (cx + 26)) / 20)
    for x in range(cx - r, cx + r):
        for y in range(int(ridge(x)), cy + r):
            if sky(x, y):
                lit = (x < cx - 2) == (y > ridge(x) + 2)
                side = STONE[2] if x < cx - 2 else STONE[1]
                if y < ridge(x) + 3:
                    side = PLASTER[3]            # snow cap
                elif (x + y) % 4 == 0 and y < cy + 20:
                    side = STONE[3] if x < cx - 2 else STONE[0]
                p.px(x, y, side)
    # monogram GP in thick pale strokes
    pale, shade_c = PLASTER[4], PLASTER[1]
    def letters(ox: int, oy: int, c: Color) -> None:
        t = 6
        gx, gy, gw, gh = 101 + ox, 31 + oy, 32, 57
        p.rect(gx, gy, gw, t, c); p.rect(gx, gy, t, gh, c); p.rect(gx, gy + gh - t, gw, t, c)
        p.rect(gx + gw - t, gy + gh // 2, t, gh // 2, c); p.rect(gx + gw // 2, gy + gh // 2, gw // 2, t, c)
        px = 141 + ox
        p.rect(px, gy, t, gh, c); p.rect(px, gy, gw, t, c); p.rect(px + gw - t, gy, t, gh // 2 + 2, c)
        p.rect(px, gy + gh // 2 - 2, gw, t, c)
    letters(1, 1, SHADOW)
    letters(0, 0, pale)
    return p.finish()


DRAWINGS: dict[str, Callable[[], Image.Image]] = {
    "injector_base.231x39.png": lambda: vial(GREEN),
    "injector_color1.231x39.png": lambda: vial(OLIVE),
    "injector_color2.231x39.png": lambda: vial(TEAL),
    "injector_dam1.231x39.png": lambda: vial(GREEN, 1),
    "injector_dam2.231x39.png": lambda: vial(GREEN, 2),
    "injector_dam3.231x39.png": lambda: vial(GREEN, 3),
    "indicator_green.231x39.png": lambda: indicator("green"),
    "indicator_orange.231x39.png": lambda: indicator("orange"),
    "indicator_red.231x39.png": lambda: indicator("red"),
    "indicator_missing.231x39.png": lambda: indicator("missing"),
    "slot.231x39.png": slot,
    "magnifying glass.242x228.png": lens,
    "magnifying_mask.242x228.png": lens_mask,
    "magnifying_screen.960x540.png": lens_frame,
    "gp_2x.278x176.png": card,
}
