"""Tool-family items, part 2: hand tools and carried things. A scanner is a brass ear-trumpet, a screwdriver an awl, a wire
cutter forged nippers, a welder a brass blowpipe, a label gun a wax-seal press, a tablet a slate in an oak frame."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_tools import (AMETHYST, BOX, COPPER, INK, LIGHT, SLATE, TEAL, ball, bitmap, corners, finish, glass, grain, hcyl,
                           lamp, plank_box, r5, ring, rivets, slab, solid, sparkle, strap_h, strap_v, tube, vcyl)
from palette import BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Pix, Ramp, mix, rgb

STEEL: Ramp = (rgb("#25262e"), rgb("#4a4c58"), rgb("#7a7d8c"), rgb("#a6aab8"), rgb("#d4d8e2"))


def awl() -> Image.Image:
    """A screwdriver as an awl: pale-wood handle with wine leather wraps, brass ferrule, tapering iron blade."""
    p = Pix(16, 48, seed=1)
    solid(p, [(6, 2), (9, 2), (10, 5), (10, 14), (9, 18), (6, 18), (5, 14), (5, 5)], PALE_WOOD)
    for y in (6, 8, 10, 12):                         # leather wrap
        p.hline(5, y, 6, WINE[2])
        p.px(5, y, WINE[3])
        p.px(10, y, WINE[0])
    p.hline(5, 7, 6, WINE[1]) if False else None
    p.px(6, 3, PALE_WOOD[4])
    slab(p, 5, 18, 6, 3, BRASS)
    p.px(6, 19, BRASS[4])
    tube(p, (8, 21), (8, 38), 2, STEEL)
    solid(p, [(7, 38), (9, 38), (8, 46)], STEEL)
    p.vline(7, 21, 17, STEEL[4])
    return finish(p)


def nippers() -> Image.Image:
    """Wire cutters as forged nippers: steel jaws, a rivet pivot, wine-leather grips."""
    p = Pix(16, 48, seed=2)
    solid(p, [(5, 4), (8, 4), (8, 21), (5, 24)], STEEL)             # left jaw
    solid(p, [(9, 5), (12, 4), (11, 24), (8, 21)], STEEL)           # right jaw
    p.vline(8, 5, 12, SHADOW)                                       # the gap between the cutting edges
    p.px(8, 17, SHADOW)
    tube(p, (6, 24), (4, 43), 4, WINE)                              # grips cross over at the pivot
    tube(p, (10, 24), (12, 43), 4, WINE)
    p.vline(3, 33, 8, WINE[4]) if False else None
    for k, y in enumerate((29, 33, 37, 41)):
        p.px(5 - k // 2 - 1 + 1, y, WINE[4])
    p.rect(6, 21, 4, 4, IRON[1])
    p.px(7, 22, BRASS[4])
    p.px(8, 22, BRASS[3])
    p.px(7, 23, BRASS[2])
    p.px(8, 23, BRASS[1])
    return finish(p)


def blowpipe() -> Image.Image:
    """A welder as a brass blowpipe: a bent nozzle with a flame, a fuel bulb, a pale-wood grip wrapped in leather."""
    p = Pix(16, 64, seed=3)
    tube(p, (9, 17), (12, 11), 3, BRASS)                            # nozzle
    tube(p, (12, 11), (13, 9), 2, STEEL)
    p.px(14, 7, FLAME[4])
    p.px(14, 8, FLAME[3])
    p.px(15, 9, FLAME[2]) if False else None
    p.px(13, 7, FLAME[2])
    p.px(14, 6, FLAME[1])
    slab(p, 5, 17, 7, 3, BRASS)
    ball(p, 3, 20, 10, BRASS)                                       # fuel bulb
    p.rect(7, 24, 2, 3, BRASS[1])
    slab(p, 5, 29, 7, 2, IRON)
    solid(p, [(5, 31), (11, 31), (11, 49), (10, 51), (6, 51), (5, 49)], PALE_WOOD)
    for y in (34, 37, 40, 43, 46):
        p.hline(5, y, 6, LEATHER[2])
        p.hline(5, y + 1, 6, LEATHER[1])
        p.px(5, y, LEATHER[3])
    slab(p, 5, 51, 7, 3, IRON)
    p.px(8, 52, BRASS[3])
    p.vline(8, 54, 4, IRON[2])
    p.px(8, 58, BRASS[2])
    return finish(p)


def trumpet() -> Image.Image:
    """A scanner as a brass ear-trumpet: wide bell with a dark throat, a stem and a leather-wrapped grip."""
    p = Pix(32, 48, seed=4)
    solid(p, [(12, 15), (22, 20), (20, 28), (14, 28)], BRASS)       # the cone behind the bell
    p.ellipse(4, 3, 18, 21, BRASS[2])
    p.ellipse(5, 4, 16, 19, BRASS[3])
    p.ellipse(7, 6, 13, 15, BRASS[1])
    p.ellipse(8, 8, 10, 11, BRASS[0])
    p.ellipse(10, 10, 6, 7, SHADOW)
    p.hline(8, 5, 6, BRASS[4])
    p.px(5, 8, BRASS[4])
    for k in range(5):                                              # glints along the rim
        p.px(6 + k, 4 + (1 if k in (0, 4) else 0), BRASS[4])
    slab(p, 14, 28, 7, 3, BRASS)
    tube(p, (17, 31), (21, 42), 5, LEATHER)
    for k in range(4):
        p.hline(17 + k, 33 + k * 2, 5, LEATHER[1])
    slab(p, 18, 42, 6, 3, IRON)
    return finish(p)


def magnifier() -> Image.Image:
    """A magnifying glass: brass ring around a pane with a glint, a wooden handle with a brass ferrule."""
    p = Pix(48, 48, seed=5)
    tube(p, (16, 31), (6, 41), 4, PALE_WOOD)
    tube(p, (20, 27), (14, 33), 5, BRASS)
    for k in (0, 1, 2):
        p.px(9 + k, 38 - k, WOOD[2])
    p.ellipse(15, 5, 27, 27, BRASS[2])
    ring(p, 28, 18, 13, 13, BRASS, 3)
    p.ellipse(18, 8, 21, 21, GLASS[3])
    p.ellipse(20, 10, 17, 17, GLASS[4])
    for k in range(5):                                              # glint arc and a tiny highlight
        p.px(21 + k, 14 - k // 2, GLASS[4])
    p.px(21, 15, GLASS[4])
    p.vline(21, 16, 3, GLASS[4])
    p.ellipse(31, 20, 4, 5, GLASS[4])
    p.px(33, 21, LINEN[3])
    p.dither(22, 22, 16, 7, GLASS[3], 0.4)
    return finish(p)


def seal_press(blue: bool) -> Image.Image:
    """A label gun as a wax-seal press: a turned knob, an iron body with a brass collar, and ribbons with wax seals hanging."""
    wax: Ramp = NAVY if blue else WINE
    p = Pix(32, 48, seed=6 + blue)
    solid(p, [(8, 6), (20, 5), (22, 9), (21, 13), (9, 13), (7, 10)], wax)          # the knob
    p.hline(9, 7, 7, r5(wax)[4])
    slab(p, 11, 13, 7, 4, IRON)
    slab(p, 5, 17, 18, 10, IRON)
    slab(p, 5, 17, 18, 3, BRASS)
    p.rect(8, 22, 6, 3, SHADOW)
    p.rect(16, 22, 5, 3, IRON[1])
    rivets(p, ((7, 22), (19, 22)))
    solid(p, [(23, 19), (28, 21), (28, 29), (24, 29)], IRON)                      # the side lever
    p.px(25, 23, BRASS[3])
    for x, ln, col in ((8, 14, PARCHMENT), (13, 17, wax), (18, 12, LINEN)):       # ribbons with seals
        p.vline(x, 27, ln, col[2])
        p.vline(x + 1, 27, ln, col[3])
        p.vline(x + 2, 27, ln, col[1])
        ball(p, x - 1, 27 + ln - 3, 6, wax if col is not LINEN else NAVY if not blue else WINE)
        p.px(x, 27 + ln - 2, r5(wax)[4])
    return finish(p)


def circlet() -> Image.Image:
    """A mind-reprogrammer as a circlet: an iron band over a linen pad with two coiled brass horns."""
    p = Pix(48, 32, seed=7)

    def band(x: int, off: int) -> int:
        return round(7 + 13 * (1 - ((x - 24) / 18) ** 2) + off)

    for x in range(6, 43):                                           # linen pad with a violet trim
        y0 = band(x, 3)
        p.vline(x, y0, 5, LINEN[2])
        p.px(x, y0, LINEN[3])
        p.px(x, y0 + 4, LINEN[1])
        p.px(x, y0 + 3, AMETHYST[3])
    for x in range(6, 43):                                           # the iron band
        y0 = band(x, -1)
        p.vline(x, y0, 4, IRON[2])
        p.px(x, y0, IRON[4])
        p.px(x, y0 + 1, IRON[3])
        p.px(x, y0 + 3, IRON[0])
        if (x - 6) % 7 == 3:
            p.px(x, y0 + 1, BRASS[4])
    for sx, d in ((6, 1), (36, -1)):                                 # coiled horns
        ring(p, sx + 4, 6, 4, 4, BRASS, 2)
        p.vline(sx + 4 - d * 3 + (0 if d == 1 else 2), 9, 3, BRASS[2])
        p.px(sx + 4, 6, BRASS[3])
    ball(p, 21, 3, 6, AMETHYST)
    return finish(p)


def slate() -> Image.Image:
    """A dealmaker as a slate in an oak frame with brass handles at both sides, chalked with a tally."""
    p = Pix(48, 32, seed=8)
    slab(p, 5, 4, 38, 24, OAK)
    corners(p, 5, 4, 38, 24, 2)
    grain(p, 6, 5, 36, 22, OAK)
    p.rect(8, 7, 32, 18, SLATE[1])
    p.hline(8, 7, 32, SLATE[0])
    p.vline(8, 7, 18, SLATE[0])
    p.hline(8, 24, 32, SLATE[3])
    p.vline(39, 7, 18, SLATE[3])
    p.dither(9, 8, 30, 5, SLATE[2], 0.25)
    for k in range(4):                                               # chalk tally and a coin
        p.vline(12 + k * 2, 11, 5, LINEN[3])
    p.line(11, 16, 18, 11, LINEN[2])
    p.ellipse(25, 11, 6, 6, LINEN[2])
    p.ellipse(26, 12, 4, 4, SLATE[1])
    p.hline(24, 20, 11, LINEN[1])
    for x in (2, 41):
        ring(p, x + 2, 16, 2, 4, BRASS, 1)
    rivets(p, ((6, 5), (41, 5), (6, 26), (41, 26)))
    return finish(p)


def astrolabe(lit: bool) -> Image.Image:
    """A desequencer as an astrolabe: a brass ring on four iron bolts, a rete over a dark disc; lit, a glowing chart."""
    p = Pix(48, 48, seed=9)
    p.rect(21, 2, 6, 5, BRASS[1])
    ring(p, 24, 4, 3, 3, BRASS, 1)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):             # diagonal bolts
        cx, cy = 24 + dx * 17, 24 + dy * 17
        p.rect(cx - 3, cy - 3, 7, 7, IRON[2])
        p.hline(cx - 3, cy - 3, 7, IRON[4])
        p.vline(cx - 3, cy - 3, 7, IRON[3])
        p.hline(cx - 3, cy + 3, 7, IRON[0])
        p.px(cx, cy, BRASS[3])
    ball(p, 6, 6, 36, BRASS)
    p.ellipse(10, 10, 28, 28, BRASS[1])
    p.ellipse(11, 11, 26, 26, PARCHMENT[2] if lit else SLATE[1])
    if lit:
        p.ellipse(13, 13, 22, 22, PARCHMENT[3])
        p.dither(11, 24, 26, 14, PARCHMENT[2], 0.3)
        for r_ in (9, 5):
            p.ellipse(24 - r_, 24 - r_, 2 * r_ + 1, 2 * r_ + 1, CLEAR) if False else None
        for a in range(0, 360, 30):
            import math
            x = round(24 + 10 * math.cos(math.radians(a)))
            y = round(24 + 10 * math.sin(math.radians(a)))
            p.px(x, y, INK)
        p.line(24, 24, 31, 16, EMBER)
        p.line(24, 24, 18, 31, INK)
        p.hline(16, 24, 17, INK)
        p.vline(24, 16, 17, INK)
        p.glow(24, 24, 12, FLAME[3], 0.3)
    else:
        for a in ((16, 17), (30, 15), (21, 30), (32, 29), (27, 22)):
            p.px(*a, SLATE[4])
        p.line(24, 24, 29, 18, SLATE[3])
        p.hline(16, 24, 17, SLATE[2])
        p.vline(24, 16, 17, SLATE[2])
        p.px(15, 15, SLATE[3])
        p.px(16, 15, SLATE[3])
    ball(p, 22, 22, 5, BRASS)
    slab(p, 18, 41, 12, 4, IRON)
    p.rect(20, 42, 2, 2, FLAME[3] if lit else SLATE[3])
    p.rect(24, 42, 2, 2, GREEN2 if lit else SLATE[3])
    return finish(p)


GREEN2 = rgb("#8fd068")


def note() -> Image.Image:
    """A post-it as a torn ochre parchment scrap pinned with a brass tack, a curled corner, a few ink lines."""
    p = Pix(32, 32, seed=10)
    solid(p, [(5, 6), (13, 5), (20, 6), (27, 5), (27, 13), (26, 21), (21, 26), (5, 26), (6, 18), (5, 12)], CLAY if False else PARCHMENT)
    p.rect(6, 7, 20, 18, rgb("#d9a85a"))
    p.dither(6, 7, 20, 18, rgb("#e8bf72"), 0.4)
    for y, ln in ((10, 14), (13, 16), (16, 12), (19, 15)):
        p.hline(8, y, ln, INK)
        p.hline(8, y + 1, ln, mix(INK, rgb("#d9a85a"), 0.6)) if False else None
    p.poly([(21, 26), (27, 20), (26, 26)], PARCHMENT[1])
    p.line(22, 25, 26, 21, PARCHMENT[0])
    ball(p, 14, 3, 4, BRASS)
    p.px(15, 4, BRASS[4])
    return finish(p)


def surgery() -> Image.Image:
    """Surgeon's kit: an open leather roll in two halves, tools standing in stitched pockets (scissors, forceps, saw, hooks)."""
    p = Pix(64, 32, seed=11)
    slab(p, 3, 2, 29, 27, WINE)
    slab(p, 32, 2, 29, 27, WINE)
    p.vline(31, 3, 25, WINE[0])
    p.vline(32, 3, 25, WINE[0])
    for x0 in (3, 32):                                               # stitching round each half
        for i in range(x0 + 2, x0 + 27, 2):
            p.px(i, 4, LINEN[2])
            p.px(i, 26, LINEN[1])
    # a strap with pockets
    p.rect(5, 17, 25, 8, WINE[1])
    p.hline(5, 17, 25, WINE[3])
    p.rect(34, 17, 25, 8, WINE[1])
    p.hline(34, 17, 25, WINE[3])
    for x in list(range(10, 29, 5)) + list(range(39, 58, 5)):
        p.vline(x, 18, 7, WINE[0])
        p.px(x + 1, 18, WINE[3])
    # left half: scissors, scalpel, forceps
    tools = [(8, 6, 17, "scis"), (13, 5, 17, "scal"), (19, 5, 17, "forc"), (25, 6, 17, "scal")]
    tools += [(37, 5, 17, "saw"), (43, 6, 17, "hook"), (49, 5, 17, "forc"), (55, 6, 17, "scal")]
    for x, y0, y1, kind in tools:
        if kind == "scal":
            p.vline(x, y0, 6, STEEL[4])
            p.vline(x + 1, y0 + 1, 5, STEEL[2])
            p.vline(x, y0 + 6, y1 - y0 - 6, BRASS[3])
            p.vline(x + 1, y0 + 6, y1 - y0 - 6, BRASS[1])
        elif kind == "forc":
            p.line(x - 1, y0, x, y0 + 7, STEEL[3])
            p.line(x + 2, y0, x + 1, y0 + 7, STEEL[2])
            p.vline(x, y0 + 7, y1 - y0 - 7, STEEL[3])
            p.vline(x + 1, y0 + 7, y1 - y0 - 7, STEEL[1])
        elif kind == "scis":
            p.line(x - 1, y0, x + 2, y0 + 7, STEEL[3])
            p.line(x + 2, y0, x - 1, y0 + 7, STEEL[2])
            p.rect(x - 2, y0 + 8, 3, 3, BRASS[3])
            p.rect(x + 1, y0 + 8, 3, 3, BRASS[2])
            p.px(x, y0 + 9, WINE[1])
            p.px(x + 2, y0 + 9, WINE[1])
        elif kind == "saw":
            p.vline(x + 1, y0, 8, STEEL[2])
            for k in range(0, 8, 2):
                p.px(x, y0 + k, STEEL[4])
            p.vline(x + 1, y0 + 8, y1 - y0 - 8, BRASS[2])
            p.vline(x + 2, y0 + 8, y1 - y0 - 8, BRASS[1])
        else:
            p.vline(x, y0 + 1, 8, STEEL[3])
            p.px(x + 1, y0, STEEL[3])
            p.px(x + 2, y0 + 1, STEEL[2])
            p.vline(x, y0 + 9, y1 - y0 - 9, BRASS[2])
    p.rect(28, 12, 6, 6, BRASS[2])                                  # the tie-strap buckle
    p.hline(28, 12, 6, BRASS[4])
    p.rect(30, 14, 2, 2, SHADOW)
    return finish(p)


