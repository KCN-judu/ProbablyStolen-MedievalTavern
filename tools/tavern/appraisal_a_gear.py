"""Appraisal close-ups: the armour add-on plates, the blade add-ons and the small engraved marks on the prosthetic hands.

Armour plate: iron breastplate (steel), quilted gambeson (carbon), brass fan lames (gold). Blade: a forged sword blade with
a bevelled edge, a fuller and a tang plate (a curved brass falchion with teeth for gold). The marks (a lightning bolt with
"EMG" or "EMG+", a nerve cell with "NI") are punched, inlaid or enamelled into the hand, in the same places as the game's.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from PIL import Image

import font
from appraisalkit_a import (
    BLACKENED, BRASS, DARKWOOD, GOLD, STEEL, Mask, distance_inside, poly_mask, scratches, solid, streaks,
)
from palette import LEATHER, PARCHMENT, SHADOW, SOOT, WINE
from pix import Color, Pix, Ramp

W, H = 456, 402
FLAT = dict(relief=1.15, gain=1.3, bias=-0.22, dither=False)


def sawtooth(v: float, period: float) -> float:
    return (v / period) % 1.0


# ------------------------------------------------------------------ armour

def armour(style: str, oy: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    canvas = Pix(W, H)
    p = Pix(120, 190, seed=seed)
    ox_l = 4                                      # local margin so outlines never clip; picture origin is (160 - 4)
    def S(pts):
        return [(x + ox_l, y + 2) for x, y in pts]

    ramp = {"steel": STEEL, "carbon": BLACKENED, "gold": GOLD}[style]
    rim = {"steel": (24, 22, 32), "carbon": (12, 10, 16), "gold": (62, 34, 24)}[style]
    trim = BRASS if style != "gold" else STEEL

    top_pts = S([(12, 3), (46, 3), (55, 9), (64, 3), (98, 3), (108, 9), (107, 41), (99, 39), (99, 70), (86, 77), (26, 77), (12, 70),
                 (12, 39), (4, 41), (3, 9)])
    belt_pts = S([(25, 127), (99, 127), (101, 150), (85, 165), (79, 176), (46, 176), (40, 165), (25, 150)])
    cx = 55 + ox_l

    def top_h(x: int, y: int) -> float:
        if style == "steel":
            # a rolled breastplate with a central ridge
            c = 1.0 - ((x - cx) / 52.0) ** 2
            return (10.0 * math.sqrt(c) if c > 0 else 0.0) - abs(x - cx) * 0.16 + (2.5 if y < 12 else 0) - (2.0 if 56 <= y - 2 < 60 else 0)
        if style == "carbon":
            # a quilted pad: puffs between diagonal stitch lines
            a, b = (x + y) * math.pi / 10.0, (x - y) * math.pi / 10.0
            c = 1.0 - ((x - cx) / 52.0) ** 2
            return (4.0 * math.sqrt(c) if c > 0 else 0.0) + 1.7 * math.cos(a) * math.cos(b)
        ang = math.atan2(y - (62 + 2), x - cx)
        return 4.0 * sawtooth(ang, 0.16) + max(0.0, 1.0 - ((x - cx) / 52.0) ** 2) * 3

    for pts, hf in ((top_pts, top_h),):
        m = poly_mask(pts)
        d = distance_inside(m)
        solid(p, m, lambda x, y: min(d.get((x, y), 0), 3) * 1.2 + hf(x, y), ramp, rim, **FLAT)
    top_mask = poly_mask(top_pts)

    # shoulder lames: three stacked strips hanging from each side flap
    for side in (-1, 1):
        for k in range(3):
            if side < 0:
                strip = S([(3, 10 + k * 10), (13, 10 + k * 10), (13, 22 + k * 10), (4, 22 + k * 10 - (0 if k == 2 else 0))])
            else:
                strip = S([(98, 10 + k * 10), (108, 10 + k * 10), (107, 22 + k * 10), (98, 22 + k * 10)])
            sm = poly_mask(strip) & top_mask
            sd = distance_inside(sm)
            solid(p, sm, lambda x, y: min(sd.get((x, y), 0), 2) * 1.5 + 1.0, ramp, rim, **FLAT)

    if style == "steel":
        for xx in (22, 88):                          # brass-inlaid trim lines either side of the ridge
            for y in range(14, 68):
                p.px(xx + ox_l, y + 2, BRASS[3] if y % 4 else BRASS[2])
                p.px(xx + ox_l + 1, y + 2, SHADOW)
        for y in range(70, 75):
            for x in range(22, 90):
                if (x + ox_l, y + 2) in top_mask:
                    p.px(x + ox_l, y + 2, BRASS[3] if y == 72 else (BRASS[1] if y > 72 else BRASS[2]))
        streaks(p, top_mask, rng, 40, (STEEL[4], STEEL[1]), True, (6, 24))
        for x in range(12, 100, 9):
            for y in (9, 52):
                p.rect(x + ox_l, y + 2, 2, 2, BRASS[3])
                p.px(x + ox_l, y + 2, BRASS[4])
                p.px(x + ox_l + 1, y + 3, BRASS[0])
        for x in range(14, 98):
            p.px(x + ox_l, 60 + 2, rim)
            p.px(x + ox_l, 59 + 2, STEEL[4])
    elif style == "carbon":
        for x in range(12, 100, 8):                  # brass studs at the quilt's seams
            for y in (8, 70):
                p.rect(x + ox_l, y + 2, 2, 2, BRASS[3])
                p.px(x + ox_l, y + 2, BRASS[4])
        for y in range(3, 77):
            p.px(cx - 1, y + 2, rim) if (y % 3) else None
        for dy in (8, 36, 60):
            for x in range(18, 94):
                p.px(x + ox_l, dy + 2, LEATHER[1]) if (x // 3) % 2 and (x + ox_l, dy + 2) in top_mask else None
    else:
        pass

    belt = poly_mask(belt_pts)
    bd = distance_inside(belt)

    def belt_h(x: int, y: int) -> float:
        row = 0.0 if y < 150 + 2 else 1.0
        lame = sawtooth(y - 129, 14.0) * 3.2
        c = 1.0 - ((x - cx) / 38.0) ** 2
        return min(bd.get((x, y), 0), 3) * 1.1 + lame + (3.0 * math.sqrt(c) if c > 0 else 0.0)
    solid(p, belt, belt_h, ramp, rim, **FLAT)
    # buckle: a diamond (gold), a tab (steel), a strap with studs (carbon)
    by = 150 + 2
    if style == "gold":
        dm = poly_mask([(cx, by - 14), (cx + 9, by), (cx, by + 14), (cx - 9, by)])
        dd = distance_inside(dm)
        solid(p, dm, lambda x, y: min(dd.get((x, y), 0), 4) * 1.2, PARCHMENT, rim, **FLAT)
    elif style == "steel":
        tab = poly_mask(S([(44, 142), (66, 142), (64, 168), (46, 168)]))
        td = distance_inside(tab)
        solid(p, tab, lambda x, y: min(td.get((x, y), 0), 3) * 1.3 + 1, STEEL, rim, **FLAT)
        for y in range(144, 164, 4):
            p.rect(cx - 1, y + 2, 3, 2, BRASS[3])
    else:
        for yy in (136, 160):
            for x in range(26, 100):
                if (x + ox_l, yy + 2) in belt:
                    p.vline(x + ox_l, yy + 2, 4, LEATHER[2] if (x // 6) % 2 else LEATHER[1])
        for x in range(32, 98, 12):
            p.px(x + ox_l, 146 + 2, BRASS[3])
        p.frame(cx - 5, 143 + 2, 10, 12, BRASS[2])
        p.frame(cx - 4, 144 + 2, 8, 10, BRASS[4])

    canvas.paste(p, 160 - ox_l, oy - 3)
    return canvas.im


# ------------------------------------------------------------------ blades

def blade(style: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    canvas = Pix(W, H)
    p = Pix(96, 244, seed=seed)
    ox, oy = 108, 41
    s = 4

    ramp = {"steel": STEEL, "carbon": BLACKENED, "gold": GOLD}[style]
    rim = {"steel": (24, 22, 32), "carbon": (12, 10, 16), "gold": (62, 34, 24)}[style]
    if style == "gold":
        pts = [(24, 0), (30, 12), (38, 22), (46, 44), (50, 90), (58, 150), (68, 196), (77, 231), (40, 231), (30, 205), (14, 160),
               (6, 120), (6, 84), (5, 50), (10, 30), (16, 14)]
    else:
        pts = [(20, 0), (32, 22), (44, 70), (57, 150), (68, 205), (77, 231), (40, 231), (26, 195), (10, 140), (2, 80), (2, 45), (8, 22)]
    pts = [(x + s, y + s - (1 if y else 0) + (1 if y == 0 else 0)) for x, y in pts]
    m = poly_mask(pts)
    d = distance_inside(m)

    def right_x(y: int) -> float:
        return 20.0 + y * 0.247 + s

    def fuller_x(y: int) -> float:
        return right_x(y) - 17

    def h(x: int, y: int) -> float:
        dd = d.get((x, y), 0.0)
        left = x < right_x(y) - 30
        edge = min(dd, 8.0) * 0.6 if left else 4.0
        fd = abs(x - fuller_x(y))
        groove = -3.2 * (1.0 - (fd / 4.5) ** 2) if (y > 26 and fd < 4.5 and y < 205) else 0.0
        spine = min(dd, 3.0) * 0.5 if x > right_x(y) - 6 else 0.0
        return edge + groove + spine + (1.2 if style == "gold" else 0)
    solid(p, m, h, ramp, rim, **FLAT)
    # a bright honed line right on the edge and a long glint down the flat
    for y in range(6, 228):
        for x in range(0, 90):
            if (x, y) in m and (x - 1, y) not in m:
                p.px(x, y, ramp[-1])
                if style != "carbon":
                    p.px(x + 1, y, ramp[-2])
                break
    for y in range(24, 200, 2):
        x = round(fuller_x(y)) - 3
        if (x, y) in m and y % 6 < 4:
            p.px(x, y, ramp[-1] if style != "carbon" else ramp[-2])
    # tang plate and guard stub at the foot, riveted
    tang = poly_mask([(x + s, y + s) for x, y in ((56, 160), (66, 154), (78, 200), (78, 231), (66, 231), (60, 200))]) & m
    td = distance_inside(tang)
    solid(p, tang, lambda x, y: min(td.get((x, y), 0), 3) * 1.3 + 1, DARKWOOD if style != "carbon" else BLACKENED, rim, **FLAT)
    for yy in (182, 214):
        p.rect(66 + s, yy + s, 3, 3, BRASS[3])
        p.px(66 + s, yy + s, BRASS[4])
        p.px(68 + s, yy + 2 + s, BRASS[0])
    if style == "gold":
        # three bone teeth set along the back, and a notch bitten out where they end
        for ty in (150, 176, 202):
            tx = round(right_x(ty)) - 4
            for k in range(6):
                for j in range(-(5 - k) // 2, (5 - k) // 2 + 1):
                    p.px(tx + k + 1, ty + s + j + k // 2, PARCHMENT[3 if j <= 0 else 1])
    else:
        for y in range(60, 190, 3):
            x = round(fuller_x(y)) + 5
            if (x, y) in m:
                p.px(x, y, ramp[1])
    scratches(p, m, rng, 0, ramp[1])
    canvas.paste(p, ox - s, oy - s)
    return canvas.im


# ------------------------------------------------------------------ engraved marks

BOLT = ((0.95, 0.0), (0.05, 0.56), (0.48, 0.56), (0.05, 1.0), (1.0, 0.40), (0.56, 0.40), (1.0, 0.0))


def bolt_set(x: int, y: int, w: int, h: int) -> Mask:
    pts = [(x + round(u * (w - 1)), y + round(v * (h - 1))) for u, v in BOLT]
    return poly_mask(pts)


def plus_set(x: int, y: int, n: int) -> Mask:
    out: Mask = {(x + n // 2, y + j) for j in range(n)} | {(x + i, y + n // 2) for i in range(n)}
    return out


def text_set(text: str, x: int, y: int) -> Mask:
    tmp = Pix(60, 20)
    font.write(tmp, 0, 0, text, (255, 255, 255))
    return {(x + i, y + j) for i in range(60) for j in range(20) if tmp.get(i, j)[3]}


def neuron_set(x: int, y: int, size: int) -> Mask:
    tmp = Pix(size, size)
    c = (255, 255, 255)
    k = size / 23.0
    cx, cy = round(10 * k) + (1 if size < 16 else 2), round(11 * k)
    r = max(1, round(3 * k))
    tmp.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, c)
    arms = ((-1, -1, 5), (1, -1, 5), (-1, 1, 5), (1, 1, 5), (-1, 0, 5), (0, -1, 5))
    for dx, dy, ln in arms:
        n = max(2, round(ln * k * 1.6))
        ex, ey = cx + dx * (r + n), cy + dy * (r + n)
        tmp.line(cx, cy, ex, ey, c)
        if size >= 16:
            tmp.px(ex + dy, ey - dx, c)
            tmp.px(ex - dy, ey + dx, c)
    # a long axon curling to the lower right
    if size >= 16:
        pts = [(cx + 3, cy + 3), (cx + 6, cy + 6), (cx + 9, cy + 9), (cx + 11, cy + 10), (size - 1, size - 1)]
    else:
        pts = [(cx + 2, cy + 2), (cx + 4, cy + 5), (size - 1, size - 1)]
    for a, b in zip(pts, pts[1:]):
        tmp.line(a[0], a[1], b[0], b[1], c)
    return {(x + i, y + j) for i in range(size) for j in range(size) if tmp.get(i, j)[3]}


# bbox top-left and size of each mark in the originals, by (family, variant)
MARKS = {
    "full_emg": (28, 12), "full_emgp": (34, 12), "full_ni": (30, 14),
    "sym_emg": (13, 21), "sym_emgp": (21, 22), "sym_ni": (23, 23),
}


def mark_cells(kind: str) -> tuple[Mask, int, int]:
    w, h = MARKS[kind]
    out: Mask = set()
    if kind.startswith("full"):
        if kind.endswith("ni"):
            out |= neuron_set(0, 1, 12)
            out |= text_set("NI", 15, 4)
        else:
            out |= bolt_set(0, 0, 7, 12)
            out |= text_set("EMG", 9, 3)
            if kind.endswith("p"):
                out |= plus_set(w - 6, 0, 5)
    else:
        if kind.endswith("ni"):
            out |= neuron_set(0, 0, 23)
        else:
            out |= bolt_set(0, h - 21, 12, 20)
            if kind.endswith("p"):
                out |= plus_set(w - 6, 0, 5)
    return out, w, h


def mark(family: str, kind: str, x0: int, y0: int) -> Image.Image:
    canvas = Pix(W, H)
    cells, w, h = mark_cells(kind)
    if family == "gold" and kind == "sym_emgp":
        h = 21
    ink, lip = {
        "steel": ((40, 38, 52), STEEL[5]),
        "carbon": (BRASS[3], BRASS[1]),
        "gold": ((70, 36, 26), GOLD[5]),
    }[family]
    for (x, y) in cells:                           # the lit lip first, one pixel down and right of the cut
        if (x + 1, y + 1) not in cells and x + 1 < w and y + 1 < h:
            canvas.px(x0 + x + 1, y0 + y + 1, lip)
    for (x, y) in cells:
        if y < h:
            canvas.px(x0 + x, y0 + y, ink)
    return canvas.im


# bbox origins (x0, y0) of each file, from the originals' layout
ORIGINS = {
    "1steel_int_full_emg": ("steel", "full_emg", 204, 255), "1steel_int_full_emgp": ("steel", "full_emgp", 204, 255),
    "1steel_int_full_ni": ("steel", "full_ni", 201, 254), "1steel_int_syml_emg": ("steel", "sym_emg", 214, 252),
    "1steel_int_syml_emgp": ("steel", "sym_emgp", 214, 251), "1steel_int_syml_ni": ("steel", "sym_ni", 209, 252),
    "2carbon_int_full_emg": ("carbon", "full_emg", 203, 255), "2carbon_int_full_emgp": ("carbon", "full_emgp", 203, 255),
    "2carbon_int_full_ni": ("carbon", "full_ni", 201, 254), "2carbon_int_symboll_emg": ("carbon", "sym_emg", 214, 252),
    "2carbon_int_symboll_emgp": ("carbon", "sym_emgp", 214, 251), "2carbon_int_symboll_ni": ("carbon", "sym_ni", 209, 252),
    "3gold_interface_emg": ("gold", "full_emg", 204, 239), "3gold_interface_emgp": ("gold", "full_emgp", 204, 239),
    "3gold_interface_ni": ("gold", "full_ni", 201, 238), "3gold_interface_symbol_emg": ("gold", "sym_emg", 214, 232),
    "3gold_interface_symbol_emgp": ("gold", "sym_emgp", 214, 232), "3gold_interface_symbol_ni": ("gold", "sym_ni", 209, 232),
}


def _mark(family: str, kind: str, x0: int, y0: int) -> Callable[[], Image.Image]:
    return lambda: mark(family, kind, x0, y0)


ASSETS: dict[str, Callable[[], Image.Image]] = {}
for _name, (_fam, _kind, _x, _y) in ORIGINS.items():
    ASSETS[f"{_name}.456x402.png"] = _mark(_fam, _kind, _x, _y)
for _fam, _prefix, _oy in (("steel", "1steel", 147), ("carbon", "2carbon", 147), ("gold", "3gold", 139)):
    ASSETS[f"{_prefix}_addon_1armor.456x402.png"] = (lambda f=_fam, o=_oy: armour(f, o, 5))
    ASSETS[f"{_prefix}_addon_2blade.456x402.png"] = (lambda f=_fam: blade(f, 9))
