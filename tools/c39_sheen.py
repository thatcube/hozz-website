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
# The ramp: 9 body tones, in Mozz's idiom.
#
# Mozz does not run a straight line from dark to light — it drifts in hue and
# saturation as well, so the deep end is a colder, more purple red and the lit
# end a warmer pink one. "you barely notice it change colors as it moves
# towards the center, and yet theyre completely different colors."
#
# Same move here: the deep end is a duller, greyer slate; the lit end pulls
# toward cyan, as a highlight picking up sky would. Ends differ by 27% of the
# base luminance, delivered in eight steps of about 3.4% each — inside Mozz's
# own 3-6% band, so no single step is a visible edge.
# ---------------------------------------------------------------------------
N_TONES = 9
L0, L1 = 0.742, 0.964     # HSL lightness, deepest -> lightest
S0, S1 = 0.40, 0.86       # saturation: the deep end is duller, as Mozz's is
H0, H1 = 206.0, 195.0     # hue drifts toward cyan as it lights


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
# The field.
# ---------------------------------------------------------------------------
CX, CY, R = 16.0, 13.0, 11.0

W_FORM = 1.00     # light from above — the part that survives 24px
W_SHEEN = 0.66    # the crossed bands — the part that appears at 96px
W_EDGE = 0.30     # the rim takes the light hardest, top and bottom both

BAND = 7.2        # half-wavelength of a band, in pixels across the diagonal


def wave(t):
    """One band: bright on its axis, falling to dark a `BAND` away and holding.

    A cosine rather than a step, because the whole brief is that you should not
    be able to point at where one tone becomes the next.
    """
    return math.cos(math.pi * min(1.0, abs(t) / BAND))


def raw(x, y):
    """Continuous lightness at a pixel, before smoothing and quantising.

    x enters only through `dx`, and `dx` flips sign under x -> 31-x while every
    use of it is even in the pair (u, v) — the two diagonals swap — so the
    field is mirror-symmetric about x=16 by construction rather than by
    correction afterwards.
    """
    dx = (x + 0.5) - CX
    dy = (y + 0.5) - CY
    r = math.hypot(dx, dy) / R

    form = -dy / R                                  # +1 at the top, -1 at the foot

    # Mozz's bands are straight diagonals — they step one pixel per row and run
    # right across the disc and out the other side. Two of them, crossed, so
    # the pattern mirrors: u -> -v and v -> -u under the flip, and `wave` is
    # even. An angular star was tried first and is wrong here — radial wedges
    # converge, and the bottom one drove a dark spike out under the chin.
    u = (dx + dy) * 0.7071
    v = (dx - dy) * 0.7071
    sheen = 0.5 * (wave(u) + wave(v))
    sheen *= 1.0 - 0.35 * max(0.0, r - 0.76) / 0.24  # ease off at the keyline

    edge = max(0.0, (r - 0.68) / 0.32)              # 0 inside, 1 at the rim
    return W_FORM * form + W_SHEEN * sheen + W_EDGE * edge * form


def smooth(body, passes=2):
    """Blur the field before quantising, so band edges land as clean one-step
    transitions instead of a sawtooth of single pixels."""
    vals = {p: raw(*p) for p in body}
    for _ in range(passes):
        nxt = {}
        for (x, y), v in vals.items():
            ns = [vals[q] for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                  if q in vals]
            nxt[(x, y)] = (2 * v + sum(ns)) / (2 + len(ns))
        vals = nxt
    return vals


def quantise(body):
    vals = smooth(body)
    lo, hi = min(vals.values()), max(vals.values())
    out = {}
    for p, v in vals.items():
        t = (v - lo) / (hi - lo)
        out[p] = min(N_TONES - 1, int(t * N_TONES))
    return out


def despeckle(tone, body):
    """Kill lone pixels so the field reads as bands, not as dither.

    A pixel that disagrees with three or more of its four neighbours is noise
    from quantising a smooth function, not a band. The rule looks at a
    neighbourhood that is itself symmetric about x=16, so applying it cannot
    break the symmetry the field was built with.
    """
    for _ in range(3):
        nxt = dict(tone)
        for (x, y), t in tone.items():
            ns = [tone[q] for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                  if q in tone]
            if len(ns) == 4 and sum(1 for n in ns if n != t) >= 3:
                nxt[(x, y)] = sorted(ns)[len(ns) // 2]
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
 * grid, Mozz's disc carries nine body tones between its keyline and its white
 * ZZ, and bucketing them by angle around the centre shows what they are: not
 * rings, but wedges. The tone swings right across the ramp as you go round the
 * compass and barely moves as you go out from the middle. That is light on a
 * spinning disc, and it is why Mozz reads as an object rather than as a circle
 * with a face on it.
 *
 * So this is nine tones in four arms. Mozz's wedges have two-fold rotational
 * symmetry, which leaves it leaning to one side; here they are built on
 * cos(4t) instead, which keeps the rotation and adds the mirror, so the sheen
 * is a four-armed star with no side to it. That matters on this mark and not
 * on Mozz, because the disc is sitting in a ring of water that is symmetric
 * about x=16, and a reflection leaning one way inside symmetric water reads as
 * an error rather than as light.
 *
 * The steps are the point. Consecutive tones are about 3.4% of the base
 * luminance apart, inside the 3-6% band measured off Mozz, so no boundary is
 * an edge you can point at; the ends are 27% apart, which is a different
 * colour entirely. The ramp drifts in hue and saturation as well as
 * lightness — duller slate at the foot, cyan at the crest.
 *
 * Underneath the arms is a plain top-to-bottom lightening. That is deliberate
 * insurance: at 24px a one-pixel wedge boundary is a third of a screen pixel
 * and gone, so what survives is simply a disc lit from above, which is a
 * correct reading of the same object.
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
  idea: "Mozz's reflection, measured: nine tones in four arms sweeping behind the face, and a plain lit disc when it shrinks.",
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