def toolbox(old: bool) -> Image.Image:
    """A carpenter's toolbox: iron-bound wood, an arched handle and a brass hasp. The old one is dark, chipped and rusted."""
    body: Ramp = OAK if old else PALE_WOOD
    p = Pix(64, 48, seed=12 + old)
    x, w = 6, 53
    # handle
    p.ellipse(22, 3, 20, 14, IRON[2] if not old else IRON[1])
    p.ellipse(24, 5, 16, 14, CLEAR)
    p.hline(25, 4, 14, IRON[4])
    # lid and body
    plank_box(p, x, 10, w, 11, body, vertical=False, grained=True)
    plank_box(p, x, 21, w, 21, body, vertical=False, grained=True)
    p.hline(x, 21, w, SHADOW)
    p.hline(x + 1, 22, w - 2, r5(body)[3])
    for xx in (x, x + w - 6):
        strap_v(p, xx, 10, 32, 6, IRON, False)
        rivets(p, ((xx + 2, 12), (xx + 2, 17), (xx + 2, 26), (xx + 2, 37)))
    slab(p, 26, 17, 12, 10, BRASS)                                   # hasp
    p.rect(30, 21, 4, 4, SHADOW)
    p.px(31, 22, BRASS[4])
    p.hline(27, 18, 10, BRASS[4])
    corners(p, x, 10, w, 32, 1)
    if old:
        p.rng.seed(3)
        for _ in range(30):                                          # scratches and chips
            xx, yy = p.rng.randrange(x + 8, x + w - 8), p.rng.randrange(12, 40)
            p.hline(xx, yy, p.rng.randrange(2, 5), OAK[0])
        for xx, yy in ((9, 24), (12, 30), (54, 33), (50, 14), (8, 38)):    # rust runs on the straps
            p.vline(xx, yy, 3, COPPER[2])
            p.px(xx, yy, COPPER[3])
        p.line(36, 24, 40, 33, SHADOW)                               # a split board
        p.line(40, 33, 38, 40, SHADOW)
        p.rect(44, 40, 4, 2, CLEAR)                                  # a chipped corner
        p.dither(x + 2, 11, w - 4, 9, SHADOW, 0.12)
    else:
        for k in range(8):                                           # varnish glints
            p.px(12 + k, 20 - k // 2 - 8 + 8, r5(body)[4]) if False else None
        p.hline(12, 12, 8, PALE_WOOD[4])
        p.hline(14, 28, 6, PALE_WOOD[4])
    return finish(p)


def kit_chest() -> Image.Image:
    """The storage-bay expansion kit: a small iron chest with an arched lid, a ring handle and a brass lock."""
    p = Pix(32, 32, seed=13)
    plank_box(p, 3, 12, 26, 15, IRON, vertical=True, grained=False)
    solid(p, [(3, 12), (4, 7), (8, 4), (23, 4), (27, 7), (28, 12)], IRON)
    p.hline(5, 6, 20, IRON[4])
    p.hline(3, 12, 26, SHADOW)
    for x in (4, 25):
        strap_v(p, x, 5, 22, 3, IRON, False)
        rivets(p, ((x + 1, 8), (x + 1, 16), (x + 1, 24)))
    slab(p, 13, 11, 6, 6, BRASS)
    p.px(15, 13, SHADOW)
    p.px(16, 14, SHADOW)
    ring(p, 16, 4, 4, 2, BRASS, 1)
    p.hline(5, 26, 22, AMETHYST[2])
    return finish(p)


def alarm(red: bool) -> Image.Image:
    """An alarm board: oak panel with a lantern window and a brass keypad on the left, a brass bell on the right; red, the lantern burns."""
    p = Pix(48, 48, seed=14)
    slab(p, 4, 6, 41, 37, OAK)
    grain(p, 5, 7, 39, 35, OAK)
    p.vline(24, 7, 35, OAK[0])
    p.vline(25, 7, 35, OAK[3])
    corners(p, 4, 6, 41, 37, 2)
    strap_h(p, 4, 9, 41, 3, IRON)
    strap_h(p, 4, 37, 41, 3, IRON)
    # lantern window
    slab(p, 7, 13, 15, 12, IRON)
    p.rect(9, 15, 11, 8, EMBER if False else (SHADOW))
    if red:
        p.rect(9, 15, 11, 8, WINE[3])
        p.glow(14, 19, 6, FLAME[3], 1.2)
        p.rect(12, 17, 5, 4, FLAME[3])
        p.rect(13, 18, 3, 2, FLAME[4])
    else:
        p.rect(9, 15, 11, 8, GLASS[1])
        p.px(10, 16, GLASS[3])
        p.px(11, 17, GLASS[3])
    # keypad
    for j in range(3):
        for i in range(3):
            slab(p, 8 + i * 5, 27 + j * 3 - 0, 4, 3, BRASS if (i + j) % 2 == 0 else IRON, False) if False else None
    for j in range(3):
        for i in range(3):
            x, y = 9 + i * 4, 27 + j * 3
            p.rect(x, y, 3, 2, BRASS[2])
            p.hline(x, y, 3, BRASS[4])
            p.hline(x, y + 2, 3, SHADOW)
    # bell on its bracket
    p.rect(33, 12, 3, 4, IRON[3])
    p.hline(28, 12, 12, IRON[2])
    solid(p, [(31, 16), (38, 16), (40, 23), (42, 28), (27, 28), (29, 23)], BRASS)
    p.hline(27, 28, 16, BRASS[1])
    p.hline(28, 29, 14, BRASS[4])
    p.vline(31, 18, 8, BRASS[4])
    ball(p, 32, 29, 4, IRON)
    if red:
        for dx in (-1, 1):                                           # ringing lines
            p.line(24 + (dx > 0) * 21, 18, 24 + (dx > 0) * 21 + dx * 2, 15, FLAME[3])
            p.line(25 + (dx > 0) * 19, 23, 25 + (dx > 0) * 19 + dx * 3, 23, FLAME[3])
    return finish(p)


def bottle_press() -> Image.Image:
    """A bottle printer as a bottling press: a timber cabinet, a cog and rod up top, a glass door with a bottle inside."""
    p = Pix(32, 48, seed=15)
    plank_box(p, 3, 3, 26, 43, OAK, vertical=True)
    corners(p, 3, 3, 26, 43, 1)
    for y in (3, 20, 43):
        strap_h(p, 3, y, 26, 3 if y != 20 else 2, IRON, False)
    p.rect(6, 7, 20, 12, SHADOW)
    p.rect(7, 8, 18, 10, rgb("#241520"))
    p.hline(8, 12, 16, IRON[3])                                       # a rod
    ring(p, 16, 12, 4, 4, BRASS, 2)
    p.px(16, 12, SHADOW)
    for a in ((16, 7), (16, 17), (12, 12), (20, 12)):
        p.px(*a, BRASS[4])
    p.rect(5, 23, 22, 17, IRON[1])
    glass(p, 6, 24, 20, 15, GLASS)
    solid(p, [(14, 38), (13, 31), (15, 29), (15, 26), (17, 26), (17, 29), (19, 31), (18, 38)], TEAL, False)
    p.vline(14, 31, 7, TEAL[4])
    p.px(15, 27, TEAL[4])
    p.hline(14, 38, 5, TEAL[0])
    for x, c in ((20, FLAME[3]), (23, GREEN2)):
        p.rect(x, 41, 2, 2, c)
    p.rect(7, 41, 8, 2, BRASS[2])
    return finish(p)


def ledger_cabinet() -> Image.Image:
    """A storage coordinator as a clerk's cabinet: a tall door with a pinned parchment label beside a grid of small drawers."""
    p = Pix(48, 48, seed=16)
    plank_box(p, 4, 5, 20, 40, PALE_WOOD, vertical=True)
    plank_box(p, 24, 5, 21, 40, OAK, vertical=False)
    corners(p, 4, 5, 41, 40, 2)
    p.vline(24, 6, 38, SHADOW)
    for y in (6, 41):
        strap_h(p, 4, y, 41, 3, IRON)
    # label on the door
    slab(p, 8, 14, 12, 14, PARCHMENT)
    for y in (17, 20, 23, 26):
        p.hline(10, y, 8 if y != 26 else 5, INK)
    p.px(13, 13, BRASS[4])
    ball(p, 19, 32, 3, BRASS)                                          # door pull
    # drawers
    for j in range(4):
        for i in range(3):
            x, y = 27 + i * 6, 10 + j * 8
            slab(p, x, y, 5, 7, OAK, False)
            p.rect(x + 1, y + 1, 3, 2, PARCHMENT[3])
            p.px(x + 2, y + 4, BRASS[4])
    p.rect(25, 41, 19, 2, OAK[0])
    return finish(p)


# ---------------------------------------------------------------------------------------------------- hands, piles

HANDS: dict[str, tuple[Ramp, str]] = {}


def gauntlet(kind: str) -> Image.Image:
    """An inspectable hand: a gauntlet of plates, palm out, fingers up. Black blackened steel, gilded, or bright steel."""
    ramp: Ramp = {"carbon": IRON, "gold": BRASS, "steel": STEEL}[kind]
    p = Pix(32, 48, seed=17)
    solid(p, [(12, 38), (21, 38), (23, 46), (10, 46)], ramp)                       # cuff
    solid(p, [(9, 21), (24, 21), (25, 33), (22, 39), (11, 39), (8, 33)], ramp)     # palm
    for x0, y0, w in ((8, 13, 3), (12, 8, 3), (16, 4, 3), (20, 7, 3)):             # fingers
        solid(p, [(x0, y0), (x0 + w - 1, y0), (x0 + w - 1, 23), (x0, 23)], ramp)
        for y in range(y0 + 4, 21, 4):                                             # plate joints
            p.hline(x0, y, w, r5(ramp)[0])
            p.hline(x0, y + 1, w - 1, r5(ramp)[4])
        p.px(x0 + 1, y0 + 1, r5(ramp)[4])
    solid(p, [(23, 30), (26, 22), (28, 24), (27, 29), (25, 34)], ramp)             # thumb
    p.hline(25, 27, 3, r5(ramp)[0])
    r = r5(ramp)
    p.hline(10, 31, 14, r[0])                                                       # palm plate
    p.hline(11, 32, 11, r[3])
    for x in (12, 16, 20):
        p.px(x, 25, r[4])                                                           # knuckle studs
        p.px(x, 26, r[0])
    p.hline(12, 40, 9, r[0])
    p.hline(12, 41, 9, r[3])
    for x in (13, 16, 19):
        p.px(x, 43, r[4] if kind != "gold" else EMBER)
    if kind == "carbon":
        for y in range(23, 38):                                                     # woven weave
            for x in range(10, 24):
                if p.get(x, y)[3] and (x + y) % 4 == 0:
                    p.px(x, y, IRON[3])
    if kind == "gold":
        p.rect(15, 33, 3, 3, EMBER)                                                 # a ruby set in the palm
        p.px(15, 33, rgb("#f08070"))
        p.hline(14, 32, 5, BRASS[0])
    if kind == "steel":
        p.dither(10, 22, 14, 14, STEEL[4], 0.12)
        p.px(18, 28, STEEL[0])
    return finish(p)


def rings_pile() -> Image.Image:
    """Nuts and bolts as a heap of iron rings, nails and rivets."""
    p = Pix(32, 32, seed=18)
    p.ellipse(5, 20, 22, 6, SHADOW)
    for cx, cy, rx, ry, c in ((9, 18, 5, 4, IRON), (20, 19, 6, 4, STEEL), (14, 14, 6, 5, STEEL), (22, 13, 4, 4, IRON),
                              (11, 21, 5, 4, STEEL), (16, 20, 4, 3, IRON), (7, 12, 3, 3, IRON)):
        ring(p, cx, cy, rx, ry, c, 2 if rx > 3 else 1)
    for x0, y0, x1, y1 in ((5, 8, 11, 12), (18, 8, 24, 11), (14, 24, 22, 26), (10, 23, 5, 25)):
        p.line(x0, y0, x1, y1, IRON[3])
        p.px(x0, y0, STEEL[4])
        p.px(x1, y1, IRON[1])
    for x, y in ((20, 17), (13, 17), (25, 20)):
        p.rect(x, y, 3, 2, BRASS[2])
        p.px(x, y, BRASS[4])
    return finish(p)


def coil() -> Image.Image:
    """A coil of copper wire lying flat: wound rings seen from above, a thick side wall, a loose end."""
    p = Pix(32, 32, seed=19)
    for k in range(5, 0, -1):                                            # side wall: stacked turns
        p.ellipse(4, 11 + k, 24, 13, COPPER[1] if k % 2 else COPPER[0])
    for i, (inset_, c) in enumerate(((0, COPPER[2]), (2, COPPER[3]), (4, COPPER[2]), (6, COPPER[3]), (8, COPPER[2]))):
        p.ellipse(4 + inset_, 8 + inset_ // 2 + 0, 24 - 2 * inset_, 13 - inset_, c)
    p.ellipse(13, 12, 6, 4, SHADOW)
    p.ellipse(14, 13, 4, 2, COPPER[0])
    for x, y in ((8, 11), (11, 9), (16, 8), (7, 14), (10, 12)):
        p.px(x, y, COPPER[4])
    p.hline(10, 8, 7, COPPER[4])
    for x in range(8, 24, 4):                                            # turns showing on the wall
        p.px(x, 22, COPPER[3])
        p.px(x + 2, 24, COPPER[3])
    p.line(24, 20, 29, 23, COPPER[3])
    p.line(24, 21, 29, 24, COPPER[1])
    p.px(29, 23, BRASS[4])
    return finish(p)


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "items~items_tool@screwdriver_s.png": awl,
    "items~items_tool@wirecutter.png": nippers,
    "items~items_tool@welder_s.png": blowpipe,
    "items~items_tool@aug_scanner.png": trumpet,
    "items~items_tool@magnifier.png": magnifier,
    "items~items_tool@labeler.png": partial(seal_press, False),
    "items~items_tool@labeler_blue.png": partial(seal_press, True),
    "items~items_tool@mind_reprogrammer.png": circlet,
    "items~items_tool@dealmaker.png": slate,
    "items~items_tool@desequencer.png": partial(astrolabe, False),
    "items~items_tool@desequencer_r.png": partial(astrolabe, True),
    "items~items_tool@postit.png": note,
    "items~items_tool@surgery_toolkit.png": surgery,
    "items~items_tool2@toolbox_new.png": partial(toolbox, False),
    "items~items_tool2@toolbox_old.png": partial(toolbox, True),
    "items~items_tool2@storage_bay_expansion_kit.png": kit_chest,
    "items~items_tool@alarm_system.png": partial(alarm, False),
    "items~items_tool@alarm_system_r.png": partial(alarm, True),
    "items~items_tool@bottle_printer.png": bottle_press,
    "items~items_tool@storage_coordinator.png": ledger_cabinet,
    "items~items_inspectable@hand_carbon.png": partial(gauntlet, "carbon"),
    "items~items_inspectable@hand_gold.png": partial(gauntlet, "gold"),
    "items~items_inspectable@hand_steel.png": partial(gauntlet, "steel"),
    "items~items_construction@nuts_metal_pile.png": rings_pile,
    "items~items_construction@wire.png": coil,
}
