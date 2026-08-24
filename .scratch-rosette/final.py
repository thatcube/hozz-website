import sys, json
sys.path.insert(0,'tools')
import breath_rosette as B
C={
 'c22_six_scallop_in': dict(n=6,dist=7.0,size=14,phase=0.0,bite=True,K=5,
        merge=[0,0,1,2,2,3,3,3,3],flip=True,palette=B.SEA),
 'c23_eight_out':      dict(n=8,dist=6.0,size=14,phase=-67.5,K=5,
        merge=[0,0,1,1,2,2,2,2,2],flip=False,palette=B.GLACIER),
 'c25_five_in':        dict(n=5,dist=6.0,size=16,phase=-90.0,K=4,
        merge=[0,0,1,1,2,2,3,3,3],flip=True,palette=B.MINT),
 'ALT_a_sixup_out':    dict(n=6,dist=6.0,size=16,phase=-90.0,bite=True,K=5,
        merge=[0,0,1,1,2,2,2,2,2],flip=False,palette=B.LAGOON),
 'ALT_b_eight_open_out':dict(n=8,dist=7.0,size=14,phase=-67.5,K=5,
        merge=[0,0,1,1,2,2,2,2,2],flip=False,palette=B.LAGOON),
 'ALT_c_eight_open_in': dict(n=8,dist=7.0,size=14,phase=-67.5,K=5,
        merge=[0,0,1,1,2,2,3,3,3],flip=True,palette=B.LAGOON),
}
out={}
for k,sp in C.items():
    sp=dict(mode='fill',**sp)
    try: r=B.build(sp); print(B.check(k,r))
    except Exception as e: print(k,'FAIL',e); continue
    out[k]=dict(name=k,fit=r['fit'],face=r['face_fill'],
                layers=[[sorted(px),f] for px,f in r['layers'] if px])
open('.scratch-rosette/marks.json','w').write(json.dumps(out))
