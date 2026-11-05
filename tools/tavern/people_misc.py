"""The odd pictures of the people group, redrawn for the bow: the drawing hand in first person, the fallen body, the
customer's shadow at the window, and the eight-frame sequence of a customer who is shot with an arrow and falls (with the
sheet of hit marks that is laid over it).

Shapes are masks painted with `people_kit.paint` (light from the upper left, a dithered shade at the lower right), the
same way the portraits are drawn, so these sit next to them without looking like a lower tier.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image, ImageDraw

from palette import PALE_WOOD as PALE
from bow_draw import SKIN, YEW, arrow, bez, stroke, string, taper, wrap_grip
from palette import BRASS, LEATHER, LINEN, SHADOW, WINE
from people_cast import NAMED
from people_figure import render
from people_kit import CH, SKINS, W, both, bayer, blank, hx, minus, oval, overlay, paint, poly, put, shift, shrink, tone
from pix import Pix, mix, rgb

Pt = tuple[float, float]


# ---------------------------------------------------------------------------------------------- the drawing hand


def one_hand() -> Image.Image:
    """First person: the left hand grips the bow, an arrow nocked on the string lying beside the fist, the forearm in a
    leather bracer and a linen sleeve running off the bottom right. The bow's limbs run off the top and bottom edges."""
    p = Pix(W, CH, seed=70)
    gx, gy = 84.0, 66.0
    dx, dy = 0.79, 0.61           # along the arrow, toward the shooter (down and to the right)
    nx, ny = 0.61, -0.79          # along the stave, toward the upper tip

    def lp(a: float, b: float) -> Pt:
        return gx + a * dx + b * nx, gy + a * dy + b * ny

    tip_u, tip_l, ctl = lp(24, 118), lp(24, -118), lp(-44, 0)
    stave = bez(tip_u, ctl, tip_l, 220)
    widths = taper(6.0, 6.0, 220, mid=11.0)
    # string first (it passes behind the arm), then the limbs over it
    string(p, tip_u, tip_l)
    p.line(round(tip_u[0]) - 1, round(tip_u[1]), round(tip_l[0]) - 1, round(tip_l[1]), mix(LINEN[1], SHADOW, 0.35))
    stroke(p, stave, widths, YEW)
    for i in range(6, 214, 4):
        x, y = stave[i]
        p.px(round(x), round(y), YEW[3])
    gm = stave[110]
    wrap_grip(p, (gm[0] + nx * 24, gm[1] + ny * 24), (gm[0] - nx * 24, gm[1] - ny * 24), 10)

    def band(a0: float, a1: float, b0: float, b1: float) -> Image.Image:
        return poly([lp(a0, -b0), lp(a0, b0), lp(a1, b1), lp(a1, -b1)])

    # forearm: wrist bare, then a studded leather bracer, then the linen sleeve
    paint(p, band(0, 190, 13, 22), SKIN, d=3)
    paint(p, band(26, 70, 15, 18), tone(rgb("#6e4326")), d=2, soft=False)
    for k in (36, 48, 60):
        a, b = lp(k, -15), lp(k + 3, 15)
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), LEATHER[0])
    for k, side in ((31, 1), (31, -1), (65, 1), (65, -1)):
        x, y = lp(k, side * 13)
        p.px(round(x), round(y), BRASS[3])
        p.px(round(x) + 1, round(y), BRASS[1])
    paint(p, band(72, 200, 22, 34), tone(rgb("#b3a88c")), d=3)
    for k in (-14, -4, 8, 18):
        a, b = lp(78, k), lp(130, k * 1.5)
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), LINEN[1])
    put(p, band(70, 76, 21, 24), LINEN[1])

    # the fist round the grip: the back of the hand, four outlined fingers curling over the grip, the thumb on top
    paint(p, poly([lp(4, -16), lp(0, -14), lp(-2, 14), lp(4, 17), lp(30, 14), lp(30, -14)]), SKIN, d=3)
    for b in (-12.0, -4.0, 4.0, 12.0):
        f0, f1 = lp(6, b), lp(-12, b)
        pts = [(f0[0] + (f1[0] - f0[0]) * t / 11, f0[1] + (f1[1] - f0[1]) * t / 11) for t in range(12)]
        stroke(p, pts, [8.0] * 12, SKIN)
        tip = lp(-14, b)
        p.px(round(tip[0]), round(tip[1]), SKIN[4])
        kx, ky = lp(0, b)
        p.px(round(kx), round(ky), SKIN[4])
        p.px(round(kx) + 1, round(ky), SKIN[3])
    t0, t1 = lp(16, 19), lp(-16, 21)
    stroke(p, [(t0[0] + (t1[0] - t0[0]) * t / 11, t0[1] + (t1[1] - t0[1]) * t / 11) for t in range(12)], [8.0] * 12, SKIN)
    # the arrow, nocked on the string and resting on the hand beside the grip (a second shaft line makes it two pixels)
    tail, head = lp(24, 24), lp(-70, 24)
    p.line(round(tail[0]), round(tail[1]) + 1, round(head[0]), round(head[1]) + 1, PALE[2])
    arrow(p, tail, head, vane=4, head_len=9)
    return p.im.crop((0, 0, 160, 112))


