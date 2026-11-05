"""Luminance-preserving recolour of a bust's garments into the tavern's wool, linen and leather ramps.

The garment pixels (below the chin line, not skin, not hair) are grouped into one to three cloth families by
their colour; each family's pixels are ranked by brightness and mapped onto the five tones of a ramp, so folds,
shadows, seams and highlights of the source survive while the colour becomes dyed wool or leather.
"""

from __future__ import annotations

import colorsys
import random

from PIL import Image

from kit import RAMPS
from landmarks import FH, FW, Landmarks, is_skin

CUTS = (0.10, 0.34, 0.70, 0.93)   # shares of a family's pixels that fall on tones 0..4


def luma(c: tuple[int, int, int]) -> float:
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _feat(c: tuple[int, int, int]) -> tuple[float, float, float]:
    L = luma(c)
    k = 100 / (L + 30)
    return ((c[0] - c[1]) * k, (c[2] - (c[0] + c[1]) / 2) * k, L * 0.2)


def _kmeans(pts: list[tuple[float, float, float]], k: int) -> tuple[list[int], list[tuple[float, float, float]]]:
    order = sorted(range(len(pts)), key=lambda i: pts[i][0])
    cent = [pts[order[int((j + 0.5) * len(pts) / k)]] for j in range(k)]
    lab = [0] * len(pts)
    for _ in range(8):
        for i, p in enumerate(pts):
            lab[i] = min(range(k), key=lambda j: sum((p[t] - cent[j][t]) ** 2 for t in range(3)))
        for j in range(k):
            mem = [pts[i] for i in range(len(pts)) if lab[i] == j]
            if mem:
                cent[j] = tuple(sum(m[t] for m in mem) / len(mem) for t in range(3))  # type: ignore[assignment]
    return lab, cent


