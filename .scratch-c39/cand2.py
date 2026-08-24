import sys, math
sys.path.insert(0, 'tools')
import c39_sheen as M
from shade import to_paths
exec(open('.scratch-c39/cand.py').read().split('def svg')[0].split('import sys')[1].replace('import c39_sheen as M','',1).replace(', math, json','',1)) if False else None

def face_px():
    E=[[(0,2)],[(1,2)],[(0,1)],[(0,2)]]
    rows=[[(a,b) for a,b in r]+[(a+5,b+5) for a,b in r] for r in E]+[[],[],[]]
    rows+=[[(0,0),(7,7)],[(0,1),(6,7)],[(1,6)]]
    s=set()
    for i,rr in enumerate(rows):
        for a,b in rr:
            s|={(12+k,8+i) for k in range(a,b+1)}
    return s
FACE=face_px()

def svg(tone, ramp):
    key=M.keyline(M.DISC)
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" shape-rendering="crispEdges">']
    for px,f in [(M.WATER_OUT,'#96bcd6'),(M.WATER_IN,'#5d8cb0')]:
        o.append(f'<path d="{" ".join(to_paths(px))}" fill="{f}"/>')
    for i,f in enumerate(ramp):
        p={q for q,t in tone.items() if t==i}
        if p: o.append(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>')
    o.append(f'<path d="{" ".join(to_paths(key))}" fill="{M.KEY}"/>')
    o.append(f'<path d="{" ".join(to_paths(FACE))}" fill="{M.KEY}"/></svg>')
    return ''.join(o)

CX,CY,R = 16.0,13.0,11.0
def build(name, prof, FORM, SHEEN, EDGE, show=False):
    def g(t):
        a=abs(t)
        for lim,v in prof:
            if a < lim: return v
        return prof[-1][1]
    key=M.keyline(M.DISC); inner=M.DISC-key
    tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=math.hypot(dx,dy)/R
        form=-dy/R
        t1=(dx+dy)*0.7071; t2=(dx-dy)*0.7071
        edge=max(0.0,(r-0.66)/0.34)
        lev = 4.0 + FORM*form + SHEEN*0.5*(g(t1)+g(t2)) + EDGE*edge*form
        tone[(x,y)] = max(0, min(8, int(round(lev))))
    for x,y in tone: assert tone[(31-x,y)]==tone[(x,y)], name
    jump=max(abs(tone[p]-tone[q]) for p in tone for q in ((p[0]+1,p[1]),(p[0],p[1]+1)) if q in tone)
    hist=[sum(1 for t in tone.values() if t==i) for i in range(9)]
    print(f'{name}: jump={jump} hist={hist} tones={sum(1 for h in hist if h)}')
    if show:
        for y in range(2,24):
            print('   '+''.join(str(tone[(x,y)]) if (x,y) in tone else ('#' if (x,y) in M.DISC else '.') for x in range(32)))
    open(f'.scratch-c39/{name}.svg','w').write(svg(tone,M.RAMP))

P_X  = [(2.5,1.0),(4.5,0.3),(7.0,-0.6),(9.5,-0.1),(99,0.4)]
P_X2 = [(3.0,1.0),(5.5,0.2),(8.0,-0.7),(99,0.2)]
P_W  = [(2.0,1.0),(4.0,0.55),(6.0,0.0),(8.0,-0.6),(99,-0.2)]
build('f-stair', P_X,  2.6, 2.2, 1.0, show=True)
build('g-stair2',P_X2, 2.6, 2.4, 1.0, show=True)
build('h-wide',  P_W,  2.4, 2.6, 1.0, show=True)
build('i-soft',  P_X,  2.9, 1.7, 1.1)
build('j-hard',  P_X2, 2.2, 3.0, 0.9)
