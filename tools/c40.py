"""Generate c40: Ripple's disc catching a reflection from the water below."""
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
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        out |= {(x + i, y) for i in range(w)}
    return out


# Lifted pixel-for-pixel from c10: the pool is not part of this variation.
WATER_OUT = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill != '#96bcd6'])

DISC = circle(22)
check(DISC)

KEY = '#132638'
TONES = [
    '#abcbdc',
    '#b2d0df',
    '#b9d5e2',
    '#c0dae5',
    '#c7dfe8',
    '#cee4eb',
    '#d5e9ee',
    '#dcedf1',
]


def tone_index(x, y):
    """A mirrored specular wake rising from the disc's point of contact.

    The ridge is a V whose arms rise one pixel for each pixel travelled away
    from centre. A dark lead-in and bright trailing edge make it read as sheen,
    while the long light tail is the cool reflection of the water below.
    """
    u2 = abs((2 * x + 1) - 32)
    ridge2 = 38 - u2
    distance2 = 2 * y - ridge2
    if distance2 <= -12:
        return 3
    if distance2 <= -10:
        return 2
    if distance2 <= -8:
        return 1
    if distance2 <= -6:
        return 0
    if distance2 <= -4:
        return 1
    if distance2 <= -2:
        return 2
    if distance2 <= 0:
        return 3
    if distance2 <= 2:
        return 4
    if distance2 <= 4:
        return 5
    if distance2 <= 6:
        return 6
    if distance2 <= 8:
        return 7
    if distance2 <= 10:
        return 6
    if distance2 <= 12:
        return 5
    return 4


outline = keyline(DISC)
surface = DISC - outline
tone_layers = [{p for p in surface if tone_index(*p) == i} for i in range(len(TONES))]

# The surface is a partition, and all eight close steps are genuinely present.
assert all(tone_layers)
assert set().union(*tone_layers) == surface
assert sum(map(len, tone_layers)) == len(surface)
assert all(
    max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5)) <= 7
    for a, b in zip(TONES, TONES[1:])
), 'neighbouring surface tones jump too far'

# This reflection is deliberately bilateral: its light changes with distance
# from centre, but never moves the silhouette or its visual weight to one side.
for layer in [outline, *tone_layers]:
    assert all((31 - x, y) in layer for x, y in layer), 'disc layer is not symmetric'

# An 8-wide face can centre on the 22-wide disc. With gap 1 it is 8 rows high,
# leaving seven rows of the disc above and below it.
FACE_SIZE = 'md'
FACE_GAP = 1
FACE_CY = 13
FACE_WIDTH = 8
FACE_HEIGHT = 8
disc_xs = [x for x, _ in DISC]
disc_ys = [y for _, y in DISC]
disc_width = max(disc_xs) - min(disc_xs) + 1
face_top = FACE_CY - 4
air_above = face_top - min(disc_ys)
air_below = max(disc_ys) - (face_top + FACE_HEIGHT - 1)
assert (disc_width - FACE_WIDTH) % 2 == 0, 'face parity does not match disc'
assert air_above == air_below == 7, f'unequal disc air: {air_above}/{air_below}'

layers = [
    (WATER_OUT, '#96bcd6'),
    (WATER_IN, '#5d8cb0'),
    *zip(tone_layers, TONES),
    (outline, KEY),
]
rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / 'c40.astro').write_text(f'''---
/**
 * 40 · Ripple, Waterlight
 *
 * Mozz's shipped sheen is not a gradient: its close red tones gather into
 * opposing diagonal reflections and pass behind the white face. This keeps
 * that integration but changes the source of light. A mirrored specular wake
 * rises from the point where Ripple meets its pool, with a dark leading edge,
 * a pale glint and a long cool tail. Eight surface tones differ by no more
 * than seven RGB points per step, so the wake blends into the disc.
 *
 * The fixed 22-wide disc and c10 water are unchanged. The 8-wide face has even
 * parity with the disc and is centred on the disc itself: 7 rows of air above,
 * 7 below. Every disc layer, including the reflection, mirrors about x=16.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — Ripple, Waterlight">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: 'wide', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / 'c40.meta.ts').write_text(f'''export default {{
  n: '40', name: 'Ripple, Waterlight',
  idea: 'The pool throws a quiet mirrored sheen back up through the disc, passing behind the face.',
  ground: 'light',
  palette: ['{KEY}', {", ".join(repr(tone) for tone in TONES)}, '#5d8cb0', '#96bcd6'],
}};
''')

print(
    f'c40: {len(TONES) + 1} disc tones · md face {FACE_WIDTH} wide · '
    f'air {air_above}/{air_below} · silhouette, layers, parity, and tone steps passed'
)
