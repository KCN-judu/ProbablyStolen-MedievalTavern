"""Pictograms of the in-play interface: arrows, crosses, ticks, faces, medallions and the small item and stat icons.

Everything here is small. A glyph function paints one shape in one colour into a rectangle of a `Pix` (so a button can
carry any of them in any state); an icon function returns a whole picture of the size it is given.
"""

from __future__ import annotations

from PIL import Image

from palette import BRASS, FLAME, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix, mix
import font

# ---------------------------------------------------------------------------------------------- glyphs


def chevron(p: Pix, x: int, y: int, w: int, h: int, c: Color, direction: str = "r", thick: int = 3) -> None:
    """A stepped arrow head (">" for 'r', "<" for 'l', "v" for 'd', "^" for 'u') filling the box, `thick` pixels thick."""
    horizontal = direction in "rl"
    length, span = (w, h) if horizontal else (h, w)         # the way the head points, and its width across
    half = (span + 1) // 2
    for i in range(span):
        d = i if i < half else span - 1 - i
        off = round(d * (length - thick) / max(1, half - 1))
        if direction in "lu":
            off = length - thick - off
        if horizontal:
            p.rect(x + off, y + i, thick, 1, c)
        else:
            p.rect(x + i, y + off, 1, thick, c)


def cross(p: Pix, x: int, y: int, s: int, c: Color, thick: int = 3) -> None:
    """An X in a square of side `s`."""
    for i in range(s):
        p.rect(x + i, y + i, thick, 1, c)
        p.rect(x + s - thick - i, y + i, thick, 1, c)


