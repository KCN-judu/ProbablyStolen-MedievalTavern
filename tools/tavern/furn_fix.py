"""`drain` (128x32), `faucet` and `faucet1` (160x80): the floor drain and the taps of the tavern.

drain    A floor drain is, in a tavern cellar, an iron grating let into a stone slab: bars over a dark sump, a worn channel
         polished by the slops that run to it, wet stains, rust and a little moss in the joints.
faucet   A brass ale spigot (a cask tap) on a stout oak block that is strapped and nailed to the wall: a turned wooden lever
         on its stem, the valve body, a flared nozzle. Closed: lever upright, a bead of ale hanging on the nozzle.
faucet1  The same tap driven into a horizontal cask lying in its cradle; open: the lever is turned level, a thin stream of
         ale runs from the nozzle (the cask on top is what the modern tube was)."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Final

from PIL import Image

import fxkit as fx
from furn_cask import Cask
from furn_kit import ALE, BRASS_AGED, clip
from furn_masks import RUNS
from palette import BRASS, FLAME, GLASS, IRON, MOSS, OAK, PALE_WOOD, SHADOW, SOOT, STONE, WOOD
from pix import Pix, mix


def rows_poly(key: str, y0: int, y1: int, inset: int = 0) -> list[tuple[int, int]]:
    """The polygon of the occupied area between rows y0 and y1, from the outer ends of each row's runs."""
    rows = [(y, RUNS[key][y][0][0] + inset, RUNS[key][y][-1][1] - 1 - inset) for y in range(y0, y1 + 1) if RUNS[key][y]]
    return [(l, y) for y, l, _ in rows] + [(r, y) for y, _, r in reversed(rows)]


# ---------------------------------------------------------------------------------------------- the drain


def _slant(key: str, y: float) -> tuple[float, float]:
    """Left and right x of the drain's slab at row y (the slab is a parallelogram, drawn in the floor's perspective)."""
    ya = int(max(4, min(30, y)))
    r = RUNS[key][ya]
    return r[0][0], r[-1][1] - 1


