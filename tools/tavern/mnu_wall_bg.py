"""The undercroft itself: ashlar vault wall, plaster with brick showing through, roof openings and their light shafts,
leaded windows over a dusk town, oak beams and the diagonal brace, flagstone floor with reflections."""

from __future__ import annotations

import math
import random

from mnu_wall_kit import (empty, BAYER, Canvas, H, Noise, Pt, W, bayer, cells, hx, inside, lerp, minus, poly_mask, shade, stroke_mask,
                          union, grow)

# Violet-brown stone in shade, the same stone lit orange by the dusk coming through the roof openings.
COOL = [hx(c) for c in ("#150f20", "#221a31", "#332845", "#483a5a", "#5f4f6e", "#7a6a84", "#9a8a98")]
WARM = [hx(c) for c in ("#2a1527", "#46232d", "#693630", "#8e4c3a", "#b86a42", "#dc9050", "#f4bc6c")]
BRICK_C = [hx(c) for c in ("#1f1220", "#33192a", "#4d2230", "#6a3036", "#85413c")]
BRICK_W = [hx(c) for c in ("#3a1a26", "#5c2a2e", "#843a34", "#a85240", "#cc7248")]
OAK_R = [hx(c) for c in ("#140c14", "#24151a", "#38221f", "#4f3228", "#6c4833", "#8a6040")]
SKY = [hx(c) for c in ("#7a2a38", "#a63a3c", "#cf5a3e", "#ee8446", "#ffb25c", "#ffdc90")]
DUSK = [hx(c) for c in ("#2c1a38", "#4c2646", "#7e3450", "#b24e56", "#dc7a66", "#f4a67c")]
IRON_R = [hx(c) for c in ("#0f0b14", "#1b1520", "#2d2532", "#463d49", "#6a5f68")]
MORTAR = hx("#6a5870")

SILL_Y = 203          # bottom of the leaded windows
FLOOR_Y = 308         # where wall meets floor
TRUSS = ((165.0, 48.0), (535.0, 205.0))
OCULUS_1 = [(235, 0), (380, 0), (350, 23), (225, 13)]
OCULUS_2 = [(500, 0), (640, 0), (576, 50), (462, 33)]
WIN_L = [(0, 92), (232, 100), (327, SILL_Y), (0, SILL_Y)]
WIN_R = [(372, 104), (640, 118), (640, 165), (535, SILL_Y), (372, 138)]
# (x at top, x at far end, y top, slope in px of x per px of y) of the two shafts of dusk light
SHAFTS = ((238, 372, 14, -0.17), (480, 640, 36, -0.15))


def brick_here(b, x: int, y: int) -> bool:
    return b.mat[y][x] == 1


