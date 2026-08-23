import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1680, height: 1200 }, deviceScaleFactor: 2 });
await page.goto('http://localhost:4783/f/', { waitUntil: 'networkidle' });
const section = page.locator('#mozz');
for (const slug of ['m10', 'm11', 'm12']) {
  const card = section.locator('figure.card').filter({ has: page.locator(`.slug:text-is("${slug}")`) });
  await card.screenshot({ path: `.scratch-m-note/${slug}-final.png` });
}
await browser.close();
