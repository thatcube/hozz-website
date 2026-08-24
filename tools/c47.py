"""
c47 · Ripple, Depth — the disc read as a thickness of water, not as a lit object.

Every other interior on the board is *lighting*: a bevel, an overhead fade, a
sheen sweeping one way. Lighting is directional, and directional shading is what
kept pulling the face off centre — a chin eats rows off the bottom of the field,
the field's middle stops being the disc's middle, and the face rides high.

So this one is not lit at all, it is refracted. Look at a photograph of a water
bead: it is darkest at its rim, because at grazing incidence the surface curves
away and bends your line of sight down into whatever the bead is sitting on, and
it is clearest face-on, where you look straight through. Colour is depth. The rim
is *the pool's own blue*, `#96bcd6`, so the bead dissolves into the water it sits
in; the middle is near-clear, which is where the face sits.

The mechanism is the cheapest honest one available. Peel nine successive
contour-following rings off the inside of the keyline and make each one a single
step paler. Because a ring is defined by which pixels have a missing neighbour,
every ring bends around the silhouette by construction, wraps it completely, and
mirrors about x=16 exactly. And because ring index changes by at most one
between orthogonal neighbours, **no two touching pixels can be more than one
tone apart** — which is Brandon's "seamlessly", enforced rather than eyeballed.

The steps are sized off Plozz. Its inset bevel runs #97e3fe → #82deff → #72daff,
about 7 units of luminance per step. This ramp runs #96bcd6 → #f5fafd across
nine stops at 8.6 units a step: near enough the same tread, walked nine times
instead of three, so the ends land on "completely different colors" without any
one step being visible.

Nine interior tones, against Plozz's eight, Mozz's eleven, and the five the
current Ripple marks carry.
"""
import re
import sys
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check  # noqa: E402
from shade import rings, keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 'c47'
NAME = 'Ripple, Depth'
IDEA = ('The disc read as a thickness of water — nine rings stepping from the '
        'pool\u2019s own blue at the rim to near-clear where the face sits.')

KEY = '#132638'

# ---------------------------------------------------------------- the fixtures

DISC = circle(22)          # 22 across, rows 2-23, centred on x=16
check(DISC)                # symmetric, no spurs

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

# --------------------------------------------------------------- the tone ramp
#
# Interpolating between two hex codes in sRGB gives uneven steps — the middle of
# a blue-to-white run bunches up and the ends spread out, which is exactly the
# banding the brief is trying to avoid. OKLab is near enough perceptually
# uniform that an even split of it is an even split to the eye, so the ramp is
# built there and only converted back at the end.


