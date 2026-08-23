import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 2 });
await p.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });
await p.locator('#mozz').screenshot({ path: '.scratch-m-disc/mozz.png' });
for (const s of ['m01','m02','m03']) {
  await p.locator('figure.card').filter({ hasText: s }).first().screenshot({ path: `.scratch-m-disc/${s}.png` });
}
await b.close();
