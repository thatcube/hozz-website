import sys
sys.path.insert(0,'tools')
import breath_rosette as B
sp=dict(mode='fill',n=8,dist=6.0,size=14,phase=-67.5,K=3,
        merge=[0,0,1,2,2,2,2,2,2],palette=B.GLACIER)
r=B.build(sp)
body=r['body']; bys=sorted({y for _,y in body}); span=bys[-1]-bys[0]+1
print('span',span,'btop',bys[0],'bands',{k:len(v) for k,v in r['bands'].items()})
rows=B.rows_of(body)
for size in ('lg','md','sm'):
    w=B.FACE_W[size]; lo,hi=16-w//2,16+(w-w//2)-1
    for gap in (2,3,1,4):
        h,off=B.GEOM[size][gap]
        if span<=h or (span-h)%2: print(f'{size} g{gap} h{h}: parity'); continue
        pad=(span-h)//2; top=bys[0]+pad
        miss=[(x,y) for y in range(top,top+h) for x in range(lo,hi+1) if (x,y) not in body]
        box={(x,y) for y in range(top,top+h) for x in range(lo,hi+1)}
        cr=len({b for b,px in r['bands'].items() if px & box})
        print(f'{size} g{gap} h{h} pad{pad} top{top} miss={len(miss)} crossed={cr} share={w/max(rr[-1]-rr[0]+1 for rr in rows.values()):.2f}')
