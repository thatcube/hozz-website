import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { readFileSync } from 'node:fs';

const file = process.argv[2];
const svg = readFileSync(file, 'utf8');

const browser = await chromium.launch();
const page = await browser.newPage({ viewportSize: { width: 64, height: 64 } });
await page.setContent(`<body style="margin:0;background:#ffffff">${svg}</body>`);
const grid = await page.evaluate(async () => {
  const svgEl = document.querySelector('svg');
  svgEl.setAttribute('width', '32');
  svgEl.setAttribute('height', '32');
  const xml = new XMLSerializer().serializeToString(svgEl);
  const img = new Image();
  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml)));
  await img.decode();
  const c = document.createElement('canvas');
  c.width = 32; c.height = 32;
  const ctx = c.getContext('2d');
  ctx.drawImage(img, 0, 0, 32, 32);
  const d = ctx.getImageData(0, 0, 32, 32).data;
  const out = [];
  for (let y = 0; y < 32; y++) {
    const row = [];
    for (let x = 0; x < 32; x++) {
      const i = (y * 32 + x) * 4;
      row.push([d[i], d[i + 1], d[i + 2], d[i + 3]]);
    }
    out.push(row);
  }
  return out;
});
await browser.close();

const hex = (p) => p[3] < 8 ? null : '#' + [p[0], p[1], p[2]].map(v => v.toString(16).padStart(2, '0')).join('');
const counts = new Map();
const rows = grid.map(r => r.map(hex));
for (const r of rows) for (const h of r) if (h) counts.set(h, (counts.get(h) || 0) + 1);
const tones = [...counts.entries()].sort((a, b) => b[1] - a[1]);
const key = new Map(tones.map(([h], i) => [h, i.toString(36)]));
console.log('tones (' + tones.length + '):');
tones.forEach(([h, n], i) => console.log(`  ${i.toString(36)}  ${h}  ${n}px`));
console.log('    ' + [...Array(32).keys()].map(i => i % 10).join(''));
rows.forEach((r, y) => console.log(String(y).padStart(3) + ' ' + r.map(h => h ? key.get(h) : '.').join('')));
