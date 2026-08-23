"""
Ripple variants: c10's size and its water, a clean disc, and different light.

Brandon's read on c10 was that the shape is the good part but the outline has
stray pixels poking out at the sides — arms. So the disc here is a true circle
of the same rough size, generated from the circle equation so columns x and
31-x mirror by construction and no row is wider than both its neighbours.

The centring is fixed with the face's `gap`, not by moving anything. The field
is an even number of rows and the faces are odd — seven or nine — so at the
default gap of two an even split is arithmetically impossible. Opening the gap
by one makes the face even and the air then divides exactly.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import rings, keyline, crescent, edge, clear, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()

# c10 paints its two rings of water before the disc; splitting there keeps the
# water exactly as drawn.
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


WATER_OUT = set().union(*[pixels(d) for d, f in PATHS[:26] if f == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, f in PATHS[:26] if f != '#96bcd6'])

KEY, DEEP, SHADE, FIELD, LIT = '#132638', '#3f6f92', '#5d8cb0', '#cfe3ef', '#eaf5fb'


def disc(cy, r):
    return {(x, y) for x in range(32) for y in range(32)
            if (x + 0.5 - 16) ** 2 + (y + 0.5 - cy) ** 2 <= r * r}


def check_round(shape):
    """Reject a raster circle with spurs or flat corners.

    Rendered side by side, r=11.5 comes out visibly octagonal and some centres
    grow single pixels standing off the left and right — the arms Brandon
    rejected on c10. r=11.0 at cy=13 is clean, and this keeps it honest.
    """
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ws = [max(v) - min(v) + 1 for _, v in sorted(rows.items())]
    for i in range(1, len(ws) - 1):
        if ws[i] > ws[i - 1] and ws[i] > ws[i + 1]:
            raise SystemExit(f'spur at row {sorted(rows)[i]}: width {ws[i]}')
    assert ws == ws[::-1], 'circle is not symmetric top to bottom'
    return ws


DISC = disc(13, 11.0)  # 22x22 — chosen by rendering candidates and looking
check_round(DISC)


def build(slug, name, mode, size, idea, note):
    k = keyline(DISC)
    inner = DISC - k

    if mode == 'even':
        rgs, core = rings(inner, 2)
        lit, shade, deep, field = rgs[0], rgs[1], set(), core
    elif mode == 'above':
        lit = edge(inner, 0, -1, 1)
        deep = crescent(inner, 0, -1)
        shade = crescent(inner, 0, -3) - deep
        field = clear(inner, lit, shade, deep)
    else:  # soft — one thin rim of each and nothing more
        lit = edge(inner, 0, -1, 1)
        deep = crescent(inner, 0, -1)
        shade = set()
        field = clear(inner, lit, deep)

    fys = sorted({p[1] for p in field})
    span = fys[-1] - fys[0] + 1

    # Measured from the face module rather than assumed: an even-height face is
    # not symmetric about cy, so computing the placement arithmetically put it a
    # row out every time. (height, top offset from cy) for each gap.
    GEOM = {
        'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
        'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
        'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
    }[size]

    # Choose the gap whose height splits the field evenly, then place the face
    # by its measured top edge.
    choice = None
    for gap in (2, 3, 1, 4):
        h, off = GEOM[gap]
        if (span - h) % 2:
            continue
        pad = (span - h) // 2
        choice = (gap, h, fys[0] + pad - off)
        break
    assert choice, f'{slug}: no gap splits a {span}-row field evenly'
    gap, h, cy = choice
    above = (cy + GEOM[gap][1]) - fys[0]
    below = fys[-1] - (cy + GEOM[gap][1] + h - 1)
    assert above == below, f'{slug}: air {above}/{below}'
    print(f'{slug} {name:18} field {span} · face {size} gap {gap} = {h} rows '
          f'· air {above}/{below}')

    layers = [(WATER_OUT, '#96bcd6'), (WATER_IN, '#5d8cb0'), (field, FIELD)]
    if shade:
        layers.append((shade, SHADE))
    if deep:
        layers.append((deep, DEEP))
    layers += [(lit, LIT), (k, KEY)]

    for px, fill in layers:
        if fill in (FIELD, SHADE, DEEP, LIT, KEY):
            assert all((31 - x, y) in px for x, y in px), f'{slug}: {fill} not symmetric'

    rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in layers)
    doc = f''' * {slug[1:]} · {name}
 *
 * {idea}
 *
 * c10's size and its water, but a true circle: c10's outline has single pixels
 * standing off the sides, which read as little arms. {note}
 *
 * Centred by opening the face's gap to {gap} rather than by nudging it — the
 * field is {span} rows and the faces are odd, so at the default gap an even
 * split cannot happen. Measured air: {above} above, {below} below.'''

    (OUT / f'{slug}.astro').write_text(f'''---
/**
{doc}
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {name}">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {cy}, size: '{size}', smile: 'wide', gap: {gap} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')
    (OUT / f'{slug}.meta.ts').write_text(f'''export default {{
  n: '{slug[1:]}', name: '{name}',
  idea: '{idea}',
  ground: 'light',
  palette: ['{KEY}', '{SHADE}', '{FIELD}', '{LIT}', '#96bcd6'],
}};
''')


build('c18', 'Ripple, Centred', 'above', 'md',
      'The shape that worked, lit from straight above so nothing pulls the face to one side.',
      'Two steps of shade fall from the top.')
build('c19', 'Ripple, Even', 'even', 'md',
      'Lit from no direction at all — one rim right the way round, so the field is uniform.',
      'The shading is concentric.')
build('c20', 'Ripple, Quiet', 'soft', 'sm',
      'The small face, and the lightest touch of shading on the disc.',
      'One thin rim of light, one of shade.')
build('c21', 'Ripple, Small', 'above', 'sm',
      'The small face with the fuller shading — the most air of the set.',
      'Two steps of shade, small face.')
print('done')
