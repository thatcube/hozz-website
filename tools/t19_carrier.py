"""
t19 · Carrier — the bubble as the wave, not the container.

The homework, first, because it decided the design.

Rasterised to 32, the three shipped marks agree on one thing nobody states:
**the centre stays plain and the whole tone spend goes into the outer band.**
Plozz's screen field is one tone under the face; Mozz's label field is one tone
under the face; c45's six rings enclose a flat core exactly the size of the
compact face. That is not taste, it is arithmetic — the face is 8-10 wide on a
28-wide container, so any tone structure that crosses the middle crosses the
face.

Where they differ is the *direction* the outer band is banded in, and each one
takes its direction from what the object physically is:

  Plozz   frame-parallel — a screen is recessed, so the bands are an inset
          bevel, lightest ring outermost, wrapping all four sides.
  Mozz    angular — a record spins, so the bands sweep rotationally, with a
          single lighter pixel line (#c10026, 12px) reading as the groove.
  c45     contour-parallel — a lens is curved, so the bands are concentric
          rings falling from a near-white rim to a deep core.

Recessed, rotational, concentric. So the honest question is what direction a
speech bubble's bands run in, and that has to come from what a speech bubble
physically is.

A record's groove is a *recorded* wave. A speech bubble is the *live* one — it
is the notation for a voice in air, and the tail is not decoration, it is the
mouth the voice came out of. So the bands here are **arcs struck from the
tail**: an inset ramp whose centre of curvature sits outside the shape, at the
tip of the tail, instead of at the middle of it.

That gives the fourth direction, and it gives it for a reason: eccentric. The
ring stack *breathes* — wide and soft where the wave has just arrived at the
bottom left, tight and crisp at the far shoulder where it has thinned to a
rim. Same six-to-seven small steps as c45, same light-rim-to-deep-core
direction, so the two read as one system; but the level lines bunch and spread
instead of sitting parallel, which is the one thing a wavefront does and a
bevel, a sweep and a concentric ring never do.

It also fixes the shipped mark's other fault. There the tail is a wedge stuck
onto a rounded rectangle. Here every tone in the bubble is measured from the
tail, so the tail is where the interior comes from.

Geometry is deliberately close to the shipped silhouette — ten attempts to
reinvent this mark lost to the original. The only change is that the tail is
swept rather than wedged: its left edge continues the body's bottom-left corner
instead of dropping vertically, and it finishes a row higher and blunter.
"""
import colorsys
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check                                    # noqa: E402
from shade import rings, keyline, clear, to_paths, is_slab    # noqa: E402

OUT = ROOT / 'src/components/mark/logos'

# ---------------------------------------------------------------------------
# Silhouette
# ---------------------------------------------------------------------------

# Body, top row first. All widths even, so every row mirrors about x=16 by
# construction. Shipped Twozz reads 18,22,24,26,26,28 into the corner; this
# keeps that and only softens the bottom by one step.
BODY_W = [18, 22, 24, 26, 26, 28] + [28] * 13 + [26, 26, 24, 22]
BODY_TOP = 2

# The swept tail. Left edge 6,6,6,7 continues the body's corner (…4,5 at y23,
# y24) instead of dropping vertically the way the shipped wedge does; the right
# edge eases 16,13,11,9 so the taper decelerates into the tip.
TAIL_ROWS = {
    25: (6, 16),
    26: (6, 13),
    27: (6, 11),
    28: (7, 9),
}

# Where the voice enters. Half a pixel below the tip, so the innermost arc
# closes around the tail rather than sitting on it.
SOURCE = (8.0, 29.0)


def body():
    s = set()
    for i, w in enumerate(BODY_W):
        x0 = 16 - w // 2
        s |= {(x0 + k, BODY_TOP + i) for k in range(w)}
    return s


def tail():
    return {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)}


BODY = body()
SHAPE = BODY | tail()

# ---------------------------------------------------------------------------
# Palette — indigo-violet
#
# Eight steps, solved rather than eyeballed. The target is a luminance ramp
# that falls by a near-constant *ratio* (~0.79 a step), which is what a real
# falloff from a source does and what stops a ramp reading as bands, and a hue
# that walks from lavender at the crest toward indigo in the deep, because
# light leaving a violet surface loses its red first.
#
# The five steps the face sits on are all deeper than the shipped #8f52f6, so
# the white face clears more contrast here than it does on the shipped mark.
# ---------------------------------------------------------------------------

STEPS = 8
TARGET_LUM = [0.44, 0.33, 0.25, 0.185, 0.145, 0.117, 0.097, 0.082]
HUE = (272, 258)        # crest -> deep
SAT = (0.80, 0.58)
KEY = '#190f31'
FACE = '#ffffff'


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lum_rgb(rgb):
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def _solve(h, s, target):
    """The lightness at which hue h and saturation s hit a target luminance."""
    lo, hi = 0.0, 1.0
    for _ in range(48):
        m = (lo + hi) / 2
        rgb = [round(v * 255) for v in colorsys.hls_to_rgb(h / 360, m, s)]
        if _lum_rgb(rgb) < target:
            lo = m
        else:
            hi = m
    rgb = [round(v * 255) for v in colorsys.hls_to_rgb(h / 360, (lo + hi) / 2, s)]
    return '#%02x%02x%02x' % tuple(rgb)


