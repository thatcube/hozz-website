import sys
sys.path.insert(0,'tools')
import breath_rosette as B
ok=[]
for size in (12,14,16,18,20):
  for dist in range(3,size//2+1):
    for ph in (-90.0,-54.0,90.0,-18.0):
      for K in (3,4,5,6):
        for mg in ([0,0,1,1,2,2,2,2,2],[0,0,1,2,2,3,3,3,3],[0,0,1,1,2,2,3,3,3]):
          for flip in (True,False):
            for bite in (False,True):
              sp=dict(mode='fill',n=5,dist=float(dist),size=size,phase=ph,K=K,
                      merge=mg,flip=flip,bite=bite,palette=B.MINT)
              try: r=B.build(sp); B.check('x',r)
              except Exception: continue
              b=r['body']; xs=[p[0] for p in b]; ys=[p[1] for p in b]
              w,h=max(xs)-min(xs)+1,max(ys)-min(ys)+1
              if w<24 or h<24: continue
              ok.append((dist/size,size,dist,ph,K,flip,bite,w,h,r['fit']['share']))
ok.sort(key=lambda t:-t[0])
print(len(ok),'pass; best ratios:')
seen=set()
for t in ok:
    k=(t[1],t[2],t[3])
    if k in seen: continue
    seen.add(k)
    print('  ratio=%.2f sz=%d d=%d ph=%.0f K=%d flip=%s bite=%s %dx%d share=%.2f'%t)
