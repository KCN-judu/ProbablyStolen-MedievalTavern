"""Machinery sprites, part 1: the crate-sized mechanisms ("modules") of the machine and the farm.

A module is an oak board carrying brass cogs, pipes, dials and iron blocks, closed at its right end by a banded cap
(leather, wax or iron) whose colour says what it is for, exactly as the game colours its circuit boards. The footprints
(tetromino-like pieces) follow the game's alpha so the pieces still snap together. Broken machines are in
items_machines_broken, consumables and gadgets in items_machines_amen.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import partial

from PIL import Image

from itemkit_machines import (Mask, cogbox, crack, dial, ellipse_mask, gear, pipe, plate, rects,
                              round_right, rim, rust, shade_mask, soot, spring, valve)
from palette import BRASS, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, STONE, WINE, WOOD
from pix import Color, Pix, Ramp, rgb


def five(r: Ramp) -> Ramp:
    return tuple(r) if len(r) >= 5 else (*r, tuple(min(255, c + 34) for c in r[-1]))  # type: ignore[return-value]


CAPS: dict[str, Ramp] = {
    "green": (rgb("#16231a"), rgb("#27402a"), rgb("#3e5e38"), rgb("#5e8250"), rgb("#86a86a")),
    "red": five(WINE),
    "yellow": (rgb("#4a3a1c"), rgb("#7a5f2c"), rgb("#a8884a"), rgb("#c9ab6a"), rgb("#e0cb8e")),
    "white": five(LINEN),
    "black": IRON,
    "purple": (rgb("#24122e"), rgb("#3f2150"), rgb("#5f3578"), rgb("#8052a0"), rgb("#a272c0")),
    "blue": five(NAVY),
    "tan": PALE_WOOD,
    "dark": (rgb("#0f0b10"), rgb("#1d1519"), rgb("#2b2027"), rgb("#3c2f37"), rgb("#52424a")),
}

# footprints, as (x0, y0, x1, y1) boxes, both ends included
SHAPES: dict[str, tuple[tuple[int, int, int, int], ...]] = {
    "s1": ((5, 4, 26, 27),),
    "s2": ((3, 2, 28, 29),),
    "s2h": ((3, 3, 30, 28), (17, 29, 30, 44)),
    "s2s": ((3, 2, 30, 13), (17, 14, 30, 33), (3, 34, 30, 45)),
    "s3": ((1, 1, 30, 30),),
    "c": ((3, 1, 30, 14), (17, 15, 30, 28)),
    "l": ((4, 1, 46, 14), (33, 15, 46, 28)),
    "t": ((17, 4, 30, 16), (2, 17, 30, 30), (17, 31, 30, 43)),
    "chem": ((10, 3, 30, 12), (1, 13, 30, 28)),
}

Draw = Callable[[], Image.Image]


def cap_tone(ramp: Ramp, t: int, capw: int) -> Color:
    """Colour of cap column t (0 = at the brass band): lit left, shaded right."""
    if t == 0:
        return BRASS[2]
    k = (t - 1) / max(1, capw - 2)
    return ramp[3] if k < 0.3 else ramp[2] if k < 0.65 else ramp[1]


def decorate(p: Pix, inner: Mask, kinds: Sequence[str], pitch: int, size: int, rng_seed: int) -> None:
    """Sets cogs, plates, dials and so on on a grid wherever a whole cell lies on bare board."""
    p.rng.seed(rng_seed)
    xs = [x for x, _ in inner]
    ys = [y for _, y in inner]
    h = size // 2
    row = 0
    prev: dict[int, int] = {}
    for cy in range(min(ys) + h + 1, max(ys) - h, pitch):
        col = 0
        for cx in range(min(xs) + h + 1, max(xs) - h + 1, pitch):
            box = {(x, y) for x in range(cx - h - 1, cx + h + 2) for y in range(cy - h - 1, cy + h + 2)}
            if not box <= inner:
                continue
            kind = kinds[(row * 3 + col * 2 + p.rng.randrange(len(kinds))) % len(kinds)]
            col += 1
            if cx in prev and cy - prev[cx] == pitch and kind not in ("flask",):
                p.vline(cx, prev[cx] + h + 1, pitch - 2 * h - 1, BRASS[1])
            prev[cx] = cy
            if kind == "gear":
                gear(p, cx, cy, max(2, h))
            elif kind == "gear2":
                gear(p, cx, cy, max(2, h), ramp=IRON)
            elif kind == "plate":
                plate(p, cx - h, cy - h, size, max(3, size - 1))
            elif kind == "dial":
                dial(p, cx, cy, max(2, h))
            elif kind == "pipe":
                pipe(p, cx - h, cy, size, ramp=BRASS) if p.rng.random() < 0.5 else pipe(p, cx, cy - h, size, vertical=True)
            elif kind == "spring":
                spring(p, cx - 1, cy - h, 3, size)
            elif kind == "valve":
                valve(p, cx, cy, max(2, h))
            elif kind == "cog":
                cogbox(p, cx - h, cy - h + 1, size, max(3, size - 2))
            elif kind == "flask":
                p.rect(cx - 1, cy - h, 3, size, GLASS[3])
                p.rect(cx - 1, cy, 3, h + 1, rgb("#c25b49") if p.rng.random() < 0.5 else rgb("#5e8250"))
                p.vline(cx - 1, cy - h, size, GLASS[4])
                p.px(cx, cy - h - 0, BRASS[3])
            elif kind == "sprout":
                p.vline(cx, cy - h + 1, h * 2, MOSS[1])
                p.px(cx - 1, cy - 1, MOSS[3])
                p.px(cx + 1, cy - 2, MOSS[3])
                p.px(cx, cy - h, MOSS[3])
                p.hline(cx - 1, cy + h, 3, WOOD[0])
        row += 1


def module(shape: str, cap: str, seed: int, size: tuple[int, int], *, capw: int = 5, kinds: Sequence[str] = ("gear", "plate", "cog", "dial", "pipe"),
           body: Ramp = WOOD, pitch: int = 8, comp: int = 5, teeth: bool = False, boxes: Sequence[tuple[int, int, int, int]] | None = None,
           ruin: bool = False) -> Image.Image:
    p = Pix(*size, seed=seed)
    mask = round_right(rects(*(boxes or SHAPES[shape])), 3 if capw else 0)
    right = {y: max(x for x, yy in mask if yy == y) for _, y in mask}
    cap_px = {(x, y) for x, y in mask if capw and x > right[y] - capw}
    ramp = CAPS[cap]
    shade_mask(p, mask, body, grain=0.05, base=2)
    edge = rim(mask)
    ring = {(x, y) for x, y in mask if any((x + dx, y + dy) in edge for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    inner = {(x, y) for x, y in mask - cap_px - ring if x < right[y] - capw}
    for y in range(min(yy for _, yy in mask) + 6, max(yy for _, yy in mask), 7):       # plank seams
        for x, yy in sorted(inner):
            if yy == y:
                p.px(x, y, WOOD[1])
    decorate(p, inner, kinds, pitch, comp, seed * 7 + 1)
    for x, y in cap_px:
        t = x - (right[y] - capw + 1)
        col = cap_tone(ramp, t, capw)
        top = min(yy for xx, yy in cap_px if xx == x)
        bot = max(yy for xx, yy in cap_px if xx == x)
        if t and (y - top < 2):
            col = ramp[min(4, ramp.index(col) + 1)] if col in ramp else col
        elif t and (bot - y < 2):
            col = ramp[max(0, ramp.index(col) - 1)] if col in ramp else col
        if t == 1 and top + 3 <= y <= top + 5:
            col = ramp[4]
        p.px(x, y, col)
    for x, y in edge:
        p.px(x, y, SHADOW)
    for y in sorted({y for _, y in mask}):                       # the seam in front of the cap
        if capw and (right[y] - capw, y) in mask and (right[y] - capw + 1, y) in cap_px:
            p.px(right[y] - capw, y, SHADOW)
    if teeth:                                                    # brass comb of contacts down the left edge
        for y in range(min(yy for _, yy in mask) + 3, max(yy for _, yy in mask) - 2, 2):
            x0 = min(x for x, yy in mask if yy == y)
            p.px(x0, y, BRASS[3])
    if ruin:
        pts = mask - cap_px
        for x in range(min(x for x, _ in pts) + 3, max(x for x, _ in pts) - 3, 6):
            crack(p, x, min(y for _, y in pts) + 2, 10, mask, 1 if x % 12 else -1)
        rust(p, pts, 0.1)
        soot(p, mask, 0.5)
    return p.im


def tag(group: str, name: str) -> str:
    return f"items~items_{group}@{name}.png"


ASSETS: dict[str, Draw] = {}


def add(name: str, fn: Draw) -> None:
    ASSETS[tag("module", name)] = fn


# ------------------------------------------------------------------ colour-coded families (green / red / yellow)
for colour, caps in (("green", "green"), ("red", "red"), ("yellow", "yellow")):
    for suffix, shape, size, extra in (
        ("2", "s2", (32, 32), {}), ("2_h", "s2h", (32, 48), {}), ("2_s", "s2s", (32, 48), {}),
        ("c", "c", (32, 32), {}), ("l", "l", (48, 32), {}), ("t", "t", (32, 48), {}),
    ):
        add(f"module_{colour}_{suffix}", partial(module, shape, caps, 11 + len(suffix) * 5, size, **extra))
    add(f"module_{colour}", partial(module, "s1", caps, 3, (32, 32), pitch=7, comp=5, kinds=("gear", "plate", "cog")))
add("module_red_3", partial(module, "s3", "red", 21, (32, 32)))
add("module_green_3", partial(module, "s3", "green", 21, (32, 32)))
add("module_white", partial(module, "s1", "white", 3, (32, 32), pitch=7, comp=5, kinds=("gear", "plate", "cog")))
add("module_corrupt", partial(module, "s1", "dark", 3, (32, 32), pitch=7, comp=5, kinds=("gear2", "plate", "cog"), body=OAK, ruin=True))
add("module_black_4", partial(module, "chem", "purple", 31, (32, 32), body=IRON, kinds=("gear", "dial", "cog")))
add("module_black_5", partial(module, "s3", "purple", 33, (32, 32), body=IRON, kinds=("gear", "dial", "cog", "plate")))
add("chem_module", partial(module, "chem", "tan", 35, (32, 32), pitch=7, kinds=("flask", "flask", "pipe", "valve", "dial")))

# ------------------------------------------------------------------ farm and long modules: narrow boards with a comb of contacts
FARM = ("gear", "plate", "sprout", "valve", "cog")
for name, size, cap, seed in (("farm_module5", (16, 32), "green", 41), ("farm_module6", (16, 32), "green", 42)):
    add(name, partial(module, "", cap, seed, size, capw=4, pitch=6, comp=5, kinds=FARM, teeth=True, boxes=((1, 5, 14, 28),)))
for i, cap in enumerate(("green", "green", "green", "green", "green", "green", "red", "dark"), 1):
    add(f"farm_module_l{i}", partial(module, "", cap, 50 + i, (16, 64), capw=4, pitch=6, comp=5, kinds=FARM, teeth=True, boxes=((1, 5, 14, 58),)))
for i, cap in enumerate(("blue", "tan", "dark"), 1):
    add(f"long_module{i}", partial(module, "", cap, 70 + i, (16, 64), capw=4, pitch=6, comp=5, kinds=("gear", "plate", "cog", "dial"), teeth=True,
                                   boxes=((1, 5, 14, 58),)))


# ------------------------------------------------------------------ the small ones


def shifted(im: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (dx, dy))
    return out


def aug_chip() -> Image.Image:
    p = Pix(16, 16, seed=81)
    m = rects((2, 1, 13, 14)) - {(2, 1), (13, 1), (2, 14), (13, 14)}
    shade_mask(p, m, LEATHER, grain=0.2, base=2)
    gear(p, 7, 7, 3)
    p.hline(4, 12, 8, BRASS[1])
    for x in (4, 11):
        p.px(x, 3, BRASS[4])
    return p.im


def node(w: int, h: int, seed: int) -> Image.Image:
    p = Pix(w, h, seed=seed)
    m = rects((1, 0 if h == 16 else 2, 14, h - (0 if h == 16 else 2) - 1))
    m -= {(1, min(y for _, y in m)), (14, min(y for _, y in m))}
    shade_mask(p, m, IRON, base=2)
    y0, y1 = min(y for _, y in m) + 3, max(y for _, y in m) - 3
    p.rect(4, y0, 8, y1 - y0 + 1, PARCHMENT[2])
    p.hline(4, y0, 8, PARCHMENT[4])
    p.vline(4, y0, y1 - y0 + 1, PARCHMENT[3])
    p.hline(4, y1, 8, PARCHMENT[0])
    p.frame(3, y0 - 1, 10, y1 - y0 + 3, SHADOW)
    for x, y in ((2, min(yy for _, yy in m) + 1), (13, max(yy for _, yy in m) - 1)):
        p.px(x, y, BRASS[4])
    if h == 16:
        gear(p, 8, 8, 3)
    else:
        gear(p, 8, y0 + 4, 3)
        dial(p, 8, y1 - 4, 3)
    return p.im


def hydro_kit() -> Image.Image:
    p = Pix(32, 32, seed=91)
    m = rects((2, 3, 27, 28), (26, 2, 29, 5), (26, 26, 29, 28), (28, 2, 29, 4))
    shade_mask(p, m, OAK, grain=0.2, base=3)
    p.rect(6, 7, 18, 18, SOOT[0])                                  # the open front: four brass pipes standing in the dark
    p.frame(5, 6, 20, 20, SHADOW)
    for i in range(4):
        pipe(p, 8 + i * 4, 8, 15, vertical=True, thick=3)
    for y in (10, 18):
        p.hline(7, y, 16, IRON[3])
        p.hline(7, y + 1, 16, IRON[1])
    for y in (4, 26):                                              # iron corner straps with rivets
        p.rect(3, y, 24, 2, IRON[2])
        p.hline(3, y, 24, IRON[3])
        for x in (5, 13, 21):
            p.px(x, y, BRASS[4])
    p.hline(26, 3, 4, IRON[3])
    p.hline(26, 27, 4, IRON[2])
    for x, y in ((28, 3), (28, 27)):
        p.px(x, y, BRASS[3])
    for x in range(3, 27):
        p.px(x, 28, SHADOW)
    return p.im


def crane(adv: bool) -> Image.Image:
    """The extractor: a stone drum with a post, a jointed boom and a hanging iron claw."""
    p = Pix(32, 48, seed=95 + adv)
    arm = (rgb("#4a1c0e"), rgb("#8a3a16"), rgb("#c2561a"), rgb("#e0842c"), rgb("#f6b25a")) if not adv else CAPS["purple"]
    base = rects((5, 38, 26, 46))
    base = {(x, y) for x, y in base if not ((x < 7 and y < 40) or (x > 24 and y < 40))}
    shade_mask(p, base, STONE, grain=0.3, base=2)
    for x in range(6, 26, 5):
        p.vline(x, 40, 6, STONE[1])
    p.hline(7, 41, 18, STONE[4])
    post = rects((12, 22, 19, 37))
    shade_mask(p, post, arm, base=2)
    p.hline(12, 33, 8, BRASS[3])
    p.hline(12, 30, 8, BRASS[1])
    for y in (28, 36):
        p.px(14, y, BRASS[4])
    drum = ellipse_mask(16, 22, 6, 5)
    shade_mask(p, drum, arm, base=2)
    gear(p, 16, 22, 3, teeth=8)
    boom = [(16, 18), (10, 11), (14, 5), (22, 5), (26, 9)]
    for (x0, y0), (x1, y1) in zip(boom, boom[1:], strict=False):
        for dx, dy, c in ((0, 0, arm[2]), (1, 0, arm[1]), (-1, 0, arm[3])):
            p.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, c)
    for x, y in boom[1:4]:
        gear(p, x, y, 2, ramp=BRASS)
    for pt in ((16, 18), (10, 11), (14, 5), (22, 5)):
        p.px(pt[0], pt[1], BRASS[4])
    p.vline(26, 10, 8, IRON[3])                                    # chain
    for y in range(10, 18, 2):
        p.px(27, y, IRON[1])
    p.rect(23, 18, 7, 3, IRON[2])                                  # claw
    p.hline(23, 18, 7, IRON[4])
    for x0, x1 in ((23, 25), (29, 27)):
        p.line(x0, 21, x1, 26, IRON[3])
        p.px(x1, 27, BRASS[3])
    p.outline(SHADOW)
    return p.im


add("aug_chip", aug_chip)
add("node_s", partial(node, 16, 16, 83))
add("node_m", partial(node, 16, 32, 84))
add("hydro_upgrade_kit", hydro_kit)
add("module_extractor", lambda: shifted(crane(False), -3, -1))
add("module_extractor_adv", lambda: shifted(crane(True), -3, -1))


def core() -> Image.Image:
    p = Pix(32, 32, seed=97)
    m = rects((1, 3, 30, 18), (10, 19, 30, 28))
    shade_mask(p, m, IRON, grain=0.1, base=2)
    for x in range(3, 29, 4):
        p.px(x, 5, BRASS[3])
        p.px(x, 16, BRASS[3])
    gear(p, 19, 14, 7, teeth=8)
    gear(p, 19, 14, 4, ramp=IRON)
    p.ellipse(17, 12, 5, 5, WINE[3])
    p.px(17, 12, WINE[4])
    gear(p, 8, 9, 3)
    gear(p, 14, 24, 2, ramp=IRON)
    pipe(p, 12, 25, 16, thick=3)
    p.px(25, 5, BRASS[4])
    return p.im


def ruined() -> Image.Image:
    """module_red/green family wrecked: charred, split, a cog on the floor of the break."""
    p = Pix(32, 32, seed=99)
    boxes = ((2, 4, 30, 13), (4, 2, 10, 3), (13, 1, 30, 3), (18, 14, 28, 26), (20, 27, 27, 27))
    m = round_right(rects(*boxes), 3)
    shade_mask(p, m, OAK, grain=0.3, base=2)
    soot(p, m, 0.6)
    for x, y in ((10, 6), (14, 8), (22, 6), (8, 10)):
        p.px(x, y, SOOT[0])
    gear(p, 9, 9, 3, ramp=IRON)
    cogbox(p, 15, 6, 5, 4)
    crack(p, 22, 3, 12, m, -1)
    crack(p, 26, 14, 10, m, -1)
    rust(p, m, 0.12)
    for x, y in ((20, 16), (21, 17), (24, 20), (23, 24)):
        p.px(x, y, FLAME2)
    return p.im


FLAME2 = rgb("#c2561a")
add("core", core)
add("module_ruined", ruined)
