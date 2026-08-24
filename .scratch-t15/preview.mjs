import fs from 'fs';
import path from 'path';
import { facePathsAt } from '../src/data/mark.ts';
import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';

const ROOT = process.cwd();

function svgFromAstro(file) {
  const src = fs.readFileSync(path.join(ROOT, 'src/components/mark/logos', file), 'utf8');
  const body = src.split('<MarkFrame')[1];
  const paths = [...body.matchAll(/<path d="([^"]+)"\s+fill="([^"]+)"/g)]
    .map(([, d, f]) => `<path d="${d}" fill="${f}"/>`)
    .join('');
  const g = body.match(/<g fill="([^"]+)"/);
  const opts = body.match(/facePathsAt\(\{([^}]+)\}\)/);
  let face = '';
  if (opts) {
    const o = {};
    for (const kv of opts[1].split(',')) {
      const [k, v] = kv.split(':').map((s) => s.trim());
      o[k] = v.startsWith("'") ? v.slice(1, -1) : Number(v);
    }
    face = `<g fill="${g[1]}">` + facePathsAt(o).map((d) => `<path d="${d}"/>`).join('') + '</g>';
  }
  return (size) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 32 32" shape-rendering="crispEdges" style="display:block">${paths}${face}</svg>`;
}

const shipped = fs.readFileSync(path.join(ROOT, '.briefs/twozz-shipped.svg'), 'utf8');
const shippedAt = (size) =>
  shipped.replace('width="32" height="32"', `width="${size}" height="${size}"`)
         .replace('<svg ', '<svg style="display:block" ')
         .replace(/id="c"/g, 'id="cc"').replace(/url\(#c\)/g, 'url(#cc)');

const t15 = svgFromAstro('t15.astro');
const c45 = svgFromAstro('c45.astro');

const cell = (label, svg) =>
  `<div style="display:flex;flex-direction:column;align-items:center;gap:6px">
     ${svg}<span style="font:10px system-ui;opacity:.55">${label}</span></div>`;

const row = (size, bg, fg) =>
  `<div style="display:flex;gap:26px;align-items:flex-end;padding:18px 22px;background:${bg};color:${fg};border-radius:12px;margin:10px">
     ${cell('t15 ' + size, t15(size))}
     ${cell('shipped', shippedAt(size))}
     ${cell('c45 Hozz', c45(size))}
   </div>`;

fs.writeFileSync('.scratch-t15/p.html',
  `<body style="margin:0;background:#eef0f3;font-family:system-ui">
     ${row(96, '#fbfbfc', '#111')}
     ${row(96, '#17181c', '#eee')}
     ${row(48, '#fbfbfc', '#111')}
     ${row(24, '#fbfbfc', '#111')}
     ${row(24, '#17181c', '#eee')}
     ${row(16, '#fbfbfc', '#111')}
   </body>`);

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 520, height: 760 }, deviceScaleFactor: 3 });
await p.goto('file://' + ROOT + '/.scratch-t15/p.html');
await p.screenshot({ path: '.scratch-t15/p.png', fullPage: true });
await b.close();
console.log('shot');
