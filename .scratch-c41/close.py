"""Blow up three candidates plus a flat control for a close look."""
import importlib.util
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r', ROOT / '.scratch-c41/render.py')
r = importlib.util.module_from_spec(spec)
sys.modules['r'] = r
spec.loader.exec_module(r)

PICKS = [('flat control', None, None), ('A iso 1px', 1.00, 'u'),
         ('B wide 1px', 0.72, 'u'), ('C tall 1px', 1.35, 'u'),
         ('E wide quant', 0.78, 'q')]

W = 208
sheet = Image.new('RGB', (len(PICKS) * W, W), '#f4f4f6')
for i, (name, ky, mode) in enumerate(PICKS):
    if ky is None:
        img = Image.new('RGB', (32, 32), '#ffffff')
        px = img.load()

        def put(s, c):
            c = tuple(int(c[j:j + 2], 16) for j in (1, 3, 5))
            for x, y in s:
                px[x, y] = c
        put(r.WATER_OUT, '#96bcd6')
        put(r.WATER_IN, '#5d8cb0')
        put(r.INNER, '#cfe3ef')
        put(r.KEYRING, r.KEY)
        put(r.FACE, r.KEY)
    else:
        img, _ = r.render(ky, mode)
    sheet.paste(img.resize((192, 192), Image.NEAREST), (i * W + 8, 8))
sheet.save(ROOT / '.scratch-c41/close.png')
print('wrote close.png ·', ', '.join(p[0] for p in PICKS))
