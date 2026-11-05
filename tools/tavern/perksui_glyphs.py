"""The perk glyphs, one function per icon, each returning an `Ic` drawn on a logical canvas (see perksui_kit).

One icon language: bold white silhouettes, two pixel strokes, corners cut by a pixel instead of rounded, inner detail in a
single light grey, and cut-outs (clear gaps) where two parts overlap. The objects are a tavern's and a guild's: tankard,
bell, scroll, key, purse, lantern, book, flask, hammer, shield.
"""

from __future__ import annotations

from perksui_kit import G, W, Ic

CLR = (0, 0, 0, 0)

# ------------------------------------------------------------------------------------------------ shared parts


def chamfer(c: Ic, x: int, y: int, w: int, h: int) -> None:
    """Cuts the four corners of a rectangle by one pixel (the pack's corner style)."""
    for px, py in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        c.cut(px, py, 1, 1)


def box(c: Ic, x: int, y: int, w: int, h: int, col=W) -> None:
    c.rect(x, y, w, h, col)
    chamfer(c, x, y, w, h)


def heart(c: Ic, x: int, y: int, s: int = 1, col=W) -> None:
    """A 13 wide, 11 tall heart (scaled by whole numbers) with its left edge at x."""
    rows = ("..###...###..", ".#####.#####.", "#############", "#############", "#############",
            ".###########.", "..#########..", "...#######...", "....#####....", ".....###.....", "......#......")
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == "#":
                c.rect(x + i * s, y + j * s, s, s, col)


def bust(c: Ic, x: int, y: int, hood: bool = False) -> None:
    """A head and shoulders, 12 wide and 14 tall, optionally hooded (a pointed cowl round a dark face)."""
    if hood:
        c.art(x, y, ["....####....", "...######...", "..########..", "..##xxxx##..", "..##xxxx##..", "...##xx##..."])
    else:
        c.disc(x + 3, y, 6, 6)
    c.art(x, y + 6, ["...######...", ".##########.", "############", "############", "############", "############",
                     "############", "############"])


# ------------------------------------------------------------------------------------------------ 32 x 32 glyphs


