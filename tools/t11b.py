"""scratch: the rebuilt t11 interior, before it replaces tools/t11.py"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from shade import keyline, to_paths, is_slab, show
from circles import check

X0, X1, Y0, Y1 = 2, 29, 2, 25
CX, CYY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2
N0, N6 = 3.6, 2.3


def shell(i):
    n = N0 + (N6 - N0) * (i / 6)
    a, b = (X1 + 1 - X0) / 2 - i, (Y1 + 1 - Y0) / 2 - i
    return {(x, y) for y in range(Y0, Y1 + 1) for x in range(X0, X1 + 1)
            if (abs(x + 0.5 - CX) / a) ** n + (abs(y + 0.5 - CYY) / b) ** n <= 1 + 1e-9}


SH = [shell(i) for i in range(7)]
BODY = SH[0]
TAIL_ROWS = {26: (9, 16), 27: (9, 15), 28: (9, 14), 29: (9, 12)}
TAIL = {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)}
SIL = BODY | TAIL
K = {}
for p in BODY:
    K[p] = max(i for i in range(7) if p in SH[i])
NAMES = {0: 'rim', 1: 'rim', 2: 'bevel1', 3: 'bevel2', 4: 'bevel3', 5: 'groove', 6: 'field'}
OUT = keyline(SIL)
layers = {}
for p in BODY:
    layers.setdefault(NAMES[K[p]], set()).add(p)
for p in TAIL:
    layers.setdefault('rim', set()).add(p)
for p in OUT:
    for s in layers.values():
        s.discard(p)
layers['key'] = OUT
sym = ['key', 'rim', 'bevel1', 'bevel2', 'bevel3', 'groove', 'field']
print({k: len(layers[k]) for k in sym})
print('slab', is_slab(layers['field'], BODY))
show([layers[k] for k in sym], ['0', '1', '2', '3', '4', 'g', 'F'])
rows = {}
for x, y in SIL:
    rows.setdefault(y, []).append(x)
tw = max(b - a + 1 for a, b in TAIL_ROWS.values())
print('tail', tw, 'wide x', len(TAIL_ROWS), 'rows  aspect', round(tw / len(TAIL_ROWS), 2))
print('tail interior per row', [len([x for x in range(a, b + 1) if (x, y) not in OUT])
                                for y, (a, b) in sorted(TAIL_ROWS.items())])
