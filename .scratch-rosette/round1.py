import sys
sys.path.insert(0, '.scratch-rosette')
from dump import dump

SEA  = ['#052a30', '#0d4c55', '#166f76', '#2a9494', '#5cb9b1', '#a5e0d4']
PALE = ['#07272c', '#12525a', '#1d7a7c', '#38a09a', '#71c4ba', '#bce8dc']
LAT  = ['#04222a', '#0e4a55', '#1a7581', '#31a5a3', '#c2ebe0']
FLAT = ['#062b31', '#155f66', '#2b8f8c', '#68c2b6', '#c8ece1']

specs = [
    ('c22 6/5.0/9.5 K5', dict(mode='fill', n=6, dist=5.0, r=9.5, cy=16.0, K=5, palette=SEA)),
    ('c22b 6/5.5/9.0 K4', dict(mode='fill', n=6, dist=5.5, r=9.0, cy=16.0, K=4, palette=SEA)),
    ('c23 8/6.0/8.5 K5', dict(mode='fill', n=8, dist=6.0, r=8.5, cy=16.0, K=5, palette=PALE)),
    ('c23b 8/5.5/9.0 K5', dict(mode='fill', n=8, dist=5.5, r=9.0, cy=16.0, K=5, palette=PALE)),
    ('c24 lat 6/5.5/7.0 r2', dict(mode='lattice', n=6, dist=5.5, r=7.0, cy=16.0, ring=2, K=4, core=5.0, palette=LAT)),
    ('c24b lat 6/6.0/8.0 r2', dict(mode='lattice', n=6, dist=6.0, r=8.0, cy=16.0, ring=2, K=3, core=5.0, palette=LAT)),
    ('c25 5/4.5/9.0 K5', dict(mode='fill', n=5, dist=4.5, r=9.0, cy=16.0, K=5, core=5.0, palette=FLAT)),
    ('c25b 5/5.0/8.5 K4', dict(mode='fill', n=5, dist=5.0, r=8.5, cy=15.5, K=4, core=5.0, palette=FLAT)),
]
dump(specs, '.scratch-rosette/cands.json')
