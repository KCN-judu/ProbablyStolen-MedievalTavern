"""`negociation_tablet` (649,177)-(779,288): a writing tablet lying flat on the bar, drawn in the shop's perspective.

An oak slab with a parchment writing field in a raised frame; its top face is foreshortened toward VP, its left end
(the side that faces the viewer's middle) and its near edge show their thickness, a quill, an inkwell and a wax seal lie
on it, and a soft shadow falls on the planks to its right and below. The writing field stays plain.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

from palette import BRASS, IRON, NAVY, PALE_WOOD, PARCHMENT, WINE, WOOD, OAK
from pix import Color, Pix
from propsy_kit import cast_shadow, clamp_to_bbox, fill_poly, scale_to_vp
from shopx_persp import VP

BBOX = (649, 177, 779, 288)
Y_NEAR, Y_BOT, Y_FAR = 278, 284, 269          # near top edge, near bottom edge, far top edge of the slab
XL, XR = 672, 766                              # near corners
S_FAR = (Y_FAR - VP[1]) / (Y_NEAR - VP[1])     # scale of the far edge toward VP


def top_pt(u: float, xn: float, lift: float = 0.0) -> tuple[float, float]:
    """Screen point of the slab's top at depth u (0 near, 1 far) and near-edge x `xn`, `lift` px above the top."""
    s = 1 - (1 - S_FAR) * u
    x, y = scale_to_vp((xn, Y_NEAR), s)
    return x, y - lift * s


def back(x: int, y: int) -> tuple[float, float]:
    """Slab coordinates (u, xn) of a screen pixel of the top face."""
    s = (y - VP[1]) / (Y_NEAR - VP[1])
    return (1 - s) / (1 - S_FAR), VP[0] + (x - VP[0]) / s


def draw() -> Image.Image:
    p = Pix(960, 540, seed=61)
    far_l, far_r = top_pt(1, XL), top_pt(1, XR)
    top = [(XL, Y_NEAR), (XR, Y_NEAR), far_r, far_l]
    side = [(XL, Y_NEAR), far_l, (far_l[0], far_l[1] + 6 * S_FAR), (XL, Y_BOT)]
    front = [(XL, Y_NEAR), (XR, Y_NEAR), (XR, Y_BOT), (XL, Y_BOT)]
    base = [(XL, Y_BOT), (XR, Y_BOT), (far_r[0], far_r[1] + 6 * S_FAR), (far_l[0], far_l[1] + 6 * S_FAR)]
    cast_shadow(p, base, (9, 3), BBOX, 0.95, 215)

    def front_col(x: int, y: int) -> Color:               # planked edge, lit lip on top, dark foot
        if y == Y_NEAR:
            return PALE_WOOD[4]
        if y == Y_BOT - 1:
            return OAK[0]
        c = WOOD[2] if y == Y_NEAR + 1 else WOOD[1] if y >= Y_BOT - 2 else WOOD[2]
        if (x - XL) % 31 == 0:
            c = OAK[0]
        if (x * 5 + y * 3) % 17 == 0:
            c = WOOD[1]
        if abs(x - (XL + XR) // 2) < 5 and Y_NEAR + 1 < y < Y_BOT - 1:
            c = BRASS[2] if y < Y_BOT - 2 else BRASS[0]   # a brass clasp on the front
        if x in (XL, XL + 1):
            c = WOOD[3]
        return c

    fill_poly(p, front, front_col)
    fill_poly(p, side, lambda x, y: WOOD[3] if y < Y_NEAR - 3 + (XL - x) // 2 + 3 else WOOD[2])
    p.line(XL, Y_BOT - 1, round(side[2][0]), round(side[2][1]) - 1, OAK[0])

    def top_col(x: int, y: int) -> Color:
        u, xn = back(x, y)
        du = u
        if xn < XL + 3 or xn > XR - 3 or du < 0.0 or du > 0.97 or u > 0.9 or u < 0.1:
            # the raised frame: oak, grain along the long side, lit near edge, dark far edge
            if u < 0.1:
                return PALE_WOOD[4] if y == Y_NEAR - 1 else WOOD[4]
            if xn < XL + 3:
                return WOOD[4] if xn < XL + 1.5 else WOOD[3]
            if xn > XR - 3:
                return WOOD[2]
            return WOOD[3] if (int(xn) // 7 + y) % 5 else WOOD[2]
        # the writing field: parchment, shaded where the far frame overshadows it
        c = PARCHMENT[3]
        if u > 0.83:
            c = PARCHMENT[2]
        if xn < XL + 6:
            c = PARCHMENT[4]
        if (x * 7 + y * 13) % 29 == 0:
            c = PARCHMENT[2]
        if xn > XR - 8:
            c = PARCHMENT[2]
        return c

    fill_poly(p, top, top_col)
    for cx in (XL + 1, XR - 3):                              # brass corner pieces at the near corners
        p.rect(cx, Y_NEAR - 1, 3, 2, BRASS[3])
        p.px(cx, Y_NEAR - 1, BRASS[4])
    for xn in (XL + 1, XR - 2):                              # and at the far corners
        x, y = top_pt(0.97, xn)
        p.rect(round(x) - 1, round(y), 3, 1, BRASS[2])
    p.line(XL, Y_NEAR, round(far_l[0]), round(far_l[1]), PALE_WOOD[4])   # lit left edge of the top
    # wax seal: a flat disc on the field, left
    sx, sy = top_pt(0.45, 692)
    p.ellipse(round(sx) - 3, round(sy) - 1, 7, 3, WINE[1])
    p.ellipse(round(sx) - 3, round(sy) - 1, 6, 2, WINE[3])
    p.px(round(sx) - 2, round(sy) - 1, WINE[4])
    # quill lying across the field at an angle (a line in the plane), its shadow beside it
    qa, qb = top_pt(0.75, 706), top_pt(0.2, 744)
    p.line(round(qa[0]) + 1, round(qa[1]) + 1, round(qb[0]) + 1, round(qb[1]) + 1, PARCHMENT[1])
    p.line(round(qa[0]), round(qa[1]), round(qb[0]), round(qb[1]), PARCHMENT[4])
    p.px(round(qb[0]) - 1, round(qb[1]), PARCHMENT[2])
    p.px(round(qa[0]) - 1, round(qa[1]) + 1, IRON[1])        # the nib
    # inkwell at the far right corner of the frame: a short drum seen from above
    ix, iy = top_pt(0.55, 753)
    ix, iy = round(ix), round(iy)
    p.ellipse(ix - 4, iy - 1, 10, 4, IRON[0])                # its foot on the frame
    p.rect(ix - 4, iy - 4, 9, 4, NAVY[1])
    p.vline(ix - 4, iy - 4, 4, NAVY[3])
    p.vline(ix + 4, iy - 4, 4, NAVY[0])
    p.ellipse(ix - 4, iy - 6, 9, 4, IRON[3])                 # the rim
    p.ellipse(ix - 2, iy - 5, 5, 2, SHADOW_INK)
    p.px(ix - 3, iy - 5, IRON[4])
    return clamp_to_bbox(p.finish(), BBOX)


SHADOW_INK: Color = (14, 10, 22)

ASSETS: Mapping[str, Callable[[], Image.Image]] = {}      # superseded by tab_slate
