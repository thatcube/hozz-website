import sys, math
sys.path.insert(0,'tools')
import c39_sheen as M
from shade import to_paths
def face_px():
    E=[[(0,2)],[(1,2)],[(0,1)],[(0,2)]]
    rows=[[(a,b) for a,b in r]+[(a+5,b+5) for a,b in r] for r in E]+[[],[],[]]
    rows+=[[(0,0),(7,7)],[(0,1),(6,7)],[(1,6)]]
    s=set()
    for i,rr in enumerate(rows):
        for a,b in rr: s|={(12+k,8+i) for k in range(a,b+1)}
    return s
FACE=face_px()
def svg(tone,R):
    key=M.keyline(M.DISC)
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" shape-rendering="crispEdges">']
    for px,f in [(M.WATER_OUT,'#96bcd6'),(M.WATER_IN,'#5d8cb0')]: o.append(f'<path d="{" ".join(to_paths(px))}" fill="{f}"/>')
    for i,f in enumerate(R):
        p={q for q,t in tone.items() if t==i}
        if p: o.append(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>')
    o.append(f'<path d="{" ".join(to_paths(key))}" fill="{M.KEY}"/>')
    o.append(f'<path d="{" ".join(to_paths(FACE))}" fill="{M.KEY}"/></svg>')
    return ''.join(o)
CX,CY,R=16.0,13.0,11.0
RAMP=[M.hsl(208+(194-208)*t,0.36+0.52*t,0.685+0.28*t) for t in [i/10 for i in range(11)]]
def build(name,STRIPE,FORM,EDGE,lo=-1,hi=2,show=False):
    o=lambda n: STRIPE[min(abs(n),len(STRIPE)-1)]
    key=M.keyline(M.DISC); inner=M.DISC-key
    tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=math.hypot(dx,dy)/R
        form=-dy/R; edge=max(0.0,(r-0.66)/0.34)
        base=5.0+FORM*form+EDGE*edge*form
        s=max(lo,min(hi,o(x+y-28)+o(x-y-3)))
        tone[(x,y)]=max(0,min(10,int(round(base))+s))
    sym=all(tone[(31-x,y)]==tone[(x,y)] for x,y in tone)
    jump=max(abs(tone[p]-tone[q]) for p in tone for q in ((p[0]+1,p[1]),(p[0],p[1]+1)) if q in tone)
    lone=sum(1 for p,t in tone.items() if not any(tone.get(q)==t for q in ((p[0]+1,p[1]),(p[0]-1,p[1]),(p[0],p[1]+1),(p[0],p[1]-1))))
    hist=[sum(1 for t in tone.values() if t==i) for i in range(11)]
    print(f'{name}: sym={sym} jump={jump} lone={lone} tones={sum(1 for h in hist if h)} hist={hist}')
    if show:
        for y in range(2,24): print('   '+''.join(('%X'%tone[(x,y)]) if (x,y) in tone else ('#' if (x,y) in M.DISC else '.') for x in range(32)))
    open(f'.scratch-c39/{name}.svg','w').write(svg(tone,RAMP))
#          |n| 0  1  2  3  4  5  6  7  8  9 10 11 12+
S1 =      [ 1, 1, 1, 1, 0, 0, 0,-1,-1,-1, 0, 0, 0]
S2 =      [ 1, 1, 1, 0, 0,-1,-1,-1, 0, 0, 1, 1, 1]
S3 =      [ 1, 1, 1, 1, 1, 0, 0, 0,-1,-1,-1,-1,-1]
build('s-S1',S1,3.6,1.4,show=True)
build('t-S2',S2,3.6,1.4,show=True)
build('u-S3',S3,3.6,1.4)
build('v-S1f',S1,4.2,1.6)
