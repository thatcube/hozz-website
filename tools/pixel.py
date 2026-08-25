"""
Pixel-shape helpers for the Hozz mark concepts.

The family marks are pixel art on a 32x32 grid. Hand-writing every rect is slow
and error-prone, so these build filled shapes as row runs and emit minimal SVG
path strings.

    from tools.pixel import disc, rrect, outline, rows_to_paths, show, sub

    body = disc(15.5, 16.5, 12.4)      # filled pixel circle
    ring = outline(body)                # 1px border around it
    print(rows_to_paths(body))          # -> ["M12 4h7v1h-7z", ...]
    show(body)                          # ASCII preview in the terminal

Never use these for the face. The face is fixed and comes from
src/data/mark.ts via components/mark/Face.astro.
"""

import math, json, sys

def rows_to_paths(rows):
    """rows: dict y -> list of (x0,x1) inclusive runs. Emits minimal SVG rects."""
    out = []
    for y in sorted(rows):
        for x0, x1 in rows[y]:
            out.append(f"M{x0} {y}h{x1-x0+1}v1h-{x1-x0+1}z")
    return out

def disc(cx, cy, r, grid=32):
    """Filled pixel circle -> rows of runs."""
    rows = {}
    for y in range(grid):
        run = []
        for x in range(grid):
            # sample pixel centre
            if (x+0.5-cx)**2 + (y+0.5-cy)**2 <= r*r:
                run.append(x)
        if run:
            rows[y] = [(run[0], run[-1])]
    return rows

def rrect(x0, y0, x1, y1, rad):
    rows = {}
    for y in range(y0, y1+1):
        # how much to inset this row
        dy = 0
        if y < y0+rad: dy = rad - (y-y0)
        elif y > y1-rad: dy = rad - (y1-y)
        inset = 0
        if dy > 0:
            inset = rad - int(math.sqrt(max(rad*rad - (rad-dy)**2, 0)))
        rows[y] = [(x0+inset, x1-inset)]
    return rows

def outline(rows, grid=32):
    """1px outline around a filled row-set."""
    filled = set()
    for y, runs in rows.items():
        for a,b in runs:
            for x in range(a,b+1): filled.add((x,y))
    edge = set()
    for (x,y) in filled:
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(x+dx,y+dy)
            if p not in filled and 0<=p[0]<grid and 0<=p[1]<grid: edge.add(p)
    er = {}
    for (x,y) in sorted(edge, key=lambda p:(p[1],p[0])):
        er.setdefault(y, []).append(x)
    res = {}
    for y, xs in er.items():
        xs.sort(); runs=[]; s=xs[0]; p=xs[0]
        for x in xs[1:]:
            if x==p+1: p=x
            else: runs.append((s,p)); s=x; p=x
        runs.append((s,p)); res[y]=runs
    return res

def show(rows, grid=32):
    filled=set()
    for y,rs in rows.items():
        for a,b in rs:
            for x in range(a,b+1): filled.add((x,y))
    for y in range(grid):
        print(''.join('#' if (x,y) in filled else '.' for x in range(grid)))

if __name__ == '__main__':
    body = disc(16, 16, 12.2)
    print(json.dumps(rows_to_paths(body)))

def sub(a, b, grid=32):
    """a minus b, as row runs."""
    fa = _fill(a, grid); fb = _fill(b, grid)
    return _runs(fa - fb)

def inter(a, b, grid=32):
    return _runs(_fill(a, grid) & _fill(b, grid))

def union(*sets, grid=32):
    out = set()
    for s in sets: out |= _fill(s, grid)
    return _runs(out)

def shrink(rows, n=1, grid=32):
    """Erode by n pixels."""
    f = _fill(rows, grid)
    for _ in range(n):
        f = {p for p in f if all((p[0]+dx, p[1]+dy) in f
                                 for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))}
    return _runs(f)

def _fill(rows, grid=32):
    f = set()
    for y, rs in rows.items():
        for a, b in rs:
            for x in range(a, b+1): f.add((x, y))
    return f

def _runs(filled):
    by = {}
    for x, y in filled: by.setdefault(y, []).append(x)
    out = {}
    for y, xs in by.items():
        xs.sort(); runs = []; s = p = xs[0]
        for x in xs[1:]:
            if x == p+1: p = x
            else: runs.append((s, p)); s = p = x
        runs.append((s, p)); out[y] = runs
    return out
