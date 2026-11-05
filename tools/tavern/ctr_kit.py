"""Helpers of the `ctr_` modules (things on and above the counter): a horizontal plane that is painted by inverse mapping,
round brass pieces (cones, horns, tubes), and small shading utilities. Built on `fxkit` and `propsy_fx.Cuboid`; nothing
here edits the shared kit.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from PIL import Image, ImageDraw

import fxkit as fx
from palette import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD
from pix import Color, Pix, Ramp, mix
from propsy_fx import Cuboid

Pt = tuple[float, float]


def mask(size: tuple[int, int], pts: Sequence[Pt]) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for x, y in pts], fill=255)
    return m


def fill(p: Pix, pts: Sequence[Pt], at: Callable[[int, int], Color | None]) -> None:
    """Paints what `at(x, y)` returns on every pixel inside the polygon (None leaves the pixel alone)."""
    m = mask((p.w, p.h), pts)
    bb = m.getbbox()
    if not bb:
        return
    for y in range(bb[1], bb[3]):
        for x in range(bb[0], bb[2]):
            if m.getpixel((x, y)):
                c = at(x, y)
                if c is not None:
                    p.px(x, y, c)


def tone(ramp: Ramp, v: float) -> Color:
    """Ramp tone for a fractional index (rounded; no dither, for small pieces)."""
    return ramp[max(0, min(len(ramp) - 1, round(v)))]


class Plane:
    """The top of a Cuboid as a world plane: `px` along the near edge, `pz` depth (0 near .. `depth` far)."""

    def __init__(self, box: Cuboid, depth: float) -> None:
        self.box, self.depth = box, depth

    def pt(self, px: float, pz: float, up: float = 0.0) -> Pt:
        return self.box.top_pt(pz / self.depth, px, up)

    def back(self, x: int, y: int) -> Pt:
        u, xn = self.box.top_uv(x, y)
        return xn, u * self.depth

    def back_lift(self, x: int, y: int, up: float) -> Pt:
        """Plane coordinates of a screen pixel that lies on a level `up` px above the plane (a book's top)."""
        s = (y - self.box.vp[1]) / (self.box.y_top - self.box.vp[1])
        for _ in range(3):
            s = (y + up * s - self.box.vp[1]) / (self.box.y_top - self.box.vp[1])
        u = (1 - s) / (1 - self.box.s_far)
        return self.box.vp[0] + (x - self.box.vp[0]) / s, u * self.depth

    def circle(self, cx: float, cz: float, r: float, n: int = 48, up: float = 0.0) -> list[Pt]:
        return [self.pt(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n), up) for i in range(n)]

    def paint(self, p: Pix, at: Callable[[float, float, int, int], Color | None], pts: Sequence[Pt] | None = None) -> None:
        fill(p, pts if pts is not None else self.box.top_poly(), lambda x, y: at(*self.back(x, y), x, y))


def slab(p: Pix, pl: Plane, px0: float, px1: float, pz0: float, pz1: float, up: float,
         top: Callable[[float, float, int, int], Color | None], front: Callable[[int, int, float], Color | None],
         left: Callable[[int, int, float], Color | None] | None = None, base: float = 0.0) -> None:
    """A flat box lying on a plane: footprint px0..px1 x pz0..pz1, `up` px thick, standing `base` above the plane.
    `top(px, pz, x, y)`, `front(x, y, t)` (t 0 at the bottom .. 1 at the top) and `left(x, y, t)` give the colours."""
    P = pl.pt
    if left is not None:
        fill(p, [P(px0, pz0, base), P(px0, pz1, base), P(px0, pz1, base + up), P(px0, pz0, base + up)],
             lambda x, y: left(x, y, 0.5))
    fill(p, [P(px0, pz0, base), P(px1, pz0, base), P(px1, pz0, base + up), P(px0, pz0, base + up)],
         lambda x, y: front(x, y, (P(px0, pz0, base)[1] - y) / max(1.0, up)))
    quad = [P(px0, pz0, base + up), P(px1, pz0, base + up), P(px1, pz1, base + up), P(px0, pz1, base + up)]
    fill(p, quad, lambda x, y: top(*pl.back_lift(x, y, base + up), x, y))


def ri(pt: Pt) -> tuple[int, int]:
    return round(pt[0]), round(pt[1])


def line(p: Pix, a: Pt, b: Pt, c: Color) -> None:
    p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), c)


def thick_line(p: Pix, a: Pt, b: Pt, ramp: Ramp, w: int = 2, lit: int = 3) -> None:
    """A rod seen from the side: dark underside row, body, lit upper row (rows, so it reads at any slope)."""
    for i in range(w):
        c = ramp[min(len(ramp) - 1, lit)] if i == 0 else ramp[1] if i == w - 1 else ramp[2]
        line(p, (a[0], a[1] + i), (b[0], b[1] + i), c)


def tube_tone(ramp: Ramp, t: float) -> Color:
    """Cylinder shading across a tube, t = -1 (lit upper-left side) .. +1 (shaded side)."""
    v = 3.6 - (t + 1) * 1.55 + 1.3 * math.exp(-((t + 0.45) / 0.18) ** 2)
    return ramp[max(0, min(len(ramp) - 1, round(v * (len(ramp) - 1) / 4)))]


