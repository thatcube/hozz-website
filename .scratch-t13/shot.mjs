import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 700, height: 1400 }, deviceScaleFactor: 2 });
await p.goto(process.argv[2], { waitUntil: 'networkidle' });
await p.waitForFunction(() => document.title === 'ready');
await p.screenshot({ path: process.argv[3], fullPage: true });
await b.close();
