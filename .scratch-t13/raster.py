"""Rasterise a rectilinear pixel-art SVG (rects + H/V paths) to a 32 grid."""
import re
import sys
from collections import Counter


def parse(svg):
    grid = {}

    def put(x, y, w, h, fill):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                grid[(xx, yy)] = fill

    for m in re.finditer(r'<rect([^>]*)/>', svg):
        a = m.group(1)
        def g(k, d='0'):
            mm = re.search(rf'{k}="([-\d.]+)"', a)
            return float(mm.group(1)) if mm else float(d)
        fill = re.search(r'fill="([^"]+)"', a).group(1)
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        tm = re.search(r'transform="matrix\(([^)]+)\)"', a)
        if tm:
            va, vb, vc, vd, ve, vf = [float(t) for t in tm.group(1).split()]
            xs, ys = [], []
            for px, py in ((x, y), (x + w, y + h)):
                xs.append(va * px + vc * py + ve)
                ys.append(vb * px + vd * py + vf)
            x, y = min(xs), min(ys)
            w, h = max(xs) - x, max(ys) - y
        put(x, y, w, h, fill.lower())

    for m in re.finditer(r'<path d="([^"]+)"\s+fill="([^"]+)"', svg):
        d, fill = m.group(1), m.group(2).lower()
        toks = re.findall(r'([MHVLZz])\s*([-\d.\s]*)', d)
        pts = []
        cx = cy = 0.0
        for cmd, arg in toks:
            nums = [float(t) for t in arg.replace(',', ' ').split()]
            if cmd == 'M':
                cx, cy = nums[0], nums[1]
                pts.append((cx, cy))
            elif cmd == 'L':
                cx, cy = nums[0], nums[1]
                pts.append((cx, cy))
            elif cmd == 'H':
                for n in nums:
                    cx = n
                    pts.append((cx, cy))
            elif cmd == 'V':
                for n in nums:
                    cy = n
                    pts.append((cx, cy))
        # scanline, even-odd, at pixel centres
        edges = []
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
        for py in range(32):
            yc = py + 0.5
            xs = []
            for x0, y0, x1, y1 in edges:
                if (y0 <= yc < y1) or (y1 <= yc < y0):
                    t = (yc - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for px in range(32):
                    if xs[i] <= px + 0.5 <= xs[i + 1]:
                        grid[(px, py)] = fill
    return grid


def show(grid, title):
    fills = Counter(grid.values())
    order = [f for f, _ in fills.most_common()]
    sym = {f: c for f, c in zip(order, '123456789abcdef')}
    print(title)
    print('    ' + ''.join(str(i % 10) for i in range(32)))
    for y in range(32):
        print(f'{y:3} ' + ''.join(sym.get(grid.get((x, y)), '.') for x in range(32)))
    print(f'{len(fills)} tones:')
    for f, n in fills.most_common():
        print(f'  {sym[f]} {f} {n}px')


if __name__ == '__main__':
    src = open(sys.argv[1]).read()
    show(parse(src), sys.argv[1])
