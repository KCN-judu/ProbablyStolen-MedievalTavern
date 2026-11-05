"""`reputation_box` (0,264)-(40,367): the landlord's letter box screwed onto the plank door at the left edge of the shop.

The door is a plane that recedes toward VP, so the box that sits on it is seen the way the door is: its outer face is
a parallelogram whose top and bottom edges run to VP, its upright edges stay upright, the end that faces the viewer
shows as a narrow side face (level edges), and its lid shows its top plane because the box is below the horizon.
Everything on the front (slot, label, hasp, padlock, bands) is placed in the face's own coordinates.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

from palette import BRASS, FLAME, IRON, LEATHER, OAK, PARCHMENT, SHADOW, WOOD
from pix import Color, Pix
from propsy_kit import cast_shadow, clamp_to_bbox, fill_poly, scale_to_vp
from shopx_persp import VP

BBOX = (0, 264, 40, 367)
XN = 9                       # where the near end of the outer face stands (the side face is x 0..XN)
S_END = 0.94                 # depth of the far end of the face, as a scale toward VP
Y_TOP, Y_BOT = 288, 364      # near edge of the outer face: top of the body, bottom
LID = 9                      # the lid band, near height


def face_pt(u: float, v: float) -> tuple[float, float]:
    """Screen point of the outer face at depth u (0 near, 1 far) and height v (0 top of body .. 1 bottom)."""
    s = 1 - (1 - S_END) * u
    return scale_to_vp((XN, Y_TOP + (Y_BOT - Y_TOP) * v), s)


def back_face(x: int, y: int) -> tuple[float, float]:
    s = (x - VP[0]) / (XN - VP[0])
    yw = VP[1] + (y - VP[1]) / s
    return (1 - s) / (1 - S_END), (yw - Y_TOP) / (Y_BOT - Y_TOP)


def draw() -> Image.Image:
    p = Pix(960, 540, seed=71)
    lid_top = Y_TOP - LID
    a_top = (0, lid_top)                                  # near face of the lid and of the body: x 0..XN
    far_x = scale_to_vp((XN, lid_top), S_END)
    top_far_left = scale_to_vp((0, lid_top), S_END)
    top_quad = [(0, lid_top), (XN, lid_top), (far_x[0], far_x[1]), (top_far_left[0], top_far_left[1])]
    footprint = [face_pt(0, 1), face_pt(1, 1), (face_pt(1, 1)[0] + 3, face_pt(1, 1)[1] + 2), (XN + 2, Y_BOT + 2)]
    # shadow on the planks: below and beyond the box, falling right and down
    cast_shadow(p, [(0, lid_top), (XN, lid_top), face_pt(1, 0), face_pt(1, 1), (XN, Y_BOT), (0, Y_BOT)],
                (6, 3), BBOX, 0.9, 210)

    # side face (the near end, turned to the viewer): level edges, lit by the lamp on the left
    def side_col(x: int, y: int) -> Color:
        if x == 0:
            return WOOD[3]
        if y == lid_top + 1 or y == Y_TOP - LID + LID:
            return OAK[0]
        c = WOOD[2] if y < Y_TOP else WOOD[1]
        if (x * 3 + y) % 7 == 0:
            c = WOOD[1]
        if x == XN - 1:
            c = OAK[0]
        return c

    fill_poly(p, [(0, lid_top), (XN, lid_top), (XN, Y_BOT), (0, Y_BOT)], side_col)
    # outer face
    quad = [face_pt(0, -LID / (Y_BOT - Y_TOP)), face_pt(1, -LID / (Y_BOT - Y_TOP)), face_pt(1, 1), face_pt(0, 1)]
    vlid = LID / (Y_BOT - Y_TOP)

    def face_col(x: int, y: int) -> Color | None:
        u, v = back_face(x, y)
        if v < -vlid:
            return None
        if v < 0:                                         # the lid band: overhangs, pale lit lower edge
            lvl = (v + vlid) / vlid
            if lvl < 0.15:
                return WOOD[4]
            if lvl > 0.82:
                return OAK[0]
            return WOOD[3] if u < 0.6 else WOOD[2]
        c = WOOD[2] if u < 0.55 else WOOD[1]
        if v < 0.05:
            c = OAK[0]                                    # shadow under the lid
        if int(u * 16) % 5 == 0 and (int(v * 70) % 9):
            pass
        if int(v * 76) % 19 == 0:
            c = WOOD[1]
        if int(u * 40 + 3) % 13 == 0:
            c = WOOD[0] if u > 0.15 else c                # a plank seam in the face
        if u < 0.04:
            c = WOOD[4]                                   # lit near edge
        if u > 0.96:
            c = OAK[0]
        if v > 0.97:
            c = OAK[0]
        return c

    fill_poly(p, quad, face_col)
    # iron bands across the face (vertical in the face), with rivets
    for u0, w in ((0.08, 0.1), (0.8, 0.1)):
        for v_i in range(0, 77):
            v = v_i / 76
            for k in range(0, 100):
                u = u0 + w * k / 99
                x, y = face_pt(u, v)
                p.px(round(x), round(y), IRON[2] if k > 12 else IRON[4])
    for u in (0.13, 0.85):
        for v in (0.1, 0.5, 0.92):
            x, y = face_pt(u, v)
            p.px(round(x), round(y), BRASS[3])
    # brass slot plate and the slit, in the face
    def box_in_face(u0, u1, v0, v1, c, edge=None):
        pts = [face_pt(u0, v0), face_pt(u1, v0), face_pt(u1, v1), face_pt(u0, v1)]
        fill_poly(p, pts, lambda x, y: c)
        if edge:
            p.line(*map(round, pts[0] + pts[1]), edge[0])
            p.line(*map(round, pts[3] + pts[2]), edge[1])

    box_in_face(0.28, 0.76, 0.2, 0.3, BRASS[2], (BRASS[4], BRASS[0]))
    box_in_face(0.34, 0.7, 0.235, 0.255, SHADOW)
    box_in_face(0.34, 0.7, 0.255, 0.262, FLAME[1])
    # label: parchment card with ink lines
    box_in_face(0.3, 0.74, 0.4, 0.58, PARCHMENT[3], (PARCHMENT[4], PARCHMENT[1]))
    for i in range(4):
        v = 0.44 + i * 0.035
        a, b = face_pt(0.35, v), face_pt(0.65 - (i % 2) * 0.1, v)
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), PARCHMENT[0])
    # hasp and padlock
    box_in_face(0.4, 0.62, 0.66, 0.74, IRON[2], (IRON[4], IRON[0]))
    px0, py0 = face_pt(0.51, 0.77)
    lx, ly = round(px0), round(py0)
    p.frame(lx - 2, ly - 4, 5, 5, IRON[3])
    p.rect(lx - 3, ly, 7, 6, BRASS[2])
    p.hline(lx - 3, ly, 7, BRASS[4])
    p.hline(lx - 3, ly + 5, 7, BRASS[0])
    p.px(lx, ly + 2, SHADOW)
    # top plane of the lid, with iron hinge leaves at the back (door side)
    def top_col(x: int, y: int) -> Color:
        c = WOOD[4] if (x * 2 + y) % 9 else PALE_WOOD_TOP
        return c

    fill_poly(p, top_quad, top_col)
    p.line(0, lid_top, XN, lid_top, WOOD[4])
    p.line(XN, lid_top, round(far_x[0]), round(far_x[1]), OAK[0])
    for t in (0.2, 0.7):
        a = (top_far_left[0] + (far_x[0] - top_far_left[0]) * t, top_far_left[1] + (far_x[1] - top_far_left[1]) * t)
        p.rect(round(a[0]) - 1, round(a[1]), 3, 2, IRON[3])
    return clamp_to_bbox(p.finish(), BBOX)


PALE_WOOD_TOP: Color = (173, 136, 86)

ASSETS: Mapping[str, Callable[[], Image.Image]] = {}      # superseded by doo_box
