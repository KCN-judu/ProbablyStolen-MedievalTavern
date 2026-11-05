"""Make-up and marks: scars, soot, dirt, rouge, freckles, stubble, moustaches, painted lines, tattoos, bandages.

Anchors lie on face landmarks (cheek_l/cheek_r/eyes/nose/mouth/jaw/forehead); `width` is the head width the part was drawn
for. Translucent parts (`alpha_part`) are tints the composer blends onto skin pixels only.
"""

from __future__ import annotations

import math
import random

from kit import RAMPS
from kit import Art as _Art
from partdef import Part

def Art(w: int, h: int, seed: int = 0) -> _Art:
    a = _Art(w, h, seed)
    a.inside = False      # marks are drawn on empty canvas
    return a


SIZES = {"S": 40, "M": 46, "L": 52}


def _mk(id_: str, style: str, a: Art, anchor: tuple[int, int], landmark: str, width: int, colour: str = "", size: str = "",
        tags: list[str] | None = None, alpha: bool = False, layer: str = "front") -> Part:
    return Part(id=id_, cat="marks", style=style, img=a.im, anchor=anchor, landmark=landmark, layer=layer, width=width,
                colour=colour, size=size, tags=tags or [], clip=True, alpha_part=alpha)


def _blob(a: Art, cx: float, cy: float, rx: float, ry: float, col: tuple[int, int, int], alpha: int, seed: int, ragged: float = 0.35) -> None:
    """A soft smudge made of whole pixels: opaque-ish pixels thinning out toward a ragged edge (ordered + random dither)."""
    rng = random.Random(seed)
    for y in range(int(cy - ry - 2), int(cy + ry + 3)):
        for x in range(int(cx - rx - 2), int(cx + rx + 3)):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d < 1.0 + ragged * 0.2:
                p = (1 - d) * 1.4 + (rng.random() - 0.5) * ragged
                if p > 0.35:
                    a.px(x, y, col, alpha if p > 0.7 else alpha // 2)


def _flip(a: Art) -> None:
    a.im = a.im.transpose(0)


def scar(kind: str, flip: bool) -> Part:
    a = Art(24, 24, 3 + len(kind))
    core, lip, st = (146, 66, 72), (226, 164, 150), (88, 46, 54)
    paths = {
        "cheek": [(3, 3), (7, 8), (12, 13), (17, 19)],
        "slash": [(2, 12), (8, 10), (14, 11), (21, 8)],
        "brow": [(12, 2), (11, 8), (12, 14), (10, 20)],
        "chin": [(6, 4), (8, 9), (7, 15)],
    }
    pts = paths[kind]
    a.line(pts, lip, 1)
    a.line([(x + 1, y) for x, y in pts], core, 1)
    n = len(pts) - 1
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        for t in (0.35, 0.8):
            x, y = x0 + (x1 - x0) * t + 1, y0 + (y1 - y0) * t
            dx, dy = (y1 - y0), -(x1 - x0)
            ln = math.hypot(dx, dy) or 1
            a.line([(x - dx / ln * 2, y - dy / ln * 2), (x + dx / ln * 2, y + dy / ln * 2)], st, 1)
    if flip:
        _flip(a)
    lm = "cheek_l" if kind in ("cheek", "slash") and not flip else "cheek_r" if kind in ("cheek", "slash") else "forehead" if kind == "brow" else "jaw"
    return _mk(f"scar_{kind}{'_r' if flip else ''}", "scar", a, (12, 12), lm, 46, tags=["scar", "merc", "rebel", "watch"])


def soot(kind: str) -> Part:
    a = Art(34, 22, 5 + len(kind))
    c = (40, 28, 30)
    if kind == "cheek":
        _blob(a, 17, 11, 12, 7, c, 150, 11)
        _blob(a, 12, 9, 6, 4, c, 190, 12)
    elif kind == "nose":
        _blob(a, 17, 11, 9, 4, c, 160, 21)
        _blob(a, 12, 11, 4, 3, c, 190, 22)
    elif kind == "streak":
        for k in range(4):
            a.line([(6 + k * 6, 4 + k % 2), (9 + k * 6, 14)], c)
            a.line([(7 + k * 6, 5), (10 + k * 6, 11)], (60, 42, 42))
    else:
        _blob(a, 17, 11, 14, 8, c, 120, 31)
    return _mk(f"soot_{kind}", "soot", a, (17, 11), "nose" if kind in ("nose", "streak") else "cheek_r", 46, tags=["soot", "smith", "cook", "commoner", "dirt"], alpha=True)


def dirt(kind: str, flip: bool = False) -> Part:
    a = Art(30, 20, 7 + len(kind))
    c = (92, 66, 44)
    _blob(a, 15, 10, 11, 6, c, 120, 41 + len(kind), 0.7)
    for _ in range(10):
        a.px(a.rng.randrange(4, 26), a.rng.randrange(3, 17), (64, 44, 32), 160)
    if flip:
        _flip(a)
    return _mk(f"dirt_{kind}{'_r' if flip else ''}", "dirt", a, (15, 10), "cheek_r" if flip else "cheek_l", 46, tags=["dirt", "farmer", "commoner", "merc"], alpha=True)


def rouge(tone: str, hw: int, sz: str) -> Part:
    cols = {"rose": (214, 96, 104), "warm": (206, 108, 78)}
    a = Art(hw + 6, 16, 9 + hw)
    ax = (hw + 6) // 2
    for sx in (-1, 1):
        _blob(a, ax + sx * 0.28 * hw, 8, 5.5, 3.6, cols[tone], 110, 51 + sx, 0.25)
    return _mk(f"rouge_{tone}_{sz}", "rouge", a, (ax, 8), "cheek_c", hw, tone, sz, tags=["rouge", "female", "gentry", "lowcheek"], alpha=True)


def lips(tone: str) -> Part:
    cols = {"rose": (190, 84, 94), "wine": (140, 52, 66)}
    a = Art(14, 7, 13)
    c = cols[tone]
    for x in range(3, 11):
        a.px(x, 3, c, 200)
    for x in range(4, 10):
        a.px(x, 2, c, 170), a.px(x, 4, c, 200)
    a.px(7, 5, (240, 170, 160), 120)
    return _mk(f"lips_{tone}", "lips", a, (7, 3), "mouth", 46, tone, tags=["lips", "female", "gentry"], alpha=True)


def freckles(dense: int, hw: int, sz: str) -> Part:
    a = Art(hw + 2, 18, 17 + dense + hw)
    ax = (hw + 2) // 2
    rng = random.Random(a.seed)
    for sx in (-1, 1):
        for _ in range(dense):
            x = ax + sx * rng.uniform(0.1, 0.38) * hw
            y = 9 + rng.uniform(-5, 5) + abs(x - ax) * 0.0
            a.px(round(x), round(y), (140, 86, 58), 170)
    for _ in range(dense // 2):  # across the nose bridge
        a.px(ax + rng.randrange(-3, 4), 8 + rng.randrange(-3, 3), (140, 86, 58), 150)
    return _mk(f"freckles_{dense}_{sz}", "freckles", a, (ax, 9), "cheek_c", hw, size=sz, tags=["freckles", "farmer", "commoner", "young"], alpha=True)


def stubble(dens: str, col: str, hw: int, sz: str) -> Part:
    """Dithered beard shadow over jaw and chin, with a gap for the mouth."""
    tone = {"dark": (40, 28, 30), "brown": (70, 48, 36), "grey": (120, 112, 112)}[col]
    h = int(0.52 * hw)
    a = Art(hw + 2, h, 19 + hw)
    ax = (hw + 2) // 2
    lvl = {"light": 5, "mid": 8, "heavy": 11}[dens]
    from pix import BAYER
    px = a.im.load()
    for y in range(h):
        for x in range(hw + 2):
            u = (x - ax) / (hw / 2 - 2)
            # jaw outline: a half-ellipse whose top is the cheek line
            top = 0.05 * h + 0.35 * h * abs(u) ** 2
            bot = h * (0.98 - 0.34 * abs(u) ** 3)
            if abs(u) < 1 and top <= y <= bot:
                mouth = ((x - ax) / (0.19 * hw)) ** 2 + ((y - 0.28 * h) / (0.1 * h + 1)) ** 2 < 1
                if not mouth and BAYER[y % 4][x % 4] < lvl and (x * 7 + y * 3) % 5:
                    px[x, y] = (*tone, 150 if dens != "heavy" else 175)
    return _mk(f"stubble_{dens}_{col}_{sz}", "stubble", a, (ax, 0), "mouth", hw, col, sz, tags=["stubble", "beard", "male"], alpha=True)


def moustache(style: str, col: str) -> Part:
    ramp = {"dark": RAMPS["black"], "brown": RAMPS["brown"], "grey": RAMPS["grey"], "red": RAMPS["rust"]}[col]
    a = Art(30, 14, 23 + len(style))
    ax = 15
    if style == "walrus":
        m = a.mask().ellipse(ax - 6, 6, 7, 4).add(a.mask().ellipse(ax + 6, 6, 7, 4)).add(a.mask().poly([(ax - 12, 6), (ax - 10, 12), (ax - 6, 8)])).add(a.mask().poly([(ax + 12, 6), (ax + 10, 12), (ax + 6, 8)]))
    elif style == "thin":
        m = a.mask().line([(ax - 11, 8), (ax - 6, 5), (ax, 5), (ax + 6, 5), (ax + 11, 8)], 2)
    elif style == "handlebar":
        m = a.mask().ellipse(ax - 5, 6, 6, 2.6).add(a.mask().ellipse(ax + 5, 6, 6, 2.6))
        m.line([(ax - 10, 6), (ax - 13, 7), (ax - 13, 3)], 1).line([(ax + 10, 6), (ax + 13, 7), (ax + 13, 3)], 1)
    else:  # soft
        m = a.mask().ellipse(ax, 6, 10, 3.4).add(a.mask().poly([(ax - 9, 6), (ax - 11, 10), (ax - 5, 7)])).add(a.mask().poly([(ax + 9, 6), (ax + 11, 10), (ax + 5, 7)]))
    a.fill(m, ramp, radius=1.8, base=0.62)
    return _mk(f"moustache_{style}_{col}", "moustache", a, (ax, 5), "nose", 46, col, tags=["moustache", "male", "gentry", "commoner"])


def warpaint(kind: str, col: str) -> Part:
    pal = {"red": (176, 44, 44), "white": (232, 224, 204), "blue": (50, 80, 150), "ochre": (206, 150, 52)}[col]
    dark = tuple(int(c * 0.62) for c in pal)
    a = Art(34, 22, 29 + len(kind))
    if kind == "bar":      # one short diagonal bar over the cheek
        a.line([(11, 6), (22, 13)], dark, 3)
        a.line([(11, 5), (22, 12)], pal, 2)
    elif kind == "twin":   # two parallel strokes
        for k in (0, 5):
            a.line([(10 + k, 5), (14 + k, 14)], dark, 2)
            a.line([(10 + k, 4), (14 + k, 13)], pal, 1)
    elif kind == "eyeband":  # a thin band across the cheekbones, just under the eyes
        a.line([(2, 10), (31, 10)], dark, 2)
        a.line([(2, 9), (31, 9)], pal, 1)
    elif kind == "dots":
        for i in range(5):
            a.px(7 + i * 5, 7 + (i % 2) * 5, pal), a.px(8 + i * 5, 7 + (i % 2) * 5, dark)
    lm = "cheek_c" if kind == "eyeband" else "cheek_l" if kind in ("bar", "twin") else "cheek_r"
    return _mk(f"warpaint_{kind}_{col}", "warpaint", a, (17, 10), lm, 46, col, tags=["paint", "rebel", "merc"])


def tattoo(kind: str) -> Part:
    ink = (40, 56, 92)
    a = Art(20, 20, 31 + len(kind))
    if kind == "spiral":
        pts = [(10 + math.cos(t / 3) * (1 + t / 9), 10 + math.sin(t / 3) * (1 + t / 9)) for t in range(0, 40)]
        a.line(pts, ink)
    elif kind == "rune":
        a.line([(10, 3), (10, 17)], ink), a.line([(10, 8), (15, 4)], ink), a.line([(10, 11), (15, 7)], ink)
    elif kind == "tear":
        a.px(10, 5, ink), a.px(10, 6, ink), a.px(9, 7, ink), a.px(10, 7, ink), a.px(11, 7, ink), a.px(10, 8, ink)
    else:  # lines
        for k in range(3):
            a.line([(4 + k * 5, 4), (4 + k * 5, 15)], ink)
    return _mk(f"tattoo_{kind}", "tattoo", a, (10, 10), "cheek_l" if kind != "rune" else "forehead", 46, tags=["tattoo", "rebel", "merc"], alpha=False)


def bandage(kind: str) -> Part:
    ramp = RAMPS["linen"]
    stain = (150, 50, 50)
    if kind == "cheek":
        a = Art(18, 12, 37)
        a.fill(a.mask().rect(1, 3, 16, 8), ramp, tex="linen", radius=1.6, base=0.62)
        a.fill(a.mask().rect(6, 1, 11, 10), ramp, radius=1.6, base=0.66)
        a.px(8, 5, stain), a.px(9, 5, stain), a.px(8, 6, (110, 36, 40))
        anchor, lm = (9, 6), "cheek_r"
    elif kind == "brow":
        a = Art(52, 9, 38)
        a.fill(a.mask().rect(1, 1, 50, 7), ramp, tex="linen", radius=1.8, base=0.62)
        a.line([(2, 4), (49, 4)], ramp[1])
        a.px(30, 3, stain), a.px(31, 3, stain), a.px(31, 4, (110, 36, 40))
        anchor, lm = (26, 4), "forehead"
    elif kind == "nose":
        a = Art(14, 8, 39)
        a.fill(a.mask().rect(1, 1, 12, 6), ramp, tex="linen", radius=1.4, base=0.62)
        a.line([(2, 3), (11, 3)], ramp[1])
        anchor, lm = (7, 4), "nose"
    else:  # eyepatch with strap
        lea = RAMPS["black"]
        a = Art(52, 20, 40)
        a.line([(1, 3), (14, 9)], lea[1], 2), a.line([(40, 9), (51, 3)], lea[1], 2)
        a.fill(a.mask().ellipse(21, 10, 8, 7), lea, tex="leather", radius=2.5, base=0.6)
        a.line([(18, 7), (24, 6)], lea[4])
        anchor, lm = (21, 10), "eye_l"
    return _mk(f"bandage_{kind}" if kind != "eyepatch" else "eyepatch", "bandage", a, anchor, lm, 46, tags=["bandage", "wound", "merc", "rebel", "watch"], alpha=False)


def tired(hw: int, sz: str) -> Part:
    a = Art(hw + 2, 12, 41 + hw)
    ax = (hw + 2) // 2
    for sx in (-1, 1):
        _blob(a, ax + sx * 0.2 * hw, 6, 0.11 * hw + 1, 1.7, (96, 62, 80), 85, 61 + sx, 0.3)
    return _mk(f"tired_{sz}", "tired", a, (ax, 6), "eyes_low", hw, size=sz, tags=["tired", "shadow"], alpha=True)


def bruise() -> Part:
    a = Art(22, 14, 43)
    _blob(a, 11, 7, 9, 5, (96, 58, 108), 120, 71, 0.4)
    _blob(a, 10, 7, 4, 3, (70, 44, 90), 140, 72, 0.3)
    return _mk("bruise", "bruise", a, (11, 7), "cheek_l", 46, tags=["bruise", "merc", "rebel"], alpha=True)


def build() -> list[Part]:
    o: list[Part] = []
    for k in ("cheek", "slash", "brow", "chin"):
        for fl in (False, True):
            o.append(scar(k, fl))
    for k in ("cheek", "nose", "streak", "wide"):
        o.append(soot(k))
    for k in ("a", "b"):
        for fl in (False, True):
            o.append(dirt(k, fl))
    for sz, hw in SIZES.items():
        for t in ("rose", "warm"):
            o.append(rouge(t, hw, sz))
        for d in (6, 12, 20):
            o.append(freckles(d, hw, sz))
        for dn in ("light", "mid", "heavy"):
            for c in ("dark", "brown", "grey"):
                o.append(stubble(dn, c, hw, sz))
        o.append(tired(hw, sz))
    for t in ("rose", "wine"):
        o.append(lips(t))
    for s in ("walrus", "thin", "handlebar", "soft"):
        for c in ("dark", "brown", "grey", "red"):
            o.append(moustache(s, c))
    for k in ("bar", "twin", "eyeband", "dots"):
        for c in ("red", "white", "blue", "ochre"):
            o.append(warpaint(k, c))
    for k in ("spiral", "rune", "tear", "lines"):
        o.append(tattoo(k))
    for k in ("cheek", "brow", "nose", "eyepatch"):
        o.append(bandage(k))
    o.append(bruise())
    return o


def sheet(parts: list[Part], out) -> None:
    """Each mark on a plain mannequin head (scale 3), cropped to the face."""
    from PIL import Image
    import sheets
    cw, ch, ay, hw = 100, 100, 18, 46
    cells = []
    for p in parts:
        if p.size in ("S", "L"):
            continue
        full = sheets.worn(p, hw, 130, 120, 65, 30)
        cells.append((full.crop((15, 18, 115, 118)), p.id))
    sheets.sheet(cells, 12, 2).save(out / "marks_sheet.png")
