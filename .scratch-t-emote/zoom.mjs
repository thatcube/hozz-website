import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const svgs = JSON.parse(fs.readFileSync('.scratch-t-emote/svgs.json', 'utf8'));
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1120, height: 800 }, deviceScaleFactor: 2 });
const cell = (s, px, bg) => `<div style="background:${bg};padding:10px;display:inline-block">${s.replace(/width="\d+"/, `width="${px}"`).replace(/height="\d+"/, `height="${px}"`)}</div>`;
for (const [slug, s] of Object.entries(svgs)) {
  const html = `<body style="margin:0;font:12px system-ui;background:#fff">
  <div style="display:flex;align-items:flex-end;gap:8px;padding:12px">
    ${cell(s, 340, '#fafaf8')}${cell(s, 340, '#141414')}
    <div>${[64,48,40,32,28,24].map(n=>cell(s,n,'#fafaf8')+cell(s,n,'#141414')).join('<br>')}</div>
  </div></body>`;
  await p.setContent(html);
  await p.screenshot({ path: `.scratch-t-emote/zoom-${slug}.png`, fullPage: true });
}
await b.close();
console.log('ok');
