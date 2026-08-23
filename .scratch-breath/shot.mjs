import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 });
await p.goto('http://localhost:4861/logos/', { waitUntil: 'networkidle' });
for (const [label, slug] of Object.entries({'Hozz — One Breath':'c35','Hozz — Two Circles':'c36','Hozz — Lit From Above':'c37','Hozz — Held':'c38'})) {
  const el = p.locator(`svg[aria-label="${label}"]`).first();
  const card = el.locator('xpath=ancestor::*[self::article or self::li or self::section][1]');
  const t = (await card.count()) ? card.first() : el;
  await t.scrollIntoViewIfNeeded();
  await t.screenshot({ path: `.scratch-breath/${slug}.png` });
}
await b.close(); console.log('shot');
