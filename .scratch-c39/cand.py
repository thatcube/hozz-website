import sys, math, json
sys.path.insert(0, 'tools')
import c39_sheen as M

FACE = None
def face_px():
    # md, gap 3 -> 8 wide at x12-19, 10 rows from y8
    EY = [[(0,3),(6,9)],[(2,3),(8,9)],[(1,2),(7,8)],[(0,1),(6,7)],[(0,3),(6,9)]]
    # md eyes are EYES_SM widened: 3-wide Z mirrored at +w-3 = +5
    E = [[(0,2)],[(1,2)],[(0,1)],[(0,2)]]
    rows = [[(a,b) for (a,b) in r] + [(a+5,b+5) for (a,b) in r] for r in E]
    rows += [[],[],[]]
    rows += [[(0,0),(7,7)],[(0,1),(6,7)],[(1,6)]]
    s=set()
    for i,rr in enumerate(rows):
        for a,b in rr:
            for k in range(a,b+1): s.add((12+k, 8+i))
    return s
FACE = face_px()

def svg(tone, ramp):
    from shade import to_paths
    key = M.keyline(M.DISC)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" shape-rendering="crispEdges">']
    for px, f in [(M.WATER_OUT,'#96bcd6'), (M.WATER_IN,'#5d8cb0')]:
        out.append(f'<path d="{" ".join(to_paths(px))}" fill="{f}"/>')
    for i, f in enumerate(ramp):
        p = {q for q,t in tone.items() if t==i}
        if p: out.append(f'<path d="{" ".join(to_paths(p))}" fill="{f}"/>')
    out.append(f'<path d="{" ".join(to_paths(key))}" fill="{M.KEY}"/>')
    out.append(f'<path d="{" ".join(to_paths(FACE))}" fill="{M.KEY}"/>')
    out.append('</svg>')
    return ''.join(out)

def make(name, lam, ws, wf, we, axes='diag', ease=0.35):
    def wave(t): return math.cos(2*math.pi*abs(t)/lam)
    def raw(x,y):
        dx=(x+0.5)-M.CX; dy=(y+0.5)-M.CY; r=math.hypot(dx,dy)/M.R
        form=-dy/M.R
        if axes=='diag': u,v=(dx+dy)*0.7071,(dx-dy)*0.7071
        else: u,v=dx,dy
        s=0.5*(wave(u)+wave(v)); s*=1.0-ease*max(0.0,r-0.76)/0.24
        e=max(0.0,(r-0.68)/0.32)
        return wf*form + ws*s + we*e*form
    M.raw=raw
    key=M.keyline(M.DISC); inner=M.DISC-key
    tone=M.despeckle(M.quantise(inner), inner)
    for x,y in tone:
        assert tone[(31-x,y)]==tone[(x,y)], f'{name} asymmetric at {x},{y}'
    open(f'.scratch-c39/{name}.svg','w').write(svg(tone, M.RAMP))
    return tone

import subprocess
cands = [('a-diag13', 13, 0.85, 0.75, 0.45, 'diag'),
         ('b-diag13s',13, 0.90, 0.70, 0.55, 'diag'),
         ('c-cross13',13, 0.85, 0.75, 0.45, 'cross'),
         ('d-cross16',16, 0.85, 0.75, 0.45, 'cross'),
         ('e-diag16', 16, 0.85, 0.75, 0.45, 'diag')]
for c in cands: make(c[0], *c[1:])
print('wrote', [c[0] for c in cands])
