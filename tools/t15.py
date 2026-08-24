"""
t15 — Swell. The bubble pulled toward the circle, and lit like one.

The brief opened one door: "you can change the shape slightly to make it more
round or cohesive." Hozz's chosen mark is a disc; Twozz's bubble is a rounded
rectangle with a five-row corner. They do not rhyme. So this mark takes its
corners **out of the same circle Hozz is drawn from** — the canonical
`circle(24)` cap, one step wider than Hozz's own 22 disc — and hangs them on a
28-wide body. The corner now runs nine rows instead of five, so the curvature of
a Twozz corner and the curvature of the Hozz disc are the same curve.

How far is too far: the body keeps 28x23, so it is still measurably wider than
it is tall (the shipped one is 28x23 too — the footprint is unchanged, only the
corners moved), it keeps five straight rows on each side and a twelve-pixel flat
top, and the tail is now the widest feature of the lower left. Take the corners
all the way to `circle(28)` and the flats vanish, the body becomes an ellipse,
and the mark is a face in a circle with a spike — Hozz's silhouette in purple.
That is the line, and this stops one step short of it.

Because the body is rounder, the tail has to do more, so it does two things the
shipped tail does not: it **takes over the bottom-left corner** rather than
hanging below a flat underside, so the left contour runs unbroken from the
corner into the spout and the two read as one drawn shape; and it carries the
**deepest two tones in the mark**, so it separates from the body by value as
well as by outline and survives the 24px row where a thin spike would not.

The interior is the exercise. Eleven tones, one monotone violet ramp, no step
larger than 16 on any channel. They are laid down by a single scalar field:
depth in from the outline (three steps, which is the glass meniscus) plus
distance from a light sitting off the top-left corner (which is the form), plus
a bonus on the spout (which is the fold). One field, so the light wraps the
corner, crosses the body and runs out into the tail without a seam anywhere.
Tone 6 of the ramp is #8f52f6, the shipped body colour, and it lands under the
face; the deepest is a shade darker than the shipped #7243c3.

The face is the shipped one — `lg`, wide smile, family gap — because 10 on 28 is
the same face-to-body ratio as Hozz's 8 on 22, and dropping to `md` would have
made the sibling smaller-faced than its own predecessor for no reason. Centred
on the **body**, tail ignored: 6 rows of air above, 6 below, measured.
"""
import json
import subprocess
import sys
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import CIRCLE_24, check  # noqa: E402
from shade import to_paths, is_slab, show, NEIGHBOURS  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't15'
NAME = 'Swell'

# ---------------------------------------------------------------------------
# The body: 28 across, corners lifted from the canonical 24 circle.
#
# CIRCLE_24's cap — the rows before it reaches full width — is the quadrant of
# a genuine 24-across circle. Widen every one of those rows by 4 and it becomes
# the corner of a 28-wide shape whose curvature is identical to that circle's.
# Nine rows of corner against the shipped five.
# ---------------------------------------------------------------------------
W = 28
CAP = []
for w in CIRCLE_24:                                     # leading run only
    if w == 24:
        break
    CAP.append(w + (W - 24))                            # 12 16 18 20 22 24 24 26 26
STRAIGHT = 5                                            # rows of full-width side
PROFILE = CAP + [W] * STRAIGHT + CAP[::-1]
TOP = 2

BODY = set()
for i, w in enumerate(PROFILE):
    x0 = 16 - w // 2
    BODY |= {(x0 + k, TOP + i) for k in range(w)}

BODY_W = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
BODY_Y0, BODY_Y1 = TOP, TOP + len(PROFILE) - 1
BODY_H = len(PROFILE)

# Symmetric about x=16 and free of spurs, asserted by the shared checker.
check(BODY)
assert (BODY_W, BODY_H) == (28, 23), (BODY_W, BODY_H)

# ---------------------------------------------------------------------------
# The tail.
#
# Rows are given explicitly rather than swept from a curve, because the thing
# that matters is the *contour*: the left edge has to leave the body's corner
# without a step out or a bite in. The body's leftmost column runs
#   ... 4 (y18-19) 5 (y20) 6 (y21) 7 (y22) 8 (y23) 10 (y24)
# so the tail claims x7 at y23 and x7-9 at y24 — finishing the corner's own
# staircase at 7 instead of letting it curl back in — then drops straight and
# tapers to a three-pixel blunt tip on y29, which is where the shipped tail
# ends too.
# ---------------------------------------------------------------------------
TAIL_ROWS = {
    23: (7, 7),
    24: (7, 9),
    25: (7, 14),
    26: (7, 12),
    27: (7, 11),
    28: (8, 10),
    29: (8, 9),
}
TAIL = {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)} - BODY
SPOUT = {p for p in TAIL if p[1] >= 25}          # the part that hangs free

