"""The in-play interface of the tavern: ledgers and parchment sheets, wooden plaques and brass tags, tile buttons, bubbles,
scroll bars, small pictograms (catalog group `ui/in-game`).

The game's screens are grey-and-cream tablets with cyan or orange trim; here the tablets are lecterns (a wooden board with
brass corners and a clasp holding a parchment sheet), paper is parchment, buttons are wooden plaques with a brass line,
and icon buttons are small wooden tiles with a brass rim and an inked glyph. A few building blocks make all of them:

* `sheet`   parchment of any size, torn or ruled, with optional columns of lines of "writing";
* `lectern` the tablet: board, brass corners, clasp, and a sheet inside;
* `plaque`  a button of any size in the four states normal, hover, pressed, disabled (one shape, only tone changes);
* `tile`    a square icon button, same four states, carrying a glyph from `ingame_icons`;
* `bubble`, `strip`, `tab`, `notched`, `slab`, `recess`, `board` for the nine-slice frames, bars and panels.

Pictures that the game tints at run time (pure white or flat grey masks) stay white or grey in shape only.
Left undrawn on purpose: see SKIPPED.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Callable, Mapping
from functools import partial
from pathlib import Path
from typing import Final

from PIL import Image

import font
import ingame_icons as ic
from materials import planks
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, STONE, WINE, WOOD
from pix import Color, Pix, Ramp, mix

CATALOG: Final = Path(__file__).resolve().parents[2] / "catalog.tsv"
PLUM: Final[Ramp] = ((38, 20, 44), (66, 36, 74), (98, 56, 108), (132, 84, 140), (168, 118, 170))
WHITE: Final[Color] = (255, 255, 255)
STATES: Final = ("normal", "hover", "pressed", "disabled")

SKIPPED: Final = (
    "sample (a character portrait), scavFemale, scavMale, special (character sprite sheets), scratch, scratch_back, "
    "exghange_logo, guide_logo (the game's own logos), bubble_sheet2, water_container2 (atlases of game items), "
    "calendar_top-Sheet, connector, lines, muzzleflash2, shotgun_shadow, shotgun_shadow_only (no readable layout)"
)

# ---------------------------------------------------------------------------------------------- catalog helpers


def _catalog() -> Mapping[str, tuple[int, int]]:
    """File name to size of every `ui/in-game` picture."""
    with CATALOG.open(encoding="utf-8", newline="") as f:
        return {r["file"]: (int(r["width"]), int(r["height"])) for r in csv.DictReader(f, delimiter="\t")
                if r["category"] == "ui" and r["group"] == "in-game"}


FILES: Final = _catalog()
ASSETS: dict[str, Callable[[], Image.Image]] = {}


def find(stem: str) -> str:
    """The file name for `stem`, or `stem@WxH` when two files share a stem."""
    want = None
    if "@" in stem:
        stem, want = stem.split("@")
    hits = [f for f in FILES if re.fullmatch(re.escape(stem) + r"\.(\d+)x(\d+)\.png", f) and (want is None or f"{FILES[f][0]}x{FILES[f][1]}" == want)]
    if len(hits) != 1:
        raise KeyError(f"{stem}: {hits}")
    return hits[0]


def reg(fn: Callable[..., Image.Image], *stems: str, **kw: object) -> None:
    """Registers `fn(w, h, seed, **kw)` for each stem; the picture's size and its seed come from the file name."""
    for stem in stems:
        name = find(stem)
        w, h = FILES[name]
        ASSETS[name] = partial(fn, w, h, sum(map(ord, name)), **kw)


# ---------------------------------------------------------------------------------------------- paper


def edge_wear(p: Pix, x: int, y: int, w: int, h: int, c: Color, depth: int = 4, density: float = 0.55) -> None:
    """Dithered darkening that thins out over `depth` pixels from every edge of a rectangle (handled, stained paper)."""
    for k in range(depth):
        d = density * (1 - k / depth)
        p.dither(x + k, y + k, w - 2 * k, 1, c, d)
        p.dither(x + k, y + h - 1 - k, w - 2 * k, 1, c, d)
        p.dither(x + k, y + k + 1, 1, h - 2 * k - 2, c, d)
        p.dither(x + w - 1 - k, y + k + 1, 1, h - 2 * k - 2, c, d)


def fake_text(p: Pix, x: int, y: int, w: int, h: int, c: Color, step: int = 4, gap: int = 4) -> None:
    """Lines of unreadable writing: short ink dashes (words) along rows `step` apart, last words short."""
    rng = p.rng
    for yy in range(y, y + h - 1, step):
        xx = x
        while xx < x + w - 3:
            n = min(rng.randrange(3, 11), x + w - xx)
            if rng.random() < 0.08 and xx > x:
                break
            p.hline(xx, yy, n, c)
            xx += n + gap // 2 + 1


def sheet(w: int, h: int, seed: int, tone: Ramp = PARCHMENT, torn: str = "", rules: int = 0, text: str = "", grid: int = 0,
          rim: bool = True, seal: bool = False) -> Image.Image:
    """A sheet of parchment: fibre, stains toward the rim, a lit upper-left edge; `torn` names the sides ("lrtb") with
    ragged edges, `rules` is the line spacing of ruled paper, `text` is "lines" or "columns" of unreadable writing,
    `grid` the cell size of a ruled grid, `seal` a wax seal in the upper left."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, tone[3])
    p.speckle(0, 0, w, h, (tone[2], tone[4]), 0.012)
    p.dither(0, 0, w, h, tone[2], 0.06)
    edge_wear(p, 0, 0, w, h, tone[1], depth=max(2, min(6, min(w, h) // 8)))
    if rules:
        for y in range(rules + 8, h - 6, rules):
            p.dither(5, y, w - 10, 1, tone[1], 0.7)
    if grid:
        for y in range(grid, h - 4, grid):
            p.dither(5, y, w - 10, 1, tone[1], 0.5)
        for x in range(grid, w - 4, grid):
            p.dither(x, 5, 1, h - 10, tone[1], 0.5)
    ink = mix(tone[0], SHADOW, 0.4)
    if text == "lines":
        fake_text(p, 8, 10, w - 16, h - 20, mix(tone[1], ink, 0.5), step=6)
    elif text == "columns":
        cols = 3
        cw = (w - 20 - (cols - 1) * 6) // cols
        p.rect(8, 8, w - 16, 14, mix(tone[1], ink, 0.5))        # masthead
        for i in range(cols):
            fake_text(p, 10 + i * (cw + 6), 30, cw, h - 42, mix(tone[1], ink, 0.45))
    if seal:
        p.ellipse(7, 7, 12, 12, WINE[0])
        p.ellipse(8, 8, 10, 10, WINE[2])
        p.ellipse(10, 10, 6, 6, WINE[3])
        p.px(9, 9, WINE[4])
    if rim:
        p.hline(0, 0, w, tone[4])
        p.vline(0, 0, h, tone[4])
        p.hline(0, h - 1, w, tone[1])
        p.vline(w - 1, 0, h, tone[1])
    for side in torn:
        length = h if side in "lr" else w
        run = 0
        while run < length:
            n = p.rng.randrange(3, 9)
            depth = p.rng.randrange(1, 4)
            for i in range(run, min(length, run + n)):
                for d in range(depth):
                    if side == "l":
                        p.px(d, i, (0, 0, 0, 0))
                    elif side == "r":
                        p.px(w - 1 - d, i, (0, 0, 0, 0))
                    elif side == "t":
                        p.px(i, d, (0, 0, 0, 0))
                    else:
                        p.px(i, h - 1 - d, (0, 0, 0, 0))
            run += n
    if torn or rim:
        p.outline(SHADOW, inside=True)
    return p.im


# ---------------------------------------------------------------------------------------------- boards and panels


def beveled(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, outline: bool = True) -> None:
    """The rim of a wooden board: an outline in SHADOW, a lit upper left, a shaded lower right."""
    if outline:
        p.frame(x, y, w, h, SHADOW)
        x, y, w, h = x + 1, y + 1, w - 2, h - 2
    p.hline(x, y, w, ramp[4])
    p.vline(x, y, h, ramp[4])
    p.hline(x, y + h - 1, w, ramp[0])
    p.vline(x + w - 1, y, h, ramp[0])


def rivet(p: Pix, x: int, y: int) -> None:
    """A brass rivet head, lit from the upper left."""
    p.px(x, y, BRASS[4])
    p.px(x + 1, y, BRASS[2])
    p.px(x, y + 1, BRASS[2])
    p.px(x + 1, y + 1, BRASS[0])


def board(w: int, h: int, seed: int, ramp: Ramp = WOOD, plank: int = 14, rivets: bool = True, trim: Color | None = None) -> Image.Image:
    """A framed panel of upright planks (dialogs, side panels): rim, corner rivets and an optional inner trim line."""
    p = Pix(w, h, seed=seed)
    planks(p, 0, 0, w, h, ramp, plank=plank, vertical=True, nails=False)
    beveled(p, 0, 0, w, h, ramp)
    if trim:
        p.frame(4, 4, w - 8, h - 8, trim)
    if rivets and min(w, h) >= 48:
        for x, y in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
            rivet(p, x, y)
    return p.im


def slab(w: int, h: int, seed: int, edge: int = 2, ramp: Ramp = STONE) -> Image.Image:
    """A slate panel with a chiselled rim of `edge` pixels (the neutral grey frames the game tints)."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, ramp[2])
    p.speckle(0, 0, w, h, (ramp[1], ramp[3]), 0.04)
    for k in range(edge):
        if k == 0:
            p.frame(0, 0, w, h, SHADOW)
        else:
            beveled(p, k, k, w - 2 * k, h - 2 * k, ramp, outline=False)
    return p.im


