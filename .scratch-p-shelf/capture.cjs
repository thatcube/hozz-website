const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 }, deviceScaleFactor: 2 });
  await page.goto('http://127.0.0.1:4587/f/', { waitUntil: 'networkidle' });
  for (const slug of ['p10', 'p11', 'p12']) {
    const card = page.locator('#plozz .card').filter({ has: page.locator('.slug', { hasText: slug }) });
    await card.screenshot({ path: `.scratch-p-shelf/${slug}.png` });
    for (const ground of ['light', 'dark']) {
      const row = card.locator(`.row--${ground}`);
      for (const px of ['96', '24']) {
        const cell = row.locator('.cell').filter({ has: page.locator('.px', { hasText: px }) });
        await cell.screenshot({ path: `.scratch-p-shelf/${slug}-${px}-${ground}.png` });
      }
    }
  }
  await browser.close();
})();
