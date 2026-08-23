import pkg from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1400 }, deviceScaleFactor: 3 });
await p.goto('http://localhost:4713/f/', { waitUntil: 'networkidle' });
const all = p.locator('.card');
const n = await all.count();
for (let i = 0; i < n; i++) {
  const c = all.nth(i);
  const s = (await c.locator('.slug').first().innerText()).trim();
  if (['m07', 'm08', 'm09'].includes(s)) {
    await c.scrollIntoViewIfNeeded();
    await c.screenshot({ path: `.scratch-m-tape/${s}.png` });
  }
}
await b.close();
