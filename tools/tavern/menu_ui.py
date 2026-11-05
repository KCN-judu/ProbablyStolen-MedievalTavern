"""The main-menu interface of the tavern: buttons, panels, check boxes, sliders, drop-downs, tabs, scroll bars, slots,
tooltips, the load-game list and the icons, as the sprites the game's menus are built from.

Every control with states is one function called with a state letter (see menu_kit.STATES), so its states are the same
shape in different tones. Sprites the game stretches (nine-slice) keep their corners inside the border in layout.tsv.
Left to the game's own art: the title logo, the Discord and Steam logos, and the network-icons atlas.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

from PIL import Image

from materials import tone
from menu_kit import (CHECKED, DISABLED, HOVER, NORMAL, PRESSED, REFUSED, STATES, Tone, bar, big_panel, board_face, groove,
                      icon, plate, put_icon, scaled)
from palette import BRASS, FLAME, IRON, LEATHER, MOSS, NAVY, OAK, PALE_WOOD, PARCHMENT, SHADOW, WINE, WOOD
from pix import CLEAR, Color, Pix, mix, rgb, scale_ramp

Drawing = Callable[[], Image.Image]
ASSETS: dict[str, Drawing] = {}

LIGHT: Color = PALE_WOOD[3]
TAN = Tone(PALE_WOOD, mix(PALE_WOOD[2], PARCHMENT[1], 0.3), BRASS[3], None)
ACTIVE = Tone(scale_ramp(OAK, 0.2), mix(WOOD[2], FLAME[0], 0.3), FLAME[3], FLAME[1])


def reg(stem: str, w: int, h: int, fn: Drawing) -> None:
    """Lists a picture under its catalog name `stem.WxH.png`."""
    ASSETS[f"{stem}.{w}x{h}.png"] = fn


def state_tone(state: str) -> Tone:
    return STATES[state]


# ---------------------------------------------------------------------------------------------- buttons


def button(w: int, h: int, state: str, thick: int = 3, cut: int = 2, straps: bool = False, accent: Color | None = None) -> Image.Image:
    """A push button: an oak plate with a brass line inside; `straps` adds iron bands near its ends like a door's."""
    t = state_tone(state)
    if accent is not None:
        t = t._replace(accent=accent if state != "h" else tone(accent, 0.3))
    p = plate(w, h, t, thick=thick, cut=cut, studs=h >= 26 and thick >= 3, seed=w * 7 + h, wood={"n": 0.5, "h": 0.3, "p": 0.72}.get(state, 0.5))
    if straps:
        for x in (thick + 8, w - thick - 14):
            p.rect(x, 1, 6, h - 2, IRON[2])
            p.vline(x, 1, h - 2, IRON[4])
            p.vline(x + 1, 1, h - 2, IRON[3])
            p.vline(x + 5, 1, h - 2, IRON[0])
            p.rect(x + 2, 5, 2, 2, BRASS[3])
            p.rect(x + 2, h - 7, 2, 2, BRASS[3])
    if state == "p":                                             # pressed: sunk, shadow along the top
        p.dither(2, 2, w - 4, 3, SHADOW, 0.8)
    return p.im


for _s, _n in (("n", "n"), ("h", "h"), ("p", "p")):
    reg(f"button_main_menu_{_n}", 220, 35, partial(button, 220, 35, _s, straps=True))
    reg(f"gen_button_2x_{_n}", 194, 68, partial(button, 194, 68, _s, thick=4, cut=4))
reg("button_load", 47, 20, lambda: button(47, 20, "n", thick=2, cut=2))
reg("button_load_hl", 47, 20, lambda: button(47, 20, "h", thick=2, cut=2))
reg("playtest_button_discord", 75, 30, lambda: button(75, 30, "n", thick=2, cut=2, accent=NAVY[3]))
reg("playtest_button_feedback", 75, 30, lambda: button(75, 30, "n", thick=2, cut=2, accent=BRASS[3]))
reg("playtest_button_steam", 75, 30, lambda: button(75, 30, "n", thick=2, cut=2, accent=MOSS[3]))
reg("button_generic_x2", 32, 32, lambda: plate(32, 32, TAN, thick=2, cut=1, accent=False, seed=3).im)
reg("key_box", 32, 16, lambda: plate(32, 16, Tone(IRON, IRON[1], BRASS[2], None), thick=2, cut=1, accent=False).im)


