"""Rasterise the shipped Plozz mark to a 32x32 grid and measure its edge ramp."""
import io
import os
from collections import Counter

import cairosvg
from PIL import Image

REF = os.path.expanduser('~/hozzshots/ref/plozz.svg')
S = 10  # supersample, then read the centre of every cell

png = cairosvg.svg2png(url=REF, output_width=32 * S, output_height=32 * S)
im = Image.open(io.BytesIO(png)).convert('RGBA')

grid = []
for y in range(32):
    row = []
    for x in range(32):
        r, g, b, a = im.getpixel((x * S + S // 2, y * S + S // 2))
        row.append(None if a < 128 else (r, g, b))
    grid.append(row)

counts = Counter(c for row in grid for c in row if c)
palette = [c for c, _ in counts.most_common()]
sym = {c: (chr(ord('a') + i) if i > 9 else str(i)) for i, c in enumerate(palette)}

print('tones present (32x32 raster):', len(palette))
for c, n in counts.most_common():
    print(f'  {sym[c]}  #{c[0]:02x}{c[1]:02x}{c[2]:02x}  {n:4d} px')

print()
print('    ' + ''.join(str(i % 10) for i in range(32)))
for y in range(32):
    print(f'{y:3} ' + ''.join(sym[c] if c else '.' for c in grid[y]))

# --- the screen: the region bounded by the black bezel -------------------
SCREEN = {'#97e3fe', '#82deff', '#72daff'}


def hx(c):
    return f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}'


print()
print('screen rows (only the ramp tones), with run lengths:')
for y in range(32):
    cells = [(x, hx(c)) for x, c in enumerate(grid[y]) if c and hx(c) in SCREEN]
    if not cells:
        continue
    runs = []
    for x, h in cells:
        if runs and runs[-1][0] == h and runs[-1][2] == x - 1:
            runs[-1][2] = x
        else:
            runs.append([h, x, x])
    desc = ' '.join(f'{h}x{a}-{b}({b - a + 1})' for h, a, b in runs)
    print(f'{y:3} {desc}')
