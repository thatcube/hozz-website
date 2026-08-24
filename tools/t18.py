"""Generate t18: a speech bubble whose face is held in one recessed field."""

import colorsys
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import is_slab, keyline, rings, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"

KEY = "#54258f"
RIM_SHADOW = "#7545b9"
RIM_BASE = "#9a70ce"
RIM_LIGHT = "#d2c0ed"
WALL_SHADOW = "#6730a9"
WALL_MID = "#7b42b9"
WALL_LIGHT = "#c3a8e7"
CORE = "#8250c5"
FACE = "#fffaf3"
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
LIGHT_TO_DARK = [
    RIM_LIGHT,
    WALL_LIGHT,
    RIM_BASE,
    CORE,
    WALL_MID,
    RIM_SHADOW,
    WALL_SHADOW,
    KEY,
]


def rows(profile, top):
    shape = set()
    for y, width in enumerate(profile, top):
        left = 16 - width // 2
        shape |= {(x, y) for x in range(left, left + width)}
    return shape


# The body keeps the shipped mark's broad bubble proportions but rounds both
# shoulders enough that the recessed field inherits curves instead of becoming
# a screen-like rectangle. Every width is even, so it remains centred on x=16.
BODY = rows(
    [14, 18, 22, 24, 26, 26, *([28] * 11), 26, 26, 24, 22, 18],
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

# Light enters from above-left. Distance from that one source drives the whole
# ramp, while the inward wall takes two fewer stops of light and the recessed
# field one fewer. On the shadow side all three converge, so the plane change
# disappears instead of wrapping the bubble in an equally bright collar.
SOURCE = (-5.0, -6.0)
RADII = (18.0, 19.5, 21.5, 25.0, 29.0, 33.0, 36.0)

(body_rings, CORE_FIELD) = rings(BODY, 4)
BODY_EDGE, RIM, WALL_OUTER, WALL_INNER = body_rings
WALL = WALL_OUTER | WALL_INNER


def distance_from_light(pixel):
    x, y = pixel
    return math.hypot(x + 0.5 - SOURCE[0], y + 0.5 - SOURCE[1])


def tone_index(pixel):
    step = sum(distance_from_light(pixel) >= radius for radius in RADII)
    if pixel in OUTLINE:
        # Keep the contour visible on white, but let it fall from lavender into
        # the dark anchor instead of drawing one key colour around the bubble.
        return max(2, step)
    if pixel in WALL:
        step += 2
    elif pixel in CORE_FIELD:
        step += 1
    return min(step, len(LIGHT_TO_DARK) - 1)


tone_map = {pixel: tone_index(pixel) for pixel in SILHOUETTE}
tone_pixels = [
    {pixel for pixel, tone in tone_map.items() if tone == index}
    for index in range(len(LIGHT_TO_DARK))
]
LAYERS = list(zip(tone_pixels, LIGHT_TO_DARK))


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

face_width = 10
body_width = max(body_widths)
assert (body_width - face_width) % 2 == 0
face_left, face_top, face_right, face_bottom = 11, 8, 20, 17
body_left, body_right = min(x for x, _ in BODY), max(x for x, _ in BODY)
body_top, body_bottom = min(y for _, y in BODY), max(y for _, y in BODY)
assert (body_left, body_right, body_top, body_bottom) == (2, 29, 2, 23)
air_above = face_top - body_top
air_below = body_bottom - face_bottom
air_left = face_left - body_left
air_right = body_right - face_right
assert air_above == air_below == 6
assert air_left == air_right == 9
assert {
    (x, y)
    for x in range(face_left, face_right + 1)
    for y in range(face_top, face_bottom + 1)
} <= CORE_FIELD

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


def rgb(colour):
    return tuple(int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5))


def relative_luminance(colour):
    linear = [
        value / 12.92
        if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in rgb(colour)
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    high, low = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


purple_colours = PALETTE[:-1]
for colour in purple_colours:
    hue, _, saturation = colorsys.rgb_to_hls(*rgb(colour))
    assert 0.69 <= hue <= 0.78
    assert saturation >= 0.45
face_contrast = contrast(FACE, CORE)
assert face_contrast >= 4.5

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
 * The body is symmetric about x=16; only the speech tail is exempt. The shipped
 * 10-wide face and 28-wide body have matching even parity. Its measured y8–17
 * box sits in the y2–23 body with six rows of air above and six below.
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
    {{facePathsAt({{ cx: 16, cy: 13, size: 'lg', smile: 'wide', gap: 1 }}).map((d) => (
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
    f"face=x{face_left}–{face_right} y{face_top}–{face_bottom} · "
    f"air=v{air_above}/{air_below} h{air_left}/{air_right} · "
    f"face/core contrast={face_contrast:.2f}:1 · "
    "bounds=x2–29 y2–29 · "
    f"body rows={body_widths} · silhouette rows={silhouette_widths}"
)
