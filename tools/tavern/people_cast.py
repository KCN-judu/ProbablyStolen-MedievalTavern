"""The cast: the named characters, each dressed as the medieval equivalent of their role, and the generic townsfolk.

The named busts are hand-written `Look`s (one line of description each). The generic strips come from `crowd`: a role
(an outfit with a few colour and headwear choices) and a seed give any number of distinct people of one gender, so a
strip keeps its frame count while every frame is someone else. Everything is seeded; two builds draw the same faces.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Final

from people_look import Look

# ---------------------------------------------------------------------------------------------- named characters

WINE: Final = "#8a2a2e"
BRASS: Final = "#d0a847"
STEEL: Final = "#c8c8d0"


def lady(**kw: object) -> Look:
    """A woman's build: narrower face, jaw and shoulders, a slim neck."""
    base: dict[str, object] = dict(male=False, w=46, h=62, jaw=0.68, sw=62, neck=7)
    base.update(kw)
    return Look(**base)  # type: ignore[arg-type]


def man(**kw: object) -> Look:
    """A man's build (the Look defaults), with fields overridden."""
    return Look(**kw)  # type: ignore[arg-type]


NAMED: Final[Mapping[str, Look]] = {
    "Courrier": man(skin=3, hair="crop", hair_col="dark", beard="stubble", age=1, outfit="jerkin", main="#6a4a32", second="#8a7f68",
                    headwear="flat", head_col="#5a4a38", extras=("strap", "satchel"), eyes="#4a3a2a", seed=1),
    "Georgio": man(skin=1, w=52, h=66, hair="ring", hair_col="white", beard="mustache", age=3, outfit="tunic", main="#8a2e26",
                   extras=("pendant", "pack"), mood="stern", seed=2),
    "Mentor": man(skin=6, hair="bald", outfit="habit", main="#2c2024", headwear="hood", face="shade", seed=3),
    "Nellis": lady(skin=5, w=45, hair="frizz", hair_col="grey", age=3, outfit="apron", main="#d4cab0", second="#b8602a",
                   extras=("pendant",), mood="smile", sw=64, seed=4),
    "Serpico": man(skin=1, hair="short", hair_col="black", outfit="tabard", main=WINE, second="#4a4a52", trim=BRASS,
                   headwear="cap", head_col="#9a2a30", mood="stern", seed=5),
    "case_enjoyer": man(skin=0, hair="short", hair_col="ginger", beard="goatee", beard_col="chestnut", age=1, outfit="doublet",
                        main="#6a2a44", second="#8a3a58", trim=BRASS, extras=("glasses", "gold", "chain"), mood="smile", seed=6),
    "eleanor1": lady(skin=0, hair="long", hair_col="ginger", outfit="gown", main="#5a2e6a", trim=BRASS, extras=("fur", "pendant"),
                     second="#7a4a8a", mood="smile", seed=7),
    "eleanor2": lady(skin=0, hair="long", hair_col="ginger", outfit="gown", main="#5a2e6a", trim=BRASS, extras=("fur", "pendant"),
                     second="#7a4a8a", mood="calm", seed=7),
    "eleanor3": lady(skin=0, hair="long", hair_col="ginger", outfit="gown", main="#5a2e6a", trim=BRASS, extras=("fur", "pendant"),
                     second="#7a4a8a", mood="worried", seed=7),
    "eleanor_rev": lady(skin=0, hair="long", hair_col="ginger", outfit="laced", main="#3e5e38", mood="stern", seed=8),
    "eleanor_scav": lady(skin=0, hair="long", hair_col="ginger", outfit="jerkin", main="#5a4a38", second="#8a7f68",
                         extras=("cudgel", "bandage"), mood="stern", seed=9),
    "femGenericsDec3": lady(skin=2, hair="bob", hair_col="black", outfit="cloak", main="#2a2226", second="#4a3a30", face="veil",
                            seed=10),
    "grandpa_cheng": man(skin=2, hair="short", hair_col="white", age=3, outfit="robe", main="#6a5a4a", second="#d4cab0",
                         mood="smile", w=48, jaw=0.7, seed=11),
    "jackson": man(skin=5, hair="bald", beard="stubble", hair_col="black", age=2, outfit="jerkin", main="#3e5e38", second="#b8602a",
                   extras=("goggles", "soot"), seed=12),
    "landlord": man(skin=7, hair="bald", age=2, outfit="coat", main="#26303f", second="#d4cab0", trim="#2f6a66",
                    extras=("stripes", "chain"), mood="stern", w=52, seed=13),
    "lou_sec": lady(skin=0, hair="long", hair_col="straw", outfit="tabard", main=WINE, second="#4a4a52", trim=BRASS,
                    headwear="cap", head_col="#9a2a30", seed=14),
    "lun": man(skin=4, hair="short", hair_col="black", beard="short", outfit="tabard", main=WINE, second="#4a4a52", trim=BRASS,
               headwear="cap", head_col="#9a2a30", extras=("scar",), mood="stern", seed=15),
    "maleScav1": man(skin=3, beard="short", hair_col="dark", outfit="jerkin", main="#2f4c70", second="#8a7f68", headwear="lamp",
                     head_col="#4c4b55", extras=("pack",), seed=16),
    "maleScav10": man(skin=3, outfit="habit", main="#2a2226", headwear="hood", face="veil", second="#3a3038", seed=17),
    "maleScav11": man(skin=1, hair="short", hair_col="chestnut", outfit="laced", main="#7a766c", extras=("pack",), seed=18),
    "maleScav2": man(skin=0, hair="short", hair_col="blond", outfit="tunic", main="#c2561a", headwear="straw", head_col="#d8b040",
                     extras=("pack",), seed=19),
    "maleScav3": man(skin=0, hair="swept", hair_col="ginger", beard="stubble", outfit="jerkin", main="#3a3036", second="#6a5a6a",
                     extras=("strap",), seed=20),
    "maleScav4": man(skin=3, hair="long", hair_col="dark", beard="stubble", outfit="jerkin", main="#5a6a5a", second="#6a4a32",
                     extras=("pack",), seed=21),
    "maleScav5": man(skin=2, hair="short", hair_col="black", beard="stubble", outfit="laced", main="#4a5a44", second="#8a3a2a",
                     headwear="headband", head_col="#3a4a3a", extras=("goggles_up", "scarf"), seed=22),
    "maleScav6": man(skin=5, hair="crop", hair_col="black", beard="short", outfit="jerkin", main="#8a6a4a", second="#4a4448",
                     extras=("scarf", "pack"), seed=23),
    "maleScav7": man(skin=2, outfit="cloak", main="#3a3238", headwear="hood", head_col="#4a2e5a", face="plague", seed=24),
    "maleScav8": man(skin=2, hair="short", hair_col="dark", beard="full", outfit="jerkin", main="#5a4a40", second="#8a7f68",
                     headwear="headband", head_col="#7a272b", extras=("scar", "strap"), seed=25),
    "maleScav9": man(skin=2, hair="swept", hair_col="black", beard="mustache", outfit="laced", main="#2f5a5a", second="#8a2a2a",
                     extras=("scarf", "pack"), seed=26),
    "odin": man(skin=0, w=54, h=66, jaw=0.84, hair_col="ginger", beard="full", outfit="mail", main="#4a3a30", sw=78, headwear="cap",
                head_col="#3e5e38", extras=("pauldron", "iron"), mood="stern", seed=27),
    "sawyer": man(skin=1, hair="short", hair_col="brown", beard="full", outfit="laced", main="#5e8250", headwear="cap",
                  head_col="#9a2a30", extras=("flour",), seed=28),
    "serpico_rev": man(skin=1, hair="short", hair_col="black", outfit="jerkin", main="#2e2a2e", second="#3e5e38", seed=29),
    "serpico_scav": man(skin=2, hair="long", hair_col="dark", outfit="cloak", main="#6a6660", second="#4a4448", headwear="hood",
                        head_col="#6a6660", extras=("scarf", "strap"), seed=30),
    "trailer_rev1": man(skin=3, hair="crop", hair_col="black", beard="short", outfit="mail", main="#4a3a30",
                        extras=("pauldron",), mood="stern", seed=31),
    "trailer_scav1": lady(skin=4, hair="ponytail", hair_col="black", outfit="gown", main="#4a3a30", trim="#8a6a4a", sw=62, seed=32),
    "waffle_enjoyer": man(skin=0, hair="bald", hair_col="ginger", beard="full", outfit="habit", main="#2f5a88", headwear="hood",
                          extras=("flour",), seed=33),
    "wanted1": man(skin=0, hair="bald", age=2, outfit="coat", main="#26222a", second="#4a4448", extras=("eyepatch", "scar"),
                   mood="stern", seed=34),
    "wanted2": man(skin=1, w=54, h=64, hair="bald", outfit="apron", main="#d4cab0", second="#a89470", headwear="cap",
                   head_col="#9a2a30", extras=("blood",), sw=76, seed=35),
    "wanted3": man(skin=6, hair="bald", beard="stubble", outfit="mail", main="#3e3a38", headwear="cap", head_col="#3e5e38",
                   extras=("pauldron",), seed=36),
    "wanted5": lady(skin=7, hair="long", hair_col="straw", outfit="gown", main="#2a2226", trim="#8a8a92", seed=37),
    "wanted6": man(skin=2, hair="short", hair_col="black", outfit="robe", main="#d4cab0", second="#3a6a74", mood="smile", seed=38),
    "wanted7": man(skin=2, hair="short", hair_col="black", beard="mustache", outfit="apron", main="#2f4c70", second="#b3a88c",
                   headwear="flat", head_col="#2f4c70", seed=39),
    "wanted8": man(skin=7, hair="bald", age=1, outfit="laced", main="#c9bea0", extras=("pendant", "soot"), seed=40),
    "wanted9": man(skin=3, hair="short", hair_col="dark", beard="full", outfit="tabard", main=WINE, second="#4a4a52", trim=BRASS,
                   headwear="cap", head_col="#9a2a30", extras=("pauldron",), mood="stern", seed=41),
    "wild": man(skin=1, hair="short", hair_col="straw", outfit="motley", main="#b02a30", second="#2e6a3a", trim="#e0b84a",
                headwear="jester", head_col="#b02a30", mood="grin", seed=42),
}


