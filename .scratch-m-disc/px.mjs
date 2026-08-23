import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const size = process.argv[2] || '96';
const b = await chromium.launch();
const c = await b.newContext({ deviceScaleFactor: 10 });
const p = await c.newPage();
await p.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });
for (const slug of ['m00','m01','m02','m03']) {
  const card = p.locator(`figure.card:has-text("${slug}")`).first();
  for (const [i, ground] of [['0','light'],['1','dark']]) {
    const svg = card.locator(`svg[width="${size}"]`).nth(Number(i));
    if (await svg.count()) await svg.screenshot({ path: `.scratch-m-disc/${slug}-${size}-${ground}.png` });
  }
}
await b.close();
console.log('px', size);
