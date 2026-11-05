"""Composer: turns the user's own exported portrait sheets into medieval-dress versions using the parts library.

    python tools/overlay/compose_busts.py --originals %TEMP%\\tp_export\\character\\people --out out\\official_based\\Textures

The originals are read from the user's own export and the results are written ONLY to --out (git-ignored, local).
Nothing of the originals is copied into the repository, embedded in code or cached outside --out / %TEMP%.
"""

from __future__ import annotations

import argparse
import colorsys
import os
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PIL import Image, ImageFilter  # noqa: E402

import recipes  # noqa: E402
from landmarks import FH, FW, Landmarks, analyse, debug_overlay, is_skin  # noqa: E402
from library import Library, PartRec  # noqa: E402
from recolor import convert_face_gear, luma, recolor  # noqa: E402

REPO = HERE.parent.parent
DEFAULT_OUT = REPO / "out" / "official_based" / "Textures"
FACE_LMS = {"cheek_l", "cheek_r", "cheek_c", "eyes", "eye_l", "eyes_low", "nose", "mouth", "jaw", "forehead", "chin", "brow"}
SIZE_RE = re.compile(r"\.(\d+)x(\d+)\.png$")


def _forbidden(out: Path) -> None:
    """Refuses to write into the code and documentation folders; the pack folder (Textures) is fine."""
    rp = out.resolve()
    for bad in ("tools", "doc"):
        try:
            rp.relative_to((REPO / bad).resolve())
        except ValueError:
            continue
        raise SystemExit(f"refusing to write derived pictures inside {bad}\\: {rp}")


def warm_skin(img: Image.Image, lm: Landmarks) -> None:
    """A gentle tone grade: skin a little warmer (the medieval light is candle light)."""
    px = img.load()
    for y in range(max(0, lm.top), FH):
        for x in range(FW):
            r, g, b, a = px[x, y]
            if a >= 128 and is_skin((r, g, b), lm):
                px[x, y] = (min(255, round(r * 1.04 + 2)), g, round(b * 0.92), a)


def foreign(c: tuple[int, int, int], lm: Landmarks) -> bool:
    """Clearly not this person's skin: another hue, much more saturated, or nearly grey."""
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    sh, ss, sv = lm.skin_hsv
    dh = min(abs(h - sh), 1 - abs(h - sh))
    return v > 0.2 and (dh > 0.06 or s > 1.5 * ss + 0.1 or s < 0.4 * ss)


def erase_hair(img: Image.Image, lm: Landmarks) -> None:
    """A closed hat replaces the hair above the forehead line (the output is local only).

    Also removes what is left of an original hat or fringe below that line: non-skin, non-outline pixels that touch the
    erased area, down to just above the brows.
    """
    px = img.load()
    x0, x1 = max(0, int(lm.cx - lm.hw / 2 - 14)), min(FW - 1, int(lm.cx + lm.hw / 2 + 14))
    for y in range(0, lm.hat_y):
        for x in range(x0, x1 + 1):
            px[x, y] = (0, 0, 0, 0)
    stack = [(x, lm.hat_y) for x in range(x0, x1 + 1)]
    seen = set(stack)
    ylim = lm.eyes_y - 4
    while stack:
        x, y = stack.pop()
        if y > ylim or not (x0 <= x <= x1):
            continue
        r, g, b, a = px[x, y]
        if a < 128:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1)):
                if (nx, ny) not in seen:
                    seen.add((nx, ny)), stack.append((nx, ny))
            continue
        if not foreign((r, g, b), lm) or luma((r, g, b)) < 52:
            continue
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen:
                seen.add((nx, ny)), stack.append((nx, ny))


def _layer(part: PartRec, lm: Landmarks, dx: int, dy: int) -> tuple[Image.Image, int, int]:
    px, py = lm.point(part.landmark)
    return part.img, round(px - part.anchor[0] + dx), round(py - part.anchor[1] + dy)


def paste_clipped(canvas: Image.Image, part: PartRec, lm: Landmarks, dx: int, dy: int, clip: Image.Image | None, orig: Image.Image,
                  min_luma: float | None) -> None:
    img, ox, oy = _layer(part, lm, dx, dy)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(img, (ox, oy))
    if clip is not None or min_luma is not None:
        lp, cp, op = layer.load(), clip.load() if clip else None, orig.load()
        for y in range(max(0, oy), min(FH, oy + img.height)):
            for x in range(max(0, ox), min(FW, ox + img.width)):
                if lp[x, y][3] == 0:
                    continue
                if cp is not None and cp[x, y] < 128:
                    lp[x, y] = (0, 0, 0, 0)
                elif min_luma is not None and luma(op[x, y][:3]) < min_luma:
                    lp[x, y] = (0, 0, 0, 0)
    canvas.alpha_composite(layer)