def framed_icon(size: int, state: str, name: str, color: Color | None = None, scale: int = 1, thick: int = 2, cut: int = 1) -> Image.Image:
    """A small square button carrying an icon in the colour of its state's accent."""
    t = state_tone(state)
    p = plate(size, size, t, thick=thick, cut=cut, accent=False, seed=size)
    put_icon(p, name, color or (t.accent if state != "n" else BRASS[3]), size // 2, size // 2, scale)
    if state == "p":
        p.dither(2, 2, size - 4, 3, SHADOW, 0.8)
    return p.im


for _s, _n in (("n", "n"), ("h", "h"), ("p", "p")):
    reg(f"close_button_{_n}", 16, 16, partial(framed_icon, 16, _s, "cross", thick=1, cut=0))
reg("close_normal", 16, 16, lambda: framed_icon(16, "n", "cross", rgb("#d06a4a"), thick=1, cut=0))
reg("close_pressed", 16, 16, lambda: framed_icon(16, "r", "cross", rgb("#e08a6a"), thick=1, cut=0))
reg("close_pressed_down", 16, 16, lambda: framed_icon(16, "p", "cross", rgb("#a04a38"), thick=1, cut=0))
reg("delete_save_button", 16, 16, lambda: framed_icon(16, "n", "trash", thick=1, cut=0))
reg("delete_save_button_hl", 16, 16, lambda: framed_icon(16, "h", "trash", thick=1, cut=0))
reg("cross_normal", 32, 32, lambda: framed_icon(32, "n", "cross", scale=2))
reg("cross_hover", 32, 32, lambda: framed_icon(32, "h", "cross", scale=2))
reg("cross", 32, 32, lambda: framed_icon(32, "d", "cross", IRON[4], scale=2))
for _n, _name in (("delete", "trash"), ("duplicate", "copy"), ("magnify", "magnify")):
    reg(f"load_{_n}_normal", 32, 32, partial(framed_icon, 32, "n", _name, scale=2))
    reg(f"load_{_n}_hover", 32, 32, partial(framed_icon, 32, "h", _name, scale=2))
reg("magnify", 32, 32, lambda: framed_icon(32, "n", "magnify", scale=2))
reg("magnify_hl", 32, 32, lambda: framed_icon(32, "h", "magnify", scale=2))
reg("settings", 42, 42, lambda: framed_icon(42, "n", "gear", scale=3, thick=3, cut=2))
reg("settings_hl", 42, 42, lambda: framed_icon(42, "h", "gear", scale=3, thick=3, cut=2))
for _dir, _flip in (("next", True), ("prev", False)):
    for _s, _suffix in (("n", "normal"), ("h", "hover")):
        def _arrow(s: str = _s, f: bool = _flip) -> Image.Image:
            t = state_tone(s)
            p = plate(32, 32, t, thick=2, cut=1, accent=False, seed=5)
            ic = icon("chevron", t.accent if s == "h" else BRASS[3], 2, flip=f)
            p.paste(ic, 16 - ic.w // 2, 16 - ic.h // 2)
            return p.im
        reg(f"arrow_{_dir}_{_suffix}", 32, 32, _arrow)


def glass_strip() -> Image.Image:
    """Three 16x16 magnifier buttons side by side: dim, lit, normal (the frames of the game's sheet)."""
    out = Pix(48, 16)
    for i, (s, c) in enumerate((("d", IRON[3]), ("h", FLAME[3]), ("n", BRASS[3]))):
        out.paste(framed_icon(16, s, "magnify", c, thick=1, cut=0), i * 16, 0)
    return out.im


reg("glass_button", 48, 16, glass_strip)


# ---------------------------------------------------------------------------------------------- check boxes and ticks


def tick_pix(w: int, h: int, color: Color, scale: int) -> Pix:
    p = Pix(w, h)
    put_icon(p, "tick", color, w // 2, h // 2, scale)
    return p


def checkbox(size: int, state: str, checked: bool = False, thick: int = 1) -> Image.Image:
    """An empty box (or one with a tick); `state` n or h."""
    t = state_tone(state)
    p = plate(size, size, t, thick=thick, cut=0, accent=False, seed=size)
    if checked:
        k = 1 if size < 20 else 2
        put_icon(p, "tick", MOSS[3] if state == "n" else FLAME[3], size // 2, size // 2, k)
    return p.im


reg("checkbox", 16, 16, lambda: checkbox(16, "n"))
reg("checkbox", 32, 32, lambda: checkbox(32, "n", thick=2))
reg("checkbox_hl", 32, 32, lambda: checkbox(32, "h", thick=2))
reg("checkbox_arrow", 16, 16, lambda: checkbox(16, "n", True))
reg("checkbox_mark", 32, 32, lambda: tick_pix(32, 32, FLAME[3], 2).im)
reg("checkbox_orange", 13, 13, lambda: plate(13, 13, Tone(OAK, SHADOW, FLAME[2], None), thick=1, cut=0, accent=False).im)
reg("checkbox_checked_orange", 13, 13, lambda: checkbox_orange_checked())
reg("check", 20, 20, lambda: tick_pix(20, 20, MOSS[3], 2).im)
reg("Checkmark", 64, 64, lambda: tick_pix(64, 64, OAK[2], 5).im)
reg("cross", 20, 20, lambda: tick_cross())


def checkbox_orange_checked() -> Image.Image:
    p = Pix(13, 13)
    p.paste(plate(13, 13, Tone(OAK, mix(SHADOW, FLAME[0], 0.5), FLAME[2], None), thick=1, cut=0, accent=False), 0, 0)
    put_icon(p, "tick", FLAME[3], 6, 6, 1)
    return p.im


def tick_cross() -> Image.Image:
    p = Pix(20, 20)
    put_icon(p, "cross", rgb("#d0583a"), 10, 10, 1)
    return p.im


# ---------------------------------------------------------------------------------------------- sliders and scroll bars


def knob(w: int, h: int, hot: bool) -> Image.Image:
    """The grip of a slider: a brass-rimmed wooden block with a notch of grip lines, brighter when `hot`."""
    t = HOVER if hot else NORMAL
    p = plate(w, h, Tone(scale_ramp(BRASS, 0.0 if hot else -0.2), mix(WOOD[2], BRASS[1], 0.4 if hot else 0.1), t.accent, None), thick=1, cut=2 if w > 14 else 1, accent=False)
    for x in range(w // 2 - 2, w // 2 + 3, 2):
        p.vline(x, 3, h - 6, SHADOW)
        p.vline(x + 1, 3, h - 6, tone(BRASS[2], 0.2))
    return p.im


reg("slider_handle_n", 18, 12, lambda: knob(18, 12, False))
reg("slider_handle_h", 18, 12, lambda: knob(18, 12, True))
reg("slider_thumb", 32, 22, lambda: knob(32, 22, False))
reg("slider_thumb_hl", 32, 22, lambda: knob(32, 22, True))
reg("slider_track", 320, 8, lambda: groove(320, 8).im)
reg("slider_gauge", 320, 8, lambda: gauge(320, 8))
reg("slider_bar_2x", 238, 16, lambda: groove(238, 16).im)
reg("slider_bar_filled_2x", 238, 16, lambda: gauge(238, 16))


def gauge(w: int, h: int) -> Image.Image:
    """The filled part of a slider: molten amber in a dark outline, lit along its top."""
    p = bar(w, h, FLAME[2], SHADOW)
    if h > 6:
        p.hline(1, 2, w - 2, FLAME[3])
    p.dither(1, h // 2, w - 2, h - h // 2 - 1, FLAME[1], 0.5)
    return p.im


def thumb(w: int, h: int, grip: bool = True) -> Image.Image:
    """A scroll-bar thumb: pale wood with a lit left edge, a shaded right edge and grip ridges in the middle."""
    p = Pix(w, h)
    p.rect(0, 0, w, h, SHADOW)
    if w > 2 and h > 2:
        p.rect(1, 1, w - 2, h - 2, PALE_WOOD[2])
        p.vline(1, 1, h - 2, PALE_WOOD[4])
        p.vline(w - 2, 1, h - 2, PALE_WOOD[0])
        p.hline(1, 1, w - 2, PALE_WOOD[4])
        if grip and w > 4 and h > 14:
            for y in range(h // 2 - 4, h // 2 + 5, 3):
                p.hline(2, y, w - 4, PALE_WOOD[0])
                p.hline(2, y + 1, w - 4, PALE_WOOD[4])
    return p.im


reg("scroll_thumb", 6, 32, lambda: thumb(6, 32, False))
reg("handle", 16, 256, lambda: thumb(16, 256))
reg("scroll_bar_top_x2", 16, 84, lambda: thumb(16, 84))
reg("vertical_scroll_bar_handle_2x", 16, 64, lambda: thumb(16, 64))
reg("scroll_track", 2, 64, lambda: groove(2, 64, True).im)
reg("scroll", 16, 797, lambda: groove(16, 797, True).im)
reg("scroll_bar_bot_x2", 16, 568, lambda: groove(16, 568, True).im)
reg("vertical_scroll_bar", 8, 32, lambda: groove(8, 32, True).im)


# ---------------------------------------------------------------------------------------------- panels


def panel(w: int, h: int, thick: int = 1, t: Tone = NORMAL, studs: bool = False, plank: int = 14) -> Image.Image:
    """A panel whose frame is as thin as its nine-slice border allows (so the corners survive stretching), over boards."""
    p = plate(w, h, t, thick=thick, cut=0, accent=False, grain=False)
    board_face(p, 1 + thick, 1 + thick, w - 2 - 2 * thick, h - 2 - 2 * thick, plank=plank)
    p.hline(1 + thick, 1 + thick, w - 2 - 2 * thick, SHADOW)
    if studs:
        for sx, sy in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)):
            p.px(sx, sy, BRASS[3])
    return p.im


reg("panel", 352, 212, lambda: panel(352, 212, 1))
reg("dropdown_template_bg", 352, 212, lambda: panel(352, 212, 1, studs=True))
reg("modding_layout_2x", 32, 32, lambda: panel(32, 32, 1))
reg("window_frame", 64, 64, lambda: big_panel(64, 64, thick=2, cut=2).im)
reg("recorder_x2", 394, 584, lambda: big_panel(394, 584, thick=4).im)
reg("option_bg", 394, 480, lambda: big_panel(394, 480, header=16, thick=4).im)
reg("option_bg", 494, 480, lambda: big_panel(494, 480, header=16, thick=4).im)
reg("loadgame_base", 394, 480, lambda: big_panel(394, 480, header=16, thick=4).im)
reg("modding", 800, 480, lambda: big_panel(800, 480, header=16, thick=4).im)
reg("shortcut_x2", 764, 418, lambda: big_panel(764, 418, header=30, thick=3).im)
reg("meta_section_2x", 910, 126, lambda: meta_section())
reg("new_game_bg", 556, 480, lambda: big_panel(556, 480, header=24, thick=4).im)
reg("perks_tooltip", 442, 178, lambda: big_panel(442, 178, thick=5, cut=3).im)
reg("tooltip_2x", 78, 116, lambda: plate(78, 116, Tone(WINE, SHADOW, BRASS[2], None), thick=2, cut=2, studs=True).im)
reg("card_plate", 64, 64, lambda: plate(64, 64, Tone(PALE_WOOD, PARCHMENT[1], BRASS[3], None), thick=2, cut=2, accent=False).im)
reg("card_header_plate", 64, 42, lambda: plate(64, 42, TAN, thick=2, cut=2, accent=False).im)
reg("uiback1", 16, 16, lambda: plate(16, 16, Tone(OAK, OAK[2], BRASS[1], None), thick=1, cut=0, accent=False).im)
reg("uibacktop1", 16, 16, lambda: plate(16, 16, Tone(WOOD, WOOD[2], BRASS[1], None), thick=1, cut=0, accent=False).im)
reg("uiback1LTan_embossed", 64, 64, lambda: plate(64, 64, Tone(PALE_WOOD, PARCHMENT[2], BRASS[2], None), thick=3, cut=2, accent=True).im)
reg("frame_2_square", 6, 6, lambda: plate(6, 6, TAN, thick=1, cut=0, accent=False).im)


def meta_section() -> Image.Image:
    """A wide section: a dark panel under a 36 pixel title strip of iron."""
    p = Pix(910, 126)
    p.paste(panel(910, 126, 1), 0, 0)
    p.rect(1, 1, 908, 34, IRON[1])
    p.hline(1, 1, 908, IRON[3])
    p.hline(1, 34, 908, SHADOW)
    p.hline(1, 33, 908, BRASS[2])
    return p.im


def white_rounded(w: int, h: int, radius: int, outline: int = 0) -> Image.Image:
    """A near-white rounded rectangle, for the sprites the game tints (masks, field backgrounds). A warm shade runs along
    its lower edge so a tint does not look flat; `outline` adds a dark rim."""
    p = Pix(w, h)
    p.draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=SHADOW if outline else (236, 228, 212, 255))
    if outline:
        p.draw.rounded_rectangle((outline, outline, w - 1 - outline, h - 1 - outline), radius=max(1, radius - outline), fill=(236, 228, 212, 255))
    shade = Pix(w, h)
    shade.rect(0, h - max(2, h // 8) - outline, w, max(2, h // 8), (200, 188, 168, 255))
    mask = p.im.getchannel("A")
    shade.im.putalpha(Image.composite(shade.im.getchannel("A"), Image.new("L", (w, h), 0), mask))
    p.paste(shade, 0, 0)
    return p.im


reg("UIBevel", 256, 256, lambda: white_rounded(256, 256, 48, 10))
reg("UIMask", 32, 32, lambda: padded(white_rounded(24, 24, 7), 32))
reg("UISprite", 32, 32, lambda: padded(white_rounded(28, 28, 8), 32))
reg("Background", 32, 32, lambda: padded(white_rounded(28, 28, 8), 32))
reg("InputFieldBackground", 32, 32, lambda: padded(field(28), 32))


def padded(im: Image.Image, size: int) -> Image.Image:
    """The picture centred on a transparent square (the game's sprites keep a margin around their shape)."""
    out = Image.new("RGBA", (size, size), CLEAR)
    out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return out


def field(size: int) -> Image.Image:
    """A writing field: parchment with a dark rim and a shaded top, so typed text sits in a hollow."""
    p = plate(size, size, Tone(OAK, PARCHMENT[3], PARCHMENT[2], None), thick=2, cut=3, accent=False, grain=False)
    p.dither(3, 3, size - 6, 3, PARCHMENT[1], 0.7)
    return p.im


# ---------------------------------------------------------------------------------------------- drop-downs, frames, tabs


def field_bar(w: int, h: int, state: str = "n", thick: int = 2, cut: int = 1) -> Image.Image:
    """A row of the menu (a drop-down head, a framed option): a plate whose tone says its state."""
    return plate(w, h, state_tone(state), thick=thick, cut=cut, accent=False, seed=w, wood=0.3 if state == "h" else 0.55).im


reg("dropdownElement", 320, 32, lambda: plate(320, 32, Tone(OAK, mix(WOOD[1], OAK[1], 0.5), BRASS[1], None), thick=1, cut=0, accent=False).im)
reg("dropdown_2x", 206, 32, lambda: field_bar(206, 32, "n", 2, 2))
reg("dropdown_box", 101, 14, lambda: field_bar(101, 14, "n", 1, 1))
reg("dropdown_panel", 101, 14, lambda: field_bar(101, 14, "d", 1, 1))
reg("dropdown_option", 101, 15, lambda: plate(101, 15, Tone(WOOD, mix(WOOD[2], FLAME[1], 0.25), FLAME[2], FLAME[1]), thick=1, cut=0, accent=False).im)
reg("frame", 320, 32, lambda: field_bar(320, 32, "n", 2, 2))
reg("frame_hl", 320, 32, lambda: field_bar(320, 32, "h", 2, 2))


def dropdown_arrow() -> Image.Image:
    p = plate(16, 16, NORMAL, thick=1, cut=0, accent=False)
    put_icon(p, "down", BRASS[3], 8, 8, 1)
    return p.im


reg("dropdown_button", 16, 16, dropdown_arrow)


def tab(w: int, h: int, t: Tone, w_used: int | None = None) -> Image.Image:
    """A tab of the menu: a plate with its top corners cut and its bottom open, so it grows out of the panel below it."""
    full = plate(w_used or w, h + 6, t, thick=2, cut=4, accent=False, seed=w, wood=0.15 if t is ACTIVE else 0.3 if t is HOVER else 0.55).im
    out = Image.new("RGBA", (w, h), CLEAR)
    out.alpha_composite(full.crop((0, 0, full.width, h)), (0, 0))
    return out


reg("tab_active", 129, 31, lambda: tab(129, 31, ACTIVE, 128))
reg("tab", 129, 31, lambda: tab(129, 31, NORMAL, 128))
reg("tab_active", 256, 42, lambda: tab(256, 42, ACTIVE))
reg("tab_hover", 256, 42, lambda: tab(256, 42, HOVER))
reg("tab_normal", 256, 42, lambda: tab(256, 42, NORMAL))


# ---------------------------------------------------------------------------------------------- slots, tags, rows


def slot_border(state: str) -> Image.Image:
    """The rim of an item slot, open in the middle: dull brass, lit amber, or moss for an owned item."""
    accent = {"n": OAK, "h": scale_ramp(BRASS, 0.1), "c": scale_ramp(MOSS, 0.1)}[state]
    t = Tone(accent if state != "n" else scale_ramp(OAK, 0.15), SHADOW, BRASS[2], None)
    p = plate(84, 84, t, thick=2, cut=1, accent=False, hollow=True, studs=state != "n")
    return p.im


reg("slot_border_normal", 84, 84, lambda: slot_border("n"))
reg("slot_border_hover", 84, 84, lambda: slot_border("h"))
reg("slot_border_purchased", 84, 84, lambda: slot_border("c"))
reg("slot_frame", 84, 84, lambda: plate(84, 84, NORMAL, thick=3, cut=2, studs=True).im)
reg("slot_inset", 76, 76, lambda: inset(76, 76))


def inset(w: int, h: int) -> Image.Image:
    """A hollow in the wood where an item sits: dark, with the shade falling from the upper left."""
    p = Pix(w, h)
    p.rect(0, 0, w, h, OAK[0])
    p.hline(0, 0, w, SHADOW)
    p.vline(0, 0, h, SHADOW)
    p.hline(1, 1, w - 2, SHADOW)
    p.vline(1, 1, h - 2, SHADOW)
    p.hline(0, h - 1, w, OAK[3])
    p.vline(w - 1, 0, h, OAK[3])
    p.dither(2, 2, w - 4, 8, SHADOW, 0.5)
    return p.im


def tag(unavailable: bool) -> Image.Image:
    """A price tag: parchment (or wine-red when the item is out of reach) with a hole at each end for the string."""
    c = WINE if unavailable else PARCHMENT
    p = Pix(56, 22)
    p.rect(0, 0, 56, 22, SHADOW)
    p.rect(1, 1, 54, 20, c[2])
    p.hline(1, 1, 54, c[3])
    p.vline(1, 1, 20, c[3])
    p.hline(1, 20, 54, c[0])
    p.vline(54, 1, 20, c[0])
    p.speckle(2, 2, 52, 18, (c[1], c[3]), 0.05)
    for x in (3, 51):
        p.rect(x, 9, 2, 4, SHADOW)
    p.clip([(3, 0), (52, 0), (55, 3), (55, 18), (52, 21), (3, 21), (0, 18), (0, 3)])
    p.outline(SHADOW, inside=True)
    return p.im


reg("price_tag_normal", 56, 22, lambda: tag(False))
reg("price_tag_unavailable", 56, 22, lambda: tag(True))


def save_row() -> Image.Image:
    """A row of the load list: an oak bar with a notched left end where a save's icon hangs, and a brass line along it."""
    p = Pix(353, 43)
    p.paste(plate(353, 43, Tone(OAK, mix(WOOD[1], OAK[0], 0.4), BRASS[2], None), thick=2, cut=3, accent=False, seed=4), 0, 0)
    p.rect(0, 0, 6, 43, SHADOW)
    p.rect(1, 1, 4, 41, IRON[2])
    p.vline(1, 1, 41, IRON[4])
    p.px(3, 6, BRASS[3])
    p.px(3, 36, BRASS[3])
    p.dither(8, 4, 340, 35, FLAME[0], 0.05)
    return p.im


reg("save_element", 353, 43, save_row)


def end_cap() -> Image.Image:
    """The top-left cap of the load dialog's header: an iron end with a slanted top, studded."""
    p = Pix(12, 42)
    p.rect(0, 0, 12, 42, IRON[2])
    p.vline(0, 0, 42, IRON[4])
    p.vline(11, 0, 42, IRON[0])
    p.hline(0, 41, 12, SHADOW)
    p.px(5, 8, BRASS[3])
    p.px(5, 34, BRASS[3])
    p.poly([(0, 0), (11, 0), (0, 11)], CLEAR)
    p.line(0, 11, 11, 0, BRASS[2])
    return p.im


reg("load_dialog_cap", 12, 42, end_cap)


def header_strip() -> Image.Image:
    """A title strip whose left end is slanted away: iron with a brass line along its foot."""
    p = Pix(64, 42)
    p.gradient(0, 0, 64, 42, IRON[3], IRON[1], 5)
    p.hline(0, 41, 64, SHADOW)
    p.hline(0, 40, 64, BRASS[2])
    p.hline(0, 0, 64, IRON[4])
    p.poly([(0, 0), (15, 0), (0, 15)], CLEAR)
    p.line(0, 15, 15, 0, BRASS[2])
    return p.im


reg("header_bar", 64, 42, header_strip)


def divider(w: int, h: int, ornament: bool) -> Image.Image:
    """A line across a panel: a lit brass thread over a dark one, with a small diamond at each end when `ornament`."""
    p = Pix(w, h)
    y = h // 2 - 1
    p.hline(0, y, w, BRASS[2])
    p.hline(0, y + 1, w, SHADOW)
    if ornament:
        for x in (4, w - 5):
            p.poly([(x, y - 3), (x + 3, y), (x, y + 3), (x - 3, y)], BRASS[3])
    return p.im


reg("seperator", 900, 2, lambda: divider(900, 2, False))
reg("option_line_single", 337, 12, lambda: divider(337, 12, True))


def chain_link() -> Image.Image:
    p = Pix(24, 4)
    for x in range(0, 24, 6):
        p.rect(x, 0, 5, 4, IRON[3])
        p.rect(x + 1, 1, 3, 2, SHADOW)
        p.hline(x, 0, 5, IRON[4])
    return p.im


reg("connector", 24, 4, chain_link)


def credit_rules() -> Image.Image:
    """The credits page: no frame of its own, just three brass rules between the blocks of names."""
    p = Pix(394, 480)
    for y in (70, 150, 220):
        p.paste(divider(394, 12, True), 0, y)
    return p.im


reg("credit_line", 394, 480, credit_rules)


def ring_badge() -> Image.Image:
    """The round badge behind a save's icon: a brass ring around a dark disc."""
    p = Pix(42, 42)
    p.ellipse(0, 0, 42, 42, SHADOW)
    p.ellipse(1, 1, 40, 40, BRASS[2])
    p.ellipse(4, 4, 34, 34, BRASS[1])
    p.ellipse(5, 5, 32, 32, FACE_DARK)
    p.dither(8, 8, 18, 10, SHADOW, 0.4)
    return p.im


FACE_DARK = mix(OAK[0], SHADOW, 0.35)
reg("load_icon_ring", 42, 42, ring_badge)


# ---------------------------------------------------------------------------------------------- loose icons


def warn_triangle() -> Image.Image:
    p = Pix(20, 19)
    p.poly([(9, 0), (19, 18), (0, 18)], SHADOW)
    p.poly([(9, 3), (16, 16), (3, 16)], FLAME[2])
    p.line(9, 3, 3, 16, FLAME[3])
    p.vline(9, 7, 5, SHADOW)
    p.px(9, 13, SHADOW)
    p.px(9, 14, SHADOW)
    return p.im


reg("mods_warning", 20, 19, warn_triangle)


def folder_badge() -> Image.Image:
    p = Pix(20, 20)
    p.ellipse(0, 0, 20, 20, SHADOW)
    p.ellipse(1, 1, 18, 18, OAK[2])
    put_icon(p, "folder", BRASS[3], 10, 10, 1)
    return p.im


reg("source_icon_local", 20, 20, folder_badge)


def padlock_big() -> Image.Image:
    p = Pix(32, 32)
    put_icon(p, "lock", BRASS[3], 16, 16, 3)
    return p.im


reg("padlock", 32, 32, padlock_big)


def clipboard() -> Image.Image:
    p = Pix(128, 128)
    put_icon(p, "clip", PARCHMENT[3], 64, 64, 10)
    put_icon(p, "tick", MOSS[2], 64, 74, 5)
    return p.im


reg("clipboard", 128, 128, clipboard)


def magnifier_big() -> Image.Image:
    """A magnifying glass drawn on a 64 grid and enlarged by 16: a ring of near-white wood with a handle."""
    g = Pix(64, 64)
    g.ellipse(4, 4, 38, 38, SHADOW)
    g.ellipse(7, 7, 32, 32, PARCHMENT[4])
    g.ellipse(13, 13, 20, 20, CLEAR)
    g.ellipse(12, 12, 22, 22, SHADOW)
    g.ellipse(13, 13, 20, 20, CLEAR)
    g.poly([(36, 40), (40, 36), (60, 56), (56, 60)], SHADOW)
    g.poly([(38, 40), (40, 38), (57, 55), (55, 57)], BRASS[3])
    return scaled(g, 16)


reg("MagnifyingGlass", 1024, 1024, magnifier_big)


def drag_arrow() -> Image.Image:
    """A double-headed diagonal arrow on a 64 grid, enlarged by 8."""
    g = Pix(64, 64)
    g.poly([(8, 56), (8, 36), (14, 42), (42, 14), (36, 8), (56, 8), (56, 28), (50, 22), (22, 50), (28, 56)], SHADOW)
    g.poly([(11, 52), (11, 41), (15, 45), (45, 15), (41, 11), (52, 11), (52, 22), (48, 18), (18, 48), (22, 52)], PARCHMENT[3])
    return scaled(g, 8)


reg("DragArrow", 512, 512, drag_arrow)


def padlock_small(w: int, h: int, body: Color, shackle: Color) -> Image.Image:
    """A padlock for the perk slots: an arch of iron over a body with a keyhole."""
    p = Pix(w, h)
    sw = w * 5 // 8
    sx = (w - sw) // 2
    top = h * 6 // 18
    p.rect(sx, 0, sw, top + 4, SHADOW)
    p.rect(sx + 2, 2, sw - 4, top + 4, CLEAR)
    p.rect(sx, 1, 2, top + 2, shackle)
    p.rect(sx + sw - 2, 1, 2, top + 2, shackle)
    p.rect(sx, 0, sw, 2, shackle)
    p.rect(0, top, w, h - top, SHADOW)
    p.rect(1, top + 1, w - 2, h - top - 2, body)
    p.hline(1, top + 1, w - 2, tone(body, 0.3))
    p.hline(1, h - 2, w - 2, tone(body, -0.4))
    kx = w // 2 - 1
    p.rect(kx, top + (h - top) // 2 - 2, 2, 3, SHADOW)
    p.vline(kx, top + (h - top) // 2 + 1, 3, SHADOW)
    return p.im


reg("perk_slot_lock", 16, 18, lambda: padlock_small(16, 18, PARCHMENT[2], IRON[3]))
reg("perk_tooltip_lock", 16, 18, lambda: padlock_small(16, 18, WINE[3], IRON[3]))
