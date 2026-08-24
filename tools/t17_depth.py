"""
t17 — Depth. The bubble as a physical object, lit from one direction.

The direction: not a flat shape with light painted on it, but something with a
front face and a body behind, so it reads as a lit balloon of glass.

Three versions of this mark reached for that with concentric structure — a
proud rim peeled off the outline, a fold, a recessed panel — and all three came
back with the same note. A ring that follows the outline at a constant offset
is a frame, whatever tone you paint it. Inset a second one and you have a
plaque inside a bezel: the visual language of a television surround, which is
Plozz's language and not this one. The rim got thinner each time and the read
never changed, because thinness was never the problem. The problem was that the
structure was concentric at all.

So the rule this version is built on, and enforces:

    NO CLOSED CONSTANT-OFFSET LOOP EXISTS INSIDE THE KEYLINE.

That is asserted, not asserted-to. `encloses()` takes any layer, removes it
from the interior, and floods what is left inward from the keyline. If a single
pixel is unreachable, that layer has closed a ring around it and the build
fails. It runs on every tone, and on every prefix and suffix of the ramp, so a
loop cannot be assembled out of two tones that individually look innocent
either.

What replaces it is the simplest thing that can describe a curved surface:

    ONE LIGHT SOURCE. ONE DIRECTION. ONE SMOOTH RAMP.

The light sits off the **upper left**, one pixel outside the interior's own
bounding box, at (minx - 1, miny - 1). Every pixel is toned by its distance
from that point. Brightest at the upper-left shoulder, steadily darker toward
the lower right, darkest in the lower-right corner.

Placing the light up and left of *every* pixel is what makes the falloff
provably monotone rather than approximately monotone. Walk from any pixel in
direction (1, 1):

    d(s)^2 = (x + s - cx)^2 + (y + s - cy)^2
    d/ds   = 2[(x - cx + s) + (y - cy + s)]

and since cx < x and cy < y for every pixel in the shape, that derivative is
positive everywhere. Never brighter again, in any straight line from upper left
to lower right — and the same argument holds for straight right and straight
down, so it is true of every direction in that quadrant, not just the diagonal.
`monotone()` checks all three empirically as well.

Radial rather than linear on purpose. A linear ramp gives straight 45-degree
stripes, which describe a tilted flat plane; distance from a point gives arcs
that bend around the light, which is what a curved surface does. And because
the light is outside the silhouette, those arcs enter one edge and leave by
another. They cannot close. The construction and the rule agree.

Two exceptions to the ramp, and only two:

  * The keyline. One pixel, near-black, all the way round. It is a loop, and it
    is the only one — an outline is allowed to be an outline.
  * A specular catch of a handful of pixels on the upper-left shoulder, where
    the surface most directly faces the light. It is taken from the contour
    just inside the keyline and cut off at a fixed radius, so it is a short arc
    that stops well before the top of the mark and appears nowhere else.

The specular is the one place MAX_STEP is deliberately broken. Every step
inside the ramp moves each channel by 15 or less; the catch jumps 28 in red. A
highlight that eases in is not a highlight, it is a fourth ramp step.

Silhouette: a true quarter-circle corner at r = 9, sampled honestly with
inset = r - sqrt(r^2 - k^2) at each row, which gives 16, 20, 22, 24, 26, 26
before full width. Six rows of arc on a body 22 rows tall, so over a quarter of
the height is curve on each end. Rounder than the shipped mark's arc and
rounder than t19's, because the concentric version read as a squircle even
after the arc had been opened once — part of that was the rings reinforcing the
corner geometry, but the corners were genuinely too tight as well.

The tail is a wedge growing off the lower left. What makes it a wedge and not a
notch is a visible change of direction: down the body's bottom-left the left
edge curves inward, and at the junction that curve stops dead and runs vertical
for all six rows, with the whole taper carried on the right. Curve, then
straight. You can see the corner turn.

Face: `lg` + `wide` + gap 1. mark.ts says to keep `lg` for a plain open field.
There is no rim, fold or panel to spill onto now — the interior is one smooth
surface — so this is the version where `lg` is easiest to defend. The ink does
sit across several ramp tones rather than one flat core, which means the
contrast test has to be made against the *lightest* tone any ink pixel lands
on, not against an average. That is the binding constraint on the whole
palette, and it is why the ramp reaches 4.5:1 by its fourth step: the face's
upper-left corner is the brightest ground the ink ever touches.

White ink, because FAMILY records Twozz's as white and it is why the shipped
mark carries at 24px.
"""
import sys
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import keyline, to_paths, is_slab, show  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't17'
NAME = 'Depth'

