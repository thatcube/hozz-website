import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('http://127.0.0.1:5317/logos/index.html');
const mine = await p.$eval('#t17 svg', e => e.outerHTML);
const tw = fs.readFileSync(process.env.HOME + '/hozzshots/ref/twozz.svg', 'utf8');
const at = (svg,s) => `<span style="width:${s}px;height:${s}px;display:inline-block">${svg.replace(/width="[^"]*"/,`width="${s}"`).replace(/height="[^"]*"/,`height="${s}"`)}</span>`;
await p.setContent(`<style>body{margin:0;background:#fbfaf8;font:12px system-ui}
svg{width:100%;height:100%;image-rendering:pixelated}
.r{display:flex;align-items:flex-end;gap:36px;padding:18px 24px}
.d{background:#141218}</style>
<div id=w><div class=r>${at(mine,320)}<div>${at(mine,96)}<br>${at(mine,48)} ${at(mine,32)} ${at(mine,24)}</div>${at(tw,320)}</div>
<div class="r d">${at(mine,320)}${at(tw,320)}</div></div>`);
await (await p.$('#w')).screenshot({ path: '.scratch-t17/big.png' });
await b.close();
