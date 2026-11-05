"""The head: skull and jaw, ears, neck, and a face with sockets, lit eyes, brows, nose, lips, cheek planes and age.

All positions come from one `Geo` (the crown, the face size, the centre), so a broad old man and a slim young woman are
the same code with other numbers. The face is about 44 pixels wide; eyes are 11 wide and four rows tall.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from palette import SHADOW
from people_kit import HAIRS, SKINS, Mask, blank, grow, minus, oval, poly
from people_look import Look
from pface_core import CH, W, dome, fill, flat, hl, inside, pixels, trace, vl
from pix import Color, Pix, Ramp, mix, rgb

CX = 144
SKIN_CUTS = (0.0, 0.36, 0.9, 1.15)
SCLERA: Color = rgb("#ddd2c0")
SCLERA_SH: Color = rgb("#b9a9a0")


@dataclass(frozen=True)
class Geo:
    """Where the parts of one head are."""

    cx: int
    sk: int          # the top row of the skull (the hair stands a little above it)
    chin: int        # the bottom row of the chin
    w: int
    jaw: float
    eye: int         # the row of the eyes' middle
    brow: int        # the row of the brows
    nose: int        # the row under the nose
    mouth: int       # the row of the mouth line
    gap: int         # columns between the centre line and an eye's inner corner

    @property
    def H(self) -> int:
        return self.chin - self.sk


def geo(look: Look) -> Geo:
    sk = look.top + 6
    chin = look.top + look.h
    H = chin - sk
    return Geo(CX, sk, chin, round(look.w * 0.92 / 2) * 2, look.jaw, sk + round(H * 0.50), sk + round(H * 0.50) - 6, sk + round(H * 0.74),
               sk + round(H * 0.855), 3 if look.w < 48 else 4)


def half_width(g: Geo, y: float) -> float:
    """Half the face's width at row `y`: a squarish dome, the cheekbones, the jaw closing round the chin."""
    t = (y - g.sk + 0.5) / (g.H + 1)
    W2 = g.w / 2
    if t <= 0 or t > 1:
        return 0.0
    if t < 0.46:
        u = (0.46 - t) / 0.46
        return W2 * max(0.0, 1 - u ** 2.5) ** (1 / 2.5)
    s = (t - 0.46) / 0.54
    f = 1 - (1 - g.jaw) * s ** 1.45
    if s > 0.84:
        f *= math.sqrt(max(0.0, 1 - ((s - 0.84) / 0.16) ** 2 * 0.78))
    return W2 * f


def head_mask(look: Look) -> Mask:
    """The skull and face as a mask, symmetrical about the centre."""
    g = geo(look)
    m = blank()
    px = m.load()
    assert px is not None
    for y in range(g.sk, g.chin + 1):
        n = round(half_width(g, y))
        for x in range(CX - n, CX + n):
            px[x, y] = 255
    return m


def skin_ramp(look: Look) -> Ramp:
    return SKINS[look.skin]


def lip_colour(sk: Ramp, look: Look) -> tuple[Color, Color]:
    """(lip, lip in shade): the skin turned towards red, more for a woman."""
    red = (176, 70, 82) if not look.male else (150, 66, 70)
    k = 0.7 if look.lips == 2 else 0.55 if look.lips == 1 else 0.4
    if not look.male:
        k += 0.12
    if look.skin >= 5:
        k *= 0.7
    return mix(sk[2], red, k), mix(sk[1], red, k * 0.8)


# ---------------------------------------------------------------------------------------------- neck and ears


