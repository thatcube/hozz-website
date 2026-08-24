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
    const pins = all.map((el) => el.querySelector('.pin').getBoundingClientRect());
    const fixed = [
      window.__stage.querySelector('.disc').getBoundingClientRect(),
      window.__stage.querySelector('.pin-src').getBoundingClientRect(),
    ];
    let s = 0;
    const PAD = 12;
    const hit = (q, z, pad) => {
      const ox = Math.min(q.right, z.right) - Math.max(q.left, z.left) + pad;
      const oy = Math.min(q.bottom, z.bottom) - Math.max(q.top, z.top) + pad;
      return ox > 0 && oy > 0 ? ox * oy : 0;
    };
    for (let i = 0; i < pins.length; i++) {
      const q = pins[i];
      s += Math.max(0, sb.left + 4 - q.left) * 40;
      s += Math.max(0, q.right - (sb.right - 4)) * 40;
      s += Math.max(0, sb.top + 2 - q.top) * 40;
      s += Math.max(0, q.bottom - (sb.bottom - 4)) * 40;
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
    await p.evaluate(setup, SEL);
    pages.push(p);
  }
  const score = async (a) => {
    let t = 0;
    for (const p of pages) t += await p.evaluate((x) => window.__score(x), a);
    return t;
  };

  let best = MODE === 'l'
    ? [130, 52, 112, 96, 141, 38, 50, 116, 28, 138, 20, 126]
    : [96, 14, 117, 66, 110, 78, 58, 96, 68, 108];
  let bs = await score(best);
  console.log('start', bs, best.join(','));

  for (let temp = 34; temp >= 2; temp -= 2) {
    let improved = true;
    while (improved) {
      improved = false;
      for (let i = 0; i < best.length; i++) {
        for (const d of [temp, -temp]) {
          const cand = best.slice();
          cand[i] = Math.max(14, Math.min(166, cand[i] + d));
          if (cand[i] === best[i]) continue;
          const cs = await score(cand);
          if (cs < bs) {
            bs = cs;
            best = cand;
            improved = true;
          }
        }
      }
    }
    if (bs === 0) break;
  }
  console.log('BEST', bs);
  console.log('dest', best.slice(0, NDEST).join(','));
  console.log('ride', best.slice(NDEST, NDEST + NRIDE).join(','));
  await b.close();
})();
