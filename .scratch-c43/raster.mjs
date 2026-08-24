import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { readFileSync } from 'node:fs';

const file = process.argv[2];
const svg = readFileSync(file, 'utf8');
const b64 = Buffer.from(svg).toString('base64');

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent(`<body style="margin:0"><canvas id="c" width="32" height="32"></canvas></body>`);
const data = await page.evaluate(async (src) => {
  const img = new Image();
  img.src = src;
  await img.decode();
  const c = document.getElementById('c');
  const ctx = c.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(img, 0, 0, 32, 32);
  return Array.from(ctx.getImageData(0, 0, 32, 32).data);
}, `data:image/svg+xml;base64,${b64}`);
await browser.close();

const hex = (r, g, b, a) => (a < 8 ? '.' : '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join(''));
const grid = [];
const counts = new Map();
for (let y = 0; y < 32; y++) {
  const row = [];
  for (let x = 0; x < 32; x++) {
    const i = (y * 32 + x) * 4;
    const h = hex(data[i], data[i + 1], data[i + 2], data[i + 3]);
    row.push(h);
    counts.set(h, (counts.get(h) || 0) + 1);
  }
  grid.push(row);
}
const keys = [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([k]) => k);
const sym = {};
keys.forEach((k, i) => { sym[k] = k === '.' ? '.' : '0123456789abcdefghijklmnop'[i > 0 ? i - (keys[0] === '.' ? 1 : 0) : 0] ?? '?'; });
// simpler: assign in order excluding '.'
let n = 0;
for (const k of keys) { if (k === '.') { sym[k] = '.'; continue; } sym[k] = '0123456789abcdefghijklmnopqrstuv'[n++]; }
console.log('    ' + Array.from({ length: 32 }, (_, i) => i % 10).join(''));
grid.forEach((row, y) => console.log(String(y).padStart(3) + ' ' + row.map((h) => sym[h]).join('')));
console.log('\nlegend (by area):');
for (const k of keys) console.log(`  ${sym[k]}  ${k}  ${counts.get(k)}`);
