"""
c41 · Ripple, Inset — the gradual fade from the edges.

Brandon's brief for this one:

    "another variation could just be more gradual fade from the edges, like
    instead of 1 pixel of lighting/shading, we have 3px of it? like how this tv
    has more white around the edges and it gradually gets more blue towards the
    center. it's subtle, you barely notice it change colors as it moves towards
    the center, and yet theyre completely different colors."

The TV is the shipped Plozz mark. Rather than take the three rows quoted in the
brief on trust, `~/hozzshots/ref/plozz.svg` was rasterised to the 32x32 grid and
the whole screen measured. What is actually there:

  * Three tones, #97e3fe -> #82deff -> #72daff, lightest at the edge.
  * One pixel per step on the flanks, two at the corners, so the ramp thickens
    on the diagonals.
  * It wraps all four sides. It is an inset bevel, not a top highlight.
  * The steps are tiny: 0.0257 and 0.0186 in Oklab. That is the number that
    matters, because it is why you "barely notice it change colors".

So the rule this mark follows is Plozz's step size, not Plozz's step count.
Every neighbouring pair here is 0.021 apart — inside Plozz's own range and
below its larger step — but there are eight of them instead of three, so the
ramp travels 0.147 in total, three times Plozz's 0.044. Same imperceptible
step, much further travelled. That is the whole idea: "you barely notice it
change colors ... and yet theyre completely different colors."

Geometry. The tone at each pixel comes from its Euclidean distance to the
outside of the disc, quantised at half-integer cuts so one pixel of travel is
always exactly one step, never two and never none. On the flanks that is 1px a
step; on the diagonals the bands double to 2px, which is the corner thickening
measured off Plozz reproduced for free rather than drawn in.

The target problem. A ramp wrapping inward from every edge of a *circle* is
concentric, and concentric bands are how you draw a target. Two things stop it
reading as one, and both are asserted below rather than eyeballed:

  * The ramp is monotone. Lightness falls from the rim to the middle and never
    comes back. A bullseye needs a ring lighter than the rings on both sides of
    it, so along every row and every column the tone sequence is asserted to be
    unimodal. No enclosed lighter ring can exist.
  * The step is below the threshold at which a band edge is visible, measured
    against the reference rather than guessed.

What is left is a radial falloff with no visible ring in it, and the deepest
blue pooled exactly where the face sits — the pearl, not the dartboard.

The disc, the water and the size are c10's, untouched. Only the tones changed.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check          # noqa: E402
from shade import keyline, to_paths        # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG, NAME = 'c41', 'Ripple, Inset'

# --- the fixed parts: c10's water, and the canonical 22-across disc ---------
SRC = (OUT / 'c10.astro').read_text()
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


WATER_OUT = set().union(*[pixels(d) for d, f in PATHS[:26] if f == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, f in PATHS[:26] if f != '#96bcd6'])

DISC = circle(22)
check(DISC)
KEYRING = keyline(DISC)
INNER = DISC - KEYRING

KEY = '#132638'

# --- colour ----------------------------------------------------------------
# Oklab, so the steps are perceptually even rather than evenly spaced in sRGB,
# which for pale blues is not the same thing at all.


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(c):
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


def oklab(h):
    r, g, b = (_lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def unlab(lab):
    L, A, B = lab
    l, m, s = ((L + 0.3963377774 * A + 0.2158037573 * B) ** 3,
               (L - 0.1055613458 * A - 0.0638541728 * B) ** 3,
               (L - 0.0894841775 * A - 1.2914855480 * B) ** 3)
    return '#%02x%02x%02x' % (
        _srgb(+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        _srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        _srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s))


def dE(a, b):
    return math.dist(oklab(a), oklab(b))


N = 8
SPAN_RIM, SPAN_CORE = '#f2f9fd', '#a9cfe8'      # the direction and length only

# Plozz's own screen ramp, read off the raster — the yardstick for "subtle".
PLOZZ = ['#97e3fe', '#82deff', '#72daff']
PLOZZ_MAX = max(dE(a, b) for a, b in zip(PLOZZ, PLOZZ[1:]))

# --- the fade --------------------------------------------------------------


def depth(shape):
    """Euclidean distance from each pixel to the nearest pixel outside `shape`.

    Derived from the silhouette, so it can only ever follow the contour — the
    same discipline as `shade.rings`, just continuous instead of stepped.
    """
    out = [(x, y) for x in range(-3, 35) for y in range(-3, 35) if (x, y) not in shape]
    d = {}
    for p in shape:
        best = min((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for q in out)
        d[p] = math.sqrt(best)
    return d


DEPTH = depth(INNER)
CUTS = [k + 1.5 for k in range(N - 1)]          # half-integers: 1px = 1 step


def tone(v):
    i = 0
    while i < len(CUTS) and v > CUTS[i]:
        i += 1
    return i


TONE = {p: tone(v) for p, v in DEPTH.items()}

# --- the face --------------------------------------------------------------
SIZE, SMILE = 'md', 'wide'
WIDTH = {'lg': 10, 'md': 8, 'sm': 7}
GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
}[SIZE]

dys = sorted({p[1] for p in DISC})
dxs = sorted({p[0] for p in DISC})
disc_w = dxs[-1] - dxs[0] + 1
disc_mid2 = dys[0] + dys[-1] + 1

assert SIZE in ('md', 'lg'), 'sm is 7 wide and cannot centre on an even disc'
assert (disc_w - WIDTH[SIZE]) % 2 == 0, (
    f'a {WIDTH[SIZE]}-wide face cannot centre on a {disc_w}-wide disc')

choice = None
for g in (2, 3, 1, 4):
    h, off = GEOM[g]
    if (disc_mid2 - h) % 2:
        continue
    choice = (g, h, (disc_mid2 - h) // 2 - off)
    break
assert choice, 'no gap centres the face on this disc'
GAP, FH, CY = choice
TOP = CY + GEOM[GAP][1]
LEFT = 16 - WIDTH[SIZE] // 2
ABOVE = TOP - dys[0]
BELOW = dys[-1] - (TOP + FH - 1)
assert ABOVE == BELOW, f'air {ABOVE}/{BELOW} on the disc'

# The md/wide face, ported from src/data/mark.ts so the ramp can be checked
# against the pixels the face actually covers rather than its bounding box.
_EYES = [[(0, 2)], [(1, 2)], [(0, 1)], [(0, 2)]]
_SMILE = [[(0, 0), (7, 7)], [(0, 1), (6, 7)], [(1, 6)]]
_ROWS = ([[(a, b), (a + 5, b + 5)] for r in _EYES for (a, b) in r]
         + [[] for _ in range(GAP)] + _SMILE)
FACE = {(LEFT + a + i, TOP + r)
        for r, runs in enumerate(_ROWS) for (a, b) in runs for i in range(b - a + 1)}
assert len(_ROWS) == FH, f'ported face is {len(_ROWS)} rows, expected {FH}'

# The port is checked against what `facePathsAt` actually emits, so a change to
# mark.ts breaks this generator rather than silently mis-measuring the air.
_EXPECT = ('M12 8h3 M17 8h3 M13 9h2 M18 9h2 M12 10h2 M17 10h2 M12 11h3 M17 11h3 '
           'M12 15h1 M19 15h1 M12 16h2 M18 16h2 M13 17h6')
_GOT = ' '.join(f'M{LEFT + a} {TOP + r}h{b - a + 1}'
                for r, runs in enumerate(_ROWS) for (a, b) in runs)
assert _GOT == _EXPECT, f'face port drifted from mark.ts:\n  {_GOT}\n  {_EXPECT}'

# --- placing the ramp ------------------------------------------------------
# First attempt hung the ramp off a near-white rim and let the far end fall
# where it fell. At 96px that looked right; at 24px the disc went ghostly next
# to c19 and c20, because the pale outer bands cover far more area than the deep
# inner ones — 76 pixels of the lightest tone against 22 of the darkest — so the
# average of the whole disc came out about a step lighter than the flat
# #cfe3ef its siblings use, and at small sizes the average is all you see.
#
# So the ramp is not positioned by its ends. It is positioned by its *mean*:
# the tone geometry is worked out first, each tone weighted by how many pixels
# of it are actually visible around the face, and the ramp slid along its own
# axis until that area-weighted average lands exactly on #cfe3ef. c41 therefore
# weighs the same as the marks beside it. What is different is the distribution,
# not the level — which is the honest way to show that the fade is doing the
# work rather than a general lightening.
VIS = {k: sum(1 for p, t in TONE.items() if t == k and p not in FACE) for k in range(N)}
MEAN_T = sum(k * n for k, n in VIS.items()) / sum(VIS.values()) / (N - 1)

FIELD = '#cfe3ef'                                # what c18-c21 use, flat
_d = [b - a for a, b in zip(oklab(SPAN_RIM), oklab(SPAN_CORE))]
_f = oklab(FIELD)
_a = [_f[i] - MEAN_T * _d[i] for i in range(3)]
RAMP = [unlab(tuple(_a[i] + _d[i] * k / (N - 1) for i in range(3))) for k in range(N)]

# --- assertions ------------------------------------------------------------
LAYERS = [(WATER_OUT, '#96bcd6'), (WATER_IN, '#5d8cb0')]
LAYERS += [({p for p, t in TONE.items() if t == k}, c) for k, c in enumerate(RAMP)]
LAYERS += [(KEYRING, KEY)]

for px, fill in LAYERS:
    assert px, f'{fill} is empty'
    assert all((31 - x, y) in px for x, y in px), f'{fill} is not symmetric about x=16'
# The face itself is not mirror-symmetric and must not be asserted so: a Z is
# not a mirrored Z, and the right eye is a second Z rather than a reflection of
# the first. What has to hold is that its *box* straddles x=16 evenly, which is
# the parity rule — an odd-width face lands on 16.5 and leans.
fxs = sorted({p[0] for p in FACE})
assert fxs[0] + fxs[-1] == 31, f'face box {fxs[0]}-{fxs[-1]} is not centred on x=16'
assert fxs[-1] - fxs[0] + 1 == WIDTH[SIZE], 'face is not the width it claims'

steps = [dE(a, b) for a, b in zip(RAMP, RAMP[1:])]
assert len(set(RAMP)) >= 6, 'fewer than 6 tones'
assert max(steps) <= PLOZZ_MAX, (
    f'step {max(steps):.4f} is coarser than Plozz\'s {PLOZZ_MAX:.4f}')

Ls = [oklab(c)[0] for c in RAMP]
assert all(a > b for a, b in zip(Ls, Ls[1:])), 'ramp is not monotone; a lighter ' \
    'tone inside a darker one is a bullseye'

# No enclosed lighter ring: along every scanline the tone must rise then fall.
for axis in (0, 1):
    lines = {}
    for p, t in TONE.items():
        lines.setdefault(p[axis], []).append((p[1 - axis], t))
    for k, seq in lines.items():
        ts = [t for _, t in sorted(seq)]
        peak = ts.index(max(ts))
        assert ts[:peak + 1] == sorted(ts[:peak + 1]), f'dip on {"xy"[axis]}={k}'
        assert ts[peak:] == sorted(ts[peak:], reverse=True), f'dip on {"xy"[axis]}={k}'
        assert all(abs(a - b) <= 1 for a, b in zip(ts, ts[1:])), \
            f'tone skipped on {"xy"[axis]}={k} — that is a band, not a fade'

vis = VIS
assert min(vis.values()) > 0, f'a tone is entirely hidden behind the face: {vis}'

# The disc must weigh the same as its siblings: the average of what you can
# actually see is the flat tone c18-c21 use, so nothing here reads as merely
# lighter or merely darker than them.
_mean = [sum(oklab(RAMP[k])[i] * n for k, n in vis.items()) / sum(vis.values())
         for i in range(3)]
MEAN_HEX = unlab(tuple(_mean))
assert dE(MEAN_HEX, FIELD) < 0.002, (
    f'area-weighted mean is {MEAN_HEX}, not {FIELD} (dE {dE(MEAN_HEX, FIELD):.4f})')

# Contrast under the face: the darkest tone still has to carry the keyline ink.
def _rl(h):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


CONTRAST = (max(_rl(RAMP[-1]), _rl(KEY)) + 0.05) / (min(_rl(RAMP[-1]), _rl(KEY)) + 0.05)
assert CONTRAST >= 7, f'face on the core is only {CONTRAST:.1f}:1'

print(f'{SLUG} {NAME}')
print(f'  disc {disc_w}x{len(dys)}  ·  face {SIZE}/{SMILE} gap {GAP} = '
      f'{WIDTH[SIZE]}x{FH} at ({16}, {CY})  ·  air {ABOVE} above / {BELOW} below')
print(f'  ramp {N} tones {RAMP[0]} -> {RAMP[-1]}')
print(f'  step dE {min(steps):.4f}-{max(steps):.4f}  (Plozz {PLOZZ_MAX:.4f})  '
      f'span dE {dE(RAMP[0], RAMP[-1]):.4f} (Plozz {dE(PLOZZ[0], PLOZZ[-1]):.4f})')
print(f'  visible px per tone outside the face: {vis}')
print(f'  area-weighted mean {MEAN_HEX} vs field {FIELD} '
      f'(dE {dE(MEAN_HEX, FIELD):.4f}) · face on core {CONTRAST:.1f}:1')
print(f'  {len({f for _, f in LAYERS})} distinct colours in the mark '
      f'(the face reuses the keyline)')

# --- emit ------------------------------------------------------------------
IDEA = ('The whole disc is the fade: eight steps of the Plozz inset bevel, palest '
        'at the rim and bluest in the middle, every step too small to see alone.')
assert "'" not in IDEA and "'" not in NAME, 'a quote here breaks the .meta.ts string'

body = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in LAYERS)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG[1:]} · {NAME}
 *
 * {IDEA}
 *
 * Brandon asked for "more gradual fade from the edges ... instead of 1 pixel of
 * lighting/shading, we have 3px of it", pointing at the Plozz TV, where the
 * screen "has more white around the edges and it gradually gets more blue
 * towards the center ... you barely notice it change colors ... and yet theyre
 * completely different colors."
 *
 * Plozz was rasterised to this grid and measured. Its screen carries three
 * tones — #97e3fe, #82deff, #72daff — one pixel a step on the flanks and two at
 * the corners, wrapping all four sides. The steps are 0.026 and 0.019 apart in
 * Oklab, and that step size is the thing worth copying, not the step count.
 *
 * So this keeps Plozz's step and lengthens the run: {N} tones, every neighbouring
 * pair {min(steps):.3f} apart — inside Plozz's own range — over a total travel of
 * {dE(RAMP[0], RAMP[-1]):.3f}, {dE(RAMP[0], RAMP[-1]) / dE(PLOZZ[0], PLOZZ[-1]):.1f}x Plozz's. Imperceptible steps, genuinely
 * different ends. The tone at each pixel is its distance to the outside of the
 * disc, cut at half-integers so one pixel of travel is always exactly one step;
 * on the diagonals the bands double to two, which is the corner thickening
 * measured off Plozz arriving on its own rather than being drawn in.
 *
 * A fade wrapping in from every edge of a circle is concentric, and concentric
 * bands are how a target is drawn. Two things stop it: the ramp is monotone, so
 * no ring is lighter than the rings either side of it, and the step is below
 * the size at which a band edge shows. Both are asserted in the generator —
 * every row and every column of the disc is checked to rise then fall with no
 * dip and no skipped tone.
 *
 * The ramp is positioned by its average, not by its ends. Hung off a near-white
 * rim it looked right at 96px and went ghostly at 24, because the pale outer
 * bands cover far more of the disc than the deep inner ones — {vis[0]} visible
 * pixels of the lightest against {vis[N - 1]} of the darkest — so the whole mark averaged
 * lighter than the flat {FIELD} its siblings use, and at small sizes the average
 * is all you get. It is now slid along its own axis until the area-weighted
 * mean of what you can actually see is exactly {FIELD}. c41 weighs the same as
 * the marks beside it; what differs is the distribution, not the level.
 *
 * The disc, the water and the size are c10's, untouched. The face is centred on
 * the disc rather than on the lit area, so the deepest blue pools under it the
 * way Mozz's banding runs behind its ZZ. Measured air on the disc: {ABOVE} above,
 * {BELOW} below. {WIDTH[SIZE]} wide on a {disc_w} wide disc, so it sits on x=16 whole.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {NAME}">
{body}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: '{SIZE}', smile: '{SMILE}', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

pal = "', '".join([KEY] + RAMP + ['#96bcd6', '#5d8cb0'])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG[1:]}', name: '{NAME}',
  idea: '{IDEA}',
  ground: 'light',
  palette: ['{pal}'],
}};
''')
print(f'  wrote {SLUG}.astro and {SLUG}.meta.ts')
