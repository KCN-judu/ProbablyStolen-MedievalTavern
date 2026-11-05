"""Two more full pictures the menus show: `wall` (the taproom's wall by the hearth, with a notice board, a shelf of mugs and
two patrons in silhouette) and `bazaar` (the night market in the lane beside the tavern, with its stalls and strings of
lanterns). Both reuse the sky, house and lamp helpers of menu_scene.py.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping

from PIL import Image

from materials import beam, iron_strap, masonry, planks, plaster, shadow_under, tone
from menu_scene import house, light_window, moon, night, smoke, sky
from palette import BRASS, FLAME, IRON, LEATHER, MOSS, NIGHT, OAK, PALE_WOOD, PARCHMENT, PLASTER, SHADOW, SOOT, STONE, WINE, WOOD
from pix import CLEAR, Color, Pix, mix, rgb

Drawing = Callable[[], Image.Image]


def flame(p: Pix, cx: int, base: int, h: int, w: int) -> None:
    """One tongue of fire, drawn as nested teardrops from red at the outside to a pale core."""
    for k, c in enumerate((FLAME[0], FLAME[1], FLAME[2], FLAME[3], FLAME[4])):
        hh, ww = h - k * h // 6, max(1, w - k * w // 5)
        top = base - hh
        p.poly([(cx - ww, base), (cx - ww // 2, base - hh // 2), (cx, top), (cx + ww // 2, base - hh // 2), (cx + ww, base)], c)


def mug(p: Pix, x: int, y: int, c: Color) -> None:
    """A tankard seen from the side, its foot at (x, y): lit on its left, with a handle on the right."""
    p.rect(x, y - 9, 8, 9, c)
    p.vline(x, y - 9, 9, tone(c, 0.3))
    p.vline(x + 7, y - 9, 9, tone(c, -0.4))
    p.hline(x, y - 9, 8, FLAME[3])
    p.rect(x + 8, y - 7, 3, 1, c)
    p.vline(x + 10, y - 7, 5, c)
    p.rect(x + 8, y - 3, 3, 1, c)
    p.hline(x, y - 1, 8, tone(c, -0.5))


def patron(p: Pix, x: int, y: int, hood: bool, seed: int) -> None:
    """A seated figure in silhouette against the fire: hunched shoulders, a hood or a bare head, a faint rim of firelight
    on the side toward the hearth (the right)."""
    body = rgb("#120b0d")
    p.poly([(x - 16, y), (x - 13, y - 30), (x - 6, y - 38), (x + 6, y - 38), (x + 13, y - 30), (x + 16, y)], body)
    p.ellipse(x - 7, y - 56, 15, 17, body)
    if hood:
        p.poly([(x - 9, y - 40), (x - 7, y - 58), (x, y - 62), (x + 7, y - 58), (x + 9, y - 40)], body)
    p.vline(x + 15, y - 28, 24, FLAME[0])
    p.vline(x + 8, y - 52, 8, FLAME[0])
    p.px(x + 8, y - 54, FLAME[1])


def taproom_wall() -> Image.Image:
    """The wall of the taproom: limewash and stone between oak, a big hearth with a living fire throwing light on the
    room, a shelf of tankards, a board of notices, a hanging lantern, and benches with two drinkers dark against the glow."""
    p = Pix(640, 360, seed=71)
    plaster(p, 0, 0, 640, 262, PLASTER)
    masonry(p, 0, 252, 640, 56, STONE, course=10)
    planks(p, 0, 308, 640, 52, WOOD, plank=13, nails=False)
    beam(p, 0, 0, 640, 24, OAK, vertical=False)
    for x in (0, 300, 616):
        beam(p, x, 0, 24, 312, OAK, vertical=True)
    beam(p, 0, 168, 640, 8, OAK, vertical=False)
    for x0, x1 in ((24, 120), (616, 540)):
        sgn = 1 if x1 > x0 else -1
        p.line(x0, 24, x1, 168, OAK[2])
        for k in range(1, 6):
            p.line(x0 + k * sgn, 24, x1 + k * sgn, 168, OAK[2] if k < 3 else OAK[1])
        p.line(x0, 24, x1, 168, OAK[3])
    shadow_under(p, 24, 24, 592, 8)
    # the hearth: a stone surround, a mantel, a cavity full of fire
    hx, hy, hw, hh = 380, 112, 170, 190
    masonry(p, hx - 20, hy - 14, hw + 40, hh + 14, STONE, course=11)
    beam(p, hx - 28, hy - 22, hw + 56, 14, OAK, vertical=False)
    p.rect(hx, hy + 28, hw, hh - 28, SOOT[0])
    p.poly([(hx, hy + 28), (hx + hw, hy + 28), (hx + hw, hy + 4), (hx + hw // 2, hy - 6), (hx, hy + 4)], SOOT[0])
    p.rect(hx, hy + hh - 14, hw, 14, SOOT[1])
    for k in range(6):
        p.dither(hx, hy + 4 + k, hw, 1, SHADOW, 0.9 - 0.1 * k)
    for x in range(hx + 12, hx + hw - 10, 7):                  # a bed of embers
        p.rect(x, hy + hh - 20, 6, 6, EMBER_TONES[(x // 7) % 3])
    for x, h, w in ((hx + 40, 70, 14), (hx + 70, 100, 18), (hx + 105, 84, 16), (hx + 130, 56, 10), (hx + 56, 44, 8)):
        flame(p, x, hy + hh - 18, h, w)
    for x in (hx + 28, hx + hw - 36):                           # two logs
        p.rect(x - 4, hy + hh - 22, 40, 8, WOOD[1])
        p.hline(x - 4, hy + hh - 22, 40, WOOD[3])
    p.line(hx + hw // 2, hy + 4, hx + hw // 2, hy + 44, IRON[2])    # a pot on a crane
    p.ellipse(hx + hw // 2 - 14, hy + 44, 28, 20, SHADOW)
    p.ellipse(hx + hw // 2 - 13, hy + 45, 26, 17, IRON[1])
    p.hline(hx + hw // 2 - 10, hy + 47, 12, IRON[4])
    # warm light of the fire over everything near
    p.glow(hx + hw // 2, hy + hh - 20, 230, FLAME[0], 0.55)
    p.glow(hx + hw // 2, hy + hh - 20, 120, FLAME[1], 0.4)
    # left: notice board
    bx, by = 60, 62
    planks(p, bx, by, 150, 112, WOOD, plank=11, nails=False)
    for x0, y0, w0, h0 in ((bx - 4, by - 4, 158, 5), (bx - 4, by + 111, 158, 5), (bx - 4, by - 4, 5, 120), (bx + 149, by - 4, 5, 120)):
        beam(p, x0, y0, w0, h0, OAK)
    rng = random.Random(5)
    for i, (px, py, pw, ph) in enumerate(((8, 8, 38, 46), (54, 14, 40, 34), (100, 8, 36, 54), (14, 64, 46, 38), (70, 62, 54, 40))):
        paper = Pix(pw, ph, seed=i)
        paper.rect(0, 0, pw, ph, PARCHMENT[3])
        paper.hline(0, 0, pw, PARCHMENT[4])
        paper.vline(0, 0, ph, PARCHMENT[4])
        paper.hline(0, ph - 1, pw, PARCHMENT[1])
        for ly in range(5, ph - 4, 4):                          # lines of writing
            paper.hline(3, ly, pw - 6 - rng.randrange(0, 12), PARCHMENT[1] if ly % 8 else SHADOW)
        p.rect(bx + px + 2, by + py + 2, pw, ph, SHADOW)
        p.paste(paper, bx + px, by + py)
        p.rect(bx + px + pw // 2 - 1, by + py + 1, 3, 3, EMBER)
        p.px(bx + px + pw // 2, by + py + 1, FLAME[3])
    # shelf with tankards and jugs
    p.rect(224, 140, 120, 6, OAK[2])
    p.hline(224, 140, 120, OAK[4])
    p.hline(224, 146, 120, SHADOW)
    for i, x in enumerate(range(230, 336, 14)):
        mug(p, x, 140, (PALE_WOOD[2], BRASS[2], IRON[3], BRASS[3])[i % 4])
    p.rect(222, 148, 5, 8, IRON[1])                              # brackets
    p.rect(338, 148, 5, 8, IRON[1])
    # hanging lantern
    lx = 262
    p.vline(lx, 24, 38, IRON[2])
    p.rect(lx - 7, 62, 15, 5, IRON[1])
    p.rect(lx - 5, 67, 11, 17, FLAME[3])
    p.rect(lx - 2, 70, 5, 10, FLAME[4])
    p.vline(lx - 5, 67, 17, IRON[1])
    p.vline(lx + 5, 67, 17, IRON[1])
    p.rect(lx - 6, 84, 13, 3, IRON[1])
    p.glow(lx, 75, 50, FLAME[1], 0.7)
    # benches and the drinkers
    p.rect(300, 300, 100, 6, OAK[3])
    p.hline(300, 300, 100, OAK[4])
    p.rect(305, 306, 5, 22, OAK[1])
    p.rect(390, 306, 5, 22, OAK[1])
    patron(p, 336, 300, True, 1)
    patron(p, 372, 300, False, 2)
    for x in (338, 374):
        mug(p, x + 12, 296, BRASS[2])
    # barrel at the far left
    p.ellipse(8, 250, 56, 64, WOOD[2])
    for y in (262, 294):
        p.hline(10, y, 52, IRON[2])
    p.ellipse(8, 250, 56, 12, WOOD[3])
    p.dither(8, 262, 56, 52, SHADOW, 0.35)
    # the room is dark at the edges
    for k in range(5):
        p.dither(k * 4, 0, 4, 360, SHADOW, 0.5 - 0.1 * k)
        p.dither(640 - (k + 1) * 4, 0, 4, 360, SHADOW, 0.5 - 0.1 * k)
    p.dither(0, 336, 640, 24, SHADOW, 0.35)
    return p.finish()


EMBER_TONES = (FLAME[1], FLAME[0], rgb("#a03018"))
EMBER = rgb("#b2402a")


# ---------------------------------------------------------------------------------------------- bazaar


def lantern(p: Pix, x: int, y: int, c: Color = FLAME[3]) -> None:
    """A paper-and-iron lantern hanging by its cord, with its halo."""
    p.vline(x, y - 4, 4, IRON[1])
    p.rect(x - 3, y, 7, 2, IRON[1])
    p.rect(x - 3, y + 2, 7, 8, c)
    p.rect(x - 1, y + 4, 3, 4, FLAME[4])
    p.rect(x - 3, y + 10, 7, 2, IRON[1])
    p.glow(x, y + 6, 15, FLAME[0], 0.6)


def stall(p: Pix, x: int, y: int, w: int, awning: tuple[Color, Color], goods: int, seed: int) -> None:
    """A market stall: two posts, a striped awning with a scalloped edge, a counter with wares on it. (x, y) is the left
    foot of the counter's front."""
    rng = random.Random(seed)
    top = y - 100
    for px in (x + 2, x + w - 8):
        beam(p, px, top, 6, 100, OAK, vertical=True)
    p.rect(x, top + 24, w, 30, SHADOW)
    p.rect(x + 4, top + 24, w - 8, 30, mix(SHADOW, OAK[0], 0.4))
    for sx in range(x - 6, x + w + 6, 12):                      # the awning, in stripes, tipped forward
        p.poly([(sx + 1, top + 4), (sx + 11, top + 4), (sx + 14, top + 22), (sx - 2, top + 22)], awning[0] if (sx - x) // 12 % 2 else awning[1])
        p.line(sx + 1, top + 4, sx - 2, top + 22, tone(awning[1], 0.15))
        p.ellipse(sx - 2, top + 20, 16, 7, awning[0] if (sx - x) // 12 % 2 else awning[1])
    p.hline(x - 6, top + 3, w + 12, SHADOW)
    p.hline(x - 6, top + 4, w + 12, tone(awning[1], 0.2))
    p.dither(x - 6, top + 22, w + 12, 7, SHADOW, 0.3)
    # counter
    planks(p, x, y - 34, w, 34, WOOD, plank=11, nails=False)
    p.rect(x - 3, y - 38, w + 6, 6, PALE_WOOD[2])
    p.hline(x - 3, y - 38, w + 6, PALE_WOOD[4])
    p.hline(x - 3, y - 33, w + 6, SHADOW)
    shadow_under(p, x, y - 32, w, 5)
    for i in range(goods):                                      # wares on the counter: fruit, loaves, jars, rolled cloth
        gx = x + 6 + i * (w - 12) // goods
        kind = (i + seed) % 4
        if kind == 0:
            for k in range(5):
                p.ellipse(gx + k * 3 - 6, y - 46 + (k % 2) * 3, 8, 8, rng.choice((WINE[3], FLAME[2], MOSS[3])))
        elif kind == 1:
            p.ellipse(gx, y - 46, 16, 9, PALE_WOOD[3])
            p.hline(gx + 3, y - 44, 9, PALE_WOOD[4])
        elif kind == 2:
            p.rect(gx, y - 52, 9, 14, rgb("#4a6e98"))
            p.rect(gx + 2, y - 55, 5, 3, WOOD[2])
            p.vline(gx + 1, y - 52, 14, rgb("#8ab0b8"))
        else:
            p.rect(gx, y - 46, 18, 8, rng.choice((WINE[2], MOSS[2], rgb("#2f4c70"))))
            p.ellipse(gx - 2, y - 46, 5, 8, tone(WINE[2], 0.2))
    lantern(p, x + w // 2, top + 34)


def bazaar() -> Image.Image:
    """The market lane at night: a row of timber houses with lit windows behind, strings of lanterns across the lane,
    three stalls with striped awnings and their wares, crates and a cart, all on cobbles that hold the lamplight."""
    rng = random.Random(81)
    W, H = 960, 540
    p = Pix(W, H, seed=81)
    sky_layer = Pix(640, 215)
    sky(sky_layer, rng)
    p.rect(0, 280, W, 80, mix(NIGHT[1], SHADOW, 0.4))
    p.paste(sky_layer.im.resize((960, 322), Image.Resampling.NEAREST), 0, -30)
    moon(p, 830, 80, 30)
    blue = mix(NIGHT[2], rgb("#4a3a58"), 0.3)
    base = 330
    for i, (x, w, wall, roof, seed) in enumerate(((10, 150, 120, 56, 7), (176, 120, 140, 50, 2), (312, 160, 110, 54, 6), (490, 130, 130, 50, 3), (640, 150, 120, 56, 9), (806, 170, 140, 52, 8))):
        hp, wins, door = house(w, wall, roof, seed)
        by = base - hp.h
        p.paste(night(hp.im, blue, 0.5), x - 8, by)
        q = Pix(W, H)
        for wx, wy, ww, wh in wins:
            if (wx + i) % 4:
                light_window(q, x - 8 + wx, by + wy, ww, wh, 0.8)
        p.paste(q, 0, 0)
        if door is not None:
            dx, dy, dw, dh = door
            p.rect(x - 8 + dx, by + dy, dw, dh, FLAME[1])
            p.glow(x - 8 + dx + dw // 2, by + dy + dh, 30, FLAME[2], 0.8)
        smoke(p, x + 20, by + 3, random.Random(i), 50)
    # ground
    p.rect(0, base, W, H - base, STONE[0])
    y, rh = base, 5
    r2 = random.Random(3)
    while y < H:
        x = -r2.randrange(0, 16)
        while x < W:
            sw = r2.randrange(rh * 2, rh * 4)
            c = r2.choice((STONE[1], STONE[1], STONE[2], mix(STONE[1], WINE[0], 0.4)))
            p.rect(x + 1, y, sw - 1, rh - 1, c)
            p.hline(x + 1, y, sw - 1, tone(c, 0.2))
            x += sw
        y += rh
        rh = min(rh + 1, 14) if (y // 24) % 2 else rh
    for cx in (140, 480, 800):
        p.glow(cx, 400, 120, mix(FLAME[0], STONE[2], 0.4), 0.5)
    # lantern strings
    for (xa, ya, xb, yb) in ((0, 150, 960, 170), (0, 210, 960, 196)):
        pts = []
        for x in range(xa, xb + 1, 4):
            t = (x - xa) / (xb - xa)
            sag = 28 * (1 - (2 * ((x - xa) / 240 % 1) - 1) ** 2)
            pts.append((x, round(ya + (yb - ya) * t + sag)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            p.line(x0, y0, x1, y1, IRON[1])
        for k in range(0, len(pts), 12):
            lantern(p, pts[k][0], pts[k][1], FLAME[3] if k % 24 else rgb("#c25b49"))
    stall(p, 40, 470, 220, (WINE[3], PARCHMENT[3]), 4, 1)
    stall(p, 370, 440, 200, (MOSS[3], PARCHMENT[3]), 4, 2)
    stall(p, 690, 480, 230, (rgb("#2f4c70"), PARCHMENT[3]), 5, 3)
    for cx, cy in ((300, 492), (620, 500), (950, 520)):         # crates and a barrel in front
        planks(p, cx - 24, cy - 28, 48, 28, WOOD, plank=9, nails=False)
        beam(p, cx - 26, cy - 30, 52, 4, OAK, vertical=False)
        beam(p, cx - 26, cy - 4, 52, 4, OAK, vertical=False)
    for k in range(5):
        p.dither(0, 536 - k * 4, W, 4, SHADOW, 0.1 + 0.08 * k)
    return p.finish()


ASSETS: Mapping[str, Drawing] = {
}
