"""Colour guides of the appraisal screens as a dyer's shop would have them: cards of woollen swatches, a strip of dyed
squares beside a touchstone, the purity scale, and the little gauges.

Where the game compares a detail of an item with a guide, the guide keeps the same layout and order as the game's:
five swatch columns on the cards, six squares on the strip, six rows on the purity scale. Only the look is medieval
(wool dyed with weld, madder, woad and oak gall; slate; linen; waxed oak). The other reference pictures (letters, seals,
logos, chips) are in appraisal_c_marks.py and the open tools in appraisal_c_tools.py.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from PIL import Image

from appraisalkit_c import VIOLET, Shape, cloth, fill, stitch
from pix import CLEAR, Color, Pix, mix

LIGHT: Color = (255, 224, 150)

# five dyes of the item card and of the "ok" strip: undyed wool, weld, madder-orange, madder red, oak-gall brown
CARD_OK: tuple[Color, ...] = ((218, 204, 164), (200, 152, 78), (176, 100, 64), (132, 48, 46), (78, 40, 46))
# the second card: woad-bleached green, heather, mulberry, indigo, soot
CARD_CHECK: tuple[Color, ...] = ((148, 190, 176), (126, 72, 126), (84, 46, 104), (48, 56, 102), (38, 30, 46))
# the saturation strip: grey wool beside three strengths of madder, then dark
CARD_SAT: tuple[Color, ...] = ((170, 172, 160), (204, 112, 72), (162, 72, 56), (150, 50, 50), (44, 34, 46))
# the dyer's test strip, weakest madder to deepest green
STRIP: tuple[Color, ...] = ((116, 50, 62), (154, 76, 62), (190, 138, 84), (206, 184, 134), (124, 176, 84), (62, 130, 64))
PURITY: tuple[Color, ...] = ((62, 120, 70), (120, 168, 84), (206, 182, 122), (188, 134, 72), (172, 94, 66), (130, 50, 54))


def swatch_card(w: int, h: int, colours: Sequence[Color], seed: int, vertical_only: bool = False, hem: int = 0) -> Image.Image:
    """Equal columns of woollen swatches side by side, each with a seam; `hem` rows at the top and bottom carry the
    stitching of the card and stay unstretched when the game scales the card."""
    p = Pix(w, h, seed=seed)
    n = len(colours)
    for i, c in enumerate(colours):
        x0, x1 = w * i // n, w * (i + 1) // n
        cloth(p, x0, 0, x1 - x0, h, c, vertical_only)
        if hem:
            thread = mix(c, LIGHT, 0.5)
            under = mix(c, VIOLET, 0.35)
            p.hline(x0 + 1, 0, x1 - x0 - 2, mix(c, LIGHT, 0.32))
            p.hline(x0 + 1, hem - 1, x1 - x0 - 2, under)
            for xx in range(x0 + 2, x1 - 3, 3):
                p.hline(xx, 1, 2, thread)
                p.hline(xx, h - hem + 1, 2, thread)
            p.hline(x0 + 1, h - hem, x1 - x0 - 2, under)
            p.hline(x0 + 1, h - 1, x1 - x0 - 2, mix(c, VIOLET, 0.55))
    return p.finish()


def nibble(im: Image.Image, n: int) -> Image.Image:
    """Makes the corner pixel (n=1) or a 2x2 block (n=2) of every corner transparent, as the game's originals are."""
    w, h = im.size
    for x0, y0 in ((0, 0), (w - n, 0), (0, h - n), (w - n, h - n)):
        for dx in range(n):
            for dy in range(n):
                im.putpixel((x0 + dx, y0 + dy), (0, 0, 0, 0))
    return im


def item_card() -> Image.Image:
    # the game stretches this picture downwards between 4 pixels at the top and 4 at the bottom: only warp threads there
    return nibble(swatch_card(110, 126, CARD_OK, 11, vertical_only=True, hem=4), 2)


def check_card() -> Image.Image:
    return nibble(swatch_card(55, 63, CARD_CHECK, 12), 1)


def ok_card() -> Image.Image:
    return swatch_card(55, 25, CARD_OK, 13)


def sat_card() -> Image.Image:
    return swatch_card(55, 25, CARD_SAT, 14)


