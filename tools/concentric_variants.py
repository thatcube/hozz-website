"""Generate c31-c34: four quiet studies of the Breathe animation."""
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check, circle  # noqa: E402
from shade import keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'

# Measured from facePathsAt. An even-height face is not symmetric about cy.
FACE_GEOMETRY = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
    'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
}
FACE_WIDTH = {'lg': 10, 'md': 8, 'sm': 7}

@dataclass(frozen=True)
class Mark:
    slug: str
    name: str
    idea: str
    palette: tuple[str, ...]
    layers: tuple[set[tuple[int, int]], ...]
    field: set[tuple[int, int]]
    outer: set[tuple[int, int]]
    ring_count: int
    ring_note: str
    target_guard: str
    face_size: str = 'sm'
    face_gap: int = 2


def canonical_circle(size, top):
    shape = circle(size, top=top)
    check(shape)
    return shape


def two_rings(outer, middle, field):
    outside = keyline(outer)
    interior = outer - outside
    assert field <= middle <= interior
    return outside, interior - middle, middle - field, field


def luminance(colour):
    raw = colour.removeprefix('#')
    rgb = [int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def face_placement(field, size, gap):
    ys = sorted({y for _, y in field})
    assert ys == list(range(ys[0], ys[-1] + 1)), 'field has a missing row'
    height, offset = FACE_GEOMETRY[size][gap]
    span = ys[-1] - ys[0] + 1
    assert (span - height) % 2 == 0, f'{span}-row field cannot split {height}-row face'
    air = (span - height) // 2
    top = ys[0] + air
    cy = top - offset
    above = top - ys[0]
    below = ys[-1] - (top + height - 1)
    assert top == cy + offset
    assert above == below
    assert above >= 4, f'face has only {above}/{below} rows of air'

    width = FACE_WIDTH[size]
    left = 16 - width // 2
    face_box = {(x, y) for x in range(left, left + width)
                for y in range(top, top + height)}
    assert face_box <= field, 'face box is not fully inside its field'
    return cy, above, below, height


def assert_and_write(mark):
    assert len(mark.layers) + 1 == len(mark.palette)
    assert len(set(mark.palette)) >= 5, f'{mark.slug}: fewer than five tones'
    assert all(mark.layers), f'{mark.slug}: empty layer'
    assert sum(map(len, mark.layers)) == len(set().union(*mark.layers)), (
        f'{mark.slug}: colour layers overlap'
    )

    body = set().union(*mark.layers)
    assert body <= mark.outer, f'{mark.slug}: paint escapes the outer circle'
    assert mark.field <= body, f'{mark.slug}: field is not painted'
    check(mark.outer)
    check(mark.field)
    for layer in mark.layers:
        check(layer)
    check(body)
    x0 = min(x for x, _ in body)
    x1 = max(x for x, _ in body)
    y0 = min(y for _, y in body)
    y1 = max(y for _, y in body)
    assert 2 <= x0 <= x1 <= 29 and 2 <= y0 <= y1 <= 29, (
        f'{mark.slug}: outside safe area ({x0},{y0})-({x1},{y1})'
    )

    for index, layer in enumerate(mark.layers):
        assert all((31 - x, y) in layer for x, y in layer), (
            f'{mark.slug}: layer {index} is not mirror-symmetric about x=16'
        )

    full_outside = keyline(mark.outer)
    dark_keyline = mark.layers[0]
    assert dark_keyline <= full_outside and dark_keyline, (
        f'{mark.slug}: dark tone is not an outside keyline'
    )
    assert luminance(mark.palette[0]) < min(map(luminance, mark.palette[1:])), (
        f'{mark.slug}: outside keyline is not the darkest tone'
    )
    field_ratio = len(mark.field) / len(body)
    assert field_ratio >= 0.5, (
        f'{mark.slug}: field is only {field_ratio:.1%} of the mark'
    )

    cy, above, below, face_height = face_placement(
        mark.field, mark.face_size, mark.face_gap
    )
    layer_rows = '\n'.join(
        f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'
        for pixels, fill in zip(mark.layers, mark.palette[:-1])
    )
    (OUT / f'{mark.slug}.astro').write_text(f'''---
/**
 * {mark.slug[1:]} · {mark.name}
 *
 * {mark.idea}
 *
 * {mark.ring_note} The field is {field_ratio:.1%} of the painted area, leaving
 * the rings subordinate to the face rather than turning the mark into a bevel.
 *
 * The face uses the measured {mark.face_size}/gap{mark.face_gap} geometry:
 * field y{min(y for _, y in mark.field)}-{max(y for _, y in mark.field)},
 * {above}px air above and {below}px below.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {mark.name}">
{layer_rows}
  <g fill="{mark.palette[-1]}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {cy}, size: '{mark.face_size}', smile: 'wide', gap: {mark.face_gap} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')
    palette = ', '.join(f"'{colour}'" for colour in mark.palette)
    (OUT / f'{mark.slug}.meta.ts').write_text(f'''export default {{
  n: '{mark.slug[1:]}', name: '{mark.name}',
  idea: '{mark.idea}',
  ground: 'light',
  palette: [{palette}],
}};
''')

    print(
        f'{mark.slug} {mark.name}: rings={mark.ring_count}; tones={len(mark.palette)} PASS; '
        f'air={above}/{below} PASS (face {mark.face_size} gap{mark.face_gap}, '
        f'{face_height} rows); field={len(mark.field)}/{len(body)}={field_ratio:.1%} PASS; '
        f'symmetry=PASS; canonical circle checks=PASS; '
        f'fit=x{x0}-{x1},y{y0}-{y1} PASS; dark outside keyline=PASS; '
        f'target guard={mark.target_guard}'
    )


def build_marks():
    outer28 = canonical_circle(28, 2)
    middle24 = canonical_circle(24, 4)
    middle22 = canonical_circle(22, 5)
    field20 = canonical_circle(20, 6)

    # Answer 1: separation. A single outer ring and the field never touch; the
    # ground itself is the second concentric band.
    field31 = field20
    key31 = keyline(outer28)
    ring31 = (outer28 - middle24) - key31
    upper31 = {(x, y) for x, y in ring31 if y <= 15}
    lower31 = ring31 - upper31
    layers31 = (key31, upper31, lower31, field31)
    c31 = Mark(
        slug='c31',
        name='Open Air',
        idea='A single ring floats beyond an empty band, making the ground itself part of one breath expanding outward.',
        palette=('#08574b', '#12b39a', '#0b806e', '#82e5d3', '#096052'),
        layers=layers31,
        field=field31,
        outer=outer28,
        ring_count=1,
        ring_note='One two-tone ring is separated from the field by a fully transparent radial gap.',
        target_guard='empty gap + 64% field/paint ratio + face',
    )

    # Answer 2: motion. Top and bottom are removed from the ring altogether,
    # leaving two side arcs that read as outward-moving parentheses.
    field32 = field20
    key32_full = keyline(outer28)
    side32 = {(x, y) for x, y in outer28 if 6 <= y <= 25}
    layers32 = (
        key32_full & side32,
        ((outer28 - middle24) - key32_full) & side32,
        (middle24 - field32) & side32,
        field32,
    )
    c32 = Mark(
        slug='c32',
        name='Outward Breath',
        idea='Two open side arcs move away from a calm centre, turning concentric expansion into visible outward motion.',
        palette=('#08574b', '#0b7565', '#12b39a', '#82e5d3', '#096052'),
        layers=layers32,
        field=field32,
        outer=outer28,
        ring_count=1,
        ring_note='One ring is broken symmetrically at both top and bottom, leaving paired side arcs.',
        target_guard='two large breaks + 59% field/paint ratio + face',
    )

    # Answer 3: weight. The outer ring is deliberately sparse and dark; the
    # inner ring is broad and bright, so the expansion reads as arriving.
    field33 = middle22
    layers33 = two_rings(outer28, middle24, field33)
    c33 = Mark(
        slug='c33',
        name='Departing Breath',
        idea='A broad outer ring gives way to a thin bright inner ring, so the breath reads as leaving its centre.',
        palette=('#08574b', '#0a6759', '#24c2a8', '#a9eee2', '#096052'),
        layers=layers33,
        field=field33,
        outer=outer28,
        ring_count=2,
        ring_note='The outer ring is 92 pixels while the inner ring is 72, with the wider radial step on the outside.',
        target_guard='thick outer / thin inner weight + high tonal jump + face',
    )

    # Keep the warm point of difference, now on the canonical 24/20 pair.
    outer34 = middle24
    field34 = field20
    key34 = keyline(outer34)
    ring34 = outer34 - key34 - field34
    upper34 = {(x, y) for x, y in ring34 if y <= 15}
    lower34 = ring34 - upper34
    layers34 = (key34, upper34, lower34, field34)
    c34 = Mark(
        slug='c34',
        name='Warm Centre',
        idea='A warm, unusually wide centre keeps health human and gives the floating face the quietest breath in the set.',
        palette=('#652f2b', '#a34c40', '#e17a62', '#f6ad91', '#814038'),
        layers=layers34,
        field=field34,
        outer=outer34,
        ring_count=1,
        ring_note='One warm two-tone ring leaves a 20-row centre covering two thirds of the mark.',
        target_guard='warm contrast + 67% plain field + face',
    )

    for mark in (c31, c32, c33, c34):
        assert_and_write(mark)
    print('done')


if __name__ == '__main__':
    build_marks()
