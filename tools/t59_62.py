"""Generate t59–t62: four controlled soft chat carriers.

The brief for this set is deliberately narrow. Earlier Twozz rounds drifted into
lenses, records, wavefronts and hardware; this one goes back to the thing a chat
mark actually is — the shape everyone already reads as a message — and spends
its whole budget on getting the *geometry* right first and the light right
second.

Three rules the four share, and the reason each exists:

**Valid body/tail geometry before anything else.** Every silhouette here is
asserted, not eyeballed: one 4-connected blob, no holes, one run per row and per
column, no pixel hanging on by a single neighbour, symmetric body, and a tail
that tapers monotonically. Four earlier marks were rejected in this project for
spurs and pasted-on wedges, so the checks run before a single tone is chosen.

**The tail is integrated at the lower left.** It is not a wedge stuck to a
rounded rectangle. The body's bottom-left corner is left square and the left
edge simply keeps going down past the bottom edge, then rakes back up to it —
the way the Material and Messages icons do it. Because the corner is spent on
the tail, the bottom edge comes out long and unbroken, which is the single
strongest cue that this is a message and not a blob.

**Contour falloff like Hozz, directional nuance like Mozz, calm centre.** The
tones are struck as contour rings peeled off the silhouette, so they bend around
every corner and the tail (c45's method). A small directional term biases the
rim toward the light, the way Mozz's disc is banded — but it is weighted by rim
proximity, so it dies out before it reaches the middle. The core is one flat
tone and the face sits entirely on it.

The face is supplied, never redrawn: `facePathsAt` at `md` / `compact` / gap 2,
which is exactly 8×8, centred on the **body** with the tail ignored.
"""

import colorsys
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from face_py import face_box, face_paths  # noqa: E402
from shade import is_slab, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"
PREVIEW = ROOT / ".briefs/t59-62"

GRID = 32
SAFE = (2, 2, 29, 29)
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def rrect(x0, y0, x1, y1, r, square=()):
    """Rounded rect as pixel centres, with named corners left square.

    Continuous extent is [x0, x1+1] x [y0, y1+1]; a pixel belongs when its
    centre is within `r` of the inner box. Sampling centres rather than corners
    is what keeps the arc symmetric — column x and column (x0+x1-x) mirror by
    construction.
    """
    out = set()
    left, right = x0 + r, x1 + 1 - r
    top, bottom = y0 + r, y1 + 1 - r
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px, py = x + 0.5, y + 0.5
            dx = max(left - px, px - right, 0.0)
            dy = max(top - py, py - bottom, 0.0)
            if dx == 0.0 or dy == 0.0:
                out.add((x, y))
                continue
            corner = ('w' if px < left else 'e') + ('n' if py < top else 's')
            if corner in square or dx * dx + dy * dy <= r * r:
                out.add((x, y))
    return out


def tail(x0, y_from, widths):
    """The lower-left tail: the left edge carried on down, then raked back up.

    `widths` is read top-down, so the taper is toward the tip. Nothing here is
    free-floating — row `y_from` sits directly under the body's bottom row and
    shares its left column, which is what makes the tail part of the silhouette
    rather than something attached to it.
    """
    out = set()
    for i, w in enumerate(widths):
        out |= {(x0 + k, y_from + i) for k in range(w)}
    return out


# --------------------------------------------------------------------------
# geometry validation — everything below the tone work depends on this passing
# --------------------------------------------------------------------------

def runs(shape, axis):
    """Contiguous runs per row (axis=0) or per column (axis=1)."""
    lines = {}
    for x, y in shape:
        key, val = (y, x) if axis == 0 else (x, y)
        lines.setdefault(key, []).append(val)
    out = {}
    for key, vals in lines.items():
        vals.sort()
        count, prev = 1, vals[0]
        for v in vals[1:]:
            if v != prev + 1:
                count += 1
            prev = v
        out[key] = (count, vals[0], vals[-1])
    return out


