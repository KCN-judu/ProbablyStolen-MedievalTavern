"""Things worn on the head and over the face: coifs, caps, hats, helmets, hoods, veils and masks.

Each piece is a mask shaped from the head's geometry and lit like a dome; the cloth ones get fold lines, the iron ones
rivets. `Look.headwear` names the piece, `Look.head_col` its cloth (the outfit's colour when empty).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from palette import FLAME
from people_kit import Mask, blank, both, grow, hx, minus, oval, poly, rect, shrink, union, tone
from people_look import Look
from pface_core import curve, dome, fill, flat, hl, inside, pixels, trace, vl
from pface_hair import STYLES, Style, hair_mask
from pface_head import CX, Geo, half_width, head_mask, skin_ramp
from pix import Pix, Ramp, mix, rgb

CLOTH_CUTS = (0.04, 0.42, 0.88, 1.18)
IRON: Ramp = tone(rgb("#6d6c78"))
BRASS: Ramp = tone(rgb("#c8a040"))
STRAW: Ramp = tone(rgb("#cdaa5a"))
LEATHER: Ramp = tone(rgb("#6a4228"))


def cloth(p: Pix, m: Mask, ramp: Ramp, g: Geo, rx: float, cy: float | None = None, ry: float | None = None, texture: float = 0.12,
          cx: float = CX - 3) -> None:
    """Fills a mask as cloth over a dome."""
    fill(p, m, ramp, dome(cx, cy if cy is not None else g.sk + 4, rx, ry if ry is not None else g.H * 0.48, flat=0.2), cuts=CLOTH_CUTS, texture=texture)


def rim_light(p: Pix, m: Mask, ramp: Ramp) -> None:
    """A highlight on the upper left edge of a mask, a shadow on the lower right: the rim that makes a piece stand off."""
    for x, y in pixels(m):
        if not inside(m, x - 1, y - 1) and (x < CX + 6) and not inside(m, x, y - 1):
            p.px(x, y, ramp[4] if x < CX - 4 else ramp[3])
        if not inside(m, x + 1, y + 1) and x > CX + 4 and not inside(m, x + 1, y):
            p.px(x, y, ramp[0])


def cap_style(vt: int, vs: int, line: float, sb: int, ear: int) -> Style:
    return Style(vt, vs, line, sb, ear)


def brow_shadow(p: Pix, look: Look, g: Geo, m: Mask, depth: int = 2) -> None:
    """Under a hat's edge the forehead falls into shade."""
    sk = skin_ramp(look)
    head = head_mask(look)
    for x, y in pixels(m):
        for d in range(1, depth + 1):
            if not inside(m, x, y + 1) and inside(head, x, y + d) and not inside(m, x, y + d):
                p.px(x, y + d, mix(sk[1], sk[0], 0.4) if d == 1 else sk[1])


def coif(p: Pix, look: Look, g: Geo, ramp: Ramp, tall: bool = False) -> None:
    """A linen coif tied under the chin: it covers the hair and ears, with a seam over the crown."""
    m = hair_mask(look, g, cap_style(4, 3, 0.17, 7, 15))
    cloth(p, m, ramp, g, g.w / 2 + 4)
    trace(p, curve((CX - 2, g.sk - 3), (CX + 3, g.sk + 8), (CX + 5, g.sk + 16), 12), ramp[1], m)
    rim_light(p, m, ramp)
    hw = g.w // 2
    for s in (-1, 1):
        pts = curve((CX + s * (hw - 1), g.eye + 14), (CX + s * (hw - 4), g.chin + 2), (CX + s * 4, g.chin + 3), 10)
        trace(p, pts, ramp[1], None)
        trace(p, [(x, y - 1) for x, y in pts], ramp[3], None)
    p.rect(CX - 2, g.chin + 2, 5, 3, ramp[2])
    p.px(CX - 2, g.chin + 2, ramp[4])
    p.px(CX + 2, g.chin + 4, ramp[0])
    brow_shadow(p, look, g, m)