def _srgb_to_lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lin_to_srgb(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


def hex_to_oklab(h):
    r, g, b = (_srgb_to_lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_hex(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return '#%02x%02x%02x' % tuple(_lin_to_srgb(c) for c in (r, g, bb))


def ramp(a, b, n):
    """`n` stops from `a` to `b`, evenly spaced in OKLab."""
    la, lb = hex_to_oklab(a), hex_to_oklab(b)
    return [oklab_to_hex(tuple(la[i] + (lb[i] - la[i]) * (k / (n - 1))
                               for i in range(3))) for k in range(n)]


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# The rim is the pool's blue exactly. The middle stops a little short of white
# so the centre still carries colour rather than reading as a hole punched in
# the disc — the tile behind these is #fff.
#
# The disc yields ten depths but carries nine tones, because the last two are
# merged. Left separate, the deepest band is the four pixels at dead centre —
# and dead centre is the gap between the ZZ's eyes and its smile, so a tone of
# its own there renders as a highlight dot sitting in the middle of the face.
# Merged, the pale centre becomes a sixteen-pixel field the face sits in.
RIM, CLEAR, CAP = '#96bcd6', '#f5fafd', 8
TONES = ramp(RIM, CLEAR, CAP + 1)

# ------------------------------------------------------------------- the build

K = keyline(DISC)
INNER = DISC - K

# Depth two ways, and the shallower of the two wins.
#
# Erosion alone is safe but not round. This disc has six rows of full width down
# its middle, so peeling rings off it turns the inner contours into a rounded
# square — the "square inside a circle" that got an earlier mark rejected.
# Distance from the centre alone is round but not safe: the silhouette is not a
# true Euclidean circle, so the outermost band would break where the two
# disagree and leave raw field touching the keyline.
#
# `min` of the two keeps both properties. Erosion caps the depth near the rim,
# so band 0 still wraps the contour completely; distance governs further in,
# where the contours want to be circles. Both change by at most one between
# touching pixels, so their minimum does too.
CX, CY = 16.0, (min(p[1] for p in DISC) + max(p[1] for p in DISC) + 1) / 2
dist = {p: hypot(p[0] + 0.5 - CX, p[1] + 0.5 - CY) for p in INNER}
RMAX = max(dist.values())

RGS, CORE = rings(INNER, 9)
assert CORE, 'the disc is too small to carry this many rings'
erosion = {p: i for i, band in enumerate(RGS + [CORE]) for p in band}
assert erosion.keys() == INNER, 'the rings do not tile the disc'

level = {p: max(0, min(CAP, erosion[p], round(RMAX - dist[p]))) for p in INNER}
BANDS = [{p for p, v in level.items() if v == i} for i in range(CAP + 1)]
assert all(BANDS), 'a tone came out empty'
assert len(BANDS) == len(TONES)

# Seamlessness, asserted rather than eyeballed: touching pixels are never more
# than one tone apart, so there is no step in the mark bigger than 8.6 units of
# luminance.
for (x, y), v in level.items():
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        q = (x + dx, y + dy)
        if q in level:
            assert abs(level[q] - v) <= 1, f'{SLUG}: tone jump at {(x, y)}'

# Symmetry about x=16, every layer including the keyline.
for i, band in enumerate(BANDS + [K]):
    assert all((31 - x, y) in band for x, y in band), f'{SLUG}: band {i} not symmetric'

# ------------------------------------------------------------- face and centring
#
# Centred on the DISC, per the brief. A radial ramp is the one interior
# treatment that cannot bias this: it is symmetric top to bottom as well as left
# to right, so there is no chin to eat rows off the bottom of the field and pull
# the face up. The assertion below is still the thing that proves it.

WIDTH = {'lg': 10, 'md': 8, 'sm': 7}
GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
}
SIZE, GAP = 'md', 3                       # the settled face — only the inside changes

dxs = sorted({p[0] for p in DISC})
dys = sorted({p[1] for p in DISC})
disc_w = dxs[-1] - dxs[0] + 1
disc_mid2 = dys[0] + dys[-1] + 1

assert (disc_w - WIDTH[SIZE]) % 2 == 0, (
    f'{SLUG}: a {WIDTH[SIZE]}-wide face cannot centre on a {disc_w}-wide disc')
H, OFF = GEOM[SIZE][GAP]
assert (disc_mid2 - H) % 2 == 0, f'{SLUG}: a {H}-row face cannot centre on this disc'
CY = (disc_mid2 - H) // 2 - OFF
TOP = CY + OFF
ABOVE = TOP - dys[0]
BELOW = dys[-1] - (TOP + H - 1)
assert ABOVE == BELOW, f'{SLUG}: air {ABOVE}/{BELOW} on the disc'

# The parity rule, checked on the emitted geometry rather than trusted. mark.ts
# places the face at `left = round(cx - w/2)`, so an odd-width face lands off
# x=16 whatever cx it is given — which is why `sm` is not in GEOM above.
LEFT = round(16 - WIDTH[SIZE] / 2)
RIGHT = LEFT + WIDTH[SIZE] - 1
assert LEFT == 31 - RIGHT, f'{SLUG}: face spans {LEFT}-{RIGHT}, not centred on x=16'

# ------------------------------------------------------------------- the output

layers = [(WATER_OUT, '#96bcd6'), (WATER_IN, '#5d8cb0')]
layers += [(b, t) for b, t in zip(BANDS, TONES)]
layers += [(K, KEY)]

rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in layers)
palette = list(dict.fromkeys([KEY] + TONES + ['#5d8cb0', '#96bcd6']))

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG[1:]} · {NAME}
 *
 * {IDEA}
 *
 * Not a light source — a depth. Every other interior on the board shades the
 * disc as though something were shining on it, and lighting is directional:
 * a chin eats rows off the bottom of the field, the field's middle stops being
 * the disc's middle, and the face rides high. This one is Beer\u2013Lambert
 * instead. A bead of water is thick at the rim, where you look through a long
 * chord of it, and thin in the middle, where you look straight through. So the
 * rim is the pool's own blue, {RIM} \u2014 the bead dissolves into the water it
 * sits in \u2014 and it clears to {CLEAR} where the face sits.
 *
 * Nine tones, one per band of depth. Depth is measured two ways and the
 * shallower wins: contour erosion, which wraps the silhouette completely but
 * turns square in the middle, capped against distance from the centre, which is
 * round but does not follow the outline. Both change by at most one between
 * touching pixels, so their minimum does \u2014 meaning **no two touching
 * pixels are more than one tone apart**, and no step in the mark is bigger than
 * 8.6 units of luminance, near enough Plozz's inset-bevel tread walked nine
 * times instead of three. It is asserted rather than eyeballed.
 *
 * The two deepest bands are merged. Kept apart, the deepest is the four pixels
 * at dead centre \u2014 which is the gap between the ZZ's eyes and its smile,
 * so it renders as a highlight dot sitting in the middle of the face. Merged,
 * the pale centre is a field the face sits in.
 *
 * The face is the settled one, centred on the disc: {ABOVE} rows of air above,
 * {BELOW} below, measured on the disc and asserted in tools/{SLUG}.py. A radial
 * ramp is the only interior here that cannot bias that, being symmetric top to
 * bottom as well as left to right.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {NAME}">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: '{SIZE}', smile: 'wide', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / f'{SLUG}.meta.ts').write_text(
    "export default {\n"
    f"  n: '{SLUG[1:]}', name: '{NAME}',\n"
    f"  idea: '{IDEA}',\n"
    "  ground: 'light',\n"
    "  palette: [" + ', '.join(f"'{c}'" for c in palette) + "],\n"
    "};\n")

