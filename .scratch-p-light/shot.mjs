import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
import fs from 'node:fs';

const PORT = '4733';
const slugs = ['p07', 'p08', 'p09', 'm00', 'p00'];

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 1 });
await p.goto(`http://127.0.0.1:${PORT}/f/`, { waitUntil: 'networkidle' });
await p.waitForTimeout(2500);

const crops = [];
for (const s of slugs) {
  const card = p.locator('figure.card').filter({ has: p.locator(`.slug:text-is("${s}")`) }).first();
  if (!(await card.count())) { console.log(s, 'MISSING'); continue; }
  await card.scrollIntoViewIfNeeded();
  await p.waitForTimeout(150);
  await card.screenshot({ path: `.scratch-p-light/card-${s}.png` });
  const svgs = card.locator('svg');
  const n = await svgs.count();
  for (let i = 0; i < n; i++) {
    const bb = await svgs.nth(i).boundingBox();
    if (!bb) continue;
    const w = Math.round(bb.width);
    if (w !== 24 && w !== 40) continue;
    const file = `.scratch-p-light/c-${s}-${w}-${i}.png`;
    await svgs.nth(i).screenshot({ path: file });
    crops.push({ s, w, i, file });
  }
}
await b.close();

const b2 = await chromium.launch();
const p2 = await b2.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 1 });
const html = `<body style="margin:0;background:#888;font:11px monospace">
<div style="display:flex;flex-wrap:wrap;gap:8px;padding:8px">
${crops
  .map(
    (c) =>
      `<div style="background:${c.i > 3 ? '#111' : '#f7f7f5'};padding:5px;text-align:center">
    <img src="data:image/png;base64,${fs.readFileSync(c.file).toString('base64')}"
      style="width:${c.w * 6}px;image-rendering:pixelated;display:block">
    <span style="color:#fff;background:#333;display:block">${c.s} ${c.w}</span></div>`
  )
  .join('')}
</div></body>`;
await p2.setContent(html);
await p2.waitForTimeout(700);
await p2.screenshot({ path: '.scratch-p-light/small.png', fullPage: true });
await b2.close();
console.log('crops', crops.length);
