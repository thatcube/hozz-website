"""Generate t18: a speech bubble whose face is held in one recessed field."""

import colorsys
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import is_slab, keyline, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"

KEYLINE = "#211532"
FACE = "#fffaf3"
RAMP = [
    "#d2c0ed",
    "#b89ae3",
    "#a27bda",
    "#8b58d1",
    "#7e45cd",
    "#7134c1",
    "#622ca7",
    "#54258f",
]
PALETTE = [KEYLINE, *RAMP, FACE]


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

# The keyline is structural and deliberately separate from the recovered
# lavender range. Inside it, one upper-left light travels on a 45-degree axis:
# x+y can only increase when walking right or down, so the ramp can never become
# lighter again on the way toward the lower-right shadow. The first three bands
# are tighter near the light; the five darker bands open into the field.
INNER = SILHOUETTE - OUTLINE
THRESHOLDS = (13, 16, 19, 25, 31, 37, 43)


def light_axis(pixel):
    return pixel[0] + pixel[1]


def tone_index(pixel):
    return sum(light_axis(pixel) >= threshold for threshold in THRESHOLDS)


tone_map = {pixel: tone_index(pixel) for pixel in INNER}
tone_pixels = [
    {pixel for pixel, tone in tone_map.items() if tone == index}
    for index in range(len(RAMP))
]
LAYERS = [(OUTLINE, KEYLINE), *zip(tone_pixels, RAMP)]


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
} <= INNER

# Paint assertions: one full-strength keyline contains the silhouette, while
# every interior shade comes from the same monotonic directional falloff.
paint_sets = [pixels for pixels, _ in LAYERS]
for i, layer in enumerate(paint_sets):
    assert layer
    xs = [x for x, _ in layer]
    ys = [y for _, y in layer]
    bounding_area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    assert len(layer) != bounding_area
    assert not any(layer & other for other in paint_sets[i + 1 :])
    assert not is_slab(layer, SILHOUETTE)
assert set().union(*paint_sets) == SILHOUETTE
assert paint_sets[0] == keyline(SILHOUETTE)
assert len(set(PALETTE)) == 10
for pixel, tone in tone_map.items():
    x, y = pixel
    for darker_neighbour in ((x + 1, y), (x, y + 1)):
        if darker_neighbour in INNER:
            assert tone_map[darker_neighbour] >= tone


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


purple_colours = RAMP
for colour in purple_colours:
    hue, _, saturation = colorsys.rgb_to_hls(*rgb(colour))
    assert 0.69 <= hue <= 0.78
    assert saturation >= 0.45
assert relative_luminance(KEYLINE) < 0.02
ramp_luminances = [relative_luminance(colour) for colour in RAMP]
assert all(
    0.60 <= darker / lighter <= 0.80
    for lighter, darker in zip(ramp_luminances, ramp_luminances[1:])
)
face_box = {
    (x, y)
    for x in range(face_left, face_right + 1)
    for y in range(face_top, face_bottom + 1)
}
face_tones = sorted({tone_map[pixel] for pixel in face_box})
face_contrast = min(
    contrast(FACE, RAMP[tone]) for tone in face_tones
)
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
 * A single recessed field, not a screen inside a bubble. A near-black violet
 * keyline contains the full contour, including the tail. Inside it, one
 * upper-left light falls monotonically across the held plane to lower right:
 * every step right or down stays at the same tone or becomes darker.
 *
 * The body is symmetric about x=16; only the speech tail is exempt. The shipped
 * 10-wide face and 28-wide body have matching even parity. Its measured y8–17
 * box sits in the y2–23 body with six rows of air above and six below.
 *
 * Ten tones. Bounds x2–29, y2–29. Body and silhouette pass the no-spur check.
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
  idea: 'A keyed recessed field falls monotonically from upper-left lavender to lower-right violet.',
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
    f"face tones={face_tones} contrast={face_contrast:.2f}:1 · "
    f"ramp={ramp_luminances[0]:.3f}→{ramp_luminances[-1]:.3f} · "
    "bounds=x2–29 y2–29 · "
    f"body rows={body_widths} · silhouette rows={silhouette_widths}"
)
