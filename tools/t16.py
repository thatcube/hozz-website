"""Generate t16: a round bubble with an unmistakable lower-left tail."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import MOZZ_28, check  # noqa: E402
from shade import bbox, is_slab, rings, to_paths  # noqa: E402

SLUG = "t16"
OUT = ROOT / "src/components/mark/logos"

KEY = "#12051f"
SURFACE = [
    "#d4c1f0",
    "#bea0e7",
    "#9d73d5",
    "#7548c2",
    "#6335ad",
    "#512795",
]
FACE = "#fffdf8"

# Keep the shipped Mozz circle's shoulders and 28-pixel diameter, removing three
# duplicate equator rows and handing its final two cap rows to the tail. The
# lower-left curve therefore changes direction once, rather than growing a lobe.
BODY_PROFILE = [*MOZZ_28[:10], *([28] * 5), *MOZZ_28[18:-2]]
assert len(BODY_PROFILE) == 23
BODY = {
    (16 - width // 2 + offset, 2 + row)
    for row, width in enumerate(BODY_PROFILE)
    for offset in range(width)
}
TAIL_ROWS = {
    25: (8, 16),
    26: (8, 14),
    27: (8, 12),
    28: (8, 10),
    29: (9, 9),
}
TAIL = {
    (x, y)
    for y, (x0, x1) in TAIL_ROWS.items()
    for x in range(x0, x1 + 1)
}
SHAPE = BODY | TAIL


def assert_connected(shape):
    pending = set(shape)
    seen = {pending.pop()}
    frontier = list(seen)
    while frontier:
        x, y = frontier.pop()
        for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if p in pending:
                pending.remove(p)
                seen.add(p)
                frontier.append(p)
    assert not pending, "silhouette is disconnected"


def assert_no_spurs(shape):
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    assert ys == list(range(ys[0], ys[-1] + 1)), "silhouette skips a row"
    widths = []
    for y in ys:
        xs = sorted(rows[y])
        assert xs == list(range(xs[0], xs[-1] + 1)), f"gap in row {y}"
        widths.append(xs[-1] - xs[0] + 1)
    for i in range(1, len(widths) - 1):
        assert not (
            widths[i] > widths[i - 1] and widths[i] > widths[i + 1]
        ), f"spur at row {ys[i]}: {widths[i - 1]}/{widths[i]}/{widths[i + 1]}"
    return widths


# Body-only symmetry is intentional: a speech-bubble tail must break it.
body_widths = check(BODY)
assert all((31 - x, y) in BODY for x, y in BODY)
assert any((31 - x, y) not in SHAPE for x, y in SHAPE - BODY)
assert_connected(SHAPE)
silhouette_widths = assert_no_spurs(SHAPE)

x0, y0, x1, y1 = bbox(SHAPE)
assert 2 <= x0 <= x1 <= 29 and 2 <= y0 <= y1 <= 29

BODY_W = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
FACE_W = 10
assert BODY_W == 28 and (BODY_W - FACE_W) % 2 == 0
body_x0 = min(x for x, _ in BODY)
body_x1 = max(x for x, _ in BODY)
face_x0 = 16 - FACE_W // 2
face_x1 = face_x0 + FACE_W - 1
assert face_x0 - body_x0 == body_x1 - face_x1 == 9

# The shipped lg face keeps its full width and default two-row breathing gap.
# Its optical body begins at y4, below the two-row circular cap; cy 14 puts its
# rendered box at y9-19, leaving five visible rows above and below.
FACE_CY = 14
FACE_GAP = 2
FACE_TOP = 9
FACE_HEIGHT = 11
body_y1 = min(y for _, y in TAIL) - 1
body_proper = {(x, y) for x, y in BODY if y <= body_y1}
assert all((31 - x, y) in body_proper for x, y in body_proper)
body_y0 = 4
assert min(y for _, y in BODY) == body_y0 - 2
air_above = FACE_TOP - body_y0
air_below = body_y1 - (FACE_TOP + FACE_HEIGHT - 1)
assert air_above == air_below == 5

assert min(y for _, y in TAIL) == body_y1 + 1
body_last = sorted(x for x, y in SHAPE if y == body_y1)
tail_first = sorted(x for x, y in SHAPE if y == body_y1 + 1)
body_last_c = (body_last[0] + body_last[-1] + 1) / 2
tail_first_c = (tail_first[0] + tail_first[-1] + 1) / 2
assert body_last_c == 16 and tail_first_c == 12.5

# A single keyline encloses the combined mark, so no line can close across the
# body-to-tail join. Upper-left light crosses two shallow contours, fades around
# the right turn, and disappears on the lower right instead of forming a bezel.
outer_rings, _ = rings(SHAPE, 1)
outline = outer_rings[0]
open_join = [
    x
    for x in range(32)
    if (x, body_y1) in SHAPE - outline
    and (x, body_y1 + 1) in TAIL - outline
]
assert len(open_join) >= 5
body_rings, body_core = rings(BODY, 3)
tail_rings, tail_core = rings(TAIL, 1)
assert len(body_rings) == 3 and body_core
assert len(tail_rings) == 1 and tail_core

body_owned = BODY - TAIL
body_join = (body_rings[0] & body_owned) - outline
inner_rim = (body_rings[1] & body_owned) - outline
mid_contour = (body_rings[2] & body_owned) - outline


def light_score(point):
    x, y = point
    return 30 - x - 1.2 * y


rim_highlight = {point for point in inner_rim if light_score(point) >= 8}
rim_light = (
    {point for point in inner_rim if 2 <= light_score(point) < 8}
    | {point for point in mid_contour if light_score(point) >= 8}
)
rim_fade = (
    {point for point in inner_rim if -4 <= light_score(point) < 2}
    | {point for point in mid_contour if 2 <= light_score(point) < 8}
    | body_join
    | (tail_rings[0] - outline)
)
body_field = (
    (body_owned - outline)
    - rim_highlight
    - rim_light
    - rim_fade
)
lower_right_turn = {
    point
    for point in inner_rim | mid_contour
    if point[0] >= 16 and point[1] >= 16
}
assert lower_right_turn <= body_field
assert sum(x for x, _ in rim_highlight) / len(rim_highlight) < 16
assert sum(y for _, y in rim_highlight) / len(rim_highlight) < 13
tail_shadow = {(x, y) for x, y in tail_core if y >= 27}
tail_depth = tail_core - tail_shadow
layers = [
    (outline, KEY),
    (rim_highlight, SURFACE[0]),
    (rim_light, SURFACE[1]),
    (rim_fade, SURFACE[2]),
    (body_field, SURFACE[3]),
    (tail_depth, SURFACE[4]),
    (tail_shadow, SURFACE[5]),
]
assert all(layer for layer, _ in layers)
assert all(not is_slab(layer, SHAPE) for layer, _ in layers)
claimed = set()
for layer, _ in layers:
    assert not claimed & layer
    claimed |= layer
assert claimed == SHAPE
assert len({fill for _, fill in layers} | {FACE}) == 8


def luminance(colour):
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# Testing the whole face box is stricter than testing only its painted pixels.
face_box = {
    (x, y)
    for y in range(FACE_TOP, FACE_TOP + FACE_HEIGHT)
    for x in range(face_x0, face_x1 + 1)
}
face_backdrops = {fill for layer, fill in layers if layer & face_box}
face_contrast = min(contrast(FACE, fill) for fill in face_backdrops)
assert face_contrast >= 4.5

paths = "\n".join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / f"{SLUG}.astro").write_text(
    f"""---
