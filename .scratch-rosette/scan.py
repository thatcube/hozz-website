"""Scan spec grids using the real build+check pipeline; keep what passes."""
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import breath_rosette as br  # noqa: E402

PAL5 = ['#062b31', '#155f66', '#2b8f8c', '#68c2b6', '#c8ece1']
PAL6 = ['#052a30', '#0d4c55', '#166f76', '#2a9494', '#5cb9b1', '#a5e0d4']


def passes(spec):
    try:
        r = br.build(spec)
        br.check('x', r)
        return r
    except (AssertionError, IndexError, KeyError):
        return None


def scan(base, **grid):
    keys = list(grid)
    hits = []
    for combo in itertools.product(*[grid[k] for k in keys]):
        spec = dict(base)
        spec.update(dict(zip(keys, combo)))
        r = passes(spec)
        if r:
            hits.append((spec, r))
    return hits


def brief(spec, r):
    f = r['fit']
    ys = sorted({y for _, y in r['body']})
    xs = sorted({x for x, _ in r['body']})
    return (f"n={spec['n']} d={spec['dist']} r={spec['r']} cy={spec['cy']} "
            f"K={spec.get('K')} core={spec.get('core', 0)} ring={spec.get('ring')} "
            f"| {xs[-1]-xs[0]+1}x{ys[-1]-ys[0]+1} face {f['size']}g{f['gap']} "
            f"cy{f['cy']} fieldair {f['pad']} markair {f['above']} "
            f"tones {len({c for _, c in r['layers']})}")


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'lattice'
    if which == 'lattice':
        hits = scan(dict(mode='lattice', n=6, phase=-90.0, palette=PAL5),
                    dist=[4.5, 5.0, 5.5, 6.0, 6.5],
                    r=[6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
                    cy=[15.0, 15.5, 16.0, 16.5],
                    ring=[2, 3],
                    K=[3, 4, 5, 6],
                    core=[0.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5])
    elif which == 'lattice8':
        hits = scan(dict(mode='lattice', n=8, phase=-90.0, palette=PAL5),
                    dist=[5.0, 5.5, 6.0, 6.5],
                    r=[7.0, 7.5, 8.0, 8.5],
                    cy=[15.0, 15.5, 16.0],
                    ring=[2, 3],
                    K=[3, 4, 5, 6],
                    core=[0.0, 3.5, 4.0, 4.5, 5.0])
    else:
        hits = scan(dict(mode='fill', n=5, palette=PAL5),
                    phase=[-90.0, 90.0],
                    dist=[3.5, 4.0, 4.5, 5.0, 5.5, 6.0],
                    r=[7.0, 7.5, 8.0, 8.5, 9.0, 9.5],
                    cy=[14.5, 15.0, 15.5, 16.0, 16.5, 17.0],
                    K=[3, 4, 5],
                    core=[0.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5])
    print(len(hits), 'pass')
    for spec, r in hits:
        print(brief(spec, r))
