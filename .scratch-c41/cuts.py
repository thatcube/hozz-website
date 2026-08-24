"""Isotropic uniform vs isotropic accelerating: band widths and a big render."""
import importlib.util
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r', ROOT / '.scratch-c41/render.py')
r = importlib.util.module_from_spec(spec)
sys.modules['r'] = r
spec.loader.exec_module(r)

D = r.depth_field(r.INNER, 1.0)


def widths(cuts, row):
    t = r.bands(D, cuts)
    seq = [t[(x, row)] for x in range(32) if (x, row) in t]
    runs = []
    for v in seq:
        if runs and runs[-1][0] == v:
            runs[-1][1] += 1
        else:
            runs.append([v, 1])
    return runs


for label, cuts in (('uniform 1px', [k + 1.5 for k in range(6)]),
                    ('accelerating (quantile)', r.quantile_cuts(D, 7)),
                    ('rim-weighted', [1.5, 2.5, 3.5, 5.5, 7.5, 9.5])):
    print(f'{label}: cuts {[round(c, 2) for c in cuts]}')
    print('   row 13 runs (tone x width):',
          ' '.join(f'{v}x{n}' for v, n in widths(cuts, 13)))
    print('   col 16 down:', ' '.join(
        str(r.bands(D, cuts)[(16, y)]) for y in range(32) if (16, y) in D))

W = 208
PICKS = [('uniform', [k + 1.5 for k in range(6)]),
         ('accelerating', r.quantile_cuts(D, 7)),
         ('rim-weighted', [1.5, 2.5, 3.5, 5.5, 7.5, 9.5])]
sheet = Image.new('RGB', (len(PICKS) * W, W + 56), '#f4f4f6')
for i, (name, cuts) in enumerate(PICKS):
    t = r.bands(D, cuts)
    img = Image.new('RGB', (32, 32), '#ffffff')
    px = img.load()

    def put(s, c):
        c = tuple(int(c[j:j + 2], 16) for j in (1, 3, 5))
        for x, y in s:
            px[x, y] = c
    put(r.WATER_OUT, '#96bcd6')
    put(r.WATER_IN, '#5d8cb0')
    for k, col in enumerate(r.RAMP):
        put({p for p, v in t.items() if v == k}, col)
    put(r.KEYRING, r.KEY)
    put(r.FACE, r.KEY)
    sheet.paste(img.resize((192, 192), Image.NEAREST), (i * W + 8, 8))
    sheet.paste(img.resize((24, 24), Image.LANCZOS).resize((48, 48), Image.NEAREST),
                (i * W + 80, 204))
sheet.save(ROOT / '.scratch-c41/cuts.png')
print('wrote cuts.png')
