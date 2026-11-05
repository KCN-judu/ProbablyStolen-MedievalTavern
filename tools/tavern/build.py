"""Draws the medieval-tavern pack: every picture the drawing modules offer, written as the PNG file a pack names it.

    python tools/tavern/build.py [--out Textures] [--only TEXT[,TEXT...]] [--module NAME[,NAME...]]

Each drawing module lists its pictures in ASSETS, by the file name of catalog.tsv. This script checks every picture
against the catalog (a name the game does not have, or a size it does not use, stops the build), writes the files, and
says how much of the catalog the pack covers. The pictures are generated from code; nothing of the game's art is read.
--module draws only the named modules (without the .py), so a module being written does not depend on the others importing.
"""

from __future__ import annotations

import csv
import importlib
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Final, cast

from PIL import Image

HERE: Final = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
Drawing = Callable[[], Image.Image]
TOOLS: Final = ("build", "sheet", "facts")      # scripts of this folder that draw nothing (facts needs UnityPy and the game)


def drawing_modules(names: Sequence[str] = ()) -> Mapping[str, Mapping[str, Drawing]]:
    """Every module of this folder that lists pictures in ASSETS, by module name (only those in `names`, if given). A new
    drawing module needs no registration: it only has to define ASSETS."""
    found: dict[str, Mapping[str, Drawing]] = {}
    for path in sorted(HERE.glob("*.py")):
        if path.stem in TOOLS or (names and path.stem not in names):
            continue
        module = importlib.import_module(path.stem)
        assets = getattr(module, "ASSETS", None)
        if isinstance(assets, Mapping):
            found[path.stem] = cast("Mapping[str, Drawing]", assets)
    return found


def catalog_sizes(path: Path) -> Mapping[str, tuple[int, int]]:
    with path.open(encoding="utf-8", newline="") as f:
        return {r["file"]: (int(r["width"]), int(r["height"])) for r in csv.DictReader(f, delimiter="\t")}


def main(argv: Sequence[str]) -> int:
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE.parents[1] / "Textures"
    only = tuple(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else ()
    modules = tuple(argv[argv.index("--module") + 1].split(",")) if "--module" in argv else ()
    sizes = catalog_sizes(HERE.parents[1] / "catalog.tsv")
    out.mkdir(parents=True, exist_ok=True)
    errors, written = 0, 0
    owner: dict[str, str] = {}
    for module_name, module in drawing_modules(modules).items():
        for name, draw in module.items():
            if name in owner:
                print(f"error: {name} is drawn by both {owner[name]} and {module_name}")
                errors += 1
                continue
            owner[name] = module_name
            if only and not any(o in name for o in only):
                continue
            if name not in sizes:
                print(f"error: {name} is not in catalog.tsv")
                errors += 1
                continue
            image = draw()
            if image.size != sizes[name]:
                print(f"error: {name} is {image.width}x{image.height}, the game's is {sizes[name][0]}x{sizes[name][1]}")
                errors += 1
                continue
            image.save(out / name, optimize=True)
            written += 1
    print(f"{written} picture(s) written to {out}" + (f", {errors} error(s)" if errors else ""))
    if not only and not modules:
        print(f"the pack covers {len(owner)} of the catalog's {len(sizes)} pictures")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
