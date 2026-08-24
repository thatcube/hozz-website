import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
const file = process.argv[2];
const svg = fs.readFileSync(file, 'utf8');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 320, height: 320 }, deviceScaleFactor: 1 });
await p.setContent(`<body style="margin:0;background:#ffffff">
<div style="width:320px;height:320px;image-rendering:pixelated">${svg.replace('width="32" height="32"','width="320" height="320"')}</div></body>`);
const buf = await p.screenshot();
fs.writeFileSync(process.argv[3], buf);
// read pixel centres
const data = await p.evaluate(async () => {
  const el = document.querySelector('svg');
  const s = new XMLSerializer().serializeToString(el);
  const img = new Image();
  const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
  await new Promise(r => { img.onload = r; img.src = url; });
  const c = document.createElement('canvas'); c.width = 32; c.height = 32;
  const ctx = c.getContext('2d'); ctx.imageSmoothingEnabled = false;
  ctx.fillStyle='#fff'; ctx.fillRect(0,0,32,32);
  ctx.drawImage(img, 0, 0, 32, 32);
  return Array.from(ctx.getImageData(0,0,32,32).data);
});
fs.writeFileSync(process.argv[4], JSON.stringify(data));
await b.close();