RAMP = [
    _solve(HUE[0] + (HUE[1] - HUE[0]) * i / (STEPS - 1),
           SAT[0] + (SAT[1] - SAT[0]) * i / (STEPS - 1),
           TARGET_LUM[i])
    for i in range(STEPS)
]


def luminance(hexstr):
    return _lum_rgb([int(hexstr[i:i + 2], 16) for i in (1, 3, 5)])


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------------------
# The wave
#
# Level sets of the distance from the tail. The radii are chosen so the wave
# is tight where it has just left the mouth and opens as it dissipates — and
# so the third arc closes just short of the face, which puts the whole face on
# the deep half of the ramp without anything being cleared for it.
# ---------------------------------------------------------------------------

RADII = [5.0, 8.6, 12.3, 16.0, 19.6, 23.2, 27.0]


def dist(p):
    return math.hypot(p[0] + 0.5 - SOURCE[0], p[1] + 0.5 - SOURCE[1])


def build():
    key = keyline(SHAPE)
    inner = SHAPE - key
    bands = [set() for _ in range(STEPS)]
    for p in inner:
        d = dist(p)
        t = sum(1 for r in RADII if d >= r)
        bands[t].add(p)
    return key, bands


def report(key, bands):
    print(f'keyline {len(key)}px')
    for i, b in enumerate(bands):
        print(f'  ramp {i} {RAMP[i]}  {len(b):4d}px  '
              f'lum {luminance(RAMP[i]):.3f}  white-contrast {contrast(RAMP[i], FACE):.2f}')


def show(key, bands):
    grid = {}
    for p in key:
        grid[p] = 'K'
    for i, b in enumerate(bands):
        for p in b:
            grid[p] = str(i)
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(32):
        line = ''.join(grid.get((x, y), '.') for x in range(32))
        if line.strip('.'):
            print(f'{y:3d} {line}')


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

FACE_CX, FACE_CY = 16, 13
FACE_SIZE, FACE_SMILE, FACE_GAP = 'md', 'wide', 2
FACE_W, FACE_H = 8, 9          # md / wide / gap 2 — brief's measured table
FACE_TOP = FACE_CY - 4         # measured offset, not computed
FACE_LEFT = 16 - FACE_W // 2


def assertions(key, bands):
    out = []

    check(BODY)
    out.append('body symmetric about x=16 and free of spurs (circles.check; '
               'tail exempt by design)')

    ys = sorted({y for _, y in SHAPE})
    xs = sorted({x for x, _ in SHAPE})
    assert xs[0] >= 2 and xs[-1] <= 29 and ys[0] >= 2 and ys[-1] <= 29
    out.append(f'fits x{xs[0]}–{xs[-1]} y{ys[0]}–{ys[-1]} inside x2–29 y2–29')

    rows = {}
    for x, y in SHAPE:
        rows.setdefault(y, []).append(x)
    ws = [max(rows[y]) - min(rows[y]) + 1 for y in sorted(rows)]
    for i in range(1, len(ws) - 1):
        assert not (ws[i] > ws[i - 1] and ws[i] > ws[i + 1]), f'spur at row {i}'
    out.append('no spurs anywhere in the full silhouette, tail included')

    body_ys = sorted({y for _, y in BODY})
    top, bot = body_ys[0], body_ys[-1]
    air_above = FACE_TOP - top
    air_below = bot - (FACE_TOP + FACE_H - 1)
    assert air_above == air_below, (air_above, air_below)
    out.append(f'face centred on the body y{top}–{bot}: '
               f'{air_above} rows of air above, {air_below} below')

    body_w = max(BODY_W)
    assert body_w % 2 == FACE_W % 2
    assert FACE_LEFT - min(xs) == max(x for x, y in BODY if y == 16) - (FACE_LEFT + FACE_W - 1)
    out.append(f'parity: body {body_w} wide and face {FACE_W} wide are both even, '
               f'so the face centres on x=16 exactly')

    tones = 1 + len(RAMP) + 1
    assert tones >= 8
    out.append(f'{tones} tones (keyline + {len(RAMP)} ramp + face)')

    for i, b in enumerate(bands):
        assert b, f'ramp step {i} is empty'
        assert not is_slab(b, SHAPE), f'ramp step {i} reads as a pasted slab'
    out.append('every ramp step is non-empty and derived from the contour '
               '(shade.is_slab clean)')

    face_px = {(x, y) for x in range(FACE_LEFT, FACE_LEFT + FACE_W)
               for y in range(FACE_TOP, FACE_TOP + FACE_H)}
    under = {i for i, b in enumerate(bands) if b & face_px}
    worst = min(contrast(RAMP[i], FACE) for i in under)
    assert worst >= 4.3, worst
    out.append(f'white face sits on ramp steps {sorted(under)} and clears '
               f'{worst:.2f}:1 on the lightest of them '
               f'(shipped mark manages {contrast("#8f52f6", "#ffffff"):.2f}:1)')

    ratios = [luminance(RAMP[i + 1]) / luminance(RAMP[i]) for i in range(len(RAMP) - 1)]
    assert all(0 < r < 1 for r in ratios)
    assert max(ratios) - min(ratios) < 0.12, ratios
    out.append('ramp falls monotonically at a near-constant ratio '
               f'({min(ratios):.2f}–{max(ratios):.2f} a step) — a falloff, not bands')
    return out


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------

