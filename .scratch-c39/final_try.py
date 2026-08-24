import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand10.py').read().split("WIDE=")[0])
WIDE=[1.0,1.0,1.0,1.0,0.9,0.7,0.45,0.2,0.05,0.0]
build5('T1',3.2,3.6,1.8,2.5,WIDE,0.10,0.60,show=True)
build5('T2',3.2,3.6,2.2,3.0,WIDE,0.06,0.70,show=True)
build5('T3',3.0,3.6,1.8,2.5,WIDE,0.10,0.60)
