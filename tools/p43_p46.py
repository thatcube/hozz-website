"""
p43–p46 · Plozz as a light-box, not a television set.

p21–p25 all draw the same object — case, screen, stand — and differ only in
proportion. A stand is the one part of a television that says *furniture*
rather than *picture*, and a play triangle says *button* rather than *light*.
So this set drops both and keeps the only thing Plozz is actually about:
something luminous you look into.

Four objects, one argument, separated by **what the light is doing** — the axis
the shipped family already varies along (Plozz recessed, Mozz rotational, c45
concentric):

  p43  Aperture   a tunnel. Contour-following rings brighten inward, so the
                  eye reads depth going away from it toward a lit field.
  p44  Throw      the same bevel, lit. Each ring's tone is pushed by the angle
                  to an off-frame source at upper-left, so one wall is bright
                  and the opposite one is deep. Level lines still follow the
                  contour; only their value is directional.
  p45  Reflector  glass. Case, bezel, then a front surface carrying two
                  specular streaks struck at 45° and a rim vignette. The
                  streaks are asymmetric because a reflection is, and they live
                  in the band, never over the face.
  p46  Well       steps. Three concentric plates, each with a shaded upper
                  wall and a lit lower one, receding to the light. Discrete
                  risers rather than a smooth ramp.

All four keep the family's rule, measured off Plozz, Mozz and c45: the centre
stays plain and the whole tone spend goes into the band, because the face is 8
wide on a 26–28 wide container and anything crossing the middle crosses the
face.

The face is identical in all four and is never drawn here — `facePathsAt` with
`size: 'md'`, `smile: 'compact'`, `gap: 2`, which is exactly 8×8.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import rings, keyline, to_paths, is_slab, edge, bbox  # noqa: E402
from face_py import face_box, face_paths                         # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
GRID = 32
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# ---------------------------------------------------------------------------
# The family cyan. One ramp, twelve steps, shared by all four so the set reads
# as one object under four lights rather than four unrelated objects. Hue runs
# 200° → 194° as it lightens, which is what a real cyan does on the way to
# white; nothing here is a tint of a single swatch.
# ---------------------------------------------------------------------------
INK = '#04202f'          # keyline and face — a near-black *of the hue*
RAMP = [
    '#063245',
    '#07445f',
    '#08587a',
    '#096b94',
    '#0a7fb0',
    '#0d93c6',
    '#22a7d6',
    '#45bbe3',
    '#68ccec',
    '#8dddf3',
    '#b2eaf8',
    '#d5f4fc',
]

FACE = INK
FACE_SIZE, FACE_SMILE, FACE_GAP = 'md', 'compact', 2
FB = face_box(cx=16, cy=16, size=FACE_SIZE, smile=FACE_SMILE, gap=FACE_GAP)


# ---------------------------------------------------------------------------
# Silhouettes
# ---------------------------------------------------------------------------

CORNER = {
    0: [], 1: [1], 2: [2, 1], 3: [3, 1, 1], 4: [4, 2, 1, 1],
    5: [5, 3, 2, 1, 1], 6: [6, 4, 2, 1, 1, 1], 7: [7, 5, 3, 2, 1, 1, 1],
}


def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle with a hand-stepped corner.

    A radius test rasterises badly at these sizes — it grows single pixels
    standing off the sides. These profiles step 4, 2, 1, 1 in the same idiom as
    the canonical circles, so no row is ever wider than both its neighbours.
    """
    out = set()
    h = y1 - y0 + 1
    for i, y in enumerate(range(y0, y1 + 1)):
        d = min(i, h - 1 - i)
        inset = CORNER[r][d] if d < len(CORNER[r]) else 0
        out |= {(x, y) for x in range(x0 + inset, x1 - inset + 1)}
    return out


def depths(solid):
    """Ring depth of every pixel: 0 on the outermost band, rising inward."""
    out = {}
    cur = set(solid)
    d = 0
    while cur:
        band = {p for p in cur
                if any((p[0] + dx, p[1] + dy) not in cur for dx, dy in N4)}
        for p in band:
            out[p] = d
        cur -= band
        d += 1
    return out


WINDOW = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if (dx, dy) != (0, 0)]


