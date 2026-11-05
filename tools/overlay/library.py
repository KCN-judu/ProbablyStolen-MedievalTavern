"""Loads the parts library (parts.json + PNGs) that tools/overlay/build_parts.py writes."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass
class PartRec:
    id: str
    cat: str
    style: str
    anchor: tuple[int, int]
    landmark: str
    layer: str
    width: int
    colour: str
    size: str
    tags: list[str]
    clip: bool
    grow: int
    alpha_part: bool
    erase: str
    img: Image.Image


class Library:
    def __init__(self, root: Path) -> None:
        meta = json.loads((root / "parts.json").read_text(encoding="utf-8"))
        self.parts: list[PartRec] = []
        for m in meta["parts"]:
            img = Image.open(root / m["file"]).convert("RGBA")
            self.parts.append(PartRec(m["id"], m["cat"], m["style"], tuple(m["anchor"]), m["landmark"], m["layer"], m["width"],
                                      m["colour"], m["size"], m["tags"], m["clip"], m["grow"], m["alpha_part"], m["erase"], img))
        self.by_id = {p.id: p for p in self.parts}

    def find(self, style: str | None = None, colours: list[str] | None = None, size: str | None = None,
             **attrs: object) -> list[PartRec]:
        out = []
        for p in self.parts:
            if style and p.style != style:
                continue
            if colours and p.colour not in colours:
                continue
            if size and p.size not in (size, ""):
                continue
            if any(getattr(p, k) != v for k, v in attrs.items()):
                continue
            out.append(p)
        return out

    def prefix(self, prefix: str, size: str | None = None) -> list[PartRec]:
        """Parts whose id starts with `prefix`; with `size`, sized parts must match it (unsized ones always pass)."""
        return [p for p in self.parts if p.id.startswith(prefix) and (size is None or p.size in (size, ""))]
