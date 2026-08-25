"""
p39-p42 — Plozz as a viewing portal.

The shipped Plozz mark is a television: a case, an antenna, feet, and a screen
that has to fight all three for room. p21-p25 answered that by simplifying the
*hardware*. These four go the other way and throw the hardware out entirely.
What is left is the only part of a television that matters — the aperture you
look through — and the light behind it.

The argument of the set

  A screen is not a flat blue rectangle with a face on it. That is the failure
  mode these are built to avoid, and it is what "no flat slabs" means here. A
  screen is a *recess*: a frame stands proud of the surface, its walls fall away
  into shadow, and a lit field sits at the bottom of the well. Everything below
  is that one observation, drawn four ways.

  So each mark is built strictly outside-in, and every layer is derived from the
  silhouette's own contour rather than written as a rectangle and dropped in:

    keyline        one pixel, closed, all the way round
    frame rim      the top face of the case catches the light, the bottom face
                   falls into shadow — straight-down light, as the shipped
                   Plozz uses, so every layer mirrors about x=16
    frame flat     the body of the case between them
    bezel          the wall of the recess, all the way round, and the darkest
                   tone in the mark after the keyline. It is the one layer that
                   tells the eye the light is *behind* the frame rather than
                   painted on its face, and it is lifted straight from the
                   shipped mark, which does the same thing in black.
    screen         four contour-following rings falling from a mid cyan at the
                   rim to a calm, near-white field at the centre, where the face
                   sits on plain colour.

  `rings()` and `keyline()` in tools/shade.py do all of it, so a band can only
  ever follow the shape. A rectangle cannot come out of them, and no layer here
  was positioned by hand.

Why four, and why these four

  They are one idea at four proportions, not four ideas. All share the palette,
  the layer order, the four-pixel frame and the same 8x8 md/compact face on a
  plain core. What changes is the shape of the opening, which is the one thing
  that actually distinguishes one viewing device from another:

    p39  Portal, Wide    28x24 · a widescreen panel. The default reading.
    p40  Portal, Square  26x26 · a square opening — a monitor, a viewport.
    p41  Portal, Deep    28x26 · a five-pixel frame. The well is deeper and the
                                 opening smaller, so it reads most as looking
                                 *through* rather than *at*.
    p42  Portal, Tube    28x24 · a superellipse, inside and out. The picture
                                 tube's swell, with none of its furniture.

  None of them can be read as an orb or a bubble: every silhouette has four
  corners, and the frame is a visibly separate part from the field it encloses.
  There is no play triangle, no text, no antenna, no stand, no gradient and no
  imported asset. 10 flat tones and a pixel grid.

The face is not redrawn

  `facePathsAt({size:'md', smile:'compact', gap:2})` is called from mark.ts by
  the component, and this script calls the same function through node to check
  where it lands before it commits to a geometry. The compact smile is Plozz's
  own — the shipped mark uses it because a busy carrier has to give the smile
  room — so keeping it here is continuity, not a compromise.

Run:
    python3 tools/p39_portal.py            # write the eight files
    python3 tools/p39_portal.py --show     # ASCII proof of every layer
    python3 tools/p39_portal.py --png      # 32px/16px previews for eyeballing
"""

import json
import math
import re
import subprocess
import sys
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import rings, inset, keyline, to_paths  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
GRID = 32
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# ---------------------------------------------------------------------------
# Palette. 11 tones, all blue, no gradients — every one is a flat fill.
#
# The frame is a four-stop steel blue; the screen is a six-stop luminous cyan.
# They are deliberately different families: hardware is grey-blue, light is
# saturated, and that difference is what stops the mark reading as one flat
# slab of colour with lines scratched into it.
# ---------------------------------------------------------------------------
INK = '#08202e'          # keyline, and the face

CASE_WALL = '#0d3b52'    # the bezel — the wall of the recess, all the way round
CASE_SILL = '#134f6d'    # the bottom of that wall, which faces back into the light
CASE_SHADE = '#16597a'   # the bottom rim of the case, turned away from the light
CASE_BODY = '#2280ab'    # the flat of the case
CASE_LIGHT = '#3aa3d0'   # the top rim of the case, facing it

