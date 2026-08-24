import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = sys.argv[1] if len(sys.argv) > 1 else 't13'
src = (ROOT / f'src/components/mark/logos/{SLUG}.astro').read_text()
grid, order = {}, []
for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]+)"', src):
    if fill not in order: order.append(fill)
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        for i in range(w): grid[(x+i, y)] = fill
def lum(h):
    r, g, b = (int(h[i:i+2],16)/255 for i in (1,3,5))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
rank = {c: i for i, c in enumerate(sorted(set(grid.values()), key=lum))}
sym = '0123456789abcdefghij'
print('    ' + ''.join(str(x%10) for x in range(32)))
for y in range(32):
    row = ''.join(sym[rank[grid[(x,y)]]] if (x,y) in grid else '.' for x in range(32))
    if row.strip('.'): print(f'{y:>3} {row}')
print()
for c, i in sorted(rank.items(), key=lambda t: t[1]):
    print(f'  {sym[i]} {c}  lum {lum(c):.4f}  vs white {(1.05)/(lum(c)+0.05):.2f}:1  n={sum(1 for p in grid if grid[p]==c)}')
