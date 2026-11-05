"""The 32 and 36 pixel perk glyphs (the perk slots of the new-game screen). Drawn at the size of the game's own icons, so
every one is about 16 to 24 pixels across and has to read at 1x: few shapes, two pixel strokes, one grey for detail."""

from __future__ import annotations

import math

from perksui_glyphs import CLR, bust, chamfer, box
from perksui_kit import G, Ic


def mortar() -> Ic:
    c = Ic(32, 32)
    c.disc(2, 4, 19, 17)
    c.cut(0, 0, 32, 10)
    c.rect(1, 9, 21, 3)
    c.cut(1, 9, 1, 1)
    c.cut(21, 9, 1, 1)
    c.rect(7, 21, 9, 2)
    c.rect(4, 14, 1, 3, G)
    c.rect(6, 13, 14, 1, G)
    c.bar(13, 8, 19, 2, 3)
    c.disc(17, 0, 5, 5)
    return c


def tankard() -> Ic:
    c = Ic(32, 32)
    c.ring(10, 9, 8, 10, 2)
    c.rect(1, 7, 12, 14)
    chamfer(c, 1, 7, 12, 14)
    for x, y in ((0, 3), (4, 1), (8, 3)):
        c.disc(x, y, 6, 6)
    c.rect(1, 6, 12, 3)
    c.rect(2, 12, 10, 1, G)
    c.rect(2, 17, 10, 1, G)
    c.rect(3, 9, 1, 2, G)
    return c


def die() -> Ic:
    c = Ic(32, 32)
    box(c, 0, 0, 17, 17)
    for x, y in ((2, 2), (12, 2), (7, 7), (2, 12), (12, 12)):
        c.cut(x, y, 3, 3)
    c.rect(15, 3, 1, 12, G)
    c.rect(3, 15, 12, 1, G)
    return c


def pipe() -> Ic:
    c = Ic(32, 32)
    c.art(10, 4, ["########", "#oooooo#", ".######.", ".######.", "..####..", "..####.."])
    c.rect(10, 10, 6, 4)
    c.rect(0, 12, 12, 3)
    c.rect(0, 11, 3, 5)
    c.cut(0, 11, 1, 1)
    c.cut(0, 15, 1, 1)
    c.rect(4, 12, 1, 1, G)
    c.art(12, 0, [".#.", "#..", ".#."])
    c.art(15, 0, ["..#", ".#."])
    return c


def bell() -> Ic:
    c = Ic(32, 32)
    rows = ["........##", ".......###", "......####", "......####", ".....#####", ".....#####", ".....#####",
            "....######", "....######", "....######", "...#######", "...#######", "..########", "..########",
            ".#########", ".#########", "##########", "##########", "..........", ".......###", ".......###"]
    c.art(0, 0, rows, mirror=True)
    c.rect(1, 15, 17, 1, G)
    c.rect(5, 7, 1, 5, G)
    return c


def torn_deed() -> Ic:
    c = Ic(32, 32)
    box(c, 0, 0, 16, 18)
    c.cut(11, 0, 5, 5)
    c.poly([(11, 0), (11, 4), (15, 4)], G)
    for y, w in ((6, 10), (9, 10), (12, 5)):
        c.rect(3, y, w, 1, G)
    c.poly([(0, 15), (3, 13), (6, 16), (9, 13), (12, 16), (15, 13), (16, 16), (16, 19), (0, 19)], CLR)
    return c


def horn() -> Ic:
    c = Ic(32, 32)
    c.poly([(8, 4), (17, 0), (17, 13), (8, 9)])
    c.rect(17, 0, 3, 14)
    c.cut(17, 0, 1, 1)
    c.cut(19, 13, 1, 1)
    c.rect(2, 5, 7, 3)
    c.rect(0, 4, 3, 5)
    c.rect(5, 3, 2, 7)
    c.rect(14, 3, 1, 8, G)
    c.rect(11, 5, 1, 4, G)
    return c


