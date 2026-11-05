"""Shared geometry and scenery of the display-case window: where the wall is cut, the plaster that fills it again when a
smaller case is shown, the dusk street that is seen through the glass, and the perspective of the case's inside.

The shop wall has nothing behind it left of the serving window (the game's back-room layers only fill x 337..632), so
the opening would show the camera's black. The street is therefore painted on the wall layer inside the opening,
behind every case (set `STREET = False` to leave it fully transparent)."""

from __future__ import annotations

import math

from materials import plaster
from palette import FLAME, OAK, PLASTER, SHADOW, STONE
from pix import Color, Pix, mix, rgb
from shopx_persp import VP, stepped, tier
from PIL import Image

W, H = 960, 540
OPEN = (115, 120, 289, 260)          # x0, y0, x1, y1 (exclusive): the largest case's footprint = the cut in the wall
STREET = True
ASSETS: dict[str, object] = {}       # a helper module: the build tool only needs the name to exist

# the three cases: outer frame rectangle (x0, y0, x1, y1)
FRAMES = {
    "small": (118, 120, 258, 228),
    "medium": (118, 120, 275, 244),
    "large": (118, 120, 289, 258),
}
RING_LEFT, RING_BOTTOM = 3, 2        # the wall's reveal visible around a case: left face and sill top
DEPTH = 0.04                          # how much the back of the case shrinks toward the vanishing point


def proj(x: float, y: float, u: float) -> tuple[float, float]:
    """Screen point of the case-front point (x, y) pushed back by depth `u` (0 front glass, 1 back glass)."""
    s = 1 - DEPTH * u
    return VP[0] + (x - VP[0]) * s, VP[1] + (y - VP[1]) * s


def plaster_wall(variant: int = 0) -> Pix:
    """The wall's own plaster, pixel for pixel (same seed and same calls as `shop.wall`), with its lamplight falloff."""
    p = Pix(W, H, seed=11 + variant)
    plaster(p, 0, 0, W, 384, PLASTER, stains=False)
    for y in range(26, 384):
        for x in range(16, 944):
            d = math.hypot((x - 480) / 520, (y - 210) / 330)
            k = tier(max(0.0, min(1.0, (d - 0.42) / 0.75)), x, y)
            if k:
                r, g, b, a = p.get(x, y)
                p.px(x, y, (*mix((r, g, b), SHADOW[:3], 0.1 * k), a))
    return p


# ---------------------------------------------------------------------------------------------- the street

NIGHT = (rgb("#10132a"), rgb("#1b1f3d"), rgb("#2b3052"), rgb("#444a70"), rgb("#6b7094"))
DUSK = (rgb("#1d2142"), rgb("#3a3562"), rgb("#6d4a63"), rgb("#b2653f"), rgb("#e8954a"))
STREET_BASE = 205                      # where the houses across the street meet the cobbles


