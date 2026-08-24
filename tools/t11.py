"""t11 — Twozz, the direct sibling of c45 · Ripple, Lens.

c45 was rasterised to the 32 grid and measured before anything was drawn here:

    6 stops, rim -> centre    #edf6fc #dcecf6 #cae1f1 #b9d7eb #a7cce6 #96c2e0
    coverage per stop         56 52 44 40 36 px, then a 62 px core
    step size                 ΔE 4.97 5.69 4.95 5.67 4.88  (mean 5.21)
    total rim -> centre       ΔE 26.07,  ΔL 20.0
    direction per step        L -4.0, chroma +3.3 — the rim is nearly neutral
                              and the colour lives in the middle
    keyline                   1 px, outside the ramp, not part of it
    face                      md/compact/gap2, 8x8, on a 22-row body: 7 rows of
                              air above, 7 below

This is that ramp in purple. Same six stops, same mean step (held to c45's 5.21
by construction and asserted), same rim-lighter/centre-deeper/centre-more-
chromatic direction, same 1 px keyline outside it, same face at the same 7/7.
Only the hue and the silhouette differ, which is the whole exercise.

**The hue.** Purple cannot be anchored where blue was. c45's rim is near-white
(L 96) because pale blue-white is a colour; pale purple-white is not Twitch. So
the ramp is anchored by its *middle*: stop 3 of 6 is #8f52f6, the purple Twozz
already ships, exactly. Three stops climb off it toward the rim and two fall
away under the face. Squint and the bubble is the shipped purple; look and it is
a surface. The one place the anchor cannot be honoured is chroma: #8f52f6 is
already at C 94 and sRGB has nothing more saturated to give at that lightness,
so the per-step chroma rise is taken as far as the gamut allows and the
remainder of the ΔE budget is spent on lightness. The step *size* is what the
eye reads, and that is matched.

**Rim to centre on a bubble.** A disc has one answer; a bubble needs one worked
out. Ring-peeling (`shade.rings`) is wrong here, and measurably: a 4-neighbour
peel erodes diagonals faster than sides, so six peels of this body leave a 16x10
rectangle with a single pixel off each corner — a box inside a curve, the exact
defect `is_slab` exists to catch, and it flags it. So the ramp is built the way
the silhouette is: seven nested superellipses on the same centre, each one pixel
in from the last. Every band is then a true parallel of the outline, the corners
keep shrinking all the way down, and the core comes out as a soft blob rather
than a box — which is what the disc's core is, and the reason the two read as one
system. `--rings` renders the rejected version.

**The tail.** It takes the rim tone and stays flat, and that was measured rather
than assumed. Peel the whole silhouette and no pixel of the tail is more than
four deep, so the body's own law would hand it the first two tones over a
handful of pixels. Rendered at 96px that is not a surface — it is a 2x2 of the
deeper tone floating inside a flap five pixels wide, and it reads as dirt. (The
generator will draw it: `--ramp-tail`.) Flat rim is also what continuity demands,
because the body's own outermost tone at the join is rim, so the tail is the same
skin carried on where the form is too thin to turn. Its shape follows the shipped
mark: one straight left edge, the taper taken entirely from the right, because a
tail that narrows on both sides at once stops being a piece of the bubble and
becomes a diagonal stroke. The silhouette is outlined once, around the outside of
the whole shape.
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
SLUG = 't11'
NAME = 'Lens'

# ---------------------------------------------------------------------------
# Colour. Everything below is CIE Lab, because "the same subtlety of step" is a
# perceptual claim and hex arithmetic cannot check it.
# ---------------------------------------------------------------------------
BRAND = '#8f52f6'           # Twozz, as shipped
KEY = '#1b0b36'             # the near-black of the hue, as Mozz does it
INK = '#ffffff'             # the family's ink on a coloured container
STEPS = 6
ANCHOR = 3                  # which stop is exactly BRAND
C45_STEP, C45_TOTAL = 5.21, 26.07   # measured, see the docstring


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _unlin(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lab(hexstr):
    r, g, b = (_lin(int(hexstr[i:i + 2], 16) / 255) for i in (1, 3, 5))
    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = f(X / 0.95047), f(Y), f(Z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def rgb(L, a, b):
    """Lab -> hex, plus whether it needed clipping to fit sRGB."""
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def g(t):
        return t ** 3 if t ** 3 > 216 / 24389 else (t - 4 / 29) * 108 / 841
    X, Y, Z = g(fx) * 0.95047, g(fy), g(fz) * 1.08883
    lin = (X * 3.2406 + Y * -1.5372 + Z * -0.4986,
           X * -0.9689 + Y * 1.8758 + Z * 0.0415,
           X * 0.0557 + Y * -0.2040 + Z * 1.0570)
    out = '#%02x%02x%02x' % tuple(
        round(_unlin(max(0.0, min(1.0, v))) * 255) for v in lin)
    return out, any(v < -0.002 or v > 1.002 for v in lin)


def de(a, b):
    return sum((x - y) ** 2 for x, y in zip(lab(a), lab(b))) ** 0.5


def build_ramp(dC):
    """Six stops through BRAND, `dC` of chroma and the rest of c45's step in L."""
    L0, a0, b0 = lab(BRAND)
    C0 = (a0 ** 2 + b0 ** 2) ** 0.5
    dL = (C45_STEP ** 2 - dC ** 2) ** 0.5
    stops, clipped = [], False
    for i in range(STEPS):
        k = i - ANCHOR                      # -3 .. +2, 0 is BRAND
        s = (C0 + dC * k) / C0
        h, cl = rgb(L0 - dL * k, a0 * s, b0 * s)
        clipped |= cl
        stops.append(h)
    return stops, clipped


