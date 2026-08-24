import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand8.py').read().split("def build3")[0])

def build4(name,B0,B1,B2,AMP,p,r0,r1,phase=0.0,show=False):
    key=M.keyline(M.DISC); inner=M.DISC-key; tone={}
    for x,y in inner:
        dx=(x+0.5)-CX; dy=(y+0.5)-CY; r=min(1.0,math.hypot(dx,dy)/R); th=math.atan2(dy,dx)
        dome=math.sqrt(max(0.0,1.0-r*r))
        base=B0 + B1*(-dy/R) + B2*dome
        w=(0.5-0.5*math.cos(4*th+phase))**p
        mask=min(1.0,max(0.0,(r-r0)/(r1-r0)))*(1.0-0.5*max(0.0,r-0.88)/0.12)
        tone[(x,y)]=max(0,min(10,int(round(base))+int(round(AMP*w*mask))))
    tone=despeck(tone); report(name,tone,show=show); return tone

build4('J',3.2,3.2,2.2,3.0,0.45,0.10,0.60,0.0,show=True)          # broad diagonal arms
build4('K',3.2,3.2,2.2,3.0,0.70,0.10,0.60,0.0)                    # tighter diagonal arms
build4('L',3.2,3.2,2.2,3.0,0.45,0.10,0.60,math.pi,show=True)      # arms on the cardinals (Mozz's phase)
build4('N',3.0,3.2,2.2,2.0,0.45,0.08,0.55,0.0)                    # broad, gentler
