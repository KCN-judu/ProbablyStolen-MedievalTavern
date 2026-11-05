"""Tool-family items, part 3: the machines as tavern equipment. A blender is a stone mill, a furnace a stone oven, a printer a
timber press with a glass door, a purifier three glass filter columns, the bays are drawered cabinets, the tank an iron-hooped tun."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_tools import (AMETHYST, BOX, COPPER, INK, LIGHT, SLATE, TEAL, WATER, ball, bitmap, corners, finish, glass, grain,
                           hcyl, lamp, plank_box, r5, ring, rivets, slab, solid, sparkle, strap_h, strap_v, tube, vcyl)
from palette import BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, STONE, WINE, WOOD
from pix import CLEAR, Pix, Ramp, mix, rgb

GREEN = rgb("#8fd068")
DEEP = rgb("#120b0e")


def flask(p: Pix, x: int, y: int, w: int, h: int, liquid: Ramp = TEAL, level: float = 0.7) -> None:
    """A round-bottomed glass flask with a neck and a stopper, filled to `level` with a liquid."""
    nw = max(3, w // 3)
    nx = x + (w - nw) // 2
    bh = int(h * 0.62)
    by = y + h - bh
    p.rect(nx, y + 2, nw, h - bh, GLASS[3])
    p.vline(nx, y + 2, h - bh, GLASS[4])
    p.rect(nx, y, nw, 2, BRASS[2])
    p.hline(nx, y, nw, BRASS[4])
    p.ellipse(x, by, w, bh, GLASS[2])
    p.ellipse(x + 1, by + 1, w - 2, bh - 2, GLASS[3])
    top = by + int(bh * (1 - level))
    for yy in range(top, by + bh - 1):
        for xx in range(x + 1, x + w - 1):
            if p.get(xx, yy)[3] and p.get(xx, yy) != (*SHADOW, 255):
                p.px(xx, yy, liquid[3] if xx < x + w // 2 else liquid[2])
    p.hline(x + 2, top, w - 4, liquid[4])
    p.px(x + 2, by + 2, GLASS[4])
    p.px(x + 2, by + 3, GLASS[4])
    p.px(x + w - 3, by + bh - 3, liquid[1])
    for dx, dy in ((w // 2, 2), (w // 2 + 1, 5)):                   # bubbles
        p.px(x + dx, top + dy, liquid[4])


# ---------------------------------------------------------------------------------------------------- workshop pieces

def mill(with_jar: bool) -> Image.Image:
    """A blender as a stone mill: a round stone base, two posts and a millstone cap; the jar variant has a flask between."""
    p = Pix(48, 48, seed=1)
    for y0, h in ((35, 11), (2, 11)):
        p.ellipse(6, y0, 36, h, STONE[1])
        p.ellipse(6, y0 - (1 if y0 < 20 else 0), 36, h - 1, STONE[3])
        p.ellipse(9, y0 + 1, 30, h - 4, STONE[2])
    p.rect(11, 13, 6, 24, STONE[2])
    p.rect(31, 13, 6, 24, STONE[2])
    p.vline(11, 13, 24, STONE[4])
    p.vline(31, 13, 24, STONE[4])
    p.vline(16, 13, 24, STONE[0])
    p.vline(36, 13, 24, STONE[0])
    p.rect(17, 14, 14, 22, DEEP)
    p.rect(17, 14, 14, 2, SHADOW)
    p.ellipse(16, 5, 16, 6, SHADOW)                                  # the throat of the upper stone
    p.ellipse(17, 6, 14, 4, DEEP)
    p.hline(14, 3, 20, STONE[4])
    p.ellipse(15, 34, 18, 6, IRON[1])                                # the lower stone's dish
    p.ellipse(16, 35, 16, 4, IRON[3])
    p.hline(19, 35, 8, IRON[4])
    for x, c in ((15, FLAME[3]), (18, GREEN), (21, FLAME[1])):     # little lamps on the foot
        p.rect(x, 42, 2, 2, c)
    p.hline(25, 43, 8, BRASS[2])
    rivets(p, ((8, 40), (39, 40), (8, 8), (39, 8)))
    if with_jar:
        flask(p, 17, 15, 14, 21)
    return finish(p)


def alchemy_cabinet(with_flask: bool) -> Image.Image:
    """A chem finisher as an alchemist's cabinet: a recipe card and two brass knobs left, an arched bay right."""
    p = Pix(48, 48, seed=2)
    plank_box(p, 3, 7, 44, 39, OAK, vertical=True)
    corners(p, 3, 7, 44, 39, 2)
    ring(p, 24, 5, 10, 4, IRON, 2)
    p.ellipse(5, 3, 40, 3, CLEAR) if False else None
    strap_h(p, 3, 7, 44, 3, IRON)
    strap_h(p, 3, 43, 44, 3, IRON)
    slab(p, 6, 12, 14, 18, IRON)
    p.rect(8, 14, 10, 14, PARCHMENT[3])
    for y in (16, 19, 22, 25):
        p.hline(9, y, 8 if y != 25 else 5, INK)
    p.px(8, 14, PARCHMENT[4])
    for x in (9, 14):
        ball(p, x, 33, 5, BRASS)
        p.px(x + 2, 35, SHADOW)
    slab(p, 6, 40 - 2, 14, 3, BRASS)
    p.ellipse(23, 12, 21, 28, IRON[2])                                 # arched bay
    p.rect(23, 26, 21, 14, IRON[2])
    p.ellipse(25, 14, 17, 24, DEEP)
    p.rect(25, 26, 17, 13, DEEP)
    p.hline(25, 38, 17, TEAL[1])
    p.hline(25, 39, 17, TEAL[0])
    p.vline(23, 26, 14, IRON[4])
    p.px(27, 17, IRON[4])
    p.px(26, 19, IRON[4])
    if with_flask:
        flask(p, 28, 20, 12, 19)
        p.glow(34, 30, 8, TEAL[3], 0.3)
    return finish(p)


