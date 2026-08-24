import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand6.py').read().split("def build(name,FORM")[0])

def despeck(tone):
    for _ in range(4):
        nxt=dict(tone); ch=0
        for p,t in tone.items():
            ns=[tone[q] for q in ((p[0]+1,p[1]),(p[0]-1,p[1]),(p[0],p[1]+1),(p[0],p[1]-1)) if q in tone]
            if len(ns)==4 and t not in ns:
                nxt[p]=sorted(ns)[2]; ch+=1
        tone=nxt
        if not ch: break
    return tone

def build3(name,B0,B1,B2,AMP,STR,r0,r1,show=False):
    o=lambda n: STR[min(abs(n),len(STR)-1)]
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=min(1.0,math.hypot(dx,dy)/R)
        dome=math.sqrt(max(0.0,1.0-r*r))
        base=B0 + B1*(-dy/R) + B2*dome
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0)))
        s=max(o(x+y-28),o(x-y-3))
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*s*mask))))
    tone=despeck(tone)
    report(name,tone,show=show); return tone

STR=[1.0,1.0,1.0,0.85,0.6,0.3,0.1,0.0]
build3('E', 3.4,3.2,2.2,2.0,STR,0.18,0.42,show=True)
build3('F', 3.2,3.4,1.8,2.0,STR,0.18,0.42,show=True)
build3('G', 3.4,3.2,2.2,3.0,STR,0.18,0.46,show=True)
build3('H', 3.6,3.0,2.4,2.0,STR,0.22,0.50)
