"""
Breath rosette marks — c22–c25.

The one idea in every Breathe reference is *overlap*: translucent circles laid
over each other, where the tone at a pixel is a function of how many circles
cover it. So none of these four is painted. A depth map is counted first —
`depth[p] = how many petals cover p` — and every tone is a slice of that count.
The ramp therefore falls out of the geometry, and the deepest overlap, which is
the calmest part of the form, is where the face goes.

Three things the rejected marks got wrong, all fixed here by assertion:

*Protrusions.* A pixel disc widens by six or more in a row near its cap, which
reads as a spur. Every silhouette here is trimmed top-down and bottom-up so no
row is more than two wider than its neighbour above. The trim is applied about
x=16, so it cannot break the mirror.

*Symmetry.* The depth map is counted for the left half and mirrored into the
right, so every layer is symmetric about x=16 by construction, not by luck.

*Centring.* The face is placed from the measured (height, offset) table, never
computed, and both the air inside the field it sits on and the air inside the
whole silhouette are asserted equal.

The palette is deliberately a cooler, greyer sea-teal than Hozz's #12b39a,
because the Apple reference is teal too and a straight copy of its hue would
read as one.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import keyline, to_paths, is_slab  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
GRID = 32
CX = 16.0

# Measured off the face module. (height, top offset from cy) per gap. Never
# recomputed — an even-height face is not symmetric about cy.
GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
    'sm': {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)},
}
FACE_W = {'lg': 10, 'md': 8, 'sm': 7}


# --------------------------------------------------------------------------- #
# geometry
# --------------------------------------------------------------------------- #

def mirror(s):
    """Complete a left-half set into a full mirror-symmetric one."""
    return {(x, y) for x, y in s} | {(31 - x, y) for x, y in s}


def disc(cx, cy, r):
    rr = r * r
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr}


def annulus(cx, cy, r, t):
    ri = max(r - t, 0.0)
    rr, rri = r * r, ri * ri
    return {(x, y) for x in range(GRID) for y in range(GRID)
            if rri < (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= rr}


def petal_centres(n, cy, dist, phase=-90.0):
    """n points on a ring. Rounded so the pair at ±angle mirrors exactly."""
    out = []
    for i in range(n):
        a = math.radians(phase + i * 360.0 / n)
        out.append((CX + round(dist * math.cos(a), 6), cy + round(dist * math.sin(a), 6)))
    return out


def depth_map(n, cy, dist, r, phase=-90.0, ring=None):
    """{(x, y): how many petals cover it}. Counted on the left half and
    mirrored, so the map is symmetric about x=16 by construction."""
    half = {}
    for (px, py) in petal_centres(n, cy, dist, phase):
        pet = disc(px, py, r) if ring is None else annulus(px, py, r, ring)
        for (x, y) in pet:
            if x <= 15:
                half[(x, y)] = half.get((x, y), 0) + 1
            else:
                # count the mirrored pixel instead; the arrangement is
                # left-right symmetric, so the two agree.
                pass
    full = {}
    for (x, y), v in half.items():
        full[(x, y)] = v
        full[(31 - x, y)] = v
    return full


def rows_of(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: sorted(v) for y, v in sorted(rows.items())}


def widths(s):
    return {y: xs[-1] - xs[0] + 1 for y, xs in rows_of(s).items()}


def fill_rows(body):
    """Close every row into one run. A union of circles can leave a row split
    into two feet with paper showing between them; that reads as a defect, and
    filling min..max cannot break the mirror."""
    return {(x, y) for y, xs in rows_of(body).items()
            for x in range(xs[0], xs[-1] + 1)}


def trim_profile(body):
    """Trim rows, symmetrically about x=16, until no row is more than two
    wider than the row above or below it. This is what kills the spurs a bare
    pixel circle grows at its cap."""
    body = fill_rows(body)
    w = widths(body)
    ys = sorted(w)
    for _ in range(4):
        for y in ys[1:]:
            if y - 1 in w:
                w[y] = min(w[y], w[y - 1] + 2)
        for y in reversed(ys[:-1]):
            if y + 1 in w:
                w[y] = min(w[y], w[y + 1] + 2)
    out = set()
    for y in ys:
        if w[y] < 2:
            continue
        half = w[y] / 2.0
        lo, hi = int(CX - half), int(CX + half) - 1
        out |= {(x, y) for x in range(lo, hi + 1)}
    return out


def split_rows(body):
    """Rows that are not a single contiguous run."""
    return [y for y, xs in rows_of(body).items()
            if xs[-1] - xs[0] + 1 != len(xs)]


def profile_faults(body):
    w = widths(body)
    ys = sorted(w)
    return ([(ys[i], w[ys[i - 1]], w[ys[i]]) for i in range(1, len(ys))
             if ys[i] == ys[i - 1] + 1 and w[ys[i]] - w[ys[i - 1]] > 2]
            + [(ys[i], w[ys[i + 1]], w[ys[i]]) for i in range(len(ys) - 1)
               if ys[i] + 1 == ys[i + 1] and w[ys[i]] - w[ys[i + 1]] > 2])


def count_faults(body):
    r = rows_of(body)
    ys = sorted(r)
    return ([(ys[i], len(r[ys[i - 1]]), len(r[ys[i]])) for i in range(1, len(ys))
             if ys[i] == ys[i - 1] + 1 and len(r[ys[i]]) - len(r[ys[i - 1]]) > 2]
            + [(ys[i], len(r[ys[i + 1]]), len(r[ys[i]])) for i in range(len(ys) - 1)
               if ys[i] + 1 == ys[i + 1] and len(r[ys[i]]) - len(r[ys[i + 1]]) > 2])


def symmetric(s):
    return all((31 - x, y) in s for x, y in s)


# --------------------------------------------------------------------------- #
# face placement
# --------------------------------------------------------------------------- #

def place_face(field, body, sizes=('md', 'sm', 'lg'), gaps=(2, 3, 1, 4), pad_min=1):
    """Find a face size and gap whose height splits *both* the field it sits on
    and the whole silhouette into exactly equal air. Returns None if nothing
    fits — the caller then changes the geometry, never the offset."""
    fr = rows_of(field)
    fys = sorted(fr)
    if not fys or fys[-1] - fys[0] + 1 != len(fys):
        return None
    span = fys[-1] - fys[0] + 1
    bys = sorted({y for _, y in body})
    btop, bbot = bys[0], bys[-1]
    for size in sizes:
        w = FACE_W[size]
        lo, hi = 16 - w // 2, 16 + (w - w // 2) - 1
        for gap in gaps:
            h, off = GEOM[size][gap]
            if span <= h or (span - h) % 2:
                continue
            pad = (span - h) // 2
            if pad < pad_min:
                continue
            top = fys[0] + pad
            if any((x, y) not in field for y in range(top, top + h)
                   for x in range(lo, hi + 1)):
                continue
            above, below = top - btop, bbot - (top + h - 1)
            if above != below:
                continue
            return dict(size=size, gap=gap, h=h, cy=top - off, top=top,
                        pad=pad, above=above, below=below, span=span)
    return None


# --------------------------------------------------------------------------- #
# marks
# --------------------------------------------------------------------------- #

def ramp(pal, m):
    """m tones spread evenly across the ramp's tail, so a spec can change how
    many depth bands it keeps without needing a new palette."""
    tail = pal[1:]
    if len(tail) == m:
        return tail
    if m == 1:
        return [tail[-1]]
    return [tail[round(i * (len(tail) - 1) / (m - 1))] for i in range(m)]


def build(spec):
    """Turn a spec into ordered (pixels, fill) layers plus a placement report."""
    n, dist, r = spec['n'], spec['dist'], spec['r']
    cy, phase = spec.get('cy', 16.0), spec.get('phase', -90.0)
    pal = spec['palette']

    dep = depth_map(n, cy, dist, r, phase)
    body = trim_profile(set(dep))
    dep = {p: v for p, v in dep.items() if p in body}
    key = keyline(body)
    inner = body - key

    if spec['mode'] == 'lattice':
        rdep = depth_map(n, cy, dist, r, phase, ring=spec['ring'])
        rdep = {p: v for p, v in rdep.items() if p in inner}
        # Plain concentric centre so the face has clean ground; the rings that
        # would cross it are absorbed into it.
        core = disc(CX, cy, spec.get('core', 0.0)) & inner
        lattice2 = {p for p, v in rdep.items() if v >= 2} - core
        lattice1 = {p for p, v in rdep.items() if v == 1} - core
        ground = inner - core - lattice1 - lattice2
        field = core
        # Crossings glow brighter than the centre, as in the reference.
        g, l1, fd, l2 = spec.get('lat', (1, 3, 4, 5))
        layers = [(ground, pal[g]), (lattice1, pal[l1]), (field, pal[fd]),
                  (lattice2, pal[l2]), (key, pal[0])]
    else:
        K, core_r = spec['K'], spec.get('core', 0.0)
        # The bright centre. A plain concentric disc when `core` is given, so the
        # face never sits on a ragged star; otherwise the deep-overlap region.
        field = (disc(CX, cy, core_r) if core_r else
                 {p for p, v in dep.items() if v >= K}) & inner
        merge = spec.get('merge')  # optional depth->band grouping for flat reads
        bands = {}
        for p in inner - field:
            d = min(dep[p], K)
            b = merge[min(d, len(merge) - 1)] if merge else d
            bands.setdefault(b, set()).add(p)
        tones = ramp(pal, len(bands) + 1)
        layers = [(bands[b], tones[i]) for i, b in enumerate(sorted(bands))]
        layers.append((field, tones[-1]))
        layers.append((key, pal[0]))

    fit = place_face(field, body, sizes=spec.get('sizes', ('md', 'sm', 'lg')),
                     gaps=spec.get('gaps', (2, 3, 1, 4)),
                     pad_min=spec.get('pad_min', 1))
    return dict(layers=layers, body=body, field=field, key=key, dep=dep, fit=fit)


def check(slug, r):
    """Every hard requirement, asserted. Returns a one-line report."""
    body, fit = r['body'], r['fit']
    assert fit, f'{slug}: no face size/gap splits both the field and the mark evenly'
    for px, fill in r['layers']:
        assert px, f'{slug}: empty layer {fill}'
        assert symmetric(px), f'{slug}: layer {fill} is not symmetric about x=16'
        assert not is_slab(px, body), f'{slug}: layer {fill} floats as a slab'
    assert symmetric(body), f'{slug}: silhouette not symmetric'
    pf, cf = profile_faults(body), count_faults(body)
    assert not pf, f'{slug}: protrusion {pf}'
    assert not cf, f'{slug}: row-count spur {cf}'
    assert not split_rows(body), f'{slug}: split rows {split_rows(body)}'
    xs = [p[0] for p in body]
    ys = [p[1] for p in body]
    assert min(xs) >= 2 and max(xs) <= 29, f'{slug}: x {min(xs)}..{max(xs)} outside 2..29'
    assert min(ys) >= 2 and max(ys) <= 29, f'{slug}: y {min(ys)}..{max(ys)} outside 2..29'
    tones = len({f for _, f in r['layers']})
    assert tones >= 5, f'{slug}: only {tones} tones'
    covered = set().union(*[p for p, _ in r['layers']])
    assert covered == body, f'{slug}: {len(body - covered)} pixels unpainted'
    assert fit['above'] == fit['below'], f'{slug}: mark air {fit["above"]}/{fit["below"]}'
    return (f'{slug}  {tones} tones · {max(xs) - min(xs) + 1}x{max(ys) - min(ys) + 1} '
            f'at x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)} · face {fit["size"]} gap'
            f'{fit["gap"]} ({fit["h"]} rows) at cy {fit["cy"]} · field air '
            f'{fit["pad"]}/{fit["pad"]} · mark air {fit["above"]}/{fit["below"]}')


def svg_body(r):
    return '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />'
                     for p, f in r['layers'])


def ascii_art(r, grid=GRID):
    marks = ' 12345678'
    dep, fit = r['dep'], r['fit']
    ys = sorted({y for _, y in r['body']})
    out = []
    for y in range(ys[0], ys[-1] + 1):
        line = ''
        for x in range(grid):
            if (x, y) in r['key']:
                line += '#'
            elif (x, y) in r['field']:
                line += '@'
            elif (x, y) in dep:
                line += marks[dep[(x, y)]]
            else:
                line += '.'
        out.append(f'{y:3} {line}')
    return '\n'.join(out)


OUT = ROOT / 'src' / 'components' / 'mark' / 'logos'


def write(slug, name, idea, doc, spec):
    """Emit the .astro + .meta.ts pair, after every hard check has passed."""
    r = build(spec)
    line = check(slug, r)
    fit, pal = r['fit'], [f for _, f in r['layers']]
    tones = list(dict.fromkeys(pal))
    body = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />'
                     for p, f in r['layers'])
    (OUT / f'{slug}.astro').write_text(f'''---
/**
 * {slug[1:]} · {name}
 *
{doc}
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {name}">
{body}
  <g fill="{spec['palette'][0]}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {fit['cy']}, size: '{fit['size']}', smile: 'wide', gap: {fit['gap']} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')
    swatch = ', '.join(f"'{c}'" for c in [spec['palette'][0]] + tones[:-1][::-1][:4])
    (OUT / f'{slug}.meta.ts').write_text(f'''export default {{
  n: '{slug[1:]}', name: '{name}',
  idea: '{idea}',
  ground: 'light',
  palette: [{swatch}],
}};
''')
    return line


SEA = ['#06282e', '#0e4f57', '#1b7a80', '#45aca4', '#86d3c5', '#cdefe1']
GLACIER = ['#062632', '#0d4b60', '#17738b', '#3ba0ab', '#79c9cf', '#c6ecec']
PETROL = ['#041f27', '#0b4450', '#157079', '#3aa39c', '#7bcfbf', '#d2f0e2']
MINT = ['#08302f', '#10585a', '#1e8781', '#4fb5a3', '#93dcc4', '#d8f2e3']

MARKS = [
    ('c22', 'Rosette, Six', SEA,
     'Six breaths overlapping — the six-lobed star is where they meet.',
     ' * Six translucent circles on a ring of 6.0, radius 8.0. Every pixel is\n'
     ' * toned by how many circles cover it, so the six-lobed star in the middle\n'
     ' * is not drawn: it is the region three or more petals agree on.\n'
     ' *\n'
     ' * The rim is chamfered rather than scalloped. A pixel circle widens by\n'
     ' * four at its cap, which would be a spur, so each row is clamped to at\n'
     ' * most two wider than the row above it — done symmetrically about x=16,\n'
     ' * top-down and bottom-up. The flower therefore reads from the banding\n'
     ' * inside, which is where the idea lives anyway.\n'
     ' *\n'
     ' * The bright centre is a plain concentric disc so the face never sits on\n'
     ' * a ragged star. Its height and offset come from the measured face table,\n'
     ' * never computed here.\n'
     ' *\n'
     ' * Six tones: keyline, three depth bands, the centre, and the face in the\n'
     ' * keyline colour. A cooler sea-teal than the brand hue, because the\n'
     ' * reference this borrows from is teal too.',
     dict(mode='fill', n=6, dist=6.0, r=8.0, cy=16.0, K=4, core=5.0,
          merge=[0, 0, 1, 2, 2, 2, 2], palette=SEA)),
    ('c23', 'Rosette, Eight', GLACIER,
     'Eight breaths instead of six — finer petals, and a sunburst rather than a star.',
     ' * Eight circles on a ring of 6.0, radius 8.5. Doubling the petal count\n'
     ' * from the six halves the angle between them, so the overlaps are\n'
     ' * narrower and the centre resolves into a sunburst instead of a star.\n'
     ' *\n'
     ' * Same construction as the six: depth counted per pixel, grouped into\n'
     ' * three broad bands so the lobes read as flat shapes rather than a\n'
     ' * gradient, rows clamped against spurs, bright centre a plain disc.\n'
     ' *\n'
     ' * This is the widest of the four — 28 across, filling the safe box — and\n'
     ' * the one that survives smallest, because eight lobes around a circle\n'
     ' * still read as texture when they stop reading as petals.\n'
     ' *\n'
     ' * Glacier teal: pushed bluer than the six so the two do not read as the\n'
     ' * same mark twice.',
     dict(mode='fill', n=8, dist=6.0, r=8.5, cy=16.0, K=4, core=5.0,
          merge=[0, 0, 0, 1, 2, 2, 2, 2, 2], palette=GLACIER)),
    ('c24', 'Rosette, Lattice', PETROL,
     'The petals drawn as rings, not discs — so the mark is the lattice their edges make.',
     ' * The same six-petal geometry, but each petal is an annulus two pixels\n'
     ' * thick rather than a filled disc. The rings cross, and the crossings —\n'
     ' * two rings deep — are the brightest tone in the mark, brighter than the\n'
     ' * centre. That is the one place the overlap rule is visible as light\n'
     ' * rather than as shape, and it leaves six dark cells ribbed apart by\n'
     ' * bright arcs.\n'
     ' *\n'
     ' * The silhouette is still the filled union, so there are no holes to the\n'
     ' * paper and the row-width rule holds; the lattice is painted inside it.\n'
     ' * The centre is a plain disc that absorbs the arcs that would otherwise\n'
     ' * cross the face.\n'
     ' *\n'
     ' * Busiest of the four by a distance. It holds at 48 and is texture by 24,\n'
     ' * which is an honest cost of the idea rather than a fault in it.',
     dict(mode='lattice', n=6, dist=6.5, r=8.0, cy=16.0, ring=2, K=3,
          core=5.5, lat=(1, 2, 4, 5), palette=PETROL)),
    ('c25', 'Rosette, Five', MINT,
     'Five breaths, flattened to two bands and an outline — the calmest reading of the same rule.',
     ' * Five circles, ring 5.0, radius 9.0. Odd counts have no mirror pair top\n'
     ' * to bottom, so the pentafoil sits off-centre by construction and the\n'
     ' * face is placed to equalise air against the silhouette, not the grid.\n'
     ' *\n'
     ' * Flattest of the four on purpose: the depth map is collapsed to two\n'
     ' * bands plus a wide centre, so what is left is the outer boundary, one\n'
     ' * step of shade, and a five-pointed field. Nothing gradates.\n'
     ' *\n'
     ' * This is the one that still reads as a single object at 16 pixels, and\n'
     ' * the one that gives up the most of the flower to get there.\n'
     ' *\n'
     ' * Soft mint — the least saturated of the set.',
     dict(mode='fill', n=5, dist=5.0, r=9.0, cy=15.5, K=4, core=6.0,
          merge=[0, 0, 1, 2, 2, 2], palette=MINT)),
]

if __name__ == '__main__':
    for slug, name, _pal, idea, doc, spec in MARKS:
        print(write(slug, name, idea, doc, spec))
