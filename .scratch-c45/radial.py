import sys, math
from pathlib import Path
sys.path.insert(0, 'tools')
from circles import circle
from shade import keyline, is_slab, show

DISC = circle(22)
K = keyline(DISC); inner = DISC - K
CX, CY = 16.0, 13.0
def r(p): return math.hypot(p[0] + 0.5 - CX, p[1] + 0.5 - CY)
rmax = max(r(p) for p in inner)
print('rmax', round(rmax, 3), 'rmin', round(min(r(p) for p in inner), 3))
for n in (6, 7, 8):
    lv = {}
    for p in inner:
        lv[p] = min(n - 1, int(rmax - r(p) + 1e-9))
    bands = [{p for p, l in lv.items() if l == i} for i in range(n)]
    sizes = [len(b) for b in bands]
    slab = [i for i, b in enumerate(bands) if b and is_slab(b, DISC)]
    empty = [i for i, b in enumerate(bands) if not b]
    print(f'n={n} sizes {sizes} slab {slab} empty {empty}')
    if n == 7:
        show([DISC] + bands, ['#'] + [str(i) for i in range(n)])
