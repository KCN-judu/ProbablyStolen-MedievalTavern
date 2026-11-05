"""The room seen through the serving window: a tavern cellar and stair room, dim, lit by the shaft of lamplight the lead
draws over it. From far to near: the back wall with its doorway and the beam that carries a gallery, the gallery's
balustrade and stair handrail, the stair and landing in the middle, a mezzanine floor, the floorboards in front, and the
lit boards near the window. Two jambs (the thick wall either side of the opening) frame it all. The cask shelf and the
wine rack, which stand in this room, are the sprites of props.py.

Each picture is a 960x540 layer drawn on a small canvas of the game's `bbox` (tools/tavern/layout.tsv) and laid at its
place (`props.on_layer`), so it never leaves the rectangle the game's layer fills. Everything here is dimmed toward the
night colour: this is the dark of the room, and only the cone of light and the lamps lift it.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image

from materials import plaster, shadow_under
from palette import BRASS, FLAME, IRON, NIGHT, OAK, PALE_WOOD, PLASTER, SHADOW, SOOT, STONE, WOOD
from pix import BAYER, CLEAR, Color, Pix, Ramp, mix
from props import Box, on_layer, post, timber
from shopx_persp import blend, board_plane, tier


def dim(ramp: Ramp, amount: float) -> Ramp:
    """A ramp pulled toward the blue-black of the night room."""
    return [mix(c[:3], NIGHT[1], amount) for c in ramp]


C_OAK: Final[Ramp] = dim(OAK, 0.15)
C_WOOD: Final[Ramp] = dim(WOOD, 0.3)
C_PALE: Final[Ramp] = dim(PALE_WOOD, 0.4)
C_PLASTER: Final[Ramp] = dim(PLASTER, 0.5)
C_STONE: Final[Ramp] = dim(STONE, 0.5)
VOID: Final[Color] = mix(SHADOW, NIGHT[0], 0.5)       # the dark under the gallery, where the room goes on


def plaster_patch(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = C_PLASTER) -> None:
    """Dim limewash kept inside a rectangle (`materials.plaster` lets its blotches run over the edge)."""
    sub = Pix(w, h, seed=p.rng.randrange(1 << 30))
    plaster(sub, 0, 0, w, h, ramp, stains=False)
    p.paste(sub, x, y)


def balusters(p: Pix, x0: int, x1: int, y0: int, y1: int, step: int, ramp: Ramp = C_WOOD) -> None:
    """Turned balusters between two rails: thin posts with a lit left edge and a swelling in the middle."""
    for x in range(x0, x1, step):
        p.vline(x, y0, y1 - y0, ramp[2])
        p.vline(x, y0, y1 - y0, ramp[3]) if (x // step) % 2 == 0 else None
        p.px(x + 1, (y0 + y1) // 2, ramp[1])
        p.px(x - 1, (y0 + y1) // 2, ramp[3])
        p.px(x, (y0 + y1) // 2 + 1, ramp[4])


def rail(p: Pix, x0: int, x1: int, y: int, thick: int = 3, ramp: Ramp = C_WOOD) -> None:
    """A horizontal handrail or sill: lit top, dark underside."""
    p.rect(x0, y, x1 - x0, thick, ramp[2])
    p.hline(x0, y, x1 - x0, ramp[4])
    p.hline(x0, y + thick - 1, x1 - x0, ramp[0])


def slope(p: Pix, xa: int, ya: int, xb: int, yb: int, thick: int, ramp: Ramp = C_WOOD) -> None:
    """A diagonal timber (a stair handrail or stringer) from (xa, ya) to (xb, yb): lit upper edge, dark lower."""
    n = max(abs(xb - xa), abs(yb - ya), 1)
    for i in range(n + 1):
        x, y = round(xa + (xb - xa) * i / n), round(ya + (yb - ya) * i / n)
        p.rect(x, y, 1, thick, ramp[2])
        p.px(x, y, ramp[4])
        p.px(x, y + thick - 1, ramp[0])


def stair_balusters(p: Pix, xa: int, ya: int, xb: int, yb: int, drop: int, step: int, ramp: Ramp = C_WOOD) -> None:
    """Balusters under a sloping handrail from (xa, ya) to (xb, yb): each runs down `drop` pixels."""
    for x in range(xa + step // 2, xb, step):
        y = round(ya + (yb - ya) * (x - xa) / max(1, xb - xa))
        p.vline(x, y + 2, drop, ramp[2])
        p.px(x, y + 2, ramp[4])


def dark_fill(p: Pix, x: int, y: int, w: int, h: int, strength: float = 0.85) -> None:
    """The dark mass of the room under a floor: the void colour with a dithered grain, so it is not a flat block."""
    p.rect(x, y, w, h, VOID)
    p.dither(x, y, w, h, NIGHT[0], strength * 0.5)
    p.speckle(x, y, w, h, (SOOT[1], NIGHT[1]), 0.03)


# ---------------------------------------------------------------------------------------------- the far wall


def back_wall() -> Image.Image:
    """`store_background` (214x134): the far wall of the room: dim plaster between timber studs, an arched doorway into
    the dark, small iron lantern hooks, a stain of soot at the right; under it the beam that carries the gallery, with
    a zigzag of bracing and the posts that stand in the dark below."""
    def draw(p: Pix) -> None:
        plaster_patch(p, 0, 0, 177, 80)
        for k in range(10):                                           # the ceiling shades the top of the wall
            p.dither(0, k, 177, 1, SHADOW, 0.85 - k * 0.08)
        p.dither(120, 0, 57, 78, SOOT[1], 0.35)                       # soot stain at the right
        post(p, 0, 0, 7, 80, C_OAK, vertical=True)                    # studs
        post(p, 72, 20, 6, 60, C_OAK, vertical=True)
        post(p, 128, 20, 6, 60, C_OAK, vertical=True)
        post(p, 0, 50, 177, 6, C_OAK, vertical=False)                 # the mid rail
        post(p, 0, 0, 177, 8, C_OAK, vertical=False)                  # the ceiling beam
        # the doorway: an arch of timber, and the dark of the next room
        p.rect(78, 20, 50, 60, VOID)
        p.ellipse(78, 12, 50, 28, VOID)
        p.dither(78, 14, 50, 66, NIGHT[1], 0.3)
        for i in range(8):                                            # a hint of shelves far inside
            p.hline(86, 40 + i * 5, 34, C_OAK[1]) if i % 2 == 0 else None
        for ang in range(0, 181, 3):                                  # the arch ring
            a = math.radians(ang)
            x, y = 103 - round(math.cos(a) * 25), 26 - round(math.sin(a) * 15)
            p.rect(x - 1, y - 2, 3, 4, C_OAK[3] if ang < 90 else C_OAK[2])
        p.vline(77, 26, 54, C_OAK[3])
        p.vline(128, 26, 54, C_OAK[0])
        for hx in (26, 150):                                          # lantern hooks, unlit
            p.rect(hx, 16, 2, 6, IRON[2])
            p.hline(hx - 2, 22, 6, IRON[2])
            p.rect(hx - 2, 23, 6, 7, IRON[1])
            p.frame(hx - 2, 23, 6, 7, IRON[0])
            p.px(hx, 26, FLAME[0])
        p.rect(0, 76, 177, 4, C_OAK[1])
        # the gallery beam, its bracing and posts
        p.rect(0, 78, 214, 11, C_OAK[2])
        post(p, 0, 78, 214, 11, C_OAK, vertical=False)
        p.hline(0, 78, 214, C_OAK[4])
        shadow_under(p, 0, 89, 214, 6, 6)
        dark_fill(p, 0, 89, 214, 45)
        for x in range(0, 214, 8):                                     # the zigzag under the beam
            p.line(x, 89, x + 4, 94, C_OAK[1])
            p.line(x + 4, 94, x + 8, 89, C_OAK[1])
        for px_ in (82, 160):
            post(p, px_, 89, 7, 45, C_OAK, vertical=True)
            p.dither(px_, 89, 7, 45, SHADOW, 0.5)
        p.poly([(0, 134), (0, 126), (28, 92), (34, 92)], C_OAK[2])    # brace
        p.line(0, 126, 28, 92, C_OAK[4])
        p.dither(0, 98, 40, 36, SHADOW, 0.5)
        post(p, 44, 0, 38, 6, C_OAK, vertical=False)
    return on_layer((388, 18, 602, 152), draw, 31)


def gallery_rail() -> Image.Image:
    """`store_background_rail` (187x71): the gallery in the far room: a carved newel post at the left, a balustrade
    along the front of the gallery, the handrail of the stair climbing to the right, a dark floor edge below."""
    def draw(p: Pix) -> None:
        dark_fill(p, 0, 57, 187, 14)
        p.hline(0, 57, 187, C_WOOD[3])
        p.hline(0, 58, 187, C_WOOD[1])
        p.dither(0, 59, 187, 4, SHADOW, 0.5)
        rail(p, 44, 162, 46, 3)
        rail(p, 44, 162, 55, 2)
        balusters(p, 46, 162, 49, 55, 4)
        post(p, 38, 0, 7, 58, C_WOOD, vertical=True)                   # newel with a finial
        p.rect(37, 0, 9, 3, C_WOOD[3])
        p.hline(37, 0, 9, C_WOOD[4])
        p.rect(38, 46, 7, 4, C_WOOD[3])
        slope(p, 108, 57, 163, 3, 2)
        stair_balusters(p, 108, 55, 163, 3, 8, 4)
        post(p, 138, 40, 3, 18, C_WOOD, vertical=True)
    return on_layer((388, 35, 575, 106), draw, 32)


# ---------------------------------------------------------------------------------------------- stairs and mezzanine


def stairs() -> Image.Image:
    """`store_mid_stairs` (50x81): the near flight of the stair, going down to the right: a handrail on balusters above
    a row of treads, the lit tread edge and the dark riser of every step, a stringer under them."""
    def draw(p: Pix) -> None:
        slope(p, 0, 0, 46, 36, 3)
        stair_balusters(p, 0, 0, 46, 36, 20, 5)
        slope(p, 0, 18, 46, 74, 3, C_OAK)
        for i in range(9):                                              # treads, each lower and further right
            x, y = i * 5, 22 + i * 6
            p.rect(x, y, 9, 2, C_WOOD[4])
            p.rect(x, y + 2, 9, 4, C_WOOD[1])
            p.hline(x, y + 2, 9, C_WOOD[0])
            p.px(x + 8, y, C_WOOD[2])
        p.poly([(0, 20), (46, 76), (46, 80), (0, 26)], C_OAK[1])
        p.dither(0, 20, 50, 60, SHADOW, 0.35)
    return on_layer((388, 71, 438, 152), draw, 33)


def landing_rail() -> Image.Image:
    """`store_mid_rail` (41x86): the end of the stair rail on the landing: the handrail coming down, a short run of
    balusters, the landing floor, a post going down to the floor."""
    def draw(p: Pix) -> None:
        slope(p, 0, 0, 34, 30, 3)
        stair_balusters(p, 0, 0, 34, 30, 12, 5)
        rail(p, 0, 38, 35, 3)
        rail(p, 0, 38, 52, 2)
        balusters(p, 3, 38, 38, 52, 5)
        post(p, 0, 33, 4, 53, C_WOOD, vertical=True)
        post(p, 34, 33, 4, 22, C_WOOD, vertical=True)
        p.rect(0, 58, 41, 10, C_OAK[2])
        p.hline(0, 58, 41, C_WOOD[3])
        p.hline(0, 67, 41, C_OAK[0])
        dark_fill(p, 4, 68, 37, 2)
    return on_layer((387, 84, 428, 170), draw, 34)


def mezzanine() -> Image.Image:
    """`store_mid` (212x50): the mezzanine across the middle of the room: a low balustrade at the left, a higher one
    along the rest, and the dark floor edge they stand on with its lit lip."""
    def draw(p: Pix) -> None:
        dark_fill(p, 0, 29, 212, 21)
        p.rect(0, 28, 212, 6, C_OAK[2])
        p.hline(0, 28, 212, C_WOOD[3])
        p.hline(0, 33, 212, C_OAK[0])
        for x in range(0, 212, 24):                                     # plank joints in the floor edge
            p.vline(x, 29, 5, C_OAK[0])
        rail(p, 0, 52, 3, 3)
        balusters(p, 3, 52, 6, 28, 4)
        rail(p, 52, 212, 4, 3)
        balusters(p, 55, 212, 7, 28, 4)
        post(p, 50, 0, 5, 30, C_WOOD, vertical=True)
    return on_layer((389, 120, 601, 170), draw, 35)


# ---------------------------------------------------------------------------------------------- floors


def floorboards(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, rows: Sequence[int], seed_tone: int = 2) -> None:
    """Boards running across the picture in rows of the given heights (wider toward the viewer), each row with its own
    tone, butt joints, a lit upper edge and a dark joint line."""
    yy = y
    for i, rh in enumerate(rows):
        if yy >= y + h:
            break
        rh = min(rh, y + h - yy)
        t = seed_tone + (p.rng.randrange(3) - 1)
        p.rect(x, yy, w, rh, ramp[max(0, min(len(ramp) - 1, t))])
        p.hline(x, yy, w, ramp[min(len(ramp) - 1, t + 1)])
        p.hline(x, yy + rh - 1, w, ramp[0])
        a = p.rng.randrange(0, 50) + x
        while a < x + w:
            p.vline(a, yy, rh, ramp[0])
            a += p.rng.randrange(50, 110)
        for _ in range(rh * w // 60):
            gx = x + p.rng.randrange(w)
            p.hline(gx, yy + 1 + p.rng.randrange(max(1, rh - 2)), p.rng.randrange(4, 16), ramp[max(0, t - 1)])
        yy += rh


def near_floor() -> Image.Image:
    """`store_front_floor` (295x194): the floor in front of the mezzanine: dark boards in rows that widen toward the
    window, darker at the ends; and a short ceiling timber at the top, the little the game's layer keeps there."""
    def draw(p: Pix) -> None:
        post(p, 65, 0, 40, 5, C_OAK, vertical=False)
        p.rect(0, 152, 295, 42, C_WOOD[0])
        board_plane(p, 337, 632, 170, 212, C_WOOD, 5, tones=(1, 1, 2), span=(110, 240), origin=(337, 18))
        for k in range(8):                                               # the floor darkens toward both ends
            p.dither(k * 3, 152, 3, 42, SHADOW, 0.7 - k * 0.09)
            p.dither(294 - k * 3 - 2, 152, 3, 42, SHADOW, 0.7 - k * 0.09)
        p.dither(0, 152, 295, 42, NIGHT[1], 0.3)
        for y in range(152, 194):                                        # a pool of lamplight: stepped, soft at its rim
            for x in range(40, 255):
                k = tier(1 - math.hypot((x - 147) / 105, (y - 174) / 19), x, y, 4)
                if k:
                    blend(p, x, y, FLAME[1], 0.07 * k)
        p.hline(0, 152, 295, C_WOOD[3])
    return on_layer((337, 18, 632, 212), draw, 36)


