"""Probe 3: three ways to get from rim to centre on the same bubble body."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from shade import rings, keyline, is_slab  # noqa: E402

X0, X1, Y0, Y1 = 2, 29, 2, 23
CX, CYY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2
N = 3.0


def shell(inset):
    a, b = (X1 + 1 - X0) / 2 - inset, (Y1 + 1 - Y0) / 2 - inset
    return {(x, y) for y in range(Y0, Y1 + 1) for x in range(X0, X1 + 1)
            if (abs(x + 0.5 - CX) / a) ** N + (abs(y + 0.5 - CYY) / b) ** N <= 1 + 1e-9}


BODY = shell(0)


def edt_levels(shape, n):
    """Euclidean erosion: level i = pixels more than i from the background."""
    bg = {(x, y) for y in range(Y0 - 2, Y1 + 3) for x in range(X0 - 2, X1 + 3)} - shape
    out = []
    d = {}
    for p in shape:
        d[p] = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 for q in bg)
    for i in range(n + 1):
        out.append({p for p in shape if d[p] > i})
    return out


def dump(name, levels):
    core = levels[-1]
    sym = {}
    for i in range(len(levels) - 1):
        for p in levels[i] - levels[i + 1]:
            sym[p] = str(i)
    for p in core:
        sym[p] = '#'
    print(f'\n== {name}: core {len(core)}px slab={is_slab(core, BODY)} '
          f'bands {[len(levels[i] - levels[i+1]) for i in range(len(levels)-1)]}')
    for y in range(Y0, Y1 + 1):
        print('   ' + ''.join(sym.get((x, y), '.') for x in range(32)))
    cxs = sorted({p[0] for p in core})
    cys = sorted({p[1] for p in core})
    print(f'   core box x{cxs[0]}-{cxs[-1]} y{cys[0]}-{cys[-1]}')


dump('nested superellipses', [shell(i) for i in range(7)])

lv, cur = [set(BODY)], set(BODY)
for _ in range(6):
    r, cur = rings(cur, 1)
    lv.append(set(cur))
dump('shade.rings peeling', lv)

dump('euclidean erosion', edt_levels(BODY, 6))
