"""Contact sheets of the parts library, shown on a plain mannequin that is itself drawn from scratch."""

from __future__ import annotations

from PIL import Image, ImageDraw

from kit import RAMPS, Art
from partdef import Part

BG = (58, 62, 74)
FIG_SKIN = RAMPS["sand"]


def mannequin(hw: int, w: int, h: int, ax: int, ay: int) -> Image.Image:
    """A plain head and shoulders (brow line at y = ay, centre x = ax); only used for the sheets."""
    a = Art(w, h)
    skin = [(60, 34, 36), (150, 100, 80), (186, 132, 104), (212, 160, 126), (230, 184, 150)]
    hair = [(30, 20, 24), (52, 36, 36), (74, 52, 44), (96, 70, 56), (110, 84, 66)]
    sh = a.mask().ellipse(ax, ay + 2.2 * hw, 1.55 * hw, 0.9 * hw).clip_rows(ay + 1.2 * hw, h)
    a.fill(sh, [(36, 30, 40), (62, 56, 70), (84, 78, 92), (104, 98, 112), (120, 114, 128)], radius=6)
    neck = a.mask().rect(ax - 0.22 * hw, ay + 0.9 * hw, ax + 0.22 * hw, ay + 1.4 * hw)
    a.fill(neck, skin, radius=3, base=0.4)
    head = a.mask().ellipse(ax, ay + 0.38 * hw, hw / 2 - 1, 0.68 * hw)
    a.fill(head, skin, radius=6)
    hairm = a.mask().ellipse(ax, ay + 0.38 * hw, hw / 2 - 0.5, 0.7 * hw).clip_rows(0, ay + 1)
    hairm.add(a.mask().rect(ax - hw / 2 + 0.5, ay - 4, ax - hw / 2 + 4, ay + 0.35 * hw))
    hairm.add(a.mask().rect(ax + hw / 2 - 4, ay - 4, ax + hw / 2 - 0.5, ay + 0.35 * hw))
    a.fill(hairm, hair, radius=4)
    ey = int(ay + 0.42 * hw)
    for sx in (-1, 1):
        a.px(int(ax + sx * 0.2 * hw), ey, skin[0]), a.px(int(ax + sx * 0.2 * hw) + 1, ey, skin[0])
        a.line([(ax + sx * 0.2 * hw - 1, ey - 3), (ax + sx * 0.2 * hw + 2, ey - 3)], hair[1])
    a.line([(ax, ey + 2), (ax, ey + 7)], skin[1])
    a.line([(ax - 3, ay + 0.72 * hw), (ax + 3, ay + 0.72 * hw)], (150, 78, 76))
    return a.im


def worn(p: Part, hw: int, cellw: int, cellh: int, ax: int, ay: int) -> Image.Image:
    """The part on the mannequin, anchored at the mannequin's landmark (brow for hats)."""
    cell = Image.new("RGBA", (cellw, cellh), BG + (255,))
    lm = {"brow": (ax, ay), "nose": (ax, ay + 0.62 * hw), "chin": (ax, ay + 1.0 * hw), "neck": (ax, ay + 1.12 * hw),
          "shoulders": (ax, ay + 1.35 * hw), "chest": (ax, ay + 1.55 * hw), "mouth": (ax, ay + 0.72 * hw),
          "cheek_l": (ax - 0.27 * hw, ay + 0.55 * hw), "cheek_r": (ax + 0.27 * hw, ay + 0.55 * hw), "eyes": (ax, ay + 0.42 * hw),
          "cheek_c": (ax, ay + 0.55 * hw), "eye_l": (ax - 0.2 * hw, ay + 0.42 * hw), "eyes_low": (ax, ay + 0.5 * hw),
          "forehead": (ax, ay + 0.1 * hw), "jaw": (ax, ay + 0.8 * hw)}
    body = mannequin(hw, cellw, cellh, ax, ay)
    lx, ly = lm.get(p.landmark, (ax, ay))
    ox, oy = round(lx - p.anchor[0]), round(ly - p.anchor[1])
    if p.layer == "back":
        _paste(cell, p.img, ox, oy)
        cell.alpha_composite(body)
    else:
        cell.alpha_composite(body)
        _paste(cell, p.img, ox, oy)
    return cell


def _paste(cell: Image.Image, img: Image.Image, ox: int, oy: int) -> None:
    x0, y0 = max(0, -ox), max(0, -oy)
    x1, y1 = min(img.width, cell.width - ox), min(img.height, cell.height - oy)
    if x1 > x0 and y1 > y0:
        cell.alpha_composite(img.crop((x0, y0, x1, y1)), (ox + x0, oy + y0))


def pair_back_front(parts: list[Part], hw: int, cw: int, ch: int, ax: int, ay: int) -> Image.Image:
    cell = Image.new("RGBA", (cw, ch), BG + (255,))
    body = mannequin(hw, cw, ch, ax, ay)
    for p in parts:
        if p.layer == "back":
            _paste(cell, p.img, ax - p.anchor[0], ay - p.anchor[1])
    cell.alpha_composite(body)
    for p in parts:
        if p.layer == "front":
            _paste(cell, p.img, ax - p.anchor[0], ay - p.anchor[1])
    return cell


def sheet(cells: list[tuple[Image.Image, str]], cols: int, scale: int = 2) -> Image.Image:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tavern"))
    import font
    from pix import Pix
    cw, ch = cells[0][0].size
    lab = 12
    rows = (len(cells) + cols - 1) // cols
    W, H = cols * (cw * scale + 4) + 4, rows * (ch * scale + lab + 4) + 4
    out = Pix(W, H, BG, seed=1)
    for i, (img, name) in enumerate(cells):
        x, y = 4 + (i % cols) * (cw * scale + 4), 4 + (i // cols) * (ch * scale + lab + 4)
        out.paste(img.resize((cw * scale, ch * scale), Image.NEAREST), x, y)
        font.write(out, x + 1, y + ch * scale + 2, name[: (cw * scale) // 6], (222, 214, 190))
    return out.im


def landmark_cells(parts: list[Part], hw: int, ax: int, ay: int, cw: int, ch: int) -> list[tuple[Image.Image, str]]:
    return [(worn(p, hw, cw, ch, ax, ay), p.id) for p in parts]
