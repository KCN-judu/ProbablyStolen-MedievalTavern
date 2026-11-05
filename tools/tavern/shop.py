"""The shop front of the tavern: the wall with its serving window, the bar, the window frame and shutter, the door, and
the lamplight. Every picture is a 960x540 layer the game stacks in a fixed order (see tools/preview/preview.py), so each
is drawn on a full canvas and keeps to the rectangle the game's layer of the same name fills (tools/tavern/layout.tsv).

The reading of the place: the game's shop is a counter behind a roller shutter in a concrete wall; here it is a bar in a
timber-framed wall, with a slatted wooden shutter over the serving window, a leaded-glass pane behind it, and a back room
of beams, stairs and casks. Customers are served through the window.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping

from PIL import Image

from font import write as write_text
from materials import beam, iron_strap, masonry, planks, plaster, shadow_under, vertical_strap
from palette import BRASS, FLAME, GLASS, IRON, MOSS, OAK, PALE_WOOD, PLASTER, SHADOW, STONE, WOOD
from pix import Pix, mix
from shopx_parts import door, door_lock, lamp, lighting, window_top
from shopx_persp import (VP, ROUND, blend, board_plane, ellipse_shadow, overlay_shadow, shade_poly, stepped,
                         tier, toward_vp)

W, H = 960, 540
HOLE = (324, 0, 639, 327)       # the serving window cut into the wall: x0, y0, x1, y1 (x1, y1 not included)


# ---------------------------------------------------------------------------------------------- the wall


def brace(p: Pix, top_x: int, post_x: int, y_post: int, width: int = 18) -> None:
    """A diagonal brace of constant width from the tie beam (at `top_x`) down to a post (at `post_x`): both long edges
    are parallel, the upper one lit, the lower one dark, with a soft cast shade on the plaster beside it."""
    sign = 1 if post_x > top_x else -1
    k = (y_post - 26) / abs(post_x - top_x)                       # drop per pixel of run
    y_low = 26 + abs(post_x - top_x) * k                           # where the outer edge reaches the post
    y_high = y_low - width * k                                      # and where the inner edge does
    pts = [(top_x, 26), (top_x + sign * width, 26), (post_x, round(y_high)), (post_x, round(y_low))]
    shade_poly(p, [(x + 7, y + 6) for x, y in pts], 0.4)           # light is from the upper left: shade falls right and down
    shade_poly(p, [(x + 12, y + 10) for x, y in pts], 0.18)
    p.poly(pts, OAK[2])
    p.line(*pts[0], *pts[3], OAK[3] if sign > 0 else OAK[0])
    p.line(*pts[1], *pts[2], OAK[0] if sign > 0 else OAK[3])
    mid_x = top_x + sign * width // 2
    mid_y = (y_high + y_low) / 2
    for off in (-3, 3):                                             # grain along the brace
        p.line(mid_x + off, 30, post_x, round(mid_y) + off, OAK[1])


def wall(variant: int = 0) -> Image.Image:
    """The wall the customer stands behind: timber frame and limewash above, a stone plinth below, boards underfoot laid
    in perspective, and the serving window cut out of the middle. `variant` is the same wall more worn."""
    p = Pix(W, H, seed=11 + variant)
    plaster(p, 0, 0, W, 384, PLASTER, stains=False)
    # soot creeping up from the plinth: the dither gets denser in small bands, so it reads as a gradient, not a mesh
    soot = mix(PLASTER[2][:3], SHADOW[:3], 0.4)     # a tone near the plaster's own, so the dots stay quiet
    for band in range(12):
        p.dither(0, 300 + band * 7, W, 7, soot, 0.05 + band * 0.05)
    masonry(p, 0, 372, W, 104, STONE, course=13, moss=None)
    p.hline(0, 474, W, STONE[4])                                 # the top edge of the plinth's last course
    p.hline(0, 475, W, STONE[0])
    floor = Pix(W, H, seed=12 + variant)
    board_plane(floor, 0, W, 476, H, WOOD, 7, tones=(1, 2, 2, 1), span=(220, 460))
    floor.clip([(0, 476), (W, 476), (W, H), (0, H)])
    p.paste(floor, 0, 0)
    for y in range(476, H):                                      # the plinth shades the boards at its foot
        for x in range(W):
            if stepped(0.55 * max(0.0, 1 - (y - 476) / 14), x, y):
                blend(p, x, y, SHADOW, 0.6)

    for top_x, post_x, y_post in ((136, 296, 200), (824, 667, 210)):   # braces, from the tie beam down to the posts
        brace(p, top_x, post_x, y_post)
    for x in (0, 296, 639, 944):                              # posts
        pw = 16 if x in (0, 944) else 28
        beam(p, x, 0, pw, 480, OAK, vertical=True)
        for y in range(480, 490):                              # a post stands on the boards: its contact shade
            for dx in range(-4, pw + 4):
                edge = max(0, -dx, dx - pw + 1) / 4
                if stepped(0.55 * (1 - (y - 480) / 10) * (1 - edge), x + dx, y):
                    blend(p, x + dx, y, SHADOW, 0.6)
    beam(p, 0, 0, W, 26, OAK, vertical=False)                 # the tie beam under the ceiling
    beam(p, 0, 340, W, 14, OAK, vertical=False)               # the rail the plaster stops at
    shadow_under(p, 0, 26, W, 7)
    shadow_under(p, 0, 354, W, 6)
    for y in range(26, H):                                    # lamplight falls off toward the corners of the room
        for x in range(16, 944):
            d = math.hypot((x - 480) / 520, (y - 210) / 330)
            k = tier(max(0.0, min(1.0, (d - 0.42) / 0.75)), x, y)
            if k:
                blend(p, x, y, SHADOW, 0.1 * k)
    for x in (296, 639):
        iron_strap(p, x - 1, 60, 30, 6)
        iron_strap(p, x - 1, 250, 30, 6)

    p.erase(HOLE[0], HOLE[1], HOLE[2] - HOLE[0], HOLE[3] - HOLE[1])
    for i in range(6):                                        # the wall is thick: its edge casts a shade into the opening
        p.vline(HOLE[0] + i, 0, HOLE[3], (*SHADOW, 255 - i * 40))
    p.hline(HOLE[0], HOLE[3], HOLE[2] - HOLE[0], OAK[3])
    p.hline(HOLE[0], HOLE[3] + 1, HOLE[2] - HOLE[0], OAK[0])
    return p.finish()


# ---------------------------------------------------------------------------------------------- the bar

TOP_Y0, TOP_Y1 = 269, 333        # the far and near edges of the counter top
WING_Y1 = 372                    # the near edge of the right wing
LEFT_X, MAIN_X1 = 201, 802       # the main top's left end and the right end of its near edge
FOOT = 520                       # where the legs and the cask stand on the boards
LEGS = (214, 772)


def desk() -> Image.Image:
    """The bar: an oak top in perspective (boards converge on the vanishing point), its lit lip, an apron of planks and
    iron, two legs, a till, the right wing that comes toward the viewer, and a cask on the floor beside the legs. The
    shade under the bar is a soft falloff that follows the counter, the legs and the cask."""
    p = Pix(W, H, seed=21)
    back_left = round(toward_vp(LEFT_X, TOP_Y1, TOP_Y0))
    wing_x = round(toward_vp(MAIN_X1, TOP_Y1, WING_Y1))
    top_shape = [(LEFT_X, TOP_Y1), (back_left, TOP_Y0), (W, TOP_Y0), (W, WING_Y1), (wing_x, WING_Y1), (MAIN_X1, TOP_Y1)]

    # shade first (it only lands on transparent pixels), then the solid things go over it
    soft_under(p)
    for lx in LEGS:                                               # a leg's contact shade on the boards
        overlay_shadow(p, max(LEFT_X, lx - 24), FOOT - 10, lx + 60, FOOT + 16, ellipse_shadow(lx + 15, FOOT, 38, 8, 0.95), alpha=210)
    overlay_shadow(p, 600, FOOT - 14, 790, FOOT + 24, ellipse_shadow(695, FOOT, 82, 12, 0.95), alpha=210)
    for lx in LEGS:
        leg(p, lx, TOP_Y1 + 14, FOOT)
    cask(p, 695, FOOT - 3, 60, 178)

    # boards of the top, in rows of equal depth
    top = Pix(W, H, seed=22)
    board_plane(top, 190, W, TOP_Y0, WING_Y1, PALE_WOOD, 9, tones=(2, 2, 3, 2), span=(170, 340))
    for sx, sy in ((345, 296), (470, 311), (615, 291), (750, 322)):       # rings left by wet tankards
        rx = 11
        ry = max(2, round(rx * (sy - VP[1]) / 600))
        top.ellipse(sx - rx, sy - ry, 2 * rx, 2 * ry, mix(PALE_WOOD[1][:3], PALE_WOOD[2][:3], 0.4))
        top.ellipse(sx - rx + 2, sy - ry + 1, 2 * rx - 4, max(1, 2 * ry - 2), PALE_WOOD[2])
    for y in range(TOP_Y1 - 22, WING_Y1):                         # wear is heaviest along the near edge, where arms rest
        for x in range(190, W):
            if top.rng.random() < 0.06 * min(1.0, (y - TOP_Y1 + 22) / 22):
                top.px(x, y, PALE_WOOD[4] if top.rng.random() < 0.5 else PALE_WOOD[1])
    top.clip(top_shape)
    p.paste(top, 0, 0)

    # the near edge: a lit lip, then the front face (the wing is nearer, so its front is thicker)
    p.line(LEFT_X, TOP_Y1, back_left, TOP_Y0, PALE_WOOD[4])
    p.line(LEFT_X + 1, TOP_Y1 + 1, back_left + 1, TOP_Y0 + 1, OAK[0])
    p.hline(LEFT_X + 4, TOP_Y1, MAIN_X1 - LEFT_X - 4, PALE_WOOD[4])
    p.hline(LEFT_X + 2, TOP_Y1 + 1, MAIN_X1 - LEFT_X - 2, PALE_WOOD[3])
    p.rect(LEFT_X, TOP_Y1 + 2, MAIN_X1 - LEFT_X, 12, OAK[2])
    p.hline(LEFT_X, TOP_Y1 + 2, MAIN_X1 - LEFT_X, OAK[3])
    p.hline(LEFT_X, TOP_Y1 + 13, MAIN_X1 - LEFT_X, OAK[0])
    for sx in range(262, 800, 118):                           # plank seams in the apron, with an iron strap at each
        p.vline(sx, TOP_Y1 + 3, 10, OAK[0])
        vertical_strap(p, sx + 3, TOP_Y1 + 2, 7, 12, rivets=False)
    p.speckle(LEFT_X, TOP_Y1 + 3, MAIN_X1 - LEFT_X, 10, (OAK[1], OAK[3]), 0.05)
    drawer(p, 376, 347, 150, 14)

    # the wing: its left side runs down the line to VP; its front is nearer, so it is thicker
    t_w = 16
    p.poly([(MAIN_X1, TOP_Y1), (wing_x, WING_Y1), (wing_x, WING_Y1 + t_w), (MAIN_X1, TOP_Y1 + 13)], OAK[1])
    p.line(MAIN_X1, TOP_Y1, wing_x, WING_Y1, PALE_WOOD[4])
    p.line(MAIN_X1, TOP_Y1 + 1, wing_x, WING_Y1 + 1, PALE_WOOD[3])
    p.line(MAIN_X1, TOP_Y1 + 13, wing_x, WING_Y1 + t_w, OAK[0])
    p.rect(wing_x, WING_Y1, W - wing_x, t_w + 1, OAK[2])         # the wing's front face
    p.hline(wing_x, WING_Y1, W - wing_x, PALE_WOOD[4])
    p.hline(wing_x, WING_Y1 + 1, W - wing_x, PALE_WOOD[3])
    p.hline(wing_x, WING_Y1 + t_w, W - wing_x, OAK[0])
    for sx in (wing_x + 22, wing_x + 80):
        p.vline(sx - 1, WING_Y1 + 3, t_w - 3, OAK[0])
        vertical_strap(p, sx, WING_Y1 + 2, 7, t_w - 2, rivets=False)
    return p.finish()


# ---------------------------------------------------------------------------------------------- the cask


def _noise(x: int, y: int, s: int = 0) -> float:
    """A repeatable 0..1 value for a pixel (so the grain does not depend on the order of drawing)."""
    n = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791)
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535


def cask(p: Pix, cx: int, foot_y: int, half: int, height: int) -> None:
    """The cask under the bar. Staves are strips of equal angle round the belly (narrow at the sides), each with its own
    tone, grain lines that bend with the belly, knots and a lit edge; the gaps between staves curve with the belly. Four
    riveted iron hoops are arcs of ellipses; the upper left is lit, the right shaded; damp darkens the foot; a brass bung
    and tap, a branded mark and scratches finish it. The top is hidden behind the apron of the bar."""
    vy = VP[1]
    top = foot_y - height
    rbot = half - 6
    rng = random.Random(41)
    staves = 13

    def hw(y: float) -> float:
        t = (y - top) / height
        return rbot + 6 * (1 - (2 * t - 1) ** 2)

    ry_b = max(2, round(rbot * (foot_y - vy) / ROUND))
    st = [{"off": rng.choice((-0.9, -0.45, 0.0, 0.0, 0.45, 0.8)) + rng.uniform(-0.15, 0.15), "grain": [rng.uniform(0.12, 0.88) for _ in range(rng.randint(2, 4))],
           "ph": rng.uniform(0, 6.3), "fr": rng.uniform(0.025, 0.06)} for _ in range(staves)]
    for y in range(top, foot_y + ry_b + 1):
        w = hw(min(y, foot_y))
        for dx in range(-half, half + 1):
            if y <= foot_y:
                if abs(dx) >= w:
                    continue
            elif abs(dx) >= rbot or y > foot_y + ry_b * math.sqrt(1 - (dx / rbot) ** 2):
                continue
            wy = w if y <= foot_y else rbot
            th = math.asin(max(-1.0, min(1.0, dx / wy)))
            u = (th + math.pi / 2) / math.pi
            k = min(staves - 1, int(u * staves))
            f = u * staves - k
            s = st[k]
            pw = max(0.2, wy * math.cos(th) * math.pi / staves)
            v = 2.5 + s["off"] + 2.5 * (0.45 * math.cos(th) - 0.85 * math.sin(th)) - 0.2
            v += 0.7 * (_noise(dx // 3, y // 9, 3) - 0.5)                     # tone drifting along a stave
            for g in s["grain"]:                                             # grain lines that wander with the wood
                gd = abs(f - (g + 0.06 * math.sin(y * s["fr"] + s["ph"]))) * pw
                if gd < 0.6 and _noise(dx // 5, y // 7, k) > 0.5:
                    v -= 0.7 if g < 0.5 else -0.6
            nz = _noise(dx, y, 9)
            v += -0.9 if nz < 0.035 else 0.7 if nz > 0.975 else 0.0           # pits and bright flecks
            v -= 1.5 * max(0.0, 1 - (y - 346) / 52) ** 1.2                    # the bar's shade at the top
            wet = max(0.0, (y - (foot_y - 40)) / 40) * (0.55 + 0.9 * _noise(dx // 4, 0, 17))
            v -= 1.15 * wet
            edge = f * pw
            if k > 0 and edge < min(1.1, pw * 0.4):                          # the joint between two staves
                p.px(cx + dx, y, WOOD[0])
                continue
            if k > 0 and edge < min(2.2, pw * 0.8):
                v += 0.7 if u < 0.62 else 0.2                                # its lit side
            if (1 - f) * pw < 1.4:
                v -= 0.5
            idx = max(0, min(4, int(v + 0.5 + (_noise(dx, y, 5) - 0.5) * 0.5)))
            c = WOOD[idx]
            if wet > 0.45 and _noise(dx, y, 23) < 0.35:                      # damp, mossy dark at the foot
                c = mix(c[:3], MOSS[0][:3], 0.45)
            p.px(cx + dx, y, c)
    for y in range(347, foot_y + 1):                                         # a rim light on the left silhouette
        xl = cx - int(hw(y)) + 1
        p.px(xl, y, WOOD[4])
        if y > 360 and _noise(0, y, 31) < 0.5:
            p.px(xl + 1, y, WOOD[3])
    # knots: a dark eye, a ring, a lit lower lip
    for kx, ky, kw, kh in ((-37, 381, 4, 6), (40, 392, 3, 5), (-12, 489, 4, 6), (-50, 438, 3, 5), (13, 471, 3, 5),
                           (46, 482, 3, 4)):
        for yy in range(-kh - 2, kh + 3):
            for xx in range(-kw - 2, kw + 3):
                d = math.hypot(xx / (kw + 1), yy / (kh + 1))
                if d < 1.0 and abs(kx + xx) < hw(ky) - 2:
                    p.px(cx + kx + xx, ky + yy, WOOD[0] if d < 0.35 else WOOD[1] if d < 0.62
                         else (WOOD[3] if (xx + yy > 0 and kx < 20) else WOOD[2]))
    for _ in range(14):                                                      # scratches and dents
        x0, y0 = rng.randrange(-52, 30), rng.randrange(360, 505)
        n = rng.randrange(5, 14)
        dark = rng.random() < 0.45
        for i in range(n):
            p.px(cx + x0 + i, y0 + (i * 2) // 5, WOOD[0] if dark else WOOD[4])
    # a mark burned in the wood between the two middle hoops
    tmp = Pix(40, 16)
    write_text(tmp, 3, 1, "ALE", (255, 255, 255), 2)
    for y in range(tmp.h):
        for x in range(tmp.w):
            if tmp.get(x, y)[3] and _noise(x, y, 51) > 0.22:                 # worn: a few specks are missing
                p.px(cx - 28 + x, 421 + y, mix(WOOD[0][:3], SHADOW[:3], 0.4))
    for ang in range(0, 360, 4):                                             # a ring with a cross under the word
        a = math.radians(ang)
        p.px(cx - 9 + round(7 * math.cos(a)), 444 + round(5 * math.sin(a)), WOOD[0])
    p.hline(cx - 16, 444, 15, WOOD[0])
    p.vline(cx - 9, 440, 9, WOOD[0])
    # the foot: a chime (rim) just inside the lower edge, then the hoops
    for dx in range(-rbot + 1, rbot):
        yy = foot_y + round(ry_b * math.sqrt(1 - (dx / rbot) ** 2))
        p.px(cx + dx, yy, SHADOW)
        p.px(cx + dx, yy - 1, WOOD[0])
        p.px(cx + dx, yy - 2, WOOD[3] if dx < -rbot // 3 else WOOD[2] if dx < rbot // 3 else WOOD[1])
        p.px(cx + dx, yy - 3, WOOD[4] if dx < -rbot // 3 and dx % 2 == 0 else WOOD[1])
    for frac in (0.14, 0.36, 0.70, 0.90):
        hy = round(top + height * frac)
        hoop(p, cx, hy, hw(hy), vy)
    bung(p, cx - 20, 386)
    tap(p, cx + 27, 433)


def hoop(p: Pix, cx: int, hy: int, wid: float, vy: int) -> None:
    """An iron ribbon round the belly: five rows lit on top, shaded to the right, rivets at equal angles."""
    ry = wid * (hy - vy) / ROUND
    for dx in range(-int(wid) + 1, int(wid)):
        yc = hy + round(ry * math.sqrt(1 - (dx / wid) ** 2))
        u = (dx / wid + 1) / 2
        shift = 0 if u < 0.35 else -1 if u < 0.7 else -2
        for i, r in enumerate((4, 3, 2, 1, 0)):
            c = IRON[max(0, min(4, r + shift + (1 if i < 2 and u < 0.2 else 0)))]
            if i == 1 and _noise(dx, hy, 61) < 0.07:
                c = BRASS[1]                                                 # a fleck of rust
            p.px(cx + dx, yc + i, c)
        for i in (5, 6):                                                    # the hoop's shade on the staves beneath it
            if stepped(0.6 if i == 5 else 0.3, cx + dx, yc + i):
                blend(p, cx + dx, yc + i, SHADOW, 0.55)
        if stepped(0.25, cx + dx, yc - 1):                                   # lit staves just above it
            blend(p, cx + dx, yc - 1, WOOD[4], 0.3)
    for k in range(1, 10):                                                   # rivets
        th = k * math.pi / 10 - math.pi / 2
        dx = round(wid * math.sin(th))
        yc = hy + round(ry * math.cos(th))
        lit = k < 6
        p.px(cx + dx, yc + 1, BRASS[4] if lit else BRASS[2])
        p.px(cx + dx + 1, yc + 1, BRASS[3] if lit else BRASS[1])
        p.px(cx + dx, yc + 2, BRASS[2] if lit else BRASS[0])
        p.px(cx + dx + 1, yc + 2, BRASS[1] if lit else BRASS[0])


def bung(p: Pix, x: int, y: int) -> None:
    """A brass plate round the bung with a wooden stopper in it."""
    p.ellipse(x - 7, y - 5, 15, 11, BRASS[0])
    p.ellipse(x - 6, y - 4, 13, 9, BRASS[2])
    p.hline(x - 4, y - 4, 7, BRASS[4])
    p.px(x - 6, y - 1, BRASS[4])
    p.hline(x - 3, y + 4, 8, BRASS[1])
    p.ellipse(x - 3, y - 2, 7, 5, WOOD[0])
    p.ellipse(x - 2, y - 1, 5, 3, WOOD[2])
    p.hline(x - 2, y - 1, 3, WOOD[3])
    p.px(x - 2, y - 2, BRASS[4])


def tap(p: Pix, x: int, y: int) -> None:
    """A brass tap: a round plate on the stave, a spout that turns down, a lever; a wet streak runs below it."""
    for yy in range(y + 7, y + 40):                                          # damp streak from the spout
        if yy < y + 14 or stepped(0.5 * (1 - (yy - y - 7) / 33), x + 20, yy):
            for xx in (x + 19, x + 20, x + 21):
                blend(p, xx, yy, SHADOW, 0.5 if xx == x + 20 else 0.25)
    for yy in range(y - 5, y + 28):                                          # the tap's cast shade, down and right
        for xx in range(x + 2, x + 28):
            if stepped(0.28, xx, yy):
                blend(p, xx + 2, yy + 3, SHADOW, 0.35)
    p.ellipse(x - 6, y - 8, 13, 17, BRASS[0])                               # round plate
    p.ellipse(x - 5, y - 7, 11, 15, BRASS[2])
    p.vline(x - 4, y - 5, 8, BRASS[4])
    p.hline(x - 3, y - 7, 5, BRASS[4])
    p.vline(x + 4, y - 4, 9, BRASS[1])
    for i, c in enumerate((BRASS[4], BRASS[3], BRASS[2], BRASS[1], BRASS[0])):             # the tube
        p.hline(x + 2, y - 3 + i, 21, c)
    for i, c in enumerate((BRASS[4], BRASS[3], BRASS[2], BRASS[1], BRASS[0])):             # the elbow and spout going down
        p.vline(x + 18 + i, y - 3, 22, c)
    p.hline(x + 16, y + 19, 9, BRASS[3])                                     # nozzle ring
    p.hline(x + 16, y + 20, 9, BRASS[1])
    p.hline(x + 16, y + 21, 9, BRASS[0])
    p.px(x + 20, y + 23, GLASS[4])                                           # a drop
    p.vline(x + 7, y - 12, 10, BRASS[4])                                     # the lever and its stem
    p.vline(x + 8, y - 12, 10, BRASS[3])
    p.vline(x + 9, y - 12, 10, BRASS[1])
    p.hline(x + 2, y - 14, 13, BRASS[4])
    p.hline(x + 2, y - 13, 13, BRASS[3])
    p.hline(x + 2, y - 12, 13, BRASS[1])
    p.px(x + 1, y - 13, BRASS[2])
    p.px(x + 15, y - 13, BRASS[0])


def soft_under(p: Pix) -> None:
    """The shade under the bar and the wing: strongest just under the apron and fading down the plinth in grains; the
    ends fade out sideways, so no edge is straight."""
    def under_main(x: int, y: int) -> float:
        fy = max(0.0, 1 - (y - 347) / 80) ** 1.1
        fx = min(1.0, (x - LEFT_X) / 46) * min(1.0, (MAIN_X1 + 20 - x) / 40)
        return 1.0 * fy * max(0.0, fx)

    def under_wing(x: int, y: int) -> float:
        fy = max(0.0, 1 - (y - 390) / 46) ** 1.4
        return 0.8 * fy * min(1.0, (x - 830) / 36)

    def on_floor(x: int, y: int) -> float:                        # the counter shades the boards under it
        fy = max(0.0, 1 - (y - 476) / 40) ** 1.2
        fx = min(1.0, (x - LEFT_X) / 40) * min(1.0, (MAIN_X1 + 50 - x) / 60)
        return 0.5 * fy * max(0.0, fx)

    overlay_shadow(p, LEFT_X, 347, MAIN_X1 + 20, 420, under_main, alpha=190)
    overlay_shadow(p, 830, 390, W, 440, under_wing, alpha=190)
    overlay_shadow(p, LEFT_X, 476, MAIN_X1 + 50, 520, on_floor, alpha=150)


def leg(p: Pix, x: int, y0: int, foot: int) -> None:
    """A square oak leg: a lit front, a turned-away side facing the room's middle, and a worn iron shoe."""
    w = 26
    h = foot - y0
    p.rect(x, y0, w, h, OAK[2])
    p.vline(x, y0, h, OAK[4])
    p.vline(x + 1, y0, h, OAK[3])
    p.vline(x + w - 1, y0, h, OAK[0])
    p.vline(x + w - 2, y0, h, OAK[1])
    side_x = x + w if x < VP[0] else x - 5
    p.rect(side_x, y0, 5, h - 2, OAK[0])                          # the side face seen toward the vanishing point
    p.vline(side_x + (0 if x < VP[0] else 4), y0, h - 2, OAK[1])
    for yy in range(y0, foot - 20, 9):                            # grain checks
        p.vline(x + 8 + (yy % 3) * 4, yy + 3, 5, OAK[1])
    p.rect(x - 2, foot - 16, w + 9, 14, IRON[2])                 # iron shoe
    p.hline(x - 2, foot - 16, w + 9, IRON[4])
    p.hline(x - 2, foot - 3, w + 9, IRON[0])
    p.px(x + 3, foot - 10, BRASS[3])
    p.px(x + w - 4, foot - 10, BRASS[3])
    p.hline(x - 2, foot - 2, w + 9, OAK[0])
    p.hline(x - 2, foot - 1, w + 9, OAK[0])


