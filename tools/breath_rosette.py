"""
Breath rosette marks — c22–c25.

The one idea in every Breathe reference is *overlap*: translucent circles laid
over each other, where the tone at a pixel is a function of how many circles
cover it. So none of these four is painted. A depth map is counted first —
`depth[p] = how many petals cover p` — and every tone is a slice of that count.
The ramp therefore falls out of the geometry, and the deepest overlap, which is
the calmest part of the form, is where the face goes.

*Every petal is a canonical circle, translated.* Not one radius test appears in
this file. Petals come from `circles.circle(...)` — the profile lifted off the
shipped Mozz mark — and are moved by whole-pixel offsets, so all n petals are
byte-identical to each other, as they plainly are in the reference images. The
earlier pass rasterised `x² + y² <= r²` at a different radius per mark and got a
different-looking circle every time; several came out octagonal.

*The shoulder steps four, and that is correct.* Mozz's own profile opens
8, 12, 16 — two four-pixel steps — so an earlier rule of mine that clamped every
row to at most two wider than the row above it was flattening the corners into an
octagon. That clamp is gone. `circles.check` is the authority now: a silhouette
must be symmetric about x=16 and free of spurs, where a spur is a row wider than
both its neighbours. `monotone()` below enforces exactly that and nothing more,
so the four-steps survive.

*Light runs outward, not inward.* The references are pale flowers glowing out of
a mid ground, so depth is mapped to *brightness*: the pixel covered by every
petal is nearly white, and the fringe covered by one is the darkest thing inside
the keyline. Nothing in these marks is darker than its own rim except the
keyline, which is the only dark tone and the only thing holding the mark off the
paper. An earlier pass ran the ramp the other way and the overlaps read as dirt.

*Scallops are legal vertically and illegal horizontally.* The union of n discs
has a cleft wherever two petals meet, and `bite` mode keeps those clefts instead
of filling them. It can only ever show at the top and bottom: `circles.check`
defines a spur as a row wider than both its neighbours, and it measures a row
edge to edge, so a notch bitten downward does not widen the row and passes,
while a notch bitten into the left or right side shrinks that row and turns its
neighbours into spurs by definition. That is a hard limit of the rule, not a
shortcoming of the search — c22 takes the two clefts that are available.

*Symmetry.* Petal offsets are whole pixels in ± pairs and the canonical circle is
symmetric about x=16, so every layer mirrors by construction, not by luck.

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
from circles import circle, check as circle_check  # noqa: E402

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

def erode(shape):
    """Peel one pixel off every edge, four-connected."""
    return {(x, y) for x, y in shape
            if {(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)} <= shape}


def round_circle(across, top=2):
    """A circle `across` pixels wide, always from the canonical set.

    Sizes the module ships are used as they come. Anything smaller is *eroded*
    off `circle(20)` — peeling a pixel from every edge of a canonical circle
    keeps its profile and its symmetry (each step is verified by
    `circles.check`), which is a derivation rather than a fresh radius test.
    """
    if across in (20, 22, 24, 28):
        return circle(across, top)
    assert 10 <= across < 20 and across % 2 == 0, f'no circle at {across}'
    s = circle(20, 2)
    for _ in range((20 - across) // 2):
        s = erode(s)
    circle_check(s)
    ys = sorted({y for _, y in s})
    return {(x, y - ys[0] + top) for x, y in s}


def petal(across, dx=0, dy=0, top=2):
    """A circle moved by whole pixels. The only source of round shapes here."""
    return {(x + dx, y + dy) for x, y in round_circle(across, top)}


def outline(shape, t=1):
    """The outer `t` pixels of a shape. Derived from the canonical circle by
    erosion, so a petal ring keeps the circle's profile instead of needing a
    second radius."""
    inner = shape
    for _ in range(t):
        inner = erode(inner)
    return shape - inner


def petal_offsets(n, dist, phase=-90.0):
    """n whole-pixel offsets on a ring. Rounded, then forced into exact ±
    pairs so the rosette mirrors about x=16 with no float slop."""
    out = []
    for i in range(n):
        a = math.radians(phase + i * 360.0 / n)
        c, sn = round(math.cos(a), 9), round(math.sin(a), 9)
        # Round the magnitude, then reapply the sign, so an angle and its
        # reflection cannot round to different columns.
        dx = int(math.copysign(round(dist * abs(c)), c)) if c else 0
        dy = int(math.copysign(round(dist * abs(sn)), sn)) if sn else 0
        out.append((dx, dy))
    have = set(out)
    for dx, dy in out:
        assert (-dx, dy) in have, f'offsets not mirror-paired: {out}'
    return out


def rows_of(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: sorted(v) for y, v in sorted(rows.items())}


def widths(s):
    return {y: xs[-1] - xs[0] + 1 for y, xs in rows_of(s).items()}


def fill_rows(body):
    """Close every row into one run. A union of circles can leave a row split
    into two feet with paper showing between them; filling min..max cannot
    break the mirror."""
    return {(x, y) for y, xs in rows_of(body).items()
            for x in range(xs[0], xs[-1] + 1)}


def connected(shape):
    """One 4-connected piece."""
    if not shape:
        return False
    seed = min(shape)
    seen, stack = {seed}, [seed]
    while stack:
        x, y = stack.pop()
        for q in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if q in shape and q not in seen:
                seen.add(q)
                stack.append(q)
    return len(seen) == len(shape)


def scallop(body):
    """Clamp the row *extent* to one rise and one fall, but leave the interior
    alone — so the notches between petals at the top and bottom of the ring
    survive as real bites out of the outline.

    `circles.check` measures a row by `max - min + 1`, so a bite that cuts down
    into the mark between two petal caps does not read as a spur: the extent
    still climbs once and falls once. A bite at the *side* would, which is why
    the ring is always turned so the notches land top and bottom.
    """
    w = widths(body)
    ys = sorted(w)
    peak = max(range(len(ys)), key=lambda i: (w[ys[i]], -abs(i - len(ys) // 2)))
    v = dict(w)
    for i in range(peak - 1, -1, -1):
        v[ys[i]] = min(v[ys[i]], v[ys[i + 1]])
    for i in range(peak + 1, len(ys)):
        v[ys[i]] = min(v[ys[i]], v[ys[i - 1]])
    out = set()
    for y in ys:
        if v[y] < 2:
            continue
        lo, hi = int(CX - v[y] / 2.0), int(CX + v[y] / 2.0) - 1
        out |= {(x, y) for x, y in body if lo <= x <= hi}
    return out


def monotone(body):
    """Remove local maxima in row width — the only defect `circles.check` names.

    The widths are cut down to the largest profile that rises to one peak and
    falls away again. That deletes a bulge without inflating anything, and it
    leaves the four-pixel shoulder steps of the canonical circle untouched.
    Rows are rebuilt as centred runs about x=16, so the mirror survives.
    """
    body = fill_rows(body)
    w = widths(body)
    ys = sorted(w)
    peak = max(range(len(ys)), key=lambda i: (w[ys[i]], -abs(i - len(ys) // 2)))
    v = dict(w)
    for i in range(peak - 1, -1, -1):
        v[ys[i]] = min(v[ys[i]], v[ys[i + 1]])
    for i in range(peak + 1, len(ys)):
        v[ys[i]] = min(v[ys[i]], v[ys[i - 1]])
    out = set()
    for y in ys:
        if v[y] < 2:
            continue
        half = v[y] / 2.0
        lo, hi = int(CX - half), int(CX + half) - 1
        out |= {(x, y) for x in range(lo, hi + 1)}
    return out


def depth_map(n, dist, size, phase=-90.0, top=2, ring=None):
    """depth[p] = how many petals cover p. Petals are identical translated
    canonical circles; a ring petal is that circle's outline."""
    dep = {}
    for dx, dy in petal_offsets(n, dist, phase):
        pet = petal(size, dx, dy, top)
        if ring:
            pet = outline(pet, ring)
        for q in pet:
            dep[q] = dep.get(q, 0) + 1
    return dep


