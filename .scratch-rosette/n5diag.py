"""Why does n=5 fail? Print body span, field span and their centres."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab import rosette, clamp_profile, profile_ok, rows_of, GEOM

FACE_W = {'lg': 10, 'md': 8, 'sm': 7}

best = []
for phase in (-90.0, 90.0):
    for d10 in range(30, 66, 5):
        dist = d10 / 10
        for r10 in range(60, 106, 5):
            r = r10 / 10
            if r <= dist * 0.6:
                continue
            for cy2 in range(28, 37):
                cy = cy2 / 2
                dep = rosette(5, cy, dist, r, phase)
                body = clamp_profile(set(dep))
                dep = {p: v for p, v in dep.items() if p in body}
                xs = [p[0] for p in body]
                ys = [p[1] for p in body]
                if min(xs) < 2 or max(xs) > 29 or min(ys) < 2 or max(ys) > 29:
                    continue
                if profile_ok(body):
                    continue
                btop, bbot = min(ys), max(ys)
                for K in range(3, 6):
                    field = {p for p, v in dep.items() if v >= K}
                    fr = rows_of(field)
                    fys = sorted(fr)
                    if not fys or fys[-1] - fys[0] + 1 != len(fys):
                        continue
                    fspan = fys[-1] - fys[0] + 1
                    for size in ('md', 'sm'):
                        w = FACE_W[size]
                        lo, hi = 16 - w // 2, 16 + (w - w // 2) - 1
                        for gap in (1, 2, 3, 4):
                            h, off = GEOM[size][gap]
                            if fspan <= h:
                                continue
                            # face top by field-centring, and by body-centring
                            if (fspan - h) % 2 == 0:
                                top_f = fys[0] + (fspan - h) // 2
                            else:
                                top_f = None
                            bspan = bbot - btop + 1
                            top_b = btop + (bspan - h) // 2 if (bspan - h) % 2 == 0 else None
                            if top_f is None or top_b is None:
                                continue
                            if any((x, y) not in field for y in range(top_f, top_f + h)
                                   for x in range(lo, hi + 1)):
                                continue
                            best.append((abs(top_f - top_b), phase, dist, r, cy, K, size,
                                         gap, h, fspan, bspan, top_f, top_b))
best.sort()
print(f'{len(best)} near-misses; smallest offsets first')
for b in best[:40]:
    off, phase, dist, r, cy, K, size, gap, h, fspan, bspan, tf, tb = b
    print(f'delta={off} ph={phase:+.0f} dist={dist} r={r} cy={cy} K={K} {size} gap{gap} '
          f'h{h} fieldspan{fspan} bodyspan{bspan} topfield{tf} topbody{tb}')