def horn(p: Pix, a: Pt, b: Pt, r0: float, r1: float, k: float = 2.4, ramp: Ramp = BRASS, mouth_rx: float = 2.5,
         seam: bool = True, seed: int = 0) -> None:
    """A flared brass horn from a throat at `a` (radius r0) to a mouth at `b` (radius r1). The radius grows as
    r0 * (r1/r0) ** (t ** k)-like exponential flare; shaded across the axis like a cylinder; the mouth is an ellipse of
    half-width `mouth_rx` (along the axis) whose inside is dark with a lit lower rim."""
    ax, ay = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ax, ay)
    ux, uy = ax / ln, ay / ln
    nx, ny = uy, -ux                       # normal, pointing up/left for a rising horn
    if nx > 0 or (abs(nx) < 1e-6 and ny > 0):
        nx, ny = -nx, -ny
    prof = lambda t: r0 + (r1 - r0) * ((math.exp(k * t) - 1) / (math.exp(k) - 1))
    # silhouette polygon
    left, right = [], []
    for i in range(0, 41):
        t = i / 40
        r = prof(t)
        cx, cy = a[0] + ax * t, a[1] + ay * t
        left.append((cx + nx * r, cy + ny * r))
        right.append((cx - nx * r, cy - ny * r))
    poly = left + right[::-1]
    rng = fx._rng(p, seed + 5)
    def at(x: int, y: int) -> Color | None:
        dx, dy = x + 0.5 - a[0], y + 0.5 - a[1]
        t = (dx * ux + dy * uy) / ln
        t = max(0.0, min(1.0, t))
        r = prof(t)
        s = (dx * nx + dy * ny) / max(0.6, r)          # +1 on the lit side
        c = tube_tone(ramp, -s)
        # a long reflection streak that widens with the flare
        if 0.55 < s < 0.72 and t > 0.12:
            c = ramp[4]
        if seam and abs(s + 0.78) < 0.14 and 0.05 < t < 0.97 and int(t * 22) % 2 == 0 and r > 2.2:
            c = ramp[1]                                  # a riveted seam on the shaded side
        return c
    fill(p, poly, at)
    # outline
    for i in range(len(poly)):
        q = poly[(i + 1) % len(poly)]
        line(p, poly[i], q, ramp[0])
    # rim ellipse at the mouth, axis perpendicular to the horn
    ang = math.atan2(uy, ux)
    # rotate: ellipse major axis along the normal
    pts = []
    for i in range(32):
        th = 2 * math.pi * i / 32
        ex, ey = mouth_rx * math.cos(th), r1 * math.sin(th)
        pts.append((b[0] + ex * ux + ey * nx, b[1] + ex * uy + ey * ny))
    inner = []
    for i in range(32):
        th = 2 * math.pi * i / 32
        ex, ey = (mouth_rx - 0.9) * math.cos(th), (r1 - 1.3) * math.sin(th)
        inner.append((b[0] + ex * ux + ey * nx, b[1] + ex * uy + ey * ny))
    fill(p, pts, lambda x, y: ramp[3] if (x - b[0]) * nx + (y - b[1]) * ny > 0 else ramp[2])
    fill(p, inner, lambda x, y: ramp[0] if ((x - b[0]) * nx + (y - b[1]) * ny) < -r1 * 0.2 else ramp[1])
    for i in range(32):
        q = pts[(i + 1) % 32]
        line(p, pts[i], q, ramp[4] if (pts[i][0] + pts[i][1]) < (b[0] + b[1]) else ramp[1])
    _ = (ang, rng)


def drum(p: Pix, cx: int, cy: int, rx: int, h: int, side: Ramp, top: Ramp, ry: int | None = None, mouth: Color | None = None) -> None:
    """A short upright cylinder standing on a horizontal surface: its foot at row `cy` (front of the base ellipse)."""
    ry = ry if ry is not None else max(1, rx // 3)
    base_cy = cy - ry
    top_cy = base_cy - h
    for y in range(top_cy, base_cy + 1):
        for x in range(cx - rx, cx + rx + 1):
            t = (x - cx) / rx
            p.px(x, y, tube_tone(side, t))
    for x in range(cx - rx, cx + rx + 1):                     # the curved foot
        d = round(ry * math.sqrt(max(0.0, 1 - ((x - cx) / rx) ** 2)))
        for y in range(base_cy + 1, base_cy + d + 1):
            p.px(x, y, tube_tone(side, (x - cx) / rx))
        p.px(x, base_cy + d, side[0])
    p.ellipse(cx - rx, top_cy - ry, 2 * rx + 1, 2 * ry + 1, top[3])
    if mouth is not None:
        p.ellipse(cx - rx + 1, top_cy - ry + 1, 2 * rx - 1, max(1, 2 * ry - 1), mouth)


def shadow(p: Pix, shape: list[Pt], shift: Pt = (3, 1), spread: int = 3, strength: float = 0.9, alpha: int = 190) -> None:
    fx.contact_shadow(p, shape, shift=shift, spread=spread, strength=strength, alpha=alpha)


def clip_to(img: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img.crop(bbox), bbox[:2])
    return out


__all__ = ["Plane", "fill", "mask", "horn", "drum", "tone", "tube_tone", "line", "thick_line", "ri", "shadow", "clip_to",
           "BRASS", "IRON", "OAK", "PALE_WOOD", "PARCHMENT", "SHADOW", "WOOD", "mix", "Cuboid", "fx"]
