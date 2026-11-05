"""`vending0..100` and `fountain0..100` (64x112): the coin-operated vending machine and the drinks fountain, as two oak cabinets.

vending   The pie-and-bread cupboard: an oak cabinet with a glazed door and five shelves of loaves, buns, pies and
          pretzels; below, a brass coin slot, a hand crank that works the delivery drawer, and the drawer itself. The
          fill level is how many of the twenty places on the shelves hold something (the same goods stay put from level
          to level, so a purchase removes only what was sold).
fountain  The cask rack: an oak stand holding a hooped cask with its brass tap over a drip grate, a tankard waiting on
          the grate, and a glass sight tube with a brass scale beside the cask whose amber ale stands at the fill level
          (0, 10, 25, 50, 75, 90, 100 per cent of the tube).
Both share the shape the game gives the machine: the vending cabinet has a chamfered cornice, the fountain a straight top."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image

import fxkit as fx
from furn_fix import rows_poly
from furn_kit import ALE, BRASS_AGED, clip, sight_tube
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, WINE, WOOD
from pix import Pix, Ramp, mix, rgb

LEVELS: Final = (0, 10, 25, 50, 75, 90, 100)
CRUST: Final[Ramp] = (rgb("#3f2210"), rgb("#6e3f18"), rgb("#9c6428"), rgb("#c98f44"), rgb("#ebc378"))


# ---------------------------------------------------------------------------------------------- small parts


def blob(p: Pix, cx: float, cy: float, rx: float, ry: float, ramp: Ramp, tilt: float = 0.0, seed: int = 0) -> None:
    """A rounded lump (loaf, bun, pie crust) lit from the upper left, with a dark rim on the lower right."""
    top = len(ramp) - 1
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            d = dx * dx + dy * dy
            if d > 1.0:
                continue
            z = math.sqrt(1 - d)
            lit = -0.55 * dx - 0.6 * dy + 0.62 * z
            v = top * max(0.0, min(1.0, 0.25 + lit * 0.85))
            if d > 0.72 and dx + dy > 0:
                v *= 0.55
            n = fx.noise(x, y, seed + 3)
            v += 0.5 if n > 0.9 else -0.4 if n < 0.08 else 0
            p.px(x, y, ramp[max(0, min(top, round(v)))])


def food(p: Pix, x: int, y: int, kind: int, seed: int = 0) -> None:
    """One baked good standing on a shelf: (x, y) is its bottom centre, it is up to 9 px wide and 8 px tall."""
    k = kind % 4
    if k == 0:                                                            # a long loaf with slashes and flour
        blob(p, x, y - 3, 5, 3.4, CRUST, seed=seed)
        for i in (-2, 0, 2):
            p.line(x + i - 1, y - 5, x + i + 1, y - 3, CRUST[4])
        p.px(x - 3, y - 5, PARCHMENT[4])
    elif k == 1:                                                          # a pie in an iron tin
        p.rect(x - 4, y - 2, 9, 3, IRON[2])
        p.hline(x - 4, y - 2, 9, IRON[4])
        p.hline(x - 4, y, 9, IRON[0])
        blob(p, x, y - 4, 4.6, 3.4, CRUST, seed=seed)
        p.px(x, y - 6, SHADOW)                                             # the steam hole
        p.px(x - 2, y - 4, CRUST[4])
        p.px(x + 2, y - 5, CRUST[1])
    elif k == 2:                                                          # two round rolls
        blob(p, x - 2, y - 2, 3, 2.8, CRUST, seed=seed)
        blob(p, x + 2, y - 3, 3, 3.2, CRUST, seed=seed + 1)
        p.px(x + 1, y - 5, CRUST[4])
        p.px(x - 3, y - 3, CRUST[4])
    else:                                                                 # a pretzel
        for a in range(0, 360, 20):
            xx, yy = x + 3.6 * math.cos(math.radians(a)), y - 3.4 + 2.6 * math.sin(math.radians(a))
            p.px(round(xx), round(yy), CRUST[3] if 90 < a < 250 else CRUST[1])
            p.px(round(xx), round(yy) + 1, CRUST[2] if 90 < a < 250 else CRUST[0])
        p.line(x - 3, y - 2, x + 3, y - 5, CRUST[3])
        p.line(x - 3, y - 5, x + 3, y - 2, CRUST[2])
        p.px(x - 2, y - 5, PARCHMENT[4])


def shell(p: Pix, key: str, seed: int) -> list[tuple[int, int]]:
    """The oak carcase in the shape the game gives it: staves running down, a lit left, a shaded right, a plinth."""
    poly = rows_poly(key, 7, 104)
    fx.contact_shadow(p, (8, 100, 49, 5), shift=(2, 1), spread=3, strength=0.9)
    fx.wood_fill(p, poly, "v", OAK, board=8, light=0.6, bias=0.4, seed=seed, knots=0.8, joints=False, nails=False, damp=0.25,
                 scratches=1.4)
    for y in range(7, 104):                                               # the right flank lies in shade
        r = rows_poly(key, y, y)
        xr = r[-1][0]
        for x in range(xr - 4, xr + 1):
            fx.over(p, x, y, SHADOW, 40 + (x - (xr - 4)) * 18)
    return poly


def plinth(p: Pix) -> None:
    """A dark plinth at the foot with a lit top moulding and a shadow where it meets the floor."""
    fx.wood_fill(p, (9, 96, 48, 8), "h", WOOD, board=8, light=0.2, bias=-0.9, seed=9, knots=0, joints=False, nails=False)
    p.hline(8, 96, 50, WOOD[4])
    p.hline(8, 97, 50, WOOD[2])


def door_strap(p: Pix, x: int, y: int, w: int, seed: int) -> None:
    """A hinge strap: an iron band with a rivet and a rounded tip."""
    fx.iron_fill(p, (x, y, w, 4), rust=0.25, hammer=0.3, rivets=0, seed=seed)
    fx.rivet(p, x + 3, y + 2, 1, BRASS)


# ---------------------------------------------------------------------------------------------- the vending cupboard


def vending(level: int) -> Image.Image:
    p = Pix(64, 112, seed=200)
    poly = shell(p, "vending", 77)
    # the cornice: a carved, chamfered head with a brass plate that shows a pie
    fx.wood_fill(p, rows_poly("vending", 7, 16), "h", WOOD, board=5, light=0.6, bias=0.5, seed=78, knots=0, joints=False, nails=False)
    for x in range(8, 58):
        p.px(x, 16, SHADOW)
    fx.brass_fill(p, (21, 9, 23, 6), ramp=BRASS_AGED, profile="plate", tarnish=0.4, studs=0, seed=79)
    blob(p, 32, 13, 4, 2.5, CRUST, seed=3)
    p.px(32, 12, SHADOW)
    blob(p, 38, 13, 3, 2.2, CRUST, seed=4)
    # the glazed bay: dark back wall, five shelves, goods
    bx0, by0, bw, bh = 13, 18, 39, 55
    fx.wood_fill(p, (bx0, by0, bw, bh), "v", OAK, board=6, light=0.2, bias=-1.5, seed=81, knots=0.2, joints=False, nails=False,
                 rim=False)
    for y in range(by0, by0 + 8):                                         # the lintel's shade
        for x in range(bx0, bx0 + bw):
            if (x + y) % 2 == 0 or y < by0 + 3:
                fx.over(p, x, y, SHADOW, 150 - (y - by0) * 14)
    for x in range(bx0, bx0 + 3):                                         # and the left jamb's
        for y in range(by0, by0 + bh):
            fx.over(p, x, y, SHADOW, 90 - (x - bx0) * 25)
    slots = [(bx0 + 5 + c * 8 + (1 if r % 2 else 0), by0 + 10 + r * 11, r * 4 + c) for r in range(5) for c in range(4) for _ in (0,)]
    order = list(range(20))
    random.Random(11).shuffle(order)
    stocked = set(order[:round(level * 20 / 100)])
    kinds = [(r + 2 * c + (r // 2)) % 4 for r in range(5) for c in range(4)]
    for i, (sx, sy, _) in enumerate(slots):
        fx.contact_shadow(p, (sx - 4, sy, 9, 1), shift=(1, 0), spread=1, strength=0.6) if i in stocked else None
        if i in stocked:
            food(p, sx, sy, kinds[i], seed=i)
    for r in range(5):                                                    # the shelf boards: lit front edge
        sy = by0 + 11 + r * 11
        fx.wood_fill(p, (bx0, sy, bw, 3), "h", PALE_WOOD, board=3, light=0.6, seed=90 + r, knots=0, joints=False, nails=False)
        p.hline(bx0, sy + 3, bw, SHADOW)
    # glass in the door: a lead-and-glass pane over the goods
    fx.glass_pane(p, (bx0, by0, bw, bh), cols=2, rows=4, came=1, alpha=34, streaks=2, back=False, seed=5)
    # the door's frame: a lit stile, a mid-rail, and iron hinge straps
    fx.wood_fill(p, (bx0 - 1, by0 - 1, bw + 2, 2), "h", WOOD, board=2, seed=7, knots=0, joints=False, nails=False)
    p.vline(bx0 - 1, by0, bh, WOOD[3])
    p.vline(bx0 + bw, by0, bh, OAK[0])
    for y in (by0 + 6, by0 + bh - 12):
        door_strap(p, bx0 - 4, y, 12, y)
    # below the glass: the coin plate, the crank and the delivery drawer
    fx.wood_fill(p, (bx0, by0 + bh + 1, bw, 22), "h", WOOD, board=11, light=0.5, seed=82, knots=0.6, joints=False, nails=False, damp=0.3)
    p.hline(bx0, by0 + bh + 1, bw, OAK[0])
    fx.brass_fill(p, (40, 78, 11, 14), ramp=BRASS_AGED, profile="plate", tarnish=0.5, studs=0, seed=83)
    p.vline(45, 80, 6, SHADOW)                                            # the coin slot
    p.vline(46, 80, 6, BRASS[4])
    fx.rivet(p, 42, 80, 1)
    fx.rivet(p, 49, 89, 1)
    fx.brass_fill(p, fx.ellipse(21, 85, 6, 6, 24), ramp=BRASS_AGED, profile="dome", tarnish=0.4, seed=84)   # the crank's boss
    p.line(21, 85, 28, 79, BRASS[3])
    p.line(22, 85, 29, 80, BRASS[1])
    fx.wood_fill(p, fx.ellipse(29, 78, 3, 3, 16), "v", PALE_WOOD, board=2, light=0.7, seed=85, knots=0, joints=False, nails=False)
    fx.wood_fill(p, (14, 93, 37, 3), "h", OAK, board=3, light=0.2, seed=86, knots=0, joints=False, nails=False)     # the drawer's slot
    p.hline(14, 93, 37, SHADOW)
    plinth(p)
    fx.wear(p, poly, 0.3, kinds=("scratch", "chip", "dust"), seed=4)
    return clip(p, "vending")


# ---------------------------------------------------------------------------------------------- the cask rack


def fountain(level: int) -> Image.Image:
    p = Pix(64, 112, seed=300)
    poly = shell(p, "fountain", 177)
    fx.wood_fill(p, rows_poly("fountain", 7, 14), "h", WOOD, board=4, light=0.6, bias=0.5, seed=178, knots=0, joints=False, nails=False)
    p.hline(9, 14, 47, SHADOW)
    # the bay: a dark back wall of planks, the cask head held by two rack rails, a hoop of iron round it
    bx0, by0, bw, bh = 13, 16, 38, 64
    fx.wood_fill(p, (bx0, by0, bw, bh), "v", OAK, board=6, light=0.2, bias=-1.4, seed=181, knots=0.2, joints=False, nails=False, rim=False)
    for y in range(by0, by0 + 6):
        for x in range(bx0, bx0 + bw):
            fx.over(p, x, y, SHADOW, 120 - (y - by0) * 18)
    cx, cy, r = 27, 37, 15
    for x, y in fx.ellipse(cx + 3, cy + 3, r + 2, r + 2, 40):              # the cask's shadow on the wall
        fx.over(p, x, y, SHADOW, 90)
    fx.wood_fill(p, (cx - r - 4, cy + r - 4, 2 * r + 8, 4), "h", OAK, board=4, seed=3, knots=0, joints=False, nails=False)   # cradle rail
    fx.wood_fill(p, fx.ellipse(cx, cy, r + 1, r + 1, 48), 90, WOOD, board=5, light=0.5, bias=1.4, seed=182, knots=0.8, joints=False,
                 nails=False, scratches=1.4)                               # the head: planks seen end-on
    for rr in (r + 1, r - 4):                                              # two iron rings round the head
        for a in range(0, 360, 3):
            x = cx + (rr - 0.5) * math.cos(math.radians(a))
            y = cy + (rr - 0.5) * math.sin(math.radians(a))
            lit = 3 if 110 < a < 230 else 1 if (a > 300 or a < 40) else 2
            p.px(round(x), round(y), IRON[lit])
    for a in range(20, 360, 55):
        x, y = cx + (r - 1.5) * math.cos(math.radians(a)), cy + (r - 1.5) * math.sin(math.radians(a))
        fx.rivet(p, round(x), round(y), 0 if False else 1, BRASS)
    fx.wood_fill(p, fx.ellipse(cx - 4, cy - 4, 2.5, 2.5, 12), "v", OAK, board=2, light=0.2, seed=5, knots=0, joints=False, nails=False)
    p.px(cx - 5, cy - 5, WOOD[4])                                          # the bung
    # the brass tap below the head, lever up, and a drip grate with a tankard
    fx.brass_fill(p, (cx - 4, cy + r - 1, 8, 9), ramp=BRASS_AGED, profile="tube", tarnish=0.5, seed=6)
    fx.brass_fill(p, (cx - 7, cy + r + 6, 14, 4), ramp=BRASS_AGED, profile="tube", tarnish=0.5, seed=7)
    p.line(cx + 4, cy + r + 1, cx + 11, cy + r - 4, BRASS[3])
    fx.wood_fill(p, fx.ellipse(cx + 12, cy + r - 5, 2.5, 2.5, 12), "v", PALE_WOOD, board=2, seed=8, knots=0, joints=False, nails=False)
    gy = 72
    fx.iron_fill(p, (bx0, gy, 28, 4), rust=0.3, hammer=0.4, seed=9)
    for x in range(bx0 + 2, bx0 + 27, 3):
        p.vline(x, gy + 1, 2, SOOT[0])
    tx = cx - 5                                                            # a pewter tankard under the tap
    fx.iron_fill(p, (tx, gy - 10, 10, 10), ramp=(IRON[1], IRON[2], IRON[3], IRON[4], (190, 190, 200)), hammer=0.1, rust=0.0, seed=10)
    p.hline(tx, gy - 10, 10, (205, 205, 215))
    p.rect(tx + 10, gy - 8, 3, 6, IRON[2])
    p.rect(tx + 12, gy - 6, 1, 3, IRON[0])
    p.rect(tx + 1, gy - 9, 8, 2, ALE[3] if level > 0 else IRON[1])
    # the sight tube to the right of the cask, scale of brass ticks
    sight_tube(p, 42, 24, 70, 5, level / 100, ALE, ticks=4)
    # the rack's cupboard below: plank doors, strap hinges and a brass pull
    fx.wood_fill(p, (bx0, 81, bw, 15), "h", WOOD, board=7, light=0.5, seed=183, knots=0.6, joints=False, nails=False, damp=0.3)
    p.hline(bx0, 80, bw, OAK[0])
    p.vline(bx0 + bw // 2, 81, 15, OAK[0])
    p.vline(bx0 + bw // 2 + 1, 81, 15, WOOD[3])
    for x in (bx0 - 3, bx0 + bw // 2 + 3):
        door_strap(p, x, 84, 10, x)
        door_strap(p, x, 91, 10, x + 1)
    fx.brass_fill(p, fx.ellipse(bx0 + bw // 2 - 3, 89, 2, 2, 12), ramp=BRASS_AGED, profile="dome", tarnish=0.3, seed=11)
    fx.brass_fill(p, fx.ellipse(bx0 + bw // 2 + 5, 89, 2, 2, 12), ramp=BRASS_AGED, profile="dome", tarnish=0.3, seed=12)
    plinth(p)
    fx.wear(p, poly, 0.3, kinds=("scratch", "chip", "dust"), seed=5)
    return clip(p, "fountain")


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    **{f"items~items_vending@vending{lv}.png": partial(vending, lv) for lv in LEVELS},
    **{f"items~items_vending@fountain{lv}.png": partial(fountain, lv) for lv in LEVELS},
}
