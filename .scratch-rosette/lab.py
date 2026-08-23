"""Rosette geometry lab: clamped silhouettes, depth fields, face fit."""
import math

GRID = 32
CX = 16.0

GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
    'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
}


def disc(cx, cy, r):
    rr = r * r
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr}


def annulus(cx, cy, r, t):
    rr, ri = r * r, (r - t) * (r - t)
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if ri < (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr}


def centres(n, cy, dist, phase=-90.0):
    out = []
    for i in range(n):
        a = math.radians(phase + i * 360.0 / n)
        out.append((CX + round(dist * math.cos(a), 6), cy + round(dist * math.sin(a), 6)))
    return out


def rosette(n, cy, dist, r, phase=-90.0, ring=None):
    depth = {}
    for (px, py) in centres(n, cy, dist, phase):
        pet = disc(px, py, r) if ring is None else annulus(px, py, r, ring)
        for p in pet:
            depth[p] = depth.get(p, 0) + 1
    return depth


def rows_of(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: sorted(v) for y, v in sorted(rows.items())}


def widths(s):
    return {y: xs[-1] - xs[0] + 1 for y, xs in rows_of(s).items()}


def clamp_profile(body, both=True):
    """Trim rows so no row is more than 2 wider than the row above (and, when
    `both`, than the row below). Rows stay centred on x=16, so symmetry holds."""
    w = widths(body)
    ys = sorted(w)
    for y in ys[1:]:
        if y - 1 in w:
            w[y] = min(w[y], w[y - 1] + 2)
    if both:
        for y in reversed(ys[:-1]):
            if y + 1 in w:
                w[y] = min(w[y], w[y + 1] + 2)
        # re-run downward in case the upward pass loosened nothing
        for y in ys[1:]:
            if y - 1 in w:
                w[y] = min(w[y], w[y - 1] + 2)
    out = set()
    for y in ys:
        half = w[y] / 2.0
        lo, hi = int(CX - half), int(CX + half) - 1
        out |= {(x, y) for x in range(lo, hi + 1) if (x, y) in body}
    return out


def profile_ok(body):
    w = widths(body)
    ys = sorted(w)
    bad = []
    for i in range(1, len(ys)):
        if ys[i] != ys[i - 1] + 1:
            continue
        if w[ys[i]] - w[ys[i - 1]] > 2:
            bad.append((ys[i], w[ys[i - 1]], w[ys[i]]))
    return bad


def count_jumps(body):
    r = rows_of(body)
    ys = sorted(r)
    bad = []
    for i in range(1, len(ys)):
        if ys[i] != ys[i - 1] + 1:
            continue
        if len(r[ys[i]]) - len(r[ys[i - 1]]) > 2:
            bad.append((ys[i], len(r[ys[i - 1]]), len(r[ys[i]])))
    return bad


def symmetric(s):
    return all((31 - x, y) in s for x, y in s)


def show(depth, extra=None, grid=GRID):
    ys = sorted({y for (_, y) in depth})
    print('     ' + ''.join(str(i % 10) for i in range(grid)))
    for y in range(min(ys), max(ys) + 1):
        line = ''
        for x in range(grid):
            if extra and (x, y) in extra:
                line += '#'
            else:
                d = depth.get((x, y), 0)
                line += '.' if d == 0 else str(d)
        print(f'{y:3}  {line}')
