"""The windows of the tavern: the tiles and sheets the game builds every window from (inventory, machines, options).

The game cuts its sheets by fixed rectangles and stretches or tiles its small pieces, so every picture here keeps the
size, the silhouette and the place of the one it replaces. Only the look changes: backgrounds are cloth, parchment,
leather and oak that tile seamlessly; borders are an oak edge with brass corners; buttons are wooden plaques with an
amber glyph; sliders and toggles are oak and brass. The big sheets (`elements_inner`, `elements_outer`, `background`,
`border-export`) are assembled from the very same sprite functions that draw the single files, so a sheet and its
pieces always agree.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image

from palette import BRASS, EMBER, FLAME, IRON, LINEN, MOSS, NAVY, PALE_WOOD, PARCHMENT, SHADOW, SOOT, STONE, WINE, WOOD
from pix import CLEAR, Color, Pix, Ramp, mix, rgb

# Hue families the window colours stand for, dark to light. NAVY, WINE, MOSS are the shared cloths; the rest are made
# here from the same warm-shadow logic.
BLUE: Final[Ramp] = (rgb("#0b1220"), NAVY[1], NAVY[2], NAVY[3], rgb("#86a2c4"))
TEAL: Final[Ramp] = (rgb("#0c2128"), rgb("#17404a"), rgb("#2a6070"), rgb("#418294"), rgb("#6aa8b4"))
GREEN: Final[Ramp] = (MOSS[0], MOSS[1], MOSS[2], MOSS[3], rgb("#93b474"))
RED: Final[Ramp] = (WINE[0], WINE[1], WINE[2], WINE[3], WINE[4])
PLUM: Final[Ramp] = (rgb("#1e0f24"), rgb("#3d1f48"), rgb("#5e3470"), rgb("#84508f"), rgb("#a874b0"))
OCHRE: Final[Ramp] = (rgb("#3a2008"), rgb("#6b3d12"), rgb("#a0602a"), rgb("#c98a45"), rgb("#e8b570"))
LINEN5: Final[Ramp] = (*LINEN, rgb("#efe6cf"))
SLATE: Final[Ramp] = (rgb("#16141a"), rgb("#26222e"), rgb("#3a3447"), rgb("#554d66"), rgb("#7a7090"))

HUES: Final[Mapping[str, Ramp]] = {
    "blue": BLUE, "red": RED, "green": GREEN, "cyan": TEAL, "orange": OCHRE, "purple": PLUM, "yellow": BRASS,
}
EDGE: Final[Color] = WOOD[3]          # the one-pixel oak edge of a window
CORNER: Final[Color] = BRASS[3]       # brass corner studs
FRAME_NAMES: Final = ("black", "white", "blue", "green", "red", "tan")    # the order of the game's background sheet
MaskRows = Sequence[str]


# ---------------------------------------------------------------------------------------------- shape helpers


def cut_mask(w: int, h: int, cut: int = 1) -> list[str]:
    """A rectangle whose corners are cut by a `cut`-pixel staircase: the silhouette of every plaque."""
    rows = []
    for y in range(h):
        d = cut - min(y, h - 1 - y)
        rows.append("".join("." if x < d or x >= w - d else "#" for x in range(w)) if d > 0 else "#" * w)
    return rows


def pill_mask(w: int, h: int) -> list[str]:
    """A stadium: a rectangle with half-round ends, the silhouette of a toggle."""
    r = h / 2
    rows = []
    for y in range(h):
        dy = r - y - 0.5
        inset = round(r - math.sqrt(max(0.0, r * r - dy * dy)))
        rows.append("".join("." if x < inset or x >= w - inset else "#" for x in range(w)))
    return rows


def apply_mask(p: Pix, rows: MaskRows) -> None:
    """Makes every pixel the mask marks '.' transparent."""
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                p.px(x, y, CLEAR)


def inside_set(rows: MaskRows) -> set[tuple[int, int]]:
    return {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != "."}


def rim_sets(rows: MaskRows) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """The edge pixels of a mask (a neighbour outside it, or the picture's edge) and the ring just inside those."""
    s = inside_set(rows)
    near = ((1, 0), (-1, 0), (0, 1), (0, -1))
    edge = {q for q in s if any((q[0] + dx, q[1] + dy) not in s for dx, dy in near)}
    rim = {q for q in s - edge if any((q[0] + dx, q[1] + dy) in edge for dx, dy in near)}
    return edge, rim


def paint(p: Pix, points: set[tuple[int, int]], c: Color) -> None:
    for x, y in points:
        p.px(x, y, c)


def outlined(p: Pix, rows: MaskRows, c: Color = SHADOW) -> Image.Image:
    """Cuts the canvas to the silhouette and draws a one-pixel outline just inside it."""
    apply_mask(p, rows)
    p.outline(c, inside=True)
    return p.finish()


# ---------------------------------------------------------------------------------------------- seamless textures


def cloth(ramp: Ramp, seed: int) -> Pix:
    """A 16x16 woven cloth that tiles: a twill of fine diagonals and a few stray threads."""
    p = Pix(16, 16, ramp[2], seed=seed)
    for y in range(16):
        for x in range(16):
            k = (x + y) % 4
            if k == 0:
                p.px(x, y, mix(ramp[2], ramp[3], 0.4))
            elif k == 2:
                p.px(x, y, mix(ramp[2], ramp[1], 0.4))
    p.speckle(0, 0, 16, 16, (ramp[1], ramp[3]), 0.02)
    return p


def leather(ramp: Ramp, seed: int) -> Pix:
    """A 16x16 pebbled hide that tiles: dark pits and soft lit grains on a flat tone."""
    p = Pix(16, 16, ramp[1], seed=seed)
    for _ in range(26):
        x, y = p.rng.randrange(16), p.rng.randrange(16)
        p.px(x, y, ramp[2])
        p.px((x + 1) % 16, y, ramp[2])
        p.px(x, (y + 1) % 16, ramp[0])
    return p


def parchment(seed: int) -> Pix:
    """A 16x16 sheet of parchment that tiles: pale fibres run across it and a few darker flecks lie on it."""
    p = Pix(16, 16, PARCHMENT[3], seed=seed)
    for _ in range(14):
        x, y = p.rng.randrange(16), p.rng.randrange(16)
        c = PARCHMENT[2] if p.rng.random() < 0.7 else PARCHMENT[4]
        for k in range(p.rng.randrange(3, 7)):
            p.px((x + k) % 16, y, c)
    p.speckle(0, 0, 16, 16, (PARCHMENT[1],), 0.03)
    return p


def oak_planks(seed: int) -> Pix:
    """A 16x16 of two oak boards that tiles both ways: lit top edge, dark joint, grain, and a butt joint with a nail."""
    p = Pix(16, 16, seed=seed)
    for b, tone in ((0, 2), (8, 3)):
        p.rect(0, b, 16, 8, WOOD[tone])
        p.hline(0, b, 16, WOOD[tone + 1])
        p.hline(0, b + 6, 16, WOOD[tone - 1])
        p.hline(0, b + 7, 16, WOOD[0])
        for _ in range(3):
            x, y = p.rng.randrange(16), b + 1 + p.rng.randrange(5)
            for k in range(p.rng.randrange(4, 9)):
                p.px((x + k) % 16, y, WOOD[tone - 1])
        j = 5 + b
        p.vline(j % 16, b, 8, WOOD[0])
        p.vline((j + 1) % 16, b + 1, 6, WOOD[tone + 1])
        p.px((j + 3) % 16, b + 3, IRON[4])
        p.px((j - 3) % 16, b + 3, IRON[4])
    return p


def texture(kind: str) -> Pix:
    """The seamless 16x16 of one window colour, named by the game's file ('black' is the indigo one, 'tan' the dark)."""
    table: Mapping[str, Callable[[], Pix]] = {
        "black": lambda: cloth(SLATE, 1),
        "white": lambda: parchment(2),
        "blue": lambda: cloth(TEAL, 3),
        "green": lambda: cloth(GREEN, 4),
        "red": lambda: cloth(RED, 5),
        "tan": lambda: leather((SOOT[0], SOOT[1], SOOT[2], SOOT[3]), 6),
    }
    return table[kind]()


def with_alpha(p: Pix, alpha: int) -> Pix:
    """Scales a picture's opacity to `alpha`: the translucent overlays of the game's 'white' window."""
    p.im.putalpha(p.im.getchannel("A").point(lambda v: min(v, alpha)))
    return p


def frame_color(kind: str) -> Color:
    """The frame of a background tile: its own material, much darker."""
    r, g, b, _ = texture(kind).get(1, 1)
    return mix((r, g, b), SHADOW, 0.62)


def background(kind: str, style: str) -> Image.Image:
    """A window-colour tile: 'plain' fills the whole square (it tiles), 'border' and 'grid' add a one-pixel frame (the
    border also a lit inner edge). The 'white' kind is a translucent overlay, as in the game."""
    p = texture(kind)
    if style != "plain":
        c = frame_color(kind)
        r, g, b, _ = texture(kind).get(2, 2)
        light = mix((r, g, b), (255, 214, 140), 0.25)
        if style == "border":
            p.hline(1, 1, 14, light)
            p.vline(1, 1, 14, light)
        p.frame(0, 0, 16, 16, c if kind != "white" else mix(PARCHMENT[0], SHADOW, 0.5))
    if kind == "white":
        solid = p.im.copy()
        out = with_alpha(p, 91).im
        for x in range(16):
            for y in range(16):
                if style != "plain" and (x in (0, 15) or y in (0, 15)):
                    r, g, b, _ = solid.getpixel((x, y))  # type: ignore[misc]
                    out.putpixel((x, y), (r, g, b, 255))
        return out
    return p.finish()


def highlight_white() -> Image.Image:
    """The pale hover frame: a brass-yellow one-pixel rim around an almost clear square."""
    p = Pix(16, 16, (*PARCHMENT[4], 32))
    p.frame(0, 0, 16, 16, BRASS[4])
    return p.finish()


def pinned_top() -> Image.Image:
    """A diagonal hatch of faint dark stitches, the stripe that marks a pinned window."""
    p = Pix(16, 16)
    for y in range(16):
        for x in range((2 - y) % 4, 16, 4):
            p.px(x, y, (*SHADOW, 91))
    return p.finish()


def background_fill() -> Image.Image:
    """The body of a window where nothing else is drawn: oak boards that tile."""
    return oak_planks(7).finish()


# ---------------------------------------------------------------------------------------------- borders


def edge_pieces(a: Color = EDGE, b: Color | None = None, corner: Color | None = CORNER) -> dict[str, Image.Image]:
    """The one-pixel pieces of a window frame, by the game's name: four edges and four corners, and the whole frames
    made of them. `b` is the colour of the bottom and right edges when the frame is bevelled (the old border)."""
    b = a if b is None else b
    c_tl = corner or a
    c_br = corner or b

    def line(x: int, y: int, w: int, h: int, c: Color, size: tuple[int, int] = (16, 16)) -> Image.Image:
        p = Pix(*size)
        p.rect(x, y, w, h, c)
        return p.finish()

    def frame(size: tuple[int, int], top: bool = True) -> Image.Image:
        w, h = size
        p = Pix(w, h)
        if top:
            p.hline(0, 0, w, a)
        p.vline(0, 0, h, a)
        p.vline(w - 1, 0, h, b)
        p.hline(0, h - 1, w, b)
        for x, y, c in ((0, 0, c_tl), (w - 1, 0, c_tl), (0, h - 1, c_br), (w - 1, h - 1, c_br)):
            if top or y:
                p.px(x, y, c)
        return p.finish()

    def dot(x: int, y: int, c: Color) -> Image.Image:
        return line(x, y, 1, 1, c)

    return {
        "inside": frame((16, 16)), "outside": frame((16, 16)), "outside_crop": frame((16, 15), top=False),
        "outside_top": line(0, 0, 16, 1, a), "outside_bottom": line(0, 15, 16, 1, b),
        "outside_left": line(0, 0, 1, 16, a), "outside_right": line(15, 0, 1, 16, b),
        "outside_top_left": dot(0, 0, c_tl), "outside_top_right": dot(15, 0, c_tl),
        "outside_bottom_left": dot(0, 15, c_br), "outside_bottom_right": dot(15, 15, c_br),
    }


def border_sheet(two_tone: bool) -> Image.Image:
    """The 88x34 sheet of border pieces: two 16x16 frames, two vertical edges, four corner dots and two horizontal
    edges, all where the game cuts them. The old border is bevelled: lit edges in one tone, shaded in another."""
    a, b = (WOOD[4], WOOD[1]) if two_tone else (EDGE, EDGE)
    corner_a, corner_b = (a, b) if two_tone else (CORNER, CORNER)
    p = Pix(88, 34)

    def frame(x0: int, light: Color, dark: Color) -> None:
        p.hline(x0, 0, 15, light)
        p.vline(x0, 0, 16, light)
        p.vline(x0 + 15, 0, 15, dark)
        p.hline(x0 + 1, 15, 15, dark)
        p.px(x0 + 15, 0, dark if two_tone else CORNER)
        p.px(x0, 15, light if two_tone else CORNER)
        if not two_tone:
            p.px(x0, 0, CORNER)
            p.px(x0 + 15, 15, CORNER)

    frame(0, a, b)
    frame(18, b, a)
    p.vline(15, 18, 16, a)
    p.vline(18, 18, 16, b)
    p.hline(72, 15, 16, a)
    p.hline(72, 18, 16, b)
    for x, y, c in ((51, 15, corner_a), (54, 15, corner_a), (51, 18, corner_b), (54, 18, corner_b)):
        p.px(x, y, c)
    return p.finish()


# ---------------------------------------------------------------------------------------------- plaques and buttons


def plaque(w: int, h: int, face: Color, light: Color, dark: Color, *, cut: int = 1, outline: bool = True,
           pressed: bool = False, grain: bool = True, seed: int = 0) -> Image.Image:
    """A wooden plaque: flat face with a few grain strokes, a bevel (lit up-left; reversed when pressed) and a dark
    outline. Without an outline it is a bare bevelled square, as the coloured 15x15 buttons are."""
    p = Pix(w, h, face, seed=seed)
    if grain:
        for y in range(3, h - 2, 3):
            for _ in range(2):
                x0 = p.rng.randrange(2, max(3, w - 6))
                p.hline(x0, y, min(p.rng.randrange(3, 8), w - 2 - x0), mix(face, dark, 0.16))
    if outline:
        rows = cut_mask(w, h, cut)
        apply_mask(p, rows)
        p.outline(SHADOW, inside=True)
        p.bevel(1, 1, w - 2, h - 2, dark if pressed else light, light if pressed else dark)
        apply_mask(p, rows)
        p.outline(SHADOW, inside=True)
    else:
        p.bevel(0, 0, w, h, dark if pressed else light, light if pressed else dark)
    return p.finish()


def tinted_button(hue: str, disabled: bool) -> Image.Image:
    """A 15x15 coloured button: lit oak-and-dye plaque, or a dull, dark one when disabled."""
    r = HUES[hue]
    if disabled:
        face = mix(r[1], STONE[1], 0.45)
        return plaque(15, 15, face, mix(face, STONE[3], 0.5), mix(face, SHADOW, 0.5), outline=False, grain=False,
                      seed=len(hue))
    return plaque(15, 15, r[3], r[4], r[1], outline=False, seed=len(hue) + 9)


def lamp(hue: str, lit: bool) -> Image.Image:
    """A 6x6 indicator bead: a dyed glass stud, bright when lit and dim when not."""
    r: Ramp = LINEN5 if hue == "white" else (SLATE if hue == "dark" else HUES[hue])
    if hue in ("white", "dark"):
        r = (LINEN5 if lit else SLATE)
        r = (r[0], r[1], r[2], r[3], r[3])
    p = Pix(6, 6, r[3] if lit else r[1])
    p.frame(0, 0, 6, 6, r[1] if lit else r[0])
    p.hline(1, 1, 3, r[4] if lit else r[2])
    p.px(1, 2, r[4] if lit else r[2])
    p.px(4, 4, r[2] if lit else r[0])
    return p.finish()


# glyph pixels on a 16x16 button, by name
def glyph(kind: str) -> set[tuple[int, int]]:
    """The pixels of a button symbol (plus, minus, play, pause, next, previous, close) on a 16x16 face."""
    s: set[tuple[int, int]] = set()
    if kind == "up":
        s |= {(x, y) for x in range(5, 11) for y in (7, 8)} | {(x, y) for x in (7, 8) for y in range(5, 11)}
    elif kind == "down":
        s |= {(x, y) for x in range(4, 12) for y in (7, 8)}
    elif kind == "play":
        for dy in range(8):
            for dx in range((min(dy, 7 - dy) + 1) * 2):
                s.add((5 + dx, 4 + dy))
    elif kind == "pause":
        s |= {(x, y) for x in (5, 6, 9, 10) for y in range(4, 12)}
    elif kind in ("next", "previous"):
        for d in range(4):
            for x in (6 + d, 7 + d):
                s |= {(x, 4 + d), (x, 11 - d)}
        if kind == "previous":
            s = {(15 - x, y) for x, y in s}
    elif kind == "close":
        for i in range(8):
            for k in (0, 1):
                s |= {(min(11, 4 + i + k), 4 + i), (max(4, 11 - i - k), 4 + i)}
    return s


STATES: Final[Mapping[str, tuple[Color, Color, Color, Color, bool]]] = {
    # state: face, lit edge, dark edge, symbol, pressed
    "": (WOOD[2], WOOD[4], WOOD[0], FLAME[3], False),
    "_hl": (WOOD[3], PALE_WOOD[3], WOOD[1], FLAME[4], False),
    "_c": (WOOD[1], WOOD[3], WOOD[0], FLAME[2], True),
    "_d": (STONE[1], STONE[2], STONE[0], STONE[3], False),
}
CLOSE_SYMBOL: Final[Mapping[str, Color]] = {"": WINE[4], "_hl": rgb("#e88060"), "_c": WINE[3], "_d": STONE[3]}


def square_button(kind: str, state: str) -> Image.Image:
    """A 16x16 button on its wooden plaque with an amber symbol; `state` is '', '_hl', '_c' (pressed) or '_d'."""
    face, lit, dark, symbol, pressed = STATES[state]
    img = plaque(16, 16, face, lit, dark, pressed=pressed, seed=hash_seed(kind + state))
    p = Pix(16, 16)
    p.paste(img, 0, 0)
    if pressed:
        p.hline(2, 2, 12, dark)
    color = CLOSE_SYMBOL[state] if kind == "close" else symbol
    pts = glyph(kind)
    for x, y in pts:
        p.px(x + 1, y + 1, (*SHADOW, 255) if state != "_d" else dark)
    for x, y in pts:
        p.px(x, y, color)
    return p.finish()


def hash_seed(text: str) -> int:
    """A stable small number from a name (Python's own hash changes between runs)."""
    return sum((i + 1) * ord(c) for i, c in enumerate(text)) % 9973


def radio(on: bool, state: str) -> Image.Image:
    """A 16x16 pad with a lamp slot: oak when off, a moss-green lit pad when on; `state` is '', 'hover' or 'pressed'."""
    if on:
        face, lit, dark = (GREEN[3], GREEN[4], GREEN[1]) if state != "hover" else (GREEN[4], rgb("#c0dc9c"), GREEN[2])
    elif state == "pressed":
        face, lit, dark = WOOD[1], WOOD[2], WOOD[0]
    elif state == "hover":
        face, lit, dark = PALE_WOOD[2], PALE_WOOD[4], PALE_WOOD[0]
    else:
        face, lit, dark = WOOD[3], WOOD[4], WOOD[1]
    p = Pix(16, 16)
    p.paste(plaque(16, 16, face, lit, dark, pressed=state == "pressed", seed=hash_seed(f"radio{on}{state}")), 0, 0)
    slot = GREEN[0] if on else WINE[1]
    p.rect(6, 6, 4, 3, slot)
    p.hline(6, 6, 4, SHADOW)
    p.hline(6, 8, 4, GREEN[2] if on else WINE[2])
    return p.finish()


def small_plate(w: int, h: int, state: str) -> Image.Image:
    """The tiny nine-slice buttons of the machine windows: 'normal', 'hover' (lit) and 'pressed' (inset)."""
    face, lit, dark = {
        "normal": (WOOD[2], WOOD[4], WOOD[1]),
        "hover": (WOOD[3], PALE_WOOD[3], WOOD[1]),
        "pressed": (WOOD[1], WOOD[1], WOOD[3]),
    }[state]
    return plaque(w, h, face, lit, dark, grain=False, pressed=state == "pressed")


def slider_thumb(hover: bool) -> Image.Image:
    """The 16x8 slider handle: an oak block with three grip grooves."""
    face, lit, dark = (WOOD[3], PALE_WOOD[3], WOOD[1]) if hover else (WOOD[2], WOOD[4], WOOD[1])
    p = Pix(16, 8)
    p.paste(plaque(16, 8, face, lit, dark, grain=False), 0, 0)
    for x in (4, 7, 10):
        p.vline(x, 2, 4, SHADOW)
        p.vline(x + 1, 2, 4, lit)
    return p.finish()


def slider_track() -> Image.Image:
    """The 16x6 slider groove: a dark channel cut into the wood with a lit lower lip."""
    p = Pix(16, 6, SOOT[2])
    p.hline(0, 0, 16, SHADOW)
    p.hline(0, 1, 16, SOOT[0])
    p.hline(0, 5, 16, BRASS[1])
    p.hline(0, 4, 16, SOOT[2])
    return _finish_cut(p, cut_mask(16, 6))


def _finish_cut(p: Pix, rows: MaskRows) -> Image.Image:
    """Cuts a canvas to a silhouette without adding an outline."""
    apply_mask(p, rows)
    return p.finish()


KNOB_ROWS: Final[tuple[str, ...]] = (
    "..######..", ".########.", "##########", "##########", "##########", "##########", ".########.", ".########.",
    ".########.", ".########.", ".########.", ".########.", ".########.", ".########.", ".########.", ".########.",
    "##########", "##########", "##########", "##########", ".########.", "..######..",
)


def slider_knob() -> Image.Image:
    """The 10x22 handle of a vertical slider: oak with brass end caps and grip lines in the waist."""
    p = Pix(10, 22, WOOD[3])
    p.vline(1, 6, 10, WOOD[4])
    p.vline(8, 6, 10, WOOD[1])
    for y in (8, 10, 12, 14):
        p.hline(2, y, 6, SHADOW)
        p.hline(2, y + 1, 6, WOOD[4])
    for y0 in (0, 16):
        p.rect(0, y0, 10, 6, BRASS[2])
        p.hline(0, y0, 10, BRASS[4])
        p.hline(0, y0 + 5, 10, BRASS[1])
        p.vline(0, y0, 6, BRASS[3])
        p.vline(9, y0, 6, BRASS[1])
    return outlined(p, KNOB_ROWS)


def screen(light: bool) -> Image.Image:
    """A 48x16 display: an oak frame with a brass lip round a flat dark slate or a flat parchment field."""
    p = Pix(48, 16, WOOD[3])
    p.rect(2, 2, 44, 12, PARCHMENT[3] if light else SOOT[1])
    p.frame(2, 2, 44, 12, PARCHMENT[1] if light else SHADOW)
    p.hline(3, 3, 42, PARCHMENT[4] if light else SOOT[2]) if light else p.hline(3, 3, 42, SOOT[0])
    p.hline(1, 1, 46, WOOD[4])
    p.vline(1, 1, 14, WOOD[4])
    p.hline(1, 14, 46, WOOD[1])
    p.vline(46, 1, 14, WOOD[1])
    p.hline(2, 13, 44, BRASS[2])
    p.vline(45, 2, 12, BRASS[2])
    p.px(1, 1, BRASS[3])
    p.px(46, 1, BRASS[3])
    p.px(1, 14, BRASS[3])
    p.px(46, 14, BRASS[3])
    return outlined(p, cut_mask(48, 16))


def push_frame() -> Image.Image:
    """The 16x16 frame round a push button: an oak ring with a bevel and an open middle."""
    rows = ["..############.." if y in (0, 15) else ".##############." if y in (1, 14) else
            ("####........####" if 4 <= y <= 11 else "################") for y in range(16)]
    p = Pix(16, 16, WOOD[3])
    p.rect(0, 0, 16, 16, WOOD[3])
    p.hline(0, 2, 16, WOOD[4])
    p.vline(0, 2, 12, WOOD[4])
    p.hline(0, 13, 16, WOOD[1])
    p.vline(15, 2, 12, WOOD[1])
    p.frame(3, 3, 10, 10, WOOD[0])
    apply_mask(p, rows)
    p.outline(SHADOW, inside=True)
    for y in range(4, 12):
        for x in range(4, 12):
            p.px(x, y, CLEAR)
    return p.finish()


RING10: Final[tuple[str, ...]] = (
    "...####...", "..######..", ".##....##.", "##......##", "##......##", "##......##", "##......##", ".##....##.",
    "..######..", "...####...",
)
RING18: Final[tuple[str, ...]] = (
    ".......####.......", ".....########.....", "...############...", "..#####....#####..", "..###........###..",
    ".###..........###.", ".###..........###.", "###............###", "###............###", "###............###",
    "###............###", ".###..........###.", ".###..........###.", "..###........###..", "..#####....#####..",
    "...############...", ".....########.....", ".......####.......",
)


def ring(rows: MaskRows, outer: Color, inner: Color, mid: Color) -> Image.Image:
    """A ring cut to `rows`: bright outer rim, darker inner rim, and `mid` between."""
    h, w = len(rows), len(rows[0])
    p = Pix(w, h)
    s = inside_set(rows)
    for x, y in s:
        p.px(x, y, mid)
    for x, y in s:
        near = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if any(q not in s and 0 <= q[0] < w and 0 <= q[1] < h for q in near):
            p.px(x, y, inner)                       # next to the hole
        elif any(not (0 <= q[0] < w and 0 <= q[1] < h) or (q not in s and not _inside_hole(q, rows)) for q in near):
            p.px(x, y, outer)
    return p.finish()


def _inside_hole(q: tuple[int, int], rows: MaskRows) -> bool:
    """True for a transparent pixel that lies inside the ring (not outside its outer edge)."""
    x, y = q
    if not (0 <= y < len(rows) and 0 <= x < len(rows[0])):
        return False
    row = rows[y]
    return "#" in row[:x] and "#" in row[x + 1:]


def indicator_ring() -> Image.Image:
    """The 10x10 ring of a status light: brass with a dark inner rim."""
    return ring(RING10, BRASS[3], BRASS[0], BRASS[2])


def big_ring() -> Image.Image:
    """The 18x18 ring (a radial selector): brass outside, ember red inside."""
    return ring(RING18, BRASS[3], EMBER, BRASS[2])


def thumb_bar(lit: bool) -> Image.Image:
    """An 8x16 vertical block split in a dark upper and lighter lower half (a two-state key), wine red; brighter if lit."""
    r = RED
    top, bottom = (r[1], r[2]) if not lit else (r[2], r[4])
    p = Pix(8, 16, top)
    p.rect(0, 8, 8, 8, bottom)
    p.frame(0, 0, 8, 16, SHADOW)
    p.hline(1, 1, 6, mix(top, (255, 220, 160), 0.25))
    p.hline(1, 8, 6, SHADOW)
    p.hline(1, 9, 6, mix(bottom, (255, 220, 160), 0.25))
    return p.finish()


PIN_ROWS: Final[tuple[str, ...]] = (
    "...##...", "...##...", "...##...", "...##...", "..####..", ".######.", "########", "########", "########",
    "########", ".######.", "..####..",
)


def pin() -> Image.Image:
    """The 8x12 marker pin: a brass needle that ends in a round head with a dark eye."""
    p = Pix(8, 12, BRASS[2])
    p.rect(3, 0, 2, 4, BRASS[3])
    p.rect(3, 6, 2, 3, BRASS[0])
    p.hline(2, 7, 1, BRASS[4])
    p.px(1, 7, BRASS[4])
    for y in range(4, 12):
        p.px(7, y, BRASS[1])
    p.hline(2, 11, 4, BRASS[1])
    return outlined(p, PIN_ROWS)


def stop_square() -> Image.Image:
    """The 16x16 stop key: a wine-red pad in a brass-edged oak frame."""
    p = Pix(16, 16, WOOD[3])
    p.frame(0, 0, 16, 16, BRASS[2])
    p.bevel(1, 1, 14, 14, BRASS[4], BRASS[1])
    p.rect(3, 3, 10, 10, RED[2])
    p.hline(3, 3, 10, RED[4])
    p.vline(3, 3, 10, RED[3])
    p.hline(3, 12, 10, RED[0])
    p.vline(12, 3, 10, RED[1])
    return outlined(p, cut_mask(16, 16))


def toggle(track: Ramp, knob: Ramp) -> Image.Image:
    """A 32x16 toggle switch: a pill-shaped brass-rimmed channel filled with the track colour and a round peg at the
    left end."""
    rows = pill_mask(32, 16)
    p = Pix(32, 16, track[3])
    p.hline(0, 3, 32, track[4])
    p.hline(0, 12, 32, track[2])
    apply_mask(p, rows)
    p.outline(SHADOW, inside=True)
    _, rim = rim_sets(rows)
    paint(p, rim, BRASS[2])
    p.hline(10, 2, 14, BRASS[3])
    # the peg
    p.ellipse(2, 2, 12, 12, SHADOW)
    p.ellipse(3, 3, 10, 10, knob[3])
    p.hline(5, 3, 4, knob[4])
    p.px(4, 4, knob[4])
    p.hline(5, 12, 5, knob[1])
    p.px(11, 10, knob[1])
    return p.finish()


GAUGE: Final[tuple[tuple[int, int, Ramp], ...]] = (
    (0, 7, RED), (8, 6, OCHRE), (15, 6, BRASS), (22, 20, GREEN),
)


def meter() -> Image.Image:
    """The 6x42 level gauge: four separate rounded cells, red at the top through amber and brass to green."""
    p = Pix(6, 42)
    for y0, h, r in GAUGE:
        rows = ["#" * 6] * h
        rows[0] = ".####."
        rows[-1] = ".####."
        cell = Pix(6, h, r[3])
        cell.hline(1, 1, 4, r[4])
        cell.vline(1, 1, h - 2, r[4])
        cell.vline(4, 1, h - 2, r[2])
        apply_mask(cell, rows)
        cell.outline(IRON[3], inside=True)
        p.paste(cell, 0, y0)
    # the last green cell runs to the bottom row; the first starts at row 0: nothing to join
    return p.finish()


# ---------------------------------------------------------------------------------------------- the rest of the outer chrome


def titled_edge(w: int, h: int, rows: MaskRows) -> Image.Image:
    """A window's title tab, cut to `rows`: an oak band with a lit brass line under a dark outline on its top and
    slanted edges (its bottom runs into the window)."""
    p = Pix(w, h, WOOD[3])
    p.rect(0, 0, w, h, WOOD[3])
    s = inside_set(rows)
    for x, y in s:
        up = (x, y - 1) not in s
        slant = (x - 1, y) not in s and x > 0 or (x + 1, y) not in s and x < w - 1
        if up or slant:
            p.px(x, y, SHADOW)
        elif ((x, y - 1) not in s) or any((x + dx, y + dy) not in s and 0 <= x + dx < w and y + dy >= 0
                                           for dx, dy in ((0, -1), (-1, 0), (1, 0))):
            p.px(x, y, WOOD[4])
    for x, y in s:
        if p.get(x, y)[:3] == WOOD[3][:3] and (x, y - 1) in s and p.get(x, y - 1)[:3] == SHADOW[:3]:
            p.px(x, y, BRASS[3])
    apply_mask(p, rows)
    return p.finish()


TAB_SMALL: Final[tuple[str, ...]] = ("..############..", ".##############.", "################")
TAB_NEW: Final[tuple[str, ...]] = (
    "......######################....", "......######################....", "....##########################..",
    "....##########################..", "..##############################", "..##############################",
    "################################", "################################",
)


def scroll_track() -> Image.Image:
    """The 7x16 scroll groove: a dark channel with rounded ends and a lit stone lip."""
    p = Pix(7, 16, STONE[2])
    p.vline(1, 2, 12, STONE[1])
    p.vline(5, 2, 12, STONE[3])
    rows = ["..###..", ".#####."] + ["#######"] * 12 + [".#####.", "..###.."]
    apply_mask(p, rows)
    p.outline(SHADOW, inside=True)
    return p.finish()


def scroll_thumb() -> Image.Image:
    """The 5x10 scroll handle: a brass pill with a lit left edge."""
    rows = [".###."] + ["#####"] * 8 + [".###."]
    p = Pix(5, 10, BRASS[2])
    p.vline(1, 1, 8, BRASS[4])
    p.vline(3, 1, 8, BRASS[1])
    apply_mask(p, rows)
    p.outline(SHADOW, inside=True)
    p.hline(1, 0, 3, BRASS[3])
    return p.finish()


def grip(pressed: bool) -> Image.Image:
    """The 6x6 corner grip of a resizable window: an iron wedge, lit on its slanting edge (darker when held)."""
    rows = ("....##", "...###", "..####", ".#####", "######", "######")
    p = Pix(6, 6, BRASS[2] if not pressed else BRASS[1])
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                edge = row.index("#") == x
                p.px(x, y, (BRASS[4] if not pressed else BRASS[3]) if edge else (BRASS[2] if not pressed else BRASS[1]))
    p.hline(0, 5, 6, BRASS[0])
    p.vline(5, 0, 6, BRASS[0])
    apply_mask(p, rows)
    return p.finish()


def text_field() -> Image.Image:
    """The 32x16 text well: a dark recessed field, shaded on its upper left, with a lit lower lip."""
    rows = cut_mask(32, 16, 2)
    p = Pix(32, 16, SOOT[1])
    p.hline(2, 1, 28, SOOT[0])
    p.vline(1, 2, 12, SOOT[0])
    p.hline(2, 14, 28, WOOD[2])
    p.vline(30, 2, 12, WOOD[1])
    apply_mask(p, rows)
    p.outline(SHADOW, inside=True)
    return p.finish()


# ---------------------------------------------------------------------------------------------- machinery bits


def machinery() -> dict[str, Image.Image]:
    """The small pieces of the machine windows, by the game's file name."""
    out: dict[str, Image.Image] = {}
    out["bevel_frame"] = Pix(4, 4, STONE[2]).finish()
    bf = Pix(4, 4, STONE[2])
    bf.hline(0, 0, 4, STONE[3])
    bf.vline(0, 0, 4, STONE[3])
    bf.hline(0, 3, 4, STONE[0])
    bf.vline(3, 0, 4, STONE[0])
    out["bevel_frame"] = bf.finish()
    out["button_normal"] = small_plate(6, 6, "normal")
    out["button_hover"] = small_plate(6, 6, "hover")
    out["button_pressed"] = small_plate(8, 8, "pressed")
    cell = Pix(16, 16)
    cell.rect(1, 1, 14, 14, (*SOOT[1], 204))
    cell.hline(1, 1, 14, (*SOOT[0], 204))
    cell.vline(1, 1, 14, (*SOOT[0], 204))
    out["cell"] = cell.finish()
    out["flat"] = Pix(2, 2, LINEN5[4]).finish()
    note = ("########", "#.####.#", "##.##.##", "###..###", "########", "#......#", "#.####.#", "########")
    n = Pix(8, 8)
    for y, row in enumerate(note):
        for x, ch in enumerate(row):
            n.px(x, y, SOOT[2] if ch == "#" else (*BRASS[2], 255))
    n.rect(2, 5, 4, 1, BRASS[2])
    nm = Pix(8, 8)
    for x, y in inside_set(("########", "#......#", "########", "########", "########", "########", "########", "########")):
        nm.px(x, y, SOOT[2])
    nm.hline(1, 1, 6, SOOT[2])
    nm.px(1, 1, BRASS[3])
    nm.rect(2, 3, 4, 1, BRASS[3])
    nm.rect(2, 5, 3, 1, BRASS[3])
    nm.px(6, 6, EMBER)
    out["icon_note"] = nm.finish()
    power = ("..###.....###..", "..#....#....#..", "#.#...###...#.#", "#.#..#####..#.#", "#.#...###...#.#",
             "..#....#....#..", "..###.....###..")
    pw = Pix(15, 7)
    for y, row in enumerate(power):
        for x, ch in enumerate(row):
            if ch == "#":
                pw.px(x, y, FLAME[2] if 4 <= x <= 10 and 1 <= y <= 5 else IRON[3])
    out["icon_power"] = pw.finish()
    intake = Pix(4, 4, IRON[1])
    intake.hline(0, 0, 4, IRON[3])
    intake.hline(0, 2, 4, IRON[3])
    intake.hline(0, 3, 4, IRON[0])
    out["intake"] = intake.finish()
    notch = Pix(4, 4, LINEN5[4])
    for x, y in ((0, 0), (3, 0), (0, 3), (3, 3)):
        notch.px(x, y, CLEAR)
    out["plate_notched"] = notch.finish()
    tab = Pix(4, 4, LINEN5[4])
    tab.px(0, 0, CLEAR)
    tab.px(3, 0, CLEAR)
    out["tab_plate"] = tab.finish()
    pf = Pix(6, 6, WOOD[2])
    pf.rect(2, 2, 2, 2, SOOT[0])
    pf.hline(1, 1, 4, WOOD[1])
    pf.vline(1, 1, 4, WOOD[1])
    pf.hline(1, 4, 4, WOOD[4])
    pf.vline(4, 1, 4, WOOD[4])
    pf.rect(2, 2, 2, 2, SOOT[0])
    apply_mask(pf, cut_mask(6, 6))
    pf.outline(SHADOW, inside=True)
    out["progress_frame"] = pf.finish()
    for key, on, state in (("radio_off", False, ""), ("radio_off_hover", False, "hover"), ("radio_on", True, ""),
                           ("radio_on_hover", True, "hover"), ("radio_pressed", False, "pressed")):
        out[key] = radio(on, state)
    out["slider_thumb_normal"] = slider_thumb(False)
    out["slider_thumb_hover"] = slider_thumb(True)
    vent = Pix(2, 3, IRON[1])
    vent.hline(0, 0, 2, IRON[3])
    vent.hline(0, 2, 2, IRON[0])
    out["vent"] = vent.finish()
    return out


# ---------------------------------------------------------------------------------------------- sprite tables and sheets

PLAYBACK: Final[tuple[tuple[str, str], ...]] = (
    ("next", "next"), ("previous", "previous"), ("play", "play"), ("pause", "pause"), ("default", ""),
    ("up", "up"), ("down", "down"),
)
STATE_NAMES: Final[tuple[str, ...]] = ("", "_hl", "_c", "_d")
HUE_ORDER: Final[tuple[str, ...]] = ("blue", "red", "green", "cyan", "orange", "purple")
LAMP_ORDER: Final[tuple[str, ...]] = ("red", "orange", "yellow", "green", "cyan", "purple", "white")
TOGGLES: Final[tuple[tuple[tuple[int, int], Ramp, Ramp], ...]] = (
    ((32, 368), GREEN, GREEN), ((32, 400), OCHRE, LINEN5), ((32, 432), LINEN5, RED),
    ((80, 432), GREEN, LINEN5), ((128, 432), BLUE, BLUE), ((79, 464), GREEN, LINEN5),
)


def button_sprite(kind: str, state: str) -> Image.Image:
    """One of the 16x16 playback-style buttons; 'default' is the blank plaque."""
    return square_button(kind if kind != "default" else "none", state)




# ---------------------------------------------------------------------------------------------- assembling


def sheet_inner() -> Image.Image:
    """The 481x496 sheet of `elements_inner`: every control of the options and machine windows at the game's offsets."""
    p = Pix(481, 496)
    for row, hue in enumerate(HUE_ORDER):
        p.paste(tinted_button(hue, False), 0, 32 * row)
        p.paste(tinted_button(hue, True), 32, 32 * row)
    for row, (_, kind) in enumerate(PLAYBACK):
        for col, state in enumerate(STATE_NAMES):
            p.paste(button_sprite(kind or "default", state), 64 + 32 * col, 96 + 32 * row)
    p.paste(push_frame(), 144, 0)
    p.paste(indicator_ring(), 147, 35)
    for i, hue in enumerate(LAMP_ORDER):
        p.paste(lamp(hue, True), 181 + 32 * i, 5)
        p.paste(lamp("dark" if hue == "white" else hue, False), 181 + 32 * i, 37)
    p.paste(slider_track(), 176, 69)
    p.paste(slider_knob(), 211, 61)
    p.paste(screen(True), 0, 192)
    p.paste(screen(False), 0, 224)
    for (x, y), track, knob in TOGGLES:
        p.paste(toggle(track, knob), x, y)
    p.paste(meter(), 357, 437)
    p.paste(big_ring(), 463, 447)
    p.paste(thumb_bar(False), 404, 448)
    p.paste(thumb_bar(True), 436, 448)
    p.paste(pin(), 404, 480)
    p.paste(stop_square(), 432, 480)
    return p.finish()


def outer_pieces() -> dict[str, Image.Image]:
    """The pictures of the `elements_outer` group, by file name (without the group prefix)."""
    return {
        "background_fill": background_fill(),
        "border_bottom_resizable_button": grip(False),
        "border_bottom_resizable_button_down": grip(True),
        "border_outside_top_rounded": titled_edge(16, 3, TAB_SMALL),
        "border_outside_top_rounded_new": titled_edge(32, 8, TAB_NEW),
        "border_right_scrollbar": scroll_track(),
        "border_right_scrollbar_button": scroll_thumb(),
        "border_top_button_x": square_button("close", ""),
        "border_top_button_x_inverted": square_button("close", "_hl"),
        "border_top_button_x_select": square_button("close", "_c"),
        "text_background_in": text_field(),
    }


def sheet_outer() -> Image.Image:
    """The 213x72 sheet of `elements_outer`: title tabs, close buttons, scrollbar, text well, fill and corner grips."""
    pieces = outer_pieces()
    p = Pix(213, 72)
    for name, (x, y) in (
        ("border_outside_top_rounded", (0, 0)), ("border_top_button_x", (80, 0)),
        ("border_top_button_x_inverted", (112, 0)), ("border_top_button_x_select", (144, 0)),
        ("border_right_scrollbar", (176, 0)), ("border_right_scrollbar_button", (208, 0)),
        ("text_background_in", (32, 32)), ("background_fill", (80, 32)),
        ("border_bottom_resizable_button", (112, 32)), ("border_bottom_resizable_button_down", (144, 32)),
        ("border_outside_top_rounded_new", (0, 64)),
    ):
        p.paste(pieces[name], x, y)
    return p.finish()


def sheet_background() -> Image.Image:
    """The 124x70 sheet of window-colour tiles: a row each of framed (border), plain and grid tiles, six colours across."""
    p = Pix(124, 70)
    for col, kind in enumerate(FRAME_NAMES):
        x = 18 * col
        p.paste(background(kind, "border"), x, 18)
        p.paste(background(kind, "plain"), x, 36)
        p.paste(background(kind, "grid"), x, 54)
    p.paste(highlight_white(), 18, 0)
    p.paste(background("white", "plain"), 108, 0)
    p.paste(pinned_top(), 108, 18)
    return p.finish()


def build_assets() -> dict[str, Callable[[], Image.Image]]:
    """Every picture of the group by its catalog file name."""
    a: dict[str, Callable[[], Image.Image]] = {}

    def add(name: str, make: Callable[[], Image.Image]) -> None:
        a[name] = make

    add("window~background@background.png", sheet_background)
    for kind in FRAME_NAMES:
        add(f"window~background@{kind}.png", lambda k=kind: background(k, "plain"))  # type: ignore[misc]
        add(f"window~background@border_{kind}.png", lambda k=kind: background(k, "border"))  # type: ignore[misc]
        add(f"window~background@grid_{kind}.png", lambda k=kind: background(k, "grid"))  # type: ignore[misc]
    add("window~background@highlight_white.png", highlight_white)
    add("window~background@pinned_top.png", pinned_top)
    add("window~background_fill@background_fill.png", background_fill)

    add("window~border-export.png", lambda: border_sheet(False))
    add("window~borderold@borderOld.png", lambda: border_sheet(True))
    for key in edge_pieces():
        add(f"window~border@{key}.png", lambda k=key: edge_pieces()[k])  # type: ignore[misc]

    for hue in HUE_ORDER:
        suffix = "" if hue == "blue" else f"_{hue}"
        # the game's plain 'button_up' is the first (blue-grey) one; its 'blue' sibling is the cyan one
        name = {"blue": "", "cyan": "_blue"}.get(hue, suffix)
        add(f"window~elements_inner@button_up{name}.png", lambda h=hue: tinted_button(h, False))  # type: ignore[misc]
        add(f"window~elements_inner@button_disabled{name}.png", lambda h=hue: tinted_button(h, True))  # type: ignore[misc]
    for dark_name, hue in (("", "dark"), ("_cyan", "cyan"), ("_green", "green"), ("_orange", "orange"),
                           ("_purple", "purple"), ("_red", "red"), ("_yellow", "yellow")):
        add(f"window~elements_inner@dark{dark_name}.png", lambda h=hue: lamp(h, False))  # type: ignore[misc]
        light_hue = "white" if hue == "dark" else hue
        add(f"window~elements_inner@light{dark_name}.png", lambda h=light_hue: lamp(h, True))  # type: ignore[misc]
    for base, kind in (("default", "none"), ("down", "down"), ("next", "next"), ("pause", "pause"),
                       ("previous", "previous"), ("up", "up")):
        for state in STATE_NAMES:
            add(f"window~elements_inner@{base}{state}.png", lambda k=kind, s=state: square_button(k, s))  # type: ignore[misc]
    for state in ("", "_hl", "_c"):
        add(f"window~elements_inner@play{state}.png", lambda s=state: square_button("play", s))  # type: ignore[misc]
    add("window~elements_inner@playd.png", lambda: square_button("play", "_d"))
    add("window~elements_inner@elements_inner.png", sheet_inner)
    add("window~elements_inner@indicator_frame.png", indicator_ring)
    add("window~elements_inner@push_button_frame.png", push_frame)
    add("window~elements_inner@screen_dark.png", lambda: screen(False))
    add("window~elements_inner@screen_light.png", lambda: screen(True))
    add("window~elements_inner@slider_background.png", slider_track)
    add("window~elements_inner@slider_button.png", slider_knob)

    add("window~elements_outer@elements_outer.png", sheet_outer)
    for key in outer_pieces():
        add(f"window~elements_outer@{key}.png", lambda k=key: outer_pieces()[k])  # type: ignore[misc]
    for key in machinery():
        add(f"window~machinery~{key}.png", lambda k=key: machinery()[k])  # type: ignore[misc]
    return a


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = build_assets()