def facing(solid, p):
    """How much a bit of wall faces a source at the upper left, -1 … +1.

    The outward normal is taken as the mean direction to every cell within two
    pixels that is *not* part of the solid, rather than from a one-pixel
    gradient. A one-pixel gradient is ambiguous exactly at the corners, which
    is where it put a stray highlight in the first cut of this; averaging over
    a window turns smoothly all the way round instead.

    This is the difference between a lit bevel and a diagonal wash: a wash cuts
    a straight crease across the corners, a normal turns with the contour and
    cannot.
    """
    x, y = p
    nx = ny = 0.0
    for dx, dy in WINDOW:
        if (x + dx, y + dy) not in solid:
            d = (dx * dx + dy * dy) ** 0.5
            nx += dx / d
            ny += dy / d
    n = (nx * nx + ny * ny) ** 0.5
    if n < 1e-9:
        return 0.0
    return -((nx / n) + (ny / n)) * 0.7071


def wall(solid, plate, dx, dy, depth):
    """The band of `plate` on the side of `solid` facing (dx, dy).

    Taken against the whole `solid`, not against the ring, because a ring has
    two top edges — its own and the one facing the hole in the middle — and
    shading both is what makes a bevel read as a picture frame lying flat.
    """
    return edge(solid, dx, dy, depth) & plate


def flat_depth(solid, pad=1):
    """The smallest ring depth that still clears the face box by `pad`.

    Everything at or beyond it is painted one tone, so the field the ZZ sits on
    is calm no matter how many steps the band is spending.
    """
    box = [(x, y)
           for x in range(FB['x'] - pad, FB['x'] + FB['w'] + pad)
           for y in range(FB['y'] - pad, FB['y'] + FB['h'] + pad)]
    d = depths(solid)
    return min(d[p] for p in box if p in d)


# ---------------------------------------------------------------------------
# p43 · Aperture — a tunnel that brightens inward
# ---------------------------------------------------------------------------

def p43():
    body = rrect(2, 3, 29, 28, 4)              # 28 × 26
    key = keyline(body)
    _, inner = rings(body, 1)

    d = depths(inner)
    cap = flat_depth(inner)                    # 7
    tones = [RAMP[0], RAMP[1], RAMP[2], RAMP[4], RAMP[6], RAMP[8], RAMP[9]]
    field = RAMP[11]

    layers = [(t, set()) for t in tones] + [(field, set())]
    for p, dd in d.items():
        layers[min(dd, cap)][1].add(p)

    return dict(name='Aperture', body=body, key=key, layers=layers,
                field=len(layers) - 1, face=(16, 16))


# ---------------------------------------------------------------------------
# p44 · Throw — the same bevel, lit from off-frame upper-left
# ---------------------------------------------------------------------------

def p44():
    body = rrect(3, 6, 28, 25, 4)              # 26 × 20
    key = keyline(body)
    _, inner = rings(body, 1)

    d = depths(inner)
    cap = flat_depth(inner)

    buckets = {}
    field = set()
    for p, dd in d.items():
        if dd >= cap:
            field.add(p)
            continue
        push = max(-1, min(1, round(facing(inner, p) * 1.5)))
        idx = max(0, min(11, dd * 2 + push))
        buckets.setdefault(idx, set()).add(p)

    layers = [(RAMP[i], buckets[i]) for i in sorted(buckets)]
    layers.append((RAMP[11], field))

    return dict(name='Throw', body=body, key=key, layers=layers,
                field=len(layers) - 1, face=(16, 16))


# ---------------------------------------------------------------------------
# p45 · Reflector — case, bezel, glass, two speculars
# ---------------------------------------------------------------------------