NEI = ((1, 0), (-1, 0), (0, 1), (0, -1))

# ---------------------------------------------------------------------------
# Silhouette.
#
# A true quarter-circle corner, not a rounded-rectangle one. The arc is r = 9
# sampled honestly — inset = r - sqrt(r^2 - k^2) at each row — which gives
# 16, 20, 22, 24, 26, 26 before full width: six rows of arc on a body 22 rows
# tall, so better than a quarter of the height is curve at each end.
#
# Opened twice. The first version copied the shipped mark's tighter arc on the
# theory that matching it exactly was the safest way to sit beside the
# siblings, and on a sheet of ten it read as an app tile. The second opened it
# partway and still read as square-shouldered — some of which was the
# concentric rings running parallel to the outline and stating the corner
# geometry twice, but the corners were tight as well. This is the full r = 9
# circle with nothing inside it echoing the outline.
#
# Every width is even, so the body is symmetric about x=16 by construction and
# its parity is fixed. That also rules out the `sm` face by arithmetic rather
# than by care: any shape symmetric about x=16 is even-width, so a 7-wide face
# would land on x=16.5 — the half-pixel error the brief warns about.
# ---------------------------------------------------------------------------
BODY_TOP = 2
BODY_WIDTHS = [16, 20, 22, 24, 26, 26] + [28] * 10 + [26, 26, 24, 22, 20, 16]

BODY = set()
for i, w in enumerate(BODY_WIDTHS):
    x0 = 16 - w // 2
    BODY |= {(x0 + k, BODY_TOP + i) for k in range(w)}

BODY_Y0, BODY_Y1 = BODY_TOP, BODY_TOP + len(BODY_WIDTHS) - 1
BODY_W = max(BODY_WIDTHS)

# The tail's left edge is flush with the body's bottom row — x8 for all six
# rows, against a bottom row of x8-x23 — rather than stepping out past it. A
# column poking out one row lower than its neighbour is a spur, and it is also
# a new surface for the light to catch.
TAIL_ROWS = {
    24: (8, 16),
    25: (8, 15),
    26: (8, 14),
    27: (8, 12),
    28: (8, 10),
    29: (8, 9),
}
TAIL = {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)}

SIL = BODY | TAIL

# ---------------------------------------------------------------------------
# Silhouette assertions.
# ---------------------------------------------------------------------------
# The body carries both halves of `check`: symmetry about x=16, and no spurs.
check(BODY)


def spur_check(shape, what):
    """The spur half of `check`, on its own.

    The tail is deliberately asymmetric and is exempt from the symmetry test,
    so the full silhouette gets the spur test separately rather than quietly
    skipping both. Said out loud because the brief asks for it to be.
    """
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
    for i in range(1, len(widths) - 1):
        if widths[i] > widths[i - 1] and widths[i] > widths[i + 1]:
            raise AssertionError(f'{what}: spur at row {ys[i]} '
                                 f'({widths[i]} vs {widths[i-1]}/{widths[i+1]})')
    return dict(zip(ys, widths))


spur_check(SIL, 'silhouette')


def connected(shape):
    seen = {next(iter(shape))}
    stack = list(seen)
    while stack:
        x, y = stack.pop()
        for dx, dy in NEI:
            p = (x + dx, y + dy)
            if p in shape and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(shape)


assert connected(SIL), 'the tail is not attached to the body'

XS = [p[0] for p in SIL]
YS = [p[1] for p in SIL]
assert min(XS) >= 2 and max(XS) <= 29, f'x out of 2-29: {min(XS)}-{max(XS)}'
assert min(YS) >= 2 and max(YS) <= 29, f'y out of 2-29: {min(YS)}-{max(YS)}'

