"""The comparison guides of the appraisal screens that show a mark: a scribe's lettering, a guild's emblems, a wax seal and
a warded lock plate, each as a correct sample and a wrong one in the same place and the same size as the game's.

The player holds an item's detail against the guide, so every pair differs in one thing you can see: a missing letter, a
leaf and a curl less in the vine, a wing less on the plaque, a cracked seal, a split plate, an empty field, a lattice for a
crust. The colour guides are in appraisal_c.py. Text uses the pack's 5x7 face (font.py) or letters drawn here.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from PIL import Image

import font
from appraisalkit_c import VIOLET, Shape, bevel, fill, rivet
from palette import BRASS, IRON, LEATHER, NAVY, PARCHMENT, WINE
from pix import CLEAR, Color, Pix, mix

LIGHT: Color = (255, 224, 150)

# ------------------------------------------------------------------------------------------------ lettering

# Lower-case textura of the specimen "Innkeeper", 6 pixels wide, two pixel stems; the row number is the first row
GLYPHS: dict[str, tuple[int, tuple[str, ...]]] = {
    "I": (1, ("#####.", "#####.", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "#####.", "#####.")),
    "n": (5, ("####..", "######", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##")),
    "k": (0, ("##....", "##....", "##....", "##....", "##....", "##..##", "##.##.", "####..", "####..", "##.##.", "##..##", "##..##",
              "##..##")),
    "e": (5, (".####.", "##..##", "##..##", "######", "##....", "##..##", "##..##", ".####.")),
    "p": (5, ("#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "#####.", "##....", "##....", "##....")),
    "r": (5, ("##.###", "####..", "###...", "##....", "##....", "##....", "##....", "##....")),
}

# the heavy capitals of the font specimen, 6 x 10
CAPS: dict[str, tuple[str, ...]] = {
    "I": ("######", "######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "######", "######"),
    "N": ("###.##", "###.##", "######", "######", "######", "######", "##.###", "##.###", "##..##", "##..##"),
    "K": ("##..##", "##.##.", "####..", "###...", "###...", "####..", "####..", "##.##.", "##..##", "##..##"),
    "E": ("######", "######", "##....", "#####.", "#####.", "##....", "##....", "##....", "######", "######"),
    "P": ("#####.", "######", "##..##", "##..##", "######", "#####.", "##....", "##....", "##....", "##...."),
    "R": ("#####.", "######", "##..##", "##..##", "######", "#####.", "##.##.", "##..##", "##..##", "##..##"),
}

INK: Color = (52, 34, 54)               # iron-gall ink: a brown that is nearly violet


def ink_pass(p: Pix, body: Color, lit: Color, shade: Color) -> None:
    """Gives flat lettering a pen's sheen: the edges toward the light are lighter, the ones away from it darker."""
    src = p.im.copy()

    def solid(x: int, y: int) -> bool:
        return 0 <= x < p.w and 0 <= y < p.h and src.getpixel((x, y))[3] > 0  # type: ignore[index]

    for y in range(p.h):
        for x in range(p.w):
            if solid(x, y):
                if not solid(x - 1, y - 1) or not solid(x - 1, y) and not solid(x, y - 1):
                    p.px(x, y, lit)
                elif not solid(x + 1, y + 1) and not solid(x, y + 1) and not solid(x + 1, y):
                    p.px(x, y, shade)
                else:
                    p.px(x, y, body)


def blackletter(word: str, w: int, h: int) -> Image.Image:
    p = Pix(w, h, seed=21)
    for i, ch in enumerate(word):
        top, rows = GLYPHS[ch]
        for j, row in enumerate(rows):
            for k, bit in enumerate(row):
                if bit == "#":
                    p.px(i * 7 + k, top + j, INK)
    ink_pass(p, INK, mix(INK, (120, 84, 80), 0.7), mix(INK, VIOLET, 0.6))
    return p.finish()


def caps_specimen() -> Image.Image:
    p = Pix(62, 10, seed=22)
    for i, ch in enumerate("INNKEEPER"):
        for j, row in enumerate(CAPS[ch]):
            for k, bit in enumerate(row):
                if bit == "#":
                    p.px(i * 7 + k, j, INK)
    ink_pass(p, INK, mix(INK, (120, 84, 80), 0.7), mix(INK, VIOLET, 0.6))
    return p.finish()


