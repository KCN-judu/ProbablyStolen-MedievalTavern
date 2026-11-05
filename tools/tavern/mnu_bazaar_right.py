"""Bazaar picture, right side: the glowing alchemist's lamp on its bracket, the cooper's nook, the hooded figure and the produce."""

from __future__ import annotations

import math
import random

import fxkit
from mnu_bazaar_kit import BRICKRED, DKWOOD, PLUM, SLATE, TEAL, beam, ell, haze, plank_rect, pool, ramp, shaded_ell, silhouette, text
from pix import Pix, mix, rgb

INK = rgb("#0a0812")
RIM = rgb("#4f9aa0")
RIM_D = rgb("#2d6068")


def back_wall(p: Pix) -> None:
    """The dark right-hand house face with the cooper's lit nook; behind the stair and the lamp."""
    wall = ramp("#0e0c16", "#16131f", "#1e1a2a", "#2a2438", "#383048")
    p.rect(848, 96, 60, 340, wall[1])
    plank_rect(p, 848, 96, 60, 340, wall, vertical=True, board=12, seed=7)
    # cooper's nook (teal-lit doorway) with two tuns showing their round heads, as the original's machines
    p.rect(866, 292, 42, 130, rgb("#0a1a20"))
    p.rect(870, 296, 36, 124, rgb("#1f5a60")); p.dither(870, 296, 36, 124, rgb("#2f7a80"), 0.35)
    p.vline(870, 296, 124, rgb("#6ab8b8")); p.hline(870, 296, 36, rgb("#6ab8b8"))
    for cy, r in ((338, 17), (388, 17)):
        ell(p, 889, cy, r + 2, r + 2, rgb("#1a1018"))
        shaded_ell(p, 889, cy, r, r, ramp("#3a2a1e", "#5a4028", "#7a5a38", "#9a7448", "#b89058"))
        for k in (5, 9, 13):
            p.ellipse(int(889 - k), int(cy - k), 2 * k + 1, 2 * k + 1, rgb("#3a2a1e"))
        ell(p, 889, cy, 6, 6, rgb("#5a4028")); ell(p, 889, cy, 3, 3, rgb("#2a1a14")); p.px(888, cy - 1, rgb("#c89a60"))
        p.hline(889 - r, cy, 2 * r, rgb("#2a1a14")) if False else None
    p.hline(870, 417, 36, rgb("#0a1a20"))
    pool(p, 888, 360, 36, 56, rgb("#2a8a90"), 0.45)


