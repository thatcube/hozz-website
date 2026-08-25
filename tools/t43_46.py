"""Generate t43–t46: one broad live-presence carrier, lit four ways.

The brief for the fourth sibling's chat mark keeps widening — Twitch, YouTube
and Kick all have to recognise it — so the silhouette here is deliberately the
plainest thing in the set: a broad rounded bubble, 28 across, with a tail that
grows straight down out of the bottom-left corner rather than being pinned on
as a wedge. No platform glyph, no play triangle. If a mark needs a triangle to
say "live", it is not the mark saying it.

The four variants are a controlled experiment. Silhouette, keyline, face
placement and the depth ramp are byte-identical across all four. The single
variable is where the light comes from:

  t43  nowhere      pure contour falloff, the Hozz lens rule
  t44  upper-left   the Mozz key, a broad lit rim falling to a deep shoulder
  t45  the tail     lit from the mouth the voice leaves, falling off around
  t46  top + bounce a key overhead and a weak return off the lower-right

Every tone is a function of contour depth, so no layer can come out as a
rectangle dropped into the middle — the failure mode this repo keeps rejecting.
The field the face sits on is one flat tone in all four, because depth 8 and
deeper is clamped to a single index and the whole face box is deeper than 8.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import is_slab, to_paths  # noqa: E402
from face_py import face_box  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
PREVIEW = ROOT / '.briefs/t43'

GRID = 32
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# --------------------------------------------------------------------------
# Silhouette
# --------------------------------------------------------------------------

# Corner inset per row, read inward from the top. 5,3,2,1,1 rasterises a radius
# that steps 4,2,2,0,2 across — the doubled row is the same idiom as the
# canonical circles, and it is why the corner reads round rather than chamfered.
CORNER = [5, 3, 2, 1, 1]
BODY_TOP, BODY_BOTTOM = 2, 23
TAIL = {24: (7, 14), 25: (7, 12), 26: (7, 10), 27: (7, 9)}


def build_body():
    out = set()
    for y in range(BODY_TOP, BODY_BOTTOM + 1):
        top, bottom = y - BODY_TOP, BODY_BOTTOM - y
        if top < len(CORNER):
            ins = CORNER[top]
        elif bottom < len(CORNER):
            ins = CORNER[bottom]
        else:
            ins = 0
        out |= {(x, y) for x in range(2 + ins, GRID - 2 - ins)}
    return out


BODY = build_body()
TAIL_PX = {(x, y) for y, (a, b) in TAIL.items() for x in range(a, b + 1)}
SHAPE = BODY | TAIL_PX


def check_silhouette(shape):
    """No spurs, no dents, and the tail must join the body without a step."""
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    assert ys == list(range(ys[0], ys[-1] + 1)), 'silhouette has a gap row'
    widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
    for i in range(1, len(widths) - 1):
        assert not (widths[i] > widths[i - 1] and widths[i] > widths[i + 1]), \
            f'spur at row {ys[i]}'
    # Every row is one unbroken run: a bubble has no holes or islands.
    for y in ys:
        xs = sorted(rows[y])
        assert xs == list(range(xs[0], xs[-1] + 1)), f'row {y} is broken'
    # The left edge never doubles back — that reads as a dent at the tail joint.
    lefts = [min(rows[y]) for y in ys]
    turn = lefts.index(min(lefts))
    assert lefts[:turn + 1] == sorted(lefts[:turn + 1], reverse=True)
    assert lefts[turn:] == sorted(lefts[turn:]), f'left edge doubles back: {lefts}'
    # The body is mirror-symmetric even though the tail is not.
    for x, y in shape:
        if y <= BODY_BOTTOM:
            assert (31 - x, y) in shape, f'body not symmetric at ({x}, {y})'


check_silhouette(SHAPE)


def depth_map(shape):
    """L1 distance to the outside: repeated 4-neighbour erosion."""
    out = {}
    cur = set(shape)
    d = 1
    while cur:
        ring = {p for p in cur
                if any((p[0] + dx, p[1] + dy) not in cur for dx, dy in NEIGHBOURS)}
        for p in ring:
            out[p] = d
        cur -= ring
        d += 1
    return out


DEPTH = depth_map(SHAPE)
KEYLINE = {p for p, d in DEPTH.items() if d == 1}

# --------------------------------------------------------------------------
# Face
# --------------------------------------------------------------------------

FACE_CX, FACE_CY = 16, 13
FACE = face_box(cx=FACE_CX, cy=FACE_CY, size='md', smile='compact', gap=2)
assert (FACE['w'], FACE['h']) == (8, 8), 'the supplied face is 8x8'
FACE_BOX = {(x, y)
            for y in range(FACE['y'], FACE['y'] + FACE['h'])
            for x in range(FACE['x'], FACE['x'] + FACE['w'])}
assert FACE_BOX <= BODY, 'the face must sit inside the body, tail ignored'

AIR_ABOVE = FACE['y'] - BODY_TOP
AIR_BELOW = BODY_BOTTOM - (FACE['y'] + FACE['h'] - 1)
assert AIR_ABOVE == AIR_BELOW, f'unequal air: {AIR_ABOVE}/{AIR_BELOW}'
assert FACE['x'] + FACE['w'] / 2 == 16, 'face is not centred on x=16'

# --------------------------------------------------------------------------
# Tones
# --------------------------------------------------------------------------

# Indigo-violet, one hue, nine steps. Twitch's association survives the pull
# toward indigo, and the deepening is what lets the white face clear 4.5:1 on
# every tone it can touch — #8f52f6, the shipped Twozz purple, does not.
RAMP = [
    '#cf9ff2',  # 0 specular: only where the rim faces the light square on
    '#be8fec',  # 1 lit rim
    '#ae7fe5',  # 2
    '#9d6fdf',  # 3
    '#8c5fd8',  # 4
    '#7c4fd2',  # 5
    '#6b40cb',  # 6
    '#5a30c4',  # 7 the field the face sits on
]
INK = '#190f31'
FIELD_INDEX = 7
FIELD_DEPTH = 8


def lit(nx, ny, light):
    """How square-on this bit of rim faces the light, in [-1, 1]."""
    lx, ly = light
    n = (nx * nx + ny * ny) ** 0.5 or 1.0
    return (nx * lx + ny * ly) / n


def centre_normal(p):
    """Outward direction at p, measured from the body's optical centre."""
    return p[0] + 0.5 - 16.0, p[1] + 0.5 - 13.0


