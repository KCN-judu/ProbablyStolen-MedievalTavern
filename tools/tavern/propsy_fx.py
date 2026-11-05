"""Fixtures of the bar redrawn on the shop's single viewpoint (see shopx_persp): the radio / music box that stands on the
bar at the right edge, the scribe's desk (`tape anim`), the abacus and the peg board of the wing.

Everything that stands on the counter is a cuboid seen from above and in front. `Cuboid` gives its three visible faces
in their own coordinates: the front face is upright and level, the top face is a trapezoid whose far edge is shorter
and nearer the horizon and whose side edges lean to the vanishing point, and the end that faces the middle of the room
shows as a narrow face whose upper and lower edges run to the vanishing point. Light comes from the upper left, so the top
is the brightest face, the left end is lit and the front is the middle tone.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image, ImageDraw

from palette import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import Color, Pix
from palette import LEATHER, LINEN
from props import arc, herb_bunch, onion_string, rope, sheet
from shopx_persp import VP, blend, ellipse_shadow, overlay_shadow

Pt = tuple[float, float]


@dataclass
class Cuboid:
    """A box on a horizontal surface. `x0..x1` is its near (front) edge, `y_top` the row of the front's upper edge,
    `h` the height of the front face, `s_far` how much smaller its far edge is. `vp` is the vanishing point in the
    coordinates of the canvas the box is drawn on."""
    x0: float
    x1: float
    y_top: float
    h: float
    s_far: float
    vp: Pt = VP

    def top_pt(self, u: float, x: float, up: float = 0.0) -> Pt:
        """Screen point on the top face at depth `u` (0 front, 1 back), near-edge x `x`, `up` pixels above the top."""
        s = 1 - (1 - self.s_far) * u
        return self.vp[0] + (x - self.vp[0]) * s, self.vp[1] + (self.y_top - up - self.vp[1]) * s

    def end_x(self) -> float:
        return self.x0 if self.x0 > self.vp[0] else self.x1

    def end_visible(self) -> bool:
        return self.x0 > self.vp[0] or self.x1 < self.vp[0]

    def top_poly(self) -> list[Pt]:
        return [self.top_pt(0, self.x0), self.top_pt(0, self.x1), self.top_pt(1, self.x1), self.top_pt(1, self.x0)]

    def end_poly(self) -> list[Pt]:
        xe = self.end_x()
        a, b = self.top_pt(0, xe), self.top_pt(1, xe)
        s = self.s_far
        return [a, b, (b[0], b[1] + self.h * s), (a[0], a[1] + self.h)]

    def front_poly(self) -> list[Pt]:
        return [(self.x0, self.y_top), (self.x1, self.y_top), (self.x1, self.y_top + self.h), (self.x0, self.y_top + self.h)]

    def footprint(self) -> list[Pt]:
        s = self.s_far
        a, b = self.top_pt(1, self.x0), self.top_pt(1, self.x1)
        return [(self.x0, self.y_top + self.h), (self.x1, self.y_top + self.h), (b[0], b[1] + self.h * s), (a[0], a[1] + self.h * s)]

    # --- inverse mappings: from a screen pixel to the face's own coordinates
    def top_uv(self, x: int, y: int) -> tuple[float, float]:
        s = (y - self.vp[1]) / (self.y_top - self.vp[1])
        return (1 - s) / (1 - self.s_far), self.vp[0] + (x - self.vp[0]) / s

    def end_uv(self, x: int, y: int) -> tuple[float, float]:
        s = (x - self.vp[0]) / (self.end_x() - self.vp[0])
        u = (1 - s) / (1 - self.s_far)
        ytop = self.vp[1] + (self.y_top - self.vp[1]) * s
        return u, (y - ytop) / (self.h * s)


def _mask(size: tuple[int, int], pts: list[Pt]) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for x, y in pts], fill=255)
    return m


def paint(p: Pix, pts: list[Pt], colour_at: Callable[[int, int], Color | None]) -> None:
    """Paints what `colour_at(x, y)` says on every pixel inside the polygon."""
    m = _mask((p.w, p.h), pts)
    bb = m.getbbox()
    if not bb:
        return
    for y in range(bb[1], bb[3]):
        for x in range(bb[0], bb[2]):
            if m.getpixel((x, y)):
                c = colour_at(x, y)
                if c is not None:
                    p.px(x, y, c)


def contact_shadow(p: Pix, box: Cuboid, shift: Pt, bbox: tuple[int, int, int, int], strength: float = 0.9,
                   alpha: int = 200) -> None:
    """A shadow on the surface under the box: its footprint pushed along `shift`, strongest at the box."""
    steps = (0.25, 0.5, 0.75, 1.0)
    masks = [_mask((p.w, p.h), [(x + shift[0] * t, y + shift[1] * t) for x, y in box.footprint()]) for t in steps]

    def level(x: int, y: int) -> float:
        for t, m in zip(steps, masks):
            if m.getpixel((x, y)):
                return strength * (1.15 - t)
        return 0.0

    overlay_shadow(p, *bbox, level, alpha=alpha)


def line_in_plane(p: Pix, a: Pt, b: Pt, c: Color) -> None:
    p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), c)


def wood_top(u: float, xn: float, x: int, y: int, ramp=WOOD) -> Color:
    """Grain on a top face: streaks that run along x in the plane (so they stay level on the screen)."""
    k = (int(u * 23) * 5 + int(xn / 9) * 3) % 7
    if k == 0:
        return ramp[3]
    if (int(xn) * 5 + y * 11) % 29 == 0:
        return ramp[2]
    return ramp[4] if u > 0.82 else ramp[3] if k > 3 else ramp[4]


# ---------------------------------------------------------------------------------------------- the radio


def pipe(p: Pix, x: int, base_y: int, height: int) -> None:
    """A brass organ pipe standing on a top face (foot ellipse, a mouth slot, a lit left edge)."""
    for dx in range(0, 7):                                   # its shadow, to the lower right
        blend(p, x + 4 + dx, base_y + (dx // 3), SHADOW, 0.55)
    p.ellipse(x, base_y - 2, 6, 3, BRASS[1])
    p.rect(x, base_y - height, 6, height - 1, BRASS[2])
    p.vline(x, base_y - height, height - 1, BRASS[4])
    p.vline(x + 1, base_y - height + 1, height - 2, BRASS[3])
    p.vline(x + 5, base_y - height, height - 1, BRASS[0])
    p.vline(x + 4, base_y - height, height - 1, BRASS[1])
    p.ellipse(x, base_y - height - 1, 6, 3, BRASS[3])        # the open end, seen from above
    p.ellipse(x + 1, base_y - height, 4, 2, SHADOW)
    p.hline(x + 1, base_y - height // 2, 4, SHADOW)          # the mouth
    p.hline(x + 1, base_y - height // 2 + 1, 4, BRASS[4])


def music_box_on_bar(p: Pix, box: Cuboid) -> None:
    """The music box: planks on the front with iron straps and a lock plate, a lit end with a crank, a lid with an inlay,
    three pipes and a horn."""
    front, top, end = box.front_poly(), box.top_poly(), box.end_poly()
    y0, h = round(box.y_top), round(box.h)
    # the front face: planks with seams, a lit upper edge, a dark foot
    def front_c(x: int, y: int) -> Color:
        v = (y - box.y_top) / box.h
        plank = int((x - box.x0) // 17)
        c = WOOD[2 + (plank % 3 == 1)]
        if v < 0.1:
            c = WOOD[4]
        elif v > 0.8:
            c = WOOD[1]
        if (x - box.x0) % 17 == 0:
            c = WOOD[0]
        elif (x * 7 + y * 3) % 23 == 0:
            c = WOOD[1]
        return c
    paint(p, front, front_c)
    p.hline(round(box.x0), round(box.y_top + box.h) - 1, round(box.x1 - box.x0) + 1, OAK[0])
    # iron straps over front, lid and end
    for sx in (box.x0 + 3, box.x0 + 60):
        p.rect(round(sx), y0 + 1, 5, h - 2, IRON[2])
        p.vline(round(sx), y0 + 1, h - 2, IRON[4])
        p.vline(round(sx) + 4, y0 + 1, h - 2, IRON[0])
        for ry in (y0 + 5, y0 + h - 6):
            p.px(round(sx) + 2, ry, BRASS[3])
    px0 = round(box.x0 + 13)                                  # the lock plate
    p.rect(px0, y0 + 9, 22, 12, BRASS[2])
    p.frame(px0, y0 + 9, 22, 12, BRASS[0])
    p.hline(px0 + 1, y0 + 10, 20, BRASS[4])
    p.rect(px0 + 10, y0 + 13, 2, 5, SHADOW)
    for cx in (px0 + 3, px0 + 18):
        p.px(cx, y0 + 18, BRASS[4])
    # the lit end face (it faces the room's middle), vertical boards
    def end_c(x: int, y: int) -> Color:
        u, v = box.end_uv(x, y)
        c = WOOD[4] if int(u * 5) % 2 else WOOD[3]
        if v < 0.1:
            c = WOOD[4]
        elif v > 0.82:
            c = WOOD[2]
        if abs(u * 5 - round(u * 5)) < 0.07:
            c = WOOD[0]
        return c
    paint(p, end, end_c)
    # the lid
    def top_c(x: int, y: int) -> Color:
        u, xn = box.top_uv(x, y)
        if u > 0.95:
            return OAK[0]
        c = wood_top(u, xn, x, y, PALE_WOOD)
        if abs(u - 0.5) < 0.04 and 0.1 < (xn - box.x0) / 12 < 11:
            return BRASS[2]                                    # an inlay line along the lid
        return c
    paint(p, top, top_c)
    line_in_plane(p, box.top_pt(0, box.x0), box.top_pt(1, box.x0), WOOD[4])       # lit left edge
    line_in_plane(p, box.top_pt(0, box.x0), box.top_pt(0, box.x1), PALE_WOOD[4])   # lit front lip
    # strap bands over the lid
    for sx in (box.x0 + 3, box.x0 + 60):
        for i in range(24):
            u = i / 23
            a, b = box.top_pt(u, sx), box.top_pt(u, sx + 5)
            p.hline(round(a[0]), round(a[1]), max(1, round(b[0] - a[0])), IRON[3])
    # the crank on the end face: a rod out to the left, an arm up, a wooden knob
    cx, cy = box.top_pt(0.5, box.x0)
    cy += h * 0.55 * (1 - (1 - box.s_far) * 0.5)
    cxi, cyi = round(cx), round(cy)
    p.rect(cxi - 9, cyi, 10, 2, IRON[3])
    p.hline(cxi - 9, cyi, 10, IRON[4])
    p.rect(cxi - 11, cyi - 8, 3, 11, IRON[3])
    p.vline(cxi - 11, cyi - 8, 11, IRON[4])
    p.ellipse(cxi - 13, cyi - 11, 7, 5, WOOD[3])
    p.hline(cxi - 12, cyi - 11, 5, PALE_WOOD[4])
    p.px(cxi, cyi, BRASS[4])
    # the pipes stand on the lid
    for i, ph in enumerate((13, 17, 10)):
        bx, by = box.top_pt(0.55, box.x0 + 16 + i * 9)
        pipe(p, round(bx) - 3, round(by), ph)
    # the horn rises from a collar at the back right and flares out of the picture
    hx, hy = box.top_pt(0.3, box.x0 + 42)
    hxi, hyi = round(hx), round(hy)
    p.rect(hxi - 4, hyi - 5, 9, 5, BRASS[2])
    p.hline(hxi - 4, hyi - 5, 9, BRASS[4])
    p.hline(hxi - 4, hyi - 1, 9, BRASS[0])
    for i in range(0, 40):
        r = 3 + i * 0.28
        yc = hyi - 6 - i * 0.55
        x = hxi + i
        for yy in range(round(yc - r), round(yc + r) + 1):
            u = (yy - yc) / max(r, 0.5)
            k = 4 if u < -0.6 else 3 if u < -0.1 else 2 if u < 0.35 else 1 if u < 0.8 else 0
            p.px(x, yy, BRASS[k])


# ---------------------------------------------------------------------------------------------- scribe's desk, abacus, pegboard


def scribe_frame(p: Pix, k: int) -> None:
    """A frame of `tape anim-Sheet` (53x36): the scribe's desk on the bar, a low oak box seen from above and in front with a
    parchment sheet on its top, an ink pot at its far corner and a quill that moves along the line being written. The
    sprite is drawn at about (668, 294) of the shop, so the vanishing point is at (-188, -144) of the cell."""
    vp = (-188.0, -144.0)
    box = Cuboid(5, 47, 22, 9, (11 + 144) / (22 + 144), vp)
    contact_shadow(p, box, (7, 2), (0, 0, 53, 36), 0.95, 190)
    # the end face (left): lit
    paint(p, box.end_poly(), lambda x, y: WOOD[4] if box.end_uv(x, y)[1] < 0.15 else WOOD[3] if (x + y) % 6 else WOOD[2])
    paint(p, box.front_poly(), lambda x, y: PALE_WOOD[4] if y == 22 else WOOD[3] if y < 25 else WOOD[2] if y < 29 else WOOD[1])
    p.hline(5, 30, 43, OAK[0])
    for sx in (5, 46):                                                     # iron corner straps on the front
        p.rect(sx, 22, 3, 9, IRON[2])
        p.vline(sx, 22, 9, IRON[4])
    for sx in range(11, 43, 9):
        p.vline(sx, 24, 5, WOOD[1])
    p.rect(22, 25, 10, 4, BRASS[2])
    p.hline(22, 25, 10, BRASS[4])
    p.px(26, 27, SHADOW)
    p.px(27, 27, SHADOW)

    def top_c(x: int, y: int) -> Color:
        u, xn = box.top_uv(x, y)
        on_sheet = 0.18 < u < 0.86 and 12 < xn < 38
        if on_sheet:
            c = PARCHMENT[3]
            if u < 0.3:
                c = PARCHMENT[2]
            elif xn < 15:
                c = PARCHMENT[4]
            return c
        return wood_top(u, xn, x, y, WOOD)
    paint(p, box.top_poly(), top_c)
    line_in_plane(p, box.top_pt(0, 5), box.top_pt(1, 5), WOOD[4])
    line_in_plane(p, box.top_pt(1, 5), box.top_pt(1, 47), OAK[0])
    line_in_plane(p, box.top_pt(0, 5), box.top_pt(0, 47), PALE_WOOD[4])
    for r, u in enumerate((0.62, 0.42)):                                   # lines of writing, growing frame by frame
        a = box.top_pt(u, 15)
        b = box.top_pt(u, 15 + 6 + k * 3 + (r == 0) * 2)
        for x in range(round(a[0]), round(b[0]), 2):
            p.px(x, round(a[1]), PARCHMENT[0])
    qa = box.top_pt(0.62, 15 + 6 + k * 3 + 2)                              # the quill lies in the plane, its tip on the line
    p.line(round(qa[0]), round(qa[1]), round(qa[0]) + 9, round(qa[1]) - 3, IRON[3])
    p.line(round(qa[0]) + 1, round(qa[1]), round(qa[0]) + 10, round(qa[1]) - 3, IRON[4])
    p.px(round(qa[0]), round(qa[1]), SHADOW)
    ix, iy = box.top_pt(0.45, 41)                                          # the ink pot, a short drum with an ellipse mouth
    ix, iy = round(ix), round(iy)
    p.ellipse(ix - 3, iy - 1, 7, 3, IRON[0])
    p.rect(ix - 3, iy - 4, 7, 4, IRON[2])
    p.vline(ix - 3, iy - 4, 4, IRON[4])
    p.vline(ix + 3, iy - 4, 4, IRON[0])
    p.ellipse(ix - 3, iy - 6, 7, 3, IRON[3])
    p.ellipse(ix - 2, iy - 5, 5, 2, SHADOW)


def abacus_frame(p: Pix, k: int) -> None:
    """A frame of `desk animations1` (36x22): a counting frame standing on the wing, seen from the front: an upright oak
    frame with four rods of beads (sliding one place per frame), a thin lit top, and the end that faces the room's middle
    as a narrow slanted face. The cell sits near (836, 346) of the shop."""
    vp = (480.0 - 836, 150.0 - 346)
    box = Cuboid(8, 36, 1, 20, (-2 - vp[1]) / (1 - vp[1]) + 0.0, vp)
    box.s_far = 0.989
    contact_shadow(p, box, (4, 2), (0, 0, 36, 22), 0.85, 190)
    paint(p, box.end_poly(), lambda x, y: WOOD[3] if (x + y) % 7 else WOOD[2])
    p.rect(8, 1, 28, 20, WOOD[2])
    p.bevel(8, 1, 28, 20, PALE_WOOD[4], OAK[0])
    p.hline(9, 2, 26, WOOD[3])
    p.vline(9, 2, 18, WOOD[3])
    paint(p, box.top_poly(), lambda x, y: PALE_WOOD[4] if y <= 1 else WOOD[4])
    p.rect(11, 4, 22, 14, OAK[1])                              # the inside of the frame, in shade
    p.hline(11, 4, 22, OAK[0])
    p.vline(11, 4, 14, OAK[0])
    cols = (WINE[3], BRASS[3], PALE_WOOD[3], (94, 130, 80))
    for r in range(4):
        y = 6 + r * 4
        p.hline(11, y + 1, 22, IRON[3])                        # the rod
        for i in range(8):
            pos = (i + k * (r + 1)) % 11
            bx = 12 + pos * 2 + (0 if pos < 5 else 3)
            p.rect(bx, y - 1, 2, 3, cols[r])
            p.px(bx, y - 1, PARCHMENT[4])
            p.px(bx + 1, y + 1, OAK[0])
    p.px(9, 3, BRASS[3])
    p.px(34, 3, BRASS[3])
    p.px(9, 19, BRASS[3])
    p.px(34, 19, BRASS[3])


def peg_strip_frame(p: Pix, k: int) -> None:
    """A frame of `desk animations4` (49x15): a scoring board lying flat on the wing, its top a foreshortened plane with a
    groove of peg holes; a brass peg steps along it. The cell sits near (870, 348) of the shop."""
    vp = (480.0 - 862, 150.0 - 346)
    box = Cuboid(37, 48, 10, 3, (5 - vp[1]) / (10 - vp[1]), vp)
    contact_shadow(p, box, (2, 2), (0, 0, 49, 15), 0.7, 170)
    paint(p, box.end_poly(), lambda x, y: WOOD[4] if y <= 10 else WOOD[2])
    paint(p, box.front_poly(), lambda x, y: PALE_WOOD[4] if y == 10 else WOOD[2] if y == 11 else OAK[0])
    paint(p, box.top_poly(), lambda x, y: wood_top(*box.top_uv(x, y), x, y, WOOD))
    line_in_plane(p, box.top_pt(0, 37), box.top_pt(1, 37), PALE_WOOD[4])
    line_in_plane(p, box.top_pt(1, 37), box.top_pt(1, 48), OAK[0])
    for r, u in enumerate((0.35, 0.7)):
        for i in range(3):
            hx, hy = box.top_pt(u, 39 + i * 3 + r)
            p.hline(round(hx), round(hy), 2, OAK[0])
    px_ = 39 + (k // 3) * 3
    bx, by = box.top_pt(0.7, px_)
    bx, by = round(bx), round(by)
    p.rect(bx, by - 4, 2, 5, BRASS[3])
    p.px(bx, by - 4, BRASS[4])
    p.px(bx + 1, by, BRASS[0])
    p.px(bx + 2, by, SHADOW)
    p.hline(bx, by - 5, 2, BRASS[4])


# ---------------------------------------------------------------------------------------------- the handbell


def handbell_layer() -> Image.Image:
    """`phone` (85x39 at 241,268): the brass handbell on a round oak tray, lying on the bar. The tray is an ellipse (a circle on
    the counter plane), its thickness shows below the near rim; the bell's lip is an ellipse of which only the front half is
    seen, its sides flare from a narrow crown, and the shadow falls to the lower right across the tray and the planks."""
    p = Pix(85, 39, seed=7)
    tcx, tcy, trx, try_ = 46, 29, 31, 8
    overlay_shadow(p, 0, 20, 85, 39, ellipse_shadow(tcx + 5, tcy + 5, trx + 6, try_ + 3, 0.95), alpha=200)
    for dy in (3, 2, 1):                                           # the tray's edge: its thickness below the near rim
        p.ellipse(tcx - trx, tcy - try_ + dy, 2 * trx + 1, 2 * try_ + 1, WOOD[0] if dy == 3 else WOOD[1])
    p.ellipse(tcx - trx, tcy - try_, 2 * trx + 1, 2 * try_ + 1, WOOD[4])      # the rim, lit on the upper left
    p.ellipse(tcx - trx + 2, tcy - try_ + 2, 2 * trx - 3, 2 * try_ - 3, WOOD[2])
    p.ellipse(tcx - trx + 3, tcy - try_ + 3, 2 * trx - 5, 2 * try_ - 4, WOOD[1])  # the dished floor
    p.dither(tcx - trx + 6, tcy - try_ + 4, 2 * trx - 12, 2 * try_ - 6, WOOD[2], 0.4)
    for x in range(tcx - trx + 4, tcx - 6):                       # a glint along the far-left rim
        p.px(x, tcy - round(try_ * math.sqrt(max(0.0, 1 - ((x - tcx) / trx) ** 2))), WOOD[4])
    cx, lip_y, lip_rx, lip_ry, crown = tcx + 1, tcy + 1, 14, 3, 9
    for yy in range(lip_y - 2, lip_y + 7):                         # the bell's own shadow on the tray, to the right
        for xx in range(cx - 4, cx + 26):
            if ((xx - cx - 9) / 15) ** 2 + ((yy - lip_y - 2) / 4.5) ** 2 < 1:
                blend(p, xx, yy, SHADOW, 0.6)
    for y in range(crown, lip_y + 1):                              # the body: flares toward the lip
        s = (y - crown) / (lip_y - crown)
        hw = 4 + (lip_rx - 4) * (0.5 * s ** 0.8 + 0.5 * s ** 3)             # a bell's profile: narrow shoulder, flared lip
        if s < 0.12:
            hw = 2 + 8 * s
        for x in range(round(cx - hw), round(cx + hw) + 1):
            t = (x - cx) / hw
            k = 4 if -0.75 < t < -0.5 else 3 if t < -0.05 else 2 if t < 0.4 else 1 if t < 0.8 else 0
            p.px(x, y, BRASS[k])
    for dx in range(-lip_rx, lip_rx + 1):                          # the lip: the front half of an ellipse, with a thick rim
        yb = lip_y + round(lip_ry * math.sqrt(1 - (dx / lip_rx) ** 2))
        t = dx / lip_rx
        for y in range(lip_y + 1, yb + 1):
            k = 4 if -0.75 < t < -0.5 else 3 if t < -0.05 else 2 if t < 0.4 else 1 if t < 0.8 else 0
            p.px(cx + dx, y, BRASS[max(0, k - 1)] if y == yb else BRASS[k])
        p.px(cx + dx, lip_y, BRASS[4] if t < 0.1 else BRASS[3])
        p.px(cx + dx, yb, BRASS[0])
    for yy, wide in ((lip_y - 7, 8), (lip_y - 11, 6)):             # engraved rings (arcs, as the body is round)
        for dx in range(-wide, wide + 1):
            p.px(cx + dx, yy + round(1.2 * (dx / wide) ** 2 * -1) + 1, BRASS[1])
    p.px(cx, lip_y + lip_ry - 1, BRASS[2])                         # the clapper's ball at the middle of the lip
    p.rect(cx - 2, 1, 5, crown, WOOD[3])                           # the turned handle on the crown
    p.vline(cx - 2, 1, crown, WOOD[4])
    p.vline(cx + 2, 1, crown, WOOD[0])
    p.hline(cx - 3, 3, 7, WOOD[1])
    p.hline(cx - 3, 6, 7, WOOD[1])
    p.rect(cx - 3, crown, 7, 1, BRASS[3])
    p.ellipse(cx - 2, 0, 5, 3, WOOD[4])
    out = Pix(960, 540)
    out.paste(p, 241, 268)
    return out.finish()


# ---------------------------------------------------------------------------------------------- assets


def radio_layer() -> Image.Image:
    """`radio` (77x327 at 883,0): ropes and herbs down from the beam to the music box on the bar at the right edge, which the
    picture's edge cuts. Drawn on the whole view so the box sits on the same perspective as the bar."""
    p = Pix(960, 540, seed=16)
    gx = 883
    for i, (rx, sag) in enumerate(((22, 4), (30, -3), (44, 3))):
        rope(p, arc(gx + rx - 3, 0, gx + rx + 2, 280, sag), 2 if i != 1 else 1, LINEN if i != 1 else LEATHER)
    herb_bunch(p, gx + 60, 80, 24, 9)
    onion_string(p, gx + 12, 120, 4)
    box = Cuboid(930, 1010, 293, 29, 0.91)
    contact_shadow(p, box, (-1, 6), (883, 0, 960, 327), 0.95, 200)
    music_box_on_bar(p, box)
    out = Image.new("RGBA", (960, 540), (0, 0, 0, 0))
    out.paste(p.finish().crop((883, 0, 960, 327)), (883, 0))
    return out


def _sheet(size: tuple[int, int], frames: int, x0: int, pitch: int, y0: int, fw: int, fh: int,
           draw: Callable[[Pix, int], None], seed: int) -> Image.Image:
    return sheet(size, frames, x0, pitch, y0, fw, fh, draw, seed)


ASSETS = {
}
