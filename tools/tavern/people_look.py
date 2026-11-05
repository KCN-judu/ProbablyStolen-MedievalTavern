"""The description of one person: everything the figure generator needs to draw a bust, as plain data.

A `Look` is a frozen record. Colours are '#rrggbb' strings (turned into tone ramps when drawn), so a cast list reads as
a list of descriptions rather than code. Fields that are empty fall back to something sensible: a beard takes the hair's
colour, an outfit's second colour the main one.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Look:
    """One bust: the head (shape, skin, hair, beard, mood), the outfit (garment and colours), headwear and extras."""

    male: bool = True
    skin: int = 0                   # index into people_kit.SKINS
    w: int = 50                     # face width, even
    h: int = 64                     # face height, from the crown to the chin
    jaw: float = 0.78               # the chin's width as a share of the face's
    age: int = 0                    # 0 young, 1 adult, 2 weathered, 3 old
    hair: str = "short"             # a style of people_hair.HAIR_STYLES
    hair_col: str = "brown"         # a key of people_kit.HAIRS
    beard: str = "none"             # none, stubble, short, full, long, goatee, mustache
    beard_col: str = ""             # empty: the hair's
    eyes: str = "#4a3a2a"           # iris colour
    mood: str = "calm"              # calm, smile, stern, sad, grin, worried
    top: int = 60                   # the crown of the head
    sw: int = 72                    # half the width of the shoulders
    neck: int = 9                   # half the width of the neck
    outfit: str = "tunic"           # a garment of people_body.GARMENTS
    main: str = "#6a4a32"
    second: str = ""
    trim: str = "#c0a050"
    headwear: str = ""              # a piece of people_hair.HEADWEAR, or empty
    head_col: str = ""              # empty: the outfit's main colour
    face: str = ""                  # '', veil (cloth over the mouth), plague (bird mask), shade (face in a hood's dark)
    extras: tuple[str, ...] = ()    # props and marks: glasses, eyepatch, scar, pack, pauldron, scarf, ...
    brow: int = 1                   # 0 thin, 1 normal, 2 heavy
    nose: int = 1                   # 0 small, 1 straight, 2 big or hooked
    lips: int = 1                   # 0 thin, 1 normal, 2 full
    build: int = 1                  # 0 slight, 1 average, 2 stout (a wider neck and shoulders)
    seed: int = 0
