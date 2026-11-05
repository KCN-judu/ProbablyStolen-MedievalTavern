"""Paint and chalk on the undercroft wall: the big antlered-stag sigil, a crossed-out crown, the slogan BREAK OUT, the green
BURN IT DOWN tag, chalk tally marks and a chalk rebel sigil. All strokes are drawn big and thresholded to whole pixels."""

from __future__ import annotations

import math
import random

from PIL import Image

from mnu_wall_kit import (Canvas, Noise, Pt, arc_pts, bayer, cells, empty, grow, hx, inside, letters, minus, poly_mask, shade,
                          stroke_mask, union)

PINK = [hx(c) for c in ("#4e1a3a", "#862c4e", "#c0465e", "#ec6f88", "#ffa6b4")]
ORANGE = [hx(c) for c in ("#4a1c28", "#80322c", "#bc5230", "#e8803c", "#ffb460")]
AMBER = [hx(c) for c in ("#3c1c2a", "#6e3128", "#a85a30", "#d08640", "#f0b868")]
GREEN = [hx(c) for c in ("#1c3426", "#33573a", "#55804a", "#85ad6c", "#b6d296")]
BLUE = [hx(c) for c in ("#1e2342", "#34407a", "#4f60a0", "#7a8cc4", "#b4c0e8")]
CHALK = [hx(c) for c in ("#6c74a8", "#8c94c6", "#aeb6dc")]
DARK = hx("#1a0f1e")


def spray(c: Canvas, mask: Image.Image, rnd: random.Random, ramp, reach: int = 2, density: float = 0.25) -> None:
    """Overspray: a few dithered pixels of the paint just outside the stencilled shape."""
    ins = inside(mask)
    halo = minus(grow(mask, 1, 0), mask)
    for dx, dy in ((-1, -1), (1, 1), (-2, 0), (0, 2), (2, -1), (-1, 2)):
        halo = union(halo, minus(grow(mask, dx, dy), mask))
    for x, y in cells(halo):
        if rnd.random() < density and not ins(x, y):
            c.put(x, y, ramp[2])


def paint_shape(c: Canvas, mask: Image.Image, ramp, shadow: Image.Image | None, tone, rnd: random.Random, rough: Noise,
                gaps: float = 0.2) -> None:
    """Paint on stone: fill by `tone(x, y)` (0..1), lit edge up-left, dark edge down-right, a drop shadow, and dry gaps
    where the rough stone refuses the paint."""
    ins = inside(mask)
    if shadow is not None:
        for x, y in cells(minus(shadow, mask)):
            r, g, b = c.get(x, y)
            c.put(x, y, (round(r * 0.45), round(g * 0.4), round(b * 0.5)))

    def fill(x: int, y: int):
        if rough(x, y) < gaps * 0.9 and rnd.random() < 0.7:
            return None
        v = tone(x, y)
        if not ins(x - 1, y - 1) or not ins(x, y - 1):
            v += 0.3
        elif not ins(x + 1, y + 1) or not ins(x + 1, y):
            v -= 0.3
        return shade(ramp, v, x, y)

    c.paint(mask, fill)


def drips(c: Canvas, mask: Image.Image, rnd: random.Random, ramp, count: int, longest: int, floor: int) -> None:
    """Runs of paint from the bottom edge of a shape: a thin line ending in a bead."""
    ins = inside(mask)
    box = mask.getbbox()
    xs = sorted(rnd.sample(range(box[0] + 4, box[2] - 4), count))
    for x in xs:
        ys = [y for y in range(box[1], box[3]) if ins(x, y)]
        if not ys:
            continue
        y0, ln = max(ys) + 1, rnd.randrange(6, longest)
        for k in range(ln):
            if y0 + k < floor:
                c.put(x, y0 + k, ramp[2] if k < ln - 2 else ramp[3])
        c.put(x, y0 + ln, ramp[3])
        c.put(x + 1, y0 + ln, ramp[2])
        c.put(x, y0 + ln + 1, ramp[2])


def rot(u: float, v: float, cx: float, cy: float, deg: float) -> Pt:
    a = math.radians(deg)
    return cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a)


