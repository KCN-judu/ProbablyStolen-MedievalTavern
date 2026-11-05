"""Shared drawing helpers for the bow pictures: shaded strokes along curves, arrows with fletching, a leather grip.

Everything is whole pixels. A stroke is drawn as a chain of small discs in four passes (outline, body, mid light, highlight),
each pass nudged toward the upper left, so a limb of two or three pixels still has a lit and a shaded side.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from palette import BRASS, IRON, LEATHER, LINEN, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE
from pix import Color, Pix, Ramp, mix, rgb

Pt = tuple[float, float]

# Skin of a tavern hand: warm, a little weathered. Dark to light.
SKIN: Sequence[Color] = (rgb("#5a3328"), rgb("#8a5238"), rgb("#b2754f"), rgb("#d39a6c"), rgb("#e8b98a"))
# Yew: the bow's own wood, a shade darker than PALE_WOOD so it sits in the dim under the counter.
YEW: Sequence[Color] = (rgb("#2e1c12"), rgb("#4d3220"), rgb("#74502e"), rgb("#9a7440"), rgb("#bf9a5c"))


def bez(a: Pt, c: Pt, b: Pt, n: int = 80) -> list[Pt]:
    """Points of a quadratic curve from a to b bent toward the control point c."""
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in (i / (n - 1) for i in range(n))]


def _disc(p: Pix, x: float, y: float, d: float, c: Color) -> None:
    r = max(1, round(d))
    x0, y0 = round(x - r / 2 + 0.01), round(y - r / 2 + 0.01)
    if r <= 2:
        p.rect(x0, y0, r, r, c)
    else:
        p.draw.ellipse((x0, y0, x0 + r - 1, y0 + r - 1), fill=c if len(c) == 4 else (*c, 255))


def taper(a: float, b: float, n: int, mid: float | None = None) -> list[float]:
    """Widths along a stroke: from a to b, or a to `mid` at the middle and back to b (a limb thick at the grip)."""
    if mid is None:
        return [a + (b - a) * i / (n - 1) for i in range(n)]
    out = []
    for i in range(n):
        t = i / (n - 1)
        k = 1 - abs(2 * t - 1)
        out.append(a + (mid - a) * k if t < 0.5 else b + (mid - b) * k)
    return out


def stroke(p: Pix, pts: Sequence[Pt], widths: Sequence[float], ramp: Sequence[Color], outline: bool = True,
           light: tuple[int, int] = (-1, -1)) -> None:
    """A lit, outlined, tapering tube along a path (ramp dark to light, at least four tones)."""
    lx, ly = light
    if outline:
        for (x, y), w in zip(pts, widths):
            _disc(p, x, y, w + 2, ramp[0])
    for (x, y), w in zip(pts, widths):
        _disc(p, x, y, w, ramp[1])
    for (x, y), w in zip(pts, widths):
        if w >= 3:
            _disc(p, x + lx * 0.5, y + ly * 0.5, w - 1.5, ramp[2])
    for (x, y), w in zip(pts, widths):
        if w >= 5:
            _disc(p, x + lx, y + ly, w - 3.5, ramp[3 if len(ramp) > 3 else 2])
        elif w >= 3:
            _disc(p, x + lx, y + ly, 1, ramp[3 if len(ramp) > 3 else 2])


def grain(p: Pix, pts: Sequence[Pt], widths: Sequence[float], ramp: Sequence[Color], every: int = 3) -> None:
    """Little streaks of lighter and darker wood along a stroke, so the stave reads as grained timber."""
    for i in range(2, len(pts) - 2, every):
        (x, y), w = pts[i], widths[i]
        if w < 4:
            continue
        side = p.rng.choice((-1, 1)) * (w / 4)
        p.px(round(x + side), round(y), ramp[p.rng.choice((1, 3))])


def string(p: Pix, a: Pt, b: Pt, c: Color | None = None) -> None:
    """A bowstring: a one-pixel waxed linen line."""
    p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), c or LINEN[2])


def arrow(p: Pix, tail: Pt, head: Pt, vane: int = 3, head_len: int = 5, shaft: Sequence[Color] = PALE_WOOD,
          fletch: Sequence[Color] = (PARCHMENT[3], PARCHMENT[2], WINE[3]), show_head: bool = True) -> None:
    """An arrow from tail to head: a pale shaft, an iron broadhead, three feather vanes at the tail (one wine-red cock feather)."""
    dx, dy = head[0] - tail[0], head[1] - tail[1]
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy, ux
    # shaft: a dark underside line, then the lit line
    p.line(round(tail[0] + 1), round(tail[1] + 1), round(head[0] + 1), round(head[1] + 1), shaft[1])
    p.line(round(tail[0]), round(tail[1]), round(head[0]), round(head[1]), shaft[3])
    # fletching: three vanes along the first sixth of the shaft, slanted backward
    flen = min(max(5, ln * 0.2), 14)
    for k, (side, col) in enumerate(((1, fletch[0]), (-1, fletch[1]), (0, fletch[2]))):
        off = side * vane if side else 0
        pts = [(tail[0], tail[1]),
               (tail[0] + ux * flen * 0.35 + nx * off, tail[1] + uy * flen * 0.35 + ny * off),
               (tail[0] + ux * flen + nx * off * 0.7, tail[1] + uy * flen + ny * off * 0.7),
               (tail[0] + ux * flen, tail[1] + uy * flen)]
        if side:
            p.poly([(round(x), round(y)) for x, y in pts], col)
            p.line(round(tail[0]), round(tail[1]), round(pts[2][0]), round(pts[2][1]), mix(col, SHADOW, 0.45))
        else:
            p.line(round(tail[0] + ux), round(tail[1] + uy), round(tail[0] + ux * flen), round(tail[1] + uy * flen), col)
    # nock: a dark notch at the very end
    p.px(round(tail[0]), round(tail[1]), SHADOW)
    if show_head:
        tip = head
        bx, by = head[0] - ux * head_len, head[1] - uy * head_len
        w = max(1.5, vane * 0.6)
        p.poly([(round(tip[0]), round(tip[1])), (round(bx + nx * w), round(by + ny * w)), (round(bx - nx * w), round(by - ny * w))], IRON[3])
        p.line(round(tip[0]), round(tip[1]), round(bx + nx * w), round(by + ny * w), IRON[4])
        p.line(round(tip[0]), round(tip[1]), round(bx - nx * w), round(by - ny * w), IRON[1])


def wrap_grip(p: Pix, a: Pt, b: Pt, width: float, ramp: Sequence[Color] = LEATHER) -> None:
    """A leather-bound handle from a to b: a thick stroke with slanted binding lines and brass-dull end rings."""
    n = max(2, round(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
    pts = [(a[0] + (b[0] - a[0]) * i / (n - 1), a[1] + (b[1] - a[1]) * i / (n - 1)) for i in range(n)]
    stroke(p, pts, [width] * n, ramp)
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy, ux
    steps = int(ln // 3)
    for k in range(1, steps):
        cx, cy = a[0] + ux * k * 3, a[1] + uy * k * 3
        h = width / 2 - 0.5
        p.line(round(cx - nx * h - ux), round(cy - ny * h - uy), round(cx + nx * h + ux), round(cy + ny * h + uy), ramp[0])
    for end in (a, b):
        p.line(round(end[0] - nx * (width / 2)), round(end[1] - ny * (width / 2)), round(end[0] + nx * (width / 2)), round(end[1] + ny * (width / 2)), BRASS[2])


def nock_tip(p: Pix, at: Pt, toward: Pt) -> None:
    """A bone-coloured tip cap where a limb ends and the string loops on."""
    dx, dy = toward[0] - at[0], toward[1] - at[1]
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    for i in range(3):
        p.px(round(at[0] - ux * i), round(at[1] - uy * i), PARCHMENT[2 + (i == 0)])