# ---------------------------------------------------------------------------------------------- body, shadow


def body() -> Image.Image:
    """A fallen customer in a dark cloak seen from the front, head back, an arrow standing in the chest (90x48)."""
    p = Pix(W, CH, seed=71)
    cloak = tone(rgb("#4a3446"))
    mass = poly([(-4, 70), (0, 40), (8, 30), (22, 24), (34, 22), (56, 22), (68, 24), (82, 30), (90, 40), (94, 70)])
    paint(p, mass, cloak, d=4)
    # folds of the cloak and the collar
    for pts in (((12, 36), (22, 44), (26, 60)), ((78, 36), (68, 44), (64, 60)), ((34, 28), (40, 40), (38, 58))):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            p.line(x0, y0, x1, y1, cloak[1])
            p.line(x0 + 1, y0, x1 + 1, y1, cloak[3])
    collar = poly([(33, 22), (40, 32), (45, 28), (50, 32), (57, 22), (52, 20), (38, 20)])
    paint(p, collar, tone(rgb("#6e4326")), d=2, soft=False)
    # the head, tipped back: skin, hair, closed eyes and a beard
    paint(p, oval(45, 12, 10, 12), SKINS[3], d=3)
    paint(p, poly([(35, 9), (36, 1), (45, -2), (54, 1), (55, 9), (50, 5), (45, 4), (40, 5)]), hx("#43302a"), d=2, soft=False)
    paint(p, poly([(37, 17), (41, 20), (49, 20), (53, 17), (51, 23), (45, 26), (39, 23)]), hx("#43302a"), d=2, soft=False)
    p.hline(39, 10, 4, SKINS[3][0])
    p.hline(48, 10, 4, SKINS[3][0])
    p.hline(42, 16, 6, SKINS[3][1])
    p.vline(45, 11, 4, SKINS[3][1])
    # the arrow in the chest, the dark stain round its foot kept small
    stain = oval(61, 38, 7, 5)
    overlay(p, stain, WINE[1], 10)
    overlay(p, shrink(stain, 2), SHADOW, 8)
    arrow(p, (74.0, 8.0), (60.0, 38.0), vane=4, head_len=1, show_head=False)
    p.px(60, 38, SHADOW)
    return p.im.crop((0, 0, 90, 48))


def client_shadow() -> Image.Image:
    """The customer's silhouette at the window: a hooded head and rounded shoulders in a flat blue-grey (48x64)."""
    p = Pix(W, CH)
    ramp = ((92, 110, 150), (110, 130, 170), (126, 146, 182), (150, 168, 204), (172, 188, 220))
    hood = poly([(22, 6), (30, 9), (35, 17), (36, 27), (32, 34), (14, 34), (10, 27), (11, 17), (15, 9)])
    paint(p, hood, ramp, d=3, edge=ramp[1])
    shoulders = poly([(1, 70), (2, 52), (7, 42), (17, 36), (29, 36), (39, 42), (43, 52), (44, 70)])
    paint(p, shoulders, ramp, d=3, edge=ramp[1])
    # the dark mouth of the hood and the cloak's fold keep it from being a blob
    opening = oval(23, 22, 7, 9)
    put(p, minus(opening, oval(21, 18, 6, 7)), ramp[1])
    p.line(22, 36, 20, 52, ramp[1])
    p.line(23, 36, 22, 52, ramp[3])
    return p.im.crop((0, 0, 48, 64))