# c45 splits its step 4.0 lightness / 3.3 chroma. Purple cannot: #8f52f6 sits
# 6 units under the sRGB boundary at its own lightness, and that boundary falls
# by 2.1 of chroma for every unit of lightness gained, so a rim three stops
# lighter has to give up chroma faster than blue does. Spend as much of the step
# on lightness as the gamut allows and take the rest in chroma — the split
# moves, the step size does not.
RAMP = None
for hundredths in range(0, 521, 5):
    cand, clipped = build_ramp(hundredths / 100)
    if not clipped:
        RAMP, DC = cand, hundredths / 100
        break
assert RAMP, 'no in-gamut ramp'
RAMP[ANCHOR] = BRAND                        # exact, not merely rounded to it

STEP_DE = [de(a, b) for a, b in zip(RAMP, RAMP[1:])]
MEAN = sum(STEP_DE) / len(STEP_DE)
TOTAL = de(RAMP[0], RAMP[-1])
assert abs(MEAN - C45_STEP) < 0.35, f'step {MEAN:.2f} is not c45\'s {C45_STEP}'
assert abs(TOTAL - C45_TOTAL) < 1.5, f'total {TOTAL:.2f} is not c45\'s {C45_TOTAL}'
assert max(STEP_DE) - min(STEP_DE) < 0.9, 'one step is louder than the others'
for a, b in zip(RAMP, RAMP[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= 18, f'{a}->{b} steps by {d} on a channel, which reads as a band'
assert lab(RAMP[0])[0] > lab(RAMP[-1])[0], 'the rim must be the lighter end'

# ---------------------------------------------------------------------------
# Geometry. Body 28x22 on x2-29 / y2-23; tail below it, to y29.
# ---------------------------------------------------------------------------
X0, X1, Y0, Y1 = 2, 29, 2, 23
CX, CYY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2
N = 3.0                     # superellipse exponent: rounder than the shipped
                            # rounded rect, still unmistakably a bubble body


def shell(inset):
    """The body, `inset` pixels in. Centred on x=16.0, so it mirrors exactly."""
    a, b = (X1 + 1 - X0) / 2 - inset, (Y1 + 1 - Y0) / 2 - inset
    return {(x, y)
            for y in range(Y0, Y1 + 1) for x in range(X0, X1 + 1)
            if (abs(x + 0.5 - CX) / a) ** N + (abs(y + 0.5 - CYY) / b) ** N <= 1 + 1e-9}


LEVELS = [shell(i) for i in range(STEPS + 1)]
BODY = LEVELS[0]
if '--rings' in sys.argv:
    # The alternative, kept runnable so the choice can be re-checked: peel
    # 4-neighbour contour rings the way the disc takes them.
    LEVELS, cur = [set(BODY)], set(BODY)
    for _ in range(STEPS):
        _r, cur = rings(cur, 1)
        LEVELS.append(set(cur))
for i in range(STEPS):
    assert LEVELS[i + 1] < LEVELS[i], f'level {i + 1} is not inside level {i}'

# The tail: a wedge off the bottom-left, built the way the shipped mark builds
# its own — one straight left edge continuing the body's bottom-left curve, the
# taper taken entirely from the right. A tail that narrows on both sides at once
# turns into a diagonal stroke; this one stays a piece of the bubble. Once the
# keyline has taken the outer ring the fill inside runs 6-5-4-3-2 and only the
# last row is pure line.
TAIL_ROWS = {24: (9, 17), 25: (8, 15), 26: (8, 13), 27: (8, 12), 28: (8, 11), 29: (8, 10)}
TAIL = {(x, y) for y, (a, b) in TAIL_ROWS.items() for x in range(a, b + 1)}
SIL = BODY | TAIL

# ---- silhouette assertions -------------------------------------------------
BODY_W = check(BODY)                       # symmetric about x=16, and no spurs
rows = {}
for x, y in SIL:
    rows.setdefault(y, []).append(x)
ys = sorted(rows)
W = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
for i in range(1, len(W) - 1):
    assert not (W[i] > W[i - 1] and W[i] > W[i + 1]), f'spur at row {ys[i]}'
assert ys == list(range(Y0, 30)), 'the silhouette has a gap in it'
xs = sorted({p[0] for p in SIL})
assert xs[0] >= 2 and xs[-1] <= 29 and ys[0] >= 2 and ys[-1] <= 29, 'outside x2-29 / y2-29'
# the tail must hang off the body, not float beside it
assert all((x, y - 1) in SIL for y in sorted(TAIL_ROWS) for x in
           [TAIL_ROWS[y][0]] if y == min(TAIL_ROWS)), 'tail is not attached'
prev = None
for y in sorted(TAIL_ROWS):
    a, b = TAIL_ROWS[y]
    if prev:
        assert a >= prev[0] - 1 and b <= prev[1], 'the tail flares instead of tapering'
        assert a <= prev[1] and b >= prev[0] - 1, 'the tail breaks contact with itself'
    prev = (a, b)
assert set(range(TAIL_ROWS[24][0], TAIL_ROWS[24][1] + 1)) <= set(rows[23]), \
    'tail overhangs the body'
# The tail is skin, not a separate object, so the question is what the body's
# own law — tone by distance from the edge — would give it. Peel the whole
# silhouette and read the depth off it: the tail never gets more than four deep,
# so the law would hand it the first two tones over a handful of pixels. Painted,
# that is not a surface, it is a stain: a 2x2 of the deeper tone floating in a
# flap five pixels wide. So the tail takes the rim tone flat, which is also the
# tone the body carries at the join, and the join reads as one skin.
# Run with --ramp-tail to see the alternative that was rejected.
DEPTH = {}
_r, _rem = rings(SIL, STEPS)
for _i, _ring in enumerate(_r, 1):
    for _p in _ring:
        DEPTH[_p] = _i
for _p in _rem:
    DEPTH[_p] = STEPS + 1
assert max(DEPTH[p] for p in TAIL) <= 4, 'the tail is deep enough to need the ramp'

# ---------------------------------------------------------------------------
# Paint. One outline around the whole silhouette; the ramp inside the body by
# shell; the tail flat at the rim tone, which is what the body carries where the
# two meet.
# ---------------------------------------------------------------------------
OUTLINE = keyline(SIL)
level = {}
for i, lv in enumerate(LEVELS):
    for p in lv:
        level[p] = i

paint = {}
for p in BODY:
    paint[p] = RAMP[min(max(level[p] - 1, 0), STEPS - 1)]
for p in TAIL:
    paint[p] = RAMP[min(max(DEPTH[p] - 2, 0), STEPS - 1)] if '--ramp-tail' in sys.argv \
        else RAMP[0]
JUNCTION = {p for p in BODY if level[p] == 0 and p not in OUTLINE}
EXEMPT = JUNCTION | {(31 - x, y) for x, y in JUNCTION}   # the tail's own rows
for p in OUTLINE:
    paint[p] = KEY

layers = {}
for p, f in paint.items():
    layers.setdefault(f, set()).add(p)

assert set(paint) == SIL, 'the silhouette is not exactly covered'
assert len(layers) == STEPS + 1, f'{len(layers)} fills, expected {STEPS + 1}'
CORE = layers[RAMP[-1]]
if '--rings' in sys.argv:
    print(f'  [rings] core slab={is_slab(CORE, BODY)}')
else:
    assert not is_slab(CORE, BODY), 'the core reads as a box dropped in the bubble'
for i, c in enumerate(RAMP[1:], 1):          # every band, inside the body, mirrors
    assert all((31 - x, y) in layers[c] for x, y in layers[c] & BODY), \
        f'{c} is not symmetric'
body_only = {p: f for p, f in paint.items() if p in BODY and p not in EXEMPT}
assert all(body_only.get((31 - x, y)) == f for (x, y), f in body_only.items()), \
    'the body is not symmetric about x=16'
assert len(EXEMPT) < 24, f'{len(EXEMPT)} px exempted for the tail is too many'

# ---------------------------------------------------------------------------
# The face. md/compact/gap2 — c45's own face, so the two are the same size on
# the same amount of air. Geometry read back out of mark.ts, never computed.
# ---------------------------------------------------------------------------
GEOM_MD_COMPACT = {1: (7, -3), 2: (8, -4), 3: (9, -4), 4: (10, -5)}
FACE_W, GAP = 8, 2


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


def measure(cx, cy, size, smile, gap):
    js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
          f"const o={{cx:{cx},cy:{cy},size:'{size}',smile:'{smile}',gap:{gap}}};"
          "console.log(JSON.stringify({box: faceBoxAt(o), paths: facePathsAt(o)}));")
    got = json.loads(subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e', js],
        capture_output=True, text=True, check=True).stdout)
    face = set()
    for d in got['paths']:
        face |= pixels(d)
    return got['box'], face


