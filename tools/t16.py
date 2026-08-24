"""Generate t16: a circular bubble whose lower-left arc flows into its tail."""

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
    "#d7c2ff",
    "#c7abfa",
    "#b993f3",
    "#aa7deb",
    "#9a68e2",
    "#8955d5",
    "#7945c4",
]
FACE = "#fffdf8"

# A canonical circle remains the measurable body. The tail begins inside its
# lower-left arc, then takes over as that arc falls away, avoiding a separate
# triangle attached below the body.
BODY = circle(24, top=2)
TAIL_ROWS = {
    21: (7, 14),
    22: (7, 18),
    23: (7, 19),
    24: (8, 18),
    25: (8, 18),
    26: (8, 16),
    27: (8, 14),
    28: (8, 12),
    29: (8, 10),
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
assert BODY_W == 24 and (BODY_W - FACE_W) % 2 == 0

# lg + wide + gap 1 is ten rows. At cy 14 it occupies y9-18, leaving
# seven body rows above and seven below the face.
FACE_CY = 14
FACE_GAP = 1
FACE_TOP = 9
FACE_HEIGHT = 10
body_y0 = min(y for _, y in BODY)
body_y1 = max(y for _, y in BODY)
air_above = FACE_TOP - body_y0
air_below = body_y1 - (FACE_TOP + FACE_HEIGHT - 1)
assert air_above == air_below == 7

peeled, core = rings(SHAPE, 7)
assert len(peeled) == 7 and core
assert all(peeled) and all(not is_slab(layer, SHAPE) for layer in [*peeled, core])
assert set().union(*peeled, core) == SHAPE
assert sum(map(len, [*peeled, core])) == len(SHAPE)

# Ring 0 is the keyline. Rings 1-6 and the core make a seven-tone,
# contour-following interior whose bands continue through the tail.
layers = [(core, SURFACE[-1])]
layers.extend((peeled[i], SURFACE[i - 1]) for i in range(6, 0, -1))
layers.append((peeled[0], KEY))
assert len({fill for _, fill in layers} | {FACE}) == 9

paths = "\n".join(
    f'  <path d="{" ".join(to_paths(layer))}" fill="{fill}" />'
    for layer, fill in layers
)

(OUT / f"{SLUG}.astro").write_text(
    f"""---
/**
 * t16 · Flow
 *
 * A canonical 24-pixel circle supplies the body, while the lower-left arc
 * widens into the tail before the circle ends. There is no seam or separate
 * triangle: all seven interior steps are peeled from the combined silhouette,
 * so light and volume continue through the join.
 *
 * The lg face matches the body's even parity and occupies y9-18 on the body
 * at y2-25: 7 pixels of air above and 7 below. Nine tones including face.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Flow">
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
  name: 'Flow',
  idea: 'A true circular body whose lower-left arc continues into the tail, with a seven-step lavender-violet lens ramp.',
  ground: 'light',
  palette: [{palette}],
}};
"""
)

print(
    f"{SLUG}: body {BODY_W}x{body_y1 - body_y0 + 1}, "
    f"air {air_above}/{air_below}, tones 9, bounds x{x0}-{x1} y{y0}-{y1}"
)
print(f"body widths: {body_widths}")
print(f"silhouette widths: {silhouette_widths}")