def p45():
    body = rrect(2, 5, 29, 26, 4)              # 28 × 22
    key = keyline(body)
    rs, glass = rings(body, 3)                 # keyline + a two-pixel case
    case = rs[1] | rs[2]
    _, solid = rings(body, 1)

    # Shipped Plozz's case treatment, taken as full bands rather than as
    # hairlines: a one-pixel light line under a one-pixel keyline reads as a
    # second outline, which is what made the first cut of this wobble.
    case_lit = wall(solid, case, 0, -1, 2)
    case_dark = wall(solid, case, 0, 1, 2) - case_lit
    case_mid = case - case_lit - case_dark

    gd = depths(glass)
    cap = flat_depth(glass)
    g = [set() for _ in range(cap + 1)]
    for p, dd in gd.items():
        g[min(dd, cap)].add(p)

    # Two specular streaks at 45°, asymmetric because a reflection is, kept
    # entirely inside the left band and clear of the face box by a pixel.
    def streak(x, y, n, w):
        return {(x + i + k, y - i) for i in range(n) for k in range(w)} & glass

    long_s = streak(6, 20, 5, 2)
    short_s = streak(6, 13, 2, 2)
    guard = {(x, y)
             for x in range(FB['x'] - 1, FB['x'] + FB['w'] + 1)
             for y in range(FB['y'] - 1, FB['y'] + FB['h'] + 1)}
    long_s -= guard
    short_s -= guard
    for s_ in g:
        s_ -= long_s | short_s

    tones = [RAMP[2], RAMP[6], RAMP[9], RAMP[11]]
    layers = [
        (RAMP[1], case_dark),
        (RAMP[3], case_mid),
        (RAMP[6], case_lit),
    ] + [(tones[i], g[i]) for i in range(len(g))] + [
        (RAMP[10], short_s),
        ('#eafaff', long_s),
    ]
    return dict(name='Reflector', body=body, key=key, layers=layers,
                field=2 + len(g), face=(16, 16))


# ---------------------------------------------------------------------------
# p46 · Well — three plates, each with a riser
# ---------------------------------------------------------------------------

def p46():
    body = rrect(3, 3, 28, 28, 6)              # 26 × 26
    key = keyline(body)
    rs, core = rings(body, 7)                  # keyline + 3 plates × 2

    solids = []
    cur = set(body)
    for r in rs:
        cur = cur - r
        solids.append(set(cur))

    plates = [rs[1] | rs[2], rs[3] | rs[4], rs[5] | rs[6]]
    tops = [solids[0], solids[2], solids[4]]

    # Recessed, so the upper wall is in shadow and the lower one catches the
    # light — the reverse of a raised boss, and the reason this reads as a
    # hollow rather than a stack of lids.
    steps = [(1, 3, 6), (2, 5, 8), (4, 7, 10)]
    layers = []
    for plate, solid, tri in zip(plates, tops, steps):
        buckets = {-1: set(), 0: set(), 1: set()}
        for q in plate:
            # Inverted, because this is a hollow: in a recess the upper wall is
            # the one in shadow and the lower one catches the light. Squaring
            # off the walls by row instead would leave teeth at the corners.
            buckets[max(-1, min(1, round(-facing(solid, q) * 1.5)))].add(q)
        layers += [(RAMP[tri[0]], buckets[-1]),
                   (RAMP[tri[1]], buckets[0]),
                   (RAMP[tri[2]], buckets[1])]
    layers.append((RAMP[11], core))

    return dict(name='Well', body=body, key=key, layers=layers,
                field=len(layers) - 1, face=(16, 16))


BUILDERS = {'p43': p43, 'p44': p44, 'p45': p45, 'p46': p46}

