"""Generate p55-p58: the Plozz bezel set.

Four readings of one idea — *the bezel is the object*. Not a television with a
picture in it, but a dimensional frame whose whole job is to hold a quiet
opening. The opening is where the face lives, so it is left almost plain; all
the material goes into the surround.

The four differ in how the frame is built, not in how it is decorated:

  p55  mitred      square frame, visible 45 degree corner joins, recessed well
  p56  pillow      soft rounded bezel with a continuous crest and one specular
  p57  oblique     the frame turned so its right and lower side walls show
  p58  aperture    an octagonal opening cut through a rounded square

Rules held across all four:

  * the face is the exact 8x8 user face — facePathsAt md / compact / gap 2
  * one 11-step cyan ramp, shared, from the Plozz family colours
  * the opening is calm: never more than two tones under the face
  * no antenna, no controls, no text, no play triangle, no gradients
  * every tone layer follows the contour, so no layer can be a floating slab

Run:  python3 tools/p55_p58.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from face_py import face_box, face_paths  # noqa: E402
from shade import is_slab  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
G = 32

# One ramp for the whole set, so the four read as a family rather than as four
# unrelated blues. Index 0 is the keyline and the face ink; index 10 is the
# opening. Steps are close enough that no single one announces itself.
P = [
    '#04202f',  # 0  ink
    '#06394f',  # 1
    '#075873',  # 2
    '#02769c',  # 3
    '#0791bd',  # 4
    '#12a6d4',  # 5
    '#32b9e4',  # 6
    '#5ccbee',  # 7
    '#85daf5',  # 8
    '#aee8fa',  # 9
    '#d3f4fd',  # 10 opening
]
INK = P[0]

FACE = dict(size='md', smile='compact', gap=2)
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# --------------------------------------------------------------------------
# grid plumbing
# --------------------------------------------------------------------------

def blank():
    return [[-1] * G for _ in range(G)]


def paint(grid, x, y, i):
    if 0 <= x < G and 0 <= y < G:
        grid[y][x] = i


def layer(grid, i):
    return {(x, y) for y in range(G) for x in range(G) if grid[y][x] == i}


def runs(grid, i):
    """Minimal horizontal runs for one tone, as an SVG path string."""
    out = []
    for y in range(G):
        x = 0
        while x < G:
            if grid[y][x] != i:
                x += 1
                continue
            end = x
            while end + 1 < G and grid[y][end + 1] == i:
                end += 1
            out.append(f'M{x} {y}h{end - x + 1}v1h-{end - x + 1}z')
            x = end + 1
    return ' '.join(out)


def outline(body):
    return {p for p in body
            if any((p[0] + dx, p[1] + dy) not in body for dx, dy in NEIGHBOURS)}


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def rr(px, py, x0, y0, x1, y1, r):
    """Is the sample point inside the rounded rectangle with those edges?"""
    if px < x0 or px > x1 or py < y0 or py > y1:
        return False
    dx = max(x0 + r - px, px - (x1 - r), 0.0)
    dy = max(y0 + r - py, py - (y1 - r), 0.0)
    return dx * dx + dy * dy <= r * r


def shells(x0, y0, x1, y1, r, floor, depth):
    """Concentric inward offsets of one rounded rectangle."""
    return [(x0 + k, y0 + k, x1 - k, y1 - k, max(r - k, floor))
            for k in range(depth + 1)]


def shell_index(px, py, sh):
    """How many offsets deep the point sits, or None if it is outside."""
    k = None
    for i, box in enumerate(sh):
        if rr(px, py, *box):
            k = i
        else:
            break
    return k


def facet(px, py, x0, y0, x1, y1):
    """Which of the four sides the point belongs to. Ties fall to top, then
    left, which is what puts a clean 45 degree miter in every corner."""
    d = ((py - y0, 'top'), (px - x0, 'left'), (x1 - px, 'right'), (y1 - py, 'bottom'))
    return min(d)[1]


def rr_normal(px, py, x0, y0, x1, y1, r):
    """Outward unit normal of a rounded rectangle at the nearest boundary."""
    gx = gy = 0.0
    if px < x0 + r:
        gx = px - (x0 + r)
    elif px > x1 - r:
        gx = px - (x1 - r)
    if py < y0 + r:
        gy = py - (y0 + r)
    elif py > y1 - r:
        gy = py - (y1 - r)
    if gx == 0.0 and gy == 0.0:
        f = facet(px, py, x0, y0, x1, y1)
        return {'top': (0.0, -1.0), 'left': (-1.0, 0.0),
                'right': (1.0, 0.0), 'bottom': (0.0, 1.0)}[f]
    n = math.hypot(gx, gy)
    return (gx / n, gy / n)


LIGHT = (-math.sqrt(0.5), -math.sqrt(0.5))  # upper left, as in Mozz


def lit(n):
    return n[0] * LIGHT[0] + n[1] * LIGHT[1]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------
# p55 — mitred
# --------------------------------------------------------------------------
# A square frame with the corner joins left visible. Each of the four bevel
# sides carries its own tone, so the ring bands meet on 45 degree miters
# instead of stacking as concentric rectangles. Four steps of bevel fall to a
# dark well wall, which then flips: the lower and right inner walls catch the
# light bouncing off the opening, the upper and left ones do not. That flip is
# what makes the opening read as recessed rather than drawn on.

def build_p55():
    grid = blank()
    sh = shells(2, 2, 30, 30, 4, 2, 6)
    bezel = {
        'top': [9, 8, 7, 6],
        'left': [8, 7, 6, 5],
        'right': [5, 4, 3, 2],
        'bottom': [4, 3, 2, 1],
    }
    well = {'top': 1, 'left': 2, 'right': 6, 'bottom': 7}
    for y in range(G):
        for x in range(G):
            px, py = x + 0.5, y + 0.5
            k = shell_index(px, py, sh)
            if k is None:
                continue
            if k >= 6:
                paint(grid, x, y, 9 if x + y < 22 else 10)
            elif k == 0:
                paint(grid, x, y, 0)
            elif k == 5:
                paint(grid, x, y, well[facet(px, py, 2, 2, 30, 30)])
            else:
                paint(grid, x, y, bezel[facet(px, py, 2, 2, 30, 30)][k - 1])
    return grid, 16, 16


# --------------------------------------------------------------------------
# p56 — pillow
# --------------------------------------------------------------------------
# The same frame, rolled. Tone is not banded by ring here; it is the surface
# normal turned through the bevel and read against one light. The outer half of
# the bezel faces out and up, the inner half faces in and down, so the two
# halves shade in opposite directions and meet on a crest that runs right round
# the frame. A rectangle cannot fall out of this, because nothing in it is
# axis-aligned except the light.

def build_p56():
    grid = blank()
    box = (2, 2, 30, 30)
    sh = shells(*box, 7, 2, 6)
    for y in range(G):
        for x in range(G):
            px, py = x + 0.5, y + 0.5
            k = shell_index(px, py, sh)
            if k is None:
                continue
            if k >= 6:
                paint(grid, x, y, 9 if x + y < 26 else 10)
            elif k == 0:
                paint(grid, x, y, 0)
            else:
                el = lit(rr_normal(px, py, *box, 7))
                slope = (3 - k) / 3
                v = 5.6 - 0.35 * k + slope * el * 4.3 + 0.55 * el
                paint(grid, x, y, int(clamp(round(v), 1, 9)))
    return grid, 16, 16


# --------------------------------------------------------------------------
# p57 — oblique
# --------------------------------------------------------------------------
# The frame turned a few degrees off square, so two of its side walls come into
# view. The front face keeps the mitred bevel; the walls behind it are the only
# place in the set where a surface is seen edge-on. Because the object is now
# off centre in the box, the face is centred on the *opening*, not on the grid —
# the rule Plozz's own mark follows.

def build_p57():
    grid = blank()
    box = (2, 2, 28, 28)
    sh = shells(*box, 3, 2, 6)
    front = set()
    for y in range(G):
        for x in range(G):
            if shell_index(x + 0.5, y + 0.5, sh) is not None:
                front.add((x, y))

    body = set(front)
    for d in (1, 2):
        body |= {(x + d, y + d) for (x, y) in front}
    key = outline(body)

    wall = {'right': [3, 2], 'bottom': [2, 1], 'corner': [2, 1]}
    for d in (2, 1):
        for (x, y) in front:
            p = (x + d, y + d)
            if p in front or p not in body:
                continue
            side_r = (x + 1, y) not in front
            side_b = (x, y + 1) not in front
            side = 'corner' if side_r and side_b else ('right' if side_r else 'bottom')
            paint(grid, p[0], p[1], wall[side][d - 1])

    bezel = {
        'top': [9, 8, 7, 6],
        'left': [8, 7, 6, 5],
        'right': [4, 3, 3, 2],
        'bottom': [3, 2, 2, 1],
    }
    well = {'top': 1, 'left': 1, 'right': 5, 'bottom': 6}
    for (x, y) in sorted(front):
        px, py = x + 0.5, y + 0.5
        k = shell_index(px, py, sh)
        if k >= 6:
            paint(grid, x, y, 9 if x + y < 24 else 10)
        elif k == 0:
            paint(grid, x, y, 1)
        elif k == 5:
            paint(grid, x, y, well[facet(px, py, *box)])
        else:
            paint(grid, x, y, bezel[facet(px, py, *box)][k - 1])

    for (x, y) in key:
        paint(grid, x, y, 0)
    return grid, 15, 15


# --------------------------------------------------------------------------
# p58 — aperture
# --------------------------------------------------------------------------
# An octagonal opening cut through a rounded square. The depth bands are
# offsets of the *opening*, not of the outer shape, so they start octagonal and
# are progressively squeezed as they meet the rounded corners — the bands are
# never parallel to each other for long. Eight facets take light instead of
# four, and the upper-left chamfer carries a specular run that has no mirror
# anywhere else in the mark.

def build_p58():
    grid = blank()
    box = (2, 2, 30, 30)
    # Facet offsets for the chamfer cut *into* the opening. A countersink faces
    # inward, so it is lit on the far side from the light — the exact inverse of
    # the outer edge, and the thing that makes the opening read as cut rather
    # than drawn. Bands: 0 well, 1-2 countersink, 3-4 plateau, 5-6 outer edge.
    well = {'tl': 1, 'top': 1, 'left': 1, 'tr': 2,
            'bl': 2, 'right': 6, 'bottom': 6, 'br': 7}
    sink = [{'tl': 2, 'top': 2, 'left': 2, 'tr': 3,
             'bl': 3, 'right': 7, 'bottom': 7, 'br': 8},
            {'tl': 3, 'top': 3, 'left': 3, 'tr': 4,
             'bl': 4, 'right': 7, 'bottom': 7, 'br': 8}]
    root2 = math.sqrt(2)

    def opening(px, py):
        """Signed distance outside the octagonal opening."""
        dx, dy = abs(px - 16), abs(py - 16)
        return max(dx - 7, dy - 7, (dx + dy - 10.5) / root2)

    def surround(px, py):
        """Signed distance inside the rounded square."""
        ex, ey = abs(px - 16) - 9, abs(py - 16) - 9
        return -(math.hypot(max(ex, 0.0), max(ey, 0.0)) + min(max(ex, ey), 0.0) - 5)

    def eight(px, py):
        dx, dy = px - 16, py - 16
        v = 'top' if dy < 0 else 'bottom'
        h = 'left' if dx < 0 else 'right'
        spread = abs(dx) - abs(dy)
        if spread > 3:
            return h
        if spread < -3:
            return v
        return {('top', 'left'): 'tl', ('top', 'right'): 'tr',
                ('bottom', 'left'): 'bl', ('bottom', 'right'): 'br'}[(v, h)]

    for y in range(G):
        for x in range(G):
            px, py = x + 0.5, y + 0.5
            if not rr(px, py, *box, 5):
                continue
            din = opening(px, py)
            if din <= 0:
                paint(grid, x, y, 9 if x + y < 24 else 10)
                continue
            # Depth as a fraction of the local bezel width, quantised, so the
            # bands stay even where the octagon runs wide into a rounded corner.
            t = din / (din + surround(px, py))
            band = min(6, int(t * 7))
            el = lit(rr_normal(px, py, *box, 5))
            if band == 0:
                v = well[eight(px, py)]
            elif band <= 2:
                v = sink[band - 1][eight(px, py)]
            elif band <= 4:
                v = 6 if el > 0.35 else 5
            else:
                v = round((5.4 if band == 5 else 5.8) + (3.0 if band == 5 else 3.4) * el)
            paint(grid, x, y, int(clamp(v, 1, 9)))

    body = {(x, y) for y in range(G) for x in range(G) if grid[y][x] >= 0}
    for (x, y) in outline(body):
        paint(grid, x, y, 0)
    return grid, 16, 16


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check(name, grid, cx, cy):
    body = {(x, y) for y in range(G) for x in range(G) if grid[y][x] >= 0}
    used = sorted({grid[y][x] for (x, y) in body})

    assert 8 <= len(used) <= 11, f'{name}: {len(used)} tones, wanted 8-11'

    box = face_box(cx=cx, cy=cy, **FACE)
    assert (box['w'], box['h']) == (8, 8), f'{name}: face is not 8x8'
    field = {i for i in (9, 10)}
    for y in range(box['y'] - 1, box['y'] + box['h'] + 1):
        for x in range(box['x'] - 1, box['x'] + box['w'] + 1):
            assert grid[y][x] in field, \
                f'{name}: face bed is busy at {x},{y} (tone {grid[y][x]})'

    # A calm centre: the opening carries at most two tones.
    opening = {grid[y][x] for (x, y) in body if grid[y][x] >= 9}
    assert len(opening) <= 2, f'{name}: opening has {len(opening)} tones'

    # Every layer has to follow the contour rather than float in the middle.
    for i in used:
        assert not is_slab(layer(grid, i), body), f'{name}: tone {i} reads as a slab'

    # Silhouette: solid, keylined, and inside the family safe area.
    xs = [x for (x, y) in body]
    ys = [y for (x, y) in body]
    assert min(xs) >= 2 and max(xs) <= 29, f'{name}: breaks the 28px safe area'
    assert min(ys) >= 2 and max(ys) <= 29, f'{name}: breaks the 28px safe area'
    assert all(grid[y][x] == 0 for (x, y) in outline(body)), f'{name}: keyline is broken'

    holes = [(x, y) for y in range(min(ys), max(ys) + 1)
             for x in range(min(xs), max(xs) + 1) if (x, y) not in body]
    for (x, y) in holes:
        assert not (min(xs) < x < max(xs) and min(ys) < y < max(ys)
                    and (x - 1, y) in body and (x + 1, y) in body
                    and (x, y - 1) in body and (x, y + 1) in body), \
            f'{name}: pinhole at {x},{y}'

    return used


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------


DOC_P55 = """A square bezel built the way a picture frame is built — four sloped sides,
 * each with its own tone, joined on visible 45 degree miters. The bands cannot
 * read as concentric rectangles because no band is one colour all the way
 * round.
 *
 * Four bevel steps fall to a dark well wall, and at the well the light flips:
 * the lower and right inner walls take the bounce off the opening, the upper
 * and left ones stay in shadow. That inversion is the whole reason the opening
 * reads as cut into the frame rather than printed on it.
 *
 * The opening is 16 across and carries two tones — the field, and the shadow
 * the upper-left wall throws across its near corner, which stops well short of
 * the face."""

DOC_P56 = """The frame rolled. Tone here is not a ring index — it is the surface normal
 * turned through the bevel and read against a single upper-left light. The
 * outer half faces out and up, the inner half faces in and down, so the two
 * shade in opposite directions and meet on a crest that travels the whole way
 * round.
 *
 * Nothing in the shading is axis-aligned except the light, so the bands bend
 * continuously and never stack into rectangles. Corner radius 7 against p55's
 * 4 gives the set two clearly different silhouettes at 16px."""

DOC_P57 = """The frame turned a few degrees, so two of its side walls show. The front keeps
 * the mitred bevel; the walls behind it are the only surfaces in the set seen
 * edge-on, and they are the only asymmetry in the silhouette — which is what
 * makes this one identifiable at 16px.
 *
 * Because the object now sits off centre in the box, the face is centred on the
 * opening rather than on the grid. That is Plozz's own rule: the face belongs
 * to the screen, not to the 32-box."""

DOC_P58 = """An eight-sided opening countersunk through a rounded square. Depth is measured
 * as a fraction of the local bezel width, so the bands stay even where the
 * octagon runs wide into a rounded corner — they begin octagonal, end square,
 * and are never parallel to each other for long.
 *
 * The two chamfers are lit in opposite directions, and that is the mark: the
 * outer edge takes the light on its upper left, the countersink faces inward
 * and so takes it on its lower right, and a flat plateau sits between them.
 * Eight facets carry that instead of four."""

SPECS = [
    ('p55', 'Miter', build_p55, DOC_P55,
     'A square media frame with its corner joins left showing: four bevel sides, '
     'four tones, meeting on 45 degree miters around a recessed opening.'),
    ('p56', 'Pillow', build_p56, DOC_P56,
     'The same frame rolled into a soft pillow bezel, shaded off one light rather '
     'than banded, with a crest running right around it.'),
    ('p57', 'Oblique', build_p57, DOC_P57,
     'The frame turned off square so its right and lower side walls come into '
     'view: the one mark in the set with real thickness.'),
    ('p58', 'Aperture', build_p58, DOC_P58,
     'An octagonal opening countersunk through a rounded square, its outer edge '
     'and its inner chamfer lit from opposite directions.'),
]

TEMPLATE = '''---
/**
 * {slug} · Plozz — {title}
 *
 * {doc}
 *
 * {tones} tones from the shared bezel ramp. The face is the exact 8x8 user
 * face — facePathsAt md, compact smile, gap 2 — centred on the opening at
 * ({cx}, {cy}) with {air}px of clear field to each side of it. Generated by
 * tools/p55_p58.py; edit that, not this.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Plozz — {title}">
{rows}
  <g fill="{ink}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: {cx}, cy: {cy}, size: 'md', smile: 'compact', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''


def air_around(grid, cx, cy):
    """Clear opening between the face box and the first frame pixel, measured
    along the four axes — the corners of an octagonal opening cut in sooner."""
    box = face_box(cx=cx, cy=cy, **FACE)
    out = []
    for dx, dy, sx, sy in ((-1, 0, box['x'], cy), (1, 0, box['x'] + box['w'] - 1, cy),
                           (0, -1, cx, box['y']), (0, 1, cx, box['y'] + box['h'] - 1)):
        n = 0
        x, y = int(sx), int(sy)
        while True:
            x, y = x + dx, y + dy
            if not (0 <= x < G and 0 <= y < G) or grid[y][x] < 9:
                break
            n += 1
        out.append(n)
    return min(out)


def main():
    report = []
    for slug, title, build, doc, idea in SPECS:
        grid, cx, cy = build()
        used = check(slug, grid, cx, cy)
        rows = '\n'.join(f'  <path d="{runs(grid, i)}" fill="{P[i]}" />' for i in used)
        (OUT / f'{slug}.astro').write_text(TEMPLATE.format(
            slug=slug, title=title, doc=doc, tones=len(used), rows=rows,
            cx=cx, cy=cy, ink=INK, air=air_around(grid, cx, cy),
        ))
        (OUT / f'{slug}.meta.ts').write_text(
            "export default {\n"
            f"  n: '{slug}', name: '{title}',\n"
            f"  idea: '{idea}',\n"
            "  ground: 'light',\n"
            f"  palette: [{', '.join(repr(P[i]) for i in used)}],\n"
            "};\n"
        )
        report.append((slug, title, used, cx, cy, grid))
    return report


if __name__ == '__main__':
    for slug, title, used, cx, cy, grid in main():
        print(f'{slug} · {title} · {len(used)} tones · face md/compact/gap2 at '
              f'({cx},{cy}) · {air_around(grid, cx, cy)}px clear · checks passed')
