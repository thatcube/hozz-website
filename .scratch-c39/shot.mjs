import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1400,height:1200}, deviceScaleFactor:2 });
await p.goto('http://localhost:4917/logos/', { waitUntil:'networkidle' });
const card = p.locator('text=Ripple, Sheen').first();
await card.scrollIntoViewIfNeeded();
const box = await card.evaluateHandle(el => el.closest('article,li,section,div'));
await p.screenshot({ path:'.scratch-c39/page.png', clip: await (await box.asElement()).boundingBox() });
await b.close();
