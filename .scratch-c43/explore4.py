"""Scratch round 4: the two real contenders against a plain-disc control."""
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
    # what is already on the board: outline, one lit rim, flat field
    'plain': lambda: [(R[0], KEY), (R[1], '#eaf5fb'),
                      (R[2] | R[3] | R[4] | R[5] | R[6] | R[7], FIELD)],
    # Plozz logic: mid frame band, deep bezel, bright catch, ramp to field
    'v6': lambda: ([(R[0], KEY)]
                   + grade(R[1], ['#a5c6e0', '#93b9d7', '#83abcd'])
                   + [(R[2], '#3f6f92'), (R[3], '#f2fafe'), (R[4], '#e4f1f9'),
                      (R[5], '#d8eaf4'), (R[6] | R[7], FIELD)]),
    # same, softer bezel
    'v6b': lambda: ([(R[0], KEY)]
                    + grade(R[1], ['#a8c8e1', '#9abed9', '#8cb4d1'])
                    + [(R[2], '#54809f'), (R[3], '#f2fafe'), (R[4], '#e6f2fa'),
                       (R[5], '#dbecf5'), (R[6] | R[7], FIELD)]),
    # bright rim, mid ring
    'vA': lambda: ([(R[0], KEY)]
                   + grade(R[1], ['#f4fbff', '#e9f4fc', '#dceef8'])
                   + [(R[2], '#7fa8c6'), (R[3], '#f2fafe'), (R[4], '#e4f1f9'),
                      (R[5], '#d8eaf4'), (R[6] | R[7], FIELD)]),
    # dim channel, mid ring, bright catch
    'vC': lambda: ([(R[0], KEY)]
                   + grade(R[1], ['#e6f2fa', '#dcecf6', '#d2e6f2'])
                   + [(R[2], '#7fa8c6'), (R[3], '#f4fbff'), (R[4], '#e8f3fb'),
                      (R[5], '#dbecf5'), (R[6] | R[7], FIELD)]),
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
        f'<div class="cell"><div class="xl">{svg(k)}</div>'
        f'<div class="big">{svg(k)}</div><div class="sm">{svg(k)}</div>'
        f'<div class="xs">{svg(k)}</div><div class="lbl">{k}</div></div>'
        for k in kinds)
    (out / 'preview4.html').write_text(f'''<!doctype html><meta charset=utf8>
<style>
 body{{background:#f6f4ef;font:12px ui-monospace,monospace;margin:20px;color:#333}}
 .row{{display:flex;gap:22px;align-items:flex-start}}
 .cell{{text-align:center}} .xl svg{{width:176px;height:176px}}
 .big svg{{width:96px;height:96px}} .sm svg{{width:24px;height:24px}}
 .xs svg{{width:16px;height:16px}}
 .big,.sm,.xs{{margin-top:10px}} .lbl{{margin-top:6px}}
</style>
<div class="row">{cells}</div>
''')
    print('wrote preview4.html')
