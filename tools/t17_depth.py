"""
t17 — Depth. The bubble as a physical object with thickness.

The direction: not a flat shape with light painted on it, but something with a
front face, an edge, and a body behind. Plozz already does this and the raster
says exactly how:

      6 .....0000000000000000000000.....   keyline
      7 ....066666666666666666666660....   case, LIT along its top edge
      8 ...06222222222222222222222260...   case, mid
      9 ..0622200000000000000000022260..   case, then the bezel closing
     10 ..0622033333333333333333302260..   screen: the bevel's lightest ring
     ...
     28 ....055555555555555555555550....   case, SHADED along its bottom edge

Three planes. A case whose top edge is lighter than its face and whose bottom
edge is darker — that is the thickness. A hard fold where the case turns
inward. A recessed panel behind it. The solidity is not in any single tone; it
is in the fact that the tones change *direction* when the plane changes.

So this is one object with a rim and a window in it:

    keyline -> rim (2px) -> fold -> recessed panel -> face

and everything rests on one inversion.

  * The **rim is proud**. Light from above lands on its top edge and misses its
    underside, so it runs light at the top, mid at the sides, dark at the
    bottom.
  * The **panel is recessed**, so it runs the other way. The near wall throws a
    shadow across the top of the floor; the light that clears that wall lands
    at the bottom. Dark at the top, lightest at the bottom.

Read down the middle and the tone reverses twice, at exactly the two rows where
the plane changes. That is the whole argument, and it is the one thing a drop
shadow cannot imitate: a shadow only darkens in one direction and it lives
*outside* the silhouette. Every pixel here is inside it. It is also what keeps
this off the 2005 bevel — a bevel filter runs light top-left to dark
bottom-right across everything at once, uniformly; here the two planes disagree
on purpose, and the light is straight top-down rather than diagonal, which is
what a rounded rim under a ceiling light actually does.

The panel's grading is carried by two contour rings rather than by horizontal
bands. The first attempt used bands and it failed: 1px stripes across a 14-row
floor were invisible at 96px, so the mark read as a flat shape with a thick
border. Rings are what Plozz uses, they wrap the corners, and grading each ring
by height means the same two rings deliver both reads at once — an inset bevel
you can still see at 24px, and a vertical gradient that tells you which way is
up.

Subtlety is enforced, not hoped for: no step within a ramp moves any channel by
more than 18, inside the 21 the shipped Plozz screen already spends. The only
large jumps are the two structural lines, keyline and fold, and Plozz draws its
fold in pure black — a deep violet is the quieter choice.

The tail is the same object and takes the same rim and the same underside
shade. Being narrow it never reaches panel depth, so it stays solid wall: a
body with a window in it and a tail without one, both made of one material. It
hangs almost vertically, with the taper carried on its right, because the first
version ran it out at 45 degrees and a 45-degree tail reads as an arrow.

Face: `md` + `wide` + gap 1. `md` because mark.ts says plainly to use it on a
busy container and this one has a rim, a fold and a graded floor in it; `wide`
because the wide smile is Twozz's own signature against Plozz's compact one;
gap 1 because that buys the eighth row back, and eight rows is what makes the
air come out equal on a 22-row body.
"""
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
# A rounded rectangle, rounder than the shipped mark's — the brief allows "more
# round or cohesive" and a longer corner arc gives the rim something to curve
# around, which is where a rim earns its keep. The top corners are rounder than
# the bottom ones on purpose: the bottom row is where the tail springs from,
# and a 12-wide bottom row (the first attempt) left the tail hanging off a
# point, which is what made it look like a spike rather than a tail.
#
# Every width is even, so the body is symmetric about x=16 by construction and
# its parity is fixed. That also rules out the `sm` face by arithmetic rather
# than by care: any shape symmetric about x=16 is even-width, so a 7-wide face
# would land on x=16.5 — the half-pixel error the brief warns about.
# ---------------------------------------------------------------------------
BODY_TOP = 2
BODY_WIDTHS = [12, 18, 20, 22, 24, 24] + [26] * 12 + [24, 22, 20, 16]

BODY = set()
for i, w in enumerate(BODY_WIDTHS):
    x0 = 16 - w // 2
    BODY |= {(x0 + k, BODY_TOP + i) for k in range(w)}

