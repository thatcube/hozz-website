import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
const names = process.argv.slice(3);
const cells = names.map(n => {
  const s = fs.readFileSync(`.scratch-c39/${n}.svg`, 'utf8');
  const at = (px) => s.replace('width="32" height="32"', `width="${px}" height="${px}"`);
  return `<div class="c"><div class="l">${n}</div><div class="r">${at(288)}</div></div>`;
}).join('');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 340*names.length, height: 380 }, deviceScaleFactor: 1 });
await p.setContent(`<body style="margin:0;background:#fff;font:12px system-ui;display:flex">
<style>.c{padding:8px}.l{font:11px ui-monospace;color:#456}svg{display:block;image-rendering:pixelated}</style>${cells}</body>`);
await p.screenshot({ path: process.argv[2], fullPage: true });
await b.close();
