"""Bazaar picture, left side: the draper's shopfront under its carved sign, the wall with the pointing hand, the pavement.

The shop mirrors the original's layout: a lit open front, a garment hung on a dummy with breeches under it, a cloth shelf,
a hung display, bills on the pillar and shutter, a tag, a rat, flagons and a roll of parchment on the pavement.
"""

from __future__ import annotations

import math
import random

import fxkit
from mnu_bazaar_kit import (BRICKRED, CREAM, DKWOOD, PLUM, SLATE, TEAL, addlight, beam, ell, haze, lantern, plank_rect, pool, ramp,
                            shade, shaded_ell, silhouette, slanted_text, text)
from palette import LINEN, NAVY, WINE, MOSS, LEATHER, PARCHMENT, BRASS, IRON
from pix import Pix, mix, rgb

INK = rgb("#120e18")
RIM = rgb("#4f9aa0")


def slope_y(x: float) -> float:
    """The lower edge of the slanted sign / shutter: 0.64 px down per px right, from (232, 0)."""
    return 0.64 * (x - 232)


def mid_wall(p: Pix) -> None:
    """Wall between the shop and the stall: dark jetty above, the pointing-hand sign, menu board, vent, the seated man."""
    # jetty underside and beams
    p.poly([(388, 0), (672, 0), (672, 58), (520, 96), (388, 70)], rgb("#0c0a14"))
    jb = ramp("#0e0c16", "#171420", "#221e30", "#2e2a42", "#3e3a58")
    for k in range(6):
        beam(p, 400 + k * 46, 66 - k * 3, 410 + k * 45, 0, 3, jb)
    p.hline(388, 70, 140, rgb("#3a3452"))
    # wall: violet plaster in vertical boards, warm light climbing from below
    p.rect(420, 92, 112, 340, rgb("#2a2036"))
    plank_rect(p, 420, 92, 112, 340, ramp("#150f1f", "#201830", "#2c2240", "#3a2e52", "#4a3c66"), vertical=True, board=9, seed=4)
    # patches of painted colour peeling (the original's sunset glow becomes lantern light on the plaster)
    for x0, y0, w, h in ((430, 340, 40, 60), (480, 300, 40, 90)):
        p.dither(x0, y0, w, h, rgb("#a8542a"), 0.3)
    # downpipe (lead) with collars, and an elbow at the foot
    lead = ramp("#141a1e", "#222e34", "#34464e", "#4e6670", "#7a9aa0")
    p.rect(406, 0, 11, 430, lead[2]); p.vline(406, 0, 430, lead[4]); p.vline(407, 0, 430, lead[3]); p.vline(416, 0, 430, lead[0])
    for y in range(40, 430, 74):
        p.rect(404, y, 15, 4, lead[3]); p.hline(404, y, 15, lead[4]); p.hline(404, y + 3, 15, lead[0])
    p.poly([(406, 420), (417, 420), (417, 432), (440, 432), (440, 438), (406, 438)], lead[2]); p.hline(406, 432, 34, lead[4])
    # bracket pipes to the lantern and the vent
    beam(p, 417, 44, 462, 36, 3, lead); beam(p, 417, 56, 470, 52, 2, lead)
    # the lantern on its bracket arm
    p.vline(470, 36, 8, INK)
    lantern(p, 470, 42, 14, 16, "red")
    # louvred vent box (replaces the air-conditioner): oak louvres, brass grille, iron rim, chimney pipes
    p.rect(484, 106, 66, 62, rgb("#6a5a58")); p.hline(484, 106, 66, rgb("#9a8a84")); p.vline(484, 106, 62, rgb("#8a7a76"))
    p.rect(486, 122, 50, 44, rgb("#2a2430"))
    for y in range(123, 166, 4):
        p.hline(486, y, 50, rgb("#5a5260")); p.hline(486, y + 1, 50, rgb("#17131f"))
    p.rect(540, 108, 8, 56, rgb("#3a343c")); p.vline(540, 108, 56, rgb("#6a626a"))
    p.rect(488, 108, 44, 10, rgb("#3a3440")); p.hline(488, 108, 44, rgb("#5a5260"))
    for x in (492, 504, 516):
        p.px(x, 113, rgb("#c8561e"))
    p.rect(484, 166, 66, 3, rgb("#241e2a"))
    beam(p, 484, 140, 462, 150, 3, lead); beam(p, 484, 128, 466, 126, 2, lead)
    # ropes (bell-pull cords) hanging from the vent to the lamp
    for i, x in enumerate((492, 501)):
        pts = [(x, 169), (x - 4, 190), (x - 6, 212)]
        for a, b in zip(pts, pts[1:]):
            p.line(*a, *b, rgb("#3a2a22"))
    # menu board: a teal-painted board with chalk lines, bolted to the wall
    p.rect(463, 224, 36, 40, INK); p.rect(465, 226, 32, 36, rgb("#2a5a60")); p.hline(465, 226, 32, rgb("#5fa8aa")); p.vline(465, 226, 36, rgb("#3f8084"))
    text(p, 469, 231, "FARE", rgb("#d8f0e8"))
    for i, w in enumerate((22, 18, 22, 14)):
        p.hline(469, 243 + i * 4, w, rgb("#a8d8d0"))
    # the pointing hand, painted pale on a dark red board, glowing a little like the neon arrow it replaces
    p.rect(432, 268, 94, 62, rgb("#2e1220")); p.frame(432, 268, 94, 62, rgb("#4a1e30"))
    p.dither(432, 268, 94, 62, rgb("#3a1a2a"), 0.3)
    hand = rgb("#e6dcc0")
    outline = rgb("#78c8c0")
    shade_h = rgb("#b8ac90")
    # forearm and cuff coming from the right, a fist with curled fingers, a long index finger pointing down-left
    p.rect(514, 272, 14, 16, rgb("#8a5aa0")); p.hline(514, 272, 14, rgb("#b88ac8")); p.rect(512, 270, 4, 20, outline)
    ell(p, 505, 283, 11, 11, outline); ell(p, 505, 283, 9, 9, hand)
    for fy in (277, 281, 285, 289):
        p.hline(500, fy, 10, shade_h); p.px(500, fy, hand)
    p.poly([(500, 288), (508, 288), (506, 294), (498, 292)], hand)           # thumb across the fingers
    for t in range(0, 24):
        x, y = 496 - t * 1.4, 278 + t * 0.62
        ell(p, x, y, 3.6, 3.6, outline)
    for t in range(0, 24):
        x, y = 496 - t * 1.4, 278 + t * 0.62
        ell(p, x, y, 2.4, 2.4, hand)
    p.hline(468, 290, 12, shade_h)
    pool(p, 480, 296, 44, 28, rgb("#2a8a88"), 0.35)
    # a seated vagrant by the wall: hood, hunched back, knees up, a cane; cyan rim from the shop light
    body = rgb("#0a0812")
    pts = [(448, 436), (444, 412), (448, 388), (456, 352), (460, 330), (468, 316), (480, 314), (488, 324), (490, 345), (496, 372), (508, 398), (520, 412), (524, 436), (500, 440), (470, 440)]
    silhouette(p, pts, body, rgb("#2d6068"), "l")
    ell(p, 474, 312, 9, 10, body)
    p.vline(465, 305, 12, RIM)
    p.poly([(464, 304), (474, 298), (484, 304), (484, 312), (480, 322), (466, 322)], body)
    beam(p, 440, 440, 452, 372, 2, ramp("#0a0812", "#14101c", "#1e1a2a", "#2e2a40", "#4a4a66"))
    p.hline(488, 410, 16, RIM); p.hline(505, 414, 14, RIM)
    # lower-wall orange glow
    pool(p, 480, 420, 64, 30, rgb("#a04818"), 0.55)