def evaporator(with_flask: bool) -> Image.Image:
    """An evaporator as a copper-cornered iron oven: a glowing coil grille above, vent slits below; the flask stands in front."""
    p = Pix(48, 48, seed=3)
    slab(p, 2, 2, 44, 44, IRON)
    corners(p, 2, 2, 44, 44, 2)
    p.rect(5, 6, 38, 18, DEEP)
    p.hline(5, 6, 38, IRON[0])
    for y in (9, 13, 17, 21):                                         # glowing coil
        p.hline(6, y, 36, EMBER if y != 13 else FLAME[1])
        p.hline(6, y + 1, 36, WINE[1])
        p.dither(6, y, 36, 1, FLAME[2], 0.3)
    p.glow(24, 14, 14, FLAME[1], 0.35)
    for y in range(28, 40, 3):                                         # vents
        p.hline(5, y, 38, SHADOW)
        p.hline(5, y + 1, 38, IRON[3])
    for x in (4, 42):
        strap_v(p, x, 3, 42, 2, COPPER, False)
    for x, c in ((8, GREEN), (11, FLAME[3]), (14, EMBER)):
        p.rect(x, 41, 2, 2, c)
    p.hline(26, 42, 14, BRASS[2])
    p.hline(26, 43, 14, BRASS[1])
    rivets(p, ((4, 4), (43, 4), (4, 44), (43, 44)), COPPER)
    if with_flask:
        flask(p, 17, 11, 14, 24, TEAL, 0.75)
    return finish(p)


