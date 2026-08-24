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
        # Two rows of chin, not four. A deep crescent three rows tall reads as
        # a heavy jaw and drags the whole mark downward.
        # One row of lit at the top and one of shade at the bottom, matched.
        # Any deeper and the chin eats the light under the smile, which reads as
        # uneven even when the face is dead centre.
        lit = edge(inner, 0, -1, 1)
        deep = crescent(inner, 0, -1)
        shade = set()
        field = clear(inner, lit, deep)
    else:  # soft — one thin rim of each and nothing more
        lit = edge(inner, 0, -1, 1)
        deep = crescent(inner, 0, -1)
        shade = set()
        field = clear(inner, lit, deep)

    # Centre the face on the DISC, not on the lit field.
    #
    # This is the bug Brandon spotted. Centring on the field looks right on
    # paper, but the field is not the shape — the chin eats rows off its bottom,
    # so the field's middle sits above the disc's middle and the face rides
    # high. Mozz centres its face on the disc and lets the shading pass behind
    # it, which is why the ZZ reads as the middle of the record rather than as
    # something dropped on top of it. Same here.
    dys = sorted({p[1] for p in DISC})
    disc_mid2 = dys[0] + dys[-1] + 1          # twice the disc's centre line

    # Face widths: lg 10, md 8, sm 7. The disc is 22 across — an even width —
    # so only an even-width face can sit on x=16. `sm` is 7 wide and lands at
    # 16.5 no matter what cx you give it, which is the half-pixel lean Brandon
    # spotted. Even widths only.
    WIDTH = {'lg': 10, 'md': 8, 'sm': 7}
    disc_w = max(p[0] for p in DISC) - min(p[0] for p in DISC) + 1
    assert (disc_w - WIDTH[size]) % 2 == 0, (
        f'{slug}: a {WIDTH[size]}-wide face cannot centre on a {disc_w}-wide disc')

    GEOM = {
        'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
        'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
        'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
    }[size]

    choice = None
    for gap in (2, 3, 1, 4):
        h, off = GEOM[gap]
        # face centre line, doubled, must equal the disc's
        if (disc_mid2 - h) % 2:
            continue
        cy = (disc_mid2 - h) // 2 - off
        choice = (gap, h, cy)
        break
    assert choice, f'{slug}: no gap centres on a disc of {dys[-1] - dys[0] + 1} rows'
    gap, h, cy = choice
    top = cy + GEOM[gap][1]
    above = top - dys[0]
    below = dys[-1] - (top + h - 1)
    assert above == below, f'{slug}: air {above}/{below} on the disc'
    print(f'{slug} {name:18} disc {dys[-1] - dys[0] + 1} rows · face {size} gap {gap} '
          f'= {h} rows · air {above}/{below}')

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
 * The face is centred on the disc, not on the lit field. Centring on the field
 * rides the face high, because the chin eats rows off the field's bottom — Mozz
 * centres on the record and lets its shading pass behind the ZZ, and that is
 * what makes the face read as the middle of the thing rather than as something
 * dropped on it. Measured air on the disc: {above} above, {below} below.'''

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
build('c20', 'Ripple, Quiet', 'soft', 'md',
      'The small face, and the lightest touch of shading on the disc.',
      'One thin rim of light, one of shade.')
build('c21', 'Ripple, Small', 'above', 'md',
      'The small face with the fuller shading — the most air of the set.',
      'Two steps of shade, small face.')
print('done')
