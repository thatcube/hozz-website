"""Generate t31-t34: the canonical rounded Twozz bubble, four controlled ways.

One silhouette family, four variants of proportion and tail prominence. Every
variant is built by the same code so the only differences are the ones being
tested.

Silhouette
    A balanced rounded body, symmetric about x=15.5 so the 8-wide face lands on
    centre exactly. The bottom-left corner turns until it runs out of curve and
    the tail's left edge carries straight on down from wherever that was — the
    tail is not positioned, it is *where the body stopped*, which is what makes
    it read as integrated rather than glued on. To the right of the tail's
    shoulder the bottom is one clean unbroken run to the corner.

Depth
    A Euclidean distance-to-edge field. The tone is a step function of that
    distance, so every boundary between tones is an honest offset of the
    silhouette and bends around the tail exactly as it bends around the body.
    Seven tones fall inward from a light meniscus just inside the keyline to a
    calm core, which is Hozz's concentric falloff. The light then moves that
    boundary by one tone on the side facing away from it, which is Mozz's
    sidedness: the shaded flank reaches each tone one ring early. Only the
    shadow moves. A lit side that took a ring back would leave the core short
    of the face, because 32 pixels only buys seven rings between the keyline
    and the middle. The core is exempt from the shift either way, so the field
    the face sits on is one flat tone however the light falls.

Keyline
    Derived from the silhouette, never drawn. It cannot fail to track the tail.

    python tools/t31_t34.py            # write the four marks
    python tools/t31_t34.py --preview  # also render inspection tiles
"""

import colorsys
import math
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from shade import is_slab, keyline, to_paths  # noqa: E402

OUT = ROOT / "src/components/mark/logos"
GRID = 32
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))

KEY = "#26124a"
FACE = "#ffffff"

# Seven surface tones, light meniscus to calm core, interpolated through HSV so
# saturation and value move together and no step exceeds 18 RGB points.
RIM = (205, 177, 248)
CORE = (122, 69, 216)
TONE_COUNT = 7
RING_STEPS = 7   # depth at which the falloff reaches the core


def ramp():
    a = colorsys.rgb_to_hsv(*[v / 255 for v in RIM])
    b = colorsys.rgb_to_hsv(*[v / 255 for v in CORE])
    out = []
    for i in range(TONE_COUNT):
        t = i / (TONE_COUNT - 1)
        hsv = [x + (y - x) * t for x, y in zip(a, b)]
        out.append(tuple(round(v * 255) for v in colorsys.hsv_to_rgb(*hsv)))
    return out


TONES = ramp()
HEX = ["#%02x%02x%02x" % c for c in TONES]


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------

def rounded_body(left, right, top, bottom, radius):
    """A rounded rectangle sampled at pixel centres."""
    body = set()
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            px, py = x + 0.5, y + 0.5
            dx = max(left + radius - px, px - (right + 1 - radius), 0.0)
            dy = max(top + radius - py, py - (bottom + 1 - radius), 0.0)
            if dx * dx + dy * dy <= radius * radius:
                body.add((x, y))
    return body


def tail_for(body, bottom, width, depth, lean=0.0, tip=2, curve=1.0):
    """The tail, grown down out of the bottom-left corner's own end.

    `tx` is not a parameter: it is wherever the body's bottom row actually
    stops, so the corner curve and the tail's left edge are one continuous
    line. The right edge tapers back toward it.
    """
    row = [x for (x, y) in body if y == bottom]
    tx = min(row)
    tail = set()
    spans = []
    for i in range(1, depth + 1):
        t = (i - 1) / (depth - 1) if depth > 1 else 1.0
        left = tx - round(lean * t)
        span = tip + (width - tip) * (1.0 - t) ** curve
        right = left + max(tip, round(span)) - 1
        spans.append((left, right))
        for x in range(left, right + 1):
            tail.add((x, bottom + i))
    return tail, tx, spans


