#!/usr/bin/env bash
# Makes the whole Medieval Tavern pack: draws every picture from code, then lays the official-based characters over it.
#   tools/tavern/make_pack.sh <exports> [out]
# <exports> is the folder the kit's export script wrote from your own copy of the game (it holds character/people and
# scene/animation). The busts and the passers-by are made by editing those pictures with the overlay parts of
# tools/overlay (hats, clothes, make-up, all drawn from scratch); every other picture is drawn from code alone.
# <out> defaults to Textures (the pack folder at the repository root).
set -euo pipefail
cd "$(dirname "$0")/../.."
exports=${1:?usage: tools/tavern/make_pack.sh <exports> [out]}
out=${2:-Textures}
mkdir -p "$out" && out=$(cd "$out" && pwd)        # the walkers composer runs from its own folder, so give it a full path
python tools/tavern/build.py --out "$out"
python tools/overlay/compose_busts.py --originals "$exports/character/people" --out "$out"
( cd tools/overlay/walkers && python compose_walkers.py --originals "$exports/scene/animation" --out "$out" )