def stag_sigil(c: Canvas, rnd: random.Random, rough: Noise) -> Image.Image:
    """The big piece: an antlered stag skull thrown up at a slant, orange at the left end and pink at the right, with a
    stencilled extrusion, running drips and overspray. Returns its mask (for the drips of the lettering to avoid)."""
    cx, cy, deg = 452.0, 172.0, -17.0
    k = 1.32

    def R(pts):
        return [rot(u * k, v * k, cx, cy, deg) for u, v in pts]

    beams: list[list[Pt]] = []
    for s in (1, -1):
        beams.append(R([(s * 18, -14), (s * 48, -26), (s * 82, -30), (s * 112, -46)]))
        beams.append(R([(s * 48, -26), (s * 56, -58)]))
        beams.append(R([(s * 80, -30), (s * 90, -64)]))
        beams.append(R([(s * 100, -40), (s * 128, -38)]))
        beams.append(R([(s * 34, -20), (s * 28, -50)]))
    horns = stroke_mask(beams, 6.6)
    skull = poly_mask(R([(-22, -14), (-14, -26), (14, -26), (22, -14), (22, 2), (14, 16), (11, 42), (-11, 42), (-14, 16), (-22, 2)]))
    face = union(horns, skull)
    shadow = union(grow(face, 3, 4), grow(face, 4, 5), grow(face, 2, 3))
    spray(c, face, rnd, PINK, density=0.22)

    def tone(x: int, y: int) -> float:
        u = (x - cx) * math.cos(math.radians(deg)) + (y - cy) * math.sin(math.radians(deg))
        return 0.5 + u / 330 + (rough(x, y) - 0.5) * 0.25

    def pink_or_orange(x: int, y: int) -> float:
        return tone(x, y)

    # left half orange, right half pink: the can was swapped mid-piece
    left = poly_mask([(0, 0), (cx - 4, 0), (cx - 4, 360), (0, 360)])
    right = poly_mask([(cx - 4, 0), (640, 0), (640, 360), (cx - 4, 360)])
    from PIL import ImageChops
    face_l = ImageChops.multiply(face, left)
    face_r = ImageChops.multiply(face, right)
    paint_shape(c, face, ORANGE, shadow, lambda x, y: 0.62 + (rough(x, y) - 0.5) * 0.3, rnd, rough)
    paint_shape(c, face_r, PINK, None, lambda x, y: 0.6 + (rough(x, y) - 0.5) * 0.3 - 0.1 * (y - 130) / 60, rnd, rough)
    # eye sockets and nose, dark
    for ex in (-11, 11):
        eye = poly_mask(R([(ex - 5, -3 if ex < 0 else 3), (ex + 5, 3 if ex < 0 else -3), (ex + 3, 8), (ex - 3, 8)]))
        c.flat(eye, DARK)
    nose = poly_mask(R([(-4, 18), (4, 18), (2, 28), (-2, 28)]))
    c.flat(nose, DARK)
    for tx in (-6, -2, 2, 6):
        c.flat(stroke_mask([R([(tx, 32), (tx, 37)])], 0.6), DARK)
    mk = face
    drips(c, mk, rnd, ORANGE, 5, 22, 296)
    return mk


def crossed_crown(c: Canvas, rnd: random.Random, rough: Noise) -> None:
    """A blue-grey painted crown struck through with a red X: the rebels' joke on the lord of the hall."""
    cx, cy, k = 374.0, 152.0, 1.4
    pts = [(-26, 12), (-28, -16), (-14, -2), (0, -22), (14, -2), (28, -16), (26, 12)]
    crown = poly_mask([(cx + u * k, cy + v * k) for u, v in pts])
    band = poly_mask([(cx - 27 * k, cy + 14 * k), (cx + 27 * k, cy + 14 * k), (cx + 26 * k, cy + 24 * k), (cx - 26 * k, cy + 24 * k)])
    both = union(crown, band)
    spray(c, both, rnd, BLUE, density=0.2)
    paint_shape(c, both, BLUE, grow(both, 2, 3), lambda x, y: 0.5 + (rough(x, y) - 0.5) * 0.3 - 0.3 * (y - cy) / 40, rnd, rough, 0.1)
    for gx, gy in ((-18, 17), (-6, 19), (8, 18), (20, 19)):
        c.put(round(cx + gx * k), round(cy + gy * k), BLUE[4])
        c.put(round(cx + gx * k + 1), round(cy + gy * k), BLUE[3])
        c.put(round(cx + gx * k + 2), round(cy + gy * k + 1), BLUE[4])
    for jx, jy in ((0, -24), (-28, -18), (28, -18)):
        c.flat(poly_mask([(cx + jx * k - 2, cy + jy * k - 2), (cx + jx * k + 2, cy + jy * k - 2), (cx + jx * k + 2, cy + jy * k + 2), (cx + jx * k - 2, cy + jy * k + 2)]), BLUE[4])
    cross = stroke_mask([[(cx - 40, cy - 30), (cx + 44, cy + 44)], [(cx + 42, cy - 32), (cx - 40, cy + 44)]], 2.6)
    paint_shape(c, cross, ORANGE, grow(cross, 1, 2), lambda x, y: 0.7, rnd, rough, 0.05)
    drips(c, cross, rnd, ORANGE, 2, 14, 296)


