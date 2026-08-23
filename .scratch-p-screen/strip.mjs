import pkg from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pkg;
const PORT = process.argv[2];
const TAG = process.argv[3];
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 3 });
await p.goto(`http://localhost:${PORT}/f/`, { waitUntil: 'networkidle' });
for (const px of [96, 24]) {
  for (const gr of ['light', 'dark']) {
    await p.evaluate(({ px, gr }) => {
      document.querySelectorAll('.__strip').forEach((n) => n.remove());
      const d = document.createElement('div');
      d.className = '__strip';
      d.style.cssText = `position:fixed;left:0;top:0;z-index:99999;display:flex;gap:${px}px;padding:${px}px;background:${gr === 'dark' ? '#16181c' : '#fbfbfa'}`;
      for (const n of ['p00', 'p01', 'p02', 'p03']) {
        const svg = [...document.querySelectorAll('svg')].find((s) => {
          const m = s.innerHTML.match(/(p0\d)-[a-z0-9]{5,}/);
          if (!m || m[1] !== n) return false;
          if (s.getAttribute('width') !== String(px)) return false;
          return (s.parentElement.parentElement.className || '').includes(gr);
        });
        if (svg) d.appendChild(svg.cloneNode(true));
      }
      document.body.appendChild(d);
    }, { px, gr });
    const el = await p.$('.__strip');
    await el.screenshot({ path: `.scratch-p-screen/${TAG}-${px}-${gr}.png` });
  }
}
await b.close();
