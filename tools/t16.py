"""Generate t16: a round bubble with an unmistakable lower-left tail."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check, circle  # noqa: E402
from shade import bbox, is_slab, rings, to_paths  # noqa: E402

SLUG = "t16"
OUT = ROOT / "src/components/mark/logos"

KEY = "#281245"
SURFACE = [
    "#e0d1fb",
    "#d1bdf5",
    "#c2a8ed",
    "#b294e4",
    "#a17eda",
    "#9068ce",
]
FACE = "#fffdf8"

# The body is a complete canonical circle. The tail begins only after it ends,
# changing direction sharply instead of extending the circle into a teardrop.
BODY = circle(22, top=2)
TAIL_ROWS = {
    24: (8, 17),
    25: (7, 16),
    26: (7, 14),
    27: (7, 12),
    28: (8, 11),
    29: (9, 10),
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
assert BODY_W == 22 and (BODY_W - FACE_W) % 2 == 0
body_x0 = min(x for x, _ in BODY)
body_x1 = max(x for x, _ in BODY)
face_x0 = 16 - FACE_W // 2
face_x1 = face_x0 + FACE_W - 1
assert face_x0 - body_x0 == body_x1 - face_x1 == 6

# lg + wide + gap 1 is ten rows. At cy 13 it occupies y8-17, leaving
# six body rows above and six below the face.
FACE_CY = 13
FACE_GAP = 1
FACE_TOP = 8
FACE_HEIGHT = 10
body_y0 = min(y for _, y in BODY)
body_y1 = max(y for _, y in BODY)
air_above = FACE_TOP - body_y0
air_below = body_y1 - (FACE_TOP + FACE_HEIGHT - 1)
assert air_above == air_below == 6

assert min(y for _, y in TAIL) == body_y1 + 1
body_last = sorted(x for x, y in BODY if y == body_y1)
tail_first = sorted(x for x, y in TAIL if y == body_y1 + 1)
body_last_c = (body_last[0] + body_last[-1] + 1) / 2
tail_first_c = (tail_first[0] + tail_first[-1] + 1) / 2
assert body_last_c == 16 and tail_first_c == 13

# A single keyline encloses the combined mark. Inside it, the circular body
# gets a true inset bevel: a light meniscus and five small steps to a deep,
# plain core. The tail has its own two nested steps, reusing the body ramp.
outer_rings, _ = rings(SHAPE, 1)
outline = outer_rings[0]
body_rings, body_core = rings(BODY, 6)
tail_rings, tail_core = rings(TAIL, 2)
assert len(body_rings) == 6 and body_core
assert len(tail_rings) == 2 and tail_core

layers = [
    (outline, KEY),
    ((body_rings[0] | body_rings[1]) - outline, SURFACE[0]),
    (body_rings[2] - outline, SURFACE[1]),
    (body_rings[3] - outline, SURFACE[2]),
    (body_rings[4] - outline, SURFACE[3]),
    (body_rings[5] - outline, SURFACE[4]),
    (body_core - outline, SURFACE[5]),
    (tail_rings[0] - outline, SURFACE[0]),
    (tail_rings[1] - outline, SURFACE[2]),
    (tail_core - outline, SURFACE[4]),
]
assert all(layer for layer, _ in layers)
assert all(not is_slab(layer, SHAPE) for layer, _ in layers)
claimed = set()
for layer, _ in layers:
    assert not claimed & layer
    claimed |= layer
assert claimed == SHAPE
assert len({fill for _, fill in layers} | {FACE}) == 8

paths = "\n".join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / f"{SLUG}.astro").write_text(
    f"""---
/**
 * t16 · Round Reply
 *
 * A complete canonical 22-pixel circle ends before a stepped lower-left wedge
 * begins. Its centre jumps three pixels at the join, preserving "speech" rather
 * than extending the body into a teardrop.
 *
 * Six body rings form a light meniscus, a stepped inward ramp and a deep core;
 * the tail reuses that ramp in two nested steps rather than receiving a wash.
 *
 * The lg face matches the body's even parity and occupies y8-17 on the body
 * at y2-23: 6 pixels of air above and 6 below. Eight tones including face.
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
  idea: 'A true circular body ends before a stepped lower-left tail, while a light rim falls inward through six structured violet tones.',
  ground: 'light',
  palette: [{palette}],
}};
"""
)

print(
    f"{SLUG}: body {BODY_W}x{body_y1 - body_y0 + 1}, "
    f"air {air_above}/{air_below}, tones 8, bounds x{x0}-{x1} y{y0}-{y1}"
)
print(f"body widths: {body_widths}")
print(f"silhouette widths: {silhouette_widths}")
print("row extents:")
for y in range(y0, y1 + 1):
    xs = sorted(x for x, py in SHAPE if py == y)
    centre = (xs[0] + xs[-1] + 1) / 2
    print(f"  y{y}: x{xs[0]}-{xs[-1]} w{len(xs)} c{centre:g}")
