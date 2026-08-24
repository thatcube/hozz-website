"""Generate t12, an emissive-screen sibling of c45's measured ramp."""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import keyline, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"
C45 = OUT / "c45.astro"

KEY = "#24102f"
RAMP = [
    "#47205f", "#52266f", "#5c2d7e", "#67338e",
    "#713a9d", "#7c40ad", "#8647bc", "#924ecd",
]
FACE = "#fff9fb"


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(value):
    channels = [channel / 255 for channel in rgb(value)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a, b):
    light, dark = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def rasterise_astro(path):
    """Paint the component's integer runs onto its native 32×32 grid."""
    grid = [[None for _ in range(32)] for _ in range(32)]
    source = path.read_text()
    for d, fill in re.findall(r'<path d="([^"]+)" fill="([^"]+)"\s*/>', source):
        for x, y, width in re.findall(r"M(\d+) (\d+)h(\d+)", d):
            x, y, width = int(x), int(y), int(width)
            for dx in range(width):
                grid[y][x + dx] = fill.lower()
    return grid


def measure_c45():
    grid = rasterise_astro(C45)
    axis = []
    for y in range(3, 14):
        tone = grid[y][16]
        if not axis or tone != axis[-1][1]:
            axis.append((y, tone))

    expected = [
        "#edf6fc", "#dcecf6", "#cae1f1",
        "#b9d7eb", "#a7cce6", "#96c2e0",
    ]
    tones = [tone for _, tone in axis]
    starts = [y for y, _ in axis]
    spacing = [b - a for a, b in zip(starts, starts[1:])]
    assert tones == expected, f"c45 ramp changed: {tones}"
    assert spacing == [1, 1, 1, 1, 1], f"c45 spacing changed: {spacing}"

    deltas = []
    for a, b in zip(tones, tones[1:]):
        ar, br = rgb(a), rgb(b)
        deltas.append(tuple(y - x for x, y in zip(ar, br)))
    distances = [
        math.sqrt(sum(channel * channel for channel in delta))
        for delta in deltas
    ]
    all_tones = {cell for row in grid for cell in row if cell}
    print(f"c45 raster: {len(all_tones)} total tones")
    print(f"c45 interior: {len(tones)} tones at centre-axis y{starts}")
    print(f"c45 spatial spacing: {spacing} grid pixels")
    print(f"c45 RGB deltas: {deltas}; mean distance {sum(distances) / len(distances):.2f}")
    return sum(distances) / len(distances)


def rows_from_widths(widths, top=2):
    shape = set()
    for y, width in enumerate(widths, start=top):
        left = 16 - width // 2
        shape |= {(left + x, y) for x in range(width)}
    return shape


c45_distance = measure_c45()

# A softened 28-wide speech-bubble body. The tail is deliberately separate:
# only the body participates in the symmetry and face-placement assertions.
BODY_WIDTHS = [18, 22, 24, 26] + [28] * 16 + [26, 24, 22, 18]
BODY = rows_from_widths(BODY_WIDTHS)
TAIL = (
    {(x, 25) for x in range(7, 13)}
    | {(x, 26) for x in range(7, 12)}
    | {(x, 27) for x in range(7, 11)}
    | {(x, 28) for x in range(7, 10)}
    | {(x, 29) for x in range(7, 10)}
)
SHAPE = BODY | TAIL

assert check(BODY) == BODY_WIDTHS
assert all((31 - x, y) in BODY for x, y in BODY), "body is not symmetric about x=16"

rows = {}
for x, y in SHAPE:
    rows.setdefault(y, []).append(x)
ys = sorted(rows)
widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
for i in range(1, len(widths) - 1):
    assert not (widths[i] > widths[i - 1] and widths[i] > widths[i + 1]), (
        f"spur at y{ys[i]}: {widths[i - 1]}/{widths[i]}/{widths[i + 1]}"
    )

xs = [x for x, _ in SHAPE]
shape_ys = [y for _, y in SHAPE]
assert min(xs) >= 2 and max(xs) <= 29 and min(shape_ys) >= 2 and max(shape_ys) <= 29

body_width = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
face_width = 10
assert (body_width - face_width) % 2 == 0, "face/body parity mismatch"

# lg + wide + gap 3 is 12 rows high and starts six rows below cy.
face_top, face_bottom = 8, 19
body_top, body_bottom = min(y for _, y in BODY), max(y for _, y in BODY)
air_above = face_top - body_top
air_below = body_bottom - face_bottom
assert air_above == air_below == 6, f"face air is {air_above}/{air_below}"

outline = keyline(SHAPE)
inner = SHAPE - outline

