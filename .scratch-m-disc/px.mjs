import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const px = Number(process.argv[2] || 96);
const b = await chromium.launch();
const p = await (await b.newContext({ deviceScaleFactor: 10 })).newPage();
await p.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });
const cards = p.locator('figure.card');
const n = await cards.count();
for (let i = 0; i < n; i++) {
  const c = cards.nth(i);
  const slug = (await c.locator('.slug').first().innerText()).trim();
  if (!['m00','m01','m02','m03'].includes(slug)) continue;
  for (const [g, sel] of [['light','.row--light'],['dark','.row--dark']]) {
    const el = c.locator(`${sel} svg[width="${px}"]`).first();
    if (await el.count()) await el.screenshot({ path: `.scratch-m-disc/${slug}-${px}-${g}.png` });
  }
}
await b.close(); console.log('px', px);
