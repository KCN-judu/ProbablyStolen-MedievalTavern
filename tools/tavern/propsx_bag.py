"""`sleeping_bag.960x540.png`: a bedroll lying on the floor boards under the bar's right wing.

A straw mat rolled round a wine-red blanket, bound with two leather straps and a brass buckle, with a small linen
pillow tucked under its side. The roll lies along the floor toward the vanishing point of the boards (the same one the
rest of the shop uses), so its near end is an ellipse that faces the viewer, and every strap is an arc that bulges
the way a ring on a cylinder does. The picture keeps to the outline the game's original filled (layout.tsv).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from palette import BRASS, LEATHER, LINEN, MOSS, PALE_WOOD, PARCHMENT, SHADOW, WINE
from pix import Pix, mix
from shopx_persp import VP, overlay_shadow, stepped

W, H = 960, 540
# where the original's picture was opaque (a polygon that bounds it): the new one stays inside
ALLOWED = [(803, 458), (846, 518), (851, 540), (960, 540), (960, 440), (944, 400), (870, 395)]

NEAR = (922, 508)                 # centre of the near end of the roll
LENGTH = 62                       # along the axis, screen pixels
R0, R1 = 19.0, 15.5               # radius at the near and far end (the far end is smaller)
FLAT = 0.5                        # how round the end ellipse is: minor radius / major radius

# straw, from dark to light
STRAW = [mix(PALE_WOOD[0][:3], SHADOW[:3], 0.3), PALE_WOOD[1], PALE_WOOD[2],
         mix(PALE_WOOD[3][:3], PARCHMENT[2][:3], 0.35), mix(PALE_WOOD[4][:3], PARCHMENT[3][:3], 0.45)]


def noise(x: int, y: int, s: int = 0) -> float:
    """A repeatable 0..1 value per pixel."""
    n = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791)
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535


def smooth(x: float, y: float, s: int) -> float:
    """Value noise on a 4-pixel grid, for lumps."""
    x0, y0 = math.floor(x / 4), math.floor(y / 4)
    fx, fy = x / 4 - x0, y / 4 - y0
    a, b = noise(x0, y0, s), noise(x0 + 1, y0, s)
    c, d = noise(x0, y0 + 1, s), noise(x0 + 1, y0 + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def frame() -> tuple[float, float, float, float]:
    """The unit vector of the axis (from the near end toward VP) and its perpendicular (toward the upper right)."""
    dx, dy = VP[0] - NEAR[0], VP[1] - NEAR[1]
    n = math.hypot(dx, dy)
    ax, ay = dx / n, dy / n
    return ax, ay, -ay, ax


AX, AY, PX, PY = frame()


def to_roll(x: float, y: float) -> tuple[float, float]:
    """A pixel centre in the roll's frame: u along the axis (0 at the near end), v across it (upper right positive)."""
    rx, ry = x - NEAR[0], y - NEAR[1]
    return rx * AX + ry * AY, rx * PX + ry * PY


def radius(u: float) -> float:
    return R0 + (R1 - R0) * max(0.0, min(1.0, u / LENGTH))


def light(t: float) -> float:
    """Brightness 0..1 for a point on the roll's cross-section at `t` (-1 lower left, +1 upper right): the top and the left
    catch the lamp, the upper right side turns away."""
    c = math.sqrt(max(0.0, 1 - t * t))
    return max(0.0, min(1.0, 0.16 + 0.52 * c - 0.3 * t))


def ramp_pick(ramp, v: float, x: int, y: int):
    """A colour of a dark-to-light ramp for a value 0..1, grained at the joints between tones."""
    k = v * (len(ramp) - 1)
    i = int(k)
    if i < len(ramp) - 1 and stepped(k - i, x, y):
        i += 1
    return ramp[max(0, min(len(ramp) - 1, i))]


