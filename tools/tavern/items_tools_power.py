"""Tool-family items, part 1: the power things. In the tavern the batteries are banded vials with a level window, the circuit
chips are brass die-plates, the department modules are heraldic tablets, the booster is a chained strongbox."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial

from PIL import Image

from itemkit_tools import (AMETHYST, BOX, COPPER, SLATE, TEAL, LIGHT, ball, bitmap, corners, finish, glass, grain, hcyl, inset,
                           lamp, plank_box, r5, rivets, slab, sparkle, strap_h, strap_v, vcyl)
from palette import BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Pix, Ramp, mix, rgb

GREEN_LIT = rgb("#8fd068")


# ---------------------------------------------------------------------------------------------------- batteries

def _fill_color(pct: int) -> tuple:
    return EMBER if pct <= 20 else FLAME[3] if pct <= 60 else GREEN_LIT


def vial(name: str, body: Ramp, pct: int, tall: bool, seed: int) -> Image.Image:
    """A banded vial: brass cap and foot, a glass slit that shows the charge in segments (red low, amber, green full)."""
    x0, y0, x1, y1 = BOX[name]
    p = Pix(16, 32, seed=seed)
    x, w = x0 + 1, 10
    top, bot = y0 + 1, y1 - 2
    vcyl(p, x, top + 4, w, bot - top - 3, body)
    # cap: a small knob on a brass collar (the tall kinds also carry an iron terminal nub)
    if tall:
        p.rect(x + 3, top, 4, 2, IRON[2])
        p.hline(x + 3, top, 4, IRON[4])
        top += 2
    p.rect(x + 2, top, w - 4, 2, BRASS[2])
    p.hline(x + 2, top, w - 4, BRASS[4])
    slab(p, x, top + 2, w, 3, BRASS)
    p.px(x + 2, top + 3, BRASS[4])
    slab(p, x, bot - 2, w, 3, BRASS)
    p.hline(x + 1, bot + 1, w - 2, IRON[1])
    # the window
    wy0, wy1 = top + 7, bot - 3
    wh = wy1 - wy0 + 1
    p.rect(x + 2, wy0 - 1, 6, wh + 2, SHADOW)
    p.rect(x + 3, wy0, 4, wh, GLASS[1])
    p.vline(x + 3, wy0, wh, GLASS[2])
    n = wh // 3
    count = round(pct / 100 * n)
    col = _fill_color(pct)
    for i in range(count):
        yy = wy1 - i * 3 - 1
        p.hline(x + 3, yy, 4, col)
        p.px(x + 3, yy, mix(col, (255, 255, 230), 0.4))
        p.hline(x + 3, yy + 1, 4, mix(col, SHADOW, 0.45)) if yy + 1 <= wy1 else None
    if pct == 10:
        p.hline(x + 3, wy1, 4, EMBER)
    p.px(x + 6, wy0, GLASS[4])
    img = finish(p)
    return img.crop((0, 0, 15, 32)) if name == "battery_dis20" else img   # the game's sheet cell is one pixel narrower


def battery_hyp() -> Image.Image:
    """A caged amethyst phial, glowing violet."""
    p = Pix(16, 32, seed=7)
    x, w = 3, 10
    vcyl(p, x, 7, w, 20, AMETHYST)
    p.rect(x + 3, 3, 4, 2, IRON[2])
    p.hline(x + 3, 3, 4, IRON[4])
    p.rect(x + 2, 5, w - 4, 2, BRASS[2])
    slab(p, x, 7, w, 3, BRASS)
    slab(p, x, 24, w, 3, BRASS)
    p.rect(x + 3, 11, 4, 12, SHADOW)
    p.rect(x + 4, 12, 2, 10, AMETHYST[3])
    for yy in (13, 16, 19):
        p.hline(x + 4, yy, 2, AMETHYST[4])
    p.vline(x + 4, 12, 10, AMETHYST[4]) if False else None
    p.px(x + 5, 21, AMETHYST[2])
    for k in range(3):                      # a cage of brass wire over the glass
        p.px(x + 2, 12 + k * 4, BRASS[3])
        p.px(x + 7, 12 + k * 4, BRASS[1])
    return finish(p)


def battery_bar() -> Image.Image:
    """The little level bar: stacked amber bars."""
    p = Pix(4, 10, seed=3)
    for i in range(5):
        p.hline(0, i * 2, 4, FLAME[3] if i % 2 == 0 else FLAME[2])
        p.hline(0, i * 2 + 1, 4, FLAME[2])
        p.px(3, i * 2 + 1, FLAME[1])
        p.px(0, i * 2, FLAME[4])
    return p.im


LEVELS = (0, 10, 20, 40, 60, 80, 100)
COPPER_VIAL = COPPER
STEEL_BLUE = (rgb("#0f1d2a"), rgb("#1b3a54"), rgb("#2d5f82"), rgb("#4b88a8"), rgb("#86bcd0"))


def _batteries() -> dict[str, Callable[[], Image.Image]]:
    out: dict[str, Callable[[], Image.Image]] = {}
    for lv in LEVELS:
        out[f"items~items_tool@battery{lv}.png"] = partial(vial, f"battery{lv}", IRON, lv, False, lv)
        out[f"items~items_tool@battery_dis{lv}.png"] = partial(vial, f"battery_dis{lv}", COPPER, lv, True, lv + 1)
        out[f"items~items_tool@battery_ext{lv}.png"] = partial(vial, f"battery_ext{lv}", STEEL_BLUE, lv, True, lv + 2)
        out[f"items~items_tool2@sbattery{lv}.png"] = partial(vial, f"sbattery{lv}", AMETHYST, lv, False, lv + 3)
    return out


# ---------------------------------------------------------------------------------------------------- chips and modules

PIPS = {1: ((1, 1),), 2: ((0, 0), (2, 2)), 3: ((0, 0), (1, 1), (2, 2)), 4: ((0, 0), (2, 0), (0, 2), (2, 2)),
        5: ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)), 6: ((0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2))}
CROSSBOW = ("..#.#..", ".#.#.#.", "#.###.#", "..###..", "..#.#..", "..###..", "...#...")


def chip(n: int | None) -> Image.Image:
    """A die-plate of black iron in a brass frame; its pips (or a crossbow) say which print it makes. Pins are rivets."""
    p = Pix(16, 16, seed=5 + (n or 9))
    slab(p, 2, 2, 12, 12, BRASS)
    slab(p, 4, 4, 8, 8, IRON)
    for yy in (4, 7, 10):                   # teeth along the sides
        p.px(1, yy, BRASS[2])
        p.px(14, yy, BRASS[1])
    if n:
        for dx, dy in PIPS[n]:
            x, y = 5 + dx * 2 + (0 if n != 6 else 0), 5 + dy * 2
            p.px(x, y, BRASS[4])
            p.px(x + 1, y, BRASS[3])
            p.px(x, y + 1, BRASS[2])
            p.px(x + 1, y + 1, BRASS[1])
    else:
        bitmap(p, 4, 4, ("...#....", ".#####..", "#.###.#.", "..###...", "..#.#...", "..#.#...", "...#....", "........"),
               {"#": BRASS[4]})
    p.px(2, 2, BRASS[4])
    return finish(p)


EMBLEMS = {
    "cmd": ("#..#..#", "##.#.##", "#######", "#######", ".#####."),
    "eng": (".#.#.#.", "#######", ".##.##.", "##...##", ".##.##.", "#######", ".#.#.#."),
    "med": ("..###..", "..###..", "#######", "#######", "#######", "..###..", "..###.."),
    "sci": ("..###..", "...#...", "..###..", ".#####.", "#######", "#######"),
    "sec": ("#######", "#######", "#######", "#######", ".#####.", "..###..", "...#..."),
    "ser": ("#####..", "#####.#", "#####.#", "#####.#", "#####..", ".###..."),
    "sup": ("..###..", ".#.#.#.", ".#####.", "#######", "#######", "#######", ".#####."),
}
CLOTH: dict[str, Ramp] = {"cmd": NAVY, "eng": COPPER, "med": TEAL, "sci": AMETHYST, "sec": WINE, "ser": MOSS,
                          "sup": (rgb("#2a2a1a"), rgb("#4d4a2a"), rgb("#78703a"), rgb("#a09450"))}


def module(kind: str) -> Image.Image:
    """A department tablet: oak frame, brass corners, a cloth inlay in the department colour and its brass badge."""
    p = Pix(32, 16, seed=len(kind) + ord(kind[0]))
    x, y, w, h = 6, 2, 21, 12
    slab(p, x, y, w, h, OAK)
    cloth = r5(CLOTH[kind])
    p.rect(x + 2, y + 2, w - 4, h - 4, cloth[2])
    p.hline(x + 2, y + 2, w - 4, cloth[3])
    p.vline(x + 2, y + 2, h - 4, cloth[3])
    p.hline(x + 2, y + h - 3, w - 4, cloth[1])
    p.vline(x + w - 3, y + 2, h - 4, cloth[1])
    for i in range(3):                      # a woven edge: stitched dots
        p.px(x + 4 + i * 6, y + 2, cloth[4])
    rows = EMBLEMS[kind]
    ex, ey = x + 7, y + 2 + (8 - len(rows)) // 2 + 0
    ex = x + (w - 7) // 2
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                p.px(ex + i, ey + j, BRASS[4] if j + i < len(rows) - 1 else BRASS[3])
    rivets(p, ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)))
    return finish(p)


def _chips_modules() -> dict[str, Callable[[], Image.Image]]:
    out: dict[str, Callable[[], Image.Image]] = {f"items~items_tool@printer_chip{n}.png": partial(chip, n) for n in range(1, 7)}
    out["items~items_tool@printer_chip_pistol.png"] = partial(chip, None)
    for k in EMBLEMS:
        out[f"items~items_tool@{k}_module.png"] = partial(module, k)
    return out


# ---------------------------------------------------------------------------------------------------- recharger, block, converter

def recharger_base() -> Image.Image:
    """An oak rack with four iron-ringed sockets for vials."""
    p = Pix(64, 32, seed=11)
    slab(p, 1, 10, 62, 21, OAK)
    grain(p, 2, 11, 60, 19, OAK)
    strap_h(p, 1, 27, 62, 3, IRON)
    for i in range(4):
        cx = 3 + i * 15
        p.rect(cx, 12, 13, 14, SHADOW)
        p.rect(cx + 1, 13, 11, 12, rgb("#120b0e"))
        p.hline(cx + 1, 13, 11, OAK[1])
        p.ellipse(cx + 2, 21, 9, 5, IRON[2])
        p.ellipse(cx + 3, 22, 7, 3, SHADOW)
        p.hline(cx + 4, 21, 3, IRON[4])
        p.px(cx, 12, BRASS[3])
        p.px(cx + 12, 12, BRASS[1])
    for xx in (1, 61):
        strap_v(p, xx, 10, 21, 2, IRON, False)
    return finish(p)


def recharger_top() -> Image.Image:
    """The lid plank that sits on the rack: iron end caps and hinge pins."""
    p = Pix(64, 32, seed=12)
    slab(p, 1, 1, 62, 8, OAK)
    grain(p, 2, 2, 60, 6, OAK)
    p.hline(2, 2, 60, OAK[4])
    strap_v(p, 1, 1, 8, 4, IRON, False)
    strap_v(p, 59, 1, 8, 4, IRON, False)
    for x in (12, 28, 44):
        p.px(x, 5, BRASS[3])
        p.px(x + 1, 5, BRASS[1])
    return finish(p)


def powerblock(on: bool) -> Image.Image:
    """An iron-banded block with a four-bladed vane in a brass ring; lit, the vane spins in firelight."""
    p = Pix(32, 32, seed=21)
    x0, y0, x1, y1 = BOX["powerblock"]
    slab(p, 3, 3, 26, 27, IRON)
    corners(p, 3, 3, 26, 27, 1)
    p.rect(5, 5, 22, 23, IRON[1])
    # the ring and vane
    cx, cy = 16, 17
    p.ellipse(cx - 9, cy - 9, 19, 19, BRASS[2])
    p.ellipse(cx - 8, cy - 8, 17, 17, BRASS[1])
    p.ellipse(cx - 7, cy - 7, 15, 15, FLAME[1] if on else SHADOW)
    if on:
        p.glow(cx, cy, 7, FLAME[3], 1.2)
    for k in range(-6, 7):                  # the vane: two crossing blades
        for t in (0, 1):
            p.px(cx + k, cy + k + t - 0, IRON[3] if k < 0 else IRON[2])
            p.px(cx + k, cy - k + t, IRON[3] if k < 0 else IRON[2])
    p.rect(cx - 1, cy - 1, 3, 3, BRASS[3])
    p.px(cx - 1, cy - 1, BRASS[4])
    for i in range(7):                      # the ring catches the light on its upper left
        p.px(cx - 9 + 2 + i // 2 * 0 + (i if i < 3 else 3), cy - 8 + (3 - min(i, 3)), BRASS[4]) if i < 3 else None
    rivets(p, ((5, 5), (26, 5), (5, 27), (26, 27)))
    # a lamp: dark or glowing
    lamp(p, 22, 6, 4, 3, on)
    if on:
        p.px(24, 10, FLAME[4])
        sparkle(p, 9, 7, FLAME[3])
    return finish(p)


def converter(on: bool) -> Image.Image:
    """A brass-capped jar with a rod on top; lit, the jar holds a warm glow."""
    p = Pix(16, 32, seed=31)
    ball(p, 6, 3, 4, BRASS)
    p.rect(7, 7, 2, 3, IRON[3])
    slab(p, 3, 9, 10, 3, BRASS)
    vcyl(p, 3, 12, 10, 14, GLASS)
    p.rect(4, 12, 8, 1, SHADOW)
    if on:
        for yy in range(13, 25):
            p.hline(4, yy, 8, FLAME[2] if yy % 4 else FLAME[3])
        p.rect(5, 14, 3, 2, FLAME[4])
        p.vline(10, 13, 11, FLAME[1])
    else:
        p.rect(5, 13, 2, 8, GLASS[3])
        p.px(5, 13, GLASS[4])
    for yy in (15, 20):
        p.hline(3, yy + 3, 10, BRASS[1])
    slab(p, 3, 25, 10, 3, BRASS)
    p.hline(4, 28, 8, IRON[1])
    return finish(p)


# ---------------------------------------------------------------------------------------------------- boosters

def booster(variant: str) -> Image.Image:
    """A chained strongbox: lacquered wine wood (violet when advanced) in iron, a brass label with a lamp, two chains to pincers."""
    adv = variant != "normal"
    body: Ramp = AMETHYST if adv else WINE
    p = Pix(48, 32, seed=41)
    x, y, w, h = 2, 5, 44, 17
    plank_box(p, x, y, w, h, body, vertical=False, grained=False)
    corners(p, x, y, w, h, 1)
    for xx in (x, x + w - 4):
        strap_v(p, xx, y, h, 4, IRON)
    p.rect(14, 2, 4, 3, IRON[3])               # two terminals on top
    p.rect(30, 2, 4, 3, IRON[2])
    p.hline(14, 2, 4, IRON[4])
    p.hline(30, 2, 4, IRON[4])
    p.px(15, 3, BRASS[3])
    p.px(31, 3, BRASS[2])
    # label plate
    slab(p, 14, 9, 20, 9, BRASS)
    p.rect(15, 10, 11, 7, PARCHMENT[3])
    for yy in (11, 13, 15):
        p.hline(16, yy, 8 if yy != 13 else 6, INK2)
    lampc = {"normal": None, "adv": None, "charging": "amber", "ready": "green"}.get(variant)
    p.rect(28, 11, 4, 5, SHADOW)
    if lampc == "amber":
        p.rect(29, 12, 2, 3, FLAME[3])
        p.px(29, 12, FLAME[4])
    elif lampc == "green":
        p.rect(29, 12, 2, 3, GREEN_LIT)
        p.px(29, 12, rgb("#d4f4a8"))
    else:
        p.rect(29, 12, 2, 3, IRON[2])
    # two chains and pincers
    for sx, ex, dark in ((8, 3, False), (12, 16, True)):
        pts = [(sx, 22), (sx + (ex - sx) // 3, 25), (ex, 28)]
        c1, c2 = (IRON[3], IRON[1]) if not dark else (IRON[2], IRON[0])
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(abs(bx - ax), abs(by - ay))
            for i in range(n + 1):
                px_ = ax + (bx - ax) * i // max(1, n)
                py_ = ay + (by - ay) * i // max(1, n)
                p.px(px_, py_, c1 if i % 2 else c2)
        p.rect(ex - 1, 28, 3, 2, IRON[3])
        p.px(ex - 1, 29, IRON[1])
        p.px(ex + 1, 29, IRON[1])
        p.px(ex, 28, BRASS[3])
    if variant == "charging":
        for x_, y_ in ((5, 27), (18, 26), (22, 24), (40, 24)):
            sparkle(p, x_, y_, FLAME[3])
        p.glow(24, 14, 14, FLAME[3], 0.35)
        p.hline(36, 18, 8, FLAME[3])
    if variant == "ready":
        p.glow(30, 13, 9, GREEN_LIT, 0.5)
    return finish(p)


INK2 = rgb("#4a3a2a")


def hyper_pack() -> Image.Image:
    """A leather pack with amethyst panels, a brass buckle, an instrument window and a coil of cord."""
    p = Pix(48, 48, seed=51)
    plank_box(p, 10, 4, 28, 38, LEATHER, vertical=False)
    corners(p, 10, 4, 28, 38, 2)
    slab(p, 13, 7, 22, 12, AMETHYST)
    slab(p, 13, 22, 22, 17, AMETHYST)
    # flap and buckle
    p.hline(11, 20, 26, LEATHER[0])
    slab(p, 20, 17, 8, 7, BRASS)
    p.rect(22, 19, 4, 3, SHADOW)
    p.px(23, 20, BRASS[3])
    # an instrument: round brass gauge
    ball(p, 19, 9, 10, BRASS)
    p.ellipse(21, 11, 6, 6, PARCHMENT[3])
    p.line(24, 14, 26, 12, EMBER)
    p.px(23, 14, SHADOW)
    # amber lamps
    for xx, c in ((15, FLAME[3]), (32, GREEN_LIT)):
        p.rect(xx, 28, 2, 3, c)
    # straps
    for xx in (8, 39):
        strap_v(p, xx, 10, 28, 2, LEATHER, False)
    rivets(p, ((15, 9), (32, 9), (15, 36), (32, 36)))
    # cord coil, hanging bottom right
    for k in range(4):
        p.ellipse(34 + k % 2, 38 + k, 10 - k, 7 - k // 2, COPPER[2] if k % 2 else COPPER[3])
    p.ellipse(37, 41, 5, 3, SHADOW)
    p.px(36, 39, COPPER[4])
    p.line(40, 40, 44, 45, COPPER[3])
    return finish(p)


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    **_batteries(),
    "items~items_tool2@battery_hyp.png": battery_hyp,
    "items~items_tool@battery_bar.png": battery_bar,
    **_chips_modules(),
    "items~items_tool@recharger_base.png": recharger_base,
    "items~items_tool@recharger_top.png": recharger_top,
    "items~items_tool@recharger_g.png": lambda: _dots(rgb("#8fd068"), rgb("#4a8a3a")),
    "items~items_tool@recharger_o.png": lambda: _dots(FLAME[3], FLAME[1]),
    "items~items_tool@powerblock.png": partial(powerblock, False),
    "items~items_tool@powerblock_on.png": partial(powerblock, True),
    "items~items_tool2@current_converter.png": partial(converter, True),
    "items~items_tool2@current_converter_off.png": partial(converter, False),
    "items~items_tool@turbo_booster.png": partial(booster, "normal"),
    "items~items_tool@turbo_booster_adv.png": partial(booster, "adv"),
    "items~items_tool@turbo_booster_adv_charging.png": partial(booster, "charging"),
    "items~items_tool@turbo_booster_adv_ready.png": partial(booster, "ready"),
    "items~items_tool2@turbo_booster_hypertech.png": hyper_pack,
}


def _dots(a, b) -> Image.Image:
    """The 2x1 indicator light of the recharger."""
    p = Pix(3, 3)
    p.px(0, 0, a)
    p.px(1, 0, b)
    return p.im
