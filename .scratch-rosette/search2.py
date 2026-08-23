"""Strict search: equal air in the core field AND in the whole silhouette."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab import rosette, clamp_profile, profile_ok, rows_of, GEOM

FACE_W = {'lg': 10, 'md': 8, 'sm': 7}


def face_fit(field, body, size, pad_min=1):
    fr = rows_of(field)
    fys = sorted(fr)
    if not fys or fys[-1] - fys[0] + 1 != len(fys):
        return None
    span = fys[-1] - fys[0] + 1
    bys = sorted({y for _, y in body})
    btop, bbot = bys[0], bys[-1]
    w = FACE_W[size]
    lo, hi = 16 - w // 2, 16 + (w - w // 2) - 1
    for gap in (2, 3, 1, 4):
        h, off = GEOM[size][gap]
        if span <= h or (span - h) % 2:
            continue
        pad = (span - h) // 2
        if pad < pad_min:
            continue
        top = fys[0] + pad
        if any((x, y) not in field for y in range(top, top + h) for x in range(lo, hi + 1)):
            continue
        above, below = top - btop, bbot - (top + h - 1)
        if above != below:
            continue
        return dict(gap=gap, h=h, cy=top - off, pad=pad, above=above, below=below, size=size)
    return None


def scan(ns=(5, 6, 8), dmin=2.5, dmax=7.5, want=None):
    out = []
    for n in ns:
        phases = (-90.0, 90.0) if n % 2 else (-90.0,)
        for phase in phases:
            for d10 in range(int(dmin * 10), int(dmax * 10) + 1, 5):
                dist = d10 / 10
                for r10 in range(55, 106, 5):
                    r = r10 / 10
                    if r <= dist * 0.6:
                        continue
                    for cy2 in range(28, 37):
                        cy = cy2 / 2
                        dep = rosette(n, cy, dist, r, phase)
                        body = clamp_profile(set(dep))
                        dep = {p: v for p, v in dep.items() if p in body}
                        xs = [p[0] for p in body]
                        ys = [p[1] for p in body]
                        if min(xs) < 2 or max(xs) > 29 or min(ys) < 2 or max(ys) > 29:
                            continue
                        if profile_ok(body):
                            continue
                        hist = {}
                        for v in dep.values():
                            hist[v] = hist.get(v, 0) + 1
                        mx = max(dep.values())
                        for K in range(3, mx + 1):
                            field = {p for p, v in dep.items() if v >= K}
                            bands = [b for b in sorted(hist) if b < K]
                            if len(bands) < 3 or min(hist[b] for b in bands) < 14:
                                continue
                            for size in ('md', 'sm'):
                                f = face_fit(field, body, size)
                                if f:
                                    f.update(n=n, phase=phase, dist=dist, r=r, cy=cy,
                                             K=K, bands=len(bands),
                                             tall=max(ys) - min(ys) + 1,
                                             wide=max(xs) - min(xs) + 1,
                                             hist=tuple(sorted(hist.items())))
                                    out.append(f)
    return out


if __name__ == "__main__":
    res = scan() if __name__ == "__main__" else []
    print(len(res), 'strict candidates')
    res.sort(key=lambda f: (-f['dist'], -f['bands']))
    seen = set()
    for f in res:
        k = (f['n'], f['dist'], f['r'], f['K'], f['size'])
        if k in seen:
            continue
        seen.add(k)
        print(f"n={f['n']} ph={f['phase']:+.0f} dist={f['dist']:4} r={f['r']:4} cy={f['cy']:4} "
              f"K={f['K']} {f['size']} gap{f['gap']} h{f['h']} facecy={f['cy']} "
              f"pad{f['pad']} air{f['above']}/{f['below']} bands{f['bands']} "
              f"{f['wide']}x{f['tall']} hist={f['hist']}")
