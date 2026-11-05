"""The liquid vessels of the tavern: glass flasks, flagons, a wicker demijohn, a pitcher, an iron-bound vat, apothecary
measures and pipettes, each in its empty state plus the liquid and highlight layers the game stacks over it
(`items~water_container3@...`, `items~water_container4@...`), and the large in-game illustration of them all.

The crates, chests and sacks live in `items_vessels_boxes.py`.  Vessel shapes are described once (`itemkit_vessels.Vessel`)
and every fill level and colour is drawn from that description.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

import itemkit_vessels as kit
from itemkit_vessels import LEVELS, Vessel, rows_from
from palette import BRASS, GLASS, IRON, LEATHER, MOSS, OAK, PALE_WOOD, SHADOW, WINE, WOOD
from pix import Pix, rgb


# ---------------------------------------------------------------------------------------------- flasks and flagons


def _mini() -> Vessel:
    """A squat corked flask."""
    rows = rows_from([(3, 5, 11), (7, 5, 11), (10, 2, 14), (12, 1, 15), (28, 1, 15), (31, 1, 15)], 3)

    def over(p: Pix) -> None:
        kit.cork(p, 5, 0, 6, 5)

    return Vessel((16, 32), rows, 5, over=over, seed=1)


def _small() -> Vessel:
    """A tall bottle with a wax-sealed cork."""
    rows = rows_from([(5, 5, 11), (15, 5, 11), (21, 1, 15), (44, 1, 15), (47, 1, 15)], 3)

    def over(p: Pix) -> None:
        kit.cork(p, 5, 2, 6, 4)
        kit.wax(p, 4, 0, 8, 3, 4)

    return Vessel((16, 48), rows, 8, over=over, seed=2)


def _normal() -> Vessel:
    """A slim flagon with a brass cap and a hanging cord tag."""
    rows = rows_from([(7, 5, 11), (24, 5, 11), (30, 1, 15), (57, 1, 15), (60, 1, 15)], 3)

    def over(p: Pix) -> None:
        kit.cork(p, 5, 4, 6, 4)
        kit.band(p, 4, 3, 8, 3)
        p.hline(5, 9, 6, rgb("#8a7f68"))               # cord tied round the neck
        p.vline(11, 10, 5, rgb("#8a7f68"))
        p.rect(11, 14, 3, 4, rgb("#d4cab0"))
        p.frame(11, 14, 3, 4, SHADOW)
        p.px(12, 16, WINE[2])

    return Vessel((16, 64), rows, 10, over=over, seed=3)


def _large() -> Vessel:
    """A glass demijohn in a wicker sleeve."""
    rows = rows_from([(7, 13, 19), (12, 13, 19), (20, 6, 26), (56, 6, 26), (61, 6, 26)], 3)
    cane, lit, shade = PALE_WOOD[2], PALE_WOOD[4], PALE_WOOD[1]

    def over(p: Pix) -> None:
        kit.cork(p, 12, 2, 8, 6)
        p.hline(12, 12, 8, rgb("#b3a88c"))             # hemp cord round the neck
        p.hline(12, 13, 8, rgb("#5d5444"))
        p.px(20, 13, rgb("#8a7f68"))
        p.px(21, 14, rgb("#8a7f68"))

    def front(p: Pix) -> None:
        for x in range(7, 25, 4):                       # upright canes with a lit left edge
            for y in range(24, 56):
                p.px(x, y, lit if (y // 2) % 2 else cane)
                p.px(x + 1, y, shade)
        for y in (24, 25, 38, 39):                      # woven bands
            for x in range(6, 26):
                p.px(x, y, cane if (x + y) % 2 else shade)
            p.hline(6, y, 1, SHADOW)
            p.hline(25, y, 1, SHADOW)
        for y in range(53, 62):                         # a woven foot
            x0, x1 = {61: (9, 23), 60: (7, 25)}.get(y, (6, 26))
            for x in range(x0, x1):
                p.px(x, y, (cane, shade, lit)[(x + y) % 3] if y < 60 else shade)
            p.px(x0, y, SHADOW)
            p.px(x1 - 1, y, SHADOW)
        p.hline(9, 61, 14, SHADOW)
        p.hline(7, 60, 2, SHADOW)
        p.hline(23, 60, 2, SHADOW)

    return Vessel((32, 64), rows, 12, over=over, front=front, seed=4)


# ---------------------------------------------------------------------------------------------- pitcher and vat


def _pitcher() -> Vessel:
    """A glass pitcher: a bellied body, a pewter rim with a pouring lip, and a turned wooden ear handle."""
    rows = rows_from([(14, 9, 42), (22, 8, 43), (32, 9, 42), (58, 12, 39), (59, 12, 39)], 2)
    for y, x1 in ((11, 47), (12, 47), (13, 46)):         # the lip pulls out to the right
        rows[y] = (9, x1) if y > 11 else (44, x1)
    rows[12], rows[13] = (9, 46), (9, 45)

    def under(p: Pix) -> None:
        for y in range(16, 49):                          # the ear: a four-pixel arc of turned wood
            t = (y - 16) / 32
            reach = round(8 * (1 - (2 * t - 1) ** 2) ** 0.5)
            x = 9 - reach
            p.px(x - 1, y, SHADOW)
            p.rect(x, y, 4, 1, WOOD[2])
            p.px(x, y, PALE_WOOD[3])
            p.px(x + 1, y, WOOD[3])
            p.px(x + 4, y, SHADOW)
        for y in (15, 49):
            p.hline(5, y, 6, SHADOW)
        for y in (16, 48):
            p.rect(6, y, 5, 1, WOOD[2])
            p.px(6, y, PALE_WOOD[3])

    def over(p: Pix) -> None:
        p.rect(9, 12, 34, 2, IRON[3])                    # pewter rim
        p.hline(9, 12, 34, IRON[4])
        p.hline(9, 14, 34, SHADOW)
        p.hline(9, 11, 34, SHADOW)
        for x in (13, 21, 29, 37):
            p.px(x, 12, BRASS[3])
        p.hline(44, 11, 3, SHADOW)
        p.hline(43, 12, 3, IRON[3])
        p.hline(43, 12, 1, IRON[4])
        p.rect(14, 56, 22, 1, IRON[2])                   # a pewter foot ring
        p.hline(14, 56, 22, IRON[3])

    return Vessel((48, 64), rows, 15, under=under, over=over, seed=5)


def _xl() -> Vessel:
    """An iron-bound glass vat with an oak lid and a rope handle."""
    rows = rows_from([(12, 4, 60), (62, 4, 60)], 0)
    rows[12] = (4, 60)

    def over(p: Pix) -> None:
        p.rect(14, 5, 36, 7, OAK[3])                    # lid of oak planks
        p.hline(14, 5, 36, OAK[4])
        p.hline(14, 7, 36, OAK[1])
        p.hline(14, 10, 36, OAK[1])
        for x in (20, 31, 42):
            p.px(x, 6, OAK[4])
        p.frame(14, 4, 36, 8, SHADOW)
        for x in range(26, 38):                         # a rope grip
            y = 1 if 28 <= x <= 35 else 2
            p.px(x, y, rgb("#b3a88c") if x % 2 else rgb("#8a7f68"))
        p.vline(26, 3, 2, rgb("#8a7f68"))
        p.vline(37, 3, 2, rgb("#8a7f68"))
        kit.strap(p, 4, 11, 56, 3, False)
        p.hline(3, 10, 58, SHADOW)
        p.hline(3, 14, 58, SHADOW)
        for x in (7, 56):
            p.px(x, 12, BRASS[4])

    def front(p: Pix) -> None:
        for x0 in (4, 56):                              # riveted corner posts
            kit.strap(p, x0, 13, 4, 49)
            for y in range(18, 60, 8):
                p.px(x0 + 1, y, BRASS[4])
                p.px(x0 + 2, y, BRASS[1])
            p.vline(x0 - 1 if x0 == 4 else x0 + 4, 13, 49, SHADOW)
        kit.strap(p, 4, 58, 56, 4, False)
        p.hline(4, 62, 56, SHADOW)
        for x in range(10, 56, 9):
            p.px(x, 59, BRASS[3])

    return Vessel((64, 64), rows, 15, over=over, front=front, seed=6)


# ---------------------------------------------------------------------------------------------- measures and pipettes


def _measure(size_ml: int) -> Vessel:
    """An apothecary's glass measure on a brass foot."""
    spec = {100: (1, 15, 1, 29, 3), 50: (2, 14, 3, 28, 5), 25: (3, 13, 5, 27, 7)}[size_ml]
    x0, x1, y0, y1, top = spec
    rows = rows_from([(y0, x0, x1), (y1 - 3, x0, x1)], 0)
    rows = {y: r for y, r in rows.items()}
    for y in range(y1 - 2, y1 + 1):
        rows[y] = (x0, x1)

    def under(p: Pix) -> None:
        pass

    def over(p: Pix) -> None:
        kit.band(p, x0 - 1, y0, (x1 - x0) + 2, 1, GLASS)       # the flared lip
        p.hline(x0 - 1, y1 - 2, (x1 - x0) + 2, SHADOW)
        for i, y in enumerate((y1 - 1, y1)):
            p.hline(x0 - 1, y, (x1 - x0) + 2, BRASS[3 - i])
        p.hline(x0 - 1, y1 - 1, (x1 - x0) + 2, BRASS[3])
        p.hline(x0 - 1, y1, (x1 - x0) + 2, BRASS[1])
        p.px(x0 - 1, y1 - 1, BRASS[4])
        p.hline(x0 - 2, y1 + 1, (x1 - x0) + 4, SHADOW)

    return Vessel((16, 32), rows, top, over=over, seed=10 + size_ml)


