import json, sys, colorsys

def load(n):
    return json.load(open(f'{n}.json'))

for name in ('plozz', 'mozz'):
    g = load(name)
    counts = {}
    for row in g:
        for c in row:
            if c: counts[c] = counts.get(c, 0) + 1
    order = sorted(counts, key=lambda c: -counts[c])
    # map each colour to a symbol by luminance rank
    def lum(c):
        r, gg, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        return 0.2126*r + 0.7152*gg + 0.0722*b
    by_lum = sorted(counts, key=lum)
    sym = {c: '0123456789abcdefghijklmnop'[i] for i, c in enumerate(by_lum)}
    print(f'=== {name}: {len(counts)} tones ===')
    for c in by_lum:
        r, gg, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        h, l, s = colorsys.rgb_to_hls(r/255, gg/255, b/255)
        print(f'  {sym[c]}  {c}  n={counts[c]:4d}  L={lum(c):6.1f}  H={h*360:5.1f} S={s*100:5.1f} Lts={l*100:5.1f}')
    print('    ' + ''.join(str(i%10) for i in range(32)))
    for y, row in enumerate(g):
        print(f'{y:3} ' + ''.join(sym[c] if c else '.' for c in row))
    print()