# ---------------------------------------------------------------------------------------------- generic townsfolk


@dataclass(frozen=True)
class Role:
    """A kind of townsperson: garments with their colour choices, headwear choices and props."""

    outfits: Sequence[Mapping[str, object]]
    headwear: Sequence[str] = ("",)
    head_cols: Sequence[str] = ("",)
    extras: Sequence[tuple[str, ...]] = ((),)
    male_hair: Sequence[str] = ("crop", "short", "swept", "receding", "curly", "mop", "bald")
    female_hair: Sequence[str] = ("long", "bob", "bun", "ponytail", "braid", "curly", "mop")
    beard_share: float = 0.4
    hooded: bool = False
    ages: Sequence[int] = (0, 1, 1, 2)
    colours: Mapping[str, object] = field(default_factory=dict)


def outfit(garment: str, main: str, second: str = "", trim: str = BRASS) -> dict[str, object]:
    """One entry of a role's wardrobe."""
    return {"outfit": garment, "main": main, "second": second, "trim": trim}


ROLES: Final[Mapping[str, Role]] = {
    "sec": Role([outfit("tabard", WINE, "#4a4a52"), outfit("tabard", "#9a2a30", "#5a5660"), outfit("tabard", "#7a2428", "#3a3a44")],
                ("helm", "cap", "helm", "coif"), ("#9a2a30", "#8a2428", "#a83234", "#d4cab0"), (("pauldron",), (), ("pauldron", "iron"), ("iron",)), beard_share=0.45),
    "sec_corpo": Role([outfit("tabard", "#2a3f60", "#4a4a52", STEEL), outfit("tabard", "#33486a", "#3a3a44", STEEL)],
                      ("helm", "helm", "coif"), ("#4c4b55", "#3e3d48", "#d4cab0"), (("pauldron", "iron"), ("pauldron",), ("iron",)), beard_share=0.3),
    "sec_off": Role([outfit("tabard", "#5a1a26", "#4a4a52", "#e0c060"), outfit("tabard", "#6a2030", "#5a5660", "#e0c060")],
                    ("beret", "wide", "cap"), ("#7a1a28", "#5a1a26", "#8a2030"), (("chain", "pauldron"), ("pauldron", "chain")), beard_share=0.5),
    "merc": Role([outfit("mail", "#4a3a30"), outfit("mail", "#5a4a3a"), outfit("jerkin", "#4a3a30", "#6a5a50")],
                 ("helm", "skull", "", "kerchief"), ("#4c4b55", "#4a3a30", "#6a2a2a"), (("pauldron",), ("pauldron", "iron"), ("scar",), ("strap",)),
                 beard_share=0.55, ages=(0, 1, 2, 2)),
    "chef": Role([outfit("apron", "#d9cfb4", "#8a2a2e"), outfit("apron", "#8a2a2e", "#d4cab0"), outfit("apron", "#cfc4a6", "#3e5e38"), outfit("apron", "#5a3a2a", "#d4cab0")],
                 ("toque", "coif", "kerchief", "skull", "toque"), ("#e0d8c0", "#d4cab0", "#8a2a2e", "#e0d8c0"), (("flour",), ("flour", "soot"), ()), beard_share=0.35),
    "eng": Role([outfit("apron", "#6a4a2a", "#b3a88c"), outfit("apron", "#5a3a22", "#3e5e38"), outfit("apron", "#4a4a52", "#8a2a2e"), outfit("apron", "#7a5a32", "#d4cab0")],
                ("", "headband", "flat", "kerchief", "skull"), ("#8a2a2a", "#4a4a52", "#6a5a44", "#3e5e38"), (("soot",), ("goggles_up", "soot"), ("soot", "scar"), ()), beard_share=0.5),
    "farmer": Role([outfit("laced", "#7a6a48", "#8a7f68"), outfit("laced", "#6a7a4a"), outfit("laced", "#8a6a4a"), outfit("laced", "#7a766c")],
                   ("straw", "kerchief", "", "cap", "straw", "skull"), ("#c8a85a", "#8a3a2a", "", "#6a5a44", "#d8b868", "#d4cab0"), ((), ("flour",), ("pack",)), beard_share=0.4),
    "lower": Role([outfit("laced", "#6a5a48"), outfit("tunic", "#5a5a52"), outfit("laced", "#7a6a58"), outfit("tunic", "#6a4a3a"),
                   outfit("laced", "#4a5a5a"), outfit("tunic", "#7a5a3a"), outfit("jerkin", "#6a4a32", "#8a7f68")],
                  ("", "", "flat", "kerchief", "skull"), ("#6a5a44", "#7a766c", "#8a4a3a", "#5a4a38"), ((), (), ("scarf",), ("pack",)), beard_share=0.4, ages=(0, 1, 2, 3)),
    "med": Role([outfit("robe", "#d4cab0", "#3e6a58"), outfit("robe", "#cfc8b0", "#3a6a74")],
                ("skull", "coif", "bonnet", "kerchief"), ("#3e6a58", "#d4cab0", "#d4cab0", "#3a6a74"), (("pendant",), ("glasses",), ()), beard_share=0.3),
    "sci": Role([outfit("robe", "#cfc8b0", "#4a5a7a"), outfit("robe", "#d4cab0", "#6a5a4a")],
                ("skull", "", "flat", "beret"), ("#4a5a7a", "#2a3f60", "#4a3a30", "#3e5e38"), (("glasses",), ("glasses", "gold"), ("pendant",)), beard_share=0.3),
    "upper": Role([outfit("doublet", "#7a2a44", "#a05a70"), outfit("doublet", "#2a3f60", "#4a6e98"), outfit("coat", "#2c3a2c", "#d4cab0", "#c0a050"),
                   outfit("doublet", "#5a2e6a", "#7a4a8a"), outfit("coat", "#6a2a2a", "#d4cab0", "#c0a050"), outfit("doublet", "#2e5a44", "#5e8250"),
                   outfit("robe", "#5a1a26", "#d4cab0", "#c0a050"), outfit("tunic", "#2e5a44", "#c0a050"), outfit("coat", "#2a3f60", "#d4cab0", "#c0a050"),
                   outfit("robe", "#2c3a2c", "#8a2a2e", "#c0a050")],
                  ("", "flat", "wide", "beret", ""), ("#2a3f60", "#5a1a26", "#2e5a44", "#26222a"), (("chain",), ("pendant",), ("fur",), ("chain", "fur"), ("glasses", "gold")),
                  beard_share=0.4, ages=(0, 1, 1, 2, 3)),
    "rev": Role([outfit("jerkin", "#3e5e38", "#6a5a48"), outfit("laced", "#4a6a40"), outfit("jerkin", "#2f4a30", "#7a766c")],
                ("headband", "kerchief", "hood", "cap", ""), ("#3e5e38", "#2f4a30", "#3e5e38", "#7a272b"), (("strap",), ("pack",), ("strap", "scar")), beard_share=0.45),
    "bm": Role([outfit("cloak", "#2a2226", "#3a3038"), outfit("habit", "#26222a"), outfit("cloak", "#33292e", "#241e22"), outfit("cloak", "#3a2a4a", "#2a2226"),
                outfit("habit", "#2a3a34"), outfit("cloak", "#4a3228", "#26222a"), outfit("habit", "#3a2a2e", "#5a4a3a"), outfit("cloak", "#26303f", "#33292e")],
               ("hood", "hood", "hood"), ("#2a2226", "#26222a", "#33292e"), ((), ("scar",)), beard_share=0.3, hooded=True),
}