def oven(on: bool) -> Image.Image:
    """A furnace as a stone oven with a barred mouth and a brass lamp row; lit, fire shows through the bars."""
    p = Pix(48, 48, seed=4)
    slab(p, 2, 3, 44, 43, STONE)
    corners(p, 2, 3, 44, 43, 2)
    for j, y in enumerate(range(5, 44, 6)):                           # masonry courses
        p.hline(3, y, 42, STONE[1])
        off = 4 if j % 2 else 0
        for x in range(4 + off, 44, 9):
            p.vline(x, y + 1, 5, STONE[1])
            p.px(x + 1, y + 1, STONE[4])
    slab(p, 5, 4, 38, 8, IRON)                                         # iron cap with lamps
    for x, c in ((8, FLAME[3] if on else IRON[1]), (12, GREEN if on else IRON[1]), (16, FLAME[1] if on else IRON[1])):
        p.rect(x, 6, 3, 3, SHADOW)
        p.rect(x + 1, 7, 1, 1, c)
    p.rect(27, 6, 13, 4, SHADOW)
    p.rect(28, 7, 11, 2, FLAME[2] if on else IRON[2])
    p.rect(8, 15, 32, 25, IRON[1])                                     # the mouth
    p.rect(10, 17, 28, 21, DEEP)
    if on:
        p.rect(10, 17, 28, 21, WINE[1])
        p.glow(24, 34, 18, FLAME[2], 1.4)
        p.glow(24, 36, 11, FLAME[3], 1.2)
        for x, y in ((14, 30), (20, 27), (28, 29), (34, 32), (24, 24)):
            p.line(x, y + 7, x + 1, y, FLAME[3])
            p.px(x, y, FLAME[4])
        p.hline(10, 37, 28, FLAME[3])
    else:
        p.dither(10, 32, 28, 6, WINE[0], 0.4)
        p.hline(12, 36, 8, EMBER)
    for x in range(13, 38, 5):                                         # bars
        p.vline(x, 16, 23, IRON[3])
        p.vline(x + 1, 16, 23, IRON[0])
    p.hline(10, 26, 28, IRON[2])
    slab(p, 5, 41, 8, 4, COPPER)
    return finish(p)


def grinder() -> Image.Image:
    """A gibber as a hand mill: a wide iron hopper bowl, a barrel body with a crank wheel, a tray and two signal lamps."""
    p = Pix(48, 48, seed=5)
    slab(p, 5, 13, 38, 32, IRON)
    corners(p, 5, 13, 38, 32, 1)
    p.ellipse(6, 2, 36, 15, IRON[2])
    p.ellipse(7, 3, 34, 12, IRON[4])
    p.ellipse(9, 5, 30, 9, IRON[1])
    p.ellipse(12, 7, 24, 6, DEEP)
    p.hline(14, 4, 14, IRON[4])
    for x in (12, 20, 28):                                              # the grist
        p.px(x, 9, STEEL3)
    p.rect(8, 20, 16, 10, IRON[1])
    for x, c in ((11, GREEN), (18, EMBER)):
        ball(p, x, 22, 5, BRASS if False else IRON)
        p.rect(x + 1, 23, 3, 3, c)
    for x in (28, 33, 38):
        p.rect(x, 22, 2, 5, IRON[0])
        p.px(x, 22, IRON[4])
    ring(p, 37, 36, 6, 6, BRASS, 2)                                     # crank wheel
    tube(p, (37, 36), (43, 30), 3, PALE_WOOD)
    p.rect(17, 32, 14, 12, DEEP)
    p.hline(17, 32, 14, IRON[0])
    p.hline(17, 44, 14, IRON[4])
    p.rect(20, 40, 8, 2, STEEL3)
    rivets(p, ((7, 15), (40, 15), (7, 42)))
    return finish(p)


STEEL3 = rgb("#a6aab8")


