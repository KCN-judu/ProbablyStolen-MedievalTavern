"""Role -> medieval outfit. A recipe picks cloth ramps, headgear, garment overlays and make-up from the parts library.

Choices are deterministic (seeded from file name and frame index) and avoid repeating the previous frame's choice
for the same slot, so neighbouring people differ.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

from landmarks import Landmarks
from library import Library, PartRec

STYLE_Z = {
    "cloak_back": -30, "hood_back": -29, "veil_back": -28, "sallet_tail": -27,
    "scar": 10, "soot": 10, "dirt": 10, "rouge": 10, "lips": 10, "freckles": 10, "stubble": 11, "tired": 9, "moustache": 12, "warpaint": 12,
    "tattoo": 12, "bandage": 13, "bruise": 10,
    "quilt": 18, "ink": 19, "tabard": 20, "brigandine": 20, "gambeson": 20, "apron": 21, "patch": 22, "studs": 22, "buttons": 23, "laces": 23, "belt": 24, "badge_shield": 25,
    "badge_cross": 25, "badge_disc": 25, "bandolier": 26, "straps_pair": 26, "sash": 27,
    "cloak_front": 30, "mantle": 31, "pauldron": 32,
    "neckline_v": 33, "collar_fold": 34, "collar_band": 34, "collar_ruff": 35, "scarf_wrap": 36, "chain_office": 37, "pendant": 38,
    "plague_beak": 44, "scarf_cover": 45, "hood_front": 50, "wimple": 51, "mail_coif": 51,
    "coif": 60, "skullcap": 60, "leather_cap": 60, "kerchief": 60, "felt_hat": 60, "wide_brim": 60, "feathered_cap": 60, "guild_cap": 60,
    "kettle_helm": 60, "sallet": 60, "toque": 60, "cook_cap": 60, "circlet": 58,
}


@dataclass
class Item:
    part: PartRec
    dx: int = 0
    dy: int = 0


@dataclass
class Outfit:
    ramps: list[str]
    items: list[Item] = field(default_factory=list)
    whole: bool = False            # the original head cloth (hood) is recoloured too
    erase_hair: bool = False
    warm: float = 0.5
    log: list[str] = field(default_factory=list)


class Ctx:
    def __init__(self, lib: Library, rng: random.Random, lm: Landmarks, sex: str, prev: dict[str, str], fcol: dict[str, str]) -> None:
        self.lib, self.rng, self.lm, self.sex, self.prev = lib, rng, lm, sex, prev
        self.fcol = fcol                       # colours shared by the whole file (watch colours...)
        self.hsz = "S" if lm.hw < 44 else ("M" if lm.hw <= 50 else "L")
        self.bsz = "S" if lm.sw < 122 else ("M" if lm.sw < 140 else "L")
        self.out = Outfit([])
        self.female = sex == "female"

    def p(self, prob: float) -> bool:
        return self.rng.random() < prob

    def choice(self, key: str, options: list):
        opts = [o for o in options if str(o) != self.prev.get(key)] or options
        c = self.rng.choice(opts)
        self.prev[key] = str(c)
        return c

    def get(self, style: str, colours: list[str] | None = None, size: str | None = "auto", contains: str | None = None,
            key: str | None = None) -> PartRec | None:
        if size == "auto":
            size = None
        cand = self.lib.find(style=style, colours=colours)
        if contains:
            cand = [c for c in cand if contains in c.id]
        sized = [c for c in cand if c.size]
        if sized:
            want = self.hsz if sized[0].cat == "hats" or style in ("scarf_cover",) else self.bsz
            if style in ("rouge", "freckles", "stubble", "tired"):
                want = self.hsz
            cand = [c for c in cand if c.size == want] or cand
        if not cand:
            return None
        k = key or style
        pick = self.choice(k, cand) if len(cand) > 1 else cand[0]
        return pick

    def add(self, part: PartRec | None, dx: int = 0, dy: int = 0) -> None:
        if part is not None:
            self.out.items.append(Item(part, dx, dy))
            self.out.log.append(part.id)

    def addg(self, style: str, colours: list[str] | None = None, dx: int = 0, dy: int = 0, contains: str | None = None, key: str | None = None) -> PartRec | None:
        part = self.get(style, colours, contains=contains, key=key)
        self.add(part, dx, dy)
        return part


# ----------------------------------------------------------------------------------------------- hats


def hat(c: Ctx, style: str, colours: list[str], **kw) -> None:
    part = c.get(style, colours, **kw)
    if part is None:
        return
    c.add(part)
    c.out.erase_hair = part.erase == "above"
    if style in ("hood_front",):
        back = c.lib.by_id.get(part.id.replace("hood_front", "hood_back"))
        c.add(back)
    elif style == "sallet":
        c.add(c.lib.by_id.get(part.id.replace("sallet_", "sallet_tail_", 1)))
    elif style == "wimple" and c.p(0.6):
        c.add(c.lib.by_id.get(part.id.replace("wimple", "veil_back")))


def marks_common(c: Ctx, dirt: float = 0.0, soot: float = 0.0, freck: float = 0.0, stub: float = 0.0, tired: float = 0.0,
                 scar: float = 0.0, rouge: float = 0.0, lips: float = 0.0, mous: float = 0.0, bruise: float = 0.0, paint: float = 0.0) -> None:
    m = not c.female
    if c.p(dirt):
        c.add(c.lib.by_id[c.choice("dirt", ["dirt_a", "dirt_b", "dirt_a_r", "dirt_b_r"])])
    if c.p(soot):
        c.add(c.lib.by_id[c.choice("soot", ["soot_cheek", "soot_nose", "soot_streak", "soot_wide"])])
    if c.p(freck):
        c.addg("freckles", key="freck")
    if m and c.p(stub):
        c.addg("stubble", ["dark", "brown", "grey"], contains=c.choice("stubd", ["light", "mid", "heavy"]), key="stub")
    if c.p(tired):
        c.addg("tired")
    if c.p(scar):
        c.add(c.lib.by_id[c.choice("scar", ["scar_cheek", "scar_cheek_r", "scar_slash", "scar_slash_r", "scar_brow", "scar_brow_r", "scar_chin"])])
    if c.female and c.p(rouge):
        c.addg("rouge", ["rose", "warm"])
    if c.female and c.p(lips):
        c.add(c.lib.by_id[c.choice("lips", ["lips_rose", "lips_wine"])])
    if m and c.p(mous):
        c.addg("moustache", ["dark", "brown", "grey", "red"], key="mous")
    if c.p(bruise):
        c.add(c.lib.by_id["bruise"])
    if c.p(paint):
        c.addg("warpaint", key="paint")


# ----------------------------------------------------------------------------------------------- roles


def r_upper(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("wine", "cream"), ("indigo", "cream"), ("plum", "linen"), ("moss", "cream"), ("teal", "cream")]))
    if c.female:
        k = c.choice("hat", ["circlet", "wimple", "feathered_cap", "kerchief", "guild_cap", "none"])
    else:
        k = c.choice("hat", ["guild_cap", "guild_cap", "feathered_cap", "felt_hat", "circlet"])
    cols = {"circlet": ["brass", "steel"], "wimple": ["linen", "cream"], "feathered_cap": ["wine", "indigo", "moss", "charcoal"],
            "kerchief": ["linen"], "guild_cap": ["wine", "indigo", "moss", "plum", "charcoal"], "felt_hat": ["charcoal", "wine", "brown"]}
    if k != "none":
        hat(c, k, cols[k])
    ck = c.choice("collar", ["collar_ruff", "collar_fold", "collar_band", "neckline_v", "collar_fold"])
    c.addg(ck, ["linen", "cream"] if ck in ("collar_ruff", "collar_fold") else None)
    if c.p(0.55):
        c.addg("chain_office")
    elif c.p(0.5):
        c.addg("pendant")
    if c.p(0.25):
        c.addg("mantle", ["wine", "indigo", "charcoal", "moss"])
    marks_common(c, rouge=0.7, lips=0.5, mous=0.3, tired=0.05)


def r_lower(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("brown", "linen"), ("grey", "linen"), ("ochre", "brown"), ("moss", "linen"), ("sand", "brown"), ("rust", "linen")]))
    if c.female:
        k = c.choice("hat", ["coif", "kerchief", "kerchief", "coif", "none"])
    else:
        k = c.choice("hat", ["skullcap", "felt_hat", "leather_cap", "wide_brim", "none", "felt_hat"])
    cols = {"coif": ["linen", "cream", "sand"], "kerchief": ["wine", "ochre", "moss", "indigo", "linen"], "skullcap": ["brown", "grey", "wine", "indigo"],
            "felt_hat": ["brown", "grey", "moss", "wine"], "leather_cap": ["leather", "brown"], "wide_brim": ["straw", "sand", "brown"]}
    if k != "none":
        hat(c, k, cols[k])
    if c.p(0.3):
        c.addg("apron", ["linen", "leather", "cream", "grey"])
    elif c.female and c.p(0.4):
        c.addg("laces", ["leather", "cream"])
    elif c.p(0.25):
        c.addg("straps_pair", ["leather", "brown"])
    if c.p(0.3):
        c.addg("patch", ["leather", "brown", "linen", "wine", "moss"])
    if c.p(0.3):
        c.addg("collar_fold", ["linen", "sand"])
    marks_common(c, dirt=0.35, freck=0.25, soot=0.12, stub=0.4, tired=0.2, rouge=0.25)


def r_bm(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("black", "charcoal"), ("charcoal", "plum"), ("plum", "black"), ("grey", "black")]))
    col = c.choice("hcol", ["charcoal", "brown", "grey"])
    if c.p(0.7):
        hat(c, "hood_front", [col])
    else:
        hat(c, "kerchief", ["indigo", "wine", "linen"])
    if c.p(0.6):
        cc = c.choice("ccol", ["charcoal", "brown", "wine", "indigo"])
        c.addg("cloak_back", [cc])
        c.addg("cloak_front", [cc])
    if c.p(0.5):
        c.addg("scarf_cover", ["charcoal", "wine", "indigo"])
    elif c.p(0.5):
        c.addg("scarf_wrap", ["charcoal", "wine", "grey"] if False else ["charcoal", "wine", "indigo"])
    if c.p(0.3):
        c.addg("pendant", contains=c.choice("pend", ["cross", "gem", "key", "moon"]))
    marks_common(c, tired=0.3, scar=0.2)


SHIELD = {"wine": "badge_shield_wine_tower", "indigo": "badge_shield_indigo_tower", "moss": "badge_shield_moss_none"}


def r_sec(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("brown", "leather"), ("sand", "brown"), ("grey", "leather")]))
    k = c.choice("hat", ["kettle_helm", "leather_cap", "kettle_helm", "mail_coif", "skullcap", "kettle_helm"])
    cols = {"kettle_helm": ["iron", "steel"], "leather_cap": ["leather", "brown"], "mail_coif": ["iron", "steel"], "skullcap": ["brown", "grey"]}
    hat(c, k, cols[k])
    wc = c.fcol.setdefault("watch", c.rng.choice(["wine", "indigo", "moss"]))
    emb = c.fcol.setdefault("emblem", c.rng.choice(["tower", "cross", "stripe", "chevron"]))
    body = c.choice("body", ["tabard", "tabard", "brigandine", "gambeson"])
    if body == "tabard":
        c.addg("tabard", [wc], contains=emb)
    elif body == "brigandine":
        c.addg("brigandine", [wc, "leather", "brown", "charcoal"])
    else:
        c.addg("gambeson", ["linen", "sand", "brown", "grey", wc])
    if body == "tabard" and c.p(0.3):
        c.add(c.lib.by_id["quilt_" + c.choice("q2", ["vertical", "diamond"])])
    if c.p(0.7):
        c.add(c.lib.by_id[SHIELD[wc]], dx=-24, dy=12)
    if c.p(0.3):
        c.addg("pauldron", ["iron", "steel", "leather"])
    marks_common(c, stub=0.35, scar=0.15, tired=0.2, bruise=0.05)


def r_secoff(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("indigo", "cream"), ("wine", "cream"), ("charcoal", "cream")]))
    k = c.choice("hat", ["guild_cap", "felt_hat", "feathered_cap", "guild_cap"])
    cols = {"guild_cap": ["wine", "indigo", "charcoal"], "felt_hat": ["charcoal", "wine"], "feathered_cap": ["wine", "indigo", "charcoal"]}
    hat(c, k, cols[k])
    wc = c.fcol.setdefault("watch", c.rng.choice(["wine", "indigo", "moss"]))
    c.addg("tabard", [wc], contains="plain")
    c.addg("collar_fold", ["linen", "cream"])
    c.addg("chain_office", contains=c.choice("chn", ["medallion", "double", "silver"]))
    if c.p(0.5):
        c.addg("sash", ["wine", "ochre", "indigo"])
    c.add(c.lib.by_id[SHIELD[wc]], dx=-26, dy=14)
    marks_common(c, mous=0.35, tired=0.15, scar=0.1)


def r_secorpo(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("charcoal", "cream"), ("indigo", "linen"), ("plum", "cream")]))
    hat(c, "guild_cap", ["charcoal", "plum", "indigo"])
    if c.p(0.4):
        c.addg("brigandine", ["charcoal", "indigo", "wine"])
    if c.p(0.5):
        c.addg("mantle", ["charcoal", "indigo", "wine"])
    c.addg("collar_band", ["indigo", "wine", "moss"])
    c.addg("chain_office", contains="silver")
    if c.p(0.6):
        c.addg("buttons", contains="brass")
    marks_common(c, mous=0.25, tired=0.1)


def r_eng(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("brown", "linen"), ("grey", "brown"), ("moss", "linen"), ("sand", "brown")]))
    k = c.choice("hat", ["leather_cap", "skullcap", "kerchief", "felt_hat", "none", "leather_cap"])
    cols = {"leather_cap": ["leather", "brown"], "skullcap": ["brown", "grey"], "kerchief": ["linen", "ochre", "wine"], "felt_hat": ["brown", "grey"]}
    if k != "none":
        hat(c, k, cols[k])
    c.addg("apron", ["leather", "leather", "brown"] if False else ["leather"])
    if c.p(0.4):
        c.addg("straps_pair", ["leather", "brown"])
    if c.p(0.3):
        c.addg("patch", ["leather", "brown", "grey"] if False else ["leather", "brown"])
    marks_common(c, soot=0.6, dirt=0.3, stub=0.3, tired=0.15)


def r_sci(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("indigo", "linen"), ("plum", "cream"), ("grey", "linen"), ("moss", "cream")]))
    k = c.choice("hat", ["coif", "skullcap", "skullcap", "guild_cap", "none"])
    cols = {"coif": ["linen", "cream"], "skullcap": ["brown", "grey", "indigo", "wine"], "guild_cap": ["indigo", "plum"]}
    if k != "none":
        hat(c, k, cols[k])
    c.addg("collar_band", ["indigo", "wine", "moss", "brown"])
    c.add(c.lib.by_id[c.choice("disc", ["badge_disc_quill", "badge_disc_flask"])], dx=-22, dy=16)
    if c.p(0.6):
        c.add(c.lib.by_id[c.choice("ink", ["ink_blot", "ink_smear"])], dx=c.rng.randint(-30, 30), dy=c.rng.randint(25, 60))
    if c.p(0.4):
        c.addg("buttons", contains="bone")
    if c.p(0.35):
        c.addg("pendant", contains=c.choice("pend", ["moon", "key", "gem"]))
    marks_common(c, tired=0.4, soot=0.1)


def r_med(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("cream", "linen"), ("linen", "cream"), ("moss", "cream")]))
    if c.female:
        k = c.choice("hat", ["wimple", "coif", "wimple", "kerchief"])
    else:
        k = c.choice("hat", ["coif", "skullcap", "hood_front", "coif"])
    cols = {"wimple": ["linen", "cream"], "coif": ["linen", "cream"], "skullcap": ["linen" if False else "grey", "brown"], "hood_front": ["grey", "moss"],
            "kerchief": ["linen"]}
    hat(c, k, cols[k])
    c.add(c.lib.by_id[c.choice("cross", ["badge_cross_red", "badge_cross_green"])], dx=-24, dy=16)
    if c.p(0.35):
        c.addg("apron", ["cream", "linen"])
    if c.p(0.3):
        c.addg("scarf_wrap", ["linen"], contains="tail")
    if c.p(0.5):
        c.addg("collar_fold", ["linen", "cream"])
    marks_common(c, tired=0.4, rouge=0.3)


def r_farmer(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("ochre", "brown"), ("moss", "brown"), ("sand", "linen"), ("rust", "brown")]))
    if c.female:
        k = c.choice("hat", ["wide_brim", "kerchief", "wide_brim", "felt_hat"])
    else:
        k = c.choice("hat", ["wide_brim", "felt_hat", "wide_brim", "none"])
    cols = {"wide_brim": ["straw", "sand", "brown"], "felt_hat": ["brown", "moss", "grey"], "kerchief": ["ochre", "wine", "linen"]}
    if k != "none":
        hat(c, k, cols[k])
    if c.p(0.6):
        c.addg("straps_pair", ["leather", "brown"])
    if c.p(0.3):
        c.addg("patch", ["linen", "moss", "leather"])
    if c.p(0.4):
        c.addg("collar_fold", ["linen", "sand"])
    marks_common(c, freck=0.5, dirt=0.4, stub=0.3, tired=0.1, rouge=0.2)


def r_chef(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("cream", "linen"), ("linen", "cream")]))
    k = c.choice("hat", ["toque", "cook_cap", "coif"] if not c.female else ["cook_cap", "coif", "kerchief"])
    cols = {"toque": ["linen", "cream"], "cook_cap": ["linen", "cream"], "coif": ["linen", "cream"], "kerchief": ["linen", "wine"]}
    hat(c, k, cols[k])
    c.addg("apron", ["cream", "linen"])
    c.addg("collar_fold", ["linen", "cream"])
    if c.p(0.4):
        c.addg("buttons", contains="bone")
    marks_common(c, rouge=0.4, soot=0.15, tired=0.1, mous=0.2)


def r_merc(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("leather", "charcoal"), ("brown", "rust"), ("charcoal", "brown"), ("grey", "leather")]))
    k = c.choice("hat", ["sallet", "mail_coif", "kettle_helm", "sallet", "leather_cap", "felt_hat"])
    cols = {"sallet": ["iron", "steel"], "mail_coif": ["iron", "steel"], "kettle_helm": ["iron", "steel"], "leather_cap": ["leather", "brown"],
            "felt_hat": ["charcoal", "brown"]}
    hat(c, k, cols[k])
    c.addg("bandolier", ["leather", "brown"])
    vest = c.choice("vest", ["brigandine", "brigandine", "gambeson", "none"])
    if vest == "brigandine":
        c.addg("brigandine", ["leather", "brown", "charcoal", "wine"])
    elif vest == "gambeson":
        c.addg("gambeson", ["brown", "grey", "sand", "charcoal" if False else "indigo"])
    if c.p(0.45):
        c.addg("pauldron", ["iron", "steel", "leather"])
    if c.p(0.4):
        c.addg("scarf_wrap", ["wine", "ochre", "charcoal"])
    if c.p(0.3):
        c.addg("patch", ["leather", "brown"])
    marks_common(c, scar=0.55, stub=0.4, bruise=0.15, tired=0.2)
    if c.p(0.1):
        c.add(c.lib.by_id["eyepatch"])
    if c.p(0.15):
        c.add(c.lib.by_id["bandage_cheek"])


def r_rev(c: Ctx) -> None:
    c.out.ramps = list(c.choice("ramp", [("moss", "brown"), ("grey", "charcoal"), ("brown", "moss"), ("rust", "grey")]))
    k = c.choice("hat", ["hood_front", "kerchief", "hood_front", "kerchief"])
    cols = {"hood_front": ["moss", "grey", "brown"], "kerchief": ["moss", "wine", "ochre", "indigo"]}
    hat(c, k, cols[k])
    if c.p(0.55):
        c.addg("scarf_cover", ["moss", "charcoal", "wine", "ochre"])
    c.addg("warpaint", key="paint") if c.p(0.7) else None
    vest = c.choice("vest", ["gambeson", "gambeson", "brigandine", "none"])
    if vest == "gambeson":
        c.addg("gambeson", ["brown", "grey", "sand", "moss"])
    elif vest == "brigandine":
        c.addg("brigandine", ["leather", "brown", "moss"])
    elif c.p(0.4):
        c.addg("straps_pair", ["leather", "brown"])
    if c.p(0.25):
        c.addg("sash", ["wine", "ochre"])
    marks_common(c, tired=0.2, scar=0.15, dirt=0.3)


ROLES = {"Upper": r_upper, "Lower": r_lower, "BM": r_bm, "Sec": r_sec, "SecOff": r_secoff, "SecCorpo": r_secorpo, "Eng": r_eng,
         "Sci": r_sci, "Med": r_med, "Farmer": r_farmer, "Chef": r_chef, "Merc": r_merc, "Rev": r_rev}

# Named portraits: (role recipe, sex, flags). Flags: whole = the original head cloth is recoloured (hooded figures), keep = no new
# headgear (the original hood stays), hat = (style, colours) to force one.
NAMED: dict[str, dict] = {
    "Courrier": dict(role="Lower", sex="male", hat=("felt_hat", ["brown"])),
    "Georgio": dict(role="Farmer", sex="male", hat=("wide_brim", ["sand"])),
    "Mentor": dict(role="BM", sex="male", whole=True, keep=True, ramps=["black", "charcoal"]),
    "Nellis": dict(role="Upper", sex="female", hat=("wimple", ["cream"])),
    "Serpico": dict(role="Sec", sex="male", hat=("kettle_helm", ["steel"])),
    "case_enjoyer": dict(role="Upper", sex="male", hat=("guild_cap", ["plum"])),
    "eleanor1": dict(role="Upper", sex="female", hat=("circlet", ["brass"])),
    "eleanor2": dict(role="Upper", sex="female", hat=("circlet", ["brass"])),
    "eleanor3": dict(role="Upper", sex="female", hat=("circlet", ["steel"])),
    "eleanor_rev": dict(role="Rev", sex="female", hat=("kerchief", ["moss"])),
    "eleanor_scav": dict(role="Merc", sex="female", hat=("leather_cap", ["leather"])),
    "femGenericsDec3": dict(role="BM", sex="female", hat=("hood_front", ["charcoal"])),
    "grandpa_cheng": dict(role="Sci", sex="male", hat=("skullcap", ["grey"])),
    "jackson": dict(role="Sci", sex="male", hat=("skullcap", ["indigo"])),
    "landlord": dict(role="Upper", sex="male", hat=("guild_cap", ["wine"]), ramps=["charcoal", "grey"]),
    "lou_sec": dict(role="Sec", sex="female", hat=("leather_cap", ["leather"])),
    "lun": dict(role="Sec", sex="male", hat=("kettle_helm", ["iron"])),
    "maleScav1": dict(role="Merc", sex="male", hat=("kettle_helm", ["iron"])),
    "maleScav10": dict(role="Rev", sex="male", whole=True, keep=True, ramps=["brown", "charcoal"]),
    "maleScav11": dict(role="Lower", sex="male", hat=("felt_hat", ["grey"])),
    "maleScav2": dict(role="Eng", sex="male", hat=("leather_cap", ["brown"])),
    "maleScav3": dict(role="Merc", sex="male"),
    "maleScav4": dict(role="Rev", sex="male"),
    "maleScav5": dict(role="Lower", sex="male"),
    "maleScav6": dict(role="Farmer", sex="male", hat=("kerchief", ["ochre"])),
    "maleScav7": dict(role="Rev", sex="male", whole=True, keep=True, ramps=["grey", "plum"]),
    "maleScav8": dict(role="Merc", sex="male", hat=("sallet", ["iron"])),
    "maleScav9": dict(role="Lower", sex="male", hat=("wide_brim", ["straw"])),
    "odin": dict(role="Merc", sex="male", hat=("mail_coif", ["steel"])),
    "sawyer": dict(role="Farmer", sex="male", hat=("felt_hat", ["wine"])),
    "serpico_rev": dict(role="Rev", sex="male", hat=("hood_front", ["moss"])),
    "serpico_scav": dict(role="Rev", sex="male", whole=True, keep=True, ramps=["grey", "brown"]),
    "trailer_rev1": dict(role="Rev", sex="female", whole=True, keep=True, ramps=["grey", "moss"]),
    "trailer_scav1": dict(role="Lower", sex="female", hat=("kerchief", ["ochre"])),
    "waffle_enjoyer": dict(role="Rev", sex="male", whole=True, keep=True, ramps=["moss", "brown"]),
    "wanted1": dict(role="Merc", sex="male", hat=("skullcap", ["grey"])),
    "wanted2": dict(role="Chef", sex="male", hat=("cook_cap", ["linen"]), ramps=["cream", "wine"]),
    "wanted3": dict(role="Sec", sex="male"),
    "wanted5": dict(role="Lower", sex="female", hat=("coif", ["linen"])),
    "wanted6": dict(role="Med", sex="male", hat=("coif", ["cream"])),
    "wanted7": dict(role="Eng", sex="male", hat=("leather_cap", ["leather"])),
    "wanted8": dict(role="Sci", sex="male", hat=("guild_cap", ["indigo"])),
    "wanted9": dict(role="Sec", sex="male"),
    "wild": dict(role="Upper", sex="male", hat=("feathered_cap", ["wine"]), ramps=["plum", "teal"]),
}

# Named portraits with white beards or similar: the face-gear detector must not take their beard for a mask.
NO_GEAR = {"Georgio", "Nellis", "grandpa_cheng", "wanted2", "landlord", "jackson"}

ROLE_RE = re.compile(r"^(male|female)(Upper|Lower|BM|SecOff|SecCorpo|Sec|Eng|Sci|Med|Farmer|Chef|Merc|Rev)\.")


def role_of(file: str) -> tuple[str, str] | None:
    """(role, sex) of a catalog file, or None for pictures that are not busts."""
    m = ROLE_RE.match(file)
    if m:
        return m.group(2), m.group(1)
    name = file.split(".")[0]
    if name in NAMED:
        return NAMED[name]["role"], NAMED[name]["sex"]
    return None


def make_outfit(c: Ctx, file: str) -> Outfit:
    name = file.split(".")[0]
    spec = NAMED.get(name)
    role = ROLE_RE.match(file).group(2) if ROLE_RE.match(file) else spec["role"]
    ROLES[role](c)
    out = c.out
    if spec:
        if spec.get("ramps"):
            out.ramps = list(spec["ramps"])
        if spec.get("whole"):
            out.whole = True
        if spec.get("keep") or spec.get("whole"):
            # keep the original hood: drop any generated headgear
            out.items = [i for i in out.items if i.part.cat != "hats" and i.part.style not in ("scarf_cover", "scarf_wrap", "cloak_back", "cloak_front", "mantle", "brigandine", "gambeson", "tabard")]
            out.erase_hair = False
        elif spec.get("hat"):
            out.items = [i for i in out.items if i.part.cat != "hats"]
            c.out.erase_hair = False
            hat(c, spec["hat"][0], spec["hat"][1])
    return out
