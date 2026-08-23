"""Measure existing marks: silhouette row profile, extent jumps, count jumps."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'src/components/mark/logos'


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


def body_of(slug):
    src = (OUT / f'{slug}.astro').read_text()
    s = set()
    for d in re.findall(r'<path d="([^"]+)"', src):
        s |= pixels(d)
    return s


def profile(body):
    rows = {}
    for x, y in body:
        rows.setdefault(y, []).append(x)
    out = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        out.append((y, min(xs), max(xs), max(xs) - min(xs) + 1, len(xs)))
    return out


for slug in sys.argv[1:]:
    b = body_of(slug)
    p = profile(b)
    sym = all((31 - x, y) in b for x, y in b)
    ext_bad, cnt_bad = [], []
    for i in range(1, len(p)):
        if p[i][0] != p[i - 1][0] + 1:
            continue
        if p[i][3] - p[i - 1][3] > 2:
            ext_bad.append((p[i][0], p[i - 1][3], p[i][3]))
        if p[i][4] - p[i - 1][4] > 2:
            cnt_bad.append((p[i][0], p[i - 1][4], p[i][4]))
    print(f'{slug}: sym={sym} rows y{p[0][0]}..{p[-1][0]} widths={[r[3] for r in p]}')
    print(f'   extent jumps>2: {ext_bad}')
    print(f'   count  jumps>2: {cnt_bad}')
