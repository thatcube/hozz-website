import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;

const OUT = new URL('./', import.meta.url).pathname;

const b = await chromium.launch();
const page = await b.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 3 });
await page.goto('http://127.0.0.1:4733/f/', { waitUntil: 'load' });

for (const slug of ['p00', 'p07', 'p08', 'p09']) {
  const fig = page.locator('figure.card', { has: page.locator(`.slug:text-is("${slug}")`) });
  const n = await fig.count();
  if (!n) { console.log('missing', slug); continue; }
  await fig.first().locator('.rows').screenshot({ path: `${OUT}${slug}-rows.png` });
}

// All three of mine side by side at 96 for composition, plus a strip of the
// small sizes only.
await page.screenshot({ path: `${OUT}full.png`, fullPage: true });

await b.close();
console.log('ok');
