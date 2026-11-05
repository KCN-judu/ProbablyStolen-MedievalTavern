"""`desk animations1-4`: small natural motion on the counter's right wing, replacing the game's key-press strips.

  animations1 (40x29, 9 frames)  a tally stand: two posts and a bar on a foot, a knotted tally cord with a brass weight
                                 swinging like a slow pendulum in the draught
  animations2 (20x15, 8 frames)  an iron inkpot with a quill stirring in it
  animations3 (20x15, 9 frames)  a candle in a brass dish: the flame flickers, a pool of light dithers on the planks
  animations4 (49x15, 9 frames)  two loose letters on the counter; the far corner of the upper one lifts in the draught and settles

Every thing stands or lies on the wing with a contact shadow. Each cell is drawn on its own canvas with the shop's vanishing
point moved into cell coordinates. All loops are periodic in the frame count.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from ctr_kit import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD, fill, fx, line, mix
from palette import FLAME, LEATHER, LINEN, WINE
from pix import Color, Pix
from props import sheet

VPX, VPY = 480.0, 150.0


def ground(ox: int, oy: int, y0: float) -> Callable[[float, float, float], tuple[float, float]]:
    """Cell point for near-edge x `x`, `z` rows behind the foot row `y0`, `up` px above the plane (perspective by the VP)."""
    vx, vy = VPX - ox, VPY - oy

    def g(x: float, z: float, up: float = 0.0) -> tuple[float, float]:
        y = y0 - z
        s = (y - vy) / (y0 - vy)
        return vx + (x - vx) * s, y - up * s
    return g


# ------------------------------------------------------------------------------------------------ 1: tally stand


def tally(p: Pix, k: int) -> None:
    """Cell 40x29 (content 4..40 x 3..25). Foot row 24. Light upper left; the cord swings through +-3 px."""
    g = ground(920, 342, 24)
    sw = math.sin(2 * math.pi * k / 9)
    # foot plank (flat slab) and its shadow
    foot = [g(8, 0), g(37, 0), g(37, 5), g(8, 5)]
    fx.contact_shadow(p, [g(9, -1), g(40, -1), g(40, 5), g(9, 5)], shift=(4, 1), spread=3, strength=0.95, alpha=190)
    fill(p, foot, lambda x, y: PALE_WOOD[4] if y <= foot[2][1] + 0.5 else WOOD[3])
    p.hline(round(foot[0][0]), round(foot[0][1]) + 1, round(foot[1][0] - foot[0][0]), WOOD[2])
    p.hline(round(foot[0][0]) - 1, round(foot[0][1]) + 2, round(foot[1][0] - foot[0][0]) + 1, OAK[0])
    fx.wood_fill(p, (9, 22, 28, 2), "h", WOOD, seed=2, knots=0, joints=False, nails=False, scratches=0.5, wear_amount=0.1)
    # two posts with a bar
    for px in (11, 33):
        fx.wood_fill(p, (px, 6, 3, 17), "v", WOOD, seed=px, knots=0, joints=False, nails=False, wear_amount=0.1)
        p.px(px + 3, 22, SHADOW)
    fx.wood_fill(p, (10, 4, 27, 3), "h", WOOD, bias=0.5, seed=5, knots=0, joints=False, nails=False, wear_amount=0.1)
    p.hline(10, 3, 27, PALE_WOOD[4])
    for px in (13, 34):                                    # iron pegs through the bar
        fx.rivet(p, px, 5, 1, IRON)
    # the tally cord: hangs from a hook at the middle of the bar; knots and a brass weight swing as a pendulum
    hx, hy, ln = 24, 7, 14
    ang = 0.26 * sw
    pts = []
    for i in range(0, ln + 1):
        t = i / ln
        pts.append((hx + math.sin(ang) * i - (1 - math.cos(ang)) * 0, hy + math.cos(ang) * i))
    ex, ey = pts[-1]
    sh = ex + 2 + 3 * sw * 0, 0
    for i, (x, y) in enumerate(pts):
        p.px(round(x) + 1, round(y) + 1, (30, 20, 22, 150))
        c = LINEN[3] if i % 4 else LEATHER[3]
        p.px(round(x), round(y), c)
        if i % 4 == 3:
            p.px(round(x) + 1, round(y), LEATHER[2])      # a tally knot
            p.px(round(x), round(y) - 1, LEATHER[3])
    wx, wy = round(ex), round(ey)
    p.rect(wx - 2, wy + 1, 5, 5, BRASS[3])
    p.vline(wx - 2, wy + 1, 5, BRASS[4])
    p.vline(wx + 2, wy + 1, 5, BRASS[1])
    p.hline(wx - 2, wy + 5, 5, BRASS[0])
    p.px(wx - 1, wy + 2, BRASS[4])
    p.px(wx, wy, IRON[3])
    # its shadow on the counter: slides with the swing
    for dx in range(-2, 3):
        fx.over(p, round(ex) + 6 + dx + round(2 * sw), 25, SHADOW, 110)
    p.px(hx, hy - 1, IRON[4])
    p.px(hx, hy, IRON[3])
    _ = sh


def tally_frame(cell: Pix, k: int) -> None:
    """The 36x22 cell is the part (4,3) of a 40x29 canvas, so the stand is drawn in the game's full-cell coordinates."""
    big = Pix(40, 29, seed=cell.rng.randrange(1 << 20))
    tally(big, k)
    cell.paste(big.finish().crop((4, 3, 40, 25)), 0, 0)


