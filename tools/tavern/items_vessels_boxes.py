"""The tavern's crates, chests and sacks: the ale crate in its bottle counts (`items~beer_case@...`) and the painted,
iron-banded chests, the linen sack and the leather pouch (`items~items_container@...`)."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

import font
import itemkit_vessels as kit
from itemkit_vessels import blob, rows_from, tones
from palette import BRASS, IRON, LEATHER, LINEN, OAK, PALE_WOOD, SHADOW, SOOT, WINE, WOOD
from pix import CLEAR, Color, Pix, Ramp, mix, rgb


# ---------------------------------------------------------------------------------------------- the ale crate

CRATE = (7, 13, 73, 64)                                  # x0, y0, x1, y1 of the empty crate
SLOTS = (19, 33, 47, 61)                                 # centres of the four bottles of a row
GLASS_ALE: Ramp = (rgb("#2c1509"), rgb("#55290f"), rgb("#8a4a14"), rgb("#c47d22"), rgb("#f1d28a"))


def _bottle(p: Pix, cx: int, top: int, seal: Ramp = WINE) -> None:
    """An amber ale bottle: a wax-sealed cork, a neck, round shoulders and a lit side."""
    prof = [(0, 3), (1, 3), (2, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 3), (10, 4), (11, 5)] + [(y, 5) for y in range(12, 24)]
    for dy, half in prof:
        y = top + dy
        for x in range(cx - half, cx + half + 1):
            edge = x in (cx - half, cx + half)
            if edge:
                c = SHADOW
            elif dy < 3:
                c = seal[3] if x < cx else seal[1]
                if dy == 1 and x == cx - half + 1:
                    c = seal[4]
            else:
                c = GLASS_ALE[2]
                if x == cx - half + 1:
                    c = GLASS_ALE[4] if dy >= 10 and dy % 5 != 3 else GLASS_ALE[3]
                elif x >= cx + half - 1:
                    c = GLASS_ALE[0]
                elif dy >= 12 and x >= cx + 1:
                    c = GLASS_ALE[1]
                if dy == 11:
                    c = GLASS_ALE[3]
            p.px(x, y, c)
    for x in range(cx - 3, cx + 4):                        # the cap's rim
        p.px(x, top + 3, seal[1] if x > cx else seal[2])
    p.px(cx + 3, top + 3, SHADOW)
    p.px(cx - 3, top + 3, SHADOW)


def _plank_row(p: Pix, x: int, y: int, w: int, h: int, ramp: Ramp, seed: int) -> None:
    """One board with a lit top edge, a dark joint under it and a little grain."""
    p.rect(x, y, w, h, ramp[2])
    p.hline(x, y, w, ramp[3])
    p.hline(x, y + h - 1, w, ramp[0])
    p.hline(x, y + h - 2, w, ramp[1])
    for i in range(w // 9):
        gx = x + (i * 13 + seed * 7) % max(1, w - 6)
        gy = y + 2 + (i * 5 + seed) % max(1, h - 5)
        p.hline(gx, gy, 5, ramp[1] if i % 2 else ramp[3])


def _mug(p: Pix, x: int, y: int) -> None:
    """A foaming tankard, the crate's mark (9x10)."""
    cream, foam = rgb("#e4cf9a"), rgb("#f5ecc8")
    p.rect(x + 1, y + 2, 6, 8, rgb("#c47d22"))
    p.vline(x + 1, y + 2, 8, rgb("#f1d28a"))
    p.vline(x + 6, y + 2, 8, rgb("#8a4a14"))
    p.frame(x, y + 1, 8, 9, SHADOW)
    p.hline(x, y + 1, 8, SHADOW)
    for dx, dy in ((1, 0), (2, 0), (3, 0), (4, 1), (5, 0), (6, 0)):
        p.px(x + dx, y + dy, foam)
    p.rect(x + 1, y + 1, 6, 1, foam)
    p.px(x + 2, y + 1, cream)
    p.px(x + 8, y + 3, SHADOW)
    for dy in (3, 4, 5, 6):
        p.px(x + 8 + (1 if dy in (4, 5) else 0), y + dy, SHADOW if dy not in (4, 5) else LEATHER[3])
    p.px(x + 9, y + 4, SHADOW)
    p.px(x + 9, y + 5, SHADOW)
    p.px(x + 8, y + 7, SHADOW)


