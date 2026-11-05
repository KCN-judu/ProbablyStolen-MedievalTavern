"""Winemaking sprites: glass bottles (also used by the food drinks), labels and seals, yeast pots, the rack, grapes."""

from __future__ import annotations

import math

from PIL import Image

from itemkit_farm import (
    BONE, BRASSR, BROWN, CREAM, IRONR, LEAF, LEAF_DK, LINEN_R, OAKR, PALER, PURPLE, SOIL, STRAW, WINER, WAX_RED, Shape, box, edge,
    ell, flat, line_set, mk, part, poly, shade, stroke, tube,
)
from items_farm_plants import grapes, leaf
from palette import BRASS, GLASS, IRON, SHADOW, WOOD
from pix import Pix, mix, rgb

CORK = mk("#c49a64")


def bottle_shape(w: int, top: int, bottom: int, body_hw: float, neck_hw: float, neck_len: int, shoulder_len: int) -> tuple[Shape, dict[int, tuple[int, int]], int, int]:
    """A glass bottle profile centred in a canvas `w` wide. Returns the shape, the x span per row, and the rows where the shoulder starts and ends."""
    cx = w / 2
    s: Shape = set()
    rows: dict[int, tuple[int, int]] = {}
    sh0 = top + 2 + neck_len
    sh1 = sh0 + shoulder_len
    for y in range(top, bottom + 1):
        if y < top + 2:
            hw = neck_hw + 1
        elif y < sh0:
            hw = neck_hw + (0.5 if y > sh0 - 3 else 0)
        elif y < sh1:
            t = (y - sh0 + 0.5) / shoulder_len
            hw = neck_hw + (body_hw - neck_hw) * math.sin(t * math.pi / 2) ** 1.4
        else:
            hw = body_hw
        if y == bottom:
            hw -= 2
        elif y == bottom - 1:
            hw -= 1
        x0, x1 = round(cx - hw), round(cx + hw) - 1
        rows[y] = (x0, x1)
        for x in range(x0, x1 + 1):
            s.add((x, y))
    return s, rows, sh0, sh1