def profile_faults(body):
    """Rows wider than both neighbours — `circles.check`'s definition."""
    w = widths(body)
    ys = sorted(w)
    return [(ys[i], w[ys[i - 1]], w[ys[i]], w[ys[i + 1]])
            for i in range(1, len(ys) - 1)
            if w[ys[i]] > w[ys[i - 1]] and w[ys[i]] > w[ys[i + 1]]]


def count_faults(body):
    r = rows_of(body)
    ys = sorted(r)
    return [(ys[i], len(r[ys[i - 1]]), len(r[ys[i]]), len(r[ys[i + 1]]))
            for i in range(1, len(ys) - 1)
            if len(r[ys[i]]) > len(r[ys[i - 1]]) and len(r[ys[i]]) > len(r[ys[i + 1]])]


def split_rows(body):
    """Rows that are not a single contiguous run."""
    return [y for y, xs in rows_of(body).items()
            if xs[-1] - xs[0] + 1 != len(xs)]


def max_step(body):
    w = widths(body)
    ys = sorted(w)
    return max((w[ys[i]] - w[ys[i - 1]] for i in range(1, len(ys))), default=0)


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
    n, dist, size = spec['n'], spec['dist'], spec['size']
    phase, top = spec.get('phase', -90.0), spec.get('top', 2)
    pal = spec['palette']

    dep = depth_map(n, dist, size, phase, top)
    # Petals are offset up and down off the ring, so the union lands wherever it
    # lands. Slide it whole-pixel into the middle of the safe box; vertical
    # translation cannot touch the mirror.
    dy0 = 2 + (28 - (max(y for _, y in dep) - min(y for _, y in dep) + 1)) // 2
    dy0 -= min(y for _, y in dep)
    dep = {(x, y + dy0): v for (x, y), v in dep.items()}
    body = (scallop(set(dep)) if spec.get('bite') else monotone(set(dep)))
    dep = {p: v for p, v in dep.items() if p in body}
    key = keyline(body)
    inner = body - key
    # The bright centre: a canonical circle, concentric with the rosette.
    ys = sorted({y for _, y in body})
    ctr = spec.get('core')
    # An odd-row silhouette cannot hold an even-row circle concentrically, so
    # the centre may be nudged a whole pixel. `place_face` still has to find a
    # face that splits *both* the centre and the silhouette evenly, or the
    # build fails — the nudge buys a parity, it never fakes the air.
    core = (petal(ctr, 0, 0, (ys[0] + ys[-1] + 1 - ctr) // 2 + spec.get('core_dy', 0))
            & inner if ctr else set())

    if spec['mode'] == 'lattice':
        rdep = depth_map(n, dist, size, phase, top, ring=spec['ring'])
        rdep = {(x, y + dy0): v for (x, y), v in rdep.items()}
        rdep = {p: v for p, v in rdep.items() if p in inner}
        # Plain concentric centre so the face has clean ground; the ring arcs
        # that would cross it are absorbed into it.
        lattice2 = {p for p, v in rdep.items() if v >= 2} - core
        lattice1 = {p for p, v in rdep.items() if v == 1} - core
        ground = inner - core - lattice1 - lattice2
        field = core
        # Crossings glow brighter than the centre, as in the reference.
        g, l1, fd, l2 = spec.get('lat', (1, 3, 4, 5))
        layers = [(ground, pal[g]), (lattice1, pal[l1]), (field, pal[fd]),
                  (lattice2, pal[l2]), (key, pal[0])]
    else:
        K = spec['K']
        # A plain concentric circle when `core` is given, so the face never sits
        # on a ragged star; otherwise the deep-overlap region itself.
        field = core if ctr else ({p for p, v in dep.items() if v >= K} & inner)
        merge = spec.get('merge')  # optional depth->band grouping for flat reads
        bands = {}
        for p in inner - field:
            d = min(dep.get(p, 1), K)  # a filled row-gap counts as rim depth
            b = merge[min(d, len(merge) - 1)] if merge else d
            bands.setdefault(b, set()).add(p)
        tones = ramp(pal, len(bands) + 1)
        layers = [(bands[b], tones[i]) for i, b in enumerate(sorted(bands))]
        layers.append((field, tones[-1]))
        layers.append((key, pal[0]))

    fit = place_face(field, body, sizes=spec.get('sizes', ('md', 'sm', 'lg')),
                     gaps=spec.get('gaps', (2, 3, 1, 4)),
                     pad_min=spec.get('pad_min', 1))
    return dict(layers=layers, body=body, field=field, key=key, dep=dep, fit=fit,
                bite=bool(spec.get('bite')))


def check(slug, r):
    """Every hard requirement, asserted. Returns a one-line report."""
    body, fit = r['body'], r['fit']
    assert fit, f'{slug}: no face size/gap splits both the field and the mark evenly'
    for px, fill in r['layers']:
        assert px, f'{slug}: empty layer {fill}'
        assert symmetric(px), f'{slug}: layer {fill} is not symmetric about x=16'
        assert not is_slab(px, body), f'{slug}: layer {fill} floats as a slab'
    assert symmetric(body), f'{slug}: silhouette not symmetric'
    assert connected(body), f'{slug}: silhouette is in more than one piece'
    circle_check(body)  # canonical authority: mirrored about x=16, no spurs
    pf, cf = profile_faults(body), count_faults(body)
    assert not pf, f'{slug}: protrusion {pf}'
    assert not cf, f'{slug}: row-count spur {cf}'
    sr = split_rows(body)
    if r.get('bite'):
        # A bitten rosette is allowed gaps, but only where they are notches
        # between petal caps at the very top and bottom — never a row that has
        # come apart into two feet somewhere in the middle.
        mid = (min(p[1] for p in body) + max(p[1] for p in body)) / 2.0
        deep = [y for y in sr if abs(y - mid) < len(set(p[1] for p in body)) / 4.0]
        assert not deep, f'{slug}: split rows near the equator {deep}'
    else:
        assert not sr, f'{slug}: split rows {sr}'
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
            f'{fit["pad"]}/{fit["pad"]} · mark air {fit["above"]}/{fit["below"]}'
            f' · max width step {max_step(body)}')


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
    lum = lambda c: (int(c[1:3], 16) * 2 + int(c[3:5], 16) * 5 + int(c[5:7], 16))
    ordered = sorted((t for t in tones if t != spec['palette'][0]), key=lum)
    swatch = ', '.join(f"'{c}'" for c in [spec['palette'][0]] + ordered[:4])
    (OUT / f'{slug}.meta.ts').write_text(f'''export default {{
  n: '{slug[1:]}', name: '{name}',
  idea: '{idea}',
  ground: 'light',
  palette: [{swatch}],
}};
''')
    return line


