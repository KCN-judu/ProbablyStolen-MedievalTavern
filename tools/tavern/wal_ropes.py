"""Every hanging rope, cord and chain of the shop: `wires`, `wires2`, `connectimg wire`.

Logic: the game's wall cables carry power between devices. In the tavern the same runs are bell-pulls and cord-and-weight
gear. Each cord hangs from a real fixing (iron eyebolt in the beam, a pulley on a bracket, a peg, a nail) and ends in a
real thing (a toggle grip, a lead weight, a lantern, a bell, a bundle of herbs). A loaded cord (one that carries a
weight) hangs straight; an unloaded one sags in a catenary.

  upper left   two herb bunches on nails.
  pulley gear  a pulley under the beam by the shutter post: one leg goes down to a wooden pull-toggle (the bell-pull of the
               shutter), the other carries a lead counterweight. `wires` (rest): the toggle high, the weight low and still.
               `wires2` (active, the game's lit state): the toggle has been pulled down, the weight has been drawn up and
               swings, the cords are taut and the wall-side faces are warmed by the lantern's glow.
  upper middle a hank of rope on a peg, a lantern on a chain, two cords that carry the tally plaque, the two short chains from
               the plaque down to the client tally board, a herb string between two nails.
  upper right  an onion string and a herb bunch on nails.
  lower left   (`wires` only) the shutter's old pull cords: an eyebolt-and-toggle bell-pull and a pulley with a weight.
`connectimg wire` is the long bell-pull at the right: an eyebolt in the beam, a rope, and a brass bell at its end.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Final

from PIL import Image, ImageDraw

import fxkit as fx
from palette import BRASS, FLAME, IRON, LEATHER, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD
from pix import Color, Pix, mix
from wal_kit import eyebolt, herb_bunch, nail, oak_frame, on_layer, onion_string

OX = 118
Pt = tuple[float, float]


def _disc(size: tuple[int, int], cx: float, cy: float, rx: float, ry: float) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse((round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)), fill=255)
    return m


def _ring(p: Pix, cx: float, cy: float, rx: float, ry: float, ramp: tuple[Color, ...] = IRON) -> None:
    for a in range(0, 360, 8):
        c = math.cos(math.radians(a - 225))
        p.px(round(cx + math.cos(math.radians(a)) * rx), round(cy + math.sin(math.radians(a)) * ry),
             ramp[4] if c > 0.45 else ramp[1] if c < -0.45 else ramp[3])


def pulley(p: Pix, cx: int, top: int) -> tuple[int, int]:
    """An iron pulley hung from a bracket bolted to the beam's underside. Returns the wheel centre."""
    fx.iron_fill(p, (cx - 4, top, 9, 3), seed=cx, rust=0.1, scratches=0.0, hammer=0.2)   # the plate on the beam
    fx.rivet(p, cx - 3, top + 1, 1, BRASS, shadow=False)
    fx.rivet(p, cx + 3, top + 1, 1, BRASS, shadow=False)
    fx.iron_fill(p, (cx - 1, top + 3, 3, 4), seed=cx + 1, scratches=0.0)                  # the strap that holds the axle
    wy = top + 12
    p.ellipse(cx - 5, wy - 5, 11, 11, IRON[0])                                           # the wheel: a dark groove between two rims
    p.ellipse(cx - 4, wy - 4, 9, 9, IRON[2])
    _ring(p, cx, wy, 5, 5)
    p.ellipse(cx - 2, wy - 2, 5, 5, IRON[1])
    for k in range(4):                                                                    # spokes
        a = k * math.pi / 2 + 0.4
        p.line(cx, wy, cx + round(math.cos(a) * 3), wy + round(math.sin(a) * 3), IRON[3])
    fx.rivet(p, cx, wy, 1, BRASS)
    return cx, wy