print(f'{SLUG} {NAME}')
print(f'  disc {len(dys)} rows x {disc_w} · face {SIZE} gap {GAP} = {H} rows · '
      f'air {ABOVE}/{BELOW}')
print(f'  {len(TONES)} interior tones + keyline + 2 water = {len(TONES) + 3}')
print('  ramp   ' + ' '.join(TONES))
print('  step L ' + ' '.join(f'{lum(TONES[i + 1]) - lum(TONES[i]):.1f}'
                             for i in range(len(TONES) - 1)))
print(f'  band sizes {[len(b) for b in BANDS]}')
print('  passed: silhouette symmetric about x=16 and free of spurs (circles.check)')
print(f'  passed: all {len(BANDS)} bands + keyline symmetric about x=16')
print('  passed: no two touching pixels more than one tone apart')
print(f'  passed: face parity — {WIDTH[SIZE]}-wide face on a {disc_w}-wide disc, '
      f'spanning x{LEFT}-{RIGHT}')
print(f'  passed: air equal on the disc — {ABOVE} above, {BELOW} below')

if '--show' in sys.argv:
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(dys[0], dys[-1] + 1):
        line = ''
        for x in range(32):
            if (x, y) in K:
                line += '#'
            elif (x, y) in level:
                line += '0123456789'[level[(x, y)]]
            else:
                line += '.'
        print(f'{y:3} ' + line)
