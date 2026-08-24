"""Render a mark component's SVG body to PNGs at several sizes, side by side."""
import io
import re
import sys
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def svg_of(slug):
    src = (ROOT / f'src/components/mark/logos/{slug}.astro').read_text()
    body = src.split('<MarkFrame', 1)[1].split('>', 1)[1].split('</MarkFrame>')[0]
    body = re.sub(r'\{facePathsAt\(([^)]*)\)[\s\S]*?\)\}', lambda m: face(m.group(1)), body)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
            f'viewBox="0 0 32 32" shape-rendering="crispEdges">{body}</svg>')


def face(args):
    sys.path.insert(0, str(ROOT / 'tools'))
    kw = dict(re.findall(r"(\w+):\s*'?([\w\d]+)'?", args))
    import face_py
    return ''.join(f'<path d="{d}" />' for d in face_py.face_paths(
        cx=int(kw['cx']), cy=int(kw['cy']), size=kw['size'],
        smile=kw['smile'], gap=int(kw['gap'])))


def sheet(slug, out, sizes=(320, 96, 48, 24, 16), bg='#ffffff'):
    svg = svg_of(slug)
    imgs = []
    for s in sizes:
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=s, output_height=s)
        imgs.append(Image.open(io.BytesIO(png)).convert('RGBA'))
    pad = 24
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2
    sheet = Image.new('RGBA', (w, h), bg)
    x = pad
    for i in imgs:
        sheet.alpha_composite(i, (x, pad + (h - pad * 2 - i.height) // 2))
        x += i.width + pad
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    slug = sys.argv[1]
    sheet(slug, ROOT / f'.scratch-t19/{slug}-light.png', bg='#ffffff')
    sheet(slug, ROOT / f'.scratch-t19/{slug}-dark.png', bg='#141414')
