"""Drawing kit for the parts library: masks, light-aware shading, textures. All art is generated from code.

A *mask* is an 'L' image (255 inside). `Art.fill(mask, ramp)` shades the mask like the game's busts: a dark rim,
3-5 tones, light from the upper left, ordered dither only on the seams between two tones. No source pixels of the game
are read anywhere in this package's parts code.
"""

from __future__ import annotations

import random
import sys
from collections.abc import Sequence
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tavern"))
from palette import BRASS, IRON, LEATHER, LINEN, MOSS, NAVY, WINE  # noqa: E402
from pix import BAYER, mix  # noqa: E402

Color = tuple[int, int, int]
Ramp = list[Color]


def hexc(h: str) -> Color:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def make_ramp(mid: Color, n: int = 5) -> Ramp:
    """Five tones from a middle colour: shadows slide toward violet-brown, lights toward warm cream."""
    dark, shade_ = (28, 16, 26), (46, 28, 40)
    cream = (255, 230, 176)
    tones = [mix(mid, dark, 0.66), mix(mid, shade_, 0.34), mid, mix(mid, cream, 0.22), mix(mid, cream, 0.46)]
    return tones if n == 5 else [tones[0], tones[1], tones[2], tones[3]]


# Wool, linen and leather ramps. Palette ramps seed the common ones; the rest are mid-tones of the same family.
RAMPS: dict[str, Ramp] = {
    "wine": make_ramp(WINE[2]), "moss": make_ramp(MOSS[2]), "indigo": make_ramp(NAVY[2]), "ochre": make_ramp(hexc("#a8782c")),
    "linen": make_ramp(LINEN[2]), "leather": make_ramp(LEATHER[3]), "brown": make_ramp(hexc("#6a4a32")),
    "grey": make_ramp(hexc("#6a6870")), "charcoal": make_ramp(hexc("#3c3840")), "straw": make_ramp(hexc("#c4a45a")),
    "plum": make_ramp(hexc("#6a3a56")), "rust": make_ramp(hexc("#a4502c")), "sand": make_ramp(hexc("#b09a72")),
    "teal": make_ramp(hexc("#356a66")), "cream": make_ramp(hexc("#d8ccb0")), "black": make_ramp(hexc("#2e2a32")),
    "iron": list(IRON), "steel": [IRON[1], IRON[2], IRON[3], IRON[4], hexc("#a3a6ae")], "brass": list(BRASS),
    "bone": make_ramp(hexc("#cdbf9c")), "red": make_ramp(hexc("#a8352f")), "blue": make_ramp(hexc("#3b5f94")),
    "green": make_ramp(hexc("#4d7a3e")),
}


def tone_index(ramp: Ramp, c: Sequence[int]) -> int:
    return min(range(len(ramp)), key=lambda i: sum((ramp[i][k] - c[k]) ** 2 for k in range(3)))


class Mask:
    """A hard-edged 'L' shape canvas."""

    def __init__(self, w: int, h: int) -> None:
        self.w, self.h = w, h
        self.im = Image.new("L", (w, h), 0)
        self.d = ImageDraw.Draw(self.im)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, v: int = 255) -> Mask:
        self.d.ellipse((cx - rx, cy - ry, cx + rx - 0.01, cy + ry - 0.01), fill=v)
        return self

    def poly(self, pts: Sequence[tuple[float, float]], v: int = 255) -> Mask:
        self.d.polygon([(round(x), round(y)) for x, y in pts], fill=v)
        return self

    def rect(self, x0: float, y0: float, x1: float, y1: float, v: int = 255) -> Mask:
        self.d.rectangle((round(x0), round(y0), round(x1), round(y1)), fill=v)
        return self

    def line(self, pts: Sequence[tuple[float, float]], width: int = 1, v: int = 255) -> Mask:
        self.d.line([(round(x), round(y)) for x, y in pts], fill=v, width=width, joint="curve")
        return self

    def sub(self, other: Mask) -> Mask:
        self.im = Image.composite(Image.new("L", self.im.size, 0), self.im, other.im.point(lambda p: 255 if p > 127 else 0))
        self.d = ImageDraw.Draw(self.im)
        return self

    def add(self, other: Mask) -> Mask:
        self.im = Image.composite(Image.new("L", self.im.size, 255), self.im, other.im.point(lambda p: 255 if p > 127 else 0))
        self.d = ImageDraw.Draw(self.im)
        return self

    def mul(self, other: Mask) -> Mask:
        self.im = Image.composite(self.im, Image.new("L", self.im.size, 0), other.im.point(lambda p: 255 if p > 127 else 0))
        self.d = ImageDraw.Draw(self.im)
        return self

    def copy(self) -> Mask:
        m = Mask(self.w, self.h)
        m.im = self.im.copy()
        m.d = ImageDraw.Draw(m.im)
        return m

    def clip_rows(self, y0: float, y1: float) -> Mask:
        """Keeps rows y0..y1-1 only."""
        y0, y1 = round(y0), round(y1)
        if y0 > 0:
            self.d.rectangle((0, 0, self.w, y0 - 1), fill=0)
        if y1 < self.h:
            self.d.rectangle((0, y1, self.w, self.h), fill=0)
        return self