DOCS = {
    'p43': ('Aperture',
            'A tunnel rather than a set. Eight contour-following rings step from a deep\n'
            ' * housing to a lit field, so the eye reads depth going away from it and the\n'
            ' * ZZ sits at the bottom of the light rather than on the front of a box.\n'
            ' *\n'
            ' * No stand, no controls, no triangle. The ring band bends around every corner\n'
            ' * of the silhouette because each ring is defined by which pixels have a\n'
            ' * missing neighbour, so nothing here is a rectangle dropped inside an\n'
            ' * outline. The band stops one pixel clear of the face and the rest is one\n'
            ' * flat tone: the family rule, measured off Plozz, Mozz and c45 — the centre\n'
            ' * stays plain and the whole tone spend goes into the band.',
            'A light-box rather than a television: eight rings step from a deep housing to a lit field, so the ZZ reads as sitting at the bottom of the light instead of on the front of a case. No stand, no controls, no play triangle.'),
    'p44': ('Throw',
            'The same bevel as the Aperture, but lit. Ring depth still sets the level\n'
            ' * lines — they follow the contour, so the structure is the object\'s, not a\n'
            ' * pattern laid over it — while the *value* of each ring is pushed by its\n'
            ' * angle to a source off-frame at the upper left.\n'
            ' *\n'
            ' * The result is a wall that runs bright along the top-left and deep along the\n'
            ' * bottom-right without a single straight-edged band anywhere in it. The face\n'
            ' * field is untouched by the push and stays one flat tone.',
            'The Aperture under a light. Ring depth still draws the level lines, so they bend with the silhouette, but each ring\'s value is pushed by its angle to an off-frame source: the upper-left wall runs bright, the lower-right deep, and the field the ZZ sits on stays flat.'),
    'p45': ('Reflector',
            'Glass, which is the other honest way to say *screen* without drawing a\n'
            ' * button. A two-pixel case carries a lit upper edge and a shaded lower one,\n'
            ' * then a black bezel, then a front surface with a rim vignette falling into\n'
            ' * the corners.\n'
            ' *\n'
            ' * Two specular streaks are struck at 45° across the left band. They are\n'
            ' * deliberately asymmetric — a reflection is a fact about where the light is,\n'
            ' * and a mirrored pair would read as decoration — and they are clipped a pixel\n'
            ' * clear of the face box, so the field under the ZZ is one flat tone.',
            'Glass says screen without drawing a button. A lit case edge, a black bezel, a vignetted front surface, and two specular streaks struck at 45° across the left band — asymmetric, because a reflection is a fact about where the light is. Both are clipped clear of the face.'),
    'p46': ('Well',
            'The bevel taken in discrete steps instead of a smooth ramp: three concentric\n'
            ' * plates, each two pixels deep, receding to the light at the bottom.\n'
            ' *\n'
            ' * Each plate is shaded as a recess rather than as a raised lid — the upper\n'
            ' * wall is in shadow and the lower one catches the light, which is the reverse\n'
            ' * of a boss and the reason this reads as a hollow you are looking into. The\n'
            ' * walls are measured against the whole solid at each step, not against the\n'
            ' * ring, because a ring has two top edges and shading both is what makes a\n'
            ' * bevel lie flat like a picture frame.',
            'The bevel taken in steps rather than as a ramp: three concentric plates, each shaded as a recess — upper wall in shadow, lower wall catching the light — receding to a lit floor. A hollow you look into, not a stack of lids.'),
}


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def symmetric(shape):
    return all((31 - x, y) in shape for x, y in shape)


def no_spurs(shape):
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    for i, y in enumerate(ys):
        w, up = len(rows[y]), len(rows[ys[i - 1]]) if i else 0
        dn = len(rows[ys[i + 1]]) if i + 1 < len(ys) else 0
        if w > up and w > dn:
            return False
    return True


def audit(slug, spec):
    body, key, layers = spec['body'], spec['key'], spec['layers']
    msgs = []

    if not symmetric(body):
        msgs.append('silhouette is not mirrored about x=16')
    if not no_spurs(body):
        msgs.append('silhouette has a spur')

    x0, y0, x1, y1 = bbox(body)
    if x0 < 2 or x1 > 29 or y0 < 2 or y1 > 29:
        msgs.append('breaks the 28x28 safe area')

    painted = set(key)
    for _, s in layers:
        if s & painted:
            msgs.append('layers overlap')
        painted |= s
    if painted != body:
        msgs.append(f'{len(body - painted)} unpainted pixels')

    for i, (fill, s) in enumerate(layers):
        if i != spec['field'] and is_slab(s, body):
            msgs.append(f'{fill} is a floating slab')

    face = {(x, y)
            for x in range(FB['x'], FB['x'] + FB['w'])
            for y in range(FB['y'], FB['y'] + FB['h'])}
    under = {fill for fill, s in layers if s & face}
    if len(under) != 1:
        msgs.append(f'face field is not calm: {sorted(under)}')

    tones = {INK} | {fill for fill, s in layers if s}
    if not 8 <= len(tones) <= 11:
        msgs.append(f'{len(tones)} tones, want 8-11')

    return not msgs, len(tones), msgs


