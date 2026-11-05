"""Bazaar picture, middle ground: the inn with its painted signs, the timber stair and gallery, the food stall, the far end.

Everything here sits behind the left shop and in front of the haze. Light: moon from the upper left (cool), lanterns warm.
"""

from __future__ import annotations

import math

from mnu_bazaar_kit import (BRICKRED, CREAM, DKWOOD, PLUM, SLATE, TEAL, beam, ell, haze, lantern, plank_rect, pool, ramp, shaded_ell,
                            shade, silhouette, text)
from pix import Pix, mix, rgb

RIM = rgb("#4f9aa0")        # cool moon rim on figures
RIM_D = rgb("#2d6068")
INK = rgb("#120e18")


def curve(a: tuple[float, float], c: tuple[float, float], b: tuple[float, float], n: int = 14) -> list[tuple[int, int]]:
    """A quadratic bend (for roof eaves that sweep up at the tips)."""
    return [(int(round((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0])),
             int(round((1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]))) for t in (i / n for i in range(n + 1))]


def tiles(p: Pix, pts: list[tuple[int, int]], base: str, seed: int) -> None:
    """Roof tiles in a polygon: scalloped rows, each tone drifting, a lit lower lip on every row."""
    rp = ramp(*{"teal": ("#0e1d22", "#17323a", "#234850", "#33636a", "#4f8a8c"),
                "red": ("#2a0f14", "#4a161c", "#6e2224", "#903230", "#b04a3c")}[base])
    p.poly(pts, rp[1])
    from PIL import Image, ImageDraw
    m = Image.new("L", p.im.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    bb = m.getbbox()
    if not bb:
        return
    for y in range(bb[1], bb[3]):
        row = (y - bb[1]) // 4
        for x in range(bb[0], bb[2]):
            if not m.getpixel((x, y)):
                continue
            ph = (y - bb[1]) % 4
            xo = (x + (row % 2) * 3) % 6
            tone = 2 + ((x * 7 + row * 13 + seed) % 5 == 0) - (ph == 0) - (xo == 0)
            if ph == 3:
                tone = 3 if xo else 1
            if ph == 0:
                tone = 0
            p.px(x, y, rp[max(0, min(4, tone))])


def inn(p: Pix) -> None:
    """The two-storey inn behind the stall: red-painted timber, curved tiled roof, the Rose Inn portrait board."""
    wall = BRICKRED
    p.rect(527, 124, 175, 160, wall[1])
    plank_rect(p, 527, 150, 175, 130, [rgb(h) for h in ("#1a0d12", "#2a1218", "#37171d", "#451c22", "#552528")], vertical=True, board=7, seed=3)
    # timber frame: posts and rails with a lit left edge
    for x in (527, 560, 600, 668, 698):
        p.rect(x, 124, 4, 160, DKWOOD[1]); p.vline(x, 124, 160, DKWOOD[3])
    for y in (150, 232, 280):
        p.rect(527, y, 175, 4, DKWOOD[1]); p.hline(527, y, 175, DKWOOD[4]); p.hline(527, y + 3, 175, DKWOOD[0])
    # lit lattice window on the right of the upper storey
    p.rect(672, 182, 26, 48, DKWOOD[0])
    for gy in range(184, 228, 11):
        for gx in range(674, 696, 8):
            p.rect(gx, gy, 6, 9, mix(rgb("#8a4a3a"), rgb("#d28a5a"), (gy % 3) / 3))
            p.hline(gx, gy, 6, rgb("#e6b078"))
    pool(p, 685, 206, 26, 34, rgb("#a05030"), 0.45)
    # roof of the tower and the sweeping eave
    eave = curve((706, 160), (660, 160), (590, 126), 16) + curve((590, 126), (560, 110), (535, 132), 8)
    roof = eave + curve((540, 142), (590, 130), (706, 172), 16)[::1]
    tiles(p, roof, "teal", 5)
    for pt in curve((540, 142), (590, 130), (706, 172), 16):
        p.px(pt[0], pt[1] + 1, rgb("#8a3030")); p.px(pt[0], pt[1] + 2, rgb("#5a1c20"))
    p.rect(573, 98, 38, 26, rgb("#13262c"))          # the tower box
    p.frame(573, 98, 38, 26, DKWOOD[3])
    for i, c in enumerate(("#2a6f78", "#1f565f")):
        p.rect(577, 101 + i * 11, 30, 9, rgb(c)); p.hline(577, 101 + i * 11, 30, rgb("#5fa8aa"))
    # a fish sign and a loaf sign in the tower
    p.poly([(581, 106), (589, 103), (597, 106), (589, 108)], rgb("#a8d8d0")); p.px(583, 106, INK)
    for x in (586, 592, 598):
        p.px(x, 113, rgb("#a8d8d0")); p.px(x + 1, 114, rgb("#a8d8d0"))
    # weather vane on the tower
    p.vline(592, 84, 14, INK); p.hline(586, 90, 12, INK)
    p.poly([(598, 86), (604, 88), (598, 90)], rgb("#c89a3c"))
    p.px(586, 90, rgb("#c89a3c"))
    # curved eave tips and finials
    p.poly([(700, 164), (708, 156), (705, 166)], rgb("#c89a3c"))
    p.poly([(534, 134), (527, 126), (532, 138)], rgb("#c89a3c"))
    # the Rose Inn portrait board
    portrait(p, 590, 145, 66, 60)
    # fish-seller's painted board
    p.rect(597, 211, 54, 36, DKWOOD[0]); p.rect(599, 213, 50, 32, TEAL[2]); p.hline(599, 213, 50, TEAL[4]); p.vline(599, 213, 32, TEAL[3])
    p.hline(599, 244, 50, TEAL[0])
    for fx, fy, dir_ in ((612, 224, 1), (633, 230, -1), (625, 217, 1)):
        for k in range(-5, 6):
            hh = int(3 * math.sqrt(max(0, 1 - (k / 5) ** 2)))
            p.vline(fx + k * dir_, fy - hh, hh * 2 + 1, rgb("#0f2a30"))
        p.poly([(fx - 5 * dir_, fy), (fx - 9 * dir_, fy - 3), (fx - 9 * dir_, fy + 3)], rgb("#0f2a30"))
        p.px(fx + 3 * dir_, fy - 1, rgb("#bfe8e0"))
        p.hline(fx - 3 * dir_ if dir_ > 0 else fx, fy - 2, 4, rgb("#3c8a8a"))
    # a bill pasted on the inn wall
    p.rect(541, 178, 30, 38, rgb("#6d4a86")); p.hline(541, 178, 30, rgb("#a07ac0")); p.vline(541, 178, 38, rgb("#8a64a8"))
    text(p, 545, 184, "FAIR", rgb("#f0d8ff")); text(p, 545, 194, "WIN", rgb("#ffe08a"))
    for i in range(3):
        p.hline(545, 206 + i * 3, 22, rgb("#c8a8e0"))
    # upper balcony with a red railing
    balcony(p, 527, 262, 150)
    # hanging green cloth awning, torn at its hem
    for y in range(218, 284):
        w = 52 - (y - 218) // 4
        for x in range(527, 527 + w):
            fold = (x + (y // 6)) % 9
            tone = 1 + (fold < 3) + (fold == 0)
            p.px(x, y, ramp("#0c1c18", "#143026", "#1f4636", "#2c5e48")[tone])
    p.poly([(527, 284), (560, 284), (545, 273), (527, 276)], rgb("#0c1c18"))
    haze(p, 527, 120, 180, 170, rgb("#2a2640"), 0.0, 0.22)


def portrait(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A big painted signboard with a woman holding a rose: the inn's sign, framed and nailed to the timber."""
    p.rect(x - 3, y - 3, w + 6, h + 6, INK)
    p.rect(x - 2, y - 2, w + 4, h + 4, DKWOOD[3]); p.hline(x - 2, y - 2, w + 4, DKWOOD[4]); p.vline(x - 2, y - 2, h + 4, DKWOOD[4])
    p.rect(x, y, w, h, TEAL[2])
    p.hline(x, y, w, TEAL[3]); p.vline(x, y, h, TEAL[3])
    for i in range(0, w, 3):
        p.px(x + i, y + 2 + (i % 2), TEAL[4])
    cx = x + w // 2
    # hair, shoulders, face
    shaded_ell(p, cx, y + 24, 20, 20, ramp("#2e1a1c", "#4a2a24", "#6e402c", "#92603a"))
    p.rect(cx - 17, y + 26, 6, 18, rgb("#4a2a24"))
    p.rect(cx + 11, y + 26, 6, 18, rgb("#4a2a24"))
    p.poly([(cx - 18, y + 46), (cx - 12, y + 40), (cx + 12, y + 40), (cx + 18, y + 46), (cx + 20, y + 56), (cx - 20, y + 56)], rgb("#6a4a9a"))
    p.hline(cx - 12, y + 40, 25, rgb("#9a7ac8"))
    p.rect(cx - 3, y + 36, 7, 6, rgb("#c89070"))
    shaded_ell(p, cx, y + 27, 8, 11, ramp("#6a4030", "#a56a4c", "#d49a72", "#efc298"))
    for ex in (-4, 3):
        p.hline(cx + ex, y + 25, 3, rgb("#2a1a1c")); p.px(cx + ex + 1, y + 26, rgb("#4a2a24"))
    p.hline(cx - 2, y + 33, 5, rgb("#a8403c"))
    p.poly([(cx - 8, y + 18), (cx, y + 15), (cx + 8, y + 18), (cx + 8, y + 21), (cx, y + 18), (cx - 8, y + 21)], rgb("#5a3424"))
    for sx, sy in ((x + 8, y + 12), (x + w - 9, y + 18), (x + w - 14, y + 34)):   # painted sparkles
        p.px(sx, sy, rgb("#e8f8f0")); p.vline(sx, sy - 2, 5, rgb("#b8e0d8")); p.hline(sx - 2, sy, 5, rgb("#b8e0d8"))
    p.rect(cx + 12, y + 44, 4, 4, rgb("#d03a4a"))        # the rose
    p.px(cx + 13, y + 45, rgb("#ff8a8a"))
    p.rect(x, y + h - 9, w, 9, rgb("#1a1424"))
    text(p, x + (w - 47) // 2, y + h - 8, "ROSE INN", rgb("#f0e4c4"))
    for nx, ny in ((x - 1, y - 1), (x + w, y - 1), (x - 1, y + h), (x + w, y + h)):
        p.px(nx, ny, rgb("#a89060"))


def balcony(p: Pix, x: int, y: int, w: int) -> None:
    """A first-floor balcony: floor boards, a red turned-baluster rail and its handrail, bracketed to the wall."""
    p.rect(x, y + 14, w, 4, DKWOOD[2]); p.hline(x, y + 14, w, DKWOOD[4]); p.hline(x, y + 17, w, DKWOOD[0])
    for bx in range(x + 8, x + w, 30):
        p.poly([(bx, y + 18), (bx + 8, y + 18), (bx, y + 26)], DKWOOD[1])
    for bx in range(x + 2, x + w, 5):
        p.vline(bx, y + 3, 11, BRICKRED[3]); p.px(bx, y + 3, BRICKRED[4]); p.px(bx, y + 8, BRICKRED[2])
    p.rect(x, y, w, 3, BRICKRED[2]); p.hline(x, y, w, BRICKRED[4]); p.hline(x, y + 2, w, BRICKRED[0])


def post(p: Pix, x: int, y0: int, y1: int, w: int = 5, rp=DKWOOD) -> None:
    p.rect(x, y0, w, y1 - y0, rp[2]); p.vline(x, y0, y1 - y0, rp[4]); p.vline(x + w - 1, y0, y1 - y0, rp[0])
    for yy in range(y0 + 6, y1, 13):
        p.px(x + 2, yy, rp[0])


def stair(p: Pix) -> None:
    """The outdoor timber stair in two flights with a landing, rails and balusters, up to the gallery."""
    ST = ramp("#0e0d16", "#181826", "#262838", "#3a3f54", "#566078")
    # dark void under the lower flight, with its supports
    p.poly([(664, 300), (748, 412), (700, 412), (668, 372)], rgb("#0c0a14"))
    post(p, 668, 296, 412, 5, ST); post(p, 700, 340, 412, 4, ST)
    beam(p, 670, 330, 700, 372, 3, ST); beam(p, 700, 346, 672, 392, 3, ST)
    # upper flight (landing -> gallery): stringer, treads, rails
    def flight(x0, y0, x1, y1, n, back: bool) -> None:
        for i in range(n):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            p.rect(int(x), int(y), 12, 2, ST[4] if not back else ST[3])
            p.hline(int(x), int(y), 12, rgb("#7a86a0") if not back else ST[4])
            p.rect(int(x), int(y) + 2, 12, 3, ST[1])
        beam(p, x0 + 6, y0 + 6, x1 + 6, y1 + 6, 4, ST)
    # back flight first (the far rail of each flight), then the near one
    flight(668, 292, 724, 238, 12, True)
    flight(660, 296, 744, 408, 20, False)
    # balusters and handrails (the near side)
    for x0, y0, x1, y1, n in ((668, 270, 724, 216, 12), (662, 276, 748, 388, 22)):
        for i in range(n + 1):
            t = i / n
            x, y = int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)
            p.vline(x, y, 24, ST[3] if i % 2 else ST[2])
        beam(p, x0, y0, x1, y1, 3, ST)
        beam(p, x0, y0 + 20, x1, y1 + 20, 2, ST)
    # newel posts with caps
    for x, y0, y1 in ((662, 262, 300), (746, 376, 412), (724, 216, 250)):
        post(p, x, y0, y1, 4, ST)
        p.rect(x - 1, y0 - 2, 6, 3, ST[4])
    # the landing deck
    p.rect(655, 292, 24, 4, DKWOOD[3]); p.hline(655, 292, 24, DKWOOD[4]); p.hline(655, 295, 24, DKWOOD[0])
    # a figure climbing the upper flight (dark, with a cool rim)
    silhouette(p, [(681, 258), (685, 252), (689, 254), (691, 262), (693, 276), (688, 280), (683, 268)], rgb("#0a0810"), RIM_D)
    ell(p, 687, 249, 3, 3, rgb("#0a0810"))


def gallery(p: Pix) -> None:
    """The gallery over the shopfront: floor beam, rail, a small roofed doorway with warm light, a standing figure."""
    # wall below with its signboards, lit shop window and a canopy
    p.rect(722, 254, 128, 90, PLUM[1])
    plank_rect(p, 722, 254, 128, 90, ramp("#0e0b16", "#18132a", "#211a38", "#2c2348", "#3a2f5a"), vertical=False, board=6, seed=9)
    p.rect(722, 244, 128, 10, DKWOOD[2]); p.hline(722, 244, 128, DKWOOD[4]); p.hline(722, 253, 128, DKWOOD[0])
    for x, kind in ((734, "loaf"), (761, "ale"), (788, "fish")):
        p.rect(x - 1, 261, 25, 14, INK)
        p.rect(x, 262, 23, 12, rgb("#5a2a46")); p.hline(x, 262, 23, rgb("#9a5a86")); p.vline(x, 262, 12, rgb("#7a3e66"))
        if kind == "loaf":
            ell(p, x + 11, 268, 7, 3, rgb("#d9a15a")); p.hline(x + 6, 266, 10, rgb("#f0c27a"))
            for k in (7, 11, 15):
                p.px(x + k, 267, rgb("#9a6a34"))
        elif kind == "ale":
            p.rect(x + 8, 265, 7, 7, rgb("#e8b83a")); p.rect(x + 8, 264, 7, 2, rgb("#f6f0d8")); p.vline(x + 15, 266, 4, rgb("#c89a2c"))
        else:
            ell(p, x + 11, 268, 7, 3, rgb("#a8c8d8")); p.poly([(x + 17, 268), (x + 21, 265), (x + 21, 271)], rgb("#a8c8d8")); p.px(x + 7, 267, INK)
    p.rect(727, 277, 78, 8, BRICKRED[2]); p.hline(727, 277, 78, BRICKRED[4])
    for x in range(727, 805, 6):
        p.rect(x, 283, 3, 3, BRICKRED[1])
    p.rect(729, 288, 74, 38, INK)                                           # shop opening, cool light inside
    p.rect(731, 290, 70, 34, rgb("#1f4a52"))
    p.dither(731, 290, 70, 34, rgb("#2f6a70"), 0.35)
    for hx in range(736, 798, 9):                                          # the crowd inside: heads and shoulders
        hh = 296 + (hx * 5) % 6
        ell(p, hx, hh, 3, 3, rgb("#0c1820")); p.rect(hx - 5, hh + 4, 11, 30, rgb("#0c1820"))
    p.rect(731, 290, 70, 2, rgb("#3f8a8c"))
    p.hline(729, 326, 74, DKWOOD[3])
    # gallery floor and rail
    p.rect(722, 244, 128, 2, DKWOOD[4])
    for x in range(724, 850, 8):
        p.vline(x, 228, 16, BRICKRED[3]); p.px(x, 228, BRICKRED[4])
    p.rect(722, 227, 128, 3, BRICKRED[2]); p.hline(722, 227, 128, BRICKRED[4])
    p.rect(722, 238, 128, 2, BRICKRED[1])
    # the little roofed doorway with warm panes
    p.rect(756, 190, 70, 56, rgb("#3a1a1e"))
    p.rect(763, 205, 56, 40, INK)
    for gx in range(765, 817, 9):
        for gy in range(207, 243, 9):
            p.rect(gx, gy, 7, 7, mix(rgb("#c25a2a"), rgb("#f2a24a"), ((gx + gy) % 5) / 5))
    p.vline(763, 205, 40, rgb("#a8402a")); p.vline(818, 205, 40, rgb("#a8402a"))
    pool(p, 790, 226, 48, 34, rgb("#a05020"), 0.7)
    for x in (756, 790, 824):
        post(p, x, 200, 246, 4, BRICKRED)
    tiles(p, curve((748, 192), (790, 184), (834, 192), 12) + [(826, 176), (790, 164), (756, 176)], "red", 2)
    p.poly([(748, 192), (742, 184), (752, 188)], rgb("#c89a3c")); p.poly([(834, 192), (840, 184), (830, 188)], rgb("#c89a3c"))
    p.poly([(786, 164), (790, 156), (794, 164)], rgb("#c89a3c"))
    p.rect(767, 197, 48, 6, rgb("#2a1014")); p.hline(767, 197, 48, rgb("#9a3a30"))
    # a lantern hanging in the pavilion door
    lantern(p, 790, 199, 4, 4, "orange", tassel=False)
    silhouette(p, [(804, 246), (803, 232), (801, 224), (805, 220), (809, 224), (809, 232), (810, 246)], rgb("#0a0810"), None)
    ell(p, 805, 217, 3, 3, rgb("#0a0810"))
    # a small guild shield under the doorway eave
    p.poly([(816, 192), (824, 192), (824, 199), (820, 204), (816, 199)], rgb("#c89a3c")); p.poly([(818, 194), (822, 194), (822, 199), (820, 201), (818, 199)], rgb("#3a2a6a"))
    haze(p, 722, 160, 130, 180, rgb("#2a2640"), 0.05, 0.3)


def stall(p: Pix) -> None:
    """The food stall: a pole-and-tile awning with upturned eaves, a lit back window, a red trestle table, stools, diners."""
    # pole carrying the lantern strings, the stall's roof posts
    post(p, 576, 228, 420, 5, DKWOOD)
    post(p, 664, 330, 420, 4, DKWOOD)
    # back wall with a lit glazed window (cool teal against the warm lanterns)
    p.rect(578, 332, 86, 88, rgb("#0f1822"))
    p.rect(590, 338, 62, 38, rgb("#173a40"))
    p.dither(590, 338, 62, 38, rgb("#2a6a70"), 0.4)
    for x in range(590, 653, 15):
        p.vline(x, 338, 38, rgb("#0c1c22"))
    p.hline(590, 357, 62, rgb("#0c1c22")); p.hline(590, 338, 62, rgb("#4f9aa0"))
    pool(p, 622, 358, 46, 30, rgb("#2a8a90"), 0.5)
    # hung pots and a ladle on the back wall
    for hx in (595, 640):
        p.vline(hx, 381, 4, INK); shaded_ell(p, hx, 389, 5, 5, ramp("#1a1a24", "#2c2e3c", "#444a5a", "#6a7288"))
    # awning: sloped tiled roof with upturned eaves and a scalloped red-and-cream valance
    tiles(p, curve((560, 318), (620, 306), (672, 318), 12) + [(680, 314), (672, 322), (560, 322)], "red", 4)
    p.poly([(560, 318), (553, 311), (565, 316)], rgb("#c89a3c")); p.poly([(672, 318), (680, 310), (669, 316)], rgb("#c89a3c"))
    for i, x in enumerate(range(562, 672, 7)):
        c = rgb("#c04a2c") if i % 2 == 0 else rgb("#e8cf9a")
        p.rect(x, 322, 7, 6, c); p.hline(x, 322, 7, mix(c, (255, 255, 255), 0.25)); p.poly([(x, 328), (x + 6, 328), (x + 3, 331)], c)
    p.hline(560, 321, 112, rgb("#2a0f14"))
    # little cooking pot on a tripod at the left, with steam
    for dx in (-8, 0, 8):
        beam(p, 539 + dx // 2, 352, 539 + dx, 388, 2, ramp("#0e0d16", "#181826", "#262838", "#3a3f54", "#566078"))
    shaded_ell(p, 539, 346, 10, 9, ramp("#14141c", "#24262f", "#383c48", "#586070"))
    p.hline(530, 338, 18, rgb("#6a7488")); p.hline(531, 339, 16, rgb("#10101a"))
    p.rect(538, 392, 18, 4, rgb("#c8561e")); p.px(540, 391, rgb("#ffb050")); p.px(546, 391, rgb("#ffd07a"))
    pool(p, 540, 394, 22, 14, rgb("#b04a18"), 0.7)
    for i, (sx, sy) in enumerate(((540, 332), (543, 326), (539, 320), (542, 314))):
        p.dither(sx - 3, sy, 7, 4, rgb("#6a6a84"), 0.4 - i * 0.07)
    # menu board on a post: a slate on legs with chalk lines
    p.rect(550, 346, 28, 38, DKWOOD[1]); p.rect(552, 348, 24, 34, rgb("#d8cdb0")); p.hline(552, 348, 24, rgb("#f4ecd4")); p.vline(552, 348, 34, rgb("#eae0c4"))
    for i, w in enumerate((18, 14, 18, 10, 16)):
        p.hline(554, 353 + i * 4, w, rgb("#4a3e3a"))
    p.poly([(556, 376), (570, 376), (566, 379), (556, 379)], rgb("#4a3e3a"))
    beam(p, 555, 384, 553, 405, 3, DKWOOD); beam(p, 572, 384, 575, 405, 3, DKWOOD)
    # whitewashed stone trough
    p.rect(535, 396, 52, 28, rgb("#6a6c7c")); p.hline(535, 396, 52, rgb("#a8aab8")); p.vline(535, 396, 28, rgb("#8a8ca0"))
    p.rect(535, 418, 52, 6, rgb("#3a3c4c")); p.rect(540, 400, 42, 14, rgb("#242632"))
    p.hline(540, 400, 42, rgb("#14141e"))
    # trestle table (red), stools (red), diners
    for sx in (597, 653):
        p.rect(sx, 406, 14, 3, rgb("#a03c2c")); p.hline(sx, 406, 14, rgb("#d0644a")); p.vline(sx + 2, 409, 14, rgb("#6a241e")); p.vline(sx + 11, 409, 14, rgb("#6a241e"))
    diner(p, 596, 360, True)
    diner(p, 648, 364, False)
    p.rect(610, 398, 50, 4, rgb("#c04a34")); p.hline(610, 398, 50, rgb("#f08a5a")); p.hline(610, 402, 50, rgb("#6a241e"))
    p.vline(614, 402, 22, rgb("#8a2e24")); p.vline(655, 402, 22, rgb("#8a2e24"))
    beam(p, 614, 424, 626, 410, 2, ramp("#2a0f14", "#4a161c", "#6e2224", "#903230", "#b04a3c")); beam(p, 655, 424, 643, 410, 2, ramp("#2a0f14", "#4a161c", "#6e2224", "#903230", "#b04a3c"))
    # food, a jug and mugs on the table
    ell(p, 636, 396, 6, 2, rgb("#e8d8a8")); p.hline(631, 395, 10, rgb("#f6ecc8")); p.px(634, 394, rgb("#a8402a")); p.px(638, 394, rgb("#7a9a3a"))
    p.rect(620, 388, 4, 10, rgb("#6a8a3a")); p.rect(621, 386, 2, 3, rgb("#6a8a3a")); p.px(620, 390, rgb("#b8d870"))
    p.rect(626, 391, 4, 7, rgb("#d8962c")); p.px(626, 391, rgb("#f8d070"))
    pool(p, 636, 395, 26, 14, rgb("#b06a28"), 0.55)
    # rim lights on diners (re-drawn after glow so they stay crisp)
    for x, y in ((596, 360), (648, 364)):
        pass
    # red stools
    for sx in (627, 662):
        p.rect(sx, 413, 10, 3, rgb("#c04a34")); p.hline(sx, 413, 10, rgb("#f08a5a")); p.vline(sx + 1, 416, 8, rgb("#7a281e")); p.vline(sx + 8, 416, 8, rgb("#7a281e"))


def diner(p: Pix, x: int, y: int, left: bool) -> None:
    """A seated diner in silhouette with a hood or cap, a rim of moon-cyan on the side that faces the window."""
    body = rgb("#0a0810")
    if left:
        pts = [(x + 4, y + 62), (x + 2, y + 30), (x + 4, y + 18), (x + 12, y + 14), (x + 22, y + 18), (x + 26, y + 30), (x + 34, y + 42), (x + 40, y + 44), (x + 38, y + 48), (x + 28, y + 46), (x + 24, y + 62)]
        silhouette(p, pts, body, RIM, "l")
        ell(p, x + 14, y + 8, 7, 8, body)
        p.vline(x + 7, y + 3, 10, RIM); p.poly([(x + 8, y), (x + 14, y - 2), (x + 21, y + 1)], body); p.hline(x + 9, y - 2, 6, RIM_D)
    else:
        pts = [(x + 6, y + 58), (x + 4, y + 36), (x + 8, y + 22), (x + 16, y + 14), (x + 28, y + 16), (x + 36, y + 26), (x + 40, y + 40), (x + 40, y + 58), (x + 32, y + 62), (x + 12, y + 62)]
        silhouette(p, pts, body, RIM, "l")
        ell(p, x + 20, y + 8, 8, 8, body)
        p.vline(x + 12, y + 3, 10, RIM); p.hline(x + 14, y, 6, RIM_D)
        p.poly([(x - 2, y + 40), (x + 6, y + 36), (x + 10, y + 44), (x, y + 46)], body)


def far_end(p: Pix) -> None:
    """The far end of the lane: dark buildings, a warm open doorway far off and a tiny figure in it."""
    p.rect(738, 330, 42, 84, rgb("#0c0a16"))
    p.rect(742, 366, 14, 44, rgb("#6a3418")); p.rect(744, 368, 10, 42, rgb("#c0642a")); p.vline(745, 370, 40, rgb("#f09a4a")); p.vline(752, 372, 38, rgb("#8a4018"))
    p.dither(744, 368, 10, 42, rgb("#f6b660"), 0.25)
    pool(p, 750, 392, 34, 32, rgb("#a05020"), 0.6)
    p.rect(748, 392, 3, 18, rgb("#0a0810")); ell(p, 749, 389, 2, 2, rgb("#0a0810"))
    p.rect(754, 396, 2, 14, rgb("#0a0810")); p.rect(754, 394, 2, 2, rgb("#0a0810"))
    # a street sign: a small hanging board with a glyph
    p.rect(730, 348, 8, 14, rgb("#244a50")); p.frame(730, 348, 8, 14, TEAL[4])
    p.hline(732, 352, 4, TEAL[4]); p.hline(732, 355, 4, TEAL[4]); p.hline(732, 358, 3, TEAL[4])
    # hanging bundles on the stair post: a green round sign (the swan)
    p.rect(766, 331, 2, 8, DKWOOD[1])
    ell(p, 770, 344, 9, 9, rgb("#14281c")); ell(p, 770, 344, 7, 7, rgb("#2f6a44"))
    p.poly([(765, 348), (770, 345), (775, 342), (775, 340), (773, 338), (772, 342), (768, 345), (765, 346)], rgb("#e4f0e0"))
    p.px(775, 339, rgb("#e0a030"))