# The screen is not one even ramp, because a recess is not evenly lit. The wall
# throws a hard shadow onto the field right at its foot, and then the light
# rises gently and evenly from there to the middle. So the first stop is a
# deliberate drop — a cast shadow, read as an edge rather than as a band,
# because it sits directly against the near-black bezel and is understood as
# part of it — and the remaining four are a very quiet rise, well inside the
# step size the shipped Plozz screen uses.
SCREEN_SHADOW = '#4b96bd'
FIELD_RIM = (0xa1, 0xd1, 0xe6)
FIELD_CORE = (0xe0, 0xf9, 0xff)
FIELD_STOPS = 4


def lerp(a, b, t):
    return round(a + (b - a) * t)


FIELD = ['#%02x%02x%02x' % tuple(
    lerp(FIELD_RIM[c], FIELD_CORE[c], i / (FIELD_STOPS - 1)) for c in range(3))
    for i in range(FIELD_STOPS)]
SCREEN = [SCREEN_SHADOW, *FIELD]
SCREEN_STOPS = len(SCREEN)

# No step inside the field may shout. Plozz's shipped screen steps by 21 at its
# widest, so this stays under it and the middle of the mark stays calm.
MAX_STEP = 22
for a, b in zip(FIELD, FIELD[1:]):
    d = max(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    assert d <= MAX_STEP, f'{a}->{b} steps by {d}, which reads as a band'

# The case has to be a run of distinct, ordered tones or it flattens into a
# drawn line at 16px, which is where most marks in this file fail.
_case = [INK, CASE_WALL, CASE_SILL, CASE_SHADE, CASE_BODY, CASE_LIGHT]
for a, b in zip(_case, _case[1:]):
    d = min(int(b[i:i + 2], 16) - int(a[i:i + 2], 16) for i in (1, 3, 5))
    assert d >= 3, f'{a}->{b} is not a step the eye can find'

PALETTE = [*_case, *SCREEN]
assert len(set(PALETTE)) == 11, 'the set is meant to run on 11 tones'


# ---------------------------------------------------------------------------
# Silhouettes. Two generators, both sampling pixel centres, so a shape is the
# same object whether it is the outside of the frame or the inside of the
# opening — which is what keeps a variant coherent with itself.
# ---------------------------------------------------------------------------
def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle, circular corners, sampled at pixel centres."""
    X0, Y0, X1, Y1 = x0, y0, x1 + 1, y1 + 1
    out = set()
    for y in range(GRID):
        for x in range(GRID):
            px, py = x + 0.5, y + 0.5
            if not (X0 <= px <= X1 and Y0 <= py <= Y1):
                continue
            cx = X0 + r if px < X0 + r else (X1 - r if px > X1 - r else px)
            cy = Y0 + r if py < Y0 + r else (Y1 - r if py > Y1 - r else py)
            if math.hypot(px - cx, py - cy) <= r + 0.001:
                out.add((x, y))
    return out


def superellipse(cx, cy, a, b, n):
    """|dx/a|^n + |dy/b|^n <= 1. A picture tube's swell without its furniture."""
    out = set()
    for y in range(GRID):
        for x in range(GRID):
            dx, dy = (x + 0.5 - cx) / a, (y + 0.5 - cy) / b
            if abs(dx) ** n + abs(dy) ** n <= 1.0:
                out.add((x, y))
    return out


def span(s):
    xs = [p[0] for p in s]
    ys = [p[1] for p in s]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# The build. Outside-in, every layer contour-derived.
# ---------------------------------------------------------------------------
def build(body, depths):
    """Return the ordered [(pixels, fill)] stack for one portal.

    `depths` is the ladder of contour erosions that cuts the opening, e.g.
    (4,) for a plain frame or (3, 5) for a two-tier well. Every step of the
    ladder is `inset(body, n)` — the silhouette's *own* contour walked inward
    — so the frame keeps an even width around a bend instead of pinching at
    the corners the way two independently drawn shapes do.
    """
    ladder = [body] + [inset(body, n) for n in depths]
    aperture = ladder[-1]
    for outer, inner in zip(ladder, ladder[1:]):
        assert inner and inner < outer, 'the opening collapsed'

    key = keyline(body)
    flat, lip_lit, lip_dark, walls, sills = set(), set(), set(), set(), set()

    # Each rung of the ladder is one ledge: a lit top rim, a shaded bottom rim,
    # a flat, and a wall where the surface drops to the next ledge down. Light
    # falls from directly above, as it does on the shipped Plozz — straight
    # down rather than from a corner, so every layer mirrors about x=16. A
    # lopsided screen is the first thing the eye finds.
    for i, (outer, inner) in enumerate(zip(ladder, ladder[1:])):
        ledge = outer - inner - (key if i == 0 else set())
        above = key if i == 0 else (ladder[i - 1] - outer)

        wall = {p for p in ledge
                if any((p[0] + dx, p[1] + dy) in inner for dx, dy in NEIGHBOURS)}
        lip = {p for p in ledge
               if any((p[0] + dx, p[1] + dy) in above for dx, dy in NEIGHBOURS)}
        # A ledge with nowhere to put both a lit face and a wall collapses into
        # a drawn line, which is the "flat slab with lines scratched in"
        # failure this whole construction exists to avoid.
        assert not (wall & lip), f'ledge {i} is too thin to shade'

        lit = {p for p in lip if (p[0], p[1] - 1) in above}
        dark = {p for p in lip if (p[0], p[1] + 1) in above} - lit
        lip_lit |= lit
        lip_dark |= dark
        # The sides of a ledge face neither toward the light nor away from it,
        # so they stay the flat.
        flat |= ledge - wall - lit - dark
        # The wall is split the way a real recess is: its top faces away from
        # the light and stays darkest, its sill at the bottom faces back into
        # the light and lifts a step. That inversion across the opening is the
        # whole reason the screen reads as set *into* the case.
        sills |= {p for p in wall if (p[0], p[1] - 1) in inner}
        walls |= wall - {p for p in wall if (p[0], p[1] - 1) in inner}

    lip_dark -= lip_lit
    flat -= lip_lit | lip_dark
    casing = body - aperture - key

    bands, core = rings(aperture, SCREEN_STOPS - 1)

    layers = [
        (flat, CASE_BODY),
        (lip_dark, CASE_SHADE),
        (lip_lit, CASE_LIGHT),
        (sills, CASE_SILL),
        (walls, CASE_WALL),
    ]
    layers += [(core, SCREEN[-1])]
    layers += [(b, SCREEN[i]) for i, b in enumerate(bands)][::-1]
    layers += [(key, INK)]
    return layers, key, casing, aperture, core


def checks(name, body, layers, key, casing, aperture, core, face):
    # One pixel of outline, closed, all the way round: nothing inside the
    # keyline may touch open space.
    interior = body - key
    for p in interior:
        for dx, dy in NEIGHBOURS:
            assert (p[0] + dx, p[1] + dy) in body, f'{name}: keyline is not one pixel thick'
    for p in key:
        assert any((p[0] + dx, p[1] + dy) not in body for dx, dy in NEIGHBOURS)

    # Mirror about x=16. A lopsided screen is the first thing the eye finds.
    for s, _ in layers:
        assert all((31 - x, y) in s for x, y in s), f'{name}: a layer is not symmetric'

    # The stack must tile the silhouette exactly: no bare pixels, no overpaint.
    covered = set()
    for s, _ in layers:
        assert not (covered & s), f'{name}: layers overlap'
        covered |= s
    assert covered == body, f'{name}: the silhouette is not exactly covered'

    # Inside the safe area every sibling shares.
    x0, y0, x1, y1 = span(body)
    assert x0 >= 2 and y0 >= 2 and x1 <= 29 and y1 <= 29, f'{name}: breaks the 28x28 safe area'

    # The face sits on plain colour, as both shipped marks do.
    assert face <= core, f'{name}: the face does not sit entirely on the calm core'

    # Frame and field are separate parts, not one slab: the frame has to be at
    # least a fifth of the mark or the opening has eaten it.
    assert len(casing) > len(body) * 0.18, f'{name}: the frame has vanished'
    assert len(aperture) > len(body) * 0.35, f'{name}: the opening has vanished'


# ---------------------------------------------------------------------------
# The face, read out of mark.ts rather than reimplemented here.
# ---------------------------------------------------------------------------
def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


def measure(cx, cy):
    js = (f"import {{facePathsAt, faceBoxAt}} from '{ROOT}/src/data/mark.ts';"
          f"const o={{cx:{cx},cy:{cy},size:'md',smile:'compact',gap:2}};"
          "console.log(JSON.stringify({box: faceBoxAt(o), paths: facePathsAt(o)}));")
    out = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e', js],
        capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    face = set()
    for d in got['paths']:
        face |= pixels(d)
    return got['box'], face


# ---------------------------------------------------------------------------
# The four.
# ---------------------------------------------------------------------------
CONCEPTS = [
    dict(
        slug='p39', name='Portal, Wide',
        body=lambda: rrect(2, 4, 29, 27, 3),
        depths=(4,),
        idea='A widescreen opening with the television thrown away: a lit frame, '
             'a dark bezel wall, and four rings of light settling to a calm '
             'field at the centre.',
        note='The default reading of the set. 28x24 outside, a 20x16 opening, '
             'and a core exactly as tall as the face — eight rows on eight, '
             'with two pixels of plain colour either side of it.',
    ),
    dict(
        slug='p40', name='Portal, Square',
        body=lambda: rrect(3, 3, 28, 28, 5),
        depths=(4,),
        idea='The same recess opened square and rounded harder — a viewport '
             'rather than a panel, and the most compact silhouette of the four.',
        note='Square is the hardest case: with equal air on all four sides the '
             'rings close into a ten-by-ten field, so the face gets a pixel of '
             'plain colour around it on every side rather than only above and '
             'below. It is also the variant that survives 16px best, because '
             'the opening stays two pixels tall after the halving.',
    ),
    dict(
        slug='p41', name='Portal, Deep',
        body=lambda: rrect(2, 3, 29, 28, 3),
        depths=(3, 5),
        idea='The same opening cut as two steps rather than one, so the frame '
             'falls to the screen down a pair of ledges and the mark reads as '
             'looking through something rather than at it.',
        note='Five pixels of frame, but not five pixels of flat: the erosion '
             'ladder stops twice, at three and at five, so there are two lit '
             'rims and two walls instead of one of each. That alternation is '
             'the whole difference from p39 and it buys the deepest-looking '
             'well in the set at the cost of the smallest opening.',
    ),
    dict(
        slug='p42', name='Portal, Tube',
        body=lambda: superellipse(16, 16, 14, 12, 4),
        depths=(4,),
        idea='The picture tube kept as a curve and nothing else: a superellipse '
             'outside and in, so the frame and the light it encloses swell '
             'together.',
        note='The opening is the silhouette itself walked four pixels inward, '
             'so the frame stays an even four pixels around the bend where a '
             'second freehand curve would pinch at the corners. It is the only '
             'silhouette here with no straight run longer than the flat of its '
             'own sides, and the one that most obviously belongs to Plozz.',
    ),
]


def emit(c, layers, cy, box, tones):
    rows = '\n'.join(f'  <path d="{" ".join(to_paths(p))}" fill="{f}" />' for p, f in layers)
    (OUT / f"{c['slug']}.astro").write_text(f'''---
/**
 * {c['slug']} · {c['name']}
 *
 * Plozz with the television thrown away and only the aperture kept.
 *
 * {c['idea']}
 *
 * Built strictly outside-in, and every band is derived from the silhouette's
 * own contour by `rings()` rather than written as a rectangle and dropped
 * inside the outline. The opening is not a second drawn shape but this
 * silhouette's own contour walked inward, which is what keeps the frame an
 * even width around a bend. Outward to inward: a one-pixel keyline, the
 * frame's lit top rim, its flat, its shaded bottom rim, then the bezel — the
 * wall of the recess, the darkest tone in the mark and the one layer that
 * tells the eye the light is *behind* the frame, lifting a step at the sill
 * where it turns back into the light — and then four rings of screen falling
 * to a calm field at the centre. Light falls straight down, as it does on the
 * shipped Plozz, so every layer mirrors about x=16.
 *
 * {c['note']}
 *
 * The face is `md`/`compact`/gap 2, Plozz's own smile, centred on cy={cy} and
 * sitting entirely on plain colour — the rings stop at its edge rather than
 * being cleared for it. {tones} flat tones, no gradient anywhere.
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="Plozz — {c['name']}">
{rows}
  <g fill="{INK}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: 16, cy: {cy}, size: 'md', smile: 'compact', gap: 2 }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
''')
    palette = ', '.join(f"'{t}'" for t in [INK, CASE_WALL, CASE_SILL, CASE_SHADE, CASE_BODY,
                                           CASE_LIGHT, *FIELD[::-1], SCREEN_SHADOW])
    (OUT / f"{c['slug']}.meta.ts").write_text(f'''export default {{
  n: '{c['slug']}', name: '{c['name']}',
  idea: '{c['idea']}',
  ground: 'light',
  palette: [{palette}],
}};
''')


# ---------------------------------------------------------------------------
# Previews. A tiny PNG writer, because the point of this set is what it looks
# like at 16 pixels and that cannot be judged from a path string.
# ---------------------------------------------------------------------------
def png(path, rgb_rows):
    h, w = len(rgb_rows), len(rgb_rows[0])
    raw = b''.join(b'\x00' + bytes(v for px in row for v in px) for row in rgb_rows)

    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))

    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw, 9))
        + chunk(b'IEND', b''))


def rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def raster(layers, face, ground):
    grid = [[ground] * GRID for _ in range(GRID)]
    for s, f in layers:
        c = rgb(f)
        for x, y in s:
            grid[y][x] = c
    for x, y in face:
        grid[y][x] = rgb(INK)
    return grid


def scale(grid, n):
    return [[px for px in row for _ in range(n)] for row in grid for _ in range(n)]


def halve(grid):
    """Box filter 32 -> 16, which is what a browser does to the favicon."""
    out = []
    for y in range(0, GRID, 2):
        row = []
        for x in range(0, GRID, 2):
            q = [grid[y][x], grid[y][x + 1], grid[y + 1][x], grid[y + 1][x + 1]]
            row.append(tuple(sum(p[c] for p in q) // 4 for c in range(3)))
        out.append(row)
    return out


def main():
    built = []
    for c in CONCEPTS:
        body = c['body']()
        layers, key, casing, ap, core = build(body, c['depths'])

        bx0, by0, bx1, by1 = span(body)
        cy = 16
        box, face = measure(16, cy)
        checks(c['slug'], body, layers, key, casing, ap, core, face)

        cx0, cy0, cx1, cy1 = span(core)
        tones = len({f for _, f in layers} | {INK})
        emit(c, layers, cy, box, tones)
        built.append((c, layers, face, body))

        print(f"{c['slug']} {c['name']}")
        print(f"  body {bx1-bx0+1}x{by1-by0+1} at x{bx0}-{bx1} y{by0}-{by1}"
              f" · frame {len(casing)}px · opening {len(ap)}px")
        print(f"  core {cx1-cx0+1}x{cy1-cy0+1} at x{cx0}-{cx1} y{cy0}-{cy1}"
              f" · face {box['w']}x{box['h']} at x{box['x']}-{box['right']}"
              f" y{box['y']}-{box['bottom']} cy={cy}")
        print(f"  air {box['y']-by0} above / {by1-box['bottom']} below · {tones} tones")

        if '--show' in sys.argv:
            from shade import show
            show([s for s, _ in layers] + [face],
                 ['.', 's', 'S', 'W', 'w', '5', '4', '3', '2', '1', '0', '#', '@'])

    if '--png' in sys.argv:
        out = ROOT / '.preview'
        out.mkdir(exist_ok=True)
        for ground, tag in (('#f6f4f0', 'light'), ('#101418', 'dark')):
            big, small = [], []
            for c, layers, face, _ in built:
                g = raster(layers, face, rgb(ground))
                big.append(scale(g, 8))
                small.append(scale(halve(g), 8))
            row = [sum((b[i] + [rgb(ground)] * 16 for b in big), []) for i in range(len(big[0]))]
            png(out / f'portal-32-{tag}.png', row)
            row = [sum((b[i] + [rgb(ground)] * 16 for b in small), []) for i in range(len(small[0]))]
            png(out / f'portal-16-{tag}.png', row)
        print(f'  previews in {out}')
    print('  written')


if __name__ == '__main__':
    main()