# Body height is fixed at 24 rows across the set. That is not a stylistic
# choice: seven tones falling from the keyline to a flat core need seven rings
# of air above the face, and 8 face rows plus 8 rings above plus 8 below is
# exactly 24. Proportion varies by width, corner radius and tail instead.
VARIANTS = {
    "t31": dict(
        name="Bubble, Canonical",
        body=(2, 29, 2, 25), radius=6.6,
        tail=dict(width=7, depth=4, lean=0, tip=2, curve=1.0),
        face=(16, 14), light=(11.5, 7.0), turn=(0.34, 0.70),
        title="Twozz — Bubble, Canonical",
    ),
    "t32": dict(
        name="Bubble, Narrow",
        body=(3, 28, 2, 25), radius=7.0,
        tail=dict(width=7, depth=4, lean=0, tip=2, curve=1.0),
        face=(16, 14), light=(11.0, 6.5), turn=(0.30, 0.62),
        title="Twozz — Bubble, Narrow",
    ),
    "t33": dict(
        name="Bubble, Wide",
        body=(1, 30, 2, 25), radius=6.0,
        tail=dict(width=8, depth=4, lean=0, tip=2, curve=0.7),
        face=(16, 14), light=(12.0, 7.5), turn=(0.38, 0.76),
        title="Twozz — Bubble, Wide",
    ),
    "t34": dict(
        name="Bubble, Long Run",
        body=(2, 29, 2, 25), radius=4.2,
        tail=dict(width=7, depth=4, lean=0, tip=2, curve=0.85),
        face=(16, 14), light=(11.0, 8.0), turn=(0.32, 0.66),
        title="Twozz — Bubble, Long Run",
    ),
}


# --------------------------------------------------------------------------
# The face, mirrored from src/data/mark.ts (md, compact, gap 2) so the core can
# be measured against exactly the pixels facePathsAt will draw.
# --------------------------------------------------------------------------

def face_pixels(cx, cy):
    eyes = [[(0, 2)], [(1, 2)], [(0, 1)], [(0, 2)]]
    rows = [[(a, b) for (a, b) in runs] + [(a + 5, b + 5) for (a, b) in runs]
            for runs in eyes]
    rows += [[], [], [(1, 1), (6, 6)], [(2, 5)]]
    top = round(cy - len(rows) / 2)
    left = round(cx - 4)
    out = {(left + x, top + i)
           for i, runs in enumerate(rows)
           for a, b in runs
           for x in range(a, b + 1)}
    return out, (left, top, left + 7, top + 7)


# --------------------------------------------------------------------------
# Shading
# --------------------------------------------------------------------------

def ring_field(shape):
    """Euclidean distance from each pixel to the first pixel that isn't shape.

    Euclidean rather than the usual four-neighbour flood: a flood measures in
    diamonds, so its contours come to a point at the corners and the flat core
    ends up looking like a rectangle with the corners bitten off. Straight-line
    distance gives contours that are honest offsets of the silhouette, which is
    what an inset should be.
    """
    out = {}
    for (x, y) in shape:
        best = 99.0
        for dy in range(-13, 14):
            for dx in range(-13, 14):
                if (x + dx, y + dy) in shape:
                    continue
                d = math.hypot(dx, dy)
                if d < best:
                    best = d
        out[(x, y)] = best - 1.0
    return out


def shade(shape, rim, interior, spec):
    """Concentric bands, warped by one directional step.

    The band is a step function of straight-line distance to the edge, so every
    boundary is an offset of the silhouette and nothing can speckle. The light
    then moves that boundary by exactly one tone on the side facing away from
    it — the shaded side reaches each tone one ring early — which is enough to
    give the form a side without giving the bands a second geometry to obey.
    The light never lightens, only the shadow deepens: a bubble this small has
    exactly seven rings between its keyline and its core and a lit side that
    borrowed one of them would leave the core short of the face. The core is
    exempt either way, so the field the face sits on is one tone whichever way
    the light falls.
    """
    ring_raw = ring_field(shape)
    lx, ly = spec["light"]
    lit = {p: math.hypot(p[0] + 0.5 - lx, p[1] + 0.5 - ly) for p in shape}
    near, far = min(lit.values()), max(lit.values())
    lo, hi = spec["turn"]

    index = {}
    for p in interior:
        band = min(max(round(ring_raw[p]) - 1, 0), TONE_COUNT - 1)
        if band == TONE_COUNT - 1:
            index[p] = band
            continue
        away = (lit[p] - near) / (far - near)
        shift = round(min(max((away - lo) / (hi - lo), 0.0), 1.0))
        index[p] = min(TONE_COUNT - 2, max(0, band + shift))
    return index


