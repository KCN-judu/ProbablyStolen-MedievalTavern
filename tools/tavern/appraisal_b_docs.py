"""Appraisal close-ups, paperwork: plaques, guild crests, hand-lettered headings, wax seals and badge tags.

These pictures are layers of a document the player checks piece by piece, so every variant keeps the same place and
size and differs only where the original series differs (wrong letters, missing line, wrong colour, broken seal ...).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from PIL import Image

from appraisalkit_b import (Canvas, band_shade, BRASS, CLOTH, INK, IRON, PARCH, SHADOW, WAX, bezier, dome_light, disc, leaf, resample,
                            ring, shade, spiral, stroke, text_line, glyph_cells, write_cells)
from palette import MOSS, NAVY, OAK, PALE_WOOD, WINE, LEATHER
from pix import CLEAR, Color, Pix, mix, rgb

# ------------------------------------------------------------------------------------------- plaques


def _plaque(p: Pix, x: int, y: int, w: int, h: int, fill: Sequence[Color], notch: int = 2) -> None:
    """A brass-rimmed plaque with clipped corners and a lightly dithered enamel face."""
    def cut(c: Color) -> None:
        pass
    p.rect(x, y, w, h, BRASS[3])
    for dx, dy in ((0, 0), (w - notch, 0), (0, h - notch), (w - notch, h - notch)):
        p.rect(x + dx, y + dy, notch, notch, CLEAR)
    p.hline(x + notch, y, w - 2 * notch, BRASS[4])
    p.vline(x, y + notch, h - 2 * notch, BRASS[4])
    p.hline(x + notch, y + h - 1, w - 2 * notch, BRASS[2])
    p.vline(x + w - 1, y + notch, h - 2 * notch, BRASS[2])
    p.rect(x + 2, y + 2, w - 4, h - 4, fill[1])
    p.dither(x + 2, y + 3, w - 4, 1, fill[2], 0.4)
    p.hline(x + 2, y + 2, w - 4, fill[2])
    p.hline(x + 2, y + h - 3, w - 4, fill[0])


def _tools(p: Pix, x0: int, y0: int, x1: int, y1: int) -> None:
    """A dagger and a ladle crossed over the letters (the house mark of the cooks' guild)."""
    def outlined(a: tuple[int, int], b: tuple[int, int], core: Color, edge: Color) -> None:
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.line(a[0] + ox, a[1] + oy, b[0] + ox, b[1] + oy, SHADOW)
        p.line(*a, *b, core)
        p.line(a[0] + 1, a[1], b[0] + 1, b[1], edge)
    outlined((x0, y0), (x1, y1), IRON[4], IRON[3])        # dagger
    outlined((x1, y0), (x0, y1), PALE_WOOD[3], PALE_WOOD[2])        # ladle
    p.rect(x0 + 3, y0 + 3, 3, 3, BRASS[3])                          # dagger guard
    p.rect(x1 - 4, y1 - 5, 5, 4, PALE_WOOD[4])                      # ladle bowl


def pen_letter(p: Pix, ch: str, x: int, y: int, w: int, h: int, c: Color) -> None:
    """D, A and U in thick pen strokes (the plaque letters are big enough to deserve real shapes)."""
    if ch == "D":
        p.rect(x, y, 3, h, c)
        p.rect(x, y, w - 3, 3, c); p.rect(x, y + h - 3, w - 3, 3, c)
        p.rect(x + w - 4, y + 1, 2, 2, c); p.rect(x + w - 4, y + h - 3, 2, 2, c)
        p.rect(x + w - 3, y + 3, 3, h - 6, c)
    elif ch == "A":
        mid = w / 2
        for r in range(h):
            half = 1.5 + (mid - 1.5) * r / (h - 1)
            p.rect(round(x + mid - half - 0.5), y + r, 3, 1, c)
            p.rect(round(x + mid + half - 2.5), y + r, 3, 1, c)
        p.rect(x + 3, y + int(h * 0.6), w - 6, 2, c)
        p.rect(x + round(mid) - 2, y, 4, 2, c)
    elif ch == "U":
        p.rect(x, y, 3, h - 3, c); p.rect(x + w - 3, y, 3, h - 3, c)
        p.rect(x + 1, y + h - 3, w - 2, 3, c)
        p.px(x, y + h - 3, CLEAR); p.px(x + w - 1, y + h - 3, CLEAR)


def davre(variant: int) -> Image.Image:
    p = Canvas(265, 104, seed=70 + variant)
    x, y, w, h = 169, 30, 29, 27
    _plaque(p, x, y, w, h, WINE)
    ink = PARCH[4]
    shadow = WINE[0]

    def letter(ch: str, lx: int) -> None:
        pen_letter(p, ch, lx + 1, y + 8, 10, 15, shadow)
        pen_letter(p, ch, lx, y + 7, 10, 15, ink)

    if variant == 4:
        letter("A", 173); letter("U", 185)
        _tools(p, 174, 34, 195, 52)
    elif variant == 5:
        letter("D", 173); letter("A", 185)
        # a little ladle laid in the A only
        p.line(192, 33, 189, 41, PALE_WOOD[3]); p.rect(191, 31, 3, 3, PALE_WOOD[4])
    elif variant == 6:
        letter("D", 173); letter("D", 185)
    return p.finish()


def ribwich(variant: int) -> Image.Image:
    p = Canvas(265, 104, seed=80 + variant)
    _plaque(p, 113, 36, 38, 19, WINE if variant == 1 else MOSS)
    cream = PARCH[4]
    shade_c = PARCH[2]
    if variant in (0, 1):
        # pie: crimped lid, meat in zigzag, base
        p.rect(122, 41, 20, 3, cream); p.rect(121, 42, 22, 1, cream)
        p.hline(122, 43, 20, shade_c)
        for i in range(10):
            p.rect(122 + 2 * i, 46 + (i % 2), 2, 2, cream)
        p.hline(122, 48, 20, shade_c)
        p.rect(122, 50, 20, 2, cream); p.hline(123, 51, 18, shade_c)
    elif variant == 2:
        # taller and narrower: a lattice top, many layers
        p.rect(125, 39, 14, 3, cream); p.hline(126, 41, 12, shade_c)
        for r in range(5):
            for i in range(7):
                if (i + r) % 2 == 0:
                    p.rect(124 + 2 * i, 43 + r, 2, 1, cream)
        p.rect(125, 49, 14, 2, cream); p.hline(126, 50, 12, shade_c)
    return p.finish()


def text_box() -> Image.Image:
    p = Canvas(137, 96, seed=90)
    x, y, w, h = 8, 31, 55, 17
    p.rect(x, y, w, h, LEATHER[1])
    p.dither(x, y, w, h, LEATHER[2], 0.07)
    p.rect(x + 1, y + 1, w - 2, 1, LEATHER[3])
    p.hline(x, y, w, LEATHER[2]); p.vline(x, y, h, LEATHER[2])
    p.hline(x, y + h - 1, w, LEATHER[0]); p.vline(x + w - 1, y, h, LEATHER[0])
    for k in range(x + 3, x + w - 3, 3):               # stitching
        p.px(k, y + 2, PARCH[2]); p.px(k, y + h - 3, PARCH[1])
    for cx in (x + 2, x + w - 3):
        for cy in (y + 5, y + h - 6):
            pass
    return p.finish()


def facility() -> Image.Image:
    """A scrap of blank parchment, torn at the edges, pasted over a printed line."""
    p = Canvas(265, 104, seed=95)
    for rect in ((154, 85, 34, 13), (188, 84, 7, 14), (153, 93, 35, 6)):
        p.rect(*rect, PARCH[3])
    p.rect(154, 85, 34, 1, PARCH[4])
    p.rect(188, 84, 7, 1, PARCH[4])
    p.hline(153, 98, 35, PARCH[2])
    p.hline(188, 97, 7, PARCH[2])
    p.vline(194, 85, 13, PARCH[2])
    p.speckle(153, 84, 42, 15, [PARCH[2], PARCH[4]], 0.03)
    # curled-up corner
    p.rect(190, 85, 2, 1, PARCH[1]); p.rect(191, 86, 1, 1, PARCH[1])
    return p.finish()


# ------------------------------------------------------------------------------------------- compass crest


def compass(p: Pix, cx: int, cy: int, fill_ramp: Sequence[Color], rim: bool = True, center: str = "square",
            arrows: bool = True, ticks: bool = True, wings: int = 3, diamond: bool = False, tall: bool = True) -> None:
    """A brass compass rose on a deep-blue disc, with three flight-feather strokes under it on both sides."""
    ox, oy = cx + 1, cy + 1
    lit, mid, dim = BRASS[4], BRASS[3], BRASS[1]
    if diamond:
        for r in range(0, 15):
            half = 14 - r
            for yy, c in ((oy - r - 1, 0), (oy + r, 0)):
                pass
        p.poly([(ox, oy - 14), (ox + 14, oy), (ox, oy + 14), (ox - 14, oy)], fill_ramp[1])
        p.poly([(ox, oy - 14), (ox - 14, oy), (ox, oy)], fill_ramp[2])
    else:
        r_fill = 10.5 if rim else 12
        band_shade(p, (ox - 14, oy - 14, ox + 14, oy + 14), lambda x, y: math.hypot(x + .5 - ox, y + .5 - oy) <= r_fill,
                   dome_light(ox, oy, 12, 12), fill_ramp)
        if rim:
            ring(p, ox, oy, 13.5, 11.2, BRASS[2])
            ring(p, ox, oy, 13.5, 13, BRASS[1])
            ring(p, ox - 0.8, oy - 0.8, 13.0, 11.6, BRASS[3]) if False else None
            for a in range(200, 300, 3):                  # lit arc on the upper left of the rim
                p.px(round(ox + 12.3 * math.cos(math.radians(a))), round(oy + 12.3 * math.sin(math.radians(a))), BRASS[4])
    top = oy - (14 if tall else 10)
    p.rect(cx, top, 2, (oy - top) * 2, mid)
    p.vline(cx, oy - 9, 18, lit)
    p.rect(ox - (14 if tall else 10) - 1, cy, (14 if tall else 10) * 2 + 2, 2, mid)
    p.hline(ox - 9, cy, 18, lit)
    if ticks:
        for dx in (-3, 4):
            p.vline(cx + dx, oy - 18, 3, mid); p.vline(cx + dx, oy + 15, 3, mid)
        for dy in (-3, 4):
            p.hline(ox - 18, cy + dy, 3, mid); p.hline(ox + 15, cy + dy, 3, mid)
    if center == "square":
        p.frame(cx - 2, cy - 2, 6, 6, lit)
        p.rect(cx, cy, 2, 2, fill_ramp[0])
    else:
        for r, c in ((6, lit), (4, mid), (2, lit)):
            p.poly([(ox, oy - r), (ox + r, oy), (ox, oy + r), (ox - r, oy)], c)
        p.poly([(ox, oy - 1), (ox + 1, oy), (ox, oy + 1), (ox - 1, oy)], fill_ramp[0])
    if arrows:
        for k in range(4):                               # chevrons on the horizontal arm
            p.px(cx - 6 + k // 2 * 0 + (3 - abs(k - 1.5) // 1 if False else 0), cy - 3 + k, mid) if False else None
        for i, d in enumerate((-1, 1)):
            bx = ox + d * 7
            for k in range(4):
                p.px(bx + d * (1 if k in (0, 3) else 0) * -1, cy - 2 + k, lit)
            p.px(bx + d, cy - 1, lit); p.px(bx + d, cy + 2, lit)
        for d in (-1, 1):                                # arrow heads on the vertical arm
            by = oy + d * 7
            for k in range(-2, 4):
                p.px(cx + k - 0, by + d * (abs(k - 0.5) // 1 - 1), mid)
        for dx in (-1, 1):                               # corner kites
            for dy in (-1, 1):
                for k in range(4):
                    p.px(ox + dx * (5 + k) - (dx < 0), oy + dy * (4 + (k % 2)) - (dy < 0), mid)
    # feathers beneath
    lines = {3: [(12, 22, 77, lit), (14, 24, 80, BRASS[2]), (17, 26, 83, lit)], 1: [(14, 24, 80, BRASS[2])]}.get(wings, [])
    for x0, x1, y, c in lines:
        sx = cx - 22 + (x0 - 12) if False else None
        # left side and its mirror about the crest centre
        lx0, lx1 = ox - 23 + (x0 - 12), ox - 23 + (x1 - 12)
        p.hline(lx0, oy + (y - 78), lx1 - lx0, c)
        p.hline(2 * ox - lx1, oy + (y - 78), lx1 - lx0, c)


def logo(variant: int) -> Image.Image:
    p = Canvas(137, 96, seed=100 + variant)
    x, y, w, h = 8, 51, 55, 39
    p.rect(x, y, w, h, rgb("#2b1d2a"))
    for dx, dy in ((0, 0), (w - 2, 0), (0, h - 2), (w - 2, h - 2)):
        p.rect(x + dx, y + dy, 2, 2, CLEAR)
    for dx, dy in ((2, 0), (w - 3, 0), (0, 2), (w - 1, 2), (2, h - 1), (w - 3, h - 1), (0, h - 3), (w - 1, h - 3)):
        pass
    p.hline(x + 2, y, w - 4, rgb("#4a3346")); p.vline(x, y + 2, h - 4, rgb("#4a3346"))
    p.hline(x + 2, y + h - 1, w - 4, rgb("#1a121a")); p.vline(x + w - 1, y + 2, h - 4, rgb("#1a121a"))
    fill = NAVY
    teal = (rgb("#233a3a"), rgb("#3f6f78"), rgb("#5a8e92"), rgb("#7fb1ac"))
    kw: dict = {}
    if variant == 1:
        kw = dict(center="diamond", arrows=False)
    elif variant == 2:
        kw = dict(wings=1)
    elif variant == 3:
        kw = dict(ticks=False, tall=False)
    elif variant == 4:
        fill = teal
    elif variant == 5:
        kw = dict(diamond=True, ticks=False)
    compass(p, 34, 69, fill, **kw)
    return p.finish()


# ------------------------------------------------------------------------------------------- lettering


def letter_sheet(variant: int) -> Image.Image:
    """Three lines of ink lettering: the charter heading. Variants break it the way a forger would."""
    p = Canvas(137, 96, seed=110 + variant)
    ink = rgb("#7a3a68") if variant == 4 else INK
    lines = ["BAKERS", "GUILD", "CHARTER"]
    if variant == 2:
        lines = ["BAKERS", "GUID", "CHARTR"]
    ys = (57, 67, 77)
    for i, t in enumerate(lines):
        if variant == 3 and i == 0:
            continue
        if variant == 6:
            text_line(p, 67, (57, 67, 77)[i], t, ink, w=4, h=6)
        else:
            text_line(p, 67, ys[i], t, ink, bold=(variant == 1), shear=(2 if variant == 5 else 0))
    return p.finish()


def hemingway(text: str, block: bool = False, center: bool = False) -> Image.Image:
    """The sender's name in a tall pen hand: stretched capitals with a larger initial."""
    p = Canvas(83, 141, seed=120)
    ink = rgb("#4a2c36")
    n = len(text)
    x = 10 + (31 - n * 7 // 2 + 0) * 0
    total = n * 7 - 1
    x = 11 + (62 - total) // 2 if (center or block) else 10
    for i, ch in enumerate(text):
        if block:
            rows = resample(glyph_cells(ch), 5, 10)
            write_cells(p, x, 112, rows, ink, bold=True)
        else:
            tall = i == 0
            rows = resample(glyph_cells(ch), 5, 16 if tall else 13)
            write_cells(p, x, 110 if tall else 111, rows, ink, bold=True)
            write_cells(p, x + 1, 110 if tall else 111, rows, ink) if False else None
            # pen nib: a one-pixel wedge at the foot of each letter
            p.px(x - 1 if i else x, 125 if tall else 124, ink)
        x += 7
    return p.finish()


# ------------------------------------------------------------------------------------------- heraldic header


def heraldic(level: int) -> Image.Image:
    """A timber gable with climbing hop bines and a shield. Level 0 is sparse, 1 is the proper header, 2 and 3 add
    more scrolls and ornament (the over-decorated forgeries)."""
    p = Canvas(83, 141, seed=130 + level)
    vine, vine_l, vine_d = MOSS[2], MOSS[3], MOSS[1]
    # gable beams: oak with a lit upper edge and brass pegs
    for t in range(0, 42):
        y = 22 + t
        for xc in (41 - t, 41 + t):
            p.rect(xc - 1, y, 3, 2, PALE_WOOD[3])
            p.px(xc - 1 if xc <= 41 else xc + 1, y, PALE_WOOD[2])
            p.px(xc, y, PALE_WOOD[4])
    for t in (12, 21, 30):
        for xc in (41 - t, 41 + t):
            p.px(xc, 22 + t, BRASS[4])
    p.rect(39, 22, 5, 3, PALE_WOOD[4])

    def bine(side: int) -> None:
        def X(x: float) -> float:
            return x if side < 0 else 82 - x
        stem = [(X(31), 118), (X(21), 112), (X(13), 100), (X(13), 88), (X(19), 78), (X(21), 66), (X(18), 58)]
        if level == 0:
            stem = [(X(31), 118), (X(22), 108), (X(16), 96), (X(17), 82), (X(20), 70), (X(18), 58)]
        path = bezier(stem, 14)
        stroke(p, path, vine, 3)
        stroke(p, [(x, y) for x, y in path], vine_l, 1)
        # curl at the foot
        curl = spiral(X(13), 112, 9, 1.4 if level else 0.6, math.pi * 0.2 if side < 0 else math.pi * 0.8, -1 if side < 0 else 1)
        cp = bezier(curl[::2], 8)
        stroke(p, [(x, y) for x, y in cp], vine, 2 if level == 0 else 3)
        if level >= 2:
            curl2 = spiral(X(6), 98, 6, 1.2, math.pi, 1 if side < 0 else -1)
            stroke(p, bezier(curl2[::2], 8), vine, 1)
            curl3 = spiral(X(27), 100, 6, 1.1, 0, -1 if side < 0 else 1)
            stroke(p, bezier(curl3[::2], 8), vine, 1)
        if level >= 3:
            for (sx, sy, r, st) in ((X(34), 114, 5, 3.3), (X(8), 76, 5, 0.5), (X(28), 80, 5, 1.0), (X(3), 112, 5, 2.0)):
                cu = spiral(sx, sy, r, 1.2, st, 1 if side < 0 else -1)
                stroke(p, bezier(cu[::2], 8), vine, 1)
        # leaves along the stem (more at higher levels)
        spots = [(X(19), 78, -side * -1, -1), (X(21), 66, 1, -1), (X(13), 94, -1, -1)]
        if level >= 1:
            spots += [(X(17), 58, 0, -1), (X(13), 104, -1, 0)]
        if level >= 2:
            spots += [(X(22), 88, 1, -1), (X(30), 112, 1, 0)]
        for sx, sy, dx, dy in spots:
            ddx = (dx if dx else 0)
            leaf(p, int(sx), int(sy), ddx * 5 * (1 if side < 0 else -1) if dx else 0, dy * 5, 9, vine_l, vine)
        # hop cones hang from the high stems
        for hx, hy in ((X(23), 70), (X(11), 90)) if level >= 1 else ((X(22), 72),):
            p.rect(int(hx), int(hy), 3, 4, MOSS[3]); p.rect(int(hx), int(hy) + 4, 2, 2, MOSS[2])
            p.px(int(hx), int(hy), MOSS[3]); p.px(int(hx) + 1, int(hy) + 1, rgb("#8aa860"))
    bine(-1)
    bine(1)

    # the shield in the middle
    cx, cy = 41, 92
    shield = [(cx - 9, cy - 13), (cx + 9, cy - 13), (cx + 9, cy + 2), (cx, cy + 14), (cx - 9, cy + 2)]
    p.poly([(x - 1 if x < cx else x + 1, y - 1) for x, y in shield], BRASS[2])
    p.poly(shield, WINE[2])
    p.poly([(cx - 9, cy - 13), (cx, cy - 13), (cx, cy + 12), (cx - 9, cy + 2)], WINE[3])
    p.line(cx - 9, cy - 13, cx + 9, cy - 13, BRASS[4])
    # cross keys / cross
    p.rect(cx - 1, cy - 10, 3, 20, BRASS[3]); p.rect(cx - 6, cy - 4, 13, 3, BRASS[3])
    p.vline(cx - 1, cy - 10, 20, BRASS[4]); p.hline(cx - 6, cy - 4, 13, BRASS[4])
    if level >= 1:
        for dx, dy in ((-5, -9), (5, -9)):
            p.rect(cx + dx - 1, cy + dy, 3, 3, BRASS[3]); p.px(cx + dx - 1, cy + dy, BRASS[4])
        p.rect(cx - 2, cy + 3, 5, 3, BRASS[2])
    if level >= 2:
        for dx in (-6, 0, 6):                               # crown over the shield
            p.rect(cx + dx - 1, cy - 19, 3, 4, BRASS[3])
        p.hline(cx - 7, cy - 15, 15, BRASS[2])
        ring(p, cx, cy - 1, 17, 16, BRASS[1]) if False else None
    if level >= 3:
        for ang in range(0, 360, 45):
            p.px(round(cx + 15 * math.cos(math.radians(ang))), round(cy - 1 + 15 * math.sin(math.radians(ang))), BRASS[4])
        p.rect(cx - 4, cy + 8, 9, 2, BRASS[4])
    # small leaf ornaments in the bottom corners
    for ox in (2, 73):
        for k in range(4):
            p.rect(ox + 2 - abs(k - 1.5) // 1, 119 + k, 2 + 2 * (k % 3 == 1), 1, rgb("#c58a4a"))
        p.rect(ox + 3, 118, 1, 7, rgb("#9a6234"))
    return p.finish()


# ------------------------------------------------------------------------------------------- seals


def _oval(cx: float, cy: float, a: float, b: float) -> Callable[[int, int], bool]:
    return lambda x, y: ((x + 0.5 - cx) / a) ** 2 + ((y + 0.5 - cy) / b) ** 2 <= 1.0


def wax_seal(state: str) -> Image.Image:
    """The wax seal on the folded letter: whole with a thread across it, or cracked in two with the thread gone."""
    p = Canvas(83, 141, seed=140)
    cx, cy, a, b = 41.5, 29.5, 10.6, 12.6
    inside = _oval(cx, cy, a, b)
    box = (30, 16, 53, 43)
    shade(p, box, inside, dome_light(cx, cy, a, b), WAX)
    # outline and raised rim
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if inside(x, y):
                if not (inside(x + 1, y) and inside(x - 1, y) and inside(x, y + 1) and inside(x, y - 1)):
                    p.px(x, y, WAX[0])
    inner = _oval(cx, cy, a - 2.2, b - 2.2)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if inside(x, y) and inner(x, y) is False and _oval(cx, cy, a - 3.4, b - 3.4)(x, y):
                p.px(x, y, WAX[1] if (x < cx and y < cy) else WAX[4] if (x > cx and y > cy) else WAX[2])
    # the crest: an eight-pointed star raised from the wax (lit on its upper left)
    def star(dx: int, dy: int, c: Color) -> None:
        sx, sy = 41 + dx, 29 + dy
        p.rect(sx - 1, sy - 6, 3, 13, c); p.rect(sx - 6, sy - 1, 13, 3, c)
        for k in range(1, 5):
            for ex, ey in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                p.rect(sx + ex * k - (1 if ex < 0 else 0), sy + ey * k - (1 if ey < 0 else 0), 2, 2, c)
        disc(p, sx + 0.5, sy + 0.5, 3, c)
    star(1, 1, WAX[4])
    star(0, 0, WAX[1])
    disc(p, 41.5, 29.5, 2, WAX[0])
    if state == "closed":
        p.hline(31, 31, 21, mix(CLOTH[2], WAX[2], 0.15))
        p.hline(31, 32, 21, mix(CLOTH[1], WAX[1], 0.3)) if False else None
    else:
        rng = p.rng
        # break the oval along the thread line: ragged teeth on both lips, a gap between
        for x in range(30, 53):
            top_cut = 30 + rng.randint(0, 1)
            bot_cut = 33 - rng.randint(0, 1)
            for y in range(top_cut + 1, bot_cut):
                p.px(x, y, CLEAR)
            if p.get(x, top_cut)[3]:
                p.px(x, top_cut, WAX[0])
            if p.get(x, bot_cut)[3]:
                p.px(x, bot_cut, WAX[0])
        for x in range(30, 53):
            for y in (31, 32):
                p.px(x, y, CLEAR)
            if p.get(x, 30)[3]:
                p.px(x, 30, WAX[0])
            if p.get(x, 33)[3]:
                p.px(x, 33, WAX[0])
    return p.finish()


def seal_gold() -> Image.Image:
    """A small brass shield stud: the 'golden' stamp."""
    p = Canvas(137, 96, seed=150)
    x, y = 117, 57
    shape = [(0, 0), (8, 0), (8, 7), (6, 10), (4, 11), (2, 10), (0, 7)]
    def inside(px: int, py: int) -> bool:
        rx, ry = px - x, py - y
        if not (0 <= rx <= 8 and 0 <= ry <= 11):
            return False
        half = 4.6 if ry < 7 else max(0.0, 4.6 - (ry - 6) * 1.0)
        return abs(rx - 4) <= half
    shade(p, (x, y, x + 9, y + 12), inside, lambda px, py: 0.85 - (py - y) / 14 - (px - x) / 22, BRASS)
    for yy in range(y, y + 12):
        for xx in range(x, x + 9):
            if inside(xx, yy) and not (inside(xx - 1, yy) and inside(xx + 1, yy) and inside(xx, yy + 1) and inside(xx, yy - 1)):
                p.px(xx, yy, BRASS[1] if (xx > x + 3 or yy > y + 6) else BRASS[4])
    p.vline(x + 4, y + 2, 7, BRASS[4]); p.hline(x + 2, y + 4, 5, BRASS[4])
    p.px(x + 5, y + 5, BRASS[1]); p.px(x + 4, y + 9, BRASS[1])
    return p.finish()


def seal_holo() -> Image.Image:
    """An enamelled oval token: sea-green glass with diagonal streaks of verdigris and amber."""
    p = Canvas(137, 96, seed=151)
    cx, cy, a, b = 122.0, 70.0, 8.0, 10.0
    inside = _oval(cx, cy, a, b)
    teal = (rgb("#2c5a62"), rgb("#4c8a90"), rgb("#7fb7b4"), rgb("#a8d2c6"))
    def tone(x: int, y: int) -> float:
        return 0.75 - 0.5 * (((x - 114) + (y - 60)) / 26.0)
    band_shade(p, (113, 59, 131, 81), inside, tone, teal)
    for y in range(60, 81):
        for x in range(114, 131):
            if not inside(x, y):
                continue
            d = (x - 114) - (y - 60) * 0.9 + 6
            k = int(d) % 7
            if (x - 122) + (y - 70) > 1:
                if k == 0:
                    p.px(x, y, rgb("#7fa84a"))
                elif k == 1:
                    p.px(x, y, rgb("#b9d070"))
                elif k == 3:
                    p.px(x, y, rgb("#d08a4a"))
            if not (inside(x + 1, y) and inside(x - 1, y) and inside(x, y + 1) and inside(x, y - 1)):
                p.px(x, y, BRASS[4] if (x + y) < 192 else BRASS[2])
    p.px(118, 64, rgb("#e8f2e0")); p.px(119, 64, rgb("#e8f2e0")); p.px(118, 65, rgb("#e8f2e0"))
    return p.finish()


# ------------------------------------------------------------------------------------------- badge tags


def _tag(p: Pix, frame: Sequence[Color] | Color) -> None:
    """A leather-and-iron badge with a coloured wire frame and a buckle strap down the right side."""
    x0, y0, x1, y1 = 236, 59, 287, 95
    bg = rgb("#2a2030")
    p.rect(x0, y0, x1 - x0, y1 - y0, bg)
    p.frame(x0, y0, x1 - x0, y1 - y0, rgb("#1a1420"))
    p.dither(x0 + 1, y0 + 1, x1 - x0 - 2, 6, rgb("#322838"), 0.25)
    fx0, fy0, fx1, fy1 = 238, 61, 285, 93
    pieces = frame if isinstance(frame, (list, tuple)) and isinstance(frame[0], tuple) else None
    for i, x in enumerate(range(fx0, fx1)):
        c = frame[(i // 5) % len(frame)] if pieces else frame
        p.px(x, fy0, c); p.px(x, fy1 - 1, c)
    for i, y in enumerate(range(fy0, fy1)):
        c = frame[(i // 5 + 2) % len(frame)] if pieces else frame
        p.px(fx0, y, c); p.px(fx1 - 1, y, c)
    # strap with two iron bars and caps
    p.rect(282, 57, 9, 40, rgb("#1c1722"))
    p.vline(284, 61, 32, IRON[2]); p.vline(285, 61, 32, IRON[1])
    p.vline(288, 61, 32, IRON[2]); p.vline(289, 61, 32, IRON[1])
    p.rect(282, 57, 9, 3, IRON[2]); p.hline(282, 57, 9, IRON[3])
    p.rect(283, 94, 8, 3, IRON[2]); p.hline(283, 96, 8, IRON[1])
    col = (frame[0] if pieces else frame)
    p.hline(283, 93, 8, col)


def tag(kind: str) -> Image.Image:
    p = Canvas(319, 124, seed=160 + len(kind))
    cx, cy = 258, 77
    if kind == "ignition":
        _tag(p, rgb("#8a5a9a"))
        shade(p, (cx - 17, cy - 17, cx + 17, cy + 17), lambda x, y: math.hypot(x - cx, y - cy) <= 15,
              dome_light(cx, cy, 15, 15), (rgb("#1c2a40"), rgb("#2c4262"), rgb("#44648a"), rgb("#6a8caa")))
        for k in range(0, 360, 4):                       # a ringed orbit tilted across the disc
            t = math.radians(k)
            x, y = cx + 19 * math.cos(t) * 0.95, cy + 7 * math.sin(t) + 9 * math.cos(t) * -0.6
            if 241 < x < 281:
                p.px(round(x), round(y), rgb("#8a5a9a") if math.sin(t) < 0 else rgb("#b78ac0"))
        for sx, sy in ((cx - 8, cy - 9), (cx + 6, cy - 5), (cx - 3, cy + 11)):
            p.px(sx, sy, rgb("#b8dcd8")); p.px(sx + 1, sy, rgb("#7fb1ac"))
        text_line(p, 241, 76, "ALCHEMY", PARCH[4]) if False else None
        for ox, oy in ((1, 1),):
            text_line(p, 241 + ox, 76 + oy, "ALCHEMY", SHADOW)
        text_line(p, 241, 76, "ALCHEMY", PARCH[4])
        for ox, oy in ((1, 1),):
            text_line(p, 254 + ox, 85 + oy, "GUILD", SHADOW)
        text_line(p, 254, 85, "GUILD", PARCH[4])
    elif kind == "ll":
        _tag(p, [rgb("#b2808a"), rgb("#8ab8b0"), rgb("#8aa850"), rgb("#d6c080"), rgb("#9a6aa0"), rgb("#c9b0a0")])
    elif kind == "republic":
        _tag(p, rgb("#3f6f78"))
        compass(p, cx - 1, cy - 1, (rgb("#10192a"), rgb("#1d3049"), rgb("#2f4c70"), rgb("#4a6e98")), wings=0, ticks=True)
    else:
        _tag(p, rgb("#b0653a"))
        ox, oy = cx + 0.5, cy + 0.5
        shade(p, (cx - 18, cy - 18, cx + 18, cy + 18), lambda x, y: math.hypot(x + .5 - ox, y + .5 - oy) <= 15.5,
              dome_light(ox, oy, 15, 15), WINE)
        ring(p, ox, oy, 15.5, 14, BRASS[2])
        for k in range(0, 360, 20):                      # beaded edge
            t = math.radians(k)
            p.px(round(ox + 12.2 * math.cos(t)), round(oy + 12.2 * math.sin(t)), BRASS[4])
        ring(p, ox, oy, 10.5, 9.5, BRASS[3])
        # a castle tower in the middle
        p.rect(cx - 5, cy - 3, 11, 10, BRASS[3]); p.vline(cx - 5, cy - 3, 10, BRASS[4])
        for bx in (cx - 5, cx - 1, cx + 3):
            p.rect(bx, cy - 6, 3, 3, BRASS[3]); p.px(bx, cy - 6, BRASS[4])
        p.rect(cx - 1, cy + 2, 3, 5, WINE[0]); p.px(cx - 1, cy + 1, WINE[0]); p.px(cx + 1, cy + 1, WINE[0])
        p.rect(cx - 4, cy - 1, 2, 2, WINE[1]); p.rect(cx + 3, cy - 1, 2, 2, WINE[1])
    return p.finish()


# ------------------------------------------------------------------------------------------- registry

NAME = "THORNBURY"


def _hem(variant: str) -> Callable[[], Image.Image]:
    return {
        "letter-correct": lambda: hemingway(NAME),
        "letter-font": lambda: hemingway(NAME, block=True),
        "letter-incorrect1": lambda: hemingway("THORNBURI"),
        "letter-incorrect2": lambda: hemingway("TAORNBURY"),
        "letter-incorrect3": lambda: hemingway("THORBURY", center=True),
        "letter-incorrect4": lambda: hemingway("THORMBURY"),
        "letter-incorrect5": lambda: hemingway("THOPNBURY"),
    }[variant]


DRAWINGS: dict[str, Callable[[], Image.Image]] = {
    "davre_logo_incorrect4.265x104.png": lambda: davre(4),
    "davre_logo_incorrect5.265x104.png": lambda: davre(5),
    "davre_logo_incorrect6.265x104.png": lambda: davre(6),
    "davre_logo_incorrect7.265x104.png": lambda: davre(7),
    "ribwich_logo.265x104.png": lambda: ribwich(0),
    "ribwich_logo_incorrect1.265x104.png": lambda: ribwich(1),
    "ribwich_logo_incorrect2.265x104.png": lambda: ribwich(2),
    "ribwich_logo_incorrect3.265x104.png": lambda: ribwich(3),
    "text box.137x96.png": text_box,
    "facility.265x104.png": facility,
    "logo correct.137x96.png": lambda: logo(0),
    "logo incorrect.137x96.png": lambda: logo(1),
    "logo incorrect2.137x96.png": lambda: logo(2),
    "logo incorrect3.137x96.png": lambda: logo(3),
    "logo incorrect4.137x96.png": lambda: logo(4),
    "logo incorrect5.137x96.png": lambda: logo(5),
    "letter correct.137x96.png": lambda: letter_sheet(0),
    "letter incorrect.137x96.png": lambda: letter_sheet(1),
    "letter incorrect2.137x96.png": lambda: letter_sheet(2),
    "letter incorrect3.137x96.png": lambda: letter_sheet(3),
    "letter incorrect4.137x96.png": lambda: letter_sheet(4),
    "letter incorrect5.137x96.png": lambda: letter_sheet(5),
    "letter incorrect6.137x96.png": lambda: letter_sheet(6),
    **{f"{k}.83x141.png": _hem(k) for k in ("letter-correct", "letter-font", "letter-incorrect1", "letter-incorrect2",
                                            "letter-incorrect3", "letter-incorrect4", "letter-incorrect5")},
    "logo-simple.83x141.png": lambda: heraldic(0),
    "logo-correct.83x141.png": lambda: heraldic(1),
    "logo-complexe1.83x141.png": lambda: heraldic(2),
    "logo-complexe2.83x141.png": lambda: heraldic(3),
    "seal-correct.83x141.png": lambda: wax_seal("closed"),
    "seal-open.83x141.png": lambda: wax_seal("open"),
    "seal golden.137x96.png": seal_gold,
    "seal holo.137x96.png": seal_holo,
    "seal_ignition.319x124.png": lambda: tag("ignition"),
    "seal_ll.319x124.png": lambda: tag("ll"),
    "seal_republic.319x124.png": lambda: tag("republic"),
    "seal_zhong.319x124.png": lambda: tag("zhong"),
}