def hair_colour(img: Image.Image, lm: Landmarks) -> tuple[int, int, int] | None:
    """The hair colour: median of non-skin pixels in the top rows of the head (None when the head top is a hat)."""
    px = img.load()
    pts = []
    for y in range(lm.top + 3, lm.top + 10):
        for x in range(int(lm.cx) - 14, int(lm.cx) + 15):
            if 0 <= x < FW and px[x, y][3] >= 128:
                pts.append(px[x, y][:3])
    if len(pts) < 8:
        return None
    return tuple(sorted(c[i] for c in pts)[len(pts) // 2] for i in range(3))  # type: ignore[return-value]


def _hairlike(c: tuple[int, int, int], hair: tuple[int, int, int] | None) -> bool:
    if hair is None:
        return False
    h1, s1, v1 = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    h2, s2, v2 = colorsys.rgb_to_hsv(*(x / 255 for x in hair))
    dh = min(abs(h1 - h2), 1 - abs(h1 - h2))
    return (dh < 0.05 or s2 < 0.15) and abs(s1 - s2) < 0.22 and abs(v1 - v2) < 0.2


PALE = ("linen", "cream", "grey", "sand", "bone")
CUTS_PALE = (0.10, 0.34, 0.62, 0.86)


def _hsv(c: tuple[int, int, int]) -> tuple[float, float, float]:
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)


def _map(out_px, src, coords: list[tuple[int, int]], ramp, cuts, rank_weight: float, lo: float = 25, span: float = 200) -> None:
    """Writes ramp tones for the pixels: brightness decides the tone (ties stay ties), rank adds fold contrast."""
    n = len(coords)
    lumas = sorted(luma(src[p][:3]) for p in coords)
    first: dict[float, int] = {}
    count: dict[float, int] = {}
    for pos, L in enumerate(lumas):
        first.setdefault(L, pos)
        count[L] = count.get(L, 0) + 1
    for p in coords:
        L = luma(src[p][:3])
        t = rank_weight * (first[L] + count[L] / 2) / n + (1 - rank_weight) * max(0.0, min(1.0, (L - lo) / span))
        out_px[p] = (*ramp[sum(1 for cut in cuts if t >= cut)], src[p][3])


def recolor(img: Image.Image, lm: Landmarks, ramp_names: list[str], start_row: int | None = None, whole: bool = False,
            seed: int = 0) -> Image.Image:
    """Returns a recoloured copy. `whole` also recolours head cloth (hooded figures): skin, outline and eyes are kept."""
    out = img.copy()
    px = out.load()
    src = img.load()
    rng = random.Random(seed)
    hair = None if whole else hair_colour(img, lm)
    if hair is not None:
        _, hs_, hv_ = _hsv(hair)
        if hs_ < 0.1 and hv_ > 0.55:
            hair = None        # a pale, neutral "hair" is an original hat or a bald head: nothing to protect
    y0 = start_row if start_row is not None else (lm.top if whole else lm.chin_y - 1)
    fcy, frx, fry = (lm.eyes_y + lm.chin_y) / 2, lm.hw * 0.42, (lm.chin_y - lm.eyes_y) / 2 + 12
    coords: list[tuple[int, int]] = []
    for y in range(max(0, y0), FH):
        for x in range(FW):
            r, g, b, a = src[x, y]
            if a < 128:
                continue
            c = (r, g, b)
            if is_skin(c, lm):
                continue
            if whole:
                # inside the face oval only skin, dark outline and eye pixels are kept; hood cloth there is recoloured
                if ((x - lm.cx) / frx) ** 2 + ((y - fcy) / fry) ** 2 < 1 and luma(c) < 60:
                    continue
            else:
                near_head = abs(x - lm.cx) < lm.hw / 2 + 12 and y < lm.chin_y + 16
                if near_head and _hairlike(c, hair):
                    continue
            coords.append((x, y))
    if len(coords) < 30:
        return out
    cset = set(coords)

    # 1. glowing trim (orange or green circuit lines, neon piping): small, bright, strongly coloured pixels whose hue is not
    #    the garment's own become gold braid
    hsv = {p: _hsv(src[p][:3]) for p in coords}
    colourful = [p for p in coords if hsv[p][1] > 0.3 and hsv[p][2] > 0.3]
    dom_h = None
    neutral = sum(1 for p in coords if hsv[p][1] < 0.25)
    if len(colourful) > 0.25 * len(coords) and neutral < 0.4 * len(coords):
        hs = sorted(hsv[p][0] for p in colourful)
        dom_h = hs[len(hs) // 2]
    accent = []
    for p in coords:
        h, sat, v = hsv[p]
        if sat > 0.5 and v > 0.5:
            if dom_h is None or min(abs(h - dom_h), 1 - abs(h - dom_h)) > 0.09:
                accent.append(p)
    # thin lines of the odd colour are trim; a big patch of it is the garment itself and is left to the cloth families
    aset = set(accent)
    accent = [p for p in accent if sum((p[0] + dx, p[1] + dy) in aset for dx in range(-2, 3) for dy in range(-2, 3)) <= 11]
    if len(accent) > 0.3 * len(coords):
        accent = []
    acc = set(accent)

    # 2. pale or grey cloth (shirts, lab coats): ONE family mapped by brightness only, so folds stay smooth
    pale = [p for p in coords if p not in acc and hsv[p][1] < 0.16 and luma(src[p][:3]) >= 95]
    if len(pale) < 0.08 * len(coords):
        pale = []
    pset = set(pale)
    if pale:
        # shadow tones of the same pale cloth (neutral, a little darker) join it when they touch it
        for _ in range(4):
            add = []
            for (x, y) in coords:
                p = (x, y)
                if p in pset or p in acc or hsv[p][1] >= 0.16 or luma(src[p][:3]) < 55:
                    continue
                if any((x + dx, y + dy) in pset for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    add.append(p)
            if not add:
                break
            pset.update(add)
            pale.extend(add)
    if pale:
        pname = ramp_names[1] if len(ramp_names) > 1 and ramp_names[1] in PALE else rng.choice(("linen", "cream", "grey"))
        mean_l = sum(luma(src[p][:3]) for p in pale) / len(pale)
        if mean_l < 135 and pname in ("linen", "cream"):
            pname = "grey"
        _map(px, src, pale, RAMPS[pname], CUTS_PALE, 0.0, lo=70, span=170)
    if accent:
        _map(px, src, accent, RAMPS["brass"], CUTS_PALE, 0.0, lo=60, span=190)

    rest = [p for p in coords if p not in acc and p not in pset]
    if len(rest) < 20:
        return out
    # 3. the remaining cloth: families come from the bright pixels only (shadow tones have unstable hue and would split a
    #    cloth into patches); dark pixels join the family of their neighbours by region growing
    sure = [p for p in rest if luma(src[p][:3]) >= 70]
    pts = [_feat(src[p][:3]) for p in sure]
    k = 1
    flab = [0] * len(pts)
    if len(pts) >= 30:
        for kk in (3, 2):
            lab_k, cent_k = _kmeans(pts, kk)
            sizes = [lab_k.count(j) for j in range(kk)]
            sep = min(sum((cent_k[i][t] - cent_k[j][t]) ** 2 for t in range(3)) ** 0.5 for i in range(kk) for j in range(i + 1, kk))
            if min(sizes) >= 0.12 * len(pts) and sep > 18:
                k, flab = kk, lab_k
                break
    label: dict[tuple[int, int], int] = {p: flab[n] for n, p in enumerate(sure)}
    rset = set(rest)
    frontier = list(label)
    while frontier:
        nxt = []
        for (x, y) in frontier:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q not in label and q in rset:
                        label[q] = label[(x, y)]
                        nxt.append(q)
        frontier = nxt
    fam: dict[int, list[tuple[int, int]]] = {}
    for p in rest:
        fam.setdefault(label.get(p, 0), []).append(p)
    for rank, j in enumerate(sorted(fam, key=lambda j: -len(fam[j]))):
        name = ramp_names[min(rank, len(ramp_names) - 1)]
        _map(px, src, fam[j], RAMPS[name], CUTS, 0.35)
    return out


def convert_face_gear(out: Image.Image, src_img: Image.Image, lm: Landmarks, mask_ramp: str, seed: int = 0) -> dict[str, bool]:
    """Turns modern face gear into period cloth and leather; returns what it found.

    - a mask over the mouth (surgical, gas, filter) becomes a cloth muffler (ramp `mask_ramp`, brightness kept)
    - goggles (big non-skin blobs around the eyes) become a leather eye-band
    Detection needs a large area, so eyes and thin spectacle frames are never touched.
    """
    px, src = out.load(), src_img.load()
    hair = hair_colour(src_img, lm)
    flags = {"mask": False, "goggles": False}

    def odd(p: tuple[int, int]) -> bool:
        r, g, b, a = src[p]
        if a < 128:
            return False
        c = (r, g, b)
        h, s, v = _hsv(c)
        sh, ss, sv = lm.skin_hsv
        dh = min(abs(h - sh), 1 - abs(h - sh))
        if v < 0.2 or _hairlike(c, hair):
            return False
        return dh > 0.06 or s > 1.5 * ss + 0.1 or s < 0.4 * ss

    cx = int(lm.cx)
    box = [(x, y) for y in range(lm.nose_y - 1, lm.chin_y - 2) for x in range(cx - int(lm.hw * 0.38), cx + int(lm.hw * 0.38) + 1)]
    def maskish(p: tuple[int, int]) -> bool:
        # surgical masks are pale or teal, gas masks green or blue-grey; beards are brown, black or grey, so they never match
        h, s, v = _hsv(src[p][:3])
        return odd(p) and ((0.28 < h < 0.75 and s > 0.12) or (v > 0.8 and s < 0.2))

    mask = [p for p in box if maskish(p)]
    if len(mask) >= 85:
        flags["mask"] = True
        _map(px, src, mask, RAMPS[mask_ramp], CUTS, 0.3)
    gear = [(x, y) for y in range(lm.eyes_y - 24, lm.eyes_y + 5) for x in range(cx - lm.hw // 2 - 6, cx + lm.hw // 2 + 7)
            if odd((x, y)) and luma(src[(x, y)][:3]) >= 45]
    if len(gear) >= 60:
        flags["goggles"] = True
        _map(px, src, gear, RAMPS["leather"], CUTS, 0.4)
    return flags
