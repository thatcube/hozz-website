"""
Shading that follows a silhouette.

Every one of these takes a set of (x, y) pixels and returns another set derived
from it, so the result can only ever follow the shape's own contour. That is the
whole point: the marks that went wrong did so because a shade layer was written
as a rectangle and dropped inside the outline, which reads as a block pasted on
rather than as light falling across a form.

Measured off the two shipped marks, which are the standard:

  Plozz  8 tones.  Black keyline around the outside, a two-pixel case in the
                   mid tone with a lighter band along the top edge and a darker
                   one along the bottom, then a black bezel, then a *nested
                   inward bevel* — lightest ring, light ring, field.
  Mozz  11 tones.  A very dark keyline (a near-black of the hue, not pure
                   black), then broad directional banding: light upper-left
                   falling to dark lower-right across the whole disc.

Both keep the field under the face plain. The detail lives in the container.
"""

NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def rings(body, n=1):
    """Peel `n` successive contour-following rings off the outside of a shape.

    Returns `(list_of_rings, core)`. Ring 0 is the outermost pixel band, ring 1
    sits just inside it, and so on. Because each ring is defined by which pixels
    have a missing neighbour, a ring bends around every curve and corner of the
    silhouette — a rectangle cannot come out of this.
    """
    out = []
    cur = set(body)
    for _ in range(n):
        r = {p for p in cur
             if any((p[0] + dx, p[1] + dy) not in cur for dx, dy in NEIGHBOURS)}
        out.append(r)
        cur = cur - r
    return out, cur


def edge(body, dx, dy, depth=1):
    """The band along one side of a shape — the side facing (dx, dy).

    `edge(body, 0, -1)` is the top edge, `edge(body, 1, 1)` the bottom-right.
    Use it for directional light: a lit band along the top, a shaded one along
    the bottom, both hugging the contour.
    """
    band = set()
    cur = set(body)
    for d in range(depth):
        layer = {p for p in cur
                 if (p[0] + dx * (d + 1), p[1] + dy * (d + 1)) not in body}
        band |= layer
    return band & set(body)


def crescent(body, dx=-2, dy=-2):
    """The shaded rim left behind when the form is lit from (dx, dy).

    Shift the shape toward the light and keep whatever the shift uncovers. This
    is the cheapest honest shade for a round object and it is exactly how a
    crescent on a disc should be built — never as a band plus an edge strip,
    which is what made one earlier mark read as a square inside a circle.
    """
    lit = {(x + dx, y + dy) for (x, y) in body}
    return set(body) - lit


def inset(body, n):
    """The shape eroded inward by `n` pixels — the field a bevel encloses."""
    _, core = rings(body, n)
    return core


def keyline(body):
    """The outermost ring, for the dark line every shipped mark carries."""
    r, _ = rings(body, 1)
    return r[0]


def clear(body, *taken):
    """Whatever is left of a shape once the named layers have claimed their
    pixels. Use it for the plain field the face sits on."""
    out = set(body)
    for t in taken:
        out -= t
    return out


def bbox(s):
    xs = [p[0] for p in s]
    ys = [p[1] for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def is_slab(layer, body, margin=2):
    """True when a layer is a filled rectangle *floating* inside the shape.

    This is the failure mode to avoid: a block dropped into the middle of a
    mark rather than derived from its contour.

    A filled rectangle is not automatically wrong. A band across a small part —
    the lit top of a lid, the mid tone of Plozz's case — is enclosed by its own
    keyline and is exactly right. What makes a slab read as pasted on is
    *floating*: clear space on all four sides, so nothing anchors it to the
    form. So the test is margin, not enclosure.
    """
    if len(layer) < 9:
        return False
    x0, y0, x1, y1 = bbox(layer)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w < 3 or h < 3:
        return False
    if len(layer) / (w * h) <= 0.92:
        return False
    rows = {}
    cols = {}
    for x, y in body:
        rows.setdefault(y, []).append(x)
        cols.setdefault(x, []).append(y)
    # Anchored if the shape runs out within `margin` on any side.
    for y in range(y0, y1 + 1):
        if y not in rows:
            return False
        if min(rows[y]) > x0 - margin or max(rows[y]) < x1 + margin:
            return False
    for x in range(x0, x1 + 1):
        if x not in cols:
            return False
        if min(cols[x]) > y0 - margin or max(cols[x]) < y1 + margin:
            return False
    return True


def to_paths(s):
    """Collapse a pixel set into horizontal-run SVG path strings."""
    rows = {}
    for x, y in s:
        rows.setdefault(y, []).append(x)
    out = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x != prev + 1:
                out.append(f'M{start} {y}h{prev - start + 1}v1h-{prev - start + 1}z')
                start = x
            prev = x if x is not None else prev
    return out


def show(layers, marks, grid=32):
    """Print overlaid layers as text, later layers winning, for eyeballing."""
    ys = sorted({y for s in layers for (_, y) in s})
    print('    ' + ''.join(str(i % 10) for i in range(grid)))
    for y in range(min(ys), max(ys) + 1):
        line = ''
        for x in range(grid):
            ch = ' '
            for s, m in zip(layers, marks):
                if (x, y) in s:
                    ch = m
            line += ch
        print(f'{y:3} ' + line)
