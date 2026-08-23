import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab import (rosette, clamp_profile, profile_ok, count_jumps, symmetric,
                 show, widths, rows_of)


def trial(tag, n, dist, r, cy=16.0, phase=-90.0, ring=None, clamp=True):
    d = rosette(n, cy, dist, r, phase, ring)
    body = set(d)
    if clamp:
        body = clamp_profile(body)
        d = {p: v for p, v in d.items() if p in body}
    xs = [p[0] for p in body]
    ys = [p[1] for p in body]
    print(f'=== {tag}  n={n} dist={dist} r={r} phase={phase} ring={ring}')
    show(d)
    print(f'  bbox x{min(xs)}..{max(xs)} y{min(ys)}..{max(ys)}  sym={symmetric(body)}')
    print(f'  ext jumps {profile_ok(body)}  cnt jumps {count_jumps(body)}')
    hist = {}
    for v in d.values():
        hist[v] = hist.get(v, 0) + 1
    print(f'  depth hist {dict(sorted(hist.items()))}')
    for k in range(2, max(d.values()) + 1):
        f = {p for p, v in d.items() if v >= k}
        if not f:
            continue
        fr = rows_of(f)
        fys = sorted(fr)
        span = fys[-1] - fys[0] + 1
        minw = min(len(v) for v in fr.values())
        print(f'   field d>={k}: y{fys[0]}..{fys[-1]} span {span} narrowest row {minw}')
    print()


trial('A6', 6, 5.5, 7.0)
trial('B6', 6, 4.5, 8.0)
trial('C8', 8, 5.5, 7.0)
trial('D5', 5, 5.0, 7.5)
