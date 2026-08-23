import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
from dump import dump
PETROL = ['#041f27', '#0b4450', '#157079', '#3aa39c', '#7bcfbf', '#d2f0e2']
S = []
def add(nm, **k):
    k.setdefault('cy', 16.0); k.setdefault('palette', PETROL); k.setdefault('K', 3)
    k['mode'] = 'lattice'; S.append((nm, k))
add('a d7.0 r7.5 g3 lat1,2,4,5', n=6, dist=7.0, r=7.5, ring=3, core=5.5, lat=(1, 2, 4, 5))
add('b d7.0 r7.5 r2', n=6, dist=7.0, r=7.5, ring=2, core=5.5, lat=(1, 2, 4, 5))
add('c d6.5 r8.0 r2', n=6, dist=6.5, r=8.0, ring=2, core=5.5, lat=(1, 2, 4, 5))
add('d d6.0 r8.0 r2', n=6, dist=6.0, r=8.0, ring=2, core=5.0, lat=(1, 2, 4, 5))
add('e d7.0 r7.5 r3 dk', n=6, dist=7.0, r=7.5, ring=3, core=5.5, lat=(1, 2, 3, 5))
add('f d7.0 r7.0 r2', n=6, dist=7.0, r=7.0, ring=2, core=5.5, lat=(1, 2, 4, 5))
add('g n5 d5.0 r9.0 r3', n=5, dist=5.0, r=9.0, cy=15.5, ring=3, core=5.5, lat=(1, 2, 4, 5))
add('h n5 d5.0 r9.0 r2', n=5, dist=5.0, r=9.0, cy=15.5, ring=2, core=5.5, lat=(1, 2, 4, 5))
add('i d6.5 r7.5 r3', n=6, dist=6.5, r=7.5, ring=3, core=5.0, lat=(1, 2, 4, 5))
add('j d7.0 r8.0 r3', n=6, dist=7.0, r=8.0, ring=3, core=5.5, lat=(1, 2, 4, 5))
add('k d7.0 r7.5 r3 md', n=6, dist=7.0, r=7.5, ring=3, core=5.5, lat=(1, 3, 4, 5))
add('l d6.0 r8.5 r3', n=6, dist=6.0, r=8.5, ring=3, core=5.0, lat=(1, 2, 4, 5))
dump(S, '.scratch-rosette/cands.json')