def connected(pixels):
    if not pixels:
        return False
    start = next(iter(pixels))
    seen, stack = {start}, [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in NEIGHBOURS:
            p = (x + dx, y + dy)
            if p in pixels and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(pixels)


def check_geometry(name, body, tail_px, spec):
    """Reject anything malformed before it can be shaded and admired."""
    shape = body | tail_px
    x0, y0, x1, y1 = SAFE
    xs = [x for x, _ in shape]
    ys = [y for _, y in shape]
    assert min(xs) >= x0 and max(xs) <= x1, f"{name}: outside the 28 safe area in x"
    assert min(ys) >= y0 and max(ys) <= y1, f"{name}: outside the 28 safe area in y"

    assert connected(shape), f"{name}: silhouette is in more than one piece"

    # No holes: the background inside the bounding box must reach the border.
    field = {(x, y) for x in range(-1, GRID + 1) for y in range(-1, GRID + 1)}
    outside = field - shape
    assert connected(outside), f"{name}: silhouette encloses a hole"

    for axis, label in ((0, "row"), (1, "column")):
        for key, (count, _, _) in runs(shape, axis).items():
            assert count == 1, f"{name}: {label} {key} is broken into {count} runs"

    # A pixel with one orthogonal neighbour is a nub, not a shape.
    for x, y in shape:
        touching = sum(1 for dx, dy in NEIGHBOURS if (x + dx, y + dy) in shape)
        assert touching >= 2, f"{name}: appendage pixel at {(x, y)}"

    # No spur: no row wider than both its neighbours, and none narrower.
    row_runs = runs(shape, 0)
    order = sorted(row_runs)
    widths = [row_runs[y][2] - row_runs[y][1] + 1 for y in order]
    for i in range(1, len(widths) - 1):
        assert not (widths[i] > widths[i - 1] and widths[i] > widths[i + 1]), \
            f"{name}: spur at row {order[i]}"
        assert not (widths[i] < widths[i - 1] and widths[i] < widths[i + 1]), \
            f"{name}: waist at row {order[i]}"

    # The body is the fully-rounded rect plus exactly one deliberate square
    # corner. Checking it that way tests the arcs *and* proves the only place
    # the shape departs from symmetry is the corner the tail is spent on.
    ref = rrect(**{**spec, 'square': ()})
    assert all((spec['x0'] + spec['x1'] - x, y) in ref for x, y in ref), \
        f"{name}: the rounded profile is not symmetric"
    extra = body - ref
    assert body >= ref, f"{name}: the square corner ate part of the arc"
    assert all(x < spec['x0'] + spec['r'] and y > spec['y1'] - spec['r'] for x, y in extra), \
        f"{name}: the body departs from the arc outside the bottom-left corner"

    # The tail: lower left, tapering, and sharing the body's left column.
    body_bottom = max(y for _, y in body)
    body_left = min(x for x, _ in body)
    assert tail_px, f"{name}: no tail"
    assert min(y for _, y in tail_px) == body_bottom + 1, f"{name}: tail is detached"
    assert min(x for x, _ in tail_px) == body_left, f"{name}: tail leaves the left edge"
    assert max(x for x, _ in tail_px) < 16, f"{name}: tail is not on the left"
    tail_rows = runs(tail_px, 0)
    tw = [tail_rows[y][2] - tail_rows[y][1] + 1 for y in sorted(tail_rows)]
    assert all(a > b for a, b in zip(tw, tw[1:])), f"{name}: tail does not taper: {tw}"
    assert all(1 <= a - b <= 3 for a, b in zip(tw, tw[1:])), f"{name}: tail rakes badly: {tw}"
    assert tw[-1] >= 2, f"{name}: tail ends in a single pixel"

    # The reason the corner was spent on the tail: a long unbroken bottom edge.
    bottom_width = row_runs[body_bottom][2] - row_runs[body_bottom][1] + 1
    assert bottom_width >= 22, f"{name}: bottom edge is only {bottom_width} long"
    assert row_runs[body_bottom][1] == body_left, f"{name}: bottom edge does not start at the tail"

    return shape, dict(bottom=bottom_width, tail_rows=len(tw), taper=tw)


# --------------------------------------------------------------------------
# tone
# --------------------------------------------------------------------------

def hexof(r, g, b):
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))