def tick(p: Pix, x: int, y: int, w: int, h: int, c: Color, thick: int = 3) -> None:
    """A check mark filling the box."""
    knee = (x + w * 3 // 8, y + h - 1)
    p.draw.line((x, y + h * 5 // 8, *knee), fill=c, width=thick)
    p.draw.line((*knee, x + w - 1, y), fill=c, width=thick)


def undo(p: Pix, x: int, y: int, s: int, c: Color) -> None:
    """Rewind: two chevrons pointing left, side by side, filling a square of side `s`."""
    half = s // 2
    chevron(p, x, y, half + 1, s, c, "l", 2)
    chevron(p, x + half, y, half + 1, s, c, "l", 2)


def refresh(p: Pix, x: int, y: int, w: int, h: int, light: Color, dark: Color) -> None:
    """Two arrows chasing each other round a rectangle (swap, reload)."""
    p.rect(x + 2, y, w - 6, 3, light)
    p.rect(x + w - 4, y, 3, h // 2 + 1, light)
    p.poly([(x + w - 7, y + h // 2 - 1), (x + w, y + h // 2 - 1), (x + w - 4, y + h // 2 + 3)], light)
    p.rect(x + 4, y + h - 3, w - 6, 3, dark)
    p.rect(x + 1, y + h // 2 - 1, 3, h // 2 + 1, dark)
    p.poly([(x, y + h // 2), (x + 6, y + h // 2), (x + 3, y + h // 2 - 4)], dark)


def bubble_glyph(p: Pix, x: int, y: int, w: int, h: int, c: Color) -> None:
    """A speech bubble with a tail at the lower left."""
    p.rect(x + 1, y, w - 2, h - 3, c)
    p.rect(x, y + 1, w, h - 5, c)
    p.poly([(x + 2, y + h - 4), (x + 5, y + h - 4), (x + 2, y + h - 1)], c)


# ---------------------------------------------------------------------------------------------- faces and discs


def face(w: int, h: int, mood: str) -> Image.Image:
    """An 11x11 face of one mood: a round tan head with a dark rim, eyes and a mouth; 'skull' is bone, 'star' a gold star."""
    p = Pix(w, h)
    if mood == "star":
        pts = [(5, 0), (6, 4), (10, 4), (7, 6), (8, 10), (5, 7), (2, 10), (3, 6), (0, 4), (4, 4)]
        p.poly(pts, SHADOW)
        p.poly([(5, 1), (6, 4), (9, 4), (7, 6), (7, 9), (5, 7), (3, 9), (3, 6), (1, 4), (4, 4)], BRASS[3])
        p.px(5, 3, BRASS[4])
        p.px(4, 4, BRASS[4])
        return p.im
    skin = LINEN[3] if mood == "skull" else PALE_WOOD[4]
    p.ellipse(0, 0, 11, 11, SHADOW)
    p.ellipse(1, 1, 9, 9, skin)
    p.px(3, 2, mix(skin, (255, 240, 200), 0.5))
    p.px(2, 3, mix(skin, (255, 240, 200), 0.5))
    if mood == "skull":
        p.rect(2, 4, 3, 3, SHADOW)
        p.rect(6, 4, 3, 3, SHADOW)
        p.px(5, 7, SHADOW)
        p.rect(3, 9, 5, 1, SHADOW)
        p.vline(4, 8, 2, SHADOW)
        p.vline(6, 8, 2, SHADOW)
        return p.im
    p.rect(3, 4, 1, 2, SHADOW)
    p.rect(7, 4, 1, 2, SHADOW)
    if mood == "smile":
        p.hline(4, 8, 3, SHADOW)
        p.px(3, 7, SHADOW)
        p.px(7, 7, SHADOW)
    elif mood == "happy":
        p.rect(3, 7, 5, 2, SHADOW)
        p.hline(4, 7, 3, LINEN[3])
    elif mood == "sad":
        p.hline(4, 7, 3, SHADOW)
        p.px(3, 8, SHADOW)
        p.px(7, 8, SHADOW)
    elif mood == "angry":
        p.px(2, 3, SHADOW)
        p.px(3, 3, SHADOW)
        p.px(7, 3, SHADOW)
        p.px(8, 3, SHADOW)
        p.hline(4, 7, 3, SHADOW)
        p.px(3, 8, SHADOW)
        p.px(7, 8, SHADOW)
        p.px(2, 2, SHADOW)
        p.px(8, 2, SHADOW)
    return p.im


def info_disc(w: int, h: int, body: Color, mark: Color) -> Image.Image:
    """A round "i" badge: a disc in `body` with a lighter lip on the upper left and the letter in `mark`."""
    p = Pix(w, h)
    p.ellipse(0, 0, w, h, mix(body, SHADOW, 0.55))
    p.ellipse(1, 1, w - 2, h - 2, body)
    p.draw.arc((1, 1, w - 2, h - 2), 180, 270, fill=mix(body, (255, 235, 190), 0.4))
    cx = w // 2 - 1
    u = max(1, w // 14)
    p.rect(cx, h * 3 // 14, 2 * u, 2 * u, mark)
    p.rect(cx, h * 6 // 14, 2 * u, h * 5 // 14, mark)
    p.rect(cx - u, h * 6 // 14, u, u, mark)
    p.rect(cx - u, h * 11 // 14 - 1, 4 * u, u, mark)
    return p.im


def medallion(w: int, h: int, ring: Color, centre: Color) -> Image.Image:
    """A flat round disc with a rim (perk badge, porthole): rim colour `ring`, middle `centre`."""
    p = Pix(w, h)
    p.ellipse(0, 0, w, h, SHADOW)
    p.ellipse(1, 1, w - 2, h - 2, ring)
    r = max(3, min(w, h) // 5)
    p.ellipse(r, r, w - 2 * r, h - 2 * r, mix(ring, SHADOW, 0.6))
    p.ellipse(r + 1, r + 1, w - 2 * r - 2, h - 2 * r - 2, centre)
    return p.im


# ---------------------------------------------------------------------------------------------- stat and item icons


def stat_icon(w: int, h: int, kind: str, c: Color, lit: bool = False) -> Image.Image:
    """The small outlined pictograms of the stat rows (herb, sack, water drop, lock, grin, cross, skull) in colour `c`."""
    p = Pix(w, h)
    inner = mix(c, SHADOW, 0.35)
    if kind == "herb":
        for dx in (-4, 0, 4):
            p.ellipse(w // 2 + dx - 2, 1 + abs(dx) // 2, 5, h - 6 - abs(dx) // 2, c)
            p.ellipse(w // 2 + dx - 1, 2 + abs(dx) // 2, 3, h - 8 - abs(dx) // 2, inner)
        p.rect(w // 2 - 1, h - 6, 3, 6, c)
        p.hline(2, h - 2, w - 4, c)
    elif kind == "sack":
        p.poly([(3, 4), (w - 4, 4), (w - 1, h - 3), (w - 3, h - 1), (2, h - 1), (0, h - 3)], c)
        p.poly([(4, 6), (w - 5, 6), (w - 3, h - 4), (4, h - 3), (2, h - 4)], inner)
        p.rect(w // 2 - 3, 1, 7, 3, c)
        p.hline(w // 2 - 2, 3, 5, SHADOW)
        p.line(5, 8, w - 6, h - 4, c)
    elif kind == "drop":
        p.poly([(w // 2, 0), (w - 2, h - 5), (w // 2, h - 1), (1, h - 5)], c)
        p.ellipse(0, h - 9, w, 9, c)
        p.poly([(w // 2, 3), (w - 4, h - 5), (w // 2, h - 3), (3, h - 5)], inner)
        p.ellipse(2, h - 8, w - 4, 7, inner)
        p.px(3, h - 6, c)
    elif kind == "lock":
        p.draw.arc((3, 0, w - 4, h - 3), 180, 360, fill=c, width=2)
        p.vline(3, 4, 4, c)
        p.vline(w - 4, 4, 4, c)
        p.rect(1, 7, w - 2, h - 8, c)
        p.rect(3, 9, w - 6, h - 12, inner)
        p.rect(w // 2 - 1, 10, 2, 3, c)
    elif kind == "grin":
        p.ellipse(0, 0, w, h, c)
        p.ellipse(2, 2, w - 4, h - 4, inner)
        p.rect(4, 4, 2, 3, c)
        p.rect(w - 6, 4, 2, 3, c)
        p.rect(3, h - 6, w - 6, 3, c)
        p.hline(4, h - 5, w - 8, inner)
    elif kind == "plus":
        t = max(4, w // 3)
        p.rect(w // 2 - t // 2, 0, t, h, c)
        p.rect(0, h // 2 - t // 2, w, t, c)
        p.rect(w // 2 - t // 2 + 1, 1, t - 2, h - 2, inner)
        p.rect(1, h // 2 - t // 2 + 1, w - 2, t - 2, inner)
    elif kind == "skull":
        p.ellipse(0, 0, w, h - 3, c)
        p.rect(3, h - 6, w - 6, 6, c)
        p.ellipse(2, 2, w - 4, h - 7, inner)
        p.rect(3, 5, 3, 3, c)
        p.rect(w - 6, 5, 3, 3, c)
        p.rect(w // 2 - 1, 9, 2, 2, c)
        p.rect(4, h - 5, w - 8, 3, inner)
        p.vline(w // 2 - 1, h - 5, 3, c)
        p.vline(w // 2 + 1, h - 5, 3, c)
    if lit:
        p.speckle(0, 0, w, h, (mix(c, (255, 240, 180), 0.5),), 0.1)
    return p.im


def tankard(w: int, h: int) -> Image.Image:
    """A red-glazed drinking flagon with a brass band and a handle (the soda can)."""
    p = Pix(w, h)
    p.rect(9, 3, 15, 26, SHADOW)
    p.rect(10, 4, 13, 24, WINE[2])
    p.rect(10, 4, 3, 24, WINE[3])
    p.rect(21, 4, 2, 24, WINE[1])
    p.rect(8, 6, 17, 3, BRASS[2])
    p.hline(8, 6, 17, BRASS[4])
    p.rect(8, 24, 17, 3, BRASS[2])
    p.hline(8, 26, 17, BRASS[0])
    p.rect(11, 2, 11, 3, FLAME[3])                     # the froth is the lit top
    p.hline(12, 2, 4, FLAME[4])
    p.draw.arc((20, 9, 30, 23), 270, 90, fill=SHADOW, width=3)
    p.px(13, 14, WINE[4])
    p.vline(13, 15, 4, WINE[4])
    return p.im


def tin(w: int, h: int, label: str) -> Image.Image:
    """A stamped tin with a paper label, lettered `label` (the peat tin)."""
    p = Pix(w, h)
    p.rect(2, 4, w - 4, h - 7, SHADOW)
    p.rect(3, 5, w - 6, h - 9, WINE[2])
    p.rect(3, 5, 3, h - 9, WINE[3])
    p.rect(w - 6, 5, 3, h - 9, WINE[1])
    p.rect(1, 2, w - 2, 4, IRON[3])
    p.hline(1, 2, w - 2, IRON[4])
    p.rect(1, h - 5, w - 2, 3, IRON[2])
    p.hline(1, h - 3, w - 2, IRON[0])
    p.rect(4, 8, w - 8, 10, PARCHMENT[3])
    p.frame(4, 8, w - 8, 10, PARCHMENT[1])
    font.write(p, (w - font.width(label)) // 2, 10, label, WINE[0])
    p.rect(11, 20, 10, 5, FLAME[2])                    # a loaf stamped on the lower label
    p.hline(12, 20, 8, FLAME[3])
    p.hline(11, 22, 10, LEATHER[2])
    p.hline(12, 24, 8, MOSS[3])
    return p.im


def turnip(w: int, h: int) -> Image.Image:
    """A purple-shouldered root with green leaves (the nutri-fruit)."""
    p = Pix(w, h)
    p.ellipse(3, 10, 26, 19, SHADOW)
    p.ellipse(4, 11, 24, 17, (110, 60, 120))
    p.ellipse(4, 11, 14, 10, (140, 84, 150))
    p.ellipse(18, 18, 10, 9, (214, 168, 120))
    p.px(8, 14, (190, 150, 205))
    p.speckle(5, 12, 22, 15, ((86, 44, 94),), 0.06)
    for k, x in enumerate((9, 14, 19)):
        p.poly([(x, 11), (x + 3, 11), (x + 1 + k, 2 + (k % 2) * 2)], MOSS[3])
        p.px(x + 1, 5, MOSS[2])
    p.rect(14, 9, 5, 3, MOSS[1])
    return p.im


def potion(w: int, h: int) -> Image.Image:
    """A corked flask of dark liquid with a few stars (the galaxy jar)."""
    p = Pix(w, h)
    p.poly([(11, 8), (21, 8), (26, 14), (27, 27), (24, 30), (8, 30), (5, 27), (6, 14)], SHADOW)
    p.poly([(12, 9), (20, 9), (25, 15), (26, 26), (23, 29), (9, 29), (6, 26), (7, 15)], GLASS[1])
    p.rect(7, 17, 19, 11, NAVY[1])
    p.hline(7, 17, 19, NAVY[3])
    p.poly([(7, 18), (7, 26), (9, 28), (23, 28), (25, 26), (25, 18)], NAVY[1])
    for x, y, c in ((10, 21, BRASS[4]), (16, 24, FLAME[3]), (21, 20, GLASS[4]), (13, 26, GLASS[3]), (19, 26, BRASS[3])):
        p.px(x, y, c)
    p.vline(8, 12, 12, GLASS[4])
    p.rect(12, 3, 8, 6, LEATHER[2])
    p.hline(12, 3, 8, LEATHER[3])
    p.rect(11, 7, 10, 2, BRASS[2])
    return p.im


def cat_banner(w: int, h: int) -> Image.Image:
    """A small wine-red hanging banner with a black cat's head and a brass rod."""
    p = Pix(w, h)
    p.rect(1, 3, w - 2, h - 5, SHADOW)
    p.rect(2, 4, w - 4, h - 7, WINE[2])
    p.rect(2, 4, w - 4, 2, WINE[3])
    p.rect(0, 1, w, 3, BRASS[2])
    p.hline(0, 1, w, BRASS[4])
    p.px(0, 1, SHADOW)
    p.px(w - 1, 1, SHADOW)
    p.poly([(9, 10), (12, 10), (13, 14)], IRON[1])
    p.poly([(23, 10), (20, 10), (19, 14)], IRON[1])
    p.ellipse(9, 12, 14, 12, IRON[1])
    p.px(13, 17, FLAME[3])
    p.px(14, 17, FLAME[3])
    p.px(18, 17, FLAME[3])
    p.px(19, 17, FLAME[3])
    p.px(16, 20, WINE[4])
    p.draw.polygon([(2, h - 3), (w // 2, h - 7), (w - 3, h - 3), (w - 3, h - 1), (2, h - 1)], fill=CLEAR)
    p.poly([(2, h - 4), (w // 2 - 1, h - 6), (w // 2 - 1, h - 4)], CLEAR)
    return p.im


def crest(w: int, h: int, label: str = "") -> Image.Image:
    """A watchman's heraldic shield: wine field, brass chief with three stars, a pale chevron and an optional motto."""
    p = Pix(w, h)
    top = h // 12
    pts = [(1, top), (w - 2, top), (w - 2, h * 5 // 9), (w // 2, h - 2), (1, h * 5 // 9)]
    p.poly(pts, SHADOW)
    inner = [(3, top + 2), (w - 4, top + 2), (w - 4, h * 5 // 9 - 1), (w // 2, h - 6), (3, h * 5 // 9 - 1)]
    p.poly(inner, WINE[2])
    p.rect(3, top + 2, w - 6, h // 5, BRASS[2])
    p.hline(3, top + 2, w - 6, BRASS[4])
    for i in range(3):
        cx = w // 2 + (i - 1) * (w // 4)
        cy = top + 2 + h // 10
        p.rect(cx - 1, cy - 3, 3, 7, WINE[1])
        p.rect(cx - 3, cy - 1, 7, 3, WINE[1])
    p.line(5, h * 5 // 12, w // 2, h * 3 // 4, PARCHMENT[3])
    p.line(w - 6, h * 5 // 12, w // 2, h * 3 // 4, PARCHMENT[3])
    p.line(5, h * 5 // 12 + 1, w // 2, h * 3 // 4 + 1, PARCHMENT[2])
    p.line(w - 6, h * 5 // 12 + 1, w // 2, h * 3 // 4 + 1, PARCHMENT[2])
    p.rect(3, top + 2, 2, h // 2, WINE[3])
    if label:
        font.write(p, (w - font.width(label)) // 2, h * 2 // 5, label, PARCHMENT[4])
    return p.im


def mouse(w: int, h: int, left: bool) -> Image.Image:
    """A mouse seen from above with the pressed button lit (a hint of which click to use)."""
    p = Pix(w, h)
    p.ellipse(0, 0, w, h, SHADOW)
    p.rect(2, h // 2 - 1, w - 4, h // 2 - 1, SHADOW)
    p.ellipse(1, 1, w - 2, h - 2, LINEN[3])
    p.rect(2, h // 2, w - 4, h // 2 - 3, LINEN[3])
    p.rect(1, h // 2 - 1, w - 2, 1, SHADOW)
    p.vline(w // 2, 1, h // 2, SHADOW)
    pressed = (2, 2, w // 2 - 2, h // 2 - 3) if left else (w // 2 + 1, 2, w // 2 - 3, h // 2 - 3)
    p.rect(*pressed, FLAME[2])
    p.hline(pressed[0], pressed[1], pressed[2], FLAME[3])
    p.vline(w - 4, h // 2, h // 2 - 4, LINEN[1])
    return p.im


def lamp_pair(w: int, h: int, red: bool) -> Image.Image:
    """Two little lantern panes one above the other, the lit one red or green (an alarm indicator)."""
    p = Pix(w, h)
    p.rect(0, 0, w, h, SHADOW)
    for k, hue in enumerate(((WINE, (210, 90, 80)), (MOSS, (150, 220, 110)))):
        ramp, bright = hue
        lit = (k == 0) == red
        y = 1 + k * (h // 2)
        p.rect(1, y, w - 2, h // 2 - 2, bright if lit else ramp[1])
        p.hline(1, y, w - 2, mix(bright, (255, 255, 255), 0.4) if lit else ramp[2])
        p.hline(1, y + h // 2 - 3, w - 2, ramp[0])
    return p.im
