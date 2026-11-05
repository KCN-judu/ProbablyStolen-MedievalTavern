"""Helpers for the small item sprites (cards, papers, fittings, signs, materials): shaded shapes and tiny pictograms.

A `Shape` is a one-bit mask drawn with the usual primitives; `fill` paints it into a `Pix` with the dark outline, a lit
upper-left rim and a shaded lower-right rim, so every part is modelled the same way (light from the upper left).
Pictograms are small bitmaps written as strings; digits pick colours from a map, a dot is empty.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image, ImageDraw

import font
from palette import BRASS, EMBER, FLAME, IRON, LEATHER, LINEN, MOSS, PARCHMENT, SHADOW, WINE, WOOD
from pix import Color, Pix, Ramp, mix, rgb

# Extra ramps (dark to light) for the guild colours of cards, books and signs.
TEAL: Final[Ramp] = (rgb("#0e2426"), rgb("#1b4547"), rgb("#2e6e6c"), rgb("#4a9a90"), rgb("#8cc8b6"))
PURPLE: Final[Ramp] = (rgb("#1d1030"), rgb("#392052"), rgb("#5a3a7c"), rgb("#7c58a0"), rgb("#a68cc6"))
RUST: Final[Ramp] = (rgb("#3a1508"), rgb("#6a2810"), rgb("#a2441a"), rgb("#d06a2a"), rgb("#f0a258"))
SLATE: Final[Ramp] = (rgb("#16141c"), rgb("#2a2832"), rgb("#403e4c"), rgb("#5c5a68"), rgb("#7e7c8a"))
SKY: Final[Ramp] = (rgb("#1c2638"), rgb("#34486a"), rgb("#5a76a0"), rgb("#8aa4c4"), rgb("#bccade"))
STEEL: Final[Ramp] = (rgb("#1c1b22"), rgb("#383741"), rgb("#5a5964"), rgb("#8a8992"), rgb("#bab8bc"))
SILVER: Final[Ramp] = (rgb("#34303a"), rgb("#625e6a"), rgb("#948f9a"), rgb("#c0bcc0"), rgb("#e6e0d8"))
CLAY: Final[Ramp] = (rgb("#3c1e14"), rgb("#6a3824"), rgb("#98583a"), rgb("#c07c52"), rgb("#dca272"))
CLEAR_GLASS: Final[Ramp] = (rgb("#3a5262"), rgb("#5d8292"), rgb("#8cb2ba"), rgb("#bad4d4"), rgb("#e4f0ec"))
INK: Final[Color] = rgb("#2a1a16")


def five(ramp: Ramp) -> Ramp:
    """A four-tone ramp widened to five by a lighter top tone (palette ramps differ in length)."""
    if len(ramp) >= 5:
        return ramp
    top = ramp[-1]
    return (*ramp, mix(top[:3], (240, 225, 180), 0.35))


class Shape:
    """A mask the size of the canvas, drawn with whole-pixel primitives (a pixel is in or out)."""

    def __init__(self, w: int, h: int) -> None:
        self.w, self.h = w, h
        self.m = Image.new("L", (w, h), 0)
        self.d = ImageDraw.Draw(self.m)

    def rect(self, x: int, y: int, w: int, h: int, on: bool = True) -> Shape:
        if w > 0 and h > 0:
            self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=255 if on else 0)
        return self

    def rrect(self, x: int, y: int, w: int, h: int, on: bool = True) -> Shape:
        """A rectangle with its four corner pixels cut."""
        self.rect(x, y, w, h, on)
        for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
            self.px(cx, cy, False)
        return self

    def ellipse(self, x: int, y: int, w: int, h: int, on: bool = True) -> Shape:
        self.d.ellipse((x, y, x + w - 1, y + h - 1), fill=255 if on else 0)
        return self

    def poly(self, pts: Sequence[tuple[int, int]], on: bool = True) -> Shape:
        self.d.polygon(list(pts), fill=255 if on else 0)
        return self

    def line(self, x0: int, y0: int, x1: int, y1: int, width: int = 1) -> Shape:
        self.d.line((x0, y0, x1, y1), fill=255, width=width)
        return self

    def px(self, x: int, y: int, on: bool = True) -> Shape:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.m.putpixel((x, y), 255 if on else 0)
        return self

    def has(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self.m.getpixel((x, y)) > 0


def _ray(s: Shape, x: int, y: int, dx: int, dy: int, cap: int) -> int:
    d = 1
    while d < cap and s.has(x + dx * d, y + dy * d):
        d += 1
    return d


def fill(p: Pix, s: Shape, ramp: Ramp, outline: Color | None = SHADOW, soft: float = 1.0, base: int | None = None,
         bias: int = 0) -> None:
    """Paints a shape: mid tone inside, lighter towards the upper-left edge, darker towards the lower-right edge."""
    n = len(ramp)
    b = n // 2 if base is None else base
    for y in range(s.h):
        for x in range(s.w):
            if not s.has(x, y):
                continue
            ul = min(_ray(s, x, y, -1, 0, 3), _ray(s, x, y, 0, -1, 3))
            lr = min(_ray(s, x, y, 1, 0, 3), _ray(s, x, y, 0, 1, 3))
            i = b + bias + round((lr - ul) * soft)
            p.px(x, y, ramp[max(0, min(n - 1, i))])
    if outline is not None:
        for y in range(s.h):
            for x in range(s.w):
                if not s.has(x, y) and any(s.has(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    p.px(x, y, outline)


def part(p: Pix, ramp: Ramp, build: Callable[[Shape], object], outline: Color | None = SHADOW, soft: float = 1.0,
         bias: int = 0) -> Shape:
    """Builds a shape with `build(shape)` and paints it at once."""
    s = Shape(p.w, p.h)
    build(s)
    fill(p, s, ramp, outline, soft, bias=bias)
    return s


def inside(p: Pix, s: Shape, x: int, y: int, c: Color) -> None:
    """A pixel that only lands where the shape is, never on its outline."""
    if s.has(x, y):
        p.px(x, y, c)


def grain(p: Pix, s: Shape, x: int, y: int, w: int, h: int, c: Color, horizontal: bool = True, count: int = 4) -> None:
    """Short wood-grain streaks inside a shape (wear and fibre), placed by the canvas' seeded random source."""
    for _ in range(count):
        if horizontal:
            yy = y + p.rng.randrange(max(1, h))
            xx = x + p.rng.randrange(max(1, w))
            for i in range(p.rng.randrange(2, 6)):
                inside(p, s, xx + i, yy, c)
        else:
            xx = x + p.rng.randrange(max(1, w))
            yy = y + p.rng.randrange(max(1, h))
            for i in range(p.rng.randrange(2, 6)):
                inside(p, s, xx, yy + i, c)


