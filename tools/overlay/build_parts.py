"""Builds the parts library: PNGs, parts.json and the contact sheets, all from code.

    python tools/overlay/build_parts.py [--out tools/overlay/parts] [--only hats|garments|marks]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sheets  # noqa: E402
from partdef import Part, write_library  # noqa: E402


def hat_sheets(parts: list[Part], out: Path) -> None:
    hw, cw, ch, ax, ay = 46, 130, 130, 65, 62
    # pair back+front layers of the same style/colour/size into one cell
    groups: dict[str, list[Part]] = {}
    for p in parts:
        if p.size != "M":
            continue
        key = p.id.replace("hood_back", "hood").replace("hood_front", "hood").replace("veil_back_", "veil_").replace("sallet_tail", "sallet")
        groups.setdefault(key, []).append(p)
    cells = [(sheets.pair_back_front(g, hw, cw, ch, ax, ay), name) for name, g in groups.items()]
    sheets.sheet(cells, 9).save(out / "hats_sheet.png")
    # the three sizes of a few styles
    sel = [("coif_linen", "linen"), ("felt_brown_leather", ""), ("kettle_iron", ""), ("guildcap_wine", ""), ("toque_linen", ""), ("hood_wine", "")]
    cells2 = []
    for sz, h2 in (("S", 40), ("M", 46), ("L", 52)):
        for stem, _ in sel:
            g = [p for p in parts if p.size == sz and (p.id.startswith(stem + "_") or p.id.replace("_back", "").replace("_front", "").startswith(stem + "_"))]
            if g:
                cells2.append((sheets.pair_back_front(g, h2, cw, ch, ax, ay), f"{stem} {sz}"))
    sheets.sheet(cells2, 6).save(out / "hats_sizes_sheet.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "parts")
    ap.add_argument("--only", default="hats,garments,marks")
    a = ap.parse_args()
    out: Path = a.out
    out.mkdir(parents=True, exist_ok=True)
    only = a.only.split(",")
    parts: list[Part] = []
    mods = {}
    if "hats" in only:
        import hats
        mods["hats"] = hats.build()
    if "garments" in only:
        import garments
        mods["garments"] = garments.build()
    if "marks" in only:
        import marks
        mods["marks"] = marks.build()
    for v in mods.values():
        parts += v
    write_library(parts, out)
    if "hats" in mods:
        hat_sheets(mods["hats"], out)
    if "garments" in mods:
        import garments
        garments.sheet(mods["garments"], out)
    if "marks" in mods:
        import marks
        marks.sheet(mods["marks"], out)
    for k, v in mods.items():
        print(k, len(v))


if __name__ == "__main__":
    main()
