const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const port = process.env.PORT || '4731';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto(`http://localhost:${port}/f/`, { waitUntil: 'networkidle' });

  for (const slug of ['tw01', 'tw02', 'tw03']) {
    const fig = page.locator('figure.card').filter({ has: page.locator('.slug', { hasText: new RegExp(`^${slug}$`) }) });
    const n = await fig.count();
    if (n === 0) { console.log('missing', slug); continue; }
    await fig.first().screenshot({ path: `.scratch-t-bubble/${slug}.png` });
    console.log('shot', slug);
  }

  // A 40px-only strip for the legibility check, at 1:1 and blown up.
  await page.addStyleTag({ content: '.card{break-inside:avoid}' });
  await browser.close();
})();
