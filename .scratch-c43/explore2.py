"""Scratch round 2: tune the two edges so the double border reads without going heavy."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / '.scratch-c43'))

from shade import rings, to_paths            # noqa: E402
from geom import DISC, DYS, WATER_OUT, WATER_IN, face_px  # noqa: E402

KEY = '#132638'
W_OUT, W_IN = '#96bcd6', '#5d8cb0'
FIELD = '#cfe3ef'
BEV1, BEV2, BEV3 = '#f2fafe', '#e4f1f9', '#d8eaf4'

RGS, CORE = rings(DISC, 7)
R = RGS + [CORE]


def grade(pix, tones):
    lo, hi = DYS[0], DYS[-1]
    n = len(tones)
    out = [set() for _ in tones]
    for x, y in pix:
        out[min(n - 1, int((y - lo) * n / (hi - lo + 1)))].add((x, y))
    return [p for p in zip(out, tones) if p[0]]


SPECS = {
    # two frame rings graded as one band, then a deep groove
    'v5': lambda: ([(R[0], KEY)]
                   + grade(R[1] | R[2], ['#a5c6e0', '#97bcd9', '#8ab2d2', '#7ea9cb'])
                   + [(R[3], '#3f6f92'), (R[4], BEV1), (R[5], BEV2),
                      (R[6] | R[7], FIELD)]),
    # one frame ring graded, deep groove, three bevel steps
    'v6': lambda: ([(R[0], KEY)]
                   + grade(R[1], ['#a5c6e0', '#93b9d7', '#83abcd'])
                   + [(R[2], '#3f6f92'), (R[3], BEV1), (R[4], BEV2), (R[5], BEV3),
                      (R[6] | R[7], FIELD)]),
    # bright channel, soft mid inner border
    'v7': lambda: [(R[0], KEY), (R[1], '#f4fbff'), (R[2], '#7fa8c6'),
                   (R[3], BEV1), (R[4], BEV2), (R[5], BEV3), (R[6] | R[7], FIELD)],
    # bright channel, deep inner border
    'v8': lambda: [(R[0], KEY), (R[1], '#f4fbff'), (R[2], '#3f6f92'),
                   (R[3], BEV1), (R[4], BEV2), (R[5], BEV3), (R[6] | R[7], FIELD)],
    # bright channel graded (lit above, shaded below), mid inner border graded too
    'v9': lambda: ([(R[0], KEY)]
                   + grade(R[1], ['#f6fcff', '#eaf5fb', '#dcecf6'])
                   + grade(R[2], ['#6f9cbc', '#628fb1', '#5885a8'])
                   + [(R[3], BEV1), (R[4], BEV2), (R[5], BEV3), (R[6] | R[7], FIELD)]),
}


def svg(kind, cy=13):
    layers = [(WATER_OUT, W_OUT), (WATER_IN, W_IN)] + SPECS[kind]()
    body = '\n'.join(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>'
                     for p, f in layers if p)
    fp, _, _ = face_px(cy)
    body += f'\n<path d="{" ".join(to_paths(fp))}" fill="{KEY}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
            f'viewBox="0 0 32 32" shape-rendering="crispEdges">{body}</svg>')


if __name__ == '__main__':
    out = Path(__file__).parent
    kinds = list(SPECS)
    for k in kinds:
        print(k, len({f for _, f in SPECS[k]()}) + 2, 'tones')
    cells = ''.join(
        f'<div class="cell"><div class="big">{svg(k)}</div>'
        f'<div class="sm">{svg(k)}</div><div class="lbl">{k}</div></div>'
        for k in kinds)
    (out / 'preview2.html').write_text(f'''<!doctype html><meta charset=utf8>
<style>
 body{{background:#f6f4ef;font:12px ui-monospace,monospace;margin:24px;color:#333}}
 .row{{display:flex;gap:26px;align-items:flex-start}}
 .cell{{text-align:center}} .big svg{{width:96px;height:96px}}
 .sm svg{{width:24px;height:24px}} .sm{{margin-top:12px}} .lbl{{margin-top:8px}}
 .dark{{background:#1b1b1b;padding:20px;margin-top:20px}}
</style>
<div class="row">{cells}</div>
<div class="row dark">{cells}</div>
''')
    print('wrote preview2.html')