def body_pixel(x: int, y: int) -> tuple[int, int, int] | None:
    """The colour of the roll's side at a pixel, or None if the pixel is not on it."""
    u, v = to_roll(x + 0.5, y + 0.5)
    r = radius(u)
    t = v / r
    if abs(t) >= 1:
        return None
    c = math.sqrt(1 - t * t)
    e = FLAT * r
    u_ring = u - e * c                          # the position of this pixel measured along the ring it lies on
    if u_ring < -0.5 or u_ring > LENGTH:
        return None
    lit = light(t)
    lit += 0.22 * (smooth(x, y, 3) - 0.5) + 0.08 * (smooth(u * 1.3, v * 0.8, 7) - 0.5)       # lumps
    # folds: dark creases that run round the roll (arcs), each with a lit lip on its near side
    for crease, wob, amp in ((6.0, 1, 0.22), (23.0, 2, 0.35), (29.0, 5, 0.2), (36.0, 3, 0.3), (52.0, 4, 0.35), (57.0, 6, 0.2)):
        cu = crease + 2.5 * (smooth(v * 0.5, 0, wob) - 0.5) * 3
        d = u_ring - cu
        span = noise(int(crease), 0, wob) * 0.4
        if abs(t) < 0.92 - span:
            if 0 <= d < 1.6:
                lit -= amp
            elif -1.6 <= d < 0:
                lit += amp * 0.6
    # straps
    for su in (13.0, 43.0):
        d = u_ring - su
        if -0.5 <= d < 4.5:
            sl = lit * 0.9 + 0.05
            lc = LEATHER[0] if d >= 3.5 else LEATHER[1] if d < 0.5 or sl < 0.35 else LEATHER[2] if sl < 0.7 else LEATHER[3]
            if d < 0.5 and sl > 0.5:
                lc = LEATHER[3]
            if 1.5 <= d < 2.5 and noise(x, y, 4) < 0.2:
                lc = LEATHER[min(3, LEATHER.index(lc) + 1)]
            return lc[:3]
        if 4.5 <= d < 6.5 and stepped(0.5 - (d - 4.5) * 0.25, x, y):      # the strap's shade on the mat
            lit -= 0.28
    # straw: stalks run along the axis, so the grain is made of short dashes in v
    stalk = noise(int(v * 0.9 + 40), int(u_ring // 7), 11)
    grain = 0.12 if stalk > 0.82 else -0.12 if stalk < 0.18 else 0.0
    weave = -0.07 if int(u_ring) % 3 == 0 and noise(x, y, 8) > 0.45 else 0.0
    lit += grain + weave
    if noise(x, y, 12) > 0.96:
        lit += 0.18
    # the far end: the mat's cut edge frays
    if u_ring > LENGTH - 2.5:
        lit -= 0.25
    return ramp_pick(STRAW, max(0.0, min(1.0, lit - 0.06)), x, y)[:3]


def cap_pixel(x: int, y: int) -> tuple[int, int, int] | None:
    """The colour of the near end (a spiral of straw and wine-red wool inside an ellipse), or None outside it."""
    u, v = to_roll(x + 0.5, y + 0.5)
    r = R0
    e = FLAT * r
    a, b = u / e, v / r
    rho = math.hypot(a, b)
    if rho >= 1.0:
        return None
    phi = math.atan2(a, b)
    # the outer straw layer, a thin lit rim, then the wool wound round and round
    t = max(-1.0, min(1.0, b))
    lit = 0.35 + 0.3 * (0.5 - 0.5 * t) + 0.25 * (-a * 0.5)
    if rho > 0.86:
        edge_lit = 0.9 if (a < 0.2 and b < 0.35) else 0.55
        return ramp_pick(STRAW, edge_lit - (0.35 if rho > 0.95 else 0.0) + 0.1 * (noise(x, y, 2) - 0.5), x, y)[:3]
    s = (rho * 3.3 + phi / (2 * math.pi) * 1.0) % 1.0
    wob = noise(x // 2, y // 2, 6) * 0.06
    s = (s + wob) % 1.0
    if s < 0.52:
        base = WINE
        k = lit + 0.1 * (noise(x, y, 5) - 0.5)
        return ramp_pick(base, max(0.0, min(1.0, k - 0.1)), x, y)[:3]
    if s < 0.62:
        return WINE[0][:3]
    return ramp_pick(STRAW, max(0.0, min(1.0, lit + 0.1)), x, y)[:3]


def buckle(p: Pix) -> None:
    """A brass buckle on the near strap, on the lit face of the roll, with the strap's tongue through it."""
    su = 13.0
    t = -0.38
    r = radius(su)
    c = math.sqrt(1 - t * t)
    u = su + 2 + FLAT * r * c
    x = NEAR[0] + AX * u + PX * t * r
    y = NEAR[1] + AY * u + PY * t * r
    x, y = round(x), round(y)
    p.rect(x - 4, y - 4, 9, 8, BRASS[0])
    p.rect(x - 3, y - 3, 7, 6, BRASS[3])
    p.rect(x - 1, y - 2, 3, 4, LEATHER[1])           # the strap shows through the frame
    p.hline(x - 3, y - 3, 7, BRASS[4])
    p.vline(x - 3, y - 3, 6, BRASS[4])
    p.hline(x - 3, y + 2, 7, BRASS[1])
    p.vline(x + 3, y - 3, 6, BRASS[2])
    p.px(x, y - 3, BRASS[2])
    p.hline(x - 1, y, 5, BRASS[4])                   # the tongue
    p.px(x + 4, y, BRASS[2])


def pillow(p: Pix, cx: int, cy: int, rx: int, ry: int) -> None:
    """A folded moss-green wool blanket on the boards: two layers, a lit top fold, striped ends, a shaded underside."""
    for layer, (lx, ly, lrx, lry) in enumerate(((cx, cy, rx, ry), (cx - 2, cy - 4, rx - 4, ry - 3))):
        for y in range(ly - lry - 2, ly + lry + 3):
            for x in range(lx - lrx - 2, lx + lrx + 3):
                a, b = (x - lx) / lrx, (y - ly) / lry
                d = abs(a) ** 3.0 + abs(b) ** 2.2
                if d >= 1.0:
                    continue
                lit = 0.3 + 0.32 * math.sqrt(1 - d) - 0.16 * a - 0.26 * b + 0.12 * (smooth(x, y, 21) - 0.5)
                if b > 0.55:
                    lit -= 0.18                                  # the rolled edge turns down into shade
                if abs(a) > 0.7 and int(a * 40 + 100) % 7 in (0, 1):
                    p.px(x, y, ramp_pick(WINE if layer == 0 else LINEN, 0.35 + 0.3 * max(0.0, lit), x, y))
                    continue
                if abs(b) < 0.14 and abs(a) < 0.8 and noise(x, y, 33) < 0.5:
                    lit -= 0.12                                  # a fold line
                p.px(x, y, ramp_pick(MOSS, max(0.0, min(1.0, lit)), x, y))
    for layer_y, lx, lrx, lry in ((cy, cx, rx, ry), (cy - 4, cx - 2, rx - 4, ry - 3)):
        for x in range(lx - lrx, lx + lrx + 1):
            a = (x - lx) / lrx
            if abs(a) < 1:
                yb = layer_y + round(lry * (1 - abs(a) ** 3.0) ** (1 / 2.2))
                yt = layer_y - round(lry * (1 - abs(a) ** 3.0) ** (1 / 2.2))
                p.px(x, yb, MOSS[0])
                p.px(x, yt, MOSS[3] if a < 0.3 else MOSS[2])


def shadow_on_floor(p: Pix) -> None:
    """The roll's contact shadow on the boards: a long soft ellipse that falls to the lower right, away from the lamp."""
    mid = LENGTH / 2

    def fn(x: int, y: int) -> float:
        u, v = to_roll(x + 0.5 - 5, y + 0.5 - 11)
        d = math.hypot((u - mid) / (mid + 17), v / (R0 + 6))
        return 1.7 * (1 - d) ** 0.55 if d < 1 else 0.0

    overlay_shadow(p, 800, 440, 960, 540, fn, alpha=250)


def sleeping_bag() -> Image.Image:
    p = Pix(W, H, seed=61)
    shadow_on_floor(p)
    pillow(p, 882, 525, 24, 9)
    # the roll: far parts first so the near end covers the body
    for y in range(400, 540):
        for x in range(800, 960):
            c = body_pixel(x, y)
            if c is not None:
                p.px(x, y, c)
    for y in range(400, 540):
        for x in range(800, 960):
            c = cap_pixel(x, y)
            if c is not None:
                p.px(x, y, c)
    rim_pass(p)
    buckle(p)
    p.clip(ALLOWED)
    return p.finish()


def rim_pass(p: Pix) -> None:
    """A one-pixel dark contour round the roll where it meets the boards or the wall, lighter on the lit side."""
    mask = Image.new("L", (W, H), 0)
    for y in range(400, 540):
        for x in range(800, 960):
            if body_pixel(x, y) is not None or cap_pixel(x, y) is not None:
                mask.putpixel((x, y), 255)
    for y in range(401, 539):
        for x in range(801, 959):
            if mask.getpixel((x, y)):
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if mask.getpixel((x + dx, y + dy)):
                    p.px(x, y, (*mix(SHADOW[:3], WINE[0][:3], 0.3), 255))
                    break


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "sleeping_bag.960x540.png": sleeping_bag,
}
