const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto('http://127.0.0.1:4733/f/', { waitUntil: 'networkidle' });

  for (const slug of ['h01', 'h02', 'h03']) {
    const card = page.locator(`figure.card:has(.slug:text-is("${slug}"))`).first();
    await card.scrollIntoViewIfNeeded();
    await card.screenshot({ path: `.scratch-h-vessel/${slug}.png` });
  }

  // The Hozz section as a whole, so the set can be judged together.
  const sec = page.locator('section#hozz');
  if (await sec.count()) {
    await sec.first().screenshot({ path: '.scratch-h-vessel/hozz-section.png' });
  }

  await browser.close();
})();
