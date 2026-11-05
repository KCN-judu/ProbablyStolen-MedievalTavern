"""Fish, eels, roe, fillets, feed and the fish vats of the aquaculture sprites."""

from __future__ import annotations

import math

from PIL import Image

from itemkit_farm import (
    BONE, BRASSR, BROWN, CLAY, CREAM, IRONR, LEAF, LEAF_DK, OAKR, PALER, PEWTER, SOIL, STRAW, TEAL, WINER, Shape, box, edge, ell,
    flat, grow, line_set, mk, only, part, poly, rim, shade, shift, stroke, tube, wave,
)
from palette import BRASS, IRON, SHADOW, STONE, WOOD
from pix import Pix, mix, rgb

HI = rgb("#fff0c0")


def columns(s: Shape) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for x, y in s:
        lo, hi = out.get(x, (y, y))
        out[x] = (min(lo, y), max(hi, y))
    return out


def vband(p: Pix, s: Shape, ramp, cuts=(0.2, 0.48, 0.8), streak: bool = True, scales: bool = False, outline: bool = True) -> None:
    """Colours a fish-like shape by how far down it each pixel is (dark back, lit flank, pale belly)."""
    cols = columns(s)
    for x, y in s:
        lo, hi = cols[x]
        f = (y - lo + 0.5) / (hi - lo + 1)
        i = 1 if f < cuts[0] else 2 if f < cuts[1] else 3 if f < cuts[2] else 4
        if lo == y:
            i = 0 if hi - lo > 3 else 1
        if scales and 2 <= i <= 3 and (x + (y % 2) * 2) % 4 == 0 and y > lo + 1 and y < hi:
            i = min(4, i + 1)
        p.px(x, y, ramp[i])
    if streak:                                                   # the glint along the flank
        for x, (lo, hi) in cols.items():
            if hi - lo >= 4 and (x % 4) != 3:
                yy = lo + max(1, round((hi - lo) * 0.3))
                if (x, yy) in s:
                    p.px(x, yy, ramp[4])
    if outline:
        edge(p, s)


# ---------------------------------------------------------------------- fish

def fish_shape(w: int, h: int, deep: float, ox: int = 0, oy: int = 0) -> tuple[Shape, Shape, int, int]:
    """Body (head at left) and tail, in a box w x h; returns body, tail, eye x, centre y."""
    bl = round(w * 0.78)
    cy = oy + h / 2 - 0.5
    body: Shape = set()
    for x in range(bl):
        t = (x + 0.5) / bl
        hh = (h / 2 - 1.5) * (math.sin(math.pi * min(1.0, t * 1.0 + 0.04)) ** 0.5) * (1 - 0.55 * t ** 2) * deep + 0.6
        top = cy - hh * 1.0
        bot = cy + hh * 1.05
        for y in range(math.ceil(top - 0.3), math.floor(bot + 0.3) + 1):
            body.add((ox + x, y))
    tl = w - bl + 2
    tx = ox + bl - 2
    tail = poly([(tx, cy - 1.0), (tx + tl, cy - h * 0.42), (tx + tl - 2, cy), (tx + tl, cy + h * 0.42), (tx, cy + 1.0)])
    return body, tail, ox + 3, round(cy)


