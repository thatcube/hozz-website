import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
from dump import dump
SEA  = ['#052a30', '#0d4c55', '#1b7a80', '#3fa8a2', '#79cdc0', '#c3ecdf']
S = []
def add(nm, **k):
    k.setdefault('cy', 16.0); k.setdefault('palette', SEA); S.append((nm, k))

# 6 petals, merged into flat lobes
for d, r in ((6.0, 7.5), (6.5, 7.5), (7.0, 6.5), (6.0, 8.0)):
    add(f'6 d{d} r{r} m3', mode='fill', n=6, dist=d, r=r, K=4, core=5.0,
        merge=[0, 0, 1, 2, 2, 2, 2])
# 8 petals
for d, r in ((6.0, 8.5), (6.5, 8.0), (7.0, 7.5), (6.0, 7.5)):
    add(f'8 d{d} r{r} m3', mode='fill', n=8, dist=d, r=r, K=4, core=5.0,
        merge=[0, 0, 0, 1, 2, 2, 2, 2, 2])
# 5 petals flat
for d, r in ((5.0, 8.5), (5.5, 8.0), (6.0, 7.5), (4.5, 9.0)):
    add(f'5 d{d} r{r} m2', mode='fill', n=5, dist=d, r=r, K=3, core=5.0,
        merge=[0, 0, 1, 1, 1, 1])
# lattice
for d, r in ((6.0, 8.0), (6.5, 7.5), (5.5, 8.5), (7.0, 7.0)):
    add(f'lat d{d} r{r}', mode='lattice', n=6, dist=d, r=r, ring=2, K=3, core=5.0)
dump(S, '.scratch-rosette/cands.json')
