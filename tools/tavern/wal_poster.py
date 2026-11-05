"""The wall poster in its three states (`poster`, `poster_no_shadow`, `poster_down`): a printed advertisement for ale,
pasted on the plaster, on real paper.

Logic: a tavern's advert is a woodcut-and-ink broadsheet. It is tacked at the top left, taped at the bottom left, one
corner has been torn and another curls. The picture is painted flat first and then the paper's own grain, folds and damp
stains (from `fxkit.paper_fill`) are carried over the ink, so creases catch the light across the drawing.
`poster_down`: the same sheet after its right nail gave way: it hangs by the left nail with its foot rolled forward
into a tube that shows the plain back of the paper.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Final

from PIL import Image

import font
import fxkit as fx
from palette import BRASS, FLAME, IRON, PALE_WOOD, PARCHMENT, WINE
from pix import Color, Pix, mix

W, H = 960, 540
CW, CH = 86, 103                       # the bbox of `poster` (769, 66)
SW, SH = 83, 100                       # the sheet
INK_DARK: Final[Color] = (46, 20, 22, 255)
CREAM: Final[Color] = PARCHMENT[4]
HEAD: Final = (41, 52)                 # where the rays meet: the tankard's middle
CHAMFER: Final = {"tl": 6, "tr": 12, "br": 9, "bl": 9}   # the printed area gives way to the torn, curled and taped corners


def _lum(c: tuple[int, ...]) -> float:
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _field(p: Pix) -> None:
    """The red ground: rays radiating from the tankard, an amber glow round it, a little print mottle."""
    cx, cy = HEAD
    glow = (WINE[3], FLAME[0], FLAME[1], FLAME[2])
    for y in range(CH):
        for x in range(CW):
            a = math.atan2(y - cy, x - cx)
            d = math.hypot(x - cx, (y - cy) * 0.9)
            if d < 27:
                v = (1.0 - d / 27) * 2.5 + 0.3 + (fx.vnoise(x / 3, y / 3, 9) - 0.5) * 0.8
                p.px(x, y, fx.pick_tone(glow, v, x, y, 2.4))
                continue
            ray = ((a + math.pi) / (2 * math.pi) * 18) % 1.0
            v = 1.5 + (0.6 if ray < 0.5 else 0.0)
            v += (fx.vnoise(x / 5, y / 5, 3) - 0.5) * 0.9
            v -= max(0.0, (d - 40) / 30) * 0.9
            p.px(x, y, fx.pick_tone(WINE, v, x, y, 2.6))


def _lettering(p: Pix, text: str, x: int, y: int, scale: int, c: Color, edge: Color) -> None:
    """Letters with a dark drop so they stand off the field."""
    font.write(p, x + 1, y + 1, text, edge, scale)
    font.write(p, x, y, text, c, scale)


def _tankard(p: Pix) -> None:
    cx = HEAD[0]
    top, bot = 42, 67
    rx_t, rx_b, ry = 12.5, 14.0, 3.6
    # the handle, behind the body: a loop of pale wood
    for t in range(0, 181, 2):
        a = math.radians(t - 90)
        hx = cx + rx_t + 1 + 7.5 * math.cos(a)
        hy = (top + bot) / 2 + 1 + 10.5 * math.sin(a)
        for k in range(-2, 3):
            xx, yy = round(hx + k * math.cos(a) * 0.9), round(hy + k * math.sin(a) * 0.9)
            p.px(xx, yy, fx.pick_tone(PALE_WOOD, 2.6 - k * 0.55 - (0.8 if t > 90 else 0), xx, yy))
    for hy in (top + 4, bot - 4):                                       # iron straps where the handle meets the body
        p.rect(cx + 11, hy, 5, 2, IRON[3])
        p.hline(cx + 11, hy, 5, IRON[4])
        p.hline(cx + 11, hy + 1, 5, IRON[1])
    # the body: staves shaded as a cylinder, widening to the foot
    for y in range(top, bot + 5):
        k = min(1.0, max(0.0, (y - top) / (bot - top)))
        rx = rx_t + (rx_b - rx_t) * k
        for x in range(round(cx - rx), round(cx + rx) + 1):
            u = (x - cx) / rx
            if y > bot + math.sqrt(max(0.0, 1 - u * u)) * ry:
                continue
            f = (u + 1) * 3.6
            v = 3.9 - (u + 0.55) * 2.0 + ((int(f) % 3) - 1) * 0.28
            v += (fx.vnoise(x / 6, y / 1.5, int(f)) - 0.5) * 0.9      # grain along the stave
            if f % 1.0 < 0.09:
                v -= 1.3                                              # the seam between two staves
            if abs(u) > 0.9:
                v -= 0.8
            p.px(x, y, fx.pick_tone(PALE_WOOD, v, x, y, 2.8))
    for hy in (top + 7, bot - 8):                                       # two iron hoops that follow the belly
        for x in range(round(cx - 14), round(cx + 14) + 1):
            u = (x - cx) / 13.4
            if abs(u) > 1:
                continue
            yy = hy + round(math.sqrt(1 - u * u) * ry)
            for dy in range(3):
                v = 3.4 - (u + 0.5) * 1.6 - dy * 1.0 + (0.8 if dy == 0 else 0)
                p.px(x, yy + dy, fx.pick_tone(IRON, v, x, yy + dy, 3.0))
        p.px(cx - 4, hy + 1 + round(math.sqrt(1 - (4 / 13.4) ** 2) * ry), BRASS[3])
    for x in range(round(cx - rx_t), round(cx + rx_t) + 1):             # the rim
        u = (x - cx) / rx_t
        p.px(x, top - round(math.sqrt(max(0, 1 - u * u)) * ry), PALE_WOOD[4] if u < 0.2 else PALE_WOOD[2])
    # foam heaped over the rim, lit from the upper left, with bubbles
    blobs = [(-8, 40, 5.0), (-2, 37, 6.0), (5, 38, 5.5), (10, 41, 4.5), (-6, 43, 4.0), (2, 43, 4.5), (8, 44, 3.4),
             (-11, 44, 3.0), (-1, 33, 4.0), (5, 34, 3.2), (-5, 34, 3.0)]
    for bx, by, r in blobs:
        for y in range(round(by - r), round(by + r) + 1):
            for x in range(round(cx + bx - r), round(cx + bx + r) + 1):
                dx, dy = (x - cx - bx) / r, (y - by) / r
                d2 = dx * dx + dy * dy
                if d2 > 1:
                    continue
                v = 3.7 - (dx * 0.8 + dy * 0.9) * 1.6 + (0.4 if d2 < 0.2 else 0) - (0.7 if d2 > 0.8 else 0)
                p.px(x, y, fx.pick_tone(PARCHMENT, v, x, y, 2.4))
    for dx, dy in ((-7, 36), (-3, 34), (3, 36), (9, 39)):               # glints on the foam
        p.px(cx + dx, dy, CREAM)
    for bx, ln in ((-12, 6), (-4, 4), (6, 7), (11, 4)):                 # foam running down the staves
        for k in range(ln):
            p.px(cx + bx, top + 2 + k, PARCHMENT[3] if k < ln - 1 else PARCHMENT[2])
            p.px(cx + bx + 1, top + 2 + k, PARCHMENT[1] if k < ln - 2 else PARCHMENT[0])


def _board_shadow(p: Pix) -> None:
    """The shelf the tankard stands on (a dark ellipse) with the tankard's foot in it."""
    cx = HEAD[0]
    p.ellipse(cx - 19, 66, 40, 9, INK_DARK)
    p.ellipse(cx - 17, 68, 36, 5, mix(INK_DARK, WINE[1], 0.35))


