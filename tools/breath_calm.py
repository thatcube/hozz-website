"""
Breath, the Headspace end: the simplest possible version.

Four marks — c35..c38 — built from nothing but circles. No lattice, no petals,
no overlap counting. The argument is calm, so the geometry has to be calm, and
all the quality has to come out of *tone* and *air* rather than out of incident.

Three things in here are defences against defects this project has actually
shipped, so they are enforced rather than trusted:

1. **Protrusions.** A pixel circle taken straight off the circle equation grows
   its top row far too fast — a 28-wide disc goes 8, 12, 16 across its first
   three rows. Those first rows leave single pixels standing off the sides,
   which is the "little arms" Brandon rejected twice. `smooth()` walks the
   row-width profile and widens whatever it has to until no row differs from
   its neighbour by more than two, then rebuilds every row centred on x=16.0.
   That makes the profile step by at most 2 the whole way down *and* makes
   mirror symmetry structural rather than hoped for. It costs a slightly
   flatter cap — twelve pixels across instead of eight — and buys a clean edge.

2. **Centring.** The face's placement is never computed; it comes from the
   measured (height, top-offset-from-cy) table, and the gap is chosen as the
   one that splits the field evenly. Asserted, then printed.

3. **The face floating.** Every face pixel must land on the plain field layer.
   Not near it — on it. Asserted, so a face can never sit half on a rim.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import keyline, edge, crescent, clear, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
GRID = 32
CX = 16.0

# Hozz teal. One ramp, seven steps, roughly even in lightness, shared by all
# four so they read as one family on the board.
INK = '#04302a'   # near-black of the hue — keyline and face
DEEP = '#08574b'
MID = '#12b39a'   # the Hozz hue itself
SOFT = '#4fd0b9'
LIGHT = '#82e5d3'
PALE = '#b6f0e4'
PAPER = '#dff8f2'


# --------------------------------------------------------------------------
# shapes
# --------------------------------------------------------------------------

def raw_disc(cy, r):
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if (x + 0.5 - CX) ** 2 + (y + 0.5 - cy) ** 2 <= r * r}


def raw_squircle(cy, a, n):
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if abs((x + 0.5 - CX) / a) ** n + abs((y + 0.5 - cy) / a) ** n <= 1}


def row_widths(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: max(rows[y]) - min(rows[y]) + 1 for y in rows}


def smooth(s):
    """Rebuild every row centred on x=16.0 with |width step| <= 2 everywhere.

    Widths only grow, so the form stays convex and no area is lost. Rebuilding
    from the centre is what guarantees (31-x, y) is present for every (x, y).
    """
    w = row_widths(s)
    ys = sorted(w)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(ys)):
            a, b = ys[i - 1], ys[i]
            if w[b] - w[a] > 2:
                w[a] = w[b] - 2
                changed = True
            if w[a] - w[b] > 2:
                w[b] = w[a] - 2
                changed = True
    out = set()
    for y in ys:
        half = w[y] // 2
        out |= {(x, y) for x in range(int(CX) - half, int(CX) + half)}
    return out


def disc(d, top):
    """A smoothed pixel circle `d` across, its first row on `top`."""
    r = {28: 14.0, 26: 13.3, 24: 12.4, 22: 11.2, 20: 10.4, 18: 9.3, 16: 8.5}[d]
    s = smooth(raw_disc(16, r))
    ys = sorted({y for _, y in s})
    assert len(ys) == d and max(row_widths(s).values()) == d, f'disc {d}: got {len(ys)}x{max(row_widths(s).values())}'
    dy = top - ys[0]
    return {(x, y + dy) for x, y in s}


def squircle(d, top, n=3.0):
    s = smooth(raw_squircle(16, d / 2 + 0.1, n))
    ys = sorted({y for _, y in s})
    assert len(ys) == d, f'squircle {d}: got {len(ys)}'
    dy = top - ys[0]
    return {(x, y + dy) for x, y in s}



def ring_split(shape):
    """The shape's outermost ring, cut at its own waist into a top arc and a
    bottom arc. Two continuous arcs — `edge` and `crescent` both come out
    dotted on a profile that double-steps, and a dotted rim reads as noise."""
    r = keyline(shape)
    ys = sorted({y for _, y in r})
    waist = (ys[0] + ys[-1] + 1) / 2
    top = {p for p in r if p[1] < waist}
    return top, r - top


# --------------------------------------------------------------------------
# the face, modelled in python so containment can be asserted
# --------------------------------------------------------------------------

EYES_LG = [[(0, 3), (6, 9)], [(2, 3), (8, 9)], [(1, 2), (7, 8)],
           [(0, 1), (6, 7)], [(0, 3), (6, 9)]]
EYES_SM = [[(0, 2)], [(1, 2)], [(0, 1)], [(0, 2)]]
SMILE_LG = [[(0, 0), (9, 9)], [(0, 1), (8, 9)], [(1, 8)], [(2, 7)]]
SMILE_MD = [[(0, 0), (7, 7)], [(0, 1), (6, 7)], [(1, 6)]]
SMILE_SM = [[(0, 0), (6, 6)], [(1, 5)]]

SPEC = {'lg': (10, EYES_LG, SMILE_LG), 'md': (8, EYES_SM, SMILE_MD),
        'sm': (7, EYES_SM, SMILE_SM)}

# Measured off the face module. (height, top offset from cy) per gap. An
# even-height face is not symmetric about cy, so this is a table, not a sum.
GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
    'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
}


def face_px(cy, size, gap):
    w, eyes, smile = SPEC[size]
    if size == 'lg':
        eye_rows = eyes
    else:
        eye_rows = [[(a, b), (a + w - 3, b + w - 3)] for r in eyes for (a, b) in [r[0]]]
    rows = eye_rows + [[] for _ in range(gap)] + smile
    h, off = GEOM[size][gap]
    assert len(rows) == h, f'face model {size} gap {gap}: {len(rows)} rows, table says {h}'
    top = cy + off
    left = math.floor(16 - w / 2 + 0.5)
    out = set()
    for i, runs in enumerate(rows):
        for a, b in runs:
            out |= {(left + x, top + i) for x in range(a, b + 1)}
    return out


def place(slug, field, size, prefer=(2, 3, 1, 4)):
    """Pick the gap that splits the field evenly, then place by the table."""
    ys = sorted({y for _, y in field})
    span = ys[-1] - ys[0] + 1
    for gap in prefer:
        h, off = GEOM[size][gap]
        if (span - h) % 2:
            continue
        pad = (span - h) // 2
        cy = ys[0] + pad - off
        px = face_px(cy, size, gap)
        top = cy + off
        above, below = top - ys[0], ys[-1] - (top + h - 1)
        assert above == below, f'{slug}: air {above}/{below}'
        if not px <= field:
            continue
        return cy, gap, above, below, px
    raise AssertionError(f'{slug}: no gap sits a {size} face on a {span}-row field')


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_symmetry(slug, name, s):
    bad = [(x, y) for x, y in s if (31 - x, y) not in s]
    assert not bad, f'{slug}: {name} not mirror-symmetric at {bad[:4]}'


def profile(s):
    w = row_widths(s)
    return [w[y] for y in sorted(w)]


def check_profile(slug, s):
    p = profile(s)
    worst = max(p[i] - p[i - 1] for i in range(1, len(p)))
    assert worst <= 2, f'{slug}: row grows by {worst} — protrusion. {p}'
    return p, worst


def check_fit(slug, s):
    xs = [x for x, _ in s]
    ys = [y for _, y in s]
    assert 2 <= min(xs) and max(xs) <= 29, f'{slug}: x {min(xs)}..{max(xs)}'
    assert 2 <= min(ys) and max(ys) <= 29, f'{slug}: y {min(ys)}..{max(ys)}'
    return min(xs), min(ys), max(xs), max(ys)


def side_air(face, field):
    rows = {}
    for x, y in field:
        rows.setdefault(y, []).append(x)
    fr = {}
    for x, y in face:
        fr.setdefault(y, []).append(x)
    return min(min(min(fr[y]) - min(rows[y]), max(rows[y]) - max(fr[y])) for y in fr)


def show(layers, grid=32):
    """Overlay layers as text, later winning, so the shape can be eyeballed."""
    marks = '.:-=+*#@%$'
    print('    ' + ''.join(str(i % 10) for i in range(grid)))
    for y in range(grid):
        line = ''
        for x in range(grid):
            ch = ' '
            for i, (s, _) in enumerate(layers):
                if (x, y) in s:
                    ch = marks[i % len(marks)]
            line += ch
        if line.strip():
            print(f'{y:3} ' + line)


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def emit(slug, name, idea, doc, layers, field, size, prefer=(2, 3, 1, 4), preview=False):
    body = set().union(*[s for s, _ in layers])
    for s, fill in layers:
        check_symmetry(slug, fill, s)
    check_symmetry(slug, 'silhouette', body)
    prof, worst = check_profile(slug, body)
    x0, y0, x1, y1 = check_fit(slug, body)
    cy, gap, above, below, fpx = place(slug, field, size, prefer)
    # The face itself cannot mirror: it is two Zs, and a Z has no mirror axis.
    # What must be centred is the box it occupies.
    fx = [x for x, _ in fpx]
    assert min(fx) == 31 - max(fx), f'{slug}: face box x{min(fx)}-{max(fx)} off centre'
    assert fpx <= field, f'{slug}: face leaves the field'
    air = side_air(fpx, field)

    tones = [f for _, f in layers]
    assert len(set(tones)) == len(tones), f'{slug}: duplicate tone'
    assert len(tones) >= 5, f'{slug}: only {len(tones)} tones'
    assert layers[-1][1] == INK, f'{slug}: keyline must be the dark outer line'

    fys = sorted({y for _, y in field})
    print(f'{slug} · {name}')
    print(f'   tones {len(tones)}  bbox x{x0}-{x1} y{y0}-{y1}  '
          f'symmetry OK  max row step {worst}')
    print(f'   face {size} gap {gap} cy {cy} · field rows {fys[0]}-{fys[-1]} '
          f'({fys[-1] - fys[0] + 1}) · air {above} above / {below} below / {air} each side')
    print(f'   profile {prof}')
    if preview:
        show(layers)

    rows = '\n'.join(f'  <path d="{" ".join(to_paths(s))}" fill="{f}" />'
                     for s, f in layers)
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
  <g fill="{INK}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {cy}, size: '{size}', smile: 'wide', gap: {gap} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')
    pal = [t for t in (INK, DEEP, MID, SOFT, LIGHT, PALE, PAPER) if t in tones]
    (OUT / f'{slug}.meta.ts').write_text(f'''export default {{
  n: '{slug[1:]}', name: '{name}',
  idea: '{idea}',
  ground: 'light',
  palette: [{", ".join(f"'{c}'" for c in pal)}],
}};
''')
    return fpx


PREVIEW = '--preview' in sys.argv


# --------------------------------------------------------------------------
# c35 — one disc, as big as the safe area takes, and nothing else
# --------------------------------------------------------------------------

def c35():
    body = disc(28, 2)
    k = keyline(body)
    r1 = keyline(body - k)
    r2 = keyline(body - k - r1)
    core = body - k - r1 - r2
    lit, low = ring_split(core)
    field = clear(core, lit, low)
    layers = [(field, LIGHT), (low, SOFT), (lit, PAPER), (r2, MID), (r1, DEEP), (k, INK)]
    doc = (' * 35 \u00b7 One Breath\n *\n'
           ' * One circle, the largest the safe area allows, and nothing else in it.\n'
           ' * Hozz is one held breath \u2014 the whole argument is that your own data can\n'
           ' * sit somewhere calm and unwatched \u2014 so the mark is the calmest shape\n'
           ' * there is, and the face gets more room here than in any other mark on the\n'
           ' * board: six clear pixels above, below and to each side.\n *\n'
           ' * Six tones, every one taken off the silhouette. A dark keyline, two rings\n'
           ' * of bevel stepping in from deep teal to the hue, then a light field with a\n'
           ' * pale arc over the top of it and a soft one under the bottom \u2014 one ring\n'
           ' * cut at its waist, so the light has a direction without a shadow being\n'
           ' * painted anywhere.\n *\n'
           ' * The circle is regularised: the raw circle equation grows 8, 12, 16 across\n'
           ' * its first three rows, and rows that widen that fast leave single pixels\n'
           ' * standing off the sides. No row here differs from its neighbour by more\n'
           ' * than two, which costs a slightly flatter cap and buys a clean edge.')
    return emit('c35', 'One Breath',
                'One held breath: a single circle, and the most air any mark here gives the face.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c36 — a disc inside a disc
# --------------------------------------------------------------------------

def c36():
    outer = disc(28, 2)
    inner = disc(20, 6)
    k = keyline(outer)
    surround = clear(outer, k, inner)
    deep = crescent(outer - k, 0, -2) & surround
    lit, low = ring_split(inner)
    field = clear(inner, lit, low)
    layers = [(surround, MID), (deep, DEEP), (low, SOFT), (field, LIGHT),
              (lit, PAPER), (k, INK)]
    doc = (' * 36 \u00b7 Two Circles\n *\n'
           ' * The plainest of the breath references: two concentric circles, the inner\n'
           ' * one the field the face sits on and the outer a four-pixel surround. The\n'
           ' * breath is the inner circle; the room around it is the argument. Hozz keeps\n'
           ' * your data in a place that has space around it.\n *\n'
           ' * Six tones. The surround carries the Hozz hue so the mark still reads teal\n'
           ' * at 16px, and it darkens along its underside; the inner circle takes a pale\n'
           ' * arc over the top and a soft one beneath. Both circles are lit the same way\n'
           ' * by the same rule, so the two forms agree.')
    return emit('c36', 'Two Circles',
                'Two concentric circles: the breath, and the room it is given.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c37 — the surround offset down, so the geometry is the light
# --------------------------------------------------------------------------

def c37():
    a = disc(28, 2)
    b = disc(26, 2)
    c = disc(24, 3)
    d = disc(22, 3)
    e = disc(20, 4)
    for inner, outer in ((b, a), (c, b), (d, c), (e, d)):
        assert inner <= outer, 'nested circles must contain one another'
    k = keyline(a)
    layers = [(clear(a, k, b), DEEP), (clear(b, c), MID), (clear(c, d), SOFT),
              (clear(d, e), LIGHT), (e, PALE), (k, INK)]
    doc = (' * 37 \u00b7 Lit From Above\n *\n'
           ' * The same two circles, but every circle hangs from the same top edge\n'
           ' * instead of sitting concentrically, so the ring is one row at the top and\n'
           ' * six at the bottom. There is no shade layer anywhere in this mark. Every\n'
           ' * tone is a whole circle; the light is only where the circles sit relative\n'
           ' * to each other. A breath rising.\n *\n'
           ' * Six tones and not one of them painted. Five nested circles, each two\n'
           ' * pixels narrower than the last and each hung from the top, so the crescents\n'
           ' * they leave uncovered stack into a graded shadow underneath \u2014 pale,\n'
           ' * light, soft, mid, deep, keyline over six rows \u2014 while the top of the\n'
           ' * mark stays one row from the light.')
    return emit('c37', 'Lit From Above',
                'The surround dropped below the breath, so the geometry itself is the light.',
                doc, layers, e, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c38 — a soft-cornered square holding a circle
# --------------------------------------------------------------------------

def c38():
    outer = squircle(28, 2)
    inner = disc(20, 6)
    k = keyline(outer)
    surround = clear(outer, k, inner)
    deep = crescent(outer - k, 0, -2) & surround
    lit, low = ring_split(inner)
    field = clear(inner, lit, low)
    layers = [(surround, MID), (deep, DEEP), (low, SOFT), (field, LIGHT),
              (lit, PAPER), (k, INK)]
    doc = (' * 38 \u00b7 Held\n *\n'
           ' * A soft-cornered square with a breath inside it. The square is the thing\n'
           ' * you own \u2014 the phone, the machine under the desk, the app icon itself \u2014\n'
           ' * and the circle inside is what is being kept there. It is the only one of\n'
           ' * the four with a container, and it sits closest to the siblings, which are\n'
           ' * all square in outline.\n *\n'
           ' * Six tones, and the same lighting rule as the two-circle mark so they read\n'
           ' * as one family. The corner is a superellipse rather than a quarter circle,\n'
           ' * so the sides stay flat for longer and the corner turns in one move.')
    return emit('c38', 'Held',
                'A soft-cornered square holding one circle: the breath, and the thing that keeps it.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


if __name__ == '__main__':
    c35()
    c36()
    c37()
    c38()
    print('done')