def charter_lines(lines: Sequence[str], w: int, h: int, scale: int) -> Image.Image:
    """Three lines of the small face in iron-gall blue on a transparent field, as a notice's heading."""
    p = Pix(w, h, seed=23)
    ink = (46, 46, 98)
    for i, text in enumerate(lines):
        font.write(p, 0, i * 10 * scale, text, ink, scale)
        if scale == 1:
            font.write(p, 1, i * 10, text, ink)                 # struck twice: the heavy stroke of a scribe's pen
    ink_pass(p, ink, mix(ink, (130, 130, 190), 0.3), mix(ink, VIOLET, 0.6))
    return p.finish()


# ------------------------------------------------------------------------------------------------ vine emblem

VINE: Color = (178, 104, 66)


def vine_half(w: int, h: int, rich: bool) -> Pix:
    """The left vine of the guild emblem: a stem curling up from the foot, a trefoil on top and, on the correct emblem,
    a curl at the foot, two broad leaves, a trailing leaf and a side shoot."""
    s = Shape(w, h)
    d = s._d
    stem = [(23, 64), (23, 59), (21, 53), (17, 47), (14, 41), (14, 35), (16, 29), (19, 23), (22, 17), (23, 11), (23, 5)]
    d.line(stem, fill=255, width=3, joint="curve")
    s.poly([(23, 0), (25, 3), (23, 8), (21, 3)])                          # the trefoil
    s.poly([(23, 7), (17, 4), (14, 6), (19, 9)])
    s.poly([(23, 7), (29, 4), (32, 6), (27, 9)])
    if rich:
        d.line([(23, 59), (19, 56), (14, 55), (9, 57), (8, 61), (11, 63), (14, 61), (12, 59)], fill=255, width=2)
        s.poly([(14, 36), (9, 35), (5, 31), (5, 26), (10, 28), (14, 32)])   # a broad leaf on the outside
        s.poly([(18, 27), (24, 24), (29, 25), (27, 29), (21, 30)])           # a leaf toward the cross
        s.poly([(15, 47), (9, 43), (2, 43), (0, 46), (5, 46), (12, 49)])     # the long trailing leaf
        d.line([(21, 53), (26, 51), (30, 53)], fill=255, width=2)
        s.poly([(30, 53), (33, 50), (32, 55)])
    p = Pix(w, h)
    fill(p, s, VINE)
    bevel(p, s, mix(VINE, LIGHT, 0.4), mix(VINE, VIOLET, 0.45), None)
    return p


def mirror(left: Pix, w: int) -> Image.Image:
    return left.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((w, left.h))


def guild_emblem(rich: bool) -> Callable[[], Image.Image]:
    def draw() -> Image.Image:
        w, h = (75, 65) if rich else (71, 65)
        p = Pix(w, h, seed=24 if rich else 25)
        shift = 0 if rich else -2                                 # the plain emblem is a little narrower
        left = vine_half(w, h, rich)
        right = left.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        p.paste(left.im, shift, 0)
        p.paste(right, w - left.w + (-shift), 0)
        cx = w // 2
        s = Shape(w, h)
        s.rect(cx - 3, 12, cx + 3, 60)
        s.rect(cx - 12, 27, cx + 12, 33)
        if rich:
            s.poly([(cx - 5, 10), (cx + 5, 10), (cx + 4, 16), (cx - 4, 16)])      # flared ends of a cross pattee
            s.poly([(cx - 5, 62), (cx + 5, 62), (cx + 4, 56), (cx - 4, 56)])
            s.poly([(cx - 14, 25), (cx - 14, 35), (cx - 8, 33), (cx - 8, 27)])
            s.poly([(cx + 14, 25), (cx + 14, 35), (cx + 8, 33), (cx + 8, 27)])
            s.ellipse(cx - 10, 20, cx + 10, 40)
            s.ellipse(cx - 7, 23, cx + 7, 37, on=False)
            s.rect(cx - 3, 12, cx + 3, 20)
            s.rect(cx - 3, 40, cx + 3, 60)
            s.rect(cx - 12, 27, cx - 7, 33)
            s.rect(cx + 7, 27, cx + 12, 33)
        fill(p, s, WINE[2])
        bevel(p, s, WINE[4], WINE[0], None)
        if rich:
            for y0 in (18, 44, 50):                                # slits cut into the bars
                p.vline(cx, y0, 4, WINE[0])
                p.vline(cx - 1, y0, 4, WINE[3])
            for x0 in (cx - 11, cx + 9):
                p.hline(x0, 30, 2, WINE[0])
            p.rect(cx - 2, 29, 5, 3, BRASS[3])                       # a brass boss at the crossing
            p.hline(cx - 2, 29, 5, BRASS[4])
            p.hline(cx - 2, 31, 5, BRASS[1])
            p.px(cx, 30, BRASS[0])
        return p.finish()
    return draw


