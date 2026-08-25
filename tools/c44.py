"""Generate c44: Ripple with a double, tonal label around the face."""

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


WATER_OUT = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, fill in PATHS[:26] if fill != '#96bcd6'])

KEY = '#132638'
EDGE_DARK = '#b3cedf'
EDGE_LIGHT = '#bad3e2'
BORDER = '#c0d7e5'
BETWEEN = '#c8dce8'
LABEL = '#cadfe9'

DISC = circle(22)
check(DISC)
KEYLINE = keyline(DISC)
INNER = DISC - KEYLINE


def distance2(point):
    """Distance from the disc's true centre, using pixel centres."""
    x, y = point
    return (x + 0.5 - 16) ** 2 + (y + 0.5 - 13) ** 2


# Two matching low-contrast rings imply a record label around the face without
# drawing a rounded rectangle. The uninterrupted label core leaves two clear
# pixels around the md face at the four cardinal points.
EDGE_0 = {p for p in INNER if distance2(p) > 9.6 ** 2}
EDGE_1 = {p for p in INNER if 9.0 ** 2 < distance2(p) <= 9.6 ** 2}
OUTER_BORDER = {p for p in INNER if 8.0 ** 2 < distance2(p) <= 9.0 ** 2}
BETWEEN_BORDERS = {p for p in INNER if 7.0 ** 2 < distance2(p) <= 8.0 ** 2}
INNER_BORDER = {p for p in INNER if 6.0 ** 2 < distance2(p) <= 7.0 ** 2}
LABEL_FIELD = {p for p in INNER if distance2(p) <= 6.0 ** 2}

DISC_LAYERS = [
    (KEYLINE, KEY),
    (EDGE_0, EDGE_DARK),
    (EDGE_1, EDGE_LIGHT),
    (OUTER_BORDER, BORDER),
    (BETWEEN_BORDERS, BETWEEN),
    (INNER_BORDER, BORDER),
    (LABEL_FIELD, LABEL),
]


def symmetric(layer):
    return all((31 - x, y) in layer for x, y in layer)


for name, layer in [
    ('water outer', WATER_OUT),
    ('water inner', WATER_IN),
    ('disc', DISC),
    *[(fill, layer) for layer, fill in DISC_LAYERS],
]:
    assert symmetric(layer), f'c44: {name} is not symmetric about x=16'

disc_sets = [layer for layer, _ in DISC_LAYERS]
assert set().union(*disc_sets) == DISC, 'c44: tonal layers do not cover the disc'
assert sum(map(len, disc_sets)) == len(DISC), 'c44: tonal layers overlap'
assert len({fill for _, fill in DISC_LAYERS}) >= 6, 'c44: fewer than six disc tones'


def rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


tonal_walk = [EDGE_DARK, EDGE_LIGHT, BORDER, BETWEEN, BORDER, LABEL]
for a, b in zip(tonal_walk, tonal_walk[1:]):
    assert max(abs(x - y) for x, y in zip(rgb(a), rgb(b))) <= 13, (
        f'c44: tonal step {a} → {b} is too abrupt')

# md is eight pixels wide, so it can centre on the even-width disc. gap 1 makes
# an eight-row face, centred at y=13 with equal air on the disc.
FACE_SIZE = 'md'
FACE_W = 8
FACE_H = 8
FACE_GAP = 1
FACE_CY = 13
disc_x = sorted({x for x, _ in DISC})
disc_y = sorted({y for _, y in DISC})
assert (len(disc_x) - FACE_W) % 2 == 0, 'c44: face/disc parity mismatch'
face_left = 16 - FACE_W // 2
face_top = FACE_CY - FACE_H // 2
air_left = face_left - disc_x[0]
air_right = disc_x[-1] - (face_left + FACE_W - 1)
air_above = face_top - disc_y[0]
air_below = disc_y[-1] - (face_top + FACE_H - 1)
assert air_left == air_right, f'c44: horizontal air {air_left}/{air_right}'
assert air_above == air_below, f'c44: vertical air {air_above}/{air_below}'

layers = [
    (WATER_OUT, '#96bcd6'),
    (WATER_IN, '#5d8cb0'),
    *DISC_LAYERS,
]
rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / 'c44.astro').write_text(f'''---
/**
 * 44 · Ripple, Double Label
 *
 * Two quiet tonal rings surround the face like the shoulders of a record label,
 * rather than outlining a rounded rectangle. The matching border tone appears
 * twice with a lighter interval between it; the broad centre stays uninterrupted
 * behind the ZZ, so the face belongs to the disc instead of sitting on a badge.
 *
 * The disc is the canonical 22-pixel circle and the water is copied verbatim
 * from c10. Six tones live inside the disc; neighbouring interior steps differ
 * by no more than 13 RGB points. The md face is eight pixels wide and eight rows
 * tall, centred on the disc with {air_above} pixels of air above and below.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — Ripple, Double Label">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: 'wide', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / 'c44.meta.ts').write_text(f'''export default {{
  n: '44', name: 'Ripple, Double Label',
  idea: 'Two tonal label borders echo around the ZZ without turning the face into a sticker.',
  ground: 'light',
  palette: ['{KEY}', '#5d8cb0', '#96bcd6', '{EDGE_DARK}', '{EDGE_LIGHT}', '{BORDER}', '{BETWEEN}', '{LABEL}'],
}};
''')

print(
    f'c44: 6 disc tones · md/{FACE_GAP} face · '
    f'air {air_above}/{air_below} vertical, {air_left}/{air_right} horizontal · '
    'coverage, symmetry, parity, and subtle-step assertions passed'
)
