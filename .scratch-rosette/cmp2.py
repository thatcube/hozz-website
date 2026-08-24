import sys, json
sys.path.insert(0,'tools')
import breath_rosette as B
G={'six':dict(n=6,dist=7.0,size=14,phase=0.0,bite=True),
   'eight':dict(n=8,dist=6.0,size=14,phase=-67.5),
   'sixup':dict(n=6,dist=6.0,size=16,phase=-90.0,bite=True),
   'five':dict(n=5,dist=4.0,size=20,phase=-54.0)}
MERGES={'3a':[0,0,1,1,2,2,2,2,2],'3b':[0,0,0,1,1,2,2,2,2],'4a':[0,0,1,1,2,2,3,3,3],
        '4b':[0,0,1,2,2,3,3,3,3],'4c':[0,1,1,2,2,3,3,3,3],'5a':[0,0,1,2,3,4,4,4,4]}
out={}
for nm,g in G.items():
  for mk,mg in MERGES.items():
    for K in (4,5,6):
      for flip in (True,False):
        sp=dict(mode='fill',K=K,merge=mg,flip=flip,palette=B.SEA,**g)
        try: r=B.build(sp); B.check(nm,r)
        except Exception: continue
        nb=len(r['bands'])
        if nb<3 or nb>4: continue
        k=f'{nm}_{mk}K{K}_{"in" if flip else "out"}'
        if any(x.startswith(f'{nm}_') and x.endswith('in' if flip else 'out') for x in out): 
            pass
        out[k]=dict(name=nm,fit=r['fit'],face=r['face_fill'],nb=nb,
                    layers=[[sorted(px),f] for px,f in r['layers'] if px])
# keep at most 3 per geometry+direction
keep={}
for k,v in out.items():
    kk=(v['name'], k.endswith('in'))
    keep.setdefault(kk,[]).append((k,v))
sel={}
for kk,lst in keep.items():
    for k,v in lst[:2]: sel[k]=v
open('.scratch-rosette/marks.json','w').write(json.dumps(sel))
print(len(sel),'variants:',sorted(sel))