def ramp(hue0, hue1, light0, light1, sat0, sat1, n):
    """A ramp from a lit rim to a deep core, even in HLS so no step shouts."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        h = (hue0 + (hue1 - hue0) * t) / 360
        out.append(hexof(*colorsys.hls_to_rgb(
            h, light0 + (light1 - light0) * t, sat0 + (sat1 - sat0) * t)))
    return out


def luminance(colour):
    ch = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def rgb_step(a, b):
    av = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    bv = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return math.dist(av, bv)


def depths(shape):
    """Contour depth: 1 on the outermost ring, counting inward."""
    d = {}
    frontier = {p for p in shape
                if any((p[0] + dx, p[1] + dy) not in shape for dx, dy in NEIGHBOURS)}
    step = 1
    while frontier:
        nxt = set()
        for p in frontier:
            d[p] = step
            for dx, dy in NEIGHBOURS:
                q = (p[0] + dx, p[1] + dy)
                if q in shape and q not in d and q not in frontier:
                    nxt.add(q)
        frontier = nxt - set(d)
        step += 1
    return d


def shade(shape, tones, keys, offset, light):
    """Contour falloff from Hozz, direction from Mozz, and a calm middle.

    The falloff is c45's: rings peeled off the silhouette, one tone per ring,
    so every band bends around the corners and the tail and none of them can be
    a rectangle. Past the last ring everything lands on the final tone, which is
    the flat field the face sits on.

    The direction is Mozz's, but spent on *where the bands sit* rather than on
    extra tones. The effective depth of a pixel is pushed inward by up to
    `offset` rings on the side facing away from the light, so the meniscus is
    wide on the lit shoulder and the deep field rises almost to the keyline on
    the far one. That keeps the field 1-Lipschitz — the tone can only change by
    about one step between touching pixels — which the tone-jump lift it
    replaced could not do without collapsing the ramp.

    The keyline carries the direction too: with two key tones the lit part of
    the rim takes the lighter one, which is the rim light every round object in
    the family has and the flattest ones here were missing.
    """
    d = depths(shape)
    cx = sum(x for x, _ in shape) / len(shape)
    cy = sum(y for _, y in shape) / len(shape)
    lx, ly = light
    norm = math.hypot(lx, ly)
    lx, ly = lx / norm, ly / norm
    proj = {p: (cx - p[0]) * lx + (cy - p[1]) * ly for p in shape}
    span = max(abs(v) for v in proj.values())
    toward = {p: max(0.0, min(1.0, 0.5 + 0.5 * proj[p] / span)) for p in shape}

    n = len(tones)
    index = {}
    for p in shape:
        if d[p] == 1:
            continue  # the keyline
        away = 1 - toward[p]
        index[p] = max(0, min(n - 1, round((d[p] - 2) + offset * away)))

    # Rounding a smooth field can still land two touching pixels two tones
    # apart. Clamping each to one step darker than its lightest neighbour, to a
    # fixpoint, repairs that; because the field is already 1-Lipschitz this
    # moves a handful of pixels rather than cascading through the ramp.
    while True:
        settled = True
        for p, i in index.items():
            lightest = min((index[q] for q in
                            ((p[0] + dx, p[1] + dy) for dx, dy in NEIGHBOURS)
                            if q in index), default=i)
            if i > lightest + 1:
                index[p] = lightest + 1
                settled = False
        if settled:
            break

    keyline = {p for p in shape if d[p] == 1}
    if len(keys) == 1:
        key_layers = [keyline]
    else:
        lit = {p for p in keyline if toward[p] >= 0.62}
        key_layers = [keyline - lit, lit]

    layers = [{p for p, i in index.items() if i == k} for k in range(n)]
    return key_layers, layers, index, d


# --------------------------------------------------------------------------
# the four
# --------------------------------------------------------------------------

VARIANTS = [
    dict(
        slug="t59", name="Plain Carrier",
        idea=("The message shape everyone already reads, drawn properly: the "
              "bottom-left corner is spent on the tail instead of a second "
              "radius, so the bottom edge runs unbroken and the tail is the "
              "left edge continuing rather than a wedge stuck on."),
        body=dict(x0=2, y0=2, x1=29, y1=24, r=7, square=('ws',)),
        tail=dict(y=25, widths=(7, 4, 2)),
        face_cy=14,
        ramp=dict(hue0=268, hue1=261, light0=0.72, light1=0.47,
                  sat0=0.60, sat1=0.56, n=7),
        keys=("#1b1036", "#271656"), offset=1.5, light=(0.75, 0.66),
        note=("Radius 7 on the three corners that survive. The face sits high "
              "of centre by a row, because the tail already weights the mark "
              "downward and splitting the difference would read as sagging."),
    ),
    dict(
        slug="t60", name="Soft Carrier",
        idea=("The same carrier with the corners opened to 9 and the tail raked "
              "blunt rather than pointed — as friendly as this silhouette gets "
              "before it stops reading as a message at all."),
        body=dict(x0=2, y0=3, x1=29, y1=24, r=8, square=('ws',)),
        tail=dict(y=25, widths=(8, 5, 3)),
        face_cy=14,
        ramp=dict(hue0=278, hue1=270, light0=0.71, light1=0.47,
                  sat0=0.58, sat1=0.54, n=7),
        keys=("#1e1039",), offset=0.9, light=(0.30, 0.95),
        note=("Light from almost straight above, the shallowest band offset in "
              "the set and a single key tone: the roundest of the four wants "
              "the quietest direction, or the corner radius and the light "
              "source end up arguing about where the top of the shape is."),
    ),
    dict(
        slug="t61", name="Long Carrier",
        idea=("Crisper corners and a tail carried a row further down, so the "
              "mark points at whoever is speaking. The one in the set with any "
              "urgency in it."),
        body=dict(x0=2, y0=2, x1=29, y1=25, r=6, square=('ws',)),
        tail=dict(y=26, widths=(8, 6, 4, 2)),
        face_cy=14,
        ramp=dict(hue0=259, hue1=252, light0=0.72, light1=0.46,
                  sat0=0.62, sat1=0.58, n=7),
        keys=("#170f34", "#231550"), offset=2.0, light=(0.92, 0.40),
        note=("The strongest band offset in the set — two whole rings, so the "
              "deep field comes almost to the keyline on the right shoulder "
              "while the left one keeps a full meniscus. Radius 6 gives more "
              "contour per corner for that to bend around, which is the only "
              "reason it can carry that much without going flat."),
    ),
    dict(
        slug="t62", name="Wide Carrier",
        idea=("The tallest body and the shortest tail: a stub flick off the "
              "bottom-left that leaves the bottom edge doing all the work. "
              "The steadiest of the four, and the one that survives 16px best."),
        body=dict(x0=2, y0=2, x1=29, y1=25, r=8, square=('ws',)),
        tail=dict(y=26, widths=(8, 5, 2)),
        face_cy=14,
        ramp=dict(hue0=272, hue1=265, light0=0.74, light1=0.45,
                  sat0=0.60, sat1=0.55, n=8),
        keys=("#1c1037", "#281657"), offset=1.2, light=(0.60, 0.80),
        note=("The extra body height buys an eighth ring, so this one gets the "
              "longest and slowest meniscus of the four, and the direction is "
              "left as a hint rather than an argument."),
    ),
]

FACE = "#ffffff"

PREVIEW.mkdir(parents=True, exist_ok=True)
report = []

def wrap(text, width=74):
    """Reflow a paragraph into the file-header comment the repo writes by hand."""
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return "\n".join(f" * {l}".rstrip() for l in out)


for v in VARIANTS:
    slug = v["slug"]
    body = rrect(**v["body"])
    tail_px = tail(v["body"]["x0"], v["tail"]["y"], v["tail"]["widths"])
    shape, geom = check_geometry(slug, body, tail_px, v["body"])

    tones = ramp(**v["ramp"])
    steps = [rgb_step(a, b) for a, b in zip(tones, tones[1:])]
    assert max(steps) < 26, f"{slug}: tone step of {max(steps):.1f} is not gentle"

    keys = list(v["keys"])
    key_layers, layers, index, depth = shade(shape, tones, keys, v["offset"], v["light"])
    keyline = set().union(*key_layers)

    assert all(layers), f"{slug}: a tone came out empty"
    assert all(key_layers), f"{slug}: a key tone came out empty"
    # A rim light on the keyline is Mozz's; a *break* in the keyline is a
    # missing outline. Both key tones have to stay dark enough to hold the
    # silhouette against the light ground the gallery shows these on.
    assert all(contrast(k, "#faf8f5") >= 9 for k in keys), \
        f"{slug}: a key tone is too light to be a keyline"
    assert set().union(*layers) | keyline == shape, f"{slug}: the ramp has gaps"
    assert sum(map(len, layers)) + len(keyline) == len(shape), f"{slug}: the ramp overlaps"

    for (x, y), i in index.items():
        for q in ((x + 1, y), (x, y + 1)):
            if q in index:
                assert abs(i - index[q]) <= 1, f"{slug}: tone jump at {(x, y)}"

    # A *band* that comes out rectangular is pasted on; the field it encloses is
    # not, because it is what the rings leave behind. So the slab test runs on
    # every band, and the field answers to a stricter check instead: it has to
    # be a genuine erosion of the silhouette.
    for i, layer in enumerate(layers[:-1]):
        assert not is_slab(layer, shape), f"{slug}: tone {i} reads as a slab"

    core = layers[-1]
    assert all(depth[p] >= len(tones) - 1 for p in core), f"{slug}: the field reaches the rim"
    # It has to be a field, not a gap: comfortably larger than the 64-pixel
    # face it carries, so the ramp arrives at the letterforms rather than
    # crowding them. c45 sets the floor here — its rings start at the face's
    # own edge and that is as tight as this family goes.
    assert len(core) >= 100, f"{slug}: the field is only {len(core)} pixels"
    assert connected(core), f"{slug}: the field is in more than one piece"

    # The face: supplied, 8x8, wholly inside the body, wholly on the flat field.
    box = face_box(cx=16, cy=v["face_cy"], size="md", smile="compact", gap=2)
    assert (box["w"], box["h"]) == (8, 8), f"{slug}: the face is not 8x8"
    # Halving a 32 grid to 16 pairs rows 0/1, 2/3, ... An 8x8 face whose top
    # row is even collapses to a clean 4x4 - two eye columns, an empty gap
    # row, a mouth. Land it on an odd row and every glyph straddles the seam
    # and smears into porridge. This one bit of parity decides more about
    # legibility at 16px than any amount of shading does.
    assert box["y"] % 2 == 0, \
        f"{slug}: the face starts on odd row {box['y']} and will smear when halved"
    face_cells = {(box["x"] + dx, box["y"] + dy)
                  for dx in range(box["w"]) for dy in range(box["h"])}
    assert face_cells <= body, f"{slug}: the face runs off the body"
    under = {index[p] for p in face_cells}
    assert under == {len(tones) - 1}, f"{slug}: the face sits on {len(under)} tones"

    body_top = min(y for _, y in body)
    body_bottom = max(y for _, y in body)
    air = (box["y"] - body_top, body_bottom - (box["y"] + box["h"] - 1))
    assert min(air) >= 6, f"{slug}: only {air} rows of body air"
    assert abs(air[0] - air[1]) <= 1, f"{slug}: lopsided body air {air}"

    field_contrast = contrast(FACE, tones[-1])
    assert field_contrast >= 4.5, f"{slug}: the face fails on its own field"

    palette = [*keys, *tones, FACE]
    assert len(palette) == len(set(palette)), f"{slug}: a tone is repeated"
    assert 8 <= len(palette) <= 11, f"{slug}: {len(palette)} tones"

    drawn = [*zip(key_layers, keys), *zip(layers, tones)]
    paths = "\n".join(f'  <path d="{" ".join(to_paths(px))}" fill="{fill}" />'
                      for px, fill in drawn)

    direction = ("a single key tone and the shallowest offset in the set"
                 if len(keys) == 1 else
                 f"two key tones, the lit part of the rim taking the lighter")
    header = "\n *\n".join([
        f" * {slug} · {v['name']}",
        wrap(v["idea"]),
        wrap("The tail is the lower-left corner rather than an addition to it: "
             "the left edge runs straight past the bottom edge and rakes back "
             f"up to it over {geom['tail_rows']} rows, taper "
             f"{'-'.join(str(t) for t in geom['taper'])}. Because that corner "
             f"is never rounded the bottom edge stays {geom['bottom']} pixels "
             "unbroken, and that edge is what still reads as a message at 16px, "
             "where the tail itself is barely a pixel and a half."),
        wrap(v["note"]),
        wrap(f"{len(tones)} tones peel inward as contour rings, one step per "
             "ring, so every band bends around the corners and around the tail "
             "— Hozz's meniscus rather than a rectangle dropped inside an "
             "outline. The direction is Mozz's, but spent on where the bands "
             "sit instead of on extra tones: a pixel's effective depth is "
             f"pushed inward by up to {v['offset']} rings on the side facing "
             "away from the light, so the meniscus is wide on the lit shoulder "
             "and the deep field rises nearly to the keyline on the far one. "
             f"The keyline carries it too — {direction}."),
        wrap("Spending the direction that way is what keeps the middle calm. "
             "The field is one flat tone, "
             f"{len(core)} pixels of it, and no two touching pixels anywhere in "
             "the mark are more than one tone apart."),
        wrap("The face is supplied and untouched — facePathsAt at md with the "
             "compact smile and the family gap of 2, which is exactly 8×8 — "
             "centred on the body with the tail ignored: "
             f"{air[0]} rows of air above and {air[1]} below, measured. Nothing "
             "is cleared for it; white on the field is "
             f"{field_contrast:.1f}:1."),
        f" * {len(palette)} tones.",
    ])

    (OUT / f"{slug}.astro").write_text(f"""---
