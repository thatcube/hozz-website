import sys, json
sys.path.insert(0,'tools')
import breath_rosette as B
out={}
for size,dist in [(14,7),(14,6),(16,6),(16,7),(18,7)]:
  for ph in (-90.0,90.0):
    for K in (3,4):
      for flip in (True,False):
        sp=dict(mode='fill',n=5,dist=float(dist),size=size,phase=ph,K=K,
                merge=[0,0,1,1,2,2,3,3,3],flip=flip,palette=B.MINT)
        try: r=B.build(sp); B.check('x',r)
        except Exception: continue
        k=f'5_{size}d{dist}p{int(ph)}K{K}_{"in" if flip else "out"}'
        out[k]=dict(name=k,fit=r['fit'],face=r['face_fill'],
                    layers=[[sorted(px),f] for px,f in r['layers'] if px])
open('.scratch-rosette/marks.json','w').write(json.dumps(out))
print(len(out),'variants')
