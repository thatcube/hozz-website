import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const OUT = new URL('./', import.meta.url).pathname;
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1500, height: 1200 },
  deviceScaleFactor: 3,
});
await page.goto('http://localhost:4733/f/', { waitUntil: 'load' });

const slugs = ['tw07', 'tw08', 'tw09'];

// Card screenshots straight off the board.
for (const slug of slugs) {
  const card = page.locator('figure.card').filter({ hasText: slug }).first();
  if ((await card.count()) === 0) {
    console.log('missing card', slug);
    continue;
  }
  await card.screenshot({ path: `${OUT}card-${slug}.png` });
}

// Pull the raw svg markup so we can look at sizes the board does not render.
const svgs = await page.evaluate((slugs) => {
  const out = {};
  for (const fig of document.querySelectorAll('figure.card')) {
    const slug = fig.querySelector('.slug')?.textContent?.trim();
    if (slugs.includes(slug)) out[slug] = fig.querySelector('svg').outerHTML;
  }
  return out;
}, slugs);

fs.writeFileSync(`${OUT}svgs.json`, JSON.stringify(svgs, null, 2));

const sizes = [96, 48, 40, 32, 28, 24, 16];
const row = (slug, bg, fg) => `
  <div style="background:${bg};padding:18px 22px;display:flex;gap:26px;align-items:flex-end">
    ${sizes
      .map(
        (s) => `<div style="display:grid;gap:6px;justify-items:center">
        <div style="width:${s}px;height:${s}px">${svgs[slug]
          .replace(/width="\d+"/, `width="${s}"`)
          .replace(/height="\d+"/, `height="${s}"`)}</div>
        <span style="font:10px ui-monospace;color:${fg}">${s}</span>
      </div>`,
      )
      .join('')}
  </div>`;

const html = `<!doctype html><meta charset="utf-8">
<body style="margin:0;font:13px system-ui;background:#fff">
${slugs
  .map(
    (slug) => `<div style="padding:10px 22px;font:12px ui-monospace">${slug}</div>
    ${row(slug, '#fbfbfa', '#666')}${row(slug, '#16181c', '#aaa')}`,
  )
  .join('')}
</body>`;

fs.writeFileSync(`${OUT}sizes.html`, html);
await page.setViewportSize({ width: 720, height: 1000 });
await page.goto(`file://${OUT}sizes.html`);
await page.screenshot({ path: `${OUT}sizes.png`, fullPage: true });

await browser.close();
console.log('done');
