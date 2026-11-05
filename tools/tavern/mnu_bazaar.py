"""bazaar.960x540.png: the title picture, a crowded market lane at night, drawn to the composition of the original.

Left a draper's shop under a big sign, mid-lane a food stall below a timber stair and gallery, right a hooded figure by
produce crates; lantern strings across the lane, cool moonlight against orange lantern light, wet cobbles.
Layers (back to front): backdrop and scaffold, far end, inn / gallery / stair, floor, stall, left wall and shop, right
side, lantern strings, glows, wet reflections, haze.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping

from PIL import Image

import mnu_bazaar_left as left
import mnu_bazaar_mid as mid
import mnu_bazaar_right as right
from mnu_bazaar_kit import BRICKRED, DKWOOD, PLUM, SLATE, beam, haze, lantern, pool, ramp
from pix import BAYER, Pix, mix, rgb

W, H = 960, 540
HORIZON = (730, 392)         # the vanishing point of the lane


def backdrop(p: Pix) -> None:
    """Night sky between the roofs, shaded down to the misty alley, plus the timber scaffold and the right jetty."""
    top, bot = rgb("#120f1e"), rgb("#2e2842")
    p.gradient(0, 0, W, 330, top, bot, 12)
    # timber scaffold in the dark upper centre
    sc = ramp("#0e0c16", "#16131f", "#201c2c", "#2c2840", "#3c3856")
    for x in (566, 626, 706, 770):
        p.rect(x, 0, 6, 135, sc[1]); p.vline(x, 0, 135, sc[3])
    for y in (30, 80, 128):
        p.rect(560, y, 224, 4, sc[1]); p.hline(560, y, 224, sc[3])
    for x0 in (566, 626, 706):
        x1 = {566: 626, 626: 706, 706: 770}[x0]
        beam(p, x0 + 3, 34, x1 + 3, 80, 3, sc); beam(p, x1 + 3, 34, x0 + 3, 80, 3, sc)
    # right: the underside of an overhanging upper floor, and a slanted shuttered wall
    p.poly([(780, 0), (960, 0), (960, 70), (905, 118), (780, 100)], rgb("#0e0c18"))
    for k in range(8):
        beam(p, 790 + k * 20, 100 - k * 2, 780 + k * 22, 0, 2, sc)
    p.poly([(905, 70), (960, 40), (960, 345), (905, 335)], rgb("#2c2038"))
    for k in range(26):
        y = 62 + k * 11
        tone = (k % 3)
        p.poly([(905, y), (960, y - 28), (960, y - 24), (905, y + 4)], (rgb("#4a3250"), rgb("#3c2a46"), rgb("#563a58"))[tone])
        p.line(905, y + 4, 960, y - 24, rgb("#1c1226"))
    p.rect(905, 70, 3, 265, rgb("#6a4a68")); p.vline(908, 70, 265, rgb("#3a2a48"))
    # chalk graffiti on the dark underside of the jetty
    chalk = rgb("#4a6a96")
    from mnu_bazaar_kit import ell, text
    ell(p, 837, 38, 11, 11, rgb("#0e0c18")); p.ellipse(826, 27, 23, 23, chalk); p.ellipse(827, 28, 21, 21, rgb("#0e0c18"))
    p.px(833, 34, chalk); p.px(842, 34, chalk); p.hline(833, 44, 9, chalk); p.px(832, 43, chalk); p.px(843, 43, chalk)
    text(p, 855, 14, "WAT", chalk); text(p, 855, 24, "WAS", chalk); text(p, 863, 34, "HERE", chalk)
    p.line(810, 46, 826, 50, chalk); p.line(826, 50, 836, 46, chalk)
    # recruiting banner hung from the jetty on two cords
    banner(p, 738, 0)


def banner(p: Pix, x: int, y: int) -> None:
    """A hanging cloth banner on a pole: the watch's recruiting notice (ENLIST / SERVE THE CROWN)."""
    p.rect(x - 2, y, 44, 4, DKWOOD[2]); p.hline(x - 2, y, 44, DKWOOD[4])
    p.vline(x + 4, y, 2, rgb("#14101a")); p.vline(x + 34, y, 2, rgb("#14101a"))
    p.rect(x, y + 4, 40, 80, rgb("#d6cdb6"))
    p.vline(x, y + 4, 80, rgb("#f2eadc")); p.vline(x + 39, y + 4, 80, rgb("#a89e8a")); p.hline(x, y + 83, 40, rgb("#8a8272"))
    p.poly([(x + 5, y + 8), (x + 35, y + 8), (x + 35, y + 22), (x + 20, y + 32), (x + 5, y + 22)], rgb("#a02a30"))
    p.poly([(x + 8, y + 10), (x + 32, y + 10), (x + 32, y + 21), (x + 20, y + 29), (x + 8, y + 21)], rgb("#c8403c"))
    for sx in (13, 20, 27):
        p.px(x + sx, y + 17, rgb("#f6e6b0"))
    p.hline(x + 8, y + 13, 24, rgb("#f6e6b0"))
    p.rect(x + 1, y + 36, 38, 11, rgb("#c0262e")); p.hline(x + 1, y + 36, 38, rgb("#e8605a"))
    from mnu_bazaar_kit import text
    text(p, x + 2, y + 39, "ENLIST", rgb("#fff4e0"))
    p.rect(x + 8, y + 52, 24, 1, rgb("#4a3a3a"))
    text(p, x + 6, y + 56, "SERVE", rgb("#3a2e34")); text(p, x + 7, y + 65, "CROWN", rgb("#3a2e34"))
    for i in range(0, 40, 4):
        p.poly([(x + i, y + 84), (x + i + 3, y + 84), (x + i + 1, y + 88)], rgb("#d6cdb6"))


