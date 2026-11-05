"""People and objects of the undercroft: two cloaked rebels standing at the left, a slumped bandaged beggar against the wall,
a spilled flagon and puddle, a stoneware bottle, a candle on the drain grate, a hanging lantern and the casks along the
wall. Everything that stands on the wet floor throws a dim reflection under itself."""

from __future__ import annotations

import math
import random

from PIL import Image

from fxkit import belly, iron_band, rivet, wood_fill
from mnu_wall_bg import FLOOR_Y, shaft_light
from mnu_wall_kit import (Canvas, Noise, Pt, arc_pts, bayer, cells, empty, grow, hx, inside, lerp, minus, poly_mask, shade,
                          stroke_mask, union)
from pix import Pix

F = [hx(c) for c in ("#0a0610", "#130c1d", "#1d1429", "#2a1e3c", "#3a2c52", "#54456e")]
RIM = [hx(c) for c in ("#2a1630", "#4a2638", "#7a4044", "#b0644a", "#e09452")]
LINEN = [hx(c) for c in ("#3a3042", "#5c5062", "#857a86", "#aaa0a4", "#cdc3bf")]
SKIN = [hx(c) for c in ("#2a1a28", "#4a2e38", "#6e4a4a", "#946a5c")]
CLAYS = [hx(c) for c in ("#2e1a20", "#52302a", "#7c4a34", "#a8683e", "#d0924e")]
WINE_R = [hx(c) for c in ("#1e0a16", "#3e1224", "#6a1c2e", "#962a36", "#c24a48")]
WAX = [hx(c) for c in ("#5a4a52", "#8c7a78", "#bca898", "#e4d4b8")]
FIRE = [hx(c) for c in ("#8a2c1c", "#d0562a", "#f89a3c", "#ffd070", "#fff0b0")]
IRONS = [hx(c) for c in ("#0f0b14", "#1b1520", "#2d2532", "#463d49", "#6a5f68")]
BRASS_L = [hx(c) for c in ("#3a2a12", "#6b4c1c", "#a07a2c", "#d0a847", "#f0d27a")]

Part = tuple[list[Pt], float]


def figure(c: Canvas, parts: list[Part], folds: list[list[Pt]], seed: int, rim_w: float = 1.0, top_light: float = 0.0) -> Image.Image:
    """Paints dark cloth parts in order (each with a base tone), then folds, a lit warm rim on the side toward the windows
    and the shaft, and a darker lower edge where one part overlaps another. Returns the silhouette."""
    n = Noise(5, seed)
    n2 = Noise(11, seed + 1)
    whole = empty()
    masks = []
    for pts, base in parts:
        m = poly_mask(pts)
        masks.append((m, base))
        whole = union(whole, m)
    for m, base in masks:
        ins = inside(m)
        for x, y in cells(m):
            v = base + (n(x, y) - 0.5) * 0.18 + (n2(x, y) - 0.5) * 0.14
            if not ins(x, y + 1) or not ins(x - 1, y + 1):
                v -= 0.12
            c.pa[x, y] = shade(F, v, x, y)
    for fl in folds:
        fm = stroke_mask([fl], 0.75)
        for x, y in cells(fm):
            c.pa[x, y] = shade(F, 0.08 + (n(x, y) - 0.5) * 0.1, x, y)
        for x, y in cells(minus(grow(fm, 1, 0), fm)):
            if inside(whole)(x, y):
                c.pa[x, y] = shade(F, 0.62 + (n(x, y) - 0.5) * 0.2, x, y)
    ins = inside(whole)
    for x, y in cells(whole):
        right = not ins(x + 1, y)
        right2 = not ins(x + 2, y) or not ins(x + 1, y - 1)
        topedge = not ins(x, y - 1)
        if right and (bayer(x + 1, y) < 0.8 * rim_w):
            c.pa[x, y] = shade(RIM, 0.55 + shaft_light(x, y) * 0.3 + (n(x, y) - 0.5) * 0.3, x, y)
        elif topedge and y < top_light and bayer(x, y) < 0.5:
            c.pa[x, y] = shade(RIM, 0.4, x, y)
        elif right2 and bayer(x, y) < 0.3 * rim_w:
            c.pa[x, y] = shade(RIM, 0.25, x, y)
    return whole