def fish(w: int, h: int, pal, bars: bool = False, fin_ramp=None, spiny: bool = True, snout: float = 0.0) -> Image.Image:
    p = Pix(w, h, seed=w + h)
    body, tail, ex, cy = fish_shape(w, h - 4 if h > 18 else h - 2, 1.0, 0, 3 if h > 18 else 1)
    fr = fin_ramp or pal
    cols = columns(body)
    top = lambda x: cols[x][0]
    bot = lambda x: cols[x][1]
    # fins behind the body: dorsal, anal, pelvic
    n0, n1 = int(w * 0.28), int(w * 0.66)
    dorsal = poly([(n0, top(n0) + 1), (n0 + 1, top(n0) - h * 0.2), (int((n0 + n1) / 2), top(int((n0 + n1) / 2)) - h * 0.24),
                   (n1 - 3, top(n1 - 3) - h * 0.1), (n1, top(n1) + 1)])
    anal = poly([(int(w * 0.5), bot(int(w * 0.5)) - 1), (int(w * 0.56), bot(int(w * 0.56)) + h * 0.14), (int(w * 0.66), bot(int(w * 0.66)) - 1)])
    pelvic = poly([(int(w * 0.28), bot(int(w * 0.28)) - 1), (int(w * 0.25), bot(int(w * 0.25)) + h * 0.14), (int(w * 0.36), bot(int(w * 0.36)) - 1)])
    for f in (dorsal, anal, pelvic, tail):
        part(p, f - body if f is not tail else f, fr, 2, grad=0.5)
    # spines and rays
    for x in range(n0 + 1, n1, 2):
        if x in cols and top(x) - 3 >= 0:
            yy = top(x) - 1
            if (x, yy) in dorsal:
                p.px(x, yy, fr[4])
    ty = (h - 1) / 2
    for k in (-2, -1, 0, 1, 2):
        for t in range(0, 6):
            xx, yy = w - 4 - t, round(ty + k * (4 - t * 0.4) * h / 20)
            if (xx, yy) in tail and t < 4:
                p.px(xx, yy, fr[1] if k % 2 else fr[3])
    vband(p, body, pal, scales=w >= 28)
    if bars:
        for x in range(int(w * 0.3), int(w * 0.68), 4):
            if x in cols:
                lo, hi = cols[x]
                for y in range(lo + 1, hi):
                    p.px(x, y, pal[1])
    # gill, eye, mouth
    gx = max(4, int(w * 0.24))
    if gx in cols:
        lo, hi = cols[gx]
        for y in range(lo + 2, hi - 1):
            p.px(gx, y, pal[1])
        if w >= 28:
            p.px(gx + 1, lo + 2, pal[3])
    e_y = cols[ex][0] + max(2, round((cols[ex][1] - cols[ex][0]) * 0.28))
    p.px(ex, e_y, SHADOW)
    if w >= 28:
        p.px(ex - 1, e_y - 1, CREAM[4])
        p.px(ex + 1, e_y - 1, CREAM[4])
        p.px(ex, e_y - 1, CREAM[3])
        p.px(ex - 1, e_y, CREAM[3])
        p.px(ex + 1, e_y, CREAM[3])
        p.px(ex, e_y + 1, CREAM[3])
        p.px(ex, e_y, SHADOW)
    else:
        p.px(ex - 1, e_y - 1, CREAM[4])
    my = cols[0][0] + (cols[0][1] - cols[0][0]) // 2 + 1
    if 0 in cols and (cols[0][1] - cols[0][0]) >= 2:
        p.px(0, my, pal[0])
    for f in (dorsal - body, anal - body, pelvic - body, tail):
        edge(p, f)
    return p.im


FISH_PAL = {
    1: (mk("#4f7aa0"), mk("#d28a6a")),        # silvery blue roach with ruddy fins
    2: (mk("#3e9a86"), mk("#e0b24a")),        # green-gold tench
    3: (mk("#8a8a3c"), mk("#a8542c")),        # olive carp with rusty fins
}


def tilapia(size: str, kind: int) -> Image.Image:
    w, h = {"s": (25, 14), "m": (30, 23), "l": (42, 26)}[size]
    pal, fin = FISH_PAL[kind]
    return fish(w, h, pal, bars=(kind == 3), fin_ramp=fin)


# ---------------------------------------------------------------------- eels

EEL_PAL = {1: mk("#6a7440"), 2: mk("#5a3a52")}