/**
 * t16 · Round Reply
 *
 * The body is 28 pixels wide, built from the shipped Mozz circle profile with
 * three duplicate equator rows removed. Its final two cap rows give way to the
 * tail, preserving the circle's shoulders while matching the siblings' width.
 *
 * Upper-left light enters across two shallow contours, fades as it turns down
 * the right edge, and disappears on the lower right. The face lives on a broad
 * violet field instead of inside a stack of collars.
 *
 * A straight-left, right-tapered 9-7-5-3-1 wedge continues the body's lower-left
 * edge. One outer keyline encloses both, leaving no seam at the join.
 *
 * The lg face matches the body's even parity and occupies y9-19 on the optical
 * body at y4-24: 5 pixels of air above and 5 below, plus 9 on either side. The
 * white face clears 4.5:1 against its full background box. Eight tones including
 * face.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Round Reply">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {FACE_CY}, size: 'lg', smile: 'wide', gap: {FACE_GAP} }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
"""
)

palette = ", ".join(f"'{tone}'" for tone in [KEY, *SURFACE, FACE])
(OUT / f"{SLUG}.meta.ts").write_text(
    f"""export default {{
  n: '16',
  name: 'Round Reply',
  idea: 'A full-width round body opens into a straight-edged stepped tail; a thin outer ramp leaves a calm violet field around the face.',
  ground: 'light',
  palette: [{palette}],
}};
"""
)

print(
    f"{SLUG}: round body {BODY_W}x23, centred body y{body_y0}-{body_y1}, "
    f"air {air_above}/{air_below}, tones 8, bounds x{x0}-{x1} y{y0}-{y1}, "
    f"side air 9/9, open join {len(open_join)}px, "
    f"face contrast {face_contrast:.2f}:1"
)
print(f"body widths: {body_widths}")
print(f"silhouette widths: {silhouette_widths}")
print("row extents:")
for y in range(y0, y1 + 1):
    xs = sorted(x for x, py in SHAPE if py == y)
    centre = (xs[0] + xs[-1] + 1) / 2
    print(f"  y{y}: x{xs[0]}-{xs[-1]} w{len(xs)} c{centre:g}")
