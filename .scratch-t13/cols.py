import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / 'src/components/mark/logos/t13.astro').read_text()
grid = {}
for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]+)"', src):
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        for i in range(w): grid[(x+i, y)] = fill
def lum(h):
    r, g, b = (int(h[i:i+2],16)/255 for i in (1,3,5))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
rank = {c: i for i, c in enumerate(sorted(set(grid.values()), key=lum))}
sym = '0123456789abcd'
cols = [int(a) for a in sys.argv[1:]] or [2,3,4,25,26,27,28,29]
print('  y ' + ' '.join(f'x{c:<3}' for c in cols))
for y in range(2, 27):
    cells = []
    for c in cols:
        v = grid.get((c, y))
        cells.append(f'{sym[rank[v]]}    ' if v else '.    ')
    print(f'{y:>3} ' + ' '.join(s[:4] for s in cells))
