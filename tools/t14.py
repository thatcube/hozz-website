"""Generate t14: the shipped Twozz lighting story, told as proper glass."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import crescent, edge, keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't14'

# The shipped bubble's body, regularised to mirror exactly around x=16. Its tail
# is built separately because intentional asymmetry is what makes it a bubble.
BODY_PROFILE = [18, 22, 24, 26, 26] + [28] * 14 + [26, 26, 24, 22]
BODY = set()
for y, width in enumerate(BODY_PROFILE, 2):
    left = 16 - width // 2
    BODY |= {(x, y) for x in range(left, left + width)}

TAIL = set()
for y, right in ((25, 12), (26, 11), (27, 10), (28, 9), (29, 9)):
    TAIL |= {(x, y) for x in range(7, right + 1)}

SILHOUETTE = BODY | TAIL

# Keep the shipped physical account, but give it anatomy rather than a wash:
# four contour-following steps form the distinct top bevel, the face sits on one
# plain field, and three nested crescents form the lower-left shadow band.
KEYLINE = keyline(SILHOUETTE)
INNER = SILHOUETTE - KEYLINE

remaining = set(INNER)
TOP_BANDS = []
for _ in range(4):
    band = edge(remaining, 0, -1)
    TOP_BANDS.append(band)
    remaining -= band

SHADOW_BANDS = []
for _ in range(3):
    band = crescent(remaining, 1, -1)
    SHADOW_BANDS.append(band)
    remaining -= band

FIELD = remaining

INK = '#211532'
GLASS = [
    '#ad84ec',
    '#a777ee',
    '#a16cf0',
    '#9960f3',
    '#8f52f6',
    '#834bdc',
    '#7946cf',
    '#7243c3',
]
FACE = '#fffdf9'


def assert_no_spurs(shape):
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
    for index in range(1, len(widths) - 1):
        assert not (
            widths[index] > widths[index - 1]
            and widths[index] > widths[index + 1]
        ), f'spur at y={ys[index]}: {widths[index - 1:index + 2]}'


# Geometry proof. `check` establishes body symmetry and its no-spur profile; the
# whole silhouette gets a separate no-spur check because the tail is exempt from
# symmetry, not from clean stepping.
check(BODY)
assert_no_spurs(SILHOUETTE)
assert all((31 - x, y) in BODY for x, y in BODY)
assert any((31 - x, y) not in SILHOUETTE for x, y in TAIL)

xs = [x for x, _ in SILHOUETTE]
ys = [y for _, y in SILHOUETTE]
assert (min(xs), max(xs), min(ys), max(ys)) == (2, 29, 2, 29)

# lg is 10 wide and the 28-wide body is even. For lg/gap2 the measured module is
# eleven rows with top offset -5; cy=13 therefore lands it at y8-18.
BODY_WIDTH = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
FACE_WIDTH = 10
assert BODY_WIDTH % 2 == FACE_WIDTH % 2
FACE_TOP = 8
FACE_HEIGHT = 11
AIR_ABOVE = FACE_TOP - min(y for _, y in BODY)
AIR_BELOW = max(y for _, y in BODY) - (FACE_TOP + FACE_HEIGHT - 1)
assert (AIR_ABOVE, AIR_BELOW) == (6, 6)

LAYERS = [KEYLINE, *TOP_BANDS, FIELD, *SHADOW_BANDS]
assert all(LAYERS)
assert set().union(*LAYERS) == SILHOUETTE
for index, layer in enumerate(LAYERS):
    assert all(layer.isdisjoint(other) for other in LAYERS[index + 1:])

PALETTE = [INK, *GLASS, FACE]
assert len(set(PALETTE)) == 10

paint = [
    (KEYLINE, INK),
    *zip(TOP_BANDS, GLASS[:4]),
    (FIELD, GLASS[4]),
    (SHADOW_BANDS[2], GLASS[5]),
    (SHADOW_BANDS[1], GLASS[6]),
    (SHADOW_BANDS[0], GLASS[7]),
]
paths = '\n'.join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{colour}" />'
    for layer, colour in paint
)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * t14 · Same Light
 *
 * This does not invent a new glass object. It articulates the shipped mark's
 * existing parts: a four-step top bevel, one plain violet field, and a
 * three-step lower-left shadow band. The boundaries are structural, not a
 * diagonal wash.
 *
 * The body is the shipped silhouette regularised to exact x=16 symmetry; the
 * tail is deliberately exempt. The shipped-size lg face preserves the happy
 * wide smile: 10 pixels across on an even-width body, with six rows of body air
 * above and six below.
 *
 * Ten tones total: eight for the glass, one violet-black keyline and warm white
 * for the face.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Same Light">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: 13, size: 'lg', smile: 'wide', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: 't14', name: 'Same Light',
  idea: 'The shipped bubble’s own anatomy, rebuilt as a four-step light bevel, a plain violet field and a three-step lower-left shadow band.',
  ground: 'light',
  palette: [{', '.join(repr(colour) for colour in PALETTE)}],
}};
''')

print(
    f'{SLUG}: {len(set(PALETTE))} tones · body air {AIR_ABOVE}/{AIR_BELOW} · '
    'fit x2-29 y2-29 · parity even/even · body symmetric · tail exempt · no spurs'
)
