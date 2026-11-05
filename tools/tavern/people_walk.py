"""Walking silhouettes: the far and mid crowd walkers and the large walker, as dark figures in four or eight frames.

One small skeleton (pelvis, thigh/shin/foot, upper arm/forearm, torso lean, head) is posed from a gait phase, and each
kind of passer-by dresses it: tapered limbs, a coat, cloak or tunic drawn over them, and a hat. The figure is painted at
a higher resolution into a tone map (far-side shade, body, lit cue) and reduced to whole pixels, so the outline is round
and the small cues (hat band, strap, hood rim, beak, lantern) read as a lighter or darker tone inside the silhouette.
The far walkers are the same people re-rendered at a quarter size with thin parts widened, so detail still reads.
Figures face right and stand on the same ground line as the game's originals.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from PIL import Image, ImageDraw

Pt = tuple[float, float]
Colour = tuple[int, int, int, int]

# Tone indices on the painted map: 0 none, 1 shade (far side, folds), 2 body, 3 lit cue.
SHADE, BODY, LIT = 1, 2, 3
CROWD: Final[tuple[Colour, Colour, Colour]] = ((27, 22, 37, 255), (41, 34, 52, 255), (72, 61, 92, 255))
BIG: Final[tuple[Colour, Colour, Colour]] = ((60, 33, 56, 255), (84, 47, 77, 255), (122, 76, 110, 255))
GROUND: Final[Colour] = (41, 34, 52, 90)

THIGH, SHIN, ANKLE = 24.0, 23.0, 5.0          # leg bones in local units (about 100 units from sole to crown)


def rad(deg: float) -> float:
    return math.radians(deg)


def chaikin(pts: Sequence[Pt], rounds: int = 2, closed: bool = True) -> list[Pt]:
    """Corner cutting: turns a coarse outline into a smooth, organic one."""
    cur = list(pts)
    for _ in range(rounds):
        nxt: list[Pt] = [] if closed else [cur[0]]
        n = len(cur)
        for i in range(n if closed else n - 1):
            a, b = cur[i], cur[(i + 1) % n]
            nxt.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            nxt.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            nxt.append(cur[-1])
        cur = nxt
    return cur


class Art:
    """A tone map painted in local units (x forward, y up from the ground) and reduced to pixels."""

    def __init__(self, size: tuple[int, int], origin: Pt, scale: float, ss: int, min_px: float = 0.0) -> None:
        self.size, self.ss = size, ss
        self.img = Image.new("L", (size[0] * ss, size[1] * ss), 0)
        self.d = ImageDraw.Draw(self.img)
        self.ox, self.oy, self.s = origin[0], origin[1], scale
        self.min_u = min_px / scale                 # thinnest part that must still show at this size

    def at(self, p: Pt) -> tuple[float, float]:
        return (self.ox + p[0] * self.s) * self.ss, (self.oy - p[1] * self.s) * self.ss

    def poly(self, pts: Sequence[Pt], tone: int = BODY) -> None:
        self.d.polygon([self.at(p) for p in pts], fill=tone)

    def smooth(self, pts: Sequence[Pt], tone: int = BODY, rounds: int = 2) -> None:
        self.poly(chaikin(pts, rounds), tone)

    def disc(self, c: Pt, r: float, tone: int = BODY) -> None:
        if tone != LIT:
            r = max(r, self.min_u / 2)
        x, y = self.at(c)
        rr = r * self.s * self.ss
        self.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=tone)

    def ell(self, c: Pt, rx: float, ry: float, tone: int = BODY) -> None:
        x, y = self.at(c)
        self.d.ellipse((x - rx * self.s * self.ss, y - ry * self.s * self.ss, x + rx * self.s * self.ss, y + ry * self.s * self.ss), fill=tone)

    def cap(self, a: Pt, ra: float, b: Pt, rb: float, tone: int = BODY) -> None:
        """A tapered, rounded limb segment from a (radius ra) to b (radius rb)."""
        if tone != LIT:
            ra, rb = max(ra, self.min_u / 2), max(rb, self.min_u / 2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        self.poly([(a[0] + nx * ra, a[1] + ny * ra), (b[0] + nx * rb, b[1] + ny * rb),
                   (b[0] - nx * rb, b[1] - ny * rb), (a[0] - nx * ra, a[1] - ny * ra)], tone)
        self.disc(a, ra, tone)
        self.disc(b, rb, tone)

    def line(self, a: Pt, b: Pt, w: float, tone: int) -> None:
        self.cap(a, w / 2, b, w / 2, tone)

    def reduce(self, thr: float, lit_bias: float = 1.4, floor: int | None = None) -> list[list[int]]:
        """Whole-pixel tone map: a pixel is solid where enough of it was painted, with the tone that covers most of it."""
        w, h = self.size
        covers = []
        for t in (SHADE, BODY, LIT):
            covers.append(list(self.img.point(lambda v, t=t: 255 if v == t else 0).resize(self.size, Image.Resampling.BOX).getdata()))
        solid = list(self.img.point(lambda v: 255 if v else 0).resize(self.size, Image.Resampling.BOX).getdata())
        out = [[0] * w for _ in range(h)]
        lim = thr * 255
        for i in range(w * (h if floor is None else min(h, floor))):
            if solid[i] >= lim:
                c = (covers[0][i], covers[1][i] * 1.15, covers[2][i] * lit_bias)     # slightly favour the body tone so cues stay crisp
                out[i // w][i % w] = 1 + c.index(max(c))
        return out


# --------------------------------------------------------------------------------------------------------- skeleton

@dataclass
class Leg:
    hip: Pt
    knee: Pt
    ankle: Pt
    foot: list[Pt]            # sole outline: heel, toe, ball, instep, in absolute units


def leg_pose(theta: float, hip: Pt, long: float = 1.0) -> Leg:
    """One leg at gait phase theta (0 = this leg leads at heel strike, pi = it trails and is about to push off)."""
    c, s = math.cos(theta), math.sin(theta)
    swing = max(0.0, -s)
    thigh = rad(27 * c + 3 + 12 * swing)
    flex = rad(5 + 52 * swing ** 1.3 + 26 * max(0.0, -c) * max(0.0, s))
    shin = thigh - flex
    t1, t2 = THIGH * long, SHIN * long
    knee = (hip[0] + t1 * math.sin(thigh), hip[1] - t1 * math.cos(thigh))
    ankle = (knee[0] + t2 * math.sin(shin), knee[1] - t2 * math.cos(shin))
    fa = rad(14 * max(0.0, c) ** 2 - 36 * max(0.0, -c) ** 2 - 18 * swing)       # toe up at the strike, toe down at the push
    ca, sa = math.cos(fa), math.sin(fa)
    local = [(-4.5, -ANKLE), (9.5, -ANKLE), (13.0, -ANKLE + 3.2), (9.0, -ANKLE + 6.2), (3.5, 1.5), (-3.0, 2.0), (-5.0, -ANKLE + 4.0)]
    foot = [(ankle[0] + x * ca - y * sa, ankle[1] + x * sa + y * ca) for x, y in local]
    return Leg(hip, knee, ankle, foot)


@dataclass
class Pose:
    near: Leg
    far: Leg
    hip: Pt
    shoulder: Pt
    neck: Pt
    head: Pt
    arm_near: tuple[Pt, Pt, Pt]
    arm_far: tuple[Pt, Pt, Pt]
    sway_f: float             # how far the leading knee reaches (cloth swings with it)
    sway_b: float             # how far the trailing knee goes back
    phase: float


def arm_pose(shoulder: Pt, theta: float, amp: float, up: float = 21.0, fore: float = 19.0) -> tuple[Pt, Pt, Pt]:
    """Shoulder-elbow-hand of an arm swinging with phase theta (forward when theta is pi)."""
    a = rad(-amp * math.cos(theta))
    bend = rad(10 + 18 * max(0.0, -math.cos(theta)))
    elbow = (shoulder[0] + up * math.sin(a), shoulder[1] - up * math.cos(a))
    hand = (elbow[0] + fore * math.sin(a + bend), elbow[1] - fore * math.cos(a + bend))
    return shoulder, elbow, hand


def make_pose(theta: float, long: float = 1.0, torso: float = 30.0, lean: float = 5.0, amp: float = 26.0) -> Pose:
    near0 = leg_pose(theta, (0.0, 0.0), long)
    far0 = leg_pose(theta + math.pi, (0.0, 0.0), long)
    low = min(min(p[1] for p in near0.foot), min(p[1] for p in far0.foot))
    hip = (0.0, -low)                                           # lower the pelvis until the lowest foot is on the ground
    near, far = leg_pose(theta, hip, long), leg_pose(theta + math.pi, hip, long)
    tl = rad(lean + 1.5 * math.cos(2 * theta))
    sh = (hip[0] + torso * math.sin(tl) + 1.0, hip[1] + torso * math.cos(tl))
    neck = (sh[0] + 2.0, sh[1] + 4.0)
    head = (sh[0] + 4.5, sh[1] + 13.0 + 0.6 * math.cos(2 * theta))
    return Pose(near, far, hip, sh, neck, head, arm_pose(sh, theta, amp), arm_pose(sh, theta + math.pi, amp),
                max(near.knee[0], far.knee[0]) - hip[0], min(near.knee[0], far.knee[0]) - hip[0], theta)


# ----------------------------------------------------------------------------------------------------------- pieces

def legs(a: Art, p: Pose, trouser: int, boot: int = BODY, r: tuple[float, float, float] = (6.6, 5.0, 3.6),
         cuff: float = 0.0, bare_above: float = 0.0) -> None:
    """Both legs: tapered thigh and calf under the clothes, and a boot with a heel and a toe cap."""
    for leg, tone in ((p.far, SHADE), (p.near, trouser)):
        a.cap(leg.hip, r[0], leg.knee, r[1], tone)
        a.cap(leg.knee, r[1], leg.ankle, r[2], tone)
        if cuff:
            a.cap(leg.ankle, r[2] + cuff, ((leg.ankle[0] + leg.knee[0]) / 2, (leg.ankle[1] + leg.knee[1]) / 2 - 2), r[2] + cuff * 0.4, tone)
        a.smooth(leg.foot, SHADE if tone == SHADE else boot, 1)


def arm(a: Art, joints: tuple[Pt, Pt, Pt], tone: int, ru: float = 4.3, rf: float = 3.5, edge: bool = True,
        sleeve_end: float = 1.0) -> None:
    """An arm drawn over the clothes; a shade outline separates it from the body it crosses."""
    s, e, h = joints
    if edge and tone != SHADE:
        a.cap(s, ru + 1.1, e, rf + 1.1, SHADE)
        a.cap(e, rf + 1.1, h, rf * 0.8 + 1.0, SHADE)
    a.cap(s, ru, e, rf, tone)
    a.cap(e, rf, h, rf * 0.8 * sleeve_end, tone)
    a.disc(h, 3.1, tone if tone == SHADE else BODY)


def head_bare(a: Art, p: Pose, tone: int = BODY, face: float = 1.0) -> None:
    """Neck, skull, jaw and the nose in profile."""
    c = p.head
    a.cap((p.shoulder[0] + 1.0, p.shoulder[1] + 1.0), 4.4, (c[0] - 1.0, c[1] - 6.0), 3.7, tone)
    a.ell(c, 8.2, 9.6, tone)
    a.disc((c[0] + 4.0, c[1] - 6.0), 3.9, tone)                                     # jaw
    a.poly([(c[0] + 6.2, c[1] + 2.8), (c[0] + 11.0 * face, c[1] - 1.6), (c[0] + 7.0, c[1] - 3.8)], tone)   # nose


def torso_body(a: Art, p: Pose, tone: int, belly: float = 0.0, back: float = 0.0) -> None:
    """The bare torso volume: chest, waist and seat."""
    s, h = p.shoulder, p.hip
    a.smooth([(s[0] - 5, s[1] + 2), (s[0] - 9.5 - back, s[1] - 9), (h[0] - 9, h[1] + 4), (h[0] - 8.5, h[1] - 4), (h[0] + 5, h[1] - 6),
              (h[0] + 9.5 + belly, h[1] + 8), (s[0] + 9.5, s[1] - 12), (s[0] + 6, s[1] + 1)], tone)


def hem_poly(p: Pose, top_back: Pt, top_front: Pt, drop: float, wb: float, wf: float, k: float = 0.55, lift: float = 3.0) -> list[Pt]:
    """Outline of a hanging garment: shoulders to a hem that swings with the knees."""
    h = p.hip
    hb = (h[0] - wb + k * p.sway_b, h[1] - drop + lift)
    hf = (h[0] + wf + k * p.sway_f, h[1] - drop + lift * 0.4)
    hm = ((hb[0] + hf[0]) / 2, h[1] - drop - 1.0)
    s = p.shoulder
    return [top_back, (s[0] - 11, s[1] - 12), (h[0] - 10, h[1] + 2), hb, hm, hf, (h[0] + 11.5, h[1] + 2), (s[0] + 10.5, s[1] - 11), top_front]


# --------------------------------------------------------------------------------------------------------- hats

def felt_hat(a: Art, c: Pt, sway: float) -> None:
    a.smooth([(c[0] - 8.5, c[1] + 4), (c[0] - 7.5, c[1] + 13), (c[0] - 2, c[1] + 16), (c[0] + 5, c[1] + 14.5), (c[0] + 8.5, c[1] + 4)], BODY)
    a.cap((c[0] - 14, c[1] + 4.6), 1.5, (c[0] + 15.5, c[1] + 3.6), 1.5, BODY)             # the brim, a little down at the front
    a.ell((c[0] + 1, c[1] + 4.4), 15, 2.4, BODY)
    a.line((c[0] - 8, c[1] + 6.6), (c[0] + 8.2, c[1] + 6.8), 2.2, LIT)                    # hat band
    a.cap((c[0] - 5, c[1] + 8), 1.5, (c[0] - 12, c[1] + 14 + sway * 0.4), 0.8, LIT)       # a feather


def floppy_cap(a: Art, c: Pt, sway: float) -> None:
    """A coif under a floppy cap whose tail flops behind the head."""
    a.ell((c[0] - 0.8, c[1] + 0.8), 8.8, 9.9, BODY)                                       # coif
    a.smooth([(c[0] + 8.2, c[1] + 4.5), (c[0] + 6, c[1] + 11), (c[0], c[1] + 15.5), (c[0] - 7, c[1] + 14), (c[0] - 14 - sway, c[1] + 7),
              (c[0] - 21 - sway, c[1] - 3 + sway * 0.4), (c[0] - 14.5 - sway, c[1] + 2), (c[0] - 9, c[1] + 4), (c[0] + 1, c[1] + 4.2)], BODY)
    a.line((c[0] - 7.5, c[1] + 4.6), (c[0] + 8.0, c[1] + 4.8), 2.4, LIT)                  # the cap's turned-up band
    a.line((c[0] - 8, c[1] - 3), (c[0] + 1, c[1] - 7), 1.6, LIT)                          # coif string under the jaw


def kerchief(a: Art, p: Pose, sway: float) -> None:
    """A neckerchief with two knot tails fluttering behind."""
    c, s = p.head, p.shoulder
    a.cap((s[0] + 2.2, s[1] + 3), 4.8, (c[0] - 0.5, c[1] - 6), 4.0, LIT)
    a.poly([(c[0] - 4, c[1] - 6), (c[0] - 12 - sway, c[1] - 6 + sway * 0.6), (c[0] - 10, c[1] - 10), (c[0] - 3, c[1] - 8.5)], LIT)
    a.poly([(c[0] - 4, c[1] - 7), (c[0] - 10 - sway, c[1] - 13 + sway), (c[0] - 7, c[1] - 14), (c[0] - 2, c[1] - 9)], LIT)


def wide_brim(a: Art, c: Pt) -> None:
    a.smooth([(c[0] - 7.5, c[1] + 5), (c[0] - 7, c[1] + 15), (c[0] - 2, c[1] + 17.5), (c[0] + 5.5, c[1] + 16), (c[0] + 7.5, c[1] + 5)], BODY)
    a.ell((c[0] + 0.5, c[1] + 5.2), 19, 3.0, BODY)
    a.poly([(c[0] - 19, c[1] + 5), (c[0] - 12, c[1] + 6.6), (c[0] - 12, c[1] + 4.2)], BODY)
    a.line((c[0] - 7.4, c[1] + 7.3), (c[0] + 7.4, c[1] + 7.5), 2.0, LIT)
    a.line((c[0] + 19, c[1] + 4.6), (c[0] + 7, c[1] + 6.6), 0.9, LIT)                     # lit upper edge of the brim


def beak_mask(a: Art, c: Pt) -> None:
    """A plague doctor's mask: a curved beak and a round lens; the hood falls behind."""
    a.smooth([(c[0] + 5.5, c[1] + 4.5), (c[0] + 11, c[1] + 1.5), (c[0] + 19, c[1] - 4), (c[0] + 25, c[1] - 11.5), (c[0] + 19.5, c[1] - 11.5),
              (c[0] + 11, c[1] - 7.5), (c[0] + 4.5, c[1] - 6)], BODY, 2)
    a.cap((c[0] + 9, c[1] + 2.3), 0.5, (c[0] + 22, c[1] - 8.6), 0.5, LIT)                 # shine along the top of the beak
    a.disc((c[0] + 3.2, c[1] + 2.3), 2.7, LIT)                                            # lens
    a.disc((c[0] + 3.6, c[1] + 2.3), 1.3, SHADE)


