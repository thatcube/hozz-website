"""Find same-tone components whose whole 8-neighbourhood is strictly darker."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = sys.argv[1] if len(sys.argv) > 1 else 't13'
src = (ROOT / f'src/components/mark/logos/{SLUG}.astro').read_text()
grid = {}
for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]+)"', src):
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        for i in range(w):
            grid[(x + i, y)] = fill
m = re.search(r"facePathsAt\(\{ cx: (\d+), cy: (\d+), size: '(\w+)', smile: '(\w+)', gap: (\d+)", src)
js = (f"import {{facePathsAt}} from '{ROOT}/src/data/mark.ts';"
      f"const o={{cx:{m[1]},cy:{m[2]},size:'{m[3]}',smile:'{m[4]}',gap:{m[5]}}};"
      "console.log(JSON.stringify(facePathsAt(o)));")
paths = json.loads(subprocess.run(['node','--experimental-strip-types','--input-type=module',
    '--no-warnings','-e',js], capture_output=True, text=True, check=True).stdout)
face = set()
for d in paths:
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        face |= {(x + i, y) for i in range(w)}

def lum(h):
    r, g, b = (int(h[i:i+2],16)/255 for i in (1,3,5))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

# only bubble tones; the face is drawn on top and is meant to be brightest
bub = {p: c for p, c in grid.items() if p not in face}
seen = set()
for p0 in sorted(bub, key=lambda q: (q[1], q[0])):
    if p0 in seen: continue
    c = bub[p0]
    comp, stack = set(), [p0]
    while stack:
        p = stack.pop()
        if p in comp: continue
        comp.add(p)
        stack += [(p[0]+dx,p[1]+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))
                  if bub.get((p[0]+dx,p[1]+dy)) == c]
    seen |= comp
    if len(comp) > 8: continue
    border = set()
    for x, y in comp:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                q = (x+dx, y+dy)
                if q in bub and q not in comp:
                    border.add(q)
    if not border: continue
    if all(lum(bub[q]) < lum(c) - 1e-9 for q in border):
        xs = [q[0] for q in comp]; ys = [q[1] for q in comp]
        w, h = max(xs)-min(xs)+1, max(ys)-min(ys)+1
        solid = len(comp) == w*h
        print(f'ISLAND {c} {len(comp)}px  x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)} '
              f'{w}x{h} {"rectangular" if solid else "irregular"}  '
              f'touches face: {bool({(x+dx,y+dy) for x,y in comp for dx in (-1,0,1) for dy in (-1,0,1)} & face)}')