def blend_tint(canvas: Image.Image, part: PartRec, lm: Landmarks, dx: int, dy: int, clip: Image.Image | None) -> None:
    """Translucent parts: blended into the pixels below (skin only for face tints, cloth only for garment tints)."""
    img, ox, oy = _layer(part, lm, dx, dy)
    cp, dp, ip = clip.load() if clip else None, canvas.load(), img.load()
    face = part.landmark in FACE_LMS
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = ip[x, y]
            X, Y = ox + x, oy + y
            if a == 0 or not (0 <= X < FW and 0 <= Y < FH):
                continue
            if cp is not None and cp[X, Y] < 128:
                continue
            tr, tg, tb, ta = dp[X, Y]
            if ta < 128:
                continue
            if face and not is_skin((tr, tg, tb), lm):
                continue
            if not face and is_skin((tr, tg, tb), lm):
                continue
            k = a / 255
            dp[X, Y] = (round(tr + (r - tr) * k), round(tg + (g - tg) * k), round(tb + (b - tb) * k), ta)


def place_pauldrons(canvas: Image.Image, part: PartRec, frame: Image.Image, lm: Landmarks | None = None) -> None:
    """A guard on each shoulder: found from the silhouette at shoulder height (outer edge and the top edge there)."""
    a = frame.getchannel("A").load()
    sh = LM_CACHE["sh_y"]
    row = sh + 16
    xs = [x for x in range(FW) if a[x, row] >= 128]
    if not xs:
        return
    for side, flip in ((xs[0], False), (xs[-1], True)):
        cx = side + (12 if not flip else -12)
        top = next((y for y in range(sh - 4, row) if a[min(FW - 1, cx), y] >= 128), sh + 4)
        img = part.img.transpose(Image.FLIP_LEFT_RIGHT) if flip else part.img
        canvas.alpha_composite(img, (cx - part.anchor[0], top - part.anchor[1] - 2)) if cx - part.anchor[0] >= 0 and top - 5 >= 0 else None


LM_CACHE: dict[str, int] = {}


SHADOW_DEPTH = {"kettle_helm": 3, "wide_brim": 3, "felt_hat": 3, "guild_cap": 2, "feathered_cap": 2, "skullcap": 2, "leather_cap": 2,
                "toque": 2, "cook_cap": 2, "sallet": 2, "coif": 2, "kerchief": 2}


def hat_shadow(canvas: Image.Image, part: PartRec, lm: Landmarks, dx: int, dy: int, depth: int) -> None:
    """The hat's shadow on the forehead: the rows under its lower edge, over the face, are darkened (strongest first)."""
    img, ox, oy = _layer(part, lm, dx, dy)
    ip, cp = img.load(), canvas.load()
    factors = (0.66, 0.8, 0.9)[:depth]
    for x in range(img.width):
        X = ox + x
        if abs(X - lm.cx) > lm.hw * 0.34 or not (0 <= X < FW):
            continue
        y = 0
        while y < img.height and ip[x, y][3] == 0:
            y += 1
        while y < img.height and ip[x, y][3] > 0:
            y += 1
        if y >= img.height:
            continue
        for k, f in enumerate(factors):
            Y = oy + y + k
            if 0 <= Y < FH:
                r, g, b, a = cp[X, Y]
                if a >= 128 and luma((r, g, b)) >= 50:
                    cp[X, Y] = (round(r * f), round(g * f * 0.98), round(min(255, b * f * 1.04)), a)


def compose_frame(frame: Image.Image, lm: Landmarks, outfit: recipes.Outfit, seed: int, role: str = "", lib: Library | None = None, gear: bool = True) -> Image.Image:
    import random
    LM_CACHE['sh_y'] = lm.sh_y
    rng = random.Random(seed ^ 0x5EED)
    orig_alpha = frame.getchannel("A").point(lambda p: 255 if p >= 128 else 0)
    fig = recolor(frame, lm, outfit.ramps, whole=outfit.whole, seed=seed)
    mask_ramp = "linen" if role == "Med" else rng.choice(("charcoal", "grey", "leather"))
    if role in ("Med", "Sci") and rng.random() < 0.6:
        mask_ramp = "leather"
    flags = convert_face_gear(fig, frame, lm, mask_ramp, seed) if gear else {"mask": False, "goggles": False}
    warm_skin(fig, lm)
    if outfit.erase_hair:
        erase_hair(fig, lm)
    items = list(outfit.items)
    if flags["mask"] and lib is not None:
        if role in ("Med", "Sci") and mask_ramp == "leather":
            items.append(recipes.Item(lib.by_id["plague_beak_" + rng.choice(("leather", "brown"))]))
        else:
            # a muffler pulled over the (recoloured) mask hides filters and straps
            sz = "S" if lm.hw < 44 else ("M" if lm.hw <= 50 else "L")
            col = "linen" if role == "Med" else rng.choice(("charcoal", "moss", "wine", "indigo", "ochre"))
            sc = [p for p in lib.find(style="scarf_cover", colours=[col]) if p.size == sz]
            if sc and not any(i.part.style == "scarf_cover" for i in items):
                items.append(recipes.Item(sc[0]))
    canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    items.sort(key=lambda it: recipes.STYLE_Z.get(it.part.style, 40))
    for it in (i for i in items if i.part.layer == "back"):
        paste_clipped(canvas, it.part, lm, it.dx, it.dy, None, frame, None)
    canvas.alpha_composite(fig)
    for it in (i for i in items if i.part.layer == "front"):
        p = it.part
        if p.style == "pauldron":
            place_pauldrons(canvas, p, frame)
            continue
        clip = None
        if p.clip:
            clip = orig_alpha.filter(ImageFilter.MaxFilter(2 * p.grow + 1)) if p.grow else orig_alpha
        if p.alpha_part:
            blend_tint(canvas, p, lm, it.dx, it.dy, clip)
        else:
            free = p.style in ("eyepatch", "bandage")
            ml = 46 if (p.cat == "marks" and not free) else None
            if p.style in SHADOW_DEPTH:
                hat_shadow(canvas, p, lm, it.dx, it.dy, SHADOW_DEPTH[p.style])
            paste_clipped(canvas, p, lm, it.dx, it.dy, clip, frame, ml)
    # keep the alpha binary and the output inside the frame
    a = canvas.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    canvas.putalpha(a)
    return canvas


