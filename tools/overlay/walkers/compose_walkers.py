"""Dress the game's own passer-by silhouette sheets in medieval parts (LOCAL OUTPUT ONLY).

    python compose_walkers.py --originals <folder with the user's exported scene/animation sheets> --out <folder>

The originals are read from `--originals` and the modified sheets are written to `--out` (default: the git-ignored
`out/official_based/Textures` of the repository). The output contains the game's pixels, so it must never be committed or
shipped; this script keeps no copy of any original and writes nothing but the sheets.

Per frame the script finds the figure in the silhouette (see `Fig` and `find_figure`), then places the parts from `parts.py`
on it, so that hats, hoods and carried things follow the walker's bob and lean:

* head: the crown (topmost rows) gives the head's x and, from the top row, its y; the 8-frame sheet smooths the anchor over the
  loop, the 4-frame sheets use the raw crown because their bob is the animation;
* shoulder: a fixed fraction of the figure's height below the crown, between the clamps found from the width profile;
* hip, hem sway: the centre of the figure at hip height and how far the feet reach ahead of and behind it;
* hands: the front edge of the chest plus an arm swing that follows the stride (the silhouette does not show the hands);
* ground: the lowest row of the figure; the staff is stretched from the hand to it.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

import parts as P

DEFAULT_OUT = Path(r"C:\Users\1\Desktop\ProbablyStolen-TexturePacks\TexturePacks\out\official_based\Textures")
ALPHA_SOLID = 200                      # the ground shadow is alpha 105 and is not part of the figure


@dataclass(frozen=True)
class Recipe:
    cls: str
    n: int
    parts: tuple[tuple[str, dict], ...]    # (part name, options) in drawing order within its layer
    erase: tuple[str, ...] = ()            # which modern shapes to cut out first
    coat: bool = False                     # a cloak/coat whose hem reaches the official coat hem


SHEETS: dict[str, Recipe] = {
    # a traveller: felt hat, a bedroll pack on the back, a walking staff
    "Backpack": Recipe("mid", 4, (("pack", {}), ("wide_brim", {}), ("belt", {}), ("staff", {})), ("pack",)),
    # a kerchief at the neck and a floppy cap, a basket on the arm
    "Bandana": Recipe("mid", 4, (("kerchief_neck", {}), ("floppy_cap", {}), ("belt", {}), ("basket", {})), ("headback",)),
    # plague doctor: the beak mask under a wide hat, a short cape, a hip satchel and a cane
    "Gasmask": Recipe("mid", 4, (("cape", {}), ("satchel", {}), ("beak_mask", {}), ("wide_brim", {}), ("cane", {})), ("pack", "snout")),
    # a hooded cloak
    "Puncho": Recipe("mid", 4, (("cloak", {"drop": 26}), ("hood", {})), ("headback",)),
    # a long coat: collar, buttons, belt, a tricorne and a lantern
    "TrechCoat": Recipe("mid", 4, (("coat_cues", {}), ("tricorne", {}), ("lantern", {}))),
}
# the far figures are 4 px heads: fewer, bolder parts with exaggerated silhouettes (parts.FAR_DRAW)
FAR_SHEETS: dict[str, Recipe] = {
    "Backpack": Recipe("far", 4, (("pack", {}), ("wide_brim", {}), ("staff", {})), ("pack",)),
    "Bandana": Recipe("far", 4, (("kerchief_neck", {}), ("floppy_cap", {}), ("basket", {})), ("headback",)),
    "Gasmask": Recipe("far", 4, (("beak_mask", {}), ("wide_brim", {}), ("cane", {})), ("pack", "snout")),
    "Puncho": Recipe("far", 4, (("cloak", {"drop": 26}), ("hood", {})), ("headback",)),
    "TrechCoat": Recipe("far", 4, (("tricorne", {}), ("lantern", {}))),
}
WALKER1 = Recipe("big", 8, (("cloak_back", {}), ("cloak", {"drop": 0}), ("pointed_hat", {}), ("staff", {})), (), True)

HEAD_W, HEAD_H = 15.0, 17.0           # head size in units
CROWN_TO_CENTRE = 8.5


@dataclass
class Fig:
    top: int
    bottom: int
    crown_x: float
    head: tuple[float, float]          # head centre (x, y) in px of the cell
    shoulder: tuple[float, float]
    hip: tuple[float, float]
    hand: tuple[float, float]
    front: float                       # x of the chest front
    back: float                        # x of the back at the shoulder
    toe_f: float                       # reach of the feet ahead of and behind the hip, in px
    toe_b: float
    hem_y: float                       # where the coat's skirt ends (the legs begin)
    hem_w: float = 0.0                 # width of the figure at the hem
    reach_f: float = 0.0               # sheet-wide reach of the feet ahead of / behind the hip (px), for planting the staff
    reach_b: float = 0.0


def rows_of(mask: Image.Image) -> list[tuple[int, int] | None]:
    px = mask.load()
    w, h = mask.size
    out: list[tuple[int, int] | None] = []
    for y in range(h):
        xs = [x for x in range(w) if px[x, y]]
        out.append((min(xs), max(xs)) if xs else None)
    return out


def find_figure(mask: Image.Image, s: float) -> Fig:
    """Head, shoulder, hip, feet and the coat's hem from the silhouette of one frame (`s` = px per unit)."""
    rows = rows_of(mask)
    ys = [y for y, r in enumerate(rows) if r]
    top, bottom = ys[0], ys[-1]
    height = bottom - top + 1
    crown = [(rows[y][0] + rows[y][1]) / 2 for y in range(top, top + max(2, round(3 * s))) if rows[y]]
    crown_x = sum(crown) / len(crown)
    head = (crown_x, top + CROWN_TO_CENTRE * s)
    # shoulder: the first row below the head that is clearly wider than the head; kept in a sane band so a pack or a snout cannot move it
    head_w = HEAD_W * s
    lo, hi = top + 0.16 * height, top + 0.23 * height
    sy = hi
    for y in range(int(top + 0.12 * height), int(hi) + 1):
        r = rows[y]
        if r and r[1] - r[0] + 1 >= 1.3 * head_w:
            sy = min(max(y, lo), hi)
            break
    shoulder = (crown_x - 1.0 * s, sy)
    hip_y = sy + 0.285 * height
    r = rows[min(int(hip_y), bottom)] or (int(crown_x), int(crown_x))
    hip = ((r[0] + r[1]) / 2, hip_y)
    chest = rows[min(int(sy + 0.12 * height), bottom)] or r
    front, back = chest[1], chest[0]
    # feet: the extremes of the lowest rows relative to the hip
    foot_rows = [rows[y] for y in range(max(top, bottom - round(0.08 * height)), bottom + 1) if rows[y]]
    toe_f = max(q[1] for q in foot_rows) - hip[0]
    toe_b = min(q[0] for q in foot_rows) - hip[0]
    # hem of the coat: the last row of the unbroken wide run below the hip (a coat skirt) before the legs
    wide = max((rows[y][1] - rows[y][0] + 1) for y in range(int(sy), int(hip_y) + 1) if rows[y])
    hem_y = hip_y
    for y in range(int(hip_y), bottom):
        q = rows[y]
        if not q or q[1] - q[0] + 1 < 0.62 * wide:
            break                                   # first narrow row: the legs begin (a wide stride must not extend the coat)
        hem_y = y
    hand = (front - 3 * s, sy + 0.30 * height)
    hr = rows[int(hem_y)] or (0, 0)
    return Fig(top, bottom, crown_x, head, shoulder, hip, hand, front, back, toe_f, toe_b, hem_y, hr[1] - hr[0] + 1)