BODY_Y0, BODY_Y1 = BODY_TOP, BODY_TOP + len(BODY_WIDTHS) - 1
BODY_W = max(BODY_WIDTHS)

# The tail, in the shipped mark's own idiom: a near-vertical left edge with the
# taper carried on the right, hanging rather than pointing. Wide where it meets
# the body — half the bottom row — so it reads as part of the same object.
# The left edge holds at x8 for the whole drop, matching the body's bottom row
# rather than stepping out past it. A single column poking out one row lower
# than its neighbour is a new upward-facing surface, and the lighting rule
# correctly lights it — one stray pale pixel halfway down the tail.
TAIL_ROWS = {
    24: (8, 15),
    25: (8, 13),
    26: (8, 11),
    27: (8, 10),
    28: (8, 9),
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
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + d[0], y + d[1])
            if p in shape and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(shape)


assert connected(SIL), 'the tail is not attached to the body'

XS = [p[0] for p in SIL]
YS = [p[1] for p in SIL]
assert min(XS) >= 2 and max(XS) <= 29, f'x out of 2-29: {min(XS)}-{max(XS)}'
assert min(YS) >= 2 and max(YS) <= 29, f'y out of 2-29: {min(YS)}-{max(YS)}'

# ---------------------------------------------------------------------------
# The three planes.
#
# Every layer below comes out of `rings` or `edge`, so each one follows the
# object's own contour and none of them could come out a rectangle.
# ---------------------------------------------------------------------------
KEY_PX = keyline(SIL)               # one continuous outline around the whole object
INNER = SIL - KEY_PX
TAIL_IN = TAIL - KEY_PX

# Rim, fold and panel are peeled off the **body on its own**, never off the
# union. Peel them off the union and the body's bottom edge simply stops where
# the tail meets it: the panel then bulges down into the junction and the
# recess is no longer square with the face. That was visible on the first
# render. Taking the rings from the body means the fold closes as a loop.
BANDS, PANEL = rings(BODY, 4)
FOLD = BANDS[3]                     # where the front face turns inward

# BANDS[0] is the body's own outline. Almost all of it coincides with the
# object's outline and is keyline; the pixels that do not are exactly the tail
# junction, and there the wall must carry on into the tail rather than have a
# dark line ruled across it.
RIM = (BANDS[0] - KEY_PX) | BANDS[1] | BANDS[2]

CASING = RIM | TAIL_IN              # everything made of wall

# One lighting rule for the whole object: surfaces facing up are lit, surfaces
# facing down are shaded, the sides stay mid. Taken from the union, so the
# tail's top is *not* lit — it is continuous with the body, not a separate
# thing with a top of its own.
LIT_CONTOUR = edge(INNER, 0, -1, 1)
SHAD_CONTOUR = edge(INNER, 0, 1, 1) - LIT_CONTOUR

W_LIT = CASING & LIT_CONTOUR
W_SHAD = CASING & SHAD_CONTOUR
W_MID = CASING - W_LIT - W_SHAD

# ---------------------------------------------------------------------------
# The recess.
#
# Two contour rings and a core, the way Plozz builds its screen — but each ring
# graded by height, which is the part Plozz has no reason to do because a TV
# screen is emissive and a recess is not.
#
# One construction, two jobs. Across the top the stack runs
# darkest -> dark -> core: an inset bevel, and the near wall's shadow lying on
# the floor. Across the bottom it runs lightest -> light -> core: the same
# bevel, and the light that cleared the wall pooling where it lands. Down the
# sides the rings pass through the core's own tone and disappear, which is
# right — a floor lit from directly above gets nothing extra from walls it is
# edge-on to, and drawing something there is how a recess turns into an emboss.
#
# The face keeps a plain field, because the core is one tone.
# ---------------------------------------------------------------------------
P_RINGS, P_CORE = rings(PANEL, 2)
P_Y0 = min(y for _, y in PANEL)
P_Y1 = max(y for _, y in PANEL)

STEPS = 7
CORE_I = STEPS // 2                 # 3 of 0..6 — the middle of the ramp


