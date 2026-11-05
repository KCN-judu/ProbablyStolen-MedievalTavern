"""`radio` (883,0)-(960,327): the counting-house document chest at the right end of the bar, and what hangs above it.

The game's radio becomes the tavern's counterpart: the day's news no longer comes out of a box but is cried by the town
crier's handbell and written in the ledger, so above the chest hang the crier's bell on its cord, a bell-pull with a wine
tassel, dried herbs and a string of onions, each tied to the beam or a peg; on the chest lie the ledger, a quill, a stick
of sealing wax and a wax seal. The chest is oak with iron straps and a brass lock, a Cuboid in the shop's perspective that
rests on the bar with a contact shadow on the planks (the picture's edge cuts it at the right).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from ctr_kit import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD, Cuboid, Plane, fill, fx, line, mix, slab
from palette import LEATHER, LINEN, MOSS, WINE
from pix import Color, Pix
from props import herb_bunch, onion_string

BBOX = (883, 0, 960, 327)
BOX = Cuboid(924, 1010, 296, 28, 0.915)
PL = Plane(BOX, 36.0)
PX = (BOX.x0, BOX.x1)


def hanging(p: Pix) -> None:
    """Things tied to the beam: each cord starts at the top edge (the beam) and ends in the thing it carries."""
    # the crier's handbell on a cord, with a wooden toggle where the cord is looped over the beam peg
    cx = 920
    fx.rope(p, [(cx, 0), (cx, 112)], 3, seed=3)
    bell_top = 112
    fx.wall_shadow(p, fx.ellipse(cx + 1, bell_top + 11, 8, 12), (3, 4), alpha=130)
    for y in range(bell_top, bell_top + 21):                      # a bell's profile: shoulder, waist, flared lip
        t = (y - bell_top) / 20
        hw = 3 + 8 * (0.35 * t + 0.65 * t ** 3) + (1 if t > 0.9 else 0)
        for x in range(round(cx - hw), round(cx + hw) + 1):
            u = (x - cx) / hw
            k = 4 if -0.7 < u < -0.4 else 3 if u < 0.0 else 2 if u < 0.45 else 1 if u < 0.8 else 0
            p.px(x, y, BRASS[k])
    for x in range(cx - 11, cx + 12):                             # lip rim
        p.px(x, bell_top + 20, BRASS[0])
        p.px(x, bell_top + 19, BRASS[3] if x < cx + 2 else BRASS[1])
    for yy, ww in ((bell_top + 7, 5), (bell_top + 12, 7)):        # engraved rings
        for x in range(cx - ww, cx + ww + 1):
            p.px(x, yy, BRASS[1])
    p.rect(cx - 1, bell_top + 21, 3, 3, BRASS[2])                  # clapper
    p.px(cx - 1, bell_top + 21, BRASS[4])
    p.ellipse(cx - 2, bell_top - 3, 5, 4, BRASS[3])                # crown loop
    p.px(cx - 1, bell_top - 3, BRASS[4])
    # a bell-pull: a thick cord ending in a wine-red tassel
    bx = 897
    fx.rope(p, fx.hang_curve((bx, 0), (bx + 3, 150), 3), 4, seed=5, knots=(0.5,))
    ty = 150
    fx.wall_shadow(p, [(bx - 2, ty), (bx + 8, ty), (bx + 9, ty + 22), (bx - 3, ty + 22)], (2, 3), alpha=120)
    p.rect(bx + 1, ty - 1, 5, 5, WOOD[3])                          # turned wooden head
    p.vline(bx + 1, ty - 1, 5, WOOD[4])
    p.vline(bx + 5, ty - 1, 5, WOOD[1])
    p.hline(bx + 1, ty + 1, 5, WOOD[1])
    fx.cloth_fill(p, [(bx - 1, ty + 4), (bx + 8, ty + 4), (bx + 9, ty + 22), (bx - 2, ty + 22)], WINE, "wool", folds=3, seed=9)
    for i in range(0, 11, 2):
        p.px(bx - 1 + i, ty + 22, WINE[1])
    # herbs and an onion string
    fx.rope(p, [(937, 0), (937, 40)], 2, seed=7)
    herb_bunch(p, 937, 40, 30, 11)
    fx.rope(p, [(891, 18), (891, 50)], 2, seed=8)
    onion_string(p, 891, 50, 4)


def chest(p: Pix) -> None:
    shadow_shape = BOX.footprint()
    fx.contact_shadow(p, shadow_shape, shift=(5, 5), spread=5, strength=0.95, alpha=205, squash=0.7)
    regions = fx.wood_box(p, BOX, OAK_PLANKS, seed=81, end_light=0.2, knots=1.0, wear_amount=0.45)
    x0, x1, yt, h = BOX.x0, BOX.x1, BOX.y_top, BOX.h
    fy = round(yt)
    # the lid line: a dark seam with a lit lip above it, and the lid's own lit top edge
    p.hline(x0, fy, 60, PALE_WOOD[4])
    p.hline(x0, fy + 7, 60, OAK[0])
    p.hline(x0, fy + 8, 60, WOOD[4])
    p.hline(x0, fy + h - 1, 60, OAK[0])                       # dark foot line where the chest meets the planks
    # iron straps on the front, wrapping over the top at the left corner and at the right
    for sx in (926, 957):
        fx.iron_fill(p, (sx, fy, 5, h - 1), hammer=0.4, rust=0.3, rivets=0, seed=sx)
        for ry in (fy + 4, fy + 12, fy + 20):
            fx.rivet(p, sx + 2, ry, 1, BRASS)
    # a lower iron rim
    fx.iron_fill(p, (x0, fy + h - 5, 36, 4), hammer=0.2, rust=0.4, seed=11)
    # left end face (lit): two vertical straps that follow the end plane
    xe = BOX.end_x()
    for u0, u1 in ((0.04, 0.12), (0.84, 0.92)):
        a0, a1 = BOX.top_pt(u0, xe), BOX.top_pt(u1, xe)
        s0, s1 = 1 - (1 - BOX.s_far) * u0, 1 - (1 - BOX.s_far) * u1
        poly = [a0, a1, (a1[0], a1[1] + h * s1), (a0[0], a0[1] + h * s0)]
        fx.iron_fill(p, poly, hammer=0.4, rust=0.3, seed=int(u0 * 100))
        mid = ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2)
        for k in (0.2, 0.55, 0.85):
            fx.rivet(p, round(mid[0]), round(mid[1] + h * (s0 + s1) / 2 * k), 1, BRASS)
    # top plane straps running front to back
    for sx in (926, 957):
        fx.iron_fill(p, [PL.pt(sx, 0), PL.pt(sx + 5, 0), PL.pt(sx + 5, 36), PL.pt(sx, 36)], hammer=0.3, rust=0.3, seed=sx + 1)
    # the hasp and the brass lock
    fx.iron_fill(p, (941, fy, 8, 9), hammer=0.3, rust=0.2, seed=21)
    fx.brass_fill(p, (938, fy + 8, 14, 12), profile="plate", tarnish=0.4, studs=0, seed=22)
    p.frame(938, fy + 8, 14, 12, BRASS[0])
    p.px(938, fy + 8, BRASS[4])
    p.rect(944, fy + 11, 3, 3, SHADOW)                        # keyhole: a round hole and a slot
    p.rect(945, fy + 14, 1, 3, SHADOW)
    for rx, ry in ((940, fy + 10), (950, fy + 10), (940, fy + 18), (950, fy + 18)):
        fx.rivet(p, rx, ry, 1, IRON)
    _ = regions


OAK_PLANKS = (WOOD[0], WOOD[1], WOOD[2], WOOD[3], WOOD[4])


def ledger(p: Pix) -> None:
    """A thick account book lying closed on the lid: wine leather, brass corners, a gilt frame, a ribbon marker."""
    px0, px1, pz0, pz1, up = 938, 964, 9, 29, 4

    def top(px: float, pz: float, x: int, y: int) -> Color | None:
        nx, nz = (px - px0) / (px1 - px0), (pz - pz0) / (pz1 - pz0)
        if min(nx, nz, 1 - nx, 1 - nz) < 0.0:
            return None
        c = WINE[3] if nx < 0.55 else WINE[2]
        if nz > 0.75:
            c = WINE[2]
        edge = min(nx * (px1 - px0), (1 - nx) * (px1 - px0), nz * (pz1 - pz0), (1 - nz) * (pz1 - pz0))
        if edge < 1.2:
            c = WINE[4] if nz < 0.5 and nx < 0.5 else WINE[1]
        elif 2.6 < edge < 3.6:
            c = BRASS[2] if (nx < 0.5) else BRASS[1]          # gilt frame line
        if 0.28 < nx < 0.78 and 0.35 < nz < 0.66:
            c = PARCHMENT[3] if nx < 0.6 else PARCHMENT[2]    # title label
            if int(nx * 40) % 3 == 0 and 0.42 < nz < 0.58:
                c = WINE[1]
        return c

    def front(x: int, y: int, t: float) -> Color:                   # the pages' edge: pale stripes between two covers
        if t < 0.28:
            return WINE[1]
        if t > 0.8:
            return WINE[3]
        return PARCHMENT[3] if int(t * 12 + x // 2) % 2 else PARCHMENT[2]

    def left(x: int, y: int, t: float) -> Color:                    # the spine, leather with raised bands
        return WINE[4] if x == round(PL.pt(px0, pz0)[0]) - 1 else WINE[3] if (x + 2 * y) % 9 else WINE[2]

    slab(p, PL, px0, px1, pz0, pz1, up, top, front, left, base=0.0)
    # shadow of the book on the lid, to its right
    # brass corners on the top
    for px, pz in ((px0 + 0.5, pz0 + 0.5), (px1 - 3.5, pz0 + 0.5), (px0 + 0.5, pz1 - 3.5), (px1 - 3.5, pz1 - 3.5)):
        a, b = PL.pt(px, pz, up), PL.pt(px + 3, pz + 3, up)
        p.rect(round(min(a[0], b[0])), round(min(a[1], b[1])), 3, 2, BRASS[3])
        p.px(round(min(a[0], b[0])), round(min(a[1], b[1])), BRASS[4])
    # the ribbon marker hanging out of the pages
    rx = px0 + 18
    a = PL.pt(rx, pz0, 1.8)
    for i in range(7):
        p.px(round(a[0]) + (i // 4), round(a[1]) + i, WINE[3] if i < 6 else WINE[1])
        p.px(round(a[0]) + 1 + (i // 4), round(a[1]) + i, WINE[4] if i < 5 else WINE[1])


def quill(p: Pix) -> None:
    """A goose quill lying across the lid (a line in the plane), its feather a pale vane, its shadow beside it."""
    a, b = PL.pt(930, 22, 0.8), PL.pt(950, 3, 0.8)
    sa, sb = PL.pt(931.5, 20.5), PL.pt(951.5, 1.5)
    for t in range(0, 21):
        x = sa[0] + (sb[0] - sa[0]) * t / 20
        y = sa[1] + (sb[1] - sa[1]) * t / 20
        fx.over(p, round(x), round(y) + 1, SHADOW, 170)
    n = 24
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        vane = 0.18 < t < 0.95
        p.px(round(x), round(y), PARCHMENT[4] if vane else PARCHMENT[3])
        if vane:
            for off in (-2, -1, 1, 2):
                if abs(off) == 2 and not (0.3 < t < 0.85):
                    continue
                p.px(round(x) + off, round(y) + (0 if off < 0 else 1), PARCHMENT[3] if off < 0 else PARCHMENT[2])
    p.px(round(a[0]) - 1, round(a[1]) + 1, IRON[1])                    # the cut nib
    p.px(round(a[0]), round(a[1]) + 1, IRON[2])


def wax(p: Pix) -> None:
    """A stick of red sealing wax (a short cylinder lying on the lid) and a spent seal of wax with a stamped mark."""
    a, b = PL.pt(947, 31, 1.5), PL.pt(962, 28, 1.5)
    sa = PL.pt(948, 30)
    for t in range(0, 17):
        fx.over(p, round(a[0] + (b[0] - a[0]) * t / 16 + 1), round(a[1] + (b[1] - a[1]) * t / 16 + 2), SHADOW, 150)
    for dy, c in ((0, WINE[4]), (1, WINE[3]), (2, WINE[2])):
        line(p, (a[0], a[1] + dy), (b[0], b[1] + dy), c)
    p.px(round(b[0]), round(b[1]) + 1, WINE[4])                        # the blackened tip
    p.px(round(a[0]), round(a[1]) + 1, WINE[1])
    p.px(round(a[0]) + 1, round(a[1]), WINE[1])
    _ = sa
    # the seal: a flat disc of wax on the lid, a pressed ring and a mark
    c = PL.pt(956, 12)
    cx, cy = round(c[0]), round(c[1])
    p.ellipse(cx - 4, cy - 1, 9, 4, WINE[0])
    p.ellipse(cx - 4, cy - 2, 9, 4, WINE[2])
    p.ellipse(cx - 3, cy - 2, 7, 3, WINE[3])
    p.px(cx - 2, cy - 2, WINE[4])
    p.px(cx, cy - 1, WINE[1])
    p.px(cx + 1, cy - 2, WINE[1])


def draw() -> Image.Image:
    p = Pix(960, 540, seed=16)
    hanging(p)
    chest(p)
    ledger(p)
    quill(p)
    wax(p)
    out = Image.new("RGBA", (960, 540), (0, 0, 0, 0))
    out.paste(p.finish().crop(BBOX), BBOX[:2])
    return out


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"radio.960x540.png": draw}