def pillar_and_wall(p: Pix) -> None:
    """The dark left wall with the hopper and downpipes, the painted fist and its tag, and the stone pillar."""
    p.rect(0, 0, 165, 436, PLUM[0])
    plank_rect(p, 0, 0, 125, 436, ramp("#0f0c18", "#171320", "#1d182a", "#252036", "#2e2840"), vertical=True, board=10, seed=2)
    # lead hopper head and three downpipes with collars
    lead = ramp("#1a1e26", "#2c3440", "#404c5c", "#5a6a7a", "#7e8e9c")
    p.poly([(48, 30), (100, 30), (98, 52), (88, 120), (60, 120), (50, 52)], lead[2])
    p.rect(48, 28, 54, 6, lead[3]); p.hline(48, 28, 54, lead[4])
    p.rect(54, 36, 40, 48, lead[1]); p.hline(54, 36, 40, lead[3])
    for x in range(58, 92, 8):
        p.vline(x, 40, 40, lead[2])
    p.rect(70, 0, 8, 30, lead[2]); p.vline(70, 0, 30, lead[4]); p.vline(77, 0, 30, lead[0])     # the gutter outlet above
    for bx in (44, 98):
        p.rect(bx, 34, 6, 3, lead[4]); p.rect(bx, 34, 2, 30, lead[1]); p.px(bx, 34, lead[4])        # wall straps
    p.rect(56, 90, 6, 4, rgb("#c85a2a")); p.rect(66, 90, 6, 4, rgb("#e8b03a")); p.rect(76, 90, 6, 4, rgb("#3aa86a"))   # painted tally marks
    p.rect(62, 118, 8, 6, lead[3]); p.rect(82, 118, 8, 6, lead[3])
    for x in (30, 68, 86):
        p.rect(x, 124, 4, 52, lead[2]); p.vline(x, 124, 52, lead[4]); p.vline(x + 3, 124, 52, lead[0])
        p.rect(x - 1, 140, 6, 3, lead[3])
    p.rect(30, 172, 60, 4, lead[2]); p.hline(30, 172, 60, lead[4])
    # painted green fist and its tag (VIVAT)
    g = ramp("#16240e", "#27401a", "#3a5e24", "#58843a")
    p.poly([(38, 218), (50, 206), (62, 204), (76, 208), (84, 216), (84, 238), (80, 252), (70, 262), (56, 262), (46, 250)], g[2])
    for fx in (48, 58, 68, 78):
        p.rect(fx, 206, 8, 14, g[3]); p.hline(fx, 206, 8, g[3]); p.vline(fx + 8, 208, 10, g[1])
    p.poly([(44, 224), (36, 232), (40, 244), (50, 240)], g[2])
    for fx in (56, 66, 76):
        p.vline(fx, 208, 20, g[1]); p.vline(fx + 1, 208, 20, g[3])
    p.hline(46, 222, 38, g[1]); p.hline(48, 223, 34, g[3])
    p.rect(52, 262, 22, 12, g[1])
    p.vline(60, 262, 12, g[2])
    slanted_text(p, 38, 296, "VIVAT", g[3], 3, -0.2)
    # intercom-like bell: a wall-hung bronze doorbell with a pull cord (the call box)
    p.rect(2, 372, 4, 4, BRASS[2])
    # stone pillar on the shop's left
    p.rect(125, 0, 40, 436, rgb("#312842")); p.vline(125, 0, 436, rgb("#4a3c60")); p.vline(126, 0, 436, rgb("#3c3052"))
    p.vline(164, 0, 436, rgb("#18121f")); p.vline(163, 0, 436, rgb("#221a2e"))
    for y in range(14, 436, 34):
        p.hline(126, y, 38, rgb("#1e1828")); p.hline(126, y + 1, 38, rgb("#3e3258"))
    # pasted things: a small tag bill, a round painted target, a red seal glyph, a notice
    p.rect(139, 107, 20, 18, rgb("#d8a24a")); p.hline(139, 107, 20, rgb("#f4cc78")); p.hline(141, 112, 14, rgb("#8a5a24")); p.hline(141, 116, 12, rgb("#8a5a24")); p.hline(141, 120, 14, rgb("#8a5a24"))
    # painted sigil: crown on a round shield board, torn and peeling
    cx, cy = 140, 176
    for r, c in ((34, "#7a3a2a"), (30, "#d8742a"), (24, "#f0a848"), (18, "#e07a3a"), (12, "#f4cf7a")):
        ell(p, cx + 6, cy, r * 0.52, r, rgb(c))
    p.poly([(132, 186), (138, 170), (144, 178), (150, 168), (154, 186)], rgb("#8a6aaa"))
    p.hline(132, 186, 23, rgb("#c8aae0")); p.px(138, 168, rgb("#e8d8f8")); p.px(150, 166, rgb("#e8d8f8"))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        p.line(int(cx + 6 + 6 * math.cos(a)), int(cy + 12 * math.sin(a)), int(cx + 6 + 16 * math.cos(a)), int(cy + 30 * math.sin(a)), rgb("#c84a2a"))
    p.rect(129, 208, 30, 28, rgb("#cc2a2a")); p.frame(129, 208, 30, 28, rgb("#f06a50"))
    p.poly([(136, 214), (152, 214), (152, 220), (142, 222), (152, 226), (152, 232), (136, 232), (136, 226), (146, 224), (136, 220)], rgb("#3a0a10"))
    p.rect(137, 243, 22, 40, rgb("#c4b89c")); p.hline(137, 243, 22, rgb("#e8dcc0")); p.vline(137, 243, 40, rgb("#dccfb0"))
    for i in range(8):
        p.hline(140, 247 + i * 4, 16 if i % 3 else 9, rgb("#6a5e4e"))


