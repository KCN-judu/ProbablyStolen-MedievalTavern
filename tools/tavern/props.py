"""The small things of the tavern: what hangs on the walls and stands on the bar (almanac, slates, notice board, handbell,
lectern, ale poster, music box, suggestion box, bedroll, ropes), the sprite sheets (animations, push-plates), and the
Resources sprites (document chests, slop barrels, ale taps, wine rack and cask shelf with their fill levels).

A scene layer is 960x540 but holds one small object: it is drawn on a small canvas of the size of the game's
`bbox` (tools/tavern/layout.tsv) and pasted at that place, so nothing leaves the rectangle the game's layer fills.
The helpers at the top (ropes, herbs, parchment, boards, barrels, bottles) are shared with backroom.py.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from functools import partial
from typing import Final

from PIL import Image, ImageChops, ImageDraw

import font
from materials import beam as _beam, iron_strap, planks as _planks, shadow_under, tone, vertical_strap
from palette import (BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT,
                     PLASTER, SHADOW, SOOT, STONE, WINE, WOOD)
from pix import CLEAR, Color, Pix, Ramp, mix

W, H = 960, 540
Box = tuple[int, int, int, int]          # x0, y0, x1, y1 as in layout.tsv (x1, y1 not included)
Point = tuple[int, int]


# ---------------------------------------------------------------------------------------------- helpers


def on_layer(box: Box, draw: Callable[[Pix], None], seed: int) -> Image.Image:
    """A 960x540 layer: `draw` paints a canvas of the box's size, which is then laid at the box's place."""
    x0, y0, x1, y1 = box
    small = Pix(x1 - x0, y1 - y0, seed=seed)
    draw(small)
    full = Pix(W, H)
    full.paste(small, x0, y0)
    return full.finish()


def timber(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = WOOD, plank: int = 12, vertical: bool = False,
           nails: bool = False) -> None:
    """Boards in a rectangle, kept inside it: `materials.planks` lets its grain streaks run past the end of a board,
    so they are drawn on a canvas of the rectangle's size and laid over."""
    sub = Pix(w, h, seed=p.rng.randrange(1 << 30))
    _planks(sub, 0, 0, w, h, ramp, plank, vertical, nails)
    p.paste(sub, x, y)


def post(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = OAK, vertical: bool | None = None) -> None:
    """One timber kept inside its rectangle (see `timber`)."""
    sub = Pix(w, h, seed=p.rng.randrange(1 << 30))
    _beam(sub, 0, 0, w, h, ramp, vertical)
    p.paste(sub, x, y)