# ---------------------------------------------------------------------------------------------- the shot sequence

CX = 125.0
# per frame: x scale, y scale, lean (a shear that moves the head), drop of the feet, and the content box the original keeps
STAGGER = (
    (1.00, 1.00, 0.04, 0, (53, 99, 198, 256)),
    (0.98, 0.955, -0.10, 0, (54, 106, 197, 256)),
    (0.86, 0.80, 0.20, 3, (63, 128, 188, 253)),
    (0.68, 0.63, -0.26, 3, (75, 155, 174, 253)),
)
LAST_BOXES = ((78, 159, 170, 253), (80, 205, 170, 253))


def _placed_figure() -> Image.Image:
    """The man of the portrait, standing as in frame 0, on the tall drawing canvas (the feet run to its bottom edge)."""
    fig = render(NAMED["case_enjoyer"])
    canvas = Image.new("RGBA", (W, CH), (0, 0, 0, 0))
    canvas.alpha_composite(fig, (-19, 45))
    bottom = canvas.crop((0, 255, W, 256)).resize((W, CH - 255), Image.Resampling.NEAREST)
    canvas.alpha_composite(bottom, (0, 255))
    return canvas


def _stagger_mask(canvas: Image.Image, kx: float, ky: float, lean: float, drop: int) -> Image.Image:
    """The figure's silhouette bent by a lean, shrunk and let down: the mask of a customer reeling from the shot."""
    ybot = 256.0
    coeff = (1 / kx, lean / kx, CX + (-CX - lean * ybot) / kx, 0, 1 / ky, ybot - ybot / ky)
    m = canvas.getchannel("A").point(lambda v: 255 if v > 100 else 0)
    m = m.transform(m.size, Image.Transform.AFFINE, coeff, Image.Resampling.NEAREST)
    out = blank()
    out.paste(m, (0, -drop))
    if drop == 0:
        out.paste(out.crop((0, 255, W, 256)).resize((W, CH - 255)), (0, 255))
    return out