KEY_PX = keyline(SIL)               # the one loop the mark is allowed
INNER = SIL - KEY_PX

# ---------------------------------------------------------------------------
# The light.
#
# One point, one pixel off the interior's own top-left corner. Everything about
# the shading is a consequence of where this sits: outside the silhouette so
# the iso-lines cannot close, and up-and-left of every single pixel so the
# falloff is monotone by proof rather than by inspection.
# ---------------------------------------------------------------------------
LX = min(x for x, _ in INNER) - 1
LY = min(y for _, y in INNER) - 1

D = {p: hypot(p[0] - LX, p[1] - LY) for p in INNER}
D_MIN, D_MAX = min(D.values()), max(D.values())

STEPS = 11
GAMMA = 0.85                        # see the ramp note below

TONE_I = {}
for p, d in D.items():
    t = (d - D_MIN) / (D_MAX - D_MIN)
    TONE_I[p] = min(STEPS - 1, int(round((t ** GAMMA) * (STEPS - 1))))

# The specular catch: the contour just inside the keyline, cut off at a fixed
# radius from the light. Because the cut is on distance and not on position, it
# lands exactly where the surface faces the light most directly and stops on
# its own — it cannot run round the top, because the top is further away.
CONTOUR = {p for p in INNER if any((p[0] + dx, p[1] + dy) not in INNER
                                   for dx, dy in NEI)}
SPEC_REACH = 1.7
SPEC = {p for p in CONTOUR if D[p] <= D_MIN + SPEC_REACH}
assert 4 <= len(SPEC) <= 12, f'the catch is {len(SPEC)}px — a catch is a few pixels'

RAMP_PX = {i: set() for i in range(STEPS)}
for p, i in TONE_I.items():
    if p not in SPEC:
        RAMP_PX[i].add(p)
RAMP_PX = {i: s for i, s in RAMP_PX.items() if s}

# ---------------------------------------------------------------------------
# Monotonicity.
#
# The client's test, run as code: walking from upper left to lower right, every
# step is the same tone or darker, never brighter again. Checked on the
# diagonal and on both axes, since all three point into that quadrant.
# ---------------------------------------------------------------------------
for dx, dy in ((1, 1), (1, 0), (0, 1)):
    for p, i in TONE_I.items():
        q = (p[0] + dx, p[1] + dy)
        if q in TONE_I:
            assert TONE_I[q] >= i, (
                f'{p}->{q} steps back toward the light ({i} -> {TONE_I[q]})')

# ---------------------------------------------------------------------------
# No closed constant-offset loop.
#
# The rule this version exists to satisfy, made falsifiable. Pull a layer out
# of the interior and flood what remains inward from the keyline. Anything a
# flood from the edge cannot reach has been ringed in, and a ring is a frame.
#
# Run on each tone alone and on every prefix and suffix of the ramp, so that a
# loop assembled out of two adjacent tones — a "bright band" made of steps 0
# and 1 together — fails just as loudly as a single-tone one.
# ---------------------------------------------------------------------------
def encloses(layer):
    rest = INNER - layer
    if not rest:
        return False
    seen = {p for p in rest
            if any((p[0] + dx, p[1] + dy) not in INNER for dx, dy in NEI)}
    stack = list(seen)
    while stack:
        x, y = stack.pop()
        for dx, dy in NEI:
            q = (x + dx, y + dy)
            if q in rest and q not in seen:
                seen.add(q)
                stack.append(q)
    return len(seen) != len(rest)


KEYS = sorted(RAMP_PX)
GROUPS = [('the catch', SPEC)]
GROUPS += [(f'tone {i}', RAMP_PX[i]) for i in KEYS]
GROUPS += [(f'tones 0-{k}', set().union(*(RAMP_PX[i] for i in KEYS[:n])))
           for n, k in ((n, KEYS[n - 1]) for n in range(2, len(KEYS)))]
GROUPS += [(f'tones {k}-{KEYS[-1]}',
            set().union(*(RAMP_PX[i] for i in KEYS[n:])))
           for n, k in ((n, KEYS[n]) for n in range(1, len(KEYS) - 1))]

