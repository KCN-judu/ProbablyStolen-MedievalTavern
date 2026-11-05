"""Specimen jars (the organs) and the town-watch kit (quarrel crates, bolt bundles, the shock prod, the poison carboy).

Organs and the carboy are opaque in the game (a solid square); here they sit on a dark shelf backdrop of the same size.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_gear import (AMBER, BONE, FLESH, KIDNEY, LIVER, LUNG, STEEL, bands_h, dots, ell_m, finish, flip_m, label,
                          outline_only, poly_m, puff, rect_m, rrect_m, stitches, stud, line_m, move_m)
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import Pix, Ramp, rgb

Draw = Callable[[], Image.Image]
BROTH: Ramp = (rgb("#1b2a24"), rgb("#2a4538"), rgb("#3f6a4c"), rgb("#6a9468"))


def _backdrop(w: int, h: int, seed: int) -> Pix:
    """A dark wall of a cellar shelf with a plank at the bottom."""
    p = Pix(w, h, fill=OAK[0], seed=seed)
    p.gradient(0, 0, w, h - h // 8, OAK[1], OAK[0], 5)
    for x in range(0, w, 7):
        p.vline(x, 0, h, OAK[0])
    p.rect(0, h - max(3, h // 8), w, max(3, h // 8), WOOD[1])
    p.hline(0, h - max(3, h // 8), w, WOOD[3])
    p.hline(0, h - 1, w, WOOD[0])
    return p


def _organ_mask(kind: str) -> tuple[set, Ramp]:
    if kind == "heart":
        m = (ell_m(10, 12, 7, 7) | ell_m(15, 12, 7, 7) | poly_m([(10, 16), (21, 16), (16, 26)]) | rect_m(13, 9, 2, 4)
             | rect_m(17, 9, 2, 4))
        return m, FLESH
    if kind == "liver":
        return poly_m([(8, 16), (13, 13), (22, 14), (24, 17), (20, 23), (13, 23), (9, 20)]) | ell_m(9, 15, 9, 8), LIVER
    if kind.startswith("kidney"):
        m = ell_m(12, 11, 9, 14) - ell_m(9, 14, 5, 8)
        return (flip_m(m, 31) if kind.endswith("right") else m), KIDNEY
    m = poly_m([(11, 11), (18, 12), (20, 18), (19, 25), (13, 26), (10, 20)]) | ell_m(11, 13, 8, 12)
    return (flip_m(m, 31) if kind.endswith("right") else m), LUNG


def organ_jar(kind: str, seed: int) -> Image.Image:
    """An anatomical specimen floating in a sealed glass jar with a brass lid (32x32)."""
    p = _backdrop(32, 32, seed)
    jar = rrect_m(7, 7, 18, 21, 3)
    puff(p, jar, BROTH, r=3)
    p.rect(8, 9, 16, 1, BROTH[3])
    m, ramp = _organ_mask(kind)
    puff(p, m, ramp, r=3)
    if kind == "heart":
        p.vline(14, 14, 3, ramp[4 if len(ramp) > 4 else 3])
        p.px(12, 14, ramp[-1])
    elif kind == "liver":
        p.hline(12, 16, 5, ramp[0])
        p.px(10, 16, ramp[-1])
    elif kind.startswith("lung"):
        xs = 15 if kind.endswith("left") else 16
        p.vline(xs, 13, 6, ramp[0])
        p.px(xs - 1, 18, ramp[0])
        p.px(xs + 1, 20, ramp[0])
    else:
        p.px(14 if kind.endswith("left") else 17, 18, ramp[0])
    p.vline(9, 11, 9, GLASS[4])
    p.vline(10, 12, 3, GLASS[3])
    p.vline(23, 12, 12, BROTH[0])
    puff(p, rect_m(6, 4, 20, 4), BRASS, r=2)
    p.hline(7, 5, 3, BRASS[4])
    puff(p, rect_m(7, 28, 18, 2), WOOD, r=1)
    p.hline(10, 5, 1, SHADOW)
    for x in (9, 15, 22):
        p.px(x, 6, BRASS[1])
    return p.im


def example_jar() -> Image.Image:
    p = _backdrop(16, 16, 9)
    puff(p, rrect_m(4, 4, 8, 10, 2), BROTH, r=2)
    puff(p, ell_m(6, 7, 4, 5), FLESH, r=2)
    puff(p, rect_m(3, 2, 10, 2), BRASS, r=1)
    p.vline(5, 5, 4, GLASS[4])
    return p.im


# --------------------------------------------------------------------------------------------- crates

def crate(kind: str, seed: int) -> Image.Image:
    """A quarrel crate: oak boards, iron corner straps; the packed ones carry a parchment label and a colour stripe."""
    p = Pix(32, 32, seed=seed)
    body = rrect_m(2, 9, 28, 15, 1)
    puff(p, body, WOOD, r=3, flat=0.6)
    for y in (13, 18):
        p.hline(3, y, 26, WOOD[1])
    for x in (4, 12, 20):
        pass
    p.hline(3, 10, 26, WOOD[4])
    p = finish(p) and p
    for x in (3, 26):                                       # iron corner straps
        p.rect(x, 10, 3, 13, IRON[2])
        p.vline(x, 10, 13, IRON[4])
        p.vline(x + 2, 10, 13, IRON[0])
        stud(p, x, 12)
        stud(p, x, 19)
    if kind != "plain":
        stripe = {"packed": WINE, "ap": MOSS, "nl": NAVY}[kind]
        p.rect(7, 10, 18, 13, PARCHMENT[3])
        p.hline(7, 10, 18, PARCHMENT[4])
        p.hline(7, 22, 18, PARCHMENT[2])
        p.rect(7, 12, 18, 3, stripe[2])
        p.hline(7, 12, 18, stripe[3])
        for i, w in enumerate((10, 7)):
            p.hline(9, 17 + i * 2, w, PARCHMENT[0])
        if kind == "ap":                                      # an iron-headed quarrel stencilled on it
            p.hline(18, 18, 5, IRON[1])
            p.px(23, 18, IRON[1])
        elif kind == "nl":
            p.rect(19, 17, 4, 3, NAVY[2])
        else:
            p.hline(18, 18, 5, WOOD[1])
    else:
        p.hline(8, 16, 16, WOOD[0])
        p.hline(8, 17, 16, WOOD[3])
    return p.im


def bolts(heavy: bool, kind: str, seed: int) -> Image.Image:
    """A tied bundle of crossbow bolts, points up. kind: plain, nl (padded blue heads), p (green poisoned heads)."""
    p = Pix(16, 16, seed=seed)
    tip = {"plain": STEEL, "nl": NAVY, "p": MOSS}[kind]
    xs = (3, 7, 11) if heavy else (4, 7, 10)
    top, bottom = (2, 14) if heavy else (4, 14)
    y0 = 0 if heavy else 1
    top = top + (0 if heavy else 0)
    for i, x in enumerate(xs):
        t = top + (1 if i == 1 else 0) * -1
        w = 3 if heavy else 2
        puff(p, rect_m(x, t + 3, w, bottom - t - 3), PALE_WOOD, r=1)
        puff(p, poly_m([(x, t + 3), (x + w - 1, t + 3), (x + (w - 1) // 2, max(y0, t - 1))]), tip, r=1)
        puff(p, rect_m(x - (0 if heavy else 0), bottom - 3, w, 2), FLAME if kind != "nl" else BONE, r=1)
    p = finish(p) and p
    p.hline(2, 9, 12 if heavy else 10, LEATHER[3])
    p.hline(2, 10, 12 if heavy else 10, LEATHER[1])
    return p.im


def pistol_ammo_tac() -> Image.Image:
    """The game draws seven faint pixels here; a pale ring of the same footprint."""
    p = Pix(48, 48)
    c = (196, 212, 221, 127)
    for xy in ((19, 3), (20, 3), (21, 3), (19, 4), (21, 4), (19, 5), (21, 5)):
        p.px(*xy, c)
    return p.im


def shock_prod() -> Image.Image:
    """A watchman's two-pronged shock rod: leather grip, brass collar, iron fork (32x48, inside 7..25 x 6..42)."""
    p = Pix(32, 48, seed=3)
    puff(p, rrect_m(12, 22, 8, 19, 2), LEATHER, r=3)
    puff(p, rect_m(11, 17, 10, 6, ), BRASS, r=2)
    puff(p, rect_m(10, 10, 3, 8), IRON, r=1)
    puff(p, rect_m(19, 10, 3, 8), IRON, r=1)
    puff(p, poly_m([(10, 10), (12, 10), (11, 7)]), STEEL, r=1)
    puff(p, poly_m([(19, 10), (21, 10), (20, 7)]), STEEL, r=1)
    puff(p, rect_m(13, 14, 6, 4), IRON, r=1)
    p = finish(p) and p
    for y in range(24, 40, 3):
        p.hline(13, y, 6, LEATHER[0])
    p.hline(12, 19, 8, BRASS[1])
    stud(p, 13, 18)
    stud(p, 17, 18)
    dots(p, [(14, 15), (17, 14), (15, 16)], FLAME[3])
    p.hline(14, 14, 2, FLAME[4])
    p.vline(16, 40, 1, SHADOW)
    return p.im


