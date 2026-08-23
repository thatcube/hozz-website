import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
import breath_rosette as br
from dump import dump
P = ['#052a30', '#0d4c55', '#166f76', '#2a9494', '#5cb9b1', '#a5e0d4']
mode, n = sys.argv[1], int(sys.argv[2])
out = []
for dist in (5.5, 6.0, 6.5, 7.0, 7.5):
    for r in (6.5, 7.0, 7.5, 8.0, 8.5):
        for core in (0.0, 4.5, 5.0, 5.5):
            for K in (3, 4, 5):
                sp = dict(mode=mode, n=n, dist=dist, r=r, cy=16.0, K=K, core=core, palette=P)
                if mode == 'lattice':
                    sp['ring'] = 2
                try:
                    res = br.build(sp); br.check('x', res)
                except Exception:
                    continue
                w = max(x for x, y in res['body']) - min(x for x, y in res['body']) + 1
                if w < 24 or len(res['layers']) < 5:
                    continue
                out.append((f'{mode[:3]}{n} d{dist} r{r} c{core} K{K}', sp))
print(len(out), 'pass')
seen, pick = set(), []
for name, sp in out:
    k = (sp['dist'], sp['r'])
    if k in seen: continue
    seen.add(k); pick.append((name, sp))
dump(pick[:16], '.scratch-rosette/cands.json')