def relax(index):
    """Pull the tone field down to its 1-Lipschitz envelope.

    Two pixels that touch must not skip a tone, or the ramp stops being a ramp
    and starts being a contour line. The infimal convolution with grid distance
    is the smallest change that guarantees it, and it can only lighten a pixel
    — it cannot invent a step the falloff did not ask for.
    """
    index = dict(index)
    changed = True
    while changed:
        changed = False
        for p in index:
            lo = min((index[(p[0] + dx, p[1] + dy)] + 1
                      for dx, dy in NEIGHBOURS
                      if (p[0] + dx, p[1] + dy) in index),
                     default=index[p])
            if lo < index[p]:
                index[p] = lo
                changed = True
    return index


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def luminance(rgb):
    lin = []
    for c in rgb:
        c /= 255
        lin.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def connected(shape):
    start = next(iter(shape))
    seen, stack = {start}, [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in NEIGHBOURS:
            p = (x + dx, y + dy)
            if p in shape and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(shape)


def holes(shape):
    seen = {(-1, -1)}
    stack = [(-1, -1)]
    while stack:
        x, y = stack.pop()
        for dx, dy in NEIGHBOURS:
            p = (x + dx, y + dy)
            if (-1 <= p[0] <= GRID and -1 <= p[1] <= GRID
                    and p not in seen and p not in shape):
                seen.add(p)
                stack.append(p)
    return any((x, y) not in shape and (x, y) not in seen
               for y in range(GRID) for x in range(GRID))


def check(shape, rim, layers, spans, face, face_box, tx, bottom):
    bad = []
    if not connected(shape):
        bad.append("silhouette is not one piece")
    if holes(shape):
        bad.append("silhouette encloses a hole")
    xs = [x for x, _ in shape]
    ys = [y for _, y in shape]
    if min(xs) < 1 or max(xs) > 30 or min(ys) < 1 or max(ys) > 30:
        bad.append("silhouette has no margin left on the grid")

    widths = [b - a + 1 for a, b in spans]
    if any(b > a for a, b in zip(widths, widths[1:])):
        bad.append(f"tail widens on the way down: {widths}")
    if widths[-1] > 2:
        bad.append(f"tail ends in a {widths[-1]}px square cap")
    if any(w < 2 for w in widths):
        bad.append(f"tail thins to a spike: {widths}")
    if any(a > tx for a, _ in spans):
        bad.append("tail steps inward off the corner")

    row = sorted(x for (x, y) in shape if y == bottom)
    run = len([x for x in row if x > spans[0][1]])
    if run < 11:
        bad.append(f"lower-right run is only {run}px")

    fx0, fy0, fx1, fy1 = face_box
    calm = {i for i, layer in enumerate(layers)
            for y in range(fy0 - 1, fy1 + 2)
            for x in range(fx0 - 1, fx1 + 2)
            if (x, y) in layer}
    if len(calm) != 1:
        bad.append(f"field under the face uses {len(calm)} tones")
    core = TONES[max(calm)] if calm else CORE
    ink = tuple(int(FACE[i:i + 2], 16) for i in (1, 3, 5))
    if contrast(core, ink) < 4.5:
        bad.append(f"face contrast {contrast(core, ink):.2f}:1")
    if not face <= (shape - rim):
        bad.append("face overruns the keyline")

    tail = {p for p in shape if p[1] > bottom}
    if len({i for i, layer in enumerate(layers) if layer & tail}) < 2:
        bad.append("tail carries no shading")

    # Every tone but the last is tested for the pasted-block failure. The last
    # is the core, and a plain core is not a fault here — it is what all three
    # shipped marks do, and it is where the face has to sit.
    for i, layer in enumerate(layers[:-1]):
        if is_slab(layer, shape):
            bad.append(f"tone {i} is a floating slab")
    return bad, run


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def astro(slug, spec, rim, layers, notes):
    cx, cy = spec["face"]
    lines = [f'  <path d="{" ".join(to_paths(layer))}" fill="{HEX[i]}" />'
             for i, layer in enumerate(layers) if layer]
    lines.append(f'  <path d="{" ".join(to_paths(rim))}" fill="{KEY}" />')
    doc = "\n".join([f"/**", f" * {slug} · {spec['name']}", " *"]
                    + [(" * " + n if n else " *") for n in notes] + [" */"])
    return f"""---
{doc}
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="{spec['title']}">
{chr(10).join(lines)}
  <g fill="{FACE}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: {cx}, cy: {cy}, size: 'md', smile: 'compact', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
"""


def meta(slug, spec, idea):
    swatches = ", ".join(f"'{c}'" for c in [KEY] + HEX[::-1])
    idea = idea.replace("'", "\\'")
    return f"""export default {{
  n: '{slug}', name: '{spec["name"]}',
  idea: '{idea}',
  ground: 'light',
  palette: [{swatches}],
}};
"""


# --------------------------------------------------------------------------
# Preview rendering
# --------------------------------------------------------------------------

def png(path, width, height, rows):
    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(tag, data):
        c = tag + data
        return len(data).to_bytes(4, "big") + c + zlib.crc32(c).to_bytes(4, "big")

    head = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head)
                     + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def cells(rim, layers, face):
    grid = {}
    for i, layer in enumerate(layers):
        for p in layer:
            grid[p] = TONES[i]
    for p in rim:
        grid[p] = tuple(int(KEY[j:j + 2], 16) for j in (1, 3, 5))
    ink = tuple(int(FACE[j:j + 2], 16) for j in (1, 3, 5))
    for p in face:
        grid[p] = ink
    return grid


