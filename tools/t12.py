"""Generate t12, a top-lit sibling of c45's six-step Lens ramp."""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import edge, keyline, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"
C45 = OUT / "c45.astro"

KEY = "#321842"
RAMP = ["#ddc0f6", "#d0b1f0", "#c3a2ea", "#b693e4", "#a984de", "#9c75d8"]
FACE = "#fff9fb"


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


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

# c45's six tones begin one grid pixel apart. Here the same cadence follows only
# the top-facing contour: five one-pixel shells, then the deep field and tail.
cumulative = [edge(inner, 0, -1, depth) for depth in range(1, 6)]
ramp_layers = [cumulative[0]]
ramp_layers.extend(cumulative[i] - cumulative[i - 1] for i in range(1, 5))
ramp_layers.append(inner - cumulative[-1])

assert all(ramp_layers)
assert set().union(*ramp_layers) == inner
assert sum(len(layer) for layer in ramp_layers) == len(inner), "ramp layers overlap"
assert all(layer <= SHAPE for layer in ramp_layers)

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
 * t12 · Canopy
 *
 * c45 rasterises to six interior tones whose starts are one grid pixel apart,
 * with a mean RGB step of {c45_distance:.2f}. This uses the same six-tone,
 * one-pixel cadence and a mean step of {mean_ramp_distance:.2f}, but changes the
 * physical story: a speech bubble hangs from its body and is lit from above.
 * Light gathers on the crown, then falls through five top-facing shells into a
 * deeper field; the low tail stays in that field instead of glowing like a rim.
 *
 * The softened body is 28 wide and symmetric about x=16; the tail is exempt.
 * The 10-wide lg face has matching parity. At gap 3 it spans y8–19 on the
 * y2–25 body, leaving {air_above} rows of air above and {air_below} below.
 *
 * Eight tones: dark violet keyline, six close amethyst surface tones, and a
 * warm-white face. The silhouette fits x2–29 and y2–29 and has no row spurs.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Canopy">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: 14, size: 'lg', smile: 'wide', gap: 3 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / "t12.meta.ts").write_text(f'''export default {{
  n: 't12', name: 'Canopy',
  idea: 'Six close violet steps follow the top-facing contour, so the crown catches light while the hanging tail keeps its weight.',
  ground: 'light',
  palette: {RAMP + [KEY, FACE]!r},
}};
''')

print(
    f"t12: 8 tones · body {body_width}×{body_bottom - body_top + 1} "
    f"· face air {air_above}/{air_below} · fit x{min(xs)}-{max(xs)} y{min(shape_ys)}-{max(shape_ys)}"
)
print("assertions: c45 measure, body symmetry, face parity, equal air, no spurs, fit, ramp coverage")