def bottle(w: int, h: int, top: int, bottom: int, body_hw: float, glass, liquid=None, level: int | None = None, seal=None, cork: bool = False,
           neck_hw: float = 3.0, neck_len: int = 9, shoulder_len: int = 9) -> Pix:
    p = Pix(w, h, seed=7)
    s, rows, sh0, sh1 = bottle_shape(w, top, bottom, body_hw, neck_hw, neck_len, shoulder_len)
    for x, y in s:
        x0, x1 = rows[y]
        u = (x - x0 + 0.5) / (x1 - x0 + 1)
        inside = liquid is not None and level is not None and y >= level
        ramp = liquid if inside else glass
        i = 3 if u < 0.2 else 2 if u < 0.45 else 1 if u < 0.8 else 0
        if inside and u < 0.2:
            i = 3
        if y >= bottom - 2 or y < top + 2:
            i = max(0, i - 1)
        p.px(x, y, ramp[i])
    # meniscus and a surface sheen
    if liquid is not None and level is not None:
        x0, x1 = rows[level]
        p.hline(x0 + 1, level, x1 - x0 - 1, liquid[4] if level > sh1 else liquid[3])
        p.hline(x0 + 1, level + 1, max(0, x1 - x0 - 2), liquid[2])
    # the glint down the left flank, with a dot above it
    gx = rows[sh1 + 2][0] + 2
    for y in range(sh1 + 2, bottom - 5):
        p.px(gx, y, (GLASS[4] if liquid is None else mix(liquid[4], (255, 255, 255), 0.25)))
    p.px(gx, bottom - 3, GLASS[3] if liquid is None else liquid[4])
    # shoulder light
    x0, _ = rows[sh1 - 3]
    for dy in range(3):
        p.px(x0 + 1, sh1 - 3 + dy, GLASS[4] if liquid is None else liquid[4])
    # base: the punt shows as a lit rim
    x0, x1 = rows[bottom]
    p.hline(x0 + 1, bottom, x1 - x0 - 1, glass[0])
    # lip ring
    lx0, lx1 = rows[top]
    p.hline(lx0, top, lx1 - lx0 + 1, glass[3])
    p.hline(lx0, top + 1, lx1 - lx0 + 1, glass[1])
    edge(p, s)
    if seal is not None:                                               # wax over the cork, dripping down the neck
        cap = box(lx0 - 0, top - 1, lx1 - lx0 + 1, neck_len // 2 + 3)
        cap |= {(lx0 + 1, top + neck_len // 2 + 3), (lx1 - 1, top + neck_len // 2 + 4)}
        part(p, {(x, y) for x, y in cap if (x, y) in s or y < top + 2}, seal, 2, grad=0.8)
        for x, y in ((lx0 + 1, top + neck_len // 2 + 3), (lx1 - 1, top + neck_len // 2 + 4)):
            p.px(x, y, seal[2])
        p.px(lx0 + 1, top, seal[4])
    elif cork:
        cap = box(lx0 + 1, top - 2, lx1 - lx0 - 1, 5)
        part(p, cap, CORK, 2, grad=0.8)
        p.px(lx0 + 2, top, CORK[1])
        p.px(lx1 - 2, top - 1, CORK[1])
    else:                                                              # open mouth: a dark ring
        p.hline(lx0 + 1, top, lx1 - lx0 - 1, SHADOW)
    return p


WINES = [mk("#3a1a2e"), mk("#4a1a24"), mk("#5c1a20"), mk("#7a1f26"), mk("#a02a30"), mk("#c43c3a")]
GLASS_BROWN = mk("#4a3028")


def wine_bottle_n(i: int) -> Image.Image:
    liq = WINES[i]
    return bottle(16, 64, 5, 62, 8, GLASS_BROWN, liq, 19 if i < 5 else 18, seal=mk("#7a1f26") if i % 2 == 0 else mk("#2a2a32"), neck_hw=3).im


def wine_empty() -> Image.Image:
    return bottle(16, 64, 4, 62, 8, GLASS_BROWN, None, None, cork=False, neck_hw=3).im


def wine_fermenting() -> Image.Image:
    p = bottle(16, 64, 8, 63, 8, GLASS_BROWN, mk("#6a3a8a"), 24, neck_hw=3)
    # bung and airlock reaching out of the top
    bung = box(5, 4, 6, 5)
    part(p, bung, CORK, 2, grad=0.8)
    tube_ = tube([(8, 4, 1.0), (8, 1, 1.0), (12, 0.8, 1.0), (13, 3, 1.0)])
    part(p, tube_, mk("#9aa5a5"), 3, grad=0.5)
    # bubbles rising in the must
    for x, y in ((6, 40), (10, 34), (7, 28), (11, 46), (5, 52)):
        p.px(x, y, mk("#6a3a8a")[4])
        p.px(x + 1, y + 1, mk("#6a3a8a")[1])
    return p.im


def wine_bottom() -> Image.Image:
    p = Pix(10, 8, seed=1)
    ring = ell(4.5, 3.5, 5, 4)
    part(p, ring, mk("#7a2c36"), 2, grad=0.8)
    core = ell(4.5, 3.8, 2.6, 2.0)
    part(p, core, mk("#2a1218"), 1, outline=None, grad=0.2)
    p.px(2, 2, mk("#7a2c36")[4])
    p.px(6, 4, mk("#7a2c36")[3])
    return p.im


# ---------------------------------------------------------------------- labels

PARCH = mk("#dccb9e")
INK = mk("#4a3a28")


def label_card(p: Pix, x: int, y: int, w: int, h: int, band) -> Shape:
    s = box(x, y, w, h)
    part(p, s, PARCH, 3, grad=0.5, outline=None)
    p.hline(x, y, w, band[3])
    p.hline(x, y + h - 1, w, band[1])
    p.vline(x, y + 1, h - 2, band[3])
    p.vline(x + w - 1, y + 1, h - 2, band[1])
    return s


def text_lines(p: Pix, x: int, y: int, n: int, w: int, c) -> None:
    for k in range(n):
        l = w - (k % 2) * 3
        for i in range(0, l, 2):
            p.px(x + i, y + k * 3, c)
            if (i + k) % 3:
                p.px(x + i + 1, y + k * 3, c)


def label_pic(kind: str) -> Image.Image:
    p = Pix(16, 64, seed=1)
    if kind in ("0", "1", "red"):
        band = {"0": mk("#c2b48a"), "1": mk("#c2b48a"), "red": mk("#a8302e")}[kind]
        s = label_card(p, 2, 40, 12, 12, band)
        if kind == "0":                                      # a red cross: spoiled
            for k in range(7):
                p.px(4 + k, 42 + k, WAX_RED[2])
                p.px(10 - k, 42 + k, WAX_RED[2])
                p.px(5 + k, 42 + k, WAX_RED[3]) if k < 6 else None
        elif kind == "1":                                    # hasty scrawl
            text_lines(p, 4, 43, 3, 8, INK[2])
            p.px(10, 49, INK[1])
        else:                                                # skull: poison
            for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (-1, 2), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
                           (0, 3), (1, 3), (2, 3), (3, 3), (1, 4), (2, 4)):
                p.px(6 + dx, 42 + dy, INK[0])
            for dx, dy in ((0, 2), (3, 2)):
                p.px(6 + dx, 42 + dy, PARCH[3])
            p.px(1 + 6, 45, PARCH[3]) if False else None
            for dx in (0, 1, 2, 3):
                p.px(6 + dx, 45 + 1, INK[0]) if dx % 2 == 0 else p.px(6 + dx, 46, PARCH[2])
            for k in range(5):
                p.px(4 + k * 1, 48 + (k % 2), INK[1]) if False else None
            p.hline(4, 49, 8, INK[1])
            p.px(5, 48, INK[1]), p.px(10, 48, INK[1])
    elif kind == "2":
        s = label_card(p, 2, 38, 12, 16, LEAF)
        text_lines(p, 4, 41, 3, 8, INK[2])
        p.hline(4, 50, 8, LEAF[2])
        p.px(7, 51, LEAF[3]), p.px(8, 51, LEAF[3])
    else:
        col = {"3": mk("#b03030"), "4": mk("#a050b8"), "5": mk("#d8942c")}[kind]
        s = label_card(p, 2, 38, 12, 16, col)
        if kind == "3":
            for y in (43, 46, 49):
                p.hline(5, y, 6, INK[2])
        elif kind == "4":                                    # a small cluster of grapes
            for x, y in ((6, 43), (8, 43), (10, 43), (7, 45), (9, 45), (8, 47)):
                p.px(x, y, col[2])
                p.px(x, y - 1, col[3]) if False else None
            p.px(8, 41, LEAF[2])
            p.hline(5, 50, 6, INK[2])
        else:                                                # a sun
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                p.px(8 + dx, 45 + dy, col[2] if abs(dx) + abs(dy) < 2 else col[3])
            for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
                p.px(8 + dx, 45 + dy, col[1])
            p.hline(5, 50, 6, INK[2])
        # the wax seal and the ribbon at the neck
        seal = mk({"3": "#a8302e", "4": "#8a3aa0", "5": "#d4a030"}[kind])
        cap = ell(5.5, 6.5, 3, 2.5) | box(3, 4, 6, 3)
        part(p, cap, seal, 2, grad=0.9)
        p.px(4, 5, seal[4])
        p.vline(5, 8, 4, INK[1])
        rib = box(3, 12, 6, 7)
        part(p, rib, col, 2, grad=0.8)
        p.px(4, 13, col[4])
        p.hline(3, 15, 6, col[1])
    return p.im


# ---------------------------------------------------------------------- yeast pots

def yeast_pot(glaze, label_band, mark: str, w: int = 16, h: int = 32) -> Image.Image:
    p = Pix(w, h, seed=3)
    body = box(2, 12, 12, 16) | ell(7.5, 28, 6, 2)
    body = {(x, y) for x, y in body if y <= 28 or True}
    part(p, body, glaze, 2, grad=1.0)
    p.hline(2, 13, 12, glaze[1])
    # linen cloth tied over the mouth with twine
    cloth = ell(7.5, 9, 6, 3.5) | box(4, 9, 8, 3)
    part(p, cloth, LINEN_R, 3, grad=0.7)
    for x in range(4, 12, 3):
        p.vline(x, 6, 5, LINEN_R[2])
    p.hline(3, 11, 10, STRAW[1])
    p.hline(3, 12, 10, STRAW[3] if False else STRAW[2])
    p.px(11, 12, STRAW[3]), p.px(12, 13, STRAW[1])
    # label
    lab = box(4, 16, 8, 8)
    part(p, lab, PARCH, 3, grad=0.3, outline=INK[0])
    p.hline(4, 16, 8, label_band[3])
    if mark == "dot":
        for x, y in ((6, 19), (7, 19), (8, 19), (6, 20), (9, 20), (7, 21), (8, 21)):
            p.px(x, y, INK[2])
    elif mark == "star":
        for x, y in ((8, 18), (7, 19), (8, 19), (9, 19), (8, 20), (6, 20), (10, 20), (7, 21), (9, 21)):
            p.px(x, y, label_band[2])
    else:
        for x, y in ((6, 18), (7, 18), (8, 18), (9, 18), (6, 19), (9, 19), (7, 20), (8, 20), (7, 21), (8, 21), (6, 22), (9, 22)):
            p.px(x, y, INK[0])
    return p.im


def yeast_jar() -> Image.Image:
    p = Pix(32, 32, seed=5)
    jar = box(9, 8, 16, 22) | ell(16.5, 29, 8, 2)
    part(p, jar, GLASS, 2, grad=0.6)
    inner = box(11, 11, 12, 17)
    amber = mk("#d49a3c")
    part(p, inner, amber, 2, outline=GLASS[0], grad=1.0, dith=True)
    for x, y in ((12, 24), (16, 20), (20, 25), (14, 16), (19, 14), (22, 20), (17, 27)):
        part(p, ell(x, y, 1.5, 1.5), amber, 3, outline=None, grad=0.3)
        p.px(x - 1, y - 1, amber[4])
    p.hline(11, 11, 12, amber[4])
    p.vline(10, 12, 15, GLASS[4])
    p.px(10, 11, GLASS[4])
    cloth = ell(16.5, 6, 9.5, 4) | box(9, 4, 15, 5)
    part(p, cloth, LINEN_R, 3, grad=0.8)
    for x in range(11, 23, 3):
        p.vline(x, 3, 5, LINEN_R[2])
    p.hline(9, 9, 15, STRAW[1])
    p.hline(9, 10, 15, STRAW[2])
    p.px(22, 10, STRAW[3]), p.px(23, 11, STRAW[1])
    return p.im


def airlock() -> Image.Image:
    p = Pix(16, 16, seed=1)
    cork = poly([(4, 8), (11, 8), (10, 13), (5, 13)])
    part(p, cork, CORK, 2, grad=0.8)
    p.px(7, 10, CORK[1])
    bulb = ell(7.5, 5.5, 6.5, 3.6)
    part(p, bulb, GLASS, 2, grad=0.7)
    water = ell(7.5, 6.5, 4.0, 1.8)
    part(p, water, mk("#5a9ab0"), 3, outline=None, grad=0.5)
    p.px(5, 4, GLASS[4]), p.px(6, 3, GLASS[4])
    p.px(8, 7, mk("#bfe0e8")[3])
    cap = box(6, 0, 4, 2)
    part(p, cap, CORK, 3, grad=0.4)
    return p.im


# ---------------------------------------------------------------------- grapes and the rack

def grape_bunch() -> Image.Image:
    p = Pix(32, 32, seed=9)
    stem = tube([(20, 2, 0.9), (17, 6, 0.9), (14, 9, 0.8)])
    part(p, stem, BROWN, 2, grad=0.3)
    p.px(21, 1, BROWN[3])
    leaf(p, 19, 4, 26, 1, 5, LEAF, False)
    berry = mk("#6a2c8a")
    pts = []
    rows = 5
    for j in range(rows):
        n = rows - j
        for i in range(n):
            pts.append((14 + (i - (n - 1) / 2) * 4.6, 12 + j * 3.9))
    for x, y in sorted(pts, key=lambda a: a[1]):
        part(p, ell(x, y, 2.6, 2.6), berry, 2, grad=0.9)
        p.px(round(x) - 1, round(y) - 1, berry[4])
        p.px(round(x) - 1, round(y) - 2, rgb("#d0a0e0")) if False else None
    return p.im


def wine_rack() -> Image.Image:
    p = Pix(48, 48, seed=11)
    frame = box(5, 1, 38, 46)
    part(p, frame, OAKR, 2, grad=0.8)
    inner = box(8, 4, 32, 40)
    part(p, inner, mk("#1d1210"), 1, outline=SHADOW, grad=0.3)
    glass = mk("#4a3a46")
    for r, ty in enumerate((5, 18, 31)):
        # shelf board under each row
        for k in range(6):
            cx, cy = 11 + k * 5.2, ty + 5
            part(p, ell(cx, cy, 2.6, 2.6), glass, 2, grad=0.9)
            part(p, ell(cx, cy, 1.1, 1.1), CORK if (k + r) % 2 else mk("#8a2a30"), 2, outline=None, grad=0.5)
            p.px(round(cx - 1), round(cy - 2), glass[4])
        shelf = box(8, ty + 9, 32, 3)
        part(p, shelf, mk("#8c6840"), 2, grad=0.8)
    top = box(5, 1, 38, 3)
    part(p, top, mk("#9c7048"), 3, grad=0.5)
    p.hline(6, 1, 36, mk("#9c7048")[4])
    # brass corner studs
    for x, y in ((6, 3), (41, 3), (6, 45), (41, 45)):
        p.px(x, y, BRASS[3])
    return p.im


# ---------------------------------------------------------------------- the list

PICS: dict = {
    "wine_bottle": wine_empty,
    "wine_fermenting": wine_fermenting,
    "wine_bottom": wine_bottom,
    "wine_berry": grape_bunch,
    "wine_rack": wine_rack,
    "fermentation_airlock": airlock,
    "yeast": lambda: yeast_pot(mk("#8a8480"), mk("#c2b48a"), "dot"),
    "superyeast": lambda: yeast_pot(mk("#7a4a8c"), mk("#d0a847"), "star"),
    "illegal_yeast": lambda: yeast_pot(mk("#8a2c2e"), mk("#a8302e"), "skull"),
    "yeast_gen": yeast_jar,
}
for _i in range(6):
    PICS[f"bottle{_i}"] = lambda i=_i: wine_bottle_n(i)
    PICS[f"wine_label{_i}"] = lambda i=_i: label_pic(str(i))
PICS["wine_label_red"] = lambda: label_pic("red")
