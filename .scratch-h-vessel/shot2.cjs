const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1200 }, deviceScaleFactor: 2 });
  await p.goto('http://127.0.0.1:4733/f/', { waitUntil: 'networkidle' });
  const card = p.locator('figure.card:has(.slug:text-is("h00"))').first();
  await card.scrollIntoViewIfNeeded();
  await card.screenshot({ path: '.scratch-h-vessel/h00.png' });
  await b.close();
})();
