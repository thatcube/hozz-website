import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
await page.goto('http://localhost:4765/f/', { waitUntil: 'networkidle' });
const card = page.getByText('tw04', { exact: true }).locator('xpath=ancestor::figure[1]');
await card.screenshot({ path: '.scratch-t-live/tw04.png' });
await browser.close();
