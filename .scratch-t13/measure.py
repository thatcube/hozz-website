"""Measure t13 from the emitted paths, not the model."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = sys.argv[1] if len(sys.argv) > 1 else 't13'
src = (ROOT / f'src/components/mark/logos/{SLUG}.astro').read_text()

grid = {}
order = []
for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]+)"', src):
    if fill not in order:
        order.append(fill)
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        for i in range(w):
            grid[(x + i, y)] = fill

# face straight out of mark.ts
m = re.search(r"facePathsAt\(\{ cx: (\d+), cy: (\d+), size: '(\w+)', smile: '(\w+)', gap: (\d+)", src)
cx, cy, size, smile, gap = int(m[1]), int(m[2]), m[3], m[4], int(m[5])
js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
      f"const o={{cx:{cx},cy:{cy},size:'{size}',smile:'{smile}',gap:{gap}}};"
      "console.log(JSON.stringify({box:faceBoxAt(o),paths:facePathsAt(o)}));")
got = json.loads(subprocess.run(['node','--experimental-strip-types','--input-type=module',
    '--no-warnings','-e',js], capture_output=True, text=True, check=True).stdout)
face = set()
for d in got['paths']:
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        face |= {(x + i, y) for i in range(w)}
for p in face:
    grid[p] = '#ffffff'

shape = set(grid)
rows = {}
for x, y in shape:
    rows.setdefault(y, []).append(x)

print(f'== {SLUG} measured from {SLUG}.astro ==')
print(f'tones: {len(set(grid.values()))}  ({len(order)} bubble + face white)')
for y in sorted(rows):
    xs = sorted(rows[y])
    c = (min(xs) + max(xs)) / 2
    print(f'  y{y:>2} x{min(xs):>2}-{max(xs):<2} w{max(xs)-min(xs)+1:<2} centre x{c:<5}')

body_rows = [y for y in rows if max(rows[y]) - min(rows[y]) + 1 > 10]
by0, by1 = min(body_rows), max(body_rows)
bw = max(max(rows[y]) - min(rows[y]) + 1 for y in body_rows)
print(f'body y{by0}-{by1}  widest {bw}')
# symmetry of the body rows only
bad = [y for y in body_rows if [31-x for x in rows[y]] != sorted(rows[y], reverse=True)]
print(f'body symmetry about x=16: {"OK" if not bad else bad}')

fx = [x for x, _ in face]; fy = [y for _, y in face]
print(f'face box x{min(fx)}-{max(fx)} y{min(fy)}-{max(fy)}  {max(fx)-min(fx)+1}x{max(fy)-min(fy)+1}'
      f'  centre x{(min(fx)+max(fx))/2}')
print(f'white pixels bbox x{min(fx)}-{max(fx)} (same set: {set((x,y) for x,y in grid if grid[(x,y)]=="#ffffff")==face})')
print(f'air {min(fy)-by0} above / {by1-max(fy)} below')
print(f'parity: body {bw} face {max(fx)-min(fx)+1} -> {"ok" if (bw-(max(fx)-min(fx)+1))%2==0 else "MISMATCH"}')

# spurs
W = {y: max(rows[y])-min(rows[y])+1 for y in rows}
ys = sorted(W)
spurs = [ys[i] for i in range(1, len(ys)-1) if W[ys[i]] > W[ys[i-1]] and W[ys[i]] > W[ys[i+1]]]
print(f'spurs: {spurs or "none"}')

# luminance helper
def lum(h):
    r, g, b = (int(h[i:i+2],16)/255 for i in (1,3,5))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

# contrast of the face against every tone it touches (incl. diagonal neighbours)
touch = set()
for x, y in face:
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            q = (x+dx, y+dy)
            if q in grid and q not in face:
                touch.add(grid[q])
worst = max(touch, key=lum)
cr = (lum('#ffffff')+0.05)/(lum(worst)+0.05)
print(f'face contrast: worst neighbour {worst} -> {cr:.2f}:1  {"PASS" if cr>=4.5 else "FAIL"}')
allt = {grid[p] for p in grid if p not in face}
w2 = max(allt, key=lum)
print(f'  (palest tone anywhere {w2} -> {(lum("#ffffff")+0.05)/(lum(w2)+0.05):.2f}:1)')

# floating brighter-than-everything-around islands
rank = {c: i for i, c in enumerate(sorted(set(grid.values()), key=lum))}
iso = []
for p in grid:
    if p in face: continue
    x, y = p
    nb = [grid[q] for q in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)) if q in grid and q not in face]
    if nb and all(rank[grid[p]] > rank[n] for n in nb):
        iso.append((p, grid[p]))
print(f'strictly-brighter-than-all-4-neighbours pixels: {len(iso)}')
for p, c in sorted(iso, key=lambda t: (t[0][1], t[0][0])):
    print(f'   {p} {c}')
