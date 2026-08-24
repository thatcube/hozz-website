"""Probe: rounded-rect bodies and tails, printed as ASCII, before committing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from circles import check  # noqa: E402
from shade import rings, keyline  # noqa: E402


def body(x0, x1, y0, y1, r):
    """Rounded rectangle by pixel-centre distance — round corners, no chamfer."""
    out = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cx = min(max(x + 0.5, x0 + r), x1 + 1 - r)
            cy = min(max(y + 0.5, y0 + r), y1 + 1 - r)
            if ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5 <= r:
                out.add((x, y))
    return out


for r in (5, 6, 6.5, 7, 7.5, 8):
    B = body(2, 29, 2, 23, r)
    rows = {}
    for x, y in B:
        rows.setdefault(y, []).append(x)
    w = [max(rows[y]) - min(rows[y]) + 1 for y in sorted(rows)]
    try:
        check(B)
        ok = 'clean'
    except AssertionError as e:
        ok = f'FAIL {e}'
    bands, core = rings(B - keyline(B), 5)
    cxs = sorted({p[0] for p in core})
    cys = sorted({p[1] for p in core})
    print(f'r={r}: widths {w}  {ok}')
    print(f'      core {len(core)}px x{cxs[0]}-{cxs[-1]} y{cys[0]}-{cys[-1]}  '
          f'bands {[len(b) for b in bands]}')
    bottom = sorted(rows)[-1]
    print(f'      bottom row x{min(rows[bottom])}-{max(rows[bottom])}')
