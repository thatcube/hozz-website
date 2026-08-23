import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
from dump import dump
P = ['#041f27', '#0b4450', '#157079', '#3aa39c', '#7bcfbf', '#d2f0e2']
S = [
    ('a d7.0 r7.5 r3', dict(n=6, dist=7.0, r=7.5, ring=3, core=5.5)),
    ('c d6.5 r8.0 r2', dict(n=6, dist=6.5, r=8.0, ring=2, core=5.5)),
    ('l d6.0 r8.5 r3', dict(n=6, dist=6.0, r=8.5, ring=3, core=5.0)),
    ('i d6.5 r7.5 r3', dict(n=6, dist=6.5, r=7.5, ring=3, core=5.0)),
]
S = [(nm, dict(mode='lattice', cy=16.0, K=3, palette=P, lat=(1, 2, 4, 5), **k))
     for nm, k in S]
dump(S, '.scratch-rosette/cands.json')