def smooth(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def truss_s(x: float, y: float) -> tuple[float, float]:
    """(distance across, distance along) of a point relative to the diagonal brace."""
    (x0, y0), (x1, y1) = TRUSS
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    return ((x - x0) * -dy + (y - y0) * dx) / ln, ((x - x0) * dx + (y - y0) * dy) / ln


def shaft_light(x: int, y: int, wall: bool = True) -> float:
    """How much dusk light a point gets from the roof openings (0 to 1); on the wall the pool ends in a rounded foot."""
    best = 0.0
    for xa, xb, yt, s in SHAFTS:
        if y < yt:
            continue
        xs = x - s * (y - yt)
        fr = (xs - xa) / (xb - xa)
        if not 0 < fr < 1:
            continue
        edge = smooth(min(fr, 1 - fr) * 9)
        fall = 1 - 0.62 * min(1.0, (y - yt) / 330)
        if wall:
            foot = 262 + 18 * math.sqrt(max(0.0, 1 - ((fr - 0.5) * 2) ** 2)) * 0.0
            cap = smooth((foot - y) / 34 + 0.15 * (1 - abs(fr - 0.5) * 2))
            best = max(best, edge * fall * cap)
        else:
            best = max(best, edge * fall * 0.85)
    return best


def tri(rnd: random.Random, cx: float, cy: float, rx: float, ry: float, n: int, jag: float) -> list[Pt]:
    """A ragged blob: the outline of a patch of fallen plaster."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + rnd.uniform(-jag, jag)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return pts


class Backdrop:
    def __init__(self) -> None:
        self.c = Canvas(11)
        self.rnd = self.c.rnd
        self.n1, self.n2, self.n3 = Noise(26, 3), Noise(9, 4), Noise(4, 5)
        self.grain = Noise(10, 6, 4.0, 0.22)
        self.V = [[0.4] * W for _ in range(H)]
        self.mat = [[0] * W for _ in range(H)]       # 0 stone or plaster, 1 brick
        self.peel_mask = empty()
        self.rust = [[0.0] * W for _ in range(H)]

    # ------------------------------------------------------------------ wall surfaces
    def ashlar(self, y0: int, y1: int, course: int, base: float, k: float = 1.0) -> None:
        rnd, V = self.rnd, self.V
        y = y0
        while y < y1:
            h = course + rnd.choice((-1, 0, 0, 1))
            x = -rnd.randrange(34)
            while x < W:
                w = rnd.randrange(24, 44)
                tone = base + rnd.uniform(-0.07, 0.07)
                for yy in range(y, min(y + h, y1)):
                    for xx in range(max(x, 0), min(x + w, W)):
                        v = tone + (self.n2(xx, yy) - 0.5) * 0.16 + (self.n3(xx, yy) - 0.5) * 0.07
                        if yy == y:
                            v += 0.13 * k
                        elif yy == y + h - 1:
                            v -= 0.22 * k
                        if xx == x:
                            v += 0.07 * k
                        elif xx == x + w - 1:
                            v -= 0.2 * k
                        V[yy][xx] = base + (v - base) * (1 if k >= 1 else 0.6 + 0.4 * k)
                x += w
            y += h
        for _ in range(int((y1 - y0) * W * 0.012)):
            xx, yy = rnd.randrange(W), rnd.randrange(y0, y1)
            V[yy][xx] -= 0.16

    def plaster(self) -> None:
        V = self.V
        for y in range(SILL_Y, FLOOR_Y):
            for x in range(W):
                v = 0.6 + (self.n1(x, y) - 0.5) * 0.30 + (self.n2(x, y) - 0.5) * 0.14 + (self.n3(x, y) - 0.5) * 0.05
                damp = smooth((y - 262 + (self.n2(x, y) - 0.5) * 30) / 36)
                V[y][x] = (V[y][x] - 0.5) * 0.7 + v - 0.24 * damp
        # the plinth: a course of dressed stone along the foot of the wall
        for y in range(297, FLOOR_Y):
            for x in range(W):
                k = (x // 38 + (y > 302)) % 3
                v = 0.30 + 0.03 * k + (self.n3(x, y) - 0.5) * 0.1
                if y == 297:
                    v += 0.16
                if y == 302:
                    v -= 0.15
                if y == FLOOR_Y - 1:
                    v -= 0.2
                if x % 38 == 0:
                    v -= 0.14
                V[y][x] = v

    def peel(self) -> None:
        """Fallen plaster: brick shows through, with a shadow under the plaster lip and a lit lip."""
        rnd = self.rnd
        patches = [
            [(212, 204), (262, 204), (268, 228), (258, 252), (264, 284), (244, 296), (220, 292), (226, 264), (212, 238)],
            [(302, 232), (326, 228), (330, 252), (318, 268), (304, 258)],
            [(520, 278), (566, 270), (580, 290), (556, 297), (524, 296)],
            [(6, 232), (40, 226), (46, 252), (30, 268), (10, 258)],
            [(150, 252), (172, 248), (178, 270), (160, 280), (146, 270)],
            [(596, 246), (622, 240), (630, 262), (610, 276), (594, 266)],
        ]
        full = empty()
        for pts in patches:
            jag: list[Pt] = []
            for i, (x, y) in enumerate(pts):
                nx, ny = pts[(i + 1) % len(pts)]
                for t in (0.0, 0.33, 0.66):
                    jag.append((x + (nx - x) * t + rnd.uniform(-3, 3), y + (ny - y) * t + rnd.uniform(-3, 3)))
            full = union(full, poly_mask(jag))
        # hanging flaps of plaster under the sill: teeth pointing down
        for x0, ln in ((213, 15), (221, 24), (230, 11), (239, 20), (248, 14)):
            full = minus(full, poly_mask([(x0 - 2, 203), (x0 + 3, 203), (x0 + 0.5, 203 + ln)]))
        inn = inside(full)
        V, mat = self.V, self.mat
        for x, y in cells(full):
            course, brow = (y - 200) // 6, (y - 200) % 6
            off = (course % 2) * 8
            bx = (x + off) % 17
            v = 0.5 + (self.n3(x, y) - 0.5) * 0.3
            if brow == 5 or bx == 0:
                v = 0.12
            elif brow == 0:
                v += 0.18
            if not inn(x - 1, y) or not inn(x, y - 1):
                v = 0.05          # shadow under the plaster lip
            elif not inn(x - 2, y) or not inn(x, y - 2):
                v *= 0.6
            mat[y][x] = 1
            V[y][x] = v
        # the lit lip of the plaster just outside the hole (light from the upper left)
        for y in range(SILL_Y - 2, FLOOR_Y):
            for x in range(W):
                if not inn(x, y) and (inn(x + 1, y + 1) or inn(x + 1, y)) and 0 < y < H:
                    V[y][x] = min(1.0, V[y][x] + 0.22)
        self.peel_mask = full

    def stains(self) -> None:
        """Rust from the iron and green damp running down the plaster, as dithered streaks of varying length."""
        rnd, V = self.rnd, self.V
        for x0, ln, w in ((304, 70, 3), (318, 44, 2), (329, 88, 2), (276, 36, 2), (196, 58, 2), (405, 40, 2), (596, 52, 3),
                          (530, 38, 2), (70, 40, 2), (133, 30, 2), (466, 34, 2)):
            xs = x0
            for k in range(ln):
                y = SILL_Y + k
                if y >= 296:
                    break
                if rnd.random() < 0.12:
                    xs += rnd.choice((-1, 1)) * (rnd.random() < 0.3)
                for dx in range(w):
                    f = 1 - k / ln
                    if f * (0.5 + rnd.random() * 0.6) > bayer(xs + dx, y) * 0.9:
                        V[y][xs + dx] -= 0.04
                        self.rust[y][xs + dx] = 0.5 + 0.5 * f

    # ------------------------------------------------------------------ colour
    def colour_wall(self) -> None:
        c, V = self.c, self.V
        for y in range(FLOOR_Y):
            ky = 0.5 + 0.5 * smooth(y / 95)
            for x in range(W):
                kx = 0.66 + 0.34 * smooth(x / 340)
                light = shaft_light(x, y)
                v = V[y][x] * ky * kx
                warm = max(light * 0.62, self.rust[y][x] * 0.9)
                if self.rust[y][x] and not brick_here(self, x, y):
                    v += 0.12 * self.rust[y][x]
                v += light * 0.16
                brick = self.mat[y][x]
                if warm > bayer(x + 2, y + 1) * 0.92:
                    c.pa[x, y] = shade(BRICK_W if brick else WARM, v * (1 if brick else 1.0), x, y)
                else:
                    c.pa[x, y] = shade(BRICK_C if brick else COOL, v, x, y)

    # ------------------------------------------------------------------ ceiling and beams
    def ceiling(self) -> None:
        c = self.c
        # vault ribs: pointed ribs bracing the dark ceiling over the left of the hall and over the right
        for x0 in (-56, 66, 392, 510):
            pts = [(x0 + 112 * t / 30, 34 - 40 * math.sin(math.pi * t / 30) ** 0.8) for t in range(31)]
            rib = stroke_mask([pts], 3.4)
            sh = grow(rib, 2, 3)
            c.mixin(minus(sh, rib), hx("#0b0710"), 0.7)
            c.paint(rib, lambda x, y: shade(COOL, 0.30 + (self.n3(x, y) - 0.5) * 0.15, x, y))
            c.edges(rib, COOL[4], COOL[0])

    def oculus(self, pts: list[Pt], flip: bool) -> None:
        c = self.c
        m = poly_mask(pts)
        box = m.getbbox()
        n = self.n1

        def sky(x: int, y: int) -> tuple[int, int, int]:
            v = 0.35 + 0.5 * (n(x * 2, y * 2) * 0.7 + self.n2(x, y) * 0.3) + 0.15 * (x - box[0]) / (box[2] - box[0])
            return shade(SKY, v, x, y)

        c.paint(m, sky)
        # the thick reveal of the opening: its lit lower face, seen from below
        low = minus(poly_mask([(x, y + 6) for x, y in pts]), m)
        c.paint(low, lambda x, y: shade(WARM, 0.55 + (self.n3(x, y) - 0.5) * 0.3 - 0.1 * ((y - box[3]) / 6 if y > box[3] else 0), x, y))
        c.edges(low, WARM[5], WARM[1], -1, 1)
        # iron grille: bars along the opening and across it, with a lit top edge
        (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = pts
        for k in range(1, 6):
            t = k / 6
            p0 = (ax + (dx - ax) * t * 0 + (bx - ax) * t, ay + (by - ay) * t)
            p1 = (dx + (cx_ - dx) * t, dy + (cy_ - dy) * t)
            bar = stroke_mask([[p0, p1]], 1.2)
            bar = minus(bar, minus(bar, m))
            c.flat(bar, IRON_R[1])
            c.flat(minus(grow(bar, -1, 0), bar), IRON_R[3])
        for k in (0.34, 0.68):
            p0 = (ax + (dx - ax) * k, ay + (dy - ay) * k)
            p1 = (bx + (cx_ - bx) * k, by + (cy_ - by) * k)
            bar = stroke_mask([[p0, p1]], 1.4)
            bar = minus(bar, minus(bar, m))
            c.flat(bar, IRON_R[1])
            c.flat(minus(grow(bar, 0, -1), bar), IRON_R[3])
        # oak frame
        frame = minus(stroke_mask([pts], 2.4, closed=True), grow(minus(m, m), 0, 0))
        c.paint(frame, lambda x, y: shade(OAK_R, 0.45 + (self.n3(x, y) - 0.5) * 0.3, x, y))
        c.edges(frame, OAK_R[5], OAK_R[0])

    def slits(self) -> None:
        """High arrow slits: a narrow bright opening in a splayed stone embrasure."""
        c = self.c
        for x0, y0, hh in ((19, 64, 26), (112, 68, 24), (204, 66, 24), (418, 66, 22), (608, 70, 22)):
            splay = poly_mask([(x0 - 5, y0 - 4), (x0 + 6, y0 - 4), (x0 + 6, y0 + hh + 3), (x0 - 5, y0 + hh + 3)])
            c.paint(splay, lambda x, y: shade(COOL, 0.22 + 0.2 * (x - x0 + 5) / 11 * (1 if x < x0 else 0.3), x, y))
            c.edges(splay, COOL[5], COOL[0])
            gap = poly_mask([(x0 - 1, y0), (x0 + 1, y0), (x0 + 1, y0 + hh), (x0 - 1, y0 + hh)])
            c.paint(gap, lambda x, y: shade(SKY, 0.6 + 0.35 * (1 - (y - y0) / hh) - 0.1 * self.n2(x, y), x, y))
            # a cross-bar of the slit
            for x in range(x0 - 1, x0 + 2):
                c.put(x, y0 + hh // 2, IRON_R[1])

    def beam_h(self, y0: int, y1: int, seed: int) -> None:
        """A heavy horizontal oak beam across the whole picture: grain, lit top, shaded underside, iron straps."""
        c = self.c
        m = poly_mask([(0, y0), (W, y0), (W, y1), (0, y1)])
        sh = poly_mask([(0, y1), (W, y1), (W, y1 + 7), (0, y1 + 7)])
        c.mixin(minus(sh, m), hx("#0a0610"), 0.55)
        c.mixin(minus(poly_mask([(0, y1 + 7), (W, y1 + 7), (W, y1 + 12), (0, y1 + 12)]), m), hx("#0a0610"), 0.25)
        g = self.grain

        def wood(x: int, y: int) -> tuple[int, int, int]:
            t = (y - y0) / (y1 - y0)
            v = 0.62 - 0.35 * t ** 1.4 + (g(x, y) - 0.5) * 0.5 + (self.n3(x, y) - 0.5) * 0.12
            if (x * 7 + y * 13 + seed) % 61 == 0:
                v -= 0.2
            if y == y0:
                v = 1.0
            elif y == y1 - 1:
                v = 0.06
            return shade(OAK_R, v, x, y)

        c.paint(m, wood)
        for xs in (60, 150, 247, 340, 428, 520, 610):
            band = poly_mask([(xs, y0), (xs + 6, y0), (xs + 6, y1), (xs, y1)])
            c.paint(band, lambda x, y: shade(IRON_R, 0.55 - 0.45 * (y - y0) / (y1 - y0) + (0.25 if x == xs else 0), x, y))
            for ry in (y0 + 4, y1 - 5):
                c.put(xs + 3, ry, hx("#d0a847"))
                c.put(xs + 3, ry + 1, hx("#6b4c1c"))
        # shaft light brushes the beam where it passes through the dusk shafts
        for x, y in cells(m):
            if shaft_light(x, y) * 0.9 > bayer(x + 1, y) and y < y0 + 4:
                c.put(x, y, shade(WARM, 0.8, x, y))

    def lintel(self, y0: int, y1: int) -> None:
        """The dressed stone band above the windows, with a drip course on its lower edge."""
        c = self.c
        sh = poly_mask([(0, y1), (W, y1), (W, y1 + 6), (0, y1 + 6)])
        c.mixin(sh, hx("#0a0610"), 0.55)
        for y in range(y0, y1):
            for x in range(W):
                v = 0.52 + (self.n2(x, y) - 0.5) * 0.18 - 0.1 * ((y - y0) / (y1 - y0))
                if y == y0:
                    v = 0.9
                elif y == y1 - 1:
                    v = 0.08
                elif x % 41 == 0:
                    v = 0.18
                lit = shaft_light(x, y)
                if lit > bayer(x + 2, y + 1):
                    c.pa[x, y] = shade(WARM, v + 0.15, x, y)
                else:
                    c.pa[x, y] = shade(COOL, v * (0.7 + 0.3 * smooth(x / 340)), x, y)

    def brace(self) -> None:
        """The diagonal timber brace, with a cast shadow on the wall, grain, lit upper edge, and strapped joints."""
        c = self.c
        (x0, y0), (x1, y1) = TRUSS
        wd = 4.6
        pts = [(x0, y0 - wd), (x1 + 40, y1 + 40 * (y1 - y0) / (x1 - x0) - wd)]
        cutline = [(x0, y0), (x1 + 40, y1 + 40 * (y1 - y0) / (x1 - x0))]
        body = stroke_mask([cutline], wd)
        sh = grow(body, 4, 5)
        c.mixin(minus(sh, body), hx("#0a0610"), 0.62)
        c.mixin(minus(grow(body, 7, 9), grow(body, 4, 5)), hx("#0a0610"), 0.25)

        def wood(x: int, y: int) -> tuple[int, int, int]:
            s, a = truss_s(x, y)
            t = (s + wd) / (2 * wd)
            v = 0.7 - 0.55 * t + (self.grain(x, y + int(a * 0.3)) - 0.5) * 0.35 + (self.n3(x, y) - 0.5) * 0.1
            return shade(OAK_R, v, x, y)

        c.paint(body, wood)
        c.edges(body, OAK_R[5], OAK_R[0], 0, -1)
        # iron straps and brass rivets where the brace is jointed
        for a0 in (40, 120, 210, 290, 370):
            def strap(x: int, y: int, a0: int = a0) -> tuple[int, int, int] | None:
                s, a = truss_s(x, y)
                if abs(a - a0) < 3.5 and abs(s) < wd:
                    return shade(IRON_R, 0.5 - 0.3 * (s / wd) + (0.2 if abs(a - a0) > 2.5 else 0), x, y)
                return None
            c.paint(body, strap)
            (dx, dy) = ((x1 - x0), (y1 - y0))
            ln = math.hypot(dx, dy)
            for sgn in (-1.8, 1.8):
                px = x0 + dx / ln * a0 + -dy / ln * sgn * -1
                py = y0 + dy / ln * a0 + dx / ln * sgn * -1
                c.put(round(px), round(py), hx("#d0a847"))
                c.put(round(px) + 1, round(py) + 1, hx("#6b4c1c"))

    # ------------------------------------------------------------------ windows
    def windows(self) -> None:
        c = self.c
        town = self._town()
        for pts, seed in ((WIN_L, 1), (WIN_R, 2)):
            m = poly_mask(pts)
            ins = inside(m)
            box = m.getbbox()
            nz = Noise(18, 20 + seed)
            nz2 = Noise(7, 30 + seed)

            def glass(x: int, y: int, seed: int = seed) -> tuple[int, int, int]:
                u, w = x + 0.62 * y, x - 0.62 * y
                pane = (math.floor(u / 17) * 7 + math.floor(w / 17) * 13 + seed) % 5
                v = 0.20 + 0.3 * (1 - (y - box[1]) / (box[3] - box[1])) + (nz(x, y) - 0.5) * 0.7 + (nz2(x, y) - 0.5) * 0.3
                v += (pane - 2) * 0.03
                if town(x, y):
                    return shade(DUSK, 0.05 + 0.12 * nz2(x, y) + (0.2 if (x * 3 + y * 5) % 23 == 0 else 0), x, y)
                if u % 17 < 1.4 or w % 17 < 1.4:
                    return shade(IRON_R, 0.32 + (0.2 if (u % 17 < 0.4 or w % 17 < 0.4) else 0) - 0.25 * (y - box[1]) / 110, x, y)
                return shade(DUSK, v, x, y)

            c.paint(m, glass)
            # saddle bars and a stone transom
            for yb in (box[1] + 36, box[1] + 74):
                bar = minus(poly_mask([(0, yb), (W, yb), (W, yb + 2), (0, yb + 2)]), minus(m, m))
                bar = Canvas_and(bar, m)
                c.flat(bar, IRON_R[1])
                c.flat(Canvas_and(poly_mask([(0, yb - 1), (W, yb - 1), (W, yb), (0, yb)]), m), IRON_R[3])
            # glow from the glass spilling over the sill and splay
            frame = minus(stroke_mask([pts], 2.6, closed=True), minus(m, m))
            c.paint(frame, lambda x, y: shade(COOL, 0.42 + (self.n3(x, y) - 0.5) * 0.2 + (0.25 if y < box[1] + 8 else 0), x, y))
            c.edges(frame, COOL[6], COOL[0])
        # window sill: a sloped stone ledge with a lit top
        sill = poly_mask([(0, SILL_Y), (327, SILL_Y), (330, SILL_Y + 5), (0, SILL_Y + 5)])
        c.paint(sill, lambda x, y: shade(COOL, 0.62 - 0.4 * (y - SILL_Y) / 5 + (self.n3(x, y) - 0.5) * 0.15, x, y))
        c.edges(sill, COOL[6], COOL[0], 0, -1)
        mullions = [poly_mask([(xm - 2, 93), (xm + 2, 93), (xm + 2, SILL_Y), (xm - 2, SILL_Y)]) for xm in (116, 232 - 0)]
        for mm in mullions[:1]:
            c.paint(mm, lambda x, y: shade(COOL, 0.45 + (self.n3(x, y) - 0.5) * 0.25 - 0.15 * (x - 114) / 4, x, y))
            c.edges(mm, COOL[6], COOL[0])

    def _town(self):
        """Roofs, gables and a spire against the dusk, seen through the lower glass: a street-level cellar light."""
        pts = [(0, 200), (0, 186), (12, 186), (20, 176), (28, 186), (60, 186), (60, 190), (74, 190), (84, 170), (94, 190), (130, 190),
               (136, 184), (150, 184), (156, 190), (176, 190), (183, 156), (187, 190), (205, 190), (214, 180), (226, 180), (232, 190),
               (330, 190), (330, 200)]
        m1 = poly_mask(pts)
        pts2 = [(380, 168), (400, 168), (410, 152), (420, 168), (450, 168), (460, 160), (470, 168), (500, 168), (508, 176), (520, 176),
                (535, 176), (535, 205), (380, 205)]
        m2 = poly_mask(pts2)
        i1, i2 = inside(m1), inside(m2)
        return lambda x, y: i1(x, y) or i2(x, y)


def Canvas_and(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


FLOOR = [hx(c) for c in ("#140e20", "#241a38", "#372b50", "#4d3f68", "#68597f", "#8a7aa0")]
FLOOR_WARM = [hx(c) for c in ("#26121f", "#40202a", "#643230", "#8c4a38", "#b8683f", "#e09452")]


def floor(b: Backdrop) -> None:
    """Wet flagstones in perspective (vanishing point at the middle of the hall), lit where the shafts land."""
    c, rnd = b.c, random.Random(5)
    vx, vy = 320.0, 96.0
    rows = [FLOOR_Y, 319, 333, 351, 380]
    streak = Noise(5, 61, 7.0, 0.22)
    mott = Noise(14, 62)
    for y in range(FLOOR_Y, H):
        r = max(i for i in range(4) if rows[i] <= y)
        f = (y - vy) / (FLOOR_Y - vy)
        for x in range(W):
            x0 = vx + (x - vx) / f + (r % 2) * 23
            col = math.floor(x0 / 46)
            jx = (x0 / 46 - col) * 46 * f
            tone = 0.40 + ((col * 7 + r * 13) % 5) * 0.025 + (mott(x, y) - 0.5) * 0.2
            if y == rows[r]:
                tone = 0.06
            elif y == rows[r] + 1:
                tone += 0.14
            elif jx < 1.2:
                tone = 0.07
            elif jx < 2.4:
                tone += 0.08
            if streak(x, y) > 0.70:
                tone += 0.17
            lit = shaft_light(x, y, False)
            if lit * 1.15 > bayer(x + 2, y + 1):
                c.pa[x, y] = shade(FLOOR_WARM, tone + lit * 0.35, x, y)
            else:
                c.pa[x, y] = shade(FLOOR, tone, x, y)
    # dark seam of wet at the foot of the wall
    for x in range(W):
        for k, t in enumerate((0.8, 0.5, 0.25)):
            if t > bayer(x, FLOOR_Y + k):
                c.put(x, FLOOR_Y + k, FLOOR[0])


def reflect(b: Backdrop, top: int = FLOOR_Y, mirror: int = FLOOR_Y) -> None:
    """Mirror the wall into the wet floor: dim, rippled, broken up by dither so it reads as a sheen and not a copy."""
    c = b.c
    src = c.img.copy().load()
    for y in range(top + 1, H):
        sy = 2 * mirror - y
        if sy < 210:
            continue
        fade = 1 - (y - top) / 75
        ripple = round(1.6 * math.sin(y * 1.3)) if (y // 2) % 2 else 0
        for x in range(W):
            lit = shaft_light(x, y, False)
            strength = (0.42 + 0.5 * lit) * fade
            if strength > bayer(x, y + 1):
                r, g, bl = src[min(max(x + ripple, 0), W - 1), sy]
                base = c.pa[x, y]
                c.pa[x, y] = lerp((r, g, bl), base, 0.40)
