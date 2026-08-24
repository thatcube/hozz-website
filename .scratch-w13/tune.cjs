const pw = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');

const MODE = process.argv[2] || 'l';
const WIDTHS = MODE === 'l' ? [1440, 1024] : [390, 430];
const SEL = MODE === 'l' ? '.stage-l' : '.stage-p';
const NDEST = 6;
const NRIDE = MODE === 'l' ? 6 : 4;

const setup = (sel) => {
  window.__stage = document.querySelector(sel);
  window.__d = [...window.__stage.querySelectorAll('.arm-dest')];
  window.__r = [...window.__stage.querySelectorAll('.arm-ride')];
  window.__score = (angles) => {
    const all = [...window.__d, ...window.__r];
    all.forEach((el, i) => el.style.setProperty('--a', angles[i] + 'deg'));
    void window.__stage.offsetHeight;
    const sb = window.__stage.getBoundingClientRect();
    const painted = (root) => {
      const q = root.getBoundingClientRect();
      let l = q.left, t = q.top, r = q.right, bm = q.bottom;
      const walk = (n) => {
        for (const k of n.childNodes) {
          if (k.nodeType === 3 && k.textContent.trim()) {
            const rg = document.createRange();
            rg.selectNodeContents(k);
            const z = rg.getBoundingClientRect();
            if (z.width) { l = Math.min(l, z.left); t = Math.min(t, z.top); r = Math.max(r, z.right); bm = Math.max(bm, z.bottom); }
          } else if (k.nodeType === 1) walk(k);
        }
      };
      walk(root);
      return { left: l, top: t, right: r, bottom: bm };
    };
    const pins = all.map((el) => painted(el.querySelector('.pin')));
    const fixed = [
      window.__stage.querySelector('.disc').getBoundingClientRect(),
      window.__stage.querySelector('.pin-src').getBoundingClientRect(),
    ];
    let s = 0;
    const PAD = Number(window.__pad || 12);
    const hit = (q, z, pad) => {
      const ox = Math.min(q.right, z.right) - Math.max(q.left, z.left) + pad;
      const oy = Math.min(q.bottom, z.bottom) - Math.max(q.top, z.top) + pad;
      return ox > 0 && oy > 0 ? ox * oy : 0;
    };
    for (let i = 0; i < pins.length; i++) {
      const q = pins[i];
      s += Math.max(0, sb.left + 16 - q.left) * 40;
      s += Math.max(0, q.right - (sb.right - 16)) * 40;
      s += Math.max(0, sb.top + 2 - q.top) * 40;
      s += Math.max(0, q.bottom - (sb.bottom - 10)) * 40;
      for (const f of fixed) s += hit(q, f, 14) * 3;
      for (let j = i + 1; j < pins.length; j++) s += hit(q, pins[j], PAD);
    }
    return Math.round(s);
  };
};

(async () => {
  const b = await pw.chromium.launch();
  const pages = [];
  for (const w of WIDTHS) {
    const c = await b.newContext({ viewport: { width: w, height: 1000 } });
    const p = await c.newPage();
    await p.goto('http://127.0.0.1:5177/w/w13/', { waitUntil: 'networkidle' });
    await p.waitForTimeout(400);
    await p.evaluate(setup, SEL); await p.evaluate((v) => (window.__pad = v), MODE === 'l' ? 12 : 7);
    pages.push(p);
  }
  const score = async (a) => {
    let t = 0;
    for (const p of pages) t += await p.evaluate((x) => window.__score(x), a);
    return t;
  };

  const seeds = [MODE === 'l'
    ? [130, 52, 112, 96, 141, 38, 50, 116, 28, 138, 20, 126]
    : [122, 14, 117, 116, 112, 78, 48, 62, 68, 76]];
  const N = MODE === 'l' ? 12 : 10;
  for (let r = 0; r < 7; r++) {
    seeds.push(Array.from({ length: N }, () => 14 + Math.floor(Math.random() * 152)));
  }

  let gBest = null, gScore = Infinity;
  for (const seed of seeds) {
    let best = seed.slice();
    let bs = await score(best);
    for (let temp = 21; temp >= 1; temp -= 1) {
      let improved = true;
      while (improved) {
        improved = false;
        for (let i = 0; i < best.length; i++) {
          for (const d of [temp, -temp]) {
            const cand = best.slice();
            cand[i] = Math.max(14, Math.min(166, cand[i] + d));
            if (cand[i] === best[i]) continue;
            const cs = await score(cand);
            if (cs < bs) { bs = cs; best = cand; improved = true; }
          }
        }
      }
      if (bs === 0) break;
    }
    console.log('  run ->', bs, best.join(','));
    if (bs < gScore) { gScore = bs; gBest = best; }
    if (gScore === 0) break;
  }
  const best = gBest, bs = gScore;
  console.log('BEST', bs);
  console.log('dest', best.slice(0, NDEST).join(','));
  console.log('ride', best.slice(NDEST, NDEST + NRIDE).join(','));
  await b.close();
})();
