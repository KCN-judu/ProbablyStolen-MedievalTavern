"""Draws a 640x360 test board of every fxkit material beside a crop of the real cask and counter top (a script, no ASSETS).

    python tools/tavern/fxkit_demo.py [out_dir]          # out_dir defaults to %TEMP%\\fxkit
It writes board_1x.png (the board), board.png (the board at 2x with the reference crops at 3x under it) and, when
`full.png` (a preview render) is in out_dir, the crops. Render the preview first with tools/preview/preview.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

import fxkit as fx
from materials import plaster
from palette import BRASS, GLASS, IRON, LEATHER, LINEN, MOSS, NAVY, OAK, PALE_WOOD, PLASTER, WINE, WOOD
from pix import Pix, mix

W, H = 640, 360


def board() -> Image.Image:
    p = Pix(W, H, seed=7)
    plaster(p, 0, 0, W, 250, stains=False)
    # the counter along the bottom
    fx.wood_fill(p, (0, 250, W, 110), "h", PALE_WOOD, board=14, seed=1, light=0.4)
    p.hline(0, 250, W, PALE_WOOD[4])
    fx.contact_shadow(p, (0, 244, W, 6), shift=(0, 0), spread=3, strength=0.8)

    # 1. a panel of planks, with damp, and a vertical-staved panel
    fx.wood_fill(p, (8, 8, 150, 92), "h", WOOD, seed=2, damp=0.7)
    fx.wood_fill(p, (8, 106, 70, 40), "v", OAK, seed=3)
    fx.wood_fill(p, (84, 106, 74, 14), "h", PALE_WOOD, seed=4)
    fx.wood_fill(p, (84, 124, 74, 22), "h", WOOD, seed=5, board=22)
    # 2. a stave barrel strip (a bellied surface)
    b = fx.belly(214, 8, 138, 52, bulge=0.12, staves=11)
    fx.wood_fill(p, b.outline, "v", WOOD, board=14, curve=b.curve, light_fn=lambda x, y: 1.3 * b.light(x, y), light=0.0,
                 seed=6, knots=1.5, joints=False, nails=False, wear_amount=0.1, scratches=2)
    for yy in (30, 62, 100, 126):
        t = (yy - 8) / 138
        hw = 52 / 1.12 * (1 + 0.12 * (1 - (2 * t - 1) ** 2))
        ry = 0.12 * hw
        arc = [(214 + dx, yy + ry * (1 - (dx / hw) ** 2) ** 0.5) for dx in range(-int(hw) + 1, int(hw))]
        fx.iron_band(p, arc, 5, rivets=17, rust=0.2, seed=yy)
    # 3. a curled poster with tape and a torn corner, and a small parchment with nails
    fx.paper_fill(p, (292, 12, 66, 92), folds=(1, 2), stains=0.6, curl=("br",), tear=("tl",), tape=("tr",), ink=0.6, seed=8)
    fx.paper_fill(p, (368, 14, 36, 44), folds=(0, 1), nails=("tl", "tr"), stains=0.4, seed=9, ink=0.5)
    # 4. a rope hanging between two nails, a coiled rope
    a1, a2 = (420, 20), (556, 28)
    fx.rope(p, fx.hang_curve(a1, a2, 34), 5, knots=(0.5,), fray=(False, False), seed=10)
    fx.rivet(p, *a1, 2, IRON)
    fx.rivet(p, *a2, 2, IRON)
    fx.chain(p, fx.hang_curve((414, 72), (478, 80), 22), link=11)
    fx.rope(p, fx.hang_curve((486, 74), (540, 100), 12), 3, fray=(False, True), seed=11)
    fx.coil(p, 598, 76, 28, 10, turns=3, thickness=6, seed=12)
    # 5. iron straps with rivets
    fx.iron_fill(p, (8, 156, 150, 12), rivets=14, seed=13)
    fx.iron_fill(p, (8, 174, 150, 8), rivets=0, seed=14)
    fx.iron_fill(p, (8, 188, 16, 50), seed=15, rivets=12)
    fx.iron_fill(p, (30, 188, 128, 50), seed=16, hammer=0.9, rust=0.6)
    # 6. brass fittings
    fx.brass_fill(p, (176, 160, 60, 14), profile="tube", seed=17)
    fx.brass_fill(p, (176, 180, 14, 40), profile="tube", seed=18)
    fx.brass_fill(p, (198, 180, 40, 30), profile="plate", studs=9, seed=19)
    fx.brass_fill(p, fx.ellipse(262, 196, 12, 12), profile="dome", seed=20)
    fx.rivet(p, 292, 196, 3)
    fx.rivet(p, 304, 196, 2)
    fx.rivet(p, 314, 196, 1)
    # 7. glass over a gradient (the gradient is the 'scene' beyond it)
    scene = Pix(W, H, seed=1)
    scene.gradient(330, 130, 120, 100, (222, 150, 70), (50, 70, 120), 8)
    scene.speckle(330, 130, 120, 100, ((250, 220, 150),), 0.01)
    fx.glass_pane(scene, (330, 130, 120, 100), cols=3, rows=3, seed=21)
    p.paste(scene, 0, 0)
    # 8. cloth swatches
    fx.cloth_fill(p, (466, 118, 50, 50), LINEN, "linen", stitch="b", fray="r", seed=22)
    fx.cloth_fill(p, (522, 118, 50, 50), WINE, "wool", stitch="t", fray="b", seed=23)
    fx.cloth_fill(p, (578, 118, 54, 50), MOSS, "linen", fold_dir="v", seed=24, stitch="tb")
    fx.cloth_fill(p, (466, 176, 166, 62), NAVY, "wool", folds=7, seed=25, stitch="l", fray="r")
    # 9. things on the counter, with contact shadows, and a Cuboid in the shop's perspective
    fx.contact_shadow(p, fx.ellipse(40, 296, 24, 6), shift=(2, 1))
    fx.brass_fill(p, fx.ellipse(40, 292, 20, 18), profile="dome", seed=26)
    fx.contact_shadow(p, fx.ellipse(110, 322, 30, 7), shift=(3, 1), spread=4)
    fx.iron_fill(p, fx.ellipse(110, 316, 24, 10), seed=27)
    fx.cast_shadow(p, (170, 280, 22, 30), direction=(1, 0.4), length=16)
    fx.wood_fill(p, (170, 270, 22, 34), "v", OAK, seed=28)
    try:
        from propsy_fx import Cuboid
        box = Cuboid(250, 330, 296, 30, 0.8, vp=(480, 150))
        fx.cast_shadow(p, box.footprint(), direction=(1.0, 0.35), length=16, strength=0.7)
        fx.wood_box(p, box, WOOD, seed=29)
    except Exception as exc:                                              # a module of the shop may be mid-edit
        print("no Cuboid:", exc)
    fx.wall_shadow(p, (360, 268, 60, 40), offset=(3, 4))
    fx.wood_fill(p, (360, 268, 60, 40), "h", WOOD, seed=30, board=10)
    fx.wear(p, (360, 268, 60, 40), 0.6)
    fx.paper_fill(p, (440, 262, 52, 40), folds=(1, 1), curl=("tr",), shadow=True, seed=31)
    fx.cloth_fill(p, (510, 262, 60, 36), WINE, "wool", folds=4, stitch="b", seed=32)
    fx.rope(p, fx.hang_curve((580, 262), (632, 300), 10), 4, seed=33, fray=(False, True))
    return p.im


def compose(out: Path) -> None:
    b = board()
    b.save(out / "board_1x.png")
    big = b.resize((W * 2, H * 2), Image.NEAREST)
    full = out / "full.png"
    if full.exists():
        f = Image.open(full).convert("RGBA")
        counter = f.crop((200, 262, 520, 345)).resize((960, 249), Image.NEAREST)
        cask = f.crop((628, 336, 790, 528)).resize((486, 576), Image.NEAREST)
        ref = Image.new("RGBA", (1280, 249 + 576 + 8), (24, 20, 22, 255))
        ref.paste(counter, (0, 0))
        ref.paste(cask, (0, 257))
        ref.save(out / "ref.png")
        sheet = Image.new("RGBA", (1280, 720 + ref.height), (24, 20, 22, 255))
        sheet.paste(big, (0, 0))
        sheet.paste(ref, (0, 720))
        sheet.save(out / "board.png")
    else:
        big.save(out / "board.png")


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ.get("TEMP", ".")) / "fxkit"
    folder.mkdir(parents=True, exist_ok=True)
    compose(folder)
    print("wrote", folder / "board.png")
