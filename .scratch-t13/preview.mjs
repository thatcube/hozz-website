/**
 * Pixel-truth preview. Marks are rasterised at their real small sizes in a
 * canvas and then magnified with smoothing off, so what you look at is what a
 * 24px favicon actually is — not a vector blown up.
 */
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('dist/logos/index.html', 'utf8');

function grab(label) {
  const i = html.indexOf(`aria-label="${label}"`);
  if (i < 0) throw new Error(`no mark labelled ${label}`);
  const start = html.lastIndexOf('<svg', i);
  const end = html.indexOf('</svg>', i) + 6;
  return html.slice(start, end);
}

const marks = [
  ['t13', grab('Twozz — Glass, cast')],
  ['twozz shipped', readFileSync('.briefs/twozz-shipped.svg', 'utf8')],
  ['c45 chosen Hozz', grab('Hozz — Ripple, Lens')],
  ['t10 sibling', grab('Twozz — Calm')],
];

writeFileSync(
  'dist/t13-preview.html',
  `<!doctype html><meta charset="utf-8"><title>t13 pixels</title>
<style>
  body { font: 12px ui-sans-serif, system-ui; margin: 20px; background: #fbfbfd; }
  .row { display: flex; align-items: center; gap: 18px; margin-bottom: 10px; }
  .name { width: 110px; text-align: right; }
  canvas { image-rendering: pixelated; }
  .dark { background: #14121a; color: #eee; padding: 10px 0; }
</style>
<div id="out"></div>
<script type="module">
const MARKS = ${JSON.stringify(marks)};
const VIEWS = [[96, 3], [32, 8], [24, 8], [16, 8]];

function load(svg, size) {
  let s = svg.replace(/width="\\d+"/, 'width="' + size + '"')
             .replace(/height="\\d+"/, 'height="' + size + '"');
  if (!s.includes('xmlns=')) s = s.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
  const img = new Image(size, size);
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
  return img.decode().then(() => img);
}

const out = document.getElementById('out');
for (const ground of ['light', 'dark']) {
  const box = document.createElement('div');
  if (ground === 'dark') box.className = 'dark';
  out.appendChild(box);
  for (const [name, svg] of MARKS) {
    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = '<div class="name">' + name + '</div>';
    box.appendChild(row);
    for (const [size, zoom] of VIEWS) {
      const img = await load(svg, size);
      const a = document.createElement('canvas');
      a.width = a.height = size;
      const ac = a.getContext('2d');
      ac.drawImage(img, 0, 0, size, size);
      const b = document.createElement('canvas');
      b.width = b.height = size * zoom;
      const bc = b.getContext('2d');
      bc.imageSmoothingEnabled = false;
      bc.drawImage(a, 0, 0, size * zoom, size * zoom);
      row.appendChild(b);
    }
  }
}
document.title = 'ready';
</script>
`,
);
console.log('wrote dist/t13-preview.html');
