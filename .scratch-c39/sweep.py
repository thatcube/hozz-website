import sys, math, importlib
sys.path.insert(0, 'tools')
import c39_sheen as M

def run(lam, wsheen, wform, wedge, phi=0.0, ease=0.35):
    M.W_SHEEN, M.W_FORM, M.W_EDGE = wsheen, wform, wedge
    def wave(t):
        return math.cos(2*math.pi*(abs(t)+phi)/lam)
    M.wave = wave
    def raw(x, y):
        dx=(x+0.5)-M.CX; dy=(y+0.5)-M.CY; r=math.hypot(dx,dy)/M.R
        form=-dy/M.R
        u=(dx+dy)*0.7071; v=(dx-dy)*0.7071
        s=0.5*(M.wave(u)+M.wave(v))
        s*= 1.0 - ease*max(0.0, r-0.76)/0.24
        e=max(0.0,(r-0.68)/0.32)
        return wform*form + wsheen*s + wedge*e*form
    M.raw = raw
    key=M.keyline(M.DISC); inner=M.DISC-key
    tone=M.despeckle(M.quantise(inner), inner)
    jump=max(abs(tone[p]-tone[q]) for p in tone for q in ((p[0]+1,p[1]),(p[0],p[1]+1)) if q in tone)
    hist=[sum(1 for t in tone.values() if t==i) for i in range(M.N_TONES)]
    print(f'--- lam={lam} phi={phi} sheen={wsheen} form={wform} edge={wedge} jump={jump} hist={hist}')
    for y in range(2,24):
        print('     ' + ''.join(str(tone[(x,y)]) if (x,y) in tone else ('#' if (x,y) in M.DISC else '.') for x in range(32)))

for args in [(13,0.85,0.75,0.45),(14,0.80,0.80,0.42),(13,0.90,0.70,0.55),(14,0.85,0.75,0.50)]:
    run(*args)