def draw_neck(p: Pix, look: Look, g: Geo) -> None:
    """The neck, dark under the jaw, with the line of the trapezius at its foot; laid down before the clothes."""
    sk = skin_ramp(look)
    n = look.neck + (1 if look.build == 2 else 0)
    top = g.chin - 16
    pts = [(CX - n, top), (CX + n, top), (CX + n + 4, g.chin + 34), (CX - n - 4, g.chin + 34)]
    neck = poly(pts)
    fill(p, neck, sk, lambda x, y: 0.62 + 0.5 * (-(x - CX) / (n + 4)), cuts=SKIN_CUTS)
    # the shadow the chin throws on the neck: a dark block that falls away with dither
    head = head_mask(look)
    from people_kit import both, shift
    for drop, c, dens in ((3, sk[0], 1.0), (6, sk[1], 1.0), (8, sk[1], 0.5), (10, sk[1], 0.25)):
        band_m = both(neck, shift(head, 1, drop))
        if dens >= 1.0:
            flat(p, band_m, c)
        else:
            lvl = round(dens * 16)
            from people_kit import bayer, both as b2
            flat(p, b2(band_m, bayer(lvl)), c)
    if look.male:
        # the Adam's apple and the sternomastoid cords
        a = g.chin + 7
        p.px(CX - 1, a, sk[3])
        p.px(CX, a + 1, sk[1])
        vl(p, CX - n + 2, g.chin + 4, 9, sk[1])
        vl(p, CX + n - 3, g.chin + 4, 9, sk[0])


def draw_ears(p: Pix, look: Look, g: Geo) -> None:
    """Ears before the head, so the skull overlaps their inner edge; the hair and headwear may cover them later."""
    sk = skin_ramp(look)
    hw = g.w // 2
    ys = g.eye - 3
    size = 5 + (1 if look.male else 0) + (1 if look.age >= 3 else 0)
    for side in (-1, 1):
        x = CX - hw - 2 if side < 0 else CX + hw - 1
        ear = oval(x + 1, ys + size, 3.4, size + 0.6)
        fill(p, ear, sk, lambda xx, yy, s=side: 0.62 - 0.18 * s + 0.0 * yy)
        # the helix rim and the dark of the canal
        for i in range(size):
            p.px(x + (0 if side < 0 else 2), ys + 2 + i, sk[1])
        p.px(x + (1 if side < 0 else 1), ys + size + 1, sk[0])
        p.px(x + 1, ys + size * 2 - 1, sk[1])


# ---------------------------------------------------------------------------------------------- the face


def face_light(look: Look, g: Geo):
    """The light of the face: a dome with the cheekbones, brow ridge and chin as small bumps."""
    base = dome(CX, g.sk + g.H * 0.52, g.w / 2 * 1.08, g.H / 2, flat=0.15)
    hw = g.w / 2

    def f(x: int, y: int) -> float:
        v = base(x, y)
        dx = (x + 0.5 - CX)
        # cheekbones catch the light (left), hollows under them are dim
        for sgn, k in ((-1, 0.2), (1, 0.12)):
            d = math.hypot((dx - sgn * hw * 0.52) / (hw * 0.28), (y - (g.eye + 5)) / 5)
            if d < 1:
                v += k * (1 - d)
        d2 = math.hypot((dx + hw * 0.5) / (hw * 0.4), (y - (g.eye + 11)) / 5)
        if d2 < 1:
            v -= 0.08 * (1 - d2) * (look.age + 1) / 2
        if y > g.mouth + 4:                      # the chin turns away and catches light
            v += 0.06 + (0.1 if dx < 0 else 0)
        if y < g.sk + g.H * 0.22:                # the forehead turns under
            v -= 0.05
        return v
    return f


def draw_face(p: Pix, look: Look, g: Geo) -> None:
    """Skin, then every feature in the order a painter would block them."""
    sk = skin_ramp(look)
    head = head_mask(look)
    fill(p, head, sk, face_light(look, g), cuts=SKIN_CUTS, texture=0.1)
    rng = random.Random(look.seed * 31 + 7)
    hair = HAIRS[look.hair_col]
    brow_col = hair[1] if look.hair_col not in ("white", "grey", "blond", "straw") else hair[2]
    if look.beard_col:
        brow_col = brow_col
    draw_cheeks(p, look, g, head)
    draw_sockets(p, look, g)
    for side in (-1, 1):
        draw_eye(p, look, g, side)
    draw_brows(p, look, g, brow_col)
    draw_nose(p, look, g)
    draw_mouth(p, look, g)
    draw_age(p, look, g, head, rng)