# ------------------------------------------------------------------------------------------------ plaques

def corner_cut(p: Pix, steps: Sequence[int]) -> None:
    """Makes the corners transparent in steps (the widths of the cut in each row from the corner), as the game rounds."""
    for row, n in enumerate(steps):
        for i in range(n):
            for x, y in ((i, row), (p.w - 1 - i, row), (i, p.h - 1 - row), (p.w - 1 - i, p.h - 1 - row)):
                p.px(x, y, CLEAR)


def plaque(wings: int) -> Callable[[], Image.Image]:
    """A dark iron plaque with a brass sun-and-compass in a ring, rays beyond it and a pair of wings at the foot."""
    def draw() -> Image.Image:
        p = Pix(55, 39, VIOLET, seed=26)
        p.hline(0, 0, 55, mix(VIOLET, (110, 90, 120), 0.35))              # lit top edge of the iron
        p.vline(0, 0, 39, mix(VIOLET, (110, 90, 120), 0.25))
        p.hline(0, 38, 55, mix(VIOLET, (0, 0, 0), 0.4))
        for x, y in ((3, 3), (49, 3), (3, 33), (49, 33)):
            rivet(p, x, y, IRON)
        cx, cy = 27, 19
        ring = Shape(55, 39).ellipse(cx - 13, cy - 14, cx + 13, cy + 14)
        ring.ellipse(cx - 11, cy - 12, cx + 11, cy + 12, on=False)
        field = Shape(55, 39).ellipse(cx - 11, cy - 12, cx + 11, cy + 12)
        fill(p, field, NAVY[1])
        for x, y in field.cells():
            if (x - cx) + (y - cy) > 6:
                p.px(x, y, NAVY[0])
        fill(p, ring, BRASS[2])
        bevel(p, ring, BRASS[4], BRASS[0], None)
        # rays through the ring, with short ticks at their ends
        p.vline(cx, 2, 35, BRASS[3])
        p.vline(cx - 1, 2, 35, BRASS[4])
        p.hline(cx - 17, cy, 35, BRASS[3])
        p.hline(cx - 17, cy - 1, 35, BRASS[4])
        for dx in (-3, 3):
            p.vline(cx + dx, 2, 4, BRASS[2])
            p.vline(cx + dx, 33, 4, BRASS[2])
        for sx in (-1, 1):
            for dy in (-4, 4):
                p.hline(cx + sx * 15 - (1 if sx > 0 else 0), cy + dy, 3, BRASS[2])
        # arrow heads on the ring, pointing in, and four on the diagonals inside
        for dx, dy, pts in ((0, -1, [(0, -10), (-3, -6), (3, -6)]), (0, 1, [(0, 10), (-3, 6), (3, 6)]),
                            (-1, 0, [(-10, 0), (-6, -3), (-6, 3)]), (1, 0, [(10, 0), (6, -3), (6, 3)])):
            p.poly([(cx + a, cy + b) for a, b in pts], BRASS[4])
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p.poly([(cx + sx * 7, cy + sy * 7), (cx + sx * 7, cy + sy * 3), (cx + sx * 3, cy + sy * 7)], BRASS[3])
            p.line(cx + sx * 3, cy + sy * 3, cx + sx * 6, cy + sy * 6, BRASS[3])
        p.rect(cx - 2, cy - 2, 5, 5, BRASS[3])
        p.rect(cx - 1, cy - 1, 3, 3, NAVY[0])
        p.px(cx - 2, cy - 2, BRASS[4])
        # wings at the foot
        bars = ((6, 29, 14, BRASS[4]), (9, 32, 17, BRASS[2]), (14, 35, 10, BRASS[3])) if wings == 2 else ((6, 32, 17, BRASS[2]),)
        for x0, y0, ln, c in bars:
            p.hline(x0, y0, ln, c)
            p.hline(55 - x0 - ln, y0, ln, c)
            p.hline(x0 + 1, y0 + 1, ln - 1, mix(c, VIOLET, 0.55))
            p.hline(55 - x0 - ln, y0 + 1, ln - 1, mix(c, VIOLET, 0.55))
        corner_cut(p, (4, 2, 1, 1))
        return p.finish()
    return draw