def drawer(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """The till under the bar: a plain drawer front with a brass pull and a keyhole."""
    p.rect(x, y, w, h, PALE_WOOD[1])
    p.bevel(x, y, w, h, PALE_WOOD[3], OAK[0])
    p.rect(x + w // 2 - 8, y + 4, 16, 3, BRASS[3])
    p.hline(x + w // 2 - 8, y + 4, 16, BRASS[4])
    p.px(x + w - 12, y + 6, SHADOW)
    p.px(x + w - 12, y + 7, SHADOW)


# ---------------------------------------------------------------------------------------------- window, shutter, glass


def window_frame() -> Image.Image:
    """The frame of the serving window in front of the shutter: two posts and a sill, strapped with iron."""
    p = Pix(W, H, seed=31)
    beam(p, 314, 0, 22, 271, OAK, vertical=True)
    beam(p, 625, 0, 22, 271, OAK, vertical=True)
    beam(p, 314, 252, 333, 19, OAK, vertical=False)
    p.hline(314, 252, 333, OAK[4])
    for x in (314, 625):
        for y in (40, 130, 215):
            iron_strap(p, x, y, 22, 7)
    for x in (320, 631):
        p.px(x + 7, 262, IRON[4])
    return p.finish()


def shutter() -> Image.Image:
    """A tambour shutter of narrow oak slats on guide rails, with an iron pull-bar and ring at the bottom."""
    p = Pix(W, H, seed=33)
    x0, y0, x1, y1 = 329, 24, 631, 265
    y = y0
    row = 0
    while y < y1 - 14:
        h = min(6, y1 - 14 - y)
        tone = (2, 3, 2, 2, 1, 3)[row % 6]
        p.rect(x0 + 4, y, x1 - x0 - 8, h, WOOD[tone])
        p.hline(x0 + 4, y, x1 - x0 - 8, WOOD[min(4, tone + 1)])
        p.hline(x0 + 4, y + h - 1, x1 - x0 - 8, WOOD[0])
        for _ in range(3):
            gx = x0 + 6 + p.rng.randrange(x1 - x0 - 30)
            p.hline(gx, y + 2, p.rng.randrange(8, 30), WOOD[max(0, tone - 1)])
        y += 6
        row += 1
    beam(p, x0, y1 - 15, x1 - x0, 15, OAK, vertical=False)    # the pull-bar
    iron_strap(p, x0 + 2, y1 - 13, x1 - x0 - 4, 5)
    cx = (x0 + x1) // 2
    p.ellipse(cx - 7, y1 - 14, 14, 14, BRASS[2])               # the ring
    p.ellipse(cx - 4, y1 - 11, 8, 8, SHADOW)
    p.hline(cx - 6, y1 - 13, 8, BRASS[4])
    beam(p, x0, y0, 5, y1 - y0, IRON, vertical=True)
    beam(p, x1 - 5, y0, 5, y1 - y0, IRON, vertical=True)
    return p.finish()


def glass() -> Image.Image:
    """The leaded pane behind the shutter: a diamond lattice of lead came, tinted glass, and slanting glare."""
    p = Pix(W, H, seed=34)
    x0, y0, x1, y1 = 331, 22, 629, 263
    p.rect(x0, y0, x1 - x0, y1 - y0, (*GLASS[2][:3], 70))
    step = 30
    for k in range(-(y1 - y0), x1 - x0 + step, step):
        p.line(x0 + k, y0, x0 + k + (y1 - y0), y1, (*IRON[1][:3], 255))
        p.line(x0 + k + (y1 - y0), y0, x0 + k, y1, (*IRON[1][:3], 255))
    p.frame(x0, y0, x1 - x0, y1 - y0, IRON[0])
    for gx, gw in ((60, 18), (110, 8), (190, 24)):             # glare
        for i in range(y1 - y0):
            p.dither(x0 + gx + i * 3 // 4, y0 + i, gw, 1, (255, 215, 150, 255), 0.07)
    p.clip([(x0, y0), (x1 - 1, y0), (x1 - 1, y1 - 1), (x0, y1 - 1)])
    return p.finish()


# ---------------------------------------------------------------------------------------------- the list


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
}
