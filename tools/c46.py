"""Generate c46: a compact face held by a quiet, concentric ripple."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check, circle  # noqa: E402
from shade import rings, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()
SLUG = 'c46'


def pixels(path):
    out = set()
    for x, y, width in re.findall(r'M(\d+) (\d+)h(\d+)', path):
        x, y, width = int(x), int(y), int(width)
        out |= {(x + offset, y) for offset in range(width)}
    return out


# Keep c10's pool verbatim.
paths = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)
WATER_OUT = set().union(*[pixels(d) for d, fill in paths[:26] if fill == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, fill in paths[:26] if fill != '#96bcd6'])

DISC = circle(22)
check(DISC)

# Seven one-pixel contour steps spend the compact face's extra air on a ripple.
# The small channel changes keep the steps present at 96px but blended at 24px.
DISC_TONES = [
    '#132638',
    '#7da7c1',
    '#84adc5',
    '#8bb3c9',
    '#92b9cd',
    '#99bfd1',
    '#a0c5d5',
    '#a7cbd9',
]
bands, core = rings(DISC, 7)
disc_layers = list(zip(bands, DISC_TONES[:-1])) + [(core, DISC_TONES[-1])]


def symmetric(layer):
    return all((31 - x, y) in layer for x, y in layer)


assert symmetric(WATER_OUT) and symmetric(WATER_IN), 'fixed water lost symmetry'
assert all(symmetric(layer) for layer, _ in disc_layers), 'disc tone lost symmetry'
assert set().union(*(layer for layer, _ in disc_layers)) == DISC, 'disc has an unpainted pixel'
assert sum(len(layer) for layer, _ in disc_layers) == len(DISC), 'disc tones overlap'
assert len(set(DISC_TONES)) >= 6, 'not enough disc tones'


def rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


for left, right in zip(DISC_TONES[1:], DISC_TONES[2:]):
    assert max(abs(a - b) for a, b in zip(rgb(left), rgb(right))) <= 7, (
        f'interior step {left} → {right} is too abrupt')

# faceBoxAt measures md/compact/gap2 as 8×8. On the 22-row disc it lands
# y9–16, leaving seven rows of air on both sides. md's even width also leaves
# equal horizontal air around x=16; sm is deliberately excluded.
FACE_W, FACE_H = 8, 8
DISC_TOP, DISC_BOTTOM = 2, 23
FACE_TOP = 9
above = FACE_TOP - DISC_TOP
below = DISC_BOTTOM - (FACE_TOP + FACE_H - 1)
assert (22 - FACE_W) % 2 == 0, 'face/disc parity failed'
assert above == below == 7, f'face air is {above}/{below}, not 7/7'

rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in [(WATER_OUT, '#96bcd6'), (WATER_IN, '#5d8cb0'), *disc_layers]
)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * 46 · Ripple, Close
 *
 * A compact ZZ face sits in the still centre of six barely stepped inner rings,
 * so the space freed by the smaller face reads as ripple rather than empty disc.
 *
 * faceBoxAt measures md/compact/gap2 at 8×8 (x12–19, y9–16). That leaves seven
 * rows of air above and below on the fixed y2–23 disc.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ faceBoxAt, facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
const face = {{ cx: 16, cy: 13, size: 'md', smile: 'compact', gap: 2 }} as const;
const box = faceBoxAt(face);
if (box.x !== 12 || box.right !== 19 || box.y !== 9 || box.w !== 8 || box.h !== 8 || box.bottom !== 16) {{
  throw new Error(`c46 face geometry changed: ${{JSON.stringify(box)}}`);
}}
const facePaths = facePathsAt(face);
const facePixels = new Set<string>();
for (const path of facePaths) {{
  const run = path.match(/^M(\\d+) (\\d+)h(\\d+)/);
  if (!run) throw new Error(`c46 cannot measure face path: ${{path}}`);
  const [, x, y, width] = run.map(Number);
  for (let offset = 0; offset < width; offset++) facePixels.add(`${{x + offset}},${{y}}`);
}}
if (![...facePixels].every((pixel) => {{
  const [x, y] = pixel.split(',').map(Number);
  return facePixels.has(`${{31 - x}},${{y}}`);
}})) throw new Error('c46 face lost x=16 symmetry');
---

<MarkFrame size={{size}} title="Hozz — Ripple, Close">
{rows}
  <g fill="{DISC_TONES[0]}" shape-rendering="crispEdges">
    {{facePaths.map((d) => <path d={{d}} />)}}
  </g>
</MarkFrame>
''')

palette = "', '".join([*DISC_TONES, '#96bcd6', '#5d8cb0'])
(OUT / f'{SLUG}.meta.ts').write_text(f"""export default {{
  n: '46',
  name: 'Ripple, Close',
  idea: 'A compact ZZ face sits in a still centre held by six barely stepped inner ripple rings.',
  ground: 'light',
  palette: ['{palette}'],
}};
""")

print(
    f'{SLUG}: md compact gap2 · {len(DISC_TONES)} disc tones '
    f'({len(DISC_TONES) + 2} with fixed water) · air {above}/{below} · assertions passed'
)
