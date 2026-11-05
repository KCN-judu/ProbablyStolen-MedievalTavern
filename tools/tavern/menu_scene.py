"""The main-menu picture: a night street in a medieval town, the tavern with its lit windows, a moon over the roofs and
a hanging sign that carries the title.

`street(lettered)` draws the 640x320 picture; the lettered and the plain version are the same scene except for the
words on the sign. The houses are drawn in daylight tones, then pushed toward night blue, and only then are their
windows lit, so every lamp is the brightest thing near it.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from typing import Final

from PIL import Image

import font
from materials import beam, iron_strap, masonry, planks, plaster, tone
from palette import BRASS, FLAME, GLASS, IRON, LEATHER, NIGHT, OAK, PALE_WOOD, PLASTER, SHADOW, SOOT, STONE, WINE, WOOD
from pix import BAYER, Color, Pix, mix, rgb

W, H = 640, 320
GROUND: Final = 268                     # the line where the houses stand on the street
WINDOW_LIGHT: Final[Sequence[Color]] = (FLAME[1], FLAME[2], FLAME[3], FLAME[4])
Window = tuple[int, int, int, int]      # x, y, w, h in the picture the house was drawn on


def night(im: Image.Image, color: Color, amount: float) -> Image.Image:
    """The picture pushed toward a colour (the blue of night) with its transparency kept."""
    solid = Image.new("RGB", im.size, color[:3])
    out = Image.blend(im.convert("RGB"), solid, amount).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


# ---------------------------------------------------------------------------------------------- sky


def sky(p: Pix, rng: random.Random) -> None:
    """Night sky: bands of deepening blue toward the horizon, a haze of town light low down, stars, a few thin clouds."""
    bands = (NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[3], mix(NIGHT[3], rgb("#6a4a5a"), 0.45), mix(NIGHT[3], rgb("#9a6a58"), 0.55))
    top, bottom = 0, 215
    for i, c in enumerate(bands):
        y0, y1 = top + (bottom - top) * i // len(bands), top + (bottom - top) * (i + 1) // len(bands)
        p.rect(0, y0, W, y1 - y0, c)
        if i:
            for k in range(4):
                p.dither(0, y0 - 4 + k, W, 1, bands[i - 1], 0.8 - k * 0.2)
    for _ in range(190):                                       # stars: more of them high up
        x, y = rng.randrange(W), int(rng.random() ** 1.7 * 170)
        c = rng.choice((NIGHT[4], rgb("#9aa6d0"), rgb("#d8d4c0"), rgb("#d8d4c0")))
        p.px(x, y, c)
        if rng.random() < 0.07:                                # a bright one with a little cross
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(x + dx, y + dy, mix(c, NIGHT[3], 0.5))
    for _ in range(5):                                         # clouds: streaks of lighter blue with a ragged underside
        cx, cy, cw = rng.randrange(40, 600), rng.randrange(20, 130), rng.randrange(60, 150)
        for row in range(5):
            span = cw - row * 14 + rng.randrange(-6, 6)
            if span > 6:
                p.dither(cx - span // 2 + row * 3, cy + row * 2, span, 2, NIGHT[3], 0.55 - row * 0.08)


def moon(p: Pix, cx: int, cy: int, r: int) -> None:
    """A full moon: a wide halo, a pale disc lit from the upper left, shaded toward the lower right, with maria."""
    for k, (rad, dens) in enumerate(((r * 3, 0.16), (r * 2, 0.22), (r * 3 // 2, 0.3))):
        p.glow(cx, cy, rad, mix(NIGHT[4], rgb("#c8c4d8"), 0.35 + k * 0.1), dens * 3)
    disc = Pix(2 * r + 2, 2 * r + 2)
    disc.ellipse(0, 0, 2 * r + 1, 2 * r + 1, rgb("#d8d4c4"))
    disc.dither(0, 0, 2 * r + 2, 2 * r + 2, rgb("#a8a6b4"), 0.0)
    for yy in range(2 * r + 2):                                # shade the far (lower right) limb
        for xx in range(2 * r + 2):
            d = ((xx - r * 0.7) ** 2 + (yy - r * 0.7) ** 2) ** 0.5 / (2 * r)
            if disc.get(xx, yy)[3] and d > 0.55:
                if BAYER[yy % 4][xx % 4] < (d - 0.55) * 36:
                    disc.px(xx, yy, rgb("#9c9aac"))
    for mx, my, mw, mh in ((0.30, 0.30, 0.34, 0.26), (0.58, 0.52, 0.26, 0.2), (0.38, 0.66, 0.2, 0.16)):
        disc.ellipse(round(mx * 2 * r), round(my * 2 * r), round(mw * 2 * r), round(mh * 2 * r), rgb("#aeabb8"))
    for mx, my in ((0.2, 0.5), (0.68, 0.28), (0.5, 0.82)):     # craters: a dark rim on the lit side
        x0, y0 = round(mx * 2 * r), round(my * 2 * r)
        disc.ellipse(x0, y0, 5, 4, rgb("#9c9aac"))
        disc.px(x0 + 1, y0 + 1, rgb("#e6e2d2"))
    keep = Pix(2 * r + 2, 2 * r + 2)
    keep.ellipse(0, 0, 2 * r + 1, 2 * r + 1, (255, 255, 255))
    for yy in range(2 * r + 2):
        for xx in range(2 * r + 2):
            if not keep.get(xx, yy)[3]:
                disc.px(xx, yy, (0, 0, 0, 0))
    p.paste(disc, cx - r, cy - r)


def skyline(p: Pix, rng: random.Random) -> None:
    """The far edge of the town: hills, a castle on the left with a lit window or two, steeples, in two hazy planes."""
    far, near = mix(NIGHT[2], rgb("#5a4a62"), 0.45), mix(NIGHT[1], rgb("#3a2a40"), 0.6)
    for x in range(W):                                         # rolling hills behind everything
        y = 188 + round(9 * (0.5 + 0.5 * math.sin(x / 61 + 1))) + round(4 * math.sin(x / 17))
        p.rect(x, y, 1, 90, far)
    for x0, w, h in ((486, 26, 70), (516, 14, 52)):             # a keep in the gap on the right
        p.rect(x0, 215 - h, w, h + 60, near)
        for k in range(0, w, 6):
            p.rect(x0 + k, 215 - h - 4, 4, 4, near)
        p.rect(x0 + w // 2, 215 - h + 12, 2, 4, FLAME[1])
    for sx, sh in ((386, 100), (92, 70)):                      # steeples of a church and its tower in the distance
        p.rect(sx, 215 - sh, 14, sh + 60, near)
        p.poly([(sx - 2, 215 - sh), (sx + 15, 215 - sh), (sx + 6, 215 - sh - 30)], near)
        p.rect(sx + 5, 215 - sh + 8, 3, 6, FLAME[1])
    p.rect(0, 232, W, 60, near)
    for x in range(0, W, 3):                                   # a low mist at the foot of the hills
        p.dither(x, 218, 3, 20, mix(NIGHT[3], rgb("#8a7a8a"), 0.4), 0.14)


# ---------------------------------------------------------------------------------------------- houses


def tiles(p: Pix, x: int, y: int, w: int, h: int, base: Color) -> None:
    """Roof tiles in rows, each row shifted half a tile, lit on the upper edge of every tile."""
    rng = p.rng
    for row in range(h // 4 + 1):
        shift = 5 if row % 2 else 0
        for tx in range(x - 10 + shift, x + w + 10, 10):
            c = mix(base, SHADOW, rng.choice((0.0, 0.0, 0.15, 0.3)))
            yy = y + row * 4
            p.rect(tx, yy, 9, 4, c)
            p.hline(tx, yy, 9, tone(c, 0.25))
            p.vline(tx + 9, yy, 4, SHADOW)
            p.hline(tx, yy + 3, 9, tone(c, -0.35))


def window_frame(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """The dark opening of a window with a timber frame, a sill, and a leaded cross; the light goes in later."""
    p.rect(x - 2, y - 2, w + 4, h + 4, OAK[1])
    p.rect(x, y, w, h, SHADOW)
    p.hline(x - 3, y + h + 2, w + 6, OAK[3])
    p.hline(x - 3, y + h + 3, w + 6, OAK[0])


def light_window(p: Pix, x: int, y: int, w: int, h: int, glow: float = 1.0) -> None:
    """A lit window: warm panes darker toward the edge and the bottom, a leaded cross, and a halo on the wall around."""
    p.glow(x + w // 2, y + h // 2, max(w, h) // 2 + 9, FLAME[1], 0.32 * glow)
    for yy in range(h):
        for xx in range(w):
            d = max(abs(xx - (w - 1) / 2) / (w / 2), abs(yy - (h - 1) / 2) / (h / 2))
            k = 3 if d < 0.45 else 2 if d < 0.8 else 1
            if yy > h * 0.65 and k > 2:
                k -= 1
            p.px(x + xx, y + yy, WINDOW_LIGHT[k])
    p.vline(x + w // 2, y, h, OAK[1])
    p.hline(x, y + h // 2, w, OAK[1])
    p.rect(x, y, w, 1, OAK[1])
    p.rect(x, y + h - 1, w, 1, OAK[1])
    p.vline(x, y, h, OAK[1])
    p.vline(x + w - 1, y, h, OAK[1])
    if w > 9:
        p.px(x + 2, y + 2, FLAME[4])                           # a glint on the glass


def house(w: int, wall_h: int, roof_h: int, seed: int, floors: int = 2) -> tuple[Pix, list[Window], tuple[int, int, int, int] | None]:
    """A timber-framed house seen from the front, in daylight tones: limewash between oak, an upper floor that juts out
    over the lower, a gable roof with barge boards, a chimney. Returns the picture, its window rectangles (in its own
    coordinates) and the door, if it has one."""
    top = roof_h
    p = Pix(w + 16, top + wall_h + 4, seed=seed)
    rng = p.rng
    ox = 8                                                     # room for the roof overhang
    floor_h = wall_h // floors
    # chimney first, so the roof overlaps its foot
    cx = ox + rng.randrange(w // 2, w - 14)
    p.rect(cx, 2, 9, top, STONE[2])
    masonry(p, cx, 2, 9, top, STONE, course=5)
    p.rect(cx - 1, 0, 11, 3, STONE[1])
    p.hline(cx - 1, 0, 11, STONE[3])
    windows: list[Window] = []
    door: tuple[int, int, int, int] | None = None
    for f in range(floors):
        y0 = top + f * floor_h
        jut = 4 if f == 1 and floors > 1 else 0
        x0, x1 = ox - jut, ox + w + jut
        plaster(p, x0, y0, x1 - x0, floor_h, PLASTER, stains=False)
        beam(p, x0, y0, 5, floor_h, OAK, vertical=True)
        beam(p, x1 - 5, y0, 5, floor_h, OAK, vertical=True)
        beam(p, x0, y0 + floor_h - 5, x1 - x0, 5, OAK, vertical=False)
        beam(p, x0, y0, x1 - x0, 4, OAK, vertical=False)
        if (x1 - x0) > 70:
            beam(p, (x0 + x1) // 2 - 2, y0, 4, floor_h, OAK, vertical=True)
        for bx, sgn in ((x0 + 5, 1), (x1 - 5, -1)):            # diagonal braces in the corners
            p.line(bx, y0 + floor_h - 6, bx + sgn * 14, y0 + 6, OAK[2])
            p.line(bx, y0 + floor_h - 7, bx + sgn * 14, y0 + 5, OAK[3])
        n = max(1, (x1 - x0 - 12) // 40)
        for i in range(n):
            wx = x0 + 6 + (x1 - x0 - 12) * (2 * i + 1) // (2 * n) - 7
            wy = y0 + 9
            ww, wh = 14, floor_h - 22
            if f == 0 and floors > 0 and door is None and i == n // 2 and w > 60 and seed % 3 == 0:
                continue
            window_frame(p, wx, wy, ww, wh)
            windows.append((wx, wy, ww, wh))
        if f == 1 and jut:                                      # the dark under the overhang
            for k in range(5):
                p.dither(ox, y0 + floor_h + k, w, 1, SHADOW, 0.9 - 0.18 * k)
    if seed % 3 == 0 and w > 60:
        dw, dh = 16, floor_h - 14
        dx = ox + w // 2 - dw // 2
        dy = top + wall_h - dh
        p.rect(dx - 2, dy - 2, dw + 4, dh + 2, OAK[1])
        planks(p, dx, dy, dw, dh, WOOD, plank=dw // 2, vertical=True, nails=False)
        p.rect(dx, dy, dw, 2, SHADOW)
        door = (dx, dy, dw, dh)
        p.rect(dx - 5, top + wall_h - 3, dw + 10, 3, STONE[2])
    # roof
    rp = Pix(w + 16, top + 6, seed=seed + 1)
    tiles(rp, 0, 0, w + 16, top + 6, [WINE[1], WOOD[1], IRON[2], WINE[2]][seed % 4])
    rp.clip([(0, top + 5), (ox + w // 2 + 4, 2), (w + 16, top + 5)])
    rp.outline(SHADOW, inside=True)
    p.paste(rp, 0, 0)
    p.line(0, top + 5, ox + w // 2 + 4, 2, OAK[3])             # barge boards along the gable
    p.line(w + 15, top + 5, ox + w // 2 + 5, 2, OAK[1])
    p.line(1, top + 5, ox + w // 2 + 4, 3, OAK[2])
    for k in range(6):                                          # the roof's shadow on the wall under the eaves
        p.dither(ox - 4, top + 5 + k, w + 8, 1, SHADOW, 0.9 - 0.15 * k)
    # attic window in the gable
    ax, ay = ox + w // 2 - 4, top - 2 - roof_h // 3
    if roof_h > 30:
        window_frame(p, ax, ay, 8, 10)
        windows.append((ax, ay, 8, 10))
    return p, windows, door


def smoke(p: Pix, x: int, y: int, rng: random.Random, height: int = 70) -> None:
    """A chimney's smoke: puffs that grow and thin out as they rise and lean with the wind, dithered into the sky."""
    for i in range(height // 4):
        k = i / (height / 4)
        r = 3 + round(7 * k)
        cx, cy = x + round(k * k * 40 + rng.randrange(-2, 3)), y - i * 4
        p.glow(cx, cy, r + 5, mix(NIGHT[4], rgb("#b4aab4"), 0.6), (1 - k) * 3.2)


# ---------------------------------------------------------------------------------------------- street


def cobbles(p: Pix, rng: random.Random) -> None:
    """The street: stones in rows that grow toward the viewer, each lit on top, with gutters between."""
    p.rect(0, GROUND, W, H - GROUND, STONE[0])
    y, rh = GROUND + 1, 4
    while y < H:
        x = -rng.randrange(0, 12)
        while x < W:
            sw = rng.randrange(rh * 2, rh * 4)
            c = rng.choice((STONE[1], STONE[1], STONE[2], mix(STONE[1], WINE[0], 0.4)))
            p.rect(x + 1, y, sw - 1, rh - 1, c)
            p.hline(x + 1, y, sw - 1, tone(c, 0.2))
            p.hline(x + 1, y + rh - 1, sw, STONE[0])
            x += sw
        y += rh
        rh = min(rh + 1 if (y - GROUND) % 16 < 4 else rh, 11)


def puddle(p: Pix, x: int, y: int, w: int, h: int, sky_c: Color, lamp: Color) -> None:
    """A wet patch that holds the sky and a reflection of the nearest lamp."""
    p.ellipse(x, y, w, h, mix(sky_c, SHADOW, 0.3))
    p.ellipse(x + 2, y + 1, w - 4, max(1, h - 3), sky_c)
    p.dither(x + w // 3, y + 1, w // 3, h - 2, lamp, 0.5)
    p.hline(x + w // 4, y + h // 2, w // 2, tone(lamp, 0.2))


def gallows(p: Pix, lettered: bool) -> None:
    """The inn sign: a tall post with a long arm and a brace, two chains, and a plank sign bound in iron that carries
    the title in cream capitals with a dark rim (or nothing, in the plain version)."""
    beam(p, 100, 12, 12, GROUND - 12 + 6, OAK, vertical=True)
    beam(p, 98, 10, 440, 9, OAK, vertical=False)
    for k in range(26):                                         # the brace under the arm
        p.rect(112 + k, 19 + k, 3, 3, OAK[2])
        p.px(112 + k, 19 + k, OAK[3])
    iron_strap(p, 98, 34, 16, 4)
    iron_strap(p, 98, 150, 16, 4)
    sx, sy, sw, sh = 150, 40, 340, 58
    for cx in (sx + 22, sx + sw - 22):                          # chains: links as alternate bars
        for y in range(19, sy + 1, 3):
            p.rect(cx, y, 2 if (y // 3) % 2 else 3, 2, IRON[3])
            p.px(cx, y, IRON[4])
        p.rect(cx - 1, 17, 4, 4, IRON[1])
    sign = Pix(sw, sh, seed=7)
    planks(sign, 0, 0, sw, sh, PALE_WOOD, plank=14, nails=False)
    for x0, y0, w0, h0 in ((0, 0, sw, 5), (0, sh - 5, sw, 5), (0, 0, 5, sh), (sw - 5, 0, 5, sh)):
        beam(sign, x0, y0, w0, h0, OAK)
    for x0, y0 in ((2, 2), (sw - 4, 2), (2, sh - 4), (sw - 4, sh - 4)):
        sign.rect(x0, y0, 2, 2, BRASS[3])
        sign.px(x0, y0, BRASS[4])
    for x0 in (sw // 2 - 40, sw // 2 + 38):                     # a pair of iron bands bind the planks
        iron_strap(sign, x0, 5, 4, sh - 10, rivets=False)
    p.paste(sign, sx, sy)
    p.rect(sx, sy + sh, sw, 3, SHADOW)                          # the sign's shadow edge
    p.dither(sx, sy + sh + 3, sw, 3, SHADOW, 0.5)
    if lettered:
        text = "DEEPSPACE EMPORIUM"
        scale = 3
        tw = font.width(text, scale)
        tx, ty = sx + (sw - tw) // 2, sy + (sh - 7 * scale) // 2
        shade = Pix(W, H)
        font.write(shade, tx, ty, text, SHADOW, scale)
        shade.outline(SHADOW)
        p.paste(shade, 1, 2)
        font.write(p, tx + 1, ty + 1, text, WINE[1], scale)     # a painted drop shadow, then the letters
        font.write(p, tx, ty, text, rgb("#f0dca0"), scale)
        for yy in range(ty, ty + 7 * scale):
            for xx in range(tx, tx + tw):
                if p.get(xx, yy)[:3] == rgb("#f0dca0") and yy - ty >= 5 * scale:
                    p.px(xx, yy, rgb("#d4b070"))


def street(lettered: bool) -> Image.Image:
    """The whole picture. Layers from far to near: sky and moon, skyline, a back row of small houses, the front row with
    the tavern in the middle, the cobbled street with its pools of light, and the inn-sign gallows over everything."""
    rng = random.Random(33)
    p = Pix(W, H, seed=33)
    sky(p, rng)
    moon(p, 560, 66, 26)
    skyline(p, rng)
    blue = mix(NIGHT[2], rgb("#4a3a58"), 0.3)
    # back row: small houses between the big ones, hazier
    for i, (x, w, wall, roof) in enumerate(((100, 40, 40, 24), (212, 40, 48, 26), (392, 50, 44, 26), (500, 40, 52, 28))):
        hp, wins, _ = house(w, wall, roof, 200 + i)
        im = night(hp.im, blue, 0.78)
        p.paste(im, x - 8, GROUND - 22 - wall - roof)
        q = Pix(W, H)
        for wx, wy, ww, wh in wins:
            light_window(q, x - 8 + wx, GROUND - 22 - wall - roof + wy, ww, wh, 0.35)
        p.paste(q, 0, 0)
    rows = ((-6, 94, 100, 50, 0), (132, 80, 92, 44, 1), (238, 140, 112, 46, 5), (410, 80, 90, 42, 2), (532, 106, 108, 52, 5))
    lights: list[tuple[int, int, int, int]] = []
    doors: list[tuple[int, int, int, int]] = []
    chimneys: list[tuple[int, int]] = []
    for i, (x, w, wall, roof, seed) in enumerate(rows):
        wall_h = wall + 40 if i == 2 else wall + 30
        hp, wins, door = house(w, wall_h, roof + 4, seed + 1)
        by = GROUND - hp.h
        im = night(hp.im, mix(NIGHT[1], rgb("#3a2a48"), 0.4), 0.58 if i != 2 else 0.5)
        p.paste(im, x - 8, by)
        q = Pix(W, H)
        for wx, wy, ww, wh in wins:
            if (i + wx) % 5 != 0 or i == 2:
                light_window(q, x - 8 + wx, by + wy, ww, wh, 1.0 if i == 2 else 0.7)
                lights.append((x - 8 + wx + ww // 2, by + wy + wh, ww, 0))
        if door is not None:
            dx, dy, dw, dh = door
            doors.append((x - 8 + dx, by + dy, dw, dh))
        p.paste(q, 0, 0)
        for y_i in range(hp.h):                                 # find this house's chimney by its stone tone at the top
            for x_i in range(hp.w):
                if hp.get(x_i, y_i)[:3] == STONE[1] and y_i < 3:
                    chimneys.append((x - 8 + x_i, by))
                    break
            else:
                continue
            break
    # the tavern's door: open, a doorway full of firelight, and a lantern on a hook beside it
    for dx, dy, dw, dh in doors:
        if 238 < dx < 380:
            p.rect(dx - 1, dy, dw + 2, dh, FLAME[0])
            for yy in range(dh):
                p.hline(dx, dy + yy, dw, FLAME[2] if yy < dh * 0.6 else FLAME[1])
            p.glow(dx + dw // 2, dy + dh, 34, FLAME[2], 0.9)
            p.vline(dx + dw // 2, dy, dh, OAK[1])
            p.ellipse(dx + dw // 2 - 10, GROUND, 20, 6, FLAME[1])
        else:
            p.rect(dx, dy, dw, dh, OAK[0])
    cobbles(p, rng)
    warm = mix(FLAME[1], STONE[2], 0.45)
    p.glow(309, GROUND + 4, 56, warm, 0.7)
    p.glow(309, GROUND + 4, 28, mix(FLAME[2], STONE[3], 0.4), 0.6)
    p.glow(150, GROUND + 4, 36, warm, 0.4)
    p.glow(560, GROUND + 4, 40, warm, 0.45)
    puddle(p, 250, 292, 60, 9, NIGHT[3], FLAME[3])
    puddle(p, 420, 303, 80, 10, NIGHT[3], FLAME[2])
    puddle(p, 40, 285, 40, 7, NIGHT[3], FLAME[1])
    # barrels and a bench by the tavern wall
    for bx in (392, 408):
        p.rect(bx, GROUND - 22, 14, 24, WOOD[2])
        for yy in (GROUND - 18, GROUND - 6):
            p.hline(bx, yy, 14, IRON[2])
        p.vline(bx, GROUND - 22, 24, WOOD[3])
        p.vline(bx + 13, GROUND - 22, 24, WOOD[0])
        p.hline(bx, GROUND - 22, 14, WOOD[4])
        p.hline(bx + 1, GROUND - 23, 12, SHADOW)
    # smoke from three chimneys
    for i, (x, y) in enumerate(chimneys[:5]):
        smoke(p, x + 4, y - 3, random.Random(9 + i), 56 + 10 * i)
    gallows(p, lettered)
    # a hanging lantern at the tavern door
    for dx, dy, dw, dh in doors:
        if 238 < dx < 380:
            lx = dx + dw + 8                                    # a lantern on a bracket beside the door
            p.hline(lx - 8, dy - 6, 9, IRON[2])
            p.rect(lx - 2, dy - 4, 5, 8, FLAME[3])
            p.rect(lx - 3, dy - 5, 7, 1, IRON[1])
            p.rect(lx - 3, dy + 4, 7, 1, IRON[1])
            p.px(lx, dy - 1, FLAME[4])
            p.glow(lx, dy, 18, FLAME[2], 0.8)
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
}
