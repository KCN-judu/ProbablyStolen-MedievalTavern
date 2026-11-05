"""Perspective helpers for the shop: one viewpoint for every picture of the shop view.

The shop is seen from slightly above and in front. Every line that runs away from the viewer meets at one vanishing
point (VP) at the horizontal middle of the picture; lines across the view stay level and lines that stand up stay
upright. Boards of a floor or a counter top are laid in rows of equal depth, so the rows grow taller toward the viewer
and their butt joints lean toward VP. Round things (casks, hoops) are ellipse arcs whose roundness grows with the
distance below the horizon.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from PIL import Image, ImageDraw

from palette import BRASS, IRON, SHADOW
from pix import BAYER, Color, Pix, Ramp, mix

VP: tuple[int, int] = (480, 150)         # the vanishing point (horizon at y = 150)
ROUND: float = 2000.0                    # a circle at depth y is an ellipse of height width * (y - VP_y) / ROUND


def toward_vp(x: float, y_from: float, y_to: float) -> float:
    """Moves the point (x, y_from) along its line to VP until it lies at y_to; returns the new x."""
    vx, vy = VP
    return vx + (x - vx) * (y_to - vy) / (y_from - vy)


def row_edges(y_far: int, y_near: int, n: int) -> list[int]:
    """The `n + 1` row boundaries of boards of equal depth between two screen rows: inverse distance below the horizon is
    linear in depth, so rows are thin far away and tall near the viewer."""
    vy = VP[1]
    u_far, u_near = 1 / (y_far - vy), 1 / (y_near - vy)
    edges = [round(vy + 1 / (u_far - (u_far - u_near) * k / n)) for k in range(n + 1)]
    edges[0], edges[-1] = y_far, y_near
    return edges


def blend(p: Pix, x: int, y: int, c: Color, t: float) -> None:
    """Pulls an opaque pixel toward colour `c` by `t`; transparent pixels are left alone."""
    if 0 <= x < p.w and 0 <= y < p.h:
        r, g, b, a = p.get(x, y)
        if a:
            p.px(x, y, (*mix((r, g, b), c[:3], t), a))


def stepped(level: float, x: int, y: int) -> bool:
    """Ordered-dither test: True on a share `level` of the pixels."""
    return BAYER[y % 4][x % 4] < round(max(0.0, min(1.0, level)) * 16)


def board_plane(p: Pix, x0: int, x1: int, y_far: int, y_near: int, ramp: Ramp, rows: int,
                tones: Sequence[int] = (1, 2, 2, 3), span: tuple[int, int] = (150, 300),
                origin: tuple[int, int] = (0, 0)) -> None:
    """Fills x0..x1, y_far..y_near with boards that run across the view, in `rows` rows of equal depth. Butt joints are
    taken in world units and projected, so they lean toward VP; each board has its own tone and grain. Coordinates are
    those of the whole view; `origin` is where the canvas `p` lies in it (for a layer drawn on a small canvas)."""
    ox, oy = origin
    vx, vy = VP
    ref = y_near - vy
    edges = row_edges(y_far, y_near, rows)
    last = len(ramp) - 1
    for r in range(rows):
        ya, yb = edges[r], edges[r + 1]
        s_min = (ya - vy) / ref
        w_lo, w_hi = (x0 - vx) / s_min - 400, (x1 - vx) / s_min + 400
        joints = [w_lo + p.rng.uniform(0, span[1])]
        while joints[-1] < w_hi:
            joints.append(joints[-1] + p.rng.uniform(*span))
        board_tone = [p.rng.choice(tones) for _ in joints]
        for y in range(ya, yb):
            s = (y - vy) / ref
            for k, jw in enumerate(joints):
                xa = round(vx + jw * s)
                xb = round(vx + (joints[k + 1] if k + 1 < len(joints) else w_hi + 400) * s)
                xa_c, xb_c = max(x0, xa), min(x1, xb)
                if xb_c <= xa_c:
                    continue
                t = board_tone[k]
                top, bottom = y == ya, y == yb - 1
                shade = y == yb - 2 and yb - ya > 4
                c = ramp[min(last, t + 1)] if top else ramp[0] if bottom else ramp[max(0, t - 1)] if shade else ramp[t]
                p.hline(xa_c - ox, y - oy, xb_c - xa_c, c)
                if x0 <= xa < x1 and not top:                    # the butt joint and its lit side
                    p.px(xa - ox, y - oy, ramp[0])
                    p.px(xa + 1 - ox, y - oy, ramp[min(last, t + 1)]) if xa + 1 < xb else None
        for k, jw in enumerate(joints):                          # grain streaks along each board
            t = board_tone[k]
            length = (joints[k + 1] - jw if k + 1 < len(joints) else 200) * (ya - vy) / ref
            for _ in range(max(1, int(length) * (yb - ya) // 70)):
                y = p.rng.randrange(ya + 1, max(ya + 2, yb - 2))
                s = (y - vy) / ref
                gx = round(vx + (jw + p.rng.uniform(0, 1) * (joints[k + 1] - jw if k + 1 < len(joints) else 200)) * s)
                c = ramp[max(0, t - 1)] if p.rng.random() < 0.7 else ramp[min(last, t + 1)]
                n = p.rng.randrange(6, 26)
                p.hline(max(x0, gx) - ox, y - oy, max(0, min(n, x1 - max(x0, gx))), c)


def clip_paste(dst: Pix, sub: Pix, points: Sequence[tuple[int, int]]) -> None:
    """Lays `sub` over `dst` keeping only what is inside a polygon (so a plane of boards gets the shape of its plane)."""
    sub.clip(points)
    dst.paste(sub, 0, 0)


def poly_mask(size: tuple[int, int], points: Sequence[tuple[int, int]]) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(list(points), fill=255)
    return m


def shade_poly(p: Pix, points: Sequence[tuple[int, int]], level: float, c: Color = SHADOW, t: float = 0.5) -> None:
    """Darkens the opaque pixels inside a polygon on an ordered-dither share `level`."""
    m = poly_mask((p.w, p.h), points)
    for y in range(p.h):
        for x in range(p.w):
            if m.getpixel((x, y)) and stepped(level, x, y):  # type: ignore[truthy-bool]
                blend(p, x, y, c, t)


def tier(level: float, x: int, y: int, steps: int = 4) -> int:
    """A strength 0..1 as a whole number of steps 0..`steps`; the fraction between two steps is dithered, so a falloff
    is a few flat tones with grained joints between them."""
    v = max(0.0, min(1.0, level)) * steps
    k = int(v)
    return min(steps, k + (1 if stepped(v - k, x, y) else 0))


def overlay_shadow(p: Pix, x0: int, y0: int, x1: int, y1: int, fn, color: Color = SHADOW, alpha: int = 160) -> None:
    """Writes a soft shadow into a mostly transparent layer: `fn(x, y)` gives the strength 0..1, which becomes up to four
    translucent steps of `alpha` in all, dithered at the joints, so the shade falls off in grains and never as a box."""
    for y in range(max(0, y0), min(p.h, y1)):
        for x in range(max(0, x0), min(p.w, x1)):
            if p.get(x, y)[3]:
                continue
            k = tier(fn(x, y), x, y)
            if k:
                p.px(x, y, (*color[:3], alpha * k // 4))


def ellipse_shadow(cx: float, cy: float, rx: float, ry: float, strength: float):
    """A strength function for a contact shadow: strongest at the middle of an ellipse, falling to nothing at its rim."""
    def fn(x: int, y: int) -> float:
        d = math.hypot((x - cx) / rx, (y - cy) / ry)
        return strength * (1 - d) ** 0.8 if d < 1 else 0.0
    return fn


def barrel(p: Pix, cx: int, foot_y: int, half: int, height: int, wood: Ramp, tap: bool = True) -> None:
    """An upright cask seen from above the horizon line: staves of equal angle (narrow at the sides, curving with the
    belly), iron hoops that are arcs of ellipses, a rim that is a curve, a brass tap. The foot of the cask is at
    `foot_y` (the front of its base circle); the top is meant to be hidden or cropped by what stands in front."""
    vy = VP[1]
    top = foot_y - height
    belly = 6
    rbot = half - belly

    def hw(y: float) -> float:
        t = (y - top) / height
        return rbot + belly * (1 - (2 * t - 1) ** 2)

    def ry_at(y: float, radius: float) -> int:
        return max(2, round(radius * (y - vy) / ROUND))

    ry_b = ry_at(foot_y, rbot)
    staves = 11
    pattern = (2, 3, 2, 1, 3, 2)
    for y in range(top, foot_y + ry_b + 1):
        w = hw(min(y, foot_y))
        for dx in range(-half, half + 1):
            if y <= foot_y:
                if abs(dx) >= w:
                    continue
            else:                                              # below the base circle's centre: the rim curves down
                if abs(dx) >= rbot or y > foot_y + ry_b * math.sqrt(1 - (dx / rbot) ** 2):
                    continue
            wy = w if y <= foot_y else rbot
            theta = math.asin(max(-1.0, min(1.0, dx / wy)))
            u = (theta + math.pi / 2) / math.pi                # 0 at the lit side, 1 at the shaded one
            k = min(staves - 1, int(u * staves))
            tone = pattern[k % len(pattern)] + (1 if u < 0.28 else 0) - (1 if u > 0.66 else 0) - (1 if u > 0.86 else 0)
            tone = max(0, min(len(wood) - 1, tone))
            edge = k > 0 and u * staves - k < 0.1
            p.px(cx + dx, y, wood[0] if edge else wood[tone])
    # the rim (chime) of the base: a lit curve just inside the lower edge
    for dx in range(-rbot + 1, rbot):
        yy = foot_y + round(ry_b * math.sqrt(1 - (dx / rbot) ** 2))
        p.px(cx + dx, yy, wood[0])
        p.px(cx + dx, yy - 1, wood[4] if dx < rbot // 3 else wood[2])
    for frac in (0.14, 0.36, 0.7, 0.9):                        # hoops: ribbons that follow the curve of the barrel
        hy = round(top + height * frac)
        wid = hw(hy)
        ry = ry_at(hy, wid)
        for dx in range(-int(wid) + 1, int(wid)):
            yc = hy + round(ry * math.sqrt(1 - (dx / wid) ** 2))
            u = (dx / wid + 1) / 2
            body = IRON[3] if u < 0.3 else IRON[1] if u > 0.78 else IRON[2]
            p.px(cx + dx, yc, IRON[4] if u < 0.78 else IRON[2])
            p.px(cx + dx, yc + 1, body)
            p.px(cx + dx, yc + 2, body)
            p.px(cx + dx, yc + 3, IRON[0])
            if dx % 14 == 0 and 0.12 < u < 0.85:
                p.px(cx + dx, yc + 1, BRASS[3])
    if tap:
        ty = foot_y - 34
        p.rect(cx + 4, ty, 16, 6, BRASS[2])
        p.hline(cx + 4, ty, 16, BRASS[4])
        p.hline(cx + 4, ty + 5, 16, BRASS[0])
        p.rect(cx + 18, ty - 2, 5, 14, BRASS[3])
        p.vline(cx + 18, ty - 2, 14, BRASS[4])
        p.vline(cx + 22, ty - 2, 14, BRASS[0])
        p.vline(cx + 20, ty + 12, 9, mix(wood[2][:3], SHADOW[:3], 0.5))      # a drip