def shade(s):
    """0 where the rim faces the light square on, 1 where it faces away."""
    return min(max((0.38 - s) / 0.95, 0.0), 1.0)


def field_distance():
    """Steps from the flat field out to each pixel, around the contour."""
    from collections import deque

    body = {p for p in SHAPE if DEPTH[p] > 1}
    dist = {p: None for p in body}
    queue = deque()
    for p in body:
        if DEPTH[p] >= FIELD_DEPTH:
            dist[p] = 0
            queue.append(p)
    while queue:
        p = queue.popleft()
        for dx, dy in NEIGHBOURS:
            q = (p[0] + dx, p[1] + dy)
            if q in dist and dist[q] is None:
                dist[q] = dist[p] + 1
                queue.append(q)
    return dist


DIST = field_distance()

# How many of the outermost bands the shade swallows where the light is fully
# off the form. Three is enough to be read as a direction and not enough to
# flatten the rim into one plate.
SWALLOW = 2.6


def tones(shade_fn):
    """Falloff measured outward from the field, tilted by the light.

    Tone is distance from the flat field, so every band follows the contour and
    the field the face sits on is untouched by construction. The light does not
    tint anything: where the form turns away it *swallows* the outer bands, so
    the deep tone comes right up to the keyline in the shade and the falloff
    opens out broad and soft into the light. That is what a lit object does,
    and it is the only directional shading that cannot strand a dark band
    inside the field.
    """
    smoothed = {}
    for p in DIST:
        vals = [shade_fn(p)]
        for dx, dy in NEIGHBOURS:
            q = (p[0] + dx, p[1] + dy)
            if q in DIST:
                vals.append(shade_fn(q))
        smoothed[p] = sum(vals) / len(vals)

    idx = {}
    for p, d in DIST.items():
        depth = DEPTH[p]
        if depth >= FIELD_DEPTH:
            idx[p] = FIELD_INDEX
            continue
        swallowed = SWALLOW * smoothed[p]
        # Only the outermost bands are swallowed, so the light's effect has
        # faded out before the falloff reaches the field.
        eaten = min(max(swallowed - (depth - 2), 0.0), swallowed)
        idx[p] = min(max(round(FIELD_INDEX - d + eaten), 0), FIELD_INDEX)

    # Rounding two smooth terms can still leave a pixel one step too deep at a
    # terminator. Lightening it is always safe — the field is the deepest tone
    # and is never touched — and the pass only ever decreases, so it settles.
    for _ in range(16):
        changed = False
        for p in idx:
            if DEPTH[p] >= FIELD_DEPTH:
                continue
            for dx, dy in NEIGHBOURS:
                q = (p[0] + dx, p[1] + dy)
                if q in idx and idx[p] - idx[q] > 1:
                    idx[p] = idx[q] + 1
                    changed = True
        if not changed:
            break
    return idx


