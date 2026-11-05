"""Garments: what each outfit of the cast is made of, from the neckline down.

Every garment is a function of a `Ctx` that paints in layers (base, panels, seams, folds, collar, fastenings). They share
the shoulder shape and the lighting of `pbody_core`, so a cook, a watchman and a guild officer differ by cut, cloth and
trim and not by drawing style.
"""

from __future__ import annotations

from collections.abc import Callable

from people_kit import SKINS, Mask, blank, both, grow, minus, oval, poly, rect, shrink, union
from pbody_core import (BRASS_R, CLOTH_CUTS, IRON_R, LEATHER_R, LINEN_R, STEEL_R, Ctx, button, drape, edge_band, fill, fold,
                        mail_texture, sag, paint_base, panel, quilt, rivet, seam, stripe, torso_light, wrinkles)
from pface_core import curve, flat, hl, inside, pixels, trace, vl
from pface_head import CX
from pix import mix


def arms(c: Ctx) -> tuple[Mask, Mask]:
    """(left sleeve, right sleeve): the parts of the torso outside the arm lines."""
    ai = c.arm_in
    left = both(c.torso, rect(0, 0, CX - ai - 1, 259))
    right = both(c.torso, rect(CX + ai, 0, 287, 259))
    return left, right


def armpits(c: Ctx, ramp=None) -> None:
    """The dark crease where each arm meets the chest, and a lit edge on the arm."""
    r = ramp or c.main
    ai = c.arm_in
    y0 = c.yn + 24
    for s in (-1, 1):
        pts = [(CX + s * (ai - 2), y0 + 2), (CX + s * (ai + 0), y0 + 18), (CX + s * (ai - 1), y0 + 40), (CX + s * (ai - 3), 259)]
        trace(c.p, pts, r[0], c.torso)
        trace(c.p, [(x + s, y) for x, y in pts], r[1], c.torso)
        if s < 0:
            trace(c.p, [(x - 2, y) for x, y in pts], r[3], c.torso)


def elbows(c: Ctx, ramp=None, seed: int = 0) -> None:
    """Creases at the bend of each arm, pointing towards the elbow."""
    r = ramp or c.main
    ai = c.arm_in
    base = c.yn + 70
    for s in (-1, 1):
        x = CX + s * (ai + 11)
        for i, dy in enumerate((0, 8, 17)):
            pts = [(x - s * 9, base + dy - 3), (x - s * 3, base + dy + 1), (x + s * 5, base + dy - 1)]
            fold(c, pts, r)


def chest_pull(c: Ctx, ramp=None) -> None:
    """Diagonal creases from the armpits across the chest, where the cloth is pulled by the arms."""
    r = ramp or c.main
    ai = c.arm_in
    for s in (-1, 1):
        for k, dy in enumerate((0, 9)):
            drape(c, CX + s * (ai - 1), c.yn + 58 + dy, CX + s * 8, c.yn + 44 + dy, s * -2, r)


def neck_open(c: Ctx, rx: int, ry: int, dy: int) -> Mask:
    """Cuts a neckline out of the torso, so the neck shows through; returns the opening."""
    hole = oval(CX, c.yn + dy, rx, ry)
    c.torso = minus(c.torso, hole)
    # inside the collar: the neck as drawn, and skin in deep shade where the neck does not reach
    sk = SKINS[c.look.skin]
    snap = c.neck.load() if c.neck is not None else None
    for x, y in pixels(hole):
        v = snap[x, y] if snap is not None else (0, 0, 0, 0)
        if v[3]:
            c.p.px(x, y, v)
        else:
            c.p.px(x, y, sk[0] if (y > c.yn + dy or abs(x - CX) > rx - 3) else sk[1])
    return hole


def skin_chest(c: Ctx, m: Mask) -> None:
    """Bare skin in a neckline, lit like the chest."""
    sk = SKINS[c.look.skin]
    fill(c.p, m, sk, lambda x, y: 0.62 + 0.3 * (-(x - CX)) / 40 - 0.02 * (y - c.yn), cuts=(0.1, 0.38, 0.95, 1.2))


