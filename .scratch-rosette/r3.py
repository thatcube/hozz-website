import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
from dump import dump
SEA = ['#052a30', '#0d4c55', '#1b7a80', '#3fa8a2', '#79cdc0', '#c3ecdf']
S = []
def add(nm, **k):
    k.setdefault('cy', 16.0); k.setdefault('palette', SEA); S.append((nm, k))

add('A 6 d6.0 r8.0', mode='fill', n=6, dist=6.0, r=8.0, K=4, core=5.0, merge=[0,0,1,2,2,2,2])
add('B 6 d6.5 r7.5', mode='fill', n=6, dist=6.5, r=7.5, K=4, core=5.0, merge=[0,0,1,2,2,2,2])
add('C 8 d6.0 r8.5', mode='fill', n=8, dist=6.0, r=8.5, K=4, core=5.0, merge=[0,0,0,1,2,2,2,2,2])
add('D 8 d6.5 r8.0', mode='fill', n=8, dist=6.5, r=8.0, K=4, core=5.0, merge=[0,0,0,1,2,2,2,2,2])
add('E 5 d5.0 r9.0', mode='fill', n=5, dist=5.0, r=9.0, cy=15.5, K=4, core=5.0, merge=[0,0,1,1,2,2])
add('F 5 d5.0 r8.5', mode='fill', n=5, dist=5.0, r=8.5, cy=15.0, K=4, core=5.0, merge=[0,0,1,2,2,2])
for nm, n, d, r, rg, co in (('G lat6 r2', 6, 6.0, 8.0, 2, 5.0), ('H lat6 r3', 6, 6.5, 8.0, 3, 5.0),
                            ('I lat8 r2', 8, 6.5, 8.0, 2, 5.0), ('J lat5 r3', 5, 5.0, 9.0, 3, 5.0),
                            ('K lat6 r3b', 6, 7.0, 7.5, 3, 5.5), ('L lat6 r2b', 6, 5.5, 8.5, 2, 5.5)):
    add(nm, mode='lattice', n=n, dist=d, r=r, ring=rg, K=3, core=co,
        cy=15.5 if n == 5 else 16.0)
dump(S, '.scratch-rosette/cands.json')
