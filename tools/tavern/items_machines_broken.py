"""Machinery sprites, part 2: the ruined machines and the pieces of the repair mini-game.

The game's repair screen shows a wrecked machine (alarm bell, furnace, dew barrel) and the parts you fix it with
(access hatch, key slot, cords, bolts, braces). Here they are wood-and-iron contraptions: each `broken_*` picture is the
wreck of a working one, and the `_` twin is the same wreck in its other state (lit embers, dripping water, sparks).
Every picture is opaque and sits on the same dark plank backdrop, as in the game they fill their rectangle.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

from PIL import Image, ImageDraw

from itemkit_machines import (RUST, Mask, crack, ellipse_mask, gear, pipe, plate, rects, rim, rust, shade_mask, soot)
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, STONE, WINE, WOOD
from pix import Color, Pix, rgb

Draw = Callable[[], Image.Image]
ASSETS: dict[str, Draw] = {}
CORD: tuple[Color, Color, Color] = (WINE[1], WINE[3], WINE[4])
WATER = (rgb("#1c3140"), rgb("#2f5266"), rgb("#4f7c8c"), rgb("#8ab0b8"))


def poly_mask(points: list[tuple[float, float]], size: tuple[int, int]) -> Mask:
    im = Image.new("L", size, 0)
    ImageDraw.Draw(im).polygon(points, fill=255)
    return {(x, y) for y in range(size[1]) for x in range(size[0]) if im.getpixel((x, y))}


def backdrop(p: Pix, x: int = 0, y: int = 0, w: int | None = None, h: int | None = None) -> None:
    """Dark plank wall: two-tone boards of 8 rows with a seam, a lit lip and a few nails."""
    w, h = w or p.w, h or p.h
    for yy in range(y, y + h):
        r = (yy - y) % 8
        c = SOOT[1] if r not in (0, 7) else SOOT[0] if r == 7 else SOOT[2]
        p.hline(x, yy, w, c)
    p.dither(x, y, w, h, SOOT[2], 0.12)
    for yy in range(y + 3, y + h, 8):
        p.px(x + 2 + (yy // 8 * 5) % 7, yy, SOOT[3])


def floor(p: Pix, y: int) -> None:
    p.rect(0, y, p.w, p.h - y, WOOD[0])
    p.hline(0, y, p.w, WOOD[2])
    p.dither(0, y + 1, p.w, p.h - y - 1, WOOD[1], 0.45)


def bricks(p: Pix, x: int, y: int, w: int, h: int, seed: int = 0, bh: int = 5, bw: int = 9) -> None:
    """Lit masonry blocks with mortar lines, upper-left light."""
    p.rect(x, y, w, h, STONE[0])
    for r, yy in enumerate(range(y, y + h, bh)):
        off = (r % 2) * (bw // 2)
        for xx in range(x - off, x + w, bw):
            x0, x1 = max(x, xx + 1), min(x + w, xx + bw)
            if x1 <= x0:
                continue
            tone = (xx * 3 + r * 5 + seed) % 3 + 1
            bh2 = min(bh - 1, y + h - yy - 1)
            if bh2 <= 0:
                continue
            p.rect(x0, yy + 1, x1 - x0, bh2, STONE[tone])
            p.hline(x0, yy + 1, x1 - x0, STONE[min(4, tone + 1)])
            p.hline(x0, yy + bh2, x1 - x0, STONE[max(0, tone - 1)])


def tile_out(p: Pix) -> Image.Image:
    return p.im


# ---------------------------------------------------------------------------------------------- the three wrecks


def alarm(sparks: bool) -> Image.Image:
    """The alarm bell: a brass bell cracked through, torn off one bracket, its rope cut and its clapper loose."""
    p = Pix(48, 48, seed=201)
    backdrop(p)
    floor(p, 43)
    p.rect(0, 6, 5, 3, IRON[2])                                  # the bracket still on the wall
    p.hline(0, 6, 5, IRON[4])
    p.rect(3, 4, 5, 22, IRON[2])
    p.vline(3, 4, 22, IRON[3])
    p.vline(7, 4, 22, IRON[1])
    for y in (7, 14, 22):
        p.px(5, y, BRASS[4])
    p.rect(8, 7, 9, 2, IRON[2])
    p.hline(8, 7, 9, IRON[3])
    pts = [(17, 8), (29, 8), (31, 14), (33, 22), (36, 30), (40, 36), (40, 38), (12, 36), (11, 32), (15, 24), (16, 14)]
    bell = poly_mask(pts, (48, 48))
    shade_mask(p, bell, BRASS, base=2)
    for y in range(11, 36):                                      # lit left flank, shaded right flank
        xs = sorted(x for x, yy in bell if yy == y)
        if len(xs) > 8:
            for x in xs[2:5]:
                p.px(x, y, BRASS[3])
            p.px(xs[3], y, BRASS[4]) if y % 3 else None
            for x in xs[-5:-2]:
                p.px(x, y, BRASS[1])
    p.hline(12, 35, 28, BRASS[1])                               # the lip
    p.hline(12, 36, 28, BRASS[0])
    p.rect(13, 37, 26, 1, SHADOW)
    for x, y in ((21, 15), (24, 16)):
        p.px(x, y, BRASS[4])
    rust(p, bell, 0.07)
    for dx in (0, 1):
        crack(p, 26 + dx, 11, 25, bell, 1)

    p.rect(35, 33, 5, 5, WOOD[0])
    p.hline(34, 33, 1, BRASS[4])
    p.rect(21, 3, 5, 5, BRASS[2])                               # crown loop
    p.hline(21, 3, 5, BRASS[4])
    p.rect(22, 4, 3, 2, SHADOW)
    p.line(23, 2, 18, 0, LEATHER[2])                              # cut rope, frayed
    p.px(17, 0, LEATHER[3])
    p.vline(23, 0, 3, LEATHER[1])
    p.ellipse(32, 41, 6, 5, IRON[2])                              # the clapper, fallen out on the floor
    p.ellipse(33, 41, 3, 2, IRON[4])
    p.hline(29, 44, 4, IRON[1])
    if sparks:
        p.glow(34, 38, 9, FLAME[2], 0.9)
        for x, y in ((15, 31), (38, 29), (28, 41), (12, 41), (41, 22)):
            p.px(x, y, FLAME[4])
            p.px(x + 1, y - 1, FLAME[2])
    else:
        for x, y in ((15, 40), (22, 41), (28, 42)):
            p.px(x, y, IRON[3])
    return p.im


CLEARC = (0, 0, 0, 0)


def furnace(lit: bool) -> Image.Image:
    """A brick furnace: broken chimney, a hole kicked in the side, the iron door torn off one hinge."""
    p = Pix(48, 48, seed=203)
    backdrop(p)
    floor(p, 43)
    bricks(p, 6, 14, 36, 29, seed=2)
    bricks(p, 17, 3, 15, 11, seed=1, bh=4, bw=7)
    for x, y in ((17, 3), (18, 3), (19, 3), (22, 3), (23, 3), (27, 3), (28, 3), (29, 4), (30, 3), (31, 3), (31, 4)):
        p.px(x, y, SOOT[1])                                       # jagged top of the stack
    p.rect(17, 3, 15, 1, SOOT[1])
    p.rect(24, 3, 4, 2, SOOT[1])
    p.vline(16, 3, 11, SHADOW)
    p.vline(32, 3, 11, SHADOW)
    p.rect(5, 14, 38, 3, STONE[3])                                  # lit cornice
    p.hline(5, 14, 38, STONE[4])
    p.hline(5, 16, 38, STONE[0])
    p.vline(5, 14, 29, SHADOW)
    p.vline(42, 14, 29, SHADOW)
    p.hline(5, 42, 38, SHADOW)
    p.rect(14, 22, 20, 20, SOOT[0])                                # fire mouth
    p.rect(14, 22, 20, 2, SHADOW)
    p.hline(13, 21, 22, STONE[4])
    for x in range(14, 34):
        p.px(x, 22 + (x % 2), SHADOW)
    p.vline(13, 21, 22, STONE[3])
    p.vline(34, 21, 22, STONE[1])
    p.rect(14, 38, 20, 4, SOOT[2])
    if lit:
        p.glow(24, 40, 12, FLAME[1], 1.0)
        for x in range(16, 32, 3):
            p.rect(x, 39, 3, 3, FLAME[1 + x % 2])
        p.rect(19, 38, 4, 2, FLAME[3])
        p.px(21, 37, FLAME[4])
        p.px(26, 37, FLAME[2])
    else:
        p.speckle(15, 38, 18, 4, (SOOT[3], STONE[1], IRON[2]), 0.5)
    door = poly_mask([(35, 20), (46, 25), (46, 43), (36, 41)], (48, 48))   # the door, hanging by one hinge at the top
    shade_mask(p, door, IRON, base=2)
    p.line(37, 24, 44, 28, IRON[4])
    p.line(37, 33, 44, 37, IRON[1])
    for x, y in ((38, 23), (44, 27), (39, 39), (44, 40)):
        p.px(x, y, BRASS[3])
    p.rect(34, 20, 3, 3, BRASS[2])
    p.px(34, 20, BRASS[4])
    rust(p, door, 0.18)
    crack(p, 9, 20, 18, rects((6, 14, 41, 42)), 1)
    crack(p, 24, 3, 10, rects((17, 3, 31, 13)), -1)
    p.rect(7, 33, 5, 6, SOOT[0])                                  # a hole where bricks fell out
    p.rect(8, 36, 3, 6, STONE[1])
    p.rect(9, 42, 4, 1, STONE[3])
    p.hline(11, 41, 3, STONE[2])
    soot(p, rects((6, 14, 41, 42)), 0.4)
    return p.im


def moisture(drips: bool) -> Image.Image:
    """The dew barrel: staves sprung, hoops slipped, the brass catch-funnel bent off, the water running out."""
    p = Pix(48, 48, seed=205)
    backdrop(p)
    floor(p, 43)
    body = ellipse_mask(20, 28, 13, 15)
    shade_mask(p, body, WOOD, base=2)
    for x in range(10, 31, 4):                                     # stave seams
        p.vline(x, 14, 29, WOOD[0])
        p.vline(x + 1, 15, 27, WOOD[3])
    for y, c in ((19, IRON[2]), (37, IRON[2])):
        for x, yy in sorted(body):
            if yy == y and (x, y - 1) in body and x not in (0,):
                p.px(x, y, c)
                p.px(x, y + 1, IRON[1])
                if (x + y) % 5 == 0:
                    p.px(x, y, BRASS[3])
    p.line(8, 31, 30, 27, IRON[2])                                 # a hoop slipped crooked
    p.line(8, 32, 30, 28, IRON[1])
    p.line(8, 30, 30, 26, IRON[3])
    for x0, y0, x1, y1 in ((9, 14, 6, 6), (15, 13, 14, 4), (24, 13, 28, 7), (30, 17, 36, 11)):
        p.line(x0, y0, x1, y1, WOOD[3])                            # splintered staves sticking up
        p.line(x0 + 1, y0, x1 + 1, y1, WOOD[1])
        p.px(x1, y1, PALE_WOOD[3])
    p.rect(14, 18, 8, 7, SOOT[0])                                  # dark gap between staves
    for x, y in ((14, 18), (21, 24), (15, 24)):
        p.px(x, y, WOOD[1])
    crack(p, 25, 22, 18, body, 1)
    rust(p, body, 0.03)
    p.ellipse(8, 40, 28, 5, WATER[1])                              # puddle running across the floor
    p.hline(12, 41, 14, WATER[2])
    p.hline(15, 42, 9, WATER[3])
    p.px(30, 43, WATER[0])
    funnel = poly_mask([(36, 29), (46, 29), (43, 36), (39, 36)], (48, 48))
    shade_mask(p, funnel, BRASS, base=2)
    p.hline(37, 30, 8, BRASS[4])
    p.vline(41, 37, 3, BRASS[1])
    p.line(41, 39, 36, 42, BRASS[2])                               # bent pipe
    p.line(41, 40, 36, 43, BRASS[1])
    p.rect(38, 36, 6, 1, IRON[2])
    p.line(43, 16, 43, 29, WOOD[1])                                # leaning post
    p.line(44, 16, 44, 29, WOOD[2])
    p.hline(41, 16, 5, WOOD[3])
    p.rect(36, 32, 3, 2, CLEARC)
    p.rect(36, 32, 3, 2, WATER[0])
    if drips:
        for x, y in ((12, 33), (13, 36), (11, 29), (34, 41)):
            p.px(x, y, WATER[3])
            p.px(x, y + 1, WATER[2])
        p.ellipse(32, 41, 8, 3, WATER[2])
        p.hline(34, 42, 4, WATER[3])
        for x, y in ((38, 38), (37, 40)):
            p.px(x, y, WATER[3])
    else:
        p.hline(13, 40, 3, WATER[0])
        for x, y in ((11, 33), (12, 35)):
            p.px(x, y, WATER[1])
    return p.im


# ---------------------------------------------------------------------------------------------- housings and hatches


def frame_casing(w: int, h: int, seed: int, sockets: tuple[tuple[int, int, int], ...], lever: bool = False) -> Image.Image:
    """An opened machine cabinet: oak frame with iron corner straps round a dark cavity of empty cog sockets."""
    p = Pix(w, h, seed=seed)
    backdrop(p)
    shade_mask(p, rects((0, 0, w - 1, h - 1)), OAK, grain=0.06, base=3)
    for y in range(2, h - 2, 7):
        p.hline(2, y, w - 4, OAK[1])
    p.rect(4, 4, w - 8, h - 8, SOOT[1])                            # cavity
    p.dither(5, 6, w - 10, h - 11, SOOT[2], 0.25)
    p.hline(4, 4, w - 8, SHADOW)
    p.hline(4, 5, w - 8, SOOT[1])
    p.vline(4, 4, h - 8, SHADOW)
    p.hline(4, h - 5, w - 8, OAK[4])
    p.vline(w - 5, 4, h - 8, OAK[4])
    for cx, cy, r in sockets:
        p.ellipse(cx - r - 1, cy - r - 1, 2 * r + 3, 2 * r + 3, IRON[3])   # socket ring
        p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, SOOT[0])
        p.ellipse(cx - r - 1, cy - r - 1, 2 * r + 3, 1, IRON[4]) if r > 2 else None
        for k in range(8):
            ax, ay = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1))[k]
            p.px(cx + ax * (r + 2), cy + ay * (r + 2), BRASS[3] if ax + ay < 0 else BRASS[1])
        p.px(cx, cy, IRON[3])
    if len(sockets) > 1:                                           # one cog left in its socket with its teeth stripped
        cx, cy, r = sockets[0]
        gear(p, cx, cy, r - 1)
        p.poly([(cx, cy), (cx + r, cy - 2), (cx + r, cy + 1)], SOOT[0])
        p.px(cx + r - 1, cy + 2, BRASS[4])
    for x in range(8, w - 8, 5):                                   # brass scraps and splinters on the sill
        p.px(x + (x * 3) % 4, h - 7, BRASS[3] if x % 2 else WOOD[3])
    if lever:
        p.vline(w // 2, 10, h - 22, IRON[2])
        p.px(w // 2, 10, BRASS[4])
        p.rect(w // 2 - 1, 8, 3, 3, BRASS[3])
    for x, y in ((6, 6), (w - 8, 6), (6, h - 8), (w - 8, h - 8)):  # corner straps with rivets
        p.rect(x - 2, y - 2, 5, 5, IRON[2])
        p.hline(x - 2, y - 2, 5, IRON[3])
        p.px(x, y, BRASS[4])
    p.line(4, 12, 9, 13, IRON[1])                                  # dangling frayed cords
    p.line(w - 6, 14, w - 10, 20, CORD[1])
    p.px(w - 10, 21, CORD[2])
    crack(p, 3 + w // 3, 1, 8, rects((0, 0, w - 1, 6)), 1)
    rust(p, rects((0, 0, w - 1, 3), (0, h - 4, w - 1, h - 1), (0, 0, 3, h - 1), (w - 4, 0, w - 1, h - 1)), 0.05)
    return p.im


def hatch(w: int, h: int, seed: int, closed: bool) -> Image.Image:
    """Access hatch: iron-strapped oak door with a latch (closed), or the empty opening it fits (base)."""
    p = Pix(w, h, seed=seed)
    backdrop(p)
    m = w // 8
    outer = rects((1, 1, w - 2, h - 2))
    shade_mask(p, outer, OAK, grain=0.05, base=3)
    ix0, iy0, ix1, iy1 = m + 3, m + 3, w - m - 4, h - m - 4
    if closed:
        door = rects((ix0, iy0, ix1, iy1))
        shade_mask(p, door, WOOD, grain=0.12, base=2)
        for x in range(ix0 + 4, ix1, 5):
            p.vline(x, iy0 + 1, iy1 - iy0 - 1, WOOD[0])
            p.vline(x + 1, iy0 + 1, iy1 - iy0 - 1, WOOD[3])
        for y in (iy0 + 3, iy1 - 5):
            p.rect(ix0 + 1, y, ix1 - ix0 - 1, 3, IRON[2])
            p.hline(ix0 + 1, y, ix1 - ix0 - 1, IRON[4])
            p.hline(ix0 + 1, y + 2, ix1 - ix0 - 1, IRON[0])
            for x in range(ix0 + 3, ix1 - 1, 5):
                p.px(x, y + 1, BRASS[4])
        cx, cy = (ix0 + ix1) // 2 + 3, (iy0 + iy1) // 2
        plate(p, cx - 3, cy - 4, 7, 9)
        p.px(cx, cy - 1, SHADOW)
        p.vline(cx, cy, 3, SHADOW)
        crack(p, ix0 + 3, iy0, (iy1 - iy0) // 2, door, 1)
        rust(p, door, 0.05)
    else:
        p.rect(ix0, iy0, ix1 - ix0 + 1, iy1 - iy0 + 1, SOOT[0])
        p.frame(ix0 - 1, iy0 - 1, ix1 - ix0 + 3, iy1 - iy0 + 3, SHADOW)
        p.hline(ix0, iy1 + 1, ix1 - ix0 + 1, OAK[4])
        p.hline(ix0, iy0, ix1 - ix0 + 1, SHADOW)
        for y in (iy0 + 3, iy1 - 4):                               # empty hinge straps and a latch hole
            p.rect(ix0 - 2, y, 5, 3, IRON[2])
            p.px(ix0 - 1, y + 1, BRASS[3])
        p.rect(ix1 - 2, (iy0 + iy1) // 2 - 1, 3, 3, IRON[1])
        p.px(ix1 - 1, (iy0 + iy1) // 2, SHADOW)
    for x, y in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
        p.px(x, y, BRASS[3])
    return p.im


def anti_tamper() -> Image.Image:
    """Warding plate: a spiked iron bar with a wax seal in the middle, snapped chain hanging off it."""
    p = Pix(48, 32, seed=221)
    backdrop(p)
    shade_mask(p, rects((2, 8, 45, 23)), IRON, grain=0.04, base=2)
    p.hline(3, 9, 42, IRON[4])
    for x in range(5, 44, 6):                                       # spikes up and down
        for dy in (0, 1, 2):
            p.px(x + (1 if dy == 0 else 0), 7 - dy if dy < 3 else 7, IRON[3])
        p.px(x, 6, IRON[4])
        p.px(x, 5, IRON[3])
        p.px(x + 1, 24, IRON[1])
        p.px(x, 25, IRON[1])
        p.px(x, 26, IRON[0])
    for x in range(5, 44, 6):
        p.px(x, 10, BRASS[4])
        p.px(x, 21, BRASS[2])
    p.ellipse(18, 10, 13, 12, WINE[2])                             # wax seal, cracked
    p.ellipse(19, 11, 11, 10, WINE[3])
    p.hline(21, 12, 6, WINE[4])
    p.px(20, 13, WINE[4])
    p.ellipse(21, 14, 7, 5, WINE[1])
    gear(p, 24, 16, 3, ramp=BRASS)
    crack(p, 23, 10, 12, rects((18, 10, 30, 21)), 1)
    p.line(2, 16, 0, 22, IRON[3])                                  # chain
    for i, y in enumerate(range(24, 31, 2)):
        p.rect(3 + i % 2 * 2, y, 2, 2, IRON[3])
    rust(p, rects((2, 8, 45, 23)), 0.06)
    return p.im


def structural_panel() -> Image.Image:
    """Bracing: oak beams crossed in an X inside an iron-cornered frame, one beam split and sagging."""
    p = Pix(48, 32, seed=223)
    backdrop(p)
    shade_mask(p, rects((0, 0, 47, 31)), OAK, grain=0.05, base=2)
    p.rect(3, 3, 42, 26, SOOT[0])
    for a, b in (((3, 3), (44, 28)), ((44, 3), (3, 28))):
        for d, c in ((-2, WOOD[3]), (-1, WOOD[3]), (0, WOOD[2]), (1, WOOD[2]), (2, WOOD[1]), (3, WOOD[0])):
            p.line(a[0], a[1] + d, b[0], b[1] + d, c)
    p.line(4, 29, 22, 15, SOOT[0])                                  # the split in one beam
    p.line(5, 30, 23, 16, WOOD[0])
    for x, y in ((22, 14), (23, 15), (24, 16), (25, 14)):
        p.px(x, y, PALE_WOOD[3])
    for x, y in ((0, 0), (41, 0), (0, 27), (41, 27)):
        p.rect(x, y, 7, 5, IRON[2])
        p.hline(x, y, 7, IRON[4])
        p.px(x + 2, y + 2, BRASS[4])
        p.px(x + 5, y + 2, BRASS[3])
    p.frame(0, 0, 48, 32, SHADOW)
    gear(p, 24, 16, 3, ramp=IRON)
    rust(p, rects((0, 0, 47, 31)), 0.02)
    return p.im


# ---------------------------------------------------------------------------------------------- small tiles (16x16, 16x32)


def tile_bg() -> Image.Image:
    p = Pix(16, 16, seed=231)
    backdrop(p)
    return p.im


def component_bg() -> Image.Image:
    """Recessed slot where a part sits: lit lower-right lip, dark upper-left shade (it is sunk, not raised)."""
    p = Pix(16, 16, seed=232)
    backdrop(p)
    p.rect(1, 1, 14, 14, SOOT[0])
    p.hline(1, 1, 14, SHADOW)
    p.vline(1, 1, 14, SHADOW)
    p.hline(2, 14, 13, OAK[3])
    p.vline(14, 2, 13, OAK[3])
    p.dither(2, 2, 12, 12, SOOT[1], 0.3)
    return p.im


def reinforced() -> Image.Image:
    p = Pix(16, 16, seed=233)
    backdrop(p)
    shade_mask(p, rects((0, 0, 15, 15)), IRON, base=2)
    p.line(2, 13, 13, 2, IRON[1])
    p.line(3, 13, 13, 3, IRON[3])
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        p.px(x, y, BRASS[4])
        p.px(x + (1 if x < 8 else -1), y + 1 if y < 8 else y - 1, IRON[0])
    rust(p, rects((1, 1, 14, 14)), 0.05)
    return p.im


def screw(set_: bool) -> Image.Image:
    """An empty bolt hole (base) or an iron bolt turned home with its slot and shadow (set)."""
    p = Pix(16, 16, seed=235 + set_)
    backdrop(p)
    shade_mask(p, rects((0, 0, 15, 15)), OAK, base=2)
    if set_:
        p.ellipse(3, 3, 11, 11, SHADOW)
        p.ellipse(3, 3, 10, 10, IRON[2])
        p.ellipse(4, 4, 7, 7, IRON[3])
        p.px(5, 5, IRON[4])
        p.px(6, 4, IRON[4])
        p.line(5, 9, 10, 4, SHADOW)
        p.line(5, 10, 10, 5, IRON[1])
        p.hline(11, 11, 2, OAK[0])
    else:
        p.ellipse(3, 3, 10, 10, IRON[1])
        p.ellipse(4, 4, 8, 8, SOOT[0])
        p.px(4, 5, IRON[0])
        p.hline(5, 11, 6, IRON[3])
        p.px(11, 8, IRON[3])
    return p.im


def disarm(step: int) -> Image.Image:
    """A sprung pin drawn from home (1) to pulled clear (4), so the four frames read as one action."""
    p = Pix(16, 16, seed=240 + step)
    backdrop(p)
    shade_mask(p, rects((1, 1, 14, 14)), IRON, base=1)
    p.rect(5, 5, 6, 6, SOOT[0])
    p.frame(4, 4, 8, 8, SHADOW)
    lift = (0, 2, 4, 7)[step - 1]
    if step < 4:
        sx, sy = 5, 5
        p.rect(sx, sy + 5 - lift + 0, 6, 1, SHADOW)
        p.rect(6, 6 - lift // 2, 4, 6, BRASS[2])
        p.vline(6, 6 - lift // 2, 6, BRASS[4])
        p.vline(9, 6 - lift // 2, 6, BRASS[1])
        p.rect(5, 4 - lift // 2, 6, 2, BRASS[3])
        p.hline(5, 4 - lift // 2, 6, BRASS[4])
        for k in range(lift // 2):
            p.px(8, 12 - k, SHADOW)
    else:
        p.px(7, 8, BRASS[1])
        p.rect(2, 12, 5, 2, BRASS[2])
        p.hline(2, 12, 5, BRASS[4])
        p.px(7, 13, SHADOW)
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        p.px(x, y, IRON[3])
    return p.im


def swiper(locked: bool) -> Image.Image:
    """Key slot: an oak post with a brass-lipped track and a sliding latch; locked shows an iron padlock across it."""
    p = Pix(16, 32, seed=250 + locked)
    backdrop(p)
    shade_mask(p, rects((1, 0, 14, 31)), OAK, grain=0.1, base=2)
    p.rect(6, 3, 4, 26, SOOT[0])
    p.frame(5, 2, 6, 28, SHADOW)
    p.vline(5, 3, 26, IRON[3])
    p.vline(10, 3, 26, IRON[2])
    p.hline(4, 1, 8, BRASS[3])
    p.hline(4, 30, 8, BRASS[1])
    for y in (5, 11, 17, 23):
        p.px(3, y, BRASS[4])
        p.px(12, y, BRASS[2])
    y0 = 20 if locked else 7
    p.rect(5, y0, 6, 7, BRASS[2])                                  # the slider
    p.hline(5, y0, 6, BRASS[4])
    p.vline(5, y0, 7, BRASS[3])
    p.hline(5, y0 + 6, 6, BRASS[1])
    p.px(8, y0 + 3, SHADOW)
    if locked:
        p.rect(3, 11, 10, 8, IRON[2])                              # padlock body
        p.hline(3, 11, 10, IRON[4])
        p.vline(3, 11, 8, IRON[3])
        p.hline(3, 18, 10, IRON[0])
        p.frame(4, 5, 8, 7, IRON[3])
        p.frame(5, 6, 6, 6, SHADOW)
        p.px(8, 14, SHADOW)
        p.vline(8, 15, 2, SHADOW)
        p.px(5, 12, BRASS[4])
    return p.im


# ---------------------------------------------------------------------------------------------- cords


def cord(name: str) -> Image.Image:
    """A twisted wine-red cord on the plank tile, with a brass ferrule wherever it ends inside the tile."""
    p = Pix(16, 16, seed=260)
    backdrop(p)
    segs = {
        "horizontal": ("h", 0, 15), "horizontal_left": ("h", 0, 8), "horizontal_right": ("h", 7, 15),
        "vertical": ("v", 0, 15), "vertical_upper": ("v", 0, 8), "vertical_lower": ("v", 7, 15),
    }

    def run(kind: str, a: int, b: int, at: int = 7) -> None:
        for i in range(a, b + 1):
            x, y = (i, at) if kind == "h" else (at, i)
            dx, dy = (0, 1) if kind == "h" else (1, 0)
            p.px(x - dx * 0 + dx, y + dy, SHADOW)
            twist = i % 3
            p.px(x, y, CORD[2] if twist == 0 else CORD[1] if twist == 1 else CORD[0])
            p.px(x + dx, y + dy, CORD[1] if twist == 2 else CORD[0] if twist == 0 else CORD[2])
            p.px(x + 2 * dx, y + 2 * dy, SHADOW)
            p.px(x - dx, y - dy, SHADOW)

    def ferrule(x: int, y: int) -> None:
        p.rect(x - 1, y - 1, 4, 4, BRASS[2])
        p.hline(x - 1, y - 1, 4, BRASS[4])
        p.vline(x - 1, y - 1, 4, BRASS[3])
        p.hline(x - 1, y + 2, 4, BRASS[0])

    if name in segs:
        kind, a, b = segs[name]
        run(kind, a, b)
        if a != 0:
            ferrule(*( (7, a + 1) if kind == "v" else (a + 1, 7)))
        if b != 15:
            ferrule(*((7, b - 3) if kind == "v" else (b - 3, 7)))
        return p.im
    horiz = "left" if "left" in name else "right"
    vert = "upper" if "upper" in name else "lower"
    run("h", 0, 8) if horiz == "left" else run("h", 7, 15)
    run("v", 0, 8) if vert == "upper" else run("v", 7, 15)
    p.rect(6, 6, 4, 4, CORD[1])                                     # the knot where they turn
    p.hline(6, 6, 4, CORD[2])
    p.px(7, 7, CORD[0])
    p.frame(5, 5, 6, 6, SHADOW)
    p.px(6, 6, CORD[2])
    p.px(8, 8, CORD[0])
    return p.im


def add(name: str, fn: Draw) -> None:
    ASSETS[f"items~items_broken_machine@{name}.png"] = fn


add("broken_alarm", partial(alarm, False))
add("broken_alarm_", partial(alarm, True))
add("broken_furnace", partial(furnace, False))
add("broken_furnace_", partial(furnace, True))
add("broken_moisture_farm", partial(moisture, False))
add("broken_moisture_farm_", partial(moisture, True))
add("rm_machine_large", partial(frame_casing, 64, 48, 271, ((20, 24, 7), (44, 24, 7), (32, 38, 3)), False))
add("rm_machine_medium", partial(frame_casing, 48, 48, 272, ((24, 24, 8), (24, 40, 2)), False))
add("rm_machine_small", partial(frame_casing, 32, 48, 273, ((16, 20, 5),), True))
add("rm_access_panel", partial(hatch, 48, 48, 281, True))
add("rm_access_panel_base", partial(hatch, 48, 48, 282, False))
add("rm_access_panel_small", partial(hatch, 32, 32, 283, True))
add("rm_access_panel_base_small", partial(hatch, 32, 32, 284, False))
add("rm_anti_tamper", anti_tamper)
add("rm_structural_panel", structural_panel)
add("rm_background", tile_bg)
add("rm_component_background", component_bg)
add("rm_reinforced_panel", reinforced)
add("rm_screw_base", partial(screw, False))
add("rm_screw_set", partial(screw, True))
add("rm_card_swiper", partial(swiper, False))
add("rm_card_swiper_lock", partial(swiper, True))
for i in range(1, 5):
    add(f"rm_disarm{i}", partial(disarm, i))
for n in ("horizontal", "horizontal_left", "horizontal_right", "vertical", "vertical_upper", "vertical_lower",
          "left_lower", "left_upper", "right_lower", "right_upper"):
    add(f"rm_wire_{n}", partial(cord, n))
_ = (RUST, GLASS, LEATHER, PARCHMENT, rim, pipe, tile_out)
