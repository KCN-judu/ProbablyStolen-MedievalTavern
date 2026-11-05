"""Husbandry sprites: rats (living and dead, two coats, five sizes), traps, droppings, cage, feeder, skep, quill."""

from __future__ import annotations

import math

from PIL import Image

from itemkit_farm import (
    BONE, BRASSR, BROWN, CREAM, IRONR, LEAF, OAKR, PALER, PINK, SOIL, STRAW, Shape, box, edge, ell, flat, grow, line_set, mk,
    only, part, poly, rim, shade, stroke, tube,
)
from palette import BRASS, IRON, SHADOW, WOOD
from pix import Pix, mix, rgb

COAT = {"f": mk("#8f8884"), "m": mk("#5d433c")}
BELLY = {"f": mk("#cfc6bc"), "m": mk("#9a8478")}
PINKR = mk("#e29a94")


def rat_alive(w: int, h: int, sex: str) -> Pix:
    p = Pix(w, h, seed=w * 7 + h)
    c, bl = COAT[sex], BELLY[sex]
    big = h >= 22
    ground = h - 1
    # tail first: a pink whip that trails to the right and curls up at the end
    if h <= 16:
        tail = tube([(w * 0.78, h * 0.5, 0.6), (w * 0.88, h - 3.5, 0.5), (w - 3, h - 2.5, 0.5), (w - 1, h - 4.5, 0.5)])
        flat(p, tail, PINKR[2])
        for x, y in tail:
            if x % 2:
                p.px(x, y, PINKR[3])
    else:
        tail = tube([(w * 0.78, h * 0.5, 1.3), (w * 0.9, h * 0.8, 1.0), (w - 4, h - 2.5, 0.8), (w - 1.5, h - 5, 0.6)] if False else [(w * 0.78, h * 0.5, 0.9), (w * 0.9, h * 0.8, 0.8), (w - 4, h - 2.5, 0.7), (w - 1.5, h - 5, 0.5)])
        part(p, tail, PINKR, 2, grad=0.4)
    pts = [(0.0, 0.66), (0.04, 0.5), (0.10, 0.36), (0.17, 0.29), (0.24, 0.33), (0.30, 0.27), (0.40, 0.15), (0.52, 0.07), (0.62, 0.09), (0.71, 0.19),
           (0.77, 0.36), (0.80, 0.52), (0.77, 0.72), (0.75, 0.97), (0.57, 0.97), (0.58, 0.85), (0.47, 0.83), (0.34, 0.83), (0.31, 0.97), (0.16, 0.97),
           (0.18, 0.85), (0.14, 0.76), (0.06, 0.75)]
    body = poly([(x * (w - 1), y * (h - 1)) for x, y in pts]) | ell(w * 0.62, h * 0.55, w * 0.16, h * 0.42)
    body = {(x, y) for x, y in body if y < h and y >= 0}
    part(p, body, c, 2, grad=1.0)
    cols = {}
    for x, y in body:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    # pale belly between the legs
    for x in range(int(w * 0.33), int(w * 0.57)):
        if x in cols:
            for y in range(round(h * 0.74), round(h * 0.84)):
                if (x, y) in body and (x, y - 1) in body:
                    p.px(x, y, bl[2] if (x + y) % 4 else bl[1])
    # thigh line
    thigh = {(x, y) for x, y in rim(ell(w * 0.64, h * 0.58, w * 0.14, h * 0.34)) if x < w * 0.64 and (x, y) in body}
    flat(p, thigh, c[1])
    # fur strokes
    n = 0
    for x in range(int(w * 0.28), int(w * 0.72), 3):
        if x in cols:
            lo, hi = cols[x]
            y = lo + 2 + (n % 3)
            if (x, y) in body and hi - lo > 5:
                p.px(x, y, c[3])
                p.px(x + 1, y + 1, c[1])
                if big:
                    p.px(x + 1, y + 3, c[1])
                    p.px(x, y + 2, c[3])
            n += 1
    for k in range(2 if not big else 3):                          # forehead to nose highlight
        p.px(2 + k * 2, round(h * 0.48) - k, c[4])
    ear = ell(w * 0.21, h * 0.25, max(1.2, w * 0.04), max(1.4, h * 0.09))
    part(p, ear, PINKR, 2, grad=0.5)
    ey = round(h * 0.46)
    p.px(round(w * 0.09), ey, SHADOW)
    if big:
        p.px(round(w * 0.09) - 1, ey - 1, CREAM[4])
        for k in range(3):
            p.px(1 + k, round(h * 0.74) + (k // 2), bl[3])
    p.px(0, round(h * 0.66), rgb("#d07a80"))
    p.px(1, round(h * 0.66), SHADOW)
    for fx in (w * 0.17, w * 0.58):                              # pink toes
        for k in range(2 if h <= 16 else 3):
            p.px(round(fx) + k, ground, PINKR[2] if k != 1 else PINKR[3])
    return p


def rat_dead(w: int, h: int, sex: str) -> Pix:
    """Belly up: pale underside, four stiff paws in the air, a limp tail, a cross for an eye."""
    p = Pix(w, h, seed=w * 5 + h)
    c, bl = COAT[sex], BELLY[sex]
    big = h >= 22
    cy = h * 0.68
    tail = tube([(w * 0.84, cy + 1, 0.7), (w * 0.9, h - 2.5, 0.6), (w - 2, h - 2.4, 0.5), (w - 1, h - 4, 0.5)])
    if big:
        part(p, tail, PINKR, 2, grad=0.4)
    else:
        flat(p, tail, PINKR[2])
    body = ell(w * 0.47, cy, w * 0.33, h * 0.27) | ell(w * 0.68, cy + 0.02 * h, w * 0.17, h * 0.26)
    body = {(x, y) for x, y in body if y < h - 1}
    head = ell(w * 0.15, cy - 0.04 * h, w * 0.13, h * 0.22) | poly([(0.5, cy - h * 0.12), (w * 0.2, cy - h * 0.26), (w * 0.2, cy + h * 0.2), (w * 0.05, cy + h * 0.04)])
    part(p, body, c, 2, grad=0.7)
    cols = {}
    for x, y in body:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    for x, (lo, hi) in cols.items():
        n = hi - lo + 1
        if n >= 4:
            for y in range(lo + 1, hi - max(1, n // 4) + 1):
                t = (y - lo) / n
                if (x - 1, y) in body and (x + 1, y) in body:
                    p.px(x, y, bl[3] if t < 0.5 else bl[2])
    part(p, head, c, 2, grad=0.9)
    # paws: stiff limbs standing up from the belly, pink at the ends
    plen = max(3, round(h * 0.3))
    for fx, lean in ((0.3, -1), (0.42, 1), (0.6, -1), (0.74, 1)):
        x0 = round(w * fx)
        lo = cols.get(x0, (round(cy), 0))[0]
        limb = tube([(x0, lo + 2, 1.0 + 0.5 * big), (x0 + lean * 1.5, lo - plen * 0.5, 0.9 + 0.4 * big), (x0 + lean * 2.5, lo - plen, 0.8 + 0.4 * big)])
        part(p, limb, c, 2, grad=0.3)
        for dx in range(-1 if big else 0, 1 + big):
            p.px(round(x0 + lean * 2.5) + dx, lo - plen, PINKR[3])
        p.px(round(x0 + lean * 2.5), lo - plen + 1, PINKR[2])
    ex, ey = round(w * 0.1), round(cy - h * 0.06)
    for dx, dy in ((0, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)):
        if big or (dx, dy) == (0, 0) or dx * dy == 1:
            p.px(ex + dx, ey + dy, SHADOW)
    p.px(0, round(cy - h * 0.04), PINKR[1])
    ear = ell(w * 0.21, cy - h * 0.2, max(1.2, w * 0.04), max(1.2, h * 0.08))
    part(p, ear, PINKR, 2, grad=0.5)
    return p


def rat(w: int, h: int, sex: str, dead: bool, cw: int, ch: int) -> Image.Image:
    r = (rat_dead if dead else rat_alive)(w, h, sex)
    out = Pix(cw, ch)
    out.paste(r, 0, 0)
    return out.im


# ---------------------------------------------------------------------- traps

def trap(p: Pix, ox: int, oy: int, cheese: bool, snapped: bool = False) -> None:
    """A wooden snap trap: oak board, an iron striking bar and a trigger plate (with a bait if asked)."""
    boardw, boardh = 30, 9
    board = box(ox, oy + 5, boardw, boardh)
    part(p, board, OAKR, 2, grad=0.9)
    for x in range(ox + 3, ox + boardw - 1, 7):
        p.hline(x, oy + 9, 4, OAKR[1])
    p.hline(ox + 1, oy + 6, boardw - 2, OAKR[4])
    plate = box(ox + 18, oy + 7, 8, 5)
    part(p, plate, BRASSR, 2, grad=0.7)
    p.px(ox + 21, oy + 9, BRASSR[0])
    # spring: a coil at the hinge and the bar
    for k in range(3):
        part(p, ell(ox + 4 + k * 2, oy + 4, 1.4, 2.2), IRONR, 2, outline=None, grad=0.4)
    if snapped:
        bar = box(ox + 5, oy + 7, 22, 2)
        part(p, bar, IRONR, 2, grad=0.5)
    else:
        bar = tube([(ox + 5, oy + 4, 0.8), (ox + 5, oy + 0.5, 0.8), (ox + 21, oy + 0.5, 0.8), (ox + 21, oy + 5, 0.8)])
        part(p, bar, IRONR, 3, grad=0.4)
    for x in (ox + 2, ox + boardw - 3):
        p.px(x, oy + 10, BRASS[3])
        p.px(x, oy + 11, BRASS[1])
    if cheese:
        w = poly([(ox + 19, oy + 10), (ox + 23, oy + 4), (ox + 27, oy + 10)])
        part(p, w, mk("#e0b043"), 2, grad=0.8)
        p.px(ox + 22, oy + 8, mk("#e0b043")[0])
        p.px(ox + 24, oy + 9, mk("#e0b043")[1])


def trap_pic(cheese: bool) -> Image.Image:
    p = Pix(48, 16, seed=5)
    trap(p, 9, 0, cheese)
    return p.im


def trap_rat(sex: str) -> Image.Image:
    p = Pix(48, 16, seed=6)
    trap(p, 17, 0, False, snapped=True)
    r = rat_dead(30, 11, sex)
    p.paste(r, 1, 4)
    trap_bar = box(14 + 8, 4, 2, 9)
    part(p, trap_bar, IRONR, 2, grad=0.4)
    return p.im


# ---------------------------------------------------------------------- droppings

def droppings(w: int, h: int, n: int, seed: int) -> Image.Image:
    p = Pix(w, h, seed=seed)
    ramp = mk("#4a3426")
    rng = p.rng
    spots = []
    cols = max(1, round(math.sqrt(n * w / h)))
    k = 0
    for j in range(2 + (n > 5)):
        for i in range(cols):
            if k >= n:
                break
            spots.append((2.2 + (w - 5) * (i + 0.5 * (j % 2)) / max(1, cols), h - 3.5 - j * 3.1 + rng.uniform(-0.4, 0.4)))
            k += 1
    for x, y in sorted(spots, key=lambda s: s[1]):
        part(p, ell(x, y, 2.4, 1.7), ramp, 2, grad=0.8)
        p.px(round(x) - 1, round(y) - 1, ramp[4])
        p.px(round(x) + 1, round(y), ramp[0])
    return p.im


# ---------------------------------------------------------------------- quill

def quill() -> Image.Image:
    p = Pix(32, 16, seed=3)
    vane = poly([(2, 8), (6, 5), (16, 6), (24, 9), (25, 10), (14, 11), (5, 10)]) | poly([(1, 9), (3, 6), (3, 10)])
    vane = {(x, y) for x, y in vane if 5 <= y <= 10}
    part(p, vane, CREAM, 3, grad=0.6)
    for x in range(5, 24, 2):                                   # barbs
        p.px(x, 6 + (x // 4) % 2, CREAM[1])
        p.px(x + 1, 10 - (x // 6) % 2, CREAM[1])
    shaft = line_set(2, 9, 29, 8)
    flat(p, shaft, mk("#e8dcc0")[4])
    tip = tube([(24, 8.4, 0.6), (28, 8.2, 0.5), (30, 8, 0.4)])
    part(p, tip, mk("#e8dcc0"), 3, grad=0.2)
    flat(p, {(30, 8), (31, 8)}, mk("#2a2438")[1])
    p.px(29, 8, mk("#2a2438")[2])
    p.px(29, 9, mk("#2a2438")[0])
    edge(p, vane | shaft)
    return p.im


# ---------------------------------------------------------------------- cage, feeder, skep

def cage() -> Image.Image:
    p = Pix(64, 48, seed=41)
    front = box(3, 15, 45, 31)
    side = poly([(48, 15), (62, 5), (62, 36), (48, 46)])
    top = poly([(3, 15), (17, 4), (62, 4), (48, 15)])
    part(p, side, WOOD, 2, grad=0.8, lo=0.5)
    for k in range(1, 4):
        p.line(48 + k * 3, 15 - k * 3 + 31 * 0 if False else 16 - k * 3, 48 + k * 3, 46 - k * 3 + 0, WOOD[1])
    part(p, top, mk("#8c6840"), 2, grad=0.8)
    for k in range(1, 6):
        x = 3 + k * 8
        p.line(x - 11 + 1, 13, x + 3 - 1 + 0, 5, mk("#8c6840")[1])
    part(p, front, WOOD, 2, grad=0.5)
    # the opening, hay inside, iron bars over it
    opening = box(7, 20, 37, 21)
    part(p, opening, mk("#1d1210"), 1, outline=SHADOW, grad=0.3)
    flat(p, {(x, y) for x, y in opening if y >= 36 and (x + y) % 3}, STRAW[2])
    flat(p, {(x, y) for x, y in opening if y >= 38}, STRAW[1])
    for x in range(9, 44, 4):
        p.vline(x, 20, 21, IRON[3])
        p.vline(x + 1, 20, 21, IRON[1])
        p.px(x, 20, IRON[4])
    p.hline(7, 29, 37, IRON[2])
    p.hline(7, 30, 37, IRON[1])
    p.hline(3, 43, 45, WOOD[1])
    p.hline(3, 15, 45, WOOD[4])
    for x in (5, 46):
        p.vline(x, 16, 28, IRON[2])
    lock = box(23, 40, 5, 4)
    part(p, lock, BRASSR, 2, grad=0.7)
    p.px(25, 41, SHADOW)
    for x, y in ((5, 17), (46, 17), (5, 43), (46, 43)):
        p.px(x, y, BRASS[4])
    # iron ring handle on the roof
    ring = ell(33, 8, 4.5, 2.0) - ell(33, 8, 2.5, 0.8)
    part(p, ring, IRONR, 3, outline=None, grad=0.3)
    edge(p, front | side | top)
    return p.im


def feeder() -> Image.Image:
    p = Pix(48, 48, seed=43)
    trough = box(34, 28, 12, 11) | box(36, 25, 9, 4)
    part(p, trough, OAKR, 2, grad=0.8)
    grain = ell(40, 27, 4.5, 2)
    part(p, grain, mk("#d4a64a"), 2, outline=None, grad=0.8)
    for x in (37, 40, 42):
        p.px(x, 27, mk("#d4a64a")[4])
    p.hline(34, 34, 12, OAKR[1])
    # the hopper bin
    bin_ = box(5, 13, 29, 25)
    part(p, bin_, WOOD, 2, grad=0.8)
    for x in range(10, 33, 6):
        p.vline(x, 14, 23, WOOD[1])
        p.vline(x + 1, 14, 23, WOOD[3])
    lid = poly([(3, 13), (9, 6), (31, 6), (36, 13)])
    part(p, lid, mk("#8c6840"), 2, grad=0.8)
    for x in (12, 19, 26):
        p.line(x - 2, 12, x + 1, 7, mk("#8c6840")[1])
    p.hline(3, 13, 33, IRON[1])
    p.hline(3, 12, 33, IRON[3])
    # arched hatch with brass pull
    hatch = box(11, 25, 14, 12) | ell(17.5, 25, 7, 5)
    part(p, hatch, mk("#1d1210"), 1, outline=SHADOW, grad=0.3)
    door = box(13, 27, 10, 9) | ell(17.5, 27, 5, 4)
    door = {(x, y) for x, y in door if y <= 36}
    part(p, door, OAKR, 3, grad=0.8)
    p.vline(17, 25, 11, OAKR[1])
    p.px(20, 31, BRASS[4]), p.px(21, 31, BRASS[2])
    # iron bands and feet
    for y in (17, 34):
        p.hline(5, y, 29, IRON[2])
        p.hline(5, y + 1, 29, IRON[1])
    for x in (8, 30):
        p.px(x, 17, BRASS[3])
    for x in (6, 28):
        part(p, box(x, 38, 5, 3), OAKR, 2, grad=0.4)
    edge(p, bin_ | lid | trough)
    return p.im


def skep() -> Image.Image:
    """A coiled-straw beehive, the round low thing a husbandman keeps."""
    p = Pix(48, 32, seed=47)
    cx, by, rx, ry = 22.5, 26, 22.0, 22.0
    dome = {(x, y) for x, y in ell(cx, by, rx, ry) if y <= by}
    base = box(1, 26, 44, 3)
    for x, y in sorted(dome):
        d = math.sqrt(((x - cx) / rx) ** 2 + ((y - by) / ry) ** 2)
        band = int(d * 7.3)
        up = math.sqrt(((x - cx) / rx) ** 2 + ((y - 1 - by) / ry) ** 2)
        seam = int(up * 7.3) != band
        tone = 3 if band % 2 else 2
        lit = (x - cx) / rx
        if lit < -0.35:
            tone += 1
        elif lit > 0.45:
            tone -= 1
        if lit > 0.8:
            tone -= 1
        c = STRAW[max(0, min(4, tone))]
        if seam:
            c = STRAW[max(0, tone - 2)]
        p.px(x, y, c)
        if (x * 3 + y) % 7 == 0 and not seam and lit < 0.5:                # stray stalks
            p.px(x, y, STRAW[min(4, tone + 1)])
    part(p, base, OAKR, 2, grad=0.9)
    p.hline(1, 26, 44, OAKR[4])
    entry = {(x, y) for x, y in ell(cx - 3, 25, 5, 5) if y <= 25}
    part(p, entry, mk("#2a1a12"), 1, outline=SHADOW, grad=0.2)
    p.hline(15, 26, 12, SHADOW)
    # top knot
    knot = ell(cx, 5, 3, 2.3)
    part(p, knot, STRAW, 2, grad=0.8)
    edge(p, dome | base)
    return p.im


# ---------------------------------------------------------------------- the list

PICS: dict = {
    "animal_cage": cage,
    "animal_feeder": feeder,
    "feces": lambda: droppings(16, 16, 6, 1),
    "feces_large": lambda: droppings(32, 16, 10, 2),
    "feces_small": lambda: droppings(16, 16, 3, 3),
    "marking_pen": quill,
    "mouse_trap": lambda: trap_pic(False),
    "mouse_trap_cheese": lambda: trap_pic(True),
    "mouse_trap_f": lambda: trap_rat("f"),
    "mouse_trap_m": lambda: trap_rat("m"),
    "vacuum_robot": skep,
}
for _size, (_w, _h, _cw, _ch) in {"s": (28, 10, 32, 16), "m": (40, 14, 48, 16), "l": (44, 15, 48, 16), "xl": (45, 24, 48, 32), "xxl": (60, 30, 64, 32)}.items():
    for _sex in ("f", "m"):
        PICS[f"rat_{_size}_{_sex}"] = lambda a=_w, b=_h, s=_sex, c=_cw, d=_ch: rat(a, b, s, False, c, d)
        PICS[f"rat_{_size}_{_sex}_d"] = lambda a=_w, b=_h, s=_sex, c=_cw, d=_ch: rat(a, b, s, True, c, d)
