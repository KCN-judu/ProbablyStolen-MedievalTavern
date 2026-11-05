"""Food and drink sprites: cheese, stews, pies, meat cuts, sausages, flasks, jugs and waterskins."""

from __future__ import annotations

import math

from PIL import Image

from itemkit_farm import (
    BONE, BRASSR, BROWN, CLAY, CREAM, IRONR, LEAF, LEAF_DK, LINEN_R, OAKR, PALER, PEWTER, PINK, RED, SOIL, STRAW, TEAL, WINER, Shape,
    box, edge, ell, flat, line_set, mk, only, part, poly, rim, shade, stroke, tube,
)
from items_farm_wine import CORK, INK, PARCH, bottle
from palette import BRASS, GLASS, IRON, SHADOW, WOOD
from pix import Pix, mix, rgb

MEAT = mk("#b0383a")
FAT = mk("#e8d8c8")


# ---------------------------------------------------------------------- bread-and-board food

def cheese() -> Image.Image:
    p = Pix(32, 32, seed=2)
    ch = mk("#e6b84a")
    rind = mk("#b8782c")
    top = poly([(14, 3), (3, 16), (27, 14)])
    front = poly([(3, 16), (27, 14), (27, 24), (3, 26)])
    part(p, front, rind, 2, grad=0.8)
    # the cut face: cream, with holes
    cut = poly([(4, 17), (26, 15), (26, 22), (4, 24)])
    part(p, cut, ch, 2, outline=None, grad=0.7)
    for x, y, r in ((9, 19, 1.8), (17, 18, 1.5), (22, 20, 1.3), (13, 22, 1.2)):
        hole = ell(x, y, r + 0.6, r)
        flat(p, hole, ch[0])
        p.hline(round(x - r), round(y + r), int(2 * r), ch[4])
    part(p, top, ch, 3, grad=1.0)
    for x, y in ((12, 11), (17, 13), (9, 15), (20, 15), (14, 8)):
        p.px(x, y, ch[0])
        p.px(x - 1, y - 1, ch[4])
    # rind edge on top of the wedge and on the sides
    for x, y in line_set(14, 3, 27, 14) | line_set(14, 3, 3, 16) | line_set(3, 16, 27, 14):
        p.px(x, y, rind[2])
    edge(p, top | front)
    p.px(5, 25, rind[1]), p.hline(5, 25, 20, rind[1])
    p.hline(4, 17, 6, ch[4])
    return p.im


def stew_bowl() -> Image.Image:
    p = Pix(48, 32, seed=3)
    clay = mk("#a8472f")
    bowl = ell(23, 14, 22, 9) | {(x, y) for x, y in ell(23, 14, 22, 15) if y >= 14 and y <= 28}
    bowl = {(x, y) for x, y in bowl if y <= 28}
    part(p, bowl, clay, 2, grad=1.1)
    rimm = ell(23, 12, 22, 7)
    part(p, rimm, mk("#c26a3a"), 3, grad=0.8)
    soup = ell(23, 12, 19, 5)
    sc = mk("#a85a28")
    part(p, soup, sc, 2, outline=clay[0], grad=1.0)
    # bits in the stew
    for x, y, c in ((14, 12, rgb("#e6963a")), (19, 14, LEAF[3]), (26, 11, rgb("#e6963a")), (31, 13, CREAM[3]), (22, 12, rgb("#c25b49")), (17, 10, LEAF[3]), (29, 15, rgb("#e6963a"))):
        p.px(x, y, c)
        p.px(x + 1, y, c)
    p.hline(12, 10, 5, sc[4])
    p.hline(26, 14, 3, sc[4])
    # glaze band and foot
    p.hline(8, 21, 30, clay[1])
    p.hline(10, 22, 27, clay[3] if False else clay[2])
    foot = box(14, 27, 20, 3)
    part(p, foot, clay, 1, grad=0.4)
    # wooden spoon resting on the rim
    spoon = tube([(33, 9, 1.0), (40, 5, 1.0), (45, 3, 0.8)])
    part(p, spoon, PALER, 3, grad=0.4)
    bowl_s = ell(31, 10, 3, 2)
    part(p, bowl_s, PALER, 2, grad=0.6)
    # steam
    for x, y in ((18, 6), (19, 4), (18, 2), (25, 5), (26, 3)):
        p.px(x, y, mk("#d8d0c4")[3])
    return p.im


