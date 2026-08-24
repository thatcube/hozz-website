import json, collections
d = json.load(open('.scratch-c39/mozz.json'))
grid=[[tuple(d[(y*32+x)*4:(y*32+x)*4+3]) for x in range(32)] for y in range(32)]
cnt = collections.Counter(p for row in grid for p in row)
def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]
tones = sorted(cnt, key=lum)
sym = {t: '.0123456789'[i] for i,t in enumerate(tones)}
for y in range(2,30):
    runs=[]; prev=None; n=0
    for x in range(32):
        c=grid[y][x]
        if c==prev: n+=1
        else:
            if prev is not None: runs.append((sym[prev],n))
            prev=c; n=1
    runs.append((sym[prev],n))
    inner=[r for r in runs if r[0]!='9' or runs.index(r) not in (0,len(runs)-1)]
    print(f'{y:3} ' + ' '.join(f'{s}x{n}' for s,n in runs if not (s=="9" and n>4)))