# role -> (role key, women?) for each strip file stem
STRIPS: Final[Mapping[str, tuple[str, bool]]] = {
    "femaleBM": ("bm", True), "maleBM": ("bm", False), "femaleChef": ("chef", True), "maleChef": ("chef", False),
    "femaleEng": ("eng", True), "maleEng": ("eng", False), "femaleFarmer": ("farmer", True), "maleFarmer": ("farmer", False),
    "femaleLower": ("lower", True), "maleLower": ("lower", False), "femaleMed": ("med", True), "maleMed": ("med", False),
    "femaleMerc": ("merc", True), "maleMerc": ("merc", False), "femaleRev": ("rev", True), "maleRev": ("rev", False),
    "femaleSci": ("sci", True), "maleSci": ("sci", False), "femaleSec": ("sec", True), "maleSec": ("sec", False),
    "femaleSecCorpo": ("sec_corpo", True), "maleSecCorpo": ("sec_corpo", False), "femaleSecOff": ("sec_off", True),
    "maleSecOff": ("sec_off", False), "femaleUpper": ("upper", True), "maleUpper": ("upper", False),
}

SKIN_WEIGHTS: Final = (0,) * 2 + (1,) * 3 + (2,) * 3 + (3,) * 3 + (4,) * 2 + (5,) * 2 + (6,) + (7,)
EYES: Final = ("#4a3a2a", "#3a4a5a", "#4a5a3a", "#2a2226", "#6a4a2a", "#5a6a7a")
MOODS: Final = ("calm", "calm", "smile", "stern", "sad", "worried")