def grade(px, lo, hi):
    """Bucket a layer's pixels by height, across ramp indices lo..hi."""
    out = {}
    for x, y in px:
        t = (y - P_Y0) / (P_Y1 - P_Y0)
        out.setdefault(round(lo + t * (hi - lo)), set()).add((x, y))
    return out


# Ring 0 sweeps the whole ramp; ring 1 sweeps the middle of it, so the two
# never cross and the stack always reads in one direction from outside in.
P_LAYERS = {}
for i, s in grade(P_RINGS[0], 0, STEPS - 1).items():
    P_LAYERS.setdefault(i, set()).update(s)
for i, s in grade(P_RINGS[1], 1, STEPS - 2).items():
    P_LAYERS.setdefault(i, set()).update(s)
P_LAYERS.setdefault(CORE_I, set()).update(P_CORE)

# ---------------------------------------------------------------------------
# Palette.
#
# Violet, and staying violet. Twitch is purple and the client only allowed
# *leaving* purple, he did not ask for it; the family already spends cyan on
# Plozz, red on Mozz and pale blue on Hozz, so violet is the one open hue that
# needs no argument at all. It is pulled toward indigo from the shipped
# #8f52f6 because a neon violet has nowhere to go — the client's own standard
# is "you barely notice it change colours, and yet they're completely different
# colours", which needs a *wide total range* crossed in *small steps*, and
# #8f52f6 sits too near the top of its own range to leave room for one.
#
# Two ramps, because there are two planes. The wall is deeper and more
# saturated: it is the material. The floor is lighter and travels further: it
# is the surface the message sits on, and it has to carry a dark face. Keyline
# and fold are lines rather than ramp steps, and are allowed to jump.
# ---------------------------------------------------------------------------
KEY = '#261347'
FOLD_C = '#452680'
WALL = ['#8358d4', '#7349c4', '#633bb2']        # lit, mid, shaded

FLOOR_LO, FLOOR_HI = (0x7a, 0x56, 0xbf), (0xc6, 0xa9, 0xf3)


def lerp(a, b, t):
    return round(a + (b - a) * t)


FLOOR = ['#%02x%02x%02x' % tuple(lerp(FLOOR_LO[c], FLOOR_HI[c], i / (STEPS - 1))
                                 for c in range(3))
         for i in range(STEPS)]

MAX_STEP = 18  # Plozz's own widest interior step is 21, so this is inside it.
for ramp, what in ((WALL, 'wall'), (FLOOR, 'floor')):
    for a, b in zip(ramp, ramp[1:]):
        d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
        assert d <= MAX_STEP, f'{what}: {a}->{b} steps by {d}, which reads as a band'

LAYERS = [
    (KEY_PX, KEY),
    (W_LIT, WALL[0]),
    (W_MID, WALL[1]),
    (W_SHAD, WALL[2]),
    (FOLD, FOLD_C),
] + [(P_LAYERS[i], FLOOR[i]) for i in sorted(P_LAYERS)]

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
    assert not is_slab(px, SIL), f'layer {fill} floats inside the shape as a slab'

# ---------------------------------------------------------------------------
# The face.
#
# Placement comes from the brief's measured table, never computed: an
# even-height face is not symmetric about cy. `md` + `wide` + gap 1 is 8 rows,
# and the table gives (8, -4), so top = cy - 4.
#
# Equal air on the *body*, ignoring the tail, exactly as Plozz centres on its
# screen rather than on its whole TV:
#     top - y0 == y1 - (top + h - 1)   ->   top = (y0 + y1 - h + 1) / 2
# With the body at y2-y23 and h = 8 that is top = 9, so cy = 13.
# ---------------------------------------------------------------------------
FACE_SIZE, FACE_SMILE, FACE_GAP = 'md', 'wide', 1
FACE_W, FACE_H = 8, 8
FACE_CY = 13
FACE_TOP = FACE_CY - 4              # the table's offset for an 8-row face
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
           for i, runs in enumerate(FACE_ROWS) for a, b in runs
           for x in range(a, b + 1)}
assert FACE_PX <= PANEL, 'the face spills off the panel onto the rim'
assert FACE_PX <= P_CORE, 'the face sits on the floor grading rather than its plain core'


def luminance(hexc):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


