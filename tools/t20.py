"""Generate t20: a hue-shifting current inside the shipped Twozz silhouette.

Homework, rasterised at the native 32×32 grid:

* Plozz spends eight tones by function: black structure, a grey aerial detail,
  three cyan case tones, and three nested screen-bevel tones.
* Mozz spends eleven tones across the whole disc in directional red reflections.
* Twozz spends five tones, but 438 pixels collapse into one purple field.

This keeps Twozz's proven speech-bubble silhouette and makes colour—not added
hardware, glass, roundness, or simulated depth—the new idea.
"""

import colorsys
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from circles import check  # noqa: E402
from shade import keyline, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"
SLUG = "t20"

KEY = "#241046"
FACE = "#110522"
SURFACE_TONES = [
    "#8864dd",
    "#9564dd",
    "#a264dd",
    "#ae64dd",
    "#bb64dd",
    "#c764dd",
    "#d464dd",
    "#dd64da",
    "#dd64cd",
]


def rows_from_widths(widths, top=2):
    shape = set()
    for y, width in enumerate(widths, start=top):
        left = 16 - width // 2
        shape |= {(left + dx, y) for dx in range(width)}
    return shape


def relative_luminance(colour):
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    light, dark = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


# The shipped body, through y24. The asymmetric tail is deliberately separate.
BODY_WIDTHS = [18, 22, 24, 26, 26] + [28] * 14 + [26, 26, 24, 22]
BODY = rows_from_widths(BODY_WIDTHS)
TAIL = (
    {(x, 25) for x in range(7, 26)}
    | {(x, 26) for x in range(7, 12)}
    | {(x, 27) for x in range(7, 11)}
    | {(x, 28) for x in range(7, 10)}
    | {(x, 29) for x in range(7, 10)}
)
SHAPE = BODY | TAIL

# Body symmetry and roundness are tested without the intentionally asymmetric tail.
assert check(BODY) == BODY_WIDTHS
assert all((31 - x, y) in BODY for x, y in BODY), "body is not symmetric about x=16"

# The complete speech-bubble silhouette must still be free of row spurs.
shape_rows = {}
for x, y in SHAPE:
    shape_rows.setdefault(y, []).append(x)
shape_ys = sorted(shape_rows)
shape_widths = [max(shape_rows[y]) - min(shape_rows[y]) + 1 for y in shape_ys]
for i in range(1, len(shape_widths) - 1):
    assert not (
        shape_widths[i] > shape_widths[i - 1]
        and shape_widths[i] > shape_widths[i + 1]
    ), (
        f"spur at y{shape_ys[i]}: "
        f"{shape_widths[i - 1]}/{shape_widths[i]}/{shape_widths[i + 1]}"
    )

xs = [x for x, _ in SHAPE]
ys = [y for _, y in SHAPE]
assert min(xs) >= 2 and max(xs) <= 29 and min(ys) >= 2 and max(ys) <= 29

# lg/wide/gap2 is 10×11 at y8–18. On the y2–24 body that is exactly 6/6 air.
BODY_WIDTH = max(x for x, _ in BODY) - min(x for x, _ in BODY) + 1
FACE_WIDTH = 10
FACE_TOP, FACE_BOTTOM = 8, 18
BODY_TOP, BODY_BOTTOM = min(y for _, y in BODY), max(y for _, y in BODY)
AIR_ABOVE = FACE_TOP - BODY_TOP
AIR_BELOW = BODY_BOTTOM - FACE_BOTTOM
assert (BODY_WIDTH - FACE_WIDTH) % 2 == 0, "face/body parity mismatch"
assert AIR_ABOVE == AIR_BELOW == 6, f"unequal body air: {AIR_ABOVE}/{AIR_BELOW}"

OUTLINE = keyline(SHAPE)
SURFACE = SHAPE - OUTLINE


def current_value(x, y):
    """A left-to-right colour field whose boundaries bend like one live signal."""
    return x + 2.75 * math.sin((y - 13) * math.pi / 11)


values = {pixel: current_value(*pixel) for pixel in SURFACE}
lo, hi = min(values.values()), max(values.values())


