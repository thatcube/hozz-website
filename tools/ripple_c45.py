"""
c45 — Ripple, Lens. The compact face, and the room it buys spent on a meniscus.

Brandon asked for "a smaller smiley zz more compact zz smile". The obvious
reading is `sm`, and it is wrong: `sm` is 7 wide, the disc is 22 across, and a
7-wide face lands on x=16.5 — the half-pixel lean he has already caught once.
So "smaller" here is `md` (8 wide, even, centres exactly) with the **compact**
smile — 2 rows instead of 3, 6 across instead of 8 — and the family's default
gap of 2 rather than the gap of 3 the other Ripples were pushed to.

That is the whole argument of this mark. The other Ripples run md/wide/gap3 —
ten rows of face on a twenty-two row disc, six of air either side. This one is
eight rows, seven of air either side. The two rows it gives back are spent
inward, on the thing Brandon actually pointed at:

  "this tv has more white around the edges and it gradually gets more blue
   towards the center ... you barely notice it change colors as it moves
   towards the center, and yet theyre completely different colors"

Plozz does that in three steps because a TV screen has a bezel eating its room.
A bare disc has more, and a smaller face leaves more still, so this runs the
ramp over **six** tones: a near-white meniscus just inside the keyline falling,
one small step at a time, to a core that has very nearly caught up with the
colour of the water the disc is sitting in. Rim #f2f9fd to core #a6cbe4 — put
those two side by side and they are not the same colour at all; put the six in
order and no single step announces itself.

Every ring comes out of `rings()`, so it follows the contour and wraps all four
sides — an inset bevel like Plozz's, not a top highlight. The face sits on the
plain core, as it does on both shipped marks, and the ramp passes behind its
corners rather than being cleared for it.

Nothing outside the disc changes: c10's two rings of water, lifted pixel for
pixel, and the canonical 22-across circle.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check  # noqa: E402
from shade import rings, keyline, to_paths, is_slab, show  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 'c45'
NAME = 'Ripple, Lens'

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
WATER_OUT_FILL, WATER_IN_FILL = '#96bcd6', '#5d8cb0'

# ---------------------------------------------------------------------------
# The ramp. Six stops, rim to core, interpolated so no step is louder than its
# neighbours. The core lands on the same weight as the water's own #96bcd6 and
# a little bluer, so the middle of the disc has very nearly caught the colour
# of the pool it is sitting in — which is what makes it read as something the
# light passes through rather than a painted counter.
#
# Two constructions were rendered side by side before this one was kept:
# contour rings from `rings()`, and bands quantised by radius from the disc's
# centre. Radial bands mottle — the canonical raster circle is not a euclidean
# one, so the quantisation leaves visible patches at the diagonals. The contour
# rings come out even, which is the whole reason shade.py builds shading from
# the silhouette rather than from geometry.
#
# Six is also the ceiling here, not a shortfall of nerve. A seventh ring erodes
# the core to an 8x8 blob that `is_slab` correctly rejects — a soft square
# sitting inside a circle — and it would push the face off its plain field.
# ---------------------------------------------------------------------------
RIM, CORE = (0xed, 0xf6, 0xfc), (0x96, 0xc2, 0xe0)
STEPS = 6


def lerp(a, b, t):
    return round(a + (b - a) * t)


RAMP = ['#%02x%02x%02x' % tuple(lerp(RIM[c], CORE[c], i / (STEPS - 1)) for c in range(3))
        for i in range(STEPS)]

# Subtlety: no single step may jump more than this on any channel. Plozz's own
# #97e3fe -> #82deff -> #72daff steps by 21 at the widest, so this is inside
# the standard set by the shipped mark.
MAX_STEP = 18
for a, b in zip(RAMP, RAMP[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= MAX_STEP, f'{a}->{b} steps by {d}, which reads as a band'

# ---------------------------------------------------------------------------
# Layers: keyline, then five contour-following rings, then the core.
# ---------------------------------------------------------------------------
K = keyline(DISC)
inner = DISC - K
bands, core = rings(inner, STEPS - 1)
LAYERS = [(WATER_OUT, WATER_OUT_FILL), (WATER_IN, WATER_IN_FILL)]
LAYERS += [(core, RAMP[-1])] + [(b, RAMP[i]) for i, b in enumerate(bands)][::-1]
LAYERS += [(K, KEY)]

# Every layer inside the disc must mirror about x=16, and none may be a slab
# floating in the middle of the shape.
for px, fill in LAYERS:
    if fill in (WATER_OUT_FILL, WATER_IN_FILL):
        continue
    assert px, f'{fill} is empty'
    assert all((31 - x, y) in px for x, y in px), f'{fill} is not symmetric about x=16'
    assert not is_slab(px, DISC), f'{fill} reads as a slab dropped in the disc'

# The ramp must tile the disc exactly: no bare pixels, no double paint.
covered = set()
for px, fill in LAYERS[2:]:
    assert not (covered & px), f'{fill} overlaps a layer already painted'
    covered |= px
assert covered == DISC, 'the disc is not exactly covered by its layers'

tones = {f for _, f in LAYERS}
assert len(tones) >= 6, f'only {len(tones)} tones'

# ---------------------------------------------------------------------------
# The face. md, compact, gap 2.
#
# The brief's height table covers md/**wide** only. These are the md/**compact**
# numbers, measured here rather than computed, because an even-height face is
# not symmetric about cy and computing it is how the off-by-one keeps happening:
#
#   md/compact:  gap1 (7, -3)  gap2 (8, -4)  gap3 (9, -4)  gap4 (10, -5)
#
# (height, top offset from cy). The disc is 22 rows, so only an even height can
# split its air evenly: gap 2 and gap 4. Gap 2 is the family default and the
# tighter of the two, which is the point of this mark, and it is a full two rows
# shorter than the md/wide/gap3 the other Ripples had to use.
#
# `measure()` reads the numbers back out of mark.ts itself, so the table above
# is checked rather than trusted.
# ---------------------------------------------------------------------------
GEOM_MD_COMPACT = {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)}
FACE_W = 8
GAP = 2


def measure(cx, cy, size, smile, gap):
    """faceBoxAt/facePathsAt, straight out of mark.ts — never reimplemented."""
    js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
          f"const o={{cx:{cx},cy:{cy},size:'{size}',smile:'{smile}',gap:{gap}}};"
          "console.log(JSON.stringify({box: faceBoxAt(o), paths: facePathsAt(o)}));")
    out = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e', js],
        capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    face = set()
    for d in got['paths']:
        face |= pixels(d)
    return got['box'], face


dxs = sorted({p[0] for p in DISC})
dys = sorted({p[1] for p in DISC})
disc_w = dxs[-1] - dxs[0] + 1
disc_h = dys[-1] - dys[0] + 1
assert (disc_w - FACE_W) % 2 == 0, (
    f'a {FACE_W}-wide face cannot centre on a {disc_w}-wide disc')

H, OFF = GEOM_MD_COMPACT[GAP]
assert (disc_h - H) % 2 == 0, f'a {H}-row face cannot split {disc_h} rows evenly'
CY = (dys[0] + dys[-1] + 1 - H) // 2 - OFF

box, FACE = measure(16, CY, 'md', 'compact', GAP)
assert (box['h'], box['y'] - CY) == (H, OFF), (
    f"mark.ts says {(box['h'], box['y'] - CY)}, the table says {(H, OFF)}")
assert box['w'] == FACE_W, f"mark.ts says the face is {box['w']} wide"

top = box['y']
above, below = top - dys[0], dys[-1] - box['bottom']
assert above == below, f'air {above}/{below} on the disc'
assert box['x'] + box['right'] == 31, 'face is not centred on x=16'
assert FACE <= DISC, 'face hangs off the disc'
# The face is *not* a mirror-symmetric layer and must not be asserted as one: a
# Z does not mirror. The family signature is two identical Zs repeated by
# translation, and on md that translation is 5. The smile does mirror.
eyes = {p for p in FACE if p[1] < top + 4}
smile = {p for p in FACE if p[1] >= box['bottom'] - 1}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert {(x + 5, y) for x, y in eyes if x < 16} == {p for p in eyes if p[0] >= 16}, (
    'the two Zs are not the same letter')
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric about x=16'
# Both shipped marks keep the field under the face plain; the ramp passes
# behind the disc, not under the letterforms.
assert FACE <= core, 'the face does not sit entirely on the plain core'

print(f'{SLUG} {NAME}')
print(f'  disc {disc_w}x{disc_h} rows {dys[0]}-{dys[-1]} · face md/compact gap{GAP} '
      f'= {FACE_W}x{H} at x{box["x"]}-{box["right"]}, y{top}-{box["bottom"]}, cy={CY}')
print(f'  air {above} above / {below} below · {len(tones)} tones · ramp {" ".join(RAMP)}')

if '--show' in sys.argv:
    show([p for p, _ in LAYERS] + [FACE],
         ['~', '=', '6', '5', '4', '3', '2', '1', '#', '@'])

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in LAYERS)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG[1:]} · {NAME}
 *
 * The compact face, and the room it buys spent on the light.
 *
 * "Smaller" is not `sm` here. `sm` is 7 wide and the disc is 22 across, so a
 * 7-wide face sits on x=16.5 — half a pixel left of centre, which is visible.
 * This is `md` with the **compact** smile: two rows instead of three, six
 * across instead of eight, at the family's default gap of two rather than the
 * three the other Ripples needed. Eight rows of face on a twenty-two row disc,
 * against their ten.
 *
 * The two rows it gives back are spent inward. A near-white meniscus sits just
 * inside the keyline and falls to the core over six tones, one small step at a
 * time — an inset bevel wrapping all four sides, the way Plozz's screen does
 * it, but with twice the room to do it in. The rim and the core are not the
 * same colour by any measure; no single step between them announces itself.
 * The core has very nearly caught the colour of the water the disc is sitting
 * in, so the disc reads as something the light passes through.
 *
 * Nothing is cleared for the letterforms — Mozz's rule, and the reason its ZZ
 * reads as the middle of the record instead of something dropped on it. Here
 * the arithmetic is kind: the compact face is exactly the size of the flat core
 * the six rings enclose, so it sits on a plain field with the ramp starting at
 * its edge. The face is centred on the **disc**: {above} rows of air above,
 * {below} below, measured.
 *
 * {len(tones)} tones. c10's water, unchanged, and the canonical 22-across circle.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Hozz — {NAME}">
{rows}
  <g fill="{KEY}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: 'md', smile: 'compact', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in [KEY, WATER_IN_FILL, WATER_OUT_FILL, *RAMP[::-1]])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG[1:]}', name: '{NAME}',
  idea: 'The compact smile on the same disc, and the room it buys spent inward: six tones fading from a near-white rim to a core the colour of the water.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
