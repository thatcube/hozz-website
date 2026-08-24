"""Rasterise a 32-viewBox SVG to a 32x32 grid and report its tone spend."""
import sys, io
from collections import Counter
import cairosvg
from PIL import Image


def grid(path, n=32):
    png = cairosvg.svg2png(url=path, output_width=n, output_height=n)
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    px = im.load()
    out = {}
    for y in range(n):
        for x in range(n):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            out[(x, y)] = f'#{r:02x}{g:02x}{b:02x}'
    return out


def report(path, name):
    g = grid(path)
    c = Counter(g.values())
    tones = [t for t, _ in c.most_common()]
    print(f'\n=== {name}: {len(tones)} tones, {len(g)} px ===')
    for t, k in c.most_common():
        r, g_, b = int(t[1:3], 16), int(t[3:5], 16), int(t[5:7], 16)
        lum = 0.2126 * r + 0.7152 * g_ + 0.0722 * b
        print(f'  {t}  {k:4d}px  lum {lum:5.1f}')
    idx = {t: i for i, t in enumerate(tones)}
    key = '0123456789abcdefghijklmnopqrstuvwxyz'
    print('     ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(32):
        line = ''.join(key[idx[g[(x, y)]]] if (x, y) in g else '.' for x in range(32))
        print(f'  {y:2d} {line}')
    return g


if __name__ == '__main__':
    import os
    H = os.path.expanduser('~/hozzshots/ref')
    report(f'{H}/plozz.svg', 'PLOZZ')
    report(f'{H}/mozz.svg', 'MOZZ')
    report('.briefs/twozz-shipped.svg', 'TWOZZ')