def draw_cheeks(p: Pix, look: Look, g: Geo, head: Mask) -> None:
    """Blush on the cheekbones (dither of a warm tone) and the shadow of the jaw's lower edge."""
    sk = skin_ramp(look)
    warm = mix(sk[2], (200, 90, 80), 0.28 if look.skin < 5 else 0.12)
    hw = g.w / 2
    pa = p.im.load()
    assert pa is not None
    from pix import BAYER
    for side in (-1, 1):
        cx = CX + side * hw * 0.5
        for y in range(g.eye + 2, g.eye + 11):
            for x in range(int(cx - 7), int(cx + 8)):
                d = math.hypot((x - cx) / 7, (y - (g.eye + 6)) / 4.5)
                if d < 1 and inside(head, x, y) and BAYER[y % 4][x % 4] < (1 - d) * 4:
                    p.px(x, y, warm)
    # the jawline: the lowest edge of the face goes dark where it turns under
    for y in range(g.mouth + 2, g.chin + 1):
        n = round(half_width(g, y))
        if n > 0:
            p.px(CX + n - 1, y, sk[1])
            p.px(CX + n - 2, y, sk[1]) if y > g.mouth + 6 else None
    for x in range(CX - 8, CX + 9):
        if inside(head, x, g.chin):
            p.px(x, g.chin, sk[1])


def draw_sockets(p: Pix, look: Look, g: Geo) -> None:
    """The brow ridge's shadow over the eye, and a soft dark under it, so the eyes sit in the skull."""
    sk = skin_ramp(look)
    for side in (-1, 1):
        for u in range(12):
            x = CX + side * (g.gap + u) - (1 if side < 0 else 0)
            dark = sk[1]
            p.px(x, g.eye - 3, mix(sk[2], sk[1], 0.5)) if u % 2 == 0 else None
            p.px(x, g.eye - 2, dark)
            if 1 <= u <= 10 and (u + (0 if side > 0 else 1)) % 2 == 0:
                p.px(x, g.eye + 2, sk[1])
    # the dim between the eyes at the root of the nose
    for y in range(g.eye - 2, g.eye + 3):
        p.px(CX - 1, y, sk[1] if y % 2 == 0 else sk[2])
        p.px(CX, y, sk[1])


def draw_eye(p: Pix, look: Look, g: Geo, side: int) -> None:
    """One eye: lids, sclera, an iris with a catchlight, lashes; its slope follows the mood."""
    sk = skin_ramp(look)
    iris = rgb(look.eyes)
    lash = mix(sk[0], SHADOW, 0.6)
    lid = sk[0] if look.skin >= 4 else mix(sk[0], SHADOW, 0.25)
    mood = look.mood

    def X(u: int) -> int:
        return CX + g.gap + u if side > 0 else CX - 1 - g.gap - u

    tilt = {"stern": -1, "sad": 1, "worried": 1, "calm": 0, "smile": 0, "grin": 0}.get(mood, 0)
    y = g.eye
    # an eye 11 columns wide (u = 0 at the nose), the outer corner moved by `tilt`
    lift = {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 1, 10: 1}
    for u in range(11):
        top_row = y - 1 + (1 if u in (0, 10) else 0) + (tilt if u >= 8 else 0) * 0
        if mood == "smile":
            top_row += 0
        p.px(X(u), top_row if u not in (0,) else y, lash if u not in (0, 10) else lid)
    # sclera and iris: two full rows between the lids
    ix = 4 if side > 0 else 4          # the iris sits a little towards the nose: 'looking' ahead
    for u in range(1, 10):
        sc = SCLERA if u < 6 else mix(SCLERA, SCLERA_SH, 0.5)
        if u == 1:
            sc = mix(SCLERA, (200, 120, 110), 0.3)   # the tear duct
        p.px(X(u), y, sc)
        p.px(X(u), y + 1, mix(sc, SCLERA_SH, 0.5))
    droop = 1 if mood in ("sad", "worried") else 0
    for u in range(ix, ix + 3):
        p.px(X(u), y, iris if u != ix + 1 else mix(iris, SHADOW, 0.45))
        p.px(X(u), y + 1, mix(iris, SHADOW, 0.25))
    p.px(X(ix + 1), y, mix(iris, SHADOW, 0.7))             # pupil
    p.px(X(ix + 1), y + 1, mix(iris, SHADOW, 0.6))
    p.px(X(ix if side > 0 else ix + 2), y, mix(iris, (250, 240, 220), 0.78))    # catchlight on the lit side
    # a lid shadow on the iris top
    for u in range(ix, ix + 3):
        p.px(X(u), y - 1, lash)
    # lower lid, thin
    for u in range(2, 9):
        p.px(X(u), y + 2, mix(sk[1], sk[2], 0.4) if look.age < 2 else sk[1])
    if droop:
        p.px(X(9), y, sk[1])
        p.px(X(10), y - 1, lid)
    # lashes at the outer corner (a woman's are longer)
    if not look.male:
        p.px(X(10), y - 1, lash)
        p.px(X(9), y - 2, lash)
        p.px(X(8), y - 2, lash)
    # the crease above the lid
    for u in range(2, 9):
        p.px(X(u), y - 2, sk[1] if (u + side) % 2 == 0 or look.age > 1 else sk[2])


