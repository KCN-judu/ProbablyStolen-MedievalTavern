"""The smaller layers of the shop view, drawn to the shop's single viewpoint (see shopx_persp): the street door seen
edge-on, its chain, the lamp strip, the lintel over the window and the cone of lamplight.

The door is a plane that recedes toward the vanishing point, so its upright board edges stay upright while every
horizontal line on it (straps, butt joints, the grille's top and bottom) slopes toward VP: down to the right above the
horizon, up to the right below it.
"""

from __future__ import annotations

from PIL import Image

from materials import beam, iron_strap
from palette import BRASS, FLAME, IRON, OAK, SHADOW, WOOD
from pix import Pix, mix
from shopx_persp import VP, stepped, tier

W, H = 960, 540


def toward(y0: float, x: float) -> float:
    """The height at column `x` of a line that is at height `y0` at the left edge and runs away to VP."""
    return y0 + (VP[1] - y0) * x / VP[0]


def sloped_band(p: Pix, x0: int, x1: int, y0: float, h: int, fill, top, bottom) -> None:
    """A horizontal band on the door: both edges slope toward VP. The upper edge is lit, the lower dark."""
    for x in range(x0, x1):
        ya = round(toward(y0, x))
        p.vline(x, ya, h, fill)
        p.px(x, ya, top)
        p.px(x, ya + h - 1, bottom)


def door() -> Image.Image:
    """The street door seen edge-on at the left of the room: four oak boards, three hinge straps, a latch and a barred
    hatch, all in the perspective of a wall that recedes."""
    p = Pix(W, H, seed=41)
    rng = p.rng
    edges = (0, 13, 26, 39, 52)
    for i in range(4):
        bx0, bx1 = edges[i], edges[i + 1]
        tone = (2, 3, 2, 1)[i]
        p.rect(bx0, 0, bx1 - bx0, 539, WOOD[tone])
        p.vline(bx0, 0, 539, WOOD[tone + 1])
        p.vline(bx1 - 1, 0, 539, WOOD[0])
        p.vline(bx1 - 2, 0, 539, WOOD[tone - 1])
        for _ in range(26):                                      # grain runs down the board
            gx, gy, n = bx0 + 2 + rng.randrange(bx1 - bx0 - 5), rng.randrange(539), rng.randrange(10, 50)
            p.vline(gx, gy, min(n, 539 - gy), WOOD[tone - 1] if rng.random() < 0.7 else WOOD[tone + 1])
        y = rng.randrange(30, 120)
        while y < 520:                                           # butt joints slope with the wall, a nail at each end
            for x in range(bx0 + 1, bx1 - 1):
                yy = round(toward(y, x))
                p.px(x, yy, WOOD[0])
                p.px(x, yy + 1, WOOD[tone + 1])
            p.px(bx0 + 3, round(toward(y, bx0 + 3)) - 3, IRON[4])
            p.px(bx1 - 4, round(toward(y, bx1 - 4)) - 3, IRON[4])
            y += rng.randrange(110, 200)
    beam(p, 52, 0, 8, 539, OAK, vertical=True)                   # the jamb
    for y0 in (60, 270, 470):                                    # hinge straps run to the hinge pin at the jamb
        sloped_band(p, 0, 50, y0, 11, IRON[2], IRON[4], IRON[0])
        for x in range(5, 46, 10):
            p.px(x, round(toward(y0, x)) + 5, BRASS[3])
        yk = round(toward(y0, 49))
        p.ellipse(44, yk, 10, 11, IRON[3])
        p.ellipse(47, yk + 3, 4, 4, IRON[1])
        p.px(46, yk + 2, IRON[4])
    # the latch plate and ring
    p.rect(14, 300, 9, 26, IRON[2])
    p.vline(14, 300, 26, IRON[4])
    p.vline(22, 300, 26, IRON[0])
    p.ellipse(15, 318, 7, 7, IRON[4])
    p.ellipse(17, 320, 3, 3, SHADOW)
    # the hatch at eye level: a barred opening whose top and bottom slope away
    for x in range(6, 44):
        for y in range(round(toward(150, x)), round(toward(210, x))):
            p.px(x, y, SHADOW)
    for x in range(10, 42, 7):
        p.vline(x, round(toward(150, x)) + 1, round(toward(210, x)) - round(toward(150, x)) - 2, IRON[3])
        p.px(x, round(toward(150, x)) + 1, IRON[4])
    for x in range(6, 44):
        p.px(x, round(toward(150, x)), IRON[2])
        p.px(x, round(toward(210, x)) - 1, IRON[4])             # the sill of the hatch catches the light
    p.vline(6, round(toward(150, 6)), 60, IRON[2])
    p.vline(43, round(toward(150, 43)), 56, IRON[0])
    return p.finish()


