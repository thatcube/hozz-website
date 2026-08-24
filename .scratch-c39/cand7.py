import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand6.py').read().split("def build(name,FORM")[0])

def build2(name,B1,B2,AMP,STR,r0,r1,B0=4.6,show=False):
    o=lambda n: STR[min(abs(n),len(STR)-1)]
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=min(1.0,math.hypot(dx,dy)/R)
        dome=math.sqrt(max(0.0,1.0-r*r))
        base=B0 + B1*(-dy/R) + B2*dome
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0)))
        s=max(o(x+y-28),o(x-y-3))
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*s*mask))))
    report(name,tone,show=show); return tone

STR=[1.0,1.0,1.0,0.85,0.6,0.3,0.1,0.0]
STR2=[1.0,1.0,0.95,0.8,0.55,0.25,0.0,0.0]
build2('A-dome', 2.6,2.2,2.0,STR, 0.18,0.42,show=True)
build2('B-dome3',2.4,2.0,3.0,STR, 0.18,0.45,show=True)
build2('C-dome',2.8,1.6,2.0,STR2,0.20,0.46)
build2('D-domeflat',2.2,2.6,2.0,STR,0.18,0.42)
