"""The three display cases of the shop window (`display_case`, `display_case_medium`, `display_case_large`).

Reading: the shop-window cabinet that shows our goods to the people in the street. It is an oak cabinet set into the thick
wall: the wall is cut open behind it (see cas_wall), the cabinet has a leaded glass front *and* a glass back, so the street
shows through. Oak frame with mitred corners, brass corner fittings, a hinge on the right and a brass lock on the left;
inside, a left wall and a floor seen in the shop's perspective (vanishing point on the right), shelves of pale wood on
brass wall brackets, and a few goods: an hourglass, a clay jug, books, a pewter goblet and a leather pouch.

A smaller case leaves part of the largest opening free, so its picture also paints the plaster of the wall (copied from the
wall's own plaster recipe, see cas_kit) and the wall's reveal around itself.
"""

from __future__ import annotations

from collections.abc import Callable

from PIL import Image

import cas_kit
import fxkit
from cas_kit import FRAMES, H, OPEN, RING_BOTTOM, RING_LEFT, W, proj
from fxkit import brass_fill, contact_shadow, glass_pane, noise, over, rivet, wood_fill
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, OAK, PALE_WOOD, PARCHMENT, PLASTER, SHADOW, WINE, MOSS, NAVY, WOOD
from pix import Color, Pix, mix, rgb
from shopx_persp import blend, stepped

_over_orig = fxkit.over


def _over_int(p: Pix, x: int, y: int, c: Color, alpha: int = 255) -> None:
    """fxkit.glass_pane passes a float alpha, which Pillow refuses on a transparent pixel: round it (only the type changes)."""
    _over_orig(p, x, y, c, int(alpha))


fxkit.over = _over_int

T_SIDE, T_BASE = 7, 9                 # frame thickness at the top and sides, and at the foot
CLAY = (rgb("#4a2c1a"), rgb("#6c4226"), rgb("#8e5b32"), rgb("#b27a45"), rgb("#d5a265"))
PEWTER = (rgb("#2c2b33"), rgb("#4a4a54"), rgb("#6e6e7a"), rgb("#9a9aa6"), rgb("#c8c8d0"))


# ---------------------------------------------------------------------------------------------- goods


def _body(p: Pix, cx: int, by: int, half: list[int], ramp: tuple[Color, ...], rim: Color | None = None) -> None:
    """A vessel of revolution, lit from the left: `half[i]` is the half width of the i-th row counted from the base up."""
    top = len(ramp) - 1
    for i, hw in enumerate(half):
        y = by - i
        for x in range(cx - hw, cx + hw + 1):
            u = (x - cx) / max(1, hw)                          # -1 lit edge .. +1 shaded edge
            v = 3.1 - 1.9 * (u + 1) / 2 + (noise(x, y, 4) - 0.5) * 0.7
            if u < -0.55 and i % 3:
                v += 0.6
            c = ramp[max(0, min(top, round(v)))]
            p.px(x, y, c)
        p.px(cx - hw, y, ramp[0] if i in (0, len(half) - 1) else ramp[min(top, 3)])
        p.px(cx + hw, y, ramp[0])
    if rim is not None:
        p.hline(cx - half[-1], by - len(half) + 1, 2 * half[-1] + 1, rim)


def _foot_shadow(p: Pix, cx: int, by: int, hw: int) -> None:
    for x in range(cx - hw - 1, cx + hw + 3):
        over(p, x, by + 1, SHADOW, 150)
    for x in range(cx - hw + 1, cx + hw + 3):
        if stepped(0.5, x, by + 2):
            over(p, x, by + 2, SHADOW, 100)