def door_lock() -> Image.Image:
    """A chain with a padlock hanging by the door, in place of the electronic lock's cable: links alternate between
    a ring seen face-on and a ring seen edge-on."""
    p = Pix(960, 540, seed=42)
    for i, y in enumerate(range(0, 262, 7)):
        if i % 2 == 0:                                           # face-on link: a ring with an open middle
            p.rect(59, y, 5, 8, IRON[3])
            p.rect(60, y + 2, 3, 4, (0, 0, 0, 0))
            p.vline(59, y, 8, IRON[4])
            p.vline(63, y, 8, IRON[0])
        else:                                                     # edge-on link: a thin bar between its neighbours
            p.rect(60, y + 1, 3, 7, IRON[2])
            p.vline(60, y + 1, 7, IRON[4])
            p.vline(62, y + 1, 7, IRON[1])
    p.rect(54, 266, 15, 20, BRASS[2])                           # the lock body
    p.bevel(54, 266, 15, 20, BRASS[4], BRASS[0])
    p.rect(60, 274, 3, 5, SHADOW)
    p.frame(57, 258, 9, 10, IRON[3])
    p.rect(55, 288, 13, 14, BRASS[1])
    p.rect(58, 290, 7, 10, BRASS[2])
    p.hline(58, 290, 7, BRASS[4])
    return p.finish()


def lighting() -> Image.Image:
    """The cone of warm light from the lamp over the window; the game lays it over the shop at a quarter strength. Its
    strength falls in a few dithered steps, not a smooth ramp."""
    p = Pix(W, H, seed=51)
    top, bottom, cx = 26, 168, 480
    for y in range(top, bottom):
        t = (y - top) / (bottom - top)
        half = round(36 + 52 * t)
        for x in range(cx - half, cx + half):
            edge = 1 - abs(x - cx) / half
            level = (1 - t * 0.8) * min(1.0, edge * 2.2)
            k = tier(level, x, y, 6)
            if k:
                p.px(x, y, (*FLAME[3][:3], round(255 * k / 6)))
    return p.finish()


def lamp() -> Image.Image:
    """The lamp strip over the window: a wrought-iron bar with five candles in brass cups, wax runs down the candles,
    a hanging ring at each end. It stays inside the 350..611 x 33..44 box the game's layer occupies."""
    p = Pix(W, H, seed=52)
    p.rect(350, 41, 261, 3, IRON[2])
    p.hline(350, 41, 261, IRON[4])
    p.hline(350, 43, 261, IRON[0])
    for x in range(356, 606, 12):                               # twisted-bar texture
        p.px(x, 42, IRON[3])
    for rx in (350, 607):                                       # rings the chains hang from
        p.frame(rx, 38, 4, 6, IRON[3])
        p.px(rx + 1, 39, IRON[4])
    for cx in (384, 432, 480, 528, 576):
        p.rect(cx - 4, 40, 9, 3, BRASS[2])                      # the cup
        p.hline(cx - 4, 40, 9, BRASS[4])
        p.hline(cx - 3, 42, 7, BRASS[0])
        p.rect(cx - 2, 36, 5, 4, (232, 218, 176))               # the candle
        p.vline(cx - 2, 36, 4, (250, 240, 205))
        p.vline(cx + 2, 36, 4, (176, 156, 116))
        p.px(cx + 1, 38, (205, 188, 146))                       # a run of wax
        p.px(cx + 1, 39, (205, 188, 146))
        p.px(cx, 35, (60, 40, 30))                               # the wick
        p.px(cx, 34, FLAME[4])                                   # the flame: a teardrop, hot in the middle
        p.px(cx, 33, FLAME[3])
        p.px(cx - 1, 34, FLAME[2])
        p.px(cx + 1, 34, FLAME[2])
        p.px(cx - 1, 35, FLAME[1])
        p.px(cx + 1, 35, FLAME[1])
    return p.finish()


def window_top() -> Image.Image:
    """The lintel over the serving window. Above the horizon the viewer sees its underside, a trapezoid that narrows
    toward VP, so the beam is a front face and a darker underside, with a strap at each end."""
    p = Pix(W, H, seed=32)
    x0, x1 = 329, 632
    beam(p, x0, 0, x1 - x0, 20, OAK, vertical=False)
    for y in range(20, 26):                                      # the underside: far edge is lower and inset
        s = (VP[1] - y) / (VP[1] - 20)
        xa, xb = round(VP[0] + (x0 - VP[0]) * s), round(VP[0] + (x1 - VP[0]) * s)
        p.hline(xa, y, xb - xa, OAK[1] if y < 24 else OAK[0])
        for x in range(xa, xb):
            if stepped(0.45, x, y):
                p.px(x, y, OAK[2])
    p.hline(x0, 20, x1 - x0, OAK[0])
    for x in (332, 612):
        iron_strap(p, x, 3, 18, 15)
        p.px(x + 4, 10, BRASS[3])
        p.px(x + 13, 10, BRASS[3])
    return p.finish()
