import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 2,
});

await page.goto('http://127.0.0.1:4573/f/', { waitUntil: 'networkidle' });
for (const slug of ['m04', 'm05', 'm06']) {
  const card = page.locator('#mozz .card').filter({
    has: page.locator('.slug', { hasText: new RegExp(`^${slug}$`) }),
  });
  await card.locator('.row').nth(0).locator('.cell').nth(3).screenshot({
    path: `.scratch-m-wave/${slug}-24-light.png`,
  });
  await card.locator('.row').nth(1).locator('.cell').nth(3).screenshot({
    path: `.scratch-m-wave/${slug}-24-dark.png`,
  });
  await card.screenshot({ path: `.scratch-m-wave/${slug}-card.png` });
}
await browser.close();