def seal_letter() -> Ic:
    c = Ic(32, 32)
    box(c, 0, 0, 20, 15)
    c.line(2, 1, 9, 8, G)
    c.line(17, 1, 10, 8, G)
    c.disc(5, 5, 11, 11, CLR)
    c.disc(6, 6, 9, 9)
    c.cut(10, 8, 1, 4)
    c.cut(9, 9, 3, 2)
    return c


def lute() -> Ic:
    c = Ic(32, 32)
    c.bar(9, 12, 18, 4, 3)
    c.rect(17, 0, 5, 5)
    c.cut(17, 0, 1, 1)
    c.disc(0, 8, 14, 13)
    c.disc(4, 12, 5, 5, CLR)
    c.ring(4, 12, 5, 5, 1, G)
    c.line(8, 16, 19, 4, G)
    c.rect(2, 16, 1, 3, G)
    return c


def palette() -> Ic:
    c = Ic(32, 32)
    c.disc(0, 2, 19, 17)
    c.disc(3, 13, 5, 4, CLR)
    for x, y in ((4, 5), (9, 3), (14, 5), (13, 10)):
        c.cut(x, y, 3, 3)
    c.bar(12, 20, 20, 9, 5, CLR)
    c.bar(13, 19, 19, 10, 2)
    c.rect(18, 7, 3, 3, G)
    return c


def three_nodes() -> Ic:
    c = Ic(32, 32)
    pts = ((11, 5), (5, 17), (18, 17))
    for a in range(3):
        for b in range(a + 1, 3):
            c.bar(*pts[a], *pts[b], 2)
    for x, y in pts:
        c.disc(x - 5, y - 5, 11, 11, CLR)
    for x, y in pts:
        c.ring(x - 4, y - 4, 9, 9, 3)
        c.rect(x, y, 1, 1, G)
    return c


def jail() -> Ic:
    c = Ic(32, 32)
    box(c, 0, 0, 20, 22)
    c.cut(3, 3, 14, 16)
    for x in (5, 9, 13):
        c.rect(x, 3, 2, 16)
    c.rect(3, 10, 14, 2, G)
    return c


def scroll_seal() -> Ic:
    c = Ic(32, 32)
    c.rect(6, 2, 14, 14)
    for x in (0, 20):
        box(c, x, 0, 6, 18)
        c.rect(x + 2, 2, 1, 14, G)
    c.cut(6, 0, 1, 18)
    c.cut(19, 0, 1, 18)
    c.rect(8, 4, 10, 1, G)
    c.rect(8, 6, 6, 1, G)
    c.bar(11, 12, 9, 17, 2)
    c.bar(14, 12, 16, 17, 2)
    c.disc(9, 8, 8, 8, CLR)
    c.disc(10, 9, 6, 6)
    c.rect(12, 11, 2, 2, G)
    return c


def closed_book_q() -> Ic:
    c = Ic(32, 32)
    box(c, 0, 0, 16, 22)
    c.cut(3, 1, 1, 17)
    c.rect(1, 3, 2, 1, G)
    c.rect(1, 14, 2, 1, G)
    c.rect(2, 19, 13, 2, G)
    c.art(7, 5, [".xxxx.", "xx..xx", "....xx", "...xx.", "..xx..", "..xx..", "......", "..xx.."])
    return c


def great_helm() -> Ic:
    c = Ic(32, 32)
    rows = ["...######", ".########", "#########", "#########", "#########", "#########", "#########", "#########",
            "#########", "#########", "#########", ".########", ".########", "..#######", "..#######", "...######"]
    c.art(0, 0, rows, mirror=True)
    c.cut(2, 5, 13, 2)
    c.cut(8, 7, 1, 7)
    for y in (9, 11, 13):
        c.px(5, y, CLR)
        c.px(11, y, CLR)
    c.px(3, 4, G)
    c.px(13, 4, G)
    c.rect(2, 15, 13, 1, G)
    return c


def empty_crate() -> Ic:
    c = Ic(32, 32)
    c.poly([(9, 0), (17, 4), (17, 13), (9, 17), (1, 13), (1, 4)])
    c.poly([(9, 3), (14, 6), (14, 11), (9, 14), (4, 11), (4, 6)], CLR)
    c.line(9, 9, 3, 6)
    c.line(9, 9, 15, 6)
    c.line(9, 9, 9, 15)
    return c