def _banner(p: Pix, text: str, y: int) -> None:
    """A cloth ribbon with swallow-tail ends and folds, the lettering in dark wine."""
    x0, x1 = 6, CW - 10
    for yy in range(y, y + 12):
        for x in range(x0, x1 + 1):
            side = x < x0 + 4 or x > x1 - 4
            notch = max(0, 4 - min(x - x0, x1 - x)) if side else 0
            if side and abs((yy - y) - 5.5) < notch * 0.6:
                continue
            v = (2.6 if side else 3.3) - (0.9 if yy > y + 8 else 0) + (0.7 if yy < y + 2 else 0)
            v += (fx.vnoise(x / 3, yy, 4) - 0.5) * 0.4
            p.px(x, yy, fx.pick_tone(PARCHMENT, v, x, yy, 3.0))
    for xx in (x0 + 4, x1 - 4):                                         # where the ends fold back
        p.vline(xx, y, 12, PARCHMENT[0])
    font.write(p, 12, y + 3, text, WINE[0])
    font.write(p, 12, y + 2, text, WINE[2])


def _art() -> Pix:
    p = Pix(CW, CH, seed=70)
    _field(p)
    _board_shadow(p)
    _tankard(p)
    _lettering(p, "DRINK", 12, 9, 2, CREAM, INK_DARK)
    _banner(p, "HEARTH ALE", 77)
    return p


def _printed(x: int, y: int) -> bool:
    """Inside the printed area: the sheet less a margin, with the corners cut (more where the paper is torn or curled)."""
    m = 4
    if not (m <= x < SW - m and m <= y < SH - m):
        return False
    dl, dr, dt, db = x - m, SW - 1 - m - x, y - m, SH - 1 - m - y
    return (dl + dt >= CHAMFER["tl"] and dr + dt >= CHAMFER["tr"] and dr + db >= CHAMFER["br"] and dl + db >= CHAMFER["bl"])