def tricorne(a: Art, c: Pt) -> None:
    a.smooth([(c[0] - 15, c[1] + 10.5), (c[0] - 10, c[1] + 5.5), (c[0] + 0, c[1] + 4.0), (c[0] + 10, c[1] + 5.5), (c[0] + 16, c[1] + 10),
              (c[0] + 11, c[1] + 10.5), (c[0] + 7, c[1] + 15.5), (c[0] - 6, c[1] + 15.5), (c[0] - 11, c[1] + 11.5)], BODY, 1)
    a.line((c[0] - 13.5, c[1] + 10.5), (c[0] - 9, c[1] + 8), 1.2, LIT)                      # the turned-up edges are lit
    a.line((c[0] + 14.5, c[1] + 10), (c[0] + 10, c[1] + 8), 1.2, LIT)
    a.line((c[0] - 6, c[1] + 6.6), (c[0] + 7, c[1] + 6.8), 1.6, LIT)


def hood(a: Art, p: Pose, sway: float) -> None:
    """A cloak's hood: a peaked cowl over the head, a shaded opening, a lit rim and a droop behind."""
    c = p.head
    a.smooth([(c[0] + 9.5, c[1] + 1), (c[0] + 8.2, c[1] + 9), (c[0] + 1, c[1] + 15.5), (c[0] - 8, c[1] + 14), (c[0] - 14 - sway, c[1] + 6),
              (c[0] - 16 - sway, c[1] - 3), (c[0] - 10, c[1] - 10), (c[0] - 2, c[1] - 9), (c[0] + 7, c[1] - 8)], BODY)
    a.ell((c[0] + 4.2, c[1] - 0.5), 5.8, 7.6, SHADE)                                      # the dark inside of the hood
    a.disc((c[0] + 8.5, c[1] - 1.2), 1.7, BODY)                                           # the nose tip shows as a notch of body tone
    a.cap((c[0] + 9.2, c[1] + 6.5), 0.9, (c[0] + 3, c[1] + 12.5), 0.9, LIT)               # lit edge of the cowl
    a.cap((c[0] + 3, c[1] + 12.5), 0.9, (c[0] - 6, c[1] + 12.5), 0.9, LIT)