SHAPE = BODY | TAIL

# Fit, and no spurs on the whole silhouette (the body is checked for symmetry
# separately above; the tail is deliberately asymmetric and exempt).
xs = sorted({x for x, _ in SHAPE})
ys = sorted({y for _, y in SHAPE})
assert (xs[0], xs[-1], ys[0], ys[-1]) == (2, 29, 2, 29), (xs[0], xs[-1], ys[0], ys[-1])

rows = {}
for x, y in SHAPE:
    rows.setdefault(y, []).append(x)
widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
for i in range(1, len(widths) - 1):
    assert not (widths[i] > widths[i - 1] and widths[i] > widths[i + 1]), \
        f'spur at row {ys[i]}'
# The left contour must never step back out once the tail has taken over: a
# bite in the outline is what makes a tail look bolted on.
left = [min(rows[y]) for y in ys]
for a, b in zip(left[BODY_Y1 - 2 - ys[0]:], left[BODY_Y1 - 1 - ys[0]:]):
    assert b >= a, f'left contour steps back out: {a} -> {b}'

# ---------------------------------------------------------------------------
# Depth: how many erosions in each pixel sits. 0 is the outline itself.
# ---------------------------------------------------------------------------
def depth_map(shape):
    d, cur, k = {}, set(shape), 0
    while cur:
        ring = {p for p in cur
                if any((p[0] + dx, p[1] + dy) not in cur for dx, dy in NEIGHBOURS)}
        for p in ring:
            d[p] = k
        cur -= ring
        k += 1
    return d


DEPTH = depth_map(SHAPE)
KEY_PX = {p for p, k in DEPTH.items() if k == 0}
INNER = SHAPE - KEY_PX

# Peel depth is an integer and wobbles by a pixel along a diagonal, which makes a
# rim light drawn from it speckle. This is the same measurement taken smoothly:
# the true distance from a pixel to the nearest pixel outside the mark, so it
# changes gradually as the contour turns.
OUTSIDE = [(x, y) for x in range(-2, 34) for y in range(-2, 34)
           if (x, y) not in SHAPE]
EDGE = {p: min(hypot(p[0] - q[0], p[1] - q[1]) for q in OUTSIDE) for p in INNER}

# ---------------------------------------------------------------------------
# The ramp. Eleven tones through the shipped body colour.
#
# 0-6 run from a light meniscus violet down to #8f52f6 exactly; 6-10 carry on
# past it into the shade. Every adjacent pair is checked: no channel may move
# more than MAX_STEP, or the interior reads as bands rather than as a surface.
# ---------------------------------------------------------------------------
LIGHT = (0xcd, 0xb0, 0xfa)
MID = (0x8f, 0x52, 0xf6)      # the shipped Twozz body colour, tone 6
DEEP = (0x66, 0x33, 0xbb)     # a shade under the shipped #7243c3, tone 10
N = 11
MID_AT = 6
MAX_STEP = 16


def lerp(a, b, t):
    return round(a + (b - a) * t)


RAMP = []
for i in range(N):
    if i <= MID_AT:
        c = [lerp(LIGHT[k], MID[k], i / MID_AT) for k in range(3)]
    else:
        c = [lerp(MID[k], DEEP[k], (i - MID_AT) / (N - 1 - MID_AT)) for k in range(3)]
    RAMP.append('#%02x%02x%02x' % tuple(c))

for a, b in zip(RAMP, RAMP[1:]):
    step = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert step <= MAX_STEP, f'{a}->{b} steps by {step}, which reads as a band'

KEY = '#241056'      # a near-black of the hue, as Mozz does it, not pure black
FACE_FILL = '#ffffff'

# ---------------------------------------------------------------------------
# One scalar field for the whole interior.
#
#   tone = BASE + SPREAD·(how far from the light) − rim lift + fold
#
# The second term is the form: a light sitting off the top-left corner, so the
# tone rises as the surface turns away from it and the isophotes curve the way
# they do on something round instead of running in straight bands.
#
# The rim lift is the glass edge — the outline lightened by up to three steps,
# c45's meniscus. It is drawn from a true distance to the edge rather than the
# integer peel depth, and it tapers with `nd`, so it is strongest where the
# surface faces the light and has gone out by the time it wraps underneath. Two
# earlier passes got this wrong: a flat full-strength meniscus put a bright band
# along the inside of the bottom edge that fought the falling gradient, and one
# keyed to peel depth speckled single pixels wherever that integer wobbled.
#
# The fold lifts the free part of the tail past the body it hangs off, so it
# reads as a plane turned under rather than a spike of the same colour.
#
# Because it is one field, nothing has a seam: the meniscus dims as it wraps
# under, the underside meets the tail already deep, and the ramp arrives at the
# face around tone 6 — the shipped violet — which is what the white sits on.
# ---------------------------------------------------------------------------
LIGHT_AT = (5.0, -2.0)
D0, D1 = 6.0, 30.0
BASE = 2.8
SPREAD = 6.8
RIM = 3.4          # how far the meniscus lifts the surface at the outline
MEN = 3.0          # how many pixels it takes to fall back to the interior
FOLD = 1.6