def process_file(path: Path, lib: Library, out_dir: Path, debug: Path | None, cmp_dir: Path | None) -> list[tuple[str, int, Image.Image, list[str]]]:
    m = SIZE_RE.search(path.name)
    if not m:
        return []
    W, H = int(m.group(1)), int(m.group(2))
    if W % FW or H % FH:
        return []
    ro = recipes.role_of(path.name)
    if ro is None:
        return []
    role, sex = ro
    sheet = Image.open(path).convert("RGBA")
    result = sheet.copy()
    cols, rows = W // FW, H // FH
    prev: dict[str, str] = {}
    fcol: dict[str, str] = {}
    shots = []
    for i in range(rows * cols):
        r, c = divmod(i, cols)
        box = (c * FW, r * FH, c * FW + FW, r * FH + FH)
        frame = sheet.crop(box)
        lm = analyse(frame)
        if lm is None:
            continue
        seed = zlib.crc32(f"{path.name}:{i}".encode())
        import random
        ctx = recipes.Ctx(lib, random.Random(seed), lm, sex, prev, fcol)
        outfit = recipes.make_outfit(ctx, path.name)
        new = compose_frame(frame, lm, outfit, seed, role, lib, gear=path.name.split('.')[0] not in recipes.NO_GEAR)
        result.paste(new, box[:2])
        if debug is not None:
            debug_overlay(frame, lm, 2).save(debug / f"{path.stem}_{i}.png")
        shots.append((path.stem, i, new, outfit.log))
        if cmp_dir is not None:
            pair = Image.new("RGBA", (FW * 2, FH), (90, 110, 90, 255))
            for k, im in enumerate((frame, new)):
                bg = Image.new("RGBA", frame.size, (90, 110, 90, 255))
                bg.alpha_composite(im)
                pair.paste(bg, (k * FW, 0))
            pair.convert("RGB").save(cmp_dir / f"{path.stem}_{i}.png")
    result.save(out_dir / path.name)
    return shots


def contact_sheet(shots: list[tuple[str, int, Image.Image, list[str]]], path: Path) -> None:
    """All new frames, cropped to head and shoulders, 12 per row (derived pictures: stays under out/)."""
    cw, ch, cols = 200, 180, 12
    rows = (len(shots) + cols - 1) // cols
    sh = Image.new("RGBA", (cols * cw, rows * ch), (90, 110, 90, 255))
    for k, (_, _, im, _) in enumerate(shots):
        sh.alpha_composite(im.crop((44, 31, 244, 211)), ((k % cols) * cw, (k // cols) * ch))
    sh.convert("RGB").save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--originals", type=Path, default=Path(os.path.expandvars(r"%TEMP%\tp_export\character\people")))
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--parts", type=Path, default=HERE / "parts")
    ap.add_argument("--only", default="", help="comma separated substrings of file names")
    ap.add_argument("--debug", type=Path, default=None, help="folder for landmark overlays (use a folder under %%TEMP%%)")
    ap.add_argument("--compare", type=Path, default=None, help="folder for side-by-side comparisons (under %%TEMP%%)")
    a = ap.parse_args()
    _forbidden(a.out)
    for d in (a.debug, a.compare):
        if d is not None:
            _forbidden(d)
            d.mkdir(parents=True, exist_ok=True)
    a.out.mkdir(parents=True, exist_ok=True)
    lib = Library(a.parts)
    only = [s for s in a.only.split(",") if s]
    shots = []
    n = 0
    for p in sorted(a.originals.glob("*.png")):
        if only and not any(s in p.name for s in only):
            continue
        s = process_file(p, lib, a.out, a.debug, a.compare)
        if s:
            n += 1
            shots += s
    contact_sheet(shots, a.out.parent / "busts_sheet.png")
    print(f"{n} pictures, {len(shots)} frames -> {a.out}")


if __name__ == "__main__":
    main()
