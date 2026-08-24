import playwright from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';

const { chromium } = playwright;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:5819/logos/', { waitUntil: 'networkidle' });

const marks = {};
for (const slug of ['t16', 't19', 't11']) {
  marks[slug] = await page.locator(`#${slug} .ground--light svg`).first().evaluate((svg) => svg.outerHTML);
}

for (const size of [400, 96, 48, 28, 16]) {
  const gap = Math.max(8, Math.round(size * 0.12));
  const width = size * 3 + gap * 2;
  await page.setContent(`
    <style>
      html,body{margin:0;width:${width}px;height:${size}px;background:#fff}
      body{display:flex;gap:${gap}px}
      svg{width:${size}px;height:${size}px;flex:none}
    </style>
    ${marks.t16}${marks.t19}${marks.t11}
  `);
  await page.screenshot({
    path: `.scratch-t16/compare-${size}.png`,
    clip: { x: 0, y: 0, width, height: size },
  });
}

await browser.close();