# ------------------------------------------------------------------------------------------------------------ kinds

def dress_backpack(a: Art, p: Pose) -> None:
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    arm(a, p.arm_far, SHADE)
    legs(a, p, BODY, BODY, cuff=0.6)
    # the pack hangs behind: a satchel with a flap and a bedroll across the top, bobbing a little against the walk
    bob = 0.8 * math.cos(2 * p.phase)
    a.smooth([(s[0] - 9, s[1] + 3), (s[0] - 24, s[1] - 2 + bob), (s[0] - 26, s[1] - 22 + bob), (s[0] - 21, s[1] - 31 + bob), (s[0] - 9, s[1] - 29)], BODY)
    a.smooth([(s[0] - 11, s[1] - 15), (s[0] - 25, s[1] - 17 + bob), (s[0] - 24.5, s[1] - 30 + bob), (s[0] - 12, s[1] - 28)], SHADE, 1)
    a.line((s[0] - 24.5, s[1] - 22 + bob), (s[0] - 10, s[1] - 23), 1.4, LIT)               # buckled strap of the flap
    a.cap((s[0] - 23, s[1] + 0 + bob), 4.2, (s[0] - 9, s[1] + 1.5), 4.2, BODY)               # bedroll
    a.line((s[0] - 20, s[1] + 4.5 + bob), (s[0] - 20.5, s[1] - 4 + bob), 1.5, LIT)
    a.line((s[0] - 12, s[1] + 5.5), (s[0] - 12.4, s[1] - 3), 1.5, LIT)
    # tunic to mid-thigh with a belt, over the legs
    top_b, top_f = (s[0] - 5, s[1] + 2), (s[0] + 6, s[1] + 1)
    a.smooth(hem_poly(p, top_b, top_f, 15, 9.5, 11, 0.5, 2.0), BODY)
    a.line((h[0] - 10, h[1] + 7), (h[0] + 10.5, h[1] + 8), 2.4, LIT)                      # belt
    a.line((h[0] + 8.5, h[1] + 7.6), (h[0] + 8.7, h[1] + 3), 1.5, SHADE)                  # belt tail
    head_bare(a, p)
    felt_hat(a, c, sw * 2)
    # the walking stick, planted ahead and swinging with the near hand
    hand = p.arm_near[2]
    tip = (hand[0] + 12 + 5 * sw, 0.0)
    a.line((hand[0] - 2, hand[1] + 9), tip, 2.2, BODY)
    arm(a, p.arm_near, BODY)


