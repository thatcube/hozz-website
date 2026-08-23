import pkg from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pkg;

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 3 });
await p.goto('http://localhost:4713/f/', { waitUntil: 'networkidle' });

for (const slug of ['m07', 'm08', 'm09']) {
  const card = await p.locator('#mozz .card', { has: p.locator(`.slug:text-is("${slug}")`) }).first();
  await card.screenshot({ path: `.scratch-m-tape/${slug}.png` });
}
await b.close();
