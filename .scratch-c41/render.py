"""Render c41 candidates straight to PNG so the ramp can be judged by eye."""
import math
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from circles import circle, check          # noqa: E402
from shade import keyline                   # noqa: E402

OUT = ROOT / 'src/components/mark/logos'
SRC = (OUT / 'c10.astro').read_text()
PATHS = re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', SRC)


def pixels(d):
    s = set()
    for x, y, w in re.findall(r'M(\d+) (\d+)h(\d+)', d):
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    return s


WATER_OUT = set().union(*[pixels(d) for d, f in PATHS[:26] if f == '#96bcd6'])
WATER_IN = set().union(*[pixels(d) for d, f in PATHS[:26] if f != '#96bcd6'])

KEY = '#132638'
RAMP = ['#f2f9fd', '#eaf5fb', '#daebf6', '#cfe3ef', '#c1ddef', '#b5d6ec', '#a9cfe8']

DISC = circle(22)
check(DISC)
KEYRING = keyline(DISC)
INNER = DISC - KEYRING


def depth_field(shape, ky):
    out = [(x, y) for x in range(-3, 35) for y in range(-3, 35) if (x, y) not in shape]
    d = {}
    for p in shape:
        best = 1e9
        for q in out:
            dx = p[0] - q[0]
            dy = (p[1] - q[1]) * ky
            v = dx * dx + dy * dy
            if v < best:
                best = v
        d[p] = math.sqrt(best)
    return d


def quantile_cuts(d, n):
    vals = sorted(d.values())
    return [vals[round(len(vals) * (k + 1) / n) - 1] for k in range(n - 1)]


def bands(d, cuts):
    t = {}
    for p, v in d.items():
        i = 0
        while i < len(cuts) and v > cuts[i] + 1e-9:
            i += 1
        t[p] = i
    return t


# --- the face, exactly as mark.ts lays it out ---------------------------
EYES_SM = [
    [(0, 3)], [(2, 3)], [(1, 1)], [(0, 0)], [(0, 3)],
]
FACE_TXT = (ROOT / 'src/data/mark.ts').read_text()


def face_pixels(cx, cy, gap):
    """Mirror facePathsAt('md','wide') by parsing the rows out of mark.ts."""
    import subprocess
    js = f'''
    import {{ facePathsAt }} from './src/data/mark.ts';
    console.log(JSON.stringify(facePathsAt({{cx:{cx},cy:{cy},size:'md',smile:'wide',gap:{gap}}})));
    '''
    (ROOT / '.scratch-c41/face.mjs').write_text(
        js.replace("./src/data/mark.ts", "../src/data/mark.ts"))
    r = subprocess.run(['npx', 'tsx', '.scratch-c41/face.mjs'], cwd=ROOT,
                       capture_output=True, text=True)
    ds = re.findall(r'M(\d+) (\d+)h(\d+)', r.stdout)
    s = set()
    for x, y, w in ds:
        x, y, w = int(x), int(y), int(w)
        s |= {(x + i, y) for i in range(w)}
    if not s:
        raise SystemExit('face extraction failed: ' + r.stdout + r.stderr)
    return s


FACE = face_pixels(16, 13, 3)


def render(ky, mode, n=7):
    d = depth_field(INNER, ky)
    cuts = quantile_cuts(d, n) if mode == 'q' else [k + 1.5 for k in range(n - 1)]
    t = bands(d, cuts)
    img = Image.new('RGB', (32, 32), '#ffffff')
    px = img.load()

    def put(s, c):
        c = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        for x, y in s:
            px[x, y] = c

    put(WATER_OUT, '#96bcd6')
    put(WATER_IN, '#5d8cb0')
    for i, col in enumerate(RAMP):
        put({p for p, v in t.items() if v == i}, col)
    put(KEYRING, KEY)
    put(FACE, KEY)
    return img, t


CANDS = [('A iso 1px', 1.00, 'u'), ('B wide 1px', 0.72, 'u'), ('C tall 1px', 1.35, 'u'),
         ('D iso quant', 1.00, 'q'), ('E wide quant', 0.78, 'q'), ('F tall quant', 1.30, 'q')]

sheet = Image.new('RGB', (len(CANDS) * 112, 112 + 40), '#f4f4f6')
small = Image.new('RGB', (len(CANDS) * 40, 40), '#f4f4f6')
for i, (name, ky, mode) in enumerate(CANDS):
    img, t = render(ky, mode)
    sheet.paste(img.resize((96, 96), Image.NEAREST), (i * 112 + 8, 8))
    small.paste(img.resize((24, 24), Image.LANCZOS), (i * 40 + 8, 8))
    vis = sorted({v for p, v in t.items() if p not in FACE})
    print(f'{name:14} ky={ky:.2f} {mode}  tones visible outside the face: {vis}')

sheet.paste(small.resize((len(CANDS) * 40, 40)), (0, 112))
sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(
    ROOT / '.scratch-c41/candidates.png')
print('wrote .scratch-c41/candidates.png')
