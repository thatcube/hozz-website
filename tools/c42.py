"""Generate c42: a gradual, directional edge fade on the fixed Ripple mark."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check, circle  # noqa: E402
from shade import edge, keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    out = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        out |= {(x + i, y) for i in range(w)}
    return out


# The pool is copied pixel-for-pixel from c10.
WATER_OUT = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill != '#96bcd6'])

DISC = circle(22)
check(DISC)
KEY = keyline(DISC)
INNER = DISC - KEY

# Three close steps enter from the overhead light, and three more darken toward
# the waterline. Unlike a full inset bevel, the bands do not close into rings.
top_3 = edge(INNER, 0, -1, 3)
top_2 = edge(INNER, 0, -1, 2)
top_1 = edge(INNER, 0, -1, 1)
bottom_3 = edge(INNER, 0, 1, 3)
bottom_2 = edge(INNER, 0, 1, 2)
bottom_1 = edge(INNER, 0, 1, 1)

TOP_OUT = top_1
TOP_MID = top_2 - top_1
TOP_IN = top_3 - top_2
BOTTOM_OUT = bottom_1
BOTTOM_MID = bottom_2 - bottom_1
BOTTOM_IN = bottom_3 - bottom_2
FIELD = INNER - top_3 - bottom_3

DISC_TONES = [
    ('#eaf5fb', TOP_OUT),
    ('#e1eff7', TOP_MID),
    ('#d8e9f3', TOP_IN),
    ('#cfe3ef', FIELD),
    ('#c6ddeb', BOTTOM_IN),
    ('#bdd7e7', BOTTOM_MID),
    ('#b4d1e3', BOTTOM_OUT),
]

# Eight disc tones including the keyline, with no jump large enough to band.
assert len(DISC_TONES) + 1 == 8
assert all(layer for _, layer in DISC_TONES)
for (a, _), (b, _) in zip(DISC_TONES, DISC_TONES[1:]):
    rgb_a = tuple(int(a[i:i + 2], 16) for i in (1, 3, 5))
    rgb_b = tuple(int(b[i:i + 2], 16) for i in (1, 3, 5))
    assert max(abs(x - y) for x, y in zip(rgb_a, rgb_b)) <= 9

disc_layers = [layer for _, layer in DISC_TONES] + [KEY]
assert set().union(*disc_layers) == DISC
assert sum(map(len, disc_layers)) == len(DISC)

# The face is md (8 wide), centred at x=16 and y=13 on the 22×22 disc.
FACE_SIZE = 'md'
FACE_WIDTH = 8
FACE_GAP = 3
FACE_HEIGHT = 10
FACE_CY = 13
disc_x0, disc_x1 = min(x for x, _ in DISC), max(x for x, _ in DISC)
disc_y0, disc_y1 = min(y for _, y in DISC), max(y for _, y in DISC)
assert (disc_x1 - disc_x0 + 1 - FACE_WIDTH) % 2 == 0
face_left = 16 - FACE_WIDTH // 2
assert face_left + FACE_WIDTH / 2 == 16
face_top = FACE_CY - 5
above = face_top - disc_y0
below = disc_y1 - (face_top + FACE_HEIGHT - 1)
assert above == below == 6

layers = [
    (WATER_OUT, '#96bcd6'),
    (WATER_IN, '#5d8cb0'),
    *[(layer, fill) for fill, layer in DISC_TONES],
    (KEY, '#132638'),
]
for layer, fill in layers:
    assert all((31 - x, y) in layer for x, y in layer), f'{fill} is not x-symmetric'

# A target would use complete nested rings. Each fade band here stays on one
# side of the disc's centre line, so none can close around the field.
assert all(max(y for _, y in layer) < FACE_CY for layer in (TOP_OUT, TOP_MID, TOP_IN))
assert all(min(y for _, y in layer) >= FACE_CY for layer in (BOTTOM_OUT, BOTTOM_MID, BOTTOM_IN))

rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / 'c42.astro').write_text(f'''---
/**
 * 42 · Ripple, Slow Fade
 *
 * Three close steps ease from a pale overhead rim into the disc, while three
 * shaded steps settle it into the fixed water below.
 *
 * The light is deliberately directional rather than wrapped around all four
 * sides: a closed inset ramp became concentric rings on this circle. Measured
 * air on the disc: {above} above, {below} below.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — Ripple, Slow Fade">
{rows}
  <g fill="#132638" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: 'wide', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / 'c42.meta.ts').write_text('''export default {
  n: '42', name: 'Ripple, Slow Fade',
  idea: 'Three quiet steps from overhead light into the disc, then three shaded steps into the waterline.',
  ground: 'light',
  palette: ['#132638', '#eaf5fb', '#e1eff7', '#d8e9f3', '#cfe3ef', '#c6ddeb', '#bdd7e7', '#b4d1e3'],
};
''')

print(f'c42 · 8 disc tones · face {FACE_SIZE} gap {FACE_GAP} · air {above}/{below}')
print('assertions: fixed circle, partition, subtle steps, md parity, x symmetry, no closed rings')