def dress_bandana(a: Art, p: Pose) -> None:
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    arm(a, p.arm_far, SHADE)
    legs(a, p, BODY, BODY, r=(6.0, 4.6, 3.4))
    # a shirt, a leather jerkin and a short skirt of an apron
    a.smooth(hem_poly(p, (s[0] - 5, s[1] + 2), (s[0] + 6, s[1] + 1), 14, 9, 10.5, 0.45, 1.0), BODY)
    a.smooth([(h[0] + 7, h[1] + 4), (h[0] + 13.5, h[1] + 2), (h[0] + 14, h[1] - 6), (h[0] + 8, h[1] - 7)], LIT, 1)       # a belt pouch
    a.line((h[0] - 9.5, h[1] + 8), (h[0] + 11, h[1] + 8.4), 2.2, LIT)
    head_bare(a, p)
    kerchief(a, p, 1 + 1.5 * sw)
    floppy_cap(a, c, 1.5 + 2.0 * sw)
    arm(a, p.arm_near, BODY, sleeve_end=0.85)
    e, hnd = p.arm_near[1], p.arm_near[2]
    a.line((e[0] + (hnd[0] - e[0]) * 0.45, e[1] + (hnd[1] - e[1]) * 0.45), (hnd[0] * 0.5 + e[0] * 0.5, hnd[1] * 0.5 + e[1] * 0.5 - 0.4), 4.6, LIT)   # rolled cuff


