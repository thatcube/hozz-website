"""
t13 — Glass, cast. A speech bubble made of something the light goes *through*.

The chosen Hozz mark (c45) is opaque: one monotonic ramp, light rim falling to a
deeper core, which is what light *landing on* a curved surface does. Glass is the
other case — light enters an edge, crosses the body, gathers, and leaves
somewhere else — and the tell is that a transmitting object is not monotonic.

  measured off Plozz's screen, the only glass in the shipped family:
    #97e3fe  brightest, a 1px inset ring on all four sides
    #82deff  one step down, a second ring
    #72daff  the field
  the ramp is almost entirely in the *red* channel (97->82->72, blue steady):
  the glass edge is not a brighter blue, it is a whiter one. Desaturation, not
  luminance, is what reads as an edge catching light.

Plozz rings all four sides equally, which is a lit *frame*. Light does not arrive
from four directions at once, so this mark splits the ring in two and that split
is the whole idea:

  1. the lit edge — desaturated rather than brightened, across the top and down
     the upper left, with a pure-white catch on the shoulder where the light gets
     in. It does not stop dead: over four rows down each side it gutters back
     into the field, because a rim that ends on a hard row reads as a border
     somebody drew half of;
  2. the wall — the rest of that ring, which is glass seen edge-on and therefore
     *deeper* than the field it borders, not lighter. It is what keeps the pool
     of light inside the bubble instead of letting it run out of the bottom, and
     it is what holds the silhouette on a white page at 24px;
  3. the thickness — depth is measured *from the lit ring outward through the
     glass*, not as an offset of the outline. That distinction is the whole of
     it: offset the outline and you get a band of identical width on all four
     sides, which is a moulding, not light. Measured from the lit edge, the
     ramp is five steps deep where the light enters and has run out entirely by
     the far side. Bright, dark, then field: that three-part profile is the
     difference between glass and paint. It relaxes as it descends, so the
     field carries from deep at the entering edge to mid at the base;
  4. the pool — transmitted light does not stay where it landed. It is measured
     up from the silhouette's own underside (edge(inner, 0, 1)), so its contour
     is the bottom contour, and it converges to a focus in from the far corner,
     falling off on both sides along the wall and upward away from it. It then
     carries *into* the wall it leaves through, because light that stops one
     pixel short of the surface it exits by ends on a cliff and reads as a
     patch somebody painted. A slight rake across the body, scaled by that same
     depth so it is a lean rather than a stripe, is what puts the focus off to
     one side: light enters at a corner rather than everywhere at once.

     The pool is the one thing an opaque mark cannot show — a bright region not
     attached to the lit edge. Every contour in it is still the shape's own.

Pure white is the face's alone. The catch is a violet-white a step off it, so
the ZZ stays the brightest thing on the glass — and so that measuring the white
pixels measures the face, rather than the face plus whatever else was painted
#ffffff.

The field is biased so the face's eleven rows stay on the deep half of the ramp
and the pale end is spent below them. That is asserted, not eyeballed: every tone
the ZZ sits on or touches must clear 4.5:1 against white, and the worst measures
4.94:1. Same system as c45, a fine ramp with no step louder than its neighbours,
put to the opposite use.

Silhouette: the shipped bubble at its full 28 across, rounder over the top
(insets 6,4,2,1,0 rather than 5,3,2,1,0) and flatter underneath, so the light has
a base to gather in. The tail is four rows and six wide at most, flush with the
body's bottom-left corner: the shipped tail is small relative to the body and
unmistakably a separate part, and a tail that grows into a second mass stops
being a tail. The body is symmetric about x=16; the tail is not, and is exempt.

Face: the shipped size, lg, 10 wide on a 28-wide body — both even, which is the
only way a face can centre on a body at all — placed against the *body*, not the
mark. The tail and the pool are not the object; centring on the lit field is how
a mark ends up looking broken.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import check  # noqa: E402
from shade import edge, keyline, to_paths, is_slab, show  # noqa: E402

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

# The tail hangs off the bottom-left corner, its left wall flush with where the
# body's last row starts, as the shipped one is. Four rows, six wide at most: the
# shipped tail is small relative to the body and unmistakably a separate part,
# and a tail that grows into a second mass stops reading as a tail. Row widths
# below the body fall monotonically, so the silhouette carries no spur.
TAIL = set()
for y, (a, b) in {23: (6, 11), 24: (6, 10), 25: (6, 9), 26: (6, 7)}.items():
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
SPEC = '#f6efff'     # the catch on the upper-left shoulder, where the light gets in
# ...and it is *not* #ffffff. Pure white belongs to the ZZ and the smile alone: a
# second pure-white mass elsewhere in the mark measures as part of the face and,
# worse, competes with it — the face stops being the brightest thing on the glass.

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


def spread(seed, region):
    """How many pixels of glass from `seed` to here, measured through the glass.

    rings() peels bands off the outside of a shape; this is the same idea run
    outward from an arbitrary seed, which is what lets the light be measured
    from the edge it actually enters or leaves by. The point of measuring
    distance this way rather than by row or by radius is that the answer is a
    property of the silhouette: every contour it produces is the shape's own
    contour, offset, so nothing derived from it can come out as a rectangle.
    """
    d, front, n = {}, set(seed), 0
    while front:
        nxt = set()
        for p in front:
            if p in d:
                continue
            d[p] = n
            nxt |= {(p[0] + a, p[1] + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if (p[0] + a, p[1] + b) in region and (p[0] + a, p[1] + b) not in d}
        front, n = nxt, n + 1
    return d


# How deep into the glass a pixel is, measured from the edge the light actually
# strikes — not from the whole outline. Measured from the outline it produces a
# bright inset border on all four sides, which is a moulding: a band of the same
# width everywhere reads as something that was fitted rather than something the
# light is doing. Measured from the lit edge it only brightens where the surface
# turns toward the light, and runs out on the far side, which is what an inset
# ramp on a real edge does.
DEPTH = spread(LIT, inner)
FAR = max(DEPTH.values())

# The far wall, taken off the silhouette: the pixels with no glass below them.
# This is the surface the transmitted light gathers against and leaves through,
# and because it is the shape's own underside the pool it carries is curved by
# the bubble rather than cut by a rect. It is measured over the whole of the
# inside, ring included: light that has crossed the glass has to leave somewhere,
# and stopping it one pixel short of the wall is what leaves a pale patch sitting
# in mid-air with nothing to be resting on.
BASE = {p for p in edge(inner, 0, 1) if p[1] <= BODY_Y1}
UP = spread(BASE, inner)
BX0 = min(x for x, _ in BASE)
BX1 = max(x for x, _ in BASE)

iy0 = min(y for _, y in inner)

FLOOR = 7.46     # the tone right against the lit edge, before the ramp steps in
CAP = 7.66       # ...and where that has drifted to by the last row
BEVEL = 1.35     # stops of darkening per pixel in from the lit edge
DEEPEST = 5      # how far that reaches before the field goes flat
FADE = 0.35      # ...and how much of it survives by the time it reaches the base
BIAS = 1.35      # the cast, held back so the pale end lands below the face
RAKE = 2.00      # how far across the cast leans by the time it reaches the base
RAKE0 = 0.60     # ...and how far it leans at the top, where the light comes in flat
POOL_LIFT = 7.6      # the transmitted light gathering against the far wall
POOL_DEEP = 2.6      # how far up off that wall it reaches
POOL_AT = 0.73       # where along the wall it converges, 0 at the left end
POOL_WIDE = 0.31     # ...and how much of the wall it covers
POOL_TIGHT = 1.4     # how sharply it falls off along the wall...
POOL_LENS = 1.3      # ...and up off it, so the pool is a lens, not a shelf
WALL_FRAC = 0.45     # the unlit ring, as a fraction deeper than what it holds
GUTTER = 4           # rows over which the lit edge gutters out down the side
EXIT_MIN = 1.2       # how much has to reach the wall before it counts as an exit
EXIT_DROP = 1.4      # ...and the wall still sits a step under the pool it holds


def transmitted(p):
    """How much light has crossed the glass and reached this pixel."""
    up = UP.get(p)
    if up is None or up >= POOL_DEEP:
        return 0.0
    t = (p[0] - BX0) / (BX1 - BX0)
    along = 2.718281828 ** (-(((t - POOL_AT) / POOL_WIDE) ** 2))
    return POOL_LIFT * along ** POOL_TIGHT * (1 - up / POOL_DEEP) ** POOL_LENS


def field(p):
    """Tone for a pixel: cast, minus thickness, plus what comes through.

    cast      the light arriving at the top edge, leaning further across the
              further it falls — a beam that entered one corner is displaced by
              the time it leaves, and a lean already at full strength on the top
              row would just be a stripe painted down the far side.
    thickness every pixel in from the *lit* edge is a step deeper — Plozz's inset
              ramp — running out after five, so the far side gets a wall rather
              than a second bright border. It relaxes as it descends, which is
              what carries the field from deep at the top to mid at the base:
              nearer the base it is transmission rather than reflection doing the
              work, and transmitted light does not care how thick the near face
              is.
    pool      the transmitted light, gathering against the far wall of the
              bubble: strongest on the wall itself, falling off up from it and
              along it, so it is a lens rather than a shelf. Anchored to a
              surface and shaped by the silhouette, and the part no opaque mark
              can show — a bright region not attached to the lit edge and not
              explained by the curvature.
    """
    x, y = p
    u = min(1.0, max(0.0, (y - iy0) / (BODY_Y1 - iy0)))
    lean = (RAKE0 + (RAKE - RAKE0) * u) * (x - 2) / 27
    cast = FLOOR + (CAP - FLOOR) * u ** BIAS + lean
    thick = BEVEL * min(DEPTH.get(p, DEEPEST), DEEPEST) * (1 - FADE * u)
    return cast - thick + transmitted(p)


TAIL_CAP = 6.4   # the tail is lit from within, but it is not the pool


def index(p, drop=0.0):
    v = field(p) - drop
    if p[1] > BODY_Y1:
        v = min(v, TAIL_CAP)
    return max(0, min(N - 1, round(v)))


def wall_index(p):
    """The ring the light did not strike.

    Mostly it is deeper than the field it holds — glass seen edge-on, and the
    thing that keeps a pool of light inside the bubble instead of letting it run
    out at the bottom. Two exceptions, and both are the light rather than a
    decision: down the left side the lit edge does not stop dead but gutters out
    over four rows, or the rim reads as a border somebody drew half of; and where
    the pool reaches the far wall the wall is what the light leaves through, so
    it is lit from the inside rather than dropped. Without that second one the
    pool ends on a cliff and its brightest pixels read as a patch floating clear
    of everything.
    """
    x, y = p
    gap = y - LAST_LIT.get(x, -99)
    if 0 < gap <= GUTTER:
        return index(p, -1.0 * (GUTTER + 1 - gap))
    if transmitted(p) > EXIT_MIN:
        return index(p, EXIT_DROP)
    return index(p, max(1.5, WALL_FRAC * field(p)))


BANDS = [set() for _ in range(N)]
for p in INT:
    BANDS[index(p)].add(p)
for p in WALL:
    BANDS[wall_index(p)].add(p)

# The catch: the stretch of lit edge on the upper-left shoulder, where a curved
# glass surface turns away from a light above and to the left.
CATCH = {p for p in LIT if 3 <= p[1] <= 6 and p[0] <= 9}
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
# Pure white is the face's, and only the face's. Anything else painted #ffffff
# both measures as part of the face and competes with it for the eye.
assert '#ffffff' not in {t.lower() for t in TONES}, 'the bubble is using the face white'

# ---------------------------------------------------------------------------
# The face. lg/wide/gap2 — the shipped size, 10 wide, 11 rows.
#
# Parity: the body is 28 across and the face 10, both even, so it centres on
# x=16 exactly. A 7-wide `sm` face would sit on x=16.5 and no adjustment fixes
# it. Placement is measured out of mark.ts, not computed here.
# ---------------------------------------------------------------------------
FACE_W, GAP = 10, 2
CY = 12


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


box, FACE = measure(16, CY, 'lg', 'wide', GAP)
body_w = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
body_h = BODY_Y1 - BODY_Y0 + 1
assert (body_w - box['w']) % 2 == 0, (
    f"a {box['w']}-wide face cannot centre on a {body_w}-wide body")
assert (body_h - box['h']) % 2 == 0, f"a {box['h']}-row face cannot split {body_h} rows"
assert box['w'] == FACE_W and box['h'] == 11, f"mark.ts says {box['w']}x{box['h']}"
assert box['x'] + box['right'] == 31, 'face is not centred on x=16'

above, below = box['y'] - BODY_Y0, BODY_Y1 - box['bottom']
assert above == below, f'air {above}/{below} on the body'
assert FACE <= BODY, 'face hangs off the body'
assert not (FACE & RING) and not (FACE & K), 'the face touches the edge of the glass'

# The Zs do not mirror — they are one letter repeated by translation (6 on lg).
# The smile does mirror. Assert what is true rather than what is convenient.
eyes = {p for p in FACE if p[1] < box['y'] + 5}
smile = {p for p in FACE if p[1] >= box['bottom'] - 3}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
left = {p for p in eyes if p[0] < 16}
right = {p for p in eyes if p[0] >= 16}
off = min(x for x, _ in right) - min(x for x, _ in left)
assert {(x + off, y) for x, y in left} == right, 'the two Zs are not the same letter'
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric about x=16'

# Contrast under the face: a white ZZ needs a ground dark enough to hold it at
# 24px. The shipped mark clears 4.64:1 on Twitch purple, so every tone the
# letterforms sit on clears 4.5:1 here — measured, not eyeballed.
def lum(h):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return (0.2126 * c(int(h[1:3], 16)) + 0.7152 * c(int(h[3:5], 16))
            + 0.0722 * c(int(h[5:7], 16)))


def on_white(h):
    return 1.05 / (lum(h) + 0.05)


under = {index(p) for p in FACE if p in INT}
worst = max(under)
assert on_white(RAMP[worst]) >= 4.5, (
    f'the face sits on {RAMP[worst]} at {on_white(RAMP[worst]):.2f}:1 — under 4.5:1')

# ...and the tones it butts up against, which is what actually reads at 16px
# when a letterform is one pixel wide.
near = set()
for x, y in FACE:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        q = (x + dx, y + dy)
        if q in INT and q not in FACE:
            near.add(RAMP[index(q)])
edge = min(on_white(c) for c in near)
assert edge >= 4.5, f'the face borders a tone at {edge:.2f}:1 — under 4.5:1'

print(f'{SLUG} {NAME}')
print(f'  body {body_w}x{body_h} y{BODY_Y0}-{BODY_Y1} · tail to y{ys[-1]} · '
      f'face lg/wide gap{GAP} = {box["w"]}x{box["h"]} at x{box["x"]}-{box["right"]}, '
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
 * Plozz, the only glass in the shipped family, rings its screen on all four
 * sides — #97e3fe → #82deff → #72daff, a ramp almost entirely in the red
 * channel, so the edge reads as catching light because it goes *whiter*, not
 * bluer. Desaturation is the trick and it is borrowed here. The frame is not:
 * light does not arrive from four directions at once, so the ring is split.
 *
 * Across the top and down the upper left it is lit, with a white catch on the
 * shoulder where the light gets in, guttering back into the field over four
 * rows rather than stopping on a hard line. The rest of the ring is the wall —
 * glass seen edge-on, a step *deeper* than the field it borders, which is what
 * keeps the light pooled inside the bubble rather than running out of the
 * bottom, and what holds the silhouette on a white page at 24px. Inside the lit
 * edge the tone steps deeper again per pixel, fading toward the base. Bright,
 * dark, then field: that profile is the difference between glass and paint.
 *
 * Depth is measured from that lit ring outward through the glass rather than as
 * an offset of the outline, and the difference matters: offset the outline and
 * the same band appears on all four sides at the same width, which reads as a
 * moulding. Measured from the light, the ramp has run out by the far side.
 *
 * What is over there instead is the pool — transmitted light, measured up from
 * the silhouette's own underside so its contour is the bottom contour, focusing
 * in from the far corner and falling away on both sides. It carries into the
 * wall it leaves through, because light stopping a pixel short of the surface
 * it exits by ends on a cliff and reads as a painted patch. A rake across the
 * body, scaled by the same depth so it leans rather than stripes, is what puts
 * the focus off to one side. That pool is the one thing an opaque mark cannot
 * show: a bright region not attached to the lit edge.
 *
 * The field is held back so every tone the letterforms sit on or touch clears
 * 4.5:1 against white — asserted, worst 4.94:1 — because a white ZZ needs
 * something to sit on at 24px. Nothing is cleared for the face: the bands pass
 * behind it, as they do on both shipped marks. Pure white is the face's alone,
 * the catch being a violet-white one step off it.
 *
 * The silhouette is the shipped bubble at its full 28 across, rounder over the
 * top (insets 6,4,2,1,0 rather than 5,3,2,1,0) and flatter underneath, so the
 * light has a base to gather in. The tail is four rows, six wide at most, flush
 * with the body's bottom-left corner — small relative to the body and plainly a
 * separate part, and given its own mid tone so it does not dissolve into the
 * pool. The body is symmetric about x=16, every row of it; the tail is not, and
 * is exempt.
 *
 * The face is the shipped size — lg, 10 wide, from the shared module untouched
 * — and it is centred on the *body*: {above} rows of air above it, {below} below,
 * measured. 10 on 28 is the parity that lets it centre at all.
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
    {{facePathsAt({{ cx: 16, cy: {CY}, size: 'lg', smile: 'wide', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in dict.fromkeys([INK, *RAMP, RIM, SPEC, '#ffffff']))
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'Glass rather than paint. The ring inside the keyline is lit only where the light actually strikes — desaturated, Plozz\\'s trick — and is a step deeper everywhere else, because glass seen edge-on is darker than the field behind it. That dark wall holds a pool of transmitted light, measured up from the silhouette\\'s own underside so it follows the bottom contour, focusing in from the far corner and leaving through the wall it meets: a bright region not attached to the lit edge, which is the one thing an opaque mark cannot show.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