def hourglass(p: Pix, cx: int, by: int) -> None:
    """Two turned posts between two caps hold two glass bulbs; sand runs through the waist."""
    _foot_shadow(p, cx, by, 6)
    h = 22
    mid = by - h // 2
    for post in (cx - 6, cx + 5):                              # turned posts, lit on the left
        for y in range(by - h + 2, by - 1):
            p.px(post, y, PALE_WOOD[3])
            p.px(post + 1, y, PALE_WOOD[1])
        for y in (by - h + 6, by - 5):
            p.px(post, y, PALE_WOOD[4])
            p.px(post + 1, y, PALE_WOOD[0])
    for cy_ in (by - h, by - 2):                               # caps
        p.rect(cx - 8, cy_, 17, 3, PALE_WOOD[2])
        p.hline(cx - 8, cy_, 17, PALE_WOOD[4])
        p.hline(cx - 8, cy_ + 2, 17, PALE_WOOD[0])
        p.vline(cx + 8, cy_, 3, PALE_WOOD[0])
    rows = range(by - h + 3, by - 2)
    for y in rows:                                             # glass, seen through its own walls
        dy = abs(y - mid)
        hw = 1 + round(4.4 * (dy / 8.0) ** 0.62)
        for x in range(cx - hw, cx + hw + 1):
            over(p, x, y, GLASS[3], 165)
        p.px(cx - hw, y, mix(GLASS[4][:3], (255, 255, 255), 0.0))
        p.px(cx + hw, y, GLASS[1])
    for y in range(by - 7, by - 2):                            # sand heaped in the lower bulb
        dy = abs(y - mid)
        hw = max(0, 1 + round(4.4 * (dy / 8.0) ** 0.62) - 1)
        peak = (by - 7 - y) * -1
        for x in range(cx - hw, cx + hw + 1):
            p.px(x, y, FLAME[2] if x < cx + 1 else FLAME[1])
        p.px(cx - hw + 1, y, FLAME[3])
    for y in range(by - h + 4, by - h + 6):                    # what is left in the upper bulb, and the thread through the waist
        hw = 1 + round(4.4 * (abs(y - mid) / 8.0) ** 0.62) - 1
        for x in range(cx - hw, cx + hw + 1):
            p.px(x, y, FLAME[1])
    p.vline(cx, mid - 1, 7, FLAME[3])


def jug(p: Pix, cx: int, by: int) -> None:
    """A clay jug with a glazed shoulder, a loop handle and a cork."""
    _foot_shadow(p, cx, by, 7)
    half = [4, 5, 6, 7, 8, 8, 8, 8, 8, 7, 7, 6, 5, 4, 3, 3, 3, 3]            # base to lip
    for i in range(7, 13):                                                    # the handle: a loop on the right
        pass
    _body(p, cx, by, half, CLAY)
    for y in range(by - 12, by - 8):                                          # dark glaze on the shoulder, dripping
        for x in range(cx - 7, cx + 8):
            if p.get(x, y)[3] and (x + y) % 3:
                p.px(x, y, CLAY[0] if x > cx - 3 else CLAY[1])
    p.hline(cx - 3, by - 17, 7, CLAY[0])                                       # the lip
    p.rect(cx - 1, by - 20, 3, 3, PALE_WOOD[2])                                # cork
    p.hline(cx - 1, by - 20, 3, PALE_WOOD[4])
    for y in range(by - 14, by - 6):                                           # the handle
        x = cx + 9 + (1 if by - 12 > y > by - 9 else 0)
        p.px(x, y, CLAY[2] if y % 2 else CLAY[3])
        p.px(x + 1, y, CLAY[0])
    p.hline(cx + 7, by - 14, 3, CLAY[1])
    p.hline(cx + 7, by - 7, 3, CLAY[1])


def pouch(p: Pix, cx: int, by: int) -> None:
    """A leather coin pouch, slumped, tied at the neck with a cord."""
    _foot_shadow(p, cx, by, 6)
    half = [5, 6, 7, 7, 7, 6, 6, 5, 4, 3, 3, 3]
    _body(p, cx, by, half, LEATHER)
    p.hline(cx - 4, by - 8, 9, WINE[1])                                         # the cord
    p.hline(cx - 4, by - 9, 9, WINE[3])
    p.px(cx + 3, by - 7, WINE[2])
    p.px(cx + 4, by - 6, WINE[2])
    p.px(cx + 4, by - 5, WINE[1])
    for y in range(by - 13, by - 10):                                           # the gathered mouth
        p.px(cx - 4 + (y % 2), y, LEATHER[3])
        p.px(cx + 3 - (y % 2), y, LEATHER[1])
    p.rect(cx - 3, by - 5, 2, 2, BRASS[3])                                      # a coin shows through a worn patch
    p.px(cx - 3, by - 5, BRASS[4])


