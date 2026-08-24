const pw = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

(async () => {
  const b = await pw.chromium.launch();
  for (const w of [1920, 1440, 1024, 390]) {
    const c = await b.newContext({ viewport: { width: w, height: 1000 } });
    const p = await c.newPage();
    await p.goto('http://127.0.0.1:5177/w/w13/', { waitUntil: 'networkidle' });
    await p.waitForTimeout(600);
    const out = await p.evaluate(() => {
      const stage = [...document.querySelectorAll('.stage')].find(
        (s) => getComputedStyle(s).display !== 'none'
      );
      const sb = stage.getBoundingClientRect();
      const pins = [...stage.querySelectorAll('.pin')].map((el) => {
        const r = el.getBoundingClientRect();
        return {
          label: (el.textContent || '').trim().split('\n')[0].slice(0, 26),
          l: r.left, t: r.top, r: r.right, b: r.bottom,
        };
      });
      const hits = [];
      for (let i = 0; i < pins.length; i++)
        for (let j = i + 1; j < pins.length; j++) {
          const a = pins[i], z = pins[j];
          const ox = Math.min(a.r, z.r) - Math.max(a.l, z.l);
          const oy = Math.min(a.b, z.b) - Math.max(a.t, z.t);
          if (ox > -6 && oy > -6)
            hits.push(`${a.label} × ${z.label}  (gapX ${Math.round(-ox)}, gapY ${Math.round(-oy)})`);
        }
      const clipped = pins
        .filter((q) => q.l < sb.left - 2 || q.r > sb.right + 2 || q.t < sb.top - 2 || q.b > sb.bottom + 2)
        .map((q) => q.label);
      return { pins: pins.length, hits, clipped };
    });
    console.log(`--- ${w} --- pins:${out.pins}`);
    out.hits.forEach((h) => console.log('  COLLIDE ' + h));
    if (out.clipped.length) console.log('  CLIPPED ' + out.clipped.join(' | '));
    if (!out.hits.length && !out.clipped.length) console.log('  clean');
    await c.close();
  }
  await b.close();
})();