def arc(x0: int, y0: int, x1: int, y1: int, sag: int) -> list[Point]:
    """The pixels of a hanging curve from one point to another that droops `sag` pixels in the middle."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
    out: list[Point] = []
    for i in range(n + 1):
        t = i / n
        pt = (round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)))
        if not out or out[-1] != pt:
            out.append(pt)
    return out


def rope(p: Pix, pts: Sequence[Point], thick: int = 2, ramp: Ramp = LINEN) -> None:
    """A twisted hemp rope along `pts`: a dark underlay, light and mid strands alternating, a lit edge."""
    for x, y in pts:
        p.rect(x + 1, y + 1, thick, thick, SHADOW)
    for i, (x, y) in enumerate(pts):
        strand = (i // 3) % 2 == 0
        p.rect(x, y, thick, thick, ramp[2] if strand else ramp[1])
        p.px(x, y, ramp[3] if strand else ramp[2])
        if thick > 1:
            p.px(x + thick - 1, y + thick - 1, ramp[0])


def chain(p: Pix, pts: Sequence[Point]) -> None:
    """An iron chain along `pts`: links alternate flat and edge-on every four pixels."""
    for i in range(0, len(pts), 4):
        x, y = pts[i]
        w, h = (4, 3) if (i // 4) % 2 == 0 else (3, 4)
        p.frame(x, y, w, h, IRON[3])
        p.px(x, y, IRON[4])
        p.px(x + w - 1, y + h - 1, IRON[0])


def nail(p: Pix, x: int, y: int) -> None:
    """An iron nail head with its small shadow."""
    p.px(x + 1, y + 1, SHADOW)
    p.px(x, y, IRON[4])


def herb_bunch(p: Pix, x: int, y: int, length: int, width: int = 9, dry: bool = False) -> None:
    """A bunch of herbs hung head down from a tie at (x, y): a swelling, ragged mass of leaves on a cord."""
    greens: Sequence[Color] = (PALE_WOOD[1], PALE_WOOD[2], LEATHER[2], MOSS[1]) if dry else (MOSS[1], MOSS[2], MOSS[3], MOSS[0])
    p.vline(x, y - 2, 4, LEATHER[1])
    p.rect(x - 1, y + 1, 3, 2, LEATHER[2])
    for r in range(length):
        half = round(math.sin(math.pi * (r + 2) / (length + 3)) ** 0.8 * width / 2)
        if r < 3:
            half = min(half, 1 + r)
        for xx in range(x - half, x + half + 1):
            if p.rng.random() < 0.88:
                c = p.rng.choice(greens)
                if xx <= x - half + 1 and p.rng.random() < 0.6:
                    c = tone(c, 0.18)
                p.px(xx, y + 3 + r, c)
    p.speckle(x - width // 2, y + 6, width, max(1, length - 8), (WINE[3], EMBER), 0.02)


def onion_string(p: Pix, x: int, y: int, n: int) -> None:
    """A cord with `n` onions or garlic heads knotted along it."""
    p.vline(x, y, n * 7 + 3, LEATHER[1])
    for i in range(n):
        cx, cy = x + (2 if i % 2 else -3), y + 3 + i * 7
        p.ellipse(cx - 1, cy, 6, 6, PLASTER[3])
        p.ellipse(cx, cy + 1, 4, 5, PLASTER[4])
        p.px(cx + 1, cy, PLASTER[1])
        p.hline(cx + 3, cy + 4, 2, PLASTER[1])
        p.px(cx + 2, cy - 1, LEATHER[2])


def ink_lines(p: Pix, x: int, y: int, w: int, rows: int, gap: int = 3, c: Color = PARCHMENT[0], indent: int = 0) -> None:
    """Rows of unreadable writing: dashes of random length that follow a ruled line."""
    for r in range(rows):
        xx = x + (indent if r == 0 else 0)
        end = x + w - p.rng.randrange(0, max(1, w // 4)) if r < rows - 1 else x + w * 2 // 3
        while xx < end:
            n = p.rng.randrange(2, 7)
            p.hline(xx, y + r * gap, min(n, end - xx), c)
            xx += n + 2


def parchment(p: Pix, x: int, y: int, w: int, h: int, ink: Color = PARCHMENT[0], torn: bool = False) -> None:
    """A sheet of parchment: lit on its upper left, shaded on its lower right, blotched with age; the bottom edge may be
    torn into a ragged line."""
    p.rect(x, y, w, h, PARCHMENT[3])
    p.dither(x, y, w, h, PARCHMENT[2], 0.12)
    for _ in range(max(2, w * h // 500)):
        p.dither(x + p.rng.randrange(w), y + p.rng.randrange(h), p.rng.randrange(6, 16), p.rng.randrange(4, 10),
                 PARCHMENT[2], 0.45)
    p.hline(x, y, w, PARCHMENT[4])
    p.vline(x, y, h, PARCHMENT[4])
    p.vline(x + w - 1, y, h, PARCHMENT[2])
    p.hline(x, y + h - 1, w, PARCHMENT[2])
    p.dither(x + w - 4, y, 4, h, PARCHMENT[1], 0.5)
    if torn:
        for xx in range(x, x + w):
            cut = p.rng.choice((0, 0, 1, 1, 2, 3))
            for k in range(cut):
                p.px(xx, y + h - 1 - k, CLEAR)
    del ink


def board(p: Pix, x: int, y: int, w: int, h: int, face: Ramp, frame: Ramp = WOOD, t: int = 3) -> None:
    """A wall board: a timber frame round a flat face, a shadow from the frame falling on the face, brass tacks at the
    corners. Used for slates, the tally board, the notice board."""
    p.rect(x, y, w, h, frame[2])
    p.hline(x, y, w, frame[4])
    p.vline(x, y, h, frame[4])
    p.hline(x, y + h - 1, w, frame[0])
    p.vline(x + w - 1, y, h, frame[0])
    p.hline(x + 1, y + 1, w - 2, frame[3])
    p.vline(x + 1, y + 1, h - 2, frame[3])
    p.hline(x + 1, y + h - 2, w - 2, frame[1])
    p.vline(x + w - 2, y + 1, h - 2, frame[1])
    p.rect(x + t, y + t, w - 2 * t, h - 2 * t, face[3])
    p.dither(x + t, y + t, w - 2 * t, h - 2 * t, face[2], 0.14)
    p.speckle(x + t, y + t, w - 2 * t, h - 2 * t, (face[2], face[4]), 0.015)
    p.dither(x + w // 2, y + h // 2, w // 2 - t, h // 2 - t, face[2], 0.2)
    p.hline(x + t, y + t, w - 2 * t, face[0])
    p.vline(x + t, y + t, h - 2 * t, face[1])
    p.hline(x + t + 1, y + t + 1, w - 2 * t - 2, face[1])
    for cx, cy in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
        p.px(cx, cy, BRASS[3])


def cabinet_frame(p: Pix, x: int, y: int, w: int, h: int, t: int) -> None:
    """A heavy oak frame of four timbers, joined at the corners, with an iron stud in every corner and along the rails."""
    post(p, x, y, w, t, OAK, vertical=False)
    post(p, x, y + h - t, w, t, OAK, vertical=False)
    post(p, x, y + t, t, h - 2 * t, OAK, vertical=True)
    post(p, x + w - t, y + t, t, h - 2 * t, OAK, vertical=True)
    for xx in range(x + 6, x + w - 4, 14):
        p.px(xx, y + t // 2, IRON[4])
        p.px(xx, y + h - 1 - t // 2, IRON[4])
    for yy in range(y + 6, y + h - 4, 14):
        p.px(x + t // 2, yy, IRON[4])
        p.px(x + w - 1 - t // 2, yy, IRON[4])
    for cx, cy in ((x + 1, y + 1), (x + w - t + 1, y + 1), (x + 1, y + h - t + 1), (x + w - t + 1, y + h - t + 1)):
        p.rect(cx, cy, t - 2, t - 2, IRON[2])
        p.frame(cx, cy, t - 2, t - 2, IRON[0])
        p.px(cx + 1, cy + 1, BRASS[3])


def bottle(p: Pix, x: int, y: int, body: Ramp, label: bool = False) -> None:
    """A standing bottle 5 wide and 11 tall at (x, y) its top left: cork, neck, shoulder, body, lit left side."""
    p.rect(x + 2, y, 2, 1, LEATHER[3])
    p.rect(x + 2, y + 1, 2, 3, body[1])
    p.rect(x + 1, y + 4, 4, 1, body[1])
    p.rect(x, y + 5, 5, 6, body[2])
    p.vline(x, y + 5, 6, body[3])
    p.vline(x + 4, y + 5, 6, body[0])
    p.hline(x, y + 10, 5, body[0])
    p.px(x + 2, y + 1, body[3])
    if label:
        p.rect(x + 1, y + 7, 3, 2, PARCHMENT[3])


def drop_shadow(p: Pix, x: int, y: int, w: int, h: int, depth: int = 2) -> None:
    """A soft dithered shadow thrown to the lower right of a rectangle that is drawn after it."""
    p.dither(x + depth, y + depth, w, h, SHADOW, 0.7)


# ---------------------------------------------------------------------------------------------- walls: slates


def hanging_board(p: Pix, x: int, y: int, w: int, h: int, face: Ramp, cords: Sequence[int], top: int = 0) -> None:
    """A board hung by two cords from the beam above (the cords start at row `top`): used for the credit slate."""
    for cx in cords:
        rope(p, arc(cx, top, x + (6 if cx < x + w // 2 else w - 7), y + 1, 3), 2)
    board(p, x, y, w, h, face)


def credit_slate() -> Image.Image:
    """`credit_display` (82x103): a framed limewashed tablet on two cords from the beam, with a chalked tally
    underneath; the face stays plain so the numbers the game writes on it can be read."""
    def draw(p: Pix) -> None:
        p.dither(24, 78, 56, 27, SHADOW, 0.6)
        hanging_board(p, 22, 75, 56, 28, PLASTER, (28, 71))
        p.hline(28, 93, 44, PLASTER[1])
        for i in range(4):
            p.vline(30 + i * 2, 96, 3, PLASTER[0])
        for yy in range(76, 98):
            p.px(80, yy, SHADOW)
    return on_layer((97, 0, 179, 103), draw, 3)


def tally_board() -> Image.Image:
    """`client_display` (49x46): a small tally board with a parchment face in an oak frame, on two clips, with brass
    tacks along the foot."""
    def draw(p: Pix) -> None:
        p.dither(3, 3, 45, 42, SHADOW, 0.55)
        board(p, 0, 0, 46, 42, PARCHMENT, OAK, 4)
        p.rect(5, 5, 36, 28, PARCHMENT[3])
        p.dither(5, 5, 36, 28, PARCHMENT[2], 0.2)
        p.hline(5, 5, 36, PARCHMENT[1])
        p.vline(5, 5, 28, PARCHMENT[1])
        for i, c in enumerate((WINE[3], MOSS[3], BRASS[3])):
            p.rect(26 + i * 5, 36, 3, 2, c)
        p.hline(6, 36, 12, OAK[0])
        p.hline(6, 38, 8, OAK[0])
        for cx in (10, 34):
            p.rect(cx, 0, 3, 2, IRON[2])
    return on_layer((696, 121, 745, 167), draw, 4)


def notice_board(new_note: bool) -> Image.Image:
    """`marketplace_pc` / `marketplace_pc_notif` (156x74): the notice board of the tavern, cut by the top of the picture:
    boards in an oak frame with pinned notes and string. The `_notif` one has a fresh note with a red wax seal."""
    def draw(p: Pix) -> None:
        p.rect(0, 0, 156, 74, OAK[1])
        timber(p, 4, 0, 148, 68, WOOD, plank=11, nails=False)
        post(p, 0, 0, 5, 74, OAK, vertical=True)
        post(p, 151, 0, 5, 74, OAK, vertical=True)
        post(p, 0, 68, 156, 6, OAK, vertical=False)
        shadow_under(p, 5, 0, 146, 5)
        notes = ((10, 8, 26, 30, 0), (40, 4, 22, 22, 1), (68, 10, 30, 36, 2), (104, 3, 24, 26, 0), (126, 20, 22, 30, 1),
                 (20, 38, 20, 24, 1), (46, 32, 18, 20, 0), (104, 36, 18, 26, 2))
        for nx, ny, nw, nh, kind in notes:
            p.dither(nx + 2, ny + 2, nw, nh, SHADOW, 0.7)
            parchment(p, nx, ny, nw, nh, torn=kind == 1)
            ink_lines(p, nx + 3, ny + 8, nw - 6, max(2, (nh - 8) // 3))
            font.write(p, nx + 3, ny + 2, "..", WINE[2]) if kind == 2 else p.hline(nx + 3, ny + 3, nw // 2, WINE[2])
            p.px(nx + nw // 2, ny + 1, BRASS[4])
            p.px(nx + nw // 2, ny + 2, IRON[0])
        rope(p, arc(36, 14, 82, 20, 6), 1)
        rope(p, arc(82, 20, 110, 15, 3), 1)
        if new_note:
            p.glow(77, 30, 28, FLAME[3], 0.55)
            p.dither(70, 24, 32, 38, SHADOW, 0.5)
            parchment(p, 66, 22, 30, 38)
            ink_lines(p, 69, 32, 24, 5)
            p.rect(76, 48, 9, 9, WINE[1])
            p.ellipse(76, 48, 9, 9, WINE[3])
            p.ellipse(78, 50, 5, 5, WINE[2])
            p.px(77, 49, WINE[4])
            p.px(80, 22, BRASS[4])
    return on_layer((788, 0, 944, 74), draw, 5 + new_note)


def lectern() -> Image.Image:
    """`negociation_tablet` (130x111): a lectern on the bar: a ruled sheet of parchment standing between two posts, a
    sloped writing desk with ink pot and quill and a brass seal plate, a plank front with studs."""
    def draw(p: Pix) -> None:
        p.ellipse(4, 98, 122, 12, SHADOW)
        post(p, 14, 6, 9, 72, WOOD, vertical=True)
        post(p, 107, 6, 9, 72, WOOD, vertical=True)
        for px_ in (14, 107):
            p.rect(px_, 3, 9, 4, BRASS[2])
            p.hline(px_, 3, 9, BRASS[4])
            p.hline(px_, 6, 9, BRASS[0])
        parchment(p, 23, 0, 84, 70)
        p.hline(23, 0, 84, PARCHMENT[4])
        font.write(p, 32, 6, "TERMS", WINE[2])
        p.hline(32, 15, 30, WINE[2])
        ink_lines(p, 32, 21, 68, 9, 4)
        p.rect(30, 56, 22, 8, PARCHMENT[2])
        p.frame(30, 56, 22, 8, PARCHMENT[0])
        p.dither(23, 62, 84, 8, SOOT[1], 0.35)
        p.poly([(10, 72), (120, 72), (126, 92), (4, 92)], WOOD[2])                     # the sloped desk
        p.hline(10, 72, 110, WOOD[4])
        p.dither(4, 84, 122, 8, WOOD[1], 0.5)
        p.line(10, 72, 4, 92, WOOD[3])
        p.line(120, 72, 126, 92, WOOD[0])
        p.rect(4, 92, 122, 17, WOOD[2])
        timber(p, 4, 92, 122, 17, WOOD, plank=8, nails=False)
        p.hline(4, 92, 122, WOOD[4])
        p.hline(4, 108, 122, SHADOW)
        for sx in (14, 112):
            vertical_strap(p, sx, 92, 5, 17)
        for sx in range(30, 100, 10):
            p.px(sx, 100, BRASS[3])
        p.rect(52, 96, 26, 9, BRASS[2])                                              # a brass seal plate
        p.frame(52, 96, 26, 9, BRASS[0])
        p.hline(53, 97, 24, BRASS[4])
        p.ellipse(60, 98, 10, 6, BRASS[3])
        p.ellipse(62, 99, 6, 4, BRASS[1])
        p.ellipse(100, 76, 8, 6, IRON[1])                                            # ink pot
        p.rect(100, 73, 8, 5, IRON[2])
        p.hline(100, 73, 8, IRON[4])
        p.rect(102, 74, 4, 2, SHADOW)
        p.line(104, 74, 112, 62, PARCHMENT[4])                                       # quill
        p.line(105, 74, 113, 63, PARCHMENT[2])
        p.ellipse(8, 77, 8, 6, WINE[3])                                              # wax stub
        p.rect(9, 77, 6, 3, WINE[3])
        p.px(10, 76, FLAME[3])
    return on_layer((649, 177, 779, 288), draw, 6)


def handbell() -> Image.Image:
    """`phone` (85x39): the brass handbell that calls the landlord, on a round oak tray on the bar, with a brass speaking
    horn lying beside it."""
    def draw(p: Pix) -> None:
        # the tray: a round board with a raised rim, seen from above (an ellipse), its thickness showing below
        p.ellipse(1, 22, 62, 16, SHADOW)
        p.dither(0, 26, 66, 11, OAK[1], 0.4)
        p.ellipse(3, 21, 58, 14, WOOD[0])                                            # the edge
        p.ellipse(3, 18, 58, 14, WOOD[4])                                            # the rim, lit
        p.ellipse(5, 19, 54, 12, WOOD[2])
        p.ellipse(7, 20, 50, 10, WOOD[1])                                            # the dished floor of the tray
        p.dither(9, 21, 46, 8, WOOD[2], 0.4)
        p.px(10, 22, WOOD[3])
        p.hline(13, 19, 24, WOOD[4])
        # the bell: a brass body that flares from a narrow crown to a wide lip, shaded across and lit on the left
        cx, y0, y1 = 32, 7, 23
        for y in range(y0, y1 + 1):
            s = (y - y0) / (y1 - y0)
            hw = 3 + 9 * s ** 0.55 + 3 * s ** 5
            for x in range(round(cx - hw), round(cx + hw) + 1):
                t = (x - cx) / hw
                k = 4 if -0.7 < t < -0.45 else 3 if t < -0.05 else 2 if t < 0.35 else 1 if t < 0.75 else 0
                if t >= 0.75:
                    k = 0 if t > 0.9 else 1
                p.px(x, y, BRASS[k])
        for y in range(y1 - 2, y1 + 1):                                              # the thick lip, a band
            hw = 3 + 9 * ((y - y0) / (y1 - y0)) ** 0.55 + 3 * ((y - y0) / (y1 - y0)) ** 5
            p.hline(round(cx - hw), y, round(2 * hw) + 1, BRASS[3] if y == y1 - 2 else BRASS[2])
        p.ellipse(cx - 15, y1 - 2, 31, 6, BRASS[0])                                   # the lip is a ring seen from above
        p.ellipse(cx - 15, y1 - 3, 31, 5, BRASS[3])
        p.ellipse(cx - 12, y1 - 2, 25, 3, BRASS[1])                                   # the dark inside under the lip
        p.hline(cx - 9, y1 - 3, 12, BRASS[4])
        p.vline(cx - 6, y0 + 6, 9, BRASS[4])                                          # a bright streak down its shoulder
        p.vline(cx - 7, y0 + 9, 5, BRASS[4])
        p.hline(cx - 10, y0 + 11, 20, BRASS[1])                                       # an engraved ring
        p.hline(cx - 6, y0 + 4, 12, BRASS[1])
        p.ellipse(cx - 2, y1 + 1, 5, 4, BRASS[0])                                     # the clapper peeping below the lip
        p.px(cx - 1, y1 + 2, BRASS[3])
        # the turned wooden handle on the crown
        p.rect(cx - 2, 0, 5, 7, WOOD[3])
        p.vline(cx - 2, 0, 7, WOOD[4])
        p.vline(cx + 2, 0, 7, WOOD[0])
        p.hline(cx - 3, 2, 7, WOOD[1])
        p.hline(cx - 3, 5, 7, WOOD[1])
        p.rect(cx - 3, 6, 7, 1, BRASS[3])
        p.dither(cx + 8, y1 + 1, 10, 3, SHADOW, 0.7)                                   # the bell's shadow on the tray
        # the speaking horn: a brass cone lying on the bar with its wide mouth to the right
        p.ellipse(60, 33, 24, 5, SHADOW)
        cone(p, 62, 28, 2, 79, 24, 8)
        p.rect(59, 25, 4, 7, LEATHER[2])                                               # a leather-bound mouthpiece
        p.vline(59, 25, 7, LEATHER[3])
        p.hline(59, 31, 4, LEATHER[0])
        p.ellipse(75, 15, 9, 20, BRASS[3])                                             # the mouth
        p.ellipse(76, 17, 6, 16, BRASS[1])
        p.ellipse(77, 19, 4, 12, SHADOW)
        p.vline(75, 20, 10, BRASS[4])
        p.hline(66, 21, 8, BRASS[4])                                                   # a bead of light along the top
    return on_layer((241, 268, 326, 307), draw, 7)


# ---------------------------------------------------------------------------------------------- the poster


def ale_poster(shadow: bool, down: bool = False) -> Image.Image:
    """`poster` / `poster_no_shadow` (86x103) / `poster_down` (89x90): a hand-painted advertisement for ale, a tankard
    in the middle of a sunburst, lettered DRINK above and HEARTH ALE below, held by four nails. The `down` one hangs from
    a single nail with its lower part rolled forward, showing the plain back."""
    def draw_up(p: Pix) -> None:
        if shadow:
            p.dither(2, 3, 82, 98, SHADOW, 0.8)
        px, py, pw, ph = 0, 0, 83, 100
        p.rect(px, py, pw, ph, WINE[2])
        cx, cy = 41, 51
        for yy in range(ph):                                   # sunburst: wedges around the tankard
            for xx in range(pw):
                a = math.atan2(yy - (cy - py), xx - (cx - px))
                d = math.hypot(yy - cy, xx - cx)
                k = int((a + math.pi) / (2 * math.pi) * 16)
                c = WINE[2] if k % 2 == 0 else WINE[3]
                if d < 26:
                    c = mix(c, FLAME[2], 0.45)
                elif d < 32:
                    c = mix(c, FLAME[1], 0.25)
                p.px(px + xx, py + yy, c)
        p.dither(0, 0, pw, 100, WINE[1], 0.18)
        p.rect(0, 0, pw, 2, PARCHMENT[2])                      # a cream border, a little frayed
        p.rect(0, ph - 2, pw, 2, PARCHMENT[2])
        p.rect(0, 0, 2, ph, PARCHMENT[2])
        p.rect(pw - 2, 0, 2, ph, PARCHMENT[2])
        for sx, sy in ((0, 0), (pw - 3, 0), (0, ph - 3), (pw - 3, ph - 3)):
            p.rect(sx, sy, 3, 3, CLEAR)
        font.write(p, 16, 7, "DRINK", PARCHMENT[4], 2)
        # the tankard
        p.ellipse(27, 78, 30, 6, WINE[0])
        p.rect(30, 44, 22, 34, PALE_WOOD[3])
        p.vline(30, 44, 34, PALE_WOOD[4])
        p.vline(51, 44, 34, PALE_WOOD[1])
        p.dither(44, 44, 8, 34, PALE_WOOD[1], 0.5)
        for yy in (52, 70):
            p.rect(29, yy, 24, 3, IRON[2])
            p.hline(29, yy, 24, IRON[4])
            p.hline(29, yy + 2, 24, IRON[0])
        p.rect(30, 44, 22, 5, FLAME[3])                        # amber ale with foam above
        p.ellipse(28, 38, 12, 10, PARCHMENT[4])
        p.ellipse(36, 35, 14, 12, PARCHMENT[4])
        p.ellipse(44, 39, 11, 10, PARCHMENT[3])
        p.hline(30, 46, 22, PARCHMENT[2])
        p.dither(28, 44, 26, 4, PARCHMENT[2], 0.4)
        p.poly([(53, 48), (62, 48), (64, 56), (64, 66), (62, 70), (53, 68)], CLEAR)
        p.rect(52, 50, 9, 3, PALE_WOOD[2])                     # the handle
        p.rect(59, 50, 3, 16, PALE_WOOD[2])
        p.rect(52, 63, 9, 3, PALE_WOOD[2])
        p.vline(61, 50, 16, PALE_WOOD[0])
        font.write(p, 12, 88, "HEARTH ALE", PARCHMENT[4])
        for sx, sy in ((3, 3), (pw - 5, 3), (3, ph - 5), (pw - 5, ph - 5)):
            nail(p, sx, sy)

    def draw_down(p: Pix) -> None:
        r, cx, cy = 11, 18, 62
        ax, ay = 0.8, -0.6                                        # the roll climbs to the right
        ex, ey = cx + ax * 70, cy + ay * 70
        nx, ny = -ay, ax
        if shadow:
            p.poly([(round(cx + nx * r + 5), round(cy + ny * r + 5)), (round(ex + nx * r + 4), round(ey + ny * r + 5)),
                    (round(ex - nx * r + 4), round(ey - ny * r + 5)), (round(cx - nx * r + 5), round(cy - ny * r + 5))], (*SHADOW, 150))
        p.poly([(round(cx + nx * r), round(cy + ny * r)), (round(ex + nx * r), round(ey + ny * r)),
                (round(ex - nx * r), round(ey - ny * r)), (round(cx - nx * r), round(cy - ny * r))], PARCHMENT[2])
        for i in range(2 * r + 1):                                # stripes along the roll, lit toward the upper left
            t = i / (2 * r) * 2 - 1
            c = PARCHMENT[4] if t < -0.5 else PARCHMENT[3] if t < 0.1 else PARCHMENT[2] if t < 0.6 else PARCHMENT[1]
            p.line(round(cx + nx * r * t), round(cy + ny * r * t), round(ex + nx * r * t), round(ey + ny * r * t), c)
        for k in (0.25, 0.7):                                    # ties
            sx, sy = cx + ax * 70 * k, cy + ay * 70 * k
            p.line(round(sx + nx * r), round(sy + ny * r), round(sx - nx * r), round(sy - ny * r), LEATHER[2])
            p.line(round(sx + nx * r + 1), round(sy + ny * r), round(sx - nx * r + 1), round(sy - ny * r), LEATHER[0])
        p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, WINE[2])    # the red face, rolled in
        for k in range(r, 1, -3):
            p.ellipse(cx - k, cy - k, 2 * k + 1, 2 * k + 1, WINE[3] if (k // 3) % 2 else PARCHMENT[3])
        p.ellipse(cx - 2, cy - 2, 5, 5, WINE[0])
        for hx in range(0, 3):                                    # the cord by which it hangs from a nail
            p.line(60 - hx, 4, round(cx + ax * 28), round(cy + ay * 28) - r + 2, LEATHER[1 + hx % 2])
        nail(p, 60, 2)
    if down:
        return on_layer((769, 114, 858, 204), draw_down, 9)
    return on_layer((769, 66, 855, 169), draw_up, 8 + shadow)


# ---------------------------------------------------------------------------------------------- music box, box, bedroll


def cone(p: Pix, x0: int, y0: int, r0: float, x1: int, y1: int, r1: float, ramp: Ramp = BRASS) -> None:
    """A tube that widens from (x0, y0) to (x1, y1), running mostly sideways: drawn column by column and shaded across,
    light on top and dark underneath (the light comes from the upper left)."""
    n = max(1, abs(x1 - x0))
    for i in range(n + 1):
        s = i / n
        x = round(x0 + (x1 - x0) * s)
        yc = y0 + (y1 - y0) * s
        r = r0 + (r1 - r0) * s
        top, bot = round(yc - r), round(yc + r)
        for y in range(top, bot + 1):
            u = (y - yc) / max(r, 0.5)
            k = 4 if u < -0.65 else 3 if u < -0.15 else 2 if u < 0.3 else 1 if u < 0.75 else 0
            p.px(x, y, ramp[k])
        p.px(x, top, ramp[4] if i % 5 else ramp[3])


def music_box(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A wooden music box in the rectangle, seen from slightly above: the top of the lid is a foreshortened plane with a
    brass inlay, three brass pipes stand on it and a brass horn flares to the right; the front is planked, with iron
    straps, a brass lock plate and short feet, and a crank sticks out on the left."""
    lid = max(7, h // 9)                                                   # height of the lid seen from above
    top = y + h * 40 // 100                                                # where the lid meets the front
    foot = 4
    bot = y + h - foot
    p.ellipse(x - 3, y + h - 7, w + 8, 9, SHADOW)                          # contact shadow
    p.dither(x - 5, y + h - 4, w + 12, 4, OAK[1], 0.5)
    for fx in (x + 3, x + w - 9):                                          # feet
        p.rect(fx, bot, 6, foot, OAK[1])
        p.hline(fx, bot, 6, WOOD[2])
    p.rect(x, top, w, bot - top, WOOD[2])
    timber(p, x, top + 2, w, bot - top - 2, WOOD, plank=9, nails=False)
    p.vline(x, top, bot - top, WOOD[4])
    p.vline(x + 1, top + 2, bot - top - 2, WOOD[3])
    p.vline(x + w - 1, top, bot - top, OAK[0])
    p.dither(x + w * 2 // 3, top + 2, w // 3, bot - top - 2, OAK[1], 0.4)
    p.dither(x, bot - 4, w, 4, OAK[1], 0.5)
    p.hline(x, bot - 1, w, OAK[0])
    p.poly([(x + 4, top - lid), (x + w - 5, top - lid), (x + w - 1, top), (x, top)], WOOD[4])     # the top plane
    p.dither(x + 3, top - lid + 1, w - 6, lid - 1, WOOD[3], 0.35)
    p.line(x + 4, top - lid, x + w - 5, top - lid, OAK[0])
    p.line(x, top, x + 4, top - lid, PALE_WOOD[4])
    p.line(x + w - 1, top, x + w - 5, top - lid, WOOD[2])
    p.line(x + 6, top - lid + 2, x + w - 7, top - lid + 2, BRASS[2])                          # inlay line
    p.hline(x, top, w, PALE_WOOD[4])                                       # the lit front edge of the lid
    p.hline(x, top + 1, w, OAK[0])
    p.hline(x + 1, top + 2, w - 2, WOOD[1])
    for sx in (x + 5, x + w - 9):                                          # iron straps with rivets
        p.rect(sx, top + 2, 4, bot - top - 2, IRON[2])
        p.vline(sx, top + 2, bot - top - 2, IRON[4])
        p.vline(sx + 3, top + 2, bot - top - 2, IRON[0])
        for ry in range(top + 6, bot - 3, 11):
            p.px(sx + 1, ry, BRASS[3])
    plate_w = max(10, w // 4)
    px0 = x + w * 5 // 12
    py0 = top + (bot - top) // 2 - 3
    p.rect(px0, py0, plate_w, 8, BRASS[2])                                 # the lock plate
    p.frame(px0, py0, plate_w, 8, BRASS[0])
    p.hline(px0 + 1, py0 + 1, plate_w - 2, BRASS[4])
    p.rect(px0 + plate_w // 2 - 1, py0 + 3, 2, 3, SHADOW)
    p.px(px0 + 1, py0 + 6, BRASS[4])
    p.px(px0 + plate_w - 2, py0 + 6, BRASS[4])
    for i, ph in enumerate((9, 12, 7)):                                    # pipes on the lid, each with its mouth and shadow
        qx = x + 10 + i * 6
        base = top - lid // 2
        p.dither(qx + 4, base - 2, 5, 3, SHADOW, 0.8)
        p.rect(qx, base - ph, 4, ph, BRASS[2])
        p.vline(qx, base - ph, ph, BRASS[4])
        p.vline(qx + 3, base - ph, ph, BRASS[0])
        p.ellipse(qx, base - ph - 1, 4, 3, BRASS[3])
        p.px(qx + 1, base - ph, SHADOW)
        p.px(qx + 2, base - ph, SHADOW)
    hx = x + w - 30                                                        # the horn, flaring up and to the right
    base = top - lid // 2
    cone(p, hx, base - 1, 3, hx + 24, y + (top - y) // 3, 9)
    mx, my = hx + 25, y + (top - y) // 3
    p.ellipse(mx - 4, my - 11, 9, 22, BRASS[3])                            # the mouth, a rim round the dark inside
    p.ellipse(mx - 3, my - 9, 6, 18, BRASS[1])
    p.ellipse(mx - 2, my - 7, 4, 14, SHADOW)
    p.vline(mx - 4, my - 6, 12, BRASS[4])
    p.rect(hx - 3, base - 5, 7, 6, BRASS[2])                               # the collar where it joins the lid
    p.hline(hx - 3, base - 5, 7, BRASS[4])
    p.hline(hx - 3, base, 7, BRASS[0])
    cy = top + 9                                                           # the crank
    p.rect(x - 6, cy, 7, 3, IRON[3])
    p.hline(x - 6, cy, 7, IRON[4])
    p.rect(x - 8, cy - 7, 3, 10, IRON[3])
    p.vline(x - 8, cy - 7, 10, IRON[4])
    p.ellipse(x - 10, cy - 9, 6, 5, WOOD[3])
    p.hline(x - 9, cy - 9, 4, PALE_WOOD[4])
    p.px(x - 1, cy + 1, BRASS[3])


def suggestion_box() -> Image.Image:
    """`reputation_box` (40x103): the landlord's letter box on the left post, half out of the picture: an iron-banded
    oak box under a sloped lid, a brass slot plate on its front, a label, a padlock."""
    def draw(p: Pix) -> None:
        p.poly([(0, 6), (36, 0), (40, 10), (40, 98), (0, 103)], OAK[1])
        p.poly([(0, 6), (30, 0), (34, 4), (0, 12)], WOOD[3])                    # the sloped lid
        p.line(0, 6, 30, 0, WOOD[4])
        p.poly([(8, 12), (34, 6), (34, 98), (8, 100)], WOOD[2])                 # the front
        p.poly([(0, 12), (8, 12), (8, 100), (0, 103)], WOOD[0])                 # the side in shade
        p.dither(0, 14, 8, 88, SHADOW, 0.5)
        for yy in (18, 44, 70, 92):
            p.rect(8, yy, 26, 1, WOOD[1])
        p.vline(8, 12, 88, WOOD[4])
        p.vline(33, 8, 90, WOOD[0])
        for sy in (14, 86):
            p.rect(8, sy, 26, 5, IRON[2])
            p.hline(8, sy, 26, IRON[4])
            p.hline(8, sy + 4, 26, IRON[0])
            p.px(12, sy + 2, BRASS[3])
            p.px(29, sy + 2, BRASS[3])
        p.rect(12, 28, 18, 13, BRASS[2])                                          # slot plate
        p.frame(12, 28, 18, 13, BRASS[0])
        p.hline(13, 29, 16, BRASS[4])
        p.rect(15, 33, 12, 3, SHADOW)
        p.hline(15, 36, 12, FLAME[1])
        p.dither(12, 29, 18, 12, BRASS[1], 0.15)
        p.rect(13, 50, 16, 20, PARCHMENT[3])                                      # label
        p.frame(13, 50, 16, 20, PARCHMENT[1])
        ink_lines(p, 15, 54, 12, 4, 3)
        nail(p, 14, 51)
        nail(p, 26, 51)
        p.rect(18, 74, 8, 7, BRASS[2])                                            # padlock
        p.frame(18, 74, 8, 7, BRASS[0])
        p.frame(19, 70, 6, 6, IRON[3])
        p.px(21, 77, SHADOW)
        p.glow(20, 34, 14, FLAME[2], 0.25)
    return on_layer((0, 264, 40, 367), draw, 10)


def straw_roll(p: Pix, cx: int, cy: int, r: int, dx: int, dy: int, length: int, straps: int = 2) -> None:
    """A rolled straw mat lying with its round end toward the viewer at (cx, cy) and its body running away along
    (dx, dy) for `length` pixels. The body is woven straw (stripes along the axis, cross ties every few pixels) with
    leather straps; the end shows the spiral of the roll, a wine-red blanket rolled up inside the straw."""
    norm = math.hypot(dx, dy)
    ax, ay = dx / norm, dy / norm                       # along the roll
    nx, ny = -ay, ax                                    # across it
    ex, ey = cx + ax * length, cy + ay * length
    body = [(round(cx + nx * r), round(cy + ny * r)), (round(ex + nx * r), round(ey + ny * r)),
            (round(ex - nx * r), round(ey - ny * r)), (round(cx - nx * r), round(cy - ny * r))]
    p.poly(body, PALE_WOOD[1])
    steps = max(1, r * 2)
    for i in range(steps + 1):                           # stripes along the axis, lit on the upper-left side
        t = i / steps * 2 - 1
        c = PALE_WOOD[3] if t < -0.45 else PALE_WOOD[2] if t < 0.1 else PALE_WOOD[1] if t < 0.6 else PALE_WOOD[0]
        if i % 4 == 1:
            c = tone(c, -0.15)
        p.line(round(cx + nx * r * t), round(cy + ny * r * t), round(ex + nx * r * t), round(ey + ny * r * t), c)
    for k in range(4, int(length), 5):                   # the cross ties of the weave
        sx, sy = cx + ax * k, cy + ay * k
        for j in range(-r, r, 3):
            q = ((j // 3) + (k // 5)) % 2
            if q:
                p.px(round(sx + nx * j), round(sy + ny * j), PALE_WOOD[0])
    for si in range(straps):                             # leather straps round the body
        t = (si + 1) / (straps + 1) * length * 0.85
        sx, sy = cx + ax * t, cy + ay * t
        for w_ in range(3):
            pa = (round(sx + nx * r + ax * w_), round(sy + ny * r + ay * w_))
            pb = (round(sx - nx * r + ax * w_), round(sy - ny * r + ay * w_))
            p.line(pa[0], pa[1], pb[0], pb[1], (LEATHER[2], LEATHER[3], LEATHER[1])[w_])
        p.px(round(sx + ax), round(sy + ay), BRASS[3])
    for yy in range(cy - r, cy + r + 1):                 # the round end, pixel by pixel
        for xx in range(cx - r, cx + r + 1):
            d = math.hypot(xx - cx, yy - cy)
            if d > r:
                continue
            ang = math.atan2(yy - cy, xx - cx)
            lit = (-(xx - cx) - (yy - cy)) / (r * 1.4)          # +1 toward the light
            if d > r - 4:
                c = PALE_WOOD[3] if lit > 0.2 else PALE_WOOD[2] if lit > -0.4 else PALE_WOOD[1]
            else:
                spiral = d + ang * 3.2 / math.pi
                ring = int(spiral // 3)
                if ring % 2 == 0:
                    c = WINE[3] if lit > 0.1 else WINE[2] if lit > -0.5 else WINE[1]
                else:
                    c = PALE_WOOD[3] if lit > 0.1 else PALE_WOOD[2] if lit > -0.5 else PALE_WOOD[1]
                if int(spiral) % 3 == 0:
                    c = WINE[0] if ring % 2 == 0 else PALE_WOOD[0]
            p.px(xx, yy, c)
    p.ellipse(cx - 2, cy - 2, 5, 5, WINE[0])
    p.px(cx - 1, cy - 1, WINE[2])
    for _ in range(r * 3):                               # loose straws sticking out of the end
        th = p.rng.random() * math.tau
        q = r - p.rng.randrange(0, 4)
        px_, py_ = round(cx + math.cos(th) * q), round(cy + math.sin(th) * q)
        p.px(px_, py_, PALE_WOOD[4] if p.rng.random() < 0.5 else PALE_WOOD[0])
    for a10 in range(0, 360, 2):                         # rim: dark below right, lit above left
        th = math.radians(a10)
        shade = math.cos(th) + math.sin(th)
        p.px(round(cx + math.cos(th) * r), round(cy + math.sin(th) * r), PALE_WOOD[4] if shade < -0.7 else OAK[0] if shade > 0.1 else PALE_WOOD[0])


def bedroll() -> Image.Image:
    """`sleeping_bag` (159x145): two rolled straw bedrolls on the floor by the bar, strapped with leather, a
    wine-red blanket rolled up inside each."""
    def draw(p: Pix) -> None:
        p.ellipse(10, 112, 148, 32, SHADOW)
        straw_roll(p, 42, 58, 30, -3, -2, 34, 2)
        straw_roll(p, 112, 96, 42, -5, -3, 90, 3)
    return on_layer((801, 395, 960, 540), draw, 11)


# ---------------------------------------------------------------------------------------------- ropes and hanging things


def hanging_ropes(box: Box, lower: bool) -> Callable[[Pix], None]:
    """What hangs from the beam in the upper corners of the shop: herb bunches, onion strings, a coil of rope, a
    chain, and a wooden tally plaque. `lower` adds the frayed rope ends hanging down the left."""
    ox = box[0]

    def gx(x: int) -> int:
        return x - ox

    def draw(p: Pix) -> None:
        # top left: a bundle on a nail
        nail(p, gx(124), 4)
        herb_bunch(p, gx(133), 2, 17, 9)
        herb_bunch(p, gx(148), 0, 12, 7, dry=True)
        # left rope with a hanging onion string and a wooden spool
        rope(p, arc(gx(177), 42, gx(181), 112, 3), 2)
        p.rect(gx(175), 110, 12, 3, WOOD[3])
        p.rect(gx(177), 113, 8, 12, WOOD[2])
        p.hline(gx(177), 113, 8, WOOD[4])
        p.vline(gx(177), 113, 12, WOOD[3])
        p.hline(gx(177), 124, 8, OAK[0])
        p.rect(gx(175), 125, 12, 3, WOOD[1])
        # a lantern chain and rope looped over the top right
        chain(p, arc(gx(688), 0, gx(740), 34, 22))
        rope(p, arc(gx(712), 0, gx(776), 30, 20), 3)
        rope(p, arc(gx(776), 30, gx(782), 0, 4), 2)
        chain(p, arc(gx(800), 0, gx(752), 28, 6))
        # the tally plaque hung by a cord
        rope(p, [(gx(722), y) for y in range(40, 68)], 1)
        board(p, gx(692), 67, 62, 38, WOOD, OAK, 3)
        for i in range(5):
            p.vline(gx(702) + i * 5, 74, 12, PALE_WOOD[3])
        p.line(gx(700), 90, gx(727), 74, PALE_WOOD[4])
        for i in range(3):
            p.vline(gx(730) + i * 5, 74, 12, PALE_WOOD[3])
        p.hline(gx(699), 94, 48, OAK[1])
        for i in range(8):
            p.px(gx(700) + i * 6, 98, BRASS[3])
        # a rope running down the right of the opening, and a long onion string by the post
        rope(p, [(gx(852) + (1 if y > 140 else 0), y) for y in range(0, 190)], 1, LINEN)
        p.hline(gx(840), 190, 13, LINEN[1])
        p.vline(gx(840), 190, 52, LINEN[1])
        # right: ropes and herbs hung from the beam down to the radio
        for i, (rx, ry, sag) in enumerate(((886, 268, 6), (896, 266, -5), (906, 270, 4), (918, 272, -6))):
            rope(p, arc(gx(rx - 2 + i * 3), 0, gx(rx), ry, sag), 2 if i % 2 == 0 else 1, LINEN if i != 1 else LEATHER)
        herb_bunch(p, gx(930), 4, 30, 11)
        onion_string(p, gx(943), 0, 7)
        herb_bunch(p, gx(920), 140, 24, 9, dry=True)
        # the long sag curving to the radio on the bar
        rope(p, arc(gx(872), 120, gx(922), 266, 26), 2, LEATHER)
        if lower:
            for fx, fy, lean in ((160, 325, 14), (170, 330, 22)):
                pts = [(gx(fx) + round(lean * (y - fy) / 140) + round(3 * math.sin((y - fy) / 17)), y) for y in range(fy, 465)]
                rope(p, pts, 2 if lean < 20 else 1, LEATHER)
                p.hline(pts[-1][0] - 1, 465, 4, LEATHER[3])
    return draw


def wires_layer(lower: bool) -> Image.Image:
    """`wires` (842x467) / `wires2` (842x270): the ropes, chains and hanging herbs that stand where the game has cables.
    `wires2` is the upper part only."""
    box: Box = (118, 0, 960, 467 if lower else 270)
    return on_layer(box, hanging_ropes(box, lower), 12 + lower)


def table_ropes() -> Image.Image:
    """`wires_table` (194x49): a coil of rope on the bar by the music box, an end of cord trailing away, and a few herb
    sprigs lying on the planks."""
    def draw(p: Pix) -> None:
        p.ellipse(8, 28, 40, 18, SHADOW)
        for i, (w, h, yy) in enumerate(((36, 14, 24), (34, 13, 28), (32, 12, 32))):
            p.ellipse(10 + (36 - w) // 2, yy, w, h, LINEN[1] if i % 2 else LINEN[2])
            p.ellipse(13 + (36 - w) // 2, yy + 2, w - 6, h - 5, WOOD[1])
        p.ellipse(10, 22, 36, 14, LINEN[2])
        p.ellipse(13, 24, 30, 9, LINEN[1])
        p.ellipse(18, 26, 20, 5, SHADOW)
        for k in range(0, 36, 4):
            p.px(12 + k, 25 + (3 if 8 < k < 28 else 0), LINEN[3])
        rope(p, arc(40, 28, 120, 38, 6), 2)
        rope(p, arc(120, 38, 190, 12, -8), 1)
        for sx, sy in ((92, 12), (150, 30)):
            p.line(sx, sy, sx + 14, sy + 4, MOSS[1])
            p.line(sx + 2, sy - 1, sx + 12, sy + 2, MOSS[2])
            p.speckle(sx, sy - 2, 14, 7, (MOSS[3], MOSS[2], MOSS[0]), 0.35)
    return on_layer((766, 246, 960, 295), draw, 14)


def hanging_rope_end() -> Image.Image:
    """`connectimg wire` (24x244): a long rope hanging down the right of the window, ending in an iron hook."""
    def draw(p: Pix) -> None:
        pts = [(5 + round(2 * math.sin(y / 31)), y) for y in range(0, 226)]
        rope(p, pts, 2)
        p.rect(3, 224, 5, 5, LEATHER[2])
        p.rect(3, 224, 5, 1, LEATHER[3])
        for y, x in ((230, 5), (232, 4), (234, 5), (236, 7), (238, 9), (239, 11), (238, 12), (236, 12)):
            p.rect(x, y, 2, 2, IRON[3])
            p.px(x, y, IRON[4])
        p.line(12, 236, 12, 232, IRON[3])
    return on_layer((922, 34, 946, 278), draw, 15)


# ---------------------------------------------------------------------------------------------- the curio cabinet


def mitred_frame(p: Pix, w: int, h: int, t: int) -> None:
    """A heavy oak frame of four timbers mitred at the corners: a lit outer bevel, a flat face with grain, a dark inner
    rebate, a brass stud in each corner and along the rails."""
    for y in range(h):
        for x in range(w):
            if t <= x < w - t and t <= y < h - t:
                continue
            dl, dr, dtp, db = x, w - 1 - x, y, h - 1 - y
            edge = min(dl, dr, dtp, db)                                  # distance in from the outer edge
            inner = max(0, t - 1 - edge)                                 # the same from the rebate
            if edge == 0:
                c = WOOD[4] if (dl == 0 or dtp == 0) else OAK[0]
            elif edge == 1:
                c = WOOD[3] if (dl == 1 or dtp == 1) else OAK[1]
            elif inner == 0:
                c = OAK[0]
            elif inner == 1:
                c = OAK[2] if (dl == t - 2 or dtp == t - 2) else WOOD[1]
            else:
                lit = (dl < t and dl <= dtp and dl <= db) or (dtp < t and dtp < dl and dtp <= dr)
                c = WOOD[3] if lit else WOOD[2]
                vert = t <= y < h - t
                if ((y if vert else x) // 4 + (x if vert else y) * 5) % 11 == 0 and ((x if vert else y) % 3):
                    c = WOOD[1] if lit else WOOD[0]
            p.px(x, y, c)
    for k in range(t):                                                   # the mitre joints
        for cx, cy, sx, sy in ((0, 0, 1, 1), (w - 1, 0, -1, 1), (0, h - 1, 1, -1), (w - 1, h - 1, -1, -1)):
            p.px(cx + sx * k, cy + sy * k, OAK[0])
    for xx in range(t + 8, w - t - 4, 16):
        for yy in (t // 2, h - 1 - t // 2):
            p.px(xx, yy, BRASS[3])
            p.px(xx + 1, yy + 1, BRASS[0])
    for yy in range(t + 8, h - t - 4, 16):
        for xx in (t // 2, w - 1 - t // 2):
            p.px(xx, yy, BRASS[3])
            p.px(xx + 1, yy + 1, BRASS[0])
    for cx, cy in ((3, 3), (w - 6, 3), (3, h - 6), (w - 6, h - 6)):
        p.rect(cx, cy, 4, 4, BRASS[2])
        p.hline(cx, cy, 4, BRASS[4])
        p.vline(cx + 3, cy, 4, BRASS[0])


def curio_cabinet(box: Box, seed: int) -> Image.Image:
    """`display_case`, `_medium`, `_large`: a glass-fronted curio cabinet set into the wall, seen from slightly above: a
    heavy oak frame mitred at the corners with brass studs, the niche behind leaded glass (its dark back of boards, its
    side walls and the sill in perspective, a shelf whose top plane shows), and two broad gleams on the glass."""
    w, h = box[2] - box[0], box[3] - box[1]

    def draw(p: Pix) -> None:
        t = 10
        ix, iy, iw, ih = t, t, w - 2 * t, h - 2 * t
        d, dt, db = 7, 5, 8                                            # depth of the niche at its sides, top and sill
        bx, by, bw, bh = ix + d, iy + dt, iw - 2 * d, ih - dt - db
        # the back wall of boards, lit from the upper left
        p.rect(ix, iy, iw, ih, OAK[0])
        for k in range(0, bw, 12):
            bwid = min(12, bw - k)
            p.rect(bx + k, by, bwid, bh, OAK[2] if (k // 12) % 2 else OAK[1])
            p.vline(bx + k, by, bh, OAK[0])
            p.vline(bx + k + 1, by, bh, OAK[3] if (k // 12) % 2 else OAK[2])
        for i in range(bh // 2):                                       # light falls off toward the lower right
            p.dither(bx, by + i * 2, bw, 2, SHADOW, 0.3 * (i * 2 / bh))
        p.dither(bx + bw * 55 // 100, by, bw * 45 // 100, bh, SHADOW, 0.25)
        # the walls of the niche: left lit, right in shade, a dark reveal on top, the sill with its top plane in light
        p.poly([(ix, iy), (bx, by), (bx, by + bh), (ix, iy + ih)], OAK[3])
        p.dither(ix, iy, d, ih, OAK[2], 0.4)
        p.poly([(ix + iw - 1, iy), (bx + bw - 1, by), (bx + bw - 1, by + bh), (ix + iw - 1, iy + ih)], OAK[1])
        p.poly([(ix, iy), (ix + iw - 1, iy), (bx + bw - 1, by), (bx, by)], OAK[0])
        p.poly([(ix, iy + ih - 1), (ix + iw - 1, iy + ih - 1), (bx + bw - 1, by + bh), (bx, by + bh)], WOOD[3])
        p.dither(ix, iy + ih - db, iw, db, WOOD[2], 0.3)
        p.line(bx, by + bh, bx + bw - 1, by + bh, WOOD[1])
        for k in range(1, 4):
            p.hline(bx - k * 2 + 1 if False else ix + 1 + k, by + bh + (ih - dt - bh) * k // 4, iw - 2 - 2 * k, WOOD[2])
        # a shelf: the lit top plane, its front edge, the shade it throws below
        sy = by + bh * 62 // 100
        p.poly([(bx, sy - 4), (bx + bw - 1, sy - 4), (ix + iw - 1 - 2, sy), (ix + 2, sy)], WOOD[4])
        p.dither(bx, sy - 4, bw, 3, WOOD[3], 0.4)
        p.rect(ix + 2, sy, iw - 4, 4, WOOD[3])
        p.hline(ix + 2, sy, iw - 4, PALE_WOOD[4])
        p.hline(ix + 2, sy + 3, iw - 4, OAK[0])
        shadow_under(p, ix + 2, sy + 4, iw - 4, 7)
        # the leaded glass: lead bars, then two broad gleams over everything
        n = 1 if w < 160 else 2
        for i in range(1, n + 1):
            mx = ix + iw * i // (n + 1)
            p.rect(mx - 1, iy, 3, ih, IRON[1])
            p.vline(mx - 1, iy, ih, IRON[3])
            p.vline(mx + 1, iy, ih, IRON[0])
        my = by + bh * 40 // 100
        p.rect(ix, my - 1, iw, 3, IRON[1])
        p.hline(ix, my - 1, iw, IRON[3])
        p.hline(ix, my + 1, iw, IRON[0])
        for off, wide in ((iw // 3, 6), (iw * 3 // 4, 3)):
            for yy in range(ih):
                for j in range(wide):
                    xx = off + (ih - yy) * 2 // 3 - ih // 2 + j
                    if 0 <= xx < iw:
                        c = p.get(ix + xx, iy + yy)
                        if c[:3] not in (IRON[1][:3], IRON[3][:3], IRON[0][:3]):
                            p.px(ix + xx, iy + yy, mix(c[:3], GLASS[4], 0.2 if j else 0.3))
        p.hline(ix, iy, iw, mix(OAK[0], GLASS[3], 0.5))                   # glass edge catching the light, top and left
        p.vline(ix, iy, ih, mix(OAK[0], GLASS[3], 0.5))
        mitred_frame(p, w, h, t)
        for sx in (w // 2 - 7,):                                       # a brass escutcheon and a latch
            p.rect(sx, h - t + 2, 14, 6, BRASS[2])
            p.frame(sx, h - t + 2, 14, 6, BRASS[0])
            p.hline(sx + 1, h - t + 3, 12, BRASS[4])
            p.rect(sx + 6, h - t + 5, 2, 2, SHADOW)
        p.rect(w - t + 2, h // 2 - 7, 6, 14, IRON[2])                  # an iron hinge strap on the right post
        p.vline(w - t + 2, h // 2 - 7, 14, IRON[4])
        p.px(w - t + 4, h // 2 - 4, BRASS[3])
        p.px(w - t + 4, h // 2 + 3, BRASS[3])
    return on_layer(box, draw, seed)


# ---------------------------------------------------------------------------------------------- sprite sheets


def push_plate_bell(state: int) -> Callable[[Pix], None]:
    """One frame of the bell button (28x18): a brass oval push-plate with an embossed bell. State 0 is rest, 1 is
    hovered (brighter rim), 2 is pressed (sunk, darker)."""
    def draw(p: Pix) -> None:
        sink = 2 if state == 2 else 0
        p.ellipse(0, 6, 28, 12, SHADOW)
        p.ellipse(0, 4 + sink, 28, 12, BRASS[1] if state != 1 else BRASS[2])
        p.ellipse(1, 3 + sink, 26, 11, BRASS[2] if state != 2 else BRASS[1])
        p.ellipse(3, 4 + sink, 22, 8, BRASS[3] if state != 2 else BRASS[2])
        p.hline(7, 4 + sink, 14, BRASS[4])
        p.dither(14, 8 + sink, 10, 5, BRASS[1], 0.5)
        # the bell
        bx, by = 11, 4 + sink
        p.poly([(bx + 1, by + 6), (bx + 2, by + 1), (bx + 5, by + 1), (bx + 6, by + 6)], BRASS[0])
        p.hline(bx, by + 6, 8, BRASS[0])
        p.px(bx + 3, by + 7, BRASS[0])
        p.px(bx + 3, by, BRASS[0])
        p.vline(bx + 2, by + 2, 3, BRASS[4])
        if state == 1:
            p.frame(0, 3, 28, 12, BRASS[4])
    return draw


def push_plate_shutter(state: int) -> Callable[[Pix], None]:
    """One frame of the shutter button (31x30): an oak plate on iron corners with a round brass knob engraved with an
    up-and-down arrow. Hovered lights the knob, pressed sinks it."""
    def draw(p: Pix) -> None:
        p.rect(0, 0, 31, 30, WOOD[2])
        p.bevel(0, 0, 31, 30, WOOD[4], OAK[0])
        p.dither(2, 2, 27, 26, WOOD[3], 0.3)
        for cx, cy in ((2, 2), (26, 2), (2, 26), (26, 26)):
            p.rect(cx, cy, 3, 3, IRON[3])
            p.px(cx + 1, cy + 1, BRASS[4])
        sink = 1 if state == 2 else 0
        p.ellipse(5, 6, 22, 22, SHADOW)
        p.ellipse(4, 4, 22, 22, IRON[1])
        p.ellipse(5, 5 + sink, 20, 20, BRASS[2] if state != 2 else BRASS[1])
        p.ellipse(7, 7 + sink, 16, 16, BRASS[3] if state == 1 else BRASS[2])
        p.ellipse(7, 7 + sink, 12, 12, BRASS[4] if state == 1 else BRASS[3])
        p.ellipse(11, 11 + sink, 10, 10, BRASS[2])
        p.hline(9, 7 + sink, 6, BRASS[4])
        for yy, dy in ((9, 1), (21, -1)):                               # the arrows: tip and a bar
            for i in range(3):
                p.hline(15 - i, yy + sink + i * dy, 1 + i * 2, SHADOW)
        p.vline(15, 13 + sink, 5, SHADOW)
        if state == 1:
            p.frame(3, 3, 24, 24, FLAME[2])
    return draw


def sheet(size: tuple[int, int], frames: int, x0: int, pitch: int, y0: int, fw: int, fh: int,
          draw: Callable[[Pix, int], None], seed: int) -> Image.Image:
    """A sprite sheet of `frames` cells laid in a row: cell k is a canvas of fw x fh at (x0 + k * pitch, y0), painted by
    `draw(canvas, k)`."""
    out = Pix(*size)
    for k in range(frames):
        cell = Pix(fw, fh, seed=seed * 31 + k)
        draw(cell, k)
        out.paste(cell, x0 + k * pitch, y0)
    return out.finish()


def queue_board_frame(p: Pix, k: int) -> None:
    """A frame of `clientele-Sheet` (25x47): the queue board: a parchment under an oak frame lit by a flickering flame,
    three pegs at the foot that take turns to glow."""
    p.rect(0, 0, 25, 47, OAK[2])
    p.bevel(0, 0, 25, 47, OAK[4], OAK[0])
    p.dither(1, 1, 23, 45, OAK[3], 0.25)
    p.rect(3, 4, 19, 28, PARCHMENT[3])
    p.dither(3, 4, 19, 28, PARCHMENT[2], 0.18)
    p.hline(3, 4, 19, PARCHMENT[1])
    p.vline(3, 4, 28, PARCHMENT[1])
    p.dither(15, 4, 7, 28, PARCHMENT[2], 0.4)
    glow_y = 8 + (k * 5) % 20
    p.dither(3, glow_y, 19, 8, FLAME[3], 0.3)
    for r in range(8):
        p.hline(5, 8 + r * 3, 12 + (r * 5 + k) % 5, PARCHMENT[0])
    p.rect(3, 34, 19, 1, OAK[0])
    p.rect(2, 38, 21, 1, OAK[1])
    glows = (EMBER, MOSS[3], BRASS[3])
    for i in range(3):
        on = (i + k) % 3 == 0
        c = glows[i] if on else tone(glows[i], -0.55)
        p.rect(5 + i * 6, 41, 3, 3, c)
        p.px(5 + i * 6, 41, tone(c, 0.3))
    p.px(2, 2, BRASS[3])
    p.px(22, 2, BRASS[3])


def ink_scrawl_frame(p: Pix, k: int) -> None:
    """A frame of `client_counter-Sheet` (35x21): a faint haze of ink writing that appears over the tally board, a
    little more in each frame (the game fades it over the board)."""
    for r in range(5):
        xx, yy = 2, 3 + r * 4
        reach = 8 + (k + 1) * 6
        while xx < min(32, reach):
            n = p.rng.randrange(2, 6)
            p.hline(xx, yy, min(n, 32 - xx), (*OAK[1], 70))
            xx += n + 2


def tally_marks_frame(p: Pix, k: int) -> None:
    """A frame of `pc_count-Sheet` (22x23): chalk tally strokes, one more stroke each frame, the fifth drawn across."""
    n = k + 2
    for i in range(n):
        x = 3 + i * 4
        p.vline(x, 3, 14, PARCHMENT[4])
        p.vline(x + 1, 4, 13, PARCHMENT[2])
        p.px(x, 2, PARCHMENT[3])
    if n >= 5:
        p.line(1, 15, 20, 5, PARCHMENT[4])
        p.line(1, 16, 20, 6, PARCHMENT[2])
    p.speckle(0, 0, 22, 23, (PARCHMENT[1],), 0.01)


def music_notes_frame(p: Pix, k: int) -> None:
    """A frame of `recorder-Sheet` (40x24): a small music box whose crank turns through three positions while a note
    rises over its horn."""
    p.ellipse(0, 18, 36, 6, SHADOW)
    p.rect(4, 12, 28, 10, WOOD[2])
    timber(p, 4, 13, 28, 9, WOOD, plank=5, nails=False)
    p.poly([(4, 12), (32, 12), (30, 8), (7, 8)], WOOD[4])                      # the lid's top plane, foreshortened
    p.line(4, 12, 7, 8, PALE_WOOD[4])
    p.line(32, 12, 30, 8, WOOD[2])
    p.hline(7, 8, 24, WOOD[3])
    p.hline(4, 12, 28, PALE_WOOD[4])
    p.hline(4, 21, 28, OAK[0])
    p.rect(8, 4, 3, 6, BRASS[3])
    p.rect(13, 2, 3, 8, BRASS[3])
    p.vline(8, 4, 6, BRASS[4])
    p.vline(13, 2, 8, BRASS[4])
    p.poly([(24, 11), (30, 11), (38, 2), (38, 12)], BRASS[2])
    p.line(24, 11, 38, 2, BRASS[4])
    p.vline(38, 3, 9, BRASS[0])
    crank = ((0, 13, 3, 4), (1, 17, 3, 4), (1, 9, 3, 4))[k]
    p.rect(2, 15, 3, 2, IRON[3])
    p.rect(crank[0], crank[1], 3, 4, IRON[3])
    p.px(crank[0], crank[1], IRON[4])
    ny = 8 - k * 3
    p.rect(30 + k * 2, max(0, ny), 2, 2, FLAME[3])
    p.vline(31 + k * 2, max(0, ny - 4), 4, FLAME[3])
    p.px(32 + k * 2, max(0, ny - 4), FLAME[2])


def scribe_frame(p: Pix, k: int) -> None:
    """A frame of `tape anim-Sheet` (53x36), the recording machine of the bar: a scribe's sloped desk seen from above
    and in front (its top is a foreshortened trapezoid whose sides lean toward the vanishing point), a sheet on it, an
    ink pot, and a quill that moves along the line it is writing; the line grows each frame."""
    top_y, front_y, foot_y = 7, 24, 33
    p.ellipse(0, 31, 52, 5, SHADOW)                                            # the contact shadow
    p.poly([(9, top_y), (44, top_y), (51, front_y), (1, front_y)], WOOD[3])    # the desk top (rear edge narrower)
    p.poly([(11, top_y + 2), (43, top_y + 2), (48, front_y - 2), (4, front_y - 2)], PARCHMENT[3])   # the sheet
    p.dither(11, top_y + 2, 36, 6, PARCHMENT[2], 0.3)
    p.line(11, top_y + 2, 4, front_y - 2, PARCHMENT[4])
    p.line(9, top_y, 1, front_y, WOOD[4])                                      # lit left edge
    p.line(44, top_y, 51, front_y, WOOD[1])
    p.hline(9, top_y, 36, OAK[0])
    p.rect(1, front_y, 51, foot_y - front_y, WOOD[2])                          # the front of the desk
    p.hline(1, front_y, 51, PALE_WOOD[4])
    p.dither(1, front_y + 3, 51, foot_y - front_y - 3, WOOD[1], 0.5)
    p.hline(1, foot_y - 1, 51, OAK[0])
    p.vline(1, front_y, foot_y - front_y, WOOD[4])
    for r in range(2):                                                         # lines of writing follow the rows
        yy = 13 + r * 5
        x0 = 13 - (yy - top_y) // 4
        for i in range(x0, x0 + 4 + k * 4 + r * 2, 2):
            p.px(i, yy, PARCHMENT[0])
    qx = 14 + k * 4
    p.line(qx, 18, qx + 6, 6, PARCHMENT[4])
    p.line(qx + 1, 18, qx + 7, 6, PARCHMENT[2])
    p.px(qx - 1, 19, SHADOW)
    p.ellipse(40, 14, 9, 5, IRON[0])                                           # the ink pot: a drum seen from above
    p.rect(40, 11, 9, 5, IRON[2])
    p.vline(40, 11, 5, IRON[4])
    p.ellipse(40, 9, 9, 4, IRON[3])
    p.ellipse(42, 10, 5, 2, SHADOW)


def abacus_frame(p: Pix, k: int) -> None:
    """A frame of `desk animations1` (36x22): a counting frame with four rods of beads, the beads sliding over by one
    place from frame to frame."""
    p.rect(0, 0, 36, 22, WOOD[1])
    p.bevel(0, 0, 36, 22, WOOD[4], OAK[0])
    p.hline(1, 1, 34, WOOD[3])
    for r in range(4):
        y = 4 + r * 5
        p.hline(2, y + 1, 32, OAK[0])
        for i in range(9):
            pos = (i + (k * (r + 1))) % 12
            bx = 3 + pos * 2 + (0 if pos < 6 else 6)
            c = (WINE[3], BRASS[3], PALE_WOOD[3], MOSS[3])[r]
            p.rect(bx, y - 1, 2, 4, c)
            p.px(bx, y - 1, tone(c, 0.35))
            p.px(bx + 1, y + 2, tone(c, -0.5))
    p.vline(1, 1, 20, WOOD[4])


def slip_frame(color_a: Ramp, color_b: Ramp) -> Callable[[Pix, int], None]:
    """A frame of `desk animations2` / `3` (20x15): slanting strips of paper passing across the desk, the pattern moving
    two pixels in each frame so the strip appears to slide."""
    def draw(p: Pix, k: int) -> None:
        period = 10
        for x in range(-period, 20 + period):
            xx = x + (k * 2) % period
            if (x // 5) % 2 == 0:
                for y in range(15):
                    cx = xx + (14 - y) // 3
                    if 0 <= cx < 20:
                        p.px(cx, y, color_a[3] if y not in (0, 14) else color_b[1])
                        if 0 <= cx + 4 < 20 and (x // 5) % 2 == 0:
                            p.px(cx + 4, y, color_b[2])
            else:
                for y in range(15):
                    cx = xx + (14 - y) // 3
                    if 0 <= cx < 20:
                        p.px(cx, y, color_b[2] if y % 4 else color_b[3])
    return draw


def peg_strip_frame(p: Pix, k: int) -> None:
    """A frame of `desk animations4` (49x15): a groove of peg holes in an oak strip, as on a scoring board, with a brass peg
    that steps along it frame by frame."""
    p.rect(0, 0, 49, 15, WOOD[2])
    p.bevel(0, 0, 49, 15, WOOD[4], OAK[0])
    for r in (4, 10):
        for i in range(10):
            p.rect(4 + i * 4 + r % 3, r, 2, 2, OAK[0])
    px_ = 4 + (k * 5) % 40
    p.rect(px_ - 1, 2, 4, 6, BRASS[3])
    p.rect(px_ - 1, 2, 4, 1, BRASS[4])
    p.vline(px_ + 2, 3, 5, BRASS[1])
    p.hline(2, 7, 45, OAK[1])


# ---------------------------------------------------------------------------------------------- Resources sprites


def document_chest(level: int) -> Image.Image:
    """`dossier_0..3` (112x96): an open oak document chest on the bar, banded with iron, with a brass lock plate. Level 0
    is empty; 1 holds one sheet; 2 a ledger and sheets; 3 is crammed with ledger, scrolls, letters and a green book."""
    p = Pix(112, 96, seed=40 + level)
    p.ellipse(2, 82, 108, 14, SHADOW)
    # interior seen from above and in front
    p.poly([(14, 40), (98, 40), (106, 52), (6, 52)], OAK[0])
    p.dither(14, 40, 84, 12, SHADOW, 0.5)

    def sheet_up(x: int, y: int, w: int, h: int, skew: int) -> None:
        p.poly([(x, y + h), (x + skew, y), (x + skew + w, y), (x + w, y + h)], PARCHMENT[3])
        p.line(x + skew, y, x + skew + w, y, PARCHMENT[4])
        p.line(x, y + h, x + skew, y, PARCHMENT[4])
        p.line(x + skew + w, y, x + w, y + h, PARCHMENT[2])
        for i in range(3, h - 4, 4):
            p.hline(x + skew * (h - i) // h + 3, y + i, w - 8, PARCHMENT[1])

    def scroll(x: int, y: int, h: int, ribbon: Ramp) -> None:
        p.rect(x, y, 9, h, PARCHMENT[3])
        p.vline(x, y, h, PARCHMENT[4])
        p.vline(x + 8, y, h, PARCHMENT[1])
        p.ellipse(x, y - 2, 9, 4, PARCHMENT[4])
        p.ellipse(x + 2, y - 1, 5, 2, PARCHMENT[0])
        p.rect(x, y + h // 2, 9, 2, ribbon[2])
        p.px(x, y + h // 2, ribbon[3])

    if level >= 1:
        sheet_up(60, 14, 28, 36, -6)
    if level >= 2:
        p.rect(20, 8, 38, 40, WINE[2])                       # ledger standing in the chest
        p.bevel(20, 8, 38, 40, WINE[4], WINE[0])
        p.rect(22, 12, 34, 10, BRASS[2])
        p.frame(22, 12, 34, 10, BRASS[0])
        p.hline(23, 13, 32, BRASS[4])
        font.write(p, 25, 14, "DEBTS", BRASS[0])
        for cy in (8, 44):
            for cx in (20, 53):
                p.rect(cx, cy, 5, 5, BRASS[2])
                p.px(cx + 1, cy + 1, BRASS[4])
        p.dither(46, 10, 10, 36, WINE[1], 0.4)
        sheet_up(72, 20, 26, 30, 8)
        p.rect(92, 30, 12, 18, PARCHMENT[2])
    if level >= 3:
        scroll(8, 20, 28, WINE)
        scroll(98, 18, 30, MOSS)
        scroll(64, 4, 38, NAVY)
        p.rect(58, 18, 10, 30, MOSS[2])                      # a green book leaning
        p.vline(58, 18, 30, MOSS[3])
        p.vline(67, 18, 30, MOSS[0])
        p.rect(60, 22, 6, 5, BRASS[2])
        p.poly([(30, 36), (46, 30), (54, 38), (36, 46)], PARCHMENT[2])          # a sealed letter
        p.ellipse(41, 36, 6, 6, WINE[3])
        p.px(42, 37, WINE[4])
    # the front: a tapering plank face with iron bands
    front = [(6, 48), (106, 48), (98, 92), (14, 92)]
    face = Pix(112, 96, seed=70)
    face.rect(0, 40, 112, 56, WOOD[2])
    timber(face, 6, 48, 100, 44, WOOD, plank=11, nails=False)
    face.dither(70, 48, 40, 44, OAK[1], 0.4)
    face.clip(front)
    p.paste(face, 0, 0)
    p.line(6, 48, 14, 92, OAK[0])
    p.line(106, 48, 98, 92, OAK[0])
    p.line(7, 48, 15, 92, WOOD[4])
    p.rect(6, 46, 100, 3, WOOD[4])                          # the lit rim
    p.hline(6, 46, 100, PALE_WOOD[3])
    p.hline(6, 49, 100, OAK[0])
    p.poly([(14, 40), (6, 46), (106, 46), (98, 40)], WOOD[3])
    p.hline(14, 40, 84, PALE_WOOD[2])
    p.dither(60, 40, 40, 6, WOOD[1], 0.5)
    for bx, off in ((26, 4), (80, 3)):                       # iron straps follow the taper
        for yy in range(48, 92):
            sx = bx + round((yy - 48) * (0.18 if bx < 56 else -0.18))
            p.rect(sx, yy, 7, 1, IRON[2])
            p.px(sx, yy, IRON[4])
            p.px(sx + 6, yy, IRON[0])
            if (yy - 48) % 9 == 4:
                p.px(sx + 3, yy, BRASS[3])
    p.rect(46, 56, 20, 14, BRASS[2])                         # lock plate
    p.frame(46, 56, 20, 14, BRASS[0])
    p.hline(47, 57, 18, BRASS[4])
    p.rect(54, 61, 4, 6, SHADOW)
    p.px(55, 60, SHADOW)
    for cx in (48, 62):
        p.px(cx, 58, BRASS[4])
        p.px(cx, 68, BRASS[1])
    p.hline(14, 91, 84, OAK[0])
    p.hline(15, 92, 82, SHADOW)
    return p.finish()


CASK_CX, CASK_TOP, CASK_BOT, CASK_RY = 46, 30, 118, 11
# the shape the game gives the bin (its occupied area): the cask and its lid stay inside it
BIN_AREA: Final[list[Point]] = [(20, 7), (89, 7), (89, 121), (79, 138), (6, 138), (6, 43)]
LIQUID: Final[Ramp] = ((52, 28, 16), (72, 40, 18), (92, 52, 22), (122, 72, 28), (150, 92, 36), (222, 164, 72))


def _cask_hw(yc: float) -> float:
    """Half width of the cask at a height of its axis: a belly in the middle, narrower at both ends."""
    return 31 + 6 * (1 - ((yc - 76) / 46) ** 2)


def _cask_axis(x: int, y: int) -> tuple[float, float]:
    """For a pixel of the cask, the height on its axis (undoing the ellipse curve of the ends) and t, -1 at its left edge."""
    yc = float(y)
    t = 0.0
    for _ in range(3):
        hw = _cask_hw(yc)
        t = max(-1.0, min(1.0, (x - CASK_CX) / hw))
        yc = y - CASK_RY * math.sqrt(1 - t * t)
    return yc, t


def _ellipse_poly(cx: float, cy: float, a: float, b: float, tilt: float) -> list[Point]:
    """The points of a tilted ellipse (tilt in degrees, turning toward the upper right when negative)."""
    r = math.radians(tilt)
    pts = []
    for k in range(48):
        th = k / 48 * 2 * math.pi
        u, v = a * math.cos(th), b * math.sin(th)
        pts.append((round(cx + u * math.cos(r) - v * math.sin(r)), round(cy + u * math.sin(r) + v * math.cos(r))))
    return pts


def _cask_body(p: Pix) -> None:
    """The staves with their light from the upper left, bellied, and the iron hoops that follow the curve."""
    for y in range(CASK_TOP - CASK_RY, CASK_BOT + CASK_RY + 2):
        for x in range(CASK_CX - 40, CASK_CX + 41):
            yc, t = _cask_axis(x, y)
            if not (CASK_TOP <= yc <= CASK_BOT) or abs(x - CASK_CX) > _cask_hw(yc) + 0.5:
                continue
            ang = math.asin(max(-1.0, min(1.0, t)))
            pos = (ang / math.pi + 0.5) * 9
            stave = int(pos)
            v = 3.5 - 2.7 * (t + 1) / 2 + (0.35 if stave % 2 else -0.15)
            if yc > CASK_BOT - 14:
                v -= 0.5                                       # the foot is in its own shadow
            c = WOOD[max(0, min(4, round(v)))]
            if pos % 1 < 0.07 and stave:                       # the seam between two staves
                c = WOOD[0]
            elif (x * 7 + y * 3) % 11 == 0 and v > 1.2:        # a grain fleck
                c = WOOD[max(0, round(v) - 1)]
            p.px(x, y, c)
    for _ in range(70):                                        # grain streaks along the staves
        gx = CASK_CX - 36 + p.rng.randrange(72)
        gy = p.rng.randrange(CASK_TOP + 8, CASK_BOT - 4)
        if p.get(gx, gy)[3] and p.get(gx, gy + 3)[3]:
            p.vline(gx, gy, p.rng.randrange(3, 7), tone(p.get(gx, gy)[:3], -0.18))
    for hy, wide in ((CASK_TOP + 2, 6), (CASK_TOP + 19, 5), (CASK_BOT - 24, 5), (CASK_BOT - 4, 6)):
        hw = _cask_hw(hy)
        for x in range(CASK_CX - 40, CASK_CX + 41):
            t = (x - CASK_CX) / hw
            if abs(t) > 1.0:
                continue
            y = round(hy + CASK_RY * math.sqrt(1 - t * t))
            lit = 4 if t < -0.45 else 3 if t < 0.35 else 2
            p.vline(x, y, wide, IRON[lit - 1])
            p.px(x, y, IRON[lit])
            p.px(x, y + wide - 1, IRON[0])
            if (x - CASK_CX) % 15 == 7 and abs(t) < 0.9:
                p.px(x, y + 2, BRASS[3])
                p.px(x + 1, y + 3, BRASS[0])


def _sight_tube(p: Pix, level: int) -> None:
    """The gauge: a glass tube on the side of the cask between two brass fittings, joined to the cask by short pipes,
    with a brass scale of ticks. The murky liquid stands at exactly `level` per cent of the glass."""
    gx, top, bot = 64, 53, 113                    # the glass: x of its left edge, first and last row
    height = bot - top                            # 60 steps: 15 per quarter
    for py in (top - 6, bot + 3):                 # pipes into the cask and their flanges
        p.rect(54, py, 10, 4, BRASS[2])
        p.hline(54, py, 10, BRASS[4])
        p.hline(54, py + 3, 10, BRASS[0])
        p.rect(52, py - 1, 3, 6, BRASS[1])
        p.vline(52, py - 1, 6, BRASS[3])
        p.vline(54, py - 1, 6, BRASS[0])
    p.rect(gx - 2, top - 8, 11, height + 17, IRON[1])          # the dark steel back of the gauge
    p.rect(gx - 1, top - 7, 9, height + 15, IRON[0])
    p.rect(gx, top, 7, height + 1, GLASS[3])
    p.vline(gx, top, height + 1, GLASS[4])
    p.vline(gx + 1, top, height + 1, GLASS[4])
    p.vline(gx + 5, top, height + 1, GLASS[2])
    p.vline(gx + 6, top, height + 1, GLASS[1])
    rise = round(height * level / 100)
    if rise:
        y0 = bot - rise + 1
        p.rect(gx, y0, 7, rise, LIQUID[2])
        p.vline(gx + 1, y0, rise, LIQUID[4])
        p.vline(gx + 2, y0, rise, LIQUID[3])
        p.vline(gx + 5, y0, rise, LIQUID[1])
        p.vline(gx + 6, y0, rise, LIQUID[0])
        p.dither(gx + 2, y0, 4, rise, LIQUID[0], 0.35)
        p.hline(gx, y0, 7, LIQUID[5])                          # the meniscus
        for i in range(rise // 9):                             # dregs in it
            p.px(gx + 2 + (i * 3) % 4, y0 + 3 + i * 8, LIQUID[0])
        p.px(gx + 3, y0 + 2 + rise // 3, LIQUID[5])
    else:
        p.hline(gx + 1, bot, 5, LIQUID[1])                     # only a film of dregs at the foot
    p.vline(gx + 2, top + 2, 7, (222, 236, 232))               # a glint on the glass
    p.px(gx + 2, top + 11, (222, 236, 232))
    for fy, fh in ((top - 7, 7), (bot + 1, 7)):                # brass caps at the ends of the glass
        p.rect(gx - 2, fy, 11, fh, BRASS[2])
        p.hline(gx - 2, fy, 11, BRASS[4])
        p.vline(gx - 2, fy, fh, BRASS[3])
        p.hline(gx - 2, fy + fh - 1, 11, BRASS[0])
        p.vline(gx + 8, fy, fh, BRASS[1])
        p.px(gx + 3, fy + 3, BRASS[4])
        p.px(gx + 4, fy + 4, BRASS[0])
    p.rect(gx + 10, top - 2, 7, height + 5, BRASS[1])          # the scale: a tick at each quarter, a short one at each eighth
    p.vline(gx + 10, top - 2, height + 5, BRASS[3])
    p.vline(gx + 16, top - 2, height + 5, BRASS[0])
    for k in range(9):
        ty = bot - round(height * k / 8)
        major = k % 2 == 0
        p.hline(gx + 11 if major else gx + 13, ty, 5 if major else 3, SHADOW)
        if major:
            p.hline(gx + 11, ty + 1, 5, BRASS[4])


def _clip_to_disc(p: Pix, pts: list[Point], edge: int) -> None:
    """Keeps only a tilted disc and its edge `edge` pixels lower (both drawn as polygons, so the union has no seam)."""
    mask = Image.new("L", p.im.size, 0)
    d = ImageDraw.Draw(mask)
    d.polygon(pts, fill=255)
    d.polygon([(x, y + edge) for x, y in pts], fill=255)
    for k in range(1, edge):
        d.polygon([(x, y + k) for x, y in pts], fill=255)
    p.im.putalpha(ImageChops.multiply(p.im.getchannel("A"), mask))


def _junk(p: Pix, x: int, y: int, kind: int) -> None:
    """One piece of rubbish with a dark rim and a lit upper left: a bone, a cabbage leaf, a crumpled note, a fish head, a rag."""
    if kind == 0:                                              # a bone with two knobs
        p.rect(x, y + 1, 9, 2, PARCHMENT[3])
        p.rect(x - 1, y, 3, 4, PARCHMENT[4])
        p.rect(x + 7, y, 3, 4, PARCHMENT[3])
        p.hline(x, y + 3, 9, PARCHMENT[1])
    elif kind == 1:                                            # a cabbage leaf
        p.poly([(x, y + 4), (x + 3, y), (x + 8, y + 1), (x + 9, y + 5), (x + 4, y + 7)], MOSS[2])
        p.line(x + 1, y + 4, x + 8, y + 3, MOSS[3])
        p.px(x + 3, y + 1, MOSS[3])
        p.hline(x + 3, y + 6, 4, MOSS[0])
    elif kind == 2:                                            # a crumpled note
        p.poly([(x, y + 2), (x + 4, y), (x + 8, y + 2), (x + 7, y + 6), (x + 2, y + 6)], PARCHMENT[3])
        p.px(x + 3, y + 1, PARCHMENT[4])
        p.line(x + 2, y + 3, x + 6, y + 4, PARCHMENT[1])
        p.hline(x + 2, y + 6, 5, PARCHMENT[0])
    elif kind == 3:                                            # a fish head
        p.poly([(x, y + 3), (x + 5, y), (x + 10, y + 3), (x + 5, y + 7)], LINEN[2])
        p.px(x + 3, y + 3, SHADOW)
        p.hline(x + 5, y + 5, 4, LINEN[1])
        p.hline(x + 4, y + 1, 3, LINEN[3])
    else:                                                      # a wine-red rag
        p.poly([(x, y + 3), (x + 4, y), (x + 9, y + 2), (x + 7, y + 6), (x + 1, y + 6)], WINE[2])
        p.line(x + 1, y + 3, x + 7, y + 2, WINE[3])
        p.hline(x + 1, y + 6, 6, WINE[0])


def slop_barrel(level: int) -> Image.Image:
    """`trashcan0..100` (96x144): a wooden cask with a sight tube on its side, standing in the bin's place. The tube is
    a glass between brass fittings, joined to the cask by pipes, and the murky liquid in it stands at `level` per cent of its
    height (ticks at each eighth); inside the cask the rubbish rises with it, and at the top it heaps over the rim of the
    cask in front of the propped-open lid. All five pictures have the same cask, lid and tube and differ only in the fill."""
    p = Pix(96, 144, seed=50 + level)
    cx = CASK_CX
    p.ellipse(6, 118, 78, 19, SHADOW)                          # the floor: a pool of dark under the foot
    p.dither(2, 122, 86, 15, OAK[1], 0.5)
    lid = Pix(96, 144, seed=3)                                 # the lid, propped behind the rim: planks, an iron strap
    pts = _ellipse_poly(60, 19, 25, 9, -16)
    lid.poly([(x, y + 3) for x, y in pts], WOOD[0])
    lid.poly(pts, WOOD[3])
    for k in range(-4, 5):
        lid.line(60 + k * 6 - 4, 6, 60 + k * 6 + 4, 31, WOOD[1])
    lid.dither(36, 10, 50, 14, WOOD[2], 0.35)
    lid.line(38, 24, 84, 12, IRON[2])
    lid.line(38, 25, 84, 13, IRON[1])
    for rx in (46, 60, 74):
        lid.px(rx, 22 - (rx - 38) * 12 // 46, BRASS[3])
    _clip_to_disc(lid, pts, 3)
    lid.outline(SHADOW, inside=True)
    p.paste(lid, 0, 0)
    body = Pix(96, 144, seed=4)
    _cask_body(body)
    rx = round(_cask_hw(CASK_TOP))                             # the top: a rim of pale wood, the opening within
    body.ellipse(cx - rx, CASK_TOP - CASK_RY, 2 * rx + 1, 2 * CASK_RY + 1, WOOD[4])
    body.ellipse(cx - rx + 2, CASK_TOP - CASK_RY + 1, 2 * rx - 3, 2 * CASK_RY - 1, WOOD[3])
    body.ellipse(cx - rx + 3, CASK_TOP - CASK_RY + 3, 2 * rx - 5, 2 * CASK_RY - 4, OAK[0])
    _sight_tube(body, level)
    body.outline(SHADOW, inside=True)
    p.paste(body, 0, 0)
    ox, oy, ow, oh = cx - rx + 3, CASK_TOP - CASK_RY + 3, 2 * rx - 5, 2 * CASK_RY - 4
    inner = Pix(96, 144, seed=60 + level)                      # what lies in the cask, seen through the opening
    inner.dither(ox, oy, ow, oh, SHADOW, 0.55)
    inner.hline(ox + 3, oy + 1, ow - 6, WOOD[1])
    if level > 0:
        d = round((100 - level) / 100 * 8)
        inner.ellipse(ox, oy + d, ow, oh, LEATHER[1])
        inner.ellipse(ox + 2, oy + d + 1, ow - 4, oh - 3, MOSS[1])
        inner.dither(ox + 2, oy + d + 1, ow - 4, oh - 3, LEATHER[2], 0.45)
        inner.speckle(ox + 3, oy + d + 2, ow - 6, oh - 5, (MOSS[3], PARCHMENT[2], WINE[2], BRASS[2]), 0.05)
    mask = Image.new("L", (96, 144), 0)
    ImageDraw.Draw(mask).ellipse((ox, oy, ox + ow - 1, oy + oh - 1), fill=255)
    inner.im.putalpha(ImageChops.multiply(inner.im.getchannel("A"), mask))
    p.paste(inner, 0, 0)

    def lip() -> None:
        for x in range(cx - rx + 1, cx + rx):
            t = (x - cx) / rx
            yy = round(CASK_TOP + CASK_RY * math.sqrt(1 - t * t))
            p.vline(x, yy - 2, 3, WOOD[4] if t < 0.3 else WOOD[2])

    lip()                                                      # the front lip of the rim hides the foot of the contents
    heap = {0: 0, 25: 0, 50: 0, 75: 2, 100: 7}[level]
    rng = p.rng
    if heap:                                                   # rubbish above the rim
        blobs = []
        for _ in range(heap * 8):
            u = rng.random() * 2 - 1
            hx = cx + round(u * (rx - 6))
            hy = CASK_TOP + 2 - round((1 - u * u) ** 0.7 * (4 + heap * 2.3)) + rng.randrange(0, 6)
            blobs.append((hy, hx, rng.choice((MOSS[1], LEATHER[2], WINE[1], LEATHER[1], MOSS[2]))))
        for hy, hx, col in sorted(blobs):                      # back to front
            p.ellipse(hx - 5, hy, 11, 8, SHADOW)
            p.ellipse(hx - 4, hy, 9, 7, col)
            p.hline(hx - 2, hy, 4, tone(col, 0.25))
        pieces = ((-18, -5, 1), (-7, -13, 2), (6, -12, 0), (16, -6, 3), (-2, -5, 4), (-12, 0, 0), (12, 1, 1), (0, -18, 3))
        for i, (jx, jy, kind) in enumerate(pieces):
            if heap == 2 and i > 1:
                continue
            _junk(p, cx + jx - 4, CASK_TOP + jy - (2 if heap == 7 and jy < -5 else 0), kind)
        lip()
    p.clip(BIN_AREA)
    return p.finish()


def wine_rack(level: int) -> Image.Image:
    """`vending0..100` (64x112): the wine rack by the left of the window: an oak cabinet with five shelves of bottles
    (wine red, green, amber, with a brass cork) over a plank cupboard. `level` is the share of the 25 places that hold a
    bottle, the same bottles staying put from level to level."""
    p = Pix(64, 112, seed=80)
    p.ellipse(4, 100, 56, 10, SHADOW)
    body = [(12, 7), (53, 7), (57, 11), (57, 105), (8, 105), (8, 11)]
    p.poly(body, OAK[2])
    p.rect(8, 11, 4, 94, WOOD[3])                                  # the lit left post
    p.rect(8, 11, 1, 94, WOOD[4])
    p.rect(53, 11, 4, 94, OAK[1])                                  # the right side, in shade
    p.vline(56, 11, 94, OAK[0])
    p.line(12, 7, 8, 11, WOOD[3])
    p.hline(13, 7, 40, WOOD[4])
    p.rect(12, 8, 41, 2, WOOD[3])
    p.rect(12, 10, 41, 1, OAK[0])
    p.rect(12, 11, 41, 71, SOOT[0])                                # the back of the rack
    timber(p, 12, 11, 41, 71, OAK, plank=6, vertical=True, nails=False)
    p.dither(12, 11, 41, 71, SHADOW, 0.45)
    for i in range(1, 7):
        p.dither(12, 11 + i - 1, 41, 1, SHADOW, 0.8 - i * 0.12)    # the top of the niche is dark
    cols = (WINE, MOSS, WINE, GLASS, WINE)
    places: list[tuple[int, int, int]] = []
    for row in range(5):
        for c in range(5):
            places.append((15 + c * 7, 22 + row * 14 - 12 + (1 if row == 0 else 0), (row * 5 + c * 2) % 5))
    order = list(range(25))
    random.Random(5).shuffle(order)
    count = round(level * 25 / 100)
    stocked = set(order[:count])
    for row in range(5):
        sy = 22 + row * 14
        for c in range(5):
            idx = row * 5 + c
            if idx in stocked:
                bx, by, ci = places[idx]
                bottle(p, bx, by, cols[ci], label=(idx % 3 == 0))
        p.rect(12, sy, 41, 3, WOOD[3])                             # the shelf board in front of the bottle feet
        p.hline(12, sy, 41, WOOD[4])
        p.hline(12, sy + 2, 41, OAK[0])
        p.dither(40, sy, 13, 3, OAK[1], 0.5)
    p.rect(12, 79, 41, 3, WOOD[3])
    p.hline(12, 79, 41, WOOD[4])
    p.hline(12, 81, 41, OAK[0])
    # the cupboard under the rack
    p.rect(12, 84, 41, 19, WOOD[2])
    timber(p, 12, 84, 41, 19, WOOD, plank=9, nails=False)
    p.bevel(12, 84, 41, 19, WOOD[4], OAK[0])
    p.frame(15, 87, 35, 13, OAK[1])
    p.hline(16, 88, 33, WOOD[4])
    p.rect(29, 91, 8, 3, BRASS[2])
    p.hline(29, 91, 8, BRASS[4])
    p.px(29, 93, BRASS[0])
    p.rect(14, 24, 0, 0, CLEAR)
    return p.finish()


def cask_shelf(level: int) -> Image.Image:
    """`fountain0..100` (64x112): the cask shelf by the right of the window: an oak cabinet holding a big hooped cask head,
    a brass tap over a niche with a tankard, a glass sight tube beside it that shows the ale left (amber, rising with
    `level`), a plank cupboard below."""
    p = Pix(64, 112, seed=90)
    p.ellipse(4, 100, 56, 10, SHADOW)
    body = [(12, 7), (53, 7), (57, 11), (57, 105), (8, 105), (8, 11)]
    p.poly(body, OAK[2])
    p.rect(8, 11, 4, 94, WOOD[3])
    p.rect(8, 11, 1, 94, WOOD[4])
    p.rect(53, 11, 4, 94, OAK[1])
    p.vline(56, 11, 94, OAK[0])
    p.line(12, 7, 8, 11, WOOD[3])
    p.hline(13, 7, 40, WOOD[4])
    p.rect(12, 8, 41, 2, WOOD[3])
    p.rect(12, 10, 41, 1, OAK[0])
    p.rect(12, 11, 41, 71, SOOT[0])
    timber(p, 12, 11, 41, 71, OAK, plank=7, vertical=True, nails=False)
    p.dither(12, 11, 41, 71, SHADOW, 0.45)
    # the cask head: staves seen end-on inside two hoops
    cx, cy, r = 27, 29, 14
    p.ellipse(cx - r - 2, cy - r - 2, 2 * r + 5, 2 * r + 5, IRON[0])
    p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, IRON[3])
    p.ellipse(cx - r + 2, cy - r + 2, 2 * r - 3, 2 * r - 3, WOOD[2])
    for k in range(-r + 4, r - 3, 5):
        p.vline(cx + k, cy - r + 3, 2 * r - 5, WOOD[1] if (k // 5) % 2 else WOOD[3])
    p.dither(cx - 2, cy - r, r + 4, 2 * r, OAK[1], 0.45)
    p.ellipse(cx - 3, cy - 8, 6, 6, OAK[0])                        # the bung
    p.px(cx - 2, cy - 7, WOOD[4])
    p.px(cx - r, cy, IRON[4])
    # the tap and the niche
    p.rect(cx - 4, cy + r - 2, 8, 8, BRASS[2])
    p.rect(cx - 4, cy + r - 2, 8, 1, BRASS[4])
    p.vline(cx - 4, cy + r - 2, 8, BRASS[3])
    p.vline(cx + 3, cy + r - 2, 8, BRASS[0])
    p.rect(cx - 1, cy + r + 6, 3, 4, BRASS[3])
    p.rect(cx - 2, cy + r + 8, 6, 2, BRASS[1])
    p.rect(cx + 4, cy + r, 6, 2, BRASS[3])                          # the lever
    p.rect(cx + 8, cy + r - 3, 2, 4, WOOD[3])
    p.rect(14, 64, 24, 14, SOOT[1])                                 # the niche where a tankard stands
    p.frame(14, 64, 24, 14, OAK[0])
    p.rect(20, 66, 10, 10, PALE_WOOD[3])
    p.rect(20, 66, 10, 2, FLAME[3])
    p.vline(20, 66, 10, PALE_WOOD[4])
    p.vline(29, 66, 10, PALE_WOOD[1])
    p.hline(20, 70, 10, IRON[2])
    p.hline(20, 74, 10, IRON[2])
    p.rect(30, 68, 3, 6, PALE_WOOD[2])
    p.rect(12, 77, 26, 3, IRON[1])                                  # drip grate
    p.hline(12, 77, 26, IRON[3])
    # the sight tube
    tx, ty, th = 42, 12, 56
    p.rect(tx - 2, ty - 2, 8, th + 4, IRON[1])
    p.frame(tx - 2, ty - 2, 8, th + 4, IRON[0])
    p.rect(tx, ty, 4, th, GLASS[0])
    fill = round(th * level / 100)
    if fill:
        p.rect(tx, ty + th - fill, 4, fill, FLAME[2])
        p.vline(tx, ty + th - fill, fill, FLAME[3])
        p.vline(tx + 3, ty + th - fill, fill, FLAME[1])
        p.hline(tx, ty + th - fill, 4, FLAME[4])
    p.vline(tx, ty + 1, th - 2, GLASS[4]) if fill == 0 else None
    for gy in range(ty + 4, ty + th, 8):                            # the marks on the tube
        p.px(tx + 5, gy, BRASS[3])
    p.rect(tx - 2, ty - 2, 8, 2, BRASS[2])
    p.rect(tx - 2, ty + th, 8, 2, BRASS[2])
    p.rect(12, 79, 41, 3, WOOD[3])
    p.hline(12, 79, 41, WOOD[4])
    p.hline(12, 81, 41, OAK[0])
    p.rect(12, 84, 41, 19, WOOD[2])
    timber(p, 12, 84, 41, 19, WOOD, plank=9, nails=False)
    p.bevel(12, 84, 41, 19, WOOD[4], OAK[0])
    p.frame(15, 87, 35, 13, OAK[1])
    p.hline(16, 88, 33, WOOD[4])
    p.rect(29, 91, 8, 3, BRASS[2])
    p.hline(29, 91, 8, BRASS[4])
    p.px(29, 93, BRASS[0])
    return p.finish()


def ale_tap(with_cask: bool) -> Image.Image:
    """`faucet` / `faucet1` (160x80): a brass ale tap on a wooden bracket over an iron drip grate; `faucet1` has the
    horizontal cask on its cradle above it, full of ale."""
    p = Pix(160, 80, seed=100 + with_cask)
    cx = 81
    if with_cask:
        p.ellipse(10, 6, 142, 40, SHADOW)
        for x in range(7, 154):                                # the barrel: staves bulging at the middle
            t = (x - 80) / 73
            bulge = round(18 * math.sqrt(max(0.0, 1 - t * t)) ** 0.5)
            y0, y1 = 20 - bulge, 20 + bulge
            stave = (y0 // 1)
            for y in range(y0, y1 + 1):
                k = (y - y0) / max(1, y1 - y0)
                c = WOOD[4] if k < 0.12 else WOOD[3] if k < 0.35 else WOOD[2] if k < 0.65 else WOOD[1] if k < 0.9 else OAK[0]
                if (y - y0) % 6 == 5:
                    c = OAK[0]
                p.px(x, y, c)
            del stave
        for hx in (24, 52, 108, 136):
            t = (hx - 80) / 73
            bulge = round(18 * math.sqrt(max(0.0, 1 - t * t)) ** 0.5)
            p.rect(hx, 20 - bulge, 6, 2 * bulge + 1, IRON[2])
            p.vline(hx, 20 - bulge, 2 * bulge + 1, IRON[4])
            p.vline(hx + 5, 20 - bulge, 2 * bulge + 1, IRON[0])
        p.rect(78, 14, 6, 6, OAK[0])                           # the bung
        p.rect(79, 15, 3, 2, WOOD[2])
        p.rect(60, 34, 42, 4, OAK[1])
        for lx in (20, 128):                                   # the cradle
            p.poly([(lx, 30), (lx + 18, 30), (lx + 22, 42), (lx - 4, 42)], OAK[2])
            p.hline(lx, 30, 18, OAK[4])
    # the bracket, the tap, the grate
    p.rect(cx - 12, 26 if with_cask else 9, 24, 12, WOOD[2])
    top = 26 if with_cask else 9
    p.bevel(cx - 12, top, 24, 12, WOOD[4], OAK[0])
    p.rect(cx - 12, top + 4, 24, 1, IRON[2])                    # an iron strap round the bracket block with rivets
    for rx_ in (cx - 10, cx + 8):
        p.px(rx_, top + 6, BRASS[3])
        p.px(rx_, top + 9, BRASS[3])
    p.dither(cx - 11, top + 10, 22, 2, SHADOW, 0.6)
    # the brass body of the tap: a horizontal barrel shaded top to bottom, a flange at the bracket, a spout going down
    for i in range(8):
        p.hline(cx - 10, top + 12 + i, 20, BRASS[(4, 3, 3, 2, 2, 1, 1, 0)[i]])
    p.vline(cx - 10, top + 12, 8, BRASS[4])
    p.rect(cx - 12, top + 12, 3, 8, BRASS[2])
    p.vline(cx - 12, top + 12, 8, BRASS[4])
    p.vline(cx - 10, top + 12, 8, BRASS[0])
    for i in range(10):                                          # the spout: a cylinder lit on its left
        col = BRASS[(4, 3, 3, 2, 2, 2, 1, 1, 0, 0)[i]]
        p.vline(cx - 5 + i, top + 20, 10, col)
    p.hline(cx - 5, top + 20, 10, BRASS[0])
    p.rect(cx - 7, top + 29, 14, 3, BRASS[2])                    # the flared nozzle
    p.hline(cx - 7, top + 29, 14, BRASS[4])
    p.hline(cx - 7, top + 31, 14, BRASS[0])
    p.rect(cx - 3, top + 32, 6, 2, SHADOW)
    p.line(cx + 4, top + 14, cx + 15, top + 5, WOOD[3])          # the lever, with a turned knob
    p.line(cx + 4, top + 15, cx + 15, top + 6, WOOD[1])
    p.ellipse(cx + 13, top + 1, 7, 7, WOOD[3])
    p.ellipse(cx + 14, top + 2, 4, 4, WOOD[4])
    p.px(cx + 14, top + 2, PALE_WOOD[4])
    for dy in range(4):                                          # a drip
        p.px(cx - 1, top + 36 + dy * 2, FLAME[2] if dy < 2 else CLEAR)
    p.px(cx - 1, top + 34, FLAME[3])
    gy = 62
    p.rect(47, gy, 68, 17, IRON[1])
    p.bevel(47, gy, 68, 17, IRON[4], IRON[0])
    p.rect(51, gy + 3, 60, 10, SOOT[0])
    for gx in range(53, 110, 4):
        p.vline(gx, gy + 3, 10, IRON[3])
    p.hline(49, gy + 16, 64, SHADOW)
    return p.finish()


def floor_grate() -> Image.Image:
    """`drain` (128x32): an iron grate set in a stone slab: bars across a dark opening, a chipped stone rim, a lit lip."""
    p = Pix(128, 32, seed=110)
    p.rect(4, 4, 112, 27, STONE[2])
    p.dither(4, 4, 112, 27, STONE[1], 0.3)
    p.bevel(4, 4, 112, 27, STONE[4], STONE[0])
    p.hline(5, 5, 110, STONE[3])
    p.rect(11, 9, 98, 15, SOOT[0])
    p.frame(11, 9, 98, 15, IRON[1])
    for gx in range(13, 108, 5):
        p.rect(gx, 10, 3, 13, IRON[2])
        p.vline(gx, 10, 13, IRON[4])
        p.vline(gx + 2, 10, 13, IRON[0])
    p.hline(12, 16, 96, IRON[1])
    p.speckle(4, 4, 112, 27, (STONE[0], STONE[4], MOSS[1]), 0.02)
    p.dither(4, 28, 112, 3, SHADOW, 0.6)
    return p.finish()


def music_box_sprite() -> Image.Image:
    """`cassette_player` (80x80): the music box as a sprite."""
    p = Pix(80, 80, seed=120)
    music_box(p, 7, 4, 72, 76)
    return p.finish()


def music_box_layer() -> Image.Image:
    """`radio` (77x327): ropes down from the beam to the music box that stands on the bar at the right edge of the
    picture; the box is cut by the edge."""
    def draw(p: Pix) -> None:
        for i, (rx, sag) in enumerate(((22, 4), (30, -3), (44, 3))):
            rope(p, arc(rx - 3, 0, rx + 2, 268, sag), 2 if i != 1 else 1, LINEN if i != 1 else LEATHER)
        herb_bunch(p, 60, 80, 24, 9)
        onion_string(p, 12, 120, 4)
        music_box(p, 4, 265, 85, 62)
    return on_layer((883, 0, 960, 327), draw, 16)


def push_asset(frames: Sequence[Callable[[Pix], None]], size: tuple[int, int], x0: int, y0: int, pitch: int,
               fw: int, fh: int, seed: int) -> Image.Image:
    """A three-frame button sheet."""
    return sheet(size, len(frames), x0, pitch, y0, fw, fh, lambda c, k: frames[k](c), seed)


# ---------------------------------------------------------------------------------------------- assets


def _build_assets() -> dict[str, Callable[[], Image.Image]]:
    a: dict[str, Callable[[], Image.Image]] = {
        "recorder-Sheet.144x32.png": lambda: sheet((144, 32), 3, 4, 48, 3, 40, 24, music_notes_frame, 25),
    }
    return a


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = _build_assets()
