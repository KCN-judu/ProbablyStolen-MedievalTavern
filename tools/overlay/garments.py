"""Garment parts: collars, laces, buttons, tabards, aprons, straps, belts, guards, cloaks, scarves, chains, badges.

`width` is the shoulder width (px) the part was drawn for. Anchors: neck / shoulders / chest centre; the composer reads
`landmark` and `anchor` only. `clip` parts are cut to the figure's silhouette (+ `grow` px) so nothing hangs in the air.
"""

from __future__ import annotations

import math

from kit import RAMPS, Art, Mask, Ramp, shift_tone
from partdef import Part

SIZES = {"S": 112, "M": 130, "L": 148}


def _fold(a: Art, ramp: Ramp, pts: list[tuple[float, float]]) -> None:
    """A fold in the cloth: a dark crease with a lit lip on its left (light comes from the upper left)."""
    m = a.mask().line(pts, 1)
    px = a.im.load()
    mp = m.im.load()
    for y in range(a.h):
        for x in range(a.w):
            if mp[x, y] > 127 and px[x, y][3] > 0 and px[x, y][:3] != ramp[0]:
                c = shift_tone(ramp, px[x, y][:3], -1)
                px[x, y] = (*c, 255)
                if x > 0 and px[x - 1, y][3] > 0 and px[x - 1, y][:3] != ramp[0] and mp[x - 1, y] < 128:
                    px[x - 1, y] = (*shift_tone(ramp, px[x - 1, y][:3], 1), 255)


def _mk(id_: str, style: str, a: Art, anchor: tuple[int, int], landmark: str, width: int, colour: str = "", size: str = "",
        tags: list[str] | None = None, layer: str = "front", clip: bool = False, grow: int = 0) -> Part:
    return Part(id=id_, cat="garments", style=style, img=a.im, anchor=anchor, landmark=landmark, layer=layer, width=width,
                colour=colour, size=size, tags=tags or [], clip=clip, grow=grow)


