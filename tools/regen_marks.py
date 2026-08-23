"""
Regenerate the marks Brandon flagged as flat or broken.

Two complaints, both fair:

  1. The shading went flat. Measured against the shipped marks, Plozz carries
     eight tones and Mozz eleven; several of these had collapsed to two or
     three, and a few had a shade layer authored as a rectangle and dropped
     inside the outline, which reads as a block pasted on.
  2. The hearts lost the smile. An earlier pass decided a heart could not carry
     one and shipped eyes alone. Two Zs with no mouth read as asleep, so that
     was the wrong trade — the shape had to change instead.

Everything here derives its shading from the silhouette via tools/shade.py, so
a slab cannot be produced by construction.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from shade import rings, edge, crescent, keyline, clear, to_paths, is_slab  # noqa: E402

OUT = ROOT / 'src/components/mark/logos'


# ---------------------------------------------------------------- primitives
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def rrect(x0, y0, x1, y1, r):
    s = rect(x0, y0, x1, y1)
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        for dx in range(r):
            for dy in range(r):
                if dx + dy < r - 1:
                    px = cx + dx if cx == x0 else cx - dx
                    py = cy + dy if cy == y0 else cy - dy
                    s.discard((px, py))
    return s


def centroid(s):
    return (sum(p[0] for p in s) / len(s) + 0.5,
            sum(p[1] for p in s) / len(s) + 0.5)


# --------------------------------------------------------------- the heart
# Rounder, per Brandon: it ends on a four-pixel flat instead of a point, and
# the notch between the lobes is two rows deep with the lobes rounded over
# rather than peaked.
HEART_SPAN = {
    4: [(9, 13), (18, 22)],
    5: [(7, 14), (17, 24)],
    6: [(6, 25)],
    7: [(5, 26)],
    8: [(4, 27)], 9: [(4, 27)], 10: [(4, 27)], 11: [(4, 27)],
    12: [(4, 27)], 13: [(4, 27)], 14: [(4, 27)], 15: [(4, 27)],
    16: [(5, 26)], 17: [(5, 26)],
    18: [(6, 25)], 19: [(7, 24)], 20: [(8, 23)], 21: [(9, 22)],
    22: [(10, 21)], 23: [(11, 20)], 24: [(12, 19)], 25: [(13, 18)],
    26: [(14, 17)],
}


def heart():
    s = set()
    for y, runs in HEART_SPAN.items():
        for a, b in runs:
            s |= {(x, y) for x in range(a, b + 1)}
    return s


def path_el(pixels, fill):
    return f'  <path d="{" ".join(to_paths(pixels))}" fill="{fill}" />'


def write(slug, title, doc, layers, face, meta):
    """Emit one mark. `layers` is [(pixels, fill)] painted in order, or
    [(pixels, fill, 'field')] to mark the plain area the face sits on.

    A large plain field is correct — Plozz's screen is one — so only the
    shading layers are checked for being rectangles pasted inside the outline.
    """
    body = set().union(*[layer[0] for layer in layers])
    for layer in layers:
        pixels, fill = layer[0], layer[1]
        role = layer[2] if len(layer) > 2 else 'shade'
        if role != 'field' and is_slab(pixels, body):
            raise SystemExit(f'{slug}: {fill} is a buried slab — rebuild it from the contour')

    cx, cy, size, smile, fcol = face
    rows = '\n'.join(path_el(layer[0], layer[1]) for layer in layers)
    src = f'''---
/**
{doc}
 */
import MarkFrame from '../MarkFrame.astro';
import {{ facePathsAt }} from '../../../data/mark';

interface Props {{ size?: number }}
const {{ size = 128 }} = Astro.props;
---

<MarkFrame size={{size}} title="{title}">
{rows}
  <g fill="{fcol}" shape-rendering="crispEdges">
    {{facePathsAt({{ cx: {cx}, cy: {cy}, size: '{size}', smile: '{smile}' }}).map((d) => (
      <path d={{d}} />
    ))}}
  </g>
</MarkFrame>
'''
    (OUT / f'{slug}.astro').write_text(src)
    (OUT / f'{slug}.meta.ts').write_text(meta)
    return body


# ------------------------------------------------------------------ hearts
HEART_COLOURS = {
    'c26': ('Coral Heart', 'coral, kept well off Mozz’s red',
            dict(deep='#8f2f22', key='#5e1f14', shade='#c9503a', field='#ef7e64', lit='#f7a894', face='#5e1f14')),
    'c27': ('Sage Heart', 'a planted green rather than an alarm colour',
            dict(deep='#3d5a34', key='#20301c', shade='#5f8455', field='#93b177', lit='#b6cf9c', face='#20301c')),
    'c28': ('Tide Heart', 'a green-leaning teal, clear of Plozz’s cyan',
            dict(deep='#175753', key='#0b2f2d', shade='#2c7d78', field='#4fa89c', lit='#7eccbf', face='#0b2f2d')),
    'c29': ('Oat Heart', 'oat and clay, the heart drained of symbolism',
            dict(deep='#7d5c3e', key='#463222', shade='#ac8663', field='#dcb692', lit='#f0d6ba', face='#463222')),
    'c30': ('Plum Heart', 'wine plum with a pale face, the way Mozz carries its own',
            dict(deep='#3f1a2c', key='#2e1220', shade='#5c2740', field='#8f4361', lit='#b96d89', face='#f3dbe2')),
}


def build_hearts():
    shape = heart()
    k = keyline(shape)
    inner = shape - k
    # Two steps of shade, not one: a deep rim right at the edge and a broader
    # band inside it. One step is what made these read flat.
    deep = crescent(inner, -1, -1)
    sh = crescent(inner, -3, -3) - deep
    lit = (edge(inner, 0, -1, 1) | edge(inner, -1, 0, 1)) - sh - deep
    field = clear(inner, sh, deep, lit)

    cx, cyf = centroid(shape)
    # The face sits on the shape's own centre of mass, which on a heart is well
    # above the middle of the box.
    cy = round(cyf) - 1

    for slug, (name, why, col) in HEART_COLOURS.items():
        doc = f''' * {slug[1:]} · {name}
 *
 * {why[0].upper() + why[1:]}. Rounder than the first attempt at Brandon's
 * asking: it ends on a four-pixel flat rather than a point, and the notch
 * between the lobes is two rows deep with the lobes rounded over.
 *
 * It carries the smile again. The earlier pass dropped it and called the
 * shape the reason, but two Zs with no mouth read as asleep — so the shape
 * gave way instead, not the face.
 *
 * Four tones, all derived from the silhouette: a keyline, a lit rim along the
 * top and left, a crescent of shade falling to the lower right, and a plain
 * field for the face.'''
        layers = [(deep, col['deep']), (sh, col['shade']),
                  (field, col['field'], 'field'), (lit, col['lit']), (k, col['key'])]
        meta = f'''export default {{
  n: '{slug[1:]}', name: '{name}',
  idea: 'A rounder heart — blunt at the tip, shallow in the cleft — carrying the full face, not just the eyes.',
  ground: 'light',
  palette: ['{col['key']}', '{col['deep']}', '{col['shade']}', '{col['field']}', '{col['lit']}'],
}};
'''
        write(slug, f'Hozz — {name}', doc, layers,
              (16, cy, 'md', 'wide', col['face']), meta)
    print(f'hearts: face at (16,{cy}), shape y{min(p[1] for p in shape)}-{max(p[1] for p in shape)}')


# --------------------------------------------------------------------- jar
def build_jar():
    # A wide lid sitting straight on the shoulder — no neck. The neck was
    # what made it read as a potion bottle rather than a preserve jar.
    lid = rrect(8, 3, 23, 9, 1)
    glass = rrect(5, 10, 26, 28, 3)

    gk = keyline(glass)
    gr, core = rings(glass - gk, 2)
    rim_lit, rim_mid = gr[0], gr[1]

    lk = keyline(lid)
    li = lid - lk
    ltop = edge(li, 0, -1, 1)
    lbot = edge(li, 0, 1, 1) - ltop
    lmid = clear(li, ltop, lbot)

    doc = ''' * 12 · Preserve Jar
 *
 * Rebuilt to the shipped grammar after it went flat. Plozz carries eight tones
 * and does it with a nested inward bevel — a black keyline, then a lighter ring,
 * then a light one, then the plain field the face sits on. This does the same,
 * and the lid gets its own volume from a lit top edge and a shaded base.
 *
 * Every layer is derived from the silhouette rather than drawn as a rectangle,
 * so the bevel bends around the corners instead of sitting inside them.'''

    layers = [(core, '#cde2bd', 'field'), (rim_mid, '#dcecc9'), (rim_lit, '#eff4d2'),
              (gk, '#31544b'), (lmid, '#b59b6a'), (ltop, '#d3bb8e'),
              (lbot, '#8d7247'), (lk, '#31544b')]

    meta = '''export default {
  n: '12', name: 'Preserve Jar',
  idea: 'A jar with real glass to it — a nested bevel catching light at the rim, the way the shipped marks do it.',
  ground: 'light',
  palette: ['#31544b', '#8d7247', '#b59b6a', '#cde2bd', '#eff4d2'],
};
'''
    body = write('c12', 'Hozz — Preserve Jar', doc, layers,
                 (16, 20, 'md', 'wide', '#31544b'), meta)
    print(f'jar: {len(layers)} tones, field {len(core)}px')
    return body


build_hearts()
build_jar()
print('done')
