// Independent check: rasterise the shipped .astro files and re-measure.
import fs from 'fs';
import { facePathsAt } from './mark.mjs';

const RECT = /M(-?\d+) (-?\d+)h(\d+)v1h-\3z/g;
const rects = (d) => {
  const out = [];
  for (const m of d.matchAll(RECT)) {
    const [x, y, w] = [+m[1], +m[2], +m[3]];
    for (let i = 0; i < w; i++) out.push([x + i, y]);
  }
  return out;
};

for (const slug of ['c22', 'c23', 'c24', 'c25']) {
  const src = fs.readFileSync(`src/components/mark/logos/${slug}.astro`, 'utf8');
  const px = new Map(); // "x,y" -> fill, in paint order
  const layers = [];
  for (const m of src.matchAll(/<path d="([^"]+)" fill="(#[0-9a-f]{6})" \/>/g)) {
    const p = rects(m[1]);
    layers.push([p, m[2]]);
    for (const [x, y] of p) px.set(`${x},${y}`, m[2]);
  }
  const fm = src.match(/facePathsAt\(\{ cx: 16, cy: (\d+), size: '(\w+)', smile: 'wide', gap: (\d+) \}\)/);
  const key = src.match(/<g fill="(#[0-9a-f]{6})"/)[1];
  const face = facePathsAt({ cx: 16, cy: +fm[1], size: fm[2], smile: 'wide', gap: +fm[3] });
  const facePx = face.flatMap(rects);
  for (const [x, y] of facePx) px.set(`${x},${y}`, key);

  const all = [...px.keys()].map((k) => k.split(',').map(Number));
  const X = all.map(([x]) => x), Y = all.map(([, y]) => y);
  const bbox = [Math.min(...X), Math.max(...X), Math.min(...Y), Math.max(...Y)];

  // rows of the silhouette
  const rows = new Map();
  for (const [x, y] of all) {
    if (!rows.has(y)) rows.set(y, []);
    rows.get(y).push(x);
  }
  const ys = [...rows.keys()].sort((a, b) => a - b);

  // 1. mirror symmetry about x=16 (pixel set AND colour), per layer
  let sym = true;
  for (const [p, f] of [...layers, [facePx, key]]) {
    const s = new Set(p.map(([x, y]) => `${x},${y}`));
    for (const [x, y] of p) if (!s.has(`${31 - x},${y}`)) { sym = false; break; }
    void f;
  }
  // 2. no row more than 2 wider than the row above (extent AND pixel count)
  const ext = (y) => Math.max(...rows.get(y)) - Math.min(...rows.get(y)) + 1;
  const cnt = (y) => rows.get(y).length;
  const spurs = [];
  for (let i = 1; i < ys.length; i++) {
    if (ys[i] !== ys[i - 1] + 1) spurs.push(['gap', ys[i]]);
    if (ext(ys[i]) - ext(ys[i - 1]) > 2) spurs.push(['ext-down', ys[i], ext(ys[i - 1]), ext(ys[i])]);
    if (cnt(ys[i]) - cnt(ys[i - 1]) > 2) spurs.push(['cnt-down', ys[i], cnt(ys[i - 1]), cnt(ys[i])]);
  }
  for (let i = ys.length - 2; i >= 0; i--) {
    if (ext(ys[i]) - ext(ys[i + 1]) > 2) spurs.push(['ext-up', ys[i], ext(ys[i + 1]), ext(ys[i])]);
    if (cnt(ys[i]) - cnt(ys[i + 1]) > 2) spurs.push(['cnt-up', ys[i], cnt(ys[i + 1]), cnt(ys[i])]);
  }
  // 3. tones
  const tones = new Set([...px.values()]);
  // 4. air above/below the face, measured on the raster
  const fy = facePx.map(([, y]) => y);
  const faceTop = Math.min(...fy), faceBot = Math.max(...fy);
  const above = faceTop - bbox[2], below = bbox[3] - faceBot;
  // 5. face fully on one flat tone
  const under = new Set();
  for (const [x, y] of facePx) {
    for (const [p, f] of layers) if (p.some(([a, b]) => a === x && b === y)) under.add(f);
  }

  const ok = sym && !spurs.length && tones.size >= 5 && above === below &&
    bbox[0] >= 2 && bbox[1] <= 29 && bbox[2] >= 2 && bbox[3] <= 29;
  console.log(
    `${slug} ${ok ? 'PASS' : 'FAIL'} | tones ${tones.size} | bbox x${bbox[0]}-${bbox[1]} y${bbox[2]}-${bbox[3]}` +
    ` (${bbox[1] - bbox[0] + 1}x${bbox[3] - bbox[2] + 1}) | air ${above}/${below}` +
    ` | symmetric ${sym} | spurs ${spurs.length ? JSON.stringify(spurs) : 'none'}` +
    ` | face ground ${[...under].join(',') || 'n/a'} | keyline ${key}`,
  );
}
