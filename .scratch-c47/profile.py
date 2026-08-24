"""Prototype the c47 radial brightness profile and print the level map."""
import sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from circles import circle, check
from shade import keyline

DISC = circle(22)
print('disc widths', check(DISC))
ys = sorted({y for _, y in DISC})
print('rows', ys[0], ys[-1], len(ys))

CX, CY = 16.0, (ys[0] + ys[-1] + 1) / 2
print('centre', CX, CY)

K = keyline(DISC)
INNER = DISC - K


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def profile(r, r0, sig, rim_a, rim_b, rim_amt, core_amt, core_r):
    """Brightness in [0,1]. Non-monotonic: dark rim, bright caustic ring at r0,
    settling to a mid-pale core."""
    v = 0.55
    v -= rim_amt * smoothstep(rim_a, rim_b, r)          # Fresnel darkening at the edge
    v += 0.45 * math.exp(-((r - r0) ** 2) / (2 * sig * sig))  # caustic ring
    v += core_amt * smoothstep(core_r, 0.0, r)          # gentle lift in the very centre
    return v


def levels(n, **kw):
    vals = {}
    for x, y in INNER:
        r = math.hypot(x + 0.5 - CX, y + 0.5 - CY)
        vals[(x, y)] = profile(r, **kw)
    lo, hi = min(vals.values()), max(vals.values())
    out = {}
    for p, v in vals.items():
        t = (v - lo) / (hi - lo) if hi > lo else 0
        out[p] = min(n - 1, int(t * n))
    return out


def show(lv):
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(0, 32):
        line = ''
        for x in range(32):
            if (x, y) in K:
                line += '#'
            elif (x, y) in lv:
                line += '0123456789'[lv[(x, y)]]
            else:
                line += '.'
        print(f'{y:3} ' + line)
    from collections import Counter
    print(sorted(Counter(lv.values()).items()))


import itertools
for r0, sig, rim_amt, core_amt, core_r in [
    (6.8, 1.6, 0.30, 0.10, 4.0),
    (7.2, 1.9, 0.34, 0.14, 4.5),
    (6.5, 2.2, 0.30, 0.18, 5.0),
]:
    print(f'\n=== r0={r0} sig={sig} rim={rim_amt} core={core_amt}/{core_r} ===')
    show(levels(8, r0=r0, sig=sig, rim_a=6.5, rim_b=10.5, rim_amt=rim_amt,
                core_amt=core_amt, core_r=core_r))
