import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { readFileSync, writeFileSync } from 'node:fs';

const PORT = process.env.PORT || 5317;
const slugs = (process.env.SLUGS || 't17').split(',');
const out = process.env.OUT || '.scratch-t17/shot.png';

const browser = await chromium.launch();
const page = await browser.newPage({ viewportSize: { width: 1000, height: 700 }, deviceScaleFactor: 2 });
await page.goto(`http://127.0.0.1:${PORT}/logos/index.html`, { waitUntil: 'load' });

// Pull each mark's inline SVG out of the built page and re-render it on a
// clean strip at the sizes that matter.
const svgs = await page.evaluate((slugs) => {
  const found = {};
  for (const s of slugs) {
    const el = document.querySelector(`#${s} svg`) || null;
    found[s] = el ? el.outerHTML : null;
  }
  if (Object.values(found).some((v) => !v)) {
    // Fall back: match by aria-label / order using the card headings.
    const cards = [...document.querySelectorAll('article, li, .card, .mark')];
    for (const s of slugs) {
      if (found[s]) continue;
      const c = cards.find((c) => c.textContent.trim().toLowerCase().includes(s));
      const el = c && c.querySelector('svg');
      if (el) found[s] = el.outerHTML;
    }
  }
  return found;
}, slugs);

const missing = slugs.filter((s) => !svgs[s]);
if (missing.length) {
  const html = await page.content();
  writeFileSync('.scratch-t17/page.html', html);
  console.error('missing:', missing.join(','), '- dumped page.html');
}

const SIZES = [96, 48, 32, 24, 16];
const strip = `<!doctype html><body style="margin:0;font:12px system-ui;background:#fff">
${slugs.filter((s) => svgs[s]).map((s) => `
<div style="display:flex;gap:26px;align-items:flex-end;padding:22px 26px;background:#fbfaf8">
  <div style="width:34px">${s}</div>
  ${SIZES.map((n) => `<div>${svgs[s].replace(/width="\d+"/, `width="${n}"`).replace(/height="\d+"/, `height="${n}"`)}</div>`).join('')}
</div>
<div style="display:flex;gap:26px;align-items:flex-end;padding:22px 26px;background:#14161a;color:#888">
  <div style="width:34px">${s}</div>
  ${SIZES.map((n) => `<div>${svgs[s].replace(/width="\d+"/, `width="${n}"`).replace(/height="\d+"/, `height="${n}"`)}</div>`).join('')}
</div>`).join('')}
</body>`;

await page.setContent(strip);
await page.setViewportSize({ width: 700, height: 60 + slugs.length * 260 });
await page.screenshot({ path: out, fullPage: true });
await browser.close();
console.log('wrote', out);
