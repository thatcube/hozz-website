"""t11 — Twozz, the direct sibling of c45 · Ripple, Lens.

c45 was rasterised to the 32 grid and measured before anything was drawn here:

    6 stops, rim -> centre    #edf6fc #dcecf6 #cae1f1 #b9d7eb #a7cce6 #96c2e0
    step size                 ΔE 4.97 5.69 4.95 5.67 4.88  (mean 5.21)
    total rim -> centre       ΔE 26.07,  ΔL 20.0
    direction per step        L -4.0, chroma +3.3
    parts                     a light rim, a stepped ramp inward, a deeper
                              centre, rings outside — the eye can find the
                              seams even though every step is small

This is that system in purple, on the bubble. Same six stops, same mean step
(held to c45's 5.21 by construction and asserted). What changed after the first
review is everything the tone count could not see.

**The face.** md (8 wide) in a 28-wide body left the face floating in a violet
field — the exact note the client has made all along, that a mark should *be* a
face rather than contain one. It is now lg, 10 wide, the same ratio the shipped
mark uses, and the body grew to 24 rows so a 10-row face still splits its air
7/7. The face is 40 px of ink on a 282 px plate: it is the subject, not an inset.

**The parts.** Six stops spent as an even wash is still a wash — every step does
the same thing as the one before, so the eye finds no seam. The first rebuild
spent them as six even 1px contours and still looked airbrushed. What makes a
part legible is *area* and a *boundary*, so the stops are spent as named parts
of very unequal size:

    keyline  1 px                            the outline
    rim      1 px, the lightest stop         the lit outer edge
    bevel    1 px, one stop down             the edge turning away
    step     1 px, one more                  where the wall starts to face you
    plate    the whole middle, brand purple  the plane the face sits on
    shadow   under the belly, 3 stops down   the underside, in shade
    floor    beneath it, one stop back up    light bouncing off the ground

Within a part the neighbour step is still c45's ΔE 5. Between parts it is not:
bevel to shadow is ΔE 15.5, three steps at once, because a seam has to be
visible. The shadow is placed by surface normal rather than by height — a y
split laid a hard horizontal seam straight across both side walls at the
equator — so it wraps only what faces downward. The shells also relax from a
squarish superellipse (n=3.6, close to the shipped silhouette) to a soft oval
(n=2.3) as they go in, so the plate's edge is not parallel to the outline and
reads as a different part rather than another band.

**The tail.** A tail is what makes the silhouette a speech bubble, and the first
version's — six rows, tapering from both the top and the tip — read as a
hairline flick. Mass is stubbiness, not length: the shipped tail is 6 px across
and 4 rows deep, an aspect of 1.5. This one is 8 across and 4 deep, aspect 2.0,
with a straight left edge continuing the body's corner and the taper taken
entirely from the right. Interior widths after the keyline run 6-5-3.

**The hue.** Purple cannot be anchored where blue was — a near-white rim stops
being Twitch — so the ramp is anchored by its *middle*: stop 3 of 6 is #8f52f6,
the purple Twozz already ships, exactly. #8f52f6 is already at C 94 and sRGB has
nothing more saturated at that lightness, so the per-step chroma rise is taken as
far as the gamut allows and the rest of the ΔE budget goes to lightness. The step
*size* is what the eye reads, and that is matched.
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
# Geometry. Body 28x24 on x2-29 / y2-25 — the shipped mark's proportion, which
# is what makes a 10-wide face read as the subject. Tail below it, to y29.
#
# The shells relax as they go in: n=3.6 at the outline (a hair rounder than the
# shipped rounded rect, and matching its row profile to within 2 px) down to
# n=2.3 at the innermost. So the field's edge is a soft oval inside a squarish
# bubble — not a parallel of the outline, which is what stops it reading as one
# more band and starts it reading as a different part.
# ---------------------------------------------------------------------------
X0, X1, Y0, Y1 = 2, 29, 2, 25
CX, CYY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2
N_OUT, N_IN = 3.6, 2.3
INSETS = 6


def shell(i):
    """The body, `i` pixels in. Centred on x=16.0, so it mirrors exactly."""
    n = N_OUT + (N_IN - N_OUT) * (i / INSETS)
    a, b = (X1 + 1 - X0) / 2 - i, (Y1 + 1 - Y0) / 2 - i
    return {(x, y)
            for y in range(Y0, Y1 + 1) for x in range(X0, X1 + 1)
            if (abs(x + 0.5 - CX) / a) ** n + (abs(y + 0.5 - CYY) / b) ** n <= 1 + 1e-9}


SHELLS = [shell(i) for i in range(INSETS + 1)]
BODY = SHELLS[0]
for i in range(INSETS):
    assert SHELLS[i + 1] < SHELLS[i], f'shell {i + 1} is not inside shell {i}'

# The parts, by how many pixels in a pixel is — and, below the equator, by the
# fact that light comes from above. An even ramp inward is a wash however many
# stops it has: every step does the same thing as the one before, so the eye
# finds no seam. These stops are clustered instead.
#
#   depth 1   rim        RAMP[0]   the lit outer edge, 1 px
#   depth 2   bevel      RAMP[1]   the wall, 1 px
#   depth 3   facing up  RAMP[2]   the wall stepping down into the plate
#             facing down RAMP[5]  ...or, underneath, dropping three stops into shadow
#   depth 4   facing down RAMP[4]  the shadow lifting back toward the plate
#   otherwise            RAMP[3]   the plate: one flat tone, the brand purple,
#                                  the largest area in the mark, carrying the face
#
# So the top and sides step gently — three subtle stops and then flat — and the
# underside drops hard into a two-pixel shadow and comes back up. Same six stops,
# same step size between neighbours; what changed is that they are spent where a
# surface actually changes instead of being spread evenly.
#
# "Facing down" is the surface normal, not the half of the picture: on a
# superellipse the normal turns from sideways to downward where (dy/b)^n
# overtakes (dx/a)^n, so the shadow covers the underside and the bottom corners
# and stops before it climbs the side walls. Splitting on y alone puts a hard
# horizontal seam across both walls at the equator, which reads as a glitch.
A0, B0 = (X1 + 1 - X0) / 2, (Y1 + 1 - Y0) / 2


def faces_down(p):
    dx, dy = abs(p[0] + 0.5 - CX) / A0, (p[1] + 0.5 - CYY) / B0
    return dy > 0 and dy ** N_OUT > dx ** N_OUT


def part_of(p):
    d, down = depth[p], faces_down(p)
    if d <= 1:
        return 'rim'
    if d == 2:
        return 'bevel'
    if d == 3:
        return 'shadow' if down else 'step'
    if d == 4 and down:
        return 'floor'
    return 'plate'


TONE = {'rim': RAMP[0], 'bevel': RAMP[1], 'step': RAMP[2], 'plate': RAMP[3],
        'floor': RAMP[4], 'shadow': RAMP[5]}
ORDER_PARTS = ['rim', 'bevel', 'step', 'shadow', 'floor', 'plate']
assert set(TONE.values()) == set(RAMP), 'a stop is going unused'
assert lab(TONE['shadow'])[0] < lab(TONE['floor'])[0] < lab(TONE['plate'])[0], \
    'the shadow must be the darkest of the three and lift back toward the plate'

# The tail. Mass is stubbiness, not length: the shipped tail is 6 across and 4
# rows deep. This one is 8 across and 4 deep, straight down the left the way the
# shipped one is built, with the whole taper taken from the right. A tail that
# narrows from both sides turns into a diagonal stroke; one that runs six rows
# turns into a flick.
TAIL_ROWS = {26: (9, 16), 27: (9, 15), 28: (9, 14), 29: (9, 12)}
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
TOP = min(TAIL_ROWS)
assert set(range(*TAIL_ROWS[TOP])) <= set(rows[TOP - 1]), 'tail overhangs the body'
prev = None
for y in sorted(TAIL_ROWS):
    a, b = TAIL_ROWS[y]
    if prev:
        assert a == prev[0], 'the tail must keep one straight edge'
        assert b <= prev[1], 'the tail flares instead of tapering'
    prev = (a, b)
TW = max(b - a + 1 for a, b in TAIL_ROWS.values())
assert TW / len(TAIL_ROWS) >= 1.4, (
    f'tail is {TW} across and {len(TAIL_ROWS)} deep — the shipped one is 1.5 '
    f'wider than deep, and anything leaner reads as a flick')

# ---------------------------------------------------------------------------
# Paint. One keyline around the whole silhouette; the parts inside the body by
# depth; the tail flat at the plate tone.
#
# Whether the tail takes the ramp was measured, not chosen: peel the silhouette
# and nothing in the tail is more than four deep, so the body's own law would
# give it two tones over a handful of pixels — a 2x2 smudge in a flap, a stain
# rather than a surface. Flat at the plate tone, because the tail's face is
# coplanar with the plate: same plane, same tone, so the two read as one skin.
# --ramp-tail draws the alternative.
# ---------------------------------------------------------------------------
DEPTH = {}
_r, _rem = rings(SIL, INSETS)
for _i, _ring in enumerate(_r, 1):
    for _p in _ring:
        DEPTH[_p] = _i
for _p in _rem:
    DEPTH[_p] = INSETS + 1
assert max(DEPTH[p] for p in TAIL) <= 4, 'the tail is deep enough to need the ramp'

OUTLINE = keyline(SIL)
depth = {p: max(i for i in range(INSETS + 1) if p in SHELLS[i]) for p in BODY}
part = {p: part_of(p) for p in BODY}
paint = {p: TONE[part[p]] for p in BODY}
for p in TAIL:
    part[p] = 'plate'
    paint[p] = RAMP[min(max(DEPTH[p] - 2, 0), INSETS - 1)] if '--ramp-tail' in sys.argv \
        else TONE['plate']
# The only asymmetry the mark is allowed: where the tail hangs off it, the body's
# bottom row keeps a fill instead of turning into keyline. Exactly those pixels
# and their mirrors are exempt from the symmetry check — nothing else. They take
# the tail's tone, not the rim's: a rim light exists because there is an edge
# there, and where the tail joins there is no edge, so the rim is interrupted.
JUNCTION = {(x, Y1) for x in range(TAIL_ROWS[TOP][0], TAIL_ROWS[TOP][1] + 1)} & BODY
EXEMPT = JUNCTION | {(31 - x, y) for x, y in JUNCTION}
assert len(EXEMPT) <= 2 * TW, f'{len(EXEMPT)} px exempted, more than the tail is wide'
assert all(y == Y1 for _, y in EXEMPT), 'the exemption has crept off the tail row'
for p in JUNCTION:
    part[p] = 'plate'
    paint[p] = TONE['plate']
for p in OUTLINE:
    paint[p] = KEY
    part[p] = 'keyline'

parts = {}
for p, nm in part.items():
    parts.setdefault(nm, set()).add(p)
layers = {}
for p, f in paint.items():
    layers.setdefault(f, set()).add(p)

assert set(paint) == SIL, 'the silhouette is not exactly covered'
assert len(layers) == INSETS + 1, f'{len(layers)} fills, expected {INSETS + 1}'
PLATE = parts['plate']
assert not is_slab(PLATE, BODY), 'the plate reads as a box dropped in the bubble'
for nm in ORDER_PARTS:                       # every part, inside the body, mirrors
    assert all((31 - x, y) in parts[nm] for x, y in parts[nm] & BODY if (x, y) not in EXEMPT), \
        f'{nm} is not symmetric'
body_only = {p: f for p, f in paint.items() if p in BODY and p not in EXEMPT}
assert all(body_only.get((31 - x, y)) == f for (x, y), f in body_only.items()), \
    'the body is not symmetric about x=16'

# the bands must read as single lines and the plate as one flat field, so
# lines, or "parts" is just a word
assert len(parts['rim'] & BODY) > len(parts['bevel']), 'the rim has lost the outside'
assert len(PLATE) > 2 * max(len(parts[nm] & BODY) for nm in ORDER_PARTS if nm != 'plate'), \
    'the plate is not decisively the largest area — the interior is a ramp again'
assert len(parts['shadow']) >= 20 and len(parts['floor']) >= 16, \
    'the shadow is too thin to read as a part'
for nm in ('shadow', 'floor'):
    assert all(faces_down(p) for p in parts[nm]), f'{nm} has crept onto a surface facing up'

# ---------------------------------------------------------------------------
# The face. lg/compact/gap2 — 10 wide, the shipped mark's ratio to this body.
# Geometry read back out of mark.ts, never computed.
# ---------------------------------------------------------------------------
GEOM_LG_COMPACT = {1: (9, -4), 2: (10, -5), 3: (11, -5), 4: (12, -6)}
FACE_W, GAP = 10, 2


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
H, OFF = GEOM_LG_COMPACT[GAP]
assert (body_h - H) % 2 == 0, f'a {H}-row face cannot split {body_h} rows evenly'
CY = (Y0 + Y1 + 1 - H) // 2 - OFF

box, FACE = measure(16, CY, 'lg', 'compact', GAP)
assert (box['h'], box['y'] - CY) == (H, OFF), 'mark.ts disagrees with the table'
assert box['w'] == FACE_W, f"mark.ts says the face is {box['w']} wide"
ABOVE, BELOW = box['y'] - Y0, Y1 - box['bottom']
assert ABOVE == BELOW, f'air {ABOVE}/{BELOW} on the body'
assert box['x'] + box['right'] == 31, 'face is not centred on x=16'
assert FACE <= BODY and not (FACE & TAIL), 'the face is not on the body'
assert FACE <= PLATE, 'the face does not sit entirely on the plate'
assert FACE_W / body_w >= 0.35, 'the face is small for the body again'
eyes = {p for p in FACE if p[1] < box['y'] + 5}
smile = {p for p in FACE if p[1] >= box['bottom'] - 2}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert {(x + 6, y) for x, y in eyes if x < 16} == {p for p in eyes if p[0] >= 16}, \
    'the two Zs are not the same letter'
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric'

# ---------------------------------------------------------------------------
ORDER = [(layers[c], c) for c in RAMP[::-1]]
ORDER += [(layers[KEY], KEY)]

print(f'{SLUG} {NAME}')
print(f'  body {body_w}x{body_h} y{Y0}-{Y1} (superellipse n={N_OUT}->{N_IN}) · '
      f'tail {TW}x{len(TAIL_ROWS)} y{TOP}-29 · silhouette x{xs[0]}-{xs[-1]} y{ys[0]}-{ys[-1]}')
print(f'  face lg/compact gap{GAP} = {FACE_W}x{H} at x{box["x"]}-{box["right"]} '
      f'y{box["y"]}-{box["bottom"]}, cy={CY} · air {ABOVE} above / {BELOW} below')
print(f'  ramp {" ".join(RAMP)}  (anchor {ANCHOR} = {BRAND}, chroma step {DC})')
print(f'  steps ΔE {" ".join(f"{d:.2f}" for d in STEP_DE)}  mean {MEAN:.2f} '
      f'(c45 {C45_STEP})  total {TOTAL:.2f} (c45 {C45_TOTAL})')
print('  parts ' + ' · '.join(f'{nm} {len(parts[nm])}' for nm in ORDER_PARTS)
      + f' · keyline {len(parts["keyline"])}')
print(f'  face {len(FACE)} px on a {len(PLATE)} px plate · {len(layers) + 1} tones')

if '--show' in sys.argv:
    show([parts['keyline']] + [parts[nm] for nm in ORDER_PARTS] + [FACE],
         ['0', '.', ':', '-', 'S', 's', 'P', '@'])

# ---------------------------------------------------------------------------
rows_svg = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in ORDER)

if '--svg' in sys.argv:
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
 * The Hozz mark's system, in purple, on the bubble — and rebuilt after review
 * so that the interior has parts instead of a wash.
 *
 * Six parts, not six steps. A 1px keyline; a **rim** at the lightest stop and a
 * **bevel** below it, the two thin bands that turn the outline into an edge; a
 * 1px **step** where the wall starts to face the viewer; then the **plate**,
 * {len(PLATE)} px of the brand purple, flat, by far the largest thing in the mark and
 * the plane the face sits on. Under the belly the plate drops three stops at
 * once into a **shadow**, with a **floor** one stop back up beneath it.
 *
 * The first attempt spent the same six stops as six even 1px contours and still
 * looked airbrushed: at 150px a 1px band is 5px of screen and every one did the
 * same thing as the last, so they blurred into a vignette. What makes a part
 * legible is area and a boundary — one large flat field, and a jump big enough
 * to see. The bevel-to-shadow drop is ΔE 15.5, three neighbour steps in one go,
 * because it is a boundary *between parts*; every step within a part is still
 * c45's own ΔE 5. Shadow is placed by surface normal, not by y: splitting on
 * height alone laid a hard seam straight across both side walls at the equator,
 * so the test is whether a pixel's face turns downward, which keeps the dark to
 * the underside and the two bottom corners. The shells also relax from n=3.6 at
 * the outline to n=2.3 inward, so the plate's edge is a soft oval inside a
 * squarish bubble rather than another parallel band.
 *
 * The face is lg — 10 wide in a 28-wide body, the shipped mark's own ratio,
 * {len(FACE)} px of ink on a {len(PLATE)} px plate. It is the subject of the mark, not
 * something the mark contains. The body is 24 rows so a 10-row face still
 * splits its air {ABOVE}/{BELOW}.
 *
 * The tail is {TW} across and {len(TAIL_ROWS)} deep, an aspect of {TW / len(TAIL_ROWS):.1f} against the shipped
 * mark's 1.5. Mass is stubbiness, not length: the first version ran six rows and
 * tapered from both ends, and read as a hairline flick off the corner. Straight
 * left edge continuing the body's corner, the whole taper from the right, and
 * flat at the plate tone: peeling the silhouette shows nothing in the tail is
 * more than four pixels deep, so a ramp would leave a smudge rather than a
 * surface, and the tail's face is coplanar with the plate, so it takes the
 * plate's tone. The rim light stops where the tail joins, because a rim exists
 * where there is an edge and there is no edge there.
 *
 * Colour is unchanged and is the point of holding onto this one: stop 3 of 6 is
 * {BRAND} exactly, so the bubble is the shipped purple at a glance and a
 * surface up close. Mean step ΔE {MEAN:.2f} against c45's {C45_STEP}.
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
    {{facePathsAt({{ cx: 16, cy: {CY}, size: 'lg', smile: 'compact', gap: {GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

palette = ', '.join(f"'{c}'" for c in [KEY, *RAMP[::-1], INK])
(OUT / f'{SLUG}.meta.ts').write_text(f'''export default {{
  n: '{SLUG}', name: '{NAME}',
  idea: 'c45\u2019s ramp measured off the grid and rebuilt in purple, then spent on parts rather than on a wash \u2014 keyline, lit rim, bevel, step, a big flat brand-purple plate, and a shadow and floor under the belly placed by surface normal. Steps inside a part are c45\u2019s \u0394E 5; the drop into shadow is three at once, because that is a seam. Face is lg, {len(FACE)} px of ink on a {len(PLATE)} px plate, air {ABOVE}/{BELOW}; the tail is {TW}x{len(TAIL_ROWS)} and takes the plate tone. Stop 3 is #8f52f6 exactly.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