body_w, body_h = max(BODY_W), Y1 - Y0 + 1
assert (body_w - FACE_W) % 2 == 0, (
    f'a {FACE_W}-wide face cannot centre on a {body_w}-wide body')
H, OFF = GEOM_MD_COMPACT[GAP]
assert (body_h - H) % 2 == 0, f'a {H}-row face cannot split {body_h} rows evenly'
CY = (Y0 + Y1 + 1 - H) // 2 - OFF

box, FACE = measure(16, CY, 'md', 'compact', GAP)
assert (box['h'], box['y'] - CY) == (H, OFF), 'mark.ts disagrees with the table'
assert box['w'] == FACE_W, f"mark.ts says the face is {box['w']} wide"
ABOVE, BELOW = box['y'] - Y0, Y1 - box['bottom']
assert ABOVE == BELOW, f'air {ABOVE}/{BELOW} on the body'
assert box['x'] + box['right'] == 31, 'face is not centred on x=16'
assert FACE <= BODY and not (FACE & TAIL), 'the face is not on the body'
assert FACE <= CORE, 'the face does not sit entirely on the plain core'
eyes = {p for p in FACE if p[1] < box['y'] + 4}
smile = {p for p in FACE if p[1] >= box['bottom'] - 1}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert {(x + 5, y) for x, y in eyes if x < 16} == {p for p in eyes if p[0] >= 16}, \
    'the two Zs are not the same letter'
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric'

