# tools/tavern: the medieval-tavern pack, drawn by code

The pictures of the pack (`Textures/`) are not painted in an editor; they are made by Python from a palette, a few
materials and a seed, so the same code always draws the same picture. The drawing modules read nothing of the game's art:
the only things taken from the game are numbers (`layout.tsv`: each picture's size, where its content sits, its nine-slice
border). The one exception is the characters (see below), which are the game's own pictures edited with parts drawn here.

## The whole pack

Most pictures are drawn from code alone. The 76 busts and the 11 passer-by sheets are made differently: the game's own
pictures are edited with the overlay parts of `tools/overlay` (hats, clothes and make-up, all drawn from scratch), which keeps the
faces and the lighting of the game's art. The publisher has said such edits and their publication are allowed.

```
tools/tavern/make_pack.sh <exports>      # <exports>: what the kit's export script wrote from your own copy of the game
```

It draws everything, then runs `tools/overlay/compose_busts.py` and `tools/overlay/walkers/compose_walkers.py` into the
same folder. Without the export, `python tools/tavern/build.py` alone draws all of those 87 pictures from code as well.

## Building and looking

```
python tools/tavern/build.py                         # draws everything into Textures/
python tools/tavern/build.py --only wall,desk        # only pictures whose file name contains one of these
python tools/tavern/sheet.py <folder> out.png        # a labelled grid of a folder of PNGs
python tools/tavern/sheet.py <folder> out.png --against <originals>   # each picture beside the game's
# the shop view, game above pack: the preview of the Texture Packs repository (tools/preview/preview.py there)
python <Texture Packs>/tools/preview/preview.py "<game>" --pack Textures --compare
```

`layout.tsv` is made by `python tools/tavern/facts.py "<game>"` and committed; it needs the game only to be remade.

## The code

| File | What it holds |
| --- | --- |
| `pix.py` | `Pix`, a canvas with hard-edged shapes, ordered dithering, glow, outline, clipping |
| `palette.py` | the colours: one ramp per material, dark to light |
| `materials.py` | boards, beams, masonry, plaster, iron straps, the shade under an edge |
| `font.py` | a 5x7 alphabet for lettering on signs and labels |
| `shop.py`, ... | drawing modules; each lists its pictures in `ASSETS` |
| `build.py` | finds every module with `ASSETS`, checks names and sizes against `catalog.tsv`, writes the PNGs |

A drawing module defines `ASSETS: Mapping[str, Callable[[], Image.Image]]`, keyed by the file name in `catalog.tsv`
(`wall.960x540.png`). A function takes nothing and returns an RGBA image of exactly the catalog's size. Seed the `Pix`
(`Pix(w, h, seed=n)`) so the picture does not change between builds. A name the catalog does not have, or a wrong size,
stops the build, and two modules may not draw the same file.

## The look

A timber-framed tavern at night, lit by lanterns and a hearth. One palette for all of it.

- **Materials:** oak and pale wood, black iron with brass rivets, limewashed plaster stained with soot, rough stone,
  leather, linen, wine-red and moss-green cloth, parchment, glass in lead.
- **Light:** from the upper left and from lamps. Shadows are warm, deep brown that is nearly violet (`SHADOW`), never
  black; highlights are amber (`FLAME`), never white.
- **Pixels:** whole pixels only, no anti-aliasing. Shade with the ramps and with ordered dither (`Pix.dither`), not with
  smooth gradients. Edges facing the light get the lighter tone, edges facing away the darker. Outline shapes that must
  stand out on a busy ground with `SHADOW`.
- **Placement:** a scene-sized layer (960x540) keeps to the rectangle the game's layer fills (`bbox` in `layout.tsv`);
  things that sit on the bar sit on its top plane. Nine-slice pictures keep their corners within `border`. A sprite
  sheet keeps its frames where the game's are.
- **No game art in the drawing modules:** draw from your own composition. Looking at the originals to understand a layout is fine; copying their
  pixels, or tracing them, is not. (Only the characters are edited from the game's own pictures, by `tools/overlay`.) Do not redraw third-party logos (Steam, Discord) or the game's title logo.

## What is drawn

1831 of the catalog's 1835 pictures. A picture that is not drawn stays the game's own. `python tools/tavern/build.py`
prints the count, and the list is in `ASSETS` of each module.

| Part of the catalog | Drawn | Module |
| --- | --- | --- |
| `scene/shop-structure` (wall, bar, window, shutter, door, lamp, back room) | 19 of 19 | `shop.py`, `backroom.py` |
| `scene/fixtures` (almanac, bell, poster, lectern, cabinets, casks, chests) | 50 of 50 | `props.py` |
| `scene/animation` (queue board, music box, walkers) | 21 of 21 | `props.py`, `people_walk.py` |
| `scene/illustrations` (the title picture, a taproom, a night market) | 4 of 4 | `menu_scene.py`, `menu_places.py` |
| `scene/backgrounds` | 6 of 6 | `shop.py`, `perksui_bg.py` |
| `character/people` (about 50 busts, strips of townsfolk) | 80 of 80 | `people*.py` |
| `ui/main-menu` | 116 of 120 (not the title logo or the Steam and Discord pictures) | `menu_ui.py`, `menu_kit.py`, `perksui_*` |
| `ui/in-game` | 229 of 229 | `ingame_ui.py`, `ingame_icons.py`, `perksui_*`, `bow_art.py`, `propsx_calendar.py` |
| `ui/window-elements` (the tiles every window is built from) | 128 of 128 | `windows.py` |
| `new-game` (perk screen, shared, specializations) | 54 of 54, with the 37 perk icons | `menu_newgame.py`, `perks_ui.py` |
| `item/*` (958 atlas sprites, appraisal pictures, opened tools) | all | `items_*`, `appraisal_*` |

Left undrawn on purpose: the game's title logo and third-party logos (Steam, Discord), four pictures. The shotgun is a bow here (`bow_art.py`, `people_misc.py`), and the calendar a blank-paged book.
The preview (`tools/preview/preview.py` in the Texture Packs repository) shows the shop view only, so the rest is judged on contact sheets.