# The bubble is its own light source: a broad central violet glow falls through
# elliptical bands into dark corners and an almost unlit tail. These thresholds
# keep the centre readable at small sizes without tracing a second border.
RADIANCE_THRESHOLDS = [0.44, 0.54, 0.64, 0.74, 0.84, 0.94, 1.06]
ramp_layers = [set() for _ in RAMP]
pixel_tones = {}
for pixel in inner:
    x, y = pixel
    radius = math.hypot((x - 15.5) / 11.5, (y - 13.5) / 10.5)
    tone_index = next(
        (len(RAMP) - 1 - i for i, threshold in enumerate(RADIANCE_THRESHOLDS)
         if radius <= threshold),
        0,
    )
    ramp_layers[tone_index].add(pixel)
    pixel_tones[pixel] = RAMP[tone_index]

assert all(ramp_layers)
assert set().union(*ramp_layers) == inner
assert sum(len(layer) for layer in ramp_layers) == len(inner), "ramp layers overlap"
assert all(layer <= SHAPE for layer in ramp_layers)

# The face uses the shipped 10-wide ZZ eyes and wide smile at x11–20/y8–19.
face_rows = [
    [(0, 3), (6, 9)],
    [(2, 3), (8, 9)],
    [(1, 2), (7, 8)],
    [(0, 1), (6, 7)],
    [(0, 3), (6, 9)],
    [], [], [],
    [(0, 0), (9, 9)],
    [(0, 1), (8, 9)],
    [(1, 8)],
    [(2, 7)],
]
face_pixels = {
    (11 + x, 8 + y)
    for y, runs in enumerate(face_rows)
    for start, end in runs
    for x in range(start, end + 1)
}
assert face_pixels <= inner, "face leaves the bubble interior"
lightest_under_face = max(
    {pixel_tones[pixel] for pixel in face_pixels},
    key=relative_luminance,
)
face_contrast = contrast_ratio(FACE, lightest_under_face)
assert face_contrast >= 4.5, (
    f"face contrast {face_contrast:.2f}:1 on {lightest_under_face} is below 4.5:1"
)

ramp_distances = []
for a, b in zip(RAMP, RAMP[1:]):
    ar, br = rgb(a), rgb(b)
    ramp_distances.append(math.sqrt(sum((y - x) ** 2 for x, y in zip(ar, br))))
mean_ramp_distance = sum(ramp_distances) / len(ramp_distances)
assert abs(mean_ramp_distance - c45_distance) < 1, (
    f"ramp step {mean_ramp_distance:.2f} does not match c45 {c45_distance:.2f}"
)

layers = list(zip(ramp_layers, RAMP)) + [(outline, KEY)]
paths = "\n".join(
    f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'
    for pixels, fill in layers
)

(OUT / "t12.astro").write_text(f'''---
/**
 * t12 · Phosphor
 *
 * c45 rasterises to six interior tones whose starts are one grid pixel apart,
 * with a mean RGB step of {c45_distance:.2f}. This eight-tone violet ramp keeps
 * that subtle cadence at {mean_ramp_distance:.2f}, but spans a deeper range.
 * The bubble is a tiny live screen: its surface emits violet light behind the
 * face, then falls through elliptical bands into dark corners and tail.
 *
 * The softened body is 28 wide and symmetric about x=16; the tail is exempt.
 * The 10-wide lg face has matching parity. At gap 3 it spans y8–19 on the
 * y2–25 body, leaving {air_above} rows of air above and {air_below} below.
 *
 * Ten tones: a one-pixel plum keyline, eight violet emission tones, and a
 * warm-white face. The face clears {face_contrast:.2f}:1 on its lightest
 * underlying tone. The mark fits x2–29/y2–29 and has no row spurs.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Phosphor">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: 14, size: 'lg', smile: 'wide', gap: 3 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / "t12.meta.ts").write_text(f'''export default {{
  n: 't12', name: 'Phosphor',
  idea: 'A tiny live screen emits violet light from behind the face, fading through elliptical bands into dark corners and tail.',
  ground: 'light',
  palette: {RAMP + [KEY, FACE]!r},
}};
''')

print(
    f"t12: {len(RAMP) + 2} tones · body {body_width}×{body_bottom - body_top + 1} "
    f"· face air {air_above}/{air_below} · fit x{min(xs)}-{max(xs)} y{min(shape_ys)}-{max(shape_ys)}"
)
print(
    f"face contrast: {face_contrast:.2f}:1 on {lightest_under_face} · "
    "assertions: c45 measure, symmetry, parity, equal air, no spurs, fit, ramp coverage"
)
