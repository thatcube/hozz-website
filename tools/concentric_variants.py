"""
Generate c31-c34: four pixel studies of the Breathe animation.

The bands are filled contour steps, not alternating outlines. Broad, adjacent
tones keep the expansion readable when the 32-pixel source is shown at 24px
instead of turning into a high-contrast target or moiré pattern.
"""
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import keyline, rings, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'

# Measured from facePathsAt. An even-height face is not symmetric about cy.
FACE_GEOMETRY = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
    'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
}
FACE_WIDTH = {'lg': 10, 'md': 8, 'sm': 7}

# A circle-equation disc jumps six pixels between its first two rows at this
# scale. This measured profile keeps the round cap but limits every outward
# step to two pixels, so there can be no shoulder spur.
HALF_PROFILE = [8, 10, 12, 14, 16, 18, 20, 22, 24, 24, 26, 26, 28, 28]


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
    face_size: str = 'md'
    face_gap: int = 3


def profiled_disc():
    pixels = set()
    for y, width in enumerate(HALF_PROFILE + HALF_PROFILE[::-1], 2):
        left = 16 - width // 2
        pixels |= {(x, y) for x in range(left, left + width)}
    return pixels


def erode(body, depth):
    return rings(body, depth)[1]


def shift_y(body, amount):
    return {(x, y + amount) for x, y in body}


def concentric_layers(body, thicknesses):
    outside = keyline(body)
    current = body - outside
    bands = []
    for thickness in thicknesses:
        peeled, current = rings(current, thickness)
        bands.append(set().union(*peeled))
    return outside, bands, current


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

    width = FACE_WIDTH[size]
    left = 16 - width // 2
    face_box = {(x, y) for x in range(left, left + width)
                for y in range(top, top + height)}
    assert face_box <= field, 'face box is not fully inside its field'
    return cy, above, below, height


def assert_and_write(mark):
    assert len(mark.layers) == len(mark.palette)
    assert len(set(mark.palette)) >= 5, f'{mark.slug}: fewer than five tones'
    assert all(mark.layers), f'{mark.slug}: empty layer'
    assert sum(map(len, mark.layers)) == len(set().union(*mark.layers)), (
        f'{mark.slug}: colour layers overlap'
    )

    body = set().union(*mark.layers)
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

    ys = sorted({y for _, y in body})
    assert ys == list(range(y0, y1 + 1)), f'{mark.slug}: silhouette has a missing row'
    widths = [sum(py == y for _, py in body) for y in ys]
    for y, previous, width in zip(ys[1:], widths, widths[1:]):
        assert width <= previous + 2, (
            f'{mark.slug}: row {y} is {width}, more than 2 wider than {previous}'
        )

    full_outside = keyline(mark.outer)
    dark_keyline = mark.layers[0]
    assert dark_keyline <= full_outside and dark_keyline, (
        f'{mark.slug}: dark tone is not an outside keyline'
    )
    assert luminance(mark.palette[0]) < min(map(luminance, mark.palette[1:])), (
        f'{mark.slug}: outside keyline is not the darkest tone'
    )

    cy, above, below, face_height = face_placement(
        mark.field, mark.face_size, mark.face_gap
    )
    layer_rows = '\n'.join(
        f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'
        for pixels, fill in zip(mark.layers, mark.palette)
    )
    (OUT / f'{mark.slug}.astro').write_text(f'''---
/**
 * {mark.slug[1:]} · {mark.name}
 *
 * {mark.idea}
 *
 * {mark.ring_note} The tones are adjacent fills rather than alternating
 * outlines, and the family face breaks the centre, guarding against a target
 * reading at small sizes.
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
  <g fill="{mark.palette[0]}" shape-rendering="crispEdges">
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
        f'{face_height} rows); symmetry=PASS; protrusions=PASS; '
        f'fit=x{x0}-{x1},y{y0}-{y1} PASS; dark outside keyline=PASS; '
        f'target guard={mark.target_guard}'
    )


def build_marks():
    outer = profiled_disc()

    key31, bands31, field31 = concentric_layers(outer, [2, 2, 2])
    c31 = Mark(
        slug='c31',
        name='Even Breath',
        idea='Three broad, evenly spaced tones let one calm breath expand from Hozz’s face without the alternating contrast of a target.',
        palette=('#08574b', '#0a7061', '#0d8976', '#12b39a', '#82e5d3'),
        layers=(key31, *bands31, field31),
        field=field31,
        outer=outer,
        ring_count=3,
        ring_note='Three two-pixel bands move inward at an even pace.',
        target_guard='broad 2px bands + face',
    )

    key32, bands32, field32 = concentric_layers(outer, [1, 1, 1, 2, 2])
    c32 = Mark(
        slug='c32',
        name='Quickening Breath',
        idea='Five bands compress toward the outside, making one measured breath accelerate into places its owner controls.',
        palette=('#08574b', '#09695b', '#0a7b69', '#0b8c77', '#0d9d85', '#12b39a', '#82e5d3'),
        layers=(key32, *bands32, field32),
        field=field32,
        outer=outer,
        ring_count=5,
        ring_note='The inner bands are two pixels thick, then compress to one pixel as the breath travels outward.',
        target_guard='single-direction tone ramp + face',
    )

    shifted = (
        shift_y(erode(outer, 1), 0),
        shift_y(erode(outer, 3), 0),
        shift_y(erode(outer, 5), -1),
        shift_y(erode(outer, 6), -1),
        shift_y(erode(outer, 8), -2),
    )
    for inner, parent in zip(shifted[1:], shifted):
        assert inner <= parent, 'c33: offset layer escapes its parent'
    key33 = outer - shifted[0]
    bands33 = tuple(parent - inner for parent, inner in zip(shifted, shifted[1:]))
    field33 = shifted[-1]
    c33 = Mark(
        slug='c33',
        name='Toplit Breath',
        idea='Successive rings settle lower as they expand, leaving the lightest centre high as if breath itself were lit from above.',
        palette=('#08574b', '#0a6c5d', '#0c8270', '#0e9882', '#35c5ad', '#82e5d3'),
        layers=(key33, *bands33, field33),
        field=field33,
        outer=outer,
        ring_count=4,
        ring_note='Four nested fields step downward by two pixels from the light core to the outer silhouette, creating direction without a separate shade.',
        target_guard='offset centres + face',
    )

    full_key34, bands34, field34 = concentric_layers(outer, [1, 3, 2])
    key34 = {p for p in full_key34 if p[1] < 27}
    c34 = Mark(
        slug='c34',
        name='Warm Exhale',
        idea='Warm tones keep health human, while the broken lower ring lets breath leave rather than closing into a data target.',
        palette=('#652f2b', '#93443b', '#c35e4d', '#eb8068', '#f6ad91'),
        layers=(key34, *bands34, field34),
        field=field34,
        outer=outer,
        ring_count=3,
        ring_note='Three unequal bands sit inside a dark keyline whose lower five-pixel arc is left open.',
        target_guard='open lower keyline + face',
    )

    for mark in (c31, c32, c33, c34):
        assert_and_write(mark)
    print('done')


if __name__ == '__main__':
    build_marks()
