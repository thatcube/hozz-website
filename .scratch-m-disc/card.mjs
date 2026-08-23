import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 2000, height: 1200 } });
const p = await c.newPage();
await p.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });
for (const slug of ['m01','m02','m03']) {
  await p.locator(`figure.card:has-text("${slug}")`).first().screenshot({ path: `.scratch-m-disc/card-${slug}.png` });
}
await b.close();
console.log('cards');