def _crate_front(p: Pix) -> None:
    """The front of the crate: a top rail, two boards, iron corner brackets, a hand slot and a painted mark."""
    x0, y0, x1, y1 = CRATE
    w = x1 - x0
    _plank_row(p, x0, y0 + 6, w, 5, PALE_WOOD_RAMP, 1)           # the rail the bottles lean on
    _plank_row(p, x0, y0 + 11, w, 18, WOOD, 2)
    _plank_row(p, x0, y0 + 29, w, y1 - y0 - 29, WOOD, 3)
    p.hline(x0, y0 + 11, w, SHADOW)
    p.hline(x0, y0 + 29, w, SHADOW)
    # the hand slot, a dark cut with a lit lower lip
    p.rect(x0 + 12, y0 + 15, w - 24, 5, SOOT[0])
    p.hline(x0 + 12, y0 + 14, w - 24, SHADOW)
    p.hline(x0 + 12, y0 + 20, w - 24, WOOD[4])
    p.hline(x0 + 13, y0 + 16, w - 26, SOOT[2])
    # the plaque: wine-red paint, a brass rule, a tankard and burnt-in letters
    px, py, pw, ph = x0 + 27, y0 + 24, w - 54, 22
    p.rect(px, py, pw, ph, WINE[1])
    p.frame(px, py, pw, ph, BRASS[2])
    p.hline(px + 1, py + 1, pw - 2, BRASS[4])
    p.vline(px + 1, py + 1, ph - 2, WINE[3])
    p.frame(px - 1, py - 1, pw + 2, ph + 2, SHADOW)
    _mug(p, px + (pw - 10) // 2, py + 6)
    font.write(p, px - 3 - font.width("OLD"), py + 8, "OLD", WOOD[0])
    font.write(p, px + pw + 2, py + 8, "ALE", WOOD[0])
    # iron corner brackets with brass rivets
    for bx, flip in ((x0, 1), (x1 - 7, -1)):
        p.rect(bx, y0 + 6, 7, 5, IRON[2])
        p.hline(bx, y0 + 6, 7, IRON[4])
        p.rect(bx + (0 if flip == 1 else 3), y0 + 6, 4, y1 - y0 - 6, IRON[2])
        p.vline(bx + (0 if flip == 1 else 6), y0 + 6, y1 - y0 - 6, IRON[1])
        p.vline(bx + (0 if flip == 1 else 3), y0 + 6, y1 - y0 - 6, IRON[4])
        for yy in (y0 + 8, y0 + 22, y0 + 38, y1 - 4):
            p.px(bx + (1 if flip == 1 else 4), yy, BRASS[4])
            p.px(bx + (2 if flip == 1 else 5), yy, BRASS[1])
    for x, y in ((x0, y0 + 6), (x1 - 1, y0 + 6)):
        p.px(x, y, CLEAR)
    p.frame(x0, y0 + 6, w, y1 - y0 - 6, SHADOW)
    p.px(x0, y0 + 6, CLEAR)
    p.px(x1 - 1, y0 + 6, CLEAR)
    p.hline(x0, y1 - 1, w, SHADOW)


PALE_WOOD_RAMP: Ramp = PALE_WOOD


def _crate_back(p: Pix, dark: bool = False) -> None:
    """The open top seen from above and the back board: a lit rim and a dark inside."""
    x0, y0, x1, y1 = CRATE
    w = x1 - x0
    p.rect(x0, y0, w, y1 - y0, WOOD[1])
    p.frame(x0, y0, w, y1 - y0, SHADOW)
    p.hline(x0 + 1, y0 + 1, w - 2, PALE_WOOD[3])             # the back rim, lit
    p.hline(x0 + 1, y0 + 2, w - 2, PALE_WOOD[1])
    inner = SOOT[1] if not dark else SOOT[0]
    p.rect(x0 + 3, y0 + 3, w - 6, y1 - y0 - 6 if dark else 4, inner)
    p.rect(x0 + 3, y0 + 3, 1, y1 - y0 - 6 if dark else 4, SOOT[3])
    for x in range(x0 + 6, x1 - 6, 7):                       # the gaps between the back boards
        p.vline(x, y0 + 3, y1 - y0 - 6 if dark else 4, SOOT[2] if dark else SOOT[0])
    p.px(x0, y0, CLEAR)
    p.px(x1 - 1, y0, CLEAR)


def crate(bottles: int, corners: bool = False, back_only: bool = False) -> Image.Image:
    p = Pix(80, 64, seed=40 + bottles)
    _crate_back(p, dark=back_only)
    if back_only:
        return p.im
    for i in range(max(0, bottles - 4)):
        _bottle(p, SLOTS[i], 0)
    for i in range(min(4, bottles)):
        _bottle(p, SLOTS[i], 5)
    if corners:                                              # the corner posts stand proud of the rim
        for x in (CRATE[0], CRATE[2] - 4):
            p.rect(x, 7, 4, 8, WOOD[2])
            p.vline(x, 7, 8, PALE_WOOD[3])
            p.hline(x, 7, 4, PALE_WOOD[4])
            p.vline(x + 3, 7, 8, WOOD[1])
            p.frame(x, 6, 4, 9, SHADOW)
    _crate_front(p)
    return p.im


# ---------------------------------------------------------------------------------------------- chests

CHEST_PAINT: dict[str, Color] = {
    "eng": rgb("#b8662e"), "evidence": rgb("#463a4c"), "expedition": rgb("#7e6a88"),
    "med": rgb("#2f8a80"), "sec": rgb("#a63a3a"), "service": rgb("#4e6c36"),
}


def _hline(p: Pix, x: int, y: int, w: int, c: Color) -> None:
    p.hline(x, y, w, c)


def chest(size: tuple[int, int], box: tuple[int, int, int, int], ramp: Ramp, mode: str, strap: Ramp = IRON,
          seed: int = 0) -> Image.Image:
    """A painted chest: a vaulted lid on a panelled body, with a hasp and lock.  `mode` is `strapped` (iron bands over
    everything, hasp shut), `ajar` (no bands, the lid cracked open on a dark gap, the hasp hanging) or `coffer`
    (leather straps with brass buckles)."""
    p = Pix(*size, seed=seed)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    lid = round(h * 0.38)
    rows = rows_from([(y0, x0 + 2, x1 - 2), (y0 + 1, x0 + 1, x1 - 1), (y0 + 2, x0, x1), (y1 - 3, x0, x1), (y1 - 2, x0 + 1, x1 - 1),
                      (y1 - 1, x0 + 2, x1 - 2)])
    blob(p, rows, ramp, grain=False)
    seam = y0 + lid
    gap = 3 if mode == "ajar" else 0
    # lid: lit bevel, boards, shaded underside
    p.hline(x0 + 2, y0 + 1, w - 4, ramp[4])
    p.hline(x0 + 1, y0 + 2, w - 2, ramp[3])
    for y in range(y0 + 3, seam - 3):
        t = (y - y0 - 3) / max(1, seam - y0 - 6)
        p.hline(x0 + 1, y, w - 2, ramp[3] if t < 0.3 else ramp[2])
    p.dither(x0 + 1, y0 + 3, w - 2, 3, ramp[3], 0.4)
    mid = y0 + lid // 2 + 1
    p.hline(x0 + 1, mid, w - 2, ramp[1])
    p.hline(x0 + 1, mid + 1, w - 2, ramp[3])
    p.hline(x0 + 1, seam - 3, w - 2, ramp[1])
    p.hline(x0 + 1, seam - 2, w - 2, ramp[1])
    p.hline(x0 + 1, seam - 1, w - 2, ramp[0])
    if gap:                                                  # the cracked lid: a black slit and the lid's lit lip
        p.hline(x0 + 1, seam - 1, w - 2, ramp[3])
        p.rect(x0 + 1, seam, w - 2, gap, SOOT[0])
        p.hline(x0 + 1, seam + gap, w - 2, ramp[0])
    p.vline(x0 + 1, y0 + 3, lid - 3, ramp[4])
    # body: panels framed like a joiner's work
    top = seam + gap + 3
    pw = (w - 28) // 2
    for px in (x0 + 8, x1 - 8 - pw):
        p.rect(px, top, pw, y1 - top - 7, ramp[1])
        p.rect(px + 1, top + 1, pw - 2, y1 - top - 9, ramp[2])
        p.hline(px + 1, y1 - 8, pw - 2, ramp[3])
        p.vline(px + pw - 2, top + 1, y1 - top - 9, ramp[3])
        p.hline(px + 1, top + 1, pw - 2, ramp[0])
        p.dither(px + 2, top + 2, pw - 4, 3, ramp[1], 0.35)
    p.hline(x0 + 1, y1 - 5, w - 2, ramp[1])
    p.hline(x0 + 1, y1 - 4, w - 2, ramp[3])
    p.hline(x0 + 1, y1 - 3, w - 2, ramp[1])
    cx = x0 + w // 2
    # lock: brass escutcheon on the body, iron hasp tongue from the lid
    ly = seam + gap + 5
    p.rect(cx - 4, ly, 9, 8, BRASS[2])
    p.frame(cx - 4, ly, 9, 8, SHADOW)
    p.hline(cx - 3, ly + 1, 7, BRASS[4])
    p.vline(cx - 3, ly + 1, 6, BRASS[3])
    p.vline(cx + 3, ly + 1, 6, BRASS[1])
    p.px(cx, ly + 3, SHADOW)
    p.px(cx, ly + 4, SHADOW)
    p.px(cx, ly + 5, SHADOW)
    p.px(cx - 1, ly + 3, SHADOW)
    p.px(cx + 1, ly + 3, SHADOW)
    if mode == "ajar":
        p.rect(cx - 3, ly - 6, 7, 5, IRON[2])                   # hasp hanging open on its pin
        p.frame(cx - 3, ly - 6, 7, 5, SHADOW)
        p.hline(cx - 2, ly - 5, 5, IRON[4])
    else:
        p.rect(cx - 5, seam - 12, 11, 17, IRON[2])
        p.frame(cx - 5, seam - 12, 11, 17, SHADOW)
        p.hline(cx - 4, seam - 11, 9, IRON[4])
        p.vline(cx - 4, seam - 11, 15, IRON[3])
        p.vline(cx + 4, seam - 11, 15, IRON[1])
        p.hline(cx - 3, seam - 2, 7, IRON[0])
        p.hline(cx - 3, seam - 1, 7, IRON[1])
        p.px(cx, seam - 6, BRASS[3])
        p.px(cx, seam - 5, BRASS[1])
    # bands
    if mode in ("strapped", "coffer"):
        buckle = BRASS if mode == "coffer" else IRON
        for sx in (x0 + 5, x1 - 11):
            kit.strap(p, sx, y0 + 1, 6, h - 2, True, strap)
            p.vline(sx - 1, y0 + 2, h - 4, SHADOW)
            p.vline(sx + 6, y0 + 2, h - 4, SHADOW)
            for yy in range(y0 + 6, y1 - 4, 9):
                p.px(sx + 2, yy, BRASS[4])
                p.px(sx + 3, yy, BRASS[1])
            p.rect(sx - 2, seam - 2, 10, 6, buckle[2])         # the hinge or buckle plate at the seam
            p.frame(sx - 2, seam - 2, 10, 6, SHADOW)
            p.hline(sx - 1, seam - 1, 8, buckle[4])
            p.px(sx + 2, seam + 1, BRASS[4] if mode == "strapped" else SHADOW)
            p.px(sx + 3, seam + 1, BRASS[4] if mode == "strapped" else SHADOW)
    else:
        for bx in (x0 + 1, x1 - 6):                             # corner brackets
            for by in (y1 - 11,):
                p.rect(bx, by, 5, 9, IRON[2])
                p.hline(bx, by, 5, IRON[4])
                p.frame(bx, by, 5, 9, SHADOW)
                p.px(bx + 2, by + 3, BRASS[4])
    # the corners of the box stay rounded
    for x, y in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
        p.px(x, y, CLEAR)
    return p.im


# ---------------------------------------------------------------------------------------------- sack and pouch


def sack() -> Image.Image:
    """A linen sack tied at the neck with a cord."""
    p = Pix(48, 48, seed=70)
    rows = rows_from([(10, 14, 34), (14, 10, 38), (20, 5, 43), (34, 4, 44), (42, 6, 42), (45, 12, 36)], 0)
    for y, (a, b) in {2: (11, 17), 3: (10, 18), 4: (10, 19), 5: (11, 20), 6: (12, 21), 7: (13, 22), 8: (13, 23), 9: (14, 24)}.items():
        rows[y] = (a, b)                                         # the left ear of the gathered neck
    rows.update({y: (rows[y][0], rows[y][1]) for y in rows})
    for y, (a, b) in {2: (29, 36), 3: (28, 37), 4: (27, 38), 5: (26, 37), 6: (25, 36), 7: (24, 35), 8: (23, 34), 9: (22, 33)}.items():
        rows[y] = (min(rows[y][0], a), max(rows[y][1], b)) if y in rows else (a, b)
    for y in range(10, 14):
        rows[y] = (rows[y][0], rows[y][1])
    inner = blob(p, rows, LINEN)
    for x, y in sorted(inner):                                  # woven cloth: a fine checker on the shade side
        if y > 12 and (x * 3 + y) % 5 == 0:
            p.px(x, y, LINEN[1])
        elif y > 12 and (x + y * 3) % 7 == 0:
            p.px(x, y, LINEN[3])
    for y in range(13, 44, 6):                                  # folds
        p.hline(8 + (y % 12), y, 6, LINEN[1])
        p.hline(30 - (y % 9), y + 2, 5, LINEN[3])
    for y in (11, 12, 13):                                      # the cord and its knot
        p.hline(13 if y > 11 else 15, y, 22 if y > 11 else 18, LEATHER[2])
    p.hline(13, 13, 22, LEATHER[1])
    p.hline(14, 11, 20, LEATHER[3])
    p.rect(22, 12, 4, 5, LEATHER[2])
    p.frame(22, 12, 4, 5, SHADOW)
    p.px(23, 13, LEATHER[3])
    p.rect(12, 26, 24, 11, rgb("#8a7f68"))                        # a stitched patch
    p.frame(12, 26, 24, 11, SHADOW)
    for x in range(13, 35, 2):
        p.px(x, 27, LINEN[3])
        p.px(x, 35, LINEN[3])
    font.write(p, 15, 28, "ALE", WINE[1])
    return p.im


def pouch() -> Image.Image:
    """A leather pouch: a rounded flap with a brass stud, stitched, over a gathered purse."""
    p = Pix(48, 48, seed=71)
    rows = rows_from([(4, 11, 37), (6, 8, 40), (14, 7, 41), (30, 5, 43), (40, 6, 42), (44, 12, 36)], 0)
    inner = blob(p, rows, LEATHER)
    for x, y in sorted(inner):
        if (x * 5 + y * 3) % 11 == 0:
            p.px(x, y, LEATHER[1])
        elif (x * 3 + y * 7) % 13 == 0:
            p.px(x, y, LEATHER[3])
    flap = [(14, 8, 40), (19, 8, 40), (25, 17, 31), (28, 22, 26)]
    for y in range(13, 27):                                      # the flap's lower edge, a scalloped shadow
        t = (y - 13)
    p.hline(8, 22, 33, LEATHER[0])
    for x in range(9, 40):
        k = 22 + (3 if 16 < x < 32 else 2 if 12 < x < 36 else 1)
        for y in range(22, k):
            p.px(x, y, LEATHER[0] if y == 22 else LEATHER[2])
        p.px(x, k, SHADOW)
        p.px(x, 21, LEATHER[3])
    p.px(24, 26, SHADOW)
    for x in range(10, 39, 3):                                   # stitching along the top
        p.px(x, 8, LEATHER[3])
    for y in range(31, 41, 3):
        p.px(8, y, LEATHER[3])
        p.px(40, y, LEATHER[1])
    p.rect(22, 22, 5, 5, BRASS[2])                               # the brass stud
    p.frame(22, 22, 5, 5, SHADOW)
    p.px(23, 23, BRASS[4])
    p.px(24, 23, BRASS[3])
    p.px(25, 25, BRASS[1])
    for x, y in ((11, 4), (36, 4)):
        p.px(x, y, CLEAR)
    return p.im


# ---------------------------------------------------------------------------------------------- the series


def _chests() -> dict[str, Callable[[], Image.Image]]:
    out: dict[str, Callable[[], Image.Image]] = {}
    box = (6, 3, 90, 61)
    for i, (name, paint) in enumerate(CHEST_PAINT.items()):
        ramp = tones(paint)
        if name == "expedition":
            out["items~items_container@expedition_box.png"] = lambda r=ramp: chest((96, 64), (6, 4, 90, 61), r, "ajar", seed=3)
            continue
        out[f"items~items_container@{name}_box.png"] = lambda r=ramp, s=i: chest((96, 64), box, r, "strapped", seed=s)
        out[f"items~items_container@{name}_box_u.png"] = lambda r=ramp, s=i: chest((96, 64), (6, 4, 90, 61), r, "ajar", seed=s)
    out["items~items_container@eleanor_box.png"] = lambda: chest(
        (80, 48), (6, 2, 75, 46), tones(rgb("#7a4a86")), "coffer", tones(rgb("#b8763a")), seed=9)
    out["items~items_container@bag.png"] = sack
    out["items~items_container@pouch.png"] = pouch
    return out


def _crates() -> dict[str, Callable[[], Image.Image]]:
    out: dict[str, Callable[[], Image.Image]] = {f"items~beer_case@beer_case_{n}.png": (lambda n=n: crate(n)) for n in range(9)}
    out["items~beer_case@case.png"] = lambda: crate(0)
    out["items~beer_case@case_back.png"] = lambda: crate(0, back_only=True)
    out["items~beer_case@case_front.png"] = lambda: crate(4, corners=True)
    return out


ASSETS: Mapping[str, Callable[[], Image.Image]] = {**_chests(), **_crates()}
