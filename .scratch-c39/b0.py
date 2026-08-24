import sys, math, io, contextlib
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand10.py').read().split("WIDE=")[0])
WIDE=[1.0,1.0,1.0,1.0,0.9,0.7,0.45,0.2,0.05,0.0]
for B0 in (2.9,3.0,3.05,3.1,3.15,3.2,3.3):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): build5('x',B0,3.6,2.2,3.0,WIDE,0.06,0.70)
    print(B0, buf.getvalue().strip())
