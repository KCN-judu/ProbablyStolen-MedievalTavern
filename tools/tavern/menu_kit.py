"""Building blocks for the menu pictures: plates, bars, grooves and bitmap icons, written once and used by every control.

A control that has states (normal, hover, pressed, ...) is always drawn by the same function with a different `Tone`, so
its shape stays the same and only the colours change: normal is oak and dull brass, hover is lit brass with an amber
rim, pressed is sunk and dark, checked/purchased is moss, refused is wine red.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final, NamedTuple

from PIL import Image

from materials import planks, tone
from palette import BRASS, FLAME, IRON, MOSS, OAK, SHADOW, WINE, WOOD
from pix import Color, Pix, Ramp, mix, scale_ramp


class Tone(NamedTuple):
    """The colours of one state of a control."""

    rim: Ramp           # the frame, dark to light
    face: Color         # the inside
    accent: Color       # the fine line inside the frame, and icons
    glow: Color | None  # a warm light laid over the inside's edge, or None


FACE: Final[Color] = mix(OAK[0], SHADOW, 0.35)
NORMAL: Final = Tone(OAK, FACE, BRASS[2], None)
HOVER: Final = Tone(scale_ramp(OAK, 0.1), mix(FACE, FLAME[0], 0.22), FLAME[3], FLAME[0])
PRESSED: Final = Tone(scale_ramp(OAK, -0.35), SHADOW, BRASS[1], None)
CHECKED: Final = Tone(OAK, mix(FACE, MOSS[1], 0.5), MOSS[3], None)
REFUSED: Final = Tone(WINE, mix(FACE, WINE[0], 0.6), WINE[3], None)
DISABLED: Final = Tone(scale_ramp(OAK, -0.2), mix(FACE, OAK[1], 0.5), IRON[2], None)
STATES: Final = {"n": NORMAL, "h": HOVER, "p": PRESSED, "c": CHECKED, "r": REFUSED, "d": DISABLED}


def cut_outline(w: int, h: int, cut: int) -> list[tuple[int, int]]:
    """The corners of a rectangle with its four corners cut off by `cut` pixels (a plain rectangle when cut is 0)."""
    if cut <= 0:
        return [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    return [(cut, 0), (w - 1 - cut, 0), (w - 1, cut), (w - 1, h - 1 - cut), (w - 1 - cut, h - 1), (cut, h - 1), (0, h - 1 - cut), (0, cut)]


def plate(w: int, h: int, t: Tone = NORMAL, thick: int = 2, cut: int = 1, accent: bool = True, studs: bool = False,
          seed: int = 0, grain: bool = True, hollow: bool = False, wood: float | None = None) -> Pix:
    """A framed plate: a one-pixel `SHADOW` outline, a frame of `thick` pixels lit at its top left, a face that sits
    below it (shaded along its top and left, lit along its bottom and right), a fine accent line, and corner studs.
    With `hollow` the face is left transparent, so the plate is only a frame (a slot border over an item)."""
    p = Pix(w, h, seed=seed)
    rim = list(t.rim) + [t.rim[-1]] * (5 - len(t.rim))        # a four-tone ramp has no fifth tone: repeat its lightest
    t = t._replace(rim=rim)
    p.rect(0, 0, w, h, SHADOW)
    p.rect(1, 1, w - 2, h - 2, t.rim[2])
    p.hline(1, 1, w - 2, t.rim[4])
    p.vline(1, 1, h - 2, t.rim[3])
    p.hline(1, h - 2, w - 2, t.rim[0])
    p.vline(w - 2, 1, h - 2, t.rim[1])
    i = 1 + thick
    iw, ih = w - 2 * i, h - 2 * i
    if iw > 0 and ih > 0:
        p.rect(i, i, iw, ih, t.face)
        if wood is not None:                                   # a face of narrow boards, lighter the smaller `wood` is
            board_face(p, i, i, iw, ih, dark=wood, plank=max(6, ih // 2))
        if grain and iw * ih > 60:
            p.speckle(i, i, iw, ih, (mix(t.face, SHADOW, 0.4), tone(t.face, 0.08)), 0.04)
        p.hline(i, i, iw, mix(t.face, SHADOW, 0.55))
        p.vline(i, i, ih, mix(t.face, SHADOW, 0.35))
        p.hline(i, i + ih - 1, iw, tone(t.rim[1], 0.1))
        p.vline(i + iw - 1, i + 1, ih - 1, tone(t.rim[1], 0.1))
        if t.glow is not None and ih > 6:
            for k, d in enumerate((0.05, 0.1, 0.16, 0.22)):
                band = min(3, (ih - 2) // 8 + 1)
                p.dither(i + 1, i + ih - 1 - band * (k + 1), iw - 2, band, t.glow, d)
        if accent and iw > 6 and ih > 6:
            ax, ay, aw, ah = i + 1, i + 1, iw - 2, ih - 2
            p.hline(ax, ay, aw, t.accent)
            p.hline(ax, ay + ah - 1, aw, t.accent)
            p.vline(ax, ay, ah, t.accent)
            p.vline(ax + aw - 1, ay, ah, t.accent)
        if hollow:
            p.erase(i, i, iw, ih)
    if studs and w > 8 and h > 8:
        for sx, sy in ((2, 2), (w - 4, 2), (2, h - 4), (w - 4, h - 4)):
            p.px(sx, sy, BRASS[4])
            p.px(sx + 1, sy, BRASS[2])
            p.px(sx, sy + 1, BRASS[2])
            p.px(sx + 1, sy + 1, BRASS[0])
    if cut > 0:
        p.clip(cut_outline(w, h, cut))
        p.outline(SHADOW, inside=True)
    return p


def board_face(p: Pix, x: int, y: int, w: int, h: int, dark: float = 0.55, plank: int = 14) -> None:
    """Dark boards for the face of a big panel: the wood ramp pushed toward black so light text reads on it."""
    planks(p, x, y, w, h, scale_ramp(WOOD, -dark), plank=plank, nails=False)
    if w * h > 20000:
        p.dither(x, y, w, h, SHADOW, 0.25)


def big_panel(w: int, h: int, t: Tone = NORMAL, header: int = 0, seed: int = 0, thick: int = 4, cut: int = 2) -> Pix:
    """A window: a plank face in an oak frame with brass studs; `header` > 0 adds a strip across the top in brass-edged
    iron where a title goes (the game's window panels have such a strip)."""
    p = plate(w, h, t, thick=thick, cut=0, accent=False, studs=False, seed=seed, grain=False)
    board_face(p, 1 + thick, 1 + thick, w - 2 - 2 * thick, h - 2 - 2 * thick)
    p.rect(1 + thick, 1 + thick, w - 2 - 2 * thick, 1, SHADOW)
    p.vline(1 + thick, 1 + thick, h - 2 - 2 * thick, SHADOW)
    p.rect(2 + thick, 2 + thick, w - 4 - 2 * thick, 1, mix(WOOD[0], SHADOW, 0.5))
    if header:
        p.rect(1, 1, w - 2, header, IRON[1])
        p.hline(1, 1, w - 2, IRON[3])
        p.hline(1, header, w - 2, SHADOW)
        p.hline(1, header - 1, w - 2, t.accent)
        for x in range(8, w - 8, 12):
            p.px(x, 1 + header // 2 - 1, BRASS[3])
            p.px(x + 1, 1 + header // 2, SHADOW)
    for sx, sy in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
        p.rect(sx, sy, 2, 2, BRASS[2])
        p.px(sx, sy, BRASS[4])
        p.px(sx + 1, sy + 1, BRASS[0])
    if cut:
        p.clip(cut_outline(w, h, cut))
        p.outline(SHADOW, inside=True)
    return p


def bar(w: int, h: int, fill: Color, edge: Color = SHADOW, lit: bool = True) -> Pix:
    """A flat strip of one colour with an outline, a lit top row and a shaded bottom row (a groove's contents, a fill)."""
    p = Pix(w, h)
    p.rect(0, 0, w, h, edge)
    if w > 2 and h > 2:
        p.rect(1, 1, w - 2, h - 2, fill)
        if lit and h > 3:
            p.hline(1, 1, w - 2, tone(fill, 0.22))
            p.hline(1, h - 2, w - 2, tone(fill, -0.3))
    return p


def groove(w: int, h: int, vertical: bool = False) -> Pix:
    """A channel cut in wood (the track of a slider or a scroll bar): dark, shaded on the side the light comes from,
    with a thin lit lip on the opposite side."""
    p = Pix(w, h)
    p.rect(0, 0, w, h, SHADOW)
    if vertical and w > 2:
        p.rect(1, 0, w - 2, h, OAK[0])
        p.vline(1, 0, h, SHADOW)
        p.vline(w - 1, 0, h, OAK[3]) if w > 3 else None
    elif h > 2:
        p.rect(0, 1, w, h - 2, OAK[0])
        p.hline(0, 1, w, SHADOW)
        p.hline(0, h - 1, w, OAK[3]) if h > 3 else None
    return p


# ---------------------------------------------------------------------------------------------- bitmap icons


ICONS: Final[dict[str, Sequence[str]]] = {
    "tick": ["........##", ".......###", "......###.", "##...###..", "###.###...", ".#####....", "..###.....", "...#......"],
    "cross": ["##......##", "###....###", ".###..###.", "..######..", "...####...", "..######..", ".###..###.", "###....###", "##......##"],
    "trash": ["...###....", "##########", ".########.", ".#.#..#.#.", ".#.#..#.#.", ".#.#..#.#.", ".#.#..#.#.", "..######.."],
    "copy": ["#######...", "##...##...", "##...#####", "##...##..#", "#######..#", "...##....#", "...##....#", "...#######"],
    "magnify": ["..####....", ".######...", "##....##..", "##....##..", "##....##..", ".######...", "..#####...", ".....###..", "......###.", ".......###"],
    "gear": ["....##....", ".##.##.##.", ".########.", "..##..##..", "###....###", "###....###", "..##..##..", ".########.", ".##.##.##.", "....##...."],
    "warning": ["....##....", "...####...", "...#..#...", "..##..##..", "..##..##..", ".###..###.", ".###..###.", "####..####", "##########", "##########"],
    "folder": ["#####.....", "##########", "##########", "##########", "##########", "##########", "##########"],
    "lock": ["..#####...", ".##...##..", ".##...##..", "#########.", "#########.", "####.####.", "####.####.", "#########.", "#########."],
    "clip": ["...####...", "#########.", "##.###.##.", "##.....##.", "##.....##.", "##...##.#.", "##..###.#.", "##.###..#.", "##.##...#.", "##......#.", "#########."],
    "chevron": ["....#", "...##", "..##.", ".##..", "##...", ".##..", "..##.", "...##", "....#"],
    "down": ["#.....#", "##...##", ".##.##.", "..###..", "...#..."],
    "arrow": ["......##", "....####", "...#####", "......##", "..#...##", ".##....#", "####....", "####....", "###.....", "####...."],
}


def icon(name: str, color: Color, scale: int = 1, flip: bool = False, light: Color | None = None, dark: Color | None = None) -> Pix:
    """A bitmap icon in `color`, its upper-left edges lit and lower-right edges shaded, with a `SHADOW` outline."""
    rows = ICONS[name]
    w, h = len(rows[0]), len(rows)
    p = Pix(w * scale + 2, h * scale + 2)
    lit = light or tone(color, 0.3)
    dim = dark or tone(color, -0.35)

    def on(x: int, y: int) -> bool:
        if flip:
            x = w - 1 - x
        return 0 <= x < w and 0 <= y < h and rows[y][x] == "#"

    for y in range(h):
        for x in range(w):
            if on(x, y):
                c = lit if not on(x - 1, y - 1) and (not on(x - 1, y) or not on(x, y - 1)) else dim if not on(x + 1, y + 1) else color
                p.rect(1 + x * scale, 1 + y * scale, scale, scale, c)
    p.outline(SHADOW)
    return p


def put_icon(p: Pix, name: str, color: Color, cx: int, cy: int, scale: int = 1, flip: bool = False) -> None:
    """Lays an icon with its centre at (cx, cy)."""
    ic = icon(name, color, scale, flip)
    p.paste(ic, cx - ic.w // 2, cy - ic.h // 2)


def scaled(p: Pix | Image.Image, factor: int) -> Image.Image:
    """A picture enlarged by a whole number with hard pixels (a 1024 pixel icon drawn on a 64 pixel grid)."""
    im = p.im if isinstance(p, Pix) else p
    return im.resize((im.width * factor, im.height * factor), Image.Resampling.NEAREST)