ASTRO = '''---
/**
 * t19 · Carrier
 *
 * A record's groove is a recorded wave. A speech bubble is the live one.
 *
 * Rasterised to 32, the three shipped marks all agree on something they never
 * say: the centre stays plain and the whole tone spend goes into the outer
 * band. They only differ in the *direction* that band is banded in, and each
 * takes its direction from what the object physically is — Plozz's screen is
 * recessed so its bands are a frame-parallel bevel, Mozz's record spins so its
 * bands sweep rotationally around it, Hozz's lens is curved so its bands are
 * concentric rings falling from a near-white rim to a deep core.
 *
 * Recessed, rotational, concentric. A speech bubble is none of those. It is
 * the notation for a voice in air, and the tail is not decoration — it is the
 * mouth the voice came out of. So the bands here are arcs struck from the
 * tail: the same seven small steps as the Lens, running the same way from a
 * light rim to a deep core, but with their centre of curvature outside the
 * shape rather than in the middle of it.
 *
 * That makes the stack *breathe*. Where the wave has just arrived, at the
 * bottom left, the rings run wide and soft and reach a third of the way across
 * the bubble. At the far shoulder they have thinned to a one-pixel rim. Level
 * lines that bunch and spread are the one thing a wavefront does and a bevel,
 * a sweep and a concentric ring never do — so this is a fourth direction, and
 * it is a fourth direction for a reason rather than for variety.
 *
 * It also repairs the shipped mark's second fault. There the tail is a wedge
 * stuck onto a rounded rectangle. Here every tone in the bubble is measured
 * from the tail, so the tail is where the interior comes from. Its left edge
 * now continues the body's bottom-left corner instead of dropping vertically,
 * and it finishes a row higher and blunter.
 *
 * Indigo-violet rather than the shipped mark's #8f52f6. Twitch's association
 * is kept, but pulled toward indigo and deepened: a seven-step ramp needs
 * somewhere to go, and #8f52f6 is already light enough that the white face
 * only clears 4.3:1 on it. Every tone the face sits on here clears more.
 *
 * The face is `md` with the `wide` smile — the size the chosen Hozz mark uses
 * — centred on the bubble **body**, tail ignored: __AIR__ rows of air above
 * and __AIR__ below, measured. Nothing is cleared for it.
 *
 * __TONES__ tones.
 */
import MarkFrame from '../MarkFrame.astro';
import { facePathsAt } from '../../../data/mark';

interface Props { size?: number }
const { size = 128 } = Astro.props;
---

<MarkFrame size={size} title="Twozz — Carrier">
__PATHS__
  <g fill="__FACE__" shape-rendering="crispEdges">
    {facePathsAt({ cx: __CX__, cy: __CY__, size: '__SZ__', smile: '__SMILE__', gap: __GAP__ }).map((d) => (
      <path d={d} />
    ))}
  </g>
</MarkFrame>
'''

META = '''export default {
  n: 't19', name: 'Carrier',
  idea: 'A record has a groove — a recorded wave. A speech bubble has the live one: seven close tones struck as arcs from the tail, so the ring stack runs wide where the voice has just arrived and thins to a rim at the far shoulder.',
  ground: 'light',
  palette: __PALETTE__,
};
'''


def emit(key, bands, air):
    parts = [f'  <path d="{" ".join(to_paths(bands[i]))}" fill="{RAMP[i]}" />'
             for i in range(len(bands) - 1, -1, -1)]
    parts.insert(0, f'  <path d="{" ".join(to_paths(key))}" fill="{KEY}" />')
    astro = (ASTRO
             .replace('__PATHS__', '\n'.join(parts))
             .replace('__FACE__', FACE)
             .replace('__CX__', str(FACE_CX))
             .replace('__CY__', str(FACE_CY))
             .replace('__SZ__', FACE_SIZE)
             .replace('__SMILE__', FACE_SMILE)
             .replace('__GAP__', str(FACE_GAP))
             .replace('__AIR__', str(air))
             .replace('__TONES__', str(2 + len(RAMP))))
    (OUT / 't19.astro').write_text(astro)

    pal = [KEY] + list(reversed(RAMP)) + [FACE]
    (OUT / 't19.meta.ts').write_text(
        META.replace('__PALETTE__', '[' + ', '.join(f"'{c}'" for c in pal) + ']'))


if __name__ == '__main__':
    k, b = build()
    report(k, b)
    show(k, b)
    for line in assertions(k, b):
        print('  ok ·', line)
    emit(k, b, FACE_TOP - min(y for _, y in BODY))
    print('\nwrote t19.astro / t19.meta.ts')
