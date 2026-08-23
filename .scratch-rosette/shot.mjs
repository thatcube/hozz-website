import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import fs from 'fs';
import { facePathsAt } from './mark.mjs';

const data = JSON.parse(fs.readFileSync(process.argv[2] || '.scratch-rosette/cands.json', 'utf8'));
const out = process.argv[3] || '.scratch-rosette/sheet.png';

const svg = (m, size) => {
  const body = m.paths.map(([d, f]) => `<path d="${d}" fill="${f}"/>`).join('');
  const face = m.face
    ? `<g fill="${m.key}">${facePathsAt({ cx: 16, cy: m.face.cy, size: m.face.size, smile: 'wide', gap: m.face.gap }).map((d) => `<path d="${d}"/>`).join('')}</g>`
    : '';
  return `<svg width="${size}" height="${size}" viewBox="0 0 32 32" shape-rendering="crispEdges" style="display:block">${body}${face}</svg>`;
};

const cell = (m) => `<div style="display:flex;flex-direction:column;align-items:center;gap:6px">
  ${svg(m, 96)}
  <div style="display:flex;gap:10px;align-items:flex-end">${svg(m, 48)}${svg(m, 32)}${svg(m, 24)}${svg(m, 16)}</div>
  <div style="font:11px ui-monospace;color:#555">${m.name}${m.ok ? '' : ' ✗'}</div>
</div>`;

const rows = [];
for (let i = 0; i < data.length; i += 4) rows.push(data.slice(i, i + 4));

const html = `<body style="margin:0;font-family:system-ui;background:#eef0f3">
${rows.map((r) => `<div style="display:flex;gap:26px;padding:18px 24px;background:#fbfbfc;margin:10px;border-radius:12px">${r.map(cell).join('')}</div>`).join('')}
${rows.map((r) => `<div style="display:flex;gap:26px;padding:18px 24px;background:#17181c;margin:10px;border-radius:12px">${r.map(cell).join('')}</div>`).join('')}
</body>`;

fs.writeFileSync('.scratch-rosette/p.html', html);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 720, height: 500 }, deviceScaleFactor: 2 });
await p.goto('file://' + process.cwd() + '/.scratch-rosette/p.html');
await p.screenshot({ path: out, fullPage: true });
await b.close();
console.log('wrote', out);
