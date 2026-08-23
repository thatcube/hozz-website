"""Search (n, dist, r, K) for a deep core that holds the face with equal air."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab import rosette, clamp_profile, profile_ok, rows_of, GEOM

FACE_W = {'lg': 10, 'md': 8, 'sm': 7}


def fit(field, size):
    """Return (gap, h, cy, air) if the face fits with equal air, else None."""
    fr = rows_of(field)
    fys = sorted(fr)
    if not fys:
        return None
    span = fys[-1] - fys[0] + 1
    w = FACE_W[size]
    for gap in (2, 3, 1, 4):
        h, off = GEOM[size][gap]
        if (span - h) % 2 or span <= h:
            continue
        pad = (span - h) // 2
        top = fys[0] + pad
        ok = True
        for y in range(top, top + h):
            xs = fr.get(y, [])
            if not xs:
                ok = False
                break
            lo, hi = 16 - w // 2, 16 + (w - w // 2) - 1
            if any((x, y) not in field for x in range(lo, hi + 1)):
                ok = False
                break
        if ok:
            return (gap, h, top - off, pad)
    return None


rows = []
for n in (5, 6, 8):
    for dist10 in range(25, 76, 5):
        dist = dist10 / 10
        for r10 in range(55, 101, 5):
            r = r10 / 10
            if dist + r > 13.6 or r <= dist * 0.55:
                continue
            d = rosette(n, 16.0, dist, r)
            body = clamp_profile(set(d))
            d = {p: v for p, v in d.items() if p in body}
            xs = [p[0] for p in body]
            ys = [p[1] for p in body]
            if min(xs) < 2 or max(xs) > 29 or min(ys) < 2 or max(ys) > 29:
                continue
            if profile_ok(body):
                continue
            mx = max(d.values())
            hist = {}
            for v in d.values():
                hist[v] = hist.get(v, 0) + 1
            for K in range(2, mx + 1):
                field = {p for p, v in d.items() if v >= K}
                bands = sorted({v for v in d.values() if v < K})
                if len(bands) < 3:
                    continue
                if min(hist[b] for b in bands) < 12:
                    continue
                for size in ('md', 'sm'):
                    f = fit(field, size)
                    if f:
                        gap, h, cy, pad = f
                        rows.append((n, dist, r, K, size, gap, h, cy, pad,
                                     len(bands), len(field),
                                     max(ys) - min(ys) + 1, tuple(sorted(hist.items()))))

print(f'{len(rows)} candidates')
for row in rows[:400]:
    n, dist, r, K, size, gap, h, cy, pad, nb, nf, hgt, hist = row
    print(f'n={n} dist={dist:4} r={r:4} K={K} {size} gap{gap} h{h} cy{cy} air{pad} '
          f'bands{nb} field{nf} tall{hgt} hist={hist}')
