
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

# The parts, by how many pixels in a pixel is. The keyline eats depth 0 almost
# everywhere; depth 1 is the rim; 2-4 are the bevel; 5 is the groove; everything
# deeper is the field. Note the groove is RAMP[5], the darkest stop, and the
# field is RAMP[4] — a step back *up*. Six stops that only ever darken read as a
# gradient no matter how many there are; one reversal gives the eye a seam.
PART = {0: 'rim', 1: 'rim', 2: 'bevel-1', 3: 'bevel-2', 4: 'bevel-3',
        5: 'groove', 6: 'field'}
TONE = {'rim': RAMP[0], 'bevel-1': RAMP[1], 'bevel-2': RAMP[2],
        'bevel-3': RAMP[3], 'groove': RAMP[5], 'field': RAMP[4]}
ORDER_PARTS = ['rim', 'bevel-1', 'bevel-2', 'bevel-3', 'groove', 'field']
assert set(TONE.values()) == set(RAMP), 'a stop is going unused'
assert lab(TONE['groove'])[0] < lab(TONE['field'])[0], 'the groove must be the darker of the two'

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
# depth; the tail flat at the rim tone.
#
# Whether the tail takes the ramp was measured, not chosen: peel the silhouette
# and nothing in the tail is more than four deep, so the body's own law would
# give it two tones over a handful of pixels — a 2x2 smudge in a flap, a stain
# rather than a surface. Flat rim is also what the body carries at the join, so
# the two read as one skin. --ramp-tail draws the alternative.
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
part = {p: PART[depth[p]] for p in BODY}
paint = {p: TONE[part[p]] for p in BODY}
for p in TAIL:
    part[p] = 'rim'
    paint[p] = RAMP[min(max(DEPTH[p] - 2, 0), INSETS - 1)] if '--ramp-tail' in sys.argv \
        else RAMP[0]
JUNCTION = {p for p in BODY if depth[p] == 0 and p not in OUTLINE}
EXEMPT = JUNCTION | {(31 - x, y) for x, y in JUNCTION}
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
FIELD = parts['field']
assert not is_slab(FIELD, BODY), 'the field reads as a box dropped in the bubble'
for nm in ORDER_PARTS:                       # every part, inside the body, mirrors
    assert all((31 - x, y) in parts[nm] for x, y in parts[nm] & BODY), \
        f'{nm} is not symmetric'
body_only = {p: f for p, f in paint.items() if p in BODY and p not in EXEMPT}
assert all(body_only.get((31 - x, y)) == f for (x, y), f in body_only.items()), \
    'the body is not symmetric about x=16'
assert len(EXEMPT) < 24, f'{len(EXEMPT)} px exempted for the tail is too many'
# the bevel must read as a run of even steps, and the rim and groove as single
# lines, or "parts" is just a word
assert len(parts['rim'] & BODY) > len(parts['bevel-1']), 'the rim has lost the outside'
for nm in ('bevel-1', 'bevel-2', 'bevel-3'):
    assert 40 <= len(parts[nm]) <= 110, f'{nm} is {len(parts[nm])} px — not a 1 px step'
assert len(parts['groove']) < len(parts['bevel-3']), 'the groove is wider than a line'
assert len(FIELD) > 1.5 * len(parts['groove']), 'the field is not the biggest part'

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
assert FACE <= FIELD, 'the face does not sit entirely on the field'
assert FACE_W / body_w >= 0.35, 'the face is small for the body again'
eyes = {p for p in FACE if p[1] < box['y'] + 5}
smile = {p for p in FACE if p[1] >= box['bottom'] - 1}
assert eyes | smile == FACE, 'unexpected rows between the eyes and the smile'
assert all((31 - x, y) in smile for x, y in smile), 'smile is not symmetric'

# ---------------------------------------------------------------------------
ORDER = [(layers[TONE['field']], TONE['field'])]
ORDER += [(layers[TONE[nm]], TONE[nm]) for nm in ('groove', 'bevel-3', 'bevel-2',
                                                  'bevel-1', 'rim')]
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
print(f'  face {len(FACE)} px on a {len(FIELD)} px field · {len(layers) + 1} tones')

if '--show' in sys.argv:
    show([parts['keyline']] + [parts[nm] for nm in ORDER_PARTS] + [FACE],
         ['0', '1', '2', '3', '4', 'g', 'F', '@'])

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
 * Inward from the outline: a 1px keyline, a 1px **rim** at the lightest stop, a
 * three-step **bevel** a pixel to a step, a 1px **groove** at the *darkest*
 * stop, and then the **field** one step back up, which is the plane the face
 * sits on. That single reversal at the groove is the whole trick — six stops
 * that only ever darken read as a gradient however many there are, and the eye
 * cannot say where one thing ends and the next begins. The shells also relax
 * from n=3.6 at the outline to n=2.3 at the field, so the field's edge is a
 * soft oval inside a squarish bubble rather than another parallel band.
 *
 * The face is lg — 10 wide in a 28-wide body, the shipped mark's own ratio,
 * {len(FACE)} px of ink on a {len(FIELD)} px field. It is the subject of the mark, not
 * something the mark contains. The body is 24 rows so a 10-row face still
 * splits its air {ABOVE}/{BELOW}.
 *
 * The tail is {TW} across and {len(TAIL_ROWS)} deep, an aspect of {TW / len(TAIL_ROWS):.1f} against the shipped
 * mark's 1.5. Mass is stubbiness, not length: the first version ran six rows and
 * tapered from both ends, and read as a hairline flick off the corner. Straight
 * left edge continuing the body's corner, the whole taper from the right, flat
 * at the rim tone because peeling the silhouette shows nothing in the tail is
 * more than four pixels deep — the ramp would leave a smudge, not a surface.
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
  idea: 'c45\\u2019s ramp measured off the grid and rebuilt in purple, then spent on parts \\u2014 rim, three-step bevel, a groove at the darkest stop, and the field a step back up. The reversal is what lets the eye find the seams. Face is lg, {len(FACE)} px of ink on a {len(FIELD)} px field, air {ABOVE}/{BELOW}; the tail is {TW}x{len(TAIL_ROWS)}, stubby like the shipped one. Stop 3 is #8f52f6 exactly.',
  ground: 'light',
  palette: [{palette}],
}};
''')
print('  written')
