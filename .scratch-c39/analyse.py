import json, collections
d = json.load(open('.scratch-c39/mozz.json'))
grid = []
for y in range(32):
    row = []
    for x in range(32):
        i = (y*32+x)*4
        r,g,b,a = d[i:i+4]
        row.append((r,g,b))
    grid.append(row)
cnt = collections.Counter(p for row in grid for p in row)
# map to symbols by luminance
tones = sorted(cnt, key=lambda c: 0.299*c[0]+0.587*c[1]+0.114*c[2])
sym = {}
alpha = '.0123456789abcdefghijklmnopqrstuvwxyz'
for i,t in enumerate(tones):
    sym[t] = alpha[i] if i < len(alpha) else '?'
print(f'{len(tones)} distinct colours in the raster')
for t in tones:
    print(f'  {sym[t]}  #{t[0]:02x}{t[1]:02x}{t[2]:02x}  lum {0.299*t[0]+0.587*t[1]+0.114*t[2]:6.1f}  count {cnt[t]}')
print()
print('     ' + ''.join(str(i%10) for i in range(32)))
for y in range(32):
    print(f'{y:3}  ' + ''.join(sym[grid[y][x]] for x in range(32)))
