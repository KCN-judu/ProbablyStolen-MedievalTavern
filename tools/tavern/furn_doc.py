"""`dossier_0..3` (112x96): the document tray as an iron-bound oak letter-box with two leather pockets.

What it is: a clerk's document box, an open oak tray with a hulled foot, iron straps and two stitched leather pockets on its
front for slips and tallies. dossier_0 is empty; _1 holds one sheet of parchment; _2 a ledger (wine-red leather, brass
corners, a green ribbon, a wax seal on its strap) with loose papers; _3 the same with a green and an orange slip pushed
into the pockets. The box is seen from a corner, as the game's tray is: a long left face, a short right face, the open top."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PIL import Image, ImageChops, ImageDraw

import fxkit as fx
from furn_kit import BRASS_AGED, clip
from palette import BRASS, FLAME, IRON, LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, WINE, WOOD
from pix import Pix, mix

B, L, R, F = (31, 24), (4, 33), (107, 41), (80, 52)
LEFT_FACE: Final = [L, F, (76, 94), (60, 94), (44, 88), (17, 80), (4, 66)]
RIGHT_FACE: Final = [F, R, (107, 76), (99, 80), (85, 88), (76, 94)]


def _yt(x: float) -> float:
    """y of the left face's top edge at column x."""
    return L[1] + (x - L[0]) * (F[1] - L[1]) / (F[0] - L[0])


