const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 }, deviceScaleFactor: 1 });
  await page.goto('http://127.0.0.1:4579/f/', { waitUntil: 'networkidle' });
  for (const slug of ['p10', 'p11', 'p12']) {
    const card = page.locator('#plozz .card').filter({ has: page.locator(`.slug`, { hasText: slug }) });
    await card.screenshot({ path: `.scratch-p-shelf/${slug}.png` });
  }
  await browser.close();
})();
