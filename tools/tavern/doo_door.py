"""The street door seen edge-on at the left of the shop, and its chained padlock (`door`, `door lock`).

The door is a plane that recedes to VP: boards stay upright, every horizontal line on it (battens, straps, the hatch,
the foot of the door) runs to VP.  A point on the floor at sideways offset d from the door plane and depth scale s
(1 = the near end, falling to 0 at VP) is at x = 480 + (d - 480) s, y = 150 + (floor - 150) s; the threshold stone and
its shadow are drawn from that.  Material comes from fxkit (oak boards, forged iron, brass, stone).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

from fxkit import brass_fill, chain, contact_shadow, iron_fill, rivet, wear, wood_fill
from palette import BRASS, FLAME, IRON, MOSS, OAK, SHADOW, STONE, WOOD
from pix import Pix, mix
from shopx_persp import VP, blend, stepped

W, H = 960, 540
FLOOR_NEAR = 545                  # the floor line of the door at the left edge of the picture
DOOR_X, JAMB_X = 52, 60           # the door boards end at 52, the jamb stands from 52 to 60
JAMB_FOOT = round(VP[1] + (FLOOR_NEAR - VP[1]) * (VP[0] - DOOR_X) / VP[0])


def toward(y0: float, x: float) -> float:
    """Height at column x of a line on the door plane that is at y0 at the left edge."""
    return y0 + (VP[1] - y0) * x / VP[0]


def foot(x: float) -> int:
    return round(toward(FLOOR_NEAR, x))


def band(x0: int, x1: int, y0: float, h0: float, h1: float) -> list[tuple[int, int]]:
    """A strip on the door plane: top at y0 at the left edge, `h0` tall there and `h1` tall at x1; both edges run to VP."""
    top = [(x, round(toward(y0, x))) for x in range(x0, x1 + 1)]
    bot = [(x, round(toward(y0 + h0, x) + (h1 - h0) * (x - x0) / max(1, x1 - x0) * 0)) for x in range(x1, x0 - 1, -1)]
    return top + bot


def hinge_strap(p: Pix, y0: float, seed: int) -> None:
    """A wrought strap hinge: a flat bar on a batten, nailed with rivets, tapering to a pointed tail at the left,
    ending in a rolled eye round the pin at the jamb."""
    # the batten under the strap: a plank nailed across the boards
    bat = band(0, DOOR_X, y0 - 5, 22, 22)
    contact_shadow(p, bat, shift=(2, 4), spread=4, strength=0.9, alpha=200)
    wood_fill(p, bat, grain_dir="h", ramp=OAK, board=22, joints=False, nails=False, knots=0.4, wear_amount=0.5, seed=seed)
    for x in range(0, DOOR_X + 1):                                  # lit top edge, dark underside
        yt = round(toward(y0 - 5, x))
        p.px(x, yt, OAK[4])
        p.px(x, yt + 21 + round((toward(y0 - 5, x) - toward(y0 - 5, 0)) * 0.0), OAK[0])
    strap = [(x, round(toward(y0, x))) for x in range(0, DOOR_X - 1)]
    thick = [7 + (x * 5) // DOOR_X for x in range(0, DOOR_X - 1)]
    poly = strap + [(x, y + t) for (x, y), t in reversed(list(zip(strap, thick)))]
    contact_shadow(p, poly, shift=(1, 3), spread=3, strength=1.0, alpha=230)
    iron_fill(p, poly, hammer=0.7, rust=0.35, rivets=0, seed=seed + 1)
    for x in range(8, DOOR_X - 8, 11):                              # brass-headed nails along the strap
        t = 7 + (x * 5) // DOOR_X
        rivet(p, x, round(toward(y0, x)) + t // 2, 1, BRASS)
    # the rolled eye round the hinge pin
    ey = round(toward(y0, DOOR_X)) + 6
    p.ellipse(DOOR_X - 8, ey - 7, 16, 15, IRON[0])
    p.ellipse(DOOR_X - 7, ey - 6, 14, 13, IRON[3])
    p.ellipse(DOOR_X - 4, ey - 3, 8, 8, IRON[1])
    p.ellipse(DOOR_X - 3, ey - 2, 6, 6, IRON[0])
    p.hline(DOOR_X - 6, ey - 6, 6, IRON[4])
    p.px(DOOR_X - 7, ey - 4, IRON[4])


def jamb(p: Pix) -> None:
    """The door post: an oak beam facing us, with iron pintle plates where the hinges turn, and a stone footing."""
    wood_fill(p, (DOOR_X, 0, JAMB_X - DOOR_X, JAMB_FOOT), grain_dir="v", ramp=OAK, board=8, joints=False, nails=False,
              knots=0.5, wear_amount=0.5, damp=0.4, seed=3)
    p.vline(DOOR_X, 0, JAMB_FOOT, OAK[0])                           # the gap between door and post
    p.vline(DOOR_X + 1, 0, JAMB_FOOT, OAK[1])
    p.vline(JAMB_X - 1, 0, JAMB_FOOT, OAK[0])
    for y0 in (60, 226, 470):                                       # the pintle: an iron plate with a pin, level edges
        yk = round(toward(y0, DOOR_X)) + 6
        iron_fill(p, (DOOR_X + 1, yk - 8, 7, 16), hammer=0.4, rust=0.3, seed=y0)
        rivet(p, DOOR_X + 4, yk - 5, 1, BRASS)
        rivet(p, DOOR_X + 4, yk + 5, 1, BRASS)


def hatch(p: Pix) -> None:
    """The spy hatch cut in the boards: an oak frame, a dark opening with a lit slit of the room beyond, and an iron
    grille of round bars with a cross-rail, riveted where they cross. The opening's edges follow the door plane."""
    x0, x1, ya, yb = 5, 46, 150, 212
    outer = band(x0 - 3, x1 + 3, ya - 5, yb - ya + 10, 0)
    contact_shadow(p, outer, shift=(1, 2), spread=3, strength=0.8, alpha=200)
    wood_fill(p, outer, grain_dir="h", ramp=OAK, board=7, joints=False, nails=False, knots=0, wear_amount=0.6, seed=9)
    for x in range(x0, x1 + 1):
        top, bot = round(toward(ya, x)), round(toward(yb, x))
        for y in range(top, bot):
            depth = (y - top) / max(1, bot - top)
            c = SHADOW if y < top + 3 or x > x1 - 3 else IRON[0] if depth < 0.5 else IRON[1]
            if depth > 0.55 and x < x1 - 3 and stepped((depth - 0.5) * 1.4, x, y):
                c = mix(FLAME[0][:3], SHADOW[:3], 0.45) + (255,)    # a firelit room beyond the bars
            p.px(x, y, c)
        # the lit slit of the room: a thin warm glow low in the opening, broken by the bars
        ys = top + (bot - top) * 3 // 4
        if x < x1 - 3:
            p.px(x, ys, FLAME[3] if x % 5 else FLAME[2])
            p.px(x, ys + 1, FLAME[2] if x % 2 else FLAME[1])
            p.px(x, ys - 1, FLAME[1] if x % 3 == 0 else FLAME[0])
    for x in range(x0, x1 + 1):                                     # the opening's own rim: lit sill, dark head
        p.px(x, round(toward(ya, x)) - 1, OAK[0])
        p.px(x, round(toward(yb, x)), OAK[4])
        p.px(x, round(toward(yb, x)) + 1, OAK[3])
    for bx in range(x0 + 4, x1, 7):                                 # round bars: lit left, dark right
        top, bot = round(toward(ya, bx)) - 1, round(toward(yb, bx)) + 1
        p.vline(bx, top, bot - top, IRON[4])
        p.vline(bx + 1, top, bot - top, IRON[3])
        p.vline(bx + 2, top, bot - top, IRON[1])
    for yr in (ya + 22, ya + 40):                                   # two cross rails at different heights
        for x in range(x0, x1):
            y = round(toward(yr, x))
            p.px(x, y, IRON[4])
            p.px(x, y + 1, IRON[2])
            p.px(x, y + 2, IRON[0])
        for bx in range(x0 + 4, x1, 7):
            rivet(p, bx + 1, round(toward(yr, bx)) + 1, 1, BRASS)
    for x in (x0 - 1, x1 + 1):                                      # grille bolted to the frame
        for yr in (ya + 6, yb - 8):
            rivet(p, x, round(toward(yr, x)), 1, IRON)


