const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 2 });
  await page.goto('http://localhost:4733/f/', { waitUntil: 'networkidle' });

  const slugs = process.argv.slice(2);
  for (const slug of slugs) {
    const card = page.locator(`figure.card:has(.slug:text-is("${slug}"))`).first();
    if (await card.count()) {
      await card.screenshot({ path: `.scratch-h-pulse/${slug}.png` });
      console.log('shot', slug);
    } else {
      console.log('MISSING', slug);
    }
  }
  await browser.close();
})();
