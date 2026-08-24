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
RAMP=[M.hsl(208-14*t,0.36+0.52*t,0.685+0.28*t) for t in [i/10 for i in range(11)]]
def report(name,tone,N=11,show=False):
    sym=all(tone[(31-x,y)]==tone[(x,y)] for x,y in tone)
    jump=max(abs(tone[p]-tone[q]) for p in tone for q in ((p[0]+1,p[1]),(p[0],p[1]+1)) if q in tone)
    lone=sum(1 for p,t in tone.items() if not any(tone.get(q)==t for q in ((p[0]+1,p[1]),(p[0]-1,p[1]),(p[0],p[1]+1),(p[0],p[1]-1))))
    hist=[sum(1 for t in tone.values() if t==i) for i in range(N)]
    print(f'{name}: sym={sym} jump={jump} lone={lone} tones={sum(1 for h in hist if h)} hist={hist}')
    if show:
        for y in range(2,24): print('   '+''.join(('%X'%tone[(x,y)]) if (x,y) in tone else ('#' if (x,y) in M.DISC else '.') for x in range(32)))
    open(f'.scratch-c39/{name}.svg','w').write(svg(tone,RAMP))

def build(name,FORM,EDGE,AMP,sharp,r0,r1,show=False):
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=math.hypot(dx,dy)/R; th=math.atan2(dy,dx)
        form=-dy/R; edge=max(0.0,(r-0.66)/0.34)
        base=4.4+FORM*form+EDGE*edge*form
        w=max(0.0,-math.cos(4*th))**sharp
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0))) * (1.0-0.45*max(0.0,r-0.86)/0.14)
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*w*mask))))
    report(name,tone,show=show); return tone

def build_str(name,FORM,EDGE,AMP,STR,r0,r1,show=False):
    o=lambda n: STR[min(abs(n),len(STR)-1)]
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=math.hypot(dx,dy)/R
        form=-dy/R; edge=max(0.0,(r-0.66)/0.34)
        base=4.4+FORM*form+EDGE*edge*form
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0)))
        s=max(o(x+y-28),o(x-y-3))
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*s*mask))))
    report(name,tone,show=show); return tone

build('w-wedge',3.6,1.4,2.0,0.7,0.20,0.45,show=True)
build('x-wedge3',3.4,1.4,3.0,0.9,0.20,0.50,show=True)
#            |n| 0    1    2    3    4    5    6    7+
STR=[1.0,1.0,1.0,0.85,0.6,0.3,0.1,0.0]
build_str('y-strp',3.6,1.4,2.0,STR,0.18,0.42,show=True)
build_str('z-strp3',3.4,1.4,3.0,STR,0.18,0.45)