def test_strips() -> Image.Image:
    """A linen strip: a slate touchstone on the left (the grey of the game's guide) and six squares of dyed cloth."""
    p = Pix(264, 40, seed=15)
    p.rect(0, 0, 264, 40, VIOLET)
    # linen ground with a lit top edge and a soft shaded foot
    linen = (214, 208, 180)
    p.rect(1, 1, 262, 38, linen)
    linen_threads(p, 66, 1, 197, 38)
    p.hline(66, 1, 197, mix(linen, LIGHT, 0.5))
    p.hline(66, 37, 197, mix(linen, VIOLET, 0.18))
    p.hline(66, 38, 197, mix(linen, VIOLET, 0.35))
    # the touchstone
    slate = Shape(264, 40).rect(1, 1, 65, 38)
    fill(p, slate, (136, 148, 138))
    p.speckle(2, 2, 63, 36, [(122, 134, 126), (150, 160, 150), (112, 122, 118)], 0.09)
    for y in range(2, 38):                                    # layers of the stone
        if y % 7 == 3:
            p.hline(2, y, 62 - (y * 5) % 17, (124, 136, 128))
            p.hline(8 + (y * 3) % 11, y + 1, 40, (150, 160, 152))
    p.hline(1, 1, 65, (166, 176, 164))
    p.vline(1, 1, 38, (158, 168, 158))
    p.hline(1, 38, 65, (96, 106, 102))
    p.vline(65, 1, 38, (104, 114, 108))
    p.line(30, 14, 36, 24, (106, 118, 112))                   # a vein of the stone
    p.line(36, 24, 34, 29, (106, 118, 112))
    for k, c in enumerate(STRIP):
        x0 = (77, 107, 136, 165, 194, 223)[k]
        w = 19 if k < 2 else 18
        cloth(p, x0, 1, w, 19, c)
        p.hline(x0, 1, w, mix(c, LIGHT, 0.4))
        p.hline(x0, 19, w, mix(c, VIOLET, 0.45))
        stitch(p, x0 + 1, 3, x0 + w - 2, 3, mix(c, LIGHT, 0.5), 3)       # the stitched hem of each square
        p.px(x0 + w // 2, 28, mix(linen, VIOLET, 0.3))                   # a tick mark below it
        p.vline(x0 + w // 2, 25, 4, mix(linen, VIOLET, 0.3))
    return nibble(p.finish(), 1)


def linen_threads(p: Pix, x: int, y: int, w: int, h: int) -> None:
    for j in range(0, h, 3):
        for i in range(w):
            if p.rng.random() < 0.08:
                p.px(x + i, y + j, (200, 194, 164))
    for i in range(0, w, 4):
        p.vline(x + i, y, h, (208, 202, 174)) if i % 8 == 0 else None


def purity_scale() -> Image.Image:
    """Six rows, from the clear green of clean water to the red of foul: a dyed swatch on the left of each row and two
    halves of tinted glass (half transparent, as the game's rows are) that the numbers show through."""
    p = Pix(628, 804, seed=16)
    for k, c in enumerate(PURITY):
        y = 160 + 32 * k
        # the tinted glass first, then the swatch over its left end
        for x0, x1 in ((114, 331), (336, 569)):
            for yy in range(y, y + 28):
                for xx in range(x0, x1 + 1):
                    if (xx == x1 or (xx == x0 and x0 != 114)) and (yy in (y, y + 27)):
                        continue
                    edge = yy == y or xx == x0
                    shade = yy == y + 27 or xx == x1
                    tone = mix(c, LIGHT, 0.25) if edge else mix(c, VIOLET, 0.3) if shade else c
                    p.px(xx, yy, (*tone, 150 if (edge or shade) else 128))
        cloth(p, 98, y, 16, 28, c)
        p.hline(98, y, 16, mix(c, LIGHT, 0.4))
        p.hline(98, y + 27, 16, mix(c, VIOLET, 0.45))
        stitch(p, 100, y + 2, 111, y + 2, mix(c, LIGHT, 0.5), 3)
        for x0, x1 in ((98, 331), (336, 569)):                       # the game rounds each row: 2 pixels, then 1
            for k, n in ((0, 2), (1, 2)):
                for i in range(n):
                    for yy in (y + k, y + 27 - k):
                        p.px(x0 + i, yy, CLEAR)
                        p.px(x1 - i, yy, CLEAR)
    return p.finish()


def color_guide() -> Image.Image:
    """Two columns, a light-to-dark moss cloth and a light-to-dark grey linen: the sample of a colour in three lights."""
    p = Pix(12, 21, seed=17)
    for x0, rows in ((0, ((122, 176, 84), (62, 130, 64), (50, 92, 56))), (6, ((206, 202, 176), (164, 170, 160), (140, 150, 140)))):
        for (y0, y1), c in zip(((0, 3), (3, 18), (18, 21)), rows):
            cloth(p, x0, y0, 6, y1 - y0, c, vertical_only=True)
    p.vline(5, 0, 21, (36, 44, 40))
    p.vline(6, 0, 21, (170, 176, 160))
    return p.finish()


def indicator(body: Sequence[Color]) -> Callable[[], Image.Image]:
    """A wooden trough 15x6 with a bar of coloured wax filling the right of it."""
    def draw() -> Image.Image:
        p = Pix(15, 6, VIOLET, seed=18)
        p.hline(0, 0, 15, (58, 46, 62))
        p.hline(0, 5, 15, (30, 22, 34))
        for x in range(1, 9, 3):
            p.px(x, 5, (84, 62, 40))
        p.rect(9, 0, 5, 6, body[1])
        p.hline(9, 0, 5, body[0])
        p.hline(9, 1, 5, mix(body[0], body[1], 0.5))
        p.rect(9, 4, 5, 2, body[2])
        p.vline(13, 1, 5, body[2])
        return p.finish()
    return draw


GREEN = ((136, 190, 90), (74, 138, 70), (50, 96, 58))
ORANGE = ((206, 134, 82), (176, 100, 64), (128, 60, 50))
RED = ((120, 52, 62), (108, 40, 52), (78, 30, 42))

ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "cigarette_color_card_item.110x126.png": item_card,
    "colorChecker.55x63.png": check_card,
    "cropped-color-ok.55x25.png": ok_card,
    "cropped-color-saturation.55x25.png": sat_card,
    "test_strips.264x40.png": test_strips,
    "water_purity_2x.628x804.png": purity_scale,
    "guide_color_guide.12x21.png": color_guide,
    "guide_indicator_green.15x6.png": indicator(GREEN),
    "guide_indicator_orange.15x6.png": indicator(ORANGE),
    "guide_indicator_red.15x6.png": indicator(RED),
}
