"""The calendar as an almanac book: a ledger of leather with brass corners, ribbon markers and a thick fan of pages, bound
at its top and hanging from two cords (the shop's `calendar` and `calendar wire`), the same book as the window of the
in-game calendar (`calendar_stripped`), and the faint ruled lines that run over its page (`calendar_top-Sheet`).

The game writes the day number over the page, so every page here is clean parchment (no figures, grid or text): only
a soft shade into the binding and the page's edge. The page keeps the place of the game's own page.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final

from PIL import Image

from materials import tone
from palette import BRASS, IRON, LEATHER, LINEN, MOSS, PARCHMENT, SHADOW, WINE
from pix import CLEAR, Color, Pix

W, H = 960, 540


@dataclass(frozen=True)
class Book:
    """The measures of one almanac: its size, where its page lies and how big its fittings are (`u` is 1 for the small
    picture and grows with the big window, so the same drawing scales)."""
    w: int
    h: int
    page: tuple[int, int, int, int]       # x0, y0, x1, y1 of the page, both ends included
    spine: int                            # height of the binding at the top
    stack: int                            # thickness of the fan of page edges at the sides and the bottom
    corner: int                           # radius of the cover's corners
    guard: int                            # size of a brass corner guard
    u: int                                # unit for the fine details
    page_r: int                           # radius of the page's corners


SMALL: Final = Book(125, 84, (12, 11, 111, 73), 8, 5, 3, 10, 1, 2)
WINDOW: Final = Book(729, 496, (54, 49, 673, 446), 42, 14, 15, 44, 5, 14)


def _leather(p: Pix, b: Book) -> None:
    """The cover: leather lit on its upper left, with grain, a tooled double border and rounded corners."""
    w, h, u = b.w, b.h, b.u
    p.rect(0, 0, w, h, LEATHER[2])
    p.dither(0, 0, w, h, LEATHER[1], 0.22)
    p.dither(w // 3, h // 2, w, h, LEATHER[1], 0.2)
    p.speckle(0, 0, w, h, (LEATHER[3], LEATHER[3], LEATHER[1]), 0.05 / u)
    if u > 1:                                                          # coarse pores at the size of the big picture
        for _ in range(w * h // 160):
            x, y = p.rng.randrange(w), p.rng.randrange(h)
            p.rect(x, y, p.rng.randrange(2, 2 * u), max(1, u // 3), LEATHER[3] if p.rng.random() < 0.25 else LEATHER[1])
    p.hline(0, 0, w, LEATHER[3])                                       # lit upper and left edges, shaded lower and right
    p.vline(0, 0, h, LEATHER[3])
    p.hline(0, h - 1, w, LEATHER[0])
    p.vline(w - 1, 0, h, LEATHER[0])
    for k in range(1, max(2, u)):
        p.hline(k, k, w - 2 * k, tone(LEATHER[3], -0.1))
        p.vline(k, k, h - 2 * k, tone(LEATHER[3], -0.1))
        p.hline(k, h - 1 - k, w - 2 * k, LEATHER[1])
        p.vline(w - 1 - k, k, h - 2 * k, LEATHER[1])
    inset = max(3, b.page[0] // 2 - 1) if u == 1 else b.page[0] - b.stack - 3 * u
    p.draw.rounded_rectangle((inset, inset, w - 1 - inset, h - 1 - inset), max(1, b.corner - inset // 2), outline=LEATHER[0])
    p.draw.rounded_rectangle((inset + 1, inset + 1, w - 2 - inset, h - 2 - inset), max(1, b.corner - inset // 2),
                             outline=LEATHER[3])
    c = b.corner
    for dx, dy in ((0, 0), (w - c, 0), (0, h - c), (w - c, h - c)):    # round the corners
        for yy in range(c):
            for xx in range(c):
                cx = c - xx - 0.5 if dx == 0 else xx + 0.5
                cy = c - yy - 0.5 if dy == 0 else yy + 0.5
                if math.hypot(c - cx, c - cy) > c:
                    p.px(dx + xx, dy + yy, CLEAR)


def _stack(p: Pix, b: Book) -> None:
    """The thick fan of pages: nested outlines round the page, a thin sheet each, a few sticking out so the leaves fan; the
    left edge catches the light, the right edge and the foot are in shade, the outermost leaf is the darkest."""
    x0, y0, x1, y1 = b.page
    mid = (x0 + x1) / 2
    step = 1 if b.u == 1 else 2
    for k in range(b.stack, 0, -step):
        wob = 1 if (k * 7) % 5 == 0 and b.u == 1 else (k % 3) * (b.u // 2)
        ring = Pix(b.w, b.h)
        ring.draw.rounded_rectangle((x0 - k - wob, y0 - 12 * b.u, x1 + k + wob, y1 + k + wob), b.page_r + k, outline=(1, 1, 1), width=step)
        odd = k % 2
        for y in range(b.h):
            for x in range(b.w):
                if ring.get(x, y)[3]:
                    if k == b.stack:
                        c = PARCHMENT[0]
                    elif y > y1 - b.page_r and x >= x0 + b.page_r:
                        c = PARCHMENT[2] if odd else PARCHMENT[1]
                    elif x < mid:
                        c = PARCHMENT[4] if odd else PARCHMENT[2]
                    else:
                        c = PARCHMENT[2] if odd else PARCHMENT[0]
                    p.px(x, y, c)


def _page(p: Pix, b: Book) -> None:
    """The page: clean parchment, softly shaded into the binding and at its right edge; nothing printed."""
    x0, y0, x1, y1 = b.page
    p.draw.rounded_rectangle((x0, y0, x1, y1), b.page_r, fill=PARCHMENT[3])
    pw, ph = x1 - x0 + 1, y1 - y0 + 1
    p.dither(x0, y0, pw, ph, PARCHMENT[2], 0.07)
    p.speckle(x0, y0, pw, ph, (PARCHMENT[2], PARCHMENT[4]), 0.004)
    gut = max(3, 3 * b.u)                                              # the leaf curves down into the binding
    for i in range(gut):
        p.dither(x0, y0 + i, pw, 1, PARCHMENT[1], 0.7 * (1 - i / gut))
    for i in range(max(2, 2 * b.u)):                                   # a little shade where the page edge meets the stack
        p.dither(x1 - i, y0, 1, ph, PARCHMENT[2], 0.55 * (1 - i / (2 * b.u)))
        p.dither(x0 + i, y0, 1, ph, PARCHMENT[2], 0.3 * (1 - i / (2 * b.u)))
        p.dither(x0, y1 - i, pw, 1, PARCHMENT[2], 0.4 * (1 - i / (2 * b.u)))


def _spine(p: Pix, b: Book) -> None:
    """The binding along the top: a darker leather band with raised ribs, stitches and a brass strip, and brass eyelets
    by which the book hangs."""
    w, u, s = b.w, b.u, b.spine
    p.rect(0, 0, w, s, LEATHER[1])
    p.dither(0, 0, w, s, LEATHER[2], 0.4)
    p.hline(0, 0, w, LEATHER[3])
    p.hline(0, 1 * u, w, LEATHER[2])
    p.hline(0, s - 1 * u, w, LEATHER[0])
    p.hline(0, s - 2 * u if u > 1 else s - 1, w, LEATHER[0])
    for rx in (w // 4, w // 2, w * 3 // 4):                            # raised ribs
        p.rect(rx - u, 0, 2 * u, s, LEATHER[3])
        p.vline(rx + u, 0, s, LEATHER[0])
        p.vline(rx - u, 0, s, LEATHER[3])
    for x in range(b.guard + 2 * u, w - b.guard - 2 * u, 4 * u):       # stitching
        if abs(x - w // 4) > 2 * u and abs(x - w // 2) > 2 * u and abs(x - w * 3 // 4) > 2 * u:
            p.rect(x, s // 2, 2 * u, max(1, u // 2 + 1), LEATHER[3])
            p.rect(x, s // 2 + max(1, u // 2 + 1), 2 * u, max(1, u // 2), LEATHER[0])
    # the gutter shadow the binding throws on the page
    for i in range(2 * u):
        p.dither(b.page[0] + 1, b.spine + i, b.page[2] - b.page[0] - 1, 1, SHADOW, 0.45 * (1 - i / (2 * u)))


def _guard(p: Pix, x: int, y: int, size: int, sx: int, sy: int, u: int) -> None:
    """A brass corner guard: a triangle of metal wrapped over a corner, lit on the upper left, with a rivet."""
    for yy in range(size):
        for xx in range(size - yy + (size // 3)):
            if xx >= size or yy >= size:
                continue
            px_, py_ = (x + xx if sx > 0 else x - xx), (y + yy if sy > 0 else y - yy)
            edge = xx + yy >= size + size // 3 - 1
            lit = (sx > 0 and xx == 0) or (sy > 0 and yy == 0)
            dark = (sx < 0 and xx == 0) or (sy < 0 and yy == 0)
            p.px(px_, py_, BRASS[0] if edge else BRASS[4] if lit else BRASS[1] if dark else BRASS[3] if xx + yy < size // 2 else BRASS[2])
    rx = x + sx * (size // 3)
    ry = y + sy * (size // 3)
    p.rect(rx, ry, max(1, u), max(1, u), BRASS[4])
    p.rect(rx + max(1, u), ry + max(1, u), max(1, u), max(1, u), BRASS[0])


def _ribbon(p: Pix, x: int, top: int, bottom: int, width: int, ramp: tuple[Color, ...]) -> None:
    """A silk marker hanging down over the edge of the pages, its end cut into a swallow's tail."""
    for y in range(top, bottom + 1):
        notch = max(0, y - (bottom - width))                           # the V cut into its end
        for xx in range(width):
            if notch and abs(xx - (width - 1) / 2) < notch * 0.5:
                continue
            c = ramp[3] if xx == 0 else ramp[1] if xx == width - 1 else ramp[2]
            if (y + xx) % 7 == 0 and 0 < xx < width - 1:
                c = ramp[3]
            p.px(x + xx, y, c)
    p.vline(x - 1, top, bottom - top - width // 2, ramp[0])
    p.vline(x + width, top, bottom - top - width // 2, ramp[0])


def _quill(p: Pix, x: int, top: int, bottom: int) -> None:
    """A goose quill tucked upright in a loop on the right of the cover: a shaft, a slim feather with a vane each side
    and a dark rim, an ink-dipped nib."""
    for k in range(22):                                                # the vane, widest a third of the way down
        wv = round(2.4 * math.sin(math.pi * (k + 1) / 23)) + 1
        y = top + k
        p.px(x - wv - 1, y, SHADOW)
        p.px(x + wv + 1, y, SHADOW)
        for d in range(1, wv + 1):
            p.px(x - d, y, PARCHMENT[4] if d < wv else PARCHMENT[3])
            p.px(x + d, y, PARCHMENT[2] if d < wv else PARCHMENT[1])
    p.px(x, top - 1, SHADOW)
    for y in range(top, bottom):
        p.px(x, y, PARCHMENT[4] if y < top + 22 else BRASS[3] if y > bottom - 4 else PARCHMENT[3])
    p.px(x, bottom, SHADOW)
    p.px(x, bottom + 1, WINE[1])
    p.px(x, bottom + 2, SHADOW)


def _boss(p: Pix, cx: int, cy: int, r: int) -> None:
    """A round brass boss studded on the cover, a dome lit on its upper left."""
    p.ellipse(cx - r + 1, cy - r + 1, 2 * r + 1, 2 * r + 1, LEATHER[0])
    p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, BRASS[1])
    p.ellipse(cx - r + 1, cy - r + 1, 2 * r - 1, 2 * r - 1, BRASS[2])
    p.ellipse(cx - r + 2, cy - r + 2, r, r, BRASS[3])
    p.rect(cx - r + 3, cy - r + 3, max(1, r // 3), max(1, r // 3), BRASS[4])


def book(b: Book, seed: int, ribbons: tuple[tuple[int, int, tuple[Color, ...]], ...], quill: bool) -> Pix:
    """One almanac: cover, fan of pages, page, binding, brass guards, ribbons."""
    p = Pix(b.w, b.h, seed=seed)
    _leather(p, b)
    _stack(p, b)
    _page(p, b)
    _spine(p, b)
    g, u = b.guard, b.u
    _guard(p, 0, 0, g, 1, 1, u)
    _guard(p, b.w - 1, 0, g, -1, 1, u)
    _guard(p, 0, b.h - 1, g, 1, -1, u)
    _guard(p, b.w - 1, b.h - 1, g, -1, -1, u)
    for rx, length, ramp in ribbons:
        _ribbon(p, rx, b.page[3] - 2 * b.u, b.page[3] + length, 5 * u, ramp)
    if u > 1:
        for bx in (b.page[0] // 2 - 1, b.w - b.page[0] // 2 - 1):
            for by in (b.h // 4, b.h // 2, b.h * 3 // 4):
                _boss(p, bx, by, 2 * u)
    else:
        for ex in (20, 88):                                            # the eyelets the cords run through
            p.rect(ex - 3, 1, 7, 5, BRASS[2])
            p.hline(ex - 3, 1, 7, BRASS[4])
            p.hline(ex - 3, 5, 7, BRASS[0])
            p.rect(ex - 1, 2, 3, 2, SHADOW)
    if quill:
        _quill(p, b.w - 6, 22, 66)
        p.rect(b.w - 10, 50, 8, 3, LEATHER[0])                         # the leather loop that holds it
        p.rect(b.w - 10, 50, 8, 1, LEATHER[3])
        p.px(b.w - 6, 51, BRASS[3])
    return p


def almanac() -> Image.Image:
    """`calendar` (125x84 at (177, 19)): the almanac of the tavern: the page is where the game writes the day."""
    wine = (WINE[0], WINE[1], WINE[2], WINE[3])
    moss = (MOSS[0], MOSS[1], MOSS[2], MOSS[3])
    small = book(SMALL, 11, ((36, 9, wine), (80, 7, moss)), quill=True)
    full = Pix(W, H)
    full.paste(small, 177, 19)
    return full.finish()


def almanac_cords() -> Image.Image:
    """`calendar wire` (117x50 at (154, 0)): the two cords that carry the book from the beam, down to its brass eyelets, and a
    bunch of herbs hanging beside it."""
    from props import arc, chain, herb_bunch, rope             # shared drawing of ropes and herbs
    small = Pix(117, 50, seed=2)
    rope(small, [(43, y) for y in range(0, 21)], 2)
    chain(small, [(111, y) for y in range(0, 21)])
    for ex in (43, 111):
        small.draw.ellipse((ex - 4, 16, ex + 4, 24), outline=IRON[2])           # the ring through the eyelet
        small.px(ex - 3, 17, IRON[4])
    small.vline(10, 0, 8, LEATHER[1])
    herb_bunch(small, 10, 8, 22, 9)
    herb_bunch(small, 77, 0, 15, 7, dry=True)
    del arc
    full = Pix(W, H)
    full.paste(small, 154, 0)
    return full.finish()


# ---------------------------------------------------------------------------------------------- the window and its lines


def calendar_window() -> Image.Image:
    """`calendar_stripped` (729x496): the window of the in-game calendar as the open face of the same almanac; the game puts
    its figures on the page."""
    ribbons = ((200, 30, (WINE[0], WINE[1], WINE[2], WINE[3])), (470, 22, (MOSS[0], MOSS[1], MOSS[2], MOSS[3])))
    return book(WINDOW, 5, ribbons, quill=False).finish()


def calendar_lines() -> Image.Image:
    """`calendar_top-Sheet` (405x63): four frames of faint ruled lines in warm ink; frame k has its lines one row lower than
    frame k-1 so that the lines seem to creep as the sheet plays. Kept to the rows and columns of the game's strips."""
    p = Pix(405, 63, seed=21)
    ink = (*PARCHMENT[0], 34)
    for k in range(4):
        for y in range(1 + k, 62, 4):
            drift = y // 14
            x0, x1 = k * 101 + 2 + drift, k * 101 + 97 + y // 22
            for x in range(x0, x1 + 1):
                a = 24 if (x // 9 + y // 4) % 5 else 36              # the quill pressed a little harder in places
                p.px(x, y, (*PARCHMENT[0], a))
    del ink
    return p.finish()


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
}
