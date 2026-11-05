"""Helpers for the tool-family item sprites: boxes that fill the game's cells, shaded slabs and cylinders, iron, brass,
glass, wood grain, small bitmaps. Everything is whole pixels, light from the upper left, outline in SHADOW."""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image

from palette import BRASS, EMBER, FLAME, GLASS, IRON, LEATHER, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix, Ramp, mix, rgb

# Opaque area (x0.y0.x1.y1) of each original: the cells the item occupies in the game's grid.
_BOXES = """book1=2.3.30.46 c4=1.5.46.43 cigarette_color_guide=2.1.14.15 newspaper=2.2.46.31 page3=6.2.27.30 paper_wanted=1.3.31.45 scav_medal=1.1.15.31 small_flash=1.1.15.31 small_smoke=1.1.15.31 tutorial_book=2.5.30.43 tutorial_book_full=2.5.30.43 tutorial_page=6.2.27.30 unknown=2.2.14.14 nuts_metal_pile=3.6.29.28 wire=2.6.31.27 hand_carbon=5.2.28.46 hand_gold=5.2.28.47 hand_steel=5.2.28.46 battery_hyp=2.1.14.31 blender=5.1.43.47 blender_b=5.1.43.47 chem_finisher=2.2.47.47 chem_finisher_b=2.2.47.47 current_converter=1.2.15.30 current_converter_off=1.2.15.30 evaporator=1.1.47.47 evaporator_b=1.1.47.47 furnace=1.2.47.47 furnace_on=1.2.47.47 gibber=3.1.45.47 heating_plate=4.1.44.47 heating_plate_b=4.1.44.47 hypertech_bay=1.0.47.48 machine_bay0=5.3.59.60 machine_bay1=5.3.59.60 machine_bay2=5.3.59.60 machine_bay3=7.2.61.59 machine_bay4=5.3.59.60 machine_bay_ext=1.0.63.64 printer_off=1.2.47.47 printer_on=1.2.47.47 projector=3.4.45.44 purifier=2.3.46.63 purifier_on=2.3.46.63 purifier_w=2.2.46.62 sbattery0=2.3.14.29 sbattery10=2.3.14.29 sbattery100=2.3.14.29 sbattery20=2.3.14.29 sbattery40=2.3.14.29 sbattery60=2.3.14.29 sbattery80=2.3.14.29 storage_bay_expansion_kit=1.1.31.30 toolbox_new=5.4.59.43 toolbox_old=5.4.59.43 turbo_booster_hypertech=3.1.46.48 water_tank=7.2.57.62 alarm_system=3.5.45.43 alarm_system_r=3.5.45.43 aug_scanner=3.2.27.46 battery0=2.3.14.29 battery10=2.3.14.29 battery100=2.3.14.29 battery20=2.3.14.29 battery40=2.3.14.29 battery60=2.3.14.29 battery80=2.3.14.29 battery_bar=0.0.4.10 battery_dis0=2.1.14.31 battery_dis10=2.1.14.31 battery_dis100=2.1.14.31 battery_dis20=1.1.13.31 battery_dis40=2.1.14.31 battery_dis60=2.1.14.31 battery_dis80=2.1.14.31 battery_ext0=2.1.14.31 battery_ext10=2.1.14.31 battery_ext100=2.1.14.31 battery_ext20=2.1.14.31 battery_ext40=2.1.14.31 battery_ext60=2.1.14.31 battery_ext80=2.1.14.31 bottle_printer=1.2.31.47 cmd_module=5.1.27.15 dealmaker=2.2.46.30 desequencer=2.1.46.47 desequencer_r=2.1.46.47 eng_module=5.1.27.15 hopper_in=1.1.31.31 hopper_out=1.1.31.31 labeler=1.4.30.45 labeler_blue=1.4.30.45 magnifier=3.5.43.44 med_module=5.1.27.15 mind_reprogrammer=4.1.44.31 moisture_farm=2.1.46.47 moisture_farm_w=2.1.46.47 postit=4.5.28.27 powerblock=2.2.30.31 powerblock_on=2.2.30.31 printer_chip1=1.1.15.15 printer_chip2=1.1.15.15 printer_chip3=1.1.15.15 printer_chip4=1.1.15.15 printer_chip5=1.1.15.15 printer_chip6=1.1.15.15 printer_chip_pistol=1.1.15.15 recharger_base=0.9.64.32 recharger_g=0.0.2.1 recharger_o=0.0.2.1 recharger_top=0.0.64.10 sci_module=5.1.27.15 screwdriver_s=4.1.12.47 sec_module=5.1.27.15 ser_module=5.1.27.15 storage_coordinator=3.4.45.45 sup_module=5.1.27.15 surgery_toolkit=2.1.62.31 turbo_booster=1.1.47.31 turbo_booster_adv=1.1.47.31 turbo_booster_adv_charging=1.1.47.31 turbo_booster_adv_ready=1.1.47.31 welder_s=0.6.16.60 wirecutter=1.3.15.46"""
BOX: dict[str, tuple[int, int, int, int]] = {
    k: tuple(int(v) for v in b.split(".")) for k, b in (e.split("=") for e in _BOXES.split())}  # type: ignore[misc]