def crock() -> Image.Image:
    p = Pix(48, 32, seed=4)
    st = mk("#c8b28c")
    body = {(x, y) for x, y in ell(24, 16, 21, 15) if y >= 8 and y <= 30}
    part(p, body, st, 2, grad=1.1)
    band = {(x, y) for x, y in body if 14 <= y <= 18}
    flat(p, band, mk("#4a6e98")[2])
    for x, y in band:
        if (x - 1, y) in band and y == 14:
            p.px(x, y, mk("#4a6e98")[3])
        if y == 18:
            p.px(x, y, mk("#4a6e98")[1])
    for x in range(8, 40, 6):                                # painted dashes in the band
        p.px(x, 16, st[4])
        p.px(x + 1, 16, st[4])
    lip = ell(24, 9, 18, 5)
    part(p, lip, st, 3, grad=0.8)
    butter = ell(24, 9, 15, 3.4)
    part(p, butter, mk("#f0d268"), 3, outline=st[0], grad=0.9)
    p.hline(14, 8, 8, mk("#f0d268")[4])
    for x in range(18, 32, 3):
        p.px(x, 10, mk("#f0d268")[1])
    knife = tube([(30, 8, 0.7), (38, 3, 0.7)])
    part(p, knife, PALER, 3, grad=0.2)
    p.px(39, 2, PALER[3])
    return p.im


def honey_bar() -> Image.Image:
    p = Pix(32, 32, seed=5)
    cake = box(2, 7, 26, 15)
    part(p, cake, mk("#c88a3a"), 2, grad=0.9)
    for x, y in ((6, 11), (11, 15), (16, 10), (21, 14), (8, 19), (14, 18), (24, 19), (19, 17)):
        p.px(x, y, mk("#e8b860")[4])
        p.px(x + 1, y, mk("#8a5420")[2])
    p.hline(3, 8, 24, mk("#e8b860")[3])
    wrap = poly([(11, 6), (29, 6), (30, 24), (11, 24)])
    part(p, wrap, PARCH, 3, grad=0.6)
    p.vline(12, 7, 16, PARCH[4])
    for y in (10, 14, 18):
        p.hline(15, y, 9, PARCH[1])
    p.vline(18, 8, 15, WAX_STRAW) if False else None
    twine_c = mk("#a8302e")
    p.vline(20, 6, 19, twine_c[1])
    p.vline(21, 6, 19, twine_c[3])
    for dx, dy in ((0, 0), (1, 1), (2, 2), (-1, 1), (-2, 2)):
        p.px(21 + dx, 5 + dy, twine_c[3])
    edge(p, cake | wrap)
    return p.im


# ---------------------------------------------------------------------- meats

