"""Draft the four marks, print ASCII + checks, and render a preview sheet."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import breath_rosette as br  # noqa: E402

SEA = ['#052a30', '#0d4c55', '#166f76', '#2a9494', '#5cb9b1', '#a5e0d4']
PALE = ['#07272c', '#12525a', '#1d7a7c', '#38a09a', '#71c4ba', '#bce8dc']
LAT = ['#04222a', '#0e4a55', '#1a7581', '#31a5a3', '#c2ebe0']
FLAT = ['#062b31', '#155f66', '#2b8f8c', '#68c2b6', '#c8ece1']

SPECS = {
    'c22': dict(mode='fill', n=6, dist=5.0, r=9.5, cy=16.0, K=5, palette=SEA),
    'c23': dict(mode='fill', n=8, dist=6.0, r=8.5, cy=16.0, K=5, palette=PALE),
    'c24': dict(mode='lattice', n=6, dist=5.5, r=7.0, cy=16.0, ring=2, K=4,
                core=3.0, palette=LAT),
    'c25': dict(mode='fill', n=5, dist=3.0, r=8.0, cy=14.0, K=4, palette=FLAT),
}

svgs = {}
for slug, spec in SPECS.items():
    r = br.build(spec)
    print(f'--- {slug} ---')
    print(br.ascii_art(r))
    try:
        print(br.check(slug, r))
    except AssertionError as e:
        print('FAIL', e)
    svgs[slug] = br.svg_body(r)
    if r['fit']:
        f = r['fit']
        svgs[slug] += f"\n<!--face cy={f['cy']} size={f['size']} gap={f['gap']}-->"

Path(ROOT / '.scratch-rosette/svgs.py').write_text('SVG = ' + repr(svgs) + '\n')
