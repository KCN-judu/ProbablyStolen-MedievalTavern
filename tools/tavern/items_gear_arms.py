"""Blades, cudgels and crossbows: the melee and ranged weapons of the tavern pack.

Melee weapons lie horizontally with the point to the right. Crossbows are seen from above (stock to the right, the bow
across it, a bolt on the rail) so they read as ranged weapons at a glance.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_gear import (AMBER, BONE, STEEL, bands_h, dots, ell_m, finish, line_m, outline_only, paint, poly_m, puff,
                          rect_m, rrect_m, stitches, stud)
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, OAK, PALE_WOOD, SHADOW, WINE, WOOD
from pix import Pix, Ramp, rgb

Draw = Callable[[], Image.Image]
Fn = Callable[[int], int]


def _f(name: str) -> str:
    return f"items~items_weapons_melee@{name}.png"


def blade(p: Pix, x0: int, x1: int, top: Fn, bot: Fn, ramp: Ramp = STEEL, fuller: bool = True) -> None:
    """A blade between two edge curves: lit upper face, a dark fuller groove, shaded lower face, bright edge line."""
    for x in range(x0, x1 + 1):
        t, b = top(x), bot(x)
        for y in range(t, b + 1):
            if y == t:
                c = ramp[4]
            elif y == b:
                c = ramp[1]
            elif fuller and b - t >= 4 and y == (t + b) // 2:
                c = ramp[1]
            elif y * 2 < t + b:
                c = ramp[3]
            else:
                c = ramp[2]
            p.px(x, y, c)
        if b - t >= 3 and fuller and x > x0 + 1 and x < x1 - 2:
            p.px(x, (t + b) // 2 + 1, ramp[4]) if (x % 6 == 0) else None


def taper(x0: int, x1: int, cy: int, hw: int, start: float = 0.55) -> tuple[Fn, Fn]:
    """Edge curves for a blade of half-width hw that runs straight, then tapers to a point at x1."""
    xs = x0 + (x1 - x0) * start

    def half(x: int) -> float:
        return hw if x <= xs else hw * (x1 - x) / max(1, x1 - xs)

    return (lambda x: cy - round(half(x))), (lambda x: cy + round(half(x)))


def grip(p: Pix, x0: int, x1: int, cy: int, hh: int, ramp: Ramp, wrap: Ramp | None = None) -> None:
    puff(p, rrect_m(x0, cy - hh, x1 - x0 + 1, hh * 2 + 1, 1), ramp, r=hh + 1, flat=0.3)
    if wrap is not None:
        for x in range(x0 + 1, x1, 3):
            p.vline(x, cy - hh + 1, hh * 2 - 1, wrap[1])
            p.vline(x + 1, cy - hh + 1, 1, wrap[3])


def guard(p: Pix, x: int, cy: int, hh: int, w: int = 3, ramp: Ramp = BRASS) -> None:
    puff(p, rect_m(x, cy - hh, w, hh * 2 + 1), ramp, r=2)


def pommel(p: Pix, x: int, cy: int, r: int, ramp: Ramp = BRASS) -> None:
    puff(p, ell_m(x, cy - r, r * 2, r * 2), ramp, r=r)


def sword(w: int, h: int, cy: int, *, gx: int, tip: int, hw: int, grip_ramp: Ramp, ramp: Ramp = STEEL, start: float = 0.6,
          wrap: Ramp | None = LEATHER, gh: int | None = None, pom: int = 2, x0: int = 1, seed: int = 0) -> Image.Image:
    p = Pix(w, h, seed=seed)
    gh = gh if gh is not None else hw + 2
    top, bot = taper(gx + 3, tip, cy, hw, start)
    blade(p, gx + 3, tip, top, bot, ramp)
    grip(p, x0 + pom * 2 - 1, gx, cy, max(1, hw - 1) if hw < 4 else 2, grip_ramp, wrap)
    pommel(p, x0, cy, pom)
    guard(p, gx, cy, gh)
    p = finish(p) and p
    stud(p, gx, cy - gh + 1) if gh > 3 else None
    return p.im


def razor() -> Image.Image:
    """A folding razor: wooden scales with brass bolsters and a single clipped blade."""
    p = Pix(64, 16, seed=1)
    top, bot = taper(30, 60, 8, 2, 0.5)
    blade(p, 30, 60, top, bot, STEEL, False)
    grip(p, 4, 30, 8, 3, PALE_WOOD)
    guard(p, 28, 8, 3, 3)
    guard(p, 4, 8, 3, 2)
    p = finish(p) and p
    stud(p, 12, 7)
    stud(p, 21, 7)
    p.hline(8, 8, 14, PALE_WOOD[4])
    return p.im


def falchion() -> Image.Image:
    """A long curved single-edged blade (the machete): straight spine, belly that swells then curves to the tip."""
    p = Pix(144, 16, seed=2)
    spine = lambda x: 3 + (max(0, x - 124) * 6) // 20
    belly = lambda x: min(13, 8 + (x - 30) // 18) if x < 124 else 13 - (x - 124) * 8 // 19
    blade(p, 30, 143, spine, lambda x: max(spine(x) + 1, belly(x)), STEEL)
    grip(p, 4, 26, 8, 2, WOOD, LEATHER)
    guard(p, 26, 8, 5, 4)
    pommel(p, 1, 8, 3, IRON)
    p = finish(p) and p
    stud(p, 27, 4)
    stud(p, 27, 11)
    return p.im


def crow() -> Image.Image:
    """The pry bar: black iron, a hooked claw at the left, a flat chisel at the right, a wine-red leather grip."""
    p = Pix(96, 16, seed=3)
    puff(p, line_m([(10, 7), (90, 7)], 3), IRON, r=2, bias=0.2)
    puff(p, line_m([(10, 7), (6, 4), (3, 3)], 3), IRON, r=2, bias=0.2)
    puff(p, line_m([(8, 5), (3, 6), (3, 9)], 2), IRON, r=1, bias=0.2)
    puff(p, poly_m([(82, 5), (94, 3), (94, 8), (92, 11), (82, 9)]), STEEL, r=2)
    puff(p, line_m([(30, 7), (62, 7)], 3), WINE, r=2)
    p = finish(p) and p
    for x in range(32, 62, 4):
        p.vline(x, 6, 3, WINE[0])
    return p.im


def shard(wrapped: bool) -> Image.Image:
    """A splinter of obsidian-bright glass; the shiv has a cloth-wrapped handle."""
    p = Pix(48, 16, seed=4)
    obs: Ramp = (rgb("#10202a"), rgb("#1f3a48"), rgb("#3f6a7c"), rgb("#7aa8b4"), rgb("#c4e0e0"))
    if wrapped:
        top = lambda x: 4 + max(0, (46 - x) // 8) if x >= 17 else 5
        puff(p, poly_m([(15, 4), (22, 2), (36, 5), (46, 10), (24, 12), (15, 11)]), obs, r=3)
        puff(p, rrect_m(2, 5, 15, 6, 2), LINEN, r=3)
    else:
        puff(p, poly_m([(2, 8), (10, 3), (24, 2), (36, 5), (46, 11), (20, 13), (8, 12)]), obs, r=4)
    p = finish(p) and p
    if wrapped:
        for x in range(4, 16, 3):
            p.line(x, 11, x + 2, 5, LEATHER[1])
        p.line(15, 4, 15, 11, LEATHER[2])
    else:
        p.line(8, 6, 22, 5, obs[4])
        p.line(24, 6, 34, 7, obs[3])
    return p.im


def hand_axe() -> Image.Image:
    """The hatchet: a haft along the top, a bearded iron head hanging at the right end."""
    p = Pix(64, 32, seed=5)
    grip(p, 4, 52, 9, 2, WOOD, LEATHER)
    puff(p, ell_m(2, 6, 5, 7), WOOD, r=2)
    puff(p, poly_m([(46, 4), (54, 4), (58, 10), (61, 28), (55, 28), (50, 22), (46, 16)]), STEEL, r=2, bias=0.1)
    puff(p, rect_m(44, 3, 6, 14), IRON, r=2)
    p = finish(p) and p
    p.line(59, 17, 60, 28, STEEL[4])
    p.vline(52, 7, 5, SHADOW)
    stud(p, 46, 5)
    stud(p, 46, 12)
    return p.im


def cleaver() -> Image.Image:
    p = Pix(80, 32, seed=6)
    grip(p, 6, 28, 9, 3, WOOD)
    puff(p, rrect_m(26, 3, 52, 24, 3) - rect_m(70, 3, 8, 2), STEEL, r=5, flat=0.4)
    p = finish(p) and p
    p.hline(27, 4, 49, STEEL[4])
    p.hline(27, 5, 49, STEEL[1])
    p.hline(27, 25, 49, STEEL[4])
    p.hline(30, 20, 40, STEEL[3])
    p.hline(60, 8, 6, STEEL[4])
    p.px(70, 9, SHADOW)
    p.rect(68, 8, 3, 3, SHADOW)
    p.rect(69, 9, 1, 1, STEEL[3])
    for x in (10, 17, 24):
        stud(p, x, 8)
    p.hline(7, 8, 20, WOOD[4])
    p.rect(26, 6, 3, 7, BRASS[2])
    return p.im


def knife(w: int, hw: int, tip: int, seed: int, rivets: int = 3, curve: bool = False) -> Image.Image:
    """Kitchen knife / skinning knife: wooden handle with brass rivets, an iron bolster and a long blade."""
    p = Pix(w, 16, seed=seed)
    cy = 8
    if curve:
        top = lambda x: 4 + (((x - 38) ** 2) * 6 // 576 if x > 38 else 0)
        bot = lambda x: 12 - ((x - 44) * 2 // 18 if x > 44 else 0)
        blade(p, 22, tip, top, lambda x: max(bot(x), top(x) + 1), STEEL)
    else:
        t, b = taper(22, tip, cy, hw, 0.62)
        blade(p, 22, tip, t, b, STEEL)
    grip(p, 3, 22, cy, 3, WOOD)
    puff(p, rect_m(2, cy - 3, 2, 7), IRON, r=1)
    guard(p, 21, cy, hw + 1, 2, IRON)
    p = finish(p) and p
    for i in range(rivets):
        stud(p, 7 + i * 5, cy - 1)
    p.hline(5, cy - 2, 14, WOOD[4])
    return p.im


def staff() -> Image.Image:
    """The pipe becomes a shepherd's staff: ash wood with an iron-shod foot and a crook that bends down at the end."""
    p = Pix(80, 32, seed=8)
    pts = [(5, 7), (64, 7), (71, 8), (75, 12), (75, 19)]
    puff(p, line_m(pts, 4), PALE_WOOD, r=2, bias=0.1)
    puff(p, rect_m(3, 5, 6, 5), IRON, r=1)
    puff(p, rect_m(73, 22, 5, 4), IRON, r=1)
    puff(p, line_m([(75, 19), (75, 22)], 4), PALE_WOOD, r=2)
    p = finish(p) and p
    for x in (16, 30, 44, 58):
        p.vline(x, 6, 4, PALE_WOOD[1])
        p.px(x + 1, 6, PALE_WOOD[4])
    p.hline(10, 6, 52, PALE_WOOD[4])
    stud(p, 5, 6)
    return p.im


