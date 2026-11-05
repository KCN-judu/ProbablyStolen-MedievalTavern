"""Counter and wall devices of the `ctr_` pass: the call bell and the speaking tube (`phone`), the counting-house cabinet
(`marketplace_pc`, `marketplace_pc_notif`), the rope coil on the bar (`wires_table`) and the two pull-handles
(`bell_button_sheet`, `shutter_button_sheet`).

Counter things lie on the bar with contact shadows in its perspective (round things are ellipse arcs); the cabinet and the
shutter pull are on the wall and are seen face-on, hung or screwed to something.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from ctr_kit import BRASS, IRON, OAK, PALE_WOOD, PARCHMENT, SHADOW, WOOD, clip_to, drum, fill, fx, horn, line, mix, tube_tone
from palette import LEATHER, LINEN, MOSS, WINE
from pix import Color, Pix
from props import sheet

# ------------------------------------------------------------------------------------------------ phone: bell + speaking tube


def bell_on_tray(p: Pix, cx: int, cy: int) -> None:
    """A round oak tray (ellipse, its thickness under the near rim) with a brass handbell standing on it."""
    rx, ry = 20, 6
    fx.contact_shadow(p, fx.ellipse(cx + 2, cy + 2, rx + 1, ry + 1), shift=(4, 2), spread=4, strength=0.95, alpha=200)
    for dy in (3, 2, 1):
        p.ellipse(cx - rx, cy - ry + dy, 2 * rx + 1, 2 * ry + 1, WOOD[0] if dy == 3 else WOOD[1])
    fx.wood_fill(p, fx.ellipse(cx, cy, rx, ry), "h", WOOD, bias=0.2, seed=41, knots=0.3, joints=False, nails=False, wear_amount=0.2)
    p.ellipse(cx - rx + 3, cy - ry + 2, 2 * rx - 5, 2 * ry - 3, WOOD[1])
    p.dither(cx - rx + 5, cy - ry + 3, 2 * rx - 10, 2 * ry - 5, WOOD[2], 0.4)
    # the bell's shadow on the tray, to the right
    for y in range(cy - 3, cy + 4):
        for x in range(cx - 2, cx + 18):
            if ((x - cx - 7) / 10) ** 2 + ((y - cy) / 3.2) ** 2 < 1:
                fx.over(p, x, y, SHADOW, 150)
    lip_y, lip_rx, lip_ry, crown = cy + 1, 10, 2, cy - 12
    for y in range(crown, lip_y + 1):
        s = (y - crown) / (lip_y - crown)
        hw = 2 + (lip_rx - 2) * (0.45 * s ** 0.9 + 0.55 * s ** 3)
        for x in range(round(cx - hw), round(cx + hw) + 1):
            t = (x - cx) / max(hw, 1)
            k = 4 if -0.75 < t < -0.45 else 3 if t < 0.0 else 2 if t < 0.45 else 1 if t < 0.8 else 0
            p.px(x, y, BRASS[k])
    for dx in range(-lip_rx, lip_rx + 1):
        yb = lip_y + round(lip_ry * math.sqrt(1 - (dx / lip_rx) ** 2))
        t = dx / lip_rx
        for y in range(lip_y + 1, yb + 1):
            p.px(cx + dx, y, BRASS[3 if t < 0 else 1])
        p.px(cx + dx, lip_y, BRASS[4] if t < 0.1 else BRASS[3])
        p.px(cx + dx, yb, BRASS[0])
    for yy, wd in ((lip_y - 5, 5), (lip_y - 8, 4)):
        for dx in range(-wd, wd + 1):
            p.px(cx + dx, yy + (dx * dx) // 14, BRASS[1])
    p.rect(cx - 1, crown - 5, 3, 5, WOOD[3])                       # turned wooden grip
    p.vline(cx - 1, crown - 5, 5, WOOD[4])
    p.vline(cx + 1, crown - 5, 5, WOOD[0])
    p.hline(cx - 2, crown, 5, BRASS[3])
    p.ellipse(cx - 1, crown - 7, 3, 3, WOOD[4])


def speaking_tube(p: Pix, cx: int, cy: int) -> None:
    """A brass speaking tube: a round wall-plate flush in the counter, a short pipe that bends up into a funnel, and a
    whistle stopper on a short chain lying on the plate."""
    fx.contact_shadow(p, fx.ellipse(cx + 3, cy, 10, 3), shift=(4, 1), spread=3, strength=0.9, alpha=190)
    p.ellipse(cx - 9, cy - 3, 19, 8, BRASS[0])                     # plate: thickness below, face above
    p.ellipse(cx - 9, cy - 4, 19, 7, BRASS[3])
    p.ellipse(cx - 7, cy - 3, 15, 5, BRASS[2])
    p.hline(cx - 6, cy - 4, 6, BRASS[4])
    for dx in (-7, 7):                                             # four screws, two shown
        p.px(cx + dx, cy - 1, BRASS[0])
    # the pipe: vertical, then bent toward the funnel
    for y in range(cy - 14, cy - 2):
        for x in range(cx - 2, cx + 3):
            p.px(x, y, tube_tone(BRASS, (x - cx) / 2.0))
    for i, ww in enumerate((cy - 3, cy - 14)):
        p.hline(cx - 3, ww, 7, BRASS[3] if i == 0 else BRASS[2])    # collar rings
        p.hline(cx - 3, ww + 1, 7, BRASS[0])
        p.px(cx - 3, ww, BRASS[4])
    horn(p, (cx, cy - 14), (cx + 17, cy - 26), 2.4, 7.5, k=2.0, mouth_rx=3.6, seed=9)
    # a stopper on a chain: a small brass whistle with a link or two to the plate
    wx = cx + 12
    p.rect(wx, cy - 4, 4, 3, BRASS[3])
    p.px(wx, cy - 4, BRASS[4])
    p.hline(wx, cy - 2, 4, BRASS[0])
    for i, (dx, dy) in enumerate(((-2, -1), (-4, -2), (-6, -2))):
        p.px(wx + dx, cy - 3 + dy + 2, IRON[3 if i % 2 else 4])


def phone() -> Image.Image:
    p = Pix(85, 39, seed=7)
    bell_on_tray(p, 24, 28)
    speaking_tube(p, 62, 34)
    out = Pix(960, 540)
    out.paste(p, 241, 268)
    return clip_to(out.finish(), (241, 268, 326, 307))


# ------------------------------------------------------------------------------------------------ marketplace_pc: cabinet

PC_BOX = (788, 0, 944, 74)


def cabinet(notif: bool) -> Image.Image:
    p = Pix(960, 540, seed=33)
    x0, x1, y0, y1 = 792, 940, 11, 71
    # two chains from the beam (the picture's top) to iron rings on the cabinet's top
    for cx in (808, 924):
        fx.chain(p, [(cx, 0), (cx, y0 - 2)], link=5)
        p.ellipse(cx - 2, y0 - 3, 5, 4, IRON[3])
        p.px(cx - 1, y0 - 3, IRON[4])
        p.px(cx, y0 - 2, IRON[0])
    fx.wall_shadow(p, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], offset=(3, 4), spread=3, strength=0.9, alpha=190)
    fx.wood_fill(p, (x0, y0, x1 - x0, y1 - y0), "h", OAK, bias=0.4, seed=34, board=14, knots=0.6, wear_amount=0.5)
    # the open niche: dark inside, a lit shelf under it
    nx0, nx1, ny0, ny1 = x0 + 8, x1 - 8, y0 + 7, y0 + 32
    p.rect(nx0, ny0, nx1 - nx0, ny1 - ny0, OAK[0])
    fx.wood_fill(p, (nx0 + 1, ny0 + 1, nx1 - nx0 - 2, ny1 - ny0 - 2), "h", OAK, bias=-0.9, seed=35, knots=0, joints=False, nails=False, wear_amount=0.1)
    p.hline(nx0, ny0, nx1 - nx0, OAK[0])
    p.hline(nx0 + 1, ny1 - 1, nx1 - nx0 - 2, PALE_WOOD[3])           # lit shelf edge
    p.rect(nx0 - 1, ny1, nx1 - nx0 + 2, 2, WOOD[4])
    p.hline(nx0 - 1, ny1 + 1, nx1 - nx0 + 2, OAK[0])
    # the abacus: oak frame, four rods of beads
    ax0, ay0, aw, ah = nx0 + 8, ny0 + 4, 54, 19
    fx.wood_fill(p, (ax0, ay0, aw, ah), "h", WOOD, bias=0.2, seed=36, knots=0, joints=False, nails=False, wear_amount=0.2)
    p.rect(ax0 + 3, ay0 + 3, aw - 6, ah - 6, OAK[0])
    cols = (WINE[3], BRASS[3], PARCHMENT[2], MOSS[3])
    for r in range(4):
        y = ay0 + 5 + r * 3 + (1 if r > 1 else 0)
        p.hline(ax0 + 3, y + 1, aw - 6, IRON[3])
        for i in range(10):
            bx = ax0 + 4 + i * 4 + (0 if i < 5 else 6) - (r % 2) * (1 if i < 3 else 0)
            p.rect(bx, y - 1, 3, 3, cols[r])
            p.px(bx, y - 1, mix(cols[r][:3], (240, 220, 160), 0.5))
            p.px(bx + 2, y + 1, OAK[0])
    # the ledger: a tall leather book standing beside it, spine out, with brass bands
    lx = nx0 + 70
    fx.cloth_fill(p, (lx, ny0 + 3, 12, 22), LEATHER, "wool", folds=1, seed=37)
    p.vline(lx, ny0 + 3, 22, LEATHER[3])
    for yy in (ny0 + 6, ny0 + 22):
        p.hline(lx, yy, 12, BRASS[2])
        p.hline(lx, yy + 1, 12, BRASS[0])
    p.rect(lx + 2, ny0 + 11, 8, 6, PARCHMENT[3])
    p.hline(lx + 3, ny0 + 13, 6, WINE[1])
    p.hline(lx + 3, ny0 + 15, 4, WINE[1])
    # a small scale for coin and a stack of coins at the right
    sx = nx0 + 96
    p.rect(sx, ny1 - 6, 14, 1, BRASS[3])
    p.vline(sx + 7, ny1 - 14, 8, BRASS[2])
    p.hline(sx + 1, ny1 - 14, 13, BRASS[3])
    p.hline(sx + 1, ny1 - 13, 3, BRASS[2])
    p.hline(sx + 11, ny1 - 13, 3, BRASS[2])
    for i in range(4):
        p.rect(nx1 - 14, ny1 - 3 - i * 2, 6, 2, BRASS[3 - (i % 2)])
        p.hline(nx1 - 14, ny1 - 3 - i * 2, 6, BRASS[4])
    # the drawers: two rows of small ones, brass pulls and paper labels
    dy0 = ny1 + 5
    cw, chh = (x1 - x0 - 12) // 6, 15
    for row in range(2):
        for c in range(6):
            dx = x0 + 6 + c * cw
            dy = dy0 + row * (chh + 1)
            if dy + chh > y1 - 2:
                continue
            fx.wood_fill(p, (dx, dy, cw - 1, chh - 1), "h", WOOD, bias=0.1 + ((c + row) % 2) * 0.2, seed=40 + c + row * 7,
                         knots=0.3, joints=False, nails=False, wear_amount=0.2)
            p.frame(dx, dy, cw - 1, chh - 1, OAK[0])
            p.hline(dx + 1, dy + 1, cw - 3, PALE_WOOD[3])
            p.rect(dx + cw // 2 - 4, dy + 3, 8, 4, PARCHMENT[3])
            p.hline(dx + cw // 2 - 3, dy + 5, 5, WINE[1])
            p.hline(dx + cw // 2 - 4, dy + 6, 8, PARCHMENT[1])
            fx.brass_fill(p, (dx + cw // 2 - 3, dy + 9, 6, 3), profile="tube", tarnish=0.2, seed=c * 3 + row)
    # a brass strip and iron corner pieces
    fx.iron_fill(p, (x0, y1 - 3, x1 - x0, 3), hammer=0.2, rust=0.3, seed=51)
    for cx_, cy_ in ((x0, y0), (x1 - 5, y0), (x0, y1 - 8), (x1 - 5, y1 - 8)):
        fx.iron_fill(p, (cx_, cy_, 5, 8), hammer=0.3, rust=0.3, seed=cx_ + cy_)
        fx.rivet(p, cx_ + 2, cy_ + 3, 1, BRASS)
    if notif:
        # a letter slipped under the abacus' frame with a red wax seal: a new message has come
        px_, py_ = 868, 30
        fx.paper_fill(p, [(px_, py_), (px_ + 14, py_ - 2), (px_ + 16, py_ + 14), (px_ + 2, py_ + 17)], shadow=True, seed=5, folds=(0, 1))
        p.ellipse(px_ + 6, py_ + 7, 5, 5, WINE[2])
        p.px(px_ + 7, py_ + 8, WINE[4])
        p.px(px_ + 9, py_ + 10, WINE[1])
        # a brass bell-flag raised on the cabinet's top edge
        p.rect(902, y0 - 0, 1, 1, BRASS[4])
        fx.brass_fill(p, [(900, y0 + 1), (906, y0 + 1), (906, y0 + 5), (900, y0 + 5)], profile="dome", seed=6)
    out = Image.new("RGBA", (960, 540), (0, 0, 0, 0))
    out.paste(p.finish().crop(PC_BOX), PC_BOX[:2])
    return out


# ------------------------------------------------------------------------------------------------ wires_table


def rope_coil() -> Image.Image:
    p = Pix(960, 540, seed=44)
    fx.coil(p, 790, 278, 18, 6, turns=3, thickness=5, tail=True, seed=12)
    out = Image.new("RGBA", (960, 540), (0, 0, 0, 0))
    out.paste(p.finish().crop((766, 246, 960, 295)), (766, 246))
    return out


# ------------------------------------------------------------------------------------------------ the push-button sheets


def counter_bell(p: Pix, k: int) -> None:
    """Cell 28x18 at (635,314): a brass service bell on the bar. 0 rest, 1 hover (brighter, a glint), 2 pressed (the plunger
    is down, the dome sits lower, the ring lines show it rings)."""
    cx, fy = 14, 15
    fx.contact_shadow(p, fx.ellipse(cx + 3, fy - 1, 12, 3), shift=(3, 1), spread=3, strength=0.9, alpha=190)
    p.ellipse(cx - 12, fy - 5, 25, 7, BRASS[0])                    # the base dish: edge below, face above
    p.ellipse(cx - 12, fy - 6, 25, 7, BRASS[2])
    p.ellipse(cx - 10, fy - 5, 21, 5, BRASS[1])
    p.hline(cx - 9, fy - 6, 8, BRASS[4])
    dip = 1 if k == 2 else 0
    top, base = fy - 13 + dip, fy - 5                               # the dome
    for y in range(top, base + 1):
        s = (y - top) / (base - top)
        hw = 3 + 8 * math.sin(min(1.0, s * 1.15) * math.pi / 2) ** 0.9
        for x in range(round(cx - hw), round(cx + hw) + 1):
            t = (x - cx) / hw
            v = 4 if -0.7 < t < -0.4 else 3 if t < 0.1 else 2 if t < 0.5 else 1 if t < 0.85 else 0
            if k == 1 and v < 4 and t < 0.1:
                v += 1
            p.px(x, y, BRASS[min(4, v)])
    p.hline(cx - 11, base, 23, BRASS[0])
    stem = 4 - (2 if k == 2 else 0)                                 # the plunger: a stem and a button
    p.rect(cx - 1, top - stem, 3, stem, BRASS[1])
    p.ellipse(cx - 3, top - stem - 3, 7, 4, BRASS[0])
    p.ellipse(cx - 3, top - stem - 4, 7, 4, BRASS[3] if k != 1 else BRASS[4])
    p.hline(cx - 2, top - stem - 3, 3, BRASS[4])
    if k == 1:
        p.px(cx - 8, top + 2, (255, 245, 200))
        p.px(cx - 7, top + 2, BRASS[4])
        p.px(cx - 8, top + 1, BRASS[4])
        p.px(cx - 8, top + 3, BRASS[4])
    if k == 2:
        for dx, yy in ((-13, top + 3), (13, top + 3), (-12, top + 6), (12, top + 6)):
            p.px(cx + dx, yy, BRASS[4])
            p.px(cx + dx + (1 if dx < 0 else -1), yy - 1, BRASS[2])


def shutter_pull(p: Pix, k: int) -> None:
    """Cell 31x30 on the wall beside the window: an iron plate with a brass pulley, a chain and a brass pull-ring. 0 rest,
    1 hover (ring bright, a glint), 2 pulled (the chain is taut and the ring sits lower, the pulley turned)."""
    drop = 4 if k == 2 else 0
    fx.wall_shadow(p, [(2, 1), (29, 1), (29, 11), (2, 11)], offset=(2, 2), spread=2, strength=0.8, alpha=170)
    fx.iron_fill(p, (2, 1, 27, 10), hammer=0.5, rust=0.3, rivets=0, seed=61)
    for rx, ry in ((4, 3), (26, 3), (4, 8), (26, 8)):
        fx.rivet(p, rx, ry, 1, BRASS)
    # pulley: a brass wheel on an axle, the groove shows the chain
    p.ellipse(10, 2, 11, 9, BRASS[0])
    fx.brass_fill(p, fx.ellipse(15, 6, 5, 4), profile="dome", seed=62)
    p.px(15, 6, IRON[1])
    spoke = (k == 2)
    p.px(15 + (1 if spoke else -1), 5 if spoke else 7, BRASS[1])
    # the chain from the pulley down to the ring; the rest chain hangs a little loose, the pulled chain is straight
    sag = 0 if k == 2 else 1
    pts = [(15 + (sag if i in (6, 7, 8) else 0) * (1 if i % 2 else 0), 10 + i) for i in range(0, 11 + drop)]
    for i, (x, y) in enumerate(pts):
        c = IRON[4] if i % 2 == 0 else IRON[2]
        p.px(x, y, c)
        p.px(x - 1 if i % 2 == 0 else x + 1, y, IRON[3] if i % 2 == 0 else IRON[1])
        p.px(x + 2, y + 1, (28, 20, 24, 140))
    ex, ey = pts[-1]
    # the pull: a brass ring
    ring = BRASS[4] if k == 1 else BRASS[3]
    p.ellipse(ex - 4, ey + 1, 9, 9, BRASS[0])
    p.ellipse(ex - 4, ey, 9, 9, ring)
    p.ellipse(ex - 2, ey + 2, 5, 5, (30, 22, 18, 0))
    for yy in range(ey + 2, ey + 7):
        for xx in range(ex - 2, ex + 3):
            if ((xx - ex) / 2.3) ** 2 + ((yy - ey - 4) / 2.5) ** 2 < 1:
                p.px(xx, yy, (0, 0, 0, 0))
    p.px(ex - 3, ey + 2, BRASS[4])
    p.px(ex - 3, ey + 3, BRASS[4])
    if k == 1:
        p.px(ex - 4, ey + 1, (255, 245, 200))
    p.px(ex, ey - 1, BRASS[2])
    # the wall shadow of ring and chain
    p.px(ex + 4, ey + 7, (28, 20, 24, 130))


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "phone.960x540.png": phone,
    "marketplace_pc.960x540.png": lambda: cabinet(False),
    "marketplace_pc_notif.960x540.png": lambda: cabinet(True),
    "wires_table.960x540.png": rope_coil,
    "bell_button_sheet.101x34.png": lambda: sheet((101, 34), 3, 3, 33, 8, 28, 18, counter_bell, 20),
    "shutter_button_sheet.101x34.png": lambda: sheet((101, 34), 3, 2, 33, 2, 31, 30, shutter_pull, 21),
}
