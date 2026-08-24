"""Rasterise a rectilinear pixel-art SVG (rects + H/V paths) to a 32 grid.

Document order is honoured, <defs> is skipped, and translate/matrix transforms
on rects are applied.
"""
import re
import sys
from collections import Counter


def fill_path(d, grid, fill):
    toks = re.findall(r'([MHVLZz])\s*([-\d.,\s]*)', d)
    subpaths, pts = [], []
    cx = cy = 0.0
    for cmd, arg in toks:
        nums = [float(t) for t in arg.replace(',', ' ').split()]
        if cmd == 'M':
            if pts:
                subpaths.append(pts)
            cx, cy = nums[0], nums[1]
            pts = [(cx, cy)]
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
        elif cmd in 'Zz':
            if pts:
                subpaths.append(pts)
                pts = []
    if pts:
        subpaths.append(pts)
    edges = []
    for sp in subpaths:
        for i in range(len(sp)):
            x0, y0 = sp[i]
            x1, y1 = sp[(i + 1) % len(sp)]
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


def parse(svg):
    svg = re.sub(r'<defs>.*?</defs>', '', svg, flags=re.S)
    grid = {}
    for m in re.finditer(r'<(rect|path)([^>]*?)/?>', svg):
        tag, a = m.group(1), m.group(2)
        fm = re.search(r'fill="([^"]+)"', a)
        if not fm:
            continue
        fill = fm.group(1).lower()
        if tag == 'path':
            fill_path(re.search(r'd="([^"]+)"', a).group(1), grid, fill)
            continue

        def g(k, d='0'):
            mm = re.search(rf'\b{k}="([-\d.]+)"', a)
            return float(mm.group(1)) if mm else float(d)
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        tm = re.search(r'transform="(matrix|translate)\(([^)]+)\)"', a)
        if tm:
            v = [float(t) for t in tm.group(2).replace(',', ' ').split()]
            va, vb, vc, vd, ve, vf = v if tm.group(1) == 'matrix' else (1, 0, 0, 1, v[0], v[1])
            xs, ys = [], []
            for px, py in ((x, y), (x + w, y + h)):
                xs.append(va * px + vc * py + ve)
                ys.append(vb * px + vd * py + vf)
            x, y, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                grid[(xx, yy)] = fill
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
