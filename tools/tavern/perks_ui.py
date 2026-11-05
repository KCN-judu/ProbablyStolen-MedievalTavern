"""The 37 perk pictures (catalog group `new-game/perk-icons`): white glyphs the game tints, drawn as medieval emblems.

`perksui_glyphs` holds the drawings, `perksui_kit` the canvas and the placement. Every 32 pixel icon lands on the
middle of the area the game's own icon occupies; the 100 and 256 pixel ones are drawn small and scaled by whole numbers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from PIL import Image

import perksui_g32 as g
import perksui_g36 as h
from perksui_kit import Ic, bbox_of, place
from pix import Pix

# file name -> (drawing, scale of one logical pixel). Sizes come from the name.
SINGLE: Final[dict[str, tuple[Callable[[], Ic], int]]] = {
    "addiction_narcotic.32x32.png": (g.mortar, 1),
    "additionc_alcohol.32x32.png": (g.tankard, 1),
    "additionc_gambling.32x32.png": (g.die, 1),
    "additionc_nicotine.32x32.png": (g.pipe, 1),
    "alert.32x32.png": (g.bell, 1),
    "bad_lease.32x32.png": (g.torn_deed, 1),
    "blabbermouth.32x32.png": (g.horn, 1),
    "blackmail.32x32.png": (g.seal_letter, 1),
    "cassette.32x32.png": (g.lute, 1),
    "colorful.32x32.png": (g.palette, 1),
    "connected.32x32.png": (g.three_nodes, 1),
    "convict.32x32.png": (g.jail, 1),
    "diplomatic.32x32.png": (g.scroll_seal, 1),
    "illiterate.32x32.png": (g.closed_book_q, 1),
    "intimidating.32x32.png": (g.great_helm, 1),
    "lucky.36x36.png": (g.lucky_shoe, 1),
    "minimalist.32x32.png": (g.empty_crate, 1),
    "model_citizen.32x32.png": (g.rosette, 1),
    "prime_real_estate.32x32.png": (g.key, 1),
    "rev.32x32.png": (g.pitchfork, 1),
    "saving.32x32.png": (g.purse, 1),
    "sawyer_crew.32x32.png": (g.bucket_broom, 1),
    "scav.32x32.png": (g.sack, 1),
    "secret_admirer.32x32.png": (g.heart_door, 1),
    "sentinel.32x32.png": (g.skull, 1),
    "short_sleeper.32x32.png": (g.moon_z, 1),
    "side_street.32x32.png": (g.signpost, 1),
    "snitch.36x36.png": (g.whisper, 1),
    "vending.32x32.png": (g.stall, 1),
    "welfare_program.32x32.png": (g.loaves, 1),
    "working_pipes.32x32.png": (g.well, 1),
    "noun-beaker-7821176-FFFFFF.100x100.png": (h.flask, 3),
    "noun-flag-7646741-FFFFFF.100x100.png": (h.banner, 3),
    "noun-flyer-7880108-FFFFFF.100x100.png": (h.notices, 3),
    "stopwatch.100x100.png": (h.hourglass, 3),
    "noun-people-6240743-FFFFFF.256x256.png": (h.folk_trio, 2),
}

# The sheet of 23 cells of 36 pixels: (drawing, x0 y0 x1 y1 of the occupied area of the game's cell).
SHEET: Final[tuple[tuple[Callable[[], Ic], tuple[int, int, int, int]], ...]] = (
    (h.cottage_person, (7, 7, 29, 28)), (h.banned_leaf, (5, 5, 31, 31)), (h.thumb_down, (9, 11, 27, 28)),
    (h.broken_heart, (8, 9, 29, 28)), (h.toolbox, (6, 7, 32, 29)), (h.hammer_tongs, (7, 8, 29, 28)),
    (h.three_folk, (3, 8, 33, 29)), (h.crutch, (5, 5, 30, 30)), (h.herb_basket, (4, 6, 31, 30)),
    (h.midden, (5, 7, 31, 30)), (h.strongbox, (5, 10, 31, 26)), (h.crossbow, (8, 4, 27, 31)),
    (h.dotted_barrel, (9, 10, 27, 28)), (h.dotted_shield, (9, 9, 27, 27)), (h.cottage_chimney, (8, 9, 28, 27)),
    (h.satchel_down, (5, 8, 29, 29)), (h.satchel_up, (7, 8, 32, 30)), (h.hat, (7, 9, 30, 27)),
    (h.boot_mud, (4, 2, 31, 26)), (h.boot_coin, (4, 2, 31, 26)), (h.shoes_coin, (7, 6, 34, 29)),
    (h.shoes_leaf, (5, 6, 34, 29)), (h.boot_spur, (3, 2, 34, 29)),
)


def _size(name: str) -> tuple[int, int]:
    w, h = name.rsplit(".", 2)[1].split("x")
    return int(w), int(h)


def _single(name: str, make: Callable[[], Ic], k: int) -> Callable[[], Image.Image]:
    def draw() -> Image.Image:
        p = Pix(*_size(name))
        place(p, make(), bbox_of(name), k)
        return p.im
    return draw


def _sheet() -> Image.Image:
    p = Pix(36 * len(SHEET), 36)
    for i, (make, box) in enumerate(SHEET):
        place(p, make(), box, 1, (36 * i, 0))
    return p.im


ASSETS: dict[str, Callable[[], Image.Image]] = {n: _single(n, f, k) for n, (f, k) in SINGLE.items()}
ASSETS["2perkSet2.828x36.png"] = _sheet