# ------------------------------------------------------------------------------------------------ 2: inkpot and quill


def inkpot(p: Pix, k: int) -> None:
    """Cell 20x15 at (881,348). An iron pot standing on the counter; the quill's top circles slowly (stirring)."""
    cx, foot = 9, 13
    fx.contact_shadow(p, fx.ellipse(cx + 4, foot - 1, 8, 2.5), shift=(2, 1), spread=3, strength=0.95, alpha=190)
    # pot body: a squat drum, lit left, dark right, with a wide mouth ellipse
    for y in range(7, foot):
        for x in range(cx - 5, cx + 6):
            t = (x - cx) / 5
            c = IRON[4] if -0.8 < t < -0.5 else IRON[3] if t < -0.1 else IRON[2] if t < 0.45 else IRON[1]
            if y > foot - 3 and t > 0.2:
                c = IRON[0]
            p.px(x, y, c)
    for x in range(cx - 5, cx + 6):
        p.px(x, foot, IRON[0])
    p.ellipse(cx - 6, 5, 13, 5, IRON[3])                      # the rim
    p.ellipse(cx - 5, 6, 11, 3, (14, 10, 22))                 # ink
    p.px(cx - 3, 7, (60, 70, 110))                            # a glint on the ink
    p.hline(cx - 5, 5, 6, IRON[4])
    # the quill: base in the ink, top swings round a small circle
    a = 2 * math.pi * k / 8
    tx, ty = cx + 3 + 2.2 * math.cos(a), 0.5 + 1.2 * math.sin(a)
    bx, by = cx, 7
    for i in range(0, 15):
        t = i / 14
        x, y = bx + (tx - bx) * t, by + (ty - by) * t
        p.px(round(x), round(y), PARCHMENT[4] if i > 3 else PARCHMENT[2])
        if i > 6:
            p.px(round(x) + 1, round(y) + 1, PARCHMENT[3])
            if i > 8:
                p.px(round(x) - 1, round(y), PARCHMENT[2])
    p.px(round(tx) + 1, round(ty), PARCHMENT[3])
    # a ring of ripples on the ink, which move with the stirring
    p.px(cx - 2 + round(math.sin(a)), 7, (50, 56, 90))


# ------------------------------------------------------------------------------------------------ 3: candle


FLICKER = (
    (0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 1), (-1, 1, 0), (-1, 0, 0), (0, -1, 1), (1, -1, 1), (0, 0, 1),
)


def candle(p: Pix, k: int) -> None:
    """Cell 20x15 at (901,348). A brass dish with a tallow candle: the flame sways, the light pool on the planks pulses."""
    cx, foot = 8, 13
    dx, dy, dh = FLICKER[k % 9]
    pulse = 0.5 + 0.12 * math.sin(2 * math.pi * k / 9)
    p.glow(cx + 2, foot, 8, mix(FLAME[3][:3], FLAME[2][:3], 0.5) + (110,), pulse * 0.8) if False else None
    for yy in range(8, 15):
        for xx in range(cx - 9, cx + 10):
            d = math.hypot((xx - cx) / 9, (yy - foot) / 3.2)
            if d < 1 and fx.noise(xx, yy, 5) < (1 - d) * pulse * 1.2:
                fx.over(p, xx, yy, FLAME[2], 60)
    fx.contact_shadow(p, fx.ellipse(cx + 3, foot, 7, 2), shift=(3, 0), spread=2, strength=0.9, alpha=190)
    # dish: a brass saucer (ellipse, thickness below the near rim)
    p.ellipse(cx - 5, foot - 3, 11, 4, BRASS[0])
    p.ellipse(cx - 5, foot - 4, 11, 4, BRASS[3])
    p.ellipse(cx - 3, foot - 3, 7, 2, BRASS[1])
    p.hline(cx - 3, foot - 4, 3, BRASS[4])
    # candle stub with drips
    p.rect(cx - 1, foot - 10, 4, 7, PARCHMENT[3])
    p.vline(cx - 1, foot - 10, 7, PARCHMENT[4])
    p.vline(cx + 2, foot - 10, 7, PARCHMENT[1])
    p.px(cx + 1, foot - 6, PARCHMENT[4])
    p.px(cx, foot - 5, PARCHMENT[4])
    p.hline(cx - 1, foot - 11, 4, PARCHMENT[2])
    p.px(cx, foot - 11, PARCHMENT[0])                         # wick
    # flame: teardrop that leans and stretches by frame
    fx_, fy_ = cx + 1 + dx, foot - 12
    h = 5 + dh
    for i in range(h):
        w = 0 if i == 0 else 1 if i < h - 2 else 0
        lean = round(dx * (h - i) / h)
        for xx in range(-w, w + 1):
            c = FLAME[1] if abs(xx) == w and w else FLAME[3] if i > h - 3 else FLAME[2]
            p.px(fx_ + xx + lean - (0 if i else 0), fy_ - i + (0), c)
    p.px(fx_, fy_ - 1, FLAME[4])
    p.px(fx_, fy_, FLAME[4])
    # a dust mote drifting in the light
    mx = (cx + 6 + (k * 2) % 9) % 20
    p.px(mx, 3 + (k % 3), FLAME[4])