def front(p: Pix) -> None:
    """Hanging alchemist's lamp (replacing the neon sign), the refuse barrel, sacks and a notice."""
    # bracket: iron post up the wall, curled arm, two chains to the lamp box
    iron = ramp("#12111a", "#1e1d2a", "#2c2b3c", "#403f56", "#6a6880")
    p.rect(846, 120, 4, 100, iron[2]); p.vline(846, 120, 100, iron[4]); p.vline(849, 120, 100, iron[0])
    beam(p, 848, 188, 866, 202, 3, iron); beam(p, 866, 202, 893, 198, 3, iron)
    for x, y0 in ((860, 204), (889, 200)):
        for k in range(5):
            p.rect(x, y0 + k * 3, 2, 2, iron[4] if k % 2 else iron[3])
    # the lamp: tall glass box in a rose-iron frame, a pale amber glow with a bright diagonal stripe
    frame = ramp("#3a1a3a", "#6a2a5a", "#9a3e7a", "#c25a98", "#e07ab8")
    x, y, w, h = 852, 218, 40, 60
    p.rect(x, y, w, h, frame[1])
    p.rect(x + 3, y + 3, w - 6, h - 6, rgb("#201a14"))
    for yy in range(y + 4, y + h - 3):
        for xx in range(x + 4, x + w - 4):
            d = (xx - x) * 0.42 + (yy - y) * 0.9 - 24
            tone = "#f6e8a0" if 0 <= d % 40 < 7 else ("#c8a850" if 0 <= d % 40 < 14 else "#8a6a2c")
            p.px(xx, yy, rgb(tone))
    p.frame(x + 3, y + 3, w - 6, h - 6, rgb("#18121a"))
    p.hline(x, y, w, frame[4]); p.vline(x, y, h, frame[3]); p.hline(x, y + h - 1, w, frame[0]); p.vline(x + w - 1, y, h, frame[0])
    p.hline(x + 1, y + 2, w - 2, frame[3]); p.rect(x + 16, y - 3, 8, 3, frame[3])
    for cx, cy in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
        p.rect(cx, cy, 2, 2, rgb("#e8c860"))
    pool(p, 872, 248, 40, 52, rgb("#b0a838"), 0.55)
    # small notice at the far right wall
    p.rect(935, 240, 16, 36, rgb("#d8d0c0")); p.hline(935, 240, 16, rgb("#f4ecd8")); text(p, 937, 244, "DUE", rgb("#b8281e"))
    for i in range(5):
        p.hline(937, 253 + i * 4, 12 if i % 2 else 8, rgb("#6a5a4a"))
    # a refuse barrel with herb sprigs at the stair's foot, and two sacks of rubbish
    p.rect(690, 392, 26, 24, rgb("#0a0812"))
    for k in range(26):
        u = (k - 13) / 13
        hh = 24 - int(2 * u * u)
        tone = ramp("#10201a", "#1c3a2a", "#2c5a3e", "#44805a")[max(0, min(3, int(2.4 - u * 1.8 + (1 if k == 2 else 0))))]
        p.vline(690 + k, 392 + (k // 20), hh, tone)
    for y in (396, 410):
        p.hline(690, y, 26, rgb("#0c1810")); p.hline(690, y + 1, 26, rgb("#4a8a62"))
    for sx, sy, c in ((695, 387, "#6a5aa0"), (702, 384, "#e090b0"), (708, 388, "#7a5aa0"), (699, 390, "#4a8a3a")):
        p.rect(sx, sy, 3, 4, rgb(c)); p.vline(sx + 1, sy + 3, 5, rgb("#2c5a3e"))
    for sx, sy in ((786, 408), (802, 414)):
        shaded_ell(p, sx + 8, sy - 4, 11, 14, ramp("#0a0a12", "#14141e", "#20202e", "#34364a"))
        p.poly([(sx + 5, sy - 18), (sx + 11, sy - 18), (sx + 9, sy - 14)], rgb("#0a0a12"))
        p.rect(sx - 2, sy + 9, 21, 3, rgb("#0a0810"))


def figure_and_produce(p: Pix) -> None:
    """The hooded seated figure at the right edge, the produce crate beside it, plums spilled on a sack in front."""
    body = rgb("#0c0a14")
    cloak = ramp("#0a0810", "#12101c", "#1c1828", "#292438")
    # contact shadow under everything
    p.dither(826, 478, 134, 22, rgb("#0c0a14"), 0.6)
    # the cloak, pooling to the left over the crate's far side and to the floor
    ell(p, 926, 322, 25, 29, cloak[0])                               # the hood: a dome, head bowed
    pts = [(900, 330), (910, 348), (930, 346), (960, 334), (960, 440), (906, 446), (880, 452), (844, 464), (826, 474), (850, 458), (872, 436), (884, 404), (890, 372), (898, 345)]
    silhouette(p, pts, cloak[0], RIM, "l")
    ell(p, 926, 322, 25, 29, cloak[0])
    for yy in range(294, 352):
        for xx in range(900, 930):
            if p.get(xx, yy)[0] == cloak[0][0] and (xx == 901 + (yy - 330) // 6 * 0 or False):
                pass
    p.vline(902, 312, 24, RIM); p.px(903, 306, RIM); p.px(904, 302, RIM); p.hline(906, 297, 6, RIM_D)
    # folds of the cloak: lighter ridges
    for a, b, c in (((920, 300), (898, 380), 1), ((934, 318), (922, 420), 2), ((948, 340), (944, 438), 1), ((902, 398), (850, 458), 2)):
        p.line(*a, *b, cloak[c]); p.line(a[0] + 1, a[1], b[0] + 1, b[1], cloak[c + 1] if c + 1 < 4 else cloak[c])
    # the hood's face: a deep shadow with a faint pale chin
    ell(p, 919, 326, 11, 14, rgb("#040307"))
    p.hline(912, 338, 8, rgb("#2a2434")); p.px(910, 332, rgb("#3a3248")); p.vline(908, 322, 8, rgb("#1c1828"))
    for yy in range(330, 440):                                       # soft moon-lit sheen on the shoulder and back
        for xx in range(912, 960):
            if (xx * 3 + yy * 5) % 13 == 0 and (xx - 912) < 30 - (yy - 330) // 5:
                p.px(xx, yy, cloak[3])
    # the crate: pale plank sides, slatted gaps, a corner post
    pal = ramp("#3a2e28", "#5a4a3c", "#7a6650", "#9a8264", "#b89e78")
    p.rect(878, 410, 82, 88, rgb("#1a1214"))
    plank_rect(p, 880, 412, 80, 84, pal, vertical=False, board=11, seed=12)
    p.rect(880, 410, 80, 3, pal[4]); p.vline(879, 410, 88, pal[3]); p.vline(959, 410, 88, pal[0])
    for yy in (413, 470):
        p.hline(880, yy, 80, pal[0])
    p.line(884, 428, 930, 490, rgb("#1a1214")); p.line(885, 428, 931, 490, pal[1])      # a split board
    for nx in (884, 954):
        for ny in (418, 440, 462, 486):
            p.px(nx, ny, rgb("#2a2024"))
    # the produce heaped in the crate and on the sack: turnips, beets, plums
    plum = [ramp("#20102a", "#3a1c48", "#5e2e6e", "#84508c", "#a47aac"), ramp("#2a1228", "#4a2040", "#6e3458", "#94587a", "#b4849c")]
    rng = random.Random(9)
    heap = [(sx, sy) for sy in range(380, 412, 5) for sx in range(890, 960, 8)
            if sy > 380 + abs(sx - 935) * 0.55 - 18 or sy > 400]
    for sx, sy in sorted(heap, key=lambda a: a[1]):
        cx, cy = sx + rng.randint(-2, 2), sy + rng.randint(-2, 2)
        shaded_ell(p, cx, cy, 6, 5, rng.choice(plum))
        p.px(cx - 2, cy - 2, rgb("#d8b8e0"))
    # the sack spread on the cobbles with the second heap on it
    sack = [(800, 480), (826, 466), (870, 458), (900, 466), (918, 486), (880, 498), (820, 498)]
    p.poly(sack, rgb("#7a6c58")); p.line(800, 480, 826, 466, rgb("#a8987a")); p.line(826, 466, 870, 458, rgb("#b8a888"))
    p.poly([(860, 462), (900, 466), (918, 486), (880, 498)], rgb("#5a4e40"))
    for k in range(14):
        p.px(806 + k * 8, 481 + (k % 3), rgb("#5a4e40"))
    heap2 = [(sx, sy) for sy in range(446, 492, 6) for sx in range(820, 886, 8) if sy > 446 + abs(sx - 852) * 0.6 - 8 and sy < 494 - abs(sx - 852) * 0.1]
    for sx, sy in sorted(heap2, key=lambda a: a[1]):
        cx, cy = sx + rng.randint(-2, 2), sy + rng.randint(-2, 2)
        shaded_ell(p, cx, cy, 7, 6, rng.choice(plum))
        p.px(cx - 2, cy - 2, rgb("#d8b8e0")); p.px(cx - 3, cy - 1, rgb("#a47aac"))
    pool(p, 860, 470, 70, 40, rgb("#5a3a6a"), 0.12)
    # gutter pipe along the bottom, the same iron as the left
    iron = ramp("#12111a", "#1e1d2a", "#2c2b3c", "#403f56", "#5a5878")
    p.rect(520, 512, 440, 20, iron[1]); p.hline(520, 512, 440, iron[4]); p.hline(520, 514, 440, iron[3]); p.hline(520, 531, 440, iron[0])
    for x in range(550, 960, 80):
        p.rect(x, 510, 6, 24, iron[2]); p.vline(x, 510, 24, iron[4])
