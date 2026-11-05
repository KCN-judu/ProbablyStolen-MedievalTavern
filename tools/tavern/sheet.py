"""Contact sheets for looking at pictures: a folder of PNGs as a labelled grid, or two folders side by side.

    python tools/tavern/sheet.py <folder> <out.png> [--width PX] [--cell PX] [--against OTHER_FOLDER]
    python tools/tavern/sheet.py <folder> <out.png> --only text,text   # only files whose name contains one of the texts

With --against, each file of <folder> is shown with the file of the same name from OTHER_FOLDER on its left (for example
the game's exported originals, kept outside the repository), so a new drawing can be judged next to what it replaces.
Pictures larger than --cell are shrunk, smaller ones are enlarged by whole numbers; transparency shows as grey.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GREY = (110, 110, 120, 255)


def fitted(image: Image.Image, cell: int) -> Image.Image:
    w, h = image.size
    if max(w, h) > cell:
        k = cell / max(w, h)
        return image.resize((max(1, round(w * k)), max(1, round(h * k))), Image.Resampling.LANCZOS)
    k = max(1, cell // max(w, h)) if max(w, h) * 2 <= cell else 1
    return image.resize((w * k, h * k), Image.Resampling.NEAREST) if k > 1 else image


def on_grey(image: Image.Image) -> Image.Image:
    base = Image.new("RGBA", image.size, GREY)
    base.alpha_composite(image)
    return base.convert("RGB")


def option(argv: Sequence[str], name: str, default: str | None = None) -> str | None:
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv: Sequence[str]) -> int:
    folder, out = Path(argv[0]), Path(argv[1])
    width = int(option(argv, "--width", "1600") or 1600)
    cell = int(option(argv, "--cell", "220") or 220)
    against = Path(option(argv, "--against") or "") if "--against" in argv else None
    only = tuple((option(argv, "--only") or "").split(",")) if "--only" in argv else ()
    names = sorted(f.name for f in folder.glob("*.png") if not only or any(o in f.name for o in only))
    font = ImageFont.load_default()
    tiles: list[tuple[str, list[Image.Image]]] = []
    for name in names:
        pair = []
        if against is not None:
            other = against / name
            pair.append(on_grey(fitted(Image.open(other).convert("RGBA"), cell)) if other.exists() else Image.new("RGB", (cell // 2, 20), (60, 20, 20)))
        pair.append(on_grey(fitted(Image.open(folder / name).convert("RGBA"), cell)))
        tiles.append((name, pair))
    x = y = 4
    row_h = 0
    placed: list[tuple[int, int, str, list[Image.Image]]] = []
    for name, pair in tiles:
        w = sum(i.width for i in pair) + 4 * (len(pair) - 1)
        if x + max(w, 100) + 4 > width:
            x, y, row_h = 4, y + row_h + 18, 0
        placed.append((x, y, name, pair))
        x += max(w, 100) + 8
        row_h = max(row_h, max(i.height for i in pair))
    sheet = Image.new("RGB", (width, y + row_h + 22), (60, 60, 70))
    d = ImageDraw.Draw(sheet)
    for px, py, name, pair in placed:
        cx = px
        for im in pair:
            sheet.paste(im, (cx, py))
            cx += im.width + 4
        d.text((px, py + max(i.height for i in pair) + 2), name[:42], fill=(255, 255, 255), font=font)
    sheet.save(out)
    print(out, sheet.size, len(tiles), "pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
