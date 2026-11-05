"""The bow pictures that live outside the people group: the hunting bow and quiver leaning under the counter (and its
shadow layer), the burst of a released arrow, and the two ranged-weapon item pictures (a longbow and a crossbow).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping

from PIL import Image

from bow_draw import YEW, arrow, bez, grain, nock_tip, string, stroke, taper, wrap_grip
from palette import BRASS, FLAME, IRON, LEATHER, LINEN, OAK, PARCHMENT, PLASTER, SHADOW, WINE, WOOD
from pix import Pix, mix, rgb

# --------------------------------------------------------------------------- the bow under the counter


def _stand_bow(p: Pix) -> None:
    """A hunting longbow and a quiver of arrows leaning on the counter, filling the 49x158 shop slot, lit from the upper left."""
    tip_top, tip_bot, ctrl = (41.0, 3.0), (22.0, 155.0), (6.0, 76.0)
    stave = bez(tip_top, ctrl, tip_bot, 160)
    wide = taper(2.8, 2.8, 160, mid=7.6)
    # quiver first, so the stave and string lie in front of it where they cross
    q_base, q_mouth = (38.0, 152.0), (43.0, 90.0)
    _quiver(p, q_base, q_mouth)
    stroke(p, stave, wide, YEW)
    grain(p, stave, wide, YEW, 2)
    # leather grip at the middle, with a brass ring above and below
    mid = stave[80]
    wrap_grip(p, (mid[0] + 0.8, mid[1] - 12), (mid[0] - 0.6, mid[1] + 12), 7)
    # bone nocks and the bowstring on the chord
    nock_tip(p, tip_top, stave[8])
    nock_tip(p, tip_bot, stave[-9])
    string(p, (tip_top[0] + 1, tip_top[1] + 1), (tip_bot[0] + 1, tip_bot[1] - 1))
    p.line(round(tip_top[0] + 2), round(tip_top[1] + 2), round(tip_bot[0] + 2), round(tip_bot[1] - 1), mix(LINEN[1], SHADOW, 0.3))
    # a pair of spare strings wound as a loop hanging from the grip (small readable detail)
    p.px(round(mid[0] + 5), round(mid[1] + 3), BRASS[3])


def _quiver(p: Pix, base: tuple[float, float], mouth: tuple[float, float]) -> None:
    """A tapered leather quiver leaning to the right, arrows bristling from its mouth with their fletching in the light."""
    # arrows first (they go inside the quiver): tails up, three of them fanned
    for k, (dx, top_y) in enumerate(((-4, 46), (1, 40), (6, 52))):
        tail = (mouth[0] + dx + 1.5, float(top_y))
        inner = (mouth[0] + dx * 0.4, mouth[1] + 4)
        arrow(p, tail, inner, vane=2, show_head=False,
              fletch=((rgb("#d9cfae"), rgb("#b8ab88"), WINE[3]) if k != 1 else (rgb("#b8ab88"), rgb("#d9cfae"), WINE[2])))
    n = 70
    pts = [(base[0] + (mouth[0] - base[0]) * i / (n - 1), base[1] + (mouth[1] - base[1]) * i / (n - 1)) for i in range(n)]
    widths = [7.5 + 3.5 * i / (n - 1) for i in range(n)]  # a little wider at the mouth
    stroke(p, pts, widths, LEATHER)
    # stitched seam, brass band at the mouth, iron tip at the foot
    for i in range(6, n - 4, 5):
        x, y = pts[i]
        p.px(round(x + widths[i] * 0.22), round(y), LEATHER[3])
    mx, my = pts[-4]
    p.hline(round(mx - widths[-4] / 2 + 1), round(my), round(widths[-4] - 1), BRASS[2])
    p.hline(round(mx - widths[-4] / 2 + 1), round(my) - 1, round(widths[-4] - 2), BRASS[3])
    fx, fy = pts[3]
    p.hline(round(fx - 3), round(fy), 6, IRON[3])
    # a strap running up the front
    for i in range(10, n - 14, 1):
        x, y = pts[i]
        p.px(round(x - widths[i] * 0.18), round(y), LEATHER[0])


def bow_object() -> Image.Image:
    p = Pix(49, 158, seed=130)
    _stand_bow(p)
    return p.im


def bow_shadow() -> Image.Image:
    """The shadow layer drawn behind the bow: the same silhouette in near-black violet, and a softer cast shape beside it."""
    obj = bow_object()
    a = obj.getchannel("A")
    p = Pix(49, 158, seed=131)
    # cast shadow: the silhouette pushed to the lower left, translucent
    cast = Image.new("RGBA", obj.size, (0, 0, 0, 0))
    solid = Image.new("RGBA", obj.size, (26, 17, 32, 150))
    cast.paste(solid, (-4, 2), a)
    cast.paste(solid, (-3, 1), a)
    p.im.alpha_composite(cast)
    body = Image.new("RGBA", obj.size, (0, 0, 0, 0))
    body.paste(Image.new("RGBA", obj.size, (35, 28, 44, 255)), (0, 0), a)
    p.im.alpha_composite(body)
    # a lit edge on the upper left of each shape, as the original shadow object has
    for y in range(158):
        for x in range(49):
            if a.getpixel((x, y)) and (x == 0 or not a.getpixel((x - 1, y))) and a.getpixel((min(48, x + 3), y)):
                p.px(x, y, (50, 43, 60))
    return p.im


# --------------------------------------------------------------------------- the release burst


def release_burst() -> Image.Image:
    """Where a gun flash would be: a star of dust, a hot spark where the arrow leaves, a shiver of the string and feathers."""
    p = Pix(173, 156, seed=140)
    rng = random.Random(14)
    cx, cy = 86, 78

    def star(rx: float, ry: float, lo: float, spikes: int, col: tuple[int, int, int], seed: int) -> None:
        r = random.Random(seed)
        pts = []
        for i in range(spikes * 2):
            ang = math.tau * i / (spikes * 2)
            k = r.uniform(0.85, 1.0) if i % 2 == 0 else r.uniform(lo, lo + 0.18)
            pts.append((round(cx + math.cos(ang) * rx * k), round(cy + math.sin(ang) * ry * k)))
        p.poly(pts, col)

    star(85, 76, 0.5, 38, rgb("#8a3a24"), 1)           # outer rust-red streaks
    star(72, 65, 0.45, 34, rgb("#c96f45"), 2)          # dusty orange
    star(58, 52, 0.45, 30, rgb("#e0a46a"), 3)          # sunlit dust
    star(42, 38, 0.5, 26, PARCHMENT[3], 4)             # pale body of the puff
    star(26, 24, 0.55, 20, PARCHMENT[4], 5)            # hot centre
    # dust grain: dithered darker flecks in the outer ring, so it reads as a cloud and not as a flat star
    for _ in range(420):
        ang, rad = rng.uniform(0, math.tau), rng.uniform(0.42, 0.95)
        x, y = round(cx + math.cos(ang) * 84 * rad), round(cy + math.sin(ang) * 75 * rad)
        if p.get(x, y)[3]:
            p.px(x, y, rng.choice((rgb("#8a3a24"), rgb("#c96f45"), rgb("#b9855a"))))
    # the string's shiver: three zigzag lines crossing the burst, thinning outward
    for off, amp, col in ((-9, 4, rgb('#6a4a2c')), (0, 6, rgb('#4a2e1c')), (10, 3, rgb('#6a4a2c'))):
        prev = None
        for x in range(8, 165, 4):
            y = cy + off + (amp if (x // 4) % 2 else -amp) * (1 - abs(x - cx) / 90) * (1 if abs(x - cx) < 85 else 0)
            if prev:
                p.line(prev[0], prev[1], x, round(y), col)
            prev = (x, round(y))
    # feathers flung out of the burst, each a short quill with a cream vane
    for ang, ln in ((-2.6, 78), (0.5, 76), (2.0, 70), (-0.6, 80)):
        qx, qy = cx + math.cos(ang) * ln * 0.55, cy + math.sin(ang) * ln * 0.55
        ex, ey = cx + math.cos(ang) * ln, cy + math.sin(ang) * ln
        nx, ny = -math.sin(ang), math.cos(ang)
        mx, my = (qx + ex) / 2, (qy + ey) / 2
        p.poly([(round(qx), round(qy)), (round(mx + nx * 4), round(my + ny * 4)), (round(ex), round(ey)), (round(mx - nx * 3), round(my - ny * 3))], PARCHMENT[4])
        p.line(round(qx), round(qy), round(ex), round(ey), rgb("#a88a5a"))
        p.line(round(qx - math.cos(ang) * 6), round(qy - math.sin(ang) * 6), round(qx), round(qy), rgb("#8a6a40"))
    for _ in range(70):
        ang = rng.uniform(0, math.tau)
        r0, r1 = rng.uniform(0.82, 0.92), rng.uniform(0.96, 1.0)
        p.line(round(cx + math.cos(ang) * 86 * r0), round(cy + math.sin(ang) * 77 * r0), round(cx + math.cos(ang) * 86 * r1), round(cy + math.sin(ang) * 77 * r1), rgb("#8a3a24"))
    # the spark where the arrow leaves: a small hard cross of light
    for d in range(1, 15):
        c = FLAME[4] if d < 8 else FLAME[3]
        for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if d < (15 if sx else 10):
                p.px(cx + sx * d, cy + sy * d, c)
    p.ellipse(cx - 5, cy - 5, 11, 11, FLAME[4])
    p.ellipse(cx - 3, cy - 3, 7, 7, rgb("#fffbe8"))
    return p.im


# --------------------------------------------------------------------------- item pictures


def longbow_item() -> Image.Image:
    """A strung hunting longbow lying flat, with two arrows laid under it (112x48)."""
    p = Pix(112, 48, seed=150)
    a, b, c = (4.0, 32.0), (108.0, 32.0), (56.0, -30.0)
    stave = bez(a, c, b, 160)
    w = taper(2.4, 2.4, 160, mid=6.2)
    # arrows first, under the stave
    arrow(p, (14.0, 39.0), (98.0, 38.0), vane=3, head_len=6)
    arrow(p, (100.0, 45.0), (22.0, 44.0), vane=2, head_len=5, fletch=(PARCHMENT[2], PARCHMENT[3], WINE[2]))
    stroke(p, stave, w, YEW)
    grain(p, stave, w, YEW, 2)
    wrap_grip(p, (47.0, 4.0), (65.0, 4.0), 7)
    nock_tip(p, a, stave[8])
    nock_tip(p, b, stave[-9])
    string(p, (a[0] + 1, a[1] + 1), (b[0] - 1, b[1] + 1))
    p.line(5, 34, 107, 34, mix(LINEN[1], SHADOW, 0.3))
    return p.im


def crossbow_item() -> Image.Image:
    """A spanned heavy crossbow seen from above: tiller, steel prod, drawn string and a bolt on the rail (112x48)."""
    p = Pix(112, 48, seed=151)
    # steel prod across the front, bowed forward
    prod = bez((76.0, 2.0), (98.0, 24.0), (76.0, 46.0), 90)
    stroke(p, prod, taper(2.5, 2.5, 90, mid=6.5), IRON)
    for i in range(10, 80, 14):
        x, y = prod[i]
        p.px(round(x), round(y), BRASS[3])
    # tiller: a tapering oak stock
    n = 60
    pts = [(3 + 100 * i / (n - 1), 24.0) for i in range(n)]
    wd = [12.0 - 5.0 * (i / (n - 1)) ** 1.5 if i < 30 else 6.0 for i in range(n)]
    stroke(p, pts, wd, WOOD)
    for x in range(8, 90, 9):
        p.px(x, 22, WOOD[4])
        p.px(x + 4, 25, WOOD[0])
    # bolt rail with the bolt resting in it, a brass cheek plate and a stirrup ring at the front
    p.hline(34, 22, 70, OAK[0])
    p.hline(34, 26, 70, OAK[0])
    arrow(p, (34.0, 24.0), (106.0, 24.0), vane=3, head_len=6)
    p.rect(3, 19, 4, 10, BRASS[1])
    p.vline(3, 19, 10, BRASS[3])
    p.ellipse(100, 18, 10, 12, IRON[1])
    p.ellipse(102, 20, 6, 8, (0, 0, 0, 0))
    p.draw.arc((100, 18, 109, 29), 120, 330, fill=IRON[3])
    # lock: brass nut and a short trigger
    p.rect(44, 28, 8, 4, IRON[2])
    p.rect(40, 18, 8, 3, BRASS[2])
    # the string, drawn back from the prod tips to the nut
    string(p, (76, 3), (36, 24))
    string(p, (76, 45), (36, 24))
    p.px(35, 24, BRASS[4])
    return p.im


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "shotgun_shadow.49x158.png": bow_object,
    "shotgun_shadow_only.49x158.png": bow_shadow,
    "muzzleflash2.173x156.png": release_burst,
    "items~items_weapons_ranged_antique@shotgun.png": longbow_item,
    "items~items_weapons_ranged_antique@heavy_smg.png": crossbow_item,
}
