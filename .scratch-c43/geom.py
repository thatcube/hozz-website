"""Scratch: try several readings of "a double border around the ZZ" side by side."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check           # noqa: E402
from shade import rings, to_paths, show      # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


WATER_OUT = set().union(*[pixels(d) for d, f in PATHS[:26] if f == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, f in PATHS[:26] if f != '#96bcd6'])

DISC = circle(22)
check(DISC)
DYS = sorted({p[1] for p in DISC})

# --- face, md gap 1: 8 wide, 8 tall -----------------------------------------
EYES = [[(0, 2), (5, 7)], [(1, 2), (6, 7)], [(0, 1), (5, 6)], [(0, 2), (5, 7)]]
SMILE = [[(0, 0), (7, 7)], [(0, 1), (6, 7)], [(1, 6)]]


def face_px(cy, gap=1):
    rows = EYES + [[] for _ in range(gap)] + SMILE
    top = cy - len(rows) // 2
    left = 12
    s = set()
    for i, runs in enumerate(rows):
        for a, b in runs:
            s |= {(left + a + k, top + i) for k in range(b - a + 1)}
    return s, top, len(rows)


def ring_map(n=9):
    rgs, core = rings(DISC, n)
    idx = {}
    for i, r in enumerate(rgs):
        for p in r:
            idx[p] = i
    for p in core:
        idx[p] = n
    return idx, rgs, core


if __name__ == '__main__':
    idx, rgs, core = ring_map(9)
    fp, top, h = face_px(13)
    print(f'disc rows {DYS[0]}-{DYS[-1]}  face rows {top}-{top + h - 1}  '
          f'air {top - DYS[0]}/{DYS[-1] - (top + h - 1)}')
    print('\nring index map (face as #):')
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(DYS[0], DYS[-1] + 1):
        line = ''
        for x in range(32):
            if (x, y) in fp:
                line += '#'
            elif (x, y) in idx:
                line += str(idx[(x, y)])
            else:
                line += '.'
        print(f'{y:3} {line}')
    print('\nring sizes:', [len(r) for r in rgs], 'core', len(core))
