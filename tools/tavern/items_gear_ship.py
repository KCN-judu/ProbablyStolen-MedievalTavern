"""Ship parts become the tavern's cellar and yard: cargo coffers (open and closed), slatted smuggler crates, the larder
chest, a copper still for the reactor, a glowing oil tube for the fuel cell, and heaps of broken yard junk.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_gear import (AMBER, BONE, OCHRE, PLUM, STEEL, ell_m, finish, line_m, outline_only, poly_m, puff, rect_m,
                          rrect_m, stud)
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, SHADOW, STONE, WINE, WOOD
from pix import Pix, Ramp, rgb

Draw = Callable[[], Image.Image]
COPPER: Ramp = (rgb("#3a1c12"), rgb("#6e3318"), rgb("#a8561f"), rgb("#d98438"), rgb("#f2b565"))
GREYOAK: Ramp = (rgb("#2a2a2c"), rgb("#4a4846"), rgb("#6e6a64"), rgb("#928c80"))


def _f(n: str) -> str:
    return f"items~items_ship@{n}.png"


def coffer(x0: int, x1: int, ramp: Ramp, kind: str, seed: int) -> Image.Image:
    """A cargo coffer on two feet. kind: open (dark hollow), chem (plum door with a flask), gun (iron door with a bow)."""
    p = Pix(48, 48, seed=seed)
    w = x1 - x0
    puff(p, rect_m(x0 + 3, 44, 5, 4), OAK, r=1)
    puff(p, rect_m(x1 - 8, 44, 5, 4), OAK, r=1)
    puff(p, rrect_m(x0, 3, w, 42, 3), ramp, r=4, flat=0.55)
    puff(p, rrect_m(x0, 1, w, 7, 2), ramp, r=3, bias=0.15)                         # the lid
    puff(p, rrect_m(x0 + w // 2 - 7, 0, 14, 4, 1), IRON, r=2)                      # carrying bar
    p = finish(p) and p
    p.hline(x0 + 2, 2, w - 4, ramp[-1])
    p.hline(x0 + 1, 8, w - 2, ramp[0])
    for x in (x0 + 2, x1 - 3):
        stud(p, x, 5)
        stud(p, x, 40)
    hx0, hx1 = x0 + 5, x1 - 5
    if kind == "open":
        p.rect(hx0, 13, hx1 - hx0, 24, OAK[0])
        p.rect(hx0 + 1, 14, hx1 - hx0 - 2, 3, OAK[1])
        p.dither(hx0 + 1, 17, hx1 - hx0 - 2, 8, OAK[1], 0.3)
        p.rect(hx0, 32, hx1 - hx0, 5, ramp[1])
        p.hline(hx0, 32, hx1 - hx0, ramp[3])
        p.hline(hx0, 36, hx1 - hx0, ramp[0])
        p.vline(hx0 + 4, 20, 4, OAK[3]) if False else None
    else:
        door = PLUM if kind == "chem" else IRON
        puff(p, rect_m(hx0, 13, hx1 - hx0, 24), door, r=3, flat=0.5)
        for y in (18, 24, 30):
            p.hline(hx0 + 1, y, hx1 - hx0 - 2, door[0])
            p.hline(hx0 + 1, y + 1, hx1 - hx0 - 2, door[3])
        p.frame(hx0, 13, hx1 - hx0, 24, SHADOW)
        mx = (hx0 + hx1) // 2
        p.rect(mx - 2, 27, 5, 4, BRASS[2])
        p.hline(mx - 2, 27, 5, BRASS[4])
        p.px(mx, 29, SHADOW)
        if kind == "chem":                                    # a painted flask
            p.rect(mx - 1, 15, 3, 2, PARCHMENT_C)
            p.rect(mx - 3, 17, 7, 1, PARCHMENT_C)
        else:                                                 # a painted crossed bolt and bow
            p.line(mx - 4, 15, mx + 4, 17, PARCHMENT_C)
            p.line(mx - 4, 17, mx + 4, 15, PARCHMENT_C)
    return p.im


PARCHMENT_C = rgb("#c4ad78")


def slat_crate(x0: int, y0: int, x1: int, y1: int, size: int, seed: int) -> Image.Image:
    """A smuggler's crate: dark boards in horizontal slats, iron straps at both ends, a lid and a hasp."""
    p = Pix(size, size, seed=seed)
    w, h = x1 - x0, y1 - y0
    puff(p, rrect_m(x0, y0, w, h, 2), OAK, r=3, flat=0.6, bias=0.1)
    p = finish(p) and p
    for y in range(y0 + 4, y1 - 2, 3):
        p.hline(x0 + 5, y, w - 10, SHADOW)
        p.hline(x0 + 5, y + 1, w - 10, OAK[3])
    p.hline(x0 + 1, y0 + 2, w - 2, OAK[4])
    for x in (x0 + 1, x1 - 4):
        p.rect(x, y0 + 1, 3, h - 2, IRON[2])
        p.vline(x, y0 + 1, h - 2, IRON[4])
        p.vline(x + 2, y0 + 1, h - 2, IRON[0])
    for y in range(y0 + 4, y1 - 3, max(6, h // 4)):
        stud(p, x0 + 1, y)
        stud(p, x1 - 4, y)
    cx = (x0 + x1) // 2
    p.rect(cx - 2, y0 + 1, 4, 5, BRASS[2])
    p.hline(cx - 2, y0 + 1, 4, BRASS[4])
    p.px(cx, y0 + 3, SHADOW)
    return p.im


def larder() -> Image.Image:
    """The fridge becomes a cold larder chest: oak cabinet, iron hinges, brass latch, cooling slits (48x48)."""
    p = Pix(48, 48, seed=3)
    puff(p, rect_m(8, 43, 4, 1), OAK, r=1)
    puff(p, rrect_m(6, 5, 37, 38, 3), PALE_WOOD, r=4, flat=0.6)
    p = finish(p) and p
    p.hline(7, 6, 35, PALE_WOOD[4])
    p.frame(10, 9, 29, 30, PALE_WOOD[1])
    p.frame(11, 10, 27, 28, PALE_WOOD[3])
    for y in range(12, 20, 2):
        p.hline(16, y, 17, PALE_WOOD[0])
    for y in (11, 31):
        p.rect(6, y, 9, 3, IRON[2])
        p.hline(6, y, 9, IRON[4])
        p.hline(6, y + 2, 9, IRON[0])
        stud(p, 13, y)
    p.rect(33, 20, 4, 8, IRON[2])
    p.vline(33, 20, 8, IRON[4])
    p.rect(34, 23, 2, 3, BRASS[3])
    p.rect(9, 34, 31, 6, PALE_WOOD[2])
    p.hline(9, 34, 31, PALE_WOOD[4])
    for x in range(14, 36, 4):
        p.vline(x, 36, 3, PALE_WOOD[0])
    p.rect(8, 42, 5, 3, OAK[1])
    p.rect(35, 42, 5, 3, OAK[1])
    return p.im


def still() -> Image.Image:
    """A copper still on a stone hearth with a swan-neck pipe to a hooped condenser tub (80x48)."""
    p = Pix(80, 48, seed=4)
    puff(p, rect_m(4, 31, 38, 16), STONE, r=3, flat=0.5)
    puff(p, ell_m(6, 8, 36, 28), COPPER, r=7)
    puff(p, rect_m(18, 3, 10, 8), COPPER, r=2)
    puff(p, ell_m(15, 0, 16, 9), COPPER, r=4)
    puff(p, line_m([(31, 5), (46, 3), (56, 8), (60, 20)], 3), COPPER, r=2)
    puff(p, rrect_m(52, 16, 24, 26, 3), WOOD, r=4, flat=0.5)
    puff(p, rect_m(60, 43, 8, 4), GLASS, r=1)
    p = finish(p) and p
    for y in (16, 30):                                       # iron bands and rivets on the boiler
        p.hline(8, y, 32, IRON[2])
        p.hline(8, y + 1, 32, IRON[0])
        for x in range(10, 40, 6):
            stud(p, x, y - 1) if False else p.px(x, y, BRASS[4])
    for y in (21, 36):
        p.rect(52, y, 24, 2, IRON[2])
        p.hline(52, y, 24, IRON[4])
    p.rect(14, 37, 12, 9, SHADOW)                            # the fire mouth
    p.rect(15, 41, 10, 5, FLAME[1])
    p.rect(17, 43, 6, 3, FLAME[3])
    p.rect(19, 45, 2, 1, FLAME[4])
    p.rect(64, 44, 4, 3, AMBER[3])
    p.vline(63, 8, 3, COPPER[4])
    p.px(21, 2, COPPER[4])
    p.px(12, 14, COPPER[4])
    p.px(11, 17, COPPER[4])
    p.rect(30, 14, 4, 4, BRASS[3])                           # a pressure gauge
    p.px(31, 15, SHADOW)
    p.line(7, 40, 40, 40, STONE[1])
    for x in (10, 22, 34):
        p.vline(x, 33, 7, STONE[1])
    return p.im


def oil_tube() -> Image.Image:
    """The plasma cell becomes a glass tube of burning lamp oil capped in brass (64x32)."""
    p = Pix(64, 32, seed=5)
    puff(p, rect_m(8, 8, 48, 16), GLASS, r=4, flat=0.2)
    puff(p, rect_m(11, 10, 42, 12), AMBER, r=4)
    for cx in (3, 54):
        puff(p, rrect_m(cx, 4, 7, 22, 2), BRASS, r=3)
    p = finish(p) and p
    p.hline(10, 9, 44, GLASS[4])
    p.hline(13, 11, 38, AMBER[4])
    for x, y in ((14, 16), (20, 18), (26, 15), (33, 19), (40, 15), (47, 18)):
        p.px(x, y, FLAME[4])
        p.px(x + 1, y + 1, FLAME[3])
    p.line(18, 14, 24, 19, FLAME[4])
    p.line(24, 19, 30, 14, FLAME[4])
    p.line(30, 14, 37, 19, FLAME[3])
    for x in (5, 57):
        stud(p, x, 7)
        stud(p, x, 21)
    return p.im


# ------------------------------------------------------------------------------------------------ heaps of junk

def _put(p: Pix, m: set, ramp: Ramp, r: int = 2) -> None:
    ring = {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - m
    for x, y in ring:
        p.px(x, y, SHADOW)
    puff(p, m, ramp, r=r)


def pile(w: int, h: int, box: tuple[int, int, int, int], seed: int, cloth: tuple[Ramp, ...], pieces: int,
         grate: bool = False, peak: float = 0.5) -> Image.Image:
    """A heap of yard junk built back to front inside `box`: planks, hoops, wheels, sacks, cloth, crate chunks."""
    p = Pix(w, h, seed=seed)
    rng = p.rng
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    px_ = x0 + bw * peak

    def top(x: float) -> float:
        d = (x - px_) / (bw * (peak if x < px_ else 1 - peak))
        return y0 + bh * (0.15 + 0.85 * min(1.0, abs(d)) ** 1.5)

    heap = {(x, y) for x in range(x0, x1) for y in range(int(top(x)), y1 - 2)}
    puff(p, heap, STONE, r=5, flat=0.2, bias=-0.2)
    items: list[tuple[int, Callable[[], None]]] = []
    for _ in range(pieces):
        cx = rng.randint(x0 + 4, x1 - 4)
        cy = rng.randint(min(int(top(cx)) + 3, y1 - 8), y1 - 5)
        kind = rng.choice(("plank", "plank", "hoop", "wheel", "sack", "cloth", "cloth", "chunk", "stave"))
        c = rng.choice(cloth)
        ang = rng.uniform(-0.9, 0.9)
        ln = rng.randint(max(8, bw // 6), max(12, bw // 3))

        def draw(kind=kind, cx=cx, cy=cy, c=c, ang=ang, ln=ln) -> None:
            dx, dy = math.cos(ang) * ln / 2, math.sin(ang) * ln / 2
            if kind == "plank":
                _put(p, line_m([(round(cx - dx), round(cy - dy)), (round(cx + dx), round(cy + dy))], 3),
                     rng.choice((WOOD, PALE_WOOD, OAK)))
            elif kind == "stave":
                _put(p, line_m([(round(cx - dx), round(cy - dy)), (round(cx + dx), round(cy + dy))], 2), PALE_WOOD)
            elif kind == "hoop":
                r = rng.randint(5, 8)
                m = ell_m(cx - r, cy - r // 2 - 1, 2 * r, r + 3)
                inner = ell_m(cx - r + 2, cy - r // 2 + 1, 2 * r - 4, r - 1)
                _put(p, m - inner, IRON, 1)
            elif kind == "wheel":
                r = rng.randint(6, 9)
                m = ell_m(cx - r, cy - r, 2 * r, 2 * r)
                hub = ell_m(cx - 2, cy - 2, 4, 4)
                inner = ell_m(cx - r + 2, cy - r + 2, 2 * r - 4, 2 * r - 4)
                _put(p, m - inner, WOOD, 2)
                for a in range(0, 360, 60):
                    q = (round(cx + math.cos(math.radians(a)) * (r - 2)), round(cy + math.sin(math.radians(a)) * (r - 2)))
                    puff(p, line_m([(cx, cy), q], 1), WOOD, r=1)
                puff(p, hub, IRON, r=2)
            elif kind == "sack":
                _put(p, ell_m(cx - 6, cy - 5, 13, 11), LINEN if rng.random() < 0.5 else OCHRE, 4)
                p.hline(cx - 2, cy - 4, 5, SHADOW)
            elif kind == "cloth":
                pts = [(cx - 8, cy), (cx - 2, cy - 5), (cx + 7, cy - 3), (cx + 9, cy + 4), (cx + 2, cy + 6), (cx - 6, cy + 5)]
                _put(p, poly_m(pts), c, 3)
            else:
                _put(p, rrect_m(cx - 5, cy - 4, 11, 9, 1), WOOD, 2)
                p.line(cx - 4, cy - 3, cx + 4, cy + 3, WOOD[0])

        items.append((cy, draw))
    if grate:
        gx, gy = x0 + bw // 2 - 14, y0 + bh // 2 - 4
        items.append((gy + 12, lambda: _grate(p, gx, gy)))
    for _, fn in sorted(items, key=lambda t: t[0]):
        fn()
    p.outline(SHADOW)
    for _ in range(pieces * 3):                              # glints of metal and glass in the heap
        x, y = rng.randint(x0 + 3, x1 - 3), rng.randint(int(top(x0 + bw // 2)) + 4, y1 - 4)
        if p.get(x, y)[3]:
            p.px(x, y, rng.choice((STEEL[3], BRASS[3], GLASS[4])))
    return p.im


def _grate(p: Pix, x: int, y: int) -> None:
    puff(p, rect_m(x, y, 28, 16), IRON, r=2)
    p.frame(x - 1, y - 1, 30, 18, SHADOW)
    for yy in range(y + 3, y + 14, 3):
        p.hline(x + 2, yy, 24, SHADOW)
        p.hline(x + 2, yy + 1, 24, IRON[4])


ASSETS: Mapping[str, Draw] = {
    _f("debris_pile1"): partial(pile, 80, 48, (3, 3, 77, 46), 1, (WINE, MOSS, NAVY), 13, peak=0.55),
    _f("debris_pile2"): partial(pile, 80, 80, (4, 5, 78, 77), 2, (PLUM, WINE, OCHRE), 24, peak=0.6),
    _f("debris_pile3"): partial(pile, 96, 64, (2, 4, 94, 62), 3, (WINE, WINE, MOSS), 22, peak=0.35),
    _f("dumping_ground_pile"): partial(pile, 96, 48, (2, 3, 94, 45), 4, (MOSS, NAVY, WINE), 14, grate=True, peak=0.5),
    _f("fridge"): larder,
    _f("makeshift_reactor"): still,
    _f("plasma_fuel_cell"): oil_tube,
    _f("smuggler_bay"): partial(slat_crate, 7, 6, 41, 43, 48, 1),
    _f("smuggler_bay_large"): partial(slat_crate, 3, 2, 45, 45, 48, 2),
    _f("smuggler_bay_mini"): partial(slat_crate, 3, 2, 29, 30, 32, 3),
    _f("storage_bay"): partial(coffer, 6, 42, GREYOAK, "open", 1),
    _f("storage_bay1"): partial(coffer, 6, 42, PALE_WOOD, "open", 2),
    _f("storage_bay2"): partial(coffer, 6, 42, MOSS, "open", 3),
    _f("storage_bay_chem"): partial(coffer, 6, 42, WINE, "chem", 4),
    _f("storage_bay_gun"): partial(coffer, 6, 42, IRON, "gun", 5),
    _f("storage_bay_large"): partial(coffer, 2, 46, GREYOAK, "open", 6),
    _f("storage_bay_large1"): partial(coffer, 2, 46, PALE_WOOD, "open", 7),
    _f("storage_bay_large2"): partial(coffer, 2, 46, MOSS, "open", 8),
}
