"""Explore the rosette space: silhouette profile, symmetry, protrusions."""
import math

GRID = 32


def circle(cx, cy, r):
    rr = r * r
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr}


def petal_centres(n, cx, cy, dist, phase=-math.pi / 2):
    out = []
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        dx = round(dist * math.cos(a), 6)
        dy = round(dist * math.sin(a), 6)
        out.append((cx + dx, cy + dy))
    return out


def rosette(n, cx, cy, dist, r, phase=-math.pi / 2):
    depth = {}
    for (px, py) in petal_centres(n, cx, cy, dist, phase):
        for p in circle(px, py, r):
            depth[p] = depth.get(p, 0) + 1
    return depth


def rowwidths(body):
    rows = {}
    for x, y in body:
        rows.setdefault(y, []).append(x)
    return {y: (min(v), max(v), max(v) - min(v) + 1, len(v)) for y, v in sorted(rows.items())}


def protrusion(body):
    rw = rowwidths(body)
    ys = sorted(rw)
    bad = []
    prev = None
    for y in ys:
        w = rw[y][2]
        if prev is not None and w - prev > 2:
            bad.append((y, prev, w))
        prev = w
    return bad


def symmetric(body):
    return all((31 - x, y) in body for x, y in body)


def show(depth, grid=GRID):
    ys = sorted({y for (_, y) in depth})
    xs = sorted({x for (x, _) in depth})
    print('     ' + ''.join(str(i % 10) for i in range(grid)))
    for y in range(min(ys), max(ys) + 1):
        line = ''
        for x in range(grid):
            d = depth.get((x, y), 0)
            line += '.' if d == 0 else str(d)
        print(f'{y:3}  {line}')
    print(f'  x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}  maxdepth {max(depth.values())}')


def report(tag, n, dist, r, cy=16.0, phase=-math.pi / 2):
    d = rosette(n, 16.0, cy, dist, r, phase)
    body = set(d)
    print(f'=== {tag}: n={n} dist={dist} r={r} cy={cy} phase={round(math.degrees(phase))}')
    show(d)
    print('  sym', symmetric(body), ' protrusions', protrusion(body))
    hist = {}
    for v in d.values():
        hist[v] = hist.get(v, 0) + 1
    print('  depth hist', dict(sorted(hist.items())))
    print()


report('A', 6, 5.5, 7.0)
report('B', 6, 4.5, 8.0)
report('C', 8, 5.5, 7.0)
report('D', 5, 5.0, 7.5)
report('E', 6, 6.5, 6.5)
