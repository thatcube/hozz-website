import sys, itertools
sys.path.insert(0,'tools')
import breath_rosette as B

GEOMS = {
 'c23_eight': dict(n=8,dist=6.0,size=14,phase=-67.5),
 'c25_five':  dict(n=5,dist=4.0,size=20,phase=-54.0),
 'c22_six':   dict(n=6,dist=7.0,size=14,phase=0.0,bite=True),
 'c24_six_up':dict(n=6,dist=6.0,size=16,phase=-90.0,bite=True),
}
MERGES = [
 [0,0,1,2,3,4,5,6,7],[0,0,1,2,3,4,4,4,4],[0,1,2,3,4,5,6,7,8],
 [0,0,1,1,2,3,4,5,6],[0,0,1,2,2,3,4,4,4],[0,0,0,1,2,3,4,5,6],
 [0,1,1,2,2,3,3,4,4],[0,0,1,1,2,2,3,3,4],
]
for name,g in GEOMS.items():
    found=[]
    for K in (3,4,5,6,7,8):
        for mg in MERGES:
            for flip in (False,True):
                sp=dict(mode='fill',K=K,merge=mg,flip=flip,palette=B.GLACIER,**g)
                try:
                    r=B.build(sp); B.check(name,r)
                except Exception as e:
                    continue
                f=r['fit']
                found.append((f['crossed'],f['share'],K,tuple(mg),flip,len(r['bands']),f['size']))
    found.sort(key=lambda t:(-t[0],-t[1]))
    print(f'--- {name}: {len(found)} pass')
    for t in found[:4]:
        print('   crossed=%d share=%.2f K=%d mg=%s flip=%s bands=%d face=%s'%t)