def reflection(c: Canvas, mask: Image.Image, base_y: int, depth: int = 16, strength: float = 0.5) -> None:
    """The figure's dim, dithered mirror image in the wet floor under its feet, plus a contact shadow."""
    cols = {(x, y): c.get(x, y) for x, y in cells(mask) if base_y - depth <= y <= base_y}
    for (x, y), col in cols.items():
        ty = 2 * base_y - y + 1
        if 0 <= ty < 360 and (1 - (ty - base_y) / (depth + 2)) * strength > bayer(x, ty):
            if not inside(mask)(x, ty):
                c.put(x, ty, lerp(c.get(x, ty), col, 0.7))


def contact(c: Canvas, cx: float, cy: float, rx: float, ry: float, t: float = 0.75) -> None:
    m = poly_mask(arc_pts(cx, cy, rx, ry, 0, 360, 24))
    c.paint(m, lambda x, y: lerp(c.get(x, y), hx("#07040c"), t) if t > bayer(x, y) or (x - cx) ** 2 / rx ** 2 + (y - cy) ** 2 / ry ** 2 < 0.5 else None)


# ---------------------------------------------------------------------------------------------- the two standing rebels
def rebel_coat(c: Canvas) -> Image.Image:
    """Left: a wide-brimmed hat, a high collar and a knee-length travelling coat, hands pushed into the pockets."""
    contact(c, 76, 334, 36, 5)
    parts: list[Part] = [
        ([(58, 330), (79, 330), (77, 240), (60, 240)], 0.22),                                   # trousers
        ([(80, 332), (99, 326), (94, 240), (79, 240)], 0.30),
        ([(46, 326), (77, 325), (80, 334), (44, 337)], 0.20),                                  # boots
        ([(83, 327), (105, 322), (113, 332), (84, 337)], 0.30),
        ([(62, 88), (86, 88), (97, 96), (100, 130), (103, 190), (107, 244), (98, 254), (86, 250), (70, 254), (56, 246), (57, 190),
          (53, 140), (56, 100)], 0.34),                                                         # coat
        ([(48, 100), (58, 98), (62, 150), (72, 186), (64, 192), (52, 172), (45, 130)], 0.44),    # sleeve to the pocket
        ([(96, 100), (104, 108), (106, 150), (98, 188), (88, 184), (92, 140)], 0.40),
        ([(64, 76), (88, 76), (94, 92), (58, 92)], 0.42),                                      # raised collar
        ([(66, 64), (84, 64), (83, 78), (79, 84), (70, 84), (67, 78)], 0.10),                  # face in the hat's shadow
        ([(60, 59), (62, 48), (70, 44), (80, 44), (85, 48), (86, 59)], 0.40),                  # crown of the hat
        ([(46, 63), (58, 58), (88, 58), (101, 63), (88, 67), (58, 67)], 0.44),                 # brim
    ]
    folds = [[(66, 98), (62, 150), (60, 210), (58, 245)], [(86, 100), (90, 150), (94, 215), (100, 248)], [(76, 96), (76, 150), (76, 250)],
             [(54, 160), (62, 186)], [(98, 150), (92, 186)], [(70, 254), (70, 244)], [(60, 92), (76, 98), (90, 92)], [(61, 59), (85, 59)]]
    m = figure(c, parts, folds, 21, 0.9)
    # a leather belt, a brass buckle, and a glint in the shadowed face
    belt = stroke_mask([[(55, 168), (76, 172), (100, 168)]], 1.2)
    c.paint(belt, lambda x, y: LEATHER_D[1] if y % 2 else LEATHER_D[2])
    c.put(76, 172, BRASS_L[3])
    c.put(77, 172, BRASS_L[2])
    c.put(73, 74, SKIN[2])
    c.put(78, 74, SKIN[2])
    c.put(75, 76, SKIN[1])
    for yy in (66, 67):
        for xx in range(63, 90):
            if bayer(xx, yy) < 0.4:
                c.put(xx, yy, shade(F, 0.05, xx, yy))
    reflection(c, m, 337)
    return m


LEATHER_D = [hx("#2a170f"), hx("#4a2b1a"), hx("#6e4326"), hx("#935e36")]


