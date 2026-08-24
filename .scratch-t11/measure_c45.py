"""Rasterise c45 to a 32 grid and read its ramp back out.

Painter's algorithm over the path list in the component, plus the face group,
so what comes out is what is actually on screen rather than what the source
claims. Then: tone sequence rim -> centre, pixel count per tone, and the size
of each step in CIE Lab, which is the number the sibling has to match.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'src/components/mark/logos/c45.astro').read_text()


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


grid = {}
order = []
for d, fill in re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC):
    order.append(fill)
    for p in pixels(d):
        grid[p] = fill

# the face, from mark.ts itself
js = ("import {facePathsAt} from '%s/src/data/mark.ts';"
      "console.log(JSON.stringify(facePathsAt({cx:16,cy:13,size:'md',smile:'compact',gap:2})));" % ROOT)
face = set()
for d in json.loads(subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e', js],
        capture_output=True, text=True, check=True).stdout):
    face |= pixels(d)
for p in face:
    grid[p] = 'FACE(#132638)'

tones = {}
for p, f in grid.items():
    tones.setdefault(f, set()).add(p)

print('tone counts (as rendered):')
for f in sorted(tones, key=lambda f: -len(tones[f])):
    xs = sorted({p[0] for p in tones[f]})
    ys = sorted({p[1] for p in tones[f]})
    print(f'  {f:16} {len(tones[f]):4} px   x{xs[0]}-{xs[-1]} y{ys[0]}-{ys[-1]}')
print(f'  {len(tones)} distinct tones on screen\n')


# ---- the ramp itself -------------------------------------------------------
def srgb_to_lab(hexstr):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505
    Xn, Yn, Zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = f(X / Xn), f(Y / Yn), f(Z / Zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de(a, b):
    la, lb = srgb_to_lab(a), srgb_to_lab(b)
    return sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5


RAMP = ['#edf6fc', '#dcecf6', '#cae1f1', '#b9d7eb', '#a7cce6', '#96c2e0']
print('the six-stop ramp, rim -> centre:')
prev = None
for i, c in enumerate(RAMP):
    L, a, b = srgb_to_lab(c)
    n = len(tones.get(c, ()))
    step = f'  ΔE {de(prev, c):5.2f}' if prev else ''
    chan = ''
    if prev:
        chan = '  Δchan %2d %2d %2d' % tuple(
            abs(int(prev[k:k + 2], 16) - int(c[k:k + 2], 16)) for k in (1, 3, 5))
    print(f'  {i} {c}  {n:4} px   L {L:5.1f} a {a:5.1f} b {b:5.1f}{step}{chan}')
    prev = c
print(f'\n  total rim->centre ΔE {de(RAMP[0], RAMP[-1]):.2f}'
      f'   ΔL {srgb_to_lab(RAMP[0])[0] - srgb_to_lab(RAMP[-1])[0]:.1f}')
print(f'  mean step ΔE {de(RAMP[0], RAMP[-1]) / 5:.2f}')
print(f'  ramp covers {sum(len(tones.get(c, ())) for c in RAMP)} px of the '
      f'{len(tones.get("#132638", set()) | set().union(*[tones.get(c, set()) for c in RAMP]))} in the disc')

print('\nthe grid (0 = keyline, 1..6 rim->centre, @ = face, ~ = water):')
sym = {'#132638': '0', '#96bcd6': '~', '#5d8cb0': '=', 'FACE(#132638)': '@'}
for i, c in enumerate(RAMP):
    sym[c] = str(i + 1)
ys = sorted({p[1] for p in grid})
print('     ' + ''.join(str(i % 10) for i in range(32)))
for y in ys:
    print(f'  {y:3} ' + ''.join(sym.get(grid.get((x, y)), '.') for x in range(32)))
