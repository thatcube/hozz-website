const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const port = process.env.PORT || '4731';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 6 });
  await page.goto(`http://localhost:${port}/f/`, { waitUntil: 'networkidle' });

  for (const slug of ['tw01', 'tw02', 'tw03']) {
    const fig = page.locator('figure.card').filter({ has: page.locator('.slug', { hasText: new RegExp(`^${slug}$`) }) });
    if (await fig.count() === 0) { console.log('missing', slug); continue; }
    // first svg in the light row = the 96px render
    const svg = fig.first().locator('.row:not(.row--dark) svg').first();
    await svg.screenshot({ path: `.scratch-t-bubble/${slug}-zoom.png` });
    console.log('zoom', slug);
  }
  await browser.close();
})();
