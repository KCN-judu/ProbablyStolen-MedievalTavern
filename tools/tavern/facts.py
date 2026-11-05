"""Writes layout.tsv: the numbers a drawing needs about every picture of catalog.tsv, and no pixel of the game's art.

    python tools/tavern/facts.py "<game folder>" [--out tools/tavern/layout.tsv]

For each catalog row: `file`, the picture's size, `bbox` (the rectangle the picture's visible pixels fill, x0 y0 x1 y1,
or 0 0 0 0 for an empty picture) and `border` (left bottom right top, the nine-slice border the game's sprite gives
it, 0 0 0 0 when it has none). A scene-sized layer is mostly empty, and where its content sits and where a panel
stretches is what a new drawing has to respect; the colours and shapes inside are the artist's own.
"""

from __future__ import annotations

import csv
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, cast

import UnityPy
from PIL import Image

DATA_FOLDER: Final = "Probably Stolen_Data"
SCENE_FILES: Final = ("sharedassets0.assets", "sharedassets1.assets")
SUPPORT: Final = ("globalgamemanagers", "resources.assets")
VISIBLE_ALPHA: Final = 8
Row = Mapping[str, str]


def bbox_of(image: Image.Image) -> tuple[int, int, int, int]:
    """The rectangle of pixels more opaque than VISIBLE_ALPHA; all zeros for a picture with none."""
    alpha = image.convert("RGBA").getchannel("A").point(lambda a: 255 if a > VISIBLE_ALPHA else 0)
    box = alpha.getbbox()
    return box if box is not None else (0, 0, 0, 0)


def read_catalog(path: Path) -> list[Row]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def borders(env: object, scene_file: str) -> Mapping[str, tuple[int, int, int, int]]:
    """Texture name -> border of the sprite that covers the whole texture, for the sprites of one scene file."""
    found: dict[str, tuple[int, int, int, int]] = {}
    for o in cast("Sequence[object]", getattr(env, "objects")):
        if getattr(o, "type").name != "Sprite" or getattr(getattr(o, "assets_file"), "name") != scene_file:
            continue
        tree = cast("Mapping[str, Mapping[str, float]]", getattr(o, "read_typetree")())
        b = tree.get("m_Border")
        if b is None or not any(b.values()):
            continue
        sprite = getattr(o, "read")()
        try:
            texture = sprite.m_RD.texture.read()
        except Exception:
            continue
        r = tree["m_Rect"]
        if round(r["width"]) == texture.m_Width and round(r["height"]) == texture.m_Height:
            found[str(texture.m_Name)] = (round(b["x"]), round(b["y"]), round(b["z"]), round(b["w"]))
    return found


def main(argv: Sequence[str]) -> int:
    game = Path(argv[0]) if argv else Path(".")
    data = game if game.name == DATA_FOLDER else game / DATA_FOLDER
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path(__file__).with_name("layout.tsv")
    catalog = read_catalog(Path(__file__).resolve().parents[2] / "catalog.tsv")
    rows: list[list[str]] = []
    for scene_file in SCENE_FILES:
        env = UnityPy.load(*(str(data / f) for f in (scene_file, *SUPPORT) if (data / f).exists()))
        border_of = borders(env, scene_file)
        textures = {
            f"{t.m_Name}.{t.m_Width}x{t.m_Height}": t
            for t in (o.read() for o in env.objects if o.type.name == "Texture2D" and o.assets_file.name == scene_file)
        }
        for row in catalog:
            if row["kind"] != "scene" or row["source"] != scene_file:
                continue
            t = textures.get(row["file"].removesuffix(".png"))
            if t is None:
                continue
            x0, y0, x1, y1 = bbox_of(t.image)
            b = border_of.get(str(t.m_Name), (0, 0, 0, 0))
            rows.append([row["file"], str(t.m_Width), str(t.m_Height), f"{x0} {y0} {x1} {y1}", " ".join(map(str, b))])
        print(scene_file, len(rows), "rows so far")
    rows.sort()
    with out.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["file", "width", "height", "bbox", "border"])
        w.writerows(rows)
    print("wrote", out, len(rows), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
