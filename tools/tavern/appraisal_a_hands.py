"""Appraisal close-ups: the three prosthetic hands (iron gauntlet, dark-oak hand, brass gauntlet) in normal, worn and damaged state.

The player judges the hand by what the series shows: normal is clean; worn has scuffs on the palm, dulled tips and a grimy
cuff; damaged adds a torn-open palm with a clockwork inside and glowing cracks, a snapped little finger, a broken ring
finger, a soot-black middle fingertip and a bitten cuff. The same drawing code serves all nine, so those differences stay
in the same places for every material.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image

from appraisalkit_a import (
    BLACKENED, BRASS, DARKWOOD, GOLD, GRIME, RUST, STEEL, Mask, capsule, capsule_mask, distance_inside, gear, plate,
    poly_mask, scratches, solid, stain, streaks,
)
from palette import FLAME, LEATHER, MOSS, PARCHMENT, SHADOW, SOOT
from pix import Color, Pix, Ramp

W, H = 456, 402


@dataclass(frozen=True)
class Mat:
    ramp: Ramp
    rim: Color
    pin: Ramp              # joint pins and rivets
    scuff_dark: tuple[Color, ...]
    scuff_light: Color
    tip_wear: tuple[Color, ...]
    grain: tuple[Color, ...]
    pointed: bool = False
    cuff_point: bool = False
    wood: bool = False


STEEL_M = Mat(STEEL, (24, 22, 32), BRASS, (RUST[1], RUST[2], GRIME[1]), STEEL[5], (RUST[0], RUST[1], GRIME[1]), (STEEL[4], STEEL[1]))
WOOD_M = Mat(DARKWOOD, (14, 8, 10), STEEL, (SOOT[1], SOOT[2], DARKWOOD[0]), DARKWOOD[5], (SOOT[0], SOOT[1], SOOT[2]), (DARKWOOD[4], DARKWOOD[0]), wood=True)
GOLD_M = Mat(GOLD, (62, 34, 24), STEEL, (RUST[0], (84, 92, 66), (66, 74, 54)), GOLD[5], ((70, 78, 58), (94, 100, 76), (66, 52, 40)), (GOLD[4], GOLD[1]),
             pointed=True, cuff_point=True)

# Finger table: base, tip, radius at base, radius at tip. The thumb is separate.
FINGERS = (
    ((20, 124), (9, 52), 6.2, 5.0),
    ((43, 120), (35, 22), 7.0, 5.6),
    ((67, 118), (64, 9), 7.6, 6.0),
    ((91, 120), (93, 26), 7.0, 5.6),
)
JOINTS = (0.37, 0.69)
PALM = ((5, 130), (10, 121), (33, 117), (57, 115), (80, 115), (102, 118), (108, 126), (110, 150), (105, 190), (98, 224),
        (30, 224), (22, 192), (11, 154))


def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def shifted(points, dx: int, dy: int):
    return [(x + dx, y + dy) for x, y in points]


def facet_height2(left: int, right: int, seams: tuple[int, ...], slopes: tuple[float, ...], roll: float) -> Callable[[int, int], float]:
    centre, half = (left + right) / 2, (right - left) / 2

    def h(x: int, y: int) -> float:
        i = sum(1 for s in seams if x >= s)
        lo = ([left] + list(seams))[i]
        c = 1.0 - ((x - centre) / half) ** 2
        return (roll * math.sqrt(c) if c > 0 else 0.0) + slopes[i] * (x - lo)
    return h


def band(p: Pix, mask: Mask, c0: tuple[float, float], u: tuple[float, float], r: float, dark: Color, light: Color) -> None:
    """A groove across a finger at c0 (u runs along the finger): a dark line with a lit lip above it."""
    nx, ny = -u[1], u[0]
    steps = int(r * 2 + 2)
    for k in range(-steps, steps + 1):
        s = k / 2
        x, y = c0[0] + nx * s, c0[1] + ny * s
        q = (round(x), round(y))
        if q in mask and abs(s) <= r - 0.3:
            p.px(q[0], q[1], dark)
            q2 = (round(x - u[0] * 1.2), round(y - u[1] * 1.2))
            if q2 in mask and q2 != q:
                p.px(q2[0], q2[1], light)


def draw_finger(p: Pix, m: Mat, base, tip, r0: float, r1: float) -> Mask:
    """Three overlapping phalanges, the nearer ones over the farther, each its own lit tube: an articulated finger."""
    ux, uy = tip[0] - base[0], tip[1] - base[1]
    ln = math.hypot(ux, uy)
    u = (ux / ln, uy / ln)
    cuts = (0.0, 0.40, 0.71, 1.0)
    mask: Mask = set()
    segs = []
    for i in range(3):
        a, b = lerp(base, tip, cuts[i]), lerp(base, tip, cuts[i + 1])
        ra = r0 + (r1 - r0) * cuts[i]
        rb = r0 + (r1 - r0) * cuts[i + 1]
        segs.append((a, b, ra, rb))
    for i in (2, 1, 0):
        a, b, ra, rb = segs[i]
        if i == 2 and m.pointed:
            b = lerp(base, tip, 0.9)
        # each phalanx starts a little inside its neighbour so the rims overlap like lames
        mask |= capsule(p, a, b, ra * 0.97, rb * (0.98 if i else 0.9), m.ramp, m.rim, relief=1.15, gain=1.25, bias=-0.26, dither=False)
        if i == 2 and m.pointed:
            cut = b
            claw = ((round(cut[0] - u[1] * rb * 0.9), round(cut[1] + u[0] * rb * 0.9)),
                    (round(tip[0] + u[0] * 7), round(tip[1] + u[1] * 7 - 2)),
                    (round(cut[0] + u[1] * rb * 0.9), round(cut[1] - u[0] * rb * 0.9)))
            cm = poly_mask(claw)
            d = distance_inside(cm)
            solid(p, cm, lambda x, y: min(d.get((x, y), 0), 3) * 1.2, PARCHMENT, m.rim, relief=1.1, dither=False)
            mask |= cm
    for t in (0.40, 0.71):
        c = lerp(base, tip, t)
        r = r0 + (r1 - r0) * t
        if m.pointed:
            cx, cy = round(c[0] + u[0] * 5), round(c[1] + u[1] * 5)
            for j in range(-5, 6):
                w = 3 - abs(j) * 3 // 5
                for i in range(-w, w + 1):
                    if (cx + i, cy + j) in mask:
                        p.px(cx + i, cy + j, PARCHMENT[3] if (i + j) < 1 else PARCHMENT[1])
        else:
            cx, cy = round(c[0] - u[0] * 1), round(c[1] - u[1] * 1)
            p.rect(cx - 1, cy - 1, 3, 3, m.pin[2])
            p.px(cx - 1, cy - 1, m.pin[4])
            p.px(cx + 1, cy + 1, m.pin[0])
    return mask


def cluster_wear(p: Pix, m: Mat, rng: random.Random, region: Mask, centres, per: int, dark: tuple[Color, ...]) -> None:
    """Scuffs gather where a hand is gripped and knocked, not evenly: a few patches of short strokes."""
    for cx, cy, r in centres:
        zone = {pt for pt in region if math.hypot(pt[0] - cx, pt[1] - cy) <= r}
        if zone:
            scratches(p, zone, rng, per, rng.choice(dark), m.scuff_light, (4, 11), (1, -3))
            scratches(p, zone, rng, per // 2, dark[0], None, (3, 7), (1, -3))
            stain(p, zone, rng, cx, cy, r // 2, m.tip_wear, 0.5)


def draw_hand(m: Mat, state: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    layer = Pix(W, H)
    ox, oy = 160, 50
    p = Pix(150, 310, seed=seed)       # local canvas; (sh, sh) is the picture's (ox, oy)
    sh = 4
    flat: dict[str, object] = dict(relief=1.15, gain=1.25, bias=-0.26, dither=False)

    def S(pt):
        return (pt[0] + sh, pt[1] + sh)

    broken = state == "damage"
    worn = state in ("wear", "damage")

    # thumb first: the palm overlaps its root. Two phalanges with a bend, the lower one fat.
    ta, tm, tb = S((106, 196)), S((118, 148)), S((131, 106))
    t_mask = capsule(p, ta, tm, 12.0, 9.6, m.ramp, m.rim, **flat)
    t_mask |= capsule(p, tm, tb, 9.4, 6.8, m.ramp, m.rim, **flat)
    c = tm
    p.rect(c[0] - 2, c[1] - 1, 4, 3, m.pin[2])
    p.px(c[0] - 2, c[1] - 1, m.pin[4])
    p.px(c[0] + 1, c[1] + 1, m.pin[0])

    # fingers
    masks: list[Mask] = []
    for i, (b, t, r0, r1) in enumerate(FINGERS):
        b, t = S(b), S(t)
        if broken and i == 0:
            t = S((13, 98))                      # snapped little finger: a short stub
        if broken and i == 1:
            t = S((38, 62))                      # broken ring finger
        if broken and i == 2 and m.pointed:
            t = S((65, 15))
        masks.append(draw_finger(p, m, b, t, r0, r1))

    # the palm: lames that each tilt their own way, so the plate catches the light in strips
    seams = tuple(x + sh for x in (34, 58, 82))
    palm_pts = [S(q) for q in PALM]
    ph = facet_height2(5 + sh, 110 + sh, seams, (0.20, -0.10, 0.14, -0.18), 8.0)
    palm = poly_mask(palm_pts)
    d = distance_inside(palm)
    solid(p, palm, lambda x, y: min(d.get((x, y), 0), 3) * 1.1 + ph(x, y), m.ramp, m.rim, **flat)
    # the heel guard at the palm base, a raised plate
    pad = [S(q) for q in ((33, 172), (40, 166), (82, 166), (89, 172), (91, 218), (31, 218))]
    pm = poly_mask(pad)
    pd = distance_inside(pm)
    solid(p, pm, lambda x, y: min(pd.get((x, y), 0), 3) * 1.3 + ph(x, y) * 0.4, m.ramp, m.rim, **flat)
    for q in ((37, 175), (85, 175), (37, 212), (85, 212)):
        x, y = S(q)
        p.rect(x - 1, y - 1, 3, 3, m.pin[2])
        p.px(x - 1, y - 1, m.pin[4])
        p.px(x + 1, y + 1, m.pin[0])
    # knuckle caps where the fingers enter the palm, drawn over the palm's top edge
    for (b, _t, r0, _r1) in FINGERS:
        bx, by = S(b)
        cap_m, cap_h = capsule_mask((bx - 2, by + 3), (bx + 2, by + 3), r0 * 1.0, r0 * 1.0)
        solid(p, cap_m, cap_h, m.ramp, m.rim, **flat)
        p.rect(bx - 1, by + 2, 3, 3, m.pin[2])
        p.px(bx - 1, by + 2, m.pin[4])

    # brushing or grain
    if m.wood:
        streaks(p, palm, rng, 90, (m.grain[0], m.ramp[1], m.ramp[2], m.ramp[4]), True, (10, 40))
        for mk in masks:
            streaks(p, mk, rng, 5, (m.grain[0], m.ramp[1]), True, (6, 18))
    else:
        streaks(p, palm, rng, 40, (m.ramp[4], m.ramp[1]), True, (6, 26))

    # wrist bands, then the cuff
    for k, yy in enumerate((224, 229, 234)):
        wd = 66 + k
        p.hline(sh + 31 - k // 2, sh + yy, wd, m.rim)
        p.hline(sh + 31 - k // 2, sh + yy - 1, wd, m.ramp[4])
    if m.cuff_point:
        cuff_pts = [(30, 237), (98, 237), (103, 258), (99, 278), (64, 288), (29, 278), (25, 258)]
    else:
        cuff_pts = [(30, 237), (98, 237), (104, 258), (106, 286), (22, 286), (24, 258)]
    cuff = poly_mask([S(q) for q in cuff_pts])
    cd = distance_inside(cuff)
    ch = facet_height2(24 + sh, 106 + sh, tuple(x + sh for x in (38, 52, 66, 80, 93)), (0.2, -0.12, 0.16, -0.2, 0.1, -0.14), 10.0)
    solid(p, cuff, lambda x, y: min(cd.get((x, y), 0), 3) * 1.1 + ch(x, y), m.ramp, m.rim, **flat)
    if m.wood:
        # iron hoops round the oak cuff
        for yy in (245, 270):
            for x in range(sh + 22, sh + 108):
                if (x, sh + yy) in cuff:
                    p.px(x, sh + yy - 1, STEEL[5] if x % 5 else STEEL[4])
                    p.px(x, sh + yy, STEEL[3] if x % 9 else STEEL[1])
                    p.px(x, sh + yy + 1, STEEL[2])
                    p.px(x, sh + yy + 2, STEEL[0])
            for x in range(sh + 28, sh + 100, 12):
                p.px(x, sh + yy, BRASS[4])
    else:
        for yy in (247, 267):
            for x in range(sh + 20, sh + 110):
                for j, c in enumerate((LEATHER[3], LEATHER[2], LEATHER[2], LEATHER[1], LEATHER[0])):
                    if (x, sh + yy + j) in cuff:
                        p.px(x, sh + yy + j, c)
            for x in range(sh + 30, sh + 100, 11):
                p.px(x, sh + yy + 2, BRASS[4])
                p.px(x + 1, sh + yy + 2, BRASS[2])
        bx, by = sh + 78, sh + 244
        p.frame(bx, by, 12, 12, BRASS[1])
        p.frame(bx + 1, by + 1, 10, 10, BRASS[3])
        p.vline(bx + 6, by, 12, BRASS[2])
        p.hline(bx + 1, by + 1, 10, BRASS[4])
    if m.cuff_point:
        cx, cy = sh + 64, sh + 238
        dm = {(x, y) for y in range(cy - 12, cy + 2) for x in range(cx - 19, cx + 20)
              if ((x - cx) / 19) ** 2 + ((y - cy) / 12) ** 2 <= 1}
        solid(p, dm, lambda x, y: max(0.0, 1 - ((x - cx) / 19) ** 2 - ((y - cy) / 12) ** 2) ** 0.5 * 7, PARCHMENT, m.rim, relief=1.1, dither=False)

    if worn:
        heavy = 1 if broken else 0
        cluster_wear(p, m, rng, palm, ((sh + 86, sh + 140, 22), (sh + 40, sh + 200, 22), (sh + 60, sh + 160 - heavy * 30, 16)), 16 + 10 * heavy, m.scuff_dark)
        cluster_wear(p, m, rng, cuff, ((sh + 36, sh + 280, 14), (sh + 94, sh + 276, 14)), 8, m.scuff_dark)
        for mk in masks:
            top = min(y for _, y in mk)
            tip_zone = {pt for pt in mk if pt[1] < top + 13}
            cx = sum(x for x, _ in tip_zone) // max(1, len(tip_zone))
            stain(p, tip_zone, rng, cx, top + 4, 9, m.tip_wear, 0.95)
            scratches(p, mk, rng, 3, m.scuff_dark[0], m.scuff_light, (3, 7), (1, -3))
        stain(p, t_mask, rng, tb[0], tb[1] - 3, 8, m.tip_wear, 0.95)
    if broken:
        _damage(p, m, rng, palm, cuff, masks, sh, S)

    layer.paste(p, ox - sh, oy - sh)
    return layer.im


CLEAR_PX: Color = (0, 0, 0, 0)


def _damage(p: Pix, m: Mat, rng: random.Random, palm: Mask, cuff: Mask, masks: list[Mask], sh: int, S) -> None:
    from appraisalkit_a import outer_ring
    # the torn-open palm: a jagged hole into a clockwork, with a glowing crack down its edge
    hole_pts = [S(q) for q in ((9, 134), (18, 126), (24, 133), (34, 129), (40, 141), (33, 150), (42, 158), (38, 172), (45, 184),
                               (35, 198), (38, 208), (24, 202), (20, 188), (12, 180), (15, 165), (9, 152))]
    hole = poly_mask(hole_pts) & palm
    for (x, y) in outer_ring(hole):
        if (x, y) in palm:
            lit = (x + 1, y) in hole or (x, y + 1) in hole
            p.px(x, y, m.ramp[-1] if lit else m.rim)
    hd = distance_inside(hole)
    for (x, y) in hole:
        p.px(x, y, SOOT[0] if hd[(x, y)] > 1.5 else SOOT[1])
    gear(p, sh + 26, sh + 151, 11, 9, BRASS, phase=0.3)
    gear(p, sh + 28, sh + 182, 9, 8, BRASS, phase=1.1)
    gear(p, sh + 35, sh + 137, 5, 6, BRASS, phase=0.6)
    for k in range(4):                                   # a coiled spring in the dark
        p.hline(sh + 14 + k % 2, sh + 168 + k * 2, 6, BRASS[1] if k % 2 else BRASS[3])
    glow = [(43, 132), (41, 143), (46, 153), (42, 165), (49, 177), (44, 191), (47, 206)]
    for a, b in zip(glow, glow[1:]):
        ax, ay = S(a)
        bx, by = S(b)
        p.line(ax - 1, ay, bx - 1, by, SHADOW)
        p.line(ax, ay, bx, by, FLAME[1])
    for a in glow[::2]:
        ax, ay = S(a)
        p.px(ax, ay, FLAME[3])
        p.px(ax, ay + 1, FLAME[2])
    gx, gy = sh + 37, sh + 160
    p.rect(gx, gy, 4, 4, MOSS[2])
    p.px(gx, gy, MOSS[3])
    mid = masks[2]
    top = min(y for _, y in mid)
    tipm = {pt for pt in mid if pt[1] < top + 11}
    for (x, y) in tipm:
        p.px(x, y, SOOT[1] if (x + y) % 3 else SOOT[0])
    for (x, y) in outer_ring(tipm):
        if y < top + 11 and (x, y) in mid:
            p.px(x, y, m.rim)
    # broken ends: jagged dark stumps with a bright lip, and a dangling spring
    for i, (rx, ry, w) in enumerate(((13, 98, 6), (38, 62, 7))):
        x0, y0 = S((rx, ry))
        for k in range(-w, w + 1):
            jag = (k * 7) % 5 - 2
            for yy in range(y0 - 8, y0 + jag + 1):
                if (x0 + k, yy) in masks[i]:
                    p.px(x0 + k, yy, CLEAR_PX)
        for k in range(-w, w + 1):
            jag = (k * 7) % 5 - 2
            p.px(x0 + k, y0 + jag + 1, m.ramp[-1] if k < 0 else m.rim)
            p.px(x0 + k, y0 + jag + 2, SOOT[1])
        p.px(x0 - 1, y0 + 2, BRASS[3])
        p.px(x0 + 1, y0 + 3, BRASS[2])
    wx, wy = S((38, 62))
    for k in range(10):
        p.px(wx + 3 + k // 2, wy + 2 + k, BRASS[3] if k % 3 else BRASS[1])
    bite = [S(q) for q in ((76, 281), (84, 287), (96, 287), (98, 279))]
    for (x, y) in poly_mask(bite):
        if (x, y) in cuff:
            p.px(x, y, CLEAR_PX)


def _clear_alpha_zero(p: Pix) -> None:
    pass


def make(m: Mat, state: str, seed: int) -> Callable[[], Image.Image]:
    return lambda: draw_hand(m, state, seed)


_SEEDS = {"1steel_hand_": 11, "2carbon_hand_": 23, "3gold_hand_": 37}
_STATES = (("1normal", "normal"), ("2wear", "wear"), ("3damage", "damage"))
ASSETS: dict[str, Callable[[], Image.Image]] = {}
for _prefix, _mat in (("1steel_hand_", STEEL_M), ("2carbon_hand_", WOOD_M), ("3gold_hand_", GOLD_M)):
    for _tag, _state in _STATES:
        ASSETS[f"{_prefix}{_tag}.456x402.png"] = make(_mat, _state, _SEEDS[_prefix] + len(_state))
