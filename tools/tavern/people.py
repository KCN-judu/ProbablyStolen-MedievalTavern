"""People: the named busts, the strips of townsfolk, and the walking silhouettes, for the catalog's `character/people`
group and the character pictures of `scene/animation`. Each file is drawn by `people_figure.render` from a `Look`
(`people_cast`), so faces are generated from a few numbers and dressed in the medieval equivalent of their role.
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path

from PIL import Image

from people_cast import NAMED, crowd
from people_figure import render
from people_look import Look
from people_kit import H, W
import people_misc
import people_walk

# strip file (without .png) -> number of figures, laid out row by row in frames of 288x211
STRIP_FILES: dict[str, int] = {
    "femaleBM.1440x211": 5, "femaleBM.864x211": 3, "femaleChef.576x211": 2, "femaleEng.576x211": 2,
    "femaleFarmer.576x211": 2, "femaleLower.2880x422": 14, "femaleLower.864x211": 3, "femaleMed.576x211": 2,
    "femaleMerc.1152x211": 4, "femaleRev.2016x211": 7, "femaleSci.576x211": 2, "femaleSec.1440x211": 5,
    "femaleSecCorpo.576x211": 2, "femaleSecOff.576x211": 2, "femaleUpper.2880x422": 13, "femaleUpper.864x211": 3,
    "maleBM.1728x211": 6, "maleBM.864x211": 3, "maleChef.864x211": 3, "maleEng.1728x211": 6, "maleFarmer.1152x211": 4,
    "maleLower.2880x422": 11, "maleLower.864x211": 3, "maleMed.576x211": 2, "maleMerc.1152x211": 4,
    "maleRev.1152x211": 4, "maleSci.576x211": 2, "maleSec.1728x211": 6, "maleSecCorpo.576x211": 2,
    "maleSecOff.864x211": 3, "maleUpper.1728x422": 9, "maleUpper.864x211": 3,
}


def bbox_of(file: str) -> tuple[int, int, int, int]:
    """The area the game's original of `file` occupies (layout.tsv), so ours stays inside it."""
    with (Path(__file__).with_name("layout.tsv")).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="	"):
            if row["file"] == file:
                x0, y0, x1, y1 = (int(v) for v in row["bbox"].split())
                return x0, y0, x1, y1
    return 0, 0, W, H


def fitted(look: Look, box: tuple[int, int, int, int], col: int, cols: int, row: int) -> Image.Image:
    """Renders `look` for a frame at (col, row) of a picture whose original occupies `box`: shoulders narrowed to the
    box's sides where this frame touches them, and the whole figure lowered when the hat would rise above its top."""
    x0, y0, x1, y1 = box
    sw = look.sw
    if col == 0:
        sw = min(sw, 144 - x0 - 5)
    if col == cols - 1:
        sw = min(sw, x1 - col * W - 144 - 5)
    img = render(replace(look, sw=sw))
    if row == 0:
        top = img.getchannel("A").getbbox()
        if top is not None and top[1] < y0:
            shifted = Image.new("RGBA", img.size, (0, 0, 0, 0))
            shifted.alpha_composite(img, (0, y0 - top[1]))
            img = shifted
    # whatever still pokes past the original's sides (a pauldron, a hat brim) is cut at the box
    lo, hi = (x0 - col * W if col == 0 else 0), (x1 - col * W if col == cols - 1 else W)
    if lo > 0 or hi < W:
        img.paste((0, 0, 0, 0), (0, 0, max(0, lo), H))
        img.paste((0, 0, 0, 0), (min(W, hi), 0, W, H))
    return img


def portrait(name: str) -> Callable[[], Image.Image]:
    """A drawing function for the named bust."""
    file = f"{name}.288x211.png"
    return lambda: fitted(NAMED[name], bbox_of(file), 0, 1, 0)


def strip(key: str, count: int) -> Callable[[], Image.Image]:
    """A drawing function for a strip: `count` generated people in frames of 288x211, filled row by row."""
    def draw() -> Image.Image:
        size = key.split(".")[1].split("x")
        width, height = int(size[0]), int(size[1])
        out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        cols = width // W
        box = bbox_of(f"{key}.png")
        for i, look in enumerate(crowd(key, count)):
            out.alpha_composite(fitted(look, box, i % cols, cols, i // cols), ((i % cols) * W, (i // cols) * H))
        return out
    return draw


ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    **{f"{n}.288x211.png": portrait(n) for n in NAMED},
    **{f"{k}.png": strip(k, c) for k, c in STRIP_FILES.items()},
    **people_walk.PICTURES,
    **people_misc.PICTURES,
}