def hair_colour(rng: random.Random, skin: int, age: int) -> str:
    """A hair colour that suits the skin and age: dark for deep skin, grey for the old."""
    if age >= 3 and rng.random() < 0.8:
        return rng.choice(("grey", "white"))
    if skin >= 5:
        return rng.choice(("black", "black", "dark"))
    if skin >= 3:
        return rng.choice(("black", "dark", "dark", "brown"))
    return rng.choice(("black", "dark", "brown", "brown", "chestnut", "ginger", "blond", "straw", "auburn"))


def person(role: Role, female: bool, seed: int) -> Look:
    """One generic person of `role`: a seeded draw of build, face, hair, beard, wardrobe and headwear."""
    rng = random.Random(seed * 7919 + 13)
    skin = rng.choice(SKIN_WEIGHTS)
    age = rng.choice(role.ages)
    hair_style = rng.choice(role.female_hair if female else role.male_hair)
    beard = "none"
    if not female and rng.random() < role.beard_share:
        beard = rng.choice(("stubble", "short", "short", "full", "mustache", "goatee", "long"))
    if age >= 3 and hair_style in ("bun", "ponytail", "braid") and rng.random() < 0.5:
        hair_style = "frizz"
    wardrobe = dict(rng.choice(role.outfits))
    wear_i = rng.randrange(len(role.headwear))
    wear = role.headwear[wear_i]
    if female and wear in ("flat", "wide", "beret") and role is ROLES["upper"]:
        wear = ""
    if female and wear == "kerchief" and rng.random() < 0.2:
        wear = "bonnet"
    head_col = rng.choice(role.head_cols) if role.head_cols[0] else ""
    if role.hooded:
        head_col = wardrobe["main"]  # type: ignore[assignment]
    face = ""
    if role.hooded:
        face = rng.choice(("shade", "veil", "", ""))
    elif wear == "hood":
        face = rng.choice(("veil", "", ""))
        head_col = wardrobe["main"]  # type: ignore[assignment]
    body = dict(brow=rng.choice((0, 1, 1, 2)), nose=rng.choice((0, 1, 1, 2)), lips=rng.choice((0, 1, 1, 2)), build=rng.choice((0, 1, 1, 2)),
                male=not female, skin=skin, age=age, hair=hair_style,
                hair_col=hair_colour(rng, skin, age), beard=beard, eyes=rng.choice(EYES), mood=rng.choice(MOODS),
                headwear=wear, head_col=head_col, face=face, extras=rng.choice(role.extras), seed=seed)
    body.update(wardrobe)
    if female:
        body.update(w=rng.choice((44, 46, 46, 48)), h=rng.choice((60, 62, 62, 64)), jaw=rng.choice((0.64, 0.68, 0.72)),
                    sw=rng.choice((60, 62, 64)), neck=7)
        if body["outfit"] in ("doublet", "coat"):
            body["outfit"] = "gown"
    else:
        body.update(w=rng.choice((48, 50, 50, 52)), h=rng.choice((62, 64, 64, 66)), jaw=rng.choice((0.74, 0.8, 0.84)),
                    sw=rng.choice((68, 72, 72, 76)), neck=rng.choice((9, 9, 10)))
    return Look(**body)  # type: ignore[arg-type]


def crowd(file_key: str, count: int) -> list[Look]:
    """`count` distinct people for the strip file `file_key` (for example 'femaleSec.1440x211')."""
    key, female = STRIPS[file_key.split(".")[0]]
    base = sum(ord(c) * (i + 1) for i, c in enumerate(file_key)) * 31
    return [person(ROLES[key], female, base + i) for i in range(count)]