def eel(w: int, h: int, kind: int) -> Image.Image:
    p = Pix(w, h, seed=w)
    r = 3.6 if w >= 60 else 3.2 if w >= 45 else 2.8
    r = max(2.6, r * w / 70) if w < 80 else 4.0
    amp = (h - 2 * r - 3) / 2
    pts = wave(3 + r, w - 5, h / 2 - 0.5, amp * 0.9, 1.1, r * 0.85, 0.9, phase=math.pi * 0.15, bulge=0.45 * r)
    # the head: broader, pointing left
    body = tube(pts)
    ramp = EEL_PAL[kind]
    cols = columns(body)
    # fin ridge along the back and the vent
    vband(p, body, ramp, cuts=(0.25, 0.55, 0.82), outline=False)
    fin: Shape = set()
    for x in range(int(w * 0.28), w - 5):
        if x in cols:
            fin.add((x, cols[x][0] - 1))
    flat(p, fin, ramp[1])
    for x, y in fin:
        if x % 2 == 0:
            p.px(x, y, ramp[2])
    s2 = body | fin
    edge(p, s2)
    hx = pts[0][0]
    hy = pts[0][1]
    # eye and gill
    ex, ey = round(hx + r * 0.6), round(hy - r * 0.35)
    p.px(ex, ey, SHADOW)
    p.px(ex + 1, ey - 1, CREAM[4]) if w >= 45 else None
    gx = round(hx + r * 2.4)
    for y in range(round(pts[round(len(pts) * 0.07)][1] - r * 0.3), round(pts[round(len(pts) * 0.07)][1] + r * 0.7)):
        if (gx, y) in body:
            p.px(gx, y, ramp[0])
    return p.im


# ---------------------------------------------------------------------- meat

SKIN = mk("#3f5a74")
FLESH_V = {1: mk("#c0413c"), 2: mk("#d4685a"), 3: mk("#e19a94"), 4: mk("#ecd2c0")}