def tone_index(p):
    x, y = p
    d = hypot(x + 0.5 - LIGHT_AT[0], y + 0.5 - LIGHT_AT[1])
    nd = min(1.0, max(0.0, (d - D0) / (D1 - D0)))
    s = BASE + SPREAD * nd
    if p in SPOUT:
        s += FOLD
    else:
        near = max(0.0, 1.0 - (EDGE[p] - 2.0) / MEN)
        s -= RIM * near * (1 - nd)
    return max(0, min(N - 1, int(round(s))))


BANDS = {}
for p in INNER:
    BANDS.setdefault(tone_index(p), set()).add(p)

for i in range(N):
    assert len(BANDS.get(i, ())) >= 3, f'tone {i} ({RAMP[i]}) is unused — the field is mistuned'

# No layer may be a rectangle floating inside the shape.
for i, px in BANDS.items():
    assert not is_slab(px, SHAPE), f'tone {i} reads as a slab dropped in the bubble'

# The interior is tiled exactly once.
covered = set()
for px in BANDS.values():
    assert not (covered & px), 'two tones claim the same pixel'
    covered |= px
assert covered == INNER, 'the interior is not exactly covered'

# ---------------------------------------------------------------------------
# The face.
#
# Which rows count as "the body" decides this, and there are two honest answers:
#
#   outline   y2-24, 23 rows  — every row the body silhouette occupies, keyline
#                              ring included, tail-junction rows included.
#   field     y3-22, 20 rows  — the violet the face actually floats in: interior
#                              only (the keyline ring is outline, not field) and
#                              stopping where the tail takes the corner at y23,
#                              because those rows read as tail, not as chin.
#
# The eye reads the field, so the field is what the face is centred on, and it
# is measured off the emitted pixels rather than assumed. Twenty rows is even,
# so the face has to be even too: `lg` at gap 1 is 10 rows and lands 5/5. The
# family's gap of 2 is 11 rows and cannot split 20 evenly — it is what put this
# mark 5-above/4-below in the first place. 10 rows on a 23-row body is also the
# closer rhyme with Hozz, whose face is 9 on 22.
#
# The field's middle is y13.0 and the outline's is y13.5, so centring on the
# field leaves the outline half a row light on top: 6 above, 7 below. That is
# the safe direction — the tail already loads the bottom — and it is asserted,
# so the extra row can never drift back above the face.
# ---------------------------------------------------------------------------
GEOM_LG_WIDE = {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)}
FACE_W, GAP, SIZE, SMILE = 10, 1, 'lg', 'wide'
H, OFF = GEOM_LG_WIDE[GAP]

assert (BODY_W - FACE_W) % 2 == 0, \
    f'a {FACE_W}-wide face cannot centre on a {BODY_W}-wide body'

TAIL_TOP = min(TAIL_ROWS)
FIELD = {p for p in INNER if p in BODY and p[1] < TAIL_TOP}
FIELD_Y0 = min(y for _, y in FIELD)
FIELD_Y1 = max(y for _, y in FIELD)
FIELD_H = FIELD_Y1 - FIELD_Y0 + 1
assert (FIELD_H - H) % 2 == 0, \
    f'a {H}-row face cannot split the {FIELD_H}-row field evenly'

CY = (FIELD_Y0 + FIELD_Y1 + 1) / 2     # the field's middle; keyline and tail out


def pixels(d):
    import re
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


def measure(cx, cy, size, smile, gap):
    """faceBoxAt/facePathsAt straight out of mark.ts — never reimplemented."""
    js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
          f"const o={{cx:{cx},cy:{cy},size:'{size}',smile:'{smile}',gap:{gap}}};"
          "console.log(JSON.stringify({box: faceBoxAt(o), paths: facePathsAt(o)}));")
    out = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings',
         '-e', js],
        capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    face = set()
    for d in got['paths']:
        face |= pixels(d)
    return got['box'], face


box, FACE = measure(16, CY, SIZE, SMILE, GAP)
# The brief's table is quoted for an integer cy; this body's optical middle is a
# half. Check the table at the integer, then check this face against the table.
tbox, _ = measure(16, int(CY), SIZE, SMILE, GAP)
assert (tbox['h'], tbox['y'] - int(CY)) == (H, OFF), \
    f"mark.ts says {(tbox['h'], tbox['y'] - int(CY))}, the table says {(H, OFF)}"
