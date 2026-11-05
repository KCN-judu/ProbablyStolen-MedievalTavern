"""The colours of the tavern: one palette for every picture, so a hundred drawings read as one place.

Each material is a ramp of five or four tones from dark to light. Light comes from the upper left, from a lantern and a
hearth: shadows are warm and deep (a brown that is nearly violet), never black, and highlights are amber, never white.
"""

from __future__ import annotations

from typing import Final

from pix import Color, Ramp, rgb

# Timber. WOOD is boards and furniture, OAK is the heavy beams and the bar.
WOOD: Final[Ramp] = (rgb("#24150f"), rgb("#3d2415"), rgb("#5a371d"), rgb("#7a4e2a"), rgb("#9c6b3a"))
OAK: Final[Ramp] = (rgb("#1a0f0a"), rgb("#2c1a10"), rgb("#41271a"), rgb("#573624"), rgb("#6d4630"))
PALE_WOOD: Final[Ramp] = (rgb("#4a3220"), rgb("#6b4a2e"), rgb("#8c6840"), rgb("#ad8856"), rgb("#caa76c"))

# Iron and brass.
IRON: Final[Ramp] = (rgb("#141318"), rgb("#26252c"), rgb("#3b3a43"), rgb("#575660"), rgb("#7a7983"))
BRASS: Final[Ramp] = (rgb("#3a2a12"), rgb("#6b4c1c"), rgb("#a07a2c"), rgb("#d0a847"), rgb("#f0d27a"))

# Masonry and plaster.
STONE: Final[Ramp] = (rgb("#2b2725"), rgb("#403b37"), rgb("#57514b"), rgb("#6f685f"), rgb("#8a8277"))
PLASTER: Final[Ramp] = (rgb("#4a3f33"), rgb("#6a5a45"), rgb("#8a7758"), rgb("#a89470"), rgb("#c2ae88"))
SOOT: Final[Ramp] = (rgb("#120d0d"), rgb("#1d1514"), rgb("#2a1f1c"), rgb("#3a2c27"))

# Light: lantern, candle, hearth and embers.
FLAME: Final[Ramp] = (rgb("#7a2c10"), rgb("#c2561a"), rgb("#f0953a"), rgb("#ffcf70"), rgb("#fff0b8"))
EMBER: Final[Color] = rgb("#b2402a")

# Paper and cloth.
PARCHMENT: Final[Ramp] = (rgb("#6b5a36"), rgb("#9a8450"), rgb("#c4ad78"), rgb("#e0cf9f"), rgb("#f0e3bb"))
WINE: Final[Ramp] = (rgb("#2e0f14"), rgb("#521a20"), rgb("#7a272b"), rgb("#a13a38"), rgb("#c25b49"))
MOSS: Final[Ramp] = (rgb("#16231a"), rgb("#27402a"), rgb("#3e5e38"), rgb("#5e8250"))
NAVY: Final[Ramp] = (rgb("#10192a"), rgb("#1d3049"), rgb("#2f4c70"), rgb("#4a6e98"))
LEATHER: Final[Ramp] = (rgb("#2a170f"), rgb("#4a2b1a"), rgb("#6e4326"), rgb("#935e36"))
LINEN: Final[Ramp] = (rgb("#5d5444"), rgb("#8a7f68"), rgb("#b3a88c"), rgb("#d4cab0"))

# Glass and night.
GLASS: Final[Ramp] = (rgb("#0f1a22"), rgb("#1c3140"), rgb("#2f5266"), rgb("#4f7c8c"), rgb("#8ab0b8"))
NIGHT: Final[Ramp] = (rgb("#0a0a14"), rgb("#12142a"), rgb("#1c2040"), rgb("#2a3158"), rgb("#3f4a78"))

SHADOW: Final[Color] = rgb("#170f12")       # the deepest tone: used for outlines and the dark under things
