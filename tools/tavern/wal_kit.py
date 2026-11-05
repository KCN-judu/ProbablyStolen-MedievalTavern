"""Small shared pieces of the wall-fixture pass (prefix `wal_`): mitred oak frames, iron corners and eyebolts, nails, herb
bunches, onion strings. Everything is built from `fxkit` materials so it matches the cask's quality, and every hanging
piece ends in a real fixing (the callers draw the rope to an eyebolt or hook made here)."""

from __future__ import annotations

import math
from collections.abc import Sequence

from PIL import Image, ImageDraw

import fxkit as fx
from palette import BRASS, IRON, LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import Color, Pix, Ramp, mix

W, H = 960, 540
Pt = tuple[float, float]


def on_layer(box: tuple[int, int, int, int], draw, seed: int) -> Image.Image:
    """A 960x540 layer holding one small canvas at `box` (x0, y0, x1, y1), as the game's layers are."""
    x0, y0, x1, y1 = box
    small = Pix(x1 - x0, y1 - y0, seed=seed)
    draw(small)
    full = Pix(W, H)
    full.paste(small, x0, y0)
    return full.finish()


def _mask(size: tuple[int, int], poly: Sequence[Pt]) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(round(x), round(y)) for x, y in poly], fill=255)
    return m


def oak_frame(p: Pix, x: int, y: int, w: int, h: int, t: int, ramp: Ramp = WOOD, seed: int = 0) -> None:
    """A frame of four timbers mitred at the corners, painted member by member so the grain follows each; the outer edge
    is lit on the upper left and shaded on the lower right, the inner rebate casts a dark line."""
    x1, y1 = x + w, y + h
    ox, oy = x1 - t, y1 - t
    sz = (p.w, p.h)
    top = _mask(sz, [(x, y), (x1, y), (ox, y + t), (x + t, y + t)])
    bot = _mask(sz, [(x + t, oy), (ox, oy), (x1, y1), (x, y1)])
    lef = _mask(sz, [(x, y), (x + t, y + t), (x + t, oy), (x, y1)])
    rig = _mask(sz, [(x1, y), (x1, y1), (ox, oy), (ox, y + t)])
    fx.wood_fill(p, top, "h", ramp, board=t, seed=seed + 1, knots=0.4, joints=False, nails=False, scratches=0.6, wear_amount=0.2)
    fx.wood_fill(p, bot, "h", ramp, board=t, seed=seed + 2, knots=0.4, joints=False, nails=False, scratches=0.6, wear_amount=0.2)
    fx.wood_fill(p, lef, "v", ramp, board=t, seed=seed + 3, knots=0.4, joints=False, nails=False, scratches=0.6, wear_amount=0.2)
    fx.wood_fill(p, rig, "v", ramp, board=t, seed=seed + 4, knots=0.4, joints=False, nails=False, scratches=0.6, wear_amount=0.2)
    p.hline(x, y, w, ramp[4])                                           # lit outer edges
    p.vline(x, y, h, ramp[4])
    p.hline(x + 1, y1 - 1, w - 1, ramp[0])
    p.vline(x1 - 1, y + 1, h - 1, ramp[0])
    p.hline(x + t - 1, y + t - 1, w - 2 * t + 2, ramp[0])               # the rebate: dark top and left, lit foot and right
    p.vline(x + t - 1, y + t - 1, h - 2 * t + 2, ramp[0])
    p.hline(x + t - 1, oy, w - 2 * t + 2, ramp[3])
    p.vline(ox, y + t - 1, h - 2 * t + 2, ramp[3])


def nail(p: Pix, x: int, y: int) -> None:
    """A forged nail head with a lit top-left and a hard shadow to its lower right."""
    fx.rivet(p, x, y, 1, IRON)


def eyebolt(p: Pix, x: int, y: int, ring: int = 4, drop: int = 3) -> None:
    """An iron eye screwed into a timber: a small square plate with a rivet, an eye ring that hangs from it, so the cord
    below ties onto something. (x, y) is the plate's centre; the ring hangs `drop` px below it."""
    fx.iron_fill(p, (x - 2, y - 2, 5, 5), seed=x * 7 + y, rust=0.1, hammer=0.2, scratches=0.0)
    p.px(x, y, IRON[4])
    cy = y + drop + ring // 2
    for a in range(0, 360, 12):
        rx = x + round(math.cos(math.radians(a)) * (ring / 2 + 0.2))
        ry = cy + round(math.sin(math.radians(a)) * (ring / 2 + 0.6))
        lit = math.cos(math.radians(a - 225)) > 0.2
        p.px(rx, ry, IRON[4] if lit else IRON[1])


def hook(p: Pix, x: int, y: int, length: int = 8, open_right: bool = True) -> None:
    """An iron S-hook hanging from an eye: a shaft, a curve at the foot and a pointed tip."""
    d = 1 if open_right else -1
    for k in range(length):
        p.px(x, y + k, IRON[3] if k % 2 == 0 else IRON[2])
        p.px(x - d, y + k, IRON[4]) if k < length - 3 else None
    for a in range(0, 200, 25):
        hx = x + d * round(2.5 - 2.5 * math.cos(math.radians(a)))
        hy = y + length + round(2.2 * math.sin(math.radians(a)))
        p.px(hx, hy, IRON[3])
        p.px(hx, hy - 1, IRON[4])
    p.px(x + d * 4, y + length - 1, IRON[4])


