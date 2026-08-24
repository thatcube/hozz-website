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