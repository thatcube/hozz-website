import sys
sys.path.insert(0, '.scratch-rosette'); sys.path.insert(0, 'tools')
import breath_rosette as br
from dump import dump
dump([(s, sp) for s, _n, _p, _i, _d, sp in br.MARKS], '.scratch-rosette/cands.json')