def cap(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A round wool cap with a turned-up band."""
    m = hair_mask(look, g, cap_style(8, 4, 0.14, 3, -1))
    cloth(p, m, ramp, g, g.w / 2 + 4, texture=0.16)
    band = both(m, rect(0, g.sk + round(g.H * 0.14) - 5, 287, 259))
    fill(p, band, ramp, dome(CX - 3, g.sk + 12, g.w / 2 + 4, 12), cuts=CLOTH_CUTS, texture=0.2)
    hl(p, CX - g.w // 2 - 4, g.sk + round(g.H * 0.14) - 5, g.w + 8, ramp[0]) if False else None
    for x, y in pixels(band):
        if not inside(band, x, y - 1):
            p.px(x, y, ramp[1])
            p.px(x, y + 1, ramp[4]) if x < CX - 6 else None
    trace(p, curve((CX - 12, g.sk - 4), (CX, g.sk - 8), (CX + 14, g.sk - 3), 10), ramp[3], m)
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, band)


def beret(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A slouching beret tipped to one side, with a nub on top and a thin band."""
    hw = g.w // 2
    m = union(oval(CX + 3, g.sk - 2, hw + 8, 11), both(oval(CX + 6, g.sk + 8, hw + 5, 8), rect(0, 0, 287, g.sk + 7)))
    m = minus(m, rect(0, g.sk + round(g.H * 0.14) + 1, 287, 259))
    cloth(p, m, ramp, g, hw + 9, g.sk, 11, texture=0.2, cx=CX + 2)
    p.rect(CX + 8, g.sk - 13, 3, 3, ramp[1])
    p.px(CX + 8, g.sk - 13, ramp[3])
    # radial folds from the nub
    for i in range(5):
        trace(p, curve((CX + 9, g.sk - 10), (CX + 9 - 10 + i * 5, g.sk - 4), (CX - hw + 4 + i * 12, g.sk + 7), 8), ramp[3] if i % 2 else ramp[1], m)
    band = both(m, rect(0, g.sk + round(g.H * 0.14) - 2, 287, 259))
    fill(p, band, ramp, dome(CX - 3, g.sk + 12, hw + 4, 10), cuts=(0.2, 0.5, 0.95, 1.25))
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, m)


def flat_cap(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A flat cap: a low puffed crown and a short stiff peak."""
    hw = g.w // 2
    m = hair_mask(look, g, cap_style(5, 5, 0.16, 2, -2))
    cloth(p, m, ramp, g, hw + 6, texture=0.2)
    brim = both(oval(CX - 2, g.sk + round(g.H * 0.16), hw + 5, 4), rect(0, g.sk + round(g.H * 0.12), 287, 259))
    fill(p, brim, ramp, dome(CX - 4, g.sk + 10, hw + 8, 9), cuts=(0.3, 0.6, 1.0, 1.3))
    for x, y in pixels(brim):
        if not inside(brim, x, y + 1):
            p.px(x, y, ramp[0])
    trace(p, curve((CX - hw, g.sk + 1), (CX, g.sk - 4), (CX + hw, g.sk + 3), 12), ramp[3], m)
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, brim, 3)


def toque(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A cook's tall linen toque, pleated, with a puffed top."""
    hw = g.w // 2
    base_y = g.sk + round(g.H * 0.14)
    band = rect(CX - hw - 1, base_y - 8, CX + hw, base_y)
    crown = oval(CX, g.sk - 17, hw + 7, 11)
    stem = rect(CX - hw + 1, g.sk - 16, CX + hw - 2, base_y - 8)
    m = union(band, crown, stem)
    cloth(p, m, ramp, g, hw + 7, g.sk - 8, 22, texture=0.1)
    for x in range(CX - hw + 3, CX + hw - 2, 4):               # pleats
        trace(p, [(x, g.sk - 12), (x + (1 if x > CX else -1), base_y - 9)], ramp[1], m)
        trace(p, [(x - 1, g.sk - 12), (x - 1 + (1 if x > CX else -1), base_y - 9)], ramp[3], m)
    hl(p, CX - hw - 1, base_y - 8, 2 * hw + 2, ramp[1])
    hl(p, CX - hw - 1, base_y - 7, 2 * hw + 2, ramp[3])
    hl(p, CX - hw - 1, base_y, 2 * hw + 2, ramp[0])
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, band, 2)