def dress_gasmask(a: Art, p: Pose) -> None:
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    arm(a, p.arm_far, SHADE)
    legs(a, p, BODY, BODY, r=(6.0, 4.4, 3.2))
    # a long waxed coat to the calf, wide skirted, a short shoulder cape over it
    a.smooth(hem_poly(p, (s[0] - 6, s[1] + 3), (s[0] + 7, s[1] + 2), 35, 11, 13, 0.7, 2.5), BODY)
    a.poly([(h[0] + 1, h[1] + 1), (h[0] + 1.6 + 0.4 * p.sway_f, h[1] - 32), (h[0] + 4.2 + 0.5 * p.sway_f, h[1] - 32)], SHADE)         # a fold of the skirt
    a.line((h[0] - 9, h[1] + 9), (h[0] + 10.5, h[1] + 9.5), 1.8, SHADE)
    a.smooth([(s[0] - 6, s[1] + 4), (s[0] - 13, s[1] - 4), (s[0] - 12, s[1] - 15 - sw), (s[0] + 4, s[1] - 13), (s[0] + 12, s[1] - 6), (s[0] + 8, s[1] + 2)], SHADE, 2)
    a.line((s[0] - 11.5, s[1] - 14 - sw), (s[0] + 3.5, s[1] - 12.5), 1.2, LIT)            # cape edge
    head_bare(a, p, face=0.7)
    a.smooth([(c[0] - 9.5, c[1] - 2), (c[0] - 8, c[1] + 9), (c[0] + 4, c[1] + 6), (c[0] + 7, c[1] - 6), (c[0] - 3, c[1] - 12)], BODY)    # the hood under the hat
    beak_mask(a, c)
    wide_brim(a, c)
    hand = p.arm_near[2]
    tip = (hand[0] + 9 + 3 * sw, 0.0)
    a.line((hand[0] - 1.5, hand[1] + 6), tip, 2.2, BODY)                                   # cane
    a.disc((hand[0] - 1.5, hand[1] + 6.5), 2.6, LIT)                                        # its knob
    arm(a, p.arm_near, BODY)


