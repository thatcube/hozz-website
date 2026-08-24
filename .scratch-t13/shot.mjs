import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 3 });
await page.goto('http://127.0.0.1:5311/t13-preview.html', { waitUntil: 'networkidle' });
await page.screenshot({ path: '.scratch-t13/shot.png', fullPage: true });
await browser.close();
console.log('ok');
