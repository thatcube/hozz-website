"""Scratch: four readings of "a double border around the ZZ", rendered side by side."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / '.scratch-c43'))

from shade import rings, to_paths            # noqa: E402
from geom import DISC, DYS, WATER_OUT, WATER_IN, face_px  # noqa: E402

KEY = '#132638'
W_OUT, W_IN = '#96bcd6', '#5d8cb0'

FRAME_HI, FRAME_MD, FRAME_LO = '#bcd6e8', '#abc9de', '#9bbcd4'
GROOVE = '#3f6f92'
BEV1, BEV2, BEV3 = '#f2fafe', '#e2f0f9', '#d7e9f4'
FIELD = '#cfe3ef'

RGS, CORE = rings(DISC, 7)
R = RGS + [CORE]


def grade(ring, tones):
    """Split a ring into horizontal bands top to bottom — symmetric about x=16."""
    lo, hi = DYS[0], DYS[-1]
    n = len(tones)
    out = [set() for _ in tones]
    for x, y in ring:
        i = min(n - 1, int((y - lo) * n / (hi - lo + 1)))
        out[i].add((x, y))
    return list(zip(out, tones))


def variant(kind):
    """Return [(pixels, fill)] inside the disc, outermost first."""
    if kind == 'v1':   # keyline, one frame ring, groove, two bevel steps
        return ([(R[0], KEY)] + grade(R[1], [FRAME_HI, FRAME_MD, FRAME_LO])
                + [(R[2], GROOVE), (R[3], BEV1), (R[4], BEV2),
                   (R[5] | R[6] | R[7], FIELD)])
    if kind == 'v2':   # keyline, border, channel, border, bevel, field
        return [(R[0], KEY), (R[1], GROOVE), (R[2], BEV1), (R[3], GROOVE),
                (R[4], BEV2), (R[5], BEV3), (R[6] | R[7], FIELD)]
    if kind == 'v3':   # two frame rings graded, groove, two bevel steps
        return ([(R[0], KEY)] + grade(R[1], [FRAME_HI, FRAME_MD, FRAME_LO])
                + grade(R[2], [FRAME_MD, FRAME_LO, '#8caec7'])
                + [(R[3], GROOVE), (R[4], BEV1), (R[5], BEV2),
                   (R[6] | R[7], FIELD)])
    if kind == 'v4':   # borders inside the keyline: dark / light channel / dark
        return ([(R[0], KEY)] + grade(R[1], [FRAME_HI, FRAME_MD, FRAME_LO])
                + [(R[2], GROOVE), (R[3], BEV1), (R[4], BEV2), (R[5], BEV3),
                   (R[6] | R[7], FIELD)])
    raise ValueError(kind)


def svg(kind, cy=13):
    layers = [(WATER_OUT, W_OUT), (WATER_IN, W_IN)] + variant(kind)
    body = '\n'.join(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>'
                     for p, f in layers if p)
    fp, top, h = face_px(cy)
    body += f'\n<path d="{" ".join(to_paths(fp))}" fill="{KEY}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
            f'viewBox="0 0 32 32" shape-rendering="crispEdges">{body}</svg>')


if __name__ == '__main__':
    out = Path(__file__).parent
    kinds = ['v1', 'v2', 'v3', 'v4']
    for k in kinds:
        (out / f'{k}.svg').write_text(svg(k))
        tones = {f for _, f in variant(k)}
        print(k, len(tones) + 2, 'tones')
    cells = ''.join(
        f'<div class="cell"><div class="big">{svg(k)}</div>'
        f'<div class="sm">{svg(k)}</div><div class="lbl">{k}</div></div>'
        for k in kinds)
    (out / 'preview.html').write_text(f'''<!doctype html><meta charset=utf8>
<style>
 body{{background:#f6f4ef;font:12px ui-monospace,monospace;margin:24px;color:#333}}
 .row{{display:flex;gap:28px;align-items:flex-start}}
 .cell{{text-align:center}}
 .big svg{{width:96px;height:96px}}
 .sm svg{{width:24px;height:24px}}
 .sm{{margin-top:12px}} .lbl{{margin-top:8px}}
 .dark{{background:#1b1b1b;padding:20px;margin-top:24px}}
</style>
<div class="row">{cells}</div>
<div class="row dark">{cells}</div>
''')
    print('wrote preview.html')