# ------------------------------------------------------------------------------------------------ signboard labels

CREAM = ((140, 112, 70), (190, 164, 110), (222, 204, 156), (238, 224, 180))


def label_frame(w: int, h: int, field: Color, seed: int) -> Pix:
    """A signboard label: parchment border three pixels wide, rounded, with a coloured field inside."""
    p = Pix(w, h, seed=seed)
    outer = Shape(w, h).rect(0, 0, w - 1, h - 1)
    fill(p, outer, CREAM[2])
    bevel(p, outer, CREAM[3], CREAM[1], None)
    inner = Shape(w, h).rect(3, 3, w - 4, h - 4)
    fill(p, inner, field)
    p.hline(3, 3, w - 6, mix(field, VIOLET, 0.35))
    p.vline(3, 3, h - 6, mix(field, VIOLET, 0.25))
    p.hline(3, h - 4, w - 6, mix(field, LIGHT, 0.18))
    p.vline(w - 4, 3, h - 6, mix(field, LIGHT, 0.12))
    return p


def tankard_label(mark: bool) -> Callable[[], Image.Image]:
    """A wine-red label; the correct one carries a foaming tankard, the wrong one is empty."""
    def draw() -> Image.Image:
        h = 26 if mark else 27
        p = label_frame(29, h, WINE[3], 31)
        p.dither(4, h - 8, 21, 4, WINE[2], 0.25)
        if mark:
            body = Shape(29, h).rect(8, 10, 18, 21)
            fill(p, body, (214, 198, 150))
            bevel(p, body, (244, 232, 190), (150, 120, 80), None)
            for y in (13, 18):                                          # iron hoops
                p.hline(8, y, 11, (92, 84, 96))
                p.hline(8, y + 1, 11, (58, 52, 64))
            handle = Shape(29, h).rect(19, 12, 23, 19).rect(19, 14, 21, 17, on=False)
            fill(p, handle, (190, 158, 104))
            bevel(p, handle, (230, 214, 168), (120, 92, 60), None)
            for x, y, r in ((8, 7, 3), (11, 6, 4), (15, 7, 3), (18, 8, 2)):   # foam
                p.ellipse(x, y, r * 2 - 1, r * 2 - 1, (246, 238, 214))
            p.hline(9, 10, 9, (200, 184, 140))
            p.px(10, 6, (255, 252, 236))
        corner_cut(p, (2, 1))
        return p.finish()
    return draw


def pie_label(correct: bool) -> Callable[[], Image.Image]:
    """A green label with a baker's pie: a domed lid, a crimped seam and a flat base; the wrong one has a lattice top."""
    def draw() -> Image.Image:
        p = label_frame(38, 19, (84, 106, 66), 32)
        crust, lit, shade = (226, 208, 160), (246, 236, 196), (170, 140, 90)
        if correct:
            lid = Shape(38, 19).rrect(7, 4, 30, 8, 3).rect(7, 7, 30, 8)
            fill(p, lid, crust)
            bevel(p, lid, lit, shade, None)
            for x in range(8, 30, 4):                                  # the crimped seam
                p.hline(x, 10, 2, crust)
                p.hline(x + 2, 11, 2, crust)
                p.px(x + 1, 9, shade)
            p.hline(7, 9, 24, (84, 106, 66))
            base = Shape(38, 19).rect(7, 12, 30, 15)
            fill(p, base, crust)
            bevel(p, base, lit, shade, None)
        else:
            lid = Shape(38, 19).rrect(11, 3, 26, 6, 2)
            fill(p, lid, crust)
            bevel(p, lid, lit, shade, None)
            for y in range(7, 13):                                      # lattice instead of a lid
                for x in range(11, 27):
                    if (x + y) % 4 in (0, 1) and (x - y) % 4 in (0, 1) or y % 2 == 0 and x % 4 < 3:
                        p.px(x, y, crust if (x + y) % 2 else shade)
            p.hline(11, 13, 16, crust)
            p.hline(11, 14, 16, shade)
        corner_cut(p, (2, 1))
        return p.finish()
    return draw


# ------------------------------------------------------------------------------------------------ lock plates