def recess(w: int, h: int, seed: int, ramp: Ramp = OAK, lip: int = 1) -> Image.Image:
    """A sunk field: dark with soot-dither, a deep shade along the top and left, a lit lip below and right."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, ramp[1])
    p.speckle(0, 0, w, h, (ramp[0], ramp[2]), 0.03)
    p.dither(0, 0, w, min(h, 8), SHADOW, 0.4)
    for k in range(min(lip, h)):
        p.hline(0, h - 1 - k, w, ramp[3])
    return p.im


def strip(w: int, h: int, seed: int, ramp: Ramp = LINEN, cut: int = 0, white: bool = False, lit_top: bool = True) -> Image.Image:
    """A flat label bar (list row, section heading): one tone, a lit top edge, a dark foot, optional cut top-left corner.
    With `white` it is the flat white mask the game tints."""
    p = Pix(w, h, seed=seed)
    if white:
        p.rect(0, 0, w, h, WHITE)
    else:
        p.rect(0, 0, w, h, ramp[2])
        if lit_top:
            p.hline(0, 0, w, ramp[4])
        p.hline(0, h - 1, w, ramp[0])
        p.dither(0, 1, w, max(1, h // 3), ramp[3], 0.4)
        p.speckle(0, 0, w, h, (ramp[1], ramp[3]), 0.03)
    for i in range(cut):
        p.rect(0, i, cut - i, 1, (0, 0, 0, 0))
        if not white and cut - i < w:
            p.px(cut - i, i, SHADOW)
    return p.im


def tab(w: int, h: int, seed: int, ramp: Ramp = WOOD, left: int = 0, right: int = 0, white: bool = False, trim: bool = True) -> Image.Image:
    """A tab or ribbon (progress segment, screen tab): a plank with slanted ends `left`/`right` pixels wide and a brass line;
    `white` gives the flat white mask of the same shape."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, WHITE if white else ramp[2])
    if not white:
        p.hline(0, 0, w, ramp[4])
        p.hline(0, h - 1, w, ramp[0])
        p.dither(0, 1, w, h // 2, ramp[3], 0.35)
        if trim and h >= 10:
            p.hline(left, h // 2 + 1, w - left - right, BRASS[2])
            p.hline(left, h // 2, w - left - right, BRASS[3])
    for i in range(h):
        if left:
            cut = max(0, left * (h - 1 - i) // max(1, h - 1))
            p.rect(0, i, cut, 1, (0, 0, 0, 0))
            if not white:
                p.px(cut, i, SHADOW)
        if right:
            cut = max(0, right * (h - 1 - i) // max(1, h - 1))
            p.rect(w - cut, i, cut, 1, (0, 0, 0, 0))
            if not white:
                p.px(w - cut - 1, i, SHADOW)
    return p.im


def notched(w: int, h: int, seed: int, fill: Color | None, ring: Color | None, notch: int = 2, rim: int = 2) -> Image.Image:
    """A square with its corners cut off (nine-slice plates and card outlines): `fill` inside, a `ring` of `rim` pixels."""
    p = Pix(w, h, seed=seed)
    body = ring if ring is not None else fill
    assert body is not None
    p.rect(0, 0, w, h, body)
    if ring is not None and fill is not None:
        p.rect(rim, rim, w - 2 * rim, h - 2 * rim, fill)
    for cx, cy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        for i in range(notch):
            for j in range(notch - i):
                p.px(cx + (j if cx == 0 else -j), cy + (i if cy == 0 else -i), (0, 0, 0, 0))
    return p.im


def rounded(w: int, h: int, seed: int, r: int, c: Color = WHITE) -> Image.Image:
    """A flat rounded rectangle of radius `r` (masks and tags the game tints)."""
    p = Pix(w, h, seed=seed)
    p.draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=c)
    return p.im


# ---------------------------------------------------------------------------------------------- lecterns


def lectern(w: int, h: int, seed: int, left: int = 8, right: int = 22, notch: bool = True, tab_label: bool = False, bell: bool = False) -> Image.Image:
    """The tablet as a lectern board: oak planks with brass corner caps, a brass clasp down the right edge (`right`
    pixels wide), and a parchment sheet inset with an inked rule and, if `notch`, a stepped notch in the top rule.
    `bell` fits a hand bell into a wide left margin (the telephone)."""
    p = Pix(w, h, seed=seed)
    planks(p, 0, 0, w, h, WOOD, plank=16, vertical=True, nails=False)
    beveled(p, 0, 0, w, h, WOOD)
    top = 9
    sx, sy, sw, sh = left, top, w - left - right, h - top - 11
    inner = sheet(sw, sh, seed + 1, rim=False)
    p.paste(inner, sx, sy)
    p.hline(sx, sy, sw, SHADOW)                                   # the frame throws its shade onto the sheet
    p.dither(sx, sy + 1, sw, 3, SHADOW, 0.45)
    p.dither(sx + 1, sy + 1, 3, sh - 1, SHADOW, 0.35)
    p.frame(sx - 1, sy - 1, sw + 2, sh + 2, SHADOW)
    ink = PARCHMENT[1]
    rx0, rx1, ry0, ry1 = sx + 7, sx + sw - 8, sy + 7, sy + sh - 8
    if notch:
        mid = (rx0 + rx1) // 2
        p.hline(rx0, ry0, mid - 22 - rx0, ink)
        p.hline(mid - 22, ry0 + 4, 14, ink)
        p.vline(mid - 22, ry0, 5, ink)
        p.vline(mid - 8, ry0, 5, ink)
        p.hline(mid - 8, ry0, rx1 - mid + 8, ink)
    else:
        p.hline(rx0, ry0, rx1 - rx0, ink)
    p.hline(rx0, ry1, rx1 - rx0, ink)
    p.vline(rx0, ry0, ry1 - ry0, ink)
    p.vline(rx1, ry0, ry1 - ry0, ink)
    if tab_label:
        p.rect(rx1 - 40, ry0 + 8, 40, 9, FLAME[1])
        p.hline(rx1 - 40, ry0 + 8, 40, FLAME[2])
    for k in range(4):                                            # brass cap at each corner of the board
        x = 2 if k % 2 == 0 else w - 12
        y = 2 if k < 2 else h - 12
        p.rect(x, y, 10, 10, SHADOW)
        p.rect(x + 1, y + 1, 8, 8, BRASS[2])
        p.hline(x + 1, y + 1, 8, BRASS[4])
        p.vline(x + 1, y + 1, 8, BRASS[3])
        p.hline(x + 1, y + 8, 8, BRASS[0])
        rivet(p, x + 4, y + 4)
    cx = w - right + 4                                            # the clasp: a strap with a ring at mid-height
    cw = right - 8
    if cw >= 6:
        p.rect(cx - 1, 12, cw + 2, h - 24, SHADOW)
        p.rect(cx, 13, cw, h - 26, IRON[2])
        p.vline(cx, 13, h - 26, IRON[4])
        p.vline(cx + cw - 1, 13, h - 26, IRON[0])
        for y in (18, h - 21):
            rivet(p, cx + cw // 2 - 1, y)
        my = h // 2
        p.ellipse(cx + 1, my - 6, cw - 2, 12, SHADOW)
        p.ellipse(cx + 2, my - 5, cw - 4, 10, BRASS[3])
        p.ellipse(cx + 4, my - 3, max(1, cw - 8), 6, IRON[1])
    if bell:
        bx, by = 18, h // 2 - 40
        p.rect(bx - 2, by - 2, 48, 90, SHADOW)
        p.rect(bx - 1, by - 1, 46, 88, WOOD[1])
        p.poly([(bx + 22, by + 8), (bx + 36, by + 54), (bx + 8, by + 54)], BRASS[2])
        p.poly([(bx + 22, by + 8), (bx + 14, by + 54), (bx + 8, by + 54)], BRASS[3])
        p.rect(bx + 4, by + 52, 36, 6, BRASS[1])
        p.ellipse(bx + 18, by + 62, 8, 8, IRON[2])
        p.rect(bx + 19, by + 2, 6, 6, BRASS[4])
    return p.im


def spine(w: int, h: int, seed: int) -> Image.Image:
    """The narrow oak spine of a bargain ledger: a brass-bound strip with a catch."""
    p = Pix(w, h, seed=seed)
    planks(p, 0, 0, w, h, OAK, plank=w, vertical=True, nails=False)
    beveled(p, 0, 0, w, h, OAK)
    for y in (6, h - 10):
        p.rect(3, y, w - 6, 4, BRASS[2])
        p.hline(3, y, w - 6, BRASS[4])
    p.ellipse(w // 2 - 3, h // 2 - 4, 7, 8, BRASS[3])
    p.rect(w // 2 - 1, h // 2 - 1, 3, 3, IRON[1])
    return p.im


# ---------------------------------------------------------------------------------------------- buttons


def plaque(w: int, h: int, seed: int, state: str = "normal", ramp: Ramp = WOOD, trim: Ramp | None = BRASS, cut: int = 1) -> Image.Image:
    """A button plaque: SHADOW rim, a plank body with a lit top and a shaded foot, an inset brass line, corners cut by
    `cut`. The four states are one shape: hover lifts the tone and warms the top, pressed sinks it with the bevel
    reversed, disabled greys it and dithers it with soot."""
    p = Pix(w, h, seed=seed)
    big = h >= 40
    t = 2 if big else 1
    idx = {"normal": 2, "hover": 3, "pressed": 1, "disabled": 2}[state]
    body, lit, dark = ramp[idx], ramp[min(4, idx + 1)], ramp[max(0, idx - 1)]
    if state == "disabled":
        body, lit, dark = (mix(c, (84, 76, 74), 0.6) for c in (body, lit, dark))
    p.rect(0, 0, w, h, SHADOW)
    p.rect(t, t, w - 2 * t, h - 2 * t, body)
    p.gradient(t, t, w - 2 * t, h - 2 * t, lit if state != "pressed" else dark, dark if state != "pressed" else body, steps=max(2, min(5, h // 5)))
    top, bottom = (dark, lit) if state == "pressed" else (lit, dark)
    p.rect(t, t, w - 2 * t, t, top)
    p.rect(t, t, t, h - 2 * t, top)
    p.rect(t, h - 2 * t, w - 2 * t, t, bottom)
    p.rect(w - 2 * t, t, t, h - 2 * t, bottom)
    if state == "hover":
        p.rect(t, t, w - 2 * t, t, mix(lit, FLAME[3], 0.45))
    if trim is not None and min(w, h) >= 12:
        c = {"normal": trim[2], "hover": trim[4], "pressed": trim[1], "disabled": IRON[2]}[state]
        p.frame(3 * t, 3 * t, w - 6 * t, h - 6 * t, c)
    if state == "disabled":
        p.dither(0, 0, w, h, SHADOW, 0.12)
    for cx, cy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        for i in range(cut):
            for j in range(cut - i):
                p.px(cx + (j if cx == 0 else -j), cy + (i if cy == 0 else -i), (0, 0, 0, 0))
    return p.im


def tile(w: int, h: int, seed: int, state: str = "normal", glyph: str = "none", body: Ramp = IRON, frame: Ramp = BRASS,
         ink: Ramp = PARCHMENT) -> Image.Image:
    """A square icon button: a dark tile with a brass rim and a glyph in `ink`; one shape in four states (hover brightens
    rim and glyph, pressed darkens and shifts the glyph down-right, disabled greys all)."""
    p = Pix(w, h, seed=seed)
    k = {"normal": 2, "hover": 3, "pressed": 1, "disabled": 0}[state]
    rim = frame[k] if state != "disabled" else IRON[2]
    face_c = body[{"normal": 1, "hover": 2, "pressed": 0, "disabled": 1}[state]]
    gc = ink[3] if state == "normal" else ink[4] if state == "hover" else ink[1] if state == "pressed" else mix(ink[1], IRON[2], 0.6)
    p.rect(0, 0, w, h, SHADOW)
    t = 2 if min(w, h) >= 24 else 1
    p.rect(t, t, w - 2 * t, h - 2 * t, rim)
    p.rect(2 * t, 2 * t, w - 4 * t, h - 4 * t, face_c)
    p.hline(2 * t, 2 * t, w - 4 * t, SHADOW)
    if state != "pressed":
        p.hline(t, t, w - 2 * t, mix(rim, WHITE, 0.25))
    off = 1 if state == "pressed" else 0
    gx, gy, gw, gh = 2 * t + 2 + off, 2 * t + 2 + off, w - 4 * t - 4, h - 4 * t - 4
    draw_glyph(p, glyph, gx, gy, gw, gh, gc, max(2, min(w, h) // 8))
    if state == "disabled":
        p.dither(0, 0, w, h, SHADOW, 0.12)
    return p.im


def draw_glyph(p: Pix, name: str, x: int, y: int, w: int, h: int, c: Color, thick: int) -> None:
    """Paints the glyph `name` into a box (see `ingame_icons`)."""
    if name in ("next", "prev"):
        ic.chevron(p, x + w // 4, y, w // 2, h, c, "r" if name == "next" else "l", thick)
    elif name == "cross":
        s = min(w, h)
        ic.cross(p, x + (w - s) // 2, y + (h - s) // 2, s, c, thick)
    elif name == "undo":
        ic.undo(p, x, y, min(w, h), c)
    elif name == "down":
        ic.chevron(p, x, y + h // 4, w, h // 2, c, "d", thick)
    elif name == "arrow_down":
        p.rect(x + w // 2 - thick // 2 - 1, y, thick + 2, h // 2, c)
        p.poly([(x, y + h // 2 - 1), (x + w - 1, y + h // 2 - 1), (x + w // 2, y + h - 1)], c)
    elif name == "bubble":
        ic.bubble_glyph(p, x, y, w, h, c)
    elif name == "zoom":
        p.frame(x, y + h // 3, w * 2 // 3, h * 2 // 3, c)
        p.frame(x + w // 3, y, w * 2 // 3, h * 2 // 3, c)
    elif name == "helm":
        p.ellipse(x + 1, y, w - 2, h - 2, c)
        p.rect(x + 1, y + h // 2, w - 2, h // 2 - 1, c)
        p.rect(x + w // 2 - 1, y + h // 2, 2, h // 2 - 1, SHADOW)
        p.rect(x + 2, y + h // 2 - 1, w - 4, 2, SHADOW)
    elif name == "plain":
        pass


def tile_strip(w: int, h: int, seed: int, glyph: str, ink: Ramp = PARCHMENT, body: Ramp = IRON) -> Image.Image:
    """A row of 16-pixel tiles, one per state (normal, hover, pressed), as in the game's three-frame buttons."""
    p = Pix(w, h, seed=seed)
    for i, state in enumerate(STATES[: w // h]):
        p.paste(tile(h, h, seed + i, state, glyph, body=body, ink=ink), i * h, 0)
    return p.im


def square_frames(w: int, h: int, seed: int) -> Image.Image:
    """Four hollow square sockets in a row (14 pixels each), lit more and more: the glyph-button back plates."""
    p = Pix(w, h, seed=seed)
    for i, k in enumerate((1, 3, 2, 0)):
        x = i * 14
        p.rect(x + 1, 1, 12, 13, SHADOW)
        p.rect(x + 2, 2, 10, 11, BRASS[k])
        p.rect(x + 4, 4, 6, 7, IRON[1])
    return p.im


def paper_arrow(w: int, h: int, seed: int, glyph: str, state: int) -> Image.Image:
    """A loose chevron or X in ink on nothing, in four tones (state 0..3: pale, bright, dark, dim); it is the glyph the
    game lays on paper sheets, so it carries a SHADOW rim to stay readable on parchment."""
    p = Pix(w, h, seed=seed)
    tone = (PARCHMENT[2], FLAME[3], WOOD[1], IRON[3])[state]
    if glyph == "cross":
        ic.cross(p, 1, 2, 11, SHADOW, 5)
        ic.cross(p, 1, 2, 11, tone, 3)
    else:
        d = "r" if glyph == "next" else "l"
        ic.chevron(p, 2, 1, 10, 13, SHADOW, d, 5)
        ic.chevron(p, 3, 2, 8, 11, tone, d, 3)
    return p.im


# ---------------------------------------------------------------------------------------------- bubbles


def bubble(w: int, h: int, seed: int, ramp: Ramp = PARCHMENT, tail: int = 0, tail_x: int = 6, r: int = 4, ink: Color = SHADOW) -> Image.Image:
    """A speech bubble: a rounded body of `ramp` with a rim, a lit upper-left edge and, if `tail` > 0, a pointer of that
    height at the lower left, `tail_x` pixels from the left."""
    p = Pix(w, h, seed=seed)
    bh = h - tail
    p.draw.rounded_rectangle((0, 0, w - 1, bh - 1), radius=r, fill=ink)
    p.draw.rounded_rectangle((1, 1, w - 2, bh - 2), radius=max(1, r - 1), fill=ramp[3])
    p.rect(2, bh - 3, w - 4, 1, ramp[2])
    p.hline(r, 1, w - 2 * r, ramp[4])
    if tail:
        p.poly([(tail_x, bh - 2), (tail_x + tail + 2, bh - 2), (tail_x, h - 1)], ink)
        p.poly([(tail_x + 1, bh - 2), (tail_x + tail, bh - 2), (tail_x + 1, h - 3)], ramp[2])
    return p.im


# ---------------------------------------------------------------------------------------------- one-offs


def day_card(w: int, h: int, seed: int, today: bool = False) -> Image.Image:
    """A calendar day card: a plank with a pale header band (`today`: header over a slate body, as the game's)."""
    p = Pix(w, h, seed=seed)
    if today:
        p.rect(0, 0, w, h, SHADOW)
        p.rect(1, 1, w - 2, h - 2, STONE[1])
        p.dither(1, 12, w - 2, h - 14, STONE[2], 0.4)
        p.rect(1, 1, w - 2, 11, PARCHMENT[3])
        p.hline(1, 11, w - 2, PARCHMENT[1])
    else:
        planks(p, 0, 0, w, h, PALE_WOOD, plank=h, nails=False)
        p.rect(0, 0, w, h, PALE_WOOD[3])
        p.dither(0, 0, w, h, PALE_WOOD[2], 0.3)
        p.rect(0, 14, w, 2, PARCHMENT[3])
        p.frame(0, 0, w, h, SHADOW)
    return p.im


def stack_icon(w: int, h: int, seed: int, kind: str) -> Image.Image:
    """The small cost-tag plaques: parchment tag, bought one darker with a punched hole."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, PARCHMENT[3] if kind == "cost" else PARCHMENT[1])
    p.hline(1, 1, w - 2, PARCHMENT[4])
    return p.im


def checkbox(w: int, h: int, seed: int, checked: bool = False) -> Image.Image:
    """A small wooden box with a parchment inside; ticked, it carries a green tick."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, WOOD[3])
    p.rect(3, 3, w - 6, h - 6, PARCHMENT[3] if checked else PARCHMENT[2])
    p.hline(3, 3, w - 6, PARCHMENT[1])
    if checked:
        ic.tick(p, 3, 3, w - 6, h - 6, MOSS[2], 2)
    return p.im


def tick_big(w: int, h: int, seed: int) -> Image.Image:
    """A bold green tick with a SHADOW rim."""
    p = Pix(w, h, seed=seed)
    ic.tick(p, 2, 2, w - 4, h - 4, SHADOW, 7)
    ic.tick(p, 2, 2, w - 4, h - 4, MOSS[3], 5)
    ic.tick(p, 3, 2, w - 6, h - 6, MOSS[2], 2)
    return p.im


def glyph_white(w: int, h: int, seed: int, glyph: str, thick: int) -> Image.Image:
    """A flat white glyph filling the picture (large masks the game tints)."""
    p = Pix(w, h, seed=seed)
    draw_glyph(p, glyph, 0, 0, w, h, WHITE, thick)
    return p.im


def thin_arrow(w: int, h: int, seed: int) -> Image.Image:
    """A narrow brown arrow pointing right (a step marker)."""
    p = Pix(w, h, seed=seed)
    p.rect(0, h // 2 - 1, w - 5, 2, LEATHER[2])
    ic.chevron(p, w - 8, 0, 8, h, LEATHER[2], "r", 2)
    return p.im


def curved_arrow(w: int, h: int, seed: int, right: bool) -> Image.Image:
    """A swoop of an arrow bending down and round (page back or forward), in dark indigo ink."""
    p = Pix(w, h, seed=seed)
    p.draw.arc((2, -h + 4, w - 3, h - 3), 20, 160, fill=NAVY[1], width=3)
    tip = (w - 3, h // 2 + 1) if right else (2, h // 2 + 1)
    side = -1 if right else 1
    p.poly([tip, (tip[0] + side * 7, tip[1] - 4), (tip[0] + side * 2, tip[1] - 7)], NAVY[2])
    p.px(tip[0] + side * 4, tip[1] - 4, NAVY[3])
    return p.im


def refresh_icon(w: int, h: int, seed: int) -> Image.Image:
    """Two arrows chasing each other (reload): moss and wine."""
    p = Pix(w, h, seed=seed)
    ic.refresh(p, 0, 0, w, h, MOSS[3], MOSS[2])
    return p.im


def scroll_rail(w: int, h: int, seed: int) -> Image.Image:
    """The groove a scroll bar slides in: a dark channel between two lit lips, the whole 18 pixels wide with 2 spare."""
    p = Pix(w, h, seed=seed)
    p.rect(2, 0, w - 4, h, SHADOW)
    p.rect(3, 0, w - 6, h, OAK[1])
    p.vline(3, 0, h, OAK[0])
    p.vline(w - 4, 0, h, OAK[3])
    p.speckle(3, 0, w - 6, h, (OAK[0], OAK[2]), 0.05)
    return p.im


def scroll_grip(w: int, h: int, seed: int) -> Image.Image:
    """The slider of a scroll bar: a polished plank with brass end caps and grip ridges at the middle."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, PALE_WOOD[2])
    p.vline(1, 1, h - 2, PALE_WOOD[4])
    p.vline(w - 2, 1, h - 2, PALE_WOOD[0])
    p.dither(2, 1, w - 4, h - 2, PALE_WOOD[3], 0.3)
    for y in (1, h - 6):
        p.rect(1, y, w - 2, 5, BRASS[2])
        p.hline(1, y, w - 2, BRASS[4])
        p.hline(1, y + 4, w - 2, BRASS[0])
    for k in range(-3, 4):
        yy = h // 2 + k * 3
        p.hline(4, yy, w - 8, PALE_WOOD[0])
        p.hline(4, yy + 1, w - 8, PALE_WOOD[4])
    return p.im


def track(w: int, h: int, seed: int, knob: bool = False) -> Image.Image:
    """A slider's channel (`knob` False) or its small handle (`knob` True) in brass and dark wood."""
    p = Pix(w, h, seed=seed)
    if knob:
        p.rect(0, 0, w, h, SHADOW)
        p.rect(1, 1, w - 2, h - 2, BRASS[2])
        p.hline(1, 1, w - 2, BRASS[4])
        p.vline(1, 1, h - 2, BRASS[3])
        p.hline(1, h - 2, w - 2, BRASS[0])
    else:
        p.rect(0, 0, w, h, BRASS[2])
        p.rect(1, 0, w - 2, h, SHADOW)
        p.rect(2, 0, w - 4, h, OAK[1])
    return p.im


def ruler(w: int, h: int, seed: int) -> Image.Image:
    """A vertical rule of tick marks in ink on nothing: long every fifth, short between."""
    p = Pix(w, h, seed=seed)
    p.vline(w - 6, 0, h, BRASS[1])
    for i, y in enumerate(range(2, h, 6)):
        n = 12 if i % 5 == 0 else 6
        p.hline(w - 6 - n, y, n, BRASS[2])
    return p.im


def shutter(w: int, h: int, seed: int) -> Image.Image:
    """Closed slats of dark wood, each with a lit top edge and a gap of shade beneath."""
    p = Pix(w, h, seed=seed)
    y = 0
    while y < h:
        slat = min(7, h - y)
        tone = p.rng.choice((1, 2, 2))
        p.rect(0, y, w, slat, OAK[tone])
        p.hline(0, y, w, OAK[4])
        p.hline(0, y + slat - 1, w, SHADOW)
        p.speckle(0, y + 1, w, slat - 2, (OAK[0], OAK[3]), 0.03)
        y += slat
    return p.im


def wanted(w: int, h: int, seed: int) -> Image.Image:
    """A big parchment notice with a grid of twelve empty portrait frames, each a head-and-shoulders silhouette."""
    p = Pix(w, h, seed=seed)
    p.paste(sheet(w, h, seed, torn="lrtb"), 0, 0)
    cw, ch = (w - 60) // 3, (h - 220) // 4
    for i in range(12):
        x, y = 30 + (i % 3) * cw, 170 + (i // 3) * ch
        p.rect(x + 8, y + 8, cw - 16, ch - 16, SHADOW)
        p.rect(x + 10, y + 10, cw - 20, ch - 20, PARCHMENT[2])
        cx = x + cw // 2
        p.ellipse(cx - 24, y + ch // 2 - 40, 48, 56, WOOD[1])
        p.ellipse(cx - 44, y + ch // 2 + 8, 88, 70, WOOD[1])
        p.dither(x + 10, y + 10, cw - 20, 8, SHADOW, 0.3)
    p.rect(60, 40, w - 120, 90, WINE[1])
    p.frame(60, 40, w - 120, 90, SHADOW)
    p.rect(66, 46, w - 132, 78, WINE[2])
    font.write(p, (w - font.width("WANTED", 9)) // 2, 62, "WANTED", PARCHMENT[4], 9)
    return p.im


def wine_notice(w: int, h: int, seed: int) -> Image.Image:
    """A pale pink-tinted parchment page with a scatter of bottles, glasses and grapes (the wine tutorial)."""
    p = Pix(w, h, seed=seed)
    p.paste(sheet(w, h, seed, tone=tuple(mix(c, (200, 120, 130), 0.18) for c in PARCHMENT), torn="b"), 0, 0)
    for i in range(7):
        x, y = 30 + (i * 83) % (w - 80), 40 + (i * 131) % (h - 140)
        ang = (-1) ** i
        p.rect(x + 12, y, 14, 28, WINE[1])
        p.rect(x + 8, y + 26, 22, 54, WINE[2])
        p.rect(x + 8, y + 26, 5, 54, WINE[3])
        p.rect(x + 12, y - 5, 14, 7, BRASS[2])
        p.rect(x + 11, y + 50, 16, 14, PARCHMENT[3])
        p.hline(x + 8, y + 79, 22, SHADOW)
        if ang > 0:
            p.ellipse(x + 40, y + 60, 12, 12, PLUM[2])
            p.ellipse(x + 46, y + 70, 12, 12, PLUM[3])
    return p.im


def clipboard(w: int, h: int, seed: int) -> Image.Image:
    """A writing board: dark wood with a brass clip, a pale sheet showing."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 2, w, h - 2, SHADOW)
    p.rect(1, 3, w - 2, h - 4, WOOD[2])
    p.dither(1, 3, w - 2, h - 4, WOOD[3], 0.3)
    p.rect(5, 9, w - 10, h - 14, SHADOW)
    p.rect(6, 10, w - 12, h - 16, PARCHMENT[3])
    p.dither(6, 10, w - 12, 5, PARCHMENT[1], 0.4)
    p.rect(w // 2 - 10, 0, 20, 8, BRASS[2])
    p.hline(w // 2 - 10, 0, 20, BRASS[4])
    p.hline(w // 2 - 10, 7, 20, BRASS[0])
    fake_text(p, 9, 18, w - 18, h - 28, PARCHMENT[1], gap=2)
    return p.im


def book_cover(w: int, h: int, seed: int, pale: bool = False) -> Image.Image:
    """The back of a book: leather over boards with brass corners and raised bands on the spine edge."""
    p = Pix(w, h, seed=seed)
    ramp = PALE_WOOD if pale else LEATHER
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, ramp[2])
    p.dither(1, 1, w - 2, h - 2, ramp[1], 0.3)
    p.rect(1, 1, 5, h - 2, ramp[1])
    for y in (8, h // 2, h - 10):
        p.hline(1, y, w - 2, ramp[3])
        p.hline(1, y + 1, w - 2, ramp[0])
    for x, y in ((w - 9, 1), (w - 9, h - 9)):
        p.rect(x, y, 8, 8, BRASS[2])
        p.hline(x, y, 8, BRASS[4])
    p.frame(10, 12, w - 22, h - 24, ramp[3])
    return p.im


def seal_card(w: int, h: int, seed: int) -> Image.Image:
    """The watch's pass: a red card with a brass crest and the lettering SECURITY 110 as on the game's."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, WINE[2])
    p.dither(1, 1, w - 2, h - 2, WINE[1], 0.25)
    p.hline(1, 1, w - 2, WINE[4])
    p.vline(1, 1, h - 2, WINE[3])
    crest = ic.crest(14, 14)
    p.paste(crest, (w - 14) // 2, 3)
    font.write(p, (w - font.width("SECURITY")) // 2, 19, "SECURITY", BRASS[3])
    font.write(p, (w - font.width("110")) // 2, 28, "110", BRASS[4])
    return p.im


def end_key(w: int, h: int, seed: int) -> Image.Image:
    """A red keypad key lettered END (hang up)."""
    p = Pix(w, h, seed=seed)
    p.paste(plaque(w, h, seed, "normal", WINE, None), 0, 0)
    font.write(p, (w - font.width("END")) // 2, (h - 7) // 2, "END", WINE[4])
    return p.im


def num_key(w: int, h: int, seed: int, state: int) -> Image.Image:
    """A small dark key with an engraved 1 (state 0 plain/hover, 1 pressed) or an empty key (state 2)."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, NAVY[1] if state != 1 else NAVY[0])
    p.rect(1, h - 3, w - 2, 2, NAVY[0])
    p.hline(1, 1, w - 2, NAVY[2])
    if state < 2:
        font.write(p, (w - 5) // 2, 1, "1", NAVY[3])
    return p.im


def key_cap(w: int, h: int, seed: int, round_: bool) -> Image.Image:
    """A keypad cap in pale wood with a teal-glass rim: octagonal (`round_`) or rectangular."""
    p = Pix(w, h, seed=seed)
    cut = 3 if round_ else 2
    for c, inset in ((SHADOW, 0), (GLASS[3], 1), (PARCHMENT[3], 3)):
        q = Pix(w, h)
        q.rect(inset, inset, w - 2 * inset, h - 2 * inset, c)
        for cx, cy in ((inset, inset), (w - 1 - inset, inset), (inset, h - 1 - inset), (w - 1 - inset, h - 1 - inset)):
            for i in range(cut - inset // 2):
                for j in range(cut - inset // 2 - i):
                    q.px(cx + (j if cx == inset else -j), cy + (i if cy == inset else -i), (0, 0, 0, 0))
        p.paste(q, 0, 0)
    p.dither(3, 3, w - 6, h - 6, PARCHMENT[2], 0.3)
    return p.im


def porthole(w: int, h: int, seed: int) -> Image.Image:
    """A round brass-rimmed window onto night (the station marker)."""
    return ic.medallion(w, h, BRASS[3], SHADOW)


def frame_square(w: int, h: int, seed: int) -> Image.Image:
    """A hollow wooden frame with a dark field (the red square: a selected-slot frame)."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, FLAME[1])
    p.hline(1, 1, w - 2, FLAME[2])
    p.vline(1, 1, h - 2, FLAME[2])
    p.rect(4, 4, w - 8, h - 8, SHADOW)
    p.rect(5, 5, w - 10, h - 10, STONE[1])
    return p.im


def patch(w: int, h: int, seed: int) -> Image.Image:
    """An embroidered cloth patch: wine twill with stitched stars in a grid."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, WINE[1])
    p.dither(0, 0, w, h, WINE[2], 0.4)
    for y in range(3, h, 8):
        for x in range(3 + (y // 8 % 2) * 4, w, 8):
            p.px(x, y, WINE[4])
            p.px(x - 1, y, WINE[3])
            p.px(x + 1, y, WINE[3])
            p.px(x, y - 1, WINE[3])
            p.px(x, y + 1, WINE[3])
    return p.im


def postit(w: int, h: int, seed: int, ramp: Ramp) -> Image.Image:
    """A scrap of coloured paper with a curled lower corner."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, ramp[2])
    p.hline(0, 0, w, ramp[3])
    p.dither(0, h // 2, w, h // 2, ramp[1], 0.3)
    p.poly([(w - 5, h - 1), (w - 1, h - 1), (w - 1, h - 5)], CLEAR_C)
    p.poly([(w - 5, h - 1), (w - 5, h - 5), (w - 1, h - 5)], ramp[3])
    return p.im


CLEAR_C: Final[Color] = (0, 0, 0, 0)


def red_cross(w: int, h: int, seed: int) -> Image.Image:
    """A big red X (refusal) in flat ink with a dark rim."""
    p = Pix(w, h, seed=seed)
    s = min(w, h)
    ic.cross(p, 0, 0, s, SHADOW, s // 5 + 4)
    ic.cross(p, 2, 2, s - 4, WINE[3], s // 5)
    ic.cross(p, 2, 2, s - 4, WINE[4], 2)
    return p.im


def growth_row(w: int, h: int, seed: int, lit: bool = False) -> Image.Image:
    """Six growth stages side by side (13 pixels each): a seed, a sprout, then taller and taller plants; `lit` is brighter."""
    p = Pix(w, h, seed=seed)
    leaf, stem = (MOSS[3], MOSS[2]) if lit else (MOSS[2], MOSS[1])
    for i in range(6):
        x = i * 13 + 6
        p.ellipse(x - 3, h - 3, 7, 3, LEATHER[2])
        up = 2 + i * 2
        p.vline(x, h - 3 - up, up, stem)
        for k in range(min(i, 3) + 1):
            y = h - 4 - up + k * 3
            p.rect(x - 2 - (k % 2), y, 2, 2, leaf)
            p.rect(x + 1 + (k % 2) * 0, y + 1, 2, 2, leaf)
    return p.im


def one_bar(w: int, h: int, seed: int, c: Color) -> Image.Image:
    """A one-pixel-high progress bar colour."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, c)
    return p.im


def dashes(w: int, h: int, seed: int, c: Color, dot: bool = False) -> Image.Image:
    """A dashed or dotted separator rule."""
    p = Pix(w, h, seed=seed)
    step = 2 if dot else 6
    for x in range(0, w, step * 2 if dot else 8):
        p.rect(x, 0, step if dot else 5, h, c)
    return p.im


def purple_foil(w: int, h: int, seed: int) -> Image.Image:
    """A 6x6 flecked plum foil tile."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, PLUM[1])
    p.speckle(0, 0, w, h, (PLUM[2], PLUM[0], PLUM[3]), 0.5)
    return p.im


def cloth_panel(w: int, h: int, seed: int, ramp: Ramp, header: Ramp | None = None) -> Image.Image:
    """A nine-slice panel of woven cloth in `ramp` with a brass edge line; with `header`, a wooden bar over it carrying
    stitched notepad rules (the orange note panel)."""
    p = Pix(w, h, seed=seed)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, ramp[2])
    for y in range(2, h - 1, 3):
        p.hline(1, y, w - 2, mix(ramp[2], ramp[1], 0.6))
    p.hline(1, 1, w - 2, ramp[3])
    p.vline(1, 1, h - 2, ramp[3])
    p.frame(2, 2, w - 4, h - 4, BRASS[1])
    if header:
        p.rect(1, 1, w - 2, 8, header[2])
        p.hline(1, 1, w - 2, header[4])
        p.hline(1, 8, w - 2, header[0])
        for y in range(14, h - 4, 4):
            p.hline(4, y, w - 8, mix(ramp[2], SHADOW, 0.35))
    return p.im


def dialog_slab(w: int, h: int, seed: int) -> Image.Image:
    """The big confirm dialog: a dark oak board with a brass inner trim."""
    return board(w, h, seed, OAK, plank=22, trim=BRASS[1])


# ---------------------------------------------------------------------------------------------- the list

# paper and notice sheets
reg(sheet, "appraisal_panel", "card_blank_2x")
reg(sheet, "card_ripped_2x", torn="lrb")
reg(sheet, "inspection_receipt", torn="rb")
reg(sheet, "slip", text="lines", torn="bt")
reg(sheet, "handnote", text="lines", torn="b")
reg(sheet, "newspaper", text="columns", torn="b")
reg(sheet, "guide_clean", torn="b")
reg(sheet, "guide_grid", grid=22)
reg(sheet, "guide_reworked", text="lines", torn="r")
reg(sheet, "lease_doc", text="lines", seal=True)
reg(sheet, "layout2", "layout3", "layout4", grid=30)
reg(sheet, "mentors_notes", text="lines", torn="rb")
reg(sheet, "notebook_manual", rules=12)
reg(sheet, "exchange", text="lines", tone=tuple(mix(c, (170, 120, 130), 0.2) for c in PARCHMENT))
reg(sheet, "incident_slip_2x", text="lines", seal=True)
reg(sheet, "contractBack", seal=True)
reg(sheet, "perks_tooltip_calendar")
reg(sheet, "reputation_background", rules=0)
reg(sheet, "bargain", "bargain_plate")
reg(wanted, "wanted")
reg(wine_notice, "wine_tutorial")
reg(clipboard, "clipboard")
reg(book_cover, "bookBack")
reg(book_cover, "bookBack_white", pale=True)
reg(day_card, "day")
reg(day_card, "today", today=True)
# lecterns
reg(lectern, "tablet")
reg(lectern, "offer window", notch=True, tab_label=True)
reg(lectern, "endofday")
reg(lectern, "tablet_bargain_open", right=8, notch=False)
reg(lectern, "phone", left=96, right=8, notch=False, bell=True)
reg(spine, "bargain_spine")
# dark panels and bars
reg(dialog_slab, "confirmation_dialog_2x")
reg(board, "subpanel_x2", ramp=WOOD)
reg(slab, "grey_2x", edge=2)
reg(slab, "grey2_2x", edge=3)
reg(recess, "deepArea2", "deepArea_2x")
reg(recess, "element_bg", "element_bg_single", ramp=STONE)
reg(recess, "reputation_box", ramp=STONE)
reg(cloth_panel, "uiback1L", ramp=WINE)
reg(cloth_panel, "uiback2L", ramp=PLUM)
reg(cloth_panel, "uibackOrange1L", ramp=PALE_WOOD, header=FLAME)
reg(shutter, "shutter_door_cropped_2x")
reg(ruler, "reputation_grid")
# strips, tabs, tags
reg(strip, "notebook_manual_section", "notebook_manual_section_2x", white=True)
reg(strip, "depression_section_x2", ramp=STONE, cut=6)
reg(strip, "guide_section", ramp=PALE_WOOD)
reg(strip, "button_contact", ramp=PARCHMENT, cut=0)
reg(strip, "header_bar", ramp=WOOD, cut=14)
reg(strip, "requirement", ramp=BRASS)
reg(strip, "notice_box", ramp=FLAME, cut=5)
reg(strip, "pricebox", ramp=BRASS)
reg(strip, "textbox", ramp=PARCHMENT)
reg(strip, "top_button", ramp=PALE_WOOD)
reg(strip, "overlay box", ramp=IRON, cut=6)
reg(strip, "notebox", "Note box", ramp=IRON, cut=8)
reg(strip, "header2", ramp=WOOD, cut=7)
reg(tab, "start", left=5, ramp=FLAME)
reg(tab, "middle", ramp=FLAME)
reg(tab, "end", right=5, ramp=FLAME)
reg(tab, "start_top", left=5, white=True)
reg(tab, "middle_top", white=True)
reg(tab, "end_top", right=5, white=True)
reg(tab, "event", left=4, right=4, ramp=FLAME)
reg(tab, "event_top", left=4, right=4, white=True)
reg(tab, "container_tag_2x", left=8, right=8, white=True)
reg(tab, "nightly_tab", right=8, white=True)
reg(tab, "nightly_tab_reversed", left=8, white=True)
reg(stack_icon, "cost_area", kind="cost")
reg(stack_icon, "cost_area_bought", kind="bought")
reg(red_cross, "cross@79x80")
reg(growth_row, "iconGrowth")
reg(growth_row, "iconGrowth_lit", lit=True)
reg(one_bar, "green_bar", c=MOSS[3])
reg(one_bar, "red_bar", c=WINE[3])
reg(dashes, "recorder_text separators", c=IRON[3])
reg(dashes, "dotted_line", c=WHITE, dot=True)
reg(scroll_rail, "marketplace_scrollbar_back")
reg(scroll_grip, "scrollbar_handle")
reg(track, "sliding_area")
reg(track, "handle", knob=True)
# buttons with four states
for _stem, _states, _kw in (
    ("nego_button", ("", "_Hover", "_Pressed", "_Disabled"), {"ramp": WOOD, "trim": FLAME}),
    ("nego_buttonx2", ("-1Normal", "-2Hover", "-3Pressed", "-4Disabled"), {"ramp": WOOD, "trim": FLAME}),
):
    for _s, _st in zip(_states, STATES):
        _stem2 = f"{_stem}{_s}"
        reg(plaque, _stem2, state=_st, **_kw)
reg(plaque, "general_button_2x", state="normal", ramp=PALE_WOOD)
reg(plaque, "general_button_2x_c", state="pressed", ramp=PALE_WOOD)
reg(plaque, "general_button_2x_d", state="disabled", ramp=PALE_WOOD)
reg(plaque, "general_button_2x_hl", state="hover", ramp=PALE_WOOD)
reg(plaque, "button", state="normal", ramp=WOOD, trim=FLAME)
reg(plaque, "button_unavaible", state="disabled", ramp=WOOD)
reg(plaque, "button_confront", "button_confront_2x", state="normal", ramp=IRON, trim=PARCHMENT)
reg(plaque, "aqua_scan_button", "chem_scan_button", state="normal", ramp=MOSS, trim=PARCHMENT)
reg(plaque, "playtest_button", state="normal", ramp=IRON, trim=PARCHMENT)
reg(plaque, "blue_button_2x", state="normal", ramp=NAVY, trim=GLASS)
reg(plaque, "button_back_blue_m", state="normal", ramp=NAVY, trim=None, cut=2)
reg(tile_strip, "button_bargain-Sheet", glyph="bubble", ink=WINE, body=IRON)
reg(tile_strip, "button_zoom", glyph="zoom")
reg(square_frames, "paper_buttons_screen")
# tile buttons
for _stem, _gl, _body, _ink in (
    ("network_button", "plain", WOOD, PARCHMENT),
):
    for _s, _st in zip(("_normal", "_hover", "_pressed", "_disabled"), STATES):
        reg(tile, f"{_stem}{_s}", state=_st, glyph=_gl, body=_body, ink=_ink)
for _s, _st in zip(("_normal", "_hover"), STATES):
    reg(tile, f"next{_s}", state=_st, glyph="next", body=IRON, ink=PARCHMENT)
    reg(tile, f"prev{_s}", state=_st, glyph="prev", body=IRON, ink=PARCHMENT)
for _s, _st in zip(("_normal", "_highlight", "_pressed", "_disabled"), ("normal", "hover", "pressed", "disabled")):
    reg(tile, f"button_rewind{_s}", state=_st, glyph="undo", body=PALE_WOOD, ink=FLAME)
reg(tile, "button_dismiss", state="normal", glyph="cross", body=WINE, ink=PARCHMENT)
reg(tile, "button_sec", state="normal", glyph="helm", body=GLASS, ink=IRON)
reg(tile, "button_transfer", state="normal", glyph="arrow_down", body=MOSS, ink=MOSS)
reg(tile, "close", state="normal", glyph="cross", body=NAVY, ink=PARCHMENT)
reg(tile, "blue_close_button", state="normal", glyph="cross", body=IRON, ink=GLASS)
reg(tile, "cross@28x28", state="normal", glyph="cross", body=IRON, ink=LINEN)
reg(tile, "cross_hover", state="hover", glyph="cross", body=IRON, ink=BRASS)
reg(tile, "bargain_active", state="hover", glyph="bubble", body=MOSS, ink=WINE)
reg(tile, "phone_button_hover", state="hover", glyph="plain", body=NAVY, ink=PARCHMENT)
reg(num_key, "phone_button1h", state=0)
reg(num_key, "phone_button1p", state=1)
reg(num_key, "phone_button_press", state=2)
reg(key_cap, "phone_button_large", round_=False)
reg(key_cap, "phone_button_normal", round_=True)
reg(end_key, "phone_red_button_p")
reg(porthole, "station")
reg(frame_square, "red_square")
# glyph buttons on paper
for _i in range(4):
    reg(paper_arrow, f"paper_buttons{_i + 1}", glyph="next", state=_i)
    reg(paper_arrow, f"paper_buttons_close{_i + 1}", glyph="cross", state=_i)
    reg(paper_arrow, f"paper_buttons_l_{_i + 1}", glyph="prev", state=_i)
reg(thin_arrow, "arrow@16x12")
reg(glyph_white, "arrow@600x600", glyph="next", thick=150)
reg(glyph_white, "dropdown_arrow", glyph="down", thick=12)
reg(curved_arrow, "arrow_left", right=False)
reg(curved_arrow, "arrow_right", right=True)
reg(tick_big, "Check")
reg(checkbox, "checkbox")
reg(checkbox, "checkbox_checked", checked=True)
reg(refresh_icon, "refresh")
reg(lambda w, h, s, left: ic.mouse(w, h, left), "mouse_icon_left", left=True)
reg(lambda w, h, s, left: ic.mouse(w, h, left), "mouse_icon_right", left=False)
# pictograms
for _stem, _mood in (("emoji_angry", "angry"), ("emoji_happy", "happy"), ("emoji_sad", "sad"), ("emoji_skull", "skull"),
                     ("emoji_smile", "smile"), ("emoji_star", "star")):
    reg(lambda w, h, s, mood: ic.face(w, h, mood), _stem, mood=_mood)
for _stem, _disc, _mark in (("info_cream", PARCHMENT[3], SHADOW), ("info_dark", IRON[2], LINEN[3]), ("info_light", LINEN[3], IRON[2]),
                            ("info_red", WINE[3], SHADOW), ("info_tan", FLAME[2], SHADOW), ("info@128x128", WHITE, IRON[2])):
    reg(lambda w, h, s, body, mark: ic.info_disc(w, h, body, mark), _stem, body=_disc, mark=_mark)
reg(lambda w, h, s, kind, c, lit=False: ic.stat_icon(w, h, kind, c, lit), "iconMineral", kind="herb", c=MOSS[2])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "iconTrash", kind="sack", c=WINE[3])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "iconWater", kind="drop", c=GLASS[3])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "icon_contraceptive", kind="lock", c=STONE[2])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "icon_euphoria", kind="grin", c=PLUM[3])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "icon_synaprest", kind="plus", c=LINEN[2])
reg(lambda w, h, s, kind, c: ic.stat_icon(w, h, kind, c), "icon_toxicity", kind="skull", c=MOSS[3])
reg(lambda w, h, s: ic.cat_banner(w, h), "cat")
reg(lambda w, h, s: ic.potion(w, h), "galaxy")
reg(lambda w, h, s: ic.turnip(w, h), "nutrifruit")
reg(lambda w, h, s: ic.tin(w, h, "PEAT"), "peat")
reg(lambda w, h, s: ic.tankard(w, h), "soda")
reg(lambda w, h, s: ic.medallion(w, h, PALE_WOOD[3], PALE_WOOD[4]), "perk_h")
reg(lambda w, h, s: ic.crest(w, h), "sec_seal_2x")
reg(seal_card, "sec_card")
reg(lambda w, h, s, red: ic.lamp_pair(w, h, red), "sec lamps green", red=False)
reg(lambda w, h, s, red: ic.lamp_pair(w, h, red), "sec lamps red", red=True)
reg(patch, "patch")
reg(postit, "postit_blue", ramp=NAVY)
reg(postit, "postit_pink", ramp=WINE)
reg(purple_foil, "foil")
# small nine-slice parts
reg(notched, "card_header_plate", fill=WHITE, ring=None)
reg(notched, "card_plate", fill=OAK[0], ring=None)
reg(notched, "card_outline_normal", fill=STONE[2], ring=STONE[3])
reg(notched, "card_outline_selected", fill=STONE[2], ring=FLAME[3])
reg(notched, "card_outline_unavailable", fill=STONE[1], ring=WINE[3])
reg(notched, "frame_notched", fill=IRON[1], ring=None)
reg(notched, "frame_2", fill=IRON[3], ring=WHITE, rim=2, notch=0)
reg(rounded, "tag_rounded", r=3)
reg(rounded, "white_rounded", r=8)
# bubbles
reg(bubble, "tutorial_bubble_unpointed_x2")
reg(bubble, "tutorial_bubble_x2", tail=14, tail_x=8)
reg(bubble, "dialogue_bubble_science", ramp=PLUM, r=8)
reg(bubble, "bubble_sci_p", ramp=PLUM, tail=9, tail_x=10, r=8)
reg(bubble, "dialogue_bubble2_pink_pointed", ramp=WINE, tail=9, tail_x=10, r=8)
