"""How many tones? Same span, same 1px bands, 6/7/8/9 steps."""
import importlib.util
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r', ROOT / '.scratch-c41/render.py')
r = importlib.util.module_from_spec(spec)
sys.modules['r'] = r
spec.loader.exec_module(r)

spec2 = importlib.util.spec_from_file_location('ramp', ROOT / '.scratch-c41/ramp.py')

# reuse the Oklab helpers without re-running its prints
src = (ROOT / '.scratch-c41/ramp.py').read_text().split("print('Plozz")[0]
ns = {}
exec(src, ns)  # noqa: S102
mkramp, de = ns['ramp'], ns['de']

D = r.depth_field(r.INNER, 1.0)
A, B = '#f2f9fd', '#a9cfe8'
W = 208
PICKS = [6, 7, 8, 9]
sheet = Image.new('RGB', (len(PICKS) * W, W + 56), '#f4f4f6')
for i, n in enumerate(PICKS):
    cols = mkramp(A, B, n)
    steps = [de(x, y) for x, y in zip(cols, cols[1:])]
    t = r.bands(D, [k + 1.5 for k in range(n - 1)])
    used = sorted(set(t.values()))
    print(f'{n} tones  step dE {min(steps):.4f}-{max(steps):.4f}  '
          f'(Plozz 0.0186-0.0257)  tones actually used {len(used)}')
    print('   ', ' '.join(cols))
    img = Image.new('RGB', (32, 32), '#ffffff')
    px = img.load()

    def put(s, c):
        c = tuple(int(c[j:j + 2], 16) for j in (1, 3, 5))
        for x, y in s:
            px[x, y] = c
    put(r.WATER_OUT, '#96bcd6')
    put(r.WATER_IN, '#5d8cb0')
    for k, col in enumerate(cols):
        put({p for p, v in t.items() if v == k}, col)
    put(r.KEYRING, r.KEY)
    put(r.FACE, r.KEY)
    sheet.paste(img.resize((192, 192), Image.NEAREST), (i * W + 8, 8))
    sheet.paste(img.resize((24, 24), Image.LANCZOS).resize((48, 48), Image.NEAREST),
                (i * W + 80, 204))
sheet.save(ROOT / '.scratch-c41/tones.png')
print('wrote tones.png')