def carboy() -> Image.Image:
    """A tall glass carboy of green vapour with a brass valve, strapped in iron (32x80, opaque like the original)."""
    p = _backdrop(32, 80, 5)
    puff(p, rect_m(12, 8, 8, 12), BROTH, r=2)
    puff(p, ell_m(3, 16, 26, 58), BROTH, r=7)
    puff(p, rect_m(10, 3, 12, 6), BRASS, r=2)
    puff(p, rect_m(14, 0, 4, 4), BRASS, r=1)
    p.vline(8, 24, 36, GLASS[4])
    p.vline(9, 28, 12, GLASS[3])
    for y in (34, 56):
        p.rect(3, y, 26, 3, IRON[2])
        p.hline(3, y, 26, IRON[4])
        p.hline(3, y + 2, 26, IRON[0])
        stud(p, 6, y)
        stud(p, 24, y)
    label(p, 10, 42, 12, 10, ink=SHADOW, band=WINE[2])
    p.rect(14, 45, 4, 3, SHADOW)
    p.px(15, 46, PARCHMENT[3])
    p.px(16, 46, PARCHMENT[3])
    p.rect(8, 74, 16, 4, WOOD[2])
    p.hline(8, 74, 16, WOOD[4])
    return p.im


ASSETS: Mapping[str, Draw] = {
    **{f"items~items_organ@organ_{k}.png": partial(organ_jar, k, i) for i, k in enumerate(
        ("heart", "kidney_left", "kidney_right", "liver", "lung_left", "lung_right"))},
    "items~items_organ@example.png": example_jar,
    "items~items_sec@ammo_box.png": partial(crate, "plain", 1),
    "items~items_sec@ammo_box_packed.png": partial(crate, "packed", 2),
    "items~items_sec@ap_ammo_box_packed.png": partial(crate, "ap", 3),
    "items~items_sec@nl_ammo_box_packed.png": partial(crate, "nl", 4),
    "items~items_sec@heavy_pistol_ammo.png": partial(bolts, True, "plain", 5),
    "items~items_sec@heavy_pistol_ammo_nl.png": partial(bolts, True, "nl", 6),
    "items~items_sec@heavy_pistol_ammo_p.png": partial(bolts, True, "p", 7),
    "items~items_sec@light_pistol_ammo.png": partial(bolts, False, "plain", 8),
    "items~items_sec@light_pistol_ammo_nl.png": partial(bolts, False, "nl", 9),
    "items~items_sec@light_pistol_ammo_p.png": partial(bolts, False, "p", 10),
    "items~items_sec@revolver_short_tac.png": pistol_ammo_tac,
    "items~items_sec@tazer.png": shock_prod,
    "items~items_sec@canister_nerve.png": carboy,
}