def _pipette(size_ml: int) -> Vessel:
    """A glass dropper with a leather bulb: 1 ml has a green wax collar, 5 ml a red one."""
    top = {1: 5, 5: 2}[size_ml]
    tip = {1: 26, 5: 29}[size_ml]
    rows: dict[int, tuple[int, int]] = {}

    def over(p: Pix) -> None:
        for y in range(top + 8, tip):                   # the glass tube: two dark walls and a lit core
            p.px(6, y, SHADOW)
            p.px(8, y, SHADOW)
            p.px(7, y, GLASS[3] if y % 5 else GLASS[4])
        p.px(7, tip, SHADOW)
        leather = LEATHER
        for dy, (a, b) in enumerate(((6, 9), (5, 10), (4, 11), (4, 11), (4, 11), (5, 10), (5, 10))):
            y = top + dy
            for x in range(a, b + 1 if b > a else b):
                p.px(x, y, leather[2])
            p.px(a, y, SHADOW)
            p.px(b, y, SHADOW)
            p.px(a + 1, y, leather[3])
            p.px(b - 1, y, leather[1])
        p.hline(6, top - 1, 4, SHADOW)
        p.hline(7, top, 2, leather[3])
        p.hline(5, top + 7, 6, SHADOW)
        collar = (MOSS, WINE)[size_ml == 5]
        p.rect(5, top + 7, 6, 1, collar[3])
        p.hline(5, top + 8, 6, SHADOW)
        p.px(5, top + 7, SHADOW)
        p.px(10, top + 7, SHADOW)
        p.px(6, top + 7, collar[3])

    return Vessel((16, 32), rows, top + 9, over=over, seed=20 + size_ml)