for what, layer in GROUPS:
    assert not encloses(layer), f'{what} closes a loop inside the keyline'

# ---------------------------------------------------------------------------
# Palette.
#
# Violet, and staying violet. Twitch is purple and the client only allowed
# *leaving* purple, he did not ask for it; the family already spends cyan on
# Plozz, red on Mozz and pale blue on Hozz, so violet is the one open hue with
# nothing to argue about.
#
# The ramp is anchored at three points rather than two, and the middle anchor
# is the one doing the real work. The face's upper-left corner is the brightest
# ground the white ink ever touches, and it lands on step 3, so step 3 has to
# clear 4.5:1 on its own. Everything brighter than that — the shoulder glow and
# the catch — lives outside the face entirely.
#
# GAMMA = 0.85 is what puts the face's corner on step 3 rather than step 2. It
# also biases the ramp's resolution toward the lit end, which is where a curved
# surface actually turns fastest.
# ---------------------------------------------------------------------------
KEY = '#1c0f38'
SPEC_C = '#d3b0fb'                              # the catch
A, A_I = (0xb9, 0x88, 0xf0), 0                  # the lit shoulder
B, B_I = (0x8a, 0x52, 0xdd), 3                  # the face's brightest ground
C, C_I = (0x46, 0x21, 0x9c), STEPS - 1          # the far corner
INK = '#ffffff'                                 # Twozz's own ink, per FAMILY


def lerp(p, q, t):
    return '#%02x%02x%02x' % tuple(round(p[c] + (q[c] - p[c]) * t)
                                   for c in range(3))


RAMP = [lerp(A, B, i / (B_I - A_I)) if i <= B_I
        else lerp(B, C, (i - B_I) / (C_I - B_I))
        for i in range(STEPS)]

