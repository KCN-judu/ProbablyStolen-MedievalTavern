"""Headgear parts, drawn from scratch. Every hat is parametrised by the head width `hw` it is drawn for.

Anchor = (centre x, y of the hat's lower edge on the forehead); landmark `brow`. The composer puts that point on the
head's hat line (a little above the brows) and erases the hair above it when the hat is closed.
"""

from __future__ import annotations

from PIL import Image, ImageFilter

from kit import RAMPS, Art, Mask, Ramp
from partdef import Part

SIZES = {"S": 40, "M": 46, "L": 52}


def rot(m: Mask, deg: float, cx: float, cy: float) -> Mask:
    m.im = m.im.rotate(deg, resample=Image.NEAREST, center=(cx, cy))
    from PIL import ImageDraw
    m.d = ImageDraw.Draw(m.im)
    return m


def ring(m: Mask, d: int) -> Mask:
    """Pixels at distance exactly d (1..3) outside of mask m."""
    from PIL import ImageChops, ImageDraw
    bin_ = m.im.point(lambda p: 255 if p > 127 else 0)
    big = bin_.filter(ImageFilter.MaxFilter(2 * d + 1))
    small = bin_.filter(ImageFilter.MaxFilter(2 * d - 1)) if d > 1 else bin_
    out = Mask(m.w, m.h)
    out.im = ImageChops.subtract(big, small)
    out.d = ImageDraw.Draw(out.im)
    return out


def _canvas(hw: int, up: float, down: float, ext: int, seed: int) -> tuple[Art, int, int]:
    W = hw + 2 * ext
    a = Art(W, int(up + down), seed)
    return a, W // 2, int(up)


def _hem(a: Art, hole: Mask, dist: int, ramp: Ramp, tone: int = 3) -> None:
    """A lighter seam row at distance `dist` from the opening, where the cloth is turned over."""
    rg = ring(hole, dist)
    a.over_mask(rg, ramp[tone])


def framed(hw: int, ramp: Ramp, *, pad: float = 2.5, dome: float = 0.46, side: float = 0.38, open_in: float = 4.5,
           open_ro: float = 0.5, open_top: float = 3, cowl: tuple[float, float, float] | None = None, tex: str | None = "linen",
           hem: int = 2, hem_tone: int = 3, up_extra: int = 4, ext: int = 8, seed: int = 1, radius: float = 3.5,
           vbias: float = 0.0, base: float = 0.58, tip: bool = False) -> tuple[Art, int, int, Mask, Mask]:
    """A head-hugging cover with a face opening: coifs, hoods, wimples, mail coifs, kerchief caps.

    cowl = (spread, depth, v_half) adds a drape over the shoulders (spread and depth in head widths, v_half the half
    width of the chest opening as a share of the head width).
    """
    r = hw / 2
    down = (cowl[1] + 0.5) * hw if cowl else (side + 0.1) * hw
    spread = cowl[0] * hw if cowl else 0
    a, ax, ay = _canvas(hw, dome * hw + up_extra, down, ext + int(spread * 0.5) + int(pad), seed)
    body = a.mask().ellipse(ax, ay, r + pad, dome * hw).clip_rows(0, ay + 1)
    body.add(a.mask().rect(ax - r - pad, ay, ax + r + pad, ay + side * hw))
    if cowl:
        sp, dp = cowl[0] * hw, cowl[1] * hw
        top = ay + side * hw * 0.8
        xl, xr = ax - r - pad, ax + r + pad
        # shoulders slope down and out; the hem rises toward the chest like a mozzetta
        left = [(xl, top), (xl - sp * 0.5, top + dp * 0.16), (xl - sp, top + dp * 0.5), (xl - sp * 0.95, ay + dp - 2),
                (xl - sp * 0.5, ay + dp + 2), (ax - 10, ay + dp - 6)]
        right = [(2 * ax - x, y) for x, y in left]
        body.add(a.mask().poly(left + right[::-1]))
    if tip:   # the peak of a hood, folded back and hanging to one side
        top_y = ay - dome * hw
        body.add(a.mask().poly([(ax + r * 0.1, top_y + 3), (ax + r + pad + 8, top_y + dome * hw * 0.5), (ax + r + pad + 9, top_y + dome * hw * 0.78),
                                (ax + r + pad + 2, top_y + dome * hw * 0.6), (ax + r * 0.55, top_y + dome * hw * 0.35)]))
    ro = open_ro * hw
    hole = a.mask().ellipse(ax, ay - open_top + ro, r - open_in, ro)
    if cowl:
        vh = cowl[2] * hw
        hole.add(a.mask().poly([(ax - r + open_in + 2, ay + 0.7 * hw), (ax - vh, ay + 0.9 * hw), (ax, ay + cowl[1] * hw * 0.85),
                                (ax + vh, ay + 0.9 * hw), (ax + r - open_in - 2, ay + 0.7 * hw)]))
    body.sub(hole)
    a.fill(body, ramp, tex=tex, radius=radius, vbias=vbias, base=base)
    if hem:
        _hem(a, hole, hem, ramp, hem_tone)
    return a, ax, ay, body, hole


