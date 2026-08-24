import sys, importlib
sys.path.insert(0,'tools')
import c39_sheen as G
exec(open('.scratch-c39/cand6.py').read().split("import sys")[1].split("def build(name,FORM")[0].replace("import math","import math",1)) if False else None
import math
sys.path.insert(0,'.scratch-c39')
from mark_face import FACE
from shade import to_paths

def render(name):
    key=G.keyline(G.DISC); inner=G.DISC-key
    tone=G.despeckle(G.quantise(inner), inner)
    n=len({*tone.values()})
    jump=max(abs(tone[p]-tone[q]) for p in tone for q in ((p[0]+1,p[1]),(p[0],p[1]+1)) if q in tone)
    lone=sum(1 for p,t in tone.items() if all(tone.get(q,t)!=t for q in ((p[0]+1,p[1]),(p[0]-1,p[1]),(p[0],p[1]+1),(p[0],p[1]-1))))
    sym=all((31-x,y) in {q for q,t in tone.items() if t==tone[(x,y)]} for x,y in tone)
    top=[tone[(x,y)] for x,y in tone if y<9]
    print(f'{name}: tones={n} jump={jump} lone={lone} sym={sym} toprange={max(top)-min(top)}')
    parts=[]
    for px,f in [(G.WATER_OUT,'#96bcd6'),(G.WATER_IN,'#5d8cb0')]:
        parts.append(f'<path d="{" ".join(to_paths(px))}" fill="{f}"/>')
    for i,f in enumerate(G.RAMP):
        px={p for p,t in tone.items() if t==i}
        if px: parts.append(f'<path d="{" ".join(to_paths(px))}" fill="{f}"/>')
    parts.append(f'<path d="{" ".join(to_paths(key))}" fill="{G.KEY}"/>')
    open(f'.scratch-c39/{name}.svg','w').write(
      '<svg xmlns="http://www.w3.org/2000/svg" width="288" height="288" viewBox="0 0 32 32" shape-rendering="crispEdges">'
      + ''.join(parts) + FACE + '</svg>')

for name,(BASE,WK,WD,AMP) in {
  'V0':(3.2,3.6,2.2,3.0),
  'V1':(2.9,3.0,2.6,3.0),
  'V2':(2.9,3.0,2.6,3.4),
  'V3':(3.0,2.6,3.0,3.0),
}.items():
    G.BASE,G.W_KEY,G.W_DOME,G.AMP=BASE,WK,WD,AMP
    render(name)