def dress_puncho(a: Art, p: Pose) -> None:
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    arm(a, p.arm_far, SHADE)
    legs(a, p, BODY, BODY, r=(6.3, 4.8, 3.5), cuff=0.5)
    # a hooded cloak: hangs from the shoulders, flares and swings, with the near hand held out of it
    top_b, top_f = (s[0] - 6, s[1] + 3), (s[0] + 8, s[1] + 2)
    pts = hem_poly(p, top_b, top_f, 27, 17, 18, 0.9, 4.5)
    a.smooth(pts, BODY)
    a.cap((h[0] - 5, h[1] + 14), 1.2, (h[0] - 11 + 0.5 * p.sway_b, h[1] - 24), 0.8, SHADE)   # folds
    a.cap((h[0] + 2, h[1] + 10), 1.2, (h[0] + 2 + 0.3 * (p.sway_f + p.sway_b), h[1] - 26), 0.8, SHADE)
    a.cap((h[0] + 8, h[1] + 12), 1.0, (h[0] + 12 + 0.6 * p.sway_f, h[1] - 23), 0.8, SHADE)
    a.line((s[0] + 8, s[1] - 4), (h[0] + 14.5 + 0.8 * p.sway_f, h[1] - 25), 1.2, LIT)       # front opening edge
    a.line((s[0] - 5, s[1] - 1), (s[0] + 5, s[1] - 1), 2.2, LIT)                            # the clasp cord at the throat
    head_bare(a, p, tone=SHADE)
    hood(a, p, 1.5 * sw)
    hand = p.arm_near[2]
    a.cap(p.arm_near[1], 5.5, (hand[0] + 1, hand[1] + 1), 4.0, BODY)
    a.disc((hand[0] + 1, hand[1]), 3.3, SHADE)


