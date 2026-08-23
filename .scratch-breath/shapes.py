import math, sys
sys.path.insert(0, 'tools')

def disc(cx, cy, r, grid=32):
    return {(x,y) for x in range(grid) for y in range(grid)
            if (x+0.5-cx)**2 + (y+0.5-cy)**2 <= r*r}

def widths(s):
    rows={}
    for x,y in s: rows.setdefault(y,[]).append(x)
    return [(y, max(rows[y])-min(rows[y])+1) for y in sorted(rows)]

def smooth(s, cx=16.0):
    """Rebuild rows centred on cx with |width step| <= 2 everywhere.
    Widths only ever grow, so the shape stays convex-ish and never loses area."""
    w = dict(widths(s))
    ys = sorted(w)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(ys)):
            a, b = ys[i-1], ys[i]
            if w[b] - w[a] > 2:
                w[a] = w[b] - 2; changed = True
            if w[a] - w[b] > 2:
                w[b] = w[a] - 2; changed = True
    out=set()
    for y in ys:
        half = w[y] / 2
        x0 = int(cx - half); x1 = int(cx + half) - 1
        out |= {(x,y) for x in range(x0, x1+1)}
    return out

def maxstep(s):
    w=[q[1] for q in widths(s)]
    return max(abs(w[i]-w[i-1]) for i in range(1,len(w)))

def sym(s):
    return all((31-x, y) in s for x,y in s)

def show(s, grid=32):
    ys=sorted({y for _,y in s})
    for y in range(grid):
        print(f'{y:2} ' + ''.join('#' if (x,y) in s else ('.' if 2<=x<=29 and 2<=y<=29 else ' ') for x in range(grid)))

for r, cy in ((14.0,16),(13.5,16),(13.0,16)):
    raw = disc(16, cy, r)
    s = smooth(raw)
    print(f'--- r={r} cy={cy}  raw maxstep={maxstep(raw)} -> smooth maxstep={maxstep(s)} sym={sym(s)}')
    print('    widths', [q[1] for q in widths(s)])
    xs=[x for x,y in s]; yss=[y for x,y in s]
    print(f'    bbox x{min(xs)}-{max(xs)} y{min(yss)}-{max(yss)}  px={len(s)}')
show(smooth(disc(16,16,14.0)))

print('\n=== distortion scan (pixels added by smoothing) ===')
r=11.0
while r <= 14.2:
    raw = disc(16,16,r); s = smooth(raw)
    xs=[x for x,y in s]; ys=[y for x,y in s]
    add = len(s)-len(raw)
    print(f'r={r:5.2f} w={max(xs)-min(xs)+1} h={max(ys)-min(ys)+1} raw={len(raw)} +{add:3d} cap={dict(widths(s))[min(ys)]} '
          f'widths={[q[1] for q in widths(s)][:8]}')
    r += 0.1
