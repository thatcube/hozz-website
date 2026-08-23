import pkg from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pkg;
const PORT = process.env.PORT || 4761;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1500, height: 1600 }, deviceScaleFactor: 6 });
await p.goto(`http://localhost:${PORT}/f/`, { waitUntil: 'networkidle' });
const cards = p.locator('.card');
const n = await cards.count();
let hits = 0;
for (let i = 0; i < n; i++) {
  const c = cards.nth(i);
  const t = ((await c.locator('.slug').first().textContent()) || '').trim();
  if (!['m07', 'm08', 'm09', 'm00'].includes(t)) continue;
  hits++;
  await c.scrollIntoViewIfNeeded();
  await c.screenshot({ path: `.scratch-m-tape/${t}.png` });
  for (const [tag, sel] of [['96', 'svg[width="96"]'], ['24', 'svg[width="24"]']]) {
    const L = c.locator(sel);
    for (let k = 0; k < await L.count(); k++)
      await L.nth(k).screenshot({ path: `.scratch-m-tape/${t}-${tag}-${k}.png` });
  }
}
console.log('hits', hits);
await b.close();
