"""Draws one bust from a `Look`: layers in the order a painter would lay them, then a dark rim and the crop.

Order: hair behind, neck, garment, body extras, ears, face, beard, face covering, hair, headwear, face marks, rim.
The faces, hair, hats and clothes live in the `pface_*` and `pbody_*` modules.
"""

from __future__ import annotations

import random

from PIL import Image

from pbody_core import Ctx, torso_mask
from pbody_wear import GARMENTS
from pface_extras import body_extras, face_marks
from pface_hair import back_hair, front_hair, over_body
from pface_head import CX, draw_beard, draw_ears, draw_face, draw_neck, geo
from pface_wear import draw_headwear, face_cover
from people_kit import CH, H, W, hx, outline_all
from people_look import Look
from pix import Pix


def render(look: Look) -> Image.Image:
    """The bust of `look` on a transparent 288x211 frame."""
    p = Pix(W, CH, seed=look.seed)
    g = geo(look)
    main, second, trim = hx(look.main), hx(look.second or look.main), hx(look.trim)
    wear = hx(look.head_col or look.main)
    sw = look.sw + (3 if look.build == 2 else -3 if look.build == 0 else 0)
    nk = look.neck + 1
    yn = g.chin + 6
    back_hair(p, look, g)
    draw_neck(p, look, g)
    lone = Pix(W, CH)
    draw_neck(lone, look, g)
    only_neck = lone.im
    c = Ctx(p, look, g, torso_mask(sw, yn, nk), main, second, trim, sw, yn, nk, random.Random(look.seed * 3 + 11), only_neck)
    GARMENTS[look.outfit](c)
    body_extras(c)
    over_body(p, look, g)
    if look.hair not in ("long", "bob", "frizz", "curly", "mop") and look.headwear not in ("coif", "bonnet", "hood"):
        draw_ears(p, look, g)
    draw_face(p, look, g)
    draw_beard(p, look, g)
    if look.face:
        face_cover(p, look, g, wear)
    front_hair(p, look, g)
    draw_headwear(p, look, g, wear, second, sw)
    face_marks(p, look, g)
    outline_all(p)
    return p.im.crop((0, 0, W, H))