def weight(p: Pix, cx: int, top: int, w: int = 9, h: int = 13) -> None:
    """A lead-and-iron counterweight: a ring on top, a cylinder shaded across, two iron bands, a dented surface."""
    _ring(p, cx, top + 2, 2.6, 3.2)
    fx.contact_shadow(p, (cx - w // 2, top + 4, w, h), shift=(1, 2), spread=2, strength=0.5)
    reg = fx.brass_fill(p, (cx - w // 2, top + 5, w, h), profile="tube", tarnish=0.9, seed=cx + top, ramp=IRON)
    for by in (top + 8, top + 5 + h - 4):
        p.hline(cx - w // 2, by, w, IRON[1])
        p.hline(cx - w // 2, by + 1, w, IRON[4])
    del reg


def toggle(p: Pix, cx: int, top: int) -> None:
    """A turned wooden pull grip with a leather wrap at its neck, the rope knotted into its top."""
    fx.contact_shadow(p, (cx - 2, top + 3, 5, 10), shift=(1, 2), spread=2, strength=0.5)
    fx.wood_fill(p, (cx - 2, top + 3, 5, 11), "v", PALE_WOOD, board=5, knots=0.0, joints=False, nails=False, seed=cx + top, wear_amount=0.1)
    p.hline(cx - 1, top + 2, 3, PALE_WOOD[2])
    p.rect(cx - 2, top + 5, 5, 2, LEATHER[2])
    p.hline(cx - 2, top + 5, 5, LEATHER[3])
    p.hline(cx - 2, top + 6, 5, LEATHER[0])
    p.rect(cx - 1, top + 13, 3, 1, PALE_WOOD[0])


def bell(p: Pix, cx: int, top: int) -> None:
    """A small brass cow-bell hung by a loop: waisted body (polygon, `brass_fill` tube), dark mouth, clapper."""
    _ring(p, cx, top + 1, 2.2, 2.4, BRASS)
    pts = [(cx - 3, top + 3), (cx + 3, top + 3), (cx + 4, top + 8), (cx + 6, top + 12), (cx - 6, top + 12), (cx - 4, top + 8)]
    fx.contact_shadow(p, pts, shift=(1, 1), spread=2, strength=0.5)
    fx.brass_fill(p, pts, profile="tube", tarnish=0.5, seed=cx)
    p.hline(cx - 5, top + 12, 11, BRASS[0])
    p.hline(cx - 4, top + 13, 9, SHADOW)
    p.ellipse(cx - 1, top + 13, 3, 3, BRASS[2])
    p.px(cx - 1, top + 13, BRASS[4])


def lantern(p: Pix, cx: int, top: int, active: bool) -> tuple[int, int]:
    """A horn-and-iron lantern on a ring: pointed cap, four iron posts with amber glass between, a candle flame, a foot."""
    w, h = 12, 15
    x0, y0 = cx - w // 2, top + 5
    fx.contact_shadow(p, (x0, y0, w, h), shift=(2, 2), spread=2, strength=0.5)
    p.rect(x0, y0, w, h, (74, 40, 18, 255))
    for yy in range(y0 + 1, y0 + h - 1):                                                  # amber panes lit from within
        for xx in range(x0 + 2, x0 + w - 2):
            d = math.hypot(xx - cx, yy - (y0 + h // 2 + 1))
            v = 3.3 - d / 4.5 + (0.6 if active else 0)
            p.px(xx, yy, fx.pick_tone((FLAME[0], FLAME[1], FLAME[2], FLAME[3], FLAME[4]), v, xx, yy, 2.6))
    p.vline(cx - 1, y0 + 5, 7, FLAME[4])                                                  # the flame
    p.vline(cx, y0 + 4, 8, FLAME[3])
    p.px(cx, y0 + 3, FLAME[2])
    for gx in (x0, x0 + w - 2):                                                           # corner posts
        fx.iron_fill(p, (gx, y0, 2, h), seed=gx, rust=0.1, scratches=0.0, hammer=0.2)
    p.hline(cx - 1, y0 + h // 2, 2, IRON[2]) if False else None
    cap = [(cx, top + 2), (x0 + w + 1, y0), (x0 - 1, y0)]
    fx.iron_fill(p, cap, seed=cx + 3, rust=0.1, scratches=0.0)
    fx.iron_fill(p, (x0 - 1, y0 + h, w + 2, 2), seed=cx + 4, rust=0.2, scratches=0.0)
    _ring(p, cx, top + 1, 2.0, 2.2)
    return cx, y0 + h // 2


def hank(p: Pix, x: int, y: int) -> None:
    """A hank of spare rope hung over a wooden peg driven into the beam: three loops of rope falling from the peg."""
    for i, (rx, ry, off) in enumerate(((7, 20, 0), (5.5, 17, 1), (4, 14, -1))):
        pts = []
        for k in range(0, 41):
            a = math.pi * 2 * k / 40 - math.pi / 2
            pts.append((x + off + math.cos(a) * rx, y + 1 + ry + math.sin(a) * ry))
        fx.rope(p, pts, 2.6, seed=i + 5, shadow=(i == 0))
    fx.wood_fill(p, fx.ellipse(x, y, 3.5, 3.5), "v", PALE_WOOD, board=3, knots=0.0, joints=False, nails=False, seed=7)
    p.px(x, y, PALE_WOOD[4])
    p.px(x + 1, y + 1, PALE_WOOD[0])
    p.hline(x - 2, y + 1, 5, LEATHER[1])                                                  # the lashing that holds the hank together
    p.hline(x - 2, y + 2, 5, LEATHER[3])


def _glow_pass(p: Pix, cx: float, cy: float, radius: float) -> None:
    """Warms what is near the lantern: iron and rope take a little of the flame's light on the side facing it."""
    for y in range(p.h):
        for x in range(p.w):
            c = p.get(x, y)
            if c[3] < 255:
                continue
            d = math.hypot(x - cx, y - cy)
            if d >= radius or d < 11:
                continue
            k = (1 - d / radius) * 0.55
            if fx.noise(x, y, 3) < k + 0.1 and (x - cx) * 0 + (y - cy) * 0 == 0:
                p.px(x, y, mix(c[:3], FLAME[3], 0.38))


def _upper(p: Pix, active: bool) -> None:
    A = lambda x, y: (x - OX, y)                                                          # scene -> canvas

    # ---- upper left: two herb bunches on nails in the beam face
    for nx, ln, dry in ((108, 21, False), (123, 17, True)):
        cx, cy = A(nx, 5)
        nail(p, cx, cy)
        p.vline(cx, cy + 1, 3, fx.ROPE[2])
        herb_bunch(p, cx, cy + 3, ln, 9, dry=dry, seed=nx)

    # ---- pulley gear by the shutter post: toggle leg and weight leg
    px_, wy = pulley(p, 305 - OX, 27)
    pull = 7 if active else 0
    tx, ty = 299 - OX, 188 + pull
    lx = 300 - OX
    fx.rope(p, [(lx, wy), (lx - 0.5, (wy + ty) / 2), (tx, ty + 1)], 2.6, seed=1)
    toggle(p, tx, ty)
    wx = 311 - OX
    wtop = 112 - pull if active else 140
    sway = 3 if active else 0
    fx.rope(p, [(wx, wy), (wx + sway * 0.4, (wy + wtop) / 2), (wx + sway, wtop + 1)], 2.6, seed=2)
    weight(p, wx + sway, wtop, 9, 13)

    # ---- upper middle: a hank on a peg, the lantern, the plaque's cords and the chains below it
    hank(p, *A(680, 12))
    lx0 = 723 - OX
    eyebolt(p, lx0, 24, ring=5, drop=1)
    swing = 2 if active else 0
    fx.chain(p, [(lx0, 31), (lx0 + swing, 46)], link=6)
    cx_l, cy_l = lantern(p, lx0 + swing, 42, active)
    for ex in (700, 746):                                                                 # plaque cords: loaded, so straight
        cx = ex - OX
        eyebolt(p, cx, 24, ring=5, drop=1)
        fx.rope(p, [(cx, 31), (cx, 64)], 2.6, seed=ex)
        p.rect(cx - 2, 64, 5, 3, LEATHER[2])                                              # the cord is lashed to the plaque's staple
        p.hline(cx - 2, 64, 5, LEATHER[3])
    bx, by = A(692, 67)                                                                   # the tally plaque the cords carry
    fx.wall_shadow(p, (bx, by, 62, 38), offset=(3, 4), spread=3, strength=0.8)
    oak_frame(p, bx, by, 62, 38, 3, WOOD, seed=31)
    fx.wood_fill(p, (bx + 3, by + 3, 56, 32), "v", PALE_WOOD, board=8, knots=0.6, seed=32, wear_amount=0.2)
    chalk = (PARCHMENT[4], PARCHMENT[3], PARCHMENT[2])
    for g in range(2):                                                                    # chalk tally: two gates of five
        gx = bx + 8 + g * 24
        for i in range(4):
            for y in range(by + 9, by + 24):
                p.px(gx + i * 4 + (1 if fx.noise(gx + i, y, 2) > 0.8 else 0), y, chalk[(y + i) % 3 > 0])
        for k in range(15):
            p.px(gx - 1 + k * 18 // 15 + 0, by + 25 - k * 15 // 15 + 0, chalk[0])
    for sx in (bx + 5, bx + 56):
        fx.rivet(p, sx, by + 5, 1, BRASS, shadow=False)
        fx.rivet(p, sx, by + 32, 1, BRASS, shadow=False)
    for ex in (706, 732):                                                                 # chains plaque -> client board
        cx = ex - OX
        fx.iron_fill(p, (cx - 2, 105, 5, 3), seed=ex, rust=0.1, scratches=0.0)
        fx.chain(p, [(cx, 108), (cx, 120)], link=6)
    # herb string between two nails, with three bunches tied to it
    a, b = A(772, 28), A(836, 28)
    nail(p, *a)
    nail(p, *b)
    pts = fx.hang_curve(a, b, 7 if not active else 6)
    fx.rope(p, pts, 2.0, seed=4)
    for t, ln, dry in ((0.25, 15, False), (0.52, 18, True), (0.78, 14, False)):
        i = int(t * (len(pts) - 1))
        hx, hy = pts[i]
        herb_bunch(p, round(hx), round(hy) + 1, ln, 8, dry=dry, seed=i)

    # ---- upper right
    ox_, oy_ = A(866, 28)
    nail(p, ox_, oy_)
    onion_string(p, ox_, oy_ + 1, 6, seed=2)
    hx, hy = A(880, 6)
    nail(p, hx, hy)
    p.vline(hx, hy + 1, 3, fx.ROPE[2])
    herb_bunch(p, hx, hy + 3, 20, 8, seed=7)

    bx, by = A(934, 24)                                                                   # the long bell-pull's fixing
    eyebolt(p, bx, by, ring=5, drop=1)
    fx.rope(p, [(bx, by + 7), (bx, by + 17)], 2.6, seed=5)
    if active:
        _glow_pass(p, cx_l, cy_l, 55)


def _lower(p: Pix) -> None:
    """The old pull cords of the shutter on the left wall: a ring-bolt with a toggle, a pulley with a weight."""
    A = lambda x, y: (x - OX, y)
    ex, ey = A(163, 322)
    eyebolt(p, ex, ey, ring=6, drop=1)
    fx.rope(p, [(ex, ey + 9), (ex - 1, 365), (ex + 1, 410)], 2.6, seed=21)
    toggle(p, ex + 1, 408)
    px_, wy = pulley(p, 182 - OX, 322)
    lx, rx = px_ - 5, px_ + 5
    fx.rope(p, [(lx, wy), (lx - 1, 360), (lx, 395)], 2.6, seed=22)
    fx.rope(p, [(lx, 395), (lx - 2, 402), (lx - 4, 396), (lx - 3, 391)], 2.0, seed=23, shadow=False)
    fx.rope(p, [(rx, wy), (rx, 400), (rx, 430)], 2.6, seed=24)
    weight(p, rx, 429, 11, 16)


def wires(active: bool) -> Image.Image:
    box = (118, 0, 960, 270 if active else 467)
    def draw(p: Pix) -> None:
        _upper(p, active)
        if not active:
            _lower(p)
    return on_layer(box, draw, 40 + active)


def end_bell() -> Image.Image:
    """`connectimg wire` (24x244 at (922, 34)): the long bell-pull at the right: from an eyebolt in the beam a rope that
    hangs with a gentle bow (it carries only its own weight) down to a brass bell."""
    def draw(p: Pix) -> None:
        ex = 12
        pts = [(ex + 3 * math.sin((y / 215) * math.pi), y) for y in range(0, 218)]
        fx.rope(p, pts, 2.6, knots=(0.86,), seed=5)
        bell(p, round(pts[-1][0]), 216)
    return on_layer((922, 34, 946, 278), draw, 45)


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "wires.960x540.png": lambda: wires(False),
    "wires2.960x540.png": lambda: wires(True),
    "connectimg wire.960x540.png": end_bell,
}
