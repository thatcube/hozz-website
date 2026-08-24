"""Preview: t11's two band constructions beside c45 and the shipped Twozz."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SC = ROOT / '.scratch-t11'


def face_svg(cx, cy, size, smile, gap, fill):
    js = (f"import {{facePathsAt}} from '{ROOT}/src/data/mark.ts';"
          f"console.log(JSON.stringify(facePathsAt({{cx:{cx},cy:{cy},size:'{size}',"
          f"smile:'{smile}',gap:{gap}}})));")
    ds = json.loads(subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '--no-warnings', '-e', js],
        capture_output=True, text=True, check=True).stdout)
    return f'<g fill="{fill}">' + ''.join(f'<path d="{d}"/>' for d in ds) + '</g>'


def from_astro(slug, face):
    src = (ROOT / f'src/components/mark/logos/{slug}.astro').read_text()
    body = '\n'.join(f'<path d="{d}" fill="{f}"/>'
                     for d, f in re.findall(r'<path d="([^"]+)"\s+fill="([^"]+)"', src))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
            f'shape-rendering="crispEdges">{body}{face}</svg>')


c45 = from_astro('c45', face_svg(16, 13, 'md', 'compact', 2, '#132638'))
shipped = (ROOT / '.briefs/twozz-shipped.svg').read_text()
shipped = re.sub(r'width="\d+" height="\d+"', '', shipped, count=1)
a = (SC / 'a-shells.svg').read_text()
b = (SC / 'b-rings.svg').read_text()

MARKS = [('c45 (Hozz)', c45), ('t11 shells', a), ('t11 rings', b), ('shipped', shipped)]


def sized(svg, px):
    return svg.replace('<svg ', f'<svg width="{px}" height="{px}" ', 1)


def row(px, bg, fg):
    cells = ''.join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
        f'{sized(s, px)}<span style="font:11px system-ui;color:{fg};opacity:.65">{n}</span></div>'
        for n, s in MARKS)
    return (f'<div style="display:flex;gap:34px;align-items:flex-end;padding:22px 26px;'
            f'background:{bg};border-radius:14px;margin:10px">{cells}</div>')


html = ('<body style="margin:0;background:#e9eaee;padding:10px">'
        + row(96, '#ffffff', '#111') + row(96, '#15161a', '#eee')
        + row(48, '#ffffff', '#111') + row(24, '#ffffff', '#111')
        + row(24, '#15161a', '#eee') + row(16, '#ffffff', '#111') + '</body>')
(SC / 'p.html').write_text(html)

shot = f'''
import {{ chromium }} from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({{ viewport: {{ width: 620, height: 780 }}, deviceScaleFactor: 3 }});
await p.goto('file://{SC}/p.html');
await p.screenshot({{ path: '{SC}/p.png', fullPage: true }});
await b.close();
'''
(SC / 'shot.mjs').write_text(shot)
subprocess.run(['node', SC / 'shot.mjs'], check=True)
print('shot written')
