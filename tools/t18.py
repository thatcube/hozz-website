"""Generate t18: a speech bubble whose face is held in one recessed field."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import edge, keyline, rings, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"

KEY = "#241438"
RIM_SHADOW = "#69488b"
RIM_BASE = "#79599a"
RIM_LIGHT = "#9173ae"
WALL_SHADOW = "#4b3068"
WALL_MID = "#5a3b76"
WALL_LIGHT = "#806196"
CORE = "#61447d"
FACE = "#fff8e8"
PALETTE = [
    KEY,
    WALL_SHADOW,
    WALL_MID,
    CORE,
    RIM_SHADOW,
    RIM_BASE,
    WALL_LIGHT,
    RIM_LIGHT,
    FACE,
]


def rows(profile, top):
    shape = set()
    for y, width in enumerate(profile, top):
        left = 16 - width // 2
        shape |= {(x, y) for x in range(left, left + width)}
    return shape


# The body keeps the shipped mark's broad, unmistakable bubble proportions.
# Every width is even, so it is symmetric about x=16 and accepts an even face.
BODY = rows(
    [18, 22, 24, 26, 26, *([28] * 14), 26, 26, 24, 22],
    top=2,
)

# The tail is deliberately exempt from symmetry. Its vertical left edge and
# descending right edge retain the shipped mark's speech-bubble read.
TAIL = {
    (x, y)
    for y, (left, width) in {
        23: (7, 7),
        24: (7, 7),
        25: (7, 6),
        26: (7, 5),
        27: (7, 4),
        28: (7, 3),
        29: (7, 3),
    }.items()
    for x in range(left, left + width)
}
SILHOUETTE = BODY | TAIL
OUTLINE = keyline(SILHOUETTE)

# One plane change: a narrow outer rim, a two-pixel inward wall, then the field.
# Every part of the well is peeled from the body contour, never pasted inside it.
(body_rings, CORE_FIELD) = rings(BODY, 4)
BODY_EDGE, RIM, WALL_OUTER, WALL_INNER = body_rings
available_rim = (BODY_EDGE | RIM) - OUTLINE
wall = (WALL_OUTER | WALL_INNER) - OUTLINE

rim_top = available_rim & edge(BODY, 0, -1, 3)
rim_bottom = (available_rim & edge(BODY, 0, 1, 3)) - rim_top
rim_middle = available_rim - rim_top - rim_bottom

inner_body = BODY - BODY_EDGE - RIM
wall_top = wall & edge(inner_body, 0, -1, 2)
wall_bottom = (wall & edge(inner_body, 0, 1, 2)) - wall_top
wall_middle = wall - wall_top - wall_bottom

tail_only = (TAIL - BODY) - OUTLINE
tail_shadow = tail_only & edge(TAIL, 0, 1, 2)
tail_middle = tail_only - tail_shadow

LAYERS = [
    (tail_shadow | rim_bottom, RIM_SHADOW),
    (tail_middle | rim_middle, RIM_BASE),
    (rim_top, RIM_LIGHT),
    (wall_top, WALL_SHADOW),
    (wall_middle, WALL_MID),
    (wall_bottom, WALL_LIGHT),
    (CORE_FIELD, CORE),
    (OUTLINE, KEY),
]


def row_widths(shape):
    by_row = {}
    for x, y in shape:
        by_row.setdefault(y, []).append(x)
    ys = sorted(by_row)
    widths = [max(by_row[y]) - min(by_row[y]) + 1 for y in ys]
    for i in range(1, len(widths) - 1):
        assert not (
            widths[i] > widths[i - 1] and widths[i] > widths[i + 1]
        ), f"spur at y{ys[i]}: {widths[i - 1]}/{widths[i]}/{widths[i + 1]}"
    return widths


# Geometry assertions.
body_widths = check(BODY)
silhouette_widths = row_widths(SILHOUETTE)
assert min(x for x, _ in SILHOUETTE) >= 2
assert max(x for x, _ in SILHOUETTE) <= 29
assert min(y for _, y in SILHOUETTE) >= 2
assert max(y for _, y in SILHOUETTE) <= 29
assert all((31 - x, y) in BODY for x, y in BODY)

face_width = 8
body_width = max(body_widths)
assert (body_width - face_width) % 2 == 0
face_top, face_bottom = 9, 17
body_top, body_bottom = 2, 24
air_above = face_top - body_top
air_below = body_bottom - face_bottom
assert air_above == air_below == 7

# Paint assertions: disjoint layers cover the silhouette, the recessed plane is
# symmetric, and all nine intended tones are present.
paint_sets = [pixels for pixels, _ in LAYERS]
for i, layer in enumerate(paint_sets):
    assert layer
    assert not any(layer & other for other in paint_sets[i + 1 :])
assert set().union(*paint_sets) == SILHOUETTE
for layer in (wall_top, wall_middle, wall_bottom, CORE_FIELD):
    assert all((31 - x, y) in layer for x, y in layer)
assert len(set(PALETTE)) == 9

paths = "\n".join(
    f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'
    for pixels, fill in LAYERS
)

(OUT / "t18.astro").write_text(
    f"""---
/**
 * t18 · Held
 *
 * A single recessed field, not a screen inside a bubble. The outer two pixels
 * remain the bubble's rim; the next two are one continuous inward wall, dark at
 * the top and light at the bottom; the face rests on the quieter field below.
 * Because every layer is peeled from the body contour, there is no second
 * outlined panel and therefore no second object.
 *
 * The body is symmetric about x=16; only the speech tail is exempt. The md
 * face and 28-wide body have matching even parity. Its y9–17 box sits in the
 * y2–24 body with seven rows of air above and seven below.
 *
 * Nine tones. Bounds x2–29, y2–29. Body and silhouette pass the no-spur check.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Held">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: 13, size: 'md', smile: 'wide', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
"""
)

(OUT / "t18.meta.ts").write_text(
    f"""export default {{
  n: 't18', name: 'Held',
  idea: 'One contour-following step down: a shaded inward wall holds the face in a quiet plum field.',
  ground: 'light',
  palette: [{", ".join(repr(colour) for colour in PALETTE)}],
}};
"""
)

print(
    "t18 Held · depth=recession · "
    f"tones={len(PALETTE)} · body={body_width}×{body_bottom - body_top + 1} · "
    f"air={air_above}/{air_below} · bounds=x2–29 y2–29 · "
    f"body rows={body_widths} · silhouette rows={silhouette_widths}"
)
