"""
t13 — Glass, cast. A speech bubble made of something the light goes *through*.

The chosen Hozz mark (c45) is opaque: a monotonic ramp, light rim falling to a
deeper core, which is what light *falling on* a curved surface looks like. Glass
is the other case — light enters an edge, crosses the body and leaves somewhere
else — and the way you tell the two apart in a picture is that a transmitting
object is not monotonic:

  measured off Plozz's screen, the only glass in the shipped family:
    #97e3fe  brightest, a 1px inset ring on all four sides
    #82deff  one step down, a second ring
    #72daff  the field
  the ramp is almost entirely in the *red* channel (97->82->72, blue steady):
  the glass edge is not a brighter blue, it is a whiter one. Desaturation, not
  luminance, is what reads as an edge catching light.

So this mark spends its tones on three things Plozz spends two on:

  1. the lit edge — a desaturated ring right inside the keyline, all the way
     round, including round the tail, with a pure-white catch on the upper-left
     shoulder where the light gets in;
  2. the thickness — the ring just inside that one is a step *deeper* than the
     field it borders, everywhere except the top, where the light is arriving
     and bleeds two steps lighter instead. Bright, dark, then field: that
     three-part edge is the whole difference between glass and paint, and it is
     the profile no opaque mark has;
  3. the cast — nine tones falling top to bottom, deep violet under the entering
     edge to a pale lilac pool where the light gathers and leaves through the
     tail. The tail is thin, so it is nearly all edge, and it glows.

The ramp is biased low (u**1.5), which keeps the face's nine rows on the deep
half so a white ZZ still has something to sit on at 24px, and puts the pale
tones under it where the tail is. Same system as c45 — a fine ramp, no step
louder than its neighbours — running the other way.

Silhouette: the shipped bubble, rounder (corner radius 6 rather than 5) and
narrowed to 26 so the tail can leave from a squared bottom-left corner rather
than being hung off a curve. Body symmetric about x=16; the tail is not, and is
exempt.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import keyline, rings, to_paths, is_slab, show  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SLUG = 't13'
NAME = 'Glass, cast'

# ---------------------------------------------------------------------------
# Silhouette.
# ---------------------------------------------------------------------------
BODY_TOP = 2
# 28 across, the shipped width, so the mark has the same presence in a 32 box.
# Rounder on top than the shipped bubble (insets 6,4,2,1,0 rather than 5,3,2,1,0)
# and flatter underneath, because light pools in a base and a tail needs a corner
# to leave from, not a curve to slide off.
WIDTHS = ([16, 20, 24, 26, 28] + [28] * 13 + [26, 24, 20])

BODY = set()
LEFT = {}
for i, w in enumerate(WIDTHS):
    y = BODY_TOP + i
    x0 = 16 - w // 2
    LEFT[y] = x0
    BODY |= {(x0 + k, y) for k in range(w)}

BODY_Y0, BODY_Y1 = BODY_TOP, BODY_TOP + len(WIDTHS) - 1

# The tail hangs off the bottom-left corner, its left wall carrying straight down
# from x6 where the body's last row starts. Row widths below the body fall
# monotonically, so the silhouette carries no spur.
TAIL = set()
for y, (a, b) in {23: (6, 12), 24: (6, 11), 25: (6, 10),
                  26: (6, 8), 27: (6, 7)}.items():
    TAIL |= {(x, y) for x in range(a, b + 1)}

SHAPE = BODY | TAIL

# ---------------------------------------------------------------------------
# Assertions on the shape itself.
# ---------------------------------------------------------------------------
check(BODY)                                   # body: symmetric about x=16, no spurs
assert all((31 - x, y) in BODY for x, y in BODY), 'body is not symmetric about x=16'


def widths(s):
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    return {y: max(v) - min(v) + 1 for y, v in rows.items()}


W = widths(SHAPE)
ys = sorted(W)
for i in range(1, len(ys) - 1):
    a, b, c = W[ys[i - 1]], W[ys[i]], W[ys[i + 1]]
    assert not (b > a and b > c), f'spur at row {ys[i]}: {b} vs {a}/{c}'
xs = [p[0] for p in SHAPE]
assert min(xs) >= 2 and max(xs) <= 29, f'x{min(xs)}-{max(xs)} leaves the safe area'
assert ys[0] >= 2 and ys[-1] <= 29, f'y{ys[0]}-{ys[-1]} leaves the safe area'
# One connected piece: the tail must be part of the bubble, not floating near it.
seen, stack = set(), [next(iter(SHAPE))]
while stack:
    p = stack.pop()
    if p in seen:
        continue
    seen.add(p)
    stack += [(p[0] + dx, p[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if (p[0] + dx, p[1] + dy) in SHAPE]
assert seen == SHAPE, 'the silhouette is not one connected shape'

# ---------------------------------------------------------------------------
# Palette.
#
# Purple, because Twitch is purple and the client asked for the association;
# violet rather than magenta so it stays clear of Mozz's red, and saturated
# rather than pale so it stays clear of Hozz's pale blue and Plozz's cyan even
# at 16px. The mid stop is a hair lighter than the shipped #8f52f6 — a straight
# line from the deep stop to a pale enough pool cannot pass through #8f52f6
# without one step in green jumping louder than the rest, and an audible step is
# the one thing this system is not allowed.
# ---------------------------------------------------------------------------
INK = '#1d0a3b'      # keyline: a near-black of the hue, Mozz's rule, not pure black
RIM = '#e9dcff'      # the lit edge, desaturated rather than brightened — Plozz's trick
SPEC = '#ffffff'     # the catch on the upper-left shoulder, where the light gets in

DEEP, MID, POOL = (0x5d, 0x27, 0xb0), (0x9a, 0x68, 0xf2), (0xc9, 0xb0, 0xf9)
SEG = 6              # steps per segment; 13 stops in all


def lerp(a, b, t):
    return round(a + (b - a) * t)


def span(a, b, n):
    return [tuple(lerp(a[c], b[c], i / n) for c in range(3)) for i in range(n + 1)]


RAMP = [f'#{r:02x}{g:02x}{b:02x}'
        for r, g, b in span(DEEP, MID, SEG) + span(MID, POOL, SEG)[1:]]
N = len(RAMP)

# Plozz's own #97e3fe -> #82deff steps by 21; c45 held itself to 18. So does this.
MAX_STEP = 18
for a, b in zip(RAMP, RAMP[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= MAX_STEP, f'{a}->{b} steps by {d}, which reads as a band'

# ---------------------------------------------------------------------------
# Layers.
# ---------------------------------------------------------------------------
K = keyline(SHAPE)
inner = SHAPE - K
RING = keyline(inner)          # the 1px ring right inside the keyline
INT = inner - RING             # the field: everything the light crosses

# Light arrives from above and to the left. Only the ring it actually strikes is
# lit; the rest of the ring is glass seen edge-on, and glass seen edge-on is
# *darker* than the field behind it, not lighter. Getting that the wrong way
# round is what makes a translucent object read as a sticker with a white border.
LIT_TO = 13


def faces_light(p):
    x, y = p
    return (x, y - 1) not in inner or ((x - 1, y) not in inner and y <= LIT_TO)


LIT = {p for p in RING if faces_light(p)}
WALL = RING - LIT
assert LIT and WALL, 'the ring did not split into a lit side and a dark side'

# How far down each column the light got. A wall pixel just under the lit part
# is still half lit, and saying so is what keeps the rim from stopping dead
# halfway round like a border someone drew half of.
LAST_LIT = {}
for x, y in LIT:
    LAST_LIT[x] = max(LAST_LIT.get(x, -99), y)

# Depth inside the field, straight out of rings(), so the bevel it drives follows
# the contour rather than the rows.
DEPTH = {}
layer, rest = rings(INT, 6)
for i, r in enumerate(layer):
    for q in r:
        DEPTH[q] = i
for q in rest:
    DEPTH[q] = 6

iy0 = min(y for _, y in inner)
iy1 = max(y for _, y in inner)

FLOOR = 3.6      # the top of the cast, leaving room for the bevel under the rim
CAP = 11.0          # the bottom of it: the palest four stops belong to the light
BEVEL = 1.15     # stops of darkening per pixel in from the lit edge
DEEPEST = 3      # how far that reaches before the field goes flat
FADE = 0.75      # ...and how much of it survives by the time it reaches the base
BIAS = 0.95       # the cast, held back so the pale end lands under the face
GLOW = (16, 20.8)      # where the transmitted light gathers
GLOW_R = 4.4
GLOW_LIFT = 8.2
WALL_FRAC = 0.45       # the unlit ring, as a fraction deeper than what it holds
GUTTER = 4             # rows over which the lit edge gutters out down the side


def field(p):
    """Tone for a pixel: cast, minus thickness, plus what comes through.

    cast      the light arriving at the top edge, reaching further down the body
              the deeper it goes, biased low so the pale end lands under the face
              rather than behind it.
    thickness every pixel in from the lit edge is a step deeper — Plozz's inset
              bevel, and what makes an edge read as an edge. It fades toward the
              base, where transmission rather than reflection is doing the work.
    glow      the transmitted light, gathering *inside* the lower body and
              leaking out at the tail tip. This is the part no opaque mark can
              show: a bright region that is not attached to the lit edge.
    """
    x, y = p
    u = (y - iy0) / (iy1 - iy0)
    cast = FLOOR + (CAP - FLOOR) * u ** BIAS
    thick = BEVEL * min(DEPTH.get(p, 0), DEEPEST) * (1 - FADE * u)
    d = ((x + 0.5 - GLOW[0]) ** 2 + (y + 0.5 - GLOW[1]) ** 2) ** 0.5
    glow = max(0.0, (GLOW_R - d) / GLOW_R) * GLOW_LIFT
    return cast - thick + glow


def index(p, drop=0.0):
    return max(0, min(N - 1, round(field(p) - drop)))


def wall_index(p):
    """The ring the light did not strike.

    Mostly it is deeper than the field it holds — glass seen edge-on, and the
    thing that keeps a pool of light inside the bubble instead of letting it run
    out at the bottom. Down the left side, though, the lit edge does not stop
    dead: it gutters out over three rows, or the rim reads as a border that
    someone drew half of.
    """
    x, y = p
    gap = y - LAST_LIT.get(x, -99)
    if 0 < gap <= GUTTER:
        return index(p, -1.0 * (GUTTER + 1 - gap))
    return index(p, max(1.5, WALL_FRAC * field(p)))


BANDS = [set() for _ in range(N)]
for p in INT:
    BANDS[index(p)].add(p)
for p in WALL:
    BANDS[wall_index(p)].add(p)

# The catch: the stretch of lit edge on the upper-left shoulder, where a curved
# glass surface turns away from a light above and to the left.
CATCH = {p for p in LIT if 3 <= p[1] <= 7 and p[0] <= 10}
LIT -= CATCH

LAYERS = [(BANDS[i], RAMP[i]) for i in range(N) if BANDS[i]]
LAYERS += [(LIT, RIM), (CATCH, SPEC), (K, INK)]

covered = set()
for px, fill in LAYERS:
    assert px, f'{fill} is empty'
    assert not (covered & px), f'{fill} overlaps a layer already painted'
    assert not is_slab(px, SHAPE), f'{fill} reads as a slab dropped in the bubble'
    covered |= px
assert covered == SHAPE, 'the bubble is not exactly covered by its layers'

TONES = [f for _, f in LAYERS]
assert len(set(TONES)) == len(TONES), 'a tone is used twice'
assert len(TONES) >= 8, f'only {len(TONES)} tones'

# ---------------------------------------------------------------------------
# The face. md/wide/gap2 — 8 wide, 9 rows.
#
# Parity: the body is 26 across and the face 8, both even, so it centres on
# x=16 exactly. A 7-wide `sm` face would sit on x=16.5.
# Placement is measured out of mark.ts, not computed here.
# ---------------------------------------------------------------------------
FACE_W, GAP = 8, 2
CY = 12.5


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


def measure(cx, cy, size, smile, gap):
    """faceBoxAt/facePathsAt, straight out of mark.ts — never reimplemented."""
    js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
          f"const o={{cx:{cx},cy:{cy},size:'{size}',smile:'{smile}',gap:{gap}}};"
          "console.log(JSON.stringify({box: faceBoxAt(o), paths: facePathsAt(o)}));")
    out = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings',
         '-e', js], capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    face = set()
    for d in got['paths']:
        face |= pixels(d)
    return got['box'], face


box, FACE = measure(16, CY, 'md', 'wide', GAP)
body_w = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
body_h = BODY_Y1 - BODY_Y0 + 1
assert (body_w - box['w']) % 2 == 0, (
    f"a {box['w']}-wide face cannot centre on a {body_w}-wide body")
assert (body_h - box['h']) % 2 == 0, f"a {box['h']}-row face cannot split {body_h} rows"
assert box['w'] == FACE_W and box['h'] == 9, f"mark.ts says {box['w']}x{box['h']}"
assert box['x'] + box['right'] == 31, 'face is not centred on x=16'

above, below = box['y'] - BODY_Y0, BODY_Y1 - box['bottom']
assert above == below, f'air {above}/{below} on the body'
assert FACE <= BODY, 'face hangs off the body'
assert not (FACE & RING) and not (FACE & K), 'the face touches the edge of the glass'

# The Zs do not mirror — they are one letter repeated by translation (5 on md).
# The smile does mirror. Assert what is true rather than what is convenient.
eyes = {p for p in FACE if p[1] < box['y'] + 4}
smile = {p for p in FACE if p[1] >= box['bottom'] - 2}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert {(x + 5, y) for x, y in eyes if x < 16} == {p for p in eyes if p[0] >= 16}, (
    'the two Zs are not the same letter')
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric about x=16'

# Contrast under the face: a white ZZ needs a ground dark enough to hold it at
# 24px, so every tone the letterforms sit on must stay on the deep half.
under = {index(p) for p in FACE if p in INT}
assert max(under) <= (N - 1) // 2, (
    f'the face sits on ramp stops {sorted(under)} — too pale for a white ZZ')

print(f'{SLUG} {NAME}')
print(f'  body {body_w}x{body_h} y{BODY_Y0}-{BODY_Y1} · tail to y{ys[-1]} · '
      f'face md/wide gap{GAP} = {box["w"]}x{box["h"]} at x{box["x"]}-{box["right"]}, '
      f'y{box["y"]}-{box["bottom"]}')
print(f'  air {above} above / {below} below · {len(TONES)} tones · '
      f'face on stops {sorted(under)} of 0-{N - 1}')
print('  ramp ' + ' '.join(RAMP))

if '--show' in sys.argv:
    n_bands = len(LAYERS) - 3
    show([p for p, _ in LAYERS] + [FACE],
         [str(i % 10) for i in range(n_bands)] + ['+', '*', '#', '@'])

# ---------------------------------------------------------------------------
# Emit.
# ---------------------------------------------------------------------------
rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in LAYERS)

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG} · {NAME}
 *
 * The opposite case to the chosen Hozz mark. That one is opaque — a light rim
 * falling to a deeper core, which is what light landing on a curved surface
 * does. This is glass, so the light also comes *through*, and the tell is that
 * the tones stop being monotonic.
 *
 * Three things carry it. A lit edge, desaturated rather than brightened —
 * Plozz's screen ramps #97e3fe → #82deff → #72daff almost entirely in the red
 * channel, so its glass front reads as glass because the edge goes *whiter*,
 * not bluer. A thickness: the ring just inside that edge is one step deeper
 * than the field it borders, except across the top, where the light is arriving
 * and bleeds two steps lighter instead. And a cast: nine stops falling from
 * deep violet under the entering edge to a pale pool at the bottom, where the
 * light gathers and leaves through the tail. The tail is thin, so it is very
 * nearly all edge, and it glows.
 *
 * The ramp is biased low, which keeps the face's nine rows on the deep half —
 * a white ZZ needs something to sit on at 24px — and spends the pale end below
 * it, where the tail is. Nothing is cleared for the letterforms; the bands pass
 * behind them, as they do on both shipped marks.
 *
 * The silhouette is the shipped bubble, rounder (radius 6, not 5) and narrowed
 * to 26 so the tail leaves from a squared bottom-left corner instead of hanging
 * off a curve. The body is symmetric about x=16 and the face is centred on the
 * body, not the whole mark: {above} rows of air above, {below} below, measured. The
 * tail is deliberately asymmetric and is exempt.
 *
 * {len(TONES)} tones, no step louder than {MAX_STEP} on any channel.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {NAME}">
{rows}
  <g fill="#ffffff" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: 'md', smile: 'wide', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in [INK, *RAMP, RIM, SPEC, '#ffffff'])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'Glass rather than paint: a desaturated lit edge all the way round, a step-deeper ring behind it for thickness, and nine stops falling from deep violet at the top to a pale pool that leaves through the tail.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