def _fold_lines(a: Art, ramp: Ramp, ax: int, y0: float, pts: list[tuple[float, float, float, float]]) -> None:
    for x0, yy0, x1, yy1 in pts:
        a.line([(ax + x0, y0 + yy0), (ax + x1, y0 + yy1)], ramp[1])


def mk(id_: str, cat_style: str, a: Art, ax: int, ay: int, hw: int, colour: str, size: str, tags: list[str],
       layer: str = "front", erase: str = "above", landmark: str = "brow") -> Part:
    return Part(id=id_, cat="hats", style=cat_style, img=a.im, anchor=(ax, ay), landmark=landmark, layer=layer, width=hw,
                colour=colour, size=size, tags=tags, erase=erase)


# --------------------------------------------------------------------------------------------- the styles


def coif(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    a, ax, ay, body, hole = framed(hw, ramp, tex="linen", seed=hw)
    r = hw / 2
    # a seam over the crown and the tie strings that hang from the lappets
    a.line([(ax - 2, ay - 0.42 * hw), (ax - 1, ay - 10), (ax, ay - 4)], ramp[1])
    for sx in (-1, 1):
        x = ax + sx * (r - 2)
        a.line([(x, ay + 0.34 * hw), (x + sx, ay + 0.34 * hw + 4)], ramp[1])
        a.px(int(x + sx), int(ay + 0.34 * hw + 5), ramp[0])
    return mk(f"coif_{col}_{size}", "coif", a, ax, ay, hw, col, size, ["coif", "commoner", "cook", "scholar", "female", "male"])


def skullcap(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.34 * hw + 5, 5, 5, hw + 3)
    m = a.mask().ellipse(ax, ay + 1, r + 2.2, 0.36 * hw).clip_rows(0, ay + 2)
    a.fill(m, ramp, tex="wool", radius=3.5)
    band = a.mask().rect(ax - r - 3, ay - 2, ax + r + 3, ay + 1).mul(m)
    a.recolor_mask(band, ramp, [ramp[0], ramp[2], ramp[3], ramp[4], ramp[4]])
    a.line([(ax - r - 1, ay + 2), (ax + r + 1, ay + 2)], ramp[0])
    return mk(f"skullcap_{col}_{size}", "skullcap", a, ax, ay + 1, hw, col, size, ["cap", "scholar", "commoner", "male"])


def leather_cap(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    a, ax, ay, body, hole = framed(hw, ramp, pad=2.2, dome=0.4, side=0.3, open_in=5, open_ro=0.46, tex="leather", hem=1, seed=hw + 9)
    r = hw / 2
    for sx in (-1, 1):  # stud and the strap that ties the ear flaps
        a.px(int(ax + sx * (r - 3)), int(ay + 6), RAMPS["brass"][3])
        a.line([(ax + sx * (r - 2), ay + 0.3 * hw), (ax + sx * (r - 2), ay + 0.3 * hw + 5)], ramp[1])
    a.line([(ax - r - 1, ay - 1), (ax + r + 1, ay - 1)], ramp[1])
    for x in range(int(ax - r + 2), int(ax + r - 1), 6):
        a.px(x, int(ay - 3), RAMPS["brass"][3])
    return mk(f"leathercap_{col}_{size}", "leather_cap", a, ax, ay, hw, col, size, ["watch", "leather", "cap", "smith", "male", "female"])


def hood_back(hw: int, col: str, size: str, peak: bool = False) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.62 * hw + 6, 1.25 * hw, 22, hw + 20)
    m = a.mask().ellipse(ax, ay, r + 6, 0.56 * hw).clip_rows(0, ay + 1)
    m.add(a.mask().poly([(ax - r - 6, ay), (ax - r - 19, ay + 1.1 * hw), (ax + r + 19, ay + 1.1 * hw), (ax + r + 6, ay)]))
    if peak:
        m.add(a.mask().poly([(ax + r - 6, ay - 0.5 * hw), (ax + r + 11, ay - 0.78 * hw), (ax + r + 14, ay - 0.62 * hw), (ax + r + 6, ay - 0.2 * hw)]))
    a.fill(m, ramp, tex="wool", radius=5, base=0.4, strength=0.8)
    return mk(f"hood_back_{col}_{size}", "hood_back", a, ax, ay, hw, col, size, ["hood", "rebel", "dealer", "back"], layer="back", erase="")


def hood_front(hw: int, col: str, size: str) -> Part:
    """A hood framing the face with a rolled-back rim, a peak flopped to one side and a short cowl on the shoulders."""
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay, body, hole = framed(hw, ramp, pad=4.5, dome=0.5, side=0.5, open_in=3.4, open_ro=0.56, open_top=1,
                                   cowl=(0.42, 1.0, 0.18), tex="wool", hem=0, seed=hw + 21, radius=4.5, ext=12, tip=True)
    # the rim is turned back: a lit roll along the opening and a shadow line behind it
    _hem(a, hole, 2, ramp, 4)
    _hem(a, hole, 3, ramp, 3)
    _hem(a, hole, 5, ramp, 1)
    # folds fall from the neck over the shoulders
    for d in (-0.5, -0.32, 0.32, 0.5):
        a.line([(ax + d * hw, ay + 0.8 * hw), (ax + d * hw * 1.5, ay + 0.95 * hw), (ax + d * hw * 1.7, ay + 1.02 * hw)], ramp[1])
    return mk(f"hood_front_{col}_{size}", "hood_front", a, ax, ay, hw, col, size, ["hood", "rebel", "dealer", "front"], erase="above")


def wimple(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    a, ax, ay, body, hole = framed(hw, ramp, pad=5, dome=0.54, side=0.7, open_in=4.5, open_ro=0.5, open_top=2,
                                   cowl=(0.2, 1.05, 0.14), tex="linen", hem=1, seed=hw + 31, radius=4)
    a.line([(ax - 1, ay - 0.5 * hw), (ax - 1, ay - 5)], ramp[1])
    return mk(f"wimple_{col}_{size}", "wimple", a, ax, ay, hw, col, size, ["wimple", "female", "gentry", "physician"])


def veil_back(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.6 * hw + 6, 1.4 * hw, 18, hw + 41)
    m = a.mask().ellipse(ax, ay, r + 7, 0.6 * hw).clip_rows(0, ay + 1)
    m.add(a.mask().poly([(ax - r - 7, ay), (ax - r - 15, ay + 0.9 * hw), (ax - r - 11, ay + 1.4 * hw), (ax + r + 11, ay + 1.4 * hw),
                         (ax + r + 15, ay + 0.9 * hw), (ax + r + 7, ay)]))
    a.fill(m, ramp, tex="linen", radius=4.5, base=0.5, strength=0.8)
    return mk(f"veil_back_{col}_{size}", "veil_back", a, ax, ay, hw, col, size, ["veil", "female", "back"], layer="back", erase="")


def kerchief(hw: int, col: str, size: str, pattern: str = "plain") -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay, body, hole = framed(hw, ramp, pad=2.8, dome=0.47, side=0.3, open_in=4.5, open_ro=0.5, open_top=-1, tex="linen",
                                   hem=1, hem_tone=3, ext=10, seed=hw + 51)
    # the knot at the side and its two tails
    kx, ky = int(ax + r + 1), int(ay + 0.26 * hw)
    k = a.mask().ellipse(kx + 2, ky, 4, 3.5)
    k.add(a.mask().poly([(kx + 2, ky), (kx + 9, ky + 7), (kx + 5, ky + 9)]))
    k.add(a.mask().poly([(kx + 2, ky + 1), (kx + 10, ky + 2), (kx + 9, ky + 5)]))
    a.fill(k, ramp, tex=None, radius=2, rim=True)
    a.line([(kx, ky), (kx + 5, ky + 6)], ramp[1])
    # the fold across the forehead and the pattern
    a.line([(ax - r + 3, ay + 1), (ax, ay - 4), (ax + r - 3, ay - 1)], ramp[1])
    if pattern == "dots":
        for y in range(int(ay - 0.4 * hw), int(ay + 5), 5):
            for x in range(int(ax - r + 2 + (y // 5 % 2) * 3), int(ax + r), 6):
                a.px(x, y, ramp[4])
    elif pattern == "stripe":
        for y in range(int(ay - 0.4 * hw) + 2, int(ay), 6):
            a.line([(ax - r + 3, y), (ax + r - 3, y)], ramp[4])
    return mk(f"kerchief_{col}_{pattern}_{size}", "kerchief", a, ax, ay, hw, col, size, ["kerchief", "female", "commoner", "farmer"])


def _brimmed(hw: int, ramp: Ramp, brim_r: float, crown_h: float, crown_top: float, tex: str, band: Ramp | None,
             seed: int, ext: int = 22, squash: float = 5.5, tilt: float = 0) -> tuple[Art, int, int]:
    r = hw / 2
    a, ax, ay = _canvas(hw, crown_h * hw + squash + 6, squash + 3, ext, seed)
    brim = a.mask().ellipse(ax, ay - 2, r + brim_r, squash)
    if tilt:
        rot(brim, tilt, ax, ay)
    a.fill(brim, ramp, tex=tex, radius=3, base=0.5)
    cr = r + 1
    top = r - crown_top
    crown = a.mask().poly([(ax - cr, ay - 2), (ax - top, ay - crown_h * hw), (ax + top, ay - crown_h * hw), (ax + cr, ay - 2)])
    crown.add(a.mask().ellipse(ax, ay - crown_h * hw, top, 3.5))
    crown.add(a.mask().ellipse(ax, ay - 2, cr, 3.2).clip_rows(ay - 2, ay + 3))
    if tilt:
        rot(crown, tilt * 0.6, ax, ay)
    a.fill(crown, ramp, tex=tex, radius=4, base=0.6)
    if band is not None:
        bm = a.mask().rect(ax - cr - 1, ay - 0.2 * hw, ax + cr + 1, ay + 1).mul(crown)
        a.recolor_mask(bm, ramp, band)
        a.line([(ax - cr, ay - 0.2 * hw - 1), (ax + cr, ay - 0.2 * hw - 1)], band[0])
    return a, ax, ay


def felt_hat(hw: int, col: str, size: str, band: str = "leather") -> Part:
    ramp = RAMPS[col]
    a, ax, ay = _brimmed(hw, ramp, 9, 0.5, 4, "felt", RAMPS[band], hw + 61)
    a.px(ax + 4, ay - 4, RAMPS["brass"][4])
    a.line([(ax + 2, ay - 5), (ax + 6, ay - 5)], RAMPS["brass"][3])
    a.line([(ax - 2, int(ay - 0.5 * hw) + 2), (ax + 3, int(ay - 0.5 * hw) + 6)], ramp[1])  # the pinch of the crown
    return mk(f"felt_{col}_{band}_{size}", "felt_hat", a, ax, ay, hw, col, size, ["hat", "yeoman", "commoner", "male", "farmer"])


def wide_brim(hw: int, col: str, size: str, band: str = "red", straw: bool = False) -> Part:
    ramp = RAMPS[col]
    a, ax, ay = _brimmed(hw, ramp, 17, 0.36, 1, "weave" if straw else "felt", RAMPS[band], hw + 71, ext=26, squash=8)
    return mk(f"widebrim_{col}_{size}", "wide_brim", a, ax, ay, hw, col, size, ["hat", "farmer", "wide", "male", "female", "straw" if straw else "felt"])


def feathered(hw: int, col: str, size: str, feather: str = "cream") -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.5 * hw + 20, 6, 22, hw + 81)
    pts_l, pts_r = [], []
    import math
    for i in range(0, 16):
        t = i / 15
        x = ax + r * 0.2 + t * (r + 8) + 0 * t
        y = ay - 0.12 * hw - 4 - 18 * math.sin(t * math.pi * 0.9) + t * 5
        wd = 5.5 * math.sin(min(1.0, t * 1.15 + 0.12) * math.pi) ** 0.8 + 0.5
        pts_l.append((x, y - wd * 0.5)), pts_r.append((x, y + wd * 0.5))
    fe = a.mask().poly(pts_l + pts_r[::-1])
    cap = a.mask().ellipse(ax + 2, ay - 0.12 * hw, r + 7, 0.26 * hw + 1)
    rot(cap, 7, ax, ay)
    a.fill(cap, ramp, tex="wool", radius=4, base=0.58)
    bandm = a.mask().ellipse(ax, ay - 1, r + 1, 3.6).clip_rows(ay - 4, ay + 3)
    a.fill(bandm, RAMPS["brass" if col in ("black", "charcoal") else "leather"], radius=2)
    a.fill(fe, RAMPS[feather], tex=None, radius=2.2, strength=0.8)
    for p in range(1, 14, 2):
        a.px(int(pts_l[p][0]), int((pts_l[p][1] + pts_r[p][1]) / 2), RAMPS[feather][1])
    return mk(f"feathered_{col}_{feather}_{size}", "feathered_cap", a, ax, ay, hw, col, size, ["hat", "official", "gentry", "feather", "male", "female"])


def guild_cap(hw: int, col: str, size: str, pin: bool = True) -> Part:
    """The flat velvet cap of a guild officer: a wide soft disc on a band."""
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.34 * hw + 6, 6, 12, hw + 91)
    disc = a.mask().ellipse(ax + 3, ay - 0.14 * hw, r + 9, 0.25 * hw)
    rot(disc, 6, ax, ay)
    base = a.mask().ellipse(ax, ay - 2, r + 2, 5).clip_rows(0, ay + 4)
    base.add(a.mask().rect(ax - r - 2, ay - 8, ax + r + 2, ay - 2))
    a.fill(base, ramp, tex="wool", radius=3, base=0.52)
    a.fill(disc, ramp, tex="wool", radius=5, base=0.62)
    a.line([(ax - r, ay + 2), (ax + r, ay + 2)], ramp[0])
    if pin:
        br = RAMPS["brass"]
        a.px(ax + 8, ay - 5, br[2]), a.px(ax + 9, ay - 5, br[3]), a.px(ax + 8, ay - 4, br[1]), a.px(ax + 9, ay - 4, br[2])
    return mk(f"guildcap_{col}_{size}", "guild_cap", a, ax, ay, hw, col, size, ["cap", "official", "guild", "gentry", "male", "female"])


def kettle(hw: int, col: str, size: str) -> Part:
    """A kettle helm: a rounded crown on a wide brim whose underside shows, so the hat has depth."""
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.56 * hw + 16, 10, 18, hw + 101)
    cy = ay - 6                      # centre line of the brim; the front edge falls to about ay + 4
    under = a.mask().ellipse(ax, cy + 2.5, r + 14, 8)
    a.fill(under, ramp, tex=None, radius=3, base=0.2, strength=0.3)
    top = a.mask().ellipse(ax, cy - 0.5, r + 14, 7.5)
    a.fill(top, ramp, tex="plate", radius=3, base=0.52)
    crown = a.mask().ellipse(ax, cy - 2, r + 1, 0.56 * hw).clip_rows(0, cy - 1)
    crown.add(a.mask().ellipse(ax, cy - 2, r + 1, 4.5).clip_rows(cy - 2, cy + 3))
    a.fill(crown, ramp, tex="plate", radius=7, base=0.58, strength=1.25)
    # a specular patch on the upper left of the dome and a ridge where crown meets brim
    sx, sy = ax - 0.5 * r, cy - 0.56 * hw * 0.72
    for dx, dy in ((0, 0), (1, 0), (-1, 1), (0, 1), (-2, 2)):
        a.px(sx + dx, sy + dy, ramp[4])
    a.line([(ax - r - 1, cy), (ax - r * 0.5, cy + 2), (ax + r * 0.5, cy + 2), (ax + r + 1, cy)], ramp[1])
    br_ = RAMPS["brass"]
    for x in range(int(ax - r + 2), int(ax + r), 7):
        a.px(x, cy - 1, br_[3])
        a.px(x + 1, cy, br_[1])
    return mk(f"kettle_{col}_{size}", "kettle_helm", a, ax, ay, hw, col, size, ["helm", "watch", "merc", "iron", "male", "female"])


def sallet(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    a, ax, ay, body, hole = framed(hw, ramp, pad=2.5, dome=0.47, side=0.36, open_in=3.5, open_ro=0.52, open_top=-3, tex="plate",
                                   hem=1, hem_tone=4, ext=8, seed=hw + 111, radius=5, base=0.56)
    r = hw / 2
    a.line([(ax - 5, ay - 0.47 * hw + 3), (ax - 6, ay - 6)], ramp[4])
    br_ = RAMPS["brass"]
    for sx in (-1, 1):
        a.px(int(ax + sx * (r - 2)), int(ay + 2), br_[3])
    return mk(f"sallet_{col}_{size}", "sallet", a, ax, ay, hw, col, size, ["helm", "merc", "iron", "male", "female"])


def sallet_tail(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.4 * hw, 0.7 * hw, 14, hw + 121)
    m = a.mask().poly([(ax - r - 1, ay - 2), (ax - r - 9, ay + 0.5 * hw), (ax - r + 4, ay + 0.62 * hw), (ax + r - 4, ay + 0.62 * hw),
                       (ax + r + 9, ay + 0.5 * hw), (ax + r + 1, ay - 2)])
    a.fill(m, ramp, tex="plate", radius=4, base=0.42)
    return mk(f"sallet_tail_{col}_{size}", "sallet_tail", a, ax, ay, hw, col, size, ["helm", "back", "merc"], layer="back", erase="")


def chain_coif(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    a, ax, ay, body, hole = framed(hw, ramp, pad=3.5, dome=0.5, side=0.5, open_in=3.8, open_ro=0.54, open_top=1,
                                   cowl=(0.5, 1.1, 0.17), tex="mail", hem=1, hem_tone=4, ext=8, seed=hw + 131, radius=4.5, base=0.55)
    return mk(f"mailcoif_{col}_{size}", "mail_coif", a, ax, ay, hw, col, size, ["coif", "merc", "iron", "mail", "male", "female"])


def toque(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.95 * hw + 6, 4, 10, hw + 141)
    m = a.mask()
    m.ellipse(ax, ay - 0.3 * hw, r + 3, 0.2 * hw)
    m.ellipse(ax - r * 0.55, ay - 0.62 * hw, r * 0.62, 0.21 * hw)
    m.ellipse(ax + r * 0.55, ay - 0.62 * hw, r * 0.62, 0.21 * hw)
    m.ellipse(ax, ay - 0.78 * hw, r * 0.78, 0.2 * hw)
    m.rect(ax - r - 1, ay - 8, ax + r + 1, ay)
    a.fill(m, ramp, tex="linen", radius=4.5, base=0.62)
    cuff = a.mask().rect(ax - r - 1, ay - 8, ax + r + 1, ay)
    a.recolor_mask(cuff, ramp, [ramp[0], ramp[2], ramp[3], ramp[3], ramp[4]])
    a.line([(ax - r - 1, ay - 8), (ax + r + 1, ay - 8)], ramp[1])
    for k, d in enumerate((-0.62, -0.32, 0.0, 0.32, 0.62)):
        x = ax + d * r * 1.6
        a.line([(x, ay - 9), (x + d * 3, ay - 0.5 * hw), (x + d * 7, ay - 0.82 * hw)], ramp[1])
    return mk(f"toque_{col}_{size}", "toque", a, ax, ay, hw, col, size, ["chef", "cook", "tall", "male"])


def cook_cap(hw: int, col: str, size: str) -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 0.46 * hw + 6, 4, 12, hw + 151)
    m = a.mask().ellipse(ax, ay - 0.16 * hw, r + 9, 0.3 * hw).clip_rows(0, ay - 2)
    m.rect(ax - r - 1, ay - 8, ax + r + 1, ay)
    a.fill(m, ramp, tex="linen", radius=4.5, base=0.62)
    band = a.mask().rect(ax - r - 1, ay - 7, ax + r + 1, ay)
    a.recolor_mask(band, ramp, [ramp[0], ramp[2], ramp[3], ramp[3], ramp[4]])
    a.line([(ax - r - 1, ay - 8), (ax + r + 1, ay - 8)], ramp[1])
    for d in (-0.6, -0.2, 0.25, 0.6):
        a.line([(ax + d * r, ay - 9), (ax + d * r * 1.4, ay - 0.3 * hw)], ramp[1])
    return mk(f"cookcap_{col}_{size}", "cook_cap", a, ax, ay, hw, col, size, ["chef", "cook", "male", "female"])


def circlet(hw: int, col: str, size: str, gem: str = "red") -> Part:
    ramp = RAMPS[col]
    r = hw / 2
    a, ax, ay = _canvas(hw, 12, 8, 6, hw + 161)
    outer = a.mask().ellipse(ax, ay - 3, r + 2, 8).clip_rows(0, ay + 5)
    inner = a.mask().ellipse(ax, ay - 6, r - 1, 7)
    outer.sub(inner)
    a.fill(outer, ramp, radius=1.6, base=0.6, strength=1.1)
    g = RAMPS[gem]
    gx, gy = ax, ay + 1
    a.px(gx, gy - 1, g[3]), a.px(gx - 1, gy, g[2]), a.px(gx, gy, g[4]), a.px(gx + 1, gy, g[1]), a.px(gx, gy + 1, g[1])
    for dx in (-1, 1):
        a.px(gx + dx * 3, gy, ramp[0])
    return mk(f"circlet_{col}_{gem}_{size}", "circlet", a, ax, ay, hw, col, size, ["circlet", "gentry", "female", "male"], erase="")


# --------------------------------------------------------------------------------------------- catalogue


def build() -> list[Part]:
    out: list[Part] = []
    for sz, hw in SIZES.items():
        for c in ("linen", "cream", "sand"):
            out.append(coif(hw, c, sz))
        for c in ("brown", "grey", "wine", "indigo"):
            out.append(skullcap(hw, c, sz))
        for c in ("leather", "brown"):
            out.append(leather_cap(hw, c, sz))
        for c in ("charcoal", "brown", "wine"):
            out.append(hood_back(hw, c, sz, peak=(c == "charcoal"))), out.append(hood_front(hw, c, sz))
        for c in ("grey", "moss"):
            out.append(hood_back(hw, c, sz)), out.append(hood_front(hw, c, sz))
        for c in ("linen", "cream"):
            out.append(wimple(hw, c, sz))
        for c in ("linen", "cream", "grey"):
            out.append(veil_back(hw, c, sz))
        for c, pt in (("wine", "plain"), ("ochre", "dots"), ("moss", "stripe"), ("indigo", "dots"), ("linen", "plain")):
            out.append(kerchief(hw, c, sz, pt))
        for c, b in (("brown", "leather"), ("charcoal", "brass"), ("moss", "leather"), ("grey", "red"), ("wine", "leather")):
            out.append(felt_hat(hw, c, sz, "brass" if b == "brass" else b))
        for c, b, s in (("straw", "wine", True), ("sand", "leather", True), ("charcoal", "red", False), ("brown", "ochre", False)):
            out.append(wide_brim(hw, c, sz, b, s))
        for c, f in (("wine", "cream"), ("indigo", "cream"), ("moss", "red"), ("charcoal", "red")):
            out.append(feathered(hw, c, sz, f))
        for c in ("wine", "indigo", "moss", "charcoal", "plum"):
            out.append(guild_cap(hw, c, sz))
        for c in ("iron", "steel"):
            out.append(kettle(hw, c, sz))
            out.append(sallet(hw, c, sz)), out.append(sallet_tail(hw, c, sz))
            out.append(chain_coif(hw, c, sz))
        for c in ("linen", "cream"):
            out.append(toque(hw, c, sz)), out.append(cook_cap(hw, c, sz))
        for c, g in (("brass", "red"), ("brass", "blue"), ("steel", "green")):
            out.append(circlet(hw, c, sz, g))
    return out
