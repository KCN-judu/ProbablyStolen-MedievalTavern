"""Helpers for the second half of the appraisal close-ups: shaded shapes, hand-lettering, curves, wax and brass.

Everything is whole-pixel. `shade` is the workhorse: it fills a shape with a ramp driven by a lighting function and
ordered dither, so rounded things get modelling without any smooth blending.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from font import GLYPHS
from pix import BAYER, CLEAR, Color, Pix, Ramp, mix, rgb

class Canvas(Pix):
    """A Pix that rounds fractional coordinates, so curve and ring code can pass floats."""

    def px(self, x: float, y: float, c: Color) -> None:
        super().px(int(round(x)), int(round(y)), c)


Inside = Callable[[int, int], bool]
Light = Callable[[int, int], float]

# Own tones, kept near the pack palette: pastry, ink, wax, vial glass.
PASTRY: Sequence[Color] = (rgb("#4a2418"), rgb("#7a4222"), rgb("#a96a34"), rgb("#cf9248"), rgb("#ecc272"))
MEAT: Sequence[Color] = (rgb("#2a0f12"), rgb("#4a1a1c"), rgb("#6e2926"), rgb("#92403a"), rgb("#b4604c"))
PICKLE: Sequence[Color] = (rgb("#1c2a14"), rgb("#34481f"), rgb("#55702c"), rgb("#7f9640"), rgb("#aab868"))
CLOTH: Sequence[Color] = (rgb("#5b5246"), rgb("#8a8070"), rgb("#b4aa94"), rgb("#d6ccb2"), rgb("#ece3c6"))
WAX: Sequence[Color] = (rgb("#2e0c10"), rgb("#52161c"), rgb("#7a2226"), rgb("#a1332f"), rgb("#c65a44"))
INK = rgb("#2c1f2a")
BRASS = (rgb("#3a2a12"), rgb("#6b4c1c"), rgb("#a07a2c"), rgb("#d0a847"), rgb("#f0d27a"))
IRON = (rgb("#141318"), rgb("#26252c"), rgb("#3b3a43"), rgb("#575660"), rgb("#7a7983"))
PARCH = (rgb("#6b5a36"), rgb("#9a8450"), rgb("#c4ad78"), rgb("#e0cf9f"), rgb("#f0e3bb"))
SHADOW = rgb("#170f12")


def shade(p: Pix, box: tuple[int, int, int, int], inside: Inside, light: Light, ramp: Sequence[Color],
          bias: float = 0.0) -> None:
    """Fills the pixels of `box` for which `inside` holds; `light` (0 dark .. 1 lit) picks the tone, dithered between."""
    n = len(ramp)
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not inside(x, y):
                continue
            v = min(1.0, max(0.0, light(x, y) + bias)) * (n - 1)
            i = int(v)
            frac = v - i
            if i < n - 1 and BAYER[y % 4][x % 4] < frac * 16:
                i += 1
            p.px(x, y, ramp[min(i, n - 1)])


def dome_light(cx: float, cy: float, a: float, b: float, lx: float = -0.45, ly: float = -0.6) -> Light:
    """Lighting of a flattened dome: the surface normal of an ellipse lit from the upper left."""
    def f(x: int, y: int) -> float:
        nx, ny = (x - cx) / a, (y - cy) / b
        r2 = min(1.0, nx * nx + ny * ny)
        z = math.sqrt(1 - r2)
        return max(0.0, min(1.0, 0.45 + 0.55 * (nx * lx + ny * ly + z * 0.65) / 0.95 * 0.9))
    return f


def superellipse(cx: float, cy: float, a: float, b: float, n: float = 2.6, m: float = 2.0) -> Inside:
    return lambda x, y: abs((x + 0.5 - cx) / a) ** n + abs((y + 0.5 - cy) / b) ** m <= 1.0


def ring(p: Pix, cx: float, cy: float, r_out: float, r_in: float, c: Color) -> None:
    for y in range(int(cy - r_out) - 1, int(cy + r_out) + 2):
        for x in range(int(cx - r_out) - 1, int(cx + r_out) + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r_in <= d <= r_out:
                p.px(x, y, c)


def disc(p: Pix, cx: float, cy: float, r: float, c: Color) -> None:
    ring(p, cx, cy, r, 0, c)


def bezier(pts: Sequence[tuple[float, float]], steps: int = 40) -> list[tuple[int, int]]:
    """Catmull-Rom curve through the points, as pixel positions."""
    out: list[tuple[int, int]] = []
    q = [pts[0], *pts, pts[-1]]
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((round(x), round(y)))
    out.append((round(pts[-1][0]), round(pts[-1][1])))
    return out


def stroke(p: Pix, path: Sequence[tuple[int, int]], c: Color, width: int = 1) -> None:
    for x, y in path:
        if width == 1:
            p.px(x, y, c)
        else:
            p.rect(x, y, width, width, c)


def spiral(cx: float, cy: float, r0: float, turns: float, start: float, sign: int = 1) -> list[tuple[float, float]]:
    pts = []
    n = int(turns * 12) + 1
    for i in range(n):
        t = i / (n - 1)
        a = start + sign * t * turns * 2 * math.pi
        r = r0 * (1 - 0.85 * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def leaf(p: Pix, x: int, y: int, dx: int, dy: int, length: int, c: Color, c2: Color) -> None:
    """A small pointed leaf grown from (x, y) toward (dx, dy), lit on one side."""
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    for i in range(length + 1):
        w = math.sin(math.pi * i / length) * length * 0.32
        for k in range(-int(w), int(w) + 1):
            px, py = x + ux * i - uy * k, y + uy * i + ux * k
            p.px(round(px), round(py), c if k <= 0 else c2)


# --------------------------------------------------------------------------------- hand lettering

def glyph_cells(ch: str) -> list[str]:
    return list(GLYPHS.get(ch.upper(), ["00000"] * 7))


def resample(rows: Sequence[str], w: int, h: int) -> list[str]:
    """Nearest-neighbour resize of a glyph bitmap (used to stretch the 5x7 alphabet into tall pen-letters)."""
    sh, sw = len(rows), len(rows[0])
    return ["".join(rows[min(sh - 1, y * sh // h)][min(sw - 1, x * sw // w)] for x in range(w)) for y in range(h)]


def write_cells(p: Pix, x: int, y: int, rows: Sequence[str], c: Color, bold: bool = False, shear: int = 0) -> None:
    h = len(rows)
    for j, row in enumerate(rows):
        off = shear * (h - 1 - j) // max(1, h - 1)
        for i, ch in enumerate(row):
            if ch == "1":
                p.px(x + i + off, y + j, c)
                if bold:
                    p.px(x + i + off + 1, y + j, c)


def text_line(p: Pix, x: int, y: int, text: str, c: Color, bold: bool = False, shear: int = 0, gap: int = 1,
              w: int = 5, h: int = 7) -> int:
    """Writes `text` in the 5x7 alphabet (resized to w x h); returns the x after the last letter."""
    for ch in text:
        if ch == " ":
            x += w
            continue
        rows = glyph_cells(ch) if (w, h) == (5, 7) else squeeze(glyph_cells(ch), w, h)
        write_cells(p, x, y, rows, c, bold, shear)
        x += w + gap
    return x


def scribble(p: Pix, x: int, y: int, w: int, c: Color, seed: int) -> None:
    """A line of unreadable pen script: little loops and strokes."""
    import random
    r = random.Random(seed)
    cx = x
    while cx < x + w - 2:
        k = r.choice((0, 1, 2, 3))
        if k == 0:
            p.vline(cx, y - 2, 4, c)
        elif k == 1:
            p.px(cx, y, c); p.px(cx + 1, y - 1, c); p.px(cx + 2, y, c); p.px(cx + 1, y + 1, c)
            cx += 1
        elif k == 2:
            p.hline(cx, y, 3, c); p.px(cx, y - 1, c)
            cx += 1
        else:
            p.vline(cx, y - 1, 3, c); p.px(cx + 1, y - 2, c)
        cx += 3


def torn_polygon(rng, pts: Sequence[tuple[int, int]], jitter: int = 1) -> list[tuple[int, int]]:
    return [(x + rng.randint(-jitter, jitter), y + rng.randint(-jitter, jitter)) for x, y in pts]


def band_shade(p: Pix, box: tuple[int, int, int, int], inside: Inside, light: Light, ramp: Sequence[Color],
               sharp: float = 2.2) -> None:
    """Like `shade` but with a narrow dither band, so tones read as painted bands and not as a screen of dots."""
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


def squeeze(rows: Sequence[str], w: int, h: int) -> list[str]:
    """Shrinks a glyph by dropping the columns and rows that carry the least information (so small text stays legible)."""
    r = list(rows)
    while len(r[0]) > w:
        best = min(range(1, len(r[0]) - 1), key=lambda c: sum((row[c] != row[c - 1]) + (row[c] != row[c + 1]) for row in r))
        r = [row[:best] + row[best + 1:] for row in r]
    while len(r) > h:
        best = min(range(1, len(r) - 1), key=lambda i: sum((a != b) + (a != c) for a, b, c in zip(r[i], r[i - 1], r[i + 1])))
        r = r[:best] + r[best + 1:]
    return r