for _n in range(1, 9):                      # the hopper frames fill the same square as the plain hoppers
    BOX[f"hopper_in_{_n}"] = BOX[f"hopper_out_{_n}"] = (1, 1, 31, 31)

AMETHYST: Ramp = (rgb("#1f1230"), rgb("#3a2158"), rgb("#5b3a86"), rgb("#8460b0"), rgb("#ad92d4"))
COPPER: Ramp = (rgb("#2e140d"), rgb("#5e2a17"), rgb("#8f4423"), rgb("#bd6a35"), rgb("#e29a5a"))
TEAL: Ramp = (rgb("#0c2428"), rgb("#14444a"), rgb("#1f6e72"), rgb("#34a09a"), rgb("#7fd0c0"))
SLATE: Ramp = (rgb("#16141a"), rgb("#242229"), rgb("#34313a"), rgb("#47444f"), rgb("#625e6b"))
CLAY: Ramp = (rgb("#3a1d17"), rgb("#6a3426"), rgb("#9a4e33"), rgb("#c06c46"), rgb("#dc9066"))
INK = rgb("#2a1d2a")
WATER: Ramp = (rgb("#12303f"), rgb("#1f5870"), rgb("#2f86a0"), rgb("#58b4c0"), rgb("#a4e0dc"))
LIGHT = rgb("#fff0b8")


def r5(r: Ramp) -> Ramp:
    """A ramp of exactly five tones (four-tone ramps get a lighter top)."""
    return tuple(r) if len(r) == 5 else (*r, mix(r[-1], (255, 240, 200), 0.35))  # type: ignore[return-value]


def finish(p: Pix, edge: Color = SHADOW) -> Image.Image:
    """Outlines the shape on its transparent side: the art is drawn one pixel inside the box."""
    p.outline(edge)
    return p.im


def inset(name: str) -> tuple[int, int, int, int]:
    """x, y, w, h of the box minus the one-pixel rim the outline will take."""
    x0, y0, x1, y1 = BOX[name]
    return x0 + 1, y0 + 1, x1 - x0 - 2, y1 - y0 - 2


def slab(p: Pix, x: int, y: int, w: int, h: int, r: Ramp, grain: bool = False) -> None:
    """A flat block: lit top and left edge, dark bottom and right edge."""
    r = r5(r)
    p.rect(x, y, w, h, r[2])
    if grain and h > 3:
        for yy in range(y + 2, y + h - 1, 3):
            p.dither(x + 1, yy, w - 2, 1, r[1], 0.5)
    p.hline(x, y, w, r[3])
    p.vline(x, y, h, r[3])
    p.hline(x, y + h - 1, w, r[1])
    p.vline(x + w - 1, y, h, r[1])
    p.px(x, y, r[4])
    p.px(x + w - 1, y + h - 1, r[0])


def corners(p: Pix, x: int, y: int, w: int, h: int, n: int = 1) -> None:
    """Rounds the four corners of a rectangle by clearing pixels."""
    for i in range(n):
        for j in range(n - i):
            for cx, cy in ((x + i, y + j), (x + w - 1 - i, y + j), (x + i, y + h - 1 - j), (x + w - 1 - i, y + h - 1 - j)):
                p.px(cx, cy, CLEAR)


