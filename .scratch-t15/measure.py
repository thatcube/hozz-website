import re, sys, collections
src = open(sys.argv[1]).read()
KEY = '#241056'
pix = {}
for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-f]{6})"', src):
    for m in re.finditer(r'M(-?\d+) (-?\d+)h(\d+)', d):
        x, y, w = int(m[1]), int(m[2]), int(m[3])
        for k in range(w):
            pix[(x + k, y)] = fill
if not pix:
    print('no pixels parsed'); sys.exit(1)
rows = collections.defaultdict(list)
for (x, y), f in pix.items():
    rows[y].append((x, f))
print('row  span      w  key  int   colours')
for y in sorted(rows):
    xs = [x for x, _ in rows[y]]
    key = sum(1 for _, f in rows[y] if f == KEY)
    print(f'{y:>3}  {min(xs):>2}-{max(xs):<2}  {max(xs)-min(xs)+1:>3}  {key:>3}  {len(rows[y])-key:>3}')
ink = sorted(rows)
inner = sorted(y for y in rows if any(f != KEY for _, f in rows[y]))
print('ink rows      ', ink[0], '-', ink[-1], f'({len(ink)})')
print('non-key rows  ', inner[0], '-', inner[-1], f'({len(inner)})')
