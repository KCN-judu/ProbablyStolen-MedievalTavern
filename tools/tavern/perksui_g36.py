"""The 23 glyphs of the perk sheet `2perkSet2` (36 pixel cells), the 100 pixel glyphs and the 256 pixel group.

The sheet cells show places, trades and gear; each is drawn about 18 to 28 pixels across, like the game's own cells."""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image

from perksui_g32 import loaves  # noqa: F401  (kept importable for callers that want the bread)
from perksui_glyphs import CLR, bust, chamfer, box
from perksui_kit import G, W, Ic


def dotted(c: Ic, pts: Sequence[tuple[int, int]], step: int = 2) -> None:
    """A closed outline of single pixels, every `step`th pixel along the way (a drawn-in-chalk frame)."""
    n = len(pts)
    path: list[tuple[int, int]] = []
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        path += [(round(x0 + (x1 - x0) * k / steps), round(y0 + (y1 - y0) * k / steps)) for k in range(steps)]
    for i, (x, y) in enumerate(path):
        if i % step == 0:
            c.px(x, y)


def stamp(dst: Ic, src: Ic, x: int, y: int, scale: int = 1) -> None:
    img = src.content()
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
    dst.p.paste(img, x, y)


# ------------------------------------------------------------------------------------------------ sheet cells


def cottage_person() -> Ic:
    c = Ic(36, 36)
    c.poly([(0, 10), (11, 0), (22, 10)])
    c.rect(16, 2, 3, 5)
    c.cut(3, 11, 16, 1)
    c.rect(3, 12, 16, 9)
    c.cut(8, 13, 6, 8)
    c.disc(10, 14, 3, 3, G)
    c.rect(9, 18, 5, 3, G)
    return c


def banned_leaf() -> Ic:
    c = Ic(36, 36)
    c.ring(0, 0, 26, 26, 3)
    c.poly([(7, 19), (7, 12), (12, 7), (19, 7), (19, 14), (14, 19)])
    c.line(8, 18, 17, 9, G)
    c.bar(4, 4, 22, 22, 6, CLR)
    c.bar(4, 4, 22, 22, 3)
    return c


def thumb_down() -> Ic:
    c = Ic(36, 36)
    box(c, 0, 0, 3, 10)
    c.rect(4, 0, 14, 9)
    chamfer(c, 4, 0, 14, 9)
    c.rect(5, 8, 5, 9)
    c.cut(5, 16, 1, 1)
    c.cut(9, 16, 1, 1)
    for y in (2, 5):
        c.cut(11, y, 7, 1)
    c.cut(10, 8, 1, 1)
    return c


def broken_heart() -> Ic:
    c = Ic(36, 36)
    c.disc(0, 0, 12, 12)
    c.disc(10, 0, 12, 12)
    c.poly([(1, 8), (21, 8), (11, 19)])
    c.bar(11, 1, 8, 6, 2, CLR)
    c.bar(8, 6, 12, 10, 2, CLR)
    c.bar(12, 10, 9, 16, 2, CLR)
    return c


def toolbox() -> Ic:
    c = Ic(36, 36)
    c.bar(5, 10, 3, 3, 2)
    c.rect(0, 1, 6, 3)
    c.bar(11, 10, 17, 2, 2)
    c.disc(15, 0, 6, 4)
    c.bar(18, 10, 24, 4, 2)
    c.rect(23, 1, 3, 3)
    box(c, 1, 11, 24, 11)
    c.rect(1, 15, 24, 1, G)
    c.cut(10, 13, 6, 5)
    c.rect(11, 14, 4, 3)
    return c


def hammer_tongs() -> Ic:
    c = Ic(36, 36)
    c.bar(4, 4, 19, 19, 3)
    c.bar(19, 3, 4, 18, 8, CLR)
    c.bar(19, 3, 4, 18, 3)
    c.poly([(0, 1), (5, 0), (10, 5), (5, 9), (0, 5)])
    c.rect(4, 3, 2, 2, G)
    c.rect(17, 17, 4, 4)
    c.bar(20, 18, 21, 20, 2)
    return c


def three_folk() -> Ic:
    c = Ic(36, 36)
    bust(c, 0, 0)
    bust(c, 18, 0)
    c.rect(11, 8, 8, 13, CLR)
    c.rect(10, 7, 10, 15, CLR)
    bust(c, 9, 7)
    return c


def crutch() -> Ic:
    c = Ic(36, 36)
    c.bar(6, 7, 22, 23, 3)
    c.bar(1, 9, 9, 1, 3)
    c.bar(11, 10, 16, 5, 2)
    c.disc(21, 21, 4, 4)
    c.line(2, 8, 8, 2, G)
    return c


