"""Small drawing helpers for the bazaar picture: lit pools, lanterns, lettering, silhouettes, boards and beams.

All of it paints whole pixels. Light is added over what is already drawn (so texture survives under a glow), in a few
dithered steps, which is how the original's lantern light reads.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from PIL import Image

import font
from pix import BAYER, Color, Pix, mix, rgb

Pt = tuple[float, float]


def ramp(*hexes: str) -> list[Color]:
    return [rgb(h) if isinstance(h, str) else h for h in hexes]


# night materials, dark to light
PLUM = ramp("#15121f", "#1f1a2c", "#2b2540", "#3a3252", "#4d4366")       # shadowed walls in cool moonlight
SLATE = ramp("#12121c", "#1b1c2a", "#272a3c", "#363b52", "#4b526c")      # blue-grey stone
BRICKRED = ramp("#2a1218", "#43191f", "#5f232a", "#7e3030", "#9d4538")   # red-painted timber
TEAL = ramp("#0f2428", "#17393e", "#235257", "#37767a", "#5ea3a3")       # cool lit glass and boards
DKWOOD = ramp("#140d12", "#201419", "#2f1e21", "#43292a", "#5a3a34")
CREAM = ramp("#6b5a48", "#9a8466", "#c4ab80", "#e2cd9e", "#f3e6c0")


def clampc(c: Sequence[float]) -> Color:
    return (max(0, min(255, int(c[0]))), max(0, min(255, int(c[1]))), max(0, min(255, int(c[2]))))


def addlight(p: Pix, x: int, y: int, col: Color, a: float) -> None:
    """Brightens one pixel toward a light colour, keeping the pixel's own hue (so wood stays wood)."""
    if 0 <= x < p.w and 0 <= y < p.h:
        r, g, b, al = p.im.getpixel((x, y))
        p.im.putpixel((x, y), (*clampc((r + col[0] * a, g + col[1] * a, b + col[2] * a)), al))


def pool(p: Pix, cx: float, cy: float, rx: float, ry: float, col: Color, k: float = 1.0, steps: int = 6, power: float = 1.6,
         box: tuple[int, int, int, int] | None = None) -> None:
    """A pool of light added over the picture: ellipse falloff cut in `steps` dithered bands."""
    x0, x1 = max(0, int(cx - rx)), min(p.w, int(cx + rx) + 1)
    y0, y1 = max(0, int(cy - ry)), min(p.h, int(cy + ry) + 1)
    if box:
        x0, y0, x1, y1 = max(x0, box[0]), max(y0, box[1]), min(x1, box[2]), min(y1, box[3])
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d >= 1:
                continue
            lv = (1 - d) ** power * k * steps
            n = int(lv)
            if lv - n > (BAYER[y % 4][x % 4] + 0.5) / 16:
                n += 1
            if n:
                addlight(p, x, y, col, min(1.0, n / steps) * 0.85)


def shade(p: Pix, pts: Sequence[tuple[int, int]], col: Color, t: float) -> None:
    """Mixes every pixel in a polygon toward `col` (haze, shadow, tint)."""
    m = Image.new("L", p.im.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).polygon(list(pts), fill=255)
    bb = m.getbbox()
    if not bb:
        return
    for y in range(bb[1], bb[3]):
        for x in range(bb[0], bb[2]):
            if m.getpixel((x, y)):
                r, g, b, a = p.im.getpixel((x, y))
                p.im.putpixel((x, y), (*mix((r, g, b), col, t), a))


def haze(p: Pix, x: int, y: int, w: int, h: int, col: Color, top: float, bottom: float, steps: int = 6) -> None:
    """A haze band whose strength runs from `top` to `bottom` down the rectangle, dithered in steps."""
    for yy in range(max(0, y), min(p.h, y + h)):
        t = top + (bottom - top) * (yy - y) / max(1, h - 1)
        lv = t * steps
        n = int(lv)
        for xx in range(max(0, x), min(p.w, x + w)):
            m = n + (1 if lv - n > (BAYER[yy % 4][xx % 4] + 0.5) / 16 else 0)
            if m:
                r, g, b, a = p.im.getpixel((xx, yy))
                p.im.putpixel((xx, yy), (*mix((r, g, b), col, m / steps), a))


def text(p: Pix, x: int, y: int, s: str, c: Color, scale: int = 1, shadow: Color | None = None) -> None:
    if shadow:
        font.write(p, x + scale, y + scale, s, shadow, scale)
    font.write(p, x, y, s, c, scale)


def slanted_text(p: Pix, x: int, y: int, s: str, c: Color, scale: int, slope: float) -> None:
    """Lettering on a board that recedes: every column is lifted by `slope` px per px of x (whole pixels)."""
    w = font.width(s, scale) + 1
    t = Pix(w, 7 * scale + 1)
    font.write(t, 0, 0, s, c, scale)
    for i in range(w):
        col = t.im.crop((i, 0, i + 1, t.h))
        p.paste(col, x + i, y + int(round(i * slope)))


def beam(p: Pix, x0: float, y0: float, x1: float, y1: float, w: int, rp: Sequence[Color], light: bool = True) -> None:
    """A straight timber or rail: dark body, a lit upper edge, a shaded lower edge."""
    dx, dy = x1 - x0, y1 - y0
    n = max(1, int(max(abs(dx), abs(dy))))
    for i in range(n + 1):
        x, y = x0 + dx * i / n, y0 + dy * i / n
        steep = abs(dy) > abs(dx)
        for k in range(w):
            off = k - (w - 1) / 2
            xx, yy = (x + off, y) if steep else (x, y + off)
            tone = 2 if w < 3 else (3 if k == 0 and light else (1 if k == w - 1 else 2))
            p.px(int(round(xx)), int(round(yy)), rp[min(tone, len(rp) - 1)])


