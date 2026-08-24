import re, sys
from pathlib import Path
ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT / 'tools'))
from circles import circle
from shade import rings, keyline, to_paths

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

def ramp(rim, core, n):
    r = tuple(int(rim[i:i+2], 16) for i in (1, 3, 5))
    c = tuple(int(core[i:i+2], 16) for i in (1, 3, 5))
    return ['#%02x%02x%02x' % tuple(round(r[k] + (c[k]-r[k])*i/(n-1)) for k in range(3)) for i in range(n)]

def maxstep(rp):
    return max(max(abs(int(a[i:i+2],16)-int(b[i:i+2],16)) for i in (1,3,5)) for a, b in zip(rp, rp[1:]))

def mark(rim, core, n):
    rp = ramp(rim, core, n)
    K = keyline(DISC); inner = DISC - K
    bands, core_px = rings(inner, n-1)
    layers = [(WO, '#96bcd6'), (WI, '#5d8cb0'), (core_px, rp[-1])]
    layers += [(b, rp[i]) for i, b in enumerate(bands)][::-1] + [(K, KEY)]
    body = '\n'.join(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>' for p, f in layers)
    return rp, f'<svg viewBox="0 0 32 32" shape-rendering="crispEdges" width="SIZE" height="SIZE">{body}{FACE}</svg>'

CANDS = [('A current', '#f2f9fd', '#a6cbe4', 6), ('B deeper', '#edf6fc', '#96c2e0', 6),
         ('C long 7', '#f2f9fd', '#8ebdda', 7), ('D long 8', '#f4fafe', '#87b9d8', 8)]
cells = []
for name, rim, core, n in CANDS:
    rp, s = mark(rim, core, n)
    print(f'{name}: {n} tones, maxstep {maxstep(rp)} — {" ".join(rp)}')
    cell = ''.join(f'<div class="c"><div class="{g}">{s.replace("SIZE", str(sz))}</div><span>{sz}</span></div>'
                   for sz, g in [(96,'l'),(48,'l'),(24,'l'),(16,'l'),(96,'d'),(24,'d')])
    zoom = f'<div class="c"><div class="l z">{s.replace("SIZE", "288")}</div><span>24×12</span></div>'
    cells.append(f'<div class="row"><h2>{name}<br><small>{n} tones</small></h2>{cell}{zoom}</div>')
Path('.scratch-c45/cands.html').write_text('<!doctype html><meta charset=utf-8><style>'
 'body{background:#faf8f5;font:12px ui-sans-serif;margin:20px}.row{display:flex;gap:16px;align-items:flex-end;margin-bottom:20px}'
 'h2{width:90px;font-size:12px;margin:0}.c{display:flex;flex-direction:column;align-items:center;gap:4px}'
 '.l{background:#fff;padding:8px;border:1px solid #e6e2dc}.d{background:#14161a;padding:8px}.z svg{image-rendering:pixelated}'
 '</style>' + ''.join(cells))
