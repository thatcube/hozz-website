import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 980, height: 560 }, deviceScaleFactor: 2 });
await p.goto('http://127.0.0.1:5317/logos/index.html', { waitUntil: 'networkidle' });
const g = async s => p.$eval(`#${s} svg`, e => e.outerHTML);
const a = await g('t17'), c = await g('t19');
const at = (s,n) => s.replace(/width="\d+"/,`width="${n}"`).replace(/height="\d+"/,`height="${n}"`);
await p.setContent(`<style>body{margin:0;background:#fff;padding:24px;font:11px system-ui}
.r{display:flex;gap:34px;align-items:flex-end;margin-bottom:22px}
.c{display:flex;flex-direction:column;align-items:center;gap:6px}svg{image-rendering:pixelated;display:block}</style>
<div class="r"><div class="c">${at(a,400)}<small>t17 400</small></div><div class="c">${at(c,400)}<small>t19 400</small></div>
<div class="c">${at(a,28)}<small>t17 28</small></div><div class="c">${at(c,28)}<small>t19 28</small></div>
<div class="c">${at(a,16)}<small>t17 16</small></div></div>`);
await p.screenshot({ path: '.scratch-t17/r.png', fullPage: true });
await b.close();