def draw_brows(p: Pix, look: Look, g: Geo, col: Color) -> None:
    """Brows: thickness from `Look.brow`, their slope from the mood."""
    thick = 2 if (look.brow >= 1 and look.male) or look.brow == 2 else 1
    inner, outer = {"stern": (2, -1), "sad": (-1, 1), "worried": (-2, 0), "smile": (-1, -1), "grin": (-1, -1)}.get(look.mood, (0, 0))
    y0 = g.brow
    for side in (-1, 1):
        for u in range(0, 12):
            x = CX + side * (g.gap - 1 + u) - (1 if side < 0 else 0)
            k = u / 11
            arch = -1 if 3 <= u <= 7 else 0
            if look.male is False:
                arch = -1 if 4 <= u <= 8 else 0
            y = y0 + round(inner + (outer - inner) * k) + arch + (1 if u > 9 else 0)
            for t in range(thick):
                c = col if t == 0 or u < 9 else mix(col, skin_ramp(look)[2], 0.4)
                p.px(x, y + t, c)
            if thick == 2 and u in (0, 1) and look.brow == 2:
                p.px(x, y - 1, col)       # a heavy brow thickens at the nose
            if u > 9:
                p.px(x, y + thick, mix(col, skin_ramp(look)[2], 0.55)) if thick == 1 else None


