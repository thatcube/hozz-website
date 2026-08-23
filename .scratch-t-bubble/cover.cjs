const { chromium } = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
const path = require('path'), fs = require('fs');
const D = __dirname, PORT = process.env.PORT || 4739;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 4 });
  await p.goto(`http://localhost:${PORT}/f/`, { waitUntil: 'domcontentloaded' });
  const slugs = ['tw01','tw02','tw03'];
  for (const slug of slugs) {
    const card = p.locator('figure.card').filter({ has: p.locator('.slug', { hasText: new RegExp(`^${slug}$`) }) }).first();
    await card.scrollIntoViewIfNeeded();
    const svg = card.locator('.row--light .cell').first().locator('svg');
    await svg.evaluate((el) => { el.querySelectorAll('[mask]').forEach(n => n.removeAttribute('mask')); });
    await svg.screenshot({ path: path.join(D, `${slug}-cover.png`) });
  }
  fs.writeFileSync(path.join(D, 'cover.html'), `<html><body style="font:12px system-ui;background:#f1f0ee;display:flex;gap:14px;padding:14px">${slugs.map(s=>`<div style="background:#fafaf8;padding:10px;text-align:center"><img src="${s}-cover.png" style="width:200px;display:block"><div style="margin-top:6px;color:#999">${s} · covered</div></div>`).join('')}</body></html>`);
  const q = await b.newPage({ viewport: { width: 720, height: 280 }, deviceScaleFactor: 2 });
  await q.goto('file://' + path.join(D, 'cover.html'));
  await q.screenshot({ path: path.join(D, 'cover.png'), fullPage: true });
  await b.close(); console.log('ok');
})();
