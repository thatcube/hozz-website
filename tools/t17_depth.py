"""
t17 — Depth. The bubble as a physical object with thickness.

The direction: not a flat shape with light painted on it, but something with a
front face, an edge, and a body behind.

The shipped Twozz already claims thickness, which is easy to miss until you
rasterise it. Of its five tones, two do nothing but assert an edge — one row of
#ad84ec along the top of the bubble and one row of #7243c3 along the bottom,
with the tail filled in that same deep tone as though it were folded away from
you. So the shipped mark is not flat. It is a slab, one pixel of light on the
top edge and one of shadow on the bottom, with nothing behind it.

Plozz takes the same idea one step further and shows what "behind it" looks
like:

      6 .....0000000000000000000000.....   keyline
      7 ....066666666666666666666660....   case, lit along its top edge
      8 ...06222222222222222222222260...   case, mid
      9 ..0622200000000000000000022260..   case, then the bezel closing
     10 ..0622033333333333333333302260..   screen, one plane further back
     ...
     28 ....055555555555555555555550....   case, shaded along its bottom edge

Three planes, and the solidity is not in any single tone: it is in the fact
that the tones change *direction* when the plane changes.

t17 keeps the shipped Twozz's claim exactly and puts a plane behind it:

    keyline -> rim (2px) -> fold -> recessed panel -> face

and it rests on one inversion.

  * The **rim is proud**. Light from above lands on its top edge and misses its
    underside, so it runs light at the top, mid at the sides, dark along the
    bottom — which is the shipped mark's own two rows, widened to two pixels so
    there is something to see.
  * The **panel is recessed**, so it runs the other way. It sits a plane
    further from the light to begin with, and the near wall throws a shadow
    across the top of it; what light clears that wall lands at the bottom. Dark
    at the top, brightening downward.

Read down the middle and the tone reverses at exactly the rows where the plane
changes. That is the whole argument, and it is the one thing a drop shadow
cannot imitate: a shadow darkens in one direction only and it lives *outside*
the silhouette. Every pixel here is inside it. It is also what keeps this off
the 2005 bevel — a bevel filter runs light top-left to dark bottom-right across
everything at once, uniformly; here the two planes disagree on purpose, and the
light is straight top-down rather than diagonal, which is what a rounded rim
under a ceiling light actually does.

The fold is not one surface either. Its top arc is the near wall, leaning down
and away from the light, and it is the darkest thing in the mark. Its bottom
arc is the far wall, tipped up into the light, and it takes the *same tone as
the top of the rim* — because it faces the same way, and a surface that faces
the same way should be the same colour wherever it occurs. That single rule
does a lot of work: it costs nothing, it makes the bright shelf at the bottom
of the recess feel like part of the object rather than a highlight painted on
it, and the floor ramps smoothly up into it.

The floor's grading is carried by two contour rings graded by height, not by
horizontal bands. Bands were tried first and failed: 1px stripes across a
14-row floor are invisible at 96px, and the mark read as a flat shape with a
thick border. Rings wrap the corners, so grading them by height makes the same
two rings deliver an inset bevel you can still see at 24px *and* a gradient
that tells you which way is up. Down the sides they pass through the core's own
tone and vanish, which is correct: a floor lit from above gets nothing from
walls it is edge-on to, and drawing something there is how a recess becomes an
emboss.

Subtlety is enforced, not hoped for. No step inside either ramp moves any
channel by more than 18, inside the 21 the shipped Plozz screen already spends.
The only jumps larger than that are plane changes, where a jump is the point.

The silhouette is the shipped bubble's, measured off the raster: the same
six-row corner arc, the same narrow tail hung from a vertical left edge with
the taper on its right. An earlier pass ran the tail out at 45 degrees and it
read as an arrow; another made it eight pixels wide at the junction and it read
as a nub. The shipped proportion is a tail six wide falling to a point, and it
is right.

Face: `lg` + `wide` + gap 1. mark.ts says to keep `lg` for a plain open field,
and at first glance a rim, a fold and a graded floor disqualify this one — but
the recess exists precisely to make a plain open field, and its core is a
single tone across 204 pixels. That is the same argument Plozz makes: a busy
container, a plain screen built into it, and a full-size face on the screen. A
smaller face was tried and next to the shipped mark it read as timid. `wide` is
Twozz's own smile against Plozz's compact one, and gap 1 brings the face to ten
rows, which is what makes the air come out equal on a 24-row body.

White ink, because FAMILY records Twozz's as white and it is the reason the
shipped mark carries at 24px. That in turn fixes the polarity: the floor has to
stay dark enough to hold white type, which is also the physically honest
reading of a recess — a scooped-out hollow is further from the light than the
face around it, not nearer.
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
# A true quarter-circle corner, not a rounded-rectangle one. The arc is r = 9
# sampled honestly — inset = r - sqrt(r^2 - k^2) at each row — which gives
# 16, 20, 22, 24, 26, 26 before full width: six rows of arc on a body 22 rows
# tall, so better than a quarter of the height is curve. An earlier pass copied
# the shipped mark's tighter arc on the theory that matching it exactly was the
# safest way to sit next to the siblings, and on a sheet of ten it read as a
# squircle badge instead: the corners were tight enough, and the sides straight
# enough, that the thing stopped looking like a bubble and started looking like
# an app tile. Speech is the meaning of this mark, so the silhouette is not
# decoration and cannot be the part that gets compromised.
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

# The tail is a wedge growing off the lower left, and the thing that makes it
# read as a wedge rather than as a notch bitten out of the outline is a visible
# change of direction where it leaves the body. Down the body's bottom-left the
# left edge is curving inward — x3, x4, x5, x6, x8 — and at the junction that
# curve stops dead and goes vertical: x8 for all six rows, with the whole taper
# carried on the right. Curve, then straight. You can see the corner turn.
#
# Six rows and eight wide at the junction, against a bottom row only sixteen
# wide, so the tail is half the width it hangs off and cannot be mistaken for a
# nick in the arc. An earlier version gave it four rows off a flat 28-wide
# bottom, and at that proportion it was a notch.
#
# The left edge is flush with the body's bottom row rather than stepping out
# past it. A single column poking out one row lower than its neighbour is a new
# upward-facing surface, and the lighting rule correctly lights it: one stray
# pale pixel halfway down the tail.
TAIL_ROWS = {
    24: (8, 15),
    25: (8, 14),
    26: (8, 13),
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
#
# Three rings, not four. The first version spent six of the fourteen columns
# across the mark on edge treatment — keyline, three rings of rim, a fold, then
# two grading rings — and however carefully each one was toned, the sum of them
# read as a frame drawn around the shape rather than as an edge belonging to
# it. At 28px it closed over the interior and the mark went muddy. One ring of
# rim, one of fold and one of grading is enough to state three planes, and it
# hands four extra columns back to the field the face sits on.
BANDS, PANEL = rings(BODY, 3)
FOLD = BANDS[2]                     # where the front face turns inward

# The fold is not one surface, it is the recess's own wall, and its top and
# bottom face opposite ways. The near wall — the top arc — leans down and away
# from the light, so it is the darkest thing in the mark. The far wall — the
# bottom arc — leans up into it, and so takes the same tone as the top of the
# rim, which faces the same way. The sides are edge-on and stay with the wall.
#
# Derived from the panel rather than from the fold itself: `edge` follows
# contours per run, so on a closed ring it reports both arcs as "topmost" and
# the two come out identical. Asking which fold pixels have panel below them,
# and which have panel above, is unambiguous.
F_TOP = {(x, y) for (x, y) in FOLD if (x, y + 1) in PANEL}
F_BOT = {(x, y) for (x, y) in FOLD if (x, y - 1) in PANEL} - F_TOP
F_SIDE = FOLD - F_TOP - F_BOT

# BANDS[0] is the body's own outline. Almost all of it coincides with the
# object's outline and is keyline; the pixels that do not are exactly the tail
# junction, and there the wall must carry on into the tail rather than have a
# dark line ruled across it.
RIM = (BANDS[0] - KEY_PX) | BANDS[1]

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
# One contour ring and a core, graded by height — the part Plozz has no reason
# to do, because a TV screen is emissive and a recess is not.
#
# One construction, two jobs. Across the top the ring runs darker than the
# core: the near wall's shadow lying on the floor. Across the bottom it runs
# lighter: the light that cleared the wall, pooling where it lands. Down the
# sides it passes through the core's own tone and disappears, which is right —
# a floor lit from directly above gets nothing extra from walls it is edge-on
# to, and drawing something there is how a recess turns into an emboss.
#
# The ring used to be two rings, and losing one is what stopped the interior
# reading as a frame. It costs nothing: the grading was always the thing doing
# the work, and a one-pixel ring sweeping the whole ramp says it just as well
# as two pixels sweeping it twice.
#
# The core is a single tone across better than two hundred pixels, which is the
# plain open field the face needs and the reason `lg` is defensible here.
# ---------------------------------------------------------------------------
P_RINGS, P_CORE = rings(PANEL, 1)
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


P_LAYERS = {}
for i, s in grade(P_RINGS[0], 0, STEPS - 1).items():
    P_LAYERS.setdefault(i, set()).update(s)
P_LAYERS.setdefault(CORE_I, set()).update(P_CORE)

# ---------------------------------------------------------------------------
# Palette.
#
# Violet, and staying violet. Twitch is purple and the client only allowed
# *leaving* purple, he did not ask for it; the family already spends cyan on
# Plozz, red on Mozz and pale blue on Hozz, so violet is the one open hue with
# nothing to argue about. It is pulled toward indigo from the shipped #8f52f6,
# which sits too near the top of its own range to leave a ramp anywhere to go —
# and the client's standard, "you barely notice it change colours, and yet
# they're completely different colours", needs a wide total range crossed in
# small steps.
#
# Two ramps, because there are two planes, and they are stacked rather than
# side by side. The wall is the front face and is the lighter of the two: it is
# nearest the light. The floor sits behind it and runs darker, which is both
# what a scooped hollow does and what lets it carry white type. Between them
# the fold spans from one to the other, and that span is a plane change, so it
# is allowed to jump where a ramp step is not.
#
# Everything except the keyline now lives in the upper half of the range. The
# first palette put four interior tones below #6b3fc9 to buy depth, and it did
# buy depth — at 320px. At 28px those tones merged with the keyline into one
# dark ring and the mark turned to mud. The two siblings that stay legible
# small, t19 and t14, both bottom out around #6138d0 and #7243c3 and spend
# nothing below that, so this ramp does the same: one dark tone, the outline,
# and light doing all the work inside it.
#
# The floor ramp is hinged on the core rather than run straight from end to
# end, because the core is the one tone the white face has to sit on and it has
# to clear 4.5:1. Hinging lets the floor climb well past the core on the way
# down without dragging the core up with it.
# ---------------------------------------------------------------------------
KEY = '#1e1136'
WALL = ['#b78ef3', '#a87ce9', '#986bde']        # up-facing, mid, down-facing
F_SIDE_C = '#885ad3'                            # the wall, one step deeper
F_TOP_C = '#7849c7'                             # deeper again: the near wall

FLOOR_LO = (0x64, 0x37, 0xc4)                   # the near wall's shadow
FLOOR_CORE = (0x81, 0x54, 0xcf)                 # the plain field, 5.1:1 white
FLOOR_HI = (0xad, 0x86, 0xee)                   # where the light lands
INK = '#ffffff'                                 # Twozz's own ink, per FAMILY


def lerp(a, b, t):
    return round(a + (b - a) * t)


FLOOR = []
for i in range(STEPS):
    if i <= CORE_I:
        a, b, t = FLOOR_LO, FLOOR_CORE, i / CORE_I
    else:
        a, b, t = FLOOR_CORE, FLOOR_HI, (i - CORE_I) / (STEPS - 1 - CORE_I)
    FLOOR.append('#%02x%02x%02x' % tuple(lerp(a[c], b[c], t) for c in range(3)))

MAX_STEP = 18  # Plozz's own widest interior step is 21, so this is inside it.
# Two ramps, continued by the parts of the fold that belong to them. The near
# wall and the sides are the front face carrying on down into shadow. The far
# wall is tipped up into the light exactly as the top of the rim is, so it
# takes the rim's own lit tone and the floor ramps up into it — the same
# surface orientation gets the same tone wherever it occurs.
for ramp, what in ((WALL + [F_SIDE_C, F_TOP_C], 'wall'),
                   (FLOOR + [WALL[0]], 'floor')):
    for a, b in zip(ramp, ramp[1:]):
        d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
        assert d <= MAX_STEP, f'{what}: {a}->{b} steps by {d}, which reads as a band'

LAYERS = [
    (KEY_PX, KEY),
    (W_LIT | F_BOT, WALL[0]),
    (W_MID, WALL[1]),
    (W_SHAD, WALL[2]),
    (F_SIDE, F_SIDE_C),
    (F_TOP, F_TOP_C),
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
# even-height face is not symmetric about cy. `lg` + `wide` + gap 1 is 10 rows,
# and the table gives (10, -5), so top = cy - 5.
#
# Equal air on the *body*, ignoring the tail, exactly as Plozz centres on its
# screen rather than on its whole TV:
#     top - y0 == y1 - (top + h - 1)   ->   top = (y0 + y1 - h + 1) / 2
# With the body at y2-y23 and h = 10 that is top = 8, so cy = 13. The same
# arithmetic is why the body is 22 rows: it forces y0 + y1 - h + 1 even, and
# an odd result would have put the face half a pixel off centre.
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
assert FACE_PX <= PANEL, 'the face spills off the panel onto the rim'
assert FACE_PX <= P_CORE, 'the face sits on the floor grading rather than its plain core'


def luminance(hexc):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


CONTRAST = (max(luminance(FLOOR[CORE_I]), luminance(INK)) + 0.05) / \
           (min(luminance(FLOOR[CORE_I]), luminance(INK)) + 0.05)
assert CONTRAST >= 4.5, f'face contrast only {CONTRAST:.2f}:1 on the core'

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
DOC = f'''/**
 * t17 · Depth
 *
 * The bubble as a physical object with thickness, rather than a flat shape
 * with light on it.
 *
 * The shipped Twozz mark already claims thickness — of its five tones, two do
 * nothing but assert an edge: one row of #ad84ec along the top of the bubble
 * and one of #7243c3 along the bottom, with the tail filled in that same deep
 * tone as though it were folded away from you. It is a slab. What it has not
 * got is anything behind it. Plozz has: a case, a bezel, and a screen one
 * plane further back. This keeps the shipped mark's claim and adds the plane.
 *
 *     keyline -> rim (2px) -> fold -> recessed panel -> face
 *
 * It turns on one inversion. The **rim is proud**, so light lands on its top
 * edge and misses its underside: light at the top, mid at the sides, dark
 * along the bottom — the shipped mark's two rows, widened to two pixels so
 * there is something to see. The **panel is recessed**, so it runs the other
 * way. It sits a plane further from the light to begin with, and the near wall
 * throws a shadow across the top of it, so it is darkest at the top and
 * brightens downward.
 *
 * That reversal is the argument. A drop shadow darkens in one direction only
 * and lives outside the silhouette; every pixel here is inside it. A bevel
 * filter runs light top-left to dark bottom-right across everything at once;
 * here the two planes disagree on purpose, and the light is straight top-down
 * rather than diagonal, which is what a rounded rim under a ceiling light
 * actually does.
 *
 * The fold is not one surface either. Its top arc is the near wall, leaning
 * away from the light, and it is the darkest thing in the mark. Its bottom arc
 * is the far wall, tipped up into it, and it takes the *same tone as the top
 * of the rim* — a surface that faces the same way should be the same colour
 * wherever it occurs. That costs no extra tone and it makes the bright shelf
 * at the bottom of the recess feel like part of the object rather than a
 * highlight painted onto it.
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
 * the shipped Plozz screen already spends. The only jumps larger than that are
 * plane changes, where a jump is the point.
 *
 * Silhouette and tail are the shipped bubble's own, measured off the raster —
 * the same six-row corner arc, the same narrow tail on a vertical left edge.
 * One row taller in the body, which is what lets a full-size face clear the
 * floor's grading and still leave equal air.
 *
 * Violet, pulled toward indigo from the shipped #8f52f6, which sits too near
 * the top of its own range to leave a ramp anywhere to go. White ink, as the
 * shipped mark has, which is what fixes the polarity: the floor has to stay
 * dark enough to carry it, and a hollow being darker than the face around it
 * is the honest reading anyway.
 *
 * {len(TONES)} tones. Body y{BODY_Y0}-{BODY_Y1}, {BODY_W} wide, symmetric about x=16;
 * the tail is asymmetric by design and exempt. Face {FACE_SIZE}/{FACE_SMILE}/gap{FACE_GAP} on the
 * plain core at {CONTRAST:.1f}:1, with {AIR_ABOVE} rows of air above it and {AIR_BELOW} below,
 * measured on the body, not on the tail.
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

palette = [KEY, F_TOP_C, F_SIDE_C] + WALL[::-1] + FLOOR
meta = f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'The shipped mark already spends two of its five tones asserting an edge. This keeps that claim and puts a plane behind it: a proud rim lit on top and shaded underneath, folding into a recess that grades the other way, so the tone reverses exactly where the plane does.',
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
marks = ['K', 'L', 'M', 'S', 'f', 'v'] + [str(i) for i in sorted(P_LAYERS)]
show([p for p, _ in LAYERS] + [FACE_PX], marks + ['#'])