def latch(p: Pix) -> None:
    """A wrought thumb-latch: a pierced backplate, a ring pull on a staple, a thumb-lever above it."""
    y0 = 392
    plate = band(10, 30, y0, 44, 0)
    contact_shadow(p, plate, shift=(2, 3), spread=3, strength=0.9, alpha=210)
    iron_fill(p, plate, hammer=0.8, rust=0.4, seed=17)
    for x, dy in ((13, 4), (27, 4), (13, 38), (27, 38)):
        rivet(p, x, round(toward(y0, x)) + dy, 1, BRASS)
    yl = round(toward(y0 + 10, 20))
    p.rect(8, yl - 1, 28, 4, IRON[0])                               # the thumb lever, running to the keeper
    p.hline(8, yl - 1, 28, IRON[4])
    p.hline(8, yl, 28, IRON[3])
    p.hline(8, yl + 1, 28, IRON[2])
    p.ellipse(5, yl - 3, 8, 8, IRON[3])                             # thumb pad
    p.ellipse(7, yl - 1, 4, 4, IRON[0])
    p.hline(6, yl - 2, 4, IRON[4])
    yr = round(toward(y0 + 28, 20))
    contact_shadow(p, [(14, yr), (27, yr), (27, yr + 14), (14, yr + 14)], shift=(2, 3), spread=2, strength=0.8, alpha=200)
    p.ellipse(14, yr, 14, 15, IRON[0])                              # the pull ring
    p.ellipse(15, yr + 1, 12, 13, IRON[3])
    p.ellipse(17, yr + 3, 8, 9, IRON[0])
    p.ellipse(18, yr + 4, 6, 7, WOOD[0])
    p.hline(17, yr + 1, 8, IRON[4])
    p.px(15, yr + 4, IRON[4])
    p.px(15, yr + 5, IRON[4])


