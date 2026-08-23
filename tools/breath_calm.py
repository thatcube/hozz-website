"""
Breath, the Headspace end: the simplest possible version.

Four marks — c35..c38 — built from nothing but circles. No lattice, no petals,
no overlap counting. The argument is calm, so the geometry has to be calm, and
all the quality has to come out of *tone* and *air* rather than out of incident.

Three things in here are defences against defects this project has actually
shipped, so they are enforced rather than trusted:

1. **The circle.** Not chosen, not rasterised from a radius test. Every round
   form in here is `circles.circle(...)` — the profile of the disc from the
   shipped Mozz mark, which is known good because it is on the App Store, plus
   the smaller circles derived in the same idiom. Radius tests were what made
   the first pass of these four come out octagonal. `circles.check()` is run on
   every silhouette and on every shape derived from one; it raises on a spur (a
   row wider than both its neighbours) and on any break in mirror symmetry.

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

from circles import circle, check  # noqa: E402


def row_widths(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: max(rows[y]) - min(rows[y]) + 1 for y in rows}


# A soft-cornered square, 28 across. The corner is four pixels deep — enough to
# take the hardness off, little enough that the form still reads square. Widths
# are even so every row centres on x=16.0 and mirrors by construction.
SQUARE_28 = [20, 24, 26, 26] + [28] * 20 + [26, 26, 24, 20]


def square(top=2):
    out = set()
    for i, w in enumerate(SQUARE_28):
        out |= {(16 - w // 2 + k, top + i) for k in range(w)}
    return out


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
    """circles.check(): raises on a spur or on any break in mirror symmetry.

    It replaces the step<=2 rule this generator used to enforce. That rule was
    wrong: it forbids the 4,4,2,2 shoulder that is exactly what makes a pixel
    circle read round, and it is why the first pass of these four came out
    octagonal. The real defect is a spur — a row wider than both its
    neighbours — and that is what is checked here, on the canonical profile.
    """
    p = check(s)
    worst = max(p[i] - p[i - 1] for i in range(1, len(p)))
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
    body = circle(28, top=2)
    check(body)
    k = keyline(body)
    r1 = keyline(body - k)
    r2 = keyline(body - k - r1)
    core = body - k - r1 - r2
    check(core)
    lit, low = ring_split(core)
    field = clear(core, lit, low)
    layers = [(field, LIGHT), (low, SOFT), (lit, PAPER), (r2, MID), (r1, DEEP), (k, INK)]
    doc = (' * 35 \u00b7 One Breath\n *\n'
           ' * One circle, the largest the safe area allows, and nothing else in it.\n'
           ' * Hozz is one held breath \u2014 the whole argument is that your own data can\n'
           ' * sit somewhere calm and unwatched \u2014 so the mark is the calmest shape\n'
           ' * there is, and the face gets more room here than in any other mark on the\n'
           ' * board: six clear pixels above, below and to each side.\n *\n'
           ' * The circle is the shipped Mozz disc, taken whole rather than rasterised\n'
           ' * from a radius \u2014 the doubled rows and the four, four, two, two shoulder\n'
           ' * are what stop it reading as an octagon.\n *\n'
           ' * Six tones, every one taken off that silhouette. A dark keyline, two rings\n'
           ' * of bevel stepping in from deep teal to the hue, then a light field with a\n'
           ' * near-white arc over the top of it and a soft one under the bottom \u2014 one\n'
           ' * ring cut at its waist, so the light has a direction without a shadow being\n'
           ' * painted anywhere.')
    return emit('c35', 'One Breath',
                'One held breath: a single circle, and the most air any mark here gives the face.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c36 — a circle inside a circle
# --------------------------------------------------------------------------

def c36():
    outer = circle(28, top=2)
    inner = circle(20, top=6)
    check(outer)
    check(inner)
    assert inner <= outer, 'c36: inner circle leaves the outer'
    k = keyline(outer)
    surround = clear(outer, k, inner)
    deep = crescent(outer - k, 0, -2) & surround
    lit, low = ring_split(inner)
    field = clear(inner, lit, low)
    layers = [(surround, MID), (deep, DEEP), (low, SOFT), (field, LIGHT),
              (lit, PAPER), (k, INK)]
    doc = (' * 36 \u00b7 Two Circles\n *\n'
           ' * The plainest of the breath references: two concentric circles, the inner\n'
           ' * one the field the face sits on and the outer a four-pixel surround \u2014 the\n * widest ring on the board. The\n'
           ' * breath is the inner circle; the room around it is the argument. Hozz keeps\n'
           ' * your data in a place that has space around it.\n *\n'
           ' * Both circles are canonical \u2014 the shipped Mozz disc at 28 across and the\n'
           ' * derived one at 22 \u2014 so they are the same circle at two sizes rather than\n'
           ' * two different rasterisations, and they agree.\n *\n'
           ' * Six tones. The surround carries the Hozz hue so the mark still reads teal\n'
           ' * at 16px, and it darkens along its underside; the inner circle takes a\n'
           ' * near-white arc over the top and a soft one beneath. No keyline between the\n'
           ' * two circles: they meet tone to tone, which is what keeps this the quiet\n'
           ' * one of the four.')
    return emit('c36', 'Two Circles',
                'Two concentric circles: the breath, and the room it is given.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c37 — the circles hung from the top, so the geometry is the light
# --------------------------------------------------------------------------

def c37():
    a = circle(28, top=2)
    b = circle(24, top=3)
    c = circle(22, top=3)
    d = circle(20, top=4)
    for inner, outer in ((b, a), (c, b), (d, c)):
        check(inner)
        assert inner <= outer, 'c37: nested circles must contain one another'
    k = keyline(a)
    layers = [(clear(a, k, b), DEEP), (clear(b, c), MID), (clear(c, d), SOFT),
              (d, LIGHT), (k, INK)]
    doc = (' * 37 \u00b7 Lit From Above\n *\n'
           ' * The same circles, but each one hangs nearer the top of the last instead\n'
           ' * of sitting concentrically inside it, so the ring is one row above the\n'
           ' * breath and six below it. There is no shade layer anywhere in this mark.\n'
           ' * Every tone is a whole circle; the light is only where the circles sit\n'
           ' * relative to each other. A breath rising.\n *\n'
           ' * Five tones and not one of them painted \u2014 the fewest of the four, which\n'
           ' * is the price of the idea: four canonical circles leave four bands, and a\n'
           ' * fifth band would have to be a shade. Twenty-eight, twenty-four, twenty-two\n'
           ' * and twenty across, each hung a little higher than the one holding it, so\n'
           ' * the crescents they leave uncovered stack into a graded shadow underneath\n'
           ' * \u2014 light, soft, mid, deep, keyline over six rows \u2014 while the top of\n'
           ' * the mark stays one row from the light.')
    return emit('c37', 'Lit From Above',
                'The surround dropped below the breath, so the geometry itself is the light.',
                doc, layers, d, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


# --------------------------------------------------------------------------
# c38 — a soft-cornered square holding a circle
# --------------------------------------------------------------------------

def c38():
    outer = square(top=2)
    inner = circle(22, top=5)
    check(outer)
    check(inner)
    assert inner <= outer, 'c38: the circle leaves the square'
    k = keyline(outer)
    ring = keyline(inner)
    core = inner - ring
    check(core)
    lit, low = ring_split(core)
    field = clear(core, lit, low)
    layers = [(clear(outer, k, inner), MID), (ring, DEEP), (low, SOFT),
              (field, LIGHT), (lit, PAPER), (k, INK)]
    doc = (' * 38 \u00b7 Held\n *\n'
           ' * A soft-cornered square with a breath inside it. The square is the thing\n'
           ' * you own \u2014 the phone, the machine under the desk, the app icon itself \u2014\n'
           ' * and the circle inside is what is being kept there. It is the only one of\n'
           ' * the four with a container, and it sits closest to the siblings, which are\n'
           ' * all square in outline.\n *\n'
           ' * The corner is four pixels deep and no more, so the form reads square and\n'
           ' * not as a circle that has been squared off \u2014 twenty rows of the mark are\n'
           ' * full width and flat-sided. The circle inside is the canonical one at 22\n'
           ' * across and it carries its own dark keyline, so it reads as an object set\n'
           ' * into the square rather than a hole cut out of it. That keyline is the\n'
           ' * whole difference between this mark and the two-circle one.\n *\n'
           ' * Six tones. The square stays flat \u2014 a container should not compete \u2014\n'
           ' * and all the light is spent on the circle: near-white over the top of it,\n'
           ' * soft underneath.')
    return emit('c38', 'Held',
                'A soft-cornered square holding one circle: the breath, and the thing that keeps it.',
                doc, layers, field, 'md', prefer=(1, 3, 2, 4), preview=PREVIEW)


if __name__ == '__main__':
    c35()
    c36()
    c37()
    c38()
    print('done')
