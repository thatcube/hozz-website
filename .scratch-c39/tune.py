import sys, math, itertools
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand10.py').read().split("WIDE=")[0])
WIDE=[1.0,1.0,1.0,1.0,0.9,0.7,0.45,0.2,0.05,0.0]
best=[]
for AMP in (2.2,2.5,2.8,3.0):
  for B1 in (2.8,3.2,3.6):
    for B2 in (1.8,2.2,2.6):
      for r0,r1 in ((0.10,0.60),(0.06,0.70),(0.14,0.55)):
        import io,contextlib
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            t=build5('x',3.2,B1,B2,AMP,WIDE,r0,r1)
        line=buf.getvalue()
        sym='sym=True' in line
        jump=int(line.split('jump=')[1].split()[0]); lone=int(line.split('lone=')[1].split()[0])
        tones=int(line.split('tones=')[1].split()[0])
        if sym and jump<=2 and tones>=9:
            best.append((lone,-tones,AMP,B1,B2,r0,r1))
best.sort()
for b in best[:10]: print(b)