def none_light(_p):
    return 0.0


def key_upper_left(p):
    return shade(lit(*centre_normal(p), (-0.72, -0.70)))


def tail_light(p):
    """Struck from the mouth — the tail, off the bottom-left of the body."""
    return shade(lit(*centre_normal(p), (-0.55, 0.84)))


def key_and_bounce(p):
    nx, ny = centre_normal(p)
    key = lit(nx, ny, (0.0, -1.0))
    # A narrow return, squared so it stays a pool at the lower right instead of
    # lifting the whole bottom rim back to the key's level.
    lobe = max(lit(nx, ny, (0.76, 0.65)), 0.0)
    return shade(max(key, lobe * lobe * 0.78))


VARIANTS = [
    ('t43', 'Broad Carrier', none_light,
     'The plainest reading of the widened brief: one broad bubble, tail grown '
     'out of the bottom-left corner rather than pinned to it, and the whole '
     'tone spend in a contour falloff that steps from a light rim down to the '
     'flat field the face sits on. No light source, so nothing about it dates '
     'or leans; the depth alone gives it a body.'),
    ('t44', 'Key Light', key_upper_left,
     'The same carrier under the Mozz key. The rim is broad and bright at the '
     'upper left and gathers into a deep shoulder at the lower right, so the '
     'bubble reads as a lit object in a room rather than a flat sticker — the '
     'one thing a live-presence mark can borrow from a physical form.'),
    ('t45', 'Mouth Light', tail_light,
     'Lit from the tail. The tail is the mouth the voice leaves, so the light '
     'is brightest where the bubble meets it and falls off around the far '
     'shoulder — the falloff runs the same way the sound does, which no other '
     'variant here or in the shipped family does.'),
    ('t46', 'Key and Return', key_and_bounce,
     'A key overhead and a weak return off the lower right. Two sources is '
     'what a screen-lit room actually does to a rounded object, and the second '
     'lifts the bottom rim just enough that the silhouette stays readable when '
     'the mark is small and dark-on-dark.'),
]


def rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


assert all(max(abs(a - b) for a, b in zip(rgb(l), rgb(r))) <= 24
           for l, r in zip(RAMP, RAMP[1:])), 'ramp steps are too coarse'