def slogan(c: Canvas, rnd: random.Random, rough: Noise) -> None:
    """BREAK OUT in fat painted capitals (own letterforms), outlined and dropped-shadowed, climbing a little to the right."""
    lines = letters("BREAK", 438, 240, 30, 16, 3, tilt=-0.03, slant=4, jitter=0.5, seed=4)
    lines2 = letters("OUT", 542, 262, 28, 16, 3, tilt=-0.02, slant=4, jitter=0.5, seed=5)
    for ln, off in ((lines, 0), (lines2, 0)):
        m = stroke_mask(ln, 3.6)
        sh = union(grow(m, 1, 1), grow(m, 2, 2), grow(m, 1, 2), grow(m, 3, 3))
        ol = minus(union(grow(m, 1, 0), grow(m, -1, 0), grow(m, 0, 1), grow(m, 0, -1), grow(m, 1, 1), grow(m, -1, -1)), m)
        spray(c, m, rnd, AMBER, density=0.12)
        for x, y in cells(minus(sh, m)):
            r, g, b = c.get(x, y)
            c.put(x, y, (round(r * 0.5), round(g * 0.42), round(b * 0.5)))
        c.flat(minus(ol, minus(ol, ol)), hx("#3a1a26"))
        paint_shape(c, m, AMBER, None, lambda x, y: 0.62 + (rough(x, y) - 0.5) * 0.4 - 0.18 * ((y % 30) / 30), rnd, rough, 0.18)
        drips(c, m, rnd, AMBER, 3, 12, 296)


def burn_it_down(c: Canvas, rnd: random.Random, rough: Noise) -> None:
    """A thin, jittery green tag climbing to the right: spray-can handwriting, dry in places."""
    lines = letters("BURN IT DOWN", 542, 236, 21, 6.0, 1.1, tilt=0.0, rise=1.5, slant=2.4, jitter=0.3, seed=9)
    m = stroke_mask(lines, 1.6)
    shadow = grow(m, 1, 1)
    spray(c, m, rnd, GREEN, density=0.1)
    paint_shape(c, m, GREEN, shadow, lambda x, y: 0.62 + (rough(x, y) - 0.5) * 0.4, rnd, rough, 0.3)
    drips(c, m, rnd, GREEN, 2, 9, 296)


def chalk(c: Canvas, rnd: random.Random, rough: Noise) -> None:
    """Chalk on plaster: a ring with a stag's antlers (the rebels' mark), tally marks, and a scratched arrow."""
    def dust(m: Image.Image) -> None:
        for x, y in cells(m):
            if bayer(x + 1, y) < 0.78 and rough(x, y) > 0.12:
                c.put(x, y, CHALK[2] if bayer(x, y + 2) < 0.3 else CHALK[1])
    cx, cy = 292.0, 252.0
    ring = stroke_mask([arc_pts(cx, cy, 11, 11, 0, 360, 28)], 0.9)
    antl = stroke_mask([[(cx - 4, cy - 10), (cx - 7, cy - 17), (cx - 12, cy - 20)], [(cx - 7, cy - 17), (cx - 6, cy - 23)],
                        [(cx + 4, cy - 10), (cx + 7, cy - 17), (cx + 12, cy - 20)], [(cx + 7, cy - 17), (cx + 6, cy - 23)]], 0.9)
    face = stroke_mask([[(cx - 6, cy - 3), (cx - 3, cy - 2)], [(cx + 3, cy - 2), (cx + 6, cy - 3)], [(cx, cy), (cx, cy + 3)],
                        [(cx - 5, cy + 6), (cx - 2, cy + 7), (cx + 2, cy + 7), (cx + 5, cy + 6)]], 0.8)
    dust(union(ring, antl, face))
    # tally marks: groups of four struck through, one per night the hall has held out
    tally = []
    for g in range(3):
        x0 = 262 + g * 14
        for k in range(4):
            tally.append([(x0 + k * 2.6, 276 + rnd.uniform(-0.5, 0.5)), (x0 + k * 2.6 + rnd.uniform(-0.4, 0.4), 288)])
        if g < 2:
            tally.append([(x0 - 2, 286), (x0 + 11, 277)])
    dust(stroke_mask(tally, 0.8))
    arrow = stroke_mask([[(246, 268), (258, 270)], [(254, 266), (258, 270), (253, 273)]], 0.8)
    dust(arrow)
    # scratches in the plaster beside it
    for x0, y0 in ((318, 280), (326, 284)):
        c.flat(stroke_mask([[(x0, y0), (x0 + 4, y0 + 9)]], 0.7), hx("#2c2038"))


def draw_all(c: Canvas) -> None:
    rnd = random.Random(77)
    rough = Noise(3, 41)
    crossed_crown(c, rnd, rough)
    stag_sigil(c, rnd, rough)
    slogan(c, rnd, rough)
    burn_it_down(c, rnd, rough)
    chalk(c, rnd, rough)