# ---------------------------------------------------------------------------
ORDER = [(layers[RAMP[-1]], RAMP[-1])]
ORDER += [(layers[c], c) for c in RAMP[-2::-1]]
ORDER += [(layers[KEY], KEY)]

print(f'{SLUG} {NAME}')
print(f'  body {body_w}x{body_h} y{Y0}-{Y1} (superellipse n={N}) · tail y24-29 · '
      f'silhouette x{xs[0]}-{xs[-1]} y{ys[0]}-{ys[-1]}')
print(f'  face md/compact gap{GAP} = {FACE_W}x{H} at x{box["x"]}-{box["right"]} '
      f'y{box["y"]}-{box["bottom"]}, cy={CY} · air {ABOVE} above / {BELOW} below')
print(f'  ramp {" ".join(RAMP)}  (anchor {ANCHOR} = {BRAND}, chroma step {DC})')
print(f'  steps ΔE {" ".join(f"{d:.2f}" for d in STEP_DE)}  mean {MEAN:.2f} '
      f'(c45 {C45_STEP})  total {TOTAL:.2f} (c45 {C45_TOTAL})')
print(f'  coverage {[len(layers[c]) for c in RAMP]} · keyline {len(layers[KEY])} · '
      f'face {len(FACE)} · {len(layers) + 1} tones')

