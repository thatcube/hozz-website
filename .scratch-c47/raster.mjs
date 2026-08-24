import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { readFileSync, writeFileSync } from 'node:fs';

const files = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 64, height: 64 } });

for (const f of files) {
  const svg = readFileSync(f, 'utf8');
  const b64 = Buffer.from(svg, 'utf8').toString('base64');
  const grid = await page.evaluate(async (b64) => {
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,' + b64;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = 32; c.height = 32;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(img, 0, 0, 32, 32);
    const d = ctx.getImageData(0, 0, 32, 32).data;
    const rows = [];
    for (let y = 0; y < 32; y++) {
      const row = [];
      for (let x = 0; x < 32; x++) {
        const i = (y * 32 + x) * 4;
        row.push(d[i + 3] === 0 ? null :
          '#' + [d[i], d[i + 1], d[i + 2]].map(v => v.toString(16).padStart(2, '0')).join(''));
      }
      rows.push(row);
    }
    return rows;
  }, b64);
  const name = f.split('/').pop().replace('.svg', '');
  writeFileSync(new URL(`./${name}.json`, import.meta.url), JSON.stringify(grid));
  console.log('wrote', name);
}
await browser.close();
