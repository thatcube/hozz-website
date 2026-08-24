import playwright from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';

const { chromium } = playwright;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:5816/logos/', { waitUntil: 'networkidle' });

const mark = page.locator('#t16 .ground--light svg').first();
await mark.screenshot({ path: '.scratch-t16/t16-96.png' });
await mark.evaluate((svg) => {
  svg.setAttribute('width', '24');
  svg.setAttribute('height', '24');
  svg.style.width = '24px';
  svg.style.height = '24px';
});
await mark.screenshot({ path: '.scratch-t16/t16-24.png' });

await browser.close();
