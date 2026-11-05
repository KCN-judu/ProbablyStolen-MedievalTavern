"""Marks and accessories: spectacles, an eyepatch, scars and soot on the face; chains, straps, pauldrons, scarves, fur on
the body. `Look.extras` lists them by name; unknown names are ignored."""

from __future__ import annotations

import math
import random

from people_kit import Mask, blank, both, grow, minus, oval, poly, rect, union
from people_look import Look
from pbody_core import BRASS_R, IRON_R, LEATHER_R, Ctx, button, rivet, torso_light, CLOTH_CUTS
from pface_core import curve, fill, hl, inside, pixels, trace, vl
from pface_head import CX, Geo, head_mask, skin_ramp
from pix import Pix, mix, rgb

WOOL = (0.0, 0.42, 0.88, 1.18)


def face_marks(p: Pix, look: Look, g: Geo) -> None:
    """Things on or at the eyes and the skin of the face."""
    sk = skin_ramp(look)
    head = head_mask(look)
    rng = random.Random(look.seed * 5 + 1)
    ex = look.extras
    if "soot" in ex:
        for _ in range(60):
            x, y = CX + rng.randint(-20, 20), rng.randint(g.eye - 12, g.chin - 4)
            if inside(head, x, y) and rng.random() < 0.7:
                p.px(x, y, mix(sk[1], (30, 24, 28), 0.55) if rng.random() < 0.6 else mix(sk[2], (50, 40, 40), 0.5))
    if "flour" in ex:
        for _ in range(7):
            x, y = CX + rng.randint(-20, 20), rng.randint(g.eye - 12, g.chin - 4)
            if inside(head, x, y):
                p.px(x, y, mix(sk[3], (240, 232, 214), 0.7))
    if "blood" in ex:
        for i in range(10):
            p.px(CX + 7 + i // 3, g.eye + 6 + i, (126, 28, 36))
        p.px(CX + 6, g.eye + 5, (150, 40, 44))
    if "scar" in ex:
        pale = mix(sk[3], (230, 170, 160), 0.5)
        dark = mix(sk[1], (110, 40, 50), 0.5)
        pts = [(CX + 14, g.eye - 8), (CX + 10, g.eye + 1), (CX + 8, g.eye + 8), (CX + 4, g.eye + 14)]
        trace(p, pts, dark)
        trace(p, [(x - 1, y) for x, y in pts], pale)
        for i in range(3):
            p.px(CX + 12 - i * 3 + 2, g.eye - 5 + i * 5, dark)
            p.px(CX + 14 - i * 3, g.eye - 5 + i * 5, dark)
    if "bandage" in ex:
        for y in range(g.sk + 7, g.sk + 14):
            n = round(g.w / 2) - 1
            for x in range(CX - n, CX + n):
                p.px(x, y, (206, 194, 168) if (x + y) % 5 else (170, 156, 130))
        hl(p, CX - 20, g.sk + 7, 40, (236, 226, 200))
        hl(p, CX - 20, g.sk + 13, 40, (140, 126, 104))
        for i in range(5):
            p.px(CX + 6 + i, g.sk + 9 + (i % 2), (150, 40, 44))
    if "eyepatch" in ex:
        lx = CX - 1 - g.gap - 5
        p.rect(lx - 5, g.eye - 4, 11, 9, (26, 22, 26))
        p.rect(lx - 4, g.eye - 3, 9, 7, (40, 34, 40))
        p.px(lx - 3, g.eye - 3, (70, 60, 66))
        p.px(lx - 2, g.eye - 3, (58, 50, 56))
        trace(p, [(lx + 5, g.eye - 3), (CX + 14, g.sk + 8), (CX + 20, g.eye - 8)], (26, 22, 26))
        trace(p, [(lx - 5, g.eye - 2), (CX - 22, g.sk + 10)], (26, 22, 26))
    if "glasses" in ex:
        rim = BRASS_R[3] if "gold" in ex else IRON_R[3]
        sh = BRASS_R[1] if "gold" in ex else IRON_R[1]
        for s in (-1, 1):
            lx = CX + s * (g.gap + 5) - (1 if s < 0 else 0)
            p.draw.ellipse((lx - 6, g.eye - 4, lx + 6, g.eye + 5), outline=rim)
            # lens glass: the eye shows through, with a diagonal reflection
            for dy in range(-2, 4):
                for dx in range(-4, 5):
                    xx, yy = lx + dx, g.eye + dy
                    if ((dx / 4.6) ** 2 + ((dy - 0.5) / 3.6) ** 2) < 1:
                        pass
            p.px(lx - 4, g.eye - 2, (200, 220, 224))
            p.px(lx - 3, g.eye - 2, (160, 190, 200))
            p.px(lx - 3, g.eye - 3, (200, 220, 224))
        p.hline(CX - 3, g.eye - 1, 7, rim)
        p.px(CX - 1, g.eye, sh)
    if "goggles" in ex:
        for s in (-1, 1):
            lx = CX + s * (g.gap + 5) - (1 if s < 0 else 0)
            p.ellipse(lx - 6, g.eye - 5, 13, 12, BRASS_R[1])
            p.ellipse(lx - 5, g.eye - 4, 11, 10, BRASS_R[3])
            p.ellipse(lx - 4, g.eye - 3, 9, 8, (46, 80, 90))
            p.px(lx - 3, g.eye - 2, (170, 214, 220))
            p.px(lx - 2, g.eye - 2, (110, 160, 170))
            p.px(lx + 2, g.eye + 2, (28, 50, 62))
        p.hline(CX - 1, g.eye - 1, 3, BRASS_R[2])
        for y in (g.eye - 1, g.eye):
            hl(p, CX - 33, y, 8, LEATHER_R[1])
            hl(p, CX + 26, y, 8, LEATHER_R[1])
    if "goggles_up" in ex:
        y = g.sk + 7
        for s in (-1, 1):
            lx = CX + s * 11
            p.ellipse(lx - 6, y, 13, 10, BRASS_R[1])
            p.ellipse(lx - 5, y + 1, 11, 8, BRASS_R[3])
            p.ellipse(lx - 4, y + 2, 9, 6, (46, 80, 90))
            p.px(lx - 3, y + 3, (170, 214, 220))
        hl(p, CX - 1, y + 4, 3, BRASS_R[2])


def body_extras(c: Ctx) -> None:
    """Things worn on the torso, in front of the garment."""
    p, ex = c.p, c.look.extras
    from pbody_wear import stain
    for kind in ("flour", "soot", "blood"):
        if kind in ex:
            stain(c, kind)
    sw, yn, nk = c.sw, c.yn, c.nk
    if "fur" in ex:
        fur = mix_ramp((124, 98, 80))
        m = both(union(oval(CX - nk - 6, yn + 8, 13, 8), oval(CX + nk + 6, yn + 8, 13, 8), oval(CX, yn + 22, nk + 8, 5)), c.torso)
        fill(p, m, fur, torso_light(c, 0.1), cuts=WOOL, texture=0.35)
        rng = random.Random(c.look.seed)
        for x, y in pixels(m):
            if rng.random() < 0.2:
                p.px(x, y, fur[4] if rng.random() < 0.5 else fur[1])
    if "scarf" in ex:
        col = mix_ramp((150, 54, 52) if c.look.seed % 2 else (60, 98, 96))
        m = both(union(oval(CX, yn + 3, nk + 8, 8), poly([(CX + 2, yn + 6), (CX + 12, yn + 6), (CX + 16, yn + 40), (CX + 8, yn + 42)])), c.torso)
        fill(p, m, col, torso_light(c, 0.1), cuts=WOOL, texture=0.2)
        for k in range(4):
            y = yn + 12 + k * 7
            hl(p, CX + 8 - k // 2, y, 7, col[0])
            hl(p, CX + 8 - k // 2, y - 1, 7, col[3])
        trace(p, curve((CX - nk - 4, yn + 6), (CX, yn + 12), (CX + nk + 4, yn + 6), 10), col[1], m)
    if "pendant" in ex or "chain" in ex or "gold" in ex:
        n = 1
        trace(p, curve((CX - nk - 3, yn + 2), (CX, yn + 30), (CX + nk + 3, yn + 2), 14), LEATHER_R[1] if "chain" not in ex else BRASS_R[2], c.torso)
        px_, py_ = CX, yn + 22
        p.ellipse(px_ - 4, py_, 9, 9, BRASS_R[1])
        p.ellipse(px_ - 3, py_ + 1, 7, 7, BRASS_R[3])
        p.px(px_ - 2, py_ + 2, BRASS_R[4])
        p.px(px_ - 1, py_ + 2, BRASS_R[4])
        p.px(px_ + 1, py_ + 5, BRASS_R[1])
    if "chain" in ex:
        # a chain of office: two strands of links over the shoulders to a medallion
        for off in (0, 4):
            pts = curve((CX - sw + 24, yn + 8 + off), (CX, yn + 54 + off), (CX + sw - 24, yn + 8 + off), 28)
            for i, (x, y) in enumerate(pts):
                if inside(c.torso, round(x), round(y)):
                    p.px(round(x), round(y), BRASS_R[4] if i % 3 == 0 else BRASS_R[2])
                    if i % 3 == 0:
                        p.px(round(x), round(y) + 1, BRASS_R[1])
    if "strap" in ex or "satchel" in ex or "pack" in ex:
        for s in ((-1, 1) if "pack" in ex else (1,)):
            pts = poly([(CX + s * (nk + 6), yn - 2), (CX + s * (nk + 15), yn - 2), (CX - s * 30, 259), (CX - s * 42, 259)])
            if "pack" in ex:
                pts = poly([(CX + s * (nk + 8), yn - 2), (CX + s * (nk + 16), yn - 2), (CX + s * (nk + 22), 259), (CX + s * (nk + 13), 259)])
            m = both(pts, c.torso)
            fill(p, m, LEATHER_R, torso_light(c), cuts=CLOTH_CUTS, texture=0.1)
            for x, y in pixels(m):
                if not inside(m, x - 1, y) and s > 0 or not inside(m, x + 1, y) and s < 0:
                    p.px(x, y, LEATHER_R[0])
            if "pack" in ex:
                x0 = CX + s * (nk + 18)
                p.rect(x0 - 3, yn + 48, 7, 6, BRASS_R[2])
                p.rect(x0 - 2, yn + 49, 5, 4, LEATHER_R[1])
                p.hline(x0 - 3, yn + 48, 7, BRASS_R[4])
            else:
                for k in range(5):
                    rivet(p, CX + round(s * (nk + 10 - (k + 1) * (nk + 10 + 36) / 7)) + 0, yn + 20 + k * 22, BRASS_R)
    if "satchel" in ex:
        bag = both(poly([(CX - sw + 8, 168), (CX - 22, 168), (CX - 22, 259), (CX - sw + 8, 259)]), c.torso)
        fill(p, bag, LEATHER_R, torso_light(c), cuts=CLOTH_CUTS, texture=0.12)
        hl(p, CX - sw + 8, 168, sw - 30, LEATHER_R[3])
        flap = both(poly([(CX - sw + 8, 168), (CX - 22, 168), (CX - 22, 192), (CX - sw + 8, 196)]), c.torso)
        fill(p, flap, LEATHER_R, torso_light(c, 0.1), cuts=CLOTH_CUTS)
        trace(p, [(CX - sw + 8, 196), (CX - 22, 192)], LEATHER_R[0])
        button(p, CX - 38, 190, BRASS_R)
    if "pauldron" in ex:
        for s in ((-1, 1) if "iron" in ex else (-1,)):
            cx0 = CX + s * (sw - 13)
            plate = both(union(oval(cx0, yn + 22, 15, 12), oval(cx0 - s * 2, yn + 34, 13, 8)), rect(0, yn + 2, 287, 259))
            fill(p, plate, IRON_R, lambda x, y: 0.72 + 0.5 * (-(x - cx0) / 20) - 0.3 * ((y - yn - 12) / 40), cuts=(0.12, 0.5, 0.95, 1.2), texture=0.06)
            for x, y in pixels(plate):
                if not inside(plate, x - 1, y) and not inside(plate, x, y + 1) or not inside(plate, x, y - 1) and s < 0:
                    p.px(x, y, IRON_R[0])
            for dy in (22, 31):
                trace(p, curve((cx0 - 15, yn + dy), (cx0, yn + dy + 5), (cx0 + 15, yn + dy), 8), IRON_R[0], plate)
                trace(p, curve((cx0 - 15, yn + dy - 1), (cx0, yn + dy + 4), (cx0 + 15, yn + dy - 1), 8), IRON_R[4], plate)
            for dx in (-9, 0, 9):
                rivet(p, cx0 + dx, yn + 15)


def mix_ramp(rgb_: tuple[int, int, int]):
    from people_kit import tone
    return tone(rgb_)
