"""Appraisal close-ups, food: the pie (lid, filled pie), pickled gherkins, ribs and the cloth wrap."""

from __future__ import annotations

import math
from collections.abc import Callable

from PIL import Image

from appraisalkit_b import Canvas, CLOTH, MEAT, PASTRY, PICKLE, SHADOW, bezier, leaf, stroke, superellipse
from pix import BAYER, Color, Pix, mix, rgb

W, H = 265, 104
GOLD = rgb("#f3dc92")


def band_shade(p: Pix, box, inside, light, ramp, sharp: float = 2.2) -> None:
    """Like a ramp fill with dither, but the dither band is narrow so tones read as painted bands."""
    n = len(ramp)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if not inside(x, y):
                continue
            v = min(0.999, max(0.0, light(x, y))) * (n - 1)
            i = int(v)
            f = min(1.0, max(0.0, (v - i - 0.5) * sharp + 0.5))
            if i < n - 1 and BAYER[y % 4][x % 4] < f * 16:
                i += 1
            p.px(x, y, ramp[i])


def _edge(p: Pix, box, inside, c: Color, lit: Color | None = None) -> None:
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if inside(x, y):
                if not inside(x + 1, y) or not inside(x, y + 1) or not inside(x - 1, y) or not inside(x, y - 1):
                    p.px(x, y, c)
                if lit and (not inside(x - 1, y - 1)) and inside(x, y) and inside(x + 1, y + 1):
                    p.px(x, y, lit)