def steak(w: int, h: int, seed: int, bone: bool = False) -> Image.Image:
    p = Pix(w, h, seed=seed)
    s = ell(w / 2 - 0.5, h / 2 - 0.5, w / 2, h / 2) | poly([(w * 0.1, h * 0.3), (w * 0.35, 0), (w * 0.8, h * 0.05), (w - 1, h * 0.5), (w * 0.8, h - 1), (w * 0.2, h - 1), (0, h * 0.6)])
    s = {(x, y) for x, y in s if 0 <= x < w and 0 <= y < h}
    shade(p, s, MEAT, 2, grad=1.0)
    # fat rim, pale and lit, along the upper-right and down the lower edge
    cols = {}
    for x, y in s:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    rimfat = {(x, y) for x, y in s if y <= cols[x][0] + 1 and x > w * 0.25 or y >= cols[x][1] - 1 and x < w * 0.8}
    rimfat |= {(x, y) for x, y in s if x >= w - 3}
    for x, y in rimfat:
        p.px(x, y, FAT[3] if (x + y) % 3 else FAT[2])
    for x, y in rimfat:
        if (x - 1, y - 1) not in s or (x, y - 1) not in s:
            p.px(x, y, FAT[4])
    # marbling and a glossy highlight
    rng = p.rng
    for _ in range(max(4, w // 4)):
        x, y = rng.randrange(4, w - 5), rng.randrange(4, h - 4)
        for k in range(rng.randrange(2, 4)):
            if (x + k, y + (k + 1) // 2) in s and (x + k, y + (k + 1) // 2) not in rimfat:
                p.px(x + k, y + (k + 1) // 2, MEAT[4] if k % 2 else FAT[1])
    p.hline(int(w * 0.2), int(h * 0.3), max(2, w // 6), MEAT[4])
    if bone:
        b = ell(w * 0.62, h * 0.5, 4, 3.6)
        part(p, b, BONE, 3, outline=MEAT[0], grad=0.8)
        p.px(round(w * 0.62), round(h * 0.5), BONE[0])
    edge(p, s)
    return p.im


def bacon() -> Image.Image:
    p = Pix(32, 32, seed=6)
    slab = poly([(1, 4), (22, 1), (24, 4), (24, 15), (3, 16), (1, 12)])
    s = {(x + 1, y + 4) for x, y in slab}
    for x, y in sorted(s):
        stripe = ((y - 5) // 3) % 2
        c = MEAT if stripe == 0 else mk("#efdccc")
        lo = (y - 5) % 3
        p.px(x, y, c[3] if lo == 0 else c[2] if lo == 1 else c[1])
    # rind along the underside
    for x, y in s:
        if (x, y + 1) not in s or (x + 1, y) not in s:
            p.px(x, y, mk("#a06a38")[2])
    # lit top-left rim
    for x, y in s:
        if (x - 1, y) not in s or (x, y - 1) not in s:
            p.px(x, y, FAT[4])
    edge(p, s)
    return p.im


def morsel(w: int, h: int, seed: int) -> Image.Image:
    p = Pix(w, h, seed=seed)
    s = ell(w / 2 - 0.5, h / 2 - 0.5, w / 2, h / 2) | ell(w * 0.62, h * 0.45, w * 0.35, h * 0.5)
    s = {(x, y) for x, y in s if 0 <= x < w and 0 <= y < h}
    shade(p, s, mk("#b8503e"), 2, grad=1.0)
    cols = {}
    for x, y in s:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    for x in range(2, w - 3, 3):
        if x in cols:
            p.px(x, cols[x][0] + 1, FAT[3])
            p.px(x + 1, cols[x][0] + 1, FAT[4]) if w > 14 else None
    p.px(w // 2, h // 2, mk("#b8503e")[4])
    edge(p, s)
    return p.im


def scrap_pile() -> Image.Image:
    p = Pix(32, 32, seed=7)
    lumps = [(9, 23, 6, 3.4, MEAT), (22, 22, 7, 3.4, mk("#8a2c34")), (15, 17, 5.5, 3.2, mk("#c2504a")), (24, 15, 4.5, 3, MEAT), (7, 15, 4, 2.6, mk("#8a2c34")), (16, 11, 3.5, 2.4, mk("#a8403a"))]
    for x, y, rx, ry, ramp in sorted(lumps, key=lambda a: a[1]):
        part(p, ell(x, y, rx, ry), ramp, 2, grad=0.9)
        p.px(round(x - rx * 0.4), round(y - ry * 0.4), ramp[4])
        p.px(round(x + rx * 0.3), round(y + 0.2), FAT[3])
        p.px(round(x - 1), round(y + 1), FAT[2])
    return p.im


def sausage() -> Image.Image:
    p = Pix(48, 16, seed=8)
    pts = [(4, 8, 4.0), (14, 6.5, 4.4), (24, 7, 4.5), (34, 8, 4.4), (43, 8, 3.8)]
    s = tube(pts)
    link = mk("#a8503a")
    part(p, s, link, 2, grad=1.2)
    for x in range(5, 44, 3):
        p.px(x, 4 + round(2 - abs(x - 24) * 0.04), link[4])
    for x in (13, 24, 34):                                    # twine between the links
        for y in range(2, 14):
            if (x, y) in s:
                p.px(x, y, STRAW[1])
                p.px(x + 1, y, STRAW[3])
    for x, y in ((8, 9), (19, 10), (29, 10), (39, 10)):
        p.px(x, y, link[0])
        p.px(x + 1, y, link[1])
    for x, y in ((9, 6), (18, 5), (28, 6), (38, 6)):
        p.px(x, y, FAT[3])
    edge(p, s)
    return p.im


def roast_ribs() -> Image.Image:
    p = Pix(48, 32, seed=9)
    board = ell(23.5, 18, 23.5, 10)
    part(p, board, mk("#9c7048"), 2, grad=0.9)
    inner = ell(23.5, 17, 20, 7.5)
    part(p, inner, mk("#7a5030"), 2, outline=None, grad=0.5)
    rack = ell(23.5, 15, 18, 7.5)
    rb = mk("#b8602c")
    part(p, rack, rb, 2, grad=1.1)
    cols = {}
    for x, y in rack:
        lo, hi = cols.get(x, (y, y))
        cols[x] = (min(lo, y), max(hi, y))
    for x in range(9, 39, 4):                                  # rib furrows, with the bone ends sticking out below
        lo, hi = cols[x]
        for y in range(lo + 2, hi):
            p.px(x, y, rb[4] if y % 2 else rb[3])
            p.px(x + 1, y, rb[0])
        for k in range(1, 4):
            p.px(x, hi + k, BONE[3] if k < 3 else BONE[1])
            p.px(x + 1, hi + k, BONE[2] if k < 3 else BONE[0])
        p.px(x - 1, hi + 2, BONE[4])
    p.hline(10, 11, 24, rb[4])
    for x in range(12, 36, 5):
        p.px(x, 14, rb[0])
        p.px(x + 2, 17, rb[0])
    sprig = tube([(30, 7, 0.6), (36, 5, 0.6)])
    part(p, sprig, LEAF, 2, grad=0.3, outline=None)
    for x, y in ((31, 6), (33, 5), (35, 4), (32, 8), (35, 7)):
        p.px(x, y, LEAF[3])
    edge(p, board | rack)
    return p.im


def pie() -> Image.Image:
    p = Pix(32, 32, seed=10)
    crust = mk("#c8873c")
    side = {(x, y) for x, y in ell(15.5, 23, 13, 7) if y >= 15} | box(3, 15, 25, 9)
    side = {(x, y) for x, y in side if y <= 29}
    part(p, side, mk("#a86a2e"), 2, grad=1.0)
    for x in range(4, 28, 3):                                  # fluted edge
        p.px(x, 20, crust[3])
        p.px(x + 1, 21, crust[1])
    top = ell(15.5, 13.5, 13, 10)
    part(p, top, crust, 2, grad=1.2)
    for a in range(0, 360, 20):                                # crimped rim
        x = round(15.5 + math.cos(math.radians(a)) * 12.2)
        y = round(13.5 + math.sin(math.radians(a)) * 9.2)
        p.px(x, y, crust[4] if a % 40 == 0 else crust[1])
    lid = ell(15.5, 13, 10, 7)
    part(p, lid, crust, 3, outline=crust[1], grad=1.0)
    # slit and a pastry leaf
    for k in range(5):
        p.px(11 + k, 13 + (k % 2), crust[0])
        p.px(18, 10 + k, crust[0]) if k < 3 else None
    leaf_s = ell(21, 12, 3, 1.4)
    flat(p, leaf_s, crust[4])
    p.px(21, 12, crust[2])
    p.px(12, 10, crust[4]), p.px(13, 9, crust[4])
    p.hline(5, 22, 4, crust[4])
    edge(p, side | top)
    return p.im


def hardtack() -> Image.Image:
    return ration(22, 28)


def ration(w: int, h: int) -> Image.Image:
    cw, ch = (32, 32) if h > 25 and w > 16 else (16, 32)
    p = Pix(cw, ch, seed=11)
    ox, oy = (cw - w) // 2 + 1, (ch - h) // 2 + 1
    w -= 2
    h -= 2
    pk = box(ox, oy, w, h)
    part(p, pk, LINEN_R, 3, grad=0.9)
    # stitched seam and the rain-drop mark
    p.vline(ox + 1, oy + 2, h - 4, LINEN_R[4])
    for y in range(oy + 2, oy + h - 2, 3):
        p.px(ox + w - 3, y, LINEN_R[1])
    d = ell(ox + w / 2 - 0.5, oy + h * 0.35, w * 0.17, w * 0.2) | poly([(ox + w / 2 - 0.5, oy + h * 0.12), (ox + w / 2 + w * 0.15, oy + h * 0.32), (ox + w / 2 - w * 0.18, oy + h * 0.32)])
    part(p, d, mk("#3e8a86"), 2, outline=None, grad=0.8)
    p.px(round(ox + w / 2 - 1.5), round(oy + h * 0.38), mk("#3e8a86")[4])
    for k in range(3):
        p.hline(ox + 3, oy + round(h * 0.6) + k * 3, w - 6 - (k == 2) * 3, INK[2] if k % 2 == 0 else LINEN_R[1])
    # twine round the neck
    p.hline(ox, oy + 2, w, STRAW[2])
    p.hline(ox, oy + 3, w, STRAW[1])
    edge(p, pk)
    for x in range(ox, ox + w, 2):
        p.px(x, oy - 1, SHADOW) if False else None
    return p.im


# ---------------------------------------------------------------------- drinks

def flagon(ale: bool) -> Image.Image:
    p = bottle(16, 64, 6 if ale else 4, 60, 7.5, mk("#4a3028"), mk("#8a4a1c") if ale else None, 22 if ale else None, cork=ale, neck_hw=3, neck_len=11, shoulder_len=9)
    if ale:
        lab = box(3, 34, 10, 14)
        part(p, lab, PARCH, 3, grad=0.4, outline=INK[0])
        p.hline(3, 34, 10, mk("#a8302e")[3])
        for dx, dy in ((0, 0), (1, 1), (2, 2), (3, 1), (4, 0), (2, 3), (2, 4), (3, 5), (1, 5)):
            p.px(5 + dx, 38 + dy, INK[1])
        p.hline(4, 45, 8, mk("#a8302e")[2])
        p.px(8, 22, mk("#f0c870")[4]) if False else None
    return p.im


def water_flask() -> Image.Image:
    p = bottle(16, 64, 6, 61, 6.5, GLASS, mk("#5ab0b8"), 20, cork=True, neck_hw=3, neck_len=8, shoulder_len=7)
    for x, y in ((6, 28), (9, 36), (7, 44), (10, 50), (6, 54), (8, 24)):
        p.px(x, y, mk("#5ab0b8")[4])
        p.px(x + 1, y + 1, mk("#5ab0b8")[1])
    return p.im


def spirits() -> Image.Image:
    p = bottle(32, 64, 5, 60, 8.5, mk("#9bb0b8"), mk("#cfe4e8"), 24, seal=mk("#7a4a8c"), neck_hw=3.5, neck_len=12, shoulder_len=11)
    lab = box(11, 34, 10, 15)
    part(p, lab, PARCH, 3, grad=0.4, outline=INK[0])
    p.hline(11, 34, 10, mk("#7a4a8c")[3])
    p.hline(11, 48, 10, mk("#7a4a8c")[1])
    ring = ell(15.5, 40, 3.5, 3.5) - ell(15.5, 40, 1.6, 1.6)
    flat(p, ring, mk("#7a4a8c")[2])
    p.hline(12, 45, 8, INK[2])
    return p.im


def tankard() -> Image.Image:
    p = Pix(16, 32, seed=12)
    body = box(1, 6, 10, 24) | ell(5.5, 29, 5, 2)
    part(p, body, mk("#7a4e2a"), 2, grad=1.0)
    for x in (3, 6, 9):
        p.vline(x, 8, 20, mk("#7a4e2a")[1])
    for y in (10, 25):
        p.hline(1, y, 10, IRON[1])
        p.hline(1, y + 1, 10, IRON[3])
    handle = tube([(11, 11, 0.9), (14, 13, 0.9), (14, 22, 0.9), (11, 24, 0.9)])
    part(p, handle, IRON, 2, grad=0.4)
    foam = ell(5.5, 6, 6, 3.4)
    part(p, foam, CREAM, 3, grad=0.8)
    for x, y in ((3, 4), (6, 3), (8, 6)):
        part(p, ell(x, y, 1.6, 1.6), CREAM, 4, outline=None, grad=0.3)
    amber = mk("#d49a3c")
    p.hline(2, 8, 8, amber[3])
    p.vline(2, 12, 12, mk("#9c6b3a")[4])
    return p.im


def red_jug() -> Image.Image:
    p = Pix(16, 32, seed=13)
    jar = box(1, 15, 12, 14) | ell(6.5, 29, 6, 2) | ell(6.5, 15, 6, 3)
    part(p, jar, mk("#a8372e"), 2, grad=1.1)
    neck = box(4, 9, 6, 7)
    part(p, neck, mk("#a8372e"), 2, grad=0.7)
    p.hline(3, 10, 8, mk("#a8372e")[3])
    handle = tube([(11, 12, 0.9), (14, 15, 0.9), (14, 21, 0.9), (11, 24, 0.9)])
    part(p, handle, mk("#a8372e"), 2, grad=0.5)
    cork = box(4, 6, 6, 4)
    part(p, cork, CORK, 2, grad=0.8)
    p.px(7, 8, CORK[1])
    p.vline(3, 17, 9, mk("#a8372e")[4])
    for x, y in ((6, 19), (7, 20), (8, 21), (7, 22), (6, 23)):          # a painted drop
        p.px(x, y, mk("#f0c870")[3])
    return p.im


def small_bottle() -> Image.Image:
    p = bottle(16, 48, 7, 44, 5.5, mk("#4a3028"), mk("#c23a22"), 18, cork=True, neck_hw=2.5, neck_len=6, shoulder_len=6)
    lab = box(3, 24, 10, 13)
    part(p, lab, PARCH, 3, grad=0.4, outline=INK[0])
    p.hline(3, 24, 10, mk("#c23a22")[2])
    # a chilli on the label
    ch = tube([(5, 29, 1.0), (8, 31, 0.9), (11, 34, 0.5)])
    part(p, ch, mk("#c23a22"), 2, grad=0.5, outline=None)
    p.px(5, 28, LEAF[3]), p.px(4, 28, LEAF[2])
    p.hline(5, 35, 6, INK[2])
    return p.im


def cider_keg() -> Image.Image:
    p = Pix(32, 48, seed=14)
    body = box(3, 6, 26, 36) | ell(15.5, 6, 13, 3) | ell(15.5, 41, 13, 3)
    body = {(x, y) for x, y in body if y >= 3 and y <= 44}
    # a keg bulges slightly: narrow the top and bottom rows
    body = {(x, y) for x, y in body if not ((y <= 5 or y >= 42) and (x < 5 or x > 26))}
    part(p, body, mk("#7a4e2a"), 2, grad=1.0)
    for x in range(8, 28, 6):
        p.vline(x, 8, 34, mk("#7a4e2a")[1])
        p.vline(x + 1, 8, 34, mk("#7a4e2a")[3])
    for y in (9, 36):
        p.hline(3, y, 26, IRON[1])
        p.hline(3, y + 1, 26, IRON[3])
        for x in (6, 14, 22):
            p.px(x, y + 1, BRASS[3])
    topd = ell(15.5, 5, 12, 2.5)
    part(p, topd, mk("#9c6b3a"), 3, grad=0.8)
    # painted apple roundel
    roundel = ell(15.5, 23, 8, 8)
    part(p, roundel, mk("#d9c9a0"), 3, outline=SHADOW, grad=0.5)
    apple = ell(15.5, 24, 4.5, 4.5)
    part(p, apple, mk("#c23a2e"), 2, outline=None, grad=1.0)
    p.px(13, 22, mk("#c23a2e")[4])
    p.vline(16, 18, 2, BROWN[2])
    p.px(17, 19, LEAF[3]), p.px(18, 19, LEAF[2])
    tap = box(13, 40, 5, 3)
    part(p, tap, BRASSR, 2, grad=0.5)
    edge(p, body)
    return p.im


def milk_jug() -> Image.Image:
    p = Pix(32, 48, seed=15)
    body = box(4, 14, 24, 28) | ell(15.5, 14, 12, 4) | ell(15.5, 41, 12, 3)
    part(p, body, mk("#e4dcc8"), 2, grad=1.0)
    neck = box(10, 6, 12, 10)
    part(p, neck, mk("#e4dcc8"), 2, grad=0.7)
    p.hline(9, 8, 14, mk("#e4dcc8")[1])
    cork = box(11, 3, 10, 5)
    part(p, cork, CORK, 2, grad=0.8)
    # dappled patches (the dairy cow) and a blue band
    for cx, cy, rx, ry in ((11, 24, 4, 3), (20, 31, 5, 3.4), (22, 19, 2.6, 2)):
        patch = ell(cx, cy, rx, ry) & body
        flat(p, patch, mk("#6a5a58")[2])
        for x, y in patch:
            if (x - 1, y) not in patch or (x, y - 1) not in patch:
                p.px(x, y, mk("#6a5a58")[3])
    p.hline(5, 38, 22, mk("#4a6e98")[2])
    p.hline(5, 39, 22, mk("#4a6e98")[1])
    handle = tube([(28, 18, 1.0), (31, 22, 1.0), (31, 32, 1.0), (28, 36, 1.0)])
    part(p, handle, mk("#e4dcc8"), 2, grad=0.5)
    edge(p, body | neck)
    return p.im


def waterskin() -> Image.Image:
    p = Pix(32, 32, seed=16)
    skin = mk("#8a5a30")
    body = ell(15.5, 20, 10.5, 10) | poly([(11, 11), (20, 11), (21, 18), (10, 18)])
    part(p, body, skin, 2, grad=1.1)
    neck = box(12, 6, 7, 6)
    part(p, neck, skin, 2, grad=0.8)
    p.hline(11, 9, 9, mk("#3a2418")[2])
    p.hline(11, 10, 9, STRAW[2])
    stopper = box(13, 2, 5, 5)
    part(p, stopper, PALER, 2, grad=0.8)
    # seam stitching around the edge and a strap
    for a in range(30, 330, 20):
        x = round(15.5 + math.cos(math.radians(a)) * 8.2)
        y = round(20 + math.sin(math.radians(a)) * 7.8)
        if (x, y) in body:
            p.px(x, y, skin[4] if a % 40 else skin[0])
    strap = tube([(19, 9, 0.9), (26, 6, 0.9), (27, 14, 0.9), (22, 24, 0.9)])
    part(p, strap, mk("#4a2b1a"), 2, grad=0.3)
    for k in range(4):
        p.px(14 + k, 16 + k // 2, skin[3])
    p.px(12, 14, skin[4]), p.px(11, 17, skin[4])
    edge(p, body | neck)
    return p.im


# ---------------------------------------------------------------------- the list

PICS: dict = {
    "beis_icecream": crock,
    "cat_bar": honey_bar,
    "cheese": cheese,
    "cup_noodle": stew_bowl,
    "empty_beer_bottle": lambda: flagon(False),
    "energy_drink": tankard,
    "fat_meat": bacon,
    "hot_sauce": small_bottle,
    "items_food_juice": cider_keg,
    "items_food_pilk_alt": milk_jug,
    "items_food_soda_red": red_jug,
    "juice_pouch": waterskin,
    "li_eat_snackbar": sausage,
    "meat_scrap": scrap_pile,
    "morsel": lambda: morsel(24, 11, 1),
    "morsel_small": lambda: morsel(11, 12, 2),
    "nudka": spirits,
    "processed_meat": pie,
    "raw_meat": lambda: steak(38, 28, 3, True),
    "red_beer": lambda: flagon(True),
    "ribwich": roast_ribs,
    "small_raw_meat": lambda: steak(22, 20, 4),
    "water_bottle_full_premium": water_flask,
    "water_ration": lambda: ration(22, 28),
    "water_ration_small": lambda: ration(15, 25),
}
