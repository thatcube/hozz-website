"""
c39 · Ripple, Sheen — the Mozz reflection, measured off Mozz and put on water.

Brandon asked for "how for mozz i have a cd and you can see the reflections,
but again, theyre subtle and have to blend seamlessly into the face." So the
first thing here was to go and read the shipped Mozz mark rather than guess
what a reflection looks like. Rasterised to the 32 grid it gives:

  11 colours   a near-black keyline (#3e0606), pure white for the ZZ, and
               **9 body tones** in between.
  tiny steps   consecutive body tones differ by 3-6% of the base luminance —
               #b00023 -> #c00026 -> #c80028 is the whole light end. Only the
               deepest accent takes a big jump, and it covers 21 pixels.
  angular      bucketing the body by angle around the disc centre shows the
               tone is a function of *angle*, not of radius: the mean tone
               swings 2.3 -> 7.4 across the compass while it moves only
               6.0 -> 4.4 from centre to rim. Mozz's sheen is a set of wedges
               radiating from the middle, which is what light on a spinning
               disc actually does.
  behind       nothing is cleared for the letterforms. The wedges run under
               the ZZ and out the other side, and that is what makes the face
               read as part of the record.

Where this departs from Mozz, deliberately. Mozz's wedges have two-fold
*rotational* symmetry — tone(t) == tone(t+180) — which makes it left-right
asymmetric. On Ripple the disc sits in a pool of concentric rings that are
mirror-symmetric about x=16, and a sheen leaning one way inside symmetric water
reads as a mistake rather than as light. So the wedges here are built on
cos(4t), which keeps Mozz's rotational symmetry *and* adds the mirror: four
arms on the diagonals, so every layer passes the symmetry assertion. It is the
specular star you get on a polished disc under one overhead light.

Two fields are summed, on purpose, because they survive different sizes:

  form   a gentle top-to-bottom lightening. This is the part that still reads
         at 24px, where a 1px wedge boundary is a third of a screen pixel and
         is gone. Downscaled, the mark is simply a disc lit from above.
  sheen  the four arms. This is the part that appears at 96px and is the thing
         Brandon is asking for.

The disc, the water and the size are c10's, untouched.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check  # noqa: E402
from shade import keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 'c39'
NAME = 'Ripple, Sheen'

# ---------------------------------------------------------------------------
# Fixed: the disc, and c10's water.
# ---------------------------------------------------------------------------
DISC = circle(22)
check(DISC)

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

KEY = '#132638'

# ---------------------------------------------------------------------------
# The ramp: Mozz's own count, eleven tones, built in Mozz's idiom.
#
# Mozz does not run a straight line from dark to light — it drifts in hue and
# saturation as well, so the deep end is a colder, more purple red and the lit
# end a warmer pink one. "you barely notice it change colors as it moves
# towards the center, and yet theyre completely different colors."
#
# Same move here: the deep end is a duller, greyer slate; the lit end pulls
# toward cyan, as a highlight picking up sky would. Consecutive steps sit at
# 4-5% of the base luminance — inside the 3.3-9.1% band measured off Mozz — so
# no single step is an edge you can point at, while the ends are 45% apart,
# which is a different colour entirely. Mozz's own span is 56%.
# ---------------------------------------------------------------------------
N_TONES = 11
L0, L1 = 0.685, 0.965     # HSL lightness, deepest -> lightest
S0, S1 = 0.36, 0.88       # saturation: the deep end is duller, as Mozz's is
H0, H1 = 208.0, 194.0     # hue drifts toward cyan as it lights


def hsl(h, s, l):
    c = (1 - abs(2 * l - 1)) * s
    hp = (h % 360) / 60.0
    x = c * (1 - abs(hp % 2 - 1))
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x),
               (0, x, c), (x, 0, c), (c, 0, x)][int(hp) % 6]
    m = l - c / 2
    return '#%02x%02x%02x' % tuple(round(255 * (v + m)) for v in (r, g, b))


RAMP = [hsl(H0 + (H1 - H0) * t, S0 + (S1 - S0) * t, L0 + (L1 - L0) * t)
        for t in [i / (N_TONES - 1) for i in range(N_TONES)]]


def lum(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b


# ---------------------------------------------------------------------------
# The field: a lit body, plus a sheen that only ever *adds* light.
#
# The second half of that is the load-bearing idea. A reflection is light
# arriving, never light removed, so the sheen is a non-negative offset laid
# over the body. Written that way it cannot cut a dark notch into the disc —
# the first version of this made the sheen bipolar and its dark lobe drove a
# two-pixel spike out from under the chin, four tones away from its
# surroundings. Additive, that whole class of defect is unreachable.
# ---------------------------------------------------------------------------
CX, CY, R = 16.0, 13.0, 11.0

BASE = 3.2        # where the unlit body sits on the ramp
W_KEY = 3.6       # light from above: the part that survives 24px
W_DOME = 2.2      # the sphere's own falloff, so the shading follows the rim
AMP = 3.0         # how far the sheen can lift a pixel, in ramp steps
R0, R1 = 0.06, 0.70   # the sheen fades in away from the centre

# The arm profile, indexed by distance from a band's axis in whole pixels.
# Flat-topped and then easing off, so the bright core is wide enough to read as
# a band rather than as a line, and the falloff is one ramp step at a time.
ARM = [1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.45, 0.2, 0.05, 0.0]


def arm(n):
    return ARM[min(abs(n), len(ARM) - 1)]


def field(x, y):
    """The tone at a pixel, as a ramp index.

    Symmetry is structural, not corrected afterwards. The two band indices are
    n1 = x + y - 28 and n2 = x - y - 3; under x -> 31 - x they swap and negate
    (n1 -> -n2, n2 -> -n1), and `arm` is even, so max(arm(n1), arm(n2)) is
    invariant. Because they are integers the band boundaries land exactly on
    pixel edges and come out as clean 45-degree staircases — which is how
    Mozz's bands are actually drawn, one pixel of step per row.
    """
    dx = (x + 0.5) - CX
    dy = (y + 0.5) - CY
    r = min(1.0, math.hypot(dx, dy) / R)

    # A sphere's own shading: brightest where the surface faces the light,
    # falling off toward the rim in every direction. Iso-lines follow the
    # circle, so quantising it gives contour bands rather than the horizontal
    # stripes a plain top-to-bottom gradient produces.
    dome = math.sqrt(max(0.0, 1.0 - r * r))
    body = BASE + W_KEY * (-dy / R) + W_DOME * dome

    # Four arms, on the diagonals. Mozz's are a single parallel family, which
    # leaves it leaning; crossing two families keeps the straight diagonal
    # edges and adds the mirror.
    mask = min(1.0, max(0.0, (r - R0) / (R1 - R0)))
    sheen = AMP * max(arm(x + y - 28), arm(x - y - 3)) * mask

    return int(round(body)) + int(round(sheen))


def quantise(body):
    tone = {p: max(0, min(N_TONES - 1, field(*p))) for p in body}
    lo = min(tone.values())
    return {p: t - lo for p, t in tone.items()}   # sit the field on the ramp


def despeckle(tone, body):
    """Kill lone pixels so the field reads as bands, not as dither.

    A pixel that matches none of its four neighbours is a rounding artefact,
    not a band. The rule looks at a neighbourhood that is itself symmetric
    about x=16, so applying it cannot break the symmetry the field was built
    with — the assertions downstream re-check that.
    """
    for _ in range(4):
        nxt = dict(tone)
        for (x, y), t in tone.items():
            ns = [tone[q] for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                  if q in tone]
            if len(ns) == 4 and t not in ns:
                nxt[(x, y)] = sorted(ns)[2]
        if nxt == tone:
            break
        tone = nxt
    return tone


# ---------------------------------------------------------------------------
# Face placement: centred on the DISC, and even-width only.
# ---------------------------------------------------------------------------
SIZE = 'md'                      # 8 wide. `sm` is 7 and cannot centre on 22.
WIDTH = {'lg': 10, 'md': 8, 'sm': 7}
GEOM = {
    'lg': {1: (10, -5), 2: (11, -5), 3: (12, -6), 4: (13, -6)},
    'md': {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)},
}[SIZE]


def place():
    dys = sorted({p[1] for p in DISC})
    disc_mid2 = dys[0] + dys[-1] + 1
    disc_w = max(p[0] for p in DISC) - min(p[0] for p in DISC) + 1
    assert (disc_w - WIDTH[SIZE]) % 2 == 0, (
        f'a {WIDTH[SIZE]}-wide face cannot centre on a {disc_w}-wide disc')
    for gap in (3, 1, 2, 4):
        if gap not in GEOM:
            continue
        h, off = GEOM[gap]
        if (disc_mid2 - h) % 2:
            continue                       # an odd-height face cannot halve the air
        cy = (disc_mid2 - h) // 2 - off
        top = cy + off
        above, below = top - dys[0], dys[-1] - (top + h - 1)
        assert above == below, f'air {above}/{below} on the disc'
        return gap, h, cy, above, below, dys
    raise SystemExit('no gap centres the face on the disc')


def build():
    key = keyline(DISC)
    inner = DISC - key
    tone = despeckle(quantise(inner), inner)

    layers = [(WATER_OUT, '#96bcd6'), (WATER_IN, '#5d8cb0')]
    used = []
    for i, fill in enumerate(RAMP):
        px = {p for p, t in tone.items() if t == i}
        if px:
            layers.append((px, fill))
            used.append(fill)
    layers.append((key, KEY))

    # Every layer inside the circle mirrors about x=16. The sheen is
    # directional in the sense that it has arms, but the arms come in a
    # four-fold set, so there is no side to it.
    for px, fill in layers:
        if fill in used + [KEY]:
            assert all((31 - x, y) in px for x, y in px), f'{fill} not symmetric'
    assert all((31 - x, y) in inner for x, y in inner), 'interior not symmetric'
    assert set().union(*[p for p, f in layers if f in used]) == inner, 'gaps in the field'

    gap, h, cy, above, below, dys = place()

    steps = [100 * (lum(b) - lum(a)) / lum(RAMP[0]) for a, b in zip(used, used[1:])]
    jump = max(abs(tone[p] - tone[q])
               for p in tone for q in ((p[0] + 1, p[1]), (p[0], p[1] + 1))
               if q in tone)
    print(f'{SLUG} {NAME}')
    print(f'  disc {dys[-1] - dys[0] + 1} rows (y{dys[0]}-{dys[-1]}) · '
          f'face {SIZE} gap {gap} = {h} rows · air {above}/{below}')
    print(f'  {len(used)} body tones + keyline = {len(used) + 1} inside the circle')
    print(f'  steps: {" ".join(f"{s:.1f}%" for s in steps)}  '
          f'(max {max(steps):.1f}%, Mozz maxes at 9.1% ignoring its deep accent)')
    print(f'  biggest jump between neighbouring pixels: {jump} level(s) '
          f'= {jump * max(steps):.1f}%')
    for i, f in enumerate(used):
        n = sum(1 for t in tone.values() if RAMP[t] == f)
        print(f'    {i} {f}  lum {lum(f):5.1f}  {n:3} px  ' + '#' * (n // 3))

    show(tone, inner, cy, gap)

    rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />'
                     for p, f in layers)
    (OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * 39 · {NAME}
 *
 * The Mozz reflection, measured and moved onto water. Rasterised to the 32
 * grid, Mozz's disc carries eleven colours: a near-black keyline, white for the
 * ZZ, and nine body tones. Bucketing those by angle around the centre says what
 * they are — not rings, but bands. The mean tone swings 2.3 to 7.4 right around
 * the compass and moves only 6.0 to 4.4 from the centre out to the rim. Mozz's
 * sheen is a function of angle, not of radius, which is what light on a
 * spinning disc actually does, and it is why Mozz reads as an object rather
 * than as a circle with a face on it.
 *
 * So: eleven tones here too, in four straight-edged arms. The arms are built on
 * the integer diagonals x+y and x-y, so their boundaries land on pixel edges
 * and come out as 45-degree staircases stepping one pixel per row — Mozz's
 * bands are drawn exactly that way. Where this departs from Mozz is on purpose.
 * Mozz's bands are one parallel family with two-fold rotational symmetry, which
 * leaves the whole mark leaning to one side. This disc sits in a pool of rings
 * that are mirror-symmetric about x=16, and a sheen leaning one way inside
 * symmetric water reads as a mistake rather than as light, so the two diagonal
 * families are crossed. Under x -> 31-x they swap and negate and the arm
 * profile is even, so every layer mirrors by construction.
 *
 * The sheen only ever adds. A reflection is light arriving, never light
 * removed, and writing it as a non-negative offset over the lit body makes a
 * whole class of defect unreachable — the first cut of this was bipolar and its
 * dark lobe punched a two-pixel notch out from under the chin.
 *
 * The steps are the point. Consecutive tones are 4.0-5.0% of the base
 * luminance apart, inside the 3.3-9.1% band measured off Mozz, so no boundary
 * is an edge you can point at, and no two touching pixels are ever more than
 * two steps apart. The ends are 45% apart, which is a different colour
 * entirely; Mozz's own span is 56%. The ramp drifts in hue and saturation as
 * well as lightness — duller slate at the foot, cyan at the crest.
 *
 * Underneath the arms is a sphere's own falloff rather than a flat top-to-
 * bottom gradient, so the shading follows the rim instead of banding into
 * horizontal stripes. That is the part that survives 24px, where a one-pixel
 * arm boundary is a third of a screen pixel and gone: downscaled, this is
 * simply a disc lit from above, which is a correct reading of the same object.
 *
 * Nothing is cleared for the face. The arms run under the ZZ and out the other
 * side, exactly as Mozz's do, and the face is centred on the disc rather than
 * on the lit part of it — {above} rows of air above, {below} below.
 *
 * The disc, the water and the size are c10's, untouched.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {NAME}">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {cy}, size: '{SIZE}', smile: 'wide', gap: {gap} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

    pal = [KEY, used[0], used[2], used[4], used[6], used[-1], '#96bcd6']
    (OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG[1:]}', name: '{NAME}',
  idea: "Mozz's reflection, measured: eleven tones in four straight-edged arms running behind the face, adding light and never taking it, and a plainly lit disc once it shrinks.",
  ground: 'light',
  palette: {pal!r},
}};
'''.replace("'", "'").replace('"', '"'))


def show(tone, inner, cy, gap):
    face = set()
    top = cy - 5 if gap == 3 else cy - 4
    print()
    print('     ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(2, 24):
        line = ''
        for x in range(32):
            line += str(tone[(x, y)]) if (x, y) in tone else (
                '#' if (x, y) in DISC else '.')
        print(f'{y:3}  {line}')
    print()


if __name__ == '__main__':
    build()
    print('done')
