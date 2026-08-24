// What is where, and what is actually pale.
const pw = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const b = await pw.chromium.launch();
  const c = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await c.newPage();
  await p.goto('http://127.0.0.1:5188/w/w13/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(1400);

  const r = await p.evaluate(() => {
    const box = (s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), bottom: Math.round(r.bottom) }; };
    // effective opacity = product of every ancestor's opacity
    const eff = (e) => { let o = 1, n = e; while (n && n !== document.documentElement) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return +o.toFixed(3); };
    const pins = [...document.querySelectorAll('.stage-l .pin')].map((e) => {
      const r = e.getBoundingClientRect();
      return { t: e.textContent.trim().replace(/\s+/g, ' ').slice(0, 34), o: eff(e), x: Math.round(r.x), y: Math.round(r.y + window.scrollY), cx: Math.round(r.x + r.width / 2), cy: Math.round(r.y + window.scrollY + r.height / 2) };
    });
    return {
      navLogo: box('.nav a, header a'),
      h1: box('.hero-say h1'),
      lede: box('.hero-say .lede'),
      eyebrow: box('.eyebrow'),
      shell: box('.hero-copy'),
      stagewrap: box('.stagewrap'),
      stage: box('.stage-l'),
      disc: box('.disc'),
      docH: document.documentElement.scrollHeight,
      pins,
    };
  });
  console.log(JSON.stringify(r, null, 1));
  await b.close();
})();
