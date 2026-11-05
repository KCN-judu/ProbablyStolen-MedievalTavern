"""Landmark detection for the game's 288x211 bust frames, from the frame's own alpha and colours.

Everything here only *measures* a frame (numbers); nothing from a frame is stored or copied anywhere.
The portraits share one template: the shoulder line is the most reliable feature (the silhouette suddenly widens),
the face sits at a fixed distance above it, and the head width is read from the silhouette near eye level.
"""

from __future__ import annotations

import colorsys
import statistics
from dataclasses import dataclass, field

from PIL import Image

FW, FH = 288, 211
CHIN_ABOVE_SHOULDER = 12      # calibrated on the originals (see debug overlays)
EYES_ABOVE_CHIN = 27
HAT_ABOVE_EYES = 13


@dataclass
class Landmarks:
    top: int                   # first row of the silhouette (hair/hat included)
    cx: float                  # head centre
    tcx: float                 # torso centre
    hw: int                    # head width near eye level
    sw: int                    # shoulder width
    sh_y: int                  # shoulder line
    chin_y: int
    eyes_y: int
    hat_y: int                 # where a hat's lower edge sits on the forehead
    nose_y: int
    mouth_y: int
    neck_y: int
    chest_y: int
    skin: tuple[int, int, int]
    skin_hsv: tuple[float, float, float]
    notes: list[str] = field(default_factory=list)

    def point(self, name: str) -> tuple[float, float]:
        cx, hw = self.cx, self.hw
        return {
            "brow": (cx, self.hat_y), "crown": (cx, self.top), "forehead": (cx, self.hat_y + 8),
            "eyes": (cx, self.eyes_y), "eye_l": (cx - 0.2 * hw, self.eyes_y), "eyes_low": (cx, self.eyes_y + 4),
            "cheek_c": (cx, self.eyes_y + 9), "cheek_l": (cx - 0.25 * hw, self.eyes_y + 9), "cheek_r": (cx + 0.25 * hw, self.eyes_y + 9),
            "nose": (cx, self.nose_y), "mouth": (cx, self.mouth_y), "jaw": (cx, self.mouth_y), "chin": (cx, self.chin_y),
            "neck": (self.tcx, self.neck_y), "shoulders": (self.tcx, self.sh_y), "chest": (self.tcx, self.chest_y),
        }[name]


def _widths(A: list[list[bool]]) -> tuple[list[int], list[int], list[int]]:
    w, xl, xr = [], [], []
    for y in range(FH):
        xs = [x for x in range(FW) if A[y][x]]
        if len(xs) >= 2:
            w.append(xs[-1] - xs[0] + 1), xl.append(xs[0]), xr.append(xs[-1])
        else:
            w.append(0), xl.append(0), xr.append(0)
    return w, xl, xr


def alpha_grid(img: Image.Image) -> list[list[bool]]:
    a = img.getchannel("A").load()
    return [[a[x, y] >= 128 for x in range(FW)] for y in range(FH)]


def analyse(img: Image.Image) -> Landmarks | None:
    A = alpha_grid(img)
    w, xl, xr = _widths(A)
    notes: list[str] = []
    tops = [y for y in range(FH) if w[y] >= 3]
    if not tops:
        return None
    top = tops[0]
    hw0 = sorted(w[top + 14: top + 44])[int(0.8 * 30)]
    sh = None
    for y in range(top + 50, FH - 3):
        if w[y] > hw0 * 1.35 and w[y + 2] > hw0 * 1.35:
            sh = y
            break
    if sh is None or not 62 <= sh - top <= 100:
        notes.append("shoulder fallback")
        sh = min(FH - 40, top + 77)
    chin = sh - CHIN_ABOVE_SHOULDER
    eyes = chin - EYES_ABOVE_CHIN
    hat = eyes - HAT_ABOVE_EYES
    # head centre: median of row centres at cheek level; head width: median row width around the eyes
    rows = range(eyes - 8, eyes + 9)
    cx = statistics.median((xl[y] + xr[y]) / 2 for y in rows if w[y] > 10)
    hw = int(statistics.median(w[y] for y in rows if w[y] > 10))
    hw = max(36, min(hw, 58))
    rows2 = range(sh + 14, min(FH, sh + 40))
    tcx = statistics.median((xl[y] + xr[y]) / 2 for y in rows2 if w[y] > 40) if any(w[y] > 40 for y in rows2) else cx
    sw = int(statistics.median(w[y] for y in rows2 if w[y] > 40)) if any(w[y] > 40 for y in rows2) else 130
    skin, hsv = _skin(img, A, cx, eyes, hw)
    eyes, hat, hairline = _refine(img, A, cx, hw, eyes, hat, skin, top)
    if hairline is not None:
        notes.append(f"hairline {hairline}")
    return Landmarks(top=top, cx=cx, tcx=tcx, hw=hw, sw=sw, sh_y=sh, chin_y=chin, eyes_y=eyes, hat_y=hat, nose_y=eyes + 10,
                     mouth_y=eyes + 18, neck_y=chin + 5, chest_y=sh + 9, skin=skin, skin_hsv=hsv, notes=notes)