def _lit_window(p: Pix, x: int, y: int, w: int, h: int, cols: int = 2, rows: int = 2) -> None:
    """A leaded window with the lamplight of the room behind it."""
    p.rect(x - 1, y - 1, w + 2, h + 2, OAK[1])
    for j in range(h):
        c = mix(FLAME[3][:3], FLAME[1][:3], j / max(1, h - 1) * 0.7)
        p.hline(x, y + j, w, c)
    p.dither(x, y, w, h, FLAME[4], 0.12)
    for i in range(1, cols):
        p.vline(x + i * w // cols, y, h, OAK[0])
    for j in range(1, rows):
        p.hline(x, y + j * h // rows, w, OAK[0])
    p.hline(x - 1, y + h + 1, w + 2, OAK[3])           # a sill, lit from the lamp above


def street() -> Pix:
    """The view across the street at dusk, on a full-size canvas (only the opening is used)."""
    x0, y0, x1, y1 = OPEN
    p = Pix(W, H, seed=71)
    # sky: bands of dither from indigo down to a smouldering horizon
    bands = (NIGHT[0], NIGHT[1], DUSK[0], DUSK[1], DUSK[2], DUSK[3])
    for i, y in enumerate(range(y0, 150, 5)):
        p.rect(x0, y, x1 - x0, 5, bands[min(len(bands) - 1, i // 1)])
    for i in range(len(bands) - 1):
        p.dither(x0, y0 + i * 5 + 3, x1 - x0, 2, bands[i + 1], 0.5)
    p.speckle(x0, y0, x1 - x0, 14, (DUSK[4], NIGHT[4]), 0.02)          # a few early stars
    # house A (left): low, with a tiled roof and a gable
    p.rect(x0, 146, 92, STREET_BASE - 146, mix(NIGHT[2][:3], PLASTER[1][:3], 0.25))
    p.poly([(x0 - 4, 148), (150, 126), (x0 + 96, 148)], mix(NIGHT[1][:3], DUSK[1][:3], 0.4))
    for k in range(0, 96, 4):                                        # tile courses along the eave
        p.hline(x0, 138 + k // 12, 1, NIGHT[0])
    p.hline(x0, 147, 94, NIGHT[0])
    p.hline(x0, 148, 94, mix(NIGHT[3][:3], DUSK[3][:3], 0.4))
    for x in (x0 + 2, x0 + 44, x0 + 88):                              # timber studs of the lower house
        p.rect(x, 149, 3, STREET_BASE - 149, OAK[1])
        p.vline(x, 149, STREET_BASE - 149, OAK[2])
    p.rect(x0, 168, 92, 3, OAK[1])
    p.speckle(x0, 149, 92, STREET_BASE - 149, (NIGHT[1], NIGHT[3]), 0.06)
    p.rect(x0, STREET_BASE - 6, 92, 6, mix(NIGHT[1][:3], STONE[1][:3], 0.5))   # a stone footing
    _lit_window(p, 131, 175, 26, 22)
    _lit_window(p, 139, 156, 12, 10, 1, 2)
    # house B (right): taller, timber-framed, with a jetty
    bx = x0 + 94
    p.rect(bx, y0, x1 - bx, STREET_BASE - y0, mix(NIGHT[2][:3], PLASTER[1][:3], 0.35))
    for y in range(y0, STREET_BASE):                                 # the lamplight of the street falls on the lower part
        if y > 165:
            p.dither(bx, y, x1 - bx, 1, FLAME[1], 0.05 + (y - 165) / 40 * 0.12)
    p.speckle(bx, y0, x1 - bx, STREET_BASE - y0, (NIGHT[1], NIGHT[3]), 0.06)
    for x in (bx + 2, bx + 40, x1 - 6):
        p.rect(x, y0, 4, STREET_BASE - y0, OAK[2])
        p.vline(x, y0, STREET_BASE - y0, OAK[3])
    p.rect(bx, 160, x1 - bx, 6, OAK[2])                              # the jetty beam
    p.hline(bx, 160, x1 - bx, OAK[4])
    p.hline(bx, 165, x1 - bx, OAK[0])
    p.line(bx + 6, 158, bx + 38, 128, OAK[1])                        # a brace in the upper story
    _lit_window(p, bx + 10, 134, 20, 18, 2, 2)
    _lit_window(p, bx + 50, 136, 20, 16, 2, 2)
    _lit_window(p, bx + 8, 178, 24, 20, 2, 2)
    dx = bx + 52                                                     # the door, with a lamp over it
    p.rect(dx, 176, 18, STREET_BASE - 176, OAK[1])
    for i in range(1, 4):
        p.vline(dx + i * 4, 177, STREET_BASE - 177, OAK[0])
    p.hline(dx, 176, 18, OAK[3])
    p.rect(dx + 13, 192, 2, 2, FLAME[3])
    p.rect(dx + 7, 166, 4, 5, FLAME[3])                               # the hanging lantern
    p.glow(dx + 9, 170, 14, FLAME[2], 0.35)
    # cobbles: rows of equal depth, joints leaning to the vanishing point
    for y in range(STREET_BASE, y1):
        t = (y - STREET_BASE) / (y1 - STREET_BASE)
        p.hline(x0, y, x1 - x0, mix(NIGHT[1][:3], STONE[2][:3], 0.35 + 0.4 * t))
    p.hline(x0, STREET_BASE, x1 - x0, NIGHT[0])                       # the kerb line at the foot of the houses
    row = [STREET_BASE, 213, 224, 238, 255, y1]
    for ya, yb in zip(row, row[1:]):
        p.hline(x0, ya, x1 - x0, NIGHT[0])
        stone = 14 + (ya - STREET_BASE) // 3
        for k in range(-4, 40):
            wx = x0 + k * stone + (stone // 2 if row.index(ya) % 2 else 0)
            fx = VP[0] + (wx - VP[0]) * (yb - VP[1]) / max(1, (ya - VP[1]))
            if x0 <= wx < x1 and x0 <= fx < x1:
                p.line(wx, ya, round(fx), yb, NIGHT[0])
                p.line(wx + 1, ya + 1, round(fx) + 1, yb - 1, mix(NIGHT[3][:3], DUSK[3][:3], 0.3))
    for gy, gw in ((STREET_BASE + 4, 14), (STREET_BASE + 9, 10), (STREET_BASE + 16, 6)):   # the lantern's gleam on wet stones
        p.hline(bx + 61 - gw // 2, gy, gw, mix(FLAME[1][:3], NIGHT[2][:3], 0.4))
    return p


def street_image() -> Image.Image:
    return street().finish()