def _mask(poly: list[tuple[int, int]]) -> Image.Image:
    m = Image.new("L", (112, 96), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


def _box(p: Pix) -> None:
    fx.contact_shadow(p, LEFT_FACE + RIGHT_FACE[1:], shift=(2, 1), spread=2, strength=0.7)
    top = [B, L, F, R]
    fx.wood_fill(p, top, 12, PALE_WOOD, board=5, light=0.5, bias=-0.4, seed=61, knots=0.2, joints=False, nails=False)   # the rim
    fx.wood_fill(p, LEFT_FACE, 7, WOOD, board=9, light=0.6, bias=0.3, seed=62, knots=0.9, joints=False, nails=False, damp=0.5,
                 scratches=1.6)
    fx.wood_fill(p, RIGHT_FACE, 7, OAK, board=8, light=0.1, bias=-0.1, seed=63, knots=0.6, joints=False, nails=False, damp=0.5)
    # the opening, inset from the rim, and the inner walls: two back walls, the far one the darker
    inner = [(B[0], B[1] + 4), (L[0] + 7, L[1] + 0), (F[0], F[1] - 4), (R[0] - 7, R[1] + 1)]
    p.poly(inner, SOOT[0])
    fx.wood_fill(p, [(B[0], B[1] + 4), (L[0] + 7, L[1]), (L[0] + 7, L[1] + 8), (B[0], B[1] + 12)], 12, OAK, board=5, light=0.2, bias=-0.7,
                 seed=64, knots=0, joints=False, nails=False)
    fx.wood_fill(p, [(B[0], B[1] + 4), (R[0] - 7, R[1] + 1), (R[0] - 7, R[1] + 9), (B[0], B[1] + 12)], -12, OAK, board=5, light=0.2,
                 bias=-1.2, seed=65, knots=0, joints=False, nails=False)
    for x in range(L[0] + 8, F[0]):                                      # the front lip's shade falls into the box
        y = round(_yt(x)) - 4
        fx.over(p, x, y, SHADOW, 120)
        fx.over(p, x, y - 1, SHADOW, 50)
    # iron: a strap up each end of the left face, a strap round the corner, a hull band; brass rivets
    for x in (16, 56):
        fx.iron_fill(p, [(x, round(_yt(x)) + 1), (x + 5, round(_yt(x + 5)) + 1), (x + 5, 74 + (x < 30) * 2), (x, 74 + (x < 30) * 2)], rust=0.35,
                     hammer=0.5, rivets=9, seed=x)
    fx.iron_fill(p, [(F[0] - 1, F[1] + 1), (F[0] + 2, F[1]), (F[0] + 2, 92), (F[0] - 1, 93)], rust=0.3, hammer=0.4, rivets=8, seed=7)
    fx.iron_fill(p, [(R[0] - 5, R[1] + 3), (R[0] - 1, R[1] + 2), (R[0] - 1, 75), (R[0] - 5, 77)], rust=0.35, hammer=0.4, rivets=9, seed=8)
    # two stitched leather pockets on the left face
    for k, x0 in enumerate((22, 49)):
        x1 = x0 + 25
        y0, y1 = _yt(x0) + 12, _yt(x1) + 12
        quad = [(x0, round(y0)), (x1, round(y1)), (x1 - 2, round(y1) + 21), (x0 + 3, round(y0) + 23)]
        fx.wall_shadow(p, quad, offset=(1, 2), spread=1, strength=0.7)
        fx.wood_fill(p, quad, 12, LEATHER, board=6, light=0.5, bias=1.3, seed=70 + k, knots=0, joints=False, nails=False, scratches=1.2)
        for x in range(x0 + 2, x1 - 1, 3):                              # stitching along the lip
            yy = round(y0 + (x - x0) * (y1 - y0) / (x1 - x0)) + 3
            p.px(x, yy, PARCHMENT[3])
        for x in range(x0, x1 + 1):
            yy = round(y0 + (x - x0) * (y1 - y0) / (x1 - x0))
            p.px(x, yy, LEATHER[3])
            fx.over(p, x, yy + 1, SHADOW, 140)


def _contents(state: int) -> Pix:
    c = Pix(112, 96, seed=80 + state)
    if state == 1:
        fx.paper_fill(c, [(57, 46), (61, 12), (69, 12), (90, 17), (87, 46)], folds=(0, 1), stains=0.5, curl=("tr",), ink=0.6, seed=3)
    if state >= 2:
        # loose papers behind the ledger, one leaning on the other
        fx.paper_fill(c, [(70, 14), (92, 16), (97, 26), (72, 50)], folds=(0, 1), stains=0.6, ink=0.7, seed=4)
        fx.paper_fill(c, [(74, 22), (97, 24), (96, 50), (75, 50)], folds=(1, 0), stains=0.8, ink=0.5, seed=5)
        # the ledger: a thick book with its page block showing along the top, wine leather, brass corners
        cover = [(22, 54), (21, 10), (24, 5), (47, 4), (71, 9), (72, 54)]
        fx.iron_fill(c, cover, ramp=WINE, hammer=0.15, rust=0.0, scratches=0.9, light=0.7, seed=6)
        fx.paper_fill(c, [(24, 5), (47, 4), (71, 9), (71, 12), (47, 8), (24, 9)], folds=(0, 0), stains=0.3, seed=7)
        for x0, y0, dx in ((22, 29, 1), (70, 29, -1)):
            fx.brass_fill(c, (x0 - (0 if dx > 0 else 4), y0 - 6, 5, 8), ramp=BRASS_AGED, profile="plate", tarnish=0.4, seed=x0)
        fx.brass_fill(c, (31, 14, 32, 9), ramp=BRASS_AGED, profile="plate", tarnish=0.5, seed=8)         # the title plate
        fx.paper_fill(c, (33, 16, 28, 5), folds=(0, 0), stains=0.2, ink=0.9, seed=9)
        for x in range(36, 60, 5):
            c.hline(x, 18, 3, (60, 40, 36))
        fx.iron_fill(c, (22, 25, 50, 3), ramp=LEATHER, hammer=0.1, rust=0.0, seed=10)                     # the strap
        # a green ribbon marks a page and hangs over the lip; a wax seal on the strap
        c.vline(58, 8, 4, MOSS[2])
        c.vline(59, 8, 4, MOSS[1])
        c.poly([(55, 28), (61, 28), (60, 33), (58, 31), (56, 33)], MOSS[2])
        fx.rivet(c, 40, 26, 2, ((90, 20, 20), (130, 30, 30), (170, 46, 40), (205, 80, 70)), shadow=True)
    if state == 3:
        fx.paper_fill(c, [(26, 56), (36, 50), (42, 61), (30, 66)], folds=(0, 0), stains=0.2, ink=0.6, seed=11,
                      ramp=((60, 90, 58), (84, 124, 74), (112, 150, 92), (146, 180, 118), (176, 206, 140)))
        fx.paper_fill(c, [(55, 54), (64, 52), (68, 62), (58, 65)], folds=(0, 0), stains=0.2, ink=0.6, seed=12,
                      ramp=((130, 60, 22), (176, 90, 30), (214, 124, 48), (238, 162, 80), (250, 200, 130)))
    return c


def dossier(state: int) -> Image.Image:
    p = Pix(112, 96, seed=60 + state)
    _box(p)
    c = _contents(state)
    if state == 3:                                                       # slips stand in the pockets: only their tops show
        pass
    # the contents sit inside the box: the front faces hide what is below the lip
    faces = ImageChops.lighter(_mask(LEFT_FACE), _mask(RIGHT_FACE))
    if state != 3:
        c.im.putalpha(ImageChops.multiply(c.im.getchannel("A"), ImageChops.invert(faces)))
    else:
        # the slips poke out of the pockets (drawn in front of the face); the ledger and papers are behind the lip
        slips = Pix(112, 96)
        slips.paste(c, 0, 0)
        c.im.putalpha(ImageChops.multiply(c.im.getchannel("A"), ImageChops.invert(faces)))
        slips.im.putalpha(ImageChops.multiply(slips.im.getchannel("A"), ImageChops.subtract(faces, Image.new("L", (112, 96), 0))))
        slips.im.putalpha(ImageChops.multiply(slips.im.getchannel("A"), _mask([(20, 40), (80, 56), (80, 80), (20, 80)])))
        p.paste(c, 0, 0)
        c = slips
    p.paste(c, 0, 0)
    fx.wear(p, LEFT_FACE + RIGHT_FACE[1:], 0.25, kinds=("scratch", "chip", "dust"), seed=state)
    return clip(p, f"dossier{state if state < 3 else 2}")


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {f"items~dossier@dossier_{i}.png": partial(dossier, i) for i in range(4)}
