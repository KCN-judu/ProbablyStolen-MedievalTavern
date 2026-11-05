"""`cassette_player` (80x80): the tape recorder as a small portable wind-up gramophone.

What it is: a hand-wound gramophone in an oak case. The record (black, with a wine-red label) lies where the cassette was,
under a glass window of the case; the tonearm reaches over it from a pivot on the lower right; the brass horn mouth sits
at the right of the front; a crank with a turned knob stands on top of the case and a forked rest holds the tonearm
when it is parked. (The counter's gramophone is the same device, drawn larger.)

The game gives this picture a case seen in oblique projection (its top and bottom edges run down to the right), so the
front is drawn straight and then sheared by whole rows per column, which keeps every pixel crisp."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Final

from PIL import Image

import fxkit as fx
from furn_kit import BRASS_AGED, clip
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, OAK, PALE_WOOD, SHADOW, SOOT, WINE, WOOD
from pix import Pix, mix

SLOPE = 0.52
TOP0 = -3.4                       # where the case's top edge would meet its left edge


def _ring_shade(p: Pix, cx: float, cy: float, r: float, ramp: tuple, width: float) -> None:
    """A round brass bezel: a lit upper left arc and a dark lower right arc, as a turned ring."""
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            d = math.hypot(x - cx, y - cy)
            if r - width <= d <= r:
                a = math.atan2(y - cy, x - cx)
                lit = 0.5 + 0.5 * math.cos(a - math.radians(-135))
                p.px(x, y, ramp[max(0, min(len(ramp) - 1, round(lit * (len(ramp) - 1) + (0.4 if d > r - 1 else -0.2))))])


def _face() -> Pix:
    """The straight front of the case: rows 0..53, columns 8..80."""
    p = Pix(80, 56, seed=120)
    fx.wood_fill(p, (8, 0, 72, 54), "h", OAK, board=13, light=0.6, bias=0.5, seed=31, knots=0.5, joints=False, nails=False,
                 damp=0.0, scratches=1.4)
    # a moulded rail along the top and the foot, and a stile at the left
    fx.wood_fill(p, (8, 0, 72, 4), "h", WOOD, board=4, light=0.5, bias=0.4, seed=32, knots=0, joints=False, nails=False)
    fx.wood_fill(p, (8, 49, 72, 5), "h", WOOD, board=5, light=0.2, bias=-0.7, seed=33, knots=0, joints=False, nails=False)
    fx.wood_fill(p, (8, 4, 4, 45), "v", WOOD, board=4, light=0.6, bias=0.3, seed=34, knots=0, joints=False, nails=False)
    for y in (27,):                                                      # brass corner straps on the stile
        fx.brass_fill(p, (8, 6, 6, 11), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=35)
        fx.brass_fill(p, (8, 38, 6, 11), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=36)
        fx.rivet(p, 11, 9, 1)
        fx.rivet(p, 11, 14, 1)
        fx.rivet(p, 11, 41, 1)
        fx.rivet(p, 11, 46, 1)
    # the face's shade: it darkens a little toward the right and foot
    for y in range(0, 54):
        for x in range(8, 80):
            if (x - 8) / 72 + y / 54 > 1.15 and (x + y) % 2 == 0 and p.get(x, y)[3]:
                fx.over(p, x, y, SHADOW, 60)
    return p


def _discs(p: Pix) -> None:
    """The round parts, drawn straight in the picture (a record window, tonearm and horn mouth are round and face us)."""
    # the record window: a brass bezel, glass, the black record, its red label, spindle, the tonearm
    cx, cy, R = 32, 38, 17
    fx.brass_fill(p, fx.ellipse(cx, cy, R + 1, R + 1, 48), ramp=BRASS_AGED, profile="dome", tarnish=0.5, seed=37)
    _ring_shade(p, cx, cy, R + 1, BRASS, 3)
    for x, y in fx.region(p, fx.ellipse(cx, cy, R - 2, R - 2, 48)).pixels():
        d = math.hypot(x - cx, y - cy)
        c = SOOT[0] if int(d) % 3 else IRON[0]                           # the record, grooved
        if d < 5.8:
            c = WINE[2] if d > 1.6 else BRASS[3]
            if 4.6 < d < 5.8:
                c = BRASS[2]
            elif d > 1.6 and (x - cx) + (y - cy) < -2:
                c = WINE[3]
            elif d > 1.6 and (x - cx) + (y - cy) > 2:
                c = WINE[1]
        elif (x - cx) < -(y - cy) * 0.6 and (x - cx) < -2 and int(d) % 3 == 0 and d > 8:
            c = IRON[2]                                                  # the sheen on the grooves, upper left
        p.px(x, y, c)
    fx.rivet(p, cx, cy, 1, BRASS)
    # the tonearm: a tapering brass tube from the pivot boss at the lower right, over the record, to the cartridge
    px0, py0 = 49, 59
    hx, hy = 38, 31
    for i in range(0, 61):
        t = i / 60
        x, y = px0 + (hx - px0) * t, py0 + (hy - py0) * t - 4 * math.sin(math.pi * t)   # a gentle bow
        w = 2.2 - 0.9 * t
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= w * w:
                    lit = 4 if dx + dy < 0 else 2 if dx + dy == 0 else 1
                    p.px(round(x + dx), round(y + dy), BRASS[lit])
    fx.over(p, 42, 41, SHADOW, 90)
    p.rect(hx - 3, hy - 1, 5, 4, BRASS[2])                              # the cartridge head
    p.hline(hx - 3, hy - 1, 5, BRASS[4])
    p.px(hx - 3, hy + 3, SHADOW)
    fx.brass_fill(p, fx.ellipse(px0 + 1, py0, 5, 5, 24), ramp=BRASS_AGED, profile="dome", tarnish=0.3, seed=38)
    # glass over the window: reflections and a lit rim
    for k, (a, w) in enumerate(((-0.45, 3), (-0.1, 1))):
        for y in range(cy - R + 3, cy + R - 2):
            for x in range(cx - R + 3, cx + R - 2):
                if math.hypot(x - cx, y - cy) < R - 3 and abs((x - cx) + (y - cy) * 0.8 - a * 30 - 8) < w:
                    fx.over(p, x, y, GLASS[4], 110 if k == 0 else 160)
    # the horn mouth: a flared brass bell seen end-on, ringed and with a dark throat
    hx2, hy2, HR = 66, 54, 11
    fx.brass_fill(p, fx.ellipse(hx2, hy2, HR, HR, 48), ramp=BRASS_AGED, profile="dome", tarnish=0.6, seed=39)
    for x, y in fx.region(p, fx.ellipse(hx2, hy2, HR - 3, HR - 3, 48)).pixels():
        d = math.hypot(x - hx2, y - hy2)
        a = math.atan2(y - hy2, x - hx2)
        lit = 0.5 + 0.5 * math.cos(a - math.radians(-135))
        k = int(d / 2.2) % 2
        if d < 3.2:
            c = SOOT[0]
        else:
            idx = round(1 + 3 * lit) if k else round(0.5 + 1.2 * lit)
            c = BRASS_AGED[max(0, min(4, idx))]
        p.px(x, y, c)
    _ring_shade(p, hx2, hy2, HR, BRASS, 2)


def gramophone() -> Image.Image:
    p = Pix(80, 80, seed=121)
    face = _face()
    sheared = face.im.transform((80, 80), Image.Transform.AFFINE, (1, 0, 0, -SLOPE, 1, -TOP0 + SLOPE * 8), Image.Resampling.NEAREST)
    p.paste(sheared, 0, 0)
    _discs(p)
    # the top and left edges catch the light
    for x in range(8, 80):
        y = round(TOP0 + SLOPE * (x - 8))
        if y >= 20 and p.get(x, y)[3]:
            p.px(x, y, WOOD[4])
            fx.over(p, x, y + 1, PALE_WOOD[2], 120)
    # on top of the case: the crank, the forked tonearm rest, a brass ring and a finial post
    fx.brass_fill(p, (59, 7, 3, 17), ramp=BRASS_AGED, profile="tube", tarnish=0.3, seed=51)
    fx.brass_fill(p, (58, 21, 5, 3), ramp=BRASS_AGED, profile="plate", tarnish=0.3, seed=52)
    fx.wood_fill(p, fx.ellipse(60, 6, 3, 3, 20), "v", PALE_WOOD, board=2, light=0.7, seed=53, knots=0, joints=False, nails=False)
    p.px(59, 4, PALE_WOOD[4])
    fx.brass_fill(p, (7, 6, 4, 14), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=54)       # finial post
    fx.rivet(p, 8, 5, 1)
    for x0 in (19, 23):                                                  # the two prongs of the rest
        fx.brass_fill(p, (x0, 6, 3, 14), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=55 + x0)
    fx.brass_fill(p, (18, 17, 9, 3), ramp=BRASS_AGED, profile="plate", tarnish=0.4, seed=57)
    # a brass winding-key ring
    for a in range(0, 360, 12):
        x, y = 40 + 4.5 * math.cos(math.radians(a)), 16 + 3.3 * math.sin(math.radians(a))
        p.px(round(x), round(y), BRASS[3] if 90 < a < 200 else BRASS[1])
    return clip(p, "cassette")


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {"items~items_furniture@cassette_player.png": gramophone}