def clog() -> Image.Image:
    """The sandal is a wooden-soled house slipper in wine wool with a brass buckle (48x64, inside 4..45 x 3..61)."""
    p = Pix(48, 64, seed=9)
    puff(p, ell_m(6, 4, 38, 56), PALE_WOOD, r=7)
    puff(p, poly_m([(9, 26), (40, 26), (43, 36), (41, 46), (9, 46), (7, 36)]), WINE, r=6)
    puff(p, ell_m(9, 8, 30, 18), WINE, r=7)
    p = finish(p) and p
    for y in range(12, 24, 3):
        p.hline(14, y, 20, WINE[1])
    p.hline(9, 26, 32, WINE[1])
    p.rect(20, 32, 8, 10, BRASS[2])
    p.rect(22, 34, 4, 6, WINE[2])
    p.hline(20, 32, 8, BRASS[4])
    p.vline(20, 32, 10, BRASS[4])
    p.hline(20, 41, 8, BRASS[0])
    stitches(p, 12, 28, 38, 28, WINE[3], 2)
    return p.im


def mace() -> Image.Image:
    """The baton becomes a flanged iron mace with a brass collar and leather-wrapped haft."""
    p = Pix(96, 16, seed=10)
    grip(p, 4, 66, 8, 2, WOOD, LEATHER)
    puff(p, ell_m(1, 5, 5, 6), BRASS, r=2)
    guard(p, 64, 8, 3, 4)
    puff(p, ell_m(70, 2, 15, 12), IRON, r=5, bias=0.15)
    for x in (72, 76, 80):
        puff(p, rect_m(x, 1, 3, 14), IRON, r=1, bias=0.25)
    puff(p, poly_m([(85, 6), (92, 8), (85, 10)]), STEEL, r=1)
    puff(p, poly_m([(78, 1), (80, 1), (79, 0)]), STEEL, r=1)
    puff(p, poly_m([(78, 14), (80, 14), (79, 15)]), STEEL, r=1)
    p = finish(p) and p
    stud(p, 66, 6)
    stud(p, 66, 9)
    p.hline(72, 6, 11, IRON[4])
    return p.im