def goblet(p: Pix, cx: int, by: int) -> None:
    """A pewter goblet with wine in it."""
    _foot_shadow(p, cx, by, 4)
    p.hline(cx - 4, by, 9, PEWTER[1])
    p.hline(cx - 3, by - 1, 7, PEWTER[3])
    p.hline(cx - 3, by, 7, PEWTER[1])
    for y in range(by - 5, by - 1):
        p.px(cx - 1, y, PEWTER[4])
        p.px(cx, y, PEWTER[3])
        p.px(cx + 1, y, PEWTER[1])
    p.rect(cx - 2, by - 4, 5, 1, PEWTER[2])                                     # knop
    half = [2, 3, 4, 5, 5, 5]                                                   # bowl, base to rim
    _body(p, cx, by - 6, half, PEWTER)
    p.hline(cx - 4, by - 11, 9, WINE[3])                                        # wine seen over the rim
    p.hline(cx - 3, by - 11, 2, WINE[4])
    p.hline(cx - 5, by - 12, 11, PEWTER[4])


def books(p: Pix, cx: int, by: int, lying: bool = True) -> None:
    """Three upright books with spines of wine, moss and navy cloth, brass bands and a label, and one laid on top."""
    _foot_shadow(p, cx + 1, by, 8)
    spec = ((WINE, 15, 5), (MOSS, 17, 5), (NAVY, 14, 4))
    x = cx - 7
    for ramp, h, w in spec:
        for dx in range(w):
            for y in range(by - h + 1, by + 1):
                c = ramp[3] if dx == 0 else ramp[2] if dx < w - 1 else ramp[0]
                if dx == 1 and (y + dx) % 4 == 0:
                    c = ramp[3]
                p.px(x + dx, y, c)
        p.hline(x, by - h + 1, w, ramp[3])
        for yy in (by - h + 3, by - 3):
            p.hline(x + 1, yy, w - 2, BRASS[3])
        p.rect(x + 1, by - h // 2 - 1, max(1, w - 3), 3, PARCHMENT[3])
        x += w
    if lying:
        top = by - 17 - 1
        p.rect(cx - 5, top, 11, 1, LEATHER[1])
        p.rect(cx - 5, top - 1, 11, 1, LEATHER[3])
        p.rect(cx - 5, top - 3, 11, 2, PARCHMENT[3])
        p.hline(cx - 5, top - 4, 11, LEATHER[2])
        p.hline(cx - 5, top - 4, 2, LEATHER[3])
        _foot_shadow(p, cx, top + 1, 5)


# ---------------------------------------------------------------------------------------------- wood and metal


def _bars(p: Pix, f: tuple[int, int, int, int], seed: int) -> None:
    x0, y0, x1, y1 = f
    x1, y1 = x1 - 1, y1 - 1
    t, tb = T_SIDE, T_BASE
    shapes = (
        ([(x0, y0), (x1, y0), (x1 - t, y0 + t), (x0 + t, y0 + t)], "h", 0.45, T_SIDE),
        ([(x0, y0), (x0 + t, y0 + t), (x0 + t, y1 - tb), (x0, y1)], "v", 0.2, T_SIDE),
        ([(x1, y0), (x1, y1), (x1 - t, y1 - tb), (x1 - t, y0 + t)], "v", -0.5, T_SIDE),
        ([(x0, y1), (x0 + t, y1 - tb), (x1 - t, y1 - tb), (x1, y1)], "h", -0.15, T_BASE),
    )
    for i, (poly, grain, bias, board) in enumerate(shapes):
        wood_fill(p, poly, grain_dir=grain, ramp=WOOD, board=board, bias=bias, knots=0.7, joints=False, nails=False,
                  rim=True, wear_amount=0.45, seed=seed + i * 7)
    p.line(x0, y0, x0 + t, y0 + t, OAK[0])                     # the mitres
    p.line(x1, y0, x1 - t, y0 + t, OAK[0])
    p.line(x0, y1, x0 + t, y1 - tb, OAK[0])
    p.line(x1, y1, x1 - t, y1 - tb, OAK[0])
    p.hline(x0 + t, y0 + t - 1, x1 - x0 - 2 * t + 1, OAK[1])  # the glazing rebate: a dark step all round
    p.vline(x0 + t - 1, y0 + t, y1 - tb - y0 - t, OAK[1])
    p.vline(x1 - t + 1, y0 + t, y1 - tb - y0 - t, OAK[4])
    p.hline(x0 + t, y1 - tb + 1, x1 - x0 - 2 * t + 1, OAK[4])


def _corner(p: Pix, x: int, y: int, sx: int, sy: int) -> None:
    """A brass L-plate on one outer corner; (sx, sy) = (+1, +1) for the top left and so on. Lit on whatever edge faces up
    or left, dark on whatever faces down or right, so every corner is lit from the same side."""
    a, th = 13, 4
    cells = {(x + sx * i, y + sy * j) for i in range(a) for j in range(a) if i < th or j < th}
    for (cx_, cy_) in cells:
        up, left = (cx_, cy_ - 1) not in cells, (cx_ - 1, cy_) not in cells
        down, right = (cx_, cy_ + 1) not in cells, (cx_ + 1, cy_) not in cells
        tone = 3
        if noise(cx_, cy_, 17) < 0.22:
            tone = 2
        if up or left:
            tone = 4
        if down or right:
            tone = 1
        if (up and right) or (down and left):
            tone = 2
        p.px(cx_, cy_, BRASS[tone])
    for k in (th + 3, a - 2):                                    # rivets: one at the elbow, one on each arm
        pass
    for qx, qy in ((x + sx * 1, y + sy * 1), (x + sx * 9, y + sy * 1), (x + sx * 1, y + sy * 9)):
        p.px(qx, qy, BRASS[4])
        p.px(qx + 1, qy + 1, BRASS[0])


def _hinge(p: Pix, x1: int, yc: int) -> None:
    """A strap hinge on the right bar: a leaf with two rivets and a barrel with a pin head."""
    bx0, bx1 = x1 - T_SIDE, x1 - 1
    brass_fill(p, (bx0 + 1, yc - 6, T_SIDE - 1, 12), BRASS, "plate", tarnish=0.5, seed=yc)
    for k in range(3):                                         # the barrel along the outer edge
        p.vline(bx1 - 2 + k, yc - 6, 12, (BRASS[4], BRASS[3], BRASS[0])[k])
    p.hline(bx1 - 2, yc - 6, 3, BRASS[1])
    p.hline(bx1 - 2, yc + 5, 3, BRASS[1])
    p.px(bx1 - 1, yc - 7, BRASS[4])                             # the pin's head
    p.px(bx1 - 1, yc - 8, BRASS[3])
    for ry in (yc - 3, yc + 2):
        p.px(bx0 + 2, ry, BRASS[4])
        p.px(bx0 + 3, ry + 1, BRASS[0])


def _lock(p: Pix, x0: int, yc: int) -> None:
    """A brass lock plate with a keyhole and an escutcheon, on the left bar."""
    brass_fill(p, (x0 + 1, yc - 8, T_SIDE - 2, 16), BRASS, "plate", tarnish=0.35, seed=yc + 3)
    cx = x0 + 1 + (T_SIDE - 2) // 2
    p.px(cx, yc - 2, IRON[0])
    p.px(cx - 1, yc - 3, IRON[0])
    p.px(cx + 1, yc - 3, IRON[0])
    p.px(cx, yc - 3, IRON[0])
    p.vline(cx, yc - 1, 3, IRON[0])
    p.hline(cx - 2, yc - 5, 5, BRASS[4])
    for ry in (yc - 7, yc + 6):
        p.px(cx, ry, BRASS[4])
        p.px(cx + 1, ry + 1, BRASS[0])
    p.px(cx + 2, yc + 1, BRASS[0])


# ---------------------------------------------------------------------------------------------- the wall around a smaller case


def _wall_infill(p: Pix, f: tuple[int, int, int, int]) -> None:
    """Plaster out to the largest opening's edge, and the reveal around the case: a lit left face and a lit sill, a dark
    top and right edge."""
    ox0, oy0, ox1, oy1 = OPEN
    x0, y0, x1, y1 = f
    rx0, ry1 = x0 - RING_LEFT, y1 + RING_BOTTOM
    wall = cas_kit.plaster_wall(0).im
    for y in range(oy0, oy1):
        for x in range(ox0, ox1):
            if rx0 <= x < x1 and y < ry1:
                continue
            p.im.putpixel((x, y), wall.getpixel((x, y)))
    if x1 < ox1 or ry1 < oy1:
        for y in range(oy0, oy0 + 6):                           # the lintel's shade on the plaster
            for x in range(ox0, ox1):
                if p.get(x, y)[3] and not (rx0 <= x < x1) and stepped(0.7 * (1 - (y - oy0) / 6), x, y):
                    blend(p, x, y, SHADOW, 0.55)
    # the reveal
    for y in range(y0, y1):
        for k in range(RING_LEFT):
            c = (PLASTER[4], PLASTER[3], PLASTER[2])[k]
            if noise(rx0 + k, y, 8) < 0.12:
                c = PLASTER[2]
            p.px(rx0 + k, y, c)
    for k in range(RING_BOTTOM):
        for x in range(rx0, x1):
            p.px(x, y1 + k, PLASTER[4] if k == 0 else PLASTER[3])
    if x1 < ox1:
        p.vline(x1, y0, ry1 - y0, PLASTER[0])                   # the hole's right edge
        p.vline(x1 + 1, y0, ry1 - y0, PLASTER[1])
    if ry1 < oy1:
        p.hline(rx0, ry1, x1 - rx0 + (2 if x1 < ox1 else 0), PLASTER[0])    # the sill's front edge
        for x in range(rx0, x1 + 2):
            if stepped(0.55, x, ry1 + 1):
                blend(p, x, ry1 + 1, SHADOW, 0.5)
            if stepped(0.25, x, ry1 + 2):
                blend(p, x, ry1 + 2, SHADOW, 0.5)
    for k in range(ox1 - x1 if x1 < ox1 else 0):                # the jamb's shade falls on the plaster, but it is a timber 7 px away: none
        break


# ---------------------------------------------------------------------------------------------- the case


def _shelf(inner: Pix, g: tuple[int, int, int, int], ys: int) -> None:
    """A pale-wood shelf whose top face is seen from slightly above, on a brass wall bracket."""
    gx0, gy0, gx1, gy1 = g
    u_front = 0.1
    xl_f, yf = proj(gx0, ys, u_front)
    xl_b, yb = proj(gx0, ys, 1.0)
    xl_f, yf, xl_b, yb = round(xl_f), round(yf), round(xl_b), round(yb)
    for y in range(yb, yf + 1):                                  # the top face
        t = (y - yb) / max(1, yf - yb)
        xs = round(xl_b + (xl_f - xl_b) * t)
        inner.hline(xs, y, gx1 - xs + 1, PALE_WOOD[3] if y != yb else PALE_WOOD[2])
    for y in range(yf + 1, yf + 4):                              # the front edge
        inner.hline(xl_f, y, gx1 - xl_f + 1, (PALE_WOOD[4], PALE_WOOD[2], PALE_WOOD[0])[y - yf - 1])
    inner.vline(xl_f, yf + 1, 3, PALE_WOOD[4])
    for x in range(xl_f + 4, gx1, 9):                            # a grain check
        inner.px(x, yf + 2, PALE_WOOD[1])
    # the wall bracket: an arm under the shelf, a leg down the wall and a strut, all in the wall's plane
    def wp(u: float, y: float) -> tuple[int, int]:
        a, b = proj(gx0, y, u)
        return round(a), round(b)
    pts_arm = [wp(0.2, ys + 4), wp(0.72, ys + 4)]
    pts_leg = [wp(0.72, ys + 4), wp(0.72, ys + 13)]
    pts_str = [wp(0.2, ys + 4), wp(0.72, ys + 13)]
    for a, b, c in ((pts_str, None, BRASS[1]), (pts_arm, None, BRASS[3]), (pts_leg, None, BRASS[2])):
        inner.line(a[0][0], a[0][1], a[1][0], a[1][1], c)
        inner.line(a[0][0], a[0][1] + 1, a[1][0], a[1][1] + 1, BRASS[1] if c != BRASS[1] else BRASS[0])
    ax, ay = pts_arm[1]
    inner.px(ax, ay, BRASS[4])
    inner.px(ax, ay + 5, BRASS[4])
    for k in range(3):                                            # the shelf's shade on the wall below it
        for x in range(xl_f, xl_f + 12):
            if stepped(0.6 - k * 0.2, x, yf + 4 + k):
                over(inner, x, yf + 4 + k, SHADOW, 130)


def _interior(g: tuple[int, int, int, int], goods: list[tuple[str, int, float, int | None]], shelves: tuple[int, ...],
              cols: int, rows: int, seed: int) -> Pix:
    """Everything behind the front glass, drawn on its own layer: back glass, the left wall, the floor, shelves, goods."""
    gx0, gy0, gx1, gy1 = g
    layer = Pix(W, H, seed=seed)
    bx0, by0 = (round(v) for v in proj(gx0, gy0, 1.0))
    bx1, by1 = (round(v) for v in proj(gx1, gy1, 1.0))
    # the back: a thin frame and a pane of glass (transparent) behind the goods
    layer.rect(bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1, OAK[1])
    inner = (bx0 + 2, by0 + 2, bx1 - bx0 - 3, by1 - by0 - 3)
    layer.erase(*inner)
    glass_pane(layer, inner, cols=cols, rows=rows, came=1, alpha=7, streaks=0, back=False, seed=seed + 5)
    layer.hline(bx0, by0, bx1 - bx0 + 1, OAK[0])
    layer.vline(bx0, by0, by1 - by0 + 1, OAK[0])
    layer.hline(bx0 + 1, by1, bx1 - bx0, OAK[3])
    # left wall (faces the room's lamp: lit) and the floor
    left = [(gx0, gy0), (bx0, by0), (bx0, by1), (gx0, gy1)]
    wood_fill(layer, left, grain_dir="v", ramp=PALE_WOOD, board=5, bias=-0.7, knots=0.6, joints=False, nails=False,
              rim=False, wear_amount=0.1, seed=seed + 11)
    for y in range(gy0, gy1 + 1):                                 # the wall darkens toward the back
        for x in range(gx0, bx0 + 1):
            if layer.get(x, y)[3] and stepped(0.55 * (x - gx0) / max(1, bx0 - gx0), x, y):
                blend(layer, x, y, SHADOW, 0.5)
    layer.line(bx0, by0, bx0, by1, OAK[0])
    floor = [(gx0, gy1), (gx1 + 9, gy1), (bx1, by1), (bx0, by1)]
    wood_fill(layer, floor, grain_dir="h", ramp=PALE_WOOD, board=3, bias=0.6, knots=0.3, joints=True, nails=False,
              rim=False, wear_amount=0.1, seed=seed + 13)
    layer.hline(gx0, gy1, gx1 - gx0 + 1, PALE_WOOD[4])
    layer.line(gx0, gy1, bx0, by1, OAK[0])
    layer.hline(bx0, by0 - 1, bx1 - bx0 + 1, OAK[0])             # the underside of the top bar
    for y in range(gy0 - 0, gy0 + 3):
        for x in range(gx0, gx1):
            if stepped(0.5 - (y - gy0) * 0.15, x, y) and layer.get(x, y)[3] and layer.get(x, y)[3] == 255:
                blend(layer, x, y, SHADOW, 0.6)
    for ys in shelves:
        _shelf(layer, g, ys)
    fns: dict[str, Callable[[Pix, int, int], None]] = {"hourglass": hourglass, "jug": jug, "pouch": pouch,
                                                        "goblet": goblet, "books": books}
    for kind, x, u, ys in goods:                                  # goods rest on a shelf's top face or the floor
        level = gy1 if ys is None else ys
        px_, py_ = proj(x, level, u)
        fns[kind](layer, round(px_), round(py_) - 1)
    return layer


def _case(kind: str, goods: list[tuple[str, int, float, int | None]], shelves: tuple[int, ...], cols: int, rows: int) -> Image.Image:
    seed = {"small": 31, "medium": 32, "large": 33}[kind]
    f = FRAMES[kind]
    x0, y0, x1, y1 = f
    p = Pix(W, H, seed=seed)
    _wall_infill(p, f)
    _bars(p, f, seed * 3)
    g = (x0 + T_SIDE, y0 + T_SIDE, x1 - T_SIDE - 1, y1 - T_BASE - 1)
    layer = _interior(g, goods, shelves, cols, rows, seed + 100)
    # the front glass over the interior: transparent tint, sparse streaks, lead cames
    glass_pane(layer, (g[0], g[1], g[2] - g[0] + 1, g[3] - g[1] + 1), cols=cols, rows=rows, came=2, alpha=9, streaks=1,
               back=True, seed=seed + 9)
    clip = layer.im.crop((g[0], g[1], g[2] + 1, g[3] + 1))
    p.paste(clip, g[0], g[1])
    for y in range(y0, y0 + 4):                                   # the lintel's shade on the top bar
        for x in range(x0, x1):
            if stepped(0.55 - (y - y0) * 0.15, x, y):
                blend(p, x, y, SHADOW, 0.5)
    # the cabinet's furniture
    for cx_, cy_, sx, sy in ((x0, y0, 1, 1), (x1 - 1, y0, -1, 1), (x0, y1 - 1, 1, -1), (x1 - 1, y1 - 1, -1, -1)):
        _corner(p, cx_, cy_, sx, sy)
    mid = (g[1] + g[3]) // 2
    _hinge(p, x1, g[1] + (g[3] - g[1]) // 5)
    _hinge(p, x1, g[3] - (g[3] - g[1]) // 5)
    _lock(p, x0, mid)
    for x in range(x0 + 13, x1 - 13, 23):                         # pegs through the top and bottom bars
        for yy in (y0 + 3, y1 - 5):
            p.rect(x, yy, 2, 2, OAK[0])
            p.px(x, yy, OAK[4])
    return p.finish()


def small() -> Image.Image:
    return _case("small", [("hourglass", 160, 0.45, 173), ("goblet", 205, 0.5, 173), ("jug", 150, 0.4, None),
                           ("books", 215, 0.45, None)], (173,), 3, 2)


def medium() -> Image.Image:
    return _case("medium", [("hourglass", 160, 0.45, 181), ("books", 220, 0.5, 181), ("jug", 150, 0.4, None),
                            ("pouch", 235, 0.45, None)], (181,), 3, 2)


def large() -> Image.Image:
    return _case("large", [("hourglass", 160, 0.45, 168), ("books", 215, 0.5, 168), ("goblet", 258, 0.5, 168),
                           ("jug", 150, 0.4, 208), ("pouch", 205, 0.45, 208), ("goblet", 245, 0.4, 208),
                           ("books", 225, 0.5, None), ("jug", 165, 0.5, None)], (168, 208), 4, 2)


ASSETS: dict[str, Callable[[], Image.Image]] = {
    "display_case.960x540.png": small,
    "display_case_medium.960x540.png": medium,
    "display_case_large.960x540.png": large,
}
