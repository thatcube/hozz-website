"""
c43 · Ripple, Porthole — a double border around the ZZ.

Brandon's line was four words long: *"maybe try another with a double border
around the zz."* This is what that means on this object.

The reference is Plozz, and it is worth reading the actual pixels rather than
the idea of them. Plozz's face does not sit on the front of the TV; it sits
inside a recessed screen, and reading inward from the case that screen is built
out of five things:

    row 15   ..0220341111001111001111430220..
               ^  ^ ^                 ^ ^  ^
               |  | |                 | |  keyline
               |  | +- lightest #97e3fe    case
               |  +--- BLACK BEZEL         bezel
               +------ case #00a4dc        case
                                           field #72daff

That is: outer black line, a band of case, a second black line, then a bevel
that steps lightest → light → field. **Two dark lines with a lit band between
them.** The family already has a double border; it is rectangular because a TV
is. Bend it round a circle and you get this mark.

So the interpretation here is not a panel drawn around the letterforms — a
rounded rectangle inside a circle reads as a badge stuck on, and the point of
the ZZ is that it belongs to the thing it is on. The double border *is* the
disc's own edge, doubled: the keyline it already had, and a second line one
step in, with the rim between them catching light from above.

Everything inside the inner line is then given over to air. The bevel ramps in
four steps of a few points each — #f2fafe, #e8f4fb, #ddeef7, #d4e7f2 — down to
the field the face floats on, which is Brandon's TV note exactly: whitest at the
edge, and it gets bluer towards the centre without you seeing it happen.

The face is `md` at gap 1 — eight rows rather than the ten c10/c18/c19 use. A
border eats air, and the client has said more than once that the ZZ has to
float. Buying those two rows back from the face's own height is cheaper than
taking them out of the margin: it leaves seven clear rows above and below the
face on the disc, three clear pixels beside it on its own rows, and 2.61px at
the nearest point of the inner border — which is the air Plozz leaves round its
ZZ. Rendered at gap 3 the same construction closes to 1.83px and the eyes sit on
the border; that was measured and rejected, not assumed.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check            # noqa: E402
from shade import rings, to_paths            # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 'c43'
NAME = 'Ripple, Porthole'
IDEA = ("The edge of the disc, doubled: a second border one step inside the "
        "first, with the rim caught between them lit from above and the face "
        "floating clear in the middle.")
# The meta file quotes these in single quotes, so an apostrophe breaks the build.
assert "'" not in NAME + IDEA, f'{SLUG}: apostrophe in the name or idea'

# --- the fixed parts --------------------------------------------------------
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
W_OUT, W_IN = '#96bcd6', '#5d8cb0'

DISC = circle(22)
check(DISC)
DYS = sorted({p[1] for p in DISC})
DXS = sorted({p[0] for p in DISC})

# --- tones ------------------------------------------------------------------
# Two borders in the same ink as the face, because Plozz's bezel is the same
# black as its keyline and its ZZ. The rim between them is a mid tone graded
# top to bottom, so the border reads as a lit edge and not as a drawn line.
KEY = '#132638'
RIM = ['#bcd6ea', '#b0cde4', '#a4c4de', '#98bbd7']
# Inside the inner border: the bevel's catch, then four small steps down to the
# field. Largest step is 10 points in one channel — you have to look for it.
BEVEL = ['#f2fafe', '#e8f4fb', '#ddeef7', '#d4e7f2']
FIELD = '#cfe3ef'

RGS, CORE = rings(DISC, 7)
R = RGS + [CORE]


def grade(pix, tones):
    """Band a ring top to bottom. Split by y only, so it stays mirrored on x."""
    lo, hi = DYS[0], DYS[-1]
    n = len(tones)
    out = [set() for _ in tones]
    for x, y in pix:
        out[min(n - 1, int((y - lo) * n / (hi - lo + 1)))].add((x, y))
    return [(p, t) for p, t in zip(out, tones) if p]


BORDER_OUT, BORDER_IN = R[0], R[2]
LAYERS = ([(WATER_OUT, W_OUT), (WATER_IN, W_IN), (BORDER_OUT, KEY)]
          + grade(R[1], RIM)
          + [(BORDER_IN, KEY),
             (R[3], BEVEL[0]), (R[4], BEVEL[1]), (R[5], BEVEL[2]),
             (R[6], BEVEL[3]), (R[7], FIELD)])

# --- the face ---------------------------------------------------------------
# Even widths only: the disc is 22 across, so a 7-wide `sm` face lands on
# x=16.5 whatever cx it is given. `md` is 8 and centres exactly.
SIZE, SMILE = 'md', 'wide'
WIDTH = {'lg': 10, 'md': 8, 'sm': 7}[SIZE]
disc_w = DXS[-1] - DXS[0] + 1
assert (disc_w - WIDTH) % 2 == 0, \
    f'{SLUG}: a {WIDTH}-wide face cannot centre on a {disc_w}-wide disc'

# Measured heights, not computed — an even-height face is not symmetric about cy.
GEOM = {1: (8, -4), 2: (9, -4), 3: (10, -5), 4: (11, -5)}
disc_mid2 = DYS[0] + DYS[-1] + 1

# Gap 1 first: the shortest face, which is the most air a border can be given.
CHOICE = None
for gap in (1, 3, 2, 4):
    h, off = GEOM[gap]
    if (disc_mid2 - h) % 2:
        continue
    CHOICE = (gap, h, (disc_mid2 - h) // 2 - off)
    break
assert CHOICE, f'{SLUG}: no gap centres on a {len(DYS)}-row disc'
GAP, H, CY = CHOICE
TOP = CY + GEOM[GAP][1]
ABOVE, BELOW = TOP - DYS[0], DYS[-1] - (TOP + H - 1)
assert ABOVE == BELOW, f'{SLUG}: air {ABOVE}/{BELOW} on the disc'

# --- the face's own pixels, for the clearance assertion ---------------------
EYES = [[(0, 2), (5, 7)], [(1, 2), (6, 7)], [(0, 1), (5, 6)], [(0, 2), (5, 7)]]
SM_WIDE = [[(0, 0), (7, 7)], [(0, 1), (6, 7)], [(1, 6)]]
FACE = set()
for i, runs in enumerate(EYES + [[] for _ in range(GAP)] + SM_WIDE):
    for a, b in runs:
        FACE |= {(16 - WIDTH // 2 + a + k, TOP + i) for k in range(b - a + 1)}
# The ZZ itself is two identical Zs, not a mirrored pair — a mirrored Z is an S
# — so the letterforms cannot be tested for mirror symmetry. What must be true
# is that the box they occupy is centred on x=16.
fx = sorted({p[0] for p in FACE})
assert fx[0] + fx[-1] == 31 and fx[-1] - fx[0] + 1 == WIDTH, \
    f'{SLUG}: the face sits at x {fx[0]}-{fx[-1]}, not centred on 16'


def clear_to(layer):
    """Straight-line clearance between the face's ink and a layer, in pixels.

    Chebyshev is the wrong measure on a round object: it counts a diagonal step
    as one, so it reports the corner of the ZZ as nearly touching a ring that is
    plainly three and a half pixels away. This is the distance the eye reads.
    """
    return min(math.hypot(x - u, y - v)
               for x, y in FACE for u, v in layer) - 1


def beside(layer):
    """Clear pixels between the face and a layer along the face's own rows."""
    left = {}
    for x, y in FACE:
        left[y] = min(left.get(y, 99), x)
    rows_ = {}
    for x, y in layer:
        if x < 16:
            rows_[y] = max(rows_.get(y, -99), x)
    return min(left[y] - rows_[y] - 1 for y in left if y in rows_)