def rebel_antler(c: Canvas) -> Image.Image:
    """Right: a long hooded cloak, a bone half-mask under a crown of antler and thorn, a brass clasp at the throat."""
    contact(c, 160, 332, 34, 5)
    horns = stroke_mask([
        [(148, 84), (142, 74), (136, 66), (130, 62)], [(142, 74), (141, 64), (139, 56)], [(137, 66), (131, 66)],
        [(164, 82), (170, 72), (176, 64), (184, 60)], [(170, 72), (172, 63), (171, 55)], [(177, 64), (183, 66)],
        [(155, 80), (155, 66), (154, 56)], [(150, 82), (146, 62)], [(160, 82), (164, 62)]], 1.7)
    parts: list[Part] = [
        ([(142, 330), (160, 330), (158, 270), (146, 270)], 0.22),
        ([(164, 330), (182, 326), (180, 270), (160, 270)], 0.30),
        ([(132, 330), (160, 329), (160, 337), (130, 337)], 0.18),
        ([(166, 326), (190, 322), (194, 332), (168, 336)], 0.28),
        ([(140, 118), (166, 118), (182, 130), (189, 190), (193, 246), (200, 282), (166, 290), (130, 286), (136, 244), (136, 190), (131, 140)], 0.32),
        ([(130, 134), (140, 118), (142, 190), (138, 246), (130, 286), (126, 240), (128, 180)], 0.22),   # the cloak's far fold
        ([(138, 108), (144, 86), (153, 78), (163, 82), (170, 94), (172, 114), (164, 124), (146, 124)], 0.38),   # hood
        ([(146, 94), (160, 92), (166, 100), (164, 116), (150, 118), (145, 108)], 0.06),                   # face opening
    ]
    folds = [[(150, 124), (146, 190), (142, 250), (140, 284)], [(172, 130), (176, 190), (182, 250), (188, 284)],
             [(160, 120), (160, 190), (162, 288)], [(150, 84), (148, 100), (150, 118)], [(164, 90), (168, 104), (166, 120)]]
    m = figure(c, parts, folds, 31, 1.0)
    mh = horns
    for x, y in cells(mh):
        c.pa[x, y] = shade(F, 0.30 + (bayer(x, y) - 0.5) * 0.2, x, y)
    for x, y in cells(minus(grow(mh, 1, 0), mh)):
        if bayer(x, y) < 0.55:
            c.put(x, y, shade(RIM, 0.55, x, y))
    # bone half-mask with a single round eye
    mask = poly_mask(arc_pts(158, 104, 7, 9, 0, 360, 20))
    c.paint(mask, lambda x, y: shade(LINEN, 0.28 + 0.22 * (1 - (x - 151) / 14) + (0.1 if y < 100 else -0.05), x, y))
    c.flat(poly_mask(arc_pts(155, 102, 2, 2.4, 0, 360, 12)), shade(F, 0.05, 0, 0))
    c.flat(poly_mask(arc_pts(161, 102, 2, 2.4, 0, 360, 12)), shade(F, 0.05, 0, 0))
    c.put(161, 101, hx("#f89a3c"))
    c.flat(poly_mask([(156, 108), (160, 108), (160, 112), (156, 112)]), shade(F, 0.1, 0, 0))
    # brass clasp and chain at the throat, a leather strap across the chest
    c.flat(poly_mask(arc_pts(160, 128, 3, 3, 0, 360, 10)), BRASS_L[3])
    c.put(159, 127, BRASS_L[4])
    c.put(161, 129, BRASS_L[1])
    strap = stroke_mask([[(146, 134), (158, 160), (176, 196)]], 1.3)
    for x, y in cells(strap):
        c.pa[x, y] = LEATHER_D[1] if (x + y) % 3 else LEATHER_D[0]
    reflection(c, m, 337)
    return m