def rosette() -> Ic:
    c = Ic(32, 32)
    c.poly([(2, 12), (7, 13), (7, 21), (4, 18), (1, 21)])
    c.poly([(14, 12), (9, 13), (9, 21), (12, 18), (15, 21)])
    c.disc(0, -1, 16, 16, CLR)
    for k in range(8):
        a = k * math.pi / 4
        c.disc(round(8 + 6 * math.cos(a)) - 2, round(7 + 6 * math.sin(a)) - 2, 5, 5)
    c.disc(2, 1, 12, 12)
    c.disc(3, 2, 10, 10, CLR)
    c.disc(4, 3, 8, 8)
    c.art(5, 4, ["..x..", "xxxxx", ".xxx.", ".x.x.", "x...x"])
    return c


def key() -> Ic:
    c = Ic(32, 32)
    c.ring(0, 0, 10, 10, 3)
    c.rect(4, 4, 2, 2, G)
    c.rect(9, 3, 17, 3)
    c.rect(12, 1, 2, 7)
    c.rect(19, 6, 3, 4)
    c.rect(23, 6, 3, 3)
    c.rect(15, 4, 3, 1, G)
    return c


def pitchfork() -> Ic:
    c = Ic(32, 32)
    for x, h in ((0, 9), (6, 11), (12, 9)):
        c.rect(x, 12 - h, 3, h)
        c.cut(x, 12 - h, 1, 1)
        c.cut(x + 2, 12 - h, 1, 1)
    c.rect(0, 9, 15, 3)
    c.rect(5, 12, 5, 3)
    c.rect(6, 15, 3, 7)
    c.rect(5, 13, 5, 1, G)
    return c


def purse() -> Ic:
    c = Ic(32, 32)
    c.disc(7, 0, 7, 7)
    c.rect(10, 2, 1, 3, G)
    c.poly([(3, 8), (17, 8), (15, 12), (5, 12)])
    c.disc(0, 10, 21, 12)
    c.rect(5, 11, 11, 2, G)
    c.rect(6, 15, 1, 3, G)
    return c


def bucket_broom() -> Ic:
    c = Ic(32, 32)
    c.ring(1, 0, 11, 14, 2)
    c.poly([(0, 11), (12, 11), (11, 23), (1, 23)])
    c.rect(0, 9, 13, 3)
    c.rect(2, 15, 9, 1, G)
    c.rect(3, 19, 7, 1, G)
    c.rect(17, 0, 2, 15)
    c.poly([(15, 15), (20, 15), (22, 23), (14, 23)])
    c.rect(14, 17, 8, 1, G)
    c.cut(13, 14, 1, 10)
    return c


def sack() -> Ic:
    c = Ic(32, 32)
    c.poly([(3, 0), (7, 5), (4, 6)])
    c.poly([(12, 0), (8, 5), (11, 6)])
    c.rect(5, 4, 6, 4)
    c.disc(0, 7, 16, 13)
    c.rect(4, 7, 8, 2, G)
    c.rect(9, 12, 3, 3, G)
    return c


def heart_door() -> Ic:
    c = Ic(32, 32)
    c.rect(0, 6, 15, 16)
    c.disc(0, 0, 15, 15)
    c.rect(5, 14, 1, 8, G)
    c.rect(9, 14, 1, 8, G)
    c.art(4, 4, [".xx.xx.", "xxxxxxx", "xxxxxxx", ".xxxxx.", "..xxx..", "...x..."])
    c.cut(11, 15, 2, 2)
    return c


def skull() -> Ic:
    c = Ic(32, 32)
    rows = ["...#####", ".#######", "########", "########", "########", "########", "########", "########",
            ".#######", "..######", "..######", "..######", "..######", "...#####"]
    c.art(0, 0, rows, mirror=True)
    c.cut(2, 5, 4, 4)
    c.cut(9, 5, 4, 4)
    c.cut(7, 9, 1, 2)
    c.rect(3, 10, 9, 1, G)
    for x in (5, 7, 9):
        c.cut(x, 12, 1, 2)
    return c


