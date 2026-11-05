"""The farm and food items of the tavern pack: garden plants, fish, vermin and stock, wine, and the table.

The drawing lives in `items_farm_*` modules (they list functions in PICS, not ASSETS, so each file is drawn once, here).
Each picture is wrapped so its content sits where the game's own picture keeps its content.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

from PIL import Image

import items_farm_aqua
import items_farm_food
import items_farm_husb
import items_farm_plants
import items_farm_wine
from items_farm_boxes import BOXES
from itemkit_farm import anchored

SIZES = {
    r["file"]: (int(r["width"]), int(r["height"]))
    for r in csv.DictReader((Path(__file__).resolve().parents[2] / "catalog.tsv").open(encoding="utf-8", newline=""), delimiter="	")
}
ASSETS: dict[str, Callable[[], Image.Image]] = {}

# mode: 'b' bottom-aligned (things that stand), 'c' centred (things that lie or swim)
for module, group, mode in (
    (items_farm_plants, "hydroponic_plant", "b"),
    (items_farm_aqua, "aquaculture", "c"),
    (items_farm_husb, "husbandry", "c"),
    (items_farm_wine, "winemaking", "b"),
    (items_farm_food, "food", "b"),
):
    for name, fn in module.PICS.items():
        file = f"items~items_{group}@{name}.png"
        ASSETS[file] = anchored(fn, SIZES[file], BOXES[file], mode)