def nearest(grid, size, bg):
    rows = []
    for j in range(size):
        row = []
        for i in range(size):
            row += list(grid.get((int(i * GRID / size), int(j * GRID / size)), bg))
        rows.append(row)
    return rows


def area(grid, size, bg):
    step = GRID / size
    rows = []
    for j in range(size):
        row = []
        for i in range(size):
            acc, n = [0.0, 0.0, 0.0], 0
            for sy in range(int(j * step), int((j + 1) * step)):
                for sx in range(int(i * step), int((i + 1) * step)):
                    c = grid.get((sx, sy), bg)
                    for ch in range(3):
                        acc[ch] += c[ch]
                    n += 1
            row += [round(v / max(n, 1)) for v in acc]
        rows.append(row)
    return rows


def zoom(rows, size, scale):
    out = []
    for row in rows:
        big = []
        for i in range(size):
            big += row[i * 3:i * 3 + 3] * scale
        out += [big] * scale
    return out


LIGHT = (246, 243, 238)
DARK = (23, 18, 38)


def sheet(path, marks, bg):
    """Every variant across the sizes that decide it, at inspectable scale."""
    cols = [(96, 1, nearest), (28, 3, nearest), (28, 3, area),
            (16, 5, nearest), (16, 5, area)]
    pad = 14
    widths = [s * z for s, z, _ in cols]
    w = pad + sum(x + pad for x in widths)
    h = pad + len(marks) * (96 + pad)
    canvas = [list(LIGHT) * w for _ in range(h)]
    for r, grid in enumerate(marks):
        x = pad
        for size, z, fn in cols:
            tile = zoom(fn(grid, size, bg), size, z)
            side = size * z
            oy = pad + r * (96 + pad) + (96 - side) // 2
            for j, row in enumerate(tile):
                canvas[oy + j][x * 3:(x + side) * 3] = row
            x += side + pad
    png(path, w, h, canvas)


