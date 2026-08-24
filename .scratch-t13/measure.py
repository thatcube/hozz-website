"""Measure a built mark from its emitted paths — pixel truth, not the model."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'src/components/mark/logos/t13.astro')
text = src.read_text()

RECT = re.compile(r'M(-?\d+) (-?\d+)h(-?\d+)v(-?\d+)h(-?\d+)z')
grid = {}
for d, fill in re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', text):
    for x, y, w, h, _ in RECT.findall(d):
        x, y, w, h = int(x), int(y), int(w), int(h)
        for dx in range(w):
            for dy in range(h):
                grid[(x + dx, y + dy)] = fill

m = re.search(r"facePathsAt\(\{ cx: (\d+), cy: ([\d.]+), size: '(\w+)', smile: '(\w+)', gap: (\d+) \}\)", text)
cx, cy, size, smile, gap = m.groups()
out = subprocess.run(
    ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e',
     f"import {{ facePathsAt, faceBoxAt }} from './src/data/mark.ts';"
     f"const a = {{ cx: {cx}, cy: {cy}, size: '{size}', smile: '{smile}', gap: {gap} }};"
     f"console.log(JSON.stringify({{ paths: facePathsAt(a), box: faceBoxAt(a) }}));"],
    cwd=ROOT, capture_output=True, text=True, check=True)
face = json.loads(out.stdout)
FACE = set()
for d in face['paths']:
    for x, y, w, h, _ in RECT.findall(d):
        x, y, w, h = int(x), int(y), int(w), int(h)
        FACE |= {(x + dx, y + dy) for dx in range(w) for dy in range(h)}
for p in FACE:
    grid[p] = '#ffffff'


def bbox(px):
    xs = [p[0] for p in px]
    ys = [p[1] for p in px]
    return min(xs), max(xs), min(ys), max(ys)


rows = {}
for (x, y) in grid:
    rows.setdefault(y, []).append(x)
rows = {y: (min(v), max(v), max(v) - min(v) + 1) for y, v in sorted(rows.items())}

print(f'== {src.name} ==')
print(f'colours: {len(set(grid.values()))}   pixels: {len(grid)}')
x0, x1, y0, y1 = bbox(grid)
print(f'shape bbox: x{x0}-{x1}  y{y0}-{y1}')
print('row extents (x0..x1, width):')
for y, (a, b, w) in rows.items():
    mid = (a + b + 1) / 2
    print(f'  y{y:>2}  x{a:>2}-{b:<2} w{w:<3} centre {mid:>5}')

white = {p for p, c in grid.items() if c.lower() == '#ffffff'}
wx0, wx1, wy0, wy1 = bbox(white)
print(f'\npure-white pixels: bbox x{wx0}-{wx1} y{wy0}-{wy1} '
      f'(w{wx1 - wx0 + 1}) centre x{(wx0 + wx1 + 1) / 2}')
fx0, fx1, fy0, fy1 = bbox(FACE)
print(f'face module paths: bbox x{fx0}-{fx1} y{fy0}-{fy1} '
      f'(w{fx1 - fx0 + 1}) centre x{(fx0 + fx1 + 1) / 2}')
print(f'face module reports: {face["box"]}')

body_rows = [y for y in rows if rows[y][2] > rows.get(y + 1, (0, 0, 0))[2] or y < fy0]
BODY_Y1 = max(y for y in rows if rows[y][2] >= 16)
print(f'\nbody rows y{y0}-{BODY_Y1}   tail rows y{BODY_Y1 + 1}-{y1}')
print(f'body widest: {max(rows[y][2] for y in rows if y <= BODY_Y1)}')
print(f'air above face: {fy0 - y0} rows (y{y0}-{fy0 - 1})')
print(f'air below face: {BODY_Y1 - fy1} rows (y{fy1 + 1}-{BODY_Y1})')