def floor(p: Pix) -> None:
    """Wet cobbles in one-point perspective: rows widen toward the viewer, stones are staggered, wide dark joints."""
    rng = random.Random(41)
    vx, vy = HORIZON
    p.rect(0, 408, W, H - 408, rgb("#1a1726"))
    rows: list[float] = []
    y = 412.0
    while y < 500:
        rows.append(y)
        y += 2.5 + (y - 400) * 0.075
    stone = ramp("#15131f", "#1e1c2c", "#2a283c", "#363448", "#454258")
    for i, y0 in enumerate(rows):
        y1 = rows[i + 1] if i + 1 < len(rows) else 500
        scale = (y0 - vy) / 100.0 + 0.06
        sw = max(5.0, 34 * scale + 6)
        x = ((i * 0.37) % 1.0) * sw - sw
        while x < W:
            w = sw * (0.8 + rng.random() * 0.5)
            # perspective: stones' left/right edges lean toward the vanishing point
            lean = (x - vx) * (y1 - y0) / max(30.0, (y0 - vy) + 1)
            tone = rng.choice([1, 1, 2, 2, 3])
            xa, xb = int(x), int(x + w - 2)
            p.poly([(xa, int(y0)), (xb, int(y0)), (xb + int(lean * 0.5), int(y1) - 1), (xa + int(lean * 0.5), int(y1) - 1)], stone[tone])
            p.hline(xa + 1, int(y0), max(1, xb - xa - 1), stone[min(4, tone + 1)])
            if rng.random() < 0.4:
                p.px(xa + rng.randint(2, max(3, xb - xa - 2)), int(y0) + 1, stone[0])
            x += w
    # the foreground kerb and gutter strip
    p.rect(0, 495, W, 45, rgb("#1c1a2a"))
    p.hline(0, 495, W, rgb("#3a3850")); p.hline(0, 496, W, rgb("#2a2840"))
    p.rect(0, 506, W, 34, rgb("#14121e"))
    p.hline(0, 506, W, rgb("#2e2c44"))
    for k in range(0, W, 3):
        if (k // 3) % 5 == 0:
            p.px(k, 520, rgb("#2e2c44"))
    haze(p, 0, 412, W, 80, rgb("#2e2a46"), 0.5, 0.0)


def lantern_strings(p: Pix) -> None:
    """Rope strings tied on hooks to both facades, sagging across the lane, each carrying paper lanterns."""
    hook = rgb("#6a5a3c")
    strings = [
        ((529, 150), (576, 236), 10, [(0.45, "red", 5)]),
        ((576, 236), (668, 296), 18, [(0.2, "red", 5), (0.55, "orange", 4), (0.85, "red", 4)]),
        ((576, 244), (498, 330), 12, [(0.5, "red", 4)]),
        ((668, 296), (724, 240), 12, []),
        ((668, 292), (826, 262), 26, [(0.3, "red", 4), (0.62, "green", 4), (0.82, "red", 4)]),
        ((822, 214), (668, 284), 16, []),
        ((724, 210), (845, 270), 14, [(0.55, "red", 3)]),
        ((529, 262), (578, 244), 8, [(0.5, "orange", 3)]),
        ((664, 322), (790, 300), 14, [(0.4, "red", 3), (0.8, "orange", 3)]),
        ((578, 276), (664, 318), 12, [(0.3, "red", 3), (0.7, "red", 3)]),
        ((420, 250), (530, 270), 14, [(0.6, "red", 3)]),
    ]
    rp = ramp("#1a1210", "#2e2018", "#4a3424", "#6a4c32")
    for a, b, sag, lamps in strings:
        pts = []
        for i in range(0, 41):
            t = i / 40
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)))
        for x, y in pts:
            p.px(int(x), int(y), rp[2]); p.px(int(x), int(y) + 1, rp[0])
        for t, col, r in lamps:
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)
            p.vline(int(x), int(y), 3, rp[1])
            lantern(p, int(x), int(y) + 3, r, r + 2, col, tassel=r > 3)
        for end in (a, b):
            p.rect(end[0] - 1, end[1] - 1, 3, 3, hook)
            p.px(end[0] - 1, end[1] - 1, rgb("#b09a6a"))


