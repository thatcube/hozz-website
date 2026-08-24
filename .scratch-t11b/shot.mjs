import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 460 }, deviceScaleFactor: 2 });
await p.goto('file://' + process.cwd() + '/.scratch-t11b/p.html');
await p.waitForTimeout(500);
await p.screenshot({ path: '.scratch-t11b/p.png', fullPage: true });
await b.close();
