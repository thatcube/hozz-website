"""
Canonical circles, lifted from the shipped marks.

Rasterising `x² + y² ≤ r²` gives a different-looking circle for every radius,
and most of them are wrong. At 22 across, r=11.5 comes out visibly octagonal;
at other centres it grows single pixels standing off the sides. Several rounds
of this project shipped marks with exactly those defects.

So rather than let anyone pick a radius, this module carries the profile of the
disc from the shipped **Mozz** mark — a 28-across circle that is known good
because it is on the App Store — plus smaller circles derived to match its
character: the same pattern of doubled rows and the same two- and four-pixel
steps at the shoulders.

Use `circle(28)`, `circle(24)`, `circle(22)` or `circle(20)`. They are centred
on x=16.0 exactly, so column x and column 31-x mirror by construction.
"""

# (row width) top to bottom. Mozz's own profile, read off the shipped SVG.
MOZZ_28 = [8, 12, 16, 18, 20, 22, 24, 24, 26, 26,
           28, 28, 28, 28, 28, 28, 28, 28,
           26, 26, 24, 24, 22, 20, 18, 16, 12, 8]

# Smaller circles in the same idiom: shoulders that step 4, 4, 2, 2, then hold.
CIRCLE_24 = [8, 12, 14, 16, 18, 20, 20, 22, 22,
             24, 24, 24, 24, 24, 24,
             22, 22, 20, 20, 18, 16, 14, 12, 8]

CIRCLE_22 = [6, 10, 14, 16, 18, 18, 20, 20,
             22, 22, 22, 22, 22, 22,
             20, 20, 18, 18, 16, 14, 10, 6]

CIRCLE_20 = [6, 10, 12, 14, 16, 16, 18, 18,
             20, 20, 20, 20,
             18, 18, 16, 16, 14, 12, 10, 6]

PROFILES = {28: MOZZ_28, 24: CIRCLE_24, 22: CIRCLE_22, 20: CIRCLE_20}


def circle(size, top=2):
    """A pixel circle of `size` across, its first row at `top`.

    Returns a set of (x, y). Symmetric about x=16 by construction, and free of
    the spurs and flat corners that come out of a naive radius test.
    """
    if size not in PROFILES:
        raise ValueError(f'no canonical circle at {size} across; have {sorted(PROFILES)}')
    out = set()
    for i, w in enumerate(PROFILES[size]):
        x0 = 16 - w // 2
        out |= {(x0 + k, top + i) for k in range(w)}
    return out


def check(shape):
    """Assert a silhouette is symmetric and free of spurs.

    A spur is a row wider than both its neighbours — it reads as a pixel
    sticking out of the side, and it is the defect that got two marks rejected.
    """
    rows = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    ys = sorted(rows)
    widths = [max(rows[y]) - min(rows[y]) + 1 for y in ys]
    for i in range(1, len(widths) - 1):
        if widths[i] > widths[i - 1] and widths[i] > widths[i + 1]:
            raise AssertionError(f'spur at row {ys[i]}: {widths[i]} vs '
                                 f'{widths[i - 1]}/{widths[i + 1]}')
    for x, y in shape:
        if (31 - x, y) not in shape:
            raise AssertionError(f'not symmetric about x=16 at ({x}, {y})')
    return widths


if __name__ == '__main__':
    for size in sorted(PROFILES, reverse=True):
        s = circle(size)
        w = check(s)
        ys = sorted({p[1] for p in s})
        print(f'{size} across, y{ys[0]}-{ys[-1]} ({len(ys)} tall) — clean')