def shop(p: Pix) -> None:
    pillar_and_wall(p)
    # interior of the shop: cool lit back wall, shelves, hung things
    p.rect(165, 0, 223, 436, rgb("#2a4a56"))
    p.gradient(165, 0, 223, 436, rgb("#18303a"), rgb("#4a7a88"), 10)
    # plank back wall
    plank_rect(p, 190, 90, 190, 340, ramp("#1a3038", "#27444e", "#355a66", "#46707c", "#5a8a96"), vertical=True, board=14, seed=8)
    p.dither(165, 0, 223, 90, rgb("#10202a"), 0.5)
    # the rod that carries the clothes (iron on two chains) and the chains from the shutter
    p.rect(168, 103, 214, 3, rgb("#3a3a46")); p.hline(168, 103, 214, rgb("#8a8a9a"))
    for x in (240, 300, 360):
        for y in range(88, 103, 3):
            p.rect(x, y, 2, 2, rgb("#5a5a6a")); p.px(x, y, rgb("#8a8a9a"))
    # the hung display: a boarded panel with gloves, hose and a cap on pegs
    panel = [(170, 128), (247, 140), (247, 236), (170, 236)]
    p.poly(panel, rgb("#3a2a34"))
    plank_rect(p, 172, 140, 74, 94, ramp("#241a22", "#34242e", "#46303a", "#5a3e46", "#6e4c52"), vertical=False, board=8, seed=5)
    p.poly([(170, 128), (247, 140), (247, 142), (170, 130)], rgb("#8a5a58"))
    for gx, gy, c in ((184, 150, "#c49a62"), (212, 152, "#b8864e"), (234, 154, "#d4b078")):      # gloves on pegs
        p.rect(gx, gy - 2, 3, 3, rgb("#8a8a9a"))
        p.poly([(gx - 3, gy + 1), (gx + 6, gy + 1), (gx + 8, gy + 18), (gx + 4, gy + 22), (gx - 2, gy + 18)], rgb(c))
        p.vline(gx - 3, gy + 1, 17, mix(rgb(c), (255, 255, 255), 0.25))
        for f in range(4):
            p.vline(gx - 2 + f * 2, gy + 14, 8, mix(rgb(c), (0, 0, 0), 0.25))
    p.poly([(190, 190), (206, 186), (212, 200), (192, 204)], rgb("#7a2a30")); p.hline(190, 190, 14, rgb("#b04a44"))   # a folded cap
    # shelf with bolts of cloth (circle ends toward us)
    p.rect(168, 238, 84, 5, rgb("#6a4a34")); p.hline(168, 238, 84, rgb("#9a7248")); p.hline(168, 243, 84, rgb("#2a1a14"))
    for i, (c, r) in enumerate((("#7a2a30", 7), ("#2f4c70", 7), ("#3e5e38", 7), ("#c8b88a", 7), ("#6a3a6a", 6))):
        bx = 178 + i * 16
        shaded_ell(p, bx, 231, r, r, [mix(rgb(c), (0, 0, 0), 0.5), mix(rgb(c), (0, 0, 0), 0.25), rgb(c), mix(rgb(c), (255, 255, 255), 0.25)])
        p.px(bx, 231, rgb("#2a1a14")); p.px(bx + 1, 231, rgb("#2a1a14"))
        p.hline(bx - 2, 229, 4, mix(rgb(c), (255, 255, 255), 0.3))
    # louvred shutter window at the back
    p.rect(250, 128, 52, 54, rgb("#16222a")); p.frame(250, 128, 52, 54, rgb("#3a4a54"))
    for y in range(130, 180, 4):
        p.hline(252, y, 48, rgb("#5a7a84")); p.hline(252, y + 1, 48, rgb("#1a2a32"))
    # hanging lamps (oil lamps on chains from the shutter, replacing the fluorescent tubes)
    for lx, ly in ((190, 40), (214, 56)):
        p.vline(lx, 0, ly - 4, rgb("#5a5a6a"))
        shaded_ell(p, lx, ly, 8, 5, BRASS)
        p.rect(lx - 6, ly + 3, 12, 3, rgb("#ffe8a8")); p.hline(lx - 4, ly + 6, 8, rgb("#fff4d0"))
        pool(p, lx, ly + 4, 26, 18, rgb("#a8884a"), 0.6)
    # the shutter band and the sign wedge over the opening
    shutter(p)
    # the draper's wares: a green cloak behind, the red gambeson on a dummy, breeches below
    cloak(p)
    gambeson(p)
    breeches(p)
    # lowered counter shutter with bills and tag
    counter_board(p)
    # right posts: the shopfront's pillar, the iron rod, the paired timber
    p.rect(372, 0, 26, 436, rgb("#2e3446")); p.vline(372, 0, 436, rgb("#58627a")); p.vline(373, 0, 436, rgb("#424a60")); p.vline(397, 0, 436, rgb("#161a24"))
    for y in range(8, 436, 30):
        p.px(380, y, rgb("#161a24")); p.px(388, y + 12, rgb("#161a24"))
    p.rect(374, 160, 22, 12, rgb("#1c2030")); p.hline(374, 160, 22, rgb("#5a6278"))
    p.rect(399, 0, 3, 430, rgb("#8aa8b0")); p.vline(399, 0, 430, rgb("#c0d8dc")); p.vline(401, 0, 430, rgb("#4a6068"))
    # iron stay-rod, the little price card hung from it
    beam(p, 374, 117, 432, 147, 3, ramp("#14141c", "#24242e", "#3a3a48", "#5a5a6c", "#8a8a9e"))
    for cx in (421, 439):
        for k in range(4):
            p.rect(cx, 146 + k * 3 if cx == 421 else 150 + k * 2, 2, 2, rgb("#8a8a9e"))
    p.rect(414, 152, 32, 42, rgb("#2a1a14")); p.rect(416, 154, 28, 38, rgb("#e0c890"))
    p.frame(416, 154, 28, 38, rgb("#c8803a")); p.hline(417, 155, 26, rgb("#f4e4b0"))
    # spool pictogram
    p.rect(424, 160, 12, 3, rgb("#8a5a34")); p.rect(424, 181, 12, 3, rgb("#8a5a34"))
    p.rect(426, 163, 8, 18, rgb("#c04a3a")); p.vline(426, 163, 18, rgb("#e8785a"))
    for yy in range(165, 180, 3):
        p.hline(426, yy, 8, rgb("#8a2a28"))
    pool(p, 430, 174, 26, 28, rgb("#a07840"), 0.4)