def warded_plate() -> Pix:
    p = Pix(21, 17, seed=41)
    plate = Shape(21, 17).rect(0, 0, 20, 16)
    fill(p, plate, BRASS[2])
    p.rect(1, 1, 6, 4, BRASS[3])                                       # the polished bit
    p.hline(1, 1, 6, mix(BRASS[3], LIGHT, 0.5))
    for y in (5, 9, 13):
        p.hline(1, y, 7 if y < 13 else 5, BRASS[1])
        p.hline(13, y - 1 if y > 5 else y, 6, BRASS[1])
    for x in (7, 13):
        p.vline(x, 5, 9, BRASS[1])
    p.vline(10, 1, 5, BRASS[1])
    p.hline(8, 3, 4, BRASS[1])
    p.hline(14, 7, 5, BRASS[3])
    p.hline(8, 11, 5, BRASS[3])
    p.rect(14, 10, 4, 3, BRASS[3])
    for y in range(1, 16):                                              # a worn brightening beside every channel
        for x in range(1, 20):
            if p.get(x, y)[:3] == BRASS[2] and p.get(x - 1, y)[:3] == BRASS[1]:
                p.px(x, y, BRASS[3])
    bevel(p, plate, BRASS[3], BRASS[0], BRASS[0])
    return p


def chip(split: bool) -> Callable[[], Image.Image]:
    def draw() -> Image.Image:
        p = warded_plate()
        if split:
            right = p.im.crop((12, 0, 21, 17))
            p.rect(11, 0, 10, 17, CLEAR)
            p.paste(right, 12, 0)
            zig = [10, 11, 10, 11, 12, 11, 12, 11, 10, 11, 12, 11, 10, 11, 12, 11, 10]
            for y, x in enumerate(zig):                                  # the crack, dark with a bright broken edge
                p.px(x, y, (36, 22, 24))
                p.px(x + 1, y, (36, 22, 24))
                p.px(x - 1, y, BRASS[4] if y % 2 == 0 else BRASS[1])
            p.px(11, 16, (36, 22, 24))
            p.px(11, 7, (150, 190, 190))                                 # a sliver of light through it
            p.px(11, 8, (110, 150, 156))
        corner_cut(p, (2, 1))
        return p.finish()
    return draw


# ------------------------------------------------------------------------------------------------ wax seal

WAX: tuple[Color, ...] = ((24, 40, 28), (40, 70, 44), (66, 106, 60), (100, 144, 86), (152, 186, 122))


def seal_body(p: Pix, cx: int, cy: int) -> None:
    """A green wax seal with a ragged edge, a pressed ring and a cross."""
    s = Shape(p.w, p.h).ellipse(cx - 10, cy - 11, cx + 10, cy + 11)
    for x, y in ((cx - 11, cy - 3), (cx + 11, cy + 4), (cx - 5, cy + 12), (cx + 6, cy - 12), (cx + 10, cy - 8), (cx - 9, cy + 8)):
        s.rect(x, y, x + 1, y + 1)
    fill(p, s, WAX[2])
    bevel(p, s, WAX[4], WAX[0], WAX[0], hi2=WAX[3])
    ring = Shape(p.w, p.h).ellipse(cx - 7, cy - 8, cx + 7, cy + 8)
    ring.ellipse(cx - 5, cy - 6, cx + 5, cy + 6, on=False)
    for x, y in ring.cells():
        p.px(x, y, WAX[1] if x + y > cx + cy else WAX[3])
    p.rect(cx - 1, cy - 4, 3, 9, WAX[3])
    p.rect(cx - 3, cy - 1, 7, 3, WAX[3])
    p.vline(cx + 1, cy - 4, 9, WAX[1])
    p.hline(cx - 3, cy + 1, 7, WAX[1])
    for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        p.px(cx + dx, cy + dy, WAX[4] if dx < 0 else WAX[1])


