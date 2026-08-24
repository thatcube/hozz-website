import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('http://127.0.0.1:5317/logos/index.html');
const mine = await p.$eval('#t17 svg', e => e.outerHTML);
const shipped = {
  twozz: fs.readFileSync(process.env.HOME + '/hozzshots/ref/twozz.svg', 'utf8'),
  plozz: fs.readFileSync(process.env.HOME + '/hozzshots/ref/plozz.svg', 'utf8'),
};
const row = (label, svg) => `<div class=r><b>${label}</b>${[128,96,48,32,24,16].map(s=>`<span style="width:${s}px;height:${s}px;display:inline-block">${svg.replace(/width="[^"]*"/,`width="${s}"`).replace(/height="[^"]*"/,`height="${s}"`)}</span>`).join('')}</div>`;
await p.setContent(`<style>body{margin:0;background:#fbfaf8;font:12px system-ui;image-rendering:pixelated}
.r{display:flex;align-items:flex-end;gap:28px;padding:14px 20px}
.r b{width:60px;font-weight:600}
svg{width:100%;height:100%;image-rendering:pixelated}
.dark{background:#141218;color:#888}</style>
<div id=w>${row('t17',mine)}${row('twozz',shipped.twozz)}${row('plozz',shipped.plozz)}
<div class=dark>${row('t17',mine)}${row('twozz',shipped.twozz)}</div></div>`);
await p.$eval('#w', e => e.scrollHeight);
await (await p.$('#w')).screenshot({ path: process.env.OUT || '.scratch-t17/cmp.png' });
await b.close();
