const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto('http://localhost:4711/f/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);

  const section = await page.$('#plozz');
  await section.screenshot({ path: '.scratch-p-screen/plozz.png' });

  const cards = await page.$$('#plozz .card');
  for (let i = 0; i < cards.length; i++) {
    await cards[i].screenshot({ path: `.scratch-p-screen/card-${i}.png` });
  }
  console.log('cards', cards.length);
  await browser.close();
})();