def cuffs(c: Ctx, ramp, y: int = 197, h: int = 9, band=None) -> None:
    """A band at each wrist (cuffs, bracers), lit."""
    l, r = arms(c)
    for m in (l, r):
        zone = both(m, rect(0, y, 287, y + h - 1))
        fill(c.p, zone, ramp, torso_light(c), cuts=CLOTH_CUTS)
        for x, yy in pixels(zone):
            if yy == y:
                c.p.px(x, yy, ramp[3])
            elif yy == y + h - 1:
                c.p.px(x, yy, ramp[0])
    if band is not None:
        for m in (l, r):
            for x, yy in pixels(both(m, rect(0, y + 4, 287, y + 4))):
                if (x // 2) % 2 == 0:
                    c.p.px(x, yy, band[3])


def belt(c: Ctx, y: int, ramp=None, buckle: bool = True, w: int = 6) -> None:
    """A leather belt across the torso with a brass buckle (and hanging end) at the middle."""
    r = ramp or LEATHER_R
    zone = both(c.torso, rect(CX - c.arm_in - 1, y, CX + c.arm_in, y + w - 1))
    fill(c.p, zone, r, torso_light(c), cuts=CLOTH_CUTS)
    for x, yy in pixels(zone):
        if yy == y:
            c.p.px(x, yy, r[3])
        elif yy == y + w - 1:
            c.p.px(x, yy, r[0])
    if buckle:
        bx = CX - 3
        c.p.rect(bx, y - 1, 8, w + 2, BRASS_R[2])
        c.p.rect(bx + 2, y + 1, 4, w - 2, r[1])
        c.p.rect(bx, y - 1, 8, 1, BRASS_R[4])
        c.p.vline(bx, y - 1, w + 2, BRASS_R[3])
        c.p.vline(bx + 7, y - 1, w + 2, BRASS_R[1])
        c.p.hline(bx, y + w, 8, BRASS_R[0])
        c.p.px(bx + 3, y + 2, r[3])


def rope_belt(c: Ctx, y: int, ramp=None) -> None:
    """A twisted cord belt with a knot and two ends."""
    r = ramp or tone_of("#c8b890")
    zone = both(c.torso, rect(CX - c.arm_in - 1, y, CX + c.arm_in, y + 3))
    for x, yy in pixels(zone):
        c.p.px(x, yy, r[3] if (x + yy) % 3 else r[1])
        if yy == y + 3:
            c.p.px(x, yy, r[0])
    for i in range(14):
        c.p.px(CX - 4 + i // 4, y + 3 + i, r[2] if i % 3 else r[3])
        c.p.px(CX + 1 + i // 5, y + 3 + i, r[1] if i % 3 else r[3])
    c.p.rect(CX - 3, y - 1, 6, 5, r[2])
    c.p.rect(CX - 3, y - 1, 6, 1, r[4])
    c.p.rect(CX - 3, y + 3, 6, 1, r[0])


def tone_of(code: str):
    from people_kit import hx
    return hx(code)


def placket(c: Ctx, x: int, y0: int, y1: int, ramp, spacing: int = 12, buttons: bool = True, bt=BRASS_R) -> None:
    """A front opening with a seam and a row of buttons."""
    trace(c.p, [(x, y0), (x, y1)], ramp[0], c.torso)
    trace(c.p, [(x - 1, y0), (x - 1, y1)], ramp[3], c.torso)
    if buttons:
        for y in range(y0 + 6, y1 - 3, spacing):
            button(c.p, x - 5, y, bt)
            trace(c.p, [(x - 5, y + 2), (x - 3, y + 2)], ramp[0], c.torso)


def stain(c: Ctx, kind: str) -> None:
    """Flour dust, soot smears or blood on the cloth."""
    rng = c.rng
    cols = {"flour": [(232, 224, 206)], "soot": [(38, 30, 32), (58, 46, 44)], "blood": [(122, 30, 36), (90, 24, 32)]}[kind]
    for _ in range({"flour": 70, "soot": 40, "blood": 22}[kind]):
        x = CX + rng.randint(-c.sw + 20, c.sw - 20)
        y = rng.randint(c.yn + 28, 205)
        if inside(c.torso, x, y):
            c.p.px(x, y, rng.choice(cols))
            if rng.random() < 0.4:
                c.p.px(x + 1, y, rng.choice(cols))


# ---------------------------------------------------------------------------------------------- garments


def tunic(c: Ctx) -> None:
    """A plain wool tunic: round neck with a contrasting band, side folds, a belt, rolled cuffs."""
    hole = neck_open(c, c.nk + 4, 9, 3)
    paint_base(c, texture=0.14)
    armpits(c)
    chest_pull(c)
    elbows(c)
    ring = minus(grow(hole, 2), hole)
    fill(c.p, both(ring, c.torso), c.second, torso_light(c), cuts=CLOTH_CUTS)
    skin_chest(c, minus(hole, oval(CX, c.yn - 8, c.nk + 6, 8)))
    # the slit and lace at the throat
    trace(c.p, [(CX, c.yn + 12), (CX, c.yn + 26)], c.main[0], c.torso)
    for y in (c.yn + 14, c.yn + 19, c.yn + 24):
        hl(c.p, CX - 2, y, 5, c.second[3])
    belt(c, 199)
    cuffs(c, c.second, 197, 9)
    wrinkles(c, (CX - 40, c.yn + 40, CX + 30, 195), c.main, 7)


def jerkin(c: Ctx) -> None:
    """A leather jerkin laced over a linen shirt: shirt sleeves and collar, the vest with its V opening and side laces."""
    shirt = c.second
    paint_base(c, ramp=shirt, texture=0.12)
    armpits(c, shirt)
    elbows(c, shirt)
    ai = c.arm_in
    vest = both(c.torso, rect(CX - ai - 4, 0, CX + ai + 3, 259))
    v_open = poly([(CX - 7, c.yn - 2), (CX + 7, c.yn - 2), (CX + 1, c.yn + 36), (CX - 1, c.yn + 36)])
    body = minus(vest, v_open)
    # armholes cut diagonally from shoulder to armpit
    body = minus(body, poly([(CX - ai - 5, c.yn), (CX - ai - 5, c.yn + 24), (CX - ai + 3, c.yn + 6)]),
                 poly([(CX + ai + 4, c.yn), (CX + ai + 4, c.yn + 24), (CX + ai - 3, c.yn + 6)]))
    panel(c, body, c.main, texture=0.16)
    for s in (-1, 1):                              # lapel edges
        trace(c.p, [(CX + s * 8, c.yn - 1), (CX + s * 1, c.yn + 35)], c.main[0], c.torso)
        trace(c.p, [(CX + s * 7 - 1, c.yn - 1), (CX + s * 0 - 1, c.yn + 35)], c.main[3] if s < 0 else c.main[1], c.torso)
    neck = neck_open(c, c.nk + 2, 7, 1)
    ring = minus(grow(neck, 2), neck)
    fill(c.p, both(ring, c.torso), shirt, torso_light(c), cuts=CLOTH_CUTS)
    # laces down the front and the sides
    for k in range(5):
        y = c.yn + 14 + k * 8
        if k < 3:
            c.p.px(CX - 1, y, c.second[3])
            c.p.px(CX, y + 1, c.second[3])
            c.p.px(CX + 1, y, c.second[2])
    for s in (-1, 1):
        for k in range(6):
            y = c.yn + 40 + k * 8
            c.p.px(CX + s * (ai - 1), y, LEATHER_R[3])
            c.p.px(CX + s * (ai - 1), y + 1, LEATHER_R[0])
    for s in (-1, 1):
        trace(c.p, [(CX + s * 22, c.yn + 30), (CX + s * 18, c.yn + 46)], c.main[1], body)
    belt(c, 199)
    cuffs(c, LEATHER_R, 196, 9)
    for dy in range(4):
        pass
    wrinkles(c, (CX - 40, c.yn + 50, CX + 30, 195), c.main, 5, body)
    wrinkles(c, (CX - 70, c.yn + 30, CX - 50, 190), shirt, 4)
    wrinkles(c, (CX + 50, c.yn + 30, CX + 70, 190), shirt, 4)


def doublet(c: Ctx) -> None:
    """A quilted doublet buttoned to a standing collar, shoulder rolls in the second cloth, a trim at the neck."""
    paint_base(c, texture=0.1)
    ai = c.arm_in
    armpits(c)
    # slashed shoulder rolls
    for s in (-1, 1):
        roll = both(c.torso, poly([(CX + s * (ai - 4), c.yn), (CX + s * (c.sw + 2), c.yn), (CX + s * (c.sw + 2), c.yn + 46), (CX + s * (ai - 4), c.yn + 32)]))
        panel(c, roll, c.second, texture=0.12)
        for k in range(1, 4):
            x = CX + s * (ai + k * 6 - 3)
            trace(c.p, [(x, c.yn + 6 + k * 2), (x - s, c.yn + 38 + k * 2)], c.second[0], roll)
            trace(c.p, [(x - 1, c.yn + 6 + k * 2), (x - 1 - s, c.yn + 38 + k * 2)], c.second[3], roll)
    elbows(c)
    # a stand collar
    collar = both(c.torso, rect(CX - c.nk - 5, c.yn - 8, CX + c.nk + 4, c.yn + 8))
    neck_open(c, c.nk - 2, 4, -4)
    collar = both(collar, c.torso)
    panel(c, collar, c.trim, texture=0.06, base=0.1)
    hl(c.p, CX - c.nk - 4, c.yn + 7, 2 * c.nk + 8, c.trim[0])
    placket(c, CX, c.yn + 8, 215, c.main)
    # quilted chest: stitched diamonds
    quilt(c, minus(both(c.torso, rect(CX - ai + 1, c.yn + 12, CX + ai - 1, 259)), rect(CX - 2, 0, CX + 1, 259)), c.main, 9)
    belt(c, 200, buckle=True)
    cuffs(c, c.trim, 198, 8)
    wrinkles(c, (CX - 38, c.yn + 54, CX + 28, 195), c.main, 4)


def coat(c: Ctx) -> None:
    """A long coat open over a waistcoat: wide lapels, a fur or velvet collar, a row of buttons, a chain of office."""
    paint_base(c, ramp=c.second, texture=0.1)
    ai = c.arm_in
    for y in range(c.yn + 14, 210, 13):
        button(c.p, CX - 1, y, BRASS_R)
    coat_l = poly([(CX - 6, c.yn), (CX - ai - 8, c.yn), (CX - ai - 8, 259), (CX - 8, 259), (CX - 9, c.yn + 36)])
    coat_r = poly([(CX + 6, c.yn), (CX + ai + 8, c.yn), (CX + ai + 8, 259), (CX + 8, 259), (CX + 9, c.yn + 36)])
    # wait: the waistcoat shows in a V; the coat panels are the sides
    panel(c, union(coat_l, coat_r), c.main, texture=0.14)
    wv = poly([(CX - 6, c.yn), (CX + 6, c.yn), (CX + 9, c.yn + 36), (CX + 8, 259), (CX - 8, 259), (CX - 9, c.yn + 36)])
    panel(c, wv, c.second, texture=0.1)
    for s in (-1, 1):
        trace(c.p, [(CX + s * 6, c.yn), (CX + s * 9, c.yn + 36), (CX + s * 8, 259)], c.main[0], c.torso)
        trace(c.p, [(CX + s * 6 - 1 + (1 if s > 0 else 0), c.yn), (CX + s * 9 - 1 + (1 if s > 0 else 0), c.yn + 36)], c.main[3], c.torso)
    # revers: big lapels folded back
    for s in (-1, 1):
        lap = poly([(CX + s * 6, c.yn + 2), (CX + s * 22, c.yn + 2), (CX + s * 18, c.yn + 30), (CX + s * 9, c.yn + 36)])
        panel(c, lap, c.trim if "fur" in c.look.extras else c.main, texture=0.18, base=0.1)
        trace(c.p, [(CX + s * 22, c.yn + 2), (CX + s * 18, c.yn + 30), (CX + s * 9, c.yn + 36)], c.main[0], c.torso)
    neck_open(c, c.nk - 1, 5, -4)
    armpits(c)
    elbows(c)
    chest_pull(c)
    cuffs(c, c.second, 195, 11)
    for y in range(c.yn + 40, 210, 14):
        button(c.p, CX - 1, y, BRASS_R)
    wrinkles(c, (CX - 52, c.yn + 54, CX + 40, 195), c.main, 6)


def robe(c: Ctx) -> None:
    """A scholar's or physician's robe: a high collar, an opening with a trim band, deep sleeves, a cord belt."""
    paint_base(c, texture=0.12)
    ai = c.arm_in
    armpits(c)
    elbows(c)
    chest_pull(c)
    neck_open(c, c.nk + 1, 6, -2)
    # the underrobe at the throat
    v = poly([(CX - 10, c.yn - 2), (CX + 10, c.yn - 2), (CX + 1, c.yn + 44), (CX - 1, c.yn + 44)])
    panel(c, v, c.second, texture=0.08)
    for s in (-1, 1):
        # front trim along the opening
        band = poly([(CX + s * 10, c.yn - 2), (CX + s * 13, c.yn - 2), (CX + s * 4, c.yn + 50), (CX + s * 1, c.yn + 50), (CX + s * 5, c.yn + 24)])
        panel(c, band, c.trim, texture=0.06, base=0.05)
        trace(c.p, [(CX + s * 10, c.yn - 1), (CX + s * 5, c.yn + 24), (CX + s * 1, c.yn + 50)], c.main[0], c.torso)
        # a standing collar
        coll = poly([(CX + s * (c.nk + 3), c.yn - 8), (CX + s * (c.nk + 9), c.yn - 3), (CX + s * 12, c.yn + 6), (CX + s * (c.nk - 1), c.yn - 1)])
        panel(c, coll, c.trim, base=0.1)
    # the front fall: two long folds and the skirt of the robe
    for s in (-1, 1):
        drape(c, CX + s * 6, c.yn + 52, CX + s * 14, 259, s * 2, c.main)
        drape(c, CX + s * 26, c.yn + 60, CX + s * 30, 259, -s * 2, c.main)
    rope_belt(c, 198, tone_of("#c9b17a"))
    cuffs(c, c.trim, 192, 14)
    wrinkles(c, (CX - 52, c.yn + 54, CX + 40, 190), c.main, 5)


def apron(c: Ctx) -> None:
    """A work shirt under a bib apron: the shirt (second colour) at neck and sleeves, the apron (main) with straps,
    a pocket, a seam and a rolled cuff."""
    shirt = c.second
    paint_base(c, ramp=shirt, texture=0.14)
    armpits(c, shirt)
    elbows(c, shirt)
    chest_pull(c, shirt)
    hole = neck_open(c, c.nk + 3, 8, 2)
    ring = minus(grow(hole, 2), hole)
    fill(c.p, both(ring, c.torso), shirt, torso_light(c, 0.1), cuts=CLOTH_CUTS)
    skin_chest(c, minus(hole, oval(CX, c.yn - 8, c.nk + 6, 8)))
    # the bib: a trapezoid from the neck straps to the full width of the waist
    w_top, w_bot = 24, c.arm_in - 4
    bib = poly([(CX - w_top, c.yn + 22), (CX + w_top, c.yn + 22), (CX + w_bot, 259), (CX - w_bot, 259)])
    panel(c, bib, c.main, texture=0.18, base=0.05)
    for s in (-1, 1):                                  # straps over the shoulders
        strap = poly([(CX + s * (w_top - 8), c.yn + 22), (CX + s * (w_top + 1), c.yn + 22), (CX + s * (c.nk + 14), c.yn + 2), (CX + s * (c.nk + 6), c.yn - 3)])
        panel(c, strap, c.main, base=0.02)
        trace(c.p, [(CX + s * (w_top + 1), c.yn + 22), (CX + s * (c.nk + 14), c.yn + 2)], c.main[0], c.torso)
        button(c.p, CX + s * (w_top - 6), c.yn + 22, BRASS_R)
        trace(c.p, [(CX + s * w_top, c.yn + 22), (CX + s * w_bot, 259)], c.main[0], c.torso)
        trace(c.p, [(CX + s * w_top - 1, c.yn + 22), (CX + s * w_bot - 1, 259)], c.main[3], c.torso)
    trace(c.p, [(CX - w_top, c.yn + 22), (CX + w_top, c.yn + 22)], c.main[0], c.torso)
    trace(c.p, [(CX - w_top, c.yn + 21), (CX + w_top, c.yn + 21)], c.main[3], c.torso)
    # a patch pocket and a few wrinkles
    px0, py0 = CX - 14, c.yn + 60
    c.p.rect(px0, py0, 28, 20, c.main[2])
    hl(c.p, px0, py0, 28, c.main[3])
    c.p.vline(px0, py0, 20, c.main[3])
    c.p.vline(px0 + 27, py0, 20, c.main[0])
    hl(c.p, px0, py0 + 19, 28, c.main[0])
    for x in range(px0 + 1, px0 + 27, 4):
        c.p.px(x, py0 + 3, c.main[1])
    for y in (c.yn + 30, c.yn + 44):
        sag(c, CX - 22, CX + 22, y + 4, 2, c.main, bib)
    wrinkles(c, (CX - 18, c.yn + 90, CX + 18, 200), c.main, 4, bib)
    # a tie at the waist
    hl(c.p, CX - w_bot + 2, 199, 2 * w_bot - 3, c.main[1])
    hl(c.p, CX - w_bot + 2, 198, 2 * w_bot - 3, c.main[3])
    cuffs(c, LEATHER_R, 197, 8)


def habit(c: Ctx) -> None:
    """A monk's habit: coarse cloth, a cowl at the neck, wide sleeves and a rope belt."""
    paint_base(c, texture=0.2)
    armpits(c)
    elbows(c)
    chest_pull(c)
    hole = neck_open(c, c.nk + 4, 8, 1)
    ring = minus(grow(hole, 3), hole)
    fill(c.p, both(ring, c.torso), c.main, torso_light(c, 0.12), cuts=CLOTH_CUTS, texture=0.1)
    for s in (-1, 1):
        drape(c, CX + s * 4, c.yn + 30, CX + s * 10, 259, s * 3, c.main)
        drape(c, CX + s * 22, c.yn + 44, CX + s * 28, 259, -s * 2, c.main)
    rope_belt(c, 196, tone_of("#c8b890"))
    wrinkles(c, (CX - 52, c.yn + 54, CX + 40, 190), c.main, 6)
    cuffs(c, c.second, 196, 12)


def tabard(c: Ctx) -> None:
    """A watchman's kit: padded or mailed sleeves, a coloured tabard with a brass emblem and edge trim, a belt."""
    ai = c.arm_in
    under = c.second
    paint_base(c, ramp=under, texture=0.1)
    ls, rs = arms(c)
    if "mail" in c.look.extras or "iron" in c.look.extras:
        mail_texture(c, union(ls, rs), IRON_R)
    else:
        quilt(c, union(ls, rs), under, 7)
    armpits(c, under)
    elbows(c, under)
    neck_open(c, c.nk + 2, 6, -1)
    # a high padded collar
    col = both(c.torso, rect(CX - c.nk - 5, c.yn - 8, CX + c.nk + 4, c.yn + 6))
    neck_open(c, c.nk - 1, 4, -4)
    panel(c, both(col, c.torso), under, base=0.1)
    # the tabard hangs over the chest between the arm lines
    tab = poly([(CX - ai + 3, c.yn + 1), (CX - c.nk - 3, c.yn - 6), (CX + c.nk + 3, c.yn - 6), (CX + ai - 3, c.yn + 1), (CX + ai, 259), (CX - ai, 259)])
    panel(c, minus(tab, oval(CX, c.yn - 4, c.nk + 2, 9)), c.main, texture=0.16)
    # trim edges and the neck bar
    for s in (-1, 1):
        trace(c.p, [(CX + s * (ai - 3), c.yn + 1), (CX + s * ai, 259)], c.trim[3] if s < 0 else c.trim[1], c.torso)
        trace(c.p, [(CX + s * (ai - 4), c.yn + 1), (CX + s * (ai - 1), 259)], c.trim[2], c.torso)
        trace(c.p, [(CX + s * (ai - 2), c.yn + 1), (CX + s * (ai + 1), 259)], c.main[0], c.torso)
    # the emblem: a brass tower on the chest, with a lit left face
    ex, ey = CX, c.yn + 50
    emb = c.trim
    c.p.rect(ex - 9, ey, 18, 22, emb[2])
    c.p.rect(ex - 9, ey, 18, 3, emb[3])
    c.p.rect(ex - 9, ey - 5, 3, 6, emb[3])
    c.p.rect(ex - 1, ey - 5, 3, 6, emb[2])
    c.p.rect(ex + 6, ey - 5, 3, 6, emb[1])
    c.p.rect(ex - 9, ey + 3, 1, 19, emb[4])
    c.p.rect(ex + 8, ey + 3, 1, 19, emb[1])
    c.p.rect(ex - 3, ey + 11, 6, 11, c.main[0])
    c.p.rect(ex - 2, ey + 12, 4, 10, c.main[1])
    hl(c.p, ex - 9, ey + 21, 18, emb[0])
    for k in range(3):
        sag(c, CX - ai + 6, CX + ai - 6, c.yn + 36 + k * 18, 2, c.main, tab)
    belt(c, 199, w=7)
    cuffs(c, LEATHER_R, 196, 9)
    wrinkles(c, (CX - 40, c.yn + 78, CX + 30, 195), c.main, 4, tab)


def mail(c: Ctx) -> None:
    """A mail hauberk over a padded arming coat: rings on shoulders and chest, a leather strap, a belt, a mail collar."""
    paint_base(c, ramp=IRON_R, texture=0.08)
    mail_texture(c, c.torso, IRON_R)
    armpits(c, IRON_R)
    elbows(c, IRON_R)
    chest_pull(c, IRON_R)
    hole = neck_open(c, c.nk + 3, 8, 0)
    ring = minus(grow(hole, 3), hole)
    fill(c.p, both(ring, c.torso), IRON_R, torso_light(c, 0.12), cuts=CLOTH_CUTS)
    mail_texture(c, both(ring, c.torso), IRON_R)
    # the padded jack under the mail shows at the collar
    jack = minus(grow(hole, 1), hole)
    fill(c.p, both(jack, c.torso), c.main, torso_light(c), cuts=CLOTH_CUTS, texture=0.1)
    # a leather cross-strap with rivets
    pts = [(CX - 38, c.yn + 8), (CX + 30, 259)]
    strap = poly([(CX - 42, c.yn + 8), (CX - 33, c.yn + 6), (CX + 36, 259), (CX + 24, 259)])
    panel(c, strap, LEATHER_R)
    for k in range(6):
        t = k / 5
        rivet(c.p, round(CX - 37 + 66 * t) if False else round(CX - 36 + 62 * (0.05 + 0.9 * t) * 0.9), c.yn + 14 + round(0.85 * (259 - c.yn - 14) * (0.05 + 0.9 * t) * 0.6), BRASS_R)
    belt(c, 198, w=7)
    cuffs(c, LEATHER_R, 195, 9)
    wrinkles(c, (CX - 40, c.yn + 50, CX + 30, 190), IRON_R, 6)


def cloak(c: Ctx) -> None:
    """A heavy travel cloak: a wide shoulder cape, a fold-over collar, a brass clasp at the throat, folds falling from it."""
    paint_base(c, texture=0.2)
    armpits(c)
    # the tunic beneath, seen in a V
    hole = neck_open(c, c.nk + 3, 8, 1)
    v = poly([(CX - c.nk - 6, c.yn - 2), (CX + c.nk + 6, c.yn - 2), (CX + 4, c.yn + 40), (CX - 4, c.yn + 40)])
    panel(c, minus(v, hole), c.second, texture=0.1)
    for s in (-1, 1):
        drape(c, CX + s * 8, c.yn + 8, CX + s * 18, 259, s * 4, c.main)
        drape(c, CX + s * 26, c.yn + 14, CX + s * 34, 259, -s * 3, c.main)
        drape(c, CX + s * 46, c.yn + 24, CX + s * 54, 259, s * 3, c.main)
    # cape edge
    cape = poly([(CX - c.sw, c.yn + 30), (CX + c.sw, c.yn + 30), (CX + c.sw - 6, c.yn + 40), (CX - c.sw + 6, c.yn + 40)])
    for s in (-1, 1):
        trace(c.p, [(CX + s * c.nk, c.yn + 2), (CX + s * (c.nk + 22), c.yn + 14), (CX + s * (c.sw - 8), c.yn + 36)], c.main[0], c.torso)
        trace(c.p, [(CX + s * c.nk - 1, c.yn + 3), (CX + s * (c.nk + 22) - 1, c.yn + 15), (CX + s * (c.sw - 8) - 1, c.yn + 37)], c.main[3], c.torso)
    # clasp
    c.p.rect(CX - 5, c.yn + 6, 10, 4, BRASS_R[2])
    c.p.rect(CX - 5, c.yn + 6, 10, 1, BRASS_R[4])
    c.p.rect(CX - 1, c.yn + 5, 2, 6, BRASS_R[3])
    hl(c.p, CX - 5, c.yn + 9, 10, BRASS_R[0])
    wrinkles(c, (CX - 60, c.yn + 56, CX + 46, 195), c.main, 8)


def laced(c: Ctx) -> None:
    """A peasant's smock: a linen weave, a laced V neck, rolled sleeves, a strap over one shoulder."""
    paint_base(c, texture=0.2)
    armpits(c)
    elbows(c)
    chest_pull(c)
    hole = neck_open(c, c.nk + 3, 9, 3)
    ring = minus(grow(hole, 2), hole)
    fill(c.p, both(ring, c.torso), c.main, torso_light(c, 0.1), cuts=CLOTH_CUTS)
    v = poly([(CX - c.nk - 3, c.yn + 2), (CX + c.nk + 3, c.yn + 2), (CX + 1, c.yn + 34), (CX - 1, c.yn + 34)])
    skin_chest(c, both(v, minus(hole, oval(CX, c.yn - 8, c.nk + 6, 8))) if False else minus(v, oval(CX, c.yn - 8, c.nk + 6, 8)))
    for k in range(6):
        y = c.yn + 8 + k * 5
        w = max(1, 8 - k * 1)
        trace(c.p, [(CX - w, y), (CX + 1, y + 3)], c.second[3] if len(c.second) else c.main[3], c.torso)
        trace(c.p, [(CX + w - 1, y), (CX, y + 3)], c.second[2], c.torso)
    for s in (-1, 1):
        trace(c.p, [(CX + s * (c.nk + 3), c.yn + 2), (CX + s * 1, c.yn + 34)], c.main[1], c.torso)
    # rolled sleeve ends: two bands
    for s in (-1, 1):
        for y, r in ((182, c.main), (192, c.main)):
            x0 = CX + s * (c.arm_in + 12)
            for x in range(x0 - 12, x0 + 13):
                if inside(c.torso, x, y):
                    c.p.px(x, y, r[0] if s > 0 else r[1])
                    c.p.px(x, y + 1, r[3])
    belt(c, 200, ramp=c.second if len(c.second) > 3 else LEATHER_R, buckle=False)
    wrinkles(c, (CX - 52, c.yn + 54, CX + 40, 190), c.main, 8)
    # a strap diagonal
    if "strap" in c.look.extras:
        pass


def skin_window(c: Ctx, m: Mask) -> None:
    """Bare skin in an opening of a garment: shaded under the chin, lit on the chest below."""
    sk = SKINS[c.look.skin]
    snap = c.neck.load() if c.neck is not None else None
    for x, y in pixels(m):
        t = 0.75 + 0.3 * (-(x - CX)) / 40 - 0.02 * (y - c.yn)
        if y < c.yn + 8 and snap is not None and snap[x, y][3]:
            c.p.px(x, y, snap[x, y])
        elif y < c.yn - 2:
            c.p.px(x, y, sk[0])
        else:
            c.p.px(x, y, sk[3] if t > 0.95 else sk[2] if t > 0.4 else sk[1])


def gown(c: Ctx) -> None:
    """A woman's gown: a scooped neckline with trim, a laced bodice, sleeves in the second cloth, a high waist."""
    ai = c.arm_in
    paint_base(c, texture=0.1)
    ls, rs = arms(c)
    paint_base(c, m=union(ls, rs), ramp=c.second, texture=0.12)
    armpits(c)
    elbows(c, c.second)
    bod = both(c.torso, rect(CX - ai + 1, 0, CX + ai - 1, 259))
    panel(c, bod, c.main, texture=0.1)
    # the neckline: a wide scoop; skin inside, a band of trim along its edge
    win = both(union(oval(CX, c.yn + 2, c.nk + 12, 19), rect(CX - c.nk, c.yn - 12, CX + c.nk - 1, c.yn)), rect(0, 0, 287, c.yn + 21))
    win = minus(win, rect(0, 0, 287, c.yn - 12))
    c.torso = minus(c.torso, win)
    skin_window(c, win)
    edge = minus(grow(win, 2), grow(win, 0))
    fill(c.p, both(edge, both(c.torso, rect(0, c.yn - 4, 287, 259))), c.trim, torso_light(c, 0.1), cuts=CLOTH_CUTS)
    for k in range(3):                             # a necklace of small beads on the skin
        pass
    for k in range(9):
        y = c.yn + 28 + k * 7
        trace(c.p, [(CX - 6, y), (CX + 5, y + 4)], c.trim[3] if k % 2 else c.trim[2], c.torso)
        trace(c.p, [(CX + 5, y), (CX - 6, y + 4)], c.trim[1], c.torso)
    vl(c.p, CX - 6, c.yn + 26, 70, c.main[0])
    vl(c.p, CX + 5, c.yn + 26, 70, c.main[1])
    for s in (-1, 1):
        trace(c.p, [(CX + s * (ai - 1), c.yn + 22), (CX + s * (ai - 1), 259)], c.main[0], c.torso)
        drape(c, CX + s * 14, c.yn + 40, CX + s * 18, 259, s * 2, c.main, bod)
    hl(c.p, CX - ai + 1, c.yn + 72, 2 * ai - 2, c.trim[1])
    hl(c.p, CX - ai + 1, c.yn + 71, 2 * ai - 2, c.trim[3])
    cuffs(c, c.trim, 196, 9)
    wrinkles(c, (CX - 40, c.yn + 76, CX + 30, 195), c.main, 4, bod)
    wrinkles(c, (CX - 70, c.yn + 30, CX - 50, 190), c.second, 3)
    wrinkles(c, (CX + 50, c.yn + 30, CX + 70, 190), c.second, 3)


def motley(c: Ctx) -> None:
    """A jester's motley: the tunic cut in quarters of two colours with a collar of points."""
    paint_base(c, texture=0.08)
    ai = c.arm_in
    left = both(c.torso, rect(0, 0, CX - 1, 259))
    right = both(c.torso, rect(CX, 0, 287, 259))
    # diagonal check: second colour on alternating blocks
    for x, y in pixels(c.torso):
        if ((x - CX + 400) // 18 + (y // 18)) % 2 == 0:
            pass
    check = blank()
    for bx in range(CX - 90, CX + 90, 22):
        for by in range(c.yn - 10, 260, 22):
            pts = [(bx + 11, by), (bx + 22, by + 11), (bx + 11, by + 22), (bx, by + 11)]
            if ((bx - CX + 90) // 22 + (by - c.yn + 10) // 22) % 2 == 0:
                check = union(check, poly(pts))
    panel(c, check, c.second)
    neck_open(c, c.nk + 5, 8, 2)
    armpits(c)
    elbows(c)
    for s in (-1, 1):
        for k in range(4):
            x = CX + s * (c.nk + 5 + k * 6)
            pts = poly([(x - 3, c.yn + 2 + k), (x + 3, c.yn + 2 + k), (x, c.yn + 12 + k)])
            panel(c, pts, c.trim if k % 2 == 0 else c.second)
            button(c.p, x - 1, c.yn + 13 + k, BRASS_R)
    belt(c, 198)
    cuffs(c, c.trim, 196, 9)


GARMENTS: dict[str, Callable[[Ctx], None]] = {
    "tunic": tunic, "jerkin": jerkin, "doublet": doublet, "coat": coat, "robe": robe, "apron": apron, "habit": habit,
    "tabard": tabard, "mail": mail, "cloak": cloak, "laced": laced, "gown": gown, "motley": motley,
}