def skullcap(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A close skullcap with a seamed crown."""
    m = hair_mask(look, g, cap_style(3, 1, 0.17, 2, -3))
    cloth(p, m, ramp, g, g.w / 2 + 2, texture=0.14)
    for dx in (-8, 0, 8):
        trace(p, curve((CX + dx // 2, g.sk - 2), (CX + dx, g.sk + 3), (CX + dx * 2, g.sk + 12), 8), ramp[1], m)
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, m)


def kerchief(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A cloth tied over the head with a knot and two tails at the side."""
    hw = g.w // 2
    m = hair_mask(look, g, cap_style(4, 2, 0.19, 3, 0))
    cloth(p, m, ramp, g, hw + 3, texture=0.16)
    for i in range(7):
        x0 = CX - hw + 4 + i * 5
        trace(p, curve((CX + 2, g.sk - 2), (x0, g.sk + 3), (x0 + 3 - i, g.sk + round(g.H * 0.18)), 8), ramp[3] if i % 2 else ramp[1], m)
    rim_light(p, m, ramp)
    band = both(m, rect(0, g.sk + round(g.H * 0.15), 287, 259))
    for x, y in pixels(band):
        if not inside(band, x, y - 1):
            p.px(x, y, ramp[1])
    # the knot and tails
    kx, ky = CX + hw + 1, g.eye - 3
    p.rect(kx - 1, ky - 1, 5, 4, ramp[2])
    p.px(kx - 1, ky - 1, ramp[4])
    p.px(kx + 3, ky + 2, ramp[0])
    for dx, ln in ((0, 9), (3, 6)):
        for i in range(ln):
            p.px(kx + dx + (i // 3), ky + 3 + i, ramp[2] if dx == 0 else ramp[1])
            p.px(kx + dx + (i // 3) + 1, ky + 3 + i, ramp[1] if dx == 0 else ramp[0])
    brow_shadow(p, look, g, band)


def bonnet(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A woman's linen bonnet: it frames the face with a frill and ties under the chin."""
    m = hair_mask(look, g, cap_style(6, 4, 0.15, 6, 12))
    cloth(p, m, ramp, g, g.w / 2 + 6, texture=0.12)
    edge = minus(m, shrink(m, 2))
    for x, y in pixels(edge):
        if y > g.sk + 5:
            p.px(x, y, ramp[4] if (x + y) % 2 == 0 else ramp[3])
    for x, y in pixels(m):
        if not inside(m, x, y + 1) and y < g.eye - 2:
            p.px(x, y, ramp[1])
    rim_light(p, m, ramp)
    trace(p, curve((CX - 2, g.sk - 3), (CX + 4, g.sk + 8), (CX + 8, g.sk + 16), 12), ramp[1], m)
    brow_shadow(p, look, g, m)


def headband(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A twisted cloth headband with a knot at the side and short tails."""
    hw = g.w // 2
    y0 = g.sk + round(g.H * 0.13)
    m = both(union(grow(head_mask(look), 1), oval(CX, g.sk + 10, hw + 2, 13)), rect(0, y0, 287, y0 + 4))
    cloth(p, m, ramp, g, hw + 2, y0, 6, texture=0.12)
    for x in range(CX - hw, CX + hw, 5):
        if inside(m, x, y0 + 2):
            p.px(x, y0 + 1, ramp[3])
            p.px(x + 2, y0 + 3, ramp[1])
    kx = CX + hw - 1
    p.rect(kx - 1, y0, 4, 5, ramp[2])
    for dx, ln in ((1, 9), (3, 6)):
        for i in range(ln):
            p.px(kx + dx + i // 4, y0 + 5 + i, ramp[2] if dx == 1 else ramp[1])


def wide(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A broad-brimmed felt hat with a band and a feather."""
    hw = g.w // 2
    by = g.sk + round(g.H * 0.15)
    crown = both(union(oval(CX, g.sk - 2, hw - 1, 11), rect(CX - hw + 1, g.sk - 2, CX + hw - 2, by)), rect(0, 0, 287, by))
    cloth(p, crown, ramp, g, hw + 2, g.sk - 4, 16, texture=0.1)
    brim = oval(CX, by, hw + 18, 6)
    fill(p, brim, ramp, dome(CX - 6, by - 3, hw + 20, 10, flat=0.3), cuts=(0.2, 0.55, 0.95, 1.25), texture=0.08)
    # the brim edge and the underside shadow onto the forehead
    for x, y in pixels(brim):
        if not inside(brim, x, y + 1):
            p.px(x, y, ramp[0])
    flat(p, both(brim, rect(0, by, 287, 259)), ramp[1])
    for x, y in pixels(both(brim, rect(0, by, 287, 259))):
        if (x + y) % 3 == 0:
            p.px(x, y, ramp[2])
    p.px(CX - hw - 17, by, ramp[3])
    # crown back over brim
    cloth(p, both(crown, rect(0, 0, 287, by - 1)), ramp, g, hw + 2, g.sk - 4, 16, texture=0.1)
    hb = rect(CX - hw + 1, by - 5, CX + hw - 2, by - 2)
    flat(p, both(hb, crown), mix(ramp[1], (30, 20, 24), 0.4))
    hl(p, CX - hw + 1, by - 5, 2 * hw - 2, ramp[3] if False else mix(ramp[2], (210, 170, 70), 0.5))
    # a feather sweeping back from the band
    for i in range(18):
        t = i / 17
        x = round(CX + 8 + 20 * t)
        y = round(by - 4 - 14 * math.sin(t * 2.3) )
        p.px(x, y, (196, 64, 52) if i % 3 else (232, 120, 90))
        p.px(x, y + 1, (140, 44, 48))
        p.px(x + 1, y + 1, (140, 44, 48))
    rim_light(p, crown, ramp)
    brow_shadow(p, look, g, brim, 4)


def straw(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A woven straw hat: a wide brim with rows of plait, a low crown with a cord."""
    hw = g.w // 2
    by = g.sk + round(g.H * 0.14)
    crown = both(union(oval(CX, g.sk, hw, 11), rect(CX - hw, g.sk, CX + hw - 1, by)), rect(0, 0, 287, by))
    brim = oval(CX, by, hw + 22, 7)
    fill(p, brim, STRAW, dome(CX - 6, by - 3, hw + 24, 10, flat=0.3), cuts=(0.2, 0.55, 0.95, 1.25), texture=0.1)
    for x, y in pixels(brim):
        if (y + (x // 4)) % 3 == 0:
            p.px(x, y, STRAW[1] if x > CX else STRAW[3])
        if not inside(brim, x, y + 1):
            p.px(x, y, STRAW[0])
    cloth(p, crown, STRAW, g, hw + 2, g.sk, 14, texture=0.1)
    for y in range(g.sk - 10, by, 2):
        for x, yy in pixels(both(crown, rect(0, y, 287, y))):
            if (x // 3 + y) % 2 == 0:
                p.px(x, yy, STRAW[1] if x > CX - 4 else STRAW[3])
    flat(p, both(rect(CX - hw, by - 4, CX + hw - 1, by - 2), crown), ramp[2] if ramp is not STRAW else LEATHER[2])
    rim_light(p, crown, STRAW)
    brow_shadow(p, look, g, brim, 4)


def kettle(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """An iron kettle hat: a domed crown, a down-turned brim, rivets, and a leather chin strap."""
    hw = g.w // 2
    by = g.sk + round(g.H * 0.12)
    crown = both(union(oval(CX, g.sk + 2, hw + 3, 14), rect(CX - hw - 2, g.sk + 2, CX + hw + 1, by)), rect(0, 0, 287, by))
    brim = oval(CX, by, hw + 11, 5)
    fill(p, brim, IRON, dome(CX - 6, by - 4, hw + 13, 9, flat=0.3), cuts=(0.15, 0.5, 0.95, 1.25))
    flat(p, both(brim, rect(0, by + 1, 287, 259)), IRON[1])
    for x, y in pixels(brim):
        if not inside(brim, x, y + 1):
            p.px(x, y, IRON[0])
    fill(p, crown, IRON, dome(CX - 8, g.sk + 2, hw + 4, 16, flat=0.1), cuts=(0.12, 0.5, 0.95, 1.2), texture=0.06)
    # a reflected band of sky along the dome, hammered facets
    for i in range(4):
        trace(p, curve((CX - hw + 3 + i, by - 3), (CX - hw + 6 + i * 2, g.sk - 3), (CX - 2 + i * 5, g.sk - 11), 8), IRON[4] if i == 0 else IRON[3], crown)
    flat(p, both(rect(CX - hw - 2, by - 3, CX + hw + 1, by - 2), crown), IRON[1])
    for x in range(CX - hw + 2, CX + hw - 1, 8):
        p.px(x, by - 4, BRASS[4])
        p.px(x + 1, by - 3, BRASS[1])
    p.px(CX - 1, g.sk - 12, IRON[4])
    rim_light(p, crown, IRON)
    brow_shadow(p, look, g, brim, 3)
    sk = skin_ramp(look)
    for s in (-1, 1):
        for y in range(by + 2, g.mouth + 6):
            x = CX + s * (round(half_width(g, y)) - 1) - (1 if s < 0 else 0)
            p.px(x, y, LEATHER[2] if s < 0 else LEATHER[1])
    hl(p, CX - 6, g.chin + 1, 12, LEATHER[1])


def hood_mass(look: Look, g: Geo, sw: int) -> tuple[Mask, Mask]:
    """(cloth, opening): a hood around the head with its cowl over the shoulders, and the hole the face looks through."""
    hw = g.w // 2
    outer = union(oval(CX, g.sk + g.H * 0.3, hw + 10, g.H * 0.5),
                  poly([(CX - hw - 8, g.eye), (CX + hw + 8, g.eye), (CX + hw + 30, g.chin + 40), (CX - hw - 30, g.chin + 40)]))
    # the cowl falls to a V at the chest
    v = poly([(CX - 14, g.chin + 4), (CX + 14, g.chin + 4), (CX + 3, g.chin + 44), (CX - 3, g.chin + 44)])
    head = head_mask(look)
    opening = both(union(grow(head, 1), oval(CX, g.chin - 8, hw - 1, 14)), rect(0, g.sk + round(g.H * 0.10), 287, g.chin + 2))
    opening = union(opening, v)
    return minus(outer, opening), opening


def hood(p: Pix, look: Look, g: Geo, ramp: Ramp, sw: int) -> None:
    """A deep hood: dark cloth around the face, the inner edge in shadow, the cowl falling in folds."""
    m, opening = hood_mass(look, g, sw)
    hw = g.w // 2
    fill(p, m, ramp, dome(CX - 6, g.sk + 6, hw + 14, g.H * 0.7, flat=0.3), cuts=CLOTH_CUTS, texture=0.16)
    for i in range(5):                          # folds of the cowl
        sgn = -1 if i % 2 == 0 else 1
        x = CX + sgn * (hw + 8 + (i // 2) * 8)
        trace(p, curve((x, g.eye + 6), (x + sgn * 4, g.chin + 10), (x + sgn * 8, g.chin + 38), 12), ramp[1], m)
        trace(p, curve((x - 1, g.eye + 6), (x + sgn * 4 - 1, g.chin + 10), (x + sgn * 8 - 1, g.chin + 38), 12), ramp[3], m)
    # inner edge: a lit lip on the left, a deep shade on the right and across the top
    inner = minus(grow(opening, 1), opening)
    for x, y in pixels(inner):
        if inside(m, x, y):
            p.px(x, y, ramp[3] if x < CX - 6 else ramp[0])
    sk = skin_ramp(look)
    head = head_mask(look)
    for x, y in pixels(opening):
        if inside(head, x, y) and (y < g.sk + round(g.H * 0.2) + 2 or x > CX + hw - 4):
            if (x + y) % 2 == 0 or y < g.sk + round(g.H * 0.2):
                p.px(x, y, sk[0] if y < g.sk + round(g.H * 0.2) else sk[1])
    # a darker brow band so the face reads as deep inside
    rim_light(p, m, ramp)


def jester(p: Pix, look: Look, g: Geo, ramp: Ramp, ramp2: Ramp) -> None:
    """A jester's cap: a hood with two long floppy horns ending in brass bells."""
    hw = g.w // 2
    m = hair_mask(look, g, cap_style(6, 3, 0.15, 3, 1))
    cloth(p, m, ramp, g, hw + 4, texture=0.1)
    for s, rp in ((-1, ramp), (1, ramp2)):
        pts = curve((CX + s * 6, g.sk), (CX + s * (hw + 26), g.sk - 20), (CX + s * (hw + 18), g.eye + 8), 20)
        for i, (x, y) in enumerate(pts):
            w = max(2, 7 - i // 4)
            for t in range(w):
                c = rp[3] if t == 0 else rp[2] if t < w - 1 else rp[1]
                p.px(round(x) - (w // 2) + t, round(y), c)
                p.px(round(x) - (w // 2) + t, round(y) + 1, c)
        bx, by = round(pts[-1][0]), round(pts[-1][1])
        p.rect(bx - 2, by, 5, 5, BRASS[2])
        p.px(bx - 2, by, BRASS[4])
        p.px(bx - 1, by + 1, BRASS[4])
        p.rect(bx - 2, by + 4, 5, 1, BRASS[0])
        p.px(bx, by + 5, BRASS[0])
    band = both(m, rect(0, g.sk + round(g.H * 0.14) - 2, 287, 259))
    fill(p, band, ramp2, dome(CX - 3, g.sk + 12, hw + 4, 10), cuts=CLOTH_CUTS)
    for x, y in pixels(band):
        if (x // 3) % 2 == 0 and not inside(band, x, y - 1):
            p.px(x, y, ramp[2])
            p.px(x, y + 1, ramp[2])
    rim_light(p, m, ramp)
    brow_shadow(p, look, g, band)


def candle_cap(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A wool cap with a tallow candle in a brass holder on the brow: a miner's or night watchman's light."""
    cap(p, look, g, ramp)
    x, y = CX - 4, g.sk - 6
    p.rect(x - 2, y + 8, 9, 3, BRASS[2])
    p.rect(x - 2, y + 8, 9, 1, BRASS[4])
    p.hline(x - 2, y + 10, 9, BRASS[0])
    p.rect(x, y + 1, 4, 8, (214, 200, 160))
    p.vline(x, y + 1, 8, (240, 230, 196))
    p.vline(x + 3, y + 1, 8, (170, 150, 110))
    p.px(x + 1, y, (60, 40, 30))
    for dy, c in ((-1, FLAME[2]), (-2, FLAME[3]), (-3, FLAME[2]), (-4, FLAME[1])):
        w = 2 if dy > -4 else 1
        for dx in range(w):
            p.px(x + 1 + dx, y + dy, c)
    p.px(x + 1, y - 2, FLAME[4])
    for dx, dy in ((-2, -2), (4, -2), (-1, -5), (3, -5)):
        p.px(x + dx, y + dy, mix(FLAME[1], (80, 50, 40), 0.5))


HEADWEAR: dict[str, Callable[..., None]] = {
    "coif": coif, "cap": cap, "beret": beret, "flat": flat_cap, "toque": toque, "skull": skullcap, "kerchief": kerchief,
    "bonnet": bonnet, "headband": headband, "wide": wide, "straw": straw, "helm": kettle, "lamp": candle_cap,
}


def draw_headwear(p: Pix, look: Look, g: Geo, ramp: Ramp, ramp2: Ramp, sw: int) -> None:
    kind = look.headwear
    if not kind:
        return
    if kind == "hood":
        hood(p, look, g, ramp, sw)
    elif kind == "jester":
        jester(p, look, g, ramp, ramp2)
    else:
        HEADWEAR[kind](p, look, g, ramp)


# ---------------------------------------------------------------------------------------------- face coverings


def face_cover(p: Pix, look: Look, g: Geo, ramp: Ramp) -> None:
    """A veil over the mouth and nose, the shade of a deep hood, or a plague doctor's beak, as `Look.face` says."""
    sk = skin_ramp(look)
    head = head_mask(look)
    hw = g.w // 2
    if look.face == "veil":
        m = both(head, rect(0, g.eye + 4, 287, 259))
        m = union(m, both(oval(CX, g.eye + 2, hw + 1, 3), rect(0, g.eye + 3, 287, g.eye + 5)))
        fill(p, m, ramp, dome(CX - 4, g.eye + 14, hw + 3, 14, flat=0.3), cuts=CLOTH_CUTS, texture=0.12)
        for x, y in pixels(m):
            if not inside(m, x, y - 1):
                p.px(x, y, ramp[1])
        trace(p, curve((CX - hw + 3, g.eye + 8), (CX, g.nose + 4), (CX + hw - 3, g.eye + 9), 12), ramp[1], m)
        trace(p, curve((CX - hw + 4, g.mouth + 3), (CX, g.mouth + 7), (CX + hw - 4, g.mouth + 3), 12), ramp[1], m)
        p.px(CX - 2, g.eye + 8, ramp[4])
        p.px(CX - 1, g.eye + 9, ramp[3])
    elif look.face == "shade":
        for x, y in pixels(head):
            if y > g.eye + 3 or (x + y) % 2 == 0:
                if y < g.eye - 1 or y > g.eye + 2:
                    p.px(x, y, sk[0] if (x + y) % 3 else (30, 20, 28))
        # only the eyes glint
        for s in (-1, 1):
            for u in (5, 6):
                x = CX + s * (g.gap + u) - (1 if s < 0 else 0)
                p.px(x, g.eye, (236, 226, 200))
    elif look.face == "plague":
        beak = union(oval(CX, g.nose - 2, 8, 13), poly([(CX - 6, g.eye + 2), (CX + 6, g.eye + 2), (CX + 2, g.chin + 12), (CX - 2, g.chin + 12)]))
        fill(p, beak, LEATHER, dome(CX - 4, g.nose - 4, 10, 20), cuts=(0.1, 0.45, 0.9, 1.2), texture=0.1)
        trace(p, [(CX, g.eye + 2), (CX, g.chin + 10)], LEATHER[0], beak)
        for s in (-1, 1):                         # round glass lenses in brass rims
            lx = CX + s * (g.gap + 5) - (1 if s < 0 else 0)
            p.ellipse(lx - 5, g.eye - 4, 11, 11, BRASS[1])
            p.ellipse(lx - 4, g.eye - 3, 9, 9, BRASS[3])
            p.ellipse(lx - 3, g.eye - 2, 7, 7, (44, 76, 86))
            p.px(lx - 2, g.eye - 1, (170, 214, 220))
            p.px(lx - 1, g.eye - 1, (120, 170, 180))
            p.px(lx + 1, g.eye + 2, (28, 50, 60))