def facepx(spec):
    out = set()
    cx, cy = spec['face']
    for d in face_paths(cx=cx, cy=cy, size=FACE_SIZE, smile=FACE_SMILE, gap=FACE_GAP):
        head, rest = d.split('h', 1)
        x, y = head[1:].split(' ')
        for k in range(int(rest.split('v')[0])):
            out.add((int(x) + k, int(y)))
    return out


def show(spec):
    marks = '.123456789abcdef'
    fill = {p: '#' for p in spec['key']}
    for i, (_, s) in enumerate(spec['layers']):
        for p in s:
            fill[p] = marks[i + 1]
    for p in facepx(spec):
        fill[p] = '@'
    print('    ' + ''.join(str(i % 10) for i in range(GRID)))
    for y in range(GRID):
        row = ''.join(fill.get((x, y), ' ') for x in range(GRID))
        if row.strip():
            print(f'{y:3} ' + row)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------

ASTRO = '''---
/**
 * __SLUG__ · __NAME__
 *
 * __DOC__
 *
 * __TONES__ tones. Face: `md` + `compact` + gap 2, which is exactly 8x8,
 * centred on the container with __AIRX__ px of air either side and __AIRY__ above
 * and below. Nothing is cleared for it.
 */
import MarkFrame from '../MarkFrame.astro';
import { facePathsAt } from '../../../data/mark';

interface Props { size?: number }
const { size = 128 } = Astro.props;
---

<MarkFrame size={size} title="Plozz — __NAME__">
__PATHS__
  <g fill="__FACE__" shape-rendering="crispEdges">
    {facePathsAt({ cx: __CX__, cy: __CY__, size: '__SZ__', smile: '__SMILE__', gap: __GAP__ }).map((d) => (
      <path d={d} />
    ))}
  </g>
</MarkFrame>
'''

META = '''export default {
  n: '__SLUG__', name: '__NAME__',
  idea: '__IDEA__',
  ground: 'light',
  palette: __PALETTE__,
};
'''


def emit(slug, spec):
    name, doc, idea = DOCS[slug]
    parts = [f'  <path d="{" ".join(to_paths(s))}" fill="{f}" />'
             for f, s in spec['layers'] if s]
    parts.append(f'  <path d="{" ".join(to_paths(spec["key"]))}" fill="{INK}" />')
    cx, cy = spec['face']
    x0, y0, x1, y1 = bbox(spec['body'])
    tones = len({INK} | {f for f, s in spec['layers'] if s})

    astro = (ASTRO
             .replace('__SLUG__', slug)
             .replace('__NAME__', name)
             .replace('__DOC__', doc)
             .replace('__TONES__', str(tones))
             .replace('__AIRX__', str(FB['x'] - x0))
             .replace('__AIRY__', str(FB['y'] - y0))
             .replace('__PATHS__', '\n'.join(parts))
             .replace('__FACE__', FACE)
             .replace('__CX__', str(cx))
             .replace('__CY__', str(cy))
             .replace('__SZ__', FACE_SIZE)
             .replace('__SMILE__', FACE_SMILE)
             .replace('__GAP__', str(FACE_GAP)))
    (OUT / f'{slug}.astro').write_text(astro)

    seen, pal = {INK}, [INK]
    for f, s in spec['layers']:
        if s and f not in seen:
            seen.add(f)
            pal.append(f)
    (OUT / f'{slug}.meta.ts').write_text(
        META.replace('__SLUG__', slug)
            .replace('__NAME__', name)
            .replace('__IDEA__', idea)
            .replace('__PALETTE__', '[' + ', '.join(f"'{c}'" for c in pal) + ']'))


def build_all():
    out = {}
    for slug, fn in BUILDERS.items():
        out[slug] = fn()
    return out


if __name__ == '__main__':
    write = '--write' in sys.argv
    for slug, spec in build_all().items():
        ok, n, msgs = audit(slug, spec)
        print(f'\n=== {slug} · {spec["name"]} — {n} tones — {"ok" if ok else "FAIL"}')
        for m in msgs:
            print('   !', m)
        show(spec)
        if write and ok:
            emit(slug, spec)
            print(f'   wrote {slug}.astro / {slug}.meta.ts')
