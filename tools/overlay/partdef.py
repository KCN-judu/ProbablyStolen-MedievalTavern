"""The record of one library part and the helpers that write the library (PNGs + parts.json)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from PIL import Image


@dataclass
class Part:
    id: str                    # file stem
    cat: str                   # hats | garments | marks
    style: str                 # e.g. coif, hood_front, tabard
    img: Image.Image
    anchor: tuple[int, int]    # pixel of the image that lands on the landmark
    landmark: str              # crown | brow | neck | chin | shoulders | chest | cheek_l | cheek_r | eyes | jaw | forehead | nose
    layer: str                 # back (behind the figure) | front (over the figure)
    width: int                 # natural width this part was drawn for (head width for hats, shoulder width for garments)
    colour: str = ""
    size: str = ""
    tags: list[str] = field(default_factory=list)
    clip: bool = False         # True: composer clips the part to the figure's silhouette (straps, aprons, tabards)
    grow: int = 0              # with clip: how many pixels beyond the silhouette the part may reach (capes over shoulders)
    alpha_part: bool = False   # translucent overlay (rouge, soot, quilting): composited as a tint, not as paint
    erase: str = ""            # hats: "above" = hair above the hat line is erased, "" = hair stays
    mirror_of: str = ""        # a part drawn as the mirror image of another (kept for pairing)

    def meta(self) -> dict:
        d = asdict(self)
        d.pop("img")
        d["file"] = f"{self.cat}/{self.id}.png"
        d["size_px"] = list(self.img.size)
        d["anchor"] = list(self.anchor)
        return d


def write_library(parts: list[Part], root: Path) -> None:
    for sub in {p.cat for p in parts}:
        (root / sub).mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    for p in parts:
        key = f"{p.cat}/{p.id}"
        assert key not in seen, key
        seen.add(key)
        p.img.save(root / p.cat / f"{p.id}.png")
    meta = {
        "about": "Parts drawn entirely by code (tools/overlay). Anchor = pixel of the image that lands on the landmark. "
                 "Landmarks: crown/brow/neck/chin/shoulders/chest/cheek_l/cheek_r/eyes/jaw/forehead/nose. "
                 "width = head width (hats, marks) or shoulder width (garments) the part was drawn for.",
        "parts": [p.meta() for p in parts],
    }
    (root / "parts.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
