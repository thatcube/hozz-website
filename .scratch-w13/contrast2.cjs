const pw = require('/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright');
const decodePng = require('./png.cjs');

const lin = (c) => {
  c /= 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
};
const L = (r, g, b) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
const ratio = (a, b) => {
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return (hi + 0.05) / (lo + 0.05);
};

// Body and caption text runs, one per distinct colour/backdrop pairing.
const TARGETS = [
  ['.hero .lede', 'hero lede'],
  ['.hero-facts dd', 'hero fact value'],
  ['.hero-facts dt', 'hero fact label · caption'],
  ['.eyebrow', 'eyebrow · caption mono'],
  ['.stagewrap figcaption', 'hero figcaption · caption'],
  ['.stage-l .pin-dest .mono', 'ring pin fact · mono'],
  ['.stage-l .pin-ride .rsample', 'ring pin sample · mono'],
  ['.stage-l .pin-dest strong, .stage-l .pin-dest b', 'ring pin name'],
  ['.sec.t1 .lede', 'lede on wash t1'],
  ['.sec.t2 .lede', 'lede on wash t2'],
  ['.sec.t3 .lede', 'lede on wash t3'],
  ['.sec.t4 .lede', 'lede on wash t4'],
  ['.sec.t5 .lede', 'lede on wash t5'],
  ['#faq .lede', 'lede on wash t6 · deepest'],
  ['.faq dd', 'FAQ answer on t6 · deepest'],
  ['.faq dt', 'FAQ question on t6 · deepest'],
  ['.sec.t6.close p', 'close body on t6 · deepest'],
  ['.aside', 'aside note'],
  ['.caveat', 'caveat'],
  ['.cards p', 'card body'],
  ['.dests p', 'destination card body'],
  ['table td', 'table cell'],
  ['.tid', 'record id · mono'],
  ['.tval', 'record value · caption mono'],
  ['.cats li', 'category chip · caption'],
  ['.proms p', 'refusal body'],
  ['.mcp-list li', 'assistant tool body'],
  ['.foot-lead', 'footer body on ink'],
  ['.sibs p, .sibs span', 'footer caption on ink'],
  ['.ringno', 'ring number · caption mono'],
  ['.step-n', 'step number · caption mono'],
  ['.tag', 'tag · caption mono'],
];

(async () => {
  const b = await pw.chromium.launch();
  const rows = [];
  for (const w of [1440, 390]) {
    const c = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
    const p = await c.newPage();
    await p.goto('http://127.0.0.1:5177/w/w13/', { waitUntil: 'networkidle' });
    await p.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important}' });
    await p.waitForTimeout(700);

    for (const [sel, name] of TARGETS) {
      const loc = p.locator(sel).first();
      if ((await loc.count()) === 0) {
        rows.push({ w, name, note: 'absent at this width' });
        continue;
      }
      const info = await loc.evaluate((el) => {
        el.scrollIntoView({ block: 'center' });
        const r = el.getBoundingClientRect();
        return { color: getComputedStyle(el).color, w: r.width, h: r.height };
      });
      if (info.w < 4 || info.h < 4) {
        rows.push({ w, name, note: 'not rendered' });
        continue;
      }
      // Keep the box exactly where it is; just stop painting the glyphs, so the
      // screenshot is the true rendered backdrop the text sits on.
      await loc.evaluate((el) => {
        el.dataset.k = '1';
        [...el.querySelectorAll('*')].filter((k) => !k.textContent.trim()).forEach((k) => (k.style.visibility = 'hidden'));
        el.style.setProperty('color', 'transparent', 'important');
        [...el.querySelectorAll('*')].forEach((k) => k.style.setProperty('color', 'transparent', 'important'));
      });
      await p.waitForTimeout(90);
      let buf;
      try {
        buf = await loc.screenshot();
      } catch (e) {
        rows.push({ w, name, note: 'screenshot failed' });
        continue;
      } finally {
        await loc.evaluate((el) => {
          el.style.removeProperty('color');
          [...el.querySelectorAll('*')].forEach((k) => {
            k.style.removeProperty('color');
            k.style.removeProperty('visibility');
          });
        });
      }

      const img = decodePng(buf);
      const ch = img.channels;
      const [tr, tg, tb] = info.color.match(/[\d.]+/g).map(Number);
      const tl = L(tr, tg, tb);
      let worst = 1e9,
        worstPx = null;
      for (let i = 0; i < img.data.length; i += ch) {
        const cr = ratio(tl, L(img.data[i], img.data[i + 1], img.data[i + 2]));
        if (cr < worst) {
          worst = cr;
          worstPx = [img.data[i], img.data[i + 1], img.data[i + 2]];
        }
      }
      rows.push({
        w,
        name,
        text: `rgb(${tr},${tg},${tb})`,
        worstBg: `rgb(${worstPx.join(',')})`,
        ratio: Math.round(worst * 100) / 100,
      });
    }
    await c.close();
  }
  await b.close();

  let fails = 0,
    min = 1e9;
  for (const r of rows) {
    if (r.note) {
      console.log(`${String(r.w).padEnd(5)} ${r.name.padEnd(30)} ${r.note}`);
      continue;
    }
    const ok = r.ratio >= 4.5;
    if (!ok) fails++;
    min = Math.min(min, r.ratio);
    console.log(
      `${String(r.w).padEnd(5)} ${r.name.padEnd(30)} ${String(r.ratio).padStart(6)}:1 ${ok ? 'pass' : '** FAIL **'}  ${r.text} on worst pixel ${r.worstBg}`
    );
  }
  console.log(fails ? `\n${fails} FAILING — lowest ${min}:1` : `\nALL PASS — lowest measured ${min}:1 (worst single rendered pixel)`);
})();