def seal_strip(broken: bool) -> Callable[[], Image.Image]:
    """Oxblood leather with a twisted hemp cord across it and a wax seal over the cord; broken, the seal is cracked in two
    and the halves have slipped."""
    def draw() -> Image.Image:
        p = Pix(83, 28, seed=51 if not broken else 52)
        p.rect(0, 0, 83, 28, WINE[2])
        p.speckle(0, 0, 83, 28, [WINE[1], WINE[3]], 0.05)
        p.hline(0, 0, 83, WINE[4])
        p.vline(0, 0, 28, WINE[4])
        p.hline(0, 1, 83, WINE[3])
        p.vline(82, 0, 28, WINE[1])
        for x in range(0, 83):                                          # the cord: a shadow, twisted strands, a shadow
            p.px(x, 12, WINE[0])
            for k, y in enumerate((13, 14, 15)):
                twist = (x + k) % 4 < 2
                p.px(x, y, (PARCHMENT[3] if twist else PARCHMENT[1]) if k != 2 else (PARCHMENT[1] if twist else PARCHMENT[0]))
            p.px(x, 16, WINE[0])
            p.px(x, 17, WINE[1])
        for x in (1, 80):                                               # brass eyelets where the cord goes in
            p.ellipse(x - 1, 11, 5, 6, BRASS[2])
            p.ellipse(x, 12, 3, 4, WINE[0])
            p.hline(x - 1, 11, 4, BRASS[4])
        seal = Pix(83, 28)
        seal_body(seal, 41, 12)
        seal.rect(37, 21, 1, 1, WAX[1])
        for dy, x0, ln in ((22, 36, 3), (23, 37, 2), (24, 38, 1)):      # a drip
            seal.hline(x0, dy, ln, WAX[2])
        if not broken:
            p.paste(seal, 0, 0)
        else:
            crack = [12, 11, 12, 13, 12, 11, 12, 13, 12, 12, 11, 12, 13, 12, 12, 13, 12, 11, 12, 13, 12]
            upper, lower = Pix(83, 28), Pix(83, 28)
            for x in range(30, 53):
                cy = crack[x - 30] if 30 <= x < 51 else 12
                for y in range(28):
                    c = seal.get(x, y)
                    if c[3]:
                        (upper if y < cy else lower).px(x, y, c)
            p.paste(lower, 1, 2)
            p.paste(upper, -2, -1)
            for x in range(29, 53):                                        # a dark crack and a chip or two
                cy = crack[min(20, max(0, x - 30))]
                p.px(x - 1, cy + 1, WAX[0])
            p.px(32, 8, WINE[2])
            p.px(49, 18, WINE[2])
            p.px(52, 14, WAX[3])
            p.px(30, 13, WAX[1])
        return p.finish()
    return draw


def seal_tag() -> Image.Image:
    """The small sample of a seal: a wax drip hanging from a parchment tag."""
    p = Pix(9, 12, seed=53)
    wax = Shape(9, 12).rect(0, 0, 8, 7).rect(1, 8, 7, 9).rect(2, 10, 6, 10).rect(3, 11, 5, 11)
    fill(p, wax, WAX[2])
    bevel(p, wax, WAX[4], WAX[0], None)
    p.rect(2, 2, 5, 5, WAX[1])
    p.hline(2, 2, 5, WAX[3])
    p.vline(2, 2, 5, WAX[3])
    p.vline(4, 3, 3, WAX[4])
    p.hline(3, 4, 3, WAX[4])
    p.px(3, 8, WAX[3])
    for x in range(9):
        p.px(x, 0, PARCHMENT[3])
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "cropped-letter-correct.63x16.png": lambda: blackletter("Innkeeper", 63, 16),
    "cropped-letter-incorrect3.56x16.png": lambda: blackletter("Inkeeper", 56, 16),
    "cropped-letter-font.62x10.png": caps_specimen,
    "example_letter1.129x81.png": lambda: charter_lines(("GUILD", "TRADE", "CHARTER"), 129, 81, 3),
    "example_letter2.43x27.png": lambda: charter_lines(("GUILD", "TRADE", "CHARTER"), 43, 27, 1),
    "example_letter3.42x27.png": lambda: charter_lines(("GUILD", "TRDE", "CHATER"), 42, 27, 1),
    "cropped-logo-correct.75x65.png": guild_emblem(True),
    "cropped-logo-simple.71x65.png": guild_emblem(False),
    "example_logo1.55x39.png": plaque(2),
    "logo_checker.55x39.png": plaque(2),
    "example_logo2.55x39.png": plaque(1),
    "guide_davre_logo.29x26.png": tankard_label(True),
    "guide_davre_logo_incorrect.29x27.png": tankard_label(False),
    "guide_ribwich_logo.38x19.png": pie_label(True),
    "guide_ribwich_logo_incorrect.38x19.png": pie_label(False),
    "example_chip1.21x17.png": chip(False),
    "example_chip2.21x17.png": chip(True),
    "cropped-seal-correct.83x28.png": seal_strip(False),
    "cropped-seal-broke.83x28.png": seal_strip(True),
    "example_seal.9x12.png": seal_tag,
}
