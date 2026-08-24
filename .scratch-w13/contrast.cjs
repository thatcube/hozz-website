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

// Every text run whose contrast the brief cares about: body and caption text.
const TARGETS = [
  ['.hero .lede', 'hero lede'],
  ['.hero-facts dd', 'hero fact value'],
  ['.hero-facts dt', 'hero fact label (caption)'],
  ['.stagewrap figcaption', 'hero figcaption'],
  ['.pin-dest .fact', 'ring pin fact (mono)'],
  ['.pin-ride .rsample', 'ring pin sample (mono)'],
  ['.sec.t1 .lede', 'section lede on t1'],
  ['.sec.t2 .lede', 'section lede on t2'],
  ['.sec.t3 .lede', 'section lede on t3'],
  ['.sec.t4 .lede', 'section lede on t4'],
  ['.sec.t5 .lede', 'section lede on t5'],
  ['.sec.t6 .lede', 'section lede on t6'],
  ['.sec.t6 p', 'body copy on t6 (deepest wash)'],
  ['.eyebrow', 'eyebrow (caption, mono)'],
  ['.steps p', 'step body'],
  ['.dcard p', 'destination card body'],
  ['table td', 'table cell'],
  ['.tyname', 'record type name'],
  ['.tyval', 'record type value (caption)'],
  ['.faq p', 'FAQ answer'],
  ['.foot-in p', 'footer body'],
  ['.sib-what', 'footer caption'],
  ['.close p', 'close body'],
  ['.note', 'aside note'],
];

(async () => {
  const b = await pw.chromium.launch();
  const rows = [];
  for (const w of [1440, 390]) {
    const c = await b.newContext({ viewport: { width: w, height: 1000 }, deviceScaleFactor: 1 });
    const p = await c.newPage();
    await p.goto('http://127.0.0.1:5177/w/w13/', { waitUntil: 'networkidle' });
    await p.waitForTimeout(700);
    await p.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important}' });

    for (const [sel, name] of TARGETS) {
      const info = await p.evaluate((s) => {
        const el = document.querySelector(s);
        if (!el) return null;
        el.scrollIntoView({ block: 'center' });
        const r = el.getBoundingClientRect();
        if (r.width < 4 || r.height < 4) return null;
        return { color: getComputedStyle(el).color, x: r.x, y: r.y, w: r.width, h: r.height };
      }, sel);
      if (!info) {
        rows.push({ w, name, note: 'not found' });
        continue;
      }
      // hide only the glyphs so the clip shows the real painted backdrop
      await p.evaluate((s) => {
        document.querySelector(s).style.visibility = 'hidden';
      }, sel);
      await p.waitForTimeout(60);
      const vp = p.viewportSize();
      const x0 = Math.max(0, Math.round(info.x));
      const y0 = Math.max(0, Math.round(info.y));
      const clip = {
        x: x0,
        y: y0,
        width: Math.max(2, Math.min(Math.round(info.w), vp.width - x0)),
        height: Math.max(2, Math.min(Math.round(info.h), vp.height - y0, 260)),
      };
      if (clip.width < 2 || clip.height < 2 || y0 >= vp.height) {
        rows.push({ w, name, note: 'offscreen' });
        await p.evaluate((s) => { document.querySelector(s).style.visibility = ''; }, sel);
        continue;
      }
      const buf = await p.screenshot({ clip });
      await p.evaluate((s) => {
        document.querySelector(s).style.visibility = '';
      }, sel);

      const meta = decodePng(buf);
      const data = meta.data;
      const ch = meta.channels;
      let worst = 1e9,
        worstPx = null;
      const [tr, tg, tb] = info.color.match(/[\d.]+/g).map(Number);
      const tl = L(tr, tg, tb);
      for (let i = 0; i < data.length; i += ch) {
        const bl = L(data[i], data[i + 1], data[i + 2]);
        const cr = ratio(tl, bl);
        if (cr < worst) {
          worst = cr;
          worstPx = [data[i], data[i + 1], data[i + 2]];
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

  let fails = 0;
  for (const r of rows) {
    if (r.note) {
      console.log(`${String(r.w).padEnd(5)} ${r.name.padEnd(32)} ${r.note}`);
      continue;
    }
    const ok = r.ratio >= 4.5;
    if (!ok) fails++;
    console.log(
      `${String(r.w).padEnd(5)} ${r.name.padEnd(32)} ${String(r.ratio).padStart(6)}:1  ${ok ? 'PASS' : '**FAIL**'}  text ${r.text} on worst pixel ${r.worstBg}`
    );
  }
  console.log(fails ? `\n${fails} FAILING` : '\nALL PASS (>= 4.5:1, worst rendered pixel)');
})();
