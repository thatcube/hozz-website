import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;

const PORT = process.env.PORT || 5177;
const PAGE = `http://127.0.0.1:${PORT}/w/w13/`;
const WIDTHS = [1920, 1440, 1024, 390];
const OUT = '/Users/brandon/Development/copilot-worktrees/hozz-website/thatcube-curly-dollop/.scratch-w13/shots/';

const browser = await chromium.launch();
const results = [];

for (const w of WIDTHS) {
  const ctx = await browser.newContext({
    viewport: { width: w, height: w === 390 ? 844 : 1000 },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  const thirdParty = [];
  page.on('request', (r) => {
    const u = new URL(r.url());
    if (u.hostname !== '127.0.0.1' && u.hostname !== 'localhost' && u.protocol !== 'data:') {
      thirdParty.push(r.url());
    }
  });
  await page.goto(PAGE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  const overflow = await page.evaluate(() => {
    const de = document.documentElement;
    const vw = de.clientWidth;
    const offenders = [];
    for (const el of document.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      // ignore elements inside a clipped ancestor
      let p = el.parentElement,
        clipped = false;
      while (p) {
        const cs = getComputedStyle(p);
        if (cs.overflowX === 'hidden' || cs.overflowX === 'auto' || cs.overflowX === 'scroll' || cs.overflowX === 'clip') {
          clipped = true;
          break;
        }
        p = p.parentElement;
      }
      if (clipped) continue;
      if (r.right > vw + 1 || r.left < -1) {
        offenders.push({
          sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
          left: Math.round(r.left),
          right: Math.round(r.right),
        });
      }
    }
    return {
      viewport: vw,
      docScrollWidth: de.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
      overflowPx: Math.max(0, de.scrollWidth - vw),
      canScrollX: de.scrollWidth > vw,
      offenders: offenders.slice(0, 12),
      pageHeight: de.scrollHeight,
    };
  });

  await page.screenshot({ path: `${OUT}w13-${w}-top.png` });
  await page.screenshot({ path: `${OUT}w13-${w}-full.png`, fullPage: true });

  results.push({ width: w, ...overflow, thirdParty });
  await ctx.close();
}

await browser.close();
console.log(JSON.stringify(results, null, 2));
