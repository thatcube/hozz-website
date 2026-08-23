const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
const path = require('path'), fs = require('fs');
const D = __dirname, PORT = process.env.PORT || 4739;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 1 });
  await p.goto(`http://localhost:${PORT}/f/`, { waitUntil: 'domcontentloaded' });
  const slugs = ['tw01','tw02','tw03'];
  for (const slug of slugs) {
    const card = p.locator('figure.card').filter({ has: p.locator('.slug', { hasText: new RegExp(`^${slug}$`) }) }).first();
    await card.scrollIntoViewIfNeeded();
    for (const row of ['light','dark']) {
      const cells = card.locator(`.row--${row} .cell`);
      const n = await cells.count();
      for (const [label, idx] of [['96', 0], ['24', n - 1]]) {
        await cells.nth(idx).locator('svg').screenshot({ path: path.join(D, `${slug}-${label}-${row}.png`) });
      }
    }
  }
  const rows = slugs.map(s => `<tr><th>${s}</th>` + ['96-light','96-dark','24-light','24-dark'].map(k => {
    const [sz, g] = k.split('-');
    return `<td class="${g}"><img src="${s}-${sz}-${g}.png" style="width:${sz==='96'?176:176}px"><div class="c">${k}</div></td>`;
  }).join('') + '</tr>').join('');
  fs.writeFileSync(path.join(D, 'sheet.html'), `<html><body style="font:12px system-ui;background:#f1f0ee"><table cellpadding=10>${rows}</table><style>img{image-rendering:pixelated;display:block}td{text-align:center;background:#fafaf8}td.dark{background:#16181c;color:#888}.c{margin-top:6px;color:#999}</style></body></html>`);
  const q = await b.newPage({ viewport: { width: 960, height: 760 }, deviceScaleFactor: 2 });
  await q.goto('file://' + path.join(D, 'sheet.html'));
  await q.screenshot({ path: path.join(D, 'sheet.png'), fullPage: true });
  await b.close(); console.log('ok');
})();
