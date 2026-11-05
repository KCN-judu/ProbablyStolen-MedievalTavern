"""Medieval silhouette parts for the passer-by walkers: hats, hoods, masks, cloaks, packs, staves, a lantern, a basket.

Everything here is drawn from scratch by code (nothing is taken from the game's art), so the parts and their contact sheet
may be shared. Each part is painted in "units" (a standing figure is about 110 units tall, a head is 15 wide and 17 tall)
into a tone map (0 none, 1 shade, 2 body, 3 lit) at a supersampled size, reduced to whole pixels and coloured in one of three
size classes: `mid` (the 130x180 cells of the mid* sheets), `far` (the 32x45 cells of the far* sheets, a quarter size with the
thin parts widened) and `big` (walker1, 143x273 cells).

A part has an anchor on the figure (the head centre, the shoulder, the hand) and is a function of a few motion parameters
(`sway` -1..1, `sway_f`/`sway_b` knee reach in units, `swing` degrees) so that the composer can pose it frame by frame.
`python parts.py` writes the per-class PNGs, `parts.json` and `walker_parts_sheet.png` next to this file.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

Pt = tuple[float, float]
Colour = tuple[int, int, int, int]
SHADE, BODY, LIT = 1, 2, 3

CROWD = ((27, 22, 37, 255), (41, 34, 52, 255), (72, 61, 92, 255))     # dark, the official silhouette tone, rim
BIG = ((60, 33, 56, 255), (84, 47, 77, 255), (122, 76, 110, 255))


@dataclass(frozen=True)
class SizeClass:
    name: str
    scale: float            # pixels per unit
    ss: int                 # supersampling
    thr: float              # coverage a pixel needs to be solid
    tones: tuple[Colour, Colour, Colour]
    rim: bool               # light rim on upper edges
    min_px: float = 0.0     # thinnest stroke that must still show
    lit_bias: float = 1.4
    cell: tuple[int, int] = (130, 180)


CLASSES: dict[str, SizeClass] = {
    "mid": SizeClass("mid", 1.0, 4, 0.5, CROWD, True, 0.0, 1.4, (130, 180)),
    "far": SizeClass("far", 0.25, 8, 0.42, CROWD, False, 1.5, 0.8, (32, 45)),
    "big": SizeClass("big", 2.0, 3, 0.5, BIG, True, 0.0, 1.4, (143, 273)),
}


def rad(deg: float) -> float:
    return math.radians(deg)


def chaikin(pts: Sequence[Pt], rounds: int = 2) -> list[Pt]:
    cur = list(pts)
    for _ in range(rounds):
        nxt: list[Pt] = []
        n = len(cur)
        for i in range(n):
            a, b = cur[i], cur[(i + 1) % n]
            nxt.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            nxt.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        cur = nxt
    return cur


class Art:
    """A tone map painted in local units (x forward, y up) around an origin pixel, reduced to whole pixels."""

    def __init__(self, cls: SizeClass, ext: float) -> None:
        self.cls = cls
        self.o = math.ceil(ext * cls.scale)
        n = self.o * 2
        self.size = (n, n)
        self.img = Image.new("L", (n * cls.ss, n * cls.ss), 0)
        self.d = ImageDraw.Draw(self.img)
        self.s, self.ss = cls.scale, cls.ss
        self.min_u = cls.min_px / cls.scale

    def at(self, p: Pt) -> tuple[float, float]:
        return (self.o + p[0] * self.s) * self.ss, (self.o - p[1] * self.s) * self.ss

    def poly(self, pts: Sequence[Pt], tone: int = BODY) -> None:
        self.d.polygon([self.at(p) for p in pts], fill=tone)

    def smooth(self, pts: Sequence[Pt], tone: int = BODY, rounds: int = 2) -> None:
        self.poly(chaikin(pts, rounds), tone)

    def disc(self, c: Pt, r: float, tone: int = BODY) -> None:
        if tone != LIT:
            r = max(r, self.min_u / 2)
        self.ell(c, r, r, tone)

    def ell(self, c: Pt, rx: float, ry: float, tone: int = BODY) -> None:
        x, y = self.at(c)
        self.d.ellipse((x - rx * self.s * self.ss, y - ry * self.s * self.ss, x + rx * self.s * self.ss, y + ry * self.s * self.ss), fill=tone)

    def cap(self, a: Pt, ra: float, b: Pt, rb: float, tone: int = BODY) -> None:
        if tone != LIT:
            ra, rb = max(ra, self.min_u / 2), max(rb, self.min_u / 2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        self.poly([(a[0] + nx * ra, a[1] + ny * ra), (b[0] + nx * rb, b[1] + ny * rb), (b[0] - nx * rb, b[1] - ny * rb), (a[0] - nx * ra, a[1] - ny * ra)], tone)
        self.disc(a, ra, tone)
        self.disc(b, rb, tone)

    def line(self, a: Pt, b: Pt, w: float, tone: int) -> None:
        self.cap(a, w / 2, b, w / 2, tone)

    def reduce(self) -> list[list[int]]:
        """Whole-pixel tone map; the body tone is slightly favoured so thin cues stay crisp; lit rim along upper edges."""
        w, h = self.size
        c = self.cls
        covers = [list(self.img.point(lambda v, t=t: 255 if v == t else 0).resize(self.size, Image.Resampling.BOX).getdata()) for t in (SHADE, BODY, LIT)]
        solid = list(self.img.point(lambda v: 255 if v else 0).resize(self.size, Image.Resampling.BOX).getdata())
        out = [[0] * w for _ in range(h)]
        lim = c.thr * 255
        for i in range(w * h):
            if solid[i] >= lim:
                v = (covers[0][i], covers[1][i] * 1.15, covers[2][i] * c.lit_bias)
                out[i // w][i % w] = 1 + v.index(max(v))
        if c.rim:
            src = [row[:] for row in out]
            for y in range(2, h):
                for x in range(1, w):
                    if src[y][x] == BODY and src[y - 1][x] == 0 and src[y + 1 if y + 1 < h else y][x]:
                        out[y][x] = LIT
        return out


# ------------------------------------------------------------------------------------------------------ head, origin = head centre
# The skull is an ellipse 15 wide and 17 tall around (0, 0); the crown is at y = 8.5, the chin at about y = -8; the face is on +x.

def p_wide_brim(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A felt hat with a broad brim sloping down at the front, a hat band and a short feather swept back."""
    a.smooth([(-8, 3.5), (-7.4, 12.5), (-2, 15.2), (5, 13.8), (8, 3.5)], BODY)
    a.cap((-16.5, 3.4), 1.4, (17, 2.4), 1.4, BODY)
    a.ell((0.5, 3.2), 17, 2.4, BODY)
    a.line((-7.6, 5.6), (7.8, 5.8), 2.0, LIT)
    a.cap((-5.5, 7), 1.1, (-11, 10.5), 0.5, LIT)                                    # feather, fixed: swept back and slightly up