def brazier(with_flask: bool) -> Image.Image:
    """A heating plate as a clay brazier with embers and an iron arch holding a flask above."""
    p = Pix(48, 48, seed=6)
    ring(p, 24, 17, 18, 15, IRON, 2)
    p.rect(0, 30, 48, 18, CLEAR)
    p.vline(23, 3, 14, IRON[3])
    p.vline(24, 3, 14, IRON[1])
    ball(p, 21, 1, 6, BRASS)
    p.vline(23, 17, 8, IRON[3])
    p.rect(7, 30, 34, 4, IRON[2])
    p.ellipse(7, 29, 34, 8, CLAY0)
    p.ellipse(9, 30, 30, 6, DEEP)
    p.ellipse(12, 31, 24, 4, WINE[1])
    p.glow(24, 33, 11, FLAME[2], 1.3)
    for x, y in ((14, 32), (22, 34), (30, 32), (26, 31)):
        p.px(x, y, FLAME[4])
    p.rect(8, 34, 33, 11, CLAY0)
    vcyl(p, 8, 34, 33, 11, CLAYR)
    p.ellipse(8, 41, 33, 5, CLAYR[1])
    p.hline(8, 38, 33, CLAYR[1])
    p.hline(10, 39, 29, CLAYR[3])
    ball(p, 20, 40, 8, BRASS)
    p.px(23, 43, SHADOW)
    for x in (12, 33):
        p.rect(x, 43, 3, 3, IRON[1])
    if with_flask:
        flask(p, 17, 8, 14, 22)
        p.line(24, 3, 24, 8, IRON[4])
    return finish(p)


CLAY0 = rgb("#3a1d17")
CLAYR: Ramp = (rgb("#3a1d17"), rgb("#6a3426"), rgb("#9a4e33"), rgb("#c06c46"), rgb("#dc9066"))


def hyper_bay() -> Image.Image:
    """A hypertech bay as a dark alcove framed in iron, with an amethyst valance edged in brass fringe."""
    p = Pix(48, 48, seed=7)
    slab(p, 2, 2, 44, 44, IRON)
    corners(p, 2, 2, 44, 44, 2)
    p.rect(5, 12, 38, 29, DEEP)
    p.hline(5, 12, 38, IRON[0])
    for y in range(13, 40, 2):
        p.dither(6, y, 36, 2, rgb("#2a1a3a"), 0.15 + (y - 13) / 90)
    p.hline(5, 40, 38, AMETHYST[1])
    p.hline(5, 41, 38, IRON[0])
    for x in range(3, 45, 6):                                           # scalloped valance
        p.rect(x, 3, 6, 6, AMETHYST[2])
        p.ellipse(x, 6, 6, 5, AMETHYST[2])
        p.vline(x, 3, 7, AMETHYST[3])
        p.px(x + 2, 10, BRASS[3])
        p.px(x + 2, 11, BRASS[1])
    p.hline(3, 4, 42, AMETHYST[4])
    p.hline(3, 3, 42, BRASS[3])
    for x in (4, 42):
        p.vline(x, 12, 30, BRASS[2])
    p.vline(5, 12, 30, BRASS[1])
    p.hline(5, 42, 38, BRASS[2])
    rivets(p, ((4, 44), (43, 44)))
    p.rect(9, 33, 30, 7, DEEP)
    p.dither(9, 31, 30, 2, AMETHYST[1], 0.4)
    return finish(p)


