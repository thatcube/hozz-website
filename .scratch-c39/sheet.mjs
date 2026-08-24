import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
const names = process.argv.slice(3);
const cells = names.map(n => {
  const s = fs.readFileSync(`.scratch-c39/${n}.svg`, 'utf8');
  const at = (px) => s.replace('width="32" height="32"', `width="${px}" height="${px}"`);
  return `<div class="c"><div class="l">${n}</div>
    <div class="r">${at(96)}${at(48)}${at(24)}${at(16)}</div>
    <div class="r dk">${at(96)}${at(24)}</div></div>`;
}).join('');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 640, height: 200 + names.length*150 }, deviceScaleFactor: 2 });
await p.setContent(`<body style="margin:0;background:#f7f9fb;font:12px system-ui">
<style>.c{padding:10px 14px;border-bottom:1px solid #dde}.l{font:11px ui-monospace;color:#456;margin-bottom:6px}
.r{display:flex;gap:16px;align-items:center;padding:8px;background:#fff}
.dk{background:#101820;margin-top:4px}svg{display:block;image-rendering:pixelated}</style>${cells}</body>`);
await p.screenshot({ path: process.argv[2], fullPage: true });
await b.close();
