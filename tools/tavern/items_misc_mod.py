"""Fittings for the crossbow (the `items_mod` sprites): the armourer's accessories that the game draws as gun parts.

Magazines become bolt cases, quivers and drilled bolt blocks; the barrel, silencer and compensator become an iron guide
tube, a leather muffle and a bolt clamp; bipod, grip, stocks, sights and the grenade launcher become a wooden tripod, a
leather-wrapped grip, carved stocks, brass peep sights and a short bombard. Every `_item` and its `_view` twin are
drawn by the same function (the view is the same object seen as it hangs on the weapon), so they read as one thing.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image

from itemkit_misc import (conform, CLEAR_GLASS, PURPLE, SILVER, SLATE, STEEL, Shape, bitmap, five, fill, grain, icon, inside,
                          part, rivet)
from palette import (BRASS, FLAME, IRON, LEATHER, LINEN, OAK, PALE_WOOD, PARCHMENT, PLASTER, SHADOW, STONE, WINE, WOOD)
from pix import Color, Pix, Ramp, mix

LEA = five(LEATHER)
Rot = int   # quarter turns anticlockwise


def turned(p: Pix, quarter: int) -> Image.Image:
    """The picture turned by whole quarter turns (a turn keeps whole pixels, so the shading stays crisp)."""
    return p.im.transpose(Image.Transpose.ROTATE_90) if quarter == 1 else p.im.transpose(Image.Transpose.ROTATE_270)


def put(canvas: Pix, art: Image.Image, x: int, y: int) -> Image.Image:
    canvas.paste(art, x, y)
    return canvas.im


def tube(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, horizontal: bool = True) -> Shape:
    s = Shape(p.w, p.h).rect(x, y, w, h)
    fill(p, s, ramp)
    return s


def band(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = BRASS) -> None:
    """A metal hoop round a tube: lit on its left/top, dark on its right/bottom."""
    s = Shape(p.w, p.h).rect(x, y, w, h)
    fill(p, s, ramp, outline=SHADOW)


# ---------------------------------------------------------------------------------------------- bolt cases

def leather_case(w: int, h: int, straps: int = 1, seed: int = 1) -> Pix:
    """An upright leather bolt case w x h: stitched body, brass-rimmed mouth with three fletched bolts, straps and a buckle."""
    p = Pix(w, h, seed=seed)
    rim = 7 if h >= 20 else 6
    # the bolts stand in the open mouth: dark shafts with red and cream flights, a thin brass ring round the rim
    part(p, LEA, lambda s: s.rrect(0, rim, w, h - rim))
    p.hline(1, rim, w - 2, SHADOW)
    p.hline(0, rim + 1, w, BRASS[3])
    p.hline(0, rim + 2, w, BRASS[1])
    for i, x in enumerate(range(1, w - 3, 4)):
        c = (WINE[3], PARCHMENT[3], WINE[3])[i % 3]
        p.vline(x + 1, 2, rim - 2, WOOD[3])
        p.px(x, 0, c)
        p.px(x + 2, 0, c)
        p.px(x, 1, c)
        p.px(x + 2, 1, c)
        p.px(x + 1, 0, SHADOW)
    for k in range(straps):
        y = rim + 5 + k * max(6, (h - rim - 8) // max(1, straps))
        if y + 3 > h - 2:
            break
        p.hline(0, y, w, LEA[3])
        p.hline(0, y + 1, w, LEA[1])
        p.hline(0, y + 2, w, SHADOW)
        if k == 0:
            p.rect(w - 5, y - 1, 3, 5, BRASS[3])
            p.px(w - 5, y - 1, BRASS[4])
            p.px(w - 4, y + 1, BRASS[0])
    for yy in range(rim + 2, h - 2, 3):
        p.px(1, yy, LEA[4])
    p.vline(w - 2, rim + 2, h - rim - 4, LEA[1])
    return p


def case(w: int, h: int, straps: int, x: int, y: int, size: tuple[int, int], quarter: int = 0, seed: int = 1) -> Image.Image:
    """A bolt case placed on a canvas, upright or turned on its side."""
    canvas = Pix(*size, seed=seed)
    art = leather_case(w, h, straps, seed)
    return put(canvas, art.im if quarter == 0 else turned(art, quarter), x, y)


def drilled_block(w: int, h: int, holes: int, seed: int = 1) -> Pix:
    """A bolt block: a pale wooden slab drilled with holes that hold the bolt heads, an iron band at the foot."""
    p = Pix(w, h, seed=seed)
    part(p, PALE_WOOD, lambda s: s.rrect(0, 0, w, h))
    part(p, IRON, lambda s: s.rect(0, 0, w, 3), soft=1.0)
    p.hline(1, 1, w - 2, IRON[4])
    rivet(p, 2, 2, BRASS)
    rivet(p, w - 3, 2, BRASS)
    gap = (h - 8) / max(1, holes)
    for i in range(holes):
        cy = int(5 + gap * i + gap / 2) - 1
        hx = w // 2 - 1
        p.rect(hx, cy, 3, 3, SHADOW)
        p.px(hx + 1, cy + 1, IRON[3])
        p.px(hx, cy + 2, PALE_WOOD[4])
    part(p, IRON, lambda s: s.rect(0, h - 3, w, 3), soft=1.0)
    grain(p, Shape(w, h).rect(0, 4, w, h - 8), 0, 4, w, h - 8, PALE_WOOD[1], horizontal=False, count=3)
    return p


def block(w: int, h: int, holes: int, x: int, y: int, size: tuple[int, int], quarter: int = 0, seed: int = 1) -> Image.Image:
    canvas = Pix(*size, seed=seed)
    art = drilled_block(w, h, holes, seed)
    return put(canvas, art.im if quarter == 0 else turned(art, quarter), x, y)


def slotted(w: int, h: int, seed: int = 1) -> Pix:
    """A wooden bolt rack: dark oak with three open slots in which the bolt shafts stand, an iron cap on top."""
    p = Pix(w, h, seed=seed)
    part(p, WOOD, lambda s: s.rect(0, 0, w, h))
    part(p, IRON, lambda s: s.rect(0, 0, w, 4), soft=1.0)
    for i in range(3):
        x = 2 + i * ((w - 4) // 3)
        p.rect(x, 1, 2, 2, BRASS[3])
        p.rect(x, 5, 3, h - 8, SHADOW)
        p.vline(x + 1, 6, h - 10, WOOD[2])
    part(p, IRON, lambda s: s.rect(0, h - 3, w, 3), soft=1.0)
    p.vline(0, 4, h - 7, WOOD[4])
    return p


def bolt_box(w: int, h: int, seed: int = 1, side: bool = False) -> Pix:
    """A planked bolt box: oak slats, an iron strap at each end and a rope grip; `side` shows its narrow face."""
    p = Pix(w, h, seed=seed)
    part(p, WOOD, lambda s: s.rrect(0, 0, w, h))
    for y in range(4, h - 2, 4):
        p.hline(1, y, w - 2, WOOD[0])
        p.hline(1, y + 1, w - 2, WOOD[4])
    for y in (0, h - 4):
        part(p, IRON, lambda s, y=y: s.rect(0, y, w, 4), soft=1.0)
        rivet(p, 2, y + 1)
        rivet(p, w - 3, y + 1)
    if not side:
        part(p, LEA, lambda s: s.rrect(w // 2 - 4, h // 2 - 3, 8, 6), soft=1.0)
        p.rect(w // 2 - 2, h // 2 - 1, 4, 2, SHADOW)
    return p


def curved_quiver(w: int, h: int, seed: int = 1, tilt: int = 5) -> Pix:
    """A banana-curved leather quiver (the high-capacity case): a slanted body, a brass mouth, fletching above."""
    p = Pix(w, h, seed=seed)
    top = 7
    body = [(1, top), (w - 6, top), (w - 2, h - 8), (w - 6, h - 1), (tilt + 1, h - 1), (tilt - 1, h - 8), (0, h // 2)]
    part(p, LEA, lambda s: s.poly(body))
    mouth = Shape(w, h).rect(0, top - 1, w - 5, 3)
    fill(p, mouth, BRASS)
    for i, x in enumerate((2, 6, 10)):
        if x + 2 > w - 6:
            break
        c = (WINE[3], PARCHMENT[3], WINE[3])[i]
        p.rect(x, 0, 2, top - 1, WOOD[2])
        p.px(x, 0, c)
        p.px(x + 1, 2, c)
        p.px(x, 4, c)
    for k in range(3):
        y = top + 5 + k * 6
        x0 = max(1, int(1 + (y - top) * 0.06))
        p.hline(x0 + 1, y, w - 8, LEA[3])
        p.hline(x0 + 1, y + 1, w - 8, LEA[1])
    for y in range(top + 2, h - 3, 3):
        p.px(3 + (y - top) // 6, y, LEA[4])
    return p


# ---------------------------------------------------------------------------------------------- metal and leather tubes

def guide_tube(w: int, h: int, seed: int = 1) -> Pix:
    """The barrel: a bolt-guide tube of dark iron with brass hoops and a flared mouth ring."""
    p = Pix(w, h, seed=seed)
    tube(p, 0, 1, w, h - 2, IRON)
    for x in (5, w // 2 - 1, w - 12):
        band(p, x, 0, 2, h)
    p.hline(w // 2 + 3, h // 2, w // 4, IRON[1])
    band(p, w - 4, 0, 4, h, BRASS)
    p.px(w - 3, 1, BRASS[4])
    return p


def muffle(w: int, h: int, seed: int = 1, long: bool = False) -> Pix:
    """The silencer: a thick leather muffle laced round the bolt channel, with iron end rings (and a clip lug if long)."""
    p = Pix(w, h, seed=seed)
    tube(p, 2, 0, w - 4, h, LEA)
    for x in range(5, w - 5, 3):
        p.px(x, h // 2, LEA[1])
        p.px(x + 1, h // 2 - 1, LEA[4])
    band(p, 0, 0, 3, h, IRON)
    band(p, w - 3, 0, 3, h, IRON)
    if long:
        band(p, 6, h - 1, 5, 3, IRON)
        p.px(7, h, IRON[4])
        rivet(p, 7, 2)
    return p


def clamp_block(w: int, h: int, seed: int = 1) -> Pix:
    """The compensator: a notched iron clamp, three vents cut in its face, a brass pin."""
    p = Pix(w, h, seed=seed)
    part(p, IRON, lambda s: s.poly([(0, 1), (w - 3, 0), (w - 1, 2), (w - 1, h - 1), (2, h - 1), (0, h - 3)]))
    for i in range(3):
        p.rect(3 + i * 4, 3, 2, 5, SHADOW)
        p.vline(4 + i * 4, 3, 5, IRON[2])
    p.hline(2, h - 3, w - 5, IRON[4])
    rivet(p, w - 4, h - 4)
    rivet(p, 2, 2)
    return p


def flask(w: int, h: int, seed: int = 1) -> Pix:
    """The bottle: a ribbed glass flask lying on its side, corked, a pale drink inside (like the water bottle it replaces)."""
    p = Pix(w, h, seed=seed)
    bw = w - 8
    part(p, CLEAR_GLASS, lambda s: s.ellipse(7, 0, bw + 1, h).rect(4, h // 2 - 3, 8, 6))
    cork = Shape(w, h).rect(0, h // 2 - 3, 5, 6)
    fill(p, cork, WOOD)
    p.px(0, h // 2 - 2, WOOD[4])
    band(p, 4, h // 2 - 4, 2, 8, BRASS)
    for x in range(14, w - 5, 5):
        p.vline(x, 3, h - 6, CLEAR_GLASS[1])
    p.hline(9, 2, w - 18, CLEAR_GLASS[4])
    p.hline(9, 3, w - 20, CLEAR_GLASS[4])
    p.dither(12, h - 5, w - 14, 3, CLEAR_GLASS[1], 0.5)
    return p


# ---------------------------------------------------------------------------------------------- stocks, grips, tripod

def stock(seed: int = 1) -> Pix:
    """A carved crossbow butt 41x31: an oak wedge with a thumb hole, a brass butt plate and an iron strap along the top."""
    p = Pix(41, 31, seed=seed)
    pts = [(1, 4), (4, 0), (26, 0), (40, 5), (40, 14), (26, 16), (20, 22), (15, 30), (4, 30), (0, 25)]
    s = part(p, WOOD, lambda s: s.poly(pts), soft=1.0, bias=1)
    hole = Shape(41, 31).poly([(7, 8), (20, 8), (24, 13), (15, 22), (7, 22)])
    fill(p, hole, WOOD, outline=SHADOW, soft=-1.0, bias=-2)
    for x in range(8, 24):
        p.px(x, 9, WOOD[0])
    part(p, BRASS, lambda s: s.rect(0, 3, 4, 24), soft=1.0)
    p.vline(1, 5, 20, BRASS[4])
    for y in (6, 13, 20, 24):
        p.px(2, y, BRASS[0])
    part(p, IRON, lambda s: s.poly([(5, 1), (26, 1), (39, 6), (39, 8), (25, 3), (5, 3)]), soft=1.0)
    grain(p, s, 5, 10, 34, 18, WOOD[1], count=6)
    for x in (30, 35):
        rivet(p, x, 11)
    return p


def short_stock(seed: int = 1) -> Pix:
    """The short stock: an iron mounting block over a leather-wrapped haft with a red cord and a turned knob."""
    p = Pix(15, 32, seed=seed)
    part(p, IRON, lambda s: s.rrect(0, 0, 15, 11))
    p.hline(2, 2, 11, IRON[4])
    p.rect(9, 3, 4, 5, SHADOW)
    p.px(10, 4, BRASS[3])
    part(p, LEA, lambda s: s.rect(4, 10, 7, 17), soft=1.0)
    for y in range(12, 26, 3):
        p.hline(4, y, 7, LEA[1])
        p.hline(4, y + 1, 7, LEA[4])
    p.vline(7, 11, 15, WINE[3])
    part(p, WOOD, lambda s: s.ellipse(3, 25, 9, 7), soft=1.0)
    p.px(5, 26, WOOD[4])
    return p


def grip(seed: int = 1) -> Pix:
    """A pistol-style grip 16x28: a carved haft wrapped in leather, finger grooves, a brass cap."""
    p = Pix(16, 28, seed=seed)
    part(p, WOOD, lambda s: s.poly([(2, 0), (14, 0), (14, 8), (12, 20), (13, 25), (11, 27), (3, 27), (1, 22), (4, 14), (2, 6)]), soft=1.0)
    part(p, BRASS, lambda s: s.rect(1, 0, 14, 3), soft=1.0)
    for y in (6, 10, 14, 18):
        p.hline(3 + (0 if y < 12 else 0), y, 9, LEA[1])
        p.hline(3, y + 1, 9, LEA[3])
    part(p, BRASS, lambda s: s.rrect(3, 24, 9, 4), soft=1.0)
    p.px(2, 5, WOOD[4])
    return p


def tripod_closed(seed: int = 1) -> Pix:
    """The bipod folded: two wooden legs side by side with an iron collar and a foot cap at each end."""
    p = Pix(40, 14, seed=seed)
    tube(p, 3, 1, 34, 5, WOOD)
    tube(p, 3, 7, 34, 5, WOOD)
    band(p, 0, 0, 5, 13, IRON)
    band(p, 33, 0, 7, 13, IRON)
    band(p, 14, 0, 3, 13, IRON)
    p.px(36, 2, IRON[4])
    rivet(p, 2, 2)
    return p


def tripod_open(seed: int = 1) -> Pix:
    """The bipod set up (37x36): an iron mounting wedge, a pivot cap and two splayed legs with iron feet."""
    p = Pix(48, 48, seed=seed)
    for x0, x1 in ((22, 14), (24, 33)):
        s = Shape(48, 48).line(x0, 11, x1, 31, 3)
        fill(p, s, WOOD)
    part(p, IRON, lambda s: s.poly([(7, 8), (24, 0), (43, 4), (43, 8), (34, 9), (7, 10)]), soft=1.0)
    p.hline(10, 7, 24, IRON[4])
    for x in (30, 36, 40):
        p.px(x, 4, SHADOW)
    part(p, IRON, lambda s: s.ellipse(19, 8, 10, 7), soft=1.0)
    p.px(22, 10, IRON[4])
    for fx, fy in ((13, 31), (32, 31)):
        s = Shape(48, 48).ellipse(fx - 3, fy, 7, 5)
        fill(p, s, IRON)
    band(p, 17, 20, 3, 3, BRASS)
    band(p, 28, 20, 3, 3, BRASS)
    return p


# ---------------------------------------------------------------------------------------------- sights

def peep_sight(red: bool, seed: int = 1, tall: bool = True) -> Pix:
    """A brass peep sight 12x15: a slanted hood round a lens with a red dot of paint, a clamp foot below."""
    p = Pix(12, 15, seed=seed)
    part(p, BRASS, lambda s: s.poly([(2, 0), (10, 2), (11, 12), (8, 14), (1, 14), (0, 3)]))
    lens = Shape(12, 15).rrect(3, 3, 6, 7)
    fill(p, lens, CLEAR_GLASS, outline=BRASS[0])
    p.rect(5, 5, 2, 2, WINE[3] if red else SKY_BLUE[3])
    p.px(5, 5, FLAME[3] if red else SKY_BLUE[4])
    p.hline(1, 12, 9, BRASS[0])
    rivet(p, 2, 13, BRASS)
    return p


SKY_BLUE: Final[Ramp] = (mix((20, 30, 60), (0, 0, 0), 0.0), (40, 80, 150), (70, 130, 200), (120, 180, 230), (190, 225, 245))


def ring_sight(seed: int = 1) -> Pix:
    """A makeshift ring sight (12x15): a bent iron ring with a drop of red wax in the middle, on a stub of wire."""
    p = Pix(16, 16, seed=seed)
    ring = Shape(16, 16).ellipse(2, 1, 12, 13)
    ring.ellipse(5, 4, 6, 7, on=False)
    fill(p, ring, IRON)
    s = Shape(16, 16).ellipse(7, 6, 3, 3)
    fill(p, s, WINE, outline=None)
    p.px(7, 6, FLAME[3])
    part(p, IRON, lambda s: s.rect(4, 13, 8, 3), soft=1.0)
    p.hline(5, 14, 6, IRON[4])
    return p


def sight_tube(lens: Ramp, long: bool = False, seed: int = 1) -> Pix:
    """The laser sight as a brass sighting tube 26x9: a clamp at the rear, a lens set in the muzzle, a jewel of colour."""
    p = Pix(26, 10, seed=seed)
    tube(p, 3, 1, 21, 6, BRASS)
    band(p, 0, 0, 5, 10, IRON)
    band(p, 20, 0, 5, 7, IRON)
    p.rect(22, 3, 2, 2, lens[3])
    p.px(22, 3, lens[4])
    p.hline(9, 2, 8, BRASS[4])
    p.hline(7, 6, 12, lens[1])
    for x in range(8, 18, 3):
        p.px(x, 4, BRASS[1])
    return p


def jewel_housing(lens: Ramp, seed: int = 1) -> Pix:
    """The sight as an item (10x10): a small brass housing with a jewel lens and a bracket tooth."""
    p = Pix(16, 16, seed=seed)
    part(p, BRASS, lambda s: s.poly([(3, 3), (12, 3), (12, 12), (7, 12), (3, 9)]))
    p.rect(8, 5, 3, 3, SHADOW)
    p.rect(8, 5, 2, 2, lens[3])
    p.px(8, 5, lens[4])
    p.hline(4, 4, 4, BRASS[4])
    return p


def toy_tube(item: bool, seed: int = 1) -> Pix:
    """The toy sight: a painted pale-wood tube with brass studs; the view adds two sight posts and a spot of red enamel."""
    p = Pix(32 if item else 47, 16, seed=seed)
    x, y = (3, 5) if item else (0, 3)
    tube(p, x, y + (0 if item else 3), 26 if item else 40, 7, PALE_WOOD)
    for i in range(4):
        rivet(p, x + 4 + i * 4, y + 3 + (0 if item else 3), BRASS)
    band(p, x + 22 if item else 36, y + (0 if item else 3), 4, 7, IRON)
    p.rect(x + 25 if item else 38, y + 2 + (0 if item else 3), 2, 2, WINE[3])
    if not item:
        for xx in (10, 17):
            part(p, IRON, lambda s, xx=xx: s.rect(xx, 0, 3, 8), soft=1.0)
        p.rect(37, 5, 3, 2, FLAME[2])
    return p


# ---------------------------------------------------------------------------------------------- bombard and tablets

def bombard(view: bool, seed: int = 1) -> Pix:
    """The grenade launcher as a bombard: a short stock with a lock, a bell-mouthed iron barrel hooped in brass."""
    w, h = (64, 28) if view else (64, 16)
    p = Pix(w, h, seed=seed)
    oy = 6 if view else 0
    part(p, WOOD, lambda s: s.poly([(1, 3 + oy), (8, 1 + oy), (24, 1 + oy), (24, 14 + oy), (6, 14 + oy), (1, 11 + oy), (3, 7 + oy)]), soft=1.0)
    p.rect(8, 6 + oy, 4, 3, SHADOW)
    p.px(9, 6 + oy, FLAME[2])
    tube(p, 22, 2 + oy, 38, 11, IRON)
    for x in (28, 38, 48):
        band(p, x, 1 + oy, 3, 13, BRASS)
    band(p, 57, 0 + oy, 4, 15, IRON)
    p.rect(54, 5 + oy, 3, 4, SHADOW)
    p.hline(30, 4 + oy, 8, IRON[4])
    p.rect(14, 1 + oy, 9, 3, LEA[2])
    p.hline(14, 1 + oy, 9, LEA[4])
    if view:
        part(p, IRON, lambda s: s.rect(30, 3, 22, 5), soft=1.0)
        part(p, IRON, lambda s: s.poly([(26, 6), (30, 1), (34, 1), (34, 6)]))
        p.hline(32, 4, 18, IRON[4])
    return p


def tablet(light: bool, seed: int = 1) -> Pix:
    """A recipe tablet with a crossbow cut into it: slate for the large one, pale limestone for the small."""
    if light:
        p = Pix(16, 16, seed=seed)
        part(p, PLASTER, lambda s: s.rrect(2, 2, 12, 12), soft=1.0)
        c = (PLASTER[1], PLASTER[0])
        bitmap(p, ["1.....1", ".1...1.", "..111..", "...1...", "...1..."][:5], 4, 4, {"1": PLASTER[0]})
        p.hline(4, 12, 8, PLASTER[1])
        p.px(3, 3, PLASTER[4])
        return p
    p = Pix(32, 16, seed=seed)
    part(p, STONE, lambda s: s.rect(3, 1, 26, 14), soft=1.0)
    p.frame(5, 3, 22, 10, STONE[1])
    bitmap(p, ["1...........1", "11.........11", ".111111111111", ".....111.....", ".....111....."], 9, 5, {"1": STONE[0]})
    p.hline(6, 12, 20, STONE[3])
    for x, y in ((4, 2), (27, 2), (4, 13), (27, 13)):
        rivet(p, x, y, IRON)
    return p


# ---------------------------------------------------------------------------------------------- the catalog

def _assets() -> dict[str, Callable[[], Image.Image]]:
    a: dict[str, Callable[[], Image.Image]] = {}

    def add(name: str, fn: Callable[[], Image.Image]) -> None:
        a[f"items~items_mod@{name}.png"] = fn

    def on(size: tuple[int, int], x: int, y: int, art: Callable[..., Pix], *args: object, quarter: int = 0) -> Callable[[], Image.Image]:
        def draw() -> Image.Image:
            canvas = Pix(*size)
            made = art(*args)
            canvas.paste(made.im if quarter == 0 else turned(made, quarter), x, y)
            return canvas.im
        return draw

    # bolt cases (the 10 mm magazines) and drilled blocks (the .22 magazines)
    add("10mm_mag_item", on((16, 32), 0, 3, leather_case, 15, 25, 1, 1))
    add("10mm_mag_high_item", on((16, 32), 0, 1, leather_case, 15, 30, 2, 2))
    add("10mm_mag_ext_item", on((16, 48), 0, 3, leather_case, 16, 42, 3, 3))
    add("10mm_mag_view", on((16, 16), 0, 2, leather_case, 13, 16, 1, 4, quarter=1))
    add("10mm_mag_high_view", on((16, 14), 1, 6, leather_case, 8, 15, 1, 5, quarter=1))
    add("10mm_mag_ext_view", on((16, 26), 0, 9, leather_case, 16, 17, 1, 6))
    add("10mm_mag_ext_view2", on((16, 16), 0, 0, leather_case, 16, 16, 1, 7))
    add("10mm_mag_smg_item", on((16, 32), 0, 5, slotted, 16, 23, 8))
    add("10mm_mag_smg_view", on((17, 32), 0, 0, slotted, 17, 21, 9))
    add("10mm_mag_smg_box_item", on((32, 32), 5, 2, bolt_box, 22, 29, 10))
    add("10mm_mag_smg_box_view", on((16, 32), 0, 0, bolt_box, 16, 29, 11, True))
    add("10mm_mag_smg_high_item", on((32, 32), 7, 1, curved_quiver, 21, 30, 12, 5))
    add("10mm_mag_smg_high_view", on((32, 32), 0, 0, curved_quiver, 21, 30, 13, 4))
    add("22_mag_item", on((16, 32), 2, 4, drilled_block, 12, 25, 3, 14))
    add("22_mag_high_item", on((16, 32), 2, 1, drilled_block, 12, 30, 4, 15))
    add("22_mag_ext_item", on((16, 48), 2, 3, drilled_block, 12, 42, 6, 16))
    add("22_mag_view", on((16, 16), 3, 0, drilled_block, 8, 13, 3, 17, quarter=1))
    add("22_mag_ext_view", on((16, 16), 0, 0, drilled_block, 14, 16, 3, 18))
    # tubes
    add("barrel_item", on((32, 16), 1, 5, guide_tube, 29, 7, 20))
    add("barrel_view", on((32, 16), 0, 4, guide_tube, 29, 7, 21))
    add("silencer_item", on((32, 16), 2, 3, muffle, 28, 9, 22))
    add("silencer_view", on((32, 16), 0, 3, muffle, 28, 9, 23))
    add("silencer2_item", on((48, 16), 2, 2, muffle, 45, 13, 24, True))
    add("silencer2_view", on((48, 16), 0, 0, muffle, 45, 13, 25, True))
    add("compensator_item", on((16, 16), 0, 2, clamp_block, 16, 12, 26))
    add("compensator_view", on((16, 16), 0, 0, clamp_block, 16, 12, 27))
    add("bottle_item", on((48, 16), 2, 1, flask, 45, 14, 28))
    add("bottle_view", on((48, 16), 0, 1, flask, 45, 14, 29))
    # stocks, grips, tripod
    add("stock_item", on((48, 32), 4, 1, stock, 30))
    add("stock_view", on((48, 32), 7, 0, stock, 31))
    add("short_stock_item", on((16, 32), 1, 0, short_stock, 32))
    add("short_stock_view", on((32, 32), 14, 0, short_stock, 33))
    add("grip_item", on((16, 32), 0, 2, grip, 34))
    add("grip_view", on((48, 32), 7, 0, grip_mounted, 35))
    add("bipod_item", on((48, 16), 4, 1, tripod_closed, 36))
    add("bipod_view", on((48, 48), 0, 0, tripod_open, 37))
    # sights
    add("laser_item", on((16, 16), 0, 0, jewel_housing, WINE, 38))
    add("laser2_item", on((16, 16), 0, 0, jewel_housing, SKY_BLUE, 39))
    add("laser_view", on((32, 16), 0, 0, sight_tube, WINE, False, 40))
    add("laser2_view", on((32, 15), 0, 0, sight_tube, SKY_BLUE, False, 41))
    add("laser_toy_item", on((32, 16), 0, 0, toy_tube, True, 42))
    add("laser_toy_view", on((47, 16), 0, 0, toy_tube, False, 43))
    add("rds_item", on((16, 16), 2, 1, peep_sight, True, 44))
    add("rds_view2", on((16, 16), 0, 0, peep_sight, True, 45))
    add("rds_view", on((16, 16), 1, 0, sight_cap, 46))
    add("rds_makeshift_item", on((16, 16), 0, 0, ring_sight, 47))
    add("rds_makeshift_view", on((16, 31), 0, 0, ring_sight_hung, 48))
    # launcher and tablets
    add("gl_item", on((64, 16), 0, 0, bombard, False, 49))
    add("gl_view", on((64, 28), 0, 0, bombard, True, 50))
    add("special_mod", on((32, 16), 0, 0, tablet, False, 51))
    add("special_mod1", on((16, 16), 0, 0, tablet, True, 52))
    return a


def grip_mounted(seed: int = 1) -> Pix:
    """The grip as it hangs from the weapon: an iron bracket plate across the top, the same haft below."""
    p = Pix(36, 32, seed=seed)
    part(p, IRON, lambda s: s.poly([(0, 6), (20, 0), (34, 0), (35, 4), (35, 8), (0, 8)]), soft=1.0)
    p.hline(2, 5, 30, IRON[4])
    for x in (24, 29):
        p.rect(x, 2, 2, 3, SHADOW)
    art = grip(seed)
    p.paste(art, 6, 4)
    part(p, IRON, lambda s: s.rect(4, 3, 14, 5), soft=1.0)
    rivet(p, 6, 5)
    rivet(p, 15, 5)
    return p


def sight_cap(seed: int = 1) -> Pix:
    """The top of the peep sight seen over the weapon: just the curve of the brass hood and the lens rim."""
    p = Pix(10, 5, seed=seed)
    part(p, BRASS, lambda s: s.poly([(0, 4), (2, 1), (6, 0), (8, 2), (9, 4)]))
    p.hline(3, 2, 3, BRASS[4])
    return p


def ring_sight_hung(seed: int = 1) -> Pix:
    """The ring sight on the weapon: the ring up top and the wire hook that holds it, hanging below."""
    p = Pix(10, 19, seed=seed)
    ring = Shape(10, 19).ellipse(0, 0, 9, 10)
    ring.ellipse(2, 2, 5, 6, on=False)
    fill(p, ring, IRON)
    p.rect(4, 4, 2, 2, WINE[3])
    p.px(4, 4, FLAME[3])
    p.vline(4, 10, 6, IRON[3])
    p.vline(5, 10, 6, IRON[1])
    p.hline(3, 16, 3, IRON[3])
    p.px(2, 17, IRON[3])
    p.px(3, 18, IRON[2])
    return p


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = conform(_assets())