# --------------------------------------------------------------------------------------------- crossbows

def crossbow(*, w: int = 64, h: int = 48, cy: int = 24, bow_x: int, reach: int, stock: Ramp, bow: Ramp, butt: int = 3,
             muzzle: int = 58, strung: bool = True, bolt: bool = True, brass_lock: bool = True, extra: str = "",
             stock_hw: int = 4, seed: int = 0) -> Image.Image:
    """A crossbow from above, butt at the left. `bow_x` is where the bow crosses the stock (its tips point back to the
    string), `reach` is the half-height of the bow."""
    p = Pix(w, h, seed=seed)
    # the bow limbs: an arc bulging toward the muzzle, drawn as thick connected segments
    top_tip, bot_tip = (bow_x - 7, cy - reach), (bow_x - 7, cy + reach)
    arc = [top_tip, (bow_x - 3, cy - reach * 2 // 3), (bow_x + 1, cy - reach // 3), (bow_x + 3, cy), (bow_x + 1, cy + reach // 3),
           (bow_x - 3, cy + reach * 2 // 3), bot_tip]
    puff(p, line_m(arc, 5), bow, r=3, bias=0.1)
    # the stock: a tapering tiller with a butt plate and a rail on top
    st = poly_m([(butt, cy - stock_hw - 1), (butt + 14, cy - stock_hw), (muzzle, cy - 2), (muzzle, cy + 2),
                 (butt + 14, cy + stock_hw), (butt, cy + stock_hw + 1)])
    puff(p, st, stock, r=3, flat=0.3)
    puff(p, rect_m(butt, cy - stock_hw - 1, 3, stock_hw * 2 + 3), BRASS if brass_lock else IRON, r=1)
    if extra == "stirrup":
        puff(p, ell_m(muzzle - 2, cy - 5, 9, 10) - ell_m(muzzle, cy - 3, 5, 6), IRON, r=2, bias=0.2)
    if extra == "drum":
        puff(p, ell_m(butt + 18, cy - 8, 14, 16), BRASS, r=6)
        puff(p, ell_m(butt + 22, cy - 4, 6, 8), IRON, r=2)
    if extra == "flask":
        puff(p, ell_m(butt + 16, cy - 9, 13, 18), AMBER, r=6)
        puff(p, rect_m(butt + 21, cy - 11, 4, 3), BRASS, r=1)
    p = finish(p) and p
    # lashing where the bow meets the stock
    for dx in range(-2, 3, 2):
        p.vline(bow_x + dx, cy - 4, 9, LEATHER[3] if stock is not BONE else LEATHER[2])
    p.hline(bow_x - 2, cy - 4, 5, LEATHER[1])
    p.hline(bow_x - 2, cy + 4, 5, LEATHER[0])
    if brass_lock:
        puff(p, rect_m(butt + 16, cy - 2, 7, 5), BRASS, r=1)
        stud(p, butt + 17, cy - 1)
        p.hline(butt + 8, cy, 7, stock[0])
    p.hline(butt + 4, cy - 2, 9, stock[-1] if len(stock) > 4 else stock[3])
    if strung:
        sx = bow_x - 7
        for y in range(cy - reach, cy + reach + 1):
            p.px(sx, y, BONE[3] if y in (cy - reach, cy + reach) else BONE[2])
        p.px(sx + 1, cy - 1, BONE[1])
        for y in (cy - reach + 1, cy + reach - 1):
            p.px(sx - 1, y, BONE[4])
    if bolt:
        p.hline(bow_x - 6, cy, muzzle - bow_x + 8, PALE_WOOD[3])
        p.hline(bow_x - 6, cy - 1, muzzle - bow_x + 8, PALE_WOOD[4])
        p.px(muzzle + 2, cy, STEEL[4])
        p.hline(muzzle, cy - 1, 3, STEEL[3])
        p.px(muzzle + 3, cy, STEEL[2])
        p.px(bow_x - 6, cy - 1, FLAME[1])
        p.px(bow_x - 6, cy + 1, FLAME[1])
    return p.im


def _xb(**kw) -> Draw:
    return partial(crossbow, **kw)


SWD = partial(sword)

ASSETS: Mapping[str, Draw] = {
    _f("box_cutter"): razor,
    _f("combat_knife_2"): partial(sword, 80, 16, 8, gx=26, tip=79, hw=4, grip_ramp=WOOD, wrap=LEATHER, gh=6, pom=2, seed=11),
    _f("combat_machete"): falchion,
    _f("crowbar"): crow,
    _f("glass_shard"): partial(shard, False),
    _f("glass_shard_shiv"): partial(shard, True),
    _f("hatchet"): hand_axe,
    _f("kitchen_cleaver"): cleaver,
    _f("kitchen_knife"): partial(knife, 80, 4, 78, 12, 3),
    _f("pipe"): staff,
    _f("sandal_weapon"): clog,
    _f("skinning_knife"): partial(knife, 64, 3, 62, 13, 3, True),
    _f("stun_baton"): mace,
    **{f"items~items_weapons_ranged_energy@{n}.png": d for n, d in {
        "glock_receiver": _xb(bow_x=46, reach=20, stock=WOOD, bow=OAK, muzzle=60, seed=1),
        "handmade_pistol": _xb(bow_x=44, reach=17, stock=PALE_WOOD, bow=WOOD, muzzle=58, brass_lock=False, seed=2),
        "handmade_pistol_frame": _xb(bow_x=46, reach=14, stock=PALE_WOOD, bow=WOOD, muzzle=58, brass_lock=False, strung=False,
                                    bolt=False, seed=3, butt=5),
        "heavy_handmade_pistol": _xb(bow_x=44, reach=22, stock=WOOD, bow=IRON, muzzle=60, extra="stirrup", stock_hw=5, seed=4),
        "heavy_handmade_pistol_frame": _xb(bow_x=44, reach=18, stock=WOOD, bow=IRON, muzzle=58, extra="stirrup", strung=False,
                                          bolt=False, stock_hw=5, seed=5),
        "printed_gun": _xb(bow_x=47, reach=19, stock=BONE, bow=PALE_WOOD, muzzle=60, seed=6, butt=4),
        "revolver": _xb(bow_x=48, reach=18, stock=OAK, bow=WOOD, muzzle=60, extra="drum", seed=7, butt=2),
        "stun_gun": _xb(bow_x=46, reach=19, stock=WOOD, bow=OAK, muzzle=58, extra="flask", seed=8, butt=4),
    }.items()},
}
