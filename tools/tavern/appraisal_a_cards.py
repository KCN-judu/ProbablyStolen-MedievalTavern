"""Appraisal close-ups: the four cards, the Red Imp plaque, the DA badge in four variants and the stamp-die chip in four states.

Series differences kept: the DA badge is correct (red, cream rim, slashed lettering), incorrect1 (no slash), incorrect2
(green field) and incorrect3 (colours inverted). The chip is correct (bright brass), colour (dull bronze), damaged (left
third corroded through) and cracked (a split near the right edge).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from PIL import Image

import font
from appraisalkit_a import (
    BRASS, GOLD, STEEL, Mask, capsule, distance_inside, dome, ellipse_mask, plate_rect, poly_mask, rect_mask, solid,
    squiggle_line,
)
from palette import FLAME, LEATHER, MOSS, NIGHT, PALE_WOOD, PARCHMENT, SHADOW, SOOT, WINE
from pix import Color, Pix, Ramp


def embossed(p: Pix, x: int, y: int, text: str, ink: Color, lip: Color, shade: Color, scale: int) -> None:
    font.write(p, x + 1, y + 1, text, lip, scale)
    font.write(p, x - 1, y - 1, text, shade, scale)
    font.write(p, x, y, text, ink, scale)


# ------------------------------------------------------------------ plain cards

def tally_card() -> Image.Image:
    """A pale oak tally board with a dark leather band across it (where the magnetic stripe of the game's card sits)."""
    p = Pix(137, 96, seed=21)
    m = plate_rect(p, 0, 0, 137, 96, PALE_WOOD, SOOT[0], bevel=3, corner=5, gain=1.15, bias=-0.1, dither=False)
    rng = p.rng
    for _ in range(90):                                    # grain along the board
        x, y = rng.randint(3, 130), rng.randint(3, 92)
        for i in range(rng.randint(6, 22)):
            if (x + i, y) in m and 3 < x + i < 133:
                p.px(x + i, y, PALE_WOOD[1] if rng.random() < 0.6 else PALE_WOOD[4])
    for y in range(17, 35):                                # the band
        tone = LEATHER[0] if y in (17, 34) else (LEATHER[1] if y < 30 else LEATHER[0])
        p.hline(2, y, 133, tone)
    p.hline(2, 18, 133, LEATHER[2])
    p.hline(2, 35, 133, PALE_WOOD[4])
    for x in range(8, 132, 12):                            # iron nails
        p.rect(x, 24, 3, 3, STEEL[2])
        p.px(x, 24, STEEL[4])
    for x, y in ((8, 8), (125, 8), (8, 85), (125, 85)):
        p.rect(x, y, 3, 3, BRASS[2])
        p.px(x, y, BRASS[4])
    return p.im


def parchment_card() -> Image.Image:
    p = Pix(194, 116, seed=22)
    m = plate_rect(p, 0, 0, 194, 116, PARCHMENT, (92, 70, 48), bevel=2, corner=8, relief=0.7, gain=1.0, bias=0.35, dither=False)
    rng = p.rng
    for _ in range(260):
        x, y = rng.randint(3, 190), rng.randint(3, 112)
        if (x, y) in m:
            p.px(x, y, PARCHMENT[3] if rng.random() < 0.7 else PARCHMENT[2])
    p.hline(10, 12, 174, (128, 100, 70))                   # the ruled head line
    p.hline(10, 13, 174, PARCHMENT[2])
    return p.im


def card_back() -> Image.Image:
    p = Pix(139, 87, seed=23)
    green = MOSS
    m = plate_rect(p, 0, 0, 139, 87, green, SOOT[0], bevel=3, corner=4, relief=0.8, gain=1.0, bias=0.15, dither=False)
    rng = p.rng
    for _ in range(300):
        x, y = rng.randint(2, 136), rng.randint(2, 84)
        if (x, y) in m:
            p.px(x, y, green[1] if rng.random() < 0.5 else green[3])
    # a notch cut at the head, edged in brass
    for y in range(1, 22):
        half = (21 - y) * 2 if False else y
        for x in range(69 - half - 18, 70 + half + 18):
            pass
    tri = poly_mask([(40, 2), (99, 2), (69, 36)])
    td = distance_inside(tri)
    solid(p, tri, lambda x, y: -min(td.get((x, y), 0), 3), green, SOOT[0], relief=1.0, gain=1.0, bias=-0.35, dither=False)
    for k in range(34):
        p.px(42 + k * 57 // 34, 4 + k, BRASS[3])
        p.px(97 - k * 57 // 34, 4 + k, BRASS[2])
    # the serial, stamped deep
    embossed(p, 12, 47, "51189", MOSS[0], MOSS[3], SOOT[0], 4)
    for x in range(8, 132, 6):                             # stitching round the edge
        p.px(x, 82, PARCHMENT[2])
        p.px(x, 4 if x < 36 or x > 102 else 40, PARCHMENT[2]) if x < 36 or x > 102 else None
    return p.im


def card_wild() -> Image.Image:
    p = Pix(137, 85, seed=24)
    base = NIGHT
    m = plate_rect(p, 0, 0, 137, 85, base, SOOT[0], bevel=2, corner=2, relief=0.6, gain=1.0, bias=0.05, dither=False)
    # a pale diagonal sheen across the lower half
    for y in range(85):
        for x in range(137):
            if (x, y) in m and y > 85 - (x * 0.45) - 8 and y > 40:
                p.px(x, y, base[3] if y > 85 - (x * 0.45) else base[2])
    for y in range(85):
        x = round((85 - y - 8) / 0.45) if False else None
    # crown: a band and five points with orbs
    cx = 68
    band = poly_mask([(cx - 25, 38), (cx + 25, 38), (cx + 23, 29), (cx + 28, 15), (cx + 17, 24), (cx + 11, 8), (cx + 5, 22), (cx, 5), (cx - 5, 22),
                      (cx - 11, 8), (cx - 17, 24), (cx - 28, 15), (cx - 23, 29)])
    bd = distance_inside(band)
    solid(p, band, lambda x, y: min(bd.get((x, y), 0), 3) * 1.3 + (38 - y) * 0.06, BRASS, SHADOW, relief=1.2, gain=1.2, bias=-0.1, dither=False)
    p.hline(cx - 22, 34, 45, BRASS[1])
    for dx in (-28, -11, 0, 11, 28):
        yy = {-28: 14, -11: 7, 0: 4, 11: 7, 28: 14}[dx]
        p.rect(cx + dx - 1, yy - 1, 3, 3, FLAME[3])
        p.px(cx + dx - 1, yy - 1, FLAME[4])
    for dx in (-14, 0, 14):
        p.px(cx + dx, 36, WINE[3])
        p.px(cx + dx + 1, 36, WINE[1])
    # corner flourishes: a bracket with a curl
    for sx, sy in ((6, 6), (130, 6), (6, 78), (130, 78)):
        dx = 1 if sx < 60 else -1
        dy = 1 if sy < 40 else -1
        for k in range(10):
            p.px(sx + dx * k, sy, BRASS[2])
            p.px(sx, sy + dy * k, BRASS[2])
        p.px(sx + dx * 2, sy + dy * 2, BRASS[3])
        p.px(sx + dx * 4, sy + dy * 3, BRASS[1])
        p.px(sx + dx * 3, sy + dy * 4, BRASS[1])
    embossed(p, 50, 56, "8376", BRASS[3], SOOT[0], BRASS[0], 2)
    return p.im


# ------------------------------------------------------------------ Red Imp plaque

IMP: Ramp = ((60, 14, 22), (110, 24, 32), (158, 42, 40), (204, 76, 56), (236, 124, 84))


def red_imp() -> Image.Image:
    w, h = 278, 176
    p = Pix(w, h, seed=31)
    m = plate_rect(p, 0, 0, w, h, WINE, SOOT[0], bevel=4, corner=5, relief=0.9, gain=1.0, bias=-0.32, dither=False)
    rng = p.rng
    for _ in range(500):
        x, y = rng.randint(4, w - 5), rng.randint(4, h - 5)
        p.px(x, y, WINE[1] if rng.random() < 0.5 else WINE[3])
    # brass border line and corner studs
    p.frame(7, 7, w - 14, h - 14, BRASS[1])
    p.frame(8, 8, w - 16, h - 16, BRASS[3])
    for x, y in ((14, 14), (w - 17, 14), (14, h - 17), (w - 17, h - 17)):
        p.ellipse(x, y, 4, 4, BRASS[2])
        p.px(x, y, BRASS[4])
    # medallion with the imp: night sky, flames at the foot, a bat-winged red head
    cx, cy, r = 139, 56, 40
    disc = ellipse_mask(cx, cy, r, r)
    solid(p, disc, dome(cx, cy, r, r, 10), NIGHT, SHADOW, relief=0.5, gain=1.0, bias=-0.25, dither=True)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x, y) in disc and y > cy + 14:
                lick = (y - (cy + 14)) / 26.0 + 0.5 * math.sin(x * 0.6) * 0.3
                if lick > 0.28 + 0.25 * abs(math.sin(x * 0.45)):
                    p.px(x, y, FLAME[1] if lick < 0.7 else (FLAME[2] if lick < 0.95 else FLAME[3]))
    for sx in (-1, 1):                                      # wings
        wing = poly_mask([(cx + sx * 12, cy - 4), (cx + sx * 36, cy - 26), (cx + sx * 30, cy - 8), (cx + sx * 38, cy + 4),
                          (cx + sx * 26, cy + 4), (cx + sx * 28, cy + 14), (cx + sx * 12, cy + 10)])
        wd = distance_inside(wing)
        solid(p, wing, lambda x, y: min(wd.get((x, y), 0), 2) * 1.2, IMP, SHADOW, relief=1.0, dither=False)
    head = ellipse_mask(cx, cy, 15, 14)
    solid(p, head, dome(cx, cy, 15, 14, 14), IMP, SHADOW, relief=1.0, gain=1.2, bias=-0.1, dither=False)
    for sx in (-1, 1):                                      # horns and ears
        for k in range(10):
            hx = cx + sx * (8 + k // 2)
            hy = cy - 12 - k
            p.rect(hx - 1, hy, 3, 2, PARCHMENT[3] if k < 7 else PARCHMENT[1])
            p.px(hx - 1, hy, SHADOW)
        p.poly([(cx + sx * 14, cy - 3), (cx + sx * 26, cy - 8), (cx + sx * 15, cy + 4)], IMP[2])
    for sx in (-1, 1):                                      # eyes and grin
        p.rect(cx + sx * 6 - 2, cy - 4, 4, 3, FLAME[4])
        p.px(cx + sx * 6 - 1, cy - 3, SHADOW)
    p.hline(cx - 7, cy + 5, 15, SHADOW)
    for k in range(-6, 7, 3):
        p.px(cx + k, cy + 6, PARCHMENT[4])
    p.hline(cx - 6, cy + 7, 13, SHADOW)
    p.px(cx - 1, cy + 1, IMP[1])
    p.px(cx + 1, cy + 1, IMP[1])
    # lettering on a ribbon of oak
    p.rect(52, 106, 174, 28, (60, 34, 26))
    p.frame(52, 106, 174, 28, SHADOW)
    p.hline(53, 107, 172, (110, 70, 44))
    s = 3
    tx = (w - font.width("RED IMP", s)) // 2
    embossed(p, tx, 112, "RED IMP", PARCHMENT[4], SHADOW, PARCHMENT[0], s)
    tx = (w - font.width("8815", s)) // 2
    embossed(p, tx, 142, "8815", BRASS[4], SHADOW, BRASS[0], s)
    return p.im


# ------------------------------------------------------------------ DA badge

RED_F: Color = (156, 52, 54)
CREAM: Color = (224, 206, 152)
GREEN_F: Color = (92, 112, 70)


def badge(field: Color, ink: Color, rim: Color, slash: bool) -> Image.Image:
    p = Pix(265, 104, seed=41)
    ox, oy, w, h = 169, 30, 29, 26
    outer = rect_mask(ox, oy, w, h, 3)
    for (x, y) in outer:
        p.px(x, y, rim)
    inner = rect_mask(ox + 3, oy + 3, w - 6, h - 6, 1)
    for (x, y) in inner:
        p.px(x, y, field)
    shade = tuple(max(0, c - 36) for c in rim)
    for (x, y) in outer:                                    # a lit rim: bright on the top and left, shaded bottom and right
        if y == oy + h - 1 or x == ox + w - 1:
            p.px(x, y, shade)
    # block letters D and A, drawn by hand
    D = ("#####..", "##..##.", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", "##..##.", "#####..")
    A = (".#####.", "##...##", "##...##", "##...##", "##...##", "#######", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##")
    lx, ly = ox + 4, oy + 7
    for j, row in enumerate(D):
        for i, ch in enumerate(row):
            if ch == "#":
                p.px(lx + i, ly + j, ink)
    for j, row in enumerate(A):
        for i, ch in enumerate(row):
            if ch == "#":
                p.px(lx + 11 + i + 1, ly + j, ink)
    for x, y in ((ox + 4, oy + 4), (ox + w - 5, oy + 4), (ox + 4, oy + h - 5), (ox + w - 5, oy + h - 5)):
        p.px(x, y, BRASS[3])
    if slash:                                               # a sword cut across the lettering
        for k in range(18):
            x, y = ox + 5 + k, oy + 5 + k
            p.px(x, y, field)
            p.px(x + 1, y, field)
            p.px(x + 2, y, ink)
    return p.im


# ------------------------------------------------------------------ chip

def chip(variant: str) -> Image.Image:
    p = Pix(137, 96, seed=51)
    ox, oy = 108, 31
    ramp: Ramp = BRASS
    if variant == "color":
        ramp = ((38, 34, 36), (66, 56, 58), (96, 84, 80), (126, 112, 102), (150, 138, 124))
    w, h = 21, 18
    h = 17
    body = rect_mask(ox, oy, w, h, 3)
    d = distance_inside(body)
    rimc = (62, 30, 30) if variant != "color" else (36, 34, 54)
    solid(p, body, lambda x, y: min(d.get((x, y), 0), 2) * 0.9, ramp, None, relief=1.0, dither=False, gain=1.2, bias=-0.15)
    for (x, y) in body:
        if d[(x, y)] < 1.5:
            p.px(x, y, rimc)
    groove = (62, 30, 30) if variant != "color" else (44, 38, 52)
    cells = [(1, 1, 7, 4), (1, 6, 7, 5), (1, 12, 7, 5), (13, 1, 7, 4), (13, 6, 7, 5), (13, 12, 7, 5), (9, 1, 3, 5), (9, 12, 3, 5)]
    # grooves between the contact pads
    for x in (8, 12):
        for y in range(1, 17):
            if x == 12 and 6 <= y <= 11:
                continue
            p.px(ox + x, oy + y, groove)
    for y in (5, 11):
        p.hline(ox + 1, oy + y, 7, groove)
        p.hline(ox + 13, oy + y, 7, groove)
    p.hline(ox + 9, oy + 6, 3, groove)
    p.hline(ox + 9, oy + 11, 3, groove)
    p.vline(ox + 8, oy + 6, 5, groove)
    # pad highlights
    for (cx0, cy0, cw, ch) in cells:
        p.hline(ox + cx0, oy + cy0, cw, ramp[4])
        p.px(ox + cx0, oy + cy0 + 1, ramp[4])
        p.hline(ox + cx0, oy + cy0 + ch - 1, cw, ramp[1]) if cy0 + ch - 1 not in (5, 11) else None
    p.rect(ox + 1, oy + 1, 3, 2, ramp[4] if variant != "color" else ramp[3])
    if variant == "damaged":
        rng = p.rng
        for y in range(0, h):
            for x in range(0, 8):
                if (ox + x, oy + y) in body:
                    t = rng.random()
                    p.px(ox + x, oy + y, (112, 126, 114) if (x + y) % 5 else (150, 162, 148)) if t < 0.85 else p.px(ox + x, oy + y, (70, 80, 74))
        for y in range(2, 8):
            for x in range(7, 11):
                p.px(ox + x, oy + y + (x - 7), (80, 52, 46) if (x + y) % 3 else (48, 34, 38))
        p.vline(ox + 1, oy - 1, 14, (36, 24, 36))             # a split reaching above the plate
        p.vline(ox + 4, oy + 8, 8, (36, 24, 36))
        p.rect(ox + 4, oy + 8, 3, 3, (36, 26, 32))
    if variant == "cracked":
        for k in range(h + 1):
            x = ox + 17 + (1 if (k // 4) % 2 else 0)
            p.px(x, oy - 1 + k, (60, 30, 40))
            p.px(x + 1, oy - 1 + k, (150, 170, 180) if k % 5 else (200, 215, 220))
    return p.im


# ------------------------------------------------------------------ assets

ASSETS: dict[str, Callable[[], Image.Image]] = {
    "card.137x96.png": tally_card,
    "card.194x116.png": parchment_card,
    "card_rev.139x87.png": card_back,
    "card_wild.137x85.png": card_wild,
    "Red_Imp_2x.278x176.png": red_imp,
    "davre_logo_correct.265x104.png": lambda: badge(RED_F, CREAM, CREAM, True),
    "davre_logo_incorrect1.265x104.png": lambda: badge(RED_F, CREAM, CREAM, False),
    "davre_logo_incorrect2.265x104.png": lambda: badge(GREEN_F, CREAM, CREAM, True),
    "davre_logo_incorrect3.265x104.png": lambda: badge(CREAM, RED_F, RED_F, True),
    "chip color.137x96.png": lambda: chip("color"),
    "chip correct.137x96.png": lambda: chip("correct"),
    "chip damaged.137x96.png": lambda: chip("damaged"),
    "chip_cracked.137x96.png": lambda: chip("cracked"),
}