def leaf_cluster(p: Pix, cx: float, cy: float, rx: float, ry: float, ramp: Ramp, seed: int) -> None:
    """A dense clump of leaves, an ellipse shaded by lit upper-left and noisy toward its rim so it reads as foliage."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            d = math.hypot(dx, dy)
            n = fx.noise(x, y, seed)
            if d + (n - 0.5) * 0.5 > 1.0:
                continue
            v = 2.3 - (dx * 0.7 + dy * 0.8) * 1.4 + (n - 0.5) * 1.6
            p.px(x, y, fx.pick_tone(ramp, v, x, y, 2.2))


def herb_bunch(p: Pix, x: int, y: int, length: int, width: int, dry: bool = False, seed: int = 0, tie: bool = True) -> None:
    """A bunch of herbs hung head-down from a string at (x, y): stems tied together with a twine wrap near the top, leaf
    clusters fanning out below, a sprig or two sticking out of the sides. `dry` browns and thins it."""
    ramp: Ramp = (LEATHER[0], LEATHER[1], (110, 82, 40, 255), (150, 118, 62, 255)) if dry else MOSS
    top = y + 2
    for k in range(3):                                                  # stems above the wrap
        p.px(x - 1 + k, top, LEATHER[2])
        p.px(x - 1 + k, top + 1, LEATHER[1])
    for i in range(7):                                                  # clusters: widest at about a third of the way down
        t = i / 6
        cy = top + 4 + t * (length - 6)
        w = (width / 2) * (0.5 + 0.9 * math.sin(math.pi * min(1.0, 0.25 + t * 0.85))) * (1 - 0.25 * t)
        off = math.sin(i * 2.1 + seed) * width * 0.18
        leaf_cluster(p, x + off, cy, max(1.5, w), max(2.2, length / 6), ramp, seed + i)
    for sx in (-1, 1):                                                  # loose sprigs
        yy = top + length // 2
        for k in range(3):
            p.px(x + sx * (width // 2 + k), yy + k, ramp[2])
        p.px(x + sx * (width // 2 + 3), yy + 3, ramp[3])
    if tie:
        for k in range(3):
            p.hline(x - 2, top + 2 + k, 5, (LEATHER[3] if k != 1 else LEATHER[2]) if not dry else PARCHMENT[1])
        p.px(x - 2, top + 3, PARCHMENT[2])
        p.px(x + 2, top + 4, PARCHMENT[0])
    p.px(x, y, PARCHMENT[1])                                            # the string into the bunch


def onion_string(p: Pix, x: int, y: int, count: int, seed: int = 0) -> None:
    """A plaited string of onions hanging from a nail: a cord with a bulb every few pixels, lit upper left, with dry
    papery skins and a tuft of root at the bottom."""
    pitch = 8
    for i in range(count):
        cy = y + 6 + i * pitch
        sway = round(math.sin(i * 1.7 + seed) * 1.2)
        for yy in range(cy - 4, cy + 5):
            for xx in range(x + sway - 5, x + sway + 6):
                dx, dy = (xx - x - sway) / 4.6, (yy - cy) / 4.2
                d = dx * dx + dy * dy
                if d > 1 or (yy < cy - 2 and abs(dx) > 0.5 + (yy - cy + 4) * 0.25):
                    continue
                v = 3.1 - (dx * 0.8 + dy * 0.8) * 1.5 + (fx.noise(xx, yy, seed) - 0.5) * 0.7
                if abs(math.sin(dx * 3.0)) < 0.18:
                    v -= 0.9                                            # the paper skin's ribs
                p.px(xx, yy, fx.pick_tone(PARCHMENT, v - 0.2, xx, yy, 2.2) if (i + seed) % 2 else fx.pick_tone((WINE[1], WINE[2], WINE[3], WINE[4]), v - 0.4, xx, yy, 2.2))
        p.px(x + sway, cy - 5, LEATHER[2])
    rope_end = y + 6 + count * pitch
    for yy in range(y, rope_end - 2):
        p.px(x + round(math.sin(yy / 8 + seed) * 1.0), yy, LEATHER[3] if yy % 2 else LEATHER[2])
    for k in range(3):
        p.px(x - 1 + k, rope_end - 3 + k // 2, PARCHMENT[1])


def tone_over(c: Color, k: float) -> Color:
    """`c` scaled in light by k (1 = unchanged)."""
    return (max(0, min(255, round(c[0] * k))), max(0, min(255, round(c[1] * k))), max(0, min(255, round(c[2] * k))), c[3])


__all__ = ["oak_frame", "nail", "eyebolt", "hook", "herb_bunch", "onion_string", "leaf_cluster", "on_layer", "tone_over", "mix",
           "BRASS", "OAK", "PALE_WOOD", "SHADOW"]
