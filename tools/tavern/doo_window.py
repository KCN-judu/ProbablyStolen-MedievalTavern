"""The serving window of the tavern: the oak posts and sill (`window`), the lintel (`window_top`), the slatted tambour
shutter with its rails and pull-bar (`shutter_door`), the diamond-leaded pane behind it (`glass_door`), the candle bar
on the outside of the wall (`store_front_lamp`) and its cone of light (`lighting`).

Everything is built with the shared material kit (fxkit) so it meets the cask's standard: per-board tone, wandering
grain, knots, lit upper-left edges and shaded right edges, forged iron with brass nails, contact shadows.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping

from PIL import Image

from fxkit import (RUST, brass_fill, contact_shadow, iron_fill, over, region, rivet, vnoise, wear, wood_fill)
from palette import BRASS, FLAME, GLASS, IRON, MOSS, OAK, SHADOW, WOOD
from pix import Pix, mix
from shopx_persp import VP, blend, stepped, tier

W, H = 960, 540


# ---------------------------------------------------------------------------------------------- posts and sill


def strap(p: Pix, x0: int, y0: int, w: int, h: int, seed: int, tail: str = "") -> None:
    """A wrought strap across a post, seated with a contact shadow, riveted at both ends and the middle."""
    contact_shadow(p, (x0, y0, w, h), shift=(2, 3), spread=3, strength=1.0, alpha=220)
    iron_fill(p, (x0, y0, w, h), hammer=0.7, rust=0.4, seed=seed)
    for x in (x0 + 4, x0 + w // 2, x0 + w - 5):
        rivet(p, x, y0 + h // 2, 1 if h < 9 else 2, BRASS)


def post(p: Pix, x0: int, seed: int) -> None:
    """An oak post of the window: two planed faces (the front lit, a chamfer), grain, knots, damp at the foot, with
    three iron straps."""
    wood_fill(p, (x0, 0, 22, 254), grain_dir="v", ramp=OAK, board=11, joints=False, nails=False, knots=0.8, wear_amount=0.6,
              damp=0.25, damp_from="bottom", light=0.5, bias=0.5, seed=seed)
    p.vline(x0 + 1, 0, 254, OAK[4])                                 # a worn chamfer catching the light
    p.vline(x0 + 2, 0, 254, OAK[3])
    p.vline(x0 + 21, 0, 254, OAK[0])
    for y in (34, 126, 214):
        strap(p, x0, y, 22, 8, seed + y)
        for dy in range(9, 22):                                     # rust runs down from the strap's nails
            if (dy * 5 + x0) % 3 == 0:
                blend(p, x0 + 4, y + dy, RUST[1], 0.35 * (1 - dy / 22))
                blend(p, x0 + 17, y + dy, RUST[1], 0.35 * (1 - dy / 22))


def window_frame() -> Image.Image:
    p = Pix(W, H, seed=31)
    sill_top = [(314, 250), (647, 250), (647, 258), (314, 258)]
    for x0, sd in ((314, 3), (625, 7)):
        post(p, x0, sd)
    # the sill: a top (seen from above, level edges) and a thick front lip with a rounded nose
    wood_fill(p, sill_top, grain_dir="h", ramp=OAK, board=4, joints=True, nails=True, knots=0.4, wear_amount=0.7, light=0.6,
              bias=1.0, seed=11)
    contact_shadow(p, (314, 258, 333, 13), shift=(0, 4), spread=3, strength=0.6, alpha=160)
    wood_fill(p, (314, 258, 333, 13), grain_dir="h", ramp=OAK, board=13, joints=True, nails=True, knots=0.7, wear_amount=0.8,
              damp=0.25, damp_from="bottom", light=0.45, bias=0.4, seed=12)
    p.hline(314, 258, 333, OAK[0])                                  # the groove under the nose
    p.hline(314, 259, 333, OAK[4])                                  # the lit nose
    p.hline(314, 260, 333, OAK[3])
    p.hline(314, 270, 333, OAK[0])
    for x in range(314, 647):                                       # the middle is worn into a shallow dip by elbows
        d = abs(x - 480) / 120
        if d < 1 and stepped(0.35 * (1 - d), x, 255):
            blend(p, x, 255, WOOD[4], 0.35)
        if d < 1 and stepped(0.25 * (1 - d), x, 252):
            blend(p, x, 252, OAK[4], 0.3)
    for x in (334, 628):                                            # the posts' feet are seated on iron shoes
        iron_fill(p, (x - 14, 238, 24, 12), hammer=0.4, rust=0.4, seed=x)
        rivet(p, x - 9, 244, 1, BRASS)
        rivet(p, x + 5, 244, 1, BRASS)
    return p.finish()


# ---------------------------------------------------------------------------------------------- lintel


def window_top() -> Image.Image:
    """The lintel over the window. Above the horizon we see its underside, a trapezoid narrowing toward VP; the front
    face is an oak beam with iron end straps; a shade under it falls on whatever hangs below."""
    p = Pix(W, H, seed=32)
    x0, x1 = 329, 632
    wood_fill(p, (x0, 0, x1 - x0, 20), grain_dir="h", ramp=OAK, board=20, joints=True, nails=True, knots=0.7,
              wear_amount=0.7, light=0.5, bias=0.5, seed=13)
    p.hline(x0, 0, x1 - x0, OAK[3])
    # the underside: the far edge is higher on the screen than the near, and inset toward VP
    for y in range(20, 26):
        s = (VP[1] - y) / (VP[1] - 20)
        xa, xb = round(VP[0] + (x0 - VP[0]) * s), round(VP[0] + (x1 - VP[0]) * s)
        for x in range(xa, xb):
            k = vnoise(x / 6, y, 3) - 0.5
            c = OAK[1] if y < 23 else OAK[0]
            if (k > 0.2 and y == 21) or stepped(0.4 - 0.05 * (y - 20), x, y):
                c = OAK[2] if y < 24 else OAK[1]
            p.px(x, y, c)
    p.hline(x0, 20, x1 - x0, OAK[0])
    p.hline(x0, 21, x1 - x0, OAK[1])
    for x in (332, 611):
        strap(p, x, 3, 20, 14, 5 + x)
    return p.finish()


# ---------------------------------------------------------------------------------------------- shutter

SX0, SY0, SX1, SY1 = 329, 24, 631, 265


def slat_panel(p: Pix) -> None:
    """Slats 8 px tall, each its own plank: own tone, own grain, a lit top edge, a dark groove under it where the
    hinge cord lies, nails at both ends and the odd mended split."""
    rng = random.Random(33)
    ix0, ix1 = SX0 + 5, SX1 - 5
    y = SY0
    row = 0
    while y < SY1 - 18:
        h = min(8, SY1 - 18 - y)
        bias = rng.choice((-0.6, -0.3, 0.0, 0.0, 0.3, 0.6))
        wood_fill(p, (ix0, y, ix1 - ix0, h), grain_dir="h", ramp=WOOD, board=h, joints=False, nails=False,
                  knots=0.5 if h == 8 else 0, wear_amount=0.5, light=0.35, bias=bias + 0.1, rim=False, seed=100 + row)
        for x in range(ix0, ix1):
            p.px(x, y, WOOD[min(4, 3 + (x // 3 + row) % 2)])         # lit top edge
            p.px(x, y + h - 2, WOOD[1])
            p.px(x, y + h - 1, WOOD[0])                              # the groove between slats
        for nx in (ix0 + 4, ix1 - 5):
            p.px(nx, y + 3, BRASS[3] if rng.random() < 0.5 else IRON[4])
            p.px(nx + 1, y + 4, SHADOW)
        if rng.random() < 0.12:                                       # a split mended with an iron staple
            cx = rng.randrange(ix0 + 30, ix1 - 40)
            p.rect(cx, y + 2, 14, 3, IRON[2])
            p.hline(cx, y + 2, 14, IRON[4])
            p.hline(cx, y + 4, 14, IRON[0])
            p.px(cx + 2, y + 3, BRASS[3])
            p.px(cx + 11, y + 3, BRASS[3])
        y += 8
        row += 1
    # light and dirt over the whole panel: the lamp is above, the hands are low, the sides catch the street
    for yy in range(SY0, SY1 - 17):
        for xx in range(ix0, ix1):
            top_shade = max(0.0, 1 - (yy - SY0) / 40)                 # the lintel's shade
            hand = max(0.0, 1 - abs(yy - (SY1 - 38)) / 26) * max(0.0, 1 - abs(xx - 480) / 90)
            if stepped(0.55 * top_shade, xx, yy):
                blend(p, xx, yy, SHADOW, 0.5)
            if stepped(0.5 * hand, xx, yy):
                blend(p, xx, yy, WOOD[4], 0.22)                       # polished where it is pulled
            edge = max(0.0, 1 - (xx - ix0) / 22) * 0.0
    for xx in range(ix0, ix0 + 18):                                   # the left rail's lit side lightens the slat ends
        for yy in range(SY0, SY1 - 17):
            if stepped(0.25 * (1 - (xx - ix0) / 18), xx, yy):
                blend(p, xx, yy, WOOD[4], 0.18)
    for xx in range(ix1 - 18, ix1):
        for yy in range(SY0, SY1 - 17):
            if stepped(0.35 * ((xx - ix1 + 18) / 18), xx, yy):
                blend(p, xx, yy, SHADOW, 0.35)


def rails(p: Pix) -> None:
    """Two iron guide channels the slats run in: a face of forged iron with a dark slot inside, nailed to the posts every
    20 px (brass heads) with a rust streak under each nail."""
    for x0, left in ((SX0, True), (SX1 - 5, False)):
        contact_shadow(p, (x0, SY0, 5, SY1 - SY0), shift=(2 if left else -1, 2), spread=2, strength=0.8, alpha=200)
        iron_fill(p, (x0, SY0, 5, SY1 - SY0), hammer=0.4, rust=0.35, seed=x0)
        slot_x = x0 + (4 if left else 0)
        p.vline(slot_x, SY0 + 1, SY1 - SY0 - 2, IRON[0])             # the channel mouth
        for y in range(SY0 + 9, SY1 - 14, 19):
            rivet(p, x0 + 2, y, 1, BRASS)
            for dy in range(3, 11):
                if (dy + y) % 2 == 0:
                    blend(p, x0 + 2, y + dy, RUST[1], 0.5 * (1 - dy / 11))


def pull_bar(p: Pix) -> None:
    """The bottom bar: a thick oak batten with an iron strap, nailed; an iron ring hangs from a staple plate at the middle."""
    y0 = SY1 - 18
    wood_fill(p, (SX0, y0, SX1 - SX0, 18), grain_dir="h", ramp=OAK, board=18, joints=True, nails=True, knots=0.6, wear_amount=0.8,
              light=0.5, bias=0.9, seed=34)
    p.hline(SX0, y0, SX1 - SX0, OAK[4])
    p.hline(SX0, y0 + 17, SX1 - SX0, OAK[0])
    contact_shadow(p, (SX0 + 2, y0 + 5, SX1 - SX0 - 4, 7), shift=(0, 2), spread=2, strength=0.9, alpha=200)
    iron_fill(p, (SX0 + 2, y0 + 5, SX1 - SX0 - 4, 7), hammer=0.7, rust=0.45, rivets=17, seed=35)
    cx = (SX0 + SX1) // 2
    contact_shadow(p, (cx - 12, y0 + 3, 24, 11), shift=(2, 3), spread=3, strength=1.0, alpha=220)
    iron_fill(p, (cx - 12, y0 + 3, 24, 11), hammer=0.6, rust=0.3, seed=36)    # the staple plate
    rivet(p, cx - 8, y0 + 8, 2, BRASS)
    rivet(p, cx + 8, y0 + 8, 2, BRASS)
    # the ring: a thick iron torus seen face-on, hanging from the plate's eye, with a brass collar
    ry = y0 + 11
    contact_shadow(p, [(cx - 8 + 2, ry + 1), (cx + 8 + 2, ry + 1), (cx + 8 + 2, ry + 17), (cx - 8 + 2, ry + 17)], shift=(2, 3),
                   spread=2, strength=0.7, alpha=190)
    for ang in range(0, 360, 2):
        a = math.radians(ang)
        for t in (0, 1, 2):
            rx, rr = 8 - t, 7.5 - t
            x, yv = round(cx + rx * math.cos(a)), round(ry + 8 + rr * math.sin(a))
            lit = (math.cos(a) + math.sin(a)) < -0.2
            c = IRON[4] if t == 0 and lit else IRON[3] if t == 1 and lit else IRON[2] if t == 0 else IRON[1] if t == 1 else IRON[0]
            p.px(x, yv, c)
    p.rect(cx - 3, ry - 1, 6, 4, BRASS[2])
    p.hline(cx - 3, ry - 1, 6, BRASS[4])
    p.hline(cx - 3, ry + 2, 6, BRASS[0])


def shutter() -> Image.Image:
    p = Pix(W, H, seed=33)
    slat_panel(p)
    rails(p)
    pull_bar(p)
    wear(p, (SX0, SY0, SX1 - SX0, SY1 - SY0), amount=0.25, kinds=("scratch", "dust"), seed=9)
    return p.finish()


# ---------------------------------------------------------------------------------------------- glass


def glass() -> Image.Image:
    """The leaded pane behind the shutter: a lattice of diamonds in hand-blown tinted glass, held by lead cames (lit on top
    and left, dark on the lower right), solder at the crossings, a lead rim, glints and long reflections. The glass stays
    translucent (the layer lies over the scene)."""
    p = Pix(W, H, seed=34)
    x0, y0, x1, y1 = 331, 22, 629, 263
    rng = random.Random(34)
    dw, dh = 26, 36                                                  # a diamond's half-diagonals: 52 x 72 px
    tints = [GLASS[3], GLASS[2], mix(GLASS[3][:3], MOSS[3][:3], 0.4), mix(GLASS[3][:3], BRASS[2][:3], 0.28), GLASS[4]]
    cell_tint: dict[tuple[int, int], tuple[int, int, int]] = {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            fu = (x - x0) / dw + (y - y0) / dh
            fv = (x - x0) / dw - (y - y0) / dh
            iu, iv = math.floor(fu), math.floor(fv)
            du, dv = fu - iu, fv - iv
            # distance (in px) to the nearest lead line along each diagonal
            lu = min(du, 1 - du) * dw * dh / math.hypot(dw, dh) * 2
            lv = min(dv, 1 - dv) * dw * dh / math.hypot(dw, dh) * 2
            if min(lu, lv) < 1.1:
                lit = (du < 0.5 and lu <= lv) or (dv > 0.5 and lv < lu)
                dark = not lit
                tone = 3 if lit else 0
                p.px(x, y, (*IRON[tone][:3], 255))
                continue
            key = (iu, iv)
            if key not in cell_tint:
                cell_tint[key] = rng.choice(tints)[:3]
            r, g, b = cell_tint[key]
            a = 56 + round(18 * vnoise(x / 9, y / 9, 5))
            edge = min(lu, lv)
            if edge < 2.4:                                           # glass thickens at the lead: a deeper tone
                a += 26
            p.px(x, y, (r, g, b, a))
    for iu in range(-8, 12):                                         # a glint at the upper-left of each diamond, a seed bubble
        for iv in range(-8, 12):
            cx = x0 + (iu + iv + 1) * dw // 2 + 0
            cy = y0 + (iu - iv + 1) * dh // 2
    for (cu, cv), _ in cell_tint.items():
        cx = x0 + round((cu + cv + 1) * dw / 2 * 1.0)
        cy = y0 + round((cu - cv + 1) * dh / 2 * 1.0)
        gx, gy = cx - 5, cy - 7
        if x0 + 4 < gx < x1 - 4 and y0 + 4 < gy < y1 - 4 and p.get(gx, gy)[3] < 140:
            over(p, gx, gy, (232, 240, 236, 255), 150)
            over(p, gx + 1, gy + 1, (232, 240, 236, 255), 90)
            over(p, gx, gy + 1, (232, 240, 236, 255), 70)
        bx, by = cx + rng.randrange(-6, 7), cy + rng.randrange(-8, 9)
        if p.get(bx, by)[3] < 140 and x0 + 3 < bx < x1 - 3 and y0 + 3 < by < y1 - 3 and rng.random() < 0.25:
            over(p, bx, by, (200, 225, 225, 255), 130)
    # long diagonal reflections across everything
    for gx, gw, st in ((46, 14, 0.5), (96, 5, 0.7), (190, 20, 0.45)):
        for i in range(y1 - y0):
            xs = x0 + gx + i * 3 // 4
            for dx in range(gw):
                x, y = xs + dx, y0 + i
                if p.get(x, y)[3] and p.get(x, y)[3] < 140 and stepped(st * (1 - abs(dx - gw / 2) / (gw / 2 + 1)), x, y):
                    over(p, x, y, (255, 225, 170, 255), 70)
    # the lead rim of the pane, 3 px, with solder blobs at the corners
    for t in range(3):
        c = IRON[(3, 2, 0)[t]]
        for x in range(x0 + t, x1 - t):
            p.px(x, y0 + t, (*c[:3], 255))
            p.px(x, y1 - 1 - t, (*IRON[(1, 1, 0)[t]][:3], 255))
        for y in range(y0 + t, y1 - t):
            p.px(x0 + t, y, (*c[:3], 255))
            p.px(x1 - 1 - t, y, (*IRON[(1, 1, 0)[t]][:3], 255))
    p.clip([(x0, y0), (x1 - 1, y0), (x1 - 1, y1 - 1), (x0, y1 - 1)])
    return p.finish()


# ---------------------------------------------------------------------------------------------- the candle bar


CANDLES = (396, 438, 480, 522, 564)
WAX = ((124, 108, 78), (176, 156, 112), (222, 205, 160), (244, 232, 192), (255, 247, 214))


def flame(p: Pix, cx: int, y: int, size: int) -> None:
    """A teardrop flame: dark red base at the wick, orange body, a pale hot core, a tip that leans a little."""
    rows = {4: (1, 1, 3, 3), 3: (1, 3, 2), 2: (1, 2)}[size]
    for i, wdt in enumerate(rows):
        yy = y + i
        # i = 0 is the tip; the widest rows are low
        for dx in range(-(wdt // 2), wdt - wdt // 2):
            core = (i >= 1 and dx == 0 and i < len(rows) - 1)
            c = FLAME[4] if core and i >= 2 else FLAME[3] if core or (i == len(rows) - 1 and dx == 0) else FLAME[2] if i < len(rows) - 1 else FLAME[1]
            p.px(cx + dx, yy, c)
    p.px(cx, y + len(rows), mix(FLAME[0][:3], SHADOW[:3], 0.3) + (255,))   # the dark wick root


def lamp() -> Image.Image:
    """A candle bar on the outside of the wall: a forged iron bar nailed to the wall by two end plates, five brass
    dishes on it, a candle in each with its own height and a run of wax, a flame above. It stays inside 350..611 x 33..44."""
    p = Pix(W, H, seed=52)
    # the bar and its wall plates
    contact_shadow(p, (352, 42, 257, 2), shift=(1, 1), spread=1, strength=1.0, alpha=220)
    iron_fill(p, (352, 42, 257, 2), hammer=0.3, rust=0.3, seed=1)
    p.hline(352, 42, 257, IRON[4])
    p.hline(352, 43, 257, IRON[1])
    for x in range(358, 606, 9):                                     # twisted-bar texture: diagonal dark ticks
        p.px(x, 42, IRON[2])
        p.px(x + 1, 43, IRON[0])
    for px0 in (350, 606):                                           # the end plates, nailed to the wall
        iron_fill(p, (px0, 36, 5, 8), hammer=0.4, rust=0.4, seed=px0)
        rivet(p, px0 + 2, 38, 1, BRASS, shadow=False)
        p.px(px0 + 2, 42, BRASS[3])
    rng = random.Random(53)
    heights = (4, 3, 4, 3, 4)
    for cx, ch in zip(CANDLES, heights):
        # brass dish: a flat saucer seen slightly from above (a rim, a dark well), on a collar over the bar
        p.hline(cx - 5, 41, 11, BRASS[0])
        p.hline(cx - 4, 42, 9, BRASS[1])
        p.hline(cx - 5, 40, 11, BRASS[3])
        p.px(cx - 5, 40, BRASS[4])
        p.px(cx - 4, 40, BRASS[4])
        p.hline(cx - 3, 41, 3, BRASS[4])
        p.hline(cx + 1, 41, 4, BRASS[2])
        p.px(cx + 5, 40, BRASS[1])
        p.px(cx, 43, BRASS[2])
        p.hline(cx - 1, 43, 3, BRASS[2])
        # candle: a wax cylinder, lit on the left, shaded on the right, with a puddle in the dish
        top = 40 - ch
        for y in range(top, 40):
            for dx in range(-2, 3):
                c = WAX[4] if dx == -2 else WAX[3] if dx == -1 else WAX[2] if dx == 0 else WAX[1] if dx == 1 else WAX[0]
                if y == top:
                    c = WAX[4] if dx < 1 else WAX[3]                  # the rim of the molten top
                p.px(cx + dx, y, c)
        run = rng.choice((1, 2, 3))
        p.px(cx + 1 if run != 2 else cx - 1, top + 1, WAX[3])
        p.px(cx + 1 if run != 2 else cx - 1, top + 2, WAX[3])          # a run of wax down the side
        p.px(cx + 1 if run != 2 else cx - 1, top + 3 if top + 3 < 40 else 39, WAX[2])
        p.hline(cx - 3, 39, 7, WAX[1] if run % 2 else WAX[2])           # the puddle that gathered in the dish
        p.px(cx + 3, 39, WAX[0])
        p.px(cx, top - 1, (46, 30, 24))                               # the wick
        fy = top - 5 if top - 5 >= 33 else 33
        flame(p, cx, fy, 4 if top - 5 >= 33 else 3)
    return p.finish()


def lighting() -> Image.Image:
    """The cone of warm light from the candle bar, within 393..567 x 26..168. Five pools merge near the bar and fall off
    in eight dithered steps, widening down; a few dust motes hang in the beam."""
    p = Pix(W, H, seed=51)
    top, bottom = 26, 168
    for y in range(top, bottom):
        t = (y - top) / (bottom - top)
        for x in range(393, 567):
            half = 80 * min(1.0, 0.45 + 1.3 * t)
            dx = abs(x - 480)
            if dx >= half:
                continue
            edge = 1 - dx / half
            pools = max(math.exp(-((x - c) / 14.0) ** 2) for c in CANDLES) if y < 80 else 0.0
            pool_k = pools * max(0.0, 1 - (y - top) / 54)
            level = (1 - t * 0.78) * min(1.0, edge * 1.9) * 0.85 + pool_k * 0.45
            k = tier(level, x, y, 8)
            if k:
                col = FLAME[4] if k >= 7 else FLAME[3]
                p.px(x, y, (*col[:3], round(255 * k / 8)))
    rng = random.Random(51)
    for _ in range(14):                                              # motes in the beam
        x, y = rng.randrange(425, 535), rng.randrange(60, 150)
        if p.get(x, y)[3]:
            p.px(x, y, (*FLAME[4][:3], 255))
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "window.960x540.png": window_frame,
    "window_top.960x540.png": window_top,
    "shutter_door.960x540.png": shutter,
    "glass_door.960x540.png": glass,
    "store_front_lamp.960x540.png": lamp,
    "lighting.960x540.png": lighting,
}
