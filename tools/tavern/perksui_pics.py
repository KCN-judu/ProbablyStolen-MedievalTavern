"""The remaining pictures of the tavern's interface (catalog groups `ui/in-game` and `ui/main-menu`): bubbles, logos, the road
map, scratch cards, network item icons and the figure strips of scavengers."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PIL import Image

import perksui_cards as cards
import perksui_folk as folk
import perksui_icons as icons

ASSETS: Mapping[str, Callable[[], Image.Image]] = {
    "bubble_sheet2.512x512.png": cards.bubble_sheet,
    "connector.133x174.png": cards.connector,
    "exghange_logo.60x42.png": cards.exchange_logo,
    "guide_logo.283x116.png": cards.guide_logo,
    "lines.1808x832.png": cards.route_map,
    "sample.211x211.png": folk.sample,
    "scavFemale.2880x422.png": folk.scav_female,
    "scavMale.576x211.png": folk.scav_male,
    "special.2304x211.png": folk.special,
    "networkIcons.682x493.png": icons.network_icons,
    "scratch.180x142.png": cards.scratch_front,
    "scratch_back.180x142.png": cards.scratch_back,
}