def _band(t: float, r: Ramp) -> Color:
    return r[2] if t < 0.12 else r[4] if t < 0.3 else r[3] if t < 0.5 else r[2] if t < 0.72 else r[1] if t < 0.9 else r[0]


def vcyl(p: Pix, x: int, y: int, w: int, h: int, r: Ramp) -> None:
    """A vertical cylinder, lit on the left."""
    r = r5(r)
    for i in range(w):
        p.vline(x + i, y, h, _band(i / max(1, w - 1), r))


def hcyl(p: Pix, x: int, y: int, w: int, h: int, r: Ramp) -> None:
    """A horizontal cylinder, lit from above."""
    r = r5(r)
    for j in range(h):
        p.hline(x, y + j, w, _band(j / max(1, h - 1), r))


def ball(p: Pix, x: int, y: int, d: int, r: Ramp) -> None:
    """A lit sphere / disc of diameter d (modelled on its own canvas so the ground behind is not touched)."""
    r = r5(r)
    t = Pix(d, d)
    t.ellipse(0, 0, d, d, r[2])
    for yy in range(d):
        for xx in range(d):
            if t.get(xx, yy)[3] == 0:
                continue
            dx, dy = (xx - (d - 1) / 2) / (d / 2), (yy - (d - 1) / 2) / (d / 2)
            s = -0.6 * dx - 0.7 * dy
            t.px(xx, yy, r[4] if s > 0.62 else r[3] if s > 0.18 else r[2] if s > -0.3 else r[1] if s > -0.7 else r[0])
    p.paste(t, x, y)


def rivets(p: Pix, pts: Sequence[tuple[int, int]], r: Ramp = BRASS) -> None:
    for x, y in pts:
        p.px(x, y, r[3])


