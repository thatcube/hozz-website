"""
t17 — Depth. The bubble as a physical object with thickness.

The direction: not a flat shape with light painted on it, but something with a
front face, an edge, and a body behind. Plozz already does this and it is worth
saying exactly how, because the raster is unambiguous:

      6 .....0000000000000000000000.....   keyline
      7 ....066666666666666666666660....   case, LIT along the top
      8 ...06222222222222222222222260...   case, mid
      9 ..0622200000000000000000022260..   case + the bezel starting
     10 ..0622033333333333333333302260..   screen: lightest ring
     ...
     28 ....055555555555555555555550....   case, SHADED along the bottom

Three planes. A case whose top edge is lighter than its face and whose bottom
edge is darker — that is the thickness. A hard dark fold where the case turns
inward. Then a recessed panel behind it. The solidity is not in any one tone;
it is in the fact that the tones *change direction* when the plane changes.

So this mark is built as one object with a rim and a window in it:

    keyline  ->  rim (2px)  ->  fold  ->  recessed panel  ->  face

and the whole argument rests on one inversion:

  * The **rim is proud**, so it is lit on top and shaded underneath.
  * The **panel is recessed**, so it is *shaded* at the top — the near wall
    casts down onto the floor — and *lit* at the bottom, where the light that
    got past the near wall actually lands.

Follow the mark down its vertical centre and the tone goes light, mid, dark
(fold), dark, ..., light, dark (fold), dark, keyline. It reverses twice. That
reversal is what says one plane is in front of the other, and it is the one
thing a drop shadow cannot imitate — a shadow only ever gets darker in one
direction, and it lives outside the silhouette. Every pixel here is inside it.

It is also what keeps this off the 2005 bevel. A bevel filter runs light
top-left to dark bottom-right across *everything*, uniformly. Here the two
planes disagree, on purpose, and the lighting is pure top-down rather than
diagonal, which is what a rounded rim actually does under a ceiling light.

Subtlety is enforced, not hoped for: no step inside either ramp moves any
channel by more than 18, which is inside what the shipped Plozz mark already
spends (#97e3fe -> #82deff -> #72daff steps by 21). The only large jumps are
the two structural lines — the keyline and the fold — and Plozz draws its fold
in pure black, so a deep violet is the quieter choice.

The tail is the same object, so it gets the same rim and the same underside
shade — and, being narrow, it never reaches panel depth. It stays solid wall.
That is not a compromise: a bubble whose body has a window in it and whose tail
is solid is a bubble made of a material, which is the entire point.

Face: `md` + `wide` + gap 1. Eight rows, eight wide. `md` because mark.ts says
plainly to use it on a busy container and this container has a rim, a fold and
a graded panel in it; `wide` because the wide smile is Twozz's own signature
against Plozz's compact one; gap 1 because that is what buys the eighth row
back, and the eighth row is what makes the air come out equal.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import rings, edge, keyline, to_paths, is_slab, show  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't17'
NAME = 'Depth'

# ---------------------------------------------------------------------------
# Silhouette.
#
# The body is a rounded rectangle rather than the shipped mark's slightly
# squarer one — the brief allows "more round or cohesive" and a rounder corner
# gives the rim something to curve around, which is where a rim earns its keep.
# Widths are top to bottom; every one is even, so the body is symmetric about
# x=16 by construction and its width has the parity an 8- or 10-wide face
# needs. (A 7-wide `sm` face can never sit on a shape symmetric about x=16:
# every such shape is even-width, so `sm` would land on x=16.5. That is the
# half-pixel error the brief warns about, and it is ruled out here by
# arithmetic rather than by care.)
# ---------------------------------------------------------------------------
BODY_TOP = 2
BODY_WIDTHS = [12, 18, 20, 22, 24, 24] + [26] * 10 + [24, 24, 22, 20, 18, 12]

BODY = set()
for i, w in enumerate(BODY_WIDTHS):
    x0 = 16 - w // 2
    BODY |= {(x0 + k, BODY_TOP + i) for k in range(w)}

BODY_Y0, BODY_Y1 = BODY_TOP, BODY_TOP + len(BODY_WIDTHS) - 1

# The tail: a tapering wedge off the bottom-left corner, in the shipped mark's
# own idiom (a near-vertical left edge, the taper carried on the right). Fat
# enough at the base that the rim can wrap it, pointed enough at the tip that
# it still reads as a tail and not as a foot.
TAIL_ROWS = {
    24: (9, 15),
    25: (8, 14),
    26: (7, 13),
    27: (7, 12),
    28: (6, 10),
    29: (6, 8),
}
TAIL = {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)}

SIL = BODY | TAIL

# ---------------------------------------------------------------------------
# Silhouette assertions.
# ---------------------------------------------------------------------------
# The body carries both tests: symmetry about x=16 and no spurs.
BODY_WIDTHS_CHECKED = check(BODY)

# The tail is deliberately asymmetric and is exempt from the symmetry half, so
# the full silhouette gets the spur half on its own. Stated plainly rather than
# quietly skipped.
def spur_check(shape, what):
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


SIL_WIDTHS = spur_check(SIL, 'silhouette')

# The silhouette must be one connected object, or the tail is glued on.
def connected(shape):
    seen = {next(iter(shape))}
    stack = list(seen)
    while stack:
        x, y = stack.pop()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + d[0], y + d[1])
            if p in shape and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(shape)


assert connected(SIL), 'tail is not attached to the body'

xs = [p[0] for p in SIL]
ys = [p[1] for p in SIL]
assert min(xs) >= 2 and max(xs) <= 29, f'x out of 2-29: {min(xs)}-{max(xs)}'
assert min(ys) >= 2 and max(ys) <= 29, f'y out of 2-29: {min(ys)}-{max(ys)}'

# ---------------------------------------------------------------------------
# The three planes.
#
# Every layer below comes out of `rings` or `edge`, so each one follows the
# object's own contour. None of them could come out a rectangle.
# ---------------------------------------------------------------------------
KEY_PX = keyline(SIL)               # one continuous outline around the whole object
INNER = SIL - KEY_PX
TAIL_IN = TAIL - KEY_PX

# Rim, fold and panel are peeled off the **body on its own**, never off the
# union. Peel them off the union and the body's bottom edge simply stops where
# the tail meets it — the panel then bulges down into the junction and the
# recess is no longer symmetric, which was visible on the first render. Taking
# the rings from the body means the fold closes as a loop and the floor stays
# square with the face.
BANDS, PANEL = rings(BODY, 4)
FOLD = BANDS[3]                     # where the front face turns inward

# BANDS[0] is the body's own outline. Most of it coincides with the object's
# outline and is keyline; the few pixels that do not are exactly the tail
# junction, and there the wall must simply carry on into the tail rather than
# have a dark line drawn across it.
RIM = (BANDS[0] - KEY_PX) | BANDS[1] | BANDS[2]   # 2px, the thickness you see

CASING = RIM | TAIL_IN              # everything made of wall

# One lighting rule for the whole object: surfaces that face up are lit,
# surfaces that face down are shaded, the sides stay mid. Taken from the union,
# so the tail's top is *not* lit — it is continuous with the body, not a
# separate thing with its own top.
LIT_CONTOUR = edge(INNER, 0, -1, 1)
SHAD_CONTOUR = edge(INNER, 0, 1, 1) - LIT_CONTOUR

W_LIT = CASING & LIT_CONTOUR
W_SHAD = CASING & SHAD_CONTOUR
W_MID = CASING - W_LIT - W_SHAD

# The panel is behind the rim, so its lighting runs the other way: the near
# wall shades the top of the floor, and the light that clears it pools at the
# bottom. Two steps of shadow, one of pool, and a plain field for the face.
P_POOL = edge(PANEL, 0, 1, 1)
P_SH2 = edge(PANEL, 0, -1, 1) - P_POOL
P_SH1 = edge(PANEL, 0, -1, 2) - P_SH2 - P_POOL
P_FIELD = PANEL - P_POOL - P_SH2 - P_SH1

# ---------------------------------------------------------------------------
# Palette.
#
# Violet, and staying violet. Twitch is purple and the client only allowed
# leaving purple, he did not ask for it; the family already spends cyan on
# Plozz, red on Mozz and pale blue on Hozz, so violet is the one open hue that
# needs no argument. It is pushed a little toward indigo against the shipped
# #8f52f6 because a neon violet has nowhere to go — a ramp needs headroom above
# the body tone and #8f52f6 has almost none before it goes chalky.
#
# Two ramps, not one, because there are two planes:
#   wall  — deeper and more saturated. This is the material.
#   panel — lighter and softer. This is the surface the message sits on, and it
#           has to carry a dark face at 7:1.
# and two structural lines, keyline and fold, which are lines rather than ramp
# steps and are allowed to jump.
# ---------------------------------------------------------------------------
KEY = '#261347'
FOLD_C = '#4d2a86'
WALL = ['#8f64e6', '#7f54d6', '#6f45c4']              # lit, mid, shaded
PANEL_RAMP = ['#9b7ee0', '#a78ce7', '#b39aed', '#bfa8f3']  # shadow2, shadow1, field, pool

MAX_STEP = 18  # Plozz's own widest interior step is 21, so this is inside it.
for ramp, what in ((WALL, 'wall'), (PANEL_RAMP, 'panel')):
    for a, b in zip(ramp, ramp[1:]):
        d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
        assert d <= MAX_STEP, f'{what}: {a}->{b} steps by {d}, which reads as a band'

LAYERS = [
    (KEY_PX, KEY),
    (W_LIT, WALL[0]),
    (W_MID, WALL[1]),
    (W_SHAD, WALL[2]),
    (FOLD, FOLD_C),
    (P_SH2, PANEL_RAMP[0]),
    (P_SH1, PANEL_RAMP[1]),
    (P_FIELD, PANEL_RAMP[2]),
    (P_POOL, PANEL_RAMP[3]),
]

# ---------------------------------------------------------------------------
# Layer assertions.
# ---------------------------------------------------------------------------
seen = set()
for px, fill in LAYERS:
    assert px, f'empty layer {fill}'
    assert not (px & seen), f'layer {fill} overlaps an earlier one'
    seen |= px
assert seen == SIL, f'layers do not tile the silhouette ({len(seen)} vs {len(SIL)})'

TONES = {f for _, f in LAYERS}
assert len(TONES) >= 8, f'only {len(TONES)} tones'

for px, fill in LAYERS:
    assert not is_slab(px, SIL), f'layer {fill} is a slab floating inside the shape'

# ---------------------------------------------------------------------------
# The face.
#
# Placement is taken from the brief's measured table, never computed: an
# even-height face is not symmetric about cy. md at gap 1 with the wide smile
# is 8 rows, and the table gives (8, -4) — top = cy - 4.
#
# Equal air on the *body*, ignoring the tail, exactly as Plozz centres on its
# screen and not on its whole TV:
#     top - y0 == y1 - (top + h - 1)   ->   top = (y0 + y1 - h + 1) / 2
# With the body at y2-y23 and h=8 that is top = 9, so cy = 13.
# ---------------------------------------------------------------------------
FACE_SIZE, FACE_SMILE, FACE_GAP = 'md', 'wide', 1
FACE_W, FACE_H = 8, 8
FACE_CY = 13
FACE_TOP = FACE_CY - 4              # the table's offset for an 8-row face
FACE_LEFT = 16 - FACE_W // 2

BODY_W = max(BODY_WIDTHS)
assert BODY_W % 2 == FACE_W % 2, (
    f'parity: body is {BODY_W} wide, face is {FACE_W} — a face can only centre '
    f'on a container of the same parity')

air_above = FACE_TOP - BODY_Y0
air_below = BODY_Y1 - (FACE_TOP + FACE_H - 1)
assert air_above == air_below, f'air {air_above} above vs {air_below} below'

# The face lands on the panel and nothing is cleared for it — Mozz's rule, and
# the reason its ZZ reads as part of the record rather than dropped on it.
FACE_ROWS = [
    [(0, 2), (5, 7)],
    [(1, 2), (6, 7)],
    [(0, 1), (5, 6)],
    [(0, 2), (5, 7)],
    [],                              # gap 1
    [(0, 0), (7, 7)],
    [(0, 1), (6, 7)],
    [(1, 6)],
]
assert len(FACE_ROWS) == FACE_H
FACE_PX = {(FACE_LEFT + x, FACE_TOP + i)
           for i, runs in enumerate(FACE_ROWS) for a, b in runs for x in range(a, b + 1)}
assert FACE_PX <= PANEL, 'face spills off the panel onto the rim'
assert FACE_PX <= P_FIELD, 'face sits on the panel shading rather than its plain field'

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
DOC = f'''/**
 * t17 · Depth
 *
 * The bubble as a physical object with thickness, rather than a flat shape
 * with light on it. Three planes, built the way the shipped Plozz mark builds
 * its case, bezel and screen:
 *
 *     keyline -> rim (2px) -> fold -> recessed panel -> face
 *
 * The whole thing turns on one inversion. The **rim is proud**, so it is
 * lighter along its top edge and darker underneath. The **panel is recessed**,
 * so it runs the other way — shaded at the top, where the near wall casts down
 * onto the floor, and lightest at the bottom, where the light that cleared
 * that wall actually lands. Read down the centre and the tone reverses twice.
 *
 * That reversal is the argument. A drop shadow only darkens in one direction
 * and lives outside the silhouette; every pixel here is inside it. A bevel
 * filter runs light top-left to dark bottom-right across everything at once;
 * here the two planes disagree on purpose, and the light is straight top-down
 * rather than diagonal, which is what a rounded rim under a ceiling light
 * actually does.
 *
 * Subtlety is enforced rather than hoped for: no step inside either ramp moves
 * any channel by more than 18, which is inside the 21 the shipped Plozz screen
 * already spends. The only large jumps are the two structural lines — keyline
 * and fold — and Plozz draws its fold in pure black, so a deep violet is the
 * quieter choice.
 *
 * The tail is the same object and takes the same rim and the same underside
 * shade. Being narrow it never reaches panel depth, so it stays solid wall: a
 * body with a window in it, a tail without one, both made of one material.
 *
 * Violet, pushed toward indigo from the shipped #8f52f6, which sits too near
 * the top of its own range to leave a ramp anywhere to go.
 *
 * {len(TONES)} tones. Body y{BODY_Y0}-{BODY_Y1}, symmetric about x=16, tail exempt.
 * Face md/wide/gap1 on the panel, {air_above} rows of air above it and
 * {air_below} below, measured on the body.
 */'''

body_lines = []
for px, fill in LAYERS:
    d = ' '.join(to_paths(px))
    body_lines.append(f'  <path d="{d}" fill="{fill}" />')

astro = f'''---
{DOC}
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {NAME}">
{chr(10).join(body_lines)}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: '{FACE_SMILE}', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''

palette = [KEY, FOLD_C] + WALL[::-1] + PANEL_RAMP
meta = f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'A rim with real thickness — lit on top, shaded underneath — folding into a panel lit the other way round, so the tone reverses where the plane does.',
  ground: 'light',
  palette: {str(palette).replace("'", chr(39))},
}};
'''

(OUT / f'{SLUG}.astro').write_text(astro)
(OUT / f'{SLUG}.meta.ts').write_text(meta)

# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------
print(f'{SLUG} — {NAME}')
print(f'  silhouette  x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}, {len(SIL)}px, connected')
print(f'  body        y{BODY_Y0}-{BODY_Y1}, {BODY_W} wide, symmetric about x=16, no spurs')
print(f'  tail        y{min(TAIL_ROWS)}-{max(TAIL_ROWS)}, asymmetric by design, no spurs on the union')
print(f'  tones       {len(TONES)}')
print(f'  face        {FACE_SIZE}/{FACE_SMILE}/gap{FACE_GAP} — {FACE_W}x{FACE_H} at '
      f'x{FACE_LEFT}-{FACE_LEFT+FACE_W-1} y{FACE_TOP}-{FACE_TOP+FACE_H-1}, cy={FACE_CY}')
print(f'  parity      body {BODY_W} / face {FACE_W} — both even')
print(f'  air         {air_above} above, {air_below} below (on the body)')
print(f'  layers      ' + ', '.join(f'{f}:{len(p)}' for p, f in LAYERS))
print()
show([p for p, _ in LAYERS] + [FACE_PX],
     ['K', 'L', 'M', 'S', 'F', '2', '1', '.', 'P', '#'])