/**
{header}
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — {v['name']}">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {v['face_cy']}, size: 'md', smile: 'compact', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
""")

    (OUT / f"{slug}.meta.ts").write_text(f"""export default {{
  n: '{slug}', name: '{v["name"]}',
  idea: {json.dumps(v["idea"])},
  ground: 'light',
  palette: {json.dumps(palette)},
}};
""")

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
           'shape-rendering="crispEdges">'
           + "".join(f'<path d="{" ".join(to_paths(px))}" fill="{fill}"/>'
                     for px, fill in drawn)
           + f'<g fill="{FACE}">'
           + "".join(f'<path d="{d}"/>' for d in face_paths(
               cx=16, cy=v["face_cy"], size="md", smile="compact", gap=2))
           + '</g></svg>')
    (PREVIEW / f"{slug}.svg").write_text(svg)

    report.append(dict(slug=slug, tones=len(palette), bottom=geom["bottom"],
                       tail=geom["taper"], air=air, core=len(core),
                       face=round(field_contrast, 1), pixels=len(shape)))

for r in report:
    print(f"{r['slug']} · {r['tones']} tones · bottom edge {r['bottom']} "
          f"· tail {'-'.join(map(str, r['tail']))} · body air {r['air'][0]}/{r['air'][1]} "
          f"· field {r['core']}px · face {r['face']}:1 · {r['pixels']}px silhouette")
print("geometry: in the 28 safe area, connected, hole-free, one run per row and "
      "column, no single-neighbour pixels, no spurs or waists, arcs symmetric, "
      "tail integrated and tapering, bottom edge long and starting at the tail")
print("tone: no empty layer, full cover, no overlap, no neighbour skipping a "
      "tone, no band reads as a slab, gentle ramp steps, one connected flat "
      "field, face exactly 8x8 on that field with even body air above and below")