def _buckle(a: Art, cx: int, cy: int, w: int = 9, h: int = 7, col: str = "brass") -> None:
    br = RAMPS[col]
    o = a.mask().rect(cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
    i = a.mask().rect(cx - w // 2 + 2, cy - h // 2 + 2, cx + w // 2 - 2, cy + h // 2 - 2)
    o.sub(i)
    a.fill(o, br, radius=1.2, base=0.6)
    a.line([(cx - 1, cy), (cx + w // 2 - 1, cy)], br[3])


# ------------------------------------------------------------------------------------------------ collars


def collar_fold(col: str) -> Part:
    ramp = RAMPS[col]
    a = Art(60, 30, 5)
    ax, ay = 30, 12
    for sx in (-1, 1):
        f = a.mask().poly([(ax + sx * 2, ay + 2), (ax + sx * 21, ay - 7), (ax + sx * 23, ay + 2), (ax + sx * 8, ay + 15)])
        a.fill(f, ramp, tex="linen", radius=2.5)
        a.line([(ax + sx * 3, ay + 4), (ax + sx * 20, ay - 3)], ramp[1])
    return _mk(f"collar_fold_{col}", "collar_fold", a, (ax, ay), "neck", 46, col, tags=["collar", "shirt", "official", "commoner"])


def collar_ruff(col: str) -> Part:
    ramp = RAMPS[col]
    a = Art(70, 30, 6)
    ax, ay = 35, 11
    m = a.mask().ellipse(ax, ay, 29, 9)
    m.sub(a.mask().ellipse(ax, ay - 3, 14, 6))
    a.fill(m, ramp, tex=None, radius=2.5)
    for k in range(-13, 14):
        x = ax + k * 2
        a.line([(x, ay + 1), (x, ay + 8 - abs(k) // 5)], ramp[1])
        a.px(x - 1, ay + 2, ramp[4])
    return _mk(f"collar_ruff_{col}", "collar_ruff", a, (ax, ay), "neck", 58, col, tags=["collar", "gentry", "official"])


def collar_band(col: str, trim: str) -> Part:
    ramp, tr = RAMPS[col], RAMPS[trim]
    a = Art(64, 24, 7)
    ax, ay = 32, 9
    m = a.mask().ellipse(ax, ay + 1, 24, 8).clip_rows(ay - 2, 30)
    m.sub(a.mask().ellipse(ax, ay - 4, 15, 8))
    a.fill(m, ramp, tex="wool", radius=2.5)
    a.line([(ax - 22, ay + 3), (ax - 8, ay + 8), (ax, ay + 9), (ax + 8, ay + 8), (ax + 22, ay + 3)], tr[3])
    return _mk(f"collar_band_{col}_{trim}", "collar_band", a, (ax, ay), "neck", 52, col, tags=["collar", "official", "smith", "scholar"])


def neckline_v(col: str, trim: str) -> Part:
    """A trimmed V neckline of a tunic, drawn as a dark opening with a bordered edge."""
    ramp, tr = RAMPS[col], RAMPS[trim]
    a = Art(56, 36, 8)
    ax, ay = 28, 4
    m = a.mask().poly([(ax - 20, ay - 3), (ax + 20, ay - 3), (ax + 3, ay + 30), (ax - 3, ay + 30)])
    m.sub(a.mask().poly([(ax - 15, ay - 5), (ax + 15, ay - 5), (ax, ay + 21)]))
    a.fill(m, tr, radius=1.8)
    return _mk(f"neckline_v_{col}_{trim}", "neckline_v", a, (ax, ay), "neck", 40, col, tags=["collar", "tunic"])


# ------------------------------------------------------------------------------------------------ laces, buttons


def laces(col: str) -> Part:
    ramp = RAMPS[col]
    a = Art(28, 38, 9)
    a.inside = False
    ax, ay = 14, 0
    br = RAMPS["brass"]
    for sx in (-1, 1):
        e = a.mask().rect(ax + sx * 7 - 2, ay, ax + sx * 7 + 2, ay + 36)
        a.fill(e, RAMPS["leather"], radius=1.2)
        for y in range(3, 35, 6):
            a.px(ax + sx * 7, y, br[1]), a.px(ax + sx * 7 - 1, y - 1, br[3])
    for y in range(3, 33, 6):
        a.line([(ax - 7, y), (ax + 7, y + 6)], ramp[3]), a.line([(ax + 7, y), (ax - 7, y + 6)], ramp[2])
    a.line([(ax, ay + 35), (ax - 2, ay + 37)], ramp[3]), a.line([(ax, ay + 35), (ax + 2, ay + 37)], ramp[3])
    return _mk(f"laces_{col}", "laces", a, (ax, ay), "chest", 20, col, tags=["laces", "bodice", "female", "commoner"], clip=True)


def buttons(col: str, n: int) -> Part:
    r = RAMPS[col]
    a = Art(9, 7 * n + 2, 10)
    for i in range(n):
        y = 3 + i * 7
        m = a.mask().ellipse(4.5, y + 0.5, 3, 3)
        a.fill(m, r, radius=1.0, base=0.62)
        a.px(4, y, r[0]), a.px(5, y, r[0])
    return _mk(f"buttons_{col}_{n}", "buttons", a, (4, 0), "chest", 9, col, tags=["buttons", "official", "scholar"], clip=True)


# ------------------------------------------------------------------------------------------------ body panels


def _emblem(a: Art, kind: str, ax: int, y: int) -> None:
    c, br = RAMPS["cream"], RAMPS["brass"]
    if kind == "cross":
        m = a.mask().rect(ax - 2, y, ax + 2, y + 21).add(a.mask().rect(ax - 7, y + 5, ax + 7, y + 9))
        a.fill(m, c, radius=1.5, base=0.62)
    elif kind == "tower":
        m = a.mask().rect(ax - 6, y + 8, ax + 6, y + 22)
        for k in (-6, -2, 2):
            m.rect(ax + k, y + 4, ax + k + 3, y + 9)
        a.fill(m, br, radius=1.4, base=0.6)
        a.fill(a.mask().rect(ax - 2, y + 15, ax + 1, y + 22), RAMPS["black"], radius=1)
    elif kind == "chevron":
        for k in (0, 7):
            a.fill(a.mask().line([(ax - 12, y + k), (ax, y + 9 + k), (ax + 12, y + k)], 3), c, radius=1.0, base=0.62)
    elif kind == "stripe":
        a.fill(a.mask().rect(ax - 4, y - 8, ax + 4, y + 120), c, radius=1.4, base=0.62)


def tabard(col: str, emblem: str, sz: str) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.7), 112
    a = Art(w, h, 11 + sw)
    ax, ay = w // 2, 0
    top, bot = sw * 0.11, sw * 0.19
    m = a.mask().poly([(ax - top - 8, 0), (ax - 9, 0), (ax, 9), (ax + 9, 0), (ax + top + 8, 0), (ax + bot + 6, h - 2), (ax - bot - 6, h - 2)])
    a.fill(m, ramp, tex="wool", radius=4, base=0.6)
    for d in (-0.6, -0.25, 0.3, 0.62):
        _fold(a, ramp, [(ax + d * (top + 8), 4), (ax + d * (bot + 4) + 1, h * 0.5), (ax + d * (bot + 6), h - 4)])
    tr = RAMPS["brass" if col in ("wine", "indigo", "charcoal") else "leather"]
    a.line([(ax - bot - 6, h - 5), (ax + bot + 6, h - 5)], tr[3])
    a.line([(ax - bot - 6, h - 4), (ax + bot + 6, h - 4)], tr[1])
    _emblem(a, emblem, ax, 24)
    return _mk(f"tabard_{col}_{emblem}_{sz}", "tabard", a, (ax, 0), "shoulders", sw, col, sz, ["tabard", "watch", "official", "gentry", "merc"], clip=True, grow=0)


def apron(col: str, sz: str, pocket: bool = True) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.85), 110
    a = Art(w, h, 21 + sw)
    ax = w // 2
    tw, bw = sw * 0.13, sw * 0.24
    # neck straps rise from the bib corners to the shoulders
    for sx in (-1, 1):
        s = a.mask().line([(ax + sx * (tw - 1), 12), (ax + sx * (tw + 8), 0), (ax + sx * (tw + 16), -4 + 4)], 4)
        a.fill(s, RAMPS["leather"] if col != "leather" else RAMPS["brown"], radius=1.2, base=0.6)
    m = a.mask().poly([(ax - tw, 8), (ax + tw, 8), (ax + tw + 3, 22), (ax + bw, 36), (ax + bw + 6, h - 2), (ax - bw - 6, h - 2), (ax - bw, 36), (ax - tw - 3, 22)])
    a.fill(m, ramp, tex="linen" if col in ("linen", "cream", "sand") else "leather", radius=4, base=0.62)
    for d in (-0.5, 0.15, 0.55):
        _fold(a, ramp, [(ax + d * bw, 24), (ax + d * bw * 1.2, 60), (ax + d * bw * 1.25, h - 4)])
    a.line([(ax - bw - 5, 52), (ax + bw + 5, 52)], ramp[1])   # waist seam
    for sx in (-1, 1):
        a.px(ax + sx * (bw + 3), 52, RAMPS["brass"][3])
    if pocket:
        p = a.mask().rect(ax - 11, 64, ax + 11, 84)
        a.fill(p, ramp, tex=None, radius=2, base=0.66)
        a.line([(ax - 10, 66), (ax + 10, 66)], ramp[4])
    return _mk(f"apron_{col}_{sz}", "apron", a, (ax, 8), "chest", sw, col, sz, ["apron", "smith", "cook", "farmer", "commoner"], clip=True, grow=0)


def quilt(kind: str) -> Part:
    """Gambeson quilting as a translucent overlay: seams and puffed channels."""
    a = Art(110, 100, 31)
    ax = 55
    px = a.im.load()
    for y in range(100):
        for x in range(110):
            if kind == "vertical":
                if x % 9 == 4:
                    px[x, y] = (34, 20, 30, 170)
                elif x % 9 == 3 and y % 2 == 0:
                    px[x, y] = (255, 232, 190, 60)
                elif x % 9 in (5, 6) and (y + x) % 3 == 0:
                    px[x, y] = (34, 20, 30, 50)
            else:
                d1, d2 = (x + y) % 12, (x - y) % 12
                if d1 == 0 or d2 == 0:
                    px[x, y] = (34, 20, 30, 150)
                elif d1 == 11 or d2 == 11:
                    px[x, y] = (255, 232, 190, 55)
    p = _mk(f"quilt_{kind}", "quilt", a, (ax, 0), "chest", 110, tags=["gambeson", "watch", "merc", "padded"], clip=True)
    p.alpha_part = True
    return p


def patch(col: str, w: int, h: int, tag: str = "cloth") -> Part:
    ramp = RAMPS[col]
    a = Art(w + 2, h + 2, 41 + w)
    m = a.mask().rect(1, 1, w, h)
    a.fill(m, ramp, tex="wool" if tag == "cloth" else "leather", radius=2, base=0.6)
    for x in range(3, w - 1, 3):
        a.px(x, 3, ramp[1]), a.px(x, h - 2, ramp[1])
    for y in range(3, h - 1, 3):
        a.px(3, y, ramp[1]), a.px(w - 2, y, ramp[1])
    return _mk(f"patch_{tag}_{col}_{w}x{h}", "patch", a, ((w + 2) // 2, (h + 2) // 2), "chest", w, col, tags=["patch", "cover"], clip=True)


# ------------------------------------------------------------------------------------------------ straps and belts


def bandolier(col: str, sz: str, flip: bool, vials: bool) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.8), 112
    a = Art(w, h, 51 + sw)
    x0, x1 = 6, w - 6
    pts = [(x0, -4), (x1, h + 6)]
    s = a.mask().line(pts, 7)
    a.fill(s, ramp, tex="leather", radius=2, base=0.62)
    sl = (x1 - x0) / (h + 10)
    for t in (0.22, 0.4, 0.58, 0.76):
        x, y = x0 + (h * t) * sl, h * t
        if vials:
            m = a.mask().rect(x - 2, y - 2, x + 1, y + 7)
            a.fill(m, RAMPS["steel"] if t > 0.5 else RAMPS["brass"], radius=1.0)
            a.px(int(x - 1), int(y - 1), RAMPS["cream"][4])
        else:
            m = a.mask().rect(x - 4, y - 1, x + 5, y + 9)
            a.fill(m, RAMPS["brown"], tex="leather", radius=1.8, base=0.6)
            a.line([(x - 3, y + 2), (x + 4, y + 2)], RAMPS["brown"][1])
            a.px(int(x), int(y + 4), RAMPS["brass"][3])
    _buckle(a, int(x0 + 12 * sl), 12, 8, 6)
    img = a.im.transpose(0) if flip else a.im  # FLIP_LEFT_RIGHT == 0
    a.im = img
    return _mk(f"bandolier_{col}_{'v' if vials else 'p'}_{'r' if flip else 'l'}_{sz}", "bandolier", a, (w // 2, 0), "shoulders", sw, col, sz,
               ["bandolier", "merc", "strap", "leather"], clip=True)


def straps_pair(col: str, sz: str) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.7), 112
    a = Art(w, h, 61 + sw)
    a.inside = False
    ax = w // 2
    for sx in (-1, 1):
        s = a.mask().line([(ax + sx * sw * 0.2, -4), (ax + sx * sw * 0.14, h)], 6)
        a.fill(s, ramp, tex="leather", radius=2, base=0.62)
        for y in range(10, h, 14):
            a.px(int(ax + sx * (sw * 0.2 - y * sw * 0.06 / h)), y, RAMPS["brass"][3])
        _buckle(a, int(ax + sx * sw * 0.18), 34, 8, 6)
    a.line([(ax - sw * 0.14, 60), (ax + sw * 0.14, 60)], ramp[3], width=3)
    return _mk(f"straps_pair_{col}_{sz}", "straps_pair", a, (ax, 0), "shoulders", sw, col, sz, ["strap", "smith", "leather", "farmer", "suspenders"], clip=True)


def belt(col: str, sz: str) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w = int(sw * 0.95)
    a = Art(w, 16, 71 + sw)
    ax = w // 2
    m = a.mask().rect(0, 3, w, 11)
    a.fill(m, ramp, tex="leather", radius=2, base=0.62)
    a.line([(0, 5), (w, 5)], ramp[1]), a.line([(0, 9), (w, 9)], ramp[3])
    _buckle(a, ax, 7, 12, 11)
    for x in range(6, w - 4, 9):
        if abs(x - ax) > 12:
            a.px(x, 7, RAMPS["brass"][3])
    return _mk(f"belt_{col}_{sz}", "belt", a, (ax, 7), "chest", sw, col, sz, ["belt", "buckle", "leather", "all"], clip=True)


def sash(col: str, sz: str, flip: bool) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.75), 100
    a = Art(w, h, 81 + sw)
    s = a.mask().line([(4, -4), (w - 12, h - 12)], 9)
    a.fill(s, ramp, tex="wool", radius=3, base=0.6)
    _fold(a, ramp, [(14, 0), (w - 6, h - 20)])
    k = a.mask().ellipse(w - 12, h - 12, 7, 6).add(a.mask().poly([(w - 14, h - 8), (w - 6, h + 2), (w - 18, h + 2)]))
    a.fill(k, ramp, radius=2, base=0.6)
    a.px(w - 12, h - 12, ramp[0])
    if flip:
        a.im = a.im.transpose(0)
    return _mk(f"sash_{col}_{'r' if flip else 'l'}_{sz}", "sash", a, (w // 2, 0), "shoulders", sw, col, sz, ["sash", "official", "gentry", "merc"], clip=True)


# ------------------------------------------------------------------------------------------------ guards and cloaks


def pauldron(col: str) -> Part:
    """One shoulder guard (left shoulder; the composer mirrors it for the right). Anchor: top centre of the dome."""
    ramp = RAMPS[col]
    a = Art(42, 36, 91 + len(col))
    cx = 21
    top = a.mask().ellipse(cx, 16, 18, 13).clip_rows(3, 27)
    if col in ("iron", "steel"):
        a.fill(top, ramp, tex="plate", radius=4, base=0.58)
        lame = a.mask().ellipse(cx + 1, 25, 16, 6).clip_rows(22, 36)
        a.fill(lame, ramp, radius=2.5, base=0.5)
        a.px(cx - 6, 12, RAMPS["brass"][3]), a.px(cx + 6, 12, RAMPS["brass"][3]), a.px(cx, 9, RAMPS["brass"][3])
    else:
        a.fill(top, ramp, tex="leather", radius=4, base=0.6)
        for k, yy in enumerate((12, 17, 22)):
            a.line([(cx - 14 + k * 2, yy), (cx + 14 - k * 2, yy)], ramp[1])
        a.px(cx, 8, RAMPS["brass"][3])
    return _mk(f"pauldron_{col}", "pauldron", a, (cx, 3), "shoulder_edge", 42, col, tags=["guard", "merc", "watch"], grow=0)


def cloak_back(col: str, sz: str) -> Part:
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 1.35), 140
    a = Art(w, h, 101 + sw)
    ax, ay = w // 2, 20
    m = a.mask().poly([(ax - sw * 0.2, ay - 10), (ax + sw * 0.2, ay - 10), (ax + sw * 0.5, ay + 6), (ax + sw * 0.64, h - 2), (ax - sw * 0.64, h - 2), (ax - sw * 0.5, ay + 6)])
    m.add(a.mask().ellipse(ax, ay - 4, sw * 0.22, 9))
    a.fill(m, ramp, tex="wool", radius=6, base=0.45, strength=0.8)
    for d in (-0.5, -0.24, 0.06, 0.34, 0.58):
        _fold(a, ramp, [(ax + d * sw * 0.45, ay + 10), (ax + d * sw * 0.6, h * 0.6), (ax + d * sw * 0.64, h - 4)])
    return _mk(f"cloak_back_{col}_{sz}", "cloak_back", a, (ax, ay), "neck", sw, col, sz, ["cloak", "back", "dealer", "gentry", "merc", "rebel"], layer="back")


def cloak_front(col: str, sz: str, clasp: str = "brass") -> Part:
    """The front of a cloak: a shoulder drape with two short front edges that part over the chest, and a clasp."""
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 1.3), 90
    a = Art(w, h, 111 + sw)
    ax = w // 2
    left = [(ax - 14, 0), (ax - sw * 0.5, 7), (ax - sw * 0.6, 34), (ax - sw * 0.55, 52), (ax - sw * 0.36, 60), (ax - sw * 0.2, 68),
            (ax - 13, 84), (ax - 5, 86), (ax - 5, 30), (ax - 8, 14)]
    right = [(2 * ax - x, y) for x, y in left]
    m = a.mask().poly(left + right[::-1])
    a.fill(m, ramp, tex="wool", radius=5, base=0.6)
    for d in (-0.45, -0.28, 0.28, 0.45):
        _fold(a, ramp, [(ax + d * sw * 0.35, 12), (ax + d * sw * 0.48, 32), (ax + d * sw * 0.52, 52)])
    c = RAMPS[clasp]
    a.fill(a.mask().ellipse(ax - 1, 8, 4, 4), c, radius=1.2, base=0.62)
    a.line([(ax - 9, 8), (ax + 7, 8)], c[2])
    return _mk(f"cloak_front_{col}_{sz}", "cloak_front", a, (ax, 2), "neck", sw, col, sz, ["cloak", "front", "dealer", "gentry", "merc", "rebel"], clip=True, grow=6)


def mantle(col: str, sz: str) -> Part:
    """A short shoulder cape (no long front panels), thin and trimmed at the hem."""
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 1.15), 40
    a = Art(w, h, 121 + sw)
    ax = w // 2
    left = [(ax - 16, 0), (ax - sw * 0.46, 4), (ax - sw * 0.52, 20), (ax - sw * 0.46, 33), (ax - sw * 0.34, 30), (ax - sw * 0.26, 36),
            (ax - sw * 0.16, 30), (ax - 9, 24), (ax - 6, 12)]
    right = [(2 * ax - x, y) for x, y in left]
    m = a.mask().poly(left + right[::-1])
    a.fill(m, ramp, tex="wool", radius=4, base=0.6)
    for d in (-0.5, -0.3, 0.3, 0.5):
        _fold(a, ramp, [(ax + d * sw * 0.3, 6), (ax + d * sw * 0.45, 20), (ax + d * sw * 0.47, 30)])
    tr = RAMPS["brass" if col in ("wine", "indigo", "charcoal") else "leather"]
    a.line([(ax - sw * 0.44, 30), (ax - sw * 0.3, 27), (ax - sw * 0.14, 27)], tr[3])
    a.line([(ax + sw * 0.44, 30), (ax + sw * 0.3, 27), (ax + sw * 0.14, 27)], tr[3])
    return _mk(f"mantle_{col}_{sz}", "mantle", a, (ax, 2), "neck", sw, col, sz, ["cape", "mantle", "official", "scholar"], clip=True, grow=6)


def _studs_on(a: Art, pts: list[tuple[int, int]]) -> None:
    br = RAMPS["brass"]
    al = a.im.load()
    for x, y in pts:
        if all(0 <= x + dx < a.w and 0 <= y + dy < a.h and al[x + dx, y + dy][3] > 0 for dx, dy in ((0, 0), (1, 0), (0, 1))):
            a.px(x, y, br[4]), a.px(x + 1, y, br[3]), a.px(x, y + 1, br[1])


def _vest_shape(a: Art, ax: int, sw: int, h: int, wide: float) -> Mask:
    k = sw * wide
    return a.mask().poly([(ax - k, 0), (ax - sw * 0.11, 0), (ax - sw * 0.07, 10), (ax, 14), (ax + sw * 0.07, 10), (ax + sw * 0.11, 0),
                          (ax + k, 0), (ax + k + 2, 40), (ax + k * 0.95, h - 1), (ax - k * 0.95, h - 1), (ax - k - 2, 40)])


def brigandine(col: str, sz: str) -> Part:
    """A brigandine: cloth over riveted plates, shoulder straps, centre lacing and a buckled side strap. Covers rigs and carriers."""
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.62), 112
    a = Art(w, h, 401 + sw)
    ax = w // 2
    m = _vest_shape(a, ax, sw, h, 0.27)
    a.fill(m, ramp, tex="wool" if col not in ("leather", "brown") else "leather", radius=5, base=0.56)
    pts = []
    for row, y in enumerate(range(22, h - 4, 7)):
        a.line([(ax - sw * 0.27, y - 3), (ax + sw * 0.27, y - 3)], ramp[1])
        for x in range(int(ax - sw * 0.27) + 5 + (row % 2) * 3, int(ax + sw * 0.27) - 3, 6):
            if abs(x - ax) > 3:
                pts.append((x, y))
    _studs_on(a, pts)
    a.line([(ax, 15), (ax, h)], ramp[0])
    for y in range(18, h - 6, 7):
        a.line([(ax - 3, y), (ax + 3, y + 4)], RAMPS["leather"][3]), a.line([(ax + 3, y), (ax - 3, y + 4)], RAMPS["leather"][2])
    for sx in (-1, 1):
        a.line([(ax + sx * sw * 0.18, 0), (ax + sx * sw * 0.2, 24)], RAMPS["leather"][2], width=3)
        _buckle(a, int(ax + sx * sw * 0.2), 24, 6, 5)
    return _mk(f"brigandine_{col}_{sz}", "brigandine", a, (ax, 0), "shoulders", sw, col, sz, ["brigandine", "watch", "merc", "rebel", "armour"], clip=True)


def gambeson_vest(col: str, sz: str) -> Part:
    """A padded jerkin: quilted channels, toggles down the front, shoulder straps."""
    sw = SIZES[sz]
    ramp = RAMPS[col]
    w, h = int(sw * 0.66), 112
    a = Art(w, h, 411 + sw)
    ax = w // 2
    m = _vest_shape(a, ax, sw, h, 0.29)
    a.fill(m, ramp, tex="wool", radius=5, base=0.6)
    for x in range(int(ax - sw * 0.29), int(ax + sw * 0.3), 7):
        a.line([(x, 14), (x + 1, h)], ramp[1])
        a.line([(x - 1, 14), (x, h)], ramp[4])
    for y in range(26, h, 14):
        a.line([(ax - sw * 0.29, y), (ax + sw * 0.29, y + 1)], ramp[1])
    for y in range(18, h - 8, 12):
        a.fill(a.mask().ellipse(ax, y, 2.6, 2.6), RAMPS["bone"], radius=1.0, base=0.62)
    return _mk(f"gambeson_{col}_{sz}", "gambeson", a, (ax, 0), "shoulders", sw, col, sz, ["gambeson", "watch", "merc", "padded"], clip=True)


def plague_beak(col: str) -> Part:
    """A leather beak over mouth and nose, tied behind the ears: the period answer to a gas or surgical mask."""
    ramp = RAMPS[col]
    a = Art(28, 36, 421)
    a.inside = False
    cx = 14
    m = a.mask().poly([(cx - 9, 0), (cx + 9, 0), (cx + 8, 8), (cx + 6, 17), (cx + 3, 27), (cx - 1, 34), (cx - 3, 28), (cx - 5, 17), (cx - 8, 8)])
    a.fill(m, ramp, tex="leather", radius=4, base=0.58)
    a.inside = True
    a.line([(cx, 3), (cx, 30)], ramp[1])
    a.line([(cx - 3, 4), (cx - 2, 20), (cx - 1, 29)], ramp[4])
    a.inside = False
    a.line([(0, 3), (cx - 8, 2)], ramp[2]), a.line([(cx + 8, 2), (27, 3)], ramp[2])
    a.px(cx - 2, 24, ramp[0]), a.px(cx + 2, 24, ramp[0])
    return _mk(f"plague_beak_{col}", "plague_beak", a, (cx, 1), "nose", 28, col, tags=["beak", "physician", "mask"], clip=True)


# ------------------------------------------------------------------------------------------------ scarves, chains, badges


def scarf_wrap(col: str, tail: bool = True) -> Part:
    ramp = RAMPS[col]
    a = Art(80, 50, 131)
    ax, ay = 40, 10
    m = a.mask().ellipse(ax, ay + 3, 27, 9)
    m.sub(a.mask().ellipse(ax, ay - 4, 13, 7))
    if tail:
        m.add(a.mask().poly([(ax + 12, ay + 6), (ax + 24, ay + 8), (ax + 25, ay + 44), (ax + 14, ay + 38)]))
    a.fill(m, ramp, tex="knit", radius=3, base=0.6)
    for k in (-18, -9, 0, 9, 18):
        a.line([(ax + k, ay + 6), (ax + k * 0.9, ay + 11)], ramp[1])
    if tail:
        for y in range(ay + 14, ay + 40, 7):
            a.line([(ax + 14, y), (ax + 24, y + 1)], ramp[4])
        for x in range(ax + 14, ax + 25, 2):
            a.px(x, ay + 43, ramp[3])
    return _mk(f"scarf_wrap_{col}{'_tail' if tail else ''}", "scarf_wrap", a, (ax, ay), "neck", 54, col, tags=["scarf", "rebel", "dealer", "commoner"])


def scarf_cover(col: str, hw: int) -> Part:
    """A scarf pulled over mouth and chin: top edge at the nose base, falling to the neck."""
    ramp = RAMPS[col]
    r = hw / 2
    w, h = hw + 14, int(0.62 * hw)
    a = Art(w, h, 141 + hw)
    ax = w // 2
    m = a.mask().poly([(ax - r + 1, 0), (ax - 4, 4), (ax, 3), (ax + 4, 4), (ax + r - 1, 0), (ax + r + 3, h * 0.55), (ax + r - 2, h - 1), (ax - r + 2, h - 1), (ax - r - 3, h * 0.55)])
    a.fill(m, ramp, tex="knit", radius=3.5, base=0.58)
    a.line([(ax - r + 3, 4), (ax - 4, 7), (ax, 6), (ax + 4, 7), (ax + r - 3, 4)], ramp[4])
    a.line([(ax - r, h * 0.45), (ax + r, h * 0.5)], ramp[1])
    return _mk(f"scarf_cover_{col}_{hw}", "scarf_cover", a, (ax, 3), "nose", hw, col, "S" if hw < 44 else ("M" if hw < 50 else "L"),
               ["scarf", "mask", "rebel", "dealer"])


def chain_office(kind: str, sz: str) -> Part:
    """A chain of office: two strands of links falling from the neck over the chest, with a medallion."""
    sw = SIZES[sz]
    metal = RAMPS["brass" if kind != "silver" else "steel"]
    w, h = int(sw * 0.5), 74
    a = Art(w, h, 151 + sw)
    a.inside = False
    ax = w // 2
    n = 70
    prev = None
    for i in range(n + 1):
        t = i / n
        x = round(ax + (t - 0.5) * w * 0.9)
        y = round(1 + (52 if kind != "plain" else 40) * math.sin(math.pi * t) ** 1.5)
        if (x, y) == prev:
            continue
        prev = (x, y)
        j = len(a.im.getbbox() or ())  # noqa: F841
        c = (metal[3], metal[2], metal[1], metal[2])[i % 4]
        a.px(x, y, c)
        if i % 4 == 0:
            a.px(x, y - 1, metal[4])
        if i % 4 == 2:
            a.px(x, y + 1, metal[0])
    if kind == "double":
        for i in range(0, n + 1):
            t = i / n
            x = round(ax + (t - 0.5) * w * 0.9)
            y = round(1 + 30 * math.sin(math.pi * t) ** 1.5)
            a.px(x, y, (metal[3], metal[1])[i % 2])
    if kind in ("medallion", "double", "silver"):
        cx, cy = ax, 58
        a.fill(a.mask().ellipse(cx, cy, 6.5, 6.5), metal, radius=2, base=0.62)
        a.fill(a.mask().ellipse(cx, cy, 3, 3), RAMPS["wine" if kind != "silver" else "blue"], radius=1, base=0.6)
    return _mk(f"chain_{kind}_{sz}", "chain_office", a, (ax, 0), "neck", sw, kind, sz, ["chain", "official", "gentry", "guild"], clip=True, grow=0)


def pendant(kind: str) -> Part:
    a = Art(34, 36, 161)
    ax = 17
    cord = RAMPS["leather"]
    for t in range(0, 15):
        a.px(ax - 14 + t, 0 + int(t * 0.75), cord[2]), a.px(ax + 14 - t, 0 + int(t * 0.75), cord[2])
    a.px(ax, 12, cord[2])
    br = RAMPS["brass"]
    if kind == "cross":
        a.fill(a.mask().rect(ax - 1, 13, ax + 1, 25).add(a.mask().rect(ax - 4, 16, ax + 4, 18)), br, radius=1.0, base=0.62)
    elif kind == "gem":
        a.fill(a.mask().poly([(ax, 13), (ax + 4, 18), (ax, 25), (ax - 4, 18)]), RAMPS["red"], radius=1.2, base=0.62)
    elif kind == "key":
        a.fill(a.mask().ellipse(ax, 16, 3.5, 3.5), br, radius=1.0)
        a.fill(a.mask().rect(ax - 1, 19, ax + 1, 29), br, radius=1.0)
        a.fill(a.mask().rect(ax + 1, 26, ax + 3, 28), br, radius=1.0)
    else:  # moon
        m = a.mask().ellipse(ax, 19, 5, 5)
        m.sub(a.mask().ellipse(ax + 2, 18, 4, 4))
        a.fill(m, RAMPS["steel"], radius=1.2, base=0.62)
    return _mk(f"pendant_{kind}", "pendant", a, (ax, 0), "neck", 34, kind, tags=["pendant", "amulet", "commoner", "scholar"])


def badge_shield(col: str, charge: str) -> Part:
    ramp = RAMPS[col]
    br = RAMPS["brass"]
    a = Art(16, 20, 171)
    m = a.mask().poly([(1, 1), (14, 1), (14, 10), (11, 16), (8, 18), (4, 16), (1, 10)])
    a.fill(m, br, radius=1.2, base=0.58)
    i = a.mask().poly([(3, 3), (12, 3), (12, 9), (10, 14), (8, 16), (5, 14), (3, 9)])
    a.fill(i, ramp, radius=1.5, base=0.6)
    if charge == "tower":
        a.fill(a.mask().rect(5, 7, 10, 13), br, radius=1.0)
        a.dots([(5, 6), (7, 6), (9, 6)], br[3])
    elif charge == "cross":
        a.fill(a.mask().rect(7, 4, 8, 14).add(a.mask().rect(4, 7, 11, 8)), RAMPS["cream"], radius=0.8)
    else:
        a.line([(4, 12), (8, 5), (11, 12)], br[3])
    return _mk(f"badge_shield_{col}_{charge}", "badge_shield", a, (8, 9), "chest", 16, col, tags=["badge", "watch", "official"], clip=True)


def badge_cross(col: str) -> Part:
    a = Art(18, 18, 181)
    cl = RAMPS["cream"]
    a.fill(a.mask().rect(1, 1, 16, 16), cl, tex="linen", radius=1.6, base=0.62)
    r = RAMPS[col]
    a.fill(a.mask().rect(7, 3, 10, 14).add(a.mask().rect(3, 7, 14, 10)), r, radius=1.0, base=0.6)
    return _mk(f"badge_cross_{col}", "badge_cross", a, (9, 9), "chest", 18, col, tags=["badge", "physician", "medic"], clip=True)


def badge_disc(emblem: str) -> Part:
    br = RAMPS["brass"]
    a = Art(16, 16, 191)
    a.fill(a.mask().ellipse(8, 8, 7, 7), br, radius=2, base=0.6)
    a.fill(a.mask().ellipse(8, 8, 4.5, 4.5), RAMPS["leather"], radius=1.2, base=0.6)
    if emblem == "hammer":
        a.line([(8, 5), (8, 11)], br[3]), a.line([(5, 5), (10, 5)], br[4])
    elif emblem == "quill":
        a.line([(5, 11), (11, 5)], RAMPS["cream"][3]), a.px(11, 5, RAMPS["cream"][4])
    elif emblem == "flask":
        a.fill(a.mask().rect(7, 4, 8, 6).add(a.mask().poly([(8, 6), (11, 12), (5, 12)])), RAMPS["teal"], radius=0.8)
    elif emblem == "wheat":
        a.line([(8, 5), (8, 12)], br[4]), a.dots([(7, 6), (9, 6), (7, 8), (9, 8)], br[4])
    else:
        a.dots([(6, 6), (9, 6), (7, 9), (10, 9)], br[4])
    return _mk(f"badge_disc_{emblem}", "badge_disc", a, (8, 8), "chest", 16, emblem, tags=["badge", "guild", emblem], clip=True)


def studs(sz: int) -> Part:
    br = RAMPS["brass"]
    a = Art(sz * 5 + 4, 8, 201)
    for i in range(sz):
        a.fill(a.mask().ellipse(3 + i * 5 + 1, 4, 2.2, 2.2), br, radius=0.9, base=0.62)
    return _mk(f"studs_{sz}", "studs", a, (a.w // 2, 4), "chest", a.w, tags=["studs", "metal", "cover"], clip=True)


def ink(kind: str) -> Part:
    """Ink stains on cloth (translucent): blots and a smeared finger line."""
    from marks import _blob
    a = Art(26, 22, 301 + len(kind))
    a.inside = False
    c = (28, 30, 70)
    if kind == "blot":
        _blob(a, 12, 10, 7, 5, c, 200, 91, 0.6)
        _blob(a, 20, 16, 2, 2, c, 200, 92, 0.3)
    else:
        a.line([(3, 14), (10, 9), (21, 7)], c)
        a.line([(4, 15), (11, 10), (21, 8)], (46, 46, 96))
        a.px(9, 17, c), a.px(14, 15, c)
    p = _mk(f"ink_{kind}", "ink", a, (13, 11), "chest", 26, tags=["ink", "scholar", "stain"], clip=True)
    p.alpha_part = True
    return p


# ------------------------------------------------------------------------------------------------ catalogue


def build() -> list[Part]:
    o: list[Part] = []
    for c in ("linen", "cream", "sand", "wine"):
        o.append(collar_fold(c))
    for c in ("linen", "cream"):
        o.append(collar_ruff(c))
    for c, t in (("moss", "leather"), ("wine", "brass"), ("indigo", "linen"), ("brown", "cream")):
        o.append(collar_band(c, t))
        o.append(neckline_v(c, t))
    for c in ("leather", "cream", "linen"):
        o.append(laces(c))
    for c, n in (("brass", 5), ("bone", 5), ("brass", 7), ("bone", 3)):
        o.append(buttons(c, n))
    for sz in SIZES:
        for c, e in (("wine", "cross"), ("indigo", "tower"), ("moss", "stripe"), ("ochre", "chevron"), ("charcoal", "plain"), ("wine", "plain")):
            o.append(tabard(c, e, sz))
        for c in ("linen", "leather", "cream", "grey"):
            o.append(apron(c, sz, pocket=(c != "grey")))
        for c, flip, v in (("leather", False, False), ("brown", True, True), ("leather", True, False), ("brown", False, True)):
            o.append(bandolier(c, sz, flip, v))
        for c in ("leather", "brown"):
            o.append(straps_pair(c, sz))
            o.append(belt(c, sz))
        for c, f in (("wine", False), ("ochre", True), ("indigo", False)):
            o.append(sash(c, sz, f))
        for c in ("wine", "moss", "charcoal", "brown", "indigo", "grey"):
            o.append(cloak_back(c, sz))
            o.append(cloak_front(c, sz))
        for c in ("wine", "moss", "indigo", "charcoal"):
            o.append(mantle(c, sz))
        for c in ("leather", "brown", "wine", "indigo", "charcoal", "moss"):
            o.append(brigandine(c, sz))
        for c in ("linen", "sand", "brown", "grey", "wine", "indigo", "moss"):
            o.append(gambeson_vest(c, sz))
        for k in ("brass", "silver"):
            o.append(chain_office("medallion" if k == "brass" else "silver", sz))
        o.append(chain_office("double", sz))
        o.append(chain_office("plain", sz))
    for c in ("wine", "moss", "indigo", "charcoal", "ochre", "linen", "grey"):
        o.append(scarf_wrap(c, True))
        o.append(scarf_wrap(c, False))
    for c in ("charcoal", "wine", "linen", "moss", "indigo", "ochre"):
        for hw in (40, 46, 52):
            o.append(scarf_cover(c, hw))
    for k in ("cross", "gem", "key", "moon"):
        o.append(pendant(k))
    for c in ("leather", "brown"):
        o.append(plague_beak(c))
    for c, ch in (("wine", "tower"), ("indigo", "tower"), ("moss", "none"), ("charcoal", "tower"), ("wine", "none")):
        o.append(badge_shield(c, ch))
    for c in ("red", "green"):
        o.append(badge_cross(c))
    for e in ("hammer", "quill", "flask", "wheat", "star"):
        o.append(badge_disc(e))
    o += [quilt("vertical"), quilt("diamond"), ink("blot"), ink("smear")]
    for c, w, h in (("leather", 16, 14), ("brown", 24, 10), ("linen", 16, 14), ("wine", 20, 12), ("moss", 20, 12)):
        o.append(patch(c, w, h, "leather" if c in ("leather", "brown") else "cloth"))
    for n in (3, 5, 7):
        o.append(studs(n))
    for c in ("iron", "steel", "leather"):
        o.append(pauldron(c))
    return o


def sheet(parts: list[Part], out) -> None:
    """Two sections: small parts cropped around their landmark, large parts shown on the full mannequin."""
    from PIL import Image
    import sheets
    cw, ch, ay = 190, 250, 56
    small, large = [], []
    for p in parts:
        if p.size in ("S", "L"):
            continue
        hw = p.width if p.style == "scarf_cover" else max(36, round(p.width / 3.1)) if p.size else 42
        full = sheets.worn(p, hw, cw, ch, cw // 2, ay)
        if p.img.height <= 60 and p.style != "mantle":
            ly = {"neck": 1.12, "nose": 0.62, "chest": 1.55}.get(p.landmark, 1.3) * hw + ay
            y0 = int(max(0, ly - 62))
            small.append((full.crop((0, y0, cw, y0 + 120)), p.id))
        else:
            large.append((full, p.id))
    s1 = sheets.sheet(small, 10, 2)
    s2 = sheets.sheet(large, 10, 2)
    W = max(s1.width, s2.width)
    img = Image.new("RGBA", (W, s1.height + s2.height), sheets.BG + (255,))
    img.paste(s1, (0, 0))
    img.paste(s2, (0, s1.height))
    img.save(out / "garments_sheet.png")