def _lid(p: Pix, cx: float, cy: float, a: float, b: float, seeds: bool) -> None:
    """A pie lid seen from the side: rolled, crimped rim below and a glazed dome above with cuts for the steam."""
    rim_in = superellipse(cx, cy + 3, a, b - 2, 2.7, 2.0)
    rbox = (int(cx - a) - 1, int(cy - b) - 1, int(cx + a) + 2, int(cy + b) + 4)
    band_shade(p, rbox, rim_in, lambda x, y: 0.2 + 0.5 * (cy + b - y) / (2 * b) + 0.15 * (cx - x) / a, PASTRY)
    # crimping: pinched ridges around the lower rim
    for x in range(int(cx - a) + 4, int(cx + a) - 3, 4):
        for y in range(int(cy + b) - 12, int(cy + b) + 2):
            if rim_in(x, y) and rim_in(x, y + 2):
                p.px(x, y, PASTRY[1])
                p.px(x + 1, y, PASTRY[3] if x < cx + a * 0.4 else PASTRY[2])
    dome_in = superellipse(cx, cy - 3, a - 5, b - 8, 2.5, 2.0)
    light = lambda x, y: min(1.0, 0.42 + 0.5 * (cy - y) / b + 0.28 * (cx - x) / a * (1 - abs(y - cy) / b * 0.4))
    dbox = (int(cx - a), int(cy - b), int(cx + a) + 1, int(cy + b))
    band_shade(p, dbox, dome_in, light, PASTRY)
    _edge(p, dbox, dome_in, PASTRY[1], PASTRY[4])
    # the seam between dome and rim
    for x in range(dbox[0], dbox[2]):
        for y in range(dbox[3] - 18, dbox[3]):
            if dome_in(x, y) and not dome_in(x, y + 1) and y > cy:
                p.px(x, y + 1, PASTRY[0])
                p.px(x, y + 2, PASTRY[1])
    # glaze: a bright streak on the upper left of the dome
    for k in range(int(a * 0.5)):
        x = int(cx - a * 0.72 + k)
        y = int(cy - b * 0.62 + (k * k) / (a * 1.5) + (k * 0.12))
        if dome_in(x, y):
            p.px(x, y, GOLD)
            p.px(x + 1, y, PASTRY[4])
    # pastry leaves flank three steam cuts
    for sx, sgn in ((cx - 58, -1), (cx + 58, 1)):
        leaf(p, int(sx), int(cy - 2), sgn * 14, -5, 18, PASTRY[4], PASTRY[3])
        leaf(p, int(sx), int(cy - 1), sgn * 14, 5, 16, PASTRY[3], PASTRY[2])
        for k in range(0, 14, 1):
            p.px(int(sx + sgn * k), int(cy - 2 - k // 3 + 1), PASTRY[1])
    for k, sx in enumerate((cx - 26, cx, cx + 26)):
        pts = bezier([(sx - 7, cy - 6), (sx, cy - 10 + k % 2), (sx + 8, cy - 6)], 8)
        stroke(p, [(x, y + 1) for x, y in pts], PASTRY[4], 1)
        stroke(p, pts, rgb("#3a1a10"), 1)
        stroke(p, [(x, y - 1) for x, y in pts[2:-2]], PASTRY[1], 1)
    if seeds:
        for _ in range(int(a * b * 0.05)):
            x = p.rng.randint(int(cx - a * 0.8), int(cx + a * 0.8))
            y = p.rng.randint(int(cy - b * 0.7), int(cy + b * 0.35))
            if dome_in(x, y) and dome_in(x + 1, y + 1) and p.get(x, y) not in (PASTRY[0], rgb("#3a1a10")):
                c = rgb("#efe3b8") if p.rng.random() > 0.35 else rgb("#b8996a")
                p.px(x, y, c)
                p.px(x + 1, y, mix(c, PASTRY[1], 0.55))
    # shadow under the pie: two dithered rows beneath the rim
    snap = p.im.copy()
    for x in range(rbox[0], rbox[2]):
        for y in range(int(cy), rbox[3] + 3):
            if snap.getpixel((x, y))[3] == 0 and y > 0:
                for up in (1, 2):
                    if snap.getpixel((x, y - up))[3] and (up == 1 or (x + y) % 2 == 0):
                        p.px(x, y, mix(SHADOW, PASTRY[0], 0.35))
                        break


def top_lid(seeds: bool) -> Image.Image:
    p = Canvas(W, H, seed=21 if seeds else 20)
    _lid(p, 132, 34, 106, 29, seeds)
    return p.finish()


def _lump(p: Pix, cx: int, cy: int, a: int, b: int, ramp, slope: float = 0.0, outline: bool = True) -> None:
    def inside(x: int, y: int) -> bool:
        yy = y - slope * (x - cx)
        return abs((x + 0.5 - cx) / a) ** 2.3 + abs((yy + 0.5 - cy) / b) ** 2.0 <= 1.0
    box = (cx - a - 1, int(cy - b - abs(slope) * a) - 2, cx + a + 2, int(cy + b + abs(slope) * a) + 3)
    band_shade(p, box, inside, lambda x, y: 0.5 + 0.5 * ((cy - (y - slope * (x - cx))) / b) * 0.8 + 0.15 * (cx - x) / a, ramp)
    if outline:
        _edge(p, box, inside, ramp[0], ramp[4])


def _slices(p: Pix, xs, y_of, a: int, b: int) -> None:
    def slope(x: int) -> float:
        return (y_of(x + 4) - y_of(x - 4)) / 8
    for x in xs:
        s = slope(x)
        y = y_of(x)
        _lump(p, x, y, a, b, PICKLE, s)
        # the cut face: a paler flesh disc inside the dark skin, with a ring of seeds
        def flesh(xx: int, yy: int) -> bool:
            return abs((xx + 0.5 - x) / (a - 3)) ** 2 + abs((yy - s * (xx - x) + 0.5 - y) / max(1, b - 2)) ** 2 <= 1.0
        for yy in range(y - b - 4, y + b + 5):
            for xx in range(x - a, x + a + 1):
                if flesh(xx, yy):
                    p.px(xx, yy, PICKLE[2] if (xx + yy) % 5 else PICKLE[3])
        for k in (-a // 2 + 1, 0, a // 2 - 1):
            p.px(x + k, round(y + s * k), PICKLE[1])
            p.px(x + k + 1, round(y + s * k), PICKLE[2])


def _shards(p: Pix, xs, y_of) -> None:
    """Pale onion strips poking out between gherkin slices."""
    for x in xs:
        y = y_of(x) - 2
        d = -1 if x < 131 else 1
        for k in range(8):
            p.px(x + d * k, y - k // 2, rgb("#ebe2bc") if k % 3 else rgb("#bfb48c"))
            p.px(x + d * k, y - k // 2 + 1, rgb("#8e8462"))


def pickles(extra: bool) -> Image.Image:
    p = Canvas(W, H, seed=31)
    y_of = lambda x: round(54 + 15 * (1 - ((x - 131) / 112) ** 2))
    if extra:
        _slices(p, [34 + 24 * i for i in range(9)], lambda x: y_of(x) + 8, 14, 6)
    _slices(p, [34 + 24 * i for i in range(9)], y_of, 14, 6)
    _shards(p, [28, 62, 110, 150, 192, 232], y_of)
    return p.finish()


def ribs() -> Image.Image:
    p = Canvas(W, H, seed=41)
    rng = p.rng
    x0, x1 = 21, 241
    wave = {x: int(2.2 * math.sin(x / 8.0) + rng.randint(-1, 1)) for x in range(x0, x1)}
    taper = lambda x: max(0.0, 1 - abs((x - 131) / 112) ** 6) ** 0.5
    top = {x: round(80 - 30 * taper(x)) + wave[x] for x in range(x0, x1)}
    inside = lambda x, y: x0 <= x < x1 and top[x] <= y <= 84
    band_shade(p, (x0, 40, x1, 90), inside,
               lambda x, y: 0.2 + 0.18 * math.sin(x / 11.0 + y / 6) + (84 - y) / 110, MEAT, 1.2)
    _edge(p, (x0, 40, x1, 90), inside, MEAT[0])
    # lumps of meat between the bones along the lower edge, overlapping like the rack they are
    for cx in range(33, 228, 17):
        _lump(p, cx + rng.randint(-1, 1), 82 + rng.randint(-1, 2), 11, 8 + rng.randint(0, 2), MEAT)
    # bone tips and glossy glaze
    for x in range(x0 + 12, x1 - 12, 23):
        if top[x] < 62:
            p.rect(x, top[x] - 1, 5, 2, rgb("#d8caa6"))
            p.rect(x, top[x] + 1, 5, 1, rgb("#8a7a5e"))
    for sx, sy, ln in ((46, 60, 36), (112, 56, 52), (186, 61, 32)):
        p.hline(sx, sy, ln, MEAT[4])
        p.hline(sx + 5, sy + 1, ln - 14, MEAT[3])
    for x in range(x0 + 14, x1 - 10, 29):
        for k in range(rng.randint(3, 7)):      # sauce drips below the rack
            p.px(x, 92 + k // 2 - 4, MEAT[2])
    p.speckle(x0, 50, x1 - x0, 30, [MEAT[0], MEAT[1]], 0.02)
    return p.finish()


def double_meat() -> Image.Image:
    p = Canvas(W, H, seed=51)
    # bottom crust and the dark filling that fills every gap
    inside = superellipse(131, 90, 108, 13, 2.7, 2.0)
    band_shade(p, (20, 76, 244, 104), inside, lambda x, y: 0.2 + (90 - y) / 34 * 0.4 + 0.18 * (131 - x) / 108 * 0.5, PASTRY)
    _edge(p, (20, 76, 244, 104), inside, PASTRY[0])
    fill = superellipse(131, 72, 108, 20, 3.5, 2.0)
    for y in range(50, 94):
        for x in range(22, 242):
            if fill(x, y):
                p.px(x, y, MEAT[0])
    for i, cx in enumerate(range(34, 228, 18)):
        _lump(p, cx + p.rng.randint(-3, 3), 69 + (i % 2) * 3, 12 + p.rng.randint(0, 3), 8 + p.rng.randint(0, 2), MEAT)
    for i, cx in enumerate(range(36, 226, 18)):
        _lump(p, cx + p.rng.randint(-3, 3), 82 + (i % 2) * 2, 12 + p.rng.randint(0, 3), 7 + p.rng.randint(0, 2), MEAT)
    y_of = lambda x: 58 + (0 if (x // 17) % 2 else 1)
    _slices(p, [30 + 21 * i for i in range(11)], y_of, 14, 6)
    _shards(p, [30, 232], lambda x: 56)
    _lid(p, 131, 28, 109, 26, False)
    return p.finish()


def _fan(p: Pix, x: int, w: int, cy: int, half0: int, half1: int, side: int, y_pat: int) -> None:
    """A gathered end: pleats fan out from the neck (x of the tie) toward the free edge."""
    for k in range(w):
        t = k / (w - 1)
        half = round(half1 + (half0 - half1) * t)       # taller toward the free edge
        for dy in range(-half, half + 1):
            fold = (dy * 5) // max(4, 3 + k // 2) + y_pat
            tone = (1, 3, 2, 4)[fold % 4]
            if abs(dy) >= half - 1:
                tone = 0
            p.px(x + side * k, cy + dy, CLOTH[tone])


def _tie(p: Pix, x: int, cy: int, half: int) -> None:
    for dx in range(3):
        for dy in range(-half, half + 1):
            p.px(x + dx, cy + dy, (rgb("#521a20"), rgb("#a13a38"), rgb("#7a272b"))[dx])
    # knot and two cord tails
    p.rect(x - 1, cy - 2, 5, 5, rgb("#a13a38"))
    p.rect(x, cy - 1, 3, 3, rgb("#c25b49"))
    for k in range(1, 7):
        p.px(x + 1 + (k // 2), cy + 3 + k, rgb("#7a272b"))
        p.px(x - 1 - (k // 3), cy - 3 - k, rgb("#7a272b"))


def wrap(opened: bool) -> Image.Image:
    p = Canvas(W, H, seed=61)
    cx, cy, a, b = 133.0, 52.0, 106.0, 49.0
    gloss = (*CLOTH[2], 150)
    for t in range(0, 1440):
        ang = t * math.pi / 720
        x = cx + a * math.cos(ang)
        y = cy + b * math.sin(ang)
        if opened and x < 62 and 22 < y < 84:
            continue
        for d in range(3):
            yy = round(y) + (d if y > cy else -d)
            c = (*CLOTH[3], 190) if d == 0 else (gloss if d == 1 else (*CLOTH[1], 120))
            p.px(round(x), yy, c)
    # sheen: the film catches the lantern at the upper left
    for k in range(40, 130):
        yy = round(cy - b * math.sqrt(max(0, 1 - ((k + 30 - cx) / a) ** 2))) + 5
        p.px(k + 30, yy, (*CLOTH[4], 150) if k % 5 else (*CLOTH[3], 150))
    # long sharp folds run from each gathered end into the body, as in a tightly wrapped cloth
    ends = [(232, 1)] if opened else [(28, 1), (232, 1)]
    for ex, _ in ends:
        d = 1 if ex < 130 else -1
        for dy, ln in ((-20, 58), (-8, 70), (6, 66), (18, 52), (-30, 36), (30, 34)):
            for k in range(ln):
                w = max(0, 3 - (3 * k) // ln)
                yy = 52 + round(dy * (1 - (k / ln) * 0.25)) + round(0.05 * dy * k / 3)
                for j in range(w):
                    p.px(ex + d * (6 + k), yy + j - (w // 2), CLOTH[4] if j == 0 else CLOTH[3])
    for sx, ln in ((82, 40), (176, 34)):
        p.hline(sx, 49, ln, CLOTH[4])
        p.hline(sx + 8, 50, ln - 16, CLOTH[3])
    if not opened:
        _fan(p, 0, 27, 52, 40, 29, 1, 0)
        _tie(p, 27, 52, 29)
    _fan(p, 260, 28, 52, 40, 29, -1, 1)
    _tie(p, 232, 52, 29)
    if opened:
        # the left end undone and flipped over: a flat flap with its lighter inner face showing
        outer = [(0, 12), (40, 26), (62, 50), (52, 78), (0, 94)]
        p.poly(outer, CLOTH[2])
        p.poly([(0, 12), (40, 26), (62, 50), (24, 50)], CLOTH[4])
        p.poly([(0, 12), (24, 50), (0, 52)], CLOTH[3])
        p.poly([(24, 50), (62, 50), (52, 78), (0, 94), (0, 60)], CLOTH[2])
        for i, (x, y) in enumerate(outer):
            nx, ny = outer[(i + 1) % len(outer)]
            p.line(x, y, nx, ny, CLOTH[0] if i > 2 else CLOTH[1])
        for y in range(60, 94, 3):
            p.hline(0, y, 6 + (y % 7) * 3, CLOTH[1])
        p.line(24, 50, 62, 50, CLOTH[1])
        p.line(2, 14, 30, 48, CLOTH[3])
    return p.finish()


DRAWINGS: dict[str, Callable[[], Image.Image]] = {
    "top_bun_normal.265x104.png": lambda: top_lid(False),
    "top_bun_deluxe.265x104.png": lambda: top_lid(True),
    "double_meat.265x104.png": double_meat,
    "pickles.265x104.png": lambda: pickles(False),
    "pickles_extra.265x104.png": lambda: pickles(True),
    "ribs.265x104.png": ribs,
    "warp_normal.265x104.png": lambda: wrap(False),
    "wrap_open_flipped.265x104.png": lambda: wrap(True),
}