def smooth_loop(vals: list[float]) -> list[float]:
    n = len(vals)
    return [0.25 * vals[i - 1] + 0.5 * vals[i] + 0.25 * vals[(i + 1) % n] for i in range(n)]


def erase(mask_alpha: Image.Image, frame: Image.Image, fig: Fig, s: float, kinds: tuple[str, ...]) -> None:
    """Cut the modern shapes (gas-mask snout, backpack, the hair bun) out of the frame so a medieval part can replace them."""
    px = frame.load()
    w, h = frame.size
    hx, hy = fig.head

    def clear_box(x0: float, x1: float, y0: float, y1: float) -> None:
        for y in range(max(0, math.floor(y0)), min(h, math.ceil(y1))):
            for x in range(max(0, math.floor(x0)), min(w, math.ceil(x1))):
                if frame.getpixel((x, y))[3] >= ALPHA_SOLID:
                    px[x, y] = (0, 0, 0, 0)

    if "snout" in kinds:        # the gas mask's snout: right of the face, from the eyes down to the chin
        clear_box(hx + 5.2 * s, hx + 20 * s, hy - 10 * s, hy + 3 * s)
    if "headback" in kinds:     # a bun or a knot behind the head
        clear_box(hx - 16 * s, hx - 8.2 * s, hy - 12 * s, hy + 10 * s)
    if "pack" in kinds:         # the modern backpack: everything behind the back line that runs from the neck to the loins
        rows = rows_of(mask_alpha)
        y0, y1 = int(fig.shoulder[1] - 4 * s), int(fig.hip[1] - 2 * s)
        xa = rows[y0][0] if rows[y0] else fig.back
        xb = rows[y1][0] if rows[y1] else xa
        # the back line is straight between the neck and the loins, kept inside the pack's bulge
        for y in range(y0, y1 + 1):
            line = xa + (xb - xa) * (y - y0) / max(1, y1 - y0)
            clear_box(0, line + 0.2 * s, y, y + 1)