# --- assertions -------------------------------------------------------------
for px, fill in LAYERS:
    assert all((31 - x, y) in px for x, y in px), f'{SLUG}: {fill} not mirrored'

TONES = [f for _, f in LAYERS]
assert len(set(TONES)) >= 6, f'{SLUG}: only {len(set(TONES))} tones'


def step(a, b):
    return max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))


RAMPS = [RIM, BEVEL + [FIELD]]
STEPS = [step(a, b) for r in RAMPS for a, b in zip(r, r[1:])]
for r in RAMPS:
    for a, b in zip(r, r[1:]):
        assert step(a, b) <= 14, f'{SLUG}: {a}->{b} steps {step(a, b)} — that bands'

# Plozz keeps three clear pixels between its ZZ and the bezel around it. Hold to
# that: three beside the face, and no less than two and a half anywhere at all.
CLEAR, BESIDE = clear_to(BORDER_IN), beside(BORDER_IN)
assert BESIDE >= 3, f'{SLUG}: only {BESIDE}px beside the face — the border crowds it'
assert CLEAR >= 2.5, f'{SLUG}: the inner border closes to {CLEAR:.2f}px of the face'

print(f'{SLUG} {NAME:18} disc {len(DYS)} rows · face {SIZE} gap {GAP} = {H} rows '
      f'· air {ABOVE}/{BELOW} · {len(set(TONES))} tones · inner border {BESIDE}px '
      f'beside the face, {CLEAR:.2f}px at the nearest point '
      f'· largest ramp step {max(STEPS)}')

# --- write ------------------------------------------------------------------
rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />'
                 for p, f in LAYERS)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG[1:]} · {NAME}
 *
 * {IDEA}
 *
 * Plozz's face sits inside a recessed screen, and that screen is a double
 * border already: black keyline, a band of case, a second black line, then a
 * bevel stepping lightest → light → field. This is that construction bent
 * round a circle. It is deliberately not a panel drawn around the letterforms
 * — a rounded rectangle inside a circle reads as a badge stuck on the front,
 * and the ZZ is meant to belong to the thing it is on.
 *
 * So the two borders are the disc's own edge and a second line one step inside
 * it, in the same ink as the face. The rim caught between them is graded top to
 * bottom over four close tones, so it reads as an edge with light on it rather
 * than as a drawn ring.
 *
 * Everything inside the inner border is air. The bevel ramps down in four steps
 * of a few points each to the field the face floats on — whitest against the
 * border, bluer towards the middle, which is the fade Brandon pointed at on the
 * TV. {len(set(TONES))} tones, largest step in either ramp {max(STEPS)} points in one channel.
 *
 * The face is `md` at gap {GAP} — {H} rows, not ten. A border eats the air the ZZ
 * needs, and taking those rows out of the face's own height rather than out of
 * its margin is what keeps it floating: {ABOVE} clear rows above and {BELOW} below on
 * the disc, {BESIDE} clear pixels beside the face on its own rows, and {CLEAR:.2f}px at the
 * nearest point of the inner border — the same air Plozz leaves round its ZZ.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {NAME}">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: '{SIZE}', smile: '{SMILE}', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG[1:]}', name: '{NAME}',
  idea: '{IDEA}',
  ground: 'light',
  palette: ['{KEY}', '{RIM[0]}', '{RIM[3]}', '{BEVEL[0]}', '{FIELD}', '{W_OUT}'],
}};
''')
print(f'wrote {SLUG}.astro and {SLUG}.meta.ts')