def big_lanterns(p: Pix) -> None:
    """The big red lantern over the gallery, hung from the jetty by a cord and iron hook."""
    p.vline(826, 100, 52, rgb("#3a2a22")); p.rect(824, 98, 5, 3, rgb("#8a7a52"))
    lantern(p, 826, 150, 14, 16, "red")


def glows(p: Pix) -> None:
    """Lantern, window and neon light laid over everything drawn so far."""
    warm, hot, cool = rgb("#b2561e"), rgb("#d2722a"), rgb("#2a9a9a")
    for x, y, r, c, k in (
        (470, 78, 70, hot, 0.9), (826, 187, 62, hot, 0.85), (690, 170, 24, warm, 0.5), (715, 207, 22, warm, 0.55),
        (832, 270, 26, warm, 0.5), (800, 296, 26, warm, 0.55), (610, 260, 34, warm, 0.6), (582, 262, 20, warm, 0.5),
        (640, 296, 20, warm, 0.45), (700, 300, 20, warm, 0.4),
        (630, 372, 60, cool, 0.35), (880, 370, 30, cool, 0.5), (872, 245, 36, rgb("#9a9a30"), 0.55), (250, 190, 130, rgb("#3a7a84"), 0.4),
        (330, 330, 80, rgb("#3a7a84"), 0.3), (470, 420, 70, hot, 0.5),
    ):
        pool(p, x, y, r, r * 0.9, c, k)


def reflections(p: Pix) -> None:
    """Wet pavement: broken vertical streaks of lantern, window and lamp light that thin out downward, plus puddle glints."""
    from mnu_bazaar_kit import addlight
    rng = random.Random(77)
    src = [(630, rgb("#c8742c"), 46), (640, rgb("#c8742c"), 40), (545, rgb("#d86a20"), 30), (472, rgb("#d86a20"), 34),
           (826, rgb("#c8742c"), 26), (880, rgb("#3a9aa0"), 30), (748, rgb("#e08a3a"), 18), (270, rgb("#4aa8b0"), 90),
           (330, rgb("#4aa8b0"), 50), (200, rgb("#a8884a"), 40), (700, rgb("#b0602a"), 30), (860, rgb("#c0a838"), 34), (610, rgb("#c04a30"), 20)]
    for cx, col, wid in src:
        for x in range(cx - wid // 2, cx + wid // 2):
            d = abs(x - cx) / (wid / 2)
            if rng.random() > (1 - d) * 1.3:
                continue
            ln = rng.randint(14, 56)
            sway = rng.choice((0, 0, 0, 1, -1))
            for k in range(ln):
                y = 438 + k
                if y >= 494:
                    break
                a = (1 - d) ** 0.7 * (1 - k / ln) * 0.6
                if (k % 11) in (7, 8) or a < 0.06:
                    continue
                if a > 0.3 or (x + y) % 2 == 0:
                    addlight(p, x + (sway if k > ln // 2 else 0), y, col, a)
    for _ in range(50):
        x, y = rng.randint(250, 900), rng.randint(440, 492)
        p.hline(x, y, rng.randint(3, 11), rgb("#4a4a68"))


def draw() -> Image.Image:
    p = Pix(W, H, rgb("#120f1e"), seed=11)
    backdrop(p)
    mid.far_end(p)
    mid.inn(p)
    mid.gallery(p)
    right.back_wall(p)
    floor(p)
    left.pavement(p)
    mid.stair(p)
    mid.stall(p)
    left.mid_wall(p)
    left.shop(p)
    right.front(p)
    lantern_strings(p)
    big_lanterns(p)
    glows(p)
    reflections(p)
    right.figure_and_produce(p)
    left.foreground(p)
    haze(p, 380, 90, 340, 300, rgb("#2c2a44"), 0.0, 0.12)
    return p.finish().convert("RGBA")


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"bazaar.960x540.png": draw}