def grain(p: Pix, x: int, y: int, w: int, h: int, r: Ramp, vertical: bool = False) -> None:
    """Wood grain: short dark streaks and a few lit ones."""
    r = r5(r)
    for _ in range(max(2, w * h // 14)):
        a, b, ln = p.rng.randrange(w), p.rng.randrange(h), p.rng.randrange(2, 6)
        c = r[1] if p.rng.random() < 0.7 else r[3]
        for k in range(ln):
            xx, yy = (x + a, y + b + k) if vertical else (x + a + k, y + b)
            if x <= xx < x + w and y <= yy < y + h:
                p.px(xx, yy, c)


def plank_box(p: Pix, x: int, y: int, w: int, h: int, r: Ramp, vertical: bool = True, grained: bool = True) -> None:
    """A wooden face made of boards with joints and grain."""
    slab(p, x, y, w, h, r)
    r = r5(r)
    if vertical:
        for xx in range(x + 4, x + w - 2, 5):
            p.vline(xx, y + 1, h - 2, r[1])
            p.vline(xx + 1, y + 1, h - 2, r[3])
    else:
        for yy in range(y + 4, y + h - 2, 5):
            p.hline(x + 1, yy, w - 2, r[1])
            p.hline(x + 1, yy + 1, w - 2, r[3])
    if grained:
        grain(p, x + 1, y + 1, w - 2, h - 2, r, vertical)


def strap_h(p: Pix, x: int, y: int, w: int, t: int = 3, r: Ramp = IRON, studs: bool = True) -> None:
    """An iron band across (horizontal) with brass studs."""
    slab(p, x, y, w, t, r)
    if studs and t >= 3:
        for xx in range(x + 2, x + w - 1, 6):
            p.px(xx, y + t // 2, BRASS[3])


def strap_v(p: Pix, x: int, y: int, h: int, t: int = 3, r: Ramp = IRON, studs: bool = True) -> None:
    slab(p, x, y, t, h, r)
    if studs and t >= 3:
        for yy in range(y + 2, y + h - 1, 6):
            p.px(x + t // 2, yy, BRASS[3])


def glass(p: Pix, x: int, y: int, w: int, h: int, r: Ramp = GLASS, lit: bool = False) -> None:
    """A pane: dark back, a lit diagonal glint."""
    r = r5(r)
    p.rect(x, y, w, h, r[1] if not lit else r[3])
    p.hline(x, y, w, r[0])
    p.vline(x, y, h, r[0])
    for k in range(min(w, h) // 2):
        p.px(x + 1 + k, y + h - 2 - k, r[3] if not lit else r[4])
    if w > 5 and h > 5:
        p.px(x + w - 2, y + 1, r[2] if not lit else r[4])


def lamp(p: Pix, x: int, y: int, w: int, h: int, on: bool, color: Ramp = FLAME) -> None:
    """A little lantern window: amber when on, dark glass when off."""
    p.rect(x, y, w, h, SHADOW)
    if on:
        p.rect(x + 1, y + 1, max(1, w - 2), max(1, h - 2), color[2])
        p.px(x + 1, y + 1, color[4])
    else:
        p.rect(x + 1, y + 1, max(1, w - 2), max(1, h - 2), GLASS[1])
        p.px(x + 1, y + 1, GLASS[3])


def bitmap(p: Pix, x: int, y: int, rows: Sequence[str], colors: dict[str, Color]) -> None:
    """Paints a small picture from text rows; characters not in `colors` are left alone."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                p.px(x + i, y + j, colors[ch])


def sparkle(p: Pix, x: int, y: int, c: Color = LIGHT) -> None:
    p.px(x, y, c)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, mix(c, FLAME[1], 0.5))


def solid(p: Pix, pts: Sequence[tuple[int, int]], r: Ramp, rim: bool = True) -> None:
    """Fills a polygon with a material and models it: a lit rim on the upper-left edges, a dark rim on the lower-right ones."""
    r = r5(r)
    mask = Image.new("L", (p.w, p.h), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).polygon(list(pts), fill=255)
    m = mask.load()

    def on(x: int, y: int) -> bool:
        return 0 <= x < p.w and 0 <= y < p.h and m[x, y] > 0  # type: ignore[index]

    for y in range(p.h):
        for x in range(p.w):
            if not on(x, y):
                continue
            if not rim:
                p.px(x, y, r[2])
            elif not on(x - 1, y) or not on(x, y - 1):
                p.px(x, y, r[4] if (not on(x - 1, y) and not on(x, y - 1)) else r[3])
            elif not on(x + 1, y) or not on(x, y + 1):
                p.px(x, y, r[0] if (not on(x + 1, y) and not on(x, y + 1)) else r[1])
            elif not on(x - 1, y - 1):
                p.px(x, y, r[3])
            elif not on(x + 1, y + 1):
                p.px(x, y, r[1])
            else:
                p.px(x, y, r[2])


def tube(p: Pix, a: tuple[int, int], b: tuple[int, int], width: int, r: Ramp) -> None:
    """A straight bar of a given width between two points, modelled like `solid`."""
    import math
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1
    ox, oy = -dy / n * width / 2, dx / n * width / 2
    solid(p, [(round(a[0] + ox), round(a[1] + oy)), (round(b[0] + ox), round(b[1] + oy)),
              (round(b[0] - ox), round(b[1] - oy)), (round(a[0] - ox), round(a[1] - oy))], r)


def ring(p: Pix, cx: int, cy: int, rx: int, ry: int, r: Ramp, thick: int = 2) -> None:
    """An elliptical ring (hoop), lit on the upper left; the middle keeps what is behind it."""
    r = r5(r)
    w, h = 2 * rx + 1, 2 * ry + 1
    t = Pix(w, h)
    t.ellipse(0, 0, w, h, r[2])
    t.ellipse(thick, thick, w - 2 * thick, h - 2 * thick, CLEAR)
    for y in range(h):
        for x in range(w):
            if t.get(x, y)[3] == 0:
                continue
            s = -(x - rx) / max(1, rx) - (y - ry) / max(1, ry)
            t.px(x, y, r[4] if s > 0.9 else r[3] if s > 0.3 else r[2] if s > -0.4 else r[1] if s > -0.9 else r[0])
    p.paste(t, cx - rx, cy - ry)
