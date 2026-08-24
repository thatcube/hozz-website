import json, collections
d = json.load(open('.scratch-c39/mozz.json'))
def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]
cnt = collections.Counter(tuple(d[(y*32+x)*4:(y*32+x)*4+3]) for y in range(32) for x in range(32))
tones = sorted(cnt, key=lum)
body = tones[1:-1]
print('Mozz body ramp (9 tones), luminance and step as % of the base #b00023 (lum 56.6):')
prev=None
for t in body:
    L=lum(t); s = '' if prev is None else f'step {L-prev:+5.1f} = {100*(L-prev)/56.6:+5.1f}%'
    print(f'  #{t[0]:02x}{t[1]:02x}{t[2]:02x}  lum {L:5.1f}  {s}')
    prev=L
print(f'  span {lum(body[-1])-lum(body[0]):.1f} = {100*(lum(body[-1])-lum(body[0]))/56.6:.0f}% of base')