def draw_nose(p: Pix, look: Look, g: Geo) -> None:
    """A nose with a lit left plane, a shaded right plane, a ball and wings, nostrils and the shadow under it."""
    sk = skin_ramp(look)
    nw = {0: 3, 1: 4, 2: 5}[look.nose] + (1 if look.skin >= 4 else 0)
    top, base = g.eye + 2, g.nose
    # bridge: lit left, shaded right
    for y in range(top, base - 3):
        k = (y - top) / max(1, base - 3 - top)
        w = round(1 + k * (nw - 2))
        p.px(CX - 1 - (w // 2) + 0, y, sk[3])
        p.px(CX + w // 2 + 0, y, sk[1])
        p.px(CX + w // 2 + 1, y, mix(sk[2], sk[1], 0.55))
        if look.nose == 2 and k > 0.4:
            p.px(CX + w // 2 + 1, y, sk[1])
    # the ball (tip) and wings
    ball_y = base - 3
    for dy in range(3):
        for dx in range(-nw // 2, nw // 2 + 1):
            c = sk[3] if (dx < 0 and dy < 2) else sk[2]
            if dx >= nw // 2 - (0 if dy else 1):
                c = sk[1]
            p.px(CX + dx, ball_y + dy, c)
    p.px(CX - 1, ball_y, sk[4])
    # wings flaring and nostrils
    for side in (-1, 1):
        wx = CX + side * (nw // 2 + 2) - (1 if side < 0 else 0)
        p.px(wx, base - 2, sk[1])
        p.px(wx, base - 1, sk[1])
        p.px(wx - side, base, sk[0])
    p.px(CX - nw // 2, base, sk[0])
    p.px(CX - nw // 2 + 1, base, sk[0])
    p.px(CX + nw // 2 - 1, base, sk[0])
    p.px(CX + nw // 2, base, sk[0])
    # the shadow under the nose
    for dx in range(-nw // 2 - 1, nw // 2 + 2):
        p.px(CX + dx, base + 1, sk[1])
    # the philtrum
    p.px(CX - 1, base + 2, sk[3])
    p.px(CX, base + 2, sk[1])
    p.px(CX - 1, base + 3, sk[2])


def draw_mouth(p: Pix, look: Look, g: Geo) -> None:
    """Lips with a shaded upper and a lit lower, corners set by the mood, a shadow under the lower lip."""
    sk = skin_ramp(look)
    lip, lip_sh = lip_colour(sk, look)
    line = mix(sk[0], (70, 22, 34), 0.6)
    mw = {0: 10, 1: 13, 2: 14}[look.lips] if look.male else {0: 11, 1: 13, 2: 14}[look.lips]
    y = g.mouth
    half = mw // 2
    mood = look.mood
    corner = {"smile": -1, "grin": -1, "stern": 1, "sad": 1, "worried": 0, "calm": 0}.get(mood, 0)
    if mood == "grin":
        # an open smile: a row of teeth between the lips
        for dx in range(-half + 1, half - 1):
            p.px(CX + dx, y, line)
            p.px(CX + dx, y + 1, (226, 214, 190) if abs(dx) < half - 2 else line)
        for dx in range(-half + 2, half - 2):
            p.px(CX + dx, y + 2, line if abs(dx) > half - 4 else lip)
        for dx in (-half, half - 1):
            p.px(CX + dx, y - 1, sk[1])
        for dx in range(-half + 2, half - 2):
            p.px(CX + dx, y - 1, lip_sh)
        for dx in range(-half + 3, half - 3):
            p.px(CX + dx, y + 3, lip)
        return
    # upper lip (shaded), the line, lower lip (lit)
    for dx in range(-half, half):
        edge = abs(dx + 0.5) / half
        yy = y
        if edge > 0.7:
            yy += corner
        p.px(CX + dx, yy, line)
        if edge < 0.86:
            up = lip_sh if look.lips >= 1 or edge < 0.5 else sk[1]
            p.px(CX + dx, yy - 1, up)
            if look.lips == 2 and edge < 0.45:
                p.px(CX + dx, yy - 2, lip_sh)
    p.px(CX - 1, y - 1, mix(lip_sh, SHADOW, 0.2))
    p.px(CX, y - 1, mix(lip_sh, SHADOW, 0.2))
    lower = 1 + (1 if look.lips == 2 else 0)
    for row in range(lower):
        w = half - 1 - row
        for dx in range(-w, w):
            c = lip if row == 0 else mix(lip, (255, 220, 190), 0.12)
            if look.lips and row == lower - 1 and -w + 1 <= dx < -w // 2:
                c = mix(lip, (255, 220, 190), 0.3)           # the catchlight on the lower lip
            p.px(CX + dx, y + 1 + row, c)
    for dx in range(-half + 3, half - 3):
        p.px(CX + dx, y + 1 + lower, sk[1])                    # under-lip shadow
    p.px(CX - 1, y + 2 + lower, sk[3])                          # the chin catches light
    p.px(CX - 2, y + 2 + lower, sk[2])
    # the creases at the corners
    if mood in ("smile", "grin"):
        for side in (-1, 1):
            xx = CX + side * (half + 0) - (1 if side < 0 else 0)
            p.px(xx, y - 1 + corner, sk[1])
            p.px(xx + side, y - 2, sk[1])
            p.px(xx + side, y - 1, sk[1])
    elif mood in ("stern", "sad"):
        for side in (-1, 1):
            xx = CX + side * (half) - (1 if side < 0 else 0)
            p.px(xx, y + 1, sk[1])
            p.px(xx + side, y + 2, sk[1]) if mood == "sad" else None


def draw_age(p: Pix, look: Look, g: Geo, head: Mask, rng: random.Random) -> None:
    """Lines of age: nasolabial folds, then brow furrows, crow's feet, eye bags, jowls."""
    sk = skin_ramp(look)
    age = look.age
    line = sk[1]
    deep = mix(sk[1], sk[0], 0.5)
    if age >= 1:
        for side in (-1, 1):                     # nasolabial folds from the wing of the nose to the mouth corner
            x0 = CX + side * 5 - (1 if side < 0 else 0)
            for i in range(g.mouth - g.nose - 1):
                p.px(x0 + side * (i * 6 // max(1, g.mouth - g.nose)), g.nose + 1 + i, line if age < 2 else deep)
    if age >= 2 or (age == 1 and look.mood in ("stern", "worried", "sad")):
        for side in (-1, 1):                     # the frown line between the brows
            vl(p, CX + side * 2 - (1 if side < 0 else 0), g.brow - 2, 2 + (1 if look.mood in ("stern", "worried") else 0), line)
    if age >= 2:
        for dy in (-11, -8, -5):                 # forehead lines, short broken runs
            y = g.brow + dy
            for run in ((-12, -5), (3, 11)):
                for x in range(run[0], run[1]):
                    if (x + dy) % 5:
                        p.px(CX + x, y, mix(sk[2], sk[1], 0.7))
    if age >= 1:
        for side in (-1, 1):                     # crow's feet
            x0 = CX + side * (g.gap + 11) - (1 if side < 0 else 0)
            n = 2 if age == 1 else 3
            for i in range(n):
                p.px(x0 + side * 1, g.eye - 1 + i * 2, line)
                p.px(x0 + side * 2, g.eye - 1 + i * 2 + (1 if i else 0), line) if age >= 2 else None
    if age >= 2:
        for side in (-1, 1):                     # bags under the eyes, and cheek hollows
            for u in range(2, 9):
                x = CX + side * (g.gap + u) - (1 if side < 0 else 0)
                p.px(x, g.eye + 3, deep if u % 2 else line)
            p.px(CX + side * 12 - (1 if side < 0 else 0), g.mouth + 3, line)
            p.px(CX + side * 12 - (1 if side < 0 else 0), g.mouth + 4, line)
    if age >= 3:
        for side in (-1, 1):
            for i in range(4):
                p.px(CX + side * (13 + i // 2) - (1 if side < 0 else 0), g.mouth - 4 + i, line)
        for dx in range(-4, 4):
            p.px(CX + dx, g.mouth + 6, line) if dx % 2 == 0 else None


# ---------------------------------------------------------------------------------------------- facial hair


def beard_mask(look: Look, g: Geo) -> tuple[Mask, Mask]:
    """(hair mask, mouth hole): the beard's shape for the kind named in the look, without the mouth cut out."""
    kind = look.beard
    head = head_mask(look)
    m = blank()
    hw = g.w // 2
    if kind in ("short", "full", "long"):
        ln = {"short": 3, "full": 8, "long": 21}[kind]
        for y in range(g.eye + 8, g.chin + ln + 1):
            if y <= g.chin:
                n = round(half_width(g, y))
                inner = 0 if y > g.mouth - 2 else 99
                # cheek line: the beard starts under the cheekbones
                x_in = n - 1
                if y < g.nose:
                    x_in = n - 1 - ((g.nose - y) * 3)
                    if x_in < n - 5:
                        continue
                for x in range(CX - n, CX + n):
                    m.putpixel((x, y), 255)
                if y < g.nose + 3:
                    for x in range(CX - (n - 1) + 6, CX + (n - 1) - 6):
                        m.putpixel((x, y), 0)
            else:
                k = (y - g.chin) / ln
                n = round((g.w / 2 * g.jaw) * (1 - k ** 1.8 * (0.95 if kind == "long" else 0.55)))
                for x in range(CX - n, CX + n):
                    m.putpixel((x, y), 255)
    elif kind == "goatee":
        m = oval(CX, g.chin - 4, 7, 9)
    # a moustache over the lip for every kind that shows one
    if kind in ("short", "full", "long", "mustache", "goatee"):
        from people_kit import union
        mo = blank()
        sag = 1 if kind in ("mustache", "long", "full") else 0
        for dx in range(-9, 9):
            ed = abs(dx + 0.5)
            top = g.nose + 2
            bot = g.mouth - 1 + (1 if ed > 4 else 0) * sag + (1 if ed > 6 else 0)
            for y in range(top, bot + 1):
                if ed < 1 and y <= g.nose + 2:
                    continue
                mo.putpixel((CX + dx, y), 255)
        m = union(m, mo)
    return m, blank()


def draw_beard(p: Pix, look: Look, g: Geo) -> None:
    """Facial hair shaded like hair (a dome with strand streaks); stubble is a dither of the hair colour."""
    if look.beard == "none":
        return
    col = look.beard_col or look.hair_col
    ramp = HAIRS[col]
    head = head_mask(look)
    sk = skin_ramp(look)
    from people_kit import both, bayer, union, shift
    if look.beard == "stubble":
        zone = blank()
        for y in range(g.eye + 6, g.chin + 1):
            n = round(half_width(g, y))
            for x in range(CX - n, CX + n):
                if y >= g.nose + 1 or abs(x - CX + 0.5) > 6 + (g.nose - y):
                    zone.putpixel((x, y), 255)
        zone = both(zone, head)
        # not on the lips
        for y in range(g.mouth - 1, g.mouth + 3):
            for x in range(CX - 5, CX + 5):
                zone.putpixel((x, y), 0)
        flat(p, both(zone, bayer(5)), mix(sk[2], ramp[1], 0.55))
        flat(p, both(zone, bayer(2)), mix(sk[1], ramp[1], 0.6))
        return
    m, _ = beard_mask(look, g)
    # the mouth stays visible
    mouth = blank()
    half = 5
    for y in range(g.mouth - 1, g.mouth + 3):
        for x in range(CX - half, CX + half):
            mouth.putpixel((x, y), 255)
    body = minus(m, mouth) if look.beard != "mustache" else m
    if look.beard == "mustache":
        body = minus(m, mouth)
    cy = g.chin - 3
    fill(p, body, ramp, dome(CX, cy, g.w / 2, max(8, (g.chin + (8 if look.beard != "long" else 18) - g.eye) / 2)), texture=0.16)
    # strands: short combs hanging from the cheek to the chin
    rng = random.Random(look.seed + 5)
    for _ in range(26 if look.beard in ("full", "long") else 12):
        x = rng.randrange(CX - 20, CX + 20)
        y = rng.randrange(g.nose, g.chin + (14 if look.beard == "long" else 3))
        ln = rng.randint(2, 4)
        for i in range(ln):
            if inside(body, x + (i // 2) * (1 if x > CX else -1) * 0, y + i):
                p.px(x, y + i, ramp[3] if (x + y) % 3 == 0 else ramp[1])
    # the mouth: a hint of lips shows through the hair
    lip, _ = lip_colour(skin_ramp(look), look)
    for dx in range(-half + 1, half - 1):
        p.px(CX + dx, g.mouth, mix(sk[0], (90, 30, 40), 0.5))
        p.px(CX + dx, g.mouth + 1, lip) if abs(dx) < half - 2 else None
    if look.beard in ("short", "full", "long"):
        # a shadow of the beard on the neck is made by the neck itself; add the cheek edge highlight
        pass
