"""Hair: a mass shaped to the skull with a hairline, lit like a dome and combed with curved strands.

A style is a handful of numbers (volume above and beside the skull, where the hairline runs, how far the sideburns go)
plus optional extras: the hair that hangs behind the neck, a bun, a ponytail, a braid. `back_hair` is drawn before the
body, `front_hair` after the head, `over_body` after the clothes.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from collections.abc import Callable

from people_kit import HAIRS, Mask, both, blank, grow, minus, oval, poly, union
from people_look import Look
from pface_core import dome, fill, flat, inside, pixels, trace, curve
from pface_head import CX, Geo, geo, half_width, head_mask, skin_ramp
from pix import Pix, Ramp, mix


@dataclass(frozen=True)
class Style:
    vt: int                 # volume above the skull
    vs: int                 # volume beside it
    line: float             # the hairline's height as a share of the face (from the crown)
    sb: int = 3             # sideburn width
    ear: int = 0            # rows below the eye line the side hair runs to (negative: above it)
    slope: float = 0.0      # parting: the hairline falls to the right by this many rows per half-width
    temples: float = 0.0    # extra recession at the temples, in rows


STYLES: dict[str, Style] = {
    "crop": Style(2, 1, 0.15, 2, -4),
    "short": Style(4, 2, 0.18, 3, -3),
    "swept": Style(6, 2, 0.20, 3, -3, -3.0),
    "receding": Style(3, 1, 0.18, 3, -3, 0, 7.0),
    "curly": Style(6, 4, 0.18, 4, 3),
    "mop": Style(6, 3, 0.30, 4, 1),
    "long": Style(5, 3, 0.20, 4, 22, 4.0),
    "bob": Style(5, 4, 0.21, 5, 18, 3.0),
    "bun": Style(4, 2, 0.19, 3, 0, 3.0),
    "ponytail": Style(4, 2, 0.19, 3, 0, 2.0),
    "braid": Style(5, 2, 0.20, 4, 0, 4.0),
    "frizz": Style(8, 6, 0.17, 4, 4),
    "ring": Style(0, 3, 0.55, 3, 0),
}


def virtual_halfwidth(g: Geo, vt: int, vs: int, y: float) -> float:
    """Half the width of the hair mass at row `y`: the skull's dome grown by the volume."""
    top = g.sk - vt
    yc = g.sk + 0.46 * g.H
    if y < top or y > g.chin:
        return 0.0
    hw = g.w / 2 + vs
    if y >= yc:
        return hw
    u = (yc - y) / (yc - top)
    return hw * max(0.0, 1 - u ** 2.5) ** 0.4


def hair_mask(look: Look, g: Geo, style: Style) -> Mask:
    """The hair on the head: the grown dome above the hairline, and the side hair beside the face."""
    m = blank()
    px = m.load()
    assert px is not None
    hw = g.w / 2
    ear_y = g.eye + style.ear
    for y in range(g.sk - style.vt, ear_y + 1):
        vh = virtual_halfwidth(g, style.vt, style.vs, y)
        n = round(vh)
        real = half_width(g, y)
        for x in range(CX - n, CX + n):
            dx = x + 0.5 - CX
            r = min(1.0, abs(dx) / hw)
            line = g.sk + g.H * style.line + style.slope * dx / hw + r ** 3 * 6 - 2.4 * math.sin(r * math.pi * 0.95)
            if style.temples:
                line += style.temples * max(0.0, 1 - abs(dx) / (hw * 0.55)) * -1
                if abs(dx) > hw * 0.45:
                    line += style.temples * 0.8 * min(1.0, (abs(dx) - hw * 0.45) / (hw * 0.4)) * (1 if abs(dx) < hw * 0.9 else 0.3)
            side = abs(dx) >= max(real - style.sb, 0)
            if y < line or side:
                px[x, y] = 255
    return m