def drawbolt(p: Pix) -> None:
    """The bar of the door: a sliding bolt with a knob, held in two staples, shooting into a keeper on the post."""
    y0 = 254
    for x0 in (4, 18, 32):                                          # staples (guides) the bolt slides through
        yy = round(toward(y0, x0))
        contact_shadow(p, [(x0, yy), (x0 + 6, yy), (x0 + 6, yy + 12), (x0, yy + 12)], shift=(1, 3), spread=2, alpha=200)
        iron_fill(p, (x0, yy, 6, 12), hammer=0.3, rust=0.3, seed=x0)
    for x in range(0, JAMB_X - 2):
        yy = round(toward(y0 + 4, x))
        p.px(x, yy, IRON[4])
        p.px(x, yy + 1, IRON[3])
        p.px(x, yy + 2, IRON[2])
        p.px(x, yy + 3, IRON[0])
    yk = round(toward(y0 + 4, 3))
    p.ellipse(1, yk - 3, 6, 9, IRON[0])                             # the knob
    p.ellipse(2, yk - 2, 4, 6, IRON[3])
    p.px(3, yk - 1, IRON[4])
    iron_fill(p, (DOOR_X + 1, round(toward(y0 + 4, DOOR_X)) - 4, 7, 12), hammer=0.2, rust=0.2, seed=5)   # keeper