def rivet(p: Pix, x: int, y: int, ramp: Ramp = BRASS) -> None:
    """A rivet: one bright pixel (the lit head)."""
    p.px(x, y, ramp[3])


def stud(p: Pix, x: int, y: int, ramp: Ramp = BRASS) -> None:
    """A 2x2 stud with a lit corner and a dark corner."""
    p.px(x, y, ramp[4])
    p.px(x + 1, y, ramp[3])
    p.px(x, y + 1, ramp[2])
    p.px(x + 1, y + 1, ramp[1])


def scribble(p: Pix, x: int, y: int, w: int, rows: int, c: Color, gap: int = 3, seed: int = 1, short_last: bool = True) -> None:
    """Lines of unreadable 'writing': dashes with word gaps, one row every `gap` pixels."""
    import random
    r = random.Random(seed)
    for row in range(rows):
        xx = x
        end = x + w - (r.randrange(2, max(3, w // 2)) if short_last and row == rows - 1 else 0)
        while xx < end:
            n = r.randrange(2, 6)
            p.hline(xx, y + row * gap, min(n, end - xx), c)
            xx += n + 2


def wax_seal(p: Pix, cx: int, cy: int, r: int = 3, ramp: Ramp = WINE, mark: bool = True) -> None:
    """A wax seal: a lumpy disc, lit upper left, with a pressed mark."""
    s = Shape(p.w, p.h)
    s.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1)
    fill(p, s, ramp[1:] if len(ramp) > 4 else ramp, outline=ramp[0], soft=1.0)
    if mark and r >= 3:
        p.px(cx, cy - 1, ramp[1])
        p.px(cx - 1, cy, ramp[1])
        p.px(cx + 1, cy, ramp[1])
        p.px(cx, cy + 1, ramp[1])


# ---------------------------------------------------------------------------------------------- pictograms

ICONS: Final[Mapping[str, Sequence[str]]] = {
    "sword": ["......21", ".....221", "....221.", "...221..", "1.221...", ".121....", "..11....", ".1.11...", "1...1..."],
    "hammer": ["..11111.", ".1222211", ".1222211", "..11111.", "...12...", "...12...", "...12...", "...12...", "...11..."],
    "cross": ["...111...", "...121...", "...121...", "111121111", "122222221", "111121111", "...121...", "...121...", "...111..."],
    "quill": ["......21", ".....221", "....2221", "...2221.", "..222.1.", ".222.1..", ".21.1...", "1..1....", "1......."],
    "flask": ["..2222..", "..1221..", "..1221..", "...11...", "..1221..", ".122221.", "12222221", "11111111"],
    "pick": [".1111111.", "11.....11", "1...2...1", "....2....", "....2....", "....2....", "....2....", "....1...."],
    "banner": ["11111111", "12222221", "12222221", "12222221", "12222221", "12122121", "11.11.11", "1......."],
    "crown": ["1..1..1.", "11.11.11", "12121212", "12222221", "12222221", "11111111"],
    "mug": [".1111111.", ".122222111", ".122222.11", ".122222.11", ".122222111", "..11111.1."],
    "wheat": ["...2.2...", "..22.22..", "...2.2...", "..22.22..", "...2.2...", "..22.22..", "....2....", "....2....", "....2...."],
    "key": [".1111....", "12..21...", "12..21...", ".1111....", "..22.....", "..22.....", "..2221...", "..22.....", "..2221..."],
    "loaf": ["..111111..", ".12222221.", "1221221221", "1222222221", ".11111111."],
    "barrel": ["..111111..", ".12222221.", "1111111111", "1222222221", "1222222221", "1111111111", ".12222221.", "..111111.."],
}


def icon(p: Pix, name: str, x: int, y: int, main: Color, light: Color, shade: Color | None = None, scale: int = 1) -> None:
    """Paints a pictogram: '1' is the main colour, '2' the light one, '3' the shade; `shade` adds a drop shadow."""
    rows = [r.replace(" ", "") for r in ICONS[name]]
    bits = {"1": main, "2": light, "3": shade or main}
    if shade is not None:
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    p.rect(x + i * scale + 1, y + j * scale + 1, scale, scale, shade)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in bits:
                p.rect(x + i * scale, y + j * scale, scale, scale, bits[ch])


def bitmap(p: Pix, rows: Sequence[str], x: int, y: int, cmap: Mapping[str, Color], scale: int = 1) -> None:
    """Paints a custom string bitmap with a colour map (characters not in the map stay empty)."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in cmap:
                p.rect(x + i * scale, y + j * scale, scale, scale, cmap[ch])


def word(p: Pix, x: int, y: int, text: str, c: Color, shade: Color | None = None, scale: int = 1) -> None:
    """Short lettering with an optional drop shadow."""
    if shade is not None:
        font.write(p, x + 1, y + 1, text, shade, scale)
    font.write(p, x, y, text, c, scale)


# Occupied area (x0, y0, x1, y1) of each catalog picture, taken from the exported originals: the game decides what
# shows and what is clickable from the original's alpha, so a drawing must stay inside it.
BBOX: Final[Mapping[str, tuple[int, int, int, int]]] = {
    "items~items_material@chemical1.png": (3, 1, 45, 31),
    "items~items_material@chemical2.png": (3, 1, 45, 31),
    "items~items_material@electronic1.png": (1, 2, 47, 32),
    "items~items_material@electronic2.png": (1, 2, 47, 32),
    "items~items_material@electronic3.png": (1, 1, 47, 31),
    "items~items_material@flux_agent.png": (1, 1, 15, 15),
    "items~items_material@flux_agent_advanced.png": (3, 3, 29, 29),
    "items~items_material@gun_part.png": (1, 1, 47, 32),
    "items~items_material@med1.png": (3, 2, 46, 31),
    "items~items_material@med2.png": (3, 2, 46, 31),
    "items~items_material@metal_ingot.png": (4, 4, 44, 28),
    "items~items_material@nuclear_waste.png": (6, 3, 42, 61),
    "items~items_material@ore1.png": (3, 2, 45, 31),
    "items~items_material@printer_plastic.png": (3, 4, 29, 30),
    "items~items_material@scrap_metal.png": (1, 2, 48, 30),
    "items~items_material@scrap_metal_2.png": (1, 2, 47, 31),
    "items~items_misc@aug_id_guide.png": (5, 1, 26, 31),
    "items~items_misc@blank_card.png": (3, 7, 29, 25),
    "items~items_misc@blank_card_wip.png": (2, 7, 29, 25),
    "items~items_misc@book1.png": (2, 3, 30, 46),
    "items~items_misc@book2.png": (2, 3, 30, 46),
    "items~items_misc@book3.png": (2, 3, 30, 46),
    "items~items_misc@book4.png": (2, 3, 30, 46),
    "items~items_misc@book5.png": (2, 3, 30, 46),
    "items~items_misc@card_brewer.png": (4, 1, 28, 15),
    "items~items_misc@card_chem.png": (4, 1, 28, 15),
    "items~items_misc@card_mining.png": (4, 1, 28, 15),
    "items~items_misc@card_pharma.png": (5, 1, 28, 15),
    "items~items_misc@card_rev.png": (4, 1, 27, 15),
    "items~items_misc@card_wild.png": (4, 1, 27, 15),
    "items~items_misc@cert1.png": (4, 1, 44, 31),
    "items~items_misc@cert2.png": (4, 1, 44, 31),
    "items~items_misc@cert3.png": (4, 1, 44, 31),
    "items~items_misc@cert4.png": (4, 1, 44, 31),
    "items~items_misc@command_keycard.png": (3, 7, 29, 25),
    "items~items_misc@deed.png": (6, 1, 27, 31),
    "items~items_misc@eleanor_perfume.png": (6, 4, 26, 44),
    "items~items_misc@eng_card.png": (3, 7, 29, 25),
    "items~items_misc@exchange_directive.png": (1, 3, 31, 45),
    "items~items_misc@flashlight3.png": (3, 1, 45, 16),
    "items~items_misc@food_stamp.png": (3, 8, 29, 27),
    "items~items_misc@guide0.png": (5, 1, 26, 31),
    "items~items_misc@guide1.png": (5, 1, 26, 31),
    "items~items_misc@guide2.png": (5, 1, 26, 31),
    "items~items_misc@guide3.png": (5, 1, 26, 31),
    "items~items_misc@guide5.png": (5, 1, 26, 31),
    "items~items_misc@handnote.png": (6, 3, 26, 28),
    "items~items_misc@intel_sec.png": (4, 2, 44, 30),
    "items~items_misc@liquid_luck_bottle.png": (1, 0, 15, 32),
    "items~items_misc@liquid_luck_label.png": (2, 1, 14, 26),
    "items~items_misc@manual1.png": (2, 5, 30, 44),
    "items~items_misc@manual4.png": (2, 5, 30, 44),
    "items~items_misc@manual5.png": (2, 5, 30, 44),
    "items~items_misc@med_card.png": (3, 7, 29, 25),
    "items~items_misc@permit_gun_1.png": (3, 7, 29, 25),
    "items~items_misc@permit_gun_2.png": (3, 7, 29, 25),
    "items~items_misc@permit_gun_3.png": (3, 7, 29, 25),
    "items~items_misc@republic_logo_checker.png": (1, 3, 14, 14),
    "items~items_misc@sci_card.png": (3, 7, 29, 25),
    "items~items_misc@scratch.png": (3, 5, 29, 27),
    "items~items_misc@scratch_stack.png": (3, 3, 29, 29),
    "items~items_misc@sec_keycard.png": (3, 7, 29, 25),
    "items~items_misc@sec_slip.png": (1, 1, 31, 15),
    "items~items_misc@ser_card.png": (3, 7, 29, 25),
    "items~items_misc@slip.png": (2, 0, 14, 16),
    "items~items_misc@sup_card.png": (3, 7, 29, 25),
    "items~items_misc@the_coin.png": (1, 1, 15, 15),
    "items~items_mod@10mm_mag_ext_item.png": (0, 3, 16, 45),
    "items~items_mod@10mm_mag_ext_view.png": (0, 9, 16, 26),
    "items~items_mod@10mm_mag_ext_view2.png": (0, 0, 16, 16),
    "items~items_mod@10mm_mag_high_item.png": (0, 1, 15, 31),
    "items~items_mod@10mm_mag_high_view.png": (1, 6, 16, 14),
    "items~items_mod@10mm_mag_item.png": (0, 3, 15, 28),
    "items~items_mod@10mm_mag_smg_box_item.png": (5, 2, 27, 31),
    "items~items_mod@10mm_mag_smg_box_view.png": (0, 0, 16, 29),
    "items~items_mod@10mm_mag_smg_high_item.png": (7, 1, 28, 31),
    "items~items_mod@10mm_mag_smg_high_view.png": (0, 0, 21, 30),
    "items~items_mod@10mm_mag_smg_item.png": (0, 5, 16, 28),
    "items~items_mod@10mm_mag_smg_view.png": (0, 0, 17, 21),
    "items~items_mod@10mm_mag_view.png": (0, 2, 16, 15),
    "items~items_mod@22_mag_ext_item.png": (2, 3, 14, 45),
    "items~items_mod@22_mag_ext_view.png": (0, 0, 14, 16),
    "items~items_mod@22_mag_high_item.png": (2, 1, 14, 31),
    "items~items_mod@22_mag_item.png": (2, 4, 14, 29),
    "items~items_mod@22_mag_view.png": (3, 0, 16, 8),
    "items~items_mod@barrel_item.png": (1, 5, 30, 12),
    "items~items_mod@barrel_view.png": (0, 4, 29, 11),
    "items~items_mod@bipod_item.png": (4, 1, 43, 15),
    "items~items_mod@bipod_view.png": (7, 0, 43, 35),
    "items~items_mod@bottle_item.png": (2, 1, 47, 15),
    "items~items_mod@bottle_view.png": (0, 1, 45, 15),
    "items~items_mod@compensator_item.png": (0, 2, 16, 14),
    "items~items_mod@compensator_view.png": (0, 0, 16, 12),
    "items~items_mod@gl_item.png": (1, 0, 63, 16),
    "items~items_mod@gl_view.png": (0, 0, 61, 20),
    "items~items_mod@grip_item.png": (0, 2, 16, 30),
    "items~items_mod@grip_view.png": (7, 0, 43, 31),
    "items~items_mod@laser2_item.png": (3, 3, 13, 13),
    "items~items_mod@laser2_view.png": (0, 0, 26, 9),
    "items~items_mod@laser_item.png": (3, 3, 13, 13),
    "items~items_mod@laser_toy_item.png": (3, 5, 29, 12),
    "items~items_mod@laser_toy_view.png": (0, 0, 40, 13),
    "items~items_mod@laser_view.png": (0, 0, 26, 9),
    "items~items_mod@rds_item.png": (2, 1, 14, 16),
    "items~items_mod@rds_makeshift_item.png": (2, 1, 14, 16),
    "items~items_mod@rds_makeshift_view.png": (0, 0, 9, 18),
    "items~items_mod@rds_view.png": (1, 0, 9, 4),
    "items~items_mod@rds_view2.png": (0, 0, 11, 13),
    "items~items_mod@short_stock_item.png": (1, 0, 15, 32),
    "items~items_mod@short_stock_view.png": (14, 0, 32, 32),
    "items~items_mod@silencer2_item.png": (2, 2, 47, 15),
    "items~items_mod@silencer2_view.png": (0, 0, 45, 13),
    "items~items_mod@silencer_item.png": (2, 3, 30, 12),
    "items~items_mod@silencer_view.png": (0, 3, 28, 12),
    "items~items_mod@special_mod.png": (3, 1, 29, 15),
    "items~items_mod@special_mod1.png": (2, 2, 14, 14),
    "items~items_mod@stock_item.png": (4, 1, 45, 32),
    "items~items_mod@stock_view.png": (7, 0, 48, 31),
    "items~items_sign@berry_sign.png": (0, 1, 32, 31),
    "items~items_sign@black_lamp.png": (3, 4, 29, 44),
    "items~items_sign@black_lamp_on_1.png": (2, 4, 30, 44),
    "items~items_sign@black_lamp_on_2.png": (2, 4, 30, 44),
    "items~items_sign@black_lamp_on_3.png": (2, 4, 30, 44),
    "items~items_sign@black_lamp_on_alt_1.png": (2, 4, 30, 44),
    "items~items_sign@black_lamp_on_alt_2.png": (2, 4, 30, 44),
    "items~items_sign@black_lamp_on_alt_3.png": (2, 4, 30, 44),
    "items~items_sign@food_sign.png": (0, 1, 32, 31),
    "items~items_sign@gun_sign.png": (0, 1, 32, 31),
    "items~items_sign@gun_sign2.png": (0, 1, 64, 31),
    "items~items_sign@hiring_sign.png": (0, 1, 96, 31),
    "items~items_sign@household_sign.png": (0, 1, 32, 31),
    "items~items_sign@items_sign_1.png": (0, 1, 96, 31),
    "items~items_sign@material_sign.png": (0, 1, 32, 31),
    "items~items_sign@medical_sign.png": (0, 1, 32, 31),
    "items~items_sign@water_on.png": (0, 1, 63, 31),
    "items~items_sign@water_sign.png": (0, 1, 32, 47),
    "items~items_misc@republic_transmitter.png": (1, 1, 15, 15),
}


def conform(assets: Mapping[str, Callable[[], Image.Image]]) -> dict[str, Callable[[], Image.Image]]:
    """Wraps each drawing so that nothing leaves the original's occupied area: a drawing whose dark outline spills over
    the area is cropped to it and its new outermost pixels become the outline (so the shape shrinks by a pixel, not clips)."""
    def wrap(name: str, draw: Callable[[], Image.Image]) -> Callable[[], Image.Image]:
        def run() -> Image.Image:
            im = draw()
            box = BBOX.get(name)
            alpha = im.getchannel("A").point(lambda a: 255 if a > 8 else 0)
            got = alpha.getbbox()
            if box is None or got is None or (got[0] >= box[0] and got[1] >= box[1] and got[2] <= box[2] and got[3] <= box[3]):
                return im
            keep = Image.new("L", im.size, 0)
            keep.paste(255, box)
            im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), keep))
            p = Pix(im.width, im.height)
            p.im = im
            p.draw = ImageDraw.Draw(im)
            for x in range(im.width):
                for y in range(im.height):
                    if got[0] <= x < got[2] and got[1] <= y < got[3] and im.getpixel((x, y))[3] > 8:
                        edge = any(not (0 <= x + dx < im.width and 0 <= y + dy < im.height) or im.getpixel((x + dx, y + dy))[3] <= 8
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                        clipped = x in (box[0], box[2] - 1) or y in (box[1], box[3] - 1)
                        if edge and clipped:
                            im.putpixel((x, y), (*SHADOW, 255))
            return im
        return run
    return {name: wrap(name, fn) for name, fn in assets.items()}


__all__ = [name for name in dir() if not name.startswith("_")] + ["LEATHER", "LINEN", "MOSS", "FLAME", "EMBER", "IRON", "WOOD", "PARCHMENT"]