def shade(mask: Mask, ramp: Ramp, radius: float = 3.0, strength: float = 1.0, base: float = 0.58,
          vbias: float = 0.0, rim: bool = True, soft: float = 0.5, light: tuple[float, float] = (-0.62, -0.78)) -> Image.Image:
    """Colours a mask with a ramp: surface normal from a blurred height field, lit from the upper left.

    Tone 0 of the ramp is only used for the rim, so a shape has rim + (n-1) body tones.
    """
    w, h = mask.w, mask.h
    pad = int(radius * 2.5) + 3
    big = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    big.paste(mask.im, (pad, pad))
    hp = big.filter(ImageFilter.GaussianBlur(radius)).load()
    mp = big.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    n = len(ramp)
    lx, ly = light
    for y in range(h):
        for x in range(w):
            X, Y = x + pad, y + pad
            if mp[X, Y] < 128:
                continue
            if rim and (mp[X - 1, Y] < 128 or mp[X + 1, Y] < 128 or mp[X, Y - 1] < 128 or mp[X, Y + 1] < 128):
                op[x, y] = (*ramp[0], 255)
                continue
            gx = (hp[X + 1, Y] - hp[X - 1, Y]) / 510
            gy = (hp[X, Y + 1] - hp[X, Y - 1]) / 510
            lit = -(gx * lx + gy * ly)
            v = base + strength * lit * radius * 1.7 - vbias * (y / max(1, h) - 0.5)
            v = max(0.0, min(0.999, v))
            t = v * (n - 2)
            lo = int(t)
            frac = t - lo
            f = max(0.0, min(1.0, (frac - 0.5) / soft + 0.5))
            idx = 1 + lo + (1 if f > (BAYER[y % 4][x % 4] + 0.5) / 16 else 0)
            op[x, y] = (*ramp[min(n - 1, idx)], 255)
    return out


def shift_tone(ramp: Ramp, c: Sequence[int], d: int) -> Color:
    i = tone_index(ramp, c)
    return ramp[max(1, min(len(ramp) - 1, i + d))] if i > 0 else ramp[0]


