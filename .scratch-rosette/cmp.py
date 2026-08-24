import sys, json
sys.path.insert(0,'tools')
import breath_rosette as B
G={'six':dict(n=6,dist=7.0,size=14,phase=0.0,bite=True,K=3,merge=[0,0,1,2,3,4,5,6,7]),
   'eight':dict(n=8,dist=6.0,size=14,phase=-67.5,K=6,merge=[0,0,1,2,3,4,5,6,7]),
   'sixup':dict(n=6,dist=6.0,size=16,phase=-90.0,bite=True,K=6,merge=[0,0,1,2,3,4,5,6,7]),
   'five':dict(n=5,dist=4.0,size=20,phase=-54.0,K=5,merge=[0,0,1,2,3,4,5,6,7])}
out={}
for nm,g in G.items():
    for flip in (False,True):
        sp=dict(mode='fill',flip=flip,palette=B.SEA,**g)
        try: r=B.build(sp); B.check(nm,r)
        except Exception as e: print(nm,flip,'FAIL',e); continue
        out[f'{nm}_{"in" if flip else "out"}']=dict(
            name=nm,fit=r['fit'],face=r['face_fill'],
            layers=[[sorted(px),f] for px,f in r['layers'] if px])
open('.scratch-rosette/marks.json','w').write(json.dumps(out))
print('variants:',list(out))
