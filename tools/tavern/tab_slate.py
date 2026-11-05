"""`negociation_tablet` (bbox 649,177-779,288): the bargaining board of the tavern.

The game's negotiation tablet is a screen on which customer and shopkeeper agree a price. The tavern's version of that
job is a counting board: a thick oak slab lying on the bar, with a slate let into a brass frame (the price is chalked
there and wiped with a thumb), a tally groove along the near edge in which each party slides a bone peg to show an offer,
an iron-strapped hinge side with a leather loop, a brass thumb-catch on the front and a lead stylus on a thin chain.
Drawn on the shop's single viewpoint: the top is foreshortened toward VP, the left end shows its thickness.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

import fxkit as fx
from palette import BRASS, IRON, LEATHER, OAK, PALE_WOOD, SHADOW, STONE, WOOD, PARCHMENT, NAVY, LINEN
from pix import Pix
from propsy_fx import Cuboid

BBOX = (649, 177, 779, 288)
SL = ((34, 38, 50), (58, 64, 78), (84, 92, 106), (112, 120, 132), (168, 172, 176))   # blue-grey slate, chalk last
BOX = Cuboid(x0=679, x1=774, y_top=279, h=9, s_far=0.855)
# slab coordinates: u 0 near .. 1 far, x is the near-edge x


def P(u: float, x: float, up: float = 0.0) -> tuple[int, int]:
    a, b = BOX.top_pt(u, x, up)
    return round(a), round(b)


def quad(u0: float, x0: float, u1: float, x1: float, up: float = 0.0) -> list[tuple[int, int]]:
    return [P(u0, x0, up), P(u0, x1, up), P(u1, x1, up), P(u1, x0, up)]


def draw() -> Image.Image:
    p = Pix(960, 540, seed=73)
    # contact shadow on the bar, longer toward the lower right
    fx.contact_shadow(p, BOX.footprint(), shift=(3, 1), spread=3, strength=0.95, alpha=210)
    fx.wood_box(p, BOX, ramp=WOOD, seed=7, top_light=0.9, front_light=0.3, end_light=-0.1, knots=1.2, wear_amount=0.5)
    # lit edges: near top lip and left end
    for x in range(BOX.x0 + 1, BOX.x1):
        p.px(x, BOX.y_top, PALE_WOOD[4] if x % 5 else PALE_WOOD[3])
    a, b = P(0, BOX.x0), P(1, BOX.x0)
    p.line(a[0], a[1], b[0], b[1], PALE_WOOD[3])
    p.line(BOX.x1, BOX.y_top + 1, BOX.x1, BOX.y_top + 7, WOOD[0])
    for x in range(BOX.x0 + 1, BOX.x1):
        p.px(x, BOX.y_top + 7, SHADOW)

    # --- recessed slate in a brass frame
    outer = quad(0.34, 697, 0.84, 770)
    fx.brass_fill(p, outer, profile="plate", tarnish=0.6, light=0.7, seed=3)
    inner = quad(0.40, 700, 0.79, 766)
    reg = fx.region(p, inner)
    for x, y in reg.pixels():
        u, xn = BOX.top_uv(x, y)
        n = fx.vnoise(x / 6, y / 2, 5) * 0.8 + fx.vnoise(x / 2, y / 1, 9) * 0.4
        v = 1.7 + n * 1.2 - max(0.0, u - 0.62) * 2.0 + (0.5 if xn < 708 else 0)
        p.px(x, y, fx.pick_tone(SL, v, x, y))
    # inner shadow under the far frame and left, wiped chalk smears
    for x, y in reg.pixels():
        u, xn = BOX.top_uv(x, y)
        if u > 0.71 or xn < 703:
            p.px(x, y, SL[0] if u > 0.75 else SL[1])
    for k, (u, xa, xb) in enumerate(((0.55, 708, 726), (0.64, 738, 754), (0.50, 728, 744))):
        for xx in range(xa, xb):
            if (xx * 7 + k) % 3:
                q = P(u + (xx % 3) * 0.02, xx)
                p.px(q[0], q[1], SL[4] if k != 1 else SL[3])

    # --- tally groove with bone pegs along the near edge
    groove = quad(0.09, 689, 0.27, 767)
    fx.wood_fill(p, groove, ramp=OAK, board=4, knots=0, joints=False, nails=False, bias=-1.8, seed=11)
    for x in range(690, 766):
        q = P(0.10, x)
        p.px(q[0], q[1], PALE_WOOD[2])
    for tick in range(0, 12):                    # tally notches on the lip between groove and slate
        q = P(0.33, 691 + tick * 6.4)
        p.px(q[0], q[1], WOOD[0])
    for xn, shade in ((708, 0), (736, 1), (754, 0)):
        bx, by = P(0.20, xn)
        p.rect(bx - 1, by - 4, 3, 5, LINEN[3] if not shade else LINEN[2])
        p.vline(bx + 1, by - 4, 5, LINEN[1])
        p.hline(bx - 1, by - 5, 3, PARCHMENT[4])
        p.hline(bx - 1, by + 1, 4, SHADOW)

    # --- hinge side (far edge): two iron straps with brass rivets, and a leather loop
    for xn in (706, 754):
        q = quad(0.80, xn - 4, 0.998, xn + 4)
        fx.iron_fill(p, q, hammer=0.4, rust=0.2, light=0.6, seed=xn)
        r = P(0.88, xn)
        fx.rivet(p, r[0], r[1], r=1)
    # brass corners at the near corners
    for xn, sgn in ((BOX.x0, 1), (BOX.x1, -1)):
        x, y = P(0, xn)
        q = [(x, y), (x + sgn * 7, y), (x + sgn * 7, y + 3), (x, y + 6)] if sgn > 0 else [(x, y), (x - 7, y), (x - 7, y + 3), (x, y + 6)]
        fx.brass_fill(p, q, profile="plate", tarnish=0.4, seed=xn)
    # thumb-catch on the front: brass plate with a horn button
    cx = (BOX.x0 + BOX.x1) // 2
    fx.brass_fill(p, (cx - 5, BOX.y_top + 2, 10, 5), profile="plate", tarnish=0.3, seed=21)
    fx.rivet(p, cx, BOX.y_top + 4, r=1, ramp=PALE_WOOD)
    # leather strap loop on the front-right
    sx = BOX.x1 - 12
    fx.wood_fill(p, (sx, BOX.y_top + 1, 4, 7), ramp=LEATHER, grain_dir="v", knots=0, joints=False, nails=False, board=4, seed=4)
    fx.rivet(p, sx + 2, BOX.y_top + 3, r=1)

    # --- lead stylus on a thin chain, lying on the bar-side of the slate
    top = P(0.93, 770)
    fx.rivet(p, top[0], top[1], r=1, ramp=IRON)
    chain_pts = fx.hang_curve((float(top[0]), float(top[1])), (float(P(0.62, 761)[0]), float(P(0.62, 761)[1])), 3)
    fx.chain(p, chain_pts, link=3, ramp=IRON, shadow=False)
    s0, s1 = P(0.62, 761), P(0.48, 738)
    p.line(s0[0] + 1, s0[1] + 1, s1[0] + 1, s1[1] + 1, SHADOW)
    p.line(s0[0], s0[1], s1[0], s1[1], IRON[4])
    p.px(s1[0], s1[1], IRON[2])
    p.px(s0[0], s0[1], NAVY[1])
    fx.wear(p, BOX.footprint() and quad(0, BOX.x0, 1, BOX.x1), amount=0.2)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (2, 1)):      # an ink blot beside the notches
        q = P(0.30, 746 + dx)
        p.px(q[0], q[1] + dy - 1, NAVY[0])
    out = p.finish()
    keep = Image.new("L", out.size, 0)
    keep.paste(255, BBOX)
    out.putalpha(Image.composite(out.getchannel("A"), keep, keep))
    return out


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"negociation_tablet.960x540.png": draw}