# ------------------------------------------------------------------------------------------------ 4: loose letters


def letters(p: Pix, k: int) -> None:
    """Cell 49x15 at (828,356). Two letters lie on the counter; a draught lifts the upper one's far-right corner."""
    g = ground(828, 356, 11)
    lift = 2.6 * (0.5 - 0.5 * math.cos(2 * math.pi * k / 9)) ** 1.3

    def sheet_poly(x0: float, x1: float, z0: float, z1: float, rot: float, corner: float = 0.0):
        zc = (z0 + z1) / 2
        xc = (x0 + x1) / 2
        out = []
        for i, (x, z) in enumerate(((x0, z0), (x1, z0), (x1, z1), (x0, z1))):
            zz = zc + (z - zc) + (x - xc) * rot
            out.append(g(x, zz, corner if i == 2 else 0.0))
        return out
    under = sheet_poly(30, 44, 0.5, 6.5, -0.06)
    over_ = sheet_poly(34, 48, 2.0, 8.5, 0.05, lift)
    flat_over = sheet_poly(34, 48, 2.0, 8.5, 0.05)
    # shadows on the counter
    fx.contact_shadow(p, [(x + 1, y + 1) for x, y in under], shift=(1, 1), spread=2, strength=0.8, alpha=170)
    fill(p, under, lambda x, y: PARCHMENT[2] if (x * 3 + y) % 7 else PARCHMENT[1])
    for i in (0, 2, 4):
        a, b = g(32 + i * 0.5, 2.0 + i * 1.0), g(41, 2.2 + i * 1.0)
        line(p, a, b, PARCHMENT[0])
    line(p, under[0], under[1], PARCHMENT[4])
    line(p, under[0], under[3], PARCHMENT[3])
    line(p, under[2], under[3], PARCHMENT[0])
    # the upper letter's shadow, wider while the corner is lifted
    sh = [(x + 2 + lift, y + 1 + lift * 0.8) for x, y in flat_over]
    fx.contact_shadow(p, sh, shift=(1, 1), spread=2, strength=0.8, alpha=170)
    fill(p, over_, lambda x, y: PARCHMENT[4] if (x * 5 + y * 3) % 11 else PARCHMENT[3])
    for i in range(3):
        a, b = g(37, 3.2 + i * 1.6), g(46 - i * 2, 3.4 + i * 1.6)
        line(p, a, b, PARCHMENT[1])
    line(p, over_[0], over_[1], PARCHMENT[4])
    line(p, over_[1], over_[2], PARCHMENT[2])
    line(p, over_[2], over_[3], PARCHMENT[1])
    line(p, over_[0], over_[3], PARCHMENT[4])
    # the lifted corner: its turned-up underside is a lighter triangle that grows with the lift
    if lift > 0.4:
        c, d, e = over_[2], g(48 - 3, 8.5, lift * 0.7), g(48, 8.5 - 2, lift * 0.7)
        fill(p, [c, d, e], lambda x, y: PARCHMENT[2])
    # a red wax seal on the lower letter
    sx, sy = g(32, 3.2)
    p.ellipse(round(sx) - 1, round(sy) - 1, 4, 2, WINE[2])
    p.px(round(sx), round(sy) - 1, WINE[4])


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "desk animations1.360x29.png": lambda: sheet((360, 29), 9, 4, 40, 3, 36, 22, tally_frame, 27),
    "desk animations2.160x15.png": lambda: sheet((160, 15), 8, 0, 20, 0, 20, 15, inkpot, 28),
    "desk animations3.180x15.png": lambda: sheet((180, 15), 9, 0, 20, 0, 20, 15, candle, 29),
    "desk animations4.441x15.png": lambda: sheet((441, 15), 9, 0, 49, 0, 49, 15, letters, 30),
}