def _refine(img: Image.Image, A: list[list[bool]], cx: float, hw: int, eyes: int, hat: int, skin: tuple[int, int, int],
            top: int) -> tuple[int, int, int | None]:
    """Pulls the eye row and the hat line toward what the frame shows.

    Eyes and brows are the rows with the most dark pixels beside the nose bridge; the hairline is the first row going up
    the middle of the forehead where hair (dark or odd-coloured pixels) takes over from skin.
    """
    px = img.load()
    sl = 0.3 * skin[0] + 0.59 * skin[1] + 0.11 * skin[2]

    def lum(c) -> float:
        return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]

    xs = [int(cx) + d for d in range(-int(hw * 0.36), int(hw * 0.36) + 1) if abs(d) > 3]
    score = {}
    for y in range(eyes - 9, eyes + 10):
        score[y] = sum(1 for x in xs if 0 <= x < FW and A[y][x] and lum(px[x, y]) < 0.5 * sl)
    best = max(score.values())
    if best >= 5:
        rows = [y for y, v in score.items() if v >= 0.6 * best]
        est = sum(rows) / len(rows) + 1.5
        new_eyes = round(eyes + 0.6 * max(-4.0, min(4.0, est - eyes)))
    else:
        new_eyes = eyes
    shift = new_eyes - eyes
    eyes = new_eyes
    hair_row = None
    band = [int(cx) + d for d in range(-5, 6)]
    for y in range(eyes - 6, max(top, eyes - 30), -1):
        hairy = 0
        for x in band:
            c = px[x, y]
            if c[3] < 128:
                hairy += 1
            elif lum(c) < 0.55 * sl or _foreign_loose(c, skin):
                hairy += 1
        if hairy >= 6:
            hair_row = y + 1
            break
    hat = eyes - HAT_ABOVE_EYES
    if hair_row is not None and eyes - 26 <= hair_row <= eyes - 8:
        hat = max(eyes - 17, min(eyes - 9, hair_row + 1))
    return eyes, hat, hair_row


def _foreign_loose(c: tuple[int, int, int], skin: tuple[int, int, int]) -> bool:
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    sh, ss, sv = colorsys.rgb_to_hsv(skin[0] / 255, skin[1] / 255, skin[2] / 255)
    dh = min(abs(h - sh), 1 - abs(h - sh))
    return dh > 0.07 or s > 1.6 * ss + 0.12


def _skin(img: Image.Image, A: list[list[bool]], cx: float, eyes: int, hw: int) -> tuple[tuple[int, int, int], tuple[float, float, float]]:
    """The face colour: median of cheek pixels beside the nose (below the eyes, inside the head)."""
    px = img.load()
    pts = []
    for y in range(eyes + 4, eyes + 14):
        for dx in list(range(-14, -5)) + list(range(6, 15)):
            x = int(cx) + dx
            if 0 <= x < FW and A[y][x]:
                pts.append(px[x, y][:3])
    if not pts:
        return (190, 140, 110), (0.07, 0.4, 0.75)
    pts.sort(key=lambda c: c[0] + c[1] + c[2])
    mid = pts[len(pts) // 4: 3 * len(pts) // 4 + 1] or pts
    skin = tuple(int(statistics.median(c[i] for c in mid)) for i in range(3))
    return skin, colorsys.rgb_to_hsv(*(v / 255 for v in skin))  # type: ignore[return-value]


def is_skin(c: tuple[int, int, int], lm: Landmarks) -> bool:
    """Skin-like colours of this person: close in hue and saturation to the face (shading changes only value)."""
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    sh, ss, sv = lm.skin_hsv
    dh = min(abs(h - sh), 1 - abs(h - sh))
    if v < 0.16:
        return False
    return dh < 0.045 and 0.6 * ss - 0.04 < s < 1.45 * ss + 0.05 and v < sv * 1.35 + 0.1


def debug_overlay(img: Image.Image, lm: Landmarks, scale: int = 3) -> Image.Image:
    bg = Image.new("RGBA", img.size, (90, 110, 90, 255))
    bg.alpha_composite(img)
    from PIL import ImageDraw
    big = bg.resize((FW * scale, FH * scale), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for y, col in ((lm.top, (255, 255, 255)), (lm.hat_y, (0, 255, 255)), (lm.eyes_y, (255, 255, 0)), (lm.nose_y, (255, 128, 0)),
                   (lm.mouth_y, (255, 0, 255)), (lm.chin_y, (255, 60, 60)), (lm.sh_y, (60, 255, 60))):
        d.line((0, y * scale, FW * scale, y * scale), fill=col)
    d.line((lm.cx * scale, 0, lm.cx * scale, FH * scale), fill=(255, 255, 255))
    d.rectangle(((lm.cx - lm.hw / 2) * scale, lm.eyes_y * scale - 4, (lm.cx + lm.hw / 2) * scale, lm.eyes_y * scale + 4), outline=(255, 255, 0))
    d.rectangle(((lm.tcx - lm.sw / 2) * scale, (lm.sh_y + 20) * scale - 4, (lm.tcx + lm.sw / 2) * scale, (lm.sh_y + 20) * scale + 4), outline=(60, 255, 60))
    return big
