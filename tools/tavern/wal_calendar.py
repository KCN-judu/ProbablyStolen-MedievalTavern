"""The calendar as a hanging almanac (a book of leather, brass and paper), redrawn to the cask's material quality:
`calendar`, `calendar wire`, `calendar_stripped` (the same book's open face as the in-game window) and
`calendar_top-Sheet` (faint ruled lines that drift over the page).

Logic: the game's wall calendar is an electronic day-planner on a cable. Here it is a perpetual almanac bound in
pebbled calf with brass corner guards and ribbon markers, hung from the beam by two iron eyebolts, a short chain each,
and a ring through each brass eyelet in the spine. The page is clean paper (the game writes the day on it): only a soft
shade into the binding and the faint cockle of old paper. The fan of page edges shows around it.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final

from PIL import Image, ImageDraw

import fxkit as fx
from materials import tone
from palette import BRASS, IRON, LEATHER, LINEN, MOSS, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix
from wal_kit import eyebolt, herb_bunch, nail

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


SMALL: Final = Book(125, 84, (12, 11, 111, 73), 8, 5, 3, 10, 1, 2)
WINDOW: Final = Book(729, 496, (54, 49, 673, 446), 42, 14, 15, 44, 5, 14)


def _leather(p: Pix, b: Book) -> None:
    """The cover: pebbled calf, lit on the upper left, darker toward the lower right, rubbed pale at the edges and
    corners, with a tooled double rule and rounded corners."""
    w, h, u = b.w, b.h, b.u
    for y in range(h):
        for x in range(w):
            peb = fx.vnoise(x / (1.6 * u), y / (1.6 * u), 3)               # the pebble of the hide
            fib = fx.vnoise(x / (9 * u), y / (2.5 * u), 8)                 # long creases of the skin
            light = 1.0 - (x / w * 0.55 + y / h * 0.65)
            v = 1.7 + light * 1.1 + (peb - 0.5) * 1.5 + (fib - 0.5) * 0.9
            edge = min(x, y, w - 1 - x, h - 1 - y) / u
            if edge < 2.5:
                v += (0.9 - edge * 0.2) if (x < w // 2 and y < h // 2) or edge < 1 else -0.2   # rubbed pale at the rim
            p.px(x, y, fx.pick_tone(LEATHER, v, x, y, 2.4))
    p.hline(0, 0, w, LEATHER[3])
    p.vline(0, 0, h, LEATHER[3])
    p.hline(0, h - 1, w, LEATHER[0])
    p.vline(w - 1, 0, h, LEATHER[0])
    inset = max(3, b.page[0] // 2 - 1) if u == 1 else b.page[0] - b.stack - 3 * u
    for i, c in enumerate((LEATHER[0], LEATHER[3])):                     # tooled rule: a dark groove with a lit lip
        p.draw.rounded_rectangle((inset + i, inset + i, w - 1 - inset - i, h - 1 - inset - i), max(1, b.corner - inset // 2),
                                 outline=c, width=max(1, u // 2))
    c = b.corner
    for dx, dy in ((0, 0), (w - c, 0), (0, h - c), (w - c, h - c)):      # round the corners
        for yy in range(c):
            for xx in range(c):
                cx = c - xx - 0.5 if dx == 0 else xx + 0.5
                cy = c - yy - 0.5 if dy == 0 else yy + 0.5
                if math.hypot(c - cx, c - cy) > c:
                    p.px(dx + xx, dy + yy, CLEAR)


def _page(p: Pix, b: Book) -> None:
    """The page: clean aged paper with fine fibre, shaded into the binding and at its right edge; nothing printed."""
    x0, y0, x1, y1 = b.page
    m = Image.new("L", (b.w, b.h), 0)
    ImageDraw.Draw(m).rounded_rectangle((x0, y0, x1, y1), b.page_r, fill=255)
    u = b.u
    for y in range(y0, y1 + 1):                                        # clean paper: a soft cockle and fine tooth, no marks
        for x in range(x0, x1 + 1):
            if m.getpixel((x, y)):
                v = 3.05 + (fx.vnoise(x / (14 * u), y / (10 * u), 6) - 0.5) * 0.5 + (fx.noise(x, y, 2) - 0.5) * 0.35
                p.px(x, y, fx.pick_tone(PARCHMENT, v, x, y, 1.6))
    pw, ph = x1 - x0 + 1, y1 - y0 + 1
    gut = max(3, 3 * b.u)                                              # the leaf curves down into the binding
    for i in range(gut):
        p.dither(x0, y0 + i, pw, 1, PARCHMENT[1], 0.7 * (1 - i / gut))
    for i in range(max(2, 2 * b.u)):                                   # shade where the page meets the stack
        p.dither(x1 - i, y0, 1, ph, PARCHMENT[2], 0.55 * (1 - i / (2 * b.u)))
        p.dither(x0 + i, y0, 1, ph, PARCHMENT[2], 0.3 * (1 - i / (2 * b.u)))
        p.dither(x0, y1 - i, pw, 1, PARCHMENT[2], 0.4 * (1 - i / (2 * b.u)))


def _spine(p: Pix, b: Book) -> None:
    """The binding along the top: darker leather with raised ribs shaded as round bands, stitches, and the gutter shadow."""
    w, u, s = b.w, b.u, b.spine
    for y in range(s):
        for x in range(w):
            v = 1.3 + (fx.vnoise(x / (1.5 * u), y / (1.5 * u), 4) - 0.5) * 1.1 + (0.8 if y < u else 0) - (0.8 if y >= s - u else 0)
            p.px(x, y, fx.pick_tone(LEATHER, v, x, y, 2.4))
    p.hline(0, s - 1 * u, w, LEATHER[0])
    for rx in (w // 4, w // 2, w * 3 // 4):                            # raised ribs: cylinders lit on their left
        for dx in range(-2 * u, 2 * u + 1):
            t = dx / (2 * u)
            v = 3.2 - (t + 0.4) * 2.0
            for y in range(s - u):
                p.px(rx + dx, y, fx.pick_tone(LEATHER, v + (0.4 if y < u else 0), rx + dx, y, 3.0))
    for x in range(b.guard + 2 * u, w - b.guard - 2 * u, 4 * u):       # stitching
        if all(abs(x - r) > 3 * u for r in (w // 4, w // 2, w * 3 // 4)):
            p.rect(x, s // 2, 2 * u, max(1, u // 2 + 1), PARCHMENT[1])
            p.rect(x, s // 2 + max(1, u // 2 + 1), 2 * u, max(1, u // 2), LEATHER[0])
    for i in range(2 * u):                                             # the gutter shadow the binding throws on the page
        p.dither(b.page[0] + 1, b.spine + i, b.page[2] - b.page[0] - 1, 1, SHADOW, 0.45 * (1 - i / (2 * u)))


def _brass_guard(p: Pix, x: int, y: int, size: int, sx: int, sy: int, u: int) -> None:
    """A brass corner guard wrapped over a corner: painted by `brass_fill` as a triangle so it has a highlight and tarnish."""
    pts = [(x, y), (x + sx * (size + size // 3), y), (x + sx * size // 2 + sx * size // 3, y + sy * size // 2),
           (x + sx * size // 2, y + sy * (size // 2 + size // 3)), (x, y + sy * (size + size // 3))]
    pts = [(min(max(px_, 0), p.w - 1), min(max(py_, 0), p.h - 1)) for px_, py_ in pts]
    fx.brass_fill(p, pts, profile="plate", tarnish=0.4, seed=x + y)
    fx.rivet(p, x + sx * (size // 3), y + sy * (size // 3), max(1, u), BRASS, shadow=False)


def book(b: Book, seed: int, ribbons: tuple[tuple[int, int, tuple[Color, ...]], ...], quill: bool) -> Pix:
    """One almanac: cover, fan of pages, page, binding, brass guards, ribbons."""
    p = Pix(b.w, b.h, seed=seed)
    _leather(p, b)
    _stack(p, b)
    _page(p, b)
    _spine(p, b)
    g, u = b.guard, b.u
    _brass_guard(p, 0, 0, g, 1, 1, u)
    _brass_guard(p, b.w - 1, 0, g, -1, 1, u)
    _brass_guard(p, 0, b.h - 1, g, 1, -1, u)
    _brass_guard(p, b.w - 1, b.h - 1, g, -1, -1, u)
    for rx, length, ramp in ribbons:
        _ribbon(p, rx, b.page[3] - 2 * b.u, b.page[3] + length, 5 * u, ramp)
    if u > 1:
        for bx in (b.page[0] // 2 - 1, b.w - b.page[0] // 2 - 1):
            for by in (b.h // 4, b.h // 2, b.h * 3 // 4):
                _boss(p, bx, by, 2 * u)
    else:
        for ex in (20, 88):                                            # the eyelets the rings run through
            fx.brass_fill(p, (ex - 3, 1, 7, 5), profile="plate", tarnish=0.2, seed=ex)
            p.rect(ex - 1, 2, 3, 2, SHADOW)
    if quill:
        _quill(p, b.w - 6, 22, 66)
        p.rect(b.w - 10, 50, 8, 3, LEATHER[0])                         # the leather loop that holds it
        p.rect(b.w - 10, 50, 8, 1, LEATHER[3])
        fx.rivet(p, b.w - 6, 51, 1, BRASS, shadow=False)
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
    """`calendar wire` (117x50 at (154, 0)): two iron eyebolts in the beam, a short chain from each to a ring that runs
    through the brass eyelet of the spine (the book's own layer covers the ring's lower half), and a herb bunch tied to
    a nail beside it."""
    small = Pix(117, 50, seed=2)
    for ex in (43, 111):
        eyebolt(small, ex, 6, ring=6, drop=1)
        for k, (cy, rw, rh) in enumerate(((16, 2.0, 3.6), (21, 2.0, 3.6))):   # two links: the lower runs through the eyelet
            for a in range(0, 360, 10):
                rx = ex + round(math.cos(math.radians(a)) * rw)
                ry = cy + round(math.sin(math.radians(a)) * rh)
                small.px(rx, ry, IRON[4] if math.cos(math.radians(a - 225)) > 0.25 else IRON[1] if math.cos(math.radians(a - 45)) > 0.5 else IRON[3])
    nail(small, 11, 4)
    small.vline(11, 5, 3, fx.ROPE[2])
    herb_bunch(small, 11, 7, 22, 9, seed=3)
    full = Pix(W, H)
    full.paste(small, 154, 0)
    return full.finish()


# ---------------------------------------------------------------------------------------------- the window and its lines


def calendar_window() -> Image.Image:
    """`calendar_stripped` (729x496): the window of the in-game calendar as the open face of the same almanac."""
    ribbons = ((200, 30, (WINE[0], WINE[1], WINE[2], WINE[3])), (470, 22, (MOSS[0], MOSS[1], MOSS[2], MOSS[3])))
    return book(WINDOW, 5, ribbons, quill=False).finish()


def calendar_lines() -> Image.Image:
    """`calendar_top-Sheet` (405x63): four frames of faint ruled lines in warm ink; frame k has its lines one row lower than
    frame k-1 so that the lines seem to creep as the sheet plays. Kept to the rows and columns of the game's strips."""
    p = Pix(405, 63, seed=21)
    for k in range(4):
        for y in range(1 + k, 62, 4):
            drift = y // 14
            x0, x1 = k * 101 + 2 + drift, k * 101 + 97 + y // 22
            for x in range(x0, x1 + 1):
                a = 24 if (x // 9 + y // 4) % 5 else 36              # the quill pressed a little harder in places
                p.px(x, y, (*PARCHMENT[0], a))
    return p.finish()


ASSETS: Final[Mapping[str, Callable[[], Image.Image]]] = {
    "calendar.960x540.png": almanac,
    "calendar wire.960x540.png": almanac_cords,
    "calendar_stripped.729x496.png": calendar_window,
    "calendar_top-Sheet.405x63.png": calendar_lines,
}
