import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1 });
page.on('console', m => console.log('console:', m.type(), m.text()));
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto('http://127.0.0.1:5311/t13-preview.html', { waitUntil: 'networkidle' });
try {
  await page.waitForFunction(() => document.title === 'ready', null, { timeout: 12000 });
} catch { console.log('not ready'); }
await page.screenshot({ path: '.scratch-t13/shot.png', fullPage: true });
await browser.close();
console.log('ok');