def _under_paper(paper: Pix, reg: fx.Region, art: Pix, out: Pix) -> None:
    """Lays the ink on the paper, carrying the paper's light and dark (grain, creases, stains, foxing) through it."""
    ref = _lum(PARCHMENT[3])
    for y in range(SH):
        for x in range(SW):
            if not reg.inside(x, y) or not _printed(x, y):
                continue
            q = paper.get(x, y)
            a = art.get(x, y)
            k = 1.0 + (_lum(q) - ref) / 255 * 1.7
            out.px(x, y, (max(0, min(255, round(a[0] * k))), max(0, min(255, round(a[1] * k))),
                          max(0, min(255, round(a[2] * k))), 255))
    # a thin dark rule just inside the printed edge; paper shows through where the ink is worn off
    for y in range(SH):
        for x in range(SW):
            if _printed(x, y) and not (_printed(x - 1, y) and _printed(x + 1, y) and _printed(x, y - 1) and _printed(x, y + 1)):
                if reg.inside(x, y):
                    out.px(x, y, INK_DARK)
    for _ in range(26):                                                 # worn ink: tiny flecks of bare paper
        x, y = out.rng.randrange(5, SW - 5), out.rng.randrange(5, SH - 5)
        if _printed(x, y) and reg.inside(x, y):
            out.px(x, y, mix(out.get(x, y)[:3], PARCHMENT[2], 0.6))


def _sheet() -> tuple[Pix, Pix, fx.Region]:
    paper = Pix(CW, CH, seed=71)
    reg = fx.paper_fill(paper, (0, 0, SW, SH), folds=(1, 1), stains=0.7, foxing=0.5, tear=("tr",), curl=("br",), tape=("bl",),
                        nails=("tl",), shadow=False, seed=5)
    return paper, _art(), reg


def poster_up(shadow: bool) -> Image.Image:
    """The standing poster (86x103): paper, ink, nail, tape, a torn corner and a curled one, and (optionally) a soft shadow."""
    paper, art, reg = _sheet()
    out = Pix(CW, CH, seed=72)
    if shadow:
        fx.wall_shadow(out, reg, offset=(3, 3), spread=3, strength=0.85)
    out.paste(paper, 0, 0)
    _under_paper(paper, reg, art, out)
    return out.finish()


def _roll_end(p: Pix, cx: int, cy: int, rx: int, ry: int) -> None:
    """The end of a rolled sheet: a spiral of paper edge."""
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d > 1:
                continue
            ang = math.atan2((y - cy) / ry, (x - cx) / rx)
            ring = (d * 3.2 + ang / (2 * math.pi)) % 1.0
            v = 2.7 if ring > 0.3 else 1.0
            if d > 0.86:
                v = 1.0
            p.px(x, y, fx.pick_tone(PARCHMENT, v - (x - cx) / rx * 0.5, x, y, 3.0))


def poster_down() -> Image.Image:
    """The poster after its right nail gave way (89x90): the top still shows the picture, hanging from the left nail,
    the foot is rolled forward into a tube whose outside is the plain back of the paper."""
    sheet = poster_up(False)
    keep = 54
    c = Pix(110, 110, seed=73)
    c.paste(sheet.crop((0, 0, SW, keep)), 4, 4)
    ox, oy, ry = 4, 4 + keep - 4, 6
    roll = 83
    for x in range(roll):                                               # the tube: the paper's back, shaded as a cylinder
        for y in range(-ry, ry + 1):
            t = y / ry
            v = 3.9 - (t + 0.35) * 1.9 + (fx.vnoise(x / 7, y / 2, 5) - 0.5) * 0.7
            if abs(t) > 0.88:
                v -= 0.9
            c.px(ox + x, oy + ry + y, fx.pick_tone(PARCHMENT, v, x, y, 2.8))
        if x % 17 == 9:                                                 # a crease across the tube
            for y in range(-ry + 1, ry):
                c.px(ox + x, oy + ry + y, PARCHMENT[1])
    for y in range(ry - 1):                                             # the face above the roll sinks into its shade
        c.dither(ox, oy - 1 - y, roll, 1, (50, 25, 25, 255), 0.45 * (1 - y / (ry - 1)))
    _roll_end(c, ox + roll - 1, oy + ry, 4, ry)
    _roll_end(c, ox + 1, oy + ry, 3, ry)
    rot = c.im.rotate(-9, resample=Image.NEAREST, center=(5, 5), fillcolor=(0, 0, 0, 0))
    box = rot.getbbox()
    rot = rot.crop(box)
    out = Pix(89, 90, seed=74)
    nailx, naily = 5 - box[0], 5 - box[1]
    sh = Pix(89, 90)
    sh.paste(rot, 1, 1)
    fx.wall_shadow(out, sh.im, offset=(3, 3), spread=3, strength=0.85)
    out.paste(rot, 1, 1)
    fx.rivet(out, nailx + 1, naily + 1, 2, IRON)
    return out.finish()


def _on_layer(small: Image.Image, at: tuple[int, int]) -> Image.Image:
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.alpha_composite(small, at)
    return full


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "poster.960x540.png": lambda: _on_layer(poster_up(True), (769, 66)),
    "poster_no_shadow.960x540.png": lambda: _on_layer(poster_up(False), (769, 66)),
    "poster_down.960x540.png": lambda: _on_layer(poster_down(), (769, 114)),
}