def _dark_figure(p: Pix, m: Image.Image) -> None:
    """Paints a silhouette mask as a dark wine-black figure with a lantern sheen, a neckline and a seam down the front."""
    ramp = tone(rgb("#4a3040"))
    paint(p, m, ramp, d=3)
    x0, y0, x1, y1 = m.getbbox() or (0, 0, 1, 1)
    h, w = y1 - y0, x1 - x0
    cxm = (x0 + x1) // 2
    fold = Image.new("L", m.size, 0)
    d = ImageDraw.Draw(fold)
    d.line((cxm, y0 + round(h * 0.40), cxm, y1 - 2), fill=255)
    d.line((x0 + round(w * 0.2), y0 + round(h * 0.47), cxm - 4, y0 + round(h * 0.43)), fill=255)
    d.line((x1 - round(w * 0.2), y0 + round(h * 0.47), cxm + 4, y0 + round(h * 0.43)), fill=255)
    put(p, both(fold, shrink(m, 2)), ramp[1])
    overlay(p, both(oval(cxm, y0 + round(h * 0.37), max(3, w // 9), max(2, h // 22)), m), ramp[0], 9)
    top = minus(m, shift(m, 0, 3))
    overlay(p, both(top, bayer(8)), ramp[4], 8)


def _arrow_in_body(p: Pix, foot: Pt, tail: Pt) -> None:
    """An arrow standing in a body: shaft and fletching only, the head is inside."""
    arrow(p, tail, foot, vane=4, head_len=1, show_head=False)
    p.px(round(foot[0]), round(foot[1]), SHADOW)


def _slumped(p: Pix) -> None:
    """Frame 6: the customer folded forward over the counter, head hanging, a cloak heaped over the back, an arrow in it."""
    cloak = tone(rgb("#4a3040"))
    heap = poly([(80, 258), (80, 232), (88, 208), (104, 192), (126, 186), (148, 190), (162, 204), (169, 228), (170, 258)])
    paint(p, heap, cloak, d=4)
    paint(p, oval(108, 184, 15, 16), tone(rgb("#5a3a48")), d=3)
    paint(p, poly([(95, 180), (98, 168), (110, 166), (121, 171), (123, 182), (110, 175)]), tone(rgb("#2c2028")), d=2, soft=False)
    for pts in (((98, 200), (92, 226), (90, 250)), ((140, 190), (150, 214), (154, 250)), ((120, 196), (122, 222), (118, 250))):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            p.line(x0, y0, x1, y1, cloak[1])
            p.line(x0 + 1, y0, x1 + 1, y1, cloak[3])
    overlay(p, oval(144, 214, 9, 6), WINE[1], 9)
    _arrow_in_body(p, (144.0, 214.0), (160.0, 172.0))


def _fallen(p: Pix) -> None:
    """Frame 7: the customer lying low behind the counter edge: shoulders and head, the arrow standing up from the chest."""
    cloak = tone(rgb("#4a3040"))
    paint(p, poly([(80, 262), (82, 238), (92, 224), (108, 218), (146, 218), (162, 226), (170, 240), (170, 262)]), cloak, d=3)
    paint(p, oval(122, 214, 11, 9), tone(rgb("#5a3a48")), d=2, soft=False)
    p.hline(114, 213, 5, cloak[0])
    p.hline(125, 213, 5, cloak[0])
    overlay(p, oval(142, 230, 7, 4), WINE[1], 9)
    _arrow_in_body(p, (142.0, 230.0), (156.0, 206.0))


def shot_frames() -> Image.Image:
    """Eight 256x256 frames: the man at rest twice, then four staggering dark figures, a slumped heap, a small body."""
    canvas = _placed_figure()
    out = Image.new("RGBA", (2048, 256), (0, 0, 0, 0))
    for i in range(8):
        if i < 2:
            frame = canvas.crop((0, 0, 256, 256))
        else:
            p = Pix(W, CH, seed=80 + i)
            if i < 6:
                kx, ky, lean, drop, box = STAGGER[i - 2]
                _dark_figure(p, _stagger_mask(canvas, kx, ky, lean, drop))
            else:
                box = LAST_BOXES[i - 6]
                (_slumped if i == 6 else _fallen)(p)
            # each frame keeps its content where the original frame puts it
            frame = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            frame.alpha_composite(p.im.crop(box), box[:2])
        out.alpha_composite(frame, (i * 256, 0))
    return out


def wounds() -> Image.Image:
    """Six hit marks over the chest, widening as the figure falls: a dark entry, a short arrow shaft and its feathers
    seen nearly end-on; the last two frames carry nothing (the heap has its own arrow). Each stays in the original's box."""
    out = Image.new("RGBA", (2048, 256), (0, 0, 0, 0))
    # entry point, tail point, box of the original mark
    marks = (
        ((124, 211), (128, 207), (116, 206, 132, 216)),
        ((124, 211), (128, 207), (116, 206, 132, 216)),
        ((122, 214), (131, 205), (113, 203, 135, 220)),
        ((119, 205), (131, 197), (109, 194, 135, 211)),
        ((123, 207), (137, 200), (112, 197, 140, 212)),
        ((123, 214), (140, 208), (110, 205, 143, 220)),
    )
    for i, ((ex, ey), (tx, ty), box) in enumerate(marks):
        p = Pix(W, CH, seed=90 + i)
        r = 4 + i // 2
        p.ellipse(ex - r, ey - r // 2 - 1, 2 * r, r + 2, WINE[0])
        overlay(p, oval(ex, ey, r + 1, r // 2 + 2), SHADOW, 7)
        p.ellipse(ex - 1, ey - 1, 3, 2, SHADOW)
        arrow(p, (float(tx), float(ty)), (float(ex), float(ey)), vane=2 + (i > 1), head_len=1, show_head=False)
        out.alpha_composite(p.im.crop(box), (i * 256 + box[0], box[1]))
    return out


PICTURES: Mapping[str, Callable[[], Image.Image]] = {
    "one_hand.160x112.png": one_hand,
    "body.90x48.png": body,
    "client_shadow_small.48x64.png": client_shadow,
    "shot_animation_body.2048x256.png": shot_frames,
    "shot_animation_wound.2048x256.png": wounds,
}