def herb_basket() -> Ic:
    c = Ic(36, 36)
    c.disc(5, 2, 7, 7)
    c.disc(10, 0, 8, 8)
    c.disc(16, 3, 7, 7)
    c.bar(8, 8, 10, 11, 1, CLR)
    c.bar(14, 6, 14, 11, 1, CLR)
    c.bar(19, 8, 18, 11, 1, CLR)
    c.rect(0, 9, 27, 3)
    chamfer(c, 0, 9, 27, 3)
    c.poly([(2, 12), (25, 12), (22, 24), (5, 24)])
    for y in (15, 18, 21):
        c.rect(4, y, 19, 1, G)
    for x in (9, 14, 19):
        c.rect(x, 13, 1, 10, G)
    return c


def midden() -> Ic:
    c = Ic(36, 36)
    c.disc(0, 11, 14, 12)
    c.disc(7, 6, 15, 17)
    c.disc(13, 10, 14, 13)
    c.cut(0, 21, 27, 3)
    c.bar(4, 4, 9, 10, 2)
    c.rect(2, 3, 3, 2)
    c.rect(19, 1, 3, 6)
    c.rect(18, 4, 5, 3)
    for x, y in ((6, 15), (12, 12), (16, 17), (9, 19), (21, 15), (4, 19), (14, 9)):
        c.px(x, y, G)
        c.px(x + 1, y, G)
    c.cut(10, 14, 2, 1)
    c.cut(17, 14, 2, 1)
    return c


def strongbox() -> Ic:
    c = Ic(36, 36)
    c.rect(0, 2, 26, 15)
    chamfer(c, 0, 2, 26, 15)
    c.rect(2, 0, 22, 3)
    c.cut(2, 0, 1, 1)
    c.cut(23, 0, 1, 1)
    c.rect(1, 7, 24, 1, G)
    c.rect(4, 2, 2, 15, G)
    c.rect(20, 2, 2, 15, G)
    c.cut(11, 6, 5, 6)
    c.rect(12, 7, 3, 4)
    c.cut(13, 8, 1, 2)
    return c


def crossbow() -> Ic:
    c = Ic(36, 36)
    c.bar(2, 24, 18, 8, 3)
    c.poly([(0, 25), (3, 22), (5, 26), (2, 27)])
    c.bar(8, 1, 25, 18, 3)
    c.bar(8, 1, 13, 14, 1, G)
    c.bar(25, 18, 13, 14, 1, G)
    c.rect(15, 10, 3, 3)
    return c


def dotted_barrel() -> Ic:
    c = Ic(36, 36)
    dotted(c, [(9, 0), (17, 4), (17, 14), (9, 18), (1, 14), (1, 4)])
    dotted(c, [(1, 4), (9, 8), (17, 4)])
    dotted(c, [(9, 8), (9, 18)])
    return c


def dotted_shield() -> Ic:
    c = Ic(36, 36)
    dotted(c, [(0, 0), (17, 0), (17, 10), (14, 15), (9, 18), (4, 15), (0, 10)])
    return c


def cottage_chimney() -> Ic:
    c = Ic(36, 36)
    c.poly([(0, 10), (10, 1), (20, 10)])
    c.rect(14, 0, 3, 6)
    c.cut(2, 11, 16, 1)
    c.rect(2, 12, 16, 8)
    c.cut(8, 14, 4, 6)
    c.cut(3, 14, 3, 3)
    c.cut(14, 14, 3, 3)
    c.rect(10, 17, 1, 1, G)
    return c


def satchel(up: bool) -> Ic:
    c = Ic(36, 36)
    c.ring(6, 0, 10, 11, 2)
    box(c, 0, 6, 22, 14)
    c.poly([(0, 6), (21, 6), (21, 12), (11, 15), (0, 12)])
    c.line(1, 12, 11, 15, G)
    c.line(20, 12, 11, 15, G)
    c.cut(9, 12, 4, 4)
    c.rect(10, 13, 2, 2)
    c.disc(14, 10, 14, 14, CLR)
    if up:
        c.poly([(20, 11), (26, 17), (23, 17), (23, 22), (17, 22), (17, 17), (14, 17)])
        c.rect(23, 11, 1, 1, CLR)
    else:
        c.poly([(20, 22), (26, 16), (23, 16), (23, 11), (17, 11), (17, 16), (14, 16)])
    return c


def satchel_down() -> Ic:
    return satchel(False)


def satchel_up() -> Ic:
    return satchel(True)


def hat() -> Ic:
    c = Ic(36, 36)
    c.rect(5, 1, 12, 11)
    chamfer(c, 5, 1, 12, 11)
    c.cut(9, 1, 4, 2)
    c.disc(0, 9, 22, 9)
    c.rect(5, 8, 12, 2, G)
    c.bar(16, 8, 21, 3, 1, G)
    return c


def boot(extra: str) -> Ic:
    c = Ic(36, 36)
    c.rect(9, 0, 8, 12)
    c.rect(9, 11, 13, 7)
    c.cut(21, 11, 1, 1)
    c.cut(21, 17, 1, 1)
    c.rect(16, 11, 1, 4, CLR)
    c.rect(9, 17, 13, 2, G)
    c.rect(9, 0, 8, 2, G)
    if extra == "mud":
        c.disc(0, 16, 6, 3)
        c.px(2, 14)
        c.px(4, 13)
    else:
        c.ring(0, 12, 6, 6, 2)
    return c


