"""Medicine of the tavern pack (the apothecary's shelf) and the padded cloth: phials, bottles, lozenges, bandage rolls,
wineskin bags, syringes, the salve pot, and the quilted gambeson cloth.

Other gear lives in items_gear_*.py (organs and watch gear, ship parts, blades and crossbows, backpacks).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_gear import (AMBER, BONE, FLESH, OCHRE, PLUM, ROSE, SEA, SKY, STEEL, dots, ell_m, finish, label, line_m,
                          paint, poly_m, puff, rect_m, rrect_m, seal, stitches, stud, bands_h, bands_v, outline_only)
from palette import (BRASS, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, PARCHMENT, SHADOW, STONE, WINE, WOOD, OAK)
from pix import Pix, Ramp, rgb

Draw = Callable[[], Image.Image]

WAX_RED: Ramp = WINE
CORK: Ramp = (rgb("#4a2b14"), rgb("#7a4a24"), rgb("#a8703a"), rgb("#c99458"))


def _file(name: str) -> str:
    return f"items~items_medical@{name}.png"


# ------------------------------------------------------------------------------------------------ phials and bottles

def phial(liquid: Ramp, wax: Ramp, seed: int) -> Image.Image:
    """The small serum phial: a wax-sealed stopper, a round glass belly with a parchment label (16x32)."""
    p = Pix(16, 32, seed=seed)
    puff(p, poly_m([(7, 5), (8, 5), (10, 9), (5, 9)]), wax, r=2)            # the wax cone over the stopper
    puff(p, rect_m(6, 9, 4, 3), CORK, r=1)
    body = rrect_m(4, 12, 8, 15, 3)
    puff(p, body, lambda x, y: liquid if y >= 15 else GLASS, r=3)
    p.vline(5, 14, 6, GLASS[4])
    p.px(5, 20, liquid[3])
    p = _fin(p)
    label(p, 5, 18, 6, 5, ink=SHADOW)
    p.px(10, 17, GLASS[3])
    return p.im


def _fin(p: Pix) -> Pix:
    finish(p)
    return p


def bottle(w: int, h: int, x: int, y: int, liquid: Ramp, band: Ramp | None, seed: int, size: tuple[int, int] = (16, 32),
           dark: bool = False) -> Image.Image:
    """A corked apothecary bottle with a label: (x, y) top-left of the glass, w x h the glass body."""
    p = Pix(*size, seed=seed)
    cx = x + w // 2
    neck = 4
    nx = cx - neck // 2
    puff(p, rect_m(nx - 1, y - 3, neck + 2, 3), CORK, r=1)                  # cork
    puff(p, rect_m(nx, y, neck, 3), liquid if dark else GLASS, r=1)         # neck
    shoulder = poly_m([(nx, y + 2), (nx + neck - 1, y + 2), (x + w - 1, y + 5), (x, y + 5)])
    body = rrect_m(x, y + 3, w, h - 3, 2)
    m = body | shoulder
    top = y + 6 + (h - 6) // 4
    puff(p, m, lambda xx, yy: liquid if (yy >= top or dark) else GLASS, r=3)
    if not dark:
        p.vline(x + 1, y + 7, max(2, h // 3), GLASS[4])
    p = _fin(p)
    ly = y + h // 2 - 1
    label(p, x + 1, ly, w - 2, min(7, h // 3 + 1), ink=SHADOW, band=band[2] if band else None)
    return p.im


def dust_vial(powder: Ramp, seed: int, sparkle: tuple[int, int, int]) -> Image.Image:
    """A tiny stoppered vial of powder (16x16, drawn in the middle 8 columns)."""
    p = Pix(16, 16, seed=seed)
    puff(p, rect_m(6, 2, 4, 2), CORK, r=1)
    puff(p, rect_m(6, 4, 4, 2), GLASS, r=1)
    puff(p, rrect_m(5, 6, 6, 8, 2), lambda x, y: powder if y >= 8 else GLASS, r=2)
    p = _fin(p)
    p.vline(6, 7, 2, GLASS[4])
    dots(p, [(8, 9), (7, 11), (9, 12), (9, 10)], sparkle)
    return p.im


# ------------------------------------------------------------------------------------------------ bandages and bags

def bandage(cloth: Ramp, kind: str, seed: int) -> Image.Image:
    """An upright roll of linen with the loose end pinned: 16x32 canvas, content inside (1, 4)-(15, 29)."""
    p = Pix(16, 32, seed=seed)
    body = rrect_m(2, 6, 12, 22, 2)
    top = ell_m(2, 4, 12, 6)
    puff(p, body, cloth, r=4, flat=0.0)
    puff(p, top, cloth, r=2, bias=0.2)
    p.px(8, 7, cloth[0])
    p.hline(7, 6, 3, cloth[0])                                                  # the hollow core
    p.hline(6, 7, 5, cloth[1]) if False else None
    for yy in range(11, 27, 4):                                                 # the turns of the wrap
        for xx in range(2, 14):
            off = (xx - 2) // 4
            p.px(xx, yy + off % 2, cloth[1])
    if kind == "fish":
        for yy in range(12, 26, 3):
            for xx in range(3 + (yy // 3) % 2 * 2, 13, 4):
                p.px(xx, yy, cloth[3])
                p.px(xx + 1, yy, cloth[3])
    elif kind == "hemostatic":
        p.rect(2, 16, 12, 4, WINE[2])
        p.hline(2, 16, 12, WINE[3])
        p.hline(2, 19, 12, WINE[1])
        p.rect(7, 16, 2, 4, LINEN[3])
        p.rect(6, 17, 4, 2, LINEN[3])
    elif kind == "topical":
        p.rect(2, 15, 12, 3, MOSS[2])
        p.hline(2, 15, 12, MOSS[3])
        p.hline(2, 17, 12, MOSS[1])
        for xx in range(4, 13, 3):
            p.px(xx, 16, MOSS[3])
    p = _fin(p)
    # the pin, laid across the end of the bandage
    p.line(9, 22, 14, 26, BRASS[4])
    p.line(9, 23, 14, 27, BRASS[2])
    p.px(14, 26, BRASS[0])
    p.px(9, 22, BRASS[4])
    p.px(10, 21, BRASS[3])
    return p.im


def skin(body: Ramp, seed: int) -> Image.Image:
    """A leather bag of blood-wine hung by a thong, with a stoppered spout (32x48)."""
    p = Pix(32, 48, seed=seed)
    bag = poly_m([(8, 12), (23, 12), (28, 17), (29, 32), (25, 40), (20, 41), (11, 41), (6, 40), (3, 32), (4, 17)])
    puff(p, bag, body, r=6)
    puff(p, rect_m(11, 9, 10, 4), LEATHER, r=1)                           # the folded neck
    puff(p, rect_m(13, 40, 6, 5), CORK, r=1)
    p = _fin(p)
    p.draw.arc((12, 2, 19, 9), 0, 360, fill=BRASS[3])
    p.draw.arc((13, 3, 18, 8), 0, 360, fill=BRASS[1])
    p.px(13, 4, BRASS[4])
    stitches(p, 6, 18, 8, 36, body[0], 2)
    stitches(p, 26, 18, 25, 36, body[1], 2)
    label(p, 10, 20, 12, 13, ink=SHADOW, band=body[3])
    p.rect(12, 28, 8, 1, body[2])
    seal(p, 15, 35, WAX_RED if body is not WINE else NAVY)
    return p.im


# ------------------------------------------------------------------------------------------------ pills and lozenges

def _capsule(p: Pix, a: tuple[int, int], b: tuple[int, int], w: int, r1: Ramp, r2: Ramp) -> None:
    """A capsule along a line from a to b, split into two colours at the middle."""
    m = line_m([a, b], w)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    half1 = {q for q in m if (q[0] - mx) * dx + (q[1] - my) * dy < 0}
    half2 = m - half1
    puff(p, m, lambda x, y: r1 if (x - mx) * dx + (y - my) * dy < 0 else r2, r=3)
    del half1, half2


def pill_diag(r1: Ramp, r2: Ramp, seed: int) -> Image.Image:
    p = Pix(16, 16, seed=seed)
    _capsule(p, (4, 4), (11, 11), 7, r1, r2)
    p = _fin(p)
    p.px(4, 5, r1[3])
    p.px(5, 4, r1[3])
    return p.im


def pill_flat(r1: Ramp, r2: Ramp, seed: int) -> Image.Image:
    """The horizontal lozenge, two-toned, with a groove across the middle (inside 1..15, 4..12)."""
    p = Pix(16, 16, seed=seed)
    puff(p, rrect_m(2, 5, 12, 6, 3), lambda x, y: r1 if x < 8 else r2, r=3)
    p = _fin(p)
    p.vline(8, 5, 6, SHADOW)
    p.hline(3, 6, 4, r1[3])
    p.hline(9, 6, 4, r2[3])
    return p.im


def pill_twins(ramp: Ramp, seed: int) -> Image.Image:
    p = Pix(16, 16, seed=seed)
    for x0 in (3, 8):
        puff(p, rrect_m(x0, 2, 5, 12, 2), ramp, r=2)
    p = _fin(p)
    for x0 in (4, 9):
        p.vline(x0, 4, 3, ramp[3])
    p.hline(3, 8, 5, SHADOW)
    p.hline(8, 8, 5, SHADOW)
    return p.im


def pill_round_pair(seed: int) -> Image.Image:
    """Two small pressed lozenges, one overlapping the other, each with a cross scored in it."""
    p = Pix(16, 16, seed=seed)
    puff(p, ell_m(3, 3, 6, 6), BONE, r=3)
    puff(p, ell_m(7, 8, 6, 6), STONE_BONE, r=3)
    p = _fin(p)
    p.hline(4, 6, 4, BONE[1])
    p.vline(6, 4, 4, BONE[1])
    p.hline(8, 11, 4, BONE[1])
    p.vline(10, 9, 4, BONE[1])
    return p.im


STONE_BONE: Ramp = (rgb("#4e4540"), rgb("#7c726a"), rgb("#a69c90"), rgb("#cbc2b2"))


def chew_plug(seed: int) -> Image.Image:
    """A paper-wrapped plug of chewing herb tied with twine (inside 1..15, 4..12)."""
    p = Pix(16, 16, seed=seed)
    puff(p, rrect_m(2, 5, 12, 6, 1), BONE, r=2)
    p = _fin(p)
    for i in range(0, 12, 2):
        p.px(3 + i, 9 - (i // 2) % 2 * 0, BONE[1])
    p.vline(5, 5, 6, LEATHER[2])
    p.vline(10, 5, 6, LEATHER[2])
    p.px(5, 5, LEATHER[3])
    p.px(10, 5, LEATHER[3])
    dots(p, [(7, 7), (8, 8), (12, 6), (3, 7)], MOSS[2])
    return p.im


def smelling_salt(seed: int) -> Image.Image:
    """A flat wax-paper packet with crimped ends and a scribbled label (inside 1..14 x 6..9)."""
    p = Pix(16, 16, seed=seed)
    puff(p, rect_m(1, 6, 14, 4), BONE, r=2)
    p = _fin(p)
    p.vline(2, 6, 4, BONE[1])
    p.vline(13, 6, 4, BONE[1])
    for xx in range(4, 12, 2):
        p.px(xx, 8, SHADOW)
    p.px(5, 7, WINE[2])
    p.px(9, 7, WINE[2])
    return p.im


def salve_pot(seed: int) -> Image.Image:
    """A round pewter pot of salve, lid marked with a moss-green cross (32x32, inside 2..30 x 6..27)."""
    p = Pix(32, 32, seed=seed)
    side = rect_m(4, 15, 24, 10) | ell_m(4, 20, 24, 6)
    puff(p, side, STEEL, r=4)
    p.hline(4, 20, 24, STEEL[1])
    puff(p, ell_m(3, 8, 26, 14), STEEL, r=5, bias=0.12)
    puff(p, ell_m(6, 10, 20, 10), STEEL, r=4, bias=0.2)
    p = _fin(p)
    p.rect(14, 12, 4, 7, MOSS[2])
    p.rect(12, 14, 8, 3, MOSS[2])
    p.hline(14, 12, 4, MOSS[3])
    p.hline(12, 14, 8, MOSS[3])
    p.hline(12, 16, 8, MOSS[1])
    p.hline(14, 18, 4, MOSS[1])
    p.hline(8, 23, 16, STEEL[1])
    for xx in range(5, 28, 3):
        p.px(xx, 22, STEEL[0])
    return p.im


# ------------------------------------------------------------------------------------------------ syringes

def syringe(w: int, x0: int, x1: int, cy: int, bh: int, barrel: Ramp, tip: Ramp, seed: int, bone_rod: bool = True,
            cap: bool = False) -> Image.Image:
    """A bone-and-brass clyster syringe lying across the picture: needle at the left, thumb ring at the right."""
    p = Pix(w, 16, seed=seed)
    fx = x1 - 6                                  # the flange (finger plate) at the end of the barrel
    nx = x0 + 12                                 # where the barrel starts
    puff(p, rect_m(nx - 3, cy - 1, 4, 3), tip, r=1)                           # brass nozzle
    puff(p, rect_m(nx, cy - bh, fx - nx, bh * 2 + 1), barrel, r=bh + 1, flat=0.2)
    p.hline(nx + 2, cy - bh + 1, max(2, fx - nx - 6), barrel[-1])                # glass sheen
    p.hline(nx, cy - bh + 1, 1, barrel[-2])
    puff(p, rect_m(fx, cy - bh - 1, 2, bh * 2 + 3), tip, r=1)                   # flange
    puff(p, rect_m(nx - 1, cy - bh, 2, bh * 2 + 1), tip, r=1)                    # collar
    rod = BONE if bone_rod else STEEL
    puff(p, rect_m(fx + 2, cy - 1, x1 - fx - 5, 2), rod, r=1)
    puff(p, ell_m(x1 - 3, cy - bh - 1, 3, bh * 2 + 3), tip, r=1)                # thumb plate
    p = _fin(p)
    for xx in range(nx + 4, fx - 2, 4):                                          # graduations
        p.px(xx, cy + bh - 1, barrel[0])
    # the needle: long steel point
    p.hline(x0, cy, nx - 3 - x0, STEEL[3])
    p.hline(x0 + 3, cy, nx - 3 - x0 - 3, STEEL[4])
    p.px(x0, cy, STEEL[2])
    if cap:
        p.px(x0 + 4, cy - 1, STEEL[2])
    return p.im


# ------------------------------------------------------------------------------------------------ the gambeson cloth

def gambeson() -> Image.Image:
    """A folded bolt of quilted gambeson cloth, tied with two straps (48x16, inside 2..46 x 0..16)."""
    p = Pix(48, 16, seed=7)
    puff(p, rrect_m(3, 1, 42, 13, 3), LINEN, r=4, flat=0.3)
    p.hline(5, 12, 38, LINEN[0])
    # quilting: diagonal stitch lines in both directions
    for xx in range(-12, 48, 5):
        for k in range(10):
            x, y = xx + k, 2 + k
            if 4 <= x <= 43 and 2 <= y <= 11:
                p.px(x, y, LINEN[1])
            x2 = xx + 10 - k
            if 4 <= x2 <= 43 and 2 <= y <= 11:
                p.px(x2, y, LINEN[1])
    p.hline(4, 13, 40, WOOD[2])                                            # the binding of the edge
    p.hline(5, 14, 38, WOOD[0])
    for x0 in (11, 33):
        p.rect(x0, 1, 3, 13, WINE[2])
        p.vline(x0, 1, 13, WINE[3])
        p.vline(x0 + 2, 1, 13, WINE[1])
        p.px(x0 + 1, 7, BRASS[3])
    outline_only(p)
    return p.im


def _syr(w: int, x0: int, x1: int, cy: int, bh: int, barrel: Ramp, tip: Ramp, seed: int) -> Draw:
    return partial(syringe, w, x0, x1, cy, bh, barrel, tip, seed)


ASSETS: Mapping[str, Draw] = {
    _file("blue_serum"): partial(phial, SKY, NAVY, 1),
    _file("green_serum"): partial(phial, MOSS, MOSS, 2),
    _file("purple_serum"): partial(phial, PLUM, PLUM, 3),
    _file("red_serum"): partial(phial, WINE, WINE, 4),
    _file("red_serum_s"): lambda: _small_serum(),
    _file("med_bottle_blue"): partial(bottle, 10, 24, 3, 6, SKY, SKY, 5),
    _file("med_bottle_red"): partial(bottle, 10, 24, 3, 6, WINE, WINE, 6),
    _file("med_bottle_orange"): partial(bottle, 10, 21, 3, 7, AMBER, AMBER, 7),
    _file("med_bottle_violet"): partial(bottle, 11, 26, 2, 5, PLUM, PLUM, 8),
    _file("med_bottle_small_pink"): partial(bottle, 10, 10, 3, 4, ROSE, ROSE, 9, (16, 16)),
    _file("black_bottle"): partial(bottle, 10, 22, 3, 7, IRON, None, 10, (16, 32), True),
    _file("dream_dust"): partial(dust_vial, BONE, 11, (200, 220, 255)),
    _file("nightmare_dust"): partial(dust_vial, WINE, 12, (220, 90, 70)),
    _file("bandage_small"): partial(bandage, LINEN, "plain", 13),
    _file("bandage_fish"): partial(bandage, SEA, "fish", 14),
    _file("hemostatic_bandage_small"): partial(bandage, LINEN, "hemostatic", 15),
    _file("topical_bandage_small"): partial(bandage, ROSE, "topical", 16),
    _file("blood_bag"): partial(skin, WINE, 17),
    _file("blue_blood_bag"): partial(skin, NAVY, 18),
    _file("cafeine_pill"): partial(pill_flat, AMBER, OCHRE, 19),
    _file("pill1"): partial(pill_diag, SKY, SEA, 20),
    _file("pill2"): partial(pill_diag, MOSS, OCHRE, 21),
    _file("items_medical_12"): partial(pill_diag, STONE, IRON, 22),
    _file("items_medical_15"): partial(pill_twins, PLUM, 23),
    _file("oxycodone_pill"): partial(pill_round_pair, 24),
    _file("zerochew"): partial(chew_plug, 25),
    _file("smelling_salt"): partial(smelling_salt, 26),
    _file("salve"): partial(salve_pot, 27),
    _file("injector_black"): _syr(64, 5, 59, 8, 2, IRON, BRASS, 28),
    _file("injector_green"): _syr(64, 5, 59, 8, 2, MOSS, BRASS, 29),
    _file("injector_pink"): _syr(64, 5, 59, 8, 2, ROSE, BRASS, 30),
    _file("injector_pink_alt"): _syr(64, 5, 59, 8, 3, PLUM, BRASS, 31),
    _file("injector_purple_large"): _syr(64, 5, 59, 8, 3, MOSS, BRASS, 32),
    _file("injector_pure_white_s"): _syr(48, 3, 45, 8, 2, BONE, BRASS, 33),
    "items~items_armor@kotton_fabric.png": gambeson,
}


def _small_serum() -> Image.Image:
    """The little phial (16x16, content 3..12 x 0..16): a short flask with a red wax top."""
    p = Pix(16, 16, seed=40)
    puff(p, poly_m([(7, 2), (8, 2), (10, 5), (5, 5)]), WINE, r=2)
    puff(p, rect_m(6, 5, 4, 2), CORK, r=1)
    puff(p, rrect_m(4, 7, 8, 8, 3), lambda x, y: WINE if y >= 10 else GLASS, r=3)
    p = _fin(p)
    p.vline(5, 8, 3, GLASS[4])
    p.rect(6, 11, 4, 2, PARCHMENT[3])
    p.hline(7, 12, 2, SHADOW)
    return p.im
