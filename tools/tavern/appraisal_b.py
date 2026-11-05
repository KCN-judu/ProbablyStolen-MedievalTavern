"""Appraisal close-ups, second half (files 67 to 131 of the group, sorted by name): the tavern pack's drawings.

The drawing lives in `appraisal_b_food`, `appraisal_b_docs` and `appraisal_b_items`; this module only lists them
under the catalog file names so that a single `--module appraisal_b` builds the whole set.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageChops

import appraisal_b_docs
import appraisal_b_food

try:
    import appraisal_b_items
    _ITEMS = appraisal_b_items.DRAWINGS
except ImportError:           # items are drawn last; the rest builds without them
    _ITEMS = {}

_DRAWINGS = {**appraisal_b_food.DRAWINGS, **appraisal_b_docs.DRAWINGS, **_ITEMS}


def _bboxes() -> dict[str, tuple[int, int, int, int]]:
    """Where each original's content sits (layout.tsv), so nothing of ours lands outside it."""
    out: dict[str, tuple[int, int, int, int]] = {}
    with (Path(__file__).parent / "layout.tsv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="	"):
            if r["file"] in _DRAWINGS:
                a, b, c, d = (int(v) for v in r["bbox"].split())
                out[r["file"]] = (a, b, c, d)
    return out


def _inside(name: str, draw: Callable[[], Image.Image]) -> Callable[[], Image.Image]:
    def run() -> Image.Image:
        image = draw()
        box = _bboxes().get(name)
        if box:
            keep = Image.new("L", image.size, 0)
            keep.paste(255, box)
            image.putalpha(ImageChops.multiply(image.getchannel("A"), keep))
        return image
    return run


ASSETS: dict[str, Callable[[], Image.Image]] = {name: _inside(name, draw) for name, draw in _DRAWINGS.items()}