def lit_floor() -> Image.Image:
    """`front_counter` (285x46): the boards of the room's front, nearest the window, where the lamplight lands: a pool of
    warm light on the planks, with a dark edge all round and a lit lip along the bottom."""
    def draw(p: Pix) -> None:
        board_plane(p, 338, 623, 210, 256, C_PALE, 5, tones=(2, 2, 3), span=(130, 280), origin=(338, 210))
        cx, cy = 142, 22
        for yy in range(46):
            for xx in range(285):
                d = math.hypot((xx - cx) / 128, (yy - cy) / 19)
                if d < 1.0:
                    level = (1 - d) ** 0.9 * 0.85
                    if BAYER[yy % 4][xx % 4] < round(level * 16):
                        p.px(xx, yy, mix(p.get(xx, yy)[:3], FLAME[2], 0.55))
                elif d > 1.1:
                    if BAYER[yy % 4][xx % 4] < min(14, round((d - 1.0) * 16)):
                        p.px(xx, yy, mix(p.get(xx, yy)[:3], SHADOW, 0.6))
        for k in range(3):                                               # rounded corners and a lit bottom lip
            for i in range(5 - k * 2):
                for xx in (i, 284 - i):
                    p.px(xx, k, CLEAR)
                    p.px(xx, 45 - k, CLEAR)
        p.hline(5, 44, 275, C_PALE[4])
        p.hline(5, 45, 275, C_PALE[0])
    return on_layer((338, 210, 623, 256), draw, 37)


