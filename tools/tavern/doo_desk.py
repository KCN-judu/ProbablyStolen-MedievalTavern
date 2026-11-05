"""`desk`: the bar. The oak top is left exactly as shop.desk() draws it; this paints the weaker parts to the cask's
standard on top of it: the two legs (own boards, grain, side face, forged shoe with rivets), the apron's planks and
iron straps, the till drawer under the apron (panelled front, brass pull, keyhole, runners and a shadow) and the
wing's strapped front."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

import shop
from fxkit import brass_fill, contact_shadow, iron_fill, rivet, wood_fill
from palette import BRASS, IRON, OAK, PALE_WOOD, SHADOW, WOOD
from pix import Pix

TOP_Y1, FOOT, LEGS, LEFT_X, MAIN_X1 = shop.TOP_Y1, shop.FOOT, shop.LEGS, shop.LEFT_X, shop.MAIN_X1


def leg(p: Pix, x: int, seed: int) -> None:
    y0, w, h = TOP_Y1 + 14, 26, FOOT - TOP_Y1 - 14
    face = (x, y0, w, h - 18)
    wood_fill(p, face, grain_dir="v", ramp=OAK, board=13, joints=False, nails=False, knots=0.6, wear_amount=0.6, damp=0.35,
              damp_from="bottom", light=0.55, bias=0.7, seed=seed)
    p.vline(x, y0, h - 18, OAK[4])
    p.vline(x + 1, y0, h - 18, OAK[3])
    p.vline(x + w - 1, y0, h - 18, OAK[0])
    side = x + w if x < 480 else x - 5
    wood_fill(p, (side, y0, 5, h - 2), grain_dir="v", ramp=OAK, board=5, joints=False, nails=False, knots=0, wear_amount=0.3,
              light=0.0, bias=-0.6, seed=seed + 1)
    p.vline(side + (0 if x < 480 else 4), y0, h - 2, OAK[0])
    # the iron shoe: a boot of forged iron with a flared lip, riveted on both faces
    sy = FOOT - 20
    contact_shadow(p, (x - 2, sy, w + 9, 18), shift=(3, 2), spread=3, strength=1.0, alpha=220, squash=0.6)
    iron_fill(p, (x - 2, sy, w + 9, 17), hammer=0.7, rust=0.5, seed=seed + 2)
    for rx in (x + 4, x + w - 5, x + w + 3):
        rivet(p, rx, sy + 7, 1, BRASS)
    p.hline(x - 2, FOOT - 3, w + 9, IRON[0])
    p.hline(x - 2, FOOT - 2, w + 9, OAK[0])
    p.hline(x - 2, FOOT - 1, w + 9, OAK[0])


def apron(p: Pix) -> None:
    """The apron's planks (with their seams) and straps, replacing the flat strip."""
    y, h = TOP_Y1 + 2, 11
    wood_fill(p, (LEFT_X, y + 1, MAIN_X1 - LEFT_X, h - 1), grain_dir="h", ramp=OAK, board=11, joints=True, nails=True, knots=0.5,
              wear_amount=0.6, light=0.4, bias=0.6, seed=61)
    p.hline(LEFT_X, y, MAIN_X1 - LEFT_X, OAK[3])
    p.hline(LEFT_X, y + h, MAIN_X1 - LEFT_X, OAK[0])
    for sx in range(262, 800, 118):
        contact_shadow(p, (sx, y + 1, 8, h - 1), shift=(2, 1), spread=2, strength=0.8, alpha=200, squash=1.0)
        iron_fill(p, (sx, y + 1, 8, h - 1), hammer=0.6, rust=0.4, seed=sx)
        rivet(p, sx + 4, y + 3, 1, BRASS)
        rivet(p, sx + 4, y + 8, 1, BRASS)
    # wing front
    wx = round(shop.toward_vp(MAIN_X1, TOP_Y1, shop.WING_Y1))
    wy = shop.WING_Y1 + 2
    wood_fill(p, (wx, wy, 960 - wx, 14), grain_dir="h", ramp=OAK, board=14, joints=True, nails=True, knots=0.4, wear_amount=0.6,
              light=0.4, bias=0.6, seed=62)
    p.hline(wx, wy - 1, 960 - wx, PALE_WOOD[3])
    p.hline(wx, wy + 15, 960 - wx, OAK[0])
    for sx in (wx + 22, wx + 80):
        contact_shadow(p, (sx, wy, 7, 14), shift=(2, 1), spread=2, strength=0.8, alpha=200, squash=1.0)
        iron_fill(p, (sx, wy, 7, 14), hammer=0.6, rust=0.4, seed=sx)
        rivet(p, sx + 3, wy + 4, 1, BRASS)
        rivet(p, sx + 3, wy + 10, 1, BRASS)


def till(p: Pix) -> None:
    """The till: a drawer hung under the apron on two runner rails, its panelled pale-oak front, a brass drop-pull and
    a keyhole plate, with the shade it throws on the stone behind."""
    x, y, w, h = 376, TOP_Y1 + 14, 150, 16
    contact_shadow(p, (x - 2, y, w + 4, h + 2), shift=(2, 5), spread=5, strength=1.0, alpha=230, squash=1.0)
    for rx in (x - 6, x + w):                                     # runner rails fixed to the underside of the apron
        iron_fill(p, (rx, y - 3, 6, 6), hammer=0.4, rust=0.3, seed=rx)
        rivet(p, rx + 3, y - 1, 1, BRASS)
    wood_fill(p, (x, y, w, h), grain_dir="h", ramp=PALE_WOOD, board=16, joints=False, nails=False, knots=0.4, wear_amount=0.6,
              light=0.4, bias=0.2, seed=63)
    p.frame(x + 4, y + 3, w - 8, h - 6, PALE_WOOD[1])             # a raised panel: shaded inside top-left
    p.hline(x + 5, y + h - 4, w - 10, PALE_WOOD[4])
    p.vline(x + w - 5, y + 4, h - 8, PALE_WOOD[4])
    p.hline(x, y, w, PALE_WOOD[4])
    p.hline(x, y + h - 1, w, OAK[0])
    p.vline(x, y, h, PALE_WOOD[4])
    p.vline(x + w - 1, y, h, OAK[0])
    brass_fill(p, (x + w // 2 - 11, y + 5, 22, 4), profile="tube", tarnish=0.3, seed=64)          # the pull bar
    for px in (x + w // 2 - 11, x + w // 2 + 10):
        rivet(p, px, y + 7, 1, BRASS)
    brass_fill(p, (x + w - 22, y + 4, 9, 9), profile="plate", tarnish=0.5, seed=65)                # the keyhole plate
    p.px(x + w - 18, y + 7, SHADOW)
    p.px(x + w - 18, y + 8, SHADOW)
    p.px(x + w - 18, y + 9, SHADOW)


def desk() -> Image.Image:
    base = shop.desk()
    p = Pix(960, 540, seed=24)
    p.paste(base, 0, 0)
    for x, sd in zip(LEGS, (71, 72)):
        leg(p, x, sd)
    apron(p)
    till(p)
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"desk.960x540.png": desk}