def drain() -> Image.Image:
    p = Pix(128, 32, seed=110)
    top, bot = 4, 30

    def pt(u: float, v: float) -> tuple[float, float]:
        """(u across 0..1, v down 0..1) inside the slab's parallelogram."""
        y = top + v * (bot - top)
        l, r = _slant("drain", y)
        return l + u * (r - l), y

    def quad(u0: float, v0: float, u1: float, v1: float) -> list[tuple[int, int]]:
        pts = [pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1)]
        return [(round(x), round(y)) for x, y in pts]

    slab = rows_poly("drain", top, bot)
    # the slab: tooled stone, its lit upper-left rim and its dark front edge
    reg = fx.iron_fill(p, slab, ramp=STONE, hammer=0.55, rust=0.0, scratches=0.9, light=0.5, seed=3)
    for x, y in reg.pixels():
        n = fx.vnoise(x / 9, y / 5, 31)
        if n > 0.78 and fx.noise(x, y, 4) < 0.6:
            p.px(x, y, mix(p.get(x, y)[:3], STONE[1][:3], 0.55))
        elif n < 0.1:
            p.px(x, y, mix(p.get(x, y)[:3], STONE[4][:3], 0.3))
    # the slab's front thickness (down and right): a darker band along the lower edge
    for y in range(bot - 2, bot + 1):
        l, r = _slant("drain", y)
        for x in range(round(l), round(r) + 1):
            p.px(x, y, STONE[0] if y == bot else STONE[1])
    # the sump below the grate: dark, with a gleam of water
    frame = quad(0.1, 0.17, 0.9, 0.9)
    pit = quad(0.13, 0.24, 0.87, 0.84)
    fx.iron_fill(p, frame, ramp=IRON, hammer=0.6, rust=0.55, rivets=0, seed=8)
    pr = fx.region(p, pit)
    for x, y in pr.pixels():
        p.px(x, y, SOOT[0] if (x + y) % 5 else SOOT[1])
    for x, y in pr.pixels():
        if fx.noise(x // 2, y, 6) < 0.05:
            p.px(x, y, GLASS[1])
    # the bars run along the slope of the slab: set them out by u, the cross-bars by v
    nbars = 13
    for i in range(nbars):
        u = 0.15 + (0.7 * i) / (nbars - 1)
        bar = [pt(u, 0.24), pt(u + 0.017, 0.24), pt(u + 0.017, 0.84), pt(u, 0.84)]
        fx.iron_fill(p, [(round(a), round(b)) for a, b in bar], ramp=IRON, hammer=0.1, rust=0.3, scratches=0.2, seed=20 + i)
    for k, v in enumerate((0.42, 0.66)):                               # two flat cross straps, riveted
        a, b = pt(0.11, v - 0.05), pt(0.89, v - 0.05)
        poly = quad(0.11, v - 0.055, 0.89, v + 0.055)
        fx.iron_fill(p, poly, ramp=IRON, hammer=0.4, rust=0.4, rivets=9, seed=40 + k)
    # a polished, worn channel of water leading to the grate from the upper left, and wet stains round it
    for x, y in reg.pixels():
        l, r = _slant("drain", y)
        u = (x - l) / max(1, r - l)
        v = (y - top) / (bot - top)
        inside = 0.1 < u < 0.9 and 0.17 < v < 0.9
        if inside:
            continue
        d = min(abs(u - 0.1) if v > 0.1 else 9, abs(u - 0.9) if v > 0.1 else 9, abs(v - 0.17) * 1.4, abs(v - 0.9) * 1.4)
        if d < 0.07 and (x + y) % 2 == 0 and fx.noise(x, y, 12) < 0.8:
            p.px(x, y, mix(p.get(x, y)[:3], STONE[0][:3], 0.55))          # wet
        elif d < 0.13 and fx.noise(x, y, 13) < 0.3 and v < 0.95:
            p.px(x, y, mix(p.get(x, y)[:3], MOSS[0][:3], 0.5))            # slime in the joint
        elif 0.3 < u < 0.42 and v < 0.17 and fx.noise(x, y, 14) < 0.5:
            p.px(x, y, STONE[3])                                          # the worn, polished channel
    for k in range(5):                                                     # rust runs down from the frame onto the stone
        x, y = pt(0.2 + 0.15 * k, 0.9)
        for j in range(1, 3 + k % 2):
            fx.over(p, round(x), round(y) + j, (140, 74, 34), 120 - j * 35)
    fx.wear(p, slab, 0.5, kinds=("chip", "scratch", "dent"), seed=6)
    return clip(p, "drain")


# ---------------------------------------------------------------------------------------------- the taps


def _brass_poly(p: Pix, poly: list[tuple[int, int]], seed: int, profile: str = "tube", tarnish: float = 0.75) -> None:
    fx.brass_fill(p, poly, ramp=BRASS_AGED, profile=profile, tarnish=tarnish, seed=seed)


def _tap_body(p: Pix, open_tap: bool) -> None:
    """The valve body and the nozzle: a brass barrel at the top that tapers into the nozzle, with bands, a bonnet nut, a
    maker's plate and a flange. Drawn in the faucet's shape (rows 36..78)."""
    body = rows_poly("faucet", 38, 68)
    _brass_poly(p, body, 5)
    spout = rows_poly("faucet", 66, 78)
    _brass_poly(p, spout, 6)
    # bands (hoops of the valve) on the body: cross bands with studs at the ends
    for x0, w in ((56, 6), (104, 7)):
        fx.iron_fill(p, (x0, 40 if x0 < 100 else 40, w, 27 if x0 < 100 else 15), ramp=IRON, hammer=0.2, rust=0.35, rivets=7, seed=x0)
    # the bonnet: a domed brass boss on the front with a slot
    fx.brass_fill(p, fx.ellipse(84, 50, 12, 9), ramp=BRASS_AGED, profile="dome", tarnish=0.5, seed=9)
    fx.rivet(p, 84, 50, 2, BRASS)
    for x, y in fx.ellipse(84, 50, 8, 6, 24):
        fx.over(p, x, y, SHADOW, 150)
    # a lit rim on the underside curve and a green stain where the damp gathers
    for x in range(64, 100):
        if fx.noise(x, 3, 8) < 0.5:
            fx.over(p, x, 62 + (x - 64) // 9, (74, 128, 104), 95)
    # the nozzle: a flared ring
    fx.brass_fill(p, (65, 66, 16, 4), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=11)
    fx.rivet(p, 70, 74, 1, BRASS)


def _lever_closed(p: Pix) -> None:
    """The lever stands upright: a turned oak knob on a brass stem seated in a collar at the left end of the body."""
    fx.brass_fill(p, (51, 31, 6, 9), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=12)                 # stem
    fx.brass_fill(p, (48, 36, 10, 4), ramp=BRASS_AGED, profile="tube", tarnish=0.5, seed=13)                # collar
    fx.wood_fill(p, fx.ellipse(52, 28, 5, 5), "v", PALE_WOOD, board=3, light=0.6, seed=14, knots=0, joints=False, nails=False)
    fx.wood_fill(p, (49, 23, 7, 3), "h", PALE_WOOD, board=3, seed=15, knots=0, joints=False, nails=False)


def _drops(p: Pix, open_tap: bool) -> None:
    if open_tap:                                                            # a thin stream of ale from the nozzle
        for y in range(70, 78):
            for x, i in ((70, 3), (71, 4), (72, 2)):
                p.px(x, y, ALE[i if (y + x) % 3 else 4])
        p.px(71, 78, ALE[4])
    else:                                                                   # a bead of ale hangs from the nozzle
        p.px(71, 75, ALE[3])
        p.px(70, 76, ALE[2])
        p.px(71, 76, ALE[4])
        p.px(72, 76, ALE[1])
        p.px(71, 77, ALE[2])


def faucet() -> Image.Image:
    p = Pix(160, 80, seed=100)
    fx.wall_shadow(p, rows_poly("faucet", 9, 78), offset=(3, 3), spread=2, strength=0.6)
    # the oak block the tap is fixed to: banded with iron and nailed
    fx.wood_fill(p, (75, 9, 41, 29), "v", OAK, board=9, light=0.5, seed=21, knots=0.6, joints=False, nails=False, damp=0.3)
    for y, s in ((12, 31), (30, 32)):
        fx.iron_band(p, [(75 + k, y) for k in range(41)], 5, rivets=8, rust=0.3, hammer=0.3, seed=s)
    # a brass pipe in the block leads down into the body
    fx.brass_fill(p, (90, 24, 8, 14), ramp=BRASS_AGED, profile="tube", tarnish=0.6, seed=33)
    _tap_body(p, False)
    _lever_closed(p)
    _drops(p, False)
    fx.wear(p, rows_poly("faucet", 9, 78), 0.25, kinds=("scratch", "dent"), seed=1)
    return clip(p, "faucet")


def _horizontal_cask(p: Pix) -> None:
    """A cask lying on its side in a cradle: staves along its length, hoops across, a bung on top. It is drawn standing
    in a transposed canvas (so the light, upper left, falls on its top) and turned onto its side."""
    mask = Pix(80, 160)
    cols = {}
    for x in range(160):
        ys = [y for y in range(0, 41) if any(a <= x < b for a, b in RUNS["faucet1"][y])]
        if ys:
            cols[x] = (min(ys), max(ys))
    cy = 20.5

    class Lying(Cask):
        def hw(self, yc: float) -> float:                                  # half the cask's height at a column
            t, b = cols.get(max(7, min(153, round(yc))), (14, 28))
            return (b - t) / 2 + 0.5

        def outline(self) -> list[tuple[int, int]]:
            xs = sorted(cols)
            return [(round(cy - self.hw(x)), x) for x in xs] + [(round(cy + self.hw(x)), x) for x in reversed(xs)]

    c = Lying(cy, 7, 153, 19, 0, 1.0)
    from furn_cask import cask_body
    cask_body(mask, c, (26, 52, 108, 134), staves=11, seed=17, damp=0.0, hoop_thick=5)
    t = mask.im.transpose(Image.Transpose.TRANSPOSE)
    p.paste(t, 0, 0)
    # the bung and a cradle under the belly
    fx.wood_fill(p, fx.ellipse(80, 8, 7, 3), "h", OAK, board=2, seed=3, knots=0, joints=False, nails=False)
    p.px(79, 7, PALE_WOOD[2])
    for x0 in (19, 122):
        fx.wood_fill(p, [(x0, 34), (x0 + 14, 34), (x0 + 12, 40), (x0 + 2, 40)], "h", OAK, board=3, seed=x0, knots=0, joints=False, nails=False)


def faucet1() -> Image.Image:
    p = Pix(160, 80, seed=101)
    _horizontal_cask(p)
    # the tap is driven into the cask's belly: a brass flange plate with studs
    fx.brass_fill(p, (48, 36, 66, 5), ramp=BRASS_AGED, profile="plate", tarnish=0.6, studs=7, seed=30)
    _tap_body(p, True)
    # open: the lever lies level on the body, pointing out to the left, instead of standing upright
    fx.brass_fill(p, (54, 43, 22, 5), ramp=BRASS_AGED, profile="tube", tarnish=0.4, seed=41)
    fx.wood_fill(p, fx.ellipse(56, 45, 5, 5), "v", PALE_WOOD, board=3, light=0.6, seed=42, knots=0, joints=False, nails=False)
    fx.rivet(p, 74, 45, 1, BRASS)
    _drops(p, True)
    return clip(p, "faucet1")


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "items~items_furniture@drain.png": drain,
    "items~items_furniture@faucet.png": faucet,
    "items~items_furniture@faucet1.png": faucet1,
}
