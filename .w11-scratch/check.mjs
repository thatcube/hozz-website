import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
import fs from 'node:fs';

const PAGE_URL = 'http://127.0.0.1:5187/w/w11/';
const WIDTHS = [1920, 1440, 1024, 390];
const OUT = new URL('./shots/', import.meta.url).pathname;
fs.mkdirSync(OUT, { recursive: true });

// sRGB relative luminance + WCAG ratio, from actual rendered pixels.
const lum = ([r, g, b]) => {
  const f = (v) => {
    v /= 255;
    return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => {
  const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m);
  return (x + 0.05) / (y + 0.05);
};

const browser = await chromium.launch();
const report = { widths: {}, contrast: [] };

for (const w of WIDTHS) {
  const page = await browser.newPage({ viewport: { width: w, height: w < 700 ? 844 : 1000 }, deviceScaleFactor: 2 });
  await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForTimeout(400);

  const m = await page.evaluate(() => {
    const de = document.documentElement;
    let worst = null;
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0) continue;
      const over = Math.round(r.right - de.clientWidth);
      if (over > 1 && (!worst || over > worst.over)) {
        worst = { over, tag: el.tagName, cls: el.className?.toString?.().slice(0, 60) };
      }
    }
    return {
      overflow: de.scrollWidth - de.clientWidth,
      scrollWidth: de.scrollWidth,
      clientWidth: de.clientWidth,
      height: de.scrollHeight,
      worst,
      requests: performance.getEntriesByType('resource').map((r) => new URL(r.name).origin),
    };
  });
  report.widths[w] = m;

  await page.screenshot({ path: `${OUT}w11-${w}-hero.png`, clip: { x: 0, y: 0, width: w, height: w < 700 ? 1700 : 1000 } });
  await page.screenshot({ path: `${OUT}w11-${w}-full.png`, fullPage: true });
  await page.close();
}

// ---- rendered-pixel contrast: sample text glyph pixels vs their local background
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
await page.goto(PAGE_URL, { waitUntil: 'networkidle' });

const targets = await page.evaluate(() => {
  const sel = [
    ['hero lede', '.stage-land .lede'],
    ['hero figcaption', '.prism figcaption'],
    ['hero eyebrow', '.stage-land .eyebrow'],
    ['hero key label', '.key li b'],
    ['hero key note', '.key li span'],
    ['hero chip id', '.stage-land .chip b'],
    ['hero chip sample', '.stage-land .chip em'],
    ['hero band name', '.stage-land .band-name'],
    ['hero plate title', '.stage-land .plate b'],
    ['hero plate fact', '.stage-land .plate .mono'],
    ['hero source kicker', '.stage-land .src-k'],
    ['hero source fact', '.stage-land .src-f'],
    ['section lede', '#export .section-lede'],
    ['step body', '.steps p'],
    ['dest body', '.dests p'],
    ['dest fact', '.dests .fact'],
    ['format cell', '.formats td'],
    ['type id', '.types b'],
    ['type sample', '.types em'],
    ['cats note', '.cats span'],
    ['slab body', '.durability p'],
    ['slab fact', '.durability .fact'],
    ['faq answer', '.faq-item dd'],
    ['status not-yet', '.cross li'],
    ['mcp tool', '.mcp-list li'],
    ['caveat', '.caveat'],
    ['sibling note', '.siblings span'],
    ['footer', '.footer p'],
    ['state cell', '.states td'],
  ];
  return sel
    .map(([name, s]) => {
      const el = document.querySelector(s);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { name, s, x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height };
    })
    .filter(Boolean);
});

const shot = await page.screenshot({ fullPage: true });
fs.writeFileSync(`${OUT}full-1440.png`, shot);

// Decode PNG with sharp if available, else use the browser itself as the decoder.
const sampled = await page.evaluate(
  async ({ targets, b64 }) => {
    const img = new Image();
    img.src = 'data:image/png;base64,' + b64;
    await img.decode();
    const dpr = img.width / document.documentElement.clientWidth;
    const c = document.createElement('canvas');
    c.width = img.width;
    c.height = img.height;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0);

    const out = [];
    for (const t of targets) {
      const x0 = Math.max(0, Math.round(t.x * dpr));
      const y0 = Math.max(0, Math.round(t.y * dpr));
      const w = Math.min(Math.round(t.w * dpr), img.width - x0);
      const h = Math.min(Math.round(Math.min(t.h, 60) * dpr), img.height - y0);
      if (w < 2 || h < 2) continue;
      const d = ctx.getImageData(x0, y0, w, h).data;
      // Luminance histogram of the patch: background = the most common bright value,
      // text = the darkest cluster (or brightest, on a dark background).
      const px = [];
      for (let i = 0; i < d.length; i += 4) px.push([d[i], d[i + 1], d[i + 2]]);
      const L = (p) => {
        const f = (v) => {
          v /= 255;
          return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        };
        return 0.2126 * f(p[0]) + 0.7152 * f(p[1]) + 0.0722 * f(p[2]);
      };
      const sorted = px.map((p) => [L(p), p]).sort((a, b) => a[0] - b[0]);
      // background = modal (median of the majority side); pick by counting
      const counts = new Map();
      for (const p of px) {
        const k = p.join(',');
        counts.set(k, (counts.get(k) || 0) + 1);
      }
      let bg = null;
      let best = -1;
      for (const [k, n] of counts) if (n > best) ((best = n), (bg = k.split(',').map(Number)));
      const bgL = L(bg);
      // text = extreme opposite the background, using the 2nd percentile so
      // antialiased edge pixels don't dominate
      const idx = bgL > 0.4 ? Math.floor(sorted.length * 0.02) : Math.floor(sorted.length * 0.98);
      const fg = sorted[idx][1];
      out.push({ name: t.name, fg, bg, cover: best / px.length });
    }
    return out;
  },
  { targets, b64: shot.toString('base64') }
);

for (const s of sampled) {
  report.contrast.push({
    name: s.name,
    fg: `rgb(${s.fg.join(' ')})`,
    bg: `rgb(${s.bg.join(' ')})`,
    ratio: +ratio(s.fg, s.bg).toFixed(2),
    pass: ratio(s.fg, s.bg) >= 4.5,
  });
}

await page.close();
await browser.close();

fs.writeFileSync(new URL('./report.json', import.meta.url).pathname, JSON.stringify(report, null, 2));

console.log('--- overflow ---');
for (const [w, m] of Object.entries(report.widths)) {
  console.log(`${w}px  scrollWidth ${m.scrollWidth}  clientWidth ${m.clientWidth}  overflow ${m.overflow}px  height ${m.height}px`, m.worst ? `worst: ${m.worst.tag}.${m.worst.cls} +${m.worst.over}` : '');
}
console.log('--- third-party origins ---');
console.log([...new Set(Object.values(report.widths).flatMap((m) => m.requests))].join('\n'));
console.log('--- contrast (rendered pixels) ---');
for (const c of report.contrast) console.log(`${c.pass ? 'PASS' : 'FAIL'}  ${c.ratio.toFixed(2)}  ${c.name}  ${c.fg} on ${c.bg}`);
const fails = report.contrast.filter((c) => !c.pass);
console.log(fails.length ? `\n${fails.length} FAILING` : '\nall pass');
