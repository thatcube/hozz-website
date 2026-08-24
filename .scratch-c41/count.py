import importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r', ROOT / '.scratch-c41/render.py')
r = importlib.util.module_from_spec(spec); sys.modules['r'] = r; spec.loader.exec_module(r)
D = r.depth_field(r.INNER, 1.0)
for n in (6, 7, 8, 9):
    t = r.bands(D, [k + 1.5 for k in range(n - 1)])
    vis = {}
    for p, v in t.items():
        if p not in r.FACE:
            vis[v] = vis.get(v, 0) + 1
    print(f'{n} tones  visible px per tone: ' +
          ' '.join(f'{k}:{vis.get(k,0)}' for k in range(n)) +
          f'   min {min(vis.get(k,0) for k in range(n))}')
