import sys, math
sys.path.insert(0,'tools')
exec(open('.scratch-c39/cand8.py').read().split("def build3")[0])
from shade import edge, crescent, clear
# c18-style: 5 tones, one lit rim, one shade crescent
key=M.keyline(M.DISC); inner=M.DISC-key
lit=edge(inner,0,-1,1); deep=crescent(inner,0,-1); field=clear(inner,lit,deep)
RA=['#3f6f92','#5d8cb0','#cfe3ef','#eaf5fb']
tone={}
for p in field: tone[p]=2
for p in deep: tone[p]=0
for p in lit: tone[p]=3
open('.scratch-c39/ZZflat.svg','w').write(svg(tone,RA))
print('flat reference written')