def rail_post_grid(p: Pix, x0: int, y0: int, x1: int, y1: int, step: int, rp: Sequence[Color]) -> None:
    for x in range(x0, x1 + 1, step):
        p.vline(x, y0, y1 - y0 + 1, rp[2])
        p.px(x, y0, rp[3])
    p.hline(x0, y0, x1 - x0 + 1, rp[3])
    p.hline(x0, y1, x1 - x0 + 1, rp[1])


def lantern(p: Pix, cx: int, top: int, rx: int, ry: int, col: str = "red", tassel: bool = True) -> tuple[int, int]:
    """A paper lantern hanging from `top` (the cap): ribbed ellipse body, dark caps, a glow. Returns its centre."""
    pal = {
        "red": ramp("#4a0e10", "#8a1a16", "#c8321c", "#ee6a2c", "#ffb25a"),
        "orange": ramp("#5a2208", "#a04412", "#dc7420", "#f6a43c", "#ffd780"),
        "green": ramp("#0e3a24", "#1d6a3c", "#3aa65a", "#7cd878", "#d4f8a8"),
    }[col]
    cy = top + 3 + ry
    for y in range(cy - ry, cy + ry + 1):
        dy = (y - cy) / ry
        hw = int(round(rx * math.sqrt(max(0.0, 1 - dy * dy))))
        for x in range(cx - hw, cx + hw + 1):
            u = (x - cx) / max(1, rx)
            v = 3 - (u + 0.35) * 2.2 - abs(dy) * 1.1
            idx = max(0, min(4, int(v + 0.6)))
            if abs(u) > 0.92 or abs(dy) > 0.93:
                idx = 0
            elif (x - cx) % max(2, rx // 2) == 0 and abs(u) < 0.9:
                idx = max(0, idx - 1)         # rib
            p.px(x, y, pal[idx])
    p.rect(cx - max(2, rx // 2), top, max(4, rx), 3, (30, 18, 18))
    p.hline(cx - max(2, rx // 2), top, max(4, rx), (74, 50, 36))
    p.rect(cx - max(2, rx // 2), cy + ry, max(4, rx), 2, (30, 18, 18))
    p.vline(cx, top - 4, 4, (40, 28, 24))
    if tassel:
        p.vline(cx, cy + ry + 2, 4, pal[2])
        p.px(cx - 1, cy + ry + 5, pal[1]); p.px(cx + 1, cy + ry + 5, pal[1])
    return cx, cy


def silhouette(p: Pix, pts: Sequence[tuple[int, int]], body: Color, rim: Color | None = None, rim_side: str = "l") -> None:
    """A solid dark figure with an optional thin rim light along its lit side (the original's cyan edge)."""
    p.poly(list(pts), body)
    if rim:
        m = Image.new("L", p.im.size, 0)
        from PIL import ImageDraw
        ImageDraw.Draw(m).polygon(list(pts), fill=255)
        bb = m.getbbox()
        if bb:
            for y in range(bb[1], bb[3]):
                for x in range(bb[0], bb[2]):
                    if m.getpixel((x, y)):
                        nx = x - 1 if rim_side == "l" else x + 1
                        if nx < 0 or nx >= p.w or not m.getpixel((nx, y)) or (y > 0 and not m.getpixel((x, y - 1)) and (x + y) % 2 == 0):
                            p.px(x, y, rim)


def ell(p: Pix, cx: float, cy: float, rx: float, ry: float, c: Color) -> None:
    p.ellipse(int(cx - rx), int(cy - ry), int(2 * rx) + 1, int(2 * ry) + 1, c)


def shaded_ell(p: Pix, cx: float, cy: float, rx: float, ry: float, rp: Sequence[Color]) -> None:
    """A rounded form lit from the upper left: ramp index follows a sphere-ish normal."""
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            u, v = (x - cx) / rx, (y - cy) / ry
            if u * u + v * v <= 1:
                l = 0.5 - 0.5 * (u * 0.6 + v * 0.7) - 0.15 * (u * u + v * v)
                p.px(x, y, rp[max(0, min(len(rp) - 1, int(l * len(rp) + 0.5)))])


def plank_rect(p: Pix, x: int, y: int, w: int, h: int, rp: Sequence[Color], vertical: bool = True, board: int = 5, seed: int = 0) -> None:
    """Quick boards: each its own tone, a lit left edge, a dark seam, a few grain dashes and nail dots."""
    import random
    rng = random.Random(seed * 7919 + x * 31 + y)
    n = (w if vertical else h)
    i = 0
    while i < n:
        bw = max(2, board + rng.randint(-1, 1))
        tone = rng.randint(1, 3)
        if vertical:
            p.rect(x + i, y, bw, h, rp[tone])
            p.vline(x + i, y, h, rp[min(4, tone + 1)])
            p.vline(x + i + bw - 1, y, h, rp[0])
            for _ in range(max(1, h // 14)):
                gx, gy = x + i + rng.randint(1, max(1, bw - 2)), y + rng.randint(0, max(0, h - 5))
                p.vline(gx, gy, rng.randint(2, 6), rp[max(0, tone - 1)])
        else:
            p.rect(x, y + i, w, bw, rp[tone])
            p.hline(x, y + i, w, rp[min(4, tone + 1)])
            p.hline(x, y + i + bw - 1, w, rp[0])
            for _ in range(max(1, w // 14)):
                gx, gy = x + rng.randint(0, max(0, w - 5)), y + i + rng.randint(1, max(1, bw - 2))
                p.hline(gx, gy, rng.randint(2, 6), rp[max(0, tone - 1)])
        i += bw
