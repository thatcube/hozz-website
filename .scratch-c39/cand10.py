import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand9.py').read().split("def build4")[0])

def build5(name,B0,B1,B2,AMP,STR,r0,r1,show=False):
    o=lambda n: STR[min(abs(n),len(STR)-1)]
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=min(1.0,math.hypot(dx,dy)/R)
        dome=math.sqrt(max(0.0,1.0-r*r))
        base=B0 + B1*(-dy/R) + B2*dome
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0)))
        s=max(o(x+y-28),o(x-y-3))
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*s*mask))))
    tone=despeck(tone); report(name,tone,show=show); return tone

WIDE=[1.0,1.0,1.0,1.0,0.9,0.7,0.45,0.2,0.05,0.0]
MID =[1.0,1.0,1.0,0.9,0.7,0.45,0.2,0.0]
build5('P',3.2,3.2,2.2,3.0,WIDE,0.10,0.60,show=True)
build5('Q',3.2,3.2,2.2,3.0,MID ,0.10,0.60,show=True)
build5('S',3.0,3.2,2.2,3.0,WIDE,0.06,0.70)