def comb(p: Pix, m: Mask, ramp: Ramp, g: Geo, look: Look, n: int = 16, part: int = 3, rim: bool = True) -> None:
    """Strands of hair: curves that fan from the parting down and outward, light on the lit half, dark on the other."""
    rng = random.Random(look.seed * 17 + 3)
    box = m.getbbox()
    if box is None:
        return
    x0, y0, x1, y1 = box
    origin = (CX + part, y0 + 1)
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        ex = CX + side * rng.uniform((x1 - x0) * 0.1, (x1 - x0) * 0.5)
        ey = rng.uniform(y0 + (y1 - y0) * 0.35, y1 - 1)
        mid = (CX + side * (ex - CX) * 0.5 * side * side + side * 0.0 + (ex - CX) * 0.55, y0 + (ey - y0) * 0.1 + rng.uniform(-1, 3))
        mid = (CX + (ex - CX) * 0.8, y0 + (ey - y0) * 0.22)
        pts = curve(origin, mid, (ex, ey), 16)
        col = ramp[3] if (ex < CX) else ramp[1]
        if rng.random() < 0.28:
            col = ramp[4] if ex < CX else ramp[0]
        trace(p, pts, col, m)
    if rim:
        # the lit crown: a short bright arc on the upper left
        for x, y in pixels(m):
            if not inside(m, x - 1, y - 1) and x < CX - 2 and y < y0 + (y1 - y0) * 0.5:
                p.px(x, y, ramp[3])
                if not inside(m, x, y - 1):
                    p.px(x + 1, y, ramp[4]) if inside(m, x + 1, y) else None


