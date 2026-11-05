"""Helpers for the machinery item sprites: lit masks, gears, brass fittings, damage, bottles and boxes.

Every sprite is built from a *mask* (a set of pixels). `shade_mask` fills it with a material ramp, a dark outline on its
own rim and a lit/shaded second ring, so the silhouette stays inside the footprint the game gives the picture.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from palette import BRASS, IRON, LEATHER, LINEN, OAK, PALE_WOOD, PARCHMENT, SHADOW, SOOT, STONE, WOOD
from pix import Color, Pix, Ramp, mix, rgb

Mask = set[tuple[int, int]]
RUST: tuple[Color, Color, Color] = (rgb("#5e2f1a"), rgb("#8a4a22"), rgb("#b0652c"))
ASH: Color = rgb("#3a3036")


# ---------------------------------------------------------------------------------------------- masks


def rects(*boxes: tuple[int, int, int, int]) -> Mask:
    """Union of rectangles given as (x0, y0, x1, y1), both ends included."""
    return {(x, y) for x0, y0, x1, y1 in boxes for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def ellipse_mask(cx: float, cy: float, rx: float, ry: float) -> Mask:
    out: Mask = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / (rx + 0.3)) ** 2 + ((y - cy) / (ry + 0.3)) ** 2 <= 1:
                out.add((x, y))
    return out


def round_right(mask: Mask, depth: int = 3) -> Mask:
    """Rounds the right-hand corners of each vertical run of the right edge, as on a cylinder end."""
    out = set(mask)
    edge = sorted((x, y) for x, y in mask if (x + 1, y) not in mask)
    runs: list[list[tuple[int, int]]] = []
    for x, y in edge:
        if runs and runs[-1][-1] == (x, y - 1):
            runs[-1].append((x, y))
        else:
            runs.append([(x, y)])
    for run in runs:
        if len(run) < 2 * depth:
            continue
        for k in range(depth):
            for end in (run[k], run[-1 - k]):
                for d in range(depth - k):
                    out.discard((end[0] - d, end[1]))
    return out


def rim(mask: Mask) -> Mask:
    return {(x, y) for x, y in mask if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def shade_mask(p: Pix, mask: Mask, ramp: Ramp, grain: float = 0.0, outline: Color = SHADOW, base: int = 2) -> None:
    """Fills a mask: dark rim, lit upper-left ring, shaded lower-right ring, optional horizontal grain streaks."""
    edge = rim(mask)
    for x, y in mask:
        p.px(x, y, ramp[base])
    if grain:
        for _ in range(round(len(mask) * grain)):
            x, y = p.rng.choice(sorted(mask))
            for k in range(p.rng.randrange(2, 6)):
                if (x + k, y) in mask and (x + k, y) not in edge:
                    p.px(x + k, y, ramp[max(0, base - 1)] if p.rng.random() < 0.7 else ramp[min(len(ramp) - 1, base + 1)])
    for x, y in mask:
        if (x, y) in edge:
            continue
        if (x, y - 1) in edge or (x - 1, y) in edge:
            p.px(x, y, ramp[min(len(ramp) - 1, base + 1)])
        elif (x, y + 1) in edge or (x + 1, y) in edge:
            p.px(x, y, ramp[max(0, base - 1)])
    for x, y in edge:
        p.px(x, y, outline)


# ---------------------------------------------------------------------------------------------- fittings


def gear(p: Pix, cx: int, cy: int, r: int, ramp: Ramp = BRASS, teeth: int = 8, hole: bool = True) -> None:
    """A cog: toothed rim, lit upper-left, dark hub hole. r >= 2."""
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= (r - 0.3) ** 2:
                lit = (x - cx) + (y - cy) < -r * 0.4
                dark = (x - cx) + (y - cy) > r * 0.5
                p.px(x, y, ramp[3] if lit else ramp[1] if dark else ramp[2])
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1))[: max(4, teeth)]
    for i, (dx, dy) in enumerate(dirs):
        if teeth < 8 and i >= 4:
            break
        x, y = cx + dx * (r), cy + dy * (r)
        if dx and dy:
            x, y = cx + dx * max(1, round(r * 0.8)) , cy + dy * max(1, round(r * 0.8))
        p.px(x, y, ramp[3] if dx + dy < 0 else ramp[1])
    if hole and r >= 3:
        p.px(cx, cy, ramp[0])
    elif r >= 2:
        p.px(cx, cy, ramp[0])
    if r >= 3:
        p.px(cx - 1, cy - r + 1, ramp[4])


def plate(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = BRASS, rivets: bool = True) -> None:
    p.rect(x, y, w, h, ramp[2])
    p.hline(x, y, w, ramp[3])
    p.vline(x, y, h, ramp[3])
    p.hline(x, y + h - 1, w, ramp[1])
    p.vline(x + w - 1, y, h, ramp[1])
    if rivets and w >= 5 and h >= 5:
        for rx, ry in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
            p.px(rx, ry, ramp[4])


def pipe(p: Pix, x: int, y: int, length: int, vertical: bool = False, ramp: Ramp = BRASS, thick: int = 3) -> None:
    """A tube with a lit top (or left) and a shaded underside, banded at its ends."""
    for i in range(length):
        for t in range(thick):
            c = ramp[4] if t == 0 and thick > 2 else ramp[3] if t == 0 else ramp[1] if t == thick - 1 else ramp[2]
            if i in (0, length - 1):
                c = ramp[1] if t else ramp[2]
            (p.px(x + t, y + i, c) if vertical else p.px(x + i, y + t, c))


def dial(p: Pix, cx: int, cy: int, r: int = 3) -> None:
    p.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, BRASS[2])
    p.ellipse(cx - r + 1, cy - r + 1, 2 * r - 1, 2 * r - 1, PARCHMENT[3])
    p.line(cx, cy, cx + r - 2, cy - r + 2, SHADOW)
    p.px(cx - r, cy - 1, BRASS[4])
    p.px(cx, cy, IRON[1])


def spring(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = IRON) -> None:
    """Coiled spring drawn as a vertical zigzag."""
    for i in range(h):
        off = (i % 4)
        xx = x + (off if off < 3 else 1) % w
        p.px(xx, y + i, ramp[4] if i % 4 == 0 else ramp[3])
        p.px(min(x + w - 1, xx + 1), y + i, ramp[1])


def valve(p: Pix, cx: int, cy: int, r: int = 2) -> None:
    p.hline(cx - r, cy, 2 * r + 1, IRON[3])
    p.vline(cx, cy - r, 2 * r + 1, IRON[3])
    p.px(cx, cy, BRASS[3])
    p.px(cx - r, cy, BRASS[4])
    p.px(cx + r, cy, IRON[1])


def cogbox(p: Pix, x: int, y: int, w: int, h: int) -> None:
    """A small iron block with brass pins, the stand-in for a chip."""
    p.rect(x, y, w, h, IRON[1])
    p.hline(x, y, w, IRON[3])
    p.vline(x, y, h, IRON[2])
    p.px(x + 1, y + 1, BRASS[3])
    for i in range(1, w - 1, 2):
        p.px(x + i, y - 1, BRASS[2])
        p.px(x + i, y + h, BRASS[1])


def crack(p: Pix, x: int, y: int, length: int, mask: Mask, dx: int = 1) -> None:
    """A jagged dark crack walking down-right (or down-left)."""
    for _ in range(length):
        if (x, y) in mask:
            p.px(x, y, SHADOW)
        y += 1
        if p.rng.random() < 0.55:
            x += dx
        if (x, y) in mask and p.rng.random() < 0.3:
            p.px(x + 1, y, OAK[3])


def rust(p: Pix, mask: Mask, share: float = 0.06) -> None:
    pts = sorted(mask)
    for _ in range(round(len(pts) * share)):
        x, y = p.rng.choice(pts)
        p.px(x, y, p.rng.choice(RUST))


def soot(p: Pix, mask: Mask, share: float = 0.2) -> None:
    for x, y in sorted(mask):
        if (x * 7 + y * 13 + p.rng.randrange(4)) % 5 == 0 and p.rng.random() < share * 2:
            p.px(x, y, SOOT[p.rng.randrange(3)])


def scatter(p: Pix, pts: Iterable[tuple[int, int]], colors: Sequence[Color]) -> None:
    for x, y in pts:
        p.px(x, y, colors[(x + y) % len(colors)])


# ---------------------------------------------------------------------------------------------- generic bodies


def cylinder(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, round_top: bool = True, round_bot: bool = True) -> Mask:
    """A vertical cylinder (bottle, roll, jar): light from the left; rounded ends if asked. Returns its mask."""
    m = rects((x, y, x + w - 1, y + h - 1))
    if round_top:
        for c in ((x, y), (x + w - 1, y)):
            m.discard(c)
    if round_bot:
        for c in ((x, y + h - 1), (x + w - 1, y + h - 1)):
            m.discard(c)
    shade_mask(p, m, ramp, base=2)
    for xx in range(x + 1, x + w - 1):
        k = (xx - x) / max(1, w - 1)
        tone = 3 if k < 0.34 else 2 if k < 0.66 else 1
        for yy in range(y + 1, y + h - 1):
            if (xx, yy) in m and (xx, yy) not in rim(m):
                p.px(xx, yy, ramp[tone])
    if w >= 4:
        for yy in range(y + 2, y + h - 2):
            p.px(x + 1, yy, ramp[min(len(ramp) - 1, 4)])
    return m


def sealed_label(p: Pix, x: int, y: int, w: int, h: int, accent: Color = rgb("#a13a38")) -> None:
    p.rect(x, y, w, h, PARCHMENT[3])
    p.hline(x, y, w, PARCHMENT[4])
    p.hline(x, y + h - 1, w, PARCHMENT[1])
    if h >= 5:
        p.hline(x, y + h // 2, w, accent)
    p.frame(x - 1, y - 1, w + 2, h + 2, SHADOW)


def wood_board(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = WOOD, vertical: bool = False) -> None:
    """A plain framed board with grain, lit upper-left, outlined."""
    m = rects((x, y, x + w - 1, y + h - 1))
    shade_mask(p, m, ramp, grain=0.18)


def lerp_ramp(a: Ramp, b: Ramp, t: float) -> list[Color]:
    return [mix(x, y, t) for x, y in zip(a, b, strict=False)]


__all__ = [n for n in dir() if not n.startswith("_")]
