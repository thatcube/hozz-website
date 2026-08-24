"""Probe 2: what does 'rim to centre' look like on a bubble body?

Three candidate bodies (rounded rect, two superellipses) x two band constructions
(4-neighbour ring peeling from shade.rings, and nested offsets of the same
generator), printed as ASCII so the corners can be judged.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from circles import check  # noqa: E402
from shade import rings, keyline, is_slab  # noqa: E402

X0, X1, Y0, Y1 = 2, 29, 2, 23
CX, CY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2


def rrect(inset, r):
    x0, x1, y0, y1 = X0 + inset, X1 - inset, Y0 + inset, Y1 - inset
    out = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cx = min(max(x + 0.5, x0 + r), x1 + 1 - r)
            cy = min(max(y + 0.5, y0 + r), y1 + 1 - r)
            if ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5 <= r + 1e-9:
                out.add((x, y))
    return out


def squircle(inset, n):
    a, b = (X1 + 1 - X0) / 2 - inset, (Y1 + 1 - Y0) / 2 - inset
    out = set()
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            u, v = abs(x + 0.5 - CX) / a, abs(y + 0.5 - CY) / b
            if u ** n + v ** n <= 1 + 1e-9:
                out.add((x, y))
    return out


def render(name, levels):
    body = levels[0]
    try:
        check(body)
        ok = 'clean'
    except AssertionError as e:
        ok = f'FAIL {e}'
    rows = {}
    for x, y in body:
        rows.setdefault(y, []).append(x)
    w = [max(rows[y]) - min(rows[y]) + 1 for y in sorted(rows)]
    core = levels[-1]
    print(f'\n== {name}   {ok}   widths {w}')
    print(f'   core {len(core)}px  slab={is_slab(core, body)}  '
          f'bands {[len(levels[i] - levels[i + 1]) for i in range(len(levels) - 1)]}')
    sym = {}
    for i in range(len(levels) - 1):
        for p in levels[i] - levels[i + 1]:
            sym[p] = '0' if i == 0 else str(i)
    for p in core:
        sym[p] = '#'
    for y in range(Y0, Y1 + 1):
        print('   ' + ''.join(sym.get((x, y), '.') for x in range(32)))


for r in (7, 8):
    lv = [rrect(i, max(r - i, 1)) for i in range(7)]
    render(f'rounded rect r={r}, true offsets (r-i)', lv)
    lv = [rrect(i, max(r - i * 0.6, 1)) for i in range(7)]
    render(f'rounded rect r={r}, slow offsets (r-0.6i)', lv)

B = rrect(0, 7)
bands, core = rings(B - keyline(B), 5)
lv = [B]
cur = set(B)
for b in [keyline(B)] + bands:
    cur = cur - b
    lv.append(set(cur))
render('rounded rect r=7, shade.rings peeling', lv)

for n in (2.6, 3.0, 3.4):
    lv = [squircle(i, n) for i in range(7)]
    render(f'squircle n={n}, nested', lv)