def cabinet(name: str, rows: int, cols: int, closed: int) -> Image.Image:
    """A drawered oak cabinet: iron-strapped cap, drawers that are closed (plank front, brass pull) or open (a dark cavity)."""
    x0, y0, x1, y1 = BOX[name]
    p = Pix(64, 64, seed=8 + closed)
    x, y, w, h = x0 + 1, y0 + 1, x1 - x0 - 2, y1 - y0 - 2
    slab(p, x, y, w, h, OAK)
    corners(p, x, y, w, h, 2)
    cap = 8 if rows == 2 else 7
    slab(p, x, y, w, cap, PALE_WOOD)
    grain(p, x + 1, y + 1, w - 2, cap - 2, PALE_WOOD)
    p.hline(x + 3, y + 2, w - 6, PALE_WOOD[4])
    strap_h(p, x, y + cap, w, 2, IRON, False)
    gy0 = y + cap + 3
    gh = y + h - 3 - gy0
    dw = (w - 6 - (cols - 1) * 3) // cols
    dh = (gh - (rows - 1) * 3) // rows
    n = 0
    for j in range(rows):
        for i in range(cols):
            dx, dy = x + 3 + i * (dw + 3), gy0 + j * (dh + 3)
            if n < closed:
                plank_box(p, dx, dy, dw, dh, PALE_WOOD if (i + j) % 2 else WOOD, vertical=False, grained=False)
                p.hline(dx + 2, dy + 2, dw - 4, r5(WOOD)[1])
                strap_h(p, dx, dy + dh // 2 - 1, dw, 2, IRON, False)
                slab(p, dx + dw // 2 - 3, dy + dh // 2 - 3, 6, 5, BRASS)
                p.rect(dx + dw // 2 - 1, dy + dh // 2 - 1, 2, 2, SHADOW)
                rivets(p, ((dx + 2, dy + 2), (dx + dw - 3, dy + 2)))
            else:
                p.rect(dx, dy, dw, dh, SHADOW)
                p.rect(dx + 1, dy + 1, dw - 2, dh - 2, DEEP)
                for k in range(dh - 2):
                    c = mix((22, 13, 20), (62, 36, 40), k / max(1, dh - 3))
                    p.hline(dx + 1, dy + 1 + k, dw - 2, tuple(int(v) for v in c))
                p.hline(dx, dy + dh - 1, dw, OAK[4])
                p.hline(dx + 1, dy + dh - 2, dw - 2, OAK[3])
            n += 1
    return finish(p)


def press(on: bool) -> Image.Image:
    """A printer as a printing press: an oak frame, a spool window on top and a glass door below; lit, a warm glow and a sheet."""
    p = Pix(48, 48, seed=9)
    plank_box(p, 2, 2, 44, 44, OAK, vertical=True)
    corners(p, 2, 2, 44, 44, 2)
    for y in (2, 43):
        strap_h(p, 2, y, 44, 3, IRON, False)
    p.rect(5, 6, 38, 13, SHADOW)
    p.rect(6, 7, 36, 11, DEEP)
    p.hline(8, 12, 32, IRON[3])
    p.hline(8, 13, 32, IRON[0])
    ball(p, 11, 9, 6, BRASS)
    p.px(13, 11, SHADOW)
    p.vline(39, 8, 9, BRASS[2])
    p.rect(5, 21, 38, 21, IRON[1])
    glass(p, 6, 22, 36, 19, TEAL if False else GLASS, lit=False)
    if on:
        p.rect(7, 23, 34, 17, FLAME[1])
        p.glow(24, 32, 18, FLAME[3], 1.4)
        slab(p, 12, 27, 20, 12, PARCHMENT)
        for y in (30, 33, 36):
            p.hline(14, y, 15 if y != 36 else 9, INK)
        p.hline(7, 23, 34, FLAME[3])
    else:
        p.dither(7, 24, 34, 16, GLASS[2], 0.3)
        p.line(8, 38, 14, 31, GLASS[3])
        p.line(12, 38, 19, 31, GLASS[3])
    for x, c in ((34, FLAME[3] if on else IRON[2]), (37, GREEN if on else IRON[2])):
        p.rect(x, 43, 2, 2, c)
    p.hline(7, 44, 20, BRASS[2])
    rivets(p, ((4, 4), (43, 4)))
    return finish(p)


def magic_lantern() -> Image.Image:
    """A projector as a magic lantern: a brass-lensed iron box with a chimney and vent slits."""
    p = Pix(48, 48, seed=10)
    solid(p, [(8, 11), (40, 11), (44, 16), (44, 38), (40, 42), (8, 42), (4, 38), (4, 16)], IRON)
    p.rect(19, 6, 10, 6, IRON[2])                                       # chimney
    p.hline(17, 5, 14, IRON[4])
    p.rect(17, 5, 14, 2, IRON[3])
    p.hline(21, 8, 6, SHADOW)
    p.px(18, 6, IRON[4])
    for x in (8, 12, 32, 36):                                           # vent slits
        p.vline(x, 14, 6, SHADOW)
        p.vline(x + 1, 14, 6, IRON[3])
    ball(p, 14, 20, 20, BRASS)
    ring(p, 24, 30, 9, 9, BRASS, 3)
    p.ellipse(18, 24, 13, 13, GLASS[1])
    p.ellipse(19, 25, 11, 11, GLASS[3])
    p.ellipse(21, 27, 7, 7, GLASS[2])
    p.px(20, 26, GLASS[4])
    p.px(21, 26, GLASS[4])
    p.px(20, 27, GLASS[4])
    p.px(26, 33, FLAME[3])
    for x in range(8, 40, 3):
        p.px(x, 40, IRON[0])
        p.px(x + 1, 40, IRON[4]) if False else None
    rivets(p, ((7, 14), (40, 14), (7, 39), (40, 39)))
    p.rect(38, 13, 3, 2, FLAME[3])
    return finish(p)


def purifier(variant: str) -> Image.Image:
    """A purifier: a brass cylinder over a gauge strip, three glass filter columns in an oak frame. `on` lights the lamps,
    `w` runs clear water."""
    p = Pix(48, 64, seed=11)
    slab(p, 3, 14, 42, 48, OAK)
    corners(p, 3, 14, 42, 48, 1)
    hcyl(p, 4, 4, 40, 9, BRASS)
    p.vline(4, 4, 9, BRASS[1])
    p.vline(43, 4, 9, BRASS[0])
    for x in (12, 34):
        p.vline(x, 4, 10, BRASS[0])
        p.vline(x + 1, 4, 10, BRASS[4])
    if variant == "w":
        p.rect(18, 6, 13, 5, SHADOW)
        p.rect(19, 7, 11, 3, WATER[3])
        p.hline(19, 7, 11, WATER[4])
    slab(p, 5, 15, 38, 11, IRON)
    ball(p, 7, 16, 9, BRASS)
    p.ellipse(9, 18, 5, 5, PARCHMENT[3])
    p.line(11, 20, 13, 18, EMBER)
    for k, x in enumerate((19, 23, 27)):
        lamp(p, x, 18, 3, 4, variant == "on", FLAME if k != 1 else (GREEN, GREEN, GREEN, GREEN, GREEN))
    p.rect(34, 17, 7, 6, SHADOW)
    p.rect(35, 18, 5, 4, DEEP)
    liquid: Ramp = {"normal": TEAL, "on": TEAL, "w": WATER}[variant]
    for i in range(3):
        x = 6 + i * 12
        p.rect(x, 28, 11, 31, SHADOW)
        p.rect(x + 1, 29, 9, 29, GLASS[1])
        lv = {"normal": 0.55, "on": 0.9, "w": 1.0}[variant]
        top = 29 + int(29 * (1 - lv))
        for yy in range(top, 58):
            p.hline(x + 1, yy, 9, liquid[2])
        p.vline(x + 2, top, 58 - top, liquid[4] if variant != "normal" else liquid[3])
        p.vline(x + 3, top, 58 - top, liquid[3])
        p.vline(x + 8, top, 58 - top, liquid[1])
        p.hline(x + 1, top, 9, liquid[4])
        p.vline(x + 1, 29, 29, GLASS[3])
        if variant == "on":
            for k in range(3):
                p.px(x + 4 + (k * 2 + i) % 4, top + 5 + k * 7, liquid[4])
        p.rect(x - 1, 27, 13, 2, IRON[2])
        p.rect(x - 1, 58, 13, 3, IRON[1])
    strap_h(p, 3, 59, 42, 3, IRON, False)
    p.hline(5, 61, 38, SHADOW)
    rivets(p, ((5, 60), (42, 60)))
    return finish(p)


def tun() -> Image.Image:
    """A water tank as an iron-hooped oak tun: a studded lid with a ring and bung, three hoops, a brass tap and a sight glass."""
    p = Pix(64, 64, seed=12)
    x, w = 9, 47
    slab(p, x, 3, w, 12, PALE_WOOD)
    corners(p, x, 3, w, 12, 2)
    grain(p, x + 1, 4, w - 2, 10, PALE_WOOD)
    p.hline(x + 2, 4, w - 4, PALE_WOOD[4])
    ring(p, 32, 8, 5, 4, IRON, 1)
    p.rect(18, 7, 5, 3, SHADOW)
    p.rect(19, 8, 3, 1, WOOD[0])
    slab(p, x, 15, w, 3, IRON)
    rivets(p, [(x + 3 + k * 6, 16) for k in range(8)])
    plank_box(p, x, 18, w, 43, OAK, vertical=True)
    corners(p, x, 18, w, 43, 1)
    for y in (22, 38, 55):
        strap_h(p, x, y, w, 3, IRON)
    p.rect(14, 28, 4, 22, SHADOW)                                        # sight glass
    p.rect(15, 29, 2, 20, GLASS[1])
    p.rect(15, 38, 2, 11, WATER[3])
    p.hline(15, 38, 2, WATER[4])
    p.rect(35, 40, 10, 6, BRASS[2])                                      # tap
    p.hline(35, 40, 10, BRASS[4])
    p.rect(36, 46, 4, 6, BRASS[1])
    p.px(37, 52, WATER[4])
    p.px(37, 54, WATER[3])
    ball(p, 38, 32, 6, BRASS)
    p.rect(40, 34, 2, 2, SHADOW)
    return finish(p)


def rain_barrel(w_: bool) -> Image.Image:
    """A moisture farm as a rain barrel: a slatted grate on top, hooped staves, a basin and a spout; `w` is brimming with water."""
    p = Pix(48, 48, seed=13)
    slab(p, 3, 3, 42, 13, IRON)
    corners(p, 3, 3, 42, 13, 2)
    for y in range(5, 15, 3):
        p.hline(5, y, 38, SHADOW)
        p.hline(5, y + 1, 38, IRON[3])
    plank_box(p, 3, 16, 42, 29, OAK, vertical=True)
    corners(p, 3, 16, 42, 29, 1)
    strap_h(p, 3, 17, 42, 3, IRON)
    strap_h(p, 3, 40, 42, 3, IRON)
    p.rect(15, 24, 18, 14, IRON[1])                                      # basin
    p.rect(16, 25, 16, 12, DEEP)
    if w_:
        p.rect(16, 29, 16, 8, WATER[2])
        p.hline(16, 29, 16, WATER[4])
        p.hline(18, 31, 5, WATER[3])
        p.px(25, 34, WATER[4])
        p.px(24, 39, WATER[4])
        p.px(24, 41, WATER[3])
    p.hline(15, 38, 18, IRON[4])
    for x in (7, 33):                                                    # little sight windows
        p.rect(x, 26, 8, 8, SHADOW)
        glass(p, x + 1, 27, 6, 6, GLASS if not w_ else WATER, lit=w_)
        p.px(x + 4, 28, WATER[4] if w_ else GLASS[3])
    return finish(p)


# ---------------------------------------------------------------------------------------------------- hoppers

def hopper(kind: str, frame: int | None) -> Image.Image:
    """A hopper in (a wooden bowl on a banded box) or out (a stone chute with a round mouth); frames light a travelling lamp."""
    p = Pix(32, 32, seed=14 + (kind == "out"))
    if kind == "in":
        slab(p, 3, 16, 26, 14, OAK)
        grain(p, 4, 17, 24, 12, OAK)
        strap_h(p, 3, 16, 26, 2, IRON, False)
        p.ellipse(2, 2, 28, 19, PALE_WOOD[2])
        p.ellipse(3, 2, 26, 17, PALE_WOOD[4])
        p.ellipse(4, 4, 24, 15, PALE_WOOD[1])
        p.ellipse(7, 7, 18, 10, SHADOW)
        p.ellipse(9, 9, 14, 6, DEEP)
        p.hline(7, 3, 12, PALE_WOOD[4])
        p.px(5, 8, PALE_WOOD[4])
        p.line(16, 24, 16, 28, BRASS[3])                                   # a brass down-arrow
        p.line(13, 26, 16, 29, BRASS[3])
        p.line(19, 26, 16, 29, BRASS[3])
    else:
        slab(p, 2, 3, 28, 27, STONE)
        corners(p, 2, 3, 28, 27, 2)
        p.hline(4, 4, 24, STONE[4])
        ring(p, 16, 14, 11, 9, IRON, 2)
        p.ellipse(8, 7, 17, 15, SHADOW)
        p.ellipse(9, 8, 15, 12, DEEP)
        p.hline(11, 8, 8, IRON[0])
        p.line(16, 5, 16, 1, BRASS[3]) if False else None
        rivets(p, ((4, 5), (27, 5), (4, 28), (27, 28)))
    if frame is not None:                                                   # a lamp strip: lamp n burns
        for i in range(8):
            x = 4 + i * 3
            c = FLAME[4] if i == frame - 1 else FLAME[2] if i == (frame - 2) % 8 else IRON[1]
            p.rect(x, 25 if kind == "in" else 25, 2, 2, c)
            if i == frame - 1:
                p.px(x - 1, 24, FLAME[1])
                p.px(x + 2, 24, FLAME[1])
        p.hline(3, 27, 26, SHADOW) if False else None
    return finish(p)


def _hoppers() -> dict[str, Callable[[], Image.Image]]:
    out: dict[str, Callable[[], Image.Image]] = {
        "items~items_tool@hopper_in.png": partial(hopper, "in", None),
        "items~items_tool@hopper_out.png": partial(hopper, "out", None)}
    for n in range(1, 9):
        out[f"items~items_tool3@hopper_in_{n}.png"] = partial(hopper, "in", n)
        out[f"items~items_tool3@hopper_out_{n}.png"] = partial(hopper, "out", n)
    return out


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "items~items_tool2@blender.png": partial(mill, False),
    "items~items_tool2@blender_b.png": partial(mill, True),
    "items~items_tool2@chem_finisher.png": partial(alchemy_cabinet, False),
    "items~items_tool2@chem_finisher_b.png": partial(alchemy_cabinet, True),
    "items~items_tool2@evaporator.png": partial(evaporator, False),
    "items~items_tool2@evaporator_b.png": partial(evaporator, True),
    "items~items_tool2@furnace.png": partial(oven, False),
    "items~items_tool2@furnace_on.png": partial(oven, True),
    "items~items_tool2@gibber.png": grinder,
    "items~items_tool2@heating_plate.png": partial(brazier, False),
    "items~items_tool2@heating_plate_b.png": partial(brazier, True),
    "items~items_tool2@hypertech_bay.png": hyper_bay,
    "items~items_tool2@machine_bay0.png": partial(cabinet, "machine_bay0", 2, 2, 0),
    "items~items_tool2@machine_bay1.png": partial(cabinet, "machine_bay1", 2, 2, 1),
    "items~items_tool2@machine_bay2.png": partial(cabinet, "machine_bay2", 2, 2, 2),
    "items~items_tool2@machine_bay3.png": partial(cabinet, "machine_bay3", 2, 2, 3),
    "items~items_tool2@machine_bay4.png": partial(cabinet, "machine_bay4", 2, 2, 4),
    "items~items_tool2@machine_bay_ext.png": partial(cabinet, "machine_bay_ext", 3, 3, 9),
    "items~items_tool2@printer_off.png": partial(press, False),
    "items~items_tool2@printer_on.png": partial(press, True),
    "items~items_tool2@projector.png": magic_lantern,
    "items~items_tool2@purifier.png": partial(purifier, "normal"),
    "items~items_tool2@purifier_on.png": partial(purifier, "on"),
    "items~items_tool2@purifier_w.png": partial(purifier, "w"),
    "items~items_tool2@water_tank.png": tun,
    "items~items_tool@moisture_farm.png": partial(rain_barrel, False),
    "items~items_tool@moisture_farm_w.png": partial(rain_barrel, True),
    **_hoppers(),
}