def dress_trechcoat(a: Art, p: Pose) -> None:
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    arm(a, p.arm_far, SHADE)
    legs(a, p, BODY, BODY, r=(6.4, 4.7, 3.4), cuff=0.4)
    a.smooth(hem_poly(p, (s[0] - 6, s[1] + 3), (s[0] + 8, s[1] + 2), 31, 11, 13, 0.7, 2.5), BODY)
    a.poly([(h[0] - 1, h[1] + 2), (h[0] + 1 + 0.5 * p.sway_f, h[1] - 28), (h[0] + 3.5 + 0.5 * p.sway_f, h[1] - 28), (h[0] + 3.5, h[1] + 2)], SHADE)   # the centre vent
    for i in range(3):
        a.disc((s[0] + 7.2 + i * 0.4, s[1] - 7 - i * 9), 1.1, LIT)                                   # buttons
    a.line((h[0] - 9, h[1] + 8), (h[0] + 11, h[1] + 8.5), 2.0, LIT)                                  # belt
    a.poly([(s[0] - 5, s[1] + 4), (s[0] + 11, s[1] - 1), (s[0] + 6, s[1] - 11), (s[0] + 1, s[1] - 7)], LIT)      # the turned-up collar
    a.poly([(s[0] - 3, s[1] + 3), (s[0] + 9, s[1] - 0.5), (s[0] + 5, s[1] - 8), (s[0] + 1, s[1] - 5)], BODY)
    head_bare(a, p)
    tricorne(a, c)
    # a lantern swinging from the near hand
    hand = p.arm_near[2]
    lx, ly = hand[0] + 3 + 2.5 * sw, hand[1] - 10
    a.line((hand[0], hand[1]), (lx, ly + 4), 1.0, BODY)
    a.poly([(lx - 3.6, ly + 4), (lx + 3.6, ly + 4), (lx + 4.2, ly - 6), (lx - 4.2, ly - 6)], BODY)
    a.poly([(lx - 2.1, ly + 2.4), (lx + 2.1, ly + 2.4), (lx + 2.5, ly - 4.4), (lx - 2.5, ly - 4.4)], LIT)         # the lit pane
    a.line((lx - 4.6, ly + 4.4), (lx + 4.6, ly + 4.4), 1.6, BODY)
    a.line((lx - 4.6, ly - 6.6), (lx + 4.6, ly - 6.6), 1.6, BODY)
    arm(a, p.arm_near, BODY)


def dress_pilgrim(a: Art, p: Pose) -> None:
    """The large walker: a robed pilgrim in a travelling cloak, a pointed hat, a beard and a staff with a lit orb."""
    s, h, c = p.shoulder, p.hip, p.head
    sw = math.sin(p.phase)
    cs = math.cos(p.phase)
    arm(a, p.arm_far, SHADE, 4.6, 3.8)
    legs(a, p, BODY, BODY, r=(6.4, 4.8, 3.5))
    # the cloak behind: from the shoulders, flaring back and swinging
    a.smooth([(s[0] - 5, s[1] + 3), (s[0] - 13, s[1] - 6), (h[0] - 15 + 0.9 * p.sway_b, h[1] - 32), (h[0] - 8 + 0.4 * p.sway_b, h[1] - 35), (h[0] + 2, h[1] - 28),
              (h[0] + 3, h[1] + 4)], SHADE)
    # the robe, to the ankles, with a sash
    a.smooth(hem_poly(p, (s[0] - 6, s[1] + 3), (s[0] + 8, s[1] + 2), 42, 12, 13.5, 0.65, 2.5), BODY)
    a.cap((h[0] + 4, h[1] + 4), 1.0, (h[0] + 7 + 0.55 * p.sway_f, h[1] - 38), 0.8, SHADE)
    a.cap((h[0] - 4, h[1] + 4), 1.0, (h[0] - 7 + 0.5 * p.sway_b, h[1] - 39), 0.8, SHADE)
    a.line((h[0] - 10, h[1] + 8), (h[0] + 11, h[1] + 9), 2.6, LIT)
    a.poly([(h[0] + 9, h[1] + 8), (h[0] + 11 + cs, h[1] - 6), (h[0] + 8.5 + cs, h[1] - 7)], LIT)                      # sash end
    a.smooth([(s[0] - 6, s[1] + 4), (s[0] - 15, s[1] - 3), (s[0] - 13, s[1] - 20 - sw), (s[0] + 1, s[1] - 12), (s[0] + 11, s[1] - 7), (s[0] + 9, s[1] + 2)], BODY, 2)  # shoulder cape
    a.line((s[0] - 13.5, s[1] - 18 - sw), (s[0] + 1, s[1] - 11), 1.4, LIT)
    head_bare(a, p)
    a.smooth([(c[0] + 5, c[1] - 6), (c[0] + 10.5, c[1] - 11), (c[0] + 8.5, c[1] - 25), (c[0] + 4, c[1] - 30 - 1.5 * sw), (c[0] + 0.5, c[1] - 18)], LIT, 2)  # long beard
    a.smooth([(c[0] + 6, c[1] - 8), (c[0] + 8.5, c[1] - 11), (c[0] + 7, c[1] - 22), (c[0] + 4, c[1] - 24), (c[0] + 2, c[1] - 16)], BODY, 2)
    # the pointed hat: a cone that bends at the tip, over a broad brim
    a.smooth([(c[0] - 8.5, c[1] + 5), (c[0] - 7.5, c[1] + 15), (c[0] - 10.5, c[1] + 25 - sw), (c[0] - 19 - 2 * sw, c[1] + 33), (c[0] - 7, c[1] + 28),
              (c[0] + 0.5, c[1] + 18), (c[0] + 7.5, c[1] + 6)], BODY, 1)
    a.ell((c[0] + 0.5, c[1] + 5.4), 17.5, 2.8, BODY)
    a.line((c[0] - 8, c[1] + 8.2), (c[0] + 7.2, c[1] + 8.2), 2.4, LIT)
    a.line((c[0] + 17, c[1] + 4.8), (c[0] + 6, c[1] + 6.8), 1.0, LIT)
    # the staff with a glowing orb, planted ahead
    hand = p.arm_near[2]
    top = (hand[0] + 3, hand[1] + 24)
    a.line((hand[0] - 1, hand[1] + 2), (hand[0] + 12 + 5 * sw, 0.0), 2.4, BODY)
    a.line((hand[0] - 1, hand[1] + 2), top, 2.4, BODY)
    a.disc((top[0], top[1] + 3.5), 3.8, BODY)
    a.disc((top[0], top[1] + 3.5), 2.0, LIT)
    arm(a, p.arm_near, BODY, 4.6, 3.8)


