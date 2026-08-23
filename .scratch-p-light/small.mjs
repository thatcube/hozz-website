import pw from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.js';
const { chromium } = pw;
import { readFileSync } from 'node:fs';

const OUT = new URL('./', import.meta.url).pathname;
const SLUGS = ['p00', 'p07', 'p08', 'p09'];

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1500, height: 1200 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
await page.goto('http://127.0.0.1:4733/f/', { waitUntil: 'networkidle' });
await page.waitForTimeout(800);

const shots = {};
for (const slug of SLUGS) {
  const fig = page.locator('figure.card', { has: page.locator(`.slug:text-is("${slug}")`) });
  if (!(await fig.count())) continue;
  shots[slug] = {};
  for (const [rowIdx, rowName] of [[0, 'light'], [1, 'dark']]) {
    const row = fig.first().locator('.row').nth(rowIdx);
    for (const [cellIdx, px] of [[2, 40], [3, 24]]) {
      const svg = row.locator('.cell').nth(cellIdx).locator('svg');
      const buf = await svg.screenshot({ omitBackground: false });
      shots[slug][`${rowName}${px}`] = buf.toString('base64');
    }
  }
}
await page.close();

// Blow the true-pixel captures up with smoothing off, so the small sizes can
// actually be looked at.
const rows = SLUGS.filter((s) => shots[s])
  .map((s) => {
    const cells = ['light40', 'light24', 'dark40', 'dark24']
      .map(
        (k) =>
          `<div class="c"><img data-src="data:image/png;base64,${shots[s][k]}"><span>${k}</span></div>`,
      )
      .join('');
    return `<div class="r"><b>${s}</b>${cells}</div>`;
  })
  .join('');

const html = `<!doctype html><meta charset=utf-8><style>
body{background:#8a8f96;font:12px ui-monospace,monospace;margin:0;padding:14px}
.r{display:flex;align-items:center;gap:18px;margin-bottom:14px}
.r b{width:34px}
.c{display:grid;justify-items:center;gap:4px}
canvas{image-rendering:pixelated}
.c:nth-child(4) canvas,.c:nth-child(5) canvas{background:#16181c}
.c:nth-child(2) canvas,.c:nth-child(3) canvas{background:#fbfbfa}
</style><div id=w>${rows}</div>
<script>
const imgs=[...document.querySelectorAll('img')];
Promise.all(imgs.map(i=>new Promise(r=>{const im=new Image();im.onload=()=>{
  const cv=document.createElement('canvas');const S=7;cv.width=im.width*S;cv.height=im.height*S;
  const g=cv.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(im,0,0,cv.width,cv.height);
  i.replaceWith(cv);r();};im.src=i.dataset.src;}))).then(()=>{document.title='done'});
</script>`;

const page2 = await ctx.newPage();
await page2.setContent(html);
await page2.waitForFunction(() => document.title === 'done');
await page2.waitForTimeout(600);
await page2.screenshot({ path: `${OUT}small.png`, fullPage: true });

await b.close();
console.log('ok');
