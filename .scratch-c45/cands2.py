import re, sys, math
from pathlib import Path
ROOT = Path('.').resolve()
sys.path.insert(0, 'tools')
from circles import circle
from shade import keyline, to_paths, rings

DISC = circle(22)
SRC = (ROOT / 'src/components/mark/logos/c10.astro').read_text()
P = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)
def px(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w); s |= {(x+i, y) for i in range(w)}
    return s
WO = set().union(*[px(d) for d, f in P[:26] if f == '#96bcd6'])
WI = set().union(*[px(d) for d, f in P[:26] if f != '#96bcd6'])
KEY = '#132638'
BUILT = (ROOT / '.scratch-c45/dist/logos/index.html').read_text()
svg = re.search(r'<svg[^>]*aria-label="Hozz — Ripple, Lens"[\s\S]*?</svg>', BUILT).group(0)
FACE = re.search(r'<g fill="#132638"[\s\S]*?</g>', svg).group(0)

K = keyline(DISC); inner = DISC - K
CX, CY = 16.0, 13.0
rmax = max(math.hypot(p[0]+.5-CX, p[1]+.5-CY) for p in inner)

def ramp(rim, core, n):
    a = tuple(int(rim[i:i+2],16) for i in (1,3,5)); b = tuple(int(core[i:i+2],16) for i in (1,3,5))
    return ['#%02x%02x%02x' % tuple(round(a[k]+(b[k]-a[k])*i/(n-1)) for k in range(3)) for i in range(n)]
def maxstep(rp):
    return max(max(abs(int(a[i:i+2],16)-int(b[i:i+2],16)) for i in (1,3,5)) for a,b in zip(rp, rp[1:]))

def mark(rim, core, n, mode):
    rp = ramp(rim, core, n)
    if mode == 'radial':
        lv = {p: min(n-1, int(rmax - math.hypot(p[0]+.5-CX, p[1]+.5-CY) + 1e-9)) for p in inner}
        bands = [{p for p,l in lv.items() if l == i} for i in range(n)]
    else:
        bs, core_px = rings(inner, n-1); bands = bs + [core_px]
    layers = [(WO,'#96bcd6'), (WI,'#5d8cb0')] + [(bands[i], rp[i]) for i in range(n)][::-1] + [(K, KEY)]
    body = ''.join(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>' for p,f in layers)
    return rp, f'<svg viewBox="0 0 32 32" shape-rendering="crispEdges" width="SIZE" height="SIZE">{body}{FACE}</svg>'

CANDS = [('R6 #96c2e0','#f2f9fd','#96c2e0',6,'radial'), ('R7 #90bfdc','#f2f9fd','#90bfdc',7,'radial'),
         ('R8 #8ab9d9','#f2f9fd','#8ab9d9',8,'radial'), ('E6 #96c2e0','#edf6fc','#96c2e0',6,'erode')]
cells = []
for name, rim, core, n, mode in CANDS:
    rp, s = mark(rim, core, n, mode)
    print(f'{name}: {n} tones, maxstep {maxstep(rp)}')
    cell = ''.join(f'<div class="c"><div class="{g}">{s.replace("SIZE",str(sz))}</div><span>{sz}</span></div>'
                   for sz,g in [(96,'l'),(48,'l'),(24,'l'),(16,'l'),(96,'d'),(24,'d')])
    cells.append(f'<div class="row"><h2>{name}</h2>{cell}'
                 f'<div class="c"><div class="l z">{s.replace("SIZE","384")}</div><span>96×4</span></div>'
                 f'<div class="c"><div class="l z">{s.replace("SIZE","288")}</div><span>24×12</span></div></div>')
Path('.scratch-c45/cands.html').write_text('<!doctype html><meta charset=utf-8><style>'
 'body{background:#faf8f5;font:12px ui-sans-serif;margin:20px}.row{display:flex;gap:14px;align-items:flex-end;margin-bottom:18px}'
 'h2{width:80px;font-size:11px;margin:0}.c{display:flex;flex-direction:column;align-items:center;gap:4px}'
 '.l{background:#fff;padding:6px;border:1px solid #e6e2dc}.d{background:#14161a;padding:6px}.z svg{image-rendering:pixelated}'
 '</style>' + ''.join(cells))
