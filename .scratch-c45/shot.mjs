import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
await p.goto('http://127.0.0.1:4917/cands.html', { waitUntil: 'load' });
await p.screenshot({ path: '.scratch-c45/cands.png', fullPage: true });
await b.close();