CONTRAST = (max(luminance(FLOOR[CORE_I]), luminance(KEY)) + 0.05) / \
           (min(luminance(FLOOR[CORE_I]), luminance(KEY)) + 0.05)
assert CONTRAST >= 4.5, f'face contrast only {CONTRAST:.2f}:1 on the core'

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
DOC = f'''/**
 * t17 · Depth
 *
 * The bubble as a physical object with thickness, rather than a flat shape
 * with light on it. Three planes, built the way the shipped Plozz mark builds
 * its case, its bezel and its screen:
 *
 *     keyline -> rim (2px) -> fold -> recessed panel -> face
 *
 * It turns on one inversion. The **rim is proud**, so light lands on its top
 * edge and misses its underside: light at the top, mid at the sides, dark
 * along the bottom. The **panel is recessed**, so it runs the other way — the
 * near wall throws a shadow across the top of the floor, and the light that
 * cleared that wall pools at the bottom. Read down the middle and the tone
 * reverses twice, at exactly the two rows where the plane changes.
 *
 * That reversal is the argument. A drop shadow only darkens in one direction
 * and lives outside the silhouette; every pixel here is inside it. A bevel
 * filter runs light top-left to dark bottom-right across everything at once;
 * here the two planes disagree on purpose, and the light is straight top-down
 * rather than diagonal, which is what a rounded rim under a ceiling light
 * actually does.
 *
 * The floor's grading is carried by two contour rings graded by height, not by
 * horizontal bands. Bands were tried first and were invisible at 96px, which
 * left the mark reading as a flat shape with a thick border. Rings wrap the
 * corners, and grading them by height makes the same two rings deliver an
 * inset bevel you can still see at 24px *and* a gradient that tells you which
 * way is up. Down the sides they pass through the core's own tone and vanish,
 * which is correct: a floor lit from directly above gets nothing from walls it
 * is edge-on to, and drawing something there is how a recess becomes an
 * emboss.
 *
 * No step inside either ramp moves any channel by more than 18, inside the 21
 * the shipped Plozz screen already spends. The only large jumps are the two
 * structural lines, keyline and fold — and Plozz draws its fold in pure black,
 * so a deep violet is the quieter choice.
 *
 * The tail is the same object, with the same rim and the same underside shade.
 * Being narrow it never reaches panel depth, so it stays solid wall: a body
 * with a window in it, a tail without one, one material.
 *
 * Violet, pulled toward indigo from the shipped #8f52f6, which sits too near
 * the top of its own range to leave a ramp anywhere to go.
 *
 * {len(TONES)} tones. Body y{BODY_Y0}-{BODY_Y1}, {BODY_W} wide, symmetric about x=16;
 * the tail is asymmetric by design and exempt. Face md/wide/gap1 on the plain
 * core at {CONTRAST:.1f}:1, with {AIR_ABOVE} rows of air above it and {AIR_BELOW} below,
 * measured on the body.
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
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: '{FACE_SIZE}', smile: '{FACE_SMILE}', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''

palette = [KEY, FOLD_C] + WALL[::-1] + FLOOR
meta = f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'A rim with real thickness — lit on top, shaded underneath — folding into a recessed floor lit the other way round, so the tone reverses exactly where the plane does.',
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
print(f'  panel       y{P_Y0}-{P_Y1}, 2 graded rings + plain core')
print(f'  tones       {len(TONES)}')
print(f'  face        {FACE_SIZE}/{FACE_SMILE}/gap{FACE_GAP} — {FACE_W}x{FACE_H} at '
      f'x{FACE_LEFT}-{FACE_LEFT+FACE_W-1} y{FACE_TOP}-{FACE_TOP+FACE_H-1}, '
      f'cy={FACE_CY}, {CONTRAST:.1f}:1 on the core')
print(f'  parity      body {BODY_W} / face {FACE_W} — both even')
print(f'  air         {AIR_ABOVE} above, {AIR_BELOW} below (on the body)')
print('  layers      ' + ', '.join(f'{f}:{len(p)}' for p, f in LAYERS))
print()
marks = ['K', 'L', 'M', 'S', 'F'] + [str(i) for i in sorted(P_LAYERS)]
show([p for p, _ in LAYERS] + [FACE_PX], marks + ['#'])