# Light-forward ramps. The first entry is the keyline and the face; everything
# after it is the mark itself, and it starts at a *mid* teal rather than a dark
# one. The reference flowers are pale shapes glowing out of a mid ground, so the
# darkest thing inside any of these marks is its outermost band, and the deepest
# overlap — the calm middle where the face goes — is very nearly white.
SEA = ['#06282e', '#2f948f', '#54b3a6', '#87d0c1', '#b8e6da', '#eefaf5']
GLACIER = ['#062632', '#2f8ca4', '#54acbc', '#8bcbd5', '#bde5ea', '#eef9fb']
LAGOON = ['#04222a', '#2a9b91', '#57bcaa', '#8ed8c3', '#c0ebdd', '#f0fbf6']
MINT = ['#08302f', '#35a08e', '#5fbfa8', '#95dac2', '#c4ecdc', '#f1fbf6']

MARKS = [
    ('c22', 'Rosette, Six', SEA,
     'Six breaths overlapping, and you can count them round the rim.',
     ' * Six identical circles, each one `circles.circle(14)` translated seven\n'
     ' * pixels off centre and nothing more. Not a radius test in sight: the\n'
     ' * petal profile is the one lifted off the shipped Mozz mark, so all six\n'
     ' * petals are the same shape to the pixel, as they plainly are in the\n'
     ' * reference.\n'
     ' *\n'
     ' * This is the one where the petal count reaches the outline. The union of\n'
     ' * six discs is not a circle — it has a cleft wherever two petals meet —\n'
     ' * and here those clefts are kept rather than filled in, so the top and\n'
     ' * bottom of the mark are bitten into by the gap between two petal caps.\n'
     ' * That is as far as a scallop can honestly go: `circles.check` calls any\n'
     ' * row wider than both its neighbours a spur, so a cleft cut into the left\n'
     ' * or right side would be a fault by definition. Vertically it is legal,\n'
     ' * because a row is measured edge to edge and a notch does not widen it.\n'
     ' *\n'
     ' * Tone runs the other way from a shadow: the more petals cover a pixel\n'
     ' * the lighter it is, so the middle is nearly white and the single-petal\n'
     ' * fringe is the darkest thing inside the keyline. The mark gives off\n'
     ' * light instead of collecting dirt.\n'
     ' *\n'
     ' * The bright centre is another canonical circle, concentric, so the face\n'
     ' * never sits on a ragged star. Its height and offset come from the\n'
     ' * measured face table, never computed here.',
     dict(mode='fill', n=6, dist=7.0, size=14, phase=0.0, K=4, core=12, bite=True,
          merge=[0, 0, 1, 2, 2, 2, 2, 2, 2], palette=SEA)),
    ('c23', 'Rosette, Eight', GLACIER,
     'Eight breaths instead of six — finer petals, and a sunburst rather than a star.',
     ' * Eight circles on a ring of six, each the same translated\n'
     ' * `circles.circle(14)`. Doubling the petal count from the six halves the\n'
     ' * angle between them, so the overlaps are narrower and the middle\n'
     ' * resolves into a sunburst of eight rays instead of a six-pointed star.\n'
     ' *\n'
     ' * The ring is rolled half a step so no petal sits on an axis. Eight caps\n'
     ' * facet the rim finely enough that it reads as a flower rather than as a\n'
     ' * disc with dents, and the widest row is still the centre one, so the\n'
     ' * profile rises once and falls once with no spur anywhere.\n'
     ' *\n'
     ' * Depth is grouped into three broad bands rather than left as a gradient,\n'
     ' * which is what keeps the rays legible once the mark is small enough that\n'
     ' * individual petals stop resolving.\n'
     ' *\n'
     ' * Lit from the middle out: eight petals deep is almost white, one petal\n'
     ' * deep is the mid teal the whole thing floats on. The rays are light\n'
     ' * leaving the centre, which is the only way this reads as breathing\n'
     ' * rather than as staining.\n'
     ' *\n'
     ' * Glacier teal: pushed bluer than the six so the two do not read as the\n'
     ' * same mark twice.',
     dict(mode='fill', n=8, dist=6.0, size=14, phase=-67.5, K=3, core=10,
          merge=[0, 0, 1, 2, 2, 2, 2, 2, 2], palette=GLACIER)),
    ('c24', 'Rosette, Bloom', LAGOON,
     'The same flower with everything small taken out of it — built to be read at 24 pixels.',
     ' * This replaces a lattice mark that was lovely at 96 pixels and mud at\n'
     ' * 24. An app icon lives at small sizes, so this one is designed at the\n'
     ' * small size and allowed to be plain at the large one.\n'
     ' *\n'
     ' * Six petals again, but bigger — `circles.circle(16)` on a ring of six —\n'
     ' * and turned point-up rather than flat-up, so it stands vertically where\n'
     ' * the six lies horizontally and the two cannot be confused.\n'
     ' *\n'
     ' * Everything narrow has been merged away. Depths one and two are one\n'
     ' * band, three is a second, and everything deeper is the centre, which is\n'
     ' * a canonical circle of near-white. What is left is three areas, not a\n'
     ' * gradient: a mid-teal rim, a pale six-pointed star where the petals\n'
     ' * agree, and a light middle with the face on it. Three areas survive\n'
     ' * being four pixels across; eight rays do not.\n'
     ' *\n'
     ' * At this ring distance the petals overlap too far to leave a cleft in the\n'
     ' * outline, so unlike the six the flower is carried entirely by the star\n'
     ' * inside it. That is the trade: a bitten rim is the first thing to go\n'
     ' * when the mark has to survive being twenty-four pixels wide.',
     dict(mode='fill', n=6, dist=6.0, size=16, phase=-90.0, K=3, core=12, bite=True,
          merge=[0, 0, 1, 2, 2, 2, 2, 2, 2], palette=LAGOON)),
    ('c25', 'Rosette, Five', MINT,
     'Five breaths — the one count with no mirror pair, so the field itself is a five-pointed star.',
     ' * Five circles, which is the one count with no mirror pair top to bottom,\n'
     ' * so the pentafoil sits point-up and the two halves of the mark are\n'
     ' * genuinely different shapes.\n'
     ' *\n'
     ' * The odd count also rules out a circular centre: an odd-row silhouette\n'
     ' * cannot hold an even-row circle with equal air above and below. So this\n'
     ' * is the only one of the four whose bright field is the *deep overlap\n'
     ' * itself* — the region all five petals cover. The five-pointed shape the\n'
     ' * face sits on is the rule made visible, not a disc laid on top of it.\n'
     ' *\n'
     ' * Five is also the most constrained count on this grid. The face has to\n'
     ' * split both the field and the whole mark into equal air, and with five\n'
     ' * petals almost nothing does: a full sweep of petal size, ring distance,\n'
     ' * phase, centre and depth threshold leaves one ring distance standing.\n'
     ' * So the petals here sit closer in than the six or the eight, and the\n'
     ' * mark earns its shape from the five-pointed field rather than from a\n'
     ' * deeply lobed rim. That is a real limit of the geometry, not a choice.\n'
     ' *\n'
     ' * What it does have is light. Four even steps run from a mid teal at the\n'
     ' * rim to the palest tone in the set at the middle, and because the field\n'
     ' * is the five-fold overlap rather than a disc, that palest tone arrives\n'
     ' * in the shape of a five-pointed star.\n'
     ' *\n'
     ' * Soft mint — the least saturated of the set.',
     dict(mode='fill', n=5, dist=4.0, size=20, phase=-54.0, K=5, core=None,
          merge=[0, 1, 2, 3, 3, 3, 3, 3, 3], palette=MINT)),
]

if __name__ == '__main__':
    for slug, name, _pal, idea, doc, spec in MARKS:
        print(write(slug, name, idea, doc, spec))
