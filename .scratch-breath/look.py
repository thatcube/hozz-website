import sys; sys.path.insert(0,'.scratch-breath')
from shapes import disc, smooth, widths, maxstep, sym, show
for r in (14.1, 14.0):
    s = smooth(disc(16,16,r))
    print(f'=== smoothed r={r} maxstep={maxstep(s)} sym={sym(s)} n={len(s)}')
    print('widths', [q[1] for q in widths(s)])
    show(s)
