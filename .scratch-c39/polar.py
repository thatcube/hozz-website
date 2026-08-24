import json, collections, math
d = json.load(open('.scratch-c39/mozz.json'))
grid=[[tuple(d[(y*32+x)*4:(y*32+x)*4+3]) for x in range(32)] for y in range(32)]
def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]
cnt = collections.Counter(p for row in grid for p in row)
tones = sorted(cnt, key=lum)
idx = {t:i for i,t in enumerate(tones)}
KEY, WHITE = tones[0], tones[-1]
body = [(x,y) for y in range(32) for x in range(32)
        if grid[y][x] not in (KEY, WHITE)]
print('body px:', len(body))
# angle bucket vs tone
cx, cy = 16.0, 16.0
buckets = collections.defaultdict(list)
for x,y in body:
    a = math.degrees(math.atan2((y+0.5)-cy, (x+0.5)-cx)) % 360
    r = math.hypot(x+0.5-cx, y+0.5-cy)
    buckets[int(a//15)*15].append((idx[grid[y][x]], r))
print('\nangle  mean-tone  (0=darkest .. 8=lightest of the 9 body tones, index-1)')
for a in sorted(buckets):
    v=[t-1 for t,_ in buckets[a]]
    bar = ''.join('▁▂▃▄▅▆▇█'[min(7,max(0,int(t)))] for t,_ in sorted(buckets[a], key=lambda p:p[1]))
    print(f'{a:4}  {sum(v)/len(v):5.2f}  n={len(v):3}  by radius: {bar}')
# radius vs tone
print('\nradius bucket  mean tone')
rb = collections.defaultdict(list)
for x,y in body:
    r = math.hypot(x+0.5-cx, y+0.5-cy)
    rb[int(r)].append(idx[grid[y][x]]-1)
for r in sorted(rb):
    print(f'  r {r:2}  {sum(rb[r])/len(rb[r]):5.2f}  n={len(rb[r])}')