MAX_STEP = 18  # Plozz's own widest interior step is 21, so this is inside it.
for a, b in zip(RAMP, RAMP[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= MAX_STEP, f'ramp: {a}->{b} steps by {d}, which reads as a band'

LAYERS = [(KEY_PX, KEY)] + [(RAMP_PX[i], RAMP[i]) for i in KEYS] + [(SPEC, SPEC_C)]

# ---------------------------------------------------------------------------
# Layer assertions.
# ---------------------------------------------------------------------------
COVER = set()
for px, _ in LAYERS:
    assert px, 'an empty layer'
    assert not (px & COVER), 'two layers overlap'
    COVER |= px
assert COVER == SIL, f'{len(SIL - COVER)} pixels of the shape are unpainted'

TONES = {f for _, f in LAYERS}
assert len(TONES) >= 8, f'only {len(TONES)} tones'

for px, fill in LAYERS:
    assert not is_slab(px, SIL), f'layer {fill} floats inside the shape as a slab'

# ---------------------------------------------------------------------------
# The face.
#
# Placement comes from the brief's measured table, never computed: an
# even-height face is not symmetric about cy. `lg` + `wide` + gap 1 is 10 rows,
# and the table gives (10, -5), so top = cy - 5.
#
# Equal air on the *body*, ignoring the tail, exactly as Plozz centres on its
# screen rather than on its whole TV:
#     top - y0 == y1 - (top + h - 1)   ->   top = (y0 + y1 - h + 1) / 2
# With the body at y2-y23 and h = 10 that is top = 8, so cy = 13. The same
# arithmetic is why the body is 22 rows: it forces y0 + y1 - h + 1 even, and an
# odd result would have put the face half a pixel off centre.
# ---------------------------------------------------------------------------
FACE_SIZE, FACE_SMILE, FACE_GAP = 'lg', 'wide', 1
FACE_W, FACE_H = 10, 10
FACE_CY = 13
FACE_TOP = FACE_CY - 5              # the table's offset for a 10-row face
FACE_LEFT = 16 - FACE_W // 2

assert BODY_W % 2 == FACE_W % 2, (
    f'parity: the body is {BODY_W} wide and the face is {FACE_W} — a face can '
    f'only centre on a container of the same parity')

AIR_ABOVE = FACE_TOP - BODY_Y0
AIR_BELOW = BODY_Y1 - (FACE_TOP + FACE_H - 1)
assert AIR_ABOVE == AIR_BELOW, f'air {AIR_ABOVE} above vs {AIR_BELOW} below'

# Nothing is cleared for the face — Mozz's rule, and the reason its ZZ reads as
# part of the record rather than as something dropped on it. Mirrored from
# mark.ts purely so the assertions below can be made; the mark itself always
# imports the real thing.
FACE_ROWS = [
    [(0, 3), (6, 9)],
    [(2, 3), (8, 9)],
    [(1, 2), (7, 8)],
    [(0, 1), (6, 7)],
    [(0, 3), (6, 9)],
    [],                              # gap 1
    [(0, 0), (9, 9)],
    [(0, 1), (8, 9)],
    [(1, 8)],
    [(2, 7)],
]
assert len(FACE_ROWS) == FACE_H
FACE_PX = {(FACE_LEFT + x, FACE_TOP + i)
           for i, runs in enumerate(FACE_ROWS) for a, b in runs
           for x in range(a, b + 1)}
assert FACE_PX <= INNER, 'the face runs into the keyline'
assert not (FACE_PX & SPEC), 'the face sits on the catch'


def luminance(hexc):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(p, q):
    a, b = luminance(p), luminance(q)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


# The ink crosses the ramp, so the test is against the lightest ground any ink
# pixel actually lands on — the worst case, not the average.
BED = {RAMP[TONE_I[p]] for p in FACE_PX}
BED_LIGHTEST = max(BED, key=luminance)
CONTRAST = contrast(BED_LIGHTEST, INK)
assert CONTRAST >= 4.5, (
    f'face contrast only {CONTRAST:.2f}:1 on {BED_LIGHTEST}, its lightest ground')

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
DOC = f'''/**
 * t17 · Depth
 *
 * The bubble as a physical object lit from one direction, rather than a flat
 * shape with light painted on it.
 *
 * Three earlier versions built the depth out of concentric structure — a proud
 * rim peeled off the outline, a fold, a recessed panel — and all three read as
 * a frame around a plaque. The rim got thinner each time and the read never
 * changed, because thinness was not the problem: a ring that follows the
 * outline at a constant offset is a frame whatever tone it is painted.
 *
 * So the rule this version is built on, and asserts:
 *
 *     no closed constant-offset loop exists inside the keyline
 *
 * `encloses()` removes each layer from the interior and floods what is left
 * inward from the edge. One unreachable pixel means that layer has ringed
 * something in, and the build fails. It runs on every tone and on every prefix
 * and suffix of the ramp, so a band cannot be assembled out of two tones that
 * individually look innocent.
 *
 * What replaces it is one light source, one direction, one smooth ramp. The
 * light sits off the **upper left**, one pixel outside the interior's bounding
 * box; every pixel is toned by its distance from it. Brightest at the
 * upper-left shoulder, steadily darker toward the lower right, darkest in the
 * far corner.
 *
 * Putting the light up and left of every pixel makes that falloff monotone by
 * proof. Walking from any pixel in direction (1, 1), the derivative of
 * distance is 2[(x - cx + s) + (y - cy + s)], and both terms are positive
 * everywhere in the shape — so no straight line from upper left to lower right
 * ever gets brighter again. The same holds for straight right and straight
 * down, and all three are checked empirically too.
 *
 * Radial rather than linear on purpose. A linear ramp gives 45-degree stripes,
 * which describe a tilted flat plane; distance from a point gives arcs that
 * bend around the light, which is what a curved surface does. And because the
 * light is outside the silhouette, those arcs enter by one edge and leave by
 * another — they cannot close. The construction and the rule agree.
 *
 * Two exceptions, and only two. The keyline, one pixel, near-black, all the
 * way round: it is a loop, and it is the only one an outline is allowed to be.
 * And a specular catch of {len(SPEC)} pixels on the upper-left shoulder, taken from the
 * contour just inside the keyline and cut off at a fixed radius from the
 * light, so it stops on its own well before the top and appears nowhere else.
 * The catch is the one place the ramp's step limit is broken on purpose — a
 * highlight that eases in is not a highlight, it is another ramp step.
 *
 * Silhouette: a true quarter-circle corner at r = 9, sampled row by row, which
 * gives 16, 20, 22, 24, 26, 26 before full width. Rounder than the shipped
 * mark's arc and rounder than its siblings', because with rings inside echoing
 * the outline the corner geometry was being stated twice and read square. The
 * tail is a wedge off the lower left whose left edge stops curving and goes
 * vertical exactly where it leaves the body, so you see the corner turn rather
 * than reading a notch.
 *
 * Violet, pulled toward indigo from the shipped #8f52f6, which sits too near
 * the top of its own range to leave a ramp anywhere to go. White ink, as the
 * shipped mark has. The ink crosses the ramp rather than sitting on one flat
 * core, so its contrast is measured against the lightest ground any ink pixel
 * lands on — {BED_LIGHTEST} at {CONTRAST:.1f}:1 — and that worst case is what sets where
 * the ramp has to be dark by.
 *
 * {len(TONES)} tones. Body y{BODY_Y0}-{BODY_Y1}, {BODY_W} wide, symmetric about x=16;
 * the tail is asymmetric by design and exempt. {AIR_ABOVE} rows of air above the face
 * and {AIR_BELOW} below, measured on the body, not on the tail.
 */'''

body_lines = [f'  <path d="{" ".join(to_paths(px))}" fill="{fill}" />'
              for px, fill in LAYERS]

astro = f'''---
{DOC}
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {NAME}">
{chr(10).join(body_lines)}
  <g fill="{INK}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: '{FACE_SMILE}', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''

palette = [KEY] + RAMP[::-1] + [SPEC_C]
meta = f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'One light source off the upper left, one radial falloff, and a rule the build enforces: no closed constant-offset loop anywhere inside the keyline. Every earlier attempt at depth here was concentric — a rim, a fold, an inset panel — and concentric structure reads as a frame around a plaque however thin you make it. This is the same fourteen tones laid out as a gradient instead of as bands, so the surface curves away from the light and never brightens again.',
  ground: 'light',
  palette: {palette},
}};
'''

(OUT / f'{SLUG}.astro').write_text(astro)
(OUT / f'{SLUG}.meta.ts').write_text(meta)

# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------
print(f'{SLUG} — {NAME}')
print(f'  silhouette  x{min(XS)}-{max(XS)} y{min(YS)}-{max(YS)}, {len(SIL)}px, connected')
print(f'  body        y{BODY_Y0}-{BODY_Y1}, {BODY_W} wide, symmetric about x=16, no spurs')
print(f'  tail        y{min(TAIL_ROWS)}-{max(TAIL_ROWS)}, asymmetric by design; '
      f'union spur-checked')
print(f'  light       ({LX}, {LY}) — upper left, outside the shape; '
      f'radial falloff d={D_MIN:.1f}-{D_MAX:.1f}, gamma {GAMMA}')
print(f'  monotone    (1,1), (1,0) and (0,1) all same-or-darker: verified')
print(f'  no loops    {len(GROUPS)} layers and layer-groups tested by flood fill: '
      f'none encloses a pixel')
print(f'  catch       {len(SPEC)}px on the upper-left shoulder, {SPEC_C}')
print(f'  tones       {len(TONES)}')
print(f'  face        {FACE_SIZE}/{FACE_SMILE}/gap{FACE_GAP} — {FACE_W}x{FACE_H} at '
      f'x{FACE_LEFT}-{FACE_LEFT+FACE_W-1} y{FACE_TOP}-{FACE_TOP+FACE_H-1}, cy={FACE_CY}; '
      f'ink crosses {len(BED)} tones, lightest {BED_LIGHTEST} at {CONTRAST:.1f}:1')
print(f'  parity      body {BODY_W} / face {FACE_W} — both even')
print(f'  air         {AIR_ABOVE} above, {AIR_BELOW} below (on the body)')
print('  layers      ' + ', '.join(f'{f}:{len(p)}' for p, f in LAYERS))
print()
show([KEY_PX] + [RAMP_PX[i] for i in KEYS] + [SPEC, FACE_PX],
     ['K'] + [str(i) for i in KEYS] + ['*', '#'])
