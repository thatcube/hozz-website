import pkg from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pkg;
const PORT = process.env.PORT || 4737;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1600 }, deviceScaleFactor: 6 });
await p.goto(`http://localhost:${PORT}/f/`, { waitUntil: 'networkidle' });
const cards = p.locator('.card');
const n = await cards.count();
let hits = 0;
for (let i = 0; i < n; i++) {
  const c = cards.nth(i);
  const t = ((await c.locator('.slug').first().textContent()) || '').trim();
  if (!['m07', 'm08', 'm09'].includes(t)) continue;
  hits++;
  await c.scrollIntoViewIfNeeded();
  await c.screenshot({ path: `.scratch-m-tape/${t}.png` });
  const big = c.locator('svg[width="96"]');
  for (let k = 0; k < await big.count(); k++)
    await big.nth(k).screenshot({ path: `.scratch-m-tape/${t}-96-${k}.png` });
  const sm = c.locator('svg[width="24"]');
  for (let k = 0; k < await sm.count(); k++)
    await sm.nth(k).screenshot({ path: `.scratch-m-tape/${t}-24-${k}.png` });
}
console.log('hits', hits);
await b.close();