def tone_index(value):
    scaled = (value - lo) / (hi - lo)
    return min(len(SURFACE_TONES) - 1, int(scaled * len(SURFACE_TONES)))


indices = {pixel: tone_index(value) for pixel, value in values.items()}
tone_layers = [
    {pixel for pixel, index in indices.items() if index == i}
    for i in range(len(SURFACE_TONES))
]

assert all(tone_layers), "a surface tone disappeared"
assert set().union(*tone_layers) == SURFACE, "surface ramp has gaps"
assert sum(map(len, tone_layers)) == len(SURFACE), "surface ramp overlaps"
assert len(set(SURFACE_TONES + [KEY, FACE])) >= 8, "too few tones"

# A current can curve, but touching pixels may never skip a tone.
for (x, y), index in indices.items():
    for neighbour in ((x + 1, y), (x, y + 1)):
        if neighbour in indices:
            assert abs(index - indices[neighbour]) <= 1, (
                f"tone jump at {(x, y)} -> {neighbour}"
            )

# Colour, not lightness, is the structure: hue progresses violet -> magenta.
hues = []
for colour in SURFACE_TONES:
    r, g, b = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, _, _ = colorsys.rgb_to_hls(r, g, b)
    hues.append(hue)
assert all(a < b for a, b in zip(hues, hues[1:])), "surface hue does not shift"

rgb_steps = []
for a, b in zip(SURFACE_TONES, SURFACE_TONES[1:]):
    ar = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    br = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    rgb_steps.append(math.sqrt(sum((x - y) ** 2 for x, y in zip(ar, br))))
assert max(rgb_steps) < 16, f"surface step is too abrupt: {max(rgb_steps):.2f}"

face_contrasts = [contrast(FACE, tone) for tone in SURFACE_TONES]
assert min(face_contrasts) >= 4.5, (
    f"face contrast falls to {min(face_contrasts):.2f}:1"
)

layers = [*zip(tone_layers, SURFACE_TONES), (OUTLINE, KEY)]
paths = "\n".join(
    f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'
    for pixels, fill in layers
)

(OUT / f"{SLUG}.astro").write_text(f'''---
/**
 * t20 · Phase Shift
 *
 * Nine close tones move from blue-violet to magenta across one shallow,
 * signal-like curve. This is not a highlight pretending to be glass or depth:
 * hue itself is the event, and the curve continues behind the face and into the
 * tail like a live feed passing through the bubble.
 *
 * The silhouette is the shipped Twozz body, kept because it already reads
 * instantly as chat. Its y2–24 body is 28 wide and symmetric about x=16; the
 * tail is exempt. The 10-wide lg face has matching parity. At gap 2 it spans
 * y8–18, leaving {AIR_ABOVE} rows of body air above and {AIR_BELOW} below.
 *
 * Eleven tones total: deep-indigo keyline, nine surface hues, and a near-black
 * face. Every surface step is under 16 RGB points, touching pixels never skip a
 * tone, and the face keeps at least {min(face_contrasts):.2f}:1 contrast.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Twozz — Phase Shift">
{paths}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: 13, size: 'lg', smile: 'wide', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')

(OUT / f"{SLUG}.meta.ts").write_text(f'''export default {{
  n: '{SLUG}', name: 'Phase Shift',
  idea: 'A live current bends nine close hues from violet to magenta through the shipped bubble; colour itself, not added depth, is the character.',
  ground: 'light',
  palette: {([KEY, *SURFACE_TONES, FACE])!r},
}};
''')

print(
    f"{SLUG} · {len(set(SURFACE_TONES + [KEY, FACE]))} tones "
    f"· body {BODY_WIDTH}×{BODY_BOTTOM - BODY_TOP + 1} "
    f"· face air {AIR_ABOVE}/{AIR_BELOW} "
    f"· fit x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}"
)
print(
    "assertions passed: body symmetry, tail-exempt no-spurs, fit, parity, "
    "equal air, tone coverage/adjacency, hue shift, subtle steps, face contrast"
)