# ---------------------------------------------------------------------------------------------- the series

FLASKS: dict[str, Callable[[], Vessel]] = {
    "mini": _mini, "small": _small, "normal": _normal, "large": _large,
}
MEASURES: dict[str, Callable[[], Vessel]] = {
    "100ml": partial(_measure, 100), "50ml": partial(_measure, 50), "25ml": partial(_measure, 25),
}
PIPETTES: dict[str, Callable[[], Vessel]] = {"1ml": partial(_pipette, 1), "5ml": partial(_pipette, 5)}
COLOURS = ("blue", "dark", "red")


def _series(group: str, name: str, make: Callable[[], Vessel], ticks: bool, assets: dict[str, Callable[[], Image.Image]],
            skip: tuple[str, ...] = ()) -> None:
    vessel = make()
    assets[f"items~{group}@{name}.png"] = lambda v=vessel: kit.base(v)
    for level in LEVELS:
        for colour in COLOURS:
            assets[f"items~{group}@{name}_{colour}_{level}.png"] = lambda v=vessel, c=colour, n=level: kit.liquid(v, c, n)
        if f"{name}_hl_{level}" not in skip:
            assets[f"items~{group}@{name}_hl_{level}.png"] = lambda v=vessel, n=level, t=ticks: kit.highlight(v, n, t)