def moon_z() -> Ic:
    c = Ic(32, 32)
    c.disc(0, 0, 18, 22)
    c.disc(6, -2, 18, 22, CLR)
    c.art(13, 2, ["#####", "...#.", "..#..", ".#...", "#####"])
    c.art(17, 11, ["####", "..#.", ".#..", "####"])
    c.px(10, 2, G)
    c.px(9, 3, G)
    return c


def signpost() -> Ic:
    c = Ic(32, 32)
    c.rect(6, 2, 3, 20)
    c.disc(5, 0, 5, 3)
    c.rect(2, 20, 11, 2)
    c.poly([(0, 4), (10, 4), (14, 7), (10, 10), (0, 10)])
    c.poly([(15, 12), (5, 12), (1, 15), (5, 18), (15, 18)])
    c.rect(2, 7, 7, 1, G)
    c.rect(7, 15, 7, 1, G)
    return c


def stall() -> Ic:
    c = Ic(32, 32)
    c.rect(1, 5, 2, 13)
    c.rect(11, 5, 2, 13)
    c.rect(0, 11, 14, 3)
    c.rect(3, 8, 3, 3)
    c.rect(4, 7, 1, 1)
    c.rect(7, 6, 4, 5)
    c.rect(8, 8, 2, 1, G)
    c.rect(0, 0, 14, 4)
    for i, x in enumerate(range(0, 14, 2)):
        col = (255, 255, 255, 255) if i % 2 == 0 else G
        c.rect(x, 0, 2, 4, col)
        c.rect(x, 4, 2, 2, col)
    c.cut(0, 5, 1, 1)
    c.cut(13, 5, 1, 1)
    c.rect(1, 15, 12, 3)
    chamfer(c, 1, 15, 12, 3)
    return c


def loaves() -> Ic:
    c = Ic(32, 32)
    c.disc(0, 8, 10, 9)
    c.bar(3, 10, 4, 13, 1, CLR)
    c.bar(6, 10, 7, 13, 1, CLR)
    c.disc(10, 3, 13, 14)
    for x in (13, 16, 19):
        c.bar(x, 6, x + 2, 12, 1, CLR)
    c.rect(2, 16, 19, 1, G)
    return c


def well() -> Ic:
    c = Ic(32, 32)
    c.poly([(0, 6), (13, 0), (26, 6)])
    c.rect(13, 1, 1, 3, G)
    c.rect(4, 8, 2, 8)
    c.rect(20, 8, 2, 8)
    c.rect(13, 7, 1, 4, G)
    c.rect(11, 11, 5, 4)
    box(c, 3, 14, 20, 8)
    for y in (17, 20):
        c.rect(4, y, 18, 1, G)
    c.rect(11, 11, 5, 3, G)
    c.rect(12, 12, 3, 2)
    return c


def lucky_shoe() -> Ic:
    c = Ic(36, 36)
    c.ring(0, 0, 20, 22, 6)
    c.cut(0, 0, 20, 10)
    c.rect(0, 2, 6, 10)
    c.rect(14, 2, 6, 10)
    c.cut(0, 2, 1, 1)
    c.cut(19, 2, 1, 1)
    c.cut(5, 5, 1, 0)
    for y in (4, 7, 10):
        c.cut(2, y, 2, 2)
        c.cut(16, y, 2, 2)
    c.rect(8, 15, 1, 3, G)
    c.rect(11, 16, 1, 3, G)
    return c


def whisper() -> Ic:
    c = Ic(36, 36)
    c.ring(2, 0, 15, 9, 2)
    c.poly([(8, 8), (12, 8), (9, 12)])
    bust(c, 0, 12, True)
    c.cut(12, 12, 1, 14)
    bust(c, 13, 12, True)
    c.px(7, 4, G)
    c.px(9, 4, G)
    c.px(11, 4, G)
    return c
