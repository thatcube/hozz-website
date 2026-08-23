import math

def disc(cx, cy, r, grid=32):
    return {(x,y) for x in range(grid) for y in range(grid)
            if (x+0.5-cx)**2 + (y+0.5-cy)**2 <= r*r}

def prof(s):
    rows={}
    for x,y in s: rows.setdefault(y,[]).append(x)
    return [(y, min(rows[y]), max(rows[y]), max(rows[y])-min(rows[y])+1) for y in sorted(rows)]

def maxstep(s):
    p=prof(s); w=[r[3] for r in p]
    return max(w[i]-w[i-1] for i in range(1,len(w)))

print("radius scan, centre 16.0/16.0")
r=6.0
while r<=14.05:
    s=disc(16,16,r); p=prof(s)
    ws=[q[3] for q in p]
    x0=min(x for x,y in s); x1=max(x for x,y in s)
    y0=p[0][0]; y1=p[-1][0]
    print(f"r={r:5.2f} bbox x{x0}-{x1} y{y0}-{y1} w={x1-x0+1} h={y1-y0+1} maxstep={maxstep(s)} widths={ws}")
    r+=0.25