# --------------------------------------------------------------------------

NOTES = {
    "t31": [
        "The reference shape taken at its word, and nothing added to it.",
        "",
        "Twenty-eight columns of body on a 6.6 radius, x2 to x29, symmetric about",
        "x=15.5 so the 8-wide face lands on centre with no half-pixel to argue",
        "about. The bottom-left corner turns until it runs out of curve at x6 and",
        "the tail's left edge carries straight on down from there. That is the",
        "whole trick: the tail is not placed, it is where the body stopped, which",
        "is the difference between a tail and a wedge glued on. It falls four rows",
        "at 7, 5, 4 and 2 pixels wide, and to the right of its shoulder at x13 the",
        "bottom is one unbroken run of thirteen pixels to the corner — the part of",
        "a chat bubble the eye actually uses to identify it.",
        "",
        "Eight violet tones: seven surfaces and the keyline. The tone is a step",
        "function of straight-line distance to the edge, so the bands are offsets",
        "of the outline rather than a second shape laid over it, and they bend",
        "around the tail because the tail is part of the same silhouette. Seven",
        "rings fall from a meniscus inside the keyline to a flat core. The light",
        "sits up and left and only deepens: the shaded flank reaches each tone one",
        "ring early, the lit flank keeps its ring. The core is exempt, so the field",
        "under the face is one calm tone and the face has nothing to fight.",
        "",
        "The keyline is derived from the silhouette rather than drawn, so it cannot",
        "drift off the tail. Every pixel is on the 32 grid; nothing is a gradient.",
    ],
    "t32": [
        "The same bubble narrowed by a column each side and rounded harder, to ask",
        "how much body a speech bubble can lose and still be one.",
        "",
        "Twenty-six columns, x3 to x28, on a 7.0 radius — the roundest of the four",
        "and the only one where the curve is doing more work than the straights.",
        "The corner runs out at x7, one pixel later than the canonical, which walks",
        "the tail inward and shortens the bottom run to eleven pixels. Eleven is",
        "about the floor: below that the run stops reading as a run and the shape",
        "starts to look like a rounded square that happens to have a spur.",
        "",
        "Tail widths 7, 5, 4, 2 over four rows, identical to the canonical. Holding",
        "the tail still while the body moves is the point of the variant; if this",
        "one loses to t31 it loses on body proportion alone, which is a decidable",
        "question rather than a taste one.",
        "",
        "Eight violet tones, the same seven-ring falloff to a flat core, with the",
        "light a half pixel higher and further left and the turn to shadow a little",
        "earlier — a rounder body needs its shaded side to start sooner or it reads",
        "flat.",
    ],
    "t33": [
        "The widest body the grid allows, with the tail at full prominence.",
        "",
        "Thirty columns, x1 to x30, one pixel of air each side and a 6.0 radius.",
        "The extra width buys two things: the longest bottom run of the group at",
        "fourteen pixels, and a corner that runs out early at x5, which puts the",
        "tail further from the centre and makes the asymmetry unmistakable at a",
        "glance. That is what a speech bubble is for.",
        "",
        "The tail is the fullest here, 8, 7, 5 and 2 pixels over four rows: a slow",
        "shoulder then a fast finish, so it leaves the body thick enough to carry",
        "two tones of shading rather than reading as a single dark spike. A tail",
        "that only holds one tone is an appendage; a tail that holds the field is",
        "part of the object.",
        "",
        "Eight violet tones over seven rings to a flat core. The light sits lower",
        "and more central than in the canonical and the turn to shadow is late,",
        "which suits a wide shallow form — a broad body lit hard from the corner",
        "reads as a lozenge rather than a bubble.",
        "",
        "The cost is margin. At one pixel of air the mark sits close to the edge of",
        "its box, which is fine in the gallery and worth checking anywhere the mark",
        "is set tight against other things.",
    ],
    "t34": [
        "Tighter corners, so every straight runs longer.",
        "",
        "Twenty-eight columns like the canonical, x2 to x29, but on a 4.2 radius",
        "instead of 6.6. The curve arrives late and turns fast. The corner runs out",
        "at x4, the tail shoulder lands at x11, and the bottom run is seventeen",
        "pixels — four longer than the canonical and the longest in the set.",
        "",
        "This is the favicon argument. At 16 pixels a 32-grid mark is halved and",
        "the only things that survive are long straights and the silhouette's",
        "corners; a generous radius spends its pixels on curve that the downsample",
        "throws away. The risk is the opposite one: a late fast curve can read as a",
        "square with the corners knocked off rather than as a rounded bubble, which",
        "is why this is a variant to look at rather than a rule.",
        "",
        "Tail 7, 6, 4, 2 over four rows. Eight violet tones, seven rings to a flat",
        "core, light up and left, shadow-only turn. Because the body is squarer the",
        "rings are squarer too, and the core reads as a rounded rectangle inset",
        "rather than a dome — honest to the silhouette, but a visible difference in",
        "character from t31.",
    ],
}


