import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
from dump import dump
SEA = ['#052a30', '#0d4c55', '#1b7a80', '#3fa8a2', '#79cdc0', '#c3ecdf']
S = []
for r in (8.0, 8.5, 9.0):
    for cy in (15.0, 15.5):
        for m in ([0, 0, 1, 2, 2, 2], [0, 0, 1, 1, 2, 2], [0, 1, 2, 2, 2, 2]):
            for core in (4.5, 5.0, 5.5, 6.0):
                for ph in (-90.0, 90.0):
                    S.append((f'5 r{r} cy{cy} m{m[1]}{m[2]}{m[3]} c{core} p{int(ph)}',
                              dict(mode='fill', n=5, dist=5.0, r=r, cy=cy, K=4,
                                   core=core, merge=m, phase=ph, palette=SEA)))
import breath_rosette as br
keep = []
for nm, sp in S:
    try:
        res = br.build(sp); br.check('x', res)
    except Exception:
        continue
    keep.append((nm, sp))
print(len(keep), 'pass')
dump(keep[:12], '.scratch-rosette/cands.json')
