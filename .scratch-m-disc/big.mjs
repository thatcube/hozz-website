import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 });
await p.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });
for (const s of ['m01','m02','m03']) {
  const card = p.locator('figure.card').filter({ hasText: s }).first();
  const svg = card.locator('svg').first();
  await svg.evaluate(el => { el.setAttribute('width', 340); el.setAttribute('height', 340); });
  await svg.screenshot({ path: `.scratch-m-disc/big-${s}.png` });
}
await b.close();