# ---------------------------------------------------------------------------------------------- the beggar
def beggar(c: Canvas) -> Image.Image:
    """Slumped against the wall: hood fallen forward, one arm wrapped in a blood-stained bandage and laid on a knee,
    legs thrown out along the wet floor."""
    contact(c, 410, 356, 60, 4, 0.9)
    parts: list[Part] = [
        ([(366, 328), (402, 336), (426, 352), (440, 358), (424, 360), (396, 352), (364, 342)], 0.17),                 # far leg
        ([(380, 318), (420, 316), (450, 330), (466, 348), (454, 360), (430, 348), (398, 340), (378, 332)], 0.25),    # near leg
        ([(444, 340), (466, 346), (472, 358), (452, 360)], 0.15),                                                    # boot
        ([(354, 258), (374, 252), (398, 252), (412, 262), (418, 290), (416, 322), (398, 330), (368, 334), (348, 328), (344, 300), (348, 272)], 0.30),
        ([(336, 318), (350, 326), (346, 346), (334, 352), (330, 336)], 0.20),                                       # cloak hem pooled
        ([(398, 262), (414, 266), (426, 286), (432, 306), (420, 311), (410, 296), (398, 282)], 0.38),               # arm on the knee
        ([(372, 248), (372, 232), (380, 223), (392, 222), (399, 232), (401, 246), (397, 258), (378, 258)], 0.34),    # hood
        ([(378, 236), (394, 236), (395, 250), (387, 256), (379, 250)], 0.09),                                       # face shadow
    ]
    folds = [[(372, 262), (366, 300), (362, 330)], [(392, 262), (398, 300), (394, 326)], [(384, 258), (386, 300)], [(380, 224), (376, 246)],
             [(398, 330), (420, 335), (440, 348)], [(380, 322), (410, 330)], [(396, 228), (398, 246)]]
    m = figure(c, parts, folds, 41, 0.85)
    # the tired face: a pale cheek and brow in the hood's shadow, one closed eye
    for (x, y, k) in ((385, 242, 2), (386, 243, 2), (387, 244, 2), (388, 246, 1), (384, 239, 1), (385, 239, 1), (390, 239, 1), (391, 239, 1)):
        c.put(x, y, SKIN[k])
    c.put(386, 241, SKIN[0])
    c.put(390, 241, SKIN[0])
    c.put(388, 248, SKIN[1])
    c.put(389, 248, SKIN[1])
    # bandage: bound strips of linen across the forearm, a brown-red stain soaking through
    band = stroke_mask([[(405, 283), (427, 303)]], 5.2)
    n = Noise(3, 55)
    c.paint(band, lambda x, y: shade(LINEN, 0.26 + 0.16 * (1 if ((x - y) // 3) % 2 else 0) + (n(x, y) - 0.5) * 0.14 - 0.12 * ((x + y) % 7 == 0), x, y))
    c.edges(band, LINEN[3], LINEN[0], -1, -1)
    for bx, by in ((416, 293), (417, 294), (416, 295), (418, 295), (420, 298)):
        c.put(bx, by, WINE_R[3])
    c.flat(poly_mask([(427, 302), (433, 304), (434, 310), (427, 311)]), SKIN[1])
    c.put(429, 303, SKIN[2])
    # a trailing end of the bandage hanging from the elbow
    c.flat(stroke_mask([[(409, 292), (405, 300), (407, 308)]], 0.8), LINEN[2])
    c.put(407, 308, LINEN[1])
    # the hand, grey with cold, loose on the lap
    c.flat(poly_mask([(366, 304), (376, 302), (378, 310), (368, 313)]), SKIN[1])
    c.put(370, 303, SKIN[2])
    for k in range(3):
        c.put(367 + k * 3, 313, SKIN[0])
    return m


# ---------------------------------------------------------------------------------------------- floor props
def puddle(c: Canvas) -> None:
    """Spilled wine: a wet, deep-red pool with a lit rim, a pale highlight and a few drops, thin where it runs."""
    pm = poly_mask(arc_pts(472, 314, 31, 6.5, 0, 360, 36) + [(498, 312)])
    pm2 = poly_mask([(440, 309), (454, 308), (470, 311), (452, 314)])
    both = union(pm, pm2)
    n = Noise(4, 71)
    c.paint(both, lambda x, y: shade(WINE_R, 0.45 + 0.25 * (x - 440) / 60 + (n(x, y) - 0.5) * 0.3 - 0.15 * ((y - 308) / 14), x, y))
    c.edges(both, WINE_R[4], WINE_R[0], 0, -1)
    for x, y in ((456, 312), (457, 312), (470, 314), (471, 314), (472, 314), (484, 313), (485, 313)):
        c.put(x, y, hx("#f0b0a8"))
    for dx, dy in ((498, 316), (503, 318), (432, 313)):
        c.put(dx, dy, WINE_R[3])
        c.put(dx + 1, dy, WINE_R[2])


def flagon(c: Canvas) -> None:
    """The tipped flagon: a pot-bellied stoneware jug on its side, neck toward the wine, a leather-thonged handle on top."""
    body = poly_mask(arc_pts(459, 304, 18, 7.5, 0, 360, 28))
    neck = poly_mask([(438, 300), (446, 299), (446, 309), (438, 309)])
    lip = poly_mask([(434, 299), (439, 299), (439, 310), (434, 310)])
    foot = poly_mask([(474, 297), (478, 298), (478, 311), (474, 311)])
    handle = stroke_mask([arc_pts(461, 297, 8, 6, 180, 360, 10)], 1.0)
    allm = union(body, neck, lip, foot, handle)
    n = Noise(3, 81)
    c.paint(allm, lambda x, y: shade(CLAYS, 0.62 - 0.55 * (y - 296) / 16 + (n(x, y) - 0.5) * 0.25 + (0.2 if x < 450 else 0), x, y))
    c.edges(allm, CLAYS[4], CLAYS[0], -1, -1)
    c.flat(stroke_mask([[(448, 300), (448, 309)]], 0.5), CLAYS[1])
    c.flat(stroke_mask([[(466, 299), (466, 310)]], 0.5), CLAYS[1])
    c.flat(poly_mask([(436, 301), (438, 301), (438, 308), (436, 308)]), CLAYS[0])        # dark mouth
    for xx in range(449, 453):
        c.put(xx, 302, CLAYS[4])
    contact(c, 460, 312, 24, 2, 0.8)


def bottle(c: Canvas) -> None:
    """A stoneware bottle standing on the floor beside the puddle, corked, with a painted band."""
    body = poly_mask([(464, 288), (478, 288), (480, 296), (480, 311), (462, 311), (462, 296)])
    neck = poly_mask([(468, 278), (474, 278), (474, 288), (468, 288)])
    cork = poly_mask([(467, 275), (475, 275), (475, 279), (467, 279)])
    allm = union(body, neck)
    n = Noise(3, 83)
    c.paint(allm, lambda x, y: shade(CLAYS, 0.55 + 0.4 * (1 - (x - 462) / 18) * 0.9 - 0.2 * (y - 290) / 22 + (n(x, y) - 0.5) * 0.2, x, y))
    c.edges(allm, CLAYS[4], CLAYS[0], -1, -1)
    c.paint(cork, lambda x, y: shade(LEATHER_D, 0.6 - 0.3 * (x - 467) / 8 + (n(x, y) - 0.5) * 0.3, x, y))
    c.flat(poly_mask([(462, 298), (480, 298), (480, 302), (462, 302)]), hx("#3e1224"))
    c.flat(poly_mask([(463, 298), (466, 298), (466, 302), (463, 302)]), hx("#6a1c2e"))
    contact(c, 472, 312, 12, 2, 0.8)


def candle_grate(c: Canvas) -> None:
    """A drain grate in the flags with a candle stub burning on its rim: someone's watch light, wax running onto the bars."""
    g = poly_mask([(182, 311), (262, 311), (270, 323), (172, 323)])
    c.paint(g, lambda x, y: IRONS[0] if (x // 5) % 2 == 0 else IRONS[1])
    for bx in range(176, 268, 6):
        c.flat(stroke_mask([[(bx + 1, 312), (bx, 322)]], 0.6), IRONS[3])
    c.edges(g, IRONS[4], hx("#07040c"), -1, -1)
    rim = stroke_mask([[(182, 311), (262, 311)]], 1.0)
    c.flat(rim, IRONS[3])
    # candle stub
    c.flat(poly_mask([(228, 303), (235, 303), (236, 312), (227, 312)]), WAX[1])
    c.flat(poly_mask([(228, 303), (230, 303), (230, 312), (227, 312)]), WAX[3])
    c.flat(poly_mask([(234, 304), (236, 304), (236, 312), (234, 312)]), WAX[0])
    c.put(232, 303, WAX[0])
    for dy, col in ((0, FIRE[4]), (1, FIRE[3]), (2, FIRE[3]), (3, FIRE[2]), (4, FIRE[1])):
        c.put(232, 301 - dy + 4 - 3, col)
    for yy, ww, col in ((297, 1, FIRE[1]), (298, 1, FIRE[2]), (299, 2, FIRE[3]), (300, 2, FIRE[3]), (301, 2, FIRE[4])):
        for xx in range(232 - ww + 1, 232 + ww):
            c.put(xx, yy, col)
    # glow on the grate and floor, wax drips orange on the bars
    for yy in range(290, 324):
        for xx in range(206, 260):
            d = math.hypot((xx - 232) / 26, (yy - 300) / 17)
            if d < 1 and (1 - d) ** 1.6 * 0.85 > bayer(xx, yy):
                r, gg, b = c.get(xx, yy)
                c.put(xx, yy, lerp((r, gg, b), FIRE[2], 0.55))
    for wx, wy in ((226, 313), (227, 315), (237, 313), (238, 316), (239, 317)):
        c.put(wx, wy, WAX[2])


def lantern(c: Canvas) -> None:
    """An iron oil lantern hung from the oak beam on a chain: horn panes glowing, a ring on top, a little light around it."""
    cx = 372
    for yy in range(47, 58):
        c.put(cx, yy, IRONS[3] if yy % 2 else IRONS[1])
        c.put(cx + 1, yy, IRONS[1])
    c.flat(poly_mask(arc_pts(cx, 58, 3, 3, 0, 360, 10)), IRONS[2])
    c.put(cx, 55, IRONS[4])
    glow_cx, glow_cy = cx + 1, 70
    for yy in range(glow_cy - 20, glow_cy + 22):
        for xx in range(glow_cx - 24, glow_cx + 24):
            d = math.hypot((xx - glow_cx) / 24, (yy - glow_cy) / 20)
            if d < 1 and (1 - d) ** 1.8 * 0.7 > bayer(xx, yy):
                r, g, b = c.get(xx, yy)
                c.put(xx, yy, lerp((r, g, b), FIRE[2], 0.5))
    cap = poly_mask([(cx - 7, 62), (cx - 3, 57), (cx + 5, 57), (cx + 9, 62)])
    c.paint(cap, lambda x, y: shade(IRONS, 0.5 - 0.08 * (y - 57) - (0.12 if x > cx + 3 else -0.1), x, y))
    body = poly_mask([(cx - 6, 62), (cx + 8, 62), (cx + 7, 80), (cx - 5, 80)])
    c.paint(body, lambda x, y: shade(FIRE, 0.95 - 0.35 * abs(x - (cx + 1)) / 7 - 0.2 * (y - 62) / 18 + (bayer(x, y) - 0.5) * 0.1, x, y))
    for xx in (cx - 6, cx + 1, cx + 8):
        c.flat(stroke_mask([[(xx, 62), (xx - (xx == cx + 8), 80)]], 0.55), IRONS[1])
    c.flat(poly_mask([(cx - 7, 80), (cx + 9, 80), (cx + 7, 84), (cx - 5, 84)]), IRONS[1])
    c.flat(poly_mask([(cx - 7, 80), (cx + 9, 80), (cx + 9, 81), (cx - 7, 81)]), IRONS[3])
    c.put(cx - 7, 62, IRONS[4])
    c.put(cx + 9, 62, IRONS[0])
    for kx in (cx - 5, cx + 7):
        c.put(kx, 62 + 9, BRASS_L[3])


def cask(c: Canvas, cx: int, foot: int, half: int, height: int, seed: int) -> None:
    """A wine cask standing on end, from the shared wood kit (staves, hoops, rivets), with a cast shadow and a reflection."""
    w, h = half * 2 + 8, height + 12
    p = Pix(w, h, seed=seed)
    mid = w // 2
    b = belly(mid, 3, height - 6, half, 0.12, 11)
    wood_fill(p, b.outline, "v", curve=b.curve, light_fn=b.light, board=half * 0.5, damp=0.25, seed=seed)
    for frac in (0.14, 0.34, 0.66, 0.86):
        y = 3 + (height - 6) * frac
        t = (2 * frac - 1)
        hw = half / 1.12 * (1 + 0.12 * (1 - t * t)) - 1
        pts = [(mid - hw + 2 * hw * i / 12, y + 2.5 * math.sin(math.pi * i / 12) * 0.9) for i in range(13)]
        iron_band(p, pts, 4, rivets=9)
    img = p.im
    # place into the canvas, dropping a shadow to the right on the wall and floor first
    ox, oy = cx - mid, foot - height - 4
    sm = poly_mask([(cx - half + 8, foot - 3), (cx + half + 16, foot - 2), (cx + half + 20, foot + 4), (cx - half + 6, foot + 4)])
    c.paint(sm, lambda x, y: lerp(c.get(x, y), hx("#07040c"), 0.6) if 0.7 > bayer(x, y) else None)
    for y in range(h):
        for x in range(w):
            r, g, bl, a = img.getpixel((x, y))
            if a > 128:
                col = (r, g, bl)
                # grade the cask into the violet dusk so it belongs to the picture
                col = lerp(col, hx("#2a1e3c"), 0.34)
                c.put(ox + x, oy + y, col)
    m = empty()
    m.paste(img.getchannel("A").point(lambda v: 255 if v > 128 else 0), (ox, oy))
    reflection(c, m, foot, 14, 0.35)


def beggar_props(c: Canvas) -> None:
    puddle(c)
    flagon(c)
    bottle(c)
