"""t11 — Twozz, the direct sibling of c45 · Ripple, Lens.

c45 was rasterised to the 32 grid and measured before anything was drawn here:

    6 stops, rim -> centre    #edf6fc #dcecf6 #cae1f1 #b9d7eb #a7cce6 #96c2e0
    step size                 ΔE 4.97 5.69 4.95 5.67 4.88  (mean 5.21)
    total rim -> centre       ΔE 26.07,  ΔL 20.0
    direction per step        L -4.0, chroma +3.3
    parts                     a light rim, a stepped ramp inward, a deeper
                              centre, rings outside — the eye can find the
                              seams even though every step is small

This is that system in purple, on the bubble. Same six stops, same mean step
(held to c45's 5.21 by construction and asserted). What changed after the first
review is everything the tone count could not see.

**The face.** md (8 wide) in a 28-wide body left the face floating in a violet
field — the exact note the client has made all along, that a mark should *be* a
face rather than contain one. It is now lg, 10 wide, the same ratio the shipped
mark uses, and the body grew to 24 rows so a 10-row face still splits its air
7/7. The face is 100 px on a 164 px field: it is the subject, not an inset.

**The parts.** Six stops spent as an even wash is still a wash — every step does
the same thing as the one before, so the eye finds no seam. The stops are spent
on named parts instead, and one of them reverses direction, which is what makes
a boundary visible at all:

    rim      1 px, the lightest stop        the lit outer edge
    bevel    3 px, three stops, 1 px each   the surface turning away
    groove   1 px, the *darkest* stop       where the wall meets the floor
    field    the rest, one stop lighter     the plane the face sits on

Inward the tone goes down, down, down, down, then *up*. That single reversal at
the groove is the seam; without it six steps in a row read as a gradient. The
shells also relax from a squarish superellipse (n=3.6, close to the shipped
silhouette) to a soft oval (n=2.3) as they go in, so the field's edge is not
parallel to the outline and reads as a different part rather than another band.

**The tail.** A tail is what makes the silhouette a speech bubble, and the first
version's — six rows, tapering from both the top and the tip — read as a
hairline flick. Mass is stubbiness, not length: the shipped tail is 6 px across
and 4 rows deep, an aspect of 1.5. This one is 8 across and 4 deep, aspect 2.0,
with a straight left edge continuing the body's corner and the taper taken
entirely from the right. Interior widths after the keyline run 6-5-3.

**The hue.** Purple cannot be anchored where blue was — a near-white rim stops
being Twitch — so the ramp is anchored by its *middle*: stop 3 of 6 is #8f52f6,
the purple Twozz already ships, exactly. #8f52f6 is already at C 94 and sRGB has
nothing more saturated at that lightness, so the per-step chroma rise is taken as
far as the gamut allows and the rest of the ΔE budget goes to lightness. The step
*size* is what the eye reads, and that is matched.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import keyline, rings, to_paths, is_slab, show  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't11'
NAME = 'Lens'

# ---------------------------------------------------------------------------
# Colour. Everything below is CIE Lab, because "the same subtlety of step" is a
# perceptual claim and hex arithmetic cannot check it.
# ---------------------------------------------------------------------------
BRAND = '#8f52f6'           # Twozz, as shipped
KEY = '#1b0b36'             # the near-black of the hue, as Mozz does it
INK = '#ffffff'             # the family's ink on a coloured container
STEPS = 6
ANCHOR = 3                  # which stop is exactly BRAND
C45_STEP, C45_TOTAL = 5.21, 26.07   # measured, see the docstring


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _unlin(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lab(hexstr):
    r, g, b = (_lin(int(hexstr[i:i + 2], 16) / 255) for i in (1, 3, 5))
    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = f(X / 0.95047), f(Y), f(Z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def rgb(L, a, b):
    """Lab -> hex, plus whether it needed clipping to fit sRGB."""
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def g(t):
        return t ** 3 if t ** 3 > 216 / 24389 else (t - 4 / 29) * 108 / 841
    X, Y, Z = g(fx) * 0.95047, g(fy), g(fz) * 1.08883
    lin = (X * 3.2406 + Y * -1.5372 + Z * -0.4986,
           X * -0.9689 + Y * 1.8758 + Z * 0.0415,
           X * 0.0557 + Y * -0.2040 + Z * 1.0570)
    out = '#%02x%02x%02x' % tuple(
        round(_unlin(max(0.0, min(1.0, v))) * 255) for v in lin)
    return out, any(v < -0.002 or v > 1.002 for v in lin)


def de(a, b):
    return sum((x - y) ** 2 for x, y in zip(lab(a), lab(b))) ** 0.5


def build_ramp(dC):
    """Six stops through BRAND, `dC` of chroma and the rest of c45's step in L."""
    L0, a0, b0 = lab(BRAND)
    C0 = (a0 ** 2 + b0 ** 2) ** 0.5
    dL = (C45_STEP ** 2 - dC ** 2) ** 0.5
    stops, clipped = [], False
    for i in range(STEPS):
        k = i - ANCHOR                      # -3 .. +2, 0 is BRAND
        s = (C0 + dC * k) / C0
        h, cl = rgb(L0 - dL * k, a0 * s, b0 * s)
        clipped |= cl
        stops.append(h)
    return stops, clipped


# c45 splits its step 4.0 lightness / 3.3 chroma. Purple cannot: #8f52f6 sits
# 6 units under the sRGB boundary at its own lightness, and that boundary falls
# by 2.1 of chroma for every unit of lightness gained, so a rim three stops
# lighter has to give up chroma faster than blue does. Spend as much of the step
# on lightness as the gamut allows and take the rest in chroma — the split
# moves, the step size does not.
RAMP = None
for hundredths in range(0, 521, 5):
    cand, clipped = build_ramp(hundredths / 100)
    if not clipped:
        RAMP, DC = cand, hundredths / 100
        break
assert RAMP, 'no in-gamut ramp'
RAMP[ANCHOR] = BRAND                        # exact, not merely rounded to it

STEP_DE = [de(a, b) for a, b in zip(RAMP, RAMP[1:])]
MEAN = sum(STEP_DE) / len(STEP_DE)
TOTAL = de(RAMP[0], RAMP[-1])
assert abs(MEAN - C45_STEP) < 0.35, f'step {MEAN:.2f} is not c45\'s {C45_STEP}'
assert abs(TOTAL - C45_TOTAL) < 1.5, f'total {TOTAL:.2f} is not c45\'s {C45_TOTAL}'
assert max(STEP_DE) - min(STEP_DE) < 0.9, 'one step is louder than the others'
for a, b in zip(RAMP, RAMP[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= 18, f'{a}->{b} steps by {d} on a channel, which reads as a band'
assert lab(RAMP[0])[0] > lab(RAMP[-1])[0], 'the rim must be the lighter end'