def build(slug, name, off_fn, idea):
    idx = tones(off_fn)
    layers = {}
    for p, i in idx.items():
        layers.setdefault(i, set()).add(p)

    used = sorted(layers)
    assert set(idx) | KEYLINE == SHAPE, 'some pixels are unpainted'
    assert not (set(idx) & KEYLINE), 'a tone layer overlaps the keyline'
    assert KEYLINE == {p for p, d in DEPTH.items() if d == 1}, 'keyline is not exact'
    assert len(used) >= 7, f'{slug}: only {len(used)} tones'

    # The face sits on one flat tone, and clears 4.5:1 on it and on whatever
    # touches it.
    field = layers[FIELD_INDEX]
    assert FACE_BOX <= field, f'{slug}: the face field is not flat'
    touching = {idx[q] for p in FACE_BOX for dx, dy in NEIGHBOURS
                if (q := (p[0] + dx, p[1] + dy)) in idx}
    for i in touching:
        assert contrast('#ffffff', RAMP[i]) >= 4.5, \
            f'{slug}: white on {RAMP[i]} is {contrast("#ffffff", RAMP[i]):.2f}:1'

    for i, layer in layers.items():
        assert not is_slab(layer, SHAPE), f'{slug}: tone {i} reads as a slab'
    for p, i in idx.items():
        for dx, dy in NEIGHBOURS:
            q = (p[0] + dx, p[1] + dy)
            if q in idx:
                assert abs(i - idx[q]) <= 1, f'{slug}: tone skip at {p}'

    ordered = [(KEYLINE, INK)] + [(layers[i], RAMP[i]) for i in used]
    paths = '\n'.join(
        f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
        for layer, fill in ordered)
    palette = [INK] + [RAMP[i] for i in used] + ['#ffffff']

    doc = f'''---
/**
 * {slug[1:]} · {name}
 *
 * {idea}
 *
 * Silhouette, keyline, depth ramp and face placement are identical in t43–t46;
 * the light direction is the only variable, so the four can be compared.
 *
 * A 28-wide bubble, rows {BODY_TOP}–{BODY_BOTTOM}, with the tail grown down out of the
 * bottom-left corner: the tail's left edge continues the corner's own column,
 * so there is no step where the two meet and no wedge pinned on. Every tone is
 * a function of contour depth, so no layer can be a rectangle dropped inside
 * the outline. Depth {FIELD_DEPTH} and deeper is one flat tone, and the whole face box
 * is deeper than that, so the face never sits on banding.
 *
 * The face is the supplied 8×8 — `md`, `compact`, gap 2 — centred on the
 * bubble body with the tail ignored: {AIR_ABOVE} rows of air above and {AIR_BELOW} below.
 *
 * {len(palette) - 1} purple tones, keyline included.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Strozz — {name}">
{paths}
  <g fill="#ffffff" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: {FACE_CX}, cy: {FACE_CY}, size: 'md', smile: 'compact', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''
    (OUT / f'{slug}.astro').write_text(doc)

    meta = "export default {\n" \
        f"  n: '{slug}', name: '{name}',\n" \
        f"  idea: '{idea.replace(chr(39), chr(92) + chr(39))}',\n" \
        "  ground: 'light',\n" \
        f"  palette: {palette!r},\n".replace("'", "'") + "};\n"
    (OUT / f'{slug}.meta.ts').write_text(meta)

    PREVIEW.mkdir(parents=True, exist_ok=True)
    face = _face_paths()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
           f'shape-rendering="crispEdges">\n{paths}\n'
           '  <g fill="#ffffff">'
           + ''.join(f'<path d="{d}"/>' for d in face)
           + '</g>\n</svg>\n')
    (PREVIEW / f'{slug}.svg').write_text(svg)
    return slug, name, len(palette) - 1, used


def _face_paths():
    from face_py import face_paths
    return face_paths(cx=FACE_CX, cy=FACE_CY, size='md', smile='compact', gap=2)


if __name__ == '__main__':
    for slug, name, off_fn, idea in VARIANTS:
        s, n, tones_used, used = build(slug, name, off_fn, idea)
        print(f'{s} {n:<16} {tones_used} purple tones, indices {used}')
    print(f'face air {AIR_ABOVE}/{AIR_BELOW}, '
          f'field contrast {contrast("#ffffff", RAMP[FIELD_INDEX]):.2f}:1')
