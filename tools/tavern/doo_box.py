"""`reputation_box` (0,264)-(40,367): the tavern's suggestion and alms chest, bolted to the street door.

It is an oak box bound with iron, a slot with a brass lip for notes and coins, a brass lock and a parchment label.
It sits on the door plane (the plane that runs to VP at the left edge), so it is built like a real box in that plane:

  * a point at depth scale s (1 at the near end, falling toward VP) and offset d out of the door is at
    x = 480 + (d - 480) s,  y = 150 + (Y - 150) s;
  * the outer face (d = XN) is the long face turned to the room; its upright edges stay upright and its top and bottom
    edges run to VP;
  * the near end (d = 0..XN, s = 1) faces the viewer: a side face with level edges;
  * the lid overhangs and shows its top because the box is below the horizon;
  * two iron mounting lugs run from the far end onto the door and are nailed to the boards; the box throws its shadow
    on the door to the lower right, and the vertical door seams keep running behind it (the layer is clear around it).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from PIL import Image

from fxkit import brass_fill, contact_shadow, iron_fill, paper_fill, rivet, wear, wood_fill
from palette import BRASS, FLAME, IRON, OAK, PARCHMENT, SHADOW, WOOD
from pix import Pix, mix
from shopx_persp import VP

W, H = 960, 540
BBOX = (0, 264, 40, 367)
XN = 9                       # outward depth of the box from the door (width of the near end face)
S_END = 0.945                # depth scale of the far end of the box
Y_TOP, Y_BOT = 292, 362      # world height of the body's top and the bottom at the near end (door-plane y at s = 1)
LID = 12                     # lid band, near height
TW, TH = 72, 70 + LID        # the flat texture of the outer face (u across, v down), lid on top
BODY_V0 = LID


def proj(d: float, y: float, s: float) -> tuple[float, float]:
    return VP[0] + (d - VP[0]) * s, VP[1] + (y - VP[1]) * s


def face_pt(u: float, v: float) -> tuple[float, float]:
    """The outer face at u (0 near .. 1 far) and v in texture rows (0 top of the lid)."""
    s = 1 - (1 - S_END) * u
    return proj(XN, Y_TOP - LID + v, s)


def to_face(x: int, y: int) -> tuple[float, float]:
    """Inverse of face_pt: texture (tx, ty) for a screen pixel."""
    s = (x - VP[0]) / (XN - VP[0])
    yw = VP[1] + (y - VP[1]) / s
    return (1 - s) / (1 - S_END) * (TW - 1), yw - (Y_TOP - LID)


def poly_pts(pts: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(round(x), round(y)) for x, y in pts]


def fquad(u0: float, u1: float, v0: float, v1: float) -> list[tuple[int, int]]:
    """A rectangle of the face as a screen polygon (u 0..1, v in texture rows), edges following the perspective."""
    pts = [face_pt(u0, v0), face_pt(u1, v0), face_pt(u1, v1), face_pt(u0, v1)]
    return poly_pts(pts)


def fellipse(u: float, v: float, ru: float, rv: float, n: int = 28) -> list[tuple[int, int]]:
    return poly_pts([face_pt(u + ru * math.cos(2 * math.pi * i / n), v + rv * math.sin(2 * math.pi * i / n)) for i in range(n)])


def face_texture() -> Image.Image:
    """The outer face laid flat: three vertical oak boards (so the planks run the way the door's do), a lid band with
    its iron rim, two iron bands, a darker foot. Light comes from the upper left, so the near edge is lit."""
    t = Pix(TW, TH, seed=73)
    wood_fill(t, (0, 0, TW, TH), grain_dir="v", ramp=WOOD, board=22, joints=False, nails=False, knots=0.5,
              wear_amount=0.5, damp=0.2, damp_from="bottom", light=0.5, bias=0.6, seed=8)
    # the lid is one thick plank with its grain along the box
    wood_fill(t, (0, 0, TW, LID - 1), grain_dir="h", ramp=WOOD, board=11, joints=False, nails=False, knots=0.3,
              wear_amount=0.5, light=0.5, bias=0.5, seed=9)
    t.hline(0, 0, TW, WOOD[4])
    t.hline(0, LID - 1, TW, OAK[0])
    t.hline(0, LID, TW, OAK[0])                                  # the lid's shade on the body below it
    t.hline(0, LID + 1, TW, OAK[1])
    for x in range(TW):                                          # lid's overhang drops a dithered shade
        for y in range(LID + 2, LID + 5):
            if (x + y) % 2 == 0 or y == LID + 2:
                r, g, b, a = t.get(x, y)
                t.px(x, y, (*mix((r, g, b), SHADOW[:3], 0.45), a))
    for bx in (23, 47):                                          # seams between the boards
        t.vline(bx, LID, TH - LID, WOOD[0])
        t.vline(bx + 1, LID, TH - LID, WOOD[4])
    # iron bands up the body, over the lid's edge: lit left, dark right
    for x0 in (3, 62):
        iron_fill(t, (x0, 0, 7, TH), hammer=0.7, rust=0.35, seed=x0)
        t.vline(x0 + 6, 0, TH, IRON[0])
    return t.finish()


def draw_face(p: Pix, tex: Image.Image) -> None:
    """Projects the flat texture on the outer face by inverse mapping."""
    quad = fquad(0, 1, 0, TH)
    from PIL import ImageDraw
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(quad, fill=255)
    for y in range(H):
        for x in range(0, 60):
            if not m.getpixel((x, y)):
                continue
            tx, ty = to_face(x, y)
            if 0 <= ty < TH and 0 <= tx <= TW:
                p.px(x, y, tex.getpixel((min(TW - 1, int(tx + 0.5)), min(TH - 1, int(ty)))))


def side_face(p: Pix) -> None:
    """The near end of the box, turned to the viewer: boards with level edges, the lid end, an iron corner strap."""
    top = Y_TOP - LID
    wood_fill(p, (0, top + 1, XN, Y_BOT - top - 1), grain_dir="v", ramp=WOOD, board=8, joints=False, nails=False,
              knots=0, wear_amount=0.3, light=0.6, bias=0.2, seed=12)
    for x in range(XN):                                          # the lid's end grain: pale, ringed
        p.px(x, top, WOOD[4])
        for y in range(top + 1, top + LID - 1):
            p.px(x, y, WOOD[3] if (x + y) % 3 else WOOD[2])
        p.px(x, top + LID - 1, OAK[0])
        p.px(x, top + LID, OAK[1])
    p.vline(XN - 1, top + 1, Y_BOT - top - 1, OAK[0])            # the corner where it meets the outer face
    p.hline(0, Y_BOT - 1, XN, OAK[0])
    iron_fill(p, (0, Y_BOT - 14, XN - 1, 6), hammer=0.4, rust=0.3, seed=2)       # a strap round the foot, riveted
    rivet(p, 3, Y_BOT - 11, 1, BRASS)
    iron_fill(p, (0, Y_TOP + 12, XN - 1, 6), hammer=0.4, rust=0.3, seed=3)
    rivet(p, 3, Y_TOP + 15, 1, BRASS)


def lid_top(p: Pix) -> None:
    """The top of the lid, seen from above: a band that narrows toward VP, with the boards running along the box and
    two iron hinge leaves at the back (door side), riveted."""
    top = Y_TOP - LID
    a0, a1 = proj(0, top, 1.0), proj(XN, top, 1.0)
    b0, b1 = proj(0, top, S_END), proj(XN, top, S_END)       # d = 0 is the door plane
    quad = poly_pts([a0, a1, b1, b0])
    # far end of the door plane edge: (0,..) at s = 1 is x=0; at s=S_END the door plane edge sits further right
    wood_fill(p, quad, grain_dir="h", ramp=WOOD, board=4, joints=False, nails=False, knots=0, wear_amount=0.3,
              light=0.5, bias=1.3, seed=14)
    p.line(*poly_pts([a0])[0], *poly_pts([a1])[0], WOOD[4])
    p.line(*poly_pts([a1])[0], *poly_pts([b1])[0], OAK[1])
    for t in (0.22, 0.7):                                    # hinge leaves on the top, and a rivet in each
        x = a0[0] + (b0[0] - a0[0]) * t + 2
        y = a0[1] + (b0[1] - a0[1]) * t + 1
        iron_fill(p, (round(x), round(y), 4, 2), hammer=0.1, rust=0.2, seed=int(t * 10))
        p.px(round(x) + 1, round(y), BRASS[3])


def lugs_and_shadow(p: Pix) -> None:
    """Shadow on the door first (it falls right and down), then the mounting lugs fixed to the door boards."""
    top = Y_TOP - LID
    silhouette = [proj(0, top, 1.0), proj(XN, top, 1.0), proj(XN, top, S_END), proj(XN, Y_BOT, S_END), proj(XN, Y_BOT, 1.0),
                  proj(0, Y_BOT, 1.0)]
    contact_shadow(p, poly_pts(silhouette), shift=(5, 4), spread=5, strength=1.0, alpha=215, squash=0.9)
    contact_shadow(p, poly_pts(silhouette), shift=(1, 2), spread=2, strength=1.0, alpha=230, squash=0.9)
    # lugs: flat strips on the door plane (offset 0) running from the box's far end onward, edges to VP
    for yw in (Y_TOP + 6, Y_BOT - 14):
        xs = range(round(proj(XN, yw, S_END)[0]) - 1, 40)
        pts_top = [(x, round(VP[1] + (yw - VP[1]) * (VP[0] - x) / VP[0])) for x in xs]
        pts_bot = [(x, round(VP[1] + (yw + 7 - VP[1]) * (VP[0] - x) / VP[0])) for x in reversed(list(xs))]
        poly = pts_top + pts_bot
        contact_shadow(p, poly, shift=(2, 3), spread=2, strength=1.0, alpha=220)
        iron_fill(p, poly, hammer=0.5, rust=0.3, seed=yw)
        xr = pts_top[-3][0]
        rivet(p, xr, pts_top[-3][1] + 3, 1, BRASS)


def furniture(p: Pix) -> None:
    """Everything fixed on the outer face, placed in face coordinates so it follows the perspective."""
    # brass slot plate with the slit and its lit lip (the lower lip catches the lamp)
    plate = fquad(0.22, 0.78, 22, 34)
    contact_shadow(p, plate, shift=(1, 2), spread=2, strength=1.0, alpha=220)
    brass_fill(p, plate, profile="plate", tarnish=0.45, seed=15)
    slit = fquad(0.3, 0.7, 26.5, 29.5)
    p.poly(slit, SHADOW)
    for i in range(0, 1):
        a, b = face_pt(0.3, 29.5), face_pt(0.7, 29.5)
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), BRASS[4])          # the lit lower lip
        a, b = face_pt(0.3, 26), face_pt(0.7, 26)
        p.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), BRASS[0])
    for u in (0.24, 0.76):
        x, y = face_pt(u, 30)
        p.px(round(x), round(y), BRASS[4])
        p.px(round(x), round(y) + 1, BRASS[0])
    # parchment label held by two nails; tiny ink lines (a letter 'S' for suggestions, a coin)
    lab = fquad(0.24, 0.76, 38, 52)
    contact_shadow(p, lab, shift=(1, 2), spread=2, strength=1.0, alpha=200)
    paper_fill(p, lab, ramp=PARCHMENT, folds=(0, 0), stains=0.3, foxing=0.3, shadow=False, seed=16)
    for i, (a, b) in enumerate(((0.3, 0.68), (0.3, 0.6), (0.3, 0.66))):
        x0, y0 = face_pt(a, 41 + i * 3.4)
        x1, y1 = face_pt(b, 41 + i * 3.4)
        p.line(round(x0), round(y0), round(x1), round(y1), PARCHMENT[0])
    for u, v in ((0.28, 39), (0.72, 39)):
        x, y = face_pt(u, v)
        p.px(round(x), round(y), IRON[4])
    # brass lock plate with a keyhole
    lock = fquad(0.34, 0.68, 57, 69)
    contact_shadow(p, lock, shift=(1, 2), spread=2, strength=1.0, alpha=220)
    brass_fill(p, lock, profile="plate", tarnish=0.4, seed=19)
    x, y = face_pt(0.51, 60)
    p.ellipse(round(x) - 1, round(y) - 1, 3, 3, SHADOW)
    p.px(round(x), round(y) + 2, SHADOW)
    p.px(round(x), round(y) + 3, SHADOW)
    p.px(round(x) - 1, round(y) - 1, BRASS[4])
    # bolts through the bands (square-headed, brass)
    for u in (0.11, 0.915):
        for v in (24, 48, 66):
            x, y = face_pt(u, v)
            rivet(p, round(x), round(y), 1, BRASS)
    for u in (0.11, 0.915):                                   # and through the lid rim
        x, y = face_pt(u, 5)
        rivet(p, round(x), round(y), 1, BRASS)


def draw() -> Image.Image:
    p = Pix(W, H, seed=71)
    lugs_and_shadow(p)
    side_face(p)
    draw_face(p, face_texture())
    furniture(p)
    lid_top(p)
    # the lit near edge of the outer face and the dark far edge
    for y in range(H):
        for x in range(8, 40):
            pass
    wear(p, [(0, 270), (40, 270), (40, 365), (0, 365)], amount=0.15, kinds=("scratch", "dust"), seed=7)
    p.clip(poly_pts([(0, 264), (40, 264), (40, 367), (0, 367)]))
    return p.finish()


ASSETS: Mapping[str, Callable[[], Image.Image]] = {"reputation_box.960x540.png": draw}