def threshold(p: Pix) -> None:
    """A worn stone threshold under the door and its shadow on the boards. Both edges run to VP; the door stands on it,
    and the stone's front face is a level strip below its top."""
    pts_top, pts_front = [], []
    for x in range(0, JAMB_X):
        fx = foot(x) if x < DOOR_X else JAMB_FOOT
        s = (VP[0] - x) / (VP[0] - 14) if x >= 14 else 1.0
        fy = round(VP[1] + (FLOOR_NEAR - VP[1]) * min(1.0, s))
        pts_top.append((x, fx, fy))
    top_poly = [(x, a) for x, a, _ in pts_top] + [(x, max(a + 3, b)) for x, a, b in reversed(pts_top)]
    front_poly = [(x, max(a + 3, b)) for x, a, b in pts_top] + [(x, max(a + 3, b) + 7) for x, a, b in reversed(pts_top)]
    contact_shadow(p, front_poly, shift=(4, 6), spread=7, strength=1.0, alpha=220, squash=0.8)
    from fxkit import region
    # stone: top and front are different tones, with a chipped edge and a dip worn by boots
    for poly, ramp_bias in ((top_poly, 1), (front_poly, -1)):
        reg = region(p, poly)
        for x, y in reg.pixels():
            v = 2 + ramp_bias + (1 if (x * 7 + y * 3) % 11 == 0 else 0) - (1 if (x * 5 + y * 13) % 17 == 0 else 0)
            p.px(x, y, STONE[max(0, min(4, v))])
    for x, a, b in pts_top:
        p.px(x, a + 3 if b < a + 3 else a, STONE[1])                # the dark crack where the door meets the stone
        yb = max(a + 3, b)
        p.px(x, yb, STONE[4])                                       # the lit nose of the step
        p.px(x, yb + 1, STONE[3])
        p.px(x, yb + 7, STONE[0])
    for x in (21, 40):                                              # joints between stone blocks, one crack
        a = pts_top[x][1]
        for y in range(a, max(a + 3, pts_top[x][2]) + 7):
            p.px(x, y, STONE[0])
            p.px(x + 1, y, STONE[3])
    for x in range(JAMB_X):                                         # moss in the crack under the door
        a = pts_top[x][1]
        if (x * 13) % 7 < 2:
            p.px(x, a + 1, MOSS[1])
            p.px(x, a + 2, MOSS[2] if x % 3 == 0 else MOSS[0])


def weathering(p: Pix, door_poly: list[tuple[int, int]]) -> None:
    """Rain splash and rot at the foot of the boards, grime from hands at latch height, grey sun-bleach on top."""
    for x in range(0, DOOR_X):
        fy = foot(x)
        for dy in range(1, 46):
            k = 1 - dy / 46
            if stepped(0.65 * k * k, x, fy - dy):
                blend(p, x, fy - dy, SHADOW, 0.55)
            if dy < 8 and (x * 3 + dy * 7) % 5 == 0:
                blend(p, x, fy - dy, MOSS[1], 0.5)
    for y in range(380, 440):                                       # hand grease round the latch
        for x in range(4, 36):
            if stepped(0.14, x, y):
                blend(p, x, y, SHADOW, 0.35)
    wear(p, door_poly, amount=0.3, kinds=("scratch", "dust"), seed=5)