def place(frame: Image.Image, im: Image.Image, anchor: tuple[int, int], at: tuple[float, float], inside: Image.Image | None = None) -> None:
    x, y = round(at[0]) - anchor[0], round(at[1]) - anchor[1]
    if inside is not None:
        im = im.copy()
        ip, mp = inside.load(), im.load()
        for j in range(im.height):
            for i in range(im.width):
                xx, yy = x + i, y + j
                if not (0 <= xx < inside.width and 0 <= yy < inside.height and ip[xx, yy]):
                    mp[i, j] = (0, 0, 0, 0)
    tmp = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    tmp.paste(im, (x, y))
    frame.alpha_composite(tmp)


def dress_frame(frame: Image.Image, f: int, n: int, fig: Fig, recipe: Recipe, s: float, head: tuple[float, float]) -> dict[str, list]:
    cls = recipe.cls
    phase = 2 * math.pi * f / n
    sway = math.sin(phase)
    sway_f = max(0.0, min(26.0, 0.62 * fig.toe_f / s))
    sway_b = min(0.0, max(-22.0, 0.62 * fig.toe_b / s))
    hip_rel = ((fig.hip[0] - fig.shoulder[0]) / s, -(fig.hip[1] - fig.shoulder[1]) / s)
    ground = fig.bottom + 1
    # the silhouette hides the hands: the arm swings against the stride (cos of the gait phase), its reach scaled by the step width
    stride = (fig.reach_f - fig.reach_b)
    hand = (fig.hand[0] + 0.07 * stride * math.cos(phase + math.pi), fig.hand[1])
    # a staff is planted once per cycle and then slides back with the ground (like the stance foot), then lifts and swings forward
    lifted = max(1, n // 4)
    planted = n - lifted
    reach_a, reach_b = 0.62 * fig.reach_f + 2 * s, 0.05 * fig.reach_f
    if f < planted:
        tip_rel, raise_px = reach_a + (reach_b - reach_a) * f / max(1, planted - 1), 0.0
    else:
        t = (f - planted + 1) / (lifted + 1)
        tip_rel, raise_px = reach_b + (reach_a - reach_b) * t, 0.07 * (fig.bottom - fig.top) * math.sin(math.pi * t)
    tip_abs = (fig.hip[0] + tip_rel, fig.bottom + 1 - raise_px)
    sh = (head[0] - 1.0 * s, fig.shoulder[1] + (head[1] - fig.head[1]))
    layers: dict[str, list] = {"back": [], "front": [], "inside": []}
    for name, opt in recipe.parts:
        part = P.PARTS[name]
        kw: dict = dict(opt)
        if part.anchor == "head":
            at = head
            kw.update(sway=sway * 1.5)
            if name == "pointed_hat":                             # keep the tip inside the cell
                kw["tall"] = min(32.0, (head[1] - 1) / s)
        elif part.anchor == "shoulder":
            at = sh
            kw.update(hip=hip_rel, sway_f=sway_f, sway_b=sway_b, sway=sway * 1.2, bob=0.8 * math.cos(2 * phase))
            if name == "cloak":
                if recipe.coat:                                    # inside the official coat's outline, ending at its hem
                    kw["w"] = max(8.0, fig.hem_w / (2 * s) - 3)
                    kw["sway_f"], kw["sway_b"] = 0.25 * sway_f, 0.25 * sway_b
                    kw["drop"] = max(20.0, (fig.hem_y - fig.hip[1]) / s + 4)
                kw.setdefault("drop", 26)
            if name == "cloak_back":
                kw["sway_b"] = 0.2 * sway_b
                kw["w"] = max(8.0, fig.hem_w / (2 * s) - 2)
                kw["drop"] = max(20.0, (fig.hem_y - fig.hip[1]) / s + 6)
        elif part.anchor == "hand":
            at = hand
            kw.update(drop=(tip_abs[1] - hand[1]) / s, tip=(tip_abs[0] - hand[0]) / s)
            if name == "lantern":                                  # a pendulum that lags the arm by a quarter swing
                kw["swing"] = 16 * math.sin(phase - 0.5 * math.pi)
                at = (hand[0] + (4 if cls == "mid" or cls == "big" else 9) * s, hand[1])
            if name == "basket":
                kw["swing"] = 6 * math.sin(phase - 0.5 * math.pi)
                at = (hand[0] + (2 if cls != "far" else 7) * s, hand[1] - 3 * s)
        else:                                                      # belt at the hip, as wide as the figure there
            at = (fig.hip[0], fig.hip[1] - 2 * s)
            kw.update(half=max(4.0, (fig.front - fig.back) / (2 * s) * 0.5))
        im, anc = P.render(name, cls, **kw)
        layers[part.layer].append((im, anc, at))
    return layers


def compose_sheet(src: Image.Image, recipe: Recipe, cell: tuple[int, int]) -> Image.Image:
    s = P.CLASSES[recipe.cls].scale
    n, (cw, ch) = recipe.n, cell
    assert src.size == (cw * n, ch), (src.size, cell, n)
    frames, masks, figs = [], [], []
    for i in range(n):
        fr = src.crop((i * cw, 0, (i + 1) * cw, ch)).convert("RGBA")
        frames.append(fr)
        masks.append(fr.getchannel("A").point(lambda v: 255 if v >= ALPHA_SOLID else 0))
        figs.append(find_figure(masks[-1], s))
    # a spread stride makes the wide run look longer than the coat: the coat is one length, so use the shortest measured one
    drop = min(g.hem_y - g.hip[1] for g in figs)
    for g in figs:
        g.hem_y = g.hip[1] + drop
    reach_f, reach_b = max(g.toe_f for g in figs), min(g.toe_b for g in figs)
    for g in figs:
        g.reach_f, g.reach_b = reach_f, reach_b
    # head anchors: raw for 4 frames (the bob is the walk), smoothed for 8
    hx = [g.head[0] for g in figs]
    hy = [g.head[1] for g in figs]
    if n >= 8:
        hx, hy = smooth_loop(hx), smooth_loop(hy)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    for i in range(n):
        fig = figs[i]
        fr = frames[i]
        erase(masks[i], fr, fig, s, recipe.erase)
        layers = dress_frame(fr, i, n, fig, recipe, s, (hx[i], hy[i]))
        canvas = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        for im, anc, at in layers["back"]:
            place(canvas, im, anc, at)
        canvas.alpha_composite(fr)
        solid = fr.getchannel("A").point(lambda v: 255 if v >= ALPHA_SOLID else 0)
        for im, anc, at in layers["front"]:
            place(canvas, im, anc, at)
        for im, anc, at in layers["inside"]:
            place(canvas, im, anc, at, solid)
        out.paste(canvas, (i * cw, 0))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--originals", required=True, type=Path, help="folder holding the user's exported scene/animation sheets")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, Recipe, tuple[int, int]]] = []
    for k, r in SHEETS.items():
        jobs.append((f"mid{k}.520x180.png", r, (130, 180)))
        jobs.append((f"far{k}.128x45.png", FAR_SHEETS[k], (32, 45)))
    jobs.append(("walker1.1144x273.png", WALKER1, (143, 273)))
    for name, recipe, cell in jobs:
        src = Image.open(args.originals / name)
        res = compose_sheet(src, recipe, cell)
        assert res.size == src.size
        res.save(args.out / name)
        print("wrote", args.out / name)


if __name__ == "__main__":
    main()