if '--show' in sys.argv:
    show([layers[KEY]] + [layers[c] for c in RAMP] + [FACE],
         ['0', '1', '2', '3', '4', '5', '6', '@'])

# ---------------------------------------------------------------------------
rows_svg = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in ORDER)

if '--svg' in sys.argv:
    # Standalone dump, for looking at a variant without writing it into src.
    dest = Path(sys.argv[sys.argv.index('--svg') + 1])
    face_svg = ''.join(f'<path d="{d}"/>' for d in to_paths(FACE))
    dest.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
        f'shape-rendering="crispEdges">{rows_svg}'
        f'<g fill="{INK}">{face_svg}</g></svg>')
    print(f'  dumped {dest}')
    sys.exit()

(OUT / f'{SLUG}.astro').write_text(f'''---
/**
 * {SLUG} · {NAME}
 *
 * The Hozz mark's ramp, in purple, on the bubble.
 *
 * c45 was rasterised to the 32 grid and measured before this was drawn: six
 * stops from a light rim to a deeper centre, mean step ΔE 5.21, ΔE 26.07 end to
 * end, each step a little darker and a little more chromatic than the last, a
 * 1px keyline outside the ramp rather than part of it, and an 8x8 face on a
 * 22-row body with seven rows of air above and seven below. Every one of those
 * numbers is held here. Only the hue and the silhouette move.
 *
 * Purple cannot be anchored where pale blue was — a near-white rim would stop
 * being Twitch — so the ramp is anchored by its middle instead: stop 3 of 6 is
 * {BRAND}, the purple Twozz already ships, exactly. Three stops climb off it to
 * the rim, two fall away under the face. At a glance the bubble is the colour
 * it has always been; up close it is a surface. Only the chroma rise is
 * compromised, because {BRAND} is already at the edge of what sRGB has at that
 * lightness; the rest of the step is spent on lightness, and the step size —
 * the thing the eye actually reads — matches.
 *
 * Rim to centre had to be worked out for a bubble. Peeling contour rings the way
 * a disc takes them erodes diagonals faster than sides, and six peels of this
 * body leave a 16x10 rectangle with a pixel off each corner — a box inside a
 * curve, which is exactly what the slab check is for. So the bands are seven
 * nested superellipses on one centre, each a pixel in from the last: true
 * parallels of the outline, corners that keep shrinking, a core with no corners
 * left to speak of. Run the generator with --rings to see the version that was
 * rejected.
 *
 * Whether the tail takes the ramp was measured, not chosen. Peel the whole
 * silhouette and no pixel in the tail is more than four deep, so the body's own
 * law would give it the first two tones over a handful of pixels — at 96px that
 * is not a surface, it is a 2x2 smudge floating in a flap five pixels wide. The
 * tail takes the rim tone flat, which is the tone the body carries at the join,
 * so the two read as one skin. --ramp-tail renders the alternative.
 *
 * The tail is built the way the shipped mark builds its own: one straight left
 * edge continuing the body's bottom-left curve, the taper taken entirely from
 * the right. Narrowing on both sides at once turns a tail into a diagonal
 * stroke. Once the keyline has taken the outer ring the fill runs 6-5-4-3-2 and
 * only the last row is pure line. The outline goes round the outside of the
 * whole shape, once.
 *
 * {len(layers) + 1} tones. Body symmetric about x=16 — the tail, deliberately, is not.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {NAME}">
{rows_svg}
  <g fill="{INK}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {CY}, size: 'md', smile: 'compact', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in [KEY, *RAMP[::-1], INK])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'c45\\u2019s ramp measured off the grid and rebuilt in purple: six stops, mean step \\u0394E {MEAN:.2f} against its 5.21, anchored so stop 3 is the shipped {BRAND} exactly. Nested superellipses instead of peeled rings, so the corners stay round and the core is a blob, not a box. The tail takes the rim tone flat \\u2014 it is too thin to hold a ramp.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
