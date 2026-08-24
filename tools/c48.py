"""Generate c48: the fixed Ripple disc as a water-worn banded stone."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check, circle  # noqa: E402
from shade import keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    out = set()
    for x, y, width in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, width = int(x), int(y), int(width)
        out |= {(x + i, y) for i in range(width)}
    return out


WATER_OUT = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill != '#96bcd6'])

DISC = circle(22)
check(DISC)
KEY = keyline(DISC)
SURFACE = DISC - KEY

# Eight close tones rise and fall through shallow, mirrored curves. The repeated
# wave is mineral stratum rather than illumination, so it has no lit direction.
TONES = [
    '#bfd7e3',
    '#c3dbe6',
    '#c7dfe9',
    '#cbe3ec',
    '#cfe7ef',
    '#d3ebf2',
    '#d7eff5',
    '#dbf3f8',
]


def tone_index(x, y):
    u2 = abs((2 * x + 1) - 32)
    curve = (u2 * u2) // 96
    phase = (y + curve - 2) % 14
    return phase if phase <= 7 else 14 - phase


tone_layers = [{p for p in SURFACE if tone_index(*p) == i} for i in range(len(TONES))]

assert all(tone_layers), 'every riverstone tone must be visible'
assert set().union(*tone_layers) == SURFACE
assert sum(map(len, tone_layers)) == len(SURFACE), 'surface tones overlap'
for layer in [KEY, *tone_layers]:
    assert all((31 - x, y) in layer for x, y in layer), 'disc layer is not x-symmetric'


def rgb(colour):
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


assert all(
    max(abs(a - b) for a, b in zip(rgb(left), rgb(right))) <= 4
    for left, right in zip(TONES, TONES[1:])
), 'palette steps are too large'
neighbours = ((1, 0), (-1, 0), (0, 1), (0, -1))
assert all(
    abs(tone_index(x, y) - tone_index(x + dx, y + dy)) <= 1
    for x, y in SURFACE
    for dx, dy in neighbours
    if (x + dx, y + dy) in SURFACE
), 'adjacent surface pixels skip a tone'

FACE_SIZE = 'lg'
FACE_WIDTH = 10
FACE_GAP = 1
FACE_HEIGHT = 10
FACE_CY = 13
disc_x0, disc_x1 = min(x for x, _ in DISC), max(x for x, _ in DISC)
disc_y0, disc_y1 = min(y for _, y in DISC), max(y for _, y in DISC)
assert (disc_x1 - disc_x0 + 1 - FACE_WIDTH) % 2 == 0, 'face parity does not match disc'
face_left = 16 - FACE_WIDTH // 2
assert face_left + FACE_WIDTH / 2 == 16, 'face is not centred on x=16'
face_top = FACE_CY - 5
above = face_top - disc_y0
below = disc_y1 - (face_top + FACE_HEIGHT - 1)
assert above == below == 6, f'unequal disc air: {above}/{below}'

layers = [
    (WATER_OUT, '#96bcd6'),
    (WATER_IN, '#5d8cb0'),
    *zip(tone_layers, TONES),
    (KEY, '#132638'),
]
rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / 'c48.astro').write_text(f'''---
/**
 * 48 · Ripple, Riverstone
 *
 * Eight close blue-grey tones form shallow, repeating mineral strata through
 * the disc. The curves continue behind the face, so the ZZ belongs to a smooth
 * river stone rather than sitting on a decorated field.
 *
 * The fixed 22-wide disc and c10 water are unchanged. Every painted layer is
 * mirrored about x=16. The 10-wide face has even parity and is centred on the
 * disc itself, with {above}px air above and {below}px below.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — Ripple, Riverstone">
{rows}
  <g fill="#132638" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: 'wide', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / 'c48.meta.ts').write_text(f'''export default {{
  n: '48', name: 'Ripple, Riverstone',
  idea: 'Quiet mineral strata curve through a water-worn stone and continue behind the face.',
  ground: 'light',
  palette: ['#132638', {", ".join(repr(tone) for tone in TONES)}, '#5d8cb0', '#96bcd6'],
}};
''')

print(
    f'c48 · {len(TONES) + 1} disc tones · face {FACE_SIZE} {FACE_WIDTH}px gap {FACE_GAP} · '
    f'air {above}/{below} · fixed circle, partition, subtle steps, parity, and layer symmetry passed'
)