def boot_mud() -> Ic:
    return boot("mud")


def boot_coin() -> Ic:
    return boot("coin")


def shoes(extra: str) -> Ic:
    c = Ic(36, 36)
    for dx in (0, 8):
        c.bar(8 + dx, 18, 12 + dx, 8, 5)
        c.disc(10 + dx, 3, 7, 7)
        c.bar(9 + dx, 12, 11 + dx, 9, 2, G)
        c.cut(9 + dx, 17, 1, 1)
    c.cut(0, 0, 36, 0)
    if extra == "coin":
        c.ring(0, 17, 6, 6, 2)
        c.px(3, 20, G)
    else:
        c.poly([(0, 21), (4, 16), (9, 21), (4, 23)])
        c.line(1, 21, 7, 20, G)
    return c


def shoes_coin() -> Ic:
    return shoes("coin")


def shoes_leaf() -> Ic:
    return shoes("leaf")


def boot_spur() -> Ic:
    c = Ic(36, 36)
    c.bar(21, 2, 23, 18, 5)
    c.rect(17, 0, 10, 3)
    c.rect(19, 17, 8, 7)
    c.bar(21, 21, 14, 22, 3)
    c.disc(12, 20, 5, 5)
    c.rect(19, 21, 8, 2, G)
    c.bar(3, 23, 9, 17, 3)
    c.rect(1, 22, 4, 4)
    c.rect(3, 22, 1, 3, G)
    return c


# ------------------------------------------------------------------------------------------------ 100 pixel glyphs


def flask() -> Ic:
    c = Ic(33, 33)
    c.rect(9, 0, 8, 2)
    c.rect(10, 2, 6, 8)
    c.disc(0, 8, 26, 22)
    c.cut(10, 0, 1, 1)
    c.rect(11, 1, 4, 1, CLR)
    c.rect(3, 17, 20, 3, G)
    for x, y, d in ((7, 21, 3), (13, 23, 4), (17, 20, 2), (19, 24, 3)):
        c.rect(x, y, d, d, CLR)
        c.px(x, y)
        c.px(x + d - 1, y + d - 1)
    c.rect(5, 12, 1, 4, CLR)
    c.rect(7, 12, 1, 2, CLR)
    c.rect(11, 10, 4, 2, G)
    return c


def banner() -> Ic:
    c = Ic(33, 33)
    c.rect(1, 3, 2, 29)
    c.disc(0, 0, 4, 4)
    c.rect(0, 29, 5, 3)
    c.poly([(3, 4), (27, 4), (22, 11), (27, 18), (3, 18)])
    c.rect(6, 7, 12, 2, G)
    c.rect(6, 13, 9, 2, G)
    c.cut(6, 10, 1, 1)
    return c


def notices() -> Ic:
    c = Ic(33, 33)
    for i, (x, y) in enumerate(((10, 0), (5, 3), (0, 6))):
        c.rect(x - 1, y - 1, 17, 25, CLR)
        c.rect(x, y, 16, 23)
        chamfer(c, x, y, 16, 23)
        if i == 2:
            c.rect(x + 2, y + 2, 12, 4, G)
            for j in range(4):
                c.rect(x + 2, y + 9 + j * 3, 12 - (j == 3) * 5, 1, G)
            c.rect(x + 6, y + 1, 4, 3, CLR)
        else:
            c.rect(x + 11, y + 2, 3, 1, G)
    return c


def hourglass() -> Ic:
    c = Ic(33, 33)
    c.rect(0, 0, 17, 3)
    c.rect(0, 23, 17, 3)
    c.rect(1, 3, 2, 20)
    c.rect(14, 3, 2, 20)
    c.poly([(4, 3), (13, 3), (9, 12), (8, 12)])
    c.poly([(8, 13), (9, 13), (13, 22), (4, 22)])
    c.poly([(5, 4), (12, 4), (9, 10), (8, 10)], CLR)
    c.poly([(8, 15), (9, 15), (12, 21), (5, 21)], CLR)
    c.poly([(6, 8), (11, 8), (9, 10), (8, 10)], G)
    c.poly([(5, 21), (12, 21), (9, 17), (8, 17)], G)
    c.rect(8, 11, 1, 5, G)
    return c


def figure(c: Ic, x: int, y: int, w: int, h: int) -> None:
    """A round head over rounded shoulders, `w` wide and `h` tall, with a gap of one pixel between them."""
    head = w // 2
    c.disc(x + (w - head) // 2, y, head, head)
    top = y + head + 1
    c.disc(x, top, w, 2 * (y + h - top))
    c.cut(x, y + h, w, 40)


def folk_trio() -> Ic:
    """Three figures on a 128 x 88 canvas (doubled into the 256 pixel picture): two behind, one in front."""
    c = Ic(128, 88)
    figure(c, 0, 8, 44, 60)
    figure(c, 84, 8, 44, 60)
    c.rect(35, 22, 58, 66, CLR)
    figure(c, 36, 20, 56, 68)
    return c
