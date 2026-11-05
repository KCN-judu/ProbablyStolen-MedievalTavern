"""The new-game screens: the perk slots (a medallion for each perk, a lock for the ones not yet earned) and the
specialisation slots with the sheet of their small emblems. The shared pieces of that screen (arrows, tab, panel) are
drawn in menu_ui.py with the rest of the menu controls, from the same kit.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image

from menu_kit import HOVER, NORMAL, Tone, plate
from palette import BRASS, FLAME, IRON, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix, mix

Drawing = Callable[[], Image.Image]


def medallion(w: int, h: int, hot: bool) -> Image.Image:
    """A perk's slot: a wooden shield with a brass rim cut at the corners, a darker lip along its foot that gives it
    depth, lit amber when hovered."""
    t = HOVER if hot else NORMAL
    p = plate(w, h, Tone(t.rim, mix(OAK[1], SHADOW, 0.3), t.accent, t.glow), thick=3, cut=6, accent=True, seed=h, wood=0.3 if hot else 0.6)
    lip = Pix(w, h)
    lip.rect(4, h - 9, w - 8, 6, OAK[0])
    lip.dither(4, h - 9, w - 8, 6, SHADOW, 0.5)
    p.paste(lip, 0, 0)
    p.dither(6, 6, w - 12, 4, SHADOW, 0.5)
    p.clip([(6, 0), (w - 7, 0), (w - 1, 6), (w - 1, h - 7), (w - 7, h - 1), (6, h - 1), (0, h - 7), (0, 6)])
    p.outline(SHADOW, inside=True)
    return p.im


def node() -> Image.Image:
    """The round perk marker: a brass ring around a pale wooden disc (pale so the game's tint can colour it)."""
    p = Pix(32, 32)
    p.ellipse(0, 0, 32, 32, SHADOW)
    p.ellipse(1, 1, 30, 30, BRASS[2])
    p.ellipse(3, 3, 26, 26, BRASS[1])
    p.ellipse(4, 4, 24, 24, PALE_WOOD[3])
    p.dither(4, 14, 24, 14, PALE_WOOD[1], 0.4)
    p.dither(4, 4, 24, 5, PALE_WOOD[4], 0.5)
    for x, y in ((3, 15), (28, 15), (15, 3), (15, 28)):
        p.px(x, y, BRASS[4])
    return p.im


def specialization_slot(selected: bool) -> Image.Image:
    """A specialisation's slot: an iron-and-oak plate with cut corners and studs; lit brass when selected."""
    t = Tone(OAK, mix(OAK[1], SHADOW, 0.3), BRASS[2], None) if not selected else Tone(BRASS, mix(OAK[1], FLAME[0], 0.45), FLAME[4], FLAME[1])
    return plate(64, 64, t, thick=3, cut=6, studs=True, seed=64, wood=0.25 if selected else 0.55).im


EMBLEMS: Final[Sequence[Sequence[str]]] = (
    ["..#####..", ".#.....#.", "#.##.##.#", "#.......#", "#.#####.#", ".#.....#.", "..#####.."],            # purse
    ["...###...", "..#...#..", "..#...#..", "...###...", "....#....", "....##...", "....#....", "....###.."],          # key
    ["..####..", ".######.", "########", "##.##.##", "########", ".######.", "..####.."],                        # coin
    ["......##", ".....###", "....###.", "#..###..", ".####...", "..##....", ".#.##...", "#...#..."],             # sword
    ["...##...", "...##...", "..####..", ".######.", "########", "########", ".######."],                        # flask
    ["#######.", "#.....#.", "#.###.#.", "#.....#.", "#.###.#.", "#.....#.", "#######."],                          # scroll
    [".#####..", ".#####..", "..###...", "..###...", "..###...", "..###...", ".#####."],                          # hammer
    ["..####..", ".#.##.#.", "#.####.#", ".######.", "..####..", "...##..."],                                      # gem
    ["#######..", "##.#.##..", "##.#.##..", "##.#.##..", "##.#.##..", "#######.."],                                # book
    ["..###..#", ".#####.#", "#######.", "#######.", ".#####..", "..###..."],                                      # mug
    [".#####..", "#######.", "##.#.##.", "#######.", ".#####..", "..#.#..."],                                      # skull
    ["..##....", ".####..#", "########", ".####..#", "..##...."],                                                  # fish
)
EMBLEM_COLORS: Final[Sequence[Color]] = (
    BRASS[3], BRASS[3], BRASS[4], IRON[4], MOSS[3], PARCHMENT[3], PALE_WOOD[4], WINE[4], WINE[3], BRASS[2], PARCHMENT[2], IRON[4])


def emblem_sheet() -> Image.Image:
    """The sheet of twelve specialisation emblems, ten in the first row and two in the second, 19 pixels apart: each a
    small bitmap in its own colour on a dark round token with a brass rim."""
    sheet = Pix(190, 38)
    for i, rows in enumerate(EMBLEMS):
        cx, cy = (i % 10) * 19 + 9, (i // 10) * 19 + 9
        sheet.ellipse(cx - 8, cy - 8, 17, 17, SHADOW)
        sheet.ellipse(cx - 7, cy - 7, 15, 15, BRASS[1])
        sheet.ellipse(cx - 6, cy - 6, 13, 13, OAK[0])
        w, h = len(rows[0]), len(rows)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "#":
                    sheet.px(cx - w // 2 + x, cy - h // 2 + y, EMBLEM_COLORS[i])
    return sheet.im


ASSETS: Mapping[str, Drawing] = {
    "perk_slot_normal.64x72.png": lambda: medallion(64, 72, False),
    "perk_slot_hover.64x72.png": lambda: medallion(64, 72, True),
    "perk_n.32x32.png": node,
    "slot_normal.64x64.png": lambda: specialization_slot(False),
    "slot_selected.64x64.png": lambda: specialization_slot(True),
    "icons.190x38.png": emblem_sheet,
}
