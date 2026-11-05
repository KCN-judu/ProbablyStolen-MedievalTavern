"""The opened tools of the appraisal desk as brass-and-oak instruments: the aqua scanner (a water-testing frame of glass
vials), the chem scanner (an alchemist's rack of test tubes), the plant scanner (a botanist's press with a lens), the
labeler (a label press bench) and the inspection tray (oak with a leather pad).

Each keeps the game's size, silhouette and working areas. The scanners keep the dark felt window (x 33..178 and from y 58 to
51 pixels above the foot) where the game puts its text, with the same chamfered box and rules in it; the tray keeps its
flat pad where the items are laid and the holes in its two handles; the labeler is stretched by the game with borders of
22, 8, 8 and 38 pixels (left, bottom, right, top), so nothing but flat colour and long grain lies in its stretched middle.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from PIL import Image, ImageChops

import font
from appraisalkit_c import VIOLET, Shape, bevel, bolt, fill, grain, knot, metal_plate, rivet, stitch, vial
from palette import BRASS, GLASS, IRON, LEATHER, MOSS, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix, Ramp, mix

W = 211
LIGHT: Color = (255, 224, 150)
FELT: Color = (38, 30, 44)

AQUA: Ramp = ((16, 52, 72), (36, 96, 122), (66, 148, 164), (150, 208, 208))
VIOLETL: Ramp = ((44, 22, 62), (86, 44, 116), (126, 76, 154), (186, 150, 206))
REDL: Ramp = ((66, 16, 26), (120, 34, 42), (168, 62, 56), (222, 142, 110))
GREENL: Ramp = ((22, 52, 36), (42, 98, 58), (80, 150, 86), (170, 214, 140))
AMBERL: Ramp = ((88, 48, 16), (158, 94, 28), (208, 142, 44), (244, 206, 110))


def keep_only(im: Image.Image, s: Shape) -> Image.Image:
    """Clears everything outside the silhouette, so a picture is transparent where the game's original is."""
    a = im.getchannel("A")
    im.putalpha(ImageChops.multiply(a, s.im))
    return im


