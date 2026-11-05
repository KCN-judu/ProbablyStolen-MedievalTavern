"""The two small wall displays and their animated sheets, as tavern devices.

credit_display  the electronic credit readout becomes a counting slate: a limewashed board in an oak frame with iron
                corner straps, hung on a two-legged rope bridle from one iron eyebolt in the beam (a loaded bridle runs
                straight); below the clean writing face an abacus wire carries beads. The face stays plain paper: the
                game writes the figure there.
client_display  the visitor counter becomes a tally board: a small framed writing face over a peg rail with brass pegs
                (the way scores were kept by moving pegs), hung by two iron staples from the chains of the tally plaque.
clientele-Sheet the queue screen becomes a notice board nailed to the wall; its pegs glint in turn and a loose corner of
                the notice lifts in a draught and settles (a 4-frame loop).
client_counter-Sheet  a faint veil of chalk dust drifting over the tally board (translucent, as the original's).
pc_count-Sheet  chalk tally strokes whose chalk brightens and fades in a loop.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Final

from PIL import Image

import fxkit as fx
from palette import BRASS, IRON, LEATHER, OAK, PARCHMENT, SHADOW, WINE, WOOD, MOSS
from pix import Color, Pix, mix
from wal_kit import eyebolt, nail, oak_frame, on_layer

W, H = 960, 540


def _iron_strap(p: Pix, x: int, y: int, w: int, h: int, seed: int, rivets: bool = True) -> None:
    fx.iron_fill(p, (x, y, w, h), seed=seed, rust=0.15, hammer=0.4, scratches=0.2)
    if rivets and min(w, h) >= 3:
        fx.rivet(p, x + w - 2 if w >= h else x + 1, y + 1 if w >= h else y + h - 2, 1, BRASS, shadow=False)


def _writing_face(p: Pix, x: int, y: int, w: int, h: int, seed: int) -> None:
    """The clean face where the game writes: aged paper (limewash) with a darker rim, a soft shade under the upper rail.
    No lines, no marks in the middle."""
    fx.paper_fill(p, (x, y, w, h), folds=(0, 0), stains=0.12, foxing=0.08, shadow=False, seed=seed)
    for i in range(2):                                                  # the rail above shades the face
        p.dither(x + 1, y + i, w - 2, 1, PARCHMENT[1], 0.5 - i * 0.25)


def credit_display() -> Image.Image:
    """`credit_display` (82x103 at (97, 0)): the counting slate on its bridle."""
    def draw(p: Pix) -> None:
        cx, tx, ty = 50, 22, 75                                        # bridle ring x; tablet corner
        tw, th, t = 56, 28, 4
        l_eye, r_eye = (tx + 6, ty), (tx + tw - 7, ty)
        # the tablet: soft shadow on the wall, frame, face, abacus
        fx.wall_shadow(p, (tx, ty, tw, th), offset=(3, 4), spread=3, strength=0.8)
        oak_frame(p, tx, ty, tw, th, t, WOOD, seed=3)
        p.rect(tx + t, ty + t, tw - 2 * t, th - 2 * t, OAK[1])
        _writing_face(p, tx + t, ty + t, tw - 2 * t, 13, 6)
        ay = ty + t + 14
        p.rect(tx + t, ay, tw - 2 * t, 3, OAK[2])                      # the foot rail under the face
        p.hline(tx + t, ay, tw - 2 * t, OAK[4])
        p.hline(tx + t, ay + 2, tw - 2 * t, OAK[0])
        wy = ay + 6                                                    # the abacus wire and its beads
        p.hline(tx + t + 2, wy, tw - 2 * t - 4, BRASS[3])
        p.hline(tx + t + 2, wy + 1, tw - 2 * t - 4, BRASS[0])
        bead_cols = (WINE[3], MOSS[3], BRASS[4], WINE[3], MOSS[3])
        for i in range(14):
            bx = tx + t + 3 + i * 3 + (4 if i > 8 else 0)              # beads gathered left, a gap, then slid right
            c = bead_cols[i % 5]
            p.rect(bx, wy - 1, 2, 3, mix(c, SHADOW, 0.45))
            p.px(bx, wy - 1, mix(c, (255, 240, 200, 255), 0.5))
            p.px(bx, wy, c)
        # iron corner straps with rivets
        for sx, sy, ex, ey in ((tx, ty, 1, 1), (tx + tw, ty, -1, 1), (tx, ty + th, 1, -1), (tx + tw, ty + th, -1, -1)):
            hx = sx if ex > 0 else sx - 8
            vy = sy if ey > 0 else sy - 3
            _iron_strap(p, hx, vy, 8, 3, 11 + sx + sy)
            vx = sx if ex > 0 else sx - 3
            hy = sy if ey > 0 else sy - 8
            _iron_strap(p, vx, hy, 3, 8, 13 + sx + sy)
        # eye staples on the top rail, then the bridle: two straight legs from the beam's eyebolt
        for ex, ey in (l_eye, r_eye):
            fx.iron_fill(p, (ex - 2, ey - 3, 5, 4), seed=ex, rust=0.1, scratches=0.0)
            p.hline(ex - 1, ey - 5, 3, IRON[4])
            p.px(ex - 2, ey - 4, IRON[3])
            p.px(ex + 2, ey - 4, IRON[1])
            p.hline(ex - 1, ey - 3, 3, IRON[0])
        eyebolt(p, cx, 24, ring=6, drop=2)
        for end in (l_eye, r_eye):
            fx.rope(p, [(cx, 31), (end[0] + (cx - end[0]) * 0.02, end[1] - 4)], 3, seed=end[0])
        p.rect(cx - 2, 30, 5, 3, IRON[2])                              # a tied knot at the ring where both legs meet
        p.hline(cx - 2, 30, 5, IRON[4])
        for kx in (cx - 1, cx, cx + 1):
            p.px(kx, 32, fx.ROPE[2])
    return on_layer((97, 0, 179, 103), draw, 31)


def client_display() -> Image.Image:
    """`client_display` (49x46 at (696, 121)): the tally board with a clean face and a peg rail."""
    def draw(p: Pix) -> None:
        bx, by, bw, bh, t = 0, 4, 46, 42, 3
        fx.wall_shadow(p, (bx, by, bw, bh), offset=(3, 3), spread=3, strength=0.8)
        oak_frame(p, bx, by, bw, bh, t, WOOD, seed=9)
        p.rect(bx + t, by + t, bw - 2 * t, bh - 2 * t, OAK[1])
        _writing_face(p, bx + t + 1, by + t + 1, bw - 2 * t - 2, 17, 8)
        ry = by + t + 20                                               # the rail
        p.rect(bx + t, ry, bw - 2 * t, 2, OAK[2])
        p.hline(bx + t, ry, bw - 2 * t, OAK[4])
        for row in range(2):                                           # the peg rail: two rows of holes, brass pegs in a few
            for i in range(8):
                hx, hy = bx + t + 4 + i * 4, ry + 5 + row * 6
                p.rect(hx, hy, 2, 2, OAK[0])
                p.px(hx, hy + 1, OAK[3]) if False else None
        for hx, hy, c in ((bx + t + 4, ry + 5, BRASS), (bx + t + 4 + 4 * 3, ry + 5, BRASS), (bx + t + 4 + 4 * 5, ry + 11, BRASS)):
            fx.rivet(p, hx, hy, 1, c, shadow=True)
        # staples on the top rail, holding the chains that come down from the plaque
        for ex in (10, 36):
            fx.iron_fill(p, (ex - 2, by - 1, 5, 4), seed=ex, rust=0.1, scratches=0.0)
            for a in range(0, 360, 30):
                p.px(ex + round(math.cos(math.radians(a)) * 2), by - 3 + round(math.sin(math.radians(a)) * 2),
                     IRON[4] if math.cos(math.radians(a - 225)) > 0.2 else IRON[1])
        for cx_, cy_ in ((bx + 1, by + 1), (bx + bw - 3, by + 1), (bx + 1, by + bh - 3), (bx + bw - 3, by + bh - 3)):
            fx.rivet(p, cx_ + 1, cy_ + 1, 1, BRASS, shadow=False)
    return on_layer((696, 121, 745, 167), draw, 32)


# ---------------------------------------------------------------------------------------------- sheets


def _sheet(size: tuple[int, int], frames: int, x0: int, pitch: int, y0: int, fw: int, fh: int,
           draw: Callable[[Pix, int], None], seed: int) -> Image.Image:
    out = Pix(*size)
    for k in range(frames):
        cell = Pix(fw, fh, seed=seed * 31 + k)
        draw(cell, k)
        out.paste(cell, x0 + k * pitch, y0)
    return out.finish()


def _notice_frame(p: Pix, k: int) -> None:
    """A frame of `clientele-Sheet` (25x46): an oak board nailed to the wall with a pinned notice; the notice's lower
    right corner lifts in the draught (rises over frames 0..2, settles on 3) and the three pegs below glint in turn."""
    fx.wall_shadow(p, (1, 1, 22, 43), offset=(1, 2), spread=1, strength=0.7)
    oak_frame(p, 0, 0, 24, 44, 3, WOOD, seed=21)
    p.rect(3, 3, 18, 38, OAK[1])
    _writing_face(p, 4, 4, 16, 26, 12)
    lift = (0, 2, 4, 2)[k]
    if lift:                                                           # the corner folds up over the notice and shows its back
        cx_, cy_ = 19, 29
        for i in range(lift + 1):
            for j in range(lift + 1):
                if i + j < lift:
                    p.px(cx_ - i, cy_ - j, OAK[1])                     # bare board where the corner was
                elif i + j == lift:
                    p.px(cx_ - i, cy_ - j, PARCHMENT[4])               # the fold, catching the light
                else:
                    p.px(cx_ - i, cy_ - j, PARCHMENT[3] if i + j < lift + 2 else PARCHMENT[2])
        for i in range(lift + 1):                                      # shadow under the lifted flap
            p.px(cx_ - i - 1, cy_ - (lift - i) + 1 + 0, PARCHMENT[0]) if False else None
    ry = 33
    p.rect(3, ry, 18, 2, OAK[2])
    p.hline(3, ry, 18, OAK[4])
    for i in range(3):
        on = (i + k) % 3 == 0
        px_, py_ = 6 + i * 6, ry + 5
        p.rect(px_ - 1, py_ - 1, 4, 4, OAK[0])
        fx.rivet(p, px_ + 1, py_ + 1, 1, BRASS, shadow=False)
        if on:
            p.px(px_, py_, (255, 244, 190, 255))
            p.px(px_ + 1, py_ + 1, BRASS[4])
    for nx, ny in ((2, 2), (21, 2)):
        fx.rivet(p, nx, ny, 1, IRON, shadow=False)


def _chalk_dust(p: Pix, k: int) -> None:
    """A frame of `client_counter-Sheet` (35x21): a faint veil of chalk dust over the tally board, moving a pixel a frame
    (a loop of four). Translucent, like the original."""
    for y in range(1, 20):
        for x in range(1, 34):
            n = fx.vnoise((x + k * 2) / 3.0, y / 2.5, 7)
            if n > 0.62:
                p.px(x, y, (*PARCHMENT[4][:3], 26 if n > 0.74 else 14))


def _tally_frame(p: Pix, k: int) -> None:
    """A frame of `pc_count-Sheet` (22x23): chalk strokes, gate of three and three short ones below; the chalk brightens
    and fades over the four frames."""
    glow = (0.55, 0.8, 1.0, 0.8)[k]
    base = mix(PARCHMENT[1], PARCHMENT[4], glow)
    for i in range(3):
        x = 4 + i * 5
        for y in range(2, 15):
            xx = x + (y - 2) // 6
            wob = 1 if fx.noise(xx, y, 5) > 0.7 else 0
            p.px(xx, y, base if wob == 0 else mix(base, PARCHMENT[0], 0.5))
            p.px(xx + 1, y, mix(base, PARCHMENT[0], 0.45))
        p.px(x, 1, mix(base, (255, 255, 255, 255), 0.0))
        p.hline(x + 1, 18, 3, mix(base, PARCHMENT[1], 0.4))
        p.px(x + 4, 17, mix(base, PARCHMENT[0], 0.5))
    for i in range(14):                                                # dust of chalk falls from the strokes
        x, y = 3 + (i * 7 + k * 3) % 17, 3 + (i * 5 + k * 2) % 16
        if fx.noise(x, y, 11) > 0.6:
            p.px(x, y, mix(PARCHMENT[0], PARCHMENT[3], 0.5))


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "credit_display.960x540.png": credit_display,
    "client_display.960x540.png": client_display,
    "clientele-Sheet.105x48.png": lambda: _sheet((105, 48), 4, 1, 26, 1, 25, 46, _notice_frame, 22),
    "client_counter-Sheet.150x25.png": lambda: _sheet((150, 25), 4, 2, 37, 2, 35, 21, _chalk_dust, 23),
    "pc_count-Sheet.128x32.png": lambda: _sheet((128, 32), 4, 5, 32, 4, 22, 23, _tally_frame, 24),
}
