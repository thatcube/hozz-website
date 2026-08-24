import re, sys
from pathlib import Path
sys.path.insert(0, 'tools')
src = Path('.briefs/twozz-shipped.svg').read_text()
px = {}
for m in re.finditer(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"[^>]*fill="([^"]+)"', src):
    x,y,w,h,f = int(m[1]),int(m[2]),int(m[3]),int(m[4]),m[5]
    for j in range(h):
        for i in range(w):
            px[(x+i,y+j)] = f
if not px:
    print('no rects; head:'); print(src[:400]); sys.exit()
fills = {}
for p,f in px.items(): fills.setdefault(f,set()).add(p)
print('fills:', {f: len(s) for f,s in fills.items()})
ys = sorted({y for _,y in px})
for y in ys:
    xs = sorted(x for x,yy in px if yy==y)
    print(f'{y:3d} x{xs[0]:2d}-{xs[-1]:2d} w={xs[-1]-xs[0]+1:2d}  ' + ''.join(
        ('.' if (x,y) not in px else {f:c for c,f in enumerate(fills)}[px[(x,y)]].__str__()) for x in range(32)))