IDEAS = {
    "t31": "The reference bubble drawn exactly: a balanced 28-column body on a 6.6 radius, a tail that continues the bottom-left corner's own line instead of joining it, and one clean thirteen-pixel run along the bottom right.",
    "t32": "The same bubble narrowed to 26 columns and rounded to 7.0 with the tail held identical, testing how much body a speech bubble can lose before an eleven-pixel bottom run stops reading as a run.",
    "t33": "The widest body the grid allows at 30 columns, with the fullest tail, for the longest bottom run and the most unmistakable speech read — at the cost of a single pixel of margin.",
    "t34": "A 4.2 radius so the curve arrives late and every straight runs longer, buying a seventeen-pixel bottom run for favicon legibility and risking a squarer, less bubble-like read.",
}

def build(slug, spec):
    left, right, top, bottom = spec["body"]
    body = rounded_body(left, right, top, bottom, spec["radius"])
    tail, tx, spans = tail_for(body, bottom, **spec["tail"])
    shape = body | tail
    rim = keyline(shape)
    interior = shape - rim
    face, face_box = face_pixels(*spec["face"])

    index = relax(shade(shape, rim, interior, spec))
    layers = [set() for _ in range(TONE_COUNT)]
    for p, i in index.items():
        layers[i].add(p)

    bad, run = check(shape, rim, layers, spans, face, face_box, tx, bottom)
    skips = [p for p in index for dx, dy in NEIGHBOURS
             if (p[0] + dx, p[1] + dy) in index
             and abs(index[p] - index[(p[0] + dx, p[1] + dy)]) > 1]
    if skips:
        bad.append(f"tone field skips a step at {len(skips)} pixels")

    xs = [x for x, _ in shape]
    ys = [y for _, y in shape]
    info = (f"{slug}: bbox x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}  "
            f"tail x{tx} w{[b - a + 1 for a, b in spans]}  run {run}  "
            f"tones {sum(1 for l in layers if l)}+keyline")
    return dict(shape=shape, rim=rim, layers=layers, face=face,
                bad=bad, info=info)


def main():
    ok = True
    marks = []
    for slug, spec in VARIANTS.items():
        built = build(slug, spec)
        print(built["info"])
        for problem in built["bad"]:
            ok = False
            print(f"  !! {problem}")
        (OUT / f"{slug}.astro").write_text(
            astro(slug, spec, built["rim"], built["layers"], NOTES[slug]))
        (OUT / f"{slug}.meta.ts").write_text(meta(slug, spec, IDEAS[slug]))
        marks.append(cells(built["rim"], built["layers"], built["face"]))

    if "--preview" in sys.argv:
        out = ROOT / "tools/_preview_t31"
        out.mkdir(exist_ok=True)
        sheet(out / "light.png", marks, LIGHT)
        sheet(out / "dark.png", marks, DARK)
        print(f"previews in {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
