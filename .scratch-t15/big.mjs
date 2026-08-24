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

const t15 = svgFromAstro('t15.astro');
const shipped = fs.readFileSync(path.join(ROOT, '.briefs/twozz-shipped.svg'), 'utf8');
const shippedAt = (size) =>
  shipped.replace('width="32" height="32"', `width="${size}" height="${size}"`)
         .replace('<svg ', '<svg style="display:block" ')
         .replace(/id="c"/g, 'id="cc"').replace(/url\(#c\)/g, 'url(#cc)');

fs.writeFileSync('.scratch-t15/big.html',
  `<body style="margin:0;background:#f4f5f7;font-family:system-ui;display:flex;gap:16px;padding:16px;align-items:flex-start">
     <div style="background:#fbfbfc;padding:14px;border-radius:12px">${t15(300)}</div>
     <div style="display:flex;flex-direction:column;gap:14px">
       <div style="background:#17181c;padding:14px;border-radius:12px">${t15(180)}</div>
       <div style="background:#fbfbfc;padding:14px;border-radius:12px">${shippedAt(180)}</div>
     </div>
   </body>`);

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 580, height: 380 }, deviceScaleFactor: 2 });
await p.goto('file://' + ROOT + '/.scratch-t15/big.html');
await p.screenshot({ path: '.scratch-t15/big.png', fullPage: true });
await b.close();
console.log('shot');