def door() -> Image.Image:
    p = Pix(W, H, seed=41)
    threshold(p)
    top = -10
    door_poly = [(0, top), (DOOR_X, top), (DOOR_X, JAMB_FOOT), (DOOR_X - 1, JAMB_FOOT), ] + \
                [(x, foot(x)) for x in range(DOOR_X - 1, -1, -1)]
    wood_fill(p, door_poly, grain_dir="v", ramp=WOOD, board=13, joints=False, nails=False, knots=0.7,
              wear_amount=0.4, damp=0.55, damp_from="bottom", light=0.4, seed=4)
    for bx in (13, 26, 39):                                         # a dark seam between boards, with a lit near edge
        for y in range(0, foot(bx)):
            p.px(bx, y, WOOD[0])
            p.px(bx + 1, y, WOOD[4] if (y // 3) % 7 else WOOD[3])
    jamb(p)
    for y0, sd in ((60, 21), (226, 31), (470, 41)):
        hinge_strap(p, y0, sd)
    hatch(p)
    latch(p)
    drawbolt(p)
    weathering(p, door_poly)
    p.clip([(0, 0), (JAMB_X - 1, 0), (JAMB_X - 1, 539), (0, 539)])
    return p.finish()


# ---------------------------------------------------------------------------------------------- the chained padlock


def staple(p: Pix, x: int, y: int) -> None:
    """An iron staple driven into the beam: two legs and a bridge with a ring through it, a drop of shade below."""
    contact_shadow(p, (x - 5, y - 2, 11, 9), shift=(2, 3), spread=3, strength=1.0, alpha=220)
    iron_fill(p, (x - 5, y - 3, 11, 5), hammer=0.4, rust=0.3, seed=2)
    rivet(p, x - 3, y - 1, 1, BRASS)
    rivet(p, x + 3, y - 1, 1, BRASS)
    p.ellipse(x - 3, y, 7, 8, IRON[0])
    p.ellipse(x - 2, y + 1, 5, 6, IRON[3])
    p.ellipse(x - 1, y + 2, 3, 4, SHADOW)


def padlock(p: Pix, cx: int, top: int) -> None:
    """A brass-bodied padlock: iron shackle through the last chain link, a body with a bevelled face, a keyhole with a
    brass cover, a seam and a rivet; the body hangs plumb and throws a shadow on the wall to its lower right."""
    bw, bh = 17, 20
    x0, y0 = cx - bw // 2, top + 8
    contact_shadow(p, (x0, y0, bw, bh), shift=(4, 4), spread=4, strength=1.0, alpha=200, squash=1.0)
    # shackle: a thick iron U
    p.ellipse(x0 + 3, top - 2, bw - 6, 16, IRON[0])
    p.ellipse(x0 + 5, top, bw - 10, 12, (0, 0, 0, 0))
    for y in range(top - 1, y0 + 2):
        p.px(x0 + 4, y, IRON[4])
        p.px(x0 + 5, y, IRON[3])
        p.px(x0 + bw - 6, y, IRON[1])
        p.px(x0 + bw - 5, y, IRON[0])
    p.hline(x0 + 6, top - 1, bw - 12, IRON[4])
    p.hline(x0 + 5, top, bw - 10, IRON[3])
    # body
    brass_fill(p, (x0, y0, bw, bh), profile="plate", tarnish=0.55, seed=6)
    p.hline(x0, y0, bw, BRASS[4])
    p.vline(x0, y0, bh, BRASS[4])
    p.hline(x0, y0 + bh - 1, bw, BRASS[0])
    p.vline(x0 + bw - 1, y0, bh, BRASS[0])
    p.hline(x0 + 1, y0 + 3, bw - 2, BRASS[1])                       # the seam where the case closes
    p.hline(x0 + 1, y0 + 4, bw - 2, BRASS[3])
    p.ellipse(cx - 2, y0 + 8, 5, 5, BRASS[0])                       # keyhole cover
    p.ellipse(cx - 1, y0 + 9, 3, 3, SHADOW)
    p.px(cx, y0 + 12, SHADOW)
    p.px(cx, y0 + 13, SHADOW)
    p.px(cx - 2, y0 + 8, BRASS[4])
    rivet(p, x0 + 3, y0 + bh - 4, 1, BRASS)
    rivet(p, x0 + bw - 4, y0 + bh - 4, 1, BRASS)


def door_lock() -> Image.Image:
    """The door's lock: a chain from a staple in the tie beam, closed with a padlock; at the door a drop bar slides
    into a keeper. Layer bbox 54..89 x 0..303."""
    p = Pix(W, H, seed=42)
    cx = 66
    staple(p, cx, 8)
    chain(p, [(cx, 14), (cx, 262)], link=9.0)
    # the last link is a little ring that the padlock's shackle goes through
    p.ellipse(cx - 4, 256, 9, 12, IRON[0])
    p.ellipse(cx - 3, 257, 7, 10, IRON[3])
    p.ellipse(cx - 1, 259, 3, 6, (0, 0, 0, 0))
    padlock(p, cx, 264)
    p.clip([(54, 0), (89, 0), (89, 303), (54, 303)])
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "door.960x540.png": door,
    "door lock.960x540.png": door_lock,
}