def shutter(p: Pix) -> None:
    """The propped-up shop shutter (slanted band) and the carved sign above it: TAILOR / DRAPER with shears and a spool."""
    band = [(165, 0), (232, 0), (388, 100), (388, 132), (165, 36)]
    p.poly(band, rgb("#4a2a26"))
    # slanted boards with rust-red staining
    for k in range(0, 40, 5):
        p.line(165, k, 388, 100 + k * 0.82 + 2, rgb("#2a1618") if (k // 5) % 2 else rgb("#6a3a30"))
        p.line(165, k + 1, 388, 100 + k * 0.82 + 3, rgb("#7a4a38") if (k // 5) % 2 == 0 else rgb("#3a2020"))
    p.dither(165, 0, 223, 132, rgb("#8a4a2a"), 0.08)
    p.line(165, 36, 388, 132, rgb("#1a0e10")); p.line(165, 0, 232, 0, rgb("#1a0e10"))
    # carved sign: teal-painted board in a gold frame, lit from inside by the lamps below (as the original's light box)
    wedge = [(232, 0), (388, 0), (388, 98)]
    p.poly(wedge, rgb("#3a7a82"))
    for y in range(0, 100):
        x0 = 232 + y / 0.64
        for x in range(int(x0) + 3, 388):
            v = (x * 3 + y * 5) % 11
            if v == 0 and (x + y) % 2:
                p.px(x, y, rgb("#4f959a"))
    p.poly([(240, 0), (383, 0), (383, 88)], rgb("#58a8a8"))
    p.dither(240, 0, 143, 90, rgb("#3a7a82"), 0.25)
    p.line(232, 0, 388, 100, rgb("#c8a248")); p.line(233, 0, 388, 99, rgb("#a07a2c")); p.line(237, 0, 385, 94, rgb("#e0c068"))
    p.vline(388, 0, 100, rgb("#c8a248")); p.vline(385, 0, 94, rgb("#e0c068"))
    for k in range(3):
        p.px(300 + k * 30, 3, rgb("#fff0b8"))
    slanted_text(p, 291, 9, "TAILOR", rgb("#5a1218"), 2, 0.64)
    slanted_text(p, 290, 8, "TAILOR", rgb("#f4ecd0"), 2, 0.64)
    slanted_text(p, 301, 29, "& DRAPER", rgb("#5a1218"), 1, 0.64)
    slanted_text(p, 300, 28, "& DRAPER", rgb("#f4ecd0"), 1, 0.64)
    # shears and spool carved at the wide end
    for (x0, y0, x1, y1) in ((352, 52, 380, 88), (380, 52, 352, 88)):
        beam(p, x0, y0, x1, y1, 3, ramp("#2a2a36", "#4a4a5a", "#7a7a8e", "#b0b0c0", "#e0e0ee"))
    p.rect(349, 90, 7, 7, rgb("#c8a248")); p.rect(376, 90, 7, 7, rgb("#c8a248")); p.rect(351, 92, 3, 3, rgb("#3a7a82")); p.rect(378, 92, 3, 3, rgb("#3a7a82"))
    p.rect(364, 68, 3, 3, BRASS[3])
    # sign lit like a lamp box: a soft pale glow and a gold rim line along the lower edge
    pool(p, 340, 40, 60, 50, rgb("#6ab0b0"), 0.5, box=(232, 0, 388, 100))


def cloak(p: Pix) -> None:
    """A teal-blue hooded cloak on a hanger behind the doublet."""
    pts = [(300, 134), (330, 126), (352, 134), (376, 160), (378, 186), (366, 200), (336, 194), (300, 190), (284, 174)]
    fxkit.cloth_fill(p, pts, ramp=[rgb(h) for h in ("#14344a", "#1f4e66", "#2f6e84", "#4a90a4")], kind="wool", folds=4, seed=13)
    p.poly([(312, 128), (332, 124), (344, 136), (324, 142)], rgb("#17394e"))    # the hood's fold
    p.line(300, 134, 284, 174, rgb("#10283a")); p.line(352, 134, 376, 160, rgb("#6ab4c4"))


def gambeson(p: Pix) -> None:
    """A red quilted gambeson with a tawny fur collar, brass buttons, lacing and two leather pockets, on a wooden dummy."""
    # hanger hook and shoulder bar
    p.vline(320, 108, 16, rgb("#8a8a9a")); p.px(319, 107, rgb("#8a8a9a")); p.px(318, 108, rgb("#8a8a9a")); p.px(319, 108, rgb("#8a8a9a"))
    beam(p, 296, 146, 344, 146, 4, DKWOOD)
    beam(p, 296, 146, 320, 124, 3, ramp("#2a1a14", "#4a2e20", "#6a4630", "#8a6040", "#aa7a50"))
    beam(p, 344, 146, 320, 124, 3, ramp("#2a1a14", "#4a2e20", "#6a4630", "#8a6040", "#aa7a50"))
    body = [(286, 152), (308, 146), (332, 146), (354, 152), (364, 170), (366, 214), (368, 244), (356, 250), (350, 232), (346, 236), (346, 252), (292, 252), (284, 246), (278, 236), (272, 248), (262, 240), (262, 206), (268, 170)]
    rp = [rgb(h) for h in ("#3a0e14", "#611a22", "#8e2a2e", "#bc423a", "#de6a52")]
    fxkit.cloth_fill(p, body, ramp=rp, kind="wool", folds=3, fold_dir="v", seed=21, light=0.6)
    # quilting channels in diamond-ish lines
    for x in range(290, 348, 8):
        p.vline(x, 168, 80, rp[1])
    for y in range(172, 248, 10):
        for x in range(286, 350, 3):
            if (x // 3 + y // 10) % 2:
                p.px(x, y, rp[1])
    p.vline(319, 152, 98, rp[0]); p.vline(320, 152, 98, rp[4])        # the front opening, laced
    for y in range(158, 246, 6):
        p.px(317, y, rp[0]); p.px(322, y, rp[0]); p.line(317, y, 322, y + 3, rgb("#d8c490"))
    for y in (164, 188):
        p.rect(302, y, 3, 3, BRASS[3]); p.px(302, y, BRASS[4]); p.rect(336, y, 3, 3, BRASS[3]); p.px(336, y, BRASS[4])
    # sleeve cuffs: fur trim
    for cx0, cy0 in ((262, 228), (350, 232)):
        p.rect(cx0, cy0, 18, 14, rgb("#b08a58"))
        for k in range(0, 18, 2):
            p.px(cx0 + k, cy0 + (k % 3), rgb("#7a5a38")); p.px(cx0 + k, cy0 + 12, rgb("#d8b880"))
        p.hline(cx0, cy0, 18, rgb("#d8b880"))
    # leather pockets with straps and brass studs
    for px0 in (278, 328):
        p.rect(px0, 222, 24, 20, rgb("#6e4326")); p.hline(px0, 222, 24, rgb("#935e36")); p.vline(px0, 222, 20, rgb("#8a5632"))
        p.hline(px0, 241, 24, rgb("#2a170f")); p.vline(px0 + 23, 222, 20, rgb("#4a2b1a"))
        p.rect(px0 + 10, 228, 4, 4, BRASS[3]); p.px(px0 + 10, 228, BRASS[4])
    # fur collar around the neck
    for y in range(140, 162):
        w = 26 - abs(y - 150) // 2
        for x in range(320 - w, 320 + w):
            tone = (x * 5 + y * 3) % 7
            c = (rgb("#d4b27a"), rgb("#b08a58"), rgb("#8a6a42"), rgb("#c4a068"))[tone % 4 if tone < 4 else 1]
            if y > 156 and (x + y) % 3 == 0:
                continue
            p.px(x, y, c)
    p.poly([(310, 150), (330, 150), (320, 168)], rgb("#611a22"))      # the open neck
    p.vline(320, 128, 20, rgb("#8a6a42"))
    # a diamond price-tag on a thread, red paper
    p.line(358, 252, 358, 258, rgb("#d8c490")); p.poly([(358, 258), (364, 264), (358, 270), (352, 264)], rgb("#cc2a2a")); p.px(357, 262, rgb("#f0a080"))


def breeches(p: Pix) -> None:
    """Baggy wool breeches hung from a peg-bar, one leg with a moss-green stripe, tied at the knee."""
    p.rect(284, 262, 80, 4, DKWOOD[3]); p.hline(284, 262, 80, DKWOOD[4])
    leg_l = [(284, 266), (324, 266), (326, 320), (318, 400), (322, 418), (296, 418), (286, 400), (282, 340)]
    leg_r = [(324, 266), (364, 266), (370, 330), (368, 400), (362, 418), (332, 418), (324, 400), (324, 330)]
    rp = [rgb(h) for h in ("#2e2822", "#4a4036", "#6e6252", "#8e806a", "#aa9c84")]
    fxkit.cloth_fill(p, leg_l, ramp=rp, kind="wool", folds=3, seed=31, light=0.6)
    fxkit.cloth_fill(p, leg_r, ramp=rp, kind="wool", folds=3, seed=32, light=0.35)
    for y in range(268, 400):
        p.px(366 - (y - 268) // 60, y, rgb("#3a5e38"))
        p.px(367 - (y - 268) // 60, y, rgb("#27402a"))
    p.vline(324, 266, 150, rp[0]); p.vline(323, 270, 140, rp[1])
    p.hline(284, 276, 80, rp[0])
    # a drawstring and the pocket flaps
    p.line(324, 266, 318, 290, rgb("#d8c490")); p.line(324, 266, 330, 292, rgb("#d8c490"))
    for x0 in (290, 340):
        p.rect(x0, 288, 18, 14, rp[3]); p.hline(x0, 288, 18, rp[4]); p.hline(x0, 301, 18, rp[0]); p.px(x0 + 8, 296, BRASS[3])
    # hose and boots at the foot
    for x0 in (294, 336):
        p.rect(x0, 404, 24, 14, rgb("#2a170f")); p.hline(x0, 404, 24, rgb("#6e4326")); p.hline(x0, 416, 24, rgb("#14090a"))
    # a small red tag on the right edge
    p.poly([(366, 346), (372, 352), (366, 358), (360, 352)], rgb("#cc2a2a"))


def counter_board(p: Pix) -> None:
    """The lowered half-shutter: red boards, a spray tag, two wanted bills, rust at the foot, the painted kerb stripe."""
    poly = [(163, 238), (272, 262), (272, 432), (163, 432)]
    p.poly(poly, rgb("#3a1a2c"))
    plank_rect(p, 165, 250, 107, 182, ramp("#240e1c", "#341628", "#4a2038", "#622a46", "#7a3a58"), vertical=True, board=11, seed=6)
    # cover the triangle above the slanted top edge with the interior again
    p.poly([(163, 238), (272, 262), (272, 244), (163, 220)], rgb("#2a4a56"))
    p.line(163, 238, 272, 262, rgb("#9a5a78")); p.line(163, 239, 272, 263, rgb("#1a0a12"))
    # rust at the bottom
    for x in range(165, 272):
        for y in range(404, 432):
            if (x * 7 + y * 13) % 11 < (y - 404) // 3:
                p.px(x, y, rgb("#8a4a22") if (x + y) % 3 else rgb("#5a2a14"))
    # spray tag: NO TAX with a crown under it
    tagc = rgb("#e0603a")
    slanted_text(p, 168, 316, "NO", tagc, 3, 0.18)
    slanted_text(p, 214, 321, "TAX", tagc, 3, 0.18)
    slanted_text(p, 169, 317, "NO", rgb("#8a2a1c"), 3, 0.18)
    p.poly([(206, 352), (210, 342), (214, 350), (219, 342), (224, 350), (228, 342), (230, 356), (206, 356)], tagc)
    p.rect(206, 356, 24, 3, rgb("#c04a2a"))
    for dx in (0, 11, 22):
        p.px(206 + dx + 1, 340, tagc)
    for i in range(7):
        p.px(180 + i * 9, 380 + (i % 2) * 2, tagc)       # drips
        p.vline(180 + i * 9, 383, 3 + i % 4, tagc) if i % 2 == 0 else None
    # wanted bills
    wanted(p, 172, 250, 40, 54, True)
    wanted(p, 220, 262, 42, 58, False)


def wanted(p: Pix, x: int, y: int, w: int, h: int, single: bool) -> None:
    fxkit.paper_fill(p, (x, y, w, h), ramp=[rgb(c) for c in ("#6a5e4a", "#9a8e74", "#c4b890", "#dcd0ac", "#ece2c0")], folds=(0, 1), stains=0.3, nails=("tl", "tr"), seed=x)
    text(p, x + 3, y + 4, "WANTED", rgb("#2a2224"))
    p.hline(x + 3, y + 3, w - 6, rgb("#8a2a2a"))
    if single:
        shaded_ell(p, x + w // 2, y + 22, 10, 12, ramp("#6a5a50", "#9a8a78", "#c4b4a0", "#e0d4c0"))
        p.poly([(x + 6, y + 14), (x + 8, y + 6), (x + 12, y + 14)], rgb("#8a3030")); p.poly([(x + 28, y + 14), (x + 26, y + 6), (x + 22, y + 14)], rgb("#8a3030"))
        p.rect(x + w // 2 - 6, y + 20, 3, 2, INK); p.rect(x + w // 2 + 3, y + 20, 3, 2, INK); p.hline(x + w // 2 - 3, y + 29, 7, rgb("#6a2a2a"))
        p.vline(x + w // 2 - 8, y + 26, 5, rgb("#8a2a2a")); p.vline(x + w // 2 + 8, y + 26, 5, rgb("#8a2a2a"))
        for i in range(3):
            p.hline(x + 6, y + 38 + i * 4, w - 12, rgb("#4a4034"))
    else:
        for r in range(4):
            for c in range(3):
                fx, fy = x + 7 + c * 11, y + 13 + r * 12
                p.rect(fx - 4, fy - 4, 9, 10, rgb("#a89a7c"))
                ell(p, fx, fy, 3, 3, rgb("#5a7a48") if (r + c) % 2 else rgb("#6a5a4a"))
                p.px(fx - 1, fy, INK); p.px(fx + 1, fy, INK)
                p.hline(fx - 3, fy + 4, 7, rgb("#4a4034"))


def pavement(p: Pix) -> None:
    """The raised flagstone pavement of the shop with its painted threshold stripe (drawn before the light passes)."""
    # raised flagstone pavement
    walk = [(0, 436), (480, 436), (500, 470), (528, 498), (0, 498)]
    p.poly(walk, rgb("#2a2640"))
    rng = random.Random(5)
    stone = ramp("#1a1728", "#232036", "#2e2a46", "#3a3658", "#4a456c")
    for y0 in range(436, 498, 12):
        x = -rng.randint(0, 60)
        while x < 520:
            w = rng.randint(50, 100)
            tone = rng.choice([1, 2, 2, 3])
            p.rect(x, y0, w - 2, 11, stone[tone]); p.hline(x, y0, w - 2, stone[min(4, tone + 1)])
            p.hline(x, y0 + 11, w, stone[0])
            if rng.random() < 0.5:
                p.speckle(x, y0, w, 11, [stone[0], stone[4]], 0.03)
            x += w
    p.poly([(0, 498), (528, 498), (528, 508), (0, 508)], rgb("#16131f")); p.hline(0, 498, 528, rgb("#5a5478")); p.hline(0, 499, 528, rgb("#3a3552"))
    p.poly([(480, 436), (500, 470), (528, 498), (528, 440)], rgb("#1a1728"))
    p.line(480, 436, 528, 498, rgb("#4a456c")); p.line(481, 437, 528, 499, rgb("#2a2640"))
    # painted red-and-cream threshold stripe along the doorsill
    for i in range(0, 200):
        x = 195 + i
        tone = ((i // 6) % 2 == 0)
        p.rect(x, 428 + (i // 25), 1, 10, rgb("#d8c8a8") if tone else rgb("#a8322a"))
    p.hline(195, 427, 200, rgb("#6a5a48")); p.hline(195, 438 + 7, 200, rgb("#2a1a1a"))


def foreground(p: Pix) -> None:
    """Things standing on the pavement: flagons, parchment, the rat, the crate."""
    # contact shadows, then flagons on the sill
    for bx, top, c in ((166, 396, "#4a1a18"), (186, 400, "#3a1a14")):
        p.rect(bx - 2, 458, 24, 5, rgb("#1a1020"))
        glass = ramp("#140c0c", c, mix(rgb(c), (255, 255, 255), 0.2), mix(rgb(c), (255, 255, 255), 0.45))
        p.poly([(bx + 4, top), (bx + 10, top), (bx + 10, top + 24), (bx + 16, top + 36), (bx + 16, 460), (bx - 2, 460), (bx - 2, top + 36), (bx + 4, top + 24)], glass[1])
        p.vline(bx - 1, top + 36, 24, glass[3]); p.vline(bx + 2, top + 38, 20, glass[2]); p.vline(bx + 14, top + 36, 24, glass[0])
        p.rect(bx + 3, top - 4, 8, 6, rgb("#2a1a14")); p.hline(bx + 3, top - 4, 8, rgb("#6a4a34"))
        p.rect(bx, top + 44, 14, 14, rgb("#d8c490")); p.hline(bx, top + 44, 14, rgb("#f4e4b0"))
        p.rect(bx + 4, top + 49, 6, 5, rgb("#b8281e"))
        p.hline(bx + 2, 459, 12, glass[0])
    # roll of parchment on the pavement
    p.rect(66, 464, 56, 12, rgb("#14101c"))
    shaded_ell(p, 96, 458, 28, 12, ramp("#6a6258", "#9a9284", "#c4bcaa", "#e4dccc"))
    p.rect(68, 450, 54, 16, rgb("#b0a894")); p.hline(68, 450, 54, rgb("#e4dccc"))
    shaded_ell(p, 70, 458, 5, 8, ramp("#5a5448", "#8a8274", "#b8b09c", "#dcd4c0"))
    for rr, cc in ((7, "#4a4034"), (5, "#c4bcaa"), (3, "#4a4034"), (1, "#8a8274")):
        p.ellipse(70 - rr // 2, 458 - rr, rr + 1, rr * 2 + 1, rgb(cc))
    p.hline(70, 477, 40, rgb("#8a8a9e")); p.poly([(60, 476), (110, 476), (114, 486), (56, 486)], rgb("#3e3a58"))
    # crumpled parchment sheet
    sheet = [(312, 470), (336, 466), (360, 468), (388, 476), (372, 480), (348, 478), (324, 481)]
    p.poly(sheet, rgb("#b8b4b4")); p.line(336, 466, 348, 478, rgb("#7a7684")); p.line(360, 468, 372, 480, rgb("#e8e4e4")); p.hline(318, 478, 20, rgb("#6a6674"))
    # the rat: sitting up on its haunches, nose forward, long pale tail
    rat(p, 272, 462)
    # crate at bottom left with a corked flagon on it
    crate(p)


def rat(p: Pix, x: int, y: int, k: float = 1.35) -> None:
    """A rat sitting up on its haunches (original-sized: about 50 px with the tail), nose forward, long pale tail."""
    S = lambda v: int(round(v * k))
    fur = ramp("#3a3238", "#5a5058", "#847a82", "#a89ea4", "#c8c0c4")
    pink = rgb("#c88a90")
    p.rect(x - S(14), y + S(27), S(36), S(4), rgb("#14101c"))
    pts = [(x + S(12), y + S(32)), (x + S(24), y + S(36)), (x + S(34), y + S(40)), (x + S(38), y + S(50)), (x + S(34), y + S(60))]
    for a, b in zip(pts, pts[1:]):
        p.line(*a, *b, rgb("#c4949a")); p.line(a[0], a[1] + 1, b[0], b[1] + 1, rgb("#8a5a62"))
    shaded_ell(p, x + S(4), y + S(16), S(12), S(15), fur)
    shaded_ell(p, x - S(4), y + S(4), S(8), S(7), fur)
    p.poly([(x - S(14), y + S(6)), (x - S(8), y + S(3)), (x - S(6), y + S(10)), (x - S(13), y + S(8))], fur[3])
    p.rect(x - S(15), y + S(6), 2, 2, rgb("#e8a0a8"))
    ell(p, x - S(1), y - S(2), S(3), S(3), pink); ell(p, x + S(5), y, S(3), S(3), pink)
    p.px(x - S(1), y - S(2), fur[2]); p.px(x + S(5), y, fur[2])
    p.rect(x - S(7), y + S(3), 2, 2, rgb("#0a0810")); p.px(x - S(7), y + S(3), rgb("#e8d8d8"))
    p.hline(x - S(17), y + S(8), 3, rgb("#c8c0c4")); p.hline(x - S(18), y + S(10), 4, fur[4])
    p.rect(x - S(8), y + S(16), 4, S(11), fur[3]); p.rect(x - S(9), y + S(26), 5, 2, pink)
    p.rect(x + S(4), y + S(26), S(10), 3, fur[2]); p.hline(x + S(4), y + S(28), S(10), pink)
    p.vline(x - S(3), y + S(8), S(12), fur[4])


def crate(p: Pix) -> None:
    p.rect(0, 492, 78, 48, rgb("#2a1214"))
    plank_rect(p, 0, 494, 76, 46, ramp("#2a1214", "#4a2020", "#6a2e28", "#8a3e30", "#a85a40"), vertical=False, board=9, seed=3)
    p.rect(75, 494, 3, 46, rgb("#1a0a0c")); p.hline(0, 492, 78, rgb("#c87a50"))
    p.rect(8, 482, 12, 10, rgb("#3a1a12")); p.rect(11, 470, 6, 14, rgb("#4a2a1a")); p.hline(10, 466, 8, rgb("#8a5a34"))
    p.rect(11, 474, 2, 8, rgb("#d09a6a"))
    p.rect(8, 484, 12, 6, rgb("#d8c490"))
    # foreground gutter pipe along the bottom edge
    iron = ramp("#12111a", "#1e1d2a", "#2c2b3c", "#403f56", "#5a5878")
    p.rect(100, 512, 380, 20, iron[1]); p.hline(100, 512, 380, iron[4]); p.hline(100, 514, 380, iron[3]); p.hline(100, 531, 380, iron[0])
    for x in range(100, 480, 70):
        p.rect(x, 510, 6, 24, iron[2]); p.vline(x, 510, 24, iron[4])