def fillet(w: int, h: int, kind: int) -> Image.Image:
    p = Pix(w, h, seed=kind)
    fl = FLESH_V[kind]
    s = poly([(0, h * 0.35), (w * 0.12, 0), (w * 0.75, 0), (w - 1, h * 0.4), (w - 1, h - 1 - h * 0.2), (w * 0.8, h - 1), (w * 0.15, h - 1), (0, h * 0.7)])
    s = {(x, y) for x, y in s if 0 <= x < w and 0 <= y < h} | {(x, y) for x, y in ell(w / 2 - 0.5, h / 2 - 0.5, w / 2, h / 2) if 0 <= x < w and 0 <= y < h}
    shade(p, s, fl, 2, grad=1.0)
    cols = columns(s)
    # chevron muscle flakes (myomeres) running toward the tail
    step = 4 if w < 40 else 5
    for x0 in range(3, w - 3, step):
        for k in range(h // 2 - 1):
            for sgn in (-1, 1):
                x, y = x0 + k, round(h / 2 - 0.5 + sgn * k)
                if (x, y) in s and (x + 1, y) in s and y > cols.get(x, (0, 0))[0] + 1 and y < cols.get(x, (0, h))[1] - 1:
                    p.px(x, y, fl[4] if sgn < 0 else fl[3])
                    p.px(x, y + 1, fl[1]) if sgn > 0 else None
    # skin edge along the top, silvery and darker
    skin = {(x, y) for x, y in s if y <= cols[x][0] + (1 if h < 20 else 2)}
    for x, y in skin:
        p.px(x, y, SKIN[2] if (x + y) % 3 else SKIN[3])
    for x in range(1, w - 1, 3):
        if x in cols:
            p.px(x, cols[x][0], SKIN[4])
    # fat line
    for x in range(4, w - 4):
        if x in cols:
            yy = cols[x][0] + (2 if h < 20 else 3)
            if (x, yy) in s:
                p.px(x, yy, CREAM[3] if x % 2 else CREAM[2])
    edge(p, s)
    for x, y in s:                                               # lit upper-left rim
        if (x - 1, y - 1) not in s and (x, y - 1) not in s and (x - 1, y) not in s:
            p.px(x, y, fl[4])
    return p.im


def fillet_tiny(kind: int) -> Image.Image:
    p = Pix(16, 16, seed=kind)
    fl = FLESH_V[kind]
    s = ell(7.5, 8, 6.5, 5)
    shade(p, s, fl, 2, grad=0.8)
    for y in range(6, 11):
        for x in range(4, 12):
            if (x + y) % 4 == 0 and (x, y) in s:
                p.px(x, y, fl[4])
    for x in range(3, 13):
        if (x, 4) in s:
            p.px(x, 4, SKIN[2])
    edge(p, s)
    return p.im


def steak_eel(w: int, h: int) -> Image.Image:
    p = Pix(w, h, seed=w)
    s = ell(w / 2 - 0.5, h / 2 - 0.5, w / 2, h / 2)
    shade(p, s, mk("#5a6a48"), 2, grad=0.8)
    inner = ell(w / 2 - 0.5, h / 2 - 0.5, w / 2 - 2.2, h / 2 - 2.0)
    shade(p, inner, mk("#e8d4bc"), 2, grad=0.8)
    edge(p, inner, mk("#5a6a48")[0])
    bone = ell(w / 2 - 0.5, h / 2 - 0.5, 1.6, 1.4)
    shade(p, bone, BONE, 2, grad=0.2)
    for dx in (-3, 3):
        p.px(round(w / 2 - 0.5) + dx, round(h / 2 - 0.5), mk("#e8d4bc")[1])
    edge(p, s)
    return p.im


# ---------------------------------------------------------------------- roe

EGG = {"roe": mk("#e0762c"), "roe2": mk("#e6c25a"), "roe3": mk("#8a9a3c"), "roe_fertilized": mk("#c43a30"),
       "roe_fertilized2": mk("#d8aa4c"), "roe_fertilized3": mk("#6f8a3a"), "roe_sturgeon": mk("#3a3a44")}


def roe(kind: str) -> Image.Image:
    p = Pix(16, 16, seed=len(kind))
    ramp = EGG[kind]
    eyed = "fertilized" in kind
    rows = [(3, [(4, 4)]), (2, [(3, 3), (7, 3), (11, 3)]), (1, [(2, 6), (6, 6), (10, 6), (13, 6)]), (0, [(1, 9), (5, 9), (9, 9), (12, 9), (3, 12), (7, 12), (10, 12)])]
    balls = [(5, 3), (9, 3), (3, 6), (7, 6), (11, 6), (13, 9), (5, 9), (9, 9), (1, 9), (3, 12), (7, 12), (11, 12), (13, 12)]
    balls = [(x, y) for x, y in balls]
    union: Shape = set()
    for cx, cy in balls:
        union |= ell(cx + 1, cy + 0.5, 2.1, 2.1)
    # draw back to front
    for cx, cy in sorted(balls, key=lambda b: b[1]):
        b = ell(cx + 1, cy + 0.5, 2.1, 2.1)
        part(p, b, ramp, 2, outline=ramp[0], grad=1.0)
        p.px(cx, cy - 1, ramp[4])
        if eyed:
            p.px(cx + 1, cy + 1, SHADOW)
            p.px(cx + 2, cy + 1, ramp[0])
        elif kind == "roe_sturgeon":
            p.px(cx, cy - 1, rgb("#9a9aa8"))
    edge(p, union)
    return p.im


# ---------------------------------------------------------------------- heaps of feed and fish

def heap(w: int, h: int, ramp, pellet=None, seed: int = 1, round_pellets: bool = False) -> Image.Image:
    p = Pix(w, h, seed=seed)
    s = poly([(1, h - 3), (w * 0.28, h * 0.45), (w * 0.5, 1), (w * 0.72, h * 0.45), (w - 2, h - 3)]) | ell(w / 2 - 0.5, h - 5, w / 2 - 1, 4) | ell(w / 2 - 0.5, h * 0.5, w * 0.3, h * 0.35)
    s = {(x, y) for x, y in s if 0 <= x < w and 0 <= y < h - 1}
    shade(p, s, ramp, 2, grad=1.3, dith=True)
    rng = p.rng
    for _ in range(int(len(s) * 0.12)):
        x, y = rng.choice(sorted(s))
        c = ramp[4] if (x + y) % 3 else ramp[0]
        p.px(x, y, c)
        if round_pellets and (x + 1, y) in s:
            p.px(x + 1, y, ramp[3])
    edge(p, s)
    return p.im


def scrap_bones() -> Image.Image:
    p = Pix(32, 16, seed=3)
    # bits of flesh in the dish
    for x, y, rx, ry in ((6, 12, 4.5, 2.2), (25, 12, 3.8, 2.2), (14, 13, 3.5, 1.6)):
        part(p, ell(x, y, rx, ry), FLESH_V[1], 2, grad=0.6)
    # skeleton
    spine = [(8, 7), (9, 7), (10, 6), (11, 6), (12, 6), (13, 7), (14, 7), (15, 7), (16, 7), (17, 7), (18, 7), (19, 6), (20, 6), (21, 6), (22, 7), (23, 7)]
    sp = tube([(x, y, 0.7) for x, y in spine]) | tube([(8, 7, 0.7), (23, 7, 0.7)])
    ribs: Shape = set()
    for x in range(10, 22, 2):
        ribs |= line_set(x, 6, x - 1, 3) | line_set(x, 7, x - 1, 10)
    head = poly([(1, 7), (3, 4), (7, 4), (9, 7), (7, 10), (3, 10)])
    tail = poly([(23, 7), (28, 3), (29, 7), (28, 11)])
    part(p, tail, BONE, 2, grad=0.4)
    part(p, sp | ribs, BONE, 3, grad=0.2, outline=None)
    edge(p, sp | ribs)
    part(p, head, BONE, 2, grad=0.8)
    p.px(4, 6, SHADOW), p.px(5, 6, SHADOW)
    p.hline(2, 8, 5, BONE[0])
    return p.im


def mini_fish(p: Pix, x0: float, y0: float, x1: float, y1: float, r: float, pal) -> None:
    s = tube([(x0, y0, r * 0.9), ((x0 + x1) / 2, (y0 + y1) / 2, r), (x1, y1, r * 0.45)])
    dx, dy = x1 - x0, y1 - y0
    tail = poly([(x1, y1), (x1 + dx * 0.25 + dy * 0.2, y1 + dy * 0.25 - dx * 0.2 - 1), (x1 + dx * 0.25 - dy * 0.2, y1 + dy * 0.25 + dx * 0.2 + 1)])
    part(p, tail, pal, 2, grad=0.3)
    vband(p, s, pal, cuts=(0.3, 0.55, 0.75), streak=False)
    p.px(round(x0 + 0.5), round(y0 - 0.3), SHADOW)


def silver_pile() -> Image.Image:
    p = Pix(32, 32, seed=7)
    pal = mk("#7e9cb4")
    pal2 = mk("#8aa8a0")
    fishes = [(3, 25, 18, 26), (9, 28, 25, 28), (4, 21, 20, 22), (11, 17, 26, 20), (6, 12, 21, 14), (14, 9, 27, 14), (8, 5, 22, 8), (3, 17, 14, 15)]
    for i, (a, b, c, d) in enumerate(fishes):
        mini_fish(p, a, b, c, d, 2.0, pal if i % 2 else pal2)
    return p.im


# ---------------------------------------------------------------------- vessel sprites

def caviar() -> Image.Image:
    p = Pix(32, 32, seed=4)
    # two pewter plates under an open dish of black roe
    for y, rx in ((24, 14), (20, 13)):
        d = ell(15.5, y, rx, 4) | box(int(15.5 - rx), y, int(rx * 2), 3)
        part(p, d, PEWTER, 2, grad=0.8)
        p.hline(int(15.5 - rx) + 1, y + 1, int(rx * 2) - 2, PEWTER[4])
    dish = ell(15.5, 15, 12, 6)
    part(p, dish, BRASSR, 2, grad=1.0)
    inner = ell(15.5, 15, 9.5, 4.2)
    part(p, inner, mk("#2c2a36"), 2, outline=BRASSR[0], grad=0.8)
    for x, y in ((11, 13), (14, 14), (18, 13), (21, 15), (13, 17), (17, 17), (10, 16)):
        p.px(x, y, rgb("#8a8a9c"))
        p.px(x + 1, y + 1, mk("#2c2a36")[0])
    return p.im


# ---------------------------------------------------------------------- the sturgeon

def sturgeon() -> Image.Image:
    w, h = 112, 32
    p = Pix(w, h, seed=11)
    ramp = mk("#7a6c62")
    belly = [(2, 22, 0.9), (10, 21, 2.6), (24, 19, 5.2), (42, 17, 7.8), (62, 17, 7.2), (82, 16, 4.0), (96, 14.5, 2.0)]
    body = tube(belly)
    tail_up = poly([(94, 14), (100, 4), (111, 1), (104, 10), (101, 14)])
    tail_dn = poly([(95, 15), (102, 19), (108, 26), (99, 24), (95, 17)])
    dorsal = poly([(70, 11), (75, 5), (84, 9), (82, 13)])
    anal = poly([(72, 23), (80, 28), (82, 22)])
    pect = poly([(30, 22), (34, 29), (41, 26), (39, 22)])
    for f in (tail_up, tail_dn):
        part(p, f, mk("#8a7a6e"), 2, grad=0.6)
    for f in (dorsal, anal):
        part(p, f - body, mk("#8a7a6e"), 2, grad=0.6)
    vband(p, body, ramp, cuts=(0.22, 0.5, 0.78), streak=False)
    cols = columns(body)
    # bony scutes: a ridge on the back, a row on the flank, a row on the belly
    for x in range(26, 90, 6):
        lo, hi = cols[x]
        for dx, dy in ((0, 1), (1, 1), (0, 0), (1, 2)):
            p.px(x + dx, lo + dy, ramp[4] if dy < 2 else ramp[3])
        yf = lo + round((hi - lo) * 0.45)
        p.px(x + 2, yf, ramp[4])
        p.px(x + 3, yf, ramp[3])
        p.px(x + 2, yf + 1, ramp[0])
        yb = lo + round((hi - lo) * 0.8)
        p.px(x + 3, yb, ramp[4])
        p.px(x + 4, yb, ramp[3])
    for x in range(8, 24, 3):                                    # head plates
        lo, hi = cols[x]
        p.px(x, lo + 2, ramp[4])
        p.px(x + 1, lo + 3, ramp[3])
    # gill cover, eye, barbels
    for y in range(cols[26][0] + 3, cols[26][1] - 3):
        p.px(26, y, ramp[0])
        p.px(27, y, ramp[1]) if y % 2 else None
    p.px(17, cols[17][0] + 4, SHADOW)
    p.px(16, cols[17][0] + 3, CREAM[4])
    p.px(18, cols[17][0] + 3, CREAM[3])
    for bx in (8, 11):
        p.px(bx, cols[bx][1] + 1, BONE[3])
        p.px(bx + 1, cols[bx][1] + 2, BONE[2])
    for f in (tail_up, tail_dn, dorsal - body, anal - body):
        edge(p, f)
    edge(p, body)
    for x in range(98, 108, 3):
        p.px(x, 5 + (x - 98) // 3 * -1 + 2, ramp[4])
    return p.im


# ---------------------------------------------------------------------- vats

STAVE = mk("#7a4e2a")


def stave_tub(p: Pix, x: int, y: int, w: int, h: int, rim_h: int, water: str | None, fishes: int = 0) -> None:
    """A big stave-built tub seen from slightly above: staves, iron hoops, and the water (or the dry bottom) inside."""
    cx = x + w / 2 - 0.5
    body = box(x, y + rim_h, w, h - rim_h) | ell(cx, y + h - 1.5, w / 2, 2.5)
    body = {(a, b) for a, b in body if b >= y + rim_h}
    part(p, body, STAVE, 2, grad=1.0)
    for sx in range(x + 3, x + w - 1, 5):
        p.vline(sx, y + rim_h + 1, h - rim_h - 3, STAVE[1])
        p.vline(sx + 1, y + rim_h + 1, h - rim_h - 3, STAVE[3])
    for hy in (y + rim_h + 4, y + h - 6):
        p.hline(x, hy, w, IRON[1])
        p.hline(x, hy + 1, w, IRON[3])
        for sx in range(x + 4, x + w - 2, 10):
            p.px(sx, hy + 1, BRASS[3])
    outer = ell(cx, y + rim_h, w / 2, rim_h)
    part(p, outer, mk("#9c6b3a"), 2, grad=0.8)
    inner = ell(cx, y + rim_h, w / 2 - 2.4, rim_h - 2.0)
    if water is None:
        part(p, inner, mk("#3a2a26"), 1, outline=SHADOW, grad=0.4)
        for sx, sy in ((cx - 8, y + rim_h), (cx + 3, y + rim_h + 1), (cx + 9, y + rim_h - 1)):
            p.hline(round(sx), round(sy), 3, mk("#5a4638")[3])
        p.hline(round(cx - 12), round(y + rim_h - 1), 3, mk("#6a5a40")[2])
        for sx in (cx - 5, cx + 6):
            part(p, ell(sx, y + rim_h + 1, 2.2, 1.2), mk("#6a645c"), 2, outline=None, grad=0.5)
    else:
        wr = mk("#3e8a86")
        part(p, inner, wr, 2, outline=SHADOW, grad=1.0)
        # ripples and a lit streak
        for k, (dx, dy, l) in enumerate(((-10, -2, 5), (2, 0, 6), (-4, 2, 4), (8, -2, 4))):
            p.hline(round(cx + dx), round(y + rim_h + dy), l, wr[4])
        for k, (dx, dy, l) in enumerate(((-7, 0, 3), (5, 2, 3), (11, 0, 2))):
            p.hline(round(cx + dx), round(y + rim_h + dy), l, wr[1])
        for k in range(fishes):
            fx, fy = round(cx - 9 + k * 8), round(y + rim_h - 1 + (k % 2) * 2)
            part(p, ell(fx + 2, fy, 3.2, 1.4), mk("#d28a6a"), 2, outline=wr[0], grad=0.6)
            p.px(fx - 1, fy, mk("#d28a6a")[3])
            p.px(fx + 5, fy - 1, mk("#d28a6a")[1])
            p.px(fx + 5, fy + 1, mk("#d28a6a")[1])
    # lit back rim
    for k in range(int(w * 0.5)):
        pass


def fish_vat(state: str) -> Image.Image:
    p = Pix(64, 48, seed=31)
    # side barrel with the pump, drawn first so the tub overlaps it
    sb = box(46, 4, 15, 31)
    part(p, sb, mk("#6a4a30"), 2, grad=0.9)
    for sx in range(48, 60, 4):
        p.vline(sx, 5, 29, mk("#6a4a30")[1])
    for hy in (9, 28):
        p.hline(46, hy, 15, IRON[1])
        p.hline(46, hy + 1, 15, IRON[3])
    part(p, box(46, 2, 15, 3), mk("#9c6b3a"), 3, grad=0.6)
    pipe = tube([(53, 14, 1.8), (53, 8, 1.8), (53, 3, 1.4)])
    part(p, pipe, IRONR, 2, grad=0.6)
    part(p, box(50, 18, 7, 3), BRASSR, 2, grad=0.5)
    # pipe from the side barrel into the tub
    part(p, box(40, 20, 8, 3), IRONR, 2, grad=0.6)
    part(p, box(44, 18, 3, 7), BRASSR, 2, grad=0.5)
    # the little wine-red cask lying at the foot
    cask = box(38, 35, 24, 11) | ell(49.5, 34, 11, 3) | ell(49.5, 45, 12, 2)
    cask = {(a, b) for a, b in cask if 36 <= b <= 47}
    part(p, cask, WINER, 2, grad=1.0)
    for sx in (41, 48, 56):
        p.vline(sx, 37, 9, WINER[0])
        p.vline(sx + 1, 37, 9, WINER[3])
    p.hline(38, 39, 24, WINER[1])
    p.px(61, 41, BRASS[3]), p.px(39, 41, BRASS[3])
    stave_tub(p, 1, 8, 44, 38, 9, None if state == "empty" else "water", 3 if state == "full" else 0)
    return p.im


def fish_crate() -> Image.Image:
    p = Pix(48, 48, seed=33)
    top = poly([(4, 12), (9, 2), (38, 2), (41, 12)])
    part(p, top, mk("#8c6840"), 2, grad=0.8)
    for x in (13, 20, 27, 34):
        p.line(x - 3, 11, x, 3, mk("#8c6840")[1])
    front = box(4, 12, 38, 35)
    part(p, front, WOOD, 2, grad=0.8)
    # slats: a grid of dark openings between the oak bars
    for gy in range(18, 44, 7):
        for gx in range(8, 38, 6):
            part(p, box(gx, gy, 5, 5), mk("#1a0f0a"), 1, outline=None, grad=0.3)
            p.px(gx, gy, WOOD[3])
    p.hline(4, 14, 38, WOOD[4])
    for x in (4, 40):
        p.vline(x, 12, 35, IRON[2])
        p.vline(x + 1 if x < 10 else x - 1, 12, 35, IRON[3])
    for y in (13, 45):
        p.hline(4, y, 38, IRON[2])
    lock = ell(22, 9, 3, 3)
    part(p, lock, BRASSR, 2, grad=0.8)
    p.px(22, 9, SHADOW), p.px(22, 10, SHADOW)
    for x, y in ((6, 15), (38, 15), (6, 43), (38, 43)):
        p.px(x, y, BRASS[4])
    edge(p, top | front)
    return p.im


# ---------------------------------------------------------------------- the list

PICS: dict = {
    "caviar": caviar,
    "fish_food": lambda: heap(28, 27, mk("#7a5030"), seed=2, round_pellets=True),
    "fish_food2": lambda: heap(28, 27, mk("#aaa89a"), seed=3, round_pellets=True),
    "items_aquaculture_1": lambda: heap(28, 27, mk("#3a3640"), seed=4, round_pellets=True),
    "fishscrap": scrap_bones,
    "fries": silver_pile,
    "meat_eel_small": lambda: steak_eel(24, 16),
    "meat_eel_tiny": lambda: steak_eel(14, 12),
    "ras": lambda: fish_vat("water"),
    "ras_empty": lambda: fish_vat("empty"),
    "ras_full": lambda: fish_vat("full"),
    "ras_tank": fish_crate,
    "sturgeon": sturgeon,
    "eel1": lambda: eel(64, 32, 1), "eel2": lambda: eel(64, 32, 2),
    "eel_large1": lambda: eel(80, 32, 1), "eel_large2": lambda: eel(80, 32, 2),
    "eel_small1": lambda: eel(48, 32, 1), "eel_small2": lambda: eel(48, 32, 2),
}
for _k in range(1, 5):
    PICS[f"meat_fish{_k}"] = lambda k=_k: fillet(30, 20, k)
    PICS[f"meat_fish_large{_k}"] = lambda k=_k: fillet(43, 23, k)
    PICS[f"meat_fish_small{_k}"] = lambda k=_k: fillet(27, 14, k)
    PICS[f"meat_fish_tiny{_k}"] = lambda k=_k: fillet_tiny(k)
for _k in (1, 2, 3):
    PICS[f"tilapia{_k}"] = lambda k=_k: tilapia("m", k)
    PICS[f"tilapia_large{_k}"] = lambda k=_k: tilapia("l", k)
    PICS[f"tilapia_small{_k}"] = lambda k=_k: tilapia("s", k)
for _n in EGG:
    PICS[_n] = lambda n=_n: roe(n)