# ---------------------------------------------------------------------------------------------- the jambs of the window


def jamb(p: Pix, x: int, w: int, left: bool) -> None:
    """One jamb of the opening: the thick wall seen edge-on, dim plaster in a timber frame with a panel, lit near the
    window and darker toward the outside and the floor, a bevel at its head."""
    top, bottom = 25, 176
    plaster_patch(p, x, top, w, bottom - top)
    edge = x if left else x + w - 6                           # the outer post, against the wall
    post(p, edge, top, 6, bottom - top, C_OAK, vertical=True)
    post(p, x, top, w, 6, C_OAK, vertical=False)
    post(p, x, 118, w, 5, C_OAK, vertical=False)
    px0 = x + (10 if left else 6)
    p.frame(px0, 48, w - 18, 56, C_OAK[1])                    # a panel
    p.frame(px0 + 1, 49, w - 20, 54, C_OAK[0])
    p.rect(px0 + w // 3, 136, 22, 22, C_OAK[1])
    p.frame(px0 + w // 3, 136, 22, 22, C_OAK[0])
    p.px(px0 + w // 3 + 3, 139, BRASS[2])
    p.px(px0 + w // 3 + 18, 154, BRASS[2])
    inner = x + w - 1 if left else x
    for k in range(8):                                        # warm light from the room spills on the inner edge
        xx = inner - k if left else inner + k
        p.dither(xx, top, 1, bottom - top, FLAME[0], max(0.0, 0.3 - k * 0.04))
    for k in range(12):                                       # dark toward the floor
        p.dither(x, 120 + k * 5, w, 5, SHADOW, 0.1 + k * 0.07)
    p.dither(x, top, w, 30, SHADOW, 0.3)
    for k in range(6):                                        # the bevel at the head, toward the opening
        for i in range(6 - k):
            xx = (x + w - 1 - i) if left else (x + i)
            p.px(xx, top + k, CLEAR)


def jambs() -> Image.Image:
    """`store_front_wall_lit` (290x212): the two thick sides of the window opening, and the dark timbers that hang from
    the ceiling above them."""
    def draw(p: Pix) -> None:
        jamb(p, 0, 59, True)
        jamb(p, 228, 62, False)
        for x0, wd in ((39, 14), (233, 16)):
            post(p, x0, 0, wd, 26, C_OAK, vertical=True)
            p.dither(x0, 0, wd, 26, SHADOW, 0.4)
        p.rect(100, 14, 24, 2, IRON[1])
    return on_layer((337, 0, 627, 212), draw, 38)


# ---------------------------------------------------------------------------------------------- small pieces


def secret_niche() -> Image.Image:
    """`hidden_space` (34x38): a hiding place in the wall: a dark niche behind a loose plank that hangs from one nail,
    a brass keyhole plate beside it."""
    def draw(p: Pix) -> None:
        p.rect(0, 0, 34, 38, C_OAK[1])
        post(p, 0, 0, 34, 38, C_OAK, vertical=False)
        p.rect(4, 4, 26, 30, VOID)
        p.dither(4, 4, 26, 30, NIGHT[1], 0.4)
        for k in range(6):
            p.dither(4, 4 + k, 26, 1, SHADOW, 0.9 - k * 0.12)
            p.dither(4 + k, 4, 1, 30, SHADOW, 0.8 - k * 0.12)
        p.poly([(4, 4), (22, 4), (14, 33), (4, 31)], C_WOOD[2])        # the plank, swung aside from its nail
        p.line(4, 4, 22, 4, C_WOOD[4])
        p.line(22, 4, 14, 33, C_WOOD[0])
        p.dither(8, 8, 10, 20, C_WOOD[1], 0.4)
        p.px(6, 6, IRON[4])
        p.rect(24, 24, 5, 6, BRASS[1])
        p.frame(24, 24, 5, 6, BRASS[0])
        p.px(26, 26, SHADOW)
        p.px(26, 27, SHADOW)
    return on_layer((790, 91, 824, 129), draw, 39)


def corner_shadow() -> Image.Image:
    """`screen shadow` (148x114): the dark that gathers in the upper right corner of the shop: a mass of night at
    the corner, its edge broken up in dithered steps so it dissolves into the wall."""
    def draw(p: Pix) -> None:
        for y in range(114):
            for x in range(148):
                d = math.hypot((148 - x) * 0.95, y * 1.25)
                if d < 62:
                    a = 225
                elif d < 100:
                    level = (100 - d) / 38
                    if BAYER[y % 4][x % 4] >= round((1 - level) * 16) and level > 0:
                        a = 190 if level > 0.5 else 120
                    else:
                        continue
                elif d < 122:
                    if BAYER[y % 4][x % 4] < round((122 - d) / 22 * 5):
                        a = 70
                    else:
                        continue
                else:
                    continue
                p.px(x, y, (*SOOT[0], a))
        p.speckle(60, 0, 88, 30, (CLEAR,), 0.0)
    return on_layer((812, 0, 960, 114), draw, 40)


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "store_background.960x540.png": back_wall,
    "store_background_rail.960x540.png": gallery_rail,
    "store_mid_stairs.960x540.png": stairs,
    "store_mid_rail.960x540.png": landing_rail,
    "store_mid.960x540.png": mezzanine,
    "store_front_floor.960x540.png": near_floor,
    "front_counter.960x540.png": lit_floor,
    "store_front_wall_lit.960x540.png": jambs,
    "hidden_space.960x540.png": secret_niche,
    "screen shadow.960x540.png": corner_shadow,
}