def stagger(p: Pix, s: Shape, x0: int, y0: int, x1: int, y1: int, c: Color, density: float) -> None:
    """Dithered shade, but only on cells that belong to the shape (so it never leaks onto a rounded corner)."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            if s.has(x, y) and ((x * 7 + y * 13) % 16) < round(density * 16) and (x + y) % 2 == 0:
                p.px(x, y, c)


# ------------------------------------------------------------------------------------------------ scanners

def porthole(p: Pix, cx: int, cy: int, r: int, liquid: Ramp | None, leaf: bool = False) -> None:
    """A brass-ringed round window: clear glass with a lens glint, a leaf pressed under it, or liquid at the bottom."""
    ring = Shape(p.w, p.h).ellipse(cx - r, cy - r, cx + r, cy + r)
    glass = Shape(p.w, p.h).ellipse(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2)
    fill(p, ring, BRASS[2])
    bevel(p, ring, BRASS[4], BRASS[0], BRASS[0])
    fill(p, glass, GLASS[2] if liquid is None else GLASS[0])
    if leaf:
        fill(p, glass, PARCHMENT[2])
        p.line(cx - 3, cy + 3, cx + 3, cy - 3, MOSS[1])
        p.poly([(cx - 3, cy + 2), (cx - 2, cy - 3), (cx + 3, cy - 3), (cx + 2, cy + 2)], MOSS[2])
        p.line(cx - 2, cy + 2, cx + 2, cy - 2, MOSS[3])
    if liquid is not None:
        for x, y in glass.cells():
            if y >= cy:
                p.px(x, y, liquid[1] if x > cx else liquid[2])
        for x, y in glass.cells():
            if y == cy:
                p.px(x, y, liquid[3])
        p.px(cx - 1, cy + 3, liquid[3])
        p.px(cx + 2, cy + 2, liquid[3])
    bevel(p, glass, GLASS[0], GLASS[4], None)
    p.px(cx - r + 3, cy - 1, GLASS[4])
    p.px(cx - r + 3, cy - 2, GLASS[4])
    p.px(cx - 1, cy - r + 3, GLASS[4])
    p.px(cx - 2, cy - r + 3, GLASS[3])


def side_vials(p: Pix, h: int, kind: str) -> None:
    """The two side rails of the aqua and chem frames hold glass vials, one above and one below the hinge, on each side."""
    spans = ((58, 130), (160, h - 47))
    for side in (0, 1):
        for si, (y0, y1) in enumerate(spans):
            hh = y1 - y0
            if kind == "aqua":
                x = 5 if side == 0 else 197
                p.rect(x - 2, y0 - 2, 13, hh + 5, FELT)
                p.frame(x - 2, y0 - 2, 13, hh + 5, BRASS[1])
                vial(p, x, y0, 9, hh, AQUA, (0.78, 0.55, 0.45, 0.86)[side * 2 + si])
            else:
                x = 5 if side == 0 else 197
                p.rect(x - 2, y0 - 2, 13, hh + 5, FELT)
                p.frame(x - 2, y0 - 2, 13, hh + 5, IRON[2])
                n = 0
                for yy in range(y0, y1 - 21, 25):
                    liquid = (VIOLETL, REDL, GREENL, AMBERL)[(side + si + n) % 4]
                    level = (0.7, 0.45, 0.85, 0.55, 0.3, 0.8)[(n + side * 2 + si) % 6]
                    vial(p, x, yy, 9, 22, liquid, level, ticks=False)
                    n += 1


def inlay_vine(p: Pix, h: int) -> None:
    """A brass vine inlaid in each side rail of the plant press."""
    for x0 in (9, 201):
        for y0, y1 in ((60, 130), (160, h - 48)):
            p.vline(x0, y0, y1 - y0, BRASS[2])
            p.vline(x0 - 1, y0, y1 - y0, BRASS[1])
            for k, y in enumerate(range(y0 + 4, y1 - 4, 9)):
                d = -1 if k % 2 else 1
                p.poly([(x0, y), (x0 + d * 5, y - 3), (x0 + d * 6, y - 1), (x0 + d * 4, y + 1)], BRASS[3])
                p.px(x0 + d * 3, y - 1, BRASS[4])
        p.px(x0, 56, BRASS[4])


TOP_CUT = (22, 19, 16, 14, 13, 12, 10, 9, 8, 7, 6, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0)       # rows 26.. of the body
BOTTOM_CUT = (0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 10, 12, 13, 14, 16, 19, 22)       # its last 23 rows


def body_outline(h: int) -> list[tuple[int, int]]:
    """The body of a scanner: rounded corners cut in as the game's are, and a notch on each side where the halves hinge."""
    last = h - 18
    cut = {y: 0 for y in range(26, last + 1)}
    for k, c in enumerate(TOP_CUT):
        cut[26 + k] = c
    for k, c in enumerate(BOTTOM_CUT):
        cut[last - len(BOTTOM_CUT) + 1 + k] = c
    for y, c in ((135, 1), (136, 2)) + tuple((y, 3) for y in range(137, 155)):
        cut[y] = c
    left = [(cut[y], y) for y in range(26, last + 1)]
    right = [(210 - cut[y], y) for y in range(last, 25, -1)]
    return left + right