assert (box['h'], box['y'] - CY) == (H, OFF - 0.5), \
    f"the face landed at {(box['h'], box['y'] - CY)} on cy={CY}"
assert box['w'] == FACE_W, f"mark.ts says the face is {box['w']} wide"

above, below = box['y'] - BODY_Y0, BODY_Y1 - box['bottom']
assert above == below, f'air {above} above / {below} below on the body'
assert box['x'] + box['right'] == 31, 'the face is not centred on x=16'
assert FACE <= BODY, 'the face hangs off the body'
assert not (FACE & KEY_PX), 'the face touches the keyline'

# The two Zs are one letter repeated, and the smile mirrors. A Z does not.
eyes = {p for p in FACE if p[1] < box['y'] + 5}
smile = {p for p in FACE if p[1] >= box['bottom'] - 3}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert {(x + 6, y) for x, y in eyes if x < 16} == {p for p in eyes if p[0] >= 16}, \
    'the two Zs are not the same letter'
assert all((31 - x, y) in smile for x, y in smile), 'the smile is not symmetric'

# What the face actually sits on. The white has to stay white against it.
under = {tone_index(p) for p in FACE if p in INNER}
assert min(under) >= 5, f'the face sits on tone {min(under)} — too light for white'

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
LAYERS = [(BANDS[i], RAMP[i]) for i in range(N)] + [(KEY_PX, KEY)]
tones = {f for _, f in LAYERS} | {FACE_FILL}

print(f'{SLUG} · {NAME}')
print(f'  body {BODY_W}x{BODY_H} (y{BODY_Y0}-{BODY_Y1}), corner = circle(24) cap, '
      f'{STRAIGHT} straight rows · tail y23-29, spout {len(SPOUT)}px')
print(f'  face {SIZE}/{SMILE} gap{GAP} = {FACE_W}x{H} at x{box["x"]}-{box["right"]} '
      f'y{box["y"]}-{box["bottom"]} · air {above}/{below} · under tones {sorted(under)}')
print(f'  {len(tones)} tones · ramp {" ".join(RAMP)} · key {KEY}')
print('  areas ' + ' '.join(f'{i}:{len(BANDS[i])}' for i in range(N)))

if '--show' in sys.argv:
    show([p for p, _ in LAYERS] + [FACE],
         [str(i % 10) for i in range(N)] + ['#', '@'])

body_rows = '\n'.join(
    f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in LAYERS)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG} · {NAME}
 *
 * The bubble pulled toward the circle, and lit like one.
 *
 * Hozz's chosen mark is a disc and this is a rounded rectangle, so the two did
 * not rhyme. The corners here are the cap of the canonical **24-across circle**
 * — one step wider than the 22 Hozz is drawn from — widened onto a 28 body, so
 * a Twozz corner and the Hozz disc are now literally the same curve. Nine rows
 * of corner against the shipped five.
 *
 * It stops one step short of round. The body is 28x23, the shipped footprint
 * exactly, with five straight rows on each side and twelve pixels of flat top;
 * take the corners to circle(28) and the flats vanish, the body becomes an
 * ellipse, and the mark is Hozz's silhouette in purple with a spike on it.
 *
 * The rounder the body, the more the tail carries — so it takes over the
 * bottom-left corner instead of hanging under a flat underside (the left
 * contour runs unbroken from corner into spout, never stepping back out), and
 * it holds the two deepest tones in the mark, so it separates by value as well
 * as by outline and survives at 24px.
 *
 * {len(tones)} tones. One monotone violet ramp, no step larger than {MAX_STEP} on any
 * channel, laid down by a single scalar field: three steps of meniscus in from
 * the outline, plus distance from a light off the top-left corner, plus a fold
 * on the spout. One field, so the light wraps the corner, crosses the body and
 * runs out into the tail with no seam. Ramp tone 6 is #8f52f6 — the shipped
 * body colour — and that is what the face sits on.
 *
 * The face is the shipped one: lg, wide smile, family gap. Ten on twenty-eight
 * is the same face-to-body ratio as Hozz's eight on twenty-two. Centred on the
 * **body**, tail ignored: {above} rows of air above, {below} below, measured.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {NAME}">
{body_rows}
  <g fill="{FACE_FILL}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: '{SIZE}', smile: '{SMILE}', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in [KEY, *RAMP[::-1], FACE_FILL])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'Corners lifted out of the same circle Hozz is drawn from, so the siblings rhyme; the tail takes over the corner and the deepest tones to stay a bubble. Eleven tones on one scalar field.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
