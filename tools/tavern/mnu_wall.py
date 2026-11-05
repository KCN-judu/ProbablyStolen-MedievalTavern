"""wall.640x360.png: the title picture redrawn as the undercroft of a guild hall, where rebels meet at dusk."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

import mnu_wall_art as art
import mnu_wall_bg as bg
import mnu_wall_fig as fig


def wall() -> Image.Image:
    b = bg.Backdrop()
    b.ashlar(0, bg.SILL_Y, 11, 0.40)
    b.ashlar(bg.SILL_Y, 297, 14, 0.5, 0.35)
    b.plaster()
    b.peel()
    b.stains()
    b.colour_wall()
    b.ceiling()
    b.oculus(bg.OCULUS_1, False)
    b.oculus(bg.OCULUS_2, True)
    b.beam_h(31, 47, 3)
    b.lintel(53, 64)
    b.windows()
    b.slits()
    b.brace()
    art.draw_all(b.c)
    bg.floor(b)
    fig.lantern(b.c)
    bg.reflect(b)
    fig.cask(b.c, 586, 332, 22, 40, 5)
    fig.cask(b.c, 622, 348, 26, 52, 6)
    fig.puddle(b.c)
    fig.flagon(b.c)
    fig.bottle(b.c)
    fig.candle_grate(b.c)
    fig.rebel_coat(b.c)
    fig.rebel_antler(b.c)
    fig.beggar(b.c)
    return b.c.img.convert("RGBA")


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"wall.640x360.png": wall}
