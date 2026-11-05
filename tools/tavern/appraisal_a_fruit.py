"""Appraisal close-ups: the grape bunch in six conditions, plus the loaf's bottom half, the pipeweed packet, the cap and the tally tag.

The grapes keep the series' differences in the same places: normal is plump and plum-dark; under1 is amber (unripe);
under2 is rosy (not yet dark); over is shrivelled and long with a dried leaf; mold has grey fur on the lower middle
berries; small is a bunch of smaller berries.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from PIL import Image

import font
from appraisalkit_a import (
    BLACKENED, BRASS, GOLD, STEEL, Mask, capsule, capsule_mask, distance_inside, dome, ellipse_mask, plate_rect, poly_mask,
    solid,
)
from palette import LEATHER, MOSS, PARCHMENT, SHADOW, SOOT, WINE
from pix import Color, Pix, Ramp

PLUM: Ramp = ((26, 12, 36), (52, 24, 68), (86, 40, 104), (122, 66, 134), (168, 112, 170), (222, 190, 224))
AMBER: Ramp = ((70, 34, 22), (126, 64, 28), (186, 106, 40), (228, 156, 66), (248, 206, 124), (255, 240, 200))
ROSY: Ramp = ((58, 16, 34), (108, 28, 56), (158, 48, 80), (200, 82, 108), (232, 146, 158), (255, 220, 214))
RAISIN: Ramp = ((30, 14, 28), (56, 26, 48), (84, 42, 62), (110, 62, 76), (140, 92, 98), (176, 132, 130))
FUR: Ramp = ((60, 56, 50), (96, 94, 82), (132, 134, 114), (172, 178, 150), (206, 212, 186))
LEAF: Ramp = ((18, 36, 28), (34, 66, 40), (56, 100, 56), (88, 138, 76), (132, 176, 104))
DRYLEAF: Ramp = ((50, 42, 34), (84, 72, 56), (120, 108, 84), (158, 144, 112))
TWIG: Ramp = ((36, 20, 20), (66, 38, 32), (98, 62, 46), (130, 90, 62))

W, H = 239, 233


def berry_rows(small: bool, k: float = 0.97) -> list[tuple[int, int]]:
    rows = ((38, (104, 132)), (60, (88, 116, 144)), (84, (60, 88, 116, 144, 172)), (108, (44, 72, 100, 128, 156, 182)),
            (132, (58, 86, 114, 142, 170)), (156, (72, 100, 128, 156)), (180, (86, 114, 142)), (202, (100, 128)))
    pts: list[tuple[int, int]] = []
    for y, xs in rows:
        pts += [(x, round(y * k)) for x in xs]
    if small:
        # more, smaller berries on the same frame
        pts = []
        ry = 30
        for y in range(30, 204, 17):
            n = max(2, min(9, 2 + (y - 30) // 17 if y < 120 else 9 - (y - 120) // 17 * 1))
            width = n * 18
            x0 = 120 - width // 2 + 9
            pts += [(x0 + i * 18 + (7 if (y // 17) % 2 else 0) - 4, round(y * k)) for i in range(n)]
    return pts


def grapes(kind: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    p = Pix(W, H, seed=seed)
    ramp = {"normal": PLUM, "under1": AMBER, "under2": ROSY, "over": RAISIN, "mold": PLUM, "small": PLUM}[kind]
    small = kind == "small"
    over = kind == "over"
    r0 = 10.0 if small else 14.0
    pts = berry_rows(small, 0.945 if over else 0.97)

    # stem and a dark mass behind, so gaps between berries read as shadow and not as holes
    stem = [(206, 12), (186, 22), (166, 34), (146, 44), (126, 48)]
    for a, b in zip(stem, stem[1:]):
        capsule(p, a, b, 4.0, 3.4, TWIG, SOOT[0], relief=1.0, dither=False)
    for dx, dy in ((196, 6), (212, 14)):
        pass
    back = {(x, y) for y in range(0, H) for x in range(0, W)
            if any((x - px) ** 2 + (y - py) ** 2 < (r0 * 0.9) ** 2 for px, py in pts)}
    for (x, y) in back:
        p.px(x, y, ramp[0])
    # a leaf at the right: five lobes round a mid-rib
    if over:
        leaf = [(188, 100), (204, 96), (214, 84), (222, 100), (232, 106), (216, 114), (226, 126), (208, 124), (196, 134), (192, 118)]
        leaf = [(x - 6, y) for x, y in leaf]
        lm = poly_mask(leaf)
        ld = distance_inside(lm)
        solid(p, lm, lambda x, y: min(ld.get((x, y), 0), 3) * 0.8 + ((x * 7 + y * 3) % 5) * 0.12, DRYLEAF, SOOT[1], dither=True)
        for k in range(10):
            p.px(188 + k * 3, 114 + (k % 3) - k // 2, DRYLEAF[0])
    else:
        leaf = [(184, 108), (196, 92), (206, 80), (214, 94), (228, 92), (222, 108), (232, 118), (216, 122), (212, 140), (198, 128), (186, 126)]
        leaf = [(x - 6, y) for x, y in leaf]
        lm = poly_mask(leaf)
        ld = distance_inside(lm)
        solid(p, lm, lambda x, y: min(ld.get((x, y), 0), 3) * 1.0 + 0.8 * math.sin((x + y) * 0.4), LEAF, SOOT[0], dither=True)
        for k in range(18):
            p.px(182 + k * 2, 118 - k // 2 + (1 if k % 2 else 0), LEAF[0])
        for k in range(6):
            p.px(198 + k, 100 + k, LEAF[0])
            p.px(198 + k, 120 - k, LEAF[0])
    # twig to the leaf
    capsule(p, (176, 112), (150, 90), 1.6, 1.6, TWIG, SOOT[0], dither=False)

    moldy = {i for i, (x, y) in enumerate(pts) if 110 < y < 175 and 60 < x < 140} if kind == "mold" else set()
    order = sorted(range(len(pts)), key=lambda i: (pts[i][1], rng.random()))
    for i in order:
        x, y = pts[i]
        x += rng.randint(-2, 2)
        y += rng.randint(-2, 2)
        r = r0 + rng.uniform(-1.4, 1.6)
        if kind == "under1":
            r += rng.choice((-2.5, -1, 0, 1))
        rx, ry = (r * 0.86, r * 1.03) if over else (r, r)
        bm = ellipse_mask(x, y, rx, ry)
        use = FUR if i in moldy else ramp
        if i in moldy:
            use = RAISIN
        solid(p, bm, dome(x, y, rx, ry, r * 1.1), use, ramp[0] if i not in moldy else SOOT[0], relief=0.9, gain=1.2, bias=-0.34, dither=True)
        # glossy catch-light, calyx dot
        if not over and i not in moldy:
            hx, hy = round(x - r * 0.38), round(y - r * 0.45)
            p.rect(hx, hy, 3, 2, ramp[5])
            p.px(hx - 1, hy + 1, ramp[4])
            p.px(hx + 3, hy + 1, ramp[4])
            p.px(round(x + r * 0.2), round(y + r * 0.62), ramp[1])
        p.px(x, round(y - ry * 0.85), MOSS[1])
        p.px(x + 1, round(y - ry * 0.85) - 1, TWIG[2])
        if over:
            # wrinkles on a drying skin, long across the berry
            for k in range(-int(ry * 0.7), int(ry * 0.8), 3):
                for j in range(-int(rx * 0.6), int(rx * 0.6) + 1):
                    if (j * 3 + k) % 4:
                        p.px(x + j, y + k + (j * j) // 5, ramp[0])
            p.px(x - 3, y - 6, ramp[5])
            p.px(x - 2, y - 6, ramp[4])
        if i in moldy:
            for _ in range(int(r * r * 0.7)):
                a = rng.random() * math.tau
                d = (rng.random() ** 0.6) * r * 1.05
                xx, yy = round(x + math.cos(a) * d), round(y + math.sin(a) * d)
                if (xx, yy) in bm:
                    p.px(xx, yy, rng.choice((FUR[2], FUR[3], FUR[4], FUR[3])))
            for _ in range(10):                       # spores drifting off
                a = rng.random() * math.tau
                d = r + rng.random() * 4
                p.px(round(x + math.cos(a) * d), round(y + math.sin(a) * d), FUR[3])
    return p.im


# ------------------------------------------------------------------ loaf bottom

def bottom_bun() -> Image.Image:
    p = Pix(265, 104, seed=3)
    ox, oy = 32, 77
    w, h = 202, 25
    mask: Mask = set()
    for y in range(h):
        for x in range(w):
            t = (x - (w - 1) / 2) / ((w - 1) / 2)
            bottom = 5 + (h - 6) * math.sqrt(max(0.0, 1 - t * t) ** 1.0) ** 0.9
            top = 1.0 + 3.0 * (t * t)
            if top <= y <= bottom:
                mask.add((x + ox, y + oy))
    cx = ox + w / 2

    def hf(x: int, y: int) -> float:
        t = (x - cx) / (w / 2)
        return max(0.0, 1 - t * t) ** 0.5 * 9 + (y - oy) * 0.28
    solid(p, mask, hf, ((60, 30, 22), (110, 58, 30), (160, 96, 44), (200, 140, 66), (228, 182, 102)), SOOT[0], relief=1.2, gain=1.2, bias=-0.35, dither=True)
    # the cut face on top: pale crumb with air holes, over the crust
    rng = p.rng
    for (x, y) in mask:
        t = (x - cx) / (w / 2)
        if y - oy <= 4 + 3 * t * t and abs(t) < 0.985:
            p.px(x, y, (232, 204, 148) if (x // 3 + y) % 7 else (214, 182, 124))
    for _ in range(46):
        x, y = ox + rng.randint(8, w - 9), oy + rng.randint(1, 3)
        if (x, y) in mask:
            p.px(x, y, (178, 140, 90))
    # seeds scattered on the crust
    for _ in range(60):
        x, y = ox + rng.randint(10, w - 10), oy + rng.randint(8, h - 5)
        if (x, y) in mask and (x + 1, y + 1) in mask:
            p.px(x, y, (236, 214, 160))
            p.px(x + 1, y, (170, 118, 62))
    # a smear of sauce at the right end
    for k in range(18):
        x = ox + w - 26 + k + rng.randint(0, 1)
        y = oy + 2 + (k % 3 == 0) + rng.randint(0, 1)
        if (x, y) in mask:
            p.px(x, y, WINE[3])
            if (x, y + 1) in mask:
                p.px(x, y + 1, WINE[1])
    for k in range(3):
        if (ox + w - 14 + k, oy + 5) in mask:
            p.px(ox + w - 14 + k, oy + 5, WINE[3])
            p.px(ox + w - 14 + k, oy + 6, WINE[1])
    return p.im


# ------------------------------------------------------------------ pipeweed packet

def packet() -> Image.Image:
    p = Pix(83, 141, seed=7)
    red = WINE
    # paper: fibre speckle in two tones
    box = plate_rect(p, 0, 0, 83, 141, red, SOOT[0], bevel=2, corner=3, relief=0.5, gain=1.1, bias=0.1, dither=False)
    p.rect(2, 2, 79, 54, red[2])
    p.rect(2, 2, 79, 54, red[2])
    p.hline(2, 2, 79, red[3])
    p.hline(2, 55, 79, red[0])
    # lower body: linen with a V flap in the red above
    for y in range(56, 139):
        p.hline(2, y, 79, PARCHMENT[3] if y < 130 else PARCHMENT[2])
    p.rect(2, 56, 79, 1, red[0])
    p.rect(2, 128, 79, 11, red[2])
    p.hline(2, 128, 79, red[4])
    p.hline(2, 129, 79, red[1])
    # the red flap's V: cream triangle apex up
    for y in range(58, 98):
        half = (y - 58) * 2
        for x in range(41 - half, 42 + half):
            if 2 <= x < 81:
                p.px(x, y, PARCHMENT[3])
    for y in range(58, 98):
        half = (y - 58) * 2
        for x in (41 - half, 41 + half):
            if 2 <= x < 81:
                p.px(x, y, red[1])
    for y in range(58, 98):
        half = (y - 58) * 2
        for x in list(range(2, 41 - half)) + list(range(42 + half, 81)):
            p.px(x, y, red[2])
    for y in range(58, 98):
        half = (y - 58) * 2
        for x in (41 - half, 41 + half):
            if 2 <= x < 81:
                p.px(x, y, red[0])
                p.px(x + 1 if x < 41 else x - 1, y, red[3])
    p.rect(2, 57, 79, 1, red[0])
    # label cartouche and its lettering
    p.rect(14, 12, 55, 13, PARCHMENT[3])
    p.frame(14, 12, 55, 13, red[0])
    p.frame(15, 13, 53, 11, red[3])
    font.write(p, 21, 15, "PIPEWEED", red[0])
    font.write(p, 9, 132, "20 PIPEFULS", PARCHMENT[4])
    # a wax seal with a crest at the heart of the cream
    from appraisalkit_a import gear
    seal = ellipse_mask(41, 106, 13, 13)
    solid(p, seal, dome(41, 106, 14, 14, 9), WINE, SOOT[0], relief=1.0, dither=False)
    p.ellipse(31, 96, 20, 20, red[3]) if False else None
    for dx, dy in ((0, -5), (0, -4), (-1, -3), (1, -3), (-2, -1), (2, -1), (-3, 1), (3, 1), (-2, 3), (2, 3), (-4, 3), (4, 3), (0, 1), (0, 2), (0, 3), (0, 4)):
        p.px(41 + dx, 106 + dy, WINE[0])
    p.px(40, 102, WINE[4])
    p.px(39, 103, WINE[4])
    # a ragged tear along the edge of the fold and tobacco dust specks
    rng = p.rng
    for _ in range(50):
        p.px(rng.randint(3, 79), rng.randint(60, 126), PARCHMENT[2])
    return p.im


def cap() -> Image.Image:
    p = Pix(231, 39, seed=11)
    ox, oy = 20, 3
    pts = [(ox + 1, oy + 4), (ox + 16, oy + 1), (ox + 18, oy + 4), (ox + 15, oy + 12), (ox + 14, oy + 24), (ox + 17, oy + 30),
           (ox + 8, oy + 30), (ox + 1, oy + 26), (ox, oy + 12)]
    m = poly_mask(pts)
    d = distance_inside(m)
    cxx = ox + 4
    solid(p, m, lambda x, y: min(d.get((x, y), 0), 3) * 1.0 + max(0.0, 1 - ((x - cxx) / 14.0) ** 2) ** 0.5 * 5, STEEL, (24, 22, 32), relief=1.2, gain=1.3, bias=-0.2, dither=False)
    for y in range(oy + 6, oy + 28, 5):
        p.hline(ox + 2, y, 10, STEEL[1])
    p.rect(ox + 4, oy + 8, 3, 3, BRASS[3])
    p.px(ox + 4, oy + 8, BRASS[4])
    p.rect(ox + 4, oy + 20, 3, 3, BRASS[3])
    p.px(ox + 4, oy + 20, BRASS[4])
    return p.im


def tally_tag() -> Image.Image:
    p = Pix(265, 104, seed=13)
    ox, oy = 48, 82
    w, h = 40, 15
    m = poly_mask([(ox, oy + 1), (ox + 4, oy), (ox + w - 1, oy + 2), (ox + w - 1, oy + h - 1), (ox + 6, oy + h - 1), (ox, oy + h - 3)])
    d = distance_inside(m)
    solid(p, m, lambda x, y: min(d.get((x, y), 0), 2) * 1.0, PARCHMENT, (70, 52, 40), relief=1.0, dither=False)
    # tally strokes in ink, thick and thin, like a counting notch row
    xs = [(3, 3), (8, 2), (12, 3), (17, 2), (21, 1), (24, 3), (29, 2), (33, 1), (36, 2)]
    for x, wd in xs:
        for y in range(oy + 4, oy + h - 4):
            for k in range(wd):
                p.px(ox + x + k, y, (40, 26, 34))
    for x in range(4, 36):
        p.px(ox + x, oy + h - 3, (150, 124, 84)) if x % 2 else None
    p.rect(ox + 1, oy + 4, 2, 2, (70, 52, 40))
    return p.im


ASSETS: dict[str, Callable[[], Image.Image]] = {
    "bottom_bun.265x104.png": bottom_bun,
    "box_ok.83x141.png": packet,
    "cap.231x39.png": cap,
    "bar_code.265x104.png": tally_tag,
}
for _i, (_n, _k) in enumerate((("1normal", "normal"), ("2under1", "under1"), ("2under2", "under2"), ("3over", "over"), ("4mold", "mold"), ("5small", "small"))):
    ASSETS[f"berry_{_n}.239x233.png"] = (lambda k=_k: grapes(k, 17))
