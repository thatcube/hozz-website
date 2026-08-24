"""Python mirror of facePathsAt from src/data/mark.ts, for offline previews only.

Read-only reimplementation so a preview can be rasterised without a browser.
The shipped face always comes from mark.ts; this is never used to draw one.
"""

EYES_LG = [[(0, 3), (6, 9)], [(2, 3), (8, 9)], [(1, 2), (7, 8)],
           [(0, 1), (6, 7)], [(0, 3), (6, 9)]]
EYES_SM = [[(0, 2)], [(1, 2)], [(0, 1)], [(0, 2)]]

SMILE_WIDE = [[(0, 0), (9, 9)], [(0, 1), (8, 9)], [(1, 8)], [(2, 7)]]
SMILE_COMPACT = [[(1, 1), (8, 8)], [(1, 2), (7, 8)], [(2, 7)]]
SMILE_SMALL = [[(1, 1), (8, 8)], [(2, 7)]]
SM_WIDE = [[(0, 0), (7, 7)], [(0, 1), (6, 7)], [(1, 6)]]
SM_COMPACT = [[(1, 1), (6, 6)], [(2, 5)]]
XS_WIDE = [[(0, 0), (6, 6)], [(1, 5)]]

SPECS = {
    'lg': dict(eyes=EYES_LG, w=10, gap=2,
               smiles=dict(wide=SMILE_WIDE, compact=SMILE_COMPACT, small=SMILE_SMALL)),
    'md': dict(eyes=EYES_SM, w=8, gap=2, smiles=dict(wide=SM_WIDE, compact=SM_COMPACT)),
    'sm': dict(eyes=EYES_SM, w=7, gap=1, smiles=dict(wide=XS_WIDE, compact=XS_WIDE)),
}


def _round(v):
    """JS Math.round: halves go up."""
    import math
    return math.floor(v + 0.5)


def rows(size, smile, gap):
    sp = SPECS[size]
    if size == 'lg':
        eyes = sp['eyes']
    else:
        off = sp['w'] - 3
        eyes = [[(a, b) for a, b in r] + [(a + off, b + off) for a, b in r]
                for r in sp['eyes']]
    if smile == 'none':
        return eyes
    sm = sp['smiles'].get(smile) or sp['smiles']['wide']
    return eyes + [[] for _ in range(gap)] + sm


def face_paths(cx=16, cy=16, size='md', smile='wide', gap=None):
    sp = SPECS[size]
    gap = sp['gap'] if gap is None else gap
    rs = rows(size, smile, gap)
    top = _round(cy - len(rs) / 2)
    left = _round(cx - sp['w'] / 2)
    out = []
    for i, runs in enumerate(rs):
        for a, b in runs:
            w = b - a + 1
            out.append(f'M{left + a} {top + i}h{w}v1h-{w}z')
    return out


def face_box(cx=16, cy=16, size='md', smile='wide', gap=None):
    sp = SPECS[size]
    gap = sp['gap'] if gap is None else gap
    rs = rows(size, smile, gap)
    top = _round(cy - len(rs) / 2)
    left = _round(cx - sp['w'] / 2)
    return dict(x=left, y=top, w=sp['w'], h=len(rs))