def texture(im: Image.Image, ramp: Ramp, kind: str, seed: int = 0, strength: float = 1.0) -> None:
    """Adds a surface pattern by moving some interior pixels one tone up or down (rim pixels are left alone)."""
    rng = random.Random(seed)
    px = im.load()
    w, h = im.size
    base_rim = ramp[0]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128 or (r, g, b) == base_rim:
                continue
            d = 0
            if kind == "felt":
                d = rng.choice((-1, 1)) if rng.random() < 0.07 * strength else 0
            elif kind == "wool":
                d = -1 if (x * 7 + y * 13) % 11 == 0 else (1 if (x * 5 + y * 3) % 17 == 0 else 0)
            elif kind == "weave":  # straw: short horizontal strokes in bricks
                row = y // 2
                d = -1 if y % 2 == 0 and (x + row * 3) % 5 in (0, 1) else (1 if y % 2 == 1 and (x + row * 3) % 7 == 2 else 0)
            elif kind == "mail":
                d = 1 if (x + 2 * (y % 2)) % 4 == 0 and y % 2 == 0 else (-1 if (x + 2 * (y % 2)) % 4 == 2 and y % 2 == 1 else 0)
            elif kind == "knit":
                d = -1 if (x + y) % 4 == 0 else (1 if (x + y) % 4 == 2 and y % 2 == 0 else 0)
            elif kind == "linen":
                d = -1 if (y % 3 == 0 and (x * 5 + y) % 9 == 0) else (1 if (x % 4 == 1 and y % 5 == 2) else 0)
            elif kind == "leather":
                d = rng.choice((-1, 1)) if rng.random() < 0.04 else 0
            elif kind == "quilt":
                d = -1 if x % 7 == 3 or (y % 9 == 4 and x % 7 not in (3,)) else 0
            elif kind == "plate":
                d = 1 if (x + y) % 9 == 0 else 0
            if d:
                nr, ng, nb = shift_tone(ramp, (r, g, b), d)
                px[x, y] = (nr, ng, nb, a)


class Art:
    """A part canvas with an anchor point; shapes are filled with `fill`, details are drawn straight onto `im`."""

    def __init__(self, w: int, h: int, seed: int = 0) -> None:
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.rng = random.Random(seed)
        self.seed = seed
        self.inside = True      # lines drawn with line() only land on pixels that are already opaque

    def mask(self) -> Mask:
        return Mask(self.w, self.h)

    def fill(self, m: Mask, ramp: Ramp, tex: str | None = None, **kw: float) -> Image.Image:
        img = shade(m, ramp, **kw)
        if tex:
            texture(img, ramp, tex, self.seed + self.w)
        self.im.alpha_composite(img)
        return img

    def px(self, x: float, y: float, c: Sequence[int], a: int = 255) -> None:
        x, y = round(x), round(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), (c[0], c[1], c[2], a))

    def line(self, pts: Sequence[tuple[float, float]], c: Sequence[int], width: int = 1) -> None:
        if not self.inside:
            ImageDraw.Draw(self.im).line([(round(x), round(y)) for x, y in pts], fill=(c[0], c[1], c[2], 255), width=width)
            return
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).line([(round(x), round(y)) for x, y in pts], fill=(c[0], c[1], c[2], 255), width=width)
        keep = self.im.getchannel("A").point(lambda p: 255 if p > 0 else 0)
        layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", self.im.size, 0), keep))
        self.im.alpha_composite(layer)

    def dots(self, pts: Sequence[tuple[int, int]], c: Sequence[int]) -> None:
        for x, y in pts:
            self.px(x, y, c)

    def over_mask(self, m: Mask, c: Sequence[int]) -> None:
        """Paints colour c onto the pixels of the mask that are already opaque (stripes, trims, patterns)."""
        mp, ip = m.im.load(), self.im.load()
        for y in range(self.h):
            for x in range(self.w):
                if mp[x, y] > 127 and ip[x, y][3] > 0:
                    ip[x, y] = (c[0], c[1], c[2], 255)

    def recolor_mask(self, m: Mask, ramp_from: Ramp, ramp_to: Ramp) -> None:
        """Swaps tones of a ramp for those of another inside a mask (trims painted with the same shading)."""
        mp, ip = m.im.load(), self.im.load()
        for y in range(self.h):
            for x in range(self.w):
                r, g, b, a = ip[x, y]
                if mp[x, y] > 127 and a > 0:
                    i = tone_index(ramp_from, (r, g, b))
                    ip[x, y] = (*ramp_to[min(i, len(ramp_to) - 1)], 255)

    def rim_outside(self, ramp: Ramp) -> None:
        """Rebuilds a one-pixel dark rim around the union of everything drawn (used after details poke out)."""
        src = self.im.load()
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src[nx, ny][3] > 0:
                            add.append((x, y))
                            break
        for x, y in add:
            src[x, y] = (*ramp[0], 255)
