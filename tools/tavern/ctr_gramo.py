"""`tape anim-Sheet` (6 cells of 53x36 at (2 + 55k, 2)): the gramophone on the bar.

A walnut cabinet on four turned feet with its hinged lid raised, a shellac record on the turntable (concentric grooves
that glint, a wine-red paper label whose mark turns), a tonearm with a needle that rocks in and out as the off-centre
record turns, a crank on the lit left end and a brass horn on a bracket. Everything is on the counter's single
perspective (vanishing point at (-190, -144) of the cell): the top is a slanted plane, the left end faces the middle of the
room, and a contact shadow falls to the right. One revolution is six frames, so the sheet loops.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from ctr_kit import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD, Cuboid, Plane, fill, fx, horn, line, mix, shadow, tube_tone
from palette import WINE
from pix import Color, Pix, rgb
from props import sheet

VP = (-190.0, -144.0)
DEPTH = 24.0                                    # world depth of the cabinet top, in near-edge pixels
X0, X1, Y_TOP, H = 13, 40, 22, 9
BOX = Cuboid(X0, X1, Y_TOP, H, (13 + 144) / (Y_TOP + 144), VP)
PL = Plane(BOX, DEPTH)
CX, CZ, R = 24.0, 10.5, 8.8                     # record centre and radius (plane units)
PIV = (36.5, 19.0)                              # the tonearm pivot
FRAMES = 6

SHELLAC = (rgb("#0c0a10"), rgb("#17131d"), rgb("#241e2c"), rgb("#3a3144"), rgb("#6a5f78"))


def cabinet(p: Pix) -> None:
    base = Cuboid(X0 + 1, X1 - 1, Y_TOP + H + 3, 0, (13 + 144) / (Y_TOP + H + 3 + 144), VP)
    shadow(p, base.footprint(), shift=(7, 1), spread=4, strength=0.95, alpha=200)
    # feet: turned bun feet at the two near corners, plus the far-right one peeking behind
    for fx_, w in ((X0 + 2, 4), (X1 - 6, 4)):
        p.rect(fx_, Y_TOP + H, w, 3, WOOD[1])
        p.rect(fx_, Y_TOP + H, 2, 3, WOOD[3])
        p.hline(fx_ + 1, Y_TOP + H + 3, w - 1, SHADOW)
        p.px(fx_, Y_TOP + H, PALE_WOOD[3])
    # the wooden body
    fx.wood_box(p, BOX, WOOD, seed=71, knots=0.5, nails=False, joints=False, wear_amount=0.2)
    def end_at(x: int, y: int) -> Color:                      # the lit left end: planks whose grain runs into the depth
        u, v = BOX.end_uv(x, y)
        if v < 0.14:
            return PALE_WOOD[3]
        if v > 0.86:
            return WOOD[1]
        c = WOOD[4] if u < 0.06 else WOOD[3]
        if int(v * 9) % 3 == 0 and (x + y * 2) % 5:
            c = WOOD[2] if c == WOOD[3] else WOOD[3]
        return c
    fill(p, BOX.end_poly(), end_at)
    # front: a moulded panel with a brass knob and a keyhole plate, a lit top edge
    p.hline(X0, Y_TOP, X1 - X0, PALE_WOOD[4])
    p.hline(X0 + 1, Y_TOP + 1, X1 - X0 - 2, WOOD[4])
    p.frame(X0 + 3, Y_TOP + 3, X1 - X0 - 6, H - 5, OAK[0])
    p.hline(X0 + 4, Y_TOP + 4, X1 - X0 - 8, WOOD[4])
    p.vline(X0 + 4, Y_TOP + 4, H - 7, WOOD[4])
    p.hline(X0, Y_TOP + H - 1, X1 - X0, OAK[0])
    fx.brass_fill(p, (X0 + 12, Y_TOP + 4, 3, 3), profile="dome", tarnish=0.2, seed=3)          # knob
    fx.brass_fill(p, (X0 + 17, Y_TOP + 3, 4, 4), profile="plate", tarnish=0.2, seed=4)          # key plate
    p.px(X0 + 18, Y_TOP + 4, SHADOW)
    p.px(X0 + 18, Y_TOP + 5, SHADOW)
    # iron corner straps on the front corners
    for sx in (X0, X1 - 2):
        fx.iron_fill(p, (sx, Y_TOP + 1, 2, H - 1), hammer=0.1, rust=0.1, scratches=0.0, seed=sx)
    # lit top edge along the left end
    a, b = BOX.top_pt(0, X0), BOX.top_pt(1, X0)
    line(p, a, b, PALE_WOOD[4])


def lid(p: Pix) -> None:
    """The lid, hinged at the back edge and standing up: we see its inside (a lining of dark wood with a printed paper)."""
    bl, br = BOX.top_pt(1, X0 + 1), BOX.top_pt(1, X1 - 1)
    hgt = 10
    poly = [(bl[0], bl[1]), (br[0], br[1]), (br[0] - 1, br[1] - hgt), (bl[0] + 1, bl[1] - hgt)]

    def at(x: int, y: int) -> Color:
        v = (bl[1] - y) / hgt
        c = WOOD[2] if v < 0.9 else WOOD[4]
        if (x * 3 + y * 5) % 11 == 0:
            c = WOOD[1]
        if x < bl[0] + 2:
            c = WOOD[3]
        return c
    fill(p, poly, at)
    p.hline(round(bl[0]) + 1, round(bl[1] - hgt), round(br[0] - bl[0]) - 2, PALE_WOOD[3])      # lit top edge
    p.hline(round(bl[0]), round(bl[1]) - 1, round(br[0] - bl[0]), OAK[0])                     # dark crack at the hinge line
    # a paper maker's label tacked to the lining
    lx = round(bl[0]) + 5
    p.rect(lx, round(bl[1]) - 8, 10, 5, PARCHMENT[2])
    p.hline(lx, round(bl[1]) - 8, 10, PARCHMENT[3])
    p.hline(lx, round(bl[1]) - 4, 10, PARCHMENT[1])
    for i, ww in enumerate((6, 4)):
        p.hline(lx + 2, round(bl[1]) - 7 + i * 2, ww, WINE[2])
    p.px(lx, round(bl[1]) - 8, IRON[3])
    p.px(lx + 9, round(bl[1]) - 4, IRON[3])
    # two brass hinges
    for hx in (bl[0] + 3, br[0] - 6):
        p.rect(round(hx), round(bl[1]) - 3, 3, 2, BRASS[2])
        p.hline(round(hx), round(bl[1]) - 3, 3, BRASS[3])
        p.px(round(hx) + 2, round(bl[1]) - 2, BRASS[0])
    # a prop stick keeping the lid open
    line(p, (br[0] - 3, br[1] - 8), (br[0] - 6, br[1] + 1), IRON[3])


def record(p: Pix, k: int) -> None:
    """Turntable, record, label and groove glints for frame k (one revolution in `FRAMES` frames)."""
    spin = 2 * math.pi * k / FRAMES
    # the platter rim under the record (a thin brass-edged disc)
    def at(xn: float, pz: float, x: int, y: int) -> Color | None:
        dx, dz = xn - CX, pz - CZ
        r = math.hypot(dx, dz)
        if r > R + 1.0:
            return None
        if r > R:
            return IRON[2] if dx < 0 else IRON[1]                 # the platter edge
        th = math.atan2(dz, dx) - spin
        if r < 0.9:
            return BRASS[4]                                        # spindle
        if r < 3.7:                                                # the paper label
            c = WINE[3] if r > 2.8 or abs(math.sin(2 * th)) > 0.12 else WINE[2]
            if r > 3.2:
                c = PARCHMENT[3]                                   # a pale rim ring on the label
            mark = math.cos(th) > 0.8 and 1.2 < r < 3.0
            if mark:
                c = PARCHMENT[4]
            elif dx + dz * 0 < -1.2 and r > 2.2:
                c = mix(c[:3], (255, 255, 255), 0.18) if False else c
            return c
        if r < 4.3:
            return SHELLAC[1]                                      # run-in ring
        # grooves: rings of alternating tone; a broad sheen at the upper left, and glints that hop with the frame
        ring = int(r * 2.2)
        sheen = max(0.0, math.cos(math.atan2(dz, dx) - 3.8)) ** 3      # fixed light, upper left
        v = 1 + (ring % 3 == 0) + (1 if sheen > 0.35 and ring % 2 == 0 else 0) + (1 if sheen > 0.7 else 0)
        glint = ((ring * 7 + int(th * 4 / math.pi) * 5 + k * 3) % 23) == 0
        if glint and sheen > 0.3:
            v = 4
        if r > R - 0.8:
            v = 2 if dx < 0 else 1                                  # the bevelled edge
        return SHELLAC[min(4, v)]
    PL.paint(p, at)


def tonearm(p: Pix, k: int) -> None:
    """The arm rocks inward and back once per revolution (the record is a little off centre); it casts a shadow on the disc."""
    reach = 0.7 + 0.2 * math.sin(2 * math.pi * k / FRAMES - 0.7)
    d = math.hypot(PIV[0] - CX, PIV[1] - CZ)
    tip = (CX + (PIV[0] - CX) / d * R * reach, CZ + (PIV[1] - CZ) / d * R * reach)
    a = PL.pt(PIV[0], PIV[1], 2.5)
    b = PL.pt(tip[0], tip[1], 0.8)
    sa, sb = PL.pt(PIV[0] + 1.5, PIV[1] - 0.8), PL.pt(tip[0] + 1.5, tip[1] - 1.5)
    line(p, (sa[0], sa[1] + 1), (sb[0], sb[1] + 1), SHELLAC[0])
    pa = PL.pt(PIV[0], PIV[1])
    px_, py_ = round(pa[0]), round(pa[1])
    p.rect(px_ - 2, py_ - 3, 5, 3, BRASS[2])               # the pivot's brass drum
    p.vline(px_ - 2, py_ - 3, 3, BRASS[4])
    p.vline(px_ + 2, py_ - 3, 3, BRASS[0])
    p.hline(px_ - 2, py_ - 4, 5, BRASS[3])
    p.px(px_ - 1, py_ - 4, BRASS[4])
    line(p, (a[0], a[1]), (b[0], b[1] - 1), BRASS[4])      # the arm: a lit brass line over its own shade
    line(p, (a[0], a[1] + 1), (b[0], b[1]), BRASS[1])
    tx, ty = a[0] + 3, a[1] - 1                            # counterweight behind the pivot
    p.rect(round(tx), round(ty) - 1, 2, 2, IRON[3])
    p.px(round(tx), round(ty) - 1, IRON[4])
    p.rect(round(b[0]) - 1, round(b[1]) - 2, 3, 2, BRASS[3])   # head shell and needle
    p.px(round(b[0]) - 1, round(b[1]) - 2, BRASS[4])
    p.px(round(b[0]), round(b[1]), SHADOW)


def horn_and_bracket(p: Pix) -> None:
    neck = (31.0, 16.0)
    mouth = (45.0, 7.5)
    # an iron stand behind the cabinet: a rod from a small foot on the counter up to a ring that cradles the horn's belly
    fxp, fyp = 39, 19
    p.hline(fxp - 2, fyp + 1, 5, SHADOW)
    p.hline(fxp - 2, fyp, 5, IRON[2])
    p.px(fxp - 2, fyp, IRON[4])
    p.vline(fxp, fyp - 8, 8, IRON[3])
    p.vline(fxp - 1, fyp - 8, 8, IRON[4])
    horn(p, neck, mouth, 1.7, 7.2, k=2.2, mouth_rx=3.4, seed=3)
    p.rect(fxp - 2, fyp - 9, 5, 2, BRASS[3])                       # the ring that holds the horn
    p.hline(fxp - 2, fyp - 9, 5, BRASS[4])
    p.hline(fxp - 2, fyp - 8, 5, BRASS[0])
    # the collar where the neck leaves the deck (a brass ring with a dark joint)
    cx, cy = round(neck[0]), round(neck[1])
    p.rect(cx - 2, cy - 1, 4, 4, BRASS[3])
    p.vline(cx - 2, cy - 1, 4, BRASS[4])
    p.vline(cx + 1, cy - 1, 4, BRASS[0])
    p.hline(cx - 2, cy + 3, 4, SHADOW)


def crank(p: Pix) -> None:
    """A crank on the lit left end: a short axle out of the end face, an arm hanging down, a small wooden knob."""
    a = BOX.top_pt(0.0, X0)
    e = BOX.top_pt(1.0, X0)
    cx = round((a[0] + e[0]) / 2) - 1
    cy = round((a[1] + e[1]) / 2) + 4
    p.hline(cx - 3, cy, 4, IRON[3])
    p.hline(cx - 3, cy + 1, 4, IRON[1])
    p.rect(cx - 4, cy - 1, 2, 5, BRASS[3])
    p.vline(cx - 4, cy - 1, 5, BRASS[4])
    p.px(cx - 3, cy + 3, BRASS[0])
    p.rect(cx - 5, cy + 4, 3, 2, WOOD[4])
    p.px(cx - 5, cy + 4, PALE_WOOD[4])
    p.hline(cx - 5, cy + 5, 3, WOOD[1])


def frame(p: Pix, k: int) -> None:
    cabinet(p)
    lid(p)
    horn_and_bracket(p)
    # the horn must stand behind the deck items; cabinet top redraw order: record then arm
    record(p, k)
    tonearm(p, k)
    crank(p)


def draw() -> Image.Image:
    return sheet((332, 40), FRAMES, 2, 55, 2, 53, 36, frame, 26)


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"tape anim-Sheet.332x40.png": draw}
