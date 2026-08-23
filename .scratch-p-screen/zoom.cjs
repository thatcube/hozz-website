const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 6 });
  await page.goto('http://localhost:4711/f/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  const wanted = ['p01', 'p02', 'p03'];
  const cards = await page.$$('#plozz .card');
  for (const card of cards) {
    const slug = await card.$eval('.slug', (e) => e.textContent.trim());
    if (!wanted.includes(slug)) continue;
    const cells = await card.$$('.row--light .cell, .row--dark .cell');
    // 0 = 96 light, 2 = 40 light, 4 = 96 dark, 6 = 40 dark
    await cells[0].screenshot({ path: `.scratch-p-screen/${slug}-96L.png` });
    await cells[2].screenshot({ path: `.scratch-p-screen/${slug}-40L.png` });
    await cells[4].screenshot({ path: `.scratch-p-screen/${slug}-96D.png` });
    await cells[6].screenshot({ path: `.scratch-p-screen/${slug}-40D.png` });
    console.log('shot', slug);
  }
  await browser.close();
})();