def _build() -> dict[str, Callable[[], Image.Image]]:
    assets: dict[str, Callable[[], Image.Image]] = {}
    for name, make in FLASKS.items():
        _series("water_container3", name, make, False, assets)
    for name, make in MEASURES.items():
        _series("water_container3", name, make, True, assets)
    _series("water_container4", "pitcher", _pitcher, False, assets)
    _series("water_container4", "xl", _xl, False, assets, skip=("xl_hl_100",))
    for name, make in PIPETTES.items():
        vessel = make()
        assets[f"items~water_container3@{name}.png"] = lambda v=vessel: kit.base(v)
        y0, y1 = (14, 24) if name == "1ml" else (11, 27)
        for colour in COLOURS:
            assets[f"items~water_container3@{name}_{colour}.png"] = lambda v=vessel, c=colour, a=y0, b=y1: kit.column(v, c, 7, a, b)
    return assets


_PARTS = _build()


def _put(canvas: Image.Image, group: str, name: str, colour: str | None, level: int | None, x: int, y: int) -> None:
    """Lays one vessel (base, liquid, highlight) on the illustration at 1x."""
    stem = f"items~{group}@{name}"
    canvas.alpha_composite(_PARTS[f"{stem}.png"](), (x, y))
    if colour and level:
        canvas.alpha_composite(_PARTS[f"{stem}_{colour}_{level}.png"](), (x, y))
        key = f"{stem}_hl_{level}.png"
        if key in _PARTS:
            canvas.alpha_composite(_PARTS[key](), (x, y))


def illustration() -> Image.Image:
    """The in-game picture of the whole family: every vessel in a row of fill levels, on a parchment-free transparent
    sheet, laid out like the game's own (measures on top, pipettes, bottles, pitchers, vats)."""
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    steps = (None, 10, 25, 50, 75, 100)
    colours = ("blue", "blue", "blue", "dark", "red", "blue")
    for i, n in enumerate(steps):
        x = 16 + 32 * i
        _put(canvas, "water_container3", "100ml", colours[i], n, x, 14)
        _put(canvas, "water_container3", "50ml", colours[i], n, 216 + 32 * i, 178)
        _put(canvas, "water_container3", "25ml", colours[i], n, 216 + 32 * i, 224)
        _put(canvas, "water_container3", "mini", colours[i], n, 216 + 32 * i, 268)
        _put(canvas, "water_container3", "normal", colours[i], n, x, 180)
        _put(canvas, "water_container3", "small", colours[i], n, x, 256)
        _put(canvas, "water_container4", "pitcher", colours[i], n, 16 + 64 * i, 322)
        _put(canvas, "water_container4", "xl", colours[i], n, 16 + 80 * i, 410)
    for i, name in enumerate(("1ml", "1ml", "5ml", "5ml")):
        colour = ("blue", "dark", "red", "blue")[i]
        x = 76 + 32 * i
        canvas.alpha_composite(_PARTS[f"items~water_container3@{name}.png"](), (x, 56))
        canvas.alpha_composite(_PARTS[f"items~water_container3@{name}_{colour}.png"](), (x, 56))
    canvas.alpha_composite(_PARTS["items~water_container3@5ml.png"](), (172, 100))
    canvas.alpha_composite(_PARTS["items~water_container3@5ml_red.png"](), (172, 100))
    big = Image.new("RGBA", (32, 64), (0, 0, 0, 0))
    _put(big, "water_container3", "large", "blue", 100, 0, 0)
    canvas.alpha_composite(big.resize((64, 128), Image.Resampling.NEAREST), (414, 150))
    return canvas


ASSETS: Mapping[str, Callable[[], Image.Image]] = {**_PARTS, "water_container2.512x512.png": illustration}
