"""The scavenger strips and the sample portrait: busts drawn by `people_figure.render` from looks of our own (a role of
foragers, wanderers and the odd marked stranger), laid out in the 288x211 frames of the game's strips."""

from __future__ import annotations

from PIL import Image

from people_cast import BRASS, Role, outfit, person, man
from people_figure import render
from people_kit import H, W

SCAV = Role(
    [outfit("jerkin", "#5a4a38", "#8a7f68"), outfit("laced", "#4a5a44", "#6a4a32"), outfit("cloak", "#4a4038", "#6a6660"),
     outfit("jerkin", "#3e4a38", "#7a766c"), outfit("laced", "#6a4a3a", "#8a7f68"), outfit("mail", "#4a3a30")],
    ("hood", "kerchief", "headband", "straw", ""), ("#4a4038", "#7a272b", "#3a4a3a", "#c8a85a", "#5a4a38"),
    (("pack",), ("pack", "scarf"), ("strap", "scar"), ("goggles_up", "scarf"), ("pack", "strap")),
    beard_share=0.5, ages=(0, 1, 1, 2, 2))

SPECIAL = Role(
    [outfit("cloak", "#3a2e46", "#6a4a7a"), outfit("robe", "#d4cab0", "#7a272b"), outfit("doublet", "#2a3f60", "#4a6e98"),
     outfit("coat", "#26303f", "#d4cab0", BRASS), outfit("gown", "#5a2e6a", "#7a4a8a"), outfit("habit", "#2c2024")],
    ("hood", "wide", "beret", "", "skull"), ("#3a2e46", "#7a272b", "#2a3f60", "", "#2c2024"),
    (("pendant",), ("chain", "pendant"), ("scar",), ("glasses",), ("fur", "pendant")),
    beard_share=0.4, ages=(0, 1, 2, 3))


def strip(width: int, height: int, role: Role, genders: list[bool], base: int) -> Image.Image:
    """Frames of 288x211 filled row by row, one person per entry of `genders` (True: a woman)."""
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cols = width // W
    for i, female in enumerate(genders):
        out.alpha_composite(render(person(role, female, base + i)), ((i % cols) * W, (i // cols) * H))
    return out


def scav_female() -> Image.Image:
    return strip(2880, 422, SCAV, [True] * 14, 4100)


def scav_male() -> Image.Image:
    return strip(576, 211, SCAV, [False] * 2, 4200)


def special() -> Image.Image:
    return strip(2304, 211, SPECIAL, [False, True, False, True, True, False, False, True], 4300)


def sample() -> Image.Image:
    """The portrait used to show how a face is cut up: a goggled smith's apprentice, cropped to 211 px wide."""
    look = man(skin=2, hair="short", hair_col="dark", beard="stubble", age=1, outfit="laced", main="#8a6a4a", second="#6a4a32",
               extras=("goggles_up", "strap"), mood="smile", seed=77)
    return render(look).crop((W // 2 - 105, 0, W // 2 + 106, H))
