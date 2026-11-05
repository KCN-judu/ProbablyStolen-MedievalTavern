"""Bubbles, the connector line, the road map, the guild badges and the scratch cards (catalog group `ui/in-game`)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from PIL import Image

import font
from palette import BRASS, FLAME, IRON, OAK, PARCHMENT, SHADOW, STONE, WINE, WOOD
from perksui_shape import Mask, paint, rim, thick
from pix import CLEAR, Color, Pix, Ramp, mix

CREAM: Final[Color] = (240, 225, 190)

# ---------------------------------------------------------------------------------------------- dialogue bubbles
# The sheet: 8 colours across (cells 64 px apart, the piece at x = 16 + 64 c), 5 kinds down. The shapes are the game's
# silhouettes (tail corner, rounded corners), so its cutting of the sheet still lands on whole pieces.

BASES: Final[Sequence[Color]] = ((92, 70, 66), (46, 62, 100), (70, 62, 82), (166, 84, 58), (62, 70, 44), (126, 66, 112),
                                 (46, 122, 112), (124, 48, 56))
BRIGHT: Final[Sequence[Color]] = ((150, 120, 104), (70, 100, 140), (84, 82, 98), (190, 120, 74), (90, 90, 56), (172, 118, 170),
                                  (80, 160, 146), (170, 56, 58))

COL_X: Final = tuple(16 + 64 * c for c in range(8))
KINDS: Final = {"top": (216, 40), "mid": (283, 34), "bot": (344, 40), "flat": (408, 40), "plain": (469, 40)}
CORNER: Final = (4, 2, 1, 1)
BW: Final = 48


def parchment_ramp(base: Color) -> Ramp:
    """Dyed vellum: darkest ink edge, shade, body, lit edge, highlight."""
    return (mix(base, SHADOW, 0.72), mix(base, SHADOW, 0.35), base, mix(base, CREAM, 0.22), mix(base, CREAM, 0.45))


def bubble_extents(kind: str) -> list[tuple[int, int]]:
    """For every row of a piece the first and last filled column (the piece is 48 wide)."""
    h = KINDS[kind][1]
    rows: list[tuple[int, int]] = []
    for y in range(h):
        left, right = 0, BW - 1
        if kind in ("top", "flat") and y < 6:
            right = y + 2
        elif kind in ("top", "flat"):
            k = y - 6
            if k < 4:
                right -= (4, 2, 1, 1)[k] if kind == "top" else (2, 1, 0, 0)[k]
            if kind == "top" and y >= h - 4:
                left, right = (1, BW - 2) if y < h - 2 else ((2, BW - 3) if y == h - 2 else (4, BW - 5))
            if kind == "flat" and y >= h - 3:
                right = BW - 2
        elif kind == "bot":
            if y < 4:
                left, right = CORNER[y], BW - 1 - CORNER[y]
            elif y >= 34:
                right = 7 - (y - 34)
            elif y >= 30:
                right = BW - 1 - (1, 1, 2, 4)[y - 30]
        elif kind == "mid":
            if y < 4:
                left, right = CORNER[y], BW - 1 - CORNER[y]
            elif y >= h - 4:
                k = (1, 1, 2, 4)[y - (h - 4)]
                left, right = k, BW - 1 - k
        else:  # plain
            if y < 2:
                left, right = (2, BW - 3) if y == 0 else (1, BW - 2)
            elif y >= h - 2:
                left, right = (1, BW - 2) if y == h - 2 else (2, BW - 3)
        rows.append((left, right))
    return rows


def draw_bubble(kind: str, base: Color, seed: int, lit: bool = False) -> Pix:
    """One speech scroll: dyed vellum with an ink edge, a lit upper-left rim, a shaded lower rim and a little paper grain."""
    w, h = BW, KINDS[kind][1]
    p = Pix(w, h, seed=seed)
    ramp = parchment_ramp(base)
    ext = bubble_extents(kind)
    inside = Mask(w, h)
    for y, (a, b) in enumerate(ext):
        inside.rect(a, y, b - a + 1, 1)
    def edge(x: int, y: int) -> bool:
        """The outermost ring of the silhouette: the ink line."""
        return inside.at(x, y) and not (inside.at(x - 1, y) and inside.at(x + 1, y) and inside.at(x, y - 1) and inside.at(x, y + 1))

    for y, (a, b) in enumerate(ext):
        for x in range(a, b + 1):
            if edge(x, y):
                c = ramp[0]
            elif edge(x, y - 1) or edge(x - 1, y):
                c = ramp[3]                     # the rim that faces the light
            elif edge(x, y + 1) or edge(x + 1, y):
                c = ramp[1]                     # the rim that turns away
            else:
                c = ramp[2]
            p.px(x, y, c)
    # the paper: a few lighter and darker flecks, and short horizontal fibres
    for _ in range(w * h // 40):
        x, y = 3 + p.rng.randrange(w - 6), 3 + p.rng.randrange(h - 6)
        if p.get(x, y)[:3] == ramp[2][:3]:
            p.px(x, y, ramp[3] if p.rng.random() < 0.5 else ramp[1])
    for _ in range(4):
        x, y = 4 + p.rng.randrange(w - 14), 4 + p.rng.randrange(h - 9)
        for k in range(p.rng.randrange(3, 6)):
            if inside.at(x + k, y) and p.get(x + k, y)[:3] == ramp[2][:3]:
                p.px(x + k, y, ramp[1])
    # small brass-coloured stitch dots at the four inner corners: the scroll is tacked to the board
    if kind in ("plain", "mid"):
        for cx, cy in ((4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5)):
            p.px(cx, cy, ramp[4] if lit else ramp[3])
    return p


def bubble_sheet() -> Image.Image:
    sheet = Pix(512, 512)
    for kind, (y0, _h) in KINDS.items():
        for c, x0 in enumerate(COL_X):
            base = (BRIGHT if kind == "flat" else BASES)[c]
            sheet.paste(draw_bubble(kind, base, seed=c * 11 + y0, lit=kind == "flat"), x0, y0)
    return sheet.im


# ---------------------------------------------------------------------------------------------- connector and map


def connector() -> Image.Image:
    """A strand that falls straight down the right edge, then runs down-left to the lower left corner: an iron-wire rope
    with a lit upper edge."""
    p = Pix(133, 174)
    path = [(130.5, -2), (130.5, 63), (2, 173)]
    thick(p, path, 4, IRON[2])
    # lit and shaded sides: offset copies of the path
    off = [(129, -2), (129, 63), (0, 172)]
    thick(p, off, 1, IRON[4])
    off2 = [(132, -2), (132, 64), (4, 176)]
    thick(p, off2, 1, IRON[0])
    for y in range(0, 62, 6):                       # twisted strand ticks
        p.px(130, y, IRON[3])
        p.px(131, y + 3, IRON[1])
    return p.im


ROUTES: Final = (
    # (colour, points) in the 1808x832 frame; every route is a road drawn on the dark of the map
    ((70, 88, 108), [(282, 0), (282, 276), (450, 444), (450, 832)]),
    ((108, 62, 76), [(0, 326), (456, 326), (886, 76)]),
    ((104, 74, 120), [(410, 0), (560, 76), (1342, 76), (1620, 356), (1808, 356)]),
    ((78, 98, 88), [(1342, 76), (1710, 76), (1808, 20)]),
    ((78, 98, 88), [(1342, 76), (1342, 620), (1560, 832)]),
    ((104, 74, 120), [(886, 0), (886, 76)]),
)
STATIONS: Final = ((282, 150), (560, 76), (886, 76), (1104, 76), (1342, 76), (1710, 76), (1342, 620))


def route_map() -> Image.Image:
    """Roads between waystations: each road is a dusty track (a dark bed, a coloured wheel-rut, a lighter centre) and every
    waystation a ring of stone. Everything is dim and half transparent because the game lays it behind its screens."""
    p = Pix(1808, 832)
    layer = Pix(1808, 832)
    for col, pts in ROUTES:
        thick(layer, pts, 16, mix(col, SHADOW, 0.45))
    for col, pts in ROUTES:
        thick(layer, pts, 10, col)
    for col, pts in ROUTES:
        # a thin dashed line down the middle, the cart ruts
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(0, n, 24):
                t = i / max(1, n)
                layer.rect(round(x0 + (x1 - x0) * t) - 1, round(y0 + (y1 - y0) * t) - 1, 3, 3, mix(col, CREAM, 0.4))
    for x, y in STATIONS:
        layer.ellipse(x - 17, y - 17, 34, 34, STONE[4])
        layer.ellipse(x - 13, y - 13, 26, 26, STONE[1])
        layer.ellipse(x - 9, y - 9, 18, 18, STONE[3])
    layer.im.putalpha(layer.im.getchannel("A").point(lambda a: 70 if a else 0))
    p.paste(layer, 0, 0)
    return p.im


# ---------------------------------------------------------------------------------------------- guild badges


def oval_mask(w: int, h: int, grow: int = 0) -> Mask:
    return Mask(w, h).oval(grow, grow, w - 2 * grow, h - 2 * grow)


def scale_emblem(p: Pix, cx: int, top: int, size: int, metal: Ramp = BRASS) -> None:
    """A merchant's balance: pillar, beam, two chains and two pans, with a coin in each pan."""
    s = size
    p.rect(cx - 1, top + 2, 3, s - 4, metal[2])               # pillar
    p.vline(cx - 1, top + 2, s - 4, metal[3])
    p.rect(cx - s // 3, top + s - 2, s * 2 // 3 + 1, 2, metal[1])   # foot
    p.hline(cx - s // 3, top + s - 2, s * 2 // 3 + 1, metal[2])
    bx0, bx1 = cx - s // 2, cx + s // 2
    p.hline(bx0, top + 3, bx1 - bx0 + 1, metal[3])
    p.hline(bx0, top + 4, bx1 - bx0 + 1, metal[1])
    p.px(cx, top, metal[4])
    p.rect(cx - 1, top, 3, 2, metal[3])
    for bx in (bx0, bx1):
        p.line(bx, top + 4, bx - 3, top + 4 + s // 3, metal[1])
        p.line(bx, top + 4, bx + 3, top + 4 + s // 3, metal[1])
        py = top + 4 + s // 3
        p.hline(bx - 4, py, 9, metal[3])
        p.hline(bx - 3, py + 1, 7, metal[2])
        p.hline(bx - 2, py + 2, 5, metal[1])
        p.px(bx - 1, py - 1, metal[4])
        p.px(bx, py - 1, metal[3])


def exchange_logo() -> Image.Image:
    """The shop's trading exchange: an oval guild seal of dark oak, a brass rim, two goblets and a balance between them."""
    w, h = 60, 42
    p = Pix(w, h, seed=7)
    outer = oval_mask(w, h)
    paint(p, outer, WOOD, split=0.62)
    rim_ring = oval_mask(w, h, 2)
    paint(p, rim_ring, BRASS, split=0.6)
    inner = oval_mask(w, h, 4)
    paint(p, inner, OAK)
    # a balance in the middle, a coin heap on each pan, a rosette either side
    scale_emblem(p, 30, 7, 27)
    for gx in (12, 47):
        p.ellipse(gx - 3, 18, 7, 7, BRASS[2])
        p.hline(gx - 2, 19, 3, BRASS[4])
        p.px(gx - 2, 20, BRASS[3])
        p.hline(gx - 1, 23, 4, BRASS[0])
    # tiny stars on the rim
    for x, y in ((5, 21), (54, 21)):
        p.px(x, y, BRASS[4])
    p.outline(SHADOW)
    # keep the silhouette equal to the full oval: the outline falls outside, so clip it back
    keep = Mask(w, h).oval(0, 0, w, h)
    for y in range(h):
        for x in range(w):
            if not keep.at(x, y):
                p.px(x, y, CLEAR)
    return p.im


def crest(p: Pix, cx: int, top: int) -> None:
    """A heater shield (wine and brass) with a key and a coin, laid over crossed quills."""
    shield = Mask(p.w, p.h).poly([(cx - 15, top), (cx + 15, top), (cx + 15, top + 20), (cx + 9, top + 30), (cx, top + 35),
                                  (cx - 9, top + 30), (cx - 15, top + 20)])
    rim(p, shield, SHADOW)
    paint(p, shield, BRASS)
    inner = Mask(p.w, p.h).poly([(cx - 12, top + 3), (cx + 12, top + 3), (cx + 12, top + 19), (cx + 7, top + 27), (cx, top + 31),
                                 (cx - 7, top + 27), (cx - 12, top + 19)])
    paint(p, inner, WINE, split=0.6)
    # a brass key down the middle
    p.rect(cx - 1, top + 12, 3, 17, BRASS[3])
    p.vline(cx - 1, top + 12, 17, BRASS[4])
    p.vline(cx + 1, top + 12, 17, BRASS[1])
    p.ellipse(cx - 4, top + 5, 9, 9, BRASS[3])
    p.ellipse(cx - 2, top + 7, 5, 5, WINE[1])
    p.hline(cx + 1, top + 24, 4, BRASS[3])
    p.hline(cx + 1, top + 21, 3, BRASS[3])
    p.px(cx - 3, top + 7, BRASS[4])
    # coins either side
    for sx in (-8, 8):
        p.ellipse(cx + sx - 2, top + 15, 5, 5, BRASS[3])
        p.px(cx + sx - 1, top + 16, BRASS[4])
        p.hline(cx + sx - 1, top + 19, 3, BRASS[1])


def ribbon(p: Pix, x: int, y: int, w: int, h: int, text: str) -> None:
    """A scroll banner with swallow-tail ends and lettering."""
    body = Mask(p.w, p.h).rect(x + 5, y, w - 10, h)
    left = Mask(p.w, p.h).poly([(x, y + 2), (x + 8, y + 2), (x + 8, y + h + 1), (x, y + h + 1), (x + 4, y + h // 2 + 1)])
    right = Mask(p.w, p.h).poly([(x + w - 9, y + 2), (x + w - 1, y + 2), (x + w - 5, y + h // 2 + 1), (x + w - 1, y + h + 1),
                                 (x + w - 9, y + h + 1)])
    for m in (left, right):
        rim(p, m, SHADOW)
        paint(p, m, WINE)
    rim(p, body, SHADOW)
    paint(p, body, PARCHMENT)
    p.dither(x + 5, y + 1, w - 10, h - 2, PARCHMENT[1], 0.12)
    tw = font.width(text)
    font.write(p, x + (w - tw) // 2, y + (h - 7) // 2, text, WINE[1])


def guide_logo() -> Image.Image:
    """The guide's mark: two long rules ending in a bevel, as the page's header lines, and a guild crest on a banner."""
    p = Pix(283, 116, seed=11)
    # header rules at the same place as the game's: a short bevel down at the inner end
    p.hline(3, 21, 47, BRASS[2])
    p.hline(4, 22, 47, BRASS[1])
    p.line(0, 17, 3, 20, BRASS[3])
    p.line(48, 23, 52, 25, BRASS[1])
    p.hline(232, 21, 47, BRASS[2])
    p.hline(231, 22, 47, BRASS[1])
    p.line(282, 17, 279, 20, BRASS[3])
    p.line(234, 23, 230, 25, BRASS[1])
    p.px(0, 17, BRASS[4])
    p.px(282, 17, BRASS[4])
    crest(p, 224, 56)
    ribbon(p, 186, 88, 76, 19, "GUILD")
    return p.im


# ---------------------------------------------------------------------------------------------- scratch cards

CARD_BASE: Final = (108, 52, 70)


def card_ground(seed: int) -> Pix:
    """A lottery ticket: wine-dark card with brass frame, a field of coins and stars."""
    p = Pix(180, 142, seed=seed)
    p.rect(0, 0, 180, 142, (84, 38, 58))
    p.dither(0, 0, 180, 142, (112, 56, 78), 0.28)
    rng = p.rng
    for k in range(-142, 180, 38):                        # rays
        p.line(k, 142, k + 142, 0, (98, 46, 66))
    for _ in range(26):                                   # gold coins
        x, y = rng.randrange(6, 168), rng.randrange(6, 130)
        r = rng.choice((4, 5, 6))
        p.ellipse(x, y, r * 2, r * 2, BRASS[0])
        p.ellipse(x, y, r * 2 - 1, r * 2 - 1, BRASS[2])
        p.ellipse(x + 1, y + 1, r * 2 - 3, r * 2 - 3, BRASS[3])
        p.hline(x + 2, y + 1, max(1, r - 2), BRASS[4])
        p.px(x + 1, y + 2, BRASS[4])
        p.hline(x + r - 1, y + r - 1, 2, BRASS[2])          # the stamp on the face
        p.vline(x + r - 1, y + r - 2, 3, BRASS[2])
    for _ in range(14):                                    # stars
        x, y = rng.randrange(8, 166), rng.randrange(8, 126)
        p.hline(x - 2, y, 5, BRASS[4])
        p.vline(x, y - 2, 5, BRASS[4])
        p.px(x - 1, y - 1, BRASS[3])
        p.px(x + 1, y + 1, BRASS[3])
        p.px(x + 1, y - 1, BRASS[3])
        p.px(x - 1, y + 1, BRASS[3])
    return p


def card_frame(p: Pix) -> None:
    """Three-line brass frame with a dark outer edge and little rosettes in the corners."""
    p.frame(0, 0, 180, 142, SHADOW)
    p.frame(1, 1, 178, 140, BRASS[2])
    p.frame(2, 2, 176, 138, BRASS[4])
    p.frame(3, 3, 174, 136, BRASS[1])
    p.hline(1, 1, 178, BRASS[4])
    p.vline(1, 1, 140, BRASS[3])
    p.hline(1, 140, 178, BRASS[0])
    p.vline(178, 1, 140, BRASS[0])
    for x, y in ((6, 6), (173, 6), (6, 135), (173, 135)):
        p.rect(x - 1, y - 1, 3, 3, BRASS[3])
        p.px(x, y, SHADOW)


def window(p: Pix, x0: int, y0: int, x1: int, y1: int) -> None:
    """The foil patch (the game scratches this rectangle off): flat wine with an engraved edge."""
    p.rect(x0 - 1, y0 - 1, x1 - x0 + 3, y1 - y0 + 3, SHADOW)
    p.rect(x0, y0, x1 - x0 + 1, y1 - y0 + 1, (94, 43, 69))
    p.hline(x0, y0, x1 - x0 + 1, (74, 32, 56))
    p.vline(x0, y0, y1 - y0 + 1, (74, 32, 56))


def scratch_front() -> Image.Image:
    p = card_ground(21)
    # title block: "FORTUNE" big with a banded shade, "GRAND LOTTERY" below, a ribbon under both
    p.rect(30, 12, 120, 56, (62, 28, 46))
    p.dither(30, 12, 120, 56, (84, 38, 58), 0.4)
    letters = "FORTUNE"
    x = 90 - font.width(letters, 2) // 2 - 0
    tp = Pix(180, 142)
    font.write(tp, x, 17, letters, (255, 255, 255), 2)
    ramp = (BRASS[4], BRASS[4], BRASS[3], BRASS[3], BRASS[2], BRASS[2], BRASS[1], BRASS[1], BRASS[1], BRASS[0], BRASS[0],
            BRASS[0], BRASS[0], BRASS[0])
    for yy in range(17, 31):
        for xx in range(180):
            if tp.get(xx, yy)[3]:
                p.px(xx, yy, ramp[yy - 17])
    for yy in range(17, 31):
        for xx in range(180):
            if tp.get(xx, yy)[3] and not tp.get(xx + 1, yy + 1)[3]:
                p.px(xx + 1, yy + 1, SHADOW)
    font.write(p, 90 - font.width("GRAND LOTTERY") // 2, 38, "GRAND LOTTERY", PARCHMENT[3])
    ribbon_body = Mask(180, 142).rect(18, 50, 144, 14)
    wings = Mask(180, 142).poly([(8, 46), (24, 52), (24, 70), (8, 64), (14, 55)]).poly(
        [(172, 46), (156, 52), (156, 70), (172, 64), (166, 55)])
    for m in (wings,):
        rim(p, m, SHADOW)
        paint(p, m, WINE)
    rim(p, ribbon_body, SHADOW)
    paint(p, ribbon_body, (BRASS[2], BRASS[2], BRASS[3], BRASS[4]))
    font.write(p, 90 - font.width("SCRATCH TO WIN") // 2, 53, "SCRATCH TO WIN", WINE[1])
    window(p, 33, 99, 146, 133)
    card_frame(p)
    return p.im


def scratch_back() -> Image.Image:
    p = card_ground(22)
    window(p, 33, 13, 147, 132)
    card_frame(p)
    return p.im