def scanner(h: int, frame: Ramp, title: str, kind: str, seed: int) -> Image.Image:
    p = Pix(W, h, seed=seed)
    body = Shape(W, h).poly(body_outline(h))
    outer = [(63, 0), (59, 1), (56, 2), (53, 3), (51, 4), (49, 5), (47, 6), (45, 7), (43, 8), (42, 9), (41, 10), (40, 11), (39, 12),
             (38, 13), (37, 14), (36, 15), (35, 16), (34, 17), (33, 18), (33, 19), (32, 20), (32, 21), (31, 22), (31, 30)]
    opening = [(65, 12), (61, 13), (58, 14), (54, 15), (52, 16), (51, 17), (50, 18), (49, 19), (48, 20), (47, 21), (46, 22),
               (45, 24), (45, 32)]
    mirrored = [(210 - x, y) for x, y in reversed(outer)]
    handle = Shape(W, h).poly(outer + mirrored)
    handle.poly(opening + [(210 - x, y) for x, y in reversed(opening)], on=False)
    foot = Shape(W, h).rect(34, h - 14, 176, h - 1).rect(32, h - 17, 178, h - 15)

    # the foot: a plate of iron that the apparatus stands on
    fill(p, foot, IRON[3])
    bevel(p, foot, IRON[4], IRON[1], SHADOW)
    for x in (62, 105, 148):
        p.vline(x, h - 13, 9, IRON[2])
    rivet(p, 40, h - 12, BRASS)
    rivet(p, 168, h - 12, BRASS)

    # the handle: a brass pipe with a leather-wrapped grip
    fill(p, handle, BRASS[2])
    bevel(p, handle, BRASS[4], BRASS[0], BRASS[0], hi2=BRASS[3])
    for x, y in handle.cells():
        if y in (3, 4) and 66 < x < 144 and (x // 3) % 2 == 0:
            p.px(x, y, BRASS[3])
    grip = handle.inter(Shape(W, h).rect(76, 0, 134, 12))
    fill(p, grip, LEATHER[2])
    for x, y in grip.cells():
        if (x - 76) % 4 == 0:
            p.px(x, y, LEATHER[0])
        elif (x - 76) % 4 == 1:
            p.px(x, y, LEATHER[3])
    bevel(p, grip, LEATHER[3], LEATHER[0], SHADOW)

    # the frame
    left_rail = body.inter(Shape(W, h).rect(0, 0, 19, h))
    right_rail = body.inter(Shape(W, h).rect(191, 0, 210, h))
    top_bot = body.minus(left_rail).minus(right_rail)
    grain(p, top_bot, frame, vertical=False)
    grain(p, left_rail, frame, vertical=True)
    grain(p, right_rail, frame, vertical=True)
    bevel(p, body, frame[4], frame[1], frame[0], hi2=frame[3])
    for x0, y0, x1, y1 in ((2, 29, 18, 43), (208, 29, 192, 43), (2, h - 21, 18, h - 37), (208, h - 21, 192, h - 37)):
        p.line(x0, y0, x1, y1, frame[0])                       # the mitred corners
        p.line(x0 + (1 if x0 < 100 else -1), y0, x1 + (1 if x0 < 100 else -1), y1, frame[1])
    knot(p, 120, h - 28, frame)
    knot(p, 40, 34, frame)

    # the window: dark felt in a rounded recess, lit on its lower right edge
    rec = Shape(W, h).rrect(19, 44, 191, h - 37, 16)
    fill(p, rec, FELT)
    bevel(p, rec, mix(FELT, VIOLET, 0.0), frame[3], frame[0], hi2=None)
    for y, d in ((45, 0.7), (46, 0.5), (47, 0.3), (48, 0.15)):
        stagger(p, rec, 21, y, 190, y + 1, (22, 17, 28), d)
    for x, d in ((20, 0.6), (21, 0.4), (22, 0.2)):
        stagger(p, rec, x, 50, x + 1, h - 40, (22, 17, 28), d)
    bot = h - 51
    outline = [(37, 58), (174, 58), (178, 62), (178, bot - 4), (174, bot), (37, bot), (33, bot - 4), (33, 62), (37, 58)]
    for (xa, ya), (xb, yb) in zip(outline, outline[1:]):
        p.line(xa, ya, xb, yb, BRASS[1])
    for y in range(90, bot - 50, 26):
        p.hline(34, y, 144, mix(BRASS[1], BRASS[2], 0.5))
    for x in (35, 175):                                         # marks at the ends of the rules
        for y in range(90, bot - 50, 26):
            p.px(x, y, BRASS[3])
    p.px(33, 62, BRASS[2])

    # the brackets where the handle joins, the nameplate and the hinges
    metal_plate(p, 30, 22, 19, 9, BRASS, wear=2)
    metal_plate(p, 162, 22, 19, 9, BRASS, wear=2)
    pw = font.width(title) + 14
    px0 = 105 - pw // 2
    metal_plate(p, px0, 30, pw, 12, BRASS, rivets=False, wear=3)
    font.write(p, px0 + 8, 33, title, BRASS[4])
    font.write(p, px0 + 7, 32, title, BRASS[0])
    rivet(p, px0 + 2, 33, BRASS)
    rivet(p, px0 + pw - 5, 33, BRASS)
    for x in (3, 192):
        metal_plate(p, x, 139, 16, 15, IRON, rivets=False)
        rivet(p, x + 3, 141, BRASS)
        rivet(p, x + 10, 141, BRASS)
        rivet(p, x + 3, 148, BRASS)
        rivet(p, x + 10, 148, BRASS)
        p.hline(x + 1, 146, 14, IRON[0])

    if kind == "plant":
        inlay_vine(p, h)
        porthole(p, 148, 36, 7, None)
        porthole(p, 62, 36, 7, None, leaf=True)
    elif kind == "aqua":
        side_vials(p, h, "aqua")
        porthole(p, 148, 36, 7, AQUA)
        porthole(p, 62, 36, 7, AQUA)
    else:
        side_vials(p, h, "chem")
        porthole(p, 148, 36, 7, VIOLETL)
        porthole(p, 62, 36, 7, REDL)
    # bottom rail: a row of brass studs
    for x in range(30, 182, 20):
        rivet(p, x, h - 31, BRASS)
    return keep_only(p.finish(), union(body, handle, foot))


def union(*shapes: Shape) -> Shape:
    out = Shape(shapes[0].w, shapes[0].h)
    for s in shapes:
        out.im = ImageChops.lighter(out.im, s.im)
    out._d, out._px = None, out.im.load()  # type: ignore[assignment]
    return out


def plant_scanner() -> Image.Image:
    return scanner(303, WOOD, "HERBAL", "plant", 71)


def aqua_scanner() -> Image.Image:
    return scanner(328, PALE_WOOD, "AQUA", "aqua", 72)


def chem_scanner() -> Image.Image:
    return scanner(357, OAK, "ALCHEMY", "chem", 73)


# ------------------------------------------------------------------------------------------------ tray

# how far each of the first rows of the tray's silhouette is cut in from the left (60 is the top row, 30 the full width)
TRAY_CUT = (60, 57, 54, 52, 50, 48, 47, 46, 44, 43, 42, 41, 40, 39, 38, 38, 37, 36, 35, 35, 34, 34, 33, 33, 32, 32, 32,
            31, 31, 31, 30, 30)


def rounded_outline(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """A box whose corners follow the tray's curve (30 pixels wide, a squarer bend than a circle)."""
    n = len(TRAY_CUT)
    tl = [(x0 + TRAY_CUT[k] - 30, y0 + k) for k in range(n - 1, -1, -1)]
    tr = [(x1 - TRAY_CUT[k] + 30, y0 + k) for k in range(n)]
    br = [(x1 - TRAY_CUT[k] + 30, y1 - k) for k in range(n - 1, -1, -1)]
    bl = [(x0 + TRAY_CUT[k] - 30, y1 - k) for k in range(n)]
    return tl + tr + br + bl


def tray() -> Image.Image:
    w, h = 456, 402
    p = Pix(w, h, seed=81)
    body = Shape(w, h).poly(rounded_outline(30, 0, 425, 401))
    lug_l = [(31, 124), (29, 126), (25, 132), (0, 157), (0, 244), (26, 270), (29, 276), (31, 278)]
    lug_r = [(455 - x, y) for x, y in lug_l]
    silhouette = Shape(w, h).poly(rounded_outline(30, 0, 425, 401)).poly(lug_l).poly(lug_r)
    silhouette.ellipse(17, 198, 23, 204, on=False)
    silhouette.ellipse(432, 198, 438, 204, on=False)

    # the rim: a flat band of waxed oak all round, grain along each side
    inner = Shape(w, h).rrect(40, 10, 415, 391, 24)
    ring = body.minus(inner)
    sides = ring.inter(Shape(w, h).rect(0, 32, 455, 369)).minus(Shape(w, h).rect(41, 0, 414, 401))
    grain(p, ring.minus(sides), WOOD, vertical=False)
    grain(p, sides, WOOD, vertical=True)
    bevel(p, ring, WOOD[4], WOOD[1], WOOD[0], hi2=WOOD[3])

    # the inner walls slope down to the pad; the ones facing the light are lighter
    floor = Shape(w, h).rrect(60, 32, 395, 369, 14)
    walls = inner.minus(floor)
    fill(p, walls, WOOD[1])                                          # under the four pieces, so no corner is left open
    quads = {
        "top": ([(40, 10), (415, 10), (395, 32), (60, 32)], (WOOD[0], WOOD[0], WOOD[1], WOOD[1], WOOD[2]), False),
        "left": ([(40, 10), (60, 32), (60, 369), (40, 391)], (WOOD[0], WOOD[1], WOOD[1], WOOD[2], WOOD[2]), True),
        "right": ([(415, 10), (415, 391), (395, 369), (395, 32)], (WOOD[1], WOOD[2], WOOD[3], WOOD[3], WOOD[4]), True),
        "bottom": ([(60, 369), (395, 369), (415, 391), (40, 391)], (WOOD[1], WOOD[2], WOOD[3], WOOD[3], WOOD[4]), False),
    }
    for pts, ramp, vertical in quads.values():
        piece = walls.inter(Shape(w, h).poly(pts))
        grain(p, piece, ramp, vertical)
    for a, b in (((40, 10), (60, 32)), ((415, 10), (395, 32)), ((40, 391), (60, 369)), ((415, 391), (395, 369))):
        p.line(a[0], a[1], b[0], b[1], WOOD[0])                      # mitre joints of the four walls
    p.hline(61, 33, 334, WOOD[0])

    # the leather pad: flat where items are laid, stitched near its edge, shadowed under the walls
    fill(p, floor, LEATHER[2])
    p.speckle(60, 32, 336, 338, [LEATHER[1], LEATHER[3]], 0.012)
    for i, d in enumerate((0.75, 0.6, 0.45, 0.32, 0.2, 0.1)):
        stagger(p, floor, 62, 34 + i, 394, 35 + i, LEATHER[1], d)
        stagger(p, floor, 61 + i, 36, 62 + i, 368, LEATHER[1], d * 0.8)
    bevel(p, floor, LEATHER[3], LEATHER[1], (34, 20, 14))
    stitch(p, 74, 39, 381, 39, mix(LEATHER[3], LIGHT, 0.25), 4)
    stitch(p, 74, 362, 381, 362, mix(LEATHER[3], LIGHT, 0.25), 4)
    stitch(p, 67, 46, 67, 355, mix(LEATHER[3], LIGHT, 0.25), 4)
    stitch(p, 388, 46, 388, 355, mix(LEATHER[3], LIGHT, 0.25), 4)

    # inlay and hardware on the rim: a brass rule with ticks on the top, studs on the bottom and sides
    p.hline(70, 5, 316, BRASS[1])
    for i in range(0, 316, 10):
        long = (i // 10) % 5 == 0
        p.vline(70 + i, 5 if long else 3, 5 if long else 3, BRASS[3])
        p.px(70 + i, 3 if long else 3, BRASS[4])
    for x in range(70, 390, 40):
        rivet(p, x, 394, BRASS)
    for y in (70, 110, 292, 332):
        rivet(p, 33, y, BRASS)
        rivet(p, 420, y, BRASS)

    # the handles: iron lugs bolted to the rim, a brass washer round each hole
    for pts, hx in ((lug_l, 20), (lug_r, 435)):
        lug = Shape(w, h).poly(pts)
        lug = lug.inter(Shape(w, h).rect(0, 0, 38, 401)) if hx < 200 else lug.inter(Shape(w, h).rect(417, 0, 455, 401))
        fill(p, lug, IRON[2])
        bevel(p, lug, IRON[4], IRON[0], SHADOW, hi2=IRON[3])
        sign = 1 if hx < 200 else -1
        for y in (150, 252):
            rivet(p, hx + sign * 5 - (1 if sign < 0 else 0), y, BRASS)
        ring = Shape(w, h).ellipse(hx - 7, 194, hx + 7, 208)
        fill(p, ring, BRASS[2])
        bevel(p, ring, BRASS[4], BRASS[0], BRASS[0])
        p.ellipse(hx - 3, 198, 7, 7, CLEAR)
        # a few scratches of wear on the iron
        for k in range(5):
            x0 = hx - 9 + p.rng.randrange(18)
            y0 = 165 + p.rng.randrange(70)
            p.hline(x0, y0, 3 + p.rng.randrange(4), IRON[3])
    return keep_only(p.finish(), silhouette)


# ------------------------------------------------------------------------------------------------ labeler

def labeler() -> Image.Image:
    """A label press bench seen from above: an oak head-board with brass fittings, a leather frame and a flat blotting
    leather where the label goes. Only borders (22, 8, 8, 38) carry detail; the middle the game stretches is plain."""
    w, h = 548, 258
    p = Pix(w, h, VIOLET, seed=91)
    # the head-board: horizontal oak grain only, so stretching it sideways looks the same
    head = Shape(w, h).rect(2, 2, 545, 29)
    grain(p, head, PALE_WOOD, vertical=False, seed_tones=(1, 2, 2, 3, 3, 4), base=3)
    p.hline(2, 2, 544, PALE_WOOD[4])
    p.hline(2, 3, 544, PALE_WOOD[4])
    p.hline(2, 4, 544, PALE_WOOD[3])
    p.hline(2, 27, 544, PALE_WOOD[1])
    p.hline(2, 28, 544, PALE_WOOD[1])
    p.hline(2, 29, 544, PALE_WOOD[0])
    p.hline(22, 25, 520, BRASS[1])                        # a brass inlay rule along the foot of the board
    p.hline(22, 24, 520, BRASS[3])
    # the frame: oxblood leather with a dark seam at both edges
    p.rect(2, 32, w - 4, 224, WINE[2])
    p.speckle(2, 32, w - 4, 224, [WINE[1], WINE[3]], 0.03)
    p.hline(2, 32, w - 4, WINE[3])
    p.vline(2, 32, 224, WINE[3])
    p.hline(2, 255, w - 4, WINE[1])
    p.vline(w - 3, 32, 224, WINE[1])
    p.rect(0, 30, w, 2, VIOLET)
    p.rect(2, 36, 6, 214, WINE[2])
    p.rect(6, 36, 2, 214, (57, 46, 60))
    p.rect(540, 36, 2, 214, (57, 46, 60))
    p.rect(2, 36, w - 4, 2, (57, 46, 60))
    p.rect(2, 250, w - 4, 2, (57, 46, 60))
    # the pad: flat blotting leather, with a thin shade on its top and left edges
    p.rect(8, 38, 532, 212, (148, 126, 88))
    p.hline(8, 38, 532, (126, 106, 74))
    p.vline(8, 38, 212, (126, 106, 74))
    p.hline(8, 249, 532, (166, 144, 100))
    p.vline(539, 38, 212, (166, 144, 100))
    # brass bracket and rivets on the left of the head-board, a rivet at the right end
    metal_plate(p, 3, 4, 18, 23, BRASS, wear=3)
    bolt_x, bolt_y = 12, 15
    bolt(p, bolt_x, bolt_y)
    p.hline(5, 24, 14, BRASS[1])
    rivet(p, 540, 12, BRASS)
    # outer dark rim, then the cut corner
    p.frame(0, 0, w, h, VIOLET)
    p.frame(1, 1, w - 2, h - 2, VIOLET)
    cut = Shape(w, h).rect(0, 0, w - 1, h - 1)
    for i in range(6):
        cut.rect(0, i * 2, 11 - i * 2, i * 2 + 1, on=False)
    return keep_only(p.finish(), cut)


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "aqua_scan.211x328.png": aqua_scanner,
    "chem_scan.211x357.png": chem_scanner,
    "plant_scanner.211x303.png": plant_scanner,
    "tray.456x402.png": tray,
    "labeler.548x258.png": labeler,
}