@dataclass(frozen=True)
class Kind:
    dress: Callable[[Art, Pose], None]
    height: float             # figure scale: the passers-by differ in height
    long: float = 1.0         # leg length factor
    torso: float = 30.0
    lean: float = 5.0


KINDS: Final[Mapping[str, Kind]] = {
    "Backpack": Kind(dress_backpack, 0.97, 1.0, 30.0, 8.0),
    "Bandana": Kind(dress_bandana, 0.90, 0.97, 29.0, 4.0),
    "Gasmask": Kind(dress_gasmask, 0.99, 1.04, 31.0, 6.0),
    "Puncho": Kind(dress_puncho, 0.93, 0.98, 29.0, 5.0),
    "TrechCoat": Kind(dress_trechcoat, 0.98, 1.0, 31.0, 4.5),
    "Pilgrim": Kind(dress_pilgrim, 1.0, 1.0, 31.0, 4.0),
}


def sheet(kind: Kind, frames: int, cell: tuple[int, int], ground: float, centre: float, scale: float, ss: int,
          tones: tuple[Colour, Colour, Colour], shadow: Colour | None, thr: float = 0.5, min_px: float = 0.0, lit_bias: float = 1.4) -> Image.Image:
    """A row of `frames` walk frames, each figure on `ground` and centred on `centre`."""
    out = Image.new("RGBA", (cell[0] * frames, cell[1]), (0, 0, 0, 0))
    for i in range(frames):
        art = Art(cell, (centre, ground), scale * kind.height, ss, min_px)
        pose = make_pose(2 * math.pi * i / frames, kind.long, kind.torso, kind.lean)
        kind.dress(art, pose)
        tile = Image.new("RGBA", cell, (0, 0, 0, 0))
        if shadow:
            ImageDraw.Draw(tile).ellipse((centre - 25, ground - 3, centre + 25, ground + 2), fill=shadow)
        grid = art.reduce(thr, lit_bias, round(ground))
        px = tile.load()
        for y, row in enumerate(grid):
            for x, t in enumerate(row):
                if t:
                    px[x, y] = tones[t - 1]
        out.paste(tile, (i * cell[0], 0))
    return out


def mid(name: str) -> Callable[[], Image.Image]:
    """The mid-distance sheet (520x180, four frames of 130)."""
    return lambda: sheet(KINDS[name], 4, (130, 180), 144.0, 65.0, 1.0, 4, CROWD, GROUND)


def far(name: str) -> Callable[[], Image.Image]:
    """The far sheet (128x45, four frames of 32): the same people at a quarter size, re-rendered with thin parts widened."""
    return lambda: sheet(KINDS[name], 4, (32, 45), 36.0, 16.0, 0.25, 8, CROWD, None, 0.42, 1.5, 0.8)


def walker1() -> Image.Image:
    """The large walker (1144x273, eight frames of 143)."""
    return sheet(KINDS["Pilgrim"], 8, (143, 273), 252.0, 70.0, 1.88, 3, BIG, None)


PICTURES: Mapping[str, Callable[[], Image.Image]] = {
    **{f"far{k}.128x45.png": far(k) for k in ("Backpack", "Bandana", "Gasmask", "Puncho", "TrechCoat")},
    **{f"mid{k}.520x180.png": mid(k) for k in ("Backpack", "Bandana", "Gasmask", "Puncho", "TrechCoat")},
    "walker1.1144x273.png": walker1,
}
