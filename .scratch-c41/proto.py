"""Prototype the c41 edge ramp: isotropic vs anisotropic, printed as ASCII."""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check          # noqa: E402
from shade import keyline                   # noqa: E402

DISC = circle(22)
check(DISC)

INNER = DISC - keyline(DISC)


def depth_field(shape, ky):
    """Anisotropic distance from every pixel of `shape` to the nearest pixel
    outside it. ky < 1 makes vertical travel cheap, so the ramp reaches further
    in from the top and bottom and the innermost contour becomes a wide lens."""
    out = [(x, y) for x in range(-2, 34) for y in range(-2, 34)
           if (x, y) not in shape]
    d = {}
    for p in shape:
        best = 1e9
        for q in out:
            dx = p[0] - q[0]
            dy = (p[1] - q[1]) * ky
            v = dx * dx + dy * dy
            if v < best:
                best = v
        d[p] = math.sqrt(best)
    return d


def bands(d, cuts):
    """Quantise a depth field into tone indices at the given cut points."""
    t = {}
    for p, v in d.items():
        i = 0
        while i < len(cuts) and v > cuts[i]:
            i += 1
        t[p] = i
    return t


def show(t, n):
    ys = sorted({y for _, y in t})
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(ys[0], ys[-1] + 1):
        line = ''.join(str(t[(x, y)]) if (x, y) in t else '.' for x in range(32))
        print(f'{y:3} {line}')
    used = sorted(set(t.values()))
    print(f'    tones used: {used} of {n}')


CUTS = [1.5, 2.5, 3.5, 4.5, 5.5, 6.5]

for label, ky in (('isotropic ky=1.00', 1.00),
                  ('wide lens ky=0.70', 0.70),
                  ('tall lens ky=1.40', 1.40)):
    print(f'\n===== {label} =====')
    show(bands(depth_field(INNER, ky), CUTS), len(CUTS) + 1)