def p_floppy_cap(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A cap with a turned-up band; its round-ended bag hangs behind the head to the nape and swings a little."""
    a.ell((-0.5, 0.8), 8.4, 9.2, BODY)                                              # coif underneath
    a.smooth([(8.2, 3.6), (6.5, 10.5), (0.5, 14.5), (-6.5, 13), (-11.5, 8.5), (-13 - sway * 0.5, 1)], BODY, 2)
    a.smooth([(-6, 8), (-13, 6), (-15 - sway * 0.5, -1), (-13 - sway * 0.6, -6.5), (-8.5, -5.5), (-7, 1)], BODY, 2)
    a.disc((-12.5 - sway * 0.5, -3.5), 3.2, BODY)                                    # rounded end, no spike
    a.line((-8, 3.8), (8.2, 4.0), 2.6, LIT)
    a.line((-12.5, 5.5), (-13.5 - sway * 0.4, -1.5), 0.9, SHADE)                    # fold of the bag
    a.line((-7, -3), (1, -7.5), 1.2, SHADE)                                         # coif string


def p_tricorne(a: Art, **_: Any) -> None:
    a.smooth([(-15, 9.5), (-10, 4.5), (0, 3.2), (10, 4.5), (16, 9), (11, 9.5), (7, 14.5), (-6, 14.5), (-11, 10.5)], BODY, 1)
    a.line((-13.5, 9.5), (-9, 7), 1.2, LIT)
    a.line((14.5, 9), (10, 7), 1.2, LIT)
    a.line((-6, 5.6), (7, 5.8), 1.6, LIT)


def p_pointed_hat(a: Art, sway: float = 0.0, tall: float = 32.0, **_: Any) -> None:
    """A tall cone that bends over at the tip, on a broad brim; `tall` is the tip's height above the head centre."""
    k = (tall - 4) / 28.0
    def Y(y: float) -> float:
        return 4 + (y - 4) * k
    a.smooth([(-8, 4), (-7.4, Y(14)), (-10, Y(24 - sway)), (-19 * min(1, k + .3) - 2 * sway, Y(32)), (-7, Y(27)), (0.5, Y(17)), (7.5, 5)], BODY, 1)
    a.ell((0.5, 4.2), 17.5, 2.6, BODY)
    a.line((-8, 7), (7.2, 7), 2.4, LIT)
    a.line((17, 3.6), (6, 5.6), 1.0, LIT)


def p_helmet(a: Art, **_: Any) -> None:
    """A kettle hat: a dome with a rolled brim and a rivet row."""
    a.smooth([(-9, 3), (-9, 11), (-4, 15), (4, 15), (9, 11), (9, 3)], BODY, 2)
    a.ell((0, 3.2), 14.5, 2.5, BODY)
    a.line((-12, 3.8), (12, 3.8), 1.2, LIT)
    for x in (-5, 0, 5):
        a.disc((x, 8.5), 0.9, LIT)
    a.line((0.5, 14.5), (0.5, 4.5), 1.2, SHADE)


def p_coif(a: Art, **_: Any) -> None:
    """A linen coif tied under the chin, with a lit seam."""
    a.ell((-0.5, 1.0), 8.8, 9.8, BODY)
    a.line((-8, -2), (0, -7.5), 1.6, LIT)
    a.line((-0.5, 9.5), (-0.5, 3), 1.0, SHADE)


def p_kerchief_head(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A headscarf tied behind with two tails that flutter."""
    a.ell((-0.3, 1.2), 8.6, 9.6, BODY)
    a.line((-8, 4.2), (8, 4.6), 2.6, LIT)
    a.poly([(-7, 4), (-13 - sway, 2.5 + sway * 0.6), (-11, -1), (-6, 1)], LIT)
    a.poly([(-7, 3), (-12 - sway, -4 + sway), (-8, -6), (-5, 0)], LIT)


def p_hood(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A cloak's hood: a peaked cowl over the head, the face in shade, a lit rim, a droop behind."""
    a.smooth([(9.5, 0), (8.2, 9), (1, 15.5), (-8, 14), (-14 - sway, 6), (-16 - sway, -4), (-10, -10), (-2, -9), (7, -8)], BODY)
    a.ell((4.2, -0.5), 5.8, 7.4, SHADE)
    a.disc((8.2, -1.2), 1.6, BODY)
    a.cap((9.2, 6.5), 0.8, (3, 12.5), 0.8, LIT)
    a.cap((3, 12.5), 0.8, (-6, 12.5), 0.8, LIT)


def p_beak_mask(a: Art, **_: Any) -> None:
    """A plague doctor's mask: a long curved beak, a round glass eye and a leather coif behind."""
    a.smooth([(-9, -2), (-8.4, 8), (4, 6), (7, -6), (-3, -12)], BODY)
    a.smooth([(5, 4), (10.5, 1.5), (15.5, -2), (19.5, -8.5), (15.5, -8), (10.5, -4.5), (5, -3)], BODY, 2)
    a.cap((9, 1.4), 0.5, (17.5, -6), 0.5, LIT)
    a.disc((3.4, 2), 2.7, LIT)
    a.disc((3.8, 2), 1.4, SHADE)
    a.line((-8, -5), (4.5, -6.5), 1.0, SHADE)


# --------------------------------------------------------------------------------------------- shoulders, origin = neck base
# The origin is the point between the shoulders at the base of the neck; the hip is `hip` = (x, -L) below it.

def hem(hip: Pt, drop: float, wb: float, wf: float, sway_f: float, sway_b: float, k: float = 0.55, lift: float = 3.0) -> list[Pt]:
    """Outline of a hanging garment: from the shoulders to a hem that swings with the knees."""
    hb = (hip[0] - wb + k * sway_b, hip[1] - drop + lift)
    hf = (hip[0] + wf + k * sway_f, hip[1] - drop + lift * 0.4)
    hm = ((hb[0] + hf[0]) / 2, hip[1] - drop - 1.0)
    return [(-6, 3), (-12, -12), (hip[0] - wb + 1, hip[1] + 2), hb, hm, hf, (hip[0] + wf + 1.5, hip[1] + 2), (11, -11), (8, 2)]


def p_cloak(a: Art, hip: Pt = (-3, -30), drop: float = 26, w: float = 17, sway_f: float = 0.0, sway_b: float = 0.0, sway: float = 0.0, **_: Any) -> None:
    """A hooded travelling cloak: hangs from the shoulders, flares and swings; the front edge is lit, folds are dark."""
    a.smooth(hem(hip, drop, w, w, sway_f, sway_b, 0.9, 4.5), BODY)
    a.cap((hip[0] - 5, hip[1] + 14), 1.1, (hip[0] - 11 + 0.5 * sway_b, hip[1] - drop + 3), 0.7, SHADE)
    a.cap((hip[0] + 2, hip[1] + 10), 1.1, (hip[0] + 2 + 0.3 * (sway_f + sway_b), hip[1] - drop + 2), 0.7, SHADE)
    a.cap((hip[0] + 8, hip[1] + 12), 1.0, (hip[0] + 12 + 0.6 * sway_f, hip[1] - drop + 4), 0.7, SHADE)
    a.line((8, -4), (hip[0] + 15 + 0.8 * sway_f, hip[1] - drop + 3), 1.2, LIT)
    a.line((-5, -1), (5, -1), 2.0, LIT)                                  # clasp cord at the throat
    a.disc((0, -1), 1.3, LIT)


def p_coat_skirt(a: Art, hip: Pt = (-3, -30), drop: float = 30, sway_f: float = 0.0, sway_b: float = 0.0, **_: Any) -> None:
    """A long skirted coat: the skirt flares behind with the stride, a centre vent, buttons, a belt, a turned-up collar."""
    a.smooth(hem(hip, drop, 11, 13, sway_f, sway_b, 0.7, 2.5), BODY)
    a.poly([(hip[0] - 1, hip[1] + 2), (hip[0] + 1 + 0.5 * sway_f, hip[1] - drop + 2), (hip[0] + 3.5 + 0.5 * sway_f, hip[1] - drop + 2), (hip[0] + 3.5, hip[1] + 2)], SHADE)
    for i in range(3):
        a.disc((7.2 + i * 0.4, -7 - i * 9), 1.1, LIT)
    a.line((hip[0] - 9, hip[1] + 8), (hip[0] + 11, hip[1] + 8.5), 2.0, LIT)
    a.poly([(-5, 4), (11, -1), (6, -11), (1, -7)], LIT)
    a.poly([(-3, 3), (9, -0.5), (5, -8), (1, -5)], BODY)


def p_coat_cues(a: Art, hip: Pt = (-3, -30), sway_f: float = 0.0, **_: Any) -> None:
    """Cues for a coat that is already long: buttons, a belt, a turned-up collar and a dark centre vent (no new skirt)."""
    for i in range(3):
        a.disc((7.0 + i * 0.4, -7 - i * 8), 1.1, LIT)
    a.line((hip[0] - 8, hip[1] + 8), (hip[0] + 10, hip[1] + 8.5), 2.0, LIT)
    a.poly([(-5, 4), (11, -1), (6, -11), (1, -7)], LIT)
    a.poly([(-3, 3), (9, -0.5), (5, -8), (1, -5)], BODY)
    a.line((hip[0] + 1, hip[1] + 2), (hip[0] + 2 + 0.5 * sway_f, hip[1] - 26), 1.6, SHADE)


def p_cape(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A short shoulder cape whose hem lifts and settles."""
    a.smooth([(-6, 4), (-14, -4), (-13, -16 - sway), (4, -14), (13, -6), (8, 3)], BODY, 2)
    a.line((-12.5, -15 - sway), (3.5, -13), 1.3, LIT)
    a.line((-5, -1), (5, -1), 1.8, LIT)


def p_cloak_back(a: Art, hip: Pt = (-3, -30), drop: float = 30, sway_b: float = 0.0, w: float = 16, **_: Any) -> None:
    """The back of a cloak streaming behind the walker (drawn under the figure)."""
    a.smooth([(-5, 3), (-13, -6), (hip[0] - w + 0.9 * sway_b, hip[1] - drop), (hip[0] - w / 2 + 0.4 * sway_b, hip[1] - drop - 3), (hip[0] + 2, hip[1] - drop + 4), (hip[0] + 3, hip[1] + 4)], SHADE)
    a.cap((-9, -8), 1.0, (hip[0] - 11 + 0.7 * sway_b, hip[1] - drop + 3), 0.7, BODY)


def p_kerchief_neck(a: Art, sway: float = 0.0, **_: Any) -> None:
    """A neckerchief: a band round the neck with one knot tail fluttering behind."""
    a.cap((2, 2.0), 4.2, (0.5, 5.5), 3.8, LIT)
    a.poly([(-2.5, 4), (-9 - sway, 3 + sway * 0.5), (-8, -0.5), (-2, 1.5)], LIT)


def p_pack(a: Art, hip: Pt = (-3, -30), bob: float = 0.0, **_: Any) -> None:
    """A traveller's pack on the back: a satchel with a flap and a strap, a bedroll on top (drawn under the figure)."""
    a.smooth([(-6, 1), (-22, -4 + bob), (-26, -24 + bob), (-21, -34 + bob), (-8, -32)], BODY)
    a.smooth([(-10, -16), (-25, -18 + bob), (-24, -33 + bob), (-11, -31)], SHADE, 1)
    a.line((-24, -24 + bob), (-9, -25), 1.4, LIT)
    a.cap((-23, -1 + bob), 4.4, (-8, 0.5), 4.4, BODY)                                # bedroll
    a.line((-20, 3.8 + bob), (-20.5, -5 + bob), 1.4, LIT)
    a.line((-12, 4.6), (-12.4, -4), 1.4, LIT)
    a.line((-7, 4), (6, -6), 1.6, SHADE)                                             # shoulder strap across the chest


def p_satchel(a: Art, hip: Pt = (-3, -30), bob: float = 0.0, **_: Any) -> None:
    """A small leather satchel hanging at the hip from a strap."""
    a.smooth([(hip[0] - 5, hip[1] + 2), (hip[0] + 9, hip[1] + 3), (hip[0] + 10, hip[1] - 9 + bob), (hip[0] - 5, hip[1] - 8 + bob)], BODY, 1)
    a.line((hip[0] - 4, hip[1] - 1.6), (hip[0] + 9, hip[1] - 1.8), 1.2, LIT)
    a.disc((hip[0] + 3, hip[1] - 4.4 + bob), 1.0, LIT)


def p_belt(a: Art, half: float = 10.0, **_: Any) -> None:
    """A belt with a brass buckle across the middle (origin on the belt line, centred)."""
    a.line((-half, 0), (half, 0.4), 2.0, LIT)
    a.disc((half * 0.45, 0.2), 1.5, SHADE)


# --------------------------------------------------------------------------------------------- hands, origin = the hand
def p_staff(a: Art, drop: float = 55, tip: float = 12, **_: Any) -> None:
    """A walking staff held in the fist; the tip is `tip` units ahead and `drop` units below the hand; it runs on above the fist."""
    d = math.hypot(tip, drop) or 1.0
    ux, uy = -tip / d, drop / d                                                      # from the tip up through the hand
    top = (ux * 24, uy * 24)
    a.line(top, (tip, -drop), 2.4, BODY)
    a.line((top[0] - 0.9, top[1]), (tip - 0.9, -drop), 0.8, LIT)                      # a lit edge so it reads over the cloak
    a.line((ux * 4, uy * 4), (ux * 1, uy * 1), 2.6, LIT)                             # the hand's grip
    a.disc(top, 1.7, BODY)
    a.disc((tip, -drop + 0.6), 1.8, LIT)


def p_cane(a: Art, drop: float = 55, tip: float = 9, **_: Any) -> None:
    """A cane with a brass knob."""
    a.line((-1.5, 6), (tip, -drop), 2.0, BODY)
    a.disc((-1.5, 6.5), 2.6, LIT)


def p_lantern(a: Art, swing: float = 0.0, **_: Any) -> None:
    """A lantern on a short chain from the hand, swinging `swing` degrees: a pierced tin body with a lit pane."""
    sw = rad(swing)
    top = (0.0, -2.0)
    c, s = math.cos(sw), math.sin(sw)
    def rot(x: float, y: float) -> Pt:                                              # about the chain's top
        vy = y - top[1]
        return (top[0] + x * c + vy * s, top[1] - x * s + vy * c)
    cy = -11.0
    a.line(top, rot(0, cy + 6.5), 1.0, BODY)
    a.poly([rot(-3.6, cy + 4.2), rot(3.6, cy + 4.2), rot(4.3, cy - 5.4), rot(-4.3, cy - 5.4)], BODY)
    a.poly([rot(-2.1, cy + 2.6), rot(2.1, cy + 2.6), rot(2.6, cy - 3.8), rot(-2.6, cy - 3.8)], LIT)
    a.line(rot(-4.8, cy + 4.6), rot(4.8, cy + 4.6), 1.7, BODY)
    a.line(rot(-4.8, cy - 6), rot(4.8, cy - 6), 1.7, BODY)
    a.disc(rot(0, cy + 7.6), 1.4, BODY)


def p_basket(a: Art, swing: float = 0.0, **_: Any) -> None:
    """A wicker basket on the forearm: a curved handle, a woven body with lit weave rows and a cloth over the top."""
    sw = rad(swing)
    c, s = math.cos(sw), math.sin(sw)
    def rot(x: float, y: float) -> Pt:
        return (x * c + y * s, -x * s + y * c)
    a.smooth([rot(-7, -3), rot(7, -3), rot(5, -3), rot(0, 9), rot(-5, -3)], BODY, 1)
    a.poly([rot(-8, -3), rot(8, -3), rot(6, -14), rot(-6, -14)], BODY)
    a.poly([rot(-7, -3), rot(7, -3), rot(7.5, -5), rot(-7.5, -5)], LIT)
    for y in (-8, -11):
        a.line(rot(-6.3, y), rot(6.3, y), 1.0, SHADE)
    a.smooth([rot(-7, -1), rot(0, 1.5), rot(7, -1), rot(5, -4), rot(-5, -4)], LIT, 1)


# --------------------------------------------------------------------------------------------------------- registry
@dataclass(frozen=True)
class Part:
    draw: Callable[..., None]
    anchor: str                       # head | shoulder | hand | belt
    layer: str                        # back (under the figure) | front | inside (clipped to the figure)
    ext: float = 50.0                 # painted half-extent in units
    note: str = ""
    demo: dict[str, Any] = field(default_factory=dict)


PARTS: dict[str, Part] = {
    "wide_brim": Part(p_wide_brim, "head", "front", 40, "felt hat with a wide brim"),
    "floppy_cap": Part(p_floppy_cap, "head", "front", 40, "coif and floppy cap", {"sway": 1.5}),
    "tricorne": Part(p_tricorne, "head", "front", 40, "three-cornered hat"),
    "pointed_hat": Part(p_pointed_hat, "head", "front", 50, "tall bent pointed hat", {"sway": 1.0}),
    "helmet": Part(p_helmet, "head", "front", 40, "kettle hat"),
    "coif": Part(p_coif, "head", "front", 40, "linen coif"),
    "kerchief_head": Part(p_kerchief_head, "head", "front", 40, "tied headscarf", {"sway": 1.0}),
    "hood": Part(p_hood, "head", "front", 40, "cowl", {"sway": 1.0}),
    "beak_mask": Part(p_beak_mask, "head", "front", 45, "plague doctor beak mask"),
    "cloak": Part(p_cloak, "shoulder", "front", 90, "hooded travelling cloak", {"sway_f": 8, "sway_b": -6}),
    "coat_skirt": Part(p_coat_skirt, "shoulder", "front", 90, "long skirted coat", {"sway_f": 8, "sway_b": -6}),
    "coat_cues": Part(p_coat_cues, "shoulder", "front", 90, "collar, buttons, belt, vent for a long coat", {"sway_f": 8}),
    "cape": Part(p_cape, "shoulder", "front", 40, "short shoulder cape", {"sway": 1.0}),
    "cloak_back": Part(p_cloak_back, "shoulder", "back", 90, "cloak streaming behind", {"sway_b": -6}),
    "kerchief_neck": Part(p_kerchief_neck, "shoulder", "front", 40, "neckerchief", {"sway": 1.0}),
    "pack": Part(p_pack, "shoulder", "back", 70, "satchel pack with bedroll"),
    "satchel": Part(p_satchel, "shoulder", "front", 70, "hip satchel"),
    "belt": Part(p_belt, "belt", "inside", 30, "belt with buckle"),
    "staff": Part(p_staff, "hand", "front", 150, "walking staff"),
    "cane": Part(p_cane, "hand", "front", 150, "cane"),
    "lantern": Part(p_lantern, "hand", "front", 40, "swinging lantern", {"swing": 14}),
    "basket": Part(p_basket, "hand", "front", 40, "basket on the arm", {"swing": 6}),
}


def _far_wide_brim(a: Art, **_: Any) -> None:
    a.smooth([(-6, 2.5), (-5.5, 11), (5.5, 11), (6, 2.5)], BODY, 1)
    a.ell((0, 2.8), 20, 3.0, BODY)                                                   # brim 10 px against a 4 px head
    a.line((-5, 5.5), (5, 5.5), 2.0, LIT)


def _far_pointed_hat(a: Art, sway: float = 0.0, tall: float = 30.0, **_: Any) -> None:
    t = min(tall, 30.0)
    a.smooth([(-7, 2.5), (-5, 12), (-8, t - 8), (-13, t - 1), (-4, t - 5), (4, 10), (7, 2.5)], BODY, 1)
    a.ell((0, 2.8), 16, 3.0, BODY)
    a.line((-5, 6), (5, 6), 2.0, LIT)


def _far_beak(a: Art, **_: Any) -> None:
    a.ell((-1, 1), 9, 10, BODY)                                                      # the mask's coif
    a.poly([(4, 4), (14, 1), (24, -8), (21, -12), (13, -8), (4, -5)], BODY)
    a.disc((3.5, 2.5), 1.6, LIT)                                                     # the glass eye


def _far_hood(a: Art, **_: Any) -> None:
    a.ell((-2, 1), 12.5, 12.5, BODY)
    a.ell((5.5, 0), 4.5, 5.5, SHADE)                                                 # the dark notch of the opening
    a.line((-5, 12), (4, 12), 1.2, LIT)


def _far_cloak(a: Art, hip: Pt = (-3, -30), drop: float = 26, sway_f: float = 0.0, sway_b: float = 0.0, w: float = 15, **_: Any) -> None:
    a.smooth(hem(hip, drop, w, w, sway_f, sway_b, 0.9, 4.5), BODY)
    a.line((8, -4), (hip[0] + w - 2 + 0.8 * sway_f, hip[1] - drop + 3), 1.4, LIT)    # the lit front edge
    a.line((hip[0] - 3, hip[1] + 12), (hip[0] - 5 + 0.4 * sway_b, hip[1] - drop + 3), 1.0, SHADE)


def _far_lantern(a: Art, swing: float = 0.0, **_: Any) -> None:
    # a bright 2x2 pixel pane with a dark pixel above it (cap and chain), swinging on the chain
    sw = rad(swing)
    c, s = math.cos(sw), math.sin(sw)
    def rot(x: float, y: float) -> Pt:
        return (x * c + (y + 1) * s, -x * s + (y + 1) * c - 1)
    a.poly([rot(-3, -2), rot(3, -2), rot(3, -9), rot(-3, -9)], SHADE)
    a.poly([rot(-4.5, -9), rot(4.5, -9), rot(4.5, -18), rot(-4.5, -18)], LIT)


def _far_pack(a: Art, **_: Any) -> None:
    a.poly([(-6, 0), (-21, -2), (-21, -26), (-8, -28)], BODY)                        # a distinct bump behind the shoulders
    a.ell((-14, 0), 9.5, 4.5, BODY)                                                  # bedroll on top
    a.line((-18, -2), (-10, -2), 1.2, LIT)


def _far_floppy(a: Art, sway: float = 0.0, **_: Any) -> None:
    a.ell((-0.5, 1), 8.5, 9.5, BODY)
    a.smooth([(8, 3.5), (6, 11), (0, 15), (-8, 12), (-15, 4), (-16, -4), (-9, -4), (-8, 3)], BODY, 1)
    a.line((-8, 4), (8, 4.4), 2.4, LIT)


def _far_tricorne(a: Art, **_: Any) -> None:
    a.poly([(-19, 9), (-9, 3), (9, 3), (19, 9), (10, 7.5), (7, 14), (-7, 14), (-10, 7.5)], BODY)
    a.line((-6, 5.5), (6, 5.5), 1.6, LIT)


def _far_kerchief(a: Art, sway: float = 0.0, **_: Any) -> None:
    a.ell((1, 2), 5.5, 4, LIT)
    a.disc((-8, 1 + sway * 0.5), 2.6, LIT)


def _far_basket(a: Art, **_: Any) -> None:
    a.poly([(-6, -1), (6, -1), (5, -11), (-5, -11)], BODY)
    a.line((-6, -1), (6, -1), 1.6, LIT)


def _far_staff(a: Art, drop: float = 55, tip: float = 12, **_: Any) -> None:
    # a pale one-pixel stick so it reads against the dark body; the planted tip is a brighter dot
    d = math.hypot(tip, drop) or 1.0
    top = (-tip / d * 22, drop / d * 22)
    a.line(top, (tip, -drop), 3.5, LIT)
    a.disc((tip, -drop + 1), 2.2, LIT)


FAR_DRAW: dict[str, Callable[..., None]] = {
    "staff": _far_staff, "cane": _far_staff,
    "wide_brim": _far_wide_brim, "pointed_hat": _far_pointed_hat, "beak_mask": _far_beak, "hood": _far_hood, "cloak": _far_cloak,
    "lantern": _far_lantern, "pack": _far_pack, "floppy_cap": _far_floppy, "tricorne": _far_tricorne, "kerchief_neck": _far_kerchief,
    "basket": _far_basket,
}


def render(name: str, cls: str, **kw: Any) -> tuple[Image.Image, tuple[int, int]]:
    """Paint one part for a size class: (RGBA image cropped to its pixels, anchor position inside it)."""
    part, c = PARTS[name], CLASSES[cls]
    art = Art(c, part.ext)
    (FAR_DRAW.get(name, part.draw) if cls == "far" else part.draw)(art, **kw)
    grid = art.reduce()
    h, w = len(grid), len(grid[0])
    xs = [x for r in grid for x, t in enumerate(r) if t]
    ys = [y for y, r in enumerate(grid) for t in r if t]
    if not xs:
        return Image.new("RGBA", (1, 1)), (0, 0)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    im = Image.new("RGBA", (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0))
    px = im.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = grid[y][x]
            if t:
                px[x - x0, y - y0] = c.tones[t - 1]
    return im, (art.o - x0, art.o - y0)


# ------------------------------------------------------------------------------------------------------- sheet output
def write_all(folder: Path) -> None:
    """Per-class PNGs (a part with motion shows four phases side by side), parts.json and the contact sheet."""
    out = folder / "png"
    out.mkdir(exist_ok=True)
    meta: dict[str, Any] = {"units": "a standing figure is ~110 units; head 15x17; x forward, y up from the anchor",
                            "classes": {k: {"scale": v.scale, "cell": list(v.cell)} for k, v in CLASSES.items()}, "parts": {}}
    for name, part in PARTS.items():
        info: dict[str, Any] = {"anchor": part.anchor, "layer": part.layer, "note": part.note, "files": {}}
        for cn in CLASSES:
            phases = [part.demo]
            if "sway" in part.demo or "swing" in part.demo or "sway_f" in part.demo or "sway_b" in part.demo:
                phases = [{k: v * f for k, v in part.demo.items()} for f in (-1.0, -0.4, 0.4, 1.0)]
            ims = [render(name, cn, **ph) for ph in phases]
            w = sum(i.width for i, _ in ims) + 2 * (len(ims) - 1)
            h = max(i.height for i, _ in ims)
            strip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            anchors, x = [], 0
            for im, (ax, ay) in ims:
                strip.alpha_composite(im, (x, 0))
                anchors.append([x + ax, ay])
                x += im.width + 2
            fn = f"{name}.{cn}.png"
            strip.save(out / fn)
            info["files"][cn] = {"file": f"png/{fn}", "phases": len(ims), "anchors": anchors}
        meta["parts"][name] = info
    (folder / "parts.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    contact_sheet(folder / "walker_parts_sheet.png")


def dummy(cell: tuple[int, int], head: Pt) -> Image.Image:
    """A plain standing silhouette (my own, in the walkers' tone) for showing parts on."""
    t = CROWD[1]
    im = Image.new("RGBA", cell, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hx, hy = head
    d.ellipse((hx - 7, hy - 8, hx + 7, hy + 8), fill=t)
    d.polygon([(hx + 6, hy), (hx + 9, hy + 3), (hx + 5, hy + 4)], fill=t)
    d.rectangle((hx - 4, hy + 6, hx + 2, hy + 14), fill=t)
    d.polygon([(hx - 10, hy + 38), (hx - 8, hy + 14), (hx + 9, hy + 14), (hx + 9, hy + 38)], fill=t)
    d.rectangle((hx - 7, hy + 38, hx + 7, hy + 78), fill=t)
    d.rectangle((hx - 2, hy + 62, hx + 2, hy + 64), fill=CROWD[0])
    return im


def contact_sheet(path: Path) -> None:
    """The headgear set on its own (top), then the cloaks, packs and carried things on a plain walker, all at 4x mid size,
    with the far-size versions of the hats in a row at the bottom."""
    bg = (205, 192, 170, 255)
    heads = ["wide_brim", "floppy_cap", "tricorne", "pointed_hat", "helmet", "coif", "kerchief_head", "hood", "beak_mask"]
    bodies = [("cloak_back", "cloak"), ("cloak",), ("coat_cues", "tricorne"), ("cape",), ("pack",), ("satchel",), ("kerchief_neck",),
              ("staff",), ("cane",), ("lantern",), ("basket",), ("belt",)]
    cell, z, cols = (64, 112), 4, 9
    head, sh = (30, 34), (29, 48)
    hip = (sh[0] - 2, sh[1] + 29)
    hand = (sh[0] + 9, sh[1] + 33)
    c = CLASSES["mid"]
    tiles: list[Image.Image] = []
    for n in heads:
        t = Image.new("RGBA", cell, bg)
        t.alpha_composite(dummy(cell, head))
        im, (ax, ay) = render(n, "mid", **PARTS[n].demo)
        t.alpha_composite(im, (head[0] - ax, head[1] - ay))
        tiles.append(t)
    for combo in bodies:
        t = Image.new("RGBA", cell, bg)
        base = dummy(cell, head)
        layers = []
        for n in combo:
            part = PARTS[n]
            kw = dict(part.demo)
            at = {"head": head, "shoulder": sh, "hand": hand, "belt": hip}[part.anchor]
            kw.update(hip=(hip[0] - sh[0], -(hip[1] - sh[1])), drop=cell[1] - 10 - hand[1], tip=10, half=8.0)
            if n == "cloak":
                kw["drop"] = 26
            if n == "coat_cues":
                kw.pop("drop", None)
            if n == "cloak_back":
                kw["drop"] = 26
            im, (ax, ay) = render(n, "mid", **kw)
            layers.append((part.layer, im, (at[0] - ax, at[1] - ay)))
        for ly in ("back",):
            for l, im, pos in layers:
                if l == ly:
                    t.alpha_composite(im, pos)
        t.alpha_composite(base)
        for l, im, pos in layers:
            if l != "back":
                t.alpha_composite(im, pos)
        tiles.append(t)
    rows = math.ceil(len(tiles) / cols)
    gap = 8
    far_w = 0
    fars = [render(n, "far", **PARTS[n].demo)[0] for n in heads]
    out = Image.new("RGBA", (cell[0] * z * cols, cell[1] * z * rows + 16 * z), bg)
    for i, t in enumerate(tiles):
        out.alpha_composite(t.resize((cell[0] * z, cell[1] * z), Image.Resampling.NEAREST), ((i % cols) * cell[0] * z, (i // cols) * cell[1] * z))
    x = 4 * z
    for im in fars:
        out.alpha_composite(im.resize((im.width * 8, im.height * 8), Image.Resampling.NEAREST), (x, cell[1] * z * rows + 4))
        x += im.width * 8 + gap * 4
    out.convert("RGB").save(path)


if __name__ == "__main__":
    write_all(Path(__file__).resolve().parent)
