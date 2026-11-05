"""Materials: boards, beams, masonry, plaster and ironwork, drawn into a rectangle of a `Pix`.

Each function paints a rectangle in one material and uses the canvas's seeded random source for grain, knots and
cracks, so a drawing is the same every time it is built. Light comes from the upper left: edges facing it are lighter,
edges facing away are darker, and a joint is the darkest tone of the ramp.
"""

from __future__ import annotations

from palette import BRASS, IRON, OAK, PLASTER, SOOT, STONE, WOOD
from pix import Color, Pix, Ramp, mix


def planks(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = WOOD, plank: int = 12, vertical: bool = False,
           nails: bool = True) -> None:
    """Boards side by side: horizontal ones stack down the rectangle, vertical ones run across it.

    Every board has its own tone, a lit edge and a shaded edge, long grain streaks, now and then a knot, and butt joints
    with a nail at each end."""
    rng = p.rng
    along, across = (h, w) if vertical else (w, h)       # the board's length axis, and the axis boards are stacked on

    def put(a: int, b: int, c: Color) -> None:
        # a runs along a board, b across the stack; nothing is drawn outside the rectangle
        if not (0 <= a < along and 0 <= b < across):
            return
        if vertical:
            p.px(x + b, y + a, c)
        else:
            p.px(x + a, y + b, c)

    b0 = 0
    while b0 < across:
        thick = min(plank + rng.randrange(-2, 3), across - b0)
        tone = rng.choice((1, 2, 2, 3, 3))
        base, lit, shade = ramp[tone], ramp[min(len(ramp) - 1, tone + 1)], ramp[max(0, tone - 1)]
        for b in range(b0, b0 + thick):
            for a in range(along):
                put(a, b, base)
        for a in range(along):
            put(a, b0, lit)                                   # the edge that faces the light
            put(a, b0 + thick - 1, ramp[0])                   # the joint between boards
            if thick > 3:
                put(a, b0 + thick - 2, shade)
        for _ in range(max(2, along * thick // 90)):          # grain: long streaks along the board
            a, b, n = rng.randrange(along), b0 + 1 + rng.randrange(max(1, thick - 3)), rng.randrange(8, 40)
            c = shade if rng.random() < 0.7 else lit
            for k in range(n):
                put(a + k, b, c)
        if along > 40 and thick > 6 and rng.random() < 0.45:  # a knot
            a, b = 6 + rng.randrange(along - 12), b0 + 2 + rng.randrange(max(1, thick - 5))
            for da, db, c in ((0, 0, ramp[0]), (1, 0, shade), (-1, 0, shade), (0, 1, shade), (0, -1, lit), (2, 0, shade)):
                put(a + da, b + db, c)
        a = rng.randrange(20, 60)                             # butt joints, staggered from board to board
        while a < along - 4:
            for b in range(b0, b0 + thick):
                put(a, b, ramp[0])
                put(a + 1, b, lit)
            if nails and thick > 5:
                put(a - 2, b0 + thick // 2, ramp[4])
                put(a + 3, b0 + thick // 2, ramp[4])
            a += rng.randrange(60, 140)
        b0 += thick


def beam(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = OAK, vertical: bool | None = None) -> None:
    """One heavy timber: lit on its upper-left edges, with grain along its length and a few shallow checks (splits)."""
    vertical = h > w if vertical is None else vertical
    p.rect(x, y, w, h, ramp[2])
    p.hline(x, y, w, ramp[3])
    p.vline(x, y, h, ramp[3])
    p.hline(x, y + h - 1, w, ramp[0])
    p.vline(x + w - 1, y, h, ramp[0])
    p.hline(x + 1, y + h - 2, w - 2, ramp[1])
    p.vline(x + w - 2, y + 1, h - 2, ramp[1])
    rng = p.rng
    length = h if vertical else w
    thick = w if vertical else h
    for _ in range(max(2, length * thick // 140)):
        a, b, n = rng.randrange(length), 2 + rng.randrange(max(1, thick - 4)), rng.randrange(6, 30)
        c = ramp[1] if rng.random() < 0.7 else ramp[3]
        for k in range(min(n, length - a)):
            if vertical:
                p.px(x + b, y + a + k, c)
            else:
                p.px(x + a + k, y + b, c)


def masonry(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = STONE, course: int = 11, moss: Ramp | None = None) -> None:
    """Rough stone in courses: each course is a little taller or shorter, joints are staggered, and every stone is
    lit on top and shaded below."""
    rng = p.rng
    p.rect(x, y, w, h, ramp[0])                              # mortar shows in the joints
    yy = y
    while yy < y + h:
        ch = min(course + rng.randrange(-2, 3), y + h - yy)
        xx = x - rng.randrange(0, 14)
        while xx < x + w:
            sw = rng.randrange(14, 30)
            x0, x1 = max(x, xx + 1), min(x + w, xx + sw)
            if x1 > x0:
                tone = rng.choice((1, 2, 2, 3))
                base = ramp[tone]
                p.rect(x0, yy + 1, x1 - x0, ch - 1, base)
                p.hline(x0, yy + 1, x1 - x0, ramp[min(4, tone + 1)])
                p.hline(x0, yy + ch - 1, x1 - x0, ramp[max(0, tone - 1)])
                p.vline(x1 - 1, yy + 1, ch - 1, ramp[max(0, tone - 1)])
                p.speckle(x0, yy + 2, x1 - x0, max(1, ch - 3), (ramp[max(0, tone - 1)], ramp[min(4, tone + 1)]), 0.06)
                if moss is not None and rng.random() < 0.12:
                    p.speckle(x0, yy + ch // 2, x1 - x0, max(1, ch // 2), (moss[1], moss[2]), 0.3)
            xx += sw
        yy += ch


def plaster(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp = PLASTER, stains: bool = True) -> None:
    """Limewash that has seen smoke: blotches of lighter and darker tone, hairline cracks, and soot creeping up."""
    rng = p.rng
    p.rect(x, y, w, h, ramp[2])
    for _ in range(max(3, w * h // 900)):
        bx, by = x + rng.randrange(w), y + rng.randrange(h)
        bw, bh = min(rng.randrange(14, 48), x + w - bx), min(rng.randrange(8, 26), y + h - by)
        p.dither(bx, by, bw, bh, mix(ramp[2][:3], (ramp[1] if rng.random() < 0.55 else ramp[3])[:3], 0.5), 0.4)
    p.speckle(x, y, w, h, (ramp[1], ramp[3]), 0.025)
    for _ in range(max(1, w * h // 14000)):                  # cracks
        cx, cy = x + rng.randrange(w), y + rng.randrange(h)
        for _ in range(rng.randrange(8, 26)):
            p.px(cx, cy, ramp[0])
            cx += rng.choice((-1, 0, 0, 1))
            cy += rng.choice((0, 1, 1))
    if stains:
        p.gradient(x, y + h * 3 // 4, w, h - h * 3 // 4, ramp[2], ramp[0], 5)
        p.dither(x, y + h * 3 // 4, w, h - h * 3 // 4, SOOT[1], 0.3)


def iron_strap(p: Pix, x: int, y: int, w: int, h: int, rivets: bool = True) -> None:
    """A flat band of iron with a lit top edge and rivet heads along it."""
    p.rect(x, y, w, h, IRON[2])
    p.hline(x, y, w, IRON[4])
    p.hline(x, y + h - 1, w, IRON[0])
    if h > 5:
        p.hline(x, y + 1, w, IRON[3])
    if rivets:
        step = 9
        for xx in range(x + 4, x + w - 3, step):
            p.px(xx, y + h // 2, BRASS[3])
            p.px(xx + 1, y + h // 2 + 1, IRON[0])


def vertical_strap(p: Pix, x: int, y: int, w: int, h: int, rivets: bool = True) -> None:
    p.rect(x, y, w, h, IRON[2])
    p.vline(x, y, h, IRON[4])
    p.vline(x + w - 1, y, h, IRON[0])
    if rivets:
        for yy in range(y + 4, y + h - 3, 9):
            p.px(x + w // 2, yy, BRASS[3])
            p.px(x + w // 2 + 1, yy + 1, IRON[0])


def shadow_under(p: Pix, x: int, y: int, w: int, h: int, depth: int = 6) -> None:
    """The dark that gathers under an edge: dithered bands that fade over `depth` rows."""
    for i in range(depth):
        p.dither(x, y + i, w, 1, SOOT[0], 0.9 - i * (0.9 / depth))


def tone(c: Color, amount: float) -> Color:
    """A colour lightened (amount > 0) or darkened (amount < 0)."""
    return mix(c[:3], (255, 255, 255) if amount > 0 else (0, 0, 0), abs(amount))
