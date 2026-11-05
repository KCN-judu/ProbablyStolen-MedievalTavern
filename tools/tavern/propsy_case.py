"""`display_case`, `_medium`, `_large`: glass shop windows for the goods shown to the people outside.

An oak frame (mitred, brass studs) holds a front pane in lead cames; behind it the box is seen in the shop's
perspective (its far side moved toward VP): the inside of the left wall, a glass back pane in lead cames, a floor, and
glass shelves on brass brackets (their edges show, their top plane shows below the horizon and their underside above
it). Both panes and the shelves are translucent, so the plaster behind the case shows through the back; reflections
are pale streaks on the front pane and a soft warm light falls from the top rail.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

from palette import BRASS, FLAME, GLASS, IRON, OAK, SHADOW, WOOD
from pix import Pix
from props import mitred_frame
from shopx_persp import VP

W, H = 960, 540
DEPTH = 0.95                       # scale toward VP of the back pane
T = 10                             # frame thickness
GLASS_TINT = (120, 170, 176)


def case(box: tuple[int, int, int, int], seed: int, shelves: int) -> Image.Image:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    wall = Pix(W, H, seed=seed)                                   # everything inside the frame, in screen coordinates
    g = Pix(W, H, seed=seed + 1)                                  # the tint of the panes, under the cames
    top = Pix(W, H, seed=seed + 3)                                # shelves, streaks and light, over everything
    ix0, iy0, ix1, iy1 = x0 + T, y0 + T, x1 - T, y1 - T           # inner opening (front plane)

    def back(x: float, y: float) -> tuple[int, int]:
        return round(VP[0] + (x - VP[0]) * DEPTH), round(VP[1] + (y - VP[1]) * DEPTH)

    bx0, by0 = back(ix0, iy0)
    bx1, by1 = back(ix1, iy1)
    # side wall (left, lit, seen inside), ceiling and floor: opaque wood strips in perspective
    wall.poly([(ix0, iy0), (bx0, by0), (bx0, by1), (ix0, iy1)], WOOD[3])
    for k in range(1, 4):                                         # boards of the left wall run in depth
        yy = iy0 + (iy1 - iy0) * k // 4
        wall.line(ix0, yy, bx0, back(ix0, yy)[1], WOOD[2])
    wall.dither(ix0, iy0, bx0 - ix0, iy1 - iy0, WOOD[2], 0.12)
    wall.poly([(ix0, iy0), (ix1 - 1, iy0), (bx1, by0), (bx0, by0)], OAK[1])      # underside of the top
    wall.poly([(ix0, iy1 - 1), (ix1 - 1, iy1 - 1), (bx1, by1), (bx0, by1)], WOOD[3])   # floor: its top plane
    wall.dither(ix0, by1, ix1 - ix0, iy1 - by1, WOOD[2], 0.4)
    wall.hline(ix0, iy1 - 1, ix1 - ix0, WOOD[4])
    # glass back pane: a faint tint, lead cames in a grid
    g.rect(bx0, by0, bx1 - bx0, by1 - by0, (*GLASS_TINT, 26))
    cols = 2 if w < 160 else 3
    for i in range(1, cols + 1):
        cx = bx0 + (bx1 - bx0) * i // (cols + 1)
        wall.vline(cx, by0, by1 - by0, IRON[2])
        wall.vline(cx + 1, by0, by1 - by0, IRON[0])
    for j in range(1, 3):
        cy = by0 + (by1 - by0) * j // 3
        wall.hline(bx0, cy, bx1 - bx0, IRON[2])
        wall.hline(bx0, cy + 1, bx1 - bx0, IRON[0])
    wall.rect(bx0, by0, bx1 - bx0, 1, IRON[1])
    wall.vline(bx1 - 1, by0, by1 - by0, IRON[1])
    # glass shelves with brass brackets on the left wall
    for k in range(1, shelves + 1):
        sy = iy0 + (iy1 - iy0) * (55 + 22 * (k - 1)) // 100               # front edge row
        by_ = back(ix0, sy)[1]
        shelf_far = [(ix0, sy), (ix1 - 1, sy), back(ix1 - 1, sy), (bx0, by_)]
        top.poly(shelf_far, (*GLASS[4][:3], 70))
        top.line(ix0, sy, ix1 - 1, sy, (*GLASS[4][:3], 255))        # the front edge of the glass, aqua and bright
        top.line(ix0, sy + 1, ix1 - 1, sy + 1, (*GLASS[2][:3], 255))
        top.line(ix0, sy, bx0, by_, (*GLASS[4][:3], 200))
        top.line(bx0, by_, bx1 - 1, by_, (*GLASS[3][:3], 150))
        for bxx in (ix0 + 2, (ix0 + ix1) // 2):                   # brackets under the front edge
            wall.rect(bxx, sy + 2, 3, 4, BRASS[2])
            wall.px(bxx, sy + 2, BRASS[4])
            wall.px(bxx + 2, sy + 5, BRASS[0])
    # front pane: a lead came down the middle, reflection streaks, light from the top rail
    for i in range(1, cols):
        cx = ix0 + (ix1 - ix0) * i // cols
        wall.rect(cx - 1, iy0, 3, iy1 - iy0, IRON[1])
        wall.vline(cx - 1, iy0, iy1 - iy0, IRON[3])
        wall.vline(cx + 1, iy0, iy1 - iy0, IRON[0])
    rail = iy0 + (iy1 - iy0) * 3 // 10
    wall.rect(ix0, rail - 1, ix1 - ix0, 3, IRON[1])
    wall.hline(ix0, rail - 1, ix1 - ix0, IRON[3])
    wall.hline(ix0, rail + 1, ix1 - ix0, IRON[0])
    g.rect(ix0, iy0, ix1 - ix0, iy1 - iy0, (*GLASS_TINT, 14))
    ih = iy1 - iy0
    for off, wide, a in ((w // 3, 6, 70), (w * 3 // 4, 3, 50), (w // 3 + 10, 2, 40)):
        for yy in range(ih):
            for j in range(wide):
                xx = ix0 + off + (ih - yy) * 2 // 3 - ih // 2 + j
                if ix0 <= xx < ix1 and (xx + yy) % 5:
                    top.px(xx, iy0 + yy, (230, 240, 236, a))
    for yy in range(iy0, iy0 + 14):                               # soft warm light below the top rail
        for xx in range(ix0, ix1):
            if (xx * 3 + yy * 5) % 16 < (14 - (yy - iy0)) // 2:
                top.px(xx, yy, (*FLAME[3], 44))
    out = Pix(W, H)
    out.im.alpha_composite(g.im)
    out.im.alpha_composite(wall.im)
    out.im.alpha_composite(top.im)
    frame = Pix(w, h, seed=seed + 2)
    mitred_frame(frame, w, h, T)
    sx = w // 2 - 7                                               # brass escutcheon and a latch on the lower rail
    frame.rect(sx, h - T + 2, 14, 6, BRASS[2])
    frame.frame(sx, h - T + 2, 14, 6, BRASS[0])
    frame.hline(sx + 1, h - T + 3, 12, BRASS[4])
    frame.rect(sx + 6, h - T + 5, 2, 2, SHADOW)
    frame.rect(w - T + 2, h // 2 - 7, 6, 14, IRON[2])             # iron hinge strap on the right post
    frame.vline(w - T + 2, h // 2 - 7, 14, IRON[4])
    frame.px(w - T + 4, h // 2 - 4, BRASS[3])
    frame.px(w - T + 4, h // 2 + 3, BRASS[3])
    out.paste(frame, x0, y0)
    # nothing outside the case's rectangle
    res = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    res.paste(out.im.crop(box), (x0, y0))
    return res


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
}