def clumps(p: Pix, m: Mask, ramp: Ramp, look: Look, size: int = 5, share: float = 0.9) -> None:
    """Curls: overlapping round locks on a dark ground, each lit on its upper left and shaded on its lower right."""
    rng = random.Random(look.seed * 13 + 1)
    box = m.getbbox()
    if box is None:
        return
    x0, y0, x1, y1 = box
    step = max(3, size - 1)
    centres = []
    for row, y in enumerate(range(y0 - 1, y1 + 2, step)):
        for x in range(x0 - 2, x1 + 2, step):
            centres.append((x + rng.randint(-1, 1) + (step // 2 if row % 2 else 0), y + rng.randint(-1, 1)))
    for cx, cy in sorted(centres, key=lambda c: c[1]):
        if rng.random() > share:
            continue
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                d = dx * dx + dy * dy
                if d > 5 or not inside(m, cx + dx, cy + dy):
                    continue
                lit = (-dx - dy)
                c = ramp[3] if lit >= 2 else ramp[2] if lit >= -1 else ramp[1]
                if dx + dy >= 3:
                    c = ramp[0]
                if (dx, dy) == (-1, -1) and d == 2:
                    c = ramp[4]
                p.px(cx + dx, cy + dy, c)


def tonsure_mask(look: Look, g: Geo) -> Mask:
    """A friar's ring: hair only at the sides and back of the skull."""
    m = blank()
    px = m.load()
    assert px is not None
    ytop = g.sk + round(g.H * 0.28)
    for y in range(ytop, g.eye + 4):
        n = round(half_width(g, y)) + 2
        inner = round(half_width(g, y)) - 5 - (0 if y > g.sk + g.H * 0.4 else 3)
        for x in range(CX - n, CX + n):
            if abs(x + 0.5 - CX) > inner:
                px[x, y] = 255
    return m


def hair_tone(look: Look) -> Ramp:
    return HAIRS[look.hair_col]


# ---------------------------------------------------------------------------------------------- back, cap and over-body


def back_mass(look: Look, g: Geo) -> Mask:
    """Hair that hangs behind the head and shoulders (long, bob, ponytail); empty for the rest."""
    hw = g.w // 2
    style = look.hair
    if style == "long":
        return union(poly([(CX - hw - 5, g.sk + 6), (CX + hw + 5, g.sk + 6), (CX + hw + 15, g.chin + 36), (CX - hw - 15, g.chin + 36)]),
                     oval(CX, g.sk + 14, hw + 6, g.H * 0.4))
    if style == "bob":
        return union(poly([(CX - hw - 5, g.sk + 6), (CX + hw + 5, g.sk + 6), (CX + hw + 5, g.chin + 6), (CX + hw - 2, g.chin + 10),
                           (CX - hw + 2, g.chin + 10), (CX - hw - 5, g.chin + 6)]), oval(CX, g.sk + 14, hw + 6, g.H * 0.4))
    if style == "ponytail":
        return union(poly([(CX + hw - 4, g.sk + 6), (CX + hw + 3, g.eye), (CX + hw + 10, g.chin + 4), (CX + hw + 6, g.chin + 20),
                           (CX + hw + 1, g.chin + 6)]), oval(CX + hw + 4, g.eye - 2, 3, 5))
    if style == "bun":
        return oval(CX, g.sk - 6, 8, 6)
    if style == "frizz":
        return oval(CX, g.sk + g.H * 0.22, hw + 8, g.H * 0.36)
    return blank()


def back_hair(p: Pix, look: Look, g: Geo) -> None:
    if look.hair in ("bald", "ring") or look.hair not in STYLES and look.hair != "bald":
        pass
    m = back_mass(look, g)
    if m.getbbox() is None:
        return
    ramp = hair_tone(look)
    # behind: darker, lit only on the upper left
    fill(p, m, ramp, dome(CX - 4, g.sk + 10, g.w / 2 + 12, g.H * 0.9, flat=0.5), cuts=(0.0, 0.5, 1.0, 1.4), texture=0.12)
    comb(p, m, ramp, g, look, n=12, rim=False)
    if look.hair == "bun":
        # the bun's coil lines
        for i in range(4):
            trace(p, curve((CX - 6, g.sk - 4 + i), (CX, g.sk - 8 + i), (CX + 6, g.sk - 4 + i + 1), 8), ramp[3] if i % 2 else ramp[1], m)


def front_hair(p: Pix, look: Look, g: Geo) -> None:
    """The cap of hair over the skull, with its hairline, sideburns and strands."""
    ramp = hair_tone(look)
    if look.hair == "bald":
        return
    if look.hair == "ring":
        m = tonsure_mask(look, g)
        fill(p, m, ramp, dome(CX - 4, g.sk + 10, g.w / 2 + 3, g.H * 0.5, flat=0.2), cuts=(0.0, 0.45, 0.95, 1.3), texture=0.1)
        comb(p, m, ramp, g, look, n=8, rim=False)
        return
    style = STYLES.get(look.hair, STYLES["short"])
    m = hair_mask(look, g, style)
    cuts = (0.0, 0.42, 0.9, 1.22)
    fill(p, m, ramp, dome(CX - 3, g.sk + 6, g.w / 2 + style.vs, g.H * 0.46, flat=0.2), cuts=cuts, texture=0.12)
    if look.hair in ("curly", "frizz"):
        fill(p, m, ramp, dome(CX - 3, g.sk + 6, g.w / 2 + style.vs, g.H * 0.46, flat=0.2), cuts=(-1, 0.1, 0.9, 1.5))
        clumps(p, m, ramp, look, 5 if look.hair == "curly" else 6)
        # a few fringe curls on the forehead edge
    else:
        comb(p, m, ramp, g, look, n=18 if style.vt > 3 else 12, part=3 if style.slope >= 0 else -3)
    # the hair throws a shadow on the brow: the row under the hairline takes a darker skin tone
    sk = skin_ramp(look)
    head = head_mask(look)
    for x, y in pixels(m):
        if not inside(m, x, y + 1) and inside(head, x, y + 1):
            p.px(x, y + 1, mix(sk[2], sk[1], 0.75))
            if inside(head, x, y + 2) and (x + y) % 2 == 0:
                p.px(x, y + 2, mix(sk[2], sk[1], 0.4))


def over_body(p: Pix, look: Look, g: Geo) -> None:
    """Hair that falls in front of the shoulders: the two front locks of long hair, or a braid over one shoulder."""
    ramp = hair_tone(look)
    hw = g.w // 2
    if look.hair == "long":
        for s in (-1, 1):
            pts = [(CX + s * (hw + 1), g.eye + 6), (CX + s * (hw + 9), g.eye + 6), (CX + s * (hw + 12), g.chin + 34), (CX + s * (hw + 3), g.chin + 38),
                   (CX + s * (hw - 1), g.chin + 20)]
            m = poly(pts)
            fill(p, m, ramp, dome(CX - 4, g.sk + 10, g.w / 2 + 12, g.H * 0.9, flat=0.4), cuts=(0.0, 0.5, 1.0, 1.4), texture=0.1)
            for i in range(4):
                x = CX + s * (hw + 3 + i * 2)
                trace(p, curve((x, g.eye + 8), (x + s, g.chin + 12), (x + s * 2, g.chin + 34), 10), ramp[3] if i % 2 == 0 else ramp[1], m)
            for x, y in pixels(m):
                if not inside(m, x + s, y):
                    p.px(x, y, ramp[0])
    elif look.hair == "braid":
        x0 = CX + hw - 4
        y = g.eye + 12
        for i in range(11):
            ox = round(2 * math.sin(i * 1.4)) + i // 4
            for dx in range(7 - i // 4):
                c = ramp[3] if dx < 2 else ramp[2] if dx < 4 else ramp[1]
                p.px(x0 + ox + dx, y + i * 4, c)
                p.px(x0 + ox + dx, y + i * 4 + 1, c)
                p.px(x0 + ox + dx, y + i * 4 + 2, ramp[1] if dx > 1 else ramp[2])
                p.px(x0 + ox + dx, y + i * 4 + 3, ramp[0])
        p.rect(x0 + 8, y + 40, 5, 3, (150, 50, 50))